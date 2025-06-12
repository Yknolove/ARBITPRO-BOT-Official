# ArbitPRO Bot

Telegram-бот для P2P-арбитража USDT между биржами Binance, Bybit и Bitget.

## Функционал Free-версии

- Мониторинг одной выбранной P2P-биржи
- Установка порогов: покупка ≤ X, продажа ≥ Y, объём ≤ Z
- Уведомления при достижении условий

## Быстрый старт

1. Клонировать репозиторий и перейти в папку проекта  
2. Создать `.env` в корне со следующим содержимым:
   ```dotenv
   TELEGRAM_TOKEN=ваш_токен
   WEBHOOK_URL=https://your.domain.com
   WEBHOOK_PATH=/webhook
   PORT=8000
   DATABASE_URL=sqlite+aiosqlite:///./db.sqlite
