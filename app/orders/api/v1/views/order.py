import logging
import random
from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from account.models import PhoneVerification
from account.services import send_sms
from venues.models import Venue
from orders.models import Order, OrderStatus
from orders.api.v1.serializers import OrderListSerializer, OrderCreateSerializer
from orders.services.order import is_within_schedule

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
                name='spot_id',  # Имя параметра
                description='Фильтр по slug точки',  # Описание параметра
                required=False,  # Параметр необязательный
                type=int  # Тип данных
            ),
            OpenApiParameter(
                name='table_id',  # Имя параметра
                description='Фильтр по номеру стола',  # Описание параметра
                required=False,  # Параметр необязательный
                type=int  # Тип данных
            ),
            OpenApiParameter(
                name='phone',  # Имя параметра
                description='Фильтр по номеру',  # Описание параметра
                required=False,  # Параметр необязательный
                type=str  # Тип данных
            )
        ]
    )
)
class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin):
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "retrieve":
            return queryset.prefetch_related(
                'order_products',
                'order_products__product',
                'order_products__product__modificators',
                'order_products__product__category',
            )

        venue_slug = self.request.GET.get('venue_slug', None)
        spot_id = self.request.GET.get("spot_id", None)
        table_id = self.request.GET.get('table_id', None)
        phone = self.request.GET.get('phone', None)

        if venue_slug:
            queryset = queryset.filter(venue__slug=venue_slug.lower())
        if spot_id:
            queryset = queryset.filter(spot__id=spot_id)
        if table_id:
            queryset = queryset.filter(table__id=table_id)
        if phone:
            queryset = queryset.filter(phone=phone)

        start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timezone.timedelta(days=1)

        queryset = queryset.filter(created_at__gte=start, created_at__lt=end)

        queryset = queryset.exclude(status=OrderStatus.WAITING_FOR_PAYMENT)

        return queryset.prefetch_related(
            'order_products',
            'order_products__product',
            'order_products__product__modificators',
            'order_products__product__category',
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        venue_slug = request.data.get('venue_slug')
        if not venue_slug:
            return Response({'error': 'venue_slug is required.'}, status=status.HTTP_400_BAD_REQUEST)

        venue = Venue.objects.filter(slug=venue_slug.lower()).first()
        if not venue:
            return Response({'error': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not is_within_schedule(venue):
            return Response({'error': 'Заказ можно создать только в рабочее время заведения.'},
                            status=status.HTTP_403_FORBIDDEN)

        # --- Проверка бонуса ---
        use_bonus = request.data.get('use_bonus')
        bonus = serializer.validated_data.get("bonus", 0) or 0
        phone = serializer.validated_data.get("phone")
        code = serializer.validated_data.get("code")
        hash_val = serializer.validated_data.get("hash")

        if bonus > 0 and use_bonus:
            pv = None

            # Если hash уже есть → значит ранее телефон подтвержден
            if hash_val:
                pv = PhoneVerification.objects.filter(
                    phone=phone,
                    hash=hash_val,
                    is_bonus_verified=True
                ).first()

            if not pv:  # нет подтверждения
                if code:  # пытаемся подтвердить введённый код
                    otp = PhoneVerification.objects.filter(
                        phone=phone,
                        is_verified=False
                    ).order_by('-created_at').first()

                    if not otp or otp.code != code:
                        return Response({"code": "Неверный код."}, status=status.HTTP_400_BAD_REQUEST)

                    if otp.created_at < timezone.now() - timedelta(minutes=5):
                        return Response({"code": "Код просрочен."}, status=status.HTTP_400_BAD_REQUEST)

                    # подтвердили код → генерим hash
                    generated_hash = otp.generate_hash()
                    phone_verification_hash = generated_hash
                else:

                    last_otp = PhoneVerification.objects.filter(
                        phone=phone
                    ).order_by('-created_at').first()

                    now = timezone.now()
                    if last_otp and last_otp.created_at > now - timedelta(seconds=60):
                        seconds_passed = (now - last_otp.created_at).total_seconds()
                        seconds_left = int(60 - seconds_passed)
                        return Response(
                            {
                                "error": "Код уже был отправлен недавно. Подождите минуту.",
                                "seconds_left": max(0, seconds_left)
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )

                    code_gen = f"{random.randint(1000, 9999)}"
                    otp = PhoneVerification.objects.create(phone=phone, code=code_gen)

                    text = f"Код подтверждения бонуса: {code_gen}"
                    send_sms(phone=phone, text=text)

                    return Response({
                        "status": "waiting_for_code",
                        "message": "Для списания бонусов нужно подтвердить телефон. Код отправлен в SMS.",
                    }, status=status.HTTP_200_OK)
            else:
                phone_verification_hash = pv.hash
        else:
            phone_verification_hash = None

        try:
            order = serializer.save(venue=venue)
        except Exception as e:
            logger.error(f"Failed to save order: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to save order due to internal error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        data = OrderCreateSerializer(
            order,
            context={'transaction': serializer.context.get('transaction'),
                     'payment_account': serializer.context.get('payment_account')}
        ).data
        if phone_verification_hash:
            data["phone_verification_hash"] = phone_verification_hash

        return Response(data, status=status.HTTP_201_CREATED)
