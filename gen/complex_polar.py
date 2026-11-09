"""Topic complex/polar: argument, trigonometric form, De Moivre, n-th roots, trig applications.
Exact arithmetic throughout. Writes out/complex/polar.jsonl. Hand rows live in complex_polar_hand.py."""
import sys, os, random, re, glob, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from functools import lru_cache
from cg_core import tidy
R = sp.Rational; SQ = sp.sqrt; PI = sp.pi
TOPIC = "complex_polar"

# ---------- exact helpers ----------
@lru_cache(None)
def cs(t):
    return sp.cos(t * PI), sp.sin(t * PI)
def red(t):
    t = R(t)
    while t > 1: t -= 2
    while t <= -1: t += 2
    return t
def l1(v):
    return sp.latex(v).replace(" ", "")
def tx(v):
    v = sp.expand(v)
    if v.is_Add:
        ts = list(v.args); den = 1
        for u in ts: den = sp.ilcm(den, sp.fraction(u)[1])
        nums = sorted([sp.expand(u * den) for u in ts], key=lambda u: -float(u))
        sign = ""
        if all(float(u) < 0 for u in nums):
            sign = "-"; nums = sorted([-u for u in nums], key=lambda u: -float(u))
        body = ""
        for i, u in enumerate(nums):
            s_ = l1(u); body += ("+" if i and not s_.startswith("-") else "") + s_
        return sign + (body if den == 1 else "\\frac{" + body + "}{" + str(den) + "}")
    return l1(v)
def ib(b):
    b = sp.expand(b)
    if b == 1: return "i"
    if b == -1: return "-i"
    if b.is_Add:
        neg = float(b) < 0; c = -b if neg else b; t = tx(c)
        return ("-" if neg else "") + ("i" + t if t.startswith("\\frac") else "i\\left(" + t + "\\right)")
    neg = b < 0; c = -b if neg else b; p = "-" if neg else ""
    if c.is_Integer: return p + str(c) + "i"
    if c.is_Rational: return p + "\\frac{" + str(c.p) + "}{" + str(c.q) + "}i"
    n, d = sp.fraction(c)
    if d == 1:
        k = n.as_coeff_Mul()
        return p + ("" if k[0] == 1 else str(k[0])) + "i" + l1(k[1])
    return p + "i" + l1(c)
def tz(a, b):
    a = sp.expand(a); b = sp.expand(b)
    if a == 0 and b == 0: return "0"
    if a == 0: return ib(b)
    if b == 0: return tx(a)
    s_ = ib(b)
    return tx(a) + ("" if s_.startswith("-") else "+") + s_
def ta(t):
    t = R(t)
    if t == 0: return "0"
    neg = t < 0; c = abs(t); p, q = c.p, c.q
    num = ("" if p == 1 else str(p)) + "\\pi"
    return ("-" if neg else "") + (num if q == 1 else "\\frac{" + num + "}{" + str(q) + "}")
def arg_in(t):
    return "\\left(" + ta(t) + "\\right)" if t < 0 else ("\\," + ta(t) if R(t).q == 1 and t != 1 and t != 0 else ta(t))
def cx(t):
    return "\\cos 0" if t == 0 else "\\cos" + (arg_in(t) if t < 0 or R(t).q == 1 else ta(t))
def sx(t):
    return "\\sin 0" if t == 0 else "\\sin" + (arg_in(t) if t < 0 or R(t).q == 1 else ta(t))
def rcoef(r):
    if r == 1: return ""
    s_ = tx(r)
    return "\\left(" + s_ + "\\right)" if sp.expand(r).is_Add and not s_.startswith("\\frac") else s_
def tf(r, t):
    if r == 1: return cx(t) + "+i" + sx(t)
    return rcoef(r) + "\\left(" + cx(t) + "+i" + sx(t) + "\\right)"
def py(a, b):
    return f"({a})+I*({b})"
def pyt(r, t):
    return f"({r})*(cos(({t})*pi)+I*sin(({t})*pi))"
def sq(v):
    v = sp.expand(v)
    if v.is_Integer and v >= 0: return f"{v}^{{2}}"
    return "\\left(" + tx(v) + "\\right)^{2}"
def pw(r, n):
    return (f"{r}^{{{n}}}" if r.is_Integer else "\\left(" + tx(r) + "\\right)^{" + str(n) + "}")
def fr(n, d):
    if d == 1: return tx(n)
    if n == 0: return "0"
    return "\\frac{" + tx(n) + "}{" + tx(d) + "}"
def br(v):
    t = tx(v)
    return "\\left(" + t + "\\right)" if (t.startswith("-") or t.startswith("\\frac") or sp.expand(v).is_Add) else t

class Z:
    def __init__(s, r, t):
        s.r = sp.sympify(r); s.t = red(t); c, n = cs(s.t)
        s.a = sp.expand(s.r * c); s.b = sp.expand(s.r * n)
        s.tex = tz(s.a, s.b); s.py = py(s.a, s.b); s.tf = tf(s.r, s.t); s.pyt = pyt(s.r, s.t)
    def __mul__(s, o): return Z(s.r * o.r, s.t + o.t)
    def __truediv__(s, o): return Z(sp.radsimp(s.r / o.r), s.t - o.t)
    def pow(s, n): return Z(s.r ** n, s.t * n)
    def conj(s): return Z(s.r, -s.t)
    def key(s): return (str(s.r), str(s.t))

F6 = [R(1, 6), R(5, 6), R(-1, 6), R(-5, 6)]
F3 = [R(1, 3), R(2, 3), R(-1, 3), R(-2, 3)]
F4 = [R(1, 4), R(3, 4), R(-1, 4), R(-3, 4)]
AX = [R(0), R(1), R(1, 2), R(-1, 2)]
RAD = {6: [2, 2, 4, 4, 6, 8, 10, 1, 2*SQ(3), 2*SQ(2), 4*SQ(3)], 3: [2, 2, 4, 4, 6, 8, 10, 1, 2*SQ(3), 2*SQ(2), 4*SQ(3)],
       4: [SQ(2), SQ(2), 2*SQ(2), 2*SQ(2), 3*SQ(2), 2, 4, 1, SQ(6), 5*SQ(2), 4*SQ(2)]}
def rz(rng, axis=False, small=False):
    fam = rng.choice([6, 3, 4, 4])
    if axis and rng.random() < .15:
        return Z(rng.choice([1, 2, 3, 4, 5, 6]), rng.choice(AX))
    t = rng.choice({6: F6, 3: F3, 4: F4}[fam])
    r = rng.choice(RAD[fam][:6] if small else RAD[fam])
    return Z(r, t)

# ---------- reusable solution fragments ----------
def rsym(nm):
    m_ = re.match(r"^[zZwAB]_?\{?(\d)\}?$", nm)
    return "r_{" + m_.group(1) + "}" if m_ else "r"
def asym(nm):
    m_ = re.match(r"^[zZwAB]_?\{?(\d)\}?$", nm)
    return "\\alpha_{" + m_.group(1) + "}" if m_ else "\\alpha"
def F_mod(nm, z):
    rr = rsym(nm); s2 = sp.expand(z.a**2 + z.b**2)
    out = f"|{nm}|={rr}=\\sqrt{{{sq(z.a)}+{sq(z.b)}}}=\\sqrt{{{tx(z.a**2)}+{tx(z.b**2)}}}"
    if (z.a != 0 and z.b != 0): out += f"=\\sqrt{{{tx(s2)}}}"
    return out + ("" if tx(z.r) == "\\sqrt{" + tx(s2) + "}" else "=" + tx(z.r))
def F_cs(nm, z):
    al = asym(nm); c, n = cs(z.t)
    def one(fn, v, val, tt):
        q = fr(v, z.r); w = tx(val)
        return f"\\{fn}{al}={q}" + ("" if q == w else "=" + w) + "=" + tt
    return one("cos", z.a, c, cx(z.t)), one("sin", z.b, n, sx(z.t))
ALF = lambda nm, z: f"{asym(nm)}={ta(z.t)}+2k\\pi,\\ k\\in\\mathbb{{Z}}"
def write_trig(nm, z, rng, style=None, head=True):
    """Full derivation of the trigonometric form of z from its algebraic form."""
    st = rng.randint(0, 3) if style is None else style
    rr = rsym(nm); al = asym(nm); c1, c2 = F_cs(nm, z); pre = (f"ចំពោះ ${nm}={z.tex}$ ៖\n" if head else "")
    if z.a != 0 and z.b != 0 and st == 1 and z.r != 1:
        f1, f2 = fr(z.a, z.r), fr(z.b, z.r)
        v1, v2 = tx(cs(z.t)[0]), tx(cs(z.t)[1])
        inner = v1 + ("" if v2.startswith("-") else "+") + "i" + v2 if not v2.startswith("-") else v1 + "-i" + v2[1:]
        return (pre + f"$${F_mod(nm, z)}$$\nដាក់ម៉ូឌុលជាកត្តារួម គេបាន ៖\n$${nm}={rcoef(z.r)}\\left({inner}\\right)$$\n"
                f"ដោយ ${v1}={cx(z.t)}$ និង ${v2}={sx(z.t)}$ នោះ $${nm}={z.tf}$$")
    if st == 2:
        return (pre + f"តាង ${nm}={rr}(\\cos{al}+i\\sin{al})$ ។ យើងមាន $${F_mod(nm, z)}$$\nហើយ\n$${c1}$$\n$${c2}$$\n"
                f"នាំឱ្យ ${ALF(nm, z)}$ ។ យក ${al}={ta(z.t)}$ គេបាន $${nm}={z.tf}$$")
    if st == 3:
        return (pre + f"ម៉ូឌុល ៖ $${F_mod(nm, z)}$$\nអាគុយម៉ង់ ៖ $${c1},\\quad {c2}$$\nដូច្នេះ ${ALF(nm, z)}$ ហើយ $${nm}={z.tf}$$")
    return (pre + f"$${F_mod(nm, z)}$$\nតាង ${al}$ ជាអាគុយម៉ង់នៃ ${nm}$ ។ គេបាន\n$$\\begin{{aligned}}{c1.replace('=', '&=', 1)}\\\\{c2.replace('=', '&=', 1)}\\end{{aligned}}$$\n"
            f"$\\Rightarrow {ALF(nm, z)}$ ។ យើងបាន $${nm}={z.tf}$$")
def ck_trig(z):
    return [check(f"Abs({z.py})", z.r, "modulus"), check(z.py, z.pyt, "trigonometric form")]
def ck_arg(z):
    return [check(f"arg({z.py})", f"({z.t})*pi", "argument")] if z.t.q in (1, 2, 3, 4, 6) else []
def F_reduce(tt):
    """Sentence that reduces angle tt*pi to its principal value. Returns (text, reduced)."""
    r_ = red(tt)
    if r_ == tt: return "", r_
    m_ = (tt - r_) / 2
    if r_ == 0: return ("-" if m_ < 0 else "") + f"{abs(m_)}\\times 2\\pi", r_
    tail = ("+" if m_ > 0 else "-") + ("" if abs(m_) == 0 else ta(2 * abs(m_)))
    return ta(r_) + tail, r_
def F_power(nm, z, n, rng, alg=True, tag=None):
    """De Moivre with angle reduction, ends on z^n = value."""
    tt = z.t * n; rn = sp.expand(z.r ** n); q = z.pow(n); lead = rng.choice(["តាមរូបមន្តដឺម័រ គេបាន ៖", "ប្រើរូបមន្តដឺម័រ យើងបាន ៖", "ដោយរូបមន្តដឺម័រ ៖", "អនុវត្តរូបមន្តដឺម័រ ៖"])
    lhs = f"{nm}^{{{n}}}" if tag is None else tag
    s_ = lead + f"\n$${lhs}=\\left[{z.tf}\\right]^{{{n}}}={rcoef_pow(z.r, n)}\\left({cx(tt)}+i{sx(tt)}\\right)$$\n"
    red_txt, r_ = F_reduce(tt)
    bits = []
    if z.r != 1: bits.append(f"${pw(z.r, n)}={tx(rn)}$")
    if red_txt: bits.append(f"${ta(tt)}={red_txt}$")
    if bits: s_ += "ដោយ " + " និង ".join(bits) + " "
    s_ += f"នោះ\n$${lhs}={tf(rn, r_)}"
    if alg:
        c, n_ = cs(r_); inn = tz(c, n_)
        s_ += f"={rcoef(rn)}\\left({inn}\\right)" if rn != 1 and (c != 0 and n_ != 0) else ""
        s_ += f"={q.tex}"
    return s_ + "$$", q
def rcoef_pow(r, n):
    return "" if r == 1 else pw(r, n)
def F_prod_alg(n1, z1, n2, z2):
    a, b, c, d = z1.a, z1.b, z2.a, z2.b
    A = sp.expand(a*c - b*d); B = sp.expand(a*d + b*c)
    t1, t2, t3, t4 = tx(sp.expand(a*c)), ib(sp.expand(a*d)), ib(sp.expand(b*c)), sp.expand(b*d)
    line = "+".join(x_ for x_ in [t1, t2, t3] if x_ != "0").replace("+-", "-")
    last = "" if t4 == 0 else ("-" if t4 > 0 else "+") + tx(abs(t4))
    return (f"$${n1}\\times {n2}=\\left({z1.tex}\\right)\\left({z2.tex}\\right)={line}" + ("" if t4 == 0 else ("+" if t4 > 0 else "-") + tx(abs(t4)) + "i^{2}") + "$$\n"
            f"ដោយ $i^{{2}}=-1$ គេបាន $${n1}\\times {n2}={line}{last}={tz(A, B)}$$"), A, B
def F_quot_alg(n1, z1, n2, z2):
    a, b, c, d = z1.a, z1.b, z2.a, z2.b
    N = sp.expand(c*c + d*d); A = sp.expand(a*c + b*d); B = sp.expand(b*c - a*d)
    u, v = sp.radsimp(A / N), sp.radsimp(B / N)
    w = tz(c, -d)
    return (f"គុណភាគយក និងភាគបែងនឹង ${w}$ ជាចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែង ៖\n"
            f"$$\\frac{{{n1}}}{{{n2}}}=\\frac{{\\left({z1.tex}\\right)\\left({w}\\right)}}{{{sq(c)}+{sq(d)}}}=\\frac{{{tz(A, B)}}}{{{tx(N)}}}={tz(u, v)}$$"), sp.expand(u), sp.expand(v)
def F_ang(op, t1, t2):
    return ta(t1) + op + (arg_in(t2) if t2 < 0 else ta(t2))
def F_prod_trig(n1, z1, n2, z2, rng):
    p = z1 * z2; raw = z1.t + z2.t
    s_ = rng.choice(["តាមរូបមន្តផលគុណ ៖", "គុណម៉ូឌុលនឹងម៉ូឌុល ហើយបូកអាគុយម៉ង់ ៖", "យើងបាន ៖"])
    ang = F_ang("+", z1.t, z2.t)
    s_ += f"\n$${n1}\\times {n2}={rcoef(z1.r)}{'' if z1.r == 1 or z2.r == 1 else chr(92) + 'times '}{rcoef(z2.r)}\\left[\\cos\\left({ang}\\right)+i\\sin\\left({ang}\\right)\\right]$$\n"
    rt, r_ = F_reduce(raw)
    s_ += f"$$={tf(p.r, r_)}$$" if not rt else f"ដោយ ${ta(raw)}={rt}$ នោះ $${n1}\\times {n2}={tf(p.r, r_)}$$"
    return s_, p
def F_quot_trig(n1, z1, n2, z2, rng):
    p = z1 / z2; raw = z1.t - z2.t
    s_ = rng.choice(["តាមរូបមន្តផលចែក ៖", "ចែកម៉ូឌុលនឹងម៉ូឌុល ហើយដកអាគុយម៉ង់ ៖", "យើងបាន ៖"])
    ang = F_ang("-", z1.t, z2.t)
    s_ += f"\n$$\\frac{{{n1}}}{{{n2}}}={fr(z1.r, z2.r)}\\left[\\cos\\left({ang}\\right)+i\\sin\\left({ang}\\right)\\right]$$\n"
    rt, r_ = F_reduce(raw)
    s_ += f"$$={tf(p.r, r_)}$$" if not rt else f"ដោយ ${ta(raw)}={rt}$ នោះ $$\\frac{{{n1}}}{{{n2}}}={tf(p.r, r_)}$$"
    return s_, p
def bx(e): return "$\\boxed{" + e + "}$"

# ---------- subtypes ----------
def D(sub, diff, prob, sol, ans, checks, key, fig=None):
    return dict(sub=sub, diff=diff, prob=prob, sol=sol, ans=ans, checks=checks, key=key, fig=fig)
NAMES = ["z", "z", "z", "w", "Z", "A", "B"]
GIVE = ["គេមានចំនួនកុំផ្លិច", "គេមានចំនួនកុំផ្លិច", "គេឱ្យចំនួនកុំផ្លិច", "គេឱ្យចំនួនកុំផ្លិច", "ឱ្យចំនួនកុំផ្លិច"]
def TRIGQ(rng, obj):
    return rng.choice([f"សរសេរ {obj} ជាទម្រង់ត្រីកោណមាត្រ ។", f"ចូរសរសេរ {obj} ជាទម្រង់ត្រីកោណមាត្រ ។", f"សរសេរចំនួនកុំផ្លិច {obj} ជាទម្រង់ត្រីកោណមាត្រ ។", f"រកទម្រង់ត្រីកោណមាត្រនៃ {obj} ។"])

def s_modarg(rng):
    z = rz(rng, axis=True); nm = rng.choice(NAMES)
    q = rng.choice([f"រកម៉ូឌុល និងអាគុយម៉ង់នៃចំនួនកុំផ្លិច ${nm}={z.tex}$ ។", f"កំណត់ម៉ូឌុល និងអាគុយម៉ង់នៃ ${nm}={z.tex}$ ។",
        f"{rng.choice(GIVE)} ${nm}={z.tex}$ ។ គណនា $|{nm}|$ រួចរកអាគុយម៉ង់នៃ ${nm}$ ។", f"{rng.choice(GIVE)} ${nm}={z.tex}$ ។ រកម៉ូឌុល និងអាគុយម៉ង់របស់វា ។",
        f"គណនាម៉ូឌុល និងកំណត់អាគុយម៉ង់នៃចំនួនកុំផ្លិច ${nm}={z.tex}$ ។"])
    c1, c2 = F_cs(nm, z); al = asym(nm)
    if rng.random() < .5:
        s_ = f"យើងមាន ${nm}={z.tex}$ ។\n$${F_mod(nm, z)}$$\nតាង ${al}$ ជាអាគុយម៉ង់នៃ ${nm}$ ។ គេបាន\n$${c1}$$\n$${c2}$$\n$\\Rightarrow {ALF(nm, z)}$ ។\n"
    else:
        s_ = f"ផ្នែកពិតគឺ ${tx(z.a)}$ និងផ្នែកនិមិត្តគឺ ${tx(z.b)}$ ។ ម៉ូឌុល ៖\n$${F_mod(nm, z)}$$\nអាគុយម៉ង់ ${al}$ ផ្ទៀងផ្ទាត់ ៖\n$${c1},\\quad {c2}$$\nនាំឱ្យ ${ALF(nm, z)}$ ។\n"
    s_ += f"ដូចនេះ ម៉ូឌុលនៃចំនួនកុំផ្លិច ${nm}$ គឺ {bx('|'+nm+'|='+tx(z.r))} ហើយអាគុយម៉ង់គឺ {bx(ALF(nm, z))} ។"
    return D("modulus_argument", "easy", q, s_, f"|{nm}|={tx(z.r)},\\ {ALF(nm, z)}", ck_trig(z) + ck_arg(z), z.key())

