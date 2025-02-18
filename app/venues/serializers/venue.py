from rest_framework import serializers

from venues.models import Venue


class VenueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'logo', 'schedule')
