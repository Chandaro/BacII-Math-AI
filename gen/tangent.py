"""Generator for topic `tangent`: tangent/normal lines, slope conditions, outside points,
geometric meaning of the derivative. Writes out/tangent.jsonl. All numbers come from SymPy."""
import random, sys, os, hashlib, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from common import make_row as _make_row
from variation_hand import tidy_row, fnpow, boxed
def make_row(*a, **k):
    return tidy_row(_make_row(*a, **k), local=True)
R = sp.Rational
rng = random.Random(20261105)
ch = rng.choice
GEN = "tangent"
rows, seen = [], set()
png_left = [170]  # 124 PNGs from the first run are still in diagrams/, so the total stays under 300
NOPNG = bool(os.environ.get("NOPNG"))

# ---------- LaTeX helpers ----------
def L(e):
    t = fnpow(sp.latex(sp.sympify(e), ln_notation=True, order="lex"))
    t = re.sub(r"(^|[({=,])- ", r"\1-", t)
    t = re.sub(r"\\(sin|cos|tan|ln)\{\\left\(x \\right\)\}", r"\\\1 x", t)
    t = re.sub(r"\\(sin|cos|tan|ln)\{\\left\(([^()]*?) \\right\)\}", r"\\\1(\2)", t)
    t = re.sub(r"\\ln\((\d+)\)", r"\\ln \1", t)
    t = re.sub(r"(\d) (x|e|\\sin|\\cos|\\ln|\\sqrt|\\pi|\\left)", r"\1\2", t)
    t = re.sub(r"\} (x|e\^|\\sin|\\cos|\\ln)", r"}\1", t)
    return t
def Lq(e):
    """value in parentheses when negative, for substitution"""
    t = L(e)
    return f"({t})" if t.startswith("-") else t
def lin(mm, c):
    mm, c = sp.sympify(mm), sp.sympify(c)
    if mm == 0:
        return f"y={L(c)}"
    if mm == 1: t = "x"
    elif mm == -1: t = "-x"
    elif isinstance(mm, sp.Add): t = f"({L(mm)})x"
    else: t = L(mm) + "x" if not L(mm).endswith("}") or True else ""
    if c != 0:
        ct = L(c)
        t += ct if ct.startswith("-") else "+" + ct
    return "y=" + t
def xm(v):
    v = sp.sympify(v)
    if v == 0: return "x"
    t = L(sp.expand(-v))
    return "x" + (("+" + t) if not t.startswith("-") else t)
def ym(v):
    return xm(v).replace("x", "y", 1)
def mul(mm, a):
    mm = sp.sympify(mm)
    inner = xm(a)
    if mm == 1: return inner if sp.sympify(a) == 0 else inner
    if mm == -1: return f"-({inner})" if sp.sympify(a) != 0 else "-x"
    co = f"({L(mm)})" if isinstance(mm, sp.Add) else L(mm)
    if sp.sympify(a) == 0: return co + "x"
    return f"{co}({inner})"
def P(nm, a, b):
    return f"{nm}({L(a)};{L(b)})"
def tval(e, a):
    return sp.sympify(e).subs(x, a)
def gen_eq(u, v, w):
    """u x + v y + w = 0"""
    def term(c, s, first):
        if c == 0: return ""
        sg = "-" if c < 0 else ("" if first else "+")
        return sg + ("" if abs(c) == 1 and s else str(abs(c))) + s
    t = term(u, "x", True); t += term(v, "y", not t); t += term(w, "", not t)
    return t + "=0"

# ---------- phrase pools ----------
RPOLY = ["តាមរូបមន្ត $(x^n)'=nx^{n-1}$ យើងបាន", "ដោយប្រើរូបមន្តដេរីវេនៃពហុធា យើងបាន", "ធ្វើដេរីវេតួនីមួយៗ តាមរូបមន្ត $(x^n)'=nx^{n-1}$ គេបាន", "ដេរីវេនៃអនុគមន៍នេះគឺ"]
RQUOT = ["តាមរូបមន្តដេរីវេនៃផលចែក $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ យើងបាន", "ប្រើរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ គេបាន", "អនុគមន៍នេះជាផលចែក ដូច្នេះតាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ យើងបាន"]
RPROD = ["តាមរូបមន្តដេរីវេនៃផលគុណ $(uv)'=u'v+uv'$ យើងបាន", "អនុគមន៍នេះជាផលគុណ ដូច្នេះប្រើរូបមន្ត $(uv)'=u'v+uv'$ គេបាន"]
RTOOK = ["ជំនួសតម្លៃទាំងនេះ គេបាន", "ជំនួសចូល យើងបាន", "ដាក់តម្លៃទាំងនេះចូលក្នុងរូបមន្ត យើងបាន", "ពេលជំនួសតម្លៃ គេបាន"]
FORM = ["តាមរូបមន្ត សមីការបន្ទាត់ប៉ះត្រង់ចំណុចអាប់ស៊ីស $x_0$ គឺ", "សមីការបន្ទាត់ប៉ះនៃខ្សែកោងត្រង់ចំណុច $(x_0;y_0)$ កំណត់ដោយ ៖", "រូបមន្តសមីការបន្ទាត់ប៉ះ ៖", "គេដឹងថាបន្ទាត់ប៉ះត្រង់ $x_0$ មានសមីការ"]
END = ["ដូចនេះ", "ដូចនេះ", "ដូចនេះ", "សរុបមក", "ជាលទ្ធផល"]
def dom_R(): return ch(["អនុគមន៍ $@n$ កំណត់ចំពោះគ្រប់ $x\\in IR$ ។", "ដែនកំណត់ $D=IR$ ។", "អនុគមន៍នេះជាពហុធា ដូច្នេះ $D=IR$ ។", "យើងមាន $D=IR$ ។"])
def dom_ex(den, v):
    return ch([f"អនុគមន៍ $@n$ កំណត់លុះត្រាតែ ${den}\\neq 0$ ឬ $x\\neq {L(v)}$ ។ ដូចនេះ $D=IR-\\{{{L(v)}\\}}$ ។",
               f"ដែនកំណត់ ៖ ${den}\\neq 0$ នាំឱ្យ $x\\neq {L(v)}$ ដូច្នេះ $D=IR-\\{{{L(v)}\\}}$ ។",
               f"ភាគបែងត្រូវខុសពីសូន្យ គឺ ${den}\\neq 0$ ។ គេបាន $D=IR-\\{{{L(v)}\\}}$ ។"])

class Fn:
    def __init__(s, e, tex, dom, ds, d, xs, kind, lo=None, vas=(), dtex=None):
        s.e, s.tex, s.dom, s.ds, s.d, s.xs, s.kind, s.lo, s.vas = e, tex, dom, ds, d, list(xs), kind, lo, tuple(vas)
        s.dtex = dtex or L(d)

def poly_fn(e, xs=None, kind="poly"):
    d = sp.diff(e, x)
    return Fn(e, L(e), dom_R(), ch(RPOLY) + f" $$@D={L(d)}$$", d, xs or range(-3, 4), kind)
def fam_p2():
    a = ch([1, -1, 2, -2, 3, -3, R(1, 2), -R(1, 2), 4]); b = rng.randint(-6, 6); c = rng.randint(-7, 7)
    return poly_fn(a * x**2 + b * x + c)
def fam_p3():
    a = ch([1, -1, 2, -2, R(1, 3), -R(1, 3)]); b = rng.randint(-4, 4); c = rng.randint(-6, 6); d = rng.randint(-5, 5)
    return poly_fn(a * x**3 + b * x**2 + c * x + d, range(-2, 3))
def fam_p4():
    a = ch([1, -1, R(1, 2), R(1, 4), 2]); b = rng.randint(-4, 4); c = rng.randint(-3, 3); d = rng.randint(-4, 4)
    return poly_fn(a * x**4 + b * x**2 + c * x + d, range(-2, 3))
def fam_hom():
    while True:
        a, b, d = rng.randint(-4, 4), rng.randint(-6, 6), rng.randint(-4, 4); c = ch([1, 1, 1, 2, -1])
        if a * d - b * c != 0 and a != 0 and d != 0: break
    den = c * x + d; num = a * x + b; e = num / den; dt = a * d - b * c
    pole = R(-d, c); dd = sp.Integer(dt) / den**2
    ds = (f"តាង $u={L(num)}$ និង $v={L(den)}$ នោះ $u'={a}$ និង $v'={c}$ ។ " + ch(RQUOT) +
          f" $$@D=\\frac{{{Lq(a)}({L(den)})-{Lq(c)}({L(num)})}}{{({L(den)})^2}}=\\frac{{{dt}}}{{({L(den)})^2}}$$")
    xs = [pole + k for k in (-3, -2, -1, 1, 2, 3)]
    return Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), pole), ds, dd, xs, "hom", vas=[pole], dtex=f"\\frac{{{dt}}}{{({L(den)})^2}}")
def fam_q21():
    while True:
        p, q, c = rng.randint(-5, 5), rng.randint(-6, 6), rng.randint(-4, 4)
        if c != 0 and c * c - p * c + q != 0: break
    num = x**2 + p * x + q; den = x + c; e = num / den
    d = sp.cancel(sp.diff(e, x)); dn = sp.expand((2 * x + p) * den - num)
    r = c * c - p * c + q  # remainder
    if rng.random() < .6:
        ds = ch(RQUOT) + f" $$@D=\\frac{{({L(2*x+p)})({L(den)})-({L(num)})}}{{({L(den)})^2}}=\\frac{{{L(dn)}}}{{({L(den)})^2}}$$"
    else:
        ds = (f"ចែកភាគយកនឹងភាគបែង គេអាចសរសេរ @F ជារាង $@F={L(x+p-c)}{'+' if r>0 else '-'}\\frac{{{abs(r)}}}{{{L(den)}}}$ ។ យើងបាន "
              f"$$@D=1{'-' if r>0 else '+'}\\frac{{{abs(r)}}}{{({L(den)})^2}}=\\frac{{{L(dn)}}}{{({L(den)})^2}}$$")
        ds = ds.replace("សរសេរ @F ជារាង", "សរសេរ $@F$ ជារាង")
    return Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), -c), ds, dn / den**2, [-c + k for k in (-2, -1, 1, 2, 3)], "q21", vas=[-c], dtex=f"\\frac{{{L(dn)}}}{{({L(den)})^2}}")
def fam_rec():
    a = ch([1, -1, 2, 3, R(1, 2)]); b = rng.randint(-4, 4); c = ch([1, 2, 3, 4, 6, -1, -2, -4]); h = ch([0, 0, 1, -1, 2])
    u = x - h; e = a * x + b + c / u; d = a - c / u**2
    dom = dom_ex(L(u), h)
    ds = (ch(["តាមរូបមន្ត $\\left(\\frac{1}{u}\\right)'=-\\frac{u'}{u^2}$ យើងបាន", "ដោយ $\\left(\\frac{1}{u}\\right)'=-\\frac{u'}{u^2}$ គេបាន"]) +
          f" $$@D={L(a)}{'-' if c>0 else '+'}\\frac{{{abs(c)}}}{{{'x^2' if h==0 else '('+L(u)+')^2'}}}$$")
    ct = f"\\frac{{{abs(c)}}}{{{L(u)}}}"
    pre = L(a * x + b)
    return Fn(e, pre + ("+" if c > 0 else "-") + ct, dom, ds, d, [h + k for k in (-2, -1, 1, 2)], "rec", vas=[h],
              dtex=f"{L(a)}{'-' if c>0 else '+'}\\frac{{{abs(c)}}}{{{'x^2' if h==0 else '('+L(u)+')^2'}}}")
def fam_sqrt():
    t = rng.random()
    if t < .55:
        a = ch([1, 2, 3, 4, 5, -1, -2]); b = rng.randint(1, 9) if a > 0 else rng.randint(4, 12)
        u = a * x + b; e = sp.sqrt(u); d = sp.Integer(a) / (2 * sp.sqrt(u))
        xs = [R(k * k - b, a) for k in range(1, 6)]
        ds = (ch(["តាមរូបមន្ត $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ យើងបាន", "ដេរីវេនៃឫសការេ $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ ផ្ដល់ឱ្យ"]) +
              f" $$@D=\\frac{{({L(u)})'}}{{2\\sqrt{{{L(u)}}}}}={L(d)}$$")
        v = R(-b, a); dom = (f"អនុគមន៍កំណត់លុះត្រាតែ ${L(u)}\\geq 0$ ។ ដូចនេះ $D=" + (f"[{L(v)};+\\infty)$ ។" if a > 0 else f"(-\\infty;{L(v)}]$ ។"))
        return Fn(e, L(e), dom, ds, d, xs, "sqrt", lo=(float(v) if a > 0 else None))
    a = ch([1, 2, -1, R(1, 2), 3]); k = ch([2, 4, 6, -2, 1, 3]); b = rng.randint(-3, 3)
    e = a * x + k * sp.sqrt(x) + b; d = a + sp.Integer(k) / (2 * sp.sqrt(x))
    dom = "អនុគមន៍កំណត់លុះត្រាតែ $x\\geq 0$ ។ ដូចនេះ $D=[0;+\\infty)$ ។"
    ds = f"ដោយ $(\\sqrt{{x}})'=\\frac{{1}}{{2\\sqrt{{x}}}}$ ចំពោះ $x>0$ យើងបាន $$@D={L(d)}$$"
    return Fn(e, L(e), dom, ds, d, [1, 4, 9, 16], "sqrt", lo=0.0)
def fam_exp():
    t = rng.randint(0, 4)
    dom = ch(["អនុគមន៍កំណត់ចំពោះគ្រប់ $x\\in IR$ ។", "ដែនកំណត់ $D=IR$ ។"])
    if t == 0:
        a, b = ch([1, 2, -1, 3, -2]), rng.randint(-4, 4); u = a * x + b; e = u * sp.exp(x); d = sp.factor((u + a)) * sp.exp(x)
        ds = ch(RPROD) + f" $$@D={a}\\cdot e^{{x}}+({L(u)})e^{{x}}=({L(u+a)})e^{{x}}$$".replace("1\\cdot e", "e")
        return Fn(e, f"({L(u)})e^{{x}}", dom, ds, sp.expand(u + a) * sp.exp(x), [0, 1, -1, 0, 2], "exp", dtex=f"({L(u+a)})e^{{x}}")
    if t == 1:
        a, b, c = ch([1, 2, -1, -2, 3]), rng.randint(-3, 3), rng.randint(-3, 3); k = ch([1, 2, -2, 3])
        e = k * sp.exp(a * x) + b * x + c; d = sp.diff(e, x)
        ds = f"តាមរូបមន្ត $(e^{{u}})'=u'e^{{u}}$ យើងបាន $$@D={L(d)}$$"
        return Fn(e, L(e), dom, ds, d, [0, 0, 1, -1, sp.log(2)/a if abs(a)<3 else 0], "exp")
    if t == 2:
        a, b = ch([1, 2, -1, 3, -3, R(1, 2)]), rng.randint(-4, 4); k = ch([1, 2, -1, 3])
        e = k * sp.exp(a * x + b); d = sp.diff(e, x)
        ds = f"អនុគមន៍នេះជាអនុគមន៍បណ្ដាក់ ។ តាមរូបមន្ត $(e^{{u}})'=u'e^{{u}}$ គេបាន $$@D={L(d)}$$"
        return Fn(e, L(e), dom, ds, d, [R(-b) / a], "exp")
    if t == 3:
        a = ch([1, 2, -1, 3]); b = rng.randint(-3, 3); c = rng.randint(1, 4)
        u = x**2 + b * x + c; e = u * sp.exp(a * x); du = 2 * x + b; dd = sp.expand(du + a * u)
        ds = ch(RPROD) + f" $$@D=({L(du)})e^{{{L(a*x)}}}+({L(u)})\\cdot {L(sp.diff(sp.exp(a*x),x))}=({L(dd)})e^{{{L(a*x)}}}$$"
        return Fn(e, f"({L(u)})e^{{{L(a*x)}}}", dom, ds, dd * sp.exp(a * x), [0, 0, 1], "exp", dtex=f"({L(dd)})e^{{{L(a*x)}}}")
    a, c = ch([1, 2, 3, -1, -2]), rng.randint(-3, 4); u = x + c * 0 + a * 0 ; k = ch([1, 2, 3, 4])
    b = ch([1, 2, 3]); e = (k * x + a) * sp.exp(-b * x); dd = sp.expand(k - b * (k * x + a))
    ds = ch(RPROD) + f" $$@D={k}e^{{{L(-b*x)}}}+({L(k*x+a)})({L(-b)})e^{{{L(-b*x)}}}=({L(dd)})e^{{{L(-b*x)}}}$$".replace("$@D=1e", "$@D=e")
    return Fn(e, f"({L(k*x+a)})e^{{{L(-b*x)}}}", dom, ds, dd * sp.exp(-b * x), [0, 0, 1], "exp", dtex=f"({L(dd)})e^{{{L(-b*x)}}}")
