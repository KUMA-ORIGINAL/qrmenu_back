import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from account.models import ROLE_OWNER
from services.pos_service_factory import POSServiceFactory
from services.send_receipt_to_printer import send_receipt_to_webhook
from tg_bot.utils import send_order_notification
from venues.models import Venue, Table, Spot
from ..models import Order
from ..serializers import OrderSerializer
from ..utils import format_order_details

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

        order_data = serializer.validated_data
        venue_slug = request.data.get('venue_slug')
        spot_slug = request.data.get('spot_slug')
        table_num = request.data.get('table_num')

        if not all([venue_slug, spot_slug, table_num]):
            return Response({'error': 'Venue slug, spot slug, and table number are required.'},
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

        order_data.update({'table': table, 'venue': venue, 'spot': spot})

        pos_system_name = venue.pos_system.name.lower() if venue.pos_system else None

        if pos_system_name is None:
            try:
                order = serializer.save()
            except Exception as e:
                logger.error(f"Failed to save order: {str(e)}", exc_info=True)
                return Response({'error': 'Failed to save order due to internal error.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            user_owner = venue.users.filter(role=ROLE_OWNER).first()
            if user_owner and user_owner.tg_chat_id:
                order_info = format_order_details(order)
                logger.info(f"Attempting to send a Telegram message to {user_owner.tg_chat_id}")
                send_order_notification(user_owner.tg_chat_id, order_info)
            else:
                logger.info("No valid Telegram chat ID found or owner does not exist.")
        else:
            api_token = venue.access_token
            pos_service = POSServiceFactory.get_service(pos_system_name, api_token)

            pos_response = pos_service.send_order_to_pos(order_data)
            if not pos_response:
                return Response({'error': 'POS system did not accept the order'},
                                status=status.HTTP_400_BAD_REQUEST)

            client = pos_service.get_or_create_client(venue, pos_response.get('client_id'))
            if not client:
                return Response({'error': 'Failed to create or retrieve client from POS.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            order_data['client'] = client
            external_id = pos_response.get('incoming_order_id')
            if not external_id:
                return Response({'error': 'Failed to receive external ID from POS.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            order_data['external_id'] = external_id

            try:
                order = serializer.save()
            except Exception as e:
                logger.error(f"Failed to save order: {str(e)}", exc_info=True)
                return Response({'error': 'Failed to save order due to internal error.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Optionally handle webhook here
        # if not send_receipt_to_webhook(order, venue, spot):
        #     logger.warning("Failed to send receipt to webhook.")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

