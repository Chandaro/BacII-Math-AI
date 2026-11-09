"""Derivatives of exponential, logarithmic, trigonometric functions: original Khmer rows.
Solutions are built by a small rule engine that walks the SymPy tree and writes each step."""
import random, sys, os, re, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from common import *
from sympy import exp, log, sin, cos, tan, cot, sqrt, Rational as Q, pi, E, oo, Integer, Mul, Add

rng = random.Random(20261105)
GEN = "transcendental"; TOPIC = "transcendental"
rows = []; seen = set(); PNG = [0]; PNG_MAX = 280
_t0 = time.time()

# ---------- LaTeX ----------
FN = re.compile(r"\\(sin|cos|tan|cot|ln|log)(\^\{\d+\})?\{")
def fixfn(t):
    while True:
        mm = FN.search(t)
        if not mm:
            return t
        i = mm.end(); depth = 1; j = i
        while depth:
            c = t[j]
            if c == "\\":
                j += 2; continue
            depth += (c == "{") - (c == "}"); j += 1
        inner = t[i:j-1].strip(); rest = t[j:]; powr = mm.group(2) or ""
        if not powr:
            pm = re.match(r"\^\{(\d+)\}", rest)
            if pm:
                powr = pm.group(0); rest = rest[pm.end():]
        core = inner[6:-7].strip() if inner.startswith(r"\left(") and inner.endswith(r"\right)") else inner
        simple = re.fullmatch(r"-?\d*\s*[a-z]|\d+", core)
        name = "\\" + mm.group(1)
        t = t[:mm.start()] + name + powr + (((" " if not powr else "") + core.replace(" ", "")) if simple else (r"\left(" + core + r"\right)")) + rest

def nice(e):
    t = fixfn(lx(e))
    t = re.sub(r"(?<=\d) (?=[a-z\\])", "", t)
    t = t.replace("{- ", "{-").replace(r"\left(- ", r"\left(-").replace(r" \right)", r"\right)")
    if t.startswith("- "):
        t = "-" + t[2:]
    return t

def M(e): return "$" + nice(e) + "$"
def BX(t): return "$\\boxed{" + t + "}$"
def par(e):
    t = nice(e)
    if isinstance(e, Add) or t.startswith("-"):
        return r"\left(" + t + r"\right)"
    return t
def pwr(e, n):
    """e to the power n, unambiguous: \\cos^{3}5x, \\ln^{2}x, (x^{2})^{2}, never \\cos 5x^{3} or x^{2}^{2}."""
    ns = nice(n)
    if e.is_Symbol:
        return f"{nice(e)}^{{{ns}}}"
    if e.func in (sin, cos, tan, cot, log):
        return re.sub(r"^\\(sin|cos|tan|cot|ln) ?", lambda q: "\\" + q.group(1) + "^{" + ns + "}", nice(e))
    return r"\left(" + nice(e) + r"\right)^{" + ns + "}"
def pj(a, b, op="+"):
    """a op b as text, folding the sign of b so that +- and -- are never printed."""
    if b.startswith("-"):
        return a + ("+" if op == "-" else "-") + b[1:]
    return a + op + b
def fin(t):
    """Last pass on every row: bare numbers need no \\left( \\right), and a sign next to a split formula joins it."""
    t = re.sub(r"\\left\((\d+)\\right\)\^", r"\1^", t)
    t = re.sub(r"\\left\((-?\d+)\\right\)(?!\^)", r"(\1)", t)
    t = re.sub(r"\$ \$(>|\\neq)", r"\1", t)
    return t
def eqs(*a):
    """a=b=c without printing the same thing twice in a row"""
    out = [a[0]]
    for q in a[1:]:
        if q != out[-1]:
            out.append(q)
    return "=".join(out)
def pk(*o): return rng.choice(o)
def ri(lo, hi, no0=True):
    while True:
        v = rng.randint(lo, hi)
        if v or not no0:
            return v

def simp(d):
    c = [d]
    for fn in (sp.factor, sp.together):
        try:
            c.append(fn(d))
        except Exception:
            pass
    sc = lambda e: len(nice(e)) - 14 * nice(e).count(r"\left(")
    best = min(c, key=sc)
    return best

def prod(a, b):
    """a*b written unevaluated, without gluing digits to letters."""
    if a == 1:
        return par(b)
    if b == 1:
        return par(a)
    if a == -1:
        return "-" + par(b)
    if b == -1:
        return "-" + par(a)
    if a.is_number and a < 0:
        return "-" + prod(-a, b)
    if b.is_number and b < 0:
        return "-" + prod(a, -b)
    A, B = par(a), par(b)
    if B[0].isdigit() or (re.search(r"\\(sin|cos|tan|cot|ln)", A) and not A.startswith(r"\left(")):
        return A + r"\cdot " + B
    return A + B

# ---------- rule engine ----------
def split(e):
    if e.is_polynomial(x):
        return ("leaf",)
    if e.is_Add:
        return ("add", list(e.args))
    if e.is_Mul:
        c, r = e.as_independent(x, as_Add=False)
        if c != 1:
            return ("c", c, r)
        nums, dens = [], []
        for a in r.args:
            if a.is_Pow and a.exp.is_number and a.exp < 0:
                dens.append(1 / a)
            else:
                nums.append(a)
        if dens:
            return ("div", Mul(*nums), Mul(*dens))
        polys = [a for a in nums if a.is_polynomial(x)]
        others = [a for a in nums if not a.is_polynomial(x)]
        if polys:
            return ("mul", Mul(*polys), Mul(*others))
        return ("mul", others[0], Mul(*others[1:]))
    for fn, k in ((exp, "exp"), (log, "ln"), (sin, "sin"), (cos, "cos"), (tan, "tan"), (cot, "cot")):
        if e.func == fn:
            return (k, e.args[0])
    if e.is_Pow:
        b, n = e.base, e.exp
        if b.is_number:
            return ("apow", b, n)
        if n == Q(1, 2):
            return ("sqrt", b)
        if n.is_number and n < 0:
            return ("div", Integer(1), b ** (-n))
        if n.is_Rational:
            return ("pow", b, n)
    raise ValueError(f"split: {e}")

FORM = {"exp": r"(e^{u})'=u'e^{u}", "ln": r"(\ln u)'=\frac{u'}{u}", "sin": r"(\sin u)'=u'\cos u",
        "cos": r"(\cos u)'=-u'\sin u", "tan": r"(\tan u)'=u'(1+\tan^{2}u)", "cot": r"(\cot u)'=-u'(1+\cot^{2}u)",
        "pow": r"(u^{n})'=nu'u^{n-1}", "sqrt": r"(\sqrt{u})'=\frac{u'}{2\sqrt{u}}", "apow": r"(a^{u})'=u'a^{u}\ln a"}
BASIC = {"exp": r"(e^{x})'=e^{x}", "ln": r"(\ln x)'=\frac{1}{x}", "sin": r"(\sin x)'=\cos x", "cos": r"(\cos x)'=-\sin x",
         "tan": r"(\tan x)'=1+\tan^{2}x"}

def chain_raw(k, u, n=None, a=None):
    U = r"\left(" + nice(u) + r"\right)'"
    if k == "exp": return U + nice(exp(u))
    if k == "ln": return r"\frac{" + U + "}{" + nice(u) + "}"
    if k == "sin": return U + nice(cos(u))
    if k == "cos": return "-" + U + nice(sin(u))
    if k == "tan": return U + r"\left(1+" + nice(tan(u) ** 2) + r"\right)"
    if k == "cot": return "-" + U + r"\left(1+" + nice(cot(u) ** 2) + r"\right)"
    if k == "sqrt": return r"\frac{" + U + r"}{2" + nice(sqrt(u)) + "}"
    if k == "pow": return "2" + U + par(u) if n == 2 else nice(n) + U + pwr(u, n - 1)
    if k == "apow": return U + nice(a ** u) + r"\ln " + nice(a)
    raise ValueError(k)

def subd(e, s, depth):
    """Returns (pre_lines, inline tex of s' = ...)."""
    d = simp(sp.diff(e, x)); nd = split(e)
    if nd[0] == "leaf":
        return [], f"{s}'={nice(d)}"
    if nd[0] == "add" and all(t.is_polynomial(x) or (split(t)[0] in FORM and split(t)[0] not in ("pow", "apow") and split(t)[1] == x) for t in nd[1]):
        return [], f"{s}'={nice(d)}"
    if nd[0] in FORM and nd[1].is_polynomial(x) and nd[0] != "apow" and nd[0] != "pow":
        return [], eqs(s + "'", chain_raw(nd[0], nd[1]), nice(d)) if nd[1] != x else f"{s}'={nice(d)}"
    pre, dd = explain(e, s + "'", depth + 1)
    return pre, None

def explain(e, lab, depth=0):
    """Lines deriving lab = e' and the simplified derivative."""
    nd = split(e); k = nd[0]; d = sp.diff(e, x); ds = simp(d); L = []
    if k == "leaf":
        L.append(f"$${lab}={nice(ds)}$$")
    elif k == "c":
        c, r = nd[1], nd[2]
        if depth == 0 and rng.random() < .5:
            L.append(pk(f"ដោយ {M(c)} ជាចំនួនថេរ គេបាន $(cu)'=cu'$ ។", "មេគុណថេរនៅដដែលពេលធ្វើដេរីវេ ។"))
        lab2 = r"\left(" + nice(r) + r"\right)'"
        l2, d2 = explain(r, lab2, depth + 1); L += l2
        L.append(f"$${lab}={nice(c) if c != -1 else '-'}{lab2}={nice(ds)}$$")
    elif k == "add":
        terms = nd[1]; nonleaf = [t for t in terms if not t.is_polynomial(x)]
        L.append(pk(r"ដេរីវេនៃផលបូកស្មើនឹងផលបូកនៃដេរីវេ $(s+t)'=s'+t'$ ។", "យើងធ្វើដេរីវេម្តងមួយតួ ។", "គណនាដេរីវេនៃតួនីមួយៗ រួចបូកបញ្ចូលគ្នា ។"))
        for t in nonleaf:
            if split(t)[0] in ("mul", "div", "c", "add") or depth > 0:
                l2, _ = explain(t, r"\left(" + nice(t) + r"\right)'", depth + 1); L += l2
            else:
                L.append(f"$$\\left({nice(t)}\\right)'={nice(simp(sp.diff(t, x)))}$$")
        L.append(f"$${lab}={nice(ds)}$$")
    elif k == "mul":
        u, v = nd[1], nd[2]; u1, v1 = sp.diff(u, x), sp.diff(v, x)
        s = ("u", "v") if depth == 0 else ("p", "q")
        L.append(pk(f"អនុគមន៍នេះជាផលគុណ ។ តាង ${s[0]}={nice(u)}$ និង ${s[1]}={nice(v)}$ ។",
                    f"តាង ${s[0]}={nice(u)}$ , ${s[1]}={nice(v)}$ ។",
                    f"សរសេរជាផលគុណ ${s[0]}{s[1]}$ ដែល ${s[0]}={nice(u)}$ និង ${s[1]}={nice(v)}$ ។"))
        pa, ta = subd(u, s[0], depth); pb, tb = subd(v, s[1], depth)
        L += pa + pb
        got = [t for t in (ta, tb) if t]
        if got:
            L.append("គេបាន " + " និង ".join("$" + t + "$" for t in got) + " ។")
        L.append(pk(f"តាមរូបមន្តដេរីវេនៃផលគុណ $({s[0]}{s[1]})'={s[0]}'{s[1]}+{s[0]}{s[1]}'$ យើងបាន៖",
                    f"អនុវត្តរូបមន្ត $({s[0]}{s[1]})'={s[0]}'{s[1]}+{s[0]}{s[1]}'$ គេបាន៖"))
        u1s, v1s = simp(u1), simp(v1)
        raw = pj(prod(u1s, v), prod(u, v1s))
        L.append(f"$${lab}={raw}$$")
        if raw != nice(ds):
            L.append(f"$$={nice(ds)}$$")
    elif k == "div":
        u, v = nd[1], nd[2]; u1, v1 = sp.diff(u, x), sp.diff(v, x)
        if u.is_number:
            L.append(pk(r"តាមរូបមន្ត $\left(\frac{1}{v}\right)'=-\frac{v'}{v^{2}}$ ដោយ", r"អនុគមន៍មានរាង $\frac{c}{v}$ ដែល $\left(\frac{1}{v}\right)'=-\frac{v'}{v^{2}}$ ហើយ") + f" $v={nice(v)}$ ។")
            pb, tb = subd(v, "v", depth); L += pb
            if tb:
                L.append(f"គេបាន ${tb}$ ។")
            L.append("$$" + eqs(lab, ('-' if u == 1 else '' if u == -1 else nice(-u)) + f"\\frac{{{nice(simp(v1))}}}{{{pwr(v, 2)}}}", nice(ds)) + "$$")
        else:
            s = ("u", "v") if depth == 0 else ("p", "q")
            L.append(pk(f"អនុគមន៍នេះជាផលចែក ។ តាង ${s[0]}={nice(u)}$ និង ${s[1]}={nice(v)}$ ។",
                        f"តាង ${s[0]}={nice(u)}$ , ${s[1]}={nice(v)}$ ។"))
            pa, ta = subd(u, s[0], depth); pb, tb = subd(v, s[1], depth)
            L += pa + pb
            got = [t for t in (ta, tb) if t]
            if got:
                L.append("គេបាន " + " និង ".join("$" + t + "$" for t in got) + " ។")
            L.append(pk(f"តាមរូបមន្តដេរីវេនៃផលចែក $\\left(\\frac{{{s[0]}}}{{{s[1]}}}\\right)'=\\frac{{{s[0]}'{s[1]}-{s[0]}{s[1]}'}}{{{s[1]}^{{2}}}}$ យើងបាន៖",
                        f"អនុវត្តរូបមន្ត $\\left(\\frac{{{s[0]}}}{{{s[1]}}}\\right)'=\\frac{{{s[0]}'{s[1]}-{s[0]}{s[1]}'}}{{{s[1]}^{{2}}}}$ គេបាន៖"))
            L.append(f"$${lab}=\\frac{{{pj(prod(simp(u1), v), prod(u, simp(v1)), '-')}}}{{{pwr(v, 2)}}}$$")
            L.append(f"$$={nice(ds)}$$")
    else:
        u = nd[1] if k != "apow" else nd[2]
        n = nd[2] if k == "pow" else None
        a = nd[1] if k == "apow" else None
        if k == "ln" and u == x or (u == x and k in BASIC):
            L.append(f"$${lab}={nice(ds)}$$")
        else:
            w = "u" if depth == 0 else "w"; F = FORM[k].replace("u", w)
            if not u.is_polynomial(x) and split(u)[0] in ("mul", "div", "add", "c") and not (split(u)[0] == "add" and subd(u, w, depth)[1]):
                L.append(f"តាង ${w}={nice(u)}$ ។ ដំបូងគណនា ${w}'$ ។")
                l2, _ = explain(u, w + "'", depth + 1); L += l2
                L.append(f"តាមរូបមន្ត ${F}$ គេបាន៖")
            else:
                L.append(pk(f"តាមរូបមន្ត ${F}$ ដែល ${w}={nice(u)}$ យើងបាន៖",
                            f"នេះជាអនុគមន៍បណ្ដាក់ ។ យក ${w}={nice(u)}$ ហើយប្រើរូបមន្ត ${F}$ ៖",
                            f"តាង ${w}={nice(u)}$ ។ តាមរូបមន្ត ${F}$ គេបាន៖"))
            L.append("$$" + eqs(lab, chain_raw(k, u, n, a), nice(ds)) + "$$")
    return L, ds

# ---------- helpers ----------
def nm():
    return pk("f", "f", "f", "g", "h", "y")
def labs(n):
    if n == "y":
        return "y", "y'", "y''", "y'''"
    return f"{n}(x)", f"{n}'(x)", f"{n}''(x)", f"{n}'''(x)"
def DEF(n, f):
    return f"${labs(n)[0]}={nice(f)}$"

def emit(sub, diff_, prob, sol, ans, checks, diagrams=None, key=None):
    k = key if key is not None else prob
    if k in seen:
        return None
    seen.add(k)
    for d in diagrams or []:
        d["latex"] = fin(d["latex"])
    r = make_row(TOPIC, sub, diff_, fin(prob), fin(sol), fin(ans), checks, GEN, diagrams=diagrams)
    rows.append(r)
    return r

def concl(lhs, val):
    t = lhs + "=" + nice(val)
    return pk("ដូចនេះ " + BX(t) + " ។", "ដូចនេះ " + BX(t) + " ។", "ដូចនេះ ដេរីវេដែលត្រូវរកគឺ " + BX(t) + " ។",
              "ដូចនេះ គេបាន " + BX(t) + " ។", "សរុបមក ដូចនេះ " + BX(t) + " ។")

def dom_ln(cond, D):
    return pk(f"អនុគមន៍កំណត់លុះត្រាតែ ${cond}$ ដូច្នេះ $D={D}$ ។", f"ដែនកំណត់៖ ${cond}$ មានន័យថា $D={D}$ ។",
              f"លក្ខខណ្ឌកំណត់គឺ ${cond}$ ។ ដូចនេះ $D={D}$ ។")
def dom_R():
    return pk("អនុគមន៍កំណត់ចំពោះគ្រប់ចំនួនពិត $x$ គឺ $D=IR$ ។", "ដែនកំណត់ $D=IR$ ។", "គ្រប់ $x\\in IR$ អនុគមន៍នេះមានន័យ គឺ $D=IR$ ។")

# Domain of a printed function, worked out from its tree. Every row with ln, a root, tan or a quotient states it.
KINT = "ដែល $k$ ជាចំនួនគត់"
def _conds(f):
    out = []
    for nd in sp.preorder_traversal(f):
        c = None
        if isinstance(nd, log): c = (">", nd.args[0])
        elif isinstance(nd, tan): c = ("tan", nd.args[0])
        elif isinstance(nd, cot): c = ("cot", nd.args[0])
        elif nd.is_Pow and nd.base.has(x) and nd.exp.is_Rational:
            if nd.exp.q % 2 == 0: c = (">=" if nd.exp > 0 else ">", nd.base)
            elif nd.exp < 0: c = ("!=", nd.base)
        if c and c not in out:
            out.append(c)
    us = [c[1] for c in out if c[0] == ">"]
    out = [c for c in out if not (c[0] in ("!=", ">=") and c[1] in us)]      # u>0 already says u is nonzero
    return [c for c in out if not (c[0] == "tan" and tan(c[1]) in us) and not (c[0] == "cot" and cot(c[1]) in us)]
def _always(u):
    """1 if u>0 for all real x, -1 if u<0 for all real x, else 0."""
    if u.is_positive: return 1
    if u.is_negative: return -1
    fn = sp.lambdify(x, u, "numpy"); xs = np.linspace(-20, 20, 4001)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(np.asarray(fn(xs), dtype=complex), xs.shape)
    if not np.all(np.isfinite(ys)) or np.abs(ys.imag).max() > 1e-12: return 0
    if ys.real.min() > 1e-3: return 1
    if ys.real.max() < -1e-3: return -1
    return 0
def _kt(c, m, a=1):
    """c + m k pi / a as text"""
    q = Q(m, a); num = ("" if q.p == 1 else str(q.p)) + r"k\pi"
    kp = num if q.q == 1 else r"\frac{" + num + "}{" + str(q.q) + "}"
    return kp if c == 0 else nice(c) + "+" + kp
def _trig(kind, u):
    """periodic condition: (condition tex, exclusions or intervals tex, 'x' or 'set') or None"""
    if kind in ("tan", "cot"):
        if not u.is_polynomial(x) or sp.degree(u, x) != 1: return None
        a, b = u.coeff(x, 1), u.coeff(x, 0)
        if not a.is_Integer: return None
        c0 = ((pi/2 if kind == "tan" else 0) - b)/a
        return (nice((cos if kind == "tan" else sin)(u)) + r"\neq0", _kt(c0, 1, abs(a)), "x")
    if kind == ">" and u.func in (sin, cos, tan):
        a = u.args[0].coeff(x, 1)
        if u.args[0] != a*x or not a.is_Integer or a <= 0: return None
        lo, hi, m = {sin: (Integer(0), pi/a, 2), cos: (-pi/(2*a), pi/(2*a), 2), tan: (Integer(0), pi/(2*a), 1)}[u.func]
        return (nice(u) + ">0", r"\left(" + _kt(lo, m, a) + ";" + _kt(hi, m, a) + r"\right)", "set")
    if kind in (">", "!=") and u in (cos(x) + 1, sin(x) + 1):
        return (nice(u) + (">0" if kind == ">" else r"\neq0"), _kt(pi if u == cos(x) + 1 else -pi/2, 2), "x")
    return None