def fam_ln():
    t = rng.randint(0, 4)
    dom = ch(["អនុគមន៍កំណត់លុះត្រាតែ $x>0$ ។ ដូចនេះ $D=(0;+\\infty)$ ។", "ដែនកំណត់ ៖ $x>0$ ឬ $D=(0;+\\infty)$ ។"])
    if t == 0:
        a, b, c = ch([1, 2, -1, 3, R(1, 2), -2]), rng.randint(-4, 4), ch([1, 2, -1, -2, 3, 4, -3])
        e = a * x + b + c * sp.log(x); d = a + sp.Integer(c) / x
        ds = f"ដោយ $(\\ln x)'=\\frac{{1}}{{x}}$ យើងបាន $$@D={L(d)}$$"
        return Fn(e, L(e), dom, ds, d, [1, 1, 2, sp.E, 3], "ln", lo=0.02)
    if t == 1:
        a, b = ch([1, 2, 3, -1, -2]), rng.randint(-3, 3); e = (a * x + b) * sp.log(x); u = a * x + b
        d = a * sp.log(x) + u / x
        ds = ch(RPROD) + f" $$@D={Lq(a)}\\ln x+({L(u)})\\cdot\\frac{{1}}{{x}}={L(a)}\\ln x+{L(a)}{'+' if b>=0 else '-'}\\frac{{{abs(b)}}}{{x}}$$".replace("1\\ln","\\ln")
        return Fn(e, f"({L(u)})\\ln x", dom, ds, d, [1, 1, sp.E, sp.E**2], "ln", lo=0.02, dtex=L(d))
    if t == 2:
        k = ch([1, 2, 3, -1, 4]); c = rng.randint(-3, 3); e = k * sp.log(x) / x + c
        d = k * (1 - sp.log(x)) / x**2
        ds = ch(RQUOT) + f" $$@D={Lq(k)}\\cdot\\frac{{\\frac{{1}}{{x}}\\cdot x-\\ln x}}{{x^2}}=\\frac{{{L(k*(1-sp.log(x)))}}}{{x^2}}$$".replace("1\\cdot\\frac","\\frac")
        return Fn(e, (f"\\frac{{{L(k*sp.log(x))}}}{{x}}" + (f"{c:+d}" if c else "")), dom, ds, d, [1, 1, sp.E, sp.E**2], "ln", lo=0.1)
    if t == 3:
        a = ch([1, 2, 3, 4, 5]); b = rng.randint(-3, 4); k = ch([1, 2, -1, 3]); u = a * x + b; e = k * sp.log(u); d = k * a / u
        v = R(-b, a)
        dm = f"អនុគមន៍កំណត់លុះត្រាតែ ${L(u)}>0$ ឬ $x>{L(v)}$ ។ ដូចនេះ $D=({L(v)};+\\infty)$ ។"
        ds = f"តាមរូបមន្ត $(\\ln u)'=\\frac{{u'}}{{u}}$ យើងបាន $$@D={L(d)}$$"
        return Fn(e, L(e), dm, ds, d, [R(1 - b, a), R(2 - b, a), R(3 - b, a)], "ln", lo=float(v) + .02)
    a = ch([1, 2, -1]); c = rng.randint(-3, 3); b = ch([1, 2, 3, -1])
    e = a * x**2 + b * sp.log(x) + c; d = 2 * a * x + sp.Integer(b) / x
    ds = f"ដោយ $(x^2)'=2x$ និង $(\\ln x)'=\\frac{{1}}{{x}}$ យើងបាន $$@D={L(d)}$$"
    return Fn(e, L(e), dom, ds, d, [1, 1, 2, sp.E], "ln", lo=0.02)
def fam_trig():
    t = rng.randint(0, 4); pi = sp.pi
    dom = "អនុគមន៍កំណត់ចំពោះគ្រប់ $x\\in IR$ ។"
    nice = [0, pi / 6, pi / 4, pi / 3, pi / 2, 2 * pi / 3, pi]
    if t == 0:
        a, b = ch([1, 2, 3, -1, -2, 4]), ch([1, 2, -1, 3, 0, 0]); c = rng.randint(-3, 3)
        e = a * sp.sin(x) + b * sp.cos(x) + c
    elif t == 1:
        a, b = ch([1, 2, -1, 3]), ch([1, 2, 3, 4, -2, R(1, 2)]); e = b * x + a * sp.sin(x)
    elif t == 2:
        a, c = ch([1, 2, -1, 3, R(1, 2)]), rng.randint(-2, 3); k = ch([2, 3]); e = a * ch([sp.sin, sp.cos])(k * x) + c
        nice = [0, pi / 6, pi / 4, pi / 3, pi / 2] if k == 2 else [0, pi / 6, pi / 3, pi / 2, pi / 9 * 0 + pi / 12]
    elif t == 3:
        a, c = ch([1, 2, -1, 3]), rng.randint(-3, 3); b = ch([0, 1, -1, 2]); e = a * sp.tan(x) + b * x + c
        nice = [0, pi / 6, pi / 4, pi / 3, -pi / 4]
        d = sp.diff(e, x); d = b + a * (1 + sp.tan(x)**2)
        ds = f"ដោយ $(\\tan x)'=1+\\tan^2x=\\frac{{1}}{{\\cos^2x}}$ យើងបាន $$@D={L(b)}{'+' if a>0 else '-'}\\frac{{{abs(a)}}}{{\\cos^2x}}$$".replace("$@D=0+","$@D=").replace("$@D=0-","$@D=-")
        dm = "អនុគមន៍កំណត់លុះត្រាតែ $\\cos x\\neq 0$ ឬ $x\\neq\\frac{\\pi}{2}+k\\pi$ ។"
        return Fn(e, L(e).replace("\\tan x", "\\tan x"), dm, ds, b + a / sp.cos(x)**2, nice, "trig", dtex=(f"{L(b)}{'+' if a>0 else '-'}\\frac{{{abs(a)}}}{{\\cos^2x}}").lstrip("0").lstrip("+"), lo=-1.5)
    else:
        a, k = ch([1, 2, 3, -1]), ch([1, 2]); c = rng.randint(-2, 2); e = a * sp.sin(x)**2 + c if k == 1 else a * sp.cos(x)**2 + c
    d = sp.diff(e, x)
    ds = ch(["ដោយ $(\\sin u)'=u'\\cos u$ និង $(\\cos u)'=-u'\\sin u$ យើងបាន", "តាមរូបមន្តដេរីវេនៃអនុគមន៍ត្រីកោណមាត្រ គេបាន"]) + f" $$@D={L(d)}$$"
    return Fn(e, L(e).replace("\\sin^{2}{\\left(x \\right)}", "\\sin^2x").replace("\\cos^{2}{\\left(x \\right)}", "\\cos^2x"), dom, ds, d, nice, "trig")
FAMS = [fam_p2, fam_p3, fam_p3, fam_p4, fam_hom, fam_hom, fam_q21, fam_rec, fam_sqrt, fam_exp, fam_exp, fam_ln, fam_ln, fam_trig]

# ---------- row assembly ----------
def rid(prob): return f"tangent-{hashlib.sha1(prob.encode()).hexdigest()[:10]}"
def names():
    n = ch(["f", "f", "f", "g", "h", "y", "y"])
    F = "y" if n == "y" else f"{n}(x)"
    D = "y'" if n == "y" else f"{n}'(x)"
    C = ch(["(C)", "(C)", "(C)", "(\\Gamma)"] + ([] if n == "y" else [f"(C_{n})"]))
    return n, F, D, C
def tok(t, nm):
    n, F, D, C = nm
    if n == "y": t = t.replace("អនុគមន៍ $@n$ កំណត់ដោយ", "អនុគមន៍កំណត់ដោយ").replace("អនុគមន៍ $@n$ កំណត់លុះត្រាតែ", "អនុគមន៍កំណត់លុះត្រាតែ").replace("អនុគមន៍ $@n$ កំណត់ចំពោះ", "អនុគមន៍កំណត់ចំពោះ")
    t = t.replace("@F", F).replace("@D", D).replace("@n", n).replace("@C", C)
    t = t.replace("-1(", "-(").replace("{1(", "{(").replace("=1(", "=(")
    t = re.sub(r"(\$\$(?:\(T\):)?)y[^$=]*=0(?:\(x[^)]*\)|x)\\iff ", r"\1", t)
    t = re.sub(r"\\frac\{([^{}]*)\}\{1\}", r"\1", t)
    t = t.replace("(x)(", "x(").replace("(0-t)", "(-t)")
    t = t.replace("+-", "-").replace("+\\frac{0}{x}", "").replace("-\\frac{0}{x}", "")
    t = re.sub(r"(^|[^\d.}])1x\^2", r"\1x^2", t)
    t = re.sub(r"\+\((-[^()+\-]*)\)", r"\1", t)
    t = t.replace("0+0a+b", "b").replace("+0a", "").replace("{0a+b}", "{b}").replace("\\\\ 0+a=", "\\\\ a=")
    t = re.sub(r"(^|[^\d.}])1a(?![a-z])", r"\1a", t)
    return t
def add(sub, diff, prob, sol, ans, chk, key, nm=None, diagrams=None):
    """key must be unused; caller checks fresh() first."""
    nm = nm or names()
    prob, sol, ans = tok(prob, nm), tok(sol, nm), tok(ans, nm)
    bx = boxed(sol)
    if bx: ans = ",\\ ".join(bx)
    i = rid(prob)
    ds = []
    for d in diagrams or []:
        d = dict(d)
        if callable(d.get("image")):
            d["image"] = d["image"](i)
        d["alt_km"] = tok(d.get("alt_km", ""), nm); d["latex"] = tok(d["latex"], nm)
        ds.append(d)
    rows.append(make_row("tangent", sub, diff, prob, sol, ans, chk, GEN, diagrams=ds, row_id=i))
    return True
def fresh(*k):
    key = tuple(str(sp.sympify(v)) for v in k)
    if key in seen: return False
    seen.add(key); return True
def intro(t):
    return ch([f"គេឱ្យអនុគមន៍ $@F={t}$ មានខ្សែកោងតាងដោយ $@C$ ។", f"គេមានអនុគមន៍ $@F={t}$ ដែលមានក្រាប $@C$ ។",
               f"ឱ្យខ្សែកោង $@C$ នៃអនុគមន៍ $@F={t}$ ។", f"អនុគមន៍ $@n$ កំណត់ដោយ $@F={t}$ ហើយ $@C$ ជាខ្សែកោងតំណាង ។",
               f"ក្នុងតម្រុយអរតូណរម៉ាល់ $(O,\\vec{{i}},\\vec{{j}})$ គេឱ្យខ្សែកោង $@C$ នៃអនុគមន៍ $@F={t}$ ។",
               f"គេឱ្យ $@C$ ជាក្រាបនៃអនុគមន៍ $@F={t}$ ។"])
def ck_d(F): return check(f"diff({s(F.e)},x)", s(F.d), "derivative")
def ck_y(F, a, v): return check(f"subs({s(F.e)},x,{s(a)})", s(v), "value at point")
def ck_m(F, a, v): return check(f"subs(diff({s(F.e)},x),x,{s(a)})", s(v), "slope")
def ck_T(F, a, T): return check(f"subs({s(F.e)},x,{s(a)})+subs(diff({s(F.e)},x),x,{s(a)})*(x-({s(a)}))", s(T), "tangent line")
def yv(F, a): return sp.nsimplify(F.e.subs(x, a)) if F.kind == "x" else sp.simplify(F.e.subs(x, a))
def mv(F, a): return sp.simplify(F.d.subs(x, a))
def tan_lines(mm, a, b):
    """write-up of the line through (a;b) with slope mm; returns text, T, tex"""
    c = sp.expand(b - mm * a); T = mm * x + c; tex = lin(mm, c); v = rng.randint(0, 3)
    if mm == 0:
        return f"ដោយមេគុណប្រាប់ទិសស្មើសូន្យ បន្ទាត់ប៉ះស្របនឹងអ័ក្ស $x'ox$ ហើយមានសមីការ $${tex}$$", T, tex
    if v == 0:
        t = f"{ch(RTOOK)} $${ym(b)}={mul(mm,a)}$$ $${tex}$$"
    elif v == 1:
        t = f"យើងបាន $$y={mul(mm,a)}{'' if b==0 else ('+'+L(b) if not L(b).startswith('-') else L(b))}$$ ពន្លាតរួចសម្រួល គេបាន $${tex}$$"
    elif v == 2:
        cm = {1: "", -1: "-"}.get(mm, L(mm)); pm = {1: "", -1: "-"}.get(mm, L(mm) + "\\cdot ")
        sub_ = "p" if sp.sympify(a) == 0 else f"{pm}{Lq(a)}+p"
        t = f"តាងបន្ទាត់ប៉ះដោយ $y={cm}x+p$ ។ ដោយវាកាត់តាមចំណុច $({L(a)};{L(b)})$ គេបាន ${L(b)}={sub_}$ នាំឱ្យ $p={L(c)}$ ។ ដូច្នេះ $${tex}$$"
    else:
        t = f"{ch(RTOOK)} $${ym(b)}={mul(mm,a)}\\iff {tex}$$"
    return t, T, tex
def form(): return ch(FORM) + " $$y-y_0=@n'(x_0)(x-x_0)$$"

def pgf(e):
    Dg = sp.Function("deg")
    e = e.replace(sp.sin, lambda a: sp.sin(Dg(a))).replace(sp.cos, lambda a: sp.cos(Dg(a))).replace(sp.tan, lambda a: sp.tan(Dg(a)))
    return str(e).replace("**", "^").replace("log(", "ln(").replace("E", "exp(1)")
def window(F, pts):
    xs_ = [float(p[0]) for p in pts] or [0.0]
    x0, x1 = min(xs_ + [0]) - 2, max(xs_ + [0]) + 2
    if F.lo is not None: x0 = min(x0, -1) if F.lo <= 0 else -1; x0 = max(x0, -1) if F.lo >= -.01 else x0
    fn = sp.lambdify(x, F.e, "numpy")
    with np.errstate(all="ignore"):
        g = np.linspace(x0, x1, 200); ys = np.broadcast_to(np.asarray(fn(g), dtype=float), g.shape)
    ys = ys[np.isfinite(ys)]; ys = ys[np.abs(ys) < 30] if len(ys) else ys
    vals = [float(p[1]) for p in pts] + [0.0] + ([float(np.percentile(ys, 8)), float(np.percentile(ys, 92))] if len(ys) else [])
    return math.floor(x0), math.ceil(x1), math.floor(min(vals)) - 1, math.ceil(max(vals)) + 1
LINE_COL = ["#c0392b", "#1e8449", "#b9770e"]
def plot_tangents(row_id, f, xmin, xmax, ymin, ymax, lines_, points, vas):
    """Like common.plot_png, but every line in lines_ is drawn solid as a tangent or normal;
    only true vertical asymptotes are grey and dashed. Labels are math only."""
    fn = sp.lambdify(x, f, "numpy")
    xs = np.linspace(xmin, xmax, 1500)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(np.asarray(fn(xs), dtype=float), xs.shape).copy()
    ys[np.abs(ys) > 10 * max(abs(ymin), abs(ymax))] = np.nan
    ys[1:][np.abs(np.diff(ys)) > (ymax - ymin)] = np.nan
    fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=110)
    ax.plot(xs, ys, lw=1.8, color="#1f4e9c")
    for i, T in enumerate(lines_):
        tn = sp.lambdify(x, T, "numpy")
        with np.errstate(all="ignore"):
            ty_ = np.broadcast_to(np.asarray(tn(xs), dtype=float), xs.shape)
        ax.plot(xs, ty_, lw=1.1, color=LINE_COL[i % 3])
    for v in vas:
        ax.axvline(float(v), ls="--", lw=0.9, color="gray")
    for px, py in points:
        ax.plot([float(px)], [float(py)], "o", ms=4, color="#c0392b")
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    for sd in ("top", "right"):
        ax.spines[sd].set_visible(False)
    for sd in ("left", "bottom"):
        ax.spines[sd].set_position("zero")
    ax.grid(alpha=0.2)
    rel = f"diagrams/{row_id}.png"
    fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight")
    plt.close(fig)
    return rel
def split_poles(tz, vas):
    """Draw the curve branch by branch, so that no segment joins across a pole."""
    def rep(mo):
        a, b, body = float(mo[1]), float(mo[2]), mo[3]
        cuts = sorted(float(v) for v in vas if a < float(v) < b); out = ""
        for u, w in zip([a] + [c + .02 for c in cuts], [c - .02 for c in cuts] + [b]):
            out += f"\\addplot[thick,domain={u:.3f}:{w:.3f}] {{{body}}};\n"
        return out
    return re.sub(r"\\addplot\[thick,domain=([-\d.]+):([-\d.]+)\] \{(.*)\};\n", rep, tz, count=1)
