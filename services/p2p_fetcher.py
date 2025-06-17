import aiohttp

class P2PFetcher:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_binance(self):
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"asset":"USDT","fiat":"UAH","tradeType":"BUY","page":1,"rows":5}
        async with self.session.post(url, json=payload) as r:
            d = await r.json()
            data = d.get("data", [])
            prices = [float(x["adv"]["price"]) for x in data if "adv" in x and "price" in x["adv"]]
            return min(prices) if prices else None
