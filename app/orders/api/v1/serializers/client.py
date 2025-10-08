from rest_framework import serializers


class ClientBonusSerializer(serializers.Serializer):
    phone_number = serializers.CharField(read_only=True)
    venue = serializers.CharField(read_only=True)
    bonus = serializers.IntegerField(read_only=True)