def gdiag(F, tans, pts, alt, png_p=.3, ty="graph"):
    x0, x1, y0, y1 = window(F, pts)
    ex = ""
    for T in tans:
        ex += f"\\addplot[red,domain={x0}:{x1}] {{{pgf(sp.sympify(T))}}};\n"
    if pts:
        ex += "\\addplot[only marks,mark=*] coordinates {" + " ".join(f"({float(a):.3f},{float(b):.3f})" for a, b in pts) + "};\n"
    for v in F.vas:
        ex += f"\\draw[dashed] (axis cs:{float(v):.3f},{y0}) -- (axis cs:{float(v):.3f},{y1});\n"
    tz = tikz_graph(pgf(F.e), x0, x1, y0, y1, ex)
    if F.kind in ("sqrt", "ln") or F.lo is not None:
        fn = sp.lambdify(x, F.e, "numpy")
        with np.errstate(all="ignore"):
            g = np.linspace(x0, x1, 2000); ok = np.isfinite(np.broadcast_to(np.asarray(fn(g), dtype=float), g.shape))
        d0, d1 = (float(g[ok][0]), float(g[ok][-1])) if F.kind != "trig" else (-1.5, 1.5)
        tz = tz.replace(f"thick,domain={x0}:{x1}", f"thick,domain={d0:.3f}:{d1:.3f}")
    if F.vas:
        tz = split_poles(tz, F.vas)
        tz = tz.replace("samples=200]", f"samples=200,restrict y to domain={y0-8}:{y1+8},unbounded coords=jump]", 1)
    d = {"type": ty, "latex": tz, "alt_km": alt, "image": None}
    if rng.random() < png_p and png_left[0] > 0:
        png_left[0] -= 1
        if NOPNG: return d
        tl = [sp.sympify(T) for T in tans]
        d["image"] = lambda i, F=F, tl=tl, pts=pts, w=(x0, x1, y0, y1): plot_tangents(i, F.e, w[0], w[1], w[2], w[3], tl, pts, F.vas)
    return d
ALT = ["ខ្សែកោង និងបន្ទាត់ប៉ះត្រង់ចំណុចដែលបានរក ។", "ក្រាបនៃអនុគមន៍ជាមួយបន្ទាត់ប៉ះ ។", "រូបបង្ហាញខ្សែកោង $@C$ និងបន្ទាត់ប៉ះ ។"]
def rand_fn(fams=None):
    return ch(fams or FAMS)()
def good(v):
    return v.is_finite and v.is_real and not v.has(sp.zoo, sp.nan)

# ---------- S1, S2: tangent at an abscissa / at a point ----------
Q_AB = ["រកសមីការបន្ទាត់ប៉ះនៃខ្សែកោង $@C$ ត្រង់ចំណុចដែលមានអាប់ស៊ីស $x_0={a}$ ។", "ចូរសរសេរសមីការបន្ទាត់ប៉ះនឹង $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${a}$ ។",
        "គណនា $@n'({a})$ រួចទាញរកសមីការបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ $x={a}$ ។", "កំណត់សមីការបន្ទាត់ប៉ះ $(T)$ នៃខ្សែកោងត្រង់ចំណុចដែលមានអាប់ស៊ីសស្មើនឹង ${a}$ ។",
        "បន្ទាត់ $(T)$ ប៉ះខ្សែកោង $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${a}$ ។ រកសមីការរបស់ $(T)$ ។"]
Q_PT = ["ផ្ទៀងផ្ទាត់ថាចំណុច ${p}$ នៅលើខ្សែកោង $@C$ រួចរកសមីការបន្ទាត់ប៉ះត្រង់ចំណុចនោះ ។", "រកសមីការបន្ទាត់ប៉ះនៃខ្សែកោងត្រង់ចំណុច ${p}$ ។",
        "បង្ហាញថា ${p}$ ជាចំណុចនៃ $@C$ ។ រួចសរសេរសមីការបន្ទាត់ប៉ះ $@C$ ត្រង់ចំណុចនេះ ។", "រកមេគុណប្រាប់ទិស និងសមីការបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ ${p}$ ។"]
def s_abscissa():
    F = rand_fn(); a = ch(F.xs); b, mm = yv(F, a), mv(F, a)
    if not (good(b) and good(mm)) or F.e.subs(x, a).has(sp.zoo) or not fresh(F.e): return False
    if F.lo is not None and float(a) <= F.lo and F.kind != "sqrt": return False
    tx, T, tex = tan_lines(mm, a, b)
    big = F.kind in ("poly",) and rng.random() < .4
    lines = [] if big else [F.dom]
    p1 = ch([f"ដេរីវេ ៖ {F.ds}", F.ds, f"ជាដំបូងគណនាដេរីវេ ។ {F.ds}"])
    p2 = f"ត្រង់ $x_0={L(a)}$ យើងបាន $@n({L(a)})={L(b)}$ និង $@n'({L(a)})={L(mm)}$ ។"
    p3 = ch([f"តម្លៃ ៖ $y_0=@n({L(a)})={L(b)}$ ហើយមេគុណប្រាប់ទិសគឺ $@n'({L(a)})={L(mm)}$ ។", p2])
    order = ch([0, 1, 1])
    if order == 0: lines += [form(), p1, p3, tx]
    else: lines += [p1, p3, form(), tx]
    q = ch(Q_AB)
    pre = f"$\\boxed{{@n'({L(a)})={L(mm)}}}$ ហើយ" if "គណនា $@n'" in q else ""
    lines.append(f"{ch(END)} {pre} សមីការបន្ទាត់ប៉ះគឺ $\\boxed{{{tex}}}$ ។".replace("  ", " "))
    diff = "easy" if F.kind == "poly" else "medium"
    dg = [gdiag(F, [T], [(a, b)], ch(ALT), .12)] if rng.random() < .35 else []
    prob = intro(F.tex) + " " + q.replace("{a}", L(a))
    return add("tangent_at_abscissa", diff, prob, "\n".join(lines), tex, [ck_d(F), ck_y(F, a, b), ck_m(F, a, mm), ck_T(F, a, T)], F.e, diagrams=dg)
def s_point():
    F = rand_fn(); a = ch(F.xs); b, mm = yv(F, a), mv(F, a)
    if not (good(b) and good(mm)) or not fresh(F.e): return False
    if F.lo is not None and float(a) <= F.lo and F.kind != "sqrt": return False
    nm_ = ch(["A", "M", "B", "M_0", "P"]); p = P(nm_, a, b)
    tx, T, tex = tan_lines(mm, a, b)
    v = ch([f"យើងមាន $@n({L(a)})={L(b)}$ ដូច្នេះចំណុច ${p}$ នៅលើ $@C$ ។", f"ជំនួស $x={L(a)}$ ក្នុង $@F$ គេបាន $y={L(b)}$ នោះបញ្ជាក់ថា ${p}\\in @C$ ។"])
    q = ch(Q_PT)
    pre = f"មេគុណប្រាប់ទិសគឺ $\\boxed{{m={L(mm)}}}$ ហើយ" if "រកមេគុណប្រាប់ទិស" in q else ""
    lines = [F.dom, v, F.ds, f"មេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះត្រង់ ${nm_}$ គឺ $@n'({L(a)})={L(mm)}$ ។", form(), tx,
             f"{ch(END)} {pre} បន្ទាត់ប៉ះត្រង់ ${nm_}$ មានសមីការ $\\boxed{{{tex}}}$ ។".replace("  ", " ")]
    dg = [gdiag(F, [T], [(a, b)], ch(ALT), .1)] if rng.random() < .25 else []
    prob = intro(F.tex) + " " + q.replace("{p}", p)
    return add("tangent_at_point", "easy" if F.kind == "poly" else "medium", prob, "\n".join(lines), tex, [ck_d(F), ck_y(F, a, b), ck_m(F, a, mm), ck_T(F, a, T)], F.e, diagrams=dg)

# ---------- S3: normal ----------
Q_N = ["រកសមីការបន្ទាត់ $(N)$ ដែលកែងនឹងបន្ទាត់ប៉ះនៃខ្សែកោង $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${a}$ ហើយកាត់តាមចំណុចប៉ះនោះ ។",
       "រកសមីការបន្ទាត់ប៉ះ $(T)$ និងបន្ទាត់ណរម៉ាល់ $(N)$ នៃ $@C$ ត្រង់ $x={a}$ ។ ($(N)$ ជាបន្ទាត់កែងនឹង $(T)$ ត្រង់ចំណុចប៉ះ)",
       "ត្រង់ចំណុចអាប់ស៊ីស ${a}$ នៃ $@C$ គេគូសបន្ទាត់ប៉ះ $(T)$ ហើយគូសបន្ទាត់ $(N)$ កែងនឹង $(T)$ ត្រង់ចំណុចប៉ះនោះ ។ រកសមីការ $(T)$ និង $(N)$ ។",
       "រកសមីការបន្ទាត់ណរម៉ាល់ $(N)$ នៃខ្សែកោងត្រង់ចំណុចអាប់ស៊ីស ${a}$ គឺបន្ទាត់ដែលកាត់តាមចំណុចប៉ះ ហើយកែងនឹងបន្ទាត់ប៉ះ ។"]
def s_normal():
    F = rand_fn(); a = ch(F.xs); b, mm = yv(F, a), mv(F, a)
    if not (good(b) and good(mm)) or mm == 0 or not fresh(F.e): return False
    if F.lo is not None and float(a) <= F.lo and F.kind != "sqrt": return False
    if isinstance(mm, sp.Add) or mm.has(sp.E): return False
    n = sp.simplify(-1 / mm); c = sp.expand(b - n * a); N = n * x + c; texn = lin(n, c)
    tx, T, tex = tan_lines(mm, a, b)
    q = ch(Q_N); both = "(T)" in q
    lines = [F.dom, F.ds, f"ត្រង់ $x_0={L(a)}$ គេបាន $y_0=@n({L(a)})={L(b)}$ និង $@n'({L(a)})={L(mm)}$ ។"]
    if both: lines += [form(), tx]
    lines += [ch(["បន្ទាត់ពីរកែងគ្នាលុះត្រាតែផលគុណមេគុណប្រាប់ទិសស្មើនឹង $-1$ ។", "ដោយ $(N)$ កែងនឹងបន្ទាត់ប៉ះ នោះផលគុណមេគុណប្រាប់ទិសរបស់វាស្មើនឹង $-1$ ។"]) +
              f" ដូច្នេះ $(N)$ មានមេគុណប្រាប់ទិស $$m_N=-\\frac{{1}}{{{L(mm)}}}={L(n)}$$",
              f"សមីការ $(N)$ ៖ $${ym(b)}={mul(n,a)}$$ $${texn}$$"]
    ans = (f"(T):{tex},\\ (N):{texn}" if both else f"(N):{texn}")
    lines.append(f"{ch(END)} " + (f"$\\boxed{{(T):{tex}}}$ និង $\\boxed{{(N):{texn}}}$ ។" if both else f"បន្ទាត់ដែលត្រូវរកមានសមីការ $\\boxed{{{texn}}}$ ។"))
    chk = [ck_d(F), ck_y(F, a, b), ck_m(F, a, mm), check(f"-1/subs(diff({s(F.e)},x),x,{s(a)})", s(n), "normal slope"),
           check(f"subs({s(F.e)},x,{s(a)})-(x-({s(a)}))/subs(diff({s(F.e)},x),x,{s(a)})", s(N), "normal line")]
    if both: chk.append(ck_T(F, a, T))
    dg = [gdiag(F, [T, N], [(a, b)], "ខ្សែកោង បន្ទាត់ប៉ះ និងបន្ទាត់កែងនឹងវាត្រង់ចំណុចប៉ះ ។", .12)] if rng.random() < .3 else []
    return add("normal_line", "medium", intro(F.tex) + " " + q.replace("{a}", L(a)), "\n".join(lines), ans, chk, F.e, diagrams=dg)

# ---------- slope cases ----------
def slope_case(k=None):
    """returns F, k, roots, text solving f'(x)=k. Curve is built from the chosen roots."""
    t = ch(["c3", "c3", "c3", "c2", "hom", "hom", "rec", "ln", "exp", "trig"])
    k = sp.Integer(ch([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 9])) if k is None else k
    if t == "c3":
        p, q = sorted(rng.sample(range(-4, 5), 2)); a = ch([1, -1, R(1, 3), -R(1, 3), 2])
        if (3 * a * (p + q)) % 2 != 0 and a in (1, -1): a = a * 2
        c = rng.randint(-5, 5)
        e = a * x**3 - R(3, 2) * a * (p + q) * x**2 + (3 * a * p * q + k) * x + c
        F = poly_fn(e, kind="c3")
        eq = sp.expand((F.d - k) / (3 * a))
        st = f"$$@D={L(k)}\\iff {L(F.d)}={L(k)}\\iff {L(eq)}=0$$ សមីការនេះបំបែកបាន $({xm(p)})({xm(q)})=0$ ឬ $\\Delta={L((p-q)**2)}$ ដូច្នេះវាមានឫសពីរ $x_1={L(p)}$ និង $x_2={L(q)}$ ។"
        return F, k, [p, q], st
    if t == "c2":
        a = ch([1, -1, 2, -2, 3, R(1, 2)]); p = rng.randint(-4, 4); c = rng.randint(-6, 6)
        e = a * x**2 + (k - 2 * a * p) * x + c; F = poly_fn(e)
        st = f"$$@D={L(k)}\\iff {L(F.d)}={L(k)}\\iff x={L(p)}$$"
        return F, k, [p], st
    if t == "hom":
        h = rng.randint(-3, 3); w = ch([1, 2, 3]); r = -k * w * w; b = rng.randint(-3, 3)
        if h == 0: h = 1
        num = sp.expand(b * (x - h) + r); e = num / (x - h); den = x - h
        dt = r * -1
        F = Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), h), ch(RQUOT) + f" $$@D=\\frac{{{Lq(b)}({L(den)})-({L(num)})}}{{({L(den)})^2}}=\\frac{{{L(dt)}}}{{({L(den)})^2}}$$",
               sp.Integer(dt) / den**2, [], "hom", vas=[h], dtex=f"\\frac{{{L(dt)}}}{{({L(den)})^2}}")
        if b == 0: F.ds = F.ds.replace(f"{Lq(b)}({L(den)})-", "-")
        st = f"$$@D={L(k)}\\iff \\frac{{{L(dt)}}}{{({L(den)})^2}}={L(k)}\\iff ({L(den)})^2={w*w}$$ នាំឱ្យ ${L(den)}={w}$ ឬ ${L(den)}=-{w}$ ។ ដូច្នេះ $x_1={L(h-w)}$ និង $x_2={L(h+w)}$ ។"
        return F, k, [h - w, h + w], st
    if t == "rec":
        w = ch([1, 2, 3]); a = k + ch([1, 2, 3, -1, -2]); c = (a - k) * w * w; b = rng.randint(-3, 3); h = ch([0, 0, 1, -1])
        if a == 0: return None
        den = x - h; e = a * x + b + c / den; d = a - c / den**2; dn = "x^2" if h == 0 else f"({L(den)})^2"
        F = Fn(e, L(a * x + b) + ("+" if c > 0 else "-") + f"\\frac{{{abs(c)}}}{{{L(den)}}}" if a * x + b != 0 else "", dom_ex(L(den), h), f"យើងបាន $$@D={L(a)}{'-' if c>0 else '+'}\\frac{{{abs(c)}}}{{{dn}}}$$", d, [], "rec", vas=[h])
        st = f"$$@D={L(k)}\\iff \\frac{{{abs(c)}}}{{{dn}}}={abs(a-k)}\\iff {dn}={w*w}$$ នាំឱ្យ $x_1={L(h-w)}$ និង $x_2={L(h+w)}$ ។"
        return F, k, [h - w, h + w], st
    if t == "ln":
        w = ch([1, 2, 3, 4, R(1, 2)]); a = k - ch([1, 2, 3, -1, -2]); bb = (k - a) * w; c = rng.randint(-3, 3)
        if bb == 0: return None
        e = a * x + bb * sp.log(x) + c; d = a + bb / x
        F = Fn(e, L(e), "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ ។ ដូចនេះ $D=(0;+\\infty)$ ។", f"ដោយ $(\\ln x)'=\\frac{{1}}{{x}}$ យើងបាន $$@D={L(d)}$$", d, [], "ln", lo=0.02)
        st = f"$$@D={L(k)}\\iff {L(d)}={L(k)}\\iff \\frac{{{L(bb)}}}{{x}}={L(k-a)}\\iff x={L(w)}$$ ដោយ ${L(w)}>0$ នោះតម្លៃនេះស្ថិតក្នុង $D$ ។"
        return F, k, [w], st
    if t == "exp":
        w = ch([1, 2, 3, 4]); a = k - w; c = rng.randint(-3, 3); e = sp.exp(x) + a * x + c; d = sp.exp(x) + a
        F = Fn(e, L(e), "ដែនកំណត់ $D=IR$ ។", f"ដោយ $(e^{{x}})'=e^{{x}}$ យើងបាន $$@D={L(d)}$$", d, [], "exp")
        r = sp.log(w)
        st = f"$$@D={L(k)}\\iff e^{{x}}+{Lq(a)}={L(k)}\\iff e^{{x}}={w}\\iff x={L(r)}$$"
        return F, k, [r], st
    a = ch([2, 4, -2, -4]); cc = ch([R(1, 2), -R(1, 2)]); bb = k - a * cc; e = bb * x + a * sp.sin(x); d = bb + a * sp.cos(x)
    F = Fn(e, L(e), "អនុគមន៍កំណត់ចំពោះគ្រប់ $x\\in IR$ ។ គេសិក្សាលើ $[0;2\\pi]$ ។", f"ដោយ $(\\sin x)'=\\cos x$ យើងបាន $$@D={L(d)}$$", d, [], "trig")
    r = [sp.pi / 3, 5 * sp.pi / 3] if cc > 0 else [2 * sp.pi / 3, 4 * sp.pi / 3]
    st = f"$$@D={L(k)}\\iff \\cos x={L(cc)}$$ លើ $[0;2\\pi]$ សមីការនេះមានឫស $x_1={L(r[0])}$ និង $x_2={L(r[1])}$ ។"
    F.iv = True
    return F, k, r, st
