import math, random, sys
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables.TupleVariation import TupleVariation

# ------------------------------------------------------------------ metrics
R0 = 72            # stroke radius (stroke = 144)
h = 396            # x-height   (skeleton)  -> outer 540
CAP = 576          # cap height (skeleton)  -> outer 720
ASC = 616          # ascender   (skeleton)  -> outer 760
DES = -200         # descender  (skeleton)  -> outer -200
rr = 206           # lowercase round radius (geometric circle)
K = 8              # points per cap half

MASTERS = [0.0, 0.33, 0.66, 1.0]

def sm(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def clamp(v, a, b):
    return max(a, min(b, v))

# ------------------------------------------------------------------ skeleton helpers
def ellipse(cx, cy, rx, ry, a0, a1, step=12):
    n = max(2, int(math.ceil(abs(a1 - a0) / step)))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def E(cx, cy, rx, ry):
    return ellipse(cx, cy, rx, ry, 0, 360)

def A(cx, cy, rx, ry, a0, a1):
    return ellipse(cx, cy, rx, ry, a0, a1)

def P(*parts):
    out = []
    for part in parts:
        for p in part:
            if out and abs(out[-1][0] - p[0]) < 1e-6 and abs(out[-1][1] - p[1]) < 1e-6:
                continue
            out.append((float(p[0]), float(p[1])))
    return out

def subdivide(pts, maxlen=64):
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(math.ceil(d / maxlen)))
        for i in range(1, n + 1):
            out.append((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n))
    return out

def norm(strokes):
    out = []
    for s in strokes:
        if isinstance(s, tuple) and len(s) == 2 and isinstance(s[1], float):
            out.append((s[0], s[1]))
        else:
            out.append((s, 1.0))
    return out

def dot(x, y, rs=1.0):
    return ([(x, y)], rs)

# ------------------------------------------------------------------ glyph skeletons
BASE = {}   # char -> (strokes, width)

def add(ch, strokes, width):
    BASE[ch] = (strokes, width)

# ---- lowercase
add('o', [E(rr, 198, rr, 206)], 2 * rr)
add('a', [E(rr, 198, rr, 206), [(2 * rr, h), (2 * rr, 0)]], 2 * rr)
add('b', [[(0, ASC), (0, 0)], E(rr, 198, rr, 206)], 2 * rr)
add('c', [A(rr, 198, rr, 206, 38, 322)], 2 * rr)
add('d', [E(rr, 198, rr, 206), [(2 * rr, ASC), (2 * rr, 0)]], 2 * rr)
add('e', [P([(0, 198), (2 * rr, 198)], A(rr, 198, rr, 206, 0, 318))], 2 * rr)
add('f', [P([(100, 0), (100, ASC - 130)], A(230, ASC - 130, 130, 130, 180, 62)), [(0, h), (262, h)]], 300)
add('g', [E(rr, 198, rr, 206), P([(2 * rr, h), (2 * rr, -30)], A(2 * rr - 170, -30, 170, 170, 0, -152))], 2 * rr)
add('h', [[(0, ASC), (0, 0)], P(A(165, 231, 165, 165, 180, 0), [(330, 0)])], 330)
add('i', [[(0, 0), (0, h)], dot(0, 580, 1.08)], 0)
add('j', [P([(130, h), (130, -30)], A(-20, -30, 150, 170, 0, -165)), dot(130, 580, 1.08)], 130)
add('k', [[(0, ASC), (0, 0)], [(250, h), (10, 150)], [(95, 237), (272, 0)]], 272)
add('l', [[(0, ASC), (0, 0)]], 0)
add('m', [[(0, h), (0, 0)], P(A(135, 261, 135, 135, 180, 0), [(270, 0)]), P(A(405, 261, 135, 135, 180, 0), [(540, 0)])], 540)
add('n', [[(0, h), (0, 0)], P(A(165, 231, 165, 165, 180, 0), [(330, 0)])], 330)
add('p', [[(0, h), (0, DES)], E(rr, 198, rr, 206)], 2 * rr)
add('q', [E(rr, 198, rr, 206), [(2 * rr, h), (2 * rr, DES)]], 2 * rr)
add('r', [[(0, h), (0, 0)], A(165, 231, 165, 165, 180, 62)], 300)
add('s', [P(A(170, 296, 170, 100, 35, 270), A(170, 98, 170, 98, 90, -145))], 340)
add('t', [P([(100, 480), (100, 120)], A(220, 120, 120, 120, 180, 300)), [(0, h), (272, h)]], 290)
add('u', [P([(0, h), (0, 165)], A(165, 165, 165, 165, 180, 360)), [(330, h), (330, 0)]], 330)
add('v', [[(0, h), (185, 0), (370, h)]], 370)
add('w', [[(0, h), (130, 0), (260, h), (390, 0), (520, h)]], 520)
add('x', [[(0, h), (340, 0)], [(0, 0), (340, h)]], 340)
add('y', [[(0, h), (207, 0)], [(360, h), (130, DES)]], 360)
add('z', [[(0, h), (330, h), (0, 0), (330, 0)]], 330)
add('\u00e6', [E(175, 198, 175, 206), [(350, h), (350, 0)],
               P([(350, 198), (700, 198)], A(525, 198, 175, 206, 0, 318))], 700)
