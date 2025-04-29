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
        queryset = Product.objects.select_related('category', 'venue') \
            .prefetch_related('spots', 'modificators')

        search_query = self.request.GET.get("search")
        venue_slug = self.request.GET.get("venue_slug")
        spot_id = self.request.GET.get("spot_id")

        if not venue_slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'venue_slug': 'This parameter is required.'})

        queryset = queryset.filter(venue__slug=venue_slug)

        if spot_id:
            queryset = queryset.filter(spots__id=spot_id)

        queryset = queryset.distinct()

        if search_query:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity(Lower('product_name'), search_query.lower()),
            ).filter(similarity__gt=0.1).order_by('-similarity')

        return queryset
