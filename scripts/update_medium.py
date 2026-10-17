"""Reads the Medium RSS feed and renders the latest article as a card, plus a short list.

Writes assets/medium-latest-{dark,light}.svg and rewrites README.md between
<!-- MEDIUM:START --> and <!-- MEDIUM:END -->.

Run:  pip install fonttools brotli pillow && python3 scripts/update_medium.py
Test with a saved feed:  MEDIUM_FEED_FILE=feed.xml python3 scripts/update_medium.py
"""
import base64, html, io, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = '@mohamedaminehamdi'
FEED = f'https://medium.com/feed/{USER}'
PROFILE = f'https://medium.com/{USER}'
MORE = 3                     # how many older articles to list under the card
UA = {'User-Agent': 'Mozilla/5.0 (profile-readme; +https://github.com/mohamedaminehamdi)'}

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_projects import TT, FONTS, FD, width, wrap  # shared fonts and text measuring
from fontTools.ttLib import TTFont
from fontTools import subset

THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#f0f6fc', text='#c9d1d9', muted='#8b949e',
                  label='#ffa657', chip='#a5d6ff', chipbg='#1f3048', ph='#21262d'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#1f2328', text='#24292f', muted='#59636e',
                  label='#953800', chip='#0a3069', chipbg='#ddf4ff', ph='#e6eaef'),
}
NS = {'content': 'http://purl.org/rss/1.0/modules/content/', 'dc': 'http://purl.org/dc/elements/1.1/'}
W, H, IW = 880, 236, 300     # card size and cover width


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def read_feed():
    raw = open(os.environ['MEDIUM_FEED_FILE'], 'rb').read() if os.environ.get('MEDIUM_FEED_FILE') else fetch(FEED)
    items = []
    for it in ET.fromstring(raw).iter('item'):
        body = it.findtext('content:encoded', default='', namespaces=NS)
        img = re.search(r'<img[^>]+src="([^"]+)"', body)
        text = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))).strip()
        title = html.unescape(it.findtext('title', '').strip())
        if text.lower().startswith(title.lower()):      # Medium repeats the title as the first heading
            text = text[len(title):].lstrip(' :.-')
        items.append(dict(title=title,
                          link=it.findtext('link', '').split('?')[0],
                          date=parsedate_to_datetime(it.findtext('pubDate')),
                          tags=[c.text for c in it.findall('category')][:3],
                          image=img.group(1) if img else None,
                          excerpt=text,
                          minutes=max(1, round(len(text.split()) / 230))))
    return items


