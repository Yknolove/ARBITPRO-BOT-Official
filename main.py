import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

# 1) Добавляем эти импорты для работы с БД
from config.db import engine, Base
from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from handlers.default import router as default_router
from services.aggregator import start_aggregator
from services.filter_engine import filter_and_notify
from utils.logger import logger

# 2) Инициализируем бота как раньше
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(default_router)

# 3) Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 4) Изменяем on_startup, добавляя init_db и фильтр
async def on_startup():
    await init_db()  # <- создаём таблицы
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    # запускаем агрегатор, передаём ему функцию фильтрации и уведомлений
    asyncio.create_task(start_aggregator(filter_and_notify))

async def on_shutdown():
    await bot.delete_webhook()

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    web.run_app(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
