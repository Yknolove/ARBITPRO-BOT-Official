import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN, WEBHOOK_URL, WEBAPP_PORT
from aiohttp import web

from handlers import default, arbitrage_dynamic, calculator, history
from services.aggregator import start_aggregator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher(storage=MemoryStorage())

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/filter", description="Настроить фильтры"),
        BotCommand(command="/calc", description="Калькулятор"),
        BotCommand(command="/history", description="История уведомлений")
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=API_TOKEN, parse_mode="HTML")
    await set_bot_commands(bot)

    dp.include_router(default.router)
    dp.include_router(arbitrage_dynamic.router)
    dp.include_router(calculator.router)
    dp.include_router(history.router)

    session = aiohttp.ClientSession()
    asyncio.create_task(start_aggregator(session, bot))

    async def handle_webhook(request):
        update = await request.json()
        await dp.feed_update(bot, update)
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    await bot.set_webhook(WEBHOOK_URL)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=WEBAPP_PORT)
    await site.start()

    logger.info(f"Bot is running on {WEBHOOK_URL}")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