def block_tangents(F, k, rts):
    """Returns lines, list of T, list of tex, checks, pts"""
    lines, Ts, texs, chk, pts = [], [], [], [ck_d(F)], []
    for i, r in enumerate(rts):
        b = yv(F, r); pts.append((r, b))
        c = sp.expand(b - k * r); T = k * x + c; tex = lin(k, c)
        lab = f"ចំពោះ $x={L(r)}$ ៖ " if len(rts) > 1 else ""
        lines.append(lab + f"$y={L(b)}$ ដូច្នេះចំណុចប៉ះគឺ ${P('M_'+str(i+1) if len(rts)>1 else 'M', r, b)}$ ។ បន្ទាត់ប៉ះមានសមីការ $${ym(b)}={mul(k,r)}\\iff {tex}$$")
        Ts.append(T); texs.append(tex)
        chk += [ck_m(F, r, k), ck_y(F, r, b), ck_T(F, r, T)]
    return lines, Ts, texs, chk, pts
def concl(texs, pts=None):
    """pts: contact points as (x,y); boxed too when the question asks for them."""
    pre = ""
    if pts:
        lab = (lambda i: f"M_{i+1}") if len(pts) > 1 else (lambda i: "M")
        pre = "ចំណុចប៉ះគឺ " + " និង ".join(f"$\\boxed{{{P(lab(i), a, b)}}}$" for i, (a, b) in enumerate(pts)) + " ហើយ"
    if len(texs) == 1: return f"{ch(END)} {pre} បន្ទាត់ប៉ះដែលត្រូវរកគឺ $\\boxed{{{texs[0]}}}$ ។".replace("  ", " ")
    return f"{ch(END)} {pre} មានបន្ទាត់ប៉ះពីរគឺ $\\boxed{{{texs[0]}}}$ និង $\\boxed{{{texs[1]}}}$ ។".replace("  ", " ")
def asks_pts(q):
    return any(w in q for w in ("រកចំណុច", "ត្រង់ចំណុចណា", "កូអរដោនេចំណុចប៉ះ"))
def iv_note(F): return " (លើចន្លោះ $[0;2\\pi]$)" if getattr(F, "iv", False) else ""
Q_K = ["រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ដែលមានមេគុណប្រាប់ទិសស្មើនឹង ${k}$ ។", "រកចំណុចទាំងអស់នៃ $@C$ ដែលបន្ទាត់ប៉ះត្រង់ចំណុចនោះមានមេគុណប្រាប់ទិស ${k}$ រួចសរសេរសមីការបន្ទាត់ប៉ះទាំងនោះ ។",
       "កំណត់បន្ទាត់ប៉ះនៃខ្សែកោង $@C$ ដែលមានមេគុណប្រាប់ទិស $m={k}$ ។", "តើត្រង់ចំណុចណាខ្លះនៃ $@C$ ដែល $@n'(x)={k}$ ? រកសមីការបន្ទាត់ប៉ះត្រង់ចំណុចទាំងនោះ ។"]
def s_slope():
    r = slope_case()
    if not r: return False
    F, k, rts, st = r
    if not fresh(F.e): return False
    ls, Ts, texs, chk, pts = block_tangents(F, k, rts)
    op = ch([f"អាប់ស៊ីសនៃចំណុចប៉ះជាឫសនៃសមីការ $@n'(x)={L(k)}$ ។", f"បន្ទាត់ប៉ះត្រង់ $x_0$ មានមេគុណប្រាប់ទិស $@n'(x_0)$ ដូច្នេះយើងដោះស្រាយ $@n'(x)={L(k)}$ ។"])
    q = ch(Q_K)
    sol = "\n".join([F.dom, F.ds, op, st] + ls + [concl(texs, pts if asks_pts(q) else None)])
    dg = [gdiag(F, Ts, pts, "ខ្សែកោង និងបន្ទាត់ប៉ះដែលមានមេគុណប្រាប់ទិសដូចគ្នា ។", .12)] if rng.random() < .4 else []
    return add("tangent_given_slope", "medium", intro(F.tex) + " " + q.replace("{k}", L(k)) + iv_note(F), sol, ", ".join(texs), chk, F.e, diagrams=dg)
def line_given(l, avoid):
    """a line of slope l (Rational); returns tex, intercept"""
    for _ in range(50):
        w = rng.randint(-7, 7)
        if rng.random() < .5:
            p = w; tex = lin(l, p); expr = l * x + p
            kind = "ex"
        else:
            u, v = sp.Rational(l).p, sp.Rational(l).q
            tex = gen_eq(u, -v, w); expr = (u * x + w) / sp.Integer(v); kind = "gen"
        if all(sp.expand(expr - T) != 0 for T in avoid):
            return tex, expr, kind
    return None
Q_PAR = ["រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ដែលស្របនឹងបន្ទាត់ $(d):{l}$ ។", "ចូរសរសេរសមីការបន្ទាត់ប៉ះនឹងខ្សែកោង $@C$ ដែលស្របទៅនឹងបន្ទាត់ $(\\Delta):{l}$ ។",
         "តើ $@C$ មានបន្ទាត់ប៉ះស្របនឹង $(d):{l}$ ឬទេ ? បើមាន រកសមីការរបស់វា ។", "គេឱ្យបន្ទាត់ $(L):{l}$ ។ រកចំណុចនៃ $@C$ ដែលបន្ទាត់ប៉ះត្រង់ចំណុចនោះស្របនឹង $(L)$ ។ សរសេរសមីការបន្ទាត់ប៉ះនោះ ។"]
Q_PER = ["រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ដែលកែងនឹងបន្ទាត់ $(d):{l}$ ។", "ចូរសរសេរសមីការបន្ទាត់ប៉ះនឹង $@C$ ហើយកែងនឹងបន្ទាត់ $(\\Delta):{l}$ ។",
         "បន្ទាត់ $(T)$ ប៉ះខ្សែកោង $@C$ ហើយកែងនឹង $(d):{l}$ ។ រកសមីការ $(T)$ ។"]
def lab(q):
    m_ = re.search(r"\((d|L|\\Delta)\):", q); return f"({m_.group(1)})"
def s_parallel():
    r = slope_case()
    if not r: return False
    F, k, rts, st = r
    if not fresh(F.e): return False
    ls, Ts, texs, chk, pts = block_tangents(F, k, rts)
    g = line_given(k, Ts)
    if not g: return False
    ltex, lexp, kind = g; q = ch(Q_PAR); d = lab(q)
    pre = f"ពីសមីការ ${ltex}$ គេទាញបាន ${lin(k, sp.expand(lexp - k*x))}$ ។ " if kind == "gen" else ""
    op = pre + ch([f"បន្ទាត់ $@{d}$ មានមេគុណប្រាប់ទិស ${L(k)}$ ។ បន្ទាត់ស្របគ្នាមានមេគុណប្រាប់ទិសស្មើគ្នា ដូច្នេះបន្ទាត់ប៉ះមានមេគុណប្រាប់ទិស ${L(k)}$ ។",
                    f"ដោយបន្ទាត់ប៉ះស្របនឹង $@{d}$ នោះ $@n'(x_0)={L(k)}$ ដែល ${L(k)}$ ជាមេគុណប្រាប់ទិសនៃ $@{d}$ ។"]).replace("$@(", "$(")
    sol = "\n".join([F.dom, op, F.ds, st] + ls + [concl(texs, pts if asks_pts(q) else None)])
    chk.append(check(f"diff({s(lexp)},x)", s(k), "slope of the given line"))
    dg = [gdiag(F, Ts, pts, "ខ្សែកោង និងបន្ទាត់ប៉ះស្របនឹងបន្ទាត់ដែលឱ្យ ។", .12)] if rng.random() < .4 else []
    return add("tangent_parallel_line", "medium", intro(F.tex) + " " + q.replace("{l}", ltex) + iv_note(F), sol, ", ".join(texs), chk, F.e, diagrams=dg)
def s_perp():
    l = ch([R(1, 2), R(-1, 2), R(1, 3), R(-1, 3), 1, -1, 2, -2, 3, R(-1, 4), R(1, 5), R(-3, 2), R(2, 3), R(-1, 6)]); l = sp.Rational(l); k = -1 / l
    r = slope_case(k)
    if not r: return False
    F, k, rts, st = r
    if not fresh(F.e): return False
    if k.q != 1 and F.kind in ("hom", "rec", "exp", "trig", "ln") or (k.q != 1 and F.kind == "c3"): return False
    ls, Ts, texs, chk, pts = block_tangents(F, k, rts)
    g = line_given(l, [])
    ltex, lexp, kind = g; q = ch(Q_PER); d = lab(q)
    pre = f"ពីសមីការ ${ltex}$ គេទាញបាន ${lin(l, sp.expand(lexp - l*x))}$ ។ " if kind == "gen" else ""
    op = pre + f"បន្ទាត់ ${d}$ មានមេគុណប្រាប់ទិស $m_1={L(l)}$ ។ បន្ទាត់ប៉ះកែងនឹង ${d}$ លុះត្រាតែ $m\\cdot m_1=-1$ ឬ $m={L(k)}$ ។"
    sol = "\n".join([F.dom, op, F.ds, st] + ls + [concl(texs)])
    chk.append(check(f"-1/diff({s(lexp)},x)", s(k), "perpendicular slope"))
    dg = [gdiag(F, Ts, pts, "ខ្សែកោង និងបន្ទាត់ប៉ះកែងនឹងបន្ទាត់ដែលឱ្យ ។", .12)] if rng.random() < .4 else []
    return add("tangent_perpendicular_line", "medium", intro(F.tex) + " " + q.replace("{l}", ltex) + iv_note(F), sol, ", ".join(texs), chk, F.e, diagrams=dg)
Q_H = ["រកចំណុចនៃ $@C$ ដែលបន្ទាត់ប៉ះស្របនឹងអ័ក្ស $x'ox$ ។", "រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ដែលស្របនឹងអ័ក្សអាប់ស៊ីស ។", "តើត្រង់ចំណុចណាខ្លះដែលបន្ទាត់ប៉ះនៃខ្សែកោង $@C$ មានមេគុណប្រាប់ទិសសូន្យ ? សរសេរសមីការបន្ទាត់ប៉ះទាំងនោះ ។"]
def s_horizontal():
    r = slope_case(sp.Integer(0))
    if not r: return False
    F, k, rts, st = r
    if F.kind in ("hom",) or not fresh(F.e): return False
    ls, Ts, texs, chk, pts = block_tangents(F, k, rts)
    op = ch(["បន្ទាត់ប៉ះស្របនឹងអ័ក្ស $x'ox$ លុះត្រាតែមេគុណប្រាប់ទិសរបស់វាស្មើសូន្យ គឺ $@n'(x_0)=0$ ។", "ត្រង់ចំណុចបែបនេះ ដេរីវេត្រូវស្មើសូន្យ ។"])
    q = ch(Q_H)
    sol = "\n".join([F.dom, F.ds, op, st] + ls + [concl(texs, pts if asks_pts(q) else None)])
    return add("horizontal_tangent", "medium", intro(F.tex) + " " + q + iv_note(F), sol, ", ".join(texs), chk, F.e,
               diagrams=[gdiag(F, Ts, pts, "ខ្សែកោង និងបន្ទាត់ប៉ះស្របនឹងអ័ក្ស $x'ox$ ។", .1)] if rng.random() < .4 else [])

# ---------- outside point ----------
Q_O = ["រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ដែលគូសចេញពីចំណុច ${A}$ ។", "រកសមីការបន្ទាត់ប៉ះនឹង $@C$ ដែលកាត់តាមចំណុច ${A}$ ។",
       "ពីចំណុច ${A}$ គេគូសបន្ទាត់ប៉ះនឹងខ្សែកោង $@C$ ។ រកកូអរដោនេចំណុចប៉ះ និងសមីការបន្ទាត់ប៉ះ ។", "បង្ហាញថាចំណុច ${A}$ មិននៅលើ $@C$ រួចរកបន្ទាត់ប៉ះនៃ $@C$ ដែលកាត់តាម ${A}$ ។"]
