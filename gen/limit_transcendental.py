"""Generator for chapter `limit`, topic `limit_transcendental`: trigonometric, exponential and logarithmic
limits, the number e, comparison and squeeze arguments, changes of variable. All rows are original.
Every value is exact arithmetic in the family that builds it; lib/verify.py recomputes each with SymPy.
Run: python3 gen/limit_transcendental.py"""
import sys, os, re, glob, hashlib, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from limit_tex import clean_tex, finish_rows, tikz_poles, tikz_squeeze
from sympy import Rational as Q, sqrt as SQ, pi as PI, E as EE, oo, exp as EXP, log as LOG

TOPIC = "limit_transcendental"
GEN = "limit_transcendental"
FR00 = r"\frac{0}{0}"
SINF = r"\lim_{u\to 0}\frac{\sin u}{u}=1"
TANF = r"\lim_{u\to 0}\frac{\tan u}{u}=1"
COSF = r"\lim_{u\to 0}\frac{1-\cos u}{u^{2}}=\frac{1}{2}"
EXPF = r"\lim_{u\to 0}\frac{e^{u}-1}{u}=1"
LNF = r"\lim_{u\to 0}\frac{\ln(1+u)}{u}=1"
EF = r"\lim_{u\to 0}(1+u)^{\frac{1}{u}}=e"
EF2 = r"\lim_{x\to+\infty}\left(1+\frac{1}{x}\right)^{x}=e"
GROW = r"\lim_{x\to+\infty}\frac{e^{x}}{x}=+\infty"
LNX = r"\lim_{x\to+\infty}\frac{\ln x}{x}=0"
XLN = r"\lim_{x\to 0^{+}}x\ln x=0"
XEX = r"\lim_{x\to-\infty}xe^{x}=0"

def T(_tpl, **k):
    return re.sub(r"<(\w+)>", lambda m: str(k[m.group(1)]) if m.group(1) in k else m.group(0), _tpl)
def D(s): return "$$" + s + "$$"
def I(s): return "$" + s + "$"
def L(v):
    """LaTeX of an exact value."""
    if v is oo: return r"+\infty"
    if v is -oo: return r"-\infty"
    t = sp.latex(sp.sympify(v), ln_notation=True).replace("- ", "-").replace(" + ", "+")
    t = re.sub(r"\\ln\{\\left\((\d+) \\right\)\}", r"\\ln \1", t)
    t = re.sub(r"\\ln\{\\left\(\\frac\{(\d+)\}\{(\d+)\} \\right\)\}", r"\\ln\\frac{\1}{\2}", t)
    return t
def c(a):
    """coefficient before a letter: 1 -> '', -1 -> '-'."""
    if a == 1: return ""
    if a == -1: return "-"
    return L(a)
def sg(a):
    """signed number for a sum: +3, -3."""
    t = L(a)
    return t if t.startswith("-") else "+" + t
def hf(a):
    """LaTeX of ax/2."""
    return c(Q(a, 2)) + "x" if a % 2 == 0 else (r"\frac{x}{2}" if a == 1 else r"\frac{" + str(a) + r"x}{2}")
def lin(terms):
    """sum of (coef, latex) terms."""
    out = ""
    for co, t in terms:
        if co == 0: continue
        if t == "":
            s = L(co)
        elif co == 1: s = t
        elif co == -1: s = "-" + t
        else: s = L(co) + (t if not t.startswith("\\") else t)
        if out and not s.startswith("-"): out += "+"
        out += s
    return out or "0"
def px(n):  # x^n in LaTeX
    return "x" if n == 1 else f"x^{{{n}}}"

def ptl(p):
    if str(p) == "oo": return r"+\infty"
    if str(p) == "-oo": return r"-\infty"
    return L(sp.sympify(p))

def wrap(fx):
    """Bracket a sum or difference that follows a limit sign."""
    t = fx.replace(r"\left(", "(").replace(r"\right)", ")"); d = 0
    for i, ch in enumerate(t):
        d += ch in "({[" ; d -= ch in ")}]"
        if ch in "+-" and d == 0 and i > 0:
            return r"\left(" + fx + r"\right)"
    return fx

class P:
    """One limit: the function, the point, the exact value and the worked steps."""
    def __init__(s, fx, p, v, body, sub, diff, e, side="", hint=None, extra=(), grade=12, alt=None,
                 nolim=False, ans=None, conc=None, setup=None, tex=None):
        s.fx, s.p, s.v, s.body, s.sub, s.diff, s.e, s.side = fx, p, v, [b for b in body if b], sub, diff, e, side
        s.hint, s.extra, s.grade, s.alt, s.nolim, s.conc, s.setup = hint, list(extra), grade, alt, nolim, conc, setup
        pt = ptl(p)
        if side:
            pt = (pt if re.fullmatch(r"-?\d+", pt) else r"\left(" + pt + r"\right)") + "^{" + side + "}"
        s.pt = pt
        s.tex = tex or r"\lim_{x\to " + pt + "}" + wrap(fx)
        s.ans = ans if ans is not None else L(v)
    def checks(s):
        out = []
        if not s.nolim:
            sd = f",'{s.side}'" if s.side else ""
            out.append(check(f"limit({s.e},x,{s.p}{sd})", str(s.v), "final limit"))
        out += [check(*t) for t in s.extra]
        return out
    def key(s):
        return re.sub(r"\s", "", s.tex)

def opener(r, pt):
    return r.choice([
        f"កាលណា $x\\to {pt}$ លីមីតនេះមានរាងមិនកំណត់ ${FR00}$ ។",
        f"ជំនួស $x={pt}$ ដោយផ្ទាល់ គេបានរាងមិនកំណត់ ${FR00}$ ដូច្នេះត្រូវបំប្លែងកន្សោមសិន ។",
        f"ភាគយក និងភាគបែងខិតជិត $0$ ទាំងពីរ (រាងមិនកំណត់ ${FR00}$) ។",
        f"យើងមានរាងមិនកំណត់ ${FR00}$ ។",
        "", "",
    ])
def cite(r, f):
    return r.choice([f"(រូបមន្ត ${f}$)", f"ដោយ ${f}$", f"យើងដឹងថា ${f}$", f"តាមរូបមន្ត ${f}$"])
def got(r):
    return r.choice(["គេបាន ៖", "យើងបាន ៖", "នាំឱ្យ ៖", "ដូច្នេះ ៖", "គេបាន"])

# ---------------- trigonometric: sin u / u -----------------
def f_ratio(r):
    a, b = r.sample([1, 2, 3, 4, 5, 6, 7, 8, 9], 2)
    nt = r.choice(["sin", "sin", "tan"]); dt = r.choice(["lin", "lin", "sin", "tan"])
    if dt == "lin":
        fx = T(r"\frac{\<n> <a>x}{<b>x}", n=nt, a=c(a), b=c(b)); e = f"{nt}({a}*x)/({b}*x)"
    else:
        fx = T(r"\frac{\<n> <a>x}{\<d> <b>x}", n=nt, d=dt, a=c(a), b=c(b)); e = f"{nt}({a}*x)/{dt}({b}*x)"
    v = Q(a, b); A, B = c(a) + "x", c(b) + "x"
    f1 = SINF if nt == "sin" else TANF
    w = r.randint(0, 2)
    if dt == "lin":
        if a == 1:
            steps = [D(T(r"<fx>=\frac{1}{<b>}\cdot\frac{\<n> x}{x}", fx=fx, b=b, n=nt)), f"{cite(r,f1)} ។"]
        elif w == 0:
            steps = [D(T(r"\lim_{x\to 0}<fx>=\lim_{x\to 0}\left(\frac{\<n> <A>}{<A>}\cdot\frac{<a>}{<b>}\right)=1\cdot\frac{<a>}{<b>}", fx=fx, A=A, a=a, b=b, n=nt))]
        elif w == 1:
            steps = [T("តាង $u=<A>$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ហើយ $x=\\frac{u}{<a>}$ ។", A=A, a=a),
                     D(T(r"\lim_{x\to 0}<fx>=\lim_{u\to 0}\frac{\<n> u}{<b>\cdot\frac{u}{<a>}}=\frac{<a>}{<b>}\lim_{u\to 0}\frac{\<n> u}{u}=\frac{<a>}{<b>}", fx=fx, a=a, b=b, n=nt))]
        else:
            steps = [T("គុណភាគយក និងភាគបែងនឹង $<a>$ ដើម្បីឱ្យកន្សោមមុំនៅភាគបែងដូចនឹង $<A>$ ៖", a=a, A=A),
                     D(T(r"<fx>=\frac{<a>\,\<n> <A>}{<b>\cdot <A>}=\frac{<a>}{<b>}\cdot\frac{\<n> <A>}{<A>}", fx=fx, a=a, b=b, A=A, n=nt)), f"{cite(r,f1)} ។"]
    else:
        f2 = SINF if dt == "sin" else TANF
        if w == 2:
            steps = ["ចែកភាគយក និងភាគបែងនឹង $x$ ៖",
                     D(T(r"<fx>=\frac{\frac{\<n> <A>}{x}}{\frac{\<d> <B>}{x}}", fx=fx, A=A, B=B, n=nt, d=dt)),
                     T("ដោយ $\\frac{\\<n> <A>}{x}\\to <a>$ និង $\\frac{\\<d> <B>}{x}\\to <b>$ កាលណា $x\\to 0$ ។", A=A, B=B, a=a, b=b, n=nt, d=dt)]
        else:
            steps = ["បំប្លែងភាគយក និងភាគបែងឱ្យមានរាងនៃរូបមន្តលីមីត ៖",
                     D(T(r"<fx>=\frac{\<n> <A>}{<A>}\cdot\frac{<B>}{\<d> <B>}\cdot\frac{<A>}{<B>}", fx=fx, A=A, B=B, n=nt, d=dt)),
                     T("កត្តាទាំងពីរខាងដើមខិតជិត $1$ ហើយ $\\frac{<A>}{<B>}=<v>$ ។", A=A, B=B, v=L(v))]
    return P(fx, 0, v, [opener(r, "0")] + steps, "sin_over_x_standard", "easy" if dt == "lin" else "medium", e, hint=f1)

def f_prod(r):
    a, b, d = r.randint(2, 6), r.randint(2, 6), r.randint(2, 7)
    k = r.randint(0, 3)
    if k == 0:
        fx = T(r"\frac{\sin <a>x\,\sin <b>x}{x^{2}}", a=a, b=b); e = f"sin({a}*x)*sin({b}*x)/x**2"; v = a * b
        st = [D(T(r"<fx>=\frac{\sin <a>x}{x}\cdot\frac{\sin <b>x}{x}=<a>\cdot\frac{\sin <a>x}{<a>x}\cdot <b>\cdot\frac{\sin <b>x}{<b>x}", fx=fx, a=a, b=b)),
              T("កាលណា $x\\to 0$ កត្តា $\\frac{\\sin <a>x}{<a>x}$ និង $\\frac{\\sin <b>x}{<b>x}$ ខិតជិត $1$ ។", a=a, b=b)]
    elif k == 1:
        fx = T(r"\frac{\sin <a>x\,\tan <b>x}{x\sin <d>x}", a=a, b=b, d=d); e = f"sin({a}*x)*tan({b}*x)/(x*sin({d}*x))"; v = Q(a * b, d)
        st = ["យើងបំបែកជាផលគុណនៃកត្តាដែលស្គាល់លីមីត ៖",
              D(T(r"<fx>=\frac{\sin <a>x}{x}\cdot\frac{\tan <b>x}{x}\cdot\frac{x}{\sin <d>x}", fx=fx, a=a, b=b, d=d)),
              T("កាលណា $x\\to 0$ កត្តាទាំងបីខិតជិត $<a>$ , $<b>$ និង $<f>$ រៀងគ្នា ។", a=a, b=b, f=L(Q(1, d)))]
    elif k == 2:
        fx = T(r"\frac{\sin^{2}<a>x}{x^{2}}", a=a); e = f"sin({a}*x)**2/x**2"; v = a * a
        st = [D(T(r"<fx>=\left(\frac{\sin <a>x}{x}\right)^{2}=<aa>\left(\frac{\sin <a>x}{<a>x}\right)^{2}", fx=fx, a=a, aa=a * a))]
    else:
        fx = T(r"\frac{\sin^{2}<a>x}{x\tan <b>x}", a=a, b=b); e = f"sin({a}*x)**2/(x*tan({b}*x))"; v = Q(a * a, b)
        st = [D(T(r"<fx>=\left(\frac{\sin <a>x}{<a>x}\right)^{2}\cdot\frac{<b>x}{\tan <b>x}\cdot\frac{<aa>x^{2}}{<b>x^{2}}", fx=fx, a=a, b=b, aa=a * a)),
              T("ផលធៀបចុងក្រោយគឺ $\\frac{<aa>}{<b>}$ ។ កត្តាពីរដំបូងខិតជិត $1$ ។", aa=a * a, b=b)]
    return P(fx, 0, v, [opener(r, "0")] + st, "sin_over_x_products", "medium", e, hint=SINF)

def f_cot(r):
    a, b = r.randint(2, 9), r.randint(2, 9)
    k = r.randint(0, 2)
    if k == 0:
        fx = T(r"x\cot <a>x", a=a); e = f"x*cot({a}*x)"; v = Q(1, a)
        st = ["ប្រើ $\\cot u=\\frac{\\cos u}{\\sin u}$ ៖",
              D(T(r"x\cot <a>x=\frac{x\cos <a>x}{\sin <a>x}=\frac{1}{<a>}\cdot\frac{<a>x}{\sin <a>x}\cdot\cos <a>x", a=a)),
              T("កាលណា $x\\to 0$ គេមាន $\\cos <a>x\\to 1$ និង $\\frac{<a>x}{\\sin <a>x}\\to 1$ ។", a=a)]
        d = "easy"
    elif k == 1:
        fx = T(r"\frac{<b>x}{\tan <a>x}", a=a, b=b); e = f"{b}*x/tan({a}*x)"; v = Q(b, a)
        st = [D(T(r"<fx>=\frac{<b>}{<a>}\cdot\frac{<a>x}{\tan <a>x}", fx=fx, a=a, b=b)), f"{cite(r,TANF)} ។"]
        d = "easy"
    else:
        fx = T(r"\sin <a>x\cot <b>x", a=a, b=b); e = f"sin({a}*x)*cot({b}*x)"; v = Q(a, b)
        st = [D(T(r"\sin <a>x\cot <b>x=\frac{\sin <a>x}{\sin <b>x}\cdot\cos <b>x=\frac{\sin <a>x}{<a>x}\cdot\frac{<b>x}{\sin <b>x}\cdot\frac{<a>}{<b>}\cdot\cos <b>x", a=a, b=b))]
        d = "medium"
    return P(fx, 0, v, st, "sin_over_x_cotangent", d, e)

def f_polyden(r):
    a, b, d = r.randint(2, 9), r.randint(2, 9), r.randint(1, 6)
    k = r.randint(0, 2)
    if k == 0:
        fx = T(r"\frac{\sin <a>x}{x^{2}+<d>x}", a=a, d=c(d)); e = f"sin({a}*x)/(x**2+{d}*x)"; v = Q(a, d)
        st = ["ដាក់ $x$ ជាកត្តារួមនៅភាគបែង ៖",
              D(T(r"<fx>=\frac{\sin <a>x}{x(x+<d>)}=\frac{\sin <a>x}{x}\cdot\frac{1}{x+<d>}", fx=fx, a=a, d=d)),
              T("កត្តាទីមួយខិតជិត $<a>$ ហើយកត្តាទីពីរខិតជិត $\\frac{1}{<d>}$ ។", a=a, d=d)]
    elif k == 1:
        fx = T(r"\frac{x^{2}+<d>x}{\tan <b>x}", b=b, d=c(d)); e = f"(x**2+{d}*x)/tan({b}*x)"; v = Q(d, b)
        st = [D(T(r"<fx>=\frac{x(x+<d>)}{\tan <b>x}=\frac{1}{<b>}\cdot\frac{<b>x}{\tan <b>x}\cdot(x+<d>)", fx=fx, b=b, d=d)),
              T("ដោយ $\\frac{<b>x}{\\tan <b>x}\\to 1$ និង $x+<d>\\to <d>$ ។", b=b, d=d)]
    else:
        fx = T(r"\frac{x^{2}\cos <a>x+<d>x}{\sin <b>x}", a=a, b=b, d=c(d)); e = f"(x**2*cos({a}*x)+{d}*x)/sin({b}*x)"; v = Q(d, b)
        st = [D(T(r"<fx>=\frac{x\left(x\cos <a>x+<d>\right)}{\sin <b>x}=\frac{x}{\sin <b>x}\left(x\cos <a>x+<d>\right)", fx=fx, a=a, b=b, d=d)),
              T("យើងមាន $\\frac{x}{\\sin <b>x}\\to\\frac{1}{<b>}$ ហើយកន្សោមក្នុងវង់ក្រចកខិតជិត $<d>$ ។", b=b, d=d)]
    return P(fx, 0, v, [opener(r, "0")] + st, "sin_over_x_polynomial_denominator", "medium", e)

def f_sumlin(r):
    a, b, d, g = r.randint(1, 6), r.randint(1, 6), r.randint(1, 6), r.randint(1, 6)
    n1 = r.choice(["sin", "tan"]); n2 = r.choice(["sin", "tan"])
    fx = T(r"\frac{\<n1> <a>x+<b>x}{\<n2> <d>x+<g>x}", n1=n1, n2=n2, a=c(a), b=c(b), d=c(d), g=c(g))
    e = f"({n1}({a}*x)+{b}*x)/({n2}({d}*x)+{g}*x)"; v = Q(a + b, d + g)
    st = ["ចែកភាគយក និងភាគបែងនឹង $x$ (ព្រោះ $x\\neq 0$) ៖",
          D(T(r"<fx>=\frac{\frac{\<n1> <a>x}{x}+<b>}{\frac{\<n2> <d>x}{x}+<g>}", fx=fx, n1=n1, n2=n2, a=c(a), b=b, d=c(d), g=g)),
          T("កាលណា $x\\to 0$ ភាគយកខិតជិត $<a>+<b>=<s>$ ហើយភាគបែងខិតជិត $<d>+<g>=<t>$ ។", a=a, b=b, s=a + b, d=d, g=g, t=d + g)]
    return P(fx, 0, v, [opener(r, "0")] + st, "sin_over_x_sum_forms", "medium", e)

def f_1mcos(r):
    a = r.randint(2, 12); w = r.randint(0, 2); b = r.choice([1, 1, 2, 3, 4])
    fx = T(r"\frac{1-\cos <a>x}{<b>x^{2}}", a=a, b=c(b)); e = f"(1-cos({a}*x))/({b}*x**2)"; v = Q(a * a, 2 * b)
    H = hf(a); k = Q(a * a, 2 * b)
    mA = ["ប្រើ $1-\\cos 2u=2\\sin^{2}u$ ៖",
          D(T(r"<fx>=\frac{2\sin^{2}<H>}{<b>x^{2}}=<kk>\left(\frac{\sin <H>}{<H>}\right)^{2}", fx=fx, H=H, b=c(b), kk=c(k))),
          T("កាលណា $x\\to 0$ គេមាន $<H>\\to 0$ ដូច្នេះវង់ក្រចកខិតជិត $1$ ។", H=H)]
    mB = ["គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ $1+\\cos " + str(a) + "x$ ៖",
          D(T(r"<fx>=\frac{1-\cos^{2}<a>x}{<b>x^{2}(1+\cos <a>x)}=\frac{\sin^{2}<a>x}{<b>x^{2}}\cdot\frac{1}{1+\cos <a>x}", fx=fx, a=a, b=c(b))),
          T("ដោយ $\\frac{\\sin^{2}<a>x}{x^{2}}\\to <aa>$ និង $\\frac{1}{1+\\cos <a>x}\\to\\frac{1}{2}$ លទ្ធផលគឺ $\\frac{<aa>}{<b2>}$ ។", a=a, aa=a * a, b2=2 * b)]
    mC = [T("តាង $u=<a>x$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ហើយ $x^{2}=\\frac{u^{2}}{<aa>}$ ។", a=a, aa=a * a),
          D(T(r"\lim_{x\to 0}<fx>=\frac{<aa>}{<b>}\lim_{u\to 0}\frac{1-\cos u}{u^{2}}=\frac{<aa>}{<b>}\cdot\frac{1}{2}", fx=fx, aa=a * a, b=b))]
    st = [mA, mB, mC][w]
    alt = [mA, mB, mC][(w + 1) % 3]
    return P(fx, 0, v, [opener(r, "0")] + st, "one_minus_cos", "medium", e, hint=COSF, alt=alt)

def f_1mcos_mix(r):
    a, b = r.sample(range(2, 10), 2); k = r.randint(0, 3)
    if k == 0:
        fx = T(r"\frac{1-\cos <a>x}{x\sin <b>x}", a=a, b=b); e = f"(1-cos({a}*x))/(x*sin({b}*x))"; v = Q(a * a, 2 * b)
        st = [D(T(r"<fx>=\frac{1-\cos <a>x}{x^{2}}\cdot\frac{x}{\sin <b>x}", fx=fx, a=a, b=b)),
              T("កត្តាទីមួយខិតជិត $\\frac{<aa>}{2}$ ហើយកត្តាទីពីរខិតជិត $\\frac{1}{<b>}$ ។", aa=a * a, b=b)]
    elif k == 1:
        fx = T(r"\frac{1-\cos <a>x}{x\tan <b>x}", a=a, b=b); e = f"(1-cos({a}*x))/(x*tan({b}*x))"; v = Q(a * a, 2 * b)
        st = [T("សរសេរ $1-\\cos <a>x=2\\sin^{2}<H>$ ៖", a=a, H=hf(a)),
              D(T(r"<fx>=2\left(\frac{\sin <H>}{x}\right)^{2}\cdot\frac{x}{\tan <b>x}", fx=fx, H=hf(a), b=b)),
              T("យើងមាន $\\frac{\\sin <H>}{x}\\to <h>$ និង $\\frac{x}{\\tan <b>x}\\to\\frac{1}{<b>}$ ។", H=hf(a), h=L(Q(a, 2)), b=b)]
    elif k == 2:
        fx = T(r"\frac{1-\cos <a>x}{\sin^{2}<b>x}", a=a, b=b); e = f"(1-cos({a}*x))/sin({b}*x)**2"; v = Q(a * a, 2 * b * b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x^{2}$ ៖",
              D(T(r"<fx>=\frac{\frac{1-\cos <a>x}{x^{2}}}{\left(\frac{\sin <b>x}{x}\right)^{2}}", fx=fx, a=a, b=b)),
              T("ភាគយកខិតជិត $\\frac{<aa>}{2}$ ហើយភាគបែងខិតជិត $<bb>$ ។", aa=a * a, bb=b * b)]
    else:
        fx = T(r"\frac{1-\cos <a>x}{1-\cos <b>x}", a=a, b=b); e = f"(1-cos({a}*x))/(1-cos({b}*x))"; v = Q(a * a, b * b)
        st = ["ប្រើ $1-\\cos 2u=2\\sin^{2}u$ លើភាគយក និងភាគបែង ៖",
              D(T(r"<fx>=\frac{\sin^{2}<H>}{\sin^{2}<K>}=\left(\frac{\sin <H>}{<H>}\right)^{2}\left(\frac{<K>}{\sin <K>}\right)^{2}\cdot\frac{<aa>}{<bb>}", fx=fx, H=hf(a), K=hf(b), aa=a * a, bb=b * b))]
    return P(fx, 0, v, [opener(r, "0")] + st, "one_minus_cos_mixed", "hard" if k == 3 else "medium", e)

