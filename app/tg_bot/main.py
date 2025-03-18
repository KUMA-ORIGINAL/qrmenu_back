import logging
import re

from asgiref.sync import sync_to_async
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from account.models import User

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

    if user and user.phone:
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


def setup_bot(token: str):
    """Настраивает бота"""
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    return app