add('\u00f8', [E(rr, 198, rr, 206), ([(-8, -20), (2 * rr + 8, h + 20)], 0.78)], 2 * rr)

# ---- uppercase
c = 296
add('O', [E(c, 288, c, c)], 2 * c)
add('C', [A(c, 288, c, c, 40, 320)], 2 * c)
add('G', [P(A(c, 288, c, c, 40, 360), [(340, 288)])], 2 * c)
add('Q', [E(c, 288, c, c), [(390, 170), (580, -40)]], 2 * c)
add('D', [P([(0, 0), (0, CAP), (130, CAP)], A(130, 288, 270, 288, 90, -90), [(0, 0)])], 400)
add('B', [[(0, 0), (0, CAP)],
          P([(0, CAP), (150, CAP)], A(150, 436, 140, 140, 90, -90), [(0, 296)]),
          P([(0, 296), (170, 296)], A(170, 148, 170, 148, 90, -90), [(0, 0)])], 340)
add('P', [[(0, 0), (0, CAP)], P([(0, CAP), (150, CAP)], A(150, 406, 170, 170, 90, -90), [(0, 236)])], 320)
add('R', [[(0, 0), (0, CAP)], P([(0, CAP), (150, CAP)], A(150, 406, 170, 170, 90, -90), [(0, 236)]),
          [(170, 236), (345, 0)]], 345)
add('A', [[(0, 0), (250, CAP), (500, 0)], [(100, 170), (400, 170)]], 500)
add('E', [[(0, 0), (0, CAP)], [(0, CAP), (330, CAP)], [(0, 288), (290, 288)], [(0, 0), (330, 0)]], 330)
add('F', [[(0, 0), (0, CAP)], [(0, CAP), (330, CAP)], [(0, 288), (290, 288)]], 330)
add('H', [[(0, 0), (0, CAP)], [(380, 0), (380, CAP)], [(0, 288), (380, 288)]], 380)
add('I', [[(0, 0), (0, CAP)]], 0)
add('J', [P([(300, CAP), (300, 170)], A(150, 170, 150, 170, 0, -180))], 300)
add('K', [[(0, 0), (0, CAP)], [(340, CAP), (0, 240)], [(110, 349), (350, 0)]], 350)
add('L', [[(0, CAP), (0, 0), (300, 0)]], 300)
add('M', [[(0, 0), (0, CAP), (255, 130), (510, CAP), (510, 0)]], 510)
add('N', [[(0, 0), (0, CAP), (390, 0), (390, CAP)]], 390)
add('S', [P(A(190, 441, 190, 135, 35, 270), A(190, 153, 190, 153, 90, -145))], 380)
add('T', [[(0, CAP), (430, CAP)], [(215, CAP), (215, 0)]], 430)
add('U', [P([(0, CAP), (0, 190)], A(190, 190, 190, 190, 180, 360), [(380, CAP)])], 380)
add('V', [[(0, CAP), (225, 0), (450, CAP)]], 450)
add('W', [[(0, CAP), (145, 0), (290, CAP), (435, 0), (580, CAP)]], 580)
add('X', [[(0, CAP), (420, 0)], [(0, 0), (420, CAP)]], 420)
add('Y', [[(0, CAP), (210, 300), (420, CAP)], [(210, 300), (210, 0)]], 420)
add('Z', [[(0, CAP), (380, CAP), (0, 0), (380, 0)]], 380)
add('\u00c6', [[(0, 0), (300, CAP)], [(104, 200), (300, 200)], [(300, 0), (300, CAP)],
               [(300, CAP), (640, CAP)], [(300, 288), (600, 288)], [(300, 0), (640, 0)]], 640)
