import aiohttp
import asyncio
import logging
import json
from aiogram import Bot
from services.rate_fetcher import RateFetcher

API_TOKEN = "8131766932:AAFPfxgWtoY7fejhp5dofLsz0q7701L4GAI"
FILTERS_FILE = "filters.json"

bot = Bot(token=API_TOKEN, parse_mode="HTML")

async def start_aggregator():
    async with aiohttp.ClientSession() as session:
        rf = RateFetcher(session)

        while True:
            try:
                tickers = await rf.fetch_bybit()
                logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

                try:
                    with open(FILTERS_FILE, "r") as f:
                        filters = json.load(f)
                except Exception:
                    filters = {}
                    logging.warning("❗ Не удалось загрузить фильтры")

                for ticker in tickers:
                    symbol = ticker["symbol"]
                    ask = float(ticker.get("askPrice") or ticker.get("ask") or 0)
                    bid = float(ticker.get("bidPrice") or ticker.get("bid") or 0)

                    for user_id, f_data in filters.items():
                        if f_data["exchange"] != "bybit":
                            continue

                        if ask <= f_data["buy_price"] and bid >= f_data["sell_price"]:
                            logging.info(f"✅ Найден подходящий ордер: {symbol}")

                            try:
                                await bot.send_message(
                                    chat_id=int(user_id),
                                    text=(
                                        f"📢 Найден арбитраж по <b>{symbol}</b>:
"
                                        f"💰 Купить: <code>{ask}</code>
"
                                        f"📤 Продать: <code>{bid}</code>
"
                                        f"📦 Объем: {f_data['volume']}$"
                                    )
                                )
                            except Exception as e:
                                logging.error(f"❌ Ошибка при отправке сообщения: {e}")
            except Exception as e:
                logging.error("💥 Критическая ошибка агрегатора", exc_info=e)

            logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
            await asyncio.sleep(15)
