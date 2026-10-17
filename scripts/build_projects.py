"""Builds the featured project cards in assets/projects/ (light and dark).

Edit PROJECTS below, then run:  pip install fonttools brotli && python3 scripts/build_projects.py
"""
import base64, html, io, os
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, 'scripts', 'fonts')
OUT = os.path.join(ROOT, 'assets', 'projects')

PROJECTS = [
    dict(slug='job-hunter', lang='Python', color='#3572A5', stars=11, kind='AI tooling',
         desc='Skills for Claude Code, Codex and Cursor. Paste a job link, get your CV scored and rewritten for it, the people to reach out to, and the message to send.',
         tags=['claude-code', 'codex', 'cursor']),
    dict(slug='infra-genie', lang='Python', color='#3572A5', stars=0, kind='Cloud cost',
         desc='Scans every AWS region in parallel for unused resources and removes them safely, with dry-run mode, confirmations and an audit trail.',
         tags=['aws', 'finops', 'cli']),
    dict(slug='three-tier-devsecops-project', title='three-tier-devsecops', lang='Python', color='#3572A5', stars=0, kind='Platform',
         desc='A three-tier app on AWS EKS, provisioned with Terraform, shipped by Jenkins with Trivy and SonarQube gates, deployed by Argo CD, watched by Prometheus.',
         tags=['eks', 'argocd', 'trivy']),
    dict(slug='the-localhost-times', lang='HTML', color='#e34c26', stars=0, kind='Local-first AI',
         desc='A private morning newspaper and audio briefing from your inbox, calendar and news, written on your own machine by Gemma 4.',
         tags=['local-first', 'llm', 'privacy']),
    dict(slug='divergence', lang='Python', color='#3572A5', stars=0, kind='Search',
         desc='Scores a website twice, once for Google and once for AI answer engines, and shows exactly where the two disagree.',
         tags=['seo', 'ai-search', 'audit']),
    dict(slug='leaf-and-gill', lang='Python', color='#3572A5', stars=0, kind='On-device AI',
         desc='Identifies wild plants, trees and mushrooms fully offline, anywhere, with the open BioCLIP 2 model running on your phone.',
         tags=['bioclip', 'offline', 'mobile']),
]

THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#ffa657', text='#c9d1d9', muted='#8b949e',
                  chip='#a5d6ff', chipbg='#1f3048', kind='#3fb950'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#953800', text='#24292f', muted='#59636e',
                  chip='#0a3069', chipbg='#ddf4ff', kind='#1a7f37'),
}
FONTS = {'Mono8': 'jetbrains-mono-latin-800-normal.woff2', 'Mono4': 'jetbrains-mono-latin-400-normal.woff2',
         'Inter4': 'inter-latin-400-normal.woff2', 'Inter6': 'inter-latin-600-normal.woff2'}
TT = {k: TTFont(os.path.join(FD, v)) for k, v in FONTS.items()}
W, H = 440, 170


def width(font, s, size):
    t = TT[font]; cm = t.getBestCmap(); hm = t['hmtx']; upm = t['head'].unitsPerEm
    return sum(hm[cm[ord(c)]][0] if ord(c) in cm else upm * .55 for c in s) * size / upm


def wrap(font, s, size, w):
    lines, cur = [], ''
    for word in s.split():
        t = (cur + ' ' + word).strip()
        if width(font, t, size) <= w or not cur:
            cur = t
        else:
            lines.append(cur); cur = word
    return lines + [cur] if cur else lines


def card(p, theme):
    c = THEMES[theme]; used = {}
    els = []

    def text(x, y, s, font, size, fill, anchor='start'):
        used.setdefault(font, set()).update(s)
        els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{fill}" '
                   f'text-anchor="{anchor}">{html.escape(s)}</text>')

    els.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>')
    # header: folder glyph + path
    els.append(f'<path d="M20 22h7l2 2.5h9a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H20a1.5 1.5 0 0 1-1.5-1.5v-11.5A1.5 1.5 0 0 1 20 22z" '
               f'fill="none" stroke="{c["muted"]}" stroke-width="1.4"/>')
    title = p.get('title', p['slug'])
    size = 17
    while width('Mono8', '~/' + title, size) > W - 170:
        size -= 0.5
    text(48, 36, '~/' + title, 'Mono8', size, c['title'])
    text(W - 18, 36, p['kind'], 'Inter6', 12, c['kind'], 'end')
    y = 66
    for ln in wrap('Inter4', p['desc'], 13.5, W - 40)[:4]:
        text(20, y, ln, 'Inter4', 13.5, c['text']); y += 20
    # footer: language, stars, tags
    fy = H - 22
    els.append(f'<circle cx="26" cy="{fy - 4.5}" r="5.5" fill="{p["color"]}"/>')
    text(37, fy, p['lang'], 'Inter4', 12.5, c['muted'])
    x = 37 + width('Inter4', p['lang'], 12.5) + 16
    if p['stars']:
        els.append(f'<path transform="translate({x} {fy - 11.5}) scale(.8)" fill="{c["muted"]}" d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>')
        text(x + 16, fy, str(p['stars']), 'Inter4', 12.5, c['muted'])
    tx = W - 18
    for tag in reversed(p['tags']):
        tw = width('Mono4', tag, 11) + 16
        tx -= tw
        els.append(f'<rect x="{tx:.1f}" y="{fy - 15}" width="{tw:.1f}" height="21" rx="10.5" fill="{c["chipbg"]}"/>')
        text(tx + tw / 2, fy - 0.5, tag, 'Mono4', 11, c['chip'], 'middle')
        tx -= 6
    faces = []
    for name, chars in used.items():
        o = subset.Options(); o.flavor = 'woff2'; o.layout_features = ['kern']
        f = TTFont(os.path.join(FD, FONTS[name])); sb = subset.Subsetter(o)
        sb.populate(text=''.join(chars) + ' '); sb.subset(f)
        b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
        faces.append(f"@font-face{{font-family:'{name}';src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format('woff2')}}")
    alt = html.escape(f'{title}: {p["desc"]}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">'
            f'<style>{"".join(faces)}text{{font-variant-ligatures:none}}</style>' + ''.join(els) + '</svg>')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for p in PROJECTS:
        for t in THEMES:
            open(os.path.join(OUT, f'{p["slug"]}-{t}.svg'), 'w').write(card(p, t))
    print(len(PROJECTS), 'project cards built')
