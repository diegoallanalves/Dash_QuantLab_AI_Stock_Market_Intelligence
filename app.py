"""QuantLab AI | A dense, ocean-themed stock research terminal.

All strategy decisions are illustrative rule-based research signals, not investment advice.
"""
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from quantlab.animated_orb import orb_html
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from quantlab.data import TICKERS, demo_ohlcv, download_ohlcv, validate_ohlcv
from quantlab.analytics import enrich, agents, decision, backtest, performance
from quantlab.visuals import price_chart, sparkline, radial_network, backtest_chart, state_chart, CYAN, GREEN, RED, AMBER, BLUE, style

st.set_page_config(page_title="QuantLab AI | Stock Research Terminal", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#060e1a;color:#e8f3fc}
[data-testid="stAppViewContainer"]>.main .block-container{max-width:1900px;padding:1rem 1.3rem 3rem}
[data-testid="stHeader"]{height:0}
#MainMenu,footer{visibility:hidden}
h1,h2,h3,p{font-family:Inter,sans-serif} h1{font-size:1.75rem!important;letter-spacing:-.5px;margin:0!important}
h3{font-size:.9rem!important;color:#d5e9f5;margin:0 0 .6rem!important}
[data-testid="stMetric"]{background:#0b1b2b;border:1px solid #1c4150;border-radius:5px;padding:9px 12px;min-height:82px}
[data-testid="stMetricLabel"]{color:#8eacbf;font-size:.72rem}[data-testid="stMetricValue"]{font-family:'IBM Plex Mono',monospace;font-size:1.28rem}
[data-testid="stPlotlyChart"]{border:1px solid #183b4c;background:#091321;border-radius:5px;padding:3px}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#1d4350!important;border-radius:5px!important}
[data-testid="stTabs"] button{color:#a5c6d4} .stButton button{border-color:#22707c}
div[data-testid="stSelectbox"] label,div[data-testid="stRadio"] label{color:#9dbdce}
.mini{font:10px 'IBM Plex Mono',monospace;color:#7ca7bb;letter-spacing:1px;text-transform:uppercase}
.head{font:700 12px 'IBM Plex Mono',monospace;color:#d9f5f8;margin:5px 0 10px}
.ribbon{background:linear-gradient(90deg,#0c3040,#071a2a);border:1px solid #1d5664;padding:9px 13px;margin-bottom:12px;border-radius:4px;font:11px 'IBM Plex Mono',monospace;color:#7edbe2}
.agent{background:#0b1d2e;border:1px solid #1b4754;border-left:3px solid #1bd6d9;border-radius:3px;padding:8px;margin:4px 0;font:12px 'IBM Plex Mono',monospace}
.agent span{float:right;font-weight:700}
.decision{background:#062b30;border:1px solid #17bfae;padding:14px;border-radius:5px;text-align:center;color:#3ae3bb;font:700 27px 'IBM Plex Mono',monospace}
.note{font-size:.73rem;color:#83a3b5}.small{font-size:.83rem;color:#c4dce9}
</style>''',unsafe_allow_html=True)

@st.cache_data(ttl=900,show_spinner=False)
def get_market_data(ticker, source):
    if source=="Historical market data (Yahoo Finance)":
        return download_ohlcv(ticker)
    return demo_ohlcv(ticker)

st.markdown('<div class="mini">◉ QUANTLAB AI / RESEARCH TERMINAL / US EQUITIES · DEEP OCEAN EDITION</div>',unsafe_allow_html=True)
title_col, control_col, date_col = st.columns([2.0,2.7,1.6],vertical_alignment="center")
with title_col:
    st.title("◈ QUANTLAB AI")
    st.caption("SIX SIGNAL AGENTS · PROBABILITY STATES · DECISION NETWORK · BACKTESTING")
with control_col:
    ticker=st.selectbox("Instrument",list(TICKERS),format_func=lambda x:f"{x} — {TICKERS[x]}",label_visibility="collapsed")
    source=st.selectbox("Source",["Synthetic demo (offline)","Historical market data (Yahoo Finance)"],label_visibility="collapsed")
    refresh_label=st.selectbox("Auto-refresh",["15 seconds", "1 minute", "15 minutes", "30 minutes", "1 hour"],index=0)
with date_col:
    st.markdown(f'<div class="mini">{datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")}</div>',unsafe_allow_html=True)
    st.caption("HISTORICAL + INTRADAY · NO LIVE ORDERS")

refresh_seconds={"15 seconds":15,"1 minute":60,"15 minutes":900,"30 minutes":1800,"1 hour":3600}[refresh_label]
refresh_count=st_autorefresh(interval=refresh_seconds*1000,limit=None,key="quantlab_auto_refresh")

@st.cache_data(ttl=15,show_spinner=False)
def get_intraday_data(ticker):
    from quantlab.data import download_intraday
    return download_intraday(ticker)

# Intraday data is optional: errors are visible and never replaced with fabricated live prices.
intraday=None
intraday_error=None
if source.startswith("Historical"):
    try:
        intraday=get_intraday_data(ticker)
    except Exception as exc:
        intraday_error=str(exc)

try:
    raw=get_market_data(ticker,source)
except Exception as e:
    st.error(f"Market-data download failed: {e}. Select 'Synthetic demo (offline)' to continue.")
    st.stop()
if len(raw)<210:
    st.error("At least 210 daily bars are needed for the 200-day indicator. Choose a longer data history.")
    st.stop()
df=enrich(raw)
items=agents(df)
call, score=decision(items)
last=df.iloc[-1]
prev=df.iloc[-2]
change=float(last.Close/prev.Close-1)
bt=backtest(raw)
perf=performance(bt)
quality=validate_ohlcv(raw)
mode="SYNTHETIC / DEMO DATA" if source.startswith("Synthetic") else "HISTORICAL / YAHOO FINANCE · DELAYED"
st.markdown(f'<div class="ribbon">● REFRESH: {refresh_label.upper()} &nbsp;&nbsp; / &nbsp;&nbsp; DATA MODE: {mode} &nbsp;&nbsp; / &nbsp;&nbsp; SYMBOL: {ticker} &nbsp;&nbsp; / &nbsp;&nbsp; LAST BAR: {df.index[-1].date()} &nbsp;&nbsp; / &nbsp;&nbsp; SIGNAL: {call} &nbsp;&nbsp; / &nbsp;&nbsp; RULE SCORE: {score:+.2f} &nbsp;&nbsp; / &nbsp;&nbsp; PAPER RESEARCH ONLY</div>',unsafe_allow_html=True)

# Top telemetry strip: all four instruments, actual data if selected; demo otherwise.
top=st.columns(4)
for col,sym in zip(top,TICKERS):
    with col:
        if sym==ticker: s=df
        else:
            try: s=enrich(get_market_data(sym,source))
            except Exception: s=None
        if s is not None and len(s)>1:
            v=float(s.Close.iloc[-1]); d=float(s.Close.iloc[-1]/s.Close.iloc[-2]-1)
            st.metric(sym,f"${v:,.2f}",f"{d:+.2%}")

left,middle,right=st.columns([1.1,1.7,1.13],gap="small")
with left:
    with st.container(border=True):
        st.markdown('<div class="head">▸ MARKET OVERVIEW</div>',unsafe_allow_html=True)
        st.markdown(f'### {ticker} · {TICKERS[ticker]}')
        st.metric("LAST DAILY CLOSE",f"${last.Close:,.2f}",f"{change:+.2%}")
        if intraday is not None and not intraday.empty:
            latest=intraday.iloc[-1]
            st.metric("LATEST AVAILABLE INTRADAY",f"${latest.Close:,.2f}")
            st.caption(f"Provider timestamp: {intraday.index[-1].strftime('%Y-%m-%d %H:%M %Z')} · may be delayed")
        elif intraday_error:
            st.caption("Intraday feed unavailable: " + intraday_error[:140])
        a,b=st.columns(2)
        a.caption(f"OPEN  ${last.Open:,.2f}")
        b.caption(f"HIGH  ${last.High:,.2f}")
        a.caption(f"LOW  ${last.Low:,.2f}")
        b.caption(f"VOLUME  {last.Volume/1e6:,.1f}M")
    with st.container(border=True):
        st.markdown('<div class="head">▸ KEY METRICS</div>',unsafe_allow_html=True)
        a,b,c=st.columns(3)
        a.metric("52W HIGH",f"${df.High.tail(252).max():,.1f}")
        b.metric("52W LOW",f"${df.Low.tail(252).min():,.1f}")
        c.metric("RSI 14",f"{last.RSI:.1f}")
        a,b=st.columns(2)
        a.metric("VOLATILITY",f"{last.Volatility:.1%}")
        b.metric("20D SMA",f"${last.SMA20:,.2f}")
    with st.container(border=True):
        st.markdown('<div class="head">▸ MARKET OBSERVABLES</div>',unsafe_allow_html=True)
        st.plotly_chart(sparkline(df.Close.tail(60),CYAN),width="stretch",config={"displayModeBar":False})
        st.caption("Price action · last 60 sessions")
        st.plotly_chart(sparkline(df.Volume.tail(60),AMBER),width="stretch",config={"displayModeBar":False})
        st.caption("Trading volume · last 60 sessions")
with middle:
    with st.container(border=True):
        st.markdown('<div class="head">▸ PRICE ACTION / TECHNICAL INDICATORS</div>',unsafe_allow_html=True)
        st.plotly_chart(price_chart(df),width="stretch",config={"displayModeBar":False})
        if intraday is not None and len(intraday)>2:
            st.markdown('<div class="head">▸ INTRADAY / 1-MINUTE BARS (LATEST AVAILABLE)</div>',unsafe_allow_html=True)
            fig=go.Figure(go.Candlestick(x=intraday.index,open=intraday.Open,high=intraday.High,low=intraday.Low,close=intraday.Close,increasing_line_color=GREEN,decreasing_line_color=RED,name="1m OHLC"))
            fig.update_layout(template="plotly_dark",paper_bgcolor="#091321",plot_bgcolor="#091321",height=235,margin=dict(l=12,r=12,t=8,b=10),xaxis_rangeslider_visible=False,font_color="#bcd3e2")
            st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
            st.caption("1-minute bars are provider-dependent and can be delayed. Auto-refresh does not guarantee new trades or quotes.")
with right:
    with st.container(border=True):
        st.markdown('<div class="head">▸ RULE-BASED SIGNAL SUMMARY</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="decision">{call}</div>',unsafe_allow_html=True)
        st.metric("COMPOSITE RULE SCORE",f"{score:+.2f}")
        st.progress(min(1.0,max(0.0,(score+1)/2)))
        st.caption("Score is NOT a calibrated probability, price target or forecast.")
    with st.container(border=True):
        st.markdown('<div class="head">▸ SIX-AGENT DECISION STACK</div>',unsafe_allow_html=True)
        for item in items:
            color=GREEN if item['score']>=0 else RED
            st.markdown(f'<div class="agent" style="border-left-color:{color}">{item["name"]}<span style="color:{color}">{item["score"]:+.2f}</span><br><small style="color:#829db0">{item["detail"]}</small></div>',unsafe_allow_html=True)

network_col, stack_col=st.columns([3.35,1],gap="small")
with network_col:
    with st.container(border=True):
        st.markdown('<div class="head">▸ THE ORB / SIX AGENTS / SIGNAL PROPAGATION</div>',unsafe_allow_html=True)
        st.caption("950 observation nodes · continuously animated signal propagation · decorative visualization, not a trained neural network or live order flow.")
        components.html(orb_html(items),height=590,scrolling=False)
with stack_col:
    with st.container(border=True):
        st.markdown('<div class="head">▸ STATE BUILDER / SIGNAL STRENGTH</div>',unsafe_allow_html=True)
        st.plotly_chart(state_chart(items),width="stretch",config={"displayModeBar":False})
        st.markdown('<div class="head">▸ DECISION RULES</div>',unsafe_allow_html=True)
        st.markdown('<div class="small">BUY: score above +0.18<br>HOLD: score between -0.18 and +0.18<br>SELL: score below -0.18</div>',unsafe_allow_html=True)
        st.caption("Signals summarize current historical indicators. They are not personalized financial advice.")

bottom_left,bottom_mid,bottom_right=st.columns([1.05,1.55,1.15],gap="small")
with bottom_left:
    with st.container(border=True):
        st.markdown('<div class="head">▸ SIX AGENTS / OBSERVATIONS IN</div>',unsafe_allow_html=True)
        for row in (items[:3],items[3:]):
            cols=st.columns(3)
            for col,item in zip(cols,row):
                with col:
                    st.metric(item['name'],f"{item['score']:+.2f}")
    with st.container(border=True):
        st.markdown('<div class="head">▸ SIGNAL LOG / LATEST BAR</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(items)[['name','score','detail']],hide_index=True,width="stretch",height=255)
with bottom_mid:
    with st.container(border=True):
        st.markdown('<div class="head">▸ BACKTESTING / SMA 20–50 CROSSOVER</div>',unsafe_allow_html=True)
        st.caption("Historical long-only strategy · next-bar execution · 5 bps fee + 3 bps slippage per position change")
        a,b,c,d=st.columns(4)
        a.metric("TOTAL RETURN",f"{perf['total_return']:+.1%}")
        b.metric("ANNUALIZED",f"{perf['annual_return']:+.1%}")
        c.metric("SHARPE",f"{perf['sharpe']:.2f}")
        d.metric("MAX DRAWDOWN",f"{perf['max_drawdown']:.1%}")
        st.plotly_chart(backtest_chart(bt),width="stretch",config={"displayModeBar":False})
        st.caption(f"Buy-and-hold benchmark: {perf['benchmark_return']:+.1%}. Backtest is in-sample research, not a future-performance claim.")
with bottom_right:
    with st.container(border=True):
        st.markdown('<div class="head">▸ DATA PIPELINE / QUALITY STATUS</div>',unsafe_allow_html=True)
        st.metric("INGESTED BARS",f"{quality['rows']:,}")
        st.metric("MISSING CELLS",quality['missing_cells'])
        st.metric("DUPLICATE DATES",quality['duplicate_dates'])
        st.metric("INVALID BARS",quality['invalid_bars'])
        st.caption(f"Source: {mode}. Last daily bar: {df.index[-1].date()}.")
        st.caption(f"Refresh every {refresh_label}; reruns: {refresh_count}. Refresh is not an exchange streaming feed.")
    with st.container(border=True):
        st.markdown('<div class="head">▸ EXPORT / REPRODUCIBILITY</div>',unsafe_allow_html=True)
        st.download_button("Download daily indicators (CSV)",df.to_csv().encode(),file_name=f"{ticker}_quantlab_indicators.csv",mime="text/csv",width="stretch")
        st.download_button("Download backtest (CSV)",bt.to_csv().encode(),file_name=f"{ticker}_quantlab_backtest.csv",mime="text/csv",width="stretch")

st.divider()
st.caption("QuantLab AI · Educational quantitative research dashboard · No brokerage connection, real orders, trained forecasting model, live order flow, or investment recommendations. Yahoo Finance daily and intraday bars may be delayed or unavailable. Auto-refresh is polling, not exchange-grade real-time data.")
