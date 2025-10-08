from rest_framework import serializers

from venues.models import Table


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ('id', 'table_num')
