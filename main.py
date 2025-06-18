import aiohttp
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler

from aiohttp import web
from dotenv import load_dotenv

from handlers import default, arbitrage_dynamic, calculator, history, settings
from services.aggregator import start_aggregator

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("❗ Установите в окружении API_TOKEN и WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация роутеров
dp.include_routers(
    default.router,
    arbitrage_dynamic.router,
    calculator.router,
    history.router,
    settings.router
)

async def on_startup(app):
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logging.info("✅ Webhook установлен")

async def on_shutdown(app):
    await bot.delete_webhook()
    logging.info("🛑 Webhook удалён")

async def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Запуск фоновой задачи агрегатора
    queue = asyncio.Queue()
    session = aiohttp.ClientSession()
    asyncio.create_task(start_aggregator(queue, session, bot))

    setup_application(app, dp, bot=bot, handle_signals=False)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

    logging.info(f"🚀 Запуск сервера на порту {WEBAPP_PORT}")
    web.run_app(app, port=WEBAPP_PORT)

if __name__ == "__main__":
    asyncio.run(main())
