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
    product_photo = serializers.SerializerMethodField()
    product_photo_small = serializers.SerializerMethodField()
    product_photo_large = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_description', 'product_price', 'weight',
            'product_photo', 'product_photo_small', 'product_photo_large',
            'category', 'is_recommended', 'modificators'
        ]

    def _build_url(self, image_field):
        if not image_field:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(image_field.url)
        return image_field.url

    def get_product_photo(self, obj):
        return self._build_url(obj.product_photo)

    def get_product_photo_small(self, obj):
        return self._build_url(obj.product_photo_small)

    def get_product_photo_large(self, obj):
        return self._build_url(obj.product_photo_large)
