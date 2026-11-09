"""Generator: topic 'variation' (monotonicity, sign tables, extrema, inflection, inequalities,
number of solutions). Writes out/variation.jsonl. Text uses token § for the function name."""
import random, sys, os, re, time, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from common import make_row as _make_row
from variation_hand import tidy_row
GLOBAL_SUBS = {"extrema_on_closed_interval", "inequality_proof", "two_step_auxiliary_function", "local_extrema_word_problem", "monotonicity_word_problem"}
def make_row(topic, sub, *a, **k):
    """Extrema are local unless the row proves a global bound, so they are labelled ធៀប."""
    return tidy_row(_make_row(topic, sub, *a, **k), local=sub not in GLOBAL_SUBS)
GEN = "variation"
rng = random.Random(20261105)
oo = sp.oo; R = sp.Rational; ln = sp.log; ex = sp.exp; sq = sp.sqrt; pi = sp.pi
ch = rng.choice

# ---------- LaTeX helpers ----------
def L(e):
    t = lx(e) if not isinstance(e, str) else e
    def fix(mo):
        fn, arg, nxt = mo.group(1), mo.group(2).strip(), mo.group(3)
        arg = arg.replace(" + ", "+").replace(" - ", "-")
        simple = re.fullmatch(r"[0-9]*\s*x|[0-9]+", arg) is not None
        body = f"\\{fn} {arg}" if simple else f"\\{fn}({arg})"
        return (f"({body})" + nxt) if nxt == "^" else body + nxt
    t = re.sub(r"\\(ln|sin|cos|tan|cot)\{\\left\(((?:(?!\\right).)*?) \\right\)\}(\^?)", fix, t)
    t = re.sub(r"\\(sin|cos)\^\{2\}\{\\left\(x \\right\)\}", r"\\\1^{2}x", t)
    return t.replace("{- ", "{-")

def LT(v):
    return "+\\infty" if v == oo else "-\\infty" if v == -oo else L(v)

def itv(a, b, lc=False, hc=False):
    return ("[" if lc else "(") + LT(a) + ";" + LT(b) + ("]" if hc else ")")

def P(c, roots, tail=None):
    """c*prod (x-r)^k -> (tex, python str). tail=(tex,str) multiplies at the end."""
    tx = "" if c == 1 else "-" if c == -1 else L(c)
    st = f"({c})"
    for r, k in roots:
        b = "x" if r == 0 else "(" + L(x - r).replace(" ", "") + ")"
        tx += b + (f"^{{{k}}}" if k > 1 else "")
        st += f"*(x-({r}))**{k}"
    if tail:
        tx += tail[0]; st += "*" + tail[1]
    return tx, st

def frac(ntx, nst, dtx, dst):
    return "\\frac{" + ntx + "}{" + dtx + "}", f"({nst})/({dst})"

# ---------- phrase pools ----------
STEM = ["គេឲ្យអនុគមន៍", "គេមានអនុគមន៍", "ឲ្យអនុគមន៍", "គេពិនិត្យអនុគមន៍", "គេសិក្សាអនុគមន៍", "គេអោយអនុគមន៍"]
STEM = STEM[:5]
GOT = ["យើងបាន៖", "គេបាន៖", "នោះ៖", "យើងទទួលបាន៖"]
CONC = ["ដូចនេះ", "ដូចនេះ", "ដូចនេះ", "សរុបមក", "ជាសន្និដ្ឋាន"]
RULE = {
 "poly": ["តាមរូបមន្ត $(x^n)'=nx^{n-1}$ ", "ដេរីវេនៃពហុធាគណនាតាមតួនីមួយៗ ", "ប្រើរូបមន្ត $(x^n)'=nx^{n-1}$ និង $(u+v)'=u'+v'$ ", "គណនាដេរីវេទី១ "],
 "quot": ["តាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ ", "ប្រើរូបមន្តដេរីវេនៃផលចែក ", "គណនាដេរីវេទី១តាមរូបមន្តផលចែក $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ "],
 "prod": ["តាមរូបមន្ត $(uv)'=u'v+uv'$ ", "ប្រើរូបមន្តដេរីវេនៃផលគុណ ", "គណនាដេរីវេទី១តាមរូបមន្តផលគុណ $(uv)'=u'v+uv'$ "],
 "chain": ["តាមរូបមន្តដេរីវេនៃអនុគមន៍បណ្ដាក់ ", "ប្រើដេរីវេនៃអនុគមន៍បណ្ដាក់ ", "គណនាដេរីវេទី១ដោយប្រើអនុគមន៍បណ្ដាក់ "],
 "ln": ["តាមរូបមន្ត $(\\ln x)'=\\frac{1}{x}$ ", "ដោយ $(\\ln x)'=\\frac{1}{x}$ ", "គណនាដេរីវេទី១ ដោយចាំថា $(\\ln x)'=\\frac{1}{x}$ "],
 "exp": ["តាមរូបមន្ត $(e^{u})'=u'e^{u}$ ", "ដោយ $(e^{u})'=u'e^{u}$ ", "គណនាដេរីវេទី១ ដោយប្រើ $(e^{u})'=u'e^{u}$ "],
 "sqrt": ["តាមរូបមន្ត $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ ", "ដោយប្រើ $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ "],
 "trig": ["តាមរូបមន្ត $(\\sin x)'=\\cos x$ និង $(\\cos x)'=-\\sin x$ ", "ដោយ $(\\sin x)'=\\cos x$ និង $(\\cos x)'=-\\sin x$ "],
}
def dom_R():
    return ch(["អនុគមន៍ $§$ មានដែនកំណត់ $D=IR$ ។", "$§$ កំណត់ចំពោះគ្រប់ $x\\in IR$ ដូចនេះ $D=IR$ ។",
               "ដែនកំណត់៖ $D=IR$ ។", "ដោយ $§(x)$ មានន័យគ្រប់ $x$ ពិត នោះ $D=IR$ ។"])
def dom_ex(den, v):
    return ch([f"$§(x)$ មានន័យលុះត្រាតែ ${den}\\neq 0$ ឬ $x\\neq {L(v)}$ ។ ដូចនេះ $D=IR-\\{{{L(v)}\\}}$ ។",
               f"អនុគមន៍កំណត់លុះត្រាតែភាគបែង ${den}\\neq 0$ ។ នោះ $D=IR-\\{{{L(v)}\\}}$ ។",
               f"ដែនកំណត់៖ $§$ កំណត់កាលណា $x\\neq {L(v)}$ ដូចនេះ $D=IR-\\{{{L(v)}\\}}$ ។"])
def dom_c(cond, D):
    return ch([f"$§(x)$ មានន័យលុះត្រាតែ ${cond}$ ។ ដូចនេះ $D={D}$ ។", f"អនុគមន៍កំណត់លុះត្រាតែ ${cond}$ នោះ $D={D}$ ។",
               f"ដែនកំណត់៖ លក្ខខណ្ឌ ${cond}$ ឲ្យ $D={D}$ ។"])

def F(f, rule, steps, dtex, dstr, crit, dom=None, domtext=None, roots="", sign="", fam="", diff="medium",
      excl=(), lo=-oo, hi=oo, lc=False, hc=False, endzero=False, asym=(), given_dom=None, canon=None):
    return dict(f=f, rule=rule, steps=steps, dtex=dtex, dstr=dstr, crit=sorted(crit, key=lambda v: float(v)),
                domtext=domtext or dom_R(), roots=roots, sign=sign, fam=fam, diff=diff, excl=tuple(excl), lo=lo, hi=hi,
                lc=lc, hc=hc, asym=asym, given_dom=given_dom, canon=canon)

def quad_text(A, B, C, p, q):
    """Sentence solving A x^2+B x+C=0 with known roots p,q (A,B,C possibly rational)."""
    eq = L(A*x**2 + B*x + C)
    v = rng.random()
    if p == q:
        return f"សមីការ ${eq}=0$ មានឫសឌុប $x={L(p)}$ ។"
    pp, qq = (p, q) if float(p) < float(q) else (q, p)
    if v < 0.45:
        D = B**2 - 4*A*C
        sD = sq(D)
        return (f"ដោះស្រាយ ${eq}=0$ ។ យើងមាន $\\Delta=({L(B)})^2-4({L(A)})({L(C)})={L(D)}$ ។ "
                f"សមីការមានឫសពីរ $x_1={L(pp)}$ និង $x_2={L(qq)}$ ។")
    if v < 0.75:
        return f"បើ §$'(x)=0$ នោះ ${eq}=0$ ឲ្យ $x={L(pp)}$ ឬ $x={L(qq)}$ ។".replace("§$'", "$§'")
    return f"ឫសនៃ ${eq}=0$ គឺ $x_1={L(pp)}$ និង $x_2={L(qq)}$ ។"

ZERO = ["បើ $§'(x)=0$ នោះ ", "សមីការ $§'(x)=0$ ឲ្យ ", "ដោះស្រាយ $§'(x)=0$ គេបាន ", "$§'(x)=0$ លុះត្រាតែ "]
def zt(vals):
    return ch(ZERO) + " ឬ ".join(f"$x={L(v)}$" for v in vals) + " ។"

# ---------- families ----------
def Fa_cubic():
    a = ch([1, -1, 2, -2, 3, -3, 1, -1]); p, q = sorted(rng.sample(range(-4, 6), 2)); d = rng.randint(-6, 6)
    if (3*a*(p+q)) % 2: return None
    f = a*x**3 - R(3, 2)*a*(p+q)*x**2 + 3*a*p*q*x + d
    A, B, C = 3*a, -3*a*(p+q), 3*a*p*q
    tx, st = P(3*a, [(p, 1), (q, 1)])
    return F(f, "poly", [L(A*x**2+B*x+C)], tx, st, [p, q], roots=quad_text(R(A), R(B), R(C), R(p), R(q)),
             sign=ch([f"$§'(x)$ ជាត្រីធាដឺក្រេទីពីរ ដែលមានសញ្ញាដូចមេគុណ ${L(A)}$ នៅក្រៅឫស និងផ្ទុយសញ្ញានៅចន្លោះឫស ។", ""]),
             fam="cubic", diff=ch(["easy", "medium"]))
def Fa_cubic_frac():
    a = ch([1, -1, 2, -2, 3, 6]); p, q = sorted(rng.sample(range(-5, 7), 2)); d = rng.randint(-4, 5)
    f = R(a, 3)*x**3 - R(a, 2)*(p+q)*x**2 + a*p*q*x + d
    A, B, C = a, -a*(p+q), a*p*q
    tx, st = P(a, [(p, 1), (q, 1)])
    return F(f, "poly", [L(A*x**2+B*x+C)], tx, st, [p, q], roots=quad_text(R(A), R(B), R(C), R(p), R(q)), fam="cubic_frac", diff="easy")
def Fa_cubic_mono():
    a = ch([1, -1, 2, -2]); p = rng.randint(-3, 3); k = rng.randint(0, 4); d = rng.randint(-5, 5)
    f = sp.expand(a*((x-p)**3 + 3*k*(x-p))) + d
    if k == 0:
        tx, st = P(3*a, [(p, 2)])
        return F(f, "poly", [L(sp.expand(sp.diff(f, x)))], tx, st, [p], roots=f"$§'(x)=0$ មានឫសឌុប $x={p}$ ។",
                 sign=f"ដោយ ${tx.replace(L(3*a), '', 1) if abs(a)!=0 else tx}$ មិនអវិជ្ជមានឡើយ នោះ $§'(x)$ មានសញ្ញាដូច ${3*a}$ ។".replace("$-", "$") if False else "", fam="cubic_dbl")
    dd = sp.expand(sp.diff(f, x))
    tx = L(3*a) + "\\left[" + L((x-p)**2) + f"+{k}\\right]"
    return F(f, "poly", [L(dd)], tx, f"{3*a}*((x-({p}))**2+{k})", [],
             sign=ch([f"ដោយ ${L((x-p)**2)}+{k}>0$ ជានិច្ច នោះ $§'(x)$ មានសញ្ញាដូច ${3*a}$ ។", f"គេឃើញថា $§'(x)$ មិនអាចស្មើសូន្យទេ ព្រោះ ${L((x-p)**2)}+{k}\\geq {k}$ ។"]),
             fam="cubic_mono")
def Fa_biq():
    a = ch([1, -1, 2, -2, R(1, 2), R(1, 4)]); k = rng.randint(1, 4); d = rng.randint(-6, 6)
    f = a*x**4 - 2*a*k**2*x**2 + d
    tx, st = P(4*a, [(-k, 1), (0, 1), (k, 1)])
    return F(f, "poly", [L(sp.diff(f, x)), L(4*a) + "x(x^2-" + str(k*k) + ")"], tx, st, [-k, 0, k], roots=zt([-k, 0, k]), fam="biquadratic")
def Fa_quartic():
    a = ch([1, -1, 3, -3, R(1, 4), R(3, 4)]); r = sorted(rng.sample(range(-4, 5), 3)); d = rng.randint(-5, 5)
    e1, e2, e3 = sum(r), r[0]*r[1]+r[0]*r[2]+r[1]*r[2], r[0]*r[1]*r[2]
    f = a*(x**4 - R(4, 3)*e1*x**3 + 2*e2*x**2 - 4*e3*x) + d
    if any(c.q > 4 for c in sp.Poly(f, x).coeffs()): return None
    tx, st = P(4*a, [(v, 1) for v in r])
    return F(f, "poly", [L(sp.diff(f, x))], tx, st, r, roots=zt(r), fam="quartic", diff="hard")
def Fa_quartic_dbl():
    a = ch([1, -1, 2, R(1, 2)]); p = ch([-3, -2, -1, 1, 2, 3]); d = rng.randint(-5, 5)
    f = a*(3*x**4 - 4*p*x**3) + d
    tx, st = P(12*a, [(0, 2), (p, 1)])
    return F(f, "poly", [L(sp.diff(f, x))], tx, st, [0, p], roots=zt([0, p]),
             sign=f"ដោយ $x^2\\geq 0$ នោះ $§'(x)$ មានសញ្ញាអាស្រ័យនឹង ${L(12*a)}(x{-p:+d})$ ។", fam="quartic_dbl", diff="hard")
def Fa_quintic():
    k = rng.randint(1, 3); a = ch([1, -1, 2]); d = rng.randint(-4, 4)
    f = a*(3*x**5 - 5*k**2*x**3) + d
    tx, st = P(15*a, [(-k, 1), (0, 2), (k, 1)])
    return F(f, "poly", [L(sp.diff(f, x))], tx, st, [-k, 0, k], roots=zt([-k, 0, k]), fam="quintic", diff="hard")
def Fa_homog():
    a, b, c, d = ch([1, 2, 3, -1, -2, 4]), rng.randint(-6, 6), ch([1, 1, 2, -1]), rng.randint(-5, 5)
    D = a*d - b*c
    if D == 0 or d == 0 and b == 0: return None
    v = R(-d, c); den = L(c*x+d); num = L(a*x+b)
    f = (a*x+b)/(c*x+d)
    return F(f, "quot", [f"\\frac{{{a}({den})-({L(c)})({num})}}{{({den})^2}}"], f"\\frac{{{D}}}{{({den})^2}}", f"({D})/({c}*x+({d}))**2", [],
             domtext=dom_ex(den, v), excl=[v],
             sign=ch([f"ដោយ $({den})^2>0$ ចំពោះគ្រប់ $x\\in D$ នោះ $§'(x)$ មានសញ្ញាដូច ${D}$ ។", f"ភាគបែងវិជ្ជមានជានិច្ច ដូច្នេះសញ្ញានៃ $§'(x)$ យកតាមភាគយក ${D}$ ។"]),
             fam="homographic", diff="easy", asym=[("v", v), ("h", R(a, c))])
def Fa_slant():
    a = ch([1, 1, 2, -1, -2, R(1, 2)]); c = rng.randint(-4, 4); al = rng.randint(-4, 4); k = rng.randint(1, 4)
    be = a*k*k if rng.random() < .8 else -a*k
    N = sp.expand((a*x+al)*(x+c) + be); den = x + c; f = N/den; denL = L(den)
    v = -c
    can = L(a*x+al) + ("+" if be > 0 else "-") + "\\frac{" + L(abs(be)) + "}{" + denL + "}"
    if a*be > 0:
        tx = frac(*P(a, [(v-k, 1), (v+k, 1)]), f"({denL})^2", f"(x+({c}))**2")
        return F(f, "quot", [f"{L(a)}{'-' if be>0 else '+'}\\frac{{{L(abs(be))}}}{{({denL})^2}}"], tx[0], tx[1], [v-k, v+k], domtext=dom_ex(denL, v), excl=[v],
                 roots=zt([v-k, v+k]), sign=f"ដោយ $({denL})^2>0$ នោះ $§'(x)$ មានសញ្ញាដូចភាគយក ។", fam="slant", diff="medium",
                 asym=[("v", v), ("s", a*x+al)], canon=can)
    t = sp.expand(a*(x+c)**2 - be)
    return F(f, "quot", [f"{L(a)}{'+' if be<0 else '-'}\\frac{{{L(abs(be))}}}{{({denL})^2}}"], f"\\frac{{{L(t)}}}{{({denL})^2}}", f"({t})/(x+({c}))**2", [], domtext=dom_ex(denL, v), excl=[v],
             sign=f"គេឃើញថា $§'(x)$ ជាផលបូកនៃចំនួនដែលមានសញ្ញាដូច ${L(a)}$ ទាំងអស់ ដូចនេះ $§'(x)$ មិនប្ដូរសញ្ញាលើ $D$ ទេ ។", fam="slant_mono", asym=[("v", v), ("s", a*x+al)], canon=can)
