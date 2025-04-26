from rest_framework import serializers, request

from transactions.models import Transaction
from ..serializers import OrderProductCreateSerializer, OrderProductSerializer
from ..models import Order, OrderProduct
from ..services import generate_payment_link


class OrderCreateSerializer(serializers.ModelSerializer):
    order_products = OrderProductCreateSerializer(many=True, write_only=True)
    payment_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'phone', 'comment', 'service_mode', 'service_price',
                  'tips_price', 'spot', 'table', 'order_products', 'payment_url')
        extra_kwargs = {
            'phone': {'write_only': True},
            'comment': {'write_only': True},
            'service_mode': {'write_only': True},
            'service_price': {'write_only': True},
            'tips_price': {'write_only': True},
            'spot': {'write_only': True},  # Only write, no read
            'table': {'write_only': True},  # Only write, no read
        }

    def create(self, validated_data):
        order_product_data = validated_data.pop('order_products', [])
        order = Order.objects.create(**validated_data)

        for order_product_data_item in order_product_data:
            order_product = OrderProduct.objects.create(order=order, **order_product_data_item)
            order_product.save()

        total_amount = order.total_price
        transaction = Transaction.objects.create(order=order, total_price=total_amount)
        self.context['transaction'] = transaction

        return order

    def get_payment_url(self, obj):
        transaction = self.context.get('transaction')
        if transaction:
            return generate_payment_link(transaction)
        return None


class OrderListSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'order_products')
