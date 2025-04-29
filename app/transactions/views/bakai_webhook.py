from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from account.models import ROLE_OWNER
from orders.services import format_order_details
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

            return Response({'success': True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Ошибка при обработке webhook")
            return Response({'error': 'Внутренняя ошибка'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
