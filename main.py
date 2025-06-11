import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from handlers.default import router as default_router
from services.aggregator import start_aggregator
from utils.logger import logger

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

dp.include_router(default_router)

async def on_startup():
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    # Запускаем агрегатор в фоне
    asyncio.create_task(start_aggregator(lambda rates: None))

async def on_shutdown():
    await bot.delete_webhook()

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
