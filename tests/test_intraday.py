from quantlab.data import demo_ohlcv, validate_ohlcv

def test_demo_has_valid_bars():
    bars=demo_ohlcv("AAPL",260)
    assert validate_ohlcv(bars)["invalid_bars"]==0
