"""The animations as SMIL SVG files and live HTML pages.

1 STEERIX -> MATRIX: the supplied burst (startup-intro.svg), unchanged.
2 MATRIX -> STEERIX: the same burst played backwards over its transition (640-1672 ms of 2600): the X flies apart
  into the STEERIX symbol, MATRI fades out (I first), STEERIX slides in from the right. Splines are mirrored, so
  every ease-out becomes the matching ease-in. Fade-in from black and the final hold mirror the original.
3 loading, MATRIX X -> STEERIX X: matrix-logo.js's icon loop as the app shows it (1.05 s hold, 0.76 s
  360-degree turn, Bezier (.76,0,.18,1); the shape changes at turn progress .27-.73 with smootherstep from the
  MATRIX X (A) into the STEERIX-shaped X (B) and back on the next turn).
4 loading, the X of MATRIX turning: the same loop beside MATRI (MatrixLogo wordmark with animate on).
5 loading, STEERIX turn: steerix_loading_motion.cpp's loop (1.8 s: halves dock 7 units, 360-degree turn, undock),
  in green and in white, and the code-rain version (canvas). No outlines: the owner wants the shapes alone.

    python3 anim.py OUT_DIR
"""
import math
import sys
from pathlib import Path

import shapes as S
import vec

G = S.G
WEB = Path('~/matrix_reboot/web').expanduser()
ORIGINAL = (WEB / 'public/brand/startup-intro.svg').read_text()
MONO_WOFF2 = WEB / 'node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2'
DIRS = {1: '3-애니메이션/1-전환-STEERIX에서-MATRIX로', 2: '3-애니메이션/2-전환-MATRIX에서-STEERIX로',
        3: '3-애니메이션/3-로딩-MATRIX X에서-STEERIX X로', 4: '3-애니메이션/4-로딩-MATRIX 글자 X 회전',
        5: '3-애니메이션/5-로딩-STEERIX 회전(전부)'}
COLOURS = {'white': '#ffffff', 'green': '#00db89', 'cyan': '#53c1db', 'black': '#000000',
           'amber': '#f5b536', 'red': '#ef5a64', 'gray': '#759495'}
STEERIX_GREEN = '#00dc7d'
fmt = vec.fmt


def kt(times):
    return ';'.join('0' if t <= 0 else '1' if t >= 1 else f'{t:.9f}'.rstrip('0') for t in times)


def ks(splines):
    return ';'.join(' '.join(fmt(v) for v in s) for s in splines)


def rev(s):
    """The spline of the same segment played backwards."""
    x1, y1, x2, y2 = s
    return [round(1 - x2, 4), round(1 - y2, 4), round(1 - x1, 4), round(1 - y1, 4)]


LIN = [0, 0, 1, 1]
REVEAL = [0.22, 1, 0.36, 1]