def f_cosdiff(r):
    a, b = r.sample(range(1, 10), 2)
    A, B = c(a) + "x", c(b) + "x"
    fx = T(r"\frac{\cos <A>-\cos <B>}{x^{2}}", A=A, B=B); e = f"(cos({a}*x)-cos({b}*x))/x**2"; v = Q(b * b - a * a, 2)
    if r.random() < 0.5:
        st = ["បូក និងដក $1$ នៅភាគយក ដើម្បីបំបែកជាពីរតួ ៖",
              D(T(r"<fx>=\frac{1-\cos <B>}{x^{2}}-\frac{1-\cos <A>}{x^{2}}", fx=fx, A=A, B=B)),
              T("ដោយ $\\frac{1-\\cos kx}{x^{2}}\\to\\frac{k^{2}}{2}$ គេបាន $\\frac{<bb>}{2}-\\frac{<aa>}{2}$ ។", aa=a * a, bb=b * b)]
    else:
        s, d = a + b, b - a
        st = ["ប្រើរូបមន្តបំប្លែងផលដកទៅជាផលគុណ $\\cos p-\\cos q=-2\\sin\\frac{p+q}{2}\\sin\\frac{p-q}{2}$ ៖",
              D(T(r"\cos <A>-\cos <B>=2\sin <H>\,\sin <K>", A=A, B=B, H=hf(s), K=hf(d) if d > 0 else "(" + hf(-d) + ")") if d > 0 else
                T(r"\cos <A>-\cos <B>=-2\sin <H>\,\sin <K>", A=A, B=B, H=hf(s), K=hf(-d))),
              T("កាលណា $x\\to 0$ គេមាន $\\frac{\\sin <H>}{x}\\to <h>$ និង $\\frac{\\sin <K>}{x}\\to <k>$ ដូច្នេះលីមីតស្មើ $<sgn>2\\cdot <h>\\cdot <k>$ ។", H=hf(s), K=hf(abs(d)), h=L(Q(s, 2)), k=L(Q(abs(d), 2)), sgn="" if d > 0 else "-")]
    return P(fx, 0, v, [opener(r, "0")] + st, "cos_difference", "hard", e)

def f_sindiff(r):
    a, b = r.sample(range(2, 10), 2); d = r.randint(1, 6); plus = r.random() < 0.5; dt = r.choice(["x", "sin", "tan"])
    op = "+" if plus else "-"; v0 = a + b if plus else a - b
    den = {"x": c(d) + "x", "sin": rf"\sin {c(d)}x", "tan": rf"\tan {c(d)}x"}[dt]
    de = {"x": f"({d}*x)", "sin": f"sin({d}*x)", "tan": f"tan({d}*x)"}[dt]
    fx = T(r"\frac{\sin <a>x<op>\sin <b>x}{<den>}", a=a, b=b, op=op, den=den); e = f"(sin({a}*x){op}sin({b}*x))/{de}"; v = Q(v0, d)
    st = ["ចែកភាគយក និងភាគបែងនឹង $x$ រួចបំបែកភាគយកជាពីរតួ ៖" if dt != "x" else "បំបែកប្រភាគជាពីរតួ ៖",
          D(T(r"\frac{\sin <a>x}{x}<op>\frac{\sin <b>x}{x}\to <a><op><b>=<v0>", a=a, b=b, op=op, v0=v0))]
    if dt != "x":
        st.append(T("រីឯភាគបែង $\\frac{<den>}{x}\\to <d>$ ។", den=den, d=d))
    else:
        st.append(T("បន្ទាប់មកចែកនឹងមេគុណ $<d>$ នៃភាគបែង ។", d=d) if d != 1 else "")
    return P(fx, 0, v, [opener(r, "0")] + st, "sin_sum_difference", "medium", e)

def f_tansin(r):
    a = r.randint(1, 5); k = r.randint(0, 1)
    A = c(a) + "x"
    if k == 0:
        fx = T(r"\frac{\tan <A>-\sin <A>}{x^{3}}", A=A); e = f"(tan({a}*x)-sin({a}*x))/x**3"; v = Q(a ** 3, 2)
        st = ["ដាក់ $\\tan " + A + "$ ជាកត្តារួម ព្រោះ $\\sin u=\\tan u\\cos u$ ៖",
              D(T(r"<fx>=\frac{\tan <A>\,(1-\cos <A>)}{x^{3}}=\frac{\tan <A>}{x}\cdot\frac{1-\cos <A>}{x^{2}}", fx=fx, A=A)),
              T("កត្តាទីមួយខិតជិត $<a>$ ហើយកត្តាទីពីរខិតជិត $\\frac{<aa>}{2}$ ។", a=a, aa=a * a)]
    else:
        fx = T(r"\frac{\sin <A>\,(1-\cos <A>)}{x^{3}}", A=A); e = f"sin({a}*x)*(1-cos({a}*x))/x**3"; v = Q(a ** 3, 2)
        st = [D(T(r"<fx>=\frac{\sin <A>}{x}\cdot\frac{1-\cos <A>}{x^{2}}", fx=fx, A=A)),
              T("កាលណា $x\\to 0$ កត្តាទាំងពីរខិតជិត $<a>$ និង $\\frac{<aa>}{2}$ ។", a=a, aa=a * a)]
    return P(fx, 0, v, [opener(r, "0")] + st, "tan_minus_sin", "hard", e, extra=[(f"limit((1-cos({a}*x))/x**2,x,0)", str(Q(a * a, 2)), "factor")])

def f_cospow(r):
    k = r.randint(0, 2)
    if k == 0:
        n = r.choice([2, 3, 4])
        fx = T(r"\frac{1-\cos^{<n>}x}{x^{2}}", n=n); e = f"(1-cos(x)**{n})/x**2"; v = Q(n, 2)
        fac = {2: r"1+\cos x", 3: r"1+\cos x+\cos^{2}x", 4: r"1+\cos x+\cos^{2}x+\cos^{3}x"}[n]
        st = ["ដាក់ភាគយកជាកត្តា ៖", D(T(r"1-\cos^{<n>}x=(1-\cos x)\left(<fac>\right)", n=n, fac=fac)),
              T("កាលណា $x\\to 0$ វង់ក្រចកខិតជិត $<n>$ ហើយ $\\frac{1-\\cos x}{x^{2}}\\to\\frac{1}{2}$ ។", n=n)]
    elif k == 1:
        a, b = r.sample(range(1, 7), 2)
        fx = T(r"\frac{1-\cos <a>x\cos <b>x}{x^{2}}", a=c(a), b=c(b)); e = f"(1-cos({a}*x)*cos({b}*x))/x**2"; v = Q(a * a + b * b, 2)
        st = [T("បូក និងដក $\\cos <A>x$ នៅភាគយក ៖", A=c(a)),
              D(T(r"1-\cos <A>x\cos <B>x=(1-\cos <A>x)+\cos <A>x\,(1-\cos <B>x)", A=c(a), B=c(b))),
              T("ចែកនឹង $x^{2}$ រួចយកលីមីត គេបាន $\\frac{<aa>}{2}+1\\cdot\\frac{<bb>}{2}$ ។", aa=a * a, bb=b * b)]
    else:
        a = r.randint(1, 5)
        fx = T(r"\frac{\sin <a>2x-2\sin <a>x}{x^{3}}".replace("<a>2x", "<d>x"), a=c(a), d=2 * a); e = f"(sin({2*a}*x)-2*sin({a}*x))/x**3"; v = -a ** 3
        st = [T("ដោយ $\\sin <d>x=2\\sin <A>x\\cos <A>x$ ៖", d=2 * a, A=c(a)),
              D(T(r"<fx>=\frac{2\sin <A>x\,(\cos <A>x-1)}{x^{3}}=-2\cdot\frac{\sin <A>x}{x}\cdot\frac{1-\cos <A>x}{x^{2}}", fx=fx, A=c(a))),
              T("គេបាន $-2\\cdot <a>\\cdot\\frac{<aa>}{2}$ ។", a=a, aa=a * a)]
    return P(fx, 0, v, [opener(r, "0")] + st, "cos_products_and_powers", "hard", e)

def f_shift_poly(r):
    a = r.randint(1, 6); k = r.randint(0, 3); b = r.choice([z for z in range(-5, 7) if z != a and z != 0]); fn = r.choice(["sin", "tan"])
    t_line = T("តាង $t=x-<a>\\Rightarrow x=t+<a>$ ។ បើ $x\\to <a>$ នោះ $t\\to 0$ ។", a=a)
    if k == 0:
        fx = T(r"\frac{\<f>(x-<a>)}{x^{2}-<aa>}", f=fn, a=a, aa=a * a); e = f"{fn}(x-{a})/(x**2-{a*a})"; v = Q(1, 2 * a)
        st = [t_line, D(T(r"\lim_{x\to <a>}<fx>=\lim_{t\to 0}\frac{\<f> t}{t(t+<a2>)}=\lim_{t\to 0}\frac{\<f> t}{t}\cdot\frac{1}{t+<a2>}", fx=fx, f=fn, a=a, a2=2 * a))]
    elif k == 1:
        fx = T(r"\frac{\<f>(x-<a>)}{<q>}", f=fn, a=a, q=lin([(1, "x^{2}"), (-(a + b), "x"), (a * b, "")])); e = f"{fn}(x-{a})/((x-{a})*(x-({b})))"; v = Q(1, a - b)
        st = ["ដាក់ភាគបែងជាកត្តា ៖", D(T(r"<fx>=\frac{\<f>(x-<a>)}{x-<a>}\cdot\frac{1}{<xb>}", fx=fx, f=fn, a=a, xb=lin([(1, "x"), (-b, "")]))),
              T("កាលណា $x\\to <a>$ គេមាន $x-<a>\\to 0$ ដូច្នេះកត្តាទីមួយខិតជិត $1$ ហើយកត្តាទីពីរខិតជិត $<v>$ ។", a=a, v=L(v))]
    elif k == 2:
        fx = T(r"\frac{\<f>(x-<a>)}{x^{3}-<a3>}", f=fn, a=a, a3=a ** 3); e = f"{fn}(x-{a})/(x**3-{a**3})"; v = Q(1, 3 * a * a)
        st = [D(T(r"<fx>=\frac{\<f>(x-<a>)}{(x-<a>)\left(x^{2}+<a>x+<aa>\right)}", fx=fx, f=fn, a=c(a) if False else a, aa=a * a)),
              T("ភាគបែងកត្តាទីពីរខិតជិត $<aa>+<aa>+<aa>=<s>$ ។", aa=a * a, s=3 * a * a)]
    else:
        fx = T(r"\frac{x^{2}-<aa>}{\<f>(<b>x-<ab>)}", f=fn, aa=a * a, b=c(abs(b)), ab=abs(b) * a); e = f"(x**2-{a*a})/{fn}({abs(b)}*x-{abs(b)*a})"; v = Q(2 * a, abs(b))
        B = abs(b)
        st = [T("តាង $t=x-<a>$ ។ កាលណា $x\\to <a>$ គេបាន $t\\to 0$ ហើយ $x^{2}-<aa>=t(t+<a2>)$ ។", a=a, aa=a * a, a2=2 * a),
              D(T(r"\lim_{x\to <a>}<fx>=\lim_{t\to 0}\frac{t(t+<a2>)}{\<f> <b>t}=\lim_{t\to 0}\frac{t}{\<f> <b>t}\cdot(t+<a2>)", fx=fx, f=fn, a=a, a2=2 * a, b=c(B))),
              T("ដោយ $\\frac{t}{\\<f> <b>t}\\to\\frac{1}{<B>}$ លទ្ធផលគឺ $\\frac{<a2>}{<B>}$ ។", f=fn, b=c(B), B=B, a2=2 * a)]
    return P(fx, a, v, [opener(r, str(a))] + st, "change_of_variable_shift", "medium", e)

def f_shift_pi(r):
    n = r.randint(1, 5); k = r.randint(0, 3); m = r.randint(1, 4)
    if k == 0:
        fx = T(r"\frac{\sin <m>\pi x}{x-<n>}", m=c(m), n=n); e = f"sin({m}*pi*x)/(x-{n})"; s = (-1) ** (m * n); v = s * m * PI; p = n
        st = [T("តាង $t=x-<n>$ ។ បើ $x\\to <n>$ នោះ $t\\to 0$ ។", n=n),
              D(T(r"\sin <m>\pi x=\sin\left(<m>\pi t+<mn>\pi\right)=<s>\sin <m>\pi t", m=c(m), mn=m * n, s="" if s == 1 else "-")),
              D(T(r"\lim_{t\to 0}\frac{<s>\sin <m>\pi t}{t}=<s><m>\pi\lim_{t\to 0}\frac{\sin <m>\pi t}{<m>\pi t}", m=c(m), s="" if s == 1 else "-"))]
    elif k == 1:
        fx = T(r"\frac{\tan \pi x}{x-<n>}", n=n); e = f"tan(pi*x)/(x-{n})"; v = PI; p = n
        st = [T("តាង $t=x-<n>$ ។ ដោយ $\\tan$ មានខួប $\\pi$ គេបាន $\\tan\\pi x=\\tan(\\pi t+<n>\\pi)=\\tan\\pi t$ ។", n=c(n)),
              D(r"\lim_{t\to 0}\frac{\tan\pi t}{t}=\pi\lim_{t\to 0}\frac{\tan\pi t}{\pi t}")]
    elif k == 2:
        fx = r"\frac{\cos\frac{\pi x}{2}}{x-1}"; e = "cos(pi*x/2)/(x-1)"; v = -PI / 2; p = 1
        d = r.randint(2, 5)
        fx = T(r"\frac{\cos\frac{\pi x}{2}}{<d>x-<d>}", d=d); e = f"cos(pi*x/2)/({d}*x-{d})"; v = -PI / (2 * d)
        st = ["តាង $t=x-1$ ។ បើ $x\\to 1$ នោះ $t\\to 0$ ហើយ ៖",
              D(r"\cos\frac{\pi x}{2}=\cos\left(\frac{\pi}{2}+\frac{\pi t}{2}\right)=-\sin\frac{\pi t}{2}"),
              D(T(r"\lim_{t\to 0}\frac{-\sin\frac{\pi t}{2}}{<d>t}=-\frac{\pi}{<d2>}\lim_{t\to 0}\frac{\sin\frac{\pi t}{2}}{\frac{\pi t}{2}}", d=d, d2=2 * d))]
    else:
        fx = r"\frac{\sin\pi x}{x^{2}-1}"; e = "sin(pi*x)/(x**2-1)"; v = -PI / 2; p = 1
        q = r.randint(1, 4)
        fx = T(r"\frac{\sin\pi x}{(x-1)(x+<q>)}", q=q); e = f"sin(pi*x)/((x-1)*(x+{q}))"; v = -PI / (1 + q)
        st = ["តាង $t=x-1$ ។ បើ $x\\to 1$ នោះ $t\\to 0$ ហើយ $\\sin\\pi x=\\sin(\\pi t+\\pi)=-\\sin\\pi t$ ។",
              D(T(r"\lim_{t\to 0}\frac{-\sin\pi t}{t(t+<q1>)}=-\lim_{t\to 0}\frac{\sin\pi t}{t}\cdot\frac{1}{t+<q1>}=-\pi\cdot\frac{1}{<q1>}", q1=q + 1))]
    return P(fx, p, v, st, "change_of_variable_pi", "hard", e)

