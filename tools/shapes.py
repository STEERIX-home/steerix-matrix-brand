"""The brand shapes in the intro's 1280 x 480 artboard coordinates (the supplied STEERIX -> MATRIX burst).

STEERIX symbol: the two halves of steerix.ts (= steerix.png, the app icon), placed and scaled as the intro places its
six-part version (bbox centre 305.9, 240; x1.1997). STEERIX letters: the intro's seven letter paths. MATRI letters:
the intro's five paths (even-odd). MATRIX X: matrix.ts MATRIX_A (= favicon.svg), placed and scaled as the intro's
final X (bbox centre 963.8, 240.3; x1.538).
"""
import json
from pathlib import Path

import vec

G = json.loads((Path(__file__).parent / 'geo.json').read_text())
ICON_S, ICON_C = 1.1997, (305.90865, 240.0)
X_S, X_C = 1.53803, (963.8356, 240.30825)


def steerix_symbol(key='mark'):
    s = ICON_S
    subs = vec.transform(vec.polys([G['steerix_left'], G['steerix_right']]), s, 0, 0, s, ICON_C[0] - 80 * s, ICON_C[1] - 80 * s)
    return [(subs, 'nonzero', key)]


def steerix_letters(key='text'):
    tx, ty, s = G['steerix_letters']['transform']
    return [(vec.tsr(vec.parse(d), tx, ty, s), 'nonzero', key) for d in G['steerix_letters']['paths']]


def matrix_letters(key='text'):
    tx, ty, s = G['matrix_letters']['transform']
    return [(vec.tsr(vec.parse(d), tx, ty, s), 'evenodd', key) for d in G['matrix_letters']['paths']]


def matrix_x(key='mark', polys=None):
    s = X_S
    return [(vec.transform(vec.polys(polys or G['matrix_A']), s, 0, 0, s, X_C[0], X_C[1]), 'nonzero', key)]


LOGOS = {
    # name: (shapes, {colourway: {key: colour}}, png width)
    'steerix-logo': (lambda: steerix_symbol() + steerix_letters(), 3200),
    'steerix-symbol': (steerix_symbol, 2048),
    'steerix-wordmark': (steerix_letters, 3200),
    'matrix-logo': (lambda: matrix_letters() + matrix_x(), 3200),
    'matrix-x': (matrix_x, 2048),
}
WHITE, BLACK = {'mark': '#ffffff', 'text': '#ffffff'}, {'mark': '#000000', 'text': '#000000'}
COLOURS = {
    'steerix-logo': {'white': WHITE, 'black': BLACK},
    'steerix-symbol': {'white': WHITE, 'black': BLACK, 'green': {'mark': '#00dc7d'}},
    'steerix-wordmark': {'white': WHITE, 'black': BLACK},
    # green X = the app's ready colour (favicon); on dark the letters keep the app's #e6efec
    'matrix-logo': {'white': WHITE, 'black': BLACK, 'green-x': {'mark': '#00db89', 'text': '#e6efec'},
                    'black-green-x': {'mark': '#00db89', 'text': '#000000'}},
    'matrix-x': {'white': WHITE, 'black': BLACK, 'green': {'mark': '#00db89'}},
}
TITLES = {'steerix-logo': 'STEERIX logo', 'steerix-symbol': 'STEERIX symbol', 'steerix-wordmark': 'STEERIX wordmark',
          'matrix-logo': 'MATRIX logo', 'matrix-x': 'MATRIX X'}


def box(shapes, margin=0.02):
    x0, y0, x1, y1 = vec.bounds(shapes)
    m = margin * max(x1 - x0, y1 - y0)
    return x0 - m, y0 - m, x1 + m, y1 + m
