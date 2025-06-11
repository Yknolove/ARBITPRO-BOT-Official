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

from services.aggregator import start_aggregator
from services.filter_engine import filter_and_notify
from utils.logger import logger

# Инициализация бота с HTML-парсингом
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Dispatcher с поддержкой FSM
dp = Dispatcher(storage=MemoryStorage())
# Регистрируем маршруты хендлеров
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

async def keep_awake():
    """Регулярно пингует собственный /ping, чтобы инстанс не засыпал"""
    await asyncio.sleep(5)
    url = WEBHOOK_URL + "/ping"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(url)
            except Exception:
                pass
            await asyncio.sleep(30)

async def on_startup():
    # Инициализация базы данных
    await init_db()
    # Регистрация команд в UI
    await set_commands()
    # Установка вебхука
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    # Запуск фонового агрегатора
    asyncio.create_task(start_aggregator(filter_and_notify))
    # Запуск self-ping для предотвращения засыпания
    asyncio.create_task(keep_awake())

async def on_shutdown():
    # Удаление вебхука и закрытие сессии
    await bot.delete_webhook()
    await bot.session.close()

# Создание aiohttp-приложения
app = web.Application()
# Регистрируем обработчик вебхука
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
# Маршрут для heartbeat
app.router.add_get("/ping", lambda request: web.Response(text="OK"))

app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)
