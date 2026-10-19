"""RobotSim (STEERIX's real-to-sim service, robotsim.dev) logo files, rebuilt from the live site's header so the
files match what visitors see: the cube mark (robotsim.dev/logo-mark.svg) and the name in Inter Tight, laid out with
the header's own measurements (30 px mark; "RobotSim" 700 21 px, -0.03 em, baseline 24.5; "by Steerix" 500 13.5 px,
baseline 21.5). Text is shaped with HarfBuzz (kerning as in the browser) and turned into outlines with fontTools.

Writes 5-RobotSim/: robotsim-mark, robotsim-logo and robotsim-logo-by-steerix as SVG and transparent PNG, plus PDF
(also saved as .ai) for every colourway except white. No EPS: the mark's side face is 45 % transparent.

    ~/office-film-v5/dish/.venv/bin/python robotsim.py OUT_DIR      (needs fontTools and uharfbuzz)
"""
import asyncio
import base64
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / '4-폰트' / 'RobotSim 글꼴 (Inter Tight, JetBrains Mono)'
INTER = FONTS / 'InterTight[wght].ttf'
DIR = '5-RobotSim'

# The cube mark, exactly as robotsim.dev/logo-mark.svg (64 x 64): top face, side face at 45 %, nine dots.
MARK_TOP = 'M32 6 54.5 19 32 32 9.5 19Z'
MARK_SIDE = 'M32 32 54.5 19v26L32 58Z'
MARK_DOTS = [(13.2, 25.6), (20.7, 29.9), (28.2, 34.3), (13.2, 33.6), (20.7, 37.9), (28.2, 42.3),
             (13.2, 41.6), (20.7, 45.9), (28.2, 50.3)]
MARK_EXTENT = (9.5, 6, 54.5, 58)          # drawn bounds inside the 64 box (dots reach x 11.1)
# The site header (CSS px): mark box at (0, 1.8), 30 px; then the two lines of text.
MARK_AT, MARK_PX = (0, 1.8), 30
WORD = dict(text='RobotSim', x=40.0, base=24.5, size=21.0, wght=700, track=-0.63, key='text')
BY = dict(text='by Steerix', x=136.9, base=21.5, size=13.5, wght=500, track=0.0, key='sub')

MINT, TEXT, MUTED = '#5ef2c2', '#e9eff1', '#8d9ca3'      # robotsim.dev --mint, --text, --muted
COLOURS = {
    'mint': {'mark': MINT, 'text': TEXT, 'sub': MUTED},          # as on the site, for dark backgrounds
    'white': {'mark': '#ffffff', 'text': '#ffffff', 'sub': '#ffffff'},
    'black': {'mark': '#000000', 'text': '#000000', 'sub': '#000000'},
    'black-mint': {'mark': MINT, 'text': '#07090b', 'sub': '#5f6d73'},   # light backgrounds
}
LOGOS = {  # name: (parts, colourways, png width)
    'robotsim-mark': (('mark',), ('mint', 'white', 'black'), 2048),
    'robotsim-logo': (('mark', 'word'), tuple(COLOURS), 3200),
    'robotsim-logo-by-steerix': (('mark', 'word', 'by'), tuple(COLOURS), 3200),
}
TITLES = {'robotsim-mark': 'RobotSim mark', 'robotsim-logo': 'RobotSim logo',
          'robotsim-logo-by-steerix': 'RobotSim by Steerix logo'}
DIRS = {name: DIR for name in LOGOS}


def f3(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def text_path(spec):
    """SVG path data (CSS px, y down) and bounds of one header text, shaped like the browser does."""
    face = hb.Face(hb.Blob.from_file_path(str(INTER)))
    font = hb.Font(face)
    font.set_variations({'wght': spec['wght']})
    buf = hb.Buffer()
    buf.add_str(spec['text'])
    buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True, 'liga': True})
    tt = instantiateVariableFont(TTFont(INTER), {'wght': spec['wght']})
    glyphs, order, upem = tt.getGlyphSet(), tt.getGlyphOrder(), tt['head'].unitsPerEm
    k = spec['size'] / upem
    pen = SVGPathPen(glyphs, ntos=f3)
    bounds = BoundsPen(glyphs)
    x = spec['x']
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        t = (k, 0, 0, -k, x + pos.x_offset * k, spec['base'] - pos.y_offset * k)
        name = order[info.codepoint]
        glyphs[name].draw(TransformPen(pen, t))
        glyphs[name].draw(TransformPen(bounds, t))
        x += pos.x_advance * k + spec['track']
    return pen.getCommands(), bounds.bounds


