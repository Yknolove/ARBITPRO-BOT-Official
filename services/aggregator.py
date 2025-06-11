import asyncio
from utils.logger import logger

async def fetch_p2p_rates():
    # TODO: запросы к Binance, Bybit, Bitget
    return {
        "binance": {"buy": 41.50, "sell": 42.10},
        "bybit":   {"buy": 41.30, "sell": 42.00},
        "bitget":  {"buy": 41.40, "sell": 42.05},
    }

async def start_aggregator(publish_callback):
    while True:
        rates = await fetch_p2p_rates()
        logger.info(f"Fetched rates: {rates}")
        # TODO: передать в Filter Engine
        await publish_callback(rates)
        await asyncio.sleep(10)
