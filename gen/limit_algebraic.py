"""Topic limit_algebraic: limits of polynomial, rational and radical functions, Khmer BacII style.
All rows are original. Values come from exact SymPy arithmetic; lib/verify.py recomputes every limit."""
import sys, os, re, glob, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from limit_tex import clean_tex, finish_rows, tikz_poles
from sympy import Rational as Q, sqrt, expand, cancel, oo, Integer

TOPIC = "limit_algebraic"
rng = random.Random(20261105)
t_ = sp.Symbol("t", real=True)
ch = lambda *o: rng.choice(o)
def ni(lo, hi, ex=()):
    while True:
        v = rng.randint(lo, hi)
        if v != 0 and v not in ex:
            return v

def T(e):
    if isinstance(e, str):
        return e
    s = sp.latex(e, order="lex")
    s = s.replace("\\left(", "(").replace("\\right)", ")")
    s = s.replace(" + ", "+").replace(" - ", "-").replace("- ", "-")
    s = re.sub(r"(?<=[0-9})]) (?=[a-z(\\])", "", s)
    s = s.replace(") (", ")(")
    return s
def V(v):
    if v == oo: return r"+\infty"
    if v == -oo: return r"-\infty"
    return T(v)
def K(tpl, **kw):
    for k in sorted(kw, key=len, reverse=True):
        tpl = tpl.replace("@" + k, str(kw[k]))
    return tpl
def fr(n, d):
    return r"\frac{" + T(n) + "}{" + T(d) + "}"
def P(e):
    """Bracketed factor."""
    return "(" + T(e) + ")"
def pn(v):
    """Number, bracketed if negative."""
    return "(" + T(v) + ")" if v < 0 else T(v)
def lim(pt, var="x"):
    return r"\lim_{" + var + r"\to " + pt + "}"
def fac(*fs):
    """Product of factors without a stray (1)."""
    o = []
    for f in fs:
        if f == 1: continue
        o.append(T(f) if (sp.sympify(f).is_number and f > 0) else P(f))
    return "".join(o) if o else "1"
def subx(e, a):
    """Write e with x replaced by the number a, as a student does."""
    s = T(e); ta = T(a)
    br = "(" + ta + ")"
    s = re.sub(r"(?<=[0-9})])x", lambda m_: br, s)
    s = re.sub(r"x(?=\^)", lambda m_: br, s)
    s = re.sub(r"x", lambda m_: (br if a < 0 else ta), s)
    return s
def cs(e, a, side=None):
    return "limit(" + str(e) + ",x," + str(a) + (",'" + side + "'" if side else "") + ")"
def ck(e, a, v, side=None, note="limit"):
    return check(cs(e, a, side), str(v), note)

def chain(L, steps):
    """A chain of equalities in one of the layouts students use."""
    mode = rng.random()
    steps = [u for i, u in enumerate(steps) if i == 0 or u != steps[i - 1]]
    if mode < 0.55:
        o = ["$$" + L + "=" + steps[0] + "$$"]
        o += ["$$=" + s_ + "$$" for s_ in steps[1:]]
    elif mode < 0.8 and len(steps) <= 3:
        o = ["$$" + L + "=" + "=".join(steps) + "$$"]
    else:
        o = [r"$$\begin{aligned}" + L + "&=" + (r"\\&=").join(steps) + r"\end{aligned}$$"]
    return o

FORM = {"00": r"\frac{0}{0}", "ii": r"\frac{\infty}{\infty}", "mi": r"\infty-\infty", "zi": r"0\times\infty"}
def opener(pt, body, kind="00", name=None):
    """Names the indeterminate form in one of the guide's frames, or says nothing (science style)."""
    L = lim(pt) + body; F = FORM[kind]
    if kind == "00":
        c = ch(
            K(r"ជំនួស $x=@p$ យើងឃើញថាភាគយក និងភាគបែងស្មើ $0$ ទាំងពីរ ដូច្នេះលីមីតមានរាងមិនកំណត់ $@F$ ។", p=pt, F=F),
            K(r"កាលណា $x\to @p$ ភាគយក និងភាគបែងខិតជិត $0$ ។ យើងជួបរាងមិនកំណត់ $@F$ ។", p=pt, F=F),
            K(r"$$@L\quad\left(@F\right)$$ នេះជារាងមិនកំណត់ ។", L=L, F=F),
            K(r"លីមីតនេះមានរាងមិនកំណត់ $@F$ ព្រោះត្រង់ $x=@p$ ភាគយក និងភាគបែងសុទ្ធតែសូន្យ ។", p=pt, F=F),
            K(r"យើងមាន $@L$ (រាងមិនកំណត់ $@F$) ។", L=L, F=F),
            "", "")
    elif kind == "ii":
        c = ch(
            K(r"កាលណា $x\to @p$ ភាគយក និងភាគបែងខិតជិតអនន្ត ដូច្នេះមានរាងមិនកំណត់ $@F$ ។", p=pt, F=F),
            K(r"លីមីតនេះមានរាងមិនកំណត់ $@F$ ។", F=F),
            K(r"$$@L\quad\left(@F\right)$$ នេះជារាងមិនកំណត់ ។", L=L, F=F),
            K(r"យើងមាន $@L$ (មានរាងមិនកំណត់ $@F$) ។", L=L, F=F), "")
    else:
        c = ch(
            K(r"កាលណា $x\to @p$ កន្សោមមានរាងមិនកំណត់ $@F$ ។", p=pt, F=F),
            K(r"លីមីតនេះមានរាងមិនកំណត់ $@F$ ដូច្នេះមិនអាចជំនួសដោយផ្ទាល់បានទេ ។", F=F),
            K(r"$$@L\quad\left(@F\right)$$ នេះជារាងមិនកំណត់ ។", L=L, F=F), "")
    return [c] if c else []
def cancel_note(a, f):
    return ch(
        K(r"ដោយ $x\to @a$ យើងមាន $x\neq @a$ ដូច្នេះអាចសម្រួលកត្តា $@f$ បាន ។", a=T(a), f=f),
        K(r"សម្រួលកត្តា $@f$ ដែលខុសពីសូន្យកាលណា $x\neq @a$ ។", a=T(a), f=f),
        K(r"យើងសម្រួលភាគយក និងភាគបែងនឹង $@f$ ។", f=f),
        "", "", "")
def conj_word(e):
    return ch(
        K(r"គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ $@e$ ។", e=e),
        K(r"យើងគុណទាំងភាគយកទាំងភាគបែងនឹង $@e$ ដែលជាកន្សោមឆ្លាស់ ។", e=e),
        K(r"ដើម្បីបំបាត់រាងមិនកំណត់ គុណនឹងកន្សោមឆ្លាស់ $@e$ ទាំងភាគយក និងភាគបែង ។", e=e),
        K(r"ប្រើកន្សោមឆ្លាស់ $@e$ ហើយរូបមន្ត $(a-b)(a+b)=a^{2}-b^{2}$ ។", e=e),
        "")
def concl(L, vt):
    return ch(*([r"ដូចនេះ $\boxed{" + L + "=" + vt + r"}$ ។"] * 5 +
                ["ដូចនេះ $" + L + r"=\boxed{" + vt + r"}$ ។"] * 3 +
                [r"ដូចនេះ លីមីតដែលត្រូវរកគឺ $\boxed{" + vt + r"}$ ។",
                 r"ដូចនេះ លីមីតនេះស្មើនឹង $\boxed{" + vt + r"}$ ។",
                 "ដូចនេះ $" + L + "=" + vt + "$ ។"]))

class Atom:
    def __init__(s, body, pt, lines, val, checks, sub, diff="medium", grade=12, q=None, ans=None,
                 diag=None, plain=False, png=None, part=None):
        s.body, s.pt, s.lines, s.val, s.checks = body, pt, [l for l in lines if l], val, checks
        s.sub, s.diff, s.grade, s.q, s.diag, s.plain, s.png = sub, diff, grade, q, diag or [], plain, png
        s.vt = V(val) if val is not None else None
        s.ans = ans or (lim(pt) + body + "=" + s.vt if body else s.vt)
        s.part = part
    @property
    def L(s):
        return lim(s.pt) + s.body
    def sol(s):
        o = list(s.lines)
        if not s.plain:
            o.append(concl(s.L, s.vt))
        return o

# ---------- Grade 11: direct substitution and limit rules ----------
def a_direct_poly():
    a = ni(-4, 5); d = ch(2, 3, 3, 4)
    Pp = sum(ni(-5, 6) * x**k for k in range(1, d)) + ch(1, 1, 2, -1, 3) * x**d + rng.randint(-7, 9)
    v = Pp.subs(x, a); b = T(Pp); L = lim(T(a)) + "(" + b + ")"
    w = ch(r"អនុគមន៍នេះជាពហុធា ដូច្នេះលីមីតត្រង់ $x=@a$ រកបានដោយជំនួស $x=@a$ ផ្ទាល់ ។",
           r"ពហុធាកំណត់គ្រប់ចំនួនពិត ដូច្នេះយើងជំនួស $x=@a$ ។", r"យើងជំនួស $x$ ដោយ $@a$ ក្នុងពហុធា ។", "")
    return Atom("(" + b + ")", T(a), [K(w, a=T(a))] + chain(L, [subx(Pp, a), T(v)]), v, [ck(Pp, a, v)],
                "direct_polynomial", "easy", 11)
def a_direct_rat():
    while True:
        a = ni(-4, 5); n = ni(-3, 4) * x**2 + ni(-5, 5) * x + rng.randint(-5, 6); d = x**2 + ni(-4, 4) * x + rng.randint(-3, 5)
        if ch(0, 1): d = ni(1, 3) * x + ni(-5, 5)
        if d.subs(x, a) != 0 and n.subs(x, a) != 0: break
    v = Q(n.subs(x, a)) / d.subs(x, a); body = fr(n, d)
    w = ch(K(r"ត្រង់ $x=@a$ ភាគបែងស្មើ $@d$ ខុសពីសូន្យ ដូច្នេះអាចជំនួសដោយផ្ទាល់ ។", a=T(a), d=T(d.subs(x, a))),
           K(r"ភាគបែងមិនស្មើសូន្យត្រង់ $x=@a$ ទេ ។ តាមប្រមាណវិធីលើលីមីត លីមីតនៃផលចែកស្មើផលចែកនៃលីមីត ។", a=T(a)), "")
    return Atom(body, T(a), [w] + chain(lim(T(a)) + body, [fr(subx(n, a), subx(d, a)), T(v)]), v, [ck(n / d, a, v)],
                "direct_rational", "easy", 11)
def a_direct_rad():
    while True:
        a = ni(-3, 8); r0 = rng.randint(2, 7); p = ni(1, 4); q = r0**2 - p * a
        e = ni(-5, 6); k = ni(1, 3); c = ni(-6, 6)
        if k * a + c != 0: break
    S = sqrt(p * x + q); v = Q(r0 + e, k * a + c); body = fr(T(S) + ("+" if e > 0 else "") + T(e), k * x + c)
    w = ch(K(r"ត្រង់ $x=@a$ កន្សោមក្រោមឫសវិជ្ជមាន ហើយភាគបែងខុសពីសូន្យ ។ យើងជំនួសផ្ទាល់ ។", a=T(a)),
           K(r"អនុគមន៍កំណត់ត្រង់ $x=@a$ ដូច្នេះលីមីតស្មើតម្លៃនៃអនុគមន៍ត្រង់នោះ ។", a=T(a)), "")
    st = fr(r"\sqrt{" + T(p * a + q) + "}" + ("+" if e > 0 else "") + T(e), subx(k * x + c, a))
    return Atom(body, T(a), [w] + chain(lim(T(a)) + body, [st, T(v)]), v, [ck((S + e) / (k * x + c), a, v)],
                "direct_radical", "easy", 11)
def a_rules_explicit():
    a = ni(-3, 4); u = x**2 + ni(-4, 4) * x + ni(-3, 3); w_ = ni(1, 3) * x + ni(-5, 5)
    ua, wa = u.subs(x, a), w_.subs(x, a)
    if ua == 0 or wa == 0: return a_rules_explicit()
    mode = ch("prod", "quo", "sum")
    if mode == "prod":
        body = r"\left[" + P(u) + P(w_) + r"\right]"; e = u * w_; v = ua * wa
        st = [lim(T(a)) + P(u) + r"\times" + lim(T(a)) + P(w_), pn(ua) + r"\times" + pn(wa), T(v)]
        rule = "តាមប្រមាណវិធីលើលីមីត លីមីតនៃផលគុណស្មើផលគុណនៃលីមីត ។"
    elif mode == "quo":
        body = fr(u, w_); e = u / w_; v = Q(ua) / wa
        st = [r"\frac{" + lim(T(a)) + P(u) + "}{" + lim(T(a)) + P(w_) + "}", fr(ua, wa), T(v)]
        rule = K(r"ដោយ $@L\neq0$ លីមីតនៃផលចែកស្មើផលចែកនៃលីមីត ។", L=lim(T(a)) + P(w_))
    else:
        k = ni(2, 5); body = r"\left[" + (P(u) + "+" + T(k) + P(w_) if k > 0 else P(u) + T(k) + P(w_)) + r"\right]"; e = u + k * w_; v = ua + k * wa
        st = [lim(T(a)) + P(u) + ("+" if k > 0 else "") + T(k) + lim(T(a)) + P(w_), pn(ua) + ("+" if k > 0 else "") + T(k) + r"\times" + pn(wa), T(v)]
        rule = "លីមីតនៃផលបូកស្មើផលបូកនៃលីមីត ហើយមេគុណថេរអាចយកចេញក្រៅលីមីតបាន ។"
    return Atom(body, T(a), [rule] + chain(lim(T(a)) + body, st), v, [ck(e, a, v)], "limit_rules", "easy", 11)
def a_rules_given():
    a = ni(-3, 5); A_ = ni(-5, 7); B = ni(-5, 7, (A_,)); m_ = ni(2, 4); n_ = ni(2, 4)
    F = A_ + (x - a); G = B + 2 * (x - a)
    mode = ch("lin", "prod", "quo", "sq", "frac2", "root")
    if mode == "root":
        A_ = ch(4, 9, 16, 25, 36); F = A_ + (x - a)
        B = ni(-5, 7, (A_,)); G = B + 2 * (x - a)
    pt = T(a)
    if mode == "lin":
        ex = T(m_) + "f(x)-" + T(n_) + "g(x)"; v = m_ * A_ - n_ * B; e = m_ * F - n_ * G
        st = [T(m_) + lim(pt) + "f(x)-" + T(n_) + lim(pt) + "g(x)", T(m_) + r"\times" + pn(A_) + "-" + T(n_) + r"\times" + pn(B), T(v)]
    elif mode == "prod":
        ex = "f(x)g(x)"; v = A_ * B; e = F * G
        st = [lim(pt) + "f(x)" + r"\times" + lim(pt) + "g(x)", pn(A_) + r"\times" + pn(B), T(v)]
    elif mode == "quo":
        ex = r"\frac{f(x)}{g(x)}"; v = Q(A_, B); e = F / G
        st = [r"\frac{" + lim(pt) + "f(x)}{" + lim(pt) + "g(x)}", fr(A_, B), T(v)]
    elif mode == "sq":
        ex = r"\left[f(x)\right]^{2}+" + T(m_) + "g(x)"; v = A_**2 + m_ * B; e = F**2 + m_ * G
        st = [r"\left[" + lim(pt) + r"f(x)\right]^{2}+" + T(m_) + lim(pt) + "g(x)", pn(A_) + "^{2}+" + T(m_) + r"\times" + pn(B), T(v)]
    elif mode == "frac2":
        if A_ == -B: return a_rules_given()
        ex = r"\frac{f(x)-g(x)}{f(x)+g(x)}"; v = Q(A_ - B, A_ + B); e = (F - G) / (F + G)
        st = [r"\frac{" + lim(pt) + "f(x)-" + lim(pt) + "g(x)}{" + lim(pt) + "f(x)+" + lim(pt) + "g(x)}", fr(T(A_) + "-" + pn(B), T(A_) + "+" + pn(B)), T(v)]
    else:
        ex = r"\sqrt{f(x)}+g(x)"; v = sqrt(A_) + B; e = sqrt(F) + G
        st = [r"\sqrt{" + lim(pt) + "f(x)}+" + lim(pt) + "g(x)", r"\sqrt{" + T(A_) + "}+" + pn(B), T(v)]
    q = K(ch(r"គេដឹងថា $@Lf(x)=@A$ និង $@Lg(x)=@B$ ។ គណនា $@L\left[@E\right]$ ។",
             r"គេឱ្យអនុគមន៍ $f$ និង $g$ ដែល $@Lf(x)=@A$ ហើយ $@Lg(x)=@B$ ។ រកតម្លៃនៃ $@L\left[@E\right]$ ។",
             r"បើ $@Lf(x)=@A$ និង $@Lg(x)=@B$ នោះចូរគណនា $@L\left[@E\right]$ ។"), L=lim(pt), A=T(A_), B=T(B), E=ex)
    L = lim(pt) + r"\left[" + ex + r"\right]"
    return Atom(r"\left[" + ex + r"\right]", pt, [ch("តាមប្រមាណវិធីលើលីមីត យើងបាន ៖", "ដោយលីមីតទាំងពីរមានតម្លៃកំណត់ យើងអនុវត្តប្រមាណវិធីលើលីមីត ៖", "យើងបាន ៖")] + chain(L, st),
                v, [check(cs(e, a), str(v), "instance with f=A+(x-a), g=B+2(x-a)")], "limit_rules_given", "easy", 11, q=q)
def a_recip_inf():
    c1 = ni(-6, 7); c2 = ni(-6, 7); n1 = ch(1, 2, 3); n2 = n1 + ch(1, 2); c3 = ni(2, 6); sgn = ch(oo, -oo); pt = V(sgn)
    mode = ch(0, 1)
    if mode == 0:
        e = c1 + c2 / x**n1 + c3 / x**n2
        body = "\\left(" + T(c1) + ("+" if c2 > 0 else "") + fr(c2, x**n1) + "+" + fr(c3, x**n2) + "\\right)"
        v = c1
        l = [K(r"យើងដឹងថា $@L\frac{1}{x^{n}}=0$ ចំពោះ $n$ ជាចំនួនគត់វិជ្ជមាន ។ ដូច្នេះតួដែលមាន $x$ នៅភាគបែងខិតជិត $0$ ។", L=lim(pt))]
        l += chain(lim(pt) + body, [T(c1) + "+0+0", T(v)])
    else:
        c4 = ni(1, 5); e = (c1 + c3 / x**n1) * (c4 - c2 / x**n2); v = c1 * c4
        body = "\\left(" + T(c1) + "+" + fr(c3, x**n1) + "\\right)\\left(" + T(c4) + ("-" if c2 > 0 else "+") + fr(abs(c2), x**n2) + "\\right)"
        l = ["លីមីតនៃកត្តានីមួយៗមានតម្លៃកំណត់ ដូច្នេះលីមីតនៃផលគុណស្មើផលគុណនៃលីមីត ៖"]
        l += chain(lim(pt) + body, [pn(c1) + r"\times" + T(c4), T(v)])
    return Atom(body, pt, l, v, [ck(e, sgn, v)], "limit_rules_reciprocal", "easy", 11)

