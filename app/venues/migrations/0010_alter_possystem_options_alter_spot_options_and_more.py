# Generated by Django 5.1 on 2025-01-27 22:35

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0009_venue_tip_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='possystem',
            options={'verbose_name': 'Базовая модель', 'verbose_name_plural': 'Базовые модели'},
        ),
        migrations.AlterModelOptions(
            name='spot',
            options={'verbose_name': 'Базовая модель', 'verbose_name_plural': 'Базовые модели'},
        ),
        migrations.AddField(
            model_name='possystem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='possystem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления'),
        ),
        migrations.AddField(
            model_name='spot',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spot',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления'),
        ),
        migrations.AddField(
            model_name='table',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='table',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления'),
        ),
        migrations.AddField(
            model_name='venue',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venue',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления'),
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')),
                ('external_id', models.CharField(blank=True, max_length=100, verbose_name='Внешний ID зала')),
                ('hall_name', models.CharField(max_length=255, verbose_name='Название зала')),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='halls', to='venues.spot', verbose_name='Точка заведения')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='halls', to='venues.venue', verbose_name='Заведение')),
            ],
            options={
                'verbose_name': 'Зал',
                'verbose_name_plural': 'Залы',
            },
        ),
        migrations.AddField(
            model_name='table',
            name='hall',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='venues.hall', verbose_name='Зал'),
            preserve_default=False,
        ),
    ]