def s_trig_one(rng):
    z = rz(rng, axis=True); nm = rng.choice(NAMES); kind = rng.choice(["plain", "plain", "inv", "sq", "prod"])
    if kind == "plain":
        q = rng.choice([f"{rng.choice(GIVE)} ${nm}={z.tex}$ ។ " + TRIGQ(rng, f"${nm}$"), TRIGQ(rng, f"${nm}={z.tex}$")])
        s_ = write_trig(nm, z, rng, head=False)
        chk = ck_trig(z) + ck_arg(z); key = z.key(); diff = "easy"
    elif kind == "inv":
        w = rz(rng, small=True); k = rng.choice([2, 4, 6, 8]); z = Z(sp.radsimp(k / w.r), -w.t)
        ex = f"\\frac{{{k}}}{{{w.tex}}}"
        q = f"{rng.choice(GIVE)} ${nm}={ex}$ ។ សរសេរ ${nm}$ ជាទម្រង់ពីជគណិត រួចជាទម្រង់ត្រីកោណមាត្រ ។"
        N = sp.expand(w.a**2 + w.b**2)
        s_ = (f"គុណភាគយក និងភាគបែងនឹង ${tz(w.a, -w.b)}$ ៖\n$${nm}=\\frac{{{k}\\left({tz(w.a, -w.b)}\\right)}}{{{sq(w.a)}+{sq(w.b)}}}=\\frac{{{k}\\left({tz(w.a, -w.b)}\\right)}}{{{tx(N)}}}={z.tex}$$\n" + write_trig(nm, z, rng, head=False))
        chk = [check(f"{k}/({w.py})", z.py, "algebraic form")] + ck_trig(z); key = ("inv", k, w.key()); diff = "medium"
    elif kind == "sq":
        w = rz(rng, small=True); z = w.pow(2)
        if z.b == 0 or z.a == 0: return None
        q = f"{rng.choice(GIVE)} ${nm}=\\left({w.tex}\\right)^{{2}}$ ។ ពន្លាត ${nm}$ រួច" + TRIGQ(rng, f"${nm}$")
        s_ = (f"ពន្លាតការេ ដោយប្រើ $i^{{2}}=-1$ ៖\n$${nm}={sq(w.a)}+2\\times {br(w.a)}\\times {br(w.b)}\\,i-{sq(w.b)}={z.tex}$$\n" + write_trig(nm, z, rng, head=False))
        chk = [check(f"expand(({w.py})**2)", z.py, "expansion")] + ck_trig(z); key = ("sq", w.key()); diff = "medium"
    else:
        u = rz(rng, small=True); v = rz(rng, small=True); z = u * v
        if z.t.q == 12 or sp.expand(u.a*v.b + u.b*v.a) == 0 or sp.expand(u.a*v.a - u.b*v.b) == 0: return None
        q = f"{rng.choice(GIVE)} ${nm}=\\left({u.tex}\\right)\\left({v.tex}\\right)$ ។ គណនា ${nm}$ ជាទម្រង់ពីជគណិត រួច" + TRIGQ(rng, f"${nm}$")
        t_, A, B = F_prod_alg("u", u, "v", v)
        s_ = f"តាង $u={u.tex}$ និង $v={v.tex}$ ។\n" + t_ + f"\nដូច្នេះ ${nm}={z.tex}$ ។\n" + write_trig(nm, z, rng, head=False)
        chk = [check(f"expand(({u.py})*({v.py}))", z.py, "product")] + ck_trig(z); key = ("prod", u.key(), v.key()); diff = "medium"
    s_ += f"\nដូចនេះ ទម្រង់ត្រីកោណមាត្រនៃ ${nm}$ គឺ {bx(nm+'='+z.tf)} ។"
    return D("trigonometric_form", diff, q, s_, f"{nm}={z.tf}", chk, key)

def s_trig_several(rng):
    k = rng.choice([2, 3, 3]); zs = []
    while len(zs) < k:
        c = rz(rng, axis=True)
        if all(c.key() != o.key() for o in zs): zs.append(c)
    if not any(c.b == 0 or c.a == 0 for c in zs) and rng.random() < .5:
        zs[-1] = Z(rng.choice([2, 3, 5]), rng.choice(AX))
    nms = [f"z_{{{i+1}}}" for i in range(k)]
    lst = " , ".join(f"${n}={c.tex}$" for n, c in zip(nms[:-1], zs[:-1])) + f" និង ${nms[-1]}={zs[-1].tex}$"
    q = rng.choice(["សរសេរចំនួនកុំផ្លិចខាងក្រោមជាទម្រង់ត្រីកោណមាត្រ ៖ ", "គេមានចំនួនកុំផ្លិច ", "គេឱ្យ "]) 
    q = q + lst + (" ។" if q.startswith("សរសេរ") else " ។ សរសេរចំនួនទាំងនេះជាទម្រង់ត្រីកោណមាត្រ ។")
    st = rng.randint(0, 3); parts = []; chk = []
    for n, c in zip(nms, zs):
        if c.b == 0 or c.a == 0:
            word = {R(0): "ជាចំនួនពិតវិជ្ជមាន", R(1): "ជាចំនួនពិតអវិជ្ជមាន", R(1, 2): "ជាចំនួននិមិត្ត ហើយផ្នែកនិមិត្តវិជ្ជមាន", R(-1, 2): "ជាចំនួននិមិត្ត ហើយផ្នែកនិមិត្តអវិជ្ជមាន"}[c.t]
            parts.append(f"ចំពោះ ${n}={c.tex}$ ៖ ចំនួននេះ{word} ដូច្នេះ $|{n}|={tx(c.r)}$ ហើយគេយកអាគុយម៉ង់ ${ta(c.t)}$ ។ គេបាន $${n}={c.tf}$$")
        else:
            parts.append(write_trig(n, c, rng, style=st))
        chk += ck_trig(c)
    conc = " , ".join(f"${n}={c.tf}$" for n, c in zip(nms, zs))
    return D("trigonometric_form_several", "medium", q, "\n".join(parts) + f"\nដូចនេះ {conc} ។", ",\\ ".join(f"{n}={c.tf}" for n, c in zip(nms, zs)), chk, tuple(sorted(c.key() for c in zs)))

def s_trig_to_alg(rng):
    z = Z(rng.choice([1, 2, 3, 4, 5, 6, 8, 10, SQ(2), 2*SQ(2), SQ(3), 2*SQ(3), R(1, 2)]), rng.choice(F3 + F4 + F6 + AX)); nm = rng.choice(NAMES); c, n = cs(z.t)
    k = rng.randint(0, 2)
    if k == 0:
        q = f"{rng.choice(GIVE)} ${nm}={z.tf}$ ។ សរសេរ ${nm}$ ជាទម្រង់ពីជគណិត ។"
    elif k == 1:
        q = f"ចំនួនកុំផ្លិច ${nm}$ មានម៉ូឌុល ${tx(z.r)}$ និងអាគុយម៉ង់ ${ta(z.t)}$ ។ សរសេរ ${nm}$ ជាទម្រង់ពីជគណិត ។"
    else:
        q = f"រកផ្នែកពិត និងផ្នែកនិមិត្តនៃចំនួនកុំផ្លិច ${nm}={z.tf}$ ។"
    s_ = (f"យើងមាន ${nm}={z.tf}$ ។\n" if k != 1 else f"យើងបាន ${nm}={z.tf}$ ។\n")
    s_ += f"ដោយ ${cx(z.t)}={tx(c)}$ និង ${sx(z.t)}={tx(n)}$ នោះ\n$${nm}={rcoef(z.r)}\\left({tz(c, n)}\\right)={z.tex}$$\n"
    if k == 2: s_ += f"ដូចនេះ ផ្នែកពិតគឺ {bx(tx(z.a))} និងផ្នែកនិមិត្តគឺ {bx(tx(z.b))} ។"
    else: s_ += f"ដូចនេះ ទម្រង់ពីជគណិតគឺ {bx(nm+'='+z.tex)} ។"
    return D("trigonometric_to_algebraic", "easy", q, s_, f"{nm}={z.tex}", [check(z.pyt, z.py, "algebraic form")], z.key())

ACUTE = [R(1, 12), R(1, 6), R(1, 4), R(1, 3), R(5, 12), R(2, 3), R(3, 4), R(5, 6), R(7, 12)]
def s_false_trig(rng):
    r = rng.choice([1, 2, 3, 4, 5, SQ(2), SQ(3), 2*SQ(2)]); th = rng.choice(ACUTE[:5] + ACUTE[5:]); kind = rng.randint(0, 4); nm = rng.choice(NAMES); rc = rcoef(r); T = ta(th)
    nr = "-" + rc if r != 1 else "-"
    if kind == 0:
        ex = f"{rc}\\left(\\cos{T}-i\\sin{T}\\right)"; t2 = -th; pyx = f"({r})*(cos(({th})*pi)-I*sin(({th})*pi))"
        why = f"ដោយ $\\cos(-\\alpha)=\\cos\\alpha$ និង $\\sin(-\\alpha)=-\\sin\\alpha$ យើងសរសេរបាន ៖"
    elif kind == 1:
        ex = f"{nr}\\left(\\cos{T}+i\\sin{T}\\right)"; t2 = th - 1; pyx = f"-({r})*(cos(({th})*pi)+I*sin(({th})*pi))"
        why = f"មេគុណខាងមុខអវិជ្ជមាន ដូច្នេះត្រូវប្រើ $\\cos(\\alpha-\\pi)=-\\cos\\alpha$ និង $\\sin(\\alpha-\\pi)=-\\sin\\alpha$ ៖"
    elif kind == 2:
        ex = f"{rc}\\left(\\sin{T}+i\\cos{T}\\right)"; t2 = R(1, 2) - th; pyx = f"({r})*(sin(({th})*pi)+I*cos(({th})*pi))"
        why = f"ស៊ីនុសនៅមុខ ដូច្នេះប្រើមុំបំពេញ $\\sin\\alpha=\\cos\\left(\\frac{{\\pi}}{{2}}-\\alpha\\right)$ និង $\\cos\\alpha=\\sin\\left(\\frac{{\\pi}}{{2}}-\\alpha\\right)$ ៖"
    elif kind == 3:
        ex = f"{rc}\\left(\\sin{T}-i\\cos{T}\\right)"; t2 = th - R(1, 2); pyx = f"({r})*(sin(({th})*pi)-I*cos(({th})*pi))"
        why = f"យើងប្រើ $\\sin\\alpha=\\cos\\left(\\alpha-\\frac{{\\pi}}{{2}}\\right)$ និង $-\\cos\\alpha=\\sin\\left(\\alpha-\\frac{{\\pi}}{{2}}\\right)$ ៖"
    else:
        ex = f"{nr}\\left(\\cos{T}-i\\sin{T}\\right)"; t2 = 1 - th; pyx = f"-({r})*(cos(({th})*pi)-I*sin(({th})*pi))"
        why = f"ពន្លាតសញ្ញាដក គេបាន ${nm}={rc}\\left(-\\cos{T}+i\\sin{T}\\right)$ ។ ដោយ $\\cos(\\pi-\\alpha)=-\\cos\\alpha$ និង $\\sin(\\pi-\\alpha)=\\sin\\alpha$ ៖"
    z = Z(r, t2); rawt = t2
    q = rng.choice([f"{rng.choice(GIVE)} ${nm}={ex}$ ។ " + TRIGQ(rng, f"${nm}$"), f"ចំនួន ${nm}={ex}$ មិនទាន់ជាទម្រង់ត្រីកោណមាត្រទេ ។ សរសេរវាឱ្យត្រូវជាទម្រង់ត្រីកោណមាត្រ ។", f"រកម៉ូឌុល និងអាគុយម៉ង់នៃ ${nm}={ex}$ ។"])
    s_ = f"ទម្រង់ត្រីកោណមាត្រត្រូវមានរាង $r(\\cos\\alpha+i\\sin\\alpha)$ ដែល $r>0$ ។ {why}\n$${nm}={tf(r, rawt)}$$\n"
    s_ += f"ដូចនេះ {bx(nm+'='+z.tf)} មានម៉ូឌុល ${tx(r)}$ និងអាគុយម៉ង់ ${ta(z.t)}$ ។"
    return D("false_trigonometric_form", "medium", q, s_, f"{nm}={z.tf}", [check(pyx, z.pyt, "rewritten form"), check(f"Abs({pyx})", r, "modulus")], (str(r), str(th), kind))

def s_half(rng):
    al = rng.choice([R(1, 6), R(1, 3), R(1, 2), R(2, 3), R(5, 6)]); kind = rng.randint(0, 2); nm = rng.choice(["z", "w", "Z"]); T = ta(al); h = al / 2; H_ = ta(h)
    if kind == 0:
        ex = f"1+\\cos{T}+i\\sin{T}"; pyx = f"1+cos(({al})*pi)+I*sin(({al})*pi)"; r = sp.expand(2 * cs(h)[0]); t2 = h
        s_ = (f"យើងប្រើរូបមន្ត $1+\\cos\\alpha=2\\cos^{{2}}\\frac{{\\alpha}}{{2}}$ និង $\\sin\\alpha=2\\sin\\frac{{\\alpha}}{{2}}\\cos\\frac{{\\alpha}}{{2}}$ ៖\n"
              f"$${nm}=2\\cos^{{2}}{H_}+2i\\sin{H_}\\cos{H_}=2\\cos{H_}\\left(\\cos{H_}+i\\sin{H_}\\right)$$\nដោយ $2\\cos{H_}={tx(r)}>0$ នេះជាទម្រង់ត្រីកោណមាត្រហើយ ។\n")
    elif kind == 1:
        ex = f"1-\\cos{T}+i\\sin{T}"; pyx = f"1-cos(({al})*pi)+I*sin(({al})*pi)"; r = sp.expand(2 * cs(h)[1]); t2 = R(1, 2) - h
        s_ = (f"យើងប្រើរូបមន្ត $1-\\cos\\alpha=2\\sin^{{2}}\\frac{{\\alpha}}{{2}}$ និង $\\sin\\alpha=2\\sin\\frac{{\\alpha}}{{2}}\\cos\\frac{{\\alpha}}{{2}}$ ៖\n"
              f"$${nm}=2\\sin^{{2}}{H_}+2i\\sin{H_}\\cos{H_}=2\\sin{H_}\\left(\\sin{H_}+i\\cos{H_}\\right)$$\nក្នុងវង់ក្រចក ស៊ីនុសនៅមុខ ដូច្នេះប្ដូរទៅមុំបំពេញ ${ta(R(1,2))}-{H_}={ta(t2)}$ ៖\n$${nm}=2\\sin{H_}\\left({cx(t2)}+i{sx(t2)}\\right)$$\nដោយ $2\\sin{H_}={tx(r)}>0$ នោះនេះជាទម្រង់ត្រីកោណមាត្រ ។\n")
    else:
        al = rng.choice([R(1, 6), R(1, 4), R(1, 3), R(-1, 6), R(-1, 4), R(-1, 3), R(1, 12), R(5, 12)]); ex = f"1+i\\tan{ta(al) if al > 0 else arg_in(al)}"; T = ta(al); c = cs(al)[0]
        pyx = f"1+I*tan(({al})*pi)"; r = sp.radsimp(1 / c); t2 = al; ta_ = "\\tan" + (T if al > 0 else arg_in(al))
        s_ = (f"ដោយ ${ta_}=\\frac{{{sx(al)}}}{{{cx(al)}}}$ យើងដាក់ភាគបែងរួម ៖\n$${nm}=1+i\\frac{{{sx(al)}}}{{{cx(al)}}}=\\frac{{1}}{{{cx(al)}}}\\left({cx(al)}+i{sx(al)}\\right)$$\nដោយ ${cx(al)}={tx(c)}>0$ យើងបាន $\\frac{{1}}{{{cx(al)}}}={tx(r)}$ ជាម៉ូឌុល ។\n")
    z = Z(r, t2)
    q = rng.choice([f"{rng.choice(GIVE)} ${nm}={ex}$ ។ " + TRIGQ(rng, f"${nm}$"), f"សរសេរ ${nm}={ex}$ ជាទម្រង់ត្រីកោណមាត្រ រួចទាញរកម៉ូឌុល និងអាគុយម៉ង់របស់វា ។"])
    s_ += f"ដូចនេះ {bx(nm+'='+z.tf)} មានម៉ូឌុល ${tx(z.r)}$ និងអាគុយម៉ង់ ${ta(z.t)}$ ។"
    return D("half_angle_trigonometric_form", "hard", q, s_, f"{nm}={z.tf}", [check(pyx, z.pyt, "trigonometric form")], (str(al), kind))

def s_props(rng):
    z = rz(rng, small=True); nm = "z"
    ops = rng.sample(["conj", "neg", "inv", "iz", "sq", "zz", "cube"], rng.choice([3, 4]))
    names = {"conj": "\\overline{z}", "neg": "-z", "inv": "\\frac{1}{z}", "iz": "iz", "sq": "z^{2}", "zz": "\\frac{z}{\\overline{z}}", "cube": "z^{3}"}
    res = {"conj": z.conj(), "neg": Z(z.r, z.t + 1), "inv": Z(sp.radsimp(1 / z.r), -z.t), "iz": Z(z.r, z.t + R(1, 2)), "sq": z.pow(2), "zz": Z(1, 2 * z.t), "cube": z.pow(3)}
    why = {"conj": f"ចំនួនកុំផ្លិចឆ្លាស់មានម៉ូឌុលដូចគ្នា និងអាគុយម៉ង់ផ្ទុយគ្នា ៖ $\\overline{{z}}={tf(z.r, -z.t)}$",
           "neg": f"$-1=\\cos\\pi+i\\sin\\pi$ ដូច្នេះ $-z$ មានម៉ូឌុល ${tx(z.r)}$ ហើយអាគុយម៉ង់ ${ta(z.t)}+\\pi$",
           "inv": f"$\\frac{{1}}{{z}}$ មានម៉ូឌុល $\\frac{{1}}{{{tx(z.r)}}}$ និងអាគុយម៉ង់ $-\\left({ta(z.t)}\\right)$",
           "iz": f"$i=\\cos\\frac{{\\pi}}{{2}}+i\\sin\\frac{{\\pi}}{{2}}$ ដូច្នេះការគុណនឹង $i$ បូកអាគុយម៉ង់នឹង $\\frac{{\\pi}}{{2}}$",
           "sq": f"តាមរូបមន្តដឺម័រ ម៉ូឌុលគឺ ${pw(z.r, 2)}$ ហើយអាគុយម៉ង់គឺ $2\\times {br_ang(z.t)}$",
           "zz": f"ម៉ូឌុលនៃផលចែកគឺ $\\frac{{{tx(z.r)}}}{{{tx(z.r)}}}=1$ ហើយអាគុយម៉ង់គឺ ${br_ang(z.t)}-{br_ang(-z.t)}$",
           "cube": f"តាមរូបមន្តដឺម័រ ម៉ូឌុលគឺ ${pw(z.r, 3)}$ ហើយអាគុយម៉ង់គឺ $3\\times {br_ang(z.t)}$"}
    pyx = {"conj": f"conjugate({z.py})", "neg": f"-({z.py})", "inv": f"1/({z.py})", "iz": f"I*({z.py})", "sq": f"expand(({z.py})**2)", "zz": f"({z.py})/conjugate({z.py})", "cube": f"expand(({z.py})**3)"}
    q = rng.choice([f"គេឱ្យ $z={z.tex}$ ។ សរសេរ $z$ ជាទម្រង់ត្រីកោណមាត្រ រួចទាញរកម៉ូឌុល និងអាគុយម៉ង់នៃ ", f"គេមានចំនួនកុំផ្លិច $z={z.tex}$ ។ រកម៉ូឌុល និងអាគុយម៉ង់នៃ $z$ រួចកំណត់ម៉ូឌុល និងអាគុយម៉ង់នៃ "])
    q += " , ".join(f"${names[o]}$" for o in ops[:-1]) + f" និង ${names[ops[-1]]}$ ។"
    s_ = write_trig("z", z, rng, head=False) + "\nពីទម្រង់នេះ យើងទាញរកបានដោយមិនចាំបាច់គណនាឡើងវិញ ៖\n"
    chk = ck_trig(z); ans = []
    for o in ops:
        w = res[o]; s_ += f"• ${names[o]}$ ៖ {why[o]} ។ គេបាន $|{names[o]}|={tx(w.r)}$ ហើយអាគុយម៉ង់គឺ ${ta(w.t)}$ ។\n".replace("|\\frac", "\\left|\\frac").replace("}|=", "}\\right|=") if o in ("inv", "zz") else f"• ${names[o]}$ ៖ {why[o]} ។ គេបាន $\\left|{names[o]}\\right|={tx(w.r)}$ ហើយអាគុយម៉ង់គឺ ${ta(w.t)}$ ។\n"
        chk.append(check(pyx[o], w.pyt, names[o].replace("\\", ""))); ans.append(f"{names[o]}={w.tf}")
    s_ += "ដូចនេះ " + " , ".join("$\\boxed{" + a + "}$" for a in ans) + " ។"
    return D("argument_properties", "medium", q, s_, ",\\ ".join(ans), chk, (z.key(), tuple(sorted(ops))))
