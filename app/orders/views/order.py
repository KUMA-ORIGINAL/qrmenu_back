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

logger = logging.getLogger('django')

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
            venue = Venue.objects.filter(id=3).first()
            api_token = venue.access_token
            pos_system_name = venue.pos_system.name.lower()
            pos_service = POSServiceFactory.get_service(pos_system_name, api_token)
            pos_response = pos_service.send_order_to_pos(order_data)
            if not pos_response:
                return Response('error', status=status.HTTP_400_BAD_REQUEST)
            order_data['venue_id'] = venue.id
            order_data['external_id'] = pos_response.get('response').get('incoming_order_id')
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Order creation failed due to an error: {str(e)}", exc_info=True)
            raise ValidationError({'detail': 'Order creation failed due to an internal error.'})


class PosterWebhookViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        client_secret = settings.POSTER_APPLICATION_SECRET

        serializer = PosterWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            logger.info(f"webhook Invalid data {serializer} {request.data}")
            return Response({"error": "Invalid data"}, status=status.HTTP_200_OK)

        post_data = serializer.validated_data
        verify_original = post_data['verify']
        del post_data['verify']

        verify = [
            str(post_data['account']),
            str(post_data['object']),
            str(post_data['object_id']),
            str(post_data['action']),
        ]

        if 'data' in post_data:
            verify.append(str(post_data['data']))

        verify.append(str(post_data['time']))
        verify.append(client_secret)

        verify_string = ';'.join(verify)
        verify_hash = hashlib.md5(verify_string.encode('utf-8')).hexdigest()

        if verify_hash != verify_original:
            return Response({"error": "Verification failed"}, status=status.HTTP_200_OK)

        logger.info(f"webhook OK {verify} - {post_data}")

        venue = Venue.objects.filter(account_number=post_data['account_number']).first()
        api_token = venue.access_token
        pos_system_name = venue.pos_system.name.lower()
        pos_service = POSServiceFactory.get_service(pos_system_name, api_token)
        if post_data['object'] == 'incoming_order' and post_data['action'] == 'changed':
            order = Order.objects.filter(venue=venue, external_id=post_data['object_id']).first()
            pos_response = pos_service.get_incoming_order_by_id(order_id=post_data['object_id'])
            order.status = pos_response.get('status')
            order.save()
        return Response({"status": "accept"}, status=status.HTTP_200_OK)
