import os
FILTERS_FILE = "filters.json"
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBAPP_PORT = int(os.getenv("PORT", 10000))
