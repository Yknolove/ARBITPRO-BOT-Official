import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

from handlers.default import router as default_router
from handlers.filters import router as filters_router
from handlers.history import router as history_router
from handlers.calculator import router as calc_router
from handlers.arbitrage_dynamic import router as arbitrage_router
from handlers.set_filter_trigger import router as set_filter_router
from services.aggregator import start_aggregator

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("❗ Установите в окружении API_TOKEN и WEBHOOK_URL")

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(default_router)
dp.include_router(filters_router)
dp.include_router(set_filter_router)
dp.include_router(calc_router)
dp.include_router(history_router)
dp.include_router(arbitrage_router)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    asyncio.create_task(start_aggregator(bot))
    logging.info("🚀 Бот и агрегатор запущены")

app.on_startup.append(on_startup)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
