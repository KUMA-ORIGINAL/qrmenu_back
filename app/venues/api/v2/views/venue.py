from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from venues.models import Venue, Spot
from venues.api.v2.serializers import TableSerializer
from venues.api.v2.serializers.venue import VenueSerializer


@extend_schema(tags=['Venue'])
class VenueViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Venue.objects.all().prefetch_related('spots')  # Оптимизация
    serializer_class = VenueSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'], url_path='table/(?P<table_id>[^/.]+)')
    def retrieve_by_table_id(self, request, slug=None, table_id=None):
        """
        Получить заведение (`Venue`) + информацию о столе (`Table`) по `table_id`.
        URL: `/api/venues/{slug}/table/{table_id}/`
        """
        venue = (
            Venue.objects
            .prefetch_related(Prefetch("spots", queryset=Spot.objects.filter(is_hidden=False)))
            .get(slug=slug.lower())
        )
        table = get_object_or_404(venue.tables, pk=table_id)

        venue_data = VenueSerializer(venue, context={'request': request}).data
        venue_data['table'] = TableSerializer(table, context={'request': request}).data

        return Response(venue_data)

    def get_object(self):
        slug = self.kwargs.get(self.lookup_field).lower()

        obj = self.get_queryset().filter(slug=slug).first()

        if not obj:
            raise NotFound(f"Заведение с slug '{slug}' не найдена")
        return obj
