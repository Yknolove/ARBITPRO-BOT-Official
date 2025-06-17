import os
import json
import logging
import asyncio
from aiohttp import ClientSession
from aiogram import Bot

FILTERS_FILE = "filters.json"

API_TOKEN = os.getenv("API_TOKEN")

async def fetch_bybit():
    url = "https://api.bybit.com/v5/market/tickers?category=spot"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            if resp.content_type != "application/json":
                text = await resp.text()
                raise Exception(f"❌ Не JSON ответ: {resp.content_type}, текст: {text}")
            data = await resp.json()
            tickers = data["result"]["list"]
            logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")
            return tickers

def load_filters():
    try:
        with open(FILTERS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.warning("❗ Не удалось загрузить фильтры", exc_info=e)
        return {}

async def start_aggregator():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN, parse_mode="HTML")

    while True:
        try:
            tickers = await fetch_bybit()
            filters = load_filters()
            for symbol_data in tickers:
                symbol = symbol_data["symbol"]
                ask = float(symbol_data.get("askPrice", 0))
                bid = float(symbol_data.get("bidPrice", 0))
                for chat_id, f in filters.items():
                    if f["exchange"] != "bybit":
                        continue
                    if ask <= f["buy_price"] and bid >= f["sell_price"] and float(symbol_data["volume24h"]) >= f["volume"]:
                        logging.info(f"✅ Найден подходящий ордер: {{'symbol': '{symbol}', 'buy': {ask}, 'sell': {bid}, 'volume': {symbol_data['volume24h']}, 'chat_id': {chat_id}}}")
                        text = (
                            f"📢 Найден арбитраж по <b>{symbol}</b>:\n"
                            f"💰 Покупка: {ask}\n"
                            f"💵 Продажа: {bid}\n"
                            f"📊 Объём (24ч): {symbol_data['volume24h']}"
                        )
                        try:
                            await bot.send_message(chat_id=int(chat_id), text=text)
                        except Exception as send_err:
                            logging.error("❌ Ошибка при отправке сообщения", exc_info=send_err)
        except Exception as e:
            logging.error("💥 Критическая ошибка агрегатора", exc_info=e)

        logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд\n")
        await asyncio.sleep(15)
