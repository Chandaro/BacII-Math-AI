"""BacII multi-part function study rows (Khmer). Writes out/function_study.jsonl."""
import random, sys, os, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from common import *

rng = random.Random(20261105)
R = sp.Rational
exp, ln, oo, EE = sp.exp, sp.log, sp.oo, sp.E
GEN = "function_study"
IRS = "IR"

def P(*o):
    return rng.choice(o)

def tx(e):
    """Compact LaTeX for an expression (\\ln x rather than \\ln{\\left(x \\right)})."""
    t = e if isinstance(e, str) else lx(e)
    while "\\ln{" in t:
        i = t.index("\\ln{"); j = i + 4; d = 1
        while d:
            d += (t[j] == "{") - (t[j] == "}"); j += 1
        inner = t[i + 4:j - 1]
        mt = re.fullmatch(r"\\left\(([a-z0-9]+) \\right\)", inner)
        pw = re.match(r"\^\{(\d+)\}|\^(\d)", t[j:])
        head = "\\ln"
        if pw:
            # a power of the function: \ln^{2}x, never \ln x^{2}
            head = "\\ln^{" + (pw.group(1) or pw.group(2)) + "}"; j += pw.end()
        t = t[:i] + ((head + ("" if pw else " ") + mt.group(1) + " ") if mt else head + inner) + t[j:]
    t = t.replace(" + ", "+").replace(" - ", "-").replace("- ", "-")
    t = re.sub(r"(\d) ([a-z\\(])", r"\1\2", t)
    t = t.replace(" \\right)", "\\right)").replace("\\left(", "(").replace("\\right)", ")")
    t = t.replace(" ^", "^").replace("\\ln x }", "\\ln x}").replace("\\ln x ^", "\\ln x^")
    t = re.sub(r"\\ln (\w+)\s+(?=[+\-)}=,;(]|$)", r"\\ln \1", t)
    t = re.sub(r"\\ln\^\{(\d+)\}(\w+)\s+(?=[+\-)}=,;(]|$)", r"\\ln^{\1}\2", t)
    return t.strip()

def ttex(T):
    """Tangent line as m x + b."""
    T = sp.expand(T)
    m_ = T.coeff(x, 1); b_ = T.coeff(x, 0)
    if m_.is_Add:
        return tx(T)
    mx = tx(m_ * x)
    if b_ == 0:
        return mx
    bt = tx(b_)
    return mx + ("" if bt.startswith("-") else "+") + bt

def lin(p, v="x"):
    """x-p as text."""
    return tx(sp.Symbol(v) - p) if v != "x" else tx(x - p)

def cf(c, body):
    """coefficient c times a parenthesised body."""
    if c == 1:
        return body
    if c == -1:
        return "-" + body
    return tx(c) + body

def sterm(c, body):
    """Signed term c*body for use after another term: empty when c is 0, no 1 coefficient."""
    if c == 0:
        return ""
    a_ = abs(c)
    return ("+" if c > 0 else "-") + ("" if a_ == 1 else tx(a_)) + body

def sconst(c):
    """Signed constant after another term: empty when c is 0."""
    return "" if c == 0 else ("+" if c > 0 else "-") + tx(abs(c))

def sfrac(c):
    """Signed term c/x after another term: empty when c is 0."""
    return "" if c == 0 else ("+" if c > 0 else "-") + "\\frac{" + tx(abs(c)) + "}{x}"

def shift(sym, v):
    """sym-v as text, simplified for a zero, negative or compound v."""
    if v == 0:
        return sym
    n = tx(sp.expand(-v))
    return sym + n if n.startswith("-") else sym + "+" + n

def nsq(n):
    r = math.isqrt(n) if n >= 0 else -1
    return r * r == n

def num(e):
    return float(sp.N(e))

class St:
    def __init__(self, f, fam, sub, **k):
        self.f = f; self.fam = fam; self.sub = sub
        self.L = []; self.A = []; self.crit = []; self.holes = []; self.lo = None; self.hi = None; self.gap = None
        self.xint = None; self.xhow = ""; self.dsteps = []; self.sgn = ""; self.zero = ""
        self.center = None; self.center_lines = None; self.tans = []; self.pos = None
        self.fpp = None; self.pre = None; self.aux = None; self.param = None; self.extra_fu = []
        self.ftex = "f(x)=" + tx(f); self.Dtex = f"D={IRS}"; self.Ddoc = None; self.key = None
        self.canon = None; self.inflect = None; self.pretty = None
        self.__dict__.update(k)
    def lim(self, pt, side, val, why=""):
        self.L.append(dict(pt=pt, side=side, val=val, why=why))
    def asym(self, kind, eq, why, expr=None, side=None):
        self.A.append(dict(kind=kind, eq=eq, why=why, expr=expr, side=side))

def limtex(pt, side=None, name="f"):
    p = "+\\infty" if pt == oo else "-\\infty" if pt == -oo else tx(pt)
    if side:
        p = p + "^{" + side + "}" if not isinstance(pt, sp.Add) and not (pt.is_Rational and not pt.is_Integer) and pt >= 0 and pt == int(pt) else "(" + p + ")^{" + side + "}"
    return f"\\lim_{{x\\to {p}}}"

def vt(v):
    return "+\\infty" if v == oo else "-\\infty" if v == -oo else tx(v)

# ---------- quadratic helper ----------
def quad_txt(A, B, C, name="x"):
    """Discriminant write-up for A x^2+Bx+C=0 with rational roots."""
    d = B * B - 4 * A * C
    rt = sp.sqrt(d)
    x1, x2 = sorted([(-B - rt) / (2 * A), (-B + rt) / (2 * A)])
    bt = tx(B) if B >= 0 and sp.Rational(B).q == 1 else f"({tx(B)})"
    return f"$\\Delta={bt}^2-4({tx(A)})({tx(C)})={tx(d)}$ ដូច្នេះ $\\sqrt{{\\Delta}}={tx(rt)}$ ។ សមីការមានឫសពីរ $x_1={tx(x1)}$ ឬ $x_2={tx(x2)}$ ។"

def poly_roots(pl):
    """Rational roots if pl splits completely over Q, else None."""
    fl = sp.factor_list(pl, x)[1]
    out = []
    for fac, mlt in fl:
        if sp.degree(fac, x) != 1:
            return None
        out.append(sp.solve(fac, x)[0] if False else -fac.coeff(x, 0) / fac.coeff(x, 1))
    return sorted(set(out))

def polyL(S, lead, deg):
    sp_ = oo if lead > 0 else -oo
    sm = sp_ if deg % 2 == 0 else -sp_
    term = tx(lead * x**deg)
    S.lim(-oo, None, sm, f"{limtex(-oo)}{term}")
    S.lim(oo, None, sp_, f"{limtex(oo)}{term}")

# =================== FAMILIES ===================
def F_cubic():
    a = P(1, -1, 2, -2, R(1, 3), -R(1, 3), 1, -1, R(2, 3))
    mode = P("gen", "gen", "dbl", "dbl", "mono")
    if mode == "dbl":
        r = rng.randint(-3, 3); t = P(3, -3, 6, -6)
        s_ = r + t; a = P(1, -1, 2, R(1, 2), -R(1, 2)) if t % 2 == 0 else P(1, -1, 2)
        f = sp.expand(a * (x - r)**2 * (x - s_))
        p, q = sorted([r, r + 2 * R(t, 3)])
    elif mode == "mono":
        h = rng.randint(-2, 2); k = rng.randint(1, 4); c = rng.randint(-6, 6)
        f = sp.expand(a * ((x - h)**3 + 3 * k * (x - h)) + c)
        fp = sp.diff(f, x)
        S = St(f, "cubic", "polynomial_cubic_monotone", key=str(fp))
        A_, B_, C_ = [fp.coeff(x, i) for i in (2, 1, 0)]
        S.dsteps = [f"$$f'(x)={tx(fp)}$$"]
        S.fp = fp; S.fptex = tx(fp)
        dl = B_**2 - 4 * A_ * C_
        S.sgn = (f"ត្រីធា $f'(x)$ មាន $\\Delta={tx(dl)}<0$ នោះ $f'(x)$ មានសញ្ញាដូចមេគុណ ${tx(A_)}$ ជានិច្ច ។")
        polyL(S, a, 3)
        _cub_common(S, a); return S
    else:
        p = rng.randint(-4, 3); q = p + rng.randint(1, 5)
        if a.is_Integer if hasattr(a, "is_Integer") else True:
            if (p + q) % 2 and a % 2:
                q += 1
        c = rng.randint(-6, 8)
        f = sp.expand(a * x**3 - R(3, 2) * a * (p + q) * x**2 + 3 * a * p * q * x + c)
    fp = sp.diff(f, x)
    fac = cf(3 * a, f"({lin(p)})({lin(q)})")
    S = St(f, "cubic", "polynomial_cubic", key=str(fp))
    S.fp = 3 * a * (x - p) * (x - q); S.fptex = fac
    A_, B_, C_ = [fp.coeff(x, i) for i in (2, 1, 0)]
    S.dsteps = [P("តាមរូបមន្ត $(x^n)'=nx^{n-1}$ យើងបាន ៖", "ធ្វើដេរីវេតាមតួនីមួយៗ គេបាន ៖", "ដោយ $f$ ជាពហុធា គេបាន ៖") + f"\n$$f'(x)={tx(fp)}={fac}$$"]
    S.crit = [p, q]
    S.zero = P(f"$f'(x)=0$ សមមូល $x={tx(p)}$ ឬ $x={tx(q)}$ ។",
               f"បើ $f'(x)=0$ គេបានសមីការ ${tx(A_)}"[:0] + f"ដោះស្រាយ $f'(x)=0$ ៖ " + quad_txt(A_, B_, C_))
    S.sgn = P(f"ត្រីធា $f'(x)$ មានសញ្ញាដូចមេគុណ ${tx(3*a)}$ នៅក្រៅឫស និងមានសញ្ញាផ្ទុយនៅចន្លោះឫស ។",
              f"យកសញ្ញាតាមត្រីធាដឺក្រេទីពីរ ៖ ក្រៅឫសមានសញ្ញាដូច ${tx(3*a)}$ ហើយចន្លោះឫសមានសញ្ញាផ្ទុយ ។")
    polyL(S, a, 3)
    _cub_common(S, a)
    S.mode = mode
    return S

def _cub_common(S, a):
    f = S.f
    rts = poly_roots(f)
    if rts is not None:
        S.xint = rts
        S.xhow = f"គេអាចសរសេរ $f(x)={tx(sp.factor(f))}$ ។"
    h = -f.coeff(x, 2) / (3 * f.coeff(x, 3)); k = f.subs(x, h)
    S.center = (h, k)
    g = sp.expand(f.subs(x, 2 * h - x))
    S.center_lines = [f"$$f({tx(2*h-x)})={tx(g)}$$", f"$$f({tx(2*h-x)})+f(x)={tx(sp.expand(g+f))}$$"]
    S.fpp = sp.diff(f, x, 2); S.inflect = (h, k)
    S.tans = [t for t in range(-3, 5) if t not in S.crit]

def F_quartic():
    mode = P("bi", "bi", "gen", "stat")
    c = rng.randint(-5, 6)
    if mode == "bi":
        a = P(1, -1, R(1, 2), -R(1, 2), R(1, 4), 2); r = rng.randint(1, 4)
        f = sp.expand(a * x**4 - 2 * a * r**2 * x**2 + c)
        fp = 4 * a * x * (x - r) * (x + r); fac = cf(4 * a, f"x(x^2-{r*r})")
        fac2 = cf(4 * a, f"x({lin(r)})({lin(-r)})")
        cr = [-r, 0, r]; sub = "polynomial_biquadratic"
    elif mode == "gen":
        a = P(1, -1, R(1, 4), -R(1, 4)); p = rng.randint(-3, 0); q = p + rng.randint(1, 3); r = q + rng.randint(1, 3)
        fp = 4 * a * (x - p) * (x - q) * (x - r)
        f = sp.integrate(sp.expand(fp), x) + c
        fac = tx(sp.expand(fp)); fac2 = cf(4 * a, f"({lin(p)})({lin(q)})({lin(r)})")
        cr = [p, q, r]; sub = "polynomial_quartic"
    else:
        a = P(1, -1, R(1, 4), -R(1, 4), R(1, 2)); p = rng.randint(-2, 2); q = p + P(-3, -2, -1, 1, 2, 3)
        fp = 4 * a * (x - p)**2 * (x - q)
        f = sp.integrate(sp.expand(fp), x) + c
        fac = tx(sp.expand(fp)); fac2 = cf(4 * a, f"({lin(p)})^2({lin(q)})")
        cr = sorted([p, q]); sub = "polynomial_quartic_stationary"
    S = St(f, "quartic", sub, key=str(sp.expand(fp)))
    S.fp = fp; S.fptex = fac2; S.crit = cr
    S.dsteps = [P("ដេរីវេនៃពហុធា ៖", "តាមរូបមន្ត $(x^n)'=nx^{n-1}$ គេបាន ៖") + f"\n$$f'(x)={tx(sp.expand(fp))}={fac2}$$"]
    S.zero = "ដោះស្រាយ $f'(x)=0$ គេបាន " + " ឬ ".join(f"$x={tx(v)}$" for v in cr) + " ។"
    S.sgn = "ដោយ $(" + lin(p) + ")^2\\ge 0$ នោះ $f'(x)$ មានសញ្ញាតាមកត្តា $" + cf(4 * a, f"({lin(q)})") + "$ ។" if mode == "stat" else "សញ្ញានៃ $f'(x)$ គឺជាសញ្ញានៃផលគុណកត្តាដឺក្រេទីមួយ ដូចតារាងសញ្ញាខាងក្រោម ។"
    polyL(S, a, 4)
    rts = poly_roots(f)
    if rts is not None:
        S.xint = rts; S.xhow = f"គេអាចសរសេរ $f(x)={tx(sp.factor(f))}$ ។"
    S.fpp = sp.diff(f, x, 2)
    S.tans = [t for t in range(-3, 4) if t not in cr]
    if mode == "bi":
        S.even = True
    return S

def F_homog():
    p = rng.randint(-4, 5); k = rng.randint(-3, 4); g = P(-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6); c = P(1, 1, 1, 2)
    if k == 0 and c == 2: c = 1
    f_num = sp.expand(c * k * (x - p) + c * g); den = c * (x - p)
    if p == 0 and c == 2: return None
    A, B = f_num.coeff(x, 1), f_num.coeff(x, 0); Cc, Dd = c, -c * p
    f = k + g / (x - p)
    S = St(f, "homographic", "rational_homographic", key=f"{p},{k},{g}")
    nt, dt = tx(f_num), tx(sp.expand(den))
    S.ftex = f"f(x)=\\frac{{{nt}}}{{{dt}}}"
    S.pretty = f_num / sp.expand(den)
    S.nd = (f_num, sp.expand(den), nt, dt)
    S.holes = [p]; S.Dtex = f"D={IRS}-\\{{{tx(p)}\\}}"
    S.Ddoc = f"អនុគមន៍ $f$ មានន័យលុះត្រាតែ ${dt}\\neq 0$ ឬ $x\\neq {tx(p)}$ ។"
    det = A * Dd - B * Cc
    S.fp = det / (Cc * x + Dd)**2
    S.fptex = f"\\frac{{{tx(det)}}}{{({dt})^2}}"
    S.dsteps = [P("តាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ គេបាន ៖", "ប្រើរូបមន្តដេរីវេនៃផលចែក គេបាន ៖") +
                f"\n$$f'(x)=\\frac{{{cf(A, f'({dt})')}-{cf(Cc, f'({nt})')}}}{{({dt})^2}}={S.fptex}$$" if A != 0 else "ប្រើរូបមន្ត $\\left(\\frac{1}{v}\\right)'=-\\frac{v'}{v^2}$ គេបាន ៖\n" + f"$$f'(x)={S.fptex}$$"]
    S.sgn = f"ដោយ $({dt})^2>0$ គ្រប់ $x\\in D$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(det)}$ ជានិច្ច ។"
    lv = R(A, Cc) if False else sp.Rational(A) / Cc
    w = f"\\frac{{{nt}}}{{{dt}}}"
    S.lim(-oo, None, lv, (f"{limtex(-oo)}\\frac{{{tx(A*x)}}}{{{tx(Cc*x)}}}" if A != 0 else ""))
    S.lim(oo, None, lv, (f"{limtex(oo)}\\frac{{{tx(A*x)}}}{{{tx(Cc*x)}}}" if A != 0 else ""))
    S.lim(sp.Integer(p), "-", -oo if g > 0 else oo); S.lim(sp.Integer(p), "+", oo if g > 0 else -oo)
    S.asym("v", f"x={tx(p)}", "v", x - p); S.asym("h", f"y={tx(lv)}", "h", lv)
    S.yfix = True
    if A != 0:
        S.xint = [-sp.Rational(B) / A]; S.xhow = f"ភាគយក ${nt}=0$ ។"
    else:
        S.xint = []; S.xhow = "ភាគយកខុសពីសូន្យជានិច្ច ។"
    S.center = (sp.Integer(p), sp.Integer(k))
    S.canon = f"f(x)={tx(k)}+\\frac{{{tx(g)}}}{{{tx(x-p)}}}" if k != 0 else None
    q = 2 * p - x
    S.center_lines = [f"$$f({tx(q)})+f(x)=" + (f"{tx(k)}+\\frac{{{tx(g)}}}{{{tx(p-x)}}}+{tx(k)}+\\frac{{{tx(g)}}}{{{tx(x-p)}}}" if k != 0 else f"\\frac{{{tx(g)}}}{{{tx(p-x)}}}+\\frac{{{tx(g)}}}{{{tx(x-p)}}}") + f"={tx(2*k)}$$"]
    S.tans = [t for t in range(-3, 7) if t != p and abs(t - p) <= 3]
    return S

def _pretty_frac(N, Dn):
    return f"\\frac{{{tx(sp.expand(N))}}}{{{tx(sp.expand(Dn))}}}"

def F_oblique():
    al = P(1, 1, 1, -1, -1, 2, -2, 3); be = rng.randint(-4, 5); p = rng.randint(-4, 4)
    k = P(1, 1, 2, 2, 3)
    mono = rng.random() < 0.2
    ga = -al * P(1, 2, 3, 4, 5) if mono else al * k * k
    N = sp.expand((al * x + be) * (x - p) + ga)
    f = al * x + be + ga / (x - p)
    S = St(f, "oblique", "rational_oblique_asymptote", key=f"{al},{be},{p},{ga}")
    nt, dt = tx(N), tx(x - p)
    S.ftex = f"f(x)=\\frac{{{nt}}}{{{dt}}}"
    S.nd = (N, x - p, nt, dt)
    S.holes = [p]; S.Dtex = f"D={IRS}-\\{{{tx(p)}\\}}"
    S.Ddoc = f"$f$ មានន័យលុះត្រាតែ ${dt}\\neq 0$ ឬ $x\\neq {tx(p)}$ ។"
    canon = f"{tx(al*x+be)}" + ("+" if ga > 0 else "-") + f"\\frac{{{abs(ga)}}}{{{dt}}}"
    S.canon = "f(x)=" + canon
    S.canon_how = f"ចែកភាគយកនឹងភាគបែង គេបាន ${nt}=({tx(al*x+be)})({dt})" + ("+" if ga > 0 else "-") + f"{abs(ga)}$ ។"
    Nn = sp.expand(al * (x - p)**2 - ga)
    if mono:
        S.fptex = f"\\frac{{{tx(Nn)}}}{{({dt})^2}}"
        S.fp = Nn / (x - p)**2
    else:
        S.fptex = "\\frac{" + cf(al, f"({lin(p-k)})({lin(p+k)})") + f"}}{{({dt})^2}}"
        S.fp = al * (x - p - k) * (x - p + k) / (x - p)**2
        S.crit = [p - k, p + k]
    v1 = P(1, 2)
    Np = sp.diff(N, x)
    if v1 == 1:
        S.dsteps = [P("តាមរូបមន្តផលចែក $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ គេបាន ៖", "ដោយ $f$ ជាផលចែកនៃពហុធាពីរ គេបាន ៖") +
                    f"\n$$f'(x)=\\frac{{({tx(Np)})({dt})-({nt})}}{{({dt})^2}}=\\frac{{{tx(Nn)}}}{{({dt})^2}}$$"]
        if not mono: S.dsteps.append(f"$$f'(x)={S.fptex}$$")
    else:
        S.dsteps = [f"ដោយ $f(x)={canon}$ គេបាន ៖\n$$f'(x)={tx(al)}" + ("-" if ga > 0 else "+") + f"\\frac{{{abs(ga)}}}{{({dt})^2}}=\\frac{{{tx(Nn)}}}{{({dt})^2}}$$"]
        if not mono: S.dsteps.append(f"$$f'(x)={S.fptex}$$")
    A_, B_, C_ = [Nn.coeff(x, i) for i in (2, 1, 0)]
    if mono:
        S.sgn = f"ភាគយក ${tx(Nn)}=" + cf(al, f"[({dt})^2+{tx(abs(sp.Rational(ga, al)))}]") + f"$ មានសញ្ញាដូច ${tx(al)}$ ជានិច្ច ហើយភាគបែងវិជ្ជមាន ។"
    else:
        S.sgn = f"ដោយ $({dt})^2>0$ គ្រប់ $x\\in D$ នោះ $f'(x)$ មានសញ្ញាដូចភាគយក ${tx(Nn)}$ ។"
        S.zero = P(f"$f'(x)=0$ សមមូល ${tx(Nn)}=0$ ។ " + quad_txt(A_, B_, C_), f"$f'(x)=0$ សមមូល $({dt})^2={tx(abs(sp.Rational(ga, al)))}$ ឬ $x={tx(p-k)}$ ឬ $x={tx(p+k)}$ ។")
    for pt, nm in ((-oo, "-"), (oo, "+")):
        S.lim(pt, None, (oo if al > 0 else -oo) * (1 if nm == "+" else -1), f"{limtex(pt)}\\frac{{{tx(al*x**2)}}}{{x}}={limtex(pt)}{tx(al*x)}")
    S.lim(sp.Integer(p), "-", -oo if ga > 0 else oo); S.lim(sp.Integer(p), "+", oo if ga > 0 else -oo)
    S.asym("v", f"x={tx(p)}", "v", x - p)
    dd = f"\\frac{{{tx(ga)}}}{{{dt}}}"
    S.asym("o", f"y={tx(al*x+be)}", f"$$\\lim_{{x\\to\\pm\\infty}}[f(x)-({tx(al*x+be)})]=\\lim_{{x\\to\\pm\\infty}}{dd}=0$$", al * x + be)
    disc = sp.Poly(N, x).discriminant()
    if disc < 0:
        S.xint = []; S.xhow = f"សមីការ ${nt}=0$ មាន $\\Delta={tx(disc)}<0$ សមីការគ្មានឫស ។"
    elif disc >= 0 and sp.sqrt(disc).is_Rational:
        S.xint = [v for v in poly_roots(N)]
        S.xhow = f"$f(x)=0$ សមមូល ${nt}=0$ ។ " + (quad_txt(N.coeff(x, 2), N.coeff(x, 1), N.coeff(x, 0)) if disc > 0 else "")
        if p in S.xint: return None
    S.center = (sp.Integer(p), al * p + be)
    q = 2 * p - x
    S.center_lines = [f"$$f({tx(q)})={tx(al*q+be)}" + ("-" if ga > 0 else "+") + f"\\frac{{{abs(ga)}}}{{{dt}}}$$",
                      f"$$f({tx(q)})+f(x)={tx(sp.expand(al*q+be+al*x+be))}$$"]
    side = (ga > 0)
    S.pos = dict(dtex=dd, cases=[(f"x<{tx(p)}", not side), (f"x>{tx(p)}", side)], eq=f"y={tx(al*x+be)}", chk=[(p - 1, not side), (p + 1, side)], lin=al * x + be)
    S.tans = [t for t in range(p - 3, p + 4) if t != p and t not in S.crit]
    return S

def F_ratH():
    c = P(1, 1, 1, 3, 4); t = P(1, 2, 3, 4, R(1, 2), -1, -2, -3)
    u = -R(c) / t
    if t == u: return None
    s_ = sp.ilcm(sp.denom(t), sp.denom(u), 1)
    sum_ = t + u
    A = sp.denom(sum_ / 2) * P(1, 1, 2, -1, -2); B = -A * sum_ / 2
    if abs(A) > 12 or abs(B) > 12: return None
    k = P(0, 0, 0, 1, -1, 2)
    N = sp.expand(k * (x**2 + c) + A * x + B); Dn = x**2 + c
    f = k + (A * x + B) / Dn
    S = St(f, "rat_quad", "rational_no_vertical", key=str((A, B, c, k)))
    nt, dt = tx(N), tx(Dn)
    S.ftex = f"f(x)=\\frac{{{nt}}}{{{dt}}}"
    S.Ddoc = f"ភាគបែង ${dt}>0$ ជានិច្ច ដូច្នេះ $f$ មានន័យគ្រប់ $x$ ។"
    Nn = sp.expand(-A * x**2 - 2 * B * x + A * c)
    x1, x2 = sorted([t, u]); S.crit = [x1, x2]
    S.fp = Nn / Dn**2
    S.fptex = f"\\frac{{{tx(Nn)}}}{{({dt})^2}}"
    Np = sp.diff(N, x)
    S.dsteps = [P("តាមរូបមន្តដេរីវេនៃផលចែក គេបាន ៖", "ប្រើរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ ៖") + f"\n$$f'(x)=\\frac{{({tx(Np)})({dt})-2x({nt})}}{{({dt})^2}}={S.fptex}$$"]
    S.sgn = f"ដោយ $({dt})^2>0$ នោះ $f'(x)$ មានសញ្ញាដូចភាគយក ${tx(Nn)}$ ។"
    S.zero = f"ដោះស្រាយ ${tx(Nn)}=0$ ៖ " + quad_txt(-A, -2 * B, A * c)
    S.lim(-oo, None, sp.Integer(k), f"{limtex(-oo)}\\frac{{{tx(N.coeff(x,2)*x**2) if k else tx(A*x)}}}{{x^2}}")
    S.lim(oo, None, sp.Integer(k), f"{limtex(oo)}\\frac{{{tx(N.coeff(x,2)*x**2) if k else tx(A*x)}}}{{x^2}}")
    S.asym("h", f"y={tx(k)}", "h", sp.Integer(k))
    S.noV = True
    disc = sp.Poly(N, x).discriminant() if k else None
    if k == 0:
        S.xint = [-sp.Rational(B) / A]; S.xhow = f"ភាគយក ${nt}=0$ ។"
    elif disc < 0:
        S.xint = []; S.xhow = f"${nt}=0$ មាន $\\Delta={tx(disc)}<0$ សមីការគ្មានឫស ។"
    elif sp.sqrt(disc).is_Rational and disc > 0:
        S.xint = poly_roots(N); S.xhow = f"$f(x)=0$ សមមូល ${nt}=0$ ។ " + quad_txt(N.coeff(x, 2), N.coeff(x, 1), N.coeff(x, 0))
    S.tans = [t_ for t_ in (-2, -1, 0, 1, 2) if t_ not in S.crit]
    return S

def F_twoV():
    p = rng.randint(-4, 2); q = p + rng.randint(1, 4); k = P(0, 0, 1, -1, 2)
    if rng.random() < 0.65:
        u = P(1, 1, 2, 3); v = P(1, 2, 1, 3)
        if sp.gcd(u, v) != 1: return None
        c = P(1, -1, 2, -2)
        A, B = u * u * c, -v * v * c
        cr = sorted(set([(u * q - v * p) / sp.Integer(u - v) if u != v else None, (u * q + v * p) / sp.Integer(u + v)]) - {None})
    else:
        A = P(1, 2, 3, -1, -2); B = A * P(1, 2); cr = []
    f = k + A / (x - p) + B / (x - q)
    Dn = sp.expand((x - p) * (x - q)); N = sp.expand(k * Dn + A * (x - q) + B * (x - p))
    if sp.degree(N, x) == 0 and N == 0: return None
    S = St(f, "two_vert", "rational_two_vertical", key=str((p, q, A, B, k)))
    nt, dt = tx(N), tx(Dn)
    S.ftex = f"f(x)=\\frac{{{nt}}}{{{dt}}}"
    S.nd = (N, Dn, nt, dt)
    S.holes = [sp.Integer(p), sp.Integer(q)]
    S.Dtex = f"D={IRS}-\\{{{tx(p)};{tx(q)}\\}}"
    S.Ddoc = f"$f$ មានន័យលុះត្រាតែ ${dt}\\neq 0$ ឬ $({lin(p)})({lin(q)})\\neq 0$ គឺ $x\\neq {tx(p)}$ និង $x\\neq {tx(q)}$ ។"
    Np = sp.diff(N, x); Dp = sp.diff(Dn, x)
    Nn = sp.expand(Np * Dn - N * Dp)
    S.crit = cr; S.fp = Nn / Dn**2
    S.fptex = f"\\frac{{{tx(sp.factor(Nn))}}}{{({dt})^2}}"
    S.dsteps = [P("តាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ គេបាន ៖", "អនុវត្តរូបមន្តដេរីវេនៃផលចែក ៖") + (f"\n$$f'(x)=\\frac{{({tx(Np)})({dt})-({nt})({tx(Dp)})}}{{({dt})^2}}={S.fptex}$$" if Np != 0 else f"\n$$f'(x)={S.fptex}$$")]
    S.sgn = f"ដោយ $({dt})^2>0$ លើ $D$ នោះ $f'(x)$ មានសញ្ញាដូចភាគយក ${tx(sp.factor(Nn))}$ ។"
    if cr:
        S.zero = "$f'(x)=0$ សមមូល " + " ឬ ".join(f"$x={tx(v)}$" for v in cr) + " ។"
    if any(v in (p, q) for v in cr): return None
    S.lim(-oo, None, sp.Integer(k)); S.lim(oo, None, sp.Integer(k))
    for pt, a_, b_ in ((p, A, None), (q, B, None)):
        S.lim(sp.Integer(pt), "-", -oo if a_ > 0 else oo); S.lim(sp.Integer(pt), "+", oo if a_ > 0 else -oo)
    S.asym("v", f"x={tx(p)}", "v", x - p); S.asym("v", f"x={tx(q)}", "v", x - q); S.asym("h", f"y={tx(k)}", "h", sp.Integer(k))
    r = poly_roots(N) if sp.degree(N, x) >= 1 else []
    if r is not None and not (set(r) & {p, q}):
        S.xint = r; S.xhow = (f"ភាគយក ${nt}\\neq 0$ ជានិច្ច ។" if N.is_number else f"$f(x)=0$ សមមូល ${nt}=0$ ។") + (f" គេអាចសរសេរ ${tx(sp.factor(N))}=0$ ។" if sp.degree(N, x) == 2 else "")
    S.tans = [t for t in range(p - 2, q + 3) if t not in (p, q) and t not in cr]
    return S

