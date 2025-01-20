# menu/serializers.py

from rest_framework import serializers
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
    category_photo = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'category_photo']

    def get_category_photo(self, obj):
        if obj.category_photo and str(obj.category_photo).startswith('http'):
            return str(obj.category_photo)
        return f"{self.context['request'].build_absolute_uri('/')}{obj.category_photo}"
