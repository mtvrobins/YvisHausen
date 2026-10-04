"""One animated illustration per section page. Inserted after the first body
paragraph (or replaced in place on re-runs, between the PAGE-ILL markers)."""
import math, random, re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FG, C2, M1, M2, M3, M4, BG = '#F2F1EC', '#cfcec8', '#8A8A82', '#5C5C56', '#3A3A36', '#262624', '#0B0B0A'
I = '    '

def dr(d, dl, du=1.4, stroke=M2, w=1, extra=''):
    return f'<path class="dr" pathLength="100" style="--dl:{dl:.2f}s;--du:{du}s" d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'

def txt(x, y, s, cls='t', anchor='start', dl=None, extra=''):
    c = cls + (' fi' if dl is not None else '')
    st = f' style="--dl:{dl:.2f}s"' if dl is not None else ''
    return f'<text class="{c}"{st} x="{x}" y="{y}" text-anchor="{anchor}"{extra}>{s}</text>'

# ------------------------------------------------------------------ SOUND
def sound():
    random.seed(3)
    o = []
    o.append(dr('M64,44 L576,44', 0.1, 1.6, M3))
    for k in range(17):
        x = 64 + k * 32
        o.append(f'<line class="fi" style="--dl:{0.3 + k*0.03:.2f}s" x1="{x}" y1="44" x2="{x}" y2="{48 if k % 4 else 52}" stroke="{M3}"/>')
    for x, s, a in [(64, '20 HZ', 'start'), (192, '200', 'middle'), (320, '2K', 'middle'), (448, '8K', 'middle'), (576, '20K HZ', 'end')]:
        o.append(txt(x, 34, s, 't t-s', a, 0.6))
    for k, dl in enumerate([1.2, 2.6, 4.0]):
        o.append(f'<circle class="ripple" style="--dl:{dl}s;--k:3.6" cx="320" cy="150" r="34" fill="none" stroke="{M3}"/>')
    o.append(dr('M40,150 L600,150', 0.2, 1.8, M4))
    bars = []
    n = 76
    for k in range(n):
        x = 64 + k * (512 / (n - 1))
        e = math.exp(-((x - 320) / 150) ** 2)
        h = 8 + 88 * (0.25 + 0.75 * e) * random.uniform(0.55, 1.0)
        col = FG if e > 0.72 else C2 if e > 0.5 else M1 if e > 0.3 else M2
        d = random.uniform(0.9, 2.4)
        lo = random.uniform(0.18, 0.55)
        bars.append(f'<rect class="bar" style="--d:{d:.2f}s;--dl:{-random.uniform(0,2):.2f}s;--lo:{lo:.2f}" x="{x-1.2:.1f}" y="{150-h:.1f}" width="2.4" height="{2*h:.1f}" rx="1.2" fill="{col}"/>')
    o.append(f'<g class="fi" style="--dl:0.5s">' + ''.join(bars) + '</g>')
    o.append(f'<line class="scan" style="--dl:2.4s;--d:7s;--w:512px" x1="64" y1="56" x2="64" y2="244" stroke="{FG}" stroke-width="0.8" opacity="0"/>')
    for x, s, dl in [(150, 'RUNWAY', 1.6), (320, 'SCREEN', 1.8), (490, 'INSTALLATION', 2.0)]:
        o.append(f'<path class="pop" style="--dl:{dl}s" d="M{x},252 l3,3 l-3,3 l-3,-3 Z" fill="{FG}"/>')
        o.append(txt(x, 274, s, 't', 'middle', dl + 0.2))
    return o, 'FIG. — SOUND, SHAPED FOR SPACE'