def Fa_bump():
    a = ch([1, 2, -1, -2, 3, 4]); p = -rng.randint(1, 4); q = rng.randint(1, 4)
    if (a*(p+q)) % 2: return None
    c = -p*q; b = -R(a, 2)*(p+q); f = (a*x+b)/(x**2+c)
    n = -a*(x-p)*(x-q); nt, ns = P(-a, [(p, 1), (q, 1)])
    tx = frac(nt, ns, f"(x^2+{c})^2", f"(x**2+{c})**2")
    return F(f, "quot", [f"\\frac{{{a}(x^2+{c})-2x({L(a*x+b)})}}{{(x^2+{c})^2}}", f"\\frac{{{L(sp.expand(n))}}}{{(x^2+{c})^2}}"], tx[0], tx[1], [p, q],
             domtext=ch([f"ដោយ $x^2+{c}>0$ ជានិច្ច នោះ $D=IR$ ។", f"ភាគបែង $x^2+{c}$ មិនស្មើសូន្យទេ ដូចនេះ $D=IR$ ។"]),
             roots=zt([p, q]), sign=ch(["ភាគបែងវិជ្ជមានជានិច្ច ដូច្នេះ $§'(x)$ យកសញ្ញាតាមភាគយក ។", "$§'(x)$ មានសញ្ញាអាស្រ័យនឹងភាគយក ។"]), fam="bump", diff="medium", asym=[("h", 0)])
def Fa_even_rat():
    a = ch([1, 2, 3, -1, -2, 4]); k = rng.randint(1, 9); d = rng.randint(-4, 4)
    N = sp.expand(d*(x**2+k) + a*x**2); f = N/(x**2+k)
    tx = frac(*P(2*a*k, [(0, 1)]), f"(x^2+{k})^2", f"(x**2+{k})**2")
    return F(f, "quot", [f"\\frac{{{L(2*(a+d)*x)}(x^2+{k})-2x({L(N)})}}{{(x^2+{k})^2}}"], tx[0], tx[1], [0],
             domtext=f"ដោយ $x^2+{k}>0$ ជានិច្ច នោះ $D=IR$ ។", roots=zt([0]), sign="$§'(x)$ មានសញ្ញាអាស្រ័យនឹងភាគយក ។", fam="even_rat", asym=[("h", a+d)])
def Fa_x_over_x2():
    a = ch([1, 2, 3, 4, -1, -2]); k = rng.randint(1, 5); d = rng.randint(-3, 3)
    f = a*x/(x**2+k*k) + d
    tx = frac(*P(-a, [(-k, 1), (k, 1)]), f"(x^2+{k*k})^2", f"(x**2+{k*k})**2")
    return F(f, "quot", [f"\\frac{{{a}(x^2+{k*k})-{L(2*a)}x^2}}{{(x^2+{k*k})^2}}"], tx[0], tx[1], [-k, k],
             domtext=f"ភាគបែង $x^2+{k*k}$ វិជ្ជមានជានិច្ច ដូចនេះ $D=IR$ ។", roots=zt([-k, k]), sign="$§'(x)$ យកសញ្ញាតាមភាគយក ។", fam="x_over_x2", asym=[("h", d)])
def Fa_expl():
    k = ch([1, -1, 1, -1, 2, -2]); a = ch([1, 2, -1, -2, 3, 4]); x0 = rng.randint(-3, 3)
    b = -R(a, k) - a*x0
    if b.q != 1: return None
    f = (a*x+b)*ex(k*x); ek = L(ex(k*x))
    tx, st = P(k*a, [(x0, 1)], (ek, f"exp({k}*x)"))
    return F(f, "prod", [f"{a}{ek}+({L(k)})({L(a*x+b)}){ek}"], tx, st, [x0],
             roots=zt([x0]), sign=ch([f"ដោយ ${ek}>0$ ជានិច្ច នោះ $§'(x)$ មានសញ្ញាដូច ${L(k*a*(x-x0))}$ ។", f"$§'(x)$ យកសញ្ញាតាម ${L(k*a*(x-x0))}$ ព្រោះ ${ek}>0$ ។"]), fam="exp_lin", diff=ch(["medium", "bacii"]))
def Fa_expq():
    k = ch([1, -1]); p, q = sorted(rng.sample(range(-4, 5), 2))
    if k == 1: b = -(p+q)-2; c = p*q - b
    else: b = 2-(p+q); c = p*q + b
    g = x**2+b*x+c; f = g*ex(k*x); ek = L(ex(k*x))
    tx, st = P(k, [(p, 1), (q, 1)], (ek, f"exp({k}*x)"))
    return F(f, "prod", [f"({L(2*x+b)}){ek}+({L(k)})({L(g)}){ek}"], tx, st, [p, q], roots=zt([p, q]),
             sign=f"ដោយ ${ek}>0$ ជានិច្ច នោះ $§'(x)$ មានសញ្ញាដូច ${L(sp.expand(k*(x-p)*(x-q)))}$ ។", fam="exp_quad", diff="bacii")
def Fa_explinsum():
    a = rng.randint(1, 9); b = rng.randint(-5, 5); s_ = ch([1, 1, -1])
    f = s_*(ex(x) - a*x) + b; c = ln(a)
    return F(f, "exp", [], L(s_*ex(x)) + "".join([f"{-s_*a:+d}"]), f"({s_})*exp(x)+({-s_*a})", [c], roots=(f"$§'(x)=0$ ឲ្យ $e^{{x}}={a}$ នោះ $x={L(c)}$ ។" if a > 1 else "$§'(x)=0$ ឲ្យ $e^{x}=1$ នោះ $x=0$ ។"), fam="exp_minus_lin", diff="medium")
def Fa_exp2():
    a = rng.randint(1, 6); b = rng.randint(-5, 5)
    f = ex(2*x) - 2*a*ex(x) + b; c = ln(a)
    return F(f, "exp", [f"2e^{{2x}}-{2*a}e^{{x}}"], f"2e^{{x}}(e^{{x}}-{a})", f"2*exp(x)*(exp(x)-{a})", [c], roots=f"ដោយ $e^{{x}}>0$ នោះ $§'(x)=0$ ឲ្យ $e^{{x}}={a}$ ឬ $x={L(c)}$ ។",
             sign=f"$§'(x)$ មានសញ្ញាដូច $e^{{x}}-{a}$ ។", fam="exp_square", diff="bacii")
def Fa_cosh():
    a = rng.randint(1, 4); k = rng.randint(1, 4); b = a*k*k; d = rng.randint(-3, 3)
    f = a*ex(x) + b*ex(-x) + d; c = ln(k)
    return F(f, "exp", [f"{a if a>1 else ''}e^{{x}}-{b if b>1 else ''}e^{{-x}}"], f"\\frac{{{a if a>1 else ''}e^{{2x}}-{b}}}{{e^{{x}}}}", f"({a}*exp(2*x)-{b})/exp(x)", [c],
             roots=f"$§'(x)=0$ ឲ្យ $e^{{2x}}={k*k}$ ឬ $e^{{x}}={k}$ នោះ $x={L(c)}$ ។", sign="ដោយ $e^{x}>0$ សញ្ញានៃ $§'(x)$ យកតាមភាគយក ។", fam="cosh_like", diff="bacii")
POS = dict(lo=sp.Integer(0))
def dpos():
    return ch(["$§(x)$ មានន័យលុះត្រាតែ $x>0$ ។ ដូចនេះ $D=(0;+\\infty)$ ។", "ដោយ $\\ln x$ កំណត់ចំពោះ $x>0$ នោះ $D=(0;+\\infty)$ ។", "ដែនកំណត់៖ $D=(0;+\\infty)$ ។"])
def Fa_lnlin():
    a = ch([1, 1, 2, 3, R(1, 2)]); c = rng.randint(1, 8); b = rng.randint(-5, 5); s_ = ch([1, 1, -1])
    x0 = c/R(a); f = s_*(a*x - c*ln(x)) + b
    n = L(s_*a*x - s_*c)
    return F(f, "ln", [f"{L(s_*a)}{'-' if s_>0 else '+'}\\frac{{{c}}}{{x}}"], f"\\frac{{{n}}}{{x}}", f"({s_*a}*x-({s_*c}))/x", [x0], domtext=dpos(), lo=sp.Integer(0),
             roots=zt([x0]), sign=f"ដោយ $x>0$ នៅលើ $D$ នោះ $§'(x)$ មានសញ្ញាដូច ${n}$ ។", fam="ln_lin")
def Fa_x2ln():
    k = rng.randint(1, 4); a = ch([1, 2, 3]); b = rng.randint(-5, 5)
    f = a*x**2 - 2*a*k*k*ln(x) + b
    t = frac(*P(2*a, [(-k, 1), (k, 1)]), "x", "x")
    return F(f, "ln", [f"{L(2*a*x)}-\\frac{{{2*a*k*k}}}{{x}}"], t[0], t[1], [sp.Integer(k)], domtext=dpos(), lo=sp.Integer(0),
             roots=f"លើ $D$ គេបាន $§'(x)=0$ ឲ្យ $x={k}$ (បដិសេធ $x=-{k}$ ព្រោះមិននៅក្នុង $D$) ។", sign=f"ដោយ $x>0$ និង $x+{k}>0$ នោះ $§'(x)$ មានសញ្ញាដូច $x-{k}$ ។", fam="x2_ln", diff="bacii")
def Fa_xlnx():
    n = rng.randint(-2, 3); a = ch([1, 2, 3, -1]); d = rng.randint(-3, 3)
    f = a*(x*ln(x) - n*x) + d; c = ex(n-1)
    tx = f"{L(a) if abs(a)!=1 else ('-' if a<0 else '')}(\\ln x{1-n:+d})" if n != 1 else f"{L(a) if abs(a)!=1 else ('-' if a<0 else '')}\\ln x"
    return F(f, "prod", [], tx, f"{a}*(log(x)+({1-n}))", [c], domtext=dpos(), lo=sp.Integer(0), roots=f"$§'(x)=0$ ឲ្យ $\\ln x={n-1}$ នោះ $x={L(c)}$ ។",
             sign="ដោយ $\\ln x$ ជាអនុគមន៍កើន យើងកំណត់សញ្ញានៃ $§'(x)$ បានភ្លាម ។", fam="x_ln_x", diff="bacii")
def Fa_lnoverx():
    a = ch([1, 2, 3, -1, -2]); n = rng.randint(-1, 3); b = a*(1-n); f = (a*ln(x)+b)/x; c = ex(n)
    nt = L(-a*ln(x)+a*n)
    return F(f, "quot", [f"\\frac{{\\frac{{{a}}}{{x}}\\cdot x-({L(a*ln(x)+b)})}}{{x^2}}"], f"\\frac{{{nt}}}{{x^2}}", f"({-a}*log(x)+({a*n}))/x**2", [c], domtext=dpos(), lo=sp.Integer(0),
             roots=f"$§'(x)=0$ ឲ្យ $\\ln x={n}$ នោះ $x={L(c)}$ ។", sign=f"ដោយ $x^2>0$ នោះ $§'(x)$ មានសញ្ញាដូច ${nt}$ ។", fam="ln_over_x", diff="bacii", asym=[("v", 0), ("h", 0)])
def Fa_ln2():
    a = ch([1, 2, -1]); n = rng.randint(-3, 3); b = -2*a*n; d = rng.randint(-3, 3)
    f = a*ln(x)**2 + b*ln(x) + d; c = ex(n)
    nt = L(2*a*ln(x) + b)
    return F(f, "chain", [], f"\\frac{{{nt}}}{{x}}", f"({2*a}*log(x)+({b}))/x", [c], domtext=dpos(), lo=sp.Integer(0), roots=f"$§'(x)=0$ ឲ្យ $\\ln x={n}$ នោះ $x={L(c)}$ ។",
             sign=f"ដោយ $x>0$ នោះ $§'(x)$ យកសញ្ញាតាម ${nt}$ ។", fam="ln_squared", diff="bacii")
def Fa_lnquad():
    a = ch([1, 2, 3]); h = rng.randint(-4, 4); k = rng.randint(1, 6); d = rng.randint(-3, 3); s_ = ch([1, -1])
    g = sp.expand((x-h)**2+k); f = s_*a*ln(g) + d
    nt, ns = P(2*a*s_, [(h, 1)])
    t = frac(nt, ns, L(g), str(g))
    return F(f, "chain", [], t[0], t[1], [sp.Integer(h)], domtext=f"ដោយ ${L(g)}=({L(x-h)})^2+{k}>0$ ចំពោះគ្រប់ $x$ នោះ $D=IR$ ។", roots=zt([h]), sign="ភាគបែងវិជ្ជមានជានិច្ច ដូច្នេះ $§'(x)$ មានសញ្ញាដូចភាគយក ។", fam="ln_quad", diff="bacii")
def Fa_xminusln():
    a = rng.randint(-3, 4); b = ch([1, 2, 3]); c = 1 - R(b)*0 - a if False else None
    x0 = b - a  # f = x - b ln(x+a), f' = (x+a-b)/(x+a)
    d = rng.randint(-3, 3); f = x - b*ln(x+a) + d; den = L(x+a)
    return F(f, "ln", [f"1-\\frac{{{b}}}{{{den}}}"], f"\\frac{{{L(x-x0)}}}{{{den}}}", f"(x-({x0}))/(x+({a}))", [sp.Integer(x0)], domtext=dom_c(f"{den}>0", f"({-a};+\\infty)"), lo=sp.Integer(-a),
             roots=zt([x0]), sign=f"ដោយ ${den}>0$ នៅលើ $D$ នោះ $§'(x)$ មានសញ្ញាដូច ${L(x-x0)}$ ។", fam="x_minus_ln")
def Fa_xsqrt():
    k = rng.randint(1, 5); a = 3*k; s_ = ch([1, 1, -1]); f = s_*x*sq(a-x)
    c = sp.Integer(2*k); nt = L(s_*(2*a-3*x))
    return F(f, "sqrt", [f"{'-' if s_<0 else ''}\\left(\\sqrt{{{a}-x}}-\\frac{{x}}{{2\\sqrt{{{a}-x}}}}\\right)"], f"\\frac{{{nt}}}{{2\\sqrt{{{a}-x}}}}", f"({s_}*({2*a}-3*x))/(2*sqrt({a}-x))", [c],
             domtext=dom_c(f"{a}-x\\geq 0", f"(-\\infty;{a}]"), hi=sp.Integer(a), hc=True, roots=zt([c]), sign=f"ចំពោះ $x<{a}$ ភាគបែងវិជ្ជមាន ដូចនេះ $§'(x)$ មានសញ្ញាដូចភាគយក ។", fam="x_sqrt", diff="hard")
def Fa_xsqrt2():
    k = rng.randint(1, 5); a = 3*k; f = x*sq(x+a); c = sp.Integer(-2*k)
    return F(f, "sqrt", [f"\\sqrt{{x+{a}}}+\\frac{{x}}{{2\\sqrt{{x+{a}}}}}"], f"\\frac{{{L(3*x+2*a)}}}{{2\\sqrt{{x+{a}}}}}", f"(3*x+{2*a})/(2*sqrt(x+{a}))", [c],
             domtext=dom_c(f"x+{a}\\geq 0", f"[{-a};+\\infty)"), lo=sp.Integer(-a), lc=True, roots=zt([c]), sign="ភាគបែងវិជ្ជមាន ដូចនេះ សញ្ញានៃ $§'(x)$ យកតាមភាគយក ។", fam="x_sqrt2", diff="hard")
def Fa_semi():
    p = rng.randint(-3, 3); Rr = ch([1, 2, 3, 4, 5]); r = Rr**2-p**2; g = -x**2+2*p*x+r; d = rng.randint(-2, 3)
    f = sq(g) + d; lo, hi = p-Rr, p+Rr
    return F(f, "sqrt", [f"\\frac{{{L(-2*x+2*p)}}}{{2\\sqrt{{{L(g)}}}}}"], f"\\frac{{{L(-x+p)}}}{{\\sqrt{{{L(g)}}}}}", f"({-1}*x+({p}))/sqrt({g})", [sp.Integer(p)],
             domtext=dom_c(f"{L(g)}\\geq 0", f"[{lo};{hi}]"), lo=sp.Integer(lo), hi=sp.Integer(hi), lc=True, hc=True, roots=zt([p]), sign="ភាគបែងវិជ្ជមាននៅក្នុងចន្លោះ ដូចនេះ $§'(x)$ មានសញ្ញាដូចភាគយក ។", fam="semicircle", diff="hard")
def Fa_xroot():
    k = rng.randint(1, 5); d = rng.randint(-4, 4); a = ch([1, 2, 3])
    f = a*(x - 2*k*sq(x)) + d; c = sp.Integer(k*k)
    return F(f, "sqrt", [f"{a}-\\frac{{{a*k}}}{{\\sqrt{{x}}}}"], f"\\frac{{{a if a>1 else ''}(\\sqrt{{x}}-{k})}}{{\\sqrt{{x}}}}", f"{a}*(sqrt(x)-{k})/sqrt(x)", [c],
             domtext=dom_c("x\\geq 0", "[0;+\\infty)"), lo=sp.Integer(0), lc=True, roots=f"$§'(x)=0$ ឲ្យ $\\sqrt{{x}}={k}$ នោះ $x={k*k}$ ។", sign=f"ចំពោះ $x>0$ សញ្ញានៃ $§'(x)$ យកតាម $\\sqrt{{x}}-{k}$ ។", fam="x_minus_root")
