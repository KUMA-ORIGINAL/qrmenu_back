# Generated by Django 5.1 on 2025-05-01 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_user_full_name_alter_user_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-date_joined'], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