# ---------- Factoring ----------
def alt_t(N, D, a, v):
    n2 = expand(N.subs(x, t_ + a)); d2 = expand(D.subs(x, t_ + a))
    n3 = cancel(n2 / t_); d3 = cancel(d2 / t_)
    return [K(r"របៀបមួយទៀត ៖ តាង $t=@t$ $\Rightarrow$ $x=@x$ ។ បើ $x\to @a$ នោះ $t\to 0$ ។", t=T(x - a), x=T(t_ + a), a=T(a)),
            "$$" + lim("0", "t") + fr(n2, d2) + "=" + lim("0", "t") + fr(fac(t_) .replace("(t)", "t") + P(n3), "t" + P(d3)) + "=" + lim("0", "t") + fr(n3, d3) + "=" + T(v) + "$$"]
def a_fact_qq():
    while True:
        a = ni(-6, 6); p = ch(1, 1, 1, 2, 3); q = ch(1, 1, 1, 2, 3, -1); b = ni(-7, 7); c = ni(-7, 7)
        n1 = p * x + b; d1 = q * x + c
        if d1.subs(x, a) != 0 and n1.subs(x, a) != 0 and p * c != q * b: break
    N = expand((x - a) * n1); D = expand((x - a) * d1); v = Q(n1.subs(x, a)) / d1.subs(x, a); pt = T(a); body = fr(N, D)
    l = opener(pt, body)
    f = P(x - a)
    if rng.random() < .5:
        l.append(ch(K(r"ដាក់ជាកត្តា ៖ $@N=@FN$ និង $@D=@FD$ ។", N=T(N), D=T(D), FN=f + P(n1), FD=f + P(d1)),
                    K(r"ដោយ $x=@a$ ជាឫសនៃភាគយក និងភាគបែង ពហុធាទាំងពីរមានកត្តា $@f$ ។", a=pt, f=T(x - a))))
    l += chain(lim(pt) + body, [lim(pt) + fr(f + P(n1), f + P(d1)), lim(pt) + fr(n1, d1), fr(subx(n1, a), subx(d1, a)), T(v)])
    if rng.random() < .18:
        l += alt_t(N, D, a, v)
    return Atom(body, pt, l, v, [ck(N / D, a, v)], "factor_quadratic", ch("easy", "medium"))
def a_diff_squares():
    a = ni(1, 9); k = ch(1, 1, 2, 3, 4)
    b = ni(-6, 6, (a, -a))
    if ch(0, 1):
        N = x**2 - a**2; D = (x - a) * (x + b) if ch(0, 1) else k * (x - a); den = (x + b) if D != k * (x - a) else k
        if den != k and den.subs(x, a) == 0: return a_diff_squares()
        v = Q(2 * a) / (den.subs(x, a) if den != k else k)
        D = expand(D); pt = T(a); body = fr(N, D)
        l = opener(pt, body) + chain(lim(pt) + body, [lim(pt) + fr(P(x - a) + P(x + a), P(x - a) + (P(den) if den != k else T(k)).replace("(" + T(k) + ")", T(k))), lim(pt) + fr(x + a, den), T(v)])
        return Atom(body, pt, l, v, [ck(N / D, a, v)], "factor_difference_of_squares", "easy")
    N = k * (x + a); D = x**2 - a**2; pt = T(-a); v = Q(k) / (-2 * a); body = fr(N, D)
    l = opener(pt, body) + chain(lim(pt) + body, [lim(pt) + fr(fac(k, x + a), P(x - a) + P(x + a)), lim(pt) + fr(k, x - a), fr(k, T(-a) + "-" + T(a)), T(v)])
    return Atom(body, pt, l, v, [ck(N / D, -a, v)], "factor_difference_of_squares", "easy")
def a_fact_cubic():
    while True:
        a = ni(-4, 5); b = ni(-4, 4); c = ni(-5, 6); d0 = ni(-5, 5); m0 = ch(1, 1, 2)
        n1 = x**2 + b * x + c; d1 = m0 * x + d0
        if ch(0, 1): d1 = x**2 + ni(-3, 3) * x + ni(-4, 4)
        if n1.subs(x, a) != 0 and d1.subs(x, a) != 0: break
    N = expand((x - a) * n1); D = expand((x - a) * d1); v = Q(n1.subs(x, a)) / d1.subs(x, a); pt = T(a); body = fr(N, D); f = P(x - a)
    l = opener(pt, body)
    l.append(ch(K(r"ដោយ $x=@a$ ជាឫសនៃ $@N$ យើងចែកពហុធានេះនឹង $@f$ ហើយបាន $@N=(@f)(@q)$ ។", a=pt, N=T(N), f=T(x - a), q=T(n1)),
                K(r"ភាគយកចែកដាច់នឹង $@f$ ៖ $@N=(@f)(@q)$ ។", N=T(N), f=T(x - a), q=T(n1)),
                K(r"យើងដាក់ភាគយកជាកត្តា ៖ $@N=(@f)(@q)$ ។ ភាគបែងក៏មានកត្តា $@f$ ដែរ ។", N=T(N), f=T(x - a), q=T(n1))))
    l += chain(lim(pt) + body, [lim(pt) + fr(f + P(n1), f + P(d1)), lim(pt) + fr(n1, d1), fr(subx(n1, a), subx(d1, a)), T(v)])
    return Atom(body, pt, l, v, [ck(N / D, a, v)], "factor_cubic", "medium")
def a_cubes():
    a = ni(1, 5); s_ = ch(1, -1); k = ch(1, 2, 3)
    if s_ == 1:
        N = x**3 - a**3; n1 = x**2 + a * x + a**2; f = x - a; pt0 = a; idn = "a^{3}-b^{3}=(a-b)(a^{2}+ab+b^{2})"
    else:
        N = x**3 + a**3; n1 = x**2 - a * x + a**2; f = x + a; pt0 = -a; idn = "a^{3}+b^{3}=(a+b)(a^{2}-ab+b^{2})"
    mode = ch(0, 1)
    if mode == 0:
        D = expand(k * f); d1 = Integer(k)
    else:
        D = x**2 - a**2; d1 = (x + a) if s_ == 1 else (x - a)
    v = Q(n1.subs(x, pt0)) / (d1.subs(x, pt0) if d1 != k else k); pt = T(pt0); body = fr(N, D)
    l = opener(pt, body) + [K(r"តាមរូបមន្ត $@i$ យើងបាន $@N=@F$ ។", i=idn, N=T(N), F=P(f) + P(n1))]
    l += chain(lim(pt) + body, [lim(pt) + fr(P(f) + P(n1), (P(f) + (P(d1) if mode else "")) if mode or k == 1 else T(k) + P(f)), lim(pt) + fr(n1, d1), fr(subx(n1, pt0), subx(d1, pt0) if mode else k), T(v)])
    return Atom(body, pt, l, v, [ck(N / D, pt0, v)], "factor_sum_difference_cubes", "medium")
def a_power_diff():
    n_ = ch(3, 4, 5, 6, 7); m_ = ch(2, 3, 4, 5); a = ch(1, 1, 1, 2)
    if n_ == m_: return a_power_diff()
    pt = T(a); N = x**n_ - a**n_; D = x**m_ - a**m_; body = fr(N, D); v = Q(n_ * a**(n_ - 1), m_ * a**(m_ - 1))
    sn = sum(a**(n_ - 1 - i) * x**i for i in range(n_)); sd = sum(a**(m_ - 1 - i) * x**i for i in range(m_))
    l = opener(pt, body) + [ch(r"ប្រើរូបមន្ត $x^{n}-a^{n}=(x-a)(x^{n-1}+ax^{n-2}+\cdots+a^{n-1})$ ។", r"យើងដាក់ភាគយក និងភាគបែងជាកត្តាតាមរូបមន្តផលដកស្វ័យគុណ $x^{n}-a^{n}$ ។")]
    f = P(x - a)
    l += chain(lim(pt) + body, [lim(pt) + fr(f + P(sn), f + P(sd)), lim(pt) + fr(sn, sd), fr(sn.subs(x, a), sd.subs(x, a)), T(v)] if v != Q(sn.subs(x, a), sd.subs(x, a)) or True else [])
    return Atom(body, pt, l, v, [ck(N / D, a, v)], "factor_power_difference", "hard")
def a_biquad():
    a = ch(1, 2, 3); b = ni(1, 4, (a,)); c = ch(1, 2, 3, 4)
    N = expand((x**2 - a**2) * (x**2 + b)); D = expand((x - a) * (x + c)) if ch(0, 1) else x**2 - a**2 + 0
    D = expand((x - a) * (x + c)); v = (2 * a * (a**2 + b)) / Q(a + c); pt = T(a); body = fr(N, D)
    l = opener(pt, body) + [K(r"តាង $X=x^{2}$ ភាគយកក្លាយជា $@Y$ ដែលមានឫស $X=@s$ ។ ដូច្នេះ $@N=@F$ ។", Y=T(expand((t_ - a**2) * (t_ + b))).replace("t", "X"), s=T(a**2), N=T(N), F=P(x**2 - a**2) + P(x**2 + b))]
    f = P(x - a)
    l += chain(lim(pt) + body, [lim(pt) + fr(f + P(x + a) + P(x**2 + b), f + P(x + c)), lim(pt) + fr(P(x + a) + P(x**2 + b), x + c), fr(P(2 * a) + P(a**2 + b), a + c), T(v)])
    return Atom(body, pt, l, v, [ck(N / D, a, v)], "factor_biquadratic", "hard")
def a_double_root():
    a = ni(-4, 4); b = ni(-5, 6, (a,)); c = ni(-5, 6, (a,)); pt = T(a)
    n1 = x + b; d1 = x + c
    if n1.subs(x, a) == 0 or d1.subs(x, a) == 0: return a_double_root()
    N = expand((x - a)**2 * n1); D = expand((x - a)**2 * d1); v = Q(n1.subs(x, a)) / d1.subs(x, a); body = fr(N, D)
    f = P(x - a) + "^{2}"
    l = opener(pt, body) + [K(r"$x=@a$ ជាឫសឌុបនៃភាគយក និងភាគបែង ដូច្នេះកត្តារួមគឺ $@f$ ។", a=pt, f=f)]
    l += chain(lim(pt) + body, [lim(pt) + fr(f + P(n1), f + P(d1)), lim(pt) + fr(n1, d1), T(v)])
    return Atom(body, pt, l, v, [ck(N / D, a, v)], "factor_double_root", "hard")
def a_inner_frac():
    mode = ch(0, 1, 2)
    if mode == 0:
        a = ni(2, 8); pt = T(a); body = fr(r"\frac{1}{x}-\frac{1}{" + T(a) + "}", x - a); e = (1 / x - Q(1, a)) / (x - a); v = -Q(1, a**2)
        st = [lim(pt) + fr(fr(T(a) + "-x", T(a) + "x"), x - a), lim(pt) + fr("-(x-" + pt + ")", T(a) + "x(x-" + pt + ")"), lim(pt) + fr(-1, T(a) + "x"), T(v)]
    elif mode == 1:
        p = ni(1, 6); q = ni(2, 7); c = q - p; pt = T(c)
        body = fr(fr(1, x + p) + "-" + fr(1, q), x - c); e = (1 / (x + p) - Q(1, q)) / (x - c); v = -Q(1, q**2)
        st = [lim(pt) + fr(fr(T(q) + "-" + P(x + p), T(q) + P(x + p)), x - c), lim(pt) + fr(fr(T(c - x), T(q) + P(x + p)), x - c), lim(pt) + fr(-1, T(q) + P(x + p)), T(v)]
    else:
        a = ni(2, 6); pt = T(a); body = fr(fr(1, x**2) + "-" + fr(1, a**2), x - a); e = (1 / x**2 - Q(1, a**2)) / (x - a); v = -Q(2, a**3)
        st = [lim(pt) + fr(fr(T(a**2) + "-x^{2}", T(a**2) + "x^{2}"), x - a), lim(pt) + fr("-(x-" + pt + ")(x+" + pt + ")", T(a**2) + "x^{2}(x-" + pt + ")"), lim(pt) + fr("-(x+" + pt + ")", T(a**2) + "x^{2}"), T(v)]
    l = opener(pt, body) + [ch("យើងដាក់ប្រភាគក្នុងភាគយកឱ្យមានភាគបែងរួមសិន ។", "ដំបូងបូកប្រភាគក្នុងភាគយកដោយយកភាគបែងរួម ។", "ធ្វើផលដកប្រភាគនៅភាគយកជាមុនសិន ។")] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, a if mode != 1 else c, v)], "factor_nested_fraction", "medium")
def a_binom_h():
    a = ni(1, 5); n_ = ch(2, 3, 3); s_ = ch(1, -1); A_ = s_ * a
    N = (x + A_)**n_ - A_**n_; ex = expand(N); pt = "0"; v = n_ * A_**(n_ - 1)
    body = fr(P(x + A_) + "^{" + str(n_) + "}" + ("-" if A_**n_ > 0 else "+") + T(abs(A_**n_)), x)
    q = cancel(ex / x)
    l = opener(pt, body) + [ch("ពន្លាតភាគយកសិន ។", "ភាគយកអាចពន្លាតតាមរូបមន្តទ្វេធា ។", "យើងពន្លាតស្វ័យគុណ រួចដាក់ $x$ ជាកត្តារួម ។")]
    l += chain(lim(pt) + body, [lim(pt) + fr(ex, x), lim(pt) + fr("x" + P(q), "x"), lim(pt) + P(q), T(v)])
    return Atom(body, pt, l, v, [ck(N / x, 0, v)], "factor_expand_first", "easy")
def a_rate():
    a = ni(-3, 4); c2 = ni(-3, 4); c1 = ni(-5, 5); d = ch(2, 3); f = (x**3 if d == 3 else 0) + c2 * x**2 + c1 * x
    if f.subs(x, a) == 0 and False: pass
    fa = f.subs(x, a); pt = T(a); N = f - fa; q = cancel(N / (x - a)); v = q.subs(x, a); F = T(f)
    b = "\\frac{f(x)-f(" + pt + ")}{x" + ("-" + pt if a > 0 else "+" + T(-a)) + "}"
    qq = K(ch(r"គេឱ្យអនុគមន៍ $f(x)=@F$ ។ គណនាលីមីត $@L@b$ ។", r"ចំពោះអនុគមន៍ $f(x)=@F$ រកលីមីត $@L@b$ ។"), F=F, L=lim(pt), b=b)
    l = [K(r"យើងមាន $f(@a)=@fa$ ។ ដូច្នេះ $f(x)-f(@a)=@N$ ។", a=pt, fa=T(fa), N=T(N))]
    l.append(K(r"ភាគយកមានឫស $x=@a$ ដូច្នេះ $@N=(@f)(@q)$ ។", a=pt, N=T(N), f=T(x - a), q=T(q)))
    l += chain(lim(pt) + b, [lim(pt) + fr(P(x - a) + P(q), x - a), lim(pt) + P(q), T(v)])
    return Atom(b, pt, l, v, [ck(N / (x - a), a, v)], "factor_rate_of_change", "medium", q=qq)
def a_frac_minus():
    mode = ch(0, 1, 2, 3)
    if mode == 0:
        a = ni(1, 6); pt = T(a); k = 2 * a; body = r"\left(" + fr(1, x - a) + "-" + fr(k, x**2 - a**2) + r"\right)"; e = 1 / (x - a) - k / (x**2 - a**2); v = Q(1, 2 * a); p0 = a
        st = [lim(pt) + fr(P(x + a) if False else T(x + a) + "-" + T(k), P(x - a) + P(x + a)), lim(pt) + fr(x - a, P(x - a) + P(x + a)), lim(pt) + fr(1, x + a), T(v)]
    elif mode == 1:
        pt = "1"; p0 = 1; body = r"\left(" + fr(1, x - 1) + "-" + fr(3, x**3 - 1) + r"\right)"; e = 1 / (x - 1) - 3 / (x**3 - 1); v = Integer(1)
        k = ch(1, 2)
        if k == 2:
            body = r"\left(" + fr(2, x - 1) + "-" + fr(6, x**3 - 1) + r"\right)"; e = 2 * e; v = Integer(2)
            st = [lim(pt) + fr("2(x^{2}+x+1)-6", P(x - 1) + "(x^{2}+x+1)"), lim(pt) + fr("2(x-1)(x+2)", P(x - 1) + "(x^{2}+x+1)"), lim(pt) + fr("2(x+2)", "x^{2}+x+1"), "2"]
        else:
            st = [lim(pt) + fr("x^{2}+x+1-3", P(x - 1) + "(x^{2}+x+1)"), lim(pt) + fr("(x-1)(x+2)", P(x - 1) + "(x^{2}+x+1)"), lim(pt) + fr("x+2", "x^{2}+x+1"), "1"]
    elif mode == 2:
        a = ni(1, 5); b = ni(1, 6, (a,)); pt = T(a); p0 = a; D = (x - a) * (x + b); k = a + b
        body = r"\left(" + fr(1, x - a) + "-" + fr(k, expand(D)) + r"\right)"; e = 1 / (x - a) - k / D; v = Q(1, a + b)
        st = [lim(pt) + fr(T(x + b) + "-" + T(k), P(x - a) + P(x + b)), lim(pt) + fr(x - a, P(x - a) + P(x + b)), lim(pt) + fr(1, x + b), T(v)]
    else:
        a = ni(1, 5); pt = "0"; p0 = 0; body = r"\frac{1}{x}\left(" + fr(1, x + a) + "-" + fr(1, a) + r"\right)"; e = (1 / (x + a) - Q(1, a)) / x; v = -Q(1, a**2)
        st = [lim(pt) + r"\frac{1}{x}\cdot" + fr(T(a) + "-" + P(x + a), T(a) + P(x + a)), lim(pt) + r"\frac{1}{x}\cdot" + fr("-x", T(a) + P(x + a)), lim(pt) + fr(-1, T(a) + P(x + a)), T(v)]
    kind = "mi" if mode != 3 else "zi"
    l = opener(pt, body, kind) + [ch("យើងបញ្ចូលប្រភាគទាំងពីរក្រោមភាគបែងរួម ។", "ដាក់ប្រភាគឱ្យមានភាគបែងរួម ។", "តួនីមួយៗខិតជិតអនន្ត ដូច្នេះត្រូវបញ្ចូលជាប្រភាគតែមួយសិន ។" if mode != 3 else "បញ្ចូលប្រភាគក្នុងវង់ក្រចកជាប្រភាគតែមួយសិន ។")] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, p0, v)], "infinity_minus_infinity_rational", "hard" if mode == 1 else "medium")

# ---------- Conjugates ----------
def sq(p, q):
    return sqrt(p * x + q)
