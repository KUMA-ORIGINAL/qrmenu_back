from rest_framework import serializers

from .spot import SpotSerializer
from venues.models import Venue
from .table import TableSerializer
from .work_schedule import WorkScheduleSerializer


class VenueSerializer(serializers.ModelSerializer):
    spots = SpotSerializer(many=True)
    schedules = WorkScheduleSerializer(many=True)

    class Meta:
        model = Venue
        fields = (
            'color_theme',
            'company_name',
            'slug',
            'logo',
            'schedules',
            'delivery_service_fee_percent',   # ✅ новое поле
            'takeout_service_fee_percent',    # ✅ новое поле
            'dinein_service_fee_percent',     # ✅ новое поле
            'default_delivery_spot',
            'spots',
            'is_delivery_available',
            'is_takeout_available',
            'is_dinein_available',
            'delivery_fixed_fee',
            'delivery_free_from',
            'terms',
            'description',
            'is_bonus_system_enabled',
            'bonus_accrual_percent',
        )


class VenueWithTableSerializer(serializers.ModelSerializer):
    table = TableSerializer()
    schedules = WorkScheduleSerializer(many=True)

    class Meta:
        model = Venue
        fields = (
            'color_theme',
            'company_name',
            'slug',
            'logo',
            'schedules',
            'delivery_service_fee_percent',   # ✅ новое поле
            'takeout_service_fee_percent',    # ✅ новое поле
            'dinein_service_fee_percent',     # ✅ новое поле
            'is_delivery_available',
            'is_takeout_available',
            'is_dinein_available',
            'terms',
            'description',
            'is_bonus_system_enabled',
            'bonus_accrual_percent',
        )