def br_ang(t):
    return "\\left(" + ta(t) + "\\right)" if t < 0 else ta(t)

def s_prodquot_trig(rng):
    z1 = Z(rng.choice([2, 3, 4, 5, 6, SQ(2), 2*SQ(2), SQ(3), 2*SQ(3)]), rng.choice(F3 + F4 + F6 + [R(1, 12), R(5, 12)]))
    z2 = Z(rng.choice([1, 2, 3, 4, SQ(2), SQ(3), SQ(6)]), rng.choice(F3 + F4 + F6 + [R(1, 12), R(-5, 12)]))
    if z1.t == z2.t: return None
    n1, n2 = rng.choice([("z_{1}", "z_{2}"), ("z_{1}", "z_{2}"), ("A", "B"), ("u", "v")])
    want = rng.choice(["both", "both", "prod", "quot"])
    tgt = {"both": f"${n1}\\times {n2}$ និង $\\frac{{{n1}}}{{{n2}}}$", "prod": f"${n1}\\times {n2}$", "quot": f"$\\frac{{{n1}}}{{{n2}}}$"}[want]
    q = f"{rng.choice(GIVE)} ${n1}={z1.tf}$ និង ${n2}={z2.tf}$ ។ " + rng.choice([f"គណនា {tgt} ជាទម្រង់ត្រីកោណមាត្រ រួចសរសេរលទ្ធផលជាទម្រង់ពីជគណិត ។", f"សរសេរ {tgt} ជាទម្រង់ត្រីកោណមាត្រ រួចជាទម្រង់ពីជគណិត ។"])
    s_ = ""; chk = []; ans = []
    if want in ("both", "prod"):
        t_, p = F_prod_trig(n1, z1, n2, z2, rng); c, n = cs(p.t)
        s_ += t_ + f"\nដោយ ${cx(p.t)}={tx(c)}$ និង ${sx(p.t)}={tx(n)}$ យើងបាន ${n1}\\times {n2}={p.tex}$ ។\n"
        chk.append(check(f"({z1.pyt})*({z2.pyt})", p.py, "product")); ans.append(f"{n1}\\times {n2}={p.tf}={p.tex}")
    if want in ("both", "quot"):
        t_, p = F_quot_trig(n1, z1, n2, z2, rng); c, n = cs(p.t)
        s_ += t_ + f"\nដោយ ${cx(p.t)}={tx(c)}$ និង ${sx(p.t)}={tx(n)}$ យើងបាន $\\frac{{{n1}}}{{{n2}}}={p.tex}$ ។\n"
        chk.append(check(f"({z1.pyt})/({z2.pyt})", p.py, "quotient")); ans.append(f"\\frac{{{n1}}}{{{n2}}}={p.tf}={p.tex}")
    s_ += "ដូចនេះ " + " និង ".join("$\\boxed{" + a + "}$" for a in ans) + " ។"
    return D("product_quotient_trigonometric", "medium", q, s_, ",\\ ".join(ans), chk, (z1.key(), z2.key(), want))

def pair(rng, small=True, need12=False):
    for _ in range(60):
        a, b = rz(rng, small=small), rz(rng, small=small)
        if a.t != b.t and a.t != -b.t and (not need12 or (a.t + b.t).q == 12 or (a.t - b.t).q == 12): return a, b
    return None

def s_alg_prod(rng):
    z1, z2 = pair(rng); n1, n2 = "z_{1}", "z_{2}"; st = rng.randint(0, 3)
    q = f"{rng.choice(GIVE)} ${n1}={z1.tex}$ និង ${n2}={z2.tex}$ ។ សរសេរ ${n1}$ , ${n2}$ រួច ${n1}\\times {n2}$ និង $\\frac{{{n1}}}{{{n2}}}$ ជាទម្រង់ត្រីកោណមាត្រ ។"
    s_ = write_trig(n1, z1, rng, st) + "\n" + write_trig(n2, z2, rng, st) + "\n"
    t1, p = F_prod_trig(n1, z1, n2, z2, rng); t2, d = F_quot_trig(n1, z1, n2, z2, rng)
    s_ += t1 + "\n" + t2 + f"\nដូចនេះ {bx(n1+chr(92)+'times '+n2+'='+p.tf)} និង {bx(chr(92)+'frac{'+n1+'}{'+n2+'}='+d.tf)} ។"
    chk = ck_trig(z1) + ck_trig(z2) + [check(f"({z1.py})*({z2.py})", p.pyt, "product"), check(f"({z1.py})/({z2.py})", d.pyt, "quotient")]
    return D("product_quotient_from_algebraic", "medium", q, s_, f"{n1}\\times {n2}={p.tf},\\ \\frac{{{n1}}}{{{n2}}}={d.tf}", chk, tuple(sorted([z1.key(), z2.key()])))

def s_mixed(rng):
    a, b, c = rz(rng, small=True), rz(rng, small=True), rz(rng, small=True)
    e1, e2, e3 = rng.choice([1, 2, 3]), rng.choice([1, 2, 3]), rng.choice([1, 2])
    if len({a.key(), b.key(), c.key()}) < 3 or e1 + e2 + e3 < 4: return None
    P = a.pow(e1) * b.pow(e2) / c.pow(e3)
    pe = lambda e: "" if e == 1 else f"^{{{e}}}"
    ex = f"\\frac{{\\left({a.tex}\\right){pe(e1)}\\left({b.tex}\\right){pe(e2)}}}{{\\left({c.tex}\\right){pe(e3)}}}"
    q = rng.choice([f"គេឱ្យ $Z={ex}$ ។ រកម៉ូឌុល និងអាគុយម៉ង់នៃ $Z$ ។", f"ដោយប្រើទម្រង់ត្រីកោណមាត្រ សរសេរចំនួនកុំផ្លិច $Z={ex}$ ជាទម្រង់ត្រីកោណមាត្រ ។"])
    st = rng.randint(0, 3)
    s_ = f"តាង $u={a.tex}$ , $v={b.tex}$ និង $w={c.tex}$ ។ បើធ្វើគុណដោយផ្ទាល់ នឹងវែងពេក ដូច្នេះសរសេរនីមួយៗជាទម្រង់ត្រីកោណមាត្រសិន ។\n"
    s_ += "\n".join(write_trig(n, v, rng, st) for n, v in (("u", a), ("v", b), ("w", c))) + "\n"
    raw = a.t * e1 + b.t * e2 - c.t * e3
    num = "".join([f"{'' if e1 == 1 else e1}{br_ang(a.t) if e1 != 1 else ta(a.t)}", "+", f"{'' if e2 == 1 else e2}{br_ang(b.t) if e2 != 1 else br_ang(b.t)}", "-", f"{'' if e3 == 1 else e3}{br_ang(c.t)}"])
    s_ += (f"តាមរូបមន្តដឺម័រ និងរូបមន្តផលគុណ ផលចែក ៖\n$$|Z|=\\frac{{{pw(a.r, e1) if e1 > 1 else tx(a.r)}\\times {pw(b.r, e2) if e2 > 1 else tx(b.r)}}}{{{pw(c.r, e3) if e3 > 1 else tx(c.r)}}}={tx(P.r)}$$\n"
           f"អាគុយម៉ង់មួយនៃ $Z$ គឺ $$\\alpha={num}={ta(raw)}$$\n")
    rt, r_ = F_reduce(raw)
    if rt: s_ += f"ដោយ ${ta(raw)}={rt}$ យើងយក $\\alpha={ta(r_)}$ ។\n"
    s_ += f"ដូចនេះ {bx('Z='+P.tf)} មានម៉ូឌុល ${tx(P.r)}$ និងអាគុយម៉ង់ ${ta(P.t)}+2k\\pi,\\ k\\in\\mathbb{{Z}}$ ។"
    pyx = f"({a.pyt})**{e1}*({b.pyt})**{e2}/({c.pyt})**{e3}"
    return D("mixed_product_quotient", "hard", q, s_, f"Z={P.tf}", [check(f"expand(({a.py})**{e1})*expand(({b.py})**{e2})/expand(({c.py})**{e3})", P.py, "value of Z")] + ck_trig(a) + ck_trig(b) + ck_trig(c), (a.key(), b.key(), c.key(), e1, e2, e3))

def s_exact(rng):
    pr = pair(rng, need12=True)
    if not pr: return None
    z1, z2 = pr; n1, n2 = "z_{1}", "z_{2}"
    opts = [o for o in ("q", "p") if (z1.t - z2.t if o == "q" else z1.t + z2.t).q == 12]; o = rng.choice(opts)
    T = red(z1.t - z2.t if o == "q" else z1.t + z2.t)
    if o == "q":
        ta_, u, v = F_quot_alg(n1, z1, n2, z2); t2, P = F_quot_trig(n1, z1, n2, z2, rng); E = f"\\frac{{{n1}}}{{{n2}}}"
    else:
        ta_, u, v = F_prod_alg(n1, z1, n2, z2); t2, P = F_prod_trig(n1, z1, n2, z2, rng); E = f"{n1}\\times {n2}"
    q = (f"{rng.choice(GIVE)} ${n1}={z1.tex}$ និង ${n2}={z2.tex}$ ។\nក. " + rng.choice(["គណនា", "សរសេរ"]) + f" ${E}$ ជាទម្រង់ពីជគណិត ។\nខ. សរសេរ ${n1}$ , ${n2}$ និង ${E}$ ជាទម្រង់ត្រីកោណមាត្រ ។\nគ. ទាញរកតម្លៃពិតប្រាកដនៃ ${cx(T)}$ និង ${sx(T)}$ ។")
    st = rng.randint(0, 3); c, n = cs(T); rr = P.r
    s_ = "ក. " + ta_ + "\nខ. " + write_trig(n1, z1, rng, st) + "\n" + write_trig(n2, z2, rng, st) + "\n" + t2
    s_ += f"\nគ. ទម្រង់ទាំងពីរតំណាងចំនួនតែមួយ ដូច្នេះផ្នែកពិតស្មើគ្នា ហើយផ្នែកនិមិត្តស្មើគ្នា ៖\n$${rcoef(rr)}{cx(T)}={tx(u)}\\quad\\text{{និង}}\\quad {rcoef(rr)}{sx(T)}={tx(v)}$$\n"
    s_ += f"ដូចនេះ {bx(cx(T)+'='+tx(c))} និង {bx(sx(T)+'='+tx(n))} ។"
    chk = ck_trig(z1) + ck_trig(z2) + [check(f"re(expand(({z1.py})*({z2.py})))" if o == "p" else f"simplify(({z1.py})/({z2.py}))", tx_py(u) if o == "p" else py(u, v), "algebraic value"), check(f"cos(({T})*pi)", c, "exact cosine"), check(f"sin(({T})*pi)", n, "exact sine"), check(f"({rr})*cos(({T})*pi)", u, "real parts match")]
    return D("exact_trig_values", "hard", q, s_, f"{cx(T)}={tx(c)},\\ {sx(T)}={tx(n)}", chk, (z1.key(), z2.key(), o))
def tx_py(v): return str(v)

def s_power(rng):
    z = rz(rng, small=True); n = rng.choice([3, 4, 5, 6, 6, 7, 8, 9, 10, 12]); nm = rng.choice(NAMES)
    if z.r ** n > 2 * 10 ** 6: return None
    q = rng.choice([f"គណនា $\\left({z.tex}\\right)^{{{n}}}$ ដោយប្រើទម្រង់ត្រីកោណមាត្រ ។", f"{rng.choice(GIVE)} ${nm}={z.tex}$ ។ គណនា ${nm}^{{{n}}}$ ។", f"{rng.choice(GIVE)} ${nm}={z.tex}$ ។ សរសេរ ${nm}$ ជាទម្រង់ត្រីកោណមាត្រ រួចទាញរកតម្លៃនៃ ${nm}^{{{n}}}$ ។", f"សរសេរ ${nm}={z.tex}$ ជាទម្រង់ត្រីកោណមាត្រ រួចគណនា ${nm}^{{{n}}}$ ជាទម្រង់ពីជគណិត ។"])
    s_ = ("" if f"${nm}=" in q else f"តាង ${nm}={z.tex}$ ។\n") + write_trig(nm, z, rng, head=False) + "\n"; t_, P = F_power(nm, z, n, rng); s_ += t_
    s_ += f"\nដូចនេះ {bx(nm+'^{'+str(n)+'}='+P.tex)} ។"
    return D("de_moivre_power", "medium", q, s_, f"{nm}^{{{n}}}={P.tex}", ck_trig(z) + [check(f"expand(({z.py})**{n})", P.py, "power")], (z.key(), n))

def s_power_trig(rng):
    z = Z(rng.choice([1, 1, 2, 3, SQ(2), SQ(3)]), rng.choice(F3 + F4 + F6 + [R(1, 12), R(-1, 12), R(5, 12), R(7, 12)])); n = rng.choice([2, 3, 4, 5, 6, 8, 9, 10, 12])
    nm = rng.choice(["z", "w", "Z"])
    if z.r == 3 and n > 6: return None
    q = rng.choice([f"គណនា $\\left[{z.tf}\\right]^{{{n}}}$ រួចសរសេរលទ្ធផលជាទម្រង់ពីជគណិត ។", f"{rng.choice(GIVE)} ${nm}={z.tf}$ ។ រក ${nm}^{{{n}}}$ ជាទម្រង់ពីជគណិត ។"])
    if (z.t * n).q == 12: return None
    t_, P = F_power(nm, z, n, rng); s_ = ("" if f"${nm}=" in q else f"តាង ${nm}={z.tf}$ ។\n") + t_ + f"\nដូចនេះ {bx(nm+'^{'+str(n)+'}='+P.tex)} ។"
    return D("de_moivre_given_trigonometric", "easy", q, s_, f"{nm}^{{{n}}}={P.tex}", [check(f"({z.pyt})**{n}", P.py, "power")], (z.key(), n))

def s_power_quot(rng):
    z1, z2 = pair(rng); n = rng.choice([2, 3, 4, 6, 6, 8, 12]); P0 = z1 / z2
    if abs(float(P0.r)) ** n > 10 ** 6 or abs(float(P0.r)) ** n < 1e-4 or (P0.t * n).q == 12: return None
    mode = rng.choice(["q", "q", "p"])
    if mode == "p": P0 = z1 * z2
    if float(P0.r) ** n > 10 ** 7: return None
    E = f"\\frac{{{z1.tex}}}{{{z2.tex}}}" if mode == "q" else f"\\left({z1.tex}\\right)\\left({z2.tex}\\right)"
    q = rng.choice([f"គណនា $Z=\\left({E}\\right)^{{{n}}}$ ដោយប្រើទម្រង់ត្រីកោណមាត្រ ។", f"សរសេរ $Z=\\left({E}\\right)^{{{n}}}$ ជាទម្រង់ពីជគណិត ។"]) if mode == "q" else f"ដោយមិនពន្លាត គណនា $Z=\\left[{E}\\right]^{{{n}}}$ ។"
    st = rng.randint(0, 3); n1, n2 = "u", "v"
    s_ = f"តាង $u={z1.tex}$ និង $v={z2.tex}$ ។\n" + write_trig(n1, z1, rng, st) + "\n" + write_trig(n2, z2, rng, st) + "\n"
    if mode == "q":
        t_, W = F_quot_trig(n1, z1, n2, z2, rng); e = "\\frac{u}{v}"
    else:
        t_, W = F_prod_trig(n1, z1, n2, z2, rng); e = "u\\times v"
    s_ += t_ + "\n"; t2, P = F_power("Z", W, n, rng, tag="Z"); s_ += t2 + f"\nដូចនេះ {bx('Z='+P.tex)} ។"
    pyx = f"simplify(({z1.py})/({z2.py}))**{n}" if mode == "q" else f"expand(({z1.py})*({z2.py}))**{n}"
    return D("power_of_quotient", "hard", q, s_, f"Z={P.tex}", ck_trig(z1) + ck_trig(z2) + [check(f"expand({pyx})", P.py, "value")], (z1.key(), z2.key(), n, mode))

def s_conj_sum(rng):
    z = rz(rng, small=True); n = rng.choice([3, 4, 5, 6, 7, 8, 9, 10]); kind = rng.choice(["+", "-"])
    if z.r ** n > 10 ** 6: return None
    P = z.pow(n); val = 2 * P.a if kind == "+" else 2 * P.b; c, s2 = cs(P.t)
    E = f"z^{{{n}}}{kind}\\left(\\overline{{z}}\\right)^{{{n}}}"
    q = f"{rng.choice(GIVE)} $z={z.tex}$ (ដែល $\\overline{{z}}$ ជាចំនួនកុំផ្លិចឆ្លាស់នៃ $z$) ។ គណនា $S={E}$ ។"
    s_ = write_trig("z", z, rng, head=False) + f"\nដូច្នេះ $\\overline{{z}}={z.conj().tf}$ ។ តាមរូបមន្តដឺម័រ ៖\n"
    tt = n * z.t; rn = sp.expand(z.r ** n)
    s_ += f"$$z^{{{n}}}={rcoef_pow(z.r, n)}\\left({cx(tt)}+i{sx(tt)}\\right),\\quad \\left(\\overline{{z}}\\right)^{{{n}}}={rcoef_pow(z.r, n)}\\left({cx(tt)}-i{sx(tt)}\\right)$$\n"
    res = f"S=2\\times {tx(rn)}{cx(tt)}" if kind == "+" else f"S=2i\\times {tx(rn)}{sx(tt)}"
    s_ += "ពេលបូកចូលគ្នា តួនិមិត្តលុបគ្នា ៖\n" if kind == "+" else "ពេលដកគ្នា តួពិតលុបគ្នា ៖\n"
    s_ += f"$${res}$$\nដោយ ${cx(tt) if kind == '+' else sx(tt)}={tx(cs(tt)[0] if kind == '+' else cs(tt)[1])}$ យើងបាន $S={tx(val) if kind == '+' else ib(val)}$ ។\n"
    fin = tx(val) if kind == "+" else ib(val)
    s_ += f"ដូចនេះ {bx('S='+fin)} ។"
    pv = py(z.a, z.b); pc = py(z.a, -z.b)
    return D("conjugate_power_sum", "hard", q, s_, f"S={fin}", ck_trig(z) + [check(f"expand(({pv})**{n}{kind}({pc})**{n})", str(val) if kind == "+" else f"I*({val})", "S")], (z.key(), n, kind))