def a_conj_num():
    while True:
        c = ni(-5, 8); r0 = rng.randint(1, 6); p = ch(1, 1, 2, 3, 4, -1); q = r0**2 - p * c; kind = ch("lin", "lin", "k", "quad"); e0 = ni(-5, 6)
        d1 = {"lin": Integer(1), "k": Integer(ch(2, 3, 4)), "quad": x + e0}[kind]
        if d1.subs(x, c) != 0: break
    S = sq(p, q); s_ = T(S); num = s_ + "-" + T(r0); D = expand((x - c) * d1); pt = T(c); body = fr(num, D); e = (S - r0) / D
    v = Q(p) / (2 * r0 * d1.subs(x, c)); plus = s_ + "+" + T(r0); df = (P(x - c) + (P(d1) if kind == "quad" else "")) if kind != "k" else T(d1) + P(x - c)
    l = opener(pt, body) + [conj_word(plus)]
    d1t = {"lin": "", "k": T(d1), "quad": P(d1)}[kind]
    st = [lim(pt) + fr("(" + num + ")(" + plus + ")", df + "(" + plus + ")"),
          lim(pt) + fr(T(p * x + q) + ("-" + T(r0**2)), df + "(" + plus + ")"),
          lim(pt) + fr(T(p) + P(x - c) if p != 1 else P(x - c), df + "(" + plus + ")") if p != -1 else lim(pt) + fr("-" + P(x - c), df + "(" + plus + ")"),
          lim(pt) + fr(p, (d1t + "(" + plus + ")")),
          fr(p, (T(d1.subs(x, c)) if kind != "lin" else "") + (r"\times" if kind != "lin" else "") + "(" + T(r0) + "+" + T(r0) + ")"), T(v)]
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, c, v)], "conjugate_numerator", "medium")
def a_conj_den():
    while True:
        c = ni(-4, 8); r0 = rng.randint(1, 6); p = ch(1, 1, 2, 3); q = r0**2 - p * c; n1 = ch(Integer(1), Integer(ch(2, 3)), x + ni(-5, 6), 2 * x + ni(-5, 5))
        if n1.subs(x, c) != 0: break
    S = sq(p, q); s_ = T(S); den = s_ + "-" + T(r0); N = expand((x - c) * n1); pt = T(c); body = fr(N, den); e = N / (S - r0)
    plus = s_ + "+" + T(r0); v = Q(n1.subs(x, c) * 2 * r0, p)
    nf = (P(x - c) + P(n1)) if not n1.is_number else (T(n1) + P(x - c) if n1 != 1 else P(x - c))
    n1t = P(n1) if not n1.is_number else (T(n1) if n1 != 1 else "")
    l = opener(pt, body) + [ch(K(r"ភាគបែងមានឫសការេ ដូច្នេះគុណនឹងកន្សោមឆ្លាស់ $@e$ ។", e=plus), conj_word(plus))]
    st = [lim(pt) + fr(nf + "(" + plus + ")", "(" + den + ")(" + plus + ")"),
          lim(pt) + fr(nf + "(" + plus + ")", T(p * x + q) + "-" + T(r0**2)),
          lim(pt) + fr(nf + "(" + plus + ")", (T(p) if p != 1 else "") + P(x - c)),
          lim(pt) + (fr(n1t + "(" + plus + ")", p) if p != 1 else n1t + "(" + plus + ")"), T(v)]
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, c, v)], "conjugate_denominator", "medium")
def a_conj_both():
    while True:
        c = ni(-3, 8); r0 = rng.randint(1, 5); u = rng.randint(1, 5); p = ch(1, 1, 2, 3); s_ = ch(1, 1, 2, 3); q = r0**2 - p * c; t0 = u**2 - s_ * c
        if (p, r0) != (s_, u): break
    A_ = sq(p, q); B = sq(s_, t0); a_, b_ = T(A_), T(B); num = a_ + "-" + T(r0); den = b_ + "-" + T(u); pa = a_ + "+" + T(r0); pb = b_ + "+" + T(u)
    pt = T(c); body = fr(num, den); e = (A_ - r0) / (B - u); v = Q(p * u, s_ * r0); f = P(x - c)
    l = opener(pt, body) + [ch("ភាគយក និងភាគបែងសុទ្ធតែមានឫសការេ ដូច្នេះត្រូវគុណនឹងកន្សោមឆ្លាស់ទាំងពីរ ។", K(r"យើងគុណភាគយក និងភាគបែងនឹង $(@a)(@b)$ ។", a=pa, b=pb))]
    st = [lim(pt) + fr("(" + num + ")(" + pa + ")(" + pb + ")", "(" + den + ")(" + pb + ")(" + pa + ")"),
          lim(pt) + fr("(" + T(p * x + q - r0**2) + ")(" + pb + ")", "(" + T(s_ * x + t0 - u**2) + ")(" + pa + ")"),
          lim(pt) + fr(T(p if p != 1 else "") + f + "(" + pb + ")", T(s_ if s_ != 1 else "") + f + "(" + pa + ")"),
          fr(T(p) + r"\times" + T(2 * u), T(s_) + r"\times" + T(2 * r0)), T(v)]
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, c, v)], "conjugate_both", "hard")
def a_two_roots():
    while True:
        c = ni(-3, 6); w = rng.randint(1, 6) if ch(0, 1) else ch(2, 3, 5, 6, 7); w2 = w**2 if ch(0, 1) else ch(2, 3, 5, 6, 7, 10)
        p = ni(1, 5); s_ = ni(1, 5, (p,)); q = w2 - p * c; t0 = w2 - s_ * c
        if q != t0: break
    A_ = sq(p, q); B = sq(s_, t0); a_, b_ = T(A_), T(B); num = a_ + "-" + b_; plus = a_ + "+" + b_; pt = T(c); body = fr(num, x - c)
    e = (A_ - B) / (x - c); v = (p - s_) / (2 * sqrt(w2)); f = P(x - c)
    top = expand(A_**2 - B**2); kk = p - s_
    l = opener(pt, body) + [conj_word(plus)]
    st = [lim(pt) + fr("(" + T(p * x + q) + ")-(" + T(s_ * x + t0) + ")", f + "(" + plus + ")"),
          lim(pt) + fr((T(kk) if abs(kk) != 1 else ("-" if kk < 0 else "")) + f, f + "(" + plus + ")"),
          lim(pt) + fr(kk, plus), fr(kk, r"2\sqrt{" + T(w2) + "}") if sqrt(w2).is_integer is False else fr(kk, 2 * sqrt(w2)), T(v)]
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, c, v)], "conjugate_two_roots", "medium")
def a_root_lin():
    while True:
        c = ni(-3, 6); m_ = ch(1, 1, 2, -1); r0 = rng.randint(1, 6); n_ = r0 - m_ * c; p = ch(1, 2, 3, 4, 5); q = r0**2 - p * c
        if p != 2 * m_ * r0: break
    S = sq(p, q); L_ = m_ * x + n_; num = T(S) + "-(" + T(L_) + ")"; plus = T(S) + "+" + T(L_) if m_ > 0 else T(S) + "+(" + T(L_) + ")"
    pt = T(c); body = fr(num, x - c); e = (S - L_) / (x - c)
    top = expand(p * x + q - L_**2); G = cancel(top / (x - c)); v = Q(G.subs(x, c)) / (2 * r0); f = P(x - c)
    l = opener(pt, body) + [conj_word(plus)]
    st = [lim(pt) + fr("(" + T(p * x + q) + ")-(" + T(L_) + ")^{2}", f + "(" + plus + ")"),
          lim(pt) + fr(top, f + "(" + plus + ")"), lim(pt) + fr(f + P(G), f + "(" + plus + ")"),
          lim(pt) + fr(G, plus), fr(G.subs(x, c), 2 * r0), T(v)]
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, c, v)], "conjugate_root_minus_linear", "hard")
def a_cbrt():
    while True:
        c = ni(-4, 7); r0 = ch(1, 2, 3); p = ch(1, 1, 2, 3); q = r0**3 - p * c
        if abs(q) < 60: break
    C = (p * x + q)**Q(1, 3); ct = r"\sqrt[3]{" + T(p * x + q) + "}"; pt = T(c); den_mode = ch(0, 0, 1); A2 = ct + "^{2}+" + T(r0) + ct + "+" + T(r0**2); f = P(x - c)
    A2 = "(" + ct + ")^{2}+" + (T(r0) if r0 != 1 else "") + ct + "+" + T(r0**2)
    if den_mode == 0:
        body = fr(ct + "-" + T(r0), x - c); e = (C - r0) / (x - c); v = Q(p, 3 * r0**2)
        st = [lim(pt) + fr("(" + T(p * x + q) + ")-" + T(r0**3), f + r"\left[" + A2 + r"\right]"),
              lim(pt) + fr(fac(p) .replace("1", "") + f if p != 1 else f, f + r"\left[" + A2 + r"\right]"),
              lim(pt) + fr(p, A2), fr(p, T(3 * r0**2)) , T(v)]
    else:
        body = fr(x - c, ct + "-" + T(r0)); e = (x - c) / (C - r0); v = Q(3 * r0**2, p)
        st = [lim(pt) + fr(f + r"\left[" + A2 + r"\right]", "(" + T(p * x + q) + ")-" + T(r0**3)),
              lim(pt) + fr(f + r"\left[" + A2 + r"\right]", (T(p) if p != 1 else "") + f),
              lim(pt) + fr(A2, p), T(v)]
    l = opener(pt, body) + [ch(r"ឫសទីបីត្រូវដោះដោយរូបមន្ត $a^{3}-b^{3}=(a-b)(a^{2}+ab+b^{2})$ ។", K(r"ប្រើកន្សោមឆ្លាស់នៃឫសទីបី ៖ យក $a=@a$ និង $b=@b$ រួចគុណនឹង $a^{2}+ab+b^{2}$ ។", a=ct, b=T(r0)))]
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, c, v)], "conjugate_cube_root", "hard")
def a_split():
    a = ni(1, 6); b = ni(1, 8); s2 = ch("sc", "ss")
    if s2 == "sc":
        A_ = sqrt(1 + a * x); B = (1 + b * x)**Q(1, 3); bt = r"\sqrt[3]{" + T(b * x + 1) + "}"; vb = Q(b, 3)
        p2 = r"\frac{" + bt + "-1}{x}"; res2 = fr(b, 3)
        d2 = K(r"$$@L@p=@L\frac{@b x}{x\left[(@c)^{2}+@c+1\right]}=@r$$", L=lim("0"), p=p2, b=T(b) if b != 1 else "", c=bt, r=res2).replace(" x}", "x}")
    else:
        b = ni(1, 6, (a,)); A_ = sqrt(1 + a * x); B = sqrt(1 + b * x); bt = T(B); vb = Q(b, 2); res2 = fr(b, 2)
        p2 = r"\frac{" + bt + "-1}{x}"
        d2 = K(r"$$@L@p=@L\frac{@b x}{x(@c+1)}=@r$$", L=lim("0"), p=p2, b=T(b) if b != 1 else "", c=bt, r=res2).replace(" x}", "x}")
    at = T(A_); body = fr(at + "-" + bt, x); e = (A_ - B) / x; v = Q(a, 2) - vb; pt = "0"
    l = opener(pt, body) + [ch("យើងបូក និងដក $1$ ក្នុងភាគយក ដើម្បីបំបែកជាពីរលីមីត ៖", "សរសេរភាគយកជាផលដកនៃកន្សោមពីរ ដោយដក និងបូក $1$ ៖")]
    l.append(K(r"$$\frac{@a-@b}{x}=\frac{@a-1}{x}-\frac{@b-1}{x}$$", a=at, b=bt))
    l.append(K(r"$$@L\frac{@a-1}{x}=@L\frac{@k x}{x(@a+1)}=@r$$", L=lim("0"), a=at, k=T(a) if a != 1 else "", r=fr(a, 2)).replace(" x}", "x}"))
    l.append(d2)
    l.append("លីមីតទាំងពីរមានតម្លៃកំណត់ ដូច្នេះលីមីតនៃផលដកស្មើផលដកនៃលីមីត ៖")
    l.append("$$" + lim(pt) + body + "=" + fr(a, 2) + "-" + res2 + "=" + T(v) + "$$")
    return Atom(body, pt, l, v, [ck(e, 0, v)], "split_two_radicals", "hard")
def a_sub_sqrt():
    a = ch(1, 2, 3, 4, 5); mode = ch(0, 1, 2, 3); s_ = "\\sqrt{x}"; pt = T(a**2); tp = T(a)
    if mode == 0:
        body = fr(x - a**2, s_ + "-" + T(a)); e = (x - a**2) / (sqrt(x) - a); v = Integer(2 * a)
        st = [lim(tp, "t") + fr("t^{2}-" + T(a**2), "t-" + T(a)), lim(tp, "t") + fr("(t-" + T(a) + ")(t+" + T(a) + ")", "t-" + T(a)), lim(tp, "t") + "(t+" + T(a) + ")", T(v)]
    elif mode == 1:
        b = ni(1, 5); c0 = a * (a + b)
        body = fr("x+" + (T(b) if b != 1 else "") + s_ + "-" + T(c0), x - a**2); e = (x + b * sqrt(x) - c0) / (x - a**2); v = Q(2 * a + b, 2 * a)
        st = [lim(tp, "t") + fr("t^{2}+" + (T(b) if b != 1 else "") + "t-" + T(c0), "t^{2}-" + T(a**2)), lim(tp, "t") + fr("(t-" + T(a) + ")(t+" + T(a + b) + ")", "(t-" + T(a) + ")(t+" + T(a) + ")"), lim(tp, "t") + fr("t+" + T(a + b), "t+" + T(a)), T(v)]
    elif mode == 2:
        body = fr("x" + s_ + "-" + T(a**3), x - a**2); e = (x * sqrt(x) - a**3) / (x - a**2); v = Q(3 * a, 2)
        st = [lim(tp, "t") + fr("t^{3}-" + T(a**3), "t^{2}-" + T(a**2)), lim(tp, "t") + fr("(t-" + T(a) + ")(t^{2}+" + (T(a) if a != 1 else "") + "t+" + T(a**2) + ")", "(t-" + T(a) + ")(t+" + T(a) + ")"), lim(tp, "t") + fr("t^{2}+" + (T(a) if a != 1 else "") + "t+" + T(a**2), "t+" + T(a)), T(v)]
    else:
        body = fr("x-" + T(2 * a) + s_ + "+" + T(a**2), x - a**2); e = (x - 2 * a * sqrt(x) + a**2) / (x - a**2); v = Integer(0)
        st = [lim(tp, "t") + fr("(t-" + T(a) + ")^{2}", "(t-" + T(a) + ")(t+" + T(a) + ")"), lim(tp, "t") + fr("t-" + T(a), "t+" + T(a)), "0"]
    l = opener(pt, body) + [K(r"តាង $t=\sqrt{x}$ $\Rightarrow$ $x=t^{2}$ ។ បើ $x\to @p$ នោះ $t\to @a$ ។", p=pt, a=tp)] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, a**2, v)], "substitution_square_root", ch("medium", "hard"))
def a_sub_cbrt():
    a = ch(1, 2, 3); pt = T(a**3); tp = T(a); r3 = r"\sqrt[3]{x}"
    body = fr(r3 + "-" + T(a), x - a**3); e = (x**Q(1, 3) - a) / (x - a**3); v = Q(1, 3 * a**2)
    st = [lim(tp, "t") + fr("t-" + T(a), "t^{3}-" + T(a**3)), lim(tp, "t") + fr("t-" + T(a), "(t-" + T(a) + ")(t^{2}+" + (T(a) if a != 1 else "") + "t+" + T(a**2) + ")"), lim(tp, "t") + fr(1, "t^{2}+" + (T(a) if a != 1 else "") + "t+" + T(a**2)), T(v)]
    if ch(0, 1):
        b = ch(2, 3, 4, 5); body = fr(T(b) + "(" + r3 + "-" + T(a) + ")", x - a**3); e = b * e; v = b * v; st = [fr(T(b) + "(t-" + T(a) + ")", "t^{3}-" + T(a**3)).join([lim(tp, "t"), ""]), lim(tp, "t") + fr(b, "t^{2}+" + (T(a) if a != 1 else "") + "t+" + T(a**2)), T(v)]
    l = opener(pt, body) + [K(r"តាង $t=\sqrt[3]{x}$ $\Rightarrow$ $x=t^{3}$ ។ កាលណា $x\to @p$ គេបាន $t\to @a$ ។", p=pt, a=tp)] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, a**3, v)], "substitution_cube_root", "hard")

# ---------- Limits at infinity ----------
def inf_pt():
    v = ch(oo, oo, -oo); return v, V(v)
def tiny_note():
    return ch(r"(យើងដឹងថា $\frac{c}{x^{n}}\to0$ កាលណា $x\to\pm\infty$)", r"ដោយប្រភាគដែលមាន $x$ នៅភាគបែងខិតជិត $0$", "")
def a_poly_inf():
    s_, pt = inf_pt(); d = ch(2, 3, 3, 4, 5); lc = ni(-4, 5); c1 = ni(-6, 6); c0 = ni(-7, 7)
    Pp = lc * x**d + c1 * x**(d - 1) + c0; v = (oo if lc > 0 else -oo) * (1 if (s_ == oo or d % 2 == 0) else -1); b = "(" + T(Pp) + ")"
    br = T(lc) + ("+" if c1 > 0 else "") + fr(c1, x) + ("+" if c0 > 0 else "") + fr(c0, x**d)
    l = [ch("ដាក់តួដែលមានដឺក្រេខ្ពស់បំផុតជាកត្តា ៖", K(r"យើងដាក់ $x^{@d}$ ជាកត្តារួម ៖", d=d), "លីមីតនៃពហុធាត្រង់អនន្តស្មើលីមីតនៃតួដែលមានដឺក្រេខ្ពស់បំផុត ។ បង្ហាញដោយដាក់ជាកត្តា ៖")]
    l += chain(lim(pt) + b, [lim(pt) + "x^{" + str(d) + r"}\left(" + br + r"\right)"])
    l.append(K(r"កាលណា $x\to @p$ វង់ក្រចកខិតជិត $@c$ ហើយ $x^{@d}\to @i$ ។", p=pt, c=T(lc), d=d, i=V(oo if (s_ == oo or d % 2 == 0) else -oo)))
    return Atom(b, pt, l, v, [ck(Pp, s_, v)], "polynomial_at_infinity", "easy")
