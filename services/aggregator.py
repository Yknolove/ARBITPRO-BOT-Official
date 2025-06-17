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

                if not os.path.exists(FILTERS_FILE):
                    with open(FILTERS_FILE, "w") as f:
                        json.dump({}, f)

                try:
                    with open(FILTERS_FILE, "r") as f:
                        filters = json.load(f)
                except Exception:
                    filters = {}

                for chat_id, fdata in filters.items():
                    try:
                        buy_limit = float(fdata.get("buy_price", 0))
                        sell_limit = float(fdata.get("sell_price", 0))
                        vol_limit = float(fdata.get("volume", 0))
                    except:
                        continue

                    for t in tickers:
                        try:
                            price = float(t["price"])
                            vol = float(t["volume"])
                            if price <= buy_limit and price >= sell_limit and vol <= vol_limit:
                                msg = f"💰 Сделка!\n{t['symbol']}\nЦена: {price}$\nОбъём: {vol}$"
                                try:
                                    await bot.send_message(chat_id=int(chat_id), text=msg)
                                except Exception as send_err:
                                    logging.error(f"❌ Ошибка отправки: {send_err}")
                        except:
                            continue

        except Exception as e:
            logging.error("💥 Ошибка в агрегаторе", exc_info=e)

        await asyncio.sleep(15)