def s_outside():
    t = ch(["p2", "p2", "p2", "hom", "hom", "c3on", "exp", "lnf", "sq"]); Al, Be = None, None
    if t == "p2":
        a = ch([1, -1, 2, -2, R(1, 2), 3]); b, c = rng.randint(-5, 5), rng.randint(-5, 5); t1, t2 = rng.sample(range(-4, 5), 2)
        if (t1 + t2) % 2: return False
        e = a * x**2 + b * x + c; F = poly_fn(e); Al = R(t1 + t2, 2); Be = sp.expand(e.subs(x, t1) + F.d.subs(x, t1) * (Al - t1))
        eq = sp.expand(x**2 - (t1 + t2) * x + t1 * t2); rts = sorted([t1, t2])
        st = f"សម្រួលសមីការនេះ គេបាន $${L(eq).replace('x','t')}=0$$ ដែលមាន $\\Delta={L((t1-t2)**2)}>0$ ។ ឫសរបស់វាគឺ $t_1={L(rts[0])}$ និង $t_2={L(rts[1])}$ ។"
    elif t == "hom":
        u1, u2 = ch([(1, 3), (2, 6), (-1, -3), (1, 2), (2, 4), (3, 6), (-2, -4), (1, -2), (-1, 2), (3, -6), (1, 5), (2, 3), (1, 7)])
        rr = ch([1, 2, 3, 4, 6, -2, -3, 5, -1]); k0, c0 = rng.randint(-3, 3), ch([1, -1, 2, -2, 3, 0])
        Y = sp.Integer(2 * rr) / (u1 + u2); X = 2 * sp.Integer(u1 * u2) / (u1 + u2)
        Al, Be = X - c0, Y + k0; den = x + c0; num = sp.expand(k0 * den + rr); e = num / den
        F = Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), -c0), f"តាមរូបមន្តដេរីវេនៃផលចែក យើងបាន $$@D=-\\frac{{{L(rr)}}}{{({L(den)})^2}}$$".replace("--", "") , -rr / den**2, [], "hom", vas=[-c0])
        rts = sorted([u1 - c0, u2 - c0])
        q = sp.expand(Y * (x + c0)**2 - 2 * rr * (x + c0) + rr * (Al + c0)); q = q / Y
        q = sp.expand(q)
        st = f"គុណអង្គទាំងពីរនឹង $({L(den).replace('x','t')})^2$ រួចសម្រួល គេបានសមីការដឺក្រេទី២ $${L(q).replace('x','t')}=0$$ ដែលមានឫស $t_1={L(rts[0])}$ និង $t_2={L(rts[1])}$ ។ ឫសទាំងពីរខុសពី ${L(-c0)}$ ។"
    elif t == "c3on":
        a = ch([1, -1, 2]); b = rng.randint(-3, 3); c, d = rng.randint(-4, 4), rng.randint(-3, 3); Al = rng.randint(-2, 2)
        e = a * x**3 + b * x**2 + c * x + d; F = poly_fn(e); Be = e.subs(x, Al); t2 = (-R(b, a) - Al) / 2
        if t2 == Al: return False
        rts = [Al, t2]
        st = f"ដោយ $A$ នៅលើ $@C$ សមីការនេះមានឫសឌុប $t={L(Al)}$ ។ បន្ទាប់ពីសម្រួល គេបាន $$-{L(2*a) if a!=-1 else ''}({xm(Al).replace('x','t')})^2({xm(t2).replace('x','t')})=0$$".replace("--", "").replace("-(-2)", "2") + f" នាំឱ្យ $t_1={L(Al)}$ ឬ $t_2={L(t2)}$ ។"
        if a == -1: st = st.replace("$$-(", "$$2(", 1)
    elif t == "exp":
        k = rng.randint(-4, 4); c = rng.randint(-3, 3); e = sp.exp(x) + c; d = sp.exp(x)
        F = Fn(e, L(e), "ដែនកំណត់ $D=IR$ ។", "យើងបាន $$@D=e^{x}$$", d, [], "exp"); Al, Be = k, sp.Integer(c); rts = [k + 1]
        st = f"ដោយ $e^{{t}}>0$ សមីការនេះសម្រួលបាន ${L(k)}-t+1=0$ នាំឱ្យ $t={L(k+1)}$ ។".replace("0-t", "-t")
    elif t == "lnf":
        c = rng.randint(-3, 3); w = rng.randint(-2, 3); e = sp.log(x) + c; d = 1 / x
        F = Fn(e, L(e), "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ ។ ដូចនេះ $D=(0;+\\infty)$ ។", "យើងបាន $$@D=\\frac{1}{x}$$", d, [], "ln", lo=.02)
        Al = sp.Integer(0); Be = sp.Integer(c + w - 1); rts = [sp.exp(w)]
        st = f"ដោយ $x_A=0$ សមីការនេះក្លាយជា ${L(Be)}=\\ln t+{Lq(c)}-1$ នាំឱ្យ $\\ln t={w}$ ឬ $t={L(rts[0])}$ ។"
    else:
        w = ch([1, 2, 3, 4, 5]); c = rng.randint(-3, 3); k = ch([1, 2, 3, 4]); e = k * sp.sqrt(x) + c; d = sp.Integer(k) / (2 * sp.sqrt(x))
        F = Fn(e, L(e), "អនុគមន៍កំណត់លុះត្រាតែ $x\\geq 0$ ។ ដូចនេះ $D=[0;+\\infty)$ ។", f"ចំពោះ $x>0$ យើងបាន $$@D={L(d)}$$", d, [], "sqrt", lo=0.0)
        Al = -sp.Integer(w * w); Be = sp.Integer(c); rts = [sp.Integer(w * w)]
        st = f"គុណអង្គទាំងពីរនឹង $2\\sqrt{{t}}$ រួចសម្រួល គេបាន $t={w*w}$ ។"
    if not fresh(F.e, Al, Be): return False
    if not fresh(F.e): return False
    A = P("A", Al, Be)
    lines = [F.dom, F.ds, f"តាង $t$ ជាអាប់ស៊ីសនៃចំណុចប៉ះ ។ បន្ទាត់ប៉ះត្រង់ចំណុចនោះមានសមីការ $$y=@n'(t)(x-t)+@n(t)$$",
             f"បន្ទាត់នេះកាត់តាម ${A}$ លុះត្រាតែ $${L(Be)}=@n'(t)({L(Al)}-t)+@n(t)$$", st]
    chk = [ck_d(F)]; Ts, texs, pts = [], [], [(Al, Be)]
    for r in rts:
        b, mm = yv(F, r), mv(F, r); c_ = sp.expand(b - mm * r); T = mm * x + c_; tex = lin(mm, c_)
        lines.append(f"ចំពោះ $t={L(r)}$ ៖ $@n({L(r)})={L(b)}$ និង $@n'({L(r)})={L(mm)}$ នាំឱ្យបន្ទាត់ប៉ះ ${tex}$ ។")
        Ts.append(T); texs.append(tex); pts.append((r, b))
        chk += [ck_T(F, r, T), check(f"subs({s(F.e)},x,{s(r)})+subs(diff({s(F.e)},x),x,{s(r)})*(({s(Al)})-({s(r)}))", s(Be), "tangent passes through A")]
    if t == "c3on" : q = ch(Q_O[:3])
    else: q = ch(Q_O)
    lines.append(concl(texs, pts[1:] if asks_pts(q) else None))
    if "មិននៅលើ" in q:
        v = yv(F, Al)
        if not good(v) or v == Be: q = Q_O[1]
        else: lines.insert(1, f"យើងមាន $@n({L(Al)})={L(v)}\\neq {L(Be)}$ ដូច្នេះ $A$ មិននៅលើ $@C$ ។")
    if F.e.subs(x, Al).has(sp.zoo) and "មិននៅលើ" in q: return False
    return add("tangent_through_point", "hard", intro(F.tex) + " " + q.replace("{A}", A), "\n".join(lines), ", ".join(texs), chk, F.e,
               diagrams=[gdiag(F, Ts, pts, "ខ្សែកោង ចំណុច $A$ និងបន្ទាត់ប៉ះដែលកាត់តាម $A$ ។", .2)] if rng.random() < .55 else [])

# ---------- geometric meaning ----------
ANG = {1: ("\\frac{\\pi}{4}", sp.pi / 4), -1: ("\\frac{3\\pi}{4}", 3 * sp.pi / 4), sp.sqrt(3): ("\\frac{\\pi}{3}", sp.pi / 3), -sp.sqrt(3): ("\\frac{2\\pi}{3}", 2 * sp.pi / 3),
       sp.sqrt(3) / 3: ("\\frac{\\pi}{6}", sp.pi / 6), -sp.sqrt(3) / 3: ("\\frac{5\\pi}{6}", 5 * sp.pi / 6)}
def s_angle():
    mm = ch(list(ANG)); a = rng.randint(-3, 3) if sp.sympify(mm).is_Integer else 0; al = ch([1, 2, -1, -2, R(1, 2), 3]); c = rng.randint(-5, 5); k3 = ch([0, 0, 1, -1])
    e = al * (x - a)**2 + k3 * (x - a)**3 + mm * (x - a) + c; e = sp.expand(e); F = poly_fn(e); b = sp.expand(e.subs(x, a))
    if not fresh(F.e): return False
    tex_a, ang = ANG[mm]
    sol = "\n".join([F.ds, f"ត្រង់ $x_0={L(a)}$ មេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះគឺ $@n'({L(a)})={L(mm)}$ ។",
                     "តាមអត្ថន័យធរណីមាត្រនៃដេរីវេ បើ $\\alpha\\in[0;\\pi)$ ជាមុំរវាងបន្ទាត់ប៉ះ និងទិសវិជ្ជមាននៃអ័ក្ស $x'ox$ នោះ $\\tan\\alpha=@n'(x_0)$ ។",
                     f"គេបាន $\\tan\\alpha={L(mm)}$ នាំឱ្យ $\\alpha={tex_a}$ ។", f"{ch(END)} មុំដែលត្រូវរកគឺ $\\boxed{{\\alpha={tex_a}}}$ ។"])
    q = ch(["រកមុំ $\\alpha\\in[0;\\pi)$ រវាងបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ $x={a}$ និងទិសវិជ្ជមាននៃអ័ក្ស $x'ox$ ។", "បន្ទាត់ប៉ះនៃ $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${a}$ បង្កើតបានមុំ $\\alpha$ ជាមួយទិសវិជ្ជមាននៃអ័ក្ស $x'ox$ ។ គណនា $\\alpha$ ដោយ $0\\leq\\alpha<\\pi$ ។"]).replace("{a}", L(a))
    return add("geometric_meaning_angle", "medium", intro(F.tex) + " " + q, sol, f"\\alpha={tex_a}", [ck_d(F), ck_m(F, a, mm), check(f"tan({s(ang)})", f"subs(diff({s(F.e)},x),x,{a})", "tan(alpha)=slope")], F.e)
def s_limit():
    F = rand_fn([fam_p2, fam_p3, fam_hom, fam_p2]); a = ch(F.xs); b = yv(F, a); mm = mv(F, a)
    if not (good(b) and good(mm)) or not fresh(F.e): return False
    h = sp.cancel(sp.together(F.e - b) / (x - a)); num, den = sp.fraction(sp.together(F.e - b))
    qq = sp.cancel(sp.together(F.e - b) / (x - a))
    c = sp.expand(b - mm * a); tex = lin(mm, c)
    sol = "\n".join([f"តាមនិយមន័យ ដេរីវេត្រង់ $x_0={L(a)}$ គឺ $$@n'({L(a)})=\\lim_{{x\\to {L(a)}}}\\frac{{@n(x)-@n({L(a)})}}{{x-({L(a)})}}$$".replace("(x)-@n", "(x)-@n").replace(f"x-({L(a)})", xm(a)),
                     f"យើងមាន $@n({L(a)})={L(b)}$ ។ ពេល $x\\neq {L(a)}$ គេសម្រួលបាន $$\\frac{{@n(x)-@n({L(a)})}}{{{xm(a)}}}={L(qq)}$$",
                     f"យកលីមីតពេល $x\\to {L(a)}$ គេបាន $$@n'({L(a)})={L(mm)}$$",
                     f"តាមអត្ថន័យធរណីមាត្រ ${L(mm)}$ ជាមេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះត្រង់ ${P('A',a,b)}$ ដែលជាទីតាំងលីមីតនៃបន្ទាត់ $(AM)$ ពេល $M$ ខិតជិត $A$ លើខ្សែកោង ។",
                     f"{ch(RTOOK)} $${ym(b)}={mul(mm,a)}\\iff {tex}$$", f"ដូចនេះ $\\boxed{{@n'({L(a)})={L(mm)}}}$ ហើយបន្ទាត់ប៉ះគឺ $\\boxed{{{tex}}}$ ។"])
    q = ch(["ដោយប្រើនិយមន័យនៃដេរីវេ (លីមីតនៃអត្រាកំណើន) គណនា $@n'({a})$ រួចរកសមីការបន្ទាត់ប៉ះត្រង់ $x={a}$ ។", "គណនាលីមីត $\\lim_{{x\\to {a}}}\\frac{{@n(x)-@n({a})}}{{{xa}}}$ ។ បកស្រាយលទ្ធផលតាមធរណីមាត្រ រួចរកសមីការបន្ទាត់ប៉ះ ។".replace("{{", "{").replace("}}", "}")]).replace("{a}", L(a)).replace("{xa}", xm(a))
    return add("derivative_as_limit", "medium", intro(F.tex).replace("$@F=", "$@F=").replace("$y=", "$y=") + " " + q, sol, f"@n'({L(a)})={L(mm)},\\ {tex}",
               [check(f"limit((({s(F.e)})-({s(b)}))/(x-({s(a)})),x,{s(a)})", s(mm), "limit definition"), ck_T(F, a, mm * x + c)], F.e, nm=nm_noy())
def nm_noy():
    while True:
        n = names()
        if n[0] != "y": return n
def s_read():
    """read f(a), f'(a) from a figure: tangent through two lattice points; hidden polynomial."""
    a = rng.randint(-2, 2); b = rng.randint(-2, 3); dx = ch([1, 2, 3]); dy = rng.randint(-4, 4)
    if dy == 0: return False
    mm = R(dy, dx); al = ch([R(1, 2), -R(1, 2), R(1, 4), -R(1, 4), 1, -1]); e = sp.expand(al * (x - a)**2 + mm * (x - a) + b)
    if not fresh(e): return False
    F = poly_fn(e); c = b - mm * a; tex = lin(mm, c); T = mm * x + c; p2 = (a + dx, b + dy)
    q_t = ch([0, 1, 2]); nm = nm_noy(); 
    base = f"រូបខាងក្រោមបង្ហាញខ្សែកោង $@C$ នៃអនុគមន៍ $@n$ និងបន្ទាត់ $(T)$ ប៉ះ $@C$ ត្រង់ចំណុច ${P('A',a,b)}$ ។ បន្ទាត់ $(T)$ កាត់តាមចំណុច ${P('B',p2[0],p2[1])}$ ផងដែរ ។ "
    step = [f"ដោយ $A$ នៅលើ $@C$ នោះ $@n({L(a)})={L(b)}$ ។",
            f"មេគុណប្រាប់ទិសនៃ $(T)$ គឺ $$m=\\frac{{y_B-y_A}}{{x_B-x_A}}=\\frac{{{L(p2[1])}-{Lq(b)}}}{{{L(p2[0])}-{Lq(a)}}}={L(mm)}$$",
            f"តាមអត្ថន័យធរណីមាត្រនៃដេរីវេ $@n'({L(a)})=m={L(mm)}$ ។"]
    chk = [ck_y(F, a, b), ck_m(F, a, mm), ck_T(F, a, T)]
    if q_t == 0:
        q = f"ចូររក $@n({L(a)})$ និង $@n'({L(a)})$ រួចសរសេរសមីការ $(T)$ ។"; step += [f"សមីការ $(T)$ ៖ $${ym(b)}={mul(mm,a)}\\iff {tex}$$", f"ដូចនេះ $\\boxed{{@n({L(a)})={L(b)}}}$ , $\\boxed{{@n'({L(a)})={L(mm)}}}$ និង $\\boxed{{(T):{tex}}}$ ។"]; ans = f"@n({L(a)})={L(b)},\\ @n'({L(a)})={L(mm)},\\ {tex}"
    elif q_t == 1:
        v = sp.expand(b + a * mm); q = f"គេកំណត់ $g(x)=x\\,@n(x)$ ។ គណនា $g'({L(a)})$ ។".replace("g(x)=x\\,f(x)", "g(x)=x\\,f(x)")
        if nm[0] == "g": nm = ("f", "f(x)", "f'(x)", "(C)")
        step += [f"តាមរូបមន្តដេរីវេនៃផលគុណ $g'(x)=@n(x)+x\\,@n'(x)$ ។", f"ដូច្នេះ $g'({L(a)})=@n({L(a)})+{Lq(a)}\\cdot @n'({L(a)})={L(b)}+{Lq(a)}\\cdot {Lq(mm)}={L(v)}$ ។", f"ដូចនេះ $\\boxed{{g'({L(a)})={L(v)}}}$ ។"]
        ans = f"g'({L(a)})={L(v)}"; chk.append(check(f"subs(diff(x*({s(e)}),x),x,{a})", s(v), "product at a"))
    else:
        v = sp.expand(2 * b * mm); q = f"គេកំណត់ $g(x)=[@n(x)]^2$ ។ គណនា $g'({L(a)})$ ។"
        if nm[0] == "g": nm = ("f", "f(x)", "f'(x)", "(C)")
        step += [f"តាមរូបមន្ត $(u^2)'=2uu'$ គេបាន $g'(x)=2\\,@n(x)\\,@n'(x)$ ។", f"ដូច្នេះ $g'({L(a)})=2\\cdot {Lq(b)}\\cdot {Lq(mm)}={L(v)}$ ។", f"ដូចនេះ $\\boxed{{g'({L(a)})={L(v)}}}$ ។"]
        ans = f"g'({L(a)})={L(v)}"; chk.append(check(f"subs(diff(({s(e)})**2,x),x,{a})", s(v), "square at a"))
    dg = [{**gdiag(F, [T], [(a, b), p2], "រូបខ្សែកោង បន្ទាត់ប៉ះត្រង់ $A$ ដែលកាត់តាម $B$ ។", 1.0), "in_problem": True}]
    return add("read_slope_from_graph", "medium", base + q, "\n".join(step), ans, chk, e, nm=nm, diagrams=dg)
def s_approx():
    t = ch(["sq", "sq", "cube", "inv"])
    if t == "sq":
        a = ch([4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144]); h = ch([R(1, 10), -R(1, 10), R(2, 10), R(1, 100), -R(2, 100), R(5, 100), R(3, 10), -R(3, 10), R(4, 10)])
        e = sp.sqrt(x); nt = f"\\sqrt{{{float(a+h):g}}}"
    elif t == "cube":
        a = ch([1, 2, 3, 4, 5]); h = ch([R(1, 10), -R(1, 10), R(1, 100), R(2, 100), -R(2, 100), R(5, 100)]); e = x**3; nt = f"({float(a+h):g})^3"
    else:
        a = ch([1, 2, 4, 5, 10]); h = ch([R(1, 10), -R(1, 10), R(1, 100), R(2, 100), -R(1, 100)]); e = 1 / x; nt = f"\\frac{{1}}{{{float(a+h):g}}}"
    if not fresh(e, a, h): return False
    d = sp.diff(e, x); b, mm = e.subs(x, a), d.subs(x, a); v = b + mm * h; c = sp.expand(b - mm * a); T = mm * x + c
    def dec(r):
        fl = float(r); return f"{fl:.6f}".rstrip("0").rstrip(".")
    et = L(e)
    sol = "\n".join([f"តាង $f(x)={et}$ និង $a={a}$ ។ យើងបាន $f'(x)={L(d)}$ ។", f"នៅជិតចំណុចអាប់ស៊ីស $a$ ខ្សែកោងស្ទើរត្រួតលើបន្ទាត់ប៉ះ ដូច្នេះ $$f(a+h)\\approx f(a)+f'(a)h$$",
                     f"យើងមាន $f({a})={L(b)}$ និង $f'({a})={L(mm)}$ ។ បន្ទាត់ប៉ះត្រង់ $x={a}$ គឺ ${lin(mm,c)}$ ។", f"ចំពោះ $h={L(h)}$ គេបាន $${nt}\\approx {L(b)}+{Lq(mm)}\\cdot {Lq(h)}={L(v)}$$",
                     f"ដូចនេះ $\\boxed{{{nt}\\approx {L(v)}}}$ ។"])
    return add("tangent_approximation", "medium", f"ដោយប្រើបន្ទាត់ប៉ះនៃខ្សែកោង $y={et}$ ត្រង់ចំណុចអាប់ស៊ីស ${a}$ ចូររកតម្លៃប្រហែលនៃ ${nt}$ ។", sol, f"{nt}\\approx {L(v)}",
               [check(f"subs(diff({s(e)},x),x,{a})", s(mm), "slope"), check(f"subs({s(e)},x,{a})+subs(diff({s(e)},x),x,{a})*({s(h)})", s(v), "linear approximation")], (e, a, h)[0] + a + h)

