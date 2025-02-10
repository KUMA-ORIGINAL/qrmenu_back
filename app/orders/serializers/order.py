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
        order_product_data = validated_data.pop('order_products', [])
        order = Order.objects.create(**validated_data)

        for order_product_data_item in order_product_data:
            # product_attributes = order_product_data_item.pop('product_attributes', [])
            order_product = OrderProduct.objects.create(order=order, **order_product_data_item)

            # order_product.product_attributes.set(product_attributes)

            order_product.save()
        return order
