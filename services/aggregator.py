import json
import asyncio
import logging
from services.rate_fetcher import RateFetcher

FILTERS_FILE = "filters.json"

async def start_aggregator(queue: asyncio.Queue, session):
    rf = RateFetcher(session)

    while True:
        try:
            tickers = await rf.fetch_bybit()
            logging.info(f"🟢 Bybit вернул {len(tickers)} тикеров")

            try:
                with open(FILTERS_FILE, "r") as f:
                    filters = json.load(f)
                logging.info(f"▶ Фильтры загружены: {filters}")
            except Exception as e:
                logging.warning("❗ Не удалось загрузить фильтры", exc_info=e)
                filters = {}

            for ticker in tickers:
                symbol = ticker["symbol"]
                ask_price = float(ticker.get("askPrice", 0))
                bid_price = float(ticker.get("bidPrice", 0))

                for user_id, user_filter in filters.items():
                    if user_filter["exchange"] != "bybit":
                        continue

                    logging.info(f"⏳ Проверка: {symbol} ask={ask_price}, bid={bid_price}, фильтр={user_filter}")

                    if ask_price <= user_filter["buy_price"] and bid_price >= user_filter["sell_price"]:
                        order_data = {
                            "symbol": symbol,
                            "buy": ask_price,
                            "sell": bid_price,
                            "volume": user_filter["volume"],
                            "chat_id": user_filter["chat_id"],
                        }
                        logging.info(f"✅ Найден подходящий ордер: {order_data}")
                        await queue.put(order_data)

        except Exception as e:
            logging.error("💥 Критическая ошибка агрегатора", exc_info=e)

        logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
        await asyncio.sleep(15)
