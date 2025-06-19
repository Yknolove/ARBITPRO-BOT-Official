import sys
import types
import pytest

# Stub aiohttp so importing services.aggregator does not require the real
# dependency during tests.
aiohttp_stub = types.ModuleType("aiohttp")
class ClientSession:
    pass
aiohttp_stub.ClientSession = ClientSession
sys.modules.setdefault("aiohttp", aiohttp_stub)

from services.aggregator import parse_tickers


def test_volume_from_best_bid():
    raw = [{
        "symbol": "BTCUSDT",
        "bid1Price": "10",
        "bid1Size": "5",
        "ask1Price": "10.5",
        "lastPrice": "10",
        "volume24h": "1000",
    }]
    result = parse_tickers(raw)
    assert len(result) == 1
    assert result[0]["volume"] == 50.0


def test_volume_fallback_to_24h_when_missing_bid_fields():
    raw = [{
        "symbol": "ETHUSDT",
        "ask1Price": "11",
        "lastPrice": "10",
        "volume24h": "2000",
    }]
    result = parse_tickers(raw)
    assert result[0]["volume"] == 2000.0


def test_volume_fallback_when_size_missing():
    raw = [{
        "symbol": "XRPUSDT",
        "bid1Price": "1",
        "ask1Price": "1.1",
        "lastPrice": "1",
        "volume24h": "3000",
    }]
    result = parse_tickers(raw)
    assert result[0]["volume"] == 3000.0

