import requests
import logging
from requests.adapters import HTTPAdapter, Retry
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=2,                     # 1-я ошибка → 2с, 2-я → 4с, 3-я → 8с
    status_forcelist=(500, 502, 503, 504),
    allowed_methods=("POST",),
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)


# ---- 2. Функция отправки ----
def send_telegram_message(
    chat_id: int,
    text: str,
    buttons: list | None = None,
    parse_mode: str | None = "Markdown",
) -> bool:
    """
    Универсальная отправка сообщения в Telegram с обработкой ошибок и повторными попытками.
    """

    token = getattr(settings, "TG_BOT_TOKEN", None)
    if not token:
        logger.error("TG_BOT_TOKEN не задан в настройках!")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Ограничиваем длину (Telegram: ≤4096 символов)
    if len(text) > 4096:
        logger.warning("Сообщение слишком длинное, будет обрезано.")
        text = text[:4093] + "..."

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }

    if buttons:
        try:
            payload["reply_markup"] = InlineKeyboardMarkup(buttons).to_dict()
        except Exception:
            logger.exception("Ошибка при формировании клавиатуры Telegram")
            return False

    try:
        response = session.post(url, json=payload, timeout=10)
        try:
            data = response.json()
        except ValueError:
            logger.error(f"Некорректный JSON от Telegram: {response.text}")
            return False

        if response.ok and data.get("ok"):
            logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
            return True

        logger.error(
            f"Ошибка от Telegram (chat={chat_id}): код={response.status_code}, ответ={data}"
        )
        return False

    except requests.exceptions.RequestException as e:
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
        f"🍽 Подойдите к столу: *{table.table_num}*\n"
    )

    buttons = [
        [InlineKeyboardButton("🙋‍♂️ Принять вызов", callback_data=f"call_waiter:{table.id}")]
    ]

    return send_telegram_message(spot.telegram_chat_id, text, buttons)
