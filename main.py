import logging
import sys
from os import getenv

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- your config imports (adjust paths!) ---
# from config.config import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL, PORT
API_TOKEN = getenv("API_TOKEN")
WEBHOOK_HOST = getenv("WEBHOOK_HOST")        # e.g. https://yourdomain.com
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(getenv("PORT", 8000))
# -------------------------------------------

# Logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. Initialize Bot with default properties (parse_mode, etc.)
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)  :contentReference[oaicite:0]{index=0}

# 2. Create Dispatcher and include your routers/handlers
dp = Dispatcher()
# e.g. dp.include_router(your_router)

# 3. Register startup hook to set the webhook on Telegram
async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(WEBHOOK_URL)  :contentReference[oaicite:1]{index=1}

dp.startup.register(on_startup)

# 4. Build aiohttp Application
app = web.Application()

# 5. Mount the SimpleRequestHandler (replaces dp.webhook_handler)
webhook_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
    # secret_token=<opt>,  # if you set a secret token in set_webhook
)
webhook_handler.register(app, path=WEBHOOK_PATH)  :contentReference[oaicite:2]{index=2}

# 6. Tie in dispatcher startup/shutdown to the web app
setup_application(app, dp, bot=bot)  :contentReference[oaicite:3]{index=3}

# 7. Run!
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)  :contentReference[oaicite:4]{index=4}
