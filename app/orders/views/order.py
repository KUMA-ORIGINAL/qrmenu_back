import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from services.pos_service_factory import POSServiceFactory
from venues.models import Venue, Table
from ..models import Order
from ..serializers import OrderSerializer
from ..websocket_utils import notify_order_status

logger = logging.getLogger(__name__)


@extend_schema(tags=['Order'])
@extend_schema_view(
    create=extend_schema(summary='Создание заказа'),
    list=extend_schema(summary='Получение заказов по id заведения и id стола')
)
class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['venue', 'table']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(f"Order creation failed due to validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_data = serializer.validated_data
            venue = Venue.objects.filter(id=4).first()
            table = Table.objects.filter(venue=venue, table_num='8').first()
            api_token = venue.access_token
            pos_system_name = venue.pos_system.name.lower()
            pos_service = POSServiceFactory.get_service(pos_system_name, api_token)

            pos_response = pos_service.send_order_to_pos(order_data)
            if not pos_response:
                return Response({'error': 'POS system did not accept the order'},
                                status=status.HTTP_400_BAD_REQUEST)

            client = pos_service.get_or_create_client(venue, pos_response.get('client_id'))

            order_data['table'] = table
            order_data['client'] = client
            order_data['venue'] = venue
            order_data['external_id'] = pos_response.get('incoming_order_id')

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Order creation failed due to an error: {str(e)}", exc_info=True)
            raise ValidationError({'detail': 'Order creation failed due to an internal error.'})
