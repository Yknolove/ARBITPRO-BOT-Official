import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv(8131766932:AAFPfxgWtoY7fejhp5dofLsz0q7701L4GAI)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL")
