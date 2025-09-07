import json
import logging
from decimal import Decimal, ROUND_FLOOR

import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from account.models import ROLE_OWNER
from orders.services import format_order_details, send_receipt_to_mqtt
from services.pos_service_factory import POSServiceFactory
from tg_bot.utils import send_order_notification
from ..models import Transaction, OrderStatus, Client, BonusHistory

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookViewSet(viewsets.ViewSet):
    """
    ViewSet для обработки webhook от платёжной системы
    """

    def create(self, request, *args, **kwargs):
        try:
            data = request.data

            transaction = self._get_transaction(data)
            if isinstance(transaction, Response):
                return transaction  # это уже ответ с ошибкой

            order = transaction.order

            # обновляем статусы платежа и заказа
            self._update_transaction_and_order(transaction, order, data)

            # создаём клиента (через POS или локально)
            self._process_client_and_pos(order)

            # списание бонусов (НОВОЕ!)
            self._apply_bonus_writeoff(order)

            self._apply_bonus_logic(order)

            # Отправляем уведомления и чеки
            self._send_notifications(order, transaction)

            logger.info("Обработка вебхука успешно завершена")
            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception:
            logger.exception("Ошибка при обработке webhook")
            return Response({'error': 'Внутренняя ошибка'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- Вспомогательные методы ---

    def _get_transaction(self, data):
        """Поиск транзакции и базовая валидация входных данных"""
        transaction_id = data.get('operation_id')
        payment_status = data.get('operation_state')

        if not transaction_id or not payment_status:
            logger.warning("Недостаточно данных в webhook: %s", data)
            return Response({'error': 'Недостаточно данных'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            return Transaction.objects.select_related(
                'order__venue__pos_system',
                'order__spot'
            ).prefetch_related(
                'order__order_products__product'
            ).get(id=transaction_id)
        except Transaction.DoesNotExist:
            logger.error(f"Транзакция не найдена: {transaction_id}")
            return Response({'error': 'Транзакция не найдена'}, status=status.HTTP_404_NOT_FOUND)

    def _update_transaction_and_order(self, transaction, order, data):
        """Обновление статуса транзакции и заказа"""
        payment_status = data.get('operation_state')

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

    def _process_client_and_pos(self, order):
        """Создание/присвоение клиента (через POS или локально)"""
        venue = order.venue
        pos_system_name = venue.pos_system.name.lower() if venue.pos_system else None
        client = None

        if pos_system_name:
            logger.info(f"Отправка заказа {order.id} в POS {pos_system_name}")
            pos_service = POSServiceFactory.get_service(pos_system_name, venue.access_token)

            pos_response = pos_service.send_order_to_pos(order)
            if not pos_response:
                raise ValueError("POS не принял заказ")

            client = pos_service.get_or_create_client(venue, pos_response.get('client_id'))
            if not client:
                raise ValueError("Не удалось создать/получить клиента из POS")

            order.external_id = pos_response.get('incoming_order_id')
            if not order.external_id:
                raise ValueError("Не получили external_id от POS")

        else:
            logger.info(f"POS не подключён, создаём локального клиента для заказа {order.id}")
            client = Client.objects.filter(venue=venue, phone_number=order.phone).first()
            if not client:
                client = Client.objects.create(venue=venue, phone_number=order.phone)

        order.client = client
        order.save(update_fields=["client", "external_id"])

    def _apply_bonus_writeoff(self, order):
        """Списание бонусов клиента после успешной оплаты"""
        client = order.client
        if not client:
            logger.warning(f"У заказа {order.id} нет клиента — бонусы не списаны")
            return

        requested = order.bonus or 0
        if requested <= 0:
            logger.info(f"У заказа {order.id} не было бонусов к списанию")
            return

        # Сколько реально можем списать
        can_write_off = min(requested, client.bonus, int(order.total_price))
        if can_write_off <= 0:
            logger.info(f"Списание бонусов для заказа {order.id} невозможно (недостаточно бонусов)")
            return

        # Списываем у клиентаx
        client.bonus -= can_write_off
        client.save(update_fields=["bonus"])

        # Обновляем заказ (храним уже реально списанное количество)
        order.bonus = can_write_off
        order.save(update_fields=["bonus"])

        BonusHistory.objects.create(
            client=client,
            order=order,
            amount=-can_write_off,
            operation=BonusHistory.Operation.WRITE_OFF,
            description=f"Списание {can_write_off} бонусов при оплате заказа {order.id}"
        )

        logger.info(f"Списано {can_write_off} бонусов у клиента {client.phone_number} за заказ {order.id}")

    def _apply_bonus_logic(self, order):
        """Начисление бонусов клиенту после успешной оплаты"""
        client = order.client
        venue = order.venue

        if not client:
            logger.warning(f"У заказа {order.id} нет клиента — бонусы не начислены")
            return

        if not venue.is_bonus_system_enabled:
            logger.info(f"У заведения {venue.company_name} бонусная система выключена")
            return

        percent = venue.bonus_accrual_percent
        if percent <= 0:
            logger.info(f"У заведения {venue.company_name} процент бонусов = 0")
            return

        # Учитываем только реально оплаченные деньги (без бонусов)
        net_sum = order.total_price - Decimal(order.bonus or 0)

        percent = Decimal(str(percent))  # в Decimal
        accrued = (net_sum * percent / Decimal("100")).to_integral_value(rounding=ROUND_FLOOR)
        accrued = int(accrued)

        if accrued > 0:
            client.bonus += accrued
            client.total_payed_sum = (client.total_payed_sum or 0) + int(net_sum)
            client.save(update_fields=["bonus", "total_payed_sum"])

            BonusHistory.objects.create(
                client=client,
                order=order,
                amount=accrued,
                operation=BonusHistory.Operation.ACCRUAL,
                description=f"Начислено {percent}% за заказ {order.id}"
            )

            logger.info(
                f"Начислено {accrued} бонусов клиенту {client.phone_number} "
                f"за заказ {order.id} в заведении {venue.company_name}"
            )

    def _send_notifications(self, order, transaction):
        """Отправка Telegram-оповещения, чека и n8n webhook"""
        # Telegram
        user_owner = order.venue.users.filter(role=ROLE_OWNER).first()
        if user_owner and user_owner.tg_chat_id:
            order_info = format_order_details(order)
            send_order_notification(user_owner.tg_chat_id, order_info, order.id)
        else:
            logger.info("Нет владельца заведения или tg_chat_id")

        # Чек в MQTT
        if not send_receipt_to_mqtt(order, order.venue):
            logger.warning("Не удалось отправить чек в MQTT")

        # Webhook в n8n (если заказ из TG-бота)
        if order.is_tg_bot:
            try:
                order_payload = self._build_order_payload(order, transaction)
                webhook_url = "https://n8n.nexus.kg/webhook/payment_success"
                response = requests.post(webhook_url, json=order_payload, timeout=20)

                if response.status_code == 200:
                    logger.info("Webhook успешно отправлен в n8n")
                else:
                    logger.warning(f"Ошибка webhook: {response.status_code} {response.text}")
            except Exception:
                logger.exception("Ошибка при отправке webhook в n8n")

    def _build_order_payload(self, order, transaction):
        """Сериализуем заказ в структуру для n8n"""
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
            }
        }