def f_pi2(r):
    k = r.randint(0, 7); d = r.randint(2, 6); t0 = "តាង $t=x-\\frac{\\pi}{2}$ ។ បើ $x\\to\\frac{\\pi}{2}$ នោះ $t\\to 0$ ។"
    if k == 0:
        fx = T(r"\frac{<d>\cos x}{x-\frac{\pi}{2}}", d=d); e = f"{d}*cos(x)/(x-pi/2)"; v = -d
        st = [t0, D(T(r"<d>\cos x=<d>\cos\left(t+\frac{\pi}{2}\right)=-<d>\sin t", d=d)), D(T(r"\lim_{t\to 0}\frac{-<d>\sin t}{t}=-<d>", d=d))]
    elif k == 1:
        fx = T(r"\frac{\cos x}{<d>\pi-<d2>x}", d=c(d), d2=2 * d); e = f"cos(x)/({d}*pi-{2*d}*x)"; v = Q(1, 2 * d)
        st = [t0, D(T(r"<d2>x=<d2>t+<d>\pi\ \Rightarrow\ <d>\pi-<d2>x=-<d2>t", d=c(d), d2=2 * d)),
              D(T(r"\lim_{t\to 0}\frac{\cos\left(t+\frac{\pi}{2}\right)}{-<d2>t}=\lim_{t\to 0}\frac{-\sin t}{-<d2>t}=\frac{1}{<d2>}", d2=2 * d))]
    elif k == 2:
        fx = r"\frac{1-\sin x}{\left(x-\frac{\pi}{2}\right)^{2}}"; e = "(1-sin(x))/(x-pi/2)**2"; v = Q(1, 2)
        st = [t0, D(r"1-\sin x=1-\sin\left(t+\frac{\pi}{2}\right)=1-\cos t"), D(r"\lim_{t\to 0}\frac{1-\cos t}{t^{2}}=\frac{1}{2}")]
    elif k == 3:
        fx = r"\frac{1-\sin x}{\cos^{2}x}"; e = "(1-sin(x))/cos(x)**2"; v = Q(1, 2)
        st = ["ដោយ $\\cos^{2}x=1-\\sin^{2}x=(1-\\sin x)(1+\\sin x)$ យើងសម្រួលកត្តា $1-\\sin x$ ៖",
              D(r"\frac{1-\sin x}{\cos^{2}x}=\frac{1}{1+\sin x}"), "ឥឡូវជំនួស $x=\\frac{\\pi}{2}$ បាន ៖ $\\frac{1}{1+1}$ ។"]
    elif k == 4:
        fx = T(r"(<d>\pi-<d2>x)\tan x", d=c(d), d2=2 * d); e = f"({d}*pi-{2*d}*x)*tan(x)"; v = 2 * d
        st = [t0, D(r"\tan x=\tan\left(t+\frac{\pi}{2}\right)=-\cot t=-\frac{\cos t}{\sin t}"),
              D(T(r"\lim_{t\to 0}(-<d2>t)\left(-\frac{\cos t}{\sin t}\right)=<d2>\lim_{t\to 0}\frac{t}{\sin t}\cos t=<d2>", d2=2 * d))]
    elif k == 5:
        fx = T(r"\frac{\sin <d2>x}{\cos x}", d2=2); e = "sin(2*x)/cos(x)"; v = 2
        st = ["ប្រើ $\\sin 2x=2\\sin x\\cos x$ រួចសម្រួលកត្តា $\\cos x$ ៖", D(r"\frac{\sin 2x}{\cos x}=2\sin x"), "ដោយ $\\sin\\frac{\\pi}{2}=1$ ។"]
    elif k == 6:
        o = r.choice([3, 5, 7]); s = (-1) ** ((o - 1) // 2)
        fx = T(r"\frac{\cos <o>x}{\cos x}", o=o); e = f"cos({o}*x)/cos(x)"; v = -o * s * (-1) if False else (o if o % 4 == 1 else -o)
        sgn1 = "" if o % 4 == 3 else "-"   # cos(o(t+pi/2)) = sign * sin(o t)
        st = [t0, D(T(r"\cos <o>x=\cos\left(<o>t+\frac{<o>\pi}{2}\right)=<s1>\sin <o>t", o=o, s1=sgn1)),
              D(r"\cos x=\cos\left(t+\frac{\pi}{2}\right)=-\sin t"),
              D(T(r"\lim_{t\to 0}\frac{<s1>\sin <o>t}{-\sin t}=<v>", o=o, s1=sgn1, v=L(v)))]
    else:
        fx = r"\frac{1-\sin x}{(\pi-2x)^{2}}"; e = "(1-sin(x))/(pi-2*x)**2"; v = Q(1, 8)
        st = [t0, D(r"\pi-2x=-2t,\qquad 1-\sin x=1-\cos t"), D(r"\lim_{t\to 0}\frac{1-\cos t}{4t^{2}}=\frac{1}{4}\cdot\frac{1}{2}")]
    return P(fx, "pi/2", v, st, "change_of_variable_pi_over_2", "hard" if k in (6, 7, 4) else "medium", e)

def f_abcos(r):
    tbl = [(PI / 6, 2, 0, -1), (PI / 6, 0, 2, -SQ(3)), (PI / 6, 1, -SQ(3), 1), (PI / 6, SQ(3), -1, 0), (PI / 6, -2, 0, 1),
           (PI / 3, 2, 0, -SQ(3)), (PI / 3, 0, 2, -1), (PI / 3, 1, -SQ(3), 0), (PI / 3, 0, -2, 1),
           (PI / 4, 1, -1, 0), (PI / 4, SQ(2), 0, -1), (PI / 4, 0, SQ(2), -1), (PI / 4, -1, 1, 0),
           (PI, 1, 0, 0), (2 * PI / 3, 2, 0, -SQ(3)), (2 * PI / 3, 0, 2, 1)]
    cc, p, q, rr = r.choice(tbl); k = r.choice([1, 1, 2, 3])
    sc, co = sp.sin(cc), sp.cos(cc)
    A = sp.nsimplify(p * co - q * sc); B = sp.nsimplify(p * sc + q * co)
    assert sp.simplify(B + rr) == 0 and A != 0
    cl = L(cc); num = lin([(p, r"\sin x"), (q, r"\cos x"), (rr, "")])
    den = rf"{c(k)}\left(x-{cl}\right)" if k != 1 else f"x-{cl}"
    fx = rf"\frac{{{num}}}{{{den}}}"; e = f"(({p})*sin(x)+({q})*cos(x)+({rr}))/({k}*(x-{cc}))"
    v = sp.nsimplify(A / k)
    t1 = f"តាង $t=x-{cl}\\Rightarrow x=t+{cl}$ ។ បើ $x\\to {cl}$ នោះ $t\\to 0$ ។"
    exp_ = lin([(A, r"\sin t"), (B, r"\cos t"), (rr, "")])
    st = [t1, "ប្រើរូបមន្តបូកមុំលើភាគយក ៖", D(rf"{num}={exp_}")]
    if B != 0:
        st += ["ដូច្នេះ", D(rf"\lim_{{t\to 0}}\frac{{{exp_}}}{{{c(k)}t}}=\frac{{1}}{{{k}}}\left({L(A)}\lim_{{t\to 0}}\frac{{\sin t}}{{t}}{sg(B)}\lim_{{t\to 0}}\frac{{\cos t-1}}{{t}}\right)".replace(r"\frac{1}{1}\left(", r"\left(")),
               "ដោយ $\\frac{\\cos t-1}{t}=-t\\cdot\\frac{1-\\cos t}{t^{2}}\\to 0$ ហើយ $\\frac{\\sin t}{t}\\to 1$ ។"]
    else:
        st += [D(rf"\lim_{{t\to 0}}\frac{{{exp_}}}{{{c(k)}t}}=\frac{{{L(A)}}}{{{k}}}\lim_{{t\to 0}}\frac{{\sin t}}{{t}}")]
    return P(fx, cc, v, st, "change_of_variable_special_angle", "hard", e, hint=None)

def f_pi4(r):
    t0 = "តាង $t=x-\\frac{\\pi}{4}$ ។"
    k = r.randint(0, 5)
    if k == 0:
        fx = r"\frac{1-\tan x}{x-\frac{\pi}{4}}"; e = "(1-tan(x))/(x-pi/4)"; v = -2
        st = [t0 + " តាមរូបមន្តបូកមុំ ៖", D(r"\tan\left(t+\frac{\pi}{4}\right)=\frac{1+\tan t}{1-\tan t}"),
              D(r"1-\tan x=1-\frac{1+\tan t}{1-\tan t}=\frac{-2\tan t}{1-\tan t}"),
              D(r"\lim_{t\to 0}\frac{-2\tan t}{t(1-\tan t)}=-2\lim_{t\to 0}\frac{\tan t}{t}\cdot\frac{1}{1-\tan t}=-2")]
    elif k == 1:
        fx = r"\frac{\cos 2x}{\sin x-\cos x}"; e = "cos(2*x)/(sin(x)-cos(x))"; v = -SQ(2)
        st = ["ដាក់ភាគយកជាកត្តា ៖", D(r"\cos 2x=\cos^{2}x-\sin^{2}x=-(\sin x-\cos x)(\sin x+\cos x)"),
              "សម្រួលកត្តា $\\sin x-\\cos x$ យើងនៅសល់ ៖", D(r"\frac{\cos 2x}{\sin x-\cos x}=-(\sin x+\cos x)"),
              "ជំនួស $x=\\frac{\\pi}{4}$ ៖ $-\\left(\\frac{\\sqrt{2}}{2}+\\frac{\\sqrt{2}}{2}\\right)=-\\sqrt{2}$ ។"]
    elif k == 2:
        fx = r"\frac{\tan x-1}{\sin x-\cos x}"; e = "(tan(x)-1)/(sin(x)-cos(x))"; v = SQ(2)
        st = ["ដោយ $\\tan x-1=\\frac{\\sin x-\\cos x}{\\cos x}$ យើងបាន ៖", D(r"\frac{\tan x-1}{\sin x-\cos x}=\frac{1}{\cos x}"),
              "កាលណា $x\\to\\frac{\\pi}{4}$ គេមាន $\\frac{1}{\\cos x}\\to\\frac{2}{\\sqrt{2}}=\\sqrt{2}$ ។"]
    elif k == 3:
        fx = r"\frac{1-\tan x}{\cos 2x}"; e = "(1-tan(x))/cos(2*x)"; v = 1
        st = ["សរសេរភាគយក និងភាគបែងជាកត្តាដែលមាន $\\cos x-\\sin x$ ៖", D(r"1-\tan x=\frac{\cos x-\sin x}{\cos x},\qquad\cos 2x=(\cos x-\sin x)(\cos x+\sin x)"),
              D(r"\frac{1-\tan x}{\cos 2x}=\frac{1}{\cos x\,(\cos x+\sin x)}"), "ជំនួស $x=\\frac{\\pi}{4}$ ៖ $\\frac{1}{\\frac{\\sqrt{2}}{2}\\cdot\\sqrt{2}}=1$ ។"]
    elif k == 4:
        fx = r"\frac{\sin x-\cos x}{\cos 2x}"; e = "(sin(x)-cos(x))/cos(2*x)"; v = -SQ(2) / 2
        st = [D(r"\frac{\sin x-\cos x}{\cos 2x}=\frac{\sin x-\cos x}{(\cos x-\sin x)(\cos x+\sin x)}=\frac{-1}{\cos x+\sin x}"),
              "ដោយ $\\cos\\frac{\\pi}{4}+\\sin\\frac{\\pi}{4}=\\sqrt{2}$ ។ លទ្ធផលគឺ $-\\frac{1}{\\sqrt{2}}=-\\frac{\\sqrt{2}}{2}$ ។"]
    else:
        fx = r"\frac{\sin x-\cos x}{1-\tan x}"; e = "(sin(x)-cos(x))/(1-tan(x))"; v = -SQ(2) / 2
        st = [D(r"\frac{\sin x-\cos x}{1-\tan x}=\frac{\sin x-\cos x}{\frac{\cos x-\sin x}{\cos x}}=-\cos x"), "កាលណា $x\\to\\frac{\\pi}{4}$ គេមាន $-\\cos x\\to-\\frac{\\sqrt{2}}{2}$ ។"]
    return P(fx, "pi/4", v, [opener(r, r"\frac{\pi}{4}")] + st, "trig_factor_at_pi_over_4", "hard" if k == 0 else "medium", e)

# ---------------- roots with trig -----------------
def f_rootlin(r):
    a, b, g = r.randint(1, 6), r.randint(2, 7), r.randint(1, 5); k = r.randint(0, 2); fn = r.choice(["sin", "tan"])
    if k == 0:
        fx = T(r"\frac{\sqrt{1+<a>x}-1}{\<f> <b>x}", a=c(a), b=b, f=fn); e = f"(sqrt(1+{a}*x)-1)/{fn}({b}*x)"; v = Q(a, 2 * b)
        st = ["គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ ៖",
              D(T(r"<fx>=\frac{<a>x}{\<f> <b>x\left(\sqrt{1+<a>x}+1\right)}", fx=fx, a=c(a), b=b, f=fn)),
              T("ដោយ $\\frac{x}{\\<f> <b>x}\\to\\frac{1}{<b>}$ និង $\\sqrt{1+<a>x}+1\\to 2$ ។", a=c(a), b=b, f=fn)]
    elif k == 1:
        fx = T(r"\frac{\sqrt{x+<gg>}-<g>}{\<f> <b>x}", gg=g * g, g=g, b=b, f=fn); e = f"(sqrt(x+{g*g})-{g})/{fn}({b}*x)"; v = Q(1, 2 * b * g)
        st = ["យើងគុណនឹងកន្សោមឆ្លាស់ ដើម្បីលុបឫសនៅភាគយក ៖",
              D(T(r"<fx>=\frac{x}{\<f> <b>x}\cdot\frac{1}{\sqrt{x+<gg>}+<g>}", fx=fx, gg=g * g, g=g, b=b, f=fn)),
              T("កាលណា $x\\to 0$ កត្តាទាំងពីរខិតជិត $\\frac{1}{<b>}$ និង $\\frac{1}{<g2>}$ ។", b=b, g2=2 * g)]
    else:
        fx = T(r"\frac{\<f> <b>x}{\sqrt{x+<gg>}-<g>}", gg=g * g, g=g, b=b, f=fn); e = f"{fn}({b}*x)/(sqrt(x+{g*g})-{g})"; v = 2 * b * g
        st = ["គុណភាគយក និងភាគបែងនឹង $\\sqrt{x+" + str(g * g) + "}+" + str(g) + "$ ៖",
              D(T(r"<fx>=\frac{\<f> <b>x\left(\sqrt{x+<gg>}+<g>\right)}{x}", fx=fx, gg=g * g, g=g, b=b, f=fn)),
              T("ដោយ $\\frac{\\<f> <b>x}{x}\\to <b>$ និង $\\sqrt{x+<gg>}+<g>\\to <g2>$ ។", f=fn, b=b, gg=g * g, g=g, g2=2 * g)]
    return P(fx, 0, v, [opener(r, "0")] + st, "root_and_trig", "medium", e)

def f_roottrig(r):
    a, b = r.randint(1, 6), r.randint(1, 6); k = r.randint(0, 3)
    if k == 0:
        fx = T(r"\frac{\sqrt{1+\sin <a>x}-1}{x}", a=c(a)); e = f"(sqrt(1+sin({a}*x))-1)/x"; v = Q(a, 2)
        st = ["គុណនឹងកន្សោមឆ្លាស់ ៖", D(T(r"<fx>=\frac{\sin <a>x}{x\left(\sqrt{1+\sin <a>x}+1\right)}", fx=fx, a=c(a))),
              T("ដោយ $\\frac{\\sin <A>x}{x}\\to <a>$ ហើយភាគបែងដែលនៅសល់ខិតជិត $2$ ។", A=c(a), a=a)]
    elif k == 1:
        fx = T(r"\frac{\sqrt{1+\tan <a>x}-\sqrt{1-\tan <a>x}}{\sin <b>x}", a=c(a), b=c(b)); e = f"(sqrt(1+tan({a}*x))-sqrt(1-tan({a}*x)))/sin({b}*x)"; v = Q(a, b)
        st = ["គុណភាគយក និងភាគបែងនឹង $\\sqrt{1+\\tan " + c(a) + "x}+\\sqrt{1-\\tan " + c(a) + "x}$ ៖",
              D(T(r"<fx>=\frac{2\tan <a>x}{\sin <b>x\left(\sqrt{1+\tan <a>x}+\sqrt{1-\tan <a>x}\right)}", fx=fx, a=c(a), b=c(b))),
              T("វង់ក្រចកខិតជិត $2$ ហើយ $\\frac{\\tan <A>x}{\\sin <B>x}\\to\\frac{<a>}{<b>}$ ។", A=c(a), B=c(b), a=a, b=b)]
    elif k == 2:
        fx = T(r"\frac{1-\cos <a>x}{\sqrt{1+x^{2}}-1}", a=c(a)); e = f"(1-cos({a}*x))/(sqrt(1+x**2)-1)"; v = a * a
        st = ["គុណភាគយក និងភាគបែងនឹង $\\sqrt{1+x^{2}}+1$ ៖",
              D(T(r"<fx>=\frac{(1-\cos <a>x)\left(\sqrt{1+x^{2}}+1\right)}{x^{2}}", fx=fx, a=c(a))),
              T("គេបាន $\\frac{<aa>}{2}\\cdot 2$ ព្រោះ $\\frac{1-\\cos <A>x}{x^{2}}\\to\\frac{<aa>}{2}$ ។", aa=a * a, A=c(a))]
    else:
        fx = T(r"\frac{1-\sqrt{\cos <a>x}}{x^{2}}", a=c(a)); e = f"(1-sqrt(cos({a}*x)))/x**2"; v = Q(a * a, 4)
        st = ["គុណនឹងកន្សោមឆ្លាស់ $1+\\sqrt{\\cos " + c(a) + "x}$ ៖",
              D(T(r"<fx>=\frac{1-\cos <a>x}{x^{2}}\cdot\frac{1}{1+\sqrt{\cos <a>x}}", fx=fx, a=c(a))),
              T("លីមីតគឺ $\\frac{<aa>}{2}\\cdot\\frac{1}{2}$ ។", aa=a * a)]
    return P(fx, 0, v, [opener(r, "0")] + st, "root_and_trig", "hard", e)

# ---------------- substitution t = 1/x at infinity -----------------
def f_inf_trig(r):
    a = r.randint(1, 9); b = r.randint(2, 6); d = r.randint(1, 5); k = r.randint(0, 3); p = r.choice(["oo", "oo", "-oo"])
    pt = ptl(p); fr = rf"\frac{{{a}}}{{x}}"
    tl = T("តាង $t=\\frac{1}{x}$ ។ បើ $x\\to <pt>$ នោះ $t\\to 0$ ។", pt=pt)
    if k == 0:
        fx = rf"x\sin {fr}"; e = f"x*sin({a}/x)"; v = a
        st = [tl, D(T(r"\lim_{x\to <pt>}x\sin <fr>=\lim_{t\to 0}\frac{\sin <a>t}{t}", pt=pt, fr=fr, a=c(a)))]
    elif k == 1:
        fx = rf"{b}x\tan {fr}"; e = f"{b}*x*tan({a}/x)"; v = a * b
        st = [tl, D(T(r"\lim_{x\to <pt>}<b>x\tan <fr>=<b>\lim_{t\to 0}\frac{\tan <a>t}{t}", pt=pt, fr=fr, a=c(a), b=b))]
    elif k == 2:
        fx = rf"x^{{2}}\left(1-\cos {fr}\right)"; e = f"x**2*(1-cos({a}/x))"; v = Q(a * a, 2)
        st = [tl, D(T(r"\lim_{t\to 0}\frac{1-\cos <a>t}{t^{2}}=\frac{<aa>}{2}", a=c(a), aa=a * a))]
    else:
        fx = rf"({b}x+{d})\sin {fr}"; e = f"({b}*x+{d})*sin({a}/x)"; v = a * b
        st = ["បំបែកជាពីរតួ ៖", D(rf"({b}x+{d})\sin {fr}={b}x\sin {fr}+{d}\sin {fr}"),
              T("កាលណា $x\\to <pt>$ តួទីពីរខិតជិត $<d>\\sin 0=0$ ។ សម្រាប់តួទីមួយ <tl>", pt=pt, d=d, tl=tl),
              D(T(r"\lim_{t\to 0}\frac{<b>\sin <a>t}{t}=<v>", b=b, a=c(a), v=a * b))]
    return P(fx, p, v, st, "change_of_variable_reciprocal", "medium", e)

# ---------------- comparison and squeeze -----------------
def f_sq0(r):
    n = r.randint(1, 3); a = r.randint(1, 5); fn = r.choice(["sin", "cos"]); b = r.choice([1, 1, 2, 3])
    arg = r"\frac{1}{x}" if a == 1 else rf"\frac{{{a}}}{{x}}"
    fx = rf"{c(b)}{px(n)}\{fn} {arg}"; e = f"{b}*x**{n}*{fn}({a}/x)"
    even = n % 2 == 0; ax = px(n) if even else rf"|{px(n)}|"; bb = c(b)
    st = [f"ចំពោះ $x\\neq 0$ យើងមាន $-1\\le\\{fn} {arg}\\le 1$ ។ គុណនឹង $" + (f"{bb}{ax}" ) + "$ ដែលមិនអវិជ្ជមាន គេបានវិសមភាព ៖",
          D(rf"-{bb}{ax}\le {bb}{ax}\{fn} {arg}\le {bb}{ax}"),
          "" if even else f"ហើយ ${fx}$ ស្មើ ${bb}{ax}\\{fn} {arg}$ ឬផ្ទុយរបស់វា ដូច្នេះវាក៏នៅចន្លោះ $-{bb}{ax}$ និង ${bb}{ax}$ ដែរ ។",
          f"កាលណា $x\\to 0$ អង្គទាំងសងខាងនៃវិសមភាពខិតជិត $0$ ។ អនុគមន៍ដែលនៅចន្លោះ ក៏ត្រូវខិតជិត $0$ ដែរ ។"]
    return P(fx, 0, 0, st, "squeeze_at_zero", "medium", e, extra=[(f"limit({b}*Abs(x)**{n},x,0)", "0", "bound")])

def f_sqinf(r):
    k = r.randint(0, 4); a = r.randint(1, 6); b = r.randint(2, 6); n = r.randint(1, 3)
    if k == 0:
        fx = T(r"\frac{\sin <a>x}{<n>}", a=c(a), n=px(n)); e = f"sin({a}*x)/x**{n}"; bd = f"1/x**{n}"
        st = [T("ចំពោះ $x>0$ យើងមាន $-\\frac{1}{<n>}\\le\\frac{\\sin <a>x}{<n>}\\le\\frac{1}{<n>}$ ។", a=c(a), n=px(n))]
    elif k == 1:
        fx = T(r"\frac{<b>+\cos <a>x}{<n>}", a=c(a), n=px(n), b=b); e = f"({b}+cos({a}*x))/x**{n}"; bd = f"{b+1}/x**{n}"
        st = [T("ដោយ $-1\\le\\cos <a>x\\le 1$ យើងមាន $<b1>\\le <b>+\\cos <a>x\\le <b2>$ ។ ចែកនឹង $<n>>0$ ៖", a=c(a), b=b, b1=b - 1, b2=b + 1, n=px(n)),
              D(T(r"\frac{<b1>}{<n>}\le <fx>\le\frac{<b2>}{<n>}", b1=b - 1, b2=b + 1, n=px(n), fx=fx))]
    elif k == 2:
        fn = r.choice(["sin", "cos"])
        fx = T(r"e^{-<a>x}\<f> x", a=c(a), f=fn); e = f"exp(-{a}*x)*{fn}(x)"; bd = f"exp(-{a}*x)"
        st = [T("ដោយ $-1\\le\\<f> x\\le 1$ ហើយ $e^{-<a>x}>0$ យើងបាន ៖", f=fn, a=c(a)), D(T(r"-e^{-<a>x}\le e^{-<a>x}\<f> x\le e^{-<a>x}", f=fn, a=c(a)))]
    elif k == 3:
        fx = T(r"\frac{\sin x+\cos x}{<n>}", n=px(n)); e = f"(sin(x)+cos(x))/x**{n}"; bd = f"2/x**{n}"
        st = [T("ដោយ $|\\sin x+\\cos x|\\le|\\sin x|+|\\cos x|\\le 2$ គេបាន ៖", n=n), D(T(r"-\frac{2}{<n>}\le <fx>\le\frac{2}{<n>}", n=px(n), fx=fx))]
    else:
        fx = T(r"\frac{x\cos <a>x}{x^{2}+<b>}", a=c(a), b=b); e = f"x*cos({a}*x)/(x**2+{b})"; bd = f"x/(x**2+{b})"
        st = [T("ចំពោះ $x>0$ ៖ $\\left|\\frac{x\\cos <a>x}{x^{2}+<b>}\\right|\\le\\frac{x}{x^{2}+<b>}$ ។", a=c(a), b=b),
              T("ហើយ $\\frac{x}{x^{2}+<b>}\\le\\frac{x}{x^{2}}=\\frac{1}{x}$ ។", b=b)]
    st.append(r.choice(["អង្គសងខាងខិតជិត $0$ កាលណា $x\\to+\\infty$ ដូច្នេះកន្សោមដែលនៅចន្លោះក៏ខិតជិត $0$ ដែរ ។",
                        "កាលណា $x\\to+\\infty$ អនុគមន៍ទាំងពីរដែលនៅសងខាងមានលីមីត $0$ ដូចគ្នា ដូច្នេះអនុគមន៍នៅចន្លោះក៏មានលីមីត $0$ ។"]))
    return P(fx, "oo", 0, st, "squeeze_at_infinity", "medium", e, extra=[(f"limit({bd},x,oo)", "0", "bound")])

def f_bounded_ratio(r):
    a, b, d = r.randint(2, 9), r.randint(2, 9), r.randint(1, 9); k = r.randint(0, 2)
    if k == 0:
        fx = T(r"\frac{<a>x+\sin x}{<b>x+\cos x}", a=a, b=b); e = f"({a}*x+sin(x))/({b}*x+cos(x))"; v = Q(a, b)
        st = ["ដាក់ $x$ ជាកត្តារួម ៖", D(T(r"<fx>=\frac{x\left(<a>+\frac{\sin x}{x}\right)}{x\left(<b>+\frac{\cos x}{x}\right)}", fx=fx, a=a, b=b)),
              "ដោយ $\\left|\\frac{\\sin x}{x}\\right|\\le\\frac{1}{x}$ និង $\\left|\\frac{\\cos x}{x}\\right|\\le\\frac{1}{x}$ ចំពោះ $x>0$ កន្សោមទាំងពីរនេះខិតជិត $0$ ។"]
    elif k == 1:
        fx = T(r"\frac{<a>x^{2}+\cos x}{<b>x^{2}+<d>}", a=a, b=b, d=d); e = f"({a}*x**2+cos(x))/({b}*x**2+{d})"; v = Q(a, b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x^{2}$ ៖", D(T(r"<fx>=\frac{<a>+\frac{\cos x}{x^{2}}}{<b>+\frac{<d>}{x^{2}}}", fx=fx, a=a, b=b, d=d)),
              "ដោយ $-\\frac{1}{x^{2}}\\le\\frac{\\cos x}{x^{2}}\\le\\frac{1}{x^{2}}$ គេបាន $\\frac{\\cos x}{x^{2}}\\to 0$ ។"]
    else:
        fx = T(r"\frac{<a>x-<d>\sin x}{x}", a=a, d=c(d)); e = f"({a}*x-{d}*sin(x))/x"; v = a
        st = [D(T(r"<fx>=<a>-<d>\cdot\frac{\sin x}{x}", fx=fx, a=a, d=d)), "ដោយ $\\left|\\frac{\\sin x}{x}\\right|\\le\\frac{1}{|x|}$ យើងបាន $\\frac{\\sin x}{x}\\to 0$ កាលណា $x\\to+\\infty$ ។"]
    return P(fx, "oo", v, st, "bounded_term_at_infinity", "medium", e)

def f_compare(r):
    a, b = r.randint(2, 6), r.randint(1, 5); k = r.randint(0, 4)
    if k == 0:
        fx = T(r"x(<a>+\sin x)", a=a); e = f"x*({a}+sin(x))"
        st = [T("ដោយ $\\sin x\\ge -1$ យើងមាន $<a>+\\sin x\\ge <a1>$ ។ ចំពោះ $x>0$ ៖", a=a, a1=a - 1), D(T(r"x(<a>+\sin x)\ge <a1>x", a=a, a1=c(a - 1))),
              "ដោយអង្គស្តាំខិតជិត $+\\infty$ អង្គឆ្វេងដែលធំជាងវា ក៏ខិតជិត $+\\infty$ ដែរ ។"]
        ex = [(f"limit({a-1}*x,x,oo)", "oo", "lower bound"), (f"subs(x*({a}+sin(x))-{a-1}*x,x,pi/2)", f"{a}*pi/2+pi/2-{a-1}*pi/2", "instance of the bound")]
        p, v = "oo", oo
    elif k == 1:
        fx = T(r"x^{2}+<b>\sin x", b=c(b)); e = f"x**2+{b}*sin(x)"
        st = [T("ដោយ $<b>\\sin x\\ge -<b>$ គេបាន $x^{2}+<b>\\sin x\\ge x^{2}-<b>$ ។", b=c(b) if b != 1 else ""),
              "ហើយ $x^{2}" + f"-{b}" + "\\to+\\infty$ កាលណា $x\\to+\\infty$ ។ អនុគមន៍ដែលធំជាងវាក៏ខិតជិត $+\\infty$ ។"]
        ex = [(f"limit(x**2-{b},x,oo)", "oo", "lower bound")]; p, v = "oo", oo
    elif k == 2:
        fx = T(r"e^{x}(<a>+\cos x)", a=a); e = f"exp(x)*({a}+cos(x))"
        st = [T("ដោយ $<a>+\\cos x\\ge <a1>$ និង $e^{x}>0$ យើងមាន ៖", a=a, a1=a - 1), D(T(r"e^{x}(<a>+\cos x)\ge <a1>e^{x}", a=a, a1=c(a - 1))),
              "ហើយ $e^{x}\\to+\\infty$ កាលណា $x\\to+\\infty$ ។ ដូច្នេះអង្គឆ្វេងខិតជិត $+\\infty$ ។"]
        ex = [(f"limit({a-1}*exp(x),x,oo)", "oo", "lower bound")]; p, v = "oo", oo
    elif k == 3:
        fx = T(r"<a>x+\cos x", a=c(a)); e = f"{a}*x+cos(x)"
        st = [T("ដោយ $\\cos x\\le 1$ យើងបាន $<a>x+\\cos x\\le <a>x+1$ ។", a=c(a)),
              T("កាលណា $x\\to-\\infty$ គេមាន $<a>x+1\\to-\\infty$ ។ អនុគមន៍ដែលតូចជាងវាក៏ខិតជិត $-\\infty$ ដែរ ។", a=c(a))]
        ex = [(f"limit({a}*x+1,x,-oo)", "-oo", "upper bound")]; p, v = "-oo", -oo
    else:
        fx = T(r"<a>x-\sin x", a=c(a)); e = f"{a}*x-sin(x)"
        st = [T("ដោយ $\\sin x\\le 1$ យើងមាន $<a>x-\\sin x\\ge <a>x-1$ ។", a=c(a)), T("ហើយ $<a>x-1\\to+\\infty$ កាលណា $x\\to+\\infty$ ។ ដូច្នេះអង្គឆ្វេងក៏ខិតជិត $+\\infty$ ។", a=c(a))]
        ex = [(f"limit({a}*x-1,x,oo)", "oo", "lower bound")]; p, v = "oo", oo
    return P(fx, p, v, st, "comparison_infinite_limit", "medium", e, extra=ex, nolim=(k in (0, 2)))

# ---------------- exponentials -----------------
def f_exp(r):
    a, b = r.sample(range(1, 10), 2); k = r.randint(0, 4); A, B = c(a) + "x", c(b) + "x"
    if k == 0:
        fx = T(r"\frac{e^{<A>}-1}{<B>}", A=A, B=B); e = f"(exp({a}*x)-1)/({b}*x)"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{<a>}{<b>}\cdot\frac{e^{<A>}-1}{<A>}", fx=fx, a=a, b=b, A=A)), f"{cite(r,EXPF)} ។"]; d = "easy"
    elif k == 1:
        fx = T(r"\frac{e^{<A>}-1}{e^{<B>}-1}", A=A, B=B); e = f"(exp({a}*x)-1)/(exp({b}*x)-1)"; v = Q(a, b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x$ ៖", D(T(r"<fx>=\frac{\frac{e^{<A>}-1}{x}}{\frac{e^{<B>}-1}{x}}", fx=fx, A=A, B=B)),
              T("ភាគយកខិតជិត $<a>$ ហើយភាគបែងខិតជិត $<b>$ ។", a=a, b=b)]; d = "medium"
    elif k == 2:
        fn = r.choice(["sin", "tan"])
        fx = T(r"\frac{e^{<A>}-1}{\<f> <B>}", A=A, B=B, f=fn); e = f"(exp({a}*x)-1)/{fn}({b}*x)"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{e^{<A>}-1}{<A>}\cdot\frac{<B>}{\<f> <B>}\cdot\frac{<a>}{<b>}", fx=fx, A=A, B=B, a=a, b=b, f=fn)),
              "កត្តាពីរដំបូងខិតជិត $1$ កាលណា $x\\to 0$ ។"]; d = "medium"
    elif k == 3:
        fx = T(r"\frac{e^{<A>}-1}{\ln(1+<B>)}", A=A, B=B); e = f"(exp({a}*x)-1)/log(1+{b}*x)"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{e^{<A>}-1}{<A>}\cdot\frac{<B>}{\ln(1+<B>)}\cdot\frac{<a>}{<b>}", fx=fx, A=A, B=B, a=a, b=b)),
              "ដោយ $" + EXPF + "$ និង $" + LNF + "$ ។"]; d = "medium"
    else:
        fx = T(r"\frac{e^{<A>}-e^{<B>}}{x}", A=A, B=B); e = f"(exp({a}*x)-exp({b}*x))/x"; v = a - b
        st = ["បូក និងដក $1$ នៅភាគយក ៖", D(T(r"<fx>=\frac{e^{<A>}-1}{x}-\frac{e^{<B>}-1}{x}", fx=fx, A=A, B=B)), T("គេបាន $<a>-<b>$ ។", a=a, b=b)]; d = "medium"
    return P(fx, 0, v, [opener(r, "0")] + st, "exponential_standard", d, e, hint=EXPF)

