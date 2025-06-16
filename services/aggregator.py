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

                # 1. Создаём файл если отсутствует
                if not os.path.exists(FILTERS_FILE):
                    with open(FILTERS_FILE, "w") as f:
                        json.dump({}, f)

                # 2. Загружаем фильтры
                try:
                    with open(FILTERS_FILE, "r") as f:
                        filters = json.load(f)
                except Exception as e:
                    logging.warning("❗ Ошибка чтения filters.json", exc_info=e)
                    filters = {}

                # 3. Обработка каждого фильтра
                for chat_id, f in filters.items():
                    try:
                        buy_limit = float(f.get("buy_price", 0))
                        sell_limit = float(f.get("sell_price", 999999))
                        vol_limit = float(f.get("volume", 100))

                        for ticker in tickers:
                            try:
                                price = float(ticker.get("lastPrice", 0))
                                volume = float(ticker.get("turnover24h", 0))

                                if price <= buy_limit and price >= sell_limit and volume <= vol_limit:
                                    msg = (
                                        f"💰 Сделка найдена:\n"
                                        f"Цена: {price}$\n"
                                        f"Объём: {volume}$"
                                    )
                                    await bot.send_message(chat_id=int(chat_id), text=msg)

                            except Exception as e:
                                logging.warning(f"⚠️ Ошибка в тикере: {e}")
                                continue
                    except Exception as e:
                        logging.warning(f"⚠️ Ошибка обработки фильтра пользователя {chat_id}: {e}")
                        continue

        except Exception as e:
            logging.error("❌ Критическая ошибка агрегатора", exc_info=e)

        await asyncio.sleep(15)
