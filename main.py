import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from os import getenv

from handlers.default import router as default_router
from handlers.filters import router as filters_router
from handlers.calculator import router as calc_router
from handlers.history import router as history_router
from handlers.referral import router as referral_router

from services.aggregator import start_aggregator
from services.notifier import notifier_worker

logging.basicConfig(level=logging.INFO)

API_TOKEN = getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❗ Установите в окружении API_TOKEN")

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

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
