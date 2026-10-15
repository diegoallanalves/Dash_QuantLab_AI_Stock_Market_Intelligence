"""Technical indicators, interpretable agents, and non-lookahead daily backtesting."""
import numpy as np
import pandas as pd


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    c = x["Close"]
    for n in (20, 50, 200):
        x[f"SMA{n}"] = c.rolling(n).mean()
    delta = c.diff()
    gains = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    losses = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gains / losses.replace(0, np.nan)
    x["RSI"] = (100 - 100 / (1 + rs)).fillna(50)
    ema12, ema26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    x["MACD"] = ema12 - ema26
    x["MACD_signal"] = x["MACD"].ewm(span=9, adjust=False).mean()
    x["Return"] = c.pct_change().fillna(0)
    x["Volatility"] = x["Return"].rolling(21).std() * np.sqrt(252)
    x["BB_upper"] = x["SMA20"] + 2 * c.rolling(20).std()
    x["BB_lower"] = x["SMA20"] - 2 * c.rolling(20).std()
    return x


def agents(df: pd.DataFrame) -> list[dict]:
    """Six transparent rule-based agent scores; no LLM or trained AI is implied."""
    r = df.iloc[-1]
    close = float(r["Close"])
    sma20, sma50 = float(r["SMA20"]), float(r["SMA50"])
    rsi = float(r["RSI"])
    vol = float(r["Volatility"]) if pd.notna(r["Volatility"]) else 0.3
    macd_gap = float(r["MACD"] - r["MACD_signal"])
    avg_vol = float(df["Volume"].tail(21).mean())
    volume_ratio = float(r["Volume"]) / avg_vol if avg_vol else 1
    def clamp(v): return round(float(np.clip(v, -1, 1)), 2)
    return [
        {"name": "TREND", "score": clamp((close / sma50 - 1) * 10 if sma50 else 0), "detail": "Close vs 50-day SMA"},
        {"name": "MOMENTUM", "score": clamp((rsi - 50) / 35), "detail": f"RSI {rsi:.1f}"},
        {"name": "MACD", "score": clamp(macd_gap / max(close * 0.012, 0.01)), "detail": "MACD vs signal line"},
        {"name": "VOLUME", "score": clamp((volume_ratio - 1) / 2), "detail": f"Volume ratio {volume_ratio:.2f}x"},
        {"name": "VOLATILITY", "score": clamp(0.5 - vol * 2), "detail": f"Annualized vol {vol:.1%}"},
        {"name": "RISK", "score": clamp(0.4 - max(0, (sma20 - close) / max(sma20, 1)) * 8 - vol), "detail": "Risk-adjusted context"},
    ]


def decision(items: list[dict]) -> tuple[str, float]:
    score = float(np.mean([x["score"] for x in items]))
    label = "BUY" if score > 0.18 else "SELL" if score < -0.18 else "HOLD"
    return label, score


def backtest(df: pd.DataFrame, fee_bps: float = 5, slippage_bps: float = 3) -> pd.DataFrame:
    """Long-only SMA20/SMA50 crossover, next-bar execution, costs on position changes."""
    x = enrich(df)
    target = (x["SMA20"] > x["SMA50"]).astype(float)
    target[x["SMA50"].isna()] = 0
    # Signal from yesterday determines exposure over today's close-to-close return.
    exposure = target.shift(1).fillna(0)
    turnover = exposure.diff().abs().fillna(exposure.abs())
    gross = exposure * x["Return"]
    net = gross - turnover * (fee_bps + slippage_bps) / 10_000
    result = pd.DataFrame(index=x.index)
    result["strategy_return"] = net
    result["benchmark_return"] = x["Return"]
    result["strategy_equity"] = (1 + net).cumprod()
    result["benchmark_equity"] = (1 + x["Return"]).cumprod()
    result["exposure"] = exposure
    result["drawdown"] = result["strategy_equity"] / result["strategy_equity"].cummax() - 1
    return result


def performance(bt: pd.DataFrame) -> dict:
    daily = bt["strategy_return"]
    total = float(bt["strategy_equity"].iloc[-1] - 1)
    annual = float((1 + total) ** (252 / max(len(bt), 1)) - 1) if total > -1 else -1.0
    sigma = float(daily.std())
    sharpe = float(daily.mean() / sigma * np.sqrt(252)) if sigma > 0 else 0.0
    return {"total_return": total, "annual_return": annual, "sharpe": sharpe, "max_drawdown": float(bt["drawdown"].min()), "benchmark_return": float(bt["benchmark_equity"].iloc[-1] - 1)}
