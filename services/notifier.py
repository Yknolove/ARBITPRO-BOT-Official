from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

_bot = Bot(token="YOUR_TOKEN", default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def notify_user(chat_id: int, text: str):
    await _bot.send_message(chat_id, text)
