from rest_framework import viewsets, mixins

from venues.models import Venue
from venues.serializers.venue import VenueSerializer


class VenueViewSet(viewsets.GenericViewSet,
                   mixins.RetrieveModelMixin):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    lookup_field = 'slug'
