from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from ..models import Product
from ..serializers import ProductSerializer

@extend_schema(
    tags=['Product',],
    parameters=[
        OpenApiParameter(
            name='search',  # Имя параметра
            description='Поиск по product_name',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        )
    ]
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category',)

    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        search_query = self.request.GET.get("search")

        if search_query:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('product_name', search_query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

        return queryset
