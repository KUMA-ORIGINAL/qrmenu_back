# Generated by Django 5.1 on 2025-01-21 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_alter_category_category_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Внешний ID товара'),
        ),
        migrations.AlterField(
            model_name='product',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Внешний ID товара'),
        ),
    ]