def a_rat_inf():
    s_, pt = inf_pt()
    dn = ch(1, 2, 2, 3); dd = ch(1, 2, 2, 3); mode = ch("eq", "eq", "lo", "hi")
    if mode == "eq": dd = dn
    elif mode == "lo": dn = dd - 1 if dd > 1 else 0
    else:
        dd = max(1, dn - 1); dn = dd + ch(1, 1, 2)
    a = ni(-5, 6); b = ni(1, 5) * ch(1, 1, -1)
    cn = [rng.randint(-6, 6) for _ in range(dn)]; cd = [rng.randint(-6, 6) for _ in range(dd)]
    N = a * x**dn + sum(c * x**i for i, c in enumerate(cn)); D = b * x**dd + sum(c * x**i for i, c in enumerate(cd))
    body = fr(N, D); dm = max(dn, dd)
    nb = "+".join(fr(c, x**(dn - i)) if i < dn else T(c) for i, c in [(dn, a)] + list(enumerate(cn))[::-1] if c != 0).replace("+-", "-")
    db = "+".join(fr(c, x**(dd - i)) if i < dd else T(c) for i, c in [(dd, b)] + list(enumerate(cd))[::-1] if c != 0).replace("+-", "-")
    xn = "x^{" + str(dn) + "}" if dn > 1 else ("x" if dn == 1 else ""); xd = "x^{" + str(dd) + "}" if dd > 1 else "x"
    l = opener(pt, body, "ii") if dn > 0 else []
    top = xn + r"\left(" + nb + r"\right)" if dn else T(N)
    if mode == "eq":
        v = Q(a, b); st = [lim(pt) + fr(top, xd + r"\left(" + db + r"\right)"), lim(pt) + fr(nb, db), fr(a, b)] + ([T(v)] if Q(a, b).q != b else [])
        if ch(0, 1): l.append(K(r"ដាក់ $@x$ ជាកត្តារួមទាំងភាគយក និងភាគបែង ។", x=xn))
    elif mode == "lo":
        v = Integer(0); st = [lim(pt) + fr(top, xd + r"\left(" + db + r"\right)"), lim(pt) + (r"\frac{1}{" + ("x^{" + str(dd - dn) + "}" if dd - dn > 1 else "x") + r"}\cdot" + fr(nb, db) if dn else fr(top, xd + r"\left(" + db + r"\right)")), "0"]
        l.append("ដឺក្រេភាគយកតូចជាងដឺក្រេភាគបែង ។")
        if dn == 0: st = st[:1] + ["0"]
    else:
        e_ = dn - dd; sg = 1 if (s_ == oo or e_ % 2 == 0) else -1; v = (oo if a * b > 0 else -oo) * sg
        xe = "x^{" + str(e_) + "}" if e_ > 1 else "x"
        st = [lim(pt) + fr(top, xd + r"\left(" + db + r"\right)"), lim(pt) + xe + r"\cdot" + fr(nb, db)]
        l.append("ដឺក្រេភាគយកធំជាងដឺក្រេភាគបែង ។")
    l += chain(lim(pt) + body, st)
    if mode == "hi":
        l.append(K(r"ប្រភាគខិតជិត $@r$ ហើយ $@xe\to @i$ កាលណា $x\to @p$ ។", r=fr(a, b), xe=xe, i=V(oo if sg * 1 > 0 else -oo), p=pt))
    return Atom(body, pt, l, v, [ck(N / D, s_, v)], {"eq": "rational_infinity_equal_degree", "lo": "rational_infinity_lower_degree", "hi": "rational_infinity_higher_degree"}[mode], ch("easy", "medium"))
def a_prod_inf():
    s_, pt = inf_pt(); a = ch(1, 2, 3); b = ni(-5, 5); c = ch(1, 2, 3); d = ni(-5, 5); m_ = ch(2, 3); e = ch(1, 2, 3); f = ni(-5, 5)
    N = (a * x + b)**m_ * (c * x + d); D = (e * x + f)**(m_ + 1); v = Q(a**m_ * c, e**(m_ + 1)); body = fr(P(a * x + b) + "^{" + str(m_) + "}" + P(c * x + d), P(e * x + f) + "^{" + str(m_ + 1) + "}")
    u = lambda p_, q_: T(p_) + ("+" if q_ > 0 else "") + fr(q_, x)
    st = [lim(pt) + fr("x^{" + str(m_) + r"}\left(" + u(a, b) + r"\right)^{" + str(m_) + r"}\cdot x\left(" + u(c, d) + r"\right)", "x^{" + str(m_ + 1) + r"}\left(" + u(e, f) + r"\right)^{" + str(m_ + 1) + "}"),
          lim(pt) + fr(r"\left(" + u(a, b) + r"\right)^{" + str(m_) + r"}\left(" + u(c, d) + r"\right)", r"\left(" + u(e, f) + r"\right)^{" + str(m_ + 1) + "}"),
          fr(T(a) + "^{" + str(m_) + r"}\times" + T(c), T(e) + "^{" + str(m_ + 1) + "}"), T(v)]
    l = opener(pt, body, "ii") + [ch("មិនចាំបាច់ពន្លាតទេ ។ យើងដាក់ $x$ ជាកត្តាក្នុងវង់ក្រចកនីមួយៗ ។", "ដាក់ $x$ ជាកត្តាក្នុងកត្តានីមួយៗ ។")] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(N / D, s_, v)], "rational_infinity_product_form", "medium")
def a_sqrt_lin():
    s_, pt = inf_pt(); k = ch(1, 2, 3, 4, 5); a = k**2; b = rng.randint(-5, 5); c = rng.randint(1, 7); d = ch(1, 2, 3, -1, -2); e = ni(-6, 6); g = ni(-3, 4) if ch(0, 1) else 0
    S = sqrt(a * x**2 + b * x + c); s0 = T(S); num = s0 + (("+" if g > 0 else "") + T(g) if g else "")
    sg = 1 if s_ == oo else -1; v = Q(sg * k, d); body = fr(num, d * x + e)
    ab = "|x|" ; inner = r"\sqrt{" + T(a) + ("+" if b > 0 else "") + (fr(b, x) if b else "") + "+" + fr(c, x**2) + "}"
    ext = ("+" if g > 0 else "") + fr(g, x) if g else ""; extm = fr(g, x) if g else ""
    den = T(d) + ("+" if e > 0 else "") + fr(e, x)
    if s_ == oo:
        w = r"កាលណា $x\to+\infty$ យើងមាន $x>0$ ដូច្នេះ $\sqrt{x^{2}}=|x|=x$ ។"
        st = [lim(pt) + fr("x" + inner + (("+" if g > 0 else "") + T(g) if g else ""), "x" + r"\left(" + den + r"\right)"), lim(pt) + fr(inner + ext, den), fr(k, d)]
    else:
        w = r"កាលណា $x\to-\infty$ យើងមាន $x<0$ ដូច្នេះ $\sqrt{x^{2}}=|x|=-x$ ។ ត្រូវប្រយ័ត្នសញ្ញា ។"
        st = [lim(pt) + fr("-x" + inner + (("+" if g > 0 else "") + T(g) if g else ""), "x" + r"\left(" + den + r"\right)"), lim(pt) + fr("-" + inner + ext, den), fr(-k, d)]
    if Q(sg * k, d).q != abs(d) or d < 0: st.append(T(v))
    l = opener(pt, body, "ii") + [w] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck((S + g) / (d * x + e), s_, v)], "radical_over_linear_at_infinity", ch("medium", "hard"))
def a_sqrt_mx():
    k = ch(1, 1, 1, 2, 3, 4); b = ni(-8, 8) * (2 * k if ch(0, 1) else 1); c = rng.randint(-4, 9); neg = ch(0, 0, 1)
    if c < 0 and b == 0: c = 1
    S = sqrt(k**2 * x**2 + b * x + c); s0 = T(S); kx = T(k * x)
    if not neg:
        pt = r"+\infty"; p0 = oo; body = "(" + s0 + "-" + kx + ")"; e = S - k * x; plus = s0 + "+" + kx; v = Q(b, 2 * k)
        inner = r"\sqrt{" + T(k**2) + ("+" if b > 0 else "") + fr(b, x) + ("+" + fr(c, x**2) if c > 0 else (fr(c, x**2) if c < 0 else "")) + "}"
        den = "x" + r"\left(" + inner + ("+" + T(k)) + r"\right)"; rest = fr(T(b) + ("+" if c > 0 else "") + (fr(c, x) if c else ""), inner + "+" + T(k))
        top = T(b * x + c)
        st = [lim(pt) + fr("(" + s0 + ")^{2}-(" + kx + ")^{2}", plus), lim(pt) + fr(top, plus), lim(pt) + fr("x" + r"\left(" + T(b) + ("+" if c > 0 else "") + (fr(c, x) if c else "") + r"\right)", den), lim(pt) + rest, fr(b, 2 * k), ]
        if Q(b, 2 * k).q != 2 * k: st.append(T(v))
    else:
        pt = r"-\infty"; p0 = -oo; body = "(" + s0 + "+" + kx + ")"; e = S + k * x; minus = s0 + "-" + kx; v = -Q(b, 2 * k)
        inner = r"\sqrt{" + T(k**2) + ("+" if b > 0 else "") + fr(b, x) + ("+" + fr(c, x**2) if c > 0 else (fr(c, x**2) if c < 0 else "")) + "}"
        top = T(b * x + c)
        st = [lim(pt) + fr("(" + s0 + ")^{2}-(" + kx + ")^{2}", minus), lim(pt) + fr(top, minus),
              lim(pt) + fr("x" + r"\left(" + T(b) + ("+" if c > 0 else "") + (fr(c, x) if c else "") + r"\right)", "-x" + r"\left(" + inner + "+" + T(k) + r"\right)"),
              lim(pt) + fr(T(b) + ("+" if c > 0 else "") + (fr(c, x) if c else ""), "-" + r"\left(" + inner + "+" + T(k) + r"\right)"), T(v)]
    l = opener(pt, body, "mi") + [ch(K(r"គុណ និងចែកនឹងកន្សោមឆ្លាស់ $@e$ ។", e=(plus if not neg else minus)), "ប្រើកន្សោមឆ្លាស់ ដើម្បីបំបាត់រាងមិនកំណត់ ។")]
    if neg: l.append(r"កាលណា $x\to-\infty$ យើងមាន $\sqrt{x^{2}}=-x$ ។")
    l += chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, p0, v)], "infinity_minus_infinity_radical", "hard")
def a_two_sqrt_inf():
    a = ni(-7, 8); b = ni(-7, 8, (a,)); c = rng.randint(1, 6); d = rng.randint(1, 6); A_ = sqrt(x**2 + a * x + c); B = sqrt(x**2 + b * x + d); at, bt = T(A_), T(B); pt = r"+\infty"
    body = "(" + at + "-" + bt + ")"; e = A_ - B; v = Q(a - b, 2); plus = at + "+" + bt; top = (a - b) * x + c - d
    i1 = r"\sqrt{1" + ("+" if a > 0 else "") + fr(a, x) + "+" + fr(c, x**2) + "}"; i2 = r"\sqrt{1" + ("+" if b > 0 else "") + fr(b, x) + "+" + fr(d, x**2) + "}"
    tt = T(a - b) + (("+" if c - d > 0 else "") + fr(c - d, x) if c != d else "")
    st = [lim(pt) + fr("(" + T(x**2 + a * x + c) + ")-(" + T(x**2 + b * x + d) + ")", plus), lim(pt) + fr(top, plus), lim(pt) + fr("x" + r"\left(" + tt + r"\right)", "x" + r"\left(" + i1 + "+" + i2 + r"\right)"), lim(pt) + fr(tt, i1 + "+" + i2), fr(a - b, "1+1"), T(v)]
    l = opener(pt, body, "mi") + [conj_word(plus).replace("ភាគយក និងភាគបែង", "ភាគយក និងភាគបែង (ដោយចាត់ទុកភាគបែងស្មើ $1$)") if False else K(r"គុណ និងចែកនឹងកន្សោមឆ្លាស់ $@e$ ។", e=plus)] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, oo, v)], "infinity_minus_infinity_two_radicals", "hard")
def a_sqrt_notindet():
    k = ch(2, 3, 4); m_ = ni(1, 5, (k,)); s_ = oo; c = rng.randint(1, 6); S = sqrt(k**2 * x**2 + c)
    mode = ch(0, 1)
    if mode == 0:
        body = "(" + T(S) + "-" + T(m_ * x) + ")"; e = S - m_ * x; pt = r"+\infty"; v = oo if k > m_ else -oo; co = k - m_
        st = [lim(pt) + r"x\left(\sqrt{" + T(k**2) + "+" + fr(c, x**2) + "}-" + T(m_) + r"\right)"]
        l = [K(r"មើលដំបូងមានរាង $\infty-\infty$ ប៉ុន្តែមេគុណ $@k$ និង $@m$ ខុសគ្នា ដូច្នេះដាក់ $x$ ជាកត្តា ។", k=k, m=m_)] + chain(lim(pt) + body, st)
        l.append(K(r"វង់ក្រចកខិតជិត $@k-@m=@c$ ហើយ $x\to+\infty$ ។", k=k, m=m_, c=T(co)))
    else:
        body = "(" + T(S) + "+" + T(m_ * x) + ")"; e = S + m_ * x; pt = r"+\infty"; v = oo
        l = [r"កាលណា $x\to+\infty$ តួទាំងពីរខិតជិត $+\infty$ ហើយផលបូកមិនមែនជារាងមិនកំណត់ទេ ។"]
    return Atom(body, pt, l, v, [ck(e, oo, v)], "radical_infinity_not_indeterminate", "medium")
def a_cbrt_inf():
    a = ch(3, 6, 9, -3, -6, 12); c = rng.randint(1, 5); pt = r"+\infty"; C = (x**3 + a * x**2 + c)**Q(1, 3); ct = r"\sqrt[3]{" + T(x**3 + a * x**2 + c) + "}"
    body = "(" + ct + "-x)"; e = C - x; v = Q(a, 3)
    i_ = r"\sqrt[3]{1" + ("+" if a > 0 else "") + fr(a, x) + "+" + fr(c, x**3) + "}"
    den = "(" + ct + ")^{2}+x" + ct + "+x^{2}"
    st = [lim(pt) + fr("(" + T(x**3 + a * x**2 + c) + ")-x^{3}", den), lim(pt) + fr(a * x**2 + c, den), lim(pt) + fr("x^{2}" + r"\left(" + T(a) + "+" + fr(c, x**2) + r"\right)", "x^{2}" + r"\left[\left(" + i_ + r"\right)^{2}+" + i_ + r"+1\right]"), fr(a, "1+1+1"), T(v)]
    l = opener(pt, body, "mi") + [r"យក $a=" + ct + r"$ និង $b=x$ ហើយប្រើ $a-b=\frac{a^{3}-b^{3}}{a^{2}+ab+b^{2}}$ ។"] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, oo, v)], "infinity_minus_infinity_cube_root", "hard")
def a_sqrt_zero():
    a = rng.randint(1, 9); b = rng.randint(1, 9); mode = ch(0, 1, 2); pt = r"+\infty"; A_ = sqrt(x + a + b); B = sqrt(x + b)
    at, bt = T(A_), T(B); plus = at + "+" + bt
    if mode == 0:
        body = "(" + at + "-" + bt + ")"; e = A_ - B; v = Integer(0)
        st = [lim(pt) + fr("(" + T(x + a + b) + ")-(" + T(x + b) + ")", plus), lim(pt) + fr(a, plus), "0"]
        w = "ភាគយកជាចំនួនថេរ ហើយភាគបែងខិតជិត $+\\infty$ ។"
    elif mode == 1:
        body = r"\sqrt{x}(" + at + "-" + bt + ")"; e = sqrt(x) * (A_ - B); v = Q(a, 2)
        st = [lim(pt) + fr(T(a) + r"\sqrt{x}", plus), lim(pt) + fr(T(a) + r"\sqrt{x}", r"\sqrt{x}\left(\sqrt{1+" + fr(a + b, x) + r"}+\sqrt{1+" + fr(b, x) + r"}\right)"), fr(a, "1+1"), T(v)]
        w = r"ដាក់ $\sqrt{x}$ ជាកត្តារួមក្នុងភាគបែង ។"
    else:
        body = "x(" + T(sqrt(x**2 + a)) + "-x)"; e = x * (sqrt(x**2 + a) - x); v = Q(a, 2); at = T(sqrt(x**2 + a)); plus = at + "+x"
        st = [lim(pt) + fr("x" + r"\left[(" + T(x**2 + a) + r")-x^{2}\right]", plus), lim(pt) + fr(T(a) + "x", "x" + r"\left(\sqrt{1+" + fr(a, x**2) + r"}+1\right)"), fr(a, "1+1"), T(v)]
        w = "បន្ទាប់មកដាក់ $x$ ជាកត្តារួមក្នុងភាគបែង ។"
    l = [K(r"គុណនឹងកន្សោមឆ្លាស់ $@e$ ។", e=plus)] + chain(lim(pt) + body, st) + [w]
    return Atom(body, pt, l, v, [ck(e, oo, v)], "radical_difference_at_infinity", "hard" if mode else "medium")
def a_rat_minus_lin():
    s_, pt = inf_pt(); p = ch(1, 2, 3); b = ni(-5, 6); c = ni(-6, 6); e0 = ni(-5, 6)
    N = p * x**2 + b * x + c; D = x + e0; e = N / D - p * x; top = expand(N - p * x * D); v = top.coeff(x, 1); body = r"\left(" + fr(N, D) + "-" + T(p * x) + r"\right)"
    st = [lim(pt) + fr(T(N) + "-" + T(p * x) + P(D), D), lim(pt) + fr(top, D)]
    if top.coeff(x, 1) != 0: st += [lim(pt) + fr("x" + r"\left(" + T(top.coeff(x, 1)) + ("+" if top.coeff(x, 0) > 0 else "") + (fr(top.coeff(x, 0), x) if top.coeff(x, 0) != 0 else "") + r"\right)", "x" + r"\left(1" + ("+" if e0 > 0 else "") + fr(e0, x) + r"\right)"), T(v)]
    else: st += ["0"]
    l = opener(pt, body, "mi") + [ch("ដាក់ជាប្រភាគតែមួយសិន ។", "យកភាគបែងរួម ។")] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(e, s_, v)], "infinity_minus_infinity_rational", "medium")
def a_root_ratio():
    s_ = oo; pt = r"+\infty"; a = ch(1, 4, 9, 16); b = ch(1, 4, 9); k = ni(1, 4); m_ = ch(1, 2, 3); ra = sqrt(a); rb = sqrt(b); c = rng.randint(1, 5); d = rng.randint(1, 5)
    A_ = sqrt(a * x**2 + c); B = sqrt(b * x**2 + d); N = A_ + k * x; D = B + m_ * x; v = Q(ra + k, rb + m_); body = fr(T(A_) + "+" + T(k * x), T(B) + "+" + T(m_ * x))
    st = [lim(pt) + fr(r"x\left(\sqrt{" + T(a) + "+" + fr(c, x**2) + "}+" + T(k) + r"\right)", r"x\left(\sqrt{" + T(b) + "+" + fr(d, x**2) + "}+" + T(m_) + r"\right)"), fr(T(ra) + "+" + T(k), T(rb) + "+" + T(m_)), T(v)]
    l = opener(pt, body, "ii") + [r"ដោយ $x>0$ យើងមាន $\sqrt{x^{2}}=x$ ។"] + chain(lim(pt) + body, st)
    return Atom(body, pt, l, v, [ck(N / D, oo, v)], "radical_ratio_at_infinity", "medium")
