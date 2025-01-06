from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins
from ..models import Category
from ..serializers import CategorySerializer

@extend_schema(tags=['Сategory',])
class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer