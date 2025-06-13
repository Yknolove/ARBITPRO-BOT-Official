import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.default import router  # ваш router с командами

API_TOKEN = os.getenv(8131766932:AAFPfxgWtoY7fejhp5dofLsz0q7701L4GAI)  # убедитесь, что переменная окружения задана

logging.basicConfig(level=logging.INFO)

async def main():
    # Создаем бот с HTML-разметкой
    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Starting polling…")
    # Запускаем polling (бот будет реагировать на все входящие сообщения)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
