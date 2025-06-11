import asyncio
import aiohttp
from utils.logger import logger

async def fetch_p2p_rates() -> dict:
    """
    Каждый цикл открывает свою сессию и сразу её закрывает,
    чтобы не оставалось не закрытых ClientSession.
    """
    async with aiohttp.ClientSession() as session:
        # Binance BUY
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

        # Binance SELL
        payload["tradeType"] = "SELL"
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            sell_price = float(data["data"][0]["adv"]["price"])

        # Заглушки для Bybit и Bitget (поменяешь на реальные запросы позже)
        return {
            "binance": {"buy": buy_price, "sell": sell_price},
            "bybit":   {"buy": 41.30, "sell": 42.00},
            "bitget":  {"buy": 41.40, "sell": 42.05},
        }

async def start_aggregator(publish_callback):
    """
    Основной цикл агрегатора: каждые 10 сек собирает курсы
    и передаёт их в функцию publish_callback.
    """
    while True:
        try:
            rates = await fetch_p2p_rates()
            logger.info(f"Fetched rates: {rates}")

            result = publish_callback(rates)
            if asyncio.iscoroutine(result):
                await result

        except Exception as e:
            logger.error(f"Aggregator error: {e}")

        # пауза перед следующим циклом
        await asyncio.sleep(10)
