import aiohttp

class RateFetcher:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_binance(self) -> dict:
        url = "https://api.binance.com/api/v3/ticker/bookTicker?symbol=USDTBUSD"
        async with self.session.get(url) as r:
            d = await r.json()
            return {"buy": float(d["bidPrice"]), "sell": float(d["askPrice"])}

    async def fetch_bybit(self) -> dict:
        url = "https://api.bybit.com/v2/public/tickers?symbol=USDTUSD"
        async with self.session.get(url) as r:
            d = await r.json()
            t = d["result"][0]
            return {"buy": float(t["bid_price"]), "sell": float(t["ask_price"])}

    async def fetch_bitget(self) -> dict:
        url = "https://api.bitget.com/api/spot/v1/market/ticker?symbol=usdt_usd"
        async with self.session.get(url) as r:
            d = await r.json()
            t = d["data"]
            return {"buy": float(t["buy"]), "sell": float(t["sell"])}
