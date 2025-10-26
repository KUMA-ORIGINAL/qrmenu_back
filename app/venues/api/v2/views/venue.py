from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import viewsets, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from venues.models import Venue, Spot
from venues.api.v2.serializers import TableSerializer
from venues.api.v2.serializers.venue import VenueSerializer


@extend_schema(tags=['Venue'])
class VenueViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """
    API для работы с заведениями (Venue).

    Поддерживает получение данных о конкретном заведении по его `slug`.
    Можно передать параметр `table_id`, чтобы дополнительно получить данные выбранного стола.
    """
    queryset = Venue.objects.all().prefetch_related('spots')
    serializer_class = VenueSerializer
    lookup_field = 'slug'

    @extend_schema(
        summary="Получить данные о заведении (и, опционально, о столе)",
        description=(
            "Возвращает информацию о заведении по `slug`. "
            "Если указан параметр `tableId`, дополнительно возвращает информацию о конкретном столе.\n\n"
            "**Примеры запросов:**\n"
            "- `/api/venues/london-bar/`\n"
            "- `/api/venues/london-bar/?tableId=42`"
        ),
        parameters=[
            OpenApiParameter(
                name='table_id',
                description='Идентификатор стола (необязательный параметр)',
                required=False,
                type=int,
            ),
        ],
        examples=[
            OpenApiExample(
                'Без стола',
                summary='Получение только заведения',
                description='Возвращает данные о заведении London Bar.',
                value={'slug': 'london-bar'}
            ),
            OpenApiExample(
                'С указанием стола',
                summary='Получение заведения и конкретного стола',
                description='Возвращает заведение London Bar и стол с ID 12.',
                value={'slug': 'london-bar', 'table_id': 12}
            )
        ],
        responses={200: VenueSerializer},
    )
    def retrieve(self, request, slug=None):
        """
        Получить заведение (`Venue`) и, если указан ?table_id= — добавить информацию о столе (`Table`).

        **Примеры:**
        - `/api/venues/{slug}/`
        - `/api/venues/{slug}/?table_id={id}`
        """
        venue = get_object_or_404(
            Venue.objects.prefetch_related(
                Prefetch("spots", queryset=Spot.objects.filter(is_hidden=False))
            ),
            slug=slug.lower()
        )

        data = VenueSerializer(venue, context={'request': request}).data
        table_id = request.query_params.get('table_id')

        if table_id:
            table = get_object_or_404(venue.tables, pk=table_id)
            data["table"] = TableSerializer(table, context={'request': request}).data

        return Response(data)

    def get_object(self):
        slug = self.kwargs.get(self.lookup_field).lower()
        obj = self.get_queryset().filter(slug=slug).first()
        if not obj:
            raise NotFound(f"Заведение с slug '{slug}' не найдено")
        return obj
