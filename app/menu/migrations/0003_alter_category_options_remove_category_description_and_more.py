# Generated by Django 5.1 on 2025-01-06 22:11

import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_venue_api_token'),
        ('menu', '0002_remove_product_source_category_venue_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
        migrations.RemoveField(
            model_name='category',
            name='name',
        ),
        migrations.AddField(
            model_name='category',
            name='category_hidden',
            field=models.BooleanField(default=False, verbose_name='Скрыта ли категория'),
        ),
        migrations.AddField(
            model_name='category',
            name='category_id',
            field=models.CharField(default=1, max_length=100, unique=True, verbose_name='ID категории'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='category_name',
            field=models.CharField(default=1, max_length=255, verbose_name='Название категории'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='category_photo',
            field=models.ImageField(blank=True, null=True, upload_to='menu/category/', verbose_name='Фото категории'),
        ),
        migrations.AddField(
            model_name='category',
            name='category_photo_origin',
            field=models.ImageField(blank=True, null=True, upload_to='menu/category/', verbose_name='Оригинальное фото категории'),
        ),
        migrations.AddField(
            model_name='category',
            name='level',
            field=models.PositiveIntegerField(default=1, verbose_name='Уровень категории'),
        ),
        migrations.AddField(
            model_name='category',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='parent_category',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategories', to='menu.category', verbose_name='Родительская категория'),
        ),
        migrations.AddField(
            model_name='category',
            name='rght',
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='visible',
            field=models.JSONField(default=list, verbose_name='Видимость категории на точках'),
        ),
        migrations.AlterField(
            model_name='category',
            name='venue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='account.venue', verbose_name='Заведение'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['venue'], name='menu_catego_venue_i_7b5ea0_idx'),
        ),
    ]