# ---------- axes intersection ----------
def s_axes():
    t = ch(["y", "x", "x"])
    if t == "y":
        F = rand_fn([fam_p3, fam_p2, fam_hom, fam_q21, fam_exp, fam_rec]); a = sp.Integer(0)
        if 0 in [sp.sympify(v) for v in F.vas]: return False
        b, mm = yv(F, 0), mv(F, 0)
        if not (good(b) and good(mm)): return False
        loc = f"យើងមាន $x=0$ នាំឱ្យ $y=@n(0)={L(b)}$ ។ ចំណុចប្រសព្វគឺ ${P('A',0,b)}$ ។"
        q = ch(["រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ចំណុចប្រសព្វរបស់វាជាមួយអ័ក្ស $y'oy$ ។", "ខ្សែកោង $@C$ កាត់អ័ក្សអរដោនេត្រង់ចំណុច $A$ ។ រកសមីការបន្ទាត់ប៉ះត្រង់ $A$ ។"])
    else:
        r = rng.randint(-3, 4); s2 = rng.randint(-4, 4); w = ch(["q", "h", "c", "l"])
        if w == "q":
            e = sp.expand(ch([1, -1, 2]) * (x - r) * (x**2 + 1 + s2 * s2)); F = poly_fn(e)
        elif w == "c":
            k = ch([1, 2, -1]); e = sp.expand(k * (x - r) * (x**2 + s2 * x + s2**2 + 1)); F = poly_fn(e)
        elif w == "h":
            c = rng.randint(-4, 4); k = ch([1, 2, 3, -1])
            if c == -r or c == 0: return False
            num = k * x - k * r; den = x + c; e = num / den; dt = k * (c + r)
            F = Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), -c), ch(RQUOT) + f" $$@D=\\frac{{{Lq(k)}({L(den)})-({L(num)})}}{{({L(den)})^2}}=\\frac{{{L(dt)}}}{{({L(den)})^2}}$$", sp.Integer(dt) / den**2, [], "hom", vas=[-c])
        else:
            k = ch([1, 2, 3, -1]); cc = ch([1, 2, -1, 3]); e = k * sp.log(cc * x if cc > 0 else x); r = R(1, cc) if cc > 0 else sp.Integer(1); d = sp.Integer(k) / x
            F = Fn(e, L(e), "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ ។ ដូចនេះ $D=(0;+\\infty)$ ។", f"តាមរូបមន្ត $(\\ln u)'=\\frac{{u'}}{{u}}$ យើងបាន $$@D={L(d)}$$", d, [], "ln", lo=.02)
        a = r; b = sp.Integer(0); mm = mv(F, a)
        why0 = ("ភាគយកជាពហុធាដឺក្រេទីមួយ ដូច្នេះវាមានឫសតែមួយលើ $D$" if w == "h" else "អនុគមន៍ $\\ln$ កើនដាច់ខាតលើ $D$ ដូច្នេះសមីការមានឫសតែមួយ")
        loc = f"ដោះស្រាយ $@n(x)=0$ ។ {why0} គឺ $x={L(a)}$ ។ ចំណុចប្រសព្វគឺ ${P('A',a,0)}$ ។"
        q = ch(["រកសមីការបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ចំណុចប្រសព្វរបស់វាជាមួយអ័ក្ស $x'ox$ ។", "ខ្សែកោង $@C$ កាត់អ័ក្សអាប់ស៊ីសត្រង់ចំណុច $A$ ។ រកកូអរដោនេ $A$ និងសមីការបន្ទាត់ប៉ះត្រង់ $A$ ។"])
        if F.kind == "poly" and w in "qc":
            co = sp.cancel(F.e / (x - r))
            loc = f"គេបំបែកបាន $@F=({xm(r)})({L(co)})$ ។ កត្តាទីពីរវិជ្ជមានជានិច្ច ឬអវិជ្ជមានជានិច្ច (មាន $\\Delta<0$) ដូច្នេះ $@n(x)=0$ មានឫសតែមួយ $x={L(a)}$ ។ ចំណុចប្រសព្វគឺ ${P('A',a,0)}$ ។"
    if not fresh(F.e): return False
    tx, T, tex = tan_lines(mm, a, b)
    pre = f"$\\boxed{{{P('A',a,b)}}}$ ហើយ" if "រកកូអរដោនេ $A$" in q else ""
    sol = "\n".join([F.dom, loc, F.ds, f"មេគុណប្រាប់ទិសត្រង់ $A$ គឺ $@n'({L(a)})={L(mm)}$ ។", form(), tx, f"{ch(END)} {pre} សមីការបន្ទាត់ប៉ះត្រង់ $A$ គឺ $\\boxed{{{tex}}}$ ។".replace("  ", " ")])
    return add("tangent_at_axis_intersection", "medium", intro(F.tex) + " " + q, sol, tex, [ck_d(F), ck_y(F, a, b), ck_m(F, a, mm), ck_T(F, a, T)], F.e,
               diagrams=[gdiag(F, [T], [(a, b)], ch(ALT), .1)] if rng.random() < .3 else [])

# ---------- parameters ----------
def s_params():
    t = ch(["p2", "p2", "hom", "rec", "p3"])
    a = rng.randint(-3, 3); mm = sp.Integer(rng.randint(-5, 6)); b0 = sp.Integer(rng.randint(-5, 6))
    if t == "p2":
        A = ch([1, -1, 2, -2, 3, R(1, 2)]); B = mm - 2 * A * a; C = b0 - A * a**2 - B * a; e = A * x**2 + B * x + C
        ft = f"{L(A*x**2)}+ax+b"; d = f"{L(2*A*x)}+a"
        sysm = f"\\begin{{cases}}{L(A*a*a)}+{Lq(a)}a+b={L(b0)}\\\\ {L(2*A*a)}+a={L(mm)}\\end{{cases}}"
        sol2 = f"សមីការទីពីរឱ្យ $a={L(B)}$ ។ ជំនួសក្នុងសមីការទីមួយ គេបាន $b={L(C)}$ ។"; res = f"a={L(B)},\\ b={L(C)}"; va = [(B, "a"), (C, "b")]
    elif t == "p3":
        A = ch([1, -1, 2]); c = rng.randint(-3, 3); B = mm - 3 * A * a**2 - 2 * c * a; C = b0 - A * a**3 - c * a**2 - B * a
        e = A * x**3 + c * x**2 + B * x + C; ft = f"{L(A*x**3+c*x**2)}+ax+b"; d = f"{L(3*A*x**2+2*c*x)}+a"
        sysm = f"\\begin{{cases}}{L(A*a**3+c*a**2)}+{Lq(a)}a+b={L(b0)}\\\\ {L(3*A*a**2+2*c*a)}+a={L(mm)}\\end{{cases}}"
        sol2 = f"សមីការទីពីរឱ្យ $a={L(B)}$ ។ ជំនួសក្នុងសមីការទីមួយ គេបាន $b={L(C)}$ ។"; res = f"a={L(B)},\\ b={L(C)}"; va = [(B, "a"), (C, "b")]
    elif t == "hom":
        h = ch([1, 2, -1, -2, 3]); w = ch([1, -1, 2, -2]); a = h + w; b_ = rng.randint(-4, 4); B = rng.randint(-4, 4)
        if B == b_ * 1 and False: return False
        # f=(ax+b)/(x-h), unknown a,b with f(a0)=b0,f'(a0)=m : f=A+r/(x-h), r=-m w^2, A=b0-r/w
        r = -mm * w * w
        if r == 0: return False
        Aa = b0 - r / w; Bb = r - Aa * h; e = (Aa * x + Bb) / (x - h); ft = f"\\frac{{ax+b}}{{{xm(h)}}}"; d = f"\\frac{{{Lq(-h)}a-b}}{{({xm(h)})^2}}"
        sysm = f"\\begin{{cases}}\\frac{{{L(a)}a+b}}{{{L(w)}}}={L(b0)}\\\\ \\frac{{{Lq(-h)}a-b}}{{{w*w}}}={L(mm)}\\end{{cases}}"
        sol2 = f"លុបភាគបែង រួចបូកសមីការទាំងពីរ គេបាន $a={L(Aa)}$ និង $b={L(Bb)}$ ។"; res = f"a={L(Aa)},\\ b={L(Bb)}"; va = [(Aa, "a"), (Bb, "b")]
    else:
        a = ch([1, 2, -1, -2, 3]); B = R(b0 * 1 + mm * a, 2 * 1) / 1 / a * 1  # f=ax... : f=Ax+C/x
        Aa = (b0 / a + mm) / 2; Cc = (b0 - Aa * a) * a; e = Aa * x + Cc / x; ft = "ax+\\frac{b}{x}"; d = "a-\\frac{b}{x^2}"
        if Cc == 0: return False
        sysm = f"\\begin{{cases}}{L(a)}a+\\frac{{b}}{{{L(a)}}}={L(b0)}\\\\ a-\\frac{{b}}{{{a*a}}}={L(mm)}\\end{{cases}}"
        sol2 = f"ដោះស្រាយប្រព័ន្ធនេះ គេបាន $a={L(Aa)}$ និង $b={L(Cc)}$ ។"; res = f"a={L(Aa)},\\ b={L(Cc)}"; va = [(Aa, "a"), (Cc, "b")]
    e = sp.cancel(e) if t == "hom" else e
    if not fresh(e): return False
    sol = "\n".join([f"យើងមាន $@F={ft}$ នោះ $@D={d}$ ។", f"លក្ខខណ្ឌ ៖ ខ្សែកោងកាត់តាម ${P('A',a,b0)}$ មានន័យថា $@n({L(a)})={L(b0)}$ ហើយមេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះត្រង់ $A$ ស្មើនឹង ${L(mm)}$ មានន័យថា $@n'({L(a)})={L(mm)}$ ។",
                     f"គេបានប្រព័ន្ធ $${sysm}$$", sol2, f"{ch(END)} $\\boxed{{{res}}}$ ។"])
    q = ch([f"គេឱ្យ $@F={ft}$ ដែល $a,b$ ជាចំនួនពិត ។ កំណត់ $a$ និង $b$ ដើម្បីឱ្យខ្សែកោងកាត់តាមចំណុច ${P('A',a,b0)}$ ហើយបន្ទាត់ប៉ះត្រង់ $A$ មានមេគុណប្រាប់ទិស ${L(mm)}$ ។",
            f"អនុគមន៍ $@n$ កំណត់ដោយ $@F={ft}$ ។ រកតម្លៃ $a$ និង $b$ ដើម្បីឱ្យបន្ទាត់ ${lin(mm, b0-mm*a)}$ ប៉ះនឹងខ្សែកោងត្រង់ចំណុចអាប់ស៊ីស ${L(a)}$ ។"])
    return add("find_parameters", "hard", q, sol, res, [check(f"subs({s(e)},x,{a})", s(b0), "passes through A"), check(f"subs(diff({s(e)},x),x,{a})", s(mm), "slope at A")], e, nm=nm_noy())

# ---------- double root ----------
def s_double():
    t = ch(["pp", "pp", "pm", "hy"])
    if t == "pp":
        A = ch([1, -1, 2, R(1, 2), -2, 3]); x0 = rng.randint(-4, 4); k = rng.randint(-6, 6); C = rng.randint(-4, 5); B = k - 2 * A * x0
        p = sp.expand(A * x0**2 + B * x0 + C - k * x0); e = A * x**2 + B * x + C; F = poly_fn(e); q2 = sp.expand(e - k * x)
        dlt = f"\\Delta=({L(B-k)})^2-4({L(A)})({L(C)}-p)".replace("(0-p)", "(-p)")
        sol = "\n".join([f"អាប់ស៊ីសនៃចំណុចប្រសព្វជាឫសនៃសមីការ $${F.tex}={lin(k,0)[2:]}+p\\iff {L(q2)}-p=0$$", f"បន្ទាត់ប៉ះនឹងក្រាបលុះត្រាតែសមីការនេះមានឫសឌុប គឺ $\\Delta=0$ ។", f"យើងមាន $${dlt}$$ ដោះស្រាយ $\\Delta=0$ គេបាន $p={L(p)}$ ។",
                         f"ឫសឌុបគឺ $x=-\\frac{{{L(B-k)}}}{{2\\cdot {Lq(A)}}}={L(x0)}$ ដូច្នេះចំណុចប៉ះគឺ ${P('M',x0,yv(F,x0))}$ ។", f"{ch(END)} $\\boxed{{p={L(p)}}}$ ហើយចំណុចប៉ះគឺ $\\boxed{{{P('M',x0,yv(F,x0))}}}$ ។"])
        pr = f"គេឱ្យប៉ារ៉ាបូល $@C:y={F.tex}$ និងបន្ទាត់ $(d):y={lin(k,0)[2:]}+p$ ។ រកតម្លៃ $p$ ដើម្បីឱ្យ $(d)$ ប៉ះនឹង $@C$ រួចរកចំណុចប៉ះ ។".replace("0+p", "p")
        sol = sol.replace("=0+p", "=p")
        chk = [check(f"subs(({s(e)})-(({s(k)})*x+({s(p)})),x,{x0})", "0", "common point"), check(f"subs(diff({s(e)},x),x,{x0})", s(k), "same slope")]
        if not fresh(e): return False
        return add("tangency_double_root", "hard", pr, sol, f"p={L(p)}", chk, e, nm=("y", "y", "y'", "(C)"))
    if t == "pm":
        # line through (0;p) tangent to y=x^2+bx+c, two slopes
        w = rng.randint(1, 4); b = rng.randint(-5, 5); c = rng.randint(-3, 6); A = ch([1, 2, -1]); p = c - A * w * w
        e = A * x**2 + b * x + c; F = poly_fn(e); s1 = sorted([b + 2 * A * w, b - 2 * A * w]); r1 = (s1[0] - b) / (2 * sp.Integer(A)); r2 = (s1[1] - b) / (2 * sp.Integer(A))
        if not fresh(e): return False
        sol = "\n".join([f"បន្ទាត់ដែលកាត់តាម ${P('B',0,p)}$ មានសមីការ $y=mx{'+' if p>=0 else ''}{L(p)}$ ។", f"សមីការអាប់ស៊ីសប្រសព្វ ៖ $${L(A*x**2)}+({L(b)}-m)x+{Lq(c-p)}=0$$", "បន្ទាត់ប៉ះនឹងក្រាបលុះត្រាតែ $\\Delta=0$ ។",
                         f"$$\\Delta=({L(b)}-m)^2-4\\cdot {Lq(A)}\\cdot {Lq(c-p)}=({xm(b).replace('x','m')})^2-{L(4*A*(c-p))}=0$$", f"នាំឱ្យ ${xm(b).replace('x','m')}=\\pm {L(2*abs(A)*w)}$ ដូច្នេះ $m_1={L(s1[0])}$ ឬ $m_2={L(s1[1])}$ ។",
                         f"ដូចនេះ បន្ទាត់ប៉ះគឺ $\\boxed{{{lin(s1[0],p)}}}$ និង $\\boxed{{{lin(s1[1],p)}}}$ ។"])
        pr = f"គេឱ្យខ្សែកោង $(P):y={F.tex}$ ។ ដោយប្រើលក្ខខណ្ឌឌីសគ្រីមីណង់ រកសមីការបន្ទាត់ដែលកាត់តាមចំណុច ${P('B',0,p)}$ ហើយប៉ះនឹង $(P)$ ។"
        chk = [check(f"subs(({s(e)})-(({s(s1[0])})*x+({s(p)})),x,{s(r1)})", "0", "tangent 1"), check(f"subs(diff({s(e)},x),x,{s(r1)})", s(s1[0]), "slope 1"),
               check(f"subs(({s(e)})-(({s(s1[1])})*x+({s(p)})),x,{s(r2)})", "0", "tangent 2"), check(f"subs(diff({s(e)},x),x,{s(r2)})", s(s1[1]), "slope 2")]
        return add("tangency_double_root", "hard", pr, sol, f"{lin(s1[0],p)},\\ {lin(s1[1],p)}", chk, e, nm=("y", "y", "y'", "(P)"))
    w = ch([1, 2, 3, 4, 5, 6]); k = ch([-1, -2, -4, -3, R(-1, 2), -R(1, 4), 1, 2]); r = -k * w * w if k < 0 else -k * w * w; r = sp.sympify(r); e = r / x; x0 = sp.Integer(w); p = 2 * r / sp.Integer(w)
    if not fresh(e): return False
    sol = "\n".join([f"លក្ខខណ្ឌ $x\\neq 0$ ។ សមីការអាប់ស៊ីសប្រសព្វ ៖ $$\\frac{{{L(r)}}}{{x}}={L(k)}x+p\\iff {L(k)}x^2+px{'+' if r<0 else '-'}{L(abs(r))}=0$$", "បន្ទាត់ប៉ះនឹងខ្សែកោងលុះត្រាតែសមីការមានឫសឌុប គឺ $\\Delta=0$ ។",
                     f"$$\\Delta=p^2+{Lq(4*k*r)}=0$$".replace("+(-", "-(").replace("-(", "-").replace(")=0", "=0") if False else f"$$\\Delta=p^2+4\\cdot {Lq(k)}\\cdot {Lq(r)}=p^2{'+' if 4*k*r>0 else '-'}{L(abs(4*k*r))}=0$$",
                     f"គេបាន $p=\\pm {L(abs(p))}$ ។", f"ដូចនេះ $\\boxed{{p={L(abs(p))}}}$ ឬ $\\boxed{{p=-{L(abs(p))}}}$ ។"])
    if 4 * k * r > 0: return False
    pr = f"គេឱ្យអ៊ីពែបូល $(H):y=\\frac{{{L(r)}}}{{x}}$ និងបន្ទាត់ $(d):y={L(k)}x+p$ ។ រកតម្លៃ $p$ ដើម្បីឱ្យ $(d)$ ប៉ះនឹង $(H)$ ។".replace("=1x", "=x").replace("=-1x", "=-x")
    sol = sol.replace("=1x", "=x").replace("=-1x", "=-x")
    chk = [check(f"subs(({s(e)})-(({s(k)})*x+({s(p)})),x,{w})", "0", "common point"), check(f"subs(diff({s(e)},x),x,{w})", s(k), "same slope"),
           check(f"subs(({s(e)})-(({s(k)})*x-({s(p)})),x,-{w})", "0", "common point 2"), check(f"subs(diff({s(e)},x),x,-{w})", s(k), "same slope 2")]
    return add("tangency_double_root", "hard", pr, sol, f"p=\\pm {L(abs(p))}", chk, e, nm=("y", "y", "y'", "(H)"))

