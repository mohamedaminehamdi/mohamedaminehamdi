"""Builds the "Contributions in the last 31 days" graph (assets/activity-dark.svg, activity-light.svg).

Run locally:    GITHUB_TOKEN=$(gh auth token) python3 scripts/build_activity.py
In Actions:     GITHUB_TOKEN is set by the workflow.
"""
import datetime as dt, html, json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = 'mohamedaminehamdi'
DAYS = 31
W, H = 900, 300
PAD_L, PAD_R, PAD_T, PAD_B = 52, 28, 62, 44
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#ffa657', text='#c9d1d9', grid='#30363d', line='#3fb950', point='#ffa657'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#953800', text='#24292f', grid='#d0d7de', line='#1a7f37', point='#953800'),
}


def fetch_days():
    now = dt.datetime.now(dt.timezone.utc)
    start = (now - dt.timedelta(days=DAYS - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    q = '''query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
      contributionsCollection(from:$from,to:$to){ contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }'''
    req = urllib.request.Request('https://api.github.com/graphql',
                                 data=json.dumps({'query': q, 'variables': {'login': USER, 'from': start.isoformat(), 'to': now.isoformat()}}).encode(),
                                 headers={'Authorization': f'bearer {os.environ["GITHUB_TOKEN"]}', 'Content-Type': 'application/json'})
    weeks = json.load(urllib.request.urlopen(req, timeout=30))['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    days = sorted((d['date'], d['contributionCount']) for w in weeks for d in w['contributionDays'])
    return days[-DAYS:]


def build(theme, days):
    c = THEMES[theme]
    top = max(4, -(-max(n for _, n in days) // 4) * 4)       # round the axis up to a multiple of 4
    pw, ph = W - PAD_L - PAD_R, H - PAD_T - PAD_B
    px = lambda i: PAD_L + pw * i / (len(days) - 1)
    py = lambda n: PAD_T + ph * (1 - n / top)
    pts = [(px(i), py(n)) for i, (_, n) in enumerate(days)]
    line = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" '
           f'aria-label="Contributions per day over the last {DAYS} days, {sum(n for _, n in days)} in total">',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="{c["bg"]}" stroke="{c["border"]}"/>',
           f'<text x="{PAD_L - 28}" y="34" font-size="18" font-weight="600" fill="{c["title"]}">Contributions in the last {DAYS} days</text>',
           f'<text x="{W - PAD_R}" y="34" font-size="13" text-anchor="end" fill="{c["text"]}">{sum(n for _, n in days)} total</text>']
    for k in range(5):                                         # horizontal grid and y labels
        v = top * k // 4
        out.append(f'<line x1="{PAD_L}" x2="{W - PAD_R}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{c["grid"]}" stroke-dasharray="3 4"/>')
        out.append(f'<text x="{PAD_L - 10}" y="{py(v) + 4:.1f}" font-size="11" text-anchor="end" fill="{c["text"]}">{v}</text>')
    for i in range(0, len(days), 5):                           # x labels every fifth day
        label = dt.date.fromisoformat(days[i][0]).strftime('%b %-d')
        out.append(f'<text x="{px(i):.1f}" y="{H - 16}" font-size="11" text-anchor="middle" fill="{c["text"]}">{html.escape(label)}</text>')
    out.append(f'<polygon points="{px(0):.1f},{py(0):.1f} {line} {px(len(days) - 1):.1f},{py(0):.1f}" fill="{c["line"]}" fill-opacity="0.22"/>')
    out.append(f'<polyline points="{line}" fill="none" stroke="{c["line"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    out += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{c["point"]}"><title>{days[i][0]}: {days[i][1]}</title></circle>' for i, (x, y) in enumerate(pts)]
    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    days = fetch_days()
    for theme in THEMES:
        with open(os.path.join(ROOT, 'assets', f'activity-{theme}.svg'), 'w') as f:
            f.write(build(theme, days))
    print(f'activity graph built: {len(days)} days, {sum(n for _, n in days)} contributions')