def set_tex(S_):
    if S_ == sp.S.Reals: return "IR"
    ex = sp.S.Reals - S_
    if isinstance(ex, sp.FiniteSet):
        return r"IR-\left\{" + ";".join(nice(v) for v in sorted(ex.args, key=float)) + r"\right\}"
    if isinstance(S_, sp.Union):
        return r"\cup ".join(set_tex(a) for a in sorted(S_.args, key=lambda i: float(i.inf)))
    return (r"\left(" if S_.left_open else r"\left[") + T(S_.inf) + ";" + T(S_.sup) + (r"\right)" if S_.right_open else r"\right]")
_DOM = {}
def dom_info(f):
    """(always-true conditions, real conditions tex, domain set or None, periodic part, set where a root is differentiable)"""
    k = str(f)
    if k in _DOM: return _DOM[k]
    allw, conds, Dset, per, Dstrict = [], [], sp.S.Reals, [], sp.S.Reals
    for kind, u in _conds(f):
        if kind in (">", ">=", "!="):
            w = _always(u)
            if w:
                allw.append(nice(u) + (">0" if w > 0 else "<0")); continue
        tr = _trig(kind, u)
        if tr:
            conds.append(tr[0]); per.append(tr); continue
        if u.has(sin, cos, tan, cot):
            conds.append(nice(u) + {">": ">0", ">=": r"\ge0", "!=": r"\neq0"}[kind]); Dset = None; continue
        tex = nice(u) + {">": ">0", ">=": r"\ge0", "!=": r"\neq0"}[kind]
        conds.append(tex)
        if kind == "!=":
            s1 = sp.S.Reals - sp.solveset(u, x, sp.S.Reals); s2 = s1
        else:
            s1 = sp.solve_univariate_inequality(u > 0 if kind == ">" else u >= 0, x, relational=False)
            s2 = sp.solve_univariate_inequality(u > 0, x, relational=False)
        if Dset is not None:
            Dset = Dset.intersect(s1)
        Dstrict = Dstrict.intersect(s2)
    _DOM[k] = (allw, conds, Dset, per, Dstrict)
    return _DOM[k]
def auto_dom(f):
    """One domain sentence for f, with the conditions solved. Empty only for a function defined on IR with nothing to check."""
    allw, conds, Dset, per, Dstrict = dom_info(f)
    pre = ("ដោយ " + " និង ".join("$" + c + "$" for c in allw) + " ជានិច្ច ") if allw else ""
    if not conds:
        return pre + "នោះ $D=IR$ ។" if allw else dom_R()
    cs = " និង ".join("$" + c + "$" for c in conds)
    if len(per) == 1 and per[0][2] == "set" and len(conds) == 1:
        return pre + f"អនុគមន៍កំណត់លុះត្រាតែ {cs} ។ ដូចនេះ ដែនកំណត់ $D$ ជាសំណុំនៃចន្លោះ ${per[0][1]}$ {KINT} ។"
    if len(per) == 1 and per[0][2] == "x" and len(conds) == 1:
        return pre + f"អនុគមន៍កំណត់លុះត្រាតែ {cs} គឺ $x\\neq{per[0][1]}$ {KINT} ។ ដូចនេះ $D=IR-\\left\\{{{per[0][1]}\\right\\}}$ ។"
    if per or Dset is None:
        return pre + f"អនុគមន៍កំណត់លុះត្រាតែ {cs} ។ ដូចនេះ $D=\\left\\{{x\\in IR\\mid " + r",\ ".join(conds) + r"\right\}$ ។"
    D_ = set_tex(Dset)
    s_ = pre + pk(f"អនុគមន៍កំណត់លុះត្រាតែ {cs} ។ ដូចនេះ $D={D_}$ ។", f"ដែនកំណត់៖ លក្ខខណ្ឌគឺ {cs} ។ ដូចនេះ $D={D_}$ ។", f"លក្ខខណ្ឌកំណត់គឺ {cs} ។ ដូចនេះ $D={D_}$ ។")
    if Dstrict != Dset and Dset.intersect(Dstrict) != Dset:
        s_ += f" ដេរីវេមានចំពោះ $x\\in {set_tex(Dset.intersect(Dstrict))}$ ។"
    return s_

def parts(prob, chunks, pre=()):
    """Solution lines laid out the way the problem is: the problem's own ក. ខ. headers over each chunk.
    A problem with no labels gets the chunks in order, unlabelled."""
    sp_ = re.split(r"(?:(?<=\s)|^)([កខគឃងច])\. ", prob)
    labs = list(zip(sp_[1::2], [q.strip() for q in sp_[2::2]]))
    out = [q for q in pre if q]
    for i, ch in enumerate(chunks):
        if len(labs) == len(chunks):
            out.append(f"{labs[i][0]}. {labs[i][1]}")
        out += [q for q in ch if q]
    return out
def has_parts(prob): return bool(re.search(r"(?:(?<=\s)|^)ក\. ", prob))
def yminus(v, s="y"):
    """s - v with the sign of v folded in"""
    if v == 0: return s
    if v.could_extract_minus_sign(): return s + "+" + nice(-v)
    return s + "-" + par(v)
def tline(y0, m_, x0):
    """y-y0=m(x-x0) with nothing to tidy: no y-0, no y-(-2), no 1( or (-1)("""
    xm = yminus(x0, "x"); xf = xm if x0 == 0 else r"\left(" + xm + r"\right)"
    if m_ == 0: rhs = "0"
    elif m_ == 1: rhs = xf
    elif m_ == -1: rhs = "-" + xf
    elif isinstance(m_, Add): rhs = r"\left(" + nice(m_) + r"\right)" + xf
    else: rhs = nice(m_) + xf
    return yminus(y0) + "=" + rhs

def pgf(e):
    t = str(e).replace("**", "^").replace("log(", "ln(").replace("E", "exp(1)")
    return t
def poles(f, lo, hi):
    """x values in (lo,hi) where f blows up: the curve must not be joined across them"""
    out = set()
    for nd in sp.preorder_traversal(f):
        if isinstance(nd, (tan, cot)):
            u = nd.args[0]; a, b = float(u.coeff(x, 1)), float(u.coeff(x, 0))
            for k in range(-40, 41):
                v = ((np.pi/2 if isinstance(nd, tan) else 0) + k*np.pi - b)/a
                if lo < v < hi: out.add(round(v, 4))
        elif nd.is_Pow and nd.base.has(x) and nd.exp.is_number and nd.exp < 0:
            for v in sp.solveset(nd.base, x, sp.Interval.open(lo, hi)) if nd.base.is_polynomial(x) else ():
                out.add(round(float(v), 4))
    return sorted(out)
def graph(row, f, xmin, xmax, ymin, ymax, alt, tangent=None, points=(), asym=(), d0=None, d1=None, extra=""):
    xmin, xmax = round(float(xmin), 2), round(float(xmax), 2)
    lo, hi = (xmin if d0 is None else float(d0)), (xmax if d1 is None else float(d1))
    Dset = dom_info(f)[2]
    if Dset is not None and Dset != sp.S.Reals:                # the curve starts where the domain starts
        a0, b0 = Dset.inf, Dset.sup
        if a0 != -oo and float(a0) >= lo:
            lo = round(float(a0) + (.02 if a0 not in Dset else 0), 2)
        if b0 != oo and float(b0) <= hi:
            hi = round(float(b0) - (.02 if b0 not in Dset else 0), 2)
    if tangent is not None:
        extra += "\\addplot[dashed,domain=%s:%s] {%s};\n" % (xmin, xmax, pgf(tangent))
    if points:
        extra += "\\addplot[only marks,mark=*] coordinates {" + " ".join(f"({round(float(a), 3)},{round(float(b), 3)})" for a, b in points) + "};\n"
    t = tikz_graph(pgf(f), xmin, xmax, ymin, ymax, extra).replace("samples=200]", "samples=200,trig format plots=rad]")
    pl = poles(f, lo, hi); ed = [lo] + [v for q in pl for v in (round(q - .03, 3), round(q + .03, 3))] + [hi]
    seg = "".join(f"\\addplot[thick,domain={ed[i]}:{ed[i + 1]}] {{{pgf(f)}}};\n" for i in range(0, len(ed), 2))
    t = t.replace(f"\\addplot[thick,domain={xmin}:{xmax}] {{{pgf(f)}}};\n", seg, 1)
    if pl or Dset != sp.S.Reals:
        t = t.replace("samples=200,", f"samples=200,unbounded coords=jump,restrict y to domain={ymin - 1}:{ymax + 1},", 1)
    img = None
    if PNG[0] < PNG_MAX:
        img = plot_png(row["id"], f, xmin, xmax, ymin, ymax, tangent=tangent, points=points, asymptotes=asym); PNG[0] += 1
    t = re.sub(r"(?<![\d.])(-?\d+)\.0(?!\d)", r"\1", t)                # -3 in the figure source, never -3.0
    row["diagrams"].append({"type": "graph", "latex": fin(t), "image": img, "alt_km": alt})

# ---------- A: direct derivative ----------
def lin(a, b): return a * x + b
def fam_exp():
    a, b, c, k = ri(-5, 5), ri(-6, 6), ri(-6, 6), ri(-4, 4)
    p = ri(1, 5); n = rng.randint(2, 5); q = rng.randint(1, 6)
    return [
     (exp(lin(a, b)), None), (exp(a*x**2 + b*x + c), None), (lin(a, b)*exp(k*x), None),
     ((a*x**2 + b*x + c)*exp(k*x), None), (x**n*exp(k*x), None),
     (exp(k*x)/(x + b), f"អនុគមន៍កំណត់លុះត្រាតែ $x+{b}\\neq0$ ។".replace("+-", "-")),
     ((exp(x) + b)/(exp(x) + q), "ដោយ $e^{x}>0$ នោះភាគបែងខុសពីសូន្យជានិច្ច គឺ $D=IR$ ។"),
     (exp(p*x)/(x**2 + q), "ដោយ " + M(x**2 + q) + " $>0$ ជានិច្ច នោះ $D=IR$ ។"),
     (a*exp(k*x) + b*exp(-p*x) + c*x, None),
     (c/(q + exp(k*x)), "ភាគបែងវិជ្ជមានជានិច្ច នោះ $D=IR$ ។"),
     ((exp(p*x) - exp(-p*x))/(exp(p*x) + exp(-p*x)), "ភាគបែងវិជ្ជមានជានិច្ច នោះ $D=IR$ ។"),
     (Integer(rng.choice([2, 3, 5, 7, 10]))**lin(p, b), None),
     (sqrt(exp(p*x) + q), "ដោយ " + M(exp(p*x) + q) + " $>0$ នោះ $D=IR$ ។"),
     (exp(sqrt(x + q)), None), (exp(Integer(a)/x), "អនុគមន៍កំណត់ចំពោះ $x\\neq0$ ។"),
     ((exp(k*x) + q)**n, None), (exp(x)*lin(a, b)/(x**2 + q), None),
     (x*exp(-x**2*p), None), (lin(a, b)/exp(p*x), None),
    ]
def fam_log():
    a, b, c = ri(1, 6), ri(-6, 6), ri(-5, 5); p, q = ri(1, 5), ri(1, 7); n = rng.randint(2, 4)
    r = Q(-b, a)
    D = lambda v: f"\\left({nice(v)};+\\infty\\right)"
    pos = "ចំពោះ $x>0$ អនុគមន៍មានន័យ គឺ $D=(0;+\\infty)$ ។"
    return [
     (log(lin(a, b)), dom_ln(nice(lin(a, b)) + ">0", D(r))),
     (log(x**2 + q), "ដោយ " + M(x**2 + q) + " $>0$ ជានិច្ច នោះ $D=IR$ ។"),
     (x*log(x), pos), (lin(c, b)*log(x), pos), (x**n*log(x), pos),
     (log(x)/x, pos), (log(x)/x**n, pos), ((c + q*log(x))/x, pos),
     (log(x)**n, pos), ((log(x) + b)**n, pos),
     (log(log(x)), "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ និង $\\ln x>0$ គឺ $x>1$ ។"),
     (Integer(c)/log(x), "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ និង $\\ln x\\neq0$ ។"),
     (x/log(x), "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ និង $x\\neq1$ ។"),
     (lin(c, b) - q*log(x), pos), (lin(c, b) + q*log(x)/x, pos), (lin(p, b) + log(x)**2, pos),
     (log(exp(x) + q), "ដោយ " + M(exp(x) + q) + " $>0$ នោះ $D=IR$ ។"),
     (log(x + sqrt(x**2 + q)), "ដោយ " + M(sqrt(x**2 + q)) + " $>|x|$ នោះកន្សោមក្នុងលោការីតវិជ្ជមាន ហើយ $D=IR$ ។"),
     (sqrt(log(x)), "អនុគមន៍កំណត់លុះត្រាតែ $\\ln x\\ge0$ គឺ $x\\ge1$ ហើយដេរីវេមានចំពោះ $x>1$ ។"),
     (log(x**2 + q)/x, "អនុគមន៍កំណត់ចំពោះ $x\\neq0$ ។"),
     (x**2*log(x**2 + q), None), (log(q + sin(x)**2), None),
     (log(p*x + q)*exp(x) if b else exp(-x)*log(x + q), None),
    ]
def fam_trig():
    a, b, c = ri(-5, 5), ri(-4, 4), ri(-5, 5); p, q = ri(2, 6), ri(2, 5); n = rng.randint(2, 5)
    ph = rng.choice([pi/6, pi/4, pi/3, pi/2, -pi/4, -pi/3, 1, 2])
    A = rng.randint(2, 6)
    return [
     (sin(lin(a, ph)), None), (cos(lin(a, ph)), None), (tan(lin(p, b)), None),
     (sin(p*x)**n, None), (cos(p*x)**n, None), (x*sin(p*x), None), (x**2*cos(p*x), None),
     (lin(a, b)*cos(q*x), None), (sin(p*x)*cos(q*x), None),
     (sin(x)/(A + cos(x)), f"ដោយ $-1\\le\\cos x\\le1$ នោះ ${A}+\\cos x>0$ ជានិច្ច ។"),
     ((A + sin(x))/(A + cos(x)), f"ដោយ ${A}+\\cos x>0$ ជានិច្ច នោះ $D=IR$ ។"),
     (Integer(c)/(A + sin(p*x)), None), (tan(p*x)**2, None), (x*tan(x), None),
     (sqrt(A + sin(p*x)), f"ដោយ ${A}+\\sin {p}x>0$ ជានិច្ច នោះ $D=IR$ ។"),
     (sqrt(A + cos(x)**2), None), (sin(x**2 + b), None), (cos(sqrt(x)*p), "ដេរីវេមានចំពោះ $x>0$ ។"),
     (sin(Integer(p)/x), "អនុគមន៍កំណត់ចំពោះ $x\\neq0$ ។"),
     (exp(a*x)*sin(p*x), None), (exp(a*x)*cos(p*x), None), (exp(sin(p*x)), None), (exp(cos(p*x)), None),
     (exp(tan(x)*p), None), (sin(exp(p*x)), None), (cos(log(x)*p), "ចំពោះ $x>0$ អនុគមន៍មានន័យ ។"),
     (sin(log(x)*p), "ចំពោះ $x>0$ អនុគមន៍មានន័យ ។"), (log(A + sin(p*x)), f"ដោយ ${A}+\\sin {p}x>0$ ជានិច្ច នោះ $D=IR$ ។"),
     (log(A + cos(x)), None), (cot(p*x), None), (a*sin(x) + b*cos(x) + c*x, None),
     (sin(p*x) - p*x*cos(p*x), None), (p*x*sin(p*x) + cos(p*x), None), (exp(p*x)*(sin(x) - cos(x)), None),
     (log(x)*sin(p*x), None), (log(cos(x)), "ចំពោះ $-\\frac{\\pi}{2}<x<\\frac{\\pi}{2}$ យើងមាន $\\cos x>0$ ។"),
     (log(sin(x)), "ចំពោះ $0<x<\\pi$ យើងមាន $\\sin x>0$ ។"),
     (log(tan(x)), "ចំពោះ $0<x<\\frac{\\pi}{2}$ យើងមាន $\\tan x>0$ ។"),
     (sin(x)**2*cos(x), None), (x/(A + sin(x)), None), (sin(cos(p*x)), None), (cos(sin(x)*p), None),
    ]

def ask_deriv(n, f):
    y = labs(n)
    if n == "y":
        return pk(f"គេមានអនុគមន៍ {DEF(n,f)} ។ ចូរគណនាដេរីវេ $y'$ ។", f"គណនាដេរីវេនៃអនុគមន៍ {DEF(n,f)} ។", f"រកដេរីវេ $y'$ នៃអនុគមន៍ {DEF(n,f)} ។",
                  f"គេឱ្យអនុគមន៍ $$y={nice(f)}$$ ចូរគណនាដេរីវេ $y'$ ។")
    return pk(f"គណនាដេរីវេនៃអនុគមន៍ {DEF(n,f)} ។", f"គេឱ្យអនុគមន៍ {DEF(n,f)} ។ ចូរគណនា ${y[1]}$ ។",
              f"រកដេរីវេនៃអនុគមន៍ខាងក្រោម៖ $${y[0]}={nice(f)}$$", f"គេមានអនុគមន៍ {DEF(n,f)} ។ រកដេរីវេទី១ នៃ ${n}$ ។",
              f"អនុគមន៍ ${n}$ កំណត់ដោយ {DEF(n,f)} ។ ចូរគណនាដេរីវេ ${y[1]}$ ។", f"ចូរគណនា ${y[1]}$ ដោយដឹងថា {DEF(n,f)} ។",
              f"ឱ្យ {DEF(n,f)} ។ គណនាដេរីវេ ${y[1]}$ រួចសម្រួលលទ្ធផល ។")

def sub_of(f):
    h = f.has
    if h(sin, cos, tan, cot) and h(exp, log): return "composition_mixed"
    if h(sin, cos, tan, cot): return "trig_derivative"
    if h(log) and h(exp): return "composition_mixed"
    if h(log): return "log_derivative"
    return "exp_derivative"

def dif_of(f):
    t = sp.count_ops(f)
    return "easy" if t <= 4 else ("medium" if t <= 10 else "hard")

def row_deriv(f, dom):
    n = nm(); y = labs(n)
    key = ("d", str(f))
    if str(f) in seen or key in seen:
        return
    try:
        L, ds = explain(f, y[1])
    except ValueError:
        return
    pre = auto_dom(f)
    sol = "\n".join(([pre] if pre else []) + L + [concl(y[1], ds)])
    emit(sub_of(f), dif_of(f), ask_deriv(n, f), sol, y[1] + "=" + nice(ds),
         [check(f"diff({s(f)},x)", s(ds), "derivative")], key=str(f))

def gen_direct(target_each=18):
    for fam in (fam_exp, fam_log, fam_trig):
        n = len(fam()); cnt = [0] * n
        for _ in range(target_each * 12):
            items = fam()
            for i, (f, dom) in enumerate(items):
                if cnt[i] >= target_each or f.is_number or f.has(sp.zoo, sp.nan):
                    continue
                b4 = len(rows); row_deriv(f, dom)
                if len(rows) > b4:
                    cnt[i] += 1
            if min(cnt) >= target_each:
                break

# ---------- B: derivative at a point ----------
def fam_point():
    a, k, q = ri(1, 5), ri(-4, 4), ri(1, 5); b = ri(-5, 5); p = rng.choice([2, 3, 4])
    t = rng.choice([pi/6, pi/4, pi/3, pi/2, pi, 2*pi/3])
    return [
     (lin(a, b)*exp(k*x), Integer(0)), (x**2*exp(k*x), Integer(1)), (log(a*x + 1), Integer(0)), (log(lin(a, 1 - a)), Integer(1)),
     (x*log(x) + b*x, E), (log(x)/x, E), (log(x)**2 + b*x, E), (x**p*log(x), Integer(1)), (log(x)/x**2 + b, Integer(1)), ((log(x) + b)/x, E),
     (sin(k*x) + b*x, t), (x*sin(x), t), (x*cos(x), t), (exp(sin(k*x)), Integer(0)), (exp(cos(x))*q, pi/2), (tan(x) + b*x, pi/4), (sin(x)**2 + b*x, t), (cos(x)**p, t),
     (log(q + sin(x)), Integer(0)), (log(x**2 + q) + b*x, Integer(1)), (sqrt(exp(2*x) + 3 + q*0)*q, Integer(0)), (exp(x)/(x + q), Integer(0)), (sin(x)/(q + cos(x)), Integer(0)),
     (exp(k*x)*sin(x), Integer(0)), (exp(k*x)*cos(x), Integer(0)), (x*exp(x**2 - 1), Integer(1)), (log(cos(x)) + b*x, pi/4), (log(x)*exp(x - 1), Integer(1)),
     (Integer(rng.choice([2, 3, 5]))**x, Integer(rng.choice([0, 1, 2]))), (sin(log(x)), Integer(1)), (cos(p*x)*exp(x), Integer(0)),
    ]
