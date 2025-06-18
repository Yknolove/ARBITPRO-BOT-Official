# services/aggregator.py
import asyncio
import json
import logging
import aiohttp
from aiogram import Bot
from config import API_TOKEN  # теперь работает!
from services.filter_engine import apply_filters
from services.const import FILTERS_FILE

async def fetch_bybit(session):
    url = "https://api.bybit.com/v5/market/tickers?category=spot"
    async with session.get(url) as resp:
        if resp.content_type != 'application/json':
            text = await resp.text()
            raise Exception(f"❌ Не JSON ответ: {resp.content_type}, текст: {text}")
        data = await resp.json()
        return data["result"]["list"]

async def start_aggregator(queue, session):
    bot = Bot(token=API_TOKEN, parse_mode="HTML")

    while True:
        try:
            tickers = await fetch_bybit(session)
            logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

            try:
                with open(FILTERS_FILE, "r") as f:
                    filters = json.load(f)
            except Exception as e:
                logging.warning("❗ Не удалось загрузить фильтры", exc_info=e)
                filters = {}

            orders = apply_filters(tickers, FILTERS_FILE)

            for order in orders:
                symbol = order["symbol"]
                buy = order.get("buy", 0)
                sell = order.get("sell", 0)
                volume = order.get("volume", 0)
                chat_id = order["chat_id"]

                text = (
                    f"📢 Найден арбитраж по <b>{symbol}</b>:\n"
                    f"🔹 Покупка: <code>{buy}</code>\n"
                    f"🔹 Продажа: <code>{sell}</code>\n"
                    f"🔹 Объём: <code>{volume}</code>\n\n"
                    f"👤 Фильтр пользователя активирован"
                )

                await bot.send_message(chat_id=chat_id, text=text)

        except Exception as e:
            logging.error("💥 Критическая ошибка агрегатора", exc_info=e)

        logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
        await asyncio.sleep(15)