T2 = 2*pi
TRIG = [
 (lambda a: a*(sq(2)*0+sp.sin(x)+sp.cos(x)), lambda a: (f"{a if a>1 else ''}(\\cos x-\\sin x)", f"{a}*(cos(x)-sin(x))"), [pi/4, 5*pi/4], T2, "$\\cos x=\\sin x$ ឬ $\\tan x=1$"),
 (lambda a: a*(x-2*sp.sin(x)), lambda a: (f"{a if a>1 else ''}(1-2\\cos x)", f"{a}*(1-2*cos(x))"), [pi/3, 5*pi/3], T2, "$\\cos x=\\frac{1}{2}$"),
 (lambda a: a*(x+2*sp.sin(x)), lambda a: (f"{a if a>1 else ''}(1+2\\cos x)", f"{a}*(1+2*cos(x))"), [2*pi/3, 4*pi/3], T2, "$\\cos x=-\\frac{1}{2}$"),
 (lambda a: a*(x+2*sp.cos(x)), lambda a: (f"{a if a>1 else ''}(1-2\\sin x)", f"{a}*(1-2*sin(x))"), [pi/6, 5*pi/6], pi, "$\\sin x=\\frac{1}{2}$"),
 (lambda a: a*(sq(3)*x-2*sp.cos(x)*0-2*sp.sin(x)), lambda a: (f"{a if a>1 else ''}(\\sqrt{{3}}-2\\cos x)", f"{a}*(sqrt(3)-2*cos(x))"), [pi/6, 11*pi/6], T2, "$\\cos x=\\frac{\\sqrt{3}}{2}$"),
 (lambda a: a*(sp.cos(2*x)+2*sp.sin(x)), lambda a: (f"{2*a}\\cos x(1-2\\sin x)", f"{2*a}*cos(x)*(1-2*sin(x))"), [pi/6, pi/2, 5*pi/6], pi, "$\\cos x=0$ ឬ $\\sin x=\\frac{1}{2}$"),
 (lambda a: a*(sp.sin(x)**2+sp.cos(x)), lambda a: (f"{a if a>1 else ''}\\sin x(2\\cos x-1)", f"{a}*sin(x)*(2*cos(x)-1)"), [pi/3], pi, "$\\sin x=0$ ឬ $\\cos x=\\frac{1}{2}$"),
 (lambda a: a*(sp.sin(2*x)-2*x), lambda a: (f"{2*a}(\\cos 2x-1)", f"{2*a}*(cos(2*x)-1)"), [pi], T2, "$\\cos 2x=1$"),
 (lambda a: a*(x-sp.sin(x)), lambda a: (f"{a if a>1 else ''}(1-\\cos x)", f"{a}*(1-cos(x))"), [], T2, "$\\cos x=1$"),
 (lambda a: a*(sp.sqrt(3)*sp.sin(x)+sp.cos(x)), lambda a: (f"{a if a>1 else ''}(\\sqrt{{3}}\\cos x-\\sin x)", f"{a}*(sqrt(3)*cos(x)-sin(x))"), [pi/3, 4*pi/3], T2, "$\\tan x=\\sqrt{3}$"),
]
def Fa_trig():
    fn, dt, c, hi, eqn = ch(TRIG); a = ch([1, 2, 3]); d = rng.randint(-3, 3)
    f = fn(a) + d; tx, st = dt(a)
    D = "[0;" + L(hi) + "]"
    return F(f, "trig", [], tx, st, c, domtext=ch([f"លើចន្លោះ ${D}$ អនុគមន៍ $§$ កំណត់ និងមានដេរីវេ ។", f"គេសិក្សាអនុគមន៍លើ $D={D}$ ។"]), lo=sp.Integer(0), hi=hi, lc=True, hc=True,
             roots=(f"$§'(x)=0$ ឲ្យ {eqn} ។ លើ ${D}$ គេបាន " + " ឬ ".join(f"$x={L(v)}$" for v in c) + " ។") if c else "", fam="trig", diff="hard", given_dom=D)

FAM_ALL = {"cubic": (Fa_cubic, 9), "cubic_frac": (Fa_cubic_frac, 5), "cubic_mono": (Fa_cubic_mono, 3), "biq": (Fa_biq, 4), "quartic": (Fa_quartic, 3), "qdbl": (Fa_quartic_dbl, 2),
    "quintic": (Fa_quintic, 1), "homog": (Fa_homog, 4), "slant": (Fa_slant, 7), "bump": (Fa_bump, 4), "evenrat": (Fa_even_rat, 2), "xx2": (Fa_x_over_x2, 3),
    "expl": (Fa_expl, 8), "expq": (Fa_expq, 8), "expminus": (Fa_explinsum, 3), "exp2": (Fa_exp2, 3), "cosh": (Fa_cosh, 3),
    "lnlin": (Fa_lnlin, 8), "x2ln": (Fa_x2ln, 5), "xlnx": (Fa_xlnx, 5), "lnoverx": (Fa_lnoverx, 6), "ln2": (Fa_ln2, 4), "lnquad": (Fa_lnquad, 4), "xmln": (Fa_xminusln, 4),
    "xsqrt": (Fa_xsqrt, 2), "xsqrt2": (Fa_xsqrt2, 1), "semi": (Fa_semi, 2), "xroot": (Fa_xroot, 2), "trig": (Fa_trig, 4)}
SEEN = set()
def draw(allow=None):
    keys = [k for k in FAM_ALL if allow is None or k in allow]; w = [FAM_ALL[k][1] for k in keys]
    for _ in range(300):
        k = rng.choices(keys, w)[0]; F_ = FAM_ALL[k][0]()
        if F_ is None: continue
        key = str(sp.diff(F_["f"], x))
        if key in SEEN: continue
        st = St(F_)
        if st.ok:
            SEEN.add(key); return st
    return None

# ---------- study engine ----------
_lim = {}
def lim(f, v, d):
    key = (str(f), str(v), d)
    if key not in _lim:
        _lim[key] = sp.limit(f, x, v, d) if abs(v) != oo else sp.limit(f, x, v)
    return _lim[key]

def between(a, b):
    if a == -oo and b == oo: return sp.Integer(0)
    if a == -oo: return sp.floor(b) - 1
    if b == oo: return sp.ceiling(a) + 1
    fa, fb = float(a), float(b); mid = (fa+fb)/2
    for den in (1, 2, 4, 10, 100, 1000):
        t = R(round(mid*den), den)
        if fa + (fb-fa)*.1 < float(t) < fb - (fb-fa)*.1: return t
    return R(round(mid*10000), 10000)

class St:
    def __init__(s, D):
        s.__dict__.update(D); s.nm = ch(["f", "f", "f", "g", "h"])
        s.fpe = sp.diff(s.f, x); s.ok = True
        pts = [("lo", s.lo)]
        for c in s.crit:
            if float(s.lo) < float(c) < float(s.hi): pts.append(("crit", c))
        for e in s.excl:
            pts.append(("excl", e))
        pts.append(("hi", s.hi)); pts.sort(key=lambda t: float(t[1]))
        s.pts = pts
        if len({str(p[1]) for p in pts}) != len(pts): s.ok = False; return
        fn = sp.lambdify(x, s.fpe, "numpy"); dn = sp.lambdify(x, sp.sympify(s.dstr, locals={"x": x, "log": ln, "exp": ex, "sqrt": sq, "sin": sp.sin, "cos": sp.cos}), "numpy")
        s.iv = []
        for (k1, a), (k2, b) in zip(pts, pts[1:]):
            lo = max(float(a), -40) if a != -oo else float(b) - 12 if b != oo else -12
            hi = min(float(b), 40) if b != oo else float(a) + 12 if a != -oo else 12
            g = np.linspace(lo, hi, 62)[1:-1]
            with np.errstate(all="ignore"):
                v = np.asarray(fn(g), dtype=float) + 0*g; w = np.asarray(dn(g), dtype=float) + 0*g
            if np.any(~np.isfinite(v)) or np.any(np.abs(v-w) > 1e-6*(1+np.abs(v))): s.ok = False; return
            nz = v[np.abs(v) > 1e-11]
            if len(nz) == 0 or not (np.all(nz > 0) or np.all(nz < 0)): s.ok = False; return
            s.iv.append(dict(a=a, b=b, sg=1 if nz[0] > 0 else -1, t=between(a, b), ka=k1, kb=k2))
        for c in s.crit:
            if float(s.lo) <= float(c) <= float(s.hi) and abs(float(s.fpe.subs(x, c))) > 1e-9: s.ok = False; return
        s.ext = []; s.val = {}
        for i, (k, v) in enumerate(pts):
            if k == "crit":
                s.val[v] = sp.nsimplify(sp.expand_log(sp.expand(s.f.subs(x, v)), force=True)) if s.f.has(sp.sin, sp.cos) is False and False else sp.expand(s.f.subs(x, v))
                l, r = s.iv[i-1]["sg"], s.iv[i]["sg"]
                s.ext.append((v, "max" if l > r else "min" if l < r else None, s.val[v]))
        s.inc = [i for i in s.iv if i["sg"] > 0]; s.dec = [i for i in s.iv if i["sg"] < 0]
    def endv(s):
        """values at table columns: list of (left,right) limit-or-value; computes limits."""
        out = []
        for k, v in s.pts:
            if k == "lo":
                val = lim(s.f, v, "+") if (v == -oo or not s.lc) else s.f.subs(x, v); out.append((None, val))
            elif k == "hi":
                val = lim(s.f, v, "-") if (v == oo or not s.hc) else s.f.subs(x, v); out.append((val, None))
            elif k == "excl":
                out.append((lim(s.f, v, "-"), lim(s.f, v, "+")))
            else:
                out.append((s.val[v], s.val[v]))
        return out
    def count_text(s, e, m):
        """Root count of §(x)=m interval by interval over the whole domain."""
        out = []; tot = 0
        for i, iv in enumerate(s.iv):
            a, b = e[i][1], e[i+1][0]; lo_, hi_ = sorted((float(a), float(b))); yes = lo_ < float(m) < hi_; tot += yes
            out.append(f"លើ ${itv(iv['a'], iv['b'])}$ អនុគមន៍ $§$ ជាប់ និង{'កើន' if iv['sg']>0 else 'ចុះ'}ពី ${LT(a)}$ ដល់ ${LT(b)}$ ដូចនេះសមីការ{'មានឫសមួយ' if yes else 'គ្មានឫស'}លើចន្លោះនេះ ។")
        for j, (k, v) in enumerate(s.pts):
            if (k == "crit" and s.val[v] == m) or (k == "lo" and s.lc and e[j][1] == m) or (k == "hi" and s.hc and e[j][0] == m):
                tot += 1; out.append(f"ត្រង់ $x={L(v)}$ គេបាន $§({L(v)})={L(m)}$ ដូចនេះ $x={L(v)}$ ជាឫសមួយទៀត ។")
        out.append(f"សរុបលើដែនកំណត់ទាំងមូល សមីការមាន ${tot}$ ឫស ។" if tot else "សរុបលើដែនកំណត់ទាំងមូល សមីការគ្មានឫសទេ ។")
        return out
    def signrow(s):
        row = []
        for i, (k, v) in enumerate(s.pts):
            if k == "crit": row.append("0")
            elif k == "excl": row.append("\\|")
            elif k in ("lo", "hi") and abs(v) != oo and ((s.lc and k == "lo") or (s.hc and k == "hi")):
                z = None
                try: z = s.fpe.subs(x, v)
                except Exception: pass
                row.append("0" if z == 0 else ("\\|" if s.fam in ("x_sqrt", "x_sqrt2", "semicircle", "x_minus_root") else ""))
            elif k in ("lo", "hi") and abs(v) != oo: row.append("\\|")
            else: row.append("")
            if i < len(s.iv): row.append("+" if s.iv[i]["sg"] > 0 else "-")
        return row
    def cols(s): return [LT(v) for k, v in s.pts]
    def table(s):
        e = s.endv(); fv = []
        for i, (k, v) in enumerate(s.pts):
            l, r = e[i]
            if k == "excl": fv.append(f"{LT(l)}\\|{LT(r)}")
            else: fv.append(LT(l if l is not None else r))
            if i < len(s.iv): fv.append("\\nearrow" if s.iv[i]["sg"] > 0 else "\\searrow")
        return variation_table(s.cols(), s.signrow(), fv, name=s.nm), e
    def signtable(s, label=None):
        nm = label or s.nm + "'(x)"; c = s.cols(); xr = []
        for i, t in enumerate(c):
            xr.append(t)
            if i < len(c)-1: xr.append("")
        n = len(xr)
        return "\\begin{array}{c|" + "c"*n + "}\nx & " + " & ".join(xr) + " \\\\\n\\hline\n" + nm + " & " + " & ".join(s.signrow()) + "\n\\end{array}"
    def D_tex(s):
        if s.excl: return "IR-\\{" + L(s.excl[0]) + "\\}"
        if s.lo == -oo and s.hi == oo: return "IR"
        return itv(s.lo, s.hi, s.lc, s.hc)
    def ivt(s, i):
        if i["a"] == -oo and i["b"] == oo: return "IR"
        return itv(i["a"], i["b"], i["ka"] == "lo" and s.lc, i["kb"] == "hi" and s.hc)
    def problem_f(s):
        t = f"${s.nm}(x)={L(s.f)}$"
        if s.given_dom: t += f" លើចន្លោះ ${s.given_dom}$"
        return t
    def deriv_block(s):
        pre = ch(RULE[s.rule]) + ch(["ចំពោះគ្រប់ $x\\in D$ ", "", "លើ $D$ ", ""]) + ch(GOT)
        lines = [f"§'(x)={t}" for t in s.steps] if s.steps else []
        if s.steps and s.steps[-1] != s.dtex: lines.append(f"§'(x)={s.dtex}")
        if not s.steps: lines = [f"§'(x)={s.dtex}"]
        if len(lines) > 1:
            body = "$$" + lines[0] + "$$\n" + ch(["សម្រួលបាន៖", "គេអាចសរសេរ៖", "បន្ទាប់ពីសម្រួល៖", "ឬ"]) + "\n$$" + "$$\n$$".join(lines[1:]) + "$$"
        else: body = "$$" + lines[0] + "$$"
        return pre + "\n" + body
    def mono_text(s, style=None):
        style = style if style is not None else rng.randint(0, 2)
        I = " និង ".join(f"${s.ivt(i)}$" for i in s.inc); Dn = " និង ".join(f"${s.ivt(i)}$" for i in s.dec)
        if style == 0:
            out = []
            for i in s.iv:
                w = ch(["ចំពោះ", "លើចន្លោះ", "បើ"]) if True else ""
                out.append(f"{'បើ $x' if w=='បើ' else w+' $x'}\\in {s.ivt(i)}$ {ch(['នោះ','គេបាន'])} $§'(x){'>' if i['sg']>0 else '<'}0$ ដូច្នេះ $§$ {'កើន' if i['sg']>0 else 'ចុះ'} ។")
            return "\n".join(out)
        if style == 1:
            a = f"$§'(x)>0$ លើ {I} នោះ $§$ កើនលើចន្លោះទាំងនេះ ។" if len(s.inc) > 1 else (f"$§'(x)>0$ លើ {I} នោះ $§$ កើនលើចន្លោះនេះ ។" if s.inc else "")
            b = f"$§'(x)<0$ លើ {Dn} នោះ $§$ ចុះលើចន្លោះទាំងនេះ ។" if len(s.dec) > 1 else (f"$§'(x)<0$ លើ {Dn} នោះ $§$ ចុះលើចន្លោះនេះ ។" if s.dec else "")
            return "\n".join(t for t in (a, b) if t)
        t = []
        if s.inc: t.append(f"អនុគមន៍កើនលើ {I}")
        if s.dec: t.append(f"អនុគមន៍ចុះលើ {Dn}")
        return "តាមសញ្ញានៃ $§'(x)$ " + " ហើយ ".join(t) + " ។"
    def conc_mono(s):
        I = " និង ".join(f"${s.ivt(i)}$" for i in s.inc); Dn = " និង ".join(f"${s.ivt(i)}$" for i in s.dec)
        if not s.dec: return f"{ch(CONC)} $§$ ជាអនុគមន៍កើនលើ {I} ។"
        if not s.inc: return f"{ch(CONC)} $§$ ជាអនុគមន៍ចុះលើ {Dn} ។"
        return f"{ch(CONC)} $§$ កើនលើ {I} និងចុះលើ {Dn} ។"
    def ans_mono(s):
        p = []
        if s.inc: p.append("\\nearrow:" + "\\cup".join(s.ivt(i) for i in s.inc) if len(s.excl) == 0 else "\\nearrow:" + ",\\ ".join(s.ivt(i) for i in s.inc))
        if s.dec: p.append("\\searrow:" + "\\cup".join(s.ivt(i) for i in s.dec) if len(s.excl) == 0 else "\\searrow:" + ",\\ ".join(s.ivt(i) for i in s.dec))
        return ",\\quad ".join(p).replace("§", s.nm)
    def ext_text(s):
        out = []; 
        for v, t, val in s.ext:
            xv, yv = L(v), L(val)
            if t == "max":
                out.append(ch([f"អនុគមន៍មានអតិបរមាស្មើនឹង ${yv}$ ត្រង់ $x={xv}$ ។", f"ត្រង់ $x={xv}$, $§'(x)$ ប្ដូរសញ្ញាពី $+$ ទៅ $-$ ដូចនេះ $§({xv})={yv}$ ជាអតិបរមា ។",
                               f"ដោយ $§'$ ប្ដូរពីវិជ្ជមានទៅអវិជ្ជមានត្រង់ $x={xv}$ នោះ $§$ មានអតិបរមា $§({xv})={yv}$ ។"]))
            elif t == "min":
                out.append(ch([f"អនុគមន៍មានអប្បបរមាស្មើនឹង ${yv}$ ត្រង់ $x={xv}$ ។", f"ត្រង់ $x={xv}$, $§'(x)$ ប្ដូរសញ្ញាពី $-$ ទៅ $+$ ដូចនេះ $§({xv})={yv}$ ជាអប្បបរមា ។",
                               f"ដោយ $§'$ ប្ដូរពីអវិជ្ជមានទៅវិជ្ជមានត្រង់ $x={xv}$ នោះ $§$ មានអប្បបរមា $§({xv})={yv}$ ។"]))
            else:
                out.append(f"ត្រង់ $x={xv}$, $§'(x)=0$ តែមិនប្ដូរសញ្ញា ដូចនេះ $§$ គ្មានបរមាត្រង់ចំណុចនេះទេ ។")
        if not s.ext or all(t is None for _, t, _ in s.ext):
            out.append(ch(["ដោយ $§'(x)$ មិនប្ដូរសញ្ញា អនុគមន៍គ្មានអតិបរមា ឬអប្បបរមាធៀបទេ ។" if not s.excl else "$§'(x)$ មិនស្មើសូន្យលើ $D$ ដូចនេះអនុគមន៍គ្មានចំណុចបរមាទេ ។"]))
        return "\n".join(out)
    def ans_ext(s):
        p = [f"\\text{{{'អតិបរមាធៀប' if t=='max' else 'អប្បបរមាធៀប'}}}={L(val)}\\ (x={L(v)})" for v, t, val in s.ext if t]
        return ",\\quad ".join(p) if p else "\\text{-}"
    def lim_lines(s, e):
        L_ = []
        for (k, v), (l, r) in zip(s.pts, e):
            if k == "lo" and (v == -oo or not s.lc):
                L_.append(f"\\lim_{{x\\to {LT(v)}}}§(x)={LT(r)}" if v == -oo else f"\\lim_{{x\\to {L(v)}^{{+}}}}§(x)={LT(r)}")
            if k == "hi" and (v == oo or not s.hc):
                L_.append(f"\\lim_{{x\\to {LT(v)}}}§(x)={LT(l)}" if v == oo else f"\\lim_{{x\\to {L(v)}^{{-}}}}§(x)={LT(l)}")
            if k == "excl":
                L_.append(f"\\lim_{{x\\to {L(v)}^{{-}}}}§(x)={LT(l)}"); L_.append(f"\\lim_{{x\\to {L(v)}^{{+}}}}§(x)={LT(r)}")
        return L_
    def lim_note(s):
        return {"cubic": "លីមីតនៃពហុធាត្រង់អនន្តស្មើនឹងលីមីតនៃតួដែលមានដឺក្រេខ្ពស់ជាងគេ ។"}.get(s.fam, "")
    def checks(s, limits=None, sign=True):
        fs = str(s.f); c = [check(f"diff({fs},x)", s.dstr, "derivative")]
        for k, v in s.pts:
            if k == "crit":
                c.append(check(f"subs(diff({fs},x),x,{v})", "0", "critical point"))
                c.append(check(f"subs({fs},x,{v})", str(s.val[v]), "value at critical point"))
        if sign:
            for i in s.iv:
                c.append(check(f"subs(diff({fs},x),x,{i['t']})" + (">0" if i["sg"] > 0 else "<0"), "True", "sign of derivative"))
        if limits:
            for (k, v), (l, r) in zip(s.pts, limits):
                if k == "lo" and (v == -oo or not s.lc):
                    c.append(check(f"limit({fs},x,{v})" if v == -oo else f"limit({fs},x,{v},'+')", str(r), "limit"))
                if k == "hi" and (v == oo or not s.hc):
                    c.append(check(f"limit({fs},x,{v})" if v == oo else f"limit({fs},x,{v},'-')", str(l), "limit"))
                if k == "excl":
                    c.append(check(f"limit({fs},x,{v},'-')", str(l), "limit")); c.append(check(f"limit({fs},x,{v},'+')", str(r), "limit"))
        return c

