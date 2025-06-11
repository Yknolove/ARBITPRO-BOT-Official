import asyncio
import aiohttp
from utils.logger import logger

async def fetch_p2p_rates() -> dict:
    # Каждый цикл открываем и закрываем сессию, чтобы не было утечек
    async with aiohttp.ClientSession() as session:
        # BINANCE BUY
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "UAH",
            "tradeType": "BUY",
            "merchantCheck": False,
            "page": 1,
            "rows": 1
        }
        headers = {"Content-Type": "application/json"}

        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            buy_price = float(data["data"][0]["adv"]["price"])

        # BINANCE SELL
        payload["tradeType"] = "SELL"
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            sell_price = float(data["data"][0]["adv"]["price"])

        # Заменить заглушки аналогично для Bybit/Bitget
        return {
            "binance": {"buy": buy_price, "sell": sell_price},
            "bybit":   {"buy": 41.30, "sell": 42.00},
            "bitget":  {"buy": 41.40, "sell": 42.05},
        }

async def start_aggregator(publish_callback):
    while True:
        try:
            rates = await fetch_p2p_rates()
            logger.info(f"Fetched rates: {rates}")
            result = publish_callback(rates)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.error(f"Aggregator error: {e}")
        await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Aggregator error: {e}")

            await asyncio.sleep(10)