add('\u00d8', [E(c, 288, c, c), ([(-12, -34), (2 * c + 12, CAP + 34)], 0.8)], 2 * c)

# ---- digits
add('0', [E(210, 288, 210, 296)], 420)
add('1', [[(0, 430), (170, CAP), (170, 0)]], 170)
add('2', [P(A(200, 396, 200, 180, 165, -35), [(0, 0), (400, 0)])], 400)
add('3', [P(A(190, 438, 175, 138, 150, -90), A(190, 150, 205, 150, 90, -150))], 395)
add('4', [[(330, 0), (330, CAP)], [(330, CAP), (0, 190), (430, 190)]], 430)
add('5', [P([(350, CAP), (55, CAP), (30, 330)], A(195, 213, 195, 213, 125, -145))], 390)
add('6', [E(200, 200, 200, 208), P([(0, 208), (0, 388)], A(200, 388, 200, 188, 180, 50))], 400)
add('7', [[(0, CAP), (380, CAP), (130, 0)]], 380)
add('8', [E(200, 150, 200, 158), E(200, 440, 172, 136)], 400)
six = BASE['6'][0]
add('9', [[(400 - x, 576 - y) for x, y in s] for s in six], 400)

# ---- punctuation
add('.', [dot(0, 0, 1.12)], 0)
add(',', [([(0, 0), (-38, -125)], 0.95), dot(0, 0, 1.12)], 0)
add('!', [[(0, CAP), (0, 215)], dot(0, 0, 1.12)], 0)
add('?', [P(A(180, 410, 180, 166, 165, -90), [(180, 215)]), dot(180, 0, 1.12)], 360)
add(':', [dot(0, 0, 1.12), dot(0, h, 1.12)], 0)
add(';', [([(0, 0), (-38, -125)], 0.95), dot(0, 0, 1.12), dot(0, h, 1.12)], 0)
add('-', [[(0, 230), (230, 230)]], 230)
add('\u2013', [[(0, 230), (420, 230)]], 420)
add('\u2014', [[(0, 230), (720, 230)]], 720)
add("'", [([(0, CAP), (0, 450)], 0.85)], 0)
add('"', [([(0, CAP), (0, 450)], 0.85), ([(150, CAP), (150, 450)], 0.85)], 150)
add('(', [A(250, 288, 200, 330, 128, 232)], 150)
add(')', [A(-50, 288, 200, 330, 52, -52)], 150)
add('/', [[(0, -50), (300, CAP + 50)]], 300)
add('+', [[(0, 288), (300, 288)], [(150, 138), (150, 438)]], 300)
add('=', [[(0, 200), (300, 200)], [(0, 380), (300, 380)]], 300)

# ---- accents
def with_accent(base, new, kind, upper=False):
    strokes, w = BASE[base]
    cx = w / 2.0
    if base == 'i' or base == 'j':
        return
    if kind == 'ring':
        y = 758 if upper else 608
        extra = [(E(cx, y, 52, 52), 0.42)]
    elif kind == 'uml':
        y = 715 if upper else 575
        extra = [dot(cx - 72, y, 0.78), dot(cx + 72, y, 0.78)]
    elif kind == 'acute':
        y = 700 if upper else 560
        extra = [([(cx - 30, y), (cx + 55, y + 105)], 0.55)]
    BASE[new] = (list(strokes) + extra, w)
    SBBASE[new] = base

SBBASE = {}
with_accent('a', '\u00e5', 'ring')
with_accent('a', '\u00e4', 'uml')
with_accent('o', '\u00f6', 'uml')
with_accent('e', '\u00e9', 'acute')
with_accent('A', '\u00c5', 'ring', True)
with_accent('A', '\u00c4', 'uml', True)
with_accent('O', '\u00d6', 'uml', True)
with_accent('E', '\u00c9', 'acute', True)

