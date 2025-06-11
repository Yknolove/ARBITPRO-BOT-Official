import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL
from config.db import engine, Base
from handlers.default import router as default_router
from services.aggregator import start_aggregator, fetch_current_arbitrage
from services.filter_engine import filter_and_notify
from utils.logger import logger

# Инициализируем бота с HTML-парсингом
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Dispatcher с поддержкой FSM
dp = Dispatcher(storage=MemoryStorage())
# Регистрируем маршруты
dp.include_router(default_router)

async def init_db():
    """Создаёт таблицы в базе при старте"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def set_commands():
    """Устанавливает команды бота, видимые в UI"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="settings", description="Показать настройки"),
        BotCommand(command="set_exchange", description="Выбрать биржу"),
        BotCommand(command="set_buy", description="Задать порог покупки"),
        BotCommand(command="set_sell", description="Задать порог продажи"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    # 1) Инициализируем базу
    await init_db()
    # 2) Регистрируем команды
    await set_commands()
    # 3) Ставим webhook
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    # 4) Запускаем агрегатор с фильтрацией
    asyncio.create_task(start_aggregator(filter_and_notify))

async def on_shutdown():
    # Удаляем webhook и закрываем сессию
    await bot.delete_webhook()
    await bot.session.close()

# Составляем aiohttp-приложение
app = web.Application()

# Регистрируем webhook handler
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

# Добавляем /ping для heartbeat
app.router.add_get("/ping", lambda request: web.Response(text="OK"))

app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    # Порт из окружения (Render задаёт переменную PORT автоматически)
    port = int(os.getenv("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)
