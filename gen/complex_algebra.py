"""Topic complex_algebra: algebraic form of complex numbers (Grade 11 Advanced ch. 7 lesson 1, examined at BacII science).
Parametric rows are built here; hand rows live in complex_algebra_hand.py. Every value comes from exact arithmetic."""
import sys, os, re, random, hashlib, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from cg_core import tidy

TOPIC = "complex_algebra"
rng = random.Random(20261105)
ROWS = []
SEEN = set()
K = lambda *a: rng.choice(a)
Q = sp.Rational
RT = sp.sqrt

# ---------- exact complex arithmetic and display ----------

def mm(c, s):
    """Coefficient times a term: never print two numbers side by side."""
    s = str(s)
    return f"{c}{s}" if s.startswith("(") or s.startswith("\\left") else f"{c}\\times {s}"

def nt(q):
    """LaTeX of a real number, no spaces."""
    return sp.latex(sp.sympify(q)).replace(" ", "")

class Z:
    __slots__ = ("a", "b")
    def __init__(s, a=0, b=0):
        s.a = sp.expand(sp.sympify(a))
        s.b = sp.expand(sp.sympify(b))
    @staticmethod
    def w(o):
        return o if isinstance(o, Z) else Z(o, 0)
    def __add__(s, o): o = Z.w(o); return Z(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __neg__(s): return Z(-s.a, -s.b)
    def __sub__(s, o): o = Z.w(o); return Z(s.a - o.a, s.b - o.b)
    def __rsub__(s, o): return Z.w(o) - s
    def __mul__(s, o):
        o = Z.w(o)
        return Z(sp.expand(s.a * o.a - s.b * o.b), sp.expand(s.a * o.b + s.b * o.a))
    __rmul__ = __mul__
    def __truediv__(s, o):
        o = Z.w(o); n = o.n2(); t = s * o.c()
        return Z(sp.radsimp(t.a / n), sp.radsimp(t.b / n))
    def __rtruediv__(s, o): return Z.w(o) / s
    def __pow__(s, n):
        r = Z(1, 0)
        for _ in range(n): r = r * s
        return r
    def __eq__(s, o):
        o = Z.w(o); return sp.expand(s.a - o.a) == 0 and sp.expand(s.b - o.b) == 0
    def __hash__(s): return hash((s.a, s.b))
    def c(s): return Z(s.a, -s.b)
    def n2(s): return sp.expand(s.a ** 2 + s.b ** 2)
    def mod(s): return sp.sqrt(s.n2())
    def isint(s): return s.a.is_integer and s.b.is_integer
    def tex(s, v="i"):
        a, b = s.a, s.b
        if b == 0: return nt(a)
        neg = bool(b < 0)
        ab = sp.expand(-b) if neg else b
        if ab == 1: im = v
        elif ab.is_Rational and ab.is_integer: im = nt(ab) + v
        elif ab.is_Rational: im = nt(ab) + v
        elif ab.is_Add:
            tg = sp.together(ab)
            im = (nt(tg) + v) if tg.is_Mul else (r"\left(" + nt(ab) + r"\right)" + v)
        else:
            c_, r_ = ab.as_coeff_Mul()
            if c_ == 1: im = v + nt(r_)
            elif c_.is_integer: im = nt(c_) + v + nt(r_)
            else: im = nt(ab) + v
        if a == 0: return ("-" if neg else "") + im
        return nt(sp.together(a) if a.is_Add else a) + ("-" if neg else "+") + im
    def p(s):
        t = s.tex()
        return "(" + t + ")" if (s.a != 0 and s.b != 0) or t.startswith("-") else t
    def py(s):
        return f"(({s.a})+({s.b})*I)"
    def __repr__(s): return s.tex()

I_ = Z(0, 1)
def G(lo=-6, hi=6, nz=True):
    while True:
        a, b = rng.randint(lo, hi), rng.randint(lo, hi)
        if not nz or (a != 0 and b != 0):
            return Z(a, b)
def key(z): return (str(z.a), str(z.b))

def tsum(terms):
    """terms: (coef, suffix). Drops zeros and unit coefficients."""
    out = ""
    for c, sfx in terms:
        c = sp.sympify(c)
        if c == 0: continue
        neg = c < 0; ac = -c if neg else c
        body = (nt(ac) if (ac != 1 or not sfx) else "") + sfx
        out += ("-" if neg else ("+" if out else "")) + body
    return out or "0"

def chain(*items):
    o = []
    for t in items:
        if not o or o[-1] != t: o.append(t)
    return "=".join(o)

def mul_chain(u, v):
    """List of chain items expanding u*v, for Gaussian rationals."""
    a, b, c, d = u.a, u.b, v.a, v.b
    r = u * v
    l1 = tsum([(a * c, ""), (a * d, "i"), (b * c, "i"), (b * d, "i^{2}")])
    l2 = tsum([(a * c, ""), (a * d + b * c, "i"), (-b * d, "")])
    return [l1, l2, r.tex()]

def div_chain(u, v):
    """Items for u/v by the conjugate of v, starting from the fraction."""
    n = u * v.c(); d = v.n2(); r = u / v
    items = [rf"\frac{{{u.tex()}}}{{{v.tex()}}}"]
    if v.b != 0:
        items.append(rf"\frac{{{u.p()}{v.c().p()}}}{{{v.p()}{v.c().p()}}}")
        items.append(rf"\frac{{{n.tex()}}}{{{nt(v.a**2)}+{nt(v.b**2)}}}" if v.a != 0 else rf"\frac{{{n.tex()}}}{{{nt(d)}}}")
        items.append(rf"\frac{{{n.tex()}}}{{{nt(d)}}}")
    if d == 1: items = items[:2]
    items.append(r.tex())
    return items

def ptex(cs, v="z"):
    """Polynomial LaTeX from coefficient list (Z or numbers), highest first."""
    n = len(cs) - 1; out = ""
    for k, c in enumerate(cs):
        c = Z.w(c); e = n - k
        if c == 0: continue
        pw = "" if e == 0 else (v if e == 1 else f"{v}^{{{e}}}")
        if c.b == 0:
            neg = c.a < 0; body = (nt(abs(c.a)) if abs(c.a) != 1 or not pw else "") + pw
        elif c.a == 0:
            neg = c.b < 0
            t = (-c if neg else c).tex(); body = t + pw
        else:
            if e == 0:
                t = c.tex(); out += ("" if t.startswith("-") or not out else "+") + t
                continue
            neg = c.a < 0
            body = "(" + (-c if neg else c).tex() + ")" + pw
        out += ("-" if neg else ("+" if out else "")) + body
    return out or "0"

def peval(cs, r):
    acc = Z(0, 0)
    for c in cs: acc = acc * r + Z.w(c)
    return acc
def pchk(cs, r):
    """SymPy string of P(r) term by term from the coefficients in the problem."""
    n = len(cs) - 1
    return "expand(" + "+".join(f"{Z.w(c).py()}*{r.py()}**{n-k}" for k, c in enumerate(cs)) + ")"
def pmul(p, q):
    out = [Z(0, 0) for _ in range(len(p) + len(q) - 1)]
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] = out[i + j] + Z.w(a) * Z.w(b)
    return out
def pfrom(rs, lead=1):
    p = [Z(lead)]
    for r in rs: p = pmul(p, [Z(1), -Z.w(r)])
    return p
def pxstr(cs):
    n = len(cs) - 1
    return "+".join(f"{Z.w(c).py()}*x**{n-k}" for k, c in enumerate(cs))

def labels(n=None):
    st = K(["ក.", "ខ.", "គ.", "ឃ.", "ង.", "ច."], ["ក-", "ខ-", "គ-", "ឃ-", "ង-", "ច-"],
           ["១.", "២.", "៣.", "៤.", "៥.", "៦."], ["a.", "b.", "c.", "d.", "e.", "f."])
    return st

KH = re.compile(r"[\u1780-\u17FF]")
def lengthen(p):
    """Bare drill prompts get the fuller wording of the guide."""
    if len(KH.findall(p)) >= 14: return p
    if p.startswith("គេឱ្យ $S"): return p.replace("គេឱ្យ $S", "គេឱ្យផលបូក $S", 1)
    if p.startswith("គេឱ្យ $"): return p.replace("គេឱ្យ $", "គេឱ្យចំនួនកុំផ្លិច $", 1)
    if p.startswith("សរសេរ $") and "ទម្រង់ពីជគណិត" not in p: return p
    if p.startswith("រកម៉ូឌុលនៃ $"): return p.replace("រកម៉ូឌុលនៃ $", "រកម៉ូឌុលនៃចំនួនកុំផ្លិច $", 1)
    if p.startswith("រកឫសការេនៃ $"): return p.replace("រកឫសការេនៃ $", "រកឫសការេនៃចំនួនកុំផ្លិច $", 1)
    m_ = re.match(r"^(គណនា|សរសេរ|រកផ្នែក|រកម៉ូឌុល)(ផលចែក|ផលគុណ|ផលបូក)? ", p)
    if m_ is None: return p
    rest = p[m_.end():]
    if m_.group(1) == "គណនា":
        w = m_.group(2)
        lead = {"ផលចែក": K("គណនាផលចែកខាងក្រោម ៖ ", "គណនាផលចែកនៃចំនួនកុំផ្លិច ៖ "), "ផលគុណ": K("គណនាផលគុណខាងក្រោម ៖ ", "គណនាផលគុណនៃចំនួនកុំផ្លិច ៖ "), "ផលបូក": "គណនាផលបូកខាងក្រោម ៖ "}.get(w) or K("គណនាតម្លៃនៃកន្សោម ", "គណនាកន្សោមខាងក្រោម ៖ ", "គណនាតម្លៃនៃកន្សោមខាងក្រោម ៖ ")
        return lead + rest
    return p

def R(sub, diff, prob, sol, ans, checks, k=None, diagrams=None, row_id=None):
    if k is not None:
        kk = (sub, k)
        if kk in SEEN: return False
        SEEN.add(kk)
    if isinstance(sol, (list, tuple)): sol = "\n".join(sol)
    prob = lengthen(prob)
    ROWS.append(make_row(TOPIC, sub, diff, prob, sol, ans, [check(*c) for c in checks], "complex_algebra",
                         diagrams=diagrams, chapter="complex", grade=11, row_id=row_id))
    return True

def fill(fn, n):
    start = len(ROWS); t = 0
    while len(ROWS) - start < n and t < n * 60:
        t += 1
        fn()
    print(f"{fn.__name__}: {len(ROWS)-start}")

GIVE = ["គេមានចំនួនកុំផ្លិច", "គេឱ្យចំនួនកុំផ្លិច", "គេមានចំនួនកុំផ្លិច", "គេឱ្យចំនួនកុំផ្លិច"]
HAVE = ["យើងបាន", "គេបាន", "យើងមាន", "គេមាន"]
GET = ["យើងបាន", "គេបាន"]
ALGF = ["ជាទម្រង់ពីជគណិត", "ជាទម្រង់ពីជគណិត $a+bi$", "ជាទម្រង់ $a+bi$ ដែល $a,b\\in\\mathbb{R}$"]
I2 = ["ដោយ $i^2=-1$", "ដោយដឹងថា $i^2=-1$", "ព្រោះ $i^2=-1$", "តាម $i^2=-1$"]
def dd(s): return "$$" + s + "$$"
def ll(s): return "$" + s + "$"

# ---------- A. real part, imaginary part, operations ----------
def g_re_im():
    t = K("prod", "sq", "lin", "iz", "frac")
    u, v = G(-5, 5), G(-5, 5)
    pr = K("រកផ្នែកពិត និងផ្នែកនិមិត្តនៃចំនួនកុំផ្លិច {E} ។",
           "គេឱ្យ {E} ។ សរសេរ $z$ ជាទម្រង់ពីជគណិត រួចបញ្ជាក់ផ្នែកពិត និងផ្នែកនិមិត្តរបស់វា ។",
           "កំណត់ផ្នែកពិត និងផ្នែកនិមិត្តនៃ {E} ។",
           "គេមានចំនួនកុំផ្លិច {E} ។ តើផ្នែកពិត និងផ្នែកនិមិត្តនៃ $z$ ស្មើនឹងប៉ុន្មាន ?")
    if t == "prod":
        E = f"z={u.p()}{v.p()}"; r = u * v
        steps = [dd("z=" + chain(*mul_chain(u, v)))]; py = f"{u.py()}*{v.py()}"
        intro = K("ពន្លាតផលគុណ", "យើងគុណតួនីមួយៗ", "សរសេរ $z$ ជាទម្រង់ពីជគណិតដោយពន្លាតផលគុណ") + " ដោយប្រើ $i^2=-1$ ៖"
        k = (t, key(u), key(v))
    elif t == "sq":
        E = f"z={u.p()}^{{2}}"; r = u ** 2
        a, b = u.a, u.b
        steps = [dd("z=" + chain(tsum([(a*a, "")]) + ("+" if a*b > 0 else "-") + nt(abs(2*a*b)) + "i+" + nt(b*b) + "i^{2}", tsum([(a*a, ""), (2*a*b, "i"), (-b*b, "")]), r.tex()))]
        py = f"{u.py()}**2"
        intro = K("តាមរូបមន្ត $(a+b)^2=a^2+2ab+b^2$ យើងបាន ៖", "ពន្លាតការេ ហើយជំនួស $i^2=-1$ ៖"); k = (t, key(u))
    elif t == "lin":
        p, q = rng.choice([2, 3, 4, 5]), rng.choice([-3, -2, 2, 3])
        E = f"z={p}{u.p()}{'+' if q > 0 else '-'}{mm(abs(q),v.p())}"; r = p * u + q * v
        steps = [dd("z=" + chain(f"{(p*u).tex()}{'+' if q > 0 else '-'}" + (f"({abs(q)*v})" if True else ""), r.tex()))]
        py = f"{p}*{u.py()}+({q})*{v.py()}"; intro = K("គុណចូលក្នុងវង់ក្រចក រួចបូកតួដូចគ្នា ៖", "យើងបូកផ្នែកពិតជាមួយផ្នែកពិត និងផ្នែកនិមិត្តជាមួយផ្នែកនិមិត្ត ៖")
        k = (t, p, q, key(u), key(v))
    elif t == "iz":
        q = rng.choice([2, 3, -2, -3, 4]); 
        E = f"z={q}i{u.p()}+{v.p()}" if True else ""; r = q * I_ * u + v
        qi = q * I_
        steps = [dd("z=" + chain(tsum([(q*u.a, "i"), (q*u.b, "i^{2}")]) + ("+" if not v.tex().startswith("-") else "") + v.tex(), tsum([(q*u.a, "i"), (-q*u.b, "")]) + ("+" if not v.tex().startswith("-") else "") + v.tex(), r.tex()))]
        py = f"{qi.py()}*{u.py()}+{v.py()}"; intro = K(*I2) + " យើងបាន ៖"; k = (t, q, key(u), key(v))
    else:
        d = K(Z(1, 1), Z(1, -1), Z(2, 1), Z(1, 2), Z(2, -1), Z(3, 1), Z(1, 3), Z(3, -1))
        w = G(-4, 4); n = w * d
        E = rf"z=\frac{{{n.tex()}}}{{{d.tex()}}}"; r = w
        steps = [dd("z=" + chain(*div_chain(n, d)))]; py = f"{n.py()}/{d.py()}"
        intro = K("គុណភាគយក និងភាគបែងនឹងចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែង ៖", f"ចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែងគឺ ${d.c().tex()}$ ។ គុណភាគយក និងភាគបែងនឹងវា ៖"); k = (t, key(n), key(d))
    conc = K(f"ដូចនេះ ផ្នែកពិតនៃ $z$ គឺ $\\boxed{{{nt(r.a)}}}$ និងផ្នែកនិមិត្តគឺ $\\boxed{{{nt(r.b)}}}$ ។",
             f"ដូចនេះ $z={r.tex()}$ មានផ្នែកពិត $\\boxed{{{nt(r.a)}}}$ និងផ្នែកនិមិត្ត $\\boxed{{{nt(r.b)}}}$ ។")
    R("real_imag_parts", "easy", pr.replace("{E}", ll(E)), [intro] + steps + [conc], f"a={nt(r.a)},\\ b={nt(r.b)}",
      [(f"re(expand({py}))", str(r.a), "real part"), (f"im(expand({py}))", str(r.b), "imaginary part")], k)

def g_param_real():
    t = K("quad", "prod", "quot")
    if t == "quad":
        al, be = rng.sample(range(-5, 6), 2); ga, de = rng.sample(range(-5, 6), 2)
        if {al, be} & {ga, de} and len({al, be} & {ga, de}) == 2: return
        A = [1, -(al + be), al * be]; B = [1, -(ga + de), ga * de]
        tA, tB = ptex(A, "m"), ptex(B, "m")
        zt = f"z=({tA})+({tB})i"
        ask = K("real", "imag", "both")
        fa = rf"(m{tsum([(-al,'')]) if al>0 else '+'+nt(-al)})(m{tsum([(-be,'')]) if be>0 else '+'+nt(-be)})" if al and be else None
        def roots(a_, b_): return sorted({a_, b_})
        rr, ri = roots(ga, de), roots(al, be)
        fm = lambda v_: "m=" + nt(v_)
        lines = []
        pre = K("គេមានចំនួនកុំផ្លិច", "គេឱ្យចំនួនកុំផ្លិច") + f" ${zt}$ ដែល $m$ ជាចំនួនពិត ។"
        cks = []
        real_txt = " ឬ ".join(ll(fm(v_)) for v_ in rr); im_txt = " ឬ ".join(ll(fm(v_)) for v_ in ri)
        if ask in ("real", "both"):
            lines += [f"$z$ ជាចំនួនពិត លុះត្រាតែផ្នែកនិមិត្តរបស់វាស្មើសូន្យ ៖", dd(f"{tB}=0"), K("ដោះស្រាយសមីការនេះ យើងបាន ", "សមីការដឺក្រេទីពីរនេះមានឫស ") + real_txt + " ។"]
            cks += [(f"({v_})**2+({B[1]})*({v_})+({B[2]})", "0", "imag part vanishes") for v_ in rr]
        if ask in ("imag", "both"):
            lines += [f"$z$ ជាចំនួននិមិត្ត លុះត្រាតែផ្នែកពិតស្មើសូន្យ ៖", dd(f"{tA}=0"), K("នាំឱ្យ ", "គេបាន ") + im_txt + " ។"]
            cks += [(f"({v_})**2+({A[1]})*({v_})+({A[2]})", "0", "real part vanishes") for v_ in ri]
            # the imaginary case must keep a nonzero imaginary part
            bad = [v_ for v_ in ri if v_ in rr]
            if bad: return
            lines.append(f"ចំពោះតម្លៃទាំងនេះ ផ្នែកនិមិត្តខុសពីសូន្យ ព្រោះ ${', '.join(f'{v_}^{{2}}' if v_>=0 else f'(-{-v_})^{{2}}' for v_ in [])}$".replace(" $$", "") if False else "ចំពោះតម្លៃទាំងនេះ ផ្នែកនិមិត្តខុសពីសូន្យ ដូច្នេះ $z$ ជាចំនួននិមិត្តពិតមែន ។")
        q = {"real": "រកតម្លៃ $m$ ដើម្បីឱ្យ $z$ ជាចំនួនពិត ។", "imag": "រកតម្លៃ $m$ ដើម្បីឱ្យ $z$ ជាចំនួននិមិត្ត (ផ្នែកពិតស្មើសូន្យ) ។",
             "both": "រកតម្លៃ $m$ ដើម្បីឱ្យ $z$ ជាចំនួនពិត រួចរកតម្លៃ $m$ ដើម្បីឱ្យ $z$ ជាចំនួននិមិត្ត ។"}[ask]
        if ask == "real": c = "ដូចនេះ $z$ ជាចំនួនពិតកាលណា " + real_txt.replace("$m=", "$\\boxed{m=").replace("$ ឬ", "}$ ឬ")[:-1] + "}$ ។"; ans = ",\\ ".join(fm(v_) for v_ in rr)
        elif ask == "imag": c = "ដូចនេះ $z$ ជាចំនួននិមិត្តកាលណា " + im_txt + " ។"; ans = ",\\ ".join(fm(v_) for v_ in ri)
        else: c = f"ដូចនេះ $z$ ជាចំនួនពិតកាលណា {real_txt} ហើយជាចំនួននិមិត្តកាលណា {im_txt} ។"; ans = "\\text{real: }" + ",\\ ".join(fm(v_) for v_ in rr) + r";\ \text{imag: }" + ",\\ ".join(fm(v_) for v_ in ri)
        if ask == "both": ans = ",\\ ".join(fm(v_) for v_ in rr) + r"\ ;\ " + ",\\ ".join(fm(v_) for v_ in ri)
        R("parameter_real_or_imaginary", "medium", pre + " " + q, lines + [c], ans, cks, (t, ask, al, be, ga, de))
    elif t == "prod":
        u = G(-4, 4)  # z=(m+pi)*u
        p = rng.choice([-3, -2, -1, 1, 2, 3, 4])
        a, b = u.a, u.b
        # z = (m a - p b) + (m b + p a) i
        want = K("real", "imag")
        m0 = Q(-p * a, b) if want == "real" else Q(p * b, a)
        if m0.q > 3: return
        mi = Z(0, p)
        E = rf"z=(m{'+' if p>0 else '-'}{'' if abs(p)==1 else abs(p)}i){u.p()}"
        re_t = tsum([(a, "m"), (-p * b, "")]); im_t = tsum([(b, "m"), (p * a, "")])
        l = [K("ពន្លាតផលគុណ ៖", "យើងសរសេរ $z$ ជាទម្រង់ពីជគណិត ៖"),
             dd(f"z=({re_t})+({im_t})i")]
        if want == "real":
            l += [f"$z$ ជាចំនួនពិត លុះត្រាតែផ្នែកនិមិត្តស្មើសូន្យ ៖", dd(rf"{im_t}=0\Leftrightarrow m={nt(m0)}")]
            val = Z(m0, p) * u; cks = [(f"im(expand((({m0})+({p})*I)*{u.py()}))", "0", "imag part zero"), (f"expand((({m0})+({p})*I)*{u.py()})", str(val.a), "value")]
            c = f"ដូចនេះ $\\boxed{{m={nt(m0)}}}$ ហើយពេលនោះ $z={val.tex()}$ ។"
            q = K("រកចំនួនពិត $m$ ដើម្បីឱ្យ $z$ ជាចំនួនពិត រួចគណនា $z$ ។", "កំណត់តម្លៃនៃចំនួនពិត $m$ ដែលធ្វើឱ្យ $z$ ជាចំនួនពិត ហើយគណនាតម្លៃនៃ $z$ ពេលនោះ ។")
        else:
            l += [f"$z$ ជាចំនួននិមិត្ត លុះត្រាតែផ្នែកពិតស្មើសូន្យ ៖", dd(rf"{re_t}=0\Leftrightarrow m={nt(m0)}")]
            val = Z(m0, p) * u; cks = [(f"re(expand((({m0})+({p})*I)*{u.py()}))", "0", "real part zero"), (f"im(expand((({m0})+({p})*I)*{u.py()}))", str(val.b), "value")]
            if val == 0: return
            c = f"ដូចនេះ $\\boxed{{m={nt(m0)}}}$ ហើយពេលនោះ $z={val.tex()}$ ។"
            q = K("រកចំនួនពិត $m$ ដើម្បីឱ្យ $z$ ជាចំនួននិមិត្ត រួចគណនា $z$ ។", "កំណត់ $m\\in\\mathbb{R}$ ដើម្បីឱ្យផ្នែកពិតនៃ $z$ ស្មើសូន្យ ហើយគណនា $z$ ពេលនោះ ។")
        R("parameter_real_or_imaginary", "medium", f"{K(*GIVE)} ${E}$ ដែល $m$ ជាចំនួនពិត ។ {q}", l + [c], f"m={nt(m0)}", cks, (t, want, p, key(u)))
    else:
        d = K(Z(1, 1), Z(1, -1), Z(2, 1), Z(1, 2), Z(2, -1), Z(1, -2), Z(3, 1), Z(1, 3))
        p = rng.choice([-3, -2, -1, 1, 2, 3])
        # z=(m+pi)/d ; numerator (m+pi)*conj(d)
        a, b = d.a, -d.b; n = d.n2()
        want = K("real", "imag")
        m0 = Q(-p * a, b) if want == "real" else Q(p * b, a)
        val = Z(m0, p) / d
        if m0.q > 2 or val == 0: return
        E = rf"z=\frac{{m{'+' if p>0 else '-'}{'' if abs(p)==1 else abs(p)}i}}{{{d.tex()}}}"
        re_t = tsum([(a, "m"), (-p * b, "")]); im_t = tsum([(b, "m"), (p * a, "")])
        l = [f"គុណភាគយក និងភាគបែងនឹង ${d.c().tex()}$ ៖",
             dd(rf"z=\frac{{(m{'+' if p>0 else '-'}{'' if abs(p)==1 else abs(p)}i){d.c().p()}}}{{{nt(n)}}}=\frac{{{re_t}}}{{{nt(n)}}}+\frac{{{im_t}}}{{{nt(n)}}}i")]
        word = "ពិត" if want == "real" else "និមិត្ត"
        tt = im_t if want == "real" else re_t
        other = "ផ្នែកនិមិត្ត" if want == "real" else "ផ្នែកពិត"
        l += [f"$z$ ជាចំនួន{word} លុះត្រាតែ{other}ស្មើសូន្យ គឺ ៖", dd(rf"{tt}=0\Leftrightarrow m={nt(m0)}")]
        fnc = "im" if want == "real" else "re"
        cks = [(f"{fnc}(expand((({m0})+({p})*I)*{d.c().py()}))", "0", "vanishing part"), (f"(({m0})+({p})*I)/{d.py()}", val.py(), "value")]
        R("parameter_real_or_imaginary", "hard", f"គេឱ្យ ${E}$ ដែល $m\\in\\mathbb{{R}}$ ។ រកតម្លៃ $m$ ដើម្បីឱ្យ $z$ ជាចំនួន{word} ។ រួចគណនា $z$ ចំពោះតម្លៃនោះ ។",
          l + [f"ជំនួសចូលវិញ $z={val.tex()}$ ។", f"ដូចនេះ $\\boxed{{m={nt(m0)}}}$ ។"], f"m={nt(m0)}", cks, (t, want, p, key(d)))

def g_lincomb():
    u, v = G(-7, 7), G(-7, 7)
    p, q = K(1, 2, 3, 4, 5), K(-1, -2, -3, 1, 2, 3)
    w = K(None, None, G(-4, 4))
    e = (f"{'' if p==1 else p}z_1{'+' if q>0 else '-'}{'' if abs(q)==1 else abs(q)}z_2")
    r = p * u + q * v
    pr = K(f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ គណនា ${e}$ ។",
           f"ឱ្យ $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ សរសេរ ${e}$ ជាទម្រង់ពីជគណិត ។",
           f"គណនា ${e}$ ដោយដឹងថា $z_1={u.tex()}$ ហើយ $z_2={v.tex()}$ ។")
    a = p * u; b = q * v
    body = K(1, 2)
    if body == 1:
        l = [f"ជំនួស $z_1$ និង $z_2$ {K('យើងបាន', 'គេបាន')} ៖",
             dd(chain(e, f"{'' if p==1 else p}{u.p() if p!=1 else '('+u.tex()+')'}{'+' if q>0 else '-'}{'' if abs(q)==1 else abs(q)}({v.tex()})",
                      a.tex() + (("+" if not b.tex().startswith("-") else "") + b.tex()) if b.tex()[0] != "-" else a.tex() + b.tex(), r.tex()))]
    else:
        l = [f"យើងគណនាផ្នែកពិត និងផ្នែកនិមិត្តដោយឡែកពីគ្នា ៖",
             f"ផ្នែកពិត ៖ ${nt(p)}\\times({nt(u.a)})+({nt(q)})\\times({nt(v.a)})={nt(r.a)}$",
             f"ផ្នែកនិមិត្ត ៖ ${nt(p)}\\times({nt(u.b)})+({nt(q)})\\times({nt(v.b)})={nt(r.b)}$"]
    R("sum_and_difference", "easy", pr, l + [f"ដូចនេះ $\\boxed{{{e}={r.tex()}}}$ ។"], f"{e}={r.tex()}",
      [(f"{p}*{u.py()}+({q})*{v.py()}", r.py(), "linear combination")], (p, q, key(u), key(v)))

