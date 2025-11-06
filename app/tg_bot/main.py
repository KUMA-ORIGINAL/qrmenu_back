import logging
import re

from asgiref.sync import sync_to_async
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from account.models import User
from orders.models import Order, ServiceMode
from orders.services import notify_order_status, build_yandex_taxi_link

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_phone(phone: str) -> str:
    phone = re.sub(r'\D', '', phone)  # Оставляем только цифры
    if not phone.startswith('+'):
        phone = f"+{phone}"
    return phone


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = await sync_to_async(User.objects.filter(tg_chat_id=chat_id).first)()

    if user and user.phone_number:
        await update.message.reply_text(f"Добро пожаловать обратно! Ваш номер: {user.phone_number}.")
    else:
        contact_keyboard = KeyboardButton("📲 Отправить мой номер", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True)
        await update.message.reply_text(
            "Добро пожаловать! Пожалуйста, отправьте свой номер телефона для регистрации.",
            reply_markup=keyboard
        )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone_number = contact.phone_number if contact else None

    if not phone_number:
        await update.message.reply_text("Ошибка! Не удалось получить номер телефона.")
        return

    phone_number = normalize_phone(phone_number)
    logger.info(f'Получен номер телефона: {phone_number}')

    user = await sync_to_async(User.objects.filter(phone_number=phone_number).first)()

    if user:
        user.tg_chat_id = update.effective_chat.id
        await sync_to_async(user.save)()
        message = "✅ Вы успешно зарегистрированы!"
        logger.info(f"Пользователь {user.phone_number} зарегистрирован в боте с chat_id {update.effective_chat.id}")
    else:
        message = "❌ Вас нет в системе."

    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())


STATUS_ACTIONS = {
    "accept_": {
        "status": 1,
        "next_button": lambda order_id: [
            InlineKeyboardButton("🍽 Готово", callback_data=f"ready_{order_id}")
        ],
    },
    "ready_": {
        "status": 2,
        "next_button": lambda order_id: [
            InlineKeyboardButton("✅ Выполнено", callback_data=f"complete_{order_id}")
        ],
    },
    "complete_": {
        "status": 3,
        "next_button": lambda order_id: [
            InlineKeyboardButton("✔ Заказ завершён", callback_data="noop")
        ],
    },
    "reject_": {
        "status": 7,
        "next_button": lambda order_id: [
            InlineKeyboardButton("❌ Отклонено", callback_data="noop")
        ],
    },
}


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "noop":
        await query.answer("Это действие уже выполнено.")
        return

    logger.info(f"Callback query received: {data}")

    # находим ключ из STATUS_ACTIONS
    action_key = next((key for key in STATUS_ACTIONS if data.startswith(key)), None)
    if not action_key:
        await query.answer("Неизвестное действие.", show_alert=True)
        return

    order_id = data.split("_")[1]
    order = await sync_to_async(
        lambda: Order.objects.select_related("spot").filter(id=order_id).first()
    )()
    if not order:
        await query.answer("❗ Заказ не найден.", show_alert=True)
        return

    # применяем действие
    conf = STATUS_ACTIONS[action_key]
    new_status = conf["status"]
    buttons = conf["next_button"](order_id)

    if action_key == "accept_" and order.service_mode == ServiceMode.DELIVERY:
        taxi_link = build_yandex_taxi_link(order)
        logger.info(f"[Order {order.id}] Generated taxi link: {taxi_link}")
        if taxi_link:
            buttons.append(InlineKeyboardButton("🚖 Вызвать такси", url=taxi_link))

    order.status = new_status
    await sync_to_async(order.save)()
    await notify_order_status(order)

    logger.info(f"Order {order_id} updated to status '{new_status}'")

    # обновляем reply markup (все кнопки в один ряд)
    markup = InlineKeyboardMarkup([buttons])
    await query.edit_message_reply_markup(reply_markup=markup)


async def handle_call_waiter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # формата call_waiter:<table_id>
    try:
        _, table_id = data.split(":")
    except ValueError:
        await query.answer("Ошибка данных.", show_alert=True)
        return

    user = query.from_user  # это Telegram-пользователь
    waiter_name = user.full_name or user.username or "Официант"

    # Делаем новую кнопку с именем кто принял
    new_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {waiter_name} принял заказ", callback_data="noop")]
    ])

    # Обновляем сообщение, чтобы заменить кнопку
    await query.edit_message_reply_markup(reply_markup=new_markup)

    logger.info(f"🧾 Официант {waiter_name} принял вызов к столу {table_id}")


def setup_bot(token: str):
    """Настраивает бота"""
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(CallbackQueryHandler(handle_call_waiter_callback, pattern="^call_waiter:"))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    return app
