"""Draws the YVIS HAUSEN wordmark as an SVG (original artwork).

The letters start from a free font (SIL Open Font License, licence in
tools/fonts/); the sweep that runs on from the A beneath the U is drawn here. Writes the SVG into partials/header.html between
<!-- wordmark --> markers.

    python3 tools/wordmark.py                      # the chosen style
    python3 tools/wordmark.py --style NAME --preview out.svg
"""
import math, os, re, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from PIL import Image, ImageDraw, ImageFont
import pathops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STYLES = {  # base font, horizontal scale, tracking (font units)
    'bodoni':    ('tools/fonts/WordmarkBodoni.ttf', 0.86, 40),
    'cormorant': ('tools/fonts/WordmarkCormorant.ttf', 0.92, 45),
    'playfair':  ('tools/fonts/WordmarkPlayfair.ttf', 0.84, 110),
}
CHOSEN = 'playfair'
TEXT = 'YVIS HAUSEN'


def measure(path, upm, cap):
    """Stem and hairline thickness of the base font, read from its H."""
    size = 1000
    f = ImageFont.truetype(path, size)
    im = Image.new('L', (1400, 1400), 0)
    ImageDraw.Draw(im).text((100, 100), 'H', font=f, fill=255)
    px = im.load()
    bbox = im.getbbox()
    ymid = (bbox[1] + bbox[3]) // 2 + int(0.17 * (bbox[3] - bbox[1]))
    run = 0
    for x in range(bbox[0], bbox[2]):
        if px[x, ymid] > 128: run += 1
        elif run: break
    stem = run * upm / size
    # crossbar: vertical run through the middle of the H
    xm = (bbox[0] + bbox[2]) // 2
    runs, cur = [], 0
    for y in range(bbox[1], bbox[3]):
        if px[xm, y] > 128: cur += 1
        elif cur: runs.append(cur); cur = 0
    hair = (min(runs) if runs else 20) * upm / size
    return stem, hair


def raster(path, ch, upm):
    """The glyph drawn at 1 px per font unit; returns pixel access and a mapper."""
    f = ImageFont.truetype(path, upm)
    im = Image.new('L', (upm * 2, upm * 2), 0)
    ImageDraw.Draw(im).text((200, int(upm * 1.4)), ch, font=f, fill=255, anchor='ls')
    return im.load(), (lambda px: px - 200), (lambda py: int(upm * 1.4) - py), (lambda fy: int(upm * 1.4) - fy), im.size


def runs_at(px, w, row):
    out, start = [], None
    for x in range(w):
        on = px[x, row] > 128
        if on and start is None: start = x
        if not on and start is not None: out.append((start, x)); start = None
    return out


def rebuilt_a(path, gs, cmap, upm, cap, stem, hair, sx, x0, ux, uw):
    """The base A without its left leg; returns (path data for the rest, apex, leg foot)."""
    px, fx, fy, toRow, (w, h) = raster(path, 'A', upm)
    inner = []
    for yy in range(int(cap * 0.45), int(cap * 0.85), 8):
        r = runs_at(px, w, toRow(yy))
        if len(r) >= 2: inner.append((fx(r[0][1]), yy))
    # inner edge of the left leg, as a line x = m*y + c
    n = len(inner); my = sum(y for _, y in inner) / n; mx = sum(x for x, _ in inner) / n
    m = sum((x - mx) * (y - my) for x, y in inner) / sum((y - my) ** 2 for _, y in inner)
    c = mx - m * my
    base = runs_at(px, w, toRow(int(cap * 0.06)))
    right_leg = fx(base[-1][0])
    top = runs_at(px, w, toRow(int(cap * 0.97)))
    apex = (fx(top[0][0]), cap)
    pen_path = pathops.Path()
    gs[cmap[ord('A')]].draw(pen_path.getPen())
    # cut away everything left of the leg's inner edge (traced row by row, so
    # the bracketed foot goes too; across the bar, the fitted line is used)
    edge = []
    for yy in range(-40, int(cap * 0.9), 6):
        r = runs_at(px, w, toRow(max(yy, 2)))
        xr = fx(r[0][1]) + 4 if len(r) >= 2 else m * yy + c + 4
        edge.append((max(xr, m * yy + c + 4), yy))
    cut = pathops.Path(); cp = cut.getPen()
    cp.moveTo((-600, -300)); cp.lineTo((edge[0][0], -300))
    for pt in edge: cp.lineTo(pt)
    cp.lineTo((m * (cap + 300) + c + 4, cap + 300)); cp.lineTo((-600, cap + 300)); cp.closePath()
    foot = pathops.Path(); fp = foot.getPen()
    fp.moveTo((-500, -300)); fp.lineTo((right_leg - stem * 0.9, -300)); fp.lineTo((right_leg - stem * 0.9, hair * 2.2)); fp.lineTo((-500, hair * 2.2)); fp.closePath()
    rest = pathops.op(pen_path, cut, pathops.PathOp.DIFFERENCE)
    rest = pathops.op(rest, foot, pathops.PathOp.DIFFERENCE)
    svg = SVGPathPen(None)
    rest.draw(TransformPen(svg, (sx, 0, 0, -1, x0, 0)))
    line = lambda y: (x0 + (m * y + c - hair * 0.5) * sx, y)
    return svg.getCommands(), line


