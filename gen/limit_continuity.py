"""Topic limit_continuity (chapter limit): continuity at a point and on an interval, piecewise functions,
parameters, extension by continuity, intermediate value theorem, asymptotes from limits, reading graphs.
Hand rows live in limit_continuity_hand.py. All statements are checked by SymPy strings in lib/verify.py."""
import sys, os, re, glob, random, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from common import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from limit_tex import clean_tex, finish_rows, PLAIN_LIMIT
R = sp.Rational
TOPIC = "limit_continuity"
PNG_CAP = 290
state = {"png": 0}
for _f in glob.glob(os.path.join(ROOT, "diagrams", TOPIC + "-*.png")):
    os.remove(_f)

# ---------- small text helpers ----------
def L(e):
    if isinstance(e, str): return e
    e = sp.sympify(e)
    if e == sp.oo: return "+\\infty"
    return sp.latex(e, ln_notation=True)
def I(s): return "$" + L(s) + "$"
def D(s): return "$$" + L(s) + "$$"
def fr(a, b): return "\\frac{" + L(a) + "}{" + L(b) + "}"
def W(rng, *o): return rng.choice(o)
def lim(c, side=""):
    if c in ("+oo", sp.oo): t = "+\\infty"
    elif c in ("-oo", -sp.oo): t = "-\\infty"
    else: t = L(c)
    if side: t = t + "^{" + side + "}"
    return "\\lim_{x\\to " + t + "}"
def cs(s):
    return str(s)
def cl(e, c, side=""):
    return f"limit({e},x,{c}" + (f",'{side}')" if side else ")")
def cases(n, rows):
    body = " \\\\ ".join(L(a) + ", & " + b for a, b in rows)
    return f"{n}(x)=\\begin{{cases}} {body} \\end{{cases}}"
def chain(start, steps, val=None):
    """start, then each step on its own line."""
    parts = list(steps) + ([L(val)] if val is not None else [])
    if len(parts) <= 1:
        return D(start + " = " + parts[0])
    return "$$\\begin{aligned} " + start + " &= " + " \\\\ &= ".join(parts) + " \\end{aligned}$$"
def fname(rng): return rng.choice("fffffgh")
ZZ = "\\frac{0}{0}"
LAB = ["(រាងមិនកំណត់ $" + ZZ + "$)", "(មានរាងមិនកំណត់ $" + ZZ + "$)"]
PARTS = {"k": "កខគឃងច", "n": "១២៣៤៥៦"}
def fixtex(t):
    t = re.sub(r"(?<!\\)(\\[a-zA-Z]+)(\d)", r"\1 \2", t)
    t = t.replace("- \\frac", "-\\frac").replace("- x", "-x") if False else t.replace("- \\frac", "-\\frac")
    t = re.sub(r"(\\lim_\{(?:[^{}]|\{[^{}]*\})*\})\\left\((\d+)\\right\)", r"\1 \2", t)
    t = re.sub(r"\\(ln|sin|cos|tan)\{\\left\(([a-zA-Z0-9]+) \\right\)\}", r"\\\1 \2", t)
    t = re.sub(r"\\(ln|sin|cos|tan)\{\\left\(((?:(?!\\right).)*?) \\right\)\}", r"\\\1\\left(\2\\right)", t)
    t = re.sub(r"[ \t]*\n*\$\$(.+?)\$\$\n*[ \t]*", lambda m: "\n$$" + m.group(1) + "$$\n", t, flags=re.S)
    t = re.sub(r"(?<![a-zA-Z])\\left\(x\\right\)", "x", t).replace("(x-0)", "x")
    t = re.sub(r"\n{2,}", "\n", t).strip()
    return t

class P:  # one row or one part of a row
    def __init__(s, q, sol, ans, checks, fig=None, tables=None):
        s.q, s.sol, s.ans, s.checks, s.fig, s.tables = q, sol, ans, checks, fig, tables or []

# ---------- pieces with an indeterminate form ----------
class Piece: pass
def ind(rng, c, kinds=None):
    """A 0/0 expression at x=c, with the write-up steps. val is exact."""
    base = ["quad", "rr", "rn", "rd"] + (["dos", "cub"] if c != 0 else [])
    tr = ["sin", "tan", "cos", "exp", "ln", "sin", "cos"] if c == 0 else ["ssin"]
    pool = kinds or (base + tr)
    k = rng.choice(pool); p = Piece(); p.kind = k; p.why = ""
    d = x - c
    if k == "quad":
        b = rng.choice([v for v in range(-5, 6) if v not in (-c, 0)]); s = rng.choice([1, 1, 2])
        num = sp.expand(s * d * (x + b)); fac = (L(s) if s != 1 else "") + "\\left(" + L(d) + "\\right)\\left(" + L(x + b) + "\\right)"
        if c == 0: fac = (L(s) if s != 1 else "") + "x\\left(" + L(x + b) + "\\right)"
        p.e = num / d; p.t = fr(num, d); p.steps = [fr(fac, d), "\\left(" + L(s * (x + b)) + "\\right)"]; p.val = s * (c + b)
        p.why = W(rng, "ដាក់ភាគយកជាកត្តា", "ភាគយកមានឫស " + I(c) + " ដូច្នេះដាក់ជាកត្តាបាន", "បំបែកភាគយកជាកត្តា")
    elif k == "dos":
        num = x**2 - c**2
        p.e = num / d; p.t = fr(num, d); p.steps = [fr("\\left(" + L(d) + "\\right)\\left(" + L(x + c) + "\\right)", d), "\\left(" + L(x + c) + "\\right)"]; p.val = 2 * c
        p.why = "ភាគយកជាផលដកការេ"
    elif k == "cub":
        num = x**3 - c**3; q = x**2 + c * x + c**2
        p.e = num / d; p.t = fr(num, d); p.steps = [fr("\\left(" + L(d) + "\\right)\\left(" + L(q) + "\\right)", d), "\\left(" + L(q) + "\\right)"]; p.val = 3 * c * c
        p.why = "ប្រើរូបមន្តផលដកគូប"
    elif k == "rr":
        b = rng.choice([v for v in range(-5, 6) if v not in (-c, 0)]); e_ = rng.choice([v for v in range(-5, 6) if v not in (-c, b, 0)])
        n_ = sp.expand(d * (x + b)); m_ = sp.expand(d * (x + e_))
        fa = "x" if c == 0 else "\\left(" + L(d) + "\\right)"
        p.e = n_ / m_; p.t = fr(n_, m_)
        p.steps = [fr(fa + "\\left(" + L(x + b) + "\\right)", fa + "\\left(" + L(x + e_) + "\\right)"), fr(x + b, x + e_)]; p.val = R(c + b, c + e_); p.other = -e_
        p.why = "ដាក់ភាគយក និងភាគបែងជាកត្តា"
    elif k == "rn":
        r = rng.choice([1, 2, 3, 4]); kk = rng.choice([1, 1, 2, 3]); a = r * r - kk * c
        u = kk * x + a; sq = sp.sqrt(u); num = sq - r
        p.e = num / d; p.t = fr(num, d)
        st2 = fr(L(kk) + "\\left(" + L(d) + "\\right)" if kk != 1 else L(d), "\\left(" + L(d) + "\\right)\\left(" + L(sq + r) + "\\right)")
        p.steps = [fr("\\left(" + L(sq - r) + "\\right)\\left(" + L(sq + r) + "\\right)", "\\left(" + L(d) + "\\right)\\left(" + L(sq + r) + "\\right)"), st2, fr(kk, sq + r)]
        p.val = R(kk, 2 * r); p.why = W(rng, "គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់នៃភាគយក", "គុណនឹងកន្សោមឆ្លាស់ " + I(sq + r))
    elif k == "rd":
        r = rng.choice([1, 2, 3]); a = r * r - c; sq = sp.sqrt(x + a)
        p.e = d / (sq - r); p.t = fr(d, sq - r)
        p.steps = [fr("\\left(" + L(d) + "\\right)\\left(" + L(sq + r) + "\\right)", "\\left(" + L(sq - r) + "\\right)\\left(" + L(sq + r) + "\\right)"), fr("\\left(" + L(d) + "\\right)\\left(" + L(sq + r) + "\\right)", d), "\\left(" + L(sq + r) + "\\right)"]
        p.val = 2 * r; p.why = "គុណនឹងកន្សោមឆ្លាស់នៃភាគបែង"
    elif k in ("sin", "tan"):
        a = rng.choice([2, 3, 4, 5, 6]); mm = rng.choice([1, 1, 2, 3]);
        while a == mm: mm = rng.choice([1, 2, 3])
        F = sp.sin if k == "sin" else sp.tan; nm = "\\sin" if k == "sin" else "\\tan"
        p.e = F(a * x) / (mm * x); p.t = fr(nm + " " + L(a) + "x", (L(mm) if mm != 1 else "") + "x")
        p.steps = [(fr(a, mm) if mm != 1 else L(a)) + "\\cdot" + fr(nm + " " + L(a) + "x", L(a) + "x")]; p.val = R(a, mm)
        p.why = "តាមរូបមន្ត $" + lim("u", "").replace("x\\to u", "u\\to 0") + fr(nm + " u", "u") + "=1$"
    elif k == "cos":
        a = rng.choice([2, 4, 6])
        p.e = (1 - sp.cos(a * x)) / x**2; p.t = fr("1-\\cos " + L(a) + "x", "x^{2}")
        h = a // 2; hx = (L(h) if h != 1 else "") + "x"
        p.steps = [fr("2\\sin^{2} " + hx, "x^{2}"), (L(2 * h * h) if True else "") + "\\left(" + fr("\\sin " + hx, hx) + "\\right)^{2}"]
        p.val = R(a * a, 2); p.why = "ប្រើ $1-\\cos 2u=2\\sin^{2} u$"
    elif k == "exp":
        a = rng.choice([1, 2, 3, 4, 5]); ax_ = (L(a) if a != 1 else "") + "x"
        p.e = (sp.exp(a * x) - 1) / x; p.t = fr("e^{" + ax_ + "}-1", "x")
        p.steps = [L(a) + "\\cdot" + fr("e^{" + ax_ + "}-1", ax_)] ; p.val = sp.Integer(a)
        p.why = "តាមរូបមន្ត $\\lim_{u\\to 0}" + fr("e^{u}-1", "u") + "=1$"
    elif k == "ln":
        a = rng.choice([1, 2, 3, 4]); ax_ = (L(a) if a != 1 else "") + "x"
        p.e = sp.log(1 + a * x) / x; p.t = fr("\\ln\\left(1+" + ax_ + "\\right)", "x")
        p.steps = [L(a) + "\\cdot" + fr("\\ln\\left(1+" + ax_ + "\\right)", ax_)]; p.val = sp.Integer(a)
        p.why = "តាមរូបមន្ត $\\lim_{u\\to 0}" + fr("\\ln(1+u)", "u") + "=1$"
    elif k == "ssin":
        a = rng.choice([1, 2, 3, 4]); dd = L(d); ad = (L(a) if a != 1 else "") + "\\left(" + dd + "\\right)"
        p.e = sp.sin(a * d) / d; p.t = fr("\\sin " + ad, dd)
        p.steps = [L("") if False else (L(a) + "\\cdot" + fr("\\sin " + L(a) + "t", L(a) + "t") if a != 1 else fr("\\sin t", "t"))]
        p.val = sp.Integer(a); p.sub = True
        p.why = "តាង $t=" + dd + "$ បើ $x\\to " + L(c) + "$ នោះ $t\\to 0$"
    return p

def indchain(rng, p, c, side=""):
    """Write-up of the limit of piece p at c."""
    start = lim(c, side) + p.t
    pre = W(rng, "ជំនួស $x=" + L(c) + "$ ឃើញថាវា" + LAB[1][1:-1] + " ។ ", "កាលណា $x\\to " + L(c) + "$ កន្សោមនេះ" + LAB[1][1:-1] + " ។ ", "កន្សោមនេះ" + LAB[1][1:-1] + " ។ ", "ភាគយក និងភាគបែងខិតជិតសូន្យទាំងពីរ ។ ", "")
    why = p.why + " ៖" if p.why else ""
    if getattr(p, "sub", False):
        tl = "\\lim_{t\\to 0}"
        return pre + why + "\n" + chain(start, [tl + s for s in p.steps], p.val)
    steps = []
    for s_ in p.steps:
        steps.append(lim(c, side) + s_)
    return pre + why + "\n" + chain(start, steps, p.val)

def simple(rng, c, kinds=("lin", "lin", "quad", "const", "root")):
    k = rng.choice(kinds); p = Piece(); p.kind = k
    if k == "lin":
        a = rng.choice([-3, -2, -1, 1, 2, 3, 4]); b = rng.randint(-5, 6); p.e = a * x + b
    elif k == "quad":
        p.e = rng.choice([1, 1, -1, 2]) * x**2 + rng.randint(-3, 3) * x + rng.randint(-4, 4)
    elif k == "const":
        p.e = sp.Integer(rng.choice([-3, -2, -1, 1, 2, 3, 4, 5]))
    else:
        r = rng.choice([1, 2, 3]); a = r * r - c; p.e = sp.sqrt(x + a) + rng.randint(-2, 2)
    p.val = p.e.subs(x, c); p.t = L(p.e)
    return p
def rel(c, s): return "x" + s + L(c)
LE, LT, GE, GT, NE = "\\le ", "<", "\\ge ", ">", "\\neq "

OPEN = ["គេឱ្យអនុគមន៍ {n} កំណត់ដោយ ៖", "គេមានអនុគមន៍ {n} កំណត់ដោយ ៖", "អនុគមន៍ {n} កំណត់លើ $\\mathbb{{R}}$ ដូចខាងក្រោម ៖",
        "ចំពោះចំនួនពិត $x$ គេកំណត់អនុគមន៍ {n} ដោយ ៖", "គេកំណត់អនុគមន៍ {n} ដូចតទៅ ៖", "គេឱ្យ ៖"]
def opening(rng, n, on_R=True):
    t = rng.choice(OPEN)
    if not on_R and ("mathbb" in t or "ចំនួនពិត" in t): t = OPEN[0]
    return t.format(n="$" + n + "$")
def good(rng, n, c):
    return W(rng, f"ដូចនេះ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។", f"ដូចនេះ អនុគមន៍ ${n}$ ជាអនុគមន៍ជាប់ត្រង់ $x={L(c)}$ ។",
             f"សន្និដ្ឋាន ៖ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។")
def bad(rng, n, c):
    return W(rng, f"ដូចនេះ ${n}$ មិនជាប់ត្រង់ $x={L(c)}$ ទេ ។", f"ដូចនេះ អនុគមន៍ ${n}$ ដាច់ត្រង់ $x={L(c)}$ ។",
             f"សន្និដ្ឋាន ៖ ${n}$ មិនជាប់ត្រង់ $x={L(c)}$ ទេ ។")
def qcont(rng, n, c):
    return W(rng, f"សិក្សាភាពជាប់នៃអនុគមន៍ ${n}$ ត្រង់ $x={L(c)}$ ។", f"តើ ${n}$ ជាអនុគមន៍ជាប់ត្រង់ $x={L(c)}$ ឬទេ ?",
             f"សិក្សាភាពជាប់ត្រង់ $x={L(c)}$ ។", f"ចូរពិនិត្យមើលថា ${n}$ ជាប់ត្រង់ $x={L(c)}$ ឬមិនជាប់ ។",
             f"តើអនុគមន៍នេះជាប់ត្រង់ចំណុច $x={L(c)}$ ឬទេ ? ពន្យល់ ។")
HEAD = lambda c: f"សិក្សាភាពជាប់ត្រង់ $x={L(c)}$ ៖\n"
def on_R(prob):
    """True if the question is about all of R and not one point."""
    return "ជាប់លើ $\\mathbb{R}$" in prob or "ជាប់គ្រប់តម្លៃ" in prob
def pieces_ok(n, c):
    return f"ផ្នែកនីមួយៗនៃ ${n}$ ជាអនុគមន៍ជាប់លើចន្លោះរបស់វា ដូច្នេះ ${n}$ ជាប់ចំពោះគ្រប់ $x\\neq {L(c)}$ ។ យើងនៅត្រូវសិក្សាតែត្រង់ $x={L(c)}$ ។\n"
def solve_eq(lhs, rhs, pv, val):
    """lhs=rhs, then the solved form unless lhs is already the parameter alone."""
    return f"{lhs}={rhs}" if lhs.strip() == pv else f"{lhs}={rhs}\\Leftrightarrow {pv}={val}"

# ---------- A. continuity at a point ----------
def g_removable(rng):
    c = rng.choice([-3, -2, -1, 0, 0, 0, 1, 2, 3, 4]); p = ind(rng, c); n = fname(rng)
    eq = rng.random() < .62
    v = p.val if eq else p.val + rng.choice([-2, -1, 1, 2, 3])
    fx = cases(n, [(p.t, "x" + NE + L(c)), (v, f"x={L(c)}")])
    prob = opening(rng, n) + "\n" + D(fx) + qcont(rng, n, c)
    limtxt = indchain(rng, p, c)
    val = W(rng, f"តាមការកំណត់ ${n}({L(c)})={L(v)}$ ។", f"យើងមាន ${n}({L(c)})={L(v)}$ ដូច្នេះ ${n}$ កំណត់ត្រង់ $x={L(c)}$ ។", f"តម្លៃនៃអនុគមន៍ត្រង់ចំណុចនេះគឺ ${n}({L(c)})={L(v)}$ ។")
    if eq:
        end = W(rng, f"យើងឃើញថា ${lim(c)}{n}(x)={n}({L(c)})={L(v)}$ ។\n", f"លីមីតស្មើនឹងតម្លៃនៃអនុគមន៍ត្រង់ $x={L(c)}$ ។\n") + good(rng, n, c)
    else:
        end = W(rng, f"យើងឃើញថា ${lim(c)}{n}(x)={L(p.val)}\\neq {L(v)}={n}({L(c)})$ ។\n", f"លីមីតមានមែន ប៉ុន្តែមិនស្មើនឹង ${n}({L(c)})$ ទេ ។\n") + bad(rng, n, c)
    order = rng.random() < .6
    sol = HEAD(c) + (val + "\n" + limtxt if order else limtxt + "\n" + val) + "\n" + end
    ans = (f"{n}\\ \\text{{ជាប់ត្រង់}}\\ x={L(c)}" if eq else f"{n}\\ \\text{{មិនជាប់ត្រង់}}\\ x={L(c)}")
    return P(prob, sol, ans, [check(cl(p.e, c), p.val, "limit"), check(cl(p.e, c, "-"), p.val, "left")])

def g_join_polys(rng):
    c = rng.randint(-3, 4); n = fname(rng); a = simple(rng, c); b = simple(rng, c)
    cont = rng.random() < .55
    if cont: b.e = b.e - b.val + a.val; b.val = a.val; b.t = L(b.e)
    elif a.val == b.val: b.e = b.e + rng.choice([1, 2, -1]); b.val = b.e.subs(x, c); b.t = L(b.e)
    leftclosed = rng.random() < .6
    fx = cases(n, [(a.t, "x" + (LE if leftclosed else LT) + L(c)), (b.t, "x" + (GT if leftclosed else GE) + L(c))])
    fc = a.val if leftclosed else b.val
    prob = opening(rng, n) + "\n" + D(fx) + qcont(rng, n, c)
    l1 = D(f"{lim(c,'-')}{n}(x)={lim(c,'-')}\\left({a.t}\\right)={L(a.val)}")
    l2 = D(f"{lim(c,'+')}{n}(x)={lim(c,'+')}\\left({b.t}\\right)={L(b.val)}")
    fv = f"${n}({L(c)})={L(fc)}$ ។"
    if rng.random() < .5:
        body = W(rng, "តម្លៃត្រង់ចំណុចនេះ ៖ ", "យើងមាន ") + fv + "\n" + W(rng, "លីមីតឆ្វេង ៖", "គណនាលីមីតឆ្វេង ៖") + l1 + W(rng, "លីមីតស្តាំ ៖", "ហើយលីមីតស្តាំ ៖") + l2
    else:
        body = "ដោយរូបមន្តខុសគ្នាសងខាង $x=" + L(c) + "$ យើងគណនាលីមីតម្ខាងៗ ៖" + l1 + l2 + "ម្យ៉ាងទៀត " + fv
    if cont:
        end = f"យើងឃើញថា ${lim(c,'-')}{n}(x)={lim(c,'+')}{n}(x)={n}({L(c)})={L(fc)}$ ។\n" + good(rng, n, c)
    else:
        end = W(rng, f"យើងឃើញថា លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ $({L(a.val)}\\neq {L(b.val)})$ ដូច្នេះ ${n}$ គ្មានលីមីតត្រង់ $x={L(c)}$ ទេ ។\n", f"លីមីតទាំងពីរខុសគ្នា នាំឱ្យគ្មានលីមីតត្រង់ $x={L(c)}$ ។\n") + bad(rng, n, c)
    ans = (f"{n}\\ \\text{{ជាប់ត្រង់}}\\ x={L(c)}" if cont else f"{n}\\ \\text{{មិនជាប់ត្រង់}}\\ x={L(c)}")
    fig = None
    if rng.random() < .22 and a.kind != "root" and b.kind != "root":
        sp_ = [(a.e, c - 4, c), (b.e, c, c + 4)]
        y0, y1 = a.val, b.val
        fig = dict(pieces=sp_, dots=[(c, fc)], holes=[] if cont else [(c, b.val if leftclosed else a.val)], where="s",
                   alt=f"ក្រាបនៃ ${n}$ សងខាង $x={L(c)}$ ។" + ("ក្រាបតភ្ជាប់គ្នា ។" if cont else "ក្រាបលោតត្រង់ចំណុចនេះ ។"), win=(c - 4, c + 4, min(y0, y1) - 5, max(y0, y1) + 5))
    return P(prob, HEAD(c) + body + "\n" + end, ans, [check(cl(a.e, c, "-"), a.val, "left"), check(cl(b.e, c, "+"), b.val, "right")], fig=fig)

