# Generated by Django 5.1 on 2025-03-18 20:55

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_user_tg_chat_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='phone number'),
        ),
    ]
