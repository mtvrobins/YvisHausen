"""Builds the System Page (SP) from tools/sp_template.html: fills in the
animated illustrations and writes src/protected/engine.html."""
import re
import math, random, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
tpl = open('tools/sp_template.html').read()
# the System Page is private: its readable source lives in src/protected and
# tools/build.py publishes an encrypted copy as engine.html
OUT = 'src/protected/engine.html'
src = open('sound.html').read()
head = src[src.index('  <header id="topbar">'):src.index('  </nav>') + len('  </nav>')]
foot = src[src.index('  <footer class="site-footer">'):src.index('  </footer>') + len('  </footer>')]
I = '          '
FG, M1, M2, M3, BG = '#F2F1EC', '#8A8A82', '#5C5C56', '#3A3A36', '#0B0B0A'

# ---------- 02 AUDIENCES ----------
random.seed(7)
cx, cy = 130, 112
bands = [  # (rmin, rmax, count, colour, radius, base delay)
    (74, 93, 34, M2, 1.6, 1.3),
    (49, 67, 20, M1, 1.8, 1.6),
    (24, 41, 12, '#cfcec8', 2.0, 1.9),
    (0, 14, 5, FG, 2.4, 2.2),
]
dots = []
for rmin, rmax, n, col, r, dl in bands:
    placed = []
    tries = 0
    while len(placed) < n and tries < 5000:
        tries += 1
        a = random.uniform(0, 2 * math.pi)
        rr = math.sqrt(random.uniform(rmin ** 2, rmax ** 2))
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        if any((x - px) ** 2 + (y - py) ** 2 < 49 for px, py in placed):
            continue
        placed.append((x, y))
    for k, (x, y) in enumerate(placed):
        dots.append(f'{I}<circle class="fi" style="--dl:{dl + k * 0.025:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>')
aud_dots = '\n'.join(dots)

leaders = []
for (ang, ring, ly, lab, sub, dl) in [
    (-50, 96, 44, 'BROAD', 'Prospecting at scale', 2.5),
    (-20, 70, 84, 'LOOKALIKES', 'Modelled on buyers', 2.7),
    (10, 45, 124, 'ENGAGED', 'Visitors and viewers', 2.9),
    (40, 20, 164, 'CUSTOMERS', 'Past purchasers', 3.1),
]:
    a = math.radians(ang)
    px, py = cx + ring * math.cos(a), cy + ring * math.sin(a)
    leaders.append(
        f'{I}<path class="dr" pathLength="100" style="--dl:{dl}s;--du:.7s" d="M{px:.1f},{py:.1f} L{px + (ly - py) * 0.0 + 14:.1f},{ly} L232,{ly}" fill="none" stroke="{M2}" stroke-width="0.8"/>\n'
        f'{I}<circle class="pop" style="--dl:{dl}s" cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#000" stroke="{FG}"/>\n'
        f'{I}<g class="fi" style="--dl:{dl + 0.4}s"><text class="t t-b" x="238" y="{ly + 1}">{lab}</text><text class="t t-s" x="238" y="{ly + 10}">{sub}</text></g>')
aud_leaders = '\n'.join(leaders)

# ---------- 03 CREATIVE ----------
glyphs = [
    # A: face / portrait
    lambda x: f'<circle cx="{x+32}" cy="46" r="10" fill="none" stroke="{M2}"/><path d="M{x+18},66 C{x+22},56 {x+42},56 {x+46},66" fill="none" stroke="{M2}"/>',
    # B: video play
    lambda x: f'<circle cx="{x+32}" cy="48" r="11" fill="none" stroke="{M2}"/><path d="M{x+29},43 L{x+37},48 L{x+29},53 Z" fill="{M1}"/>',
    # C: bold statement (the winner)
    lambda x: f'<rect x="{x+14}" y="36" width="36" height="5" rx="1" fill="{FG}" fill-opacity=".85"/><rect x="{x+14}" y="45" width="28" height="5" rx="1" fill="{FG}" fill-opacity=".85"/><rect x="{x+14}" y="54" width="32" height="5" rx="1" fill="{FG}" fill-opacity=".5"/>',
    # D: carousel
    lambda x: f'<rect x="{x+12}" y="36" width="26" height="26" fill="none" stroke="{M2}"/><rect x="{x+42}" y="36" width="12" height="26" fill="none" stroke="{M3}"/><circle cx="{x+28}" cy="68" r="1" fill="{M1}"/><circle cx="{x+32}" cy="68" r="1" fill="{M3}"/><circle cx="{x+36}" cy="68" r="1" fill="{M3}"/>',
]
hook = [0.46, 0.62, 0.92, 0.38]
ctr = [0.52, 0.4, 0.84, 0.56]
cards = []
for i, x in enumerate([14, 90, 166, 242]):
    win = i == 2
    dl = 0.15 * i
    body = (
        f'<rect x="{x}" y="16" width="64" height="112" rx="7" fill="{BG}" stroke="{M3}"' + (f' class="lit" style="--dl:2.8s"' if win else '') + '/>'
        f'<rect x="{x+26}" y="20" width="12" height="2" rx="1" fill="#262624"/>'
        f'<rect x="{x+6}" y="28" width="52" height="46" rx="2" fill="#111110" stroke="#1E1E1C"/>'
        + glyphs[i](x) +
        f'<rect x="{x+6}" y="80" width="40" height="3" rx="1.5" fill="#4A4A45"/>'
        f'<rect x="{x+6}" y="87" width="30" height="3" rx="1.5" fill="{M3}"/>'
        f'<rect x="{x+6}" y="94" width="36" height="3" rx="1.5" fill="{M3}"/>'
        f'<rect x="{x+6}" y="106" width="52" height="12" rx="6" fill="none" stroke="{M2}"/>'
        f'<text class="t t-s" x="{x+32}" y="114" text-anchor="middle">SHOP NOW</text>'
        f'<text class="t{" t-b" if win else ""}" x="{x+32}" y="142" text-anchor="middle">HOOK {"ABCD"[i]}</text>'
        f'<rect x="{x}" y="150" width="64" height="4" rx="2" fill="#1C1C1A"/>'
        f'<rect x="{x}" y="160" width="64" height="4" rx="2" fill="#1C1C1A"/>'
    )
    bars = (
        f'<rect class="gx" style="--dl:{1.3 + 0.12*i:.2f}s;--du:1.3s" x="{x}" y="150" width="{64*hook[i]:.1f}" height="4" rx="2" fill="{FG}"/>'
        f'<rect class="gx" style="--dl:{1.5 + 0.12*i:.2f}s;--du:1.3s" x="{x}" y="160" width="{64*ctr[i]:.1f}" height="4" rx="2" fill="{M1}"/>'
    )
    inner = f'<g class="fi" style="--dl:{dl:.2f}s">{body}</g>{bars}'
    if win:
        cards.append(f'{I}<g>{inner}</g>')
    else:
        cards.append(f'{I}<g class="dim" style="--dl:2.6s">{inner}</g>')
