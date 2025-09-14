from rest_framework import serializers
from ..models import WorkSchedule


class WorkScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)
    work_start = serializers.SerializerMethodField()
    work_end = serializers.SerializerMethodField()

    class Meta:
        model = WorkSchedule
        fields = (
            "day_of_week",
            "day_name",
            "work_start",
            "work_end",
            "is_day_off",
            "is_24h",
        )

    def get_work_start(self, obj):
        if obj.work_start:
            return obj.work_start.strftime("%H:%M") + " "  # пробел в конце
        return None

    def get_work_end(self, obj):
        if obj.work_end:
            return " " + obj.work_end.strftime("%H:%M")  # пробел в начале
        return None