def F_invsq():
    al = P(1, -1, 2, -2); be = rng.randint(-3, 4); p = rng.randint(-3, 3); t = P(1, -1, 2, -2)
    ga = al * R(t**3, 2)
    if ga.q != 1: al2 = 2 * al; ga = al2 * R(t**3, 2); al = al2
    f = al * x + be + ga / (x - p)**2
    S = St(f, "inv_square", "rational_inverse_square", key=str((al, be, p, t)))
    dt = tx(x - p)
    S.ftex = f"f(x)={tx(al*x+be)}" + ("+" if ga > 0 else "-") + f"\\frac{{{abs(ga)}}}{{({dt})^2}}"
    S.holes = [sp.Integer(p)]; S.Dtex = f"D={IRS}-\\{{{tx(p)}\\}}"
    S.Ddoc = f"$f$ មានន័យលុះត្រាតែ ${dt}\\neq 0$ ឬ $x\\neq {tx(p)}$ ។"
    S.nd = (sp.Integer(ga), (x - p)**2, tx(ga), f"({dt})^2")
    u = x - p
    cr = p + t; S.crit = [cr]
    S.fp = al * (x - p - t) * (u**2 + t * u + t**2) / u**3
    qq = f"({dt})^2{'+' if t>0 else '-'}{abs(t)}({dt})+{t*t}"
    S.fptex = "\\frac{" + cf(al, f"({lin(cr)})[{qq}]") + f"}}{{({dt})^3}}"
    S.dsteps = [f"ដោយ $\\left(\\frac{{1}}{{u^2}}\\right)'=-\\frac{{2u'}}{{u^3}}$ គេបាន ៖\n$$f'(x)={tx(al)}" + ("-" if ga > 0 else "+") + f"\\frac{{{abs(2*ga)}}}{{({dt})^3}}=\\frac{{{tx(al)}({dt})^3{'-' if ga>0 else '+'}{abs(2*ga)}}}{{({dt})^3}}$$",
                f"ប្រើរូបមន្ត $a^3-b^3=(a-b)(a^2+ab+b^2)$ គេបាន ៖\n$$f'(x)={S.fptex}$$"]
    S.sgn = f"ដោយ ${qq}>0$ ជានិច្ច នោះ $f'(x)$ មានសញ្ញាដូច $\\frac{{{cf(al, f'({lin(cr)})')}}}{{{dt}}}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល $x={tx(cr)}$ ។"
    s1 = oo if al > 0 else -oo
    S.lim(-oo, None, -s1, f"{limtex(-oo)}{tx(al*x)}"); S.lim(oo, None, s1, f"{limtex(oo)}{tx(al*x)}")
    sg = oo if ga > 0 else -oo
    S.lim(sp.Integer(p), "-", sg); S.lim(sp.Integer(p), "+", sg)
    S.asym("v", f"x={tx(p)}", "v", x - p)
    dd = f"\\frac{{{tx(ga)}}}{{({dt})^2}}"
    S.asym("o", f"y={tx(al*x+be)}", f"$$\\lim_{{x\\to\\pm\\infty}}[f(x)-({tx(al*x+be)})]=\\lim_{{x\\to\\pm\\infty}}{dd}=0$$", al * x + be)
    S.pos = dict(dtex=dd, cases=[(f"x\\in D", ga > 0)], eq=f"y={tx(al*x+be)}", chk=[(p + 1, ga > 0), (p - 1, ga > 0)], lin=al * x + be)
    S.tans = [t_ for t_ in range(p - 2, p + 3) if t_ != p and t_ != cr]
    return S

# ---- exponential ----
def _ek(k):
    return tx(exp(k * x))

def F_linexp():
    k = sp.Rational(P(1, 1, -1, -1, 2, -2, R(1, 2), -R(1, 2))); a = sp.Integer(P(1, 1, -1, 2, -2, 3)); b = sp.Integer(rng.randint(-5, 5)); c = P(0, 0, 0, 1, -1, 2, -2)
    f = (a * x + b) * exp(k * x) + c
    u = a * k * x + a + b * k
    x0 = -(a + b * k) / (a * k)
    if b == 0 and a != 1 and False: return None
    if x0.q > 4: return None
    S = St(f, "lin_exp", "exponential_linear_times_exp", key=str((a, b, k, c)))
    e_ = _ek(k); lt = tx(a * x + b)
    S.ftex = f"f(x)=({lt}){e_}" + (("+" if c > 0 else "-") + str(abs(c)) if c else "")
    S.Ddoc = f"អនុគមន៍ $f$ ជាផលគុណនៃពហុធានិងអនុគមន៍អ៊ិចស្ប៉ូណង់ស្យែល ដូច្នេះមានន័យគ្រប់ $x$ ។"
    S.fp = u * exp(k * x); S.fptex = f"({tx(u)}){e_}"
    S.dsteps = [P("តាមរូបមន្ត $(uv)'=u'v+uv'$ ជាមួយ", "ប្រើរូបមន្តដេរីវេនៃផលគុណ ដោយយក") + f" $u={lt}$ និង $v={e_}$ គេបាន $u'={tx(a)}$ និង $v'={tx(k*exp(k*x))}$ ។\n$$f'(x)={tx(a)}{e_}+({lt})({tx(k*exp(k*x))})={S.fptex}$$"]
    S.sgn = f"ដោយ ${e_}>0$ គ្រប់ $x$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(u)}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល ${tx(u)}=0$ ឬ $x={tx(x0)}$ ។"
    S.crit = [x0]
    zero_side = -oo if k > 0 else oo; big = oo if k > 0 else -oo
    S.lim(zero_side, None, sp.Integer(c), f"ដោយ ${limtex(zero_side)}x{e_}=0$ និង ${limtex(zero_side)}{e_}=0$")
    sgnb = (1 if a > 0 else -1) * (1 if big == oo else -1)
    S.lim(big, None, oo if sgnb > 0 else -oo, f"ដោយ ${limtex(big)}({lt})={vt(oo if a*(1 if big==oo else -1)>0 else -oo)}$ និង ${limtex(big)}{e_}=+\\infty$")
    S.L.sort(key=lambda d: d["pt"] == oo)
    S.asym("h", f"y={tx(c)}", "h", sp.Integer(c), side=zero_side)
    S.noObl = True
    if c == 0:
        S.xint = [-R(b) / a]; S.xhow = f"ដោយ ${e_}>0$ នោះ $f(x)=0$ សមមូល ${lt}=0$ ។"
    S.fpp = sp.expand(k * (a * k * x + a + b * k) + a * k) * exp(k * x)
    S.tans = [t for t in (0, 1, -1, 2) if t != x0]
    S.xr = (-5, 5)
    return S

def F_quadexp():
    k = sp.Integer(P(1, -1)); A = sp.Rational(P(1, 1, -1, 2, -2, R(1, 2))); p = rng.randint(-3, 2); q = p + rng.randint(1, 4)
    a = k * A
    b_ = (-a * (p + q) - 2 * A) / k; c_ = (a * p * q - b_) / k
    if not (sp.Rational(b_).q in (1, 2) and sp.Rational(c_).q in (1, 2)): return None
    poly = A * x**2 + b_ * x + c_
    f = poly * exp(k * x)
    S = St(f, "quad_exp", "exponential_quadratic_times_exp", key=str((A, p, q, k)))
    e_ = _ek(k); lt = tx(poly)
    S.ftex = f"f(x)=({lt}){e_}"
    S.Ddoc = "អនុគមន៍នេះកំណត់ចំពោះគ្រប់ចំនួនពិត $x$ ។"
    u = sp.expand(a * (x - p) * (x - q))
    S.fp = u * exp(k * x); S.fptex = cf(a, f"({lin(p)})({lin(q)})") + e_
    S.dsteps = [P("តាមរូបមន្ត $(uv)'=u'v+uv'$ គេបាន ៖", "អនុគមន៍ជាផលគុណ ដូច្នេះ ៖") + f"\n$$f'(x)=({tx(sp.diff(poly,x))}){e_}+({lt})({tx(k*exp(k*x))})=({tx(u)}){e_}$$\n$$f'(x)={S.fptex}$$"]
    S.sgn = f"ដោយ ${e_}>0$ នោះ $f'(x)$ មានសញ្ញាដូចត្រីធា ${tx(u)}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល ${tx(u)}=0$ ។ " + quad_txt(u.coeff(x, 2), u.coeff(x, 1), u.coeff(x, 0))
    S.crit = [sp.Integer(p), sp.Integer(q)]
    zs = -oo if k > 0 else oo; big = -zs
    S.lim(zs, None, sp.Integer(0), f"ដោយ ${limtex(zs)}x^n{e_}=0$ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$")
    S.lim(big, None, oo if A > 0 else -oo, f"ដោយ ${limtex(big)}({lt})={vt(oo if A>0 else -oo)}$ និង ${limtex(big)}{e_}=+\\infty$")
    S.L.sort(key=lambda d: d["pt"] == oo)
    S.asym("h", "y=0", "h", sp.Integer(0), side=zs); S.noObl = True
    r = poly_roots(poly) if sp.Poly(poly, x).discriminant() >= 0 else []
    if r is not None:
        S.xint = r; S.xhow = f"ដោយ ${e_}>0$ នោះ $f(x)=0$ សមមូល ${lt}=0$ ។"
    S.tans = [t for t in (0, 1, -1, 2, -2) if t not in S.crit]
    S.xr = (-5, 5)
    return S

def F_linplusexp():
    k = P(1, 1, -1); al = P(1, -1, 2, -2, 3, -3); be = rng.randint(-3, 4)
    mode = P("c0", "c0", "cl", "cl", "mono")
    if mode == "c0":
        x0 = sp.Integer(0); w = sp.Integer(1)
    elif mode == "cl":
        w = sp.Integer(P(2, 3)) if k == 1 else R(1, P(2, 3)) if False else sp.Integer(P(2, 3))
        x0 = ln(w) / k
    if mode == "mono":
        ga = P(1, 2, 3, -1, -2) * (1 if al > 0 else -1) * k
        S_c = []
    else:
        ga = -al / (k * w); S_c = [x0]
    f = al * x + be + ga * exp(k * x)
    if sp.Rational(ga).q > 3: return None
    S = St(f, "lin_plus_exp", "exponential_oblique_asymptote", key=str((al, be, ga, k)))
    e_ = _ek(k)
    S.Ddoc = "អនុគមន៍ $f$ កំណត់គ្រប់ $x\\in IR$ ព្រោះ $e^{x}$ មានន័យគ្រប់ចំនួនពិត ។"
    d = al + ga * k * exp(k * x)
    S.fp = d; S.fptex = tx(al) + ("+" if ga * k > 0 else "-") + (tx(abs(ga * k)) if abs(ga * k) != 1 else "") + e_
    S.dsteps = [P(f"ដោយ $(e^{{u}})'=u'e^{{u}}$ គេបាន ៖", f"ដេរីវេតាមតួនីមួយៗ ដោយប្រើ $(e^{{u}})'=u'e^{{u}}$ ៖") + f"\n$$f'(x)={S.fptex}$$"]
    S.crit = S_c
    if mode == "mono":
        S.sgn = f"ដោយ ${e_}>0$ ហើយ ${tx(al)}$ និង ${tx(ga*k)}$ មានសញ្ញាដូចគ្នា នោះ $f'(x)$ មានសញ្ញាដូច ${tx(al)}$ ជានិច្ច ។"
    else:
        ww = -al / (ga * k)
        grow = (ga * k > 0)
        pos_side = ("x>" if (grow == (k > 0)) else "x<") + tx(x0)
        neg_side = ("x<" if (grow == (k > 0)) else "x>") + tx(x0)
        S.zero = f"$f'(x)=0$ សមមូល ${e_}={tx(ww)}$ ឬ $x={tx(x0)}$ ។"
        S.sgn = f"ដោយ ${e_}$ ជាអនុគមន៍{'កើន' if k>0 else 'ចុះ'} គេបាន $f'(x)>0$ ចំពោះ ${pos_side}$ និង $f'(x)<0$ ចំពោះ ${neg_side}$ ។"
    zs = -oo if k > 0 else oo; big = -zs
    S.lim(zs, None, (oo if al > 0 else -oo) * (1 if zs == oo else -1), f"ដោយ ${limtex(zs)}{e_}=0$")
    S.lim(big, None, oo if ga > 0 else -oo, f"សរសេរ $f(x)={e_}\\left[{tx(ga)}+({tx(al*x+be)}){tx(exp(-k*x))}\\right]$ ហើយ ${limtex(big)}({tx(al*x+be)}){tx(exp(-k*x))}=0$")
    S.L.sort(key=lambda d_: d_["pt"] == oo)
    S.asym("o", f"y={tx(al*x+be)}", f"$${limtex(zs)}[f(x)-({tx(al*x+be)})]={limtex(zs)}{tx(ga*exp(k*x))}=0$$", al * x + be, side=zs)
    S.pos = dict(dtex=tx(ga * exp(k * x)), cases=[("x\\in IR", ga > 0)], eq=f"y={tx(al*x+be)}", chk=[(0, ga > 0), (1, ga > 0)], lin=al * x + be)
    S.tans = [t for t in (0, 1, -1) if t not in S_c]
    S.fpp = ga * k * k * exp(k * x)
    S.xr = (-4, 4)
    return S

def F_e2x():
    m_ = P(1, 2, 3, 4); d = P(1, 2, 3); r, s_ = m_ - d, m_ + d
    sc = P(1, 1, -1, 2, R(1, 2))
    f = sc * (exp(x) - r) * (exp(x) - s_)
    fe = sc * (exp(2 * x) - (r + s_) * exp(x) + r * s_)
    S = St(fe, "e2x", "exponential_quadratic_in_exp", key=str((r, s_, sc)))
    S.Ddoc = "អនុគមន៍នេះកំណត់គ្រប់ $x\\in IR$ ។"
    x0 = ln(sp.Integer(m_))
    S.fp = 2 * sc * exp(x) * (exp(x) - m_)
    S.fptex = cf(2 * sc, f"e^{{x}}(e^{{x}}-{m_})")
    S.dsteps = [f"ដោយ $(e^{{2x}})'=2e^{{2x}}$ គេបាន ៖\n$$f'(x)={tx(sc*2*exp(2*x))}{tx(-sc*(r+s_)*exp(x)) if tx(-sc*(r+s_)*exp(x)).startswith('-') else '+'+tx(-sc*(r+s_)*exp(x))}={S.fptex}$$"]
    S.sgn = f"ដោយ $e^{{x}}>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${cf(2*sc, f'(e^{{x}}-{m_})')}$ ។" if sc != 1 else f"ដោយ $2e^{{x}}>0$ នោះ $f'(x)$ មានសញ្ញាដូច $e^{{x}}-{m_}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល $e^{{x}}={m_}$ ឬ $x={tx(x0)}$ ។"
    S.crit = [x0]
    S.lim(-oo, None, sc * r * s_, "ដោយ $\\lim_{x\\to-\\infty}e^{x}=0$")
    S.lim(oo, None, oo if sc > 0 else -oo, "សរសេរ $f(x)=" + cf(sc, "e^{2x}(1" + sterm(-(r + s_), "e^{-x}") + sterm(r * s_, "e^{-2x}") + ")") + "$")
    S.asym("h", f"y={tx(sc*r*s_)}", "h", sc * r * s_, side=-oo); S.noObl = True
    xs = [ln(sp.Integer(v)) for v in (r, s_) if v > 0]
    S.xint = sorted(xs, key=num)
    S.xhow = f"តាង $t=e^{{x}}>0$ សមីការក្លាយជា $(t-{r})(t-{s_})=0$ ។".replace("(t-0)", "t").replace("t--", "t+")
    if r < 0: S.xhow = S.xhow.replace(f"(t-{r})", f"(t+{-r})") + f" ឫស $t={r}<0$ មិនយក ។"
    S.tans = [0] if 0 != x0 else [1]
    S.xr = (-4, 3)
    return S

def F_expquot():
    p = rng.randint(-3, 3); a = P(1, -1, 2, -2, 3); k = P(1, 1, -1)
    f = a * exp(k * x) / (x - p)
    S = St(f, "exp_quot", "exponential_quotient", key=str((p, a, k)))
    e_ = _ek(k); dt = tx(x - p)
    S.ftex = f"f(x)=\\frac{{{tx(a*exp(k*x))}}}{{{dt}}}"
    S.nd = (a * exp(k * x), x - p, tx(a * exp(k * x)), dt)
    S.holes = [sp.Integer(p)]; S.Dtex = f"D={IRS}-\\{{{tx(p)}\\}}"
    S.Ddoc = f"$f$ មានន័យលុះត្រាតែ ${dt}\\neq 0$ ឬ $x\\neq {tx(p)}$ ។"
    x0 = p + (1 if k == 1 else -1)
    S.crit = [sp.Integer(x0)]
    u = k * (x - p) - 1
    S.fp = a * exp(k * x) * u / (x - p)**2
    S.fptex = f"\\frac{{{cf(a, f'({tx(u)})')}{e_}}}{{({dt})^2}}"
    S.dsteps = [P("តាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ គេបាន ៖", "ប្រើរូបមន្តដេរីវេនៃផលចែក គេបាន ៖") + f"\n$$f'(x)=\\frac{{{tx(a*k*exp(k*x))}({dt})-{tx(a*exp(k*x))}}}{{({dt})^2}}={S.fptex}$$"]
    S.sgn = f"ដោយ ${e_}>0$ និង $({dt})^2>0$ លើ $D$ នោះ $f'(x)$ មានសញ្ញាដូច ${cf(a, f'({tx(u)})')}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល ${tx(u)}=0$ ឬ $x={x0}$ ។"
    zs = -oo if k > 0 else oo; big = -zs
    S.lim(zs, None, sp.Integer(0), f"ដោយ ${limtex(zs)}{e_}=0$ និង ${limtex(zs)}({dt})=" + ("-\\infty" if zs == -oo else "+\\infty") + "$")
    sb = (1 if a > 0 else -1) * (1 if big == oo else -1)
    S.lim(big, None, oo if sb > 0 else -oo, f"តាមលីមីតគោល ${limtex(big)}\\frac{{{e_}}}{{{'x' if k>0 else '-x'}}}=+\\infty$")
    S.lim(sp.Integer(p), "-", -oo if a > 0 else oo); S.lim(sp.Integer(p), "+", oo if a > 0 else -oo)
    S.L.sort(key=lambda d: (d["pt"] == oo, d["pt"] != -oo))
    S.asym("v", f"x={tx(p)}", "v", x - p); S.asym("h", "y=0", "h", sp.Integer(0), side=zs); S.noObl = True
    S.xint = []; S.xhow = f"ដោយ ${tx(a*exp(k*x))}\\neq 0$ ជានិច្ច នោះសមីការ $f(x)=0$ គ្មានឫស ។"
    S.tans = [t for t in (p - 1, p + 1, p + 2, p - 2) if t != x0]
    S.xr = (p - 4, p + 4)
    return S

def F_logistic():
    a = P(1, 2, 3, -1, -2, 0); b = P(1, 2, -1, -2, 3, 4, 0); c = P(1, 1, 2, 3, -1, -2, -3)
    det = a * c - b
    if det == 0: return None
    if a == 0 and b == 0: return None
    N = a * exp(x) + b; Dn = exp(x) + c
    f = N / Dn
    S = St(f, "logistic", "exponential_rational_in_exp", key=str((a, b, c)))
    nt, dt = tx(N), tx(Dn)
    S.nd = (N, Dn, nt, dt)
    S.ftex = f"f(x)=\\frac{{{nt}}}{{{dt}}}"
    S.fp = det * exp(x) / Dn**2
    S.fptex = f"\\frac{{{tx(det*exp(x))}}}{{({dt})^2}}"
    S.dsteps = [P("តាមរូបមន្តដេរីវេនៃផលចែក ៖", "ប្រើ $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ ៖") + (f"\n$$f'(x)=\\frac{{{tx(a*exp(x))}({dt})-e^{{x}}({nt})}}{{({dt})^2}}={S.fptex}$$" if a else f"\n$$f'(x)={S.fptex}$$")]
    S.sgn = f"ដោយ $e^{{x}}>0$ និង $({dt})^2>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(det)}$ ជានិច្ច ។"
    S.lim(-oo, None, R(b, c), "ដោយ $\\lim_{x\\to-\\infty}e^{x}=0$")
    S.lim(oo, None, sp.Integer(a), f"ចែកភាគយកនិងភាគបែងនឹង $e^{{x}}$ ទទួលបាន $f(x)=\\frac{{{tx(a+b*exp(-x))}}}{{{tx(1+c*exp(-x))}}}$")
    S.asym("h", f"y={tx(R(b,c))}", "h", R(b, c), side=-oo); S.asym("h", f"y={a}", "h", sp.Integer(a), side=oo)
    S.noObl = True
    if c > 0:
        S.Ddoc = f"ដោយ ${dt}>0$ ជានិច្ច នោះ $f$ កំណត់គ្រប់ $x$ ។"
        hc = ln(sp.Integer(c)); S.center = (hc, (a + R(b, c)) / 2)
        S.center_lines = [f"ដោយ $e^{{{tx(2*hc)}-x}}=\\frac{{{c*c}}}{{e^{{x}}}}$ គេបាន $f({tx(2*hc-x)})=\\frac{{{tx(b*exp(x)+a*c*c)}}}{{{tx(c*(exp(x)+c))}}}$ ។".replace("e^{0-x}", "e^{-x}").replace("f(-x)", "f(-x)") ,
                          f"$$f({tx(2*hc-x)})+f(x)={tx(a+R(b,c))}$$"]
        S.tans = [0] if det else []
    else:
        h = ln(sp.Integer(-c)); S.holes = [h]
        S.Dtex = f"D={IRS}-\\{{{tx(h)}\\}}"
        S.Ddoc = f"$f$ មានន័យលុះត្រាតែ ${dt}\\neq 0$ ឬ $e^{{x}}\\neq {-c}$ គឺ $x\\neq {tx(h)}$ ។"
        nv = a * (-c) + b
        if nv == 0: return None
        S.lim(h, "-", -oo if nv > 0 else oo); S.lim(h, "+", oo if nv > 0 else -oo)
        S.L.sort(key=lambda d: (d["pt"] == oo, d["pt"] != -oo))
        S.asym("v", f"x={tx(h)}", "v", x - h)
        S.tans = [t for t in (1, -1, 2) if num(h) != t]
    if a != 0 and b * a < 0:
        S.xint = [ln(R(-b, a))]; S.xhow = f"$f(x)=0$ សមមូល ${nt}=0$ ឬ $e^{{x}}={tx(R(-b,a))}$ ។"
        if c < 0 and S.xint[0] == S.holes[0]: return None
    else:
        S.xint = []; S.xhow = f"ភាគយក ${nt}\\neq 0$ ជានិច្ច ។" if a == 0 else f"សមីការ ${nt}=0$ គ្មានឫសទេ ព្រោះ $e^{{x}}>0$ ។"
    S.xr = (-5, 5)
    return S

def F_auxexp():
    b = P(1, 0, -1, -2, -3); be = rng.randint(-3, 3)
    f = x + be + (x + b) * exp(-x)
    S = St(f, "aux_exp", "exponential_auxiliary_function", key=str((b, be)))
    lt = tx(x + b)
    S.ftex = f"f(x)={tx(x+be)}+({lt})e^{{-x}}"
    S.Ddoc = "អនុគមន៍ $f$ កំណត់គ្រប់ $x\\in IR$ ។"
    g = exp(x) - x + 1 - b
    gt = tx(g)
    S.aux = dict(g=g, ask=f"គេឱ្យអនុគមន៍ $g(x)={gt}$ ។ សិក្សាអថេរភាពនៃ $g$ រួចទាញបញ្ជាក់ថា $g(x)>0$ គ្រប់ $x\\in IR$ ។",
                 sol=f"$g'(x)=e^{{x}}-1$ ។ $g'(x)=0$ សមមូល $x=0$ ។ ចំពោះ $x<0$ គេបាន $g'(x)<0$ ហើយចំពោះ $x>0$ គេបាន $g'(x)>0$ ។ ដូច្នេះ $g$ ចុះលើ $(-\\infty;0)$ កើនលើ $(0;+\\infty)$ ហើយមានអប្បបរមា $g(0)={tx(2-b)}$ ។\nដោយ $g(0)={tx(2-b)}>0$ នោះ $g(x)\\ge g(0)>0$ គ្រប់ $x\\in IR$ ។",
                 chk=[check(f"subs({s(g)},x,0)", s(2 - b), "g min"), check(f"diff({s(g)},x)", "exp(x)-1", "g'")])
    S.fp = g * exp(-x)
    S.fptex = f"({gt})e^{{-x}}"
    S.dsteps = [f"តាមរូបមន្ត $(uv)'=u'v+uv'$ គេបាន ៖\n$$f'(x)=1+e^{{-x}}-({lt})e^{{-x}}=e^{{-x}}(e^{{x}}+1-x{sconst(-b)})$$" + f"\n$$f'(x)=e^{{-x}}g(x)$$"]
    S.sgn = "ដោយ $e^{-x}>0$ និង $g(x)>0$ គ្រប់ $x$ នោះ $f'(x)>0$ ។"
    S.lim(-oo, None, -oo, f"សរសេរ $f(x)=e^{{-x}}[({tx(x+be)})e^{{x}}+{lt}]$ ហើយ $\\lim_{{x\\to-\\infty}}({tx(x+be)})e^{{x}}=0$")
    S.lim(oo, None, oo, "ដោយ $\\lim_{x\\to+\\infty}xe^{-x}=0$ និង $\\lim_{x\\to+\\infty}e^{-x}=0$")
    S.asym("o", f"y={tx(x+be)}", f"$$\\lim_{{x\\to+\\infty}}[f(x)-({tx(x+be)})]=\\lim_{{x\\to+\\infty}}({lt})e^{{-x}}=0$$", x + be, side=oo)
    S.pos = dict(dtex=f"({lt})e^{{-x}}", cases=[(f"x<{tx(-b)}", False), (f"x>{tx(-b)}", True)], eq=f"y={tx(x+be)}", chk=[(-b - 1, False), (-b + 1, True)], lin=x + be, cross=-b)
    S.tans = [0, 1]
    S.xr = (-3, 5)
    return S

def F_gauss():
    a = P(-1, -1, 1, R(-1, 2), R(1, 2)); p = rng.randint(-3, 3); c = rng.randint(-2, 2); A = P(1, 1, 2, 3)
    u = sp.expand(a * (x - p)**2 + c)
    f = A * exp(u)
    S = St(f, "gauss", "exponential_composite", key=str((a, p, c, A)))
    ut = tx(u)
    S.ftex = f"f(x)={tx(A) if A!=1 else ''}e^{{{ut}}}"
    S.Ddoc = "អនុគមន៍នេះកំណត់គ្រប់ចំនួនពិត $x$ ។"
    du = sp.diff(u, x)
    S.fp = A * du * exp(u); S.fptex = cf(A, f"({tx(du)})") + f"e^{{{ut}}}"
    S.dsteps = [f"ប្រើរូបមន្តអនុគមន៍បណ្ដាក់ $(e^{{u}})'=u'e^{{u}}$ ជាមួយ $u={ut}$ គេបាន $u'={tx(du)}$ ។\n$$f'(x)={S.fptex}$$"]
    S.sgn = f"ដោយ $e^{{{ut}}}>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(du)}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល ${tx(du)}=0$ ឬ $x={tx(p)}$ ។"
    S.crit = [sp.Integer(p)]
    v = sp.Integer(0) if a < 0 else oo
    w = f"ដោយ $\\lim_{{x\\to\\pm\\infty}}({ut})={'-' if a<0 else '+'}\\infty$"
    S.lim(-oo, None, v, w); S.lim(oo, None, v, w)
    if a < 0:
        S.asym("h", "y=0", "h", sp.Integer(0))
    else:
        S.noAsym = True
    S.xint = []; S.xhow = "ដោយ $e^{u}>0$ ជានិច្ច នោះសមីការ $f(x)=0$ គ្មានឫស ។"
    S.tans = [t for t in (p - 1, p + 1) ]
    S.xr = (p - 4, p + 4)
    return S

# ---- logarithm ----
LOD = "D=(0;+\\infty)"
LDOC = "អនុគមន៍ $f$ មានន័យលុះត្រាតែ $x>0$ ។"

def _lnbase(S):
    S.lo = sp.Integer(0); S.Dtex = LOD; S.Ddoc = LDOC