def s_year(rng):
    t = rng.choice(F3 + F4 + F6); z = Z(1, t); n = rng.choice([100, 200, 2022, 2023, 2024, 2025, 2026, 1000, 500, 150, 301, 77, 365, 99, 2000, 121]); q0 = t.q * 2
    m_ = n % q0; nm = "z"
    if m_ == 0: m_ = q0
    s0 = red(t * n)
    if t * n == s0: return None
    q = rng.choice([f"{rng.choice(GIVE)} $z={z.tex}$ ។ គណនា $z^{{{n}}}$ ។", f"គេឱ្យ $z={z.tex}$ ។ បង្ហាញថា $|z|=1$ រួចរកតម្លៃនៃ $z^{{{n}}}$ ។"])
    W = z.pow(n); c, s2 = cs(s0)
    s_ = write_trig("z", z, rng, head=False) + f"\nតាមរូបមន្តដឺម័រ $$z^{{{n}}}={cx(t*n)}+i{sx(t*n)}$$\nនិទស្សន្តធំ ដូច្នេះត្រូវដកពហុគុណនៃ $2\\pi$ ចេញពីមុំ ៖ $${ta(t*n)}={F_reduce(t*n)[0]}$$\nអនុគមន៍កូស៊ីនុស និងស៊ីនុសមានខួប $2\\pi$ ដូច្នេះ $$z^{{{n}}}={cx(s0)}+i{sx(s0)}={W.tex}$$\nដូចនេះ {bx('z^{'+str(n)+'}='+W.tex)} ។"
    return D("large_power_periodicity", "hard", q, s_, f"z^{{{n}}}={W.tex}", ck_trig(z) + [check(f"cos(({t})*pi*{n})+I*sin(({t})*pi*{n})", W.py, "power")], (str(t), n))

def s_small_n(rng):
    t = rng.choice([R(1, 6), R(-1, 6), R(1, 4), R(-1, 4), R(1, 3), R(-1, 3), R(5, 6), R(-5, 6), R(3, 4), R(-3, 4), R(2, 3), R(-2, 3)]); fam = {6: 6, 4: 4, 3: 3}[t.q]
    z = Z(rng.choice(RAD[fam][:6]), t); p, q_ = abs(t.p), t.q; kind = rng.choice(["real", "real", "imag", "pos", "neg"]); sg = "" 
    if kind in ("imag", "neg") and p != 1: kind = "real"
    if kind == "imag" and q_ % 2: kind = "pos"
    A = ta(abs(t)); T = ta(t)
    n = {"real": q_, "pos": q_ * (1 if p % 2 == 0 else 2), "imag": q_ // 2 if q_ % 2 == 0 else 0, "neg": q_}[kind]
    want = {"real": "ជាចំនួនពិត", "pos": "ជាចំនួនពិតវិជ្ជមាន", "imag": "ជាចំនួននិមិត្ត", "neg": "ជាចំនួនពិតអវិជ្ជមាន"}[kind]
    q = rng.choice([f"{rng.choice(GIVE)} $z={z.tex}$ ។ រកចំនួនគត់វិជ្ជមាន $n$ តូចបំផុត ដើម្បីឱ្យ $z^{{n}}$ {want} ។", f"គេឱ្យ $z={z.tex}$ ។ កំណត់ចំនួនគត់ធម្មជាតិ $n>0$ តូចបំផុត ដែល $z^{{n}}$ {want} រួចគណនា $z^{{n}}$ នោះ ។"])
    P = z.pow(n); s_ = write_trig("z", z, rng, head=False) + f"\nតាមរូបមន្តដឺម័រ $$z^{{n}}={rcoef_pow_sym(z.r)}\\left(\\cos{NTP(t, p, q_)}+i\\sin{NTP(t, p, q_)}\\right)$$\n"
    nt = ("-" if t < 0 else "") + "\\frac{" + ("" if p == 1 else str(p)) + "n\\pi}{" + str(q_) + "}"
    ntp = "\\left(" + nt + "\\right)" if t < 0 else nt
    if kind == "real":
        s_ += f"$z^{{n}}$ ជាចំនួនពិត លុះត្រាតែផ្នែកនិមិត្តស្មើសូន្យ គឺ $\\sin{ntp}=0$ ។ នាំឱ្យ ${nt}=k\\pi,\\ k\\in\\mathbb{{Z}}$ មានន័យថា ${'' if p == 1 else p}n={'-' if t < 0 else ''}{q_}k$ ។\n"
        s_ += f"ដូច្នេះ $n$ ជាពហុគុណនៃ ${q_}$ ហើយតម្លៃតូចបំផុតគឺ $n={q_}$ ។\n" if p == 1 else f"ដោយ ${p}$ និង ${q_}$ គ្មានតួចែករួមក្រៅពី $1$ នោះ $n$ ជាពហុគុណនៃ ${q_}$ ហើយតម្លៃតូចបំផុតគឺ $n={q_}$ ។\n"
    elif kind == "pos":
        s_ += f"$z^{{n}}$ ជាចំនួនពិតវិជ្ជមាន លុះត្រាតែ $\\cos{ntp}=1$ គឺ ${nt}=2k\\pi,\\ k\\in\\mathbb{{Z}}$ ។ នាំឱ្យ ${'' if p == 1 else p}n={'-' if t < 0 else ''}{2*q_}k$ ។\n"
        s_ += f"តម្លៃវិជ្ជមានតូចបំផុតនៃ $n$ ដែលសមីការនេះមានចំនួនគត់ $k$ គឺ $n={n}$ ។\n"
    elif kind == "imag":
        s_ += f"$z^{{n}}$ ជាចំនួននិមិត្ត លុះត្រាតែផ្នែកពិតស្មើសូន្យ គឺ $\\cos{ntp}=0$ ។ នាំឱ្យ ${nt}=\\frac{{\\pi}}{{2}}+k\\pi,\\ k\\in\\mathbb{{Z}}$ ។ ដូច្នេះ $n={'-' if t < 0 else ''}{q_}\\left(\\frac{{1}}{{2}}+k\\right)$ ។\n"
        s_ += f"យក $k={-1 if t < 0 else 0}$ គេបាន $n={n}$ ជាតម្លៃតូចបំផុត ។\n"
    else:
        s_ += f"$z^{{n}}$ ជាចំនួនពិតអវិជ្ជមាន លុះត្រាតែ $\\cos{ntp}=-1$ គឺ ${nt}=\\pi+2k\\pi,\\ k\\in\\mathbb{{Z}}$ ។ ដូច្នេះ $n={'-' if t < 0 else ''}{q_}(1+2k)$ ។\n"
        s_ += f"យក $k={-1 if t < 0 else 0}$ គេបាន $n={n}$ ជាតម្លៃតូចបំផុត ។\n"
    s_ += f"ពេលនោះ $z^{{{n}}}={P.tex}$ ។\nដូចនេះ {bx('n='+str(n))} ។"
    chk = ck_trig(z) + [check(f"expand(({z.py})**{n})", P.py, "value at n")]
    for m_ in range(1, n):  # no smaller n works
        W = z.pow(m_)
        ok = {"real": W.b != 0, "pos": W.b != 0 or W.a < 0, "imag": W.a != 0, "neg": W.b != 0 or W.a > 0}[kind]
        assert ok, (z.tex, kind, n, m_)
    W = z.pow(n); assert {"real": W.b == 0, "pos": W.b == 0 and W.a > 0, "imag": W.a == 0, "neg": W.b == 0 and W.a < 0}[kind]
    return D("smallest_power_condition", "hard", q, s_, f"n={n}", chk, (z.key(), kind))
def NTP(t, p, q_):
    b = "\\frac{" + ("" if p == 1 else str(p)) + "n\\pi}{" + str(q_) + "}"
    return "\\left(-" + b + "\\right)" if t < 0 else b
def rcoef_pow_sym(r):
    return "" if r == 1 else ("\\left(" + tx(r) + "\\right)^{n}" if not r.is_Integer else f"{r}^{{n}}")

def s_param(rng):
    if rng.random() < .6:
        t = rng.choice([R(1, 6), R(5, 6), R(1, 4), R(3, 4), R(1, 3), R(2, 3)]); z = Z(rng.choice(RAD[t.q][:5]), t); c, s2 = cs(t)
        if z.b.is_Rational or rng.random() < .8:
            pass
        q = f"គេឱ្យចំនួនកុំផ្លិច $z=m+{ib(z.b)}$ ដែល $m$ ជាចំនួនពិត ។ រក $m$ ដើម្បីឱ្យ ${ta(t)}$ ជាអាគុយម៉ង់នៃ $z$ រួចគណនា $|z|$ ។"
        s_ = (f"បើ $z$ មានអាគុយម៉ង់ ${ta(t)}$ នោះ $z=r\\left({cx(t)}+i{sx(t)}\\right)$ ដែល $r>0$ ។ គេបាន\n$$z=r\\left({tz(c, s2)}\\right)$$\nប្រៀបធៀបផ្នែកនិមិត្តនឹង ${tx(z.b)}$ ៖\n"
              f"$${tx(s2)}\\,r={tx(z.b)}\\Rightarrow r={tx(z.r)}$$\nប្រៀបធៀបផ្នែកពិត ៖\n$$m=r{cx(t)}={tx(z.r)}\\times {br(c)}={tx(z.a)}$$\nដូចនេះ {bx('m='+tx(z.a))} ហើយ {bx('|z|='+tx(z.r))} ។")
        return D("argument_parameter", "medium", q, s_, f"m={tx(z.a)},\\ |z|={tx(z.r)}", [check(f"arg({z.py})", f"({t})*pi", "argument"), check(f"Abs({z.py})", z.r, "modulus")], ("a", z.key()))
    a, b = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, -1), (2, -1), (-1, 2), (-1, 1), (3, -2)]); m_ = R(b, a); im = sp.expand(a + b * m_)
    tgt = R(1, 2) if im > 0 else R(-1, 2); ex = f"\\left({tz(a, b)}\\right)\\left(m+i\\right)"
    q = f"គេឱ្យ $z={ex}$ ដែល $m$ ជាចំនួនពិត ។ រក $m$ ដើម្បីឱ្យ $z$ ជាចំនួននិមិត្ត រួចកំណត់ម៉ូឌុល និងអាគុយម៉ង់នៃ $z$ ។"
    s_ = (f"ពន្លាត ៖ $$z={br(a)}m+{br(a)}i+{br(b)}mi+{br(b)}i^{{2}}=\\left({tx(a)}m{'-' if b > 0 else '+'}{abs(b)}\\right)+i\\left({a}{'+' if b > 0 else '-'}{'' if abs(b) == 1 else abs(b)}m\\right)$$\n"
          f"$z$ ជាចំនួននិមិត្ត លុះត្រាតែផ្នែកពិតស្មើសូន្យ ៖ $${tx(a)}m{'-' if b > 0 else '+'}{abs(b)}=0\\Leftrightarrow m={tx(m_)}$$\nជំនួសទៅផ្នែកនិមិត្ត ៖ $z={ib(im)}$ ។ ដូច្នេះ $|z|={tx(abs(im))}$ ហើយ $z$ នៅលើអ័ក្សនិមិត្ត ខាង{'លើ' if im > 0 else 'ក្រោម'} ។\n"
          f"ដូចនេះ {bx('m='+tx(m_))} , $|z|={tx(abs(im))}$ និងអាគុយម៉ង់គឺ {bx(ta(tgt)+'+2k'+chr(92)+'pi,'+chr(92)+' k'+chr(92)+'in'+chr(92)+'mathbb{Z}')} ។")
    return D("argument_parameter", "medium", q, s_, f"m={tx(m_)}", [check(f"re(expand(({a}+I*({b}))*({m_}+I)))", 0, "real part zero"), check(f"expand(({a}+I*({b}))*({m_}+I))", f"I*({im})", "value"), check(f"arg(expand(({a}+I*({b}))*({m_}+I)))", f"({tgt})*pi", "argument")], ("b", a, b))

def s_find_z(rng):
    kind = rng.choice(["q", "p", "c", "sq"]); w = rz(rng, small=True); rr = rng.choice([1, 2, 4, 6, SQ(2), 2*SQ(2), SQ(3), 2*SQ(3)]); ph = rng.choice(F3 + F4 + F6 + [R(1, 2)])
    if kind == "q":
        z = Z(rr, ph + w.t); E = f"\\frac{{z}}{{{w.tex}}}"; rel = f"តាង $w={w.tex}$ ។ បើ $\\alpha$ ជាអាគុយម៉ង់នៃ $z$ នោះអាគុយម៉ង់នៃ $\\frac{{z}}{{w}}$ គឺ $\\alpha-{br_ang(w.t)}$ ។ គេបាន\n$$\\alpha-{br_ang(w.t)}={ta(ph)}+2k\\pi\\Rightarrow \\alpha={ta(z.t)}+2k\\pi$$"
    elif kind == "p":
        z = Z(rr, ph - w.t); E = f"\\left({w.tex}\\right)z"; rel = f"តាង $w={w.tex}$ ។ បើ $\\alpha$ ជាអាគុយម៉ង់នៃ $z$ នោះអាគុយម៉ង់នៃ $wz$ គឺ $\\alpha+{br_ang(w.t)}$ ។ គេបាន\n$$\\alpha+{br_ang(w.t)}={ta(ph)}+2k\\pi\\Rightarrow \\alpha={ta(z.t)}+2k\\pi$$"
    elif kind == "c":
        z = Z(rr, -ph); E = "\\overline{z}"; w = None; rel = f"អាគុយម៉ង់នៃ $\\overline{{z}}$ ផ្ទុយនឹងអាគុយម៉ង់នៃ $z$ ដូច្នេះ $\\alpha={ta(-ph)}+2k\\pi$"
    else:
        ph = rng.choice([R(1, 3), R(2, 3), R(1, 2), R(-1, 2), R(-1, 3), R(-2, 3)]); z = Z(rr, ph / 2); E = "z^{2}"; w = None
        rel = f"តាមរូបមន្តដឺម័រ បើ $\\alpha$ ជាអាគុយម៉ង់នៃ $z$ នោះ $2\\alpha={ta(ph)}+2k\\pi$ នាំឱ្យ $\\alpha={ta(z.t)}+k\\pi$ ។ ដោយផ្នែកពិតនៃ $z$ វិជ្ជមាន គេយក $\\alpha={ta(z.t)}$"
    cond = f"ផ្នែកពិតនៃ $z$ វិជ្ជមាន ហើយ " if kind == "sq" else ""
    if kind == "sq" and z.a <= 0: return None
    q = f"រកចំនួនកុំផ្លិច $z$ ជាទម្រង់ពីជគណិត ដោយដឹងថា $|z|={tx(rr)}$ , {cond}${ta(ph)}$ ជាអាគុយម៉ង់មួយនៃ ${E}$ ។"
    c, n = cs(z.t)
    s_ = rel + " ។\n" + f"គេបាន $$z={z.tf}$$\n" + f"ដោយ ${cx(z.t)}={tx(c)}$ និង ${sx(z.t)}={tx(n)}$ យើងបាន $z={rcoef(z.r)}\\left({tz(c, n)}\\right)={z.tex}$ ។\nដូចនេះ {bx('z='+z.tex)} ។"
    chk = [check(f"Abs({z.py})", rr, "modulus"), check(z.py, z.pyt, "form")]
    if kind in ("q", "p"):
        e = f"({z.py})/({w.py})" if kind == "q" else f"({z.py})*({w.py})"
        chk.append(check(f"simplify(({e})/(cos(({ph})*pi)+I*sin(({ph})*pi)))", sp.radsimp(z.r / w.r) if kind == "q" else z.r * w.r, "argument condition"))
    return D("find_z_from_modulus_argument", "medium", q, s_, f"z={z.tex}", chk, (z.key(), kind, str(ph), w.key() if w else 0))

def s_quad(rng):
    z = rz(rng, small=True)
    while z.b == 0 or not (2 * z.a).is_Rational or not (z.r ** 2).is_Rational or z.r ** 2 > 40: z = rz(rng, small=True)
    if z.b < 0: z = z.conj()
    p = sp.expand(-2 * z.a); qq = sp.expand(z.r ** 2); n = rng.choice([3, 4, 6, 6, 8, 12]); w = z.conj()
    if z.r ** n > 10 ** 6: return None
    eq = f"z^{{2}}{'' if p == 0 else ('+' if p > 0 else '-') + ('' if abs(p) == 1 else tx(abs(p))) + 'z'}+{tx(qq)}=0"
    D2 = sp.expand(p ** 2 - 4 * qq); root = sp.sqrt(-D2)
    q = f"ដោះស្រាយសមីការ ${eq}$ ក្នុងសំណុំចំនួនកុំផ្លិច ។ សរសេរឫសនីមួយៗជាទម្រង់ត្រីកោណមាត្រ រួចគណនា $z_{{1}}^{{{n}}}+z_{{2}}^{{{n}}}$ ។"
    s_ = (f"ឌីសគ្រីមីណង់ ៖ $$\\Delta={sq(p)}-4\\times {tx(qq)}={tx(D2)}=\\left({ib(root)}\\right)^{{2}}$$\nសមីការមានឫសពីរ ៖\n$$z_{{1}}=\\frac{{{tx(-p)}+{ib(root)}}}{{2}}={z.tex},\\quad z_{{2}}=\\frac{{{tx(-p)}-{ib(root)}}}{{2}}={w.tex}$$\n" + write_trig("z_{1}", z, rng) +
          f"\nឫសទីពីរជាចំនួនកុំផ្លិចឆ្លាស់នៃឫសទីមួយ ដូច្នេះ $z_{{2}}={w.tf}$ ។\nតាមរូបមន្តដឺម័រ $$z_{{1}}^{{{n}}}+z_{{2}}^{{{n}}}=2\\times {tx(z.r**n)}{cx(z.t*n)}$$\n")
    v = sp.expand(2 * z.pow(n).a)
    s_ += f"ដោយ ${cx(z.t*n)}={tx(cs(red(z.t*n))[0])}$ យើងបាន $z_{{1}}^{{{n}}}+z_{{2}}^{{{n}}}={tx(v)}$ ។\nដូចនេះ {bx('z_{1}='+z.tex)} , {bx('z_{2}='+w.tex)} ហើយ {bx('z_{1}^{'+str(n)+'}+z_{2}^{'+str(n)+'}='+tx(v))} ។"
    chk = [check(f"expand(({z.py})**2+({p})*({z.py})+({qq}))", 0, "root"), check(f"expand(({w.py})**2+({p})*({w.py})+({qq}))", 0, "root")] + ck_trig(z) + [check(f"expand(({z.py})**{n}+({w.py})**{n})", v, "power sum")]
    return D("quadratic_then_trigonometric", "hard", q, s_, f"z_{{1}}={z.tex},\\ z_{{2}}={w.tex},\\ z_{{1}}^{{{n}}}+z_{{2}}^{{{n}}}={tx(v)}", chk, (z.key(), n))

# ---------- roots ----------
STD = (1, 2, 3, 4, 6)
RROOT = {2: [1, 2, 3, 4, SQ(2), SQ(3), 2*SQ(2)], 3: [1, 2, 3], 4: [1, 2, 3, SQ(2)], 6: [1, 2, SQ(2)]}
def rand_target(rng, n):
    for _ in range(100):
        u = R(rng.randint(-12, 12), 12); ph = red(n * u)
        if ph.q in STD and (n * u == ph): return ph, rng.choice(RROOT[n])
    return None
