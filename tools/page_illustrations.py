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
    o.append('<defs><linearGradient id="scCone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".22"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></linearGradient>'
             '<radialGradient id="scPool"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".18"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient></defs>')
    # room in one-point perspective
    o.append(f'<rect class="fi" x="230" y="70" width="180" height="110" fill="{BG}" stroke="{M2}"/>')
    for k, d in enumerate(['M230,70 L40,8', 'M410,70 L600,8', 'M230,180 L60,292', 'M410,180 L580,292']):
        o.append(dr(d, 0.1 + k * 0.1, 1.2, M2))
    o.append(dr('M60,292 L580,292', 0.5, 1.2, M2))
    for i in range(1, 8):
        o.append(dr(f'M{230+i*22.5},180 L{60+i*65},292', 0.7 + i * 0.05, 1.0, '#1C1C1A', 0.8))
    for k, t in enumerate([0.14, 0.34, 0.62]):
        y = 180 + t * 112
        xl, xr = 230 - t * 170, 410 + t * 170
        o.append(dr(f'M{xl:.1f},{y:.1f} L{xr:.1f},{y:.1f}', 0.9 + k * 0.1, 1.0, '#1C1C1A', 0.8))
    o.append(f'<polygon class="fi" style="--dl:1.2s" points="305,180 335,180 372,292 268,292" fill="#121211" stroke="{M2}" stroke-width="0.8"/>')
    # back wall screen
    o.append(f'<g class="fi" style="--dl:1.0s"><rect x="268" y="88" width="104" height="64" fill="#0E0E0D" stroke="{M1}"/>'
             f'<path d="M276,140 L300,112 L318,128 L334,114 L364,140" fill="none" stroke="{M3}"/><circle cx="350" cy="102" r="5" fill="none" stroke="{M3}"/></g>')
    # plinths with objects
    o.append(f'<g class="fi" style="--dl:1.4s"><path d="M124,238 L162,238 L172,230 L134,230 Z" fill="#141413" stroke="{M2}" stroke-width="0.8"/><rect x="124" y="238" width="38" height="36" fill="#0E0E0D" stroke="{M2}" stroke-width="0.8"/><path d="M162,238 L172,230 L172,264 L162,274 Z" fill="#0A0A0A" stroke="{M2}" stroke-width="0.8"/><circle cx="148" cy="220" r="10" fill="none" stroke="{C2}"/></g>')
    o.append(f'<g class="fi" style="--dl:1.5s"><path d="M478,238 L516,238 L506,230 L468,230 Z" fill="#141413" stroke="{M2}" stroke-width="0.8"/><rect x="478" y="238" width="38" height="36" fill="#0E0E0D" stroke="{M2}" stroke-width="0.8"/><path d="M478,238 L468,230 L468,264 L478,274 Z" fill="#0A0A0A" stroke="{M2}" stroke-width="0.8"/><path d="M490,230 C484,214 490,200 494,194 C498,200 504,214 498,230 Z" fill="none" stroke="{C2}"/></g>')
    # truss and swaying lights
    o.append(dr('M150,34 L490,34', 0.4, 1.2, M1, 1.2))
    for k, (x, r0, r1, d) in enumerate([(200, -4, 14, 5.2), (320, -9, 9, 6.4), (440, -14, 4, 5.8)]):
        o.append(f'<g class="sway" style="--ox:{x}px;--oy:38px;--r0:{r0}deg;--r1:{r1}deg;--d:{d}s;--dl:{-k*1.3}s">'
                 f'<g class="fi" style="--dl:{1.8+k*0.2:.1f}s"><polygon points="{x-3},41 {x+3},41 {x+46},246 {x-46},246" fill="url(#scCone)"/>'
                 f'<ellipse cx="{x}" cy="248" rx="54" ry="10" fill="url(#scPool)"/></g></g>')
        o.append(f'<path class="pop" style="--dl:{1.6+k*0.15:.2f}s" d="M{x-6},34 L{x+6},34 L{x+4},42 L{x-4},42 Z" fill="{FG}"/>')
    # figure walking the runway
    o.append('<g class="flow" style="--dl:2.6s"><g>'
             f'<circle cx="0" cy="-15" r="3" fill="{FG}"/><path d="M0,-12 L0,0 M0,-9 L-4,-3 M0,-9 L4,-3 M0,0 L-3,9 M0,0 L3,9" stroke="{FG}" stroke-width="1.3" stroke-linecap="round" fill="none"/>'
             '<animateTransform attributeName="transform" type="scale" values="0.55;1.35" dur="7s" repeatCount="indefinite"/>'
             '<animateMotion path="M320,176 L320,268" dur="7s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.85;1" dur="7s" repeatCount="indefinite"/></g></g>')
    o.append(txt(496, 30, 'LIGHT', 't t-s', 'start', 1.6))
    o.append(txt(320, 64, 'BACK WALL', 't t-s', 'middle', 1.1))
    o.append(txt(380, 288, 'RUNWAY', 't t-s', 'start', 1.3))
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
    o = []
    CH = '#D9CCAE'   # champagne, used only for the chosen one
    o.append('<defs>'
             '<linearGradient id="tFig" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E1E1C"/><stop offset="1" stop-color="#0B0B0A"/></linearGradient>'
             '<linearGradient id="tCone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".26"/><stop offset=".85" stop-color="#F2F1EC" stop-opacity=".05"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></linearGradient>'
             '<radialGradient id="tPool"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".32"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="tHalo"><stop offset="0" stop-color="{CH}" stop-opacity=".22"/><stop offset="1" stop-color="{CH}" stop-opacity="0"/></radialGradient>'
             '<radialGradient id="tBack" cx=".5" cy=".75" r=".6"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".06"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient>'
             '<linearGradient id="tFloor" x1="0" x2="1"><stop offset="0" stop-color="#F2F1EC" stop-opacity="0"/><stop offset=".5" stop-color="#F2F1EC" stop-opacity=".35"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></linearGradient>'
             '<linearGradient id="tReflG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
             '<mask id="tRefl" maskUnits="userSpaceOnUse" x="0" y="262" width="640" height="60"><rect x="0" y="262" width="640" height="60" fill="url(#tReflG)"/></mask>'
             '</defs>')
    # the studio: cyclorama glow, glossy floor, height rule
    o.append('<rect class="fi" x="0" y="40" width="640" height="240" fill="url(#tBack)"/>')
    o.append('<rect class="fi" style="--dl:.2s" x="40" y="261.5" width="560" height="1" fill="url(#tFloor)"/>')
    o.append(dr('M58,90 L58,262', 0.3, 1.6, M3, 0.8))
    for k in range(19):
        y = 262 - k * 9.55
        o.append(f'<line class="fi" style="--dl:{0.4+k*0.04:.2f}s" x1="58" y1="{y:.1f}" x2="{62 if k % 4 else 66}" y2="{y:.1f}" stroke="{M3}" stroke-width="0.8"/>')
    for k, cm in enumerate([180, 140, 100, 60, 20]):
        y = 262 - cm * 0.955
        o.append(txt(70, y + 2.2, str(cm), 't t-s', 'start', 0.6 + k * 0.05))
    o.append(txt(58, 80, 'CM', 't t-s', 'middle', 0.5))
    # the lineup
    line = [(152, 'coat', 'brim'), (236, 'slip', 'long'), (320, 'gown', 'bun'), (404, 'suit', 'none'), (488, 'slip', 'bun')]
    chosen = 2
    refl_parts = []
    for k, (x, kind, hair) in enumerate(line):
        dl = 0.6 + k * 0.18
        parts = ''.join(figure(x, kind, hair, dl=dl))
        num = txt(x, 74, f'{k+1:02d}', 't t-s', 'middle', dl + 0.6)
        g = f'<g class="fi" style="--dl:{dl:.2f}s">{parts}</g>{num}'
        o.append(g if k == chosen else f'<g class="dim" style="--dl:7.6s">{g}</g>')
        refl_parts.append(''.join(figure(x, kind, hair, stroke=M2, cls_dr=False)))
    # glossy floor reflection of the lineup
    o.append(f'<g class="fi" style="--dl:1.4s" mask="url(#tRefl)"><g transform="translate(0,524) scale(1,-1)" opacity=".5">{"".join(refl_parts)}</g></g>')
    # the spotlight that walks the line and settles on the chosen one
    o.append('<g class="tspot">'
             '<polygon points="-3,24 3,24 54,262 -54,262" fill="url(#tCone)"/><path d="M-6,16 L6,16 L4,24 L-4,24 Z" fill="#F2F1EC" opacity=".85"/>'
             '<ellipse cx="0" cy="263" rx="64" ry="9" fill="url(#tPool)"/></g>')
    # chosen: champagne halo and a lit outline drawn over her
    o.append(f'<g class="fi" style="--dl:7.6s"><ellipse class="flicker" style="--d:3.4s;--a:.55" cx="320" cy="176" rx="46" ry="98" fill="url(#tHalo)"/></g>')
    o.append(f'<g class="fi" style="--dl:7.7s">' + ''.join(figure(320, 'gown', 'bun', stroke=FG, cls_dr=False, w=1.1)) + '</g>')
    o.append(txt(320, 74, '03', 't t-b t-s', 'middle', 7.7))
    # dust drifting in the beam once it settles
    motes = []
    for k, (mx, my, dx, dy, d) in enumerate([(306, 120, 6, -30, 7), (330, 160, -8, -26, 9), (316, 210, 5, -34, 8), (338, 110, -4, -20, 6.5), (302, 180, 9, -28, 10), (324, 236, -6, -30, 7.5)]):
        motes.append(f'<circle r="{0.7 + (k % 3) * 0.25:.2f}" fill="{FG}" opacity=".6"><animateMotion dur="{d}s" repeatCount="indefinite" path="M{mx},{my} q{dx},{dy/2} {dx/2},{dy}"/>'
                     f'<animate attributeName="opacity" values="0;.7;0" dur="{d}s" repeatCount="indefinite"/></circle>')
    o.append(f'<g class="flow" style="--dl:8s">{"".join(motes)}</g>')
    # viewfinder closing in
    bx0, by0, bx1, by1 = 288, 82, 352, 270
    br = (f'M{bx0},{by0+12} L{bx0},{by0} L{bx0+12},{by0} M{bx1-12},{by0} L{bx1},{by0} L{bx1},{by0+12} '
          f'M{bx0},{by1-12} L{bx0},{by1} L{bx0+12},{by1} M{bx1-12},{by1} L{bx1},{by1} L{bx1},{by1-12} '
          f'M316,176 L324,176 M320,172 L320,180')
    o.append(f'<path class="tvf" d="{br}" fill="none" stroke="{FG}" stroke-width="1"/>')
    # the flash, then a polaroid slides out and develops
    o.append(f'<rect class="tflash" x="0" y="20" width="640" height="290" fill="{FG}"/>')
    px, py = 548, 132
    mini = ''.join(figure(320, 'gown', 'bun', stroke=C2, cls_dr=False, w=2.4))
    o.append(f'<g class="tpola">'
             f'<rect x="{px}" y="{py}" width="68" height="92" fill="#ECE9E1"/>'
             f'<rect x="{px+6}" y="{py+6}" width="56" height="58" fill="#0D0D0C"/>'
             f'<g transform="translate({px+34},{py+36}) scale(.3) translate(-320,-176)">{mini}</g>'
             f'<rect class="tdev" x="{px+6}" y="{py+6}" width="56" height="58" fill="#DCD8CE"/>'
             f'<text x="{px+9}" y="{py+77}" style="font:italic 9px var(--serif);fill:#3A3A36">N&#186; 03</text>'
             f'<text x="{px+9}" y="{py+86}" style="font:500 4.4px var(--sans);letter-spacing:.24em;fill:#5C5C56">SELECTED</text>'
             f'</g>')
    o.append(txt(320, 304, 'CASTING &#183; FASHION &#183; FILM', 't', 'middle', 1.0))
    return o, 'FIG. — CASTING, CONSIDERED'