def fin(st, txt):
    return txt.replace("§", st.nm)
def lines(*a):
    return "\n".join(t for t in a if t)
def Dg(kind, latex, alt, image=None):
    d = {"type": kind, "latex": latex, "alt_km": alt}
    if image: d["image"] = image
    return d
ALT_V = ["តារាងអថេរភាពនៃអនុគមន៍", "តារាងអថេរភាពបង្ហាញទិសដៅកើន និងចុះនៃអនុគមន៍", "តារាងអថេរភាព"]
ALT_S = ["តារាងសញ្ញានៃដេរីវេទី១", "សញ្ញានៃដេរីវេលើចន្លោះនីមួយៗ"]
HEAD = [("+ ", ""), ("- ", ""), ("", " ៖")]
def H(t, sty):
    return sty[0] + t + sty[1]

# ---------- task renderers ----------
ROWS = []
def add(st, sub, diff, prob, sol, ans, checks, diagrams=None, raw=False):
    p = prob if raw else fin(st, prob); so = sol if raw else fin(st, sol); a = ans if raw else ans.replace("§", st.nm)
    ROWS.append(make_row("variation", sub, diff, p, so, a, checks, GEN, diagrams=diagrams))
    return ROWS[-1]

def T_mono(st):
    sty = ch(HEAD)
    q = ch(["រកចន្លោះដែលអនុគមន៍ $§$ កើន និងចន្លោះដែលវាចុះ ។", "សិក្សាទិសដៅអថេរភាពនៃ $§$ ។", "ចូរកំណត់ចន្លោះកើន និងចន្លោះចុះនៃអនុគមន៍នេះ ។", "សិក្សាអថេរភាពនៃអនុគមន៍ $§$ (មិនចាំបាច់គណនាលីមីត) ។",
            "ចូរបង្ហាញថាតើ $§$ កើន ឬចុះលើចន្លោះណាខ្លះ ។", "គណនា $§'(x)$ រួចកំណត់ទិសដៅអថេរភាពនៃ $§$ ។", "គណនាដេរីវេ រួចទាញរកចន្លោះដែល $§$ កើន និងចុះ ។", "តើអនុគមន៍នេះកើនលើចន្លោះណា ហើយចុះលើចន្លោះណា ?"])
    prob = f"{ch(STEM)} {st.problem_f()} ។ {q}"
    sol = lines(H("ដែនកំណត់", sty) if not st.domtext.startswith("ដែនកំណត់") else "", st.domtext, H("ដេរីវេទី១", sty), st.deriv_block(), st.roots, st.sign, H("សញ្ញាដេរីវេទី១", sty) if rng.random() < .6 else "", st.mono_text(), st.conc_mono())
    add(st, "monotonicity", st.diff, prob, sol, st.ans_mono(), st.checks(), [Dg("sign_table", st.signtable(), ch(ALT_S))] if rng.random() < .5 else [])

def T_sign(st):
    q = ch(["សិក្សាសញ្ញានៃ $§'(x)$ រួចសង់តារាងសញ្ញា ។", "គណនា $§'(x)$ រួចសិក្សាសញ្ញារបស់វា ។", "សង់តារាងសញ្ញានៃដេរីវេទី១ ។", "រកសញ្ញានៃដេរីវេ $§'(x)$ លើដែនកំណត់ ។", "ចូរគូសតារាងសញ្ញានៃ $§'(x)$ ហើយទាញរកទិសដៅអថេរភាពនៃ $§$ ។"])
    prob = f"{ch(STEM)} {st.problem_f()} ។ {q}"
    tb = st.signtable()
    sol = lines(st.domtext, st.deriv_block(), st.roots, st.sign, ch(["តារាងសញ្ញានៃ $§'(x)$៖", "សញ្ញាដេរីវេទី១៖", "គេបានតារាងសញ្ញា៖"]), f"$${tb}$$", st.mono_text(2), st.conc_mono())
    add(st, "sign_table", st.diff, prob, sol, tb.replace("\n", " "), st.checks(), [Dg("sign_table", tb, ch(ALT_S))])

def T_table(st, graph=False):
    tb, e = st.table(); sty = ch(HEAD)
    q = ch(["គណនាដេរីវេនៃ $§$ រួចសង់តារាងអថេរភាពនៃ $§$ ។", "សិក្សាអថេរភាព និងសង់តារាងអថេរភាពនៃអនុគមន៍នេះ ។", "ចូរសង់តារាងអថេរភាពនៃ $§$ ។", "គណនាលីមីតនៅចុងដែនកំណត់ គណនា $§'(x)$ រួចសង់តារាងអថេរភាព ។", "សិក្សាទិសដៅអថេរភាព រកលីមីត ហើយសង់តារាងអថេរភាពនៃ $§$ ។", "សង់តារាងអថេរភាពនៃ $§$ រួចបញ្ជាក់ចំណុចបរមា (បើមាន) ។"])
    prob = f"{ch(STEM)} {st.problem_f()} ។ {q}"
    ll = st.lim_lines(e)
    limtxt = (H("លីមីត", sty) + "\n" + ch(["គេមាន៖", "យើងមានលីមីត៖", "លីមីតនៅចុងដែនកំណត់៖"]) + "\n$$" + ",\\quad ".join(ll) + "$$") if ll else ""
    dpart = lines(H("ទិសដៅអថេរភាព", sty), st.deriv_block(), st.roots, st.sign, st.mono_text(), st.ext_text())
    order = [dpart, limtxt] if rng.random() < .75 else [limtxt, dpart]
    sol = lines(H("ដែនកំណត់", sty) if not st.domtext.startswith("ដែនកំណត់") else "", st.domtext, *order, H("តារាងអថេរភាព", sty), f"$${tb}$$", st.conc_mono())
    add(st, "variation_table", st.diff if st.diff != "easy" else "medium", prob, sol, tb.replace("\n", " "), st.checks(e), [Dg("variation_table", tb, ch(ALT_V))])

def T_ext(st):
    if not any(t for _, t, _ in st.ext) : return T_mono(st)
    q = ch(["រកបរមាធៀបនៃ $§$ ។", "រកតម្លៃអតិបរមា និងតម្លៃអប្បបរមាធៀបនៃអនុគមន៍នេះ (បើមាន) ។", "កំណត់ចំណុចបរមានៃខ្សែកោងតាងអនុគមន៍នេះ ។", "ចូរសិក្សាថាតើ $§$ មានអតិបរមា ឬអប្បបរមាត្រង់ណា រួចគណនាតម្លៃនោះ ។", "រកកូអរដោនេនៃចំណុចបរមានៃក្រាបនៃ $§$ ។", "តើអនុគមន៍នេះមានបរមាធៀបដែរឬទេ ? បើមាន ចូរគណនា ។"])
    prob = f"{ch(STEM)} {st.problem_f()} ។ {q}"
    pts = [f"$\\boxed{{{'M' if t=='max' else 'N'}({L(v)};{L(val)})}}$" for v, t, val in st.ext if t]
    sol = lines(st.domtext, st.deriv_block(), st.roots, st.sign, ch(["សញ្ញានៃ $§'(x)$៖", "គេបានតារាងសញ្ញា៖"]), f"$${st.signtable()}$$", st.ext_text(),
                f"{ch(CONC)} ចំណុចបរមានៃក្រាបគឺ " + " និង ".join(pts) + " ។")
    add(st, "local_extrema", st.diff, prob, sol, st.ans_ext(), st.checks(), [Dg("sign_table", st.signtable(), ch(ALT_S))])

def T_second(st):
    ex_ = [(v, t, val) for v, t, val in st.ext if t]
    if not ex_: return T_ext(st)
    f2 = sp.diff(st.fpe, x); out = []; chs = st.checks(sign=False)
    for v, t, val in ex_:
        w = f2.subs(x, v)
        if w == 0 or abs(float(w)) < 1e-12: return T_ext(st)
        w2 = sp.expand(w)
        out.append(f"ចំពោះ $x={L(v)}$៖ $§'({L(v)})=0$ និង $§''({L(v)})={L(w2)}{'<' if float(w)<0 else '>'}0$ ដូចនេះ $§({L(v)})={L(val)}$ ជា{'អតិបរមា' if float(w)<0 else 'អប្បបរមា'} ។")
        chs.append(check(f"subs(diff({st.f},x,2),x,{v})", str(w2), "f'' at critical point"))
    f2t = L(sp.simplify(f2)) if st.f.is_polynomial(x) else None
    q = ch(["ប្រើដេរីវេទី២ ដើម្បីបញ្ជាក់ប្រភេទនៃបរមានៃ $§$ ។", "រកចំណុចដែល $§'(x)=0$ រួចប្រើសញ្ញានៃ $§''$ ដើម្បីកំណត់អតិបរមា និងអប្បបរមា ។", "ដោយប្រើដេរីវេទី២ ចូររកបរមាធៀបនៃអនុគមន៍នេះ ។"])
    if f2t is None: return T_ext(st)
    sol = lines(st.domtext, st.deriv_block(), st.roots, f"ដេរីវេទី២៖\n$$§''(x)={f2t}$$", *out, f"{ch(CONC)} " + " និង ".join(f"{'អតិបរមាធៀប' if t=='max' else 'អប្បបរមាធៀប'} $§({L(v)})={L(val)}$" for v, t, val in ex_) + " ។")
    add(st, "local_extrema_second_derivative", "medium", f"{ch(STEM)} {st.problem_f()} ។ {q}", sol, st.ans_ext(), chs)

WORDS = ["គ្មានឫស", "មានឫសមួយ", "មានឫសពីរ", "មានឫសបី", "មានឫសបួន", "មានឫសប្រាំ"]
def count_sol(st, e, m):
    n = 0
    for i, iv in enumerate(st.iv):
        lo_, hi_ = sorted((float(e[i][1]), float(e[i+1][0])))
        if lo_ < float(m) < hi_: n += 1
    for j, (k, v) in enumerate(st.pts):
        if k == "crit" and st.val[v] == m: n += 1
        if k == "lo" and st.lc and e[j][1] == m: n += 1
        if k == "hi" and st.hc and e[j][0] == m: n += 1
    return n
def thresholds(e):
    t = set()
    for l, r in e:
        for v in (l, r):
            if v is not None and abs(v) != oo: t.add(v)
    return sorted(t, key=float)
def y_window(st, y):
    """Vertical window built around the extreme values, so that far tails cannot flatten them."""
    ys = [float(v) for v in st.val.values()]
    if st.lc: ys.append(float(st.f.subs(x, st.lo)))
    if st.hc: ys.append(float(st.f.subs(x, st.hi)))
    if ys:
        lo_, hi_ = min(ys), max(ys); pad = max(2.0, .2*(hi_-lo_))
    else:
        lo_, hi_ = float(np.percentile(y, 25)), float(np.percentile(y, 75)); pad = max(2.0, .25*(hi_-lo_))
    y0, y1 = lo_-pad, hi_+pad
    if 0 < y0 <= 2*pad: y0 = -1.0
    if -2*pad <= y1 < 0: y1 = 1.0
    return int(np.floor(y0)), int(np.ceil(y1))
def graph_of(st, row, e=None, png=True, tang=None):
    f = st.f; xs = [float(v) for k, v in st.pts if abs(v) != oo]; 
    x0, x1 = (min(xs) - 3, max(xs) + 3) if xs else (-5, 5)
    if st.lo != -oo: x0 = float(st.lo) - .5
    if st.hi != oo: x1 = float(st.hi) + .5
    x0, x1 = int(np.floor(x0)), int(np.ceil(x1))
    fn = sp.lambdify(x, f, "numpy"); g = np.linspace(x0, x1, 800)
    with np.errstate(all="ignore"): y = np.asarray(fn(g), dtype=complex).real + 0*g
    y = y[np.isfinite(y)]; 
    y0, y1 = y_window(st, y)
    pg = str(f).replace("**", "^").replace("log(", "ln(")
    pg = re.sub(r"\b(sin|cos)\(([^()]*)\)", r"\1(deg(\2))", pg)
    extra = ""
    lo = x0 if st.lo == -oo else float(st.lo) + (0 if st.lc else .03); hi = x1 if st.hi == oo else float(st.hi) - (0 if st.hc else .03)
    src = tikz_graph(pg, x0, x1, y0, y1, "")
    head = f"\\addplot[thick,domain={x0}:{x1}] {{{pg}}};\n"
    cuts = [float(v) for v in st.excl]; a = lo; plots = ""
    for c in cuts + [None]:
        b = hi if c is None else c - .03
        plots += f"\\addplot[thick,domain={a:.2f}:{b:.2f}] {{{pg}}};\n"
        if c is not None:
            a = c + .03; plots += f"\\addplot[dashed] coordinates {{({c:.2f},{y0}) ({c:.2f},{y1})}};\n"
    for v, t, val in st.ext:
        if t: plots += f"\\addplot[only marks] coordinates {{({float(v):.3f},{float(val):.3f})}};\n"
    src = src.replace(head, plots)
    d = Dg("graph", src, ch(["ក្រាបនៃអនុគមន៍ និងចំណុចបរមា", "ខ្សែកោងតាងអនុគមន៍", "សំណង់ក្រាបនៃអនុគមន៍"]))
    global PNG
    if png and PNG < 280:
        PNG += 1
        asy = [("v", v) for v in st.excl]
        d["image"] = plot_png(row["id"], f, x0, x1, y0, y1, points=[(v, val) for v, t, val in st.ext if t], asymptotes=asy)
    return d
PNG = 0
def T_sol(st):
    if not st.ext or not any(t for _, t, _ in st.ext): return T_table(st)
    tb, e = st.table(); ths = thresholds(e)
    if len(ths) < 1 or not all(sp.sympify(t).is_number for t in ths): return T_table(st)
    mode = rng.choice(["disc", "disc", "disc", "num", "exact"])
    cases = []; pts = [ths[0]-1] 
    seq = []
    for i, t in enumerate(ths):
        lowt = f"m<{L(t)}" if i == 0 else f"{L(ths[i-1])}<m<{L(t)}"
        mid = sp.floor(t) - 1 if i == 0 else between(ths[i-1], t)
        seq.append((lowt, count_sol(st, e, mid), mid)); seq.append((f"m={L(t)}", count_sol(st, e, t), t))
    seq.append((f"m>{L(ths[-1])}", count_sol(st, e, sp.ceiling(ths[-1])+1), sp.ceiling(ths[-1])+1))
    intro = ch(["ចំនួនឫសនៃសមីការ $§(x)=m$ ស្មើនឹងចំនួនចំណុចប្រសព្វរវាងខ្សែកោង $(C)$ និងបន្ទាត់ $y=m$ ។", "តាមតារាងអថេរភាព យើងរាប់ចំណុចប្រសព្វនៃបន្ទាត់ដេក $y=m$ ជាមួយក្រាបនៃ $§$ ។", "ឫសនៃសមីការគឺជាអាប់ស៊ីសនៃចំណុចប្រសព្វរវាង $(C)$ និង $y=m$ ។"])
    intro += " លើចន្លោះនីមួយៗដែល $§$ កើន ឬចុះ សមីការមានឫសយ៉ាងច្រើនមួយ ហើយវាមានឫសមួយកាលណា $m$ ស្ថិតនៅចន្លោះតម្លៃចុងទាំងពីរនៃចន្លោះនោះ ។"
    base = lines(st.domtext, st.deriv_block(), st.roots, st.sign, st.ext_text(), ch(["លីមីត៖", "គេមាន៖"]) if st.lim_lines(e) else "", ("$$" + ",\\quad ".join(st.lim_lines(e)) + "$$") if st.lim_lines(e) else "",
                 ch(["តារាងអថេរភាព៖", "គេបានតារាងអថេរភាព៖"]), f"$${tb}$$")
    if mode == "disc":
        q = ch(["សង់តារាងអថេរភាពនៃ $§$ រួចពិភាក្សាតាមតម្លៃនៃប៉ារ៉ាម៉ែត្រ $m$ នូវចំនួនឫសនៃសមីការ $§(x)=m$ ។", "សិក្សាអថេរភាពនៃ $§$ ។ ទាញរកចំនួនឫសនៃសមីការ $§(x)=m$ តាមតម្លៃ $m$ ។", "ពិភាក្សាចំនួនឫសនៃសមីការ $§(x)=m$ ដោយប្រើតារាងអថេរភាព ។"])
        body = [f"បើ ${c}$ នោះសមីការ{WORDS[n]} ។" for c, n, _ in seq]
        ans = ",\\ ".join(f"{c}:{n}" for c, n, _ in seq)
        concl = f"{ch(CONC)} ចំនួនឫសអាស្រ័យនឹង $m$ ដូចបានបង្ហាញខាងលើ ។"
    elif mode == "num":
        c, n, mv = ch(seq)
        q = f"សង់តារាងអថេរភាពនៃ $§$ រួចរកចំនួនឫសនៃសមីការ $§(x)={L(mv)}$ ។"
        body = [f"យើងប្រៀបធៀប $m={L(mv)}$ ជាមួយតម្លៃក្នុងតារាង ។ ករណីនេះ ${c}$ ។"] + st.count_text(e, mv)
        ans = f"{n}"; concl = f"{ch(CONC)} សមីការ $§(x)={L(mv)}$ {WORDS[n]} ។"
    else:
        mx = max(n for _, n, _ in seq); good = [c for c, n, _ in seq if n == mx]
        if mx < 2: return T_table(st)
        q = f"សង់តារាងអថេរភាពនៃ $§$ រួចរកតម្លៃ $m$ ដើម្បីឲ្យសមីការ $§(x)=m$ មានចំនួនឫសច្រើនបំផុត ។"
        body = [f"តាមតារាង ចំនួនឫសច្រើនបំផុតគឺ ${mx}$ ហើយកើតឡើងកាលណា " + " ឬ ".join(f"${c}$" for c in good) + " ។"]
        ans = " \\text{ ឬ } ".join(good); concl = f"{ch(CONC)} តម្លៃ $m$ ត្រូវការគឺ " + " ឬ ".join(f"$\\boxed{{{c}}}$" for c in good) + " ។"
    prob = f"{ch(STEM)} {st.problem_f()} ។ {q}"
    sol = lines(base, intro, *body, concl)
    row = add(st, "number_of_solutions", "hard" if st.diff != "bacii" else "bacii", prob, sol, ans.replace("\\text{ ឬ }", "\\ \\vee\\ "), st.checks(e), [Dg("variation_table", tb, ch(ALT_V))])
    row["diagrams"].append(graph_of(st, row, e))

