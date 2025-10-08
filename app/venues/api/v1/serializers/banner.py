from rest_framework import serializers
from venues.models import Banner


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'title', 'text', 'banner', 'image', 'url')
