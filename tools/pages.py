"""Live HTML pages for the animations (self-contained: SVG inline, the code-rain font embedded).

Each page plays on its own; ?capture=1 hides the controls and exposes renderAt(ms) for frame capture,
&bg=transparent drops the background, &color=<key> and &variant=<icon|wordmark> pick a version.

    python3 pages.py OUT_DIR      (after anim.py)
"""
import base64
import re
import sys
from pathlib import Path

import anim as A

CSS = '''
  :root { --bg: #000000; --fg: #e6efec; --muted: #759495; --line: #22302f; --chip: #0d1414; }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: var(--bg); color: var(--fg);
    font: 14px/1.4 "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif; }
  body.light { --bg: #ffffff; --fg: #101615; --muted: #5d6f6f; --line: #cfd8d7; --chip: #f2f5f5; }
  .stage { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; overflow: hidden; }
  .label { position: fixed; left: 16px; top: 12px; color: var(--muted); font-size: 13px; letter-spacing: 0.04em; }
  .bar { position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%); display: flex; flex-wrap: wrap;
    gap: 8px; align-items: center; justify-content: center; width: max-content; max-width: calc(100vw - 32px); }
  .bar button, .bar a { font: inherit; color: var(--fg); background: var(--chip); border: 1px solid var(--line);
    border-radius: 6px; padding: 6px 12px; cursor: pointer; text-decoration: none; }
  .bar button[aria-pressed="true"] { border-color: var(--fg); }
  .bar .sep { width: 1px; height: 22px; background: var(--line); }
  .bar .swatch { width: 26px; height: 26px; padding: 0; border-radius: 50%; }
  body.capture .bar, body.capture .label { display: none; }
  html.clear, html.clear body { background: transparent; }
'''