def cover(url):
    """Download, crop to the card's cover shape, return a JPEG data URI (or None)."""
    if not url:
        return None
    try:
        from PIL import Image
        if url.startswith('file://'):
            im = Image.open(url[7:])
        else:
            im = Image.open(io.BytesIO(fetch(url)))
        im = im.convert('RGB'); tw, th = IW * 2, H * 2
        s = max(tw / im.width, th / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        l, t = (im.width - tw) // 2, (im.height - th) // 2
        im = im.crop((l, t, l + tw, t + th))
        b = io.BytesIO(); im.save(b, 'JPEG', quality=78, optimize=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    except Exception as e:
        print('cover image skipped:', e)
        return None


def card(a, theme, img):
    c = THEMES[theme]; used = {}; els = []

    def text(x, y, s, font, size, fill, extra=''):
        used.setdefault(font, set()).update(s)
        els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{fill}" {extra}>{html.escape(s)}</text>')

    els.append(f'<clipPath id="cl"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12"/></clipPath>')
    els.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{c["bg"]}"/>')
    if img:
        els.append(f'<image href="{img}" x="0" y="0" width="{IW}" height="{H}" preserveAspectRatio="xMidYMid slice" clip-path="url(#cl)"/>')
    else:   # no cover in the post: Medium-style placeholder
        els.append(f'<rect x="0" y="0" width="{IW}" height="{H}" fill="{c["ph"]}" clip-path="url(#cl)"/>')
        for k, cx in enumerate((IW / 2 - 52, IW / 2 + 12, IW / 2 + 52)):
            rx = (34, 17, 6)[k]
            els.append(f'<ellipse cx="{cx}" cy="{H / 2}" rx="{rx}" ry="34" fill="{c["muted"]}" opacity=".55"/>')
    els.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{c["border"]}"/>')
    x0, tw = IW + 28, W - IW - 56
    # Medium mark + label
    els.append(f'<g transform="translate({x0} 26)"><ellipse cx="6" cy="8" rx="6" ry="7" fill="{c["label"]}"/>'
               f'<ellipse cx="15.5" cy="8" rx="3" ry="6.6" fill="{c["label"]}"/><ellipse cx="20.5" cy="8" rx="1.1" ry="6" fill="{c["label"]}"/></g>')
    text(x0 + 30, 39, 'Latest on Medium', 'Inter6', 13, c['label'])
    y = 74
    for ln in wrap('Inter6', a['title'], 22, tw)[:2]:
        text(x0, y, ln, 'Inter6', 22, c['title']); y += 29
    y += 4
    ex = wrap('Inter4', a['excerpt'], 14, tw)
    for i, ln in enumerate(ex[:2]):
        if i == 1 and len(ex) > 2:
            while width('Inter4', ln + '...', 14) > tw and ' ' in ln:
                ln = ln.rsplit(' ', 1)[0]
            ln += '...'
        text(x0, y, ln, 'Inter4', 14, c['text']); y += 21
    fy = H - 26
    meta = f'{a["date"]:%b %-d, %Y}  |  {a["minutes"]} min read'
    text(x0, fy, meta, 'Inter4', 13, c['muted'])
    tx = W - 28
    for tag in reversed(a['tags'][:3]):
        w = width('Mono4', tag, 11) + 16
        if tx - w < x0 + width('Inter4', meta, 13) + 12:
            break
        tx -= w
        els.append(f'<rect x="{tx:.1f}" y="{fy - 15}" width="{w:.1f}" height="21" rx="10.5" fill="{c["chipbg"]}"/>')
        text(tx + w / 2, fy - .5, tag, 'Mono4', 11, c['chip'], 'text-anchor="middle"')
        tx -= 6
    faces = []
    for name, chars in used.items():
        o = subset.Options(); o.flavor = 'woff2'
        f = TTFont(os.path.join(FD, FONTS[name])); sb = subset.Subsetter(o)
        sb.populate(text=''.join(chars) + ' '); sb.subset(f)
        b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
        faces.append(f"@font-face{{font-family:'{name}';src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format('woff2')}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{html.escape("Latest on Medium: " + a["title"])}"><style>{"".join(faces)}text{{font-variant-ligatures:none}}</style>'
            + ''.join(els) + '</svg>')


def section(items):
    a = items[0]
    lines = [f'<a href="{a["link"]}"><picture>',
             '  <source media="(prefers-color-scheme: dark)" srcset="assets/medium-latest-dark.svg">',
             f'  <img src="assets/medium-latest-light.svg" width="100%" alt="{html.escape("Latest on Medium: " + a["title"])}">',
             '</picture></a>', '']
    if len(items) > 1:
        lines += [f'- [{b["title"]}]({b["link"]}) <sub>{b["date"]:%b %-d, %Y}</sub>' for b in items[1:1 + MORE]]
        lines.append('')
    lines.append(f'<sub><a href="{PROFILE}">All articles on Medium</a></sub>')
    return '\n'.join(lines)


if __name__ == '__main__':
    try:
        items = read_feed()
    except Exception as e:
        print('feed unavailable, keeping the current card:', e); sys.exit(0)
    if not items:
        print('no articles in the feed yet'); sys.exit(0)
    img = cover(items[0]['image'])
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    for t in THEMES:
        open(os.path.join(ROOT, 'assets', f'medium-latest-{t}.svg'), 'w').write(card(items[0], t, img))
    p = os.path.join(ROOT, 'README.md'); s = open(p).read()
    s = re.sub(r'<!-- MEDIUM:START -->.*?<!-- MEDIUM:END -->',
               lambda m: '<!-- MEDIUM:START -->\n' + section(items) + '\n<!-- MEDIUM:END -->', s, flags=re.S)
    open(p, 'w').write(s)
    print('latest article:', items[0]['title'])
