# Generated by Django 5.1 on 2025-02-22 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('owner', 'Owner'), ('admin', 'Administrator')], max_length=20),
        ),
    ]
