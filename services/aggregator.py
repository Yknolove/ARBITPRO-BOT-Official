import asyncio
import aiohttp
import json
import os
import logging
from services.rate_fetcher import RateFetcher

FILTERS_FILE = "filters.json"

async def start_aggregator(bot):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                rf = RateFetcher(session)
                tickers = await rf.fetch_bybit()
                print(f"🟢 Bybit вернул {len(tickers)} тикеров")

                # ✅ Авто-создание пустого filters.json, если его нет
                if not os.path.exists(FILTERS_FILE):
                    with open(FILTERS_FILE, "w") as f:
                        json.dump({}, f)

                try:
                    with open(FILTERS_FILE, "r") as f:
                        filters = json.load(f)
                except Exception as e:
                    logging.warning("❗ Не удалось загрузить фильтры", exc_info=e)
                    filters = {}

                for chat_id, f in filters.items():
                    for ticker in tickers:
                        try:
                            price = float(ticker.get("lastPrice", 0))
                            volume = float(ticker.get("turnover24h", 0))

                            if (
                                price <= f["buy_price"]
                                and price >= f["sell_price"]
                                and volume <= f["volume"]
                            ):
                                msg = (
                                    f"💰 Найдена подходящая сделка:\n"
                                    f"Цена: {price}$\n"
                                    f"Объём: {volume}$"
                                )
                                await bot.send_message(chat_id=int(chat_id), text=msg)
                        except Exception as deal_error:
                            logging.warning(f"⚠️ Пропущен тикер: {deal_error}")
                            continue

        except Exception as e:
            logging.error("❌ Ошибка в агрегаторе", exc_info=e)

        await asyncio.sleep(15)
