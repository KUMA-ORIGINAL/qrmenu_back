import requests
import logging
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, text, buttons=None, parse_mode="Markdown") -> bool:
    """
    Универсальная отправка сообщения в Telegram
    """
    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }

    if buttons:
        payload["reply_markup"] = InlineKeyboardMarkup(buttons).to_dict()

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
            return True
        else:
            logger.error(f"Ошибка при отправке в чат {chat_id}: {response.text}")
            return False
    except Exception as e:
        logger.exception(f"Ошибка сети при отправке Telegram-сообщения: {e}")
        return False


def send_order_notification(chat_id, message, order_id):
    """Отправка уведомления о заказе с кнопками"""
    buttons = [
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{order_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{order_id}")
        ]
    ]
    return send_telegram_message(chat_id, message, buttons)


def notify_waiter(table):
    """Отправка уведомления официанту"""
    spot = getattr(table, "spot", None)
    if not spot or not spot.telegram_chat_id:
        logger.warning(f"У стола {table.id} нет chat_id или Spot")
        return False

    text = (
        f"📢 *Вызов официанта!*\n\n"
        f"🏠 Точка: *{spot.name}*\n"
        f"🍽 Стол: *{table.table_num}*\n"
        f"📍 Адрес: {spot.address or '-'}"
    )

    # можно добавить кнопку "✅ Принять" прямо здесь
    # buttons = [
    #     [InlineKeyboardButton("✅ Принять вызов", callback_data=f"waiter_accept_{table.id}")]
    # ]

    return send_telegram_message(spot.telegram_chat_id, text)
