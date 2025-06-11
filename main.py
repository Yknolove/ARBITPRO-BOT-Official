import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL, PORT
from config.db import engine, Base
from handlers.default import router as default_router
from services.aggregator import start_aggregator
from services.filter_engine import filter_and_notify
from utils.logger import logger

# 1) Инициализируем бота с HTML-парсингом
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(default_router)

# 2) Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 3) Регистрируем команды, чтобы они отображались в списке чата
async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="settings", description="Показать настройки"),
        BotCommand(command="set_exchange", description="Выбрать биржу"),
        BotCommand(command="set_buy", description="Задать порог покупки"),
        BotCommand(command="set_sell", description="Задать порог продажи"),
    ])

# 4) Стартап: init DB, команды, webhook и агрегатор
async def on_startup():
    await init_db()
    await set_commands()
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    asyncio.create_task(start_aggregator(filter_and_notify))

# 5) Шатдаун: удаляем webhook и закрываем сессию
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

# 6) Собираем приложение
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", PORT)))