# ------------------------------------------------------------------ VISUAL DIRECTION
def visual():
    o = []
    x0, y0, w, h = 96, 22, 172, 256
    o.append(f'<rect class="fi" x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{BG}" stroke="{M3}"/>')
    for k, (ax, ay, dx, dy) in enumerate([(x0, y0, -1, -1), (x0 + w, y0, 1, -1), (x0, y0 + h, -1, 1), (x0 + w, y0 + h, 1, 1)]):
        o.append(f'<path class="fi" style="--dl:{0.2+k*0.08:.2f}s" d="M{ax+dx*6},{ay} h{dx*10} M{ax},{ay+dy*6} v{dy*10}" stroke="{M2}" fill="none"/>')
    for k, x in enumerate([108, 139, 147, 178, 186, 217, 225, 256]):
        o.append(dr(f'M{x},34 L{x},266', 0.3 + k * 0.07, 1.2, M4, 0.8))
    for k, y in enumerate([125.5, 190, 228]):
        o.append(dr(f'M108,{y} L256,{y}', 0.8 + k * 0.1, 1.2, M4, 0.8))
    o.append(f'<rect class="fi" style="--dl:0.9s" x="108" y="34" width="148" height="91.5" fill="#111110"/>')
    for k, d in enumerate(['M199.5,34 L199.5,125.5', 'M199.5,90.5 L256,90.5', 'M221,90.5 L221,125.5', 'M199.5,104 L221,104']):
        o.append(dr(d, 1.2 + k * 0.15, 0.6, M3, 0.8))
    o.append(dr('M108,125.5 A91.5,91.5 0 0 1 199.5,34 A56.5,56.5 0 0 1 256,90.5 A35,35 0 0 1 221,125.5 A21.5,21.5 0 0 1 199.5,104 A13.5,13.5 0 0 1 213,90.5', 1.4, 2.4, FG, 1.1))
    o.append(f'<rect class="gx" style="--dl:2.2s;--du:1.1s" x="108" y="138" width="126" height="10" fill="{FG}"/>')
    o.append(f'<rect class="gx" style="--dl:2.35s;--du:1.1s" x="108" y="152" width="96" height="10" fill="{FG}"/>')
    for k in range(5):
        o.append(f'<rect class="gx" style="--dl:{2.6+k*0.08:.2f}s" x="108" y="{198+k*6}" width="{[70,64,70,52,60][k]}" height="2" fill="{M3}"/>')
        o.append(f'<rect class="gx" style="--dl:{2.7+k*0.08:.2f}s" x="186" y="{198+k*6}" width="{[70,58,66,70,40][k]}" height="2" fill="{M3}"/>')
    o.append(txt(108, 262, 'YH — 01', 't t-s', 'start', 2.9))
    o.append(f'<circle class="pop" style="--dl:3s" cx="250" cy="259" r="4" fill="none" stroke="{M1}"/>')
    o.append(txt(96, 294, 'GRID', 't', 'start', 1.0))
    # palette
    o.append(txt(320, 26, 'PALETTE', 't', 'start', 0.5))
    for k, col in enumerate([FG, C2, M1, M2, M3]):
        o.append(f'<rect class="pop" style="--dl:{0.8+k*0.12:.2f}s" x="{320+k*44}" y="34" width="36" height="36" fill="{col}"/>')
        o.append(txt(320 + k * 44, 82, f'0{k+1}', 't t-s', 'start', 1.2 + k * 0.1))
    # typography
    o.append(txt(320, 108, 'TYPOGRAPHY', 't', 'start', 1.4))
    o.append(f'<text class="t-serif fi" style="--dl:1.6s;font-size:86px" x="316" y="186" fill="{FG}">Aa</text>')
    for k, s in enumerate(['ABCDEFGHIJKLM', 'abcdefghijklm', '0123456789 &amp;']):
        o.append(f'<text class="t-serif fi" style="--dl:{1.9+k*0.15:.2f}s;font-size:12px;letter-spacing:.14em" x="444" y="{136+k*20}" fill="{M1 if k else C2}">{s}</text>')
    # pen tool curve
    o.append(txt(320, 214, 'FORM', 't', 'start', 2.2))
    o.append(dr('M322,272 C360,212 430,292 480,236 S566,214 604,228', 2.4, 1.8, FG, 1.2))
    for (ax, ay), (hx, hy) in [((322, 272), (360, 212)), ((480, 236), (440, 280)), ((604, 228), (566, 214))]:
        o.append(f'<g class="pop" style="--dl:3.4s"><line x1="{ax}" y1="{ay}" x2="{hx}" y2="{hy}" stroke="{M2}" stroke-width="0.8"/><circle cx="{hx}" cy="{hy}" r="2.2" fill="#000" stroke="{M1}"/><rect x="{ax-3}" y="{ay-3}" width="6" height="6" fill="#000" stroke="{FG}"/></g>')
    o.append(f'<line x1="480" y1="236" x2="520" y2="192" stroke="{M2}" stroke-width="0.8" class="fi" style="--dl:3.4s"/><circle class="pop" style="--dl:3.4s" cx="520" cy="192" r="2.2" fill="#000" stroke="{M1}"/>')
    return o, 'FIG. — GRID, TYPE, IMAGE'

# ------------------------------------------------------------------ SCENOGRAPHY
def sceno():
    o = []
    o.append('<defs>'
             '<radialGradient id="scDisc"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".30"/><stop offset=".55" stop-color="#F2F1EC" stop-opacity=".08"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient>'
             '<linearGradient id="scBeam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".16"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></linearGradient>'
             '<linearGradient id="scFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
             '<mask id="scRefl" maskUnits="userSpaceOnUse" x="0" y="232" width="640" height="70"><rect x="0" y="232" width="640" height="70" fill="url(#scFade)"/></mask>'
             '</defs>')
    VX, VY = 320, 150
    # the horizon and a polished floor running to the vanishing point
    o.append(dr('M40,232 L600,232', 0.1, 1.6, M3, 0.8))
    for i in range(-6, 7):
        x2 = VX + i * 48
        o.append(dr(f'M{VX + i * 9},232 L{x2},300', 0.4 + abs(i) * 0.05, 1.0, '#1A1A18', 0.7))
    # the back wall: a disc of light, breathing slowly
    o.append(f'<circle class="fi breathe" style="--dl:0.6s;--d:7s;--a:.6" cx="{VX}" cy="118" r="96" fill="url(#scDisc)"/>')
    o.append(dr(f'M{VX - 54},118 a54,54 0 1 0 108,0 a54,54 0 1 0 -108,0', 0.5, 2.2, M2, 0.8))
    o.append(dr(f'M{VX - 38},118 a38,38 0 1 0 76,0 a38,38 0 1 0 -76,0', 0.8, 2.0, M3, 0.6))
    # a corridor of arches, receding: you walk through the world
    arches = [(232, 236, 172, 1.0), (214, 170, 128, 1.3), (204, 120, 96, 1.6), (198, 84, 70, 1.9)]
    refl = []
    for k, (base, w, h, dl) in enumerate(arches):
        x0, x1 = VX - w / 2, VX + w / 2
        r = w / 2
        d = f'M{x0:.1f},{base} L{x0:.1f},{base - h + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x1:.1f},{base - h + r:.1f} L{x1:.1f},{base}'
        col = [FG, C2, M1, M2][k]
        o.append(dr(d, dl, 1.6, col, [1.3, 1.0, 0.8, 0.7][k]))
        refl.append(f'<path d="{d}" fill="none" stroke="{M2}" stroke-width="0.8"/>')
    o.append(f'<g class="fi" style="--dl:2.4s" mask="url(#scRefl)"><g transform="translate(0,464) scale(1,-1)" opacity=".45">{"".join(refl)}</g></g>')
    # two slender lights sweeping softly across the space
    for k, (x, r0, r1, d) in enumerate([(130, -10, 16, 7.5), (510, -16, 10, 8.5)]):
        o.append(f'<g class="sway" style="--ox:{x}px;--oy:20px;--r0:{r0}deg;--r1:{r1}deg;--d:{d}s;--dl:{-k * 2}s">'
                 f'<g class="fi" style="--dl:{2.2 + k * 0.2:.1f}s"><polygon points="{x - 2},22 {x + 2},22 {x + 60},232 {x - 60},232" fill="url(#scBeam)"/></g></g>')
        o.append(f'<path class="pop" style="--dl:{2.0 + k * 0.15:.2f}s" d="M{x - 5},14 L{x + 5},14 L{x + 3},22 L{x - 3},22 Z" fill="{FG}"/>')
    # a figure walks out through the arches towards you
    o.append('<g class="flow" style="--dl:3s"><g>'
             f'<circle cx="0" cy="-15" r="3" fill="{FG}"/><path d="M0,-12 L0,0 M0,-9 L-3.5,-3 M0,-9 L3.5,-3 M0,0 L-2.6,9 M0,0 L2.6,9" stroke="{FG}" stroke-width="1.2" stroke-linecap="round" fill="none"/>'
             '<animateTransform attributeName="transform" type="scale" values="0.45;1.5" dur="9s" repeatCount="indefinite"/>'
             '<animateMotion path="M320,190 L320,282" dur="9s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.85;1" dur="9s" repeatCount="indefinite"/></g></g>')
    o.append(txt(140, 10, 'LIGHT', 't t-s', 'middle', 2.2))
    o.append(txt(VX, 50, 'BACK WALL', 't t-s', 'middle', 1.0))
    o.append(txt(470, 266, 'RUNWAY', 't t-s', 'start', 2.6))
    return o, 'FIG. — A WORLD, BUILT TO BE WALKED THROUGH'

