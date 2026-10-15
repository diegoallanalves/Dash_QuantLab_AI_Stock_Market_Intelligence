"""Plotly visuals inspired by dense quant terminals with deep-ocean colors."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CYAN="#21d9e4"; GREEN="#40e0b0"; AMBER="#f6ba5c"; RED="#f06b81"; BLUE="#79a9f7"; GRID="#213249"; BG="#091321"

def style(fig, height=260, margins=None):
    fig.update_layout(height=height, paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color="#bed1e4", family="Arial", size=10), margin=margins or dict(l=12,r=10,t=20,b=12), xaxis=dict(gridcolor=GRID, zeroline=False), yaxis=dict(gridcolor=GRID, zeroline=False), legend=dict(orientation="h",y=1.14,x=0), hovermode="x unified")
    return fig

def price_chart(df):
    view=df.tail(150)
    fig=make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[.66,.16,.18], vertical_spacing=.025)
    fig.add_trace(go.Candlestick(x=view.index,open=view.Open,high=view.High,low=view.Low,close=view.Close,name="OHLC",increasing_line_color=GREEN,decreasing_line_color=RED),row=1,col=1)
    for col,color in [("SMA20",CYAN),("SMA50",AMBER),("SMA200",BLUE)]:
        fig.add_trace(go.Scatter(x=view.index,y=view[col],name=col,line=dict(color=color,width=1.3)),row=1,col=1)
    fig.add_trace(go.Bar(x=view.index,y=view.Volume,name="Volume",marker_color="#267b8c"),row=2,col=1)
    fig.add_trace(go.Scatter(x=view.index,y=view.RSI,name="RSI 14",line=dict(color="#b3a2fa",width=1.5)),row=3,col=1)
    fig.add_hline(y=70,row=3,col=1,line_color=RED,line_dash="dot",line_width=1)
    fig.add_hline(y=30,row=3,col=1,line_color=GREEN,line_dash="dot",line_width=1)
    fig.update_layout(xaxis_rangeslider_visible=False,showlegend=True)
    style(fig,355)
    for axis in ("xaxis","xaxis2","xaxis3"):
        fig.layout[axis].update(gridcolor=GRID)
    fig.update_yaxes(gridcolor=GRID)
    return fig

def sparkline(series, color=CYAN):
    fig=go.Figure(go.Scatter(y=series,mode="lines",line=dict(color=color,width=1.8),fill="tozeroy",fillcolor="rgba(33,217,228,.06)"))
    style(fig,60,dict(l=0,r=0,t=0,b=0))
    fig.update_xaxes(visible=False);fig.update_yaxes(visible=False)
    return fig

def radial_network(items, seed=21):
    """Dense, deterministic spherical signal illustration (not a trained neural net)."""
    rng=np.random.default_rng(seed)
    fig=go.Figure()
    colors=[BLUE, AMBER, GREEN, RED, "#a98cf5", "#a7c2d8"]
    cx,cy=.36,0.0
    # Fine meridians and parallels establish the original reference's spherical silhouette.
    for r in (.23,.45,.66,.84,1.0):
        ang=np.linspace(0,2*np.pi,240)
        fig.add_trace(go.Scatter(x=cx+r*np.cos(ang),y=cy+r*np.sin(ang),mode="lines",line=dict(color="rgba(101,145,176,.12)",width=.6),hoverinfo="skip",showlegend=False))
    # Hundreds of nodes across a projected sphere; batched line traces for fast rendering.
    n=950
    theta=rng.uniform(0,2*np.pi,n)
    radial=np.sqrt(rng.uniform(.003,1,n))
    xx=cx+radial*np.cos(theta)
    yy=cy+radial*np.sin(theta)
    group=rng.integers(0,len(items),n)
    for i,item in enumerate(items):
        color=colors[i%len(colors)]
        sy=.84-i*.335
        startx=-1.75
        hubx=-.73
        huby=sy*.86
        # Source signal: small waveform at left, connector, and an intermediate hub.
        t=np.linspace(0,1,65)
        wave=sy+.024*np.sin(t*13+i)*np.exp(-.7*t)+.007*np.sin(t*29+i*2)
        fig.add_trace(go.Scatter(x=-2.63+.68*t,y=wave,mode="lines",line=dict(color=color,width=2),showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[-1.94,hubx],y=[sy,huby],mode="lines+markers",line=dict(color=color,width=1.8),marker=dict(color=color,size=[3,7]),showlegend=False,hoverinfo="skip"))
        fig.add_annotation(x=-2.63,y=sy+.11,text=f"<b>{item['name'].upper()}</b>  {item['score']:+.2f}",showarrow=False,xanchor="left",font=dict(size=10,color=color))
        ids=np.flatnonzero(group==i)
        lx=[];ly=[]
        for k in ids:
            # Hub -> spherical observation; some inner links add depth.
            lx.extend([hubx,float(xx[k]),None])
            ly.extend([huby,float(yy[k]),None])
        fig.add_trace(go.Scattergl(x=lx,y=ly,mode="lines",line=dict(color=color,width=.55),opacity=.19,hoverinfo="skip",showlegend=False))
        fig.add_trace(go.Scattergl(x=xx[ids],y=yy[ids],mode="markers",marker=dict(size=rng.uniform(1.5,4.2,len(ids)),color=color,opacity=.75),hovertemplate=f"{item['name']} observation<extra></extra>",showlegend=False))
    # Subtle dense radial spokes from the decision center to a subset of observations.
    lx=[];ly=[]
    for k in rng.choice(n,size=210,replace=False):
        lx.extend([cx,float(xx[k]),None]);ly.extend([cy,float(yy[k]),None])
    fig.add_trace(go.Scattergl(x=lx,y=ly,mode="lines",line=dict(color="rgba(173,205,220,.20)",width=.45),hoverinfo="skip",showlegend=False))
    # Sparse brighter 'active' observations to mimic the reference's illuminated orb.
    ids=rng.choice(n,size=65,replace=False)
    fig.add_trace(go.Scattergl(x=xx[ids],y=yy[ids],mode="markers",marker=dict(size=rng.uniform(3,7,len(ids)),color=AMBER,opacity=.75),hoverinfo="skip",showlegend=False))
    fig.add_trace(go.Scatter(x=[cx],y=[cy],mode="markers+text",text=["DECISION"],textposition="middle center",textfont=dict(size=9,color="white"),marker=dict(size=37,color="#113b4d",line=dict(color=CYAN,width=1.5)),hoverinfo="skip",showlegend=False))
    style(fig,610,dict(l=0,r=0,t=8,b=0))
    fig.update_layout(dragmode="pan",hovermode="closest",uirevision="orb")
    fig.update_xaxes(visible=False,range=[-2.85,1.52],fixedrange=False)
    fig.update_yaxes(visible=False,range=[-1.15,1.15],scaleanchor="x",scaleratio=1,fixedrange=False)
    return fig

def backtest_chart(bt):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=bt.index,y=(bt.strategy_equity-1)*100,name="SMA strategy",line=dict(color=CYAN,width=2)))
    fig.add_trace(go.Scatter(x=bt.index,y=(bt.benchmark_equity-1)*100,name="Buy & hold",line=dict(color=BLUE,width=1.5)))
    return style(fig,205)

def state_chart(items):
    names=[a["name"] for a in items]
    vals=[a["score"] for a in items]
    fig=go.Figure(go.Bar(x=vals,y=names,orientation="h",marker_color=[GREEN if v>=0 else RED for v in vals]))
    fig.update_xaxes(range=[-1,1],title="Rule score")
    fig.update_yaxes(autorange="reversed")
    return style(fig,235)