def g_product():
    t = K("two", "two", "three", "conjpair", "surd")
    if t == "two":
        u, v = G(-6, 6), G(-6, 6); r = u * v
        pr = K(f"គណនាផលគុណ ${u.p()}{v.p()}$ ។", f"សរសេរ ${u.p()}{v.p()}$ {K(*ALGF)} ។",
               f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ គណនា $z_1\\times z_2$ ។")
        l = [K("យើងគុណតួនីមួយៗនៃវង់ក្រចកទីមួយនឹងវង់ក្រចកទីពីរ ៖", "ពន្លាតផលគុណ ៖", K(*I2) + " យើងបាន ៖"), dd(chain(f"{u.p()}{v.p()}", *mul_chain(u, v)))]
        R("product", "easy", pr, l + [f"ដូចនេះ ផលគុណស្មើនឹង $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"{u.py()}*{v.py()}", r.py(), "product")], (t, key(u), key(v)))
    elif t == "three":
        u, v, w = G(-3, 3), G(-3, 3), G(-3, 3); r1 = u * v; r = r1 * w
        pr = K(f"គណនា ${u.p()}{v.p()}{w.p()}$ ។", f"សរសេរ $z={u.p()}{v.p()}{w.p()}$ {K(*ALGF)} ។")
        l = [f"គុណកត្តាពីរដំបូងជាមុនសិន ៖", dd(chain(f"{u.p()}{v.p()}", *mul_chain(u, v))), "រួចគុណលទ្ធផលនឹងកត្តាទីបី ៖", dd(chain(f"{r1.p()}{w.p()}", *mul_chain(r1, w)))]
        R("product", "medium", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"{u.py()}*{v.py()}*{w.py()}", r.py(), "triple product")], (t, key(u), key(v), key(w)))
    elif t == "conjpair":
        u = G(-9, 9); r = u * u.c()
        pr = K(f"គណនា ${u.p()}{u.c().p()}$ ដោយមិនពន្លាតតួម្តងមួយៗ ។", f"គណនាផលគុណនៃ $z={u.tex()}$ និងចំនួនកុំផ្លិចឆ្លាស់របស់វា ។", f"បង្ហាញថា ${u.p()}{u.c().p()}$ ជាចំនួនពិត រួចគណនាតម្លៃរបស់វា ។")
        l = [K("ផលគុណនេះមានរាង $(a+bi)(a-bi)=a^2+b^2$ ។", "ដោយ $(a+bi)(a-bi)=a^2-(bi)^2=a^2+b^2$ ។"),
             f"ដោយ $a={nt(abs(u.a))}$ និង $b={nt(abs(u.b))}$ យើងបាន ៖", dd(f"{u.p()}{u.c().p()}={nt(abs(u.a))}^{{2}}+{nt(abs(u.b))}^{{2}}={nt(u.a**2)}+{nt(u.b**2)}={nt(r.a)}")]
        R("product", "easy", pr, l + [f"ដូចនេះ ផលគុណជាចំនួនពិតស្មើនឹង $\\boxed{{{nt(r.a)}}}$ ។"], nt(r.a), [(f"{u.py()}*conjugate({u.py()})", str(r.a), "z times conjugate")], (t, str(abs(u.a)), str(abs(u.b)), key(u)))
    else:
        k = K(2, 3, 5); a, b, c, d = rng.randint(1, 4), rng.randint(1, 3), rng.randint(1, 4), rng.randint(1, 3)
        s1, s2 = K(1, -1), K(1, -1)
        u = Z(a, s1 * b * RT(k)); v = Z(c, s2 * d * RT(k)); r = u * v
        pr = K(f"គណនា $({u.tex()})({v.tex()})$ ។", f"{K(*GIVE)} $A={u.tex()}$ និង $B={v.tex()}$ ។ គណនា $A\\times B$ ។")
        t1 = nt(a * c); t2 = f"{nt(a*s2*d)}i\\sqrt{{{k}}}"; t3 = f"{nt(s1*b*c)}i\\sqrt{{{k}}}"; t3 = ("+" if s1 * b * c > 0 else "") + t3; t2 = ("+" if s2 > 0 else "") + t2
        l = [f"ពន្លាត ហើយកត់សម្គាល់ថា $\\left(i\\sqrt{{{k}}}\\right)^{{2}}=-{k}$ ៖",
             dd(f"({u.tex()})({v.tex()})={t1}{t2}{t3}{tsum([(s1*s2*b*d,'')]) if s1*s2<0 else '+'+nt(b*d)}\\left(i\\sqrt{{{k}}}\\right)^{{2}}={r.tex()}")]
        R("product", "medium", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"{u.py()}*{v.py()}", r.py(), "product with surd")], (t, k, a, b, c, d, s1, s2))

def g_binom_power():
    t = K(2, 3, 3, 4)
    u = G(-4, 4) if t < 4 else G(-3, 3)
    a, b = u.a, u.b
    if t == 2:
        r = u ** 2
        pr = K(f"គណនា ${u.p()}^{{2}}$ ។", f"សរសេរ $z={u.p()}^{{2}}$ {K(*ALGF)} ។")
        l = [dd(chain(f"{u.p()}^{{2}}", tsum([(a*a, ""), (2*a*b, "i"), (b*b, "i^{2}")]), tsum([(a*a - b*b, ""), (2*a*b, "i")])))]
        R("binomial_power", "easy", pr, ["តាមរូបមន្តការេនៃទ្វេធា ៖"] + l + [f"ដូចនេះ $\\boxed{{{u.p()}^{{2}}={r.tex()}}}$ ។"], r.tex(), [(f"expand({u.py()}**2)", r.py(), "square")], (t, key(u)))
    elif t == 3:
        if abs(a) > 3 or abs(b) > 3: return
        r = u ** 3; s = u ** 2
        way = K(1, 2)
        pr = K(f"គណនា ${u.p()}^{{3}}$ ។", f"សរសេរ ${u.p()}^{{3}}$ ជាទម្រង់ពីជគណិត ។", f"គេឱ្យ $z={u.tex()}$ ។ គណនា $z^2$ រួចទាញរក $z^3$ ។")
        if way == 1 or "z^2" in pr:
            l = ["យើងគណនាការេជាមុនសិន ៖", dd(f"{u.p()}^{{2}}=" + chain(tsum([(a*a, ""), (2*a*b, "i"), (b*b, "i^{2}")]), s.tex())),
                 "គុណនឹងកត្តាដើមម្តងទៀត ៖", dd(chain(f"{u.p()}^{{3}}", f"{s.p()}{u.p()}", *mul_chain(s, u)))]
        else:
            l = ["តាមរូបមន្ត $(a+b)^3=a^3+3a^2b+3ab^2+b^3$ ដោយ $i^2=-1$ និង $i^3=-i$ យើងបាន ៖",
                 dd(chain(f"{u.p()}^{{3}}", tsum([(a**3, ""), (3*a*a*b, "i"), (3*a*b*b, "i^{2}"), (b**3, "i^{3}")]), tsum([(a**3, ""), (3*a*a*b, "i"), (-3*a*b*b, ""), (-b**3, "i")]), r.tex()))]
        R("binomial_power", "medium", pr, l + [f"ដូចនេះ $\\boxed{{{u.p()}^{{3}}={r.tex()}}}$ ។"], r.tex(), [(f"expand({u.py()}**3)", r.py(), "cube"), (f"expand({u.py()}**2)", s.py(), "square")], (t, key(u)))
    else:
        r = u ** 4; s = u ** 2
        pr = K(f"គណនា ${u.p()}^{{4}}$ ដោយគណនា ${u.p()}^{{2}}$ ជាមុន ។", f"សរសេរ $Z={u.p()}^{{4}}$ ជាទម្រង់ពីជគណិត ។")
        l = ["យើងគណនាការេមុន ៖", dd(f"{u.p()}^{{2}}=" + chain(tsum([(a*a, ""), (2*a*b, "i"), (b*b, "i^{2}")]), s.tex())),
             "ស្វ័យគុណទី $4$ គឺជាការេនៃលទ្ធផលនេះ ៖", dd(chain(f"{u.p()}^{{4}}", r"\left[" + f"{u.p()}^{{2}}" + r"\right]^{2}", f"{s.p()}^{{2}}", tsum([(s.a**2, ""), (2*s.a*s.b, "i"), (s.b**2, "i^{2}")]), r.tex()))]
        R("binomial_power", "medium", pr, l + [f"ដូចនេះ $\\boxed{{{u.p()}^{{4}}={r.tex()}}}$ ។"], r.tex(), [(f"expand({u.py()}**4)", r.py(), "fourth power")], (t, key(u)))

# ---------- B. powers of i ----------
IV = {0: "1", 1: "i", 2: "-1", 3: "-i"}
def ipow(n): return [Z(1), Z(0, 1), Z(-1), Z(0, -1)][n % 4]
def g_ipow():
    t = K("single", "sum3", "cycle_sum", "prod", "neg", "general", "mix")
    if t == "single":
        ns = rng.sample(range(5, 2100), 4); 
        ns = [rng.randint(5, 99), rng.randint(100, 999), rng.randint(1000, 2600)]
        pr = K(f"គណនា $i^{{{ns[0]}}}$ , $i^{{{ns[1]}}}$ និង $i^{{{ns[2]}}}$ ។", f"សរសេរជាទម្រង់សាមញ្ញ $i^{{{ns[0]}}}$ , $i^{{{ns[1]}}}$ និង $i^{{{ns[2]}}}$ ។")
        l = [K("យើងដឹងថា $i^4=1$ ដូច្នេះចែកនិទស្សន្តនឹង $4$ ហើយយកសំណល់ ។", "ដោយ $i^4=1$ ស្វ័យគុណនៃ $i$ វិលជុំតាមខួប $4$ ។", "ស្វ័យគុណនៃ $i$ មានតម្លៃដដែលៗគឺ $i,-1,-i,1$ ។")]
        for n in ns:
            q, r = divmod(n, 4)
            l.append(dd(f"i^{{{n}}}=i^{{4\\times{q}+{r}}}=\\left(i^{{4}}\\right)^{{{q}}}\\times i^{{{r}}}=i^{{{r}}}={IV[r]}"))
        ans = ",\\ ".join(IV[n % 4] for n in ns)
        R("powers_of_i", "easy", pr, l + [f"ដូចនេះ $\\boxed{{i^{{{ns[0]}}}={IV[ns[0]%4]}}}$ , $\\boxed{{i^{{{ns[1]}}}={IV[ns[1]%4]}}}$ និង $\\boxed{{i^{{{ns[2]}}}={IV[ns[2]%4]}}}$ ។"], ans,
          [(f"I**{n}", IV[n % 4].replace("i", "I"), "power of i") for n in ns], (t, tuple(ns)))
    elif t == "sum3":
        ns = [rng.randint(6, 400) for _ in range(3)]; cs = [K(1, 2, 3, -1, -2), K(1, 2, -1, -3), K(1, 2, -2, 4)]
        e = tsum([(cs[0], f"i^{{{ns[0]}}}"), (cs[1], f"i^{{{ns[1]}}}"), (cs[2], f"i^{{{ns[2]}}}")])
        r = sum((c * ipow(n) for c, n in zip(cs, ns)), Z(0))
        pr = K(f"គណនា $A={e}$ ។", f"សម្រួលកន្សោម $A={e}$ ។", f"សរសេរ $A={e}$ ជាទម្រង់ពីជគណិត ។")
        l = ["ចែកនិទស្សន្តនីមួយៗនឹង $4$ ៖"] + [f"${n}=4\\times{n//4}+{n%4}$ នាំឱ្យ $i^{{{n}}}={IV[n%4]}$" for n in ns]
        l += [K("ជំនួសចូលកន្សោម ៖", "យើងបាន ៖"), dd("A=" + chain("".join(("+" if c > 0 and j else ("-" if c < 0 else "")) + (nt(abs(c)) if abs(c) != 1 else "") + (f"({IV[n%4]})" if abs(c) != 1 or IV[n%4][0] == "-" else IV[n%4]) for j, (c, n) in enumerate(zip(cs, ns))), r.tex()))]
        R("powers_of_i", "medium", pr, l + [f"ដូចនេះ $\\boxed{{A={r.tex()}}}$ ។"], f"A={r.tex()}", [("+".join(f"({c})*I**{n}" for c, n in zip(cs, ns)), r.py(), "sum of powers")], (t, tuple(ns), tuple(cs)))
    elif t == "cycle_sum":
        n = rng.randint(7, 2100); st = K(0, 1)
        r = sum((ipow(j) for j in range(n % 4 + 1)), Z(0)) if st == 0 else sum((ipow(j) for j in range(1, n % 4 + 1)), Z(0))
        first = "1+i+i^{2}" if st == 0 else "i+i^{2}+i^{3}"
        pr = K(f"គណនាផលបូក $S={first}+\\cdots+i^{{{n}}}$ ។", f"គេឱ្យ $S={first}+\\cdots+i^{{{n}}}$ ។ គណនា $S$ ។")
        if st == 0:
            full = n // 4 * 4; 
            l = ["តួបួនជាប់គ្នាណាក៏ដោយ មានផលបូកស្មើសូន្យ ព្រោះ $1+i+i^2+i^3=1+i-1-i=0$ ។",
                 f"ផលបូកនេះមានតួចំនួន ${n+1}$ ។ ដោយ ${n+1}=4\\times{(n+1)//4}+{(n+1)%4}$ ក្រុមបួនតួទាំង ${(n+1)//4}$ មានផលបូកសូន្យ ហើយនៅសល់ ${(n+1)%4}$ តួចុងក្រោយ ។"]
            rem = (n + 1) % 4
            tail = [full + j for j in range(rem)] if (n + 1) % 4 else []
            val = sum((ipow(j) for j in tail), Z(0))
            if rem == 0: l.append("គ្មានតួនៅសល់ទេ ។")
            else: l.append(dd("S=" + chain("+".join(f"i^{{{j}}}" for j in tail), "+".join(IV[j % 4] for j in tail).replace("+-", "-"), val.tex())))
        else:
            l = ["ស្វ័យគុណបួនតួជាប់គ្នាមានផលបូកសូន្យ ព្រោះ $i+i^2+i^3+i^4=i-1-i+1=0$ ។",
                 f"ផលបូកនេះមានតួចំនួន ${n}$ ។ ដោយ ${n}=4\\times{n//4}+{n%4}$ ក្រុមបួនតួទាំង ${n//4}$ មានផលបូកសូន្យ ហើយនៅសល់ ${n%4}$ តួចុងក្រោយ ។"]
            rem = n % 4; tail = [n - rem + 1 + j for j in range(rem)]
            val = sum((ipow(j) for j in tail), Z(0))
            if rem == 0: l.append("គ្មានតួនៅសល់ទេ ។")
            else: l.append(dd("S=" + chain("+".join(f"i^{{{j}}}" for j in tail), "+".join(IV[j % 4] for j in tail).replace("+-", "-"), val.tex())))
        lhs = "+".join(f"I**{j}" for j in range(st, st + 0)) 
        R("powers_of_i", "medium", pr, l + [f"ដូចនេះ $\\boxed{{S={val.tex()}}}$ ។"], f"S={val.tex()}",
          [(f"(1-I**{n+1})/(1-I)" if st == 0 else f"I*(1-I**{n})/(1-I)", val.py(), "geometric sum")], (t, n, st))
    elif t == "prod":
        n = rng.randint(4, 40); e = n * (n + 1) // 2; v = IV[e % 4]
        pr = K(f"គណនាផលគុណ $P=i\\times i^{{2}}\\times i^{{3}}\\times\\cdots\\times i^{{{n}}}$ ។", f"គេឱ្យ $P=i\\times i^{{2}}\\times\\cdots\\times i^{{{n}}}$ ។ សរសេរ $P$ ជាទម្រង់សាមញ្ញ ។")
        l = ["ផលគុណនៃស្វ័យគុណមានគោលដូចគ្នា ស្មើនឹងគោលនោះដែលមាននិទស្សន្តជាផលបូកនៃនិទស្សន្ត ៖",
             dd(f"P=i^{{1+2+\\cdots+{n}}}=i^{{\\frac{{{n}\\times{n+1}}}{{2}}}}=i^{{{e}}}"), f"ដោយ ${e}=4\\times{e//4}+{e%4}$ យើងបាន $i^{{{e}}}={IV[e%4]}$ ។"]
        R("powers_of_i", "medium", pr, l + [f"ដូចនេះ $\\boxed{{P={v}}}$ ។"], f"P={v}", [(f"I**({n}*{n+1}/2)", v.replace("i", "I"), "product exponent")], (t, n))
    elif t == "neg":
        n = rng.randint(3, 300); r = Z(1) / ipow(n)
        c = K(1, 2, 3); e = rng.randint(5, 90); s = ipow(e) * c + r
        pr = f"គណនា $A={'' if c==1 else c}i^{{{e}}}+\\frac{{1}}{{i^{{{n}}}}}$ ។"
        l = [f"ចែកនិទស្សន្តនឹង $4$ ៖ $i^{{{e}}}={IV[e%4]}$ និង $i^{{{n}}}={IV[n%4]}$ ។",
             dd(chain(rf"\frac{{1}}{{i^{{{n}}}}}", rf"\frac{{1}}{{{IV[n%4]}}}", r.tex())) if n % 4 else f"ដោយ $i^{{{n}}}=1$ នោះ $\\frac{{1}}{{i^{{{n}}}}}=1$ ។"]
        if n % 4 in (1, 3): l.append(f"(យើងប្រើ $\\frac{{1}}{{i}}=\\frac{{i}}{{i^2}}=-i$ ។)")
        l.append(dd("A=" + s.tex()))
        R("powers_of_i", "easy", pr, l + [f"ដូចនេះ $\\boxed{{A={s.tex()}}}$ ។"], f"A={s.tex()}", [(f"{c}*I**{e}+1/I**{n}", s.py(), "expression")], (t, n, e, c))
    elif t == "general":
        r0 = K(0, 1, 2, 3); s0 = K(0, 1, 2, 3); 
        if r0 == s0: return
        v = ipow(r0) + ipow(s0)
        A, B = f"4n+{r0}" if r0 else "4n", f"4n+{s0}" if s0 else "4n"
        pr = K(f"បង្ហាញថា ចំពោះគ្រប់ចំនួនគត់ធម្មជាតិ $n$ គេបាន $i^{{{A}}}+i^{{{B}}}={v.tex()}$ ។", f"ស្រាយបញ្ជាក់ថា $i^{{{A}}}+i^{{{B}}}={v.tex()}$ ចំពោះគ្រប់ $n\\in\\mathbb{{N}}$ ។")
        l = ["យើងមាន $i^{4n}=\\left(i^{4}\\right)^{n}=1^n=1$ ។ ដូច្នេះ ៖", dd(f"i^{{{A}}}=i^{{4n}}\\times i^{{{r0}}}={IV[r0]}"), dd(f"i^{{{B}}}=i^{{4n}}\\times i^{{{s0}}}={IV[s0]}"), "បូកលទ្ធផលទាំងពីរ ៖", dd(f"i^{{{A}}}+i^{{{B}}}={v.tex()}")]
        R("powers_of_i", "medium", pr, l + [f"ដូចនេះ $\\boxed{{i^{{{A}}}+i^{{{B}}}={v.tex()}}}$ ចំពោះគ្រប់ $n$ ។"], v.tex(),
          [(f"I**(4*{n}+{r0})+I**(4*{n}+{s0})", v.py(), f"instance n={n}") for n in (1, 2, 7)], (t, r0, s0))
    else:
        u = G(-4, 4); n = rng.randint(5, 200); w = ipow(n); r = u * w
        pr = f"សរសេរ $z={u.p()}i^{{{n}}}$ ជាទម្រង់ពីជគណិត ។"
        l = [f"ដោយ ${n}=4\\times{n//4}+{n%4}$ នោះ $i^{{{n}}}={IV[n%4]}$ ។", dd("z=" + chain(f"{u.p()}\\times({IV[n%4]})" if n % 4 else u.tex(), r.tex()))]
        R("powers_of_i", "easy", pr, l + [f"ដូចនេះ $\\boxed{{z={r.tex()}}}$ ។"], f"z={r.tex()}", [(f"{u.py()}*I**{n}", r.py(), "value")], (t, key(u), n))

def g_one_plus_i_power():
    t = K("even", "ratio", "sum", "conjratio")
    if t == "even":
        s = K(1, -1); m_ = rng.randint(2, 12); n = 2 * m_; w = Z(1, s)
        sq = Z(0, 2 * s); r = sq ** m_
        pr = K(f"គណនា ${w.p()}^{{2}}$ រួចទាញរកតម្លៃនៃ ${w.p()}^{{{n}}}$ ។", f"ដោយគណនា ${w.p()}^{{2}}$ សរសេរ ${w.p()}^{{{n}}}$ ជាទម្រង់ពីជគណិត ។")
        l = [dd(f"{w.p()}^{{2}}=1{'+' if s>0 else '-'}2i+i^{{2}}={sq.tex()}"), f"ដូច្នេះ ៖",
             dd(chain(f"{w.p()}^{{{n}}}", rf"\left[{w.p()}^{{2}}\right]^{{{m_}}}", f"({sq.tex()})^{{{m_}}}", f"{'' if s>0 or m_%2==0 else '-'}2^{{{m_}}}i^{{{m_}}}"))]
        l.append(f"ដោយ $i^{{{m_}}}={IV[m_%4]}$ និង $2^{{{m_}}}={2**m_}$ យើងបាន ${w.p()}^{{{n}}}={r.tex()}$ ។")
        R("powers_of_one_plus_i", "medium", pr, l + [f"ដូចនេះ $\\boxed{{{w.p()}^{{{n}}}={r.tex()}}}$ ។"], r.tex(), [(f"expand({w.py()}**{n})", r.py(), "power"), (f"expand({w.py()}**2)", sq.py(), "square")], (t, s, n))
    elif t == "ratio":
        n = rng.randint(3, 120); s = K(1, -1)
        a, b = Z(1, s), Z(1, -s); q = a / b; r = Z(0, s) ** (n % 4)
        pr = K(f"សរសេរ $\\frac{{{a.tex()}}}{{{b.tex()}}}$ ជាទម្រង់ពីជគណិត រួចគណនា $\\left(\\frac{{{a.tex()}}}{{{b.tex()}}}\\right)^{{{n}}}$ ។", f"គេឱ្យ $w=\\frac{{{a.tex()}}}{{{b.tex()}}}$ ។ គណនា $w$ រួចទាញរក $w^{{{n}}}$ ។")
        l = [dd(chain(rf"\frac{{{a.tex()}}}{{{b.tex()}}}", rf"\frac{{{a.p()}^{{2}}}}{{{a.p()}{b.p()}}}", rf"\frac{{{(a*a).tex()}}}{{2}}", q.tex())),
             f"ដោយ ${n}=4\\times{n//4}+{n%4}$ យើងបាន ៖", dd(f"({q.tex()})^{{{n}}}={r.tex()}" if s > 0 else f"(-i)^{{{n}}}=(-1)^{{{n}}}i^{{{n}}}={r.tex()}")]
        R("powers_of_one_plus_i", "medium", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"({a.py()}/{b.py()})**{n}", r.py(), "power of ratio"), (f"{a.py()}/{b.py()}", q.py(), "ratio")], (t, n, s))
    elif t == "sum":
        m_ = rng.randint(1, 10); n = 2 * m_
        r = Z(1, 1) ** n + Z(1, -1) ** n
        pr = K(f"គណនា $S=(1+i)^{{{n}}}+(1-i)^{{{n}}}$ ។", f"បង្ហាញថា $(1+i)^{{{n}}}+(1-i)^{{{n}}}$ ជាចំនួនពិត រួចគណនាតម្លៃរបស់វា ។")
        l = ["ដោយ $(1+i)^2=2i$ និង $(1-i)^2=-2i$ យើងបាន ៖", dd(f"(1+i)^{{{n}}}=(2i)^{{{m_}}}={(Z(0,2)**m_).tex()}"), dd(f"(1-i)^{{{n}}}=(-2i)^{{{m_}}}={(Z(0,-2)**m_).tex()}"), dd(f"S={r.tex()}")]
        R("powers_of_one_plus_i", "hard" if n > 8 else "medium", pr, l + [f"ដូចនេះ $\\boxed{{S={r.tex()}}}$ ជាចំនួនពិត ។"], f"S={r.tex()}", [(f"expand((1+I)**{n}+(1-I)**{n})", str(r.a), "sum")], (t, n))
    else:
        u = K(Z(2, 1), Z(1, 2), Z(3, 1), Z(1, 3), Z(2, 3), Z(3, 2), Z(3, 4), Z(4, 3), Z(1, 4), Z(5, 2))
        w = (Z(0, 1) * u) * K(1, -1)
        q = w / u  # = ±i
        n = rng.randint(3, 60); r = q ** (n % 4)
        pr = f"គណនា $\\left(\\frac{{{w.tex()}}}{{{u.tex()}}}\\right)^{{{n}}}$ ។"
        l = ["យើងសម្រួលផលចែកជាមុន ៖", dd(chain(*div_chain(w, u))), f"ដោយ ${n}=4\\times{n//4}+{n%4}$ យើងបាន ៖", dd(f"({q.tex()})^{{{n}}}={r.tex()}")]
        R("powers_of_one_plus_i", "medium", pr, l + [f"ដូចនេះ លទ្ធផលស្មើនឹង $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"({w.py()}/{u.py()})**{n}", r.py(), "power")], (t, key(u), key(w), n))

# ---------- C. conjugate, modulus, quotient ----------
def g_conjugate():
    t = K("list", "expr", "prop_prod", "prop_quot", "sumdiff", "solve_bar")
    if t == "list":
        zs = [G(-9, 9), Z(0, rng.choice([-7, -5, -3, 2, 4, 6])), Z(rng.choice([-5, 3, 7, 8]), 0), Z(rng.randint(1, 5), K(1, -1) * RT(K(2, 3, 5)))]
        rng.shuffle(zs)
        pr = K("រកចំនួនកុំផ្លិចឆ្លាស់នៃចំនួនខាងក្រោម ៖ ", "សរសេរចំនួនកុំផ្លិចឆ្លាស់នៃចំនួនកុំផ្លិចនីមួយៗ ៖ ") + " , ".join(f"$z_{j+1}={z.tex()}$" for j, z in enumerate(zs)) + " ។"
        l = ["ចំនួនកុំផ្លិចឆ្លាស់នៃ $a+bi$ គឺ $a-bi$ គឺយើងប្តូរសញ្ញាផ្នែកនិមិត្តតែប៉ុណ្ណោះ ។"] + [dd(f"\\overline{{z_{j+1}}}={z.c().tex()}") for j, z in enumerate(zs)]
        fin = " , ".join(f"$\\overline{{z_{j+1}}}={z.c().tex()}$" for j, z in enumerate(zs))
        R("conjugate", "easy", pr, l + [f"ដូចនេះ {fin} ។"], ",\\ ".join(z.c().tex() for z in zs), [(f"conjugate({z.py()})", z.c().py(), "conjugate") for z in zs], (t, tuple(key(z) for z in zs)))
    elif t == "expr":
        u, v = G(-5, 5), G(-5, 5); r = u * v; c = r.c()
        way = K(1, 2)
        pr = K(f"គណនា $\\overline{{{u.p()}{v.p()}}}$ ។", f"រកចំនួនកុំផ្លិចឆ្លាស់នៃ $z={u.p()}{v.p()}$ ។")
        if way == 1:
            l = ["យើងគណនាផលគុណជាមុន ៖", dd(chain(f"{u.p()}{v.p()}", *mul_chain(u, v))), f"រួចប្តូរសញ្ញាផ្នែកនិមិត្ត ៖ ចំនួនកុំផ្លិចឆ្លាស់គឺ ${c.tex()}$ ។"]
        else:
            l = ["ដោយ $\\overline{z_1\\times z_2}=\\overline{z_1}\\times\\overline{z_2}$ យើងអាចយកចំនួនកុំផ្លិចឆ្លាស់នៃកត្តានីមួយៗមុន ៖", dd(chain(f"\\overline{{{u.p()}{v.p()}}}", f"{u.c().p()}{v.c().p()}", *mul_chain(u.c(), v.c())))]
        R("conjugate", "easy", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{c.tex()}}}$ ។"], c.tex(), [(f"conjugate(expand({u.py()}*{v.py()}))", c.py(), "conjugate of product")], (t, key(u), key(v)))
    elif t == "prop_prod":
        u, v = G(-5, 5), G(-5, 5); r = u * v
        pr = f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ ផ្ទៀងផ្ទាត់ថា $\\overline{{z_1\\times z_2}}=\\overline{{z_1}}\\times\\overline{{z_2}}$ ។"
        l = ["គណនាអង្គខាងឆ្វេង ៖", dd(f"z_1\\times z_2=" + chain(*mul_chain(u, v))), dd(f"\\overline{{z_1\\times z_2}}={r.c().tex()}\\quad(1)"),
             "គណនាអង្គខាងស្តាំ ៖", dd(f"\\overline{{z_1}}\\times\\overline{{z_2}}=" + chain(f"{u.c().p()}{v.c().p()}", *mul_chain(u.c(), v.c())) + r"\quad(2)")]
        R("conjugate", "medium", pr, l + [f"ដូចនេះ តាមទំនាក់ទំនង $(1)$ និង $(2)$ យើងបាន $\\boxed{{\\overline{{z_1\\times z_2}}=\\overline{{z_1}}\\times\\overline{{z_2}}}}$ ។"], r.c().tex(),
          [(f"conjugate(expand({u.py()}*{v.py()}))", f"expand(conjugate({u.py()})*conjugate({v.py()}))", "both sides"), (f"conjugate(expand({u.py()}*{v.py()}))", r.c().py(), "value")], (t, key(u), key(v)))
    elif t == "prop_quot":
        v = K(Z(1, 1), Z(1, -1), Z(2, 1), Z(1, -2), Z(3, 1), Z(1, 3), Z(2, -1)); w = G(-4, 4); u = w * v
        pr = f"គេឱ្យ $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ គណនា $\\overline{{\\left(\\frac{{z_1}}{{z_2}}\\right)}}$ រួចផ្ទៀងផ្ទាត់ថាវាស្មើនឹង $\\frac{{\\overline{{z_1}}}}{{\\overline{{z_2}}}}$ ។"
        l = ["មុនដំបូង ៖", dd(r"\frac{z_1}{z_2}=" + chain(*div_chain(u, v))), dd(rf"\overline{{\left(\frac{{z_1}}{{z_2}}\right)}}={w.c().tex()}\quad(1)"),
             "ម្យ៉ាងទៀត ៖", dd(r"\frac{\overline{z_1}}{\overline{z_2}}=" + chain(*div_chain(u.c(), v.c())) + r"\quad(2)")]
        R("conjugate", "medium", pr, l + [f"ដូចនេះ តាម $(1)$ និង $(2)$ អង្គទាំងពីរស្មើគ្នា ហើយស្មើនឹង $\\boxed{{{w.c().tex()}}}$ ។"], w.c().tex(),
          [(f"conjugate({u.py()}/{v.py()})".replace("conjugate(", "conjugate(expand(") + ")", w.c().py(), "left"), (f"{u.c().py()}/{v.c().py()}", w.c().py(), "right")], (t, key(u), key(v)))
    elif t == "sumdiff":
        u = G(-8, 8)
        pr = K(f"គេឱ្យ $z={u.tex()}$ ។ គណនា $z+\\bar{{z}}$ , $z-\\bar{{z}}$ និង $z\\times\\bar{{z}}$ ។", f"ចំពោះ $z={u.tex()}$ គណនា $z+\\bar{{z}}$ , $z-\\bar{{z}}$ និង $z\\bar{{z}}$ រួចបញ្ជាក់ថាមួយណាជាចំនួនពិត ។")
        s, d, p = u + u.c(), u - u.c(), u * u.c()
        l = [f"យើងមាន $\\bar{{z}}={u.c().tex()}$ ។", dd(f"z+\\bar{{z}}={u.p()}+{u.c().p()}={s.tex()}"), dd(f"z-\\bar{{z}}={u.p()}-{u.c().p()}={d.tex()}"), dd(f"z\\times\\bar{{z}}={nt(u.a)}^{{2}}+{nt(abs(u.b))}^{{2}}={nt(p.a)}".replace(f"{nt(u.a)}^{{2}}", f"({nt(u.a)})^{{2}}" if u.a < 0 else f"{nt(u.a)}^{{2}}"))]
        R("conjugate", "easy", pr, l + [f"ដូចនេះ $\\boxed{{z+\\bar{{z}}={s.tex()}}}$ និង $\\boxed{{z\\times\\bar{{z}}={nt(p.a)}}}$ ជាចំនួនពិត ហើយ $\\boxed{{z-\\bar{{z}}={d.tex()}}}$ ជាចំនួននិមិត្ត ។"], f"{s.tex()},\\ {d.tex()},\\ {nt(p.a)}",
          [(f"{u.py()}+conjugate({u.py()})", s.py(), "sum"), (f"{u.py()}-conjugate({u.py()})", d.py(), "difference"), (f"{u.py()}*conjugate({u.py()})", str(p.a), "product")], (t, key(u)))
    else:
        u = G(-6, 6); w = Z(0, 1) * u.c() * K(1, 2, -1)
        c = K(2, 3, -2); r = c * u.c() + w
        pr = f"គេឱ្យ $z={u.tex()}$ ។ គណនា ${c}\\bar{{z}}+{w.p()}$ ។"
        l = [f"ដោយ $\\bar{{z}}={u.c().tex()}$ យើងបាន ៖", dd(chain(f"{c}\\bar{{z}}+{w.p()}", f"{c}{u.c().p()}+{w.p()}", r.tex()))]
        R("conjugate", "easy", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"{c}*conjugate({u.py()})+{w.py()}", r.py(), "value")], (t, key(u), key(w), c))

