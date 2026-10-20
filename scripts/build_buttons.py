"""Builds the social buttons in assets/buttons/ (light and dark), styled to match the profile.

Edit LINKS, then:  pip install fonttools brotli && python3 scripts/build_buttons.py
"""
import base64, html, io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from build_projects import FONTS, FD, width
from fontTools.ttLib import TTFont
from fontTools import subset

# name, handle shown, url, brand colour, simple-icons path (24x24)
LINKS = [
    ('LinkedIn', 'mohamed-amine-hamdi', 'https://www.linkedin.com/in/mohamed-amine-hamdi/', '#0A66C2',
     'M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'),
    ('Medium', '@mohamedaminehamdi', 'https://medium.com/@mohamedaminehamdi', 'mono', None),
    ('DEV', '@mohamedaminehamdi', 'https://dev.to/mohamedaminehamdi', 'mono', None),
    ('X', '@baryouchahamdi', 'https://x.com/baryouchahamdi', 'mono', None),
]
SI = {'Medium': 'medium', 'DEV': 'devdotto', 'X': 'x'}
THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#f0f6fc', muted='#8b949e', mono_bg='#f0f6fc', mono_fg='#0d1117', arrow='#ffa657'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#1f2328', muted='#59636e', mono_bg='#1f2328', mono_fg='#ffffff', arrow='#953800'),
}
W, H = 224, 58


def si_path(slug):
    import re
    return re.search(r'<path d="([^"]+)"', open(os.path.join(ROOT, 'scripts', 'icons', f'si-{slug}.svg')).read()).group(1)


def button(name, handle, color, path, theme):
    c = THEMES[theme]; used = {}
    bg, fg = (c['mono_bg'], c['mono_fg']) if color == 'mono' else (color, '#ffffff')
    path = path or si_path(SI[name])
    els = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>',
           f'<rect x="12" y="12" width="34" height="34" rx="9" fill="{bg}"/>',
           f'<g transform="translate(19 19) scale(.8333)"><path fill="{fg}" d="{path}"/></g>']

    def text(x, y, s, font, size, fill):
        used.setdefault(font, set()).update(s)
        els.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}">{html.escape(s)}</text>')
    text(58, 27, name, 'Inter6', 15, c['title'])
    size = 11.5
    while width('Mono4', handle, size) > W - 58 - 30:
        size -= .5
    text(58, 44, handle, 'Mono4', size, c['muted'])
    els.append(f'<path d="M{W - 24} {H / 2 - 5} l5 5 -5 5" fill="none" stroke="{c["arrow"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    faces = []
    for fname, chars in used.items():
        o = subset.Options(); o.flavor = 'woff2'
        f = TTFont(os.path.join(FD, FONTS[fname])); sb = subset.Subsetter(o)
        sb.populate(text=''.join(chars) + ' '); sb.subset(f)
        b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
        faces.append(f"@font-face{{font-family:'{fname}';src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format('woff2')}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{name} {html.escape(handle)}"><style>{"".join(faces)}</style>' + ''.join(els) + '</svg>')


def readme_block():
    cells = []
    for name, handle, url, *_ in LINKS:
        slug = name.lower()
        cells.append(f'<a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/buttons/{slug}-dark.svg">'
                     f'<img src="assets/buttons/{slug}-light.svg" width="23.5%" alt="{name} {html.escape(handle)}"></picture></a>')
    return '<p align="center">\n  ' + '\n  '.join(cells) + '\n</p>'


if __name__ == '__main__':
    out = os.path.join(ROOT, 'assets', 'buttons'); os.makedirs(out, exist_ok=True)
    for name, handle, url, color, path in LINKS:
        for t in THEMES:
            open(os.path.join(out, f'{name.lower()}-{t}.svg'), 'w').write(button(name, handle, color, path, t))
    print(readme_block())
