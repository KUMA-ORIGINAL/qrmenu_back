# Generated by Django 5.1 on 2025-01-18 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_rename_modificator_name_modificator_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Цена товара'),
        ),
    ]