def g_join_ind(rng):
    c = rng.choice([-2, -1, 0, 0, 0, 1, 2, 3]); n = fname(rng); p = ind(rng, c); q = simple(rng, c, ("lin", "lin", "quad", "const"))
    cont = rng.random() < .6
    if cont: q.e = q.e - q.val + p.val; q.val = p.val
    elif q.val == p.val: q.e = q.e + 1; q.val = q.val + 1
    q.t = L(q.e)
    swap = rng.random() < .5
    if swap: rows = [(p.t, "x" + LT + L(c)), (q.t, "x" + GE + L(c))]; sp_, sq = "-", "+"
    else: rows = [(q.t, "x" + LE + L(c)), (p.t, "x" + GT + L(c))]; sp_, sq = "+", "-"
    prob = opening(rng, n) + "\n" + D(cases(n, rows)) + qcont(rng, n, c)
    lp = indchain(rng, p, c, sp_); lq = D(f"{lim(c,sq)}{n}(x)={lim(c,sq)}\\left({q.t}\\right)={L(q.val)}")
    fc = f"យើងមាន ${n}({L(c)})={L(q.val)}$ ។\n"
    nm = {"-": "លីមីតឆ្វេង", "+": "លីមីតស្តាំ"}
    sol = HEAD(c) + fc + nm[sp_] + " ៖ " + lp + "\n" + nm[sq] + " ៖" + lq
    if cont: sol += f"យើងឃើញថា លីមីតឆ្វេង លីមីតស្តាំ និង ${n}({L(c)})$ ស្មើគ្នា គឺស្មើ ${L(p.val)}$ ។\n" + good(rng, n, c); ans = f"{n}\\ \\text{{ជាប់ត្រង់}}\\ x={L(c)}"
    else: sol += f"យើងឃើញថា លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ដូច្នេះ ${n}$ គ្មានលីមីតត្រង់ $x={L(c)}$ ទេ ។\n" + bad(rng, n, c); ans = f"{n}\\ \\text{{មិនជាប់ត្រង់}}\\ x={L(c)}"
    return P(prob, sol, ans, [check(cl(p.e, c, sp_), p.val, "indeterminate side"), check(cl(q.e, c, sq), q.val, "other side")])

def g_abs(rng):
    c = rng.randint(-3, 4); k = rng.choice([1, 2, 3]); n = fname(rng); mode = rng.choice(["ratio", "ratio", "absfun", "sq"])
    d = x - c; dt = L(d)
    if mode == "ratio":
        b = rng.randint(-3, 3); v = rng.randint(-3, 3)
        e = k * sp.Abs(d) / d + b
        t = (L(k) if k != 1 else "") + fr("|" + dt + "|", dt) + ("" if b == 0 else ("+" if b > 0 else "") + L(b))
        prob = opening(rng, n) + "\n" + D(cases(n, [(t, "x" + NE + L(c)), (v, f"x={L(c)}")])) + qcont(rng, n, c)
        sol = HEAD(c) + f"ដោយសញ្ញានៃ ${dt}$ ផ្លាស់ប្តូរត្រង់ $x={L(c)}$ យើងសរសេរតម្លៃដាច់ខាតជាពីរករណី ៖\n"
        sol += f"ចំពោះ $x>{L(c)}$ គេបាន $|{dt}|={dt}$ ដូច្នេះ ${n}(x)={L(k + b)}$ ហើយ ${lim(c,'+')}{n}(x)={L(k + b)}$ ។\n"
        sol += f"ចំពោះ $x<{L(c)}$ គេបាន $|{dt}|=-\\left({dt}\\right)$ ដូច្នេះ ${n}(x)={L(b - k)}$ ហើយ ${lim(c,'-')}{n}(x)={L(b - k)}$ ។\n"
        sol += "លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ នាំឱ្យគ្មានលីមីតត្រង់ចំណុចនេះទេ ។\n" + bad(rng, n, c)
        return P(prob, sol, f"{n}\\ \\text{{មិនជាប់ត្រង់}}\\ x={L(c)}", [check(cl(e, c, "+"), k + b, "right"), check(cl(e, c, "-"), b - k, "left")])
    if mode == "absfun":
        b = rng.randint(-3, 3); e = k * sp.Abs(d) + b
        t = (L(k) if k != 1 else "") + "|" + dt + "|" + ("" if b == 0 else ("+" if b > 0 else "") + L(b))
        prob = f"គេឱ្យ ${n}(x)={t}$ ។ " + qcont(rng, n, c)
        sol = HEAD(c) + f"សរសេរ ${n}$ ដោយមិនប្រើតម្លៃដាច់ខាត ៖\n" + D(cases(n, [(k * d + b, "x" + GE + L(c)), (-k * d + b, "x<" + L(c))])) + f"គេបាន ${n}({L(c)})={L(b)}$ ។\n"
        sol += D(f"{lim(c,'-')}{n}(x)={lim(c,'-')}\\left({L(-k*d+b)}\\right)={L(b)}") + D(f"{lim(c,'+')}{n}(x)={lim(c,'+')}\\left({L(k*d+b)}\\right)={L(b)}")
        sol += "លីមីតទាំងពីរស្មើគ្នា ហើយស្មើនឹងតម្លៃនៃអនុគមន៍ត្រង់ចំណុចនោះ ។\n" + good(rng, n, c)
        return P(prob, sol, f"{n}\\ \\text{{ជាប់ត្រង់}}\\ x={L(c)}", [check(cl(e, c, "+"), b, "right"), check(cl(e, c, "-"), b, "left"), check(f"subs({e},x,{c})", b, "value")])
    a = rng.choice([v for v in range(1, 5)]);
    e = sp.Abs(x**2 - a * a) / (x - a)
    t = fr("|" + L(x**2 - a * a) + "|", L(x - a)); v = 2 * a
    prob = opening(rng, n) + "\n" + D(cases(n, [(t, "x" + NE + L(a)), (v, f"x={L(a)}")])) + qcont(rng, n, a)
    sol = HEAD(a) + f"សម្រាប់ $x$ ជិត ${L(a)}$ យើងមាន $x+{L(a)}>0$ ដូច្នេះសញ្ញានៃ ${L(x**2-a*a)}$ គឺសញ្ញានៃ ${L(x-a)}$ ។\n"
    sol += D(f"{lim(a,'+')}{n}(x)={lim(a,'+')}{fr(L((x-a)*(x+a)),L(x-a))}={lim(a,'+')}\\left({L(x+a)}\\right)={L(2*a)}")
    sol += D(f"{lim(a,'-')}{n}(x)={lim(a,'-')}{fr('-'+L((x-a)*(x+a)),L(x-a))}={lim(a,'-')}\\left(-x-{L(a)}\\right)={L(-2*a)}")
    sol += f"ទោះជា ${n}({L(a)})={L(v)}$ ស្មើលីមីតស្តាំក៏ដោយ លីមីតឆ្វេងមិនស្មើលីមីតស្តាំទេ ។\n" + bad(rng, n, a)
    return P(prob, sol, f"{n}\\ \\text{{មិនជាប់ត្រង់}}\\ x={L(a)}", [check(cl(e, a, "+"), 2 * a, "right"), check(cl(e, a, "-"), -2 * a, "left")])

def g_undefined(rng):
    c = rng.randint(-3, 4); n = fname(rng); mode = rng.choice(["pole", "hole", "pole2"])
    if mode == "hole":
        p = ind(rng, c, ["quad", "rr", "rn"] + ([] if c == 0 else ["dos"]))
        prob = W(rng, f"គេឱ្យអនុគមន៍ ${n}(x)={p.t}$ ។ ", f"គេមាន ${n}(x)={p.t}$ ។ ") + W(rng, f"តើ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ឬទេ ? បើមានលីមីតត្រង់ចំណុចនោះ ចូរគណនា ។", f"គណនា ${lim(c)}{n}(x)$ រួចសិក្សាភាពជាប់ត្រង់ $x={L(c)}$ ។")
        sol = indchain(rng, p, c) + f"\nលីមីតមានតម្លៃ ${L(p.val)}$ ប៉ុន្តែភាគបែងស្មើសូន្យត្រង់ $x={L(c)}$ ដូច្នេះ ${n}({L(c)})$ មិនកំណត់ ។ លក្ខខណ្ឌទីមួយនៃភាពជាប់មិនផ្ទៀងផ្ទាត់ទេ ។\n" + bad(rng, n, c)
        return P(prob, sol, f"{lim(c)}{n}(x)={L(p.val)},\\ {n}\\ \\text{{មិនជាប់ត្រង់}}\\ x={L(c)}", [check(cl(p.e, c), p.val, "limit")])
    k = rng.choice([1, 2, 3, -1, -2]); pw = 1 if mode == "pole" else 2; e = k / (x - c)**pw
    t = fr(k, (x - c)**pw)
    prob = f"គេឱ្យអនុគមន៍ ${n}(x)={t}$ ។ " + W(rng, f"គណនាលីមីតឆ្វេង និងលីមីតស្តាំត្រង់ $x={L(c)}$ រួចសន្និដ្ឋានអំពីភាពជាប់ ។", f"សិក្សាលីមីតនៃ ${n}$ ត្រង់ ${L(c)}$ រួចប្រាប់ថា ${n}$ ជាប់ឬមិនជាប់ត្រង់ចំណុចនេះ ។")
    sl = sp.oo * sp.sign(k) if pw == 2 else -sp.oo * sp.sign(k); sr = sp.oo * sp.sign(k)
    sol = f"ភាគបែងស្មើសូន្យត្រង់ $x={L(c)}$ ដូច្នេះ ${n}({L(c)})$ មិនកំណត់ ។\n"
    d0m = "0^{+}" if pw == 2 else "0^{-}"
    sol += D(f"{lim(c,'-')}{n}(x)={lim(c,'-')}{t}={L(sl)}") + f"ព្រោះភាគយកស្មើ ${L(k)}$ ហើយភាគបែងខិតជិត ${d0m}$ ។\n"
    sol += D(f"{lim(c,'+')}{n}(x)={lim(c,'+')}{t}={L(sr)}") + f"ព្រោះភាគបែងខិតជិត $0^{{+}}$ ។\n" + bad(rng, n, c)
    return P(prob, sol, f"{lim(c,'-')}{n}(x)={L(sl)},\\ {lim(c,'+')}{n}(x)={L(sr)}", [check(cl(e, c, "-"), sl, "left"), check(cl(e, c, "+"), sr, "right")])

def g_three_cond(rng):
    n = fname(rng); mode = rng.choice(["rat", "root", "ln", "trig"])
    if mode == "rat":
        c = rng.randint(-3, 4); a = rng.choice([v for v in range(-4, 5) if v != c]); P_ = x**2 + rng.randint(-3, 3) * x + rng.randint(-3, 3); e = P_ / (x - a); t = fr(P_, x - a); nm = "ផលចែកនៃពហុធាពីរ"
    elif mode == "root":
        r = rng.choice([1, 2, 3, 4]); c = rng.randint(-3, 3); a = r * r - c * 2; e = sp.sqrt(2 * x + a); t = L(e); nm = "អនុគមន៍ឫសការេ"
    elif mode == "ln":
        c = rng.randint(1, 5); a = rng.randint(-2, 2); e = sp.log(x + 1 - c) + a * x; t = L(e); nm = "ផលបូកនៃអនុគមន៍លោការីត និងពហុធា"
    else:
        c = sp.pi / rng.choice([2, 3, 4, 6]); e = sp.sin(x) + sp.cos(x); t = "\\sin x+\\cos x"; nm = "ផលបូកនៃអនុគមន៍ត្រីកោណមាត្រ"
    v = e.subs(x, c)
    prob = W(rng, f"ដោយផ្ទៀងផ្ទាត់លក្ខខណ្ឌទាំងបីនៃនិយមន័យ បង្ហាញថា ${n}(x)={t}$ ជាប់ត្រង់ $x={L(c)}$ ។", f"តើ ${n}(x)={t}$ ជាប់ត្រង់ $x={L(c)}$ ឬទេ ?", f"គេឱ្យ ${n}(x)={t}$ ។ សិក្សាភាពជាប់ត្រង់ $x={L(c)}$ ។")
    sol = f"លក្ខខណ្ឌទី១ ៖ ${n}$ កំណត់ត្រង់ $x={L(c)}$ ហើយ ${n}({L(c)})={L(v)}$ ។\n"
    sol += f"លក្ខខណ្ឌទី២ ៖ ${n}$ ជា{nm} ដូច្នេះលីមីតត្រង់ ${L(c)}$ មាន ហើយគណនាបានដោយជំនួសផ្ទាល់ ៖ ${lim(c)}{n}(x)={L(v)}$ ។\n"
    sol += f"លក្ខខណ្ឌទី៣ ៖ យើងឃើញថា ${lim(c)}{n}(x)={n}({L(c)})$ ។\n" + good(rng, n, c)
    return P(prob, sol, f"{n}\\ \\text{{ជាប់ត្រង់}}\\ x={L(c)}", [check(cl(e, c), v, "limit"), check(f"subs({e},x,{c})", v, "value")])

# ---------- B. continuity on intervals ----------
def iv(a, b, lo="(", hi=")"):
    A = "-\\infty" if a == -sp.oo else L(a); B = "+\\infty" if b == sp.oo else L(b)
    return f"{lo}{A},{B}{hi}"
def g_interval_rational(rng):
    n = fname(rng); a, b = sorted(rng.sample(range(-5, 6), 2)); one = rng.random() < .35
    den = (x - a) if one else sp.expand((x - a) * (x - b)); num = rng.choice([x + rng.randint(-3, 3), x**2 + rng.randint(1, 5), 2 * x - 1, x**3 + 1])
    if num.subs(x, a) == 0 or (not one and num.subs(x, b) == 0): num = x**2 + 7
    t = fr(num, den); e = num / den
    prob = W(rng, f"រកចន្លោះដែលអនុគមន៍ ${n}(x)={t}$ ជាប់ ។", f"សិក្សាភាពជាប់នៃអនុគមន៍ ${n}(x)={t}$ លើដែនកំណត់របស់វា ។", f"គេឱ្យ ${n}(x)={t}$ ។ រកដែនកំណត់ រួចកំណត់ចន្លោះដែល ${n}$ ជាប់ ។", f"តើអនុគមន៍ ${n}(x)={t}$ ជាប់ត្រង់ចំណុចណាខ្លះ ហើយដាច់ត្រង់ចំណុចណាខ្លះ ?")
    pts = [a] if one else [a, b]
    dom = "\\mathbb{R}\\setminus\\{" + ",".join(L(v) for v in pts) + "\\}"
    ivs = [(-sp.oo, a), (a, sp.oo)] if one else [(-sp.oo, a), (a, b), (b, sp.oo)]
    ivt = "\\cup".join(iv(*i) for i in ivs)
    sol = f"${n}$ កំណត់លុះត្រាតែភាគបែងខុសពីសូន្យ ៖ ${L(den)}\\neq 0$ " + (f"គឺ $x\\neq {L(a)}$ ។\n" if one else f"មានន័យថា $(x-{L(a)})(x-{L(b)})\\neq 0$ ។\n".replace("x--", "x+")) + f"ដូច្នេះ $D={dom}$ ។\n"
    sol += f"${n}$ ជាអនុគមន៍សនិទាន ដូច្នេះវាជាប់គ្រប់តម្លៃ $x$ ក្នុងដែនកំណត់របស់វា ។\n"
    sol += "ត្រង់ " + " និង ".join(f"$x={L(v)}$" for v in pts) + f" អនុគមន៍មិនកំណត់ ដូច្នេះវាមិនជាប់ត្រង់ទីនោះទេ ។\nដូចនេះ ${n}$ ជាប់លើចន្លោះ $\\boxed{{{ivt}}}$ ។"
    ch = [check(f"subs({den},x,{v})", 0, "excluded") for v in pts] + [check(f"limit({e},x,{a+R(1,2)})", e.subs(x, a + R(1, 2)), "continuous inside")]
    return P(prob, sol, ivt, ch)
def g_interval_root(rng):
    n = fname(rng); mode = rng.choice(["sqrt", "ln", "sqrtln", "sqrtneg", "inv"]); a = rng.randint(-4, 5); k = rng.choice([1, 2, 3])
    if mode == "sqrt":
        e = sp.sqrt(k * x - k * a); t = L(e); cond = f"{L(k*x-k*a)}\\ge 0"; I_ = iv(a, sp.oo, "[", ")"); s = rng.randint(a, a + 3) + 1
        why = "អនុគមន៍ឫសការេនៃពហុធា"
    elif mode == "sqrtneg":
        e = sp.sqrt(a - x); t = L(e); cond = f"{L(a-x)}\\ge 0"; I_ = iv(-sp.oo, a, "(", "]"); s = a - 1; why = "អនុគមន៍ឫសការេនៃពហុធា"
    elif mode == "ln":
        e = sp.log(x - a) + x; t = L(e); cond = f"{L(x-a)}>0"; I_ = iv(a, sp.oo); s = a + 1; why = "ផលបូកនៃអនុគមន៍លោការីត និងពហុធា"
    elif mode == "sqrtln":
        e = sp.log(a + 3 - x) * sp.sqrt(x - a); t = "\\sqrt{" + L(x - a) + "}\\,\\ln\\left(" + L(a + 3 - x) + "\\right)"; cond = f"{L(x-a)}\\ge 0$ និង ${L(a+3-x)}>0"; I_ = iv(a, a + 3, "[", ")"); s = a + 1; why = "ផលគុណនៃអនុគមន៍ជាប់ពីរ"
    else:
        e = 1 / sp.sqrt(x - a); t = fr(1, sp.sqrt(x - a)); cond = f"{L(x-a)}>0"; I_ = iv(a, sp.oo); s = a + 1; why = "ច្រាសនៃអនុគមន៍ឫសការេ"
    prob = W(rng, f"រកចន្លោះធំបំផុតដែល ${n}(x)={t}$ ជាប់ ។", f"កំណត់ដែនកំណត់នៃ ${n}(x)={t}$ រួចសិក្សាភាពជាប់លើដែននោះ ។", f"តើអនុគមន៍ ${n}(x)={t}$ ជាប់លើចន្លោះណា ?")
    sol = f"${n}$ កំណត់លុះត្រាតែ ${cond}$ ។ ដោះស្រាយលក្ខខណ្ឌនេះ គេបាន $D={I_}$ ។\n${n}$ ជា{why} ដូច្នេះវាជាប់លើគ្រប់ចំណុចនៃ $D$ ។\nឧទាហរណ៍ ត្រង់ $x={L(s)}$ លីមីតស្មើនឹងតម្លៃនៃអនុគមន៍ ៖ ${lim(s)}{n}(x)={L(e.subs(x,s))}$ ។\nដូចនេះ ${n}$ ជាប់លើចន្លោះ $\\boxed{{{I_}}}$ ។"
    return P(prob, sol, I_, [check(cl(e, s), e.subs(x, s), "continuous at an interior point")])

def g_on_R(rng):
    c = rng.randint(-2, 3); n = fname(rng); a = simple(rng, c, ("lin", "quad", "const")); b = simple(rng, c, ("lin", "quad"))
    cont = rng.random() < .55
    if cont: b.e = b.e - b.val + a.val; b.val = a.val; b.t = L(b.e)
    elif a.val == b.val: b.e = b.e + 2; b.val += 2; b.t = L(b.e)
    fx = cases(n, [(a.t, "x<" + L(c)), (b.t, "x" + GE + L(c))])
    prob = opening(rng, n) + "\n" + D(fx) + W(rng, f"សិក្សាភាពជាប់នៃ ${n}$ លើ $\\mathbb{{R}}$ ។", f"តើ ${n}$ ជាប់គ្រប់តម្លៃ $x$ ឬទេ ?", f"រកសំណុំនៃចំណុចដែល ${n}$ ជាប់ ។")
    sol = f"ចំពោះ $x<{L(c)}$ អនុគមន៍ជាពហុធា ដូច្នេះវាជាប់លើ ${iv(-sp.oo,c)}$ ។\nចំពោះ $x>{L(c)}$ អនុគមន៍ជាពហុធាដូចគ្នា ដូច្នេះវាជាប់លើ ${iv(c,sp.oo)}$ ។\nនៅសល់តែចំណុចត្រង់ $x={L(c)}$ ។\n" + HEAD(c)
    sol += f"${n}({L(c)})={L(b.val)}$ ។" + D(f"{lim(c,'-')}{n}(x)={L(a.val)},\\quad {lim(c,'+')}{n}(x)={L(b.val)}")
    if cont:
        sol += f"យើងឃើញថា តម្លៃទាំងបីស្មើគ្នា នោះ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។\nសន្និដ្ឋាន ៖ ដូចនេះ ${n}$ ជាប់លើ $\\boxed{{\\mathbb{{R}}}}$ ។"; ans = "\\mathbb{R}"
    else:
        ans = "\\mathbb{R}\\setminus\\{" + L(c) + "\\}"
        sol += f"លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ នោះ ${n}$ មិនជាប់ត្រង់ $x={L(c)}$ ទេ ។\nដូចនេះ ${n}$ ជាប់លើ $\\boxed{{{ans}}}$ ប៉ុណ្ណោះ ។"
    return P(prob, sol, ans, [check(cl(a.e, c, "-"), a.val, "left"), check(cl(b.e, c, "+"), b.val, "right")])