TRIP = [(3, 4), (4, 3), (6, 8), (8, 6), (5, 12), (12, 5), (8, 15), (15, 8), (7, 24), (24, 7), (9, 12), (12, 9), (20, 21), (21, 20), (9, 40)]
def rsg(): return K(1, -1)
def g_modulus():
    t = K("simple", "surd", "prod", "quot", "pow", "prop", "frac")
    if t == "simple":
        a, b = K(*TRIP); u = Z(a * rsg(), b * rsg()); v = G(-7, 7)
        pr = K(f"គណនាម៉ូឌុលនៃចំនួនកុំផ្លិច $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។", f"រក $|z_1|$ និង $|z_2|$ ដោយដឹងថា $z_1={u.tex()}$ ហើយ $z_2={v.tex()}$ ។")
        fz = lambda z: f"({nt(z.a)})^{{2}}" if z.a < 0 else f"{nt(z.a)}^{{2}}"
        fy = lambda z: f"({nt(z.b)})^{{2}}" if z.b < 0 else f"{nt(z.b)}^{{2}}"
        l = ["ចំពោះ $z=a+bi$ គេមាន $|z|=r=\\sqrt{a^2+b^2}$ ។",
             dd(f"|z_1|=r_1=\\sqrt{{{fz(u)}+{fy(u)}}}=\\sqrt{{{nt(u.n2())}}}={nt(u.mod())}"), dd(f"|z_2|=r_2=\\sqrt{{{fz(v)}+{fy(v)}}}=\\sqrt{{{nt(v.n2())}}}" + ("" if nt(v.mod()) == f"\\sqrt{{{nt(v.n2())}}}" else f"={nt(v.mod())}"))]
        R("modulus", "easy", pr, l + [f"ដូចនេះ ម៉ូឌុលនៃ $z_1$ គឺ $\\boxed{{{nt(u.mod())}}}$ ហើយម៉ូឌុលនៃ $z_2$ គឺ $\\boxed{{{nt(v.mod())}}}$ ។"], f"|z_1|={nt(u.mod())},\\ |z_2|={nt(v.mod())}",
          [(f"Abs({u.py()})", str(u.mod()), "modulus"), (f"Abs({v.py()})", str(v.mod()), "modulus")], (t, key(u), key(v)))
    elif t == "surd":
        k = K(2, 3, 5, 6, 7); p, q = rng.randint(1, 5), rng.randint(1, 4)
        u = Z(p * rsg(), q * rsg() * RT(k))
        pr = K(f"គណនាម៉ូឌុលនៃ $z={u.tex()}$ ។", f"រកម៉ូឌុលនៃចំនួនកុំផ្លិច $z={u.tex()}$ ។")
        l = [dd(f"|z|=r=\\sqrt{{({nt(u.a)})^{{2}}+\\left({nt(abs(u.b))}\\right)^{{2}}}}=\\sqrt{{{nt(u.a**2)}+{nt(u.b**2)}}}={nt(u.mod())}")]
        R("modulus", "easy", pr, ["យើងមាន ៖"] + l + [f"ដូចនេះ $\\boxed{{|z|={nt(u.mod())}}}$ ។"], f"|z|={nt(u.mod())}", [(f"Abs({u.py()})", str(u.mod()), "modulus")], (t, str(u.a), str(u.b)))
    elif t == "prod":
        u, v = G(-5, 5), G(-5, 5); m1 = u.mod() * v.mod()
        pr = K(f"ដោយមិនពន្លាត គណនា $\\left|{u.p()}{v.p()}\\right|$ ។", f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ គណនា $|z_1\\times z_2|$ ។")
        r = sp.sqrt(u.n2() * v.n2())
        l = [K("តាមលក្ខណៈម៉ូឌុល $|z_1\\times z_2|=|z_1|\\times|z_2|$ យើងបាន ៖", "យើងប្រើ $|z_1z_2|=|z_1||z_2|$ ៖"), dd(f"|{u.tex()}|=\\sqrt{{{nt(u.n2())}}}\\quad,\\quad|{v.tex()}|=\\sqrt{{{nt(v.n2())}}}"), dd(f"\\sqrt{{{nt(u.n2())}}}\\times\\sqrt{{{nt(v.n2())}}}=\\sqrt{{{nt(u.n2()*v.n2())}}}={nt(r)}")]
        if nt(r) == f"\\sqrt{{{nt(u.n2()*v.n2())}}}": l[-1] = dd(f"\\sqrt{{{nt(u.n2())}}}\\times\\sqrt{{{nt(v.n2())}}}={nt(r)}")
        R("modulus", "medium", pr, l + [f"ដូចនេះ ម៉ូឌុលនៃផលគុណស្មើនឹង $\\boxed{{{nt(r)}}}$ ។"], nt(r), [(f"Abs(expand({u.py()}*{v.py()}))", str(r), "modulus of product")], (t, key(u), key(v)))
    elif t == "quot":
        a, b = K(*TRIP[:6]); c, d = K(*TRIP[:6]); u, v = Z(a * rsg(), b * rsg()), Z(c * rsg(), d * rsg())
        r = u.mod() / v.mod()
        pr = K(f"គណនា $\\left|\\frac{{{u.tex()}}}{{{v.tex()}}}\\right|$ ។", f"រកម៉ូឌុលនៃផលចែក $z=\\frac{{{u.tex()}}}{{{v.tex()}}}$ ។")
        l = ["តាមលក្ខណៈម៉ូឌុល $\\left|\\frac{z_1}{z_2}\\right|=\\frac{|z_1|}{|z_2|}$ យើងគណនាម៉ូឌុលនៃភាគយក និងភាគបែងដោយឡែក ៖", dd(f"|{u.tex()}|={nt(u.mod())}\\quad,\\quad|{v.tex()}|={nt(v.mod())}"), dd(rf"\left|\frac{{{u.tex()}}}{{{v.tex()}}}\right|=" + chain(rf"\frac{{{nt(u.mod())}}}{{{nt(v.mod())}}}", nt(r)))]
        R("modulus", "medium", pr, l + [f"ដូចនេះ ម៉ូឌុលនៃផលចែកគឺ $\\boxed{{{nt(r)}}}$ ។"], nt(r), [(f"Abs({u.py()}/{v.py()})", str(r), "modulus of quotient")], (t, key(u), key(v)))
    elif t == "pow":
        u = K(Z(1, 1), Z(1, -1), Z(1, 2), Z(2, -1), Z(3, 4), Z(3, -4), Z(RT(3), 1), Z(1, -RT(3)), Z(2, 2), Z(1, RT(2)), Z(RT(2), RT(2))); n = rng.randint(3, 10)
        r = u.mod() ** n; r = sp.nsimplify(sp.expand(r))
        pr = K(f"គណនា $\\left|({u.tex()})^{{{n}}}\\right|$ ។", f"គេឱ្យ $z={u.tex()}$ ។ គណនា $|z|$ រួចទាញរក $|z^{{{n}}}|$ ។")
        l = [dd(f"|z|=|{u.tex()}|=\\sqrt{{{nt(u.a**2)}+{nt(u.b**2)}}}={nt(u.mod())}"), f"តាមលក្ខណៈម៉ូឌុល $|z^n|=|z|^n$ យើងបាន ៖", dd(f"\\left|({u.tex()})^{{{n}}}\\right|=\\left({nt(u.mod())}\\right)^{{{n}}}={nt(r)}")]
        if "z" not in pr: l[0] = l[0].replace("|z|=|", "|").replace("z", "")
        R("modulus", "medium", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{nt(r)}}}$ ។"], nt(r), [(f"Abs({u.py()})**{n}", str(r), "power modulus"), (f"Abs(expand({u.py()}**{n}))", str(r), "direct")], (t, key(u), n))
    elif t == "prop":
        u, v = G(-4, 4), G(-4, 4); r = u * v
        pr = f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ ផ្ទៀងផ្ទាត់ថា $|z_1\\times z_2|=|z_1|\\times|z_2|$ ។"
        s = sp.sqrt(r.n2())
        l = ["គណនាអង្គខាងឆ្វេង ៖", dd(f"z_1\\times z_2={r.tex()}"), dd(f"|z_1\\times z_2|=\\sqrt{{{nt(r.a**2)}+{nt(r.b**2)}}}=\\sqrt{{{nt(r.n2())}}}\\quad(1)"), "គណនាអង្គខាងស្តាំ ៖", dd(f"|z_1|\\times|z_2|=\\sqrt{{{nt(u.n2())}}}\\times\\sqrt{{{nt(v.n2())}}}=\\sqrt{{{nt(u.n2()*v.n2())}}}\\quad(2)")]
        R("modulus", "medium", pr, l + [f"ដូចនេះ តាម $(1)$ និង $(2)$ យើងបាន $\\boxed{{|z_1\\times z_2|=|z_1|\\times|z_2|={nt(s)}}}$ ។"], nt(s), [(f"Abs(expand({u.py()}*{v.py()}))", f"Abs({u.py()})*Abs({v.py()})", "both sides"), (f"Abs(expand({u.py()}*{v.py()}))", str(s), "value")], (t, key(u), key(v)))
    else:
        a, b = K(*TRIP[:6]); c = K(5, 10, 13, 25); 
        den = K(5, 10, 13, 25); u = Z(Q(a * rsg(), den), Q(b * rsg(), den))
        pr = f"គណនាម៉ូឌុលនៃ $z={u.tex()}$ ។"
        l = [dd(f"|z|=\\sqrt{{\\left({nt(abs(u.a))}\\right)^{{2}}+\\left({nt(abs(u.b))}\\right)^{{2}}}}=\\sqrt{{{nt(u.n2())}}}={nt(u.mod())}")]
        R("modulus", "easy", pr, ["យើងមាន ៖"] + l + [f"ដូចនេះ $\\boxed{{|z|={nt(u.mod())}}}$ ។"], f"|z|={nt(u.mod())}", [(f"Abs({u.py()})", str(u.mod()), "modulus")], (t, key(u)))

DENS = [Z(1, 1), Z(1, -1), Z(2, 1), Z(2, -1), Z(1, 2), Z(1, -2), Z(3, 1), Z(3, -1), Z(1, 3), Z(1, -3), Z(3, 2), Z(2, -3), Z(3, 4), Z(4, -3), Z(2, 2), Z(0, 2), Z(0, 3), Z(0, 1), Z(0, -1)]
def g_quotient():
    t = K("exact", "frac", "named", "imagden", "surd")
    if t == "exact":
        v = K(*DENS[:14]); w = G(-5, 5); u = w * v; r = w
    elif t == "frac":
        v = K(*DENS[:14]); u = G(-7, 7); r = u / v
        if r.a.q > 26 or r.b.q > 26: return
    elif t == "named":
        v = K(*DENS[:14]); w = G(-4, 4) ; u = w * v; r = w
    elif t == "imagden":
        v = K(*DENS[14:]); u = G(-8, 8); r = u / v
    else:
        k = K(2, 3, 5); p, q = rng.randint(1, 3), K(1, -1)
        v = Z(p, q * RT(k)); w = Z(rng.randint(1, 4) * rsg(), rng.randint(1, 3) * rsg() * RT(k)); u = w * v; r = w
        pr = K(f"សរសេរ $\\frac{{{u.tex()}}}{{{v.tex()}}}$ ជាទម្រង់ពីជគណិត ។", f"គណនាផលចែក $\\frac{{{u.tex()}}}{{{v.tex()}}}$ ។")
        n = u * v.c()
        l = [f"គុណភាគយក និងភាគបែងនឹង ${v.c().tex()}$ ។ ភាគបែងក្លាយជា ${nt(v.a**2)}+{nt(v.b**2)}={nt(v.n2())}$ ។", dd(chain(rf"\frac{{{u.tex()}}}{{{v.tex()}}}", rf"\frac{{({u.tex()})({v.c().tex()})}}{{{nt(v.n2())}}}", rf"\frac{{{n.tex()}}}{{{nt(v.n2())}}}", r.tex()))]
        R("quotient", "medium", pr, l + [f"ដូចនេះ $\\boxed{{\\frac{{{u.tex()}}}{{{v.tex()}}}={r.tex()}}}$ ។"], r.tex(), [(f"{u.py()}/{v.py()}", r.py(), "quotient")], (t, key(u), key(v)))
        return
    frac = rf"\frac{{{u.tex()}}}{{{v.tex()}}}"
    if t == "named":
        pr = f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ " + K("គណនា $\\frac{z_1}{z_2}$ ។", "សរសេរ $\\frac{z_1}{z_2}$ ជាទម្រង់ពីជគណិត ។")
        lead = r"\frac{z_1}{z_2}="
    else:
        pr = K(f"សរសេរ ${frac}$ ជាទម្រង់ពីជគណិត ។", f"គណនាផលចែក ${frac}$ ។", f"សរសេរ $z={frac}$ {K(*ALGF)} ។"); lead = ""
    if t == "imagden":
        cj = v.c()
        l = [K(f"គុណភាគយក និងភាគបែងនឹង $i$ ដើម្បីឱ្យភាគបែងក្លាយជាចំនួនពិត ៖" , "យើងលុប $i$ ពីភាគបែង ដោយគុណនឹង $i$ ទាំងភាគយក និងភាគបែង ៖")]
        l.append(dd(chain(frac, rf"\frac{{({u.tex()})i}}{{{v.tex()}\times i}}" if v.tex() not in ("i", "-i") else rf"\frac{{({u.tex()})i}}{{{v.tex()}\times i}}", rf"\frac{{{(u*I_).tex()}}}{{{(v*I_).tex()}}}", r.tex())))
    else:
        way = K(1, 1, 2)
        if way == 1 or t == "named":
            l = [K("គុណភាគយក និងភាគបែងនឹងចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែង ៖", f"ចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែងគឺ ${v.c().tex()}$ ។ យើងគុណភាគយក និងភាគបែងនឹងវា ៖"), dd(lead + chain(*div_chain(u, v)))]
        else:
            l = ["យើងគណនាភាគយក និងភាគបែងដោយឡែក បន្ទាប់ពីគុណនឹងចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែង ៖", f"ភាគបែង ៖ ${v.p()}{v.c().p()}={nt(v.a**2)}+{nt(v.b**2)}={nt(v.n2())}$", f"ភាគយក ៖ $" + chain(f"{u.p()}{v.c().p()}", *mul_chain(u, v.c())) + "$", dd(chain(frac, rf"\frac{{{(u*v.c()).tex()}}}{{{nt(v.n2())}}}", r.tex()))]
    lhs = lead[:-1] if lead else frac
    R("quotient", "easy" if t != "frac" else "medium", pr, l + [f"ដូចនេះ $\\boxed{{{lhs}={r.tex()}}}$ ។"], r.tex(), [(f"{u.py()}/{v.py()}", r.py(), "quotient")], (t, key(u), key(v)))

def g_inverse_mix():
    t = K("inverse", "sum_inv", "ratio_sum", "z_plus_inv", "expr_at")
    u = K(*DENS[:14]); v = K(*DENS[:14])
    if t == "inverse":
        u = G(-5, 5); r = Z(1) / u
        pr = K(f"រកចំនួនច្រាសនៃ $z={u.tex()}$ ជាទម្រង់ពីជគណិត ។".replace("ចំនួនច្រាសនៃ $z", "ទម្រង់ពីជគណិតនៃ $\\frac{1}{z}$ ដោយដឹងថា $z").replace(" ជាទម្រង់ពីជគណិត ។", " ។"), f"គេឱ្យ $z={u.tex()}$ ។ សរសេរ $\\frac{{1}}{{z}}$ ជាទម្រង់ពីជគណិត ។")
        l = [f"ដោយ $z\\bar{{z}}=|z|^2={nt(u.n2())}$ យើងបាន $\\frac{{1}}{{z}}=\\frac{{\\bar{{z}}}}{{|z|^2}}$ ។", dd(r"\frac{1}{z}=" + chain(rf"\frac{{{u.c().tex()}}}{{{nt(u.n2())}}}", r.tex()))]
        R("inverse_and_mixed", "easy", pr, l + [f"ដូចនេះ $\\boxed{{\\frac{{1}}{{z}}={r.tex()}}}$ ។"], r.tex(), [(f"1/{u.py()}", r.py(), "inverse")], (t, key(u)))
    elif t == "sum_inv":
        if u == v or u == v.c(): return
        a, b = Z(1) / u, Z(1) / v; r = a + b
        if r.a.q > 60 or r.b.q > 60: return
        pr = K(f"គណនា $\\frac{{1}}{{{u.tex()}}}+\\frac{{1}}{{{v.tex()}}}$ ។", f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។ សរសេរ $\\frac{{1}}{{z_1}}+\\frac{{1}}{{z_2}}$ ជាទម្រង់ពីជគណិត ។")
        l = ["យើងសរសេរប្រភាគនីមួយៗជាទម្រង់ពីជគណិត ៖", dd(chain(rf"\frac{{1}}{{{u.tex()}}}", rf"\frac{{{u.c().tex()}}}{{{nt(u.n2())}}}", a.tex())), dd(chain(rf"\frac{{1}}{{{v.tex()}}}", rf"\frac{{{v.c().tex()}}}{{{nt(v.n2())}}}", b.tex())), "បូកផ្នែកពិតនឹងផ្នែកពិត ផ្នែកនិមិត្តនឹងផ្នែកនិមិត្ត ៖", dd(f"\\left({a.tex()}\\right)+\\left({b.tex()}\\right)={r.tex()}")]
        R("inverse_and_mixed", "medium", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"1/{u.py()}+1/{v.py()}", r.py(), "sum of inverses")], (t, key(u), key(v)))
    elif t == "ratio_sum":
        a, b = G(-5, 5), G(-5, 5); s, d = a + b, a - b
        if d == 0 or s == 0: return
        r = s / d
        if r.a.q > 26 or r.b.q > 26: return
        pr = f"{K(*GIVE)} $z_1={a.tex()}$ និង $z_2={b.tex()}$ ។ គណនា $\\frac{{z_1+z_2}}{{z_1-z_2}}$ ។"
        l = [f"មុនដំបូង $z_1+z_2={s.tex()}$ និង $z_1-z_2={d.tex()}$ ។", dd(r"\frac{z_1+z_2}{z_1-z_2}=" + chain(*div_chain(s, d)))]
        R("inverse_and_mixed", "medium", pr, l + [f"ដូចនេះ $\\boxed{{\\frac{{z_1+z_2}}{{z_1-z_2}}={r.tex()}}}$ ។"], r.tex(), [(f"({a.py()}+{b.py()})/({a.py()}-{b.py()})", r.py(), "ratio")], (t, key(a), key(b)))
    elif t == "z_plus_inv":
        a = K(*DENS[:14]); iv = Z(1) / a; r = a + iv
        pr = K(f"គេឱ្យ $z={a.tex()}$ ។ គណនា $z+\\frac{{1}}{{z}}$ ។", f"ចំពោះ $z={a.tex()}$ សរសេរ $z-\\frac{{1}}{{z}}$ ជាទម្រង់ពីជគណិត ។")
        sg = 1 if "z+" in pr else -1; r = a + sg * iv; op = "+" if sg > 0 else "-"
        l = [dd(r"\frac{1}{z}=" + chain(rf"\frac{{1}}{{{a.tex()}}}", rf"\frac{{{a.c().tex()}}}{{{nt(a.n2())}}}", iv.tex())), dd(f"z{op}\\frac{{1}}{{z}}={a.p()}{op}\\left({iv.tex()}\\right)={r.tex()}")]
        R("inverse_and_mixed", "medium", pr, l + [f"ដូចនេះ លទ្ធផលគឺ $\\boxed{{{r.tex()}}}$ ។"], r.tex(), [(f"{a.py()}{op}1/{a.py()}", r.py(), "value")], (t, key(a), sg))
    else:
        a = G(-3, 3); b, c = rng.randint(-5, 5), rng.randint(-6, 6); r = a * a + b * a + c
        e = ptex([1, b, c])
        pr = K(f"គេឱ្យពហុធា $P(z)={e}$ ។ គណនា $P({a.tex()})$ ។", f"គណនាតម្លៃនៃកន្សោម $P(z)={e}$ ចំពោះ $z={a.tex()}$ ។")
        s = a * a
        l = [f"មុនដំបូង $({a.tex()})^{{2}}={s.tex()}$ ។", "ជំនួសចូល ៖", dd(chain(f"P({a.tex()})", f"{s.p()}{'+' if b>=0 else '-'}{abs(b)}({a.tex()}){'+' if c>=0 else '-'}{abs(c)}", r.tex()))]
        R("inverse_and_mixed", "easy", pr, l + [f"ដូចនេះ $\\boxed{{P({a.tex()})={r.tex()}}}$ ។"], r.tex(), [(f"expand({a.py()}**2+({b})*{a.py()}+({c}))", r.py(), "value")], (t, key(a), b, c))

