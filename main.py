import asyncio
from aiohttp import web
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL, PORT
from handlers.default import router

async def on_startup(bot: Bot):
    # Устанавливаем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

async def on_shutdown(bot: Bot):
    await bot.session.close()

async def run_app():
    session = AiohttpSession()
    bot = Bot(
        token=API_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()
    dp.include_router(router)

    await on_startup(bot)
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, dp.webhook_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"🚀 Running on 0.0.0.0:{PORT}, webhook={WEBHOOK_URL}")
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await on_shutdown(bot)
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(run_app())
