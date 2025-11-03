from urllib.parse import urlencode

from django.core.cache import cache
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from menu.models import Category
from menu.api.v2.serializers import CategorySerializer


@extend_schema(
    tags=['Category'],
    parameters=[
        OpenApiParameter(
            name='venue_slug',
            description='Фильтр по слагу заведения',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='section_id',
            description='Фильтр по ID раздела (пр. ?section_id=3)',
            required=False,
            type=int
        ),
    ]
)
class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = CategorySerializer

    def get_queryset(self):
        request = self.request
        venue_slug = request.GET.get("venue_slug")
        section_id = request.GET.get("section_id")

        if not venue_slug:
            raise ValidationError({'venue_slug': 'This parameter is required.'})

        queryset = Category.objects.select_related("venue").prefetch_related("sections")

        queryset = queryset.filter(
            venue__slug__iexact=venue_slug,
            category_hidden=False
        )

        if section_id:
            queryset = queryset.filter(sections__id=section_id)

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        venue_slug = request.GET.get("venue_slug")
        if not venue_slug:
            raise ValidationError({'venue_slug': 'This parameter is required.'})

        # формируем стабильный кеш‑ключ
        other_params = request.GET.copy()
        other_params.pop("venue_slug", None)
        params_str = urlencode(sorted(other_params.items()))  # упорядочиваем, чтобы порядок параметров не влиял
        cache_key = f"categories:{venue_slug.lower()}:{params_str}"

        data = cache.get(cache_key)

        if not data:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60 * 30)  # 30 минут

        return Response(data, status=status.HTTP_200_OK)


def get_categories(request):
    venue_id = request.GET.get('venue_id')
    categories = Category.objects.filter(venue_id=venue_id).values('id', 'category_name')
    return JsonResponse(list(categories), safe=False)