def g_three_piece(rng):
    n = fname(rng); c1 = rng.randint(-3, 0); c2 = c1 + rng.randint(2, 4)
    a = simple(rng, c1, ("lin", "quad", "const")); b = simple(rng, c1, ("lin",)); d = simple(rng, c2, ("lin", "quad", "const"))
    ok1 = rng.random() < .7; ok2 = rng.random() < .7
    if ok1: b.e = b.e - b.val + a.val
    else: b.e = b.e - b.val + a.val + rng.choice([1, 2, -1])
    b.val = b.e.subs(x, c1); m2 = b.e.subs(x, c2); b.t = L(b.e)
    if ok2: d.e = d.e - d.val + m2
    else: d.e = d.e - d.val + m2 + rng.choice([1, -2, 3])
    d.val = d.e.subs(x, c2); d.t = L(d.e)
    fx = cases(n, [(a.t, "x<" + L(c1)), (b.t, L(c1) + LE + "x" + LE + L(c2)), (d.t, "x>" + L(c2))])
    prob = opening(rng, n) + "\n" + D(fx) + W(rng, f"សិក្សាភាពជាប់នៃ ${n}$ ត្រង់ $x={L(c1)}$ និងត្រង់ $x={L(c2)}$ ។ រួចសន្និដ្ឋាន ។", f"រកចំណុចទាំងអស់ដែល ${n}$ ដាច់ ។", f"តើ ${n}$ ជាប់លើ $\\mathbb{{R}}$ ឬទេ ?")
    sol = "លើចន្លោះនីមួយៗ អនុគមន៍ជាពហុធា ដូច្នេះវាជាប់ ។ យើងត្រូវពិនិត្យតែត្រង់ចំណុចភ្ជាប់ទាំងពីរ ។\n"
    sol += HEAD(c1) + f"${n}({L(c1)})={L(b.val)}$ ។" + D(f"{lim(c1,'-')}{n}(x)={L(a.val)},\\quad {lim(c1,'+')}{n}(x)={L(b.val)}")
    sol += (f"លីមីតទាំងពីរស្មើ ${n}({L(c1)})$ នោះ ${n}$ ជាប់ត្រង់ $x={L(c1)}$ ។\n" if ok1 else f"លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ នោះ ${n}$ ដាច់ត្រង់ $x={L(c1)}$ ។\n")
    sol += HEAD(c2) + f"${n}({L(c2)})={L(m2)}$ ។" + D(f"{lim(c2,'-')}{n}(x)={L(m2)},\\quad {lim(c2,'+')}{n}(x)={L(d.val)}")
    sol += (f"លីមីតទាំងពីរស្មើ ${n}({L(c2)})$ នោះ ${n}$ ជាប់ត្រង់ $x={L(c2)}$ ។\n" if ok2 else f"លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ នោះ ${n}$ ដាច់ត្រង់ $x={L(c2)}$ ។\n")
    bads = [c for c, o in ((c1, ok1), (c2, ok2)) if not o]
    if bads:
        ans = "\\mathbb{R}\\setminus\\{" + ",".join(L(v) for v in bads) + "\\}"
        sol += f"ដូចនេះ ${n}$ ជាប់លើ $\\boxed{{{ans}}}$ ។"
    else:
        ans = "\\mathbb{R}"; sol += f"ដូចនេះ ${n}$ ជាប់លើ $\\boxed{{\\mathbb{{R}}}}$ ។"
    ch = [check(cl(a.e, c1, "-"), a.val, "left c1"), check(cl(b.e, c1, "+"), b.val, "right c1"), check(cl(b.e, c2, "-"), m2, "left c2"), check(cl(d.e, c2, "+"), d.val, "right c2")]
    return P(prob, sol, ans, ch)

# ---------- C. parameters ----------
PV = "aakm"
def qparam(rng, n, pv, c, scope=None):
    t = W(rng, f"រកតម្លៃ ${pv}$ ដោយដឹងថា ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។", f"កំណត់ចំនួនពិត ${pv}$ ដើម្បីឱ្យ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។",
             f"រកតម្លៃ ${pv}$ ដើម្បីឱ្យអនុគមន៍ ${n}$ ជាប់គ្រប់តម្លៃ $x$ ។", f"តើ ${pv}$ ត្រូវមានតម្លៃប៉ុន្មាន ទើប ${n}$ ជាអនុគមន៍ជាប់លើ $\\mathbb{{R}}$ ?")
    if scope == "point" and on_R(t):   # a piece not defined or not continuous on all of R
        t = f"កំណត់ចំនួនពិត ${pv}$ ដើម្បីឱ្យ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។"
    return t
def coef(k, v):
    return v if k == 1 else ("-" + v if k == -1 else L(k) + v)
def pretty_lin(pv, a, b, order=0):
    """a*pv*x-free helper: text for pv*x + b style."""
    return (L(a) if a not in (1,) else "") + pv
def g_param_linear(rng):
    n = fname(rng); c = rng.choice([-2, -1, 1, 2, 3]); pv = rng.choice(PV); q = simple(rng, c, ("lin", "quad", "const")); b = rng.randint(-5, 5)
    # left: pv*x + b ; right: q ; solve pv*c + b = q(c)
    aval = R(q.val - b, c)
    form = rng.choice(["ax+b", "ax^2+b", "x+a"])
    if form == "ax+b": lt = pv + "x" + ("" if b == 0 else ("+" if b > 0 else "") + L(b)); eqt = coef(c, pv) + ("" if b == 0 else ("+" if b > 0 else "") + L(b)); ee = aval * x + b
    elif form == "ax^2+b":
        aval = R(q.val - b, c * c); lt = pv + "x^{2}" + ("" if b == 0 else ("+" if b > 0 else "") + L(b)); eqt = coef(c * c, pv) + ("" if b == 0 else ("+" if b > 0 else "") + L(b)); ee = aval * x**2 + b
    else:
        aval = q.val - b * c; lt = L(b * x) + "+" + pv if b else pv; eqt = (L(b * c) + "+" if b else "") + pv; ee = b * x + aval
    fx = cases(n, [(lt, "x<" + L(c)), (q.t, "x" + GE + L(c))])
    prob = opening(rng, n) + "\n" + D(fx) + W(rng, f"ដែល ${pv}$ ជាចំនួនពិត ។ ", "") + qparam(rng, n, pv, c)
    sol = W(rng, f"លើចន្លោះ $x<{L(c)}$ និង $x>{L(c)}$ អនុគមន៍ជាពហុធា ដូច្នេះជាប់ជានិច្ច ។ យើងពិនិត្យតែត្រង់ $x={L(c)}$ ។\n", f"យើងមាន ${n}({L(c)})={L(q.val)}$ ។\n", HEAD(c))
    if on_R(prob): sol = f"លើចន្លោះ $x<{L(c)}$ និង $x>{L(c)}$ អនុគមន៍ជាពហុធា ដូច្នេះជាប់ជានិច្ច ។ យើងពិនិត្យតែត្រង់ $x={L(c)}$ ដែល ${n}({L(c)})={L(q.val)}$ ។\n"
    sol += D(f"{lim(c,'-')}{n}(x)={lim(c,'-')}\\left({lt}\\right)={eqt}") + D(f"{lim(c,'+')}{n}(x)={lim(c,'+')}\\left({q.t}\\right)={L(q.val)}")
    sol += f"${n}$ ជាប់ត្រង់ $x={L(c)}$ លុះត្រាតែ ${lim(c,'-')}{n}(x)={lim(c,'+')}{n}(x)={n}({L(c)})$ ។\n" + D(solve_eq(eqt, L(q.val), pv, L(aval))) + f"ដូចនេះ $\\boxed{{{pv}={L(aval)}}}$ ។"
    return P(prob, sol, f"{pv}={L(aval)}", [check(cl(ee, c, "-"), q.val, "left limit with the found parameter"), check(cl(q.e, c, "+"), q.val, "right")])

def g_param_two(rng):
    n = fname(rng); c1 = rng.randint(-2, 0); c2 = c1 + rng.choice([1, 2, 3]); p1 = simple(rng, c1, ("quad", "const", "lin")); p3 = simple(rng, c2, ("quad", "lin", "const"))
    aa = R(p3.val - p1.val, c2 - c1); bb = p1.val - aa * c1
    if aa.q > 2: return None
    fx = cases(n, [(p1.t, "x" + LE + L(c1)), ("ax+b", L(c1) + "<x<" + L(c2)), (p3.t, "x" + GE + L(c2))])
    prob = opening(rng, n) + "\n" + D(fx) + W(rng, f"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ ${n}$ ជាប់លើ $\\mathbb{{R}}$ ។", f"កំណត់ $a$ និង $b$ ដោយដឹងថា ${n}$ ជាប់ត្រង់ $x={L(c1)}$ និងត្រង់ $x={L(c2)}$ ។")
    A1 = coef(c1, "a") + "+b" if c1 != 0 else "b"; A2 = coef(c2, "a") + "+b" if c2 != 0 else "b"
    sol = "នៅក្រៅចំណុចភ្ជាប់ អនុគមន៍ជាពហុធា ហើយជាប់ជានិច្ច ។ ដូច្នេះត្រូវឱ្យជាប់ត្រង់ចំណុចភ្ជាប់ទាំងពីរ ។\n"
    sol += f"ត្រង់ $x={L(c1)}$ ៖ ${n}({L(c1)})={lim(c1,'-')}{n}(x)={L(p1.val)}$ ហើយ ${lim(c1,'+')}{n}(x)={A1}$ ។ លក្ខខណ្ឌគឺ ${A1}={L(p1.val)}$ ។\n"
    sol += f"ត្រង់ $x={L(c2)}$ ៖ ${n}({L(c2)})={lim(c2,'+')}{n}(x)={L(p3.val)}$ ហើយ ${lim(c2,'-')}{n}(x)={A2}$ ។ លក្ខខណ្ឌគឺ ${A2}={L(p3.val)}$ ។\n"
    sol += "ដកសមីការទាំងពីរ ៖ " + (f"$a={L(aa)}$ ។" if c2 - c1 == 1 else f"${L(c2-c1)}a={L(p3.val-p1.val)}$ នាំឱ្យ $a={L(aa)}$ ។") + f" ជំនួសចូលវិញ គេបាន $b={L(bb)}$ ។\n"
    sol += f"ដូចនេះ $\\boxed{{a={L(aa)},\\ b={L(bb)}}}$ ។"
    mid = aa * x + bb
    return P(prob, sol, f"a={L(aa)},\\ b={L(bb)}", [check(cl(mid, c1, "+"), p1.val, "join 1"), check(cl(mid, c2, "-"), p3.val, "join 2")])

def g_param_ind(rng):
    n = fname(rng); c = rng.choice([-1, 0, 0, 0, 1, 2, 3]); p = ind(rng, c); pv = rng.choice(PV); mode = rng.choice(["value", "line", "sum"])
    if mode == "value":
        aval = p.val; fx = cases(n, [(p.t, "x" + NE + L(c)), (pv, f"x={L(c)}")])
        pre = f"តាមការកំណត់ ${n}({L(c)})={pv}$ ។\n"; eqn = f"{pv}={L(p.val)}"; ee = None
    elif mode == "sum":
        s = rng.randint(-4, 4); aval = p.val - s; rhs = pv + ("" if s == 0 else ("+" if s > 0 else "") + L(s)); fx = cases(n, [(p.t, "x" + NE + L(c)), (rhs, f"x={L(c)}")])
        pre = f"យើងមាន ${n}({L(c)})={rhs}$ ។\n"; eqn = solve_eq(rhs, L(p.val), pv, L(aval))
    else:
        s = rng.randint(-4, 4); q = rng.choice([2, 3, 1]); aval = (p.val - s) if c == 0 or True else 0
        # right side x-term q*(x-c) keeps value s+aval
        cst = s - q * c; rhs = L(q * x + cst) + "+" + pv; fx = cases(n, [(p.t, "x<" + L(c)), (rhs, "x" + GE + L(c))])
        pre = f"យើងមាន ${n}({L(c)})={lim(c,'+')}{n}(x)={pv}" + ("" if s == 0 else ("+" if s > 0 else "") + L(s)) + "$ ។\n"; eqn = solve_eq(f"{pv}" + ("" if s == 0 else ("+" if s > 0 else "") + L(s)), L(p.val), pv, L(aval))
    side = "-" if mode == "line" else ""
    whole = p.kind in ("quad", "dos", "cub", "sin", "cos", "exp", "ssin")   # the other forms have a restricted domain or a second pole
    prob = opening(rng, n, whole) + "\n" + D(fx) + qparam(rng, n, pv, c, None if whole else "point")
    sol = (pieces_ok(n, c) if on_R(prob) else "") + HEAD(c) + pre + indchain(rng, p, c, side) + f"\n${n}$ ជាប់ត្រង់ $x={L(c)}$ លុះត្រាតែលីមីតស្មើនឹង ${n}({L(c)})$ ៖" + D(eqn) + f"ដូចនេះ $\\boxed{{{pv}={L(aval)}}}$ ។"
    return P(prob, sol, f"{pv}={L(aval)}", [check(cl(p.e, c, side or "+"), aval + (s if mode != "value" else 0), "limit equals the value given by the found parameter")])

def g_param_exp(rng):
    n = fname(rng); pv = rng.choice(PV); t = rng.choice(["exp", "ln", "cos", "sinratio", "e2"]); s = rng.randint(1, 4)
    if t == "exp":
        lt = L(s) + "e^{x}+" + pv; le = None; rt = L(x**2 + 2 * x + s + 2); val = s + 2; aval = 2; base = s * sp.exp(x) + 2; c = 0
        lv = f"{L(s)}+{pv}"; re_ = x**2 + 2 * x + s + 2
    elif t == "e2":
        lt = "e^{" + L(s * x) + "}"; aval = R(1, 1); base = sp.exp(s * x); c = 0; lv = "1"; rt = pv + "x+" + pv; val = None; re_ = aval * x + aval
    elif t == "ln":
        lt = "\\ln x+" + pv; aval = s + 1 - 0; base = sp.log(x) + aval; c = 1; lv = pv; rt = L(s * x + 1); val = s + 1; re_ = s * x + 1
    elif t == "cos":
        lt = L(s) + "\\cos x+" + pv; aval = R(1); base = s * sp.cos(x) + 1; c = 0; lv = f"{L(s)}+{pv}"; rt = L(x + s + 1); val = s + 1; re_ = x + s + 1
    else:
        k = s + 1; lt = fr("\\sin " + L(k) + "x", "x"); aval = sp.Integer(k - 1); base = sp.sin(k * x) / x; c = 0; lv = L(k); rt = L(x**2) + "+" + pv + "+1"; val = None; re_ = x**2 + k
    if t == "ln":
        fx = cases(n, [(rt, "x<1"), (lt, "x" + GE + "1")]); sl, sr = "+", "-"; le, ri = lt, rt
    else:
        fx = cases(n, [(lt, "x<0"), (rt, "x" + GE + "0")]); sl, sr = "-", "+"
    prob = opening(rng, n) + "\n" + D(fx) + qparam(rng, n, pv, c)
    rv = re_.subs(x, c)
    rtext = rt if val is not None else {"e2": pv, "sinratio": pv + "+1"}[t]
    if val is None: 
        rvt = rtext
    else: rvt = L(val)
    sol = (pieces_ok(n, c) if on_R(prob) else "") + HEAD(c) + f"យើងមាន ${n}({L(c)})={lv if t == 'ln' else rvt}$ ។ គណនាលីមីតនៃផ្នែកទាំងពីរត្រង់ $x={L(c)}$ ។\n"
    lim1 = lim(c, sl) + "\\left(" + lt + "\\right)" if t != "sinratio" else lim(c, sl) + lt
    sol += D(f"{lim1}={lv}" if t != "sinratio" else f"{lim1}={lim(c,sl)}{L(k)}\\cdot{fr(chr(92)+'sin '+L(k)+'x',L(k)+'x')}={L(k)}")
    sol += D(f"{lim(c,sr)}\\left({rt}\\right)={rvt}")
    sol += f"${n}$ ជាប់ត្រង់ $x={L(c)}$ លុះត្រាតែលីមីតទាំងពីរស្មើគ្នា និងស្មើ ${n}({L(c)})$ ៖" + D(solve_eq(lv, rvt, pv, L(aval))) + f"ដូចនេះ $\\boxed{{{pv}={L(aval)}}}$ ។"
    return P(prob, sol, f"{pv}={L(aval)}", [check(cl(base, c, sl), rv, "left equals right"), check(cl(re_, c, sr), rv, "other side")])

def g_param_quadratic(rng):
    n = fname(rng); c = rng.choice([1, 2, -1]); r1, r2 = rng.sample([-3, -2, -1, 1, 2, 3, 4], 2)
    # a^2 - (r1+r2) a + r1 r2 = 0 ; left: a^2 x (at c) ...
    s_, p_ = r1 + r2, r1 * r2
    # left: (a^2 + p) x / c  -> keep c=1 form simple: left a^2 + p  (const in x) + (x-c) ; right  s*a * ... 
    lt = "a^{2}x+" + L(p_ - 0) if c == 1 else None
    c = 1
    lt = "a^{2}x" + ("+" if p_ > 0 else "") + L(p_)
    rt = L(s_) + "a\\,x^{2}" if s_ != 1 else "ax^{2}"
    if s_ == -1: rt = "-ax^{2}"
    if s_ == 0: return None
    fx = cases(n, [(lt, "x<1"), (rt, "x" + GE + "1")])
    prob = opening(rng, n) + "\n" + D(fx) + W(rng, f"រកគ្រប់តម្លៃនៃចំនួនពិត $a$ ដើម្បីឱ្យ ${n}$ ជាប់ត្រង់ $x=1$ ។", f"តើមានតម្លៃ $a$ ប៉ុន្មាន ដែលធ្វើឱ្យ ${n}$ ជាប់លើ $\\mathbb{{R}}$ ? រកតម្លៃទាំងនោះ ។")
    ra = L(s_) + "a" if abs(s_) != 1 else ("a" if s_ == 1 else "-a")
    sol = HEAD(1) + D(f"{lim(1,'-')}{n}(x)=a^{{2}}{'+' if p_>0 else ''}{L(p_)}") + D(f"{lim(1,'+')}{n}(x)={n}(1)={ra}")
    q = "a^{2}" + ("-" if s_ > 0 else "+") + (L(abs(s_)) if abs(s_) != 1 else "") + "a" + ("+" if p_ > 0 else "") + L(p_)
    lo, hi = sorted([r1, r2])
    sol += f"លក្ខខណ្ឌនៃភាពជាប់ឱ្យសមីការដឺក្រេទីពីរ ៖" + D(f"{q}=0\\Leftrightarrow (a-{L(lo)})(a-{L(hi)})=0".replace("--", "+")) + f"សមីការនេះមានឫសពីរ ។ ពហុធានៅសងខាងជាប់ស្រាប់ ដូច្នេះចំពោះតម្លៃទាំងពីរ ${n}$ ជាប់លើ $\\mathbb{{R}}$ ។\nដូចនេះ $\\boxed{{a={L(lo)}\\ \\text{{ឬ}}\\ a={L(hi)}}}$ ។"
    ch = [check(cl(v * v * x + p_, 1, "-"), s_ * v, f"a={v}") for v in (r1, r2)]
    return P(prob, sol, f"a={L(lo)}\\ \\text{{ឬ}}\\ a={L(hi)}", ch)

