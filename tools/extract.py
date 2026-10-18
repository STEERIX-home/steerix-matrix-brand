"""Pull the brand geometry and animation keys out of the original sources into geo.json.

Sources (read-only): web/public/brand/startup-intro.svg (the supplied STEERIX -> MATRIX burst, 2.6 s SMIL),
web/src/brand/matrix.ts (port of matrix-logo.js: the X polygons A/B, loop timing) and web/src/brand/steerix.ts
(port of steerix_loading_motion.cpp: the STEERIX halves, dock/turn timing).

    python3 extract.py ~/matrix_reboot/web geo.json
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = '{http://www.w3.org/2000/svg}'


def floats(s):
    return [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', s)]


def polys_of(d):
    """'M x y L x y ... Z M ...' (absolute M/L/Z only) -> [[[x, y], ...], ...]"""
    out = []
    for sub in re.findall(r'M[^M]*', d.strip()):
        v = floats(sub)
        out.append([[v[i], v[i + 1]] for i in range(0, len(v), 2)])
    return out


def ts_points(src, name):
    m = re.search(name + r'[^=]*=\s*(?:scaled\()?\[(.*?)\]\)?;', src, re.S)
    v = floats(m.group(1))
    return [[v[i], v[i + 1]] for i in range(0, len(v), 2)]


def main():
    web, out = Path(sys.argv[1]).expanduser(), Path(sys.argv[2])
    svg = ET.parse(web / 'public/brand/startup-intro.svg').getroot()
    parent = {c: p for p in svg.iter() for c in p}
    anims = {}
    for el in svg.iter():
        if el.tag in (NS + 'animate', NS + 'animateTransform'):
            p = parent[el]
            key = (p.get('id') or parent[p].get('id')) + ':' + el.get('attributeName')
            a = {k: el.get(k) for k in ('keyTimes', 'keySplines', 'values', 'calcMode', 'dur', 'type')}
            a['keyTimes'] = [float(v) for v in a['keyTimes'].split(';')]
            if el.get('attributeName') == 'd':
                a['values'] = [v.strip() for v in a['values'].split(';')]
            else:
                a['values'] = [floats(v) for v in a['values'].split(';')]
                a['keySplines'] = [floats(v) for v in (a['keySplines'] or '').split(';') if v.strip()]
            anims[key] = a

    def group_paths(gid):
        g = next(e for e in svg.iter() if e.get('id') == gid)
        return g

    sw = group_paths('steerix-wordmark')
    inner = sw.find(NS + 'g')
    m = re.match(r'translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)', inner.get('transform'))
    steerix_letters = {'transform': [float(m.group(1)), float(m.group(2)), float(m.group(3))],
                       'paths': [p.get('d') for p in inner.findall(NS + 'path')]}
    matrix_letters = {'paths': [], 'ids': []}
    for letter in 'matri':
        g = group_paths('matrix-letter-' + letter)
        p = g.find(NS + 'path')
        m = re.match(r'translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)', p.get('transform'))
        matrix_letters['transform'] = [float(m.group(1)), float(m.group(2)), float(m.group(3))]
        matrix_letters['paths'].append(p.get('d'))
        matrix_letters['fill_rule'] = p.get('fill-rule')
    mono = anims['monogram-shape:d']
    ts = (web / 'src/brand/matrix.ts').read_text()
    a = {n: ts_points(ts, 'const ' + n) for n in ('aNW', 'aW', 'aSW')}
    b = {n: [[x * 100 / 109, y * 100 / 109] for x, y in ts_points(ts, 'const ' + n)] for n in ('bNW', 'bW', 'bSW')}
    opp = lambda pts: [[-x, -y] for x, y in pts]
    aE = [[-x, y] for x, y in a['aW']][::-1]
    matrix_A = [a['aNW'], opp(a['aSW']), a['aW'], aE, a['aSW'], opp(a['aNW'])]
    matrix_B = [b['bNW'], opp(b['bSW']), b['bW'], opp(b['bW']), b['bSW'], opp(b['bNW'])]
    st = (web / 'src/brand/steerix.ts').read_text()
    left = ts_points(st, 'export const STEERIX_LEFT')
    geo = {
        'artboard': [1280, 480],
        'steerix_letters': steerix_letters,
        'matrix_letters': matrix_letters,
        'steerix_icon6': polys_of(mono['values'][0]),
        'matrix_x6': polys_of(mono['values'][-1]),
        'monogram_keys': {'times': mono['keyTimes'], 'values': mono['values']},
        'anims': {k: v for k, v in anims.items() if not k.endswith(':d')},
        'matrix_A': matrix_A, 'matrix_B': matrix_B,
        'steerix_left': left, 'steerix_right': [[160 - x, 160 - y] for x, y in left],
    }
    out.write_text(json.dumps(geo))
    print('paths', len(steerix_letters['paths']), len(matrix_letters['paths']), 'mono keys', len(mono['values']),
          'icon6', [len(p) for p in geo['steerix_icon6']], 'x6', [len(p) for p in geo['matrix_x6']])
    print('anims', sorted(geo['anims']))
    print('A', [len(p) for p in matrix_A], 'B', [len(p) for p in matrix_B], 'left', len(left))


if __name__ == '__main__':
    main()
