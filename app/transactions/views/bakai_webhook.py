import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from account.models import ROLE_OWNER
from orders.services import format_order_details, send_receipt_to_mqtt
from tg_bot.utils import send_order_notification
from ..models import Transaction
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')  # отключаем CSRF
class PaymentWebhookViewSet(viewsets.ViewSet):
    """
    ViewSet для обработки webhook от платёжной системы.
    """
    def create(self, request, *args, **kwargs):
        try:
            data = request.data

            transaction_id = data.get('operation_id')
            payment_status = data.get('operation_state')

            logger.info(f'webhook data: {data}')

            if not transaction_id or not payment_status:
                logger.warning("Недостаточно данных в webhook: %s", data)
                return Response({'error': 'Недостаточно данных'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                logger.error(f"Транзакция не найдена: ID {transaction_id}")
                return Response({'error': 'Транзакция не найдена'}, status=status.HTTP_404_NOT_FOUND)

            if transaction.status != payment_status:
                logger.info(f"Обновление статуса транзакции {transaction.id}: {transaction.status} → {payment_status}")
                transaction.status = payment_status
                transaction.save(update_fields=["status"])
            else:
                logger.info(f"Повторное получение webhook: статус уже установлен — {payment_status}")

            user_owner = transaction.order.venue.users.filter(role=ROLE_OWNER).first()
            order = transaction.order
            if user_owner and user_owner.tg_chat_id:
                order_info = format_order_details(order)
                logger.info(f"Attempting to send a Telegram message to {user_owner.tg_chat_id}")
                send_order_notification(user_owner.tg_chat_id, order_info, order.id)
            else:
                logger.info("No valid Telegram chat ID found or owner does not exist.")

            if not send_receipt_to_mqtt(order, order.venue):
                logger.warning("Failed to send receipt to webhook.")

            try:
                order = transaction.order

                order_payload = {
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

                webhook_url = "https://emirtest.app.n8n.cloud/webhook/payment_success"
                response = requests.post(webhook_url, json=order_payload, timeout=5)

                if response.status_code == 200:
                    logger.info("Webhook успешно отправлен в n8n")
                else:
                    logger.warning(f"Ошибка при отправке webhook: код {response.status_code}, ответ: {response.text}")

            except Exception as e:
                logger.exception("Ошибка при отправке webhook в n8n")

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Ошибка при обработке webhook")
            return Response({'error': 'Внутренняя ошибка'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