# ------------------------------------------------------------------ TALENT
def figure(x, kind, hair, stroke=C2, cls_dr=True, dl=0.0, w=0.9):
    """A tall fashion silhouette standing on the floor at y=262 (head top ~90)."""
    def P(d):
        c = f' class="dr" pathLength="100" style="--dl:{dl:.2f}s;--du:1.8s"' if cls_dr else ''
        return f'<path{c} d="{d}" fill="url(#tFig)" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'
    def L(d):
        c = f' class="dr" pathLength="100" style="--dl:{dl+0.3:.2f}s;--du:1.6s"' if cls_dr else ''
        return f'<path{c} d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
    X = lambda v: f'{x+v:g}'
    o = []
    if kind == 'gown':
        o.append(P(f'M{X(-2)},111 C{X(-6)},112 {X(-11)},113 {X(-12)},117 L{X(-10)},128 C{X(-8)},138 {X(-6)},144 {X(-6)},150 C{X(-9)},160 {X(-11)},170 {X(-10)},182 C{X(-10)},210 {X(-14)},240 {X(-21)},262 L{X(23)},262 C{X(14)},240 {X(10)},210 {X(10)},182 C{X(11)},170 {X(9)},160 {X(6)},150 C{X(6)},144 {X(8)},138 {X(10)},128 L{X(12)},117 C{X(11)},113 {X(6)},112 {X(2)},111 Z'))
        o.append(L(f'M{X(-12)},117 C{X(-15)},132 {X(-16)},150 {X(-14)},176 M{X(12)},117 C{X(18)},128 {X(20)},142 {X(9)},158'))
        o.append(L(f'M{X(4)},190 C{X(6)},214 {X(10)},240 {X(16)},262'))
    elif kind == 'suit':
        o.append(P(f'M{X(-2)},111 C{X(-8)},112 {X(-14)},113 {X(-14)},118 L{X(-12)},182 L{X(12)},182 L{X(14)},118 C{X(14)},113 {X(8)},112 {X(2)},111 Z'))
        o.append(P(f'M{X(-11)},182 L{X(-9)},261 L{X(-2)},261 L{X(-0.6)},194 L{X(0.6)},194 L{X(2)},261 L{X(9)},261 L{X(11)},182 Z'))
        o.append(L(f'M{X(-2)},111 L{X(0)},140 L{X(2)},111 M{X(-14)},118 L{X(-16)},178 M{X(14)},118 L{X(16)},178'))
    elif kind == 'slip':
        o.append(P(f'M{X(-2)},111 C{X(-6)},112 {X(-9)},113 {X(-10)},117 L{X(-8)},150 C{X(-10)},165 {X(-12)},185 {X(-13)},202 L{X(13)},202 C{X(12)},185 {X(10)},165 {X(8)},150 L{X(10)},117 C{X(9)},113 {X(6)},112 {X(2)},111 Z'))
        o.append(L(f'M{X(-5)},202 L{X(-6)},256 L{X(-10)},261 M{X(5)},202 C{X(7)},226 {X(9)},244 {X(10)},256 L{X(14)},260 M{X(-10)},117 L{X(-13)},150 L{X(-12)},176 M{X(10)},117 L{X(13)},150 L{X(12)},176'))
    elif kind == 'coat':
        o.append(P(f'M{X(-2)},111 C{X(-8)},112 {X(-14)},113 {X(-15)},118 L{X(-18)},234 L{X(18)},234 L{X(15)},118 C{X(14)},113 {X(8)},112 {X(2)},111 Z'))
        o.append(L(f'M{X(-15)},152 L{X(15)},152 M{X(0)},118 L{X(0)},234 M{X(-6)},234 L{X(-6)},260 M{X(6)},234 L{X(6)},260 M{X(-15)},118 L{X(-19)},196 M{X(15)},118 L{X(19)},196'))
    # head, neck and hair
    o.append(P(f'M{X(0)},91 C{X(4)},91 {X(5.8)},95 {X(5.8)},99 C{X(5.8)},104 {X(3.4)},107 {X(0)},107 C{X(-3.4)},107 {X(-5.8)},104 {X(-5.8)},99 C{X(-5.8)},95 {X(-4)},91 {X(0)},91 Z'))
    o.append(L(f'M{X(-1.8)},106 L{X(-2)},111 M{X(1.8)},106 L{X(2)},111'))
    if hair == 'bun':
        o.append(L(f'M{X(3)},91.5 m-3.2,0 a3.2,3.2 0 1 0 6.4,0 a3.2,3.2 0 1 0 -6.4,0'))
    elif hair == 'long':
        o.append(L(f'M{X(-5.8)},97 C{X(-8)},106 {X(-8)},116 {X(-9)},124 M{X(5.8)},97 C{X(8)},106 {X(8)},116 {X(9)},124'))
    elif hair == 'brim':
        o.append(L(f'M{X(-11)},94 L{X(11)},94 M{X(-5)},94 C{X(-5)},86 {X(5)},86 {X(5)},94'))
    return o