def f_expshift(r):
    a = r.randint(1, 5); b = r.randint(2, 4); k = r.randint(0, 2)
    if k == 0:
        fx = T(r"\frac{e^{x}-e^{<a>}}{x-<a>}", a=a).replace("e^{1}", "e"); e = f"(exp(x)-exp({a}))/(x-{a})"; v = EXP(a)
        ea = L(v)
        st = [T("តាង $t=x-<a>$ ។ បើ $x\\to <a>$ នោះ $t\\to 0$ ។", a=a),
              D(T(r"\lim_{x\to <a>}<fx>=\lim_{t\to 0}\frac{e^{t+<a>}-<ea>}{t}=<ea>\lim_{t\to 0}\frac{e^{t}-1}{t}", a=a, fx=fx, ea=ea))]
    elif k == 1:
        fx = T(r"\frac{e^{x-<a>}-1}{x^{2}-<aa>}", a=a, aa=a * a); e = f"(exp(x-{a})-1)/(x**2-{a*a})"; v = Q(1, 2 * a)
        st = [T("តាង $t=x-<a>$ ដូច្នេះ $x^{2}-<aa>=t(t+<a2>)$ ។", a=a, aa=a * a, a2=2 * a),
              D(T(r"\lim_{t\to 0}\frac{e^{t}-1}{t(t+<a2>)}=\lim_{t\to 0}\frac{e^{t}-1}{t}\cdot\frac{1}{t+<a2>}", a2=2 * a))]
    else:
        fx = T(r"\frac{e^{<b>x}-e^{<ab>}}{x-<a>}", b=b, a=a, ab=a * b); e = f"(exp({b}*x)-exp({a*b}))/(x-{a})"; v = b * EXP(a * b)
        ea = L(EXP(a * b))
        st = [T("ដាក់ $<ea>$ ជាកត្តារួម ៖", ea=ea), D(T(r"<fx>=<ea>\cdot\frac{e^{<b>(x-<a>)}-1}{x-<a>}", fx=fx, ea=ea, b=b, a=a)),
              T("តាង $t=x-<a>$ កាលណា $x\\to <a>$ គេបាន $\\frac{e^{<b>t}-1}{t}\\to <b>$ ។", a=a, b=b)]
    return P(fx, a, v, [opener(r, str(a))] + st, "exponential_shift", "medium", e)

# ---------------- logarithms -----------------
def f_ln(r):
    a, b = r.sample(range(1, 10), 2); k = r.randint(0, 5); A, B = c(a) + "x", c(b) + "x"
    if k == 0:
        fx = T(r"\frac{\ln(1+<A>)}{<B>}", A=A, B=B); e = f"log(1+{a}*x)/({b}*x)"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{<a>}{<b>}\cdot\frac{\ln(1+<A>)}{<A>}", fx=fx, a=a, b=b, A=A)), f"{cite(r,LNF)} ។"]; d = "easy"
    elif k == 1:
        fx = T(r"\frac{\ln(1+<A>)}{\ln(1+<B>)}", A=A, B=B); e = f"log(1+{a}*x)/log(1+{b}*x)"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{\ln(1+<A>)}{<A>}\cdot\frac{<B>}{\ln(1+<B>)}\cdot\frac{<a>}{<b>}", fx=fx, A=A, B=B, a=a, b=b)), "ផលគុណនៃកត្តាពីរដំបូងខិតជិត $1$ ។"]; d = "medium"
    elif k == 2:
        fn = r.choice(["sin", "tan"])
        fx = T(r"\frac{\ln(1+<A>)}{\<f> <B>}", A=A, B=B, f=fn); e = f"log(1+{a}*x)/{fn}({b}*x)"; v = Q(a, b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x$ ។ កាលណា $x\\to 0$ ៖", D(T(r"\frac{\ln(1+<A>)}{x}\to <a>,\qquad\frac{\<f> <B>}{x}\to <b>", A=A, B=B, a=a, b=b, f=fn))]; d = "medium"
    elif k == 3:
        n = r.choice([2, 3])
        fx = T(r"\frac{\ln\left(1+<a>x^{<n>}\right)}{<b>x^{<n>}}", a=c(a), n=n, b=c(b)); e = f"log(1+{a}*x**{n})/({b}*x**{n})"; v = Q(a, b)
        st = [T("តាង $u=<a>x^{<n>}$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", a=c(a), n=n), D(T(r"<fx>=\frac{<a>}{<b>}\cdot\frac{\ln(1+u)}{u}", fx=fx, a=a, b=b))]; d = "medium"
    elif k == 4:
        fx = T(r"\frac{\ln\left(1+<a>x^{2}\right)}{x\sin <B>}", a=c(a), B=B); e = f"log(1+{a}*x**2)/(x*sin({b}*x))"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{\ln\left(1+<a>x^{2}\right)}{<a>x^{2}}\cdot <a>\cdot\frac{x}{\sin <B>}", fx=fx, a=c(a), B=B)),
              T("កត្តាទីមួយខិតជិត $1$ ហើយកត្តាចុងក្រោយខិតជិត $\\frac{1}{<b>}$ ។", b=b)]; d = "hard"
    else:
        fx = T(r"\frac{\ln\left(1+<a>x^{2}\right)}{1-\cos <B>}", a=c(a), B=B); e = f"log(1+{a}*x**2)/(1-cos({b}*x))"; v = Q(2 * a, b * b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x^{2}$ ៖", D(T(r"\frac{\ln\left(1+<a>x^{2}\right)}{x^{2}}\to <aa>,\qquad\frac{1-\cos <B>}{x^{2}}\to\frac{<bb>}{2}", a=c(a), aa=a, B=B, bb=b * b)),
              T("លីមីតគឺ $<a>\\cdot\\frac{2}{<bb>}$ ។", a=a, bb=b * b)]; d = "hard"
    return P(fx, 0, v, [opener(r, "0")] + st, "logarithm_standard", d, e, hint=LNF)

def f_lnshift(r):
    a = r.randint(2, 7); k = r.randint(0, 5)
    tl = "តាង $t=x-1$ ។ បើ $x\\to 1$ នោះ $t\\to 0$ ។"
    if k == 0:
        fx = T(r"\frac{\ln x}{<a>x-<a>}", a=a); e = f"log(x)/({a}*x-{a})"; v = Q(1, a); p = 1
        st = [tl, D(T(r"\lim_{t\to 0}\frac{\ln(1+t)}{<a>t}=\frac{1}{<a>}", a=a))]
    elif k == 1:
        fx = r"\frac{\ln x}{x^{2}-1}"; fx = T(r"\frac{\ln x}{x^{<a>}-1}", a=a if a < 5 else 2); n = a if a < 5 else 2; e = f"log(x)/(x**{n}-1)"; v = Q(1, n); p = 1
        fac = {2: r"(x-1)(x+1)", 3: r"(x-1)\left(x^{2}+x+1\right)", 4: r"(x-1)(x+1)\left(x^{2}+1\right)"}[n]
        rest = {2: "x+1", 3: "x^{2}+x+1", 4: r"(x+1)\left(x^{2}+1\right)"}[n]
        st = [T("ដាក់ភាគបែងជាកត្តា $x^{<n>}-1=<fac>$ ។", n=n, fac=fac),
              D(T(r"<fx>=\frac{\ln x}{x-1}\cdot\frac{1}{<rest>}", fx=fx, rest=rest)), tl + T(" គេបាន $\\frac{\\ln x}{x-1}=\\frac{\\ln(1+t)}{t}\\to 1$ ហើយកត្តាទីពីរខិតជិត $\\frac{1}{<n>}$ ។", n=n)]
    elif k == 2:
        fx = r"\frac{\ln x}{\sqrt{x}-1}"; e = "log(x)/(sqrt(x)-1)"; v = 2; p = 1
        st = ["គុណភាគយក និងភាគបែងនឹង $\\sqrt{x}+1$ ៖", D(r"\frac{\ln x}{\sqrt{x}-1}=\frac{\ln x}{x-1}\left(\sqrt{x}+1\right)"), tl + " ដោយ $\\frac{\\ln(1+t)}{t}\\to 1$ ហើយ $\\sqrt{x}+1\\to 2$ ។"]
    elif k == 3:
        fx = T(r"\frac{\ln(<a>x-<a1>)}{x-1}", a=a, a1=a - 1); e = f"log({a}*x-{a-1})/(x-1)"; v = a; p = 1
        st = [tl, D(T(r"<a>x-<a1>=<a>(t+1)-<a1>=1+<a>t", a=a, a1=a - 1)), D(T(r"\lim_{t\to 0}\frac{\ln(1+<a>t)}{t}=<a>\lim_{t\to 0}\frac{\ln(1+<a>t)}{<a>t}", a=a))]
    elif k == 4:
        fx = T(r"\frac{\ln x-\ln <a>}{x-<a>}", a=a); e = f"(log(x)-log({a}))/(x-{a})"; v = Q(1, a); p = a
        st = [T("តាង $t=x-<a>$ ដូច្នេះ $\\ln x-\\ln <a>=\\ln\\frac{t+<a>}{<a>}=\\ln\\left(1+\\frac{t}{<a>}\\right)$ ។", a=a),
              D(T(r"\lim_{t\to 0}\frac{\ln\left(1+\frac{t}{<a>}\right)}{t}=\frac{1}{<a>}\lim_{t\to 0}\frac{\ln\left(1+\frac{t}{<a>}\right)}{\frac{t}{<a>}}", a=a))]
    else:
        fx = r"\frac{\ln x-1}{x-e}"; e = "(log(x)-1)/(x-E)"; v = 1 / EE; p = "E"
        st = ["តាង $t=x-e$ ។ បើ $x\\to e$ នោះ $t\\to 0$ ។", D(r"\ln x-1=\ln x-\ln e=\ln\frac{t+e}{e}=\ln\left(1+\frac{t}{e}\right)"),
              D(r"\lim_{t\to 0}\frac{\ln\left(1+\frac{t}{e}\right)}{t}=\frac{1}{e}\lim_{t\to 0}\frac{\ln\left(1+\frac{t}{e}\right)}{\frac{t}{e}}")]
    return P(fx, p, v, st, "logarithm_shift", "medium", e, hint=LNF)

def f_mix(r):
    a, b = r.sample(range(1, 8), 2); k = r.randint(0, 6); A, B = c(a) + "x", c(b) + "x"
    if k == 0:
        fx = T(r"\frac{e^{\sin <A>}-1}{x}", A=A); e = f"(exp(sin({a}*x))-1)/x"; v = a
        st = [D(T(r"<fx>=\frac{e^{\sin <A>}-1}{\sin <A>}\cdot\frac{\sin <A>}{x}", fx=fx, A=A)), T("តាង $u=\\sin <A>$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ដូច្នេះកត្តាទីមួយខិតជិត $1$ ហើយកត្តាទីពីរខិតជិត $<a>$ ។", A=A, a=a)]
    elif k == 1:
        fx = T(r"\frac{\ln(1+\sin <A>)}{x}", A=A); e = f"log(1+sin({a}*x))/x"; v = a
        st = [D(T(r"<fx>=\frac{\ln(1+\sin <A>)}{\sin <A>}\cdot\frac{\sin <A>}{x}", fx=fx, A=A)), T("ដោយ $\\sin <A>\\to 0$ កាលណា $x\\to 0$ កត្តាទីមួយខិតជិត $1$ ។ កត្តាទីពីរខិតជិត $<a>$ ។", A=A, a=a)]
    elif k == 2:
        fx = T(r"\frac{\ln(1+\tan <A>)}{\sin <B>}", A=A, B=B); e = f"log(1+tan({a}*x))/sin({b}*x)"; v = Q(a, b)
        st = [D(T(r"<fx>=\frac{\ln(1+\tan <A>)}{\tan <A>}\cdot\frac{\tan <A>}{x}\cdot\frac{x}{\sin <B>}", fx=fx, A=A, B=B)), T("កត្តាទាំងបីខិតជិត $1$ , $<a>$ និង $<q>$ រៀងគ្នា ។", a=a, q=L(Q(1, b)))]
    elif k == 3:
        fx = T(r"\frac{e^{x^{2}}-\cos <A>}{x^{2}}", A=A); e = f"(exp(x**2)-cos({a}*x))/x**2"; v = 1 + Q(a * a, 2)
        st = ["បូក និងដក $1$ នៅភាគយក ៖", D(T(r"<fx>=\frac{e^{x^{2}}-1}{x^{2}}+\frac{1-\cos <A>}{x^{2}}", fx=fx, A=A)), T("តួទីមួយខិតជិត $1$ ហើយតួទីពីរខិតជិត $\\frac{<aa>}{2}$ ។", aa=a * a)]
    elif k == 4:
        fx = T(r"\frac{e^{<A>}-\cos <B>}{x}", A=A, B=B); e = f"(exp({a}*x)-cos({b}*x))/x"; v = a
        st = [D(T(r"<fx>=\frac{e^{<A>}-1}{x}+\frac{1-\cos <B>}{x}", fx=fx, A=A, B=B)), T("ដោយ $\\frac{1-\\cos <B>}{x}=x\\cdot\\frac{1-\\cos <B>}{x^{2}}\\to 0\\cdot\\frac{<bb>}{2}=0$ ។", B=B, bb=b * b)]
    elif k == 5:
        fx = T(r"\frac{\ln(\cos <A>)}{x^{2}}", A=A); e = f"log(cos({a}*x))/x**2"; v = -Q(a * a, 2)
        st = [T("តាង $u=\\cos <A>-1$ ។ កាលណា $x\\to 0$ គេមាន $u\\to 0$ ។", A=A), D(T(r"<fx>=\frac{\ln(1+u)}{u}\cdot\frac{\cos <A>-1}{x^{2}}", fx=fx, A=A)),
              T("កត្តាទីមួយខិតជិត $1$ ហើយកត្តាទីពីរខិតជិត $-\\frac{<aa>}{2}$ ។", aa=a * a)]
    else:
        fx = T(r"\frac{\ln(\cos <A>)}{\ln(\cos <B>)}", A=A, B=B); e = f"log(cos({a}*x))/log(cos({b}*x))"; v = Q(a * a, b * b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x^{2}$ ។ យើងដឹងថា $\\frac{\\ln(\\cos kx)}{x^{2}}\\to-\\frac{k^{2}}{2}$ ព្រោះ ៖",
              D(r"\frac{\ln(\cos kx)}{x^{2}}=\frac{\ln\left(1+(\cos kx-1)\right)}{\cos kx-1}\cdot\frac{\cos kx-1}{x^{2}}"),
              T("ដូច្នេះលីមីតស្មើ $\\frac{-\\frac{<aa>}{2}}{-\\frac{<bb>}{2}}$ ។", aa=a * a, bb=b * b)]
    return P(fx, 0, v, [opener(r, "0")] + st, "mixed_trig_exp_log", "hard", e)

def f_growth(r):
    a = r.randint(1, 4); n = r.randint(2, 4); k = r.randint(0, 6)
    if k == 0:
        fx = T(r"\frac{e^{x}}{x^{<n>}}", n=n); e = f"exp(x)/x**{n}"; p, v = "oo", oo
        st = [T("តាង $t=\\frac{x}{<n>}$ ។ បើ $x\\to+\\infty$ នោះ $t\\to+\\infty$ ហើយ ៖", n=n),
              D(T(r"\frac{e^{x}}{x^{<n>}}=\frac{\left(e^{t}\right)^{<n>}}{(<n>t)^{<n>}}=\frac{1}{<nn>}\left(\frac{e^{t}}{t}\right)^{<n>}", n=n, nn=n ** n)), f"ដោយ ${GROW}$ ។"]
        h = GROW
    elif k == 1:
        fx = T(r"x^{<n>}e^{-x}", n=n); e = f"x**{n}*exp(-x)"; p, v = "oo", 0
        st = [T("សរសេរ $x^{<n>}e^{-x}=\\frac{x^{<n>}}{e^{x}}$ ។ ដោយ $\\frac{e^{x}}{x^{<n>}}\\to+\\infty$ កាលណា $x\\to+\\infty$ ប្រភាគ $\\frac{x^{<n>}}{e^{x}}$ ខិតជិត $0$ ។", n=n)]
        h = GROW
    elif k == 2:
        fx = T(r"\frac{\ln x}{x^{<n>}}", n=n); e = f"log(x)/x**{n}"; p, v = "oo", 0
        st = [D(T(r"\frac{\ln x}{x^{<n>}}=\frac{\ln x}{x}\cdot\frac{1}{x^{<n1>}}", n=n, n1=n - 1)), f"ដោយ ${LNX}$ ហើយកត្តាទីពីរក៏ខិតជិត $0$ ដែរ ។"]; h = LNX
    elif k == 3:
        fx = T(r"x^{<n>}\ln x", n=n); e = f"x**{n}*log(x)"; p, v, sd = 0, 0, "+"
        st = [D(T(r"x^{<n>}\ln x=x^{<n1>}\cdot x\ln x", n=n, n1=n - 1)), f"ដោយ ${XLN}$ ហើយ ${px(n-1)}\\to 0$ ។"]
        return P(fx, p, v, st, "growth_comparison", "medium", e, side="+", hint=XLN)
    elif k == 4:
        fx = r"\sqrt{x}\ln x"; e = "sqrt(x)*log(x)"
        st = ["តាង $t=\\sqrt{x}\\Rightarrow x=t^{2}$ ។ បើ $x\\to 0^{+}$ នោះ $t\\to 0^{+}$ ។", D(r"\sqrt{x}\ln x=t\ln t^{2}=2t\ln t"), "ដោយ $\\lim_{t\\to 0^{+}}t\\ln t=0$ ។"]
        return P(fx, 0, 0, st, "growth_comparison", "medium", e, side="+")
    elif k == 5:
        fx = T(r"x^{<n>}e^{<a>x}", n=n, a=c(a)); e = f"x**{n}*exp({a}*x)"; p, v = "-oo", 0
        st = [T("តាង $t=-x$ ។ បើ $x\\to-\\infty$ នោះ $t\\to+\\infty$ ។", a=a),
              D(T(r"x^{<n>}e^{<a>x}=(-t)^{<n>}e^{-<a>t}=<s>\frac{t^{<n>}}{e^{<a>t}}", n=n, a=c(a), s="" if n % 2 == 0 else "-")),
              "ដោយអ៊ិចស្ប៉ូណង់ស្យែលកើនលឿនជាងស្វ័យគុណនៃ $t$ ប្រភាគនេះខិតជិត $0$ ។"]
        h = XEX
    else:
        fx = r"\frac{(\ln x)^{2}}{x}"; e = "log(x)**2/x"; p, v = "oo", 0
        st = ["តាង $t=\\ln x\\Rightarrow x=e^{t}$ ។ បើ $x\\to+\\infty$ នោះ $t\\to+\\infty$ ។", D(r"\frac{(\ln x)^{2}}{x}=\frac{t^{2}}{e^{t}}"), "ប្រភាគនេះខិតជិត $0$ ព្រោះ $\\frac{e^{t}}{t^{2}}\\to+\\infty$ ។"]; h = GROW
    return P(fx, p, v, st, "growth_comparison", "medium", e, hint=h)

def f_growth2(r):
    a, b = r.randint(1, 5), r.randint(1, 5); n = r.randint(1, 3); k = r.randint(0, 4)
    if k == 0:
        fx = T(r"<a>x-\ln x", a=c(a)); e = f"{a}*x-log(x)"; p, v = "oo", oo
        st = [T("មានរាងមិនកំណត់ $\\infty-\\infty$ ។ ដាក់ $x$ ជាកត្តារួម ៖", a=a), D(T(r"<a>x-\ln x=x\left(<b>-\frac{\ln x}{x}\right)", a=c(a), b=a)), f"ដោយ ${LNX}$ វង់ក្រចកខិតជិត ${a}$ ដូច្នេះផលគុណខិតជិត $+\\infty$ ។"]
    elif k == 1:
        fx = T(r"e^{x}-<a>x", a=c(a)); e = f"exp(x)-{a}*x"; p, v = "oo", oo
        st = ["មានរាងមិនកំណត់ $\\infty-\\infty$ ។ ដាក់ $x$ ជាកត្តារួម ៖", D(T(r"e^{x}-<a>x=x\left(\frac{e^{x}}{x}-<b>\right)", a=c(a), b=a)), f"ដោយ ${GROW}$ វង់ក្រចកខិតជិត $+\\infty$ ។"]
    elif k == 2:
        fx = T(r"\ln x-<a>x^{<n>}", a=c(a), n=n + 1); e = f"log(x)-{a}*x**{n+1}"; p, v = "oo", -oo
        st = [D(T(r"\ln x-<a>x^{<n>}=x^{<n>}\left(\frac{\ln x}{x^{<n>}}-<b>\right)", a=c(a), b=a, n=n + 1)), T("វង់ក្រចកខិតជិត $-<a>$ ហើយ $x^{<n>}\\to+\\infty$ ។", a=a, n=n + 1)]
    elif k == 3:
        fx = T(r"\frac{<a>}{x}+\ln x", a=c(a) if a != 1 else "1"); e = f"{a}/x+log(x)"
        st = ["មានរាងមិនកំណត់ $\\infty-\\infty$ ។ ធ្វើជាប្រភាគតែមួយ ៖", D(T(r"\frac{<a>}{x}+\ln x=\frac{<a>+x\ln x}{x}", a=a)), f"ដោយ ${XLN}$ ភាគយកខិតជិត ${a}$ ហើយភាគបែងខិតជិត $0^{{+}}$ ។"]
        return P(fx, 0, oo, st, "growth_comparison_differences", "hard", e, side="+")
    else:
        fx = T(r"x-e^{<a>x}", a=c(a)); e = f"x-exp({a}*x)"; p, v = "-oo", -oo
        st = [T("កាលណា $x\\to-\\infty$ គេមាន $<a>x\\to-\\infty$ ដូច្នេះ $e^{<a>x}\\to 0$ ។ ", a=c(a)), "តួ $x$ ខិតជិត $-\\infty$ ហើយគ្មានរាងមិនកំណត់ទេ ។"]
    return P(fx, p, v, st, "growth_comparison_differences", "medium", e)

