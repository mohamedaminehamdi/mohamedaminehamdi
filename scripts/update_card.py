"""Builds the neofetch-style profile card (dark_mode.svg, light_mode.svg).

Run locally:    python3 scripts/update_card.py
In Actions:     GITHUB_TOKEN is set, so live stats are fetched from the GraphQL API.
"""
import base64, html, json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = 'mohamedaminehamdi'

# ----------------------------------------------------------------- content
# Edit these lines freely. Keys and values are aligned with dots automatically.
SPECS = [
    ('OS', 'Linux, Kubernetes, AWS'),
    ('Host', 'EcoG, Munich, Germany'),
    ('Kernel', 'DevSecOps Engineer'),
    ('Packages', 'kubectl, helm, argocd, trivy'),
    ('Shell', 'bash, kubectl, terraform'),
    None,
    ('Languages.Programming', 'Go, Python, TypeScript'),
    ('Languages.Infra', 'HCL, YAML, Bash'),
    None,
    ('Focus.Platform', 'Kubernetes, containers'),
    ('Focus.Security', 'secure access, hardening'),
    ('Focus.Automation', 'Terraform, Ansible, CI/CD'),
    None,
    ('Previously', 'Decentral AI, CTO Colocqui'),
    ('Speaker', 'AWS Community Day DACH'),
    ('Open.To', 'freelance and contract work'),
]
CONTACT = [
    ('LinkedIn', 'mohamed-amine-hamdi'),
    ('Medium', '@mohamedaminehamdi'),
    ('DEV', '@mohamedaminehamdi'),
    ('X', '@aminehamdibarca'),
]
# Used when no GITHUB_TOKEN is available (local runs). Actions overwrite these.
FALLBACK = dict(repos=46, stars=17, followers=16, contributions=3176, contributed=0)

# ----------------------------------------------------------------- layout
FS, LH, CW = 16, 20, 9.6          # font size, line height, monospace char width
AFS, ALH, ACW = 12, 14, 7.2       # ASCII portrait: smaller type for more detail
ASCII_X, COLS = 15, 56            # text columns on the right
THEMES = {
    'dark':  dict(bg='#161b22', text='#c9d1d9', key='#ffa657', value='#a5d6ff', cc='#616e7f', accent='#3fb950'),
    'light': dict(bg='#f6f8fa', text='#24292f', key='#953800', value='#0a3069', cc='#c2cfde', accent='#1a7f37'),
}