# ---------- D. equality ----------
def g_equality():
    t = K("lin", "prod", "frac", "basis", "square", "mxy")
    x0, y0 = rng.randint(-5, 5), rng.randint(-5, 5)
    if x0 == 0 or y0 == 0: return
    W = K("រកចំនួនពិត $x$ និង $y$ ដែលផ្ទៀងផ្ទាត់ ", "កំណត់ចំនួនពិត $x$ និង $y$ ដើម្បីឱ្យ ", "រកចំនួនពិត $x,y$ ដែលធ្វើឱ្យ ")
    RULE = K("ចំនួនកុំផ្លិចពីរស្មើគ្នា លុះត្រាតែផ្នែកពិតស្មើគ្នា ហើយផ្នែកនិមិត្តស្មើគ្នា ។", "យើងប្រើលក្ខខណ្ឌស្មើគ្នា ៖ $a+bi=c+di$ លុះត្រាតែ $a=c$ និង $b=d$ ។", "ផ្ទឹមផ្នែកពិតនឹងផ្នែកពិត និងផ្នែកនិមិត្តនឹងផ្នែកនិមិត្ត ។".replace("ផ្ទឹម", "យើងប្រៀបធៀប"))
    if t == "lin":
        p, q, r_, s = [K(1, 2, 3, -1, -2) for _ in range(4)]
        if p * s - q * r_ == 0: return
        A, B = p * x0 + q * y0, r_ * x0 + s * y0
        e1, e2 = tsum([(p, "x"), (q, "y")]), tsum([(r_, "x"), (s, "y")])
        rhs = Z(A, B)
        eq_ = f"({e1})+({e2})i={rhs.tex()}"
        l = [RULE, "គេបានប្រព័ន្ធសមីការ ៖", dd(rf"\begin{{cases}}{e1}={A}\\{e2}={B}\end{{cases}}"), f"ដោះស្រាយប្រព័ន្ធនេះ {K('យើងបាន', 'គេទទួលបាន')} $x={x0}$ និង $y={y0}$ ។"]
        R("equality", "easy", W + f"${eq_}$ ។", l + [f"ដូចនេះ $\\boxed{{x={x0},\\ y={y0}}}$ ។"], f"x={x0},\\ y={y0}", [(f"({p})*({x0})+({q})*({y0})", str(A), "real"), (f"({r_})*({x0})+({s})*({y0})", str(B), "imag")], (t, p, q, r_, s, x0, y0))
    elif t == "prod":
        v = G(-4, 4); r = Z(x0, y0) * v
        eq_ = f"(x+iy){v.p()}={r.tex()}"
        way = K(1, 2)
        if way == 1:
            l = ["ពន្លាតអង្គខាងឆ្វេង ៖", dd(f"(x+iy){v.p()}=({tsum([(v.a,'x'),(-v.b,'y')])})+({tsum([(v.b,'x'),(v.a,'y')])})i"), RULE, dd(rf"\begin{{cases}}{tsum([(v.a,'x'),(-v.b,'y')])}={nt(r.a)}\\{tsum([(v.b,'x'),(v.a,'y')])}={nt(r.b)}\end{{cases}}"), f"ដោះស្រាយប្រព័ន្ធ យើងបាន $x={x0}$ និង $y={y0}$ ។"]
        else:
            l = [f"ចែកអង្គទាំងពីរនឹង ${v.tex()}$ ៖", dd("x+iy=" + chain(*div_chain(r, v))), RULE.replace("ចំនួនកុំផ្លិចពីរស្មើគ្នា លុះត្រាតែផ្នែកពិតស្មើគ្នា ហើយផ្នែកនិមិត្តស្មើគ្នា ។", "ដោយ $x$ និង $y$ ជាចំនួនពិត យើងអានតម្លៃបានភ្លាម ។"), ]
        R("equality", "medium", W + f"${eq_}$ ។", l + [f"ដូចនេះ $\\boxed{{x={x0},\\ y={y0}}}$ ។"], f"x={x0},\\ y={y0}", [(f"(({x0})+({y0})*I)*{v.py()}", r.py(), "substitution")], (t, key(v), x0, y0))
    elif t == "basis":
        u, v = G(-4, 4), G(-4, 4)
        det = u.a * v.b - u.b * v.a
        if det == 0: return
        r = x0 * u + y0 * v
        eq_ = f"x{u.p()}+y{v.p()}={r.tex()}"
        e1, e2 = tsum([(u.a, "x"), (v.a, "y")]), tsum([(u.b, "x"), (v.b, "y")])
        l = ["ដាក់ផ្នែកពិត និងផ្នែកនិមិត្តដោយឡែក ៖", dd(f"({e1})+({e2})i={r.tex()}"), RULE, dd(rf"\begin{{cases}}{e1}={nt(r.a)}\\{e2}={nt(r.b)}\end{{cases}}"), f"ដោះស្រាយប្រព័ន្ធ (ដោយជំនួស ឬបំបាត់អថេរ) គេបាន $x={x0}$ , $y={y0}$ ។"]
        R("equality", "medium", W + f"${eq_}$ ។", l + [f"ដូចនេះ $\\boxed{{x={x0},\\ y={y0}}}$ ។"], f"x={x0},\\ y={y0}", [(f"({x0})*{u.py()}+({y0})*{v.py()}", r.py(), "substitution")], (t, key(u), key(v), x0, y0))
    elif t == "frac":
        u = K(Z(1, 1), Z(1, -1), Z(2, 1), Z(1, 2), Z(1, -2), Z(3, 1)); v = K(Z(2, 1), Z(1, 2), Z(1, -1), Z(3, -1), Z(2, -1), Z(1, 1))
        if u == v: return
        # x/u + y/v = r, x=x0*n1, y=y0*n2 keep integers
        X, Y = x0 * u.n2(), y0 * v.n2()
        r = X / u + Y / v
        d1, d2 = u.c(), v.c()
        det = d1.a * d2.b - d1.b * d2.a
        if det == 0: return
        eq_ = rf"\frac{{x}}{{{u.tex()}}}+\frac{{y}}{{{v.tex()}}}={r.tex()}"
        e1 = tsum([(Q(u.a, u.n2()), "x"), (Q(v.a, v.n2()), "y")]); e2 = tsum([(Q(-u.b, u.n2()), "x"), (Q(-v.b, v.n2()), "y")])
        l = ["យើងសរសេរប្រភាគនីមួយៗជាទម្រង់ពីជគណិត ៖", dd(rf"\frac{{x}}{{{u.tex()}}}=\frac{{x({u.c().tex()})}}{{{nt(u.n2())}}}\quad,\quad\frac{{y}}{{{v.tex()}}}=\frac{{y({v.c().tex()})}}{{{nt(v.n2())}}}"),
             RULE, dd(rf"\begin{{cases}}{e1}={nt(r.a)}\\{e2}={nt(r.b)}\end{{cases}}"), f"ដោះស្រាយប្រព័ន្ធ យើងបាន $x={X}$ និង $y={Y}$ ។"]
        R("equality", "hard", W + f"${eq_}$ ។", l + [f"ដូចនេះ $\\boxed{{x={X},\\ y={Y}}}$ ។"], f"x={X},\\ y={Y}", [(f"({X})/{u.py()}+({Y})/{v.py()}", r.py(), "substitution")], (t, key(u), key(v), x0, y0))
    elif t == "square":
        a = rng.randint(1, 5); b = rng.randint(1, 5) * rsg(); r = Z(a, b) ** 2
        if r.a == 0: return
        eq_ = f"x^{{2}}-y^{{2}}+2xyi={r.tex()}"
        # all real solutions (±a, ±b)
        l = [RULE, dd(rf"\begin{{cases}}x^{{2}}-y^{{2}}={nt(r.a)}\\2xy={nt(r.b)}\end{{cases}}"), f"ពីសមីការទីពីរ $y=\\frac{{{nt(Q(r.b,2))}}}{{x}}$ ។ ជំនួសចូលសមីការទីមួយ ហើយគុណនឹង $x^2$ ៖", dd(f"x^{{4}}{tsum([(-r.a,'x^{2}')]) if -r.a<0 else '+'+tsum([(-r.a,'x^{2}')])}-{nt(Q(r.b,2)**2)}=0"),
             f"តាង $t=x^2\\ge 0$ សមីការក្លាយជា ${ptex([1,-r.a,-Q(r.b,2)**2],'t')}=0$ ដែលមានឫសវិជ្ជមាន $t={a*a}$ ។ នាំឱ្យ $x=\\pm{a}$ ។"]
        R("equality", "hard", W + f"${eq_}$ ។", l + [f"ដូចនេះ $\\boxed{{(x,y)=({a},{b})}}$ ឬ $\\boxed{{(x,y)=({-a},{-b})}}$ ។"], f"(x,y)=({a},{b}),\\ ({-a},{-b})", [(f"({a})**2-({b})**2", str(r.a), "real"), (f"2*({a})*({b})", str(r.b), "imag"), (f"({-a})**2-({-b})**2", str(r.a), "second pair")], (t, a, b))
    else:
        v = G(-3, 3); w = Z(x0, y0)
        # conj relation: (x+iy) + c(x-iy)=rhs
        c = K(2, 3, -2, 4)
        rhs = w + c * w.c()
        eq_ = f"(x+iy)+{c}(x-iy)={rhs.tex()}" if c > 0 else f"(x+iy)-{-c}(x-iy)={rhs.tex()}"
        l = [dd(f"({nt(1+c)})x+({nt(1-c)})yi={rhs.tex()}"), RULE, dd(rf"{nt(1+c)}x={nt(rhs.a)}\quad,\quad {nt(1-c)}y={nt(rhs.b)}"), f"នាំឱ្យ $x={x0}$ និង $y={y0}$ ។"]
        R("equality", "easy", W + f"${eq_}$ ។", ["ពន្លាត ហើយបូកតួដូចគ្នា ៖"] + l + [f"ដូចនេះ $\\boxed{{x={x0},\\ y={y0}}}$ ។"], f"x={x0},\\ y={y0}", [(f"{w.py()}+({c})*{w.c().py()}", rhs.py(), "substitution")], (t, c, x0, y0))

# ---------- E. square roots ----------
def sqrt_lines(w, r, name="\\delta", word=None):
    """Lines finding the square roots of w=r^2 by x+iy, with r having nonzero parts (rational)."""
    A, B = w.a, w.b; M = w.mod(); p, q = abs(r.a), abs(r.b)
    same = B > 0
    wn = word or f"${w.tex()}$"
    l = [K(f"តាង ${name}=x+iy$ ដែល $x,y\\in\\mathbb{{R}}$ ជាឫសការេនៃ {wn} ។", f"យក ${name}=x+iy$ ($x,y$ ជាចំនួនពិត) ដែល ${name}^2={w.tex()}$ ។"),
         "យើងបាន ៖", dd(rf"(x+iy)^{{2}}={w.tex()}\Leftrightarrow x^{{2}}-y^{{2}}+2xyi={w.tex()}"),
         "ដោយផ្នែកពិតស្មើគ្នា និងផ្នែកនិមិត្តស្មើគ្នា ៖", dd(rf"\begin{{cases}}x^{{2}}-y^{{2}}={nt(A)}\quad(1)\\2xy={nt(B)}\quad(2)\end{{cases}}"),
         f"ម្យ៉ាងទៀត $|{name}|^2=|{w.tex()}|$ នាំឱ្យ ៖", dd(rf"x^{{2}}+y^{{2}}=\sqrt{{{nt(A**2)}+{nt(B**2)}}}={nt(M)}\quad(3)"),
         "បូក $(1)$ និង $(3)$ រួចដក $(1)$ ពី $(3)$ យើងបាន ៖", dd(rf"x^{{2}}={nt(p**2)}\quad,\quad y^{{2}}={nt(q**2)}"),
         f"តាម $(2)$ ផលគុណ $xy$ {'វិជ្ជមាន ដូច្នេះ $x$ និង $y$ មានសញ្ញាដូចគ្នា' if same else 'អវិជ្ជមាន ដូច្នេះ $x$ និង $y$ មានសញ្ញាផ្ទុយគ្នា'} ។"]
    return l

def g_sqrt():
    t = K("gen", "gen", "gen", "imag", "real", "surd", "half")
    if t == "gen":
        r = G(-7, 7)
        if r.a < 0 or abs(r.a) == abs(r.b): return
        w = r * r
        pr = K(f"រកឫសការេនៃចំនួនកុំផ្លិច $z={w.tex()}$ ។", f"គណនាឫសការេនៃ ${w.tex()}$ ។", f"រកចំនួនកុំផ្លិច $Z$ ដែល $Z^2={w.tex()}$ ។", f"កំណត់ចំនួនកុំផ្លិច $\\delta$ ដែល $\\delta^2={w.tex()}$ ។")
        nm = "Z" if "Z^2" in pr else "\\delta"
        l = sqrt_lines(w, r, nm)
        fin = f"ដូចនេះ ឫសការេនៃ ${w.tex()}$ គឺ $\\boxed{{{r.tex()}}}$ និង $\\boxed{{{(-r).tex()}}}$ ។"
        R("square_root", "medium", pr, l + [fin], f"\\pm({r.tex()})", [(f"expand({r.py()}**2)", w.py(), "first root"), (f"expand({(-r).py()}**2)", w.py(), "second root")], (t, key(r)))
    elif t == "imag":
        c = K(1, 2, 3, 4, 5, 6, 7) ; s = rsg(); w = Z(0, 2 * c * c * s); r = Z(c, c * s)
        pr = K(f"រកឫសការេនៃ ${w.tex()}$ ។", f"ដោះស្រាយសមីការ $z^2={w.tex()}$ ក្នុងសំណុំចំនួនកុំផ្លិច ។")
        l = [f"តាង $z=x+iy$ ដែល $x,y\\in\\mathbb{{R}}$ ។ សមីការ $(x+iy)^2={w.tex()}$ ផ្តល់ ៖", dd(rf"\begin{{cases}}x^{{2}}-y^{{2}}=0\\2xy={nt(w.b)}\end{{cases}}"), f"សមីការទីមួយឱ្យ $y=x$ ឬ $y=-x$ ។",
             (f"បើ $y=x$ នោះ $2x^2={nt(w.b)}$ នាំឱ្យ $x=\\pm{c}$ ។ ករណី $y=-x$ ឱ្យ $-2x^2={nt(w.b)}$ ដែលគ្មានឫសពិត ។" if s > 0 else f"បើ $y=-x$ នោះ $-2x^2={nt(w.b)}$ នាំឱ្យ $x=\\pm{c}$ ។ ករណី $y=x$ ឱ្យ $2x^2={nt(w.b)}$ ដែលគ្មានឫសពិត ។")]
        R("square_root", "medium", pr, l + [f"ដូចនេះ ឫសទាំងពីរគឺ $\\boxed{{{r.tex()}}}$ និង $\\boxed{{{(-r).tex()}}}$ ។"], f"\\pm({r.tex()})", [(f"expand({r.py()}**2)", w.py(), "root"), (f"expand({(-r).py()}**2)", w.py(), "root")], (t, c, s))
    elif t == "real":
        n = K(*range(2, 25)); neg = sp.sqrt(n); w = Z(-n, 0); r = Z(0, neg)
        pr = K(f"រកឫសការេនៃចំនួនពិត ${-n}$ ក្នុង $\\mathbb{{C}}$ ។", f"ដោះស្រាយសមីការ $z^2+{n}=0$ ក្នុងសំណុំចំនួនកុំផ្លិច ។", f"រកគ្រប់ចំនួនកុំផ្លិច $z$ ដែល $z^2={-n}$ ។")
        l = [dd(f"z^{{2}}={-n}\\Leftrightarrow z^{{2}}={n}i^{{2}}\\Leftrightarrow z^{{2}}-({r.tex()})^{{2}}=0"), "ដាក់ជាកត្តា ៖", dd(f"(z-{r.p()})(z+{r.p()})=0")]
        R("square_root", "easy", pr, [f"ដោយ $i^2=-1$ យើងអាចសរសេរ ៖"] + l + [f"ដូចនេះ $\\boxed{{z={r.tex()}}}$ ឬ $\\boxed{{z={(-r).tex()}}}$ ។"], f"z=\\pm {r.tex()}", [(f"expand({r.py()}**2)", str(-n), "root"), (f"expand({(-r).py()}**2)", str(-n), "root")], (t, n))
    elif t == "surd":
        a, b = rng.randint(1, 7), rng.randint(1, 7)
        if a == b or sp.sqrt(a).is_integer and sp.sqrt(b).is_integer: return
        r = Z(RT(a), RT(b) * rsg()); w = r * r
        pr = K(f"បង្ហាញថា $({r.tex()})^{{2}}={w.tex()}$ រួចទាញរកឫសការេនៃ ${w.tex()}$ ។", f"គណនា $\\left({r.tex()}\\right)^{{2}}$ ។ ទាញរកឫសការេនៃ ${w.tex()}$ ។")
        l = ["ពន្លាតការេ ៖", dd(chain(f"({r.tex()})^{{2}}", f"{nt(r.a**2)}{'+' if r.b>0 else '-'}2\\times{nt(r.a)}\\times i{nt(abs(r.b))}+{nt(r.b**2)}i^{{2}}".replace("\\times i", "\\times i "), w.tex())), "ដូច្នេះ ចំនួននេះ និងចំនួនផ្ទុយរបស់វា សុទ្ធតែមានការេស្មើនឹង " + f"${w.tex()}$ ។"]
        R("square_root", "medium", pr, l + [f"ដូចនេះ ឫសការេនៃ ${w.tex()}$ គឺ $\\boxed{{\\pm\\left({r.tex()}\\right)}}$ ។"], f"\\pm({r.tex()})", [(f"expand({r.py()}**2)", w.py(), "square")], (t, a, b, str(r.b)))
    else:
        p, q = rng.randint(1, 5), rng.randint(1, 5) * rsg()
        if p == abs(q): return
        r = Z(Q(p, 2), Q(q, 2)); w = r * r
        if w.a == 0: return
        l = sqrt_lines(w, r, "\\delta")
        R("square_root", "hard", f"រកឫសការេនៃចំនួនកុំផ្លិច ${w.tex()}$ ។", l + [f"ដូចនេះ ឫសការេគឺ $\\boxed{{{r.tex()}}}$ និង $\\boxed{{{(-r).tex()}}}$ ។"], f"\\pm({r.tex()})", [(f"expand({r.py()}**2)", w.py(), "root"), (f"expand({(-r).py()}**2)", w.py(), "root")], (t, p, q))

# ---------- F. linear equations ----------
SOLVEC = ["ដោះស្រាយសមីការ {E} ក្នុងសំណុំចំនួនកុំផ្លិច ។", "ដោះស្រាយក្នុង $\\mathbb{C}$ នូវសមីការ {E} ។", "រកចំនួនកុំផ្លិច $z$ ដែលផ្ទៀងផ្ទាត់ {E} ។", "ដោះស្រាយសមីការ {E} ក្នុង $\\mathbb{C}$ រួចសរសេរចម្លើយជាទម្រង់ពីជគណិត ។"]
def g_linear():
    t = K("az", "azb", "both", "frac", "iz", "ratio")
    z0 = G(-5, 5)
    S = K(*SOLVEC)
    if t == "az":
        a = K(*DENS[:14]); b = a * z0
        E = f"{a.p()}z={b.tex()}"
        l = [f"ចែកអង្គទាំងពីរនឹង ${a.tex()}$ ៖", dd("z=" + chain(*div_chain(b, a)))]
        ck = [(f"{a.py()}*{z0.py()}", b.py(), "substitution")]
    elif t == "azb":
        a = G(-3, 3); b = G(-6, 6); c = a * z0 + b
        E = f"{a.p()}z+{b.p()}={c.tex()}"
        d = c - b
        l = [f"បញ្ជូន ${b.tex()}$ ទៅអង្គខាងស្តាំ ៖", dd(f"{a.p()}z={c.p()}-{b.p()}={d.tex()}"), "ចែកនឹងមេគុណនៃ $z$ ៖", dd("z=" + chain(*div_chain(d, a)))]
        ck = [(f"{a.py()}*{z0.py()}+{b.py()}", c.py(), "substitution")]
    elif t == "both":
        a, c = G(-3, 3), G(-3, 3); b = G(-5, 5)
        if a == c: return
        d = (a - c) * z0 + b
        E = f"{a.p()}z+{b.p()}={c.p()}z+{d.p()}"
        ac, db = a - c, d - b
        l = ["ប្រមូលតួមាន $z$ ទៅអង្គខាងឆ្វេង ៖", dd(f"\\left[{a.p()}-{c.p()}\\right]z={d.p()}-{b.p()}"), dd(f"{ac.p()}z={db.tex()}"), dd("z=" + chain(*div_chain(db, ac)) if ac.b != 0 or True else "")]
        ck = [(f"{a.py()}*{z0.py()}+{b.py()}", f"{c.py()}*{z0.py()}+{d.py()}", "both sides")]
    elif t == "frac":
        a = G(-4, 4); c = K(*DENS[:14]); 
        # (z+a)/(z+b)=c ; choose b so that denominators fine
        b = G(-4, 4)
        if c == 1 or z0 + b == 0: return
        c_ = (z0 + a) / (z0 + b)
        if not c_.isint() or c_ == 1: return
        c = c_
        E = rf"\frac{{z+{a.p()}}}{{z+{b.p()}}}={c.tex()}"
        rhs = c * b - a; co = 1 - c
        l = [f"លក្ខខណ្ឌ ៖ $z\\neq{(-b).tex()}$ ។ គុណអង្គទាំងពីរនឹង $z+{b.p()}$ ៖", dd(f"z+{a.p()}={c.p()}\\left[z+{b.p()}\\right]"), "ប្រមូលតួមាន $z$ ៖", dd(f"{co.p()}z={rhs.tex()}"), dd("z=" + chain(*div_chain(rhs, co))), f"តម្លៃនេះខុសពី ${(-b).tex()}$ ដូច្នេះទទួលយកបាន ។"]
        ck = [(f"({z0.py()}+{a.py()})/({z0.py()}+{b.py()})", c.py(), "substitution")]
    elif t == "iz":
        k = K(1, 2, 3, -1, -2); ii = Z(0, k); b = G(-5, 5); c = ii * z0 + b
        E = f"{ii.tex()}z+{b.p()}={c.tex()}"
        d = c - b
        l = [dd(f"{ii.tex()}z={d.tex()}"), f"គុណអង្គទាំងពីរនឹង $i$ ដើម្បីលុប $i$ ពីមេគុណ ៖", dd(f"{(ii*I_).tex()}z={(d*I_).tex()}"), dd(f"z={z0.tex()}")]
        ck = [(f"{ii.py()}*{z0.py()}+{b.py()}", c.py(), "substitution")]
    else:
        a = K(*DENS[:10]); b = G(-3, 3); 
        c = a * z0 - b * z0  # a z - b z = c
        if a == b or (a - b) == 0: return
        E = f"{a.p()}z={b.p()}z+{c.p()}"
        ab = a - b
        l = ["ប្រមូលតួមាន $z$ ៖", dd(f"\\left[{a.p()}-{b.p()}\\right]z={c.tex()}"), dd(f"{ab.p()}z={c.tex()}"), dd("z=" + chain(*div_chain(c, ab)))]
        ck = [(f"{a.py()}*{z0.py()}", f"{b.py()}*{z0.py()}+{c.py()}", "both sides")]
    R("linear_equation", "easy" if t in ("az", "iz") else "medium", S.replace("{E}", ll(E)), l + [K(f"ដូចនេះ $\\boxed{{z={z0.tex()}}}$ ។", f"ដូចនេះ សមីការមានឫស $\\boxed{{z={z0.tex()}}}$ ។")], f"z={z0.tex()}", ck, (t, E))

def g_linear_conj():
    t = K("real", "cplx", "mixz", "zbar_only", "sys")
    z0 = G(-5, 5)
    S = K(*SOLVEC)
    if t == "real":
        p, q = rng.randint(1, 5), K(-3, -2, -1, 1, 2, 3, 4)
        if p == abs(q): return
        c = p * z0 + q * z0.c()
        E = f"{p}z{'+' if q>0 else '-'}{abs(q)}\\bar{{z}}={c.tex()}".replace("1z", "z").replace("1\\bar", "\\bar")
        l = ["តាង $z=x+iy$ ដែល $x,y\\in\\mathbb{R}$ នោះ $\\bar{z}=x-iy$ ។ ជំនួសចូលសមីការ ៖", dd(f"{p}(x+iy){'+' if q>0 else '-'}{abs(q)}(x-iy)={c.tex()}"), dd(f"{tsum([(p+q,'x')])}+({tsum([(p-q,'y')])})i={c.tex()}"),
             "ដោយផ្នែកពិតស្មើគ្នា និងផ្នែកនិមិត្តស្មើគ្នា ៖", dd(rf"\begin{{cases}}{tsum([(p+q,'x')])}={nt(c.a)}\\{tsum([(p-q,'y')])}={nt(c.b)}\end{{cases}}\Rightarrow\begin{{cases}}x={nt(z0.a)}\\y={nt(z0.b)}\end{{cases}}")]
        if p + q == 0: return
        ck = [(f"{p}*{z0.py()}+({q})*conjugate({z0.py()})", c.py(), "substitution")]
    elif t == "cplx":
        p = K(Z(0, 1), Z(0, 2), Z(1, 1), Z(2, 1), Z(1, -1), Z(0, -1)); q = K(2, 3, -2, 1, -1)
        c = p * z0 + q * z0.c()
        px = Z(p.a + q, -p.b * 0 + 0)  # coefficient bookkeeping below
        # p(x+iy)+q(x-iy): real = (p.a+q)x - p.b y ; imag = p.b x + (p.a-q) y
        r1, r2, r3, r4 = p.a + q, -p.b, p.b, p.a - q
        if r1 * r4 - r2 * r3 == 0: return
        e1, e2 = tsum([(r1, "x"), (r2, "y")]), tsum([(r3, "x"), (r4, "y")])
        E = f"{p.p()}z{'+' if q>0 else '-'}{'' if abs(q)==1 else abs(q)}\\bar{{z}}={c.tex()}"
        l = ["តាង $z=x+iy$ ដែល $x,y$ ជាចំនួនពិត ។ ពន្លាតអង្គខាងឆ្វេង ៖", dd(f"{p.p()}(x+iy){'+' if q>0 else '-'}{'' if abs(q)==1 else abs(q)}(x-iy)=({e1})+({e2})i"),
             "យើងបានប្រព័ន្ធសមីការ ៖", dd(rf"\begin{{cases}}{e1}={nt(c.a)}\\{e2}={nt(c.b)}\end{{cases}}"), f"ដោះស្រាយប្រព័ន្ធ ៖ $x={nt(z0.a)}$ និង $y={nt(z0.b)}$ ។"]
        ck = [(f"{p.py()}*{z0.py()}+({q})*conjugate({z0.py()})", c.py(), "substitution")]
    elif t == "mixz":
        k = K(1, 2, 3); c0 = z0 * z0.c()
        c = c0 + k * (z0 - z0.c())
        if z0.b == 0: return
        # z zbar + k(z-zbar) = c : x^2+y^2 + 2k y i ; multiple sols x=±
        a0 = abs(z0.a)
        E = f"z\\bar{{z}}+{'' if k==1 else k}(z-\\bar{{z}})={c.tex()}"
        l = ["តាង $z=x+iy$ ។ យើងមាន $z\\bar{z}=x^2+y^2$ និង $z-\\bar{z}=2iy$ ។ សមីការក្លាយជា ៖", dd(f"x^{{2}}+y^{{2}}+{2*k}yi={c.tex()}"), "ដោយផ្នែកពិតស្មើគ្នា និងផ្នែកនិមិត្តស្មើគ្នា ៖", dd(rf"\begin{{cases}}x^{{2}}+y^{{2}}={nt(c.a)}\\{2*k}y={nt(c.b)}\end{{cases}}"), f"នាំឱ្យ $y={nt(z0.b)}$ រួច $x^2={nt(c.a)}-{nt(z0.b**2)}={nt(a0**2)}$ ដូច្នេះ $x=\\pm{nt(a0)}$ ។"]
        z1, z2 = Z(a0, z0.b), Z(-a0, z0.b)
        ck = [(f"{r.py()}*conjugate({r.py()})+{k}*({r.py()}-conjugate({r.py()}))", c.py(), "substitution") for r in (z1, z2)]
        R("linear_equation_with_conjugate", "hard", S.replace("{E}", ll(E)), l + [f"ដូចនេះ សមីការមានឫសពីរគឺ $\\boxed{{z={z1.tex()}}}$ និង $\\boxed{{z={z2.tex()}}}$ ។"], f"z={z1.tex()},\\ z={z2.tex()}", ck, (t, E))
        return
    elif t == "zbar_only":
        a = G(-3, 3); b = G(-5, 5); c = a * z0.c() + b
        E = f"{a.p()}\\bar{{z}}+{b.p()}={c.tex()}"
        d = c - b
        l = ["យើងដោះស្រាយរក $\\bar{z}$ ជាមុន ៖", dd(f"{a.p()}\\bar{{z}}={d.tex()}"), dd(r"\bar{z}=" + chain(*div_chain(d, a))), f"$z$ គឺជាចំនួនកុំផ្លិចឆ្លាស់នៃ ${z0.c().tex()}$ ។"]
        ck = [(f"{a.py()}*conjugate({z0.py()})+{b.py()}", c.py(), "substitution")]
    else:
        w0 = G(-4, 4); a = K(1, 2, 3); c = Z(0, K(1, 2, -1))
        e1 = z0 + a * w0; e2 = c * z0 - w0
        den = -1 - a * c
        S2 = K("ដោះស្រាយប្រព័ន្ធសមីការ", "រកចំនួនកុំផ្លិច $z$ និង $w$ ដែលផ្ទៀងផ្ទាត់ប្រព័ន្ធសមីការ")
        lhs1 = f"z+{'' if a==1 else a}w"; lhs2 = f"{c.tex()}z-w"
        pr = f"{S2} ៖ $$\\begin{{cases}}{lhs1}={e1.tex()}\\\\{lhs2}={e2.tex()}\\end{{cases}}$$"
        comb = e1 + a * e2; co = 1 + a * c
        l = [f"គុណសមីការទីពីរនឹង ${a}$ រួចបូកនឹងសមីការទីមួយ ដើម្បីបំបាត់ $w$ ៖", dd(f"{co.p()}z={comb.tex()}"), dd("z=" + chain(*div_chain(comb, co))), f"ជំនួសចូលសមីការទីពីរ ៖ $w={c.tex()}z-({e2.tex()})={w0.tex()}$ ។"]
        if a == 1: l[0] = "បូកសមីការទាំងពីរ ដើម្បីបំបាត់ $w$ ៖"
        R("linear_system", "hard", pr, l + [f"ដូចនេះ $\\boxed{{z={z0.tex()}}}$ និង $\\boxed{{w={w0.tex()}}}$ ។"], f"z={z0.tex()},\\ w={w0.tex()}", [(f"{z0.py()}+{a}*{w0.py()}", e1.py(), "first"), (f"{c.py()}*{z0.py()}-{w0.py()}", e2.py(), "second")], (t, a, key(c), key(z0), key(w0)))
        return
    R("linear_equation_with_conjugate", "medium", S.replace("{E}", ll(E)), l + [f"ដូចនេះ $\\boxed{{z={z0.tex()}}}$ ។"], f"z={z0.tex()}", ck, (t, E))

