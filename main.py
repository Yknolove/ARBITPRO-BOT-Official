import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import API_TOKEN
from handlers.default import router
from services.aggregator import start_aggregator

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    # пример пользовательских настроек
    user_settings = {"chat_id": 123456789, "thresholds": {("binance","bybit"): {"min_profit": 0.5}}}
    asyncio.create_task(start_aggregator(user_settings))

    logging.info("🚀 Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
