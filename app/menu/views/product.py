from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Lower
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins

from ..models import Product
from ..serializers import ProductSerializer


@extend_schema(
    tags=['Product',],
    parameters=[
        OpenApiParameter(
            name='venue_slug',  # Имя параметра
            description='Фильтр по slug заведения',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        ),
        OpenApiParameter(
            name='spot_id',  # Имя параметра
            description='Фильтр по id точки',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        ),
        OpenApiParameter(
            name='search',  # Имя параметра
            description='Поиск по product_name',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        )
    ]
)
class ProductViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category',)

    def get_queryset(self):
        request = self.request
        venue_slug = request.GET.get("venue_slug")
        search_query = request.GET.get("search")
        spot_id = request.GET.get("spot_id")

        if not venue_slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'venue_slug': 'This parameter is required.'})

        # фильтруем сразу только актуальные продукты конкретного venue
        qs = (
            Product.objects
            .filter(venue__slug__iexact=venue_slug, hidden=False)
            .select_related("category", "venue")
            .prefetch_related("modificators")
        )

        if spot_id:
            qs = qs.filter(spots__id=spot_id)

        if search_query:
            qs = (
                qs.annotate(
                    similarity=TrigramSimilarity(
                        Lower('product_name'), search_query.lower()
                    )
                )
                .filter(similarity__gt=0.1)
                .order_by('-similarity')
            )

        return qs.distinct()