def talent():
    """Three portrait frames; the casting settles on one. Fine lines, quiet motion."""
    o = []
    o.append('<defs><radialGradient id="tGlow"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".16"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient>'
             '<linearGradient id="tFig" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151514"/><stop offset="1" stop-color="#0B0B0A"/></linearGradient></defs>')
    frames = [(200, 'coat', 'brim'), (320, 'gown', 'bun'), (440, 'suit', 'none')]
    for k, (x, kind, hair) in enumerate(frames):
        dl = 0.2 + k * 0.25
        frame = dr(f'M{x - 50},64 L{x + 50},64 L{x + 50},272 L{x - 50},272 Z', dl, 1.6, M3, 0.8)
        fig = ''.join(figure(x, kind, hair, stroke=C2 if k == 1 else M1, dl=dl + 0.4, w=0.8))
        num = txt(x, 54, f'{k + 2:02d}', 't t-s', 'middle', dl + 0.6)
        g = f'{frame}{fig}{num}'
        o.append(g if k == 1 else f'<g class="dim" style="--dl:3.6s">{g}</g>')
    # the chosen frame: a soft light behind, the frame drawn in white
    o.append(f'<g class="fi" style="--dl:3.6s"><ellipse class="breathe" style="--d:5s;--a:.5" cx="320" cy="170" rx="70" ry="110" fill="url(#tGlow)"/></g>')
    o.append(dr('M270,64 L370,64 L370,272 L270,272 Z', 3.7, 1.4, FG, 1))
    # the viewfinder closes in on her
    bx0, by0, bx1, by1 = 262, 56, 378, 280
    br = (f'M{bx0},{by0 + 14} L{bx0},{by0} L{bx0 + 14},{by0} M{bx1 - 14},{by0} L{bx1},{by0} L{bx1},{by0 + 14} '
          f'M{bx0},{by1 - 14} L{bx0},{by1} L{bx0 + 14},{by1} M{bx1 - 14},{by1} L{bx1},{by1} L{bx1},{by1 - 14}')
    o.append(f'<path class="vf" style="--dl:4.4s;--ox:320px;--oy:168px;--s0:1.7" d="{br}" fill="none" stroke="{FG}" stroke-width="1"/>')
    # quiet annotation beneath the chosen frame
    o.append(f'<text class="t-serif fi" style="--dl:5.6s;font-size:14px;font-style:italic" x="320" y="298" text-anchor="middle" fill="{FG}">N&#186; 03</text>')
    o.append(txt(320, 311, 'SELECTED', 't t-s', 'middle', 5.8))
    o.append(txt(320, 336, 'CASTING &#183; FASHION &#183; FILM', 't', 'middle', 1.0))
    return o, 'FIG. — CASTING, CONSIDERED'

