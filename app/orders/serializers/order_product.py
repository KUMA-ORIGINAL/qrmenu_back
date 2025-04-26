from rest_framework import serializers

from config.settings import MEDIA_URL
from menu.models import Product
from orders.models import OrderProduct


class OrderProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = ('product', 'count', 'modificator')


class ProductSerializer(serializers.ModelSerializer):
    product_photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'weight', 'product_photo',
        ]

    def get_product_photo(self, obj):
        if obj.product_photo  and str(obj.product_photo).startswith('http'):
            return str(obj.product_photo)
        return f"{self.context['request'].build_absolute_uri('/')}{MEDIA_URL[1:]}{obj.product_photo}"


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderProduct
        fields = ('product', 'count', 'price', 'modificator')