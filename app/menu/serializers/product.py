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


class AbsoluteImageSerializerField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        value_str = str(value)
        if value_str.startswith("http"):
            return value_str
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(value.url)
        return value.url


class ProductSerializer(serializers.ModelSerializer):
    modificators = ModificatorSerializer(many=True, read_only=True)
    category = CategoryShortSerializer(read_only=True)

    product_photo = AbsoluteImageSerializerField(read_only=True)
    product_photo_small = AbsoluteImageSerializerField(read_only=True)
    product_photo_large = AbsoluteImageSerializerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_description', 'product_price', 'weight',
            'product_photo', 'product_photo_small', 'product_photo_large',
            'category', 'is_recommended', 'modificators'
        ]