# ---------- G. quadratic equations ----------
def g_quad_real():
    t = K("monic", "monic", "surd", "nonmonic", "even", "square")
    S = K(*SOLVEC)
    if t in ("monic", "even", "square"):
        p, q = rng.randint(-6, 6), rng.randint(1, 7)
        r1, r2 = Z(p, q), Z(p, -q); b, c = -2 * p, p * p + q * q
        E = ptex([1, b, c]) + "=0"
        if t == "monic":
            D = b * b - 4 * c
            l = [f"សមីការមានមេគុណ $a=1$ , $b={b}$ , $c={c}$ ។ គណនាឌីសគ្រីមីណង់ ៖", dd(f"\\Delta=b^{{2}}-4ac=" + chain(f"({b})^{{2}}-4\\times 1\\times {c}" if b < 0 else f"{b}^{{2}}-4\\times 1\\times {c}", str(D), f"({2*q}i)^{{2}}")),
                 "ដោយ $\\Delta<0$ សមីការមានឫសកុំផ្លិចពីរឆ្លាស់គ្នា ៖", dd(rf"z_1=\frac{{{-b}+{2*q}i}}{{2}}={r1.tex()}\quad,\quad z_2=\frac{{{-b}-{2*q}i}}{{2}}={r2.tex()}")]
        elif t == "even":
            if b == 0: return
            hb = b // 2; D = hb * hb - c
            l = [f"មេគុណ $b={b}$ ជាចំនួនគូ ដូច្នេះយើងប្រើ $b'={hb}$ ។", dd(f"\\Delta'=b'^{{2}}-ac=" + chain(f"({hb})^{{2}}-{c}", str(D), f"({q}i)^{{2}}".replace("(1i)", "i") if q != 1 else "i^{2}")),
                 "ឫសទាំងពីរគឺ ៖", dd(rf"z_1={-hb}+{'' if q==1 else q}i\quad,\quad z_2={-hb}-{'' if q==1 else q}i".replace("0+", "").replace("=0-", "=-"))]
        else:
            if b == 0: return
            l = ["យើងសរសេរជារាងកាណូនិក ៖", dd(f"{E}\\Leftrightarrow (z{'+' if -p>0 else '-'}{abs(p)})^{{2}}+{q*q}=0" if p else ""), dd(f"(z{'+' if -p>0 else '-'}{abs(p)})^{{2}}={-q*q}={q*q}i^{{2}}"), dd(rf"z{'+' if -p>0 else '-'}{abs(p)}={'' if q==1 else q}i\quad\text{{ឬ}}\quad z{'+' if -p>0 else '-'}{abs(p)}=-{'' if q==1 else q}i".replace("\\text{ឬ}", "\\vee"))]
        cks = [(pchk([1, b, c], r1), "0", "root"), (pchk([1, b, c], r2), "0", "root"), (f"{r1.py()}+{r2.py()}", str(-b), "sum of roots"), (f"{r1.py()}*{r2.py()}", str(c), "product of roots")]
        kk = (t, b, c)
    elif t == "surd":
        b, c = rng.randint(-5, 5), rng.randint(2, 14); D = b * b - 4 * c
        if D >= 0 or sp.sqrt(-D).is_integer: return
        s = sp.sqrt(-D); r1, r2 = Z(Q(-b, 2), s / 2), Z(Q(-b, 2), -s / 2)
        E = ptex([1, b, c]) + "=0"
        l = ["គណនាឌីសគ្រីមីណង់ ៖", dd(f"\\Delta=" + chain((f"({b})^{{2}}" if b < 0 else f"{b}^{{2}}") + f"-4\\times {c}", str(D), f"\\left(i{nt(s)}\\right)^{{2}}" if s.is_Pow else f"\\left({nt(s).split(chr(92))[0]}i\\sqrt{{{s.as_coeff_Mul()[1].args[0]}}}\\right)^{{2}}")),
             "ឫសទាំងពីរគឺ ៖", dd(rf"z_{{1,2}}=\frac{{{-b}\pm {Z(0,s).tex()}}}{{2}}")]
        cks = [(pchk([1, b, c], r1), "0", "root"), (pchk([1, b, c], r2), "0", "root")]; kk = (t, b, c)
    else:
        a = rng.randint(2, 5); d = K(1, 2, 3, 5); p = Q(rng.randint(-5, 5), a); q = Q(rng.randint(1, 5), a)
        b, c = -2 * a * p, a * (p * p + q * q)
        if not (b.is_integer and c.is_integer): return
        D = b * b - 4 * a * c; s = sp.sqrt(-D)
        r1, r2 = Z(p, q), Z(p, -q)
        E = ptex([a, b, c]) + "=0"
        l = ["គណនាឌីសគ្រីមីណង់ ៖", dd(f"\\Delta=" + chain((f"({b})^{{2}}" if b < 0 else f"{b}^{{2}}") + f"-4\\times {a}\\times {c}", str(D), f"({nt(s)}i)^{{2}}")), "ឫសទាំងពីរគឺ ៖", dd(rf"z_1=\frac{{{-b}+{nt(s)}i}}{{{2*a}}}={r1.tex()}\quad,\quad z_2=\frac{{{-b}-{nt(s)}i}}{{{2*a}}}={r2.tex()}")]
        cks = [(pchk([a, b, c], r1), "0", "root"), (pchk([a, b, c], r2), "0", "root")]; kk = (t, a, b, c)
    R("quadratic_real_coefficients", "easy" if t != "nonmonic" else "medium", S.replace("{E}", ll(E)), l + [K(f"ដូចនេះ សមីការមានឫស $\\boxed{{z_1={r1.tex()}}}$ និង $\\boxed{{z_2={r2.tex()}}}$ ។", f"ដូចនេះ សំណុំឫសគឺ $\\boxed{{\\left\\{{{r1.tex()}\\,;\\,{r2.tex()}\\right\\}}}}$ ។")], f"z_1={r1.tex()},\\ z_2={r2.tex()}", cks, kk)

def g_quad_complex():
    t = K("general", "general", "general", "pure", "imag_lead", "given_root")
    S = K(*SOLVEC)
    if t == "general":
        r1, r2 = G(-4, 4, False), G(-4, 4, False)
        d = r1 - r2
        if d.a == 0 or d.b == 0 or abs(d.a) == abs(d.b) or r1 == r2: return
        if (r1 + r2).b == 0 and (r1 * r2).b == 0: return
        if d.a < 0: r1, r2 = r2, r1; d = -d
        s, p = r1 + r2, r1 * r2; D = d * d
        cs = [1, -s, p]; E = ptex(cs) + "=0"
        sq = s * s
        l = ["ឌីសគ្រីមីណង់នៃសមីការគឺ ៖", dd(chain(f"\\Delta=b^{{2}}-4ac", f"{s.p()}^{{2}}-4{p.p()}", f"{sq.p()}-{(4*p).p()}", D.tex())), f"យើងត្រូវរកឫសការេនៃ $\\Delta={D.tex()}$ ។"]
        l += sqrt_lines(D, d, "\\delta", "$\\Delta$")
        l += [f"យក $\\delta={d.tex()}$ ។ ឫសទាំងពីរគឺ ៖", dd(rf"z_1=\frac{{{s.p()}+{d.p()}}}{{2}}={r1.tex()}\quad,\quad z_2=\frac{{{s.p()}-{d.p()}}}{{2}}={r2.tex()}")]
        cks = [(pchk(cs, r1), "0", "root"), (pchk(cs, r2), "0", "root"), (f"expand({d.py()}**2)", f"expand(({s.py()})**2-4*{p.py()})", "delta")]
        R("quadratic_complex_coefficients", "hard", S.replace("{E}", ll(E)), l + [f"ដូចនេះ $\\boxed{{z_1={r1.tex()}}}$ និង $\\boxed{{z_2={r2.tex()}}}$ ។"], f"z_1={r1.tex()},\\ z_2={r2.tex()}", cks, (t, E))
    elif t == "pure":
        r = G(-5, 5); w = r * r; b = G(-3, 3)  # (z+b)^2 = w
        if r.a < 0 or abs(r.a) == abs(r.b): return
        E = f"(z+{b.p()})^{{2}}={w.tex()}"
        r1, r2 = r - b, -r - b
        l = [f"តាង $Z=z+{b.p()}$ ។ សមីការក្លាយជា $Z^2={w.tex()}$ ។ យើងរកឫសការេនៃ ${w.tex()}$ ៖"] + sqrt_lines(w, r, "Z") + [f"នាំឱ្យ $Z={r.tex()}$ ឬ $Z={(-r).tex()}$ ។", "ត្រឡប់ទៅ $z$ វិញ ៖", dd(f"z_1={r.p()}-{b.p()}={r1.tex()}\\quad,\\quad z_2={(-r).p()}-{b.p()}={r2.tex()}")]
        cks = [(f"expand(({r1.py()}+{b.py()})**2)", w.py(), "root"), (f"expand(({r2.py()}+{b.py()})**2)", w.py(), "root")]
        R("quadratic_complex_coefficients", "hard", S.replace("{E}", ll(E)), l + [f"ដូចនេះ $\\boxed{{z_1={r1.tex()}}}$ និង $\\boxed{{z_2={r2.tex()}}}$ ។"], f"z_1={r1.tex()},\\ z_2={r2.tex()}", cks, (t, E))
    elif t == "imag_lead":
        # Delta a perfect imaginary or real square: z^2 - s z + p with r1-r2 pure real or pure imaginary
        r1 = G(-4, 4); k = K(1, 2, 3, 4, 5, 6); typ = K("re", "im")
        r2 = r1 - (Z(k, 0) if typ == "re" else Z(0, k))
        s, p = r1 + r2, r1 * r2; cs = [1, -s, p]; E = ptex(cs) + "=0"; d = r1 - r2; D = d * d
        l = [dd(chain(f"\\Delta={s.p()}^{{2}}-4{p.p()}", f"{(s*s).p()}-{(4*p).p()}", D.tex())),
             (f"ដោយ $\\Delta={D.tex()}={d.p()}^{{2}}$ ដែលជាការេប្រាកដ យើងបាន ៖"), dd(rf"z_1=\frac{{{s.p()}+{d.p()}}}{{2}}={r1.tex()}\quad,\quad z_2=\frac{{{s.p()}-{d.p()}}}{{2}}={r2.tex()}")]
        cks = [(pchk(cs, r1), "0", "root"), (pchk(cs, r2), "0", "root")]
        R("quadratic_complex_coefficients", "medium", S.replace("{E}", ll(E)), l + [f"ដូចនេះ សមីការមានឫស $\\boxed{{{r1.tex()}}}$ និង $\\boxed{{{r2.tex()}}}$ ។"], f"z_1={r1.tex()},\\ z_2={r2.tex()}", cks, (t, E))
    else:
        r1, r2 = K(Z(0, 1), Z(1, 0), Z(0, -1), Z(0, 2), Z(2, 0), Z(1, 1), Z(-1, 0), Z(0, -2)), G(-4, 4)
        if r1 == r2: return
        s, p = r1 + r2, r1 * r2; cs = [1, -s, p]; E = ptex(cs) + "=0"
        pr = f"គេឱ្យសមីការ ${E}$ ។ បង្ហាញថា $z_1={r1.tex()}$ ជាឫសរបស់សមីការនេះ រួចទាញរកឫសមួយទៀត $z_2$ ។"
        sq = r1 * r1
        l = [f"ជំនួស $z={r1.tex()}$ ក្នុងអង្គខាងឆ្វេង ៖", dd(chain(f"{r1.p()}^{{2}}-{s.p()}{r1.p()}+{p.p()}", f"{sq.p()}-{(s*r1).p()}+{p.p()}", "0")), f"ដូច្នេះ $z_1={r1.tex()}$ ជាឫស ។",
             "ផលគុណឫសនៃសមីការ $z^2+bz+c=0$ គឺ $z_1z_2=c$ ។ យើងបាន ៖", dd(f"z_2=" + chain(rf"\frac{{{p.tex()}}}{{{r1.tex()}}}", r2.tex()))]
        cks = [(pchk(cs, r1), "0", "given root"), (pchk(cs, r2), "0", "other root"), (f"{r1.py()}+{r2.py()}", s.py(), "sum")]
        R("quadratic_complex_coefficients", "medium", pr, l + [f"ដូចនេះ ឫសមួយទៀតគឺ $\\boxed{{z_2={r2.tex()}}}$ ។"], f"z_2={r2.tex()}", cks, (t, E))

def g_biquad():
    t = K("two_neg", "one_pos", "ipair")
    S = K(*SOLVEC)
    if t == "two_neg":
        a, b = rng.sample(range(1, 11), 2); a, b = min(a, b), max(a, b)
        cs = [1, 0, a + b, 0, a * b]; E = ptex(cs) + "=0"
        ra, rb = Z(0, RT(a)), Z(0, RT(b))
        l = ["តាង $t=z^2$ ។ សមីការក្លាយជា ៖", dd(ptex([1, a + b, a * b], "t") + f"=0\\Leftrightarrow (t+{a})(t+{b})=0"), f"នាំឱ្យ $t={-a}$ ឬ $t={-b}$ ។", dd(f"z^{{2}}={-a}\\Rightarrow z=\\pm {ra.tex()}"), dd(f"z^{{2}}={-b}\\Rightarrow z=\\pm {rb.tex()}")]
        roots = [ra, -ra, rb, -rb]; kk = (t, a, b)
    elif t == "one_pos":
        a, b = rng.randint(1, 8), rng.randint(1, 10)
        cs = [1, 0, b - a * a, 0, -a * a * b]; E = ptex(cs) + "=0"
        rb = Z(0, RT(b))
        l = ["តាង $t=z^2$ យើងបាន ៖", dd(ptex([1, b - a * a, -a * a * b], "t") + f"=0\\Leftrightarrow (t-{a*a})(t+{b})=0"), dd(f"z^{{2}}={a*a}\\Rightarrow z=\\pm {a}"), dd(f"z^{{2}}={-b}\\Rightarrow z=\\pm {rb.tex()}")]
        roots = [Z(a), Z(-a), rb, -rb]; kk = (t, a, b)
    else:
        a = K(1, 2, 3, 4, 5); e = 4 * a ** 4
        # z^4 + 4a^4 = (z^2+2a z+2a^2)(z^2-2a z+2a^2)
        cs = [1, 0, 0, 0, e]; E = ptex(cs) + "=0"
        r = [Z(a, a), Z(a, -a), Z(-a, a), Z(-a, -a)]
        l = [f"ដោយ $z^4={-e}$ យើងរកឃើញ $z^2=\\pm {2*a*a}i$ ព្រោះ $({2*a*a}i)^{{2}}={-e}$ ។", f"ករណី $z^2={2*a*a}i$ ៖ ដោយ $({a}+{a}i)^{{2}}={2*a*a}i$ នោះ $z=\\pm({a}+{a}i)$ ។", f"ករណី $z^2=-{2*a*a}i$ ៖ ដោយ $({a}-{a}i)^{{2}}=-{2*a*a}i$ នោះ $z=\\pm({a}-{a}i)$ ។"]
        l = [x_.replace("(1+1i)", "(1+i)").replace("(1-1i)", "(1-i)") for x_ in l]
        roots = r; kk = (t, a)
    txt = " , ".join(rt.tex() for rt in roots)
    R("biquadratic_equation", "medium", S.replace("{E}", ll(E)), l + [f"ដូចនេះ សមីការមានឫសបួនគឺ $\\boxed{{{txt}}}$ ។"], txt, [(pchk(cs, r_), "0", "root") for r_ in roots], kk)

def g_vieta():
    t = K("sumsq", "inv", "ratio", "cube", "mods")
    p, q = rng.randint(-4, 4), rng.randint(1, 5)
    b, c = -2 * p, p * p + q * q
    r1, r2 = Z(p, q), Z(p, -q)
    E = ptex([1, b, c]) + "=0"
    s, pr_ = -b, c
    head = K(f"គេឱ្យ $z_1$ និង $z_2$ ជាឫសនៃសមីការ ${E}$ ។", f"តាង $z_1$ , $z_2$ ជាឫសរបស់សមីការ ${E}$ ក្នុង $\\mathbb{{C}}$ ។")
    pre = ["ដោយមិនចាំបាច់រកឫស យើងប្រើផលបូកឫស និងផលគុណឫសនៃសមីការដឺក្រេទីពីរ ៖", dd(f"z_1+z_2={s}\\quad,\\quad z_1z_2={pr_}")]
    if t == "sumsq":
        r = s * s - 2 * pr_
        l = pre + [dd(chain("z_1^{2}+z_2^{2}", "(z_1+z_2)^{2}-2z_1z_2", f"({s})^{{2}}-2\\times {pr_}", str(r)))]
        R("sum_product_of_roots", "medium", head + " ដោយមិនដោះស្រាយសមីការ គណនា $z_1^2+z_2^2$ ។", l + [f"ដូចនេះ $\\boxed{{z_1^2+z_2^2={r}}}$ ។"], str(r), [(f"expand({r1.py()}**2+{r2.py()}**2)", str(r), "value")], (t, b, c))
    elif t == "inv":
        r = Q(s, pr_)
        l = pre + [dd(chain(r"\frac{1}{z_1}+\frac{1}{z_2}", r"\frac{z_1+z_2}{z_1z_2}", rf"\frac{{{s}}}{{{pr_}}}", nt(r)))]
        R("sum_product_of_roots", "medium", head + " គណនា $\\frac{1}{z_1}+\\frac{1}{z_2}$ ។", l + [f"ដូចនេះ $\\boxed{{\\frac{{1}}{{z_1}}+\\frac{{1}}{{z_2}}={nt(r)}}}$ ។"], nt(r), [(f"1/{r1.py()}+1/{r2.py()}", str(r), "value")], (t, b, c))
    elif t == "ratio":
        r = Q(s * s - 2 * pr_, pr_)
        l = pre + [dd(chain(r"\frac{z_1}{z_2}+\frac{z_2}{z_1}", r"\frac{z_1^{2}+z_2^{2}}{z_1z_2}", r"\frac{(z_1+z_2)^{2}-2z_1z_2}{z_1z_2}", rf"\frac{{{s*s-2*pr_}}}{{{pr_}}}", nt(r)))]
        R("sum_product_of_roots", "hard", head + " គណនា $\\frac{z_1}{z_2}+\\frac{z_2}{z_1}$ ។", l + [f"ដូចនេះ $\\boxed{{\\frac{{z_1}}{{z_2}}+\\frac{{z_2}}{{z_1}}={nt(r)}}}$ ។"], nt(r), [(f"{r1.py()}/{r2.py()}+{r2.py()}/{r1.py()}", str(r), "value")], (t, b, c))
    elif t == "cube":
        r = s ** 3 - 3 * s * pr_
        l = pre + [dd(chain("z_1^{3}+z_2^{3}", "(z_1+z_2)^{3}-3z_1z_2(z_1+z_2)", f"({s})^{{3}}-3\\times {pr_}\\times ({s})", str(r)))]
        R("sum_product_of_roots", "hard", head + " គណនា $z_1^3+z_2^3$ ។", l + [f"ដូចនេះ $\\boxed{{z_1^3+z_2^3={r}}}$ ។"], str(r), [(f"expand({r1.py()}**3+{r2.py()}**3)", str(r), "value")], (t, b, c))
    else:
        m_ = sp.sqrt(c)
        l = ["សមីការមានមេគុណពិត និង $\\Delta<0$ ដូច្នេះឫសទាំងពីរឆ្លាស់គ្នា គឺ $z_2=\\overline{z_1}$ ។", f"នាំឱ្យ $z_1z_2=z_1\\overline{{z_1}}=|z_1|^2={c}$ ។", dd(f"|z_1|=|z_2|={nt(m_)}")]
        R("sum_product_of_roots", "medium", head + " ដោយមិនគណនាឫស រកម៉ូឌុលនៃឫសទាំងពីរ ។", l + [f"ដូចនេះ $\\boxed{{|z_1|=|z_2|={nt(m_)}}}$ ។"], nt(m_), [(f"Abs({r1.py()})", str(m_), "modulus"), (f"Abs({r2.py()})", str(m_), "modulus")], (t, b, c))

def g_build_quad():
    t = K("from_root", "from_roots", "find_ab", "find_ab2")
    r = G(-6, 6)
    if t == "from_root":
        b, c = -2 * r.a, r.n2(); E = ptex([1, b, c])
        pr = K(f"រកសមីការដឺក្រេទីពីរមានមេគុណពិត ដែលមានឫសមួយគឺ ${r.tex()}$ ។", f"បង្កើតសមីការដឺក្រេទីពីរ $z^2+bz+c=0$ ដែល $b,c\\in\\mathbb{{R}}$ ហើយមានឫស $z_1={r.tex()}$ ។")
        l = [f"ដោយមេគុណជាចំនួនពិត ឫសមួយទៀតគឺចំនួនកុំផ្លិចឆ្លាស់ $z_2={r.c().tex()}$ ។", dd(f"z_1+z_2={nt(2*r.a)}\\quad,\\quad z_1z_2={nt(r.a**2)}+{nt(r.b**2)}={nt(c)}"), "សមីការគឺ $z^2-(z_1+z_2)z+z_1z_2=0$ ។"]
        R("build_equation_from_roots", "medium", pr, l + [f"ដូចនេះ សមីការដែលរកបានគឺ $\\boxed{{{E}=0}}$ ។"], E + "=0", [(pchk([1, b, c], r), "0", "root"), (pchk([1, b, c], r.c()), "0", "conjugate root")], (t, key(r)))
    elif t == "from_roots":
        a, b2 = G(-4, 4), G(-4, 4)
        if a == b2: return
        s, p = a + b2, a * b2; cs = [1, -s, p]; E = ptex(cs)
        pr = K(f"រកសមីការដឺក្រេទីពីរដែលមានឫស $z_1={a.tex()}$ និង $z_2={b2.tex()}$ ។", f"សរសេរសមីការរាង $z^2+bz+c=0$ ដែលមានឫសពីរគឺ ${a.tex()}$ និង ${b2.tex()}$ ។")
        l = ["គណនាផលបូក និងផលគុណនៃឫស ៖", dd(f"z_1+z_2={s.tex()}"), dd("z_1z_2=" + chain(f"{a.p()}{b2.p()}", *mul_chain(a, b2))), "សមីការមានរាង $z^2-(z_1+z_2)z+z_1z_2=0$ ។"]
        R("build_equation_from_roots", "medium", pr, l + [f"ដូចនេះ $\\boxed{{{E}=0}}$ ។"], E + "=0", [(pchk(cs, a), "0", "root"), (pchk(cs, b2), "0", "root")], (t, key(a), key(b2)))
    elif t == "find_ab":
        b, c = -2 * r.a, r.n2(); E = "z^{2}+az+b=0"; sq = r * r
        pr = K(f"រកចំនួនពិត $a$ និង $b$ ដោយដឹងថា ${r.tex()}$ ជាឫសនៃសមីការ ${E}$ ។", f"គេដឹងថា $z_0={r.tex()}$ ជាឫសរបស់សមីការ ${E}$ ដែល $a,b\\in\\mathbb{{R}}$ ។ កំណត់ $a$ និង $b$ ។")
        l = [f"ជំនួស $z={r.tex()}$ ក្នុងសមីការ ៖", dd(f"{r.p()}^{{2}}+a{r.p()}+b=0"), dd(f"{sq.p()}+a{r.p()}+b=0"), dd(f"({tsum([(sq.a,''),(r.a,'a'),(1,'b')])})+({tsum([(sq.b,''),(r.b,'a')])})i=0"), "ចំនួនកុំផ្លិចស្មើសូន្យ លុះត្រាតែផ្នែកពិត និងផ្នែកនិមិត្តស្មើសូន្យ ៖", dd(rf"\begin{{cases}}{tsum([(sq.a,''),(r.a,'a'),(1,'b')])}=0\\{tsum([(sq.b,''),(r.b,'a')])}=0\end{{cases}}"), f"សមីការទីពីរឱ្យ $a={nt(b)}$ ។ ជំនួសក្នុងសមីការទីមួយ យើងបាន $b={nt(c)}$ ។"]
        R("find_coefficients_from_root", "medium", pr, l + [f"ដូចនេះ $\\boxed{{a={nt(b)},\\ b={nt(c)}}}$ ។"], f"a={nt(b)},\\ b={nt(c)}", [(pchk([1, b, c], r), "0", "substitution")], (t, key(r)))
    else:
        lead = K(2, 3); b, c = -2 * r.a * lead, r.n2() * lead
        E = f"{lead}z^{{2}}+mz+n=0"
        pr = f"រកចំនួនពិត $m$ និង $n$ ដែលសមីការ ${E}$ មានឫសមួយគឺ ${r.tex()}$ ។"
        l = [f"ដោយ $m,n$ ជាចំនួនពិត ឫសមួយទៀតគឺ ${r.c().tex()}$ ។ ផលបូកឫសស្មើ $-\\frac{{m}}{{{lead}}}$ ហើយផលគុណឫសស្មើ $\\frac{{n}}{{{lead}}}$ ។", dd(rf"-\frac{{m}}{{{lead}}}={nt(2*r.a)}\Rightarrow m={nt(b)}"), dd(rf"\frac{{n}}{{{lead}}}={nt(r.n2())}\Rightarrow n={nt(c)}")]
        R("find_coefficients_from_root", "medium", pr, l + [f"ដូចនេះ $\\boxed{{m={nt(b)},\\ n={nt(c)}}}$ ។"], f"m={nt(b)},\\ n={nt(c)}", [(pchk([lead, b, c], r), "0", "root"), (pchk([lead, b, c], r.c()), "0", "root")], (t, key(r), lead))

