# Generated by Django 5.1 on 2025-01-14 19:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('venues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=100, verbose_name='Внешний ID товара')),
                ('category_name', models.CharField(max_length=255, verbose_name='Название категории')),
                ('category_photo', models.ImageField(blank=True, null=True, upload_to='menu/category/', verbose_name='Фото категории')),
                ('category_hidden', models.BooleanField(default=False, verbose_name='Скрыта ли категория')),
                ('pos_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venues.possystem', verbose_name='POS система')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='venues.venue', verbose_name='Заведение')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=100, verbose_name='Внешний ID товара')),
                ('product_name', models.CharField(max_length=255, verbose_name='Название товара')),
                ('product_description', models.TextField(blank=True, null=True, verbose_name='Описание товара')),
                ('product_photo', models.ImageField(blank=True, null=True, upload_to='menu/products/%Y/%m', verbose_name='Фото товара')),
                ('product_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, verbose_name='Цена товара')),
                ('hidden', models.BooleanField(default=False, verbose_name='Скрытый товар')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='menu.category', verbose_name='Категория')),
                ('pos_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venues.possystem', verbose_name='POS система')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='venues.venue', verbose_name='Заведение')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Продукты',
                'ordering': ['product_name'],
            },
        ),
        migrations.CreateModel(
            name='Modificator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=100, verbose_name='Внешний ID товара')),
                ('modificator_name', models.CharField(max_length=255)),
                ('modificator_selfprice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modificators', to='menu.product', verbose_name='Товар')),
            ],
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['venue'], name='menu_catego_venue_i_7b5ea0_idx'),
        ),
    ]
