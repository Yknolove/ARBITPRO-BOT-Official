import asyncio
import json
import logging
from aiogram import Bot
from config import API_TOKEN
from services.rate_fetcher import RateFetcher

bot = Bot(token=API_TOKEN)
FILTERS_FILE = "filters.json"

async def start_aggregator():
    from aiohttp import ClientSession
    async with ClientSession() as session:
        rf = RateFetcher(session)

        while True:
            try:
                tickers = await rf.fetch_bybit()
                logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

                try:
                    with open(FILTERS_FILE, "r") as f:
                        filters = json.load(f)
                except Exception as e:
                    logging.warning("❗ Не удалось загрузить фильтры", exc_info=e)
                    filters = {}

                for chat_id, flt in filters.items():
                    for t in tickers:
                        symbol = t["symbol"]
                        ask = float(t.get("askPrice", 0) or 0)
                        bid = float(t.get("bidPrice", 0) or 0)

                        if ask <= flt["buy_price"] and bid >= flt["sell_price"]:
                            order = {
                                "symbol": symbol,
                                "buy": ask,
                                "sell": bid,
                                "volume": flt["volume"],
                                "chat_id": flt["chat_id"]
                            }
                            logging.info(f"✅ Найден подходящий ордер: {order}")
                            try:
                                await bot.send_message(
                                    chat_id=order["chat_id"],
                                    text=f"📢 Найден арбитраж по <b>{order['symbol']}</b>:
"
                                         f"Покупка: {order['buy']}
"
                                         f"Продажа: {order['sell']}",
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                logging.error(f"❌ Ошибка отправки уведомления: {e}")

                logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
                await asyncio.sleep(15)

            except Exception as e:
                logging.error("💥 Критическая ошибка агрегатора", exc_info=e)
                await asyncio.sleep(30)
