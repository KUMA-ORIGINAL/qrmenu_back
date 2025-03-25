from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from venues.models import Venue, Table
from venues.serializers.table import TableSerializer
from venues.serializers.venue import VenueSerializer


class VenueViewSet(viewsets.GenericViewSet,
                   mixins.RetrieveModelMixin):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'], url_path='table/(?P<table_id>[^/.]+)')
    def retrieve_by_table_id(self, request, slug=None, table_id=None):
        """
        Получить заведение (`Venue`) + информацию о столе (`Table`) по `table_id`.
        URL: `/api/venues/{slug}/table/{table_id}/`
        """
        venue = get_object_or_404(Venue, slug=slug)
        table = get_object_or_404(Table, pk=table_id, venue=venue)  # Проверяем, что стол принадлежит заведению

        venue_data = VenueSerializer(venue).data
        venue_data['table'] = TableSerializer(table).data  # Добавляем данные о столе

        return Response(venue_data)