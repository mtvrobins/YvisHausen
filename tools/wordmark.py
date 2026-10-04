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
TAIL_END = 0.62   # where the tail finishes, as a share of the U's width
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


def tailed_a(path, gs, cmap, upm, cap, stem, hair, sx, x0):
    """The base A with the foot of its full (right) stroke removed. Returns the
    path data, plus the centre line, direction and width of that stroke where
    the tail takes over."""
    px, fx, fy, toRow, (w, h) = raster(path, 'A', upm)
    rows = []
    for yy in range(int(cap * 0.42), int(cap * 0.80), 6):
        r = runs_at(px, w, toRow(yy))
        if len(r) >= 2: rows.append((yy, fx(r[-1][0]), fx(r[-1][1])))
    n = len(rows)
    def fit(vals):
        my = sum(y for y, _ in vals) / n; mv = sum(v for _, v in vals) / n
        m = sum((v - mv) * (y - my) for y, v in vals) / sum((y - my) ** 2 for y, _ in vals)
        return m, mv - m * my
    mi, ci = fit([(y, l) for y, l, _ in rows])        # inner edge of the full stroke
    mo, co = fit([(y, r) for y, _, r in rows])        # outer edge
    # where the tail begins: just under the bar
    bar = [yy for yy in range(int(cap * 0.12), int(cap * 0.5), 3) if len(runs_at(px, w, toRow(yy))) == 1]
    y0 = (min(bar) if bar else cap * 0.3) - 30
    glyph = pathops.Path()
    gs[cmap[ord('A')]].draw(glyph.getPen())
    cut = pathops.Path(); cp = cut.getPen()
    yl = cap * 0.12
    cp.moveTo((mi * y0 + ci - 2, y0)); cp.lineTo((upm * 2, y0)); cp.lineTo((upm * 2, -400))
    cp.lineTo((mi * yl + ci - 90, -400)); cp.lineTo((mi * yl + ci - 90, yl - 20)); cp.lineTo((mi * yl + ci - 2, yl)); cp.closePath()
    rest = pathops.op(glyph, cut, pathops.PathOp.DIFFERENCE)
    svg = SVGPathPen(None)
    rest.draw(TransformPen(svg, (sx, 0, 0, -1, x0, 0)))
    ys = y0 + 30  # start a little inside the kept stroke, so the two overlap
    cx = ((mi * ys + ci) + (mo * ys + co)) / 2
    m = (mi + mo) / 2                                  # dx per dy along the stroke
    dirx, diry = -m * sx, -1.0                         # heading down the stroke
    L = math.hypot(dirx, diry); dirx, diry = dirx / L, diry / L
    width_h = ((mo * ys + co) - (mi * ys + ci)) * sx
    width = width_h / math.hypot(1, m * sx)          # measured across the stroke
    return svg.getCommands(), (x0 + cx * sx, ys), (dirx, diry), width, y0


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
    # --- the A: its full stroke does not stop at the baseline; it carries on,
    # curving down and round beneath the U, and thins to a hairline ---
    ax = pos['A'][0]
    ux, uw = pos['U'][0], pos['U'][1] * sx
    rest, p0, (dx, dy), sw, y0 = tailed_a(path, gs, cmap, upm, cap, stem, hair, sx, ax)
    out.append(rest)
    k = cap * 0.30
    end = (ux + uw * TAIL_END, -cap * 0.17)
    c = (p0, (p0[0] + dx * k, p0[1] + dy * k), (p0[0] + dx * k * 1.15 + uw * 0.10, -cap * 0.21), end)
    def w(t):
        f = min(1, max(0, (t - 0.18) / 0.82))
        return sw * (1 - f * f * (3 - 2 * f)) ** 1.05 + hair * 0.55
    out.append(stroke([c], w, n=120))
    top, bottom = cap + 20, -cap * 0.26
    # letters in one path; the tail on its own, so the overlap never cancels out
    d = ' '.join(out[:-1])
    return (f'<svg class="wordmark-svg" viewBox="0 {-top:.0f} {width:.0f} {top - bottom:.0f}" role="img" '
            f'aria-label="Yvis Hausen" xmlns="http://www.w3.org/2000/svg" fill="currentColor"><path d="{d}"/><path d="{out[-1]}"/></svg>')


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