def T_multi(st):
    tb, e = st.table(); nm = st.nm
    dom_lo = int(np.ceil(float(st.lo))) + 1 if st.lo != -oo else -2
    cand = [c for c in range(dom_lo, dom_lo + 7) if float(st.lo) < c < float(st.hi) and c not in st.excl and c not in st.crit]
    if not cand: return T_table(st)
    t0 = ch(cand); y0 = sp.expand(st.f.subs(x, t0)); sl = sp.expand(st.fpe.subs(x, t0))
    tan = sp.expand(sl*(x-t0)+y0)
    if len(str(tan)) > 40: return T_table(st)
    asy = []; chs = st.checks(e)
    for k, v in st.asym:
        if k == "v": asy.append(f"បន្ទាត់ $x={L(v)}$ ជាអាស៊ីមតូតឈរនៃខ្សែកោង ។")
        if k == "h": asy.append(f"បន្ទាត់ $y={L(v)}$ ជាអាស៊ីមតូតដេកនៃខ្សែកោង ។"); 
        if k == "s":
            asy.append(f"ដោយ $\\lim_{{x\\to\\pm\\infty}}[§(x)-({L(v)})]=0$ នោះបន្ទាត់ $y={L(v)}$ ជាអាស៊ីមតូតទ្រេតនៃខ្សែកោង ។")
            chs.append(check(f"limit({st.f}-({v}),x,oo)", "0", "slant asymptote"))
    can = f"សរសេរ $§(x)$ ជារាងកាណូនិក៖ $§(x)={st.canon}$ ។" if st.canon else ""
    parts = ["ក. រកដែនកំណត់ និងគណនាលីមីតនៅចុងដែនកំណត់ ។", "ខ. គណនា $§'(x)$ រួចសង់តារាងអថេរភាពនៃ $§$ ។", f"គ. រកសមីការបន្ទាត់ប៉ះនៃខ្សែកោង $(C)$ ត្រង់ចំណុចដែលមានអាប់ស៊ីស $x={t0}$ ។", "ឃ. សង់ក្រាប $(C)$ ។"]
    ll = st.lim_lines(e); slope = f"§'({t0})={L(sl)}"
    sol = lines("ក.", st.domtext, can, ("$$" + ",\\quad ".join(ll) + "$$") if ll else "", *asy, "ខ.", st.deriv_block(), st.roots, st.sign, st.ext_text(), ch(["តារាងអថេរភាព៖", "គេបានតារាងអថេរភាព៖"]), f"$${tb}$$",
                "គ.", f"តាមរូបមន្ត $y-y_0=§'(x_0)(x-x_0)$ ដោយ $x_0={t0}$, $y_0=§({t0})={L(y0)}$ និង ${slope}$ គេបាន៖", f"$$y={L(sl)}({L(x-t0)}){'+' if float(y0)>=0 else ''}{L(y0)}$$", f"ដូចនេះ សមីការបន្ទាត់ប៉ះគឺ $\\boxed{{y={L(tan)}}}$ ។",
                "ឃ.", ch(["សំណង់ក្រាបតាមតារាងអថេរភាព និងចំណុចបរមាដូចរូបខាងក្រោម ។", "យើងសង់ក្រាបដោយប្រើតារាងអថេរភាពខាងលើ ។"]))
    chs += [check(f"subs(diff({st.f},x),x,{t0})", str(sl), "slope"), check(f"subs({st.f},x,{t0})", str(y0), "y0"), check(f"subs({st.f},x,{t0})+subs(diff({st.f},x),x,{t0})*(x-{t0})", str(tan), "tangent")]
    prob = f"{ch(STEM)} {st.problem_f()} ដែលមានក្រាបតាងដោយ $(C)$ ។\n" + "\n".join(parts)
    row = add(st, "full_function_study", "bacii", prob, sol, f"y={L(tan)}", chs, [Dg("variation_table", tb, ch(ALT_V))])
    row["diagrams"].append(graph_of(st, row, e))

def T_closed(st):
    """Global extrema of a polynomial on [a,b]."""
    cs = [v for v, t, val in st.ext]
    if not cs or not st.f.is_polynomial(x): return T_mono(st)
    a = int(min(float(c) for c in cs)) - rng.randint(0, 2) - 1; b = int(max(float(c) for c in cs)) + rng.randint(1, 2)
    pts = [a] + sorted(cs, key=float) + [b]; vals = [st.f.subs(x, p) for p in pts]
    mx, mn = max(vals, key=float), min(vals, key=float)
    xm, xn = pts[vals.index(mx)], pts[vals.index(mn)]
    if vals.count(mx) > 1 or vals.count(mn) > 1: return T_mono(st)
    q = ch([f"រកតម្លៃអតិបរមា និងតម្លៃអប្បបរមានៃ $§$ លើចន្លោះ $[{a};{b}]$ ។", f"លើចន្លោះបិទ $[{a};{b}]$ ចូរកំណត់តម្លៃធំបំផុត និងតម្លៃតូចបំផុតនៃអនុគមន៍នេះ ។"])
    tbl = "\n".join(f"$§({L(p)})={L(v)}$" + (" (ចុងចន្លោះ)" if p in (a, b) else "") for p, v in zip(pts, vals))
    sol = lines(f"អនុគមន៍ $§$ ជាពហុធា ដូចនេះវាជាប់លើ $[{a};{b}]$ ។", st.deriv_block().replace("ចំពោះគ្រប់ $x\\in D$ ", "").replace("លើ $D$ ", ""), st.roots, "យើងគណនាតម្លៃនៃអនុគមន៍ត្រង់ចំណុចទាំងនេះ និងត្រង់ចុងចន្លោះ៖", tbl,
                f"{ch(CONC)} តម្លៃអតិបរមាគឺ $\\boxed{{{L(mx)}}}$ ត្រង់ $x={L(xm)}$ និងតម្លៃអប្បបរមាគឺ $\\boxed{{{L(mn)}}}$ ត្រង់ $x={L(xn)}$ ។")
    chs = [check(f"diff({st.f},x)", st.dstr, "derivative")] + [check(f"subs({st.f},x,{p})", str(v), "value") for p, v in zip(pts, vals)]
    add(st, "extrema_on_closed_interval", "medium", f"{ch(STEM)} {st.problem_f()} ។ {q}", sol, f"\\max={L(mx)},\\ \\min={L(mn)}", chs)

# ---------- inflection ----------
def infl(f, d1tex, d1str, d2tex, d2str, roots, domtext=None, lo=-oo, hi=oo, lc=False, hc=False, rootsent="", sign="", fam="", rule="poly", diff="medium", given_dom=None, center=False):
    if str(sp.diff(f, x)) in SEEN: return
    st = St(F(sp.diff(f, x), rule, [], d2tex, d2str, roots, domtext=domtext, lo=lo, hi=hi, lc=lc, hc=hc, fam=fam, diff=diff, given_dom=given_dom))
    if not st.ok: return
    SEEN.add(str(sp.diff(f, x))); nm = ch(["f", "f", "g", "h"])
    pts = [(v, f.subs(x, v)) for v, t, _ in st.ext if t]; pts = [(v, sp.expand(y)) for v, y in pts]
    tb = st.signtable(nm + "''(x)").replace(st.nm + "'", nm + "'")
    prob_f = f"${nm}(x)={L(f)}$" + (f" លើចន្លោះ ${given_dom}$" if given_dom else "")
    fs = str(f)
    chs = [check(f"diff({fs},x)", d1str, "f'"), check(f"diff({fs},x,2)", d2str, "f''")]
    for v, y in pts:
        chs += [check(f"subs(diff({fs},x,2),x,{v})", "0", "f'' root"), check(f"subs({fs},x,{v})", str(y), "ordinate")]
    for i in st.iv:
        chs.append(check(f"subs(diff({fs},x,2),x,{i['t']})" + (">0" if i["sg"] > 0 else "<0"), "True", "sign of f''"))
    pos = " និង ".join(f"${st.ivt(i)}$" for i in st.inc); neg = " និង ".join(f"${st.ivt(i)}$" for i in st.dec)
    sgn = []
    if pos: sgn.append(f"$§''(x)>0$ លើ {pos}")
    if neg: sgn.append(f"$§''(x)<0$ លើ {neg}")
    I = " និង ".join(f"$I({L(v)};{L(y)})$" if len(pts) == 1 else f"$I_{{{j+1}}}({L(v)};{L(y)})$" for j, (v, y) in enumerate(pts))
    q = ch(["គណនា $§''(x)$ រួចរកចំណុចរបត់នៃខ្សែកោង $(C)$ ។", "សិក្សាសញ្ញានៃដេរីវេទី២ រួចកំណត់ចំណុចរបត់នៃក្រាបនៃ $§$ ។", "រកកូអរដោនេនៃចំណុចរបត់នៃខ្សែកោងតាងអនុគមន៍នេះ ។", "ចូរគណនាដេរីវេទី១ និងដេរីវេទី២ ហើយសិក្សាថាតើខ្សែកោងមានចំណុចរបត់ឬទេ ។", "សង់តារាងសញ្ញានៃ $§''(x)$ រួចទាញរកចំណុចរបត់ ។"])
    z = rootsent or (("$§''(x)=0$ ឲ្យ " + " ឬ ".join(f"$x={L(v)}$" for v in roots) + " ។") if roots else "")
    pre = (domtext + "\n") if domtext else ""
    sol = lines(pre.strip(), ch(["ដេរីវេទី១៖", "គណនាដេរីវេទី១៖"]), f"$$§'(x)={d1tex}$$", ch(["ដេរីវេទី២៖", "បន្តគណនាដេរីវេទី២៖", "ធ្វើដេរីវេម្ដងទៀត៖"]), f"$$§''(x)={d2tex}$$", z, sign, ch(["តារាងសញ្ញានៃ $§''(x)$៖", "សញ្ញានៃដេរីវេទី២៖"]), f"$${tb}$$", " ហើយ ".join(sgn) + " ។")
    if pts:
        sol = lines(sol, ch(["ដោយ $§''(x)$ ប្ដូរសញ្ញាត្រង់ចំណុចនេះ នោះវាជាចំណុចរបត់ ។", "ដេរីវេទី២ ស្មើសូន្យ ហើយប្ដូរសញ្ញា ដូច្នេះមានចំណុចរបត់ ។"]) if len(pts) == 1 else "$§''(x)$ ស្មើសូន្យ ហើយប្ដូរសញ្ញាត្រង់ចំណុចទាំងនោះ ដូច្នេះវាជាចំណុចរបត់ ។", f"{ch(CONC)} ខ្សែកោងមានចំណុចរបត់ {I} ។")
        ans = ",\\ ".join(f"({L(v)};{L(y)})" for v, y in pts)
    else:
        sol = lines(sol, f"{ch(CONC)} $§''(x)$ មិនប្ដូរសញ្ញាទេ ខ្សែកោងគ្មានចំណុចរបត់ទេ ។"); ans = "\\varnothing"
    if center and len(pts) == 1:
        v, y = pts[0]
        q = "រកចំណុចរបត់ $I$ នៃខ្សែកោង $(C)$ រួចផ្ទៀងផ្ទាត់ថា $I$ ជាផ្ចិតឆ្លុះនៃ $(C)$ ។"
        sol = lines(sol, f"ផ្ទៀងផ្ទាត់ផ្ចិតឆ្លុះ៖ យើងត្រូវបង្ហាញថា $§({L(2*v)}-x)+§(x)={L(2*y)}$ ។ ដោយពន្លាតតួទាំងអស់ យើងឃើញថាតួដែលមាន $x$ រលុបគ្នា ហើយនៅសល់ ${L(2*y)}$ ។", f"នោះបញ្ជាក់ថា $I({L(v)};{L(y)})$ ជាផ្ចិតឆ្លុះនៃ $(C)$ ។")
        chs.append(check(f"subs({fs},x,{2*v}-x)+{fs}", str(2*y), "centre of symmetry"))
    prob = f"{ch(STEM)} {prob_f} ។ {q}"
    ROWS.append(make_row("variation", "inflection_point" if pts else "no_inflection_point", diff, prob.replace("§", nm), sol.replace("§", nm), ans, chs, GEN, diagrams=[Dg("sign_table", tb, "តារាងសញ្ញានៃដេរីវេទី២")]))

