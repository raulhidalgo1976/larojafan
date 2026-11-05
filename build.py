#!/usr/bin/env python3
"""LaRojaFan static site builder: every Spain match ever -> SEO pages. Run: python3 build.py"""
import csv, json, re, html, os, shutil, unicodedata
from collections import defaultdict
from datetime import date, datetime, timezone
from urllib.parse import quote_plus
R = os.path.dirname(os.path.abspath(__file__)); D = R + '/data'; O = R + '/docs'
cfg = json.load(open(R + '/config.json')); HL = json.load(open(R + '/highlights.json'))
PHOTOS = json.load(open(R + '/player_photos.json'))
MATCH_STATS = json.load(open(R + '/match_stats.json'))
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
def aff(q):
    tag = cfg.get('amazon_tag', '').strip()
    if not tag or tag == 'REPLACE-20': return None
    return f"https://www.amazon.com/s?k={quote_plus(q)}&tag={quote_plus(tag)}"
def badge(m): return f'<span class="b {m["res"]}">{m["res"]}</span>' if m['played'] else '<span class="b D">–</span>'

pages = []
def write(path, t, desc, body, schema=None):
    pages.append(path); head = cfg['url'].rstrip('/') + '/' + path.replace('index.html', '')
    ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={cfg["adsense_id"]}" crossorigin="anonymous"></script>' if cfg['adsense_id'] else ''
    analytics = '<script defer src="/analytics.js"></script>' if cfg.get('ga4_measurement_id') else ''
    ld = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")}</script>' if schema else ''
    out = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(t)} | LaRojaFan</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{head}">