SB_DEFAULT = (42, 42)
SB = {'A': (8, 8), 'V': (8, 8), 'W': (10, 10), 'X': (14, 14), 'Y': (8, 8), 'T': (12, 12),
      'v': (12, 12), 'w': (12, 12), 'x': (14, 14), 'y': (12, 12), 'z': (34, 34), 'Z': (34, 34),
      '7': (30, 30), 'L': (44, 18), 'F': (44, 22), 'P': (44, 26), 'r': (44, 16), 'f': (22, 16),
      't': (26, 26), 'j': (34, 44), 'k': (44, 14), 'K': (44, 14), '1': (30, 40), 'J': (26, 44),
      '.': (40, 40), ',': (50, 40), '\u00c6': (8, 40), '\u00e6': (36, 36), 'g': (36, 36),
      'o': (36, 36), 'c': (36, 36), 'e': (36, 36), 'a': (36, 36), 'd': (36, 40), 'b': (40, 36),
      'q': (36, 40), 'p': (40, 36), '-': (40, 40), '/': (20, 20)}

NAMES = {
    ' ': 'space', '.': 'period', ',': 'comma', '!': 'exclam', '?': 'question', ':': 'colon',
    ';': 'semicolon', '-': 'hyphen', '\u2013': 'endash', '\u2014': 'emdash', "'": 'quotesingle',
    '"': 'quotedbl', '(': 'parenleft', ')': 'parenright', '/': 'slash', '+': 'plus', '=': 'equal',
    '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six',
    '7': 'seven', '8': 'eight', '9': 'nine',
    '\u00c5': 'Aring', '\u00c4': 'Adieresis', '\u00d6': 'Odieresis', '\u00c6': 'AE',
    '\u00d8': 'Oslash', '\u00c9': 'Eacute', '\u00e5': 'aring', '\u00e4': 'adieresis',
    '\u00f6': 'odieresis', '\u00e6': 'ae', '\u00f8': 'oslash', '\u00e9': 'eacute',
}

def gname(ch):
    return NAMES.get(ch, ch)

# ------------------------------------------------------------------ geometry primitives
def capsule(p0, r0, p1, r1, k=K):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy)
    th = math.atan2(dy, dx) if d > 1e-9 else 0.0
    if d < 1e-9:
        cv = 0.0 if abs(r0 - r1) < 1e-9 else (1.0 if r0 > r1 else -1.0)
    else:
        cv = clamp((r0 - r1) / d, -1.0, 1.0)
    beta = math.acos(cv)
    pts = []
    for i in range(k + 1):
        a = th - beta + 2 * beta * i / k
        pts.append((p1[0] + r1 * math.cos(a), p1[1] + r1 * math.sin(a)))
    for i in range(k + 1):
        a = th + beta + (2 * math.pi - 2 * beta) * i / k
        pts.append((p0[0] + r0 * math.cos(a), p0[1] + r0 * math.sin(a)))
    pts.reverse()
    return pts

def circle(cx, cy, r, n=14):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    pts.reverse()
    return pts

def blob(cx, cy, rx, ry, phi, n=32):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        w = 1 + 0.10 * math.sin(2 * t + phi) + 0.07 * math.sin(3 * t + 2 * phi) + 0.04 * math.sin(5 * t + phi * 3)
        pts.append((cx + rx * w * math.cos(t), cy + ry * w * math.sin(t)))
    pts.reverse()
    return pts

# ------------------------------------------------------------------ melt deformation
def deform(x, y, m, Pm):
    e = sm(0, 1, m)
    yt, cx, hw = Pm['yt'], Pm['cx'], Pm['hw']
    u = y / yt
    uc = clamp(u, 0, 1.1)
    base = R0 - 16 * e
    if y >= R0:
        y1 = base + (y - R0) * (1 - Pm['c'] * e)
    else:
        y1 = base + (y - R0) * (1 - 0.85 * e)
    dx = (x - cx) / hw
    y1 -= 22 * e * (uc ** 1.5) * (1 - min(dx * dx, 1))
    y1 -= Pm['droop'] * e * uc * clamp(dx, -1, 1)
    x1 = x + Pm['lean'] * e * (uc ** 2) * hw * 1.5 + 10 * e * math.sin(0.017 * y + Pm['ph']) * uc
    b = 0.12 * e * (1 - min(uc, 1)) ** 2
    x1 = cx + (x1 - cx) * (1 + b)
    return (x1, y1)

