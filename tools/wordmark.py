"""Draws the YVIS HAUSEN wordmark as an SVG (original artwork).

Letters start from Italiana (SIL Open Font License, tools/fonts/Italiana-OFL.txt);
the sweeping stroke from the A beneath the U is drawn here. Writes the SVG
into partials/header.html between <!-- wordmark --> markers.

    python3 tools/wordmark.py [--preview out.svg]
"""
import math, os, re, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
font = TTFont('tools/fonts/Italiana-Regular.ttf')
glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
TEXT, TRACK = 'YVIS HAUSEN', 120          # tracking in font units (0.12em)
TOP, BOTTOM = 720, -175                    # vertical extent incl. the sweep

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))

def sweep(curve, width, n=90):
    """A tapered stroke along a cubic curve: hairline at both ends, fuller in the middle."""
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(*curve, t)
        x2, y2 = bez(*curve, min(t + 1e-3, 1)) if t < 1 else (x, y)
        if t == 1:
            xa, ya = bez(*curve, t - 1e-3); dx, dy = x - xa, y - ya
        else:
            dx, dy = x2 - x, y2 - y
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = width * (math.sin(math.pi * t ** 0.8) ** 1.4) + 3   # swelling stroke, fine tips
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    pts = left + right[::-1]
    return 'M' + ' L'.join(f'{x:.1f} {-y:.1f}' for x, y in pts) + ' Z'

paths, x = [], 0
pos = {}
for ch in TEXT:
    g = cmap[ord(ch)]
    pos.setdefault(ch, x)
    if ch != ' ':
        pen = SVGPathPen(glyphs)
        glyphs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        paths.append(pen.getCommands())
    x += font['hmtx'][g][0] + TRACK
width = x - TRACK
ax = pos['A']; ux = pos['U']
# the A's left foot runs on, dips under the baseline and sweeps beneath the U
curve = ((ax + 44, 6), (ax + 4, -100), (ux - 90, -196), (ux + 700, -50))
paths.append(sweep(curve, 38))
d = ' '.join(paths)
svg = (f'<svg class="wordmark-svg" viewBox="0 {-TOP} {width} {TOP - BOTTOM}" role="img" aria-label="Yvis Hausen" '
       f'xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="{d}"/></svg>')

if '--preview' in sys.argv:
    open(sys.argv[sys.argv.index('--preview') + 1], 'w').write(svg)
else:
    p = 'partials/header.html'
    s = open(p).read()
    new = re.sub(r'<!-- wordmark -->.*?<!-- /wordmark -->', lambda m: f'<!-- wordmark -->{svg}<!-- /wordmark -->', s, flags=re.S)
    assert new != s or svg in s, 'wordmark markers missing'
    open(p, 'w').write(new)
    print('wordmark', len(svg), 'bytes')
