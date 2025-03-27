from rest_framework import serializers

from ..serializers import OrderProductSerializer
from ..models import Order, OrderProduct
from ..services import generate_payment_link


class OrderCreateSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True)
    payment_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'phone', 'comment', 'service_mode', 'status', 'service_price',
                  'tips_price', 'order_products', 'payment_url')

    def create(self, validated_data):
        order_product_data = validated_data.pop('order_products', [])
        order = Order.objects.create(**validated_data)

        for order_product_data_item in order_product_data:
            # product_attributes = order_product_data_item.pop('product_attributes', [])
            order_product = OrderProduct.objects.create(order=order, **order_product_data_item)

            # order_product.product_attributes.set(product_attributes)

            order_product.save()
        return order

    def get_payment_url(self, obj):
        return generate_payment_link(obj)  # 👈 Тут вызываем функцию генерации URL


class OrderListSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'order_products')