def radius_at(y1, m):
    e = sm(0, 1, m)
    t = clamp((y1 - 50) / 200.0, 0, 1)
    return R0 * (1 + 0.02 * e) + 14 * e * (1 - t) ** 1.3

# ------------------------------------------------------------------ glyph model
class GlyphModel:
    pass

def build_model(ch, strokes, width, sb, is_space=False):
    G = GlyphModel()
    rnd = random.Random(ord(ch) * 7919 + 13)
    G.ch = ch
    lsb, rsb = sb
    if is_space:
        G.strokes = []
        G.adv0 = 300
        G.P = dict(yt=540, cx=150, hw=150, lean=0, ph=0, droop=0, c=0.28)
        G.rnd = rnd
        G.drips = []; G.droplets = []; G.rings = []; G.domes = []
        G.puddle = dict(cx=150, cy=34, rx=150 + 90, ry=78, phi=rnd.uniform(0, 6.28))
        G.domes = [(300 * f + rnd.uniform(-20, 20), 100 + rnd.uniform(0, 20), rnd.uniform(30, 56)) for f in (0.2, 0.5, 0.8)]
        return G
    st = norm(strokes)
    # outer extents at m=0 skeleton frame
    minx = min(x - R0 * rs for pts, rs in st for x, y in pts)
    maxx = max(x + R0 * rs for pts, rs in st for x, y in pts)
    tx = lsb - minx
    G.adv0 = int(round(maxx - minx + lsb + rsb))
    fin = []
    for pts, rs in st:
        fp = [(x + tx, y + R0) for x, y in subdivide(pts)]
        fin.append((fp, rs))
    G.strokes = fin
    ys = [y + R0 * rs for pts, rs in fin for x, y in pts]
    xs0 = minx + tx; xs1 = maxx + tx
    yt = max(ys)
    G.P = dict(yt=max(yt, 300), cx=(xs0 + xs1) / 2, hw=max((xs1 - xs0) / 2, 60),
               lean=rnd.choice([-1, 1]) * rnd.uniform(0.16, 0.36), ph=rnd.uniform(0, 6.28),
               droop=rnd.uniform(-40, 60), c=rnd.uniform(0.12, 0.19) * min(1.0, max(yt, 300) / 720.0 + 0.15))
    G.rnd = rnd
    # ---- analyse master-0 body for drip candidates
    polys = []
    for pts, rs in fin:
        if len(pts) == 1:
            polys.append(Polygon(capsule(pts[0], R0 * rs, pts[0], R0 * rs)))
        else:
            for a, b in zip(pts, pts[1:]):
                polys.append(Polygon(capsule(a, R0 * rs, b, R0 * rs)))
    U = unary_union([p.buffer(0) for p in polys])
    cands = []
    x = xs0 + 24
    while x < xs1 - 24:
        inter = U.intersection(LineString([(x, -400), (x, 1000)]))
        geoms = list(inter.geoms) if hasattr(inter, 'geoms') else [inter]
        for gm in geoms:
            if gm.is_empty or gm.geom_type != 'LineString':
                continue
            ylo = min(p[1] for p in gm.coords)
            if ylo > 170:
                cands.append((x, ylo + 30))
        x += 14
    rnd.shuffle(cands)
    chosen = []
    for cx_, cy_ in cands:
        if all(abs(cx_ - a) > 85 for a, _ in chosen):
            chosen.append((cx_, cy_))
        if len(chosen) >= 4:
            break
    sides = [(xs0 + 20, rnd.uniform(0.35, 0.8) * yt), (xs1 - 20, rnd.uniform(0.35, 0.8) * yt)]
    rnd.shuffle(sides)
    for s in sides:
        if len(chosen) >= 2:
            break
        chosen.append(s)
    G.drips = []
    G.droplets = []
    for i, (dx_, dy_) in enumerate(chosen):
        frac = 1.0 if i == 0 else rnd.uniform(0.4, 0.92)
        ys1 = deform(dx_, dy_, 1.0, G.P)[1]
        Lmax = frac * (ys1 - 105)
        if Lmax < 45:
            Lmax = max(0, ys1 - 105)
            frac = 1.0
        if Lmax < 30:
            continue
        G.drips.append(dict(x=dx_, y=dy_, frac=frac, L=Lmax))
    # droplets: for non-reaching drips
    for dr in G.drips:
        if dr['frac'] < 0.78:
            yend1 = deform(dr['x'], dr['y'], 1.0, G.P)[1] - dr['L']
            if yend1 - 80 > 150:
                G.droplets.append(dr)
    # ---- bubbles above slumped glyph
    top1 = 0
    for pts, rs in fin:
        for x_, y_ in pts:
            top1 = max(top1, deform(x_, y_, 1.0, G.P)[1] + radius_at(deform(x_, y_, 1.0, G.P)[1], 1.0) * rs)
    G.rings = []
    for i in range(3):
        r = [rnd.uniform(36, 58), rnd.uniform(22, 34), rnd.uniform(16, 24)][i]
        rx = rnd.uniform(xs0 + 30, xs1 - 30)
        ry = top1 + 40 + r + rnd.uniform(0, 90) + i * 80
        G.rings.append((rx, ry, r))
    G.domes = [(G.adv0 * f + rnd.uniform(-22, 22), 100 + rnd.uniform(0, 20), rnd.uniform(30, 56))
               for f in (0.18, 0.5, 0.82)]
    G.puddle = dict(cx=G.adv0 / 2.0, cy=34, rx=G.adv0 / 2.0 + 90, ry=78, phi=rnd.uniform(0, 6.28))
    return G