def F_roots(w, n, R0, nm="z", var="w", rng=None):
    """Solve z^n = w by the trigonometric method. Returns text and root data."""
    ph = w.t; rho = w.r; lst = []; k0 = [ph / n + R(2 * k, n) for k in range(n)]
    s_ = (f"យើងសរសេរ ${var}$ ជាទម្រង់ត្រីកោណមាត្រ ${var}={w.tf}$ ។\nតាង ${nm}=\\rho(\\cos\\beta+i\\sin\\beta)$ ដែល $\\rho>0$ ។ តាមរូបមន្តដឺម័រ ${nm}^{{{n}}}=\\rho^{{{n}}}(\\cos {n}\\beta+i\\sin {n}\\beta)$ ។ សមីការផ្ដល់ឱ្យ ៖\n"
          f"$$\\rho^{{{n}}}={tx(rho)}\\quad\\text{{និង}}\\quad {n}\\beta={ta(ph)}+2k\\pi,\\ k\\in\\mathbb{{Z}}$$\nនាំឱ្យ $\\rho={tx(R0)}$ និង $\\beta={ta(ph / n)}+\\frac{{2k\\pi}}{{{n}}}$ ។ យក $k=0,1,\\ldots,{n-1}$ គេបាន ៖\n")
    s_ = s_.replace("k=0,1,\\ldots," + str(n - 1), "k=" + ",".join(str(j) for j in range(n)))
    for k, b in enumerate(k0):
        z = Z(R0, b); lst.append((z, b))
        s_ += f"$$z_{{{k}}}={tf(R0, b)}" + (f"={z.tex}" if z.t.q in STD else "") + "$$\n"
    return s_, lst
def fig_roots(lst, R0, poly=True, center=(0, 0), alt=""):
    return dict(points=[(f"z_{{{k}}}", float(z.a) + center[0], float(z.b) + center[1]) for k, (z, _) in enumerate(lst)], circle=(float(R0), center), poly=poly, alt=alt)

def s_nth(rng):
    n = rng.choice([2, 3, 3, 3, 4, 4, 6]); ph, R0 = rand_target(rng, n); w = Z(R0 ** n, ph)
    if n == 2 and ph == 0: return None
    alg = rng.random() < .55
    wtex = w.tex if alg else w.tf; wn = {2: "ឫសការេ", 3: "ឫសទី $3$ ", 4: "ឫសទី $4$ ", 6: "ឫសទី $6$ "}[n]
    q = rng.choice([f"រក{wn}នៃចំនួនកុំផ្លិច $w={wtex}$ ជាទម្រង់ត្រីកោណមាត្រ ។", f"ដោះស្រាយសមីការ $z^{{{n}}}={wtex}$ ក្នុងសំណុំចំនួនកុំផ្លិច ។", f"គេឱ្យ $w={wtex}$ ។ រកចំនួនកុំផ្លិច $z$ ទាំងអស់ដែល $z^{{{n}}}=w$ ។"])
    t_, lst = F_roots(w, n, R0)
    s_ = "" if "$w=" in q else f"តាង $w={wtex}$ ។\n"
    if alg: s_ += write_trig("w", w, rng, head=False) + "\n"
    s_ += t_ + f"ដូចនេះ សមីការមានឫស ${n}$ គឺ " + " , ".join(f"$z_{{{k}}}={tf(R0, b)}$" for k, (z, b) in enumerate(lst)) + " ។"
    chk = [check(f"Abs({w.py})", w.r, "modulus of w")]
    for z, b in lst:
        chk.append(check(f"({pyt(R0, b)})**{n}" if z.t.q == 12 else f"expand(({z.py})**{n})", w.pyt if z.t.q == 12 else w.py, "root satisfies equation"))
    fig = None
    if n >= 3: fig = fig_roots(lst, R0, alt=f"រូបភាពនៃឫសទាំង {n} នៅលើរង្វង់ផ្ចិត O កាំ {tx(R0)} ហើយបង្កើតជាពហុកោណនិយ័ត")
    return D("textbook_nth_roots", "hard" if n > 2 else "medium", q, s_, ",\\ ".join(f"z_{{{k}}}={tf(R0, b)}" for k, (z, b) in enumerate(lst)), chk, (n, w.key()), fig)

def s_unity(rng):
    n = rng.choice([3, 4, 5, 6, 8, 10, 12]); kind = rng.choice(["list", "sum", "pow"])
    W = f"\\cos\\frac{{2\\pi}}{{{n}}}+i\\sin\\frac{{2\\pi}}{{{n}}}"; t1 = R(2, n)
    if kind == "list":
        q = rng.choice([f"រកឫសទី ${n}$ នៃចំនួន $1$ ទាំងអស់ជាទម្រង់ត្រីកោណមាត្រ ។", f"ដោះស្រាយសមីការ $z^{{{n}}}=1$ ក្នុងសំណុំចំនួនកុំផ្លិច ។"])
        s_ = f"សរសេរ $1=\\cos 0+i\\sin 0$ ។ តាង $z=\\rho(\\cos\\beta+i\\sin\\beta)$ ។ តាមរូបមន្តដឺម័រ ៖\n$$\\rho^{{{n}}}=1\\quad\\text{{និង}}\\quad {n}\\beta=2k\\pi,\\ k\\in\\mathbb{{Z}}$$\nដូច្នេះ $\\rho=1$ និង $\\beta=\\frac{{2k\\pi}}{{{n}}}$ ។ យក $k=0,1,\\ldots,{n-1}$ ៖\n"
        pts = []; chk = []
        for k in range(n):
            b = R(2 * k, n); s_ += f"$$z_{{{k}}}={cx(b)}+i{sx(b)}"
            if n in (3, 4, 6, 12) and red(b).q in STD: zz = Z(1, b); s_ += "=" + zz.tex
            s_ += "$$\n"; pts.append((f"z_{{{k}}}", float(sp.cos(b * PI)), float(sp.sin(b * PI))))
            chk.append(check(f"(cos(({b})*pi)+I*sin(({b})*pi))**{n}" if n not in (5, 10, 8) else f"cos({n}*({b})*pi)+I*sin({n}*({b})*pi)", 1, "root of unity"))
        s_ += f"ដូចនេះ ឫសទី ${n}$ នៃ $1$ គឺ {bx('z_{k}='+chr(92)+'cos'+chr(92)+'frac{2k'+chr(92)+'pi}{'+str(n)+'}+i'+chr(92)+'sin'+chr(92)+'frac{2k'+chr(92)+'pi}{'+str(n)+'}')} ដែល $k=0,1,\\ldots,{n-1}$ ។"
        return D("textbook_roots_of_unity", "medium", q, s_, f"z_{{k}}=\\cos\\frac{{2k\\pi}}{{{n}}}+i\\sin\\frac{{2k\\pi}}{{{n}}}", chk, (n, kind), dict(points=pts, circle=(1.0, (0, 0)), poly=True, alt=f"ឫសទី {n} នៃ 1 នៅលើរង្វង់ឯកតា"))
    if kind == "sum":
        q = f"តាង $\\omega={W}$ ។ បង្ហាញថា $1+\\omega+\\omega^{{2}}+\\cdots+\\omega^{{{n-1}}}=0$ រួចទាញរកតម្លៃនៃ $S=" + "+".join([f"\\cos\\frac{{{2*k}\\pi}}{{{n}}}" for k in range(1, 3)]) + f"+\\cdots+\\cos\\frac{{{2*(n-1)}\\pi}}{{{n}}}$ ។"
        s_ = (f"តាមរូបមន្តដឺម័រ $\\omega^{{{n}}}=\\cos 2\\pi+i\\sin 2\\pi=1$ ហើយ $\\omega\\neq1$ ។ ផលបូកនៃស្វ៊ីតធរណីមាត្រឱ្យ ៖\n$$1+\\omega+\\cdots+\\omega^{{{n-1}}}=\\frac{{1-\\omega^{{{n}}}}}{{1-\\omega}}=\\frac{{1-1}}{{1-\\omega}}=0$$\n"
              f"ម្យ៉ាងទៀត $\\omega^{{k}}=\\cos\\frac{{2k\\pi}}{{{n}}}+i\\sin\\frac{{2k\\pi}}{{{n}}}$ ។ យកផ្នែកពិតនៃសមភាពខាងលើ ៖\n$$1+\\cos\\frac{{2\\pi}}{{{n}}}+\\cos\\frac{{4\\pi}}{{{n}}}+\\cdots+\\cos\\frac{{{2*(n-1)}\\pi}}{{{n}}}=0$$\nដូចនេះ {bx('S=-1')} ។")
        pys = "+".join(f"cos({2*k}*pi/{n})" for k in range(1, n))
        return D("textbook_roots_of_unity", "hard", q, s_, "S=-1", [check(pys, -1, "cosine sum"), check("+".join(f"sin({2*k}*pi/{n})" for k in range(1, n)), 0, "sine sum")], (n, kind))
    if n in (5, 10, 8): return None
    a = rng.randint(n + 1, 60); b = rng.randint(n + 1, 60); ra, rb = a % n, b % n; t = R(2 * (ra + rb), n)
    if a == b: return None
    q = f"តាង $\\omega={W}$ ។ គណនា $\\omega^{{{a}}}\\times\\omega^{{{b}}}$ និង $\\omega^{{{a}}}+\\omega^{{{b}}}$ ។"
    ZA, ZB = Z(1, R(2 * ra, n)), Z(1, R(2 * rb, n)); P = Z(1, t); Ssum = (sp.expand(ZA.a + ZB.a), sp.expand(ZA.b + ZB.b))
    s_ = (f"តាមរូបមន្តដឺម័រ $\\omega^{{{n}}}=\\cos 2\\pi+i\\sin 2\\pi=1$ ។ ដូច្នេះស្វ័យគុណនៃ $\\omega$ វិលជុំរៀងរាល់ ${n}$ ដង ។\n$${a}={n}\\times {a//n}+{ra},\\quad {b}={n}\\times {b//n}+{rb}$$\nគេបាន $\\omega^{{{a}}}=\\omega^{{{ra}}}={ZA.tex}$ និង $\\omega^{{{b}}}=\\omega^{{{rb}}}={ZB.tex}$ ។\n"
          f"ដូចនេះ {bx(chr(92)+'omega^{'+str(a)+'}'+chr(92)+'times'+chr(92)+'omega^{'+str(b)+'}='+P.tex)} និង {bx(chr(92)+'omega^{'+str(a)+'}+'+chr(92)+'omega^{'+str(b)+'}='+tz(*Ssum))} ។")
    return D("textbook_roots_of_unity", "medium", q, s_, f"{P.tex},\\ {tz(*Ssum)}", [check(f"cos(2*pi*{a}/{n})+I*sin(2*pi*{a}/{n})", ZA.py, "power a"), check(f"cos(2*pi*{b}/{n})+I*sin(2*pi*{b}/{n})", ZB.py, "power b"), check(f"cos(2*pi*{a+b}/{n})+I*sin(2*pi*{a+b}/{n})", P.py, "product")], (n, kind, a, b))

WP = "(-1/2+I*sqrt(3)/2)"
def s_omega(rng):
    kind = rng.choice(["ab", "n1", "n2", "abc", "pq"])
    intro = rng.choice(["តាងចំនួនកុំផ្លិច $\\omega=-\\frac{1}{2}+i\\frac{\\sqrt{3}}{2}$ ។ ", "គេឱ្យចំនួនកុំផ្លិច $\\omega=-\\frac{1}{2}+i\\frac{\\sqrt{3}}{2}$ ។ "])
    base = ("ទម្រង់ត្រីកោណមាត្រ ៖ $\\omega=\\cos\\frac{2\\pi}{3}+i\\sin\\frac{2\\pi}{3}$ ។ តាមរូបមន្តដឺម័រ $\\omega^{3}=\\cos 2\\pi+i\\sin 2\\pi=1$ ។ ដោយ $\\omega^{3}-1=(\\omega-1)(\\omega^{2}+\\omega+1)=0$ ហើយ $\\omega\\neq1$ នោះ $1+\\omega+\\omega^{2}=0$ ។\n")
    if kind == "n1" or kind == "n2":
        n = rng.randint(4, 40); e = 2 if kind == "n1" else 1; ex = "1+\\omega" if kind == "n1" else "1+\\omega^{2}"; sg = (-1) ** n; m_ = (e * n) % 3
        val = Z(1, R(2 * m_, 3)); a, b = sg * val.a, sg * val.b
        q = intro + f"បង្ហាញថា $1+\\omega+\\omega^{{2}}=0$ រួចគណនា $\\left({ex}\\right)^{{{n}}}$ ។"
        s_ = base + f"ដូច្នេះ ${ex}=-\\omega^{{{e}}}$ ។ គេបាន\n$$\\left({ex}\\right)^{{{n}}}=(-1)^{{{n}}}\\omega^{{{e*n}}}$$\nដោយ ${e*n}=3\\times {e*n//3}+{m_}$ នោះ $\\omega^{{{e*n}}}=\\omega^{{{m_}}}$ ។\nដូចនេះ {bx(chr(92)+'left('+ex+chr(92)+'right)^{'+str(n)+'}='+tz(a, b))} ។"
        pyx = f"expand((1+{WP})**{n})" if e == 2 else f"expand((1+{WP}**2)**{n})"
        return D("textbook_cube_root_of_unity", "hard", q, s_, tz(a, b), [check(pyx, py(a, b), "value")], (kind, n))
    if kind == "ab":
        a, b = rng.randint(4, 50), rng.randint(4, 50); ra, rb = a % 3, b % 3; A, B = Z(1, R(2 * ra, 3)), Z(1, R(2 * rb, 3)); u, v = sp.expand(A.a + B.a), sp.expand(A.b + B.b)
        if a == b: return None
        q = intro + f"គណនា $\\omega^{{{a}}}+\\omega^{{{b}}}$ ។"
        s_ = base + f"ស្វ័យគុណនៃ $\\omega$ វិលជុំរៀងរាល់ $3$ ដង ៖ ${a}=3\\times {a//3}+{ra}$ និង ${b}=3\\times {b//3}+{rb}$ ។\nគេបាន $\\omega^{{{a}}}+\\omega^{{{b}}}=\\omega^{{{ra}}}+\\omega^{{{rb}}}=\\left({A.tex}\\right)+\\left({B.tex}\\right)$ ។\nដូចនេះ {bx(chr(92)+'omega^{'+str(a)+'}+'+chr(92)+'omega^{'+str(b)+'}='+tz(u, v))} ។"
        return D("textbook_cube_root_of_unity", "medium", q, s_, tz(u, v), [check(f"expand({WP}**{a}+{WP}**{b})", py(u, v), "value")], (kind, ra, rb, a, b))
    if kind == "abc":
        a, b, c = rng.randint(1, 7), rng.randint(1, 7), rng.randint(1, 7); v = a*a + b*b + c*c - a*b - b*c - c*a
        if a == b == c: return None
        q = intro + f"គណនា $P=\\left({a}+{b}\\omega+{c}\\omega^{{2}}\\right)\\left({a}+{b}\\omega^{{2}}+{c}\\omega\\right)$ ។"
        s_ = base + f"ពន្លាតផលគុណ ហើយប្រើ $\\omega^{{3}}=1$ ៖\n$$P={a*a}+{a*b}\\omega^{{2}}+{a*c}\\omega+{a*b}\\omega+{b*b}\\omega^{{3}}+{b*c}\\omega^{{2}}+{a*c}\\omega^{{2}}+{b*c}\\omega^{{4}}+{c*c}\\omega^{{3}}$$\nដោយ $\\omega^{{4}}=\\omega$ គេដាក់ជាក្រុមបាន ៖\n$$P={a*a+b*b+c*c}+{a*b+b*c+a*c}\\left(\\omega+\\omega^{{2}}\\right)$$\nដោយ $\\omega+\\omega^{{2}}=-1$ នោះ $P={a*a+b*b+c*c}-{a*b+b*c+a*c}$ ។\nដូចនេះ {bx('P='+str(v))} ។"
        return D("textbook_cube_root_of_unity", "hard", q, s_, f"P={v}", [check(f"expand(({a}+{b}*{WP}+{c}*{WP}**2)*({a}+{b}*{WP}**2+{c}*{WP}))", v, "P")], (kind, a, b, c))
    p, r_ = rng.randint(1, 9), rng.randint(1, 9); v = p*p - p*r_ + r_*r_
    q = intro + f"គណនា $\\left({p}+{r_}\\omega\\right)\\left({p}+{r_}\\omega^{{2}}\\right)$ ។"
    s_ = base + f"ពន្លាត ៖ $$\\left({p}+{r_}\\omega\\right)\\left({p}+{r_}\\omega^{{2}}\\right)={p*p}+{p*r_}\\left(\\omega+\\omega^{{2}}\\right)+{r_*r_}\\omega^{{3}}$$\nជំនួស $\\omega+\\omega^{{2}}=-1$ និង $\\omega^{{3}}=1$ គេបាន ${p*p}-{p*r_}+{r_*r_}={v}$ ។\nដូចនេះ លទ្ធផលស្មើ {bx(str(v))} ។"
    return D("textbook_cube_root_of_unity", "medium", q, s_, str(v), [check(f"expand(({p}+{r_}*{WP})*({p}+{r_}*{WP}**2))", v, "value")], (kind, p, r_))

