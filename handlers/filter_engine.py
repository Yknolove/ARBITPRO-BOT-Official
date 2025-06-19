import json

def apply_filters(tickers, filters_file):
    try:
        with open(filters_file, "r") as f:
            filters = json.load(f)
    except Exception:
        filters = {}

    results = []
    for chat_id, f in filters.items():
        buy_limit = float(f.get("buy_price", 0))
        sell_limit = float(f.get("sell_price", 999999))
        # "volume" represents the trade size derived from the best bid
        # (bid1Price * bid1Size). If that is not available, the aggregator
        # falls back to the ticker's 24h volume. User limits compare
        # against this value.
        vol_limit = float(f.get("volume", 100))
        exchange = f.get("exchange", "bybit")

        for t in tickers:
            # Исправленная логика фильтрации
            if (
                t["price"] <= buy_limit and
                t.get("sell_price", t["price"]) >= sell_limit and
                t["volume"] <= vol_limit
            ):
                results.append({
                    **t,
                    "chat_id": chat_id,
                    "exchange": exchange
                })
    return results
