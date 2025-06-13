import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import API_TOKEN
from handlers.default import router

logging.basicConfig(level=logging.INFO)

async def main():
    # Создаём бота с HTML-парсингом
    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("🚀 Запуск polling...")
    # Запускаем долгий polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
