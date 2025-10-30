from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.db.models.functions import Lower
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from menu.models import Product
from menu.api.v2.serializers import ProductSerializer


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
    filterset_fields = ('categories',)

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
            .prefetch_related('categories', "modificators")
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

    def list(self, request, *args, **kwargs):
        venue_slug = request.GET.get("venue_slug")
        if not venue_slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'venue_slug': 'This parameter is required.'})

        other_params = request.GET.copy()
        other_params.pop("venue_slug", None)
        params_str = other_params.urlencode()
        cache_key = f"products:{venue_slug.lower()}:{params_str}"

        data = cache.get(cache_key)

        if not data:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60 * 30)  # кеш на 5 минут

        return Response(data, status=status.HTTP_200_OK)
