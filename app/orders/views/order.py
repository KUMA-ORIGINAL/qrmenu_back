import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from services.pos_service_factory import POSServiceFactory
from venues.models import Venue, Table
from ..models import Order
from ..serializers import OrderSerializer

logger = logging.getLogger(__name__)


@extend_schema(
    tags=['Order'],
)
@extend_schema_view(
    create=extend_schema(
        summary='Создание заказа',
    ),
    list=extend_schema(
        summary='Получение заказов по названию заведения и номеру стола',
        parameters=[
            OpenApiParameter(
                name='venue_name',  # Имя параметра
                description='Фильтр по имени заведения',  # Описание параметра
                required=False,  # Параметр необязательный
                type=str  # Тип данных
            ),
            OpenApiParameter(
                name='table_num',  # Имя параметра
                description='Фильтр по номеру стола',  # Описание параметра
                required=False,  # Параметр необязательный
                type=str  # Тип данных
            )
        ]
    )
)
class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        queryset = super().get_queryset()

        venue_name = self.request.GET.get('venue_name', None)
        table_num = self.request.GET.get('table_num', None)

        if venue_name:
            queryset = queryset.filter(venue__company_name__icontains=venue_name)

        if table_num:
            queryset = queryset.filter(table__table_num=table_num)

        return queryset


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(f"Order creation failed due to validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_data = serializer.validated_data

            venue_name = request.data.get('venue_name')
            table_num = request.data.get('table_num')

            if not venue_name or not table_num:
                return Response({'error': 'Venue name and table number are required.'},
                                status=status.HTTP_400_BAD_REQUEST)

            venue = Venue.objects.filter(company_name__icontains=venue_name).first()
            if not venue:
                return Response({'error': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

            table = Table.objects.filter(venue=venue, table_num=table_num).first()
            if not table:
                return Response({'error': 'Table not found.'}, status=status.HTTP_404_NOT_FOUND)

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
