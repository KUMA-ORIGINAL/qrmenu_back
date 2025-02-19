from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from ..models import Category
from ..serializers import CategorySerializer

@extend_schema(
    tags=['Сategory',],
    parameters=[
        OpenApiParameter(
            name='venue_name',  # Имя параметра
            description='Фильтр по имени заведения',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        ),
    ]
)
class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


    def get_queryset(self):
        queryset = Category.objects.select_related('venue')
        venue_name = self.request.GET.get("venue_name")

        if venue_name:
            queryset = queryset.filter(venue__company_name__icontains=venue_name)

        queryset = queryset.distinct()
        return queryset