def gen_point(each=7):
    n = len(fam_point()); cnt = [0] * n
    for _ in range(each * 15):
        for i, (f, x0) in enumerate(fam_point()):
            if cnt[i] >= each: continue
            key = "p" + str(f)
            if key in seen or str(f) in seen: continue
            d = sp.diff(f, x); v = d.subs(x, x0)
            if v.has(sp.zoo, sp.nan): continue
            n_ = nm()
            if n_ == "y": n_ = "f"
            y = labs(n_)
            L, ds = explain(f, y[1])
            v2 = sp.simplify(ds.subs(x, x0))
            vraw = ds.subs(x, x0) if False else None
            P = f"{n_}'\\left({nice(x0)}\\right)"
            prob = pk(f"គេឱ្យអនុគមន៍ {DEF(n_,f)} ។ ចូរគណនា ${P}$ ។", f"គណនាតម្លៃដេរីវេនៃអនុគមន៍ {DEF(n_,f)} ត្រង់ $x={nice(x0)}$ ។",
                      f"គេមានអនុគមន៍ {DEF(n_,f)} ។\nក. គណនា ${y[1]}$ ។\nខ. ទាញរកតម្លៃ ${P}$ ។",
                      f"ចូររកតម្លៃដេរីវេ ${P}$ ដោយដឹងថា {DEF(n_,f)} ។")
            two = has_parts(prob); fx = y[1] + "=" + nice(ds)
            val = [pk("ជំនួស", "យក", "ចំពោះ") + f" $x={nice(x0)}$ " + pk("គេបាន៖", "ក្នុង " + f"${y[1]}$ យើងបាន៖"), f"$${P}={nice(v2)}$$", "ដូចនេះ " + BX(P + "=" + nice(v2)) + " ។"]
            sol = "\n".join(parts(prob, [L + (["ដូចនេះ " + BX(fx) + " ។"] if two else []), val], pre=[auto_dom(f)]))
            emit("derivative_at_point", dif_of(f), prob, sol, (fx + ",\\ " if two else "") + P + "=" + nice(v2),
                 [check(f"diff({s(f)},x)", s(ds), "derivative"), check(f"subs(diff({s(f)},x),x,{s(x0)})", s(v2), "value at point")], key=key)
            seen.add(str(f)); cnt[i] += 1

# ---------- C: higher order ----------
def fam_high():
    a, k, q = ri(1, 5), ri(-3, 3), ri(1, 5); b = ri(-5, 5); p = rng.choice([2, 3, 4]); w = rng.randint(1, 4)
    return [
     (lin(a, b)*exp(k*x), "R"), ((x**2 + b*x + q)*exp(k*x), "R"), (x**2*exp(k*x), "R"), (x*log(x), "P"), (x**2*log(x), "P"), (lin(a, b)*log(x), "P"),
     (log(x)/x, "P"), (log(lin(a, q)), None), (log(x**2 + q), "R"), (x*sin(w*x), "R"), (x*cos(w*x), "R"), (exp(k*x)*sin(w*x), "R"), (exp(k*x)*cos(w*x), "R"),
     (sin(w*x)**2, "R"), (cos(w*x)**2, "R"), (tan(w*x), None), (exp(k*x**2), "R"), (exp(a*x) + exp(-q*x), "R"), (log(x)**2, "P"), (log(exp(x) + q), "R"),
     (sin(lin(p, b)) + cos(lin(w, 1)), "R"), (Integer(q)/(exp(x) + 1), "R"), (x*exp(k*x) + b*sin(x), "R"), (sqrt(x**2 + q), "R"), (exp(sin(x)), "R"),
    ]
def gen_high(each=10):
    n = len(fam_high()); cnt = [0] * n
    for _ in range(each * 12):
        for i, (f, dm) in enumerate(fam_high()):
            if cnt[i] >= each or f.is_number: continue
            key = "h" + str(f)
            if key in seen or str(f) in seen: continue
            n_ = nm(); y = labs(n_)
            try:
                L1, d1 = explain(f, y[1]); L2, d2 = explain(d1, y[2], 0)
            except ValueError:
                continue
            third = rng.random() < .3 and sp.count_ops(d2) < 14
            chk = [check(f"diff({s(f)},x)", s(d1), "first"), check(f"diff({s(f)},x,2)", s(d2), "second")]
            pre = auto_dom(f)
            c1 = [pk("គណនាដេរីវេទី១ ។", "ដំបូង រកដេរីវេទី១ ។", "ជំហានទី១៖ ដេរីវេទី១ ។")] + L1
            c2 = [pk("បន្តធ្វើដេរីវេម្តងទៀត ដើម្បីបានដេរីវេទី២ ។", "គណនាដេរីវេទី២ ។", "ជំហានទី២៖ ដេរីវេនៃ $" + y[1] + "$ ។")] + L2
            ans = f"{y[1]}={nice(d1)},\\ {y[2]}={nice(d2)}"
            if third:
                try:
                    L3, d3 = explain(d2, y[3], 0)
                except ValueError:
                    third = False
            if third:
                c3 = ["ធ្វើដេរីវេមួយដងទៀត យើងបានដេរីវេទី៣ ។"] + L3
                chk.append(check(f"diff({s(f)},x,3)", s(d3), "third")); ans += f",\\ {y[3]}={nice(d3)}"
                prob = pk(f"គេឱ្យ {DEF(n_,f)} ។ គណនា ${y[1]}$ , ${y[2]}$ និង ${y[3]}$ ។", f"រកដេរីវេទី១ ទី២ និងទី៣ នៃអនុគមន៍ {DEF(n_,f)} ។")
                sol = parts(prob, [c1 + c2 + c3], pre=[pre]) + ["ដូចនេះ " + BX(y[1] + "=" + nice(d1)) + " , " + BX(y[2] + "=" + nice(d2)) + " និង " + BX(y[3] + "=" + nice(d3)) + " ។"]
            else:
                prob = pk(f"គេឱ្យ {DEF(n_,f)} ។ គណនា ${y[1]}$ និង ${y[2]}$ ។", f"រកដេរីវេទី១ និងដេរីវេទី២ នៃអនុគមន៍ {DEF(n_,f)} ។",
                          f"គេមានអនុគមន៍ {DEF(n_,f)} ។\nក. គណនា ${y[1]}$ ។\nខ. គណនា ${y[2]}$ ។", f"ចូរគណនាដេរីវេទី២ នៃ {DEF(n_,f)} ។")
                sol = parts(prob, [c1, c2] if has_parts(prob) else [c1 + c2], pre=[pre]) + ["ដូចនេះ " + BX(y[1] + "=" + nice(d1)) + " និង " + BX(y[2] + "=" + nice(d2)) + " ។"]
            emit("higher_order", "hard" if third else "medium", prob, "\n".join(sol), ans, chk, key=key)
            seen.add(str(f)); cnt[i] += 1

# ---------- D: nth derivative ----------
def pw(a, n):
    if a == 1: return ""
    if a == -1: return "(-1)^{" + n + "}"
    return (f"({a})" if a < 0 else f"{a}") + "^{" + n + "}"
def ln_(a, b): return nice(lin(a, b))

def nth_families():
    a = ri(-4, 4); ap = ri(1, 4); b = ri(-6, 6); c = rng.randint(1, 6); u = ln_(a, b); up = ln_(ap, c)
    cap = "" if ap == 1 else r"\cdot " + str(ap)
    F = []
    # (name, f, formula(n), tex(n as string), mid-tex, n_start)
    F.append(("e", exp(lin(a, b)), lambda n: a**n*exp(lin(a, b)),
              lambda n: pw(a, n) + "e^{" + u + "}",
              lambda: pw(a, "k") + r"\left(e^{" + u + r"}\right)'=" + pw(a, "k") + ("" if a == 1 else r"\cdot " + par(Integer(a))) + "e^{" + u + "}", 1))
    F.append(("xe", x*exp(a*x), lambda n: (Integer(a)**n*x + n*Integer(a)**(n-1))*exp(a*x),
              lambda n: r"\left(" + pw(a, n) + "x+" + ("(" + n + ")" if len(n) > 1 else n) + pw(a, ("k" if n == "k+1" else "k-1" if n == "k" else "n-1")) + r"\right)e^{" + nice(a*x) + "}",
              lambda: pw(a, "k") + "e^{" + nice(a*x) + "}" + ("+" if a == 1 else "-" if a == -1 else "+" + par(Integer(a))) + r"\left(" + pw(a, "k") + "x+k" + pw(a, "k-1") + r"\right)e^{" + nice(a*x) + "}", 1))
    F.append(("inv", 1/lin(ap, c), lambda n: (-1)**n*sp.factorial(n)*Integer(ap)**n/lin(ap, c)**(n+1),
              lambda n: r"\frac{(-1)^{" + n + "}(" + n + ")!\\," + pw(ap, n) + r"}{\left(" + up + r"\right)^{" + n + "+1}}",
              lambda: r"(-1)^{k}k!\," + pw(ap, "k") + r"\cdot\frac{-(k+1)" + cap + r"}{\left(" + up + r"\right)^{k+2}}", 1))
    F.append(("ln", log(lin(ap, c)), lambda n: (-1)**(n-1)*sp.factorial(n-1)*Integer(ap)**n/lin(ap, c)**n,
              lambda n: r"\frac{(-1)^{" + n + "-1}(" + n + "-1)!\\," + pw(ap, n) + r"}{\left(" + up + r"\right)^{" + n + "}}",
              lambda: r"(-1)^{k-1}(k-1)!\," + pw(ap, "k") + r"\cdot\frac{-k" + cap + r"}{\left(" + up + r"\right)^{k+1}}", 1))
    F.append(("sin", sin(lin(ap, b)), lambda n: Integer(ap)**n*sin(lin(ap, b) + n*pi/2),
              lambda n: pw(ap, n) + r"\sin\left(" + ln_(ap, b) + "+" + ("(" + n + ")" if len(n) > 1 else n) + r"\frac{\pi}{2}\right)",
              lambda: pw(ap, "k+1") + r"\cos\left(" + ln_(ap, b) + r"+k\frac{\pi}{2}\right)", 1))
    F.append(("cos", cos(lin(ap, b)), lambda n: Integer(ap)**n*cos(lin(ap, b) + n*pi/2),
              lambda n: pw(ap, n) + r"\cos\left(" + ln_(ap, b) + "+" + ("(" + n + ")" if len(n) > 1 else n) + r"\frac{\pi}{2}\right)",
              lambda: "-" + pw(ap, "k+1") + r"\sin\left(" + ln_(ap, b) + r"+k\frac{\pi}{2}\right)", 1))
    A = rng.choice([2, 3, 5, 7])
    F.append(("ax", Integer(A)**lin(1, c), lambda n: log(A)**n*Integer(A)**lin(1, c),
              lambda n: r"(\ln " + str(A) + ")^{" + n + "}" + str(A) + "^{" + ln_(1, c) + "}",
              lambda: r"(\ln " + str(A) + r")^{k}\cdot " + str(A) + "^{" + ln_(1, c) + r"}\ln " + str(A), 1))
    F.append(("sin2", sin(ap*x)**2, lambda n: 2**(n-1)*Integer(ap)**n*sin(2*ap*x + (n-1)*pi/2),
              lambda n: "2^{" + n + "-1}" + pw(ap, n) + r"\sin\left(" + nice(2*ap*x) + "+(" + n + r"-1)\frac{\pi}{2}\right)",
              lambda: "2^{k-1}" + pw(ap, "k") + r"\cdot " + str(2*ap) + r"\cos\left(" + nice(2*ap*x) + r"+(k-1)\frac{\pi}{2}\right)", 1))
    F.append(("cos2", cos(ap*x)**2, lambda n: 2**(n-1)*Integer(ap)**n*cos(2*ap*x + n*pi/2),
              lambda n: "2^{" + n + "-1}" + pw(ap, n) + r"\cos\left(" + nice(2*ap*x) + "+" + ("(" + n + ")" if len(n) > 1 else n) + r"\frac{\pi}{2}\right)",
              lambda: "-2^{k-1}" + pw(ap, "k") + r"\cdot " + str(2*ap) + r"\sin\left(" + nice(2*ap*x) + r"+k\frac{\pi}{2}\right)", 1))
    F.append(("inv2", 1/lin(ap, c)**2, lambda n: (-1)**n*sp.factorial(n+1)*Integer(ap)**n/lin(ap, c)**(n+2),
              lambda n: r"\frac{(-1)^{" + n + "}(" + n + "+1)!\\," + pw(ap, n) + r"}{\left(" + up + r"\right)^{" + n + "+2}}",
              lambda: r"(-1)^{k}(k+1)!\," + pw(ap, "k") + r"\cdot\frac{-(k+2)" + cap + r"}{\left(" + up + r"\right)^{k+3}}", 1))
    F.append(("sc", sin(ap*x)*cos(ap*x), lambda n: 2**(n-1)*Integer(ap)**n*sin(2*ap*x + n*pi/2),
              lambda n: "2^{" + n + "-1}" + pw(ap, n) + r"\sin\left(" + nice(2*ap*x) + "+" + ("(" + n + ")" if len(n) > 1 else n) + r"\frac{\pi}{2}\right)",
              lambda: "2^{k-1}" + pw(ap, "k") + r"\cdot " + str(2*ap) + r"\cos\left(" + nice(2*ap*x) + r"+k\frac{\pi}{2}\right)", 1))
    return F

def fix_tex(t):
    t = t.replace("k+1+1", "k+2").replace("(k+1-1)!", "k!").replace("k+1-1", "k").replace("(1-1)!", "0!").replace("(k)", "k")
    return t
# Each induction on sin or cos moves through this identity: state it in the base case and in the step.
ID_C = r"$\cos\theta=\sin\left(\theta+\frac{\pi}{2}\right)$"
ID_S = r"$-\sin\theta=\cos\left(\theta+\frac{\pi}{2}\right)$"
IDENT = {"sin": ID_C, "cos": ID_S, "sin2": ID_C, "cos2": ID_S, "sc": ID_C}
def at_one(tex):
    return tex("1").replace("^{1-1}", "^{0}").replace("2^{0}", "").replace("^{1}", "").replace("+1\\frac", "+\\frac").replace("+(1-1)\\frac{\\pi}{2}", "")
def base_case(name, d1, tex, f):
    """the case n=1, with each move written out"""
    F1 = at_one(tex); ap = abs(sp.diff(f.args[0] if name in ("sin", "cos") else f.atoms(sin, cos).pop().args[0], x))
    z = nice(2*ap*x); ca = "" if ap == 1 else str(ap)
    if name == "sin2":
        mid = f"={ca}\\sin {z}"
    elif name == "cos2":
        mid = f"=-{ca}\\sin {z}"
    elif name == "sc":
        mid = f"={ca}\\cos {z}"
    else:
        mid = ""
    head = pk(f"ចំពោះ $n=1$ យើងមាន $f'(x)={nice(d1)}{mid}$ ។", f"ពេល $n=1$ ៖ ដេរីវេទី១ គឺ $f'(x)={nice(d1)}{mid}$ ។")
    if name == "sin2":
        return head + f" នេះគឺជា $f'(x)={F1}$ ដែលត្រូវនឹងរូបមន្ត ។"
    return head + f" ដោយ {IDENT[name]} គេបាន $f'(x)={F1}$ ដែលត្រូវនឹងរូបមន្ត ។"

def gen_nth(each=8):
    keys = [r[0] for r in nth_families()]; cnt = {k: 0 for k in keys}
    for _ in range(each * 14):
        for name, f, fm, tex, mid, n0 in nth_families():
            if cnt[name] >= each: continue
            key = "n" + str(f)
            if key in seen or f.is_number: continue
            n_ = "f"; d1 = simp(sp.diff(f, x)); d2 = simp(sp.diff(f, x, 2)); d3 = simp(sp.diff(f, x, 3))
            Fn, Fk, Fk1 = tex("n"), fix_tex(tex("k")), fix_tex(tex("k+1"))
            mode = pk("prove", "prove", "find", "eval")
            chk = [check(f"diff({s(f)},x,{i})", s(fm(i)), f"n={i}") for i in (1, 2, 3, 4, 5)]
            dm_ = auto_dom(f)
            if name in IDENT:
                base = base_case(name, d1, tex, f)
            else:
                base = pk(f"ចំពោះ $n=1$ យើងមាន $f'(x)={nice(d1)}$ ដែលត្រូវនឹងរូបមន្ត ។", f"ពេល $n=1$ ៖ ដេរីវេទី១ គឺ $f'(x)={nice(d1)}$ ហើយរូបមន្តក៏ឱ្យលទ្ធផលដូចគ្នា ។ ដូច្នេះវាពិតចំពោះ $n=1$ ។")
            md = mid(); glue = (f"ដោយ {IDENT[name]} គេបាន៖\n" if name in IDENT else "")
            last = "" if md.rsplit("=", 1)[-1].strip() == Fk1.strip() else f"{glue}$$={Fk1}$$\n"
            step = (pk(f"ឧបមាថារូបមន្តពិតចំពោះ $n=k$ ដែល $k\\ge1$ គឺ", f"សន្មតថារូបមន្តនេះពិតចំពោះ $n=k$ មានន័យថា") + f" $$f^{{(k)}}(x)={Fk}$$" +
                    "\n" + pk("យើងត្រូវស្រាយថាវាពិតចំពោះ $n=k+1$ ។ ធ្វើដេរីវេអង្គទាំងពីរ គេបាន៖", "ធ្វើដេរីវេអង្គទាំងពីរម្តងទៀត យើងបាន៖") +
                    f"\n$$f^{{(k+1)}}(x)=\\left[f^{{(k)}}(x)\\right]'={md}$$\n{last}" + "នេះគឺជារូបមន្តពេល $n=k+1$ ។")
            end = "ដូចនេះ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ គេបាន " + BX(f"f^{{(n)}}(x)={Fn}") + " ។"
            ans = f"f^{{(n)}}(x)={Fn}"
            if mode == "prove":
                prob = pk(f"គេឱ្យ {DEF('f',f)} ។ ស្រាយបញ្ជាក់ថា ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ $$f^{{(n)}}(x)={Fn}$$",
                          f"បង្ហាញថាដេរីវេទី $n$ នៃអនុគមន៍ {DEF('f',f)} គឺ $f^{{(n)}}(x)={Fn}$ ចំពោះគ្រប់ $n\\ge1$ ។")
                sol = "\n".join([dm_] + [base, step, end] if dm_ else [base, step, end])
            else:
                head = pk("គណនាដេរីវេដំបូងៗ ដើម្បីមើលទម្រង់ ។", "ដំបូង យើងគណនាដេរីវេបីដំបូង ។")
                first = [head, f"$$f'(x)={nice(d1)}$$", f"$$f''(x)={nice(d2)}$$", f"$$f'''(x)={nice(d3)}$$"]
                rest = [pk(f"យើងឃើញទម្រង់ទូទៅគឺ $f^{{(n)}}(x)={Fn}$ ។ ស្រាយបញ្ជាក់រូបមន្តនេះ ។", f"ពីលទ្ធផលខាងលើ យើងអាចទាយថា $f^{{(n)}}(x)={Fn}$ ។ យើងស្រាយបញ្ជាក់ដូចខាងក្រោម ។"), base, step, end]
                if mode == "find":
                    prob = pk(f"គេមានអនុគមន៍ {DEF('f',f)} ។\nក. គណនា $f'(x)$ , $f''(x)$ និង $f'''(x)$ ។\nខ. ទាញរកដេរីវេទី $n$ នៃ $f$ ហើយស្រាយបញ្ជាក់លទ្ធផល ។",
                              f"រករូបមន្តនៃដេរីវេទី $n$ នៃអនុគមន៍ {DEF('f',f)} ។")
                    if has_parts(prob):
                        d123 = f"f'(x)={nice(d1)},\\ f''(x)={nice(d2)},\\ f'''(x)={nice(d3)}"
                        first.append("ដូចនេះ " + " , ".join(BX(q) for q in (f"f'(x)={nice(d1)}", f"f''(x)={nice(d2)}", f"f'''(x)={nice(d3)}")) + " ។")
                        ans = d123 + ",\\ " + ans
                        chunks = [first, rest]
                    else:
                        chunks = [first + rest]
                else:
                    m_ = rng.randint(6, 9); x0 = Integer(0) if name not in () else Integer(0)
                    val = fm(m_).subs(x, x0)
                    if val.has(sp.zoo, sp.nan): continue
                    val = sp.simplify(val); mt = f"f^{{({m_})}}(0)"
                    prob = f"គេឱ្យ {DEF('f',f)} ។\nក. រករូបមន្តនៃ $f^{{(n)}}(x)$ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ។\nខ. ទាញរកតម្លៃ ${mt}$ ។"
                    chunks = [first + rest, [f"ជំនួស $n={m_}$ និង $x=0$ ក្នុងរូបមន្តខាងលើ គេបាន " + BX(f"{mt}={nice(val)}") + " ។"]]
                    chk.append(check(f"subs(diff({s(f)},x,{m_}),x,0)", s(val), "value")); ans += f",\\ {mt}={nice(val)}"
                sol = "\n".join(parts(prob, chunks, pre=[dm_]))
            emit("nth_derivative", pk("hard", "bacii"), prob, sol, ans, chk, key=key)
            seen.add(str(f)); cnt[name] += 1

