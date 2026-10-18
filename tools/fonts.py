"""Fonts: the logo letters as installable TrueType fonts, and the UI fonts the MATRIX app uses.

STEERIX Logo: S T E R I X from the STEERIX wordmark (the first E's shape serves both Es; a kern pair puts the R
where the logo has it). MATRIX Logo: M A T R I from MATRI and the X mark as X. Typing STEERIX / MATRIX (or lower
case) sets the logo spacing. Cap height 700 of 1000 units; outlines keep the artwork's quadratic curves.
IBM Plex Sans 400/500/600 and Mono 400/500 (Latin): the app's @fontsource WOFF files, unpacked to TTF (OFL 1.1).

    ~/office-film-v5/dish/.venv/bin/python fonts.py OUT_DIR
"""
import math
import shutil
import sys
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

import shapes as S
import vec

G = S.G
CAP = 700
FONTSOURCE = Path('~/matrix_reboot/web/node_modules/@fontsource').expanduser()


def area(pts):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2


def inside(pt, pts):
    x, y, c = pt[0], pt[1], False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def glyph(subs, place):
    """subs in artwork coordinates (y down); place(p) -> font units (y up). Outer contours clockwise, holes not."""
    contours = []
    for st, segs, _ in subs:
        pts = [(st, True)]
        for seg in segs:
            if seg[0] == 'L':
                pts.append((seg[1], True))
            elif seg[0] == 'Q':
                pts += [(seg[1], False), (seg[2], True)]
            else:
                raise ValueError('cubic segment in a letter')
        if pts[-1][1] and math.dist(pts[-1][0], pts[0][0]) < 1e-6:
            pts.pop()
        contours.append([(place(p), on) for p, on in pts])
    pen = TTGlyphPen(None)
    for i, c in enumerate(contours):
        on_pts = [p for p, on in c if on]
        hole = sum(inside(on_pts[0], [p for p, on in o if on]) for j, o in enumerate(contours) if j != i) % 2 == 1
        clockwise = area(on_pts) < 0
        if clockwise == hole:
            c = [c[0]] + c[1:][::-1]
        pen.moveTo(c[0][0])
        k = 1
        while k < len(c):
            if c[k][1]:
                pen.lineTo(c[k][0])
                k += 1
            else:
                end = c[k + 1][0] if k + 1 < len(c) else c[0][0]
                pen.qCurveTo(c[k][0], end)
                k += 2
        pen.closePath()
    return pen.glyph()


def notdef():
    pen = TTGlyphPen(None)
    for box, cw in (((50, 0, 450, 700), True), ((100, 50, 400, 650), False)):
        x0, y0, x1, y1 = box
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)] if cw else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def build(path, family, letters, kern, extra_desc):
    """letters: [(char, subs, (left, top, bottom) of the letter row in artwork units, advance in artwork units)]"""
    names = ['.notdef', 'space'] + [c for c, *_ in letters]
    glyphs, metrics = {'.notdef': notdef(), 'space': TTGlyphPen(None).glyph()}, {'.notdef': (500, 50)}
    ymin, ymax = 0, CAP
    for c, subs, (left, top, base), adv in letters:
        k = CAP / (base - top)
        place = lambda p, left=left, base=base, k=k: (round((p[0] - left) * k), round((base - p[1]) * k))
        g = glyphs[c] = glyph(subs, place)
        g.recalcBounds(None)
        metrics[c] = (round(adv * k), g.xMin)
        ymin, ymax = min(ymin, g.yMin), max(ymax, g.yMax)
    metrics['space'] = (round(0.4 * 1000), 0)
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    cmap = {32: 'space'}
    for c, *_ in letters:
        cmap[ord(c)] = c
        cmap[ord(c.lower())] = c
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    asc, desc = max(900, ymax + 50), min(-200, ymin - 50)
    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    ps = family.replace(' ', '') + '-Regular'
    fb.setupNameTable({'familyName': family, 'styleName': 'Regular', 'uniqueFontIdentifier': f'{ps};1.000',
                       'fullName': f'{family} Regular', 'psName': ps, 'version': 'Version 1.000',
                       'description': f'Letterforms of the {family.split()[0]} logo artwork. {extra_desc}'})
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0, usWinAscent=asc, usWinDescent=-desc,
                sCapHeight=CAP, sxHeight=CAP, achVendID='NONE', fsType=0)
    fb.setupPost()
    fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nfeature kern {\n' + \
          ''.join(f'  pos {a} {b} {v};\n' for (a, b), v in kern.items()) + '} kern;\n'
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(path)
    return ymin, ymax