cards.append(
    f'{I}<circle class="ping" style="--dl:3.1s" cx="230" cy="16" r="8" fill="none" stroke="{FG}" stroke-width="0.9"/>\n'
    f'{I}<g class="pop" style="--dl:2.9s"><circle cx="230" cy="16" r="8" fill="{FG}"/>'
    f'<path d="M226,16 L229,19 L234.5,13" fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></g>\n'
    f'{I}<text class="t t-b fi" style="--dl:3.2s" x="198" y="184" text-anchor="middle">WINNER · READY TO SCALE</text>')
creative = '\n'.join(cards)

# ---------- 05 STRUCTURE ----------
# a blueprint: your goals branch into three separate lanes; the ad that proves
# itself in testing graduates to scale, and the budget divides across them
S = []
for gx in range(20, 320, 20):
    S.append(f'{I}<path class="dr" pathLength="100" style="--dl:{0.02 * gx / 20:.2f}s;--du:.8s" d="M{gx},34 V150" fill="none" stroke="#151514" stroke-width="0.5"/>')
S.append(f'{I}<g class="pop" style="--dl:0.3s"><rect x="122" y="8" width="76" height="18" rx="9" fill="{BG}" stroke="{FG}"/>'
         f'<text class="t t-b" x="160" y="19.6" text-anchor="middle">YOUR GOALS</text></g>')
lanes = [(56, 'TEST', 0.8), (160, 'SCALE', 1.0), (264, 'RETARGET', 1.2)]
for cx, lab, dl in lanes:
    S.append(f'{I}<path class="dr" pathLength="100" style="--dl:{dl - 0.3:.2f}s;--du:.6s" d="M160,26 C160,36 {cx},32 {cx},44" fill="none" stroke="{M2}" stroke-width="0.8"/>')
    S.append(f'{I}<g class="fi" style="--dl:{dl:.2f}s"><rect x="{cx - 48}" y="44" width="96" height="104" rx="3" fill="{BG}" stroke="{M3}" stroke-dasharray="3 2"/>'
             f'<text class="t t-b" x="{cx - 40}" y="56">{lab}</text><path d="M{cx - 40},61 H{cx + 40}" stroke="#262624" stroke-width="0.6"/></g>')
# test lane: four ad sets race, one proves itself, the rest dim
bars = [0.35, 0.92, 0.28, 0.45]
for k in range(4):
    y = 67 + k * 19
    win = k == 1
    if not win: S.append(f'{I}<g class="dim" style="--dl:2.9s">')
    S.append(f'{I}<g class="fi" style="--dl:{1.3 + k * 0.1:.2f}s"><rect x="14" y="{y}" width="84" height="14" rx="2" fill="#121211" stroke="#2E2E2B"/>'
             f'<rect x="18" y="{y + 3.5}" width="7" height="7" fill="{M2}"/><rect x="29" y="{y + 4}" width="22" height="2" rx="1" fill="{M3}"/><rect x="29" y="{y + 8}" width="14" height="2" rx="1" fill="#262624"/>'
             f'<rect x="56" y="{y + 6}" width="36" height="2" rx="1" fill="#1C1C1A"/></g>')
    S.append(f'{I}<rect class="gx" style="--dl:{1.7 + k * 0.08:.2f}s;--du:1.3s" x="56" y="{y + 6}" width="{36 * bars[k]:.1f}" height="2" rx="1" fill="{FG if win else M2}"/>')
    if not win: S.append(f'{I}</g>')
S.append(f'{I}<rect class="pop" style="--dl:3.0s" x="13" y="85" width="86" height="16" rx="2.5" fill="none" stroke="{FG}"/>')
S.append(f'{I}<text class="t t-s fi" style="--dl:3.1s" x="56" y="160" text-anchor="middle">Proven: moves to scale</text>')
# the winner graduates into the scale lane
S.append(f'{I}<g class="grad" style="--dl:3.4s;--tx:104px;--ty:-18px"><rect x="14" y="86" width="84" height="14" rx="2" fill="#1A1A18" stroke="{FG}"/>'
         f'<rect x="18" y="89.5" width="7" height="7" fill="{FG}"/><rect x="29" y="90" width="22" height="2" rx="1" fill="#cfcec8"/><rect x="56" y="92" width="33" height="2" rx="1" fill="{FG}"/></g>')
for k in range(2):
    y = 90 + k * 26
    S.append(f'{I}<g class="fi" style="--dl:{1.5 + k * 0.15:.2f}s"><rect x="118" y="{y}" width="84" height="20" rx="2" fill="#121211" stroke="#2E2E2B"/>'
             f'<rect x="122" y="{y + 4}" width="12" height="12" fill="{M2}" fill-opacity=".7"/><rect x="138" y="{y + 5}" width="40" height="2.5" rx="1.2" fill="#4A4A45"/><rect x="138" y="{y + 11}" width="28" height="2.5" rx="1.2" fill="{M3}"/></g>')
# retarget lane: warm segments light up as people arrive
for k, lab in enumerate(['VIEWED', 'ADDED TO CART', 'PURCHASED']):
    y = 68 + k * 24
    S.append(f'{I}<g class="fi" style="--dl:{1.7 + k * 0.12:.2f}s"><rect x="222" y="{y}" width="84" height="18" rx="2" fill="#121211" stroke="#2E2E2B"/>'
             f'<circle cx="231" cy="{y + 9}" r="2.6" fill="none" stroke="{M1}"/><text class="t t-s" x="238" y="{y + 11}">{lab}</text></g>')
    S.append(f'{I}<circle cx="231" cy="{y + 9}" r="1.4" fill="{FG}" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="2.4s" begin="{4.2 + k * 0.8:.1f}s" repeatCount="indefinite"/></circle>')