def a_sqrt_pm():
    """Both ends: the two limits differ."""
    k = ch(1, 2, 3); d = ch(1, 2, 3); c = rng.randint(1, 6); e = ni(-5, 5); S = sqrt(k**2 * x**2 + c); f = S / (d * x + e); body = fr(S, d * x + e)
    vp, vm = Q(k, d), Q(-k, d); inner = r"\sqrt{" + T(k**2) + "+" + fr(c, x**2) + "}"; den = T(d) + ("+" if e > 0 else "") + fr(e, x)
    q = K(ch(r"គេឱ្យអនុគមន៍ $f(x)=@b$ ។ គណនាលីមីតនៃ $f(x)$ ត្រង់ $-\infty$ និងត្រង់ $+\infty$ ។", r"គណនា $\lim_{x\to+\infty}f(x)$ និង $\lim_{x\to-\infty}f(x)$ ដោយដឹងថា $f(x)=@b$ ។"), b=body)
    l = [r"ចំពោះ $x\neq0$ យើងមាន $\sqrt{x^{2}}=|x|$ ។", r"កាលណា $x\to+\infty$ យើងបាន $|x|=x$ ៖",
         "$$" + lim(r"+\infty") + "f(x)=" + lim(r"+\infty") + fr("x" + inner, r"x\left(" + den + r"\right)") + "=" + T(vp) + "$$",
         r"កាលណា $x\to-\infty$ យើងបាន $|x|=-x$ ៖",
         "$$" + lim(r"-\infty") + "f(x)=" + lim(r"-\infty") + fr("-x" + inner, r"x\left(" + den + r"\right)") + "=" + T(vm) + "$$",
         r"ដូចនេះ $\boxed{\lim_{x\to+\infty}f(x)=" + T(vp) + r"}$ និង $\boxed{\lim_{x\to-\infty}f(x)=" + T(vm) + r"}$ ។"]
    return Atom("", "", l, None, [ck(f, oo, vp), ck(f, -oo, vm)], "radical_both_infinities", "hard", q=q, plain=True, ans=r"\lim_{x\to+\infty}f(x)=" + T(vp) + r",\ \lim_{x\to-\infty}f(x)=" + T(vm))

# ---------- One-sided limits ----------
def sgn_table(fs, c_list, row_label):
    """Sign table with factors; fs is a list of (latex, signs list per interval, zero index or None)."""
    pts = [r"-\infty"] + [T(c) for c in c_list] + [r"+\infty"]; n = 2 * len(pts) - 1
    xr = []
    for i, p_ in enumerate(pts):
        xr.append(p_); xr.append("")
    xr = xr[:n]
    spec = "c|" + "c" * n
    rows = ["x & " + " & ".join(xr)]
    for lab, cells in fs:
        rows.append(lab + " & " + " & ".join(cells))
    return r"\begin{array}{" + spec + "}\n" + " \\\\\n\\hline\n".join(rows) + "\n\\end{array}"
def lin_cells(c, cl):
    """Sign cells of x-c on a grid with the points cl."""
    cells = [""]
    for i in range(len(cl) + 1):
        lo = cl[i - 1] if i else None; cells.append("-" if (lo is None or lo < c) else "+") if False else None
    cells = [""]
    for i in range(len(cl) + 1):
        hi = cl[i] if i < len(cl) else None
        cells.append("+" if (hi is None and True and (not cl or cl[-1] >= c)) or (hi is not None and hi > c) else "-")
        if i < len(cl):
            cells.append("0" if cl[i] == c else "")
    cells.append("")
    return cells
def a_pole_simple():
    c = ni(-5, 6); p = ch(1, 2, 3, -1, -2); b = ni(-6, 6); n = p * x + b; nc = n.subs(x, c)
    if nc == 0: return a_pole_simple()
    pt = T(c); body = fr(n, x - c); e = n / (x - c); vr = oo if nc > 0 else -oo; vl = -vr
    tab = sgn_table([("x" + ("-" + T(c) if c > 0 else "+" + T(-c)), lin_cells(c, [c]))], [c], "")
    q = K(ch(r"គណនាលីមីតឆ្វេង និងលីមីតស្តាំនៃ $f(x)=@b$ ត្រង់ $x=@c$ ។ តើ $f$ មានលីមីតត្រង់ $x=@c$ ឬទេ ?",
             r"គេឱ្យ $f(x)=@b$ ។ គណនា $\lim_{x\to @c^{-}}f(x)$ និង $\lim_{x\to @c^{+}}f(x)$ រួចសន្និដ្ឋាន ។",
             r"សិក្សាលីមីតនៃអនុគមន៍ $f(x)=@b$ ត្រង់ $x=@c$ ។"), b=body, c=pt)
    l = [K(r"ភាគយកខិតជិត $@n$ កាលណា $x\to @c$ ។ សញ្ញានៃភាគបែងអាស្រ័យនឹងទីតាំងរបស់ $x$ ធៀបនឹង $@c$ ។", n=T(nc), c=pt),
         K(r"បើ $x\to @c^{-}$ នោះ $x<@c$ ហើយ $@d\to 0^{-}$ ។ គេបាន $$\lim_{x\to @c^{-}}f(x)=@vl$$", c=pt, d=T(x - c), vl=V(vl)),
         K(r"បើ $x\to @c^{+}$ នោះ $x>@c$ ហើយ $@d\to 0^{+}$ ។ គេបាន $$\lim_{x\to @c^{+}}f(x)=@vr$$", c=pt, d=T(x - c), vr=V(vr)),
         K(r"ដូចនេះ $\boxed{\lim_{x\to @c^{-}}f(x)=@vl}$ និង $\boxed{\lim_{x\to @c^{+}}f(x)=@vr}$ ។ លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ដូច្នេះ $f$ គ្មានលីមីតត្រង់ $x=@c$ ទេ ។", c=pt, vl=V(vl), vr=V(vr))]
    return Atom("", "", l, None, [ck(e, c, vl, "-"), ck(e, c, vr, "+")], "one_sided_simple_pole", "medium", q=q, plain=True,
                ans=K(r"\lim_{x\to @c^{-}}f(x)=@vl,\ \lim_{x\to @c^{+}}f(x)=@vr", c=pt, vl=V(vl), vr=V(vr)),
                diag=[{"type": "sign_table", "latex": tab, "image": None, "alt_km": K(r"តារាងសញ្ញានៃភាគបែង $@d$ ជុំវិញ $x=@c$ ។", d=T(x - c), c=pt)}])
def a_pole_quad():
    c = ni(-4, 4); d = ni(-5, 5, (c,)); side = ch("+", "-"); n = ni(1, 4) * x + ni(-5, 5); nc = n.subs(x, c)
    if nc == 0: return a_pole_quad()
    D = expand((x - c) * (x - d)); e = n / D; pt = T(c) + "^{" + side + "}"; body = fr(n, D); oth = c - d
    s1 = 1 if side == "+" else -1; sg = (1 if nc > 0 else -1) * (1 if oth > 0 else -1) * s1; v = oo * sg
    l = [K(r"យើងដាក់ភាគបែងជាកត្តា ៖ $@D=@F$ ។", D=T(D), F=P(x - c) + P(x - d)),
         K(r"កាលណា $x\to @p$ ភាគយកខិតជិត $@n$ កត្តា $@f$ ខិតជិត $@o$ ហើយ $@g\to 0^{@s}$ ។", p=pt, n=T(nc), f=T(x - d), o=T(oth), g=T(x - c), s=side),
         K(r"ដូច្នេះប្រភាគមានរាង $\frac{@n}{(@o)\times 0^{@s}}$ ហើយសញ្ញារបស់វាគឺ @w ។", n=T(nc), o=T(oth), s=side, w="វិជ្ជមាន" if sg > 0 else "អវិជ្ជមាន")]
    return Atom(body, pt, l, v, [ck(e, c, v, side)], "one_sided_quadratic_denominator", "medium")
def a_pole_double():
    c = ni(-5, 6); n = ch(1, 2, 3, -1, -2, -3) * x**2 + rng.randint(-3, 3); nc = n.subs(x, c); 
    if nc == 0: return a_pole_double()
    D = (x - c)**2; e = n / D; pt = T(c); body = fr(n, expand(D)); v = oo if nc > 0 else -oo; 
    l = [K(r"ភាគបែង $@D=@F$ វិជ្ជមានជានិច្ចចំពោះ $x\neq @c$ ហើយខិតជិត $0^{+}$ ។ ភាគយកខិតជិត $@n$ ។", D=T(expand(D)), F=P(x - c) + "^{2}", c=pt, n=T(nc)),
         "ដូច្នេះលីមីតឆ្វេង និងលីមីតស្តាំស្មើគ្នា ។"]
    return Atom(body, pt, l, v, [ck(e, c, v, "-"), ck(e, c, v, "+")], "one_sided_double_pole", "medium")
def a_abs():
    a = ni(-5, 6); mode = ch(0, 1, 2); k = ch(1, 2, 3); pt = T(a); f = T(x - a); A_ = "|" + f + "|"
    if mode == 0:
        body = fr(k * x - k * a, A_) if False else fr(A_, k * x - k * a); e = sp.Abs(x - a) / (k * x - k * a); vr, vl = Q(1, k), Q(-1, k); simp_r = fr(f, T(k) + "(" + f + ")"); simp_l = fr("-(" + f + ")", T(k) + "(" + f + ")")
    elif mode == 1:
        b = ni(-5, 6, (-a,)) ; 
        if a + b == 0: return a_abs()
        body = fr(expand((x - a) * (x + b)), A_); e = (x - a) * (x + b) / sp.Abs(x - a); vr, vl = Integer(a + b), Integer(-(a + b)); simp_r = fr("(" + f + ")(" + T(x + b) + ")", f); simp_l = fr("(" + f + ")(" + T(x + b) + ")", "-(" + f + ")")
    else:
        body = fr(r"\sqrt{" + T(expand((x - a)**2)) + "}", x - a); e = sqrt((x - a)**2) / (x - a); vr, vl = Integer(1), Integer(-1); simp_r = fr(f, f); simp_l = fr("-(" + f + ")", f)
    pre = K(r"យើងមាន $\sqrt{@e}=|@f|$ ។", e=T(expand((x - a)**2)), f=f) if mode == 2 else ""
    q = K(ch(r"គេឱ្យ $f(x)=@b$ ។ គណនាលីមីតស្តាំ និងលីមីតឆ្វេងនៃ $f$ ត្រង់ $x=@c$ ។ តើ $f$ មានលីមីតត្រង់ចំណុចនេះឬទេ ?",
             r"សិក្សាលីមីតនៃ $f(x)=@b$ ត្រង់ $x=@c$ ។"), b=body, c=pt)
    l = [pre, K(r"តាមនិយមន័យតម្លៃដាច់ខាត បើ $x>@c$ នោះ $|@f|=@f$ ហើយបើ $x<@c$ នោះ $|@f|=-(@f)$ ។", c=pt, f=f),
         "$$" + lim(pt + "^{+}") + "f(x)=" + lim(pt + "^{+}") + simp_r + "=" + T(vr) + "$$", "$$" + lim(pt + "^{-}") + "f(x)=" + lim(pt + "^{-}") + simp_l + "=" + T(vl) + "$$",
         K(r"ដូចនេះ $\boxed{\lim_{x\to @c^{+}}f(x)=@r}$ និង $\boxed{\lim_{x\to @c^{-}}f(x)=@l}$ ។ លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ដូច្នេះ $f$ គ្មានលីមីតត្រង់ $x=@c$ ទេ ។", c=pt, r=T(vr), l=T(vl))]
    return Atom("", "", l, None, [ck(e, a, vr, "+"), ck(e, a, vl, "-")], "one_sided_absolute_value", "medium", q=q, plain=True, ans=K(r"\lim_{x\to @c^{+}}f(x)=@r,\ \lim_{x\to @c^{-}}f(x)=@l", c=pt, r=T(vr), l=T(vl)))
def a_sqrt_edge():
    a = ni(-4, 8); b = ni(1, 8); mode = ch(0, 1, 2); pt = T(a) + "^{+}"; f = T(x - a); r_ = r"\sqrt{" + f + "}"
    if mode == 0:
        body = fr(x - a, r_); e = (x - a) / sqrt(x - a); v = Integer(0)
        l = [K(r"ចំពោះ $x>@a$ យើងមាន $@f=(@r)^{2}$ ។", a=T(a), f=f, r=r_)] + chain(lim(pt) + body, [lim(pt) + r_, "0"])
    elif mode == 1:
        body = fr(r_, x - a); e = sqrt(x - a) / (x - a); v = oo
        l = [K(r"ចំពោះ $x>@a$ យើងសម្រួលបាន $\frac{@r}{@f}=\frac{1}{@r}$ ។ ភាគបែងខិតជិត $0^{+}$ ។", a=T(a), r=r_, f=f)]
    else:
        n1 = x + b; v = Integer(0)
        D = expand((x - a) * (x + b)); 
        if a + b == 0: return a_sqrt_edge()
        body = r"\sqrt{" + T(D) + "}"; e = sqrt(D)
        s_ = ch(1, 2); l = [K(r"កន្សោមក្រោមឫសខិតជិត $0^{+}$ ពីព្រោះ $@D=@F$ ។ តាមលីមីតនៃអនុគមន៍បណ្ដាក់ លីមីតនេះស្មើ $\sqrt{0}=0$ ។", D=T(D), F=P(x - a) + P(x + b))] if a + b > 0 else None
        if l is None: return a_sqrt_edge()
    return Atom(body, pt, l, v, [ck(e, a, v, "+")], "one_sided_radical_edge", "medium")
def a_piece():
    c = ni(-3, 4); m1 = ni(-3, 4); b1 = ni(-5, 5); m2 = ni(-3, 4); b2 = ni(-5, 5); quad = ch(0, 1); pt = T(c)
    g1 = (x**2 + b1) if quad else m1 * x + b1; g2 = m2 * x + b2
    if ch(0, 1, 1):
        b2 = g1.subs(x, c) - m2 * c; g2 = m2 * x + b2
    L1, L2 = g1.subs(x, c), g2.subs(x, c); eq = L1 == L2
    F = r"f(x)=\begin{cases}" + T(g1) + r" & x<" + pt + r"\\" + T(g2) + r" & x\ge " + pt + r"\end{cases}"
    q = K(ch(r"គេឱ្យអនុគមន៍កំណត់ជាផ្នែក $$@F$$ សិក្សាលីមីតនៃ $f$ ត្រង់ $x=@c$ ។", r"ចំពោះអនុគមន៍ $$@F$$ គណនា $\lim_{x\to @c^{-}}f(x)$ និង $\lim_{x\to @c^{+}}f(x)$ ។ តើ $\lim_{x\to @c}f(x)$ មានឬទេ ?"), F=F, c=pt)
    l = [K(r"កាលណា $x\to @c^{-}$ យើងមាន $x<@c$ ដូច្នេះ $f(x)=@g$ ៖", c=pt, g=T(g1)), "$$" + lim(pt + "^{-}") + "f(x)=" + lim(pt + "^{-}") + "(" + T(g1) + ")=" + T(L1) + "$$",
         K(r"កាលណា $x\to @c^{+}$ យើងមាន $x>@c$ ដូច្នេះ $f(x)=@g$ ៖", c=pt, g=T(g2)), "$$" + lim(pt + "^{+}") + "f(x)=" + lim(pt + "^{+}") + "(" + T(g2) + ")=" + T(L2) + "$$"]
    if eq:
        l.append(K(r"យើងឃើញថាលីមីតឆ្វេងស្មើលីមីតស្តាំ ។ ដូចនេះ $\boxed{\lim_{x\to @c}f(x)=@v}$ ។", c=pt, v=T(L1))); ans = lim(pt) + "f(x)=" + T(L1)
    else:
        l.append(K(r"ដូចនេះ លីមីតឆ្វេង $\boxed{@l}$ មិនស្មើលីមីតស្តាំ $\boxed{@r}$ ហើយ $f$ គ្មានលីមីតត្រង់ $x=@c$ ទេ ។", l=T(L1), r=T(L2), c=pt)); ans = r"\lim_{x\to " + pt + "^{-}}f(x)=" + T(L1) + r",\ \lim_{x\to " + pt + "^{+}}f(x)=" + T(L2)
    return Atom("", "", l, None, [ck(g1, c, L1, "-", "left branch"), ck(g2, c, L2, "+", "right branch")], "one_sided_piecewise", "medium", q=q, plain=True, ans=ans)
def graph_png(row_id, segs, dots):
    fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=110)
    for (x0, x1, fn) in segs:
        xs = np.linspace(x0, x1, 100); ax.plot(xs, [fn(u) for u in xs], lw=1.8, color="#1f4e9c")
    for (px, py, fill) in dots:
        ax.plot([px], [py], "o", ms=5, mfc="#1f4e9c" if fill else "white", mec="#1f4e9c", zorder=5)
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 7)
    for sd in ("top", "right"): ax.spines[sd].set_visible(False)
    for sd in ("left", "bottom"): ax.spines[sd].set_position("zero")
    ax.set_xticks(range(-5, 6)); ax.set_yticks(range(-5, 7)); ax.tick_params(labelsize=7); ax.grid(alpha=0.25)
    rel = f"diagrams/{row_id}.png"; fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig); return rel
