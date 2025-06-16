import aiohttp

class RateFetcher:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_bybit(self):
        url = "https://api.bybit.com/v5/market/tickers?category=spot"

        try:
            async with self.session.get(url) as r:
                if r.status != 200:
                    raise Exception(f"Bybit responded with status {r.status}")
                data = await r.json()
                tickers = data.get("result", {}).get("list", [])
                print(f"✅ Загружено {len(tickers)} тикеров с Bybit")
                return tickers
        except Exception as e:
            print(f"❌ Ошибка Bybit: {e}")
            return []
