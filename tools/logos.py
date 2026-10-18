"""Static logo files: SVG (white / black / colour), PDF + EPS + AI (black and colour; the .ai is PDF-based, which
Illustrator opens as editable paths) and transparent PNGs, plus the STEERIX app icon at 1024 px.

    ~/office-film-v5/dish/.venv/bin/python logos.py OUT_DIR
"""
import asyncio
import sys
from pathlib import Path

import shapes as S
import vec
from cdp import Chrome

DIRS = {'steerix-logo': '1-STEERIX/로고(심볼+글자)', 'steerix-symbol': '1-STEERIX/심볼(그림만)',
        'steerix-wordmark': '1-STEERIX/글자만', 'matrix-logo': '2-MATRIX/로고(MATRIX 전체 글자)',
        'matrix-x': '2-MATRIX/X 로고만'}
TMP = Path(__file__).parent / 'tmp'


def page(svg_text, w, h, bg='transparent'):
    return (f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;background:{bg}}}'
            f'svg{{display:block;width:{w}px;height:{h}px}}</style>{svg_text}')


async def main(out):
    jobs = []
    for name, (make, png_w) in S.LOGOS.items():
        shp = make()
        bx = S.box(shp)
        d = out / DIRS[name]
        d.mkdir(parents=True, exist_ok=True)
        w, h = bx[2] - bx[0], bx[3] - bx[1]
        png_h = round(png_w * h / w)
        for cw, colours in S.COLOURS[name].items():
            title = f'{S.TITLES[name]} ({cw})'
            (d / f'{name}-{cw}.svg').write_text(vec.svg(shp, colours, bx, title))
            if cw != 'white':
                stem = name if cw == 'black' else f'{name}-{cw}'
                pdf = vec.pdf(shp, colours, bx, title)
                (d / f'{stem}.pdf').write_bytes(pdf)
                (d / f'{stem}.ai').write_bytes(pdf)
                (d / f'{stem}.eps').write_bytes(vec.eps(shp, colours, bx, title))
            jobs.append((page(vec.svg(shp, colours, bx, title), png_w, png_h), png_w, png_h, d / f'{name}-{cw}.png', True))
        print(f'{name}: {w:.1f} x {h:.1f} units, png {png_w} x {png_h}')
    # The app icon: steerix.png's layout (the halves in a 160 box) at 1024 px, white on black.
    icon = vec.polys([S.G['steerix_left'], S.G['steerix_right']])
    icon_svg = vec.svg([(icon, 'nonzero', 'mark')], {'mark': '#ffffff'}, (0, 0, 160, 160), 'STEERIX app icon')
    jobs.append((page(icon_svg, 1024, 1024, '#000'), 1024, 1024, out / DIRS['steerix-symbol'] / 'steerix-app-icon-1024.png', False))
    async with Chrome() as c:
        for html, w, h, dest, clear in jobs:
            f = TMP / 'logo.html'
            f.write_text(html)
            await c.size(w, h)
            await c.transparent(clear)
            await c.goto(f)
            await c.shot(dest)
    print('png', len(jobs))


if __name__ == '__main__':
    asyncio.run(main(Path(sys.argv[1]).expanduser()))
