import json
import logging


def apply_filters(tickers, filters_file):
    """Load user filters from ``filters_file`` and apply them to ``tickers``."""
    try:
        with open(filters_file, "r") as f:
            filters = json.load(f)
    except Exception:
        filters = {}

    results = []
    for chat_id, f in filters.items():
        buy_limit = float(f.get("buy_price", 0))
        sell_limit = float(f.get("sell_price", 999999))
        # "volume" represents the trade size taken from the best bid when
        # available (bid1Price * bid1Size). If that information is missing,
        # the aggregator falls back to the ticker's 24h volume.
        vol_limit = float(f.get("volume", 100))
        exchange = f.get("exchange", "bybit")

        for t in tickers:
            # Debug print
            if "price" not in t:
                logging.warning(f"[filter_engine] Нет ключа 'price' в: {t}")
                continue
            if (
                t["price"] <= buy_limit and
                t.get("sell_price", t["price"]) >= sell_limit and
                t.get("volume", 0) <= vol_limit
            ):
                results.append({
                    **t,
                    "chat_id": chat_id,
                    "exchange": exchange
                })
    return results
