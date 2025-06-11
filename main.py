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
from handlers.default import router, menu_registry, version_menu
from services.aggregator import start_aggregator
from services.filter_engine import filter_and_notify
from utils.logger import logger

# Инициализация бота
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
# Диспетчер с поддержкой FSM
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def init_db():
    """Создает таблицы при старте."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def set_commands():
    """Регистрирует команды в Telegram UI."""
    await bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
    ])

async def keep_awake():
    """Пингует свой /ping, чтобы инстанс не засыпал."""
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

async def refresh_menus():
    """Обновляет главное меню каждые 30 секунд."""
    await asyncio.sleep(10)
    while True:
        for chat_id, msg_id in list(menu_registry.items()):
            try:
                await bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=version_menu()
                )
            except Exception:
                menu_registry.pop(chat_id, None)
        await asyncio.sleep(30)

async def on_startup():
    await init_db()
    await set_commands()
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook set to {WEBHOOK_URL + WEBHOOK_PATH}")
    asyncio.create_task(start_aggregator(filter_and_notify))
    asyncio.create_task(keep_awake())
    asyncio.create_task(refresh_menus())

async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

# Создаем веб-приложение
app = web.Application()
# Регистрируем webhook и /ping
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.router.add_get("/ping", lambda req: web.Response(text="OK"))
app.on_startup.append(lambda _: on_startup())
app.on_shutdown.append(lambda _: on_shutdown())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port)