# ---------- two curves ----------
def s_common():
    t0 = rng.randint(-3, 3); y0 = rng.randint(-4, 4); mm = rng.randint(-4, 4); a1 = ch([1, 2, -1, R(1, 2)]); a2 = ch([-1, -2, 3, 1, R(-1, 2), 2])
    if a1 == a2: return False
    f = sp.expand(a1 * (x - t0)**2 + mm * (x - t0) + y0)
    k3 = ch([0, 1, -1]); g = sp.expand(a2 * (x - t0)**2 + k3 * (x - t0)**3 + mm * (x - t0) + y0)
    if not fresh(f, g): return False
    df, dg_ = sp.diff(f, x), sp.diff(g, x); c = y0 - mm * t0; tex = lin(mm, c); T = mm * x + c
    sol = "\n".join([f"យើងមាន $f({L(t0)})={L(y0)}$ និង $g({L(t0)})={L(y0)}$ ដូច្នេះ ${P('A',t0,y0)}$ នៅលើខ្សែកោងទាំងពីរ ។", f"ដេរីវេ ៖ $f'(x)={L(df)}$ និង $g'(x)={L(dg_)}$ ។",
                     f"ត្រង់ $x={L(t0)}$ គេបាន $f'({L(t0)})={L(mm)}$ និង $g'({L(t0)})={L(mm)}$ ។", "ដោយមេគុណប្រាប់ទិសស្មើគ្នាត្រង់ចំណុចរួម ខ្សែកោងទាំងពីរមានបន្ទាត់ប៉ះរួមត្រង់ $A$ ។",
                     f"សមីការបន្ទាត់ប៉ះរួម ៖ $${ym(y0)}={mul(mm,t0)}\\iff {tex}$$" if mm else f"បន្ទាត់ប៉ះរួមគឺ ${tex}$ ។", f"ដូចនេះ បន្ទាត់ប៉ះរួមមានសមីការ $\\boxed{{{tex}}}$ ។"])
    q = ch(["បង្ហាញថាខ្សែកោងទាំងពីរប៉ះគ្នាត្រង់ចំណុច $A$ ដែលមានអាប់ស៊ីស ${a}$ រួចរកសមីការបន្ទាត់ប៉ះរួម ។", "ផ្ទៀងផ្ទាត់ថាខ្សែកោងទាំងពីរមានបន្ទាត់ប៉ះរួមត្រង់ចំណុចអាប់ស៊ីស ${a}$ ។ រកសមីការបន្ទាត់នោះ ។"]).replace("{a}", L(t0))
    pr = f"គេឱ្យអនុគមន៍ $f(x)={L(f)}$ និង $g(x)={L(g)}$ ។ " + q
    chk = [check(f"subs({s(f)},x,{t0})", s(y0)), check(f"subs({s(g)},x,{t0})", s(y0)), check(f"subs(diff({s(f)},x),x,{t0})", s(mm)), check(f"subs(diff({s(g)},x),x,{t0})", s(mm)),
           check(f"subs({s(f)},x,{t0})+subs(diff({s(f)},x),x,{t0})*(x-({t0}))", s(T), "common tangent")]
    G = poly_fn(f); G2 = None
    dg = [gdiag(G, [T, g], [(t0, y0)], "ខ្សែកោងពីរប៉ះគ្នាត្រង់ $A$ ជាមួយបន្ទាត់ប៉ះរួម ។", .1)] if rng.random() < .3 else []
    return add("common_tangent", "hard", pr, sol, tex, chk, f + 2 * g, nm=("f", "f(x)", "f'(x)", "(C)"), diagrams=dg)

# ---------- position / tangent crosses the curve ----------
def s_position():
    a = ch([1, -1, 2, -2]); p = rng.randint(-3, 3); q = rng.randint(-3, 3); c = rng.randint(-3, 3); m0 = rng.randint(-3, 3); d0 = rng.randint(-3, 3)
    if p == q: return False
    e = sp.expand(a * (x - p)**2 * (x - q) + m0 * x + d0); F = poly_fn(e, kind="poly")
    if not fresh(e): return False
    b, mm = e.subs(x, p), F.d.subs(x, p); T = m0 * x + d0; tex = lin(m0, d0)
    assert mv(F, p) == m0
    diffx = sp.expand(e - T); lo_, hi_ = ("-", "+") if a > 0 else ("+", "-")
    table = f"\\begin{{array}}{{c|ccccc}}\nx & -\\infty & {L(min(p,q))} & & {L(max(p,q))} & +\\infty \\\\\n\\hline\n@F-y & {lo_} & {'0' } & {lo_ if p<q else hi_} & 0 & {hi_}\n\\end{{array}}"
    if p < q: table = f"\\begin{{array}}{{c|ccccccc}}\nx & -\\infty & & {L(p)} & & {L(q)} & & +\\infty \\\\\n\\hline\n\\varphi(x) & & {lo_} & 0 & {lo_} & 0 & {hi_} &\n\\end{{array}}"
    else: table = f"\\begin{{array}}{{c|ccccccc}}\nx & -\\infty & & {L(q)} & & {L(p)} & & +\\infty \\\\\n\\hline\n\\varphi(x) & & {lo_} & 0 & {hi_} & 0 & {hi_} &\n\\end{{array}}"
    below = f"$x<{L(q)}$" ; above = f"$x>{L(q)}$"
    if a < 0: below, above = above, below
    sol = "\n".join([F.ds, f"$@n({L(p)})={L(b)}$ និង $@n'({L(p)})={L(mm)}$ ។ បន្ទាត់ប៉ះគឺ $$(T):{tex}$$", f"តាង $\\varphi(x)=@n(x)-({lin(m0,d0)[2:]})$ ។ គេបាន $$\\varphi(x)={L(diffx)}={L(a) if abs(a)!=1 else ('-' if a<0 else '')}({xm(p)})^2({xm(q)})$$",
                     f"ដោយ $({xm(p)})^2\\geq 0$ សញ្ញានៃ $\\varphi(x)$ អាស្រ័យតាមសញ្ញានៃ ${L(a*(x-q))}$ ។", f"ពេល {above} គេបាន $\\varphi(x)>0$ (លើកលែងត្រង់ $x={L(p)}$) ខ្សែកោងនៅខាងលើ $(T)$ ។ ពេល {below} គេបាន $\\varphi(x)<0$ (លើកលែងត្រង់ $x={L(p)}$) ខ្សែកោងនៅខាងក្រោម $(T)$ ។",
                     f"ដូចនេះ $\\boxed{{(T):{tex}}}$ ហើយ $@C$ ជួប $(T)$ ត្រង់ចំណុចអាប់ស៊ីស ${L(p)}$ (ប៉ះ) និង ${L(q)}$ (កាត់) ។"])
    pr = intro(F.tex) + " " + ch([f"រកសមីការបន្ទាត់ប៉ះ $(T)$ ត្រង់ចំណុចអាប់ស៊ីស ${L(p)}$ រួចសិក្សាទីតាំងនៃ $@C$ ធៀបនឹង $(T)$ ។", f"សរសេរសមីការបន្ទាត់ប៉ះ $(T)$ នៃខ្សែកោងត្រង់ $x={L(p)}$ ។ សិក្សាសញ្ញានៃ $@n(x)-y_T$ ដើម្បីរកទីតាំងរបស់ $@C$ ធៀបនឹង $(T)$ ។"])
    dgm = [{"type": "sign_table", "latex": table, "alt_km": "តារាងសញ្ញានៃ $\\varphi(x)$ ។", "image": None}, gdiag(F, [T], [(p, b), (q, T.subs(x, q))], ch(ALT), .1)]
    return add("curve_position_vs_tangent", "hard", pr, sol, tex, [ck_d(F), ck_T(F, p, T), check(f"({s(e)})-(({s(T)}))", s(a * (x - p)**2 * (x - q)), "factorisation")], e, nm=nm_noy(), diagrams=dgm)
def s_second():
    a = ch([1, -1, 2]); b = rng.randint(-4, 4); c = rng.randint(-5, 5); d = rng.randint(-4, 4); t = rng.randint(-2, 3)
    e = a * x**3 + b * x**2 + c * x + d; F = poly_fn(e); x1 = -R(b, a) - 2 * t
    if x1 == t or not fresh(e): return False
    y0, mm = e.subs(x, t), F.d.subs(x, t); cc = y0 - mm * t; T = mm * x + cc; y1 = e.subs(x, x1); tex = lin(mm, cc)
    sol = "\n".join([F.ds, f"$@n({L(t)})={L(y0)}$ និង $@n'({L(t)})={L(mm)}$ ។ បន្ទាត់ប៉ះមានសមីការ $$(T):{ym(y0)}={mul(mm,t)}\\iff {tex}$$", f"អាប់ស៊ីសនៃចំណុចប្រសព្វរវាង $@C$ និង $(T)$ ជាឫសនៃសមីការ $$@F={tex[2:]}\\iff {L(sp.expand(e-T))}=0$$",
                     f"ដោយ $x={L(t)}$ ជាឫសឌុប (ចំណុចប៉ះ) គេបំបែកបាន $${L(a) if abs(a)!=1 else ('-' if a<0 else '')}({xm(t)})^2({xm(x1)})=0$$", f"ដូច្នេះឫសទីពីរគឺ $x={L(x1)}$ ហើយ $y=@n({L(x1)})={L(y1)}$ ។", f"ដូចនេះ @@ $(T)$ កាត់ $@C$ ម្ដងទៀតត្រង់ចំណុច $\\boxed{{{P('B',x1,y1)}}}$ ។"])
    q = ch([f"បន្ទាត់ប៉ះ $(T)$ ត្រង់ចំណុចអាប់ស៊ីស ${L(t)}$ កាត់ $@C$ ម្ដងទៀតត្រង់ចំណុច $B$ ។ រកកូអរដោនេ $B$ ។", f"រកសមីការបន្ទាត់ប៉ះ $(T)$ ត្រង់ $x={L(t)}$ រួចរកចំណុចប្រសព្វផ្សេងទៀតរវាង $(T)$ និង $@C$ ។"])
    sol = sol.replace("ដូចនេះ @@ ", f"ដូចនេះ $\\boxed{{(T):{tex}}}$ ហើយ " if q.startswith("រកសមីការ") else "ដូចនេះ ")
    pr = intro(F.tex) + " " + q
    return add("tangent_second_intersection", "hard", pr, sol, P("B", x1, y1), [ck_d(F), ck_T(F, t, T), check(f"subs(({s(e)})-(({s(T)})),x,{s(x1)})", "0", "B on both"), check(f"subs({s(e)},x,{s(x1)})", s(y1))], e, nm=nm_noy(),
               diagrams=[gdiag(F, [T], [(t, y0), (x1, y1)], ch(ALT), .1)] if rng.random() < .3 else [])
def s_inflect():
    a = ch([1, -1, 2, -2, R(1, 3), -R(1, 3)]); i = rng.randint(-3, 3); c = rng.randint(-4, 4); d = rng.randint(-4, 4)
    e = sp.expand(a * (x - i)**3 + c * (x - i) + d); F = poly_fn(e)
    if not fresh(e): return False
    d2 = sp.diff(F.d, x); T = c * (x - i) + d; cc = d - c * i; tex = lin(c, cc)
    sol = "\n".join([F.ds, f"ដេរីវេទី២ ៖ $@n''(x)={L(d2)}$ ។", f"$@n''(x)=0$ មានឫស $x={L(i)}$ ហើយ $@n''$ ប្ដូរសញ្ញាត្រង់នោះ ។ ដូច្នេះ $@C$ មានចំណុចរបត់ ${P('I',i,d)}$ ។", f"$@n'({L(i)})={L(c)}$ ។", f"បន្ទាត់ប៉ះត្រង់ $I$ ៖ $${ym(d)}={mul(c,i)}\\iff {tex}$$" if c else f"បន្ទាត់ប៉ះត្រង់ $I$ ស្របនឹង $x'ox$ គឺ ${tex}$ ។",
                     f"ដូចនេះ ចំណុចរបត់គឺ $\\boxed{{{P('I',i,d)}}}$ និងបន្ទាត់ប៉ះគឺ $\\boxed{{{tex}}}$ ។"])
    pr = intro(F.tex) + " " + ch(["រកកូអរដោនេចំណុចរបត់ $I$ នៃ $@C$ រួចសរសេរសមីការបន្ទាត់ប៉ះត្រង់ $I$ ។", "គណនា $@n''(x)$ ។ ទាញរកចំណុចរបត់ $I$ និងសមីការបន្ទាត់ប៉ះ $@C$ ត្រង់ $I$ ។"])
    return add("tangent_at_inflection", "medium", pr, sol, f"I({L(i)};{L(d)}),\\ {tex}", [ck_d(F), check(f"subs(diff({s(e)},x,2),x,{i})", "0", "f''=0"), ck_y(F, i, d), ck_T(F, i, T)], e, nm=nm_noy(),
               diagrams=[gdiag(F, [T], [(i, d)], "ខ្សែកោង និងបន្ទាត់ប៉ះត្រង់ចំណុចរបត់ ។", .1)] if rng.random() < .35 else [])
def s_area():
    F = rand_fn([fam_p2, fam_hom, fam_rec, fam_p3]); a = ch(F.xs); b, mm = yv(F, a), mv(F, a)
    if not (good(b) and good(mm)) or mm == 0: return False
    c = sp.expand(b - mm * a)
    if c == 0 or not fresh(F.e): return False
    xi = -c / mm; ar = sp.Abs(c * xi) / 2; T = mm * x + c; tex = lin(mm, c)
    if sp.fraction(ar)[1] > 200: return False
    sol = "\n".join([F.dom, F.ds, f"ត្រង់ $x={L(a)}$ ៖ $y={L(b)}$ និង $@n'({L(a)})={L(mm)}$ ។", f"បន្ទាត់ប៉ះ ៖ $${ym(b)}={mul(mm,a)}\\iff {tex}$$", f"ពេល $x=0$ គេបាន $y={L(c)}$ ហើយពេល $y=0$ គេបាន $x={L(xi)}$ ។ បន្ទាត់ប៉ះកាត់អ័ក្សត្រង់ ${P('P',xi,0)}$ និង ${P('Q',0,c)}$ ។",
                     f"ត្រីកោណ $OPQ$ កែងត្រង់ $O$ ដូច្នេះ $$S=\\frac{{1}}{{2}}\\cdot OP\\cdot OQ=\\frac{{1}}{{2}}\\cdot {L(abs(xi))}\\cdot {L(abs(c))}={L(ar)}$$", f"ដូចនេះ ក្រឡាផ្ទៃត្រីកោណគឺ $\\boxed{{S={L(ar)}}}$ ឯកតាផ្ទៃ ។"])
    pr = intro(F.tex) + " " + f"បន្ទាត់ប៉ះនៃ $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${L(a)}$ កាត់អ័ក្ស $x'ox$ ត្រង់ $P$ និងអ័ក្ស $y'oy$ ត្រង់ $Q$ ។ គណនាក្រឡាផ្ទៃត្រីកោណ $OPQ$ ។"
    return add("tangent_triangle_area", "hard", pr, sol, f"S={L(ar)}", [ck_d(F), ck_T(F, a, T), check(f"Abs((subs({s(T)},x,0))*(-subs({s(T)},x,0)/diff({s(T)},x)))/2", s(ar), "area")], F.e)