def f_ratioexp(r):
    a, b, d, g = r.randint(1, 7), r.randint(1, 7), r.randint(1, 7), r.randint(1, 7); k = r.randint(0, 4)
    if k == 0:
        fx = T(r"\frac{<a>e^{x}+<b>}{<d>e^{x}+<g>}", a=c(a), b=b, d=c(d), g=g); e = f"({a}*exp(x)+{b})/({d}*exp(x)+{g})"; v = Q(a, d); p = "oo"
        st = ["ចែកភាគយក និងភាគបែងនឹង $e^{x}$ ៖", D(T(r"<fx>=\frac{<a>+<b>e^{-x}}{<d>+<g>e^{-x}}", fx=fx, a=a, b=c(b), d=d, g=c(g))), "ដោយ $e^{-x}\\to 0$ កាលណា $x\\to+\\infty$ ។"]
    elif k == 1:
        fx = T(r"\frac{<a>e^{x}+<b>}{<d>e^{x}+<g>}", a=c(a), b=b, d=c(d), g=g); e = f"({a}*exp(x)+{b})/({d}*exp(x)+{g})"; v = Q(b, g); p = "-oo"
        st = ["កាលណា $x\\to-\\infty$ គេមាន $e^{x}\\to 0$ ។ លីមីតនេះមិនមែនរាងមិនកំណត់ទេ ។", T("ជំនួសដោយផ្ទាល់ គេបានផលធៀប $\\frac{<b>}{<g>}$ ។", b=b, g=g)]
    elif k == 2:
        fx = T(r"\frac{e^{<a>x}-e^{-<a>x}}{e^{<a>x}+e^{-<a>x}}", a=c(a)); e = f"(exp({a}*x)-exp(-{a}*x))/(exp({a}*x)+exp(-{a}*x))"; p = r.choice(["oo", "-oo"]); v = 1 if p == "oo" else -1
        st = [("ចែកភាគយក និងភាគបែងនឹង $e^{" + c(a) + "x}$ ៖" if p == "oo" else "ចែកភាគយក និងភាគបែងនឹង $e^{-" + c(a) + "x}$ ៖"),
              D(T(r"<fx>=\frac{1-e^{-<a2>x}}{1+e^{-<a2>x}}", fx=fx, a2=c(2 * a)) if p == "oo" else T(r"<fx>=\frac{e^{<a2>x}-1}{e^{<a2>x}+1}", fx=fx, a2=c(2 * a))),
              ("ដោយ $e^{-" + c(2 * a) + "x}\\to 0$ ។" if p == "oo" else "ដោយ $e^{" + c(2 * a) + "x}\\to 0$ កាលណា $x\\to-\\infty$ ។")]
    elif k == 3:
        fx = T(r"\frac{<a>e^{x}+x}{<d>e^{x}+x^{2}}", a=c(a), d=c(d)); e = f"({a}*exp(x)+x)/({d}*exp(x)+x**2)"; v = Q(a, d); p = "oo"
        st = ["ចែកភាគយក និងភាគបែងនឹង $e^{x}$ ៖", D(T(r"<fx>=\frac{<a>+\frac{x}{e^{x}}}{<d>+\frac{x^{2}}{e^{x}}}", fx=fx, a=a, d=d)), "ដោយ $\\frac{x}{e^{x}}\\to 0$ និង $\\frac{x^{2}}{e^{x}}\\to 0$ កាលណា $x\\to+\\infty$ ។"]
    else:
        fx = T(r"\frac{<a>x+<b>}{e^{x}+<g>}", a=c(a), b=b, g=g); e = f"({a}*x+{b})/(exp(x)+{g})"; v = 0; p = "oo"
        st = [D(T(r"<fx>=\frac{x\left(<a>+\frac{<b>}{x}\right)}{e^{x}\left(1+<g>e^{-x}\right)}=\frac{x}{e^{x}}\cdot\frac{<a>+\frac{<b>}{x}}{1+<g>e^{-x}}", fx=fx, a=a, b=b, g=c(g))), T("កត្តាទីមួយខិតជិត $0$ ហើយកត្តាទីពីរខិតជិត $<a>$ ។", a=a)]
    return P(fx, p, v, st, "exponential_at_infinity", "medium", e)

def f_lninf(r):
    a, b, d, g = r.randint(1, 7), r.randint(1, 7), r.randint(1, 7), r.randint(1, 7); k = r.randint(0, 5)
    if k <= 1:
        side = "+" if k else ""; p = 0 if k else "oo"
        fx = T(r"\frac{<a>\ln x+<b>}{<d>\ln x+<g>}", a=c(a), b=b, d=c(d), g=g); e = f"({a}*log(x)+{b})/({d}*log(x)+{g})"; v = Q(a, d)
        st = ["តាង $t=\\ln x$ ។ " + ("បើ $x\\to 0^{+}$ នោះ $t\\to-\\infty$ ។" if k else "បើ $x\\to+\\infty$ នោះ $t\\to+\\infty$ ។"),
              D(T(r"\frac{<a>t+<b>}{<d>t+<g>}=\frac{<A>+\frac{<b>}{t}}{<D>+\frac{<g>}{t}}", a=c(a), b=b, d=c(d), g=g, A=a, D=d)), "ដោយ $\\frac{1}{t}\\to 0$ ។"]
        return P(fx, p, v, st, "logarithm_at_infinity", "medium", e, side=side)
    if k == 2:
        fx = T(r"\ln(<a>x+<b>)-\ln(<d>x+<g>)", a=c(a), b=b, d=c(d), g=g); e = f"log({a}*x+{b})-log({d}*x+{g})"; v = LOG(Q(a, d))
        st = ["ប្រើ $\\ln p-\\ln q=\\ln\\frac{p}{q}$ ៖", D(T(r"<fx>=\ln\frac{<a>x+<b>}{<d>x+<g>}", fx=fx, a=c(a), b=b, d=c(d), g=g)),
              T("កាលណា $x\\to+\\infty$ ប្រភាគក្នុងលោការីតខិតជិត $<q>$ ហើយ $\\ln$ ជាអនុគមន៍ជាប់ ។", q=L(Q(a, d)))]
    elif k == 3:
        fx = T(r"\ln\left(x^{2}+<a>\right)-2\ln x", a=a); e = f"log(x**2+{a})-2*log(x)"; v = 0
        st = [D(T(r"<fx>=\ln\frac{x^{2}+<a>}{x^{2}}=\ln\left(1+\frac{<a>}{x^{2}}\right)", fx=fx, a=a)), "ដោយ $1+\\frac{" + str(a) + "}{x^{2}}\\to 1$ និង $\\ln 1=0$ ។"]
    elif k == 4:
        fx = T(r"\ln\left(1+e^{<a>x}\right)-<a>x", a=c(a)); e = f"log(1+exp({a}*x))-{a}*x"; v = 0
        st = [T("ដាក់ $e^{<a>x}$ ជាកត្តាក្នុងលោការីត ៖", a=c(a)), D(T(r"\ln\left(1+e^{<a>x}\right)=<a>x+\ln\left(1+e^{-<a>x}\right)", a=c(a))), "ដូច្នេះ កន្សោមស្មើ $\\ln\\left(1+e^{-" + c(a) + "x}\\right)$ ដែលខិតជិត $\\ln 1=0$ ។"]
    else:
        fx = T(r"\frac{\ln(<a>x+<b>)}{\ln x}", a=c(a) if a > 1 else "", b=b); e = f"log({a}*x+{b})/log(x)"; v = 1
        st = [D(T(r"\ln(<a>x+<b>)=\ln x+\ln\left(<A>+\frac{<b>}{x}\right)", a=c(a), A=a, b=b)), D(T(r"<fx>=1+\frac{\ln\left(<A>+\frac{<b>}{x}\right)}{\ln x}", fx=fx, A=a, b=b)), T("ភាគយកនៃតួទីពីរខិតជិត $\\ln <a>$ ហើយភាគបែងខិតជិត $+\\infty$ ។", a=a)]
    return P(fx, "oo", v, st, "logarithm_at_infinity", "medium", e)

def f_xln(r):
    a, b = r.sample(range(1, 8), 2); k = r.randint(0, 3); tl = "តាង $t=\\frac{1}{x}$ ។ បើ $x\\to+\\infty$ នោះ $t\\to 0^{+}$ ។"
    if k == 0:
        fx = T(r"x\ln\left(1+\frac{<a>}{x}\right)", a=a); e = f"x*log(1+{a}/x)"; v = a
        st = [tl, D(T(r"\lim_{t\to 0}\frac{\ln(1+<A>t)}{t}=<a>\lim_{t\to 0}\frac{\ln(1+<A>t)}{<A>t}", A=c(a), a=a))]
    elif k == 1:
        fx = T(r"x\left(e^{\frac{<a>}{x}}-1\right)", a=a); e = f"x*(exp({a}/x)-1)"; v = a
        st = [tl, D(T(r"\lim_{t\to 0}\frac{e^{<A>t}-1}{t}=<a>\lim_{t\to 0}\frac{e^{<A>t}-1}{<A>t}", A=c(a), a=a))]
    elif k == 2:
        fx = T(r"x\ln\frac{x+<a>}{x+<b>}", a=a, b=b); e = f"x*log((x+{a})/(x+{b}))"; v = a - b
        st = ["បំបែកលោការីតជាផលដក ៖", D(T(r"x\ln\frac{x+<a>}{x+<b>}=x\ln\left(1+\frac{<a>}{x}\right)-x\ln\left(1+\frac{<b>}{x}\right)", a=a, b=b)),
              T("ដោយ $x\\ln\\left(1+\\frac{k}{x}\\right)\\to k$ កាលណា $x\\to+\\infty$ គេបាន $<a>-<b>$ ។", a=a, b=b)]
    else:
        fx = T(r"xe^{\frac{<a>}{x}}-x", a=a); e = f"x*exp({a}/x)-x"; v = a
        st = [T("ដាក់ $x$ ជាកត្តារួម ៖ $x\\left(e^{\\frac{<a>}{x}}-1\\right)$ ។", a=a), tl, D(T(r"\lim_{t\to 0}\frac{e^{<A>t}-1}{t}=<a>", A=c(a), a=a))]
    return P(fx, "oo", v, st, "change_of_variable_reciprocal_exp_log", "medium", e)

def f_enum(r):
    a, b = r.randint(1, 6), r.randint(2, 5); g = r.randint(1, 6); k = r.randint(0, 7)
    while g == a: g = r.randint(1, 6)
    if k == 0:
        fx = T(r"\left(1+\frac{<a>}{x}\right)^{<b>x}", a=a, b=b); e = f"(1+{a}/x)**({b}*x)"; p, v = "oo", EXP(a * b)
        st = [T("តាង $t=\\frac{x}{<a>}$ ។ បើ $x\\to+\\infty$ នោះ $t\\to+\\infty$ ហើយ $x=<a>t$ ។", a=a),
              D(T(r"\left(1+\frac{<a>}{x}\right)^{<b>x}=\left(1+\frac{1}{t}\right)^{<ab>t}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{<ab>}", a=a, b=b, ab=a * b)), f"ដោយ ${EF2.replace('x','t')}$ ។"]
    elif k == 1:
        fx = T(r"(1+<a>x)^{\frac{<b>}{x}}", a=c(a), b=b); e = f"(1+{a}*x)**({b}/x)"; p, v = 0, EXP(a * b)
        st = [T("តាង $u=<a>x$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", a=c(a)), D(T(r"(1+<a>x)^{\frac{<b>}{x}}=\left[(1+u)^{\frac{1}{u}}\right]^{<ab>}", a=c(a), b=b, ab=a * b)), f"{cite(r,EF)} ។"]
    elif k == 2:
        fx = T(r"\left(\frac{x+<a>}{x+<g>}\right)^{<b>x}", a=a, g=g, b=c(b)); e = f"((x+{a})/(x+{g}))**({b}*x)"; p, v = "oo", EXP(b * (a - g))
        h = a - g
        st = ["សរសេរប្រភាគជាទម្រង់ $1+\\frac{1}{t}$ ៖", D(T(r"\frac{x+<a>}{x+<g>}=1<sg>\frac{<ah>}{x+<g>}", a=a, g=g, sg="+" if h > 0 else "-", ah=abs(h))),
              T("តាង $t=<sg>\\frac{x+<g>}{<ah>}\\Rightarrow x=<h>t-<g>$ ។ បើ $x\\to+\\infty$ នោះ <dir> ។", g=g, h=c(h), ah=abs(h), sg="" if h > 0 else "-", dir="$t\\to+\\infty$" if h > 0 else "$t\\to-\\infty$"),
              D(T(r"\left(1+\frac{1}{t}\right)^{<b>(<h>t-<g>)}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{<bh>}\cdot\left(1+\frac{1}{t}\right)^{-<bg>}", b=b, h=c(h), g=g, bh=b * h, bg=b * g)),
              T("កត្តាទីមួយខិតជិត $<v>$ ហើយកត្តាទីពីរខិតជិត $1$ ។", v=L(v))]
    elif k == 3:
        fx = T(r"(1+\sin <a>x)^{\frac{<b>}{x}}", a=c(a), b=b if b != 1 else 1); e = f"(1+sin({a}*x))**({b}/x)"; p, v = 0, EXP(a * b)
        st = [T("តាង $u=\\sin <a>x$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", a=c(a)),
              D(T(r"(1+\sin <a>x)^{\frac{<b>}{x}}=\left[(1+u)^{\frac{1}{u}}\right]^{\frac{<b>\sin <a>x}{x}}", a=c(a), b=b)),
              T("តួក្នុងវង់ក្រចកខិតជិត $e$ ហើយនិទស្សន្ត $\\frac{<b>\\sin <A>x}{x}\\to <ab>$ ។", A=c(a), b=b, ab=a * b)]
    elif k == 4:
        fx = T(r"(\cos <a>x)^{\frac{1}{x^{2}}}", a=c(a)); e = f"cos({a}*x)**(1/x**2)"; p, v = 0, EXP(-Q(a * a, 2))
        st = [T("តាង $u=\\cos <a>x-1$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", a=c(a)), D(T(r"(\cos <a>x)^{\frac{1}{x^{2}}}=\left[(1+u)^{\frac{1}{u}}\right]^{\frac{\cos <a>x-1}{x^{2}}}", a=c(a))),
              T("និទស្សន្តខិតជិត $-\\frac{<aa>}{2}$ ។", aa=a * a)]
    elif k == 5:
        fx = T(r"\left(1-\frac{<a>}{x}\right)^{x}", a=a); e = f"(1-{a}/x)**x"; p, v = "oo", EXP(-a)
        st = [T("តាង $t=-\\frac{x}{<a>}\\Rightarrow x=-<a>t$ ។ បើ $x\\to+\\infty$ នោះ $t\\to-\\infty$ ។", a=a if a != 1 else ""), D(T(r"\left(1-\frac{<a>}{x}\right)^{x}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{-<a>}", a=a)),
              "ដោយ $\\left(1+\\frac{1}{t}\\right)^{t}\\to e$ កាលណា $t\\to-\\infty$ ដែរ ។"]
    elif k == 6:
        fx = T(r"\left(1+<a>x^{2}\right)^{\frac{1}{x^{2}}}", a=c(a)); e = f"(1+{a}*x**2)**(1/x**2)"; p, v = 0, EXP(a)
        st = [T("តាង $u=<a>x^{2}$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", a=c(a)), D(T(r"\left(1+<a>x^{2}\right)^{\frac{1}{x^{2}}}=\left[(1+u)^{\frac{1}{u}}\right]^{<b>}", a=c(a), b=a))]
    else:
        fx = T(r"\left(\frac{<b>x+1}{<b>x-1}\right)^{x}", b=b); e = f"(({b}*x+1)/({b}*x-1))**x"; p, v = "oo", EXP(Q(2, b))
        st = [D(T(r"\frac{<b>x+1}{<b>x-1}=1+\frac{2}{<b>x-1}", b=b)), T("តាង $t=\\frac{<b>x-1}{2}\\Rightarrow x=\\frac{2t+1}{<b>}$ ។", b=b),
              D(T(r"\left(1+\frac{1}{t}\right)^{\frac{2t+1}{<b>}}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{\frac{2}{<b>}}\cdot\left(1+\frac{1}{t}\right)^{\frac{1}{<b>}}", b=b)), T("កត្តាទីមួយខិតជិត $e^{\\frac{2}{<b>}}$ ហើយកត្តាទីពីរខិតជិត $1$ ។", b=b)]
    return P(fx, p, v, st, "number_e", "hard" if k in (2, 3, 4, 7) else "medium", e, hint=EF2 if p == "oo" else EF)

def f_ax(r):
    a, b = r.sample([2, 3, 5, 7, 10], 2); k = r.randint(0, 3); d = r.randint(2, 6)
    if k == 0:
        fx = T(r"\frac{<a>^{x}-1}{x}", a=a); e = f"({a}**x-1)/x"; v = LOG(a)
        st = [T("សរសេរ $<a>^{x}=e^{x\\ln <a>}$ ។ តាង $u=x\\ln <a>$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", a=a), D(T(r"\frac{<a>^{x}-1}{x}=\ln <a>\cdot\frac{e^{u}-1}{u}", a=a))]
    elif k == 1:
        fx = T(r"\frac{<a>^{x}-<b>^{x}}{x}", a=a, b=b); e = f"({a}**x-{b}**x)/x"; v = LOG(a) - LOG(b)
        st = ["បូក និងដក $1$ នៅភាគយក ៖", D(T(r"<fx>=\frac{<a>^{x}-1}{x}-\frac{<b>^{x}-1}{x}", fx=fx, a=a, b=b)), T("ដោយ $\\frac{k^{x}-1}{x}\\to\\ln k$ គេបាន $\\ln <a>-\\ln <b>$ ។", a=a, b=b)]
    elif k == 2:
        fx = T(r"\frac{<a>^{x}-1}{<b>^{x}-1}", a=a, b=b); e = f"({a}**x-1)/({b}**x-1)"; v = LOG(a) / LOG(b)
        st = ["ចែកភាគយក និងភាគបែងនឹង $x$ ៖", D(T(r"<fx>=\frac{\frac{<a>^{x}-1}{x}}{\frac{<b>^{x}-1}{x}}", fx=fx, a=a, b=b)), T("ភាគយកខិតជិត $\\ln <a>$ ហើយភាគបែងខិតជិត $\\ln <b>$ ។", a=a, b=b)]
    else:
        fx = T(r"\frac{<a>^{x}-1}{\sin <d>x}", a=a, d=d); e = f"({a}**x-1)/sin({d}*x)"; v = LOG(a) / d
        st = [D(T(r"<fx>=\frac{<a>^{x}-1}{x}\cdot\frac{x}{\sin <d>x}", fx=fx, a=a, d=d)), T("កត្តាទាំងពីរខិតជិត $\\ln <a>$ និង $\\frac{1}{<d>}$ ។", a=a, d=d)]
    return P(fx, 0, v, [opener(r, "0")] + st, "exponential_base_a", "medium", e)

def f_side(r):
    a = r.randint(1, 6); k = r.randint(0, 5)
    if k == 0:
        fx = T(r"\frac{\sin <a>x}{|x|}", a=c(a)); e = f"sin({a}*x)/Abs(x)"
        st = ["ព្រោះមាន $|x|$ យើងត្រូវរកលីមីតឆ្វេង និងលីមីតស្តាំដាច់ពីគ្នា ។",
              T("បើ $x>0$ នោះ $|x|=x$ ៖ $$\\lim_{x\\to 0^{+}}\\frac{\\sin <A>x}{x}=<a>$$", A=c(a), a=a),
              T("បើ $x<0$ នោះ $|x|=-x$ ៖ $$\\lim_{x\\to 0^{-}}\\frac{\\sin <A>x}{-x}=-<a>$$", A=c(a), a=a)]
        l, rr = -a, a
    elif k == 1:
        fx = T(r"\frac{\sqrt{1-\cos <d>x}}{x}", d=c(2 * a)); e = f"sqrt(1-cos({2*a}*x))/x"
        st = [T("ប្រើ $1-\\cos <d>x=2\\sin^{2}<A>x$ ដូច្នេះ $\\sqrt{1-\\cos <d>x}=\\sqrt{2}\\,|\\sin <A>x|$ ។", d=c(2 * a), A=c(a)),
              T("បើ $x>0$ ជិត $0$ នោះ $\\sin <A>x>0$ ៖ $$\\lim_{x\\to 0^{+}}\\frac{\\sqrt{2}\\sin <A>x}{x}=<a>\\sqrt{2}$$", A=c(a), a=c(a)),
              T("បើ $x<0$ ជិត $0$ នោះ $\\sin <A>x<0$ ៖ $$\\lim_{x\\to 0^{-}}\\frac{-\\sqrt{2}\\sin <A>x}{x}=-<a>\\sqrt{2}$$", A=c(a), a=c(a))]
        l, rr = -a * SQ(2), a * SQ(2)
    elif k == 2:
        fx = T(r"\frac{1}{1+e^{\frac{<a>}{x}}}", a=a); e = f"1/(1+exp({a}/x))"
        st = [T("កាលណា $x\\to 0^{+}$ គេមាន $\\frac{<a>}{x}\\to+\\infty$ ដូច្នេះ $e^{\\frac{<a>}{x}}\\to+\\infty$ ហើយប្រភាគខិតជិត $0$ ។", a=a),
              T("កាលណា $x\\to 0^{-}$ គេមាន $\\frac{<a>}{x}\\to-\\infty$ ដូច្នេះ $e^{\\frac{<a>}{x}}\\to 0$ ហើយប្រភាគខិតជិត $1$ ។", a=a)]
        l, rr = 1, 0
    elif k == 3:
        fx = T(r"\frac{e^{\frac{<a>}{x}}-1}{e^{\frac{<a>}{x}}+1}", a=a); e = f"(exp({a}/x)-1)/(exp({a}/x)+1)"
        st = [T("កាលណា $x\\to 0^{+}$ តាង $u=e^{\\frac{<a>}{x}}\\to+\\infty$ ៖ $\\frac{u-1}{u+1}=\\frac{1-\\frac{1}{u}}{1+\\frac{1}{u}}\\to 1$ ។", a=a),
              T("កាលណា $x\\to 0^{-}$ គេមាន $e^{\\frac{<a>}{x}}\\to 0$ ដូច្នេះប្រភាគខិតជិត $-1$ ។", a=a)]
        l, rr = -1, 1
    elif k == 4:
        fx = T(r"\frac{|\sin <a>x|}{\tan <a>x}", a=c(a)); e = f"Abs(sin({a}*x))/tan({a}*x)"
        st = [T("កាលណា $x\\to 0^{+}$ គេមាន $\\sin <a>x>0$ ៖ $\\frac{\\sin <a>x}{\\tan <a>x}=\\cos <a>x\\to 1$ ។", a=c(a)),
              T("កាលណា $x\\to 0^{-}$ គេមាន $\\sin <a>x<0$ ៖ $\\frac{-\\sin <a>x}{\\tan <a>x}=-\\cos <a>x\\to-1$ ។", a=c(a))]
        l, rr = -1, 1
    else:
        fx = T(r"\frac{<a>x}{1+e^{\frac{1}{x}}}+\frac{|x|}{x}", a=c(a)); e = f"{a}*x/(1+exp(1/x))+Abs(x)/x"
        st = ["កាលណា $x\\to 0^{+}$ ៖ $\\frac{|x|}{x}=1$ ហើយតួទីមួយខិតជិត $0$ ។ លីមីតស្តាំគឺ $1$ ។", "កាលណា $x\\to 0^{-}$ ៖ $\\frac{|x|}{x}=-1$ ហើយតួទីមួយខិតជិត $\\frac{0}{1+0}=0$ ។ លីមីតឆ្វេងគឺ $-1$ ។"]
        l, rr = -1, 1
    ll, lr = r"\lim_{x\to 0^{-}}" + fx, r"\lim_{x\to 0^{+}}" + fx
    conc = f"ដូចនេះ លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ព្រោះ $\\boxed{{{L(l)}\\neq {L(rr)}}}$ ។ អនុគមន៍នេះគ្មានលីមីតត្រង់ $x=0$ ទេ ។"
    return P(fx, 0, 0, st, "one_sided_no_limit", "medium", e, nolim=True, ans=rf"\lim_{{x\to 0^{{-}}}}f(x)={L(l)},\ \lim_{{x\to 0^{{+}}}}f(x)={L(rr)}", conc=conc,
             extra=[(f"limit({e},x,0,'-')", str(l), "left limit"), (f"limit({e},x,0,'+')", str(rr), "right limit")], setup="side")

