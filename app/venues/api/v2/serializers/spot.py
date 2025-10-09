from rest_framework import serializers

from venues.models import Spot


class SpotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Spot
        fields = ('id', 'name', 'address', 'wifi_text', 'wifi_url')
