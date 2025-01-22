# Generated by Django 5.1 on 2025-01-22 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_alter_modificator_options_alter_product_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_recommended',
            field=models.BooleanField(default=False, verbose_name='Показывать в рекомендациях'),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Вес товара'),
        ),
    ]