def g_param_finite(rng):
    n = fname(rng); c = rng.choice([-2, -1, 1, 2, 3]); r = rng.choice([v for v in range(-4, 5) if v != c]); mode = rng.choice(["one", "two", "root"])
    if mode == "one":
        # x^2 + a x + q with q fixed, numerator zero at c: root r
        q = c * r; aval = -(c + r); num = x**2 + aval * x + q
        qs = "" if q == 0 else ("+" if q > 0 else "") + L(q)
        t = fr("x^{2}+ax" + qs, x - c); Lv = c - r
        prob = f"គេឱ្យ ${n}(x)={t}$ ដែល $x\\neq {L(c)}$ ។ " + W(rng, f"រកតម្លៃ $a$ ដើម្បីឱ្យ ${n}$ មានលីមីតកំណត់ត្រង់ $x={L(c)}$ រួចគណនាលីមីតនោះ ។", f"តើ $a$ ត្រូវស្មើប៉ុន្មាន ទើបគេអាចកំណត់តម្លៃ ${n}({L(c)})$ ឱ្យ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ? រកតម្លៃនោះ ។")
        sol = f"កាលណា $x\\to {L(c)}$ ភាគបែងខិតជិតសូន្យ ។ ដើម្បីឱ្យលីមីតកំណត់ ភាគយកត្រូវខិតជិតសូន្យដែរ ។\n" + D(f"{L(c*c)}{'+' if c>0 else '-'}{L(abs(c)) if abs(c)!=1 else ''}a{qs}=0\\Leftrightarrow a={L(aval)}")
        sol += f"ជំនួសចូលវិញ ភាគយកក្លាយជា ${L(num)}=\\left({L(x-c)}\\right)\\left({L(x-r)}\\right)$ ។\n" + D(f"{lim(c)}{n}(x)={lim(c)}\\left({L(x-r)}\\right)={L(Lv)}") + f"ដូចនេះ $\\boxed{{a={L(aval)},\\ {lim(c)}{n}(x)={L(Lv)}}}$ ។"
        return P(prob, sol, f"a={L(aval)},\\ {lim(c)}{n}(x)={L(Lv)}", [check(cl(num / (x - c), c), Lv, "limit"), check(f"subs({num},x,{c})", 0, "numerator vanishes")])
    if mode == "two":
        Lv = c - r; aval = -(c + r); bval = c * r; num = x**2 + aval * x + bval
        prob = f"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ ${lim(c)}{fr('x^{2}+ax+b',x-c)}={L(Lv)}$ ។"
        sol = f"ភាគបែងខិតជិតសូន្យ ហើយលីមីតកំណត់ ដូច្នេះ ${L(c)}$ ជាឫសនៃភាគយក ។ សរសេរ $x^{{2}}+ax+b=\\left({L(x-c)}\\right)(x+m)$ ។\nគេបាន ${lim(c)}(x+m)={L(c)}+m={L(Lv)}$ នាំឱ្យ $m={L(Lv-c)}$ ។\nពន្លាត ៖ $\\left({L(x-c)}\\right)\\left({L(x-r)}\\right)={L(num)}$ ។\nដូចនេះ $\\boxed{{a={L(aval)},\\ b={L(bval)}}}$ ។"
        return P(prob, sol, f"a={L(aval)},\\ b={L(bval)}", [check(cl(num / (x - c), c), Lv, "limit")])
    rr = rng.choice([1, 2, 3]); aval = rr * rr - c
    sq = sp.sqrt(x + aval)
    prob = f"គេឱ្យ ${n}(x)={fr('\\sqrt{x+a}-'+L(rr),x-c)}$ ។ រកតម្លៃ $a$ ដើម្បីឱ្យ ${n}$ មានលីមីតកំណត់ត្រង់ $x={L(c)}$ ។ រួចគណនាលីមីតនោះ ។"
    sol = f"ភាគបែងខិតជិតសូន្យ ដូច្នេះភាគយកត្រូវខិតជិតសូន្យ ៖ $\\sqrt{{{L(c)}+a}}={L(rr)}$ នាំឱ្យ ${L(c)}+a={L(rr*rr)}$ គឺ $a={L(aval)}$ ។\n" + chain(lim(c) + fr(sq - rr, x - c), [lim(c) + fr(L(x - c), "\\left(" + L(x - c) + "\\right)\\left(" + L(sq + rr) + "\\right)"), lim(c) + fr(1, sq + rr)], R(1, 2 * rr)) + f"ដូចនេះ $\\boxed{{a={L(aval)},\\ {lim(c)}{n}(x)={L(R(1,2*rr))}}}$ ។"
    return P(prob, sol, f"a={L(aval)},\\ {lim(c)}{n}(x)={L(R(1,2*rr))}", [check(cl((sq - rr) / (x - c), c), R(1, 2 * rr), "limit")])

# ---------- D. extension ----------
def g_extend(rng):
    c = rng.choice([-3, -2, -1, 0, 0, 0, 1, 2, 3, 4]); p = ind(rng, c); n = rng.choice("fh"); gname = "g"; 
    prob = W(rng, f"អនុគមន៍ ${n}(x)={p.t}$ មិនកំណត់ត្រង់ $x={L(c)}$ ។ រកតម្លៃ ${gname}({L(c)})$ ដើម្បីឱ្យអនុគមន៍ ${gname}$ ដែល ${gname}(x)={n}(x)$ ចំពោះ $x\\neq {L(c)}$ ជាប់ត្រង់ $x={L(c)}$ ។",
               f"គេឱ្យ ${n}(x)={p.t}$ ។ បង្ហាញថាគេអាចកំណត់អនុគមន៍ជាប់ ${gname}$ លើចន្លោះជុំវិញ $x={L(c)}$ ដែលស្មើនឹង ${n}$ គ្រប់កន្លែងលើកលែងត្រង់ $x={L(c)}$ ។ សរសេរ ${gname}(x)$ ជាអនុគមន៍កំណត់ជាផ្នែក ។",
               f"គណនា ${lim(c)}{n}(x)$ ដែល ${n}(x)={p.t}$ ។ តើគួរកំណត់ ${n}({L(c)})$ ស្មើប៉ុន្មាន ទើបអនុគមន៍ដែលទទួលបានជាប់ត្រង់ $x={L(c)}$ ?")
    limit_first = prob.startswith("គណនា")   # the row is mainly a limit, and it names only the one function
    if limit_first: gname = n
    sol = W(rng, f"${n}$ មិនកំណត់ត្រង់ $x={L(c)}$ ព្រោះភាគបែងស្មើសូន្យ ។ យើងគណនាលីមីតត្រង់ចំណុចនេះ ។\n", "យើងរកលីមីតជាមុន ព្រោះបើលីមីតមានតម្លៃកំណត់ នោះតម្លៃត្រូវបំពេញគឺលីមីតនេះ ។\n", "")
    sol += indchain(rng, p, c) + f"\nលីមីតនេះមានតម្លៃកំណត់ ។ បើគេកំណត់តម្លៃត្រង់ $x={L(c)}$ ស្មើ ${L(p.val)}$ នោះលីមីតស្មើនឹងតម្លៃនៃអនុគមន៍ ហើយអនុគមន៍ជាប់ត្រង់ចំណុចនោះ ។\n"
    sol += "ដូចនេះ " + D("\\boxed{" + cases(gname, [(p.t, "x" + NE + L(c)), (p.val, f"x={L(c)}")]) + "}")
    out = P(prob, sol, f"{gname}({L(c)})={L(p.val)}", [check(cl(p.e, c), p.val, "limit"), check(cl(p.e, c, "-"), p.val, "left")])
    if limit_first: out.sub = PLAIN_LIMIT
    return out
def g_extend_no(rng):
    c = rng.randint(-3, 3); n = fname(rng); mode = rng.choice(["abs", "pole", "polypole"]); d = x - c
    if mode == "abs":
        q = rng.choice([1, 2, 3]); e = q * sp.Abs(d) / d; t = (L(q) if q > 1 else "") + fr("|" + L(d) + "|", d)
        pre = f"ចំពោះ $x>{L(c)}$ គេបាន ${n}(x)={L(q)}$ ហើយចំពោះ $x<{L(c)}$ គេបាន ${n}(x)={L(-q)}$ ។" + D(f"{lim(c,'+')}{n}(x)={L(q)},\\quad {lim(c,'-')}{n}(x)={L(-q)}") + "លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ដូច្នេះ"
        chs = [check(cl(e, c, "+"), q, "right"), check(cl(e, c, "-"), -q, "left")]
    else:
        b = rng.choice([v for v in range(-4, 5) if v != c]); e = (x - b) / d if mode == "pole" else (x**2 + 1) / d; t = fr(x - b, d) if mode == "pole" else fr(x**2 + 1, d)
        N = e.subs(x, c + 1) * 1; num = (c - b) if mode == "pole" else c * c + 1; sg = 1 if num > 0 else -1
        pre = f"កាលណា $x\\to {L(c)}$ ភាគយកខិតជិត ${L(num)}\\neq 0$ ហើយភាគបែងខិតជិតសូន្យ ។" + D(f"{lim(c,'-')}{n}(x)={L(-sp.oo*sg)},\\quad {lim(c,'+')}{n}(x)={L(sp.oo*sg)}") + f"${n}(x)$ ខិតទៅរកអនន្តនៅសងខាង $x={L(c)}$ ដូច្នេះ"
        chs = [check(cl(e, c, "+"), sp.oo * sg, "right"), check(cl(e, c, "-"), -sp.oo * sg, "left")]
    prob = W(rng, f"តើគេអាចកំណត់តម្លៃ ${n}({L(c)})$ ដើម្បីឱ្យ ${n}(x)={t}$ ជាប់ត្រង់ $x={L(c)}$ បានឬទេ ?", f"គេឱ្យ ${n}(x)={t}$ ។ បង្ហាញថាគ្មានចំនួនពិត $k$ ណាដែលធ្វើឱ្យអនុគមន៍ជាប់ត្រង់ $x={L(c)}$ ក្រោយពីកំណត់ ${n}({L(c)})=k$ ទេ ។")
    sol = pre + f"គ្មានលីមីតកំណត់ត្រង់ $x={L(c)}$ ទេ ។ មិនថាគេយក ${n}({L(c)})$ ស្មើប៉ុន្មានក្តី លក្ខខណ្ឌទីពីរនៃភាពជាប់មិនផ្ទៀងផ្ទាត់ ។\nដូចនេះ គេមិនអាចធ្វើឱ្យ ${n}$ ជាប់ត្រង់ $x={L(c)}$ បានទេ ។"
    return P(prob, sol, f"\\text{{មិនអាចធ្វើឱ្យជាប់ត្រង់}}\\ x={L(c)}", chs)

# ---------- E. intermediate value theorem ----------
TV = "ទ្រឹស្តីបទតម្លៃកណ្តាល"
def roundtex(v):
    return L(sp.Float(round(float(v), 2), 3)) if False else f"{float(v):.2f}"
def signs(rng, n, a, b, ea, eb, va=None, vb=None):
    """text of two endpoint values."""
    def one(p, e):
        s = f"{n}({L(p)})={L(e)}"
        if not e.is_Rational: s += f"\\approx {float(e):.2f}"
        return s + ("<0" if e < 0 else ">0")
    return "$" + one(a, ea) + "$ និង $" + one(b, eb) + "$"
def cubic(rng):
    for _ in range(100):
        cs_ = [rng.choice([1, 1, 1, 2, -1]), rng.randint(-4, 4), rng.randint(-6, 6), rng.randint(-7, 7)]
        e = cs_[0] * x**3 + cs_[1] * x**2 + cs_[2] * x + cs_[3]
        vals = {p: e.subs(x, p) for p in range(-4, 5)}
        if 0 in vals.values(): continue
        ch = [p for p in range(-4, 4) if vals[p] * vals[p + 1] < 0]
        if ch: return e, ch, vals
def g_ivt_poly(rng):
    n = fname(rng); e, ch, v = cubic(rng); a = rng.choice(ch); b = a + 1
    wide = rng.random() < .25
    if wide:
        for w in (2, 3):
            if a + w <= 4 and v[a] * v[a + w] < 0: b = a + w; break
    prob = W(rng, f"បង្ហាញថាសមីការ ${L(e)}=0$ មានឫសយ៉ាងតិចមួយក្នុងចន្លោះ $({L(a)},{L(b)})$ ។", f"គេឱ្យ ${n}(x)={L(e)}$ ។ ស្រាយបញ្ជាក់ថាខ្សែកោងនៃ ${n}$ កាត់អ័ក្ស $x'ox$ យ៉ាងតិចមួយដងចន្លោះ $x={L(a)}$ និង $x={L(b)}$ ។", f"តើសមីការ ${L(e)}=0$ មានឫសក្នុងចន្លោះ $[{L(a)},{L(b)}]$ ឬទេ ? ពន្យល់ដោយប្រើ{TV} ។")
    sol = f"តាង ${n}(x)={L(e)}$ ។\n" if "គេឱ្យ" not in prob[:6] else ""
    sol += W(rng, f"${n}$ ជាពហុធា ដូច្នេះវាជាប់លើ $\\mathbb{{R}}$ ជាពិសេសជាប់លើចន្លោះ $[{L(a)},{L(b)}]$ ។\n", f"ពហុធាជាអនុគមន៍ជាប់ ដូច្នេះ ${n}$ ជាប់លើចន្លោះ $[{L(a)},{L(b)}]$ ។\n")
    sol += "គណនាតម្លៃនៅចុងចន្លោះ ៖ " + signs(rng, n, a, b, v[a], v[b]) + " ។\n"
    sol += f"ដោយ ${n}({L(a)})\\times {n}({L(b)})<0$ តាម{TV} មានចំនួន $\\alpha$ យ៉ាងតិចមួយក្នុង $({L(a)},{L(b)})$ ដែល ${n}(\\alpha)=0$ ។\nដូចនេះ សមីការមានឫសយ៉ាងតិចមួយក្នុងចន្លោះ $\\boxed{{({L(a)},{L(b)})}}$ ។"
    return P(prob, sol, f"\\exists\\,\\alpha\\in({L(a)},{L(b)}):\\ {n}(\\alpha)=0", [check(f"subs({e},x,{a})", v[a], "left end"), check(f"subs({e},x,{b})", v[b], "right end"), check(f"sign(subs({e},x,{a})*subs({e},x,{b}))", -1, "opposite signs")])

def fam(rng):
    a = rng.choice([1, 2, 3]); b = rng.randint(1, 9)
    F = rng.choice(["e1", "e2", "e3", "e5", "e6", "e7", "e9", "e10", "e11", "e12"])
    if F == "e1": return exp_(x) + a * x - b, "e^{x}+" + L(a), "$e^{x}>0$ ហើយ $" + L(a) + ">0$", None
    if F == "e2": return sp.log(x) + a * x - b, L(a) + "+" + fr(1, "x"), "$x>0$", (0, sp.oo)
    if F == "e3": return x**3 + a * x - b, "3x^{2}+" + L(a), "$3x^{2}\\ge 0$", None
    if F == "e5": return (a + 1) * x - sp.cos(x) - b, L(a + 1) + "+\\sin x", "$\\sin x\\ge -1$", None
    if F == "e6": return exp_(x) + x**3 - b, "e^{x}+3x^{2}", "$e^{x}>0$ និង $3x^{2}\\ge 0$", None
    if F == "e7": return sp.sqrt(x) + a * x - b, fr(1, "2\\sqrt{x}") + "+" + L(a), "$x>0$", (0, sp.oo)
    if F == "e9": return x * exp_(x) - b, "(x+1)e^{x}", "$x>0$", (0, sp.oo)
    if F == "e10": return exp_(-x) - a * x + b, "-e^{-x}-" + L(a), "$e^{-x}>0$", None
    if F == "e11": return sp.log(x) - 1 / x + 1 - b + 1, fr(1, "x") + "+" + fr(1, "x^{2}"), "$x>0$", (0, sp.oo)
    if F == "e12": return x**5 + a * x + 1 - b, "5x^{4}+" + L(a), "$5x^{4}\\ge 0$", None
exp_ = sp.exp
def find_bracket(e, dom):
    fnn = sp.lambdify(x, e, "math"); lo = 1 if dom else -4
    for p in range(lo, 9):
        try:
            u, w = fnn(p), fnn(p + 1)
        except Exception: continue
        if abs(u) > 1e-6 and abs(w) > 1e-6 and u * w < 0: return p, p + 1
    return None
def g_ivt_unique(rng):
    for _ in range(40):
        e, dp, why, dom = fam(rng); br = find_bracket(e, dom)
        if br: break
    else: return None
    a, b = br; n = fname(rng); ea, eb = e.subs(x, a), e.subs(x, b); inc = float(ea) < 0
    dtx = "\\mathbb{R}" if dom is None else iv(*dom)
    prob = W(rng, f"បង្ហាញថាសមីការ ${L(e)}=0$ មានឫសតែមួយគត់ $\\alpha$ ហើយ ${L(a)}<\\alpha<{L(b)}$ ។", f"គេឱ្យអនុគមន៍ ${n}(x)={L(e)}$ កំណត់លើ ${dtx}$ ។ សិក្សាអថេរភាពនៃ ${n}$ រួចទាញបញ្ជាក់ថាសមីការ ${n}(x)=0$ មានឫសតែមួយគត់ក្នុងចន្លោះ $({L(a)},{L(b)})$ ។", f"ស្រាយបញ្ជាក់ថាខ្សែកោង $y={L(e)}$ កាត់អ័ក្ស $x'ox$ ត្រង់ចំណុចតែមួយគត់ ដែលមានអាប់ស៊ីសនៅចន្លោះ ${L(a)}$ និង ${L(b)}$ ។")
    sg = ">0" if inc else "<0"
    tname = n
    sol = f"តាង ${n}(x)={L(e)}$ ជាអនុគមន៍ជាប់លើ ${dtx}$ ។\nយើងបាន ${n}'(x)={dp}$ ។ ដោយ {why} គេបាន ${n}'(x){sg}$ " + ("ជានិច្ច " if dom is None else f"ចំពោះគ្រប់ $x$ ក្នុង ${dtx}$ ") + "។ ដូច្នេះ $" + n + "$ ជា" + ("អនុគមន៍កើន" if inc else "អនុគមន៍ចុះ") + "ដាច់ខាត ។\n".replace("ដាច់ខាត", "")
    sol += "ម្យ៉ាងទៀត " + signs(rng, n, a, b, ea, eb) + " ។\n"
    tb = variation_table([L(a), L(b)], ["", "+" if inc else "-", ""], [L(ea), "\\nearrow" if inc else "\\searrow", L(eb)], n)
    sol += D(tb) + f"តាម{TV} សមីការ ${n}(x)=0$ មានឫសយ៉ាងតិចមួយ $\\alpha$ ក្នុង $({L(a)},{L(b)})$ ។ ហើយដោយ ${n}$ " + ("កើន" if inc else "ចុះ") + f"ជានិច្ច ឫសនោះមានតែមួយ ។\nដូចនេះ សមីការមានឫសតែមួយគត់ $\\boxed{{\\alpha\\in({L(a)},{L(b)})}}$ ។"
    ch = [check(f"sign(subs({e},x,{a}))", -1 if inc else 1, "sign left"), check(f"sign(subs({e},x,{b}))", 1 if inc else -1, "sign right"), check(f"sign(subs(diff({e},x),x,{R(2*a+1,2)}))", 1 if inc else -1, "sign of derivative at the midpoint")]
    return P(prob, sol, f"\\alpha\\in({L(a)},{L(b)})", ch, tables=[dict(type="variation_table", latex=tb, image=None, alt_km=f"តារាងអថេរភាពនៃ ${n}$ លើចន្លោះ $[{L(a)},{L(b)}]$ ។")])

def g_ivt_value(rng):
    n = fname(rng); mode = rng.choice(["quad", "cubic", "rat"]); 
    if mode == "quad": e = x**2 + rng.randint(-3, 3) * x + rng.randint(-2, 3)
    elif mode == "cubic": e = x**3 + rng.randint(-2, 2) * x + rng.randint(-2, 2)
    else: e = (x**2 + 1) / (x + 5)
    a = rng.randint(0, 2); b = a + rng.choice([2, 3]); fa, fb = e.subs(x, a), e.subs(x, b)
    if fa == fb: return None
    lo, hi = min(fa, fb), max(fa, fb); k = sp.floor((lo + hi) / 2) if hi - lo > 2 else (lo + hi) / 2
    if not lo < k < hi: return None
    dtxt = "ពហុធា" if mode != "rat" else f"អនុគមន៍សនិទានដែលភាគបែងមិនស្មើសូន្យលើ $[{L(a)},{L(b)}]$"
    prob = W(rng, f"គេឱ្យ ${n}(x)={L(e)}$ ។ បង្ហាញថាមានចំនួន $c$ ក្នុងចន្លោះ $({L(a)},{L(b)})$ យ៉ាងតិចមួយ ដែល ${n}(c)={L(k)}$ ។", f"តើសមីការ ${L(e)}={L(k)}$ មានឫសក្នុងចន្លោះ $({L(a)},{L(b)})$ ឬទេ ?")
    sol = f"${'' if False else n}$ ជា{dtxt} ដូច្នេះវាជាប់លើ $[{L(a)},{L(b)}]$ ។\n" if "តើ" not in prob[:4] else f"តាង ${n}(x)={L(e)}$ ។ ${n}$ ជា{dtxt} ដូច្នេះជាប់លើ $[{L(a)},{L(b)}]$ ។\n"
    sol += f"យើងបាន ${n}({L(a)})={L(fa)}$ និង ${n}({L(b)})={L(fb)}$ ។\nដោយ ${L(k)}$ នៅចន្លោះ ${L(lo)}$ និង ${L(hi)}$ តាម{TV} មាន $c\\in({L(a)},{L(b)})$ យ៉ាងតិចមួយដែល ${n}(c)={L(k)}$ ។\nដូចនេះ សមីការមានឫសក្នុង $\\boxed{{({L(a)},{L(b)})}}$ ។"
    return P(prob, sol, f"\\exists\\,c\\in({L(a)},{L(b)}):\\ {n}(c)={L(k)}", [check(f"subs({e},x,{a})", fa, "left"), check(f"subs({e},x,{b})", fb, "right"), check(f"sign(({k}-({fa}))*({k}-({fb})))", -1, "k is between")])

def g_ivt_bisect(rng):
    n = fname(rng); e, ch, v = cubic(rng); a = rng.choice(ch); b = a + 1
    prob = f"គេឱ្យ ${n}(x)={L(e)}$ ។ បង្ហាញថាសមីការ ${n}(x)=0$ មានឫស $\\alpha$ ក្នុងចន្លោះ $({L(a)},{L(b)})$ ។ រួចកាត់ចន្លោះនោះពាក់កណ្តាលពីរដង ដើម្បីរកចន្លោះប្រវែង $\\frac{{1}}{{4}}$ ដែលមាន $\\alpha$ ។"
    lo, hi = sp.Integer(a), sp.Integer(b); elo = v[a]; ch_ = [check(f"subs({e},x,{a})", v[a], "left"), check(f"subs({e},x,{b})", v[b], "right")]
    sol = f"${n}$ ជាពហុធា ដូច្នេះជាប់លើ $[{L(a)},{L(b)}]$ ។ ដោយ " + signs(rng, n, a, b, v[a], v[b]) + f" តាម{TV} មាន $\\alpha\\in({L(a)},{L(b)})$ ។\n"
    for i in range(2):
        mid = (lo + hi) / 2; fm = e.subs(x, mid)
        if fm == 0: return None
        sol += f"ចំណុចកណ្តាល $x={L(mid)}$ ឱ្យ ${n}\\left({L(mid)}\\right)={L(fm)}" + ("<0" if fm < 0 else ">0") + "$ ។ "
        ch_.append(check(f"subs({e},x,{mid})", fm, "midpoint"))
        if fm * elo < 0: hi = mid
        else: lo = mid; elo = fm
        sol += f"សញ្ញាផ្ទុយគ្នានៅលើចន្លោះ $\\left({L(lo)},{L(hi)}\\right)$ ដូច្នេះ $\\alpha$ នៅក្នុងនោះ ។\n"
    sol += f"ដូចនេះ $\\boxed{{{L(lo)}<\\alpha<{L(hi)}}}$ ។"
    return P(prob, sol, f"{L(lo)}<\\alpha<{L(hi)}", ch_)

