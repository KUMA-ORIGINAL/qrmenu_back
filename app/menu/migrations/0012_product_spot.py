# Generated by Django 5.1 on 2025-02-11 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0011_alter_productattribute_name_and_more'),
        ('venues', '0010_alter_possystem_options_alter_spot_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='spot',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='venues.spot', verbose_name='Точка заведения'),
            preserve_default=False,
        ),
    ]
