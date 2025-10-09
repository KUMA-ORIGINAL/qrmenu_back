from rest_framework import serializers

from menu.models import Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id',)