def g_ivt_three(rng):
    n = fname(rng); r = sorted(rng.sample([R(k, 2) for k in range(-7, 8, 2)], 3))
    e = sp.expand(8 * (x - r[0]) * (x - r[1]) * (x - r[2])); 
    pts = [sp.floor(r[0]), sp.ceiling(r[0]), sp.ceiling(r[1]), sp.ceiling(r[2])]
    if len(set(pts)) < 4: return None
    vals = [e.subs(x, p) for p in pts]
    tb = "\\begin{array}{c|" + "c" * 4 + "} x & " + " & ".join(L(p) for p in pts) + " \\\\ \\hline " + n + "(x) & " + " & ".join(L(q) for q in vals) + " \\end{array}"
    prob = W(rng, f"បង្ហាញថាសមីការ ${L(e)}=0$ មានឫសបីក្នុង $\\mathbb{{R}}$ រួចកំណត់ចន្លោះដែលឫសនីមួយៗស្ថិតនៅ ។", f"ដោយគណនា ${n}(x)={L(e)}$ ត្រង់ចំនួនគត់សមស្រប បង្ហាញថាខ្សែកោងនៃ ${n}$ កាត់អ័ក្ស $x'ox$ បីដង ។")
    sol = f"តាង ${n}(x)={L(e)}$ ។ ${n}$ ជាពហុធា ដូច្នេះវាជាប់លើ $\\mathbb{{R}}$ ។\nយើងគណនាតម្លៃមួយចំនួន ៖" + D(tb)
    ivs = [(pts[i], pts[i + 1]) for i in range(3)]
    sol += "យើងឃើញថា " + " ។ ".join(f"${n}$ ប្តូរសញ្ញាលើ $({L(p)},{L(q)})$" for p, q in ivs) + f" ។\nតាម{TV} ចន្លោះនីមួយៗមានឫសយ៉ាងតិចមួយ ។ ចន្លោះទាំងបីមិនជាន់គ្នា ហើយពហុធាដឺក្រេទីបីមានឫសមិនលើសបី ។\n"
    ans = ",\\ ".join(f"x_{i+1}\\in({L(p)},{L(q)})" for i, (p, q) in enumerate(ivs))
    sol += f"ដូចនេះ សមីការមានឫសបីគត់ ៖ $\\boxed{{{ans}}}$ ។"
    return P(prob, sol, ans, [check(f"subs({e},x,{p})", q, "value") for p, q in zip(pts, vals)], tables=[dict(type="sign_table", latex=tb, image=None, alt_km=f"តារាងតម្លៃនៃ ${n}$ ត្រង់ចំនួនគត់ ។")])

def g_ivt_odd(rng):
    n = fname(rng); dg = rng.choice([3, 5]); a = rng.choice([1, 2, -1]); e = a * x**dg + rng.randint(-3, 3) * x**2 + rng.randint(-4, 4) * x + rng.randint(-5, 5)
    sg = 1 if a > 0 else -1
    prob = W(rng, f"គណនាលីមីតនៃ ${n}(x)={L(e)}$ ត្រង់ $-\\infty$ និងត្រង់ $+\\infty$ រួចទាញបញ្ជាក់ថាសមីការ ${n}(x)=0$ មានឫសពិតយ៉ាងតិចមួយ ។", f"ស្រាយបញ្ជាក់ថាសមីការ ${L(e)}=0$ មានឫសយ៉ាងតិចមួយក្នុង $\\mathbb{{R}}$ ។")
    top = L(a * x**dg)
    sol = f"លីមីតនៃពហុធាត្រង់អនន្តស្មើលីមីតនៃតួដឺក្រេខ្ពស់បំផុត ។" + D(f"{lim('+oo')}{n}(x)={lim('+oo')}{top}={L(sp.oo*sg)}") + D(f"{lim('-oo')}{n}(x)={lim('-oo')}{top}={L(-sp.oo*sg)}")
    sol += f"ដូច្នេះមានចំនួន $p$ និង $q$ ដែល ${n}(p)<0<{n}(q)$ ។ ដោយ ${n}$ ជាពហុធា វាជាប់លើចន្លោះកំណត់ដោយ $p$ និង $q$ ។\nតាម{TV} មានឫសមួយនៅចន្លោះ $p$ និង $q$ ។\nដូចនេះ សមីការមានឫសពិតយ៉ាងតិចមួយ ។"
    return P(prob, sol, f"{lim('-oo')}{n}(x)={L(-sp.oo*sg)},\\ {lim('+oo')}{n}(x)={L(sp.oo*sg)}", [check(cl(e, "oo"), sp.oo * sg, "+inf"), check(cl(e, "-oo"), -sp.oo * sg, "-inf")])

# ---------- F. asymptotes ----------
def Lsign(N, den0):
    return f"\\frac{{{L(N)}}}{{{den0}}}"
def va_lines(n, c, N, sg_left):
    """one-sided limits at pole c of N/(den), den<0 on left when sg_left=-1. Returns text, left, right."""
    s = 1 if N > 0 else -1
    l = sp.oo * s * sg_left; r = -l
    d0l, d0r = ("0^{-}", "0^{+}") if sg_left == -1 else ("0^{+}", "0^{-}")
    t = D(f"{lim(c,'-')}{n}(x)={Lsign(N,d0l)}={L(l)}") + D(f"{lim(c,'+')}{n}(x)={Lsign(N,d0r)}={L(r)}")
    return t, l, r
def askasym(rng, n, t):
    return W(rng, f"គេឱ្យអនុគមន៍ ${n}(x)={t}$ ។ រកអាស៊ីមតូតទាំងអស់នៃខ្សែកោង $(C)$ តំណាង ${n}$ ។",
             f"គណនាលីមីតនៃ ${n}(x)={t}$ ត្រង់ចុងនៃដែនកំណត់ រួចទាញរកសមីការអាស៊ីមតូតឈរ និងអាស៊ីមតូតដេក ។",
             f"សិក្សាលីមីតនៃអនុគមន៍ ${n}(x)={t}$ ត្រង់ $-\\infty$ ត្រង់ $+\\infty$ និងត្រង់តម្លៃដែលមិនកំណត់ ។ តើខ្សែកោងមានអាស៊ីមតូតអ្វីខ្លះ ?",
             f"គេមាន ${n}(x)={t}$ មានក្រាប $(C)$ ។ ទាញរកអាស៊ីមតូតនៃ $(C)$ ដោយប្រើលីមីត ។")
def homo_part(rng, n=None):
    n = n or fname(rng); cc = rng.choice([1, 1, 1, 2, 3]); a = rng.choice([-3, -2, -1, 1, 2, 3, 4]); dpole = rng.randint(-4, 4) ; 
    b = rng.randint(-6, 6); N = a * dpole + b
    if N == 0: b += 1; N += 1
    den = cc * (x - dpole); num = a * x + b; e = num / den; t = fr(num, sp.expand(den)); h = R(a, cc)
    dom = f"\\mathbb{{R}}\\setminus\\{{{L(dpole)}\\}}"
    sol = f"${n}$ កំណត់លុះត្រាតែ ${L(sp.expand(den))}\\neq 0$ គឺ $D={dom}$ ។\n"
    sol += "ត្រង់អនន្ត ដាក់ $x$ ជាកត្តាលើភាគយក និងភាគបែង ៖"
    sol += D(f"{lim('+oo')}{n}(x)={lim('+oo')}\\frac{{x\\left({L(a)}{'+' if b>=0 else '-'}\\frac{{{L(abs(b))}}}{{x}}\\right)}}{{x\\left({L(cc)}{'-' if dpole*cc>0 else '+'}\\frac{{{L(abs(dpole*cc))}}}{{x}}\\right)}}={L(h)}")
    sol += f"ដូចគ្នា ${lim('-oo')}{n}(x)={L(h)}$ ។ ដូច្នេះ បន្ទាត់ $y={L(h)}$ ជាអាស៊ីមតូតដេកនៃ $(C)$ ។\n"
    sol += f"ត្រង់ $x={L(dpole)}$ ភាគយកខិតជិត ${L(N)}$ ហើយភាគបែងខិតជិតសូន្យ ៖"
    tx, l, r = va_lines(n, dpole, R(N, 1), -1); sol += tx
    sol += f"ដូច្នេះ បន្ទាត់ $x={L(dpole)}$ ជាអាស៊ីមតូតឈរនៃ $(C)$ ។\n"
    ans = f"x={L(dpole)},\\ y={L(h)}"
    sol += f"ដូចនេះ $(C)$ មានអាស៊ីមតូតឈរ $\\boxed{{x={L(dpole)}}}$ និងអាស៊ីមតូតដេក $\\boxed{{y={L(h)}}}$ ។"
    ch = [check(cl(e, "oo"), h, "+inf"), check(cl(e, "-oo"), h, "-inf"), check(cl(e, dpole, "-"), l, "left"), check(cl(e, dpole, "+"), r, "right")]
    return e, t, sol, ans, ch, dpole, h
def g_homographic(rng):
    n = fname(rng); e, t, sol, ans, ch, d, h = homo_part(rng, n)
    fig = None
    if rng.random() < .25:
        fig = dict(pieces=[(e, d - 6, d - .02), (e, d + .02, d + 6)], va=[d], ha=[h], where="s", win=(d - 6, d + 6, float(h) - 6, float(h) + 6), alt=f"ខ្សែកោងអ៊ីពែបូលនៃ ${n}$ ជាមួយអាស៊ីមតូត $x={L(d)}$ និង $y={L(h)}$ ។".replace("អ៊ីពែបូល", ""))
    return P(askasym(rng, n, t), sol, ans, ch, fig=fig)

def slant_data(rng):
    a = rng.choice([1, 1, 2, -1, 3]); b = rng.randint(-4, 4); k = rng.choice([-4, -3, -2, -1, 1, 2, 3, 5]); d = rng.randint(-3, 4)
    num = sp.expand((a * x + b) * (x - d) + k); return a, b, k, d, num, num / (x - d)
def canon_txt(a, b, k, d, num):
    return f"ចែកភាគយកនឹងភាគបែង គេបាន ៖" + D(f"{fr(num,x-d)}={L(a*x+b)}{'+' if k>0 else '-'}{fr(abs(k),x-d)}")
def g_slant(rng):
    n = fname(rng); a, b, k, d, num, e = slant_data(rng); t = fr(num, x - d); ln = a * x + b
    mode = rng.choice(["find", "show"])
    if mode == "find":
        prob = W(rng, f"គេឱ្យ ${n}(x)={t}$ ។ សរសេរ ${n}(x)$ ជារាងកាណូនិក រួចរកអាស៊ីមតូតឈរ និងអាស៊ីមតូតទ្រេតនៃខ្សែកោង ។", f"រកអាស៊ីមតូតទាំងអស់នៃខ្សែកោង $y={t}$ ។")
    else:
        prob = f"គេឱ្យអនុគមន៍ ${n}(x)={t}$ ។ បង្ហាញថាបន្ទាត់ $(d):y={L(ln)}$ ជាអាស៊ីមតូតទ្រេតនៃក្រាបនៃ ${n}$ ត្រង់ $+\\infty$ និងត្រង់ $-\\infty$ ។ តើក្រាបមានអាស៊ីមតូតឈរឬទេ ?"
    sol = ("" if "${n}(x)".replace("{n}", n) in prob else f"តាង ${n}(x)={t}$ ។\n") + canon_txt(a, b, k, d, num)
    sol += f"គេបាន ${n}(x)-\\left({L(ln)}\\right)={fr(k,x-d)}$ ដូច្នេះ" + D(f"{lim('+oo')}\\left[{n}(x)-\\left({L(ln)}\\right)\\right]={lim('-oo')}\\left[{n}(x)-\\left({L(ln)}\\right)\\right]=0")
    sol += f"នាំឱ្យបន្ទាត់ $y={L(ln)}$ ជាអាស៊ីមតូតទ្រេត ។\nត្រង់ $x={L(d)}$ ភាគយកខិតជិត ${L(k)}$ ហើយភាគបែងខិតជិតសូន្យ ៖"
    tx, l, r = va_lines(n, d, R(k), -1); sol += tx + f"ដូចនេះ អាស៊ីមតូតឈរ $\\boxed{{x={L(d)}}}$ និងអាស៊ីមតូតទ្រេត $\\boxed{{y={L(ln)}}}$ ។"
    fig = None
    if rng.random() < .2:
        y0 = float(ln.subs(x, d)); fig = dict(pieces=[(e, d - 6, d - .05), (e, d + .05, d + 6)], va=[d], slant=[ln], where="s", win=(d - 6, d + 6, y0 - 8, y0 + 8), alt=f"ក្រាបនៃ ${n}$ ជាមួយអាស៊ីមតូតឈរ $x={L(d)}$ និងអាស៊ីមតូតទ្រេត $y={L(ln)}$ ។")
    return P(prob, sol, f"x={L(d)},\\ y={L(ln)}", [check(cl(e - ln, "oo"), 0, "slant +inf"), check(cl(e - ln, "-oo"), 0, "slant -inf"), check(cl(e, d, "-"), l, "left"), check(cl(e, d, "+"), r, "right")], fig=fig)

def g_two_va(rng):
    n = fname(rng); a = rng.choice([1, 2, 3, 4]); mode = rng.choice(["const", "lin", "sq"])
    den = x**2 - a * a
    if mode == "const": num = sp.Integer(rng.choice([1, 2, 3, -1, -2])); h = 0
    elif mode == "lin":
        num = x + rng.choice([v for v in range(-5, 6) if abs(v) != a]); h = 0
    else: num = rng.choice([1, 2, 3]) * x**2 + 1; h = num.coeff(x, 2)
    e = num / den; t = fr(num, den); Na, Nb = num.subs(x, a), num.subs(x, -a)
    prob = askasym(rng, n, t)
    sol = f"$D=\\mathbb{{R}}\\setminus\\{{-{L(a)},{L(a)}\\}}$ ព្រោះ ${L(den)}=\\left({L(x-a)}\\right)\\left({L(x+a)}\\right)$ ។\n"
    sol += f"ដឺក្រេភាគយក" + ("តូចជាងដឺក្រេភាគបែង" if h == 0 else "ស្មើនឹងដឺក្រេភាគបែង") + " ដូច្នេះ" + D(f"{lim('+oo')}{n}(x)={lim('-oo')}{n}(x)={L(h)}") + f"បន្ទាត់ $y={L(h)}$ ជាអាស៊ីមតូតដេក ។\n"
    s1 = 1 if Na > 0 else -1; s2 = 1 if Nb > 0 else -1
    lr = [(a, "-", -s1), (a, "+", s1), (-a, "-", s2), (-a, "+", -s2)]
    sol += f"ត្រង់ $x={L(a)}$ ភាគយកខិតជិត ${L(Na)}$ ហើយត្រង់ $x={L(-a)}$ ភាគយកខិតជិត ${L(Nb)}$ ។ សញ្ញានៃភាគបែងបង្ហាញលីមីត ៖"
    sol += D(",\\quad ".join(f"{lim(c,s_)}{n}(x)={L(sp.oo*g)}" for c, s_, g in lr[:2])) + D(",\\quad ".join(f"{lim(c,s_)}{n}(x)={L(sp.oo*g)}" for c, s_, g in lr[2:]))
    sol += f"ដូចនេះ អាស៊ីមតូតឈរ $\\boxed{{x={L(-a)}}}$ $\\boxed{{x={L(a)}}}$ និងអាស៊ីមតូតដេក $\\boxed{{y={L(h)}}}$ ។"
    return P(prob, sol, f"x=\\pm {L(a)},\\ y={L(h)}", [check(cl(e, c, s_), sp.oo * g, "side") for c, s_, g in lr] + [check(cl(e, "oo"), h, "inf")])

def g_hole(rng):
    n = fname(rng); a, b, c = rng.sample(range(-4, 5), 3)
    num = sp.expand((x - a) * (x - b)); den = sp.expand((x - a) * (x - c)); e = num / den; t = fr(num, den); v = R(a - b, a - c); N = c - b
    prob = W(rng, f"គេឱ្យ ${n}(x)={t}$ ។ រកចំណុចដែល ${n}$ មិនកំណត់ រួចបញ្ជាក់ថាចំណុចណាជាអាស៊ីមតូតឈរ ចំណុចណាមិនមែន ។", f"តើបន្ទាត់ $x={L(a)}$ និង $x={L(c)}$ សុទ្ធតែជាអាស៊ីមតូតឈរនៃក្រាប $y={t}$ ឬទេ ? ពន្យល់ ។", f"សិក្សាលីមីតនៃ ${n}(x)={t}$ ត្រង់ $x={L(a)}$ និងត្រង់ $x={L(c)}$ ។ រួចទាញរកអាស៊ីមតូតឈរ ។")
    sol = f"ដាក់ជាកត្តា ៖ ${n}(x)={fr(chr(92)+'left('+L(x-a)+chr(92)+'right)'+chr(92)+'left('+L(x-b)+chr(92)+'right)',chr(92)+'left('+L(x-a)+chr(92)+'right)'+chr(92)+'left('+L(x-c)+chr(92)+'right)')}$ ។ ភាគបែងស្មើសូន្យត្រង់ $x={L(a)}$ និង $x={L(c)}$ ។\n"
    sol += f"ចំពោះ $x\\neq {L(a)}$ គេអាចសម្រួល ${n}(x)={fr(x-b,x-c)}$ ។\n" + D(f"{lim(a)}{n}(x)={lim(a)}{fr(x-b,x-c)}={L(v)}") + f"លីមីតកំណត់ ដូច្នេះ $x={L(a)}$ មិនមែនជាអាស៊ីមតូតទេ ក្រាបគ្រាន់តែខ្វះចំណុច $\\left({L(a)},{L(v)}\\right)$ ។\n"
    tx, l, r = va_lines(n, c, R(N), -1)
    sol += f"ត្រង់ $x={L(c)}$ ភាគយក $x{'-' if b>0 else '+'}{L(abs(b))}$ ខិតជិត ${L(N)}\\neq 0$ ៖" + tx + f"ដូចនេះ អាស៊ីមតូតឈរតែមួយគត់គឺ $\\boxed{{x={L(c)}}}$ ។"
    sol = sol.replace("x+0", "x").replace("x-0", "x")
    return P(prob, sol, f"x={L(c)}", [check(cl(e, a), v, "hole"), check(cl(e, c, "-"), l, "left"), check(cl(e, c, "+"), r, "right")])

