# menu/serializers.py

from rest_framework import serializers
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'category_photo', 'category_photo_origin']