# ------------------------------------------------------------------ PRIVATE ART
def private_art():
    """A work on the wall: framed, lit, labelled, and placed between the four
    parties an introduction brings together."""
    o = []
    o.append('<defs>'
             '<linearGradient id="paLamp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".20"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></linearGradient>'
             '<radialGradient id="paWash" cx=".5" cy=".35"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".10"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient>'
             '<linearGradient id="paGilt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#CBB68A"/><stop offset=".5" stop-color="#8E7A52"/><stop offset="1" stop-color="#CBB68A"/></linearGradient>'
             '</defs>')
    # rail, hook and wires
    o.append(dr('M150,30 L490,30', 0.1, 1.2, M2, 0.8))
    o.append(f'<circle class="pop" style="--dl:0.5s" cx="320" cy="30" r="2.4" fill="{FG}"/>')
    o.append(dr('M320,30 L276,74 M320,30 L364,74', 0.6, 0.8, M1, 0.6))
    # picture lamp washing the wall
    o.append(f'<g class="fi" style="--dl:2.4s"><polygon points="306,58 334,58 400,236 240,236" fill="url(#paLamp)"/><ellipse class="breathe" style="--d:6s;--a:.6" cx="320" cy="150" rx="130" ry="105" fill="url(#paWash)"/></g>')
    o.append(f'<g class="pop" style="--dl:2.2s"><rect x="302" y="52" width="36" height="5" rx="2.5" fill="{FG}"/><path d="M320,52 L320,44" stroke="{FG}"/></g>')
    # the frame: a gilt moulding with an inner slip and mat
    o.append(f'<g class="fi" style="--dl:0.8s"><rect x="250" y="70" width="140" height="166" fill="#0E0E0D" stroke="url(#paGilt)" stroke-width="5"/>'
             f'<rect x="258" y="78" width="124" height="150" fill="none" stroke="#6E5F42" stroke-width="0.8"/>'
             f'<rect x="266" y="86" width="108" height="134" fill="#141412" stroke="{M3}" stroke-width="0.6"/></g>')
    for k, (cx, cy) in enumerate([(250, 70), (390, 70), (250, 236), (390, 236)]):
        o.append(f'<path class="pop" style="--dl:{1.1 + k * 0.08:.2f}s" d="M{cx - 5},{cy} L{cx},{cy - 5} L{cx + 5},{cy} L{cx},{cy + 5} Z" fill="#CBB68A"/>')
    # the work itself: a horizon, a sun, one gesture
    o.append(dr('M276,176 C300,170 340,182 364,174', 1.4, 1.2, M1, 0.8))
    o.append(dr('M320,128 m-20,0 a20,20 0 1 0 40,0 a20,20 0 1 0 -40,0', 1.5, 1.6, FG, 1.1))
    o.append(dr('M282,204 C300,186 330,214 358,192', 1.8, 1.2, C2, 1.6))
    o.append(dr('M352,96 L352,206', 2.0, 0.9, M1, 2.4))
    # the museum label beside it
    o.append(f'<g class="fi" style="--dl:2.6s"><rect x="404" y="196" width="38" height="24" fill="#E8E5DD"/>'
             f'<rect x="408" y="201" width="22" height="1.8" fill="#3A3A36"/><rect x="408" y="206" width="16" height="1.4" fill="#8A8A82"/><rect x="408" y="211" width="26" height="1.4" fill="#8A8A82"/></g>')
    # the four parties, brought together around the work
    links = [('M110,80 C190,80 210,112 248,124', 'ARTISTS', 110, 80, 58),
             ('M530,80 C450,80 430,112 392,124', 'COLLECTORS', 530, 80, 58),
             ('M110,226 C190,226 210,196 248,184', 'INSTITUTIONS', 110, 226, 258),
             ('M530,226 C450,226 430,196 392,184', 'SPACES', 530, 226, 258)]
    for k, (d, lab, x, y, ly) in enumerate(links):
        o.append(dr(d, 3.0 + k * 0.15, 1.2, M2, 0.8))
        o.append(f'<g class="pop" style="--dl:{2.8 + k * 0.15:.2f}s"><circle cx="{x}" cy="{y}" r="13" fill="#000" stroke="{M1}"/><circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{M3}"/><circle cx="{x}" cy="{y}" r="2.6" fill="{FG}"/></g>')
        o.append(txt(x, ly, lab, 't t-b', 'middle', 3.0 + k * 0.15))
    o.append('<g class="flow" style="--dl:4.2s">')
    for k, (d, *_r) in enumerate(links):
        o.append(f'<circle r="1.8" fill="{FG}"><animateMotion dur="4.2s" begin="{k * 0.9:.1f}s" repeatCount="indefinite" path="{d}"/></circle>')
    o.append('</g>')
    return o, 'FIG. — CONSIDERED INTRODUCTIONS'

# ------------------------------------------------------------------ EVENT CURATION
def event():
    random.seed(5)
    o = []
    o.append(f'<text class="t-serif fi" style="--dl:0.1s;font-size:15px;font-style:italic" x="320" y="54" text-anchor="middle" fill="{C2}">A table for fourteen</text>')
    o.append(f'<rect class="fi" style="--dl:0.3s" x="96" y="116" width="448" height="68" rx="34" fill="{BG}" stroke="{M2}"/>')
    o.append(dr('M140,150 L500,150', 0.6, 1.4, M4, 0.8))
    xs = [150 + i * (340 / 6) for i in range(7)]
    k = 0
    for row, (py, cy, gy) in enumerate([(133, 102, 124), (167, 190, 176)]):
        for x in xs:
            dl = 0.8 + k * 0.1
            chair = f'<rect x="{x-12:.1f}" y="{cy-5}" width="24" height="10" rx="4" fill="none" stroke="{M3}"/>'
            plate = (f'<circle cx="{x:.1f}" cy="{py}" r="9" fill="#111110" stroke="{M1}"/><circle cx="{x:.1f}" cy="{py}" r="5.5" fill="none" stroke="{M3}"/>'
                     f'<line x1="{x-14:.1f}" y1="{py-6}" x2="{x-14:.1f}" y2="{py+6}" stroke="{M2}"/><line x1="{x+14:.1f}" y1="{py-6}" x2="{x+14:.1f}" y2="{py+6}" stroke="{M2}"/>'
                     f'<circle cx="{x+11:.1f}" cy="{py + (9 if row == 0 else -9)}" r="2.2" fill="none" stroke="{M2}"/>')
            o.append(f'<g class="fi" style="--dl:{dl-0.2:.2f}s">{chair}</g><g class="pop" style="--dl:{dl:.2f}s">{plate}</g>')
            k += 1
    for j, x in enumerate(range(170, 480, 38)):
        dl = 2.2 + j * 0.1
        if j % 2 == 0:
            o.append(f'<circle class="fi flicker" style="--dl:{dl:.1f}s;--d:{random.uniform(1.4,2.6):.2f}s;--a:.45" cx="{x}" cy="150" r="9" fill="{FG}" fill-opacity=".14"/>')
            o.append(f'<circle class="pop" style="--dl:{dl:.1f}s" cx="{x}" cy="150" r="2" fill="{FG}"/>')
        else:
            o.append(f'<g class="pop" style="--dl:{dl:.1f}s"><circle cx="{x-2.6}" cy="148" r="2.4" fill="{M1}"/><circle cx="{x+2.6}" cy="148.5" r="2.2" fill="{M2}"/><circle cx="{x}" cy="152.5" r="2.4" fill="{C2}"/></g>')
    o.append(f'<line class="fi" style="--dl:1.4s" x1="96" y1="250" x2="544" y2="250" stroke="{M3}"/>')
    o.append(f'<rect class="gx" style="--dl:1.8s;--du:3.2s" x="96" y="249.4" width="448" height="1.4" fill="{FG}"/>')
    for j, (x, lab, a) in enumerate([(96, 'FIRST IDEA', 'start'), (245, 'CONCEPT', 'middle'), (395, 'SETTING', 'middle'), (544, 'FINAL DETAIL', 'end')]):
        dl = 1.8 + j * 1.05
        o.append(f'<circle class="pop" style="--dl:{dl:.2f}s" cx="{x}" cy="250" r="3.2" fill="{FG}"/>')
        o.append(txt(x, 272, lab, 't', a, dl + 0.1))
    return o, 'FIG. — FROM FIRST IDEA TO FINAL DETAIL'