def F_linln():
    a = P(1, -1, 2, -2, 3, R(1, 2)); t = P(1, 2, 3, 4, sp.E, 1, 2); b = rng.randint(-4, 4)
    mono = rng.random() < 0.15
    c = (a * P(1, 2, 3)) if mono else -a * t
    if t == sp.E and not mono: c = -a * sp.E
    if t == sp.E and a != 1 and a != -1: return None
    f = a * x + b + c * ln(x)
    S = St(f, "lin_ln", "logarithm_linear_plus_ln", key=str((a, b, c)))
    _lnbase(S)
    S.fp = (a * x + c) / x
    S.fptex = f"\\frac{{{tx(a*x+c)}}}{{x}}"
    S.dsteps = [P("តាមរូបមន្ត $(\\ln x)'=\\frac{1}{x}$ គេបាន ៖", "ដោយ $(\\ln x)'=\\frac{1}{x}$ គេបាន ៖") + f"\n$$f'(x)={tx(a)}{'+' if tx(c/x)[0]!='-' else ''}{tx(c/x)}={S.fptex}$$"]
    S.sgn = f"ដោយ $x>0$ លើ $D$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(a*x+c)}$ ។"
    if not mono:
        S.crit = [t]; S.zero = f"$f'(x)=0$ សមមូល ${tx(a*x+c)}=0$ ឬ $x={tx(t)}$ ។"
    S.lim(sp.Integer(0), "+", (-oo if c > 0 else oo), "ដោយ $\\lim_{x\\to 0^{+}}\\ln x=-\\infty$")
    bigv = oo if a > 0 else -oo
    S.lim(oo, None, bigv, f"សរសេរ $f(x)=x\\left({tx(a)}{sfrac(b)}{sterm(c, chr(92) + 'frac{' + chr(92) + 'ln x}{x}')}\\right)$ ហើយ $\\lim_{{x\\to+\\infty}}\\frac{{\\ln x}}{{x}}=0$")
    S.asym("v", "x=0", "v", x); S.noH = True
    S.tans = [t_ for t_ in (1, 2, sp.E) if t_ != t]
    if a + b == 0: S.onepoint = 1
    S.fpp = -c / x**2
    S.xr = (0, 7)
    return S

def F_quadln():
    a = P(R(1, 2), 1, -1, 2, -R(1, 2)); p = P(1, 2, 3); q = p + P(0, 1, 2, 3); c = rng.randint(-3, 3)
    if p == q:
        # single critical point: a x^2 + c + d ln x
        d = -2 * a * p * p; b_ = 0; cr = [p]
        Nn = 2 * a * (x**2 - p * p); fac = cf(2 * a, f"({lin(p)})({lin(-p)})")
    else:
        d = 2 * a * p * q; b_ = -2 * a * (p + q); cr = [p, q]
        Nn = 2 * a * (x - p) * (x - q); fac = cf(2 * a, f"({lin(p)})({lin(q)})")
    f = a * x**2 + b_ * x + c + d * ln(x)
    S = St(f, "quad_ln", "logarithm_quadratic_plus_ln", key=str((a, p, q, c)))
    _lnbase(S)
    S.crit = [sp.Integer(v) for v in cr]
    S.fp = Nn / x; S.fptex = f"\\frac{{{fac}}}{{x}}"
    S.dsteps = [f"ដេរីវេតាមតួនីមួយៗ ដោយ $(\\ln x)'=\\frac{{1}}{{x}}$ ៖\n$$f'(x)={tx(2*a*x+b_)}{'+' if d>0 else '-'}\\frac{{{abs(d)}}}{{x}}=\\frac{{{tx(sp.expand(Nn))}}}{{x}}={S.fptex}$$"]
    S.sgn = f"ដោយ $x>0$ នោះ $f'(x)$ មានសញ្ញាដូចភាគយក ${fac}$ ។"
    S.zero = "ភាគយកស្មើសូន្យត្រង់ " + " ឬ ".join(f"$x={tx(v)}$" for v in cr) + " (យកតែឫសក្នុង $D$) ។"
    S.lim(sp.Integer(0), "+", -oo if d > 0 else oo, "ដោយ $\\lim_{x\\to 0^{+}}\\ln x=-\\infty$")
    S.lim(oo, None, oo if a > 0 else -oo, f"ដោយ $\\lim_{{x\\to+\\infty}}\\frac{{\\ln x}}{{x^2}}=0$ នោះ $f(x)$ មានលីមីតដូច ${tx(a*x**2)}$")
    S.asym("v", "x=0", "v", x); S.noH = True
    S.tans = [t for t in (1, 2, 3, 4) if t not in cr]
    S.xr = (0, q + 3)
    return S

def F_lnoverx():
    a = P(1, -1, 2, -2, 3); L = P(0, 1, 2, -1, 1, R(1, 2)); c = P(0, 0, 0, 1, -1, 2)
    b = a - a * L
    f = (a * ln(x) + b) / x + c
    x0 = exp(L)
    S = St(f, "ln_over_x", "logarithm_ln_over_x", key=str((a, L, c)))
    _lnbase(S)
    nt = tx(a * ln(x) + b)
    S.ftex = f"f(x)=\\frac{{{nt}}}{{x}}" + (("+" if c > 0 else "-") + str(abs(c)) if c else "")
    u = a - b - a * ln(x)
    S.fp = u / x**2; S.fptex = f"\\frac{{{tx(u)}}}{{x^2}}"
    S.dsteps = [P("តាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ គេបាន ៖", "អនុវត្តរូបមន្តផលចែកជាមួយ $(\\ln x)'=\\frac{1}{x}$ ៖") + f"\n$$f'(x)=\\frac{{\\frac{{{tx(a)}}}{{x}}\\cdot x-({nt})}}{{x^2}}={S.fptex}$$"]
    S.sgn = f"ដោយ $x^2>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(u)}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល $\\ln x={tx(L)}$ ឬ $x={tx(x0)}$ ។"
    S.crit = [x0]
    S.lim(sp.Integer(0), "+", -oo if a > 0 else oo, "ដោយ $\\lim_{x\\to 0^{+}}\\ln x=-\\infty$ និង $\\lim_{x\\to 0^{+}}\\frac{1}{x}=+\\infty$")
    S.lim(oo, None, sp.Integer(c), "ដោយ $\\lim_{x\\to+\\infty}\\frac{\\ln x}{x}=0$")
    S.asym("v", "x=0", "v", x); S.asym("h", f"y={c}", "h", sp.Integer(c)); S.noObl = True
    if c == 0:
        S.xint = [exp(-R(b, 1) / a)]; S.xhow = f"$f(x)=0$ សមមូល ${nt}=0$ ឬ $\\ln x={tx(-R(b,1)/a)}$ ។"
    S.tans = [t for t in (1, sp.E) if t != x0]
    S.xr = (0, 9)
    return S

def F_lnoverx2():
    a = P(1, 2, -1, -2, 4, 3); c = P(0, 0, 1, -1)
    f = a * ln(x) / x**2 + c
    S = St(f, "ln_over_x2", "logarithm_ln_over_x_squared", key=str((a, c)))
    _lnbase(S)
    S.ftex = f"f(x)=\\frac{{{tx(a*ln(x))}}}{{x^2}}" + (("+" if c > 0 else "-") + str(abs(c)) if c else "")
    S.fp = a * (1 - 2 * ln(x)) / x**3
    S.fptex = f"\\frac{{{cf(a, '(1-2\\ln x)')}}}{{x^3}}"
    S.dsteps = [f"តាមរូបមន្តផលចែក គេបាន ៖\n$$f'(x)=\\frac{{\\frac{{{tx(a)}}}{{x}}\\cdot x^2-{tx(a*ln(x))}\\cdot 2x}}{{x^4}}={S.fptex}$$"]
    S.sgn = f"ដោយ $x^3>0$ លើ $D$ នោះ $f'(x)$ មានសញ្ញាដូច ${cf(a, '(1-2\\ln x)')}$ ។"
    x0 = exp(R(1, 2)); S.crit = [x0]
    S.zero = f"$f'(x)=0$ សមមូល $\\ln x=\\frac{{1}}{{2}}$ ឬ $x=\\sqrt{{e}}$ ។"
    S.lim(sp.Integer(0), "+", -oo if a > 0 else oo, "ដោយ $\\lim_{x\\to 0^{+}}\\ln x=-\\infty$ និង $\\lim_{x\\to 0^{+}}\\frac{1}{x^2}=+\\infty$")
    S.lim(oo, None, sp.Integer(c), "ដោយ $\\lim_{x\\to+\\infty}\\frac{\\ln x}{x^2}=0$")
    S.asym("v", "x=0", "v", x); S.asym("h", f"y={c}", "h", sp.Integer(c)); S.noObl = True
    if c == 0:
        S.xint = [sp.Integer(1)]; S.xhow = "$f(x)=0$ សមមូល $\\ln x=0$ ។"
    S.tans = [1]
    S.xr = (0, 6)
    return S

def F_xlnx():
    a = P(1, -1, 2, -2, 3); L = P(-1, 0, 1, 2); c = rng.randint(-3, 3)
    b = -a * (L + 1)
    f = a * x * ln(x) + b * x + c
    S = St(f, "x_ln_x", "logarithm_x_ln_x", key=str((a, L, c)))
    _lnbase(S)
    S.fp = a * ln(x) + a + b
    S.fptex = tx(a * ln(x) + a + b)
    S.dsteps = [f"តាមរូបមន្ត $(uv)'=u'v+uv'$ គេបាន $(x\\ln x)'=\\ln x+1$ ។\n$$f'(x)={cf(a, '(' + chr(92) + 'ln x+1)')}{sconst(b)}={S.fptex}$$"]
    x0 = exp(L); S.crit = [x0]
    S.zero = f"$f'(x)=0$ សមមូល $\\ln x={L}$ ឬ $x={tx(x0)}$ ។"
    S.sgn = f"ដោយ $\\ln x$ ជាអនុគមន៍កើន នោះ ${tx(ln(x)-L)}>0$ ចំពោះ $x>{tx(x0)}$ និង ${tx(ln(x)-L)}<0$ ចំពោះ $0<x<{tx(x0)}$ ។ ដូច្នេះ $f'(x)$ មានសញ្ញាដូច ${cf(a, ('(' + tx(ln(x)-L) + ')') if L else tx(ln(x)))}$ ។"
    S.lim(sp.Integer(0), "+", sp.Integer(c), "ដោយ $\\lim_{x\\to 0^{+}}x\\ln x=0$")
    S.lim(oo, None, oo if a > 0 else -oo, f"សរសេរ $f(x)=x({tx(a*ln(x)+b)}){sconst(c)}$")
    S.noAsym = True
    if c == 0:
        S.xint = [exp(L + 1)]; S.xhow = f"$f(x)=0$ សមមូល $x({tx(a*ln(x)+b)})=0$ ។ ដោយ $x>0$ គេបាន $\\ln x={L+1}$ ។"
    S.tans = [t for t in (1, sp.E, sp.E**2) if t != x0]
    S.fpp = R(1) * a / x
    S.xr = (0, 8)
    return S

def F_ln2():
    a = P(1, 1, -1, 2, -2); u = rng.randint(-2, 2); v = u + P(2, 4, 2)
    f = sp.expand(a * (ln(x) - u) * (ln(x) - v))
    S = St(f, "ln_sq", "logarithm_quadratic_in_ln", key=str((a, u, v)))
    _lnbase(S)
    m_ = R(u + v, 2)
    S.fp = 2 * a * (ln(x) - m_) / x
    S.fptex = f"\\frac{{{tx(sp.expand(2*a*(ln(x)-m_)))}}}{{x}}"
    S.dsteps = [f"ដោយ $(\\ln^2 x)'=2\\ln x\\cdot\\frac{{1}}{{x}}$ គេបាន ៖\n$$f'(x)={S.fptex}$$"]
    x0 = exp(m_); S.crit = [x0]
    S.sgn = f"ដោយ $x>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(sp.expand(2*a*(ln(x)-m_)))}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល $\\ln x={tx(m_)}$ ឬ $x={tx(x0)}$ ។"
    w = "តាង $t=\\ln x$ ពេល $x\\to 0^{+}$ នោះ $t\\to-\\infty$"
    S.lim(sp.Integer(0), "+", oo if a > 0 else -oo, w)
    S.lim(oo, None, oo if a > 0 else -oo, "តាង $t=\\ln x$ ពេល $x\\to+\\infty$ នោះ $t\\to+\\infty$")
    S.asym("v", "x=0", "v", x); S.noH = True
    S.xint = [exp(u), exp(v)]
    S.xhow = f"តាង $t=\\ln x$ សមីការក្លាយជា ${cf(a, f'({lin(u,chr(116))})({lin(v,chr(116))})')}=0$ ឬ $t={u}$ ឬ $t={v}$ ។"
    S.tans = [t for t in (1, sp.E) if t != x0]
    S.xr = (0, 9)
    return S

def F_auxln():
    al = P(1, 1, 2, R(1, 2), 3); be = rng.randint(-3, 3); b = P(0, 1, 2, -1, -2, 1) * (2 if al == 3 else 1)
    if al == R(1, 2) and b >= R(3, 2): return None
    if b >= 3 * al: return None
    f = al * x + be + (2 * al * ln(x) + b) / x
    S = St(f, "aux_ln", "logarithm_auxiliary_function", key=str((al, be, b)))
    _lnbase(S)
    nt = tx(2 * al * ln(x) + b)
    S.ftex = f"f(x)={tx(al*x+be)}+\\frac{{{nt}}}{{x}}"
    g = al * x**2 + 2 * al - b - 2 * al * ln(x)
    gt = tx(g)
    S.aux = dict(g=g, ask=f"គេឱ្យអនុគមន៍ $g$ កំណត់លើ $(0;+\\infty)$ ដោយ $g(x)={gt}$ ។ សិក្សាអថេរភាពនៃ $g$ រួចទាញបញ្ជាក់ថា $g(x)>0$ គ្រប់ $x>0$ ។",
                 sol=f"$g'(x)={tx(2*al*x)}-\\frac{{{tx(2*al)}}}{{x}}=\\frac{{{tx(2*al)}(x^2-1)}}{{x}}$ ។ លើ $(0;+\\infty)$ សមីការ $g'(x)=0$ មានឫស $x=1$ ។ ចំពោះ $0<x<1$ គេបាន $g'(x)<0$ ហើយចំពោះ $x>1$ គេបាន $g'(x)>0$ ។ ដូច្នេះ $g$ មានអប្បបរមា $g(1)={tx(3*al-b)}$ ។\nដោយ $g(1)={tx(3*al-b)}>0$ នោះ $g(x)\\ge g(1)>0$ គ្រប់ $x>0$ ។",
                 chk=[check(f"subs({s(g)},x,1)", s(3 * al - b), "g min"), check(f"subs(diff({s(g)},x),x,1)", "0", "g'(1)")])
    S.fp = g / x**2; S.fptex = f"\\frac{{{gt}}}{{x^2}}"
    S.dsteps = [f"តាមរូបមន្ត $\\left(\\frac{{u}}{{v}}\\right)'=\\frac{{u'v-uv'}}{{v^2}}$ គេបាន ៖\n$$\\left(\\frac{{{nt}}}{{x}}\\right)'=\\frac{{{tx(2*al)}-({nt})}}{{x^2}}$$\nដូច្នេះ ៖\n$$f'(x)={tx(al)}+\\frac{{{tx(2*al)}-({nt})}}{{x^2}}=\\frac{{g(x)}}{{x^2}}={S.fptex}$$"]
    S.sgn = "ដោយ $x^2>0$ និង $g(x)>0$ នោះ $f'(x)>0$ គ្រប់ $x\\in D$ ។"
    S.lim(sp.Integer(0), "+", -oo, f"ដោយ $\\lim_{{x\\to 0^{{+}}}}({nt})=-\\infty$ និង $\\lim_{{x\\to 0^{{+}}}}\\frac{{1}}{{x}}=+\\infty$")
    S.lim(oo, None, oo, "ដោយ $\\lim_{x\\to+\\infty}\\frac{\\ln x}{x}=0$ និង $\\lim_{x\\to+\\infty}\\frac{1}{x}=0$")
    S.asym("v", "x=0", "v", x)
    S.asym("o", f"y={tx(al*x+be)}", f"$$\\lim_{{x\\to+\\infty}}[f(x)-({tx(al*x+be)})]=\\lim_{{x\\to+\\infty}}\\frac{{{nt}}}{{x}}=0$$", al * x + be, side=oo)
    xc = exp(-R(b) / (2 * al))
    S.pos = dict(dtex=f"\\frac{{{nt}}}{{x}}", cases=[(f"0<x<{tx(xc)}", False), (f"x>{tx(xc)}", True)], eq=f"y={tx(al*x+be)}", chk=[(xc / 2, False), (xc * 2, True)], lin=al * x + be, cross=xc)
    xp = exp(1 - R(b) / (2 * al))
    S.extra_fu = ["par_asym"]; S.par = dict(x=xp, al=al, nt=nt, b=b, g=g)
    S.tans = [1, sp.E]
    S.xr = (0, 7)
    return S

def F_lnquad():
    p = rng.randint(-3, 3); q2 = P(1, 1, 2, 4, 3, 9); a = P(1, 1, 2, -1); c = P(0, 0, 1, -1)
    w = sp.expand((x - p)**2 + q2)
    f = a * ln(w) + c
    S = St(f, "ln_quad", "logarithm_composite_quadratic", key=str((p, q2, a, c)))
    wt = tx(w)
    S.ftex = f"f(x)={cf(a, f'\\ln({wt})')}" + (("+" if c > 0 else "-") + str(abs(c)) if c else "")
    S.Ddoc = f"ដោយ ${wt}=({lin(p)})^2+{q2}>0$ គ្រប់ $x$ នោះ $f$ កំណត់គ្រប់ $x\\in IR$ ។"
    du = sp.diff(w, x)
    S.fp = a * du / w
    S.fptex = f"\\frac{{{tx(sp.expand(a*du))}}}{{{wt}}}"
    S.dsteps = [f"តាមរូបមន្ត $(\\ln u)'=\\frac{{u'}}{{u}}$ ជាមួយ $u={wt}$ គេបាន ៖\n$$f'(x)={S.fptex}$$"]
    S.sgn = f"ដោយភាគបែង ${wt}>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(sp.expand(a*du))}$ ។"
    S.zero = f"$f'(x)=0$ សមមូល $x={tx(p)}$ ។"
    S.crit = [sp.Integer(p)]
    v = oo if a > 0 else -oo
    wy = f"ដោយ $\\lim_{{x\\to\\pm\\infty}}({wt})=+\\infty$"
    S.lim(-oo, None, v, wy); S.lim(oo, None, v, wy)
    S.noAsym = True
    S.tans = [t for t in (p - 1, p + 1)]
    S.xr = (p - 5, p + 5)
    return S

def F_lnlin():
    al = sp.Rational(P(-1, -1, R(-1, 2), R(-1, 3), 1, 2)); p = rng.randint(-3, 3); be = rng.randint(-2, 3); k = P(1, 1, 2)
    f = al * x + be + k * ln(x - p)
    S = St(f, "ln_lin", "logarithm_shifted_ln", key=str((al, be, p, k)))
    S.lo = sp.Integer(p); S.Dtex = f"D=({tx(p)};+\\infty)"
    S.Ddoc = f"$f$ មានន័យលុះត្រាតែ ${tx(x-p)}>0$ ឬ $x>{tx(p)}$ ។"
    dt = tx(x - p)
    u = sp.expand(al * (x - p) + k)
    S.fp = u / (x - p); S.fptex = f"\\frac{{{tx(u)}}}{{{dt}}}"
    S.dsteps = [f"ដោយ $(\\ln u)'=\\frac{{u'}}{{u}}$ គេបាន ៖\n$$f'(x)={tx(al)}+\\frac{{{k}}}{{{dt}}}={S.fptex}$$"]
    S.sgn = f"ដោយ ${dt}>0$ លើ $D$ នោះ $f'(x)$ មានសញ្ញាដូច ${tx(u)}$ ។"
    if al < 0:
        cr = p - k / al
        S.crit = [cr]; S.zero = f"$f'(x)=0$ សមមូល $x={tx(cr)}$ ។"
    S.lim(sp.Integer(p), "+", -oo, f"ដោយ $\\lim_{{x\\to {tx(p)}^{{+}}}}\\ln({dt})=-\\infty$".replace("x\\to -", "x\\to -"))
    S.lim(oo, None, oo if al > 0 else -oo, f"ដោយ $\\lim_{{x\\to+\\infty}}\\frac{{\\ln({dt})}}{{x}}=0$ នោះ $f(x)$ មានលីមីតដូច ${tx(al*x)}$")
    S.asym("v", f"x={tx(p)}", "v", x - p); S.noH = True
    S.tans = [t for t in (p + 1, p + 2) if t not in S.crit]
    S.xr = (p, p + 8)
    return S

def F_lnratio():
    p = rng.randint(-4, 2); q = p + P(1, 2, 3, 4); c = P(0, 0, 1, -1, 2); inc = P(True, False)
    n, d = ((x - q), (x - p)) if inc else ((x - p), (x - q))
    f = ln(n / d) + c
    S = St(f, "ln_ratio", "logarithm_rational_argument", key=str((p, q, c, inc)))
    S.ftex = f"f(x)=\\ln\\frac{{{tx(n)}}}{{{tx(d)}}}" + (("+" if c > 0 else "-") + str(abs(c)) if c else "")
    S.gap = (sp.Integer(p), sp.Integer(q))
    S.Dtex = f"D=(-\\infty;{tx(p)})\\cup({tx(q)};+\\infty)"
    S.Ddoc = f"$f$ មានន័យលុះត្រាតែ $\\frac{{{tx(n)}}}{{{tx(d)}}}>0$ ។ ផលចែកនេះវិជ្ជមានលុះត្រាតែ $x<{tx(p)}$ ឬ $x>{tx(q)}$ ។"
    det = (q - p) if inc else (p - q)
    S.fp = det / ((x - p) * (x - q))
    S.fptex = f"\\frac{{{det}}}{{({tx(x-p)})({tx(x-q)})}}"
    S.dsteps = [f"លើ $D$ យើងប្រើ $(\\ln u)'=\\frac{{u'}}{{u}}$ ជាមួយ $u=\\frac{{{tx(n)}}}{{{tx(d)}}}$ ។ គេបាន $u'=\\frac{{{tx(d)}-({tx(n)})}}{{({tx(d)})^2}}=\\frac{{{det}}}{{({tx(d)})^2}}$ ។\n$$f'(x)=\\frac{{u'}}{{u}}={S.fptex}$$"]
    S.sgn = f"លើ $D$ ផលគុណ $({tx(x-p)})({tx(x-q)})>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${det}$ ជានិច្ច ។"
    w = f"ដោយ $\\lim_{{x\\to\\pm\\infty}}\\frac{{{tx(n)}}}{{{tx(d)}}}=1$ និង $\\ln 1=0$"
    S.lim(-oo, None, sp.Integer(c), w); S.lim(oo, None, sp.Integer(c), w)
    fr = f"\\frac{{{tx(n)}}}{{{tx(d)}}}"
    S.lim(sp.Integer(p), "-", -oo if not inc else oo, f"ដោយ ${limtex(sp.Integer(p), '-')}{fr}={'+' + chr(92) + 'infty' if inc else '0^{+}'}$")
    S.lim(sp.Integer(q), "+", oo if not inc else -oo, f"ដោយ ${limtex(sp.Integer(q), '+')}{fr}={'0^{+}' if inc else '+' + chr(92) + 'infty'}$")
    S.L.sort(key=lambda d_: (d_["pt"] == oo, d_["pt"] != -oo))
    S.asym("v", f"x={tx(p)}", "v", x - p); S.asym("v", f"x={tx(q)}", "v", x - q); S.asym("h", f"y={c}", "h", sp.Integer(c))
    h = R(p + q, 2)
    S.center = (h, sp.Integer(c))
    S.center_lines = [f"$$f({tx(2*h-x)})=\\ln\\frac{{{tx(sp.expand(n.subs(x,2*h-x)))}}}{{{tx(sp.expand(d.subs(x,2*h-x)))}}}" + (("+" if c > 0 else "-") + str(abs(c)) if c else "") + "$$",
                      f"ដោយ $\\frac{{{tx(sp.expand(n.subs(x,2*h-x)))}}}{{{tx(sp.expand(d.subs(x,2*h-x)))}}}=\\frac{{{tx(d)}}}{{{tx(n)}}}$ នោះ $\\ln\\frac{{{tx(d)}}}{{{tx(n)}}}=-\\ln\\frac{{{tx(n)}}}{{{tx(d)}}}$ ។\n$$f({tx(2*h-x)})+f(x)={2*c}$$"]
    if c != 0:
        pass
    S.xint = None
    S.tans = [q + 1, p - 1]
    S.xr = (p - 5, q + 5)
    return S

def F_xoverln():
    a = P(1, 2, 3, -1, -2, R(1, 2), 4, -3)
    f = a * x / ln(x)
    S = St(f, "x_over_ln", "logarithm_x_over_ln", key=str(a))
    S.lo = sp.Integer(0); S.holes = [sp.Integer(1)]
    S.Dtex = "D=(0;1)\\cup(1;+\\infty)"
    S.Ddoc = "$f$ មានន័យលុះត្រាតែ $x>0$ និង $\\ln x\\neq 0$ ឬ $x\\neq 1$ ។"
    S.nd = (a * x, ln(x), tx(a * x), "\\ln x")
    S.ftex = f"f(x)=\\frac{{{tx(a*x)}}}{{\\ln x}}"
    S.fp = a * (ln(x) - 1) / ln(x)**2
    S.fptex = f"\\frac{{{cf(a, '(\\ln x-1)')}}}{{\\ln^2 x}}"
    S.dsteps = [f"តាមរូបមន្តផលចែក គេបាន ៖\n$$f'(x)=\\frac{{{tx(a)}\\ln x-{tx(a*x)}\\cdot\\frac{{1}}{{x}}}}{{\\ln^2 x}}={S.fptex}$$"]
    S.sgn = f"ដោយ $\\ln^2 x>0$ លើ $D$ នោះ $f'(x)$ មានសញ្ញាដូច ${cf(a, '(\\ln x-1)')}$ ។"
    S.zero = "$f'(x)=0$ សមមូល $\\ln x=1$ ឬ $x=e$ ។"
    S.crit = [sp.E]
    S.lim(sp.Integer(0), "+", sp.Integer(0), "ដោយ $\\lim_{x\\to 0^{+}}\\ln x=-\\infty$")
    S.lim(sp.Integer(1), "-", -oo if a > 0 else oo); S.lim(sp.Integer(1), "+", oo if a > 0 else -oo)
    S.lim(oo, None, oo if a > 0 else -oo, "ដោយ $\\lim_{x\\to+\\infty}\\frac{x}{\\ln x}=+\\infty$")
    S.asym("v", "x=1", "v", x - 1); S.noH = True
    S.xint = []; S.xhow = "លើ $D$ ភាគយកខុសពីសូន្យ ដូច្នេះ $f(x)=0$ គ្មានឫស ។"
    S.tans = [sp.E**2, sp.Integer(2)] if False else [sp.E**2]
    S.xr = (0, 9)
    return S

def F_lninv():
    sc = P(1, 1, -1, 2, 3); a = P(1, 2, 3, 4, -1, -2, sp.E); b = rng.randint(-3, 3)
    f = sc * (ln(x) + a / x + b)
    S = St(f, "ln_inv", "logarithm_ln_plus_reciprocal", key=str((sc, a, b)))
    _lnbase(S)
    S.ftex = f"f(x)={cf(sc, f'({tx(ln(x)+b)}' + ('+' if a>0 else '-') + f'\\frac{{{tx(abs(a))}}}{{x}})')}"
    S.fp = sc * (x - a) / x**2
    S.fptex = f"\\frac{{{cf(sc, f'({lin(a)})')}}}{{x^2}}"
    S.dsteps = [f"ដោយ $(\\ln x)'=\\frac{{1}}{{x}}$ និង $\\left(\\frac{{1}}{{x}}\\right)'=-\\frac{{1}}{{x^2}}$ គេបាន ៖\n$$f'(x)={cf(sc, '\\left(\\frac{1}{x}' + ('-' if a>0 else '+') + f'\\frac{{{tx(abs(a))}}}{{x^2}}' + '\\right)')}={S.fptex}$$"]
    S.sgn = f"ដោយ $x^2>0$ នោះ $f'(x)$ មានសញ្ញាដូច ${cf(sc, f'({lin(a)})')}$ ។"
    if a > 0:
        S.crit = [a]; S.zero = f"$f'(x)=0$ សមមូល $x={tx(a)}$ ។"
    S.lim(sp.Integer(0), "+", (oo if a > 0 else -oo) * (1 if sc > 0 else -1), f"សរសេរ $f(x)=\\frac{{{cf(sc, f'(x\\ln x+{tx(b*x+a)})')}}}{{x}}$ ហើយ $\\lim_{{x\\to 0^{{+}}}}x\\ln x=0$".replace("+-", "-"))
    S.lim(oo, None, oo if sc > 0 else -oo, "ដោយ $\\lim_{x\\to+\\infty}\\ln x=+\\infty$ និង $\\lim_{x\\to+\\infty}\\frac{1}{x}=0$")
    S.asym("v", "x=0", "v", x); S.noH = True
    S.tans = [t for t in (1, sp.E) if t != a]
    S.xr = (0, 9)
    return S

FAMS = [(F_cubic, 80), (F_quartic, 60), (F_homog, 30), (F_oblique, 95), (F_ratH, 30), (F_twoV, 45), (F_invsq, 25),
        (F_linexp, 70), (F_quadexp, 55), (F_linplusexp, 50), (F_e2x, 18), (F_expquot, 26), (F_logistic, 28), (F_auxexp, 30), (F_gauss, 22),
        (F_linln, 55), (F_quadln, 45), (F_lnoverx, 40), (F_lnoverx2, 10), (F_xlnx, 40), (F_ln2, 18), (F_auxln, 45), (F_lnquad, 20), (F_lnlin, 25), (F_lnratio, 25), (F_xoverln, 7), (F_lninv, 25)]

