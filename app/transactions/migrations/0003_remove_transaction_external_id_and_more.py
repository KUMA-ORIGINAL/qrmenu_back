# Generated by Django 5.1 on 2025-03-29 06:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transaction_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='external_id',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='pay_method',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_link',
        ),
    ]