# ------------------------------------------------------------------ EXHIBITIONS
def exhibitions():
    """A measured floor plan: three rooms, works on the walls, plinths, doors,
    and a visitor walking the route as each work comes into view."""
    o = []
    o.append('<defs><pattern id="exHatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="#3A3A36" stroke-width="1"/></pattern>'
             '<linearGradient id="exCone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".16"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></linearGradient></defs>')
    # thick hatched walls (outer shell with the entrance gap on the left)
    walls = [(70, 36, 500, 6), (70, 248, 500, 6), (564, 36, 6, 218), (70, 36, 6, 92), (70, 168, 6, 86),
             (234, 42, 6, 66), (234, 178, 6, 70), (402, 42, 6, 96), (402, 202, 6, 46)]
    for k, (x, y, w, h) in enumerate(walls):
        o.append(f'<rect class="fi" style="--dl:{0.1 + k * 0.06:.2f}s" x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#exHatch)" stroke="{M1}" stroke-width="0.8"/>')
    # door swings
    for k, (d, dl) in enumerate([('M240,108 A30,30 0 0 1 270,138', 0.9), ('M408,138 A28,28 0 0 1 436,166', 1.0), ('M76,128 A24,24 0 0 0 100,152', 0.8)]):
        o.append(dr(d, dl, 0.6, M3, 0.7))
    # works on the walls: lit as the visitor reaches them
    works = [(110, 42, 40, 'h', 2.4), (176, 42, 40, 'h', 3.1), (150, 248, 46, 'h', 4.0), (268, 42, 52, 'h', 4.8), (344, 42, 40, 'h', 5.4),
             (296, 248, 60, 'h', 6.3), (446, 42, 40, 'h', 7.1), (510, 42, 36, 'h', 7.6), (564, 92, 46, 'v', 8.4), (564, 176, 44, 'v', 9.0), (470, 248, 60, 'h', 9.8)]
    for k, (x, y, L, ori, t) in enumerate(works):
        if ori == 'h':
            inner = y + 6 if y < 100 else y
            o.append(f'<rect class="pop" style="--dl:{1.3 + k * 0.07:.2f}s" x="{x}" y="{inner - 1.6 if y < 100 else y - 1.6}" width="{L}" height="3.2" fill="{FG}"/>')
            cone = (f'{x},{inner + 2} {x + L},{inner + 2} {x + L / 2 + 14},{inner + 46} {x + L / 2 - 14},{inner + 46}' if y < 100
                    else f'{x},{y - 2} {x + L},{y - 2} {x + L / 2 + 14},{y - 46} {x + L / 2 - 14},{y - 46}')
        else:
            o.append(f'<rect class="pop" style="--dl:{1.3 + k * 0.07:.2f}s" x="{x - 1.6}" y="{y}" width="3.2" height="{L}" fill="{FG}"/>')
            cone = f'{x - 2},{y} {x - 2},{y + L} {x - 46},{y + L / 2 + 14} {x - 46},{y + L / 2 - 14}'
        o.append(f'<polygon points="{cone}" fill="url(#exCone)" opacity="0"><animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{max(t - 0.6, 0) / 12:.3f};{t / 12:.3f};{min(t + 1.6, 12) / 12:.3f};1" dur="12s" begin="4.6s" repeatCount="indefinite"/></polygon>')
        o.append(txt((x + L / 2) if ori == 'h' else x - 10, (y - 6 if y < 100 else y + 14) if ori == 'h' else y + L / 2, f'{k + 1:02d}', 't t-s', 'middle', 1.6 + k * 0.05))
    # plinths with objects
    for k, (x, y, w, h, obj) in enumerate([(304, 132, 30, 30, 'circle'), (140, 196, 40, 12, 'line'), (470, 126, 44, 14, 'line'), (150, 100, 18, 18, 'diamond')]):
        g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#121211" stroke="{M1}" stroke-width="0.8"/>'
        if obj == 'circle':
            g += f'<circle cx="{x + w / 2}" cy="{y + h / 2}" r="7" fill="none" stroke="{C2}"/><circle cx="{x + w / 2}" cy="{y + h / 2}" r="2" fill="{C2}"/>'
        elif obj == 'diamond':
            g += f'<path d="M{x + w / 2},{y + 3} L{x + w - 3},{y + h / 2} L{x + w / 2},{y + h - 3} L{x + 3},{y + h / 2} Z" fill="none" stroke="{C2}"/>'
        else:
            g += f'<path d="M{x + 4},{y + h / 2} L{x + w - 4},{y + h / 2}" stroke="{C2}"/>'
        o.append(f'<g class="pop" style="--dl:{1.9 + k * 0.1:.2f}s">{g}</g>')
    for x, n, dl in [(155, 'I', 0.9), (321, 'II', 1.0), (486, 'III', 1.1)]:
        o.append(f'<text class="t-serif fi" style="--dl:{dl}s;font-size:18px" x="{x}" y="80" text-anchor="middle" fill="{M1}">{n}</text>')
    route = 'M28,148 C80,148 104,140 130,134 C176,124 210,150 214,176 C218,206 176,214 160,200 C140,180 196,150 254,146 C290,144 290,104 322,108 C356,112 370,176 340,190 C320,200 312,214 330,222 C360,232 380,170 420,172 C450,174 452,98 490,100 C536,102 540,150 534,170 C528,198 500,214 480,206'
    o.append(dr(route, 2.6, 3.8, M3, 0.9, ' stroke-dasharray="100"'))
    o.append(f'<g class="flow" style="--dl:4.6s"><g><circle r="8" fill="{FG}" fill-opacity=".09"/><circle r="2.8" fill="{FG}"/><animateMotion dur="12s" repeatCount="indefinite" path="{route}"/></g></g>')
    o.append(f'<path class="pop" style="--dl:0.6s" d="M30,142 L40,148 L30,154" fill="none" stroke="{FG}" stroke-width="1.2"/>')
    o.append(txt(26, 132, 'ENTRANCE', 't t-s', 'start', 0.7))
    o.append(f'<g class="fi" style="--dl:2.6s"><line x1="470" y1="276" x2="570" y2="276" stroke="{M1}"/><rect x="470" y="274" width="25" height="4" fill="{M1}"/><rect x="520" y="274" width="25" height="4" fill="{M1}"/><rect x="470" y="274" width="100" height="4" fill="none" stroke="{M1}" stroke-width="0.6"/></g>')
    for x, s_ in [(470, '0'), (520, '5'), (570, '10 M')]:
        o.append(txt(x, 292, s_, 't t-s', 'middle', 2.7))
    o.append(f'<g class="fi" style="--dl:2.8s"><circle cx="606" cy="62" r="12" fill="none" stroke="{M2}"/><circle cx="606" cy="62" r="8" fill="none" stroke="{M3}" stroke-dasharray="1 2"/><path d="M606,52 L610,66 L606,63 L602,66 Z" fill="{FG}"/></g>')
    o.append(txt(606, 88, 'N', 't', 'middle', 2.9))
    return o, 'FIG. — A PRESENTATION, PACED'