def page(title, label, stage, controls, script, extra_css=''):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{CSS}{extra_css}</style>
</head>
<body>
<div class="label">{label}</div>
<div class="stage">{stage}</div>
<div class="bar">{controls}</div>
<script>
const q = new URLSearchParams(location.search);
if (q.has('capture')) document.body.classList.add('capture');
if (q.get('bg') === 'transparent') document.documentElement.classList.add('clear');
function press(group, button) {{
  document.querySelectorAll('[data-group="' + group + '"]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
}}
document.querySelectorAll('[data-bg]').forEach((b) => b.addEventListener('click', () => {{
  document.body.classList.toggle('light', b.dataset.bg === 'white'); press('bg', b);
}}));
{script}
</script>
</body>
</html>
'''


BG_CHIPS = ('<span class="sep"></span><button data-group="bg" data-bg="black" aria-pressed="true">검정 배경</button>'
            '<button data-group="bg" data-bg="white" aria-pressed="false">흰 배경</button>')


def full_window(svg):
    """As StartupIntro.tsx does: the artwork may fly past its 1280 x 480 artboard."""
    svg = re.sub(r'^<\?xml[^>]*>\s*', '', svg)
    svg = svg.replace('overflow="hidden"', 'overflow="visible"').replace('clip-path="url(#viewport-clip)"', '')
    return svg.replace('<svg ', '<svg class="anim intro" ', 1)


def transition(svg, title, other_href, other_label):
    css = '''
  .intro { width: min(1280px, 90vw, 240dvh); height: auto; aspect-ratio: 1280 / 480; overflow: visible; cursor: pointer; }
  body.capture .intro { width: 1280px; }
  html.clear #background { display: none; }'''
    controls = ('<button id="replay">다시 재생</button>'
                '<button id="loop" aria-pressed="false">반복 재생</button><span class="sep"></span>'
                '<button data-group="colour" data-colour="white" aria-pressed="true">X 흰색</button>'
                '<button data-group="colour" data-colour="green" aria-pressed="false">X 초록</button>'
                f'<span class="sep"></span><a href="{other_href}">{other_label}</a>')
    script = '''
const svg = document.querySelector('svg.anim');
const DUR = 2.6;
let loop = false;
function replay() { svg.setCurrentTime(0); svg.unpauseAnimations(); }
document.getElementById('replay').addEventListener('click', replay);
svg.addEventListener('click', replay);
document.getElementById('loop').addEventListener('click', (e) => {
  loop = !loop; e.currentTarget.setAttribute('aria-pressed', String(loop));
  if (loop && svg.getCurrentTime() >= DUR) replay();
});
setInterval(() => { if (loop && svg.getCurrentTime() >= DUR + 1.2) replay(); }, 100);
const mono = svg.querySelector('#monogram');
function paint(key) { mono.setAttribute('fill', key === 'green' ? '#00db89' : '#ffffff'); }
document.querySelectorAll('[data-colour]').forEach((b) => b.addEventListener('click', () => { paint(b.dataset.colour); press('colour', b); }));
if (q.get('color')) paint(q.get('color'));
window.renderAt = (ms) => { svg.pauseAnimations(); svg.setCurrentTime(ms / 1000); };
if (q.has('capture')) svg.pauseAnimations();
'''
    return page(title, title + ' · 2.6초 · 클릭하면 다시 재생', full_window(svg), controls, script, css)


def chips(colours, default):
    return ''.join(f'<button class="swatch" data-group="colour" data-colour="{k}" title="{name}" aria-label="{name}" '
                   f'aria-pressed="{str(k == default).lower()}" style="background:{fill}"></button>'
                   for k, (name, fill) in colours.items())


def loader(svgs, title, label, colours, default, script_colour, variants=None, extra_css=''):
    css = '''
  .stage svg { display: block; width: min(56vmin, 420px); height: auto; overflow: visible; }
  .stage svg.wide { width: min(86vw, 960px); }
  .stage svg[hidden] { display: none; }
  body.capture .stage svg { width: 100vmin; }
  body.capture .stage svg.wide { width: 1280px; }''' + extra_css
    controls = ''
    if variants:
        controls += ''.join(f'<button data-group="variant" data-variant="{k}" aria-pressed="{str(i == 0).lower()}">{name}</button>'
                            for i, (k, name) in enumerate(variants.items())) + '<span class="sep"></span>'
    controls += chips(colours, default) + BG_CHIPS
    script = '''
const svgs = [...document.querySelectorAll('svg.anim')];
''' + script_colour + '''
document.querySelectorAll('[data-colour]').forEach((b) => b.addEventListener('click', () => { paint(b.dataset.colour); press('colour', b); }));
document.querySelectorAll('[data-variant]').forEach((b) => b.addEventListener('click', () => {
  svgs.forEach((s) => { s.hidden = s.dataset.variant !== b.dataset.variant; }); press('variant', b);
}));
if (q.get('variant')) svgs.forEach((s) => { s.hidden = s.dataset.variant !== q.get('variant'); });
if (q.get('color')) paint(q.get('color'));
window.renderAt = (ms) => svgs.forEach((s) => { s.pauseAnimations(); s.setCurrentTime(ms / 1000); });
if (q.has('capture')) svgs.forEach((s) => s.pauseAnimations());
'''
    return page(title, label, ''.join(svgs), controls, script, css)


def inline(svg, variant='icon', wide=False, hidden=False):
    cls = 'anim wide' if wide else 'anim'
    return svg.replace('<svg ', f'<svg class="{cls}" data-variant="{variant}"{" hidden" if hidden else ""} ', 1)


def rain_page():
    font = base64.b64encode(A.MONO_WOFF2.read_bytes()).decode()
    left = A.G['steerix_left']
    css = f'''
  @font-face {{ font-family: "IBM Plex Mono"; src: url(data:font/woff2;base64,{font}) format("woff2"); font-weight: 400; }}
  canvas {{ display: block; width: min(56vmin, 420px); height: auto; aspect-ratio: 1; }}
  body.capture canvas {{ width: 100vmin; }}'''
    script = '''
// Port of web/src/brand/steerix.ts + SteerixMotion.tsx (motion "rain"), drawn in the original 320 px space,
// without the outline.
const LOOP = 1800, SIZE = 320;
const LEFT = ''' + str(left) + ''';
const RIGHT = LEFT.map(([x, y]) => [160 - x, 160 - y]);
const ALPHABET = '01ABCDEF{}[]<>/\\\\|+-=*:#';
const clamp01 = (v) => Math.max(0, Math.min(1, v));
function bezier(time, x1, y1, x2, y2, iterations = 28) {
  const x = clamp01(time);
  if (x === 0 || x === 1) return x;
  let low = 0, high = 1, u = x;
  for (let i = 0; i < iterations; i++) {
    u = (low + high) / 2;
    const v = 1 - u;
    if (3 * v * v * u * x1 + 3 * v * u * u * x2 + u * u * u < x) low = u; else high = u;
  }
  return 3 * (1 - u) * (1 - u) * u * y1 + 3 * (1 - u) * u * u * y2 + u * u * u;
}
function sample(ms) {
  const progress = (Number.isFinite(ms) && ms > 0 ? ms : 0) % LOOP / LOOP;
  const dock = progress < 0.26 ? 7 * bezier(progress / 0.26, 0.4, 0, 0.2, 1)
    : progress <= 0.72 ? 7 : 7 * (1 - bezier((progress - 0.72) / 0.28, 0.4, 0, 0.2, 1));
  const angle = progress <= 0.26 ? 0 : progress >= 0.72 ? 360 : 360 * bezier(clamp01((progress - 0.26) / 0.46), 0.65, 0, 0.35, 1);
  return { progress, left: dock, right: -dock || 0, angle };
}
function polygons(frame, size) {
  const a = frame.angle * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
  return [LEFT, RIGHT].map((poly, i) => poly.map(([x, y]) => {
    const cx = x + (i ? frame.right : frame.left) - 80, cy = y - 80;
    return [(cx * c - cy * s + 80) * size / 160, (cx * s + cy * c + 80) * size / 160];
  }));
}
function contains([x, y], polygon) {
  let inside = false, previous = polygon[polygon.length - 1];
  for (const point of polygon) {
    if ((point[1] > y) !== (previous[1] > y)
      && x < (previous[0] - point[0]) * (y - point[1]) / (previous[1] - point[1]) + point[0]) inside = !inside;
    previous = point;
  }
  return inside;
}
function columnHash(column) {
  let value = 260811 ^ Math.imul(column, 0x9e3779b9);
  value ^= value >>> 16; value = Math.imul(value, 0x7feb352d);
  value ^= value >>> 15; value = Math.imul(value, 0x846ca68b);
  return (value ^ (value >>> 16)) >>> 0;
}
function glyphs(size, frame, polys) {
  const glyphSize = Math.max(8, Math.min(18, size / 16));
  const width = glyphSize * 0.72, height = glyphSize * 1.05, phase = Math.floor(frame.progress * 30), out = [];
  for (let column = 0; column < Math.max(1, Math.floor(size / width)); column++) {
    const hash = columnHash(column), columnPhase = (hash & 0xffff) / 65535;
    const cycles = 1 + ((hash >>> 16) % 3), length = 12 + ((hash >>> 20) % 11);
    const period = size + length * height, head = ((columnPhase + cycles * frame.progress) % 1) * period, x = column * width;
    for (let trail = 0; trail < length; trail++) {
      for (const wrap of [-period, 0, period]) {
        const y = head - trail * height + wrap, point = [x + glyphSize * 0.35, y + glyphSize * 0.5];
        if (y < -glyphSize || y >= size || !polys.some((p) => contains(point, p))) continue;
        const index = ((hash >>> 8) % ALPHABET.length + column * 5 + trail * 7 + phase) % ALPHABET.length;
        const strength = 1 - trail / Math.max(1, length - 1);
        const r = trail === 0 ? 210 : Math.trunc(4 + 26 * strength ** 1.6);
        const g = trail === 0 ? 255 : Math.trunc(70 + 185 * strength ** 0.85);
        const b = trail === 0 ? 222 : Math.trunc(12 + 60 * strength ** 1.1);
        out.push({ x, y, glyph: ALPHABET[index] ?? '0', color: `rgb(${r}, ${g}, ${b})` });
      }
    }
  }
  return { glyphSize, glyphs: out };
}
const canvas = document.querySelector('canvas'), ctx = canvas.getContext('2d');
function draw(ms) {
  const px = Math.round(canvas.getBoundingClientRect().width * (window.devicePixelRatio || 1));
  if (canvas.width !== px) { canvas.width = px; canvas.height = px; }
  const k = px / SIZE;
  ctx.setTransform(k, 0, 0, k, 0, 0);
  ctx.clearRect(0, 0, SIZE, SIZE);
  const frame = sample(ms), polys = polygons(frame, SIZE);
  const paths = polys.map((pts) => { const p = new Path2D(); pts.forEach(([x, y], i) => i ? p.lineTo(x, y) : p.moveTo(x, y)); p.closePath(); return p; });
  ctx.fillStyle = '#001e0a';
  paths.forEach((p) => ctx.fill(p));
  const { glyphSize, glyphs: list } = glyphs(SIZE, frame, polys);
  ctx.font = `${glyphSize}px "IBM Plex Mono", monospace`;
  ctx.textBaseline = 'top';
  for (const g of list) { ctx.fillStyle = g.color; ctx.fillText(g.glyph, g.x, g.y); }
}
let start = null, running = !q.has('capture');
function tick(now) { if (!running) return; if (start === null) start = now; draw(now - start); requestAnimationFrame(tick); }
document.fonts.load('18px "IBM Plex Mono"').then(() => { draw(0); if (running) requestAnimationFrame(tick); });
window.renderAt = (ms) => { running = false; draw(ms); };
'''
    return page('STEERIX 코드비 로딩', 'STEERIX 로딩 · 코드비 · 1.8초 반복 (앱 첫 로딩 화면)',
                '<canvas width="320" height="320" aria-label="STEERIX loading"></canvas>',
                BG_CHIPS.replace('<span class="sep"></span>', ''), script, css)


def write(out):
    D = {k: out / v for k, v in A.DIRS.items()}
    s2m = (D[1] / 'steerix-to-matrix.svg').read_text()
    m2s = (D[2] / 'matrix-to-steerix.svg').read_text()
    pages = {}
    pages[D[1] / 'steerix-to-matrix.html'] = transition(
        s2m, 'STEERIX → MATRIX', '../2-전환-MATRIX에서-STEERIX로/matrix-to-steerix.html', '반대 방향 (MATRIX → STEERIX)')
    pages[D[2] / 'matrix-to-steerix.html'] = transition(
        m2s, 'MATRIX → STEERIX', '../1-전환-STEERIX에서-MATRIX로/steerix-to-matrix.html', '반대 방향 (STEERIX → MATRIX)')
    state = {'green': ('초록 (ready)', A.COLOURS['green']), 'white': ('흰색', '#ffffff'),
             'cyan': ('하늘색 (앱 로딩)', A.COLOURS['cyan']), 'black': ('검정', '#000000')}
    plain = '''
function paint(key) {
  const fill = {''' + ', '.join(f"{k}: '{v[1]}'" for k, v in state.items()) + '''}[key];
  if (!fill) return;
  svgs.forEach((s) => {
    s.querySelector('.paint').setAttribute('fill', fill);
    const letters = s.querySelector('.letters');
    if (letters) letters.setAttribute('fill', key === 'black' ? '#000000' : key === 'white' ? '#ffffff' : '#e6efec');
  });
}'''
    order = {k: state[k] for k in ('cyan', 'white', 'green', 'black')}
    icon = (D[3] / 'loading-x-to-steerix-cyan.svg').read_text()
    pages[D[3] / 'loading-x-to-steerix.html'] = loader(
        [inline(icon)], 'MATRIX X → STEERIX X 로딩', 'MATRIX X ↔ STEERIX X · 돌면서 모양이 바뀜 · 3.62초 반복 (앱 로딩 아이콘)',
        order, 'cyan', plain)
    word = (D[4] / 'loading-matrix-x-turn-color.svg').read_text()
    pages[D[4] / 'loading-matrix-x-turn.html'] = loader(
        [inline(word, 'wordmark', wide=True)], 'MATRIX 글자 X 회전 로딩', 'MATRIX의 X가 돌면서 STEERIX X로 바뀌었다 돌아옴 · 3.62초 반복',
        order, 'cyan', plain)
    dock = (D[5] / 'loading-steerix-spin-green.svg').read_text()
    looks = {'green': ('초록', A.STEERIX_GREEN), 'white': ('흰색', '#ffffff'), 'black': ('검정', '#000000')}
    dock_paint = '''
function paint(key) {
  const fill = { green: '#00dc7d', white: '#ffffff', black: '#000000' }[key];
  if (fill) svgs[0].querySelector('.paint').setAttribute('fill', fill);
}'''
    pages[D[5] / 'loading-steerix-spin.html'] = loader(
        [inline(dock)], 'STEERIX 회전 로딩', 'STEERIX 회전 · 1.8초 반복 (모였다가 한 바퀴 돌고 다시 벌어짐)', looks, 'green', dock_paint)
    pages[D[5] / 'loading-steerix-code-rain.html'] = rain_page()
    for path, html in pages.items():
        path.write_text(html)
    return pages


if __name__ == '__main__':
    for p, html in write(Path(sys.argv[1]).expanduser()).items():
        print(p.relative_to(Path(sys.argv[1]).expanduser()), f'{len(html) / 1024:.0f} KB')
