from rest_framework import serializers
from ..models import WorkSchedule


class WorkScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)
    work_start = serializers.TimeField(format="%H:%M", input_formats=["%H:%M"])
    work_end = serializers.TimeField(format="%H:%M", input_formats=["%H:%M"])

    class Meta:
        model = WorkSchedule
        fields = ("day_of_week", "day_name", "work_start", "work_end", "is_day_off", 'is_24h')