# ------------------------------------------------------------------ PRIVATE ART
def private_art():
    o = []
    o.append('<defs><radialGradient id="paGlow"><stop offset="0" stop-color="#F2F1EC" stop-opacity=".12"/><stop offset="1" stop-color="#F2F1EC" stop-opacity="0"/></radialGradient></defs>')
    o.append('<ellipse class="fi" style="--dl:1.6s" cx="320" cy="140" rx="120" ry="100" fill="url(#paGlow)"/>')
    links = [('M110,80 C200,80 220,114 266,124', 'M530,80 C440,80 420,114 374,124'),
             ('M110,224 C200,224 220,190 266,176', 'M530,224 C440,224 420,190 374,176')]
    paths = [p for pair in links for p in pair]
    for k, p in enumerate(paths):
        o.append(dr(p, 1.4 + k * 0.15, 1.2, M2, 1))
    for k, p in enumerate(['M96,62 C200,6 440,6 544,62', 'M96,242 C200,298 440,298 544,242']):
        o.append(f'<path class="fi" style="--dl:{2.2+k*0.2:.1f}s" d="{p}" fill="none" stroke="{M3}" stroke-dasharray="2 5"/>')
    o.append(dr('M320,36 L286,70 M320,36 L354,70', 0.2, 0.9, M1, 0.8))
    o.append(f'<circle class="pop" style="--dl:0.1s" cx="320" cy="36" r="2" fill="{FG}"/>')
    o.append(f'<g class="fi" style="--dl:0.4s"><rect x="262" y="70" width="116" height="146" fill="#0E0E0D" stroke="{M1}" stroke-width="1.4"/><rect x="272" y="80" width="96" height="126" fill="#151513" stroke="{M3}"/></g>')
    o.append(dr('M320,118 m-24,0 a24,24 0 1 0 48,0 a24,24 0 1 0 -48,0', 0.9, 1.6, FG, 1.2))
    o.append(dr('M282,186 C300,160 326,196 358,168', 1.3, 1.3, C2, 1))
    o.append(dr('M346,90 L346,196', 1.5, 1.0, M1, 2.6))
    o.append(f'<circle class="pop" style="--dl:2s" cx="298" cy="100" r="3" fill="{FG}"/>')
    for k, (x, y, lab, ly) in enumerate([(96, 80, 'ARTISTS', 58), (544, 80, 'COLLECTORS', 58), (96, 224, 'INSTITUTIONS', 256), (544, 224, 'SPACES', 256)]):
        o.append(f'<g class="pop" style="--dl:{1.0+k*0.15:.2f}s"><circle cx="{x}" cy="{y}" r="14" fill="#000" stroke="{FG}"/><circle cx="{x}" cy="{y}" r="3" fill="{FG}"/></g>')
        o.append(f'<circle class="ripple" style="--dl:{2.4+k*0.9:.1f}s;--k:2.6;--d:5s" cx="{x}" cy="{y}" r="14" fill="none" stroke="{M2}"/>')
        o.append(txt(x, ly, lab, 't t-b', 'middle', 1.3 + k * 0.15))
    o.append('<g class="flow" style="--dl:2.8s">')
    for k, p in enumerate(paths):
        for b in (0, 1.9):
            o.append(f'<circle r="2" fill="{FG}"><animateMotion dur="3.8s" begin="{b + k*0.45:.2f}s" repeatCount="indefinite" path="{p}"/></circle>')
    for k, p in enumerate(['M96,62 C200,6 440,6 544,62', 'M544,242 C440,298 200,298 96,242']):
        o.append(f'<circle r="1.6" fill="{M1}"><animateMotion dur="6s" begin="{k*1.5}s" repeatCount="indefinite" path="{p}"/></circle>')
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
    o = []
    o.append(dr('M70,128 L70,40 L570,40 L570,250 L70,250 L70,166', 0.1, 2.0, M1, 2))
    for k, d in enumerate(['M236,40 L236,112', 'M236,176 L236,250', 'M404,40 L404,142', 'M404,204 L404,250']):
        o.append(dr(d, 0.8 + k * 0.12, 0.8, M1, 2))
    for k, (x1, y1, x2, y2) in enumerate([(100, 40, 140, 40), (170, 40, 210, 40), (98, 250, 150, 250), (260, 40, 300, 40), (330, 40, 380, 40),
                                          (270, 250, 370, 250), (430, 40, 480, 40), (505, 40, 545, 40), (570, 90, 570, 140), (570, 170, 570, 220),
                                          (440, 250, 540, 250), (236, 190, 236, 236), (404, 58, 404, 120)]):
        o.append(f'<line class="pop" style="--dl:{1.4+k*0.09:.2f}s" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{FG}" stroke-width="3.2"/>')
    o.append(f'<g class="pop" style="--dl:1.9s"><rect x="308" y="132" width="24" height="24" fill="#141413" stroke="{M1}"/><circle cx="320" cy="144" r="5" fill="none" stroke="{C2}"/></g>')
    o.append(f'<g class="pop" style="--dl:2.0s"><rect x="140" y="210" width="42" height="10" fill="none" stroke="{M2}"/></g>')
    o.append(f'<g class="pop" style="--dl:2.1s"><rect x="466" y="136" width="44" height="12" fill="none" stroke="{M2}"/></g>')
    for x, n, dl in [(153, 'I', 0.9), (320, 'II', 1.0), (487, 'III', 1.1)]:
        o.append(f'<text class="t-serif fi" style="--dl:{dl}s;font-size:16px" x="{x}" y="74" text-anchor="middle" fill="{M1}">{n}</text>')
    route = 'M30,147 C90,147 108,92 150,96 C200,100 206,178 160,190 C120,200 112,150 170,146 L236,144 C282,144 280,96 320,98 C366,100 366,196 324,196 C290,196 330,172 404,173 C452,174 446,88 496,94 C546,100 540,200 498,204 C470,206 466,186 470,176'
    o.append(dr(route, 2.2, 3.6, M2, 1, ' stroke-dasharray="100"'))
    o.append('<g class="flow" style="--dl:4.6s">')
    for b in (0, 3.5):
        o.append(f'<g><circle r="7" fill="{FG}" fill-opacity=".1"/><circle r="2.8" fill="{FG}"/><animateMotion dur="11s" begin="{b}s" repeatCount="indefinite" path="{route}"/></g>')
    o.append('</g>')
    o.append(f'<path class="pop" style="--dl:0.6s" d="M34,141 L44,147 L34,153" fill="none" stroke="{FG}" stroke-width="1.2"/>')
    o.append(txt(30, 132, 'ENTRANCE', 't t-s', 'start', 0.7))
    o.append(f'<g class="fi" style="--dl:2.6s"><line x1="470" y1="272" x2="570" y2="272" stroke="{M1}"/><line x1="470" y1="268" x2="470" y2="276" stroke="{M1}"/><line x1="520" y1="269" x2="520" y2="275" stroke="{M1}"/><line x1="570" y1="268" x2="570" y2="276" stroke="{M1}"/></g>')
    for x, s in [(470, '0'), (520, '5'), (570, '10 M')]:
        o.append(txt(x, 288, s, 't t-s', 'middle', 2.7))
    o.append(f'<g class="fi" style="--dl:2.8s"><circle cx="604" cy="64" r="11" fill="none" stroke="{M2}"/><path d="M604,55 L608,68 L604,65 L600,68 Z" fill="{FG}"/></g>')
    o.append(txt(604, 88, 'N', 't', 'middle', 2.9))
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
VH = {'collectors.html': 248, 'talent-representation.html': 318}
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
