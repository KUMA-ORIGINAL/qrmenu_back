import requests
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def send_order_notification(chat_id, message, order_id):
    url = f'https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage'

    # Создаем Inline кнопки
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{order_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{order_id}")
        ]
    ])

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
        'reply_markup': keyboard.to_dict(),  # Важно привести к dict для requests
    }

    try:
        response = requests.post(url, json=data)  # Используем json вместо data
        if response.status_code == 200:
            logger.info(f"Message with order actions sent successfully to chat ID {chat_id}")
        else:
            logger.error(f"Failed to send order actions to {chat_id}: {response.text}")
    except Exception as e:
        logger.exception(f"An error occurred when sending order actions to {chat_id}: {str(e)}")
