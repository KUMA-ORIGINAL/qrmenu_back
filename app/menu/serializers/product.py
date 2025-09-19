from rest_framework import serializers

from config.settings import MEDIA_URL
from ..models import Product, Modificator, Category, ProductAttribute


class ModificatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modificator
        fields = ['id', 'name', 'price']


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'price']


class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name']


class ProductSerializer(serializers.ModelSerializer):
    modificators = ModificatorSerializer(many=True, read_only=True)
    category = CategoryShortSerializer(read_only=True)
    product_photo_small = serializers.ImageField(read_only=True)
    product_photo_large = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_description', 'product_price', 'weight',
            'product_photo', 'product_photo_small', 'product_photo_large',
            'category', 'is_recommended', 'modificators'
        ]