def bez(p, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(*p))


def stroke(curves, widths, n=70):
    """A stroke along joined cubic curves; widths(t) gives its thickness, t over the whole stroke."""
    pts = []
    for i, c in enumerate(curves):
        for j in range(n + (1 if i == len(curves) - 1 else 0)):
            pts.append(bez(c, j / n))
    total = len(pts) - 1
    left, right = [], []
    for k, (x, y) in enumerate(pts):
        a, b = pts[max(k - 1, 0)], pts[min(k + 1, total)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths(k / total)
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    return poly(left + right[::-1])


def poly(pts):
    return 'M' + ' L'.join(f'{x:.1f} {-y:.1f}' for x, y in pts) + ' Z'


def build(style):
    path, sx, track = STYLES[style]
    font = TTFont(path)
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm
    cap = font['OS/2'].sCapHeight or 700
    stem, hair = measure(path, upm, cap)
    out, x, pos = [], 0, {}
    for ch in TEXT:
        g = cmap[ord(ch)]
        adv = font['hmtx'][g][0]
        pos[ch] = (x, adv)
        if ch not in ' A':
            pen = SVGPathPen(gs)
            gs[g].draw(TransformPen(pen, (sx, 0, 0, -1, x, 0)))
            out.append(pen.getCommands())
        x += adv * sx + track
    width = x - track
    # --- the A: the base letter keeps its full stroke and bar; its fine left
    # stroke is redrawn as one line that falls from the apex, flares past the
    # baseline and sweeps beneath the U, ending in a hairline ---
    ax = pos['A'][0]
    ux, uw = pos['U'][0], pos['U'][1] * sx
    rest, line = rebuilt_a(path, gs, cmap, upm, cap, stem, hair, sx, ax, ux, uw)
    out.append(rest)
    top, mid, low, foot = line(cap - 6), line(cap * 0.62), line(cap * 0.22), line(-cap * 0.02)
    top = (top[0] + hair * 0.5, top[1])
    flare = (foot[0] - (top[0] - foot[0]) * 0.10, foot[1])
    c1 = (top, mid, (low[0] + hair * 0.4, low[1]), flare)
    dx, dy = flare[0] - c1[2][0], flare[1] - c1[2][1]
    c2 = (flare, (flare[0] + dx * 0.55, flare[1] + dy * 0.55), (ux - uw * 0.30, -cap * 0.30), (ux + uw * 1.05, -cap * 0.10))
    def w(t):
        if t < 0.45:
            return hair * (1.05 + 0.9 * (t / 0.45) ** 2)
        u = (t - 0.45) / 0.55
        return hair * 1.95 + (stem * sx * 0.55 - hair * 1.95) * math.sin(math.pi * u ** 0.7) ** 1.2 - hair * 1.6 * u ** 3
    out.append(stroke([c1, c2], w))
    top, bottom = cap + 20, -cap * 0.32
    d = ' '.join(out)
    return (f'<svg class="wordmark-svg" viewBox="0 {-top:.0f} {width:.0f} {top - bottom:.0f}" role="img" '
            f'aria-label="Yvis Hausen" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="{d}"/></svg>')


if __name__ == '__main__':
    style = sys.argv[sys.argv.index('--style') + 1] if '--style' in sys.argv else CHOSEN
    svg = build(style)
    if '--preview' in sys.argv:
        open(sys.argv[sys.argv.index('--preview') + 1], 'w').write(svg)
    else:
        p = 'partials/header.html'
        s = open(p).read()
        new = re.sub(r'<!-- wordmark -->.*?<!-- /wordmark -->', lambda m: f'<!-- wordmark -->{svg}<!-- /wordmark -->', s, flags=re.S)
        assert '<!-- wordmark -->' in s, 'wordmark markers missing'
        open(p, 'w').write(new)
        print('wordmark', style, len(svg), 'bytes')
