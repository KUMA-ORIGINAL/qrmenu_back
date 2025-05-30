# Generated by Django 5.1 on 2025-04-27 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0024_alter_banner_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='is_delivery_available',
            field=models.BooleanField(default=True, verbose_name='Доставка доступна'),
        ),
        migrations.AddField(
            model_name='venue',
            name='is_dinein_available',
            field=models.BooleanField(default=True, verbose_name='Обслуживание на месте доступно'),
        ),
        migrations.AddField(
            model_name='venue',
            name='is_takeout_available',
            field=models.BooleanField(default=True, verbose_name='Самовывоз доступен'),
        ),
    ]