def s_shift(rng):
    n = rng.choice([2, 3, 3, 4]); ph, R0 = rand_target(rng, n); w = Z(R0 ** n, ph); ca, cb = rng.choice([(1, 0), (-1, 0), (2, 0), (-2, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (3, 0), (0, 2)])
    cc = tz(ca, cb); sgn = tz(-ca, -cb); e = f"z{'' if sgn.startswith('-') else '+'}{sgn}"; e = e if not (ca and cb) else f"z-\\left({cc}\\right)"
    q = f"ដោះស្រាយសមីការ $\\left({e}\\right)^{{{n}}}={w.tex}$ ក្នុងសំណុំចំនួនកុំផ្លិច ។"
    t_, lst = F_roots(w, n, R0, nm="u", var="w")
    if any(z.t.q not in STD for z, _ in lst): return None
    s_ = f"តាង $u={e}$ និង $w={w.tex}$ ។ សមីការក្លាយជា $u^{{{n}}}=w$ ។\n" + write_trig("w", w, rng, head=False) + "\n" + t_.replace("z_{", "u_{")
    s_ += f"ត្រឡប់ទៅ $z=u+{br(ca) if cb == 0 else chr(92)+'left('+cc+chr(92)+'right)'}$ ៖\n"; res = []
    chk = []
    for k, (z, b) in enumerate(lst):
        A, B = sp.expand(z.a + ca), sp.expand(z.b + cb); res.append(tz(A, B)); s_ += f"$$z_{{{k}}}={res[-1]}$$\n"
        chk.append(check(f"expand(({py(A, B)}-({ca}+I*({cb})))**{n})", w.py, "root"))
    s_ += "ដូចនេះ សំណុំឫសគឺ $\\boxed{\\left\\{" + ",\\ ".join(res) + "\\right\\}}$ ។"
    return D("textbook_shifted_power_equation", "hard", q, s_, ",\\ ".join(res), chk, (n, w.key(), ca, cb))

def s_polygon(rng):
    n = rng.choice([3, 3, 4, 6]); ph, R0 = rand_target(rng, n); w = Z(R0 ** n, ph)
    shape = {3: "ត្រីកោណសម័ង្ស", 4: "ការេ", 6: "ឆកោណនិយ័ត"}[n]
    q = f"គេឱ្យសមីការ $z^{{{n}}}={w.tex}$ ។\nក. ដោះស្រាយសមីការនេះក្នុងសំណុំចំនួនកុំផ្លិច ។\nខ. បង្ហាញថារូបភាពនៃឫសទាំងនោះក្នុងប្លង់កុំផ្លិច ជាកំពូលនៃ{shape}មួយ ។\nគ. គណនារង្វាស់ជ្រុង និងផ្ទៃក្រឡានៃរូបនោះ ។"
    t_, lst = F_roots(w, n, R0)
    side = sp.expand(2 * R0 * sp.sin(PI / n)); area = sp.expand(R(n, 2) * R0 ** 2 * sp.sin(2 * PI / n))
    s_ = f"ក. តាង $w={w.tex}$ ។ " + t_ + f"ខ. គ្រប់ឫសមានម៉ូឌុល ${tx(R0)}$ ដូច្នេះរូបភាពនៅលើរង្វង់ផ្ចិត $O$ កាំ ${tx(R0)}$ ។ អាគុយម៉ង់នៃឫសពីរជាប់គ្នាខុសគ្នា $\\frac{{2\\pi}}{{{n}}}$ ជានិច្ច ដូច្នេះចំណុចទាំងនោះចែករង្វង់ជាធ្នូស្មើគ្នា ។ ដូច្នេះវាជាកំពូលនៃ{shape} ។\n"
    s_ += f"គ. តាង $A_{{k}}$ ជារូបភាពនៃឫស $z_{{k}}$ ក្នុងប្លង់កុំផ្លិច (ក្នុងរូប ចំណុចនេះមានស្លាក $z_{{k}}$) ។ ត្រីកោណ $OA_{{0}}A_{{1}}$ មាន $OA_{{0}}=OA_{{1}}={tx(R0)}$ និងមុំកំពូល $\\frac{{2\\pi}}{{{n}}}$ ។ រង្វាស់ជ្រុង ៖\n$$A_{{0}}A_{{1}}=|z_{{1}}-z_{{0}}|=2\\times {tx(R0)}\\sin\\frac{{\\pi}}{{{n}}}={tx(side)}$$\nផ្ទៃក្រឡាជាផលបូកនៃត្រីកោណស្មើគ្នា ${n}$ ៖\n$$S={n}\\times\\frac{{1}}{{2}}\\times {sq(R0)}\\times\\sin\\frac{{2\\pi}}{{{n}}}={tx(area)}$$\nដូចនេះ រង្វាស់ជ្រុង {bx(tx(side))} ឯកតា និងផ្ទៃក្រឡា {bx('S='+tx(area))} ឯកតាផ្ទៃ ។"
    z0, z1 = lst[0][0], lst[1][0]
    chk = [check(f"Abs(({z1.pyt})-({z0.pyt}))", side, "side"), check(f"({n})*Rational(1,2)*({R0})**2*sin(2*pi/{n})", area, "area")] + [check(f"Abs({z.pyt})", R0, "on circle") for z, _ in lst[:2]]
    return D("textbook_roots_regular_polygon", "bacii", q, s_, f"{tx(side)},\\ S={tx(area)}", chk, (n, w.key()), fig_roots(lst, R0, alt=f"{shape}ចារឹកក្នុងរង្វង់ផ្ចិត O កាំ {tx(R0)}"))

# ---------- trigonometric applications ----------
TRIP = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17), (7, 24, 25), (24, 7, 25), (20, 21, 29), (21, 20, 29)]
def s_moivre_exp(rng):
    n = rng.choice([3, 3, 4]); p, q_, h = rng.choice(TRIP); quad = rng.choice([1, 1, 2, 4]); giv = rng.choice(["c", "s"])
    c = R(p, h) * (1 if quad in (1, 4) else -1); s2 = R(q_, h) * (1 if quad in (1, 2) else -1)
    rngtxt = {1: "0<\\alpha<\\frac{\\pi}{2}", 2: "\\frac{\\pi}{2}<\\alpha<\\pi", 4: "-\\frac{\\pi}{2}<\\alpha<0"}[quad]
    gv = f"\\cos\\alpha={tx(c)}" if giv == "c" else f"\\sin\\alpha={tx(s2)}"
    C = "\\cos\\alpha"; Sn = "\\sin\\alpha"
    q = f"ក. ដោយប្រើរូបមន្តដឺម័រ សរសេរ $\\cos {n}\\alpha$ និង $\\sin {n}\\alpha$ ជាអនុគមន៍នៃ ${C}$ និង ${Sn}$ ។\nខ. គេឱ្យ ${gv}$ ដែល ${rngtxt}$ ។ គណនា $\\cos {n}\\alpha$ និង $\\sin {n}\\alpha$ ។"
    if n == 3:
        ex = f"\\cos^{{3}}\\alpha+3i\\cos^{{2}}\\alpha\\sin\\alpha-3\\cos\\alpha\\sin^{{2}}\\alpha-i\\sin^{{3}}\\alpha"; fc = "\\cos^{3}\\alpha-3\\cos\\alpha\\sin^{2}\\alpha"; fs = "3\\cos^{2}\\alpha\\sin\\alpha-\\sin^{3}\\alpha"
        vc = c**3 - 3*c*s2**2; vs = 3*c**2*s2 - s2**3
        subc = f"{br(c)}^{{3}}-3{br(c)}{br(s2)}^{{2}}"; subs_ = f"3{br(c)}^{{2}}{br(s2)}-{br(s2)}^{{3}}"
    else:
        ex = f"\\cos^{{4}}\\alpha+4i\\cos^{{3}}\\alpha\\sin\\alpha-6\\cos^{{2}}\\alpha\\sin^{{2}}\\alpha-4i\\cos\\alpha\\sin^{{3}}\\alpha+\\sin^{{4}}\\alpha"; fc = "\\cos^{4}\\alpha-6\\cos^{2}\\alpha\\sin^{2}\\alpha+\\sin^{4}\\alpha"; fs = "4\\cos^{3}\\alpha\\sin\\alpha-4\\cos\\alpha\\sin^{3}\\alpha"
        vc = c**4 - 6*c**2*s2**2 + s2**4; vs = 4*c**3*s2 - 4*c*s2**3
        subc = f"{br(c)}^{{4}}-6{br(c)}^{{2}}{br(s2)}^{{2}}+{br(s2)}^{{4}}"; subs_ = f"4{br(c)}^{{3}}{br(s2)}-4{br(c)}{br(s2)}^{{3}}"
    other = (f"\\sin^{{2}}\\alpha=1-\\cos^{{2}}\\alpha=1-{sq(c)}={tx(s2**2)}", f"\\sin\\alpha={tx(s2)}", "ស៊ីនុស") if giv == "c" else (f"\\cos^{{2}}\\alpha=1-\\sin^{{2}}\\alpha=1-{sq(s2)}={tx(c**2)}", f"\\cos\\alpha={tx(c)}", "កូស៊ីនុស")
    s_ = (f"ក. តាមរូបមន្តដឺម័រ $(\\cos\\alpha+i\\sin\\alpha)^{{{n}}}=\\cos {n}\\alpha+i\\sin {n}\\alpha$ ។ ពន្លាតអង្គខាងឆ្វេងតាមទ្វេធា និងប្រើ $i^{{2}}=-1$ ៖\n$$(\\cos\\alpha+i\\sin\\alpha)^{{{n}}}={ex}$$\nចំនួនកុំផ្លិចពីរស្មើគ្នា លុះត្រាតែផ្នែកពិតស្មើគ្នា និងផ្នែកនិមិត្តស្មើគ្នា ៖\n$$\\cos {n}\\alpha={fc}$$\n$$\\sin {n}\\alpha={fs}$$\n"
          f"ខ. យើងមាន ${other[0]}$ ។ ដោយ ${rngtxt}$ សញ្ញានៃ{other[2]}ឱ្យ ${other[1]}$ ។ ជំនួសចូលរូបមន្ត ៖\n$$\\cos {n}\\alpha={subc}={tx(vc)}$$\n$$\\sin {n}\\alpha={subs_}={tx(vs)}$$\nដូចនេះ {bx(chr(92)+'cos '+str(n)+chr(92)+'alpha='+tx(vc))} និង {bx(chr(92)+'sin '+str(n)+chr(92)+'alpha='+tx(vs))} ។")
    zp = f"({c}+I*({s2}))"
    return D("de_moivre_multiple_angle", "hard", q, s_, f"\\cos {n}\\alpha={tx(vc)},\\ \\sin {n}\\alpha={tx(vs)}", [check(f"re(expand({zp}**{n}))", vc, "cos"), check(f"im(expand({zp}**{n}))", vs, "sin"), check(f"({c})**2+({s2})**2", 1, "Pythagoras")], (n, c, s2, giv))

LIN = [("cos", 2, "\\cos^{2}\\theta", "\\left(z+\\frac{1}{z}\\right)^{2}=z^{2}+2+\\frac{1}{z^{2}}", "4\\cos^{2}\\theta=2\\cos 2\\theta+2", "\\frac{1+\\cos 2\\theta}{2}", "(1+cos(2*x))/2", "cos(x)**2", lambda t: (1 + sp.cos(2*t)) / 2),
       ("cos", 3, "\\cos^{3}\\theta", "\\left(z+\\frac{1}{z}\\right)^{3}=z^{3}+3z+\\frac{3}{z}+\\frac{1}{z^{3}}", "8\\cos^{3}\\theta=2\\cos 3\\theta+6\\cos\\theta", "\\frac{\\cos 3\\theta+3\\cos\\theta}{4}", "(cos(3*x)+3*cos(x))/4", "cos(x)**3", None),
       ("cos", 4, "\\cos^{4}\\theta", "\\left(z+\\frac{1}{z}\\right)^{4}=z^{4}+4z^{2}+6+\\frac{4}{z^{2}}+\\frac{1}{z^{4}}", "16\\cos^{4}\\theta=2\\cos 4\\theta+8\\cos 2\\theta+6", "\\frac{\\cos 4\\theta+4\\cos 2\\theta+3}{8}", "(cos(4*x)+4*cos(2*x)+3)/8", "cos(x)**4", None),
       ("cos", 5, "\\cos^{5}\\theta", "\\left(z+\\frac{1}{z}\\right)^{5}=z^{5}+5z^{3}+10z+\\frac{10}{z}+\\frac{5}{z^{3}}+\\frac{1}{z^{5}}", "32\\cos^{5}\\theta=2\\cos 5\\theta+10\\cos 3\\theta+20\\cos\\theta", "\\frac{\\cos 5\\theta+5\\cos 3\\theta+10\\cos\\theta}{16}", "(cos(5*x)+5*cos(3*x)+10*cos(x))/16", "cos(x)**5", None),
       ("sin", 2, "\\sin^{2}\\theta", "\\left(z-\\frac{1}{z}\\right)^{2}=z^{2}-2+\\frac{1}{z^{2}}", "-4\\sin^{2}\\theta=2\\cos 2\\theta-2", "\\frac{1-\\cos 2\\theta}{2}", "(1-cos(2*x))/2", "sin(x)**2", None),
       ("sin", 3, "\\sin^{3}\\theta", "\\left(z-\\frac{1}{z}\\right)^{3}=z^{3}-3z+\\frac{3}{z}-\\frac{1}{z^{3}}", "-8i\\sin^{3}\\theta=2i\\sin 3\\theta-6i\\sin\\theta", "\\frac{3\\sin\\theta-\\sin 3\\theta}{4}", "(3*sin(x)-sin(3*x))/4", "sin(x)**3", None),
       ("sin", 4, "\\sin^{4}\\theta", "\\left(z-\\frac{1}{z}\\right)^{4}=z^{4}-4z^{2}+6-\\frac{4}{z^{2}}+\\frac{1}{z^{4}}", "16\\sin^{4}\\theta=2\\cos 4\\theta-8\\cos 2\\theta+6", "\\frac{\\cos 4\\theta-4\\cos 2\\theta+3}{8}", "(cos(4*x)-4*cos(2*x)+3)/8", "sin(x)**4", None),
       ("sin", 5, "\\sin^{5}\\theta", "\\left(z-\\frac{1}{z}\\right)^{5}=z^{5}-5z^{3}+10z-\\frac{10}{z}+\\frac{5}{z^{3}}-\\frac{1}{z^{5}}", "32i\\sin^{5}\\theta=2i\\sin 5\\theta-10i\\sin 3\\theta+20i\\sin\\theta", "\\frac{\\sin 5\\theta-5\\sin 3\\theta+10\\sin\\theta}{16}", "(sin(5*x)-5*sin(3*x)+10*sin(x))/16", "sin(x)**5", None)]
def s_linear(rng):
    fn, n, nm, ex, mid, res, pyr, pyl, _ = rng.choice(LIN); th = rng.choice([None, None, R(1, 12), R(5, 12), R(1, 6), R(1, 4)])
    q = f"តាង $z=\\cos\\theta+i\\sin\\theta$ ។ បង្ហាញថា $z^{{n}}+\\frac{{1}}{{z^{{n}}}}=2\\cos n\\theta$ និង $z^{{n}}-\\frac{{1}}{{z^{{n}}}}=2i\\sin n\\theta$ ។ រួចសរសេរ ${nm}$ ជាផលបូកនៃស៊ីនុស ឬកូស៊ីនុសនៃពហុគុណនៃ $\\theta$ ។"
    s_ = ("តាមរូបមន្តដឺម័រ $z^{n}=\\cos n\\theta+i\\sin n\\theta$ និង $\\frac{1}{z^{n}}=\\cos(-n\\theta)+i\\sin(-n\\theta)=\\cos n\\theta-i\\sin n\\theta$ ។\nបូក និងដកពីរសមភាពនេះ គេបាន $z^{n}+\\frac{1}{z^{n}}=2\\cos n\\theta$ និង $z^{n}-\\frac{1}{z^{n}}=2i\\sin n\\theta$ ។\n"
          + ("យក $n=1$ ៖ $z+\\frac{1}{z}=2\\cos\\theta$ ។ លើកជាស្វ័យគុណ ហើយដាក់តួជាគូ ៖\n" if fn == "cos" else "យក $n=1$ ៖ $z-\\frac{1}{z}=2i\\sin\\theta$ ។ លើកជាស្វ័យគុណ ហើយដាក់តួជាគូ ៖\n")
          + f"$${ex}$$\nគេបាន $${mid}$$\n")
    chk = [check(pyl, pyr, "identity")]; ans = f"{nm}={res}"
    if th is not None:
        q += f" ទាញរកតម្លៃនៃ ${nm.replace(chr(92)+'theta', ta(th))}$ ។"
        val = sp.nsimplify(sp.expand(sp.sympify(pyl.replace("x", f"({th})*pi")))); r2 = res.replace("\\theta", "\\times "+ta(th)) if False else None
        terms = re.sub(r"(\d)\\theta", lambda m_: f"{m_.group(1)}\\times {ta(th)}", res).replace("\\theta", ta(th))
        s_ += f"ដូច្នេះ ${nm}={res}$ ។\nជំនួស $\\theta={ta(th)}$ ៖ $${nm.replace(chr(92)+'theta', ta(th))}={terms}={tx(val)}$$\n"
        chk.append(check(pyr.replace("x", f"({th})*pi"), val, "value")); ans += f",\\ {tx(val)}"
        s_ += f"ដូចនេះ {bx(nm+'='+res)} ហើយតម្លៃនោះគឺ {bx(tx(val))} ។"
    else:
        s_ += f"ចែកអង្គទាំងពីរនឹងមេគុណ ។\nដូចនេះ {bx(nm+'='+res)} ។"
    return D("linearize_powers_trig", "hard", q, s_, ans, chk, (fn, n, str(th)))

def s_acos(rng):
    z = rz(rng, small=True); c0 = rng.choice([1, -1, R(1, 2), R(-1, 2), SQ(2)/2, -SQ(2)/2, SQ(3)/2, -SQ(3)/2, 0])
    z = Z(z.r, z.t); a, b, r, ph = z.a, z.b, z.r, z.t; be = {1: R(0), -1: R(1), R(1, 2): R(1, 3), R(-1, 2): R(2, 3), SQ(2)/2: R(1, 4), -SQ(2)/2: R(3, 4), SQ(3)/2: R(1, 6), -SQ(3)/2: R(5, 6), 0: R(1, 2)}[c0]; c = sp.expand(r * c0)
    def term(v, f):
        return f"{tx(v)}\\{f} x" if abs(v) != 1 else ("-" if v < 0 else "") + f"\\{f} x"
    t2 = term(b, "sin"); lhs = term(a, "cos") + ("" if t2.startswith("-") else "+") + t2
    q = rng.choice([f"ដោយសរសេរ ${tz(a, b)}$ ជាទម្រង់ត្រីកោណមាត្រ ដោះស្រាយសមីការ ${lhs}={tx(c)}$ ក្នុងសំណុំចំនួនពិត ។", f"ក. សរសេរចំនួនកុំផ្លិច $z={tz(a, b)}$ ជាទម្រង់ត្រីកោណមាត្រ ។\nខ. ទាញបង្ហាញថា ${lhs}={rcoef(r)}\\cos\\left(x-{br_ang(ph)}\\right)$ ។\nគ. ដោះស្រាយសមីការ ${lhs}={tx(c)}$ ។"])
    s_ = write_trig("z", z, rng) + f"\nគេបាន ${tx(a)}={rcoef(r)}{cx(ph)}$ និង ${tx(b)}={rcoef(r)}{sx(ph)}$ ។ ជំនួសក្នុងកន្សោម ៖\n$${lhs}={rcoef(r)}\\left({cx(ph)}\\cos x+{sx(ph)}\\sin x\\right)={rcoef(r)}\\cos\\left(x-{br_ang(ph)}\\right)$$\n"
    s_ += f"សមីការក្លាយជា $\\cos\\left(x-{br_ang(ph)}\\right)={fr(c, r)}={tx(c0)}$ ។\n"
    chk = [check(f"({a})*cos(x)+({b})*sin(x)", f"({r})*cos(x-({ph})*pi)", "identity")]
    if be == 0 or be == 1:
        x0 = ph + be; s_ += f"នាំឱ្យ $x-{br_ang(ph)}={ta(be)}+2k\\pi$ ។\nដូចនេះ {bx('x='+ta(x0)+'+2k'+chr(92)+'pi,'+chr(92)+' k'+chr(92)+'in'+chr(92)+'mathbb{Z}')} ។"; ans = f"x={ta(x0)}+2k\\pi"; sols = [x0]
    else:
        x1, x2 = ph + be, ph - be; s_ += f"ដោយ ${tx(c0)}=\\cos{ta(be)}$ នាំឱ្យ $x-{br_ang(ph)}=\\pm{ta(be)}+2k\\pi$ ។\nដូចនេះ {bx('x='+ta(x1)+'+2k'+chr(92)+'pi')} ឬ {bx('x='+ta(x2)+'+2k'+chr(92)+'pi')} ដែល $k\\in\\mathbb{{Z}}$ ។"; ans = f"x={ta(x1)}+2k\\pi,\\ x={ta(x2)}+2k\\pi"; sols = [x1, x2]
    for v in sols: chk.append(check(f"({a})*cos(({v})*pi)+({b})*sin(({v})*pi)", c, "solution satisfies equation"))
    return D("trig_equation_via_complex", "hard", q, s_, ans, chk, (z.key(), str(c0)))

