# services/notifier.py

from aiogram import Bot
from aiogram.enums import ParseMode
from config.config import API_TOKEN

# Один экземпляр Bot для отправки уведомлений
_bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)

async def notify_user(user_id: int, text: str) -> None:
    """
    Отправляет пользователю в Telegram уведомление.
    :param user_id: ID чата/пользователя
    :param text: Текст сообщения
    """
    await _bot.send_message(chat_id=user_id, text=text)