def f_side2(r):
    a = r.randint(1, 6); k = r.randint(0, 4)
    if k == 0:
        s = r.choice(["+", "-"]); fx = r"\tan x"; e = "tan(x)"; p = "pi/2"; v = -oo if s == "+" else oo
        st = ["យើងមាន $\\tan x=\\frac{\\sin x}{\\cos x}$ ។ កាលណា $x\\to\\frac{\\pi}{2}$ ភាគយកខិតជិត $1$ ហើយភាគបែងខិតជិត $0$ ។",
              ("ចំពោះ $x$ ធំជាង $\\frac{\\pi}{2}$ បន្តិច គេមាន $\\cos x<0$ ។" if s == "+" else "ចំពោះ $x$ តូចជាង $\\frac{\\pi}{2}$ បន្តិច គេមាន $\\cos x>0$ ។")]
        return P(fx, p, v, st, "one_sided_infinite", "easy", e, side=s)
    if k == 1:
        s = r.choice(["+", "-"]); fx = T(r"e^{\frac{<a>}{x}}", a=a); e = f"exp({a}/x)"; v = oo if s == "+" else 0
        st = [T("កាលណា $x\\to 0^{<s>}$ គេមាន $\\frac{<a>}{x}\\to <inf>$ ។", s=s, a=a, inf=r"+\infty" if s == "+" else r"-\infty"), "ដោយ $e^{u}\\to+\\infty$ កាលណា $u\\to+\\infty$ និង $e^{u}\\to 0$ កាលណា $u\\to-\\infty$ ។"]
        return P(fx, 0, v, st, "one_sided_infinite", "easy", e, side=s)
    if k == 2:
        s = r.choice(["+", "-"]); fx = r"\frac{1}{\ln x}"; e = "1/log(x)"; v = oo if s == "+" else -oo
        st = [f"កាលណា $x\\to 1^{{{s}}}$ គេមាន $\\ln x\\to 0^{{{s}}}$ ព្រោះ $\\ln x" + (">" if s == "+" else "<") + "0$ " + ("ចំពោះ $x>1$ ។" if s == "+" else "ចំពោះ $0<x<1$ ។")]
        return P(fx, 1, v, st, "one_sided_infinite", "easy", e, side=s)
    if k == 3:
        s = r.choice(["+", "-"]); fx = T(r"\frac{<a>}{e^{x}-1}", a=a); e = f"{a}/(exp(x)-1)"; v = oo if s == "+" else -oo
        st = [f"កាលណា $x\\to 0^{{{s}}}$ គេមាន $e^{{x}}\\to 1$ ដោយ " + ("$e^{x}>1$" if s == "+" else "$e^{x}<1$") + f" ដូច្នេះ $e^{{x}}-1\\to 0^{{{s}}}$ ។"]
        return P(fx, 0, v, st, "one_sided_infinite", "easy", e, side=s)
    s = "+"; fx = T(r"\frac{\ln x}{x^{<a>}}", a=a if a > 1 else 1).replace("x^{1}", "x"); e = f"log(x)/x**{a}"; v = -oo
    st = ["កាលណា $x\\to 0^{+}$ គេមាន $\\ln x\\to-\\infty$ ហើយភាគបែងខិតជិត $0^{+}$ ។", "នេះមិនមែនរាងមិនកំណត់ទេ ។ ផលគុណនៃ $\\ln x$ និង $\\frac{1}{" + px(a) + "}$ ខិតជិត $-\\infty$ ។"]
    return P(fx, 0, v, st, "one_sided_infinite", "easy", e, side=s)

def f_direct(r):
    a, b = r.randint(1, 6), r.randint(1, 6); k = r.randint(0, 6)
    if k == 0:
        c0, s_ = r.choice([(PI / 6, 1), (PI / 3, 1), (PI / 4, 1), (PI / 2, 1), (PI, 1)])
        fx = T(r"(<a>\sin x+<b>\cos x)", a=c(a), b=c(b)); e = f"{a}*sin(x)+{b}*cos(x)"; v = sp.nsimplify(a * sp.sin(c0) + b * sp.cos(c0)); p = c0
        st = [f"អនុគមន៍ $\\sin x$ និង $\\cos x$ ជាប់ត្រង់ $x={L(c0)}$ ដូច្នេះជំនួសតម្លៃដោយផ្ទាល់ ។", D(rf"{a}\sin {L(c0)}+{b}\cos {L(c0)}={L(v)}")]
    elif k == 1:
        fx = T(r"\left(x^{2}+<a>\right)e^{x}", a=a); e = f"(x**2+{a})*exp(x)"; v = a; p = 0
        st = ["តាមប្រមាណវិធីលើលីមីត លីមីតនៃផលគុណស្មើផលគុណនៃលីមីត ។", D(T(r"\lim_{x\to 0}\left(x^{2}+<a>\right)\cdot\lim_{x\to 0}e^{x}=<a>\cdot 1", a=a))]
    elif k == 2:
        fx = T(r"\frac{\ln x+<a>}{x}", a=a); e = f"(log(x)+{a})/x"; v = a; p = 1
        st = ["ភាគបែងមិនសូន្យត្រង់ $x=1$ ដូច្នេះជំនួសដោយផ្ទាល់ ។", D(T(r"\frac{\ln 1+<a>}{1}=<a>", a=a))]
    elif k == 3:
        fx = T(r"\frac{\cos x}{<a>+\sin x}", a=a); e = f"cos(x)/({a}+sin(x))"; v = Q(1, a); p = 0
        st = ["ភាគបែងខិតជិត $" + str(a) + "\\neq 0$ ។ តាមប្រមាណវិធីលើលីមីត ៖", D(T(r"\frac{\cos 0}{<a>+\sin 0}=\frac{1}{<a>}", a=a))]
    elif k == 4:
        fx = T(r"\left(e^{x}+<b>x\right)", b=c(b)); e = f"exp(x)+{b}*x"; v = EE + b; p = 1
        st = ["លីមីតនៃផលបូកស្មើផលបូកនៃលីមីត ។", D(T(r"\lim_{x\to 1}e^{x}+\lim_{x\to 1}<b>x=e+<v>", b=c(b), v=b))]
    elif k == 5:
        fx = T(r"\sqrt{<a>+\cos x}", a=a * a + a - 1 if False else a * a - 1); e = f"sqrt({a*a-1}+cos(x))"; v = a; p = 0
        if a == 1:
            fx = r"\sqrt{\cos x}"; e = "sqrt(cos(x))"
        st = [T("កាលណា $x\\to 0$ កន្សោមក្រោមឫសខិតជិត $<q>$ ។", q=a * a), D(T(r"\sqrt{<q>}=<a>", q=a * a, a=a))]
    else:
        fx = T(r"\ln\left(e^{x}+<a>\right)", a=a); e = f"log(exp(x)+{a})"; v = LOG(1 + a); p = 0
        st = [T("កាលណា $x\\to 0$ កន្សោមក្នុងលោការីតខិតជិត $<q>$ ។ ដោយ $\\ln$ ជាប់ ៖", q=1 + a), D(T(r"\ln(1+<a>)=<v>", a=a, v=L(LOG(1 + a))))]
    return P(fx, p, v, st, "direct_substitution_rules", "easy", e, grade=11)

def f_deriv(r):
    k = r.randint(0, 4)
    if k == 0:
        c0 = r.choice([PI / 6, PI / 3, PI / 4]); cl = L(c0)
        fx = rf"\frac{{\sin x-\sin {cl}}}{{x-{cl}}}"; e = f"(sin(x)-sin({c0}))/(x-{c0})"; v = sp.cos(c0); fn = r"\sin x"; dr = r"\cos x"
    elif k == 1:
        c0 = r.choice([PI / 6, PI / 3, PI / 4]); cl = L(c0)
        fx = rf"\frac{{\cos x-\cos {cl}}}{{x-{cl}}}"; e = f"(cos(x)-cos({c0}))/(x-{c0})"; v = -sp.sin(c0); fn = r"\cos x"; dr = r"-\sin x"
    elif k == 2:
        c0 = r.choice([PI / 6, PI / 3, PI / 4]); cl = L(c0)
        fx = rf"\frac{{\tan x-\tan {cl}}}{{x-{cl}}}"; e = f"(tan(x)-tan({c0}))/(x-{c0})"; v = 1 + sp.tan(c0) ** 2; fn = r"\tan x"; dr = r"1+\tan^{2}x"
    elif k == 3:
        c0 = r.randint(1, 4); cl = str(c0)
        fx = rf"\frac{{xe^{{x}}-{L(c0*EXP(c0))}}}{{x-{cl}}}"; e = f"(x*exp(x)-{c0}*exp({c0}))/(x-{c0})"; v = (c0 + 1) * EXP(c0); fn = r"xe^{x}"; dr = r"(x+1)e^{x}"
    else:
        c0 = r.randint(2, 5); cl = str(c0)
        fx = rf"\frac{{x\ln x-{c0}\ln {c0}}}{{x-{cl}}}"; e = f"(x*log(x)-{c0}*log({c0}))/(x-{c0})"; v = LOG(c0) + 1; fn = r"x\ln x"; dr = r"\ln x+1"
    st = [f"កន្សោមនេះជាផលធៀប $\\frac{{f(x)-f(a)}}{{x-a}}$ នៃអនុគមន៍ $f(x)={fn}$ ត្រង់ $a={cl}$ ។",
          f"ដោយ $f$ មានដេរីវេ លីមីតនេះស្មើ $f'(a)$ ។ យើងមាន $f'(x)={dr}$ ។", D(rf"f'\left({cl}\right)={L(v)}")]
    return P(fx, c0, sp.nsimplify(v), st, "limit_as_derivative", "medium", e)

# algebraic opening part for exam items only (first part of a paper item)
def f_alg(r):
    a = r.randint(1, 6); b = r.choice([z for z in range(-6, 7) if z not in (0, a)]); k = r.randint(0, 3); g = r.randint(1, 5)
    if k == 0:
        fx = T(r"\frac{x^{2}-<aa>}{<q>}", aa=a * a, q=lin([(1, "x^{2}"), (-(a + b), "x"), (a * b, "")])); e = f"(x**2-{a*a})/((x-{a})*(x-({b})))"; v = Q(2 * a, a - b) if a != b else 0; p = a
        if b == -a: return None
        xb = lin([(1, "x"), (-b, "")])
        st = ["ដាក់ភាគយក និងភាគបែងជាកត្តា ៖", D(T(r"<fx>=\frac{(x-<a>)(x+<a>)}{(x-<a>)(<xb>)}=\frac{x+<a>}{<xb>}", fx=fx, a=a, xb=xb)), f"ជំនួស $x={a}$ ។"]
    elif k == 1:
        fx = T(r"\frac{\sqrt{x+<gg>}-<g>}{x}", gg=g * g, g=g); e = f"(sqrt(x+{g*g})-{g})/x"; v = Q(1, 2 * g); p = 0
        st = ["គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ ៖", D(T(r"<fx>=\frac{x}{x\left(\sqrt{x+<gg>}+<g>\right)}=\frac{1}{\sqrt{x+<gg>}+<g>}", fx=fx, gg=g * g, g=g))]
    elif k == 2:
        a2 = r.randint(2, 7); d2 = r.randint(1, 9)
        fx = T(r"\frac{<a>x^{2}+<g>x-<d>}{<b>x^{2}+<d>}", a=a2, g=c(g), d=d2, b=c(a + 1)); e = f"({a2}*x**2+{g}*x-{d2})/({a+1}*x**2+{d2})"; v = Q(a2, a + 1); p = "oo"
        st = ["ដាក់ស្វ័យគុណខ្ពស់បំផុតជាកត្តា ៖", D(T(r"<fx>=\frac{x^{2}\left(<a>+\frac{<g>}{x}-\frac{<d>}{x^{2}}\right)}{x^{2}\left(<b>+\frac{<d>}{x^{2}}\right)}", fx=fx, a=a2, g=g, d=d2, b=a + 1))]
    else:
        fx = T(r"\frac{x^{3}-<a3>}{x-<a>}", a3=a ** 3, a=a); e = f"(x**3-{a**3})/(x-{a})"; v = 3 * a * a; p = a
        st = [D(T(r"<fx>=x^{2}+<a>x+<aa>", fx=fx, a=c(a), aa=a * a)), f"ជំនួស $x={a}$ ។"]
    return P(fx, p, v, st, "algebraic_opening_part", "easy", e)

FAM = {f_ratio: 44, f_prod: 26, f_cot: 16, f_polyden: 22, f_sumlin: 14, f_1mcos: 24, f_1mcos_mix: 26, f_cosdiff: 20, f_sindiff: 18, f_tansin: 10, f_cospow: 22,
       f_shift_poly: 26, f_shift_pi: 18, f_pi2: 16, f_abcos: 24, f_pi4: 6, f_rootlin: 22, f_roottrig: 22, f_inf_trig: 22, f_sq0: 16, f_sqinf: 22, f_bounded_ratio: 18,
       f_compare: 16, f_exp: 34, f_expshift: 18, f_ln: 34, f_lnshift: 16, f_mix: 28, f_growth: 18, f_growth2: 14, f_ratioexp: 22, f_lninf: 20, f_xln: 16, f_enum: 34,
       f_ax: 16, f_side: 14, f_side2: 9, f_direct: 26, f_deriv: 10}

Q_SINGLE = [
    lambda t: f"គណនាលីមីតខាងក្រោម ៖ $${t}$$", lambda t: f"គណនាលីមីតនៃអនុគមន៍ខាងក្រោម ៖ $${t}$$", lambda t: f"រកតម្លៃនៃលីមីត ${t}$ ។",
    lambda t: f"គណនាតម្លៃនៃលីមីត ${t}$ ។", lambda t: f"គណនាលីមីតនៃអនុគមន៍ ៖ $${t}$$", lambda t: f"រកលីមីតខាងក្រោមនេះ ៖ $${t}$$", lambda t: f"តើលីមីត ${t}$ ស្មើប៉ុន្មាន ?",
]
def word_single(r, p):
    u = r.random()
    if p.setup == "side":
        return r.choice([f"គេឱ្យអនុគមន៍ $f(x)={p.fx}$ ។ សិក្សាលីមីតនៃ $f$ ត្រង់ $x=0$ ។",
                         f"តើអនុគមន៍ $f(x)={p.fx}$ មានលីមីតត្រង់ $x=0$ ឬទេ ?",
                         f"គណនាលីមីតឆ្វេង និងលីមីតស្តាំនៃ $f(x)={p.fx}$ ត្រង់ $x=0$ រួចសន្និដ្ឋាន ។"])
    if u < 0.14:
        return f"គេឱ្យអនុគមន៍ $f$ កំណត់ដោយ $f(x)={p.fx}$ ។ គណនាលីមីតនៃ $f(x)$ កាលណា $x\\to {p.pt}$ ។"
    if u < 0.24:
        return f"សិក្សាលីមីតនៃអនុគមន៍ $f(x)={p.fx}$ ត្រង់ ${p.pt}$ ។"
    if u < 0.40 and p.hint:
        return f"គណនាលីមីត ${p.tex}$ ។ (យើងដឹងថា ${p.hint}$)"
    return r.choice(Q_SINGLE)(p.tex)

def conclude(r, p):
    if p.conc: return p.conc
    return r.choice([f"ដូចនេះ $\\boxed{{{p.tex}={L(p.v)}}}$ ។", f"ដូចនេះ $\\boxed{{{p.tex}={L(p.v)}}}$ ។", f"ដូចនេះ ${p.tex}=\\boxed{{{L(p.v)}}}$ ។",
                     f"ដូចនេះ លីមីតដែលត្រូវរកស្មើ $\\boxed{{{L(p.v)}}}$ ។", f"ដូចនេះ $$\\boxed{{{p.tex}={L(p.v)}}}$$"])

ROWS, SEEN, USED = [], set(), {}
def add(row):
    k = re.sub(r"\s", "", row["problem_km"])
    if k in SEEN: return False
    SEEN.add(k); ROWS.append(row); return True
def tidy(t):
    """Drop the coefficient artefacts that parameters can produce: a fraction over 1, and 1 before lim."""
    t = re.sub(r"\\frac\{(\d+)\}\{1\}", r"\1", t)
    return re.sub(r"(?<![\d.])1\\lim", r"\\lim", t)
def mk(sub, diff, prob, sol, ans, checks, diagrams=None, grade=12):
    return make_row(TOPIC, sub, diff, clean_tex(prob), clean_tex(tidy(sol)), clean_tex(ans), checks, GEN, diagrams=diagrams, chapter="limit", grade=grade)
def rid(prob):
    return f"{TOPIC}-" + hashlib.sha1(clean_tex(prob).encode()).hexdigest()[:10]

N_PNG = [0]
def png(prob, draw):
    """Render at most 300 figures for this topic; returns the path, or None past the cap."""
    if N_PNG[0] >= 290: return None
    N_PNG[0] += 1
    return draw(rid(prob))

def curve_png(row_id, fns, xmin, xmax, ymin, ymax, pts=(), hl=(), vl=()):
    """Plot several curves, the first solid and the others dashed bounds. Labels are math only."""
    fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=110)
    for i, (f, lab) in enumerate(fns):
        xs = np.linspace(xmin, xmax, 2500); xs = xs[np.abs(xs) > 1e-6]
        with np.errstate(all="ignore"):
            ys = np.broadcast_to(np.asarray(f(xs), dtype=float), xs.shape).copy()
        ys[np.abs(ys) > 20 * max(abs(ymin), abs(ymax))] = np.nan
        ys[1:][np.abs(np.diff(ys)) > (ymax - ymin)] = np.nan
        if xmin < 0 < xmax: ys[np.argmin(np.abs(xs))] = np.nan   # no joining line across x=0
        ax.plot(xs, ys, lw=1.7 if i == 0 else 1.0, ls="-" if i == 0 else "--", color="#1f4e9c" if i == 0 else "#c0392b", label=lab)
    for h in hl: ax.axhline(h, ls=":", lw=0.9, color="gray")
    for v_ in vl: ax.axvline(v_, ls=":", lw=0.9, color="gray")
    for a_, b_ in pts: ax.plot([a_], [b_], "o", ms=4, color="#c0392b", mfc="white")
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    for sd in ("top", "right"): ax.spines[sd].set_visible(False)
    for sd in ("left", "bottom"): ax.spines[sd].set_position("zero")
    ax.grid(alpha=0.2)
    if any(l for _, l in fns): ax.legend(fontsize=7, frameon=False, loc="upper right")
    rel = f"diagrams/{row_id}.png"; fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
    return rel

def single_rows(r):
    for fam, n in FAM.items():
        n = max(6, round(n * 0.85))
        got_n, tries = 0, 0
        while got_n < n and tries < n * 12:
            tries += 1
            p = fam(r)
            if p is None or p.key() in USED: continue
            prob = word_single(r, p)
            sol = "\n".join(p.body + [conclude(r, p)])
            if len(re.findall("[\u1780-\u17FF]", sol)) < 30 and not p.conc:
                sol = "\n".join(p.body + [f"ដូចនេះ លីមីតដែលត្រូវរកស្មើ $\\boxed{{{L(p.v)}}}$ ។"])
            dia = None
            if fam is f_sq0 and got_n < 12:
                m_ = re.search(r"x\^\{(\d)\}", p.fx); n_ = int(m_.group(1)) if m_ else 1
                fnn = sp.lambdify(x, sp.sympify(p.e, locals={"x": x}), "numpy")
                k_ = int(p.e.split("*")[0]); bb = sp.lambdify(x, sp.Abs(x) ** n_ * k_, "numpy")
                bt = c(k_) + ("x^{%d}" % n_ if n_ % 2 == 0 else "|x|" if n_ == 1 else "|x^{%d}|" % n_)   # as the solution writes the bound
                bp = f"{k_}*abs(x)" + (f"^{n_}" if n_ > 1 else "")
                im = png(prob, lambda i: curve_png(i, [(fnn, f"$y={p.fx}$"), (bb, f"$y=\\pm {bt}$"), (lambda t: -bb(t), "")], -1, 1, -1.2, 1.2))
                dia = [{"type": "graph", "latex": tikz_squeeze(pgf(p.e), [bp, "-" + bp], -1, 1, -1.2, 1.2, poles=[0]),
                        "image": im, "alt_km": "ក្រាបនៃអនុគមន៍ដែលនៅចន្លោះខ្សែកោងពីរ ហើយខ្សែកោងទាំងពីរខិតជិតគ្នាត្រង់គល់តម្រុយ ។"}]
            elif fam in (f_sqinf,) and got_n < 10 and "exp" in p.e:
                fnn = sp.lambdify(x, sp.sympify(p.e, locals={"x": x}), "numpy"); a_ = int(re.search(r"exp\(-(\d+)", p.e).group(1))
                im = png(prob, lambda i: curve_png(i, [(fnn, f"$y={p.fx}$"), (lambda t: np.exp(-a_ * t), f"$y=\\pm e^{{-{c(a_)}x}}$"), (lambda t: -np.exp(-a_ * t), "")], 0.01, 8, -1.1, 1.1))
                dia = [{"type": "graph", "latex": tikz_squeeze(pgf(p.e), [f"exp(-{a_}*x)", f"-exp(-{a_}*x)"], 0, 8, -1.1, 1.1), "image": im,
                        "alt_km": "ក្រាបលំយោលនៅចន្លោះខ្សែកោងអ៊ិចស្ប៉ូណង់ស្យែលពីរ ដែលខិតជិតអ័ក្សអាប់ស៊ីស ។"}]
            elif fam is f_side and p.nolim and got_n < 12:
                fnn = sp.lambdify(x, sp.sympify(p.e, locals={"x": x, "Abs": sp.Abs}), "numpy")
                im = png(prob, lambda i: curve_png(i, [(fnn, "")], -2, 2, -7, 7))
                dia = [{"type": "graph", "latex": tikz_graph("x", -2, 2, -7, 7).replace("samples=200]", "samples=200,trig format=rad]").replace("\\addplot[thick,domain=-2:2] {x};", "\\addplot[thick,domain=-2:-0.01] {" + pgf(p.e) + "};\n\\addplot[thick,domain=0.01:2] {" + pgf(p.e) + "};"),
                        "image": im, "alt_km": "ក្រាបដែលលោតត្រង់ $x=0$ ហើយលីមីតឆ្វេងខុសពីលីមីតស្តាំ ។"}]
            row = mk(p.sub, p.diff, prob, sol, p.ans, p.checks(), diagrams=dia, grade=p.grade)
            if add(row):
                USED[p.key()] = 1; got_n += 1

def pgf(e):
    """SymPy string to pgfplots syntax."""
    t = e.replace("**", "^").replace("Abs", "abs").replace("log(", "ln(")
    return re.sub(r"\^1(?![\d.])", "", t)

LBL = [["ក", "ខ", "គ", "ឃ", "ង"], ["ក", "ខ", "គ", "ឃ", "ង"], ["១", "២", "៣", "៤", "៥"]]
HEAD = ["គណនាលីមីត ៖", "គណនាលីមីតខាងក្រោម ៖", "គណនាលីមីតនៃអនុគមន៍ខាងក្រោម ៖", "គណនាលីមីតខាងក្រោមនេះ ៖", "I. គណនាលីមីត ៖", "រកតម្លៃនៃលីមីតខាងក្រោម ៖"]
PROFILES = [
    ("science_three", [[f_alg, f_exp, f_ln, f_ratioexp], [f_ratio, f_prod, f_polyden, f_1mcos, f_rootlin], [f_1mcos_mix, f_cosdiff, f_shift_poly, f_abcos, f_pi2, f_tansin, f_shift_pi, f_roottrig]], 220),
    ("science_trig_only", [[f_ratio, f_cot, f_sumlin], [f_1mcos, f_sindiff, f_shift_poly], [f_cospow, f_abcos, f_pi2, f_pi4, f_roottrig]], 75),
    ("science_exp_log", [[f_exp, f_ln, f_ratioexp], [f_expshift, f_lnshift, f_mix, f_xln], [f_enum, f_growth2, f_mix]], 75),
    ("science_four", [[f_alg, f_direct], [f_ratio, f_exp, f_ln], [f_1mcos_mix, f_shift_poly, f_rootlin], [f_abcos, f_enum, f_mix, f_cosdiff]], 50),
    ("science_five", [[f_alg], [f_ratio, f_polyden], [f_exp, f_ln], [f_1mcos, f_roottrig], [f_enum, f_abcos, f_shift_pi]], 25),
    ("society_style", [[f_direct, f_alg], [f_ratioexp, f_growth, f_lninf], [f_growth2, f_exp, f_ln, f_prod]], 50),
]
def multi_rows(r):
    for name, slots, n in PROFILES:
        done, tries = 0, 0
        while done < n and tries < n * 30:
            tries += 1
            ps = []
            for sl in slots:
                p = r.choice(sl)(r)
                if p is None or p.setup == "side": ps = None; break
                ps.append(p)
            if not ps or len({q.key() for q in ps}) < len(ps): continue
            if any(USED.get(q.key(), 0) >= 2 for q in ps): continue
            if len({q.sub for q in ps}) < len(ps) - (1 if len(ps) > 3 else 0): continue
            lb = r.choice(LBL); sep = r.choice([". ", ". ", "- "])
            head = r.choice(HEAD if name != "society_style" else ["គណនាលីមីតនៃអនុគមន៍ខាងក្រោម ៖", "គណនាលីមីត ៖"])
            prob = head + "\n" + "\n".join(f"{lb[i]}{sep}${q.tex}$" for i, q in enumerate(ps))
            parts = []
            for i, q in enumerate(ps):
                first = r.choice([f"{lb[i]}{sep}គណនា ${q.tex}$", f"{lb[i]}{sep}${q.tex}$", f"{lb[i]}{sep}គណនា ${q.tex}$ ។"])
                parts.append("\n".join([first] + q.body + [conclude(r, q)]))
            sol = ("ដំណោះស្រាយ\n" if r.random() < 0.3 else "") + "\n".join(parts)
            ans = r",\ ".join(q.ans for q in ps)
            ch = [c_ for q in ps for c_ in q.checks()]
            if add(mk("exam_multi_part_" + name, "bacii", prob, sol, ans, ch, grade=12)):
                done += 1
                for q in ps: USED[q.key()] = USED.get(q.key(), 0) + 1

