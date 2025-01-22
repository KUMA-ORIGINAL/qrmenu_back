# Generated by Django 5.1 on 2025-01-20 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_external_id_alter_order_service_mode'),
        ('venues', '0005_alter_table_table_shape'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='external_id',
            field=models.CharField(default=1, max_length=100, verbose_name='Внешний ID клиента'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='venue',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='venues.venue', verbose_name='Заведение'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='orders', to='orders.client'),
            preserve_default=False,
        ),
    ]