def g_asym_exp(rng):
    n = fname(rng); mode = rng.choice(["lin+e-x", "k+ex", "xe", "logistic", "lin+ex"]); a = rng.choice([1, 2, -1, 3]); b = rng.randint(-3, 4); k = rng.choice([1, 2, 3, -1, -2])
    if mode == "lin+e-x":
        e = a * x + b + sp.exp(-x); t = L(a * x + b) + "+e^{-x}"; ln = a * x + b
        prob = f"គេឱ្យ ${n}(x)={t}$ ។ បង្ហាញថាបន្ទាត់ $y={L(ln)}$ ជាអាស៊ីមតូតទ្រេតនៃខ្សែកោងត្រង់ $+\\infty$ ។"
        sol = f"យើងមាន ${n}(x)-\\left({L(ln)}\\right)=e^{{-x}}$ ។" + D(f"{lim('+oo')}e^{{-x}}=0") + f"ដូចនេះ បន្ទាត់ $\\boxed{{y={L(ln)}}}$ ជាអាស៊ីមតូតទ្រេតនៃខ្សែកោងត្រង់ $+\\infty$ ។"
        return P(prob, sol, f"y={L(ln)}", [check(cl(e - ln, "oo"), 0, "slant")])
    if mode == "lin+ex":
        e = a * x + b + sp.exp(x); t = L(a * x + b) + "+e^{x}"; ln = a * x + b
        prob = f"រកអាស៊ីមតូតទ្រេតនៃខ្សែកោង $y={t}$ ត្រង់ $-\\infty$ ។ តើវាមានអាស៊ីមតូតត្រង់ $+\\infty$ ឬទេ ?"
        sol = f"តាង ${n}(x)={t}$ ។ កាលណា $x\\to -\\infty$ គេបាន $e^{{x}}\\to 0$ នោះ" + D(f"{lim('-oo')}\\left[{n}(x)-\\left({L(ln)}\\right)\\right]={lim('-oo')}e^{{x}}=0") + f"ត្រង់ $+\\infty$ ៖ ${lim('+oo')}{fr(n+'(x)','x')}=+\\infty$ ព្រោះ ${lim('+oo')}{fr('e^{x}','x')}=+\\infty$ ដូច្នេះគ្មានអាស៊ីមតូតត្រង់ $+\\infty$ ទេ ។\nដូចនេះ អាស៊ីមតូតទ្រេតគឺ $\\boxed{{y={L(ln)}}}$ ត្រង់ $-\\infty$ ។"
        return P(prob, sol, f"y={L(ln)}", [check(cl(e - ln, "-oo"), 0, "slant"), check(cl(e / x, "oo"), "oo", "no asymptote")])
    if mode == "k+ex":
        e = k + sp.exp(x); t = L(k) + "+e^{x}"
        prob = W(rng, f"គណនា ${lim('-oo')}\\left({t}\\right)$ រួចទាញរកអាស៊ីមតូតដេកនៃក្រាប $y={t}$ ។", f"ក្រាបនៃ ${n}(x)={t}$ មានអាស៊ីមតូតដេកឬទេ ? បើមាន រកសមីការ ។")
        sol = f"យើងដឹងថា ${lim('-oo')}e^{{x}}=0$ ។" + D(f"{lim('-oo')}\\left({t}\\right)={L(k)}") + f"ត្រង់ $+\\infty$ លីមីតស្មើ $+\\infty$ ។ ដូចនេះ ក្រាបមានអាស៊ីមតូតដេក $\\boxed{{y={L(k)}}}$ ត្រង់ $-\\infty$ ។"
        return P(prob, sol, f"y={L(k)}", [check(cl(e, "-oo"), k, "-inf"), check(cl(e, "oo"), "oo", "+inf")])
    if mode == "xe":
        e = (x + b) * sp.exp(x) + k; t = "\\left(" + L(x + b) + "\\right)e^{x}" + ("+" if k > 0 else "") + L(k)
        prob = f"គេឱ្យ ${n}(x)={t}$ ។ (យើងដឹងថា ${lim('-oo')}xe^{{x}}=0$) គណនា ${lim('-oo')}{n}(x)$ រួចបកស្រាយលទ្ធផលជាអាស៊ីមតូត ។"
        sol = f"ពន្លាត ៖ ${n}(x)=xe^{{x}}" + ("" if b == 0 else ("+" if b > 0 else "") + L(b) + "e^{x}") + ("+" if k > 0 else "") + L(k) + "$ ។\n" + f"ដោយ ${lim('-oo')}xe^{{x}}=0$ និង ${lim('-oo')}e^{{x}}=0$ គេបាន ${lim('-oo')}{n}(x)={L(k)}$ ។\nដូចនេះ បន្ទាត់ $\\boxed{{y={L(k)}}}$ ជាអាស៊ីមតូតដេកនៃក្រាបត្រង់ $-\\infty$ ។"
        return P(prob, sol, f"y={L(k)}", [check(cl(e, "-oo"), k, "-inf")])
    kk = abs(k) + 1
    e = kk / (1 + sp.exp(x)); t = fr(kk, "1+e^{x}")
    prob = f"គណនាលីមីតនៃ ${n}(x)={t}$ ត្រង់ $-\\infty$ និងត្រង់ $+\\infty$ ។ បង្ហាញថាក្រាបមានអាស៊ីមតូតដេកពីរ ។"
    sol = D(f"{lim('-oo')}{n}(x)={fr(kk,'1+0')}={L(kk)}") + "ព្រោះ $e^{x}\\to 0$ កាលណា $x\\to -\\infty$ ។" + D(f"{lim('+oo')}{n}(x)=0") + f"ព្រោះភាគបែងខិតជិត $+\\infty$ ។\nដូចនេះ អាស៊ីមតូតដេកទាំងពីរគឺ $\\boxed{{y={L(kk)}}}$ ត្រង់ $-\\infty$ និង $\\boxed{{y=0}}$ ត្រង់ $+\\infty$ ។"
    return P(prob, sol, f"y={L(kk)},\\ y=0", [check(cl(e, "-oo"), kk, "-inf"), check(cl(e, "oo"), 0, "+inf")])

def rated(p, diff):
    """Fix the difficulty by the form of the row, so one form never carries two levels."""
    p.diff = diff
    return p
def g_asym_ln(rng):
    n = fname(rng); mode = rng.choice(["lnshift", "lnx/x", "lin+lnx/x", "lnratio"]); a = rng.randint(-3, 4); b = rng.randint(-3, 4); s = rng.choice([1, 2, -1])
    if mode == "lnshift":
        e = sp.log(x - a) + b; t = L(e); h = -sp.oo
        prob = W(rng, f"រកដែនកំណត់នៃ ${n}(x)={t}$ រួចបង្ហាញថាក្រាបមានអាស៊ីមតូតឈរ ។", f"គណនា ${lim(a,'+')}{n}(x)$ ដែល ${n}(x)={t}$ ។ តើលទ្ធផលនេះបញ្ជាក់អ្វីអំពីក្រាប ?")
        sol = f"${n}$ កំណត់លុះត្រាតែ ${L(x-a)}>0$ គឺ $D={iv(a,sp.oo)}$ ។\nកាលណា $x\\to {L(a)}^{{+}}$ គេបាន ${L(x-a)}\\to 0^{{+}}$ ហើយ $\\ln\\left({L(x-a)}\\right)\\to -\\infty$ ។" + D(f"{lim(a,'+')}{n}(x)=-\\infty") + f"ដូចនេះ បន្ទាត់ $\\boxed{{x={L(a)}}}$ ជាអាស៊ីមតូតឈរនៃក្រាប ។"
        return rated(P(prob, sol, f"x={L(a)}", [check(cl(e, a, "+"), "-oo", "right")]), "easy")
    if mode == "lnx/x":
        e = sp.log(x) / x + b; t = fr("\\ln x", "x") + ("" if b == 0 else ("+" if b > 0 else "") + L(b))
        prob = f"គេឱ្យ ${n}(x)={t}$ ចំពោះ $x>0$ ។ គណនា ${lim(0,'+')}{n}(x)$ និង ${lim('+oo')}{n}(x)$ (យើងដឹងថា ${lim('+oo')}{fr(chr(92)+'ln x','x')}=0$) ។ រួចទាញរកអាស៊ីមតូត ។"
        sol = f"កាលណា $x\\to 0^{{+}}$ យើងមាន $\\ln x\\to -\\infty$ ហើយ ${fr(1,'x')}\\to +\\infty$ ដូច្នេះ ${lim(0,'+')}{n}(x)=-\\infty$ ។\nតាមលីមីតដែលឱ្យ ${lim('+oo')}{n}(x)={L(b)}$ ។\nដូចនេះ អាស៊ីមតូតឈរ $\\boxed{{x=0}}$ និងអាស៊ីមតូតដេក $\\boxed{{y={L(b)}}}$ ។"
        return rated(P(prob, sol, f"x=0,\\ y={L(b)}", [check(cl(e, 0, "+"), "-oo", "0+"), check(cl(e, "oo"), b, "+inf")]), "medium")
    if mode == "lin+lnx/x":
        ln = s * x + b; e = ln + sp.log(x) / x; t = L(ln) + "+" + fr("\\ln x", "x")
        prob = f"គេឱ្យ ${n}(x)={t}$ ដែល $x>0$ ។ បង្ហាញថា $y={L(ln)}$ ជាអាស៊ីមតូតទ្រេតនៃ $(C)$ ។ (យើងដឹងថា ${lim('+oo')}{fr(chr(92)+'ln x','x')}=0$)"
        sol = f"${n}(x)-\\left({L(ln)}\\right)={fr(chr(92)+'ln x','x')}$ ដូច្នេះ" + D(f"{lim('+oo')}\\left[{n}(x)-\\left({L(ln)}\\right)\\right]=0") + f"ដូចនេះ បន្ទាត់ $\\boxed{{y={L(ln)}}}$ ជាអាស៊ីមតូតទ្រេតនៃ $(C)$ ត្រង់ $+\\infty$ ។"
        return rated(P(prob, sol, f"y={L(ln)}", [check(cl(e - ln, "oo"), 0, "slant")]), "medium")
    p, q = sorted(rng.sample(range(-4, 5), 2))  # domain x<p or x>q
    e = sp.log((x - q) / (x - p)); t = "\\ln\\left(" + fr(x - q, x - p) + "\\right)"
    prob = f"រកដែនកំណត់នៃ ${n}(x)={t}$ រួចរកអាស៊ីមតូតទាំងអស់នៃក្រាប ។"
    sol = f"${n}$ កំណត់លុះត្រាតែ ${fr(x-q,x-p)}>0$ ។ តារាងសញ្ញាឱ្យ $D={iv(-sp.oo,p)}\\cup{iv(q,sp.oo)}$ ។\nកាលណា $x\\to\\pm\\infty$ ផលធៀបខិតជិត $1$ ហើយ $\\ln 1=0$ ដូច្នេះ" + D(f"{lim('+oo')}{n}(x)={lim('-oo')}{n}(x)=0")
    sol += f"បន្ទាត់ $y=0$ ជាអាស៊ីមតូតដេក ។\nកាលណា $x\\to {L(q)}^{{+}}$ ផលធៀបខិតជិត $0^{{+}}$ គេបាន ${lim(q,'+')}{n}(x)=-\\infty$ ។\nកាលណា $x\\to {L(p)}^{{-}}$ ផលធៀបខិតជិត $+\\infty$ គេបាន ${lim(p,'-')}{n}(x)=+\\infty$ ។\nដូចនេះ អាស៊ីមតូតគឺ $\\boxed{{y=0,\\ x={L(p)},\\ x={L(q)}}}$ ។"
    return rated(P(prob, sol, f"y=0,\\ x={L(p)},\\ x={L(q)}", [check(cl(e, "oo"), 0, "+inf"), check(cl(e, "-oo"), 0, "-inf"), check(cl(e, q, "+"), "-oo", "q+"), check(cl(e, p, "-"), "oo", "p-")]), "hard")

def g_asym_root(rng):
    n = fname(rng); mode = rng.choice(["slantp", "slantm", "minus"]); p = rng.choice([-6, -4, -2, 2, 4, 6]); q = p * p // 4 + rng.choice([1, 2, 3, 5])
    if mode == "minus":
        q = rng.choice([1, 2, 3, 4, 5, 9]); sq = sp.sqrt(x**2 + q); e = sq - x
        prob = W(rng, f"គណនា ${lim('+oo')}\\left({L(sq)}-x\\right)$ រួចទាញរកអាស៊ីមតូតដេកនៃក្រាប $y={L(sq)}-x$ ត្រង់ $+\\infty$ ។", f"បង្ហាញថាក្រាបនៃ ${n}(x)={L(sq)}-x$ មានអាស៊ីមតូតដេកត្រង់ $+\\infty$ ។")
        sol = "កន្សោមមានរាងមិនកំណត់ $\\infty-\\infty$ ។ គុណនឹងកន្សោមឆ្លាស់ ៖" + chain(lim('+oo') + "\\left(" + L(sq) + "-x\\right)", [lim('+oo') + fr(f"\\left({L(sq)}-x\\right)\\left({L(sq)}+x\\right)", L(sq) + "+x"), lim('+oo') + fr(q, L(sq) + "+x")], 0) + f"ព្រោះភាគបែងខិតជិត $+\\infty$ ។\nដូចនេះ បន្ទាត់ $\\boxed{{y=0}}$ ជាអាស៊ីមតូតដេកត្រង់ $+\\infty$ ។"
        return P(prob, sol, "y=0", [check(cl(e, "oo"), 0, "+inf")])
    Q = x**2 + p * x + q; sq = sp.sqrt(Q); r = p // 2
    plus = mode == "slantp"; ln = x + r if plus else -x - r; inf = "+oo" if plus else "-oo"; infs = "oo" if plus else "-oo"; it = "+\\infty" if plus else "-\\infty"
    prob = W(rng, f"បង្ហាញថាបន្ទាត់ $y={L(ln)}$ ជាអាស៊ីមតូតទ្រេតនៃក្រាប ${n}(x)={L(sq)}$ ត្រង់ ${it}$ ។", f"គេឱ្យ ${n}(x)={L(sq)}$ ។ គណនា ${lim(inf)}\\left[{n}(x)-\\left({L(ln)}\\right)\\right]$ រួចសន្និដ្ឋាន ។")
    rem = q - r * r
    sol = f"ពហុធា ${L(Q)}$ វិជ្ជមានជានិច្ច ព្រោះ $\\Delta={L(p*p-4*q)}<0$ ដូច្នេះ $D=\\mathbb{{R}}$ ។\nគុណនឹងកន្សោមឆ្លាស់ ៖" + D(f"{n}(x)-\\left({L(ln)}\\right)={fr(L(Q)+'-'+chr(92)+'left('+L(ln)+chr(92)+'right)^{2}',L(sq)+'+'+chr(92)+'left('+L(ln)+chr(92)+'right)')}={fr(rem,L(sq)+'+'+chr(92)+'left('+L(ln)+chr(92)+'right)')}")
    sol += f"កាលណា $x\\to {it}$ ភាគបែងខិតជិត $+\\infty$ ព្រោះ ${L(ln)}\\to +\\infty$ ដូច្នេះលីមីតស្មើ $0$ ។\nដូចនេះ បន្ទាត់ $\\boxed{{y={L(ln)}}}$ ជាអាស៊ីមតូតទ្រេតត្រង់ ${it}$ ។"
    return P(prob, sol, f"y={L(ln)}", [check(cl(sq - ln, infs), 0, "slant")])

def g_asym_find(rng):
    n = fname(rng); h = rng.choice([-2, -1, 1, 2, 3]); d = rng.choice([-3, -2, -1, 1, 2, 4]); px = rng.choice([v for v in range(-3, 6) if v != d]); py = h + rng.choice([-3, -2, -1, 1, 2, 3]) * 1
    # f=(h x + b)/(x-d), f(px)=py => b = py(px-d)-h px
    b = py * (px - d) - h * px; e = (h * x + b) / (x - d)
    if h * d + b == 0: return None
    prob = W(rng, f"គេឱ្យ ${n}(x)={fr('ax+b','x+c')}$ ។ កំណត់ $a$, $b$, $c$ ដោយដឹងថាក្រាបមានអាស៊ីមតូតឈរ $x={L(d)}$ អាស៊ីមតូតដេក $y={L(h)}$ និងកាត់តាមចំណុច $A({L(px)};{L(py)})$ ។", f"រកចំនួនពិត $a$, $b$, $c$ ដើម្បីឱ្យក្រាបនៃ ${n}(x)={fr('ax+b','x+c')}$ មានបន្ទាត់ $x={L(d)}$ និង $y={L(h)}$ ជាអាស៊ីមតូត ហើយ ${n}({L(px)})={L(py)}$ ។")
    sol = f"ភាគបែងត្រូវស្មើសូន្យត្រង់ $x={L(d)}$ ៖ ${L(d)}+c=0$ នាំឱ្យ $c={L(-d)}$ ។\nលីមីតត្រង់អនន្តគឺ $a$ ៖ ${lim('+oo')}{fr('ax+b','x+c')}=a$ ដូច្នេះ $a={L(h)}$ ។\nក្រាបកាត់តាមចំណុចដែលឱ្យ ៖" + D(f"{fr(L(h*px)+'+b',L(px-d))}={L(py)}\\Leftrightarrow b={L(b)}") + f"ផ្ទៀងផ្ទាត់ ៖ ភាគយកមិនស្មើសូន្យត្រង់ $x={L(d)}$ ព្រោះ ${L(h*d+b)}\\neq 0$ ។\nដូចនេះ $\\boxed{{a={L(h)},\\ b={L(b)},\\ c={L(-d)}}}$ ។"
    return P(prob, sol, f"a={L(h)},\\ b={L(b)},\\ c={L(-d)}", [check(cl(e, "oo"), h, "ha"), check(f"subs({e},x,{px})", py, "point"), check(f"sign(Abs({cl(e,d,'+')}))", 1, "pole") if False else check(f"Abs({cl(e,d,'+')})", "oo", "pole")])

def g_from_limits(rng):
    n = fname(rng); a = rng.randint(-4, 4); b = rng.randint(-3, 3); c = rng.choice([v for v in range(-4, 5) if v != a]); s1 = rng.choice(["+\\infty", "-\\infty"]); s2 = rng.choice(["+\\infty", "-\\infty"])
    # hidden model
    sg1 = 1 if s1[0] == "+" else -1; sg2 = 1 if s2[0] == "+" else -1
    e = b + sg1 / (x - a) ** 2 ; L1 = sp.oo * sg1
    pool = [f"{lim(a,'-')}{n}(x)={s1}", f"{lim(a,'+')}{n}(x)={s1}", f"{lim('+oo')}{n}(x)={L(b)}", f"{lim('-oo')}{n}(x)={L(b)}"]
    extra = rng.random() < .5
    prob = f"អនុគមន៍ ${n}$ មានក្រាប $(C)$ ។ គេដឹងថា ៖" + D(",\\quad ".join(pool[:2])) + D(",\\quad ".join(pool[2:])) + W(rng, "ទាញរកអាស៊ីមតូតនៃ $(C)$ ។", "តើក្រាប $(C)$ មានអាស៊ីមតូតអ្វីខ្លះ ? សរសេរសមីការរបស់វា ។") + (f"\nផ្តល់ឧទាហរណ៍នៃអនុគមន៍មួយដែលផ្ទៀងផ្ទាត់លីមីតទាំងនេះ ។" if extra else "")
    sol = f"ដោយ ${lim(a,'-')}{n}(x)={s1}$ និង ${lim(a,'+')}{n}(x)={s1}$ នោះ ${n}(x)$ ខិតទៅរកអនន្តត្រង់ ${L(a)}$ ដូច្នេះ បន្ទាត់ $x={L(a)}$ ជាអាស៊ីមតូតឈរ ។\nដោយ ${lim('+oo')}{n}(x)={lim('-oo')}{n}(x)={L(b)}$ លីមីតត្រង់អនន្តជាចំនួនកំណត់ ដូច្នេះ បន្ទាត់ $y={L(b)}$ ជាអាស៊ីមតូតដេក ។\n"
    if extra: sol += f"ឧទាហរណ៍ ${n}(x)={L(e)}$ ផ្ទៀងផ្ទាត់លីមីតទាំងបួន ព្រោះ ${fr(sg1,(x-a)**2)}$ ខិតជិត ${s1}$ ត្រង់ ${L(a)}$ និងខិតជិត $0$ ត្រង់អនន្ត ។\n"
    sol += f"ដូចនេះ $(C)$ មានអាស៊ីមតូតឈរ $\\boxed{{x={L(a)}}}$ និងអាស៊ីមតូតដេក $\\boxed{{y={L(b)}}}$ ។"
    return P(prob, sol, f"x={L(a)},\\ y={L(b)}", [check(cl(e, a, "-"), L1, "model left"), check(cl(e, a, "+"), L1, "model right"), check(cl(e, "oo"), b, "model +inf"), check(cl(e, "-oo"), b, "model -inf")])

def g_from_table(rng):
    n = fname(rng); k = rng.choice([1, 2, 3, 4]); s = rng.randint(-3, 3); e = x + s + k * k / x; mode = rng.choice(["ext", "homo"])
    if mode == "homo":
        d = rng.randint(-3, 3); h = rng.randint(-3, 3); sg = rng.choice([1, -1]); e = h + sg / (x - d)
        tb = variation_table(["-\\infty", L(d), "+\\infty"], ["", "-" if sg > 0 else "+", "\\|", "-" if sg > 0 else "+", ""],
                             [L(h), "\\searrow" if sg > 0 else "\\nearrow", ("-\\infty\\ \\|\\ +\\infty" if sg > 0 else "+\\infty\\ \\|\\ -\\infty"), "\\searrow" if sg > 0 else "\\nearrow", L(h)], n)
        l, r = -sp.oo * sg, sp.oo * sg
        prob = f"តារាងអថេរភាពនៃអនុគមន៍ ${n}$ មានដូចខាងក្រោម ៖" + D(tb) + f"ផ្អែកលើតារាង សរសេរលីមីតនៃ ${n}$ ត្រង់ $\\pm\\infty$ និងត្រង់ ${L(d)}$ រួចទាញរកអាស៊ីមតូត ។"
        sol = f"អានពីតារាង ៖" + D(f"{lim('-oo')}{n}(x)={L(h)},\\quad {lim('+oo')}{n}(x)={L(h)}") + D(f"{lim(d,'-')}{n}(x)={L(l)},\\quad {lim(d,'+')}{n}(x)={L(r)}") + f"លីមីតត្រង់អនន្តជាចំនួនកំណត់ ដូច្នេះបន្ទាត់ $y={L(h)}$ ជាអាស៊ីមតូតដេក ។ ${n}(x)$ ខិតទៅរកអនន្តត្រង់ ${L(d)}$ ដូច្នេះបន្ទាត់ $x={L(d)}$ ជាអាស៊ីមតូតឈរ ។\nដូចនេះ $\\boxed{{x={L(d)}}}$ និង $\\boxed{{y={L(h)}}}$ ។"
        return P(prob, sol, f"x={L(d)},\\ y={L(h)}", [check(cl(e, d, "-"), l, "left"), check(cl(e, d, "+"), r, "right"), check(cl(e, "oo"), h, "+inf")], tables=[dict(type="variation_table", latex=tb, image=None, alt_km=f"តារាងអថេរភាពដែលមានតម្លៃមិនកំណត់ត្រង់ $x={L(d)}$ ។")])
    M, mn = s - 2 * k, s + 2 * k
    tb = variation_table(["-\\infty", L(-k), "0", L(k), "+\\infty"], ["", "+", "0", "-", "\\|", "-", "0", "+", ""],
                         ["-\\infty", "\\nearrow", L(M), "\\searrow", "-\\infty\\ \\|\\ +\\infty", "\\searrow", L(mn), "\\nearrow", "+\\infty"], n)
    m_ = rng.choice([mn + 1, M - 1, s])
    cnt = 2 if (m_ > mn or m_ < M) else 0
    prob = f"តារាងអថេរភាពនៃអនុគមន៍ ${n}$ ឱ្យដូចខាងក្រោម ៖" + D(tb) + f"១. សរសេរលីមីតត្រង់ $0^{{-}}$ និងត្រង់ $0^{{+}}$ រួចបញ្ជាក់អាស៊ីមតូតឈរ ។\n២. តើអនុគមន៍ជាប់លើចន្លោះ $(0,+\\infty)$ ឬទេ ?\n៣. រកចំនួនឫសនៃសមីការ ${n}(x)={L(m_)}$ ។"
    sol = f"១. ពីតារាង ${lim(0,'-')}{n}(x)=-\\infty$ និង ${lim(0,'+')}{n}(x)=+\\infty$ ដូច្នេះបន្ទាត់ $x=0$ ជាអាស៊ីមតូតឈរ ។\n២. តារាងមិនមានតម្លៃមិនកំណត់លើ $(0,+\\infty)$ ហើយព្រួញគូរបន្ត ដូច្នេះ ${n}$ ជាប់លើចន្លោះនេះ ។\n"
    if cnt:
        wh = f"${L(m_)}>{L(mn)}$" if m_ > mn else f"${L(m_)}<{L(M)}$"
        sol += f"៣. ដោយ {wh} " + ("បន្ទាត់ដេកកាត់ផ្នែកខាងស្តាំពីរដង ហើយមិនកាត់ផ្នែកខាងឆ្វេងទេ ។" if m_ > mn else "បន្ទាត់ដេកកាត់ផ្នែកខាងឆ្វេងពីរដង ហើយមិនកាត់ផ្នែកខាងស្តាំទេ ។") + f" តាម{TV} លើចន្លោះកើន ឬចុះនីមួយៗ មានឫសមួយ ។\nដូចនេះ សមីការមាន $\\boxed{{2}}$ ឫស ។"
    else:
        sol += f"៣. ដោយ ${L(M)}<{L(m_)}<{L(mn)}$ តម្លៃនេះធំជាងអតិបរមាធៀបនៃផ្នែកខាងឆ្វេង ហើយតូចជាងអប្បបរមាធៀបនៃផ្នែកខាងស្តាំ ។\nដូចនេះ សមីការមាន $\\boxed{{0}}$ ឫស ។".replace("អតិបរមាធៀប", "អតិបរមា").replace("អប្បបរមាធៀប", "អប្បបរមា")
    q = sp.Poly(x**2 + (s - m_) * x + k * k, x); nreal = len(set(sp.real_roots(q)))
    return P(prob, sol, str(cnt), [check(cl(e, 0, "-"), "-oo", "left"), check(cl(e, 0, "+"), "oo", "right"), check(f"subs({e},x,{k})", mn, "min"), check(f"subs({e},x,{-k})", M, "max"), check(str(nreal), cnt, "number of real roots")], tables=[dict(type="variation_table", latex=tb, image=None, alt_km="តារាងអថេរភាពដែលមានអតិបរមា អប្បបរមា និងតម្លៃមិនកំណត់ត្រង់ $x=0$ ។")])

