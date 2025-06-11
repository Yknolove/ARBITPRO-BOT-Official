import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DB_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./db.sqlite')
TRON_API_KEY = os.getenv('TRON_API_KEY')

# Новый блок:
PORT = int(os.getenv('PORT', 8000))
