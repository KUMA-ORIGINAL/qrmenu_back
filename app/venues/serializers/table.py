from rest_framework import serializers

from ..models import Table


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ('id', 'table_num')