def contours(G, m):
    out = []
    # body
    for pts, rs in G.strokes:
        dp = [deform(x, y, m, G.P) for x, y in pts]
        rad = [radius_at(p[1], m) * rs for p in dp]
        if len(dp) == 1:
            out.append(capsule(dp[0], rad[0], dp[0], rad[0]))
        else:
            for i in range(len(dp) - 1):
                out.append(capsule(dp[i], rad[i], dp[i + 1], rad[i + 1]))
    # drips
    s = sm(0.05, 0.6, m)
    e2 = sm(0.10, 0.85, m)
    for dr in G.drips:
        xs, ys = deform(dr['x'], dr['y'], m, G.P)
        yend = ys - dr['L'] * e2
        out.append(capsule((xs, ys), 36 * s, (xs, yend), 22 * s))
        out.append(circle(xs, yend - 6 * s, 47 * s))
    # falling droplets
    s3 = sm(0.45, 1.0, m)
    for dr in G.droplets:
        xs, ys = deform(dr['x'], dr['y'], m, G.P)
        yend = ys - dr['L'] * e2
        out.append(circle(xs + 3, yend - 84 * s3 - 6, 30 * s3, 12))
    # puddle
    sp = sm(0.28, 0.92, m)
    pu = G.puddle
    out.append(blob(pu['cx'], pu['cy'], pu['rx'] * sp, pu['ry'] * sp, pu['phi']))
    # foam domes
    sd = sm(0.45, 1.0, m)
    for dx_, dy_, dr_ in G.domes:
        out.append(circle(dx_, dy_ * sd + 34 * (1 - sd), dr_ * sd, 14))
    # floating bubble rings
    sr = sm(0.5, 1.0, m)
    for rx_, ry_, r_ in G.rings:
        n = 12
        ring = [(rx_ + r_ * sr * math.cos(2 * math.pi * i / n), ry_ + r_ * sr * math.sin(2 * math.pi * i / n)) for i in range(n)]
        for i in range(n):
            out.append(capsule(ring[i], 11 * sr, ring[(i + 1) % n], 11 * sr, 3))
    return out

def adv_at(G, m):
    return int(round(G.adv0 * (1 + 0.05 * sm(0, 1, m))))

def to_int(conts):
    return [[(int(round(x)), int(round(y))) for x, y in c] for c in conts]

def make_glyph(conts_int):
    g = Glyph()
    pts = []
    ends = []
    for c in conts_int:
        pts.extend(c)
        ends.append(len(pts) - 1)
    g.numberOfContours = len(conts_int)
    g.coordinates = GlyphCoordinates(pts)
    g.endPtsOfContours = ends
    g.flags = bytearray([1] * len(pts))
    if len(g.flags):
        g.flags[0] |= 0x40       # overlapping contours
    g.program = ttProgram.Program()
    g.program.fromBytecode(b"")
    return g