def a_graph():
    c = rng.randint(-2, 3); L1 = ni(-3, 4); L2 = ni(-3, 5, (L1,)); yc = ch(L1, L2, ni(-4, 5, (L1, L2))); m1 = ch(1, 2, -1); m2 = ch(1, -1, 0)
    if ch(0, 1, 0): L2 = L1
    g1 = m1 * (x - c) + L1; g2 = m2 * (x - c) + L2; pt = T(c)
    f1 = sp.lambdify(x, g1); f2 = sp.lambdify(x, g2)
    lo = max(-6, c - (5 if m1 == 1 else 2)); hi = min(6, c + 3)
    tik = (r"\begin{tikzpicture}\begin{axis}[axis lines=middle,xlabel=$x$,ylabel=$y$,xmin=-6,xmax=6,ymin=-6,ymax=7]" + "\n"
           + r"\addplot[thick,domain=%d:%d] {%s};" % (lo, c, str(g1).replace("**", "^")) + "\n" + r"\addplot[thick,domain=%d:%d] {%s};" % (c, hi, str(g2).replace("**", "^")) + "\n"
           + r"\addplot[only marks,mark=o] coordinates {(%d,%d) (%d,%d)};" % (c, L1, c, L2) + "\n" + r"\addplot[only marks,mark=*] coordinates {(%d,%d)};" % (c, yc) + "\n" + r"\end{axis}\end{tikzpicture}")
    q = K(ch(r"រូបខាងក្រោមជាក្រាបនៃអនុគមន៍ $f$ ។ ដោយអានលើក្រាប រក $\lim_{x\to @c^{-}}f(x)$ , $\lim_{x\to @c^{+}}f(x)$ និង $f(@c)$ ។ តើ $f$ មានលីមីតត្រង់ $x=@c$ ឬទេ ?",
             r"អនុគមន៍ $f$ មានក្រាបដូចរូប ។ រកលីមីតឆ្វេង លីមីតស្តាំ និងតម្លៃ $f(@c)$ ត្រង់ $x=@c$ រួចសន្និដ្ឋានអំពីលីមីតនៃ $f$ ត្រង់ចំណុចនេះ ។"), c=pt)
    same = L1 == L2; kk = ni(-4, 5); gk = T(kk * x)
    q += K(r" បន្ទាប់មកគណនា $\lim_{x\to @c^{+}}\left[f(x)@s\right]$ ។", c=pt, s=("+" if kk > 0 else "") + gk)
    fv = L2 + kk * c
    l = [K(r"នៅខាងឆ្វេងនៃ $x=@c$ ក្រាបខិតជិតចំណុចដែលមានអរដោនេ $@a$ ដូច្នេះ $\lim_{x\to @c^{-}}f(x)=@a$ ។", c=pt, a=T(L1)),
         K(r"នៅខាងស្តាំនៃ $x=@c$ ក្រាបខិតជិតចំណុចដែលមានអរដោនេ $@b$ ដូច្នេះ $\lim_{x\to @c^{+}}f(x)=@b$ ។", c=pt, b=T(L2)),
         K(r"ចំណុចពេញនៅត្រង់ $x=@c$ មានអរដោនេ $@y$ ដូច្នេះ $f(@c)=@y$ ។", c=pt, y=T(yc)),
         K(r"តាមប្រមាណវិធីលើលីមីត $\lim_{x\to @c^{+}}\left[f(x)@s\right]=@b@t=@v$ ។", c=pt, s=("+" if kk > 0 else "") + gk, b=T(L2), t=("+" if kk * c >= 0 else "") + T(kk * c), v=T(fv)),
         (K(r"ដូចនេះ លីមីតទាំងពីរស្មើគ្នា ហើយ $\boxed{\lim_{x\to @c}f(x)=@a}$ ។", c=pt, a=T(L1)) if same else K(r"ដូចនេះ លីមីតឆ្វេង $\boxed{@a}$ មិនស្មើលីមីតស្តាំ $\boxed{@b}$ ហើយ $f$ គ្មានលីមីតត្រង់ $x=@c$ ទេ ។", a=T(L1), b=T(L2), c=pt))]
    ans = (lim(pt) + "f(x)=" + T(L1)) if same else K(r"\lim_{x\to @c^{-}}f(x)=@a,\ \lim_{x\to @c^{+}}f(x)=@b", c=pt, a=T(L1), b=T(L2))
    l.insert(-1, ""); l = [u for u in l if u]
    l[-1] = l[-1].rstrip(" ។") + K(r" ហើយ $\boxed{\lim_{x\to @c^{+}}\left[f(x)@s\right]=@v}$ ។", c=pt, s=("+" if kk > 0 else "") + gk, v=T(fv))
    ans += r",\ " + T(fv)
    pf = lambda rid: graph_png(rid, [(lo, c, f1), (c, hi, f2)], [(c, L1, False), (c, L2, False), (c, yc, True)])
    return Atom("", "", l, None, [ck(g1, c, L1, "-", "left branch of the drawn graph"), ck(g2, c, L2, "+", "right branch of the drawn graph"), ck(g2 + kk * x, c, fv, "+", "follow-on limit")], "one_sided_read_from_graph", "easy", q=q, plain=True, ans=ans,
                diag=[{"type": "graph", "latex": tik, "image": None, "alt_km": K(r"ក្រាបមានពីរផ្នែកបន្ទាត់ជួបបន្ទាត់ឈរ $x=@c$ ។ រង្វង់ចំហនៅអរដោនេ $@a$ និង $@b$ ចំណុចពេញនៅអរដោនេ $@y$ ។", c=pt, a=T(L1), b=T(L2), y=T(yc))}], png=pf)

# ---------- Parameters ----------
def p_quad_ab():
    c = ni(-5, 6); d = ni(-6, 6, (-c,)) if False else ni(-6, 6); pt = T(c); L = c - d if False else None
    Lv = c + d  # (x-c)(x+d)/(x-c) -> c+d
    if Lv == 0: return p_quad_ab()
    a_ = d - c; b_ = -c * d; pfx = ch("a", "m"); s2 = ch("b", "n"); den = x - c
    body = "\\frac{x^{2}+" + pfx + "x+" + s2 + "}{" + T(den) + "}"
    q = K(ch(r"រកចំនួនពិត $@p$ និង $@s$ ដើម្បីឱ្យ $@L@b=@v$ ។", r"កំណត់តម្លៃ $@p$ និង $@s$ ដោយដឹងថា $@L@b=@v$ ។", r"គេដឹងថា $@L@b=@v$ ។ រកតម្លៃនៃចំនួនពិត $@p$ និង $@s$ ។"), p=pfx, s=s2, L=lim(pt), b=body, v=T(Lv))
    e1 = pfx + "x"
    l = [K(r"ភាគបែងខិតជិត $0$ កាលណា $x\to @c$ ។ ដើម្បីឱ្យលីមីតមានតម្លៃកំណត់ ភាគយកត្រូវខិតជិត $0$ ដែរ ។ ដូច្នេះ $x=@c$ ជាឫសនៃភាគយក ៖", c=pt),
         K(r"$$@c2@cc@p+@s=0\Leftrightarrow @s=@e$$", c2=T(c**2), cc=("+" + (T(c) if c != 1 else "") if c > 0 else (T(c) if c != -1 else "-")), p=pfx, s=s2, e=T(sp.Symbol(pfx) * (-c) - c**2)),
         K(r"ជំនួសចូលភាគយក ហើយភាគយកមានកត្តា $@f$ ៖ $x^{2}+@px+@s=(@f)(x+@p@c)$ ។ ដូច្នេះ", f=P(den)[1:-1], p=pfx, s=s2, c=("+" if c > 0 else "") + T(c)),
         K(r"$$@L@b=@L(x+@p@c)=@c2+@p$$", L=lim(pt), b=body, c=("+" if c > 0 else "") + T(c), p=pfx, c2=T(2 * c)),
         K(r"តាមបម្រាប់ $@c2+@p=@v$ នោះ $@p=@a$ ហើយ $@s=@bb$ ។", c2=T(2 * c), p=pfx, v=T(Lv), a=T(a_), s=s2, bb=T(b_)),
         K(r"ដូចនេះ $\boxed{@p=@a,\ @s=@bb}$ ។", p=pfx, a=T(a_), s=s2, bb=T(b_))]
    e = (x**2 + a_ * x + b_) / den
    return Atom("", "", l, None, [ck(e, c, Lv, note="limit with the found values"), check(f"({c})**2+({a_})*({c})+({b_})", "0", "root condition")], "parameter_rational_two_constants", "hard", q=q, plain=True, ans=K(r"@p=@a,\ @s=@bb", p=pfx, a=T(a_), s=s2, bb=T(b_)))
def p_m_value():
    c = ni(-4, 5); pt = T(c); w = ni(-6, 6); 
    m0 = ni(-6, 7, (c,)); Lv = c - m0  # (x-c)(x-m)/(x-c) -> c-m
    N_ = r"x^{2}-(m" + ("+" if c > 0 else "-") + T(abs(c)) + ")x+" + (T(c) if c != 1 else "") + "m" if c > 0 else r"x^{2}-(m-" + T(-c) + ")x-" + (T(-c) if c != -1 else "") + "m"
    body = fr(N_, x - c)
    q = K(ch(r"រកតម្លៃ $m$ ដើម្បីឱ្យ $@L@b=@v$ ។", r"គេឱ្យ $f(x)=@b$ ។ កំណត់ $m$ ដោយដឹងថា $@Lf(x)=@v$ ។"), L=lim(pt), b=body, v=T(Lv))
    l = [K(r"ភាគយកមានឫស $x=@c$ និង $x=m$ ព្រោះផលបូកឫសស្មើ $m+@cc$ និងផលគុណឫសស្មើ $@ccm$ ។ ដូច្នេះ ភាគយកស្មើ $@f(x-m)$ ។", c=pt, cc=pn(c), ccm=(T(c) if c != 1 else "") + "m" if c != -1 else "-m", f=P(x - c)),
         "$$" + lim(pt) + body + "=" + lim(pt) + "(x-m)=" + pt + "-m$$", K(r"តាមបម្រាប់ $@c-m=@v$ នោះ $m=@m$ ។", c=pt, v=T(Lv), m=T(m0)), K(r"ដូចនេះ $\boxed{m=@m}$ ។", m=T(m0))]
    e = (x - c) * (x - m0) / (x - c)
    return Atom("", "", l, None, [ck(expand((x - c) * (x - m0)) / (x - c), c, Lv, note="limit with m substituted")], "parameter_value_of_m", "medium", q=q, plain=True, ans="m=" + T(m0))
def p_sqrt_ab():
    c = ni(-3, 6); r0 = rng.randint(1, 5); q0 = r0**2 - c; pt = T(c); Lv = Q(1, 2 * r0)
    body = r"\frac{\sqrt{x+a}-b}{" + T(x - c) + "}"
    q = K(ch(r"រកចំនួនពិត $a$ និង $b$ $(b>0)$ ដើម្បីឱ្យ $@L@B=@v$ ។", r"កំណត់ $a$ និង $b$ ដែល $b>0$ ដោយដឹងថា $@L@B=@v$ ។"), L=lim(pt), B=body, v=T(Lv))
    l = [K(r"ដោយភាគបែងខិតជិត $0$ ហើយលីមីតមានតម្លៃកំណត់ ភាគយកត្រូវខិតជិត $0$ ដែរ ៖ $\sqrt{@c+a}-b=0$ ឬ $@c+a=b^{2}$ ។", c=T(c)),
         K(r"យើងបាន $x+a=(@f)+b^{2}$ ។ គុណនឹងកន្សោមឆ្លាស់ $\sqrt{x+a}+b$ ៖", f=T(x - c)),
         K(r"$$@L@B=@L\frac{(x+a)-b^{2}}{(@f)(\sqrt{x+a}+b)}=@L\frac{1}{\sqrt{x+a}+b}=\frac{1}{2b}$$", L=lim(pt), B=body, f=T(x - c)),
         K(r"តាមបម្រាប់ $\frac{1}{2b}=@v$ នោះ $b=@b$ ។ បន្ទាប់មក $a=b^{2}-@cc=@a$ ។", v=T(Lv), b=r0, cc=pn(c), a=T(q0)), K(r"ដូចនេះ $\boxed{a=@a,\ b=@b}$ ។", a=T(q0), b=r0)]
    return Atom("", "", l, None, [ck((sqrt(x + q0) - r0) / (x - c), c, Lv, note="limit with the found values")], "parameter_radical_two_constants", "hard", q=q, plain=True, ans=K(r"a=@a,\ b=@b", a=T(q0), b=r0))
def p_inf_ab():
    d = ni(-5, 6); Lv = ni(-6, 7); cst = ni(-7, 8); pt = ch(r"+\infty", r"-\infty"); p0 = oo if pt[0] == "+" else -oo
    body = r"\frac{ax^{2}+bx" + ("+" if cst > 0 else "") + T(cst) + "}{" + T(x + d) + "}"
    q = K(ch(r"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ $@L@B=@v$ ។", r"កំណត់ $a$ និង $b$ បើគេដឹងថា $@L@B=@v$ ។"), L=lim(pt), B=body, v=T(Lv))
    l = [K(r"បើ $a\neq0$ ដឺក្រេភាគយកធំជាងដឺក្រេភាគបែង ហើយលីមីតជាអនន្ត ។ ដូច្នេះត្រូវមាន $a=0$ ។"),
         K(r"ពេលនោះ $$@L\frac{bx@c}{@d}=b$$", L=lim(pt), c=("+" if cst > 0 else "") + T(cst), d=T(x + d)), K(r"តាមបម្រាប់ $b=@v$ ។", v=T(Lv)), K(r"ដូចនេះ $\boxed{a=0,\ b=@v}$ ។", v=T(Lv))]
    return Atom("", "", l, None, [ck((Lv * x + cst) / (x + d), p0, Lv, note="limit with the found values")], "parameter_at_infinity", "medium", q=q, plain=True, ans=K(r"a=0,\ b=@v", v=T(Lv)))
def p_slant_ab():
    d = ni(-5, 6); p = ch(1, 2, 3, -1); b1 = ni(-6, 6); c1 = ni(-6, 8); N = p * x**2 + b1 * x + c1; D = x + d; qn = sp.div(sp.Poly(N, x), sp.Poly(D, x))[0].as_expr(); a_ = qn.coeff(x, 1); b_ = qn.coeff(x, 0); rem = expand(N - qn * D); pt = r"+\infty"
    if rem == 0: return p_slant_ab()
    body = r"\left(" + fr(N, D) + r"-ax-b\right)"
    q = K(ch(r"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ $@L@B=0$ ។", r"គេឱ្យ $f(x)=@F$ ។ កំណត់ $a$ និង $b$ ដើម្បីឱ្យ $@L\left[f(x)-(ax+b)\right]=0$ ។"), L=lim(pt), B=body, F=fr(N, D))
    l = [K(r"ចែកពហុធា $@N$ នឹង $@D$ យើងបាន $$@F=@Q@R$$", N=T(N), D=T(D), F=fr(N, D), Q=T(qn), R=("+" if rem > 0 else "") + fr(rem, D) if rem != 0 else ""),
         K(r"ដូច្នេះ $$@B=(@p-a)x+(@q-b)@R$$", B=body, p=T(a_), q=T(b_), R=("+" if rem > 0 else "") + fr(rem, D) if rem != 0 else ""),
         K(r"តួ $@r$ ខិតជិត $0$ ។ ដើម្បីឱ្យលីមីតស្មើ $0$ មេគុណ $x$ និងតួថេរត្រូវស្មើសូន្យ ។", r=fr(rem, D) if rem != 0 else "0"), K(r"ដូចនេះ $\boxed{a=@a,\ b=@b}$ ។", a=T(a_), b=T(b_))]
    return Atom("", "", l, None, [ck(N / D - a_ * x - b_, oo, 0, note="limit with the found values")], "parameter_slant_form", "hard", q=q, plain=True, ans=K(r"a=@a,\ b=@b", a=T(a_), b=T(b_)))
def p_sqrt_inf():
    k = ch(1, 2, 3); Lv = ni(-5, 6); a_ = 2 * k * Lv; c = rng.randint(1, 8); pt = r"+\infty"; body = r"\left(\sqrt{" + T(k**2 * x**2) + "+ax+" + T(c) + "}-bx\\right)"
    q = K(ch(r"រកចំនួនពិត $a$ និង $b$ $(b>0)$ ដើម្បីឱ្យ $@L@B=@v$ ។", r"កំណត់ $a$ និង $b$ $(b>0)$ ដោយដឹងថា $@L@B=@v$ ។"), L=lim(pt), B=body, v=T(Lv))
    S = sqrt(k**2 * x**2 + a_ * x + c)
    l = [K(r"ដាក់ $x$ ជាកត្តា ៖ $@B=x\left(\sqrt{@k2+\frac{a}{x}+@c}-b\right)$ ។ បើ $b\neq @k$ លីមីតស្មើអនន្ត ដូច្នេះត្រូវមាន $b=@k$ ។", B=body[6:-7] if False else r"\sqrt{" + T(k**2 * x**2) + "+ax+" + T(c) + "}-bx", k2=T(k**2), c=fr(c, x**2), k=k),
         K(r"ពេលនោះគុណនឹងកន្សោមឆ្លាស់ ៖ $$@L\frac{ax+@c}{\sqrt{@e+ax+@c}+@kx}=\frac{a}{@k2}$$", L=lim(pt), c=T(c), e=T(k**2 * x**2), k=T(k) if k != 1 else "", k2=T(2 * k)),
         K(r"តាមបម្រាប់ $\frac{a}{@k2}=@v$ នោះ $a=@a$ ។", k2=T(2 * k), v=T(Lv), a=T(a_)), K(r"ដូចនេះ $\boxed{a=@a,\ b=@k}$ ។", a=T(a_), k=k)]
    return Atom("", "", l, None, [ck(S - k * x, oo, Lv, note="limit with the found values")], "parameter_radical_at_infinity", "hard", q=q, plain=True, ans=K(r"a=@a,\ b=@k", a=T(a_), k=k))
def p_piece_exist():
    c = ni(-3, 4); pt = T(c); m1 = ni(-3, 4); b1 = ni(-5, 5); k = ch(1, 2, 3); g1 = m1 * x + b1; L1 = g1.subs(x, c); a_ = L1 - k * c
    if ch(0, 1):
        F = r"f(x)=\begin{cases}" + T(g1) + r" & x<" + pt + r"\\" + T(k * x) + r"+a & x\ge " + pt + r"\end{cases}"; 
    else:
        F = r"f(x)=\begin{cases}" + T(g1) + r" & x\le " + pt + r"\\" + T(k * x) + r"+a & x>" + pt + r"\end{cases}"
    q = K(ch(r"គេឱ្យ $$@F$$ រកតម្លៃ $a$ ដើម្បីឱ្យ $f$ មានលីមីតត្រង់ $x=@c$ ។", r"ចំពោះ $$@F$$ កំណត់ $a$ ដើម្បីឱ្យលីមីតឆ្វេង និងលីមីតស្តាំត្រង់ $x=@c$ ស្មើគ្នា ។"), F=F, c=pt)
    l = ["$$" + lim(pt + "^{-}") + "f(x)=" + subx(g1, c) + "=" + T(L1) + "$$", "$$" + lim(pt + "^{+}") + "f(x)=" + T(k * c) + "+a$$",
         K(r"$f$ មានលីមីតត្រង់ $x=@c$ លុះត្រាតែលីមីតឆ្វេងស្មើលីមីតស្តាំ ៖ $@k+a=@L$ ។", c=pt, k=T(k * c), L=T(L1)), K(r"ដូចនេះ $\boxed{a=@a}$ ។", a=T(a_))]
    return Atom("", "", l, None, [ck(g1, c, L1, "-", "left"), ck(k * x + a_, c, L1, "+", "right with a found")], "parameter_piecewise", "medium", q=q, plain=True, ans="a=" + T(a_))
def p_discuss():
    d = ni(-5, 6); c = ni(-5, 6); pt = r"+\infty"; body = r"\frac{mx^{2}+" + "x" + ("+" if c > 0 else "") + T(c) + "}{" + T(x + d) + "}"
    q = K(r"គេឱ្យ $f(x)=@b$ ដែល $m$ ជាប៉ារ៉ាម៉ែត្រ ។ គណនា $\lim_{x\to+\infty}f(x)$ តាមតម្លៃនៃ $m$ ។", b=body)
    l = [r"ចំពោះ $m=0$ ភាគយក និងភាគបែងមានដឺក្រេ $1$ ដូចគ្នា ហើយមេគុណនាំមុខស្មើ $1$ ។ លីមីតស្មើ $1$ ។",
         r"ចំពោះ $m\neq0$ ដឺក្រេភាគយកធំជាងដឺក្រេភាគបែង ៖", r"$$f(x)=x\cdot\frac{m+\frac{1}{x}" + ("+" if c > 0 else "") + fr(c, x**2) + "}{1" + ("+" if d > 0 else "") + fr(d, x) + "}$$",
         r"ប្រភាគខិតជិត $m$ ហើយ $x\to+\infty$ ។ ដូច្នេះលីមីតស្មើ $+\infty$ បើ $m>0$ និងស្មើ $-\infty$ បើ $m<0$ ។",
         r"ដូចនេះ $\boxed{\lim_{x\to+\infty}f(x)=1}$ បើ $m=0$ , $\boxed{+\infty}$ បើ $m>0$ និង $\boxed{-\infty}$ បើ $m<0$ ។"]
    return Atom("", "", l, None, [ck((x + c) / (x + d), oo, 1, note="m=0"), ck((2 * x**2 + x + c) / (x + d), oo, oo, note="instance m=2"), ck((-3 * x**2 + x + c) / (x + d), oo, -oo, note="instance m=-3")],
                "parameter_discussion", "hard", q=q, plain=True, ans=r"1\ (m=0),\ +\infty\ (m>0),\ -\infty\ (m<0)")

