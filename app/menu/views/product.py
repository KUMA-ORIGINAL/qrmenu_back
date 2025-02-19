from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
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
            name='venue_name',  # Имя параметра
            description='Фильтр по имени заведения',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        ),
        OpenApiParameter(
            name='spot_name',  # Имя параметра
            description='Фильтр по номеру зоны',  # Описание параметра
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
        queryset = Product.objects.select_related('category', 'venue').prefetch_related('spots')
        search_query = self.request.GET.get("search")
        venue_name = self.request.GET.get("venue_name")
        spot_name = self.request.GET.get("spot_name")

        if venue_name:
            queryset = queryset.filter(venue__company_name__icontains=venue_name)

        if spot_name:
            queryset = queryset.filter(spots__name__icontains=spot_name)

        queryset = queryset.distinct()

        if search_query:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity(Lower('product_name'), search_query.lower()),
            ).filter(similarity__gt=0.1).order_by('-similarity')


        return queryset
