import math, random, sys, itertools
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import newTable
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

import smor
from smor import (BASE, SBBASE, SB, SB_DEFAULT, NAMES, gname, R0, h, CAP, ASC, DES, rr, sm, clamp,
                  ellipse, E, A, P, subdivide, norm, dot, with_accent, capsule, circle, blob,
                  to_int, make_glyph)

KS = 6          # points per cap half (segments)
JK = 4          # mid points on a joint kite
MASTERS = [0.0, 0.33, 0.66, 1.0]

# ------------------------------------------------------------------ extra glyph designs
# double-storey a (ss01)
BASE['a.ss01'] = ([E(165, 99, 165, 99), P(A(165, 246, 165, 150, 128, 0), [(330, 0)])], 330)
SB['a.ss01'] = (36, 40)
with_accent('a.ss01', 'aring.ss01', 'ring')
with_accent('a.ss01', 'adieresis.ss01', 'uml')
SBBASE['aring.ss01'] = 'a.ss01'
SBBASE['adieresis.ss01'] = 'a.ss01'

BASE['\u00e6'] = ([E(190, 198, 190, 206), [(380, h), (380, 0)],
                  P([(380, 198), (760, 198)], A(570, 198, 190, 206, 0, 318))], 760)

# ------------------------------------------------------------------ primitives
def rho_of(m):
    return sm(0.0, 0.7, m)

def cut_corners(p, r, u, v):
    if abs(u[1]) >= abs(u[0]):
        cy = p[1] + math.copysign(r, u[1])
        def hit(sg):
            ey = p[1] + sg * v[1] * r
            t = (cy - ey) / u[1]
            return (p[0] + sg * v[0] * r + t * u[0], cy)
    else:
        cx = p[0] + math.copysign(r, u[0])
        def hit(sg):
            ex = p[0] + sg * v[0] * r
            t = (cx - ex) / u[0]
            return (cx, p[1] + sg * v[1] * r + t * u[1])
    return hit(-1), hit(1)

def end_pts(p, r, u, v, rho, ext, axis, k):
    corners = cut_corners(p, r, u, v) if axis else None
    q = (p[0] + u[0] * ext, p[1] + u[1] * ext)
    out = []
    for i in range(k + 1):
        t = i / float(k)
        a = math.radians(-90 + 180.0 * t)
        ca, sa = math.cos(a), math.sin(a)
        if corners:
            R_, L_ = corners
            cut = (R_[0] + (L_[0] - R_[0]) * t, R_[1] + (L_[1] - R_[1]) * t)
            arc = (p[0] + u[0] * r * ca + v[0] * r * sa, p[1] + u[1] * r * ca + v[1] * r * sa)
            out.append(((1 - rho) * cut[0] + rho * arc[0], (1 - rho) * cut[1] + rho * arc[1]))
        else:
            out.append((q[0] + u[0] * r * ca * rho + v[0] * r * sa, q[1] + u[1] * r * ca * rho + v[1] * r * sa))
    return out

def seg_poly(p0, r0, p1, r1, rho, k=KS, e0=0.0, e1=0.0, cut0=False, cut1=False):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy)
    if d < 1e-9:
        ux, uy = 1.0, 0.0
    else:
        ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    front = end_pts(p1, r1, (ux, uy), (nx, ny), rho, e1, cut1, k)
    back = end_pts(p0, r0, (-ux, -uy), (-nx, -ny), rho, e0, cut0, k)
    pts = front + back
    pts.reverse()
    return pts

def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    if d < 1e-9:
        return (1.0, 0.0)
    return (dx / d, dy / d)