def g_position(rng):
    n = fname(rng); a, b, k, d, num, e = slant_data(rng); ln = a * x + b; t = fr(num, x - d)
    prob = W(rng, f"គេឱ្យ ${n}(x)={t}$ មានក្រាប $(C)$ ។ បង្ហាញថាបន្ទាត់ $(d):y={L(ln)}$ ជាអាស៊ីមតូតទ្រេត រួចសិក្សាទីតាំងធៀបនៃ $(C)$ និង $(d)$ ។", f"សិក្សាទីតាំងនៃក្រាប $(C)$ នៃ $y={t}$ ធៀបនឹងអាស៊ីមតូតទ្រេតរបស់វា ។")
    above = f"$x>{L(d)}$" if k > 0 else f"$x<{L(d)}$"; below = f"$x<{L(d)}$" if k > 0 else f"$x>{L(d)}$"
    sol = (f"តាង ${n}(x)={t}$ ។\n" if prob.startswith("សិក្សា") else "") + canon_txt(a, b, k, d, num) + f"យើងមាន ${n}(x)-\\left({L(ln)}\\right)={fr(k,x-d)}$ ។ ផលដកនេះខិតជិត $0$ ត្រង់ $\\pm\\infty$ ដូច្នេះ $y={L(ln)}$ ជាអាស៊ីមតូតទ្រេត ។\n" + (f"ដោយភាគយក ${L(k)}$ វិជ្ជមាន ផលដកមានសញ្ញាដូច ${L(x-d)}$ ៖\n" if k > 0 else f"ដោយភាគយក ${L(k)}$ អវិជ្ជមាន ផលដកមានសញ្ញាផ្ទុយពី ${L(x-d)}$ ៖\n")
    sol += f"ចំពោះ {above} ផលដកវិជ្ជមាន នោះ $(C)$ នៅលើ $(d)$ ។\nចំពោះ {below} ផលដកអវិជ្ជមាន នោះ $(C)$ នៅក្រោម $(d)$ ។\nដូចនេះ $(C)$ មិនកាត់ $(d)$ ទេ ហើយ $(C)$ នៅលើ $(d)$ ចំពោះ $\\boxed{{{above.strip('$')}}}$ ។"
    p1 = d + 1; 
    return P(prob, sol, above.strip("$"), [check(cl(e - ln, "oo"), 0, "slant"), check(f"sign(subs({e-ln},x,{p1}))", 1 if k > 0 else -1, "sign right of pole"), check(f"sign(subs({e-ln},x,{d-1}))", -1 if k > 0 else 1, "sign left of pole")])

# ---------- graphs ----------
def pgf_expr(e):
    return str(e).replace("**", "^").replace("log(", "ln(").replace("Abs(", "abs(")
def tikz(sp_):
    xmin, xmax, ymin, ymax = [float(v) for v in sp_["win"]]
    extra = ""
    for e, a, b in sp_.get("pieces", []):
        extra += f"\\addplot[thick,domain={float(a):g}:{float(b):g},samples=120] {{{pgf_expr(e)}}};\n"
    for px, py in sp_.get("holes", []):
        extra += f"\\addplot[only marks,mark=o,mark options={{fill=white}}] coordinates {{({float(px):g},{float(py):g})}};\n"
    for px, py in sp_.get("dots", []):
        extra += f"\\addplot[only marks,mark=*] coordinates {{({float(px):g},{float(py):g})}};\n"
    for c in sp_.get("va", []):
        extra += f"\\draw[dashed] (axis cs:{float(c):g},{ymin:g}) -- (axis cs:{float(c):g},{ymax:g});\n"
    for c in sp_.get("ha", []):
        extra += f"\\draw[dashed] (axis cs:{xmin:g},{float(c):g}) -- (axis cs:{xmax:g},{float(c):g});\n"
    for e in sp_.get("slant", []):
        extra += f"\\addplot[dashed,domain={xmin:g}:{xmax:g}] {{{pgf_expr(e)}}};\n"
    return ("\\begin{tikzpicture}\n\\begin{axis}[axis lines=middle,xlabel=$x$,ylabel=$y$,"
            f"xmin={xmin:g},xmax={xmax:g},ymin={ymin:g},ymax={ymax:g},grid=both]\n" + extra + "\\end{axis}\n\\end{tikzpicture}")
def draw(rid, sp_):
    xmin, xmax, ymin, ymax = [float(v) for v in sp_["win"]]
    fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=110)
    for e, a, b in sp_.get("pieces", []):
        fn = sp.lambdify(x, e, "numpy"); xs = np.linspace(float(a), float(b), 500)
        with np.errstate(all="ignore"):
            ys = np.broadcast_to(np.asarray(fn(xs), dtype=float), xs.shape).copy()
        ys[(ys > ymax + 3) | (ys < ymin - 3)] = np.nan
        ax.plot(xs, ys, lw=1.8, color="#1f4e9c")
    for c in sp_.get("va", []): ax.axvline(float(c), ls="--", lw=.9, color="gray")
    for c in sp_.get("ha", []): ax.axhline(float(c), ls="--", lw=.9, color="gray")
    for e in sp_.get("slant", []):
        xs = np.array([xmin, xmax]); fn = sp.lambdify(x, e, "numpy"); ax.plot(xs, fn(xs), ls="--", lw=.9, color="gray")
    for px, py in sp_.get("holes", []):
        ax.plot([float(px)], [float(py)], "o", ms=6, mfc="white", mec="#1f4e9c", zorder=5)
    for px, py in sp_.get("dots", []):
        ax.plot([float(px)], [float(py)], "o", ms=5, color="#1f4e9c", zorder=6)
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    for sd in ("top", "right"): ax.spines[sd].set_visible(False)
    if ymin < 0 < ymax: ax.spines["bottom"].set_position("zero")
    if xmin < 0 < xmax: ax.spines["left"].set_position("zero")
    ax.set_xticks(range(int(np.ceil(xmin)), int(xmax) + 1)); ax.set_yticks(range(int(np.ceil(ymin)), int(ymax) + 1, 1 if ymax - ymin <= 14 else 2))
    ax.tick_params(labelsize=7); ax.grid(alpha=.25)
    rel_ = f"diagrams/{rid}.png"; fig.savefig(os.path.join(ROOT, rel_), bbox_inches="tight"); plt.close(fig)
    return rel_

# ---------- reading graphs: a scene is a list of segments ----------
def seg(e, a, b): return dict(e=e, a=a, b=b)
def scene(rng):
    k = rng.choice(["hole", "hole_dot", "jump", "jump2", "va", "mix", "mix2", "corner", "ha"])
    win = (-6, 6, -6, 6); dots, va, ha = [], [], []; holes = []
    def line_through(px, py, m): return py + m * (x - px)
    if k in ("hole", "hole_dot"):
        c = rng.randint(-3, 3); v = rng.randint(-2, 3); e = rng.choice([line_through(c, v, rng.choice([1, -1, R(1, 2), 2])), v + (x - c)**2, v - (x - c)**2 / 2])
        segs = [seg(e, -6, c), seg(e, c, 6)]
        if k == "hole_dot": w = v + rng.choice([-3, -2, 2, 3]); dots = {c: w}
        else: dots = {}
        brk = [c]
    elif k in ("jump", "jump2", "corner"):
        c = rng.randint(-2, 2); v1 = rng.randint(-3, 3); v2 = v1 + rng.choice([-4, -3, -2, 2, 3, 4]) if k != "corner" else v1
        e1 = line_through(c, v1, rng.choice([1, R(1, 2), -1, 2])); e2 = rng.choice([line_through(c, v2, rng.choice([-1, R(1, 2), 1, -R(1, 2)])), sp.Integer(v2) if v2 else line_through(c, v2, 1), v2 + (x - c)**2 / 2])
        segs = [seg(e1, -6, c), seg(e2, c, 6)]
        dots = {c: rng.choice([v1, v2]) if k != "jump2" else v1 + rng.choice([1, -1]) if abs(v2 - v1) != 1 and v1 + 1 != v2 else v1}
        brk = [c]
    elif k in ("va", "ha"):
        c = rng.randint(-2, 2); h = rng.randint(-2, 2); s = rng.choice([1, -1, 2, -2])
        e = h + s / (x - c) if k == "ha" else h + s / (x - c)**2
        segs = [seg(e, -6, c), seg(e, c, 6)]; va = [c]; ha = [h]; dots = {}; brk = [c]
    elif k == "mix":
        c1 = rng.randint(-4, -2); c2 = rng.randint(1, 3); h = rng.randint(-2, 2); v = rng.randint(-2, 3); w = v + rng.choice([-3, 2, 3])
        s = rng.choice([1, -1]); e1 = h + s / (x - c1); e2 = line_through(c2, v, rng.choice([R(1, 2), 1, -R(1, 2)])); e3 = w + R(1, 2) * (x - c2)
        segs = [seg(e1, -6, c1), seg(e2, c1, c2), seg(e3, c2, 6)]; va = [c1]; dots = {c2: v}; brk = [c1, c2]
        ha = []
        # the left branch has horizontal asymptote; right branch stays a line, so only +/-inf left is asked
    else:  # mix2: hole then va then decaying branch
        c1 = rng.randint(-4, -2); c2 = rng.randint(1, 3); v = rng.randint(-2, 3); h = rng.randint(-2, 2); s = rng.choice([2, -2, 1])
        e1 = line_through(c1, v, rng.choice([R(1, 2), 1, -1])); e2 = e1; e3 = h + s / (x - c2)
        va_e = e1
        segs = [seg(e1, -6, c1), seg(e1, c1, c2 - 0), seg(e3, c2, 6)]; va = [c2]; dots = {c1: v + rng.choice([2, -2])} if rng.random() < .5 else {}; brk = [c1, c2]; ha = []
        if rng.random() < .5: pass
    return dict(kind=k, segs=segs, dots=dots, va=va, ha=ha, brk=brk, win=win)
def side_lim(sc, c, side):
    for s in sc["segs"]:
        if side == "-" and s["b"] == c: return sp.limit(s["e"], x, c, "-"), s["e"]
        if side == "+" and s["a"] == c: return sp.limit(s["e"], x, c, "+"), s["e"]
def g_read(rng):
    sc = scene(rng); n = "f"; brk = sc["brk"]; c = rng.choice(brk)
    pieces = []; holes = []; dots = []
    for s in sc["segs"]:
        a = s["a"] + (.03 if s["a"] in sc["va"] else 0); b = s["b"] - (.03 if s["b"] in sc["va"] else 0); pieces.append((s["e"], a, b))
    seen_h = set()
    for b_ in brk:
        if b_ in sc["va"]:
            for sd_ in "-+":
                v = side_lim(sc, b_, sd_)[0]
                if v.is_finite: holes.append((b_, v))
            continue
        l, _ = side_lim(sc, b_, "-"); r, _ = side_lim(sc, b_, "+"); val = sc["dots"].get(b_)
        for v in {l, r}:
            if val is None or v != val: holes.append((b_, v))
        if val is not None: dots.append((b_, val))
    if any(abs(v) > 5.5 for _, v in holes + dots): return None
    spec = dict(pieces=pieces, holes=holes, dots=dots, va=sc["va"], ha=sc["ha"], win=sc["win"], where="p")
    # questions
    qs, ss, ch, an = [], [], [], []
    l, el = side_lim(sc, c, "-"); r, er = side_lim(sc, c, "+"); val = sc["dots"].get(c)
    ch += [check(cl(el, c, "-"), l, "left limit of the drawn branch"), check(cl(er, c, "+"), r, "right limit of the drawn branch")]
    q1 = f"${lim(c,'-')}f(x)$ និង ${lim(c,'+')}f(x)$"
    qs.append(W(rng, f"អានពីក្រាប រកតម្លៃ {q1} ។", f"តាមរយៈក្រាប កំណត់ {q1} ។", f"ប្រាប់ {q1} ។"))
    ss.append(W(rng, f"កាលណា $x$ ខិតជិត ${L(c)}$ ពីខាងឆ្វេង ខ្សែកោងទៅរក", f"នៅខាងឆ្វេង $x={L(c)}$ ផ្នែកក្រាបទៅរក") + (f"អរដោនេ ${L(l)}$" if l.is_finite else " $" + L(l) + "$") + f" ដូច្នេះ ${lim(c,'-')}f(x)={L(l)}$ ។ នៅខាងស្តាំវាទៅរក" + (f"អរដោនេ ${L(r)}$" if r.is_finite else " $" + L(r) + "$") + f" ដូច្នេះ ${lim(c,'+')}f(x)={L(r)}$ ។")
    an.append(f"{lim(c,'-')}f(x)={L(l)},\\ {lim(c,'+')}f(x)={L(r)}")
    qs.append(W(rng, f"តើ $f$ មានលីមីតត្រង់ $x={L(c)}$ ឬទេ ?", f"តើលីមីត ${lim(c)}f(x)$ មានឬទេ ?"))
    if l == r and l.is_finite: ss.append(f"លីមីតឆ្វេង និងលីមីតស្តាំស្មើគ្នា ដូច្នេះ ${lim(c)}f(x)={L(l)}$ ។")
    elif l == r: ss.append(f"លីមីតទាំងពីរស្មើ ${L(l)}$ ដូច្នេះលីមីតមិនមែនជាចំនួនកំណត់ទេ ។")
    else: ss.append(f"លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ដូច្នេះ $f$ គ្មានលីមីតត្រង់ $x={L(c)}$ ទេ ។")
    qs.append(W(rng, f"រក $f({L(c)})$ បើមាន ។ រួចសិក្សាភាពជាប់ត្រង់ $x={L(c)}$ ។", f"តើ $f$ ជាប់ត្រង់ $x={L(c)}$ ឬទេ ? ពន្យល់ ។"))
    cont = val is not None and l == r == val
    if val is None: ss.append(f"ក្រាបគ្មានចំណុចពេញត្រង់ $x={L(c)}$ ដូច្នេះ $f({L(c)})$ មិនកំណត់ ហើយ $f$ មិនជាប់ត្រង់ចំណុចនេះទេ ។")
    elif cont: ss.append(f"ចំណុចពេញបង្ហាញថា $f({L(c)})={L(val)}$ ស្មើនឹងលីមីត ដូច្នេះ $f$ ជាប់ត្រង់ $x={L(c)}$ ។")
    else: ss.append(f"ចំណុចពេញបង្ហាញថា $f({L(c)})={L(val)}$ ។ " + ("តម្លៃនេះមិនស្មើនឹងលីមីត" if l == r else "ដោយគ្មានលីមីត") + f" ដូច្នេះ $f$ មិនជាប់ត្រង់ $x={L(c)}$ ទេ ។")
    an.append(f"{'f\\ \\text{ជាប់ត្រង់}' if cont else 'f\\ \\text{មិនជាប់ត្រង់}'}\\ x={L(c)}")
    if sc["kind"] in ("va", "ha"):
        h = sc["ha"][0]; qs.append(f"គណនា ${lim('-oo')}f(x)$ និង ${lim('+oo')}f(x)$ ។ រួចសរសេរសមីការអាស៊ីមតូតនៃក្រាប ។")
        ss.append(f"ក្រាបខិតជិតបន្ទាត់ដាច់ៗ $y={L(h)}$ ត្រង់អនន្តទាំងពីរ ដូច្នេះ ${lim('-oo')}f(x)={lim('+oo')}f(x)={L(h)}$ ។ ដូច្នេះមានអាស៊ីមតូតដេក $y={L(h)}$ និងអាស៊ីមតូតឈរ $x={L(c)}$ ។")
        ch += [check(cl(sc["segs"][1]["e"], "oo"), h, "+inf"), check(cl(sc["segs"][0]["e"], "-oo"), h, "-inf")]; an.append(f"x={L(c)},\\ y={L(h)}")
    elif len(brk) == 2:
        qs.append("រកគ្រប់តម្លៃ $x$ ក្នុងរូបដែល $f$ មិនជាប់ ។")
        bad_ = []
        for b_ in brk:
            ll, _ = side_lim(sc, b_, "-"); rr, _ = side_lim(sc, b_, "+"); vv = sc["dots"].get(b_)
            if not (vv is not None and ll == rr == vv): bad_.append(b_)
        ss.append("មើលតាមក្រាប ខ្សែកោងដាច់ត្រង់ " + " និង ".join(f"$x={L(b_)}$" for b_ in bad_) + " ហើយគូរបន្តនៅកន្លែងផ្សេង ។")
        an.append("x=" + ",\\ ".join(L(b_) for b_ in bad_))
    head = W(rng, "ក្រាបខាងក្រោមជាក្រាបនៃអនុគមន៍ $f$ ។", "រូបខាងក្រោមបង្ហាញក្រាបនៃអនុគមន៍ $f$ ។", "គេឱ្យក្រាបនៃអនុគមន៍ $f$ ដូចរូប ។", "សង្កេតក្រាបនៃ $f$ ក្នុងរូបខាងក្រោម ។")
    head += W(rng, " ចំណុចពេញជាចំណុចរបស់ក្រាប ចំណុចទទេមិនមែនជាចំណុចរបស់ក្រាបទេ ។", " រង្វង់ទទេមានន័យថាចំណុចនោះមិននៅលើក្រាប ។") if (holes or dots) else ""
    if sc["va"]: head += " បន្ទាត់ដាច់ៗជាអាស៊ីមតូត ។"
    style = rng.choice(["k", "k", "n"])
    lab = PARTS[style]
    prob = head + "\n" + "\n".join(f"{lab[i]}. {q}" for i, q in enumerate(qs))
    sol = "\n".join(f"{lab[i]}. {s_}" for i, s_ in enumerate(ss))
    last = "ដូចនេះ $\\boxed{" + an[-1] + "}$ ។"
    sol += "\n" + last
    desc = "ក្រាបមាន " + ("រន្ធ " if holes else "") + ("ការលោត " if len(holes) + len(dots) > 1 else "") + ("អាស៊ីមតូត" if sc["va"] else "")
    desc_ = "ក្រាបនៃ $f$ ដែលមាន" + " និង".join(filter(None, [f"ចំណុចទទេត្រង់ $x={L(holes[0][0])}$" if holes else "", f"អាស៊ីមតូតឈរ $x={L(sc['va'][0])}$" if sc["va"] else "", f"ចំណុចពេញត្រង់ $x={L(dots[0][0])}$" if dots else ""])) + " ។"
    spec["alt"] = desc_
    pr = P(prob, sol, ",\\ ".join(an), ch, fig=spec); pr.key = repr(sc["segs"]) + repr(sc["dots"]) + str(c)
    return pr

# ---------- multi-part items ----------
def build(rng, intro, parts, style=None):
    lab = PARTS[style or rng.choice(["k", "k", "n"])]
    prob = intro + "\n" + "\n".join(f"{lab[i]}. {p[0]}" for i, p in enumerate(parts))
    sol = "\n".join(f"{lab[i]}. {p[1]}" for i, p in enumerate(parts))
    return prob, sol