def gen_infl(n):
    start = len(ROWS)
    for _ in range(n*6):
        if len(ROWS)-start >= n: break
        k = rng.choices(range(12), [7, 6, 3, 6, 6, 3, 4, 3, 5, 3, 3, 3])[0]
        if k == 0:
            a = ch([1, -1, 2, -2, 3]); c = rng.randint(-3, 3); b = rng.randint(-6, 6); d = rng.randint(-6, 6)
            f = sp.expand(a*(x-c)**3 + b*(x-c)) + d; d1 = sp.expand(sp.diff(f, x)); t, s_ = P(6*a, [(c, 1)])
            infl(f, L(d1), str(d1), t, s_, [c], domtext=dom_R().replace("§", "§"), fam="cubic", diff=ch(["easy", "medium"]), center=rng.random() < .35)
        elif k == 1:
            a = ch([1, -1, 2, R(1, 2), R(1, 3), R(1, 12)]); p, q = sorted(rng.sample(range(-3, 4), 2)); e = rng.randint(-3, 3); d = rng.randint(-4, 4)
            f = a*(x**4 - 2*(p+q)*x**3 + 6*p*q*x**2) + e*x + d; d1 = sp.diff(f, x); t, s_ = P(12*a, [(p, 1), (q, 1)])
            infl(f, L(d1), str(d1), t, s_, [p, q], domtext=dom_R(), fam="quartic")
        elif k == 2:
            a = ch([1, -1, 2]); k_ = rng.randint(1, 3); d = rng.randint(-4, 4); f = a*(x**4 - 6*k_**2*x**2) + d; d1 = sp.diff(f, x); t, s_ = P(12*a, [(-k_, 1), (k_, 1)])
            infl(f, L(d1), str(d1), t, s_, [-k_, k_], domtext=dom_R(), fam="biquadratic")
        elif k == 3:
            kk = ch([1, -1, 2, -2]); a = ch([1, 2, -1, 3, 4]); x0 = rng.randint(-3, 3); b = -a*x0 - R(2*a, kk)
            if b.q != 1: continue
            f = (a*x+b)*ex(kk*x); e_ = L(ex(kk*x))
            A = kk*a; B = a + kk*b; t1 = L(A*x+B); t1s = f"({A}*x+({B}))*exp({kk}*x)"
            t2, s2 = P(kk*kk*a, [(x0, 1)], (e_, f"exp({kk}*x)"))
            infl(f, f"({t1}){e_}", t1s, t2, s2, [x0], domtext=dom_R(), fam="exp_lin", rule="prod", diff="bacii", sign=f"ដោយ ${e_}>0$ ជានិច្ច សញ្ញានៃ $§''(x)$ យកតាម ${L(kk*kk*a*(x-x0))}$ ។")
        elif k == 4:
            p, q = sorted(rng.sample(range(-5, 3), 2)); b = -(p+q)-4; c = p*q-2-2*b; g = x**2+b*x+c; f = g*ex(x)
            d1 = x**2+(b+2)*x+b+c; t2, s2 = P(1, [(p, 1), (q, 1)], ("e^{x}", "exp(x)"))
            infl(f, f"({L(d1)})e^{{x}}", f"({d1})*exp(x)", t2, s2, [p, q], domtext=dom_R(), fam="exp_quad", rule="prod", diff="bacii", sign="ដោយ $e^{x}>0$ សញ្ញានៃ $§''(x)$ យកតាមត្រីធា ។")
        elif k == 5:
            a = ch([1, 2, 3, -1]); k_ = rng.randint(1, 3); w = 2*k_*k_; f = a*ex(-x**2/w); e_ = L(ex(-x**2/w))
            t1 = f"{L(-R(2*a, w))}x{e_}"; t2 = "\\frac{" + L(R(4*a, w*w)) + "}{1}" if False else L(R(4*a, w*w)) + f"(x^2-{k_*k_}){e_}"
            infl(f, t1, f"({-R(2*a, w)})*x*exp(-x**2/{w})", t2, f"({R(4*a, w*w)})*(x**2-{k_*k_})*exp(-x**2/{w})", [-k_, k_], domtext=dom_R(), fam="gauss", rule="exp", diff="hard")
        elif k == 6:
            a = ch([1, 2, 3, -1]); k_ = rng.randint(1, 5); b = rng.randint(-3, 3); c = rng.randint(-2, 2); f = a*ln(x**2+k_*k_) + b*x + c
            t1 = f"\\frac{{{2*a}x}}{{x^2+{k_*k_}}}" + (f"{b:+d}" if b else ""); t2 = f"\\frac{{{L(-2*a)}(x^2-{k_*k_})}}{{(x^2+{k_*k_})^2}}"
            infl(f, t1, f"{2*a}*x/(x**2+{k_*k_})+({b})", t2, f"({-2*a})*(x**2-{k_*k_})/(x**2+{k_*k_})**2", [-k_, k_], domtext=f"ដោយ $x^2+{k_*k_}>0$ នោះ $D=IR$ ។", fam="ln_even", rule="chain", diff="hard", sign="ភាគបែងវិជ្ជមាន ដូច្នេះ $§''(x)$ មានសញ្ញាដូចភាគយក ។")
        elif k == 7:
            a = ch([1, 2, 3, 4, 6, -1, -2]); k_ = rng.randint(1, 4); w = 3*k_*k_; f = a/(x**2+w)
            infl(f, f"\\frac{{{L(-2*a)}x}}{{(x^2+{w})^2}}", f"({-2*a})*x/(x**2+{w})**2", f"\\frac{{{6*a}(x^2-{k_*k_})}}{{(x^2+{w})^3}}", f"({6*a})*(x**2-{k_*k_})/(x**2+{w})**3", [-k_, k_], domtext=f"ភាគបែង $x^2+{w}$ មិនស្មើសូន្យ ដូចនេះ $D=IR$ ។", fam="witch", rule="quot", diff="hard", sign="ភាគបែងវិជ្ជមាន ដូច្នេះ $§''(x)$ មានសញ្ញាដូចភាគយក ។")
        elif k == 8:
            n8 = rng.randint(-2, 3); a = ch([1, 2, 3]); w = rng.choice(["lnx2", "lnoverx", "ln2"])
            if w == "ln2":
                b = rng.randint(-3, 3); f = a*ln(x)**2 + b*ln(x); r0 = R(2*a-b, 2*a); c = ex(r0)
                infl(f, f"\\frac{{{L(2*a*ln(x)+b)}}}{{x}}", f"({2*a}*log(x)+({b}))/x", f"\\frac{{{L(-2*a*ln(x)+2*a-b)}}}{{x^2}}", f"({-2*a}*log(x)+({2*a-b}))/x**2", [c], domtext=dpos(), lo=sp.Integer(0), fam="ln2", rule="chain", diff="bacii",
                     rootsent=f"$§''(x)=0$ ឲ្យ $\\ln x={L(r0)}$ នោះ $x={L(c)}$ ។", sign="ដោយ $x^2>0$ សញ្ញានៃ $§''(x)$ យកតាមភាគយក ។")
            elif w == "lnoverx":
                f = (ln(x)+n8)/x; r0 = R(3, 2)-n8; c = ex(r0)
                infl(f, f"\\frac{{{L(1-n8-ln(x))}}}{{x^2}}", f"({1-n8}-log(x))/x**2", f"\\frac{{{L(2*ln(x)+2*n8-3)}}}{{x^3}}", f"(2*log(x)+({2*n8-3}))/x**3", [c], domtext=dpos(), lo=sp.Integer(0), fam="lnx", rule="quot", diff="bacii",
                     rootsent=f"$§''(x)=0$ ឲ្យ $\\ln x={L(r0)}$ នោះ $x={L(c)}$ ។", sign="ដោយ $x^3>0$ លើ $D$ សញ្ញានៃ $§''(x)$ យកតាមភាគយក ។")
            else:
                f = a*x**2*(ln(x)+n8); r0 = -R(3, 2)-n8; c = ex(r0)
                infl(f, f"{L(a)}x({L(2*ln(x)+2*n8+1)})", f"{a}*x*(2*log(x)+({2*n8+1}))", f"{L(a)}({L(2*ln(x)+2*n8+3)})", f"{a}*(2*log(x)+({2*n8+3}))", [c], domtext=dpos(), lo=sp.Integer(0), fam="x2lnx", rule="prod", diff="bacii",
                     rootsent=f"$§''(x)=0$ ឲ្យ $\\ln x={L(r0)}$ នោះ $x={L(c)}$ ។")
        elif k == 9:
            a = ch([1, 2, 3, -1]); b = rng.randint(-3, 3); d = rng.randint(-3, 3); T = ch([0, 1])
            if T == 0:
                f = a*sp.sin(x)+b*x+d; infl(f, f"{L(a*sp.cos(x))}" + (f"{b:+d}" if b else ""), f"{a}*cos(x)+({b})", L(-a*sp.sin(x)), f"({-a})*sin(x)", [pi], lo=sp.Integer(0), hi=2*pi, lc=True, hc=True, fam="trig", rule="trig", diff="hard", given_dom="[0;2\\pi]", rootsent="លើចន្លោះបើក $(0;2\\pi)$ សមីការ $§''(x)=0$ ឲ្យ $\\sin x=0$ នោះ $x=\\pi$ ។")
            else:
                f = a*sp.cos(x)+b*x+d; infl(f, f"{L(-a*sp.sin(x))}" + (f"{b:+d}" if b else ""), f"{-a}*sin(x)+({b})", L(-a*sp.cos(x)), f"({-a})*cos(x)", [pi/2, 3*pi/2], lo=sp.Integer(0), hi=2*pi, lc=True, hc=True, fam="trig", rule="trig", diff="hard", given_dom="[0;2\\pi]", rootsent="$§''(x)=0$ ឲ្យ $\\cos x=0$ នោះ $x=\\frac{\\pi}{2}$ ឬ $x=\\frac{3\\pi}{2}$ ។")
        elif k == 10:
            a = rng.randint(1, 4); b = rng.randint(1, 5); c = rng.randint(-4, 4); f = a*x**2 + b*ex(x) + c
            t = f"{2*a}+{b if b>1 else ''}e^{{x}}"
            infl(f, f"{2*a}x+{b if b>1 else ''}e^{{x}}", f"{2*a}*x+{b}*exp(x)", t, f"{2*a}+{b}*exp(x)", [], domtext=dom_R(), fam="none_exp", rule="exp", rootsent=f"ដោយ $e^{{x}}>0$ នោះ $§''(x)={t}>0$ ជានិច្ច ។")
        else:
            a = rng.randint(1, 4); b = rng.randint(1, 6); c = rng.randint(-4, 4); f = a*x**2 - b*ln(x) + c
            t = f"{2*a}+\\frac{{{b}}}{{x^2}}"
            infl(f, f"{2*a}x-\\frac{{{b}}}{{x}}", f"{2*a}*x-{b}/x", t, f"{2*a}+{b}/x**2", [], domtext=dpos(), lo=sp.Integer(0), fam="none_ln", rule="ln", rootsent="ចំពោះគ្រប់ $x>0$ ដេរីវេទី២វិជ្ជមានជានិច្ច ។")

# ---------- inequalities ----------
def T_ineq(st, lhs, rel, rhs, quant, gname="g", diff="hard"):
    st.nm = gname
    good = "min"
    ex_ = [e for e in st.ext if e[1] == good]
    assert len(ex_) == 1 and ex_[0][2] == 0, (str(st.f), st.ext)
    v, _, val = ex_[0]
    q = ch([f"ស្រាយបញ្ជាក់ថា ${lhs}{rel}{rhs}$ ចំពោះគ្រប់ ${quant}$ ។", f"ដោយប្រើដេរីវេ ចូរបង្ហាញថា ${lhs}{rel}{rhs}$ ចំពោះគ្រប់ ${quant}$ ។", f"ចំពោះគ្រប់ ${quant}$ ចូរស្រាយបញ្ជាក់វិសមភាព ${lhs}{rel}{rhs}$ ។", f"បង្ហាញថាវិសមភាព ${lhs}{rel}{rhs}$ ពិតចំពោះគ្រប់ ${quant}$ រួចបញ្ជាក់ករណីស្មើ ។"])
    tb = st.signtable()
    sol = lines(ch([f"តាង $§(x)={L(st.f)}$ ចំពោះ ${quant}$ ។", f"យើងពិនិត្យអនុគមន៍ជំនួយ $§(x)={L(st.f)}$ នៅលើ ${quant}$ ។", f"យកអង្គទាំងអស់មកម្ខាង ហើយតាង $§(x)={L(st.f)}$ ។"]),
        st.deriv_block().replace("ចំពោះគ្រប់ $x\\in D$ ", "").replace("លើ $D$ ", ""), st.roots, st.sign, ch(["សញ្ញានៃ $§'(x)$៖", "តារាងសញ្ញា៖"]), f"$${tb}$$",
        f"អនុគមន៍ $§$ មាន{'អប្បបរមា' if good=='min' else 'អតិបរមា'} $§({L(v)})=0$ ត្រង់ $x={L(v)}$ ។", f"នោះ $§(x)\\geq 0$ ចំពោះគ្រប់ ${quant}$ ។",
        f"{ch(CONC)} $\\boxed{{{lhs}{rel}{rhs}}}$ ចំពោះគ្រប់ ${quant}$ ហើយសញ្ញាស្មើកើតមានត្រង់ $x={L(v)}$ ។")
    add(st, "inequality_proof", diff, q, sol, f"{lhs}{rel}{rhs}", st.checks(), [Dg("sign_table", tb, "តារាងសញ្ញានៃដេរីវេនៃអនុគមន៍ជំនួយ")])

def gen_ineq(n):
    start = len(ROWS)
    def go(f, Fd, lhs, rel, rhs, quant, diff="hard"):
        key = str(sp.diff(f, x))
        if key in SEEN: return
        st = St(Fd)
        if st.ok:
            SEEN.add(key); T_ineq(st, lhs, rel, rhs, quant, ch(["g", "h", "\\varphi"]) if False else ch(["g", "h"]), diff)
    for _ in range(n*8):
        if len(ROWS)-start >= n: break
        k = rng.randint(0, 10)
        if k == 0:
            a = rng.randint(-4, 5); f = ex(x-a) - x + a - 1
            if a == 0: continue
            e_ = L(ex(x-a)); go(f, F(f, "exp", [], f"{e_}-1", f"exp(x-({a}))-1", [sp.Integer(a)], roots=f"$§'(x)=0$ ឲ្យ ${e_}=1$ នោះ $x={a}$ ។", sign=f"ដោយ ${e_}$ កើន នោះ $§'(x)<0$ ពេល $x<{a}$ និង $§'(x)>0$ ពេល $x>{a}$ ។"), e_, "\\geq", L(x-a+1), "x\\in IR")
        elif k == 1:
            kk = ch([2, 3, 4, 5, R(1, 2), R(1, 3), -1, -2, -3]); f = ex(kk*x) - kk*x - 1; e_ = L(ex(kk*x))
            go(f, F(f, "exp", [], f"{L(kk)}({e_}-1)", f"({kk})*(exp({kk}*x)-1)", [sp.Integer(0)], roots=f"$§'(x)=0$ ឲ្យ ${e_}=1$ នោះ $x=0$ ។"), e_, "\\geq", L(kk*x+1), "x\\in IR")
        elif k == 2:
            a = rng.randint(2, 9); f = x/R(a) + ln(a) - 1 - ln(x)
            go(f, F(f, "ln", [f"\\frac{{1}}{{{a}}}-\\frac{{1}}{{x}}"], f"\\frac{{x-{a}}}{{{a}x}}", f"(x-{a})/({a}*x)", [sp.Integer(a)], domtext=dpos(), lo=sp.Integer(0), roots=zt([a]), sign=f"ដោយ $x>0$ នោះ $§'(x)$ មានសញ្ញាដូច $x-{a}$ ។"), "\\ln x", "\\leq", L(x/R(a)) + f"+\\ln {a}-1", "x>0")
        elif k == 3:
            a = rng.randint(2, 9); f = x*ln(x) - (1+ln(a))*x + a
            go(f, F(f, "prod", [f"\\ln x+1-(1+\\ln {a})"], f"\\ln x-\\ln {a}", f"log(x)-log({a})", [sp.Integer(a)], domtext=dpos(), lo=sp.Integer(0), roots=f"$§'(x)=0$ ឲ្យ $\\ln x=\\ln {a}$ នោះ $x={a}$ ។", sign="ដោយ $\\ln x$ ជាអនុគមន៍កើន សញ្ញានៃ $§'(x)$ កំណត់បានភ្លាម ។"), "x\\ln x", "\\geq", f"(1+\\ln {a})x-{a}", "x>0")
        elif k == 4:
            nn = rng.randint(3, 7); kk = rng.randint(1, 4); f = x**nn - nn*kk**(nn-1)*x + (nn-1)*kk**nn
            if abs(f.subs(x, 0)) > 3000: continue
            lhs = L(x**nn + (nn-1)*kk**nn); rhs = L(nn*kk**(nn-1)*x)
            go(f, F(f, "poly", [], f"{nn}(x^{{{nn-1}}}-{kk**(nn-1)})", f"{nn}*(x**{nn-1}-{kk**(nn-1)})", [sp.Integer(kk)], domtext="", lo=sp.Integer(0), roots=f"លើ $x>0$ សមីការ $x^{{{nn-1}}}={kk**(nn-1)}$ ឲ្យ $x={kk}$ ។"), lhs, "\\geq", rhs, "x>0")
        elif k == 5:
            a = rng.randint(1, 5); kk = rng.randint(1, 6); f = a*x + R(a*kk*kk)/x - 2*a*kk
            t = frac(*P(a, [(-kk, 1), (kk, 1)]), "x^2", "x**2")
            go(f, F(f, "quot", [f"{a}-\\frac{{{a*kk*kk}}}{{x^2}}"], t[0], t[1], [sp.Integer(kk)], lo=sp.Integer(0), roots=f"លើ $x>0$ គេបាន $§'(x)=0$ ឲ្យ $x={kk}$ ។", sign=f"ដោយ $x>0$ នោះ $§'(x)$ មានសញ្ញាដូច $x-{kk}$ ។"), L(a*x) + f"+\\frac{{{a*kk*kk}}}{{x}}", "\\geq", str(2*a*kk), "x>0")
        elif k == 6:
            kk = rng.randint(1, 5); f = x**2 + R(2*kk**3)/x - 3*kk**2
            t = f"\\frac{{2(x^3-{kk**3})}}{{x^2}}"
            go(f, F(f, "quot", [f"2x-\\frac{{{2*kk**3}}}{{x^2}}"], t, f"2*(x**3-{kk**3})/x**2", [sp.Integer(kk)], lo=sp.Integer(0), roots=f"$§'(x)=0$ ឲ្យ $x^3={kk**3}$ នោះ $x={kk}$ ។", sign=f"ដោយ $x^2>0$ នោះ $§'(x)$ មានសញ្ញាដូច $x^3-{kk**3}$ ។"), f"x^2+\\frac{{{2*kk**3}}}{{x}}", "\\geq", str(3*kk**2), "x>0")
        elif k == 7:
            a = rng.randint(-3, 3); 
            if a == 0: continue
            f = ex(x) - ex(a)*x + ex(a)*(a-1); ea = L(ex(a))
            go(f, F(f, "exp", [], f"e^{{x}}-{ea}", f"exp(x)-exp({a})", [sp.Integer(a)], roots=f"$§'(x)=0$ ឲ្យ $e^{{x}}={ea}$ នោះ $x={a}$ ។"), "e^{x}", "\\geq", f"{ea}({L(x-a+1)})", "x\\in IR")
        elif k == 8:
            kk = ch([2, 3, 4, 5, R(1, 2), R(1, 3)]); f = kk*x - ln(1+kk*x); lo = -1/R(kk); den = L(1+kk*x)
            go(f, F(f, "chain", [f"{L(kk)}-\\frac{{{L(kk)}}}{{{den}}}"], f"\\frac{{{L(kk*kk)}x}}{{{den}}}", f"({kk*kk})*x/({1+kk*x})", [sp.Integer(0)], lo=lo, roots="$§'(x)=0$ ឲ្យ $x=0$ ។", sign=f"ដោយ ${den}>0$ សញ្ញានៃ $§'(x)$ ដូចសញ្ញានៃ $x$ ។"), L(ln(1+kk*x)), "\\leq", L(kk*x), f"x>{L(lo)}")
        elif k == 9:
            kk = rng.randint(1, 8); f = (x+kk*kk)/(2*kk) - sq(x)
            go(f, F(f, "sqrt", [], f"\\frac{{\\sqrt{{x}}-{kk}}}{{{2*kk}\\sqrt{{x}}}}", f"(sqrt(x)-{kk})/({2*kk}*sqrt(x))", [sp.Integer(kk*kk)], lo=sp.Integer(0), roots=f"$§'(x)=0$ ឲ្យ $\\sqrt{{x}}={kk}$ នោះ $x={kk*kk}$ ។"), "\\sqrt{x}", "\\leq", f"\\frac{{{L(x+kk*kk)}}}{{{2*kk}}}", "x>0")
        else:
            a = rng.randint(2, 9); f = ln(x) - ln(a) - 1 + R(a)/x
            go(f, F(f, "ln", [f"\\frac{{1}}{{x}}-\\frac{{{a}}}{{x^2}}"], f"\\frac{{x-{a}}}{{x^2}}", f"(x-{a})/x**2", [sp.Integer(a)], lo=sp.Integer(0), roots=zt([a]), sign=f"ភាគបែងវិជ្ជមាន ដូច្នេះ $§'(x)$ មានសញ្ញាដូច $x-{a}$ ។"), "\\ln x", "\\geq", f"\\ln {a}+1-\\frac{{{a}}}{{x}}", "x>0")

