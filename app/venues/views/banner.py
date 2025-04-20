from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins

from ..models import Banner
from ..serializers import BannerSerializer


@extend_schema(
    tags=['Banner',],
    parameters=[
        OpenApiParameter(
            name='venue_slug',  # Имя параметра
            description='Фильтр по слагу заведения',  # Описание параметра
            required=False,  # Параметр необязательный
            type=str  # Тип данных
        ),
    ]
)
class BannerViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,):
    serializer_class = BannerSerializer

    def get_queryset(self):
        queryset = Banner.objects.select_related('venue')
        venue_slug = self.request.GET.get("venue_slug")

        if venue_slug:
            queryset = queryset.filter(venue__slug=venue_slug)

        queryset = queryset.filter(status="active")

        return queryset.distinct()
