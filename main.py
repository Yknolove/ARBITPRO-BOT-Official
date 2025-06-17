# main.py

import logging
import asyncio
import aiohttp

from os import getenv
from dotenv import load_dotenv
load_dotenv()  # загрузит все переменные из .env

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.default import router as default_router
from handlers.filters import router as filters_router
from handlers.calculator import router as calc_router
from handlers.history import router as history_router
from handlers.referral import router as referral_router

from services.aggregator import start_aggregator
from services.notifier import notifier_worker
from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(default_router)
dp.include_router(filters_router)
dp.include_router(calc_router)
dp.include_router(history_router)
dp.include_router(referral_router)

async def start_bot():
    session = aiohttp.ClientSession()
    queue = asyncio.Queue()

    asyncio.create_task(start_aggregator(queue, session))
    asyncio.create_task(notifier_worker(queue, bot))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(start_bot())
