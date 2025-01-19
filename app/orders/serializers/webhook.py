from rest_framework import serializers


class PosterWebhookSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=255)
    account_number = serializers.CharField(max_length=255)
    object = serializers.CharField(max_length=255)
    object_id = serializers.IntegerField()
    action = serializers.CharField(max_length=255)
    time = serializers.IntegerField()
    verify = serializers.CharField(max_length=255)
    data = serializers.CharField(required=False)
