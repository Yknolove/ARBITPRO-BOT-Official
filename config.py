import os

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❗ Не задана переменная окружения API_TOKEN")

# Если polling, PORT не нужен
# Если webhook: uncomment below
# WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# WEBHOOK_PATH = "/webhook"
