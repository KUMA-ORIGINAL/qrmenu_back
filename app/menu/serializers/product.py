from rest_framework import serializers
from ..models import Product, Modificator, Category

class ModificatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modificator
        fields = ['id', 'external_id', 'modificator_name', 'modificator_selfprice']

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
            'id', 'external_id', 'product_name', 'product_description', 'product_price',
            'product_photo', 'hidden', 'category', 'modificators'
        ]

    def get_product_photo(self, obj):
        if obj.product_photo  and str(obj.product_photo).startswith('http'):
            return str(obj.product_photo)
        return f"{self.context['request'].build_absolute_uri('/')}{obj.product_photo}"