# ---------- Limit theorems ----------
def t_squeeze():
    a = ni(-3, 5); Lv = ni(-5, 7); k = ch(1, 2, 3); pt = T(a); g = Lv - k * (x - a)**2; h = Lv + ni(1, 3) * (x - a)**2
    q = K(ch(r"អនុគមន៍ $f$ ផ្ទៀងផ្ទាត់ $@g\le f(x)\le @h$ ចំពោះគ្រប់ $x$ ជិត $@a$ ។ គណនា $\lim_{x\to @a}f(x)$ ។", r"គេដឹងថា $@g\le f(x)\le @h$ ជុំវិញ $x=@a$ ។ រកលីមីតនៃ $f(x)$ កាលណា $x\to @a$ ។"), g=T(g), h=T(h), a=pt)
    l = [K(r"យើងគណនាលីមីតនៃអនុគមន៍ទាំងពីរដែលព័ទ្ធ $f$ ៖ $$@L(@g)=@v,\quad @L(@h)=@v$$", L=lim(pt), g=T(g), h=T(h), v=T(Lv)),
         "ដោយ $f(x)$ ស្ថិតនៅចន្លោះអនុគមន៍ទាំងពីរ ហើយអនុគមន៍ទាំងពីរមានលីមីតដូចគ្នា នោះ $f(x)$ មានលីមីតនោះដែរ ។", K(r"ដូចនេះ $\boxed{\lim_{x\to @a}f(x)=@v}$ ។", a=pt, v=T(Lv))]
    return Atom("", "", l, None, [ck(g, a, Lv, note="lower bound"), ck(h, a, Lv, note="upper bound")], "theorem_squeeze", "medium", q=q, plain=True, ans=lim(pt) + "f(x)=" + T(Lv))
def t_abs_bound():
    Lv = ni(-5, 7); k = ch(1, 2, 3, 5); n_ = ch(1, 2); pt = r"+\infty"
    q = K(ch(r"អនុគមន៍ $f$ ផ្ទៀងផ្ទាត់ $|f(x)-@L|\le \frac{@k}{x^{@n}}$ ចំពោះគ្រប់ $x>0$ ។ គណនា $\lim_{x\to+\infty}f(x)$ ។", r"គេដឹងថា $|f(x)-@L|\le\frac{@k}{x^{@n}}$ ចំពោះ $x>0$ ។ រកលីមីតនៃ $f$ ត្រង់ $+\infty$ ។"), L=pn(Lv) if Lv < 0 else T(Lv), k=k, n=n_).replace("^{1}", "")
    l = [K(r"វិសមភាពនេះមានន័យថា $$@L-\frac{@k}{x^{@n}}\le f(x)\le @L+\frac{@k}{x^{@n}}$$", L=T(Lv), k=k, n=n_).replace("^{1}", ""), K(r"កាលណា $x\to+\infty$ អនុគមន៍ទាំងពីរនៅសងខាងខិតជិត $@L$ ព្រោះ $\frac{@k}{x^{@n}}\to0$ ។", L=T(Lv), k=k, n=n_).replace("^{1}", ""),
         K(r"ដូចនេះ $\boxed{\lim_{x\to+\infty}f(x)=@L}$ ។", L=T(Lv))]
    return Atom("", "", l, None, [ck(Lv - k / x**n_, oo, Lv, note="lower"), ck(Lv + k / x**n_, oo, Lv, note="upper")], "theorem_bound_at_infinity", "medium", q=q, plain=True, ans=r"\lim_{x\to+\infty}f(x)=" + T(Lv))
def t_compare():
    k = ch(1, 2, 3); c = ni(-5, 6); up = ch(0, 1); g = k * x**2 + c if up else -k * x**2 + c; pt = r"+\infty"; v = oo if up else -oo
    q = K(r"គេដឹងថា $f(x)@s @g$ ចំពោះគ្រប់ $x>0$ ។ រក $\lim_{x\to+\infty}f(x)$ ។", s=r"\ge" if up else r"\le", g=T(g))
    l = [K(r"យើងមាន $\lim_{x\to+\infty}(@g)=@v$ ។", g=T(g), v=V(v)), ("ដោយ $f(x)$ ធំជាង ឬស្មើកន្សោមនេះ ហើយកន្សោមនេះកើនដល់ $+\\infty$ នោះ $f(x)$ ក៏ខិតជិត $+\\infty$ ដែរ ។" if up else "ដោយ $f(x)$ តូចជាង ឬស្មើកន្សោមនេះ ហើយកន្សោមនេះចុះដល់ $-\\infty$ នោះ $f(x)$ ក៏ខិតជិត $-\\infty$ ដែរ ។"),
         K(r"ដូចនេះ $\boxed{\lim_{x\to+\infty}f(x)=@v}$ ។", v=V(v))]
    return Atom("", "", l, None, [ck(g, oo, v, note="bounding function")], "theorem_comparison_infinity", "medium", q=q, plain=True, ans=r"\lim_{x\to+\infty}f(x)=" + V(v))
def t_composite():
    c = ni(-3, 5); w = ch(2, 3, 4, 5); d = ni(-4, 6); 
    n1 = x + w**2 * 1 - c - 0; mode = ch("sqrt", "cbrt")
    w = w if mode == "sqrt" else ch(2, 3); inner_v = w**2 if mode == "sqrt" else w**3; p = 1
    # (x-c)(x+e)/(x-c) -> c+e = inner_v
    e_ = inner_v - c; N = expand((x - c) * (x + e_)); pt = T(c); inn = fr(N, x - c)
    if mode == "sqrt":
        body = r"\sqrt{" + inn + "}"; e = sqrt(N / (x - c)); v = Integer(w); rt = r"\sqrt{" + T(inner_v) + "}"
    else:
        body = r"\sqrt[3]{" + inn + "}"; e = (N / (x - c))**Q(1, 3); v = Integer(w); rt = r"\sqrt[3]{" + T(inner_v) + "}"
    l = [K(r"យើងគណនាលីមីតនៃកន្សោមខាងក្នុងជាមុនសិន ៖ $$@L@i=@L@f=@L(@g)=@w$$", L=lim(pt), i=inn, f=fr(P(x - c) + P(x + e_), x - c), g=T(x + e_), w=T(inner_v)),
         ch("ដោយឫសជាអនុគមន៍ជាប់ត្រង់តម្លៃនេះ យើងអាចយកលីមីតចូលក្នុងឫសបាន ៖", "លីមីតនៃអនុគមន៍បណ្ដាក់ឱ្យ ៖"), "$$" + lim(pt) + body + "=" + rt + "=" + T(v) + "$$"]
    return Atom(body, pt, l, v, [ck(e, c, v)], "theorem_composite_limit", "medium")
def t_inf_rules():
    a = ni(1, 6); s_ = ch(1, -1); A_ = s_ * a; pt = "@"; mode = ch(0, 1, 2); c = ni(-3, 5); ptt = T(c)
    F = oo; 
    if mode == 0:
        ex = r"f(x)+g(x)"; v = oo; e = 1 / (x - c)**2 + A_ + (x - c); why = r"ផលបូកនៃ $+\infty$ និងចំនួនកំណត់ស្មើ $+\infty$ ។"
    elif mode == 1:
        ex = r"f(x)g(x)"; v = oo * s_; e = (1 / (x - c)**2) * (A_ + (x - c)); why = K(r"ផលគុណនៃ $+\infty$ និងចំនួន@w ស្មើ $@v$ ។", w="វិជ្ជមាន" if s_ > 0 else "អវិជ្ជមាន", v=V(v))
    else:
        ex = r"\frac{g(x)}{f(x)}"; v = Integer(0); e = (A_ + (x - c)) * (x - c)**2; why = r"ចំនួនកំណត់ចែកនឹងអនុគមន៍ដែលខិតជិតអនន្ត ឱ្យលីមីតស្មើ $0$ ។"
    q = K(r"គេដឹងថា $@Lf(x)=+\infty$ និង $@Lg(x)=@a$ ។ គណនា $@L\left[@e\right]$ ។", L=lim(ptt), a=T(A_), e=ex)
    l = [why, K(r"ដូចនេះ $\boxed{@L\left[@e\right]=@v}$ ។", L=lim(ptt), e=ex, v=V(v))]
    return Atom("", "", l, None, [ck(e, c, v, note="instance f=1/(x-c)^2, g=A+(x-c)")], "theorem_rules_with_infinity", "easy", q=q, plain=True, ans=lim(ptt) + r"\left[" + ex + r"\right]=" + V(v))

# ---------- Limits inside a function study ----------
def s_hv():
    c = ni(-4, 4); a = ch(1, 2, 3, -1, -2); b = ni(-6, 6); 
    if a * c + b == 0: return s_hv()
    N = a * x + b; D = x - c; f = N / D; F = fr(N, D); nc = N.subs(x, c); vr = oo if nc > 0 else -oo; ct = T(c)
    q = "\n".join([K(ch(r"គេឱ្យអនុគមន៍ $f(x)=@F$ មានក្រាប $(C)$ ។", r"គេមានអនុគមន៍ $f$ កំណត់ដោយ $f(x)=@F$ ។"), F=F),
                   "ក. រកដែនកំណត់នៃ $f$ ។", K(r"ខ. គណនា $\lim_{x\to-\infty}f(x)$ , $\lim_{x\to+\infty}f(x)$ , $\lim_{x\to @c^{-}}f(x)$ និង $\lim_{x\to @c^{+}}f(x)$ ។", c=ct), "គ. ទាញរកអាស៊ីមតូតនៃក្រាប $(C)$ ។"])
    u = T(a) + ("+" if b > 0 else "") + fr(b, x); w = "1" + ("+" if c < 0 else "-") + fr(abs(c), x)
    l = [K(r"ក. $f(x)$ កំណត់លុះត្រាតែ $@D\neq0$ ។ ដូចនេះ $\boxed{D=\mathbb{R}\setminus\{@c\}}$ ។", D=T(D), c=ct),
         "ខ. ដាក់ $x$ ជាកត្តា ៖", r"$$\lim_{x\to\pm\infty}f(x)=\lim_{x\to\pm\infty}\frac{x\left(" + u + r"\right)}{x\left(" + w + r"\right)}=" + T(a) + "$$",
         K(r"ត្រង់ $x=@c$ ភាគយកខិតជិត $@n$ ។ បើ $x\to @c^{-}$ នោះ $@D\to0^{-}$ ហើយបើ $x\to @c^{+}$ នោះ $@D\to0^{+}$ ។ គេបាន $$\lim_{x\to @c^{-}}f(x)=@l,\quad\lim_{x\to @c^{+}}f(x)=@r$$", c=ct, n=T(nc), D=T(D), l=V(-vr), r=V(vr)),
         K(r"គ. ដោយ $\lim_{x\to\pm\infty}f(x)=@a$ បន្ទាត់ $y=@a$ ជាអាស៊ីមតូតដេក ។ ដោយ $\lim_{x\to @c^{\pm}}f(x)$ ជាអនន្ត បន្ទាត់ $x=@c$ ជាអាស៊ីមតូតឈរ ។", a=T(a), c=ct),
         K(r"ដូចនេះ ក្រាប $(C)$ មានអាស៊ីមតូតដេក $\boxed{y=@a}$ និងអាស៊ីមតូតឈរ $\boxed{x=@c}$ ។", a=T(a), c=ct)]
    yl = abs(a) + 5
    tik = tikz_poles(str(f).replace("**", "^"), c - 6, c + 6, a - 6, a + 6, [c], r"\addplot[dashed] coordinates {(%d,%d) (%d,%d)};" % (c, a - 6, c, a + 6) + "\n" + r"\addplot[dashed,domain=%d:%d] {%d};" % (c - 6, c + 6, a) + "\n")
    pf = lambda rid: plot_png(rid, f, c - 6, c + 6, a - 6, a + 6, asymptotes=[("v", c), ("o", Integer(a) + 0 * x)])
    return Atom("", "", l, None, [ck(f, oo, a), ck(f, -oo, a), ck(f, c, vr, "+"), ck(f, c, -vr, "-")], "study_horizontal_vertical_asymptotes", "bacii", q=q, plain=True, ans=K(r"y=@a,\ x=@c", a=T(a), c=ct),
                diag=[{"type": "graph", "latex": tik, "image": None, "alt_km": K(r"ក្រាបអ៊ីពែបូលមានអាស៊ីមតូតឈរ $x=@c$ និងអាស៊ីមតូតដេក $y=@a$ ។", a=T(a), c=ct)}], png=pf)
def s_slant():
    c = ni(-3, 3); a = ch(1, 2, -1); b = ni(-4, 4); k = ni(-4, 5)
    L_ = a * x + b; f = L_ + k / (x - c); N = expand(L_ * (x - c) + k); D = x - c; F = fr(N, D); ct = T(c); vr = oo if k > 0 else -oo
    q = "\n".join([K(r"គេឱ្យអនុគមន៍ $f(x)=@F$ ។", F=F), K(r"១. សរសេរ $f(x)$ ជារាង $ax+b+\frac{c}{@D}$ ។", D=T(D)), K(r"២. គណនា $\lim_{x\to @c^{-}}f(x)$ និង $\lim_{x\to @c^{+}}f(x)$ ។", c=ct), r"៣. គណនា $\lim_{x\to\pm\infty}\left[f(x)-(ax+b)\right]$ រួចទាញរកអាស៊ីមតូតទ្រេត ។"])
    l = [K(r"១. ចែកភាគយកនឹង $@D$ យើងបាន $$f(x)=@L@R$$", D=T(D), L=T(L_), R=("+" if k > 0 else "") + fr(k, D)),
         K(r"២. កាលណា $x\to @c$ តួ $@L$ ខិតជិត $@v$ ហើយតួ $@R$ ជាអនន្ត ។ $$\lim_{x\to @c^{-}}f(x)=@l,\quad\lim_{x\to @c^{+}}f(x)=@r$$", c=ct, L=T(L_), v=T(L_.subs(x, c)), R=fr(k, D), l=V(-vr), r=V(vr)),
         K(r"៣. យើងបាន $$\lim_{x\to\pm\infty}\left[f(x)-(@L)\right]=\lim_{x\to\pm\infty}@R=0$$", L=T(L_), R=fr(k, D)),
         K(r"ដូចនេះ បន្ទាត់ $\boxed{y=@L}$ ជាអាស៊ីមតូតទ្រេត ហើយបន្ទាត់ $\boxed{x=@c}$ ជាអាស៊ីមតូតឈរនៃក្រាប ។", L=T(L_), c=ct)]
    y0 = int(L_.subs(x, c))   # centre the window on the pole, so both branches show
    tik = tikz_poles(str(f).replace("**", "^"), c - 7, c + 7, y0 - 10, y0 + 10, [c], r"\addplot[dashed,domain=%d:%d] {%s};" % (c - 7, c + 7, str(L_).replace("**", "^")) + "\n" + r"\addplot[dashed] coordinates {(%d,%d) (%d,%d)};" % (c, y0 - 10, c, y0 + 10) + "\n")
    pf = lambda rid: plot_png(rid, f, c - 7, c + 7, y0 - 10, y0 + 10, asymptotes=[("v", c), ("o", L_)])
    return Atom("", "", l, None, [ck(N / D - L_, oo, 0), ck(N / D - L_, -oo, 0), ck(N / D, c, vr, "+"), ck(N / D, c, -vr, "-"), check(f"expand(({N})-(({L_})*({D})+({k})))", "0", "division")], "study_slant_asymptote", "bacii", q=q, plain=True, ans=K(r"y=@L,\ x=@c", L=T(L_), c=ct),
                diag=[{"type": "graph", "latex": tik, "image": None, "alt_km": K(r"ក្រាបមានអាស៊ីមតូតទ្រេត $y=@L$ និងអាស៊ីមតូតឈរ $x=@c$ ។", L=T(L_), c=ct)}], png=pf)
def s_hole():
    a = ni(-4, 4); b = ni(-4, 5, (a,)); e = ni(-5, 5, (a, -a, -b)); p = ch(1, 2)
    n1 = p * x + e
    if n1.subs(x, b) == 0 or n1.subs(x, a) == 0: return s_hole()
    N = expand((x - a) * n1); D = expand((x - a) * (x - b)); f = N / D; F = fr(N, D); at, bt = T(a), T(b); v = Q(n1.subs(x, a), a - b); nb = n1.subs(x, b); vr = oo if nb > 0 else -oo
    q = "\n".join([K(ch(r"គេឱ្យអនុគមន៍ $f(x)=@F$ ។", r"គេមានអនុគមន៍សនិទាន $f$ កំណត់ដោយ $f(x)=@F$ ។"), F=F), "ក. រកដែនកំណត់នៃ $f$ ។", K(r"ខ. គណនា $\lim_{x\to @a}f(x)$ ។", a=at), K(r"គ. គណនា $\lim_{x\to @b^{-}}f(x)$ និង $\lim_{x\to @b^{+}}f(x)$ ។", b=bt), r"ឃ. គណនា $\lim_{x\to\pm\infty}f(x)$ រួចទាញរកអាស៊ីមតូតនៃក្រាប ។"])
    l = [K(r"ក. ភាគបែង $@D=@F$ ។ ដូចនេះ $\boxed{D=\mathbb{R}\setminus\{@s\}}$ ។", D=T(D), F=P(x - a) + P(x - b), s=",".join(sorted([at, bt], key=lambda s_: int(s_)))),
         K(r"ខ. ចំពោះ $x\in D$ យើងសម្រួល $f(x)=@G$ ។ ត្រង់ $x=@a$ លីមីតមានរាង $\frac{0}{0}$ ៖ $$\lim_{x\to @a}f(x)=\lim_{x\to @a}@G=@v$$", G=fr(n1, x - b), a=at, v=T(v)),
         K(r"គ. កាលណា $x\to @b$ ភាគយក $@n$ ខិតជិត $@nb$ ហើយភាគបែង $@d$ ខិតជិត $0$ ។ $$\lim_{x\to @b^{-}}f(x)=@l,\quad\lim_{x\to @b^{+}}f(x)=@r$$", b=bt, n=T(n1), nb=T(nb), d=T(x - b), l=V(-vr), r=V(vr)),
         K(r"ឃ. $$\lim_{x\to\pm\infty}f(x)=\lim_{x\to\pm\infty}@G=@p$$", G=fr(n1, x - b), p=p),
         K(r"ដូចនេះ បន្ទាត់ $\boxed{x=@b}$ ជាអាស៊ីមតូតឈរ បន្ទាត់ $\boxed{y=@p}$ ជាអាស៊ីមតូតដេក ។ ត្រង់ $x=@a$ លីមីតមានតម្លៃកំណត់ ដូច្នេះបន្ទាត់ $x=@a$ មិនមែនជាអាស៊ីមតូតទេ ។", b=bt, p=p, a=at)]
    return Atom("", "", l, None, [ck(f, a, v), ck(f, b, vr, "+"), ck(f, b, -vr, "-"), ck(f, oo, p), ck(f, -oo, p)], "study_removable_point_and_asymptote", "bacii", q=q, plain=True, ans=K(r"x=@b,\ y=@p", b=bt, p=p))
