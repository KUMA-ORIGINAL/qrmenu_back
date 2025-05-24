from rest_framework import serializers

from ..serializers import OrderProductCreateSerializer, OrderProductSerializer
from ..models import Order, OrderProduct, Transaction, PaymentAccount
from ..services import generate_payment_link


class OrderCreateSerializer(serializers.ModelSerializer):
    order_products = OrderProductCreateSerializer(many=True, write_only=True)
    payment_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'phone', 'comment', 'service_mode', 'address', 'service_price',
            'tips_price', 'spot', 'table', 'is_tg_bot', 'tg_redirect_url',
            'order_products', 'payment_url',
        )
        extra_kwargs = {
            'phone': {'write_only': True},
            'comment': {'write_only': True},
            'service_mode': {'write_only': True},
            'address': {'write_only': True},
            'service_price': {'write_only': True},
            'tips_price': {'write_only': True},
            'spot': {'write_only': True},
            'table': {'write_only': True},
            'is_tg_bot': {'write_only': True},
            'tg_redirect_url': {'write_only': True},
        }

    def create(self, validated_data):
        order_product_data = validated_data.pop('order_products', [])
        order = Order.objects.create(**validated_data)

        order_products = [
            OrderProduct(order=order, **item)
            for item in order_product_data
        ]
        OrderProduct.objects.bulk_create(order_products)

        total_amount = order.total_price

        transaction = Transaction.objects.create(order=order, total_price=total_amount)
        payment_account = PaymentAccount.objects.filter(venue=order.venue).first()

        self.context['transaction'] = transaction
        self.context['payment_account'] = payment_account

        return order

    def get_payment_url(self, obj):
        transaction = self.context.get('transaction')
        payment_account = self.context.get('payment_account')
        if transaction:
            return generate_payment_link(transaction, obj, payment_account)
        return None


class OrderListSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)
    table_num = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'total_price', 'status', 'created_at', 'service_mode',
            'address', 'comment', 'phone', 'order_products', 'table_num', 'status_text'
        )

    def get_table_num(self, obj):
        if obj.table:
            return obj.table.table_num
        return ''

    def get_status_text(self, obj):
        return obj.get_status_display()