def s_geo(rng):
    z1 = rz(rng, small=True); kind = rng.choice(["eq", "eq", "ri", "rg", "is"]); sg = rng.choice([1, -1]); th = {"eq": R(1, 3), "ri": R(1, 2), "rg": R(1, 2), "is": rng.choice([R(1, 6), R(1, 4), R(2, 3), R(3, 4)])}[kind] * sg; rho = rng.choice([2, 3, SQ(3)]) if kind == "rg" else 1
    z2 = Z(z1.r * rho, z1.t + th)
    if z2.t.q not in STD: return None
    Q = Z(rho, th); ta_, u, v = F_quot_alg("z_{2}", z2, "z_{1}", z1); ptA = (float(z1.a), float(z1.b)); ptB = (float(z2.a), float(z2.b)); Rg = max(float(z1.r), float(z2.r))
    q = f"ក្នុងប្លង់កុំផ្លិច គេឱ្យចំណុច $A$ និង $B$ ជារូបភាពរៀងគ្នានៃ $z_{{1}}={z1.tex}$ និង $z_{{2}}={z2.tex}$ ។\nក. គណនា $\\frac{{z_{{2}}}}{{z_{{1}}}}$ រួចសរសេរជាទម្រង់ត្រីកោណមាត្រ ។\nខ. ទាញរកប្រភេទនៃត្រីកោណ $OAB$ ។"
    s_ = "ក. " + ta_ + "\n" + write_trig("\\frac{z_{2}}{z_{1}}", Q, rng, head=False).replace("|\\frac{z_{2}}{z_{1}}|", "\\left|\\frac{z_{2}}{z_{1}}\\right|") + "\n"
    D_ = sp.expand(sp.sqrt(sp.expand((z2.a - z1.a)**2 + (z2.b - z1.b)**2)))
    s_ += f"ខ. យើងមាន $\\frac{{OB}}{{OA}}=\\left|\\frac{{z_{{2}}}}{{z_{{1}}}}\\right|={tx(rho)}$ ហើយមុំពី $\\overrightarrow{{OA}}$ ទៅ $\\overrightarrow{{OB}}$ មានរង្វាស់ ${ta(th)}$ ។\n"
    verdict = {"eq": "ត្រីកោណសម័ង្ស", "ri": "ត្រីកោណកែងសមបាតត្រង់ $O$", "rg": "ត្រីកោណកែងត្រង់ $O$", "is": "ត្រីកោណសមបាតត្រង់ $O$"}[kind]
    why = {"eq": "ដោយ $OA=OB$ និងមុំកំពូល $AOB$ ស្មើ $\\frac{\\pi}{3}$ នោះត្រីកោណសមបាតនេះមានមុំទាំងបីស្មើ $\\frac{\\pi}{3}$ ។", "ri": "ដោយ $OA=OB$ និងមុំ $AOB$ ស្មើ $\\frac{\\pi}{2}$ ។", "rg": f"ដោយមុំ $AOB$ ស្មើ $\\frac{{\\pi}}{{2}}$ ប៉ុន្តែ $OB={tx(rho)}OA$ ។", "is": "ដោយ $OA=OB$ ប៉ុន្តែមុំកំពូលមិនមែន $\\frac{\\pi}{3}$ ឬ $\\frac{\\pi}{2}$ ទេ ។"}[kind]
    s_ += why + f"\nដូចនេះ $OAB$ ជា{verdict} ។"
    chk = [check(f"simplify(({z2.py})/({z1.py}))", Q.py, "ratio"), check(f"Abs({z2.py})/Abs({z1.py})", rho, "ratio of lengths")]
    return D("textbook_triangle_from_quotient", "hard", q, s_, verdict.replace("$", "").replace("ត្រីកោណកែងសមបាតត្រង់ O", "OA=OB,\\ \\widehat{AOB}=\\frac{\\pi}{2}") if False else f"\\frac{{z_{{2}}}}{{z_{{1}}}}={Q.tf}", chk, (z1.key(), z2.key()),
             dict(points=[("A", *ptA), ("B", *ptB), ("O", 0, 0)], circle=None, poly=True, alt=f"ត្រីកោណ OAB ក្នុងប្លង់កុំផ្លិច"))

def s_geosum(rng):
    m_ = rng.choice([3, 4, 6, 12]); N = rng.randint(m_ + 1, 30); kk = [k for k in range(1, m_) if sp.gcd(k, m_) == 1]; k = rng.choice(kk); z = Z(1, R(2 * k, m_))
    q = f"{rng.choice(GIVE)} $z={z.tex}$ ។ បង្ហាញថា $z^{{{m_}}}=1$ រួចគណនា $S=1+z+z^{{2}}+\\cdots+z^{{{N}}}$ ។"
    L = N + 1; rem = L % m_; A = sum([Z(1, R(2 * k * j, m_)).a for j in range(rem)], sp.Integer(0)); B = sum([Z(1, R(2 * k * j, m_)).b for j in range(rem)], sp.Integer(0))
    s_ = write_trig("z", z, rng, head=False) + f"\nតាមរូបមន្តដឺម័រ $z^{{{m_}}}=\\cos {2*k}\\pi+i\\sin {2*k}\\pi=1$ ។\nដោយ $z\\neq1$ ផលបូកតួ ${m_}$ ជាប់គ្នាណាមួយស្មើសូន្យ ព្រោះ $$1+z+\\cdots+z^{{{m_-1}}}=\\frac{{1-z^{{{m_}}}}}{{1-z}}=0$$\nផលបូក $S$ មាន ${L}$ តួ ហើយ ${L}={m_}\\times {L//m_}+{rem}$ ។ ក្រុមតួ ${m_}$ ពេញៗ ស្មើសូន្យ ។ "
    if rem == 0: s_ += f"គ្មានតួសល់ទេ ។\nដូចនេះ {bx('S=0')} ។"; fin = "0"
    else:
        tl = "+".join(["1"] + ([f"z"] if rem > 1 else []) + [f"z^{{{j}}}" for j in range(2, rem)]); fin = tz(A, B)
        s_ += f"នៅសល់តែ ${rem}$ តួខាងចុង ដែលស្មើនឹង ${tl}$ ។\nគណនា ៖ $S={tl}={fin}$ ។\nដូចនេះ {bx('S='+fin)} ។"
    pys = "+".join(f"({z.py})**{j}" for j in range(N + 1))
    return D("sum_of_powers_root_of_unity", "hard", q, s_, f"S={fin}", [check(f"expand({pys})", py(A, B), "S"), check(f"expand(({z.py})**{m_})", 1, "period")], (m_, k, N))

def s_rootcheck(rng):
    z = rz(rng, small=True)
    while z.b == 0 or not (2*z.a).is_Integer or not (z.r**2).is_Integer: z = rz(rng, small=True)
    c = rng.choice([1, 2, 3, -1, -2, -3]); p = sp.expand(2*z.a); r2 = sp.expand(z.r**2); A = -(c + p); B = r2 + c*p; C = -c*r2; w = z.conj(); n = rng.choice([3, 4, 6, 8])
    def mono(co, e):
        sgn = "+" if co > 0 else "-"; ab = abs(co)
        return "" if co == 0 else f"{sgn}{'' if ab == 1 and e else ab}" + {2: "z^{2}", 1: "z", 0: ""}[e]
    P = "z^{3}" + mono(A, 2) + mono(B, 1) + mono(C, 0); z2 = z.pow(2); z3 = z.pow(3)
    if z.r ** n > 10**6: return None
    q = f"គេឱ្យពហុធា $P(z)={P}$ ។\nក. បង្ហាញថា $z_{{0}}={z.tex}$ ជាឫសរបស់សមីការ $P(z)=0$ ។\nខ. ដោះស្រាយសមីការ $P(z)=0$ ក្នុងសំណុំចំនួនកុំផ្លិច ។\nគ. សរសេរ $z_{{0}}$ ជាទម្រង់ត្រីកោណមាត្រ រួចគណនា $z_{{0}}^{{{n}}}$ ។"
    trm = lambda co, v: "" if co == 0 else ("+" if co > 0 else "-") + (str(abs(co)) if abs(co) != 1 else "") + "\\left(" + v + "\\right)"
    s_ = f"ក. គណនាស្វ័យគុណនៃ $z_{{0}}$ ៖ $z_{{0}}^{{2}}={z2.tex}$ និង $z_{{0}}^{{3}}={z3.tex}$ ។ ជំនួសក្នុង $P$ ៖\n$$P(z_{{0}})=\\left({z3.tex}\\right){trm(A, z2.tex)}{trm(B, z.tex)}{mono(C, 0)}=0$$\nដូច្នេះ $z_{{0}}$ ជាឫសនៃសមីការ ។\n"
    s_ += f"ខ. មេគុណនៃ $P$ ជាចំនួនពិត ដូច្នេះ $\\overline{{z_{{0}}}}={w.tex}$ ក៏ជាឫសដែរ ។ យើងមាន $z_{{0}}+\\overline{{z_{{0}}}}={tx(p)}$ និង $z_{{0}}\\overline{{z_{{0}}}}={tx(r2)}$ ដូច្នេះ $P(z)$ ចែកដាច់នឹង $z^{{2}}{mono(-p, 1)}+{tx(r2)}$ ។ គេបាន\n$$P(z)=\\left(z{mono(-c, 0)}\\right)\\left(z^{{2}}{mono(-p, 1)}+{tx(r2)}\\right)$$\nឫសទីបីគឺ $z={c}$ ។ ដូច្នេះសំណុំឫសគឺ $\\left\\{{{c},\\ {z.tex},\\ {w.tex}\\right\\}}$ ។\n"
    s_ += "គ. " + write_trig("z_{0}", z, rng, head=False) + "\n"; t_, W = F_power("z_{0}", z, n, rng); s_ += t_ + f"\nដូចនេះ {bx('z_{0}^{'+str(n)+'}='+W.tex)} ។"
    Ppy = lambda v: f"expand(({v})**3+({A})*({v})**2+({B})*({v})+({C}))"
    return D("cubic_root_then_trigonometric", "bacii", q, s_, f"z={c},\\ z={z.tex},\\ z={w.tex},\\ z_{{0}}^{{{n}}}={W.tex}", [check(Ppy(z.py), 0, "root"), check(Ppy(w.py), 0, "root"), check(Ppy(str(c)), 0, "root")] + ck_trig(z) + [check(f"expand(({z.py})**{n})", W.py, "power")], (z.key(), c, n))

# ---------- BacII multi-part items ----------
LAB = [list("កខគឃងច"), list("១២៣៤៥៦"), list("abcdef"), list("១២៣៤៥៦")]
def labels(rng):
    i = rng.randint(0, 3); sep = rng.choice([". ", ". ", "- "]) if i == 0 else ". "
    return [c + sep for c in LAB[i]]
def assemble(sub, intro, parts, rng, key):
    lab = labels(rng); qs = [intro]; ss = []; chk = []; ans = []
    for i, (q, s_, a, c) in enumerate(parts):
        qs.append(lab[i] + q); ss.append(lab[i] + s_.replace("@PREV", lab[max(i-1, 0)].strip(" .-")).replace("@P0", lab[0].strip(" .-")).replace("@P1", lab[min(1, i)].strip(" .-"))); chk += c; ans.append(a)
    return D(sub, "bacii", "\n".join(qs), "\n".join(ss), ",\\ ".join(a for a in ans if a), chk, key)
def s_bacii_two(rng):
    pr = pair(rng)
    if not pr: return None
    z1, z2 = pr; n1, n2 = rng.choice([("z_{1}", "z_{2}"), ("z_{1}", "z_{2}"), ("z_{1}", "z_{2}"), ("A", "B")]); parts = []; st = rng.randint(0, 3)
    E = rng.choice(["q", "p", "both"]); done_alg = {}
    if rng.random() < .75:
        qq = {"q": f"$\\frac{{{n1}}}{{{n2}}}$", "p": f"${n1}\\times {n2}$", "both": f"${n1}\\times {n2}$ និង $\\frac{{{n1}}}{{{n2}}}$"}[E]; s_ = ""; a_ = []; c_ = []
        if E in ("p", "both"):
            t_, A, B = F_prod_alg(n1, z1, n2, z2); s_ += t_ + "\n"; done_alg["p"] = (A, B); a_.append(f"{n1}\\times {n2}={tz(A, B)}"); c_.append(check(f"expand(({z1.py})*({z2.py}))", py(A, B), "product"))
        if E in ("q", "both"):
            t_, A, B = F_quot_alg(n1, z1, n2, z2); s_ += t_ + "\n"; done_alg["q"] = (A, B); a_.append(f"\\frac{{{n1}}}{{{n2}}}={tz(A, B)}"); c_.append(check(f"simplify(({z1.py})/({z2.py}))", py(A, B), "quotient"))
        s_ += "ដូចនេះ " + " និង ".join("$\\boxed{" + a + "}$" for a in a_) + " ។"
        parts.append((f"គណនា {qq} ជាទម្រង់ពីជគណិត ។", s_, ",\\ ".join(a_), c_))
    s_ = write_trig(n1, z1, rng, st) + "\n" + write_trig(n2, z2, rng, st) + f"\nដូចនេះ {bx(n1+'='+z1.tf)} និង {bx(n2+'='+z2.tf)} ។"
    parts.append((f"សរសេរ ${n1}$ និង ${n2}$ ជាទម្រង់ត្រីកោណមាត្រ ។", s_, f"{n1}={z1.tf},\\ {n2}={z2.tf}", ck_trig(z1) + ck_trig(z2) + ck_arg(z1)))
    Q = rng.choice(list(done_alg) or ["q", "p"]); pick_ = rng.choice([Q, Q, "both"]); s_ = ""; a_ = []; c_ = []; W = {}
    if pick_ in ("p", "both"):
        t_, P = F_prod_trig(n1, z1, n2, z2, rng); s_ += t_ + "\n"; W["p"] = P; a_.append(f"{n1}\\times {n2}={P.tf}"); c_.append(check(f"({z1.py})*({z2.py})", P.pyt, "product trig"))
    if pick_ in ("q", "both"):
        t_, P = F_quot_trig(n1, z1, n2, z2, rng); s_ += t_ + "\n"; W["q"] = P; a_.append(f"\\frac{{{n1}}}{{{n2}}}={P.tf}"); c_.append(check(f"({z1.py})/({z2.py})", P.pyt, "quotient trig"))
    s_ += "ដូចនេះ " + " និង ".join("$\\boxed{" + a + "}$" for a in a_) + " ។"
    qq = {"q": f"$\\frac{{{n1}}}{{{n2}}}$", "p": f"${n1}\\times {n2}$", "both": f"${n1}\\times {n2}$ និង $\\frac{{{n1}}}{{{n2}}}$"}[pick_]
    parts.append((rng.choice([f"ទាញរក {qq} ជាទម្រង់ត្រីកោណមាត្រ ។", f"សរសេរ {qq} ជាទម្រង់ត្រីកោណមាត្រ ។"]), s_, ",\\ ".join(a_), c_))
    # exact values part
    ex = [k for k in W if k in done_alg and W[k].t.q == 12]
    if ex:
        k = ex[0]; P = W[k]; u, v = done_alg[k]; T = P.t; c, n = cs(T); Ee = f"\\frac{{{n1}}}{{{n2}}}" if k == "q" else f"{n1}\\times {n2}"
        s_ = (f"តាមសំណួរខាងលើ ${Ee}$ មានទម្រង់ពីរ ៖ $${P.tf}={tz(u, v)}$$\nប្រៀបធៀបផ្នែកពិត និងផ្នែកនិមិត្ត ៖\n$${rcoef(P.r)}{cx(T)}={tx(u)},\\quad {rcoef(P.r)}{sx(T)}={tx(v)}$$\nដូចនេះ {bx(cx(T)+'='+tx(c))} និង {bx(sx(T)+'='+tx(n))} ។")
        parts.append((f"ទាញរកតម្លៃនៃ ${cx(T)}$ និង ${sx(T)}$ ។", s_, f"{cx(T)}={tx(c)},\\ {sx(T)}={tx(n)}", [check(f"cos(({T})*pi)", c, "exact cos"), check(f"sin(({T})*pi)", n, "exact sin")]))
    k = rng.choice(list(W)); P = W[k]; Ee = f"\\frac{{{n1}}}{{{n2}}}" if k == "q" else f"{n1}\\times {n2}"
    opts = [m_ for m_ in (2, 3, 4, 6, 8, 12) if (P.t * m_).q != 12 and 1e-4 < float(P.r) ** m_ < 10 ** 6]
    if opts and rng.random() < .75:
        m_ = rng.choice(opts); Pn = P.pow(m_); t_, _ = F_power("Z", P, m_, rng, tag=f"\\left({Ee}\\right)^{{{m_}}}")
        pyv = f"simplify(({z1.py})/({z2.py}))" if k == "q" else f"expand(({z1.py})*({z2.py}))"
        parts.append((rng.choice([f"គណនា $\\left({Ee}\\right)^{{{m_}}}$ ។", f"ទាញរកតម្លៃនៃ $\\left({Ee}\\right)^{{{m_}}}$ ។"]), t_ + f"\nដូចនេះ {bx(chr(92)+'left('+Ee+chr(92)+'right)^{'+str(m_)+'}='+Pn.tex)} ។", f"\\left({Ee}\\right)^{{{m_}}}={Pn.tex}", [check(f"expand({pyv}**{m_})", Pn.py, "power")]))
    elif float(z1.r) ** 4 < 10**5:
        m_ = rng.choice([3, 4, 6]); t_, Pn = F_power(n1, z1, m_, rng)
        parts.append((f"គណនា ${n1}^{{{m_}}}$ ។", t_ + f"\nដូចនេះ {bx(n1+'^{'+str(m_)+'}='+Pn.tex)} ។", f"{n1}^{{{m_}}}={Pn.tex}", [check(f"expand(({z1.py})**{m_})", Pn.py, "power")]))
    intro = rng.choice([f"គេមានចំនួនកុំផ្លិច ${n1}={z1.tex}$ និង ${n2}={z2.tex}$ ។", f"គេឱ្យចំនួនកុំផ្លិច ${n1}={z1.tex}$ និង ${n2}={z2.tex}$ ។", f"គេមាន ${n1}={z1.tex}$ និង ${n2}={z2.tex}$ ជាចំនួនកុំផ្លិចពីរ ។"])
    return assemble("bacii_two_numbers", intro, parts, rng, (z1.key(), z2.key(), E, pick_, len(parts)))