# ------------------------------------------------------------------ COLLECTORS
def collectors():
    random.seed(8)
    o = []
    o.append(txt(40, 24, 'SOURCED', 't t-b', 'start', 0.1))
    fills = [M3, M2, '#2A2A27', M4, M1]
    picks = {(0, 3): (420, 60, 80 / 30, 2.0), (2, 1): (344, 76, 44 / 30, 2.5), (3, 4): (526, 70, 48 / 30, 3.0)}
    k = 0
    for r in range(4):
        for c in range(5):
            x, y = 40 + c * 44, 40 + r * 44
            art = (f'<rect x="{x}" y="{y}" width="30" height="22" fill="#111110" stroke="#2E2E2B"'
                   + (f' class="lit" style="--dl:{picks[(r,c)][3]-0.6:.1f}s"' if (r, c) in picks else '') + '/>'
                   f'<rect x="{x+4}" y="{y+4}" width="22" height="14" fill="{random.choice(fills)}"/>'
                   + (f'<circle cx="{x+15}" cy="{y+11}" r="4" fill="none" stroke="{C2}" stroke-width="0.8"/>' if random.random() < .4 else
                      f'<path d="M{x+5},{y+16} L{x+12},{y+8} L{x+18},{y+13} L{x+25},{y+6}" fill="none" stroke="{C2}" stroke-width="0.8"/>'))
            o.append(f'<g class="fi" style="--dl:{0.2+k*0.04:.2f}s">{art}</g>')
            k += 1
    o.append('<g class="flow" style="--dl:0.8s"><g>'
             f'<circle r="18" fill="{FG}" fill-opacity=".05" stroke="{FG}"/><line x1="13" y1="13" x2="22" y2="22" stroke="{FG}" stroke-width="2" stroke-linecap="round"/>'
             '<animateMotion dur="8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.33;.66;1" keySplines=".45 0 .25 1;.45 0 .25 1;.45 0 .25 1" values="187,51;99,139;231,183;187,51"/></g></g>')
    # the private interior the works are placed in
    o.append(txt(300, 24, 'PLACED', 't t-b', 'start', 0.2))
    o.append(f'<rect class="fi" style="--dl:0.3s" x="300" y="34" width="300" height="196" fill="{BG}" stroke="{M3}"/>')
    o.append(dr('M282,230 L618,230', 0.5, 1.2, M2))
    o.append(dr('M300,222 L600,222', 0.6, 1.2, M4, 0.8))
    o.append(dr('M392,222 L392,196 C392,186 400,182 410,182 L500,182 C510,182 518,186 518,196 L518,222 M380,222 L380,202 C380,194 392,194 392,202 M530,222 L530,202 C530,194 518,194 518,202 M400,182 L400,170 C400,164 406,162 412,162 L498,162 C504,162 510,164 510,170 L510,182', 1.0, 1.8, M1, 1))
    o.append(dr('M572,222 L572,120 M560,120 L584,120 L578,104 L566,104 Z', 1.2, 1.2, M1, 1))
    for (r, c), (tx, ty, s, dl) in picks.items():
        x, y = 40 + c * 44, 40 + r * 44
        o.append(f'<rect class="fi" style="--dl:0.8s" x="{tx}" y="{ty}" width="{30*s:.1f}" height="{22*s:.1f}" fill="none" stroke="{M3}" stroke-dasharray="3 3"/>')
        o.append(f'<g class="fly" style="--dl:{dl}s;--tx:{tx-x}px;--ty:{ty-y}px;--s:{s:.3f}"><rect x="{x}" y="{y}" width="30" height="22" fill="#141413" stroke="{FG}" stroke-width="{1/s:.2f}"/>'
                 f'<rect x="{x+4}" y="{y+4}" width="22" height="14" fill="{M2}"/><circle cx="{x+15}" cy="{y+11}" r="4" fill="none" stroke="{FG}" stroke-width="{0.9/s:.2f}"/></g>')
    o.append(f'<ellipse class="flicker" style="--dl:4.4s;--a:0;--d:3s" cx="460" cy="60" rx="46" ry="6" fill="{FG}" fill-opacity=".08"/>')
    o.append(f'<line class="pop" style="--dl:4.2s" x1="440" y1="54" x2="480" y2="54" stroke="{FG}" stroke-width="1.6"/>')
    return o, 'FIG. — SOURCED, THEN PLACED'

