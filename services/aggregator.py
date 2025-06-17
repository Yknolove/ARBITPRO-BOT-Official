import asyncio
import json
import logging
from services.rate_fetcher import RateFetcher

FILTERS_FILE = "filters.json"

async def start_aggregator(queue: asyncio.Queue, session):
    try:
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
                    logging.warning("⚠️ Не удалось загрузить filters.json")

                for ticker in tickers:
                    symbol = ticker["symbol"]
                    price = float(ticker["lastPrice"])
                    volume = float(ticker["volume"])

                    for user_id, user_filter in filters.items():
                        if user_filter["exchange"] != "bybit":
                            continue

                        if (price <= user_filter["buy_price"] and
                            price >= user_filter["sell_price"] and
                            volume <= user_filter["volume"]):
                            
                            msg = (
                                f"📢 <b>Сделка найдена!</b>\n\n"
                                f"Биржа: Bybit\n"
                                f"Монета: {symbol}\n"
                                f"Цена: {price}\n"
                                f"Объём: {volume}\n"
                                f"🔗 <a href='https://www.bybit.com/trade/spot/{symbol}'>Перейти к ордеру</a>"
                            )

                            await queue.put({
                                "chat_id": int(user_id),
                                "message": msg
                            })

                logging.info("🔁 Цикл агрегатора завершён, спим 15 секунд")
                await asyncio.sleep(15)

            except Exception as e:
                logging.error("💥 Ошибка агрегатора", exc_info=e)
                await asyncio.sleep(10)

    except Exception as e:
        logging.critical("💥 Критическая ошибка агрегатора", exc_info=e)