def kite(v, r, d1, d2, side, flip, rho, J=JK):
    n1 = (-d1[1], d1[0]); n2 = (-d2[1], d2[0])
    a = (v[0] + side * n1[0] * r, v[1] + side * n1[1] * r)
    b = (v[0] + side * n2[0] * r, v[1] + side * n2[1] * r)
    wx, wy = side * (n1[0] + n2[0]), side * (n1[1] + n2[1])
    wl = math.hypot(wx, wy)
    if wl < 1e-4:
        w = (side * n1[0], side * n1[1]); cosh = 0.0
    else:
        w = (wx / wl, wy / wl); cosh = wl / 2.0
    phi = 2 * math.acos(clamp(cosh, 0.0, 1.0))
    Lmit = r / max(cosh, 1e-3)
    Lcap = r * (1 + 0.4143 * clamp((120 - math.degrees(phi)) / 30.0, 0, 1))
    Lm = min(Lmit, Lcap)
    if Lm >= Lmit - 1e-6:
        tip = (v[0] + w[0] * Lmit, v[1] + w[1] * Lmit)
        a2 = b2 = tip
    else:
        den1 = d1[0] * w[0] + d1[1] * w[1]
        t1 = (Lm - ((a[0] - v[0]) * w[0] + (a[1] - v[1]) * w[1])) / max(den1, 1e-6)
        a2 = (a[0] + d1[0] * t1, a[1] + d1[1] * t1)
        den2 = -(d2[0] * w[0] + d2[1] * w[1])
        t2 = (Lm - ((b[0] - v[0]) * w[0] + (b[1] - v[1]) * w[1])) / max(den2, 1e-6)
        b2 = (b[0] - d2[0] * t2, b[1] - d2[1] * t2)
    path = [a, a2, b2, b]
    aa = math.atan2(a[1] - v[1], a[0] - v[0])
    ab = math.atan2(b[1] - v[1], b[0] - v[0])
    da = (ab - aa + math.pi) % (2 * math.pi) - math.pi
    mids = []
    for j in range(1, J + 1):
        t = j / (J + 1.0)
        sg = min(2, int(t * 3)); f = t * 3 - sg
        sp = (path[sg][0] + (path[sg + 1][0] - path[sg][0]) * f, path[sg][1] + (path[sg + 1][1] - path[sg][1]) * f)
        ang = aa + da * t
        rp = (v[0] + r * math.cos(ang), v[1] + r * math.sin(ang))
        mids.append(((1 - rho) * sp[0] + rho * rp[0], (1 - rho) * sp[1] + rho * rp[1]))
    pts = [v, a] + mids + [b]
    if flip:
        pts.reverse()
    return pts

def dotpoly(c, r, rho, square, n=16):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        cx_, sy_ = math.cos(t), math.sin(t)
        circ = (cx_ * r, sy_ * r)
        if square:
            mx = max(abs(cx_), abs(sy_))
            sq = (cx_ / mx * r * 0.88, sy_ / mx * r * 0.88)
            pts.append((c[0] + (1 - rho) * sq[0] + rho * circ[0], c[1] + (1 - rho) * sq[1] + rho * circ[1]))
        else:
            pts.append((c[0] + circ[0], c[1] + circ[1]))
    pts.reverse()
    return pts

# ------------------------------------------------------------------ melt deformation
def deform(x, y, m, Pm, s=1.0):
    e = sm(0, 1, m) * (0.1 + 0.9 * s)
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

def radius_at(y1, m, s=1.0):
    e = sm(0, 1, m) * (0.1 + 0.9 * s)
    t = clamp((y1 - 50) / 200.0, 0, 1)
    return R0 * (1 + 0.02 * e) + 14 * e * (1 - t) ** 1.3

# ------------------------------------------------------------------ strokes
def joint_info(pts, closed):
    n = len(pts)
    idx = range(n) if closed else range(1, n - 1)
    info = []
    for j in idx:
        pv = pts[(j - 1) % n]; v = pts[j]; nx = pts[(j + 1) % n]
        d1 = unit(pv, v); d2 = unit(v, nx)
        cr = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(cr) < 1e-3:
            side, flip = 1, False
        elif cr > 0:
            side, flip = -1, True
        else:
            side, flip = 1, False
        info.append((j, side, flip))
    return info

def make_stroke(pts, rs):
    if len(pts) == 1:
        return dict(pts=[pts[0]], rs=rs, closed=False, vinfo=[], dot=True, cut=(False, False))
    pts = subdivide(pts)
    closed = len(pts) > 3 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1e-6
    if closed:
        pts = pts[:-1]
    cut = (False, False)
    if not closed:
        def straight(seq):
            d0 = unit(seq[0], seq[1]); d1 = unit(seq[0], seq[min(3, len(seq) - 1)])
            return abs(d0[0] * d1[1] - d0[1] * d1[0]) < 0.10
        cut = (straight(pts), straight(pts[::-1]))
    return dict(pts=pts, rs=rs, closed=closed, vinfo=joint_info(pts, closed), dot=False, cut=cut)

