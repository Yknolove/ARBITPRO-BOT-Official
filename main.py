import os
import asyncio
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from dotenv import load_dotenv
load_dotenv()

from handlers.default import router  # ваш роутер с командами и callback'ами

API_TOKEN    = os.getenv("API_TOKEN")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"
PORT         = int(os.getenv("PORT", 8000))

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("❗ Установите в окружении API_TOKEN и WEBHOOK_URL")

bot = Bot(token=API_TOKEN)
dp  = Dispatcher()

# подключаем все ваши хэндлеры
dp.include_router(router)

async def on_startup(app: web.Application):
    # ставим webhook у Telegram
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    # убираем webhook и закрываем сессию
    await bot.delete_webhook()
    await bot.session.close()

# создаём aiohttp-приложение и прокидываем туда aiogram
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# всё пришедшие POST-запросы на /webhook обрабатывает aiogram
app.router.add_post(WEBHOOK_PATH, dp.process_update)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)
