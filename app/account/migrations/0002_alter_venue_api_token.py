# Generated by Django 5.1 on 2025-01-06 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='api_token',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
