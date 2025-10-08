import json
import logging
from decimal import Decimal, ROUND_FLOOR
from pprint import pformat

import requests
from django.db.models import F
from django.db import transaction as django_transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from account.models import ROLE_OWNER
from orders.services import format_order_details, send_receipt_to_mqtt
from services.pos_service_factory import POSServiceFactory
from tg_bot.utils import send_order_notification
from orders.models import Transaction, OrderStatus, Client, BonusHistory, ClientVenueProfile

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class PaymentWebhookViewSet(viewsets.ViewSet):
    """
    ViewSet для обработки webhook от платёжной системы
    """

    def create(self, request, *args, **kwargs):
        try:
            logger.info("===== NEW REQUEST =====")
            logger.info("Headers: %s", pformat(dict(request.headers)))

            try:
                body_json = json.dumps(request.data, indent=2, ensure_ascii=False)
                logger.info("Body:\n%s", body_json)
            except Exception:
                logger.warning("Не удалось сериализовать request.data")

            data = request.data

            # ВАЖНО: бизнес-операции под одной транзакцией
            with django_transaction.atomic():
                transaction = self._get_transaction(data)
                if isinstance(transaction, Response):
                    return transaction  # это уже готовый ответ с ошибкой

                order = transaction.order
                client, venue = order.client, order.venue

                # статусы
                self._update_transaction_and_order(transaction, order, data)

                # клиент и отправка в POS
                self._process_client_and_pos(order, venue)

                # бонусы
                self._apply_bonus_writeoff(order, client, venue)
                self._apply_bonus_logic(order, client, venue)

            # внешние вызовы/уведомления выполняются уже после коммита
            self._send_notifications(order, transaction)

            logger.info("Обработка вебхука успешно завершена")
            return Response({"success": True}, status=status.HTTP_200_OK)

        except Exception:
            logger.exception("Ошибка при обработке webhook")
            return Response({"error": "Внутренняя ошибка"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- Вспомогательные методы ---

    def _get_transaction(self, data):
        """Поиск транзакции и базовая валидация"""
        transaction_id = data.get("operation_id")
        payment_status = data.get("operation_state")

        if not transaction_id or not payment_status:
            logger.warning("Недостаточно данных в webhook: %s", data)
            return Response({"error": "Недостаточно данных"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            return Transaction.objects.select_related(
                "order__venue__pos_system",
                "order__spot"
            ).prefetch_related(
                "order__order_products__product"
            ).get(id=transaction_id)
        except Transaction.DoesNotExist:
            logger.error(f"Транзакция не найдена: {transaction_id}")
            return Response({"error": "Транзакция не найдена"}, status=status.HTTP_404_NOT_FOUND)

    def _update_transaction_and_order(self, transaction, order, data):
        """Обновление статуса транзакции и заказа"""
        payment_status = data.get("operation_state")

        if transaction.status != payment_status:
            logger.info(f"Обновление транзакции {transaction.id}: {transaction.status} → {payment_status}")
            transaction.status = payment_status
            transaction.json_data = json.dumps(data)
            transaction.save(update_fields=["status", "json_data"])

            if order.status == OrderStatus.WAITING_FOR_PAYMENT:
                order.status = OrderStatus.NEW
                order.save(update_fields=["status"])
                logger.info(f"Статус заказа {order.id} обновлён на 'Заказ оформлен'")
        else:
            logger.info(f"Webhook повторный — статус {payment_status} уже установлен")

    def _process_client_and_pos(self, order, venue):
        """Создание/обновление клиента (через POS или локально)"""
        pos_system_name = venue.pos_system.name.lower() if venue.pos_system else None
        client = None

        if pos_system_name:
            logger.info(f"Отправка заказа {order.id} в POS {pos_system_name}")
            pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

            pos_response = pos_service.send_order_to_pos(order)
            if not pos_response:
                raise ValueError("POS не принял заказ")

            client = pos_service.get_or_create_client(venue, pos_response.get("client_id"))
            if not client:
                raise ValueError("Не удалось создать/получить клиента из POS")

            order.external_id = pos_response.get("incoming_order_id")
            if not order.external_id:
                raise ValueError("Не получили external_id от POS")

        else:
            logger.info(f"POS не подключён, ищем/создаём локального клиента для заказа {order.id}")
            client = Client.objects.filter(phone_number=order.phone).first()
            if not client:
                client = Client.objects.create(phone_number=order.phone)

        # профиль клиента в конкретном заведении
        ClientVenueProfile.objects.get_or_create(
            client=client,
            venue=venue,
            defaults={"bonus": 0, "total_payed_sum": 0},
        )

        order.client = client
        order.save(update_fields=["client", "external_id"])

    def _apply_bonus_writeoff(self, order, client, venue):
        """Списание бонусов клиента после оплаты"""
        amount = order.bonus or 0

        if not client or not venue or amount <= 0:
            return

        # атомарное списание
        updated = ClientVenueProfile.objects.filter(
            client=client,
            venue=venue,
            bonus__gte=amount
        ).update(bonus=F("bonus") - amount)

        if not updated:
            logger.warning("Недостаточно бонусов у клиента %s для списания", client.phone_number)
            return

        BonusHistory.objects.create(
            client=client,
            order=order,
            venue=venue,
            amount=-amount,
            operation=BonusHistory.Operation.WRITE_OFF,
            description=f"Списание {amount} бонусов при оплате заказа {order.id}",
        )
        logger.info("Списано %s бонусов у клиента %s", amount, client.phone_number)

    def _apply_bonus_logic(self, order, client, venue):
        """Начисление бонусов после успешной оплаты"""
        if not client or not venue or not venue.is_bonus_system_enabled:
            return

        percent = Decimal(str(venue.bonus_accrual_percent or 0))
        if percent <= 0:
            return

        net_sum = Decimal(order.total_price)
        accrued = (net_sum * percent / Decimal("100")).to_integral_value(rounding=ROUND_FLOOR)
        accrued = int(accrued)
        if accrued <= 0:
            return

        profile, created = ClientVenueProfile.objects.get_or_create(
            client=client,
            venue=venue,
            defaults={"bonus": accrued, "total_payed_sum": int(net_sum)},
        )

        if not created:
            ClientVenueProfile.objects.filter(id=profile.id).update(
                bonus=F("bonus") + accrued,
                total_payed_sum=F("total_payed_sum") + int(net_sum),
            )

        BonusHistory.objects.create(
            client=client,
            venue=venue,
            order=order,
            amount=accrued,
            operation=BonusHistory.Operation.ACCRUAL,
            description=f"Начислено {percent}% за заказ {order.id}",
        )
        logger.info("Начислено %s бонусов клиенту %s", accrued, client.phone_number)

    def _send_notifications(self, order, transaction):
        """Отправка Telegram, чеков и n8n webhook"""
        # Telegram владельцу
        user_owner = order.venue.users.filter(role=ROLE_OWNER).first()
        if user_owner and user_owner.tg_chat_id:
            order_info = format_order_details(order)
            send_order_notification(user_owner.tg_chat_id, order_info, order.id)

        # MQTT чек
        if not send_receipt_to_mqtt(order, order.venue):
            logger.warning("Не удалось отправить чек в MQTT")

        # Webhook в n8n
        if order.is_tg_bot:
            try:
                order_payload = self._build_order_payload(order, transaction)
                webhook_url = "https://n8n.nexus.kg/webhook/payment_success"
                response = requests.post(webhook_url, json=order_payload, timeout=20)

                if response.status_code == 200:
                    logger.info("Webhook успешно отправлен в n8n")
                else:
                    logger.warning("Ошибка webhook: %s %s", response.status_code, response.text)
            except Exception:
                logger.exception("Ошибка при отправке webhook в n8n")

    def _build_order_payload(self, order, transaction):
        """Формирование payload для n8n"""
        return {
            "order_id": order.id,
            "venue_id": order.venue.id,
            "venue_name": order.venue.company_name,
            "phone": order.phone,
            "total_price": str(order.total_price),
            "created_at": order.created_at.isoformat(),
            "is_tg_bot": order.is_tg_bot,
            "tg_redirect_url": order.tg_redirect_url,
            "address": order.address,
            "spot": order.spot.address if order.spot else None,
            "service_mode": order.get_service_mode_display(),
            "products": [
                {
                    "product_name": op.product.product_name,
                    "count": op.count,
                    "price": str(op.total_price),
                }
                for op in order.order_products.all()
            ],
            "transaction": {
                "id": transaction.id,
                "status": transaction.status,
                "amount": str(transaction.total_price),
            },
        }
