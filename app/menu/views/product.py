from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from ..models import Product
from ..serializers import ProductSerializer

@extend_schema(tags=['Product',])
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