def s_bacii_one(rng):
    z = rz(rng, small=True); parts = []; nm = "z"; w = z.conj()
    c1, c2 = F_cs("z", z)
    parts.append(("រកម៉ូឌុល និងអាគុយម៉ង់នៃ $z$ រួចសរសេរ $z$ ជាទម្រង់ត្រីកោណមាត្រ ។", write_trig("z", z, rng, head=False) + f"\nដូចនេះ ម៉ូឌុលនៃ $z$ គឺ ${tx(z.r)}$ អាគុយម៉ង់គឺ ${ta(z.t)}+2k\\pi,\\ k\\in\\mathbb{{Z}}$ ហើយ {bx('z='+z.tf)} ។", f"z={z.tf}", ck_trig(z) + ck_arg(z)))
    ch = rng.sample(["pow2", "conjq", "inv", "powbig", "sum", "real", "sqrt"], rng.choice([2, 3]))
    if "real" in ch and "powbig" in ch: ch.remove("powbig")
    for c in ch:
        if c == "pow2":
            t_, P2 = F_power("z", z, 2, rng); t3, P3 = F_power("z", z, 3, rng)
            parts.append(("គណនា $z^{2}$ និង $z^{3}$ ។", t_ + "\n" + t3 + f"\nដូចនេះ {bx('z^{2}='+P2.tex)} និង {bx('z^{3}='+P3.tex)} ។", f"z^{{2}}={P2.tex},\\ z^{{3}}={P3.tex}", [check(f"expand(({z.py})**2)", P2.py, "z^2"), check(f"expand(({z.py})**3)", P3.py, "z^3")]))
        if c == "conjq":
            Q = z / w
            parts.append(("សរសេរ $\\frac{z}{\\overline{z}}$ ជាទម្រង់ត្រីកោណមាត្រ (ដែល $\\overline{z}$ ជាចំនួនកុំផ្លិចឆ្លាស់នៃ $z$) ។", f"យើងមាន $\\overline{{z}}={w.tf}$ ។ ចែកម៉ូឌុលនឹងម៉ូឌុល ហើយដកអាគុយម៉ង់ ៖\n$$\\frac{{z}}{{\\overline{{z}}}}={tf(1, 2*z.t)}$$\n" + (f"ដោយកាត់បន្ថយមុំ គេបាន $\\frac{{z}}{{\\overline{{z}}}}={Q.tf}$ ។\n" if red(2*z.t) != 2*z.t else "") + f"ដូចនេះ {bx(chr(92)+'frac{z}{'+chr(92)+'overline{z}}='+Q.tf)} ។", f"\\frac{{z}}{{\\overline{{z}}}}={Q.tf}", [check(f"({z.py})/conjugate({z.py})", Q.pyt, "z over conj")]))
        if c == "inv":
            Q = Z(sp.radsimp(1 / z.r), -z.t)
            parts.append(("គណនា $\\frac{1}{z}$ ជាទម្រង់ត្រីកោណមាត្រ និងជាទម្រង់ពីជគណិត ។", f"តាមទម្រង់ត្រីកោណមាត្រនៃ $z$ ៖ $$\\frac{{1}}{{z}}={fr(1, z.r)}\\left[{cx(-z.t)}+i{sx(-z.t)}\\right]$$\nគណនាតម្លៃ គេបាន $\\frac{{1}}{{z}}={Q.tex}$ ។\nដូចនេះ {bx(chr(92)+'frac{1}{z}='+Q.tf+'='+Q.tex)} ។", f"\\frac{{1}}{{z}}={Q.tex}", [check(f"1/({z.py})", Q.py, "inverse")]))
        if c == "powbig":
            n = rng.choice([m_ for m_ in (6, 8, 9, 10, 12) if float(z.r) ** m_ < 10 ** 7] or [4]); t_, P = F_power("z", z, n, rng)
            parts.append((f"ទាញរកតម្លៃនៃ $z^{{{n}}}$ ។", t_ + f"\nដូចនេះ {bx('z^{'+str(n)+'}='+P.tex)} ។", f"z^{{{n}}}={P.tex}", [check(f"expand(({z.py})**{n})", P.py, "power")]))
        if c == "sum":
            n = rng.choice([m_ for m_ in (3, 4, 5, 6) if float(z.r) ** m_ < 10 ** 6]); P = z.pow(n); v = sp.expand(2 * P.a)
            parts.append((f"គណនា $z^{{{n}}}+\\left(\\overline{{z}}\\right)^{{{n}}}$ ។", f"ដោយ $\\left(\\overline{{z}}\\right)^{{{n}}}=\\overline{{z^{{{n}}}}}$ ផលបូកស្មើពីរដងផ្នែកពិតនៃ $z^{{{n}}}$ ៖\n$$z^{{{n}}}+\\left(\\overline{{z}}\\right)^{{{n}}}=2\\times {tx(z.r**n)}{cx(n*z.t)}={tx(v)}$$\nដូចនេះ {bx('z^{'+str(n)+'}+'+chr(92)+'left('+chr(92)+'overline{z}'+chr(92)+'right)^{'+str(n)+'}='+tx(v))} ។", f"{tx(v)}", [check(f"expand(({z.py})**{n}+({py(z.a, -z.b)})**{n})", v, "sum")]))
        if c == "real":
            n = z.t.q; P = z.pow(n)
            parts.append((f"បង្ហាញថា $z^{{{n}}}$ ជាចំនួនពិត ។", f"តាមរូបមន្តដឺម័រ ៖ $$z^{{{n}}}={rcoef_pow(z.r, n)}\\left({cx(n*z.t)}+i{sx(n*z.t)}\\right)$$\nដោយ ${sx(n*z.t)}=0$ ផ្នែកនិមិត្តរលាយបាត់ ។\nដូចនេះ {bx('z^{'+str(n)+'}='+P.tex)} ជាចំនួនពិត ។", f"z^{{{n}}}={P.tex}", [check(f"im(expand(({z.py})**{n}))", 0, "real"), check(f"expand(({z.py})**{n})", P.py, "value")]))
        if c == "sqrt":
            if (z.t / 2).q == 12 or z.t.q == 4: continue
            A = Z(sp.sqrt(z.r), z.t / 2)
            parts.append(("រកចំនួនកុំផ្លិច $u$ ពីរ ដែល $u^{2}=z$ ជាទម្រង់ត្រីកោណមាត្រ ។", f"តាង $u=\\rho(\\cos\\beta+i\\sin\\beta)$ ។ តាមរូបមន្តដឺម័រ $\\rho^{{2}}={tx(z.r)}$ និង $2\\beta={ta(z.t)}+2k\\pi$ ។ ដូច្នេះ $\\rho={tx(A.r)}$ និង $\\beta={ta(z.t/2)}+k\\pi$ ។ យក $k=0,1$ ៖\n$$u_{{0}}={tf(A.r, z.t/2)},\\quad u_{{1}}={tf(A.r, z.t/2+1)}$$\nដូចនេះ {bx('u_{0}='+tf(A.r, z.t/2))} និង {bx('u_{1}='+tf(A.r, z.t/2+1))} ។", f"u_{{0}}={tf(A.r, z.t/2)}", [check(f"({A.pyt})**2", z.py, "square root")]))
    if len(parts) < 3: return None
    intro = rng.choice([f"គេមានចំនួនកុំផ្លិច $z={z.tex}$ ។", f"គេឱ្យចំនួនកុំផ្លិច $z={z.tex}$ ។"])
    return assemble("bacii_single_number", intro, parts, rng, (z.key(), tuple(sorted(ch))))

def s_bacii_quad(rng):
    z = rz(rng, small=True)
    while z.b == 0 or not (2*z.a).is_Rational or not (z.r**2).is_Rational or z.r**2 > 40: z = rz(rng, small=True)
    if z.b < 0: z = z.conj()
    w = z.conj(); p = sp.expand(-2*z.a); qq = sp.expand(z.r**2); D2 = sp.expand(p**2 - 4*qq); root = sp.sqrt(-D2)
    eq = f"z^{{2}}{'' if p == 0 else ('+' if p > 0 else '-') + ('' if abs(p) == 1 else tx(abs(p))) + 'z'}+{tx(qq)}=0"; Q = Z(1, 2*z.t); n = rng.choice([m_ for m_ in (3, 4, 6, 12) if (Q.t*m_).q != 12]); Qn = Q.pow(n); m_ = rng.choice([6, 12, 4, 3]); Pm = z.pow(m_)
    if float(z.r) ** m_ > 10 ** 7: return None
    parts = [(f"ដោះស្រាយសមីការ ${eq}$ ក្នុងសំណុំចំនួនកុំផ្លិច ។ តាង $z_{{1}}$ ជាឫសដែលមានផ្នែកនិមិត្តវិជ្ជមាន និង $z_{{2}}$ ជាឫសមួយទៀត ។",
              f"$$\\Delta={sq(p)}-4\\times {tx(qq)}={tx(D2)}=\\left({ib(root)}\\right)^{{2}}$$\nសមីការមានឫសពីរ ៖ $$z_{{1}}=\\frac{{{tx(-p)}+{ib(root)}}}{{2}}={z.tex},\\quad z_{{2}}=\\frac{{{tx(-p)}-{ib(root)}}}{{2}}={w.tex}$$\nដូចនេះ {bx('z_{1}='+z.tex)} និង {bx('z_{2}='+w.tex)} ។", f"z_{{1}}={z.tex},\\ z_{{2}}={w.tex}", [check(f"expand(({z.py})**2+({p})*({z.py})+({qq}))", 0, "root"), check(f"expand(({w.py})**2+({p})*({w.py})+({qq}))", 0, "root")]),
             ("សរសេរ $z_{1}$ , $z_{2}$ និង $\\frac{z_{1}}{z_{2}}$ ជាទម្រង់ត្រីកោណមាត្រ ។", write_trig("z_{1}", z, rng) + f"\nដោយ $z_{{2}}=\\overline{{z_{{1}}}}$ នោះ $z_{{2}}={w.tf}$ ។\nចែកទម្រង់ទាំងពីរ ៖ $$\\frac{{z_{{1}}}}{{z_{{2}}}}={tf(1, 2*z.t)}$$\nដូចនេះ {bx(chr(92)+'frac{z_{1}}{z_{2}}='+Q.tf)} ។", f"\\frac{{z_{{1}}}}{{z_{{2}}}}={Q.tf}", ck_trig(z) + [check(f"({z.py})/({w.py})", Q.pyt, "quotient")]),
             (f"គណនា $\\left(\\frac{{z_{{1}}}}{{z_{{2}}}}\\right)^{{{n}}}$ និង $z_{{1}}^{{{m_}}}$ ។", F_power("Q", Q, n, rng, tag=f"\\left(\\frac{{z_{{1}}}}{{z_{{2}}}}\\right)^{{{n}}}")[0] + "\n" + F_power("z_{1}", z, m_, rng)[0] + f"\nដូចនេះ {bx(chr(92)+'left('+chr(92)+'frac{z_{1}}{z_{2}}'+chr(92)+'right)^{'+str(n)+'}='+Qn.tex)} និង {bx('z_{1}^{'+str(m_)+'}='+Pm.tex)} ។", f"{Qn.tex},\\ {Pm.tex}", [check(f"expand(simplify(({z.py})/({w.py}))**{n})", Qn.py, "power of quotient"), check(f"expand(({z.py})**{m_})", Pm.py, "power")])]
    return assemble("bacii_quadratic_roots", "", parts, rng, (z.key(), n, m_)) if False else _noint("bacii_quadratic_roots", parts, rng, (z.key(), n, m_))
def _noint(sub, parts, rng, key):
    d = assemble(sub, "", parts, rng, key); d["prob"] = d["prob"].lstrip("\n"); return d

def s_bacii_three(rng):
    a, b, c = rz(rng, small=True), rz(rng, small=True), rz(rng, small=True)
    if len({a.key(), b.key(), c.key()}) < 3: return None
    W = a * b / c; st = rng.randint(0, 3); N = ("z_{1}", "z_{2}", "z_{3}"); opts = [m_ for m_ in (2, 3, 4, 6, 12) if (W.t*m_).q != 12 and 1e-4 < float(W.r)**m_ < 10**6]
    if not opts or (a.t + b.t - c.t) .q == 12 and rng.random() < .0: return None
    m_ = rng.choice(opts); Wn = W.pow(m_); raw = a.t + b.t - c.t; rt, r_ = F_reduce(raw)
    s2 = f"$$|Z|=\\frac{{{tx(a.r)}\\times {tx(b.r)}}}{{{tx(c.r)}}}={tx(W.r)}$$\nអាគុយម៉ង់មួយនៃ $Z$ គឺ $${ta(a.t)}+{br_ang(b.t)}-{br_ang(c.t)}={ta(raw)}$$\n" + (f"ហើយ ${ta(raw)}={rt}$ ។\n" if rt else "") + f"ដូចនេះ {bx('Z='+W.tf)} ។"
    t3 = F_power("Z", W, m_, rng)[0] + f"\nដូចនេះ {bx('Z^{'+str(m_)+'}='+Wn.tex)} ។"
    parts = [("សរសេរ $z_{1}$ , $z_{2}$ និង $z_{3}$ ជាទម្រង់ត្រីកោណមាត្រ ។", "\n".join(write_trig(n, v, rng, st) for n, v in zip(N, (a, b, c))) + f"\nដូចនេះ ទម្រង់ទាំងបីគឺដូចខាងលើ ។", "", ck_trig(a) + ck_trig(b) + ck_trig(c)),
             ("ទាញរកទម្រង់ត្រីកោណមាត្រនៃ $Z=\\frac{z_{1}\\times z_{2}}{z_{3}}$ ។", s2, f"Z={W.tf}", [check(f"({a.py})*({b.py})/({c.py})", W.pyt, "Z")]),
             (f"គណនា $Z^{{{m_}}}$ ជាទម្រង់ពីជគណិត ។", t3, f"Z^{{{m_}}}={Wn.tex}", [check(f"({W.pyt})**{m_}", Wn.py, "power")])]
    intro = rng.choice(GIVE) + f" $z_{{1}}={a.tex}$ , $z_{{2}}={b.tex}$ និង $z_{{3}}={c.tex}$ ។"
    return assemble("bacii_three_numbers", intro, parts, rng, (a.key(), b.key(), c.key()))

def s_bacii_roots(rng):
    n = rng.choice([3, 3, 4]); ph, R0 = rand_target(rng, n); w = Z(R0**n, ph); t_, lst = F_roots(w, n, R0)
    u = lst[0][0]; 
    parts = [(f"សរសេរ $w$ ជាទម្រង់ត្រីកោណមាត្រ ។", write_trig("w", w, rng, head=False) + f"\nដូចនេះ {bx('w='+w.tf)} ។", f"w={w.tf}", ck_trig(w)),
             (f"ដោះស្រាយសមីការ $z^{{{n}}}=w$ ក្នុងសំណុំចំនួនកុំផ្លិច ។", t_ + "ដូចនេះ ឫសទាំងអស់គឺដូចខាងលើ ។", ",\\ ".join(tf(R0, b) for _, b in lst), [check(f"({pyt(R0, b)})**{n}", w.pyt, "root") for _, b in lst]),
             (f"តាង $A_{{k}}$ ជារូបភាពនៃឫសទាំងនោះក្នុងប្លង់កុំផ្លិច ។ រកចម្ងាយពីចំណុច $A_{{k}}$ ទៅគល់តម្រុយ $O$ និងគណនា $|z_{{1}}-z_{{0}}|$ ។", f"គ្រប់ឫសមានម៉ូឌុល ${tx(R0)}$ ដូច្នេះ $OA_{{k}}={tx(R0)}$ ឯកតា ។\nមុំ $A_{{0}}OA_{{1}}$ ស្មើ $\\frac{{2\\pi}}{{{n}}}$ ហើយត្រីកោណ $OA_{{0}}A_{{1}}$ សមបាត ដូច្នេះ $$|z_{{1}}-z_{{0}}|=2\\times {tx(R0)}\\sin\\frac{{\\pi}}{{{n}}}={tx(2*R0*sp.sin(PI/n))}$$\nដូចនេះ {bx('OA_{k}='+tx(R0))} និង {bx('A_{0}A_{1}='+tx(2*R0*sp.sin(PI/n)))} ឯកតា ។", f"{tx(2*R0*sp.sin(PI/n))}", [check(f"Abs(({lst[1][0].pyt})-({lst[0][0].pyt}))", 2*R0*sp.sin(PI/n), "side")])]
    d = assemble("textbook_multipart_roots", f"គេឱ្យចំនួនកុំផ្លិច $w={w.tex}$ ។", parts, rng, (n, w.key()))
    d["fig"] = fig_roots(lst, R0, alt=f"ឫសទី {n} នៃ w នៅលើរង្វង់ផ្ចិត O កាំ {tx(R0)}")
    return d

# ---------- figures ----------
def tikz_plane(f):
    pts = f["points"]; ext = max([abs(p[1]) for p in pts] + [abs(p[2]) for p in pts] + [1]) * 1.35; sc = round(2.6 / ext, 2)
    if f.get("circle"): ext = max(ext, f["circle"][0] * 1.35)
    t = [f"\\begin{{tikzpicture}}[scale={sc}]", f"\\draw[->] ({-ext:.2f},0)--({ext:.2f},0) node[right]{{$x$}};", f"\\draw[->] (0,{-ext:.2f})--(0,{ext:.2f}) node[above]{{$y$}};"]
    if f.get("circle"):
        r_, c = f["circle"]; t.append(f"\\draw[dashed] ({c[0]:.3f},{c[1]:.3f}) circle ({r_:.3f});")
    if f.get("poly"):
        t.append("\\draw[thick] " + "--".join(f"({p[1]:.3f},{p[2]:.3f})" for p in pts) + "--cycle;")
    for lb, a, b in pts:
        t.append(f"\\fill ({a:.3f},{b:.3f}) circle (1pt) node[above right]{{${lb}$}};")
    t.append("\\end{tikzpicture}")
    return "\n".join(t)
def plane_png(rid, f):
    import matplotlib.patches as mp
    pts = f["points"]; ext = max([abs(p[1]) for p in pts] + [abs(p[2]) for p in pts] + [1]) * 1.4
    if f.get("circle"): ext = max(ext, f["circle"][0] * 1.4)
    fig, ax = plt.subplots(figsize=(3.6, 3.6), dpi=100)
    ax.axhline(0, color="#555", lw=.8); ax.axvline(0, color="#555", lw=.8)
    if f.get("circle"):
        r_, c = f["circle"]; ax.add_patch(mp.Circle(c, r_, fill=False, ls="--", lw=.9, color="gray"))
    if f.get("poly"):
        xs = [p[1] for p in pts] + [pts[0][1]]; ys = [p[2] for p in pts] + [pts[0][2]]; ax.plot(xs, ys, lw=1.6, color="#1f4e9c")
    for lb, a, b in pts:
        ax.plot([a], [b], "o", ms=4, color="#c0392b"); ax.annotate(f"${lb}$", (a, b), xytext=(5, 5), textcoords="offset points", fontsize=10)
    ax.set_xlim(-ext, ext); ax.set_ylim(-ext, ext); ax.set_aspect("equal"); ax.grid(alpha=.2)
    rel = f"diagrams/{rid}.png"; fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
    return rel

# ---------- driver ----------
QUOTA = [(s_modarg, 45), (s_trig_one, 90), (s_trig_several, 45), (s_trig_to_alg, 40), (s_false_trig, 50), (s_half, 22), (s_props, 50), (s_prodquot_trig, 60),
         (s_alg_prod, 45), (s_mixed, 35), (s_exact, 45), (s_power, 80), (s_power_trig, 30), (s_power_quot, 50), (s_conj_sum, 30), (s_year, 25), (s_small_n, 45),
         (s_param, 30), (s_find_z, 35), (s_quad, 45), (s_rootcheck, 25), (s_nth, 55), (s_unity, 22), (s_omega, 30), (s_shift, 25), (s_polygon, 20),
         (s_moivre_exp, 35), (s_linear, 14), (s_acos, 35), (s_geo, 30), (s_geosum, 22), (s_bacii_two, 190), (s_bacii_one, 100), (s_bacii_quad, 40), (s_bacii_three, 45), (s_bacii_roots, 20)]
def mkey(sub, t):
    return sub + "|" + re.sub(r"\s+", "", "|".join(re.findall(r"\$\$?(.+?)\$\$?", t, flags=re.S)))
def main():
    rng = random.Random(20261105); rows = []; seen = set(); ms = set(); figs = []
    for p in glob.glob(os.path.join(ROOT, "diagrams", TOPIC + "-*.png")): os.remove(p)
    try:
        from complex_polar_hand import H
    except ImportError:
        H = []
    for h in H:
        figs.append((h["row"], h.get("fig"))); ms.add(mkey(h["row"]["subtopic"], h["row"]["problem_km"]))
    for fn, quota in QUOTA:
        got = 0; tries = 0
        while got < quota and tries < quota * 40:
            tries += 1
            d = fn(rng)
            if not d: continue
            k = (d["sub"], d["key"]); m_ = mkey(d["sub"], d["prob"])
            if k in seen or m_ in ms: continue
            seen.add(k); ms.add(m_); got += 1
            r = make_row(TOPIC, d["sub"], d["diff"], d["prob"], d["sol"], d["ans"], d["checks"], "complex_polar", chapter="complex", grade=11)
            figs.append((r, d["fig"]))
        print(fn.__name__, got, tries, flush=True)
    png = 0
    for r, f in figs:
        if f:
            dg = {"type": "figure", "latex": tikz_plane(f), "alt_km": f["alt"]}
            if png < 290:
                dg["image"] = plane_png(r["id"], f); png += 1
            r["diagrams"] = [dg]
        r["exam"] = "BacII science"
        for k in ("problem_km", "solution_km", "answer_latex"):
            r[k] = tidy(r[k])
        r["exam_fit"] = "bacii_seen"
        rows.append(r)
    ids = set(); out = []
    for r in rows:
        if r["id"] in ids: continue
        ids.add(r["id"]); out.append(r)
    bad = [r["id"] for r in out for f in ("problem_km", "solution_km", "answer_latex") if re.search(r"\\(?:pi|alpha|beta|theta|omega|cos|sin|tan|times|cdot|rho)[0-9a-zA-Z]{0}(?=[0-9])|\}\^\{[^}]*\}\^", r[f])]
    print("latex lint", len(bad), bad[:5])
    write_jsonl(out, "complex/polar.jsonl"); print("png", png)
if __name__ == "__main__":
    main()
