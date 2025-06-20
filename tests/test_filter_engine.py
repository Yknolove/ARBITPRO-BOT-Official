import json
from services.filter_engine import apply_filters


def test_apply_filters_respects_limits(tmp_path):
    filters = {"1": {"buy_price": 100, "sell_price": 500, "volume": 10}}
    fpath = tmp_path / "filters.json"
    fpath.write_text(json.dumps(filters))

    tickers = [
        {"symbol": "AAA", "price": 90, "sell_price": 520, "volume": 5},
        {"symbol": "BBB", "price": 90, "sell_price": 480, "volume": 5},
        {"symbol": "CCC", "price": 110, "sell_price": 520, "volume": 5},
        {"symbol": "DDD", "price": 90, "sell_price": 520, "volume": 15},
    ]

    result = apply_filters(tickers, fpath)
    assert len(result) == 1
    entry = result[0]
    assert entry["symbol"] == "AAA"
    assert entry["chat_id"] == "1"
