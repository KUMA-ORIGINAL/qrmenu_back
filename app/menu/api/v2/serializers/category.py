from rest_framework import serializers

from config.settings import MEDIA_URL
from menu.models import Category


class CategorySerializer(serializers.ModelSerializer):
    category_photo = serializers.SerializerMethodField()
    category_photo_small = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'slug', 'category_photo', 'category_photo_small']

    def get_category_photo(self, obj):
        # Если внешний URL
        if obj.category_photo and str(obj.category_photo).startswith('http'):
            return str(obj.category_photo)
        # Если локальный файл
        if obj.category_photo:
            return self.context['request'].build_absolute_uri(obj.category_photo.url)
        return None

    def get_category_photo_small(self, obj):
        # Для внешних URL нельзя сделать превью — возвращаем оригинал
        if obj.category_photo and str(obj.category_photo).startswith('http'):
            return str(obj.category_photo)
        # Для локального файла возвращаем уменьшенную версию
        if obj.category_photo_small:
            return self.context['request'].build_absolute_uri(obj.category_photo_small.url)
        return None
