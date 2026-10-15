import numpy as np
from quantlab.data import demo_ohlcv, validate_ohlcv
from quantlab.analytics import enrich, agents, decision, backtest, performance


def test_demo_reproducible():
    a=demo_ohlcv('AAPL',260)
    b=demo_ohlcv('AAPL',260)
    np.testing.assert_allclose(a.Close.values,b.Close.values)
    assert validate_ohlcv(a)['invalid_bars']==0


def test_indicators_and_agents():
    x=enrich(demo_ohlcv('NVDA',350))
    assert np.isfinite(x.SMA200.iloc[-1])
    assert 0 <= x.RSI.iloc[-1] <= 100
    six=agents(x)
    assert len(six)==6
    assert all(-1<=a['score']<=1 for a in six)
    assert decision(six)[0] in ('BUY','HOLD','SELL')


def test_backtest_next_bar_and_costs():
    x=demo_ohlcv('SPY',260)
    free=backtest(x,fee_bps=0,slippage_bps=0)
    charged=backtest(x,fee_bps=10,slippage_bps=10)
    assert len(free)==len(x)
    assert charged.strategy_equity.iloc[-1]<=free.strategy_equity.iloc[-1]+1e-9
    assert np.isfinite(performance(charged)['sharpe'])
