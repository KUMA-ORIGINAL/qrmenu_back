# Generated by Django 5.1 on 2025-03-11 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0017_receiptprinter'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='telegram_bot_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Telegram Bot Токен'),
        ),
        migrations.AddField(
            model_name='venue',
            name='telegram_chat_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Chat ID'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='access_token',
            field=models.CharField(max_length=255, verbose_name='Токен доступа для POS-системы'),
        ),
    ]
