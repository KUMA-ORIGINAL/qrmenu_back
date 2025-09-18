from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from rest_framework import serializers

from ..serializers import OrderProductCreateSerializer, OrderProductSerializer
from ..models import Order, OrderProduct, Transaction, PaymentAccount, ServiceMode, BonusHistory
from ..services import generate_payment_link


class OrderCreateSerializer(serializers.ModelSerializer):
    order_products = OrderProductCreateSerializer(many=True, write_only=True)
    payment_url = serializers.SerializerMethodField(read_only=True)

    code = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    hash = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    phone_verification_hash = serializers.CharField(read_only=True)
    use_bonus = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Order
        fields = (
            'id', 'phone', 'comment', 'service_mode', 'address',
            'service_price', 'tips_price', 'bonus', 'spot', 'table',
            'is_tg_bot', 'tg_redirect_url', 'order_products',
            'payment_url', 'code', 'hash', 'phone_verification_hash', 'use_bonus'
        )
        extra_kwargs = {
            f: {'write_only': True}
            for f in fields if f not in ('id', 'payment_url', 'phone_verification_hash')
        }

    def create(self, validated_data):
        order_product_data = validated_data.pop('order_products', [])
        bonus = validated_data.get("bonus", 0) or 0
        validated_data.pop("code", None)
        validated_data.pop("use_bonus", None)
        validated_data.pop("hash", None)

        with transaction.atomic():  # 🚀 всё, что внутри, будет атомарно
            # --- создаём заказ ---
            order = Order.objects.create(**validated_data)
            products_total_price = Decimal('0.00')

            for item in order_product_data:
                product = item['product']
                modificator = item.get('modificator')
                count = item['count']

                price = Decimal(modificator.price) if modificator else Decimal(product.product_price)
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

            # сервисный сбор
            service_fee_percent = order.venue.service_fee_percent or Decimal('0.00')
            if not isinstance(service_fee_percent, Decimal):
                service_fee_percent = Decimal(str(service_fee_percent))
            service_price = (products_total_price * service_fee_percent / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            # доставка
            delivery_price = Decimal('0.00')
            if order.service_mode == ServiceMode.DELIVERY:
                delivery_fixed_fee = order.venue.delivery_fixed_fee or Decimal('0.00')
                delivery_free_from = order.venue.delivery_free_from
                delivery_price = (
                    Decimal('0.00')
                    if delivery_free_from and products_total_price >= delivery_free_from
                    else delivery_fixed_fee
                )

            # итоговая сумма
            total_price = (products_total_price + service_price + delivery_price).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            if bonus:
                applied_bonus = min(bonus, total_price)
                total_price = (total_price - applied_bonus).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                order.bonus = applied_bonus

            order.delivery_price = delivery_price
            order.service_price = service_price
            order.total_price = total_price
            order.save()

            # создаём транзакцию и платежный аккаунт
            transaction_obj = Transaction.objects.create(order=order, total_price=total_price)
            payment_account = PaymentAccount.objects.filter(venue=order.venue).first()

            # Передаём в context (для get_payment_url или других методов)
            self.context['transaction'] = transaction_obj
            self.context['payment_account'] = payment_account

        return order

    def get_payment_url(self, obj):
        transaction_obj = self.context.get('transaction')
        payment_account = self.context.get('payment_account')
        if transaction_obj:
            return generate_payment_link(transaction_obj, obj, payment_account)
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
