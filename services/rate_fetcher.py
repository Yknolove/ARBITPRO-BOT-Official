class RateFetcher:
    def __init__(self, session):
        self.session = session

    async def fetch_bybit(self):
        url = "https://api.bybit.com/v2/public/tickers"
        async with self.session.get(url) as resp:
            data = await resp.json()
            filtered = []
            for item in data.get("result", []):
                try:
                    symbol = item.get("symbol", "")
                    price = float(item.get("last_price", 0))
                    volume = float(item.get("turnover_24h", 0))
                    filtered.append({"symbol": symbol, "price": price, "volume": volume})
                except:
                    continue
            return filtered
