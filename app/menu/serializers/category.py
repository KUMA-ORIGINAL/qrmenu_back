# menu/serializers.py

from rest_framework import serializers
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
    category_photo = serializers.CharField()

    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'category_photo']