def d_of(polys):
    return ' '.join('M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in p) + ' Z' for p in polys)


def smoother(t):
    t = min(1, max(0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp_polys(a, b, m):
    return [[[p[0] + (q[0] - p[0]) * m, p[1] + (q[1] - p[1]) * m] for p, q in zip(P, Q)] for P, Q in zip(a, b)]


# ---------------------------------------------------------------- 2: MATRIX -> STEERIX
def reverse_svg():
    A = G['anims']
    mid = 0.246153846 + 0.643076923          # t' = mid - t over the transition (640 + 1672 ms)
    sw_tx, sw_ty, sw_s = G['steerix_letters']['transform']
    mx_tx, mx_ty, mx_s = G['matrix_letters']['transform']
    so, st = A['steerix-wordmark:opacity'], A['steerix-wordmark:transform']
    # STEERIX: hidden, then the original fade-out / slide reversed; hold to the end.
    s_op = (f'<animate attributeName="opacity" dur="2.6s" begin="0s" fill="freeze" repeatCount="1" calcMode="spline" '
            f'keyTimes="{kt([0, mid - so["keyTimes"][3], mid - so["keyTimes"][2], 1])}" '
            f'keySplines="{ks([LIN, rev(so["keySplines"][2]), LIN])}" values="0;0;1;1" />')
    s_tr = (f'<animateTransform attributeName="transform" dur="2.6s" begin="0s" fill="freeze" repeatCount="1" calcMode="spline" '
            f'keyTimes="{kt([0, mid - st["keyTimes"][2], mid - st["keyTimes"][1], 1])}" '
            f'keySplines="{ks([LIN, rev(st["keySplines"][1]), LIN])}" values="240 0;240 0;0 0;0 0" type="translate" />')
    letters = []
    for letter, d in zip('matri', G['matrix_letters']['paths']):
        o = A[f'matrix-letter-{letter}:opacity']
        a, b = o['keyTimes'][1], o['keyTimes'][2]
        fade = rev(o['keySplines'][1])
        letters.append(
            f'      <g id="matrix-letter-{letter}" opacity="0" transform="translate(-10 0)">\n'
            f'        <animate attributeName="opacity" dur="2.6s" begin="0s" fill="freeze" repeatCount="1" calcMode="spline" '
            f'keyTimes="{kt([0, 0.0692, mid - b, mid - a, 1])}" keySplines="{ks([REVEAL, LIN, fade, LIN])}" values="0;1;1;0;0" />\n'
            f'        <animateTransform attributeName="transform" dur="2.6s" begin="0s" fill="freeze" repeatCount="1" calcMode="spline" '
            f'keyTimes="{kt([0, mid - b, mid - a, 1])}" keySplines="{ks([LIN, fade, LIN])}" values="0 0;0 0;-10 0;-10 0" type="translate" />\n'
            f'        <path d="{d}" fill-rule="evenodd" transform="translate({fmt(mx_tx)} {fmt(mx_ty)}) scale({fmt(mx_s)})" />\n'
            f'      </g>')
    mk = G['monogram_keys']
    times, values = mk['times'], mk['values']
    rt = [0] + [mid - t for t in reversed(times[1:-1])] + [1]
    rv = [values[-1]] + list(reversed(values[1:-1])) + [values[0]]
    for i in range(1, len(rt)):           # keep strictly increasing after rounding
        if round(rt[i], 9) <= round(rt[i - 1], 9):
            rt[i] = rt[i - 1] + 1e-9
    paths = '\n'.join(f'        <path d="{d}" />' for d in G['steerix_letters']['paths'])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="480" viewBox="0 0 1280 480" version="1.1" overflow="hidden" role="img" aria-labelledby="animation-title animation-desc">
  <title id="animation-title">MATRIX → STEERIX · Continuous burst (reverse)</title>
  <desc id="animation-desc">White logos on pure black. The supplied STEERIX → MATRIX burst played backwards over its transition: MATRI fades out from the I back to the M, the six parts of the X burst apart and gather into the STEERIX symbol while STEERIX slides in from the right. Splines are mirrored. 2.6 second SVG timeline, plays once and holds STEERIX. Vector paths only; no scripts or external assets.</desc>
  <!-- The original's 120 Hz geometric samples, in reverse order, with linear interpolation. -->
  <rect id="background" width="1280" height="480" fill="#000000" />
  <defs>
    <clipPath id="viewport-clip" clipPathUnits="userSpaceOnUse">
      <rect width="1280" height="480" />
    </clipPath>
  </defs>
  <g clip-path="url(#viewport-clip)">
    <g id="steerix-wordmark" fill="#ffffff" opacity="1" transform="translate(0 0)">
      {s_op}
      {s_tr}
      <g transform="translate({fmt(sw_tx)} {fmt(sw_ty)}) scale({fmt(sw_s)})">
{paths}
      </g>
    </g>
    <g id="matrix-wordmark" fill="#ffffff">
{chr(10).join(letters)}
    </g>
    <g id="monogram" fill="#ffffff" opacity="1">
      <animate attributeName="opacity" dur="2.6s" begin="0s" fill="freeze" repeatCount="1" calcMode="spline" keyTimes="0;0.0692;1" keySplines="0.22 1 0.36 1;0 0 1 1" values="0;1;1" />
      <path id="monogram-shape" fill-rule="nonzero" d="{values[0]}">
        <animate attributeName="d" begin="0s" dur="2.6s" repeatCount="1" fill="freeze" calcMode="linear" keyTimes="{kt(rt)}" values="{';'.join(rv)}" />
      </path>
    </g>
  </g>
</svg>
'''


# ---------------------------------------------------------------- 3 and 4: the turning icons
HOLD, TURN = 1050, 760
PERIOD = 2 * (HOLD + TURN)


def turning(a, b, n=36):
    """SMIL for matrix.ts sampleMatrix: rotate 0 -> 360 -> 720 and the shape a -> b -> a, looping."""
    h = HOLD / PERIOD
    rot = (f'<animateTransform attributeName="transform" type="rotate" dur="{PERIOD / 1000}s" repeatCount="indefinite" '
           f'calcMode="spline" keyTimes="{kt([0, h, 0.5, 0.5 + h, 1])}" values="0;0;360;360;720" '
           f'keySplines="0 0 1 1;0.76 0 0.18 1;0 0 1 1;0.76 0 0.18 1" />')
    times, vals = [0], [d_of(a)]
    for half, (p, q) in enumerate(((a, b), (b, a))):
        t0 = half * PERIOD / 2 + HOLD
        for i in range(n + 1):
            u = i / n
            times.append((t0 + (0.27 + 0.46 * u) * TURN) / PERIOD)
            vals.append(d_of(lerp_polys(p, q, smoother(u))))
    times.append(1)
    vals.append(d_of(a))
    morph = (f'<animate attributeName="d" dur="{PERIOD / 1000}s" repeatCount="indefinite" calcMode="linear" '
             f'keyTimes="{kt(times)}" values="{";".join(vals)}" />')
    return rot, morph


def icon_svg(a, b, fill, title, size=128):
    rot, morph = turning(a, b)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-64 -64 128 128" width="{size}" height="{size}" role="img">\n'
            f'  <title>{title}</title>\n'
            f'  <g class="paint" fill="{fill}">\n    <g>\n      {rot}\n'
            f'      <path fill-rule="nonzero" d="{d_of(a)}">\n        {morph}\n      </path>\n    </g>\n  </g>\n</svg>\n')


def wordmark_svg(fill_letters, fill_x, title):
    letters = S.matrix_letters()
    x0, y0, x1, y1 = S.box(letters + S.matrix_x())
    # room for the X's tips while it turns: the circle through its farthest corner
    r = max(math.hypot(x, y) for p in G['matrix_A'] + G['matrix_B'] for x, y in p) * S.X_S
    m = 0.02 * (x1 - x0)
    y0, y1 = min(y0, S.X_C[1] - r - m), max(y1, S.X_C[1] + r + m)
    x1 = max(x1, S.X_C[0] + r + m)
    rot, morph = turning(G['matrix_A'], G['matrix_B'])
    body = '\n'.join(f'    <path fill-rule="evenodd" d="{vec.svg_d(subs)}" />' for subs, _, _ in letters)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(x0)} {fmt(y0)} {fmt(x1 - x0)} {fmt(y1 - y0)}" '
            f'width="{fmt((x1 - x0) / 2)}" height="{fmt((y1 - y0) / 2)}" role="img">\n  <title>{title}</title>\n'
            f'  <g class="letters" fill="{fill_letters}">\n{body}\n  </g>\n'
            f'  <g class="paint" fill="{fill_x}" transform="translate({fmt(S.X_C[0])} {fmt(S.X_C[1])}) scale({fmt(S.X_S)})">\n'
            f'    <g>\n      {rot}\n      <path fill-rule="nonzero" d="{d_of(G["matrix_A"])}">\n        {morph}\n'
            f'      </path>\n    </g>\n  </g>\n</svg>\n')


# ---------------------------------------------------------------- 5: STEERIX turn (dock)
def steerix_svg(fill, title, size=160):
    pts = lambda poly: ' '.join(f'{fmt(x)},{fmt(y)}' for x, y in poly)
    common = 'dur="1.8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.26;0.72;1"'
    dock = 'keySplines="0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" width="{size}" height="{size}" role="img">\n'
            f'  <title>{title}</title>\n  <g class="paint" fill="{fill}">\n    <g>\n'
            f'      <animateTransform attributeName="transform" type="rotate" {common} values="0 80 80;0 80 80;360 80 80;360 80 80" '
            f'keySplines="0 0 1 1;0.65 0 0.35 1;0 0 1 1" />\n'
            f'      <polygon points="{pts(G["steerix_left"])}">\n'
            f'        <animateTransform attributeName="transform" type="translate" {common} values="0 0;7 0;7 0;0 0" {dock} />\n'
            f'      </polygon>\n      <polygon points="{pts(G["steerix_right"])}">\n'
            f'        <animateTransform attributeName="transform" type="translate" {common} values="0 0;-7 0;-7 0;0 0" {dock} />\n'
            f'      </polygon>\n    </g>\n  </g>\n</svg>\n')


def write(out):
    for k, d in DIRS.items():
        (out / d).mkdir(parents=True, exist_ok=True)
    files = {}
    files[(1, 'steerix-to-matrix.svg')] = ORIGINAL
    files[(2, 'matrix-to-steerix.svg')] = reverse_svg()
    green = lambda svg: svg.replace('<g id="monogram" fill="#ffffff"', f'<g id="monogram" fill="{COLOURS["green"]}"', 1)
    files[(1, 'steerix-to-matrix-green-x.svg')] = green(ORIGINAL)
    files[(2, 'matrix-to-steerix-green-x.svg')] = green(reverse_svg())
    for c in ('cyan', 'white', 'green'):
        files[(3, f'loading-x-to-steerix-{c}.svg')] = icon_svg(G['matrix_A'], G['matrix_B'], COLOURS[c],
                                                               'MATRIX X -> STEERIX X, loading')
    files[(4, 'loading-matrix-x-turn-color.svg')] = wordmark_svg('#e6efec', COLOURS['cyan'], 'MATRIX, loading')
    files[(4, 'loading-matrix-x-turn-white.svg')] = wordmark_svg('#ffffff', '#ffffff', 'MATRIX, loading')
    files[(4, 'loading-matrix-x-turn-green.svg')] = wordmark_svg('#e6efec', COLOURS['green'], 'MATRIX, loading')
    files[(5, 'loading-steerix-spin-green.svg')] = steerix_svg(STEERIX_GREEN, 'STEERIX, loading')
    files[(5, 'loading-steerix-spin-white.svg')] = steerix_svg('#ffffff', 'STEERIX, loading')
    for (k, name), text in files.items():
        (out / DIRS[k] / name).write_text(text)
    return files


if __name__ == '__main__':
    out = Path(sys.argv[1]).expanduser()
    files = write(out)
    for (k, name), text in files.items():
        print(f'{DIRS[k]}/{name}  {len(text) / 1024:.0f} KB')