# ---------- H. polynomial equations with a given root ----------
def factor_tex(lin, quad):
    return f"({lin})({quad})"
def g_cubic_real():
    t = K("given_complex", "given_real", "find_coef", "show_root")
    p, q = rng.randint(-3, 3), rng.randint(1, 4)
    a0 = rng.randint(-4, 4)
    if a0 == 0: a0 = 2
    r = Z(p, q); qd = [1, -2 * p, p * p + q * q]
    cs = [int(c_.a) for c_ in pmul([1, -a0], qd)]
    Pt = ptex(cs); lin = f"z{tsum([(-a0,'')]) if a0>0 else '+'+nt(-a0)}"; qt = ptex(qd)
    roots = [Z(a0), r, r.c()]
    if t == "given_complex":
        pr = K(f"គេឱ្យពហុធា $P(z)={Pt}$ ។ ដោយដឹងថា $z_0={r.tex()}$ ជាឫសនៃ $P(z)=0$ ដោះស្រាយសមីការ $P(z)=0$ ក្នុង $\\mathbb{{C}}$ ។",
               f"ដោះស្រាយសមីការ ${Pt}=0$ ក្នុងសំណុំចំនួនកុំផ្លិច ដោយដឹងថា ${r.tex()}$ ជាឫសមួយរបស់វា ។")
        l = [f"ដោយមេគុណជាចំនួនពិត ហើយ ${r.tex()}$ ជាឫស នោះ ${r.c().tex()}$ ក៏ជាឫសដែរ ។", "ពហុធាចែកដាច់នឹង ៖", dd(f"(z-{r.p()})(z-{r.c().p()})={qt}"), f"ចែកពហុធា ឬផ្ទឹមមេគុណ យើងបាន ៖".replace("ឬផ្ទឹមមេគុណ ", ""), dd(f"{Pt}=({lin})({qt})"), f"ឫសទីបីគឺ $z={a0}$ ។"]
        ck = [(pchk(cs, x_), "0", "root") for x_ in roots] + [(f"expand(({pxstr([1,-a0])})*({pxstr(qd)}))", f"expand({pxstr(cs)})", "factorisation")]
        R("polynomial_given_root", "hard", pr, l + [f"ដូចនេះ សំណុំឫសគឺ $\\boxed{{\\left\\{{{a0}\\,;\\,{r.tex()}\\,;\\,{r.c().tex()}\\right\\}}}}$ ។"], f"{a0},\\ {r.tex()},\\ {r.c().tex()}", ck, (t, a0, p, q))
    elif t == "given_real":
        if p == 0 and K(0, 1): return
        val = "0"
        pr = K(f"គេឱ្យ $P(z)={Pt}$ ។ គណនា $P({a0})$ រួចដាក់ $P(z)$ ជាកត្តា ហើយដោះស្រាយ $P(z)=0$ ។", f"បង្ហាញថា ${a0}$ ជាឫសនៃសមីការ ${Pt}=0$ រួចរកឫសទាំងអស់ក្នុង $\\mathbb{{C}}$ ។")
        n = len(cs) - 1
        sub = "+".join(f"({nt(c_)})\\times ({a0})^{{{n-k_}}}" if n - k_ > 0 else f"({nt(c_)})" for k_, c_ in enumerate(cs))
        D = qd[1] ** 2 - 4 * qd[2]
        l = [("" if "P(z)" in pr else f"តាង $P(z)={Pt}$ ។ ") + f"ជំនួស $z={a0}$ ៖ ${cs[0]*a0**3:+d}{cs[1]*a0**2:+d}{cs[2]*a0:+d}{cs[3]:+d}=0$ ។ ដូច្នេះ $z={a0}$ ជាឫស ហើយ $P(z)$ ចែកដាច់នឹង ${lin}$ ។".replace("=$", "=$"),
             "ចែកពហុធា យើងបាន ៖", dd(f"P(z)=({lin})({qt})"), f"ដោះស្រាយ ${qt}=0$ ៖ $\\Delta={D}=({2*q}i)^{{2}}$ នាំឱ្យ $z={r.tex()}$ ឬ $z={r.c().tex()}$ ។"]
        l[0] = l[0].replace("$+", "$")
        ck = [(pchk(cs, x_), "0", "root") for x_ in roots] + [(f"expand(({pxstr([1,-a0])})*({pxstr(qd)}))", f"expand({pxstr(cs)})", "factorisation")]
        R("polynomial_given_root", "medium", pr, l + [f"ដូចនេះ ឫសទាំងបីគឺ $\\boxed{{z_1={a0}}}$ , $\\boxed{{z_2={r.tex()}}}$ និង $\\boxed{{z_3={r.c().tex()}}}$ ។"], f"{a0},\\ {r.tex()},\\ {r.c().tex()}", ck, (t, a0, p, q))
    elif t == "find_coef":
        c2, c1, c0 = cs[1], cs[2], cs[3]
        Pm = f"z^{{3}}{tsum([(c2,'z^{2}')]) if c2<0 else '+'+tsum([(c2,'z^{2}')]) if c2>0 else ''}+az+b"
        s2, s3 = r * r, r * r * r
        ee = s3 + c2 * s2
        pr = f"គេឱ្យ $P(z)={Pm}$ ដែល $a,b\\in\\mathbb{{R}}$ ។ រក $a$ និង $b$ ដោយដឹងថា $P({r.tex()})=0$ រួចរកឫសទាំងអស់នៃ $P(z)=0$ ។"
        l = [f"យើងគណនា $({r.tex()})^{{2}}={s2.tex()}$ និង $({r.tex()})^{{3}}={s3.tex()}$ ។", "ជំនួសចូល $P$ ៖", dd(f"{s3.p()}{'+' if c2>=0 else '-'}{mm(abs(c2),s2.p())}+a{r.p()}+b=0"), dd(f"({tsum([(ee.a,''),(r.a,'a'),(1,'b')])})+({tsum([(ee.b,''),(r.b,'a')])})i=0"),
             "ផ្នែកពិត និងផ្នែកនិមិត្តស្មើសូន្យ ៖", dd(rf"\begin{{cases}}{tsum([(ee.a,''),(r.a,'a'),(1,'b')])}=0\\{tsum([(ee.b,''),(r.b,'a')])}=0\end{{cases}}\Rightarrow\begin{{cases}}a={nt(c1)}\\b={nt(c0)}\end{{cases}}"),
             "ពេលនោះ ៖", dd(f"P(z)=({lin})({qt})"), f"ឫសរបស់ $P(z)=0$ គឺ ${a0}$ , ${r.tex()}$ និង ${r.c().tex()}$ ។"]
        if c2 == 0: return
        ck = [(pchk(cs, x_), "0", "root") for x_ in roots]
        R("polynomial_find_coefficients", "hard", pr, l + [f"ដូចនេះ $\\boxed{{a={nt(c1)},\\ b={nt(c0)}}}$ ហើយឫសទាំងបីគឺ ${a0}$ , ${r.tex()}$ , ${r.c().tex()}$ ។"], f"a={nt(c1)},\\ b={nt(c0)}", ck, (t, a0, p, q))
    else:
        s2, s3 = r * r, r * r * r
        pr = f"ផ្ទៀងផ្ទាត់ថា $z_0={r.tex()}$ ជាឫសនៃសមីការ ${Pt}=0$ ។"
        terms = f"{s3.p()}{'+' if cs[1]>=0 else '-'}{mm(abs(cs[1]),s2.p())}{'+' if cs[2]>=0 else '-'}{mm(abs(cs[2]),r.p())}{'+' if cs[3]>=0 else '-'}{abs(cs[3])}"
        l = [f"យើងគណនាស្វ័យគុណនៃ $z_0$ ៖ $z_0^2={s2.tex()}$ និង $z_0^3={s3.tex()}$ ។", "ជំនួសក្នុងអង្គខាងឆ្វេង ៖", dd(chain(terms, "0"))]
        R("polynomial_given_root", "easy", pr, l + [f"ដូចនេះ $\\boxed{{z_0={r.tex()}}}$ ជាឫសនៃសមីការនេះ ។"], f"P({r.tex()})=0", [(pchk(cs, r), "0", "substitution")], (t, a0, p, q))

def g_cubic_complex():
    t = K("imag_root", "real_root", "given_c")
    if t == "imag_root":
        y0 = K(1, 2, 3, -1, -2); r = Z(0, y0)
        s, p = G(-3, 3), G(-4, 4)
        qd = [Z(1), s, p]
        cs = pmul([Z(1), -r], qd)
        Pt = ptex(cs)
        # need P(iy) real and imag parts: find
        if any(c_.b == 0 for c_ in cs[1:]) : return
        A = peval(cs, Z(0, sp.Symbol("y", real=True)))
        pr = f"គេឱ្យសមីការ ${Pt}=0$ ។ បង្ហាញថាសមីការនេះមានឫសជាចំនួននិមិត្តមួយ រួចរកឫសនោះ ។"
        y = sp.Symbol("y", real=True)
        ra = sp.Poly(A.a, y); ia = sp.Poly(A.b, y)
        g = sp.gcd(ra, ia)
        if g.degree() != 1: return
        ra_t = nt(ra.as_expr()); ia_t = nt(ia.as_expr())
        l = ["តាង $z=iy$ ដែល $y\\in\\mathbb{R}$ ជាឫស ។ ជំនួសចូលសមីការ ហើយបំបែកផ្នែកពិត និងផ្នែកនិមិត្ត ៖", dd(f"({ra_t})+({ia_t})i=0"), "នាំឱ្យ ៖", dd(rf"\begin{{cases}}{ra_t}=0\\{ia_t}=0\end{{cases}}"), f"ឫសរួមនៃសមីការទាំងពីរគឺ $y={y0}$ ។ ពិនិត្យ ៖ វាផ្ទៀងផ្ទាត់សមីការទាំងពីរ ។"]
        R("polynomial_imaginary_or_real_root", "hard", pr, l + [f"ដូចនេះ ឫសនិមិត្តគឺ $\\boxed{{z={r.tex()}}}$ ។"], f"z={r.tex()}", [(pchk(cs, r), "0", "substitution")], (t, key(s), key(p), y0))
    elif t == "real_root":
        x0 = K(1, 2, 3, -1, -2, -3); s, p = G(-3, 3), G(-4, 4)
        qd = [Z(1), s, p]; cs = pmul([Z(1), Z(-x0)], qd)
        if any(c_.b == 0 for c_ in cs[1:]): return
        y = sp.Symbol("t", real=True)
        A = peval(cs, Z(y, 0)); ra = sp.Poly(A.a, y); ia = sp.Poly(A.b, y)
        g = sp.gcd(ra, ia)
        if g.degree() != 1: return
        Pt = ptex(cs); ra_t, ia_t = nt(ra.as_expr()), nt(ia.as_expr())
        ot = None
        D = s * s - 4 * p
        pr = f"គេឱ្យសមីការ ${Pt}=0$ ។ រកឫសជាចំនួនពិតនៃសមីការនេះ ។"
        l = ["តាង $t$ ជាឫសពិត ។ ជំនួស $z=t$ ហើយបំបែកផ្នែកពិត និងផ្នែកនិមិត្ត ៖", dd(f"({ra_t})+({ia_t})i=0"), "ដោយ $t$ ជាចំនួនពិត យើងបាន ៖", dd(rf"\begin{{cases}}{ra_t}=0\\{ia_t}=0\end{{cases}}"), f"ចម្លើយរួមនៃសមីការទាំងពីរគឺ $t={x0}$ ។"]
        R("polynomial_imaginary_or_real_root", "hard", pr, l + [f"ដូចនេះ ឫសពិតនៃសមីការគឺ $\\boxed{{z={x0}}}$ ។"], f"z={x0}", [(pchk(cs, Z(x0)), "0", "substitution")], (t, key(s), key(p), x0))
    else:
        r1 = K(Z(0, 1), Z(1, 0), Z(0, -1), Z(2, 0), Z(0, 2), Z(-1, 0)); r2, r3 = G(-3, 3), G(-3, 3)
        d = r2 - r3
        if r2 == r3 or d.a == 0 or d.b == 0 or abs(d.a) == abs(d.b) or r1 == r2 or r1 == r3: return
        if d.a < 0: r2, r3 = r3, r2; d = -d
        s, p = r2 + r3, r2 * r3
        qd = [Z(1), -s, p]; cs = pmul([Z(1), -r1], qd)
        Pt = ptex(cs); qt = ptex(qd); lin = f"z{'-' if not (-r1).tex().startswith('-') and False else ''}" + ("+" + (-r1).tex() if not (-r1).tex().startswith("-") else (-r1).tex())
        D = d * d
        pr = f"គេឱ្យ $P(z)={Pt}$ ។\n១. បង្ហាញថា $P({r1.tex()})=0$ ។\n២. កំណត់ពហុធា $Q(z)$ ដែល $P(z)=({lin})Q(z)$ ។\n៣. ដោះស្រាយសមីការ $P(z)=0$ ក្នុង $\\mathbb{{C}}$ ។"
        l = ["១. ជំនួស ៖", dd(chain(f"P({r1.tex()})", "0")), f"ដូចនេះ $\\boxed{{P({r1.tex()})=0}}$ ។", "២. ចែក $P(z)$ នឹង " + f"${lin}$ យើងបាន ៖", dd(f"Q(z)={qt}"), f"ដូចនេះ $\\boxed{{Q(z)={qt}}}$ ។", "៣. ដោះស្រាយ $Q(z)=0$ ។ ឌីសគ្រីមីណង់ ៖", dd(f"\\Delta={s.p()}^{{2}}-4{p.p()}={D.tex()}={d.p()}^{{2}}"), dd(rf"z=\frac{{{s.p()}\pm{d.p()}}}{{2}}"), f"គេបាន $z={r2.tex()}$ ឬ $z={r3.tex()}$ ។", f"ដូចនេះ ឫសទាំងបីគឺ $\\boxed{{{r1.tex()}}}$ , $\\boxed{{{r2.tex()}}}$ និង $\\boxed{{{r3.tex()}}}$ ។"]
        ck = [(pchk(cs, r_), "0", "root") for r_ in (r1, r2, r3)] + [(f"expand(({d.py()})**2)", f"expand(({s.py()})**2-4*{p.py()})", "delta")]
        R("polynomial_given_root", "bacii", pr, l, f"{r1.tex()},\\ {r2.tex()},\\ {r3.tex()}", ck, (t, key(r1), key(r2), key(r3)))

def g_quartic():
    p, q = rng.randint(-2, 2), rng.randint(1, 3); u, v = rng.randint(-2, 3), rng.randint(1, 3)
    if (p, q) == (u, v): return
    r, s = Z(p, q), Z(u, v)
    q1, q2 = [1, -2 * p, p * p + q * q], [1, -2 * u, u * u + v * v]
    cs = [int(c_.a) for c_ in pmul(q1, q2)]
    Pt = ptex(cs)
    pr = K(f"ដោះស្រាយសមីការ ${Pt}=0$ ក្នុង $\\mathbb{{C}}$ ដោយដឹងថា ${r.tex()}$ ជាឫសមួយ ។", f"គេឱ្យ $P(z)={Pt}$ ។ បង្ហាញថា $P({r.tex()})=0$ ។ ដាក់ $P(z)$ ជាផលគុណនៃពហុធាដឺក្រេទីពីរមានមេគុណពិតពីរ រួចដោះស្រាយ $P(z)=0$ ។")
    D = q2[1] ** 2 - 4 * q2[2]
    l = [("" if "P(z)" in pr else f"តាង $P(z)={Pt}$ ។ ") + f"ដោយមេគុណជាចំនួនពិត ${r.c().tex()}$ ក៏ជាឫសដែរ ។ ដូច្នេះ $P(z)$ ចែកដាច់នឹង ៖", dd(f"(z-{r.p()})(z-{r.c().p()})={ptex(q1)}"), "ធ្វើវិធីចែកពហុធា យើងបាន ៖", dd(f"{Pt}=({ptex(q1)})({ptex(q2)})"), f"សមីការ ${ptex(q2)}=0$ មាន $\\Delta={D}=({2*v}i)^{{2}}$ នាំឱ្យ $z={s.tex()}$ ឬ $z={s.c().tex()}$ ។"]
    rs = [r, r.c(), s, s.c()]
    txt = " , ".join(x_.tex() for x_ in rs)
    R("polynomial_given_root", "hard", pr, l + [f"ដូចនេះ ឫសទាំងបួនគឺ $\\boxed{{{txt}}}$ ។"], txt, [(pchk(cs, x_), "0", "root") for x_ in rs] + [(f"expand(({pxstr(q1)})*({pxstr(q2)}))", f"expand({pxstr(cs)})", "factorisation")], (p, q, u, v))

# ---------- I. modulus and conjugate conditions ----------
def g_conditions():
    t = K("z_plus_mod", "mod_param", "eqdist", "z2bar", "real_cond", "z_times", "mod_pair")
    if t == "z_plus_mod":
        a, b = K(*TRIP[:12]); a *= rsg(); b *= rsg(); k = K(1, 2, 3)
        m_ = sp.sqrt(a * a + b * b); z0 = Z(a, b); c = z0 + k * m_
        E = f"z+{'' if k==1 else k}|z|={c.tex()}"
        pr = K(f"រកចំនួនកុំផ្លិច $z$ ដែល ${E}$ ។", f"ដោះស្រាយសមីការ ${E}$ ក្នុង $\\mathbb{{C}}$ ។")
        l = [f"តាង $z=x+iy$ ។ ផ្នែកនិមិត្តនៃអង្គទាំងពីរស្មើគ្នា ព្រោះ $|z|$ ជាចំនួនពិត ដូច្នេះ $y={nt(b)}$ ។", "ផ្នែកពិតផ្តល់ ៖", dd(f"x+{'' if k==1 else k}\\sqrt{{x^{{2}}+{nt(b*b)}}}={nt(c.a)}")]
        if k == 1:
            l += [dd(f"\\sqrt{{x^{{2}}+{nt(b*b)}}}={nt(c.a)}-x"), f"ដោយលើកការេអង្គទាំងពីរ (លក្ខខណ្ឌ $x\\le {nt(c.a)}$) ៖", dd(f"x^{{2}}+{nt(b*b)}={nt(c.a**2)}-{nt(2*c.a)}x+x^{{2}}".replace("--", "+")), f"នាំឱ្យ $x={nt(a)}$ ដែលផ្ទៀងផ្ទាត់លក្ខខណ្ឌ ។"]
            ck = [(f"{z0.py()}+Abs({z0.py()})", c.py(), "substitution")]
            R("modulus_conjugate_conditions", "hard", pr, l + [f"ដូចនេះ $\\boxed{{z={z0.tex()}}}$ ។"], f"z={z0.tex()}", ck, (t, a, b, k))
        else:
            # k>1 quadratic in x: solve exactly, keep rows with one valid root
            xs_ = sp.Symbol("t", real=True)
            sol = sp.solve((k * k) * (xs_ ** 2 + b * b) - (c.a - xs_) ** 2, xs_)
            good = [s_ for s_ in sol if s_.is_rational and s_ <= c.a]
            bad = [s_ for s_ in sol if s_ not in good]
            if len(good) != 1 or not all(s_.is_rational for s_ in sol): return
            A_, B_, C_ = k * k - 1, 2 * c.a, k * k * b * b - c.a ** 2
            l += [f"ដាក់ជារាង ${k}\\sqrt{{x^{{2}}+{nt(b*b)}}}={nt(c.a)}-x$ រួចលើកការេ (លក្ខខណ្ឌ $x\\le {nt(c.a)}$) ៖", dd(ptex([A_, B_, C_], "x") + "=0"), f"សមីការនេះមានឫស " + " និង ".join(ll("x=" + nt(s_)) for s_ in sol) + f" ។ មានតែ $x={nt(a)}$ ប៉ុណ្ណោះដែលផ្ទៀងផ្ទាត់លក្ខខណ្ឌ ។"]
            ck = [(f"{z0.py()}+{k}*Abs({z0.py()})", c.py(), "substitution")]
            R("modulus_conjugate_conditions", "hard", pr, l + [f"ដូចនេះ $\\boxed{{z={z0.tex()}}}$ ។"], f"z={z0.tex()}", ck, (t, a, b, k))
    elif t == "mod_param":
        a, b = K(*TRIP[:10]); s = rsg(); c = K(1, 2, 3, -1, -2); m0 = a - c; val = sp.sqrt(a * a + b * b)
        # z=(m+c)+bi with |z|=val: m+c=±a
        m1, m2 = a - c, -a - c
        pr = K(f"គេឱ្យ $z=(m{c:+d})+{b}i$ ដែល $m\\in\\mathbb{{R}}$ ។ រកតម្លៃ $m$ ដើម្បីឱ្យ $|z|={val}$ ។", f"កំណត់ចំនួនពិត $m$ ដើម្បីឱ្យចំនួនកុំផ្លិច $z=(m{c:+d})+{b}i$ មានម៉ូឌុលស្មើនឹង ${val}$ ។")
        l = ["យើងមាន ៖", dd(f"|z|=\\sqrt{{(m{c:+d})^{{2}}+{b*b}}}={val}"), "លើកការេអង្គទាំងពីរ ៖", dd(rf"(m{c:+d})^{{2}}+{b*b}={val*val}\Leftrightarrow (m{c:+d})^{{2}}={a*a}"), dd(rf"m{c:+d}={a}\quad\vee\quad m{c:+d}=-{a}")]
        R("modulus_conjugate_conditions", "medium", pr, l + [f"ដូចនេះ $\\boxed{{m={m1}}}$ ឬ $\\boxed{{m={m2}}}$ ។"], f"m={m1},\\ m={m2}", [(f"Abs(({m1}+({c}))+{b}*I)", str(val), "modulus"), (f"Abs(({m2}+({c}))+{b}*I)", str(val), "modulus")], (t, a, b, c))
    elif t == "eqdist":
        p, q = G(-4, 4), G(-4, 4); 
        # |z-p|=|z-q| & z real => x; or z on imag axis
        d = q - p
        if d.a == 0: return
        x0 = (q.n2() - p.n2()) / (2 * d.a)
        if x0.q > 2: return
        z0 = Z(x0, 0)
        pr = f"រកចំនួនពិត $x$ ដែល $|x-({p.tex()})|=|x-({q.tex()})|$ ។"
        l = ["យើងសរសេរភាពស្មើគ្នានៃការេម៉ូឌុល ៖", dd(f"(x{tsum([(-p.a,'')]) if p.a>0 else '+'+nt(-p.a)})^{{2}}+{nt(p.b**2)}=(x{tsum([(-q.a,'')]) if q.a>0 else '+'+nt(-q.a)})^{{2}}+{nt(q.b**2)}"), "ពន្លាត ហើយលុបតួ $x^2$ ៖", dd(f"{tsum([(-2*p.a,'x')])}+{nt(p.n2())}={tsum([(-2*q.a,'x')])}+{nt(q.n2())}"), dd(f"{tsum([(2*d.a,'x')])}={nt(q.n2()-p.n2())}")]
        R("modulus_conjugate_conditions", "medium", pr, l + [f"ដូចនេះ $\\boxed{{x={nt(x0)}}}$ ។"], f"x={nt(x0)}", [(f"Abs({z0.py()}-{p.py()})", f"Abs({z0.py()}-{q.py()})", "equal distances")], (t, key(p), key(q)))
    elif t == "z2bar":
        c = K(2, 3, 4, 5, 6)
        # z^2 = c \bar z solutions: 0, c, c(-1/2 ± i√3/2)
        roots = [Z(0), Z(c), Z(Q(-c, 2), RT(3) * c / 2), Z(Q(-c, 2), -RT(3) * c / 2)]
        pr = f"រកគ្រប់ចំនួនកុំផ្លិច $z$ ដែល $z^2={c}\\bar{{z}}$ ។"
        l = ["តាង $z=x+iy$ ។ យើងបាន ៖", dd(f"x^{{2}}-y^{{2}}+2xyi={c}x-{c}yi"), dd(rf"\begin{{cases}}x^{{2}}-y^{{2}}={c}x\\2xy=-{c}y\end{{cases}}"), f"សមីការទីពីរសរសេរ $y(2x+{c})=0$ ។", f"ករណី $y=0$ ៖ $x^2={c}x$ ឱ្យ $x=0$ ឬ $x={c}$ ។", f"ករណី $x={nt(Q(-c,2))}$ ៖ $y^2=x^2-{c}x={nt(Q(3*c*c,4))}$ នាំឱ្យ $y=\\pm{nt(RT(3)*c/2)}$ ។"]
        txt = " , ".join(r_.tex() for r_ in roots)
        R("modulus_conjugate_conditions", "hard", pr, l + [f"ដូចនេះ ចម្លើយគឺ $\\boxed{{{txt}}}$ ។"], txt, [(f"expand({r_.py()}**2)", f"expand({c}*conjugate({r_.py()}))", "substitution") for r_ in roots], (t, c))
    elif t == "real_cond":
        # Z=(z+a)/(z-b)... instance: for z=x+iy, imag part of z^2 + k z̄
        c = K(1, 2, 3, 4); y0 = K(1, 2, 3, -1, -2)
        # z=x+y0 i ; Im(z^2 + c z) = 2 x y0 + c y0 =0 -> x=-c/2
        x0 = Q(-c, 2); z0 = Z(x0, y0); val = z0 ** 2 + c * z0
        pr = f"គេឱ្យ $z=x+{Z(0,y0).tex()}$ ដែល $x\\in\\mathbb{{R}}$ ។ រកតម្លៃ $x$ ដើម្បីឱ្យ $z^2+{c}z$ ជាចំនួនពិត ។".replace("+1z", "+z")
        l = ["ពន្លាត ៖", dd(f"z^{{2}}+{c}z=x^{{2}}{tsum([(-y0*y0,'')])}+{tsum([(2*y0,'x')])}i+{c}x+{Z(0,c*y0).tex()}".replace("+-", "-")), f"ផ្នែកនិមិត្តគឺ ${tsum([(2*y0,'x'),(c*y0,'')])}$ ។ កន្សោមជាចំនួនពិត លុះត្រាតែ ៖", dd(rf"{tsum([(2*y0,'x'),(c*y0,'')])}=0\Leftrightarrow x={nt(x0)}")]
        R("modulus_conjugate_conditions", "medium", pr, l + [f"ដូចនេះ $\\boxed{{x={nt(x0)}}}$ ហើយពេលនោះកន្សោមស្មើនឹង ${nt(val.a)}$ ។"], f"x={nt(x0)}", [(f"im(expand({z0.py()}**2+{c}*{z0.py()}))", "0", "imag zero"), (f"expand({z0.py()}**2+{c}*{z0.py()})", str(val.a), "value")], (t, c, y0))
    elif t == "z_times":
        z0 = G(-5, 5); n2 = z0.n2(); w = z0 + z0.c(); 
        pr = f"រកចំនួនកុំផ្លិច $z$ ដែលមានផ្នែកនិមិត្តវិជ្ជមាន ហើយផ្ទៀងផ្ទាត់ $z+\\bar{{z}}={nt(w.a)}$ និង $z\\bar{{z}}={nt(n2)}$ ។"
        z1 = Z(z0.a, abs(z0.b))
        l = ["តាង $z=x+iy$ ដែល $y>0$ ។ យើងមាន $z+\\bar{z}=2x$ និង $z\\bar{z}=x^2+y^2$ ។", dd(rf"2x={nt(w.a)}\Rightarrow x={nt(z0.a)}"), dd(rf"x^{{2}}+y^{{2}}={nt(n2)}\Rightarrow y^{{2}}={nt(z0.b**2)}\Rightarrow y={nt(abs(z0.b))}"), "(យើងយកតម្លៃវិជ្ជមាន ព្រោះ $y>0$ ។)"]
        R("modulus_conjugate_conditions", "easy", pr, l + [f"ដូចនេះ $\\boxed{{z={z1.tex()}}}$ ។"], f"z={z1.tex()}", [(f"{z1.py()}+conjugate({z1.py()})", str(w.a), "sum"), (f"{z1.py()}*conjugate({z1.py()})", str(n2), "product")], (t, str(z0.a), str(abs(z0.b))))
    else:
        a, b = K(*TRIP[:10]); k = sp.sqrt(a * a + b * b)
        z0 = Z(a, b * rsg())
        c = z0.a * 2
        pr = f"រកចំនួនកុំផ្លិច $z$ ដែល $|z|={k}$ និងផ្នែកពិតនៃ $z$ ស្មើនឹង ${a}$ ។"
        l = [f"តាង $z={a}+iy$ ដែល $y\\in\\mathbb{{R}}$ ។", dd(rf"|z|=\sqrt{{{a*a}+y^{{2}}}}={k}\Rightarrow y^{{2}}={k*k-a*a}\Rightarrow y=\pm{b}")]
        R("modulus_conjugate_conditions", "easy", pr, l + [f"ដូចនេះ $\\boxed{{z={Z(a,b).tex()}}}$ ឬ $\\boxed{{z={Z(a,-b).tex()}}}$ ។"], f"z={a}\\pm {b}i", [(f"Abs({Z(a,b).py()})", str(k), "modulus"), (f"Abs({Z(a,-b).py()})", str(k), "modulus")], (t, a, b))

