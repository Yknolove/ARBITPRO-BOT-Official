import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL")
