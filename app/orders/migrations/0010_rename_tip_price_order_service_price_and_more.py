# Generated by Django 5.1 on 2025-01-25 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_order_bonus_order_discount_order_tip_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='tip_price',
            new_name='service_price',
        ),
        migrations.AddField(
            model_name='order',
            name='tips_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Чаевые'),
        ),
    ]
