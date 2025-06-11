import os
import asyncio
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from config.db import engine, Base
from handlers.default import router
from services.aggregator import start_aggregator, fetch_p2p_rates
from services.filter_engine import filter_and_notify
from utils.logger import logger

# Инициализация бота
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Dispatcher с поддержкой FSM
dp = Dispatcher(storage=MemoryStorage())
# Регистрируем маршруты хендлера
dp.include_router(router)

async def init_db():
    """Создает таблицы при старте"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def set_commands():
    """Устанавливает команды в UI"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="stats", description="Показать настройки Free версии"),
    ]
    await bot.set_my_commands(commands)

async def keep_awake():
    """Пингует /ping каждый 30 секунд, чтобы инстанс не засыпал"""
    await asyncio.sleep(5)
    url = WEBHOOK_URL + "/ping"
    session = aiohttp.ClientSession()
    try:
        while True:
            try:
                await session.get(url)
            except Exception:
                pass
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        await session.close()
        raise

async def on_startup():
    await init_db()
    await set_commands()
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    asyncio.create_task(start_aggregator(filter_and_notify))
    asyncio.create_task(keep_awake())

async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

# Создание веб-приложения
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.router.add_get("/ping", lambda request: web.Response(text="OK"))
app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)