def fetch_stats():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        return FALLBACK
    q = '''query($login:String!){ user(login:$login){
      followers{totalCount}
      repositories(ownerAffiliations:OWNER, first:100, privacy:PUBLIC){ totalCount nodes{ stargazerCount } }
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY], first:1){ totalCount }
      contributionsCollection{ contributionCalendar{ totalContributions } } } }'''
    req = urllib.request.Request('https://api.github.com/graphql',
                                 data=json.dumps({'query': q, 'variables': {'login': USER}}).encode(),
                                 headers={'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    try:
        u = json.load(urllib.request.urlopen(req, timeout=30))['data']['user']
        return dict(repos=u['repositories']['totalCount'],
                    stars=sum(n['stargazerCount'] for n in u['repositories']['nodes']),
                    followers=u['followers']['totalCount'],
                    contributions=u['contributionsCollection']['contributionCalendar']['totalContributions'],
                    contributed=u['repositoriesContributedTo']['totalCount'])
    except Exception as e:  # keep the card valid even if the API hiccups
        print('stats fetch failed, using fallback:', e)
        return FALLBACK


def e(s):
    return html.escape(s, quote=False)


def kv(key, value, width=COLS):
    """'. Key: ...... value' padded to width, as tspans."""
    dots = width - len(key) - len(value) - 6
    dots = max(dots, 1)
    return (f'<tspan class="cc">. </tspan><tspan class="key">{e(key)}</tspan>:'
            f'<tspan class="cc"> {"." * dots} </tspan><tspan class="value">{e(value)}</tspan>')


def kv_pair(k1, v1, k2, v2, half=27):
    """Two key/value pairs on one line, separated by a bar."""
    d1 = max(half - len(k1) - len(v1) - 6, 1)
    d2 = max(COLS - half - 3 - len(k2) - len(v2) - 4, 1)
    return (f'<tspan class="cc">. </tspan><tspan class="key">{e(k1)}</tspan>:<tspan class="cc"> {"." * d1} </tspan>'
            f'<tspan class="value">{e(v1)}</tspan> | <tspan class="key">{e(k2)}</tspan>:'
            f'<tspan class="cc"> {"." * d2} </tspan><tspan class="value">{e(v2)}</tspan>')


def header(title):
    return f'<tspan class="title">{e(title)}</tspan> ' + '-' * (COLS - len(title) - 1)


def section(name):
    return f'- {e(name)} ' + '-' * (COLS - len(name) - 3)


PROMPT = 'mohamed@hamdi:~$ '
WHOAMI = 'Mohamed Amine Hamdi, DevSecOps Engineer at EcoG'
HIRE_ME = ['Open to freelance and contract work.', 'Say hi on LinkedIn: mohamed-amine-hamdi']
# Scenes typed after neofetch. Each scene starts with `clear`.
# Each entry: (command, output lines); a line is a list of (text, colour) segments.
# Colours: text, key (orange), value (blue), cc (dim), accent (green).
ok, dim, val, txt, key = 'accent', 'cc', 'value', 'text', 'key'
SCENES = [
    [   # who I am
        ('kubectl get pods -n mohamed', [
            [('NAME                          READY   STATUS    RESTARTS   AGE', dim)],
            [('platform-engineering-7d9f     ', val), ('1/1     ', txt), ('Running   ', ok), ('0          4y', txt)],
            [('security-hardening-5c2b       ', val), ('1/1     ', txt), ('Running   ', ok), ('0          4y', txt)],
            [('iac-automation-8f1a           ', val), ('1/1     ', txt), ('Running   ', ok), ('0          4y', txt)],
            [('fullstack-sidequests-2e7c     ', val), ('1/1     ', txt), ('Running   ', ok), ('0          2y', txt)],
            [('coffee-sidecar-9a4d           ', val), ('1/1     ', txt), ('Running   ', ok), ('12         4y', txt)],
        ]),
        ('kubectl get certifications', [
            [('NAME                        ISSUER      STATUS', dim)],
            [('ccna-1-2                    ', val), ('Cisco       ', txt), ('Certified', ok)],
            [('machine-learning            ', val), ('Stanford    ', txt), ('Completed', ok)],
        ]),
        ('git log --oneline', [
            [('3f9c2e1 ', key), ('feat: DevSecOps Engineer at EcoG, Munich', txt)],
            [('b71d0a4 ', key), ('feat: DevSecOps Engineer at Decentral AI', txt)],
            [('9e2c5f8 ', key), ('feat: CTO at Colocqui', txt)],
            [('41ab7d3 ', key), ('chore: President, INSAT Junior Enterprise', txt)],
            [('c0ffee1 ', key), ('init: ICT Engineering, INSAT', txt)],
        ]),
        ('cat talks.txt', [
            [('AWS Community Day DACH', val)],
        ]),
    ],
    [   # what I ship
        ('argocd app list', [
            [('NAME                       SYNC STATUS   HEALTH STATUS', dim)],
            [('firecrawl/firecrawl        ', val), ('Synced        ', ok), ('Healthy', ok)],
            [('kubernetes/kubernetes      ', val), ('Synced        ', ok), ('Healthy', ok)],
            [('backstage/backstage        ', val), ('Synced        ', ok), ('Healthy', ok)],
            [('netbirdio/netbird          ', val), ('Synced        ', ok), ('Healthy', ok)],
            [('Tracer-Cloud/opensre       ', val), ('Synced        ', ok), ('Healthy', ok)],
            [('kubernetes/website         ', val), ('Synced        ', ok), ('Healthy', ok)],
        ]),
        ('terraform plan', [
            [('  # engineer.mohamed will be created', dim)],
            [('  + ', ok), ('resource "engineer" "mohamed" {', txt)],
            [('      + ', ok), ('role    ', key), ('= ', txt), ('"DevSecOps Engineer"', val)],
            [('      + ', ok), ('stack   ', key), ('= ', txt), ('["kubernetes", "terraform", "aws"]', val)],
            [('      + ', ok), ('open_to ', key), ('= ', txt), ('"freelance and contract work"', val)],
            [('    }', txt)],
            [('Plan: ', txt), ('1 to add', ok), (', 0 to change, 0 to destroy.', txt)],
        ]),
        ('ansible fleet -m ping', [
            [('fleet | SUCCESS => {"changed": false, "ping": "pong"}', ok)],
        ]),
    ],
    [   # security mindset, then contact
        ('kubectl get secrets -n mohamed', [
            [('Error from server (Forbidden): ', 'key'), ('least privilege applies here too', txt)],
        ]),
        ('kubectl auth can-i ship --to=production', [
            [('yes', ok)],
        ]),
        ('trivy image mohamed:latest', [
            [('mohamed:latest (hardened)', txt)],
            [('Total: 0 ', ok), ('(UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0)', dim)],
        ]),
        ('ssh -J bastion mohamed@field-device-042', [
            [('Connected through a hardened bridge. ', txt), ('Session audited.', ok)],
        ]),
        ('wg show wg0', [
            [('peer: ', key), ('recruiter', val), ('   latest handshake: ', txt), ('just now', ok)],
        ]),
        ('terraform output', [
            [('linkedin ', key), ('= ', txt), ('"mohamed-amine-hamdi"', val)],
            [('medium   ', key), ('= ', txt), ('"@mohamedaminehamdi"', val)],
            [('dev      ', key), ('= ', txt), ('"@mohamedaminehamdi"', val)],
            [('x        ', key), ('= ', txt), ('"@aminehamdibarca"', val)],
        ]),
        ('./hire-me.sh', [
            [('Open to freelance and contract work.', txt)],
            [('Say hi on LinkedIn: ', txt), ('mohamed-amine-hamdi', val)],
        ]),
    ],
]
TYPE = 0.11       # seconds per typed character
PRINT = 0.07      # seconds between printed output lines
HOLD = 9.0        # seconds the finished screen stays up before the session replays
AFTER_CMD = 1.4   # pause after a command's output before the next command
READ = 4.0        # time to read a full screen before `clear`


def build(theme, stats, ascii_lines):
    """A short terminal session: commands are typed, answers print line by line (SMIL, plays on load)."""
    c = THEMES[theme]
    info = [header('mohamed@hamdi')]
    for item in SPECS:
        if item and item[0] == 'Open.To':
            continue                                   # answered by ./hire-me.sh instead
        info.append('' if item is None else kv(*item))
    info += ['', section('Contact')] + [kv(k, v) for k, v in CONTACT]
    info += ['', section('GitHub Stats'),
             kv_pair('Repos', f'{stats["repos"]}', 'Stars', f'{stats["stars"]}'),
             kv_pair('Followers', f'{stats["followers"]}', 'Contributions', f'{stats["contributions"]:,}')]

    asc_w = max(len(l) for l in ascii_lines)
    rx = ASCII_X + asc_w * ACW + 26
    W = int(rx + COLS * CW + 18)
    block_h = max(len(info) * LH, len(ascii_lines) * ALH)
    row = lambda r: 30 + r * LH
    # rows: whoami, answer, neofetch, [block], blank, hire-me, 2 answers, blank, prompt
    y_block = row(3) - 14
    after = y_block + block_h + 14
    H = int(after + 7 * LH)

    fonts = ''.join(
        f"@font-face{{font-family:'JBM';font-weight:{w};src:url(data:font/woff2;base64,"
        f"{base64.b64encode(open(os.path.join(ROOT, 'scripts', 'fonts', f'jetbrains-mono-latin-{w}-normal.woff2'), 'rb').read()).decode()}) format('woff2')}}"
        for w in (400, 800))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="JBM,Consolas,monospace" font-size="{FS}px" role="img" '
           f'aria-label="Terminal session. whoami: {WHOAMI}. neofetch: Linux, Kubernetes, AWS. Certifications: CCNA, Stanford Machine Learning. Repos: firecrawl/firecrawl, kubernetes/kubernetes, backstage/backstage, netbirdio/netbird, Tracer-Cloud/opensre, kubernetes/website. Experience: EcoG, Decentral AI, CTO at Colocqui, President of INSAT Junior Enterprise. Talk: AWS Community Day DACH. {HIRE_ME[0]}">',
           f'<style>{fonts}text,tspan{{white-space:pre;font-variant-ligatures:none;font-feature-settings:\'liga\' 0,\'calt\' 0}}'
           f'.key{{fill:{c["key"]}}}.value{{fill:{c["value"]}}}.cc{{fill:{c["cc"]}}}.title{{font-weight:800;fill:{c["accent"]}}}</style>',
           f'<rect width="{W}" height="{H}" fill="{c["bg"]}" rx="15"/>']
    t = 0.5
    uid = [0]
    head = len(out)

    def appear(at):
        # hidden at the start of every cycle, shown at its moment in the session
        return (f'<set attributeName="opacity" to="0" begin="clk.begin" fill="freeze"/>'
                f'<set attributeName="opacity" to="1" begin="clk.begin+{at:.2f}s" fill="freeze"/>')

    def prompt_markup():
        return (f'<tspan font-weight="800" fill="{c["accent"]}">mohamed@hamdi</tspan><tspan fill="{c["cc"]}">:</tspan>'
                f'<tspan fill="{c["value"]}">~</tspan><tspan fill="{c["text"]}">$ </tspan>')

    def command(y, cmd):
        nonlocal t
        out.append(f'<text x="{ASCII_X}" y="{y}" opacity="0">{appear(t)}{prompt_markup()}</text>')
        x0 = ASCII_X + len(PROMPT) * CW
        start, n = t + 0.7, len(cmd)
        steps = ';'.join(f'{(k * CW * 1.03 + 4) if k < n else (n * CW + 60):.1f}' if k else '0' for k in range(n + 1))
        uid[0] += 1; cid = f'c{uid[0]}'
        out.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y - 16}" width="0" height="22">'
                   f'<set attributeName="width" to="0" begin="clk.begin" fill="freeze"/>'
                   f'<animate attributeName="width" values="{steps}" calcMode="discrete" begin="clk.begin+{start:.2f}s" dur="{n * TYPE:.2f}s" fill="freeze"/></rect></clipPath>')
        out.append(f'<text x="{x0}" y="{y}" fill="{c["text"]}" clip-path="url(#{cid})">{e(cmd)}</text>')
        xs = ';'.join(f'{x0 + k * CW * 1.03:.1f}' for k in range(n + 1))
        out.append(f'<rect y="{y - 14}" width="{CW:.1f}" height="17" fill="{c["accent"]}" opacity="0" x="{x0}">'
                   f'<set attributeName="opacity" to="1" begin="clk.begin+{t:.2f}s" dur="{start + n * TYPE + 0.25 - t:.2f}s"/>'
                   f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="clk.begin+{start:.2f}s" dur="{n * TYPE:.2f}s" fill="freeze"/>'
                   '</rect>')
        t = start + n * TYPE + 0.6

    def output(x, y, markup, plain=False, size=None):
        nonlocal t
        fs = f' font-size="{size}px"' if size else ''
        body = e(markup) if plain else markup
        out.append(f'<text x="{x:.1f}" y="{y:.1f}"{fs} fill="{c["text"]}" opacity="0">{appear(t)}{body}</text>')

    # 1) whoami
    command(row(0), 'whoami')
    output(ASCII_X, row(1), WHOAMI, plain=True); t += AFTER_CMD
    # 2) neofetch: portrait and info print together, top to bottom
    command(row(2), 'neofetch')
    t0 = t
    ay = y_block + (block_h - len(ascii_lines) * ALH) / 2 + ALH * 0.75
    for i, line in enumerate(ascii_lines):
        t = t0 + i * 0.05
        output(ASCII_X, ay + i * ALH, line, plain=True, size=AFS)
    for j, line in enumerate(info):
        t = t0 + j * PRINT
        if line:
            output(rx, y_block + 14 + j * LH, line)
    t = t0 + max(len(ascii_lines) * 0.05, len(info) * PRINT) + 0.8
    # 3) each scene: pause to read, type `clear`, wipe the screen, run the scene's commands
    seg = head
    clear_y = after + LH
    for scene in SCENES:
        t += READ
        command(clear_y, 'clear')
        t_clear = t + 0.15
        shown = out[seg:]
        del out[seg:]
        out.append(f'<g><set attributeName="opacity" to="1" begin="clk.begin" fill="freeze"/>'
                   f'<set attributeName="opacity" to="0" begin="clk.begin+{t_clear:.2f}s" fill="freeze"/>' + ''.join(shown) + '</g>')
        seg = len(out)
        t = t_clear + 0.3
        r = 0
        for cmd, lines in scene:
            command(row(r), cmd); r += 1
            for segs in lines:
                body = ''.join(f'<tspan fill="{c[col]}">{e(tx)}</tspan>' for tx, col in segs)
                out.append(f'<text x="{ASCII_X}" y="{row(r)}" opacity="0">{appear(t)}{body}</text>')
                t += PRINT * 1.6; r += 1
            r += 1; t += AFTER_CMD
        clear_y = row(r)
    # 4) idle prompt with a blinking cursor
    t += 0.4
    yp = clear_y
    out.append(f'<text x="{ASCII_X}" y="{yp}" opacity="0">{appear(t)}{prompt_markup()}</text>')
    out.append(f'<rect x="{ASCII_X + len(PROMPT) * CW:.1f}" y="{yp - 14}" width="{CW:.1f}" height="17" fill="{c["accent"]}" opacity="0">'
               f'<animate attributeName="opacity" values="1;0" dur="1.1s" calcMode="discrete" begin="clk.begin+{t:.2f}s" repeatDur="{HOLD:.2f}s"/></rect>')
    # master clock: one cycle = the session plus a pause on the finished screen, then it all restarts
    out.insert(3, f'<rect width="0" height="0"><animate id="clk" attributeName="x" from="0" to="0" dur="{t + HOLD:.2f}s" begin="0s;clk.end"/></rect>')
    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    stats = fetch_stats()
    for theme in THEMES:
        art = open(os.path.join(ROOT, 'scripts', f'ascii_{theme}.txt')).read().split('\n')
        while art and not art[-1].strip():
            art.pop()
        with open(os.path.join(ROOT, f'{theme}_mode.svg'), 'w') as f:
            f.write(build(theme, stats, art))
    print('card built with', stats)