def g_expr_xy():
    """Re and Im of an expression in z=x+iy, checked at concrete values of x."""
    t = K("sq", "conj", "ratio")
    y0 = K(1, 2, 3, -1, -2, -3)
    if t == "sq":
        c = K(2, 3, -2, -3, 4)
        reS = f"x**2-{y0*y0}+({c})*x"; imS = f"{2*y0}*x+({c*y0})"
        reT = ptex([1, c, -y0 * y0], "x"); imT = tsum([(2 * y0, "x"), (c * y0, "")])
        pr = f"គេឱ្យ $z=x+{Z(0,y0).tex()}$ ដែល $x\\in\\mathbb{{R}}$ ។ រកផ្នែកពិត និងផ្នែកនិមិត្តនៃ $w=z^2{c:+d}z$ ជាអនុគមន៍នៃ $x$ ។"
        l = ["ពន្លាត ៖", dd(f"z^{{2}}=x^{{2}}{tsum([(2*y0,'x')]) if y0<0 else '+'+tsum([(2*y0,'x')])}i{tsum([(-y0*y0,'')])}"), dd(f"w=({reT})+({imT})i")]
        ck = [(f"re(expand((x+({y0})*I)**2+({c})*(x+({y0})*I)))", reS, "real part"), (f"im(expand((x+({y0})*I)**2+({c})*(x+({y0})*I)))", imS, "imag part")]
        R("expression_in_x_y", "medium", pr, l + [f"ដូចនេះ ផ្នែកពិតគឺ $\\boxed{{{reT}}}$ ហើយផ្នែកនិមិត្តគឺ $\\boxed{{{imT}}}$ ។"], f"{reT},\\ {imT}", ck, (t, c, y0))
    elif t == "conj":
        a, b = rng.randint(2, 5), K(1, 2, 3, -1, -2)
        pr = f"តាង $z=x+iy$ ដែល $x,y\\in\\mathbb{{R}}$ ។ សរសេរ $Z={a}z{b:+d}i\\bar{{z}}$ ជាទម្រង់ $A+iB$ ដែល $A,B$ ជាកន្សោមនៃ $x$ និង $y$ ។".replace("+1i", "+i").replace("-1i", "-i")
        # a(x+iy)+b i (x-iy) = a x + b y + i(a y + b x)
        A_, B_ = tsum([(a, "x"), (b, "y")]), tsum([(b, "x"), (a, "y")])
        l = [f"ដោយ $\\bar{{z}}=x-iy$ យើងបាន ៖", dd(f"Z={a}(x+iy){b:+d}i(x-iy)".replace("+1i", "+i").replace("-1i", "-i")), dd(f"Z={a}x+{a}iy{tsum([(b,'ix')]) if b<0 else '+'+tsum([(b,'ix')])}{tsum([(b,'y')]) if b<0 else '+'+tsum([(b,'y')])}"), "ប្រមូលផ្នែកពិត និងផ្នែកនិមិត្ត ៖", dd(f"Z=({A_})+i({B_})")]
        ck = [(f"re(expand({a}*(x+2*I)+({b})*I*(x-2*I)))", f"{a}*x+({b})*2", "instance y=2"), (f"im(expand({a}*(x+2*I)+({b})*I*(x-2*I)))", f"({b})*x+{a}*2", "instance y=2")]
        R("expression_in_x_y", "medium", pr, l + [f"ដូចនេះ $\\boxed{{A={A_}}}$ និង $\\boxed{{B={B_}}}$ ។"], f"A={A_},\\ B={B_}", ck, (t, a, b))
    else:
        # z=x+i, Z=(z-1... ) : 1/z
        pr = f"គេឱ្យ $z=x+{Z(0,y0).tex()}$ ដែល $x\\in\\mathbb{{R}}$ ។ រកផ្នែកពិត និងផ្នែកនិមិត្តនៃ $\\frac{{1}}{{z}}$ ។"
        n = f"x^{{2}}+{y0*y0}"
        l = ["គុណភាគយក និងភាគបែងនឹង $\\bar{z}$ ៖", dd(rf"\frac{{1}}{{z}}=\frac{{\bar{{z}}}}{{z\bar{{z}}}}=\frac{{x{Z(0,-y0).tex() if -y0<0 else '+'+Z(0,-y0).tex()}}}{{{n}}}")]
        ck = [(f"re(1/(x+({y0})*I))", f"x/(x**2+{y0*y0})", "real part"), (f"im(1/(x+({y0})*I))", f"({-y0})/(x**2+{y0*y0})", "imag part")]
        R("expression_in_x_y", "medium", pr, l + [f"ដូចនេះ ផ្នែកពិតគឺ $\\boxed{{\\frac{{x}}{{{n}}}}}$ ហើយផ្នែកនិមិត្តគឺ $\\boxed{{\\frac{{{-y0}}}{{{n}}}}}$ ។"], f"\\frac{{x}}{{{n}}},\\ \\frac{{{-y0}}}{{{n}}}", ck, (t, y0))

# ---------- J. multi-part exam items (difficulty bacii) ----------
BASES = [Z(RT(3), 1), Z(RT(3), -1), Z(1, RT(3)), Z(1, -RT(3)), Z(1, 1), Z(1, -1), Z(-1, RT(3)), Z(-RT(3), 1), Z(RT(2), RT(2)), Z(RT(2), -RT(2)), Z(-1, 1), Z(2, 2), Z(2, -2), Z(2 * RT(3), 2), Z(3, RT(3)), Z(RT(3), 3), Z(RT(6), RT(2)), Z(0, 2)]
def wrap(z):
    return z.tex()
def g_m_surd():
    u, v = rng.sample(BASES, 2)
    if u == v or u == v.c() or u == -v: return
    s, p, q = u + v, u * v, u / v
    L = labels()
    n1, n2 = K(("z_1", "z_2"), ("z_1", "z_2"), ("A", "B"))
    stem = f"{K(*GIVE)} ${n1}={u.tex()}$ និង ${n2}={v.tex()}$ ។"
    conj = K(0, 1)
    pr = "\n".join([stem, f"{L[0]} គណនា ${n1}+{n2}$ និង ${n1}\\times {n2}$ ។", f"{L[1]} សរសេរ $\\frac{{{n1}}}{{{n2}}}$ ជាទម្រង់ពីជគណិត ។",
                    f"{L[2]} រកម៉ូឌុលនៃ ${n1}$ , ${n2}$ រួចទាញរកម៉ូឌុលនៃ ${n1}\\times {n2}$ និង $\\frac{{{n1}}}{{{n2}}}$ ។"] + ([f"{L[3]} គណនា $\\overline{{{n1}}}\\times {n2}$ ។"] if conj else []))
    pa = u.a * v.a; pb = u.b * v.b
    ml = u.mod() * v.mod(); mq = sp.radsimp(u.mod() / v.mod())
    l = [f"{L[0]} បូកផ្នែកពិត និងផ្នែកនិមិត្តរៀងគ្នា ៖", dd(f"{n1}+{n2}={s.tex()}"), "ពន្លាតផលគុណ ៖", dd(f"{n1}\\times {n2}=({u.tex()})({v.tex()})={p.tex()}"),
         f"ដូចនេះ $\\boxed{{{n1}+{n2}={s.tex()}}}$ និង $\\boxed{{{n1}\\times {n2}={p.tex()}}}$ ។",
         f"{L[1]} គុណភាគយក និងភាគបែងនឹង $\\overline{{{n2}}}={v.c().tex()}$ ៖", dd(rf"\frac{{{n1}}}{{{n2}}}=\frac{{({u.tex()})({v.c().tex()})}}{{{nt(v.a**2)}+{nt(v.b**2)}}}=\frac{{{(u*v.c()).tex()}}}{{{nt(v.n2())}}}={q.tex()}"),
         f"ដូចនេះ $\\boxed{{\\frac{{{n1}}}{{{n2}}}={q.tex()}}}$ ។",
         f"{L[2]} ម៉ូឌុលនីមួយៗគឺ ៖", dd(f"|{n1}|=r_1=\\sqrt{{{nt(u.a**2)}+{nt(u.b**2)}}}={nt(u.mod())}"), dd(f"|{n2}|=r_2=\\sqrt{{{nt(v.a**2)}+{nt(v.b**2)}}}={nt(v.mod())}"),
         "តាមលក្ខណៈម៉ូឌុល ៖", dd(rf"|{n1}\times {n2}|=|{n1}|\times|{n2}|={nt(ml)}\quad,\quad\left|\frac{{{n1}}}{{{n2}}}\right|=\frac{{|{n1}|}}{{|{n2}|}}={nt(mq)}"),
         f"ដូចនេះ $\\boxed{{|{n1}\\times {n2}|={nt(ml)}}}$ និង $\\boxed{{\\left|\\frac{{{n1}}}{{{n2}}}\\right|={nt(mq)}}}$ ។"]
    ck = [(f"{u.py()}+{v.py()}", s.py(), "sum"), (f"expand({u.py()}*{v.py()})", p.py(), "product"), (f"{u.py()}/{v.py()}", q.py(), "quotient"), (f"Abs({u.py()})*Abs({v.py()})", str(ml), "modulus product"), (f"Abs({u.py()}/{v.py()})", str(mq), "modulus quotient")]
    if conj:
        w = u.c() * v
        l += [f"{L[3]} ដោយ $\\overline{{{n1}}}={u.c().tex()}$ យើងបាន ៖", dd(f"\\overline{{{n1}}}\\times {n2}=({u.c().tex()})({v.tex()})={w.tex()}"), f"ដូចនេះ $\\boxed{{\\overline{{{n1}}}\\times {n2}={w.tex()}}}$ ។"]
        ck.append((f"expand(conjugate({u.py()})*{v.py()})", w.py(), "conj product"))
    R("exam_operations", "bacii", pr, l, f"{p.tex()},\\ {q.tex()},\\ {nt(ml)},\\ {nt(mq)}", ck, (key(u), key(v), conj, n1))

def g_m_gauss():
    v = K(*DENS[:14]); w = G(-4, 4); u = w * v
    if u.a == 0 or u.b == 0: return
    L = labels(); typ = K(1, 2, 3)
    stem = f"{K(*GIVE)} $z_1={u.tex()}$ និង $z_2={v.tex()}$ ។"
    p = u * v; d = u - v
    if d == 0: return
    if typ == 1:
        Zq = u.c() * v
        pr = "\n".join([stem, f"{L[0]} គណនា $z_1-z_2$ , $z_1\\times z_2$ ។", f"{L[1]} សរសេរ $\\frac{{z_1}}{{z_2}}$ ជាទម្រង់ពីជគណិត ។", f"{L[2]} រក $\\left|\\frac{{z_1}}{{z_2}}\\right|$ តាមពីរវិធី ។"])
        mq = w.mod()
        l = [f"{L[0]} " + K("យើងមាន ៖", "គេបាន ៖"), dd(f"z_1-z_2={u.p()}-{v.p()}={d.tex()}"), dd("z_1\\times z_2=" + chain(f"{u.p()}{v.p()}", *mul_chain(u, v))), f"ដូចនេះ $\\boxed{{z_1-z_2={d.tex()}}}$ និង $\\boxed{{z_1\\times z_2={p.tex()}}}$ ។",
             f"{L[1]} គុណនឹងចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែង ៖", dd(r"\frac{z_1}{z_2}=" + chain(*div_chain(u, v))), f"ដូចនេះ $\\boxed{{\\frac{{z_1}}{{z_2}}={w.tex()}}}$ ។",
             f"{L[2]} វិធីទី១ ៖ ប្រើលទ្ធផលសំណួរមុន ៖", dd(rf"\left|\frac{{z_1}}{{z_2}}\right|=|{w.tex()}|=\sqrt{{{nt(w.a**2)}+{nt(w.b**2)}}}={nt(mq)}"), "វិធីទី២ ៖ ប្រើលក្ខណៈម៉ូឌុល ៖", dd(rf"\frac{{|z_1|}}{{|z_2|}}=\frac{{\sqrt{{{nt(u.n2())}}}}}{{\sqrt{{{nt(v.n2())}}}}}=\sqrt{{{nt(w.n2())}}}={nt(mq)}"), f"ដូចនេះ វិធីទាំងពីរឱ្យលទ្ធផលតែមួយ គឺ $\\boxed{{\\left|\\frac{{z_1}}{{z_2}}\\right|={nt(mq)}}}$ ។"]
        ck = [(f"{u.py()}-{v.py()}", d.py(), "difference"), (f"{u.py()}*{v.py()}", p.py(), "product"), (f"{u.py()}/{v.py()}", w.py(), "quotient"), (f"Abs({u.py()})/Abs({v.py()})", str(mq), "modulus")]
        R("exam_operations", "bacii", pr, l, f"{d.tex()},\\ {p.tex()},\\ {w.tex()},\\ {nt(mq)}", ck, ("g1", key(u), key(v)))
    elif typ == 2:
        A = u + v.c(); B = u * v.c(); C = v * v
        pr = "\n".join([stem, f"{L[0]} រក $\\overline{{z_1}}$ , $\\overline{{z_2}}$ រួចគណនា $z_1+\\overline{{z_2}}$ ។", f"{L[1]} គណនា $z_1\\times\\overline{{z_2}}$ និង $z_2^2$ ។", f"{L[2]} បង្ហាញថា $\\frac{{z_1}}{{z_2}}=\\frac{{z_1\\times\\overline{{z_2}}}}{{|z_2|^2}}$ រួចទាញរកទម្រង់ពីជគណិតនៃ $\\frac{{z_1}}{{z_2}}$ ។"])
        l = [f"{L[0]} ប្តូរសញ្ញាផ្នែកនិមិត្ត ៖ $\\overline{{z_1}}={u.c().tex()}$ និង $\\overline{{z_2}}={v.c().tex()}$ ។", dd(f"z_1+\\overline{{z_2}}={u.p()}+{v.c().p()}={A.tex()}"), f"ដូចនេះ $\\boxed{{z_1+\\overline{{z_2}}={A.tex()}}}$ ។",
             f"{L[1]} យើងពន្លាត ៖", dd("z_1\\times\\overline{z_2}=" + chain(f"{u.p()}{v.c().p()}", *mul_chain(u, v.c()))), dd("z_2^{2}=" + chain(f"{v.p()}^{{2}}", C.tex())), f"ដូចនេះ $\\boxed{{z_1\\times\\overline{{z_2}}={B.tex()}}}$ និង $\\boxed{{z_2^2={C.tex()}}}$ ។",
             f"{L[2]} ដោយ $z_2\\times\\overline{{z_2}}=|z_2|^2$ យើងបាន ៖", dd(r"\frac{z_1}{z_2}=\frac{z_1\times\overline{z_2}}{z_2\times\overline{z_2}}=\frac{z_1\times\overline{z_2}}{|z_2|^2}"), f"យើងមាន $|z_2|^2={nt(v.n2())}$ ដូច្នេះ ៖", dd(rf"\frac{{z_1}}{{z_2}}=\frac{{{B.tex()}}}{{{nt(v.n2())}}}={w.tex()}"), f"ដូចនេះ $\\boxed{{\\frac{{z_1}}{{z_2}}={w.tex()}}}$ ។"]
        ck = [(f"{u.py()}+conjugate({v.py()})", A.py(), "sum"), (f"expand({u.py()}*conjugate({v.py()}))", B.py(), "product"), (f"expand({v.py()}**2)", C.py(), "square"), (f"{u.py()}*conjugate({v.py()})/Abs({v.py()})**2", w.py(), "quotient")]
        R("exam_operations", "bacii", pr, l, f"{A.tex()},\\ {B.tex()},\\ {C.tex()},\\ {w.tex()}", ck, ("g2", key(u), key(v)))
    else:
        s2 = u + v; c = K(2, 3); e = c * u - v; Zf = (u + v) / v
        pr = "\n".join([stem, f"{L[0]} គណនា ${c}z_1-z_2$ ។", f"{L[1]} សរសេរ $Z=\\frac{{z_1+z_2}}{{z_2}}$ ជាទម្រង់ពីជគណិត ។", f"{L[2]} ផ្ទៀងផ្ទាត់ថា $Z=\\frac{{z_1}}{{z_2}}+1$ ។", f"{L[3]} រកផ្នែកពិត និងផ្នែកនិមិត្តនៃ $Z^2$ ។"])
        Z2 = Zf * Zf
        l = [f"{L[0]} យើងបាន ៖", dd(f"{c}z_1-z_2={(c*u).p()}-{v.p()}={e.tex()}"), f"ដូចនេះ $\\boxed{{{c}z_1-z_2={e.tex()}}}$ ។",
             f"{L[1]} ដោយ $z_1+z_2={s2.tex()}$ ៖", dd("Z=" + chain(*div_chain(s2, v))), f"ដូចនេះ $\\boxed{{Z={Zf.tex()}}}$ ។",
             f"{L[2]} គណនា $\\frac{{z_1}}{{z_2}}$ ៖", dd(r"\frac{z_1}{z_2}=" + chain(*div_chain(u, v))), f"បូក $1$ យើងបាន ${w.tex()}+1={(w+1).tex()}$ ដែលស្មើនឹង $Z$ ។ ដូចនេះ $Z=\\frac{{z_1}}{{z_2}}+1$ ពិតមែន ។",
             f"{L[3]} ពន្លាតការេ ៖", dd("Z^{2}=" + chain(f"{Zf.p()}^{{2}}", Z2.tex())) if Zf.b != 0 else dd(f"Z^{{2}}={Z2.tex()}"), f"ដូចនេះ ផ្នែកពិតនៃ $Z^2$ គឺ $\\boxed{{{nt(Z2.a)}}}$ ហើយផ្នែកនិមិត្តគឺ $\\boxed{{{nt(Z2.b)}}}$ ។"]
        ck = [(f"{c}*{u.py()}-{v.py()}", e.py(), "combination"), (f"({u.py()}+{v.py()})/{v.py()}", Zf.py(), "Z"), (f"{u.py()}/{v.py()}+1", Zf.py(), "identity"), (f"re(expand(({Zf.py()})**2))", str(Z2.a), "re"), (f"im(expand(({Zf.py()})**2))", str(Z2.b), "im")]
        R("exam_operations", "bacii", pr, l, f"{e.tex()},\\ {Zf.tex()},\\ {Z2.tex()}", ck, ("g3", key(u), key(v), c))

def g_m_quad():
    p, q = rng.randint(-4, 4), rng.randint(1, 5)
    if p == 0: return
    b, c = -2 * p, p * p + q * q
    r1, r2 = Z(p, q), Z(p, -q); cs = [1, b, c]; E = ptex(cs); L = labels()
    D = b * b - 4 * c; typ = K(1, 2, 3)
    h = f"{L[0]} ដោះស្រាយសមីការ ${E}=0$ ក្នុងសំណុំចំនួនកុំផ្លិច ។ តាង $z_1$ ជាឫសដែលមានផ្នែកនិមិត្តវិជ្ជមាន និង $z_2$ ជាឫសមួយទៀត ។"
    base = [f"{L[0]} " + K("គណនាឌីសគ្រីមីណង់ ៖", "យើងមាន ៖"), dd(f"\\Delta=" + chain((f"({b})^{{2}}" if b < 0 else f"{b}^{{2}}") + f"-4\\times {c}", str(D), f"({2*q}i)^{{2}}")), dd(rf"z_1=\frac{{{-b}+{2*q}i}}{{2}}={r1.tex()}\quad,\quad z_2=\frac{{{-b}-{2*q}i}}{{2}}={r2.tex()}"), f"ដូចនេះ $\\boxed{{z_1={r1.tex()}}}$ និង $\\boxed{{z_2={r2.tex()}}}$ ។"]
    ck = [(pchk(cs, r1), "0", "root"), (pchk(cs, r2), "0", "root")]
    if typ == 1:
        s2 = r1 * r1; qn = r1 / r2; m_ = r1.mod()
        pr = "\n".join([h, f"{L[1]} សរសេរ $z_1^2$ និង $\\frac{{z_1}}{{z_2}}$ ជាទម្រង់ពីជគណិត ។", f"{L[2]} រក $|z_1|$ រួចបង្ហាញថា $z_1\\times z_2=|z_1|^2$ ។"])
        l = base + [f"{L[1]} ពន្លាត ៖", dd("z_1^{2}=" + chain(f"{r1.p()}^{{2}}", s2.tex())), dd(r"\frac{z_1}{z_2}=" + chain(rf"\frac{{{r1.p()}^{{2}}}}{{{r1.p()}{r2.p()}}}", rf"\frac{{{s2.tex()}}}{{{c}}}", qn.tex())), f"ដូចនេះ $\\boxed{{z_1^2={s2.tex()}}}$ និង $\\boxed{{\\frac{{z_1}}{{z_2}}={qn.tex()}}}$ ។",
                    f"{L[2]} ម៉ូឌុលគឺ ៖", dd(f"|z_1|=\\sqrt{{{nt(p*p)}+{nt(q*q)}}}={nt(m_)}"), f"ម្យ៉ាងទៀត $z_2=\\overline{{z_1}}$ ។ ដូច្នេះ ៖", dd(f"z_1\\times z_2={r1.p()}{r2.p()}={nt(p*p)}+{nt(q*q)}={c}=|z_1|^2"), f"ដូចនេះ $\\boxed{{z_1\\times z_2=|z_1|^2={c}}}$ ។"]
        ck += [(f"expand({r1.py()}**2)", s2.py(), "square"), (f"{r1.py()}/{r2.py()}", qn.py(), "quotient"), (f"{r1.py()}*{r2.py()}", f"Abs({r1.py()})**2", "identity")]
        R("exam_quadratic", "bacii", pr, l, f"{r1.tex()},\\ {r2.tex()},\\ {qn.tex()}", ck, (typ, b, c))
    elif typ == 2:
        n = 3; s3 = r1 ** 3; t3 = s3 + r2 ** 3
        pr = "\n".join([h, f"{L[1]} គណនា $z_1+z_2$ និង $z_1\\times z_2$ ។", f"{L[2]} ដោយប្រើលទ្ធផលខាងលើ គណនា $z_1^2+z_2^2$ និង $z_1^3+z_2^3$ ។"])
        S = 2 * p; P = c; A = S * S - 2 * P; B = S ** 3 - 3 * S * P
        l = base + [f"{L[1]} បូក និងគុណឫសទាំងពីរ ៖", dd(f"z_1+z_2={S}\\quad,\\quad z_1\\times z_2={P}"), f"ដូចនេះ $\\boxed{{z_1+z_2={S}}}$ និង $\\boxed{{z_1\\times z_2={P}}}$ ។",
                    f"{L[2]} យើងប្រើរូបមន្តពន្លាត ៖", dd(chain("z_1^{2}+z_2^{2}", "(z_1+z_2)^{2}-2z_1z_2", f"({S})^{{2}}-2\\times {P}", str(A))), dd(chain("z_1^{3}+z_2^{3}", "(z_1+z_2)^{3}-3z_1z_2(z_1+z_2)", f"({S})^{{3}}-3\\times {P}\\times ({S})", str(B))), f"ដូចនេះ $\\boxed{{z_1^2+z_2^2={A}}}$ និង $\\boxed{{z_1^3+z_2^3={B}}}$ ។"]
        ck += [(f"expand({r1.py()}**2+{r2.py()}**2)", str(A), "sum squares"), (f"expand({r1.py()}**3+{r2.py()}**3)", str(B), "sum cubes")]
        R("exam_quadratic", "bacii", pr, l, f"{r1.tex()},\\ {r2.tex()},\\ {A},\\ {B}", ck, (typ, b, c))
    else:
        k = K(1, 2, 3); w = r1 + k * I_
        pr = "\n".join([h, f"{L[1]} គេឱ្យ $w=z_1{'+' if True else ''}{'' if k==1 else k}i$ ។ សរសេរ $\\frac{{1}}{{w}}$ ជាទម្រង់ពីជគណិត ។", f"{L[2]} រកម៉ូឌុលនៃ $z_1\\times w$ ។"])
        iv = Z(1) / w; mw = sp.sqrt(c * w.n2())
        l = base + [f"{L[1]} យើងមាន $w={r1.p()}+{Z(0,k).tex()}={w.tex()}$ ។", dd(r"\frac{1}{w}=" + chain(rf"\frac{{{w.c().tex()}}}{{{nt(w.n2())}}}", iv.tex())), f"ដូចនេះ $\\boxed{{\\frac{{1}}{{w}}={iv.tex()}}}$ ។", f"{L[2]} តាមលក្ខណៈម៉ូឌុល ៖", dd(rf"|z_1\times w|=|z_1|\times|w|=\sqrt{{{c}}}\times\sqrt{{{nt(w.n2())}}}={nt(mw)}"), f"ដូចនេះ $\\boxed{{|z_1\\times w|={nt(mw)}}}$ ។"]
        ck += [(f"1/{w.py()}", iv.py(), "inverse"), (f"Abs(expand({r1.py()}*{w.py()}))", str(mw), "modulus")]
        R("exam_quadratic", "bacii", pr, l, f"{r1.tex()},\\ {r2.tex()},\\ {iv.tex()},\\ {nt(mw)}", ck, (typ, b, c, k))