def m_piecewise_ivt(rng):
    n = "f"; c = rng.choice([1, 2, -1]); b = rng.randint(1, 4); p = ind(rng, c, ["quad", "rn", "rd"] + ([] if c == 0 else ["dos"])); v = p.val
    pv = rng.choice("am"); s = rng.choice([1, 2, 3])
    rt = L(s * (x - c)) + "+" + pv; re_ = s * (x - c) + v
    fx = cases(n, [(p.t, "x<" + L(c)), (rt, "x" + GE + L(c))])
    if p.kind in ("rn", "rd") and False: pass
    k1 = c + 2; val2 = re_.subs(x, k1); k = val2 + 1 if s else 0; k3 = c + 4; val3 = re_.subs(x, k3)
    kk = (val2 + val3) / 2
    intro = opening(rng, n) + "\n" + D(fx)
    pa = (f"គណនា ${lim(c,'-')}{n}(x)$ ។", indchain(rng, p, c, "-"))
    pb = (f"រកតម្លៃ ${pv}$ ដើម្បីឱ្យ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ។", f"យើងមាន ${n}({L(c)})={lim(c,'+')}{n}(x)={pv}$ ។ ${n}$ ជាប់ត្រង់ $x={L(c)}$ លុះត្រាតែ ${pv}={L(v)}$ ។")
    pc = (f"ចំពោះតម្លៃ ${pv}$ នេះ បង្ហាញថាសមីការ ${n}(x)={L(kk)}$ មានឫសក្នុងចន្លោះ $\\left({L(k1)},{L(k3)}\\right)$ ។", f"លើ $[{L(k1)},{L(k3)}]$ អនុគមន៍ជាពហុធាដឺក្រេទីមួយ ដូច្នេះជាប់ ។ ${n}({L(k1)})={L(val2)}$ និង ${n}({L(k3)})={L(val3)}$ ។ ដោយ ${L(kk)}$ នៅចន្លោះតម្លៃទាំងពីរ តាម{TV} សមីការមានឫសក្នុងចន្លោះនេះ ។")
    prob, sol = build(rng, intro, [pa, pb, pc])
    sol += f"\nដូចនេះ $\\boxed{{{pv}={L(v)}}}$ ។"
    return P(prob, sol, f"{pv}={L(v)}", [check(cl(p.e, c, "-"), v, "left"), check(f"subs({re_},x,{k1})", val2, "value"), check(f"subs({re_},x,{k3})", val3, "value"), check(f"sign(({kk}-({val2}))*({kk}-({val3})))", -1, "between")])
def m_rational_study(rng):
    n = "f"; a, b, k, d, num, e = slant_data(rng); ln = a * x + b; t = fr(num, x - d); x0s = sp.solve(num, x)
    tx, l, r = va_lines(n, d, R(k), -1); sa = 1 if a > 0 else -1
    li = sp.oo * sa
    above = f"x>{L(d)}" if k > 0 else f"x<{L(d)}"
    pa = ("រកដែនកំណត់ $D$ នៃ $" + n + "$ ។", f"${n}$ កំណត់លុះត្រាតែ ${L(x-d)}\\neq 0$ ។ ដូច្នេះ $D=\\mathbb{{R}}\\setminus\\{{{L(d)}\\}}$ ។")
    pb = ("គណនាលីមីតនៃ $" + n + f"$ ត្រង់ $-\\infty$ ត្រង់ $+\\infty$ និងត្រង់ ${L(d)}$ ។", D(f"{lim('+oo')}{n}(x)={lim('+oo')}{fr(L(a*x**2),'x')}={L(li)},\\quad {lim('-oo')}{n}(x)={L(-li)}") + "ត្រង់ $x=" + L(d) + "$ ភាគយកខិតជិត $" + L(k) + "$ ៖" + tx)
    pc = (f"កំណត់ចំនួនពិត $a$, $b$, $c$ ដើម្បីឱ្យ ${n}(x)=ax+b+{fr('c',x-d)}$ ។", canon_txt(a, b, k, d, num) + f"គេបាន $a={L(a)}$, $b={L(b)}$, $c={L(k)}$ ។")
    pd = (f"ទាញរកអាស៊ីមតូតទាំងពីរនៃ $(C)$ ។", f"ដោយ ${n}(x)$ ខិតទៅរកអនន្តត្រង់ ${L(d)}$ បន្ទាត់ $x={L(d)}$ ជាអាស៊ីមតូតឈរ ។ ដោយ ${lim('+oo')}{fr(k,x-d)}={lim('-oo')}{fr(k,x-d)}=0$ បន្ទាត់ $(d):y={L(ln)}$ ជាអាស៊ីមតូតទ្រេត ។")
    pe = (f"សិក្សាទីតាំងធៀបនៃ $(C)$ និង $(d)$ ។", f"${n}(x)-\\left({L(ln)}\\right)={fr(k,x-d)}$ ។ បើ ${above}$ ផលដកវិជ្ជមាន ហើយ $(C)$ នៅលើ $(d)$ ។ បើផ្ទុយពីនេះ $(C)$ នៅក្រោម $(d)$ ។")
    y0 = float(ln.subs(x, d))
    prob, sol = build(rng, f"គេឱ្យអនុគមន៍ ${n}(x)={t}$ មានក្រាបតំណាង $(C)$ ។", [pa, pb, pc, pd, pe])
    sol += f"\nដូចនេះ អាស៊ីមតូតគឺ $\\boxed{{x={L(d)}}}$ និង $\\boxed{{y={L(ln)}}}$ ។"
    fig = dict(pieces=[(e, d - 6, d - .05), (e, d + .05, d + 6)], va=[d], slant=[ln], where="s", win=(d - 6, d + 6, y0 - 8, y0 + 8), alt=f"ក្រាប $(C)$ ជាមួយអាស៊ីមតូត $x={L(d)}$ និង $y={L(ln)}$ ។") if rng.random() < .3 else None
    return P(prob, sol, f"x={L(d)},\\ y={L(ln)}", [check(cl(e, "oo"), li, "+inf"), check(cl(e, "-oo"), -li, "-inf"), check(cl(e, d, "-"), l, "left"), check(cl(e, d, "+"), r, "right"), check(cl(e - ln, "oo"), 0, "slant")], fig=fig)
def m_function_root(rng):
    for _ in range(40):
        e, dp, why, dom = fam(rng); br = find_bracket(e, dom)
        if br: break
    else: return None
    n = "f"; a, b = br; ea, eb = e.subs(x, a), e.subs(x, b); inc = float(ea) < 0; dtx = "\\mathbb{R}" if dom is None else iv(*dom)
    lp = sp.limit(e, x, sp.oo); lm = sp.limit(e, x, -sp.oo if dom is None else 0, "+" if dom is None else "+") if dom is None else sp.limit(e, x, 0, "+")
    side = "-oo" if dom is None else 0; sd = "" if dom is None else "+"
    tb = variation_table([("-\\infty" if dom is None else "0"), "+\\infty"], ["", "+" if inc else "-", ""], [L(lm), "\\nearrow" if inc else "\\searrow", L(lp)], n)
    a0 = lim(side, sd); 
    pa = (f"គណនា ${a0}{n}(x)$ និង ${lim('+oo')}{n}(x)$ ។", f"${a0}{n}(x)={L(lm)}$ និង ${lim('+oo')}{n}(x)={L(lp)}$ ។")
    pb = (f"គណនា ${n}'(x)$ រួចសង់តារាងអថេរភាពនៃ ${n}$ ។", f"${n}'(x)={dp}$ ។ ដោយ {why} សញ្ញានៃ ${n}'(x)$ " + ("វិជ្ជមាន" if inc else "អវិជ្ជមាន") + " លើដែនកំណត់ ។" + D(tb))
    pc = (f"បង្ហាញថាសមីការ ${n}(x)=0$ មានឫសតែមួយគត់ $\\alpha$ ហើយ ${L(a)}<\\alpha<{L(b)}$ ។", "យើងមាន " + signs(rng, n, a, b, ea, eb) + f" ។ ${n}$ ជាប់ និង" + ("កើន" if inc else "ចុះ") + f"ជានិច្ច ដូច្នេះតាម{TV} សមីការមានឫសតែមួយគត់ក្នុង $({L(a)},{L(b)})$ ។")
    prob, sol = build(rng, f"គេឱ្យអនុគមន៍ ${n}(x)={L(e)}$ កំណត់លើ ${dtx}$ ។", [pa, pb, pc])
    sol += f"\nដូចនេះ $\\boxed{{{L(a)}<\\alpha<{L(b)}}}$ ។"
    return P(prob, sol, f"{L(a)}<\\alpha<{L(b)}", [check(cl(e, "oo"), lp, "+inf"), check(cl(e, side, sd), lm, "other end"), check(f"sign(subs({e},x,{a}))", -1 if inc else 1, "sign"), check(f"sign(subs({e},x,{b}))", 1 if inc else -1, "sign")], tables=[dict(type="variation_table", latex=tb, image=None, alt_km=f"តារាងអថេរភាពនៃ ${n}$ ។")])
def m_extend_chain(rng):
    c = rng.choice([1, 2, 3, -1, -2]); p = ind(rng, c, ["quad", "dos", "cub", "rr"]); n = "f"
    po = sorted([c, p.other]) if p.kind == "rr" else [c]
    pa = (f"រកដែនកំណត់ $D$ នៃ ${n}$ ។", "ភាគបែងស្មើសូន្យត្រង់ " + " និង ".join(f"$x={L(v)}$" for v in po) + " ។ ដូច្នេះ $D=\\mathbb{R}\\setminus\\{" + ",".join(L(v) for v in po) + "\\}$ ។")
    pb = (f"គណនា ${lim(c)}{n}(x)$ ។", indchain(rng, p, c))
    pc = (f"តើ ${n}$ ជាប់ត្រង់ $x={L(c)}$ ឬទេ ?", f"${n}({L(c)})$ មិនកំណត់ ដូច្នេះ ${n}$ មិនជាប់ត្រង់ $x={L(c)}$ ទេ ។")
    pd = (f"កំណត់អនុគមន៍ $g$ ដែលស្មើនឹង ${n}$ លើ $D$ ហើយជាប់ត្រង់ $x={L(c)}$ ។", D(cases("g", [(p.t, "x" + NE + L(c)), (p.val, f"x={L(c)}")])) + f"ព្រោះ ${lim(c)}g(x)={L(p.val)}=g({L(c)})$ ។")
    prob, sol = build(rng, W(rng, f"គេឱ្យអនុគមន៍ ${n}(x)={p.t}$ ។", f"គេមានអនុគមន៍សនិទាន ${n}(x)={p.t}$ ។"), [pa, pb, pc, pd])
    sol += f"\nដូចនេះ $\\boxed{{g({L(c)})={L(p.val)}}}$ ។"
    return P(prob, sol, f"g({L(c)})={L(p.val)}", [check(cl(p.e, c), p.val, "limit")])
def m_ab_graph(rng):
    n = "f"; c1 = rng.randint(-3, -1); c2 = rng.randint(1, 3); v1 = rng.randint(-2, 3); v2 = rng.randint(-2, 4)
    if (v2 - v1) % (c2 - c1): v2 = v1 + (c2 - c1)
    aa = R(v2 - v1, c2 - c1); bb = v1 - aa * c1
    p1 = v1 + (x - c1)**2 if rng.random() < .5 else v1 + (x - c1); p3 = v2 - (x - c2) if rng.random() < .5 else sp.Integer(v2); p1 = sp.expand(p1); p3 = sp.expand(p3); mid = aa * x + bb
    fx = cases(n, [(p1, "x<" + L(c1)), ("ax+b", L(c1) + LE + "x" + LE + L(c2)), (p3, "x>" + L(c2))])
    A1 = coef(c1, "a") + "+b"; A2 = coef(c2, "a") + "+b"
    pa = (f"គណនា ${lim(c1,'-')}{n}(x)$ និង ${lim(c2,'+')}{n}(x)$ ។", f"${lim(c1,'-')}{n}(x)={L(v1)}$ និង ${lim(c2,'+')}{n}(x)={L(v2)}$ ។")
    pb = (f"រក $a$ និង $b$ ដើម្បីឱ្យ ${n}$ ជាប់លើ $\\mathbb{{R}}$ ។", f"ភាពជាប់ត្រង់ចំណុចភ្ជាប់ទាំងពីរឱ្យ ${A1}={L(v1)}$ និង ${A2}={L(v2)}$ ។ ដោះស្រាយប្រព័ន្ធនេះ គេបាន $a={L(aa)}$ និង $b={L(bb)}$ ។")
    pc = (f"សង់ក្រាបនៃ ${n}$ ។", f"ក្រាបមានបីផ្នែកតភ្ជាប់គ្នា ។ ផ្នែកកណ្តាលជាអង្កត់ភ្ជាប់ចំណុច $({L(c1)};{L(v1)})$ និង $({L(c2)};{L(v2)})$ ។ សង់ផ្នែកនីមួយៗតាមរូបមន្តរបស់វា ដូចរូប ។")
    prob, sol = build(rng, opening(rng, n) + "\n" + D(fx), [pa, pb, pc])
    sol += f"\nដូចនេះ $\\boxed{{a={L(aa)},\\ b={L(bb)}}}$ ។"
    ys = [v1, v2]
    fig = dict(pieces=[(p1, c1 - 3, c1), (mid, c1, c2), (p3, c2, c2 + 3)], dots=[(c1, v1), (c2, v2)], where="s", win=(c1 - 3, c2 + 3, min(ys) - 4, max(ys) + 6), alt=f"ក្រាបជាប់នៃ ${n}$ មានបីផ្នែក ។")
    return P(prob, sol, f"a={L(aa)},\\ b={L(bb)}", [check(cl(p1, c1, "-"), v1, "left"), check(cl(p3, c2, "+"), v2, "right"), check(cl(mid, c1, "+"), v1, "join1"), check(cl(mid, c2, "-"), v2, "join2")], fig=fig)
def m_exam_three(rng):
    """society-style: limits, then a parameter item; ក ខ គ"""
    n = "f"; c0 = 0; p = ind(rng, 0, ["sin", "tan", "cos", "exp", "ln"]); q = ind(rng, rng.choice([1, 2, 3]), ["quad", "rn", "rd", "dos"]); c = None
    cc = None
    # continuous g at 0 uses p ; second piece q at its own point
    pv = rng.choice("am")
    fx = cases(n, [(p.t, "x" + NE + "0"), (pv, "x=0")])
    cq = [v for v in (1, 2, 3) if q.e.subs(x, v) in (sp.nan, sp.zoo) or (q.e.as_numer_denom()[1].subs(x, v) == 0)][0]
    pa = (f"គណនា ${lim(cq)}{q.t}$ ។", indchain(rng, q, cq))
    pb = (f"គណនា ${lim(0)}{p.t}$ ។", indchain(rng, p, 0))
    pc = ("គេឱ្យ " + "$" + fx + f"$ ។ រកតម្លៃ ${pv}$ ដោយដឹងថា ${n}$ ជាប់ត្រង់ $x=0$ ។", f"${n}$ ជាប់ត្រង់ $x=0$ លុះត្រាតែ ${n}(0)={lim(0)}{n}(x)$ ។ តាមសំណួរមុន ${pv}={L(p.val)}$ ។")
    prob, sol = build(rng, "ចូរដោះស្រាយសំណួរខាងក្រោម ។", [pa, pb, pc])
    sol += f"\nដូចនេះ $\\boxed{{{pv}={L(p.val)}}}$ ។"
    return P(prob, sol, f"{pv}={L(p.val)}", [check(cl(q.e, cq), q.val, "first"), check(cl(p.e, 0), p.val, "second")])

# ---------- driver ----------
GEN = [  # generator, subtopic, difficulties, quota, grade
 (g_read, "read_graph", ["medium", "easy", "medium"], 130),
 (g_removable, "continuity_point_removable", ["easy", "medium"], 40),
 (g_join_polys, "continuity_join_polynomials", ["easy", "easy", "medium"], 36),
 (g_join_ind, "continuity_join_indeterminate", ["medium", "hard"], 40),
 (g_abs, "continuity_absolute_value", ["medium"], 26),
 (g_undefined, "continuity_undefined_point", ["easy", "medium"], 26),
 (g_three_cond, "continuity_three_conditions", ["easy"], 22),
 (g_interval_rational, "continuity_interval_rational", ["easy", "medium"], 30),
 (g_interval_root, "continuity_interval_root_ln", ["easy", "medium"], 26),
 (g_on_R, "continuity_on_R_piecewise", ["medium"], 30),
 (g_three_piece, "continuity_three_pieces", ["medium", "hard"], 34),
 (g_param_linear, "parameter_linear_join", ["easy", "medium"], 34),
 (g_param_two, "parameter_two_unknowns", ["medium", "hard"], 34),
 (g_param_ind, "parameter_indeterminate", ["medium", "hard"], 40),
 (g_param_exp, "parameter_exp_ln_trig", ["medium"], 24),
 (g_param_quadratic, "parameter_quadratic", ["hard"], 18),
 (g_param_finite, "parameter_finite_limit", ["medium", "hard"], 34),
 (g_extend, "extension_by_continuity", ["medium", "hard"], 34),
 (g_extend_no, "extension_impossible", ["medium"], 22),
 (g_ivt_poly, "ivt_polynomial_root", ["easy", "medium"], 34),
 (g_ivt_unique, "ivt_unique_root", ["medium", "hard"], 44),
 (g_ivt_value, "ivt_intermediate_value", ["medium"], 22),
 (g_ivt_bisect, "ivt_narrow_interval", ["hard"], 18),
 (g_ivt_three, "ivt_three_roots", ["hard"], 18),
 (g_ivt_odd, "ivt_odd_degree", ["medium"], 16),
 (g_homographic, "asymptote_homographic", ["easy", "medium"], 30),
 (g_slant, "asymptote_slant_rational", ["medium"], 34),
 (g_two_va, "asymptote_two_vertical", ["medium"], 24),
 (g_hole, "asymptote_hole_vs_vertical", ["medium", "hard"], 24),
 (g_asym_exp, "asymptote_exponential", ["medium"], 26),
 (g_asym_ln, "asymptote_logarithmic", ["medium", "hard"], 26),
 (g_asym_root, "asymptote_root", ["hard"], 22),
 (g_asym_find, "asymptote_find_parameters", ["medium", "hard"], 18),
 (g_from_limits, "asymptote_from_limits", ["easy"], 14),
 (g_from_table, "asymptote_from_variation_table", ["medium"], 24),
 (g_position, "asymptote_position", ["medium"], 20),
 (m_piecewise_ivt, "bacii_piecewise_parameter_ivt", ["bacii"], 28),
 (m_rational_study, "bacii_rational_limits_asymptotes", ["bacii"], 28),
 (m_function_root, "bacii_variation_unique_root", ["bacii"], 26),
 (m_extend_chain, "bacii_extension_chain", ["bacii"], 20),
 (m_ab_graph, "bacii_two_parameters_graph", ["bacii"], 22),
 (m_exam_three, "bacii_limits_then_continuity", ["bacii"], 20),
]
ANS_CLEAN = re.compile(r"\s+")
def to_row(p, sub, diff, gen="limit_continuity", grade=12):
    prob, sol, ans = clean_tex(fixtex(p.q)), clean_tex(fixtex(p.sol)), clean_tex(fixtex(p.ans))
    rid = TOPIC + "-" + hashlib.sha1((prob + getattr(p, "key", "")).encode()).hexdigest()[:10]
    r = make_row(TOPIC, sub, diff, prob, sol, ans, p.checks, gen, chapter="limit", grade=grade, row_id=rid)
    dg = list(p.tables)
    if p.fig:
        spc = p.fig; img = None
        if state["png"] < PNG_CAP:
            img = draw(r["id"], spc); state["png"] += 1
        dg.append(dict(type="graph", latex=tikz(spc), image=img, alt_km=spc["alt"]))
    r["diagrams"] = dg
    return r

def mathkey(t):
    return re.sub(r"\s+", "", t)
def main():
    rows, seen = [], set()
    import limit_continuity_hand as H
    for hr in H.build():
        seen.add(mathkey(hr.q))
        rows.append(to_row(hr, hr.sub, hr.diff, "limit_continuity_hand"))
    print("hand", len(rows), "png", state["png"])
    for i, (g, sub, diffs, quota) in enumerate(GEN):
        rng = random.Random(1000 + i); got = 0; tries = 0; sk = set()
        while got < quota and tries < quota * 12:
            tries += 1
            try:
                p = g(rng)
            except (ZeroDivisionError, TypeError, IndexError, ValueError) as e:
                if tries < 3: print("ERR", sub, repr(e))
                continue
            if p is None: continue
            k = mathkey(p.q)
            # the formula alone must be new, so reworded copies of one exercise are skipped
            core = "".join(re.findall(r"\$\$.*?\$\$|\$.*?\$", p.q, flags=re.S))
            core = re.sub(r"(?<![a-zA-Z\\])[fgh](?=\(|\$|'|\\)", "F", core)
            core = getattr(p, "key", core)
            if k in seen and not hasattr(p, "key") or core in sk: continue
            seen.add(k); sk.add(core)
            d_ = rng.choice(diffs)
            rows.append(to_row(p, getattr(p, "sub", sub), getattr(p, "diff", d_))); got += 1
        print(f"{sub}: {got}/{quota}")
    finish_rows(rows)
    write_jsonl(rows, "limit/continuity.jsonl")
    print("rows", len(rows), "png", state["png"])
if __name__ == "__main__":
    main()