def steerix_font(path):
    tx, ty, s = G['steerix_letters']['transform']
    subs = [vec.parse(d) for d in G['steerix_letters']['paths']]       # S T E E R I X, local units
    lefts = [vec.bounds([(p, 'nonzero', 'k')])[0] for p in subs]
    top, base = 15.9, 36.1
    order = ['S', 'T', 'E', None, 'R', 'I', 'X']                        # the second E is not a glyph of its own
    letters = []
    for i, c in enumerate(order):
        if c is None:
            continue
        nxt = i + 1 if order[i + 1:i + 2] != [None] else i + 1
        adv = (lefts[nxt] - lefts[i]) if i + 1 < len(order) else (vec.bounds([(subs[i], 'nonzero', 'k')])[2] - lefts[i] + 6.4)
        letters.append((c, subs[i], (lefts[i], top, base), adv))
    k = 1000 * (CAP / 1000) / (base - top)
    e_r = (lefts[4] - lefts[3]) - (lefts[3] - lefts[2])                # R after the second E
    build(path, 'STEERIX Logo', letters, {('E', 'R'): round(e_r * k)}, 'Contains S T E R I X.')


def matrix_font(path):
    tx, ty, s = G['matrix_letters']['transform']
    subs = [vec.parse(d) for d in G['matrix_letters']['paths']]         # M A T R I, local units
    top, base = 26.7, 88.7
    # the X mark in the same local units (artwork -> letters' local frame)
    xs = vec.transform(S.matrix_x()[0][0], 1 / s, 0, 0, 1 / s, -tx / s, -ty / s)
    allsubs = subs + [xs]
    lefts = [vec.bounds([(p, 'nonzero', 'k')])[0] for p in allsubs]
    letters = []
    for i, c in enumerate('MATRIX'):
        adv = (lefts[i + 1] - lefts[i]) if i < 5 else (vec.bounds([(xs, 'nonzero', 'k')])[2] - lefts[i] + 20)
        letters.append((c, allsubs[i], (lefts[i], top, base), adv))
    return build(path, 'MATRIX Logo', letters, {}, 'Contains M A T R I and the X mark.')


def plex(out):
    for fam, weights in (('sans', (400, 500, 600)), ('mono', (400, 500))):
        for w in weights:
            f = TTFont(FONTSOURCE / f'ibm-plex-{fam}/files/ibm-plex-{fam}-latin-{w}-normal.woff')
            f.flavor = None
            name = {400: 'Regular', 500: 'Medium', 600: 'SemiBold'}[w]
            f.save(out / f'IBMPlex{fam.title()}-{name}-Latin.ttf')
    shutil.copy(FONTSOURCE / 'ibm-plex-sans/LICENSE', out / 'IBM-Plex-OFL-LICENSE.txt')


if __name__ == '__main__':
    out = Path(sys.argv[1]).expanduser() / '4-폰트'
    (out / 'UI 글꼴 (IBM Plex)').mkdir(parents=True, exist_ok=True)
    steerix_font(out / 'STEERIX-Logo-Regular.ttf')
    print('MATRIX X y range', matrix_font(out / 'MATRIX-Logo-Regular.ttf'))
    plex(out / 'UI 글꼴 (IBM Plex)')
    for p in sorted(out.rglob('*')):
        print(p.relative_to(out), p.stat().st_size if p.is_file() else '')
