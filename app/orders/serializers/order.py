from rest_framework import serializers

from ..serializers import OrderProductSerializer
from ..models import Order, OrderProduct


class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'phone', 'comment', 'service_mode', 'status', 'service_price', 'tips_price',
                  'created_at', 'order_products')

    def create(self, validated_data):
        order_products_data = validated_data.pop('order_products')
        order = Order.objects.create(**validated_data)

        for order_product_data in order_products_data:
            OrderProduct.objects.create(order=order, **order_product_data)

        return order