<meta property="og:title" content="{E(t)}"><meta property="og:url" content="{E(head)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website"><link rel="stylesheet" href="/style.css">{ld}{ads}{analytics}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="/">LA<b>ROJA</b>FAN</a><nav aria-label="Main navigation"><a href="/">All matches</a><a href="/players/">Players</a><a href="/tournaments/">Tournaments</a><a href="/about/">About</a></nav></div></header>
<main class="wrap">{body}</main><footer><div class="wrap">LaRojaFan.com is an independent fan site. Historical match data is sourced from a community-maintained dataset and may be incomplete. <a href="/about/">About &amp; sources</a> · <a href="/privacy/">Privacy &amp; cookies</a> · <button type="button" id="cookie-settings" class="cookie-settings">Cookie settings</button>. As an Amazon Associate I earn from qualifying purchases when you use qualifying Amazon links.</div></footer></body></html>'''
    os.makedirs(os.path.dirname(f'{O}/{path}'), exist_ok=True); open(f'{O}/{path}', 'w', encoding='utf-8').write(out)

def table(ms):
    return '<table>' + ''.join(f'<tr><td>{badge(m)}</td><td><a href="/match/{m["id"]}.html">{dstr(m["date"])}</a></td><td>{E(m["opp"])}</td><td class="s">{score(m)}</td><td class="meta">{E(m["label"])}</td></tr>' for m in reversed(ms)) + '</table>'
def statbar(r): return '<div class="stats">' + ''.join(f'<div class="stat"><b>{v}</b><span>{k}</span></div>' for k, v in [('Played', r['p']), ('Won', r['w']), ('Drawn', r['d']), ('Lost', r['l']), ('Goals for', r['gf']), ('Goals against', r['ga'])]) + '</div>'
def gear(m):
    url = aff('Spain national football team jersey')
    if not url or not cfg.get('enable_generic_affiliate_links', False): return ''
    return f'<div class="card"><b>Spain supporter gear</b><p class="meta">Browse national-team shirts and fan merchandise. Availability and authenticity vary by seller.</p><a class="btn" rel="sponsored nofollow noopener" href="{E(url, quote=True)}">Browse fan gear</a> <span class="aff">Paid affiliate link</span></div>'

kit = f'<div class="card"><b>Never miss a match</b><p class="meta">Free match alerts and results straight to your inbox.</p><script async data-uid="{cfg["kit_uid"]}" src="{cfg["kit_src"]}"></script></div>' if cfg['kit_uid'] and cfg['kit_src'] else ''

# players
players = defaultdict(list)
for m in P:
    for g in m['goals']:
        if g['team'] == 'Spain' and g['own_goal'] != 'TRUE': players[g['scorer']].append((m, g))
def player_photo(name, compact=False):
    """Render only explicitly approved image metadata; never guess image licenses."""
    item = PHOTOS.get(slug(name))
    if not item or not all(item.get(k) for k in ('url','source_url','license','credit')):
        return '<div class="player-placeholder" role="img" aria-label="Player photo unavailable">' + E(name[:1].upper()) + '</div>'
    url = item['url']
    if not url.startswith('https://') or not item['source_url'].startswith('https://'):
        return '<div class="player-placeholder" role="img" aria-label="Player photo unavailable">' + E(name[:1].upper()) + '</div>'
    img = f'<img class="player-photo" loading="lazy" src="{E(url,quote=True)}" alt="{E(name,quote=True)}" referrerpolicy="no-referrer">'
    if compact: return img
    return img + f'<p class="meta photo-credit">Photo: {E(item["credit"])} · {E(item["license"])} · <a href="{E(item["source_url"],quote=True)}" rel="noopener noreferrer">Image source and license</a></p>'

def match_statistics(m):
    """Distinguish missing measurements from zero; only publish sourced values."""
    if not m['played']: return ''
    key = m['id']; item = MATCH_STATS.get(key, {})
    valid = bool(item.get('source_url','').startswith('https://') and item.get('source_name'))
    labels = [('possession','Possession (%)'),('shots','Shots'),('shots_on_target','Shots on target'),('corners','Corners'),('fouls','Fouls')]
    rows=[]
    if valid:
        for k,label in labels:
            v=item.get(k)
            if isinstance(v,dict) and isinstance(v.get('spain'),(int,float)) and isinstance(v.get('opponent'),(int,float)):
                rows.append(f'<tr><td>{v["spain"]}</td><th scope="row">{label}</th><td>{v["opponent"]}</td></tr>')
    if rows:
        content='<table class="match-stats"><thead><tr><th>Spain</th><th>Statistic</th><th>'+E(m['opp'])+'</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
        content+=f'<p class="meta">Statistics source: <a href="{E(item["source_url"],quote=True)}" rel="noopener noreferrer">{E(item["source_name"])}</a></p>'
    else:
        content='<p class="meta">Detailed possession, shots, corners and foul statistics have not yet been verified for this match. Unavailable values are not zero.</p>'
    return '<section class="card"><h2>Match statistics</h2>'+content+'</section>'

# match pages
for m in P + [x for x in M if not x['played']]:
    vs = [x for x in P if x['opp'] == m['opp']]; r = rec(vs) if vs else None
    gl = ''.join(f'<li>{(f"<a href=/players/{slug(g[chr(115)+chr(99)+chr(111)+chr(114)+chr(101)+chr(114)])}.html>{E(g[chr(115)+chr(99)+chr(111)+chr(114)+chr(101)+chr(114)])}</a>" if g["team"]=="Spain" and g["own_goal"]!="TRUE" else E(g["scorer"]))} {g["minute"]}\'{" (pen.)" if g["penalty"]=="TRUE" else ""}{" (o.g.)" if g["own_goal"]=="TRUE" else ""} <span class="meta">{E(g["team"])}{(" · assist: "+E(g["assist"])) if g["assist"] not in ("NA","") else ""}</span></li>' for g in m['goals'])
    vid = f'<div class="vid"><iframe src="https://www.youtube-nocookie.com/embed/{HL[m["hkey"]]}" title="{E(title(m))} highlights" allowfullscreen loading="lazy"></iframe></div>' if m['hkey'] in HL else f'<a class="btn" href="https://www.youtube.com/results?search_query={quote_plus(f"Spain {m[chr(111)+chr(112)+chr(112)]} {m[chr(121)+chr(101)+chr(97)+chr(114)]} highlights")}" rel="nofollow">Find highlights on YouTube</a>'
    outcome = {'W': 'Spain won', 'D': 'Spain drew', 'L': 'Spain lost'}.get(m['res'], 'Upcoming')
    if m['pen']: outcome += f' ({m["pen"]} won on penalties)'
    body = f'<h1>{E(title(m))}</h1><p class="meta">{E(m["label"])} · {dstr(m["date"])} · {E(m["city"])}, {E(m["country"])}</p>'
    body += (f'<div class="card"><b>{outcome}</b>{"<ul>"+gl+"</ul>" if gl else "<p class=meta>Scorer details not available for this match.</p>"}</div>' if m['played'] else '<div class="card"><b>Upcoming fixture</b><p class="meta">Check back after the final whistle for the result, scorers and highlights.</p></div>')
    body += match_statistics(m)
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
    write(f"players/{slug(n)}.html", f"{n}: documented Spain goals", f"Browse {len(gs)} documented goals by {n} in our match-event dataset. This is not a verified international career total.",
          f'<h1>{E(n)}</h1><div class="player-profile">{player_photo(n)}</div><div class="stats"><div class="stat"><b>{len(gs)}</b><span>Goals in dataset</span></div></div><table>' + ''.join(f'<tr><td><a href="/match/{m["id"]}.html">{dstr(m["date"])}</a></td><td>{E(title(m))}</td><td class="meta">{g["minute"]}\'</td></tr>' for m, g in reversed(gs)) + '</table>')
top = sorted(players.items(), key=lambda kv: -len(kv[1]))
write('players/index.html', 'Spain goalscorer records in our dataset', 'Explore Spain goals recorded in our historical match-event dataset; counts are not verified career totals.',
      '<h1>Spain goals recorded in our dataset</h1><p class="meta">These counts reflect available event records, not verified all-time international career totals. Historical scorer coverage is incomplete.</p><table>' + ''.join(f'<tr><td>{i}</td><td><div class="player-list-name">{player_photo(n, True)} <a href="/players/{slug(n)}.html">{E(n)}</a></div></td><td class="s">{len(g)}</td></tr>' for i, (n, g) in enumerate(top[:100], 1)) + '</table>')
# home
last = P[-1]; nxt = next((m for m in M if not m['played']), None); allr = rec(P)
J = json.dumps([[m['id'], m['date'], m['opp'], m['label'], m['f'], m['a'], m['res'], 1 if m['pen'] else 0] for m in reversed(P)], ensure_ascii=False, separators=(',', ':'))
opts = ''.join(f'<option>{E(t)}</option>' for t, ms in sorted(tn.items(), key=lambda kv: -len(kv[1])))
home = f'''<h1>Spain national team match archive</h1><p class="meta">{len(P)} matches in our dataset since {P[0]['year']}. Explore results, scorers where available, and highlights.</p>{statbar(allr)}
<div class="card"><b>Latest:</b> <a href="/match/{last['id']}.html">{E(title(last))}</a> <span class="meta">· {E(last['label'])} · {dstr(last['date'])}</span></div>
{f'<div class="card"><b>Next:</b> <a href="/match/{nxt["id"]}.html">{E(title(nxt))}</a> <span class="meta">· {dstr(nxt["date"])}</span></div>' if nxt else ''}
<div class="filters"><input id="q" placeholder="Search opponent, year, tournament" aria-label="Search matches"><select id="r" aria-label="Result"><option value="">Any result</option><option value="W">Wins</option><option value="D">Draws</option><option value="L">Losses</option></select><select id="t" aria-label="Tournament"><option value="">All tournaments</option>{opts}</select></div>
<table id="out" aria-label="Spain match results">{table(P[-20:])}</table><p><button class="btn" id="more">Show more</button></p>{kit}
<script>const D={J};let n=40,L=[];const q=document.getElementById('q'),r=document.getElementById('r'),t=document.getElementById('t'),o=document.getElementById('out'),b=document.getElementById('more');
const e=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
function draw(){{o.innerHTML=L.slice(0,n).map(m=>`<tr><td><span class="b ${{m[6]}}">${{m[6]}}</span></td><td><a href="/match/${{m[0]}}.html">${{m[1]}}</a></td><td>${{e(m[2])}}</td><td class="s">${{m[4]}}–${{m[5]}}</td><td class="meta">${{e(m[3])}}</td></tr>`).join('')||'<tr><td>No matches found</td></tr>';b.style.display=L.length>n?'':'none'}}
function run(){{const s=q.value.toLowerCase();n=40;L=D.filter(m=>(!s||(m[2]+' '+m[3]+' '+m[1]).toLowerCase().includes(s))&&(!r.value||m[6]===r.value)&&(!t.value||m[3].includes(t.value)));draw()}}
[q,r,t].forEach(x=>x.oninput=run);b.onclick=()=>{{n+=60;draw()}};run()</script>'''
write('index.html', 'Spain national team match archive', f'Explore {len(P)} Spain matches in our historical dataset: results, scorers where available, head-to-head records and highlights.', home)
write('about/index.html', 'About LaRojaFan and data sources', 'Learn about the LaRojaFan match archive, sources, data limitations and corrections.', '<h1>About LaRojaFan</h1><p>LaRojaFan is an independent, unofficial archive of Spain national football team matches and records.</p><h2>Data sources and limitations</h2><p>Match results and scorer events are built from the community-maintained <a href="https://github.com/martj42/international_results" rel="noopener">international_results dataset</a>. Historical coverage, event details and future fixtures may be incomplete or inaccurate. Goals in our dataset must not be interpreted as verified career totals.</p><h2>Corrections</h2><p>For corrections, please contact the site operator through the project repository. Official records should be verified with the RFEF, FIFA or UEFA.</p><h2>Affiliate disclosure</h2><p>Some outbound shopping links may be affiliate links. We may receive a commission if you make a qualifying purchase, at no additional cost to you.</p>')
write('privacy/index.html', 'Privacy and cookies', 'Privacy and analytics choices for LaRojaFan.', '<h1>Privacy and cookies</h1><p>LaRojaFan is an independent static football website hosted using GitHub Pages. Hosting providers may process technical request information necessary to deliver the site.</p><h2>Optional analytics</h2><p>With your permission, this site uses Google Analytics 4 to measure page views, visitor engagement and outbound links. Google may process device and usage information and set analytics cookies. Analytics does not load unless you accept optional analytics. You can withdraw your choice using Cookie settings in the footer.</p><h2>External services and affiliate links</h2><p>Following links to other sites, including YouTube and Amazon, subjects you to their own privacy practices. Some links may be affiliate links. As an Amazon Associate I earn from qualifying purchases.</p><h2>Contact and further information</h2><p>For questions about this website or requests relating to personal data, please contact the site operator through the <a href="https://github.com/raulhidalgo1976/larojafan/issues" rel="noopener noreferrer">project issue tracker</a>. Google Analytics retention and your rights are also described in the <a href="https://policies.google.com/privacy" rel="noopener noreferrer">Google Privacy Policy</a>. This policy was last updated November 4, 2026.</p>')
write('404.html', 'Page not found', 'Page not found', '<h1>Page not found</h1><p><a href="/">Search all Spain matches</a></p>')
shutil.copy(R + '/style.css', O + '/style.css')
analytics_js = open(R + '/analytics.js', encoding='utf-8').read().replace('__GA4_MEASUREMENT_ID__', cfg.get('ga4_measurement_id', '')).replace('__AMAZON_TAG__', cfg.get('amazon_tag', ''))
open(O + '/analytics.js', 'w', encoding='utf-8').write(analytics_js)
open(O + '/sitemap.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{cfg["url"]}/{p.replace("index.html","")}</loc></url>' for p in pages if p != '404.html') + '</urlset>')
open(O + '/robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {cfg["url"]}/sitemap.xml\n')
print(f'{len(P)} played, {len(pages)} pages, {len(players)} players')
if cfg['amazon_tag'] == 'REPLACE-20': print('WARNING: set amazon_tag in config.json')