def T_bound(st):
    """f(x)>=min on connected domain, single extremum."""
    e = [t for t in st.ext if t[1]]
    if len(e) != 1 or st.excl or len(st.iv) != 2: return T_ext(st)
    v, t, val = e[0]; rel = "\\geq" if t == "min" else "\\leq"
    D = st.D_tex()
    q = ch([f"បង្ហាញថា $§(x){rel}{L(val)}$ ចំពោះគ្រប់ $x\\in {D}$ ។", f"សិក្សាអថេរភាពនៃ $§$ រួចទាញបញ្ជាក់ថា $§(x){rel}{L(val)}$ ចំពោះគ្រប់ $x\\in {D}$ ។", f"ទាញរក{'តម្លៃតូចបំផុត' if t=='min' else 'តម្លៃធំបំផុត'}នៃ $§$ រួចស្រាយបញ្ជាក់វិសមភាពដែលកើតចេញពីវា ។"])
    tb = st.signtable()
    sol = lines(st.domtext, st.deriv_block(), st.roots, st.sign, f"$${tb}$$", st.mono_text(1), st.ext_text(), f"ដោយ $§$ មាន{'អប្បបរមា' if t=='min' else 'អតិបរមា'}តែមួយគត់ លើ $D$ នោះ {'វាជាតម្លៃតូចបំផុត' if t=='min' else 'វាជាតម្លៃធំបំផុត'} ។", f"{ch(CONC)} $\\boxed{{§(x){rel}{L(val)}}}$ ចំពោះគ្រប់ $x\\in {D}$ ។")
    add(st, "inequality_from_extremum", "hard", f"{ch(STEM)} {st.problem_f()} ។ {q}", sol, f"{st.nm}(x){rel}{L(val)}", st.checks(), [Dg("sign_table", tb, ch(ALT_S))])

# ---------- given f' ----------
def T_given():
    nr = ch([2, 3, 3]); r = sorted(rng.sample(range(-5, 6), nr)); mult = [ch([1, 1, 2, 3]) for _ in r]; c = ch([1, 2, -1, 3, -2])
    tail = ch([None, None, ("e^{x}", "exp(x)"), ("(x^2+1)", "(x**2+1)")])
    tx, st_ = P(c, list(zip(r, mult)), tail); key = "given" + st_
    if key in SEEN or not any(m % 2 for m in mult): return
    SEEN.add(key)
    e = sp.sympify(st_, locals={"x": x, "exp": ex})
    b = [-oo] + r + [oo]; sg = []; ts = []
    for u, v in zip(b, b[1:]):
        t = between(u, v); ts.append(t); sg.append(1 if float(e.subs(x, t)) > 0 else -1)
    xr = []; fr = []
    for i, u in enumerate(b):
        xr.append(LT(u)); fr.append("0" if abs(u) != oo else "")
        if i < len(sg): xr.append(""); fr.append("+" if sg[i] > 0 else "-")
    tb = "\\begin{array}{c|" + "c"*len(xr) + "}\nx & " + " & ".join(xr) + " \\\\\n\\hline\nf'(x) & " + " & ".join(fr) + "\n\\end{array}"
    inc = [itv(b[i], b[i+1]) for i in range(len(sg)) if sg[i] > 0]; dec = [itv(b[i], b[i+1]) for i in range(len(sg)) if sg[i] < 0]
    mx = [r[i] for i in range(len(r)) if sg[i] > 0 > sg[i+1]]; mn = [r[i] for i in range(len(r)) if sg[i] < 0 < sg[i+1]]; no = [r[i] for i in range(len(r)) if sg[i] == sg[i+1]]
    q = ch(["គេដឹងថាអនុគមន៍ $f$ មានដេរីវេលើ $IR$ កំណត់ដោយ", "អនុគមន៍ $f$ មានដេរីវេទី១", "សន្មតថា $f$ ជាអនុគមន៍ដែលមានដេរីវេ"])
    prob = q + f" $f'(x)={tx}$ ។ " + ch(["រកចន្លោះកើន ចន្លោះចុះ និងអាប់ស៊ីសនៃចំណុចបរមានៃ $f$ ។", "សង់តារាងសញ្ញានៃ $f'(x)$ ហើយបញ្ជាក់ថា $f$ មានអតិបរមា ឬអប្បបរមាត្រង់ណា ។", "តើ $f$ មានបរមាធៀបត្រង់តម្លៃ $x$ ណាខ្លះ ?"])
    nt = []
    for rr, mm in zip(r, mult):
        nt.append(f"កត្តា ${'x' if rr==0 else '('+L(x-rr).replace(' ','')+')'}{'^{'+str(mm)+'}' if mm>1 else ''}$ " + ("ប្ដូរសញ្ញាត្រង់ " if mm % 2 else "មិនប្ដូរសញ្ញាត្រង់ ") + f"$x={rr}$ ព្រោះស្វ័យគុណ{'សេស' if mm%2 else 'គូ'} ។")
    if tail: nt.append(f"កត្តា ${tail[0]}$ វិជ្ជមានជានិច្ច ដូច្នេះវាមិនប៉ះពាល់សញ្ញាទេ ។")
    parts = []
    if mx: parts.append("អតិបរមាត្រង់ " + " ឬ ".join(f"$x={v}$" for v in mx))
    if mn: parts.append("អប្បបរមាត្រង់ " + " ឬ ".join(f"$x={v}$" for v in mn))
    sol = lines("$f'(x)=0$ ឲ្យ " + " ឬ ".join(f"$x={v}$" for v in r) + " ។", *nt, "តារាងសញ្ញានៃ $f'(x)$៖", f"$${tb}$$",
                ("$f$ កើនលើ " + " និង ".join(f"${t}$" for t in inc) + " ។") if inc else "", ("$f$ ចុះលើ " + " និង ".join(f"${t}$" for t in dec) + " ។") if dec else "",
                ("ត្រង់ " + " និង ".join(f"$x={v}$" for v in no) + " ដេរីវេស្មើសូន្យ តែមិនប្ដូរសញ្ញា ដូចនេះមិនមែនជាបរមាទេ ។") if no else "", f"{ch(CONC)} $f$ មាន" + " និង".join(parts) + " ។" if parts else f"{ch(CONC)} $f$ គ្មានបរមាធៀបទេ ។")
    chs = [check(f"subs({st_},x,{v})", "0", "root of f'") for v in r] + [check(f"subs({st_},x,{t})" + (">0" if g > 0 else "<0"), "True", "sign") for t, g in zip(ts, sg)]
    ROWS.append(make_row("variation", "sign_of_given_derivative", "medium", prob, sol, ",\\ ".join([f"\\text{{អតិបរមាធៀប}}:x={v}" for v in mx] + [f"\\text{{អប្បបរមាធៀប}}:x={v}" for v in mn]) or "\\varnothing", chs, GEN, diagrams=[Dg("sign_table", tb, ch(ALT_S))]))

# ---------- unique root ----------
def T_root():
    k = rng.randint(0, 4)
    if k == 0:
        p, q = rng.randint(1, 9), rng.randint(-20, 20); f = x**3+p*x+q; dt, ds = f"3x^2+{p}", f"3*x**2+{p}"; why = f"$§'(x)=3x^2+{p}>0$ ចំពោះគ្រប់ $x$"; lo = -oo
    elif k == 1:
        q = rng.randint(2, 12); a = ch([1, 2, 3]); f = ex(x)+a*x-q; dt, ds = f"e^{{x}}+{a}", f"exp(x)+{a}"; why = f"$§'(x)=e^{{x}}+{a}>0$ ជានិច្ច"; lo = -oo
    elif k == 2:
        q = rng.randint(1, 9); a = ch([1, 2, 3]); f = ln(x)+a*x-q; dt, ds = f"\\frac{{1}}{{x}}+{a}", f"1/x+{a}"; why = f"$§'(x)=\\frac{{1}}{{x}}+{a}>0$ ចំពោះ $x>0$"; lo = sp.Integer(0)
    elif k == 3:
        q = rng.randint(-15, 15); p = rng.randint(1, 4); f = x**5+p*x+q; dt, ds = f"5x^4+{p}", f"5*x**4+{p}"; why = f"$§'(x)=5x^4+{p}>0$ ជានិច្ច"; lo = -oo
    else:
        a = rng.randint(2, 5); q = rng.randint(-6, 6); f = a*x+sp.cos(x)+q; dt, ds = f"{a}-\\sin x", f"{a}-sin(x)"; why = f"$§'(x)={a}-\\sin x>0$ ព្រោះ $\\sin x\\leq 1$"; lo = -oo
    if str(f) in SEEN: return
    fn = sp.lambdify(x, f, "math"); n = None
    for c in range(-6 if lo == -oo else 1, 12):
        if fn(c) == 0: return
        if fn(c) < 0 < fn(c+1): n = c; break
    if n is None: return
    SEEN.add(str(f)); nm = ch(["f", "g"])
    a_, b_ = sp.expand(f.subs(x, n)), sp.expand(f.subs(x, n+1))
    prob = f"{ch(STEM)} ${nm}(x)={L(f)}$ ។ " + ch([f"ស្រាយបញ្ជាក់ថាសមីការ ${nm}(x)=0$ មានឫសតែមួយគត់ $\\alpha$ ហើយ ${n}<\\alpha<{n+1}$ ។", f"បង្ហាញថា ${nm}$ កើនជានិច្ច រួចទាញបញ្ជាក់ថាសមីការ ${nm}(x)=0$ មានឫសតែមួយគត់នៅចន្លោះ $({n};{n+1})$ ។"])
    Dt = "(0;+\\infty)" if lo == 0 else "IR"
    sol = lines(f"អនុគមន៍ $§$ ជាប់ និងមានដេរីវេលើដែនកំណត់ $D={Dt}$ ។", f"យើងបាន $§'(x)={dt}$ ។", f"ដោយ {why} នោះ $§$ ជាអនុគមន៍កើនលើ $D$ ទាំងមូល ដូច្នេះសមីការ $§(x)=0$ មានឫសច្រើនបំផុតមួយលើ $D$ ។",
                f"ម្យ៉ាងទៀត $§({n})={L(a_)}<0$ និង $§({n+1})={L(b_)}>0$ ។", f"តាមទ្រឹស្ដីបទតម្លៃកណ្ដាល មាន $\\alpha\\in({n};{n+1})$ ដែល $§(\\alpha)=0$ ។", f"{ch(CONC)} សមីការមានឫសតែមួយគត់ $\\boxed{{\\alpha\\in({n};{n+1})}}$ ។").replace("§", nm)
    chs = [check(f"diff({f},x)", ds, "derivative"), check(f"subs({f},x,{n})<0", "True", "f(n)<0"), check(f"subs({f},x,{n+1})>0", "True", "f(n+1)>0"), check(f"subs({f},x,{n})", str(a_), "value"), check(f"subs({f},x,{n+1})", str(b_), "value")]
    ROWS.append(make_row("variation", "unique_root_by_monotonicity", "hard", prob, sol, f"\\alpha\\in({n};{n+1})", chs, GEN))

# ---------- parameters ----------
def T_param():
    k = rng.randint(0, 7); m = sp.Symbol("m")
    if k in (0, 1):
        u, v = sorted(rng.sample(range(-4, 6), 2)); d = rng.randint(-4, 4); s_ = 1 if k == 0 else -1
        fm = lambda M: s_*(x**3 - 3*M*x**2 + 3*((u+v)*M - u*v)*x) + d
        fx = fm(m); key = str(fx)
        if key in SEEN: return
        SEEN.add(key); nm = "f"; word = "កើន" if s_ > 0 else "ចុះ"; c3 = 3*s_
        e_ = L(sp.expand(m**2 - (u+v)*m + u*v))
        cc = L((u+v)*m - u*v)
        cc0 = L((u+v)*m - u*v)
        ptx = (f"x^3-3mx^2+3({cc0})x{d:+d}" if s_ > 0 else f"-x^3+3mx^2-3({cc0})x{d:+d}").replace("x+0", "x")
        prob = f"{ch(STEM)} $f(x)={ptx}$ ដែល $m$ ជាប៉ារ៉ាម៉ែត្រ ។ " + ch([f"រកតម្លៃ $m$ ដើម្បីឲ្យ $f$ ជាអនុគមន៍{word}លើ $IR$ ។", f"កំណត់ $m$ ដើម្បីឲ្យអនុគមន៍{word}ជានិច្ច ។"])
        sol = lines("$D=IR$ ។", f"យើងបាន $f'(x)={c3}(x^2-2mx+{cc})$ ។".replace("(x^2-2mx+-", "(x^2-2mx-"), f"$f$ {word}លើ $IR$ លុះត្រាតែ $f'(x)$ មិនប្ដូរសញ្ញា ពោលគឺត្រីធា $x^2-2mx+({cc})$ មាន $\\Delta'\\leq 0$ ។",
                    f"$$\\Delta'=m^2-({cc})={e_}=(m{-u:+d})(m{-v:+d})$$".replace("m+0", "m").replace("m-0", "m"), f"$\\Delta'\\leq 0$ លុះត្រាតែ ${u}\\leq m\\leq {v}$ ។", f"ដូចនេះ $\\boxed{{{u}\\leq m\\leq {v}}}$ ។")
        chs = [check(f"diff({fm(u)},x)", f"{c3}*(x-({u}))**2", "double root at m=u"), check(f"diff({fm(v)},x)", f"{c3}*(x-({v}))**2", "double root at m=v"),
               check(f"subs(diff({fm(v+1)},x),x,{v+1})" + ("<0" if s_ > 0 else ">0"), "True", "outside the range f' changes sign")]
        ROWS.append(make_row("variation", "parameter_monotonic", "hard", prob, sol, f"{u}\\leq m\\leq {v}", chs, GEN)); return
    if k == 2:
        a = rng.randint(-6, 6); b = ch([1, 2, 3, 4, -1, -2, -3]); key = f"hom{a},{b}"
        if key in SEEN or a == 0: return
        SEEN.add(key); t = R(a, b); den = L(x+b); w = ch([1, -1]); 
        rel = ">" if (b > 0) == (w > 0) else "<"; word = "កើន" if w > 0 else "ចុះ"
        samp = t + 1 if rel == ">" else t - 1; bad = t - 1 if rel == ">" else t + 1
        prob = f"{ch(STEM)} $f(x)=\\frac{{mx{a:+d}}}{{{den}}}$ ។ រកតម្លៃ $m$ ដើម្បីឲ្យ $f$ {word}លើចន្លោះនីមួយៗនៃដែនកំណត់ ។"
        sol = lines(f"ដែនកំណត់៖ $D=IR-\\{{{-b}\\}}$ ។", f"$$f'(x)=\\frac{{m({den})-(mx{a:+d})}}{{({den})^2}}=\\frac{{{b}m{-a:+d}}}{{({den})^2}}$$".replace("{1m", "{m").replace("{-1m", "{-m"), f"សញ្ញានៃ $f'(x)$ យកតាមភាគយក ព្រោះភាគបែងវិជ្ជមាន ។",
                    f"$f$ {word}លុះត្រាតែ ${b}m{-a:+d}{'>' if w>0 else '<'}0$ ឬ $m{rel}{L(t)}$ ។".replace("$1m", "$m").replace("$-1m", "$-m"), f"ដូចនេះ $\\boxed{{m{rel}{L(t)}}}$ ។")
        F_ = lambda M: (M*x+a)/(x+b)
        chs = [check(f"subs(diff({F_(samp)},x),x,{-b+1})" + (">0" if w > 0 else "<0"), "True", "inside range"), check(f"subs(diff({F_(bad)},x),x,{-b+1})" + ("<0" if w > 0 else ">0"), "True", "outside range"), check(f"diff({F_(t)},x)", "0", "constant at the bound")]
        ROWS.append(make_row("variation", "parameter_monotonic", "medium", prob, sol, f"m{rel}{L(t)}", chs, GEN)); return
    if k == 3:
        p, q = rng.sample(range(-3, 5), 2)
        if p == 0 or (3*(p+q)) % 2: return
        a = -R(3, 2)*(p+q); b = 3*p*q; c = rng.randint(-5, 5); f = x**3+a*x**2+b*x+c; y0 = f.subs(x, p)
        key = f"ab{p},{q},{c}"
        if key in SEEN: return
        SEEN.add(key); typ = "អតិបរមា" if p < q else "អប្បបរមា"
        prob = f"{ch(STEM)} $f(x)=x^3+ax^2+bx{c:+d}$ ។ រកចំនួនពិត $a$ និង $b$ ដើម្បីឲ្យ $f$ មាន{typ}ស្មើនឹង ${y0}$ ត្រង់ $x={p}$ ។".replace("x+0", "x")
        A1, B1 = 2*p, -3*p*p; A2, B2 = p*p, y0-c-p**3
        sol = lines("យើងមាន $f'(x)=3x^2+2ax+b$ ។", f"លក្ខខណ្ឌចាំបាច់៖ $f'({p})=0$ និង $f({p})={y0}$ ។", f"$$\\begin{{cases}}{L(3*p*p)}+({2*p})a+b=0\\\\ {p**3}+({p*p})a+({p})b{c:+d}={y0}\\end{{cases}}$$", f"ដោះស្រាយប្រព័ន្ធនេះ គេបាន $a={L(a)}$ និង $b={L(b)}$ ។",
                    f"ផ្ទៀងផ្ទាត់៖ $f'(x)={L(3)}(x{-p:+d})(x{-q:+d})$ ".replace("x+0", "x").replace("x-0", "x") + f"ហើយ $f''({p})={6*p+2*a}{'<' if p<q else '>'}0$ នោះ $x={p}$ ជា{typ}ពិតប្រាកដ ។", f"ដូចនេះ $\\boxed{{a={L(a)},\\ b={L(b)}}}$ ។")
        chs = [check(f"subs(diff({f},x),x,{p})", "0", "f'(p)=0"), check(f"subs({f},x,{p})", str(y0), "value"), check(f"subs(diff({f},x,2),x,{p})" + ("<0" if p < q else ">0"), "True", "type"), check(f"diff({f},x)", f"3*(x-({p}))*(x-({q}))", "factored")]
        ROWS.append(make_row("variation", "parameter_extremum", "hard", prob, sol, f"a={L(a)},\\ b={L(b)}", chs, GEN)); return
    if k == 4:
        x0 = ch([-3, -2, -1, 1, 2, 3, 4]); a = ch([1, 2, 3, 4, R(1, 2)]); b = a*x0*x0; y0 = 2*a*x0; key = f"axb{x0},{a}"
        if key in SEEN: return
        SEEN.add(key); f = a*x+b/x; typ = "អប្បបរមា" if x0 > 0 else "អតិបរមា"
        prob = f"{ch(STEM)} $f(x)=ax+\\frac{{b}}{{x}}$ ។ រក $a$ និង $b$ ដើម្បីឲ្យក្រាបនៃ $f$ មានចំណុចបរមា $A({x0};{L(y0)})$ ។"
        sol = lines("$D=IR-\\{0\\}$ ហើយ $f'(x)=a-\\frac{b}{x^2}$ ។", f"$A$ ជាចំណុចបរមាលុះត្រាតែ $f'({x0})=0$ និង $f({x0})={L(y0)}$ ។", f"$$\\begin{{cases}}a-\\frac{{b}}{{{x0*x0}}}=0\\\\ ({x0})a+\\frac{{b}}{{{x0}}}={L(y0)}\\end{{cases}}$$", f"សមីការទីមួយឲ្យ $b={x0*x0}a$ ។ ជំនួសក្នុងសមីការទីពីរ គេបាន ${2*x0}a={L(y0)}$ នោះ $a={L(a)}$ និង $b={L(b)}$ ។",
                    f"ចំពោះតម្លៃទាំងនេះ $f'(x)$ ប្ដូរសញ្ញាត្រង់ $x={x0}$ ហើយ $A$ ជាចំណុច{typ} ។", f"ដូចនេះ $\\boxed{{a={L(a)},\\ b={L(b)}}}$ ។")
        chs = [check(f"subs(diff({f},x),x,{x0})", "0", "f'=0"), check(f"subs({f},x,{x0})", str(y0), "value"), check(f"subs(diff({f},x,2),x,{x0})" + (">0" if x0 > 0 else "<0"), "True", "type")]
        ROWS.append(make_row("variation", "parameter_extremum", "hard", prob, sol, f"a={L(a)},\\ b={L(b)}", chs, GEN)); return
    if k == 5:
        x0 = ch([-3, -2, 1, 2, 3, 4]); b = ch([1, 2, 3, -1, -2, 4, 5, 6]); 
        a = -R(b, x0+1); key = f"exab{x0},{b}"
        if key in SEEN or a.q != 1: return
        SEEN.add(key); f = (a*x+b)*ex(x)
        prob = f"{ch(STEM)} $f(x)=(ax+b)e^{{x}}$ ។ គេដឹងថា $f(0)={b}$ ហើយ $f$ មានបរមាត្រង់ $x={x0}$ ។ រក $a$ និង $b$ ។"
        sol = lines(f"$f(0)=b$ នោះ $b={b}$ ។", "តាមរូបមន្ត $(uv)'=u'v+uv'$ គេបាន $f'(x)=(ax+a+b)e^{x}$ ។", f"ដោយ $e^{{x}}>0$ លក្ខខណ្ឌ $f'({x0})=0$ ឲ្យ $({x0})a+a+b=0$ ។", f"នោះ ${x0+1}a=-{b}$ ".replace("--", "") + f"ឬ $a={L(a)}$ ។", f"ពេលនោះ $f'(x)=({L(a*x+a+b)})e^{{x}}$ ប្ដូរសញ្ញាត្រង់ $x={x0}$ ។", f"ដូចនេះ $\\boxed{{a={L(a)},\\ b={b}}}$ ។")
        chs = [check(f"subs({f},x,0)", str(b), "f(0)"), check(f"subs(diff({f},x),x,{x0})", "0", "f'(x0)=0"), check(f"diff({f},x)", f"({a}*x+({a+b}))*exp(x)", "derivative")]
        ROWS.append(make_row("variation", "parameter_extremum", "hard", prob, sol, f"a={L(a)},\\ b={b}", chs, GEN)); return
    if k == 6:
        x0 = rng.randint(2, 7); a0 = ch([1, 2, 3, -1, -2]); b = -a0*x0; key = f"lnab{x0},{a0}"
        if key in SEEN: return
        SEEN.add(key); f = a0*x+b*ln(x)
        prob = f"{ch(STEM)} $f(x)=ax+b\\ln x$ ចំពោះ $x>0$ ។ គេដឹងថា $f(1)={a0}$ ហើយ $f$ មានបរមាត្រង់ $x={x0}$ ។ រក $a$ និង $b$ រួចគណនាតម្លៃបរមា ។"
        v = sp.expand(f.subs(x, x0)); typ = "អប្បបរមា" if a0 > 0 else "អតិបរមា"
        sol = lines(f"$f(1)=a$ នោះ $a={a0}$ ។", "ដោយ $(\\ln x)'=\\frac{1}{x}$ គេបាន $f'(x)=a+\\frac{b}{x}$ ។", f"$f'({x0})=0$ ឲ្យ ${a0}+\\frac{{b}}{{{x0}}}=0$ នោះ $b={b}$ ។", f"ពេលនោះ $f'(x)=\\frac{{{L(a0*x+b)}}}{{x}}$ ប្ដូរសញ្ញាត្រង់ $x={x0}$ ដូចនេះជា{typ} ។", f"តម្លៃបរមាគឺ $f({x0})={L(v)}$ ។", f"ដូចនេះ $\\boxed{{a={a0},\\ b={b}}}$ ។")
        chs = [check(f"subs({f},x,1)", str(a0), "f(1)"), check(f"subs(diff({f},x),x,{x0})", "0", "f'=0"), check(f"subs({f},x,{x0})", str(v), "extreme value")]
        ROWS.append(make_row("variation", "parameter_extremum", "hard", prob, sol, f"a={a0},\\ b={b}", chs, GEN)); return
    p = rng.randint(-3, 3); t = rng.randint(-5, 5); q = rng.randint(-5, 5); a = -3*p; b = t + 3*p*p; c = q - p**3 - a*p**2 - b*p; key = f"infl{p},{t},{q}"
    if key in SEEN: return
    SEEN.add(key); f = x**3+a*x**2+b*x+c
    prob = f"{ch(STEM)} $f(x)=x^3+ax^2+bx+c$ ។ រក $a,b,c$ ដើម្បីឲ្យខ្សែកោងមានចំណុចរបត់ $I({p};{q})$ ហើយបន្ទាត់ប៉ះត្រង់ $I$ មានមេគុណប្រាប់ទិស ${t}$ ។"
    sol = lines("គេមាន $f'(x)=3x^2+2ax+b$ និង $f''(x)=6x+2a$ ។", f"$f''({p})=0$ ឲ្យ ${6*p}+2a=0$ នោះ $a={a}$ ។", f"$f'({p})={t}$ ឲ្យ ${3*p*p}+({2*p})({a})+b={t}$ នោះ $b={b}$ ។", f"$f({p})={q}$ ឲ្យ ${p**3}+({a})({p*p})+({b})({p})+c={q}$ នោះ $c={c}$ ។", "ដោយ $f''(x)$ ជាអនុគមន៍ដឺក្រេទីមួយ វាប្ដូរសញ្ញាត្រង់ឫសរបស់វា ។", f"ដូចនេះ $\\boxed{{a={a},\\ b={b},\\ c={c}}}$ ។")
    chs = [check(f"subs(diff({f},x,2),x,{p})", "0", "f''=0"), check(f"subs(diff({f},x),x,{p})", str(t), "slope"), check(f"subs({f},x,{p})", str(q), "ordinate")]
    ROWS.append(make_row("variation", "parameter_inflection", "hard", prob, sol, f"a={a},\\ b={b},\\ c={c}", chs, GEN))

