from rest_framework import serializers
from ..models import Product, Modificator, Category


class ModificatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modificator
        fields = ['id', 'external_id', 'name', 'price']


class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name']


class ProductSerializer(serializers.ModelSerializer):
    modificators = ModificatorSerializer(many=True, read_only=True)
    category = CategoryShortSerializer(read_only=True)
    product_photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_description', 'product_price', 'weight',
            'product_photo', 'category', 'modificators'
        ]

    def get_product_photo(self, obj):
        if obj.product_photo  and str(obj.product_photo).startswith('http'):
            return str(obj.product_photo)
        return f"{self.context['request'].build_absolute_uri('/')}{obj.product_photo}"


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryShortSerializer(read_only=True)
    product_photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_price', 'weight', 'product_photo', 'category'
        ]

    def get_product_photo(self, obj):
        if obj.product_photo  and str(obj.product_photo).startswith('http'):
            return str(obj.product_photo)
        return f"{self.context['request'].build_absolute_uri('/')}{obj.product_photo}"