def plane_diagram(row_id, pts, polygon=None, alt=""):
    """pts: list of (label, Z). Math-only labels in the PNG; TikZ source goes with it."""
    fig, ax = plt.subplots(figsize=(3.8, 3.6), dpi=110)
    xs = [float(z.a) for _, z in pts] + [0]; ys = [float(z.b) for _, z in pts] + [0]
    pad = 1.2
    ax.set_xlim(min(xs) - pad, max(xs) + pad); ax.set_ylim(min(ys) - pad, max(ys) + pad)
    for sd in ("top", "right"): ax.spines[sd].set_visible(False)
    for sd in ("left", "bottom"): ax.spines[sd].set_position("zero")
    ax.grid(alpha=0.2); ax.set_aspect("equal", adjustable="datalim")
    if polygon:
        P = [(float(z.a), float(z.b)) for z in polygon]; P.append(P[0])
        ax.plot(*zip(*P), lw=1.3, color="#1f4e9c")
    for lab, z in pts:
        ax.plot([float(z.a)], [float(z.b)], "o", ms=4.5, color="#c0392b")
        ax.annotate(f"${lab}$", (float(z.a), float(z.b)), textcoords="offset points", xytext=(6, 6))
    rel = f"diagrams/{row_id}.png"
    fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
    tz = ["\\begin{tikzpicture}[scale=0.6]", f"\\draw[->] ({min(xs)-1:.2f},0)--({max(xs)+1:.2f},0) node[right]{{$x$}};", f"\\draw[->] (0,{min(ys)-1:.2f})--(0,{max(ys)+1:.2f}) node[above]{{$y$}};"]
    if polygon: tz.append("\\draw[thick] " + "--".join(f"({float(z.a):.3f},{float(z.b):.3f})" for z in polygon) + "--cycle;")
    for lab, z in pts: tz.append(f"\\fill ({float(z.a):.3f},{float(z.b):.3f}) circle (2pt) node[above right]{{${lab}$}};")
    tz.append("\\end{tikzpicture}")
    return [{"type": "figure", "latex": "\n".join(tz), "image": rel, "alt_km": alt}]

def rid(prob): return f"{TOPIC}-{hashlib.sha1(prob.encode()).hexdigest()[:10]}"
def classify(a, b, c):
    A, B, C = sorted([a.__sub__(b).n2(), b.__sub__(c).n2(), a.__sub__(c).n2()])
    iso = A == B or B == C; right = A + B == C; eqv = A == B == C
    return A, B, C, iso, right, eqv

def tri_word(iso, right, eqv):
    if eqv: return "ត្រីកោណសម័ង្ស"
    if iso and right: return "ត្រីកោណកែងសមបាត"
    if right: return "ត្រីកោណកែង"
    if iso: return "ត្រីកោណសមបាត"
    return None

def g_m_poly():
    p, q = rng.randint(-3, 3), rng.randint(1, 4); a0 = K(-3, -2, -1, 1, 2, 3, 4)
    r = Z(p, q); qd = [1, -2 * p, p * p + q * q]
    cs = [int(c_.a) for c_ in pmul([1, -a0], qd)]
    if cs[1] == 0 or cs[2] == 0: return
    Pt = ptex(cs); L = labels(); qt = ptex(qd); lin = f"z{-a0:+d}"
    D = qd[1] ** 2 - 4 * qd[2]
    A_, B_, C_ = Z(a0), r, r.c()
    A2, B2, C2, iso, right, eqv = classify(A_, B_, C_)
    w = tri_word(iso, right, eqv)
    if w is None: return
    n = 3
    pr = "\n".join([f"គេឱ្យពហុធា $P(z)={Pt}$ ។", f"{L[0]} គណនា $P({a0})$ ។", f"{L[1]} រកចំនួនពិត $\\alpha$ និង $\\beta$ ដែល $P(z)=({lin})(z^2+\\alpha z+\\beta)$ ។", f"{L[2]} ដោះស្រាយសមីការ $P(z)=0$ ក្នុងសំណុំចំនួនកុំផ្លិច ។",
                    f"{L[3]} ក្នុងប្លង់កុំផ្លិច តាង $A$ , $B$ , $C$ ជារូបភាពរៀងគ្នានៃឫស ${a0}$ , ${r.tex()}$ និង ${r.c().tex()}$ ។ គណនា $AB$ , $AC$ , $BC$ រួចបញ្ជាក់ប្រភេទនៃត្រីកោណ $ABC$ ។"])
    dAB = (B_ - A_).mod(); dAC = (C_ - A_).mod(); dBC = (C_ - B_).mod()
    rw = rid(pr)
    dg = plane_diagram(rw, [("A", A_), ("B", B_), ("C", C_)], [A_, B_, C_], f"រូបភាពនៃឫសទាំងបី $A$ , $B$ , $C$ ក្នុងប្លង់កុំផ្លិច ។ {w} $ABC$ ។")
    l = [f"{L[0]} ជំនួស $z={a0}$ ៖", dd(f"P({a0})=({a0})^{{3}}{cs[1]:+}\\times ({a0})^{{2}}{cs[2]:+}\\times ({a0}){cs[3]:+}=0".replace("+1\\times ", "+").replace("-1\\times ", "-")), f"ដូចនេះ $\\boxed{{P({a0})=0}}$ ។",
         f"{L[1]} ពន្លាតអង្គខាងស្តាំ ៖", dd(f"(z{-a0:+d})(z^{{2}}+\\alpha z+\\beta)=z^{{3}}+(\\alpha{-a0:+d})z^{{2}}+(\\beta{-a0:+d}\\alpha)z{-a0:+d}\\beta".replace("-1\\alpha", "-\\alpha").replace("+1\\alpha", "+\\alpha").replace("-1\\beta", "-\\beta").replace("+1\\beta", "+\\beta")),
         "ប្រៀបធៀបមេគុណជាមួយ $P(z)$ ៖", dd(rf"\begin{{cases}}\alpha{-a0:+d}={cs[1]}\\{-a0}\beta={cs[3]}\end{{cases}}\Rightarrow\begin{{cases}}\alpha={nt(qd[1])}\\\beta={nt(qd[2])}\end{{cases}}".replace("{-1\\beta", "{-\\beta").replace("\\\\1\\beta", "\\\\\\beta").replace("\\\\-1\\beta", "\\\\-\\beta")),
         f"ដូចនេះ $\\boxed{{\\alpha={nt(qd[1])},\\ \\beta={nt(qd[2])}}}$ ។",
         f"{L[2]} $P(z)=0$ លុះត្រាតែ $z={a0}$ ឬ ${qt}=0$ ។", dd(f"\\Delta={nt(D)}=({2*q}i)^{{2}}\\Rightarrow z={r.tex()}\\ ,\\ z={r.c().tex()}"), f"ដូចនេះ ឫសទាំងបីគឺ $\\boxed{{{a0}}}$ , $\\boxed{{{r.tex()}}}$ និង $\\boxed{{{r.c().tex()}}}$ ។",
         f"{L[3]} ប្រវែងគិតតាម $AB=|z_B-z_A|$ ៖", dd(f"AB=|{(B_-A_).tex()}|={nt(dAB)}\\quad,\\quad AC=|{(C_-A_).tex()}|={nt(dAC)}\\quad,\\quad BC=|{(C_-B_).tex()}|={nt(dBC)}")]
    if right and not iso: l.append(f"យើងឃើញថា ផលបូកការេនៃជ្រុងខ្លីពីរស្មើនឹងការេនៃជ្រុងវែង ៖ ${nt(A2)}+{nt(B2)}={nt(C2)}$ ។")
    elif right: l.append(f"យើងឃើញថា $AB=AC$ ហើយ $AB^2+AC^2=BC^2$ ។")
    else: l.append("យើងឃើញថា $AB=AC$ ព្រោះ $B$ និង $C$ ឆ្លុះគ្នាធៀបនឹងអ័ក្សពិត ហើយ $A$ នៅលើអ័ក្សពិត ។")
    l.append(f"ដូចនេះ $ABC$ ជា{w} ។")
    ck = [(pchk(cs, x_), "0", "root") for x_ in (A_, B_, C_)] + [(f"Abs({(B_-A_).py()})", str(dAB), "AB"), (f"Abs({(C_-A_).py()})", str(dAC), "AC"), (f"Abs({(C_-B_).py()})", str(dBC), "BC")]
    R("exam_polynomial", "bacii", pr, l, f"{a0},\\ {r.tex()},\\ {r.c().tex()}", ck, (a0, p, q), dg, rw)

def g_plane_triangle():
    a, b, c = G(-4, 4, False), G(-4, 4, False), G(-4, 4, False)
    if a == b or b == c or a == c: return
    A2, B2, C2, iso, right, eqv = classify(a, b, c)
    w = tri_word(iso, right, eqv)
    if w is None: return
    area = abs((b - a).a * (c - a).b - (b - a).b * (c - a).a)
    if area == 0: return
    L = labels()
    pr = "\n".join([f"ក្នុងប្លង់កុំផ្លិច គេឱ្យចំណុច $A$ , $B$ , $C$ ជារូបភាពរៀងគ្នានៃ $z_A={a.tex()}$ , $z_B={b.tex()}$ និង $z_C={c.tex()}$ ។", f"{L[0]} សង់ចំណុច $A$ , $B$ , $C$ ។", f"{L[1]} គណនាប្រវែង $AB$ , $AC$ និង $BC$ ។", f"{L[2]} តើត្រីកោណ $ABC$ ជាត្រីកោណប្រភេទអ្វី ?"])
    dAB, dAC, dBC = (b - a).mod(), (c - a).mod(), (c - b).mod()
    rw = rid(pr)
    dg = plane_diagram(rw, [("A", a), ("B", b), ("C", c)], [a, b, c], f"ចំណុច $A$ , $B$ , $C$ ក្នុងប្លង់កុំផ្លិច ដែលបង្កើតជា{w} ។")
    tail = {"ត្រីកោណកែងសមបាត": "ត្រីកោណមានជ្រុងពីរស្មើគ្នា ហើយការេនៃជ្រុងវែងស្មើនឹងផលបូកការេនៃជ្រុងពីរទៀត ។", "ត្រីកោណកែង": f"ដោយ ${nt(A2)}+{nt(B2)}={nt(C2)}$ ត្រីកោណផ្ទៀងផ្ទាត់ទ្រឹស្តីបទពីតាគ័រ ។", "ត្រីកោណសមបាត": "ត្រីកោណមានជ្រុងពីរស្មើគ្នា ។", "ត្រីកោណសម័ង្ស": "ជ្រុងទាំងបីស្មើគ្នា ។"}[w]
    l = [f"{L[0]} ចំណុចទាំងបីគឺ $A({nt(a.a)},{nt(a.b)})$ , $B({nt(b.a)},{nt(b.b)})$ , $C({nt(c.a)},{nt(c.b)})$ (មើលរូប) ។", f"{L[1]} ដោយ $AB=|z_B-z_A|$ ៖", dd(f"AB=|{(b-a).tex()}|={nt(dAB)}"), dd(f"AC=|{(c-a).tex()}|={nt(dAC)}"), dd(f"BC=|{(c-b).tex()}|={nt(dBC)}"), f"ដូចនេះ $\\boxed{{AB={nt(dAB)}}}$ , $\\boxed{{AC={nt(dAC)}}}$ និង $\\boxed{{BC={nt(dBC)}}}$ ឯកតា ។", f"{L[2]} {tail}", f"ដូចនេះ $ABC$ ជា{w} ។"]
    ck = [(f"Abs({(b-a).py()})", str(dAB), "AB"), (f"Abs({(c-a).py()})", str(dAC), "AC"), (f"Abs({(c-b).py()})", str(dBC), "BC")]
    R("image_in_plane", "medium", pr, l, f"AB={nt(dAB)},\\ AC={nt(dAC)},\\ BC={nt(dBC)}", ck, (key(a), key(b), key(c)), dg, rw)

def g_m_sqrt_eq():
    r1, r2 = G(-4, 4, False), G(-4, 4, False)
    d = r1 - r2
    if r1 == r2 or d.a == 0 or d.b == 0 or abs(d.a) == abs(d.b): return
    if d.a < 0: r1, r2 = r2, r1; d = -d
    s, p = r1 + r2, r1 * r2; D = d * d; cs = [1, -s, p]; E = ptex(cs); L = labels()
    if s.b == 0 and p.b == 0: return
    pr = "\n".join(["គេមានសមីការ $(E)$ ៖ $" + E + "=0$ ។", f"{L[0]} គណនា ${d.p()}^{{2}}$ ។", f"{L[1]} គណនាឌីសគ្រីមីណង់នៃសមីការ $(E)$ ។", f"{L[2]} ដោះស្រាយសមីការ $(E)$ ក្នុង $\\mathbb{{C}}$ ។", f"{L[3]} ផ្ទៀងផ្ទាត់ផលបូកឫស និងផលគុណឫសនៃសមីការ $(E)$ ។"])
    l = [f"{L[0]} ពន្លាតការេ ៖", dd(chain(f"{d.p()}^{{2}}", tsum([(d.a**2, ""), (2*d.a*d.b, "i"), (d.b**2, "i^{2}")]), D.tex())), f"ដូចនេះ $\\boxed{{{d.p()}^{{2}}={D.tex()}}}$ ។",
         f"{L[1]} យើងមាន ៖", dd(chain("\\Delta=b^{2}-4ac", f"{s.p()}^{{2}}-4{p.p()}", f"{(s*s).p()}-{(4*p).p()}", D.tex())), f"ដូចនេះ $\\boxed{{\\Delta={D.tex()}}}$ ។",
         f"{L[2]} តាមសំណួរទី១ $\\Delta={d.p()}^{{2}}$ ដូច្នេះ ៖", dd(rf"z_1=\frac{{{s.p()}+{d.p()}}}{{2}}={r1.tex()}\quad,\quad z_2=\frac{{{s.p()}-{d.p()}}}{{2}}={r2.tex()}"), f"ដូចនេះ $\\boxed{{z_1={r1.tex()}}}$ និង $\\boxed{{z_2={r2.tex()}}}$ ។",
         f"{L[3]} យើងគណនាផ្ទាល់ ៖", dd(f"z_1+z_2={s.tex()}"), dd("z_1\\times z_2=" + chain(f"{r1.p()}{r2.p()}", p.tex())), f"ដូចនេះ លទ្ធផលស្របនឹងមេគុណនៃសមីការ ព្រោះ $z_1+z_2={s.tex()}$ និង $z_1z_2={p.tex()}$ ។"]
    ck = [(f"expand({d.py()}**2)", D.py(), "square"), (f"expand(({s.py()})**2-4*{p.py()})", D.py(), "delta"), (pchk(cs, r1), "0", "root"), (pchk(cs, r2), "0", "root")]
    R("exam_quadratic", "bacii", pr, l, f"z_1={r1.tex()},\\ z_2={r2.tex()}", ck, ("sq", key(r1), key(r2)))

def g_m_linear():
    z0 = G(-5, 5); p, q = rng.randint(1, 4), K(-3, -2, 1, 2, 3)
    if p + q == 0 or p == q: return
    c = p * z0 + q * z0.c(); L = labels(); E = f"{p}z{q:+d}\\bar{{z}}={c.tex()}".replace("1z", "z").replace("+1\\bar", "+\\bar").replace("-1\\bar", "-\\bar")
    if p == 1: E = E
    sq = z0 ** 2; iv = Z(1) / z0; m2 = z0.n2(); md = z0.mod()
    pr = "\n".join([f"{L[0]} កំណត់ចំនួនកុំផ្លិច $z$ ដែលផ្ទៀងផ្ទាត់ ${E}$ ។", f"{L[1]} រកម៉ូឌុលនៃ $z$ ។", f"{L[2]} សរសេរ $z^2$ និង $\\frac{{1}}{{z}}$ ជាទម្រង់ពីជគណិត ។", f"{L[3]} ផ្ទៀងផ្ទាត់ថា $z\\times\\frac{{1}}{{z}}=1$ ។"])
    rA, rB = tsum([(p + q, "x")]), tsum([(p - q, "y")])
    l = [f"{L[0]} តាង $z=x+iy$ ដែល $x,y\\in\\mathbb{{R}}$ នោះ $\\bar{{z}}=x-iy$ ។ សមីការក្លាយជា ៖", dd(f"({rA})+({rB})i={c.tex()}"), "ដោយផ្នែកពិតស្មើគ្នា និងផ្នែកនិមិត្តស្មើគ្នា ៖", dd(rf"{rA}={nt(c.a)}\quad,\quad {rB}={nt(c.b)}"), f"នាំឱ្យ $x={nt(z0.a)}$ និង $y={nt(z0.b)}$ ។ ដូចនេះ $\\boxed{{z={z0.tex()}}}$ ។",
         f"{L[1]} យើងបាន ៖", dd(f"|z|=r=\\sqrt{{{nt(z0.a**2)}+{nt(z0.b**2)}}}={nt(md)}"), f"ដូចនេះ $\\boxed{{|z|={nt(md)}}}$ ។",
         f"{L[2]} ពន្លាត ៖", dd("z^{2}=" + chain(f"{z0.p()}^{{2}}", sq.tex())), dd(r"\frac{1}{z}=\frac{\bar{z}}{|z|^{2}}=" + chain(rf"\frac{{{z0.c().tex()}}}{{{nt(m2)}}}", iv.tex())), f"ដូចនេះ $\\boxed{{z^2={sq.tex()}}}$ និង $\\boxed{{\\frac{{1}}{{z}}={iv.tex()}}}$ ។",
         f"{L[3]} គុណលទ្ធផលទាំងពីរ ៖", dd(rf"{z0.p()}\times\frac{{{z0.c().tex()}}}{{{nt(m2)}}}=\frac{{{nt(m2)}}}{{{nt(m2)}}}=1"), "ដូចនេះ ទំនាក់ទំនងនេះត្រឹមត្រូវ ។"]
    ck = [(f"{p}*{z0.py()}+({q})*conjugate({z0.py()})", c.py(), "equation"), (f"Abs({z0.py()})", str(md), "modulus"), (f"expand({z0.py()}**2)", sq.py(), "square"), (f"1/{z0.py()}", iv.py(), "inverse")]
    R("exam_linear_conjugate", "bacii", pr, l, f"z={z0.tex()},\\ |z|={nt(md)}", ck, (key(z0), p, q))

def g_m_map():
    a, b = G(-3, 3, False), G(-3, 3, False); L = labels()
    if a == b: return
    z0 = G(-4, 4); den = z0 - b
    if den == 0: return
    f0 = (z0 - a) / den
    if not (f0.a.q <= 10 and f0.b.q <= 10): return
    c = K(Z(0, 1), Z(0, -1), Z(2), Z(1, 1), Z(0, 2), Z(1, -1), Z(3))
    # solve (z-a)/(z-b)=c -> z(1-c)=a-bc
    if c == 1: return
    co = 1 - c; rhs = a - b * c; zs = rhs / co
    if zs == b or zs.a.q > 2 or zs.b.q > 2: return
    fa = f"\\frac{{z-{a.p()}}}{{z-{b.p()}}}" if a != 0 and b != 0 else None
    if fa is None: return
    pr = "\n".join([f"ចំពោះ $z\\neq{b.tex()}$ គេកំណត់ $f(z)={fa}$ ។", f"{L[0]} គណនា $f({z0.tex()})$ ជាទម្រង់ពីជគណិត ។", f"{L[1]} ដោះស្រាយសមីការ $f(z)={c.tex()}$ ក្នុង $\\mathbb{{C}}$ ។", f"{L[2]} រកម៉ូឌុលនៃ $f({z0.tex()})$ ។"])
    nn = z0 - a; md = sp.sqrt(f0.n2())
    l = [f"{L[0]} ភាគយកគឺ ${z0.p()}-{a.p()}={nn.tex()}$ ហើយភាគបែងគឺ ${z0.p()}-{b.p()}={den.tex()}$ ។", dd(f"f({z0.tex()})=" + chain(*div_chain(nn, den))), f"ដូចនេះ $\\boxed{{f({z0.tex()})={f0.tex()}}}$ ។",
         f"{L[1]} គុណអង្គទាំងពីរនឹង $z-{b.p()}$ ៖", dd(f"z-{a.p()}={c.p()}\\left[z-{b.p()}\\right]"), "ប្រមូលតួមាន $z$ ៖", dd(f"{co.p()}z={rhs.tex()}"), dd("z=" + chain(*div_chain(rhs, co))), f"តម្លៃនេះខុសពី ${b.tex()}$ ។ ដូចនេះ $\\boxed{{z={zs.tex()}}}$ ។",
         f"{L[2]} តាមលក្ខណៈម៉ូឌុល ៖", dd(rf"\left|f({z0.tex()})\right|=\frac{{|{nn.tex()}|}}{{|{den.tex()}|}}=\frac{{{nt(nn.mod())}}}{{{nt(den.mod())}}}={nt(md)}"), f"ដូចនេះ $\\boxed{{\\left|f({z0.tex()})\\right|={nt(md)}}}$ ។"]
    ck = [(f"({z0.py()}-{a.py()})/({z0.py()}-{b.py()})", f0.py(), "f value"), (f"({zs.py()}-{a.py()})/({zs.py()}-{b.py()})", c.py(), "solution"), (f"Abs(({z0.py()}-{a.py()})/({z0.py()}-{b.py()}))", str(md), "modulus")]
    R("exam_function_of_z", "bacii", pr, l, f"{f0.tex()},\\ z={zs.tex()},\\ {nt(md)}", ck, (key(a), key(b), key(z0), key(c)))

def g_show_root():
    t = K("quad_surd", "cubic", "value")
    if t == "quad_surd":
        u = K(*BASES[:8]); b, c = -2 * u.a, u.n2(); cs = [1, b, c]; 
        if not (b.is_rational and c.is_rational):
            E = f"z^{{2}}{'-' if u.a>0 else '+'}{nt(abs(2*u.a))}z+{nt(c)}"
        else: E = ptex(cs)
        s = u * u
        pr = f"បង្ហាញថា $z_0={u.tex()}$ ជាឫសរបស់សមីការ ${E}=0$ ។"
        l = ["យើងគណនា ៖", dd("z_0^{2}=" + chain(f"({u.tex()})^{{2}}", s.tex())), "ជំនួសក្នុងអង្គខាងឆ្វេង ៖", dd(chain(f"{s.p()}{'-' if u.a>0 else '+'}{nt(abs(2*u.a))}({u.tex()})+{nt(c)}", "0"))]
        R("show_root", "easy", pr, l + [f"ដូចនេះ $\\boxed{{z_0={u.tex()}}}$ ជាឫសរបស់សមីការនេះ ។"], f"P\\left({u.tex()}\\right)=0", [(pchk(cs, u), "0", "substitution")], (t, key(u)))
    elif t == "value":
        u = G(-4, 4); w = G(-3, 3); cs = pfrom([u, w]); E = ptex(cs)
        pr = f"តើ ${u.tex()}$ ជាឫសនៃសមីការ ${E}=0$ ឬទេ ?"
        s = u * u
        l = [f"ជំនួស $z={u.tex()}$ ៖", dd(chain(f"{u.p()}^{{2}}-{(u+w).p()}{u.p()}+{(u*w).p()}", f"{s.p()}-{(u*(u+w)).p()}+{(u*w).p()}", "0"))]
        R("show_root", "medium", pr, l + [f"ដូចនេះ បាទ/ចាស ${u.tex()}$ ជាឫសនៃសមីការ ។".replace("បាទ/ចាស ", "")], f"P\\left({u.tex()}\\right)=0", [(pchk(cs, u), "0", "substitution")], (t, key(u), key(w)))
    else:
        u = G(-3, 3); w = u + K(1, 2, -1) * I_
        if (w - u) == 0: return
        cs = pfrom([u, w], 1); cs2 = [c_ for c_ in cs]; cs2[-1] = cs2[-1] + K(1, 2, 3)
        val = peval(cs2, u); E = ptex(cs2)
        pr = f"តើ ${u.tex()}$ ជាឫសនៃសមីការ ${E}=0$ ឬទេ ? ពន្យល់ ។"
        l = [f"ជំនួស $z={u.tex()}$ ក្នុងអង្គខាងឆ្វេង យើងបានតម្លៃ ៖", dd(f"{u.p()}^{{2}}-{(-cs2[1]).p()}{u.p()}+{cs2[2].p()}={val.tex()}"), "តម្លៃនេះខុសពីសូន្យ ។"]
        R("show_root", "medium", pr, l + [f"ដូចនេះ ${u.tex()}$ មិនមែនជាឫសនៃសមីការទេ ។"], f"P\\left({u.tex()}\\right)={val.tex()}\\neq 0", [(pchk(cs2, u), val.py(), "substitution")], (t, key(u), key(w), str(cs2[-1])))

# ---------- run ----------
def norm(t):
    t = t.replace("+-", "-").replace("--", "+") if False else t.replace("+-", "-")
    t = re.sub(r"\$\$([^$]*?)\\quad\\vee\\quad([^$]*?)\$\$", r"$\1$ ឬ $\2$", t)
    t = re.sub(r"(\\[a-zA-Z]+)(?=[0-9])", r"\1 ", t)
    t = re.sub(r"\+\(-(\d*[xy])\)i", r"-\1i", t)
    t = re.sub(r"\+\((\d*[xy])\)i", r"+\1i", t)
    t = re.sub(r"\((-?\d*[xy])\)\+", r"\1+", t)
    t = re.sub(r"\((-?\d*[xy])\)-", r"\1-", t)
    t = re.sub(r"([+-])1\(x", r"\1(x", t)
    t = re.sub(r"(?<![0-9{])1\(x\+iy\)", "(x+iy)", t)
    t = re.sub(r"\((\d+)\)\^", r"\1^", t)
    t = re.sub(r"\\times \((\d+)\)", r"\\times \1", t)
    t = re.sub(r"-\(-(\d*i)\)", r"+\1", t)
    t = re.sub(r"\(i\)\^", "i^", t)
    t = re.sub(r"=\\frac\{[^{}]*\}\{1\}=", "=", t)
    t = re.sub(r"z\+\(-([^()]*)\)(?![(\\])", r"z-\1", t) if False else t
    t = re.sub(r"z\+\(([0-9][^()]*|i[^()]*)\)(?=[)}\\=^]|$)", r"z+\1", t)
    return tidy(t.replace("\n\n", "\n"))

def main():
    import complex_algebra_hand as H
    plan = [(g_re_im, 60), (g_param_real, 70), (g_lincomb, 30), (g_product, 60), (g_binom_power, 45), (g_ipow, 80), (g_one_plus_i_power, 45),
            (g_conjugate, 70), (g_modulus, 80), (g_quotient, 70), (g_inverse_mix, 70), (g_equality, 80), (g_sqrt, 80), (g_linear, 70), (g_linear_conj, 70),
            (g_quad_real, 80), (g_quad_complex, 70), (g_biquad, 30), (g_vieta, 40), (g_build_quad, 50), (g_cubic_real, 70), (g_cubic_complex, 30), (g_quartic, 20),
            (g_conditions, 60), (g_expr_xy, 30), (g_show_root, 30), (g_m_surd, 50), (g_m_gauss, 60), (g_m_quad, 50), (g_m_poly, 30), (g_plane_triangle, 20), (g_m_sqrt_eq, 30), (g_m_linear, 30), (g_m_map, 30)]
    for fn, n in plan:
        fill(fn, n if fn.__name__.startswith("g_m_") else int(n * 0.8))
    H.add(ROWS, make_row, check, TOPIC, plane_diagram, Z, RT, rid)
    out = {}
    for r in ROWS:
        for f in ("problem_km", "solution_km", "answer_latex"):
            r[f] = norm(r[f])
        r["exam_fit"] = "textbook" if r["subtopic"] == "image_in_plane" else "bacii_seen"
        out.setdefault(r["id"], r)
    rows = list(out.values())
    rng.shuffle(rows)
    used = {os.path.basename(d["image"]) for r in rows for d in r["diagrams"] if d.get("image")}
    for f in os.listdir(os.path.join(ROOT, "diagrams")):
        if f.startswith(TOPIC + "-") and f not in used:
            os.remove(os.path.join(ROOT, "diagrams", f))
    write_jsonl(rows, "complex/algebra.jsonl")

if __name__ == "__main__":
    main()
