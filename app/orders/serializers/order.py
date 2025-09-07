from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from ..serializers import OrderProductCreateSerializer, OrderProductSerializer
from ..models import Order, OrderProduct, Transaction, PaymentAccount, ServiceMode, BonusHistory
from ..services import generate_payment_link


class OrderCreateSerializer(serializers.ModelSerializer):
    order_products = OrderProductCreateSerializer(many=True, write_only=True)
    payment_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'phone', 'comment', 'service_mode', 'address', 'service_price',
            'tips_price', 'bonus', 'spot', 'table', 'is_tg_bot', 'tg_redirect_url',
            'order_products', 'payment_url',
        )
        extra_kwargs = {
            'phone': {'write_only': True},
            'comment': {'write_only': True},
            'service_mode': {'write_only': True},
            'address': {'write_only': True},
            'service_price': {'write_only': True},
            'tips_price': {'write_only': True},
            'bonus': {'write_only': True},
            'spot': {'write_only': True},
            'table': {'write_only': True},
            'is_tg_bot': {'write_only': True},
            'tg_redirect_url': {'write_only': True},
        }

    def create(self, validated_data):
        order_product_data = validated_data.pop('order_products', [])
        order = Order.objects.create(**validated_data)

        products_total_price = Decimal('0.00')

        for item in order_product_data:
            product = item['product']
            modificator = item.get('modificator')
            count = item['count']

            # Используем Decimal для финансовых расчётов
            if modificator:
                price = Decimal(modificator.price)
            else:
                price = Decimal(product.product_price)

            total_price = (price * count).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            OrderProduct.objects.create(
                order=order,
                product=product,
                modificator=modificator,
                count=count,
                price=price,
                total_price=total_price
            )

            products_total_price += total_price

        service_fee_percent = order.venue.service_fee_percent or Decimal('0.00')
        if not isinstance(service_fee_percent, Decimal):
            service_fee_percent = Decimal(str(service_fee_percent))

        service_price = (products_total_price * service_fee_percent / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        delivery_price = Decimal('0.00')
        if order.service_mode == ServiceMode.DELIVERY:
            delivery_fixed_fee = order.venue.delivery_fixed_fee or Decimal('0.00')
            delivery_free_from = order.venue.delivery_free_from

            if delivery_free_from and products_total_price >= delivery_free_from:
                delivery_price = Decimal('0.00')
            else:
                delivery_price = delivery_fixed_fee

        total_price = (products_total_price + service_price + delivery_price).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        order.delivery_price = delivery_price
        order.service_price = service_price
        order.total_price = total_price
        order.save()

        transaction = Transaction.objects.create(order=order, total_price=total_price)
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