S.append(f'{I}<g class="flow" style="--dl:4s">')
for b in ['0s', '1.2s']:
    S.append(f'{I}  <circle r="1.8" fill="{FG}"><animateMotion dur="2.4s" begin="{b}" repeatCount="indefinite" path="M202,100 C212,100 214,77 222,77"/></circle>')
S.append(f'{I}</g>')
# one budget, divided
S.append(f'{I}<g class="fi" style="--dl:3.6s"><text class="t t-s" x="14" y="176">SUGGESTED SHARE</text><rect x="14" y="181" width="292" height="6" rx="3" fill="#1C1C1A"/></g>')
x = 14
for (pct, sub, col, dl) in [(0.2, 'Prove the idea', M1, 3.9), (0.6, 'Grow what works', FG, 4.2), (0.2, 'Reconnect', M2, 4.5)]:
    wdt = 292 * pct
    S.append(f'{I}<rect class="gx" style="--dl:{dl:.1f}s;--du:.8s" x="{x + 1:.1f}" y="181" width="{wdt - 2:.1f}" height="6" rx="3" fill="{col}"/>')
    S.append(f'{I}<g class="fi" style="--dl:{dl + 0.3:.1f}s"><text class="t t-b" x="{x + wdt / 2:.1f}" y="200" text-anchor="middle">{int(pct * 100)}%</text><text class="t t-s" x="{x + wdt / 2:.1f}" y="209" text-anchor="middle">{sub}</text></g>')
    x += wdt
structure = '\n'.join(S)

# ---------- 06 SCALE ----------
C = []
C.append(f'{I}<line class="fi" x1="18" y1="170" x2="136" y2="170" stroke="{M3}"/>')
hs = [30, 44, 60, 78, 98]
for k, h in enumerate(hs):
    x = 22 + k * 22
    dl = 0.3 + k * 0.35
    C.append(f'{I}<rect class="gy" style="--dl:{dl:.2f}s" x="{x}" y="{170-h}" width="14" height="{h}" fill="{FG if k == 4 else M2}" fill-opacity="{1 if k == 4 else 0.55 + k*0.1:.2f}"/>')
    if k:
        C.append(f'{I}<g class="pop" style="--dl:{dl + 0.35:.2f}s"><line x1="{x+7}" y1="{170-h-12}" x2="{x+7}" y2="{170-h-6}" stroke="{FG}"/><line x1="{x+4}" y1="{170-h-9}" x2="{x+10}" y2="{170-h-9}" stroke="{FG}"/></g>')
C.append(f'{I}<path class="dr" pathLength="100" style="--dl:0.6s;--du:2s" d="M29,136 L51,122 L73,106 L95,88 L117,68" fill="none" stroke="{FG}" stroke-width="0.8" stroke-dasharray="100" />')
C.append(f'{I}<g class="fi" style="--dl:0.2s"><text class="t t-b" x="18" y="190">VERTICAL</text><text class="t t-s" x="18" y="200">Budget raised in measured steps</text></g>')
C.append(f'{I}<line class="fi" style="--dl:0.1s" x1="160" y1="28" x2="160" y2="204" stroke="#2A2A27" stroke-dasharray="2 4"/>')
# horizontal
targets = [(272, 52, 'NEW AUDIENCE', 'above'), (282, 110, 'NEW PLACEMENT', 'below'), (272, 168, 'NEW MARKET', 'below')]
paths = [f'M208,110 C236,110 244,52 {x-8},{y}' if y != 110 else f'M208,110 L{x-8},{y}' for x, y, _, _ in targets]
for k, (p, (x, y, lab, pos)) in enumerate(zip(paths, targets)):
    dl = 1.0 + k * 0.3
    C.append(f'{I}<path class="dr" pathLength="100" style="--dl:{dl:.1f}s" d="{p.replace("244,52", f"244,{y}")}" fill="none" stroke="{M2}" stroke-width="1.1"/>')
    C.append(f'{I}<g class="pop" style="--dl:{dl + 0.8:.1f}s"><circle cx="{x}" cy="{y}" r="8" fill="#000" stroke="{FG}"/><rect x="{x-3}" y="{y-4}" width="6" height="8" fill="none" stroke="{M1}" stroke-width="0.8"/></g>')
    ty = y - 13 if pos == 'above' else y + 19
    C.append(f'{I}<text class="t fi" style="--dl:{dl + 1:.1f}s" x="{x}" y="{ty}" text-anchor="middle">{lab}</text>')
C.append(f'{I}<circle class="ping" style="--dl:1.2s" cx="200" cy="110" r="10" fill="none" stroke="{FG}"/>')
C.append(f'{I}<g class="pop" style="--dl:0.7s"><rect x="190" y="97" width="20" height="26" rx="3" fill="{BG}" stroke="{FG}"/><rect x="193" y="100" width="14" height="10" fill="{FG}" fill-opacity=".7"/>'
         f'<rect x="193" y="113" width="10" height="1.8" fill="{M1}"/><rect x="193" y="117" width="12" height="1.8" fill="{M3}"/></g>')
C.append(f'{I}<text class="t t-b fi" style="--dl:0.9s" x="200" y="89" text-anchor="middle">WINNER</text>')
C.append(f'{I}<g class="flow" style="--dl:2.4s">')
for k, (p, (x, y, _, _)) in enumerate(zip(paths, targets)):
    p = p.replace('244,52', f'244,{y}')
    for b in [0.3 * k, 0.3 * k + 1.3]:
        C.append(f'{I}  <circle r="2" fill="{FG}"><animateMotion dur="2.6s" begin="{b:.1f}s" repeatCount="indefinite" path="{p}"/></circle>')
C.append(f'{I}</g>')
C.append(f'{I}<g class="fi" style="--dl:0.2s"><text class="t t-b" x="180" y="190">HORIZONTAL</text><text class="t t-s" x="180" y="200">Proven ads carried further</text></g>')
scale = '\n'.join(C)

