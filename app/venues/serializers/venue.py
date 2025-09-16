from rest_framework import serializers

from .spot import SpotSerializer
from ..models import Venue
from .table import TableSerializer
from .work_schedule import WorkScheduleSerializer


class VenueSerializer(serializers.ModelSerializer):
    spots = SpotSerializer(many=True)
    schedules = WorkScheduleSerializer(many=True)

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedules', 'service_fee_percent', 'default_delivery_spot', 'spots',
                  'is_delivery_available', 'is_takeout_available', 'is_dinein_available', 'delivery_fixed_fee', 'delivery_free_from',
                  'terms', 'description')


class VenueWithTableSerializer(serializers.ModelSerializer):
    table = TableSerializer()
    schedules = WorkScheduleSerializer(many=True)

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedules', 'service_fee_percent',
                  'is_delivery_available', 'is_takeout_available', 'is_dinein_available',
                  'terms', 'description')
