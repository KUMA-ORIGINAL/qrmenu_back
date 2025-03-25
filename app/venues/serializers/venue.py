from rest_framework import serializers

from ..models import Venue
from .table import TableSerializer


class VenueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedule')


class VenueWithTableSerializer(serializers.ModelSerializer):
    table = TableSerializer()

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedule')