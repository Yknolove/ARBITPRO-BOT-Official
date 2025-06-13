import os
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# —— Настройки из окружения ——
API_TOKEN   = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")     # например https://your-app.com
WEBHOOK_PATH= os.getenv("WEBHOOK_PATH", "/webhook")
PORT        = int(os.getenv("PORT", "8000"))

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("❗ Установите в окружении API_TOKEN и WEBHOOK_URL")

# —— Инициализация бота и диспетчера ——
bot = Bot(token=API_TOKEN)
dp  = Dispatcher()

# —— Обработчики ——
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton("🆓 Free Version", callback_data="version_free")],
            [types.InlineKeyboardButton("🔒 Pro Version",  callback_data="version_pro")],
        ]
    )
    await message.answer(
        "👋 Добро пожаловать в ArbitPRO!\nВыберите версию:",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data in ["version_free", "version_pro"])
async def cb_version(c: types.CallbackQuery):
    if c.data == "version_free":
        text = (
            "🆓 *Free Version*\n\n"
            "• Мониторинг P2P-арбитража на одной бирже\n"
            "• Установка порогов buy ≤ X, sell ≥ Y\n"
            "• Без калькулятора и истории\n"
        )
    else:
        text = (
            "🔒 *Pro Version*\n\n"
            "• Все биржи, без ограничений\n"
            "• Калькулятор прибыли\n"
            "• История сделок, топ-сделки\n"
            "• Поддержка и партнёрка\n"
        )
    # редактируем сообщение с кнопками
    await c.message.edit_text(text, parse_mode="Markdown")

# —— Webhook setup/teardown ——
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

# —— Создаём aiohttp-приложение и вешаем диспетчер ——
def create_app() -> web.Application:
    app = web.Application()
    # регистрируем обработку входящих HTTP-запросов
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(
        app, path=WEBHOOK_PATH
    )
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

# —— Точка входа ——
if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=PORT)
