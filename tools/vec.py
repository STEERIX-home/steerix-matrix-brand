"""Vector paths: parse SVG path data, transform, bounds, and write SVG / PDF (also saved as .ai) / EPS.

A shape is (subpaths, fill_rule, colour key); a subpath is [start, [(op, pts...)...], closed] with op 'L', 'Q' or 'C'.
"""
import re

TOKEN = re.compile(r'[MmLlHhVvQqCcZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def parse(d):
    toks, i, out = TOKEN.findall(d), 0, []
    cmd, cur, start, sub = None, (0.0, 0.0), (0.0, 0.0), None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v
    while i < len(toks):
        if re.fullmatch(r'[A-Za-z]', toks[i]):
            cmd = toks[i]
            i += 1
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if c == 'M':
            cur = (ox + num(), oy + num())
            start, sub = cur, [cur, [], False]
            out.append(sub)
            cmd = 'l' if rel else 'L'
        elif c == 'L':
            cur = (ox + num(), oy + num())
            sub[1].append(('L', cur))
        elif c == 'H':
            cur = ((cur[0] if rel else 0.0) + num(), cur[1])
            sub[1].append(('L', cur))
        elif c == 'V':
            cur = (cur[0], (cur[1] if rel else 0.0) + num())
            sub[1].append(('L', cur))
        elif c == 'Q':
            q = (ox + num(), oy + num())
            cur = (ox + num(), oy + num())
            sub[1].append(('Q', q, cur))
        elif c == 'C':
            c1 = (ox + num(), oy + num())
            c2 = (ox + num(), oy + num())
            cur = (ox + num(), oy + num())
            sub[1].append(('C', c1, c2, cur))
        elif c == 'Z':
            sub[2] = True
            cur = start
    return out


def polys(points_list):
    return [[tuple(p[0]), [('L', tuple(q)) for q in p[1:]], True] for p in points_list]


def transform(subs, a, b, c, d, e, f):
    t = lambda p: (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)
    return [[t(s[0]), [(seg[0],) + tuple(t(p) for p in seg[1:]) for seg in s[1]], s[2]] for s in subs]


def tsr(subs, tx, ty, s):
    """translate(tx ty) scale(s)"""
    return transform(subs, s, 0, 0, s, tx, ty)


def points(subs, steps=16):
    for st, segs, _ in subs:
        p0 = st
        yield p0
        for seg in segs:
            if seg[0] == 'L':
                p0 = seg[1]
                yield p0
            elif seg[0] == 'Q':
                q, p1 = seg[1], seg[2]
                for k in range(1, steps + 1):
                    u = k / steps
                    yield tuple((1 - u) ** 2 * p0[j] + 2 * (1 - u) * u * q[j] + u * u * p1[j] for j in (0, 1))
                p0 = p1
            else:
                c1, c2, p1 = seg[1], seg[2], seg[3]
                for k in range(1, steps + 1):
                    u = k / steps
                    yield tuple((1 - u) ** 3 * p0[j] + 3 * (1 - u) ** 2 * u * c1[j] + 3 * (1 - u) * u * u * c2[j] + u ** 3 * p1[j] for j in (0, 1))
                p0 = p1


def bounds(shapes):
    pts = [p for sh in shapes for p in points(sh[0])]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def fmt(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def svg_d(subs):
    out = []
    for st, segs, closed in subs:
        out.append(f'M{fmt(st[0])} {fmt(st[1])}')
        for seg in segs:
            out.append(seg[0] + ' '.join(f'{fmt(p[0])} {fmt(p[1])}' for p in seg[1:]))
        if closed:
            out.append('Z')
    return ''.join(out)


def svg(shapes, colours, box, title, width=None, height=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    size = f' width="{fmt(width)}" height="{fmt(height)}"' if width else ''
    body = '\n'.join(f'  <path fill="{colours[k]}" fill-rule="{rule}" d="{svg_d(transform(subs, 1, 0, 0, 1, -x0, -y0))}"/>'
                     for subs, rule, k in shapes)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}"{size}>\n'
            f'  <title>{title}</title>\n{body}\n</svg>\n')


def rgb(hexc):
    hexc = hexc.lstrip('#')
    return tuple(int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _ops(subs, x0, y0, h, flip=True, ps=False):
    """Path operators in points; y flipped so the artwork stands upright."""
    T = (lambda p: (p[0] - x0, h - (p[1] - y0))) if flip else (lambda p: (p[0] - x0, p[1] - y0))
    m, l, c, z = ('moveto', 'lineto', 'curveto', 'closepath') if ps else ('m', 'l', 'c', 'h')
    out = []
    for st, segs, closed in subs:
        p0 = st
        out.append('%s %s %s' % (fmt(T(st)[0]), fmt(T(st)[1]), m))
        for seg in segs:
            if seg[0] == 'L':
                p0 = seg[1]
                out.append('%s %s %s' % (fmt(T(p0)[0]), fmt(T(p0)[1]), l))
            else:
                if seg[0] == 'Q':
                    q, p1 = seg[1], seg[2]
                    c1 = (p0[0] + 2 / 3 * (q[0] - p0[0]), p0[1] + 2 / 3 * (q[1] - p0[1]))
                    c2 = (p1[0] + 2 / 3 * (q[0] - p1[0]), p1[1] + 2 / 3 * (q[1] - p1[1]))
                else:
                    c1, c2, p1 = seg[1], seg[2], seg[3]
                pts = [T(c1), T(c2), T(p1)]
                out.append(' '.join(f'{fmt(p[0])} {fmt(p[1])}' for p in pts) + ' ' + c)
                p0 = p1
        if closed:
            out.append(z)
    return out


def pdf(shapes, colours, box, title):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    ops = []
    for subs, rule, k in shapes:
        r, g, b = rgb(colours[k])
        ops.append(f'{fmt(r)} {fmt(g)} {fmt(b)} rg')
        ops += _ops(subs, x0, y0, h)
        ops.append('f*' if rule == 'evenodd' else 'f')
    stream = '\n'.join(ops).encode()
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            (f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {fmt(w)} {fmt(h)}] /TrimBox [0 0 {fmt(w)} {fmt(h)}] '
             f'/ArtBox [0 0 {fmt(w)} {fmt(h)}] /Contents 4 0 R /Resources << >> >>').encode(),
            b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream',
            f'<< /Title ({title}) /Creator (brand-kit vec.py) /Producer (brand-kit) >>'.encode()]
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offs = []
    for n, o in enumerate(objs, 1):
        offs.append(len(out))
        out += b'%d 0 obj\n' % n + o + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
    for o in offs:
        out += b'%010d 00000 n \n' % o
    out += b'trailer\n<< /Size %d /Root 1 0 R /Info 5 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)
    return bytes(out)


def eps(shapes, colours, box, title):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    lines = ['%!PS-Adobe-3.0 EPSF-3.0', f'%%BoundingBox: 0 0 {int(-(-w // 1))} {int(-(-h // 1))}',
             f'%%HiResBoundingBox: 0 0 {fmt(w)} {fmt(h)}', f'%%Title: {title}', '%%Creator: brand-kit vec.py',
             '%%Pages: 1', '%%EndComments', 'gsave']
    for subs, rule, k in shapes:
        r, g, b = rgb(colours[k])
        lines.append(f'{fmt(r)} {fmt(g)} {fmt(b)} setrgbcolor newpath')
        lines += _ops(subs, x0, y0, h, ps=True)
        lines.append('eofill' if rule == 'evenodd' else 'fill')
    lines += ['grestore', 'showpage', '%%EOF', '']
    return '\n'.join(lines).encode()