# ------------------------------------------------------------------ build
def build(out_path):
    chars = []
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789":
        chars.append(ch)
    chars += list(".,:;!?-'\"()/+=") + ['\u2013', '\u2014']
    chars += ['\u00c6', '\u00d8', '\u00c5', '\u00e6', '\u00f8', '\u00e5', '\u00c4', '\u00d6', '\u00e4', '\u00f6', '\u00c9', '\u00e9']

    order = ['.notdef', 'space']
    cmap = {32: 'space'}
    models = {}
    models['space'] = build_model(' ', [], 0, (0, 0), is_space=True)
    for ch in chars:
        strokes, w = BASE[ch]
        sbch = SBBASE.get(ch, ch)
        sb = SB.get(sbch, SB_DEFAULT)
        models[gname(ch)] = build_model(ch, strokes, w, sb)
        order.append(gname(ch))
        cmap[ord(ch)] = gname(ch)

    glyphs = {'.notdef': None}
    metrics = {}
    variations = {}
    total_pts = 0
    for name in order:
        if name == '.notdef':
            continue
        G = models[name]
        masters = []
        for m in MASTERS:
            masters.append(to_int(contours(G, m)))
        n0 = [len(c) for c in masters[0]]
        for mm in masters[1:]:
            assert [len(c) for c in mm] == n0, name
        g0 = make_glyph(masters[0])
        glyphs[name] = g0
        total_pts += len(g0.coordinates)
        xmin = min(p[0] for c in masters[0] for p in c)
        a0 = adv_at(G, 0.0)
        metrics[name] = (a0, xmin)
        flat0 = [p for c in masters[0] for p in c]
        tvs = []
        for i, m in enumerate(MASTERS):
            if i == 0:
                continue
            flat = [p for c in masters[i] for p in c]
            deltas = [(a[0] - b[0], a[1] - b[1]) for a, b in zip(flat, flat0)]
            dadv = adv_at(G, m) - a0
            deltas += [(0, 0), (dadv, 0), (0, 0), (0, 0)]
            lo = MASTERS[i - 1]
            pk = m
            hi = MASTERS[i + 1] if i + 1 < len(MASTERS) else 1.0
            tvs.append(TupleVariation({'MELT': (lo, pk, hi)}, deltas))
        variations[name] = tvs

    # .notdef: simple rounded box outline (no variation)
    box = [(0, 0), (0, 576), (330, 576), (330, 0), (0, 0)]
    nd = []
    for a, b in zip(box, box[1:]):
        nd.append(capsule((a[0] + 72, a[1] + 72), 60, (b[0] + 72, b[1] + 72), 60))
    glyphs['.notdef'] = make_glyph(to_int(nd))
    metrics['.notdef'] = (560, min(p[0] for c in to_int(nd) for p in c))

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf({n: glyphs[n] for n in order})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=950, descent=-300, lineGap=0)
    fam = 'BT Sm\u00f6r'
    fb.setupNameTable({'familyName': fam, 'styleName': 'Regular',
                       'uniqueFontIdentifier': 'BTSmor-Regular-1.000',
                       'fullName': fam, 'psName': 'BTSmor-Regular',
                       'version': 'Version 1.000'})
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-300, sTypoLineGap=0, usWinAscent=1000, usWinDescent=330,
                sCapHeight=720, sxHeight=540, usWeightClass=800, achVendID='BTSM', fsType=0)
    fb.setupPost()
    fb.setupFvar([('MELT', 0, 0, 100, 'Meltiness')],
                 [{'location': {'MELT': 0}, 'stylename': 'Solid'},
                  {'location': {'MELT': 33}, 'stylename': 'Soft'},
                  {'location': {'MELT': 66}, 'stylename': 'Gooey'},
                  {'location': {'MELT': 100}, 'stylename': 'Puddle'}])
    fb.setupGvar(variations)
    from fontTools.ttLib import newTable
    gasp = newTable('gasp')
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    fb.font['gasp'] = gasp
    fb.save(out_path)
    print('saved', out_path, 'glyphs', len(order), 'points(default)', total_pts)

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/BTSmor-VF.ttf')