def mark_svg(colour):
    s = MARK_PX / 64
    dots = ''.join(f'<circle cx="{cx}" cy="{cy}" r="2.1"/>' for cx, cy in MARK_DOTS)
    return (f'<g transform="translate({f3(MARK_AT[0])} {f3(MARK_AT[1])}) scale({s:.6g})">'
            f'<path d="{MARK_TOP}" fill="{colour}"/><path d="{MARK_SIDE}" fill="{colour}" fill-opacity=".45"/>'
            f'<g fill="{colour}">{dots}</g></g>')


def build(parts, colours, title):
    s = MARK_PX / 64
    x0, y0 = MARK_AT[0] + MARK_EXTENT[0] * s, MARK_AT[1] + MARK_EXTENT[1] * s
    x1, y1 = MARK_AT[0] + MARK_EXTENT[2] * s, MARK_AT[1] + MARK_EXTENT[3] * s
    body = [mark_svg(colours['mark'])]
    for part, spec in (('word', WORD), ('by', BY)):
        if part in parts:
            d, (bx0, by0, bx1, by1) = text_path(spec)
            body.append(f'<path fill="{colours[spec["key"]]}" d="{d}"/>')
            x0, y0, x1, y1 = min(x0, bx0), min(y0, by0), max(x1, bx1), max(y1, by1)
    m = 0.04 * (y1 - y0)
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    w, h = x1 - x0, y1 - y0
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f3(x0)} {f3(y0)} {f3(w)} {f3(h)}">\n'
           f'  <title>{title}</title>\n  ' + '\n  '.join(body) + '\n</svg>\n')
    return svg, w, h


def page(svg, w, h, pdf=False):
    size = f'@page{{size:{w}px {h}px;margin:0}}' if pdf else ''
    return (f'<!doctype html><meta charset="utf-8"><style>{size}html,body{{margin:0;background:transparent}}'
            f'svg{{display:block;width:{w}px;height:{h}px}}</style>{svg}')


async def main(out):
    from cdp import Chrome
    d = out / DIR
    d.mkdir(parents=True, exist_ok=True)
    tmp = Path(__file__).parent / 'tmp'
    tmp.mkdir(exist_ok=True)
    jobs = []
    for name, (parts, ways, png_w) in LOGOS.items():
        for cw in ways:
            svg, w, h = build(parts, COLOURS[cw], f'{TITLES[name]} ({cw})')
            (d / f'{name}-{cw}.svg').write_text(svg)
            png_h = round(png_w * h / w)
            jobs.append(('png', page(svg, png_w, png_h), png_w, png_h, d / f'{name}-{cw}.png'))
            if cw != 'white':
                pw, ph = round(png_w / 4), round(png_w / 4 * h / w)       # 800 px wide page, vector
                jobs.append(('pdf', page(svg, pw, ph, pdf=True), pw, ph, d / f'{name}-{cw}.pdf'))
        print(f'{name}: {", ".join(ways)}')
    async with Chrome() as c:
        for kind, html, w, h, dest in jobs:
            f = tmp / 'robotsim.html'
            f.write_text(html)
            await c.size(w, h)
            await c.transparent(True)
            await c.goto(f)
            if kind == 'png':
                await c.shot(dest)
            else:
                r = await c.call('Page.printToPDF', preferCSSPageSize=True, printBackground=False,
                                 marginTop=0, marginBottom=0, marginLeft=0, marginRight=0)
                data = base64.b64decode(r['data'])
                dest.write_bytes(data)
                dest.with_suffix('.ai').write_bytes(data)      # PDF-based .ai, as logos.py does
    print('files', len(jobs))


if __name__ == '__main__':
    asyncio.run(main(Path(sys.argv[1]).expanduser()))
