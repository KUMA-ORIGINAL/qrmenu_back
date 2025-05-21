from rest_framework import serializers

from .spot import SpotSerializer
from ..models import Venue
from .table import TableSerializer


class VenueSerializer(serializers.ModelSerializer):
    spots = SpotSerializer(many=True)
    schedule = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedule', 'service_fee_percent', 'spots',
                  'is_delivery_available', 'is_takeout_available', 'is_dinein_available')

    def get_schedule(self, obj):
        if obj.work_start and obj.work_end:
            return f"{obj.work_start.strftime('%H:%M')}-{obj.work_end.strftime('%H:%M')}"
        return None


class VenueWithTableSerializer(serializers.ModelSerializer):
    table = TableSerializer()
    schedule = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = ('color_theme', 'company_name', 'slug', 'logo', 'schedule', 'service_fee_percent',
                  'is_delivery_available', 'is_takeout_available', 'is_dinein_available')

    def get_schedule(self, obj):
        if obj.work_start and obj.work_end:
            return f"{obj.work_start.strftime('%H:%M')}-{obj.work_end.strftime('%H:%M')}"
        return None