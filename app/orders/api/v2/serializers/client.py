from rest_framework import serializers

from orders.models import Client


class ClientBonusSerializer(serializers.Serializer):
    phone_number = serializers.CharField(read_only=True)
    venue = serializers.CharField(read_only=True)
    bonus = serializers.IntegerField(read_only=True)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'firstname', 'lastname', 'patronymic', 'email')
