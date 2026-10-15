"""Animated SVG orb: no JavaScript or Canvas required."""
import html
import math
import random

COLORS = ("#66a8ff", "#f5bc55", "#19dbc0", "#ff637b", "#b89cff", "#9ed7ec")

def orb_html(items):
    rng = random.Random(24413)
    names = [html.escape(str(x.get("name", "SIGNAL"))[:22]) for x in items[:6]]
    scores = [float(x.get("score", 0)) for x in items[:6]]
    while len(names) < 6:
        names.append("SIGNAL")
        scores.append(0)
    cx, cy, R = 770, 295, 222
    hubs = [(285, 91 + 81*i) for i in range(6)]
    p = ['<rect width="1200" height="590" fill="#07111e"/>']
    for r in (60,110,165,225):
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*.91:.1f}" fill="none" stroke="#32576a" stroke-opacity=".35"/>')
    for i,((hx,hy),name,score) in enumerate(zip(hubs,names,scores)):
        color=COLORS[i]
        p.append(f'<text x="18" y="{hy-16}" fill="{color}" font-family="monospace" font-size="13" font-weight="bold">{name.upper()}</text>')
        p.append(f'<text x="18" y="{hy}" fill="#b9d2df" font-family="monospace" font-size="11">SCORE {score:+.2f}</text>')
        pts = " ".join(f"{18+j*3.5:.1f},{hy+20+math.sin(j*.32+i)*5:.1f}" for j in range(56))
        p.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5" class="blink"/>')
        p.append(f'<path d="M214 {hy+18} L{hx} {hy}" stroke="{color}" stroke-opacity=".6"/>')
        p.append(f'<circle cx="{hx}" cy="{hy}" r="3" fill="{color}"/>')
    p.append(f'<g class="orbital" style="transform-origin:{cx}px {cy}px">')
    nodes=[]
    for i in range(950):
        a=rng.random()*math.tau
        r=math.sqrt(rng.random())*R
        x,y=cx+math.cos(a)*r,cy+math.sin(a)*r*.91
        nodes.append((x,y))
        color=COLORS[i%6]
        if i%2==0:
            p.append(f'<path d="M{cx} {cy} L{x:.1f} {y:.1f}" stroke="{color}" stroke-opacity=".12" stroke-width=".65"/>')
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1+rng.random()*1.3:.1f}" fill="{("#ffd36c" if i%29==0 else color)}" class="twinkle" style="animation-delay:-{rng.random()*4:.1f}s"/>')
    p.append('</g>')
    for i,(hx,hy) in enumerate(hubs):
        for j in range(12):
            x,y=nodes[(i+j*43)%len(nodes)]
            p.append(f'<path d="M{hx} {hy} L{x:.1f} {y:.1f}" stroke="{COLORS[i]}" stroke-opacity=".15" stroke-width=".6"/>')
        p.append(f'<circle r="2.6" fill="{COLORS[i]}"><animateMotion dur="{2+i*.3:.1f}s" repeatCount="indefinite" path="M{hx} {hy} L{cx} {cy}"/></circle>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="32" fill="#0b4558" stroke="#1be3e3" stroke-width="2" class="pulse"/>')
    p.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-family="monospace" font-size="12">DECISION</text>')
    svg="".join(p)
    css = """
    html,body{margin:0;background:#07111e;overflow:hidden}
    svg{width:100%;height:590px;display:block}
    .orbital{animation:turn 110s linear infinite}
    .twinkle{animation:blink 3s ease-in-out infinite alternate}
    .pulse{animation:blink 2s ease-in-out infinite alternate}
    .blink{animation:blink 1.7s ease-in-out infinite alternate}
    @keyframes turn{to{transform:rotate(360deg)}}
    @keyframes blink{from{opacity:.4}to{opacity:1}}
    @media(prefers-reduced-motion:reduce){.orbital,.twinkle,.pulse,.blink{animation:none}}
    """
    return ('<!doctype html><html><head><meta charset="utf-8"><style>'+css+'</style></head><body>'
            +'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 590" preserveAspectRatio="xMidYMid meet">'
            +svg+'</svg></body></html>')
