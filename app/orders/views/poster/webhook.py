import hashlib
import logging

from asgiref.sync import async_to_sync
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from orders.models import Order
from orders.serializers.webhook import PosterWebhookSerializer
from orders.services import notify_order_status
from services.pos_service_factory import POSServiceFactory
from venues.models import Venue

logger = logging.getLogger(__name__)


class PosterWebhookViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = PosterWebhookSerializer

    def create(self, request, *args, **kwargs):
        client_secret = settings.POSTER_APPLICATION_SECRET

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Webhook Invalid data: {serializer.errors} | Request Data: {request.data}")
            return Response({"error": "Invalid data"}, status=status.HTTP_200_OK)

        post_data = serializer.validated_data

        if not self._verify_signature(post_data, client_secret):
            logger.warning(f"Webhook verification failed: {post_data}")
            return Response({"error": "Verification failed"}, status=status.HTTP_200_OK)

        logger.info(f"Webhook data verified successfully: {post_data}")

        try:
            self._process_webhook(post_data)
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response({"error": "Processing failed"}, status=status.HTTP_200_OK)

        return Response({"status": "accepted"}, status=status.HTTP_200_OK)

    def _verify_signature(self, post_data, client_secret):
        """ Проверка подписи webhook данных. """
        verify_original = post_data.pop('verify')
        verify_data = [
            str(post_data.get('account')),
            str(post_data.get('object')),
            str(post_data.get('object_id')),
            str(post_data.get('action')),
            str(post_data.get('data', '')),  # Добавляем 'data', если она присутствует
            str(post_data.get('time')),
            client_secret
        ]

        verify_string = ';'.join(verify_data)
        verify_hash = hashlib.md5(verify_string.encode('utf-8')).hexdigest()

        return verify_hash == verify_original

    def _process_webhook(self, post_data):
        """ Обрабатывает валидные данные webhook. """
        venue = Venue.objects.filter(account_number=post_data.get('account_number')).first()

        if not venue:
            logger.warning(f"Venue not found for account number: {post_data.get('account_number')}")
            raise ValueError("Venue not found")

        pos_service = self._get_pos_service(venue)

        if post_data['object'] == 'incoming_order' and post_data['action'] == 'changed':
            self._update_order_status(venue, post_data, pos_service)

    def _get_pos_service(self, venue):
        """ Получение POS-сервиса по системе заведения. """
        pos_system_name = venue.pos_system.name.lower()
        api_token = venue.access_token
        return POSServiceFactory.get_service(pos_system_name, api_token)

    def _update_order_status(self, venue, post_data, pos_service):
        """ Обновление статуса заказа на основании данных POS-системы. """
        order = Order.objects.filter(venue=venue, external_id=post_data.get('object_id')).first()

        if not order:
            logger.warning(f"Order not found for external ID: {post_data.get('object_id')}")
            raise ValueError("Order not found")

        pos_response = pos_service.get_incoming_order_by_id(order_id=post_data.get('object_id'))
        order_status = pos_response.get('status')

        if order_status:
            order.status = order_status
            order.save()

            async_to_sync(notify_order_status)(order)

            logger.info(f"Order {order.id} status updated to {order.status}")
        else:
            logger.warning(f"Failed to get status from POS system for order {order.id}")
