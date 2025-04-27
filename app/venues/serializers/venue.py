from rest_framework import serializers

from .spot import SpotSerializer
from ..models import Venue
from .table import TableSerializer


class VenueSerializer(serializers.ModelSerializer):
    spots = SpotSerializer(many=True)

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedule', 'service_fee_percent', 'spots',
                  'is_delivery_available', 'is_takeout_available', 'is_dinein_available')


class VenueWithTableSerializer(serializers.ModelSerializer):
    table = TableSerializer()

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedule', 'service_fee_percent',
                  'is_delivery_available', 'is_takeout_available', 'is_dinein_available')