def s_sqrt():
    k = ch(1, 2, 3); c = ch(1, 2, 3, 4, 5, 6, 8); b = ch(0, 2, -2, 4, -4) * k
    S = sqrt(k**2 * x**2 + b * x + c + Q(b, 2 * k)**2); w = Q(b, 2 * k); inner = expand(k**2 * x**2 + b * x + c + w**2); f = S; F = T(S); y1 = k * x + w; y2 = -k * x - w
    q = "\n".join([K(r"គេឱ្យអនុគមន៍ $f(x)=@F$ មានក្រាប $(C)$ ។", F=F), r"១. គណនា $\lim_{x\to+\infty}f(x)$ និង $\lim_{x\to-\infty}f(x)$ ។", K(r"២. គណនា $\lim_{x\to+\infty}\left[f(x)-(@a)\right]$ ។", a=T(y1)), K(r"៣. គណនា $\lim_{x\to-\infty}\left[f(x)-(@a)\right]$ រួចទាញរកអាស៊ីមតូតទ្រេតនៃ $(C)$ ។", a=T(y2))])
    l = [K(r"១. កន្សោមក្រោមឫសខិតជិត $+\infty$ ដូច្នេះ $\boxed{\lim_{x\to\pm\infty}f(x)=+\infty}$ ។"),
         K(r"២. គុណនឹងកន្សោមឆ្លាស់ ៖ $$\lim_{x\to+\infty}\left[@F-(@a)\right]=\lim_{x\to+\infty}\frac{@c}{@F+@a}=0$$", F=F, a=T(y1), c=T(c)),
         K(r"៣. ដូចគ្នានេះដែរ ៖ $$\lim_{x\to-\infty}\left[@F-(@a)\right]=\lim_{x\to-\infty}\frac{@c}{@F+(@a)}=0$$", F=F, a=T(y2), c=T(c)),
         K(r"ដូចនេះ បន្ទាត់ $\boxed{y=@a}$ ជាអាស៊ីមតូតទ្រេតត្រង់ $+\infty$ និងបន្ទាត់ $\boxed{y=@b}$ ជាអាស៊ីមតូតទ្រេតត្រង់ $-\infty$ ។", a=T(y1), b=T(y2))]
    tik = tikz_graph("sqrt(%s)" % str(inner).replace("**", "^"), -8, 8, -1, 12, r"\addplot[dashed,domain=-8:8] {%s};" % str(y1).replace("**", "^") + "\n" + r"\addplot[dashed,domain=-8:8] {%s};" % str(y2).replace("**", "^") + "\n")
    pf = lambda rid: plot_png(rid, f, -8, 8, -1, 12, asymptotes=[("o", y1), ("o", y2)])
    return Atom("", "", l, None, [ck(f, oo, oo), ck(f, -oo, oo), ck(f - y1, oo, 0), ck(f - y2, -oo, 0), check(f"expand(({inner})-(({y1})**2+({c})))", "0", "square completed")], "study_radical_slant_asymptotes", "bacii", q=q, plain=True, ans=K(r"y=@a,\ y=@b", a=T(y1), b=T(y2)),
                diag=[{"type": "graph", "latex": tik, "image": None, "alt_km": K(r"ក្រាបមានអាស៊ីមតូតទ្រេត $y=@a$ និង $y=@b$ ។", a=T(y1), b=T(y2))}], png=pf)

# ---------- Sequences: textbook slice, Grade 12 Advanced, not seen on BacII papers ----------
SUBQ = "sequence_textbook_not_seen_on_bacii"
n_ = sp.Symbol("n", positive=True)
def Tn(e): return T(e).replace("x", "n")
def seq_q(tex):
    return ch(r"គណនាលីមីតនៃស្វ៊ីត $(u_{n})$ ដែល $u_{n}=" + tex + "$ ។", r"គេឱ្យស្វ៊ីត $u_{n}=" + tex + r"$ ។ គណនា $\lim_{n\to+\infty}u_{n}$ ។", r"រកលីមីតនៃស្វ៊ីតដែលមានតួទូទៅ $u_{n}=" + tex + "$ ។")
def q_rat():
    a = ni(1, 6); b = ni(1, 5); c = ni(-6, 6); d = ni(-6, 6); e = ni(-4, 7); N = a * x**2 + c * x + e; D = b * x**2 + d * x + ni(1, 5); v = Q(a, b); tex = fr(Tn(N), Tn(D))
    l = [r"ដាក់ $n^{2}$ ជាកត្តារួមទាំងភាគយក និងភាគបែង ។ ដោយ $\frac{1}{n}\to0$ យើងបាន ៖", r"$$\lim_{n\to+\infty}u_{n}=\lim_{n\to+\infty}" + tex + "=" + fr(a, b) + (("=" + T(v)) if v.q != b else "") + "$$", r"ដូចនេះ $\boxed{\lim_{n\to+\infty}u_{n}=" + T(v) + "}$ ។"]
    return Atom("", "", l, None, [ck(N / D, oo, v, note="sequence, n written as x")], SUBQ, "easy", q=seq_q(tex), plain=True, ans=r"\lim_{n\to+\infty}u_{n}=" + T(v))
def q_conj():
    a = ni(1, 8); b = rng.randint(1, 7); S = sqrt(x**2 + a * x + b); tex = Tn(S) + "-n"; v = Q(a, 2)
    l = [K(r"គុណនឹងកន្សោមឆ្លាស់ $@S+n$ ៖", S=Tn(S)), "$$u_{n}=" + fr(Tn(a * x + b), Tn(S) + "+n") + "=" + fr(T(a) + "+" + fr(b, "n"), r"\sqrt{1+" + fr(a, "n") + "+" + fr(b, "n^{2}") + "}+1") + "$$",
         r"ដោយ $\frac{1}{n}\to0$ ភាគយកខិតជិត $" + T(a) + r"$ ហើយភាគបែងខិតជិត $2$ ។", r"ដូចនេះ $\boxed{\lim_{n\to+\infty}u_{n}=" + T(v) + "}$ ។"]
    return Atom("", "", l, None, [ck(S - x, oo, v, note="sequence, n written as x")], SUBQ, "medium", q=seq_q(tex), plain=True, ans=r"\lim_{n\to+\infty}u_{n}=" + T(v))
def q_sum():
    k = ni(1, 5); d = ch(1, 2, 3); 
    tex = fr(r"1+2+3+\cdots+n", T(k) + "n^{2}" + ("+" + T(d) if True else ""))
    v = Q(1, 2 * k); l = [r"យើងដឹងថា $1+2+3+\cdots+n=\frac{n(n+1)}{2}$ ។ ដូច្នេះ", "$$u_{n}=" + fr("n(n+1)", "2(" + T(k) + "n^{2}+" + T(d) + ")") + "=" + fr("n^{2}+n", T(2 * k) + "n^{2}+" + T(2 * d)) + "$$",
                          "ដាក់ $n^{2}$ ជាកត្តារួម រួចយកលីមីត ។", r"ដូចនេះ $\boxed{\lim_{n\to+\infty}u_{n}=" + T(v) + "}$ ។"]
    return Atom("", "", l, None, [ck((x**2 + x) / (2 * (k * x**2 + d)), oo, v, note="sequence, closed form of the sum")], SUBQ, "medium", q=seq_q(tex), plain=True, ans=r"\lim_{n\to+\infty}u_{n}=" + T(v))
def q_tel():
    k = ni(1, 4); tex = r"\frac{1}{1\times2}+\frac{1}{2\times3}+\cdots+\frac{1}{n(n+1)}"
    c = ni(2, 7); tex2 = tex + ("+" + T(c)); v = Integer(1 + c)
    l = [r"ប្រើការបំបែក $\frac{1}{k(k+1)}=\frac{1}{k}-\frac{1}{k+1}$ ។ ផលបូកលុបគ្នាជាជួរ ហើយនៅសល់ ៖", "$$u_{n}=1-" + fr(1, "n+1") + "+" + T(c) + "$$", r"ដោយ $\frac{1}{n+1}\to0$ ។", r"ដូចនេះ $\boxed{\lim_{n\to+\infty}u_{n}=" + T(v) + "}$ ។"]
    return Atom("", "", l, None, [ck(1 - 1 / (x + 1) + c, oo, v, note="sequence, telescoped form")], SUBQ, "hard", q=seq_q(tex2), plain=True, ans=r"\lim_{n\to+\infty}u_{n}=" + T(v))

# ---------- Assembly ----------
SINGLE = [(a_direct_poly, 22), (a_direct_rat, 22), (a_direct_rad, 20), (a_rules_explicit, 22), (a_rules_given, 30), (a_recip_inf, 18),
          (a_fact_qq, 50), (a_diff_squares, 18), (a_fact_cubic, 34), (a_cubes, 16), (a_power_diff, 12), (a_biquad, 14), (a_double_root, 14), (a_inner_frac, 22), (a_binom_h, 10), (a_rate, 16), (a_frac_minus, 24),
          (a_conj_num, 44), (a_conj_den, 32), (a_conj_both, 26), (a_two_roots, 24), (a_root_lin, 20), (a_cbrt, 22), (a_split, 16), (a_sub_sqrt, 18), (a_sub_cbrt, 6),
          (a_poly_inf, 16), (a_rat_inf, 46), (a_prod_inf, 12), (a_sqrt_lin, 26), (a_sqrt_mx, 34), (a_two_sqrt_inf, 14), (a_sqrt_notindet, 10), (a_cbrt_inf, 6), (a_sqrt_zero, 14), (a_rat_minus_lin, 14), (a_root_ratio, 10), (a_sqrt_pm, 12),
          (a_pole_simple, 20), (a_pole_quad, 18), (a_pole_double, 10), (a_abs, 20), (a_sqrt_edge, 12), (a_piece, 20), (a_graph, 30),
          (p_quad_ab, 18), (p_m_value, 14), (p_sqrt_ab, 16), (p_inf_ab, 10), (p_slant_ab, 14), (p_sqrt_inf, 10), (p_piece_exist, 14), (p_discuss, 6),
          (t_squeeze, 12), (t_abs_bound, 8), (t_compare, 6), (t_composite, 12), (t_inf_rules, 8),
          (s_hv, 30), (s_slant, 26), (s_hole, 22), (s_sqrt, 10), (q_rat, 12), (q_conj, 10), (q_sum, 6), (q_tel, 4)]
SCI_POOLS = [a_fact_qq, a_fact_cubic, a_conj_num, a_conj_den, a_conj_both, a_two_roots, a_root_lin, a_cbrt, a_rat_inf, a_sqrt_lin, a_sqrt_mx, a_two_sqrt_inf, a_frac_minus, a_inner_frac, a_sub_sqrt, a_split, a_double_root, a_rat_minus_lin, a_power_diff]
SOC_POOLS = [a_direct_rat, a_direct_rad, a_direct_poly, a_fact_qq, a_diff_squares, a_conj_num, a_conj_den, a_poly_inf, a_rat_inf, a_sqrt_lin, a_cubes]
Q_OPEN = [r"គណនាលីមីតខាងក្រោម ៖ $$@L$$", r"គណនាតម្លៃនៃលីមីត $@L$ ។", r"គណនាលីមីតខាងក្រោម ៖ $$@L$$", r"រកតម្លៃនៃលីមីតខាងក្រោម ៖ $$@L$$", r"គណនាលីមីតនៃអនុគមន៍ខាងក្រោម ៖ $$@L$$",
          r"គេឱ្យអនុគមន៍ $f(x)=@B$ ។ គណនា $@Pf(x)$ ។", r"គណនាលីមីតនៃអនុគមន៍ $f(x)=@B$ កាលណា $x\to @p$ ។", r"គណនាលីមីតនៃ $f(x)=@B$ ត្រង់ $@p$ ។",
          r"សិក្សាលីមីតនៃអនុគមន៍ $f(x)=@B$ ត្រង់ $@p$ ។", r"តើ $@B$ ខិតជិតតម្លៃប៉ុន្មាន កាលណា $x\to @p$ ?", r"ចូរគណនាលីមីតនេះ ៖ $$@L$$", r"គេមានអនុគមន៍ $f(x)=@B$ ។ រក $@Pf(x)$ ។"]
LABELS = [["ក.", "ខ.", "គ.", "ឃ.", "ង."], ["១.", "២.", "៣.", "៤.", "៥."], ["ក.", "ខ.", "គ.", "ឃ.", "ង."], ["ក-", "ខ-", "គ-", "ឃ-", "ង-"]]
HEADS = ["", "", "", "ដំណោះស្រាយ", "ចម្លើយ", "អត្រាកំណែ"]
def lint(t):
    t = t.replace("\\\\", " ")
    for mth in re.finditer(r"\\([a-zA-Z]+)", t):
        if mth.group(1) not in OKCMD:
            raise ValueError("unknown or joined command: " + mth.group(0) + " in " + t[max(0, mth.start() - 40):mth.end() + 20])
OKCMD = set("text qquad cup in aligned frac sqrt lim to infty left right cdot times neq le ge quad boxed begin end cases mathbb setminus Rightarrow Leftrightarrow pm cdots".split())
def finish(prob, sol, ans, checks, sub, diff, grade, atoms, gen=TOPIC):
    def tidy(t):
        t = re.sub(r"\{\(((?:[^(){}]|\{[^{}]*\})*)\)\}", r"{\1}", t)
        t = re.sub(r"\\frac\{-(\d+)\}", r"-\\frac{\1}", t)
        return t.replace("+-", "-").replace("--", "+")
    prob, sol, ans = clean_tex(tidy(prob)), clean_tex(tidy(sol)), clean_tex(tidy(ans))
    for t in (prob, sol, ans):
        lint(t)
    row = make_row(TOPIC, sub, diff, prob, sol, ans, checks, gen, chapter="limit", grade=grade)
    dgs = []
    png_used = False
    for a in atoms:
        for d in a.diag:
            d = dict(d)
            d.pop("image", None)
            dgs.append(d)
            if a.png and not png_used:
                row["_png"] = (a.png, len(dgs) - 1); png_used = True
    row["diagrams"] = dgs
    return row
CNT = {"png": 0}
def unwrap(b):
    for o, c in (("(", ")"), (r"\left(", r"\right)"), (r"\left[", r"\right]")):
        if b.startswith(o) and b.endswith(c):
            inner = b[len(o):-len(c)]
            d = 0
            for chh in inner:
                d += (chh == "(") - (chh == ")")
                if d < 0:
                    return b
            return inner
    return b
def single(a):
    if a.q:
        prob = a.q
    else:
        prob = K(ch(*Q_OPEN), L=a.L, B=unwrap(a.body), P=lim(a.pt), p=a.pt)
    sl = a.sol()
    if len(re.findall(r"[\u1780-\u17FF]", " ".join(sl))) < 16:
        sl.insert(0, ch("យើងគណនាដូចខាងក្រោម ៖", "យើងបានដូចតទៅ ៖", "ការគណនាមានដូចខាងក្រោម ៖"))
    return finish(prob, "\n".join(sl), a.ans, a.checks, a.sub, a.diff, a.grade, [a])
def multi(kind):
    pools = SCI_POOLS if kind == "sci" else SOC_POOLS
    n = ch(3, 3, 3, 4, 2) if kind == "sci" else ch(2, 3, 3, 4)
    n = ch(3, 3, 3, 4, 5) if kind == "sci" else n
    fns = rng.sample(pools, n)
    atoms = []
    for f in fns:
        a = f()
        while a.q: a = f()
        atoms.append(a)
    if kind == "mix":
        pass
    atoms.sort(key=lambda a: {"easy": 0, "medium": 1, "hard": 2}.get(a.diff, 1) + rng.random() * .4)
    return assemble(atoms, ch(r"គណនាលីមីតខាងក្រោម ៖", r"ចូរគណនាលីមីតខាងក្រោម ៖") if kind == "sci" else r"គណនាលីមីតនៃអនុគមន៍ខាងក្រោម ៖", kind)
def assemble(atoms, head, kind):
    lb = ch(*LABELS)[:len(atoms)]
    prob = head + "\n" + "\n".join(l + " " + ("$" + a.L + "$" + ch(" ។", "") if not a.q else a.q) for l, a in zip(lb, atoms))
    h = ch(*HEADS); sol = ([h] if h else [])
    for l, a in zip(lb, atoms):
        sol.append(l + (" " + ch("គណនា ", "") + "$" + a.L + "$" if not a.q else ""))
        sol += a.sol()
    ans = r";\ ".join(a.ans if a.q else a.vt for a in atoms)
    cks = [c for a in atoms for c in a.checks]
    return finish(prob, "\n".join(sol), ans, cks, "exam_multipart_" + kind, "bacii", 12, atoms)
def param_multi():
    """Exam-style item that mixes a parameter part with computed limits."""
    a1 = ch(p_quad_ab, p_sqrt_ab, p_m_value, p_slant_ab, p_sqrt_inf, p_piece_exist)()
    a2 = ch(a_conj_num, a_fact_cubic, a_sqrt_mx, a_rat_inf, a_two_roots)()
    a3 = ch(a_frac_minus, a_cbrt, a_sqrt_lin, a_inner_frac)()
    return assemble([a2, a3, a1], ch("ដោះស្រាយសំណួរខាងក្រោម ៖", "គណនា និងកំណត់តម្លៃដែលគេសួរ ៖"), "with_parameter")

def main():
    for p in glob.glob(os.path.join(ROOT, "diagrams", TOPIC + "-*.png")):
        os.remove(p)
    rows, seen = [], set()
    def add(r):
        k = re.sub(r"\s+", "", "|".join(re.findall(r"\$\$?(.+?)\$\$?", r["problem_km"], flags=re.S)))
        if k in seen:
            return False
        seen.add(k); rows.append(r)
        pj = r.pop("_png", None)
        if pj and CNT["png"] < 280:
            r["diagrams"][pj[1]]["image"] = pj[0](r["id"]); CNT["png"] += 1
        return True
    try:
        import limit_algebraic_hand as HH
        for r in HH.rows():
            for f_ in ("problem_km", "solution_km", "answer_latex"):
                lint(r[f_])
            add(r)
    except ImportError:
        print("no hand rows")
    nh = len(rows); print("hand", nh)
    for fn, want in SINGLE:
        got = tries = 0
        while got < want and tries < want * 25:
            tries += 1
            try:
                a = fn()
            except ZeroDivisionError:
                continue
            if single_ok(a) and add(single(a)):
                got += 1
        if got < want:
            print("short", fn.__name__, got, want)
    for kind, want in (("sci", 150), ("soc", 100)):
        got = 0
        while got < want:
            if add(multi(kind)): got += 1
    got = 0
    while got < 50:
        if add(param_multi()): got += 1
    finish_rows(rows)
    write_jsonl(rows, "limit/algebraic.jsonl")
    print("png", CNT["png"], "rows", len(rows))
def single_ok(a):
    return all("zoo" not in c["lhs"] and "nan" not in c["rhs"] for c in a.checks)
if __name__ == "__main__":
    main()