def T_twostep():
    k = rng.randint(0, 3); c = rng.randint(-5, 5); nm = "f"
    if k == 0:
        f = x + c - ln(x)/x; g = x**2-1+ln(x); key = str(f); gtx = "x^2-1+\\ln x"
        if key in SEEN: return
        SEEN.add(key); val = 1+c
        prob = lines(f"ក. គេឲ្យ $g(x)={gtx}$ ចំពោះ $x>0$ ។ សិក្សាអថេរភាពនៃ $g$ គណនា $g(1)$ រួចទាញរកសញ្ញានៃ $g(x)$ ។", f"ខ. គេឲ្យ $f(x)={L(x+c)}-\\frac{{\\ln x}}{{x}}$ ចំពោះ $x>0$ ។ បង្ហាញថា $f'(x)=\\frac{{g(x)}}{{x^2}}$ រួចសង់តារាងអថេរភាពនៃ $f$ ។")
        tb = variation_table(["0", "1", "+\\infty"], ["\\|", "-", "0", "+", ""], ["+\\infty", "\\searrow", L(val), "\\nearrow", "+\\infty"])
        sol = lines("ក.", "$g'(x)=2x+\\frac{1}{x}>0$ ចំពោះគ្រប់ $x>0$ ដូចនេះ $g$ ជាអនុគមន៍កើនលើ $(0;+\\infty)$ ។", "ដោយ $g(1)=0$ នោះ $g(x)<0$ ពេល $0<x<1$ និង $g(x)>0$ ពេល $x>1$ ។", "ខ.", "តាមរូបមន្តផលចែក៖", "$$f'(x)=1-\\frac{\\frac{1}{x}\\cdot x-\\ln x}{x^2}=1-\\frac{1-\\ln x}{x^2}=\\frac{x^2-1+\\ln x}{x^2}=\\frac{g(x)}{x^2}$$",
                    "ដោយ $x^2>0$ នោះ $f'(x)$ មានសញ្ញាដូច $g(x)$ ។", f"លីមីត៖ $\\lim_{{x\\to 0^{{+}}}}f(x)=+\\infty$ និង $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។", f"$${tb}$$", f"ដូចនេះ $f$ ចុះលើ $(0;1)$ កើនលើ $(1;+\\infty)$ និងមានអប្បបរមា $\\boxed{{f(1)={L(val)}}}$ ។")
        chs = [check(f"diff({f},x)", f"({g})/x**2", "f'=g/x^2"), check(f"subs({g},x,1)", "0", "g(1)"), check(f"subs({f},x,1)", str(val), "min"), check(f"limit({f},x,0,'+')", "oo", "lim 0"), check(f"limit({f},x,oo)", "oo", "lim oo")]
    elif k == 1:
        kk = ch([1, 0, -1, -2]); f = x + c + (kk+ln(x))/x; g = x**2+1-kk-ln(x); key = str(f); gt = L(1-kk)
        if key in SEEN: return
        SEEN.add(key); mn = sp.expand(g.subs(x, 1/sq(2))); gq = "" if kk == 1 else "+" + gt
        prob = lines(f"ក. គេឲ្យ $g(x)=x^2{gq}-\\ln x$ ចំពោះ $x>0$ ។ រកអប្បបរមានៃ $g$ រួចបង្ហាញថា $g(x)>0$ ។", f"ខ. គេឲ្យ $f(x)={L(x+c)}+\\frac{{{L(kk+ln(x))}}}{{x}}$ ។ បង្ហាញថា $f$ ជាអនុគមន៍កើនលើ $(0;+\\infty)$ ។")
        sol = lines("ក.", "$g'(x)=2x-\\frac{1}{x}=\\frac{2x^2-1}{x}$ ។ លើ $(0;+\\infty)$ សមីការ $g'(x)=0$ ឲ្យ $x=\\frac{\\sqrt{2}}{2}$ ។", "$g$ ចុះលើ $\\left(0;\\frac{\\sqrt{2}}{2}\\right)$ និងកើនលើ $\\left(\\frac{\\sqrt{2}}{2};+\\infty\\right)$ ។", f"អប្បបរមាគឺ $g\\left(\\frac{{\\sqrt{{2}}}}{{2}}\\right)={L(mn)}>0$ ដូច្នេះ $g(x)>0$ ចំពោះគ្រប់ $x>0$ ។", "ខ.", f"$$f'(x)=1+\\frac{{1-({L(kk+ln(x))})}}{{x^2}}=\\frac{{g(x)}}{{x^2}}$$", "ដោយ $g(x)>0$ និង $x^2>0$ នោះ $f'(x)>0$ ។", "ដូចនេះ $f$ ជាអនុគមន៍កើនលើ $(0;+\\infty)$ ។")
        chs = [check(f"diff({f},x)", f"({g})/x**2", "f'=g/x^2"), check(f"subs({g},x,sqrt(2)/2)", str(mn), "min g"), check(f"subs({g},x,sqrt(2)/2)>0", "True", "positive")]
    elif k == 2:
        f = x - x*ex(-x) + c; g = ex(x)+x-1; key = str(f)
        if key in SEEN: return
        SEEN.add(key)
        prob = lines("ក. គេឲ្យ $g(x)=e^{x}+x-1$ ។ សិក្សាអថេរភាពនៃ $g$ រួចទាញរកសញ្ញានៃ $g(x)$ ។", f"ខ. គេឲ្យ $f(x)=x-xe^{{-x}}{c:+d}$ ។ បង្ហាញថា $f'(x)=e^{{-x}}g(x)$ រួចរកអប្បបរមានៃ $f$ ។".replace("+0", ""))
        sol = lines("ក.", "$g'(x)=e^{x}+1>0$ ដូចនេះ $g$ កើនលើ $IR$ ។ ដោយ $g(0)=0$ នោះ $g(x)<0$ ពេល $x<0$ និង $g(x)>0$ ពេល $x>0$ ។", "ខ.", "តាមរូបមន្តផលគុណ៖", "$$f'(x)=1-e^{-x}+xe^{-x}=e^{-x}(e^{x}-1+x)=e^{-x}g(x)$$", "ដោយ $e^{-x}>0$ នោះ $f'(x)$ មានសញ្ញាដូច $g(x)$ ។", f"$f$ ចុះលើ $(-\\infty;0)$ និងកើនលើ $(0;+\\infty)$ ។", f"ដូចនេះ អប្បបរមានៃ $f$ គឺ $\\boxed{{f(0)={c}}}$ ។")
        chs = [check(f"diff({f},x)", f"exp(-x)*({g})", "f'"), check(f"subs({g},x,0)", "0", "g(0)"), check(f"subs({f},x,0)", str(c), "min")]
    else:
        kk = ch([0, 1, 2, 3, -R(1, 2)]); f = x + (x+1-kk)*ex(-x) + c; g = ex(x)-x+kk; key = str(f)
        if key in SEEN: return
        SEEN.add(key); ktx = (f"{L(kk)}" if kk < 0 else f"+{L(kk)}") if kk != 0 else ""
        prob = lines(f"ក. គេឲ្យ $g(x)=e^{{x}}-x{ktx}$ ។ រកអប្បបរមានៃ $g$ រួចបង្ហាញថា $g(x)>0$ ។", f"ខ. គេឲ្យ $f(x)=x+({L(x+1-kk)})e^{{-x}}{c:+d}$ ។ បង្ហាញថា $f$ ជាអនុគមន៍កើនលើ $IR$ ។".replace("+0 ", " ").replace("+0$", "$"))
        sol = lines("ក.", "$g'(x)=e^{x}-1$ ។ $g'(x)=0$ ឲ្យ $x=0$ ។ $g$ ចុះលើ $(-\\infty;0)$ និងកើនលើ $(0;+\\infty)$ ។", f"អប្បបរមាគឺ $g(0)={L(1+kk)}>0$ ដូច្នេះ $g(x)>0$ ចំពោះគ្រប់ $x$ ។", "ខ.", "តាមរូបមន្តផលគុណ៖", f"$$f'(x)=1+e^{{-x}}-({L(x+1-kk)})e^{{-x}}=e^{{-x}}\\left(e^{{x}}-x{ktx}\\right)=e^{{-x}}g(x)$$", "ដោយ $e^{-x}>0$ និង $g(x)>0$ នោះ $f'(x)>0$ ។", "ដូចនេះ $f$ ជាអនុគមន៍កើនលើ $IR$ ។")
        chs = [check(f"diff({f},x)", f"exp(-x)*({g})", "f'"), check(f"subs({g},x,0)", str(1+kk), "min g")]
    ans = "f'(x)=\\frac{g(x)}{x^2}" if k < 2 else "f'(x)=e^{-x}g(x)"
    if k == 0: ans += f",\\ f(1)={L(val)}"
    if k == 2: ans += f",\\ f(0)={c}"
    if k == 1: ans += f",\\ g\\left(\\frac{{\\sqrt{{2}}}}{{2}}\\right)={L(mn)}"
    if k == 3: ans += f",\\ g(0)={L(1+kk)}"
    ROWS.append(make_row("variation", "two_step_auxiliary_function", "bacii", prob, sol, ans, chs, GEN))

# ---------- main ----------
def main():
    t0 = time.time()
    plan = [(T_mono, 270, None), (T_sign, 130, None), (T_table, 280, None), (T_ext, 170, None), (T_second, 70, {"cubic", "cubic_frac", "biq", "quartic"}), (T_closed, 50, {"cubic", "cubic_frac", "biq", "quartic"}),
            (T_sol, 170, None), (T_multi, 90, {"slant", "homog", "cubic", "expl", "expq", "lnlin", "xlnx", "lnoverx", "x2ln", "bump"}), (T_bound, 80, {"expl", "lnlin", "x2ln", "xlnx", "lnoverx", "ln2", "expminus", "exp2", "cosh", "lnquad", "xmln"})]
    for fn, n, allow in plan:
        s0 = len(ROWS)
        for _ in range(n):
            st = draw(allow)
            if st is None: print("exhausted", fn.__name__); break
            fn(st)
        print(fn.__name__, len(ROWS)-s0, round(time.time()-t0), flush=True)
    gen_infl(150); print("infl", len(ROWS), round(time.time()-t0), flush=True)
    gen_ineq(110); print("ineq", len(ROWS), round(time.time()-t0), flush=True)
    for _ in range(100): T_given()
    for _ in range(100): T_root()
    for _ in range(260): T_param()
    for _ in range(90): T_twostep()
    print("misc", len(ROWS), round(time.time()-t0), flush=True)
    try:
        from variation_hand import hand_rows
        ROWS.extend(hand_rows(make_row, check, variation_table, GEN))
    except ImportError:
        print("no hand rows")
    seen = set(); out = []
    for r in ROWS:
        if r["id"] in seen: continue
        seen.add(r["id"]); out.append(r)
    rng.shuffle(out)
    write_jsonl(out, "variation.jsonl"); print(round(time.time()-t0), "s; png", PNG)
if __name__ == "__main__":
    main()
