import hashlib
import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from services.pos_service_factory import POSServiceFactory
from venues.models import Venue
from ..models import Order
from ..serializers import OrderSerializer
from ..serializers.webhook import PosterWebhookSerializer

logger = logging.getLogger(__name__)

@extend_schema(tags=['Order'])
@extend_schema_view(
    create=extend_schema(summary='Создание заказа')
)
class OrderViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(f"Order creation failed due to validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_data = serializer.validated_data
            venue = Venue.objects.filter(id=1).first()
            table = Table.objects.filter(venue=venue, table_num='8').first()
            api_token = venue.access_token
            pos_system_name = venue.pos_system.name.lower()
            pos_service = POSServiceFactory.get_service(pos_system_name, api_token)
            pos_response = pos_service.send_order_to_pos(order_data)

            if not pos_response:
                return Response('error', status=status.HTTP_400_BAD_REQUEST)

            client = pos_service.get_or_create_client(venue, pos_response.get('client_id'))

            order_data['client'] = client
            order_data['venue'] = venue
            order_data['external_id'] = pos_response.get('incoming_order_id')

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Order creation failed due to an error: {str(e)}", exc_info=True)
            raise ValidationError({'detail': 'Order creation failed due to an internal error.'})


class PosterWebhookViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        client_secret = settings.POSTER_APPLICATION_SECRET

        serializer = PosterWebhookSerializer(data=request.data)
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
            return Response({"error": "Processing failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            logger.info(f"Order {order.id} status updated to {order.status}")
        else:
            logger.warning(f"Failed to get status from POS system for order {order.id}")