# ---------- 10 RECONNECT ----------
# one visitor's journey: they browse, leave at the basket, a reminder brings
# them back, and they buy. It plays as a loop once the scene is drawn.
R = []
nodes = [(34, 'VISIT'), (106, 'VIEW'), (178, 'CART'), (286, 'PURCHASE')]
R.append(f'{I}<path class="dr" pathLength="100" style="--dl:0.3s;--du:1.4s" d="M34,70 L286,70" fill="none" stroke="{M3}" stroke-width="1" stroke-dasharray="2 3"/>')
R.append(f'{I}<path class="dr" pathLength="100" style="--dl:0.3s;--du:1.1s" d="M34,70 L178,70" fill="none" stroke="{M1}" stroke-width="1.1"/>')
for k, (x, lab) in enumerate(nodes):
    dl = 0.3 + k * 0.3
    last = lab == 'PURCHASE'
    R.append(f'{I}<g class="pop" style="--dl:{dl:.2f}s"><circle cx="{x}" cy="70" r="{11 if last else 8}" fill="#000" stroke="{FG if last else M1}" stroke-width="1.1"/>'
             + (f'<path d="M{x - 4.5},70 L{x - 1},73.5 L{x + 5},66.5" fill="none" stroke="{FG}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>' if last else f'<circle cx="{x}" cy="70" r="2.2" fill="{M1}"/>')
             + '</g>')
    R.append(f'{I}<text class="t{" t-b" if last else ""} fi" style="--dl:{dl + 0.25:.2f}s" x="{x}" y="50" text-anchor="middle">{lab}</text>')
leave = 'M178,78 C178,104 168,120 150,128'
back = 'M196,140 C244,140 282,118 286,82'
R.append(f'{I}<path class="dr" pathLength="100" style="--dl:1.5s;--du:.7s" d="{leave}" fill="none" stroke="{M2}" stroke-width="0.9" stroke-dasharray="2 2.5"/>')
R.append(f'{I}<text class="t t-s fi" style="--dl:1.8s" x="186" y="104">Left the basket</text>')
R.append(f'{I}<g class="pop" style="--dl:2.1s"><rect x="104" y="124" width="92" height="40" rx="4" fill="{BG}" stroke="{FG}"/>'
         f'<rect x="110" y="130" width="22" height="22" fill="{M2}"/><rect x="137" y="132" width="50" height="2.6" rx="1.3" fill="#cfcec8"/>'
         f'<rect x="137" y="138" width="38" height="2.6" rx="1.3" fill="{M3}"/><rect x="137" y="144" width="42" height="2.6" rx="1.3" fill="{M3}"/>'
         f'<rect x="110" y="155" width="76" height="5" rx="2.5" fill="none" stroke="{M1}" stroke-width="0.7"/></g>')
R.append(f'{I}<text class="t fi" style="--dl:2.3s" x="150" y="178" text-anchor="middle">REMINDER</text>')
R.append(f'{I}<path class="dr" pathLength="100" style="--dl:2.6s;--du:.9s" d="{back}" fill="none" stroke="{FG}" stroke-width="1.1"/>')
R.append(f'{I}<text class="t t-s fi" style="--dl:3s" x="244" y="150">Returns to buy</text>')
# the visitor, looping every 7s: browse, leave, reminded, return, buy
D, B = 7, 3.6
R.append(f'{I}<circle r="3.2" fill="{FG}" opacity="0"><animateMotion dur="{D}s" begin="{B}s" repeatCount="indefinite" path="M34,70 L178,70 C178,104 168,120 150,128" keyPoints="0;0.62;0.62;1;1" keyTimes="0;0.34;0.4;0.52;1" calcMode="linear"/>'
         f'<animate attributeName="opacity" values="0;1;1;1;0;0" keyTimes="0;0.03;0.4;0.5;0.53;1" dur="{D}s" begin="{B}s" repeatCount="indefinite"/></circle>')
