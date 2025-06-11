import asyncio
import aiohttp
from utils.logger import logger

async def fetch_p2p_rates() -> dict:
    """
    Запрашивает P2P-курсы с бирж и возвращает словарь:
    {"binance": {"buy": ..., "sell": ...}, ...}
    """
    async with aiohttp.ClientSession() as session:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"asset": "USDT", "fiat": "UAH", "tradeType": "BUY", "merchantCheck": False, "page": 1, "rows": 1}
        headers = {"Content-Type": "application/json"}

        # BUY price
        async with session.post(url, json=payload, headers=headers) as resp_buy:
            data_buy = await resp_buy.json()
            buy_price = float(data_buy["data"][0]["adv"]["price"])

        # SELL price
        payload["tradeType"] = "SELL"
        async with session.post(url, json=payload, headers=headers) as resp_sell:
            data_sell = await resp_sell.json()
            sell_price = float(data_sell["data"][0]["adv"]["price"])

    # Возвращаем stub для других бирж или дополнить
    return {
        "binance": {"buy": buy_price, "sell": sell_price},
        "bybit": {"buy": 41.30, "sell": 42.00},
        "bitget": {"buy": 41.40, "sell": 42.05},
    }

async def fetch_current_arbitrage() -> dict:
    """Обёртка над fetch_p2p_rates для меню арбитража"""
    rates = await fetch_p2p_rates()
    return rates

async def start_aggregator(publish_callback):
    """Основной цикл агрегатора: каждую минуту проверяет курсы и вызывает publish_callback"""
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

