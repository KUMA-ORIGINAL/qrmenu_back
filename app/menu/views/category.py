from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from ..models import Category
from ..serializers import CategorySerializer


@extend_schema(
    tags=['Сategory',],
    parameters=[
        OpenApiParameter(
            name='venue_slug',  # Имя параметра
            description='Фильтр по слагу заведения',  # Описание параметра
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
        venue_slug = self.request.GET.get("venue_slug")

        if venue_slug:
            queryset = queryset.filter(venue__slug=venue_slug, category_hidden=False)

        queryset = queryset.distinct()
        return queryset


def get_categories(request):
    venue_id = request.GET.get('venue_id')
    categories = Category.objects.filter(venue_id=venue_id).values('id', 'category_name')
    return JsonResponse(list(categories), safe=False)