R.append(f'{I}<rect x="102" y="122" width="96" height="44" rx="5" fill="none" stroke="{FG}" opacity="0"><animate attributeName="opacity" values="0;0;0.8;0;0" keyTimes="0;0.52;0.58;0.66;1" dur="{D}s" begin="{B}s" repeatCount="indefinite"/></rect>')
R.append(f'{I}<circle r="3.2" fill="{FG}" opacity="0"><animateMotion dur="{D}s" begin="{B}s" repeatCount="indefinite" path="{back}" keyPoints="0;0;1;1" keyTimes="0;0.62;0.84;1" calcMode="linear"/>'
         f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.61;0.63;0.83;0.85;1" dur="{D}s" begin="{B}s" repeatCount="indefinite"/></circle>')
R.append(f'{I}<circle cx="286" cy="70" r="11" fill="none" stroke="{FG}" opacity="0"><animate attributeName="r" values="11;11;22;22" keyTimes="0;0.84;0.96;1" dur="{D}s" begin="{B}s" repeatCount="indefinite"/>'
         f'<animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="0;0.84;0.86;0.96;1" dur="{D}s" begin="{B}s" repeatCount="indefinite"/></circle>')
# frequency cap: three reminders at most, then it rests
R.append(f'{I}<g class="fi" style="--dl:1s"><text class="t" x="18" y="150">FREQUENCY CAP</text>')
for k in range(5):
    R.append(f'{I}  <rect x="{18 + k * 13}" y="157" width="9" height="9" rx="2" fill="none" stroke="{M3}"/>')
R.append(f'{I}  <path d="M83,154 V169" stroke="{M1}" stroke-width="0.8" stroke-dasharray="1.5 1.5"/>')
R.append(f'{I}  <text class="t t-s" x="18" y="182">Welcome, never intrusive</text></g>')
for k in range(3):
    R.append(f'{I}<rect class="pop" style="--dl:{1.4 + k * 0.25:.2f}s" x="{20 + k * 13}" y="159" width="5" height="5" rx="1" fill="{FG}"/>')
reconnect = '\n'.join(R)

# ---------- 08 REPORT & ARCHIVE ----------
A = []
A.append(f'{I}<g class="fi"><rect x="24" y="18" width="120" height="170" rx="4" fill="{BG}" stroke="{M2}"/>'
         f'<text class="t t-b" x="34" y="34">REPORT</text><text class="t t-s" x="134" y="34" text-anchor="end">MONTH 03</text>'
         f'<line x1="34" y1="40" x2="134" y2="40" stroke="#262624"/></g>')
for k, lab in enumerate(['ROAS', 'CPA', 'SPEND']):
    x = 34 + k * 34
    A.append(f'{I}<g class="fi" style="--dl:{0.3 + k*0.12:.2f}s"><rect x="{x}" y="46" width="30" height="22" rx="2" fill="none" stroke="#2E2E2B"/>'
             f'<text class="t t-s" x="{x+4}" y="55">{lab}</text><rect x="{x+4}" y="60" width="{[18,14,20][k]}" height="3" rx="1.5" fill="{FG if k == 0 else M1}"/></g>')
A.append(f'{I}<g class="fi" style="--dl:0.6s"><line x1="34" y1="112" x2="134" y2="112" stroke="{M3}"/><line x1="34" y1="92" x2="134" y2="92" stroke="#1C1C1A"/></g>')
for k, h in enumerate([10, 16, 12, 22, 26, 32]):
    A.append(f'{I}<rect class="gy" style="--dl:{0.8 + k*0.1:.1f}s" x="{38 + k*16}" y="{112-h}" width="8" height="{h}" fill="{M3}"/>')
A.append(f'{I}<path class="dr" pathLength="100" style="--dl:1.2s;--du:1.2s" d="M42,104 L58,98 L74,100 L90,88 L106,84 L122,76" fill="none" stroke="{FG}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>')
for k, w in enumerate([96, 84, 90, 60]):
    A.append(f'{I}<rect class="gx" style="--dl:{1.4 + k*0.12:.2f}s" x="34" y="{120 + k*7}" width="{w}" height="2.4" rx="1.2" fill="{"#4A4A45" if k == 0 else M3}"/>')
# insight block inside the report (flies to the archive)
A.append(f'{I}<g class="fi" style="--dl:1.9s"><rect x="34" y="152" width="60" height="28" rx="2" fill="none" stroke="{M2}" stroke-dasharray="2 2"/></g>')
FLY=(f'{I}<g class="fly" style="--fly:spFile;--dl:2.4s"><rect x="34" y="152" width="60" height="28" rx="2" fill="#141413" stroke="{FG}"/>'
         f'<rect x="39" y="157" width="14" height="18" fill="{FG}" fill-opacity=".7"/><rect x="57" y="158" width="30" height="2.4" rx="1.2" fill="#cfcec8"/>'
         f'<rect x="57" y="164" width="22" height="2.4" rx="1.2" fill="{M1}"/><rect x="57" y="170" width="26" height="2.4" rx="1.2" fill="{M3}"/></g>')
A.append(f'{I}<text class="t t-s fi" style="--dl:1.9s" x="100" y="168">INSIGHT</text>')
# archive library: grid of kept learnings, one slot waiting
A.append(f'{I}<g class="fi" style="--dl:0.4s"><rect x="176" y="46" width="124" height="142" rx="4" fill="{BG}" stroke="{M3}"/>'
         f'<text class="t t-b" x="186" y="62">LEARNINGS</text><text class="t t-s" x="290" y="62" text-anchor="end">DOCUMENTED</text>'
         f'<line x1="186" y1="68" x2="290" y2="68" stroke="#262624"/></g>')
slot = (244, 152)
k = 0
for r in range(4):
    for c in range(3):
        x, y = 186 + c * 34, 78 + r * 26
        if (x, y) == (220, 156):
            pass
        if r == 3 and c == 1:
            A.append(f'{I}<rect class="fi" style="--dl:1.2s" x="{x}" y="{y}" width="30" height="20" rx="1.5" fill="none" stroke="{M2}" stroke-dasharray="2 2"/>')
            slot = (x, y)
            continue
        A.append(f'{I}<g class="fi" style="--dl:{0.6 + k*0.07:.2f}s"><rect x="{x}" y="{y}" width="30" height="20" rx="1.5" fill="#111110" stroke="#2A2A27"/>'
                 f'<rect x="{x+3}" y="{y+3}" width="7" height="14" fill="{M3}"/><rect x="{x+13}" y="{y+5}" width="13" height="1.8" fill="#4A4A45"/><rect x="{x+13}" y="{y+10}" width="9" height="1.8" fill="{M3}"/></g>')
        k += 1
A.append(f'{I}<circle class="ping" style="--dl:3.8s" cx="{slot[0]+15}" cy="{slot[1]+10}" r="14" fill="none" stroke="{FG}" stroke-width="0.8"/>')
A.append(f'{I}<g class="fi" style="--dl:0.3s"><text class="t t-s" x="24" y="204">Plain-language findings</text><text class="t t-s" x="176" y="204">Every learning, documented</text></g>')
A.append(FLY)
archive = '\n'.join(A)
# fly target: card (34,152,60x28) scaled to 30x20 slot
sx = 30 / 60
fly_kf = f'@keyframes spFile{{ 0%{{ opacity:0; transform:translate(0,0) scale(1); }} 12%{{ opacity:1; }} 100%{{ opacity:1; transform:translate({slot[0]-34}px,{slot[1]-152}px) scale({sx},{20/28:.3f}); }} }}'


# ---------- 01 AUDIT ----------
U = []
# website under review, with a scan line sweeping it
U.append(f'{I}<g class="fi"><rect x="14" y="22" width="116" height="156" rx="5" fill="{BG}" stroke="{M3}"/>'
         f'<line x1="14" y1="36" x2="130" y2="36" stroke="#262624"/><circle cx="22" cy="29" r="1.8" fill="{M3}"/><circle cx="28" cy="29" r="1.8" fill="{M3}"/><circle cx="34" cy="29" r="1.8" fill="{M3}"/>'
         f'<rect x="44" y="26" width="76" height="6" rx="3" fill="none" stroke="#2E2E2B"/></g>')
U.append(f'{I}<g class="fi" style="--dl:0.2s"><rect x="22" y="44" width="100" height="44" fill="#111110" stroke="#1E1E1C"/>'
         f'<rect x="30" y="56" width="50" height="4" rx="2" fill="#4A4A45"/><rect x="30" y="64" width="36" height="3" rx="1.5" fill="{M3}"/>'
         f'<rect x="30" y="74" width="24" height="7" rx="3.5" fill="none" stroke="{M1}" stroke-width="0.8"/>'
         f'<rect x="22" y="96" width="30" height="30" fill="none" stroke="{M3}"/><rect x="57" y="96" width="30" height="30" fill="none" stroke="{M3}"/><rect x="92" y="96" width="30" height="30" fill="none" stroke="{M3}"/>'
         f'<rect x="22" y="134" width="80" height="3" rx="1.5" fill="{M3}"/><rect x="22" y="141" width="64" height="3" rx="1.5" fill="#262624"/>'
         f'<rect x="22" y="152" width="100" height="16" rx="2" fill="none" stroke="{M2}"/><text class="t t-s" x="72" y="162.5" text-anchor="middle">CHECKOUT</text></g>')
U.append(f'{I}<g class="flow" style="--dl:0.6s"><rect x="14" y="40" width="116" height="1.2" fill="{FG}" fill-opacity=".55">'
         f'<animate attributeName="y" values="40;174;40" dur="4.2s" repeatCount="indefinite"/></rect></g>')
for k, (x, y) in enumerate([(84, 77), (112, 111), (116, 160)]):
    dl = 1.2 + k * 0.5
    U.append(f'{I}<circle class="ping" style="--dl:{dl + 0.2:.1f}s" cx="{x}" cy="{y}" r="6" fill="none" stroke="{FG}" stroke-width="0.8"/>')
    U.append(f'{I}<g class="pop" style="--dl:{dl:.1f}s"><circle cx="{x}" cy="{y}" r="5" fill="{FG}"/><text x="{x}" y="{y + 2.4}" text-anchor="middle" style="font:700 6.5px var(--sans);fill:#000">!</text></g>')
U.append(f'{I}<g class="fi" style="--dl:0.3s"><text class="t t-b" x="14" y="194">WEBSITE</text><text class="t t-s" x="14" y="204">Friction points found</text></g>')
# conversion-rate gauge
U.append(f'{I}<g class="fi" style="--dl:0.4s"><text class="t" x="150" y="30">CONVERSION RATE</text>'
         f'<path d="M154,76 A30,30 0 0 1 214,76" fill="none" stroke="#262624" stroke-width="4" stroke-linecap="round"/></g>')
U.append(f'{I}<path class="dr" pathLength="100" style="--dl:0.9s;--du:1.4s" d="M154,76 A30,30 0 0 1 176,47.1" fill="none" stroke="{FG}" stroke-width="4" stroke-linecap="round"/>')
U.append(f'{I}<g class="fi" style="--dl:1.6s"><text class="t t-b" x="184" y="72" text-anchor="middle" style="font-size:9px;font-weight:700">2.1%</text><text class="t t-s" x="184" y="86" text-anchor="middle">Benchmark 3%</text></g>')
U.append(f'{I}<line class="fi" style="--dl:1.2s" x1="208.3" y1="58.6" x2="213" y2="55.5" stroke="{M1}" stroke-width="1.2"/>')
# competitor ads, with a lens passing over them
U.append(f'{I}<text class="t fi" style="--dl:0.6s" x="236" y="30">COMPETITORS</text>')
for k in range(3):
    x = 236 + k * 24
    U.append(f'{I}<g class="fi" style="--dl:{0.8 + k*0.15:.2f}s"><rect x="{x}" y="38" width="20" height="36" rx="3" fill="{BG}" stroke="{M3}"/>'
             f'<rect x="{x+3}" y="42" width="14" height="14" fill="#1C1C1A"/><rect x="{x+3}" y="60" width="12" height="2" rx="1" fill="{M3}"/><rect x="{x+3}" y="65" width="9" height="2" rx="1" fill="#262624"/></g>')
U.append(f'{I}<g class="flow" style="--dl:1.4s"><g><circle r="9" fill="{FG}" fill-opacity=".06" stroke="{FG}" stroke-width="1"/><line x1="6.4" y1="6.4" x2="12" y2="12" stroke="{FG}" stroke-width="1.6" stroke-linecap="round"/>'
         f'<animateMotion dur="5s" repeatCount="indefinite" path="M246,52 C258,44 266,62 270,52 C276,44 290,58 294,52 C286,64 258,64 246,52"/></g></g>')
U.append(f'{I}<g class="fi" style="--dl:2s"><text class="t t-s" x="236" y="88">Angles &#183; offers &#183; formats</text></g>')
# funnel map drawn from the findings
U.append(f'{I}<text class="t t-b fi" style="--dl:2.2s" x="150" y="122">FUNNEL MAP</text>')
U.append(f'{I}<line class="fi" style="--dl:2.2s" x1="150" y1="128" x2="306" y2="128" stroke="#262624"/>')
U.append(f'{I}<path class="dr" pathLength="100" style="--dl:2.6s;--du:1.2s" d="M166,156 L226,156 L286,156" fill="none" stroke="{M1}" stroke-width="1.1"/>')
U.append(f'{I}<path class="dr" pathLength="100" style="--dl:3.4s;--du:1s" d="M286,166 C286,190 166,190 166,166" fill="none" stroke="{M2}" stroke-dasharray="100" stroke-width="0.9"/>')
for k, (x, lab) in enumerate([(166, 'COLD'), (226, 'WARM'), (286, 'CUSTOMER')]):
    dl = 2.5 + k * 0.4
    U.append(f'{I}<g class="pop" style="--dl:{dl:.1f}s"><circle cx="{x}" cy="156" r="8" fill="#000" stroke="{FG if k == 2 else M1}" stroke-width="1.1"/><circle cx="{x}" cy="156" r="2.4" fill="{FG if k == 2 else M1}"/></g>')
    U.append(f'{I}<text class="t t-s fi" style="--dl:{dl + 0.2:.1f}s" x="{x}" y="143" text-anchor="middle">{lab}</text>')
U.append(f'{I}<text class="t t-s fi" style="--dl:3.9s" x="226" y="200" text-anchor="middle">Repeat purchase</text>')
U.append(f'{I}<g class="flow" style="--dl:3.4s">')
for bb in ['0s', '1.4s']:
    U.append(f'{I}  <circle r="2" fill="{FG}"><animateMotion dur="2.8s" begin="{bb}" repeatCount="indefinite" path="M166,156 L286,156"/></circle>')
U.append(f'{I}</g>')
audit = '\n'.join(U)

# ---------- 07 FUNNEL ----------
# a wireframe funnel in perspective: rings and meridians draw in, traffic
# spirals down with light trails and thins as it goes; what reaches the bottom
# glows, drops into the lifetime-value ring and is carried back to the top
F = []
CX = 112
F.append(f'{I}<defs><radialGradient id="fnGlow"><stop offset="0" stop-color="{FG}" stop-opacity=".55"/><stop offset="1" stop-color="{FG}" stop-opacity="0"/></radialGradient></defs>')
N = 9
def ring(t):
    return 34 + t * 126, 16 + 68 * (1 - t) ** 1.35, 13 * (1 - t) + 3.2 * t
for k in range(N):
    t = k / (N - 1)
    y, rx, ry = ring(t)
    dl = 0.2 + k * 0.1
    F.append(f'{I}<path class="dr" pathLength="100" style="--dl:{dl:.2f}s;--du:.7s" d="M{CX - rx:.1f},{y:.1f} A{rx:.1f},{ry:.1f} 0 0 1 {CX + rx:.1f},{y:.1f}" fill="none" stroke="#2A2A27" stroke-width="0.7"/>')
    bright = k in (0, 4, 8)
    F.append(f'{I}<path class="dr" pathLength="100" style="--dl:{dl + 0.15:.2f}s;--du:.7s" d="M{CX + rx:.1f},{y:.1f} A{rx:.1f},{ry:.1f} 0 0 1 {CX - rx:.1f},{y:.1f}" fill="none" stroke="{FG if bright else M2}" stroke-width="{1.2 if bright else 0.7}"/>')
# meridians: front ones brighter
for j in range(16):
    a = j * math.pi / 8 + 0.2
    pts = []
    for k in range(13):
        t = k / 12
        y, rx, ry = ring(t)
        pts.append((CX + rx * math.cos(a), y + ry * math.sin(a)))
    front = math.sin(a) > 0
    d = 'M' + ' L'.join(f'{x:.1f},{yy:.1f}' for x, yy in pts)
    F.append(f'{I}<path class="dr" pathLength="100" style="--dl:{1.0 + j * 0.03:.2f}s;--du:.9s" d="{d}" fill="none" stroke="{"#4A4A45" if front else "#222220"}" stroke-width="0.5"/>')
# light running round the three stage rings
for k, dur in ((0, 5), (4, 4), (8, 3)):
    y, rx, ry = ring(k / (N - 1))
    F.append(f'{I}<g class="fi" style="--dl:2.2s"><ellipse cx="{CX}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{FG}" stroke-width="1.4" stroke-dasharray="6 200" stroke-linecap="round">'
             f'<animate attributeName="stroke-dashoffset" from="0" to="-206" dur="{dur}s" repeatCount="indefinite"/></ellipse></g>')
# traffic spiralling down with trails; many enter, fewer go deeper
def spiral(phase, depth):
    out = []
    for i in range(depth + 1):
        t = i / 30
        y, rx, ry = ring(t)
        a = phase + t * 6 * math.pi
        out.append((CX + rx * 0.9 * math.cos(a), y + ry * 0.9 * math.sin(a)))
    return 'M' + ' L'.join(f'{x:.1f},{yy:.1f}' for x, yy in out)
F.append(f'{I}<g class="flow" style="--dl:2.4s">')
parts = [(0.0, 30, 0.0), (1.6, 30, 1.7), (3.1, 30, 3.3), (4.7, 30, 0.9),
         (0.8, 12, 0.4), (2.3, 9, 1.2), (3.9, 16, 2.1), (5.4, 7, 2.8), (2.9, 20, 3.6), (5.9, 11, 4.2), (1.2, 6, 4.8)]
for ph, depth, b in parts:
    full = depth == 30
    dur = 1.2 + depth * 0.11
    path = spiral(ph, depth)
    for tr, (r, op) in enumerate([(2.1 if full else 1.6, 1), (1.6 if full else 1.2, .45), (1.2 if full else .9, .2)]):
        col = FG if full else ('#cfcec8' if depth > 14 else M1)
        F.append(f'{I}  <circle r="{r}" fill="{col}" opacity="0"><animateMotion dur="{dur:.1f}s" begin="{b + tr * 0.07:.2f}s" repeatCount="indefinite" path="{path}"/>'
                 f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;0.08;0.85;1" dur="{dur:.1f}s" begin="{b + tr * 0.07:.2f}s" repeatCount="indefinite"/></circle>')
F.append(f'{I}</g>')
# the bottom glows; a converted customer drops into the LTV ring
F.append(f'{I}<g class="fi" style="--dl:2.6s"><ellipse cx="{CX}" cy="161" rx="26" ry="9" fill="url(#fnGlow)"><animate attributeName="opacity" values=".5;1;.5" dur="2.6s" repeatCount="indefinite"/></ellipse></g>')
F.append(f'{I}<path class="dr" pathLength="100" style="--dl:1.8s;--du:.4s" d="M{CX},164 V180" fill="none" stroke="{M2}" stroke-width="0.8"/>')
F.append(f'{I}<g class="flow" style="--dl:3s"><circle r="2.2" fill="{FG}"><animateMotion dur="2.6s" repeatCount="indefinite" path="M{CX},162 V181" keyPoints="0;0;1;1" keyTimes="0;0.55;0.8;1" calcMode="linear"/>'
         f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.5;0.56;0.8;0.85" dur="2.6s" repeatCount="indefinite"/></circle></g>')
F.append(f'{I}<g class="pop" style="--dl:2s"><circle cx="{CX}" cy="194" r="12" fill="{BG}" stroke="{FG}" stroke-width="1"/>'
         f'<text class="t t-b" x="{CX}" y="196.3" text-anchor="middle" style="font-size:5.6px">LTV</text></g>')
F.append(f'{I}<text class="t t-s fi" style="--dl:2.3s" x="{CX}" y="219" text-anchor="middle">LIFETIME VALUE</text>')
F.append(f'{I}<g class="fi" style="--dl:2.2s"><g class="spin" style="--ox:{CX}px;--oy:194px;animation-duration:7s"><circle cx="{CX}" cy="194" r="16.5" fill="none" stroke="{M1}" stroke-width="0.8" stroke-dasharray="1 3.4"/></g></g>')
loop = f'M{CX - 14},199 C{CX - 58},214 {CX - 104},150 {CX - 98},70 C{CX - 95},44 {CX - 80},30 {CX - 60},28'
F.append(f'{I}<path class="dr" pathLength="100" style="--dl:2.3s;--du:1.2s" d="{loop}" fill="none" stroke="{M2}" stroke-width="0.8" stroke-dasharray="2 3"/>')
F.append(f'{I}<g class="flow" style="--dl:3.4s">')
for b in ['0s', '1.4s']:
    F.append(f'{I}  <circle r="2" fill="{FG}"><animateMotion dur="2.8s" begin="{b}" repeatCount="indefinite" path="{loop}"/></circle>')
F.append(f'{I}</g>')
F.append(f'{I}<text class="t t-s fi" style="--dl:2.8s" x="{CX + 22}" y="201">Repeat, refer, return</text>')
for k, (pos, lab, sub, ly, rk) in enumerate([
        ('TOP', 'COLD TRAFFIC', 'New audiences, first impressions', 40, 0),
        ('MIDDLE', 'RETARGETING', 'Engaged, visited, added to cart', 98, 4),
        ('BOTTOM', 'CUSTOMERS', 'Retention and lifetime value', 156, 8)]):
    y, rx, ry = ring(rk / (N - 1))
    ex = CX + rx
    dl = 1.4 + k * 0.35
    F.append(f'{I}<path class="dr" pathLength="100" style="--dl:{dl:.2f}s;--du:.6s" d="M{ex + 3:.1f},{y:.1f} L208,{ly}" fill="none" stroke="{M3}" stroke-width="0.8"/>')
    F.append(f'{I}<circle class="pop" style="--dl:{dl:.2f}s" cx="{ex:.1f}" cy="{y:.1f}" r="2" fill="{FG}"/>')
    F.append(f'{I}<g class="fi" style="--dl:{dl + 0.3:.2f}s"><text class="t t-s" x="214" y="{ly - 8}">{pos}</text><text class="t t-b" x="214" y="{ly + 2}">{lab}</text><text class="t t-s" x="214" y="{ly + 11}">{sub}</text></g>')
F.append(f'{I}<text class="t fi" style="--dl:0.1s" x="20" y="14">ONE FUNNEL, EVERY STAGE</text>')
funnel = '\n'.join(F)

# ---------- BEYOND THE STANDARD: icon cards ----------
def ic(d, dl, extra=''):
    return f'<path class="dr" pathLength="100" style="--dl:{dl:.2f}s;--du:1.1s" d="{d}" fill="none" stroke="{FG}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"{extra}/>'
adv_items = [
    ('ADVANCED TRACKING', 'Advanced server-side tracking (Conversions API via Stape or Meta&rsquo;s Gateway), offline event tracking and GA4 integration.<a class="fn" href="#note-2" aria-label="See note 2">*2</a>',
     ['M6,8 H34 V18 H6 Z', 'M6,22 H34 V32 H6 Z', 'M28,13 H29 M28,27 H29', 'M11,13 H20 M11,27 H20']),
    ('MULTI-STAGE FUNNELS', 'Funnel design across cold traffic, retargeting and retention, built as one connected system.',
     ['M4,6 H36 L28,16 H12 Z', 'M12,20 H28 L24,27 H16 Z', 'M17,31 H23 L21,36 H19 Z']),
    ('LARGER BUDGETS', 'Support for larger advertising budgets, where deeper analysis and testing rigour matter most.<a class="fn" href="#note-6" aria-label="See note 6">*6</a>',
     ['M6,34 V24 M14,34 V18 M22,34 V12 M30,34 V6', 'M4,36 H36']),
    ('ENHANCED REPORTING', 'Custom live dashboards and more frequent recorded video walkthroughs.',
     ['M3,7 H37 V29 H3 Z', 'M17,13 L25,18 L17,23 Z', 'M13,35 H27']),
    ('MORE FREQUENT CALLS', 'Strategy calls every two weeks, for brands moving at pace.<a class="fn" href="#note-7" aria-label="See note 7">*7</a>',
     ['M5,8 H35 V26 H18 L10,33 V26 H5 Z', 'M11,15 H29 M11,20 H23']),
    ('BROADER CONSULTING', 'Strategic advice across your offers, landing pages and wider marketing direction.',
     ['M17,5 A12,12 0 1 1 16.99,5', 'M25.5,25.5 L35,35', 'M12,17 H22 M17,12 V22']),
]
AD = []
for k, (h, p, paths) in enumerate(adv_items):
    dl = 0.3 + k * 0.12
    svg = '<svg viewBox="0 0 40 40" aria-hidden="true">' + ''.join(ic(d, dl + j * 0.15) for j, d in enumerate(paths)) + '</svg>'
    AD.append(f'        <div class="adv-item">{svg}<h3>{h}</h3><p>{p}</p></div>')
adv = '\n'.join(AD)

out = tpl
out = out.replace('  @keyframes spFile{ 0%{ opacity:0; transform:translate(0,0) scale(1); } 12%{ opacity:1; } 100%{ opacity:1; transform:translate(172px,19px) scale(0.42); } }', '  ' + fly_kf)
out = out.replace('  .fly{ opacity:0; }', '  .fly{ opacity:0; transform-box:fill-box; transform-origin:0 0; }')
# Ad B: dim wrapper so the draw animation isn't overridden
out = out.replace('<path class="dr dim" pathLength="100" style="--dl:1.2s;--du:1.6s" d="M28,136', '<g class="dim" style="--dl:3.2s"><path class="dr" pathLength="100" style="--dl:1.2s;--du:1.6s" d="M28,136')
out = out.replace(' stroke-linecap="round" data-dim="3.2s"/>', ' stroke-linecap="round"/></g>')
for k, v in [('<!--HEAD-->', head), ('<!--FOOT-->', foot), ('<!--AUD_DOTS-->', aud_dots), ('<!--AUD_LEADERS-->', aud_leaders),
             ('<!--CREATIVE_CARDS-->', creative), ('<!--STRUCTURE-->', structure), ('<!--SCALE-->', scale),
             ('<!--RECONNECT-->', reconnect), ('<!--ARCHIVE-->', archive), ('<!--AUDIT-->', audit), ('<!--FUNNEL-->', funnel), ('<!--ADV-->', adv)]:
    assert k in out, k
    out = out.replace(k, v)
assert 'spFile{ 0%' in out and 'data-dim' not in out and '<!--' not in out.replace('<!-- ', '')
open(OUT, 'w').write(out)
print('ok', len(out), 'slot', slot)

# keep each note marker attached to the word before it, so it never wraps alone
_s = open(OUT).read()
_s = re.sub(r'(\S+?)(<a class="fn" href="#note-\d+" aria-label="See note \d+">\*\d+</a>)',
            lambda m: f'<span style="white-space:nowrap">{m.group(1)}{m.group(2)}</span>', _s)
open(OUT, 'w').write(_s)
