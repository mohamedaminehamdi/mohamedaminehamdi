"""Builds assets/stack-sphere-{dark,light}.svg: a rotating 3D sphere of stack logos.

GitHub READMEs cannot run JavaScript, so the 3D rotation is precomputed into CSS keyframes
(icons) and SMIL path animations (wireframe meridians). Pure SVG, plays natively on GitHub.

Edit STACK below, then:  python3 scripts/build_sphere.py
Icons: tandpfun/skill-icons (MIT), vendored in scripts/icons/.
"""
import base64, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, 'scripts', 'icons')
OUT = os.path.join(ROOT, 'assets')

# Order matters a little: neighbours on the list end up near each other on the sphere.
STACK = [
    # platform and delivery
    'Kubernetes', 'Helm', 'ArgoCD', 'Docker', 'Harbor', 'Istio', 'Cilium', 'Traefik', 'Nginx',
    # infrastructure as code and secrets
    'Terraform', 'Ansible', 'Packer', 'Vault', 'AWS', 'Cloudflare', 'Linux', 'Bash',
    # CI/CD
    'GithubActions', 'GitLab', 'Jenkins', 'Git', 'Github',
    # security
    'Trivy', 'SonarQube', 'Snyk', 'OWASP', 'Falco', 'Keycloak', 'WireGuard',
    # observability
    'Prometheus', 'Grafana', 'OpenTelemetry', 'InfluxDB',
    # code and data
    'GoLang', 'Python', 'TypeScript', 'JavaScript', 'NodeJS', 'NestJS', 'NextJS', 'React',
    'PostgreSQL', 'MongoDB', 'TailwindCSS', 'Prisma', 'Supabase', 'Vercel',
]

W, H = 880, 540
CX, CY, R = W / 2, H / 2, 225       # sphere centre and radius (px)
ICON = 50                           # icon size at the front of the sphere
FRAMES = 72                         # keyframes per revolution
DUR = 30                            # seconds per revolution
TILT = math.radians(-18)            # axis tilt toward the viewer
THEMES = {
    'dark':  dict(wire='#30363d', glow='#ffa657', rim='#3d444d', sand=['#e8d2a8', '#d9b77e', '#c79b5b', '#f3e3c3']),
    'light': dict(wire='#d0d7de', glow='#953800', rim='#c4ccd5', sand=['#b8925a', '#9c7640', '#c9a66d', '#8a6634']),
}


def icon_uri(name, theme):
    for f in (f'{name}-{theme.capitalize()}.svg', f'{name}.svg'):
        p = os.path.join(ICONS, f)
        if os.path.exists(p):
            return 'data:image/svg+xml;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    raise SystemExit(f'missing icon {name}')


def fibonacci(n):
    pts, g = [], math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + .5) / n
        r = math.sqrt(1 - y * y)
        pts.append((math.cos(g * i) * r, y, math.sin(g * i) * r))
    return pts


def project(p, theta):
    x, y, z = p
    x, z = x * math.cos(theta) + z * math.sin(theta), -x * math.sin(theta) + z * math.cos(theta)   # spin around axis
    y, z = y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT)        # tilt toward viewer
    persp = 1 + 0.18 * z                                                                              # mild perspective
    return CX + R * x * persp, CY + R * y * persp, z