# ---------- E: differential relations ----------
NSX = {"diff": sp.diff, "x": x, "exp": exp, "log": log, "sin": sin, "cos": cos, "tan": tan, "sqrt": sqrt, "pi": pi, "E": E}
def relation(sub, f, ytex, terms, target, common=1, dom="", dif="medium", name="y"):
    """terms: list of (tex, template with {f}). ytex: relation left side tex."""
    vals = []
    lhs = "+".join("(" + t.replace("{f}", "(" + s(f) + ")") + ")" for _, t in terms)
    for _, t in terms:
        vals.append(sp.sympify(t.replace("{f}", "(" + s(f) + ")"), locals=NSX))
    tt = nice(target); rel = f"{ytex}={tt}"
    n2 = any("x,2" in t for _, t in terms)
    y1, y2 = "y'", "y''"
    L1, d1 = explain(f, y1)
    C1 = [pk("គណនាដេរីវេទី១ ។", "ដំបូងរក $y'$ ។", "យើងមាន $y=" + nice(f) + "$ ។")] + L1; C2 = []
    chk = [check(f"diff({s(f)},x)", s(d1), "y'")]
    if n2:
        L2, d2 = explain(d1, y2)
        C1.append(pk("គណនាដេរីវេទី២ ។", "បន្តរក $y''$ ។", "ធ្វើដេរីវេម្តងទៀត ។"))
        C1 += L2
        chk.append(check(f"diff({s(f)},x,2)", s(d2), "y''"))
    def jn(es):
        out = ""
        for i, e in enumerate(es):
            t = nice(e)
            out += t if (i == 0 or t.startswith("-")) else "+" + t
        return out
    C2.append(pk("ជំនួសចូលអង្គខាងឆ្វេង គេបាន៖", "យកទៅជំនួសក្នុងកន្សោមខាងឆ្វេង យើងបាន៖", "ជំនួសចូលក្នុងកន្សោម $" + ytex + "$ គេបាន៖"))
    disp = [simp(v) for v in vals]
    eq = f"$${ytex}={jn(disp)}$$"
    C2.append(eq)
    if common != 1 and sp.count_ops(common) > 0:
        c_t = nice(common)
        C2.append(f"$$={c_t}\\left[{jn([sp.expand(v / common) for v in vals])}\\right]$$")
    if jn(disp) != tt:
        C2.append(f"$$={tt}$$")
    C2.append(pk("ដូចនេះ " + BX(rel) + " ។", "នោះបញ្ជាក់ថា " + BX(rel) + " ។", "ដូចនេះ ទំនាក់ទំនងត្រូវបានផ្ទៀងផ្ទាត់ គឺ " + BX(rel) + " ។"))
    chk.append(check(lhs, s(target), "relation"))
    fd = f"$y={nice(f)}$"
    if n2 and rng.random() < .35:
        prob = f"គេឱ្យអនុគមន៍ {fd} ។\nក. គណនា $y'$ និង $y''$ ។\nខ. ផ្ទៀងផ្ទាត់ថា ${rel}$ ។"; dif = "bacii"
    else:
        prob = pk(f"គេឱ្យអនុគមន៍ {fd} ។ បង្ហាញថា ${rel}$ ។", f"ផ្ទៀងផ្ទាត់ថាអនុគមន៍ {fd} ផ្ទៀងផ្ទាត់ទំនាក់ទំនង $${rel}$$",
                  f"ស្រាយបញ្ជាក់ថា ${rel}$ ដោយដឹងថា {fd} ។", f"ចំពោះអនុគមន៍ {fd} ចូរបង្ហាញថា ${rel}$ ។",
                  f"គេមាន {fd} ។ គណនា $y'$ រួចបង្ហាញថា ${rel}$ ។" if not n2 else f"គេមាន {fd} ។ គណនា $y'$ , $y''$ រួចបង្ហាញថា ${rel}$ ។")
    asks = "គណនា $y'$" in prob                               # a question that asks for y', y'' gets them boxed and in the answer
    ds_ = [f"y'={nice(d1)}"] + ([f"y''={nice(d2)}"] if n2 else [])
    if asks:
        C1.append("ដូចនេះ " + " និង ".join(BX(q) for q in ds_) + " ។")
    ans = (",\\ ".join(ds_) + ",\\ " if asks else "") + rel
    two = has_parts(prob)
    emit(sub, dif, prob, "\n".join(parts(prob, [C1, C2] if two else [C1 + C2], pre=[auto_dom(f)])), ans, chk, key=str(f))

def sn(c):
    """signed integer, empty for 0"""
    return f"{c:+d}" if c else ""
def sg(c, t):
    """signed coefficient tex: c*t with leading sign"""
    if c == 0: return ""
    a = abs(c); m_ = "" if a == 1 else nice(a)
    return ("+" if c > 0 else "-") + m_ + t
def tm(c, sym, tmpl):
    return (sg(c, sym), f"{c}*" + tmpl)

