import asyncio
from utils.logger import logger

async def fetch_p2p_rates():
    # ... ваш код
    return { ... }

async def start_aggregator(publish_callback):
    while True:
        rates = await fetch_p2p_rates()
        logger.info(f"Fetched rates: {rates}")
        try:
            result = publish_callback(rates)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.error(f"Error in publish_callback: {e}")
        await asyncio.sleep(10)