# ------------------------------------------------------------------ ARTISTS
def artists():
    o = []
    for k, d in enumerate(['M120,284 L175,36', 'M230,284 L175,36', 'M175,36 L175,288', 'M134,250 L216,250']):
        o.append(dr(d, 0.1 + k * 0.12, 1.1, M2, 1.4))
    o.append(f'<g class="fi" style="--dl:0.5s"><rect x="106" y="58" width="138" height="172" fill="#0E0E0D" stroke="{M1}" stroke-width="1.2"/><rect x="98" y="230" width="154" height="6" fill="#141413" stroke="{M2}"/></g>')
    o.append(dr('M126,194 C150,112 200,214 224,96', 1.0, 1.7, FG, 9, ' opacity=".92"'))
    o.append(dr('M122,122 C158,100 190,146 228,118', 1.9, 1.3, M1, 5))
    o.append(dr('M196,108 m-16,0 a16,16 0 1 0 32,0 a16,16 0 1 0 -32,0', 2.4, 1.2, C2, 2.4))
    for k, (x, y, r) in enumerate([(140, 206, 2.2), (214, 186, 1.6), (150, 80, 1.8), (232, 212, 1.4), (120, 150, 1.2)]):
        o.append(f'<circle class="pop" style="--dl:{2.9+k*0.07:.2f}s" cx="{x}" cy="{y}" r="{r}" fill="{FG}"/>')
    o.append(f'<g class="fi" style="--dl:0.8s"><line x1="262" y1="232" x2="292" y2="168" stroke="{M1}" stroke-width="1.6" stroke-linecap="round"/><path d="M292,168 L296,158 L298,170 Z" fill="{FG}"/></g>')
    o.append(txt(175, 300, 'STUDIO', 't', 'middle', 0.6))
    ends = [(470, 70, 'PRIVATE COLLECTION'), (490, 150, 'CREATIVE SPACE'), (470, 230, 'INSTITUTION')]
    paths = [f'M244,144 C340,144 380,{y} {x-16},{y}' for x, y, _ in ends]
    for k, p in enumerate(paths):
        o.append(dr(p, 3.0 + k * 0.2, 1.3, M2, 1))
    for k, (x, y, lab) in enumerate(ends):
        dl = 3.8 + k * 0.2
        o.append(f'<g class="pop" style="--dl:{dl:.1f}s"><rect x="{x-14}" y="{y-11}" width="28" height="22" fill="#000" stroke="{FG}"/><rect x="{x-9}" y="{y-6}" width="18" height="12" fill="{M2}"/></g>')
        o.append(txt(x + 22, y + 3, lab, 't t-b', 'start', dl + 0.2))
    o.append('<g class="flow" style="--dl:4.4s">')
    for k, p in enumerate(paths):
        for b in (0, 1.6):
            o.append(f'<circle r="2" fill="{FG}"><animateMotion dur="3.2s" begin="{b + k*0.5:.1f}s" repeatCount="indefinite" path="{p}"/></circle>')
    o.append('</g>')
    return o, 'FIG. — FROM STUDIO TO PLACEMENT'

PAGES = {
    'sound.html': sound, 'visual-direction.html': visual, 'scenography.html': sceno,
    'talent-representation.html': talent, 'private-art.html': private_art, 'event-curation.html': event,
    'exhibitions.html': exhibitions, 'collectors.html': collectors, 'artists.html': artists,
}
VH = {'collectors.html': 248, 'talent-representation.html': 344}
for page, fn in PAGES.items():
    parts, cap = fn()
    vh = VH.get(page, 300)
    svg = '\n'.join(f'{I}  {p}' for p in parts)
    fig = (f'<!-- PAGE-ILL -->\n{I}<figure class="page-ill" aria-hidden="true">\n{I}  <svg viewBox="0 0 640 {vh}" xmlns="http://www.w3.org/2000/svg">\n'
           f'{svg}\n{I}  </svg>\n{I}  <figcaption>{cap}</figcaption>\n{I}</figure>\n{I}<!-- /PAGE-ILL -->')
    s = open(page).read()
    if '<!-- PAGE-ILL -->' in s:
        s = re.sub(r'<!-- PAGE-ILL -->.*?<!-- /PAGE-ILL -->', lambda m: fig, s, flags=re.S)
    else:
        m = re.search(r'\n(\s*)<p[^>]*>.*?</p>\n', s, re.S)
        assert m, page
        s = s[:m.end()] + m.group(1) + fig + '\n' + s[m.end():]
    open(page, 'w').write(s)
    print(page, len(fig))