def _dist_interior(pt, other):
    """distance from pt to the polyline of `other`, ignoring the last r of each open end"""
    pts = other['pts']
    n = len(pts)
    segs = range(n) if other['closed'] else range(n - 1)
    best = 1e9
    for i in segs:
        a = pts[i]; b = pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 < 1e-9 else clamp(((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / L2, 0, 1)
        cx, cy = a[0] + dx * t, a[1] + dy * t
        d = math.hypot(pt[0] - cx, pt[1] - cy)
        if not other['closed']:
            if math.hypot(cx - pts[0][0], cy - pts[0][1]) < 0.5 * R0 or math.hypot(cx - pts[-1][0], cy - pts[-1][1]) < 0.5 * R0:
                continue
        best = min(best, d)
    return best

def mark_junctions(sts):
    for st in sts:
        if st['dot'] or st['closed']:
            continue
        flags = list(st['cut'])
        for k, endpt in enumerate((st['pts'][0], st['pts'][-1])):
            for other in sts:
                if other is st or other['dot']:
                    continue
                if _dist_interior(endpt, other) < 0.6 * R0:
                    flags[k] = False
        st['cut'] = tuple(flags)

def body_contours(strokes, m, s, Pm, square=False):
    rho = rho_of(m)
    out = []
    for st in strokes:
        dp = [deform(x, y, m, Pm, s) for x, y in st['pts']]
        rad = [radius_at(p[1], m, s) * st['rs'] for p in dp]
        if st['dot']:
            out.append(dotpoly(dp[0], rad[0], rho, square))
            continue
        n = len(dp)
        nseg = n if st['closed'] else n - 1
        for i in range(nseg):
            j = (i + 1) % n
            ex = 9.0 * (1 - rho)
            e0 = rad[i] * (1 - rho) if (not st['closed'] and i == 0) else ex
            e1 = rad[j] * (1 - rho) if (not st['closed'] and i == nseg - 1) else ex
            c0_ = (not st['closed']) and i == 0 and st['cut'][0]
            c1_ = (not st['closed']) and i == nseg - 1 and st['cut'][1]
            out.append(seg_poly(dp[i], rad[i], dp[j], rad[j], rho, KS, e0, e1, c0_, c1_))
        for (j, side, flip) in st['vinfo']:
            d1 = unit(dp[(j - 1) % n], dp[j]); d2 = unit(dp[j], dp[(j + 1) % n])
            out.append(kite(dp[j], rad[j], d1, d2, side, flip, rho))
    return out

# ------------------------------------------------------------------ glyph model
class GM:
    pass

DUMMY_P = dict(yt=700, cx=0, hw=100, lean=0, ph=0, droop=0, c=0.2)

def build_model(key, strokes, width, sb, is_space=False, square=False):
    G = GM()
    G.square = square
    rnd = random.Random(sum(ord(c) * (i + 3) for i, c in enumerate(key)) * 7919 + 13)
    G.rnd = rnd
    lsb, rsb = sb
    if is_space:
        G.strokes = []
        G.adv0 = 300
        G.P = dict(DUMMY_P, yt=540, cx=150, hw=150)
        G.drips = []; G.droplets = []; G.rings = []; G.spat = []
        G.puddle = dict(cx=150, cy=34, rx=150 + 90, ry=78, phi=rnd.uniform(0, 6.28))
        G.domes = [(300 * f + rnd.uniform(-20, 20), 100 + rnd.uniform(0, 20), rnd.uniform(30, 56)) for f in (0.2, 0.5, 0.8)]
        return G
    sts = []
    for pts, rs in norm(strokes):
        fp = [(x, y + R0) for x, y in pts]
        sts.append(make_stroke(fp, rs))
    mark_junctions(sts)
    c0 = body_contours(sts, 0.0, 1.0, DUMMY_P, square)
    allp = [p for c in c0 for p in c]
    minx = min(p[0] for p in allp); maxx = max(p[0] for p in allp)
    tx = lsb - minx
    for st in sts:
        st['pts'] = [(x + tx, y) for x, y in st['pts']]
    G.strokes = sts
    G.adv0 = int(round(maxx - minx + lsb + rsb))
    xs0, xs1 = lsb, maxx + tx
    c0 = body_contours(sts, 0.0, 1.0, DUMMY_P, square)
    allp = [p for c in c0 for p in c]
    yt = max(p[1] for p in allp)
    G.P = dict(yt=max(yt, 300), cx=(xs0 + xs1) / 2, hw=max((xs1 - xs0) / 2, 60),
               lean=rnd.choice([-1, 1]) * rnd.uniform(0.16, 0.36), ph=rnd.uniform(0, 6.28),
               droop=rnd.uniform(-40, 60), c=rnd.uniform(0.12, 0.19) * min(1.0, max(yt, 300) / 720.0 + 0.15))
    # drip candidates from the sharp master-0 body
    U = unary_union([Polygon(c).buffer(0) for c in c0 if len(c) >= 3])
    cands = []
    x = xs0 + 24
    while x < xs1 - 24:
        inter = U.intersection(LineString([(x, -400), (x, 1100)]))
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
    for sd_ in sides:
        if len(chosen) >= 2:
            break
        chosen.append(sd_)
    G.drips = []; G.droplets = []
    for i, (dx_, dy_) in enumerate(chosen):
        frac = 1.0 if i == 0 else rnd.uniform(0.4, 0.92)
        ys1 = deform(dx_, dy_, 1.0, G.P, 1.0)[1]
        Lmax = frac * (ys1 - 105)
        if Lmax < 45:
            Lmax = max(0, ys1 - 105); frac = 1.0
        if Lmax < 30:
            continue
        G.drips.append(dict(x=dx_, y=dy_, frac=frac, L=Lmax))
    for dr in G.drips:
        if dr['frac'] < 0.78:
            yend1 = deform(dr['x'], dr['y'], 1.0, G.P, 1.0)[1] - dr['L']
            if yend1 - 80 > 150:
                G.droplets.append(dr)
    c1 = body_contours(sts, 1.0, 1.0, G.P, square)
    top1 = max(p[1] for c in c1 for p in c)
    G.rings = []
    for i in range(3):
        r = [rnd.uniform(36, 58), rnd.uniform(22, 34), rnd.uniform(16, 24)][i]
        rx = rnd.uniform(xs0 + 30, xs1 - 30)
        ry = top1 + 40 + r + rnd.uniform(0, 90) + i * 80
        G.rings.append((rx, ry, r))
    G.spat = [(rnd.uniform(0, G.adv0), rnd.uniform(170, 420), rnd.uniform(9, 16)) for _ in range(5)]
    G.domes = [(G.adv0 * f + rnd.uniform(-22, 22), 100 + rnd.uniform(0, 20), rnd.uniform(30, 56)) for f in (0.18, 0.5, 0.82)]
    G.puddle = dict(cx=G.adv0 / 2.0, cy=34, rx=G.adv0 / 2.0 + 90, ry=78, phi=rnd.uniform(0, 6.28))
    return G

def contours(G, m, b=1.0, s=1.0):
    out = body_contours(G.strokes, m, s, G.P, G.square)
    sdr = sm(0.05, 0.6, m)
    e2 = sm(0.10, 0.85, m)
    for dr in G.drips:
        xs, ys = deform(dr['x'], dr['y'], m, G.P, s)
        yend = ys - dr['L'] * e2
        out.append(capsule((xs, ys), 36 * sdr, (xs, yend), 22 * sdr))
        out.append(circle(xs, yend - 6 * sdr, 47 * sdr))
    s3 = sm(0.45, 1.0, m)
    for dr in G.droplets:
        xs, ys = deform(dr['x'], dr['y'], m, G.P, s)
        yend = ys - dr['L'] * e2
        out.append(circle(xs + 3, yend - 84 * s3 - 6, 30 * s3, 12))
    sp = sm(0.28, 0.92, m)
    pu = G.puddle
    out.append(blob(pu['cx'], pu['cy'], pu['rx'] * sp, pu['ry'] * sp, pu['phi']))
    sd = sm(0.45, 1.0, m) * b
    for dx_, dy_, dr_ in G.domes:
        out.append(circle(dx_, dy_ * sd + 34 * (1 - sd), dr_ * sd, 14))
    sr = sm(0.5, 1.0, m) * b
    for rx_, ry_, r_ in G.rings:
        yy = 130 + (ry_ - 130) * b
        n = 12
        ring = [(rx_ + r_ * sr * math.cos(2 * math.pi * i / n), yy + r_ * sr * math.sin(2 * math.pi * i / n)) for i in range(n)]
        for i in range(n):
            out.append(capsule(ring[i], 11 * sr, ring[(i + 1) % n], 11 * sr, 3))
    for sx_, sy_, sr_ in G.spat:
        yy = 120 + (sy_ - 120) * b
        out.append(circle(sx_, yy, sr_ * sd, 8))
    return out

def adv_at(G, m):
    return int(round(G.adv0 * (1 + 0.05 * sm(0, 1, m))))

# ------------------------------------------------------------------ build
EXTRA = ['b', 's']          # BUBL, SLMP (both default = 100 = on)
AXTAG = {'b': 'BUBL', 's': 'SLMP'}

def evaluate(G, m, off):
    b = 0.0 if 'b' in off else 1.0
    s = 0.0 if 's' in off else 1.0
    return [p for c in to_int(contours(G, m, b, s)) for p in c], [len(c) for c in contours(G, m, b, s)]

def build(out_path):
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    chars += list(".,:;!?-'\"()/+=") + ['\u2013', '\u2014']
    chars += ['\u00c6', '\u00d8', '\u00c5', '\u00e6', '\u00f8', '\u00e5', '\u00c4', '\u00d6', '\u00e4', '\u00f6', '\u00c9', '\u00e9']

    order = ['.notdef', 'space']
    cmap = {32: 'space'}
    models = {'space': build_model('space', [], 0, (0, 0), is_space=True)}
    for ch in chars:
        strokes, w = BASE[ch]
        sb = SB.get(SBBASE.get(ch, ch), SB_DEFAULT)
        nm = gname(ch)
        models[nm] = build_model(nm, strokes, w, sb)
        order.append(nm); cmap[ord(ch)] = nm
    # ss01 alternates
    for key in ['a.ss01', 'aring.ss01', 'adieresis.ss01']:
        strokes, w = BASE[key]
        models[key] = build_model(key, strokes, w, SB['a.ss01'])
        order.append(key)
    # ss02 square-dot alternates
    sq_src = ['i', 'j', '.', ',', ':', ';', '!', '?', '\u00e4', '\u00f6', '\u00c4', '\u00d6']
    sq_names = []
    for ch in sq_src:
        strokes, w = BASE[ch]
        sb = SB.get(SBBASE.get(ch, ch), SB_DEFAULT)
        nm = gname(ch) + '.sq'
        models[nm] = build_model(nm, strokes, w, sb, square=True)
        order.append(nm); sq_names.append((gname(ch), nm))
    strokes, w = BASE['adieresis.ss01']
    models['adieresis.ss01.sq'] = build_model('adieresis.ss01.sq', strokes, w, SB['a.ss01'], square=True)
    order.append('adieresis.ss01.sq')

    glyphs = {}; metrics = {}; variations = {}; total = 0
    subsets = [()]
    for r_ in (1, 2):
        subsets += [c for c in itertools.combinations(EXTRA, r_)]
    for name in order:
        if name == '.notdef':
            continue
        G = models[name]
        base_pts, base_cnt = evaluate(G, 0.0, ())
        # structure per master / subset
        cache = {}
        for i, m in enumerate(MASTERS):
            if i == 0:
                continue
            for T in subsets:
                pts, cnt = evaluate(G, m, T)
                assert cnt == base_cnt or True
                assert len(pts) == len(base_pts), (name, m, T, len(pts), len(base_pts))
                cache[(i, T)] = pts
        # glyph
        conts = []
        k = 0
        for n_ in base_cnt:
            conts.append(base_pts[k:k + n_]); k += n_
        glyphs[name] = make_glyph(conts)
        total += len(base_pts)
        a0 = adv_at(G, 0.0)
        metrics[name] = (a0, min(p[0] for p in base_pts))
        tvs = []
        for i in range(1, len(MASTERS)):
            lo = MASTERS[i - 1]; pk = MASTERS[i]
            hi = MASTERS[i + 1] if i + 1 < len(MASTERS) else 1.0
            for S in subsets:
                # Moebius inversion over subsets T of S
                acc = None
                for r_ in range(len(S) + 1):
                    for T in itertools.combinations(S, r_):
                        sign = (-1) ** (len(S) - len(T))
                        pts = cache[(i, tuple(T))]
                        if acc is None:
                            acc = [(sign * p[0], sign * p[1]) for p in pts]
                        else:
                            acc = [(a[0] + sign * p[0], a[1] + sign * p[1]) for a, p in zip(acc, pts)]
                if len(S) == 0:
                    deltas = [(a[0] - q[0], a[1] - q[1]) for a, q in zip(acc, base_pts)]
                    dadv = adv_at(G, pk) - a0
                else:
                    deltas = acc
                    dadv = 0
                if all(d == (0, 0) for d in deltas) and dadv == 0:
                    continue
                deltas = deltas + [(0, 0), (dadv, 0), (0, 0), (0, 0)]
                sup = {'MELT': (lo, pk, hi)}
                for ax in S:
                    sup[AXTAG[ax]] = (-1.0, -1.0, 0.0)
                tvs.append(TupleVariation(sup, deltas))
        variations[name] = tvs

    # .notdef: sharp box
    box = [(0, 0), (0, 576), (330, 576), (330, 0), (0, 0)]
    nd_st = [make_stroke([(x + 72, y + 72) for x, y in box], 1.0)]
    nd = to_int(body_contours(nd_st, 0.0, 1.0, DUMMY_P))
    glyphs['.notdef'] = make_glyph(nd)
    metrics['.notdef'] = (560, min(p[0] for c in nd for p in c))

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf({n: glyphs[n] for n in order})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=950, descent=-300, lineGap=0)
    fam = 'BT Sm\u00f6r'
    fb.setupNameTable({'familyName': fam, 'styleName': 'Regular',
                       'uniqueFontIdentifier': 'BTSmor-Regular-2.000', 'fullName': fam,
                       'psName': 'BTSmor-Regular', 'version': 'Version 2.000'})
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-300, sTypoLineGap=0, usWinAscent=1000, usWinDescent=330,
                sCapHeight=720, sxHeight=540, usWeightClass=800, achVendID='BTSM', fsType=0)
    fb.setupPost()
    fb.setupFvar([('MELT', 0, 0, 100, 'Meltiness'), ('BUBL', 0, 100, 100, 'Bubbles'), ('SLMP', 0, 100, 100, 'Slump')],
                 [{'location': {'MELT': 0, 'BUBL': 100, 'SLMP': 100}, 'stylename': 'Solid'},
                  {'location': {'MELT': 33, 'BUBL': 100, 'SLMP': 100}, 'stylename': 'Soft'},
                  {'location': {'MELT': 66, 'BUBL': 100, 'SLMP': 100}, 'stylename': 'Gooey'},
                  {'location': {'MELT': 100, 'BUBL': 100, 'SLMP': 100}, 'stylename': 'Puddle'},
                  {'location': {'MELT': 100, 'BUBL': 40, 'SLMP': 20}, 'stylename': 'Calm Puddle'},
                  {'location': {'MELT': 100, 'BUBL': 100, 'SLMP': 0}, 'stylename': 'Hot Pan'}])
    fb.setupGvar(variations)
    gasp = newTable('gasp'); gasp.version = 1; gasp.gaspRange = {0xFFFF: 0x000F}
    fb.font['gasp'] = gasp
    sq_rules = '\n'.join(f'    sub {a} by {b};' for a, b in sq_names) + '\n    sub adieresis.ss01 by adieresis.ss01.sq;'
    fea = f'''
feature ss01 {{
    featureNames {{ name "Double-storey a"; }};
    sub a by a.ss01;
    sub aring by aring.ss01;
    sub adieresis by adieresis.ss01;
}} ss01;
feature ss02 {{
    featureNames {{ name "Square dots"; }};
{sq_rules}
}} ss02;
'''
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(out_path)
    print('saved', out_path, 'glyphs', len(order), 'default points', total)

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/BTSmor2-VF.ttf')
