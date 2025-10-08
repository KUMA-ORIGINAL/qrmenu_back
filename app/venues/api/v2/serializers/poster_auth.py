from rest_framework import serializers

class OAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()
    account = serializers.CharField()
