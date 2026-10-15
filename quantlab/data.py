"""Historical daily market data. Demo data is clearly labeled as synthetic."""
import numpy as np
import pandas as pd

TICKERS = {"AAPL": "Apple", "NVDA": "NVIDIA", "TSLA": "Tesla", "SPY": "S&P 500 ETF"}


def demo_ohlcv(ticker: str, days: int = 520) -> pd.DataFrame:
    """Deterministic, correlated synthetic OHLCV for offline demonstration."""
    seed = {"AAPL": 17, "NVDA": 31, "TSLA": 43, "SPY": 59}.get(ticker, 73)
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    drift = {"AAPL": 0.0005, "NVDA": 0.0008, "TSLA": 0.0003, "SPY": 0.00035}.get(ticker, 0.0003)
    vol = {"AAPL": 0.018, "NVDA": 0.028, "TSLA": 0.032, "SPY": 0.011}.get(ticker, 0.018)
    returns = rng.normal(drift, vol, days)
    close = np.exp(np.log({"AAPL": 175, "NVDA": 125, "TSLA": 245, "SPY": 530}.get(ticker, 100)) + np.cumsum(returns))
    opn = close * (1 + rng.normal(0, 0.004, days))
    high = np.maximum(opn, close) * (1 + rng.uniform(0.001, 0.014, days))
    low = np.minimum(opn, close) * (1 - rng.uniform(0.001, 0.014, days))
    volume = rng.integers(12_000_000, 90_000_000, days)
    return pd.DataFrame({"Open": opn, "High": high, "Low": low, "Close": close, "Volume": volume}, index=dates).rename_axis("Date")


def download_ohlcv(ticker: str, period: str = "2y") -> pd.DataFrame:
    """Fetch Yahoo Finance daily bars; fail explicitly, never silently substitute demo data."""
    import yfinance as yf
    raw = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False, threads=False)
    if raw is None or raw.empty:
        raise RuntimeError(f"No market data returned for {ticker}.")
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None) if df.index.tz is not None else pd.to_datetime(df.index)
    return df.dropna(subset=["Close"]).sort_index()


def validate_ohlcv(df: pd.DataFrame) -> dict:
    missing = int(df[["Open", "High", "Low", "Close", "Volume"]].isna().sum().sum())
    duplicates = int(df.index.duplicated().sum())
    bad_prices = int(((df["Low"] > df["High"]) | (df["Close"] <= 0) | (df["Volume"] < 0)).sum())
    return {"rows": len(df), "missing_cells": missing, "duplicate_dates": duplicates, "invalid_bars": bad_prices}


def download_intraday(ticker: str) -> pd.DataFrame:
    """Retrieve latest available 1-minute OHLCV bars (typically recent trading days).

    Yahoo Finance availability and exchange delays vary. Never substitute synthetic
    data for a failed live request. Timestamps remain timezone-aware.
    """
    import yfinance as yf
    raw=yf.download(ticker,period="5d",interval="1m",auto_adjust=True,progress=False,threads=False)
    if raw is None or raw.empty:
        raise RuntimeError(f"No 1-minute bars available for {ticker}.")
    if isinstance(raw.columns,pd.MultiIndex):
        raw.columns=raw.columns.get_level_values(0)
    bars=raw[["Open","High","Low","Close","Volume"]].copy()
    bars.index=pd.to_datetime(bars.index)
    return bars.dropna(subset=["Close"]).sort_index()
