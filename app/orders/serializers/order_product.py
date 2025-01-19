from rest_framework import serializers

from orders.models import OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = ('product', 'count', 'modificator')
