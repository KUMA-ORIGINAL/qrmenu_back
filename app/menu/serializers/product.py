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
    # product_attributes = ProductAttributeSerializer(many=True, read_only=True)
    modificators = ModificatorSerializer(many=True, read_only=True)
    category = CategoryShortSerializer(read_only=True)
    product_photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_description', 'product_price', 'weight',
            'product_photo', 'category', 'is_recommended', 'modificators'
        ]

    def get_product_photo(self, obj):
        if obj.product_photo  and str(obj.product_photo).startswith('http'):
            return str(obj.product_photo)
        return f"{self.context['request'].build_absolute_uri('/')}{MEDIA_URL[1:]}{obj.product_photo}"

