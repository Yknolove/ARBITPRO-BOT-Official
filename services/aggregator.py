import asyncio
import aiohttp
from utils.logger import logger

async def fetch_p2p_rates(session: aiohttp.ClientSession) -> dict:
    # Пример для Binance: делаем POST-запрос и парсим цену покупки
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

    # BUY
    async with session.post(url, json=payload, headers=headers) as resp:
        data = await resp.json()
        buy_price = float(data["data"][0]["adv"]["price"])

    # SELL (меняем tradeType)
    payload["tradeType"] = "SELL"
    async with session.post(url, json=payload, headers=headers) as resp:
        data = await resp.json()
        sell_price = float(data["data"][0]["adv"]["price"])

    # Здесь stub-данные для Bybit и Bitget, позже их заменим
    return {
        "binance": {"buy": buy_price, "sell": sell_price},
        "bybit":   {"buy": 41.30, "sell": 42.00},
        "bitget":  {"buy": 41.40, "sell": 42.05},
    }


async def start_aggregator(publish_callback):
    # Одна сессия на весь цикл
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                rates = await fetch_p2p_rates(session)
                logger.info(f"Fetched rates: {rates}")

                # Вызов callback: если он async, await, иначе просто вызов
                result = publish_callback(rates)
                if asyncio.iscoroutine(result):
                    await result

            except Exception as e:
                logger.error(f"Aggregator error: {e}")

            await asyncio.sleep(10)
