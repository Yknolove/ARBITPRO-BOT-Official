import os

# Забираем токен из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❗ Переменная окружения API_TOKEN не установлена")

# Порт (необязательно для polling, но может понадобиться)
PORT = int(os.getenv("PORT", 8000))
