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
    # product_attributes = ProductAttributeSerializer(many=True, read_only=True)
    modificators = ModificatorSerializer(many=True, read_only=True)
    category = CategoryShortSerializer(read_only=True)
    # product_photo = serializers.SerializerMethodField(read_only=True)
    # product_photo_small = serializers.SerializerMethodField(read_only=True)
    # product_photo_large = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_description', 'product_price', 'weight',
            'product_photo', 'product_photo_small', 'product_photo_large', 'category', 'is_recommended', 'modificators'
        ]

    # def get_product_photo(self, obj):
    #     if obj.product_photo and str(obj.product_photo).startswith('http'):
    #         return str(obj.product_photo)
    #     if obj.product_photo:
    #         return self.context['request'].build_absolute_uri(obj.product_photo.url)
    #     return None
    #
    # def get_product_photo_small(self, obj):
    #     if obj.product_photo and str(obj.product_photo).startswith('http'):
    #         # Превью не делаем, возвращаем оригинал
    #         return str(obj.product_photo)
    #     if obj.product_photo_small:
    #         return self.context['request'].build_absolute_uri(obj.product_photo_small.url)
    #     return None
    #
    # def get_product_photo_large(self, obj):
    #     if obj.product_photo and str(obj.product_photo).startswith('http'):
    #         return str(obj.product_photo)
    #     if obj.product_photo_large:
    #         return self.context['request'].build_absolute_uri(obj.product_photo_large.url)
    #     return None