def s_pair():
    """cubic: tangents at symmetric points are parallel; parabola: perpendicular tangents"""
    if rng.random() < .5:
        i = rng.randint(-3, 3); w = rng.randint(1, 3); a = ch([1, -1, 2]); c = rng.randint(-4, 4); d = rng.randint(-4, 4)
        e = sp.expand(a * (x - i)**3 + c * (x - i) + d); F = poly_fn(e); p, q = i - w, i + w; mm = F.d.subs(x, p)
        if not fresh(e): return False
        sol = "\n".join([F.ds, f"$@n'({L(p)})={L(mm)}$ និង $@n'({L(q)})={L(F.d.subs(x,q))}$ ។", f"មេគុណប្រាប់ទិសស្មើគ្នា ដូច្នេះបន្ទាត់ប៉ះទាំងពីរស្របគ្នា ។", f"បន្ទាត់ទាំងពីរគឺ ${lin(mm, e.subs(x,p)-mm*p)}$ និង ${lin(mm, e.subs(x,q)-mm*q)}$ ។", f"ដូចនេះ បន្ទាត់ប៉ះទាំងពីរស្របគ្នា ដោយមានមេគុណប្រាប់ទិសរួម $\\boxed{{{L(mm)}}}$ ។"])
        pr = intro(F.tex) + f" បង្ហាញថាបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${L(p)}$ និង ${L(q)}$ ស្របគ្នា ។"
        return add("parallel_tangents_pair", "medium", pr, sol, L(mm), [ck_d(F), ck_m(F, p, mm), ck_m(F, q, mm)], e, nm=nm_noy())
    A = ch([R(1, 2), 1, R(1, 4), -R(1, 2), -1, 2, R(1, 6)]); t1 = ch([1, 2, -1, R(1, 2), 3, -2, R(1, 4), R(3, 2)]); h = rng.randint(-3, 3); c = rng.randint(-3, 4)
    # slopes 2A t1 and -1/(2A t1)
    t2 = -sp.Integer(1) / (4 * A * A * t1); e = sp.expand(A * (x - h)**2 + c); F = poly_fn(e); p, q = h + t1, h + t2; m1, m2 = F.d.subs(x, p), F.d.subs(x, q)
    if not fresh(e): return False
    sol = "\n".join([F.ds, f"$@n'({L(p)})={L(m1)}$ និង $@n'({L(q)})={L(m2)}$ ។", f"ផលគុណមេគុណប្រាប់ទិស ៖ $$@n'({L(p)})\\cdot @n'({L(q)})={Lq(m1)}\\cdot {Lq(m2)}=-1$$", "ដូចនេះ បន្ទាត់ប៉ះទាំងពីរកែងគ្នា ។"])
    pr = intro(F.tex) + f" បង្ហាញថាបន្ទាត់ប៉ះនៃ $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${L(p)}$ និង ${L(q)}$ កែងគ្នា ។"
    return add("perpendicular_tangents_pair", "medium", pr, sol, "m_1m_2=-1", [ck_d(F), check(f"subs(diff({s(e)},x),x,{s(p)})*subs(diff({s(e)},x),x,{s(q)})", "-1", "perpendicular")], e, nm=nm_noy())
def s_none():
    """no tangent with a given property"""
    F = fam_q21()
    r = None
    num, den = sp.fraction(F.e); c = den.subs(x, 0); rem = sp.rem(sp.Poly(num, x), sp.Poly(den, x)).as_expr()
    if rem == 0 or not fresh(F.e): return False
    quo = sp.quo(sp.Poly(num, x), sp.Poly(den, x)).as_expr()
    sol = "\n".join([F.dom, f"ចែកភាគយកនឹងភាគបែង គេបាន $$@F={L(quo)}{'+' if rem>0 else '-'}\\frac{{{L(abs(rem))}}}{{{L(den)}}}$$", f"ដោយ $\\lim_{{x\\to\\pm\\infty}}[@F-({L(quo)})]=0$ នោះបន្ទាត់ $y={L(quo)}$ ជាអាស៊ីមតូតទ្រេត ដែលមានមេគុណប្រាប់ទិស $1$ ។",
                     f"ដេរីវេ ៖ $$@D=1{'-' if rem>0 else '+'}\\frac{{{L(abs(rem))}}}{{({L(den)})^2}}$$", f"សមីការ $@n'(x)=1$ សមមូលនឹង $\\frac{{{L(abs(rem))}}}{{({L(den)})^2}}=0$ ដែលគ្មានឫសទេ ។", f"ដូចនេះ អាស៊ីមតូតទ្រេតគឺ $\\boxed{{y={L(quo)}}}$ ហើយគ្មានបន្ទាត់ប៉ះណាស្របនឹងវាទេ ។"])
    pr = intro(F.tex) + " " + ch(["រកអាស៊ីមតូតទ្រេតនៃ $@C$ រួចបង្ហាញថាគ្មានបន្ទាត់ប៉ះណាស្របនឹងអាស៊ីមតូតនោះទេ ។", "តើ $@C$ មានបន្ទាត់ប៉ះស្របនឹងអាស៊ីមតូតទ្រេតរបស់វាឬទេ ? ចូរពន្យល់ ។"])
    return add("no_such_tangent", "hard", pr, sol, f"y={L(quo)}", [ck_d(F), check(f"limit(({s(F.e)})-({s(quo)}),x,oo)", "0", "slant asymptote"), check(f"limit(diff({s(F.e)},x),x,oo)", "1", "slope tends to 1")], F.e, nm=nm_noy())

# ---------- full study ----------
def s_study():
    t = ch(["c3", "c3", "hom", "q21"])
    def num_str(v): return L(v)
    if t == "c3":
        p, q = sorted(rng.sample(range(-3, 4), 2)); a = ch([1, 1, -1, R(1, 3), 2, -2]); c = rng.randint(-3, 4)
        if (3 * a * (p + q)) % 2 != 0: a = a * 2
        e = sp.expand(a * (x**3 - R(3, 2) * (p + q) * x**2 + 3 * p * q * x) + c); F = poly_fn(e); fp, fq = e.subs(x, p), e.subs(x, q)
        if not fresh(e): return False
        A = a > 0
        cols = ["-\\infty", L(p), L(q), "+\\infty"]
        tab = variation_table(cols, ["", "+", "0", "-", "0", "+", ""] if A else ["", "-", "0", "+", "0", "-", ""],
                              ["-\\infty", "\\nearrow", L(fp), "\\searrow", L(fq), "\\nearrow", "+\\infty"] if A else ["+\\infty", "\\searrow", L(fp), "\\nearrow", L(fq), "\\searrow", "-\\infty"], name="@n")
        x0 = ch([v for v in range(-3, 4) if v not in (p, q)]); mx, mn = ((p, fp), (q, fq)) if A else ((q, fq), (p, fp))
        fac = f"{L(3*a) if abs(3*a)!=1 else ('-' if 3*a<0 else '')}({xm(p)})({xm(q)})"
        body = [f"ទិសដៅអថេរភាព ៖ {F.ds} គេអាចសរសេរ $@D={fac}$ ។", f"$@n'(x)=0$ មានឫស $x_1={L(p)}$ និង $x_2={L(q)}$ ។ សញ្ញានៃ $@n'(x)$ ដូចសញ្ញាមេគុណ ${L(3*a)}$ នៅក្រៅឫស ។",
                f"អនុគមន៍មានអតិបរមាស្មើនឹង ${L(mx[1])}$ ត្រង់ $x={L(mx[0])}$ ហើយមានអប្បបរមាស្មើនឹង ${L(mn[1])}$ ត្រង់ $x={L(mn[0])}$ ។",
                f"លីមីត ៖ $\\lim_{{x\\to-\\infty}}@F={'-' if A else '+'}\\infty$ និង $\\lim_{{x\\to+\\infty}}@F={'+' if A else '-'}\\infty$ ។"]
        chk = [ck_d(F), ck_m(F, p, 0), ck_m(F, q, 0), ck_y(F, p, fp), ck_y(F, q, fq), check(f"limit({s(e)},x,oo)", "oo" if A else "-oo", "limit")]
    elif t == "hom":
        h = rng.randint(-3, 3); k = rng.randint(-3, 3); r = ch([1, 2, 3, 4, 6, -1, -2, -3, -4]); den = x - h; num = sp.expand(k * den + r); e = num / den; d = -r / den**2
        if h == 0 or k == 0 or not fresh(e): return False
        F = Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), h), ch(RQUOT) + f" $$@D=\\frac{{{Lq(k)}({L(den)})-({L(num)})}}{{({L(den)})^2}}=\\frac{{{L(-r)}}}{{({L(den)})^2}}$$", d, [], "hom", vas=[h])
        inc = r < 0; sg = "+" if inc else "-"; ar = "\\nearrow" if inc else "\\searrow"
        mid = ("+\\infty\\|-\\infty" if inc else "-\\infty\\|+\\infty")
        tab = variation_table(["-\\infty", L(h), "+\\infty"], ["", sg, "\\|", sg, ""], [L(k), ar, mid, ar, L(k)], name="@n")
        x0 = ch([h + v for v in (-2, -1, 1, 2)])
        body = [f"ទិសដៅអថេរភាព ៖ {F.ds} ដោយ $({L(den)})^2>0$ ជានិច្ច សញ្ញានៃ $@n'(x)$ យកតាមសញ្ញានៃ ${L(-r)}$ ដូច្នេះ $@n$ ជាអនុគមន៍{'កើន' if inc else 'ចុះ'} លើចន្លោះនីមួយៗនៃ $D$ ។",
                f"លីមីតនិងអាស៊ីមតូត ៖ $\\lim_{{x\\to\\pm\\infty}}@F={L(k)}$ ដូច្នេះ $y={L(k)}$ ជាអាស៊ីមតូតដេក ។ $\\lim_{{x\\to {L(h)}^-}}@F={'+' if inc else '-'}\\infty$ និង $\\lim_{{x\\to {L(h)}^+}}@F={'-' if inc else '+'}\\infty$ ដូច្នេះ $x={L(h)}$ ជាអាស៊ីមតូតឈរ ។"]
        chk = [ck_d(F), check(f"limit({s(e)},x,oo)", s(k), "horizontal asymptote")]
    else:
        h = rng.randint(-3, 3); w = ch([1, 2, 3]); k = rng.randint(-3, 3); den = x - h; r = w * w; e = x + k + r / den; num = sp.expand((x + k) * den + r)
        if h == 0 or not fresh(e): return False
        dn = sp.expand(den**2 - r); d = dn / den**2
        F = Fn(e, f"\\frac{{{L(num)}}}{{{L(den)}}}", dom_ex(L(den), h), f"គេសរសេរជារាង $@F={L(x+k)}+\\frac{{{r}}}{{{L(den)}}}$ ។ យើងបាន $$@D=1-\\frac{{{r}}}{{({L(den)})^2}}=\\frac{{({xm(h-w)})({xm(h+w)})}}{{({L(den)})^2}}$$", d, [], "q21", vas=[h])
        p, q = h - w, h + w; fp, fq = e.subs(x, p), e.subs(x, q)
        tab = variation_table(["-\\infty", L(p), L(h), L(q), "+\\infty"], ["", "+", "0", "-", "\\|", "-", "0", "+", ""], ["-\\infty", "\\nearrow", L(fp), "\\searrow", "-\\infty\\|+\\infty", "\\searrow", L(fq), "\\nearrow", "+\\infty"], name="@n")
        x0 = ch([h + v for v in (-3 * w, -1 if w > 1 else -2, 1 if w > 1 else 2, 2 * w) if h + v != h])
        body = [f"ទិសដៅអថេរភាព ៖ {F.ds} ដោយភាគបែងវិជ្ជមាន សញ្ញានៃ $@n'(x)$ យកតាមសញ្ញានៃភាគយក ។ $@n'(x)=0$ មានឫស $x_1={L(p)}$ និង $x_2={L(q)}$ ។",
                f"អនុគមន៍មានអតិបរមាស្មើនឹង ${L(fp)}$ ត្រង់ $x={L(p)}$ ហើយមានអប្បបរមាស្មើនឹង ${L(fq)}$ ត្រង់ $x={L(q)}$ ។",
                f"លីមីតនិងអាស៊ីមតូត ៖ $\\lim_{{x\\to {L(h)}^-}}@F=-\\infty$ និង $\\lim_{{x\\to {L(h)}^+}}@F=+\\infty$ ដូច្នេះ $x={L(h)}$ ជាអាស៊ីមតូតឈរ ។ ដោយ $\\lim_{{x\\to\\pm\\infty}}[@F-({L(x+k)})]=0$ បន្ទាត់ $y={L(x+k)}$ ជាអាស៊ីមតូតទ្រេត ។"]
        chk = [ck_d(F), ck_m(F, p, 0), ck_m(F, q, 0), ck_y(F, p, fp), ck_y(F, q, fq), check(f"limit(({s(e)})-({s(x+k)}),x,oo)", "0", "slant asymptote")]
    b, mm = yv(F, x0), mv(F, x0); c = sp.expand(b - mm * x0); T = mm * x + c; tex = lin(mm, c)
    tan_ = f"បន្ទាត់ប៉ះត្រង់ $x={L(x0)}$ ៖ $@n({L(x0)})={L(b)}$ និង $@n'({L(x0)})={L(mm)}$ ។ គេបាន $${ym(b)}={mul(mm,x0)}\\iff {tex}$$" if mm != 0 else f"បន្ទាត់ប៉ះត្រង់ $x={L(x0)}$ គឺ ${tex}$ ។"
    sol = "\n".join([f"១. ដែនកំណត់ ៖ {F.dom}"] + body + ["តារាងអថេរភាព ៖ $$" + tab + "$$", f"២. {tan_}", "៣. សំណង់ក្រាប ៖ គេគូសខ្សែកោង និងបន្ទាត់ប៉ះតាមតារាងអថេរភាព (មើលក្រាបខាងក្រោម) ។", f"ដូចនេះ សមីការបន្ទាត់ប៉ះគឺ $\\boxed{{{tex}}}$ ។"])
    pr = intro(F.tex) + f"\n១. សិក្សាអថេរភាព និងសង់តារាងអថេរភាពនៃ $@n$ ។\n២. រកសមីការបន្ទាត់ប៉ះ $(T)$ នៃ $@C$ ត្រង់ចំណុចអាប់ស៊ីស ${L(x0)}$ ។\n៣. សង់ $@C$ និង $(T)$ ក្នុងតម្រុយតែមួយ ។"
    chk.append(ck_T(F, x0, T))
    dgm = [{"type": "variation_table", "latex": tab, "alt_km": "តារាងអថេរភាពនៃអនុគមន៍ ។", "image": None}, gdiag(F, [T], [(x0, b)], "ក្រាបនៃ $@C$ និងបន្ទាត់ប៉ះ $(T)$ ។", .55)]
    return add("study_with_tangent", "bacii", pr, sol, tex, chk, F.e, nm=nm_noy(), diagrams=dgm)

PLAN = [(s_abscissa, 230), (s_point, 90), (s_normal, 120), (s_slope, 110), (s_parallel, 110), (s_perp, 70), (s_horizontal, 50), (s_outside, 110), (s_angle, 40), (s_limit, 60), (s_read, 50),
        (s_approx, 30), (s_axes, 70), (s_params, 60), (s_double, 50), (s_common, 30), (s_position, 40), (s_second, 40), (s_inflect, 40), (s_area, 40), (s_pair, 40), (s_none, 30), (s_study, 90)]
def main():
    from collections import Counter
    import traceback
    errs = Counter()
    for fn, n in PLAN:
        got = tries = 0
        while got < n and tries < n * 30:
            tries += 1
            try:
                got += bool(fn())
            except Exception as ex:
                errs[fn.__name__ + ":" + type(ex).__name__ + ":" + str(ex)[:60]] += 1
        print(fn.__name__, got, tries)
    print(errs.most_common(12))
    try:
        from tangent_hand import hand_rows
        hr = hand_rows(make_row, check, gdiag, Fn, poly_fn, tok, rid, sp, x); rows.extend(hr); print("hand", len(hr))
    except ImportError as ex:
        print("no hand rows", ex)
    ids = set(); out = []
    for r in rows:
        if r["id"] not in ids:
            ids.add(r["id"]); out.append(r)
    write_jsonl(out, "tangent.jsonl")
    print("png left", png_left)
if __name__ == "__main__":
    main()