def two_method_rows(r):
    n = 0
    while n < 22:
        p = f_1mcos(r)
        if p.key() + "2" in USED: continue
        USED[p.key() + "2"] = 1
        prob = r.choice([f"គណនា ${p.tex}$ ដោយពីររបៀប ។", f"ចូរគណនាលីមីត ${p.tex}$ ។ បន្ទាប់មកផ្ទៀងផ្ទាត់លទ្ធផលដោយរបៀបមួយទៀត ។"])
        sol = "\n".join(["របៀបទី១ ៖"] + [b for b in p.body] + ["របៀបមួយទៀត ៖"] + p.alt + ["វិធីទាំងពីរឱ្យលទ្ធផលដូចគ្នា ។", f"ដូចនេះ $\\boxed{{{p.tex}={L(p.v)}}}$ ។"])
        if add(mk("two_methods", "hard", prob, sol, L(p.v), p.checks())): n += 1

def param_rows(r):
    n = 0; tries = 0
    while n < 50 and tries < 1500:
        tries += 1
        k = r.randint(0, 7); a = r.randint(2, 9); b = r.randint(2, 9); L0 = None
        if k == 0:
            v = Q(a, b); fx = rf"\frac{{\sin ax}}{{{b}x}}"; prob = f"រកចំនួនពិត $a$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}{fx}={L(v)}$ ។"
            sol = [D(rf"\lim_{{x\to 0}}{fx}=\frac{{a}}{{{b}}}\lim_{{x\to 0}}\frac{{\sin ax}}{{ax}}=\frac{{a}}{{{b}}}"), f"លក្ខខណ្ឌឱ្យ $\\frac{{a}}{{{b}}}={L(v)}$ នាំឱ្យ $a={a}$ ។", f"ដូចនេះ $\\boxed{{a={a}}}$ ។"]
            ans = f"a={a}"; ch = [check(f"limit(sin({a}*x)/({b}*x),x,0)", str(v), "value at a")]
        elif k == 1:
            v = Q(a * a, 2); prob = r.choice([f"រកតម្លៃ $a>0$ ដោយដឹងថា $\\lim_{{x\\to 0}}\\frac{{1-\\cos ax}}{{x^{{2}}}}={L(v)}$ ។", f"កំណត់ចំនួនវិជ្ជមាន $a$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}\\frac{{1-\\cos ax}}{{x^{{2}}}}={L(v)}$ ។"])
            sol = ["តាង $u=ax$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ។", D(r"\lim_{x\to 0}\frac{1-\cos ax}{x^{2}}=a^{2}\lim_{u\to 0}\frac{1-\cos u}{u^{2}}=\frac{a^{2}}{2}"), f"លក្ខខណ្ឌ ៖ $\\frac{{a^{{2}}}}{{2}}={L(v)}$ នាំឱ្យ $a^{{2}}={a*a}$ ។ ដោយ $a>0$ យើងយក $a={a}$ ។", f"ដូចនេះ $\\boxed{{a={a}}}$ ។"]
            ans = f"a={a}"; ch = [check(f"limit((1-cos({a}*x))/x**2,x,0)", str(v), "value at a")]
        elif k == 2:
            prob = f"រកតម្លៃ $a$ ដើម្បីឱ្យ $\\lim_{{x\\to+\\infty}}\\left(1+\\frac{{a}}{{x}}\\right)^{{x}}=e^{{{a}}}$ ។"
            sol = ["បើ $a\\neq 0$ តាង $t=\\frac{x}{a}$ ។ ដូច្នេះ", D(r"\left(1+\frac{a}{x}\right)^{x}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{a}\to e^{a}"), f"យើងផ្ទឹម $e^{{a}}=e^{{{a}}}$ ។ ដោយអនុគមន៍អ៊ិចស្ប៉ូណង់ស្យែលកើនដាច់ខាត យើងបាន $a={a}$ ។".replace("កើនដាច់ខាត", "ជាអនុគមន៍កើន"), f"ដូចនេះ $\\boxed{{a={a}}}$ ។"]
            ans = f"a={a}"; ch = [check(f"limit((1+{a}/x)**x,x,oo)", f"exp({a})", "value at a")]
        elif k == 3:
            m_ = r.randint(1, 6)  # (a cos x + b)/x^2 -> L: a+b=0, L=-a/2
            A = -2 * m_ if r.random() < .5 else 2 * m_; Lv = Q(-A, 2)
            prob = f"កំណត់ចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}\\frac{{a\\cos x+b}}{{x^{{2}}}}={L(Lv)}$ ។"
            sol = ["ភាគបែងខិតជិត $0$ ។ ដើម្បីឱ្យលីមីតជាចំនួនកំណត់ ភាគយកក៏ត្រូវខិតជិត $0$ ដែរ ដូច្នេះ $a+b=0$ គឺ $b=-a$ ។",
                   D(r"\lim_{x\to 0}\frac{a\cos x-a}{x^{2}}=-a\lim_{x\to 0}\frac{1-\cos x}{x^{2}}=-\frac{a}{2}"), f"លក្ខខណ្ឌ ៖ $-\\frac{{a}}{{2}}={L(Lv)}$ នាំឱ្យ $a={A}$ ហើយ $b={-A}$ ។", f"ដូចនេះ $\\boxed{{a={A},\\ b={-A}}}$ ។"]
            ans = f"a={A},\\ b={-A}"; ch = [check(f"limit(({A}*cos(x)+({-A}))/x**2,x,0)", str(Lv), "value at a,b")]
        elif k == 4:
            g = r.randint(1, 5); t_ = r.randint(1, 5); A = 2 * g * t_  # (sqrt(ax+g^2)-g)/sin x -> a/(2g)=t
            prob = f"កំណត់ចំនួនពិត $a$ និង $b>0$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}\\frac{{\\sqrt{{ax+b}}-{g}}}{{\\sin x}}={t_}$ ។"
            sol = [f"ភាគបែងខិតជិត $0$ ។ ដើម្បីឱ្យលីមីតជាចំនួនកំណត់ ភាគយកត្រូវខិតជិត $0$ ៖ $\\sqrt{{b}}={g}$ នាំឱ្យ $b={g*g}$ ។", "គុណនឹងកន្សោមឆ្លាស់ ៖",
                   D(rf"\frac{{\sqrt{{ax+{g*g}}}-{g}}}{{\sin x}}=\frac{{ax}}{{\sin x\left(\sqrt{{ax+{g*g}}}+{g}\right)}}"), f"កាលណា $x\\to 0$ កន្សោមនេះខិតជិត $\\frac{{a}}{{{2*g}}}$ ។ លក្ខខណ្ឌ $\\frac{{a}}{{{2*g}}}={t_}$ នាំឱ្យ $a={A}$ ។", f"ដូចនេះ $\\boxed{{a={A},\\ b={g*g}}}$ ។"]
            ans = f"a={A},\\ b={g*g}"; ch = [check(f"limit((sqrt({A}*x+{g*g})-{g})/sin(x),x,0)", str(t_), "value at a,b")]
        elif k == 5:
            v = Q(a, b); prob = f"រកតម្លៃ $m$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}\\frac{{e^{{mx}}-1}}{{\\sin {b}x}}={L(v)}$ ។"
            sol = [D(rf"\frac{{e^{{mx}}-1}}{{\sin {b}x}}=\frac{{e^{{mx}}-1}}{{mx}}\cdot\frac{{{b}x}}{{\sin {b}x}}\cdot\frac{{m}}{{{b}}}\qquad(m\neq 0)"), f"កាលណា $x\\to 0$ កន្សោមនេះខិតជិត $\\frac{{m}}{{{b}}}$ ។ លក្ខខណ្ឌ $\\frac{{m}}{{{b}}}={L(v)}$ នាំឱ្យ $m={a}$ ។", f"ដូចនេះ $\\boxed{{m={a}}}$ ។"]
            ans = f"m={a}"; ch = [check(f"limit((exp({a}*x)-1)/sin({b}*x),x,0)", str(v), "value at m")]
        elif k == 6:
            v = Q(a, b); prob = f"រកតម្លៃ $m$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}\\frac{{\\ln(1+mx)}}{{{b}x}}={L(v)}$ ។"
            sol = [D(rf"\frac{{\ln(1+mx)}}{{{b}x}}=\frac{{m}}{{{b}}}\cdot\frac{{\ln(1+mx)}}{{mx}}\qquad(m\neq 0)"), f"ដោយ ${LNF}$ លីមីតស្មើ $\\frac{{m}}{{{b}}}$ ។ លក្ខខណ្ឌឱ្យ $m={a}$ ។", f"ដូចនេះ $\\boxed{{m={a}}}$ ។"]
            ans = f"m={a}"; ch = [check(f"limit(log(1+{a}*x)/({b}*x),x,0)", str(v), "value at m")]
        else:
            g = r.randint(2, 7); e2 = a * b
            prob = f"រកតម្លៃ $a$ ដើម្បីឱ្យ $\\lim_{{x\\to 0}}(1+ax)^{{\\frac{{{b}}}{{x}}}}=e^{{{e2}}}$ ។"
            sol = ["បើ $a\\neq 0$ តាង $u=ax$ ។ បើ $x\\to 0$ នោះ $u\\to 0$ ហើយ", D(rf"(1+ax)^{{\frac{{{b}}}{{x}}}}=\left[(1+u)^{{\frac{{1}}{{u}}}}\right]^{{{b}a}}\to e^{{{b}a}}"), f"លក្ខខណ្ឌ $e^{{{b}a}}=e^{{{e2}}}$ នាំឱ្យ ${b}a={e2}$ គឺ $a={a}$ ។", f"ដូចនេះ $\\boxed{{a={a}}}$ ។"]
            ans = f"a={a}"; ch = [check(f"limit((1+{a}*x)**({b}/x),x,0)", f"exp({e2})", "value at a")]
        if add(mk("find_parameter", "hard" if k in (3, 4) else "medium", prob, "\n".join(sol), ans, ch)): n += 1

def identity_rows(r):
    """Multi-part items: prove an identity, then deduce a limit."""
    n = 0; tries = 0
    while n < 70 and tries < 1500:
        tries += 1
        k = r.randint(0, 4); a = r.randint(1, 6); b = r.randint(2, 7); A = c(a) + "x"
        l1, l2, l3 = r.choice([("ក", "ខ", "គ"), ("១", "២", "៣")])
        if k == 0:
            fx = T(r"\frac{\tan <A>-\sin <A>}{x^{3}}", A=A); v = Q(a ** 3, 2)
            prob = f"{l1}. បង្ហាញថា $\\tan u-\\sin u=\\tan u\\,(1-\\cos u)$ ។\n{l2}. គណនា $\\lim_{{x\\to 0}}\\frac{{1-\\cos {A}}}{{x^{{2}}}}$ ។\n{l3}. ទាញរកលីមីត $\\lim_{{x\\to 0}}{fx}$ ។"
            sol = [f"{l1}. យើងមាន $\\tan u\\cos u=\\sin u$ ។ គេបាន $\\tan u\\,(1-\\cos u)=\\tan u-\\tan u\\cos u=\\tan u-\\sin u$ ។",
                   f"{l2}. ប្រើ ${COSF}$ ជាមួយ $u={A}$ ៖ " + D(rf"\lim_{{x\to 0}}\frac{{1-\cos {A}}}{{x^{{2}}}}={a*a}\cdot\frac{{1}}{{2}}={L(Q(a*a,2))}"),
                   f"{l3}. តាមសំណួរ {l1} ៖ " + D(rf"{fx}=\frac{{\tan {A}}}{{x}}\cdot\frac{{1-\cos {A}}}{{x^{{2}}}}"), f"កត្តាទីមួយខិតជិត ${a}$ ។", f"ដូចនេះ $\\boxed{{\\lim_{{x\\to 0}}{fx}={L(v)}}}$ ។"]
            ans = L(Q(a * a, 2)) + r",\ " + L(v); ch = [check(f"limit((1-cos({a}*x))/x**2,x,0)", str(Q(a * a, 2))), check(f"limit((tan({a}*x)-sin({a}*x))/x**3,x,0)", str(v)), check("subs(tan(x)-sin(x)-tan(x)*(1-cos(x)),x,Rational(1,3))", "0", "identity instance")]
        elif k == 1:
            d = a + b - 0; p_, q_ = a + b, b
            if p_ == q_: continue
            # cos(p x)-cos(q x) with p>q: -2 sin((p+q)x/2) sin((p-q)x/2)
            fx = T(r"\frac{\cos <p>x-\cos <q>x}{x^{2}}", p=p_, q=q_); v = Q(q_ * q_ - p_ * p_, 2)
            prob = f"គេឱ្យ $f(x)={fx}$ ចំពោះ $x\\neq 0$ ។\n{l1}. សរសេរភាគយកជាផលគុណ ដោយប្រើ $\\cos p-\\cos q=-2\\sin\\frac{{p+q}}{{2}}\\sin\\frac{{p-q}}{{2}}$ ។\n{l2}. គណនា $\\lim_{{x\\to 0}}f(x)$ ។\n{l3}. ផ្ទៀងផ្ទាត់លទ្ធផលដោយបំបែក $f(x)$ ជាផលដកនៃប្រភាគពីរដែលមានរាង $\\frac{{1-\\cos kx}}{{x^{{2}}}}$ ។"
            H, K = hf(p_ + q_), hf(p_ - q_)
            sol = [f"{l1}. យើងបាន " + D(rf"\cos {p_}x-\cos {q_}x=-2\sin {H}\,\sin {K}"),
                   f"{l2}. ចែកនឹង $x^{{2}}$ ៖ " + D(rf"f(x)=-2\cdot\frac{{\sin {H}}}{{x}}\cdot\frac{{\sin {K}}}{{x}}"), f"កាលណា $x\\to 0$ គេមាន $\\frac{{\\sin {H}}}{{x}}\\to {L(Q(p_+q_,2))}$ និង $\\frac{{\\sin {K}}}{{x}}\\to {L(Q(p_-q_,2))}$ ។", f"ដូច្នេះ $\\lim_{{x\\to 0}}f(x)={L(v)}$ ។",
                   f"{l3}. យើងសរសេរ " + D(rf"f(x)=\frac{{1-\cos {q_}x}}{{x^{{2}}}}-\frac{{1-\cos {p_}x}}{{x^{{2}}}}\to\frac{{{q_*q_}}}{{2}}-\frac{{{p_*p_}}}{{2}}={L(v)}"), f"ដូចនេះ $\\boxed{{\\lim_{{x\\to 0}}f(x)={L(v)}}}$ ។"]
            ans = L(v); ch = [check(f"limit((cos({p_}*x)-cos({q_}*x))/x**2,x,0)", str(v)), check(f"subs(cos({p_}*x)-cos({q_}*x)+2*sin({Q(p_+q_,2)}*x)*sin({Q(p_-q_,2)}*x),x,Rational(1,3))", "0", "identity instance")]
        elif k == 2:
            fx = T(r"\frac{\sin <A>}{x}", A=A)
            g = r.randint(1, 5); h_ = r.randint(1, 5)
            prob = f"គេឱ្យអនុគមន៍ $f(x)=\\frac{{\\sin {A}+{g}x}}{{\\tan {A}+{h_}x}}$ ។\n{l1}. កំណត់តម្លៃ $x$ ជិត $0$ ដែលធ្វើឱ្យ $f$ មានន័យ ដោយសរសេរ $f(x)$ ជាផលធៀបនៃ $\\frac{{\\sin {A}}}{{x}}+{g}$ និង $\\frac{{\\tan {A}}}{{x}}+{h_}$ ។\n{l2}. គណនា $\\lim_{{x\\to 0}}f(x)$ ។\n{l3}. គណនា $\\lim_{{x\\to+\\infty}}\\frac{{\\sin {A}+{g}x}}{{x}}$ ។"
            sol = [f"{l1}. ចំពោះ $x\\neq 0$ ជិត $0$ ចែកភាគយក និងភាគបែងនឹង $x$ ៖ " + D(rf"f(x)=\frac{{\frac{{\sin {A}}}{{x}}+{g}}}{{\frac{{\tan {A}}}{{x}}+{h_}}}"),
                   f"{l2}. កាលណា $x\\to 0$ ភាគយកខិតជិត ${a}+{g}={a+g}$ ហើយភាគបែងខិតជិត ${a}+{h_}={a+h_}$ ។ ដូច្នេះ $\\lim_{{x\\to 0}}f(x)={L(Q(a+g,a+h_))}$ ។",
                   f"{l3}. យើងមាន " + D(rf"\frac{{\sin {A}+{g}x}}{{x}}=\frac{{\sin {A}}}{{x}}+{g}"), f"ដោយ $\\left|\\frac{{\\sin {A}}}{{x}}\\right|\\le\\frac{{1}}{{x}}$ ចំពោះ $x>0$ តួនេះខិតជិត $0$ ។", f"ដូចនេះ $\\boxed{{\\lim_{{x\\to 0}}f(x)={L(Q(a+g,a+h_))}}}$ និង $\\boxed{{\\lim_{{x\\to+\\infty}}\\frac{{\\sin {A}+{g}x}}{{x}}={g}}}$ ។"]
            ans = L(Q(a + g, a + h_)) + r",\ " + str(g); ch = [check(f"limit((sin({a}*x)+{g}*x)/(tan({a}*x)+{h_}*x),x,0)", str(Q(a + g, a + h_))), check(f"limit((sin({a}*x)+{g}*x)/x,x,oo)", str(g))]
        elif k == 3:
            prob = f"គេឱ្យ $g(x)=\\frac{{e^{{{A}}}-1}}{{x}}$ និង $h(x)=\\frac{{\\ln(1+{c(b)}x)}}{{x}}$ ។\n{l1}. គណនា $\\lim_{{x\\to 0}}g(x)$ និង $\\lim_{{x\\to 0}}h(x)$ ។\n{l2}. ទាញរក $\\lim_{{x\\to 0}}\\frac{{e^{{{A}}}-1}}{{\\ln(1+{c(b)}x)}}$ ។\n{l3}. ទាញរក $\\lim_{{x\\to 0}}\\frac{{\\left(e^{{{A}}}-1\\right)\\ln(1+{c(b)}x)}}{{x^{{2}}}}$ ។"
            sol = [f"{l1}. តាម ${EXPF}$ និង ${LNF}$ ៖", D(rf"\lim_{{x\to 0}}g(x)={a}\lim_{{x\to 0}}\frac{{e^{{{A}}}-1}}{{{A}}}={a},\qquad\lim_{{x\to 0}}h(x)={b}\lim_{{x\to 0}}\frac{{\ln(1+{c(b)}x)}}{{{c(b)}x}}={b}"),
                   f"{l2}. ដោយ $\\frac{{e^{{{A}}}-1}}{{\\ln(1+{c(b)}x)}}=\\frac{{g(x)}}{{h(x)}}$ លីមីតស្មើ $\\frac{{{a}}}{{{b}}}$ ។",
                   f"{l3}. កន្សោមនេះស្មើ $g(x)h(x)$ ដូច្នេះលីមីតស្មើ ${a}\\cdot {b}={a*b}$ ។", f"ដូចនេះ $\\boxed{{{L(Q(a,b))}}}$ និង $\\boxed{{{a*b}}}$ ជាលីមីតរៀងគ្នានៃសំណួរ {l2} និង {l3} ។"]
            ans = rf"{a},\ {b},\ {L(Q(a,b))},\ {a*b}"; ch = [check(f"limit((exp({a}*x)-1)/x,x,0)", str(a)), check(f"limit(log(1+{b}*x)/x,x,0)", str(b)), check(f"limit((exp({a}*x)-1)/log(1+{b}*x),x,0)", str(Q(a, b))), check(f"limit((exp({a}*x)-1)*log(1+{b}*x)/x**2,x,0)", str(a * b))]
        else:
            g = r.randint(1, 5)
            prob = f"តាង $t=\\frac{{1}}{{x}}$ ។\n{l1}. បង្ហាញថា $x\\sin\\frac{{{a}}}{{x}}=\\frac{{\\sin {c(a)}t}}{{t}}$ រួចគណនា $\\lim_{{x\\to+\\infty}}x\\sin\\frac{{{a}}}{{x}}$ ។\n{l2}. គណនា $\\lim_{{x\\to+\\infty}}x^{{2}}\\left(1-\\cos\\frac{{{b}}}{{x}}\\right)$ ។\n{l3}. ទាញរក $\\lim_{{x\\to+\\infty}}\\frac{{x^{{2}}\\left(1-\\cos\\frac{{{b}}}{{x}}\\right)}}{{x\\sin\\frac{{{a}}}{{x}}}}$ ។"
            v1, v2 = a, Q(b * b, 2)
            sol = [f"{l1}. ដោយ $x=\\frac{{1}}{{t}}$ គេបាន $x\\sin\\frac{{{a}}}{{x}}=\\frac{{1}}{{t}}\\sin {c(a)}t=\\frac{{\\sin {c(a)}t}}{{t}}$ ។ បើ $x\\to+\\infty$ នោះ $t\\to 0^{{+}}$ ដូច្នេះលីមីតស្មើ ${a}$ ។",
                   f"{l2}. ដូចគ្នា " + D(rf"x^{{2}}\left(1-\cos\frac{{{b}}}{{x}}\right)=\frac{{1-\cos {b}t}}{{t^{{2}}}}\to\frac{{{b*b}}}{{2}}"),
                   f"{l3}. កន្សោមនេះជាផលធៀបនៃកន្សោមទាំងពីរខាងលើ ហើយភាគបែងមានលីមីត ${a}\\neq 0$ ។", f"ដូចនេះ លីមីតស្មើ $\\boxed{{{L(v2/v1)}}}$ ។"]
            ans = rf"{a},\ {L(v2)},\ {L(v2/v1)}"; ch = [check(f"limit(x*sin({a}/x),x,oo)", str(a)), check(f"limit(x**2*(1-cos({b}/x)),x,oo)", str(v2)), check(f"limit(x*(1-cos({b}/x))/sin({a}/x),x,oo)", str(v2 / v1))]
        if add(mk("exam_guided_multi_part", "bacii", prob, "\n".join(sol), ans, ch)): n += 1

