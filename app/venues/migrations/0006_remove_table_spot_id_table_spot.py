# Generated by Django 5.1 on 2025-01-21 21:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0005_alter_table_table_shape'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='table',
            name='spot_id',
        ),
        migrations.AddField(
            model_name='table',
            name='spot',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='venues.spot'),
            preserve_default=False,
        ),
    ]
