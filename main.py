import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Импорты роутеров
from handlers.default import router as default_router
from handlers.filters import router as filters_router
from handlers.calc import router as calc_router
from handlers.history import router as history_router
from handlers.referral import router as referral_router
from handlers.payment import router as payment_router
from handlers.arbitrage_dynamic import router as arbitrage_router
from handlers.set_filter_trigger import router as set_filter_router

# Агрегатор
from services.aggregator import start_aggregator

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", 8080))

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("❗ Установите API_TOKEN и WEBHOOK_URL в окружении")

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# Подключение роутеров
dp.include_router(default_router)
dp.include_router(filters_router)
dp.include_router(calc_router)
dp.include_router(history_router)
dp.include_router(referral_router)
dp.include_router(payment_router)
dp.include_router(arbitrage_router)
dp.include_router(set_filter_router)

async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(start_aggregator(bot))
    print("✅ Webhook установлен")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()
    print("⛔ Webhook отключён")

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)
