from rest_framework import serializers
from ..models import Client


class ClientBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["phone_number", "bonus"]
        