# =================== TABLE ENGINE ===================
def sgnval(v):
    return v

def fl(v):
    return math.inf if v == oo else -math.inf if v == -oo else num(v)

def getL(S, pt, side):
    for d in S.L:
        if d["pt"] == pt and d["side"] == side:
            return d["val"]
    raise KeyError((S.fam, pt, side))

def build(S):
    f = S.f
    S.dfun = sp.lambdify(x, sp.diff(f, x), "math")
    cols = []
    cols.append(dict(x=S.lo, t="lo") if S.lo is not None else dict(x=-oo, t="inf"))
    cols.append(dict(x=oo, t="inf"))
    for c in S.crit: cols.append(dict(x=c, t="crit"))
    for h in S.holes: cols.append(dict(x=h, t="excl"))
    if S.gap:
        cols.append(dict(x=S.gap[0], t="gl")); cols.append(dict(x=S.gap[1], t="gr"))
    cols.sort(key=lambda c: fl(c["x"]))
    for a_, b_ in zip(cols, cols[1:]):
        assert fl(a_["x"]) < fl(b_["x"]), "dup col"
    signs = []; tests = []
    for a_, b_ in zip(cols, cols[1:]):
        if a_["t"] == "gl":
            signs.append(None); tests.append(None); continue
        la, lb = fl(a_["x"]), fl(b_["x"])
        if not math.isfinite(la) and not math.isfinite(lb):
            t = 0.0
        else:
            t = (la + lb) / 2 if math.isfinite(la) and math.isfinite(lb) else (lb - 1 if not math.isfinite(la) else la + 1)
        t = sp.Rational(str(round(t, 2)))
        if not (la < float(t) < lb):
            t = sp.Rational(str(round((la + lb) / 2 if math.isfinite(lb) else la + 0.5, 4)))
        v = S.dfun(float(t))
        v2 = float(sp.N(S.fp.subs(x, t)))
        assert abs(v - v2) < 1e-6 * max(1, abs(v)), ("fp mismatch", S.fam, str(f))
        assert abs(v) > 1e-9, ("zero in interval", S.fam, str(f))
        signs.append("+" if v > 0 else "-"); tests.append(t)
    S.cols, S.signs, S.tests = cols, signs, tests
    vals = {}
    # column end values: (left value, right value)
    for i, c in enumerate(cols):
        if c["t"] == "inf":
            v = getL(S, c["x"], None); c["L"] = c["R"] = v
        elif c["t"] == "lo":
            c["L"] = None; c["R"] = getL(S, c["x"], "+")
        elif c["t"] == "crit":
            v = f.subs(x, c["x"])
            v = sp.expand(v) if not v.is_Rational else v
            c["L"] = c["R"] = c["v"] = v
        elif c["t"] == "excl":
            c["L"] = getL(S, c["x"], "-"); c["R"] = getL(S, c["x"], "+")
        elif c["t"] == "gl":
            c["L"] = getL(S, c["x"], "-"); c["R"] = None
        elif c["t"] == "gr":
            c["L"] = None; c["R"] = getL(S, c["x"], "+")
    for i, sg in enumerate(signs):
        if sg is None: continue
        a_, b_ = fl(cols[i]["R"]), fl(cols[i + 1]["L"])
        assert (a_ < b_) == (sg == "+") and a_ != b_, ("table inconsistent", S.fam, str(f), a_, b_, sg)
    S.ext = []
    for i, c in enumerate(cols):
        if c["t"] == "crit":
            l, r = signs[i - 1], signs[i]
            kind = "max" if (l, r) == ("+", "-") else "min" if (l, r) == ("-", "+") else "stat"
            c["kind"] = kind
            S.ext.append((kind, c["x"], c["v"]))
    # table strings
    xr = []; fpr = [""] * (2 * len(cols) - 1); fv = [""] * (2 * len(cols) - 1)
    for i, c in enumerate(cols):
        xr.append(vt(c["x"]))
        t = c["t"]
        if t == "crit":
            fpr[2 * i] = "0"; fv[2 * i] = vt(c["v"])
        elif t == "inf":
            fv[2 * i] = vt(c["L"])
        elif t == "lo":
            fpr[2 * i] = "\\|"; fv[2 * i] = "\\|\\," + vt(c["R"])
        elif t == "excl":
            fpr[2 * i] = "\\|"; fv[2 * i] = vt(c["L"]) + "\\,\\|\\," + vt(c["R"])
        elif t == "gl":
            fpr[2 * i] = "\\|"; fv[2 * i] = vt(c["L"]) + "\\,\\|"
        elif t == "gr":
            fpr[2 * i] = "\\|"; fv[2 * i] = "\\|\\," + vt(c["R"])
        if i < len(cols) - 1:
            sg = signs[i]
            if sg is None:
                fpr[2 * i + 1] = "\\|"; fv[2 * i + 1] = "\\|"
            else:
                fpr[2 * i + 1] = sg; fv[2 * i + 1] = "\\nearrow" if sg == "+" else "\\searrow"
    S.table = variation_table(xr, fpr, fv)
    n = 2 * len(cols) - 1
    xs = []
    for i, c in enumerate(xr):
        xs.append(c)
        if i < len(xr) - 1: xs.append("")
    S.signtable = ("\\begin{array}{c|" + "c" * n + "}\nx & " + " & ".join(xs) + " \\\\\n\\hline\nf'(x) & " + " & ".join(fpr) + "\n\\end{array}")
    return S

def ivl(c1, c2):
    a_ = vt(c1["x"]); b_ = vt(c2["x"])
    return f"({a_};{b_})"

def mono_text(S):
    inc = [ivl(S.cols[i], S.cols[i + 1]) for i, g in enumerate(S.signs) if g == "+"]
    dec = [ivl(S.cols[i], S.cols[i + 1]) for i, g in enumerate(S.signs) if g == "-"]
    w = []
    if inc: w.append(P("$f$ កើនលើ ", "អនុគមន៍ $f$ កើនលើចន្លោះ ") + " និង ".join(f"${v}$" for v in inc))
    if dec: w.append(P("$f$ ចុះលើ ", "អនុគមន៍ $f$ ចុះលើចន្លោះ ") + " និង ".join(f"${v}$" for v in dec))
    return " ហើយ ".join(w) + " ។"

def ext_text(S):
    out = []
    for kind, c, v in S.ext:
        if kind == "max":
            out.append(P(f"អនុគមន៍មានអតិបរមាស្មើនឹង ${tx(v)}$ ត្រង់ $x={tx(c)}$ ។", f"$f$ មានតម្លៃអតិបរមា $f({tx(c)})={tx(v)}$ ។"))
        elif kind == "min":
            out.append(P(f"អនុគមន៍មានអប្បបរមាស្មើនឹង ${tx(v)}$ ត្រង់ $x={tx(c)}$ ។", f"$f$ មានតម្លៃអប្បបរមា $f({tx(c)})={tx(v)}$ ។"))
        else:
            out.append(f"ត្រង់ $x={tx(c)}$ ដេរីវេស្មើសូន្យ តែមិនប្ដូរសញ្ញា ដូច្នេះមិនមែនជាបរមាទេ ។")
    return "\n".join(out)

# =================== PARTS ===================
def F_(S):
    return s(S.f)

def p_domain(S):
    q = P("រកដែនកំណត់ $D$ នៃអនុគមន៍ $f$ ។", "កំណត់ដែនកំណត់នៃអនុគមន៍ $f$ ។", "រកដែនកំណត់នៃ $f$ ។", "ចូររកដែនកំណត់ $D$ របស់ $f$ ។")
    d = S.Ddoc or P("អនុគមន៍ $f$ ជាពហុធា ដូច្នេះកំណត់គ្រប់ចំនួនពិត $x$ ។", "$f$ ជាពហុធា ហេតុនេះមានន័យចំពោះគ្រប់ $x$ ។")
    sol = d + "\n" + P("ដូចនេះ ដែនកំណត់គឺ", "ដូចនេះ", "ដូចនេះ គេបាន") + f" $\\boxed{{{S.Dtex}}}$ ។"
    ch = [check(f"subs({tx_den(S)},x,{s(h)})", "0", "excluded value") for h in S.holes if tx_den(S)]
    return q, sol, ch

def tx_den(S):
    d = sp.denom(sp.together(S.f)) if S.fam in ("homographic", "oblique", "two_vert", "inv_square", "exp_quot", "logistic") else None
    return s(d) if d is not None else None

def pole_data(S, d):
    """Numerator value and denominator sign at a pole, from the printed fraction S.nd."""
    N, Dn, nt, dt = S.nd
    pt = d["pt"]
    nv = sp.simplify(N.subs(x, pt))
    eps = R(1, 1000) if d["side"] == "+" else -R(1, 1000)
    ds = 1 if num(Dn.subs(x, pt + eps)) > 0 else -1
    assert sp.simplify(Dn.subs(x, pt)) == 0 and nv != 0, ("not a pole", S.fam)
    assert d["val"] == (oo if num(nv) * ds > 0 else -oo), ("pole sign", S.fam, str(S.f))
    return N, Dn, nt, dt, nv, ds, eps

def pole_why(S, d):
    """State the limit of the numerator and the sign of the denominator at a pole."""
    N, Dn, nt, dt, nv, ds, eps = pole_data(S, d)
    L = limtex(d["pt"], d["side"])
    sg = ">0" if num(nv) > 0 else "<0"
    den = f"{L}{dt if dt.startswith('(') or dt.startswith(chr(92)) or dt == 'x' else '(' + dt + ')'}=0^{{{'+' if ds > 0 else '-'}}}"
    if N.is_number:
        return f"ដោយ ${tx(nv)}{sg}$ និង ${den}$"
    nn = nt if nt == "x" else f"({nt})"
    return f"ដោយ ${L}{nn}={tx(nv)}{sg}$ និង ${den}$"

def lim_line(S, d):
    head = limtex(d["pt"], d["side"]) + "f(x)"
    v = vt(d["val"]); w = d["why"]
    if not w:
        if d["side"]:
            return f"{pole_why(S, d)} គេបាន ៖\n$${head}={v}$$"
        return f"$${head}={v}$$"
    if KH.search(w):
        return f"{w} គេបាន ៖\n$${head}={v}$$"
    return f"$${head}={w}={v}$$"

KH = re.compile(r"[ក-៿]")

def p_limits(S):
    if len(S.L) == 2:
        a_, b_ = S.L
        q = P(f"គណនា ${limtex(a_['pt'],a_['side'])}f(x)$ និង ${limtex(b_['pt'],b_['side'])}f(x)$ ។", "គណនាលីមីតនៃ $f$ ត្រង់ចុងនៃដែនកំណត់ ។", "រកលីមីតនៃអនុគមន៍ $f$ ត្រង់ចុងដែនកំណត់ ។")
    else:
        q = P("គណនាលីមីតនៃ $f$ ត្រង់ចុងនៃដែនកំណត់ ។", "គណនាលីមីតនៃអនុគមន៍ត្រង់ចុងនីមួយៗនៃ $D$ ។", "រកគ្រប់លីមីតចាំបាច់នៃ $f$ ត្រង់ចុងដែនកំណត់ ។")
    lines = [lim_line(S, d) for d in S.L]
    ch = []
    for d in S.L:
        arg = f"limit({F_(S)},x,{s(d['pt'])}" + (f",'{d['side']}')" if d["side"] else ")")
        ch.append(check(arg, s(d["val"]), "limit"))
        if d["side"] and not d["why"]:
            N, Dn, nt, dt, nv, ds, eps = pole_data(S, d)
            ch.append(check(f"subs({s(N)},x,{s(d['pt'])})", s(nv), "numerator at pole"))
            ch.append(check(f"subs({s(Dn)},x,{s(d['pt'] + eps)})" + (">0" if ds > 0 else "<0"), "True", "denominator sign"))
    sol = "\n".join(lines) + "\n" + "ដូចនេះ " + " និង ".join(f"${limtex(d['pt'],d['side'])}f(x)={vt(d['val'])}$" for d in S.L) + " ។"
    return q, sol, ch

def no_oblique(S):
    """Rule out an oblique asymptote at each infinite end where f is unbounded and none is claimed."""
    out = []; ch = []
    for pt in ([oo] if S.lo is not None else [-oo, oo]):
        if any(a_["kind"] == "o" and a_["side"] in (None, pt) for a_ in S.A): continue
        v = getL(S, pt, None)
        if abs(fl(v)) != math.inf: continue
        L = limtex(pt); tag = "oo" if pt == oo else "-oo"
        q_ = sp.limit(S.f / x, x, pt)
        rw = tx(sp.expand(S.f / x, power_exp=False))
        ch.append(check(f"limit(({F_(S)})/x,x,{tag})", s(q_), "limit of f(x)/x"))
        line = f"$${L}\\frac{{f(x)}}{{x}}={L}\\left({rw}\\right)={vt(q_)}$$\n"
        if q_ == 0:
            line += f"ដោយលីមីតនេះស្មើ $0$ ហើយ ${L}f(x)={vt(v)}$ នោះ $(C)$ គ្មានអាស៊ីមតូតទ្រេតត្រង់ ${vt(pt)}$ ទេ ។"
        elif abs(fl(q_)) == math.inf:
            line += f"ដោយលីមីតនេះមិនមែនជាចំនួនកំណត់ នោះ $(C)$ គ្មានអាស៊ីមតូតទ្រេតត្រង់ ${vt(pt)}$ ទេ ។"
        else:
            r_ = sp.expand(S.f - q_ * x); w_ = sp.limit(r_, x, pt)
            assert abs(fl(w_)) == math.inf, ("oblique missed", S.fam, str(S.f))
            ch.append(check(f"limit(({F_(S)})-({s(q_ * x)}),x,{tag})", s(w_), "limit of f(x)-ax"))
            line += f"$${L}\\left[f(x)-({tx(q_ * x)})\\right]={L}({tx(r_)})={vt(w_)}$$\n"
            line += f"ដោយលីមីតនេះមិនមែនជាចំនួនកំណត់ នោះ $(C)$ គ្មានអាស៊ីមតូតទ្រេតត្រង់ ${vt(pt)}$ ទេ ។"
        out.append(line)
    return out, ch

def p_asym(S):
    q = P("រកសមីការអាស៊ីមតូតនៃខ្សែកោង $(C)$ ។", "បញ្ជាក់អាស៊ីមតូតទាំងអស់នៃ $(C)$ ។", "ទាញរកសមីការអាស៊ីមតូតនៃក្រាប $(C)$ ។", "សរសេរសមីការអាស៊ីមតូតនៃខ្សែកោង $(C)$ ។")
    if not S.A:
        q = "សិក្សាអាស៊ីមតូតនៃខ្សែកោង $(C)$ ។"
    obl = [a_ for a_ in S.A if a_["kind"] == "o"]
    if obl and rng.random() < 0.5:
        q = f"បង្ហាញថាបន្ទាត់ $(d):{obl[0]['eq']}$ ជាអាស៊ីមតូតទ្រេតនៃ $(C)$ ហើយរកអាស៊ីមតូតផ្សេងទៀត ។"
    out = []; ch = []
    for a_ in S.A:
        if a_["kind"] == "v":
            p_ = sp.solve(a_["expr"], x)[0]
            ds = [d for d in S.L if d["side"] and abs(fl(d["val"])) == math.inf and d["pt"] == p_]
            if len(ds) == 2 and ds[0]["val"] == ds[1]["val"]:
                said = f"${limtex(p_)}f(x)={vt(ds[0]['val'])}$"
            else:
                said = " និង ".join(f"${limtex(d['pt'],d['side'])}f(x)={vt(d['val'])}$" for d in ds)
            out.append(P(f"ដោយ {said} នោះបន្ទាត់ ${a_['eq']}$ ជាអាស៊ីមតូតឈរនៃ $(C)$ ។",
                         f"ដោយ {said} នោះ $(C)$ មានអាស៊ីមតូតឈរ ${a_['eq']}$ ។"))
        elif a_["kind"] == "h":
            sd = a_["side"] or (oo if S.lo is not None else None)
            lab = "\\pm\\infty" if sd is None else vt(sd)
            out.append(P(f"ដោយ $\\lim_{{x\\to {lab}}}f(x)={tx(a_['expr'])}$ នោះបន្ទាត់ ${a_['eq']}$ ជាអាស៊ីមតូតដេកនៃ $(C)$ ។",
                         f"លីមីតត្រង់ ${lab}$ ជាចំនួនកំណត់ ${tx(a_['expr'])}$ ដូច្នេះ ${a_['eq']}$ ជាអាស៊ីមតូតដេក ។"))
        else:
            lab = "" if a_["side"] is None else f" ត្រង់ ${vt(a_['side'])}$"
            out.append(f"យើងមាន ៖\n{a_['why']}\nនោះបន្ទាត់ ${a_['eq']}$ ជាអាស៊ីមតូតទ្រេតនៃ $(C)$" + lab + " ។")
            pt = "oo" if a_["side"] in (None, oo) else "-oo"
            ch.append(check(f"limit({F_(S)}-({s(a_['expr'])}),x,{pt})", "0", "oblique asymptote"))
    if getattr(S, "noH", False):
        out.append("ដោយលីមីតត្រង់ $+\\infty$ មិនមែនជាចំនួនកំណត់ នោះ $(C)$ គ្មានអាស៊ីមតូតដេកទេ ។")
    if getattr(S, "noAsym", False):
        out.append("ដោយលីមីតត្រង់ចុងអនន្តនៃ $D$ មិនមែនជាចំនួនកំណត់ ហើយគ្មានលីមីតអនន្តត្រង់ចំណុចកំណត់ណាមួយ នោះ $(C)$ គ្មានអាស៊ីមតូតឈរ និងអាស៊ីមតូតដេកទេ ។")
    no_o, no_c = no_oblique(S)
    out += no_o; ch += no_c
    eqs = [a_["eq"] for a_ in S.A]
    if eqs:
        out.append("ដូចនេះ សមីការអាស៊ីមតូតគឺ " + " , ".join(f"$\\boxed{{{e}}}$" for e in eqs) + " ។")
    else:
        out.append("ដូចនេះ $(C)$ គ្មានអាស៊ីមតូតទេ ។")
    return q, "\n".join(out), ch

def p_deriv(S):
    q = P("គណនាដេរីវេ $f'(x)$ ។", "រកដេរីវេ $f'(x)$ នៃអនុគមន៍ $f$ ។", "គណនា $f'(x)$ ចំពោះគ្រប់ $x\\in D$ ។")
    if rng.random() < 0.25:
        q = f"បង្ហាញថា $f'(x)={S.fptex}$ ចំពោះគ្រប់ $x\\in D$ ។"
    sol = "\n".join(S.dsteps) + "\n" + P("ដូចនេះ", "ដូចនេះ គេបាន") + f" $\\boxed{{f'(x)={S.fptex}}}$ ។"
    ch = [check(f"diff({F_(S)},x)", s(S.fp), "derivative")]
    return q, sol, ch

def p_sign(S):
    q = P("សិក្សាសញ្ញានៃ $f'(x)$ ។", "សិក្សាសញ្ញាដេរីវេ រួចទាញរកទិសដៅអថេរភាពនៃ $f$ ។", "បញ្ជាក់សញ្ញានៃ $f'(x)$ និងចន្លោះដែល $f$ កើន ឬចុះ ។")
    parts = [t for t in (S.zero, S.sgn) if t]
    sol = "\n".join(parts) + P("\nតារាងសញ្ញានៃ $f'(x)$ ៖", "\nសញ្ញាដេរីវេទី១ ៖") + f"\n$$\n{S.signtable}\n$$\n" + "ដូចនេះ " + mono_text(S)
    ch = []
    for i, (t, g) in enumerate(zip(S.tests, S.signs)):
        if g: ch.append(check(f"subs(diff({F_(S)},x),x,{s(t)})" + (">0" if g == "+" else "<0"), "True", "sign of f'"))
    for c in S.crit:
        ch.append(check(f"subs(diff({F_(S)},x),x,{s(c)})", "0", "critical point"))
    return q, sol, ch

def p_table(S):
    q = P("សង់តារាងអថេរភាពនៃ $f$ ។", "សង់តារាងអថេរភាពនៃអនុគមន៍ $f$ ។", "សិក្សាអថេរភាពនៃ $f$ រួចសង់តារាងអថេរភាព ។", "សង់តារាងអថេរភាព ហើយទាញរកបរមានៃ $f$ (បើមាន) ។")
    sol = P("តាមលទ្ធផលខាងលើ គេបានតារាងអថេរភាព ៖", "តារាងអថេរភាពនៃ $f$ ៖", "ចងក្រងសញ្ញាដេរីវេ និងលីមីត យើងបានតារាងអថេរភាព ៖") + f"\n$$\n{S.table}\n$$"
    ch = []
    for kind, c, v in S.ext:
        ch.append(check(f"subs({F_(S)},x,{s(c)})", s(v), kind + " value"))
    if S.ext:
        sol += "\n" + ext_text(S)
    else:
        sol += "\n" + ("ដូចនេះ $f$ គ្មានបរមាទេ ។")
    return q, sol, ch

def do_tan(S):
    c = [t for t in S.tans]
    rng.shuffle(c)
    for x0 in c:
        y0 = S.f.subs(x, x0); m_ = sp.diff(S.f, x).subs(x, x0)
        y0 = sp.expand(y0); m_ = sp.expand(sp.nsimplify(m_) if m_.is_Rational else m_)
        if m_ == 0 or not (y0.is_real and m_.is_real) or m_.is_Add: continue
        T = sp.expand(m_ * (x - x0) + y0)
        if len(ttex(T)) > 34: continue
        return x0, y0, m_, T
    return None

def p_tangent(S):
    r = S.tan
    x0, y0, m_, T = r
    how = P("ត្រង់ចំណុចមានអាប់ស៊ីស", "ត្រង់ចំណុចដែលមានអាប់ស៊ីស", "ត្រង់ចំណុច $A$ នៃ $(C)$ ដែលមានអាប់ស៊ីស")
    q = P(f"រកសមីការបន្ទាត់ប៉ះ $(T)$ នៃខ្សែកោង $(C)$ {how} $x_0={tx(x0)}$ ។", f"សរសេរសមីការបន្ទាត់ប៉ះ $(T)$ នឹង $(C)$ {how} ${tx(x0)}$ ។")
    if x0 == 0 and rng.random() < 0.6:
        q = "រកសមីការបន្ទាត់ប៉ះ $(T)$ នៃ $(C)$ ត្រង់ចំណុចប្រសព្វជាមួយអ័ក្ស $y'oy$ ។"
    xt = "x" if x0 == 0 else f"({tx(x - x0)})"
    rhs = xt if m_ == 1 else "-" + xt if m_ == -1 else tx(m_) + xt
    sol = (P("សមីការបន្ទាត់ប៉ះមានរាង", "តាមរូបមន្ត សមីការបន្ទាត់ប៉ះគឺ") + " $y-y_0=f'(x_0)(x-x_0)$ ។\n" +
           f"ចំពោះ $x_0={tx(x0)}$ គេបាន $y_0=f({tx(x0)})={tx(y0)}$ និង $f'({tx(x0)})={tx(m_)}$ ។\n"
           f"$${shift('y', y0)}={rhs}$$\nដូចនេះ សមីការបន្ទាត់ប៉ះគឺ $\\boxed{{(T):y={ttex(T)}}}$ ។")
    ch = [check(f"subs({F_(S)},x,{s(x0)})", s(y0), "y0"), check(f"subs(diff({F_(S)},x),x,{s(x0)})", s(m_), "slope"),
          check(f"subs({F_(S)},x,{s(x0)})+subs(diff({F_(S)},x),x,{s(x0)})*(x-({s(x0)}))", s(T), "tangent")]
    return q, sol, ch

def has0(S):
    if S.lo is not None and S.lo >= 0: return False
    if S.gap and S.gap[0] <= 0 <= S.gap[1]: return False
    if any(h == 0 for h in S.holes): return False
    if S.lo is not None and S.lo < 0: return True
    return True

def p_axes(S):
    y_ok = has0(S); x_ok = S.xint is not None
    ch = []; L = []
    if y_ok and x_ok:
        q = P("រកកូអរដោនេចំណុចប្រសព្វនៃ $(C)$ ជាមួយអ័ក្ស $x'ox$ និង $y'oy$ ។", "រកចំណុចប្រសព្វនៃខ្សែកោង $(C)$ ជាមួយអ័ក្សកូអរដោនេ ។")
    elif y_ok:
        q = "រកកូអរដោនេចំណុចប្រសព្វនៃ $(C)$ ជាមួយអ័ក្ស $y'oy$ ។"
    else:
        q = "រកកូអរដោនេចំណុចប្រសព្វនៃ $(C)$ ជាមួយអ័ក្ស $x'ox$ ។"
    if y_ok:
        y0 = S.f.subs(x, 0)
        L.append(f"+ ជាមួយអ័ក្ស $y'oy$ ៖ យក $x=0$ គេបាន $f(0)={tx(y0)}$ ។ ដូចនេះ $(C)$ កាត់ $y'oy$ ត្រង់ចំណុច $\\boxed{{(0;{tx(y0)})}}$ ។")
        ch.append(check(f"subs({F_(S)},x,0)", s(y0), "y-intercept"))
    if x_ok:
        if S.xint:
            pts = " , ".join(f"$({tx(r)};0)$" for r in S.xint)
            vs = " ឬ ".join(f"$x={tx(r)}$" for r in S.xint)
            L.append(f"+ ជាមួយអ័ក្ស $x'ox$ ៖ {S.xhow}\nគេបាន {vs} ។ ដូចនេះ $(C)$ កាត់ $x'ox$ ត្រង់ {pts} ។")
            for r in S.xint:
                ch.append(check(f"subs({F_(S)},x,{s(r)})", "0", "x-intercept"))
        else:
            L.append(f"+ ជាមួយអ័ក្ស $x'ox$ ៖ {S.xhow}\nដូចនេះ $(C)$ មិនកាត់អ័ក្ស $x'ox$ ទេ ។")
    return q, "\n".join(L), ch

def p_center(S):
    h, k = S.center
    q = P(f"បង្ហាញថាចំណុច $I({tx(h)};{tx(k)})$ ជាផ្ចិតឆ្លុះនៃខ្សែកោង $(C)$ ។", f"ស្រាយបញ្ជាក់ថា $I({tx(h)};{tx(k)})$ ជាផ្ចិតឆ្លុះនៃ $(C)$ ។")
    sol = (f"ដើម្បីបង្ហាញ គេត្រូវផ្ទៀងផ្ទាត់ថា $f(2a-x)+f(x)=2b$ ជាមួយ $a={tx(h)}$ និង $b={tx(k)}$ ។\n" + "\n".join(S.center_lines) +
           f"\nគេបាន $f({tx(2*h-x)})+f(x)={tx(2*k)}=2b$ ។\nដូចនេះ $I({tx(h)};{tx(k)})$ ជាផ្ចិតឆ្លុះនៃ $(C)$ ។")
    ch = [check(f"({s(S.f.subs(x,2*h-x))})+({F_(S)})", s(2 * k), "centre of symmetry")]
    return q, sol, ch

def p_pos(S):
    d = S.pos
    q = P(f"សិក្សាទីតាំងនៃខ្សែកោង $(C)$ ធៀបនឹងបន្ទាត់ ${d['eq']}$ ។", f"សិក្សាទីតាំងធៀបរវាង $(C)$ និងអាស៊ីមតូត ${d['eq']}$ ។")
    L = [f"តាង $d(x)=f(x)-({tx(d['lin'])})={d['dtex']}$ ។"]
    for c, up in d["cases"]:
        L.append(f"+ ចំពោះ ${c}$ គេបាន $d(x){'>' if up else '<'}0$ ដូច្នេះ $(C)$ នៅ{'ខាងលើ' if up else 'ខាងក្រោម'}បន្ទាត់ ${d['eq']}$ ។")
    if "cross" in d:
        L.append(f"+ ចំពោះ $x={tx(d['cross'])}$ គេបាន $d(x)=0$ ហើយ $(C)$ កាត់បន្ទាត់នេះ ។")
    L.append("ដូចនេះ ទីតាំងនៃ $(C)$ ធៀបនឹងអាស៊ីមតូតអាស្រ័យតែលើសញ្ញានៃ $d(x)$ ។")
    ch = []
    for t, up in d["chk"]:
        ch.append(check(f"subs({F_(S)}-({s(d['lin'])}),x,{s(t)})" + (">0" if up else "<0"), "True", "position"))
    return q, "\n".join(L), ch

NW = {0: "គ្មានឫស", 1: "មានឫសមួយ", 2: "មានឫសពីរ", 3: "មានឫសបី", 4: "មានឫសបួន", 5: "មានឫសប្រាំ"}
def count_cases(S):
    br = []
    for i, g in enumerate(S.signs):
        if g is None: continue
        a_, b_ = S.cols[i]["R"], S.cols[i + 1]["L"]
        br.append((min(a_, b_, key=fl), max(a_, b_, key=fl)))
    crit = [c["v"] for c in S.cols if c["t"] == "crit"]
    thr = sorted({v for b in br for v in b if abs(fl(v)) != math.inf}, key=fl)
    uniq = []
    for v in thr:
        if not any(abs(fl(v) - fl(u)) < 1e-12 for u in uniq): uniq.append(v)
    thr = uniq
    if not thr or len(thr) > 3: return None
    def cnt(mf):
        n = sum(1 for lo_, hi_ in br if fl(lo_) < mf < fl(hi_))
        n += sum(1 for v in crit if abs(fl(v) - mf) < 1e-12)
        return n
    out = []
    fs = [fl(t) for t in thr]
    out.append((f"m<{tx(thr[0])}", cnt(fs[0] - 1)))
    for i, t in enumerate(thr):
        out.append((f"m={tx(t)}", cnt(fs[i])))
        if i + 1 < len(thr):
            out.append((f"{tx(t)}<m<{tx(thr[i+1])}", cnt((fs[i] + fs[i + 1]) / 2)))
    out.append((f"m>{tx(thr[-1])}", cnt(fs[-1] + 1)))
    return out

def p_disc(S):
    cs = S.disc
    q = P("តាមតារាងអថេរភាព ពិភាក្សាតាមតម្លៃ $m$ នូវចំនួនឫសនៃសមីការ $f(x)=m$ ។", "ពិភាក្សាតាមប៉ារ៉ាម៉ែត្រ $m$ នូវចំនួនឫសនៃសមីការ $f(x)=m$ ។")
    L = ["ចំនួនឫសនៃសមីការ $f(x)=m$ ស្មើនឹងចំនួនចំណុចប្រសព្វនៃ $(C)$ ជាមួយបន្ទាត់ដេក $y=m$ ។ តាមតារាងអថេរភាព ៖"]
    for c, n in cs:
        L.append(f"+ បើ ${c}$ សមីការ{NW[n]} ។")
    L.append("ដូចនេះ ចំនួនឫសប្រែប្រួលតាមករណីខាងលើ ។")
    return q, "\n".join(L), []

def p_ineq(S):
    kind, c, v = S.ext[0]
    op = "\\ge " if kind == "min" else "\\le "
    q = P(f"ទាញបញ្ជាក់ថា $f(x){op}{tx(v)}$ គ្រប់ $x\\in D$ ។", f"ពីតារាងអថេរភាព ទាញបញ្ជាក់ថា $f(x){op}{tx(v)}$ ចំពោះគ្រប់ $x\\in D$ ។")
    w = "អប្បបរមា" if kind == "min" else "អតិបរមា"
    sol = f"តាមតារាងអថេរភាព អនុគមន៍ $f$ មាន{w}ដាច់ខាតលើ $D$ ត្រង់ $x={tx(c)}$ ព្រោះវា{'ចុះ' if kind=='min' else 'កើន'}មុន $x={tx(c)}$ ហើយ{'កើន' if kind=='min' else 'ចុះ'}ក្រោយ $x={tx(c)}$ ។\nដូចនេះ $f(x){op}f({tx(c)})$ គឺ $\\boxed{{f(x){op}{tx(v)}}}$ គ្រប់ $x\\in D$ ។"
    sol = sol.replace("អប្បបរមាដាច់ខាត", "អប្បបរមា").replace("អតិបរមាដាច់ខាត", "អតិបរមា")
    return q, sol, [check(f"subs({F_(S)},x,{s(c)})", s(v), "bound")]

def p_inflect(S):
    h, k = S.inflect
    fpp = S.fpp
    q = P("គណនា $f''(x)$ រួចរកកូអរដោនេចំណុចរបត់នៃ $(C)$ ។", "បង្ហាញថា $(C)$ មានចំណុចរបត់មួយ រួចរកកូអរដោនេរបស់វា ។")
    t1 = sp.Rational(str(round(num(h) - 1, 2))); t2 = sp.Rational(str(round(num(h) + 1, 2)))
    a1 = num(fpp.subs(x, t1)); 
    sol = (f"$$f''(x)={tx(fpp)}$$\n$f''(x)=0$ សមមូល $x={tx(h)}$ ហើយ $f''(x)$ ប្ដូរសញ្ញាត្រង់ $x={tx(h)}$ ។\n"
           f"គេបាន $f({tx(h)})={tx(k)}$ ។\nដូចនេះ ចំណុចរបត់គឺ $\\boxed{{I({tx(h)};{tx(k)})}}$ ។")
    ch = [check(f"subs(diff({F_(S)},x,2),x,{s(h)})", "0", "inflection"), check(f"subs({F_(S)},x,{s(h)})", s(k), "inflection y"),
          check(f"subs(diff({F_(S)},x,2),x,{s(t1)})*subs(diff({F_(S)},x,2),x,{s(t2)})<0", "True", "sign change")]
    return q, sol, ch

def ivt_others(S, i):
    """Branches of f other than i, or None if f has a root outside branch i."""
    out = []
    if any(c["t"] == "crit" and fl(c["v"]) == 0 for c in S.cols): return None
    for j, g in enumerate(S.signs):
        if g is None or j == i: continue
        lo_, hi_ = sorted((S.cols[j]["R"], S.cols[j + 1]["L"]), key=fl)
        if not (fl(lo_) >= 0 or fl(hi_) <= 0): return None
        out.append((j, lo_, hi_))
    return out

def p_ivt(S):
    a_, b_, inc, i = S.ivt
    va, vb = S.f.subs(x, a_), S.f.subs(x, b_)
    br = ivl(S.cols[i], S.cols[i + 1]); oth = ivt_others(S, i)
    q = f"បង្ហាញថាសមីការ $f(x)=0$ មានឫសតែមួយគត់ $\\alpha$ ក្នុងចន្លោះ $({a_};{b_})$ ។"
    whole = oth is not None and rng.random() < 0.5
    if whole:
        q = f"ស្រាយបញ្ជាក់ថា $(C)$ កាត់អ័ក្ស $x'ox$ ត្រង់ចំណុចតែមួយគត់ដែលមានអាប់ស៊ីស $\\alpha\\in({a_};{b_})$ ។"
    L = [f"លើចន្លោះ ${br}$ អនុគមន៍ $f$ ជាប់ និង{'កើន' if inc else 'ចុះ'} ហើយ $[{a_};{b_}]$ នៅក្នុងចន្លោះនេះ ។",
         f"គេមាន $f({a_})={tx(va)}$ និង $f({b_})={tx(vb)}$ ដែល $f({a_})\\cdot f({b_})<0$ ។"]
    ch = [check(f"subs({F_(S)},x,{a_})*subs({F_(S)},x,{b_})<0", "True", "sign change")]
    if whole:
        L.append(f"ដូច្នេះ លើចន្លោះ ${br}$ សមីការ $f(x)=0$ មានឫសតែមួយគត់ $\\alpha$ ហើយ $\\alpha\\in({a_};{b_})$ ។")
        for j, lo_, hi_ in oth:
            L.append(f"+ លើចន្លោះ ${ivl(S.cols[j], S.cols[j + 1])}$ តម្លៃនៃ $f$ នៅចន្លោះ ${vt(lo_)}$ និង ${vt(hi_)}$ ដូច្នេះ $f(x){'>' if fl(lo_) >= 0 else '<'}0$ ហើយសមីការគ្មានឫសទេ ។")
            ch.append(check(f"subs({F_(S)},x,{s(S.tests[j])})" + (">0" if fl(lo_) >= 0 else "<0"), "True", "no root on other branch"))
        L.append(f"ដូចនេះ លើដែនកំណត់ទាំងមូល $(C)$ កាត់អ័ក្ស $x'ox$ ត្រង់ចំណុចតែមួយគត់ដែលមានអាប់ស៊ីស $\\alpha\\in({a_};{b_})$ ។")
    else:
        L.append(f"ដូចនេះ សមីការ $f(x)=0$ មានឫសតែមួយគត់ $\\alpha$ ក្នុងចន្លោះ $({a_};{b_})$ ។")
    return q, "\n".join(L), ch

def find_ivt(S):
    for i, g in enumerate(S.signs):
        if g is None: continue
        lo_, hi_ = fl(S.cols[i]["x"]), fl(S.cols[i + 1]["x"])
        ints = [t for t in range(-8, 12) if lo_ < t and t + 1 < hi_]
        rng.shuffle(ints)
        for t in ints:
            va, vb = num(S.f.subs(x, t)), num(S.f.subs(x, t + 1))
            if va * vb < 0 and abs(va) < 60 and abs(vb) < 60 and len(tx(S.f.subs(x, t))) < 30 and len(tx(S.f.subs(x, t + 1))) < 30:
                return (t, t + 1, g == "+", i)
    return None

def p_aux(S):
    a_ = S.aux
    return a_["ask"], a_["sol"], a_["chk"]

def p_par(S):
    d = S.par
    xp = d["x"]; yv = S.f.subs(x, xp)
    q = f"រកកូអរដោនេចំណុច $M$ នៃ $(C)$ ដែលបន្ទាត់ប៉ះត្រង់ $M$ ស្របនឹងអាស៊ីមតូតទ្រេត ។"
    lg = sp.expand(ln(xp))
    sol = (f"បន្ទាត់ប៉ះស្របនឹងអាស៊ីមតូតទ្រេតលុះត្រាតែមេគុណប្រាប់ទិសស្មើគ្នា គឺ $f'(x)={tx(d['al'])}$ ។\n"
           f"តាមលទ្ធផលខាងលើ $f'(x)={tx(d['al'])}+\\frac{{{tx(2*d['al'])}-({d['nt']})}}{{x^2}}$ ដូច្នេះ ${tx(2*d['al'])}-({d['nt']})=0$ ឬ $\\ln x={tx(lg)}$ គឺ $x={tx(xp)}$ ។\n"
           f"គេបាន $f({tx(xp)})={tx(sp.expand(yv))}$ ។\nដូចនេះ $\\boxed{{M({tx(xp)};{tx(sp.expand(yv))})}}$ ។")
    ch = [check(f"subs(diff({F_(S)},x),x,{s(xp)})", s(d["al"]), "slope equals asymptote slope")]
    return q, sol, ch

def pgf(e):
    t = str(e).replace("**", "^").replace("log(", "ln(")
    return re.sub(r"\bE\b", "exp(1)", t)

def window(S):
    """Plot window. Every critical point, intercept, tangency point, root interval and horizontal
    asymptote stays inside, and each branch of the curve keeps its central part visible."""
    fn = sp.lambdify(x, S.f, "numpy")
    def Y(g):
        with np.errstate(all="ignore"):
            return np.broadcast_to(np.asarray(fn(g), dtype=float), g.shape)
    def Y1(v):
        r = Y(np.array([float(v)]))[0]
        return r if np.isfinite(r) else None
    ivt = getattr(S, "ivt", None) if getattr(S, "ivt_on", False) else None
    hx = [fl(c["x"]) for c in S.cols if abs(fl(c["x"])) != math.inf]
    if S.xint: hx += [num(v) for v in S.xint]
    if S.tan: hx.append(num(S.tan[0]))
    if ivt: hx += [ivt[0], ivt[1]]
    hx.append(0)
    xmin = math.floor(min(hx)) - 1; xmax = math.ceil(max(hx)) + 1
    if S.lo is not None: xmin = min(int(math.floor(num(S.lo))) - 1, -1)
    if S.gap: xmin -= 2; xmax += 2
    hy = [fl(c["v"]) for c in S.cols if c["t"] == "crit"]
    if has0(S): hy.append(num(S.f.subs(x, 0)))
    if S.tan: hy.append(num(S.tan[1]))
    if ivt: hy += [num(S.f.subs(x, ivt[0])), num(S.f.subs(x, ivt[1]))]
    hy += [num(a_["expr"]) for a_ in S.A if a_["kind"] == "h"]
    hy += [0.0]
    # widen towards the side where the curve stays tame
    want = list(getattr(S, "xr", (xmin, xmax)))
    span = max(hy) - min(hy) + 4
    def tame(v):
        r = Y1(v)
        return r is not None and min(hy) - span <= r <= max(hy) + span
    for _ in range(40):
        moved = False
        if xmax < want[1] and tame(xmax + 1): xmax += 1; moved = True
        if xmin > want[0] and S.lo is None and tame(xmin - 1): xmin -= 1; moved = True
        if not moved: break
    while xmax - xmin < 6:
        l_, r_ = Y1(xmin - 1), Y1(xmax + 1)
        if S.lo is not None or l_ is None or (r_ is not None and abs(r_) <= abs(l_)): xmax += 1
        else: xmin -= 1
    edges = sorted({float(xmin), float(xmax)} | {fl(c["x"]) for c in S.cols if c["t"] in ("excl", "gl", "gr", "lo")})
    ys_all = list(hy)
    for a_, b_ in zip(edges, edges[1:]):
        w = (b_ - a_) * 0.02
        v = Y(np.linspace(a_ + w, b_ - w, 400)); v = v[np.isfinite(v)]
        if len(v) > 20:
            ys_all += [float(np.percentile(v, 12)), float(np.percentile(v, 88))]
    lo_, hi_ = min(ys_all), max(ys_all)
    pad = max(1.0, 0.08 * (hi_ - lo_))
    ymin = min(math.floor(lo_ - pad), -1); ymax = max(math.ceil(hi_ + pad), 1)
    return xmin, xmax, ymin, ymax

def graph_diag(S):
    xmin, xmax, ymin, ymax = window(S)
    br = []
    edges = [xmin]
    for c in S.cols:
        if c["t"] in ("excl", "gl", "gr", "lo"):
            edges.append(num(c["x"]))
    edges.append(xmax)
    edges = sorted(set(edges))
    gaps = []
    if S.lo is not None: gaps.append((xmin, num(S.lo)))
    if S.gap: gaps.append((num(S.gap[0]), num(S.gap[1])))
    segs = []
    for a_, b_ in zip(edges, edges[1:]):
        if any(g0 <= a_ and b_ <= g1 for g0, g1 in gaps): continue
        segs.append((round(a_ + 0.01, 3), round(b_ - 0.01, 3)))
    ex = ""
    for a_, b_ in segs[1:]:
        ex += f"\\addplot[thick,domain={a_}:{b_}] {{{pgf(S.f)}}};\n"
    for a_ in S.A:
        if a_["kind"] == "v":
            v = num(sp.solve(a_["expr"], x)[0])
            ex += f"\\draw[dashed] (axis cs:{round(v,3)},{ymin}) -- (axis cs:{round(v,3)},{ymax});\n"
        else:
            ex += f"\\addplot[dashed,domain={xmin}:{xmax}] {{{pgf(a_['expr'])}}};\n"
    if S.tan:
        ex += f"\\addplot[thin,domain={xmin}:{xmax}] {{{pgf(S.tan[3])}}};\n"
    pts = [(num(c["x"]), num(c["v"])) for c in S.cols if c["t"] == "crit"]
    if S.xint: pts += [(num(r), 0.0) for r in S.xint]
    if has0(S): pts.append((0.0, num(S.f.subs(x, 0))))
    pts = [(round(a_, 3), round(b_, 3)) for a_, b_ in pts]
    if pts:
        ex += "\\addplot[only marks,mark=*,mark size=1.2pt] coordinates {" + " ".join(f"({a_},{b_})" for a_, b_ in pts) + "};\n"
    t = tikz_graph(pgf(S.f), xmin, xmax, ymin, ymax, ex)
    t = t.replace(f"domain={xmin}:{xmax}] {{{pgf(S.f)}", f"domain={segs[0][0]}:{segs[0][1]}] {{{pgf(S.f)}", 1)
    t = t.replace("samples=200]", f"samples=200,restrict y to domain={ymin*3}:{ymax*3},unbounded coords=jump]")
    asy = []
    for a_ in S.A:
        if a_["kind"] == "v":
            asy.append(("v", sp.solve(a_["expr"], x)[0]))
        else:
            asy.append(("o", a_["expr"] + 0 * x))
    S.plot = dict(f=S.f, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, tangent=(S.tan[3] if S.tan else None), points=pts, asymptotes=asy)
    return t

def p_graph(S):
    q = P("សង់ខ្សែកោង $(C)$ ។", "សង់ក្រាប $(C)$ នៃអនុគមន៍ $f$ ។", "សង់ខ្សែកោង $(C)$ ព្រមទាំងអាស៊ីមតូតរបស់វា ។" if S.A else "សង់ក្រាប $(C)$ ។")
    if S.tan and rng.random() < 0.5:
        q = "សង់បន្ទាត់ $(T)$ និងខ្សែកោង $(C)$ ក្នុងតម្រុយតែមួយ ។"
    L = []
    if S.A:
        L.append("គូសអាស៊ីមតូត " + " , ".join(f"${a_['eq']}$" for a_ in S.A) + " ជាបន្ទាត់ដាច់ៗ ។")
    pts = [f"$({tx(c['x'])};{tx(c['v'])})$" for c in S.cols if c["t"] == "crit"]
    if pts:
        L.append("ដៅចំណុចបរមា " + " , ".join(pts) + " ។" if any(k != "stat" for k, _, _ in S.ext) else "ដៅចំណុច " + " , ".join(pts) + " ។")
    if S.xint or has0(S):
        L.append("ដៅចំណុចប្រសព្វជាមួយអ័ក្ស ហើយគូសខ្សែកោងតាមទិសដៅក្នុងតារាងអថេរភាព ។")
    else:
        L.append("គូសខ្សែកោងតាមទិសដៅក្នុងតារាងអថេរភាព ។")
    if S.tan:
        L.append(f"បន្ទាត់ $(T):y={ttex(S.tan[3])}$ ប៉ះខ្សែកោងត្រង់ចំណុចអាប់ស៊ីស $x={tx(S.tan[0])}$ ។")
    L.append("ដូចនេះ ក្រាប $(C)$ ដូចរូបខាងក្រោម ។")
    return q, "\n".join(L), []

LABELS = [["១.", "២.", "៣.", "៤.", "៥.", "៦.", "៧.", "៨.", "៩.", "១០.", "១១."],
          ["ក.", "ខ.", "គ.", "ឃ.", "ង.", "ច.", "ឆ.", "ជ.", "ឈ.", "ញ.", "ដ."],
          ["ក-", "ខ-", "គ-", "ឃ-", "ង-", "ច-", "ឆ-", "ជ-", "ឈ-", "ញ-", "ដ-"]]

def intro(S):
    F = S.ftex; D = S.Dtex
    o = [f"គេឱ្យអនុគមន៍ $f$ កំណត់ដោយ ${F}$ ។ តាង $(C)$ ជាខ្សែកោងតំណាងនៃអនុគមន៍ $f$ ។",
         f"គេមានអនុគមន៍ ${F}$ ដែលមានក្រាបតំណាង $(C)$ ។",
         f"អនុគមន៍ $f$ កំណត់ដោយ ${F}$ ហើយ $(C)$ ជាក្រាបរបស់វា ។",
         f"ឱ្យអនុគមន៍ ${F}$ ។ គេតាងខ្សែកោងនៃ $f$ ដោយ $(C)$ ។",
         f"ចូរសិក្សាអនុគមន៍ ${F}$ ដែលមានខ្សែកោង $(C)$ តាមលំដាប់ខាងក្រោម ។",
         f"គេឱ្យ ${F}$ ។ ក្រាបនៃអនុគមន៍នេះតាងដោយ $(C)$ ។",
         f"ក្នុងលំហាត់នេះ គេសិក្សាអនុគមន៍ $f$ ដែល ${F}$ ។ យក $(C)$ ជាខ្សែកោងរបស់ $f$ ។"]
    if S.lo is not None and S.lo == 0:
        o.append(f"លើចន្លោះ $(0;+\\infty)$ គេកំណត់អនុគមន៍ $f$ ដោយ ${F}$ ។ ក្រាបរបស់វាតាងដោយ $(C)$ ។")
    return P(*o)

def compose(S):
    S.tan = do_tan(S) if S.tans and rng.random() < 0.72 else None
    S.disc = None; S.ivt = None
    body = [p_domain, p_limits, p_asym, p_deriv, p_sign, p_table]
    has_as = bool(S.A) or getattr(S, "noAsym", False)
    if not has_as: body.remove(p_asym)
    if not S.A and S.fam in ("cubic", "quartic"):
        pass
    # exam papers give the derivative before the limits; keep some limits-first rows for variety
    orderB = rng.random() < (0.8 if S.sub.startswith(("exponential_", "logarithm_")) else 0.4)
    if orderB:
        seq = [p_domain, p_deriv, p_sign, p_limits] + ([p_asym] if has_as else []) + [p_table]
    else:
        seq = [p_domain, p_limits] + ([p_asym] if has_as else []) + [p_deriv, p_sign, p_table]
    if S.aux: seq.insert(0, p_aux)
    fu = []
    if S.tan: fu.append(p_tangent)
    if (has0(S) or S.xint is not None) and rng.random() < 0.8: fu.append(p_axes)
    opts = []
    if S.center and S.center_lines: opts.append(p_center)
    if S.pos: opts.append(p_pos)
    if S.inflect: opts.append(p_inflect)
    if S.extra_fu: opts.append(p_par)
    dc = count_cases(S)
    if dc and S.fam not in ("aux_ln",): opts.append(p_disc); S.disc = dc
    if len(S.ext) == 1 and S.ext[0][0] != "stat" and not S.holes and not S.gap:
        opts.append(p_ineq)
    if S.xint is None or S.aux:
        S.ivt = find_ivt(S)
        if S.ivt: opts.append(p_ivt)
    rng.shuffle(opts)
    fu += opts[:P(0, 1, 1, 2)]
    seq += fu
    seq.append(p_graph)
    S.ivt_on = p_ivt in seq
    # sometimes the domain is given, not asked
    res = []
    for fn in seq:
        res.append((fn, fn(S)))
    # merge some adjacent parts under one label
    groups = []
    i = 0
    while i < len(res):
        fn, r = res[i]
        if i + 1 < len(res) and rng.random() < 0.28 and (fn, res[i + 1][0]) in MERGE:
            groups.append([r, res[i + 1][1]]); i += 2
        else:
            groups.append([r]); i += 1
    lab = rng.choice(LABELS)
    qs = []; sol = []; checks = []
    head = P("", "", "ចម្លើយ ៖\n", "ដំណោះស្រាយ ៖\n")
    for j, g in enumerate(groups):
        if len(g) == 2:
            a_ = g[0][0].rstrip(" ។"); b_ = g[1][0]
            q = a_ + P(" រួច", " ហើយ", " រួច") + b_ if False else a_ + " ។ " + b_
        else:
            q = g[0][0]
        qs.append(f"{lab[j]} {q}")
        sol.append(f"{lab[j]} " + "\n".join(r[1] for r in g))
        for r in g:
            checks += r[2]
    prob = intro(S) + "\n" + "\n".join(qs)
    solution = head + "\n\n".join(sol)
    extr = [("\\max " if k == "max" else "\\min ") + f"f={tx(v)}\\text{{ at }}x={tx(c)}" for k, c, v in S.ext if k != "stat"]
    ans = f"f'(x)={S.fptex}"
    extr = [("f_{\\max}=" if k == "max" else "f_{\\min}=") + tx(v) for k, c, v in S.ext if k != "stat"]
    ans = ";\\ ".join([ans] + extr + ([f"(T):y={ttex(S.tan[3])}"] if S.tan else []))
    diags = [dict(type="variation_table", latex=S.table, image=None, alt_km="តារាងអថេរភាពនៃអនុគមន៍ $f$ ដែលបង្ហាញសញ្ញាដេរីវេ និងទិសដៅកើនចុះ ។")]
    if p_sign in seq:
        diags.insert(0, dict(type="sign_table", latex=S.signtable, image=None, alt_km="តារាងសញ្ញានៃដេរីវេ $f'(x)$ ។"))
    gl = graph_diag(S)
    diags.append(dict(type="graph", latex=gl, image=None, alt_km=("ក្រាបនៃខ្សែកោង $(C)$ ជាមួយអាស៊ីមតូត និងចំណុចពិសេសរបស់វា ។" if S.A else "ក្រាបនៃខ្សែកោង $(C)$ ជាមួយចំណុចពិសេសរបស់វា ។")))
    prob, solution, ans = [tidy(v) for v in (prob, solution, ans)]
    row = make_row("function_study", S.sub, "bacii", prob, solution, ans, checks, GEN, diagrams=diags)
    return rename(row, S)

def tidy(t):
    t = re.sub(r"(?<![a-zA-Z'])\(x\)", "x", t)
    t = t.replace("+-", "-").replace("--", "+").replace("-+", "-").replace("(x-0)", "x").replace("\\ln^2 x", "\\ln^{2}x")
    t = re.sub(r"\$([^$\n]+)\$ ឬ \$\1\$", r"$\1$", t)
    return re.sub(r"(?<![\d}.^_a-zA-Z\\])(?<!\\ln )1(?=[a-zA-Z(]|\\ln|\\frac)", "", t)

MERGE = {(p_domain, p_limits), (p_limits, p_asym), (p_deriv, p_sign), (p_sign, p_table), (p_table, p_tangent), (p_axes, p_graph)}

def rename(row, S):
    nm = "f" if S.aux else P("f", "f", "f", "f", "g", "h")
    cv = P("(C)", "(C)", "(C)", "(C_f)", "(\\Gamma)", "(H)")
    if nm != "f" or cv != "(C)":
        pat = re.compile(r"(?<![A-Za-z\\])f(?![A-Za-z])")
        def rp(t):
            t = pat.sub(nm, t) if nm != "f" else t
            return t.replace("(C)", cv)
        for k in ("problem_km", "solution_km", "answer_latex"):
            row[k] = rp(row[k])
        for d in row["diagrams"]:
            if d["type"] != "graph":
                d["latex"] = rp(d["latex"])
            d["alt_km"] = rp(d["alt_km"])
    return row

# =================== HAND-WRITTEN ROWS ===================
def T(t, **k):
    for a_, b_ in k.items():
        t = t.replace("«" + a_ + "»", b_ if isinstance(b_, str) else tx(b_))
    return t

def Q(f, sub, crit=(), lo=None, holes=(), gap=None, A=(), tan=None, xint=None, fn="f", key=None):
    S = St(f, "hand", sub, key=key or str(f))
    S.fp = sp.diff(f, x); S.crit = [sp.sympify(c) for c in crit]
    S.lo = lo; S.holes = [sp.sympify(h) for h in holes]; S.gap = gap; S.xint = xint; S.tan = None
    pts = []
    if lo is None and not (gap and False): pts.append((-oo, None))
    if lo is not None: pts.append((sp.sympify(lo), "+"))
    for h in S.holes: pts += [(h, "-"), (h, "+")]
    if gap: pts += [(gap[0], "-"), (gap[1], "+")]
    pts.append((oo, None))
    for pt, sd in pts:
        v = sp.limit(f, x, pt, sd) if sd else sp.limit(f, x, pt)
        S.L.append(dict(pt=pt, side=sd, val=v, why=""))
    for kind, e in A:
        S.A.append(dict(kind=kind, eq=("x=" + tx(sp.solve(e, x)[0])) if kind == "v" else "y=" + tx(e), expr=sp.sympify(e), why="", side=None))
    if tan is not None:
        y0 = sp.expand(f.subs(x, tan)); m_ = sp.diff(f, x).subs(x, tan)
        S.tan = (tan, y0, m_, sp.expand(m_ * (x - tan) + y0))
    build(S)
    if fn != "f":
        pat = re.compile(r"(?<![A-Za-z\\])f(?![A-Za-z])")
        S.table = pat.sub(fn, S.table); S.signtable = pat.sub(fn, S.signtable)
    S.gl = graph_diag(S); S.fn = fn
    return S

HROWS = []; HPLOTS = {}
def HR(S, prob, sol, ans, d=None, chk=(), sub=None, alt=None):
    f = s(S.f); c = []
    if d is not None: c.append(check(f"diff({f},x)", s(d), "derivative"))
    for cc in S.crit: c.append(check(f"subs(diff({f},x),x,{s(cc)})", "0", "critical point"))
    for k, cc, v in S.ext: c.append(check(f"subs({f},x,{s(cc)})", s(v), k))
    for dd in S.L:
        c.append(check(f"limit({f},x,{s(dd['pt'])}" + (f",'{dd['side']}')" if dd["side"] else ")"), s(dd["val"]), "limit"))
    for t, g in zip(S.tests, S.signs):
        if g: c.append(check(f"subs(diff({f},x),x,{s(t)})" + (">0" if g == "+" else "<0"), "True", "sign"))
    c += list(chk)
    sol = sol.replace("«T»", f"$$\n{S.table}\n$$")
    prob, sol, ans = [tidy(v) for v in (prob, sol, ans)]
    dg = [dict(type="variation_table", latex=S.table, image=None, alt_km="តារាងអថេរភាពនៃអនុគមន៍ដែលបានសិក្សា ។"),
          dict(type="graph", latex=S.gl, image=None, alt_km=alt or getattr(S, "alt", None) or "ក្រាបនៃអនុគមន៍ដែលបានសិក្សា ជាមួយចំណុចពិសេស ។")]
    r = make_row("function_study", sub or S.sub, "bacii", prob, sol, ans, c, GEN + "_hand", diagrams=dg)
    HROWS.append(r); HPLOTS[r["id"]] = S.plot

def addlines(S, lines, alt=None):
    """Add straight lines the exercise asks to draw with the curve."""
    ex = "".join(f"\\addplot[dashed,domain={S.plot['xmin']}:{S.plot['xmax']}] {{{pgf(e)}}};\n" for e in lines)
    S.gl = S.gl.replace("\\end{axis}", ex + "\\end{axis}")
    S.plot["asymptotes"] = list(S.plot["asymptotes"]) + [("o", e + 0 * x) for e in lines]
    S.alt = alt

def reshow(S, g, xr, yr, curves=(), lines=(), pts=(), start=None, alt=None):
    """Draw what the exercise asks about instead of the studied f: curve g, optional second curves
    as (expr, x-start), and straight lines (dashed)."""
    xmin, xmax = xr; ymin, ymax = yr
    ex = ""
    for e, a_ in curves:
        ex += f"\\addplot[thick,domain={a_}:{xmax}] {{{pgf(e)}}};\n"
    for e in lines:
        ex += f"\\addplot[dashed,domain={xmin}:{xmax}] {{{pgf(e)}}};\n"
    if pts:
        ex += "\\addplot[only marks,mark=*,mark size=1.2pt] coordinates {" + " ".join(f"({a_},{b_})" for a_, b_ in pts) + "};\n"
    S.gl = tikz_graph(pgf(g), xmin, xmax, ymin, ymax, ex).replace("samples=200]", f"samples=200,restrict y to domain={ymin*3}:{ymax*3},unbounded coords=jump]")
    if start is not None:
        S.gl = S.gl.replace(f"domain={xmin}:{xmax}] {{{pgf(g)}", f"domain={start}:{xmax}] {{{pgf(g)}", 1)
    S.alt = alt
    S.plot = dict(f=g, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, tangent=(curves[0][0] if curves else None),
                  points=list(pts), asymptotes=[("o", e + 0 * x) for e in lines])

def C(l, r, n=""):
    return check(l, s(r), n)

def hand_rows():
    # 1 parameters of a cubic from its extrema
    f = x**3 - 3*x**2 - 9*x + 2
    S = Q(f, "hand_find_parameters", crit=[-1, 3], tan=0)
    HR(S, r"អនុគមន៍ $f(x)=x^3+ax^2+bx+c$ មានខ្សែកោង $(C)$ ។ គេដឹងថា $f$ មានបរមាត្រង់ $x=-1$ និង $x=3$ ហើយ $(C)$ កាត់អ័ក្ស $y'oy$ ត្រង់ចំណុចមានអរដោនេ $2$ ។" "\n" r"១. កំណត់ចំនួនពិត $a,b,c$ ។" "\n" r"២. សង់តារាងអថេរភាពនៃ $f$ ។" "\n" r"៣. រកសមីការបន្ទាត់ប៉ះ $(C)$ ត្រង់ចំណុចប្រសព្វជាមួយ $y'oy$ រួចសង់ $(C)$ ។",
       r"១. គេមាន $f'(x)=3x^2+2ax+b$ ។ ដោយ $f$ មានបរមាត្រង់ $-1$ និង $3$ នោះចំនួនទាំងពីរនេះជាឫសនៃ $f'(x)=0$ ។ តាមទំនាក់ទំនងផលបូកនិងផលគុណឫស គេបាន $-\frac{2a}{3}=2$ និង $\frac{b}{3}=-3$ ។ ដូច្នេះ $a=-3$ និង $b=-9$ ។" "\n" r"ម្យ៉ាងទៀត $f(0)=c=2$ ។ ដូចនេះ $\boxed{f(x)=x^3-3x^2-9x+2}$ ។" "\n\n" r"២. ពេលនេះ $f'(x)=3x^2-6x-9=3(x+1)(x-3)$ មានសញ្ញាវិជ្ជមានក្រៅឫស និងអវិជ្ជមានចន្លោះឫស ។ លីមីតត្រង់ $\pm\infty$ គឺលីមីតនៃតួ $x^3$ ។" "\n" r"យើងគណនា $f(-1)=7$ និង $f(3)=-25$ ។ តារាងអថេរភាព ៖" "\n«T»\n" r"ដូចនេះ $f$ មានអតិបរមា $7$ ត្រង់ $x=-1$ និងអប្បបរមា $-25$ ត្រង់ $x=3$ ។" "\n\n" r"៣. ត្រង់ $x_0=0$ គេមាន $f(0)=2$ និង $f'(0)=-9$ ។ សមីការបន្ទាត់ប៉ះ $y-2=-9(x-0)$ ។ ដូចនេះ $\boxed{y=-9x+2}$ ហើយខ្សែកោងត្រូវបានសង់ដូចរូប ។",
       r"f(x)=x^3-3x^2-9x+2;\ y=-9x+2", d=3*(x+1)*(x-3), chk=[C("subs(diff(x**3-3*x**2-9*x+2,x),x,0)", -9, "slope")])
    # 2 rational parameters
    f = 2*x - 1 + 8/(x - 2)
    S = Q(f, "hand_find_parameters", crit=[0, 4], holes=[2], A=[("v", x-2), ("o", 2*x-1)])
    HR(S, r"គេឱ្យ $f(x)=ax+b+\frac{c}{x-2}$ ដែល $a,b,c$ ជាចំនួនពិត ។ ខ្សែកោង $(C)$ មានអាស៊ីមតូតទ្រេត $y=2x-1$ ហើយឆ្លងកាត់ចំណុច $A(3;13)$ ។" "\n" r"ក. រក $a,b,c$ ។" "\n" r"ខ. សិក្សាអថេរភាព រួចសង់តារាងអថេរភាពនៃ $f$ ។" "\n" r"គ. សង់ $(C)$ ។",
       r"ក. ដោយ $\lim_{x\to\pm\infty}\frac{c}{x-2}=0$ បន្ទាត់ $y=ax+b$ ជាអាស៊ីមតូតទ្រេត ។ ប្រៀបធៀបជាមួយ $y=2x-1$ គេបាន $a=2$ និង $b=-1$ ។" "\n" r"ដោយ $A\in(C)$ គេបាន $f(3)=13$ គឺ $5+c=13$ ឬ $c=8$ ។ ដូចនេះ $\boxed{f(x)=2x-1+\frac{8}{x-2}}$ ។" "\n\n" r"ខ. ដែនកំណត់ $D=IR-\{2\}$ ។ ដេរីវេ ៖" "\n" r"$$f'(x)=2-\frac{8}{(x-2)^2}=\frac{2(x-2)^2-8}{(x-2)^2}=\frac{2x(x-4)}{(x-2)^2}$$" "\n" r"ភាគបែងវិជ្ជមាន នោះសញ្ញានៃ $f'(x)$ អាស្រ័យលើ $x(x-4)$ ។ ឫសគឺ $x=0$ និង $x=4$ ។ ជំនួសគេបាន $f(0)=-5$ និង $f(4)=11$ ។" "\n" r"ដោយ $8>0$ ហើយ $x-2\to 0^{-}$ ពេល $x\to 2^{-}$ និង $x-2\to 0^{+}$ ពេល $x\to 2^{+}$ គេបាន $\lim_{x\to 2^{-}}f(x)=-\infty$ និង $\lim_{x\to 2^{+}}f(x)=+\infty$ ។" "\n«T»\n" r"ដូចនេះ $f$ មានអតិបរមា $-5$ និងអប្បបរមា $11$ ។" "\n\n" r"គ. គូសអាស៊ីមតូត $x=2$ និង $y=2x-1$ ដៅចំណុច $(0;-5)$ និង $(4;11)$ ហើយភ្ជាប់តាមតារាង ។ ដូចនេះ ក្រាបដូចរូប ។",
       r"f(x)=2x-1+\frac{8}{x-2}", d=2*x*(x-4)/(x-2)**2, chk=[C("subs(2*x-1+8/(x-2),x,3)", 13, "A on C"), C("limit(8/(x-2),x,oo)", 0, "oblique")])
    # 3 exp parameters
    f = (3*x + 2)*exp(-x)
    S = Q(f, "hand_find_parameters", crit=[R(1, 3)], A=[("h", sp.Integer(0))], tan=0)
    HR(S, r"ខ្សែកោង $(C)$ នៃអនុគមន៍ $f(x)=(ax+b)e^{-x}$ ឆ្លងកាត់ $B(0;2)$ ហើយបន្ទាត់ប៉ះ $(C)$ ត្រង់ $B$ មានមេគុណប្រាប់ទិសស្មើ $1$ ។ ចូររក $a,b$ រួចសិក្សាអនុគមន៍ដែលបាន ព្រមទាំងសង់ក្រាប ។",
       r"យើងមាន $f'(x)=ae^{-x}-(ax+b)e^{-x}=(-ax+a-b)e^{-x}$ តាមរូបមន្តដេរីវេនៃផលគុណ ។" "\n" r"លក្ខខណ្ឌ $f(0)=2$ ផ្ដល់ $b=2$ ។ លក្ខខណ្ឌ $f'(0)=1$ ផ្ដល់ $a-b=1$ ឬ $a=3$ ។ គេបាន $f(x)=(3x+2)e^{-x}$ កំណត់លើ $IR$ ។" "\n" r"លីមីត ៖ ត្រង់ $-\infty$ កត្តា $3x+2\to-\infty$ និង $e^{-x}\to+\infty$ នាំឱ្យ $\lim_{x\to-\infty}f(x)=-\infty$ ។ ត្រង់ $+\infty$ ដោយ $\lim_{x\to+\infty}xe^{-x}=0$ គេបាន $\lim_{x\to+\infty}f(x)=0$ នោះ $y=0$ ជាអាស៊ីមតូតដេក ។" "\n" r"ដេរីវេ $f'(x)=(1-3x)e^{-x}$ មានសញ្ញាដូច $1-3x$ ព្រោះ $e^{-x}>0$ ។ វាសូន្យត្រង់ $x=\frac{1}{3}$ ហើយ $f\left(\frac{1}{3}\right)=3e^{-\frac{1}{3}}$ ។" "\n«T»\n" r"ខ្សែកោងកាត់ $x'ox$ ត្រង់ $\left(-\frac{2}{3};0\right)$ និង $y'oy$ ត្រង់ $B(0;2)$ ។ បន្ទាត់ប៉ះត្រង់ $B$ គឺ $y=x+2$ ។" "\n" r"ដូចនេះ $a=3,\ b=2$ ហើយ $f$ មានអតិបរមា $3e^{-\frac{1}{3}}$ ត្រង់ $x=\frac{1}{3}$ ។",
       r"a=3,\ b=2;\ f_{\max}=3e^{-1/3}", d=(1-3*x)*exp(-x), chk=[C("subs((3*x+2)*exp(-x),x,0)", 2, "f(0)"), C("subs(diff((3*x+2)*exp(-x),x),x,0)", 1, "slope"), C("subs((3*x+2)*exp(-x),x,-2/3)", 0, "root")])
    # 4 ln parameters
    f = x**2 - 2*ln(x)
    S = Q(f, "hand_find_parameters", crit=[1], lo=sp.Integer(0), A=[("v", x)])
    HR(S, r"គេឱ្យ $f(x)=ax^2+b\ln x$ លើ $(0;+\infty)$ ។ រកចំនួនពិត $a,b$ ដើម្បីឱ្យ $f$ មានអប្បបរមាស្មើ $1$ ត្រង់ $x=1$ ។ បន្ទាប់មកសង់តារាងអថេរភាព និងក្រាបនៃ $f$ ។",
       r"គេមាន $f'(x)=2ax+\frac{b}{x}$ ។ បើ $f$ មានអប្បបរមា $1$ ត្រង់ $x=1$ នោះ $f(1)=1$ និង $f'(1)=0$ ។" "\n" r"$f(1)=a$ ផ្ដល់ $a=1$ ហើយ $f'(1)=2a+b=0$ ផ្ដល់ $b=-2$ ។" "\n" r"ផ្ទៀងផ្ទាត់ ៖ $f(x)=x^2-2\ln x$ មាន $f'(x)=2x-\frac{2}{x}=\frac{2(x-1)(x+1)}{x}$ ។ លើ $(0;+\infty)$ កត្តា $\frac{2(x+1)}{x}>0$ ដូច្នេះ $f'(x)$ មានសញ្ញាដូច $x-1$ គឺវាប្ដូរពីអវិជ្ជមានទៅវិជ្ជមានត្រង់ $x=1$ ។ លក្ខខណ្ឌពិតជាត្រូវ ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=+\infty$ ព្រោះ $\ln x\to-\infty$ នោះ $x=0$ ជាអាស៊ីមតូតឈរ ។ ម្យ៉ាងទៀត $f(x)=x^2\left(1-\frac{2\ln x}{x^2}\right)$ នាំឱ្យ $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n" r"ដូចនេះ $a=1,\ b=-2$ ហើយក្រាបដូចរូប ។",
       r"a=1,\ b=-2", d=2*(x-1)*(x+1)/x)
    # 5 rational with x^2+1
    f = (4*x - 3)/(x**2 + 1)
    S = Q(f, "hand_find_parameters", crit=[R(-1, 2), 2], A=[("h", sp.Integer(0))])
    HR(S, r"គេឱ្យអនុគមន៍ $f(x)=\frac{ax+b}{x^2+1}$ ។ ដឹងថា $f(0)=-3$ និង $f'(2)=0$ ។" "\n" r"១. បង្ហាញថា $a=4$ និង $b=-3$ ។" "\n" r"២. សិក្សាអថេរភាពនៃ $f$ ។" "\n" r"៣. ទាញបញ្ជាក់ថា $-4\le f(x)\le 1$ គ្រប់ $x$ ។" "\n" r"៤. សង់ក្រាប ។",
       r"១. $f(0)=b$ ដូច្នេះ $b=-3$ ។ តាមរូបមន្តផលចែក $f'(x)=\frac{a(x^2+1)-2x(ax+b)}{(x^2+1)^2}=\frac{-ax^2-2bx+a}{(x^2+1)^2}$ ។ លក្ខខណ្ឌ $f'(2)=0$ ផ្ដល់ $-4a-4b+a=0$ ឬ $3a=-4b=12$ ។ ដូចនេះ $a=4$ ។" "\n\n" r"២. $f(x)=\frac{4x-3}{x^2+1}$ កំណត់លើ $IR$ ។ គេបាន $f'(x)=\frac{-4x^2+6x+4}{(x^2+1)^2}=\frac{-2(2x+1)(x-2)}{(x^2+1)^2}$ ។" "\n" r"ឫសនៃភាគយក $x=-\frac{1}{2}$ និង $x=2$ ។ យើងគណនា $f\left(-\frac{1}{2}\right)=-4$ និង $f(2)=1$ ។ ដោយដឺក្រេភាគយកតូចជាងភាគបែង $\lim_{x\to\pm\infty}f(x)=0$ ។" "\n«T»\n\n" r"៣. តាមតារាង តម្លៃតូចបំផុតគឺ $-4$ និងធំបំផុតគឺ $1$ ។ ដូចនេះ $-4\le f(x)\le 1$ គ្រប់ $x\in IR$ ។" "\n\n" r"៤. អាស៊ីមតូតដេក $y=0$ ខ្សែកោងកាត់ $x'ox$ ត្រង់ $\left(\frac{3}{4};0\right)$ ។ ដូចនេះ ក្រាបដូចរូប ។",
       r"-4\le f(x)\le 1", d=-2*(2*x+1)*(x-2)/(x**2+1)**2, chk=[C("subs((4*x-3)/(x**2+1),x,0)", -3, "f(0)")])
    # 6
    f = exp(2*x) - 4*exp(x)
    S = Q(f, "hand_find_parameters", crit=[ln(2)], A=[("h", sp.Integer(0))])
    HR(S, r"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យអនុគមន៍ $f(x)=ae^{2x}+be^{x}$ ផ្ទៀងផ្ទាត់ $f(0)=-3$ និង $f'(\ln 2)=0$ ។ រួចសង់តារាងអថេរភាព ហើយរកចំណុចប្រសព្វនៃក្រាបជាមួយអ័ក្ស $x'ox$ ។",
       r"យើងមាន $f'(x)=2ae^{2x}+be^{x}$ ។ លក្ខខណ្ឌទាំងពីរក្លាយជាប្រព័ន្ធ $a+b=-3$ និង $8a+2b=0$ ។ ពីសមីការទីពីរ $b=-4a$ ជំនួសក្នុងសមីការទីមួយ $-3a=-3$ ។ ដូច្នេះ $a=1$ និង $b=-4$ ។" "\n" r"គេបាន $f(x)=e^{2x}-4e^{x}$ និង $f'(x)=2e^{x}(e^{x}-2)$ ។ ដោយ $2e^{x}>0$ សញ្ញានៃ $f'$ ដូច $e^{x}-2$ ៖ អវិជ្ជមានចំពោះ $x<\ln 2$ និងវិជ្ជមានចំពោះ $x>\ln 2$ ។" "\n" r"ត្រង់ $-\infty$ តួទាំងពីរខិតជិតសូន្យ នោះ $\lim_{x\to-\infty}f(x)=0$ ។ ត្រង់ $+\infty$ សរសេរ $f(x)=e^{2x}(1-4e^{-x})$ នោះលីមីតស្មើ $+\infty$ ។ តម្លៃអប្បបរមា $f(\ln 2)=4-8=-4$ ។" "\n«T»\n" r"សមីការ $f(x)=0$ សមមូល $e^{x}(e^{x}-4)=0$ ឬ $e^{x}=4$ គឺ $x=2\ln 2$ ។" "\n" r"ដូចនេះ $a=1,\ b=-4$ ហើយក្រាបកាត់ $x'ox$ ត្រង់ $(2\ln 2;0)$ ។",
       r"a=1,\ b=-4;\ (2\ln 2;0)", d=2*exp(x)*(exp(x)-2), chk=[C("subs(exp(2*x)-4*exp(x),x,0)", -3, "f(0)"), C("subs(exp(2*x)-4*exp(x),x,2*log(2))", 0, "root")])
    # 7 reading a table
    f = x + 2 + 4/(x + 1)
    S = Q(f, "hand_read_table", crit=[-3, 1], holes=[-1], A=[("v", x+1), ("o", x+2)])
    HR(S, r"អនុគមន៍ $f(x)=x+b+\frac{c}{x+1}$ មានតារាងអថេរភាពដូចខាងក្រោម ៖" "\n" f"$$\n{S.table}\n$$\n" r"១. អានតារាង រួចរក $b$ និង $c$ ។" "\n" r"២. ផ្ទៀងផ្ទាត់សញ្ញានៃ $f'(x)$ ដោយការគណនា ។" "\n" r"៣. សង់ខ្សែកោងនៃ $f$ ។",
       r"១. តារាងបង្ហាញថា $f'(1)=0$ និង $f(1)=5$ ។ ដោយ $f'(x)=1-\frac{c}{(x+1)^2}$ គេបាន $1-\frac{c}{4}=0$ ឬ $c=4$ ។ បន្ទាប់មក $f(1)=1+b+2=5$ ផ្ដល់ $b=2$ ។ ដូចនេះ $\boxed{f(x)=x+2+\frac{4}{x+1}}$ ។" "\n\n" r"២. $f'(x)=\frac{(x+1)^2-4}{(x+1)^2}=\frac{(x-1)(x+3)}{(x+1)^2}$ ។ ភាគបែងវិជ្ជមាន ហើយភាគយកមានឫស $-3$ និង $1$ ។ វាវិជ្ជមានក្រៅឫស និងអវិជ្ជមានចន្លោះឫស ដូច្នេះត្រូវនឹងតារាង ។ ម្យ៉ាងទៀត $f(-3)=-1-2=-3$ ក៏ត្រូវនឹងតារាងដែរ ។" "\n\n" r"៣. ខ្សែកោងមានអាស៊ីមតូតឈរ $x=-1$ និងអាស៊ីមតូតទ្រេត $y=x+2$ ព្រោះ $\lim_{x\to\pm\infty}\frac{4}{x+1}=0$ ។ ដូចនេះ ក្រាបដូចរូប ។",
       r"b=2,\ c=4", d=(x-1)*(x+3)/(x+1)**2)
    # 8
    f = x**3 - 3*x + 2
    S = Q(f, "hand_read_table", crit=[-1, 1], xint=[sp.Integer(-2), sp.Integer(1)], tan=0)
    HR(S, r"ពហុធា $f(x)=ax^3+bx^2+cx+d$ មានតារាងអថេរភាព ៖" "\n" f"$$\n{S.table}\n$$\n" r"រកមេគុណ $a,b,c,d$ ហើយដាក់ $f(x)$ ជាផលគុណកត្តា រួចទាញរកចំណុចប្រសព្វជាមួយអ័ក្ស $x'ox$ ។",
       r"តារាងផ្ដល់ព័ត៌មានបួន ៖ $f'(-1)=0$ , $f'(1)=0$ , $f(-1)=4$ , $f(1)=0$ ។" "\n" r"$f'(x)=3ax^2+2bx+c$ មានឫស $\pm 1$ ដូច្នេះ $f'(x)=3a(x^2-1)$ នាំឱ្យ $b=0$ និង $c=-3a$ ។" "\n" r"គេបាន $f(x)=ax^3-3ax+d$ ។ លក្ខខណ្ឌ $f(1)=-2a+d=0$ និង $f(-1)=2a+d=4$ ។ បូកសមីការទាំងពីរ $2d=4$ ឬ $d=2$ ហើយ $a=1$ ។" "\n" r"ដូចនេះ $f(x)=x^3-3x+2$ ។ ដោយ $1$ ជាឫសឌុប (អប្បបរមាស្មើសូន្យ) គេអាចសរសេរ $f(x)=(x-1)^2(x+2)$ ។" "\n" r"ខ្សែកោងប៉ះ $x'ox$ ត្រង់ $(1;0)$ ហើយកាត់ $x'ox$ ត្រង់ $(-2;0)$ ។ ដូចនេះ ចម្លើយគឺ $a=1,\ b=0,\ c=-3,\ d=2$ ។",
       r"f(x)=(x-1)^2(x+2)", d=3*(x-1)*(x+1), chk=[C("x**3-3*x+2", (x-1)**2*(x+2), "factor")])
    # 9 parallel tangents
    f = x**3 - 3*x**2 + 2
    S = Q(f, "hand_tangent_conditions", crit=[0, 2])
    HR(S, r"គេឱ្យ $f(x)=x^3-3x^2+2$ មានក្រាប $(C)$ ។" "\n" r"ក. សិក្សាអថេរភាពនៃ $f$ ។" "\n" r"ខ. រកសមីការបន្ទាត់ប៉ះនឹង $(C)$ ដែលស្របនឹងបន្ទាត់ $y=9x$ ។" "\n" r"គ. បង្ហាញថាចំណុចប៉ះទាំងពីរឆ្លុះគ្នាធៀបនឹង $I(1;0)$ ។",
       r"ក. $f'(x)=3x^2-6x=3x(x-2)$ ។ សូន្យត្រង់ $x=0$ និង $x=2$ ។ យើងបាន $f(0)=2$ និង $f(2)=-2$ ។ លីមីតត្រង់ $\pm\infty$ ស្មើលីមីតនៃ $x^3$ ។" "\n«T»\n\n" r"ខ. បន្ទាត់ប៉ះស្របនឹង $y=9x$ លុះត្រាតែមេគុណប្រាប់ទិសស្មើ $9$ ។ ដោះស្រាយ $3x^2-6x=9$ ឬ $x^2-2x-3=0$ គេបាន $x=-1$ ឬ $x=3$ ។" "\n" r"+ ត្រង់ $x=-1$ ៖ $f(-1)=-2$ បន្ទាត់ប៉ះ $y=9(x+1)-2=9x+7$ ។" "\n" r"+ ត្រង់ $x=3$ ៖ $f(3)=2$ បន្ទាត់ប៉ះ $y=9(x-3)+2=9x-25$ ។" "\n\n" r"គ. ចំណុចប៉ះគឺ $M(-1;-2)$ និង $N(3;2)$ ។ កណ្ដាល $MN$ មានកូអរដោនេ $\left(\frac{-1+3}{2};\frac{-2+2}{2}\right)=(1;0)$ ។ ដូចនេះ $M$ និង $N$ ឆ្លុះគ្នាធៀបនឹង $I(1;0)$ ។",
       r"y=9x+7;\ y=9x-25", d=3*x*(x-2), chk=[C("subs(diff(x**3-3*x**2+2,x),x,-1)", 9, "slope"), C("subs(diff(x**3-3*x**2+2,x),x,3)", 9, "slope"), C("subs(x**3-3*x**2+2,x,-1)+9*(x+1)", 9*x+7, "T1"), C("subs(x**3-3*x**2+2,x,3)+9*(x-3)", 9*x-25, "T2")])
    # 10 e^x tangent through origin
    f = exp(x) - EE*x
    S = Q(f, "hand_tangent_conditions", crit=[1], xint=[sp.Integer(1)])
    reshow(S, exp(x), (-3, 3), (-4, 10), lines=[EE * x], pts=[(1, 2.718)], alt="ក្រាប $(\\Gamma)$ នៃ $y=e^{x}$ និងបន្ទាត់ប៉ះ $y=ex$ ។")
    HR(S, r"តាង $(\Gamma)$ ជាក្រាបនៃ $y=e^{x}$ ។" "\n" r"១. រកបន្ទាត់ប៉ះនឹង $(\Gamma)$ ដែលឆ្លងកាត់គល់អ័ក្ស $O$ ។" "\n" r"២. សិក្សាអនុគមន៍ $f(x)=e^{x}-ex$ ។" "\n" r"៣. ទាញថា $(\Gamma)$ នៅខាងលើបន្ទាត់ប៉ះនោះជានិច្ច ។",
       r"១. យក $a$ ជាអាប់ស៊ីសនៃចំណុចប៉ះ ។ បន្ទាត់ប៉ះមានសមីការ $y=e^{a}(x-a)+e^{a}$ ។ វាឆ្លងកាត់ $O$ លុះត្រាតែ $0=e^{a}(1-a)$ គឺ $a=1$ ។ ដូចនេះ បន្ទាត់ប៉ះគឺ $y=ex$ ។" "\n\n" r"២. $f$ កំណត់លើ $IR$ ហើយ $f'(x)=e^{x}-e$ ។ ដោយ $e^{x}$ កើន គេបាន $f'(x)<0$ ចំពោះ $x<1$ និង $f'(x)>0$ ចំពោះ $x>1$ ។ តម្លៃ $f(1)=0$ ។" "\n" r"លីមីត ៖ $\lim_{x\to-\infty}f(x)=+\infty$ ព្រោះ $e^{x}\to 0$ និង $-ex\to+\infty$ ។ សរសេរ $f(x)=e^{x}(1-exe^{-x})$ គេបាន $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n\n" r"៣. តាមតារាង $f(x)\ge 0$ គ្រប់ $x$ គឺ $e^{x}\ge ex$ ។ ដូចនេះ $(\Gamma)$ នៅខាងលើបន្ទាត់ $y=ex$ ហើយប៉ះត្រង់ $(1;e)$ តែមួយគត់ ។",
       r"y=ex;\ e^{x}\ge ex", d=exp(x)-EE, chk=[C("subs(exp(x)-E*x,x,1)", 0, "min")], sub="hand_tangent_conditions")
    # 11
    f = x/EE - ln(x)
    S = Q(f, "hand_tangent_conditions", crit=[EE], lo=sp.Integer(0), A=[("v", x)])
    HR(S, r"ខ្សែកោង $(L)$ មានសមីការ $y=\ln x$ ។ ចូរកំណត់បន្ទាត់ប៉ះ $(L)$ ដែលឆ្លងកាត់ $O(0;0)$ ។ រួចសិក្សាអនុគមន៍ $f(x)=\frac{x}{e}-\ln x$ លើ $(0;+\infty)$ ដើម្បីបង្ហាញថា $\ln x\le\frac{x}{e}$ ។",
       r"ចំណុចប៉ះមានអាប់ស៊ីស $a>0$ បន្ទាត់ប៉ះគឺ $y=\frac{1}{a}(x-a)+\ln a$ ។ ដាក់ $x=0,\ y=0$ គេបាន $\ln a=1$ ឬ $a=e$ ។ បន្ទាត់ដែលរកគឺ $y=\frac{x}{e}$ ។" "\n" r"ឥឡូវយើងសិក្សា $f$ ។ $f'(x)=\frac{1}{e}-\frac{1}{x}=\frac{x-e}{ex}$ មានសញ្ញាដូច $x-e$ លើ $(0;+\infty)$ ។ តម្លៃត្រង់ចំណុចបរមា $f(e)=1-1=0$ ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=+\infty$ និង $f(x)=x\left(\frac{1}{e}-\frac{\ln x}{x}\right)$ នាំឱ្យ $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n" r"អប្បបរមានៃ $f$ ស្មើ $0$ ។ ដូចនេះ $f(x)\ge 0$ គឺ $\ln x\le\frac{x}{e}$ គ្រប់ $x>0$ ។",
       r"y=\frac{x}{e};\ \ln x\le\frac{x}{e}", d=(x-EE)/(EE*x))
    # 12
    f = (x - 1)/(x + 1)
    S = Q(f, "hand_tangent_conditions", holes=[-1], A=[("v", x+1), ("h", sp.Integer(1))])
    addlines(S, [2 * x - 1, 2 * x + 7], alt="ក្រាបនៃអនុគមន៍ ជាមួយបន្ទាត់ប៉ះ $y=2x-1$ និង $y=2x+7$ ។")
    HR(S, r"អនុគមន៍ហូម៉ូក្រាហ្វិក"[:0] + r"គេមាន $f(x)=\frac{x-1}{x+1}$ ។ បន្ទាត់ប៉ះនឹងក្រាបមួយណាខ្លះមានមេគុណប្រាប់ទិសស្មើ $2$ ? ចូរឆ្លើយ ដោយសិក្សាអនុគមន៍នេះជាមុន ហើយសង់ក្រាបជាមួយបន្ទាត់ទាំងនោះ ។",
       r"ដំបូង $D=IR-\{-1\}$ ។ តាមរូបមន្តផលចែក $f'(x)=\frac{(x+1)-(x-1)}{(x+1)^2}=\frac{2}{(x+1)^2}>0$ ដូច្នេះ $f$ កើនលើចន្លោះនីមួយៗនៃ $D$ ។" "\n" r"$\lim_{x\to\pm\infty}f(x)=1$ ហើយនៅជិត $-1$ ភាគយកខិតជិត $-2$ គេបាន $\lim_{x\to(-1)^{-}}f(x)=+\infty$ និង $\lim_{x\to(-1)^{+}}f(x)=-\infty$ ។" "\n«T»\n" r"មេគុណប្រាប់ទិសស្មើ $2$ លុះត្រាតែ $(x+1)^2=1$ គឺ $x=0$ ឬ $x=-2$ ។" "\n" r"+ ត្រង់ $x=0$ ៖ $f(0)=-1$ ដូច្នេះ $y=2x-1$ ។" "\n" r"+ ត្រង់ $x=-2$ ៖ $f(-2)=3$ ដូច្នេះ $y=2(x+2)+3=2x+7$ ។" "\n" r"ដូចនេះ មានបន្ទាត់ប៉ះពីរគឺ $y=2x-1$ និង $y=2x+7$ ។",
       r"y=2x-1;\ y=2x+7", d=2/(x+1)**2, chk=[C("subs(diff((x-1)/(x+1),x),x,0)", 2, "m"), C("subs(diff((x-1)/(x+1),x),x,-2)", 2, "m"), C("subs((x-1)/(x+1),x,-2)", 3, "y")])
    # 13 delta method
    f = x + 4/x
    S = Q(f, "hand_tangent_conditions", crit=[-2, 2], holes=[0], A=[("v", x), ("o", x)])
    HR(S, r"គេឱ្យ $f(x)=x+\frac{4}{x}$ និងបន្ទាត់ $(d_m):y=-3x+m$ ។" "\n" r"១. សង់តារាងអថេរភាពនៃ $f$ ។" "\n" r"២. រកតម្លៃ $m$ ដើម្បីឱ្យ $(d_m)$ ប៉ះនឹងក្រាបនៃ $f$ ។",
       r"១. $D=IR-\{0\}$ ។ $f'(x)=1-\frac{4}{x^2}=\frac{(x-2)(x+2)}{x^2}$ ។ វាសូន្យត្រង់ $x=\pm 2$ ហើយ $f(-2)=-4$ , $f(2)=4$ ។ បន្ទាត់ $x=0$ ជាអាស៊ីមតូតឈរ និង $y=x$ ជាអាស៊ីមតូតទ្រេត ។" "\n«T»\n\n" r"២. អាប់ស៊ីសចំណុចប្រសព្វផ្ទៀងផ្ទាត់ $x+\frac{4}{x}=-3x+m$ ឬ $4x^2-mx+4=0$ ។" "\n" r"បន្ទាត់ប៉ះនឹងក្រាបលុះត្រាតែសមីការនេះមានឫសឌុប គឺ $\Delta=m^2-64=0$ ។ គេបាន $m=8$ ឬ $m=-8$ ។" "\n" r"ចំពោះ $m=8$ ឫសឌុបគឺ $x=1$ ហើយចំពោះ $m=-8$ ឫសឌុបគឺ $x=-1$ ។ ផ្ទៀងផ្ទាត់ $f'(\pm 1)=-3$ ត្រឹមត្រូវ ។" "\n" r"ដូចនេះ $\boxed{m=8}$ ឬ $\boxed{m=-8}$ ។",
       r"m=\pm 8", d=(x-2)*(x+2)/x**2, chk=[C("subs(diff(x+4/x,x),x,1)", -3, "m"), C("subs(diff(x+4/x,x),x,-1)", -3, "m"), C("subs(x+4/x,x,1)+3", 8, "m value")])
    # 14-18 inequalities
    f = exp(x) - x - 1
    S = Q(f, "hand_inequality_by_study", crit=[0], xint=[sp.Integer(0)])
    reshow(S, exp(x), (-3, 3), (-2, 8), lines=[x + 1], pts=[(0, 1)], alt="ក្រាបនៃ $y=e^{x}$ នៅខាងលើបន្ទាត់ប៉ះ $y=x+1$ ។")
    HR(S, r"ស្រាយបញ្ជាក់វិសមភាព $e^{x}\ge x+1$ គ្រប់ចំនួនពិត $x$ ដោយសិក្សាអនុគមន៍ $f(x)=e^{x}-x-1$ ។ រួចបកស្រាយវិសមភាពនេះតាមក្រាបនៃ $y=e^{x}$ ។",
       r"យើងសិក្សា $f$ លើ $IR$ ។ ដេរីវេ $f'(x)=e^{x}-1$ ។ ដោយ $e^{x}<1$ ចំពោះ $x<0$ និង $e^{x}>1$ ចំពោះ $x>0$ គេបានសញ្ញានៃ $f'$ ភ្លាម ។" "\n" r"ត្រង់ $-\infty$ តួ $e^{x}$ រលត់ នោះ $f(x)$ ខិតជិត $-x-1$ ហើយលីមីតស្មើ $+\infty$ ។ ត្រង់ $+\infty$ គេសរសេរ $f(x)=e^{x}\left(1-\frac{x+1}{e^{x}}\right)$ លីមីតស្មើ $+\infty$ ។" "\n«T»\n" r"អប្បបរមា $f(0)=0$ ដូច្នេះ $f(x)\ge 0$ គ្រប់ $x$ ។ ដូចនេះ $e^{x}\ge x+1$ ។" "\n" r"តាមក្រាប ៖ $y=x+1$ គឺបន្ទាត់ប៉ះនឹង $y=e^{x}$ ត្រង់ $(0;1)$ ហើយខ្សែកោងនៅខាងលើបន្ទាត់ប៉ះនេះ ។",
       r"e^{x}\ge x+1", d=exp(x)-1, chk=[C("subs(exp(x),x,0)+subs(diff(exp(x),x),x,0)*x", x+1, "tangent")])
    f = x - 1 - ln(x)
    S = Q(f, "hand_inequality_by_study", crit=[1], lo=sp.Integer(0), A=[("v", x)], xint=[sp.Integer(1)])
    HR(S, r"បង្ហាញថា $\ln x\le x-1$ ចំពោះគ្រប់ $x>0$ ។ សមភាពកើតឡើងនៅពេលណា ? ប្រើវិសមភាពនេះដើម្បីបង្ហាញថា $\ln 2<1$ ។",
       r"តាង $f(x)=x-1-\ln x$ លើ $D=(0;+\infty)$ ។ គេបាន $f'(x)=1-\frac{1}{x}=\frac{x-1}{x}$ ។ ដោយ $x>0$ សញ្ញានៃ $f'$ គឺសញ្ញានៃ $x-1$ ។" "\n" r"លីមីត ៖ $\lim_{x\to 0^{+}}f(x)=+\infty$ ព្រោះ $-\ln x\to+\infty$ ហើយ $f(x)=x\left(1-\frac{1}{x}-\frac{\ln x}{x}\right)$ ផ្ដល់ $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n" r"តម្លៃតូចបំផុតគឺ $f(1)=0$ ដូច្នេះ $f(x)\ge 0$ គឺ $\ln x\le x-1$ ។ សមភាពកើតឡើងតែត្រង់ $x=1$ ប៉ុណ្ណោះ ។" "\n" r"យក $x=2\neq 1$ គេបានវិសមភាពដាច់ខាត $\ln 2<2-1=1$ ។ ដូចនេះ $\ln 2<1$ ។",
       r"\ln x\le x-1", d=(x-1)/x)
    f = x - ln(1 + x)
    S = Q(f, "hand_inequality_by_study", crit=[0], lo=sp.Integer(-1), A=[("v", x+1)], xint=[sp.Integer(0)])
    HR(S, r"លើចន្លោះ $(-1;+\infty)$ គេឱ្យ $f(x)=x-\ln(1+x)$ ។ សិក្សាអថេរភាព រួចទាញថា $\ln(1+x)\le x$ ។ គណនាផងដែរនូវសមីការបន្ទាត់ប៉ះនៃ $y=\ln(1+x)$ ត្រង់គល់អ័ក្ស ។",
       r"អនុគមន៍មានន័យលុះត្រាតែ $1+x>0$ ឬ $x>-1$ ។ តាមរូបមន្ត $(\ln u)'=\frac{u'}{u}$ គេបាន $f'(x)=1-\frac{1}{1+x}=\frac{x}{1+x}$ ។" "\n" r"ភាគបែងវិជ្ជមានលើដែនកំណត់ ដូច្នេះ $f'$ មានសញ្ញាដូច $x$ ។" "\n" r"ពេល $x\to(-1)^{+}$ គេបាន $\ln(1+x)\to-\infty$ នោះ $f(x)\to+\infty$ ។ ពេល $x\to+\infty$ គេសរសេរ $f(x)=x\left(1-\frac{\ln(1+x)}{x}\right)$ នោះ $f(x)\to+\infty$ ។" "\n«T»\n" r"$f(0)=0$ ជាអប្បបរមា ដូច្នេះ $\ln(1+x)\le x$ ។" "\n" r"ត្រង់ $x=0$ អនុគមន៍ $y=\ln(1+x)$ មានតម្លៃ $0$ និងដេរីវេ $1$ ។ ដូចនេះ បន្ទាត់ប៉ះគឺ $y=x$ ហើយខ្សែកោងនៅខាងក្រោមបន្ទាត់នេះ ។",
       r"\ln(1+x)\le x;\ y=x", d=x/(1+x), chk=[C("subs(diff(log(1+x),x),x,0)", 1, "slope")])
    f = x*ln(x) - x + 1
    S = Q(f, "hand_inequality_by_study", crit=[1], lo=sp.Integer(0), xint=[sp.Integer(1)])
    HR(S, r"គេកំណត់ $f(x)=x\ln x-x+1$ ចំពោះ $x>0$ ។ រក $\lim_{x\to 0^{+}}f(x)$ និង $\lim_{x\to+\infty}f(x)$ ហើយបង្ហាញថា $x\ln x\ge x-1$ ។",
       r"ដោយលីមីតគោល $\lim_{x\to 0^{+}}x\ln x=0$ គេបាន $\lim_{x\to 0^{+}}f(x)=1$ ។ ដូច្នេះ បន្ទាត់ $x=0$ មិនមែនជាអាស៊ីមតូតទេ ។" "\n" r"សរសេរ $f(x)=x(\ln x-1)+1$ ។ ពេល $x\to+\infty$ កត្តាទាំងពីរខិតជិត $+\infty$ ដូច្នេះ $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n" r"តាម $(uv)'=u'v+uv'$ គេបាន $f'(x)=\ln x+1-1=\ln x$ ។ វាអវិជ្ជមានលើ $(0;1)$ វិជ្ជមានលើ $(1;+\infty)$ និងសូន្យត្រង់ $x=1$ ។" "\n«T»\n" r"អប្បបរមា $f(1)=0$ នាំឱ្យ $f(x)\ge 0$ ។ ដូចនេះ $x\ln x\ge x-1$ គ្រប់ $x>0$ ។",
       r"x\ln x\ge x-1", d=ln(x))
    f = exp(x) + x**2/2 - x
    S = Q(f, "hand_two_stage_study", crit=[0])
    HR(S, r"ផ្នែកទី១ ៖ គេឱ្យ $g(x)=e^{x}+x-1$ ។ បង្ហាញថា $g$ កើនលើ $IR$ ហើយកំណត់សញ្ញានៃ $g(x)$ ។" "\n" r"ផ្នែកទី២ ៖ គេឱ្យ $f(x)=e^{x}+\frac{x^2}{2}-x$ ។ បង្ហាញថា $f'(x)=g(x)$ រួចសង់តារាងអថេរភាពនៃ $f$ និងទាញថា $f(x)\ge 1$ ។",
       r"ផ្នែកទី១ ៖ $g'(x)=e^{x}+1>0$ ដូច្នេះ $g$ កើនលើ $IR$ ។ ដោយ $g(0)=0$ គេបាន $g(x)<0$ ចំពោះ $x<0$ និង $g(x)>0$ ចំពោះ $x>0$ ។" "\n\n" r"ផ្នែកទី២ ៖ ធ្វើដេរីវេតាមតួ $f'(x)=e^{x}+x-1=g(x)$ ។ តាមផ្នែកទី១ $f'$ អវិជ្ជមានមុន $0$ និងវិជ្ជមានក្រោយ $0$ ។" "\n" r"ត្រង់ $-\infty$ តួ $\frac{x^2}{2}-x$ ខិតជិត $+\infty$ ហើយ $e^{x}\to 0$ ។ ត្រង់ $+\infty$ $f(x)=e^{x}+x\left(\frac{x}{2}-1\right)$ ខិតជិត $+\infty$ ។ ហើយ $f(0)=1$ ។" "\n«T»\n" r"ដូចនេះ $f(x)\ge f(0)=1$ គ្រប់ $x\in IR$ ។",
       r"f(x)\ge 1", d=exp(x)+x-1, chk=[C("subs(exp(x)+x-1,x,0)", 0, "g(0)"), C("diff(exp(x)+x-1,x)", exp(x)+1, "g'")])
    # 19 two curves
    f = x**3 - 3*x
    S = Q(f, "hand_two_curves", crit=[-1, 1], xint=[-sp.sqrt(3), sp.Integer(0), sp.sqrt(3)])
    addlines(S, [x + 0], alt="ក្រាប $(C)$ និងបន្ទាត់ $(d):y=x$ ។")
    HR(S, r"ក្នុងលំហាត់នេះ $(C)$ ជាក្រាបនៃ $f(x)=x^3-3x$ និង $(d)$ ជាបន្ទាត់ $y=x$ ។" "\n" r"ក. បង្ហាញថា $f$ ជាអនុគមន៍សេស រួចសិក្សាអថេរភាព ។" "\n" r"ខ. រកចំណុចប្រសព្វនៃ $(C)$ និង $(d)$ ។" "\n" r"គ. សិក្សាទីតាំងនៃ $(C)$ ធៀបនឹង $(d)$ ។",
       r"ក. ចំពោះគ្រប់ $x$ គេមាន $f(-x)=-x^3+3x=-f(x)$ ដូច្នេះ $f$ សេស ហើយ $O$ ជាផ្ចិតឆ្លុះនៃ $(C)$ ។" "\n" r"$f'(x)=3x^2-3=3(x-1)(x+1)$ ។ តម្លៃ $f(-1)=2$ និង $f(1)=-2$ ។" "\n«T»\n\n" r"ខ. $f(x)=x$ សមមូល $x^3-4x=0$ ឬ $x(x-2)(x+2)=0$ ។ ដូចនេះ ចំណុចប្រសព្វគឺ $(-2;-2)$ , $(0;0)$ , $(2;2)$ ។" "\n\n" r"គ. សញ្ញានៃ $f(x)-x=x(x-2)(x+2)$ ៖ អវិជ្ជមានលើ $(-\infty;-2)$ និង $(0;2)$ វិជ្ជមានលើ $(-2;0)$ និង $(2;+\infty)$ ។ ដូចនេះ $(C)$ នៅខាងលើ $(d)$ លើ $(-2;0)$ និង $(2;+\infty)$ ហើយនៅខាងក្រោមលើចន្លោះពីរផ្សេងទៀត ។",
       r"(-2;-2),(0;0),(2;2)", d=3*(x-1)*(x+1), chk=[C("subs(x**3-3*x,x,2)", 2, "pt"), C("subs(x**3-3*x,x,-2)", -2, "pt"), C("(-x)**3-3*(-x)+x**3-3*x", 0, "odd")])
    f = x + 1 + 1/x
    S = Q(f, "hand_two_curves", crit=[-1, 1], holes=[0], A=[("v", x), ("o", x+1)])
    HR(S, r"អនុគមន៍ $f(x)=\frac{x^2+x+1}{x}$ មានក្រាប $(C)$ ។ បន្ទាត់ដេក $y=3$ មានទំនាក់ទំនងអ្វីជាមួយ $(C)$ ? ចូរសិក្សា $f$ ឱ្យពេញលេញ រួចឆ្លើយសំណួរនេះ ។",
       r"ភាគបែងត្រូវខុសពីសូន្យ ដូច្នេះ $D=IR-\{0\}$ ។ ចែកភាគយកនឹង $x$ គេបាន $f(x)=x+1+\frac{1}{x}$ ។" "\n" r"$\lim_{x\to\pm\infty}\frac{1}{x}=0$ នោះ $y=x+1$ ជាអាស៊ីមតូតទ្រេត ហើយ $\lim_{x\to 0^{-}}f(x)=-\infty$ , $\lim_{x\to 0^{+}}f(x)=+\infty$ នោះ $x=0$ ជាអាស៊ីមតូតឈរ ។" "\n" r"$f'(x)=1-\frac{1}{x^2}=\frac{(x-1)(x+1)}{x^2}$ ។ ជំនួស $f(-1)=-1$ និង $f(1)=3$ ។" "\n«T»\n" r"$f(x)=3$ សមមូល $x^2-2x+1=0$ ឬ $(x-1)^2=0$ ជាឫសឌុប ។ ដូចនេះ បន្ទាត់ $y=3$ ប៉ះ $(C)$ ត្រង់អប្បបរមា $(1;3)$ ។",
       r"(1;3)", d=(x-1)*(x+1)/x**2)
    f = exp(x) - x
    S = Q(f, "hand_two_curves", crit=[0])
    reshow(S, exp(x), (-3, 6), (-3, 6), curves=[(ln(x), 0.05)], lines=[x + 0], alt="ខ្សែកោង $y=e^{x}$ និង $y=\\ln x$ ឆ្លុះគ្នាធៀបនឹងបន្ទាត់ $y=x$ ។")
    HR(S, r"ខ្សែកោង $y=e^{x}$ និង $y=\ln x$ ឆ្លុះគ្នាធៀបនឹងបន្ទាត់ $y=x$ ។ សិក្សា $f(x)=e^{x}-x$ ហើយប្រើលទ្ធផលដើម្បីបង្ហាញថាខ្សែកោងទាំងពីរមិនកាត់គ្នាទេ ។",
       r"យើងមាន $f'(x)=e^{x}-1$ ។ ដេរីវេនេះសូន្យត្រង់ $x=0$ អវិជ្ជមានមុន និងវិជ្ជមានក្រោយ ។ លីមីតត្រង់ $-\infty$ ស្មើ $+\infty$ ព្រោះ $-x\to+\infty$ ហើយត្រង់ $+\infty$ ស្មើ $+\infty$ ព្រោះ $f(x)=e^{x}\left(1-xe^{-x}\right)$ ។" "\n«T»\n" r"អប្បបរមា $f(0)=1>0$ ដូច្នេះ $e^{x}>x$ គ្រប់ $x$ ។ ខ្សែកោង $y=e^{x}$ នៅខាងលើ $y=x$ ជានិច្ច ។" "\n" r"ដោយឆ្លុះធៀបនឹង $y=x$ ខ្សែកោង $y=\ln x$ នៅខាងក្រោម $y=x$ ជានិច្ច ។ ដូចនេះ ខ្សែកោងទាំងពីរមិនកាត់គ្នាទេ ។",
       r"e^{x}>x", d=exp(x)-1)
    f = ln(x)*(1 - ln(x))
    S = Q(sp.expand(f), "hand_two_curves", crit=[sp.sqrt(EE)], lo=sp.Integer(0), A=[("v", x)], xint=[sp.Integer(1), EE])
    reshow(S, ln(x), (-1, 8), (-3, 5), curves=[(ln(x)**2, 0.1)], pts=[(1, 0), (2.718, 1)], start=0.05, alt="ក្រាបនៃ $u(x)=\\ln x$ និង $v(x)=\\ln^{2}x$ ។")
    HR(S, r"លើ $(0;+\infty)$ គេឱ្យ $u(x)=\ln x$ និង $v(x)=\ln^2 x$ ។ តាង $f(x)=u(x)-v(x)$ ។" "\n" r"១. រកអាប់ស៊ីសចំណុចប្រសព្វនៃក្រាបទាំងពីរ ។" "\n" r"២. សិក្សាអថេរភាពនៃ $f$ ។" "\n" r"៣. នៅចន្លោះណាដែលក្រាប $u$ នៅខាងលើក្រាប $v$ ?",
       r"១. $u(x)=v(x)$ សមមូល $\ln x(1-\ln x)=0$ គឺ $\ln x=0$ ឬ $\ln x=1$ ។ ដូចនេះ $x=1$ ឬ $x=e$ ។" "\n\n" r"២. $f(x)=\ln x-\ln^2 x$ ហើយ $f'(x)=\frac{1}{x}-\frac{2\ln x}{x}=\frac{1-2\ln x}{x}$ ។ ដោយ $x>0$ សញ្ញានៃ $f'$ ដូច $1-2\ln x$ ។ វាសូន្យត្រង់ $x=\sqrt{e}$ ។ ជំនួស $\ln\sqrt{e}=\frac{1}{2}$ គេបាន $f(\sqrt{e})=\frac{1}{4}$ ។" "\n" r"តាង $t=\ln x$ គេបាន $f=t-t^2$ ដូច្នេះលីមីតត្រង់ $0^{+}$ និង $+\infty$ ស្មើ $-\infty$ ។" "\n«T»\n\n" r"៣. តាមតារាង $f(x)>0$ លុះត្រាតែ $1<x<e$ ។ ដូចនេះ ក្រាប $u$ នៅខាងលើក្រាប $v$ លើចន្លោះ $(1;e)$ ។",
       r"(1;e)", d=(1-2*ln(x))/x, chk=[C("subs(log(x)-log(x)**2,x,E)", 0, "root")])
    f = x*exp(-x)
    S = Q(f, "hand_deduced_inequality", crit=[1], A=[("h", sp.Integer(0))], xint=[sp.Integer(0)], tan=0)
    HR(S, r"គេឱ្យ $f(x)=xe^{-x}$ ។ សិក្សាអនុគមន៍ $f$ សង់តារាងអថេរភាព និងក្រាប រួចទាញបញ្ជាក់ថា $ex\le e^{x}$ ចំពោះគ្រប់ចំនួនពិត $x$ ។",
       r"$f$ កំណត់លើ $IR$ ។ តាមរូបមន្តផលគុណ $f'(x)=e^{-x}-xe^{-x}=(1-x)e^{-x}$ ។" "\n" r"លីមីត ៖ $\lim_{x\to-\infty}f(x)=-\infty$ ព្រោះ $x\to-\infty$ និង $e^{-x}\to+\infty$ ។ $\lim_{x\to+\infty}xe^{-x}=0$ ដូច្នេះ $y=0$ ជាអាស៊ីមតូតដេកត្រង់ $+\infty$ ។" "\n" r"តម្លៃអតិបរមា $f(1)=e^{-1}$ ។" "\n«T»\n" r"ក្រាបឆ្លងកាត់ $O$ ហើយបន្ទាត់ប៉ះត្រង់ $O$ គឺ $y=x$ ។" "\n" r"ពីតារាង $xe^{-x}\le e^{-1}$ ។ គុណអង្គទាំងពីរនឹង $e\cdot e^{x}>0$ គេបាន $ex\le e^{x}$ ។ ដូចនេះ វិសមភាពត្រូវបានស្រាយបញ្ជាក់ ។",
       r"f_{\max}=e^{-1}", d=(1-x)*exp(-x))
    # families with parameter
    f = x**3 - 3*x + 2
    S = Q(f + 0, "hand_parameter_family", crit=[-1, 1], key="fam1")
    HR(S, r"ចំពោះចំនួនពិត $m$ គេឱ្យ $f_m(x)=x^3-3mx+2$ ។" "\n" r"១. ពិភាក្សាតាម $m$ ថាតើ $f_m$ មានបរមាឬទេ ។" "\n" r"២. ករណី $m=1$ សង់តារាងអថេរភាព និងក្រាប ។" "\n" r"៣. បង្ហាញថាក្រាបគ្រប់ $f_m$ ឆ្លងកាត់ចំណុចនឹងមួយ ។",
       r"១. $f_m'(x)=3x^2-3m=3(x^2-m)$ ។" "\n" r"+ បើ $m\le 0$ នោះ $x^2-m\ge 0$ ដូច្នេះ $f_m$ កើនជានិច្ច ហើយគ្មានបរមាទេ ។" "\n" r"+ បើ $m>0$ នោះ $f_m'$ មានឫសពីរ $\pm\sqrt{m}$ ហើយប្ដូរសញ្ញា ដូច្នេះ $f_m$ មានអតិបរមាត្រង់ $x=-\sqrt{m}$ និងអប្បបរមាត្រង់ $x=\sqrt{m}$ ។" "\n\n" r"២. ចំពោះ $m=1$ ៖ $f(x)=x^3-3x+2$ , $f'(x)=3(x-1)(x+1)$ , $f(-1)=4$ , $f(1)=0$ ។" "\n«T»\n\n" r"៣. តួដែលមាន $m$ គឺ $-3mx$ ។ វាសូន្យគ្រប់ $m$ លុះត្រាតែ $x=0$ ហើយពេលនោះ $f_m(0)=2$ ។ ដូចនេះ ចំណុចនឹងគឺ $(0;2)$ ។",
       r"(0;2)", d=3*(x-1)*(x+1))
    f = x + 1/(x - 1)
    S = Q(f, "hand_parameter_family", crit=[0, 2], holes=[1], A=[("v", x-1), ("o", x)])
    HR(S, r"គេឱ្យគ្រួសារអនុគមន៍ $f_m(x)=\frac{x^2+mx+1}{x-1}$ ដែល $m$ ជាប៉ារ៉ាម៉ែត្រ ។ រកចំណុចនឹងដែលខ្សែកោងទាំងអស់ឆ្លងកាត់ ។ រួចសិក្សាករណី $m=-1$ ។",
       r"យក $m_1\neq m_2$ ។ ចំណុចរួមផ្ទៀងផ្ទាត់ $f_{m_1}(x)=f_{m_2}(x)$ ឬ $(m_1-m_2)x=0$ ។ ដូច្នេះ $x=0$ ហើយ $f_m(0)=-1$ មិនអាស្រ័យនឹង $m$ ។ កូអរដោនេចំណុចនឹងគឺ $(0;-1)$ ។" "\n" r"ចំពោះ $m=-1$ ៖ $f(x)=\frac{x^2-x+1}{x-1}$ ។ ចែកពហុធា គេបាន $x^2-x+1=x(x-1)+1$ នោះរាងកាណូនិកគឺ $f(x)=x+\frac{1}{x-1}$ ។" "\n" r"$D=IR-\{1\}$ ។ $f'(x)=1-\frac{1}{(x-1)^2}=\frac{x(x-2)}{(x-1)^2}$ ។ ឫស $x=0$ និង $x=2$ ជាមួយ $f(0)=-1$ , $f(2)=3$ ។" "\n" r"អាស៊ីមតូតឈរ $x=1$ និងអាស៊ីមតូតទ្រេត $y=x$ ។" "\n«T»\n" r"ផ្ចិតឆ្លុះគឺប្រសព្វនៃអាស៊ីមតូតទាំងពីរ $I(1;1)$ ។ ដូចនេះ ក្រាបដូចរូប ។",
       r"(0;-1)", d=x*(x-2)/(x-1)**2, chk=[C("subs(x+1/(x-1),x,0)", -1, "fixed point")])
    f = ln(x) - x
    S = Q(f, "hand_parameter_family", crit=[1], lo=sp.Integer(0), A=[("v", x)])
    HR(S, r"គេឱ្យ $f_m(x)=mx+\ln x$ លើ $(0;+\infty)$ ។ តើ $m$ ត្រូវមានលក្ខខណ្ឌអ្វីដើម្បីឱ្យ $f_m$ មានអតិបរមា ? ករណី $m=-1$ សង់តារាងអថេរភាព ហើយទាញថា $\ln x<x$ ។",
       r"$f_m'(x)=m+\frac{1}{x}=\frac{mx+1}{x}$ ។ បើ $m\ge 0$ នោះ $f_m'(x)>0$ ហើយ $f_m$ កើន គ្មានបរមា ។ បើ $m<0$ នោះ $f_m'$ សូន្យត្រង់ $x=-\frac{1}{m}>0$ ហើយប្ដូរពីវិជ្ជមានទៅអវិជ្ជមាន ដូច្នេះមានអតិបរមា ។ លក្ខខណ្ឌគឺ $m<0$ ។" "\n" r"ចំពោះ $m=-1$ ៖ $f(x)=\ln x-x$ , $f'(x)=\frac{1-x}{x}$ ។ $\lim_{x\to 0^{+}}f(x)=-\infty$ ហើយសរសេរ $f(x)=x\left(\frac{\ln x}{x}-1\right)$ ផ្ដល់ $\lim_{x\to+\infty}f(x)=-\infty$ ។" "\n«T»\n" r"អតិបរមា $f(1)=-1<0$ ។ ដូចនេះ $\ln x-x<0$ គឺ $\ln x<x$ គ្រប់ $x>0$ ។",
       r"m<0;\ \ln x<x", d=(1-x)/x)
    f = ln(x)/x
    S = Q(f, "hand_equation_discussion", crit=[EE], lo=sp.Integer(0), A=[("v", x), ("h", sp.Integer(0))], xint=[sp.Integer(1)])
    HR(S, r"ពិភាក្សាចំនួនឫសនៃសមីការ $\ln x=mx$ ($x>0$) តាមតម្លៃប៉ារ៉ាម៉ែត្រ $m$ ដោយប្រើអនុគមន៍ $f(x)=\frac{\ln x}{x}$ ។",
       r"ដោយ $x>0$ សមីការសមមូល $f(x)=m$ ។ ដូច្នេះយើងត្រូវការតារាងអថេរភាពនៃ $f$ ។" "\n" r"$f'(x)=\frac{\frac{1}{x}\cdot x-\ln x}{x^2}=\frac{1-\ln x}{x^2}$ មានសញ្ញាដូច $1-\ln x$ ។ វាសូន្យត្រង់ $x=e$ ហើយ $f(e)=e^{-1}$ ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=-\infty$ និង $\lim_{x\to+\infty}f(x)=0$ ។" "\n«T»\n" r"អានតារាង ៖" "\n" r"+ បើ $m\le 0$ បន្ទាត់ $y=m$ កាត់ខ្សែកោងលើសាខាកើនតែមួយដង សមីការមានឫសមួយ ។" "\n" r"+ បើ $0<m<e^{-1}$ សមីការមានឫសពីរ ។" "\n" r"+ បើ $m=e^{-1}$ សមីការមានឫសមួយ គឺ $x=e$ ។" "\n" r"+ បើ $m>e^{-1}$ សមីការគ្មានឫស ។" "\n" r"ដូចនេះ ករណីមានឫសពីរកើតឡើងតែ $0<m<e^{-1}$ ។",
       r"0<m<e^{-1}\Rightarrow 2", d=(1-ln(x))/x**2)
    f = exp(x)/x
    S = Q(f, "hand_equation_discussion", crit=[1], holes=[0], A=[("v", x), ("h", sp.Integer(0))])
    HR(S, r"តើសមីការ $e^{x}=mx$ មានឫសប៉ុន្មានតាមតម្លៃ $m$ ? ចូរឆ្លើយដោយសិក្សា $f(x)=\frac{e^{x}}{x}$ លើ $IR-\{0\}$ ។",
       r"$x=0$ មិនមែនជាឫសទេ ព្រោះ $e^{0}=1\neq 0$ ។ ដូច្នេះ សមីការសមមូល $f(x)=m$ ។" "\n" r"តាមរូបមន្តផលចែក $f'(x)=\frac{xe^{x}-e^{x}}{x^2}=\frac{(x-1)e^{x}}{x^2}$ ។ សញ្ញាដូច $x-1$ ។ ហើយ $f(1)=e$ ។" "\n" r"លីមីត ៖ $\lim_{x\to-\infty}f(x)=0$ , $\lim_{x\to 0^{-}}f(x)=-\infty$ , $\lim_{x\to 0^{+}}f(x)=+\infty$ , $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n" r"សន្និដ្ឋាន ៖" "\n" r"+ $m<0$ ៖ ឫសមួយ (អវិជ្ជមាន) ។" "\n" r"+ $0\le m<e$ ៖ គ្មានឫស ។" "\n" r"+ $m=e$ ៖ ឫសមួយ $x=1$ ។" "\n" r"+ $m>e$ ៖ ឫសពីរ វិជ្ជមានទាំងពីរ ។" "\n" r"ដូចនេះ តម្លៃកំណត់ព្រំដែនគឺ $m=0$ និង $m=e$ ។",
       r"m=e\Rightarrow x=1", d=(x-1)*exp(x)/x**2)
    f = x**2*exp(-x)
    S = Q(f, "hand_equation_discussion", crit=[0, 2], A=[("h", sp.Integer(0))], xint=[sp.Integer(0)])
    HR(S, r"អនុគមន៍ $f(x)=x^2e^{-x}$ ។ សង់តារាងអថេរភាព ហើយកំណត់តម្លៃ $k>0$ ដែលសមីការ $x^2=ke^{x}$ មានឫសបីផ្សេងគ្នា ។",
       r"ផលគុណ ៖ $f'(x)=2xe^{-x}-x^2e^{-x}=x(2-x)e^{-x}$ ។ ឫស $x=0$ និង $x=2$ ។ $f(0)=0$ និង $f(2)=4e^{-2}$ ។" "\n" r"$\lim_{x\to-\infty}f(x)=+\infty$ និង $\lim_{x\to+\infty}f(x)=0$ ។" "\n«T»\n" r"សមីការ $x^2=ke^{x}$ សមមូល $f(x)=k$ ។ សាខា $(-\infty;0)$ ផ្ដល់ឫសមួយចំពោះគ្រប់ $k>0$ ។ សាខា $(0;2)$ និង $(2;+\infty)$ ផ្ដល់ឫសមួយក្នុងសាខានីមួយៗ លុះត្រាតែ $0<k<4e^{-2}$ ។" "\n" r"ដូចនេះ សមីការមានឫសបីលុះត្រាតែ $\boxed{0<k<4e^{-2}}$ ។",
       r"0<k<4e^{-2}", d=x*(2-x)*exp(-x))
    # symmetry
    f = x**4 - 2*x**2
    S = Q(f, "hand_symmetry", crit=[-1, 0, 1], xint=[-sp.sqrt(2), sp.Integer(0), sp.sqrt(2)])
    HR(S, r"បង្ហាញថា $f(x)=x^4-2x^2$ ជាអនុគមន៍គូ ។ សិក្សា $f$ លើ $[0;+\infty)$ រួចទាញលទ្ធផលលើ $IR$ ទាំងមូល ព្រមទាំងសង់ក្រាប ។",
       r"$f(-x)=(-x)^4-2(-x)^2=f(x)$ ដូច្នេះ $f$ គូ ហើយក្រាបឆ្លុះធៀបនឹង $y'oy$ ។" "\n" r"លើ $[0;+\infty)$ ៖ $f'(x)=4x^3-4x=4x(x-1)(x+1)$ ។ កត្តា $4x(x+1)\ge 0$ ដូច្នេះសញ្ញាដូច $x-1$ ។ $f$ ចុះលើ $[0;1]$ និងកើនលើ $[1;+\infty)$ ជាមួយ $f(1)=-1$ ។" "\n" r"តាមភាពឆ្លុះ $f$ កើនលើ $[-1;0]$ និងចុះលើ $(-\infty;-1]$ ។ តារាងពេញគឺ ៖" "\n«T»\n" r"$f(x)=0$ សមមូល $x^2(x^2-2)=0$ គឺ $x=0$ ឬ $x=\pm\sqrt{2}$ ។" "\n" r"ដូចនេះ អប្បបរមា $-1$ ត្រង់ $x=\pm 1$ និងអតិបរមា $0$ ត្រង់ $x=0$ ។",
       r"f_{\min}=-1", d=4*x*(x-1)*(x+1), chk=[C("(-x)**4-2*(-x)**2-(x**4-2*x**2)", 0, "even")])
    f = x/(x**2 + 1)
    S = Q(f, "hand_symmetry", crit=[-1, 1], A=[("h", sp.Integer(0))], xint=[sp.Integer(0)], tan=0)
    HR(S, r"អនុគមន៍ $f(x)=\frac{x}{x^2+1}$ មានភាពសេស ។ ចូរបញ្ជាក់ រួចរកបរមា អាស៊ីមតូត បន្ទាត់ប៉ះត្រង់ $O$ ហើយសង់ក្រាប ។",
       r"$f(-x)=\frac{-x}{x^2+1}=-f(x)$ គ្រប់ $x\in IR$ ។ ដូច្នេះ $O$ ជាផ្ចិតឆ្លុះ ។" "\n" r"$f'(x)=\frac{(x^2+1)-2x^2}{(x^2+1)^2}=\frac{(1-x)(1+x)}{(x^2+1)^2}$ ។" "\n" r"$f(1)=\frac{1}{2}$ និង $f(-1)=-\frac{1}{2}$ ។ ដឺក្រេភាគបែងធំជាងភាគយក ដូច្នេះ $\lim_{x\to\pm\infty}f(x)=0$ ហើយ $y=0$ ជាអាស៊ីមតូតដេក ។" "\n«T»\n" r"$f'(0)=1$ ដូច្នេះបន្ទាត់ប៉ះត្រង់ $O$ គឺ $y=x$ ។" "\n" r"ដូចនេះ អតិបរមា $\frac{1}{2}$ អប្បបរមា $-\frac{1}{2}$ ។",
       r"f_{\max}=\frac{1}{2};\ f_{\min}=-\frac{1}{2}", d=(1-x)*(1+x)/(x**2+1)**2, chk=[C("subs(diff(x/(x**2+1),x),x,0)", 1, "slope")])
    f = (x**2 - 4*x + 5)/(x - 2)
    S = Q(f, "hand_symmetry", crit=[1, 3], holes=[2], A=[("v", x-2), ("o", x-2)])
    HR(S, r"តាងប្ដូរអថេរ $X=x-2$ , $Y=y$ សម្រាប់ខ្សែកោង $(C):y=\frac{x^2-4x+5}{x-2}$ ។ បង្ហាញថាសមីការថ្មីជាអនុគមន៍សេស ។ ទាញរកផ្ចិតឆ្លុះនៃ $(C)$ រួចសង់តារាងអថេរភាព ។",
       r"ដោយ $x^2-4x+5=(x-2)^2+1$ គេបាន $y=x-2+\frac{1}{x-2}$ ។ ក្នុងអថេរថ្មី $Y=X+\frac{1}{X}$ ។" "\n" r"អនុគមន៍ $X\mapsto X+\frac{1}{X}$ សេស ដូច្នេះក្រាបឆ្លុះធៀបនឹងគល់ថ្មី $X=0,\ Y=0$ ដែលត្រូវនឹង $I(2;0)$ ។ ដូចនេះ $I(2;0)$ ជាផ្ចិតឆ្លុះ ។" "\n" r"ដេរីវេ ៖ $y'=1-\frac{1}{(x-2)^2}=\frac{(x-1)(x-3)}{(x-2)^2}$ ។ $f(1)=-2$ , $f(3)=2$ ។ អាស៊ីមតូតឈរ $x=2$ និងអាស៊ីមតូតទ្រេត $y=x-2$ ។" "\n«T»\n" r"ដូចនេះ អតិបរមា $-2$ ត្រង់ $x=1$ និងអប្បបរមា $2$ ត្រង់ $x=3$ ។",
       r"I(2;0)", d=(x-1)*(x-3)/(x-2)**2, chk=[C("subs((x**2-4*x+5)/(x-2),x,4-x)+(x**2-4*x+5)/(x-2)", 0, "centre")])
    f = exp(x)/(exp(x) + 1)
    S = Q(f, "hand_symmetry", A=[("h", sp.Integer(0)), ("h", sp.Integer(1))])
    HR(S, r"បង្ហាញថា $f(x)+f(-x)=1$ ចំពោះ $f(x)=\frac{e^{x}}{e^{x}+1}$ ។ តើលទ្ធផលនេះមានន័យអ្វីលើក្រាប ? បន្តសិក្សាអថេរភាពនៃ $f$ ។",
       r"គុណភាគយកនិងភាគបែងនៃ $f(-x)=\frac{e^{-x}}{e^{-x}+1}$ នឹង $e^{x}$ គេបាន $f(-x)=\frac{1}{1+e^{x}}$ ។ បូកជាមួយ $f(x)$ គេបាន $\frac{e^{x}+1}{e^{x}+1}=1$ ។" "\n" r"ទម្រង់ $f(2a-x)+f(x)=2b$ ជាមួយ $a=0$ និង $b=\frac{1}{2}$ បង្ហាញថា $I\left(0;\frac{1}{2}\right)$ ជាផ្ចិតឆ្លុះ ។" "\n" r"$f'(x)=\frac{e^{x}(e^{x}+1)-e^{x}e^{x}}{(e^{x}+1)^2}=\frac{e^{x}}{(e^{x}+1)^2}>0$ ដូច្នេះ $f$ កើនលើ $IR$ ។" "\n" r"$\lim_{x\to-\infty}f(x)=0$ ហើយ $f(x)=\frac{1}{1+e^{-x}}$ ផ្ដល់ $\lim_{x\to+\infty}f(x)=1$ ។" "\n«T»\n" r"ដូចនេះ ក្រាបមានអាស៊ីមតូតដេកពីរ $y=0$ និង $y=1$ ហើយនៅចន្លោះបន្ទាត់ទាំងពីរ ។",
       r"I(0;\frac{1}{2})", d=exp(x)/(exp(x)+1)**2, chk=[C("exp(x)/(exp(x)+1)+exp(-x)/(exp(-x)+1)", 1, "symmetry")])
    f = ln((x + 1)/(x - 1))
    S = Q(f, "hand_symmetry", gap=(sp.Integer(-1), sp.Integer(1)), A=[("v", x+1), ("v", x-1), ("h", sp.Integer(0))])
    HR(S, r"រកដែនកំណត់នៃ $f(x)=\ln\frac{x+1}{x-1}$ ។ បង្ហាញថា $f$ សេស និងចុះលើចន្លោះនីមួយៗនៃដែនកំណត់ ។ សង់តារាងអថេរភាព ។",
       r"ត្រូវការ $\frac{x+1}{x-1}>0$ ។ តាមសញ្ញាផលចែក គឺ $x<-1$ ឬ $x>1$ ។ ដូច្នេះ $D=(-\infty;-1)\cup(1;+\infty)$ ដែលឆ្លុះធៀបនឹង $0$ ។" "\n" r"ចំពោះ $x\in D$ ៖ $f(-x)=\ln\frac{-x+1}{-x-1}=\ln\frac{x-1}{x+1}=-f(x)$ ដូច្នេះ $f$ សេស ។" "\n" r"លើ $D$ គេអាចសរសេរ $f'(x)=\frac{u'}{u}$ ជាមួយ $u=\frac{x+1}{x-1}$ , $u'=\frac{-2}{(x-1)^2}$ ។ គេបាន $f'(x)=\frac{-2}{(x-1)(x+1)}<0$ ព្រោះ $(x-1)(x+1)>0$ លើ $D$ ។" "\n" r"លីមីត ៖ $u\to 1$ ត្រង់ $\pm\infty$ នោះ $f\to 0$ ។ $u\to 0^{+}$ ពេល $x\to(-1)^{-}$ នោះ $f\to-\infty$ ។ $u\to+\infty$ ពេល $x\to 1^{+}$ នោះ $f\to+\infty$ ។" "\n«T»\n" r"ដូចនេះ អាស៊ីមតូតគឺ $x=-1$ , $x=1$ និង $y=0$ ។",
       r"D=(-\infty;-1)\cup(1;+\infty)", d=-2/((x-1)*(x+1)))
    # two stage
    f = x - 1 - ln(x)/x
    S = Q(f, "hand_two_stage_study", crit=[1], lo=sp.Integer(0), A=[("v", x), ("o", x-1)], xint=[sp.Integer(1)])
    HR(S, r"ក. គេឱ្យ $g(x)=x^2-1+\ln x$ លើ $(0;+\infty)$ ។ សិក្សាអថេរភាពនៃ $g$ គណនា $g(1)$ ហើយទាញសញ្ញានៃ $g(x)$ ។" "\n" r"ខ. គេឱ្យ $f(x)=x-1-\frac{\ln x}{x}$ ។ បង្ហាញថា $f'(x)=\frac{g(x)}{x^2}$ ។ សង់តារាងអថេរភាព និងបញ្ជាក់អាស៊ីមតូត ។",
       r"ក. $g'(x)=2x+\frac{1}{x}>0$ លើ $(0;+\infty)$ ដូច្នេះ $g$ កើន ។ ដោយ $g(1)=0$ គេបាន $g(x)<0$ លើ $(0;1)$ និង $g(x)>0$ លើ $(1;+\infty)$ ។" "\n\n" r"ខ. $\left(\frac{\ln x}{x}\right)'=\frac{1-\ln x}{x^2}$ ដូច្នេះ $f'(x)=1-\frac{1-\ln x}{x^2}=\frac{x^2-1+\ln x}{x^2}=\frac{g(x)}{x^2}$ ។" "\n" r"$f'$ មានសញ្ញាដូច $g$ ហើយ $f(1)=0$ ។ $\lim_{x\to 0^{+}}f(x)=+\infty$ ព្រោះ $-\frac{\ln x}{x}\to+\infty$ ។ $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n" r"ដោយ $\lim_{x\to+\infty}[f(x)-(x-1)]=\lim_{x\to+\infty}\left(-\frac{\ln x}{x}\right)=0$ បន្ទាត់ $y=x-1$ ជាអាស៊ីមតូតទ្រេត ហើយ $x=0$ ជាអាស៊ីមតូតឈរ ។" "\n" r"ដូចនេះ អប្បបរមានៃ $f$ គឺ $0$ ត្រង់ $x=1$ ។",
       r"f_{\min}=0", d=(x**2-1+ln(x))/x**2, chk=[C("subs(x**2-1+log(x),x,1)", 0, "g(1)"), C("limit(-log(x)/x,x,oo)", 0, "oblique")])
    f = x**2/2 - x*ln(x)
    S = Q(f, "hand_two_stage_study", crit=[1], lo=sp.Integer(0))
    HR(S, r"១. បង្ហាញថា $x-1-\ln x\ge 0$ គ្រប់ $x>0$ ។" "\n" r"២. សិក្សាអនុគមន៍ $f(x)=\frac{x^2}{2}-x\ln x$ លើ $(0;+\infty)$ ។ ត្រង់ $x=1$ តើមានអ្វីកើតឡើង ?",
       r"១. យក $h(x)=x-1-\ln x$ ។ $h'(x)=\frac{x-1}{x}$ នាំឱ្យ $h$ មានអប្បបរមា $h(1)=0$ ។ ដូច្នេះ $h(x)\ge 0$ ។" "\n\n" r"២. $f'(x)=x-(\ln x+1)=x-1-\ln x=h(x)\ge 0$ ។ ដូច្នេះ $f$ កើនលើ $(0;+\infty)$ ។ ត្រង់ $x=1$ ដេរីវេស្មើសូន្យ តែមិនប្ដូរសញ្ញាទេ ដូច្នេះមិនមែនជាបរមា ។ តម្លៃគឺ $f(1)=\frac{1}{2}$ ។" "\n" r"លីមីត ៖ $\lim_{x\to 0^{+}}x\ln x=0$ ផ្ដល់ $\lim_{x\to 0^{+}}f(x)=0$ ។ សរសេរ $f(x)=x^2\left(\frac{1}{2}-\frac{\ln x}{x}\right)$ ផ្ដល់ $\lim_{x\to+\infty}f(x)=+\infty$ ។" "\n«T»\n" r"ដូចនេះ ក្រាបមានបន្ទាត់ប៉ះដេកត្រង់ $\left(1;\frac{1}{2}\right)$ តែ $f$ គ្មានបរមាទេ ។",
       r"f(1)=\frac{1}{2}", d=x-1-ln(x))
    # contexts
    f = x + 2 + 16/x
    S = Q(f, "hand_context", crit=[4], lo=sp.Integer(0), A=[("v", x), ("o", x+2)])
    HR(S, r"ថ្លៃដើមមធ្យមនៃការផលិតទំនិញ $x$ ឯកតា ($x>0$) ត្រូវបានយកគំរូដោយ $f(x)=x+2+\frac{16}{x}$ ។ រកចំនួន $x$ ដែលធ្វើឱ្យថ្លៃដើមមធ្យមតូចបំផុត ដោយសិក្សាអនុគមន៍ $f$ ពេញលេញ ។",
       r"ដែនកំណត់ក្នុងបញ្ហានេះគឺ $(0;+\infty)$ ។ ដេរីវេ $f'(x)=1-\frac{16}{x^2}=\frac{(x-4)(x+4)}{x^2}$ ។ លើដែននេះ សញ្ញាដូច $x-4$ ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=+\infty$ និង $\lim_{x\to+\infty}f(x)=+\infty$ ។ បន្ទាត់ $x=0$ និង $y=x+2$ ជាអាស៊ីមតូត ។" "\n" r"គណនា $f(4)=4+2+4=10$ ។" "\n«T»\n" r"ដូចនេះ ថ្លៃដើមមធ្យមតូចបំផុតស្មើ $10$ នៅពេលផលិត $x=4$ ឯកតា ។",
       r"x=4;\ f_{\min}=10", d=(x-4)*(x+4)/x**2)
    f = 5*x*exp(-x/2)
    S = Q(f, "hand_context", crit=[2], lo=sp.Integer(0), A=[("h", sp.Integer(0))])
    HR(S, r"កំហាប់ថ្នាំក្នុងឈាមក្រោយរយៈពេល $x$ ម៉ោង ($x>0$) កំណត់ដោយ $f(x)=5xe^{-\frac{x}{2}}$ ។ នៅពេលណាកំហាប់ខ្ពស់បំផុត ? តើកំហាប់ខិតជិតតម្លៃអ្វីនៅពេល $x$ ធំខ្លាំង ?",
       r"យើងគណនា $f'(x)=5e^{-\frac{x}{2}}-\frac{5x}{2}e^{-\frac{x}{2}}=\frac{5}{2}(2-x)e^{-\frac{x}{2}}$ ដោយរូបមន្តផលគុណ ។" "\n" r"កត្តា $\frac{5}{2}e^{-\frac{x}{2}}$ វិជ្ជមាន ដូច្នេះ $f'$ មានសញ្ញាដូច $2-x$ ។ កំហាប់កើនរហូតដល់ $x=2$ រួចចុះវិញ ។" "\n" r"$f(2)=10e^{-1}$ ។ ពេល $x\to 0^{+}$ កំហាប់ខិតជិត $0$ ។ ដោយ $\lim_{x\to+\infty}xe^{-\frac{x}{2}}=0$ បន្ទាត់ $y=0$ ជាអាស៊ីមតូតដេក ។" "\n«T»\n" r"ដូចនេះ កំហាប់ខ្ពស់បំផុត $10e^{-1}$ ក្រោយ $2$ ម៉ោង ហើយខិតជិត $0$ នៅពេលក្រោយមក ។",
       r"x=2;\ 10e^{-1}", d=R(5, 2)*(2-x)*exp(-x/2))
    f = 20 + 60*exp(-x/2)
    S = Q(f, "hand_context", lo=sp.Integer(0), A=[("h", sp.Integer(20))])
    HR(S, r"សីតុណ្ហភាពទឹកក្ដៅក្នុងពែងក្រោយ $x$ នាទី ($x>0$) គឺ $f(x)=20+60e^{-\frac{x}{2}}$ ។ បង្ហាញថាទឹកត្រជាក់ចុះជានិច្ច ហើយរកសីតុណ្ហភាពដែលទឹកខិតជិត ។ រកពេលដែល $f(x)=50$ ។",
       r"$f'(x)=60\cdot\left(-\frac{1}{2}\right)e^{-\frac{x}{2}}=-30e^{-\frac{x}{2}}<0$ ដូច្នេះ $f$ ចុះជានិច្ច ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=80$ និង $\lim_{x\to+\infty}f(x)=20$ ។ បន្ទាត់ $y=20$ ជាអាស៊ីមតូតដេក ។" "\n«T»\n" r"សមីការ $f(x)=50$ សមមូល $e^{-\frac{x}{2}}=\frac{1}{2}$ ឬ $-\frac{x}{2}=-\ln 2$ ។ ដូចនេះ $x=2\ln 2$ នាទី ហើយទឹកខិតជិត $20$ ដឺក្រេ ។",
       r"x=2\ln 2", d=-30*exp(-x/2), chk=[C("subs(20+60*exp(-x/2),x,2*log(2))", 50, "time")])
    f = 100/(1 + 9*exp(-x))
    S = Q(f, "hand_context", lo=sp.Integer(0), A=[("h", sp.Integer(100))])
    HR(S, r"ចំនួនអ្នកដឹងព័ត៌មានមួយ (គិតជាភាគរយ) ក្រោយ $x$ ថ្ងៃ ($x>0$) គឺ $f(x)=\frac{100}{1+9e^{-x}}$ ។ សិក្សាអថេរភាព ហើយរកថ្ងៃដែលកំណើនលឿនបំផុត ពោលគឺចំណុចរបត់នៃខ្សែកោង ។",
       r"ដោយ $\left(\frac{1}{v}\right)'=-\frac{v'}{v^2}$ គេបាន $f'(x)=\frac{900e^{-x}}{(1+9e^{-x})^2}>0$ ដូច្នេះ $f$ កើន ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=10$ ហើយ $\lim_{x\to+\infty}f(x)=100$ ។" "\n«T»\n" r"តាង $t=9e^{-x}$ ។ គេបាន $f'=\frac{100t}{(1+t)^2}$ ហើយ $t'=-t$ ។ ដូច្នេះ $f''=\frac{100t(t-1)}{(1+t)^3}$ ។ $f''=0$ សមមូល $t=1$ ឬ $x=2\ln 3$ ។ ត្រង់នោះ $f=50$ ។" "\n" r"ដូចនេះ ចំណុចរបត់គឺ $(2\ln 3;50)$ និងកំណើនលឿនបំផុតនៅពេល $x=2\ln 3$ ។",
       r"(2\ln 3;50)", d=900*exp(-x)/(1+9*exp(-x))**2, chk=[C("subs(diff(100/(1+9*exp(-x)),x,2),x,2*log(3))", 0, "inflection"), C("subs(100/(1+9*exp(-x)),x,2*log(3))", 50, "value")])
    f = sp.expand(x**2*(x - 4)*x)
    S = Q(f, "hand_stationary_point", crit=[0, 3], xint=[sp.Integer(0), sp.Integer(4)])
    HR(S, r"ពិនិត្យអនុគមន៍ $f(x)=x^4-4x^3$ ។ សិស្សម្នាក់និយាយថា ដោយ $f'(0)=0$ នោះ $f$ មានបរមាត្រង់ $x=0$ ។ តើត្រឹមត្រូវឬទេ ? ចូរសិក្សាអនុគមន៍ ហើយពន្យល់ ។",
       r"$f'(x)=4x^3-12x^2=4x^2(x-3)$ ។ ដោយ $4x^2\ge 0$ សញ្ញានៃ $f'(x)$ អាស្រ័យលើ $x-3$ ។" "\n" r"ដូច្នេះ $f'(x)<0$ ទាំងនៅខាងឆ្វេង និងខាងស្ដាំ $x=0$ ។ ដេរីវេស្មើសូន្យត្រង់ $0$ ប៉ុន្តែមិនប្ដូរសញ្ញាទេ ។" "\n" r"$f(0)=0$ , $f(3)=-27$ ។ លីមីតត្រង់ $\pm\infty$ ស្មើ $+\infty$ ។" "\n«T»\n" r"ដូចនេះ ពាក្យសិស្សនោះមិនត្រឹមត្រូវ ៖ $f$ មិនមានបរមាត្រង់ $x=0$ ទេ ។ បរមាតែមួយគត់គឺអប្បបរមា $-27$ ត្រង់ $x=3$ ។ ក្រាបកាត់ $x'ox$ ត្រង់ $(0;0)$ និង $(4;0)$ ។",
       r"f_{\min}=-27", d=4*x**2*(x-3))
    f = (1 + ln(x))/x
    S = Q(f, "hand_second_derivative", crit=[1], lo=sp.Integer(0), A=[("v", x), ("h", sp.Integer(0))], xint=[exp(-1)])
    HR(S, r"លើ $(0;+\infty)$ គេឱ្យ $f(x)=\frac{1+\ln x}{x}$ ។ គណនា $f'(x)$ និង $f''(x)$ ។ រកអតិបរមា និងចំណុចរបត់នៃក្រាប ។",
       r"តាមរូបមន្តផលចែក $f'(x)=\frac{\frac{1}{x}\cdot x-(1+\ln x)}{x^2}=-\frac{\ln x}{x^2}$ ។ វាវិជ្ជមានលើ $(0;1)$ និងអវិជ្ជមានលើ $(1;+\infty)$ ។" "\n" r"ធ្វើដេរីវេម្ដងទៀត $f''(x)=-\frac{\frac{1}{x}\cdot x^2-2x\ln x}{x^4}=\frac{2\ln x-1}{x^3}$ ។ $f''(x)=0$ សមមូល $x=\sqrt{e}$ ហើយប្ដូរសញ្ញាត្រង់នោះ ។" "\n" r"$\lim_{x\to 0^{+}}f(x)=-\infty$ , $\lim_{x\to+\infty}f(x)=0$ ។" "\n«T»\n" r"$f(\sqrt{e})=\frac{3}{2\sqrt{e}}$ ។ ដូចនេះ អតិបរមា $f(1)=1$ និងចំណុចរបត់ $\left(\sqrt{e};\frac{3}{2\sqrt{e}}\right)$ ។",
       r"f_{\max}=1", d=-ln(x)/x**2, chk=[C("subs(diff((1+log(x))/x,x,2),x,sqrt(E))", 0, "inflection"), C("subs((1+log(x))/x,x,sqrt(E))", R(3, 2)/sp.sqrt(EE), "y")])
    f = sp.expand((x - 1)**2*(x + 2))
    return HROWS, HPLOTS

