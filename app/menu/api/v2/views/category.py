from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins
from menu.models import Category
from menu.api.v2.serializers import CategorySerializer


@extend_schema(
    tags=['Сategory',],
    parameters=[
        OpenApiParameter(
            name='venue_slug',  # Имя параметра
            description='Фильтр по слагу заведения',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        ),
        OpenApiParameter(
            name='section_id',
            description='Фильтр по ID раздела (пр. ?section_id=3)',
            required=False,
            type=int,
        ),
    ]
)
class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.select_related('venue')
        request = self.request
        venue_slug = request.GET.get("venue_slug")
        section_id = request.GET.get("section_id")

        if venue_slug:
            queryset = queryset.filter(
                venue__slug=venue_slug.lower(),
                category_hidden=False
            )

        if section_id:
            queryset = queryset.filter(
                sections__id=section_id
            )

        return queryset.distinct()


def get_categories(request):
    venue_id = request.GET.get('venue_id')
    categories = Category.objects.filter(venue_id=venue_id).values('id', 'category_name')
    return JsonResponse(list(categories), safe=False)
