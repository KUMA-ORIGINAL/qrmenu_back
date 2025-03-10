import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from services.pos_service_factory import POSServiceFactory
from services.send_receipt_to_printer import send_receipt_to_webhook
from venues.models import Venue, Table, Spot
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
                name='venue_slug',  # Имя параметра
                description='Фильтр по имени заведения',  # Описание параметра
                required=False,  # Параметр необязательный
                type=str  # Тип данных
            ),
            OpenApiParameter(
                name='spot_slug',  # Имя параметра
                description='Фильтр по slug точки',  # Описание параметра
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

        venue_slug = self.request.GET.get('venue_slug', None)
        spot_slug = self.request.GET.get("spot_slug")
        table_num = self.request.GET.get('table_num', None)

        if venue_slug:
            queryset = queryset.filter(venue__slug=venue_slug)
        if spot_slug:
            queryset = queryset.filter(spots__slug=spot_slug)
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

            venue_slug = request.data.get('venue_slug')
            spot_slug = request.data.get('spot_slug')
            table_num = request.data.get('table_num')

            if not venue_slug or not spot_slug or not table_num:
                return Response({'error': 'Venue slug, Spot slug and table number are required.'},
                                status=status.HTTP_400_BAD_REQUEST)

            venue = Venue.objects.filter(slug=venue_slug).first()
            if not venue:
                return Response({'error': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

            spot = Spot.objects.filter(venue=venue, slug=spot_slug).first()
            if not spot:
                return Response({'error': 'Spot not found.'}, status=status.HTTP_404_NOT_FOUND)

            table = Table.objects.filter(venue=venue, table_num=table_num).first()
            if not table:
                return Response({'error': 'Table not found.'}, status=status.HTTP_404_NOT_FOUND)

            order_data['table'] = table
            order_data['venue'] = venue
            order_data['spot'] = spot

            api_token = venue.access_token
            pos_system_name = venue.pos_system.name.lower()
            pos_service = POSServiceFactory.get_service(pos_system_name, api_token)
            order_data['spot'] = spot

            pos_response = pos_service.send_order_to_pos(order_data)
            if not pos_response:
                return Response({'error': 'POS system did not accept the order'},
                                status=status.HTTP_400_BAD_REQUEST)

            client = pos_service.get_or_create_client(venue, pos_response.get('client_id'))

            order_data['client'] = client
            order_data['external_id'] = pos_response.get('incoming_order_id')

            order = serializer.save()

            # if not send_receipt_to_webhook(order, venue, spot):
            #     logger.warning("Failed to send receipt to webhook.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Order creation failed due to an error: {str(e)}", exc_info=True)
            raise ValidationError({'detail': 'Order creation failed due to an internal error.'})