def main():
    rows = []; plots = {}; seen = set(); fails = {}
    for fam, target in FAMS:
        target = max(7, int(target * 0.84))
        got = 0; tries = 0
        while got < target and tries < target * 40:
            tries += 1
            try:
                S = fam()
                if S is None or S.key is None: continue
                k = (S.fam, S.key)
                if k in seen: continue
                build(S)
                seen.add(k)
                row = compose(S)
            except (AssertionError, KeyError, TypeError, ZeroDivisionError, ValueError, AttributeError, IndexError, OverflowError) as e:
                fails[fam.__name__ + ":" + type(e).__name__ + ":" + str(e)[:70]] = fails.get(fam.__name__ + ":" + type(e).__name__ + ":" + str(e)[:70], 0) + 1
                continue
            rows.append(row); plots[row["id"]] = S.plot; got += 1
        print(fam.__name__, got, "tries", tries)
    for k, v in sorted(fails.items(), key=lambda t: -t[1])[:25]:
        print("FAIL", v, k)
    hr, hp = hand_rows()
    print("hand rows", len(hr))
    rows += hr; plots.update(hp)
    write(rows, plots)

def write(rows, plots):
    import glob
    for g in glob.glob(os.path.join(ROOT, "diagrams", "function_study-*.png")):
        os.remove(g)
    bysub = {}
    for r in rows:
        bysub.setdefault(r["subtopic"], []).append(r)
    chosen = []
    i = 0
    while len(chosen) < 285 and any(bysub.values()):
        for k in list(bysub):
            if bysub[k] and len(chosen) < 285:
                chosen.append(bysub[k].pop(rng.randrange(len(bysub[k]))))
    for r in chosen:
        if r["id"] not in plots: continue
        kw = plots[r["id"]]
        try:
            rel = plot_png(r["id"], **kw)
        except Exception as e:
            print("plot fail", r["id"], e); continue
        for d in r["diagrams"]:
            if d["type"] == "graph":
                d["image"] = rel
    write_jsonl(rows, "function_study.jsonl")

if __name__ == "__main__":
    main()