def build(theme):
    c = THEMES[theme]
    pts = fibonacci(len(STACK))
    css, back, front, defs = [], [], [], []
    for i, (name, p) in enumerate(zip(STACK, pts)):
        kb, kf = [], []
        for k in range(FRAMES + 1):
            theta = 2 * math.pi * k / FRAMES
            x, y, z = project(p, theta)
            s = 0.55 + 0.45 * (z + 1) / 2                     # size by depth
            o = 0.18 + 0.82 * ((z + 1) / 2) ** 1.4            # fade by depth
            pct = f'{100 * k / FRAMES:.3f}%'
            tf = f'transform:translate({x:.1f}px,{y:.1f}px) scale({s:.3f})'
            kb.append(f'{pct}{{{tf};opacity:{o if z < 0 else 0:.3f}}}')
            kf.append(f'{pct}{{{tf};opacity:{o if z >= 0 else 0:.3f}}}')
        css.append(f'@keyframes b{i}{{{"".join(kb)}}}@keyframes f{i}{{{"".join(kf)}}}'
                   f'.b{i}{{animation:b{i} {DUR}s linear infinite}}.f{i}{{animation:f{i} {DUR}s linear infinite}}')
        defs.append(f'<image id="i{i}" href="{icon_uri(name, theme)}" x="{-ICON / 2}" y="{-ICON / 2}" width="{ICON}" height="{ICON}"/>')
        back.append(f'<g class="b{i}"><use href="#i{i}"/></g>')
        front.append(f'<g class="f{i}"><use href="#i{i}"/></g>')

    # wireframe: latitude rings are invariant under the spin, meridians rotate (SMIL path morph)
    wire = [f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#halo)" stroke="{c["rim"]}" stroke-width="1.2"/>']
    for lat in (-60, -30, 0, 30, 60):
        a = math.radians(lat)
        ring = [project((math.cos(t) * math.cos(a), math.sin(a), math.sin(t) * math.cos(a)), 0) for t in
                [2 * math.pi * j / 72 for j in range(73)]]
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y, _ in ring)
        wire.append(f'<path d="{d}" fill="none" stroke="{c["wire"]}" stroke-width="1" opacity=".8"/>')
    for m in range(6):
        phi0 = math.pi * m / 6
        frames = []
        for k in range(FRAMES + 1):
            theta = 2 * math.pi * k / FRAMES
            arc = [project((math.cos(phi0) * math.cos(t), math.sin(t), math.sin(phi0) * math.cos(t)), theta)
                   for t in [math.pi * (j / 36 - .5) for j in range(37)]]
            frames.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y, _ in arc))
        wire.append(f'<path fill="none" stroke="{c["wire"]}" stroke-width="1" opacity=".8" d="{frames[0]}">'
                    f'<animate attributeName="d" dur="{DUR / 2}s" repeatCount="indefinite" values="{";".join(frames[:FRAMES // 2 + 1])}"/></path>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Rotating 3D sphere of my stack: {", ".join(STACK)}">'
            f'<defs><radialGradient id="halo" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="{c["glow"]}" stop-opacity=".10"/>'
            f'<stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/></radialGradient>{"".join(defs)}</defs>'
            f'<style>{"".join(css)}g[class]{{opacity:0}}'
            '@media (prefers-reduced-motion:reduce){g[class],path animate{animation-play-state:paused}}</style>'
            + ''.join(wire) + ''.join(back) + ''.join(front) + '</svg>')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for t in THEMES:
        svg = build(t)
        open(os.path.join(OUT, f'stack-sphere-{t}.svg'), 'w').write(svg)
        print(t, len(svg) // 1024, 'KB')


# ---------------------------------------------------------------------------- interactive page
LABELS = {'ArgoCD': 'Argo CD', 'GitLab': 'GitLab CI', 'SonarQube': 'SonarQube', 'InfluxDB': 'InfluxDB', 'GithubActions': 'GitHub Actions', 'GoLang': 'Go', 'NodeJS': 'Node.js', 'NextJS': 'Next.js', 'NestJS': 'NestJS',
          'TailwindCSS': 'Tailwind CSS', 'Github': 'GitHub', 'PostgreSQL': 'PostgreSQL', 'MongoDB': 'MongoDB', 'AWS': 'AWS'}


def build_interactive():
    """docs/index.html: real 3D, hover to enlarge, drag to spin. Served by GitHub Pages."""
    import json
    icons = [dict(name=LABELS.get(n, n), light=icon_uri(n, 'light'), dark=icon_uri(n, 'dark')) for n in STACK]
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Mohamed Amine Hamdi: stack</title>
<style>
:root{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);
--bg:#ffffff;--fg:#1f2328;--muted:#59636e;--tip:#1f2328;--tipfg:#ffffff;--glow:149,56,0;
--wire:#c4ccd5}
*,*::before,*::after{box-sizing:inherit}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d1117;--fg:#f0f6fc;--muted:#9198a1;--tip:#f0f6fc;--tipfg:#0d1117;--glow:255,166,87;
--wire:#3d444d}}
:root[data-theme="dark"]{--bg:#0d1117;--fg:#f0f6fc;--muted:#9198a1;--tip:#f0f6fc;--tipfg:#0d1117;--glow:255,166,87;--wire:#3d444d}
html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;user-select:none}
h1{font:600 18px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:0 0 4px;letter-spacing:.2px}
p.hint{margin:0 0 8px;color:var(--muted);font-size:13px}
#stage{position:relative;width:min(92vw,620px);aspect-ratio:1;touch-action:none;cursor:grab}
#stage.drag{cursor:grabbing}
canvas{position:absolute;inset:0;width:100%;height:100%}
.ico{position:absolute;left:0;top:0;width:52px;height:52px;margin:-26px 0 0 -26px;will-change:transform}
.ico .in{width:100%;height:100%;border-radius:14px;transition:transform .25s cubic-bezier(.2,.9,.3,1.3),filter .25s}
.ico img{width:100%;height:100%;display:block;pointer-events:none;-webkit-user-drag:none}
.ico:hover .in{transform:scale(1.9);filter:drop-shadow(0 8px 18px rgba(var(--glow),.45))}
.ico .tip{position:absolute;left:50%;top:-12px;transform:translate(-50%,-100%) scale(.9);opacity:0;pointer-events:none;
background:var(--tip);color:var(--tipfg);font:600 12px ui-monospace,Menlo,monospace;padding:4px 8px;border-radius:6px;white-space:nowrap;transition:.2s}
.ico:hover .tip{opacity:1;transform:translate(-50%,-180%) scale(1)}
a.back{margin-top:10px;color:var(--muted);font-size:13px;text-decoration:none}
a.back:hover{color:var(--fg)}
</style></head><body>
<h1>~/stack</h1><p class="hint">Hover a logo to enlarge it. Drag to spin.</p>
<div id="stage"><canvas id="wire"></canvas></div>
<a class="back" href="https://github.com/mohamedaminehamdi">github.com/mohamedaminehamdi</a>
<script>
const ICONS = ''' + json.dumps(icons) + ''';
(() => {
  const stage = document.getElementById('stage'), cv = document.getElementById("wire"), ctx = cv.getContext('2d');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const dark = () => { const t = document.documentElement.dataset.theme; return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; };
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  // icons on a Fibonacci sphere
  const g = Math.PI * (3 - Math.sqrt(5)), N = ICONS.length;
  const nodes = ICONS.map((ic, i) => {
    const y = 1 - 2 * (i + .5) / N, r = Math.sqrt(1 - y * y);
    const el = document.createElement('div'); el.className = 'ico';
    el.innerHTML = '<div class="in"><img alt=""></div><span class="tip"></span>';
    el.querySelector('img').alt = ic.name; el.querySelector('.tip').textContent = ic.name;
    el.addEventListener('pointerenter', () => hovering++); el.addEventListener('pointerleave', () => hovering--);
    stage.appendChild(el);
    return {x: Math.cos(g * i) * r, y, z: Math.sin(g * i) * r, el, ic};
  });
  const paint = () => { const d = dark(); nodes.forEach(n => n.el.querySelector('img').src = d ? n.ic.dark : n.ic.light); };
  paint(); matchMedia('(prefers-color-scheme: dark)').addEventListener('change', paint);
  // wireframe: latitude rings and meridians, sampled as 3D points
  const lines = [];
  for (const lat of [-60, -30, 0, 30, 60]) { const a = lat * Math.PI / 180, l = [];
    for (let j = 0; j <= 72; j++) { const t = j / 72 * Math.PI * 2; l.push({x: Math.cos(t) * Math.cos(a), y: Math.sin(a), z: Math.sin(t) * Math.cos(a)}); } lines.push(l); }
  for (let m = 0; m < 6; m++) { const p = m * Math.PI / 6, l = [];
    for (let j = 0; j <= 72; j++) { const t = j / 72 * Math.PI * 2; l.push({x: Math.cos(p) * Math.cos(t), y: Math.sin(t), z: Math.sin(p) * Math.cos(t)}); } lines.push(l); }
  // rotation state
  let yaw = 0, pitch = -0.32, vy = 0.0035, vp = 0, hovering = 0, dragging = false, lx = 0, ly = 0;
  const AUTO = reduce ? 0 : 0.0035;
  stage.addEventListener('pointerdown', e => { dragging = true; lx = e.clientX; ly = e.clientY; stage.setPointerCapture(e.pointerId); stage.classList.add('drag'); });
  stage.addEventListener('pointermove', e => { if (!dragging) return;
    const dx = e.clientX - lx, dy = e.clientY - ly; lx = e.clientX; ly = e.clientY;
    vy = dx * 0.006; vp = dy * 0.006; yaw += vy; pitch = Math.max(-1.3, Math.min(1.3, pitch + vp)); });
  const end = () => { dragging = false; stage.classList.remove('drag'); };
  stage.addEventListener('pointerup', end); stage.addEventListener('pointercancel', end);
  let W = 0, R = 0, dpr = 1;
  const resize = () => { const b = stage.getBoundingClientRect(); W = b.width; R = W * 0.40; dpr = devicePixelRatio || 1;
    cv.width = W * dpr; cv.height = W * dpr; };
  new ResizeObserver(resize).observe(stage); resize();
  const rot = (p, cy, sy, cp, sp) => { const x = p.x * cy + p.z * sy, z1 = -p.x * sy + p.z * cy; return [x, p.y * cp - z1 * sp, p.y * sp + z1 * cp]; };
  function frame() {
    if (!dragging) { const target = hovering ? 0 : AUTO; vy += (target - vy) * 0.04; vp *= 0.92; yaw += vy; pitch += vp; pitch += (-0.32 - pitch) * 0.01; }
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const c = W / 2;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, W);
    const glow = ctx.createRadialGradient(c, c * .9, 0, c, c, R * 1.1);
    glow.addColorStop(0, `rgba(${css('--glow')},.10)`); glow.addColorStop(1, `rgba(${css('--glow')},0)`);
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(c, c, R * 1.1, 0, 7); ctx.fill();
    ctx.lineWidth = 1; ctx.strokeStyle = css('--wire');
    for (const l of lines) for (let j = 1; j < l.length; j++) {
      const [x0, y0, z0] = rot(l[j - 1], cy, sy, cp, sp), [x1, y1, z1] = rot(l[j], cy, sy, cp, sp);
      ctx.globalAlpha = .15 + .55 * ((z0 + z1) / 2 + 1) / 2;
      ctx.beginPath(); ctx.moveTo(c + R * x0 * (1 + .18 * z0), c + R * y0 * (1 + .18 * z0)); ctx.lineTo(c + R * x1 * (1 + .18 * z1), c + R * y1 * (1 + .18 * z1)); ctx.stroke();
    }
    ctx.globalAlpha = 1;
    for (const n of nodes) {
      const [x, y, z] = rot(n, cy, sy, cp, sp), k = 1 + .18 * z, d = (z + 1) / 2;
      const s = (.5 + .5 * d) * (W / 620);
      n.el.style.transform = `translate(${c + R * x * k}px,${c + R * y * k}px) scale(${s.toFixed(3)})`;
      n.el.style.opacity = (.15 + .85 * Math.pow(d, 1.3)).toFixed(3);
      n.el.style.zIndex = Math.round(d * 1000);
      n.el.style.pointerEvents = z > -0.2 ? 'auto' : 'none';
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
</script></body></html>'''


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    open(os.path.join(ROOT, 'docs', 'index.html'), 'w').write(build_interactive())
    print('interactive page: docs/index.html')
