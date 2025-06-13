import os
import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Токен бота (вставлен напрямую)
API_TOKEN = "8131766932:AAFPfxgWtoY7fejhp5dofLsz0q7701L4GAI"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer(f"👋 Привет! Ты написал: {message.text}")

async def main() -> None:
    logging.info("🚀 Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен.")