def study_rows(r):
    """Function-study limits with a known limit in brackets, then an asymptote, then a graph."""
    n = 0; tries = 0
    while n < 70 and tries < 2500:
        tries += 1
        k = r.randint(0, 5); a = r.choice([1, 1, 2, 3]); b = r.randint(-3, 3); g = r.randint(1, 3)
        l1, l2, l3 = r.choice([("ក", "ខ", "គ"), ("១", "២", "៣")])
        ln_ = lin([(a, "x"), (b, "")])
        if k == 0:
            fx = rf"{ln_}+\frac{{{g}\ln x}}{{x}}".replace(r"{1\ln", r"{\ln"); e = f"{a}*x+({b})+{g}*log(x)/x"
            prob = f"គេឱ្យអនុគមន៍ $f(x)={fx}$ កំណត់លើ $(0,+\\infty)$ ហើយ $(C)$ ជាក្រាបរបស់វា ។\n{l1}. គណនា $\\lim_{{x\\to 0^{{+}}}}f(x)$ រួចទាញរកអាស៊ីមតូតឈរ ។\n{l2}. គណនា $\\lim_{{x\\to+\\infty}}f(x)$ ។ (យើងដឹងថា ${LNX}$)\n{l3}. បង្ហាញថាបន្ទាត់ $y={ln_}$ ជាអាស៊ីមតូតទ្រេតនៃ $(C)$ ។"
            sol = [f"{l1}. កាលណា $x\\to 0^{{+}}$ គេមាន $\\ln x\\to-\\infty$ និង $\\frac{{1}}{{x}}\\to+\\infty$ ដូច្នេះ $\\frac{{\\ln x}}{{x}}\\to-\\infty$ ។ គេបាន $\\lim_{{x\\to 0^{{+}}}}f(x)=-\\infty$ ។", "ដូច្នេះបន្ទាត់ $x=0$ ជាអាស៊ីមតូតឈរនៃ $(C)$ ។",
                   f"{l2}. ដោយ $\\frac{{\\ln x}}{{x}}\\to 0$ និង ${ln_}\\to+\\infty$ គេបាន $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។",
                   f"{l3}. យើងគណនា " + D(rf"\lim_{{x\to+\infty}}\left[f(x)-\left({ln_}\right)\right]=\lim_{{x\to+\infty}}\frac{{{c(g)}\ln x}}{{x}}=0"), f"ដូចនេះ បន្ទាត់ $\\boxed{{y={ln_}}}$ ជាអាស៊ីមតូតទ្រេតនៃ $(C)$ ។"]
            ans = rf"-\infty,\ +\infty,\ y={ln_}"
            ch = [check(f"limit({e},x,0,'+')", "-oo"), check(f"limit({e},x,oo)", "oo"), check(f"limit({e}-({a}*x+({b})),x,oo)", "0")]
            f_ = lambda t, a=a, b=b, g=g: a * t + b + g * np.log(t) / t; dom = (0.05, 8); asy = lambda t, a=a, b=b: a * t + b; pg = f"{a}*x+({b})+{g}*ln(x)/x"; vl = (); ax_ = f"{a}*x+({b})"; yb = (-6, 12)
        elif k == 1:
            fx = rf"{ln_}+{c(g)}e^{{-x}}"; e = f"{a}*x+({b})+{g}*exp(-x)"
            prob = f"គេឱ្យអនុគមន៍ $f$ កំណត់លើ $\\mathbb{{R}}$ ដោយ $f(x)={fx}$ ។\n{l1}. គណនាលីមីតនៃ $f(x)$ ត្រង់ $+\\infty$ ។\n{l2}. គណនាលីមីតនៃ $f(x)$ ត្រង់ $-\\infty$ ។ (យើងដឹងថា ${XEX}$)\n{l3}. ទាញបញ្ជាក់ថាបន្ទាត់ $y={ln_}$ ជាអាស៊ីមតូតទ្រេតនៃក្រាបត្រង់ $+\\infty$ ។"
            sol = [f"{l1}. ដោយ $e^{{-x}}\\to 0$ កាលណា $x\\to+\\infty$ គេបាន $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។",
                   f"{l2}. មានរាងមិនកំណត់ $\\infty-\\infty$ ។ តាង $t=-x$ ៖ " + D(rf"f(x)={lin([(-a,'t'),(b,'')])}+{c(g)}e^{{t}}=e^{{t}}\left({c(g) if g!=1 else '1'}+\frac{{{lin([(-a,'t'),(b,'')])}}}{{e^{{t}}}}\right)"), "កាលណា $t\\to+\\infty$ ប្រភាគក្នុងវង់ក្រចកខិតជិត $0$ ហើយ $e^{t}\\to+\\infty$ ។ ដូច្នេះ $\\lim_{x\\to-\\infty}f(x)=+\\infty$ ។",
                   f"{l3}. យើងមាន $f(x)-\\left({ln_}\\right)={c(g)}e^{{-x}}\\to 0$ កាលណា $x\\to+\\infty$ ។", f"ដូចនេះ $\\boxed{{y={ln_}}}$ ជាអាស៊ីមតូតទ្រេតត្រង់ $+\\infty$ ។"]
            ans = rf"+\infty,\ +\infty,\ y={ln_}"
            ch = [check(f"limit({e},x,oo)", "oo"), check(f"limit({e},x,-oo)", "oo"), check(f"limit({e}-({a}*x+({b})),x,oo)", "0")]
            f_ = lambda t, a=a, b=b, g=g: a * t + b + g * np.exp(-t); dom = (-4, 6); asy = lambda t, a=a, b=b: a * t + b; pg = f"{a}*x+({b})+{g}*exp(-x)"; vl = (); ax_ = f"{a}*x+({b})"; yb = (-6, 12)
        elif k == 2:
            p_ = lin([(a, "x"), (abs(b) + 1, "")]); e = f"({a}*x+{abs(b)+1})*exp(-x)"; fx = rf"\left({p_}\right)e^{{-x}}"
            prob = f"គេឱ្យ $f(x)={fx}$ ។\n{l1}. សរសេរ $f(x)$ ជាផលបូកនៃតួដែលមាន $\\frac{{x}}{{e^{{x}}}}$ រួចគណនា $\\lim_{{x\\to+\\infty}}f(x)$ ។\n{l2}. គណនា $\\lim_{{x\\to-\\infty}}f(x)$ ។\n{l3}. ទាញរកអាស៊ីមតូតដេកនៃក្រាប ។"
            sol = [f"{l1}. យើងមាន " + D(rf"f(x)={c(a) if a!=1 else ''}\frac{{x}}{{e^{{x}}}}+\frac{{{abs(b)+1}}}{{e^{{x}}}}"), "ដោយ $\\frac{x}{e^{x}}\\to 0$ និង $\\frac{1}{e^{x}}\\to 0$ កាលណា $x\\to+\\infty$ គេបាន $\\lim_{x\\to+\\infty}f(x)=0$ ។",
                   f"{l2}. កាលណា $x\\to-\\infty$ គេមាន ${p_}\\to-\\infty$ និង $e^{{-x}}\\to+\\infty$ ។ ផលគុណខិតជិត $-\\infty$ ។", f"{l3}. ដោយ $\\lim_{{x\\to+\\infty}}f(x)=0$ ", f"ដូចនេះ បន្ទាត់ $\\boxed{{y=0}}$ ជាអាស៊ីមតូតដេកនៃក្រាបត្រង់ $+\\infty$ ។"]
            sol[3] = sol[3] + "អ័ក្សអាប់ស៊ីសជាអាស៊ីមតូតដេក ។"
            ans = r"0,\ -\infty,\ y=0"; ch = [check(f"limit({e},x,oo)", "0"), check(f"limit({e},x,-oo)", "-oo")]
            f_ = lambda t, a=a, b=abs(b) + 1: (a * t + b) * np.exp(-t); dom = (-3, 8); asy = None; pg = f"({a}*x+{abs(b)+1})*exp(-x)"; vl = (); ax_ = None; yb = (-6, 6)
        elif k == 3:
            q = r.randint(1, 4); fx = rf"\frac{{e^{{x}}+{q}}}{{e^{{x}}-1}}"; e = f"(exp(x)+{q})/(exp(x)-1)"
            prob = f"គេឱ្យអនុគមន៍ $f(x)={fx}$ កំណត់ចំពោះ $x\\neq 0$ ។\n{l1}. គណនា $\\lim_{{x\\to+\\infty}}f(x)$ និង $\\lim_{{x\\to-\\infty}}f(x)$ ។\n{l2}. គណនា $\\lim_{{x\\to 0^{{-}}}}f(x)$ និង $\\lim_{{x\\to 0^{{+}}}}f(x)$ ។\n{l3}. ទាញរកអាស៊ីមតូតទាំងអស់នៃក្រាបនៃ $f$ ។"
            sol = [f"{l1}. ចែកភាគយក និងភាគបែងនឹង $e^{{x}}$ ៖ " + D(rf"f(x)=\frac{{1+{c(q) if q!=1 else ''}e^{{-x}}}}{{1-e^{{-x}}}}\to 1\quad(x\to+\infty)"), f"កាលណា $x\\to-\\infty$ គេមាន $e^{{x}}\\to 0$ ដូច្នេះ $f(x)\\to\\frac{{{q}}}{{-1}}=-{q}$ ។",
                   f"{l2}. ភាគយកខិតជិត ${q+1}>0$ ។ ភាគបែង $e^{{x}}-1$ អវិជ្ជមានចំពោះ $x<0$ និងវិជ្ជមានចំពោះ $x>0$ ។ គេបាន $\\lim_{{x\\to 0^{{-}}}}f(x)=-\\infty$ និង $\\lim_{{x\\to 0^{{+}}}}f(x)=+\\infty$ ។",
                   f"{l3}. តាមលទ្ធផលខាងលើ ៖", f"ដូចនេះ បន្ទាត់ $\\boxed{{x=0}}$ ជាអាស៊ីមតូតឈរ ហើយ $\\boxed{{y=1}}$ និង $\\boxed{{y=-{q}}}$ ជាអាស៊ីមតូតដេក ។"]
            ans = rf"1,\ -{q},\ -\infty,\ +\infty"; ch = [check(f"limit({e},x,oo)", "1"), check(f"limit({e},x,-oo)", str(-q)), check(f"limit({e},x,0,'-')", "-oo"), check(f"limit({e},x,0,'+')", "oo")]
            f_ = lambda t, q=q: (np.exp(t) + q) / (np.exp(t) - 1); dom = (-5, 5); asy = None; pg = f"(exp(x)+{q})/(exp(x)-1)"; vl = (0,); ax_ = None; yb = (-8, 8)
        elif k == 4:
            fx = rf"\frac{{{g}+\ln x}}{{x}}"; e = f"({g}+log(x))/x"
            prob = f"គេឱ្យ $f(x)={fx}$ ដែល $x>0$ ។\n{l1}. គណនា $\\lim_{{x\\to 0^{{+}}}}f(x)$ ។\n{l2}. គណនា $\\lim_{{x\\to+\\infty}}f(x)$ ។\n{l3}. ទាញរកអាស៊ីមតូតឈរ និងអាស៊ីមតូតដេកនៃក្រាប ។"
            sol = [f"{l1}. កាលណា $x\\to 0^{{+}}$ ភាគយកខិតជិត $-\\infty$ ហើយ $\\frac{{1}}{{x}}\\to+\\infty$ ។ ដូច្នេះ $\\lim_{{x\\to 0^{{+}}}}f(x)=-\\infty$ ។",
                   f"{l2}. បំបែក ៖ " + D(rf"f(x)=\frac{{{g}}}{{x}}+\frac{{\ln x}}{{x}}"), f"ដោយ ${LNX}$ គេបាន $\\lim_{{x\\to+\\infty}}f(x)=0$ ។", f"{l3}. តាមលទ្ធផលទាំងពីរ ៖", "ដូចនេះ បន្ទាត់ $\\boxed{x=0}$ ជាអាស៊ីមតូតឈរ ហើយ $\\boxed{y=0}$ ជាអាស៊ីមតូតដេក ។"]
            ans = r"-\infty,\ 0"; ch = [check(f"limit({e},x,0,'+')", "-oo"), check(f"limit({e},x,oo)", "0")]
            f_ = lambda t, g=g: (g + np.log(t)) / t; dom = (0.02, 10); asy = None; pg = f"({g}+ln(x))/x"; vl = (); ax_ = None; yb = (-6, 6)
        else:
            fx = rf"{lin([(1,'x'),(b,'')])}-\ln x".replace("0-", "-"); e = f"x+({b})-log(x)"
            prob = f"គេឱ្យអនុគមន៍ $f(x)={fx}$ លើ $(0,+\\infty)$ ។\n{l1}. គណនា $\\lim_{{x\\to 0^{{+}}}}f(x)$ ។\n{l2}. គណនា $\\lim_{{x\\to+\\infty}}f(x)$ ។\n{l3}. គណនា $\\lim_{{x\\to+\\infty}}\\frac{{f(x)}}{{x}}$ ។"
            sol = [f"{l1}. កាលណា $x\\to 0^{{+}}$ គេមាន $-\\ln x\\to+\\infty$ ដូច្នេះ $\\lim_{{x\\to 0^{{+}}}}f(x)=+\\infty$ ។",
                   f"{l2}. មានរាងមិនកំណត់ $\\infty-\\infty$ ។ ដាក់ $x$ ជាកត្តា ៖ " + D(rf"f(x)=x\left(1{'+' if b>0 else ''}{'' if b==0 else rf'\frac{{{b}}}{{x}}'}-\frac{{\ln x}}{{x}}\right)".replace("{-", "{-")), "វង់ក្រចកខិតជិត $1$ ដូច្នេះ $\\lim_{x\\to+\\infty}f(x)=+\\infty$ ។",
                   f"{l3}. តាមការសរសេរខាងលើ $\\frac{{f(x)}}{{x}}$ គឺជាវង់ក្រចកនោះ ។", "ដូចនេះ $\\boxed{\\lim_{x\\to+\\infty}\\frac{f(x)}{x}=1}$ ។"]
            ans = r"+\infty,\ +\infty,\ 1"; ch = [check(f"limit({e},x,0,'+')", "oo"), check(f"limit({e},x,oo)", "oo"), check(f"limit(({e})/x,x,oo)", "1")]
            f_ = lambda t, b=b: t + b - np.log(t); dom = (0.02, 8); asy = None; pg = f"x+({b})-ln(x)"; vl = (); ax_ = None; yb = (-4, 10)
        if rid(prob) in {q["id"] for q in ROWS[-120:]}: continue
        fns = [(f_, "")] + ([(asy, "")] if asy else [])
        im = png(prob, lambda i: curve_png(i, fns, dom[0], dom[1], yb[0], yb[1], vl=vl))
        extra = (f"\\addplot[dashed,domain={dom[0]}:{dom[1]}] {{{ax_}}};\n" if ax_ else "")
        dia = [{"type": "graph", "latex": tikz_poles(pg, dom[0], dom[1], yb[0], yb[1], vl, extra), "image": im, "alt_km": "ក្រាបនៃ $f$ ជាមួយអាស៊ីមតូតដែលបានរកឃើញ ។"}]
        if add(mk("function_study_limits", "bacii", prob, "\n".join(sol), ans, ch, diagrams=dia)): n += 1

def continuity_rows(r):
    n = 0; tries = 0
    while n < 30 and tries < 800:
        tries += 1
        k = r.randint(0, 3); a, b = r.randint(2, 9), r.randint(2, 9)
        if k == 0:
            fx = rf"\frac{{\sin {a}x}}{{{b}x}}"; e = f"sin({a}*x)/({b}*x)"; v = Q(a, b)
        elif k == 1:
            fx = rf"\frac{{1-\cos {a}x}}{{x^{{2}}}}"; e = f"(1-cos({a}*x))/x**2"; v = Q(a * a, 2)
        elif k == 2:
            fx = rf"\frac{{e^{{{a}x}}-1}}{{{b}x}}"; e = f"(exp({a}*x)-1)/({b}*x)"; v = Q(a, b)
        else:
            fx = rf"\frac{{\ln(1+{a}x)}}{{\sin {b}x}}"; e = f"log(1+{a}*x)/sin({b}*x)"; v = Q(a, b)
        pc = rf"f(x)=\begin{{cases}}{fx} & x\neq 0\\ m & x=0\end{{cases}}"
        prob = r.choice([f"គេឱ្យអនុគមន៍កំណត់ជាផ្នែក $$ {pc} $$ រកតម្លៃ $m$ ដោយដឹងថា $f$ ជាប់ត្រង់ $x=0$ ។", f"គេឱ្យ $$ {pc} $$ កំណត់ $m$ ដើម្បីឱ្យ $f$ ជាអនុគមន៍ជាប់ត្រង់ $x=0$ ។"])
        st = [f"$f$ ជាប់ត្រង់ $x=0$ លុះត្រាតែ $\\lim_{{x\\to 0}}f(x)=f(0)$ ។ យើងមាន $f(0)=m$ ។", "គណនាលីមីត ៖",
              D(rf"\lim_{{x\to 0}}{fx}={L(v)}"), f"ព្រោះ " + {0: f"$\\frac{{\\sin {a}x}}{{{a}x}}\\to 1$ ហើយមេគុណគឺ $\\frac{{{a}}}{{{b}}}$ ។", 1: f"$\\frac{{1-\\cos u}}{{u^{{2}}}}\\to\\frac{{1}}{{2}}$ ជាមួយ $u={a}x$ ។", 2: f"$\\frac{{e^{{u}}-1}}{{u}}\\to 1$ ជាមួយ $u={a}x$ ហើយមេគុណគឺ $\\frac{{{a}}}{{{b}}}$ ។", 3: f"$\\frac{{\\ln(1+{a}x)}}{{x}}\\to {a}$ និង $\\frac{{\\sin {b}x}}{{x}}\\to {b}$ ។"}[k],
              f"លក្ខខណ្ឌ $\\Leftrightarrow m={L(v)}$ ។", f"ដូចនេះ $\\boxed{{m={L(v)}}}$ ។"]
        if add(mk("continuity_extension", "medium", prob, "\n".join(st), f"m={L(v)}", [check(f"limit({e},x,0)", str(v), "value of m")])): n += 1

def given_bound_rows(r):
    """Squeeze with a given double inequality (abstract f) and with a sketch."""
    n = 0; tries = 0
    while n < 40 and tries < 900:
        tries += 1
        k = r.randint(0, 3); a, b = r.randint(1, 7), r.randint(1, 7); g = r.randint(2, 6)
        if k == 0:
            prob = f"អនុគមន៍ $f$ ផ្ទៀងផ្ទាត់ $\\frac{{{g}x-{a}}}{{x+1}}\\le f(x)\\le\\frac{{{g}x+{b}}}{{x+1}}$ ចំពោះគ្រប់ $x>0$ ។ រក $\\lim_{{x\\to+\\infty}}f(x)$ ។"
            st = [f"កាលណា $x\\to+\\infty$ ប្រភាគនៅសងខាងមានលីមីតដូចគ្នា ៖", D(rf"\lim_{{x\to+\infty}}\frac{{{g}x-{a}}}{{x+1}}={g},\qquad\lim_{{x\to+\infty}}\frac{{{g}x+{b}}}{{x+1}}={g}"), f"ដោយ $f(x)$ នៅចន្លោះកន្សោមទាំងពីរ វាក៏ខិតជិត ${g}$ ដែរ ។", f"ដូចនេះ $\\boxed{{\\lim_{{x\\to+\\infty}}f(x)={g}}}$ ។"]
            ch = [check(f"limit(({g}*x-{a})/(x+1),x,oo)", str(g), "lower bound"), check(f"limit(({g}*x+{b})/(x+1),x,oo)", str(g), "upper bound")]; ans = str(g)
            dia = None
        elif k == 1:
            prob = f"គេដឹងថា $1-\\frac{{x^{{2}}}}{{2}}\\le\\cos x\\le 1$ ចំពោះគ្រប់ $x$ ។ ដោយប្រើវិសមភាពនេះ គណនា $\\lim_{{x\\to 0}}\\frac{{{a}(1-\\cos x)}}{{{g}x}}$ ។".replace("{1(", "{(")
            st = ["ពីវិសមភាពដែលឱ្យ យើងបាន $0\\le 1-\\cos x\\le\\frac{x^{2}}{2}$ ។", f"ចំពោះ $x>0$ ចែកនឹង ${g}x$ ហើយគុណនឹង ${a}$ ៖", D(rf"0\le\frac{{{a}(1-\cos x)}}{{{g}x}}\le\frac{{{a}x}}{{{2*g}}}"), "ចំពោះ $x<0$ សញ្ញាវិសមភាពប្តូរ ប៉ុន្តែអង្គទាំងពីរនៅតែខិតជិត $0$ ។", "កាលណា $x\\to 0$ អង្គសងខាងខិតជិត $0$ ។", f"ដូចនេះ លីមីតស្មើ $\\boxed{{0}}$ ។"]
            ch = [check(f"limit({a}*(1-cos(x))/({g}*x),x,0)", "0"), check(f"limit({a}*x/{2*g},x,0)", "0", "upper bound")]; ans = "0"; dia = None
        elif k == 2:
            prob = f"អនុគមន៍ $g$ ផ្ទៀងផ្ទាត់ $|g(x)-{a}|\\le {b}x^{{2}}$ ចំពោះគ្រប់ $x$ ជិត $0$ ។ រក $\\lim_{{x\\to 0}}g(x)$ រួចគណនា $\\lim_{{x\\to 0}}\\frac{{g(x)\\sin {g}x}}{{x}}$ ។"
            st = [f"វិសមភាពសរសេរបានថា ${a}-{b}x^{{2}}\\le g(x)\\le {a}+{b}x^{{2}}$ ។", f"អង្គសងខាងខិតជិត ${a}$ កាលណា $x\\to 0$ ដូច្នេះ $\\lim_{{x\\to 0}}g(x)={a}$ ។", "បន្ទាប់មកប្រើប្រមាណវិធីលើលីមីត ៖", D(rf"\lim_{{x\to 0}}\frac{{g(x)\sin {g}x}}{{x}}=\lim_{{x\to 0}}g(x)\cdot\lim_{{x\to 0}}\frac{{\sin {g}x}}{{x}}={a}\cdot {g}"), f"ដូចនេះ $\\boxed{{\\lim_{{x\\to 0}}g(x)={a}}}$ និង លីមីតទីពីរស្មើ $\\boxed{{{a*g}}}$ ។"]
            ch = [check(f"limit({a}-{b}*x**2,x,0)", str(a), "lower bound"), check(f"limit({a}+{b}*x**2,x,0)", str(a), "upper bound"), check(f"limit({a}*sin({g}*x)/x,x,0)", str(a * g), "second limit, g replaced by its limit")]; ans = rf"{a},\ {a*g}"; dia = None
        else:
            prob = f"បង្ហាញថា ចំពោះ $x>0$ គេមាន $\\frac{{{g}x-1}}{{x}}\\le\\frac{{{g}x+\\sin x}}{{x}}\\le\\frac{{{g}x+1}}{{x}}$ ។ ទាញរក $\\lim_{{x\\to+\\infty}}\\frac{{{g}x+\\sin x}}{{x}}$ ។"
            st = [f"ដោយ $-1\\le\\sin x\\le 1$ បូក ${g}x$ រួចចែកនឹង $x>0$ យើងបានវិសមភាពដែលត្រូវបង្ហាញ ។", D(rf"\frac{{{g}x-1}}{{x}}={g}-\frac{{1}}{{x}},\qquad\frac{{{g}x+1}}{{x}}={g}+\frac{{1}}{{x}}"), f"កាលណា $x\\to+\\infty$ អង្គទាំងពីរខិតជិត ${g}$ ។", f"ដូចនេះ $\\boxed{{\\lim_{{x\\to+\\infty}}\\frac{{{g}x+\\sin x}}{{x}}={g}}}$ ។"]
            ch = [check(f"limit(({g}*x+sin(x))/x,x,oo)", str(g)), check(f"limit(({g}*x-1)/x,x,oo)", str(g), "lower bound"), check(f"limit(({g}*x+1)/x,x,oo)", str(g), "upper bound")]; ans = str(g)
            im = png(prob, lambda i: curve_png(i, [(lambda t, g=g: (g * t + np.sin(t)) / t, "$y=f(x)$"), (lambda t, g=g: g + 1 / t, f"$y={g}\\pm\\frac{{1}}{{x}}$"), (lambda t, g=g: g - 1 / t, "")], 0.3, 30, g - 2, g + 2, hl=(g,)))
            dia = [{"type": "graph", "latex": tikz_graph(f"{g}+sin(deg(x))/x", 1, 30, g - 2, g + 2, f"\\addplot[dashed,domain=1:30] {{{g}+1/x}};\n\\addplot[dashed,domain=1:30] {{{g}-1/x}};\n"), "image": im, "alt_km": "ក្រាបនៅចន្លោះខ្សែកោងពីរដែលខិតជិតបន្ទាត់ដេកតែមួយ ។"}]
        if add(mk("squeeze_given_inequality", "medium", prob, "\n".join(st), ans, ch, diagrams=dia)): n += 1

def main():
    for f in glob.glob(os.path.join(ROOT, "diagrams", TOPIC + "-*.png")):
        os.remove(f)
    r = random.Random(20261105)
    from limit_transcendental_hand import hand_rows
    for h in hand_rows(): add(h)
    study_rows(r); given_bound_rows(r)
    single_rows(r); multi_rows(r); two_method_rows(r); param_rows(r); identity_rows(r); continuity_rows(r)
    r.shuffle(ROWS)
    finish_rows(ROWS)
    write_jsonl(ROWS, "limit/transcendental.jsonl")
    from collections import Counter
    print(Counter(q["grade"] for q in ROWS), Counter(q["difficulty"] for q in ROWS), "png", N_PNG[0])
    print(Counter(q["subtopic"] for q in ROWS).most_common())

if __name__ == "__main__":
    main()
