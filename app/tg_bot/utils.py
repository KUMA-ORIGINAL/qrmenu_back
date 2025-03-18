import requests
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_notification(chat_id, message):
    url = f'https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info(f"Message sent successfully to chat ID {chat_id}")
        else:
            logger.error(f"Failed to send message to {chat_id}: {response.text}")
    except Exception as e:
        logger.exception(f"An exception occurred when sending message to {chat_id}: {str(e)}")