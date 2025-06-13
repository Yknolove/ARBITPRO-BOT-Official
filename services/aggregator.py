import asyncio
import aiohttp
import logging
from services.rate_fetcher import RateFetcher
from services.arb_engine import ArbEngine
from services.notifier import notify_user

async def start_aggregator(user_settings):
    session = aiohttp.ClientSession()
    rf = RateFetcher(session)
    while True:
        try:
            rates = {
                "binance": await rf.fetch_binance(),
                "bybit":   await rf.fetch_bybit(),
                "bitget":  await rf.fetch_bitget(),
            }
            arb = ArbEngine(user_settings.get("thresholds", {}))
            ops = arb.find_arbitrage(rates)
            msg = "🔄 Arbitrage:\n" + "\n".join(f"{a}->{b}: {p}%" for a,b,p in ops)
            await notify_user(user_settings["chat_id"], msg)
        except Exception:
            logging.exception("Aggregator error")
        await asyncio.sleep(10)
