#!/usr/bin/env python3
"""LaRojaFan static site builder: every Spain match ever -> SEO pages. Run: python3 build.py"""
import csv, json, re, html, os, shutil, unicodedata
from collections import defaultdict
from datetime import date
from urllib.parse import quote_plus
R = os.path.dirname(os.path.abspath(__file__)); D = R + '/data'; O = R + '/docs'
cfg = json.load(open(R + '/config.json')); HL = json.load(open(R + '/highlights.json'))
E = html.escape
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def dstr(d): return date.fromisoformat(d).strftime('%B %-d, %Y')
rd = lambda f: csv.DictReader(open(f'{D}/{f}.csv', encoding='utf-8'))
shoot = {(r['date'], r['home_team'], r['away_team']): r['winner'] for r in rd('shootouts')}
goals = defaultdict(list)
for g in rd('goalscorers'): goals[(g['date'], g['home_team'], g['away_team'])].append(g)

M = []
for r in rd('results'):
    if 'Spain' not in (r['home_team'], r['away_team']): continue
    home = r['home_team'] == 'Spain'; opp = r['away_team'] if home else r['home_team']
    k = (r['date'], r['home_team'], r['away_team']); played = r['home_score'] not in ('', 'NA')
    m = dict(date=r['date'], opp=opp, city=r['city'], country=r['country'], played=played, id=f"spain-vs-{slug(opp)}-{r['date']}",
             hkey=f"{r['date']}-{slug(opp)}", tour=r['tournament'], year=r['date'][:4], goals=goals.get(k, []), pen=None, f=None, a=None, res=None)
    if played:
        hs, as_ = int(r['home_score']), int(r['away_score']); m['f'], m['a'] = (hs, as_) if home else (as_, hs)
        m['res'] = 'W' if m['f'] > m['a'] else 'L' if m['f'] < m['a'] else 'D'
        if m['res'] == 'D' and k in shoot: m['pen'] = shoot[k]
    m['label'] = f"{m['year']} {m['tour']}" if m['tour'] != 'Friendly' else 'Friendly'
    M.append(m)
M.sort(key=lambda m: m['date']); P = [m for m in M if m['played']]
for i, m in enumerate(M): m['i'] = i
def rec(ms):
    w = sum(m['res'] == 'W' for m in ms); d = sum(m['res'] == 'D' for m in ms); l = sum(m['res'] == 'L' for m in ms)
    return dict(p=len(ms), w=w, d=d, l=l, gf=sum(m['f'] for m in ms), ga=sum(m['a'] for m in ms))
def score(m): return f"{m['f']}–{m['a']}" if m['played'] else 'vs'
def title(m): return f"Spain {score(m)} {m['opp']}" if m['played'] else f"Spain vs {m['opp']}"
def aff(q): return f"https://www.amazon.com/s?k={quote_plus(q)}&tag={cfg['amazon_tag']}"
def badge(m): return f'<span class="b {m["res"]}">{m["res"]}</span>' if m['played'] else '<span class="b D">–</span>'

pages = []
def write(path, t, desc, body, schema=None):
    pages.append(path); head = cfg['url'] + '/' + path.replace('index.html', '')
    ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={cfg["adsense_id"]}" crossorigin="anonymous"></script>' if cfg['adsense_id'] else ''
    ld = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ''
    out = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(t)} | LaRojaFan</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{head}">
<meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website"><link rel="stylesheet" href="/style.css">{ld}{ads}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="/">LA<b>ROJA</b>FAN</a><nav><a href="/">All matches</a><a href="/players/">Players</a><a href="/tournaments/">Tournaments</a></nav></div></header>
<main class="wrap">{body}</main><footer><div class="wrap">LaRojaFan.com is an independent fan site. Results data: open international results dataset. Some links are affiliate links; we may earn a commission at no cost to you.</div></footer></body></html>'''
    os.makedirs(os.path.dirname(f'{O}/{path}'), exist_ok=True); open(f'{O}/{path}', 'w', encoding='utf-8').write(out)

def table(ms):
    return '<table>' + ''.join(f'<tr><td>{badge(m)}</td><td><a href="/match/{m["id"]}.html">{dstr(m["date"])}</a></td><td>{E(m["opp"])}</td><td class="s">{score(m)}</td><td class="meta">{E(m["label"])}</td></tr>' for m in reversed(ms)) + '</table>'
def statbar(r): return '<div class="stats">' + ''.join(f'<div class="stat"><b>{v}</b><span>{k}</span></div>' for k, v in [('Played', r['p']), ('Won', r['w']), ('Drawn', r['d']), ('Lost', r['l']), ('Goals for', r['gf']), ('Goals against', r['ga'])]) + '</div>'
def gear(m):
    y = int(m['year']); q = 'Spain 2026 World Cup champions jersey' if y >= 2026 else f'Spain national team retro jersey' if y < 2010 else 'Spain national team jersey'
    return f'<div class="card"><b>Wear La Roja</b><p class="meta">{"Celebrate the champions" if y >= 2026 else "Fan gear and retro kits"}.</p><a class="btn" rel="sponsored nofollow" href="{aff(q)}">Shop Spain gear</a> <span class="aff">(affiliate link)</span></div>'
kit = f'<div class="card"><b>Never miss a match</b><p class="meta">Free match alerts and results straight to your inbox.</p><script async data-uid="{cfg["kit_uid"]}" src="{cfg["kit_src"]}"></script></div>' if cfg['kit_uid'] and cfg['kit_src'] else ''

# players
players = defaultdict(list)
for m in P:
    for g in m['goals']:
        if g['team'] == 'Spain' and g['own_goal'] != 'TRUE': players[g['scorer']].append((m, g))
# match pages
for m in P + [x for x in M if not x['played']]:
    vs = [x for x in P if x['opp'] == m['opp']]; r = rec(vs) if vs else None
    gl = ''.join(f'<li>{(f"<a href=/players/{slug(g[chr(115)+chr(99)+chr(111)+chr(114)+chr(101)+chr(114)])}.html>{E(g[chr(115)+chr(99)+chr(111)+chr(114)+chr(101)+chr(114)])}</a>" if g["team"]=="Spain" and g["own_goal"]!="TRUE" else E(g["scorer"]))} {g["minute"]}\'{" (pen.)" if g["penalty"]=="TRUE" else ""}{" (o.g.)" if g["own_goal"]=="TRUE" else ""} <span class="meta">{E(g["team"])}{(" · assist: "+E(g["assist"])) if g["assist"] not in ("NA","") else ""}</span></li>' for g in m['goals'])
    vid = f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{HL[m["hkey"]]}" title="{E(title(m))} highlights" allowfullscreen loading="lazy"></iframe></div>' if m['hkey'] in HL else f'<a class="btn" href="https://www.youtube.com/results?search_query={quote_plus(f"Spain {m[chr(111)+chr(112)+chr(112)]} {m[chr(121)+chr(101)+chr(97)+chr(114)]} highlights")}" rel="nofollow">Find highlights on YouTube</a>'
    outcome = {'W': 'Spain won', 'D': 'Spain drew', 'L': 'Spain lost'}.get(m['res'], 'Upcoming')
    if m['pen']: outcome += f' ({m["pen"]} won on penalties)'
    body = f'<h1>{E(title(m))}</h1><p class="meta">{E(m["label"])} · {dstr(m["date"])} · {E(m["city"])}, {E(m["country"])}</p>'
    body += (f'<div class="card"><b>{outcome}</b>{"<ul>"+gl+"</ul>" if gl else "<p class=meta>Scorer details not available for this match.</p>"}</div>' if m['played'] else '<div class="card"><b>Upcoming fixture</b><p class="meta">Check back after the final whistle for the result, scorers and highlights.</p></div>')
    body += f'<h2>Highlights</h2>{vid}' + gear(m) + kit
    if r: body += f'<h2>Spain vs {E(m["opp"])}: head to head</h2>{statbar(r)}<p><a href="/opponent/{slug(m["opp"])}.html">Every Spain–{E(m["opp"])} match →</a></p>'
    pv = M[m['i'] - 1] if m['i'] else None; nx = M[m['i'] + 1] if m['i'] + 1 < len(M) else None
    body += '<div class="pn">' + (f'<a href="/match/{pv["id"]}.html">← {E(title(pv))}</a>' if pv else '<span></span>') + (f'<a href="/match/{nx["id"]}.html">{E(title(nx))} →</a>' if nx else '') + '</div>'
    ev = {"@context": "https://schema.org", "@type": "SportsEvent", "name": f"Spain vs {m['opp']} ({m['label']})", "startDate": m['date'],
          "location": {"@type": "Place", "name": f"{m['city']}, {m['country']}"}, "competitor": [{"@type": "SportsTeam", "name": "Spain"}, {"@type": "SportsTeam", "name": m['opp']}], "sport": "Soccer"}
    d = f"Spain {score(m)} {m['opp']} on {dstr(m['date'])} in {m['city']}, {m['country']} ({m['label']}). Scorers, head-to-head record and highlights." if m['played'] else f"Spain vs {m['opp']} on {dstr(m['date'])} ({m['label']}). Preview and result."
    write(f"match/{m['id']}.html", title(m) + f" ({m['label']})", d, body, ev)
# opponents
by = defaultdict(list)
for m in M: by[m['opp']].append(m)
for o, ms in by.items():
    pm = [x for x in ms if x['played']]
    if pm: write(f"opponent/{slug(o)}.html", f"Spain vs {o}: all matches and head-to-head", f"Complete history of Spain against {o}: {len(pm)} matches, results, scorers and highlights.", f'<h1>Spain vs {E(o)}</h1>{statbar(rec(pm))}{table(pm)}')
# tournaments
tn = defaultdict(list)
for m in M: tn[m['tour']].append(m)
for t, ms in tn.items():
    pm = [x for x in ms if x['played']]
    if pm and t != 'Friendly': write(f"tournament/{slug(t)}.html", f"Spain at the {t}: every match", f"Every Spain match in the {t}: {len(pm)} games with results and scorers.", f'<h1>Spain at the {E(t)}</h1>{statbar(rec(pm))}{table(pm)}')
write('tournaments/index.html', 'Spain tournament history', 'Spain results by tournament: World Cup, European Championship, Nations League and more.',
      '<h1>Spain by tournament</h1><table>' + ''.join(f'<tr><td><a href="/tournament/{slug(t)}.html">{E(t)}</a></td><td class="meta">{sum(x["played"] for x in ms)} matches</td></tr>' for t, ms in sorted(tn.items(), key=lambda kv: -len(kv[1])) if t != 'Friendly') + '</table>')
# players
for n, gs in players.items():
    write(f"players/{slug(n)}.html", f"{n}: goals for Spain", f"{n} scored {len(gs)} goals for Spain. See every goal with match, date and competition.",
          f'<h1>{E(n)}</h1><div class="stats"><div class="stat"><b>{len(gs)}</b><span>Goals for Spain</span></div></div><table>' + ''.join(f'<tr><td><a href="/match/{m["id"]}.html">{dstr(m["date"])}</a></td><td>{E(title(m))}</td><td class="meta">{g["minute"]}\'</td></tr>' for m, g in reversed(gs)) + '</table>')
top = sorted(players.items(), key=lambda kv: -len(kv[1]))
write('players/index.html', 'Spain all-time top scorers', 'Spain national team all-time goalscorers ranked, from David Villa to the 2026 World Cup winners.',
      '<h1>Spain top scorers</h1><table>' + ''.join(f'<tr><td>{i}</td><td><a href="/players/{slug(n)}.html">{E(n)}</a></td><td class="s">{len(g)}</td></tr>' for i, (n, g) in enumerate(top[:100], 1)) + '</table>')
# home
last = P[-1]; nxt = next((m for m in M if not m['played']), None); allr = rec(P)
J = json.dumps([[m['id'], m['date'], m['opp'], m['label'], m['f'], m['a'], m['res'], 1 if m['pen'] else 0] for m in reversed(P)], ensure_ascii=False, separators=(',', ':'))
opts = ''.join(f'<option>{E(t)}</option>' for t, ms in sorted(tn.items(), key=lambda kv: -len(kv[1])))
home = f'''<h1>Every Spain match, ever.</h1><p class="meta">{len(P)} international matches since {P[0]['year']}. Search results, scorers and highlights.</p>{statbar(allr)}
<div class="card"><b>Latest:</b> <a href="/match/{last['id']}.html">{E(title(last))}</a> <span class="meta">· {E(last['label'])} · {dstr(last['date'])}</span></div>
{f'<div class="card"><b>Next:</b> <a href="/match/{nxt["id"]}.html">{E(title(nxt))}</a> <span class="meta">· {dstr(nxt["date"])}</span></div>' if nxt else ''}
<div class="filters"><input id="q" placeholder="Search opponent, year, tournament" aria-label="Search matches"><select id="r" aria-label="Result"><option value="">Any result</option><option value="W">Wins</option><option value="D">Draws</option><option value="L">Losses</option></select><select id="t" aria-label="Tournament"><option value="">All tournaments</option>{opts}</select></div>
<table id="out"></table><p><button class="btn" id="more">Show more</button></p>{kit}
<script>const D={J};let n=40,L=[];const q=document.getElementById('q'),r=document.getElementById('r'),t=document.getElementById('t'),o=document.getElementById('out'),b=document.getElementById('more');
const e=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
function draw(){{o.innerHTML=L.slice(0,n).map(m=>`<tr><td><span class="b ${{m[6]}}">${{m[6]}}</span></td><td><a href="/match/${{m[0]}}.html">${{m[1]}}</a></td><td>${{e(m[2])}}</td><td class="s">${{m[4]}}–${{m[5]}}</td><td class="meta">${{e(m[3])}}</td></tr>`).join('')||'<tr><td>No matches found</td></tr>';b.style.display=L.length>n?'':'none'}}
function run(){{const s=q.value.toLowerCase();n=40;L=D.filter(m=>(!s||(m[2]+' '+m[3]+' '+m[1]).toLowerCase().includes(s))&&(!r.value||m[6]===r.value)&&(!t.value||m[3].includes(t.value)));draw()}}
[q,r,t].forEach(x=>x.oninput=run);b.onclick=()=>{{n+=60;draw()}};run()</script>'''
write('index.html', 'Spain national team: every match, result and highlight', f'Search all {len(P)} Spain national team matches ever played: results, scorers, head-to-head records and highlights. 2026 World Cup champions.', home)
write('404.html', 'Page not found', 'Page not found', '<h1>Page not found</h1><p><a href="/">Search all Spain matches</a></p>')
shutil.copy(R + '/style.css', O + '/style.css')
open(O + '/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{cfg["url"]}/{p.replace("index.html","")}</loc></url>' for p in pages if p != '404.html') + '</urlset>')
open(O + '/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {cfg["url"]}/sitemap.xml\n')
print(f'{len(P)} played, {len(pages)} pages, {len(players)} players')
if cfg['amazon_tag'] == 'REPLACE-20': print('WARNING: set amazon_tag in config.json')