def gen_rel(each=12):
    def r1():
        p, q = rng.sample([-4, -3, -2, -1, 1, 2, 3, 4, 5], 2); A, B = ri(-5, 5), ri(-5, 5)
        f = A*exp(p*x) + B*exp(q*x); S, P = p + q, p*q
        T = [("y''", "diff({f},x,2)")] + ([tm(-S, "y'", "diff({f},x)")] if S else []) + [tm(P, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0))
    def r2():
        r, A, B = ri(-4, 4), ri(-4, 4), ri(-5, 5); f = lin(A, B)*exp(r*x)
        T = [("y''", "diff({f},x,2)"), tm(-2*r, "y'", "diff({f},x)"), tm(r*r, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=exp(r*x))
    def r3():
        a, b, A, B = ri(-3, 3), rng.randint(1, 4), ri(-3, 3), ri(-3, 3); f = exp(a*x)*(A*cos(b*x) + B*sin(b*x))
        T = [("y''", "diff({f},x,2)"), tm(-2*a, "y'", "diff({f},x)"), tm(a*a + b*b, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=exp(a*x), dif="hard")
    def r4():
        w, A, B = rng.randint(1, 6), ri(-5, 5), ri(-5, 5); f = A*cos(w*x) + B*sin(w*x)
        T = [("y''", "diff({f},x,2)"), tm(w*w, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0))
    def r5():
        k = ri(-4, 4); c = ri(1, 4); f = c*exp(k*x**2)
        T = [("y'", "diff({f},x)"), tm(-2*k, "xy", "x*{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=exp(k*x**2))
    def r6():
        k = ri(-5, 5); c = ri(1, 4); f = c*x*exp(k*x)
        T = [("xy'", "x*diff({f},x)"), (f"-(1{'+' if k>0 else '-'}{'' if abs(k)==1 else abs(k)}x)y", f"-(1+{k}*x)*{{f}}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=exp(k*x))
    def r7():
        a, b = rng.randint(1, 6), rng.randint(1, 8); f = log(lin(a, b)) + ri(-3, 3)
        T = [("y''", "diff({f},x,2)"), ("+(y')^{2}", "diff({f},x)**2")]
        relation("differential_relation", f, "y''+(y')^{2}", T, Integer(0), dom=f"ចំពោះ ${nice(lin(a,b))}>0$ អនុគមន៍មានន័យ ។")
    def r8():
        a = rng.randint(1, 5); f = log(cos(a*x)); c = rng.randint(1, 3)
        T = [("y''", "diff({f},x,2)"), ("+(y')^{2}", "diff({f},x)**2")]
        relation("differential_relation", f, "y''+(y')^{2}", T, Integer(-a*a), dom="យើងពិនិត្យលើចន្លោះដែល $\\cos " + nice(a*x) + ">0$ ។", dif="hard")
    def r9():
        a = rng.randint(1, 6); f = tan(a*x)
        T = [("y'", "diff({f},x)"), (f"-{'' if a==1 else a}y^{{2}}", f"-{a}*({{f}})**2")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(a))
    def r10():
        a = rng.randint(1, 5); g = pk(sin, cos); c = ri(1, 4); f = c*g(a*log(x))
        T = [("x^{2}y''", "x**2*diff({f},x,2)"), ("+xy'", "x*diff({f},x)"), tm(a*a, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), dom="ចំពោះ $x>0$ អនុគមន៍មានន័យ ។", dif="hard")
    def r11():
        n = rng.randint(1, 5); c = ri(1, 5); f = c*x**n*log(x)
        T = [("xy'", "x*diff({f},x)"), tm(-n, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, c*x**n, dom="ចំពោះ $x>0$ អនុគមន៍មានន័យ ។")
    def r12():
        n, A, B = rng.randint(1, 4), ri(-4, 4), ri(-4, 4); f = (A + B*log(x))/x**n
        T = [("x^{2}y''", "x**2*diff({f},x,2)"), tm(2*n + 1, "xy'", "x*diff({f},x)"), tm(n*n, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=1/x**n, dom="ចំពោះ $x>0$ អនុគមន៍មានន័យ ។", dif="hard")
    def r12b():
        n, A, B = rng.randint(1, 4), ri(-4, 4), ri(-4, 4); f = (A + B*log(x))*x**n
        T = [("x^{2}y''", "x**2*diff({f},x,2)")] + ([tm(1 - 2*n, "xy'", "x*diff({f},x)")]) + [tm(n*n, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=x**n, dom="ចំពោះ $x>0$ អនុគមន៍មានន័យ ។", dif="hard")
    def r13():
        k = ri(-4, 4); f = 1/(1 + exp(k*x))
        T = [("y'", "diff({f},x)"), (sg(-k, "y^{2}"), f"{-k}*({{f}})**2"), tm(k, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0))
    def r14():
        a = ri(-4, 4); f = exp(a*sin(x))
        T = [("y'", "diff({f},x)"), (sg(-a, r"y\cos x"), f"{-a}*{{f}}*cos(x)")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=exp(a*sin(x)))
    def r15():
        a = rng.randint(1, 5); f = pk(sin(a*x)**2, cos(a*x)**2)
        tgt = Integer(2*a*a)
        T = [("y''", "diff({f},x,2)"), tm(4*a*a, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, tgt, dif="hard") if False else None
        d = sp.diff(f, x, 2) + 4*a*a*f
        relation("differential_relation", f, "".join(t[0] for t in T), T, tgt)
    def r16():
        k = ri(-4, 4); q = rng.randint(1, 1); f = log(1 + exp(k*x))
        T = [("y''", "diff({f},x,2)"), ("+(y')^{2}", "diff({f},x)**2"), tm(-k, "y'", "diff({f},x)")]
        relation("differential_relation", f, "y''+(y')^{2}" + T[2][0], T, Integer(0), dif="hard")
    def r17():
        a = rng.randint(1, 9); f = sqrt(x**2 + a)
        T = [("yy''", "({f})*diff({f},x,2)"), ("+(y')^{2}", "diff({f},x)**2")]
        relation("differential_relation", f, "yy''+(y')^{2}", T, Integer(1), dif="hard")
    def r18():
        a = ri(-5, 5); c = ri(1, 4); f = c*exp(a*x)/x
        T = [("xy'", "x*diff({f},x)"), (f"+(1{sg(-a,'x')})y", f"(1-{a}*x)*{{f}}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=exp(a*x)/x, dom="ចំពោះ $x\\neq0$ អនុគមន៍មានន័យ ។")
    def r21():
        a, b, c, r = ri(-5, 5), ri(-5, 5), ri(-4, 4), ri(-3, 3); f = a*x + b + c*exp(r*x)
        T = [("y''", "diff({f},x,2)"), tm(-r, "y'", "diff({f},x)")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(-r*a))
    def r22():
        w = rng.randint(1, 5); c = ri(1, 4); g = pk(sin, cos); f = c*x*g(w*x)
        T = [("y''", "diff({f},x,2)"), tm(w*w, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, simp(sp.expand(sp.diff(f, x, 2) + w*w*f)))
    def r23():
        r = ri(-4, 4); c = ri(1, 3); f = c*x**2*exp(r*x)
        T = [("y''", "diff({f},x,2)"), tm(-2*r, "y'", "diff({f},x)"), tm(r*r, "y", "{f}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, 2*c*exp(r*x), common=exp(r*x))
    def r24():
        a = rng.randint(1, 9); f = log(x + sqrt(x**2 + a))
        T = [(f"(x^{{2}}+{a})y''", f"(x**2+{a})*diff({{f}},x,2)"), ("+xy'", "x*diff({f},x)")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), dif="hard")
    def r25():
        a = rng.randint(1, 5); g = pk(sin, cos); c = ri(1, 3); f = c*g(a*x)/x
        T = [("xy''", "x*diff({f},x,2)"), ("+2y'", "2*diff({f},x)"), (sg(a*a, "xy"), f"{a*a}*x*{{f}}")]
        relation("differential_relation", f, "".join(t[0] for t in T), T, Integer(0), common=1/x**2, dom="ចំពោះ $x\\neq0$ អនុគមន៍មានន័យ ។", dif="hard")
    def r26():
        a = rng.randint(1, 7); f = log((a + x)/(a - x))
        T = [(f"({a*a}-x^{{2}})y'", f"({a*a}-x**2)*diff({{f}},x)")]
        relation("differential_relation", f, T[0][0], T, Integer(2*a), dom=f"អនុគមន៍កំណត់លុះត្រាតែ $\\frac{{{a}+x}}{{{a}-x}}>0$ គឺ $-{a}<x<{a}$ ។")
    fams = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r12b, r13, r14, r15, r16, r17, r18, r21, r22, r23, r24, r25, r26]
    caps = {r1: 30, r2: 30, r3: 30, r4: 24, r12: 22, r12b: 22, r21: 18, r22: 18}
    for fn in fams:
        cap = caps.get(fn, each); b4 = len(rows)
        for _ in range(cap * 6):
            if len(rows) - b4 >= cap: break
            try:
                fn()
            except ValueError as ex:
                pass

# ---------- H: variation tables ----------
def window(f, lo, hi, crit=()):
    """y range of a graph. With critical values given the range is built round them, so a minimum stays visible
    however fast the curve runs away elsewhere."""
    fn = sp.lambdify(x, f, "numpy"); xs = np.linspace(lo, hi, 400)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(np.asarray(fn(xs), dtype=float), xs.shape)
    ys = ys[np.isfinite(ys)]
    p_lo, p_hi = np.percentile(ys, 4), np.percentile(ys, 92)
    if not len(crit):
        a = min(p_lo, 0) - 1; b = max(p_hi, 0) + 1
        return int(np.floor(a)), int(np.ceil(b))
    c = [float(sp.N(v)) for v in crit]; a0, b0 = min(c), max(c)
    pad = max(.5, .35*(b0 - a0), .1*max(abs(a0), abs(b0)))
    a = min(a0 - pad, max(p_lo, a0 - 3*pad)); b = max(b0 + pad, min(p_hi, b0 + 3*pad))
    if a > 0 and a < 1.5*(b - a): a = -.5
    if b < 0 and -b < 1.5*(b - a): b = .5
    return float(np.floor(a*2)/2), float(np.ceil(b*2)/2)

def T(v):
    if v == oo: return r"+\infty"
    if v == -oo: return r"-\infty"
    return nice(v)
def iv(a, b): return f"\\left({T(a)};{T(b)}\\right)"

def study(sub, f, name, Dtex, sign_line, pts, signs, ends, limtex, xr, dif="bacii", pre="", closed=False, extra_chk=()):
    """pts: increasing list including end points; signs per interval; ends=(value at left, value at right)."""
    y = labs(name)
    L, ds = explain(f, y[1])
    roots = pts[1:-1]; vals = [ends[0]] + [sp.simplify(f.subs(x, r)) for r in roots] + [ends[1]]
    cols = [T(p) for p in pts]
    fp = [""]; fv = [T(vals[0])]
    for i, sgn in enumerate(signs):
        fp.append(sgn); fv.append(r"\nearrow" if sgn == "+" else r"\searrow")
        fp.append("0" if i < len(signs) - 1 else ""); fv.append(T(vals[i + 1]))
    tab = variation_table(cols, fp, fv, name=name if name != "y" else "y")
    if name == "y":
        tab = tab.replace("y'(x)", "y'").replace("y(x)", "y")
    C1 = [pk("គណនាដេរីវេទី១ ។", "ដេរីវេទី១៖", "ទិសដៅអថេរភាព៖ គណនាដេរីវេ ។")] + L + ["ដូចនេះ " + BX(y[1] + "=" + nice(ds)) + " ។"]
    C2 = [sign_line]
    if roots:
        C2.append(f"${y[1]}=0$ " + pk("ផ្តល់ឱ្យ ", "ពេល ") + " ឬ ".join(f"$x={nice(r)}$" for r in roots) + " ។")
    if limtex:
        C2.append("លីមីត៖ " + limtex)
    C2 += [pk("តារាងអថេរភាព៖", "សង់តារាងអថេរភាព៖", "គេបានតារាងអថេរភាពដូចខាងក្រោម៖"), "$$" + tab + "$$"]
    ups = [iv(pts[i], pts[i+1]) for i, g in enumerate(signs) if g == "+"]; dn = [iv(pts[i], pts[i+1]) for i, g in enumerate(signs) if g == "-"]
    con = []
    if ups: con.append("អនុគមន៍កើនលើ " + " និង ".join("$" + t + "$" for t in ups))
    if dn: con.append("ចុះលើ " + " និង ".join("$" + t + "$" for t in dn))
    ext = []; chk = [check(f"diff({s(f)},x)", s(ds), "derivative")]
    for i, r in enumerate(roots):
        v = vals[i + 1]
        chk.append(check(f"subs(diff({s(f)},x),x,{s(r)})", "0", "critical point")); chk.append(check(f"subs({s(f)},x,{s(r)})", s(v), "extreme value"))
        if signs[i] != signs[i + 1]:
            w = "អតិបរមា" if signs[i] == "+" else "អប្បបរមា"
            ext.append(f"អនុគមន៍មាន{w}ស្មើនឹង {M(v)} ត្រង់ $x={nice(r)}$")
    conclusion = "ដូចនេះ " + " ហើយ".join(con) + " ។" + ((" " + " ហើយ".join(ext) + " ។") if ext else "")
    C2.append(conclusion)
    chk += list(extra_chk)
    fd = DEF(name, f)
    asky = pk(f"គណនាដេរីវេនៃ {fd} រួចសង់តារាងអថេរភាពនៃ ${name}$ ។", f"គេឱ្យអនុគមន៍ {fd} ។ សិក្សាអថេរភាព រួចសង់តារាងអថេរភាពនៃ ${name}$ ។",
              f"គេមានអនុគមន៍ {fd} ។\nក. គណនា ${y[1]}$ ។\nខ. សង់តារាងអថេរភាពនៃ ${name}$ ។", f"សិក្សាទិសដៅអថេរភាពនៃអនុគមន៍ {fd} ហើយសង់តារាងអថេរភាព ។")
    if closed:
        asky = pk(f"គេឱ្យ {fd} លើចន្លោះ ${Dtex_short(pts)}$ ។ សិក្សាអថេរភាព រួចសង់តារាងអថេរភាពនៃ ${name}$ ។", f"លើចន្លោះ ${Dtex_short(pts)}$ គេមានអនុគមន៍ {fd} ។ សង់តារាងអថេរភាពនៃ ${name}$ ។")
    answer = f"{y[1]}={nice(ds)}"
    r = emit(sub, dif, asky, "\n".join(parts(asky, [C1, C2] if has_parts(asky) else [C1 + C2], pre=[pre, Dtex])), answer, chk, diagrams=[{"type": "variation_table", "latex": tab, "image": None, "alt_km": "តារាងអថេរភាពនៃអនុគមន៍"}], key=str(f))
    if r and xr and rng.random() < .55:
        lo, hi = float(xr[0]), float(xr[1]); pts_ = [(rr, v) for rr, v in zip(roots, vals[1:-1])]
        a, b = window(f, lo + .02, hi, [v for _, v in pts_])
        graph(r, f, xr[0], xr[1], a, b, "ក្រាបនៃអនុគមន៍ ដោយបង្ហាញចំណុចបរមា" if pts_ else "ក្រាបនៃអនុគមន៍", points=pts_,
              d0=(xr[2] if len(xr) > 2 else None), d1=(xr[3] if len(xr) > 3 else None))
    return r
def Dtex_short(pts): return f"\\left[{T(pts[0])};{T(pts[-1])}\\right]"

POS = "ដែនកំណត់ $D=(0;+\\infty)$ ព្រោះ $\\ln x$ មានន័យតែចំពោះ $x>0$ ។"
RR = "ដែនកំណត់ $D=IR$ ។"
def lims(f, pts_tex):
    out = []; chk = []
    for pt, side, v in pts_tex:
        out.append(f"$\\lim_{{x\\to {side}}}{nice(f) if len(nice(f))<30 else 'f(x)'}={T(v)}$")
    return " , ".join(out) + " ។"
def gen_var():
    # V1 (ax+b)e^{kx}
    for _ in range(90):
        k = rng.choice([1, -1, 2, -2]); a = ri(-3, 3); r = rng.randint(-3, 3); b = -a*Q(1 + k*r, k)
        f = (a*x + b)*exp(k*x); n = pk("f", "g", "h")
        l1, l2 = sp.limit(f, x, -oo), sp.limit(f, x, oo); up = k*a > 0
        sign = f"ដោយ {M(exp(k*x))} $>0$ ជានិច្ច នោះ ${n}'(x)$ មានសញ្ញាតាម {M(k*a*x + a + k*b)} ។"
        study("variation_exp", f, n, RR, sign, [-oo, Integer(r) , oo], ["-", "+"] if up else ["+", "-"], (l1, l2),
              f"$\\lim_{{x\\to-\\infty}}{n}(x)={T(l1)}$ និង $\\lim_{{x\\to+\\infty}}{n}(x)={T(l2)}$ ។", (r - 4, r + 3),
              extra_chk=[check(f"limit({s(f)},x,-oo)", s(l1), "limit"), check(f"limit({s(f)},x,oo)", s(l2), "limit")])
        if sum(1 for q in rows if q["subtopic"] == "variation_exp") >= 40: break
    # V7 quadratic times exp
    c0 = len(rows)
    for r1 in range(-4, 3):
        for r2 in range(r1 + 1, 5):
            for k in (1, -1):
                if len(rows) - c0 >= 40 or rng.random() < .3: continue
                if k == 1: b = -(r1 + r2) - 2; c = r1*r2 - b; sg_ = ["+", "-", "+"]
                else: b = 2 - (r1 + r2); c = r1*r2 + b; sg_ = ["-", "+", "-"]
                f = (x**2 + b*x + c)*exp(k*x); n = pk("f", "g")
                l1, l2 = sp.limit(f, x, -oo), sp.limit(f, x, oo)
                q = sp.expand(sp.diff(f, x)/exp(k*x))
                sign = f"ដោយ {M(exp(k*x))} $>0$ ជានិច្ច នោះសញ្ញានៃ ${n}'(x)$ យកតាមសញ្ញានៃត្រីធា {M(q)} ។"
                study("variation_exp", f, n, RR, sign, [-oo, Integer(r1), Integer(r2), oo], sg_, (l1, l2),
                      f"$\\lim_{{x\\to-\\infty}}{n}(x)={T(l1)}$ និង $\\lim_{{x\\to+\\infty}}{n}(x)={T(l2)}$ ។", (r1 - 3, r2 + 2),
                      extra_chk=[check(f"limit({s(f)},x,oo)", s(l2), "limit")])
    # V2 cx - a ln x + b
    for c in (1, 2, 3):
        for a in range(1, 7):
            for b in (0, 1, -2, 3):
                if a % c and rng.random() < .5: continue
                if rng.random() < .55: continue
                f = c*x - a*log(x) + b; r = Q(a, c); n = pk("f", "g", "h")
                sign = f"ដោយ $x>0$ នោះ ${n}'(x)$ មានសញ្ញាតាមភាគយក {M(c*x - a)} ។"
                study("variation_log", f, n, POS, sign, [Integer(0), r, oo], ["-", "+"], (oo, oo),
                      f"$\\lim_{{x\\to0^{{+}}}}{n}(x)=+\\infty$ និង $\\lim_{{x\\to+\\infty}}{n}(x)=+\\infty$ ។", (0, r + 5, .02),
                      extra_chk=[check(f"limit({s(f)},x,oo)", "oo", "limit")])
    # V3 x ln x - a x + b ; V4 (ln x + a)/x ; x^2 (ln x - a)
    for a in range(-2, 4):
        for b in (0, 1, -1, 2):
            f = x*log(x) - a*x + b; r = exp(a - 1); n = pk("f", "g")
            sign = f"សញ្ញានៃ ${n}'(x)$ ៖ បើ $0<x<{nice(r)}$ នោះ ${n}'(x)<0$ ហើយបើ $x>{nice(r)}$ នោះ ${n}'(x)>0$ ។"
            study("variation_log", f, n, POS, sign, [Integer(0), r, oo], ["-", "+"], (Integer(b), oo),
                  f"$\\lim_{{x\\to0^{{+}}}}{n}(x)={b}$ (ព្រោះ $\\lim_{{x\\to0^{{+}}}}x\\ln x=0$) និង $\\lim_{{x\\to+\\infty}}{n}(x)=+\\infty$ ។", (0, max(6, float(r)*1.6), .02),
                  extra_chk=[check(f"limit({s(f)},x,0)", str(b), "limit")])
    for a in range(-3, 4):
        for c in (1, 2, 3):
            f = c*(log(x) + a)/x; r = exp(1 - a); n = pk("f", "g", "h")
            sign = f"ដោយ $x^{{2}}>0$ នោះ ${n}'(x)$ មានសញ្ញាតាមភាគយក ។ ភាគយកវិជ្ជមានពេល $x<{nice(r)}$ និងអវិជ្ជមានពេល $x>{nice(r)}$ ។"
            study("variation_log", f, n, POS, sign, [Integer(0), r, oo], ["+", "-"], (-oo, Integer(0)),
                  f"$\\lim_{{x\\to0^{{+}}}}{n}(x)=-\\infty$ និង $\\lim_{{x\\to+\\infty}}{n}(x)=0$ ។", (0, 10, .05) if a > -1 else None,
                  extra_chk=[check(f"limit({s(f)},x,oo)", "0", "limit")])
    for a in (0, 1, 2, -1):
        for c in (1, 2):
            f = c*x**2*(log(x) - a); r = exp(a - Q(1, 2)); n = "f"
            sign = f"ដោយ $x>0$ សញ្ញានៃ $f'(x)$ យកតាមសញ្ញានៃ $2\\ln x{sg(1 - 2*a, '') or ''}{'' if abs(1-2*a)!=1 else '1'}$ ។"
            study("variation_log", f, n, POS, sign, [Integer(0), r, oo], ["-", "+"], (Integer(0), oo),
                  "$\\lim_{x\\to0^{+}}f(x)=0$ និង $\\lim_{x\\to+\\infty}f(x)=+\\infty$ ។", None, extra_chk=[check(f"limit({s(f)},x,oo)", "oo", "limit")])
    # V5 e^x - a x + b and e^{2x}-2a e^x
    for a in range(1, 10):
        for b in (0, 1, -1, 2):
            if rng.random() < .35: continue
            f = exp(x) - a*x + b; r = log(a); n = pk("f", "g")
            sign = f"${n}'(x)>0$ ពេល $e^{{x}}>{a}$ គឺ $x>{nice(r)}$ ហើយ ${n}'(x)<0$ ពេល $x<{nice(r)}$ ។"
            study("variation_exp", f, n, RR, sign, [-oo, r, oo], ["-", "+"], (oo, oo),
                  f"$\\lim_{{x\\to-\\infty}}{n}(x)=+\\infty$ និង $\\lim_{{x\\to+\\infty}}{n}(x)=+\\infty$ ។", (-3, 4),
                  extra_chk=[check(f"limit({s(f)},x,oo)", "oo", "limit"), check(f"limit({s(f)},x,-oo)", "oo", "limit")])
    for a in range(1, 7):
        for b in (0, 3, -2):
            f = exp(2*x) - 2*a*exp(x) + b; r = log(a); n = "f"
            sign = f"ដោយ $e^{{x}}>0$ នោះ $f'(x)$ មានសញ្ញាតាម $e^{{x}}-{a}$ ។"
            study("variation_exp", f, n, RR, sign, [-oo, r, oo], ["-", "+"], (Integer(b), oo),
                  f"$\\lim_{{x\\to-\\infty}}f(x)={b}$ និង $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។", None,
                  extra_chk=[check(f"limit({s(f)},x,-oo)", str(b), "limit")])
    # V8 ln(x^2+a), V11 c e^{-(x-p)^2}
    for a in range(1, 10):
        for c in (1, 2, 3):
            f = c*log(x**2 + a); n = pk("f", "g")
            sign = f"ដោយ {M(x**2 + a)} $>0$ នោះ ${n}'(x)$ មានសញ្ញាតាម $x$ ។"
            study("variation_log", f, n, RR, sign, [-oo, Integer(0), oo], ["-", "+"], (oo, oo),
                  f"$\\lim_{{x\\to\\pm\\infty}}{n}(x)=+\\infty$ ។", (-5, 5))
    for p in range(-3, 4):
        for c in (1, 2, 3, 4):
            f = c*exp(-(x - p)**2); n = pk("f", "h")
            sign = f"ដោយអនុគមន៍អិចស្ប៉ូណង់ស្យែលវិជ្ជមានជានិច្ច នោះ ${n}'(x)$ មានសញ្ញាតាម {M(p - x)} ។".replace("អិចស្ប៉ូណង់ស្យែល", "អ៊ិចស្ប៉ូណង់ស្យែល")
            study("variation_exp", f, n, RR, sign, [-oo, Integer(p), oo], ["+", "-"], (Integer(0), Integer(0)),
                  f"$\\lim_{{x\\to\\pm\\infty}}{n}(x)=0$ ។", (p - 3, p + 3), extra_chk=[check(f"limit({s(f)},x,oo)", "0", "limit")])
    # V10 e^x/(x+a) with forbidden value
    for a in range(-4, 5):
        for c in (1, 2, 3):
            f = c*exp(x)/(x + a); n = "f"; y = labs(n); L, ds = explain(f, y[1]); r = Integer(1 - a); v = sp.simplify(f.subs(x, r))
            P = -a
            cols = [r"-\infty", T(Integer(P)), T(r), r"+\infty"]
            fp = ["", "-", r"\|", "-", "0", "+", ""]
            fv = ["0", r"\searrow", r"-\infty\ \|\ +\infty", r"\searrow", T(v), r"\nearrow", r"+\infty"]
            tab = variation_table(cols, fp, fv)
            prob = pk(f"គេឱ្យអនុគមន៍ {DEF(n,f)} ។ គណនាដេរីវេ រួចសង់តារាងអថេរភាពនៃ $f$ ។", f"គណនាដេរីវេនៃ {DEF(n,f)} រួចសង់តារាងអថេរភាពនៃ $f$ ។")
            sol = "\n".join([f"អនុគមន៍កំណត់លុះត្រាតែ {M(x + a)} $\\neq0$ គឺ $D=IR-\\{{{P}\\}}$ ។"] + L +
                            ["ដូចនេះ " + BX(f"f'(x)={nice(ds)}") + " ។", f"ដោយ $e^{{x}}>0$ និង {M((x + a)**2)} $>0$ នោះ $f'(x)$ មានសញ្ញាតាម {M(x + a - 1)} ។", f"$f'(x)=0$ ពេល $x={nice(r)}$ ។",
                             f"លីមីត៖ $\\lim_{{x\\to-\\infty}}f(x)=0$ , $\\lim_{{x\\to{P}^{{-}}}}f(x)=-\\infty$ , $\\lim_{{x\\to{P}^{{+}}}}f(x)=+\\infty$ , $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។",
                             "តារាងអថេរភាព៖", "$$" + tab + "$$",
                             f"ដូចនេះ អនុគមន៍ចុះលើ $\\left(-\\infty;{P}\\right)$ និង $\\left({P};{nice(r)}\\right)$ កើនលើ $\\left({nice(r)};+\\infty\\right)$ ហើយមានអប្បបរមាស្មើនឹង {M(v)} ត្រង់ $x={nice(r)}$ ។"])
            emit("variation_exp", "bacii", prob, sol, f"f'(x)={nice(ds)}",
                 [check(f"diff({s(f)},x)", s(ds), "derivative"), check(f"subs({s(f)},x,{r})", s(v), "minimum"), check(f"subs(diff({s(f)},x),x,{r})", "0", "critical"),
                  check(f"limit({s(f)},x,oo)", "oo", "limit")],
                 diagrams=[{"type": "variation_table", "latex": tab, "image": None, "alt_km": "តារាងអថេរភាពនៃអនុគមន៍ ដែលមានតម្លៃហាមឃាត់មួយ"}], key=str(f))
    # V9 trig on an interval
    T2 = 2*pi
    trig = [(x - 2*sin(x), [Integer(0), pi/3, 5*pi/3, T2], ["-", "+", "-"], r"$f'(x)=1-2\cos x$ ដូច្នេះ $\cos x=\frac{1}{2}$ ផ្តល់ $x=\frac{\pi}{3}$ ឬ $x=\frac{5\pi}{3}$ ។"),
            (x + 2*sin(x), [Integer(0), 2*pi/3, 4*pi/3, T2], ["+", "-", "+"], r"$\cos x=-\frac{1}{2}$ ផ្តល់ $x=\frac{2\pi}{3}$ ឬ $x=\frac{4\pi}{3}$ ។"),
            (sin(x) + cos(x), [Integer(0), pi/4, 5*pi/4, T2], ["+", "-", "+"], r"$\cos x=\sin x$ មានន័យថា $\tan x=1$ ។"),
            (sin(x) - cos(x), [Integer(0), 3*pi/4, 7*pi/4, T2], ["+", "-", "+"], r"$\cos x=-\sin x$ មានន័យថា $\tan x=-1$ ។"),
            (2*cos(x) + x, [Integer(0), pi/6, 5*pi/6, pi], ["+", "-", "+"], r"$\sin x=\frac{1}{2}$ លើចន្លោះនេះ ។"),
            (sin(x)**2 - cos(x), [Integer(0), pi], ["+"], r"$f'(x)=\sin x(2\cos x+1)$ ។") ,
            (exp(x)*sin(x), [Integer(0), 3*pi/4, pi], ["+", "-"], r"ដោយ $e^{x}>0$ សញ្ញាអាស្រ័យលើ $\sin x+\cos x$ ។"),
            (exp(x)*cos(x), [Integer(0), pi/4, pi], ["+", "-"], r"ដោយ $e^{x}>0$ សញ្ញាអាស្រ័យលើ $\cos x-\sin x$ ។")]
    for f0, pts, sgs, note in trig[:5] + trig[6:]:
        for b in (0, 1, -1, 2):
            f = f0 + b
            e0, e1 = sp.simplify(f.subs(x, pts[0])), sp.simplify(f.subs(x, pts[-1]))
            study("variation_trig", f, "f", f"យើងសិក្សាលើចន្លោះ ${Dtex_short(pts)}$ ។", note, pts, sgs, (e0, e1), "", (float(pts[0]) - .5, float(pts[-1]) + .5, float(pts[0]), float(pts[-1])) if b == 0 else None, closed=True)

# ---------- F: find constants ----------
def lc(*terms):
    """linear combination of (coefficient, symbol text): no 1a, -1b, +-, 0a"""
    out = ""
    for c, sym in terms:
        c = sp.sympify(c)
        if c == 0: continue
        t_ = (sym if c == 1 else "-" + sym if c == -1 else nice(c) + sym) if sym else nice(c)
        out = pj(out, t_) if out else t_
    return out or "0"
def gen_const(each=30):
    b4 = len(rows)
    for _ in range(each * 3):                                # (ax+b)e^{kx} with given derivative
        a, b, k = ri(-5, 5), ri(-5, 5), ri(-3, 3); n = pk("F", "G"); f = lin(a, b)*exp(k*x); g = sp.diff(f, x); P = sp.expand(g/exp(k*x))
        p, q = P.coeff(x, 1), P.coeff(x, 0)
        A, B = sp.Symbol("a"), sp.Symbol("b")
        prob = pk(f"គេឱ្យ ${n}(x)=(ax+b){nice(exp(k*x))}$ និង $f(x)={nice(P*exp(k*x))}$ ។ កំណត់ចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ ${n}'(x)=f(x)$ ។",
                  f"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យអនុគមន៍ ${n}(x)=(ax+b){nice(exp(k*x))}$ មានដេរីវេ ${n}'(x)={nice(P*exp(k*x))}$ ។")
        sol = "\n".join([f"តាមរូបមន្តដេរីវេនៃផលគុណ គេបាន៖", f"$${n}'(x)=a{nice(exp(k*x))}+(ax+b){par(k*exp(k*x))}$$",
                         f"$$=\\left({lc((k, 'ax'), (1, 'a'), (k, 'b'))}\\right){nice(exp(k*x))}$$",
                         f"ដោយ {M(exp(k*x))} $\\neq0$ យើងផ្ទឹមមេគុណនៃពហុធាទាំងពីរ គេបាន៖",
                         f"$$\\begin{{cases}}{lc((k, 'a'))}={nice(p)}\\\\ {lc((1, 'a'), (k, 'b'))}={nice(q)}\\end{{cases}}$$",
                         f"ពីសមីការទី១ គេបាន $a={nice(a)}$ ។ ជំនួសក្នុងសមីការទី២ គេបាន $b={nice(b)}$ ។",
                         "ដូចនេះ " + BX(f"a={nice(a)},\\ b={nice(b)}") + " ។"])
        emit("find_constants", "medium", prob, sol, f"a={nice(a)},\\ b={nice(b)}", [check(f"diff({s(f)},x)", s(P*exp(k*x)), "derivative with found constants")], key=str(("c", f)))
        if len(rows) - b4 >= each: break
    b4 = len(rows)
    for _ in range(each * 3):                                # y''+py'+qy = g for y=(ax+b)e^{kx}
        a, b, k = ri(-4, 4), ri(-4, 4), ri(-2, 2); p, q = ri(-4, 4), ri(-5, 5)
        if k*k + p*k + q == 0: continue
        f = lin(a, b)*exp(k*x); g = sp.diff(f, x, 2) + p*sp.diff(f, x) + q*f; P = sp.expand(g/exp(k*x))
        c1 = k*k + p*k + q; c0 = 2*k + p
        rel = "y''" + sg(p, "y'") + sg(q, "y"); E_ = nice(exp(k*x))
        prob = pk(f"គេមានសមីការ ${rel}={nice(P*exp(k*x))}$ ។ រកចំនួនពិត $a$ , $b$ ដើម្បីឱ្យ $y=(ax+b){E_}$ ជាចម្លើយនៃសមីការនេះ ។",
                  f"កំណត់ចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យអនុគមន៍ $y=(ax+b){E_}$ ផ្ទៀងផ្ទាត់សមីការ ${rel}={nice(P*exp(k*x))}$ ។")
        d1t = f"\\left({lc((k, 'ax'), (1, 'a'), (k, 'b'))}\\right){E_}"; d2t = f"\\left({lc((k*k, 'ax'), (2*k, 'a'), (k*k, 'b'))}\\right){E_}"
        sol = "\n".join([f"យើងមាន $y=(ax+b){E_}$ ។", "គណនាដេរីវេទី១ និងទី២ ៖", f"$$y'={d1t}$$", f"$$y''={d2t}$$", "ជំនួសក្នុងសមីការ រួចចែកអង្គទាំងពីរនឹង " + f"${E_}\\neq0$ " + "ហើយរៀបតាមស្វ័យគុណនៃ $x$ គេបាន៖",
                         f"$${lc((c1, 'ax'), (c0, 'a'), (c1, 'b'))}={nice(P)}$$",
                         "ផ្ទឹមមេគុណ៖ " + f"${lc((c1, 'a'))}={nice(P.coeff(x,1))}$ និង ${lc((c0, 'a'), (c1, 'b'))}={nice(P.coeff(x,0))}$ ។",
                         "ដោះស្រាយ គេបាន " + BX(f"a={nice(a)},\\ b={nice(b)}") + " ។", f"ដូចនេះ អនុគមន៍ដែលត្រូវរកគឺ $y={nice(f)}$ ។"])
        if a == 0: continue
        emit("find_constants", "hard", prob, sol, f"a={nice(a)},\\ b={nice(b)}",
             [check(f"diff({s(f)},x,2)+({p})*diff({s(f)},x)+({q})*({s(f)})", s(P*exp(k*x)), "equation holds")], key=str(("c2", f, p, q)))
        if len(rows) - b4 >= each: break
    b4 = len(rows)
    for _ in range(each * 3):                                # y=a cos wx + b sin wx
        a, b, w = ri(-4, 4), ri(-4, 4), rng.randint(1, 3); p, q = ri(-3, 3), ri(-4, 4)
        c = q - w*w
        if c == 0: continue
        f = a*cos(w*x) + b*sin(w*x); g = sp.expand(sp.diff(f, x, 2) + p*sp.diff(f, x) + q*f)
        C, S_ = g.coeff(cos(w*x)), g.coeff(sin(w*x))
        rel = "y''" + sg(p, "y'") + sg(q, "y"); co, si = nice(cos(w*x)), nice(sin(w*x)); wt = "" if w == 1 else str(w)
        prob = f"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យអនុគមន៍ $y=a{co}+b{si}$ ផ្ទៀងផ្ទាត់សមីការ ${rel}={nice(g)}$ ។"
        pw_ = p*w
        sol = "\n".join([f"$$y'=-{wt}a{si}+{wt}b{co}$$", f"$$y''=-{w*w if w>1 else ''}a{co}-{w*w if w>1 else ''}b{si}$$", "ជំនួសក្នុងសមីការ រួចរៀបតាម " + f"${co}$ និង ${si}$ " + "គេបាន៖",
                         f"$$\\left({lc((c, 'a'), (pw_, 'b'))}\\right){co}+\\left({lc((-pw_, 'a'), (c, 'b'))}\\right){si}={nice(g)}$$",
                         "ផ្ទឹមមេគុណ គេបានប្រព័ន្ធសមីការ៖",
                         f"$$\\begin{{cases}}{lc((c, 'a'), (pw_, 'b'))}={nice(C)}\\\\ {lc((-pw_, 'a'), (c, 'b'))}={nice(S_)}\\end{{cases}}$$",
                         "ដោះស្រាយប្រព័ន្ធនេះ គេបាន " + BX(f"a={nice(a)},\\ b={nice(b)}") + " ។"])
        emit("find_constants", "hard", prob, sol, f"a={nice(a)},\\ b={nice(b)}",
             [check(f"diff({s(f)},x,2)+({p})*diff({s(f)},x)+({q})*({s(f)})", s(g), "equation holds")], key=str(("c3", f, p, q)))
        if len(rows) - b4 >= each: break

# ---------- G: tangent ----------
def gen_tan(each=7):
    def fam():
        a, k, b = ri(1, 4), ri(-3, 3), ri(-4, 4); q = rng.randint(1, 4); t = rng.choice([pi/6, pi/4, pi/3, pi/2])
        return [(log(lin(a, 1 - a)), Integer(1)), (x*log(x), Integer(1)), (x*log(x), E), (b*x + log(x), Integer(1)), (log(x)/x, Integer(1)), (log(x)/x, E), (log(x)**2 + b, E),
                (exp(k*x), Integer(0)), (x*exp(k*x), Integer(0)), (lin(a, b)*exp(x), Integer(0)), (exp(x) + b*x, Integer(0)), (exp(x - 1) + b, Integer(1)), (sin(a*x), Integer(0)), (sin(x) + b, t),
                (cos(x) + b, t), (tan(x), pi/4), (x*sin(x), pi/2), (log(x**2 + q), Integer(0)), (log(x**2 + 1) + b*x, Integer(1)), (exp(sin(x)), Integer(0)), (exp(x)/(x + q), Integer(0))]
    cnt = {}
    for _ in range(each * 16):
        for i, (f, x0) in enumerate(fam()):
            if cnt.get(i, 0) >= each: continue
            key = "t" + str(f) + str(x0)
            if key in seen or str(f) in seen: continue
            n = pk("f", "f", "g"); y = labs(n)
            L, ds = explain(f, y[1]); y0 = sp.simplify(f.subs(x, x0)); m_ = sp.simplify(ds.subs(x, x0)); tl = sp.expand(y0 + m_*(x - x0))
            pt = f"A\\left({nice(x0)};{nice(y0)}\\right)"
            prob = pk(f"គេឱ្យខ្សែកោង $(C)$ ៖ {DEF(n,f).replace(labs(n)[0], 'y')} ។ រកសមីការបន្ទាត់ប៉ះនៃខ្សែកោង $(C)$ ត្រង់ចំណុចដែលមានអាប់ស៊ីស $x_{{0}}={nice(x0)}$ ។",
                      f"រកសមីការបន្ទាត់ប៉ះនៃខ្សែកោងតាងអនុគមន៍ {DEF(n,f)} ត្រង់ចំណុច ${pt}$ ។",
                      f"គេមានអនុគមន៍ {DEF(n,f)} មានក្រាប $(C)$ ។\nក. គណនា ${y[1]}$ ។\nខ. សរសេរសមីការបន្ទាត់ប៉ះនឹង $(C)$ ត្រង់ចំណុចដែលមានអាប់ស៊ីស ${nice(x0)}$ ។")
            two = has_parts(prob); fx = y[1] + "=" + nice(ds)
            val = [f"ត្រង់ $x_{{0}}={nice(x0)}$ គេបាន $y_{{0}}={n}\\left({nice(x0)}\\right)={nice(y0)}$ និង {pk('មេគុណប្រាប់ទិស', 'ដេរីវេ')} ${n}'\\left({nice(x0)}\\right)={nice(m_)}$ ។",
                   "សមីការបន្ទាត់ប៉ះមានរាង $y-y_{0}=f'(x_{0})(x-x_{0})$ ។ ជំនួសតម្លៃ គេបាន៖".replace("f'", n + "'"),
                   f"$${tline(y0, m_, x0)}$$", "ដូចនេះ សមីការបន្ទាត់ប៉ះគឺ " + BX("y=" + nice(tl)) + " ។"]
            sol = "\n".join(parts(prob, [L + (["ដូចនេះ " + BX(fx) + " ។"] if two else []), val], pre=[auto_dom(f)]))
            r = emit("tangent_transcendental", "medium", prob, sol, (fx + ",\\ " if two else "") + "y=" + nice(tl),
                     [check(f"diff({s(f)},x)", s(ds), "derivative"), check(f"subs({s(f)},x,{s(x0)})", s(y0), "y0"), check(f"subs(diff({s(f)},x),x,{s(x0)})", s(m_), "slope"),
                      check(f"subs({s(f)},x,{s(x0)})+subs(diff({s(f)},x),x,{s(x0)})*(x-({s(x0)}))", s(tl), "tangent")], key=key)
            if r:
                seen.add(str(f)); cnt[i] = cnt.get(i, 0) + 1
                x0f = float(x0); lo, hi = (0 if f.has(log) and not f.has(x**2) else x0f - 3), x0f + 3
                a_, b_ = window(f, lo + .05, hi, [y0])
                graph(r, f, round(lo, 2), round(hi, 2), a_, b_, "ខ្សែកោង និងបន្ទាត់ប៉ះត្រង់ចំណុចដែលបានឱ្យ", tangent=tl, points=[(x0, y0)], d0=(.03 if lo == 0 else None))
    # tangent parallel to a line
    for a in range(-3, 4):
        for t in (2, 3, 4, 5):
            for b in (0, 1):
                f = exp(x) + a*x + b; m_ = a + t; x0 = log(t); y0 = t + a*log(t) + b; tl = sp.expand(y0 + m_*(x - x0)); c = rng.randint(-4, 4)
                prob = f"គេឱ្យ $f(x)={nice(f)}$ មានក្រាប $(C)$ ។ រកសមីការបន្ទាត់ប៉ះនឹង $(C)$ ដែលស្របនឹងបន្ទាត់ $y={nice(m_*x + c)}$ ។"
                sol = "\n".join([f"គេបាន $f'(x)={nice(sp.diff(f, x))}$ ។", f"បន្ទាត់ប៉ះស្របនឹងបន្ទាត់ដែលបានឱ្យ លុះត្រាតែមេគុណប្រាប់ទិសស្មើគ្នា គឺ $f'(x_{{0}})={m_}$ ។",
                                 f"$$e^{{x_{{0}}}}{sn(a)}={m_}$$", f"ដូច្នេះ $e^{{x_{{0}}}}={t}$ នោះ $x_{{0}}={nice(x0)}$ ។",
                                 f"$y_{{0}}=f\\left({nice(x0)}\\right)={nice(y0)}$ ។", f"$${tline(y0, Integer(m_), x0)}$$", "ដូចនេះ " + BX("y=" + nice(tl)) + " ។"])
                if m_ == 0: continue
                if rng.random() < .7:
                    emit("tangent_transcendental", "hard", prob, sol, "y=" + nice(tl),
                         [check(f"subs(diff({s(f)},x),x,{s(x0)})", str(m_), "slope"), check(f"subs({s(f)},x,{s(x0)})+subs(diff({s(f)},x),x,{s(x0)})*(x-({s(x0)}))", s(tl), "tangent")], key=str(("tp", f, t)))

# ---------- I: limits through the derivative ----------
def gen_lim():
    L_ = []
    for k in range(2, 10): L_ += [(exp(k*x), Integer(0)), (log(1 + k*x), Integer(0)), (sin(k*x), Integer(0)), (tan(k*x), Integer(0)), (exp(-k*x), Integer(0)), (sqrt(1 + k*x), Integer(0))]
    for t in (pi/6, pi/4, pi/3, pi/2): L_ += [(sin(x), t), (cos(x), t), (sin(2*x), t/2)]
    L_ += [(tan(x), pi/4), (tan(x), pi/3), (log(x), Integer(1)), (log(x), E), (exp(x), Integer(1)), (exp(x), Integer(2)), (x*log(x), Integer(1)), (x*exp(x), Integer(1)), (log(x), Integer(2)), (log(2*x - 1), Integer(1)), (log(3*x - 2), Integer(1)), (exp(x**2), Integer(1)), (x*sin(x), pi/2)]
    rng.shuffle(L_)
    for f, a in L_[:70]:
        fa = sp.simplify(f.subs(x, a)); d = sp.diff(f, x); v = sp.simplify(d.subs(x, a))
        den = x if a == 0 else x - a; num = f - fa
        expr_t = "\\frac{" + nice(num) + "}{" + nice(den) + "}"
        lm = f"\\lim_{{x\\to {nice(a)}}}{expr_t}"
        prob = pk(f"គណនាលីមីត $${lm}$$ ដោយប្រើនិយមន័យនៃដេរីវេ ។", f"ដោយប្រើដេរីវេ ចូរគណនា ${lm}$ ។", f"តាងអនុគមន៍ $g(x)={nice(f)}$ ។ គណនា $g'\\left({nice(a)}\\right)$ រួចទាញរកលីមីត ${lm}$ ។")
        L, ds = explain(f, "g'(x)")
        sol = "\n".join([q for q in [auto_dom(f)] if q] + [f"តាង $g(x)={nice(f)}$ ។ យើងមាន $g\\left({nice(a)}\\right)={nice(fa)}$ ។", r"តាមនិយមន័យនៃដេរីវេ $g'(a)=\lim_{x\to a}\frac{g(x)-g(a)}{x-a}$ លីមីតដែលត្រូវរកគឺ " + f"$g'\\left({nice(a)}\\right)$ ។"] + L +
                        [f"ជំនួស $x={nice(a)}$ គេបាន $g'\\left({nice(a)}\\right)={nice(v)}$ ។", "ដូចនេះ " + BX(f"{lm}={nice(v)}") + " ។"])
        emit("limit_via_derivative", "medium", prob, sol, nice(v), [check(f"diff({s(f)},x)", s(ds), "derivative"), check(f"limit(({s(num)})/({s(den)}),x,{s(a)})", s(v), "limit")], key=str(("l", f, a)))

# ---------- J: logarithmic differentiation ----------
def gen_logdiff():
    pos = "យើងសិក្សាលើ $D=(0;+\\infty)$ ដែលនៅទីនោះ $y>0$ ។"
    G = [x, 2*x, 3*x, log(x), sin(x), cos(x), 1/x, 2/x, sqrt(x), x + 1]
    for g in G:
        for bs in (x, x + 1, x + 2, x**2 + 1):
            if bs != x and g in (log(x), 1/x, 2/x, sqrt(x)) and rng.random() < .6: continue
            f = bs**g; e = g*log(bs); L, de = explain(e, r"\frac{y'}{y}"); res = simp(f*de)
            prob = pk(f"គណនាដេរីវេនៃអនុគមន៍ $y={nice(f)}$ ចំពោះ $x>0$ ។", f"ដោយធ្វើលោការីតអង្គទាំងពីរ រកដេរីវេ $y'$ នៃ $y={nice(f)}$ ចំពោះ $x>0$ ។")
            sol = "\n".join([pos, f"យកលោការីតនេពែរលើអង្គទាំងពីរ គេបាន $\\ln y={nice(e)}$ ។".replace("លោការីតនេពែរ", "លោការីត"), r"ធ្វើដេរីវេលើអង្គទាំងពីរ ដោយដឹងថា $(\ln y)'=\frac{y'}{y}$ ។"] + L +
                            [f"គុណអង្គទាំងពីរនឹង $y={nice(f)}$ គេបាន៖", f"$$y'={par(f) if False else nice(f)}\\left({nice(de)}\\right)$$", "ដូចនេះ " + BX(f"y'={nice(f)}\\left({nice(de)}\\right)") + " ។"])
            emit("log_differentiation", "hard", prob, sol, f"y'={nice(f)}\\left({nice(de)}\\right)", [check(f"diff({s(f)},x)", s(f*de), "derivative")], key=str(f))
    for _ in range(60):
        a, b = rng.randint(2, 5), rng.randint(2, 4); p, q = rng.sample(range(1, 7), 2); k = ri(-3, 3)
        f = (x + p)**a*(x + q)**b*exp(k*x); e = a*log(x + p) + b*log(x + q) + k*x; de = sp.diff(e, x)
        terms = f"\\frac{{{a}}}{{{nice(x + p)}}}+\\frac{{{b}}}{{{nice(x + q)}}}{sn(k)}"
        prob = f"គេឱ្យ $y={nice(f)}$ ចំពោះ $x>0$ ។ ដោយយកលោការីតអង្គទាំងពីរ គណនា $\\frac{{y'}}{{y}}$ រួចទាញរក $y'$ ។"
        sol = "\n".join(["យើងសិក្សាលើ $D=(0;+\\infty)$ ដែលនៅទីនោះ $y>0$ ។ យកលោការីតអង្គទាំងពីរ ហើយប្រើ $\\ln(AB)=\\ln A+\\ln B$ និង $\\ln A^{n}=n\\ln A$ គេបាន៖", f"$$\\ln y={nice(a*log(x + p))}+{nice(b*log(x + q))}{sg(k, 'x')}$$", "ធ្វើដេរីវេលើអង្គទាំងពីរ៖",
                         f"$$\\frac{{y'}}{{y}}={terms}$$", "ដូចនេះ " + BX(f"y'={nice(f)}\\left({terms}\\right)") + " ។"])
        emit("log_differentiation", "hard", prob, sol, f"y'={nice(f)}\\left({terms}\\right)", [check(f"diff({s(f)},x)/({s(f)})", s(de), "y'/y"), check(f"diff({s(f)},x)", s(f*de), "derivative")], key=str(f))
        if sum(1 for r in rows if r["subtopic"] == "log_differentiation") > 60: break

# ---------- C2: inflection ----------
def gen_infl():
    for p in range(-4, 5):
        for k in (1, -1):
            f = (x - p)*exp(k*x); d2 = sp.factor(sp.diff(f, x, 2)); r = Integer(p) - 2*Q(1, k); v = sp.simplify(f.subs(x, r))
            L1, d1 = explain(f, "f'(x)"); L2, dd = explain(d1, "f''(x)")
            prob = f"គេឱ្យអនុគមន៍ {DEF('f',f)} មានក្រាប $(C)$ ។ គណនា $f''(x)$ រួចបង្ហាញថា $(C)$ មានចំណុចរបត់មួយ ហើយរកកូអរដោនេចំណុចនោះ ។"
            sol = "\n".join(L1 + L2 + [f"ដោយ {M(exp(k*x))} $>0$ ជានិច្ច សញ្ញានៃ $f''(x)$ យកតាមកត្តាដឺក្រេទី១ ។".replace("កត្តាដឺក្រេទី១", "កន្សោម " + M(sp.expand(dd/exp(k*x)))), f"$f''(x)=0$ ពេល $x={nice(r)}$ ហើយ $f''$ ប្តូរសញ្ញានៅត្រង់នោះ ។",
                                       f"ម្យ៉ាងទៀត $f\\left({nice(r)}\\right)={nice(v)}$ ។", "ដូចនេះ " + BX(f"f''(x)={nice(dd)}") + " ហើយ $(C)$ មានចំណុចរបត់ " + BX(f"I\\left({nice(r)};{nice(v)}\\right)") + " ។"])
            emit("inflection", "hard", prob, sol, f"f''(x)={nice(dd)},\\ I\\left({nice(r)};{nice(v)}\\right)",
                 [check(f"diff({s(f)},x,2)", s(dd), "f''"), check(f"subs(diff({s(f)},x,2),x,{r})", "0", "f''=0"), check(f"subs({s(f)},x,{r})", s(v), "ordinate")], key=str(f))
    for a in range(1, 8):
        for c in (1, 2, 3):
            f = c*log(x**2 + a*a); r = Integer(a); v = f.subs(x, r)
            L1, d1 = explain(f, "f'(x)"); L2, dd = explain(d1, "f''(x)")
            prob = f"គេឱ្យអនុគមន៍ {DEF('f',f)} ។ សិក្សាសញ្ញានៃ $f''(x)$ រួចរកចំណុចរបត់នៃក្រាបតាងអនុគមន៍នេះ ។"
            sol = "\n".join(["ដែនកំណត់ $D=IR$ ។"] + L1 + L2 + [f"ដោយភាគបែងវិជ្ជមាន សញ្ញានៃ $f''(x)$ យកតាមសញ្ញានៃ {M(a*a - x**2)} ។", f"កន្សោមនេះស្មើសូន្យពេល $x=\\pm{a}$ ហើយប្តូរសញ្ញានៅត្រង់ចំណុចទាំងពីរនេះ ។",
                                                     f"ដោយ $f$ ជាអនុគមន៍គូ គេបាន $f(-{a})=f({a})={nice(v)}$ ។", "ដូចនេះ " + BX(f"f''(x)={nice(dd)}") + " ហើយក្រាបមានចំណុចរបត់ពីរ " + BX(f"I_{{1}}\\left(-{a};{nice(v)}\\right),\\ I_{{2}}\\left({a};{nice(v)}\\right)") + " ។"])
            emit("inflection", "hard", prob, sol, f"f''(x)={nice(dd)},\\ I_{{1}}\\left(-{a};{nice(v)}\\right),\\ I_{{2}}\\left({a};{nice(v)}\\right)",
                 [check(f"diff({s(f)},x,2)", s(dd), "f''"), check(f"subs(diff({s(f)},x,2),x,{a})", "0", "f''=0"), check(f"subs(diff({s(f)},x,2),x,-{a})", "0", "f''=0"), check(f"subs({s(f)},x,{a})", s(v), "ordinate")], key=str(f))

# ---------- K: hand-written rows ----------
POSD = "ដែនកំណត់ $D=(0;+\\infty)$ ។"
TAND = "អនុគមន៍កំណត់លុះត្រាតែ $\\cos x\\neq0$ គឺ $x\\neq\\frac{\\pi}{2}+k\\pi$ ដែល $k$ ជាចំនួនគត់ ។ ដូចនេះ $D=IR-\\left\\{\\frac{\\pi}{2}+k\\pi\\right\\}$ ។"
HDOM = {r"$y=\sqrt{1+\sin^{2}x}$": "ដោយ $1+\\sin^{2}x>0$ ជានិច្ច នោះ $D=IR$ ។", r"$f(x)=\frac{\ln x}{x}$": POSD,
        r"\ln\left(e^{3}\right)": "ដែនកំណត់ $D=IR$ ។", r"\ln\left(\frac{1-\cos x}{1+\cos x}\right)": "យើងសិក្សាលើ $D=(0;\\pi)$ ។",
        r"$y=\ln\sqrt{\frac{x+1}{x+3}}$": "យើងសិក្សាលើ $D=(-1;+\\infty)$ ។", r"$f(x)=e^{\ln x+2x}$": POSD,
        r"\ln\frac{1+\sin x}{1-\sin x}": "យើងសិក្សាលើ $D=\\left(-\\frac{\\pi}{2};\\frac{\\pi}{2}\\right)$ ។",
        r"$f(x)=\tan x-x$": "យើងសិក្សាលើ $D=\\left[0;\\frac{\\pi}{2}\\right)$ ដែល $\\tan x$ មានន័យ ។", r"ខ្សែកោង $y=\ln x$": POSD,
        r"$f(x)=x\ln x$": POSD, r"$f(x)=ax+b+c\ln x$": POSD, r"$f(x)=\tan x$": TAND, r"$f'(x)=\sqrt{2}e^{x}": "ដែនកំណត់ $D=IR$ ។", r"$y=\ln(\ln x)$": "អនុគមន៍កំណត់លុះត្រាតែ $x>0$ និង $\\ln x>0$ ។ ដូចនេះ $D=(1;+\\infty)$ ។",
        r"$f(x)=\ln(x+1)-\ln x$": POSD, r"$f(x)=\ln\frac{x^{2}}{x^{2}+1}$": POSD, r"$f(x)=\frac{1}{3}\tan^{3}x-\tan x+x$": TAND,
        r"$g(t)=\ln(1+t^{2})$": "ដោយ $1+e^{2x}>0$ ជានិច្ច នោះ $D=IR$ ។", r"$f(x)=\sin(\ln x)+\cos(\ln x)$": POSD}
def H(sub, dif, prob, sol, ans, chk):
    for frag, line in HDOM.items():
        if frag in prob:
            sol = line + "\n" + sol
            break
    emit(sub, dif, prob, sol, ans, [check(a, b, "hand") for a, b in chk], key=prob)
def gen_hand():
    P = "differential_relation"
    H(P, "medium", r"គេឱ្យ $f(x)=e^{x}\cos x$ ។ បង្ហាញថា $f''(x)-2f'(x)+2f(x)=0$ ជានិច្ច ។", "មុននឹងជំនួស យើងរក $f'$ ជាមុនសិន ដោយប្រើដេរីវេនៃផលគុណ៖\n$$f'(x)=e^{x}\\cos x-e^{x}\\sin x=e^{x}(\\cos x-\\sin x)$$\nធ្វើដូចគ្នាម្តងទៀតចំពោះ $f'$ ៖\n$$f''(x)=e^{x}(\\cos x-\\sin x)+e^{x}(-\\sin x-\\cos x)=-2e^{x}\\sin x$$\nឥឡូវបូកបញ្ចូលគ្នា៖\n$$f''-2f'+2f=-2e^{x}\\sin x-2e^{x}\\cos x+2e^{x}\\sin x+2e^{x}\\cos x=0$$\nតួទាំងអស់លុបគ្នាអស់ ។ ដូចនេះ $\\boxed{f''(x)-2f'(x)+2f(x)=0}$ ។", "f''-2f'+2f=0", [("diff(exp(x)*cos(x),x,2)", "-2*exp(x)*sin(x)"), ("diff(exp(x)*cos(x),x,2)-2*diff(exp(x)*cos(x),x)+2*exp(x)*cos(x)", "0")])
    H(P, "medium", r"គេមាន $y=\ln(1+x^{2})$ ។ ស្រាយបញ្ជាក់ថា $(1+x^{2})y'=2x$ ។", "ដោយ $1+x^{2}>0$ ជានិច្ច នោះ $D=IR$ ។\nតាមរូបមន្ត $(\\ln u)'=\\frac{u'}{u}$ គេបាន $y'=\\frac{2x}{1+x^{2}}$ ។\nគុណអង្គទាំងពីរនឹង $1+x^{2}$ យើងទទួលបានទំនាក់ទំនងភ្លាម ។\nដូចនេះ $\\boxed{(1+x^{2})y'=2x}$ ។", "(1+x^{2})y'=2x", [("(1+x**2)*diff(log(1+x**2),x)", "2*x")])
    H(P, "hard", r"ឱ្យ $y=\sqrt{1+\sin^{2}x}$ ។ បង្ហាញថា $yy'=\sin x\cos x$ ។", "ជំនួសឱ្យការធ្វើដេរីវេឫសការេដោយផ្ទាល់ យើងលើកអង្គទាំងពីរជាការេ៖ $y^{2}=1+\\sin^{2}x$ ។\nធ្វើដេរីវេលើអង្គទាំងពីរ គេបាន $2yy'=2\\sin x\\cos x$ ។\nចែកនឹង $2$ ។ ដូចនេះ $\\boxed{yy'=\\sin x\\cos x}$ ។", "yy'=\\sin x\\cos x", [("sqrt(1+sin(x)**2)*diff(sqrt(1+sin(x)**2),x)", "sin(x)*cos(x)")])
    H(P, "hard", r"គេឱ្យ $f(x)=\frac{\ln x}{x}$ ចំពោះ $x>0$ ។ បង្ហាញថា $x^{2}f''(x)+3xf'(x)+f(x)=0$ ។", "សរសេរ $xf(x)=\\ln x$ ។ វិធីនេះជៀសវាងផលចែក ។\nធ្វើដេរីវេមួយដង៖ $f(x)+xf'(x)=\\frac{1}{x}$ ។\nធ្វើដេរីវេម្តងទៀត៖ $2f'(x)+xf''(x)=-\\frac{1}{x^{2}}$ ។\nគុណសមីការចុងក្រោយនឹង $x$ គេបាន $x^{2}f''+2xf'=-\\frac{1}{x}$ ហើយបូកនឹងសមីការមុន៖\n$$x^{2}f''+3xf'+f=-\\frac{1}{x}+\\frac{1}{x}=0$$\nដូចនេះ $\\boxed{x^{2}f''(x)+3xf'(x)+f(x)=0}$ ។", "x^{2}f''+3xf'+f=0", [("x**2*diff(log(x)/x,x,2)+3*x*diff(log(x)/x,x)+log(x)/x", "0")])
    H(P, "medium", r"អនុគមន៍ $y=e^{-x}\sin x$ ។ រកចំនួនថេរ $k$ ដើម្បីឱ្យ $y''+2y'+ky=0$ ។", "គេបាន $y'=e^{-x}(\\cos x-\\sin x)$ ។\nបន្ទាប់មក $y''=e^{-x}(-\\cos x+\\sin x-\\sin x-\\cos x)=-2e^{-x}\\cos x$ ។\nជំនួស៖ $-2e^{-x}\\cos x+2e^{-x}\\cos x-2e^{-x}\\sin x+ke^{-x}\\sin x=(k-2)e^{-x}\\sin x$ ។\nកន្សោមនេះស្មើសូន្យគ្រប់ $x$ លុះត្រាតែ $k-2=0$ ។\nដូចនេះ $\\boxed{k=2}$ ។", "k=2", [("diff(exp(-x)*sin(x),x,2)+2*diff(exp(-x)*sin(x),x)+2*exp(-x)*sin(x)", "0")])
    H(P, "medium", r"បង្ហាញថាអនុគមន៍ $f(x)=\sin^{2}x+\cos^{2}x+\ln\left(e^{3}\right)$ មានដេរីវេស្មើសូន្យ រួចរកតម្លៃថេររបស់វា ។", "ដោយប្រើដេរីវេដោយផ្ទាល់៖\n$$f'(x)=2\\sin x\\cos x-2\\cos x\\sin x=0$$\nដេរីវេស្មើសូន្យលើ $IR$ នាំឱ្យ $f$ ជាអនុគមន៍ថេរ ។ យក $x=0$ គេបាន $f(0)=0+1+3=4$ ។\nដូចនេះ $\\boxed{f'(x)=0}$ និង $\\boxed{f(x)=4}$ ។", "f'(x)=0,\\ f(x)=4", [("diff(sin(x)**2+cos(x)**2,x)", "0"), ("sin(x)**2+cos(x)**2+3", "4")])
    H(P, "hard", r"ឱ្យ $f(x)=\cos^{4}x+\sin^{4}x+2\sin^{2}x\cos^{2}x$ ។ គណនា $f'(x)$ រួចទាញថា $f$ ជាអនុគមន៍ថេរ ។", "កត់សម្គាល់ថា $f(x)=(\\cos^{2}x+\\sin^{2}x)^{2}$ ។ ប៉ុន្តែលំហាត់សុំដេរីវេ ដូច្នេះយើងគណនាផ្ទាល់៖\n$$f'(x)=-4\\cos^{3}x\\sin x+4\\sin^{3}x\\cos x+4\\sin x\\cos^{3}x-4\\sin^{3}x\\cos x$$\nតួទាំងបួនលុបគ្នាជាគូ គេបាន $f'(x)=0$ ។\nដូច្នេះ $f$ ថេរ ហើយ $f(0)=1$ ។\nដូចនេះ $\\boxed{f'(x)=0}$ និង $\\boxed{f(x)=1}$ ។", "f'(x)=0,\\ f(x)=1", [("diff(cos(x)**4+sin(x)**4+2*sin(x)**2*cos(x)**2,x)", "0"), ("cos(x)**4+sin(x)**4+2*sin(x)**2*cos(x)**2", "1")])
    D = "composition_mixed"
    H(D, "medium", r"គណនាដេរីវេនៃ $f(x)=\ln\left(\frac{1-\cos x}{1+\cos x}\right)$ ចំពោះ $0<x<\pi$ ។", "លើចន្លោះនេះ ភាគយក និងភាគបែងវិជ្ជមាន ។ ប្រើលក្ខណៈលោការីតបំបែកមុន៖\n$$f(x)=\\ln(1-\\cos x)-\\ln(1+\\cos x)$$\nបន្ទាប់មកធ្វើដេរីវេម្តងមួយតួ៖\n$$f'(x)=\\frac{\\sin x}{1-\\cos x}+\\frac{\\sin x}{1+\\cos x}=\\frac{2\\sin x}{1-\\cos^{2}x}=\\frac{2}{\\sin x}$$\nដូចនេះ $\\boxed{f'(x)=\\frac{2}{\\sin x}}$ ។", "f'(x)=\\frac{2}{\\sin x}", [("diff(log(1-cos(x))-log(1+cos(x)),x)", "2/sin(x)")])
    H(D, "medium", r"រកដេរីវេនៃ $y=\ln\sqrt{\frac{x+1}{x+3}}$ ចំពោះ $x>-1$ ។", "កុំប្រញាប់ប្រើរូបមន្តបណ្ដាក់ ។ យើងសម្រួលជាមុន៖\n$$y=\\frac{1}{2}\\ln(x+1)-\\frac{1}{2}\\ln(x+3)$$\nដូច្នេះ\n$$y'=\\frac{1}{2}\\left(\\frac{1}{x+1}-\\frac{1}{x+3}\\right)=\\frac{1}{(x+1)(x+3)}$$\nដូចនេះ $\\boxed{y'=\\frac{1}{(x+1)(x+3)}}$ ។", "y'=\\frac{1}{(x+1)(x+3)}", [("diff(log(sqrt((x+1)/(x+3))),x)", "1/((x+1)*(x+3))")])
    H(D, "easy", r"គេឱ្យ $f(x)=e^{\ln x+2x}$ ចំពោះ $x>0$ ។ សរសេរ $f$ ជារាងសាមញ្ញ រួចគណនា $f'(x)$ ។", "ដោយ $e^{\\ln x}=x$ យើងអាចសរសេរ $f(x)=xe^{2x}$ ។\nតាមដេរីវេនៃផលគុណ៖\n$$f'(x)=e^{2x}+2xe^{2x}=(1+2x)e^{2x}$$\nដូចនេះ $\\boxed{f'(x)=(1+2x)e^{2x}}$ ។", "f'(x)=(1+2x)e^{2x}", [("diff(exp(log(x)+2*x),x)", "(1+2*x)*exp(2*x)")])
    H(D, "medium", r"គណនាដេរីវេនៃ $g(x)=\frac{1}{2}\ln\frac{1+\sin x}{1-\sin x}$ ចំពោះ $-\frac{\pi}{2}<x<\frac{\pi}{2}$ ។", "បំបែកលោការីត៖ $g(x)=\\frac{1}{2}\\ln(1+\\sin x)-\\frac{1}{2}\\ln(1-\\sin x)$ ។\nគេបាន\n$$g'(x)=\\frac{1}{2}\\cdot\\frac{\\cos x}{1+\\sin x}+\\frac{1}{2}\\cdot\\frac{\\cos x}{1-\\sin x}=\\frac{\\cos x}{1-\\sin^{2}x}=\\frac{1}{\\cos x}$$\nដូចនេះ $\\boxed{g'(x)=\\frac{1}{\\cos x}}$ ។", "g'(x)=\\frac{1}{\\cos x}", [("diff(log(1+sin(x))/2-log(1-sin(x))/2,x)", "1/cos(x)")])
    H("trig_derivative", "medium", r"បង្ហាញថាដេរីវេនៃ $f(x)=\tan x-x$ ស្មើនឹង $\tan^{2}x$ រួចទាញថា $f$ កើនលើ $\left[0;\frac{\pi}{2}\right)$ ។", "យើងដឹងថា $(\\tan x)'=1+\\tan^{2}x$ ។ ដូច្នេះ\n$$f'(x)=1+\\tan^{2}x-1=\\tan^{2}x$$\nការេមិនអាចអវិជ្ជមានបានទេ ហើយវាស្មើសូន្យតែត្រង់ $x=0$ ។\nដូចនេះ $\\boxed{f'(x)=\\tan^{2}x\\ge0}$ ហើយ $f$ ជាអនុគមន៍កើនលើចន្លោះនេះ ។", "f'(x)=\\tan^{2}x", [("diff(tan(x)-x,x)", "tan(x)**2")])
    H("trig_derivative", "hard", r"ស្រាយបញ្ជាក់ថា $\sin x\le x$ ចំពោះគ្រប់ $x\ge0$ ដោយសិក្សាអនុគមន៍ $f(x)=x-\sin x$ ។", "យើងមាន $f'(x)=1-\\cos x$ ។\nដោយ $\\cos x\\le1$ នោះ $f'(x)\\ge0$ ជានិច្ច ដូច្នេះ $f$ ជាអនុគមន៍កើន ។\nចំពោះ $x\\ge0$ គេបាន $f(x)\\ge f(0)=0$ មានន័យថា $x-\\sin x\\ge0$ ។\nដូចនេះ $\\boxed{\\sin x\\le x}$ ចំពោះគ្រប់ $x\\ge0$ ។", "\\sin x\\le x", [("diff(x-sin(x),x)", "1-cos(x)"), ("subs(x-sin(x),x,0)", "0")])
    H("exp_derivative", "hard", r"ដោយសិក្សាអនុគមន៍ $f(x)=e^{x}-x-1$ បង្ហាញថា $e^{x}\ge x+1$ ចំពោះគ្រប់ $x\in IR$ ។", "ដេរីវេគឺ $f'(x)=e^{x}-1$ ដែលស្មើសូន្យត្រង់ $x=0$ ។\nពេល $x<0$ គេបាន $f'(x)<0$ ហើយពេល $x>0$ គេបាន $f'(x)>0$ ។ ដូច្នេះ $f$ មានអប្បបរមាត្រង់ $x=0$ ។\nតម្លៃអប្បបរមានោះគឺ $f(0)=0$ ដូច្នេះ $f(x)\\ge0$ គ្រប់ $x$ ។\nដូចនេះ $\\boxed{e^{x}\\ge x+1}$ ។", "e^{x}\\ge x+1", [("diff(exp(x)-x-1,x)", "exp(x)-1"), ("subs(exp(x)-x-1,x,0)", "0")])
    H("log_derivative", "hard", r"ដោយសិក្សាអនុគមន៍ $g(x)=x-1-\ln x$ លើ $(0;+\infty)$ បង្ហាញថា $\ln x\le x-1$ ។", "គេបាន $g'(x)=1-\\frac{1}{x}=\\frac{x-1}{x}$ ។\nលើដែនកំណត់ $x>0$ ដូច្នេះសញ្ញាយកតាម $x-1$ ៖ អនុគមន៍ចុះលើ $(0;1)$ ហើយកើនលើ $(1;+\\infty)$ ។\nអប្បបរមាគឺ $g(1)=0$ ដូច្នេះ $g(x)\\ge0$ ។\nដូចនេះ $\\boxed{\\ln x\\le x-1}$ ។", "\\ln x\\le x-1", [("diff(x-1-log(x),x)", "(x-1)/x"), ("subs(x-1-log(x),x,1)", "0")])
    T_ = "tangent_transcendental"
    H(T_, "hard", r"រកសមីការបន្ទាត់ប៉ះនឹងខ្សែកោង $y=\ln x$ ដែលកាត់តាមគល់អ័ក្ស ។", "តាង $x_{0}>0$ ជាអាប់ស៊ីសនៃចំណុចប៉ះ ។ បន្ទាត់ប៉ះមានសមីការ\n$$y-\\ln x_{0}=\\frac{1}{x_{0}}(x-x_{0})$$\nវាកាត់តាមគល់អ័ក្ស លុះត្រាតែ $(0;0)$ ផ្ទៀងផ្ទាត់សមីការ៖ $-\\ln x_{0}=-1$ នោះ $x_{0}=e$ ។\nមេគុណប្រាប់ទិសគឺ $\\frac{1}{e}$ ។\nដូចនេះ $\\boxed{y=\\frac{x}{e}}$ ។", "y=\\frac{x}{e}", [("subs(log(x),x,E)+subs(diff(log(x),x),x,E)*(x-E)", "x/E")])
    H(T_, "hard", r"រកសមីការបន្ទាត់ប៉ះនឹងខ្សែកោង $y=e^{x}$ ដែលកាត់តាមគល់អ័ក្ស ។", "បើចំណុចប៉ះមានអាប់ស៊ីស $a$ នោះបន្ទាត់ប៉ះគឺ $y-e^{a}=e^{a}(x-a)$ ។\nជំនួស $x=0$ , $y=0$ គេបាន $-e^{a}=-ae^{a}$ ។ ដោយ $e^{a}\\neq0$ យើងបាន $a=1$ ។\nដូច្នេះមេគុណប្រាប់ទិសស្មើនឹង $e$ ។\nដូចនេះ $\\boxed{y=ex}$ ។", "y=ex", [("subs(exp(x),x,1)+subs(diff(exp(x),x),x,1)*(x-1)", "E*x")])
    H(T_, "medium", r"បង្ហាញថាខ្សែកោង $y=e^{x}$ និង $y=1+\sin x$ មានបន្ទាត់ប៉ះរួមគ្នាត្រង់ចំណុច $A(0;1)$ ។", "ខ្សែកោងទាំងពីរកាត់តាម $A$ ព្រោះ $e^{0}=1$ និង $1+\\sin0=1$ ។\nមេគុណប្រាប់ទិសត្រង់ $x=0$ ៖ $(e^{x})'=e^{x}$ ឱ្យ $1$ ហើយ $(1+\\sin x)'=\\cos x$ ក៏ឱ្យ $1$ ដែរ ។\nខ្សែកោងទាំងពីរមានចំណុចរួម និងមេគុណប្រាប់ទិសដូចគ្នា ។\nដូចនេះ បន្ទាត់ប៉ះរួមគឺ $\\boxed{y=x+1}$ ។", "y=x+1", [("subs(diff(exp(x),x),x,0)", "1"), ("subs(diff(1+sin(x),x),x,0)", "1")])
    N = "nth_derivative"
    H(N, "hard", r"គេឱ្យ $f(x)=\frac{1}{x(x+1)}$ ចំពោះ $x>0$ ។ សរសេរ $f$ ជាផលដកប្រភាគពីរ រួចរក $f^{(n)}(x)$ ។", "យើងមាន $f(x)=\\frac{1}{x}-\\frac{1}{x+1}$ ។\nពីដេរីវេ $\\left(\\frac{1}{x+a}\\right)'=-\\frac{1}{(x+a)^{2}}$ ហើយធ្វើបន្តបន្ទាប់ គេទទួលបាន $\\left(\\frac{1}{x+a}\\right)^{(n)}=\\frac{(-1)^{n}n!}{(x+a)^{n+1}}$ ។\nរូបមន្តនេះពិតពេល $n=1$ ហើយបើវាពិតចំពោះ $n=k$ ការធ្វើដេរីវេមួយដងគុណនឹង $-(k+1)$ ហើយបង្កើនស្វ័យគុណមួយ ដូច្នេះវាពិតចំពោះ $n=k+1$ ។\nអនុវត្តលើតួទាំងពីរ៖\nដូចនេះ $\\boxed{f^{(n)}(x)=(-1)^{n}n!\\left[\\frac{1}{x^{n+1}}-\\frac{1}{(x+1)^{n+1}}\\right]}$ ។", "f^{(n)}(x)=(-1)^{n}n!\\left[\\frac{1}{x^{n+1}}-\\frac{1}{(x+1)^{n+1}}\\right]", [("diff(1/(x*(x+1)),x,3)", "-6*(1/x**4-1/(x+1)**4)"), ("diff(1/(x*(x+1)),x,4)", "24*(1/x**5-1/(x+1)**5)")])
    H(N, "bacii", r"គេឱ្យ $f(x)=x^{2}e^{x}$ ។ ស្រាយបញ្ជាក់ថា $f^{(n)}(x)=\left(x^{2}+2nx+n(n-1)\right)e^{x}$ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ។", "ពេល $n=1$ ៖ $f'(x)=(x^{2}+2x)e^{x}$ ត្រូវនឹងរូបមន្ត ។\nឧបមាថារូបមន្តពិតចំពោះ $n=k$ ។ ធ្វើដេរីវេ៖\n$$f^{(k+1)}(x)=\\left(2x+2k\\right)e^{x}+\\left(x^{2}+2kx+k(k-1)\\right)e^{x}$$\n$$=\\left(x^{2}+2(k+1)x+k(k+1)\\right)e^{x}$$\nនេះជារូបមន្តពេល $n=k+1$ ព្រោះ $(k+1)k=k(k+1)$ ។\nដូចនេះ $\\boxed{f^{(n)}(x)=\\left(x^{2}+2nx+n(n-1)\\right)e^{x}}$ ។", "f^{(n)}(x)=\\left(x^{2}+2nx+n(n-1)\\right)e^{x}", [("diff(x**2*exp(x),x,%d)" % n, "(x**2+%d*x+%d)*exp(x)" % (2*n, n*(n-1))) for n in (1, 2, 3, 4)])
    H(N, "bacii", r"គេឱ្យ $f(x)=x\ln x$ ចំពោះ $x>0$ ។ ស្រាយបញ្ជាក់ថាចំពោះ $n\ge2$ គេមាន $f^{(n)}(x)=\frac{(-1)^{n}(n-2)!}{x^{n-1}}$ ។", "ដេរីវេដំបូងគឺ $f'(x)=\\ln x+1$ ហើយ $f''(x)=\\frac{1}{x}$ ។ រូបមន្តឱ្យ $\\frac{(-1)^{2}0!}{x}=\\frac{1}{x}$ ដូច្នេះវាពិតពេល $n=2$ ។\nឧបមាថាវាពិតចំពោះ $n=k\\ge2$ ។ គេបាន\n$$f^{(k+1)}(x)=(-1)^{k}(k-2)!\\cdot\\frac{-(k-1)}{x^{k}}=\\frac{(-1)^{k+1}(k-1)!}{x^{k}}$$\nនេះគឺរូបមន្តពេល $n=k+1$ ។\nដូចនេះ $\\boxed{f^{(n)}(x)=\\frac{(-1)^{n}(n-2)!}{x^{n-1}}}$ ។", "f^{(n)}(x)=\\frac{(-1)^{n}(n-2)!}{x^{n-1}}", [("diff(x*log(x),x,2)", "1/x"), ("diff(x*log(x),x,3)", "-1/x**2"), ("diff(x*log(x),x,4)", "2/x**3"), ("diff(x*log(x),x,5)", "-6/x**4")])
    H(N, "hard", r"គេឱ្យ $f(x)=e^{x}\sin x$ ។ បង្ហាញថា $f'(x)=\sqrt{2}e^{x}\sin\left(x+\frac{\pi}{4}\right)$ រួចទាញរក $f^{(n)}(x)$ ។", "គេបាន $f'(x)=e^{x}(\\sin x+\\cos x)$ ។ ដោយ $\\sin x+\\cos x=\\sqrt{2}\\sin\\left(x+\\frac{\\pi}{4}\\right)$ យើងបានទម្រង់ដែលសុំ ។\nមានន័យថា ការធ្វើដេរីវេម្តង គុណនឹង $\\sqrt{2}$ ហើយបន្ថែម $\\frac{\\pi}{4}$ ទៅក្នុងមុំ ។\nពេល $n=1$ ពិត ។ បើ $f^{(k)}(x)=(\\sqrt{2})^{k}e^{x}\\sin\\left(x+\\frac{k\\pi}{4}\\right)$ ពិត ការគណនាដូចខាងលើឱ្យ $f^{(k+1)}(x)=(\\sqrt{2})^{k+1}e^{x}\\sin\\left(x+\\frac{(k+1)\\pi}{4}\\right)$ ។\nដូចនេះ $\\boxed{f^{(n)}(x)=(\\sqrt{2})^{n}e^{x}\\sin\\left(x+\\frac{n\\pi}{4}\\right)}$ ។", "f^{(n)}(x)=(\\sqrt{2})^{n}e^{x}\\sin\\left(x+\\frac{n\\pi}{4}\\right)", [("diff(exp(x)*sin(x),x,%d)" % n, "sqrt(2)**%d*exp(x)*sin(x+%d*pi/4)" % (n, n)) for n in (1, 2, 3, 4)])
    C = "find_constants"
    H(C, "medium", r"គេឱ្យ $f(x)=ae^{2x}+be^{x}$ ។ កំណត់ $a$ និង $b$ ដោយដឹងថា $f(0)=1$ និង $f'(0)=4$ ។", "ដេរីវេគឺ $f'(x)=2ae^{2x}+be^{x}$ ។\nលក្ខខណ្ឌទាំងពីរឱ្យ $a+b=1$ និង $2a+b=4$ ។\nដកសមីការទី១ពីទី២ គេបាន $a=3$ ហើយ $b=-2$ ។\nដូចនេះ $\\boxed{a=3,\\ b=-2}$ ។", "a=3,\\ b=-2", [("subs(3*exp(2*x)-2*exp(x),x,0)", "1"), ("subs(diff(3*exp(2*x)-2*exp(x),x),x,0)", "4")])
    H(C, "medium", r"អនុគមន៍ $f(x)=ax+b+c\ln x$ ចំពោះ $x>0$ ។ រក $a,b,c$ ដោយដឹងថា $f(1)=3$ , $f'(1)=0$ និង $f'(2)=1$ ។", "យើងមាន $f'(x)=a+\\frac{c}{x}$ ។\nពី $f'(1)=0$ គេបាន $a+c=0$ ។ ពី $f'(2)=1$ គេបាន $a+\\frac{c}{2}=1$ ។\nដកគ្នា៖ $\\frac{c}{2}=-1$ នោះ $c=-2$ និង $a=2$ ។\nចុងក្រោយ $f(1)=a+b=3$ ឱ្យ $b=1$ ។\nដូចនេះ $\\boxed{a=2,\\ b=1,\\ c=-2}$ ។", "a=2,\\ b=1,\\ c=-2", [("subs(2*x+1-2*log(x),x,1)", "3"), ("subs(diff(2*x+1-2*log(x),x),x,1)", "0"), ("subs(diff(2*x+1-2*log(x),x),x,2)", "1")])
    H(C, "hard", r"គេឱ្យ $f(x)=e^{x}(a\cos x+b\sin x)$ ។ រក $a$ និង $b$ ដើម្បីឱ្យ $f'(x)=e^{x}\cos x$ ។", "តាមដេរីវេនៃផលគុណ៖\n$$f'(x)=e^{x}\\left[(a+b)\\cos x+(b-a)\\sin x\\right]$$\nផ្ទឹមមេគុណនៃ $\\cos x$ និង $\\sin x$ គេបាន $a+b=1$ និង $b-a=0$ ។\nដូច្នេះ $a=b=\\frac{1}{2}$ ។\nដូចនេះ $\\boxed{a=\\frac{1}{2},\\ b=\\frac{1}{2}}$ ។", "a=b=\\frac{1}{2}", [("diff(exp(x)*(cos(x)+sin(x))/2,x)", "exp(x)*cos(x)")])
    V = "derivative_at_point"
    H(V, "easy", r"គេឱ្យ $f(x)=\sin^{2}x$ ។ រកតម្លៃ $x\in[0;\pi]$ ដែលធ្វើឱ្យ $f'(x)=0$ ។", "គេបាន $f'(x)=2\\sin x\\cos x=\\sin2x$ ។\nសមីការ $\\sin2x=0$ ឱ្យ $2x=k\\pi$ ។ ក្នុងចន្លោះដែលឱ្យ មាន $x=0$ , $x=\\frac{\\pi}{2}$ និង $x=\\pi$ ។\nដូចនេះ $\\boxed{x\\in\\left\\{0;\\frac{\\pi}{2};\\pi\\right\\}}$ ។", "x\\in\\left\\{0;\\frac{\\pi}{2};\\pi\\right\\}", [("diff(sin(x)**2,x)", "sin(2*x)"), ("subs(diff(sin(x)**2,x),x,pi/2)", "0")])
    H(V, "medium", r"ដោះស្រាយសមីការ $f'(x)=0$ ចំពោះ $f(x)=\ln^{2}x-2\ln x$ ។", "ដែនកំណត់ $D=(0;+\\infty)$ ។\nដេរីវេគឺ $f'(x)=\\frac{2\\ln x}{x}-\\frac{2}{x}=\\frac{2(\\ln x-1)}{x}$ ។\nដោយ $x>0$ សមីការក្លាយជា $\\ln x=1$ ។\nដូចនេះ $\\boxed{x=e}$ ។", "x=e", [("diff(log(x)**2-2*log(x),x)", "2*(log(x)-1)/x"), ("subs(diff(log(x)**2-2*log(x),x),x,E)", "0")])
    H(V, "medium", r"ដោះស្រាយសមីការ $f'(x)=0$ ចំពោះ $f(x)=e^{2x}-4e^{x}+2x$ ។", "ធ្វើដេរីវេ៖ $f'(x)=2e^{2x}-4e^{x}+2=2(e^{x}-1)^{2}$ ។\nការេស្មើសូន្យតែពេល $e^{x}=1$ ។\nដូចនេះ $\\boxed{x=0}$ ហើយ $f'(x)\\ge0$ គ្រប់ $x$ ។", "x=0", [("diff(exp(2*x)-4*exp(x)+2*x,x)", "2*(exp(x)-1)**2")])
    Hh = "higher_order"
    H(Hh, "medium", r"គេឱ្យ $f(x)=e^{-x}\cos x$ ។ គណនា $f''(0)$ ដោយមិនចាំបាច់សម្រួលច្រើន ។", "ដេរីវេទី១៖ $f'(x)=-e^{-x}(\\cos x+\\sin x)$ ។\nដេរីវេទី២៖ $f''(x)=e^{-x}(\\cos x+\\sin x)-e^{-x}(\\cos x-\\sin x)=2e^{-x}\\sin x$ ។\nយក $x=0$ ។\nដូចនេះ $\\boxed{f''(0)=0}$ ។", "f''(0)=0", [("diff(exp(-x)*cos(x),x,2)", "2*exp(-x)*sin(x)"), ("subs(diff(exp(-x)*cos(x),x,2),x,0)", "0")])
    H(Hh, "hard", r"គេឱ្យ $f(x)=\tan x$ ។ សរសេរ $f'$ , $f''$ និង $f'''$ ជាអនុគមន៍នៃ $t=\tan x$ ។", "ចំណុចសំខាន់គឺ $t'=1+t^{2}$ ។\nដូច្នេះ $f'=1+t^{2}$ ។\nបន្ទាប់មក $f''=2tt'=2t+2t^{3}$ ។\nហើយ $f'''=(2+6t^{2})t'=(2+6t^{2})(1+t^{2})$ ។\nដូចនេះ $\\boxed{f'=1+t^{2}}$ , $\\boxed{f''=2t+2t^{3}}$ និង $\\boxed{f'''=2+8t^{2}+6t^{4}}$ ។", "f'=1+t^{2},\\ f''=2t+2t^{3},\\ f'''=2+8t^{2}+6t^{4}", [("diff(tan(x),x,2)", "2*tan(x)+2*tan(x)**3"), ("diff(tan(x),x,3)", "2+8*tan(x)**2+6*tan(x)**4")])
    H(Hh, "medium", r"គណនាដេរីវេទី២ នៃ $y=\ln(\ln x)$ ចំពោះ $x>1$ ។", "ដេរីវេទី១ តាមរូបមន្តបណ្ដាក់គឺ $y'=\\frac{1}{x\\ln x}$ ។\nដោយ $(x\\ln x)'=\\ln x+1$ យើងបាន\n$$y''=-\\frac{\\ln x+1}{x^{2}\\ln^{2}x}$$\nដូចនេះ $\\boxed{y''=-\\frac{\\ln x+1}{x^{2}\\ln^{2}x}}$ ។", "y''=-\\frac{\\ln x+1}{x^{2}\\ln^{2}x}", [("diff(log(log(x)),x,2)", "-(log(x)+1)/(x**2*log(x)**2)")])
    Vt = "variation_log"
    tb = variation_table([r"0", "1", r"+\infty"], ["", "-", r"\|", "-", ""], [r"0", r"\searrow", r"-\infty\ \|\ +\infty", r"\searrow", r"+\infty"]) if False else None
    H("exp_derivative", "easy", r"តើអនុគមន៍ $f(x)=e^{x}+e^{-x}$ ជាអនុគមន៍គូឬទេ? គណនា $f'(x)$ ហើយពិនិត្យថាវាជាអនុគមន៍សេស ។", "យើងឃើញ $f(-x)=e^{-x}+e^{x}=f(x)$ ដូច្នេះ $f$ ជាអនុគមន៍គូ ។\nដេរីវេគឺ $f'(x)=e^{x}-e^{-x}$ ។\nពិនិត្យ៖ $f'(-x)=e^{-x}-e^{x}=-f'(x)$ ។\nដូចនេះ $\\boxed{f'(x)=e^{x}-e^{-x}}$ ហើយវាប្តូរសញ្ញាពេលប្តូរ $x$ ទៅ $-x$ ។", "f'(x)=e^{x}-e^{-x}", [("diff(exp(x)+exp(-x),x)", "exp(x)-exp(-x)")])
    H("exp_derivative", "medium", r"គេឱ្យ $c(x)=\frac{e^{x}+e^{-x}}{2}$ និង $s(x)=\frac{e^{x}-e^{-x}}{2}$ ។ បង្ហាញថា $c'=s$ , $s'=c$ និង $c^{2}-s^{2}=1$ ។", "ធ្វើដេរីវេផ្ទាល់ គេបាន $c'(x)=\\frac{e^{x}-e^{-x}}{2}=s(x)$ និង $s'(x)=\\frac{e^{x}+e^{-x}}{2}=c(x)$ ។\nតាង $w=c^{2}-s^{2}$ ។ គេបាន $w'=2cc'-2ss'=2cs-2sc=0$ ដូច្នេះ $w$ ថេរ ។\nយក $x=0$ ៖ $c(0)=1$ , $s(0)=0$ នោះ $w=1$ ។\nដូចនេះ $\\boxed{c'=s}$ , $\\boxed{s'=c}$ និង $\\boxed{c^{2}-s^{2}=1}$ ។", "c'=s,\\ s'=c,\\ c^{2}-s^{2}=1", [("diff((exp(x)+exp(-x))/2,x)", "(exp(x)-exp(-x))/2"), ("((exp(x)+exp(-x))/2)**2-((exp(x)-exp(-x))/2)**2", "1")])
    H("log_derivative", "medium", r"គេឱ្យ $f(x)=\ln(x+1)-\ln x$ ចំពោះ $x>0$ ។ បង្ហាញថា $f$ ជាអនុគមន៍ចុះ ។", "ដេរីវេគឺ\n$$f'(x)=\\frac{1}{x+1}-\\frac{1}{x}=-\\frac{1}{x(x+1)}$$\nលើ $x>0$ ភាគបែងវិជ្ជមាន ដូច្នេះ $f'(x)<0$ ជានិច្ច ។\nដូចនេះ $\\boxed{f'(x)=-\\frac{1}{x(x+1)}<0}$ ហើយ $f$ ជាអនុគមន៍ចុះ ។", "f'(x)=-\\frac{1}{x(x+1)}", [("diff(log(x+1)-log(x),x)", "-1/(x*(x+1))")])
    H("log_derivative", "medium", r"រកដេរីវេនៃ $f(x)=\ln\frac{x^{2}}{x^{2}+1}$ ចំពោះ $x>0$ រួចសម្រួលជាប្រភាគតែមួយ ។", "ប្រើលក្ខណៈលោការីត៖ $f(x)=2\\ln x-\\ln(x^{2}+1)$ ។\nគេបាន\n$$f'(x)=\\frac{2}{x}-\\frac{2x}{x^{2}+1}=\\frac{2x^{2}+2-2x^{2}}{x(x^{2}+1)}$$\nភាគយកនៅសល់តែ $2$ ។\nដូចនេះ $\\boxed{f'(x)=\\frac{2}{x(x^{2}+1)}}$ ។", "f'(x)=\\frac{2}{x(x^{2}+1)}", [("diff(2*log(x)-log(x**2+1),x)", "2/(x*(x**2+1))")])
    H("trig_derivative", "medium", r"គណនាដេរីវេនៃ $f(x)=\frac{\sin x-\cos x}{\sin x+\cos x}$ រួចសរសេរលទ្ធផលឱ្យខ្លី ។", "យក $u=\\sin x-\\cos x$ និង $v=\\sin x+\\cos x$ ។ យើងឃើញថា $u'=v$ និង $v'=-u$ ។\nដូច្នេះរូបមន្តផលចែកឱ្យ\n$$f'(x)=\\frac{v\\cdot v+u\\cdot u}{v^{2}}=\\frac{u^{2}+v^{2}}{v^{2}}$$\nដោយ $u^{2}+v^{2}=2$ ។\nដូចនេះ $\\boxed{f'(x)=\\frac{2}{(\\sin x+\\cos x)^{2}}}$ ។", "f'(x)=\\frac{2}{(\\sin x+\\cos x)^{2}}", [("diff((sin(x)-cos(x))/(sin(x)+cos(x)),x)", "2/(sin(x)+cos(x))**2")])
    H("trig_derivative", "easy", r"ដោយប្រើដេរីវេនៃផលគុណ ចូរបង្ហាញថា $(\sin x\cos x)'=\cos2x$ ។", "តាមដេរីវេនៃផលគុណ គេបាន $(\\sin x\\cos x)'=\\cos x\\cos x-\\sin x\\sin x$ ។\nនេះជារូបមន្តមុំទ្វេ $\\cos^{2}x-\\sin^{2}x=\\cos2x$ ។\nដូចនេះ $\\boxed{(\\sin x\\cos x)'=\\cos2x}$ ។", "(\\sin x\\cos x)'=\\cos2x", [("diff(sin(x)*cos(x),x)", "cos(2*x)")])
    H("trig_derivative", "medium", r"គណនាដេរីវេនៃ $f(x)=\frac{1}{3}\tan^{3}x-\tan x+x$ រួចបង្ហាញថា $f'(x)=\tan^{4}x$ ។", "តាង $t=\\tan x$ ដែល $t'=1+t^{2}$ ។\n$$f'(x)=t^{2}(1+t^{2})-(1+t^{2})+1=t^{2}+t^{4}-t^{2}=t^{4}$$\nដូចនេះ $\\boxed{f'(x)=\\tan^{4}x}$ ។", "f'(x)=\\tan^{4}x", [("diff(tan(x)**3/3-tan(x)+x,x)", "tan(x)**4")])
    H("composition_mixed", "hard", r"គេឱ្យ $u(x)=e^{x}$ និង $g(t)=\ln(1+t^{2})$ ។ គណនាដេរីវេនៃអនុគមន៍បណ្ដាក់ $h(x)=g(u(x))$ ។", "តាមរូបមន្ត $h'(x)=g'(u(x))\\cdot u'(x)$ ។\nយើងមាន $g'(t)=\\frac{2t}{1+t^{2}}$ និង $u'(x)=e^{x}$ ។\nជំនួស $t=e^{x}$ ៖\n$$h'(x)=\\frac{2e^{x}}{1+e^{2x}}\\cdot e^{x}=\\frac{2e^{2x}}{1+e^{2x}}$$\nដូចនេះ $\\boxed{h'(x)=\\frac{2e^{2x}}{1+e^{2x}}}$ ។", "h'(x)=\\frac{2e^{2x}}{1+e^{2x}}", [("diff(log(1+exp(2*x)),x)", "2*exp(2*x)/(1+exp(2*x))")])
    H("composition_mixed", "hard", r"គេឱ្យ $f$ មានដេរីវេលើ $IR$ ហើយ $f(0)=2$ , $f'(0)=3$ ។ គណនាដេរីវេនៃ $g(x)=e^{f(x)}$ ត្រង់ $x=0$ ជាអនុគមន៍នៃ $e$ ។", "តាមរូបមន្ត $(e^{u})'=u'e^{u}$ គេបាន $g'(x)=f'(x)e^{f(x)}$ ។\nយក $x=0$ ៖ $g'(0)=3e^{2}$ ។\nដូចនេះ $\\boxed{g'(0)=3e^{2}}$ ។", "g'(0)=3e^{2}", [("subs(diff(exp(2+3*x),x),x,0)", "3*exp(2)")])
    H("composition_mixed", "medium", r"គណនាដេរីវេនៃ $f(x)=\sin(\ln x)+\cos(\ln x)$ ចំពោះ $x>0$ រួចបង្ហាញថា $xf'(x)=\cos(\ln x)-\sin(\ln x)$ ។", "តាង $t=\\ln x$ នោះ $t'=\\frac{1}{x}$ ។\nគេបាន $f'(x)=\\frac{\\cos t}{x}-\\frac{\\sin t}{x}$ ។\nគុណនឹង $x$ ។\nដូចនេះ $\\boxed{f'(x)=\\frac{\\cos(\\ln x)-\\sin(\\ln x)}{x}}$ និង $\\boxed{xf'(x)=\\cos(\\ln x)-\\sin(\\ln x)}$ ។", "f'(x)=\\frac{\\cos(\\ln x)-\\sin(\\ln x)}{x},\\ xf'(x)=\\cos(\\ln x)-\\sin(\\ln x)", [("x*diff(sin(log(x))+cos(log(x)),x)", "cos(log(x))-sin(log(x))")])

if __name__ == "__main__":
    gen_hand(); print("hand", len(rows))
    gen_rel(16); print("rel", len(rows), round(time.time() - _t0))
    gen_nth(14); print("nth", len(rows))
    gen_var(); print("var", len(rows), round(time.time() - _t0))
    gen_tan(7); gen_lim(); gen_logdiff(); gen_infl(); gen_const(32); print("misc", len(rows), round(time.time() - _t0))
    gen_high(14); gen_point(8); print("hp", len(rows), round(time.time() - _t0))
    gen_direct(12); print("direct", len(rows), round(time.time() - _t0))
    keep = {d["image"] for r in rows for d in r["diagrams"] if d.get("image")}
    for fn in os.listdir(os.path.join(ROOT, "diagrams")):      # this generator's PNGs from earlier runs that no row refers to any more
        if fn.startswith("transcendental-") and fn.endswith(".png") and "diagrams/" + fn not in keep:
            os.remove(os.path.join(ROOT, "diagrams", fn))
    write_jsonl(rows, "transcendental.jsonl")
    print("png", PNG[0])
