"""Generator for topic `rules`: definition of the derivative, basic rules, product/quotient/chain rules,
derivative at a point. Writes out/rules.jsonl. Hand-written rows live in gen/rules_hand.py."""
import random, sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

GEN = "rules"
R = sp.Rational
SQ = sp.sqrt
rng = random.Random(20261105)

# ---------- small helpers ----------
def par(e):
    return "\\left(" + lx(e) + "\\right)"
def pa(e):
    """factor display: bare for a positive number or a bare symbol, otherwise in brackets"""
    e = sp.sympify(e)
    if (e.is_number and e > 0 and e.is_integer) or e == x:
        return lx(e)
    return par(e)
def cx(e):
    """coefficient display that vanishes for 1"""
    e = sp.sympify(e)
    return "" if e == 1 else pa(e)
def kd(c):
    return "" if c == 1 else "-" if c == -1 else str(c)
def nm(n, du):
    """n times du: fold into one number when du is a number, so digits never run together"""
    du = sp.sympify(du)
    return kd(n * du) if du.is_number else kd(n) + par(du)
def top_eq(s_):
    """split on = outside any braces"""
    out, d, cur = [], 0, ""
    for c in s_:
        d += (c == "{") - (c == "}")
        if c == "=" and d == 0:
            out.append(cur); cur = ""
        else:
            cur += c
    return out + [cur]
def no_repeat(t):
    """=X=X inside a formula, and a line $$=X$$ straight after a line that ended in =X"""
    def one(q):
        delim = "$$" if q.group(1) is not None else "$"
        body = q.group(1) if q.group(1) is not None else q.group(2)
        if "\\begin" in body or "\\neq" in body:
            return q.group(0)
        ps = top_eq(body); out = [ps[0]]
        for p_ in ps[1:]:
            if p_.strip() != out[-1].strip():
                out.append(p_)
        return delim + "=".join(out) + delim
    t = re.sub(r"\$\$([\s\S]+?)\$\$|\$([^$]+?)\$", one, t)
    lines = []
    for ln in t.split("\n"):
        q = re.fullmatch(r"\$\$=(.+)\$\$", ln)
        if q and lines and lines[-1].endswith("=" + q.group(1) + "$$"):
            continue
        lines.append(ln)
    return "\n".join(lines)
def tidy(t):
    t = t.replace("^{1}", "")
    t = re.sub(r"(?<![0-9.})])1\\(left\(|sqrt)", lambda m: "\\" + m.group(1), t)
    t = re.sub(r"\\left\(x\\right\)(?!')", "x", t)
    t = re.sub(r"\\left\((\d+)\\right\)\^", r"\1^", t)
    t = re.sub(r"\\left\((-?\d+)\\right\)(?!\^)", r"(\1)", t)
    t = re.sub(r"\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{1\}", r"\1", t)
    return no_repeat(t)
def parts(prob, chunks, pre=()):
    """Solution laid out the way the problem is: the problem's own ក. ខ. headers over each chunk.
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
def B(t):
    return "\\boxed{" + t + "}"
def L(N): return "y" if N == "y" else N + "(x)"
def D(N): return "y'" if N == "y" else N + "'(x)"
def D2(N): return "y''" if N == "y" else N + "''(x)"
def Dat(N, a): return ("y'(" if N == "y" else N + "'(") + lx(a) + ")"
def nz(r, lo, hi):
    while True:
        v = r.randint(lo, hi)
        if v: return v
def pos(r, hi=6): return r.randint(1, hi)
def lin(r, big=False):
    a = r.choice([1, 1, 1, 2, 2, 3, -1, -2, 3, 4] + ([5, -3, 6] if big else []))
    return a * x + nz(r, -7, 7)
def monic(r): return x + nz(r, -6, 6)
def quad(r):
    return r.choice([1, 1, 2, 3, -1, -2]) * x**2 + r.randint(-5, 5) * x + nz(r, -6, 6)
def cubic(r):
    return r.choice([1, 1, 2, -1]) * x**3 + r.randint(-3, 3) * x**2 + nz(r, -5, 5) * x + r.randint(-4, 4)
def posquad(r):
    """quadratic with no real root, positive everywhere"""
    while True:
        b, c = r.randint(-4, 4), r.randint(1, 9)
        if b * b - 4 * c < 0:
            return x**2 + b * x + c
def rootlat(v): return lx(v)
def lin_sq(r):
    """ax+b under a root, with enough of the domain inside [-4,4] (the verifier samples there)"""
    while True:
        w = lin(r)
        r0 = -w.coeff(x, 0) / w.coeff(x, 1)
        if (w.coeff(x, 1) > 0 and r0 <= 1) or (w.coeff(x, 1) < 0 and r0 >= -1):
            return w
def sent(*a): return " ".join(a)

CONC = ["ដូចនេះ", "ដូចនេះ", "ដូចនេះ", "ដូចនេះ", "សរុបមក", "ដូចនេះ យើងបាន", "ដូចនេះ គេបាន"]
def conc(r, t):
    return r.choice(CONC) + " $" + B(t) + "$ ។"
THEN = ["យើងបាន", "គេបាន", "នោះ", "នោះគេបាន", "យើងទទួលបាន"]
SIMP = ["សម្រួលកន្សោម គេបាន", "ពន្លាតភាគយក រួចបង្រួម យើងបាន", "បន្ទាប់ពីសម្រួល គេបាន", "បង្រួមតួដូចគ្នា យើងបាន"]
R_SUM = ["តាមរូបមន្តដេរីវេនៃផលបូក និងរូបមន្ត $(x^n)'=nx^{n-1}$", "ធ្វើដេរីវេតាមតួនីមួយៗ ដោយប្រើ $(x^n)'=nx^{n-1}$",
         "ដេរីវេនៃផលបូកស្មើនឹងផលបូកនៃដេរីវេ ហើយ $(x^n)'=nx^{n-1}$ ដូច្នេះ", "ប្រើរូបមន្ត $(ku)'=ku'$ និង $(x^n)'=nx^{n-1}$ លើតួនីមួយៗ"]
R_PROD = ["តាមរូបមន្តដេរីវេនៃផលគុណ $(uv)'=u'v+uv'$", "អនុគមន៍នេះជាផលគុណនៃអនុគមន៍ពីរ ដូច្នេះយើងប្រើរូបមន្ត $(uv)'=u'v+uv'$",
          "ប្រើរូបមន្តផលគុណ $(uv)'=u'v+uv'$", "ដោយ $(uv)'=u'v+uv'$"]
R_QUOT = ["តាមរូបមន្តដេរីវេនៃផលចែក $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$",
          "អនុគមន៍នេះជាផលចែក ដូច្នេះយើងប្រើរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$",
          "ប្រើរូបមន្តផលចែក $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$", "ដោយ $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$"]
R_POW = ["តាមរូបមន្ត $(u^n)'=nu'u^{n-1}$", "នេះជាអនុគមន៍បណ្ដាក់ ដូច្នេះយើងប្រើរូបមន្ត $(u^n)'=nu'u^{n-1}$",
         "ប្រើរូបមន្តដេរីវេនៃអនុគមន៍បណ្ដាក់ $(u^n)'=nu'u^{n-1}$", "ដោយ $(u^n)'=nu'u^{n-1}$"]
R_SQRT = ["តាមរូបមន្ត $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$", "ប្រើរូបមន្តដេរីវេនៃឫសការេ $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$",
          "នេះជាអនុគមន៍បណ្ដាក់ ដូច្នេះ $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ ផ្ដល់ឱ្យ", "ដោយ $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$"]

def setuv(r, u, v):
    du, dv = sp.diff(u, x), sp.diff(v, x)
    return r.choice([
        f"តាង $u={lx(u)}$ និង $v={lx(v)}$ នោះ $u'={lx(du)}$ និង $v'={lx(dv)}$ ។",
        f"យក $u={lx(u)}$ នោះ $u'={lx(du)}$ ហើយយក $v={lx(v)}$ នោះ $v'={lx(dv)}$ ។",
        f"តាង $u={lx(u)}$ , $v={lx(v)}$ យើងមាន $u'={lx(du)}$ , $v'={lx(dv)}$ ។"])

def dom_all(r, N, kind="ពហុធា"):
    return r.choice([f"អនុគមន៍{kind}កំណត់ចំពោះគ្រប់ $x\\in IR$ ។", f"ដែនកំណត់ $D=IR$ ។",
                     f"អនុគមន៍ ${N}$ មានដែនកំណត់ $D=IR$ ។", "" if kind == "ពហុធា" else "ដែនកំណត់ $D=IR$ ។"])
def dom_excl(r, N, v, roots):
    """v: denominator expression, roots: excluded values"""
    rs = ";".join(rootlat(t) for t in roots)
    cond = (f"$x\\neq{rootlat(roots[0])}$" if len(roots) == 1 else
            " និង ".join(f"$x\\neq{rootlat(t)}$" for t in roots))
    return r.choice([f"អនុគមន៍ ${N}$ កំណត់លុះត្រាតែ ${lx(v)}\\neq0$ ឬ {cond} ។ ដូចនេះ $D=IR-\\{{{rs}\\}}$ ។",
                     f"ដែនកំណត់៖ ${lx(v)}\\neq0$ ឬ {cond} នាំឱ្យ $D=IR-\\{{{rs}\\}}$ ។",
                     f"ភាគបែងត្រូវខុសពីសូន្យ គឺ {cond} ។ ដូចនេះ $D=IR-\\{{{rs}\\}}$ ។"])
def dom_ge(r, N, u, cond, dset):
    return r.choice([f"អនុគមន៍ ${N}$ កំណត់លុះត្រាតែ ${lx(u)}\\geq0$ ឬ {cond} ។ ដូចនេះ $D={dset}$ ។",
                     f"ដែនកំណត់៖ ${lx(u)}\\geq0$ មានន័យថា {cond} ដូចនេះ $D={dset}$ ។",
                     f"លក្ខខណ្ឌ ${lx(u)}\\geq0$ ឱ្យ {cond} ដូចនេះ $D={dset}$ ។"])

def lin_ge(u):
    """u=ax+b: returns (cond latex in $..$, D latex, boundary, derivative-domain latex)"""
    a, b = u.coeff(x, 1), u.coeff(x, 0)
    r0 = -b / a
    if a > 0:
        return f"$x\\geq{lx(r0)}$", f"\\left[{lx(r0)};+\\infty\\right)", r0, f"x>{lx(r0)}"
    return f"$x\\leq{lx(r0)}$", f"\\left(-\\infty;{lx(r0)}\\right]", r0, f"x<{lx(r0)}"

def S(fam, f, fl, d, dl, steps, dom="", diff="medium", ratio=True):
    return dict(fam=fam, f=f, fl=fl, d=d, dl=dl, steps=[t for t in steps if t], dom=dom, diff=diff, ratio=ratio)

# ---------- derivative families: each returns the worked derivative of one function ----------
def fam_poly(r, N):
    deg = r.randint(2, 7)
    exps = sorted(r.sample(range(0, deg), min(r.randint(1, 3), deg)) + [deg], reverse=True)
    style = r.randrange(3)
    co = []
    for e in exps:
        if style == 2 and e >= 2:
            c = R(nz(r, -5, 5), r.choice([2, 3, e, e + 1]))
        else:
            c = sp.Integer(nz(r, -9, 9))
        co.append(c)
    f = sum(c * x**e for c, e in zip(co, exps))
    d = sp.diff(f, x)
    terms = "+".join(par(c * x**e) + "'" for c, e in zip(co, exps))
    steps = [dom_all(r, N), sent(r.choice(R_SUM), r.choice(THEN) + " ៖"), f"$${D(N)}={terms}$$", f"$$={lx(d)}$$"]
    if r.random() < .4: steps.pop(2); steps[-1] = f"$${D(N)}={lx(d)}$$"
    return S("polynomial", f, lx(f), d, lx(d), steps, diff="easy")

def fam_power(r, N):
    pool = [(1, R(1, 2)), (1, -1), (1, -2), (1, -3), (1, R(-1, 2)), (1, 2), (1, 3), (1, 4), (1, R(3, 2)), (1, R(1, 3)), (1, R(2, 3)), (1, 1)]
    ts = r.sample(pool, r.randint(2, 3))
    ts = sorted(ts, key=lambda t: -t[1])
    co = [nz(r, -6, 6) for _ in ts]
    f = sum(c * x**e for c, (_, e) in zip(co, ts))
    d = sum(c * e * x**(e - 1) for c, (_, e) in zip(co, ts))
    rew = ""
    for i, (c, (_, e)) in enumerate(zip(co, ts)):
        sign = "-" if c < 0 else ("+" if i else "")
        ca = "" if abs(c) == 1 else str(abs(c))
        rew += sign + ca + ("x" if e == 1 else "x^{" + lx(e) + "}")
    raw = ""
    for i, (c, (_, e)) in enumerate(zip(co, ts)):
        cc = sp.Integer(c) * e
        ee = e - 1
        sign = "-" if cc < 0 else ("+" if i else "")
        ca = lx(abs(cc))
        raw += sign + (ca if (abs(cc) != 1 or ee == 0) else "") + ("" if ee == 0 else ("x" if ee == 1 else "x^{" + lx(ee) + "}"))
    neg = any(e < 0 for _, e in ts); frac = any(not sp.Integer(e).is_integer if isinstance(e, int) else not e.is_integer for _, e in ts)
    if frac and neg:
        dom = r.choice(["ដែនកំណត់ $D=(0;+\\infty)$ ដែលគ្រប់តួកំណត់ និងមានដេរីវេ ។", "អនុគមន៍នេះមានន័យលើ $D=(0;+\\infty)$ ។"])
    elif frac:
        dom = r.choice(["ដែនកំណត់ $D=[0;+\\infty)$ ហើយដេរីវេមានចំពោះ $x>0$ ។", "អនុគមន៍នេះមានន័យលើ $D=[0;+\\infty)$ និងមានដេរីវេចំពោះ $x>0$ ។"])
    elif neg:
        dom = "អនុគមន៍នេះកំណត់លុះត្រាតែ $x\\neq0$ ។ ដូចនេះ $D=IR-\\{0\\}$ ។"
    else:
        dom = "ដែនកំណត់ $D=IR$ ។"
    steps = [dom, r.choice(["គេអាចសរសេរជារាងស្វ័យគុណ ៖", "សរសេរ", "ប្ដូរឫស និងភាគបែងទៅជានិទស្សន្ត ៖"]) + f" $${L(N)}={rew}$$",
             sent(r.choice(["តាមរូបមន្ត $(x^n)'=nx^{n-1}$ ដែលពិតចំពោះនិទស្សន្តសនិទានផងដែរ", "ប្រើរូបមន្ត $(x^n)'=nx^{n-1}$ លើតួនីមួយៗ"]), r.choice(THEN) + " ៖"),
             f"$${D(N)}={raw}$$", "សរសេរវិញដោយគ្មាននិទស្សន្តអវិជ្ជមាន ៖" if any(e < 1 for _, e in ts) else "", f"$${D(N)}={lx(d)}$$"]
    return S("power_radical_sum", f, lx(f), d, lx(d), steps, diff="easy", ratio=False)

def fam_prod(r, N):
    A = [lin, quad, lambda q: x**2 + nz(q, -5, 5), cubic, lambda q: x**3 + nz(q, -5, 5)]
    u, v = r.choice(A)(r), r.choice(A[:3])(r)
    f = u * v
    du, dv = sp.diff(u, x), sp.diff(v, x)
    p1, p2 = sp.expand(du * v), sp.expand(u * dv)
    e = sp.expand(p1 + p2)
    k = r.randrange(4)
    if k == 3:
        steps = [dom_all(r, N), r.choice(["ពន្លាតផលគុណជាមុនសិន ៖", "ដើម្បីងាយស្រួល យើងពន្លាតកន្សោម ៖"]) + f" $${L(N)}={lx(sp.expand(f))}$$",
                 sent(r.choice(R_SUM), r.choice(THEN) + " ៖"), f"$${D(N)}={lx(e)}$$"]
    else:
        steps = [dom_all(r, N), r.choice(R_PROD) + " ។" if k == 0 else "", setuv(r, u, v) if k < 2 else "",
                 r.choice(R_PROD) + " " + r.choice(THEN) + " ៖" if k else "គេបាន ៖",
                 f"$${D(N)}={par(u)}'{par(v)}+{par(u)}{par(v)}'$$" if k == 2 else "",
                 f"$${'' if k == 2 else D(N)}={cx(du)}{par(v)}+{cx(dv)}{par(u)}$$",
                 f"$$={par(p1)}+{par(p2)}$$", f"$$={lx(e)}$$"]
    return S("product_poly", f, par(u) + par(v), e, lx(e), steps, diff="easy")

def rat_body(r, N, u, v, vl=None, recip=False):
    du, dv = sp.diff(u, x), sp.diff(v, x)
    vl = vl or par(v)
    num = sp.expand(du * v - u * dv)
    fd = sp.factor(num / v**2)
    return du, dv, num, fd, [
        f"$${D(N)}=\\frac{{{par(u)}'{par(v)}-{par(u)}{par(v)}'}}{{{vl}^2}}$$" if r.random() < .5 else "",
        f"$${D(N)}=\\frac{{{cx(du)}{par(v)}-{cx(dv)}{par(u)}}}{{{vl}^2}}$$",
        r.choice(SIMP) + " ៖", f"$${D(N)}=\\frac{{{lx(num)}}}{{{vl}^2}}$$"]

def quot_common(r, N, u, v, dom, fam, diff="medium"):
    f = u / v
    du, dv, num, fd, body = rat_body(r, N, u, v)
    last = []
    if lx(fd) != lx(num / v**2) and sp.Poly(num, x).degree() >= 1 and sp.factor(num) != num:
        last = [r.choice(["ដាក់ភាគយកជាផលគុណកត្តា ៖", "បំបែកជាកត្តា យើងបាន ៖"]) + f" $${D(N)}={lx(fd)}$$"]
    k = r.randrange(3)
    steps = [dom, r.choice(R_QUOT) + " ។" if k == 0 else "", setuv(r, u, v) if k != 1 else "",
             r.choice(R_QUOT) + " " + r.choice(THEN) + " ៖" if k else r.choice(THEN) + " ៖"] + body + last
    fl = "\\frac{" + lx(u) + "}{" + lx(v) + "}"
    return S(fam, f, fl, fd, lx(fd), steps, diff=diff)

def fam_linlin(r, N):
    while True:
        u, v = lin(r, True), lin(r, True)
        a, b, c, d_ = u.coeff(x, 1), u.coeff(x, 0), v.coeff(x, 1), v.coeff(x, 0)
        if a * d_ - b * c != 0: break
    r0 = -d_ / c
    dom = dom_excl(r, N, v, [r0])
    if r.random() < .3:
        det = a * d_ - b * c
        f = u / v
        d = det / v**2
        form = "\\left(\\frac{ax+b}{cx+d}\\right)'=\\frac{ad-bc}{(cx+d)^2}"
        steps = [dom, f"ប្រើរូបមន្តរហ័ស ${form}$ ដែលមានប្រភពពីរូបមន្តផលចែក ។ នៅទីនេះ $a={a}$ , $b={b}$ , $c={c}$ , $d={d_}$ ។ {r.choice(THEN)} ៖",
                 f"$${D(N)}=\\frac{{({a})({d_})-({b})({c})}}{{{par(v)}^2}}=\\frac{{{det}}}{{{par(v)}^2}}$$"]
        return S("quotient_lin_lin", f, "\\frac{" + lx(u) + "}{" + lx(v) + "}", d, f"\\frac{{{det}}}{{{par(v)}^2}}", steps, diff="easy")
    return quot_common(r, N, u, v, dom, "quotient_lin_lin", "easy")

def fam_qlin(r, N):
    while True:
        rt = nz(r, -5, 5); c0 = r.choice([1, 1, 2, -1]); be = r.randint(-5, 5); ga = nz(r, -9, 9)
        v = x - rt
        Q = c0 * x + be
        u = sp.expand(Q * v + ga)
        break
    dom = dom_excl(r, N, v, [rt])
    if r.random() < .35:
        f = u / v
        d = c0 - ga / v**2
        fd = sp.factor(d)
        steps = [dom, r.choice(["ចែកភាគយកនឹងភាគបែង សរសេរជារាងកាណូនិក ៖", "សរសេរ", "ដោយចែកពហុធា យើងបាន ៖"]) + f" $${L(N)}={lx(Q)}{'+' if ga>0 else '-'}\\frac{{{abs(ga)}}}{{{lx(v)}}}$$",
                 r.choice(["តាមរូបមន្ត $\\left(\\frac{1}{v}\\right)'=-\\frac{v'}{v^2}$ គេបាន ៖", "ធ្វើដេរីវេតាមតួ ដោយប្រើ $\\left(\\frac{1}{v}\\right)'=-\\frac{v'}{v^2}$ ៖"]),
                 f"$${D(N)}={c0}{'-' if ga>0 else '+'}\\frac{{{abs(ga)}}}{{{par(v)}^2}}$$",
                 "យកភាគបែងរួម ៖", f"$${D(N)}={lx(fd)}$$"]
        return S("quotient_quad_lin", f, "\\frac{" + lx(u) + "}{" + lx(v) + "}", fd, lx(fd), steps)
    return quot_common(r, N, u, v, dom, "quotient_quad_lin")

def fam_lquad(r, N):
    u = lin(r)
    k = r.randrange(3)
    if k == 0:
        v = x**2 + pos(r, 9); dom = dom_all(r, N, "សនិទាន") ; 
        dom = sent(f"ដោយ ${lx(v)}>0$ ចំពោះគ្រប់ $x$ នោះ", "$D=IR$ ។")
    elif k == 1:
        v = posquad(r); dom = sent(f"ភាគបែង ${lx(v)}$ មាន $\\Delta<0$ ហើយវិជ្ជមានជានិច្ច ដូចនេះ $D=IR$ ។")
    else:
        a, b = r.sample([-4, -3, -2, -1, 1, 2, 3, 4, 5], 2); a, b = min(a, b), max(a, b)
        v = sp.expand((x - a) * (x - b)); dom = dom_excl(r, N, v, [a, b])
    if sp.gcd(u, v) != 1: return fam_lquad(r, N)
    return quot_common(r, N, u, v, dom, "quotient_lin_quad")

def fam_qquad(r, N):
    u = r.choice([quad, lambda q: x**2 + nz(q, -6, 6)])(r)
    if r.random() < .5:
        v = x**2 + pos(r, 8); dom = f"ភាគបែង ${lx(v)}$ វិជ្ជមានជានិច្ច ដូចនេះ $D=IR$ ។"
    else:
        a, b = r.sample([-3, -2, -1, 1, 2, 3, 4], 2); a, b = min(a, b), max(a, b)
        v = sp.expand((x - a) * (x - b)); dom = dom_excl(r, N, v, [a, b])
    if sp.gcd(u, v) != 1: return fam_qquad(r, N)
    return quot_common(r, N, u, v, dom, "quotient_quad_quad", "medium")

def fam_recip(r, N):
    k = nz(r, -8, 8)
    v = r.choice([quad, lambda q: x**2 + pos(q, 8), lin])(r)
    if sp.LC(v, x) < 0: v = -v
    if sp.degree(v, x) == 1:
        rts = [-v.coeff(x, 0) / v.coeff(x, 1)]
    else:
        rts = sp.Poly(v, x).ground_roots()
        disc = sp.discriminant(v, x)
        if disc > 0 and len(rts) != 2: return fam_recip(r, N)
        rts = sorted(rts.keys()) if disc >= 0 else []
    dom = dom_excl(r, N, v, rts) if rts else f"ដោយ ${lx(v)}\\neq0$ ចំពោះគ្រប់ $x$ នោះ $D=IR$ ។"
    dv = sp.diff(v, x)
    f = k / v
    d = sp.factor(-k * dv / v**2)
    steps = [dom, r.choice(["តាមរូបមន្ត $\\left(\\frac{1}{v}\\right)'=-\\frac{v'}{v^2}$ និង $(ku)'=ku'$ គេបាន ៖", "ដោយភាគយកជាចំនួនថេរ យើងប្រើរូបមន្ត $\\left(\\frac{k}{v}\\right)'=-\\frac{kv'}{v^2}$ ៖"]),
             f"$${D(N)}=-\\frac{{{k if k > 0 else '(' + str(k) + ')'}{'' if dv == 1 else chr(92) + 'cdot' + pa(dv)}}}{{{par(v)}^2}}$$",
             f"$$={lx(d)}$$"]
    return S("reciprocal", f, "\\frac{" + str(k) + "}{" + lx(v) + "}" if k > 0 else "-\\frac{" + str(-k) + "}{" + lx(v) + "}", d, lx(d), steps, diff="easy")

def inner_poly(r):
    return r.choice([lin, lin, lambda q: x**2 + nz(q, -6, 6), quad, lambda q: x**3 + nz(q, -4, 4) * x + q.randint(-3, 3),
                     lambda q: q.choice([1, 2, 3]) * x**2 + nz(q, -5, 5) * x])(r)

def contentform(n, du):
    """n*du as (integer content, primitive part) for tidy display"""
    c, pp = sp.Poly(n * du, x).primitive()
    pe = pp.as_expr()
    if pe.coeff(x, sp.degree(pe, x)) < 0: c, pe = -c, -pe
    return c, pe

def fam_chainpow(r, N):
    u = inner_poly(r); n = r.randint(2, 9); k = r.choice([1, 1, 1, 1, 2, 3, -1, -2])
    du = sp.diff(u, x)
    f = k * u**n
    c, pp = contentform(k * n, du)
    tail = par(u) + (f"^{{{n-1}}}" if n > 2 else "")
    pre = ("" if c == 1 else "-" if c == -1 else str(c)) + ("" if pp == 1 else par(pp))
    dl = pre + tail
    d = c * pp * u**(n - 1)
    kf = "" if k == 1 else "-" if k == -1 else str(k)
    fl = kf + par(u) + f"^{{{n}}}"
    steps = [dom_all(r, N) if r.random() < .3 else "", f"{r.choice(R_POW)} ដោយ $u={lx(u)}$ និង $u'={lx(du)}$ {r.choice(THEN)} ៖",
             f"$${D(N)}={k*n}{par(u)}'{par(u)}^{{{n-1}}}$$" if r.random() < .6 else "",
             f"$${D(N)}={nm(k*n, du)}{par(u)}^{{{n-1}}}$$" , f"$$={dl}$$"]
    return S("chain_power", f, fl, d, dl, steps, diff="easy" if sp.degree(u, x) == 1 else "medium", ratio=True)

def sqrt_inner(r):
    """returns u, condition sentence maker, derivative-domain note"""
    k = r.randrange(4)
    if k < 2:
        return lin_sq(r)
    if k == 2:
        return r.choice([1, 1, 2, 3]) * x**2 + pos(r, 9)
    return posquad(r)

def dom_sqrt(r, N, u):
    if sp.degree(u, x) == 1:
        cond, dset, r0, dd = lin_ge(u)
        return dom_ge(r, N, u, cond, dset) + r.choice([f" អនុគមន៍មានដេរីវេចំពោះ ${dd}$ ។", f" ដេរីវេមានចំពោះ ${dd}$ ។"]), dd
    return f"ដោយ ${lx(u)}>0$ ចំពោះគ្រប់ $x$ នោះ $D=IR$ ។", "x\\in IR"

def fam_sqrt(r, N):
    u = sqrt_inner(r); k = r.choice([1, 1, 1, 2, 3, -1, 4])
    du = sp.diff(u, x)
    f = k * SQ(u)
    dom, _ = dom_sqrt(r, N, u)
    kf = "" if k == 1 else "-" if k == -1 else str(k)
    fl = kf + "\\sqrt{" + lx(u) + "}"
    cf = R(k, 2) * du                       # numerator over sqrt(u)
    n_, d_ = sp.fraction(sp.together(cf))
    d = n_ / (d_ * SQ(u))
    den = ("" if d_ == 1 else str(d_)) + "\\sqrt{" + lx(u) + "}"
    dl = "\\frac{" + lx(n_) + "}{" + den + "}"
    steps = [dom, f"{r.choice(R_SQRT)} ៖", f"$${D(N)}={kf}\\frac{{{par(u)}'}}{{2\\sqrt{{{lx(u)}}}}}$$",
             f"$$={kf}\\frac{{{lx(du)}}}{{2\\sqrt{{{lx(u)}}}}}$$", f"$$={dl}$$"]
    if lx(n_) == lx(du) and k == 1 and d_ == 2: steps.pop()
    return S("chain_sqrt", f, fl, d, dl, steps, diff="easy" if sp.degree(u, x) == 1 else "medium", ratio=False)

def fam_invpow(r, N):
    u = r.choice([lin, lambda q: x**2 + pos(q, 8), posquad])(r); n = r.randint(2, 5); k = nz(r, -6, 6)
    du = sp.diff(u, x)
    f = k / u**n
    if sp.degree(u, x) == 1:
        r0 = -u.coeff(x, 0) / u.coeff(x, 1); dom = dom_excl(r, N, u, [r0])
    else:
        dom = f"ដោយ ${lx(u)}>0$ ជានិច្ច នោះ $D=IR$ ។"
    c, pp = contentform(-k * n, du)
    d = c * pp / u**(n + 1)
    num = (str(abs(c)) if abs(c) != 1 or pp == 1 else "") + ("" if pp == 1 else pa(pp))
    sg = "-" if c < 0 else ""
    dl = f"{sg}\\frac{{{num}}}{{{par(u)}^{{{n+1}}}}}"
    fl = ("-" if k < 0 else "") + f"\\frac{{{abs(k)}}}{{{par(u)}^{{{n}}}}}"
    steps = [dom, r.choice(["សរសេរជារាងស្វ័យគុណអវិជ្ជមាន ៖", "គេអាចសរសេរ", "ប្ដូរទៅជានិទស្សន្តអវិជ្ជមាន ៖"]) + f" $${L(N)}={kd(k)}{par(u)}^{{-{n}}}$$",
             f"{r.choice(R_POW)} ដែល $n=-{n}$ {r.choice(THEN)} ៖",
             f"$${D(N)}={'' if k == 1 else f'({k})'}(-{n}){'' if du == 1 else chr(92) + 'cdot ' + pa(du)}{par(u)}^{{-{n+1}}}$$", f"$$={dl}$$"]
    return S("chain_inverse_power", f, fl, d, dl, steps, ratio=True)

def fam_prodpows(r, N):
    u, v = lin(r), lin(r)
    if sp.simplify(u - v) == 0 or sp.diff(u,x)*v == sp.diff(v,x)*u: return fam_prodpows(r, N)
    m, n = r.randint(2, 5), r.randint(2, 4)
    a, c = sp.diff(u, x), sp.diff(v, x)
    f = u**m * v**n
    br = sp.expand(m * a * v + n * c * u)
    cc, pp = sp.Poly(br, x).primitive()
    pe = pp.as_expr()
    d = cc * pe * u**(m - 1) * v**(n - 1)
    pw = lambda b, e: par(b) + ("" if e == 1 else f"^{{{e}}}")
    dl = ("" if cc == 1 else str(cc)) + pw(u, m - 1) + pw(v, n - 1) + par(pe)
    steps = [dom_all(r, N, ""), f"{r.choice(R_PROD)} ជាមួយនឹង $(u^n)'=nu'u^{{n-1}}$ {r.choice(THEN)} ៖",
             f"$${D(N)}={m}{'' if a == 1 else f'({a})'}{pw(u,m-1)}{pw(v,n)}+{pw(u,m)}\\cdot{n}{'' if c == 1 else f'({c})'}{pw(v,n-1)}$$",
             r.choice(["ដាក់កត្តារួម", "យកកត្តារួម"]) + f" ${pw(u,m-1)}{pw(v,n-1)}$ ៖",
             f"$${D(N)}={pw(u,m-1)}{pw(v,n-1)}\\left[{m*a}{par(v)}+{n*c}{par(u)}\\right]$$".replace("+-", "-"),
             f"$$={dl}$$"]
    return S("product_of_powers", f, pw(u, m) + pw(v, n), d, dl, steps, ratio=True)

def fam_linsqrt(r, N):
    w = lin_sq(r); p = r.choice([x, x, x + nz(r, -4, 4), 2 * x + nz(r, -3, 3), x**2])
    if p == x**2 and r.random() < .5: p = x
    dp, a = sp.diff(p, x), sp.diff(w, x)
    f = p * SQ(w)
    num = sp.expand(2 * dp * w + a * p)
    d = num / (2 * SQ(w))
    cond, dset, r0, dd = lin_ge(w)
    cc, pp = sp.Poly(num, x).primitive()
    g = sp.gcd(cc, 2)
    nl = lx(num / g) ; dn = str(2 // g) if g != 2 else ""
    dl = "\\frac{" + nl + "}{" + dn + "\\sqrt{" + lx(w) + "}}"
    sw = "\\sqrt{" + lx(w) + "}"
    steps = [dom_ge(r, N, w, cond, dset) + f" អនុគមន៍មានដេរីវេចំពោះ ${dd}$ ។",
             f"{r.choice(R_PROD)} ដោយ $u={lx(p)}$ និង $v={sw}$ ។ យើងមាន $u'={lx(dp)}$ និង $v'=\\frac{{{lx(a)}}}{{2{sw}}}$ ។ {r.choice(THEN)} ៖",
             f"$${D(N)}={cx(dp)}{sw}+{pa(p)}\\cdot\\frac{{{lx(a)}}}{{2{sw}}}$$",
             r.choice(["ធ្វើភាគបែងរួម ៖", "យកភាគបែងរួម $2\\sqrt{" + lx(w) + "}$ ៖"]),
             f"$$=\\frac{{{cx(2*dp)}{par(w)}+{cx(a)}{pa(p)}}}{{2{sw}}}$$", f"$$={dl}$$"]
    return S("product_radical", f, (lx(p) if p == x or p == x**2 else par(p)) + sw, d, dl, steps, ratio=False)

def fam_quadsqrt(r, N):
    c = pos(r, 9); w = x**2 + c
    p = r.choice([x, x, x + nz(r, -4, 4), 2 * x + nz(r, -3, 3)])
    dp = sp.diff(p, x)
    f = p * SQ(w)
    num = sp.expand(dp * w + x * p)
    d = num / SQ(w)
    sw = "\\sqrt{" + lx(w) + "}"
    dl = "\\frac{" + lx(num) + "}{" + sw + "}"
    steps = [f"ដោយ ${lx(w)}>0$ ចំពោះគ្រប់ $x$ នោះ $D=IR$ ។",
             f"{r.choice(R_PROD)} ។ ម្យ៉ាងទៀត $({sw})'=\\frac{{2x}}{{2{sw}}}=\\frac{{x}}{{{sw}}}$ ។ {r.choice(THEN)} ៖",
             f"$${D(N)}={cx(dp)}{sw}+{pa(p)}\\cdot\\frac{{x}}{{{sw}}}$$",
             f"$$=\\frac{{{cx(dp)}{par(w)}+{'x^{2}' if p == x else 'x' + par(p)}}}{{{sw}}}$$", f"$$={dl}$$"]
    return S("product_radical", f, (lx(p) if p == x else par(p)) + sw, d, dl, steps, ratio=False)

def fam_linoversqrt(r, N):
    c = pos(r, 9); w = r.choice([x**2 + c, x**2 + c, posquad(r)])
    p = r.choice([x, 2 * x + nz(r, -3, 3), x + nz(r, -4, 4), sp.Integer(nz(r, 2, 5))])
    dp, dw = sp.diff(p, x), sp.diff(w, x)
    sw = "\\sqrt{" + lx(w) + "}"
    f = p / SQ(w)
    num = sp.expand(2 * dp * w - p * dw)
    cc = sp.Poly(num, x).content() if num != 0 else 1
    g = sp.gcd(cc, 2)
    num2 = num / g; dn = 2 // g
    d = num2 / (dn * w * SQ(w))
    dl = "\\frac{" + lx(num2) + "}{" + ("" if dn == 1 else str(dn)) + par(w) + sw + "}"
    steps = [f"ដោយ ${lx(w)}>0$ ជានិច្ច នោះ $D=IR$ ។",
             f"{r.choice(R_QUOT)} ជាមួយ $u={lx(p)}$ , $v={sw}$ ។ យើងមាន $u'={lx(dp)}$ , $v'=\\frac{{{lx(dw)}}}{{2{sw}}}$ ។ {r.choice(THEN)} ៖",
             f"$${D(N)}=\\frac{{{(cx(dp) + sw) if dp != 0 else ''}-{pa(p)}\\cdot\\frac{{{lx(dw)}}}{{2{sw}}}}}{{{lx(w)}}}$$",
             r.choice(["គុណភាគយក និងភាគបែងនឹង", "សម្រួលដោយគុណទាំងភាគយក ទាំងភាគបែងនឹង"]) + f" $2{sw}$ ៖",
             f"$$=\\frac{{{(cx(2*dp) + par(w)) if dp != 0 else ''}-{pa(p)}{pa(dw)}}}{{2{par(w)}{sw}}}$$",
             f"$$=\\frac{{{lx(num)}}}{{2{par(w)}{sw}}}$$", f"$$={dl}$$"]
    return S("quotient_radical", f, "\\frac{" + lx(p) + "}{" + sw + "}", d, dl, steps, diff="hard", ratio=False)

def fam_sqrtoverlin(r, N):
    t = pos(r, 6)
    v = x + t; p = pos(r, 4)
    # f = sqrt(px)/(x+t)? keep sqrt(x)
    f = SQ(x) / v
    num = t - x
    d = num / (2 * SQ(x) * v**2)
    dl = "\\frac{" + lx(num) + "}{2\\sqrt{x}" + par(v) + "^2}"
    steps = ["អនុគមន៍កំណត់លុះត្រាតែ $x\\geq0$ ។ ដូចនេះ $D=[0;+\\infty)$ ហើយដេរីវេមានចំពោះ $x>0$ ។",
             f"{r.choice(R_QUOT)} {r.choice(THEN)} ៖",
             f"$${D(N)}=\\frac{{\\frac{{1}}{{2\\sqrt{{x}}}}{par(v)}-\\sqrt{{x}}}}{{{par(v)}^2}}$$",
             "គុណភាគយក និងភាគបែងនឹង $2\\sqrt{x}$ ៖",
             f"$$=\\frac{{{lx(v)}-2x}}{{2\\sqrt{{x}}{par(v)}^2}}$$", f"$$={dl}$$"]
    return S("quotient_radical", f, "\\frac{\\sqrt{x}}{" + lx(v) + "}", d, dl, steps, diff="medium", ratio=False)

def fam_quotpow(r, N):
    while True:
        u, v = lin(r, True), lin(r, True)
        a, b, c, d_ = u.coeff(x, 1), u.coeff(x, 0), v.coeff(x, 1), v.coeff(x, 0)
        det = a * d_ - b * c
        if det: break
    n = r.randint(2, 6)
    f = (u / v)**n
    d = n * det * u**(n - 1) / v**(n + 1)
    r0 = -d_ / c
    nl = f"{n*det}" + par(u) + ("" if n == 2 else f"^{{{n-1}}}")
    dl = "\\frac{" + nl + "}{" + par(v) + f"^{{{n+1}}}" + "}"
    w = "\\frac{" + lx(u) + "}{" + lx(v) + "}"
    wp = f"\\frac{{{det}}}{{{par(v)}^2}}"
    steps = [dom_excl(r, N, v, [r0]),
             f"តាង $w={w}$ ។ {r.choice(R_QUOT)} គេបាន $w'={wp}$ ។",
             f"{r.choice(R_POW).replace('u', 'w')} {r.choice(THEN)} ៖",
             f"$${D(N)}={n}\\cdot{wp}\\cdot\\left({w}\\right)^{{{n-1}}}$$",
             f"$$={dl}$$"]
    return S("chain_of_quotient", f, "\\left(" + w + "\\right)^{" + str(n) + "}", d, dl, steps, diff="hard", ratio=True)

def fam_sqrtquot(r, N):
    a0, b0 = r.sample([-3, -2, -1, 1, 2, 3], 2)
    u, v = x + a0, x + b0
    det = b0 - a0
    f = SQ(u / v)
    lo, hi = sorted([-a0, -b0])
    excl_side = "\\left(-\\infty;" + lx(lo) + ("\\right]" if -a0 == lo else "\\right)") + "\\cup" + ("\\left[" if -a0 == hi else "\\left(") + lx(hi) + ";+\\infty\\right)"
    w = "\\frac{" + lx(u) + "}{" + lx(v) + "}"
    d = det / (2 * v**2 * SQ(u / v))
    dl = "\\frac{" + str(det) + "}{2" + par(v) + "^2\\sqrt{" + w + "}}"
    steps = [f"អនុគមន៍កំណត់លុះត្រាតែ ${w}\\geq0$ និង $x\\neq{-b0}$ ។ តាមសញ្ញានៃផលចែក គេបាន $D={excl_side}$ ។",
             f"តាង $w={w}$ នោះ $w'=\\frac{{{det}}}{{{par(v)}^2}}$ តាមរូបមន្តផលចែក ។",
             f"{r.choice(R_SQRT).replace('u', 'w')} ចំពោះ $w>0$ ៖", f"$${D(N)}=\\frac{{w'}}{{2\\sqrt{{w}}}}={dl}$$"]
    return S("chain_of_quotient", f, "\\sqrt{" + w + "}", d, dl, steps, diff="hard", ratio=False)

def fam_ratpow(r, N):
    c = pos(r, 9); p, q = r.choice([(1, 3), (2, 3), (3, 2), (4, 3), (5, 2), (3, 4), (5, 3)])
    u = r.choice([x**2 + c, 2 * x**2 + c, x**4 + c])
    e = R(p, q); du = sp.diff(u, x)
    f = u**e
    co = e * du
    d = co * u**(e - 1)
    steps = [f"ដោយ ${lx(u)}>0$ ជានិច្ច នោះ $D=IR$ ។",
             f"{r.choice(R_POW)} ដែលនៅទីនេះ $n={lx(e)}$ {r.choice(THEN)} ៖",
             f"$${D(N)}={lx(e)}\\cdot{par(du)}{par(u)}^{{{lx(e)}-1}}$$",
             f"$$={lx(co)}{par(u)}^{{{lx(e-1)}}}$$"]
    return S("chain_rational_exponent", f, par(u) + "^{" + lx(e) + "}", d, lx(co) + par(u) + "^{" + lx(e - 1) + "}", steps, ratio=False)

def fam_nested(r, N):
    c = pos(r, 9); n = r.randint(2, 4)
    s_ = SQ(x**2 + c); sw = "\\sqrt{" + lx(x**2 + c) + "}"
    if r.random() < .5:
        f = (x + s_)**n
        d = n * (x + s_)**n / s_
        dl = "\\frac{" + str(n) + "\\left(x+" + sw + "\\right)^{" + str(n) + "}}{" + sw + "}"
        steps = [f"ដោយ ${sw}>|x|$ កន្សោម $x+{sw}$ វិជ្ជមានជានិច្ច ហើយ $D=IR$ ។",
                 f"តាង $u=x+{sw}$ នោះ $u'=1+\\frac{{x}}{{{sw}}}=\\frac{{{sw}+x}}{{{sw}}}=\\frac{{u}}{{{sw}}}$ ។",
                 f"{r.choice(R_POW)} {r.choice(THEN)} ៖", f"$${D(N)}={n}\\cdot\\frac{{u}}{{{sw}}}\\cdot u^{{{n-1}}}=\\frac{{{n}u^{{{n}}}}}{{{sw}}}$$", f"$$={dl}$$"]
        return S("nested_radical", f, "\\left(x+" + sw + "\\right)^{" + str(n) + "}", d, dl, steps, diff="hard", ratio=False)
    f = SQ(x + s_)
    d = SQ(x + s_) / (2 * s_)
    dl = "\\frac{\\sqrt{x+" + sw + "}}{2" + sw + "}"
    steps = [f"ដោយ ${sw}>|x|$ កន្សោមក្រោមឫសវិជ្ជមានជានិច្ច ដូចនេះ $D=IR$ ។",
             f"តាង $u=x+{sw}$ នោះ $u'=\\frac{{u}}{{{sw}}}$ ។", f"{r.choice(R_SQRT)} ៖",
             f"$${D(N)}=\\frac{{u'}}{{2\\sqrt{{u}}}}=\\frac{{u}}{{2{sw}\\sqrt{{u}}}}=\\frac{{\\sqrt{{u}}}}{{2{sw}}}$$", f"$$={dl}$$"]
    return S("nested_radical", f, "\\sqrt{x+" + sw + "}", d, dl, steps, diff="hard", ratio=False)

def fam_mix(r, N):
    u = lin_sq(r); v = lin(r); p = r.choice([x**2, x**3, 2 * x, -x**2, 3 * x])
    while u.coeff(x,1) * v.coeff(x,0) == u.coeff(x,0) * v.coeff(x,1): v = lin(r)
    k = nz(r, -6, 6); sg = nz(r, -3, 3)
    a, b = sp.diff(u, x), sp.diff(v, x)
    f = p + sg * SQ(u) + k / v
    dd = sp.diff(p, x)
    cond, dset, r0, ddm = lin_ge(u)
    d = dd + R(sg, 2) * a / SQ(u) - k * b / v**2
    r1 = -v.coeff(x, 0) / v.coeff(x, 1)
    # solved domain; the root is differentiable only strictly inside, so the derivative needs u>0
    cnd = f"អនុគមន៍ ${N}$ កំណត់លុះត្រាតែ ${lx(u)}\\geq0$ និង ${lx(v)}\\neq0$ គឺ {cond} និង $x\\neq{lx(r1)}$ ។"
    if r1 == r0:
        dset = f"\\left({lx(r0)};+\\infty\\right)" if a > 0 else f"\\left(-\\infty;{lx(r0)}\\right)"
        dtxt = f"{cnd} ដូចនេះ $D={dset}$ ។"
    elif (a > 0 and r1 < r0) or (a < 0 and r1 > r0):
        dtxt = f"{cnd} ដោយ $x={lx(r1)}$ នៅក្រៅចន្លោះនេះ គេបាន $D={dset}$ ហើយដេរីវេមានចំពោះ ${ddm}$ ។"
    else:
        if a > 0:
            dset = f"\\left[{lx(r0)};{lx(r1)}\\right)\\cup\\left({lx(r1)};+\\infty\\right)"
        else:
            dset = f"\\left(-\\infty;{lx(r1)}\\right)\\cup\\left({lx(r1)};{lx(r0)}\\right]"
        dtxt = f"{cnd} ដូចនេះ $D={dset}$ ហើយដេរីវេមានចំពោះ ${ddm}$ និង $x\\neq{lx(r1)}$ ។"
    sgl = "+" if sg > 0 else "-"
    ks = "+" if k > 0 else "-"
    fl = lx(p) + sgl + ("" if abs(sg) == 1 else str(abs(sg))) + "\\sqrt{" + lx(u) + "}" + ks + "\\frac{" + str(abs(k)) + "}{" + lx(v) + "}"
    t2 = R(sg, 2) * a; t3 = -k * b
    term2 = ("+" if t2 > 0 else "-") + "\\frac{" + lx(sp.fraction(abs(t2))[0]) + "}{" + (str(sp.fraction(abs(t2))[1]) if sp.fraction(abs(t2))[1] != 1 else "") + "\\sqrt{" + lx(u) + "}}"
    term3 = ("+" if t3 > 0 else "-") + "\\frac{" + str(abs(t3)) + "}{" + par(v) + "^2}"
    dl = lx(dd) + term2 + term3
    steps = [dtxt, f"អនុគមន៍នេះជាផលបូកនៃបីតួ ។ យើងធ្វើដេរីវេមួយតួម្ដង ដោយប្រើ $(\\sqrt{{u}})'=\\frac{{u'}}{{2\\sqrt{{u}}}}$ និង $\\left(\\frac{{1}}{{v}}\\right)'=-\\frac{{v'}}{{v^2}}$ ៖",
             f"$$({lx(p)})'={lx(dd)}$$", f"$$\\left({'' if sg>0 else '-'}{'' if abs(sg)==1 else abs(sg)}\\sqrt{{{lx(u)}}}\\right)'={term2.lstrip('+')}$$",
             f"$$\\left({'' if k>0 else '-'}\\frac{{{abs(k)}}}{{{lx(v)}}}\\right)'={term3.lstrip('+')}$$",
             "បូកលទ្ធផលទាំងបី ៖", f"$${D(N)}={dl}$$"]
    return S("sum_of_mixed", f, fl, d, dl, steps, ratio=False)

FAMS = [(fam_poly, 8), (fam_power, 9), (fam_prod, 9), (fam_linlin, 8), (fam_qlin, 8), (fam_lquad, 7), (fam_qquad, 6), (fam_recip, 5),
        (fam_chainpow, 9), (fam_sqrt, 9), (fam_invpow, 6), (fam_prodpows, 6), (fam_linsqrt, 7), (fam_quadsqrt, 5), (fam_linoversqrt, 5),
        (fam_sqrtoverlin, 1), (fam_quotpow, 5), (fam_sqrtquot, 3), (fam_ratpow, 3), (fam_nested, 2), (fam_mix, 5)]
FAM_LIST = [f for f, w in FAMS for _ in range(w)]

SEEN = set()
ROWS = []
def fresh(key):
    k = str(key)
    if k in SEEN: return False
    SEEN.add(k); return True
def add(sub, diff, prob, sol, ans, checks, diagrams=None, png=None):
    row = make_row("rules", sub, diff, tidy(prob), tidy(sol), tidy(ans), checks, GEN, diagrams=diagrams)
    if png: row["_png"] = png
    ROWS.append(row)

# ---------- problem wording ----------
def intro(r, N, fl):
    Lh = L(N)
    return r.choice([f"គេឱ្យអនុគមន៍ ${Lh}={fl}$ ។", f"ឱ្យអនុគមន៍ ${N}$ កំណត់ដោយ ${Lh}={fl}$ ។" if N != "y" else f"ឱ្យអនុគមន៍ ${Lh}={fl}$ ។",
                     f"គេមានអនុគមន៍ ${Lh}={fl}$ ។", f"គេឱ្យអនុគមន៍កំណត់ដោយ ៖ $${Lh}={fl}$$", f"គេឱ្យអនុគមន៍ ${Lh}={fl}$ លើដែនកំណត់របស់វា ។", f"អនុគមន៍មួយកំណត់ដោយ ${Lh}={fl}$ ។"])
def ask_d(r, N, fl):
    Lh, Dh = L(N), D(N)
    return r.choice([
        f"គណនាដេរីវេនៃអនុគមន៍ ${Lh}={fl}$ ។", f"រកដេរីវេនៃអនុគមន៍ ${Lh}={fl}$ ។", f"ចូរគណនាដេរីវេនៃ ${Lh}={fl}$ ។",
        f"{intro(r,N,fl)} គណនា ${Dh}$ ។", f"{intro(r,N,fl)} ចូររកដេរីវេ ${Dh}$ ។", f"{intro(r,N,fl)} គណនា ${Dh}$ រួចសម្រួលលទ្ធផល ។",
        f"{intro(r,N,fl)} ចូរគណនាដេរីវេទី១ ។", f"{intro(r,N,fl)} រកដេរីវេនៃអនុគមន៍នេះ ។",
        f"{intro(r,N,fl)} ប្រើរូបមន្តដេរីវេ ដើម្បីគណនា ${Dh}$ ។", f"គណនាដេរីវេ ${Dh}$ ដោយដឹងថា ${Lh}={fl}$ ។"])

def join(steps): return "\n".join(steps)
def W_plain(r, s_, N):
    prob = ask_d(r, N, s_["fl"])
    sol = join(s_["steps"] + [conc(r, D(N) + "=" + s_["dl"])])
    add(s_["fam"], s_["diff"], prob, sol, D(N) + "=" + s_["dl"], [check(f"diff({s(s_['f'])},x)", s(s_["d"]), "derivative")])
def W_show(r, s_, N):
    prob = intro(r, N, s_["fl"]) + " " + r.choice([f"បង្ហាញថា ${D(N)}={s_['dl']}$ ។", f"ស្រាយបញ្ជាក់ថា ${D(N)}={s_['dl']}$ ។", f"ផ្ទៀងផ្ទាត់ថាដេរីវេនៃអនុគមន៍នេះគឺ ${D(N)}={s_['dl']}$ ។"])
    tail = r.choice([f"ដូចនេះ ${B(D(N)+'='+s_['dl'])}$ ដូចដែលត្រូវបង្ហាញ ។", f"នេះបញ្ជាក់ថា ${B(D(N)+'='+s_['dl'])}$ ពិតមែន ។", f"ដូចនេះ ${B(D(N)+'='+s_['dl'])}$ ។"])
    add(s_["fam"] + "_show", s_["diff"], prob, join(s_["steps"] + [tail]), D(N) + "=" + s_["dl"], [check(f"diff({s(s_['f'])},x)", s(s_["d"]), "derivative")])

def good_point(r, s_):
    pts = list(range(-3, 6)); r.shuffle(pts)
    for a in pts:
        try:
            v = s_["d"].subs(x, a); fv = s_["f"].subs(x, a)
            if v.has(sp.zoo, sp.nan, sp.oo, sp.I) or fv.has(sp.zoo, sp.nan, sp.I): continue
            if not v.is_rational or not fv.is_real: continue
            if s_["ratio"] is False and a == 0 and "fam_power" == s_["fam"]: continue
            if abs(v) > 2000 or sp.denom(v) > 2000: continue
            return a, v
        except Exception:
            continue
    return None
def subs_line(N, s_, a, v):
    n, dd = sp.fraction(sp.together(s_["d"]))
    na, da = n.subs(x, a), dd.subs(x, a)
    if da != 1 and na.is_rational and da.is_rational and da != 0:
        return f"$${Dat(N,a)}=\\frac{{{lx(na)}}}{{{lx(da)}}}={lx(v)}$$"
    return f"$${Dat(N,a)}={lx(v)}$$"
def W_point(r, s_, N):
    g = good_point(r, s_)
    if not g: return W_plain(r, s_, N)
    a, v = g
    prob = intro(r, N, s_["fl"]) + " " + r.choice([f"គណនា ${Dat(N,a)}$ ។", f"រកតម្លៃនៃដេរីវេត្រង់ $x={a}$ ។", f"គណនាដេរីវេនៃអនុគមន៍ត្រង់ចំណុច $x={a}$ ។",
                                                     f"ចូរគណនា ${D(N)}$ រួចទាញរកតម្លៃ ${Dat(N,a)}$ ។", f"តើដេរីវេនៃអនុគមន៍នេះត្រង់ $x={a}$ ស្មើនឹងប៉ុន្មាន ?"])
    two = "រួចទាញរកតម្លៃ" in prob
    sol = join(s_["steps"] + ([f"ដូចនេះ ${B(D(N) + '=' + s_['dl'])}$ ។"] if two else []) + [r.choice([f"ជំនួស $x={a}$ ក្នុង ${D(N)}$ ៖", f"ចំពោះ $x={a}$ យើងបាន ៖", f"ឥឡូវគណនាត្រង់ $x={a}$ ៖"]), subs_line(N, s_, a, v), conc(r, Dat(N, a) + "=" + lx(v))])
    add("derivative_at_point", s_["diff"] if s_["diff"] != "easy" else "medium", prob, sol, (D(N) + "=" + s_["dl"] + ",\\ " if two else "") + Dat(N, a) + "=" + lx(v),
        [check(f"diff({s(s_['f'])},x)", s(s_["d"]), "derivative"), check(f"subs(diff({s(s_['f'])},x),x,{a})", s(v), "value at point")])

KH = "កខគឃងច"
def W_drill(r, specs, N="f"):
    k = len(specs)
    names = ["f", "g", "h", "k", "p"][:k]
    head = r.choice(["គណនាដេរីវេនៃអនុគមន៍ខាងក្រោម ៖", "រកដេរីវេនៃអនុគមន៍នីមួយៗខាងក្រោម ៖", "ចូរគណនាដេរីវេទី១ នៃអនុគមន៍ខាងក្រោម ៖"])
    lines, sol, ans, chk = [head], [], [], []
    for i, (sp_, nm) in enumerate(zip(specs, names)):
        lines.append(f"{KH[i]}. ${L(nm)}={sp_['fl']}$")
        sol.append(f"{KH[i]}. គណនា ${D(nm)}$ ។")
        sol += sp_["steps"]
        sol.append(f"ដូចនេះ ${B(D(nm)+'='+sp_['dl'])}$ ។")
        ans.append(D(nm) + "=" + sp_["dl"])
        chk.append(check(f"diff({s(sp_['f'])},x)", s(sp_["d"]), f"part {i+1}"))
    add("drill_mixed", "medium", "\n".join(lines), join(sol), ",\\quad ".join(ans), chk)

# ---------- definition of the derivative ----------
h = sp.Symbol("h")
DEF_H = "f'(a)=\\lim_{h\\to0}\\frac{f(a+h)-f(a)}{h}"
DEF_X = "f'(a)=\\lim_{x\\to a}\\frac{f(x)-f(a)}{x-a}"
BYDEF = ["ដោយប្រើនិយមន័យ", "តាមនិយមន័យនៃដេរីវេ", "ដោយប្រើនិយមន័យនៃដេរីវេ (លីមីតនៃផលធៀប)"]
def t_def_point_h(r):
    f = r.choice([quad, cubic, lambda q: x**2 + nz(q, -5, 5) * x, lambda q: q.choice([1,2,3,-1]) * x**2 + nz(q, -6, 6)])(r); a = nz(r, -3, 4)
    if not fresh(("dph", f, a)): return
    fa = f.subs(x, a); fah = sp.expand(f.subs(x, a + h)); df = sp.expand(fah - fa); q_ = sp.expand(df / h); val = q_.subs(h, 0)
    prob = r.choice([f"{r.choice(BYDEF)} គណនាដេរីវេនៃអនុគមន៍ $f(x)={lx(f)}$ ត្រង់ $x={a}$ ។",
                     f"គេឱ្យ $f(x)={lx(f)}$ ។ {r.choice(BYDEF)} រកតម្លៃ $f'({a})$ ។",
                     f"គេមានអនុគមន៍ $f(x)={lx(f)}$ ។ គណនា $f'({a})$ ដោយប្រើលីមីត $\\lim_{{h\\to0}}\\frac{{f({a}+h)-f({a})}}{{h}}$ ។"])
    sol = [f"តាមនិយមន័យ ${DEF_H}$ ។", f"យើងមាន $f({a})={lx(fa)}$ ។", r.choice(["ហើយ", "ម្យ៉ាងទៀត", "គណនា"]) + f" $$f({a}+h)={lx(fah)}$$",
           f"នោះ $$f({a}+h)-f({a})={lx(df)}$$", r.choice(["ចែកនឹង $h$ ដោយ $h\\neq0$ ៖", "ចំពោះ $h\\neq0$ គេបាន ៖"]) + f" $$\\frac{{f({a}+h)-f({a})}}{{h}}={lx(q_)}$$",
           f"គេបាន $$f'({a})=\\lim_{{h\\to0}}\\left({lx(q_)}\\right)={lx(val)}$$", conc(r, f"f'({a})={lx(val)}")]
    add("definition_at_point", "medium", prob, join(sol), f"f'({a})={lx(val)}",
        [check(f"limit(({s(f.subs(x,a+x))}-({s(fa)}))/x,x,0)", s(val), "limit definition"), check(f"subs(diff({s(f)},x),x,{a})", s(val), "rule agrees")])

def t_def_point_x(r):
    a = nz(r, -3, 4); q = lin(r) if r.random() < .6 else quad(r)
    f = sp.expand((x - a) * q + nz(r, -5, 5))
    if not fresh(("dpx", f, a)): return
    fa = f.subs(x, a); val = q.subs(x, a); num = sp.expand(f - fa)
    prob = r.choice([f"គេឱ្យអនុគមន៍ $f(x)={lx(f)}$ ។ ដោយប្រើនិយមន័យ ${DEF_X}$ គណនា $f'({a})$ ។",
                     f"រកដេរីវេនៃ $f(x)={lx(f)}$ ត្រង់ចំណុច $x={a}$ ដោយគណនាលីមីតនៃផលធៀប $\\frac{{f(x)-f({a})}}{{{lx(x-a)}}}$ ។"])
    den = lx(x - a)
    sol = [f"យើងមាន $f({a})={lx(fa)}$ ។", "តាមនិយមន័យ ៖", f"$$f'({a})=\\lim_{{x\\to{a}}}\\frac{{f(x)-f({a})}}{{{den}}}=\\lim_{{x\\to{a}}}\\frac{{{lx(num)}}}{{{den}}}$$",
           r.choice(["លីមីតនេះមានរាងមិនកំណត់ $\\frac{0}{0}$ ។ ភាគយកមានឫស $x=" + str(a) + "$ ដូចនេះដាក់កត្តា ៖", "ដោយភាគយកស្មើសូន្យត្រង់ $x=" + str(a) + "$ យើងបំបែកកត្តា $" + den + "$ ៖"]),
           f"$${lx(num)}={par(x-a)}{par(q)}$$", f"សម្រួលកត្តា ${den}$ ចំពោះ $x\\neq{a}$ ៖", f"$$f'({a})=\\lim_{{x\\to{a}}}\\left({lx(q)}\\right)={lx(val)}$$", conc(r, f"f'({a})={lx(val)}")]
    add("definition_at_point", "medium", prob, join(sol), f"f'({a})={lx(val)}",
        [check(f"limit(({s(num)})/({s(x-a)}),x,{a})", s(val), "limit"), check(f"subs(diff({s(f)},x),x,{a})", s(val), "rule agrees")])

def t_def_general(r):
    f = r.choice([quad, lambda q: q.choice([1, 2, -1, 3]) * x**3 + nz(q, -5, 5) * x, lambda q: nz(q, -4, 5) * x**2 + nz(q, -5, 5), lambda q: x**3 + nz(q, -4, 4) * x**2])(r)
    if not fresh(("dg", f)): return
    fxh = sp.expand(f.subs(x, x + h)); df = sp.expand(fxh - f); q_ = sp.expand(df / h); d = q_.subs(h, 0)
    prob = r.choice([f"ដោយប្រើនិយមន័យ បង្ហាញថា ដេរីវេនៃ $f(x)={lx(f)}$ គឺ $f'(x)={lx(d)}$ ។", f"{r.choice(BYDEF)} គណនា $f'(x)$ ចំពោះគ្រប់ចំនួនពិត $x$ ដោយដឹងថា $f(x)={lx(f)}$ ។",
                     f"គេឱ្យ $f(x)={lx(f)}$ ។ គណនា $\\lim_{{h\\to0}}\\frac{{f(x+h)-f(x)}}{{h}}$ រួចសន្និដ្ឋានរក $f'(x)$ ។"])
    sol = ["ចំពោះ $x\\in IR$ និង $h\\neq0$ យើងគណនា ៖", f"$$f(x+h)={lx(fxh)}$$", f"$$f(x+h)-f(x)={lx(df)}$$", r.choice(["ចែកអង្គទាំងពីរនឹង $h$ ៖", "ចែកនឹង $h$ រួចសម្រួល ៖"]), f"$$\\frac{{f(x+h)-f(x)}}{{h}}={lx(q_)}$$",
           "ពេល $h\\to0$ តួដែលមាន $h$ ខិតជិតសូន្យ ដូច្នេះ ៖", f"$$f'(x)=\\lim_{{h\\to0}}\\left({lx(q_)}\\right)={lx(d)}$$", conc(r, f"f'(x)={lx(d)}")]
    add("definition_general", "medium", prob, join(sol), f"f'(x)={lx(d)}",
        [check(f"limit(({s(fxh)}-({s(f)}))/h,h,0)", s(d), "limit definition"), check(f"diff({s(f)},x)", s(d), "rule agrees")])

def t_def_recip(r):
    k = nz(r, -6, 8); b = r.randint(-5, 5); gen = r.random() < .45
    v = x + b; f = k / v; d = -k / v**2
    if not fresh(("dr", f, gen)): return
    fl = ("-" if k < 0 else "") + f"\\frac{{{abs(k)}}}{{{lx(v)}}}"
    if gen:
        prob = f"ដោយប្រើនិយមន័យនៃដេរីវេ គណនា $f'(x)$ នៃអនុគមន៍ $f(x)={fl}$ ចំពោះ $x\\neq{-b}$ ។"
        w = lx(v)
        sol = [f"យើងមាន $f(x)={fl}$ ដែល $x\\neq{-b}$ ។ ចំពោះ $h\\neq0$ តូចគ្រប់គ្រាន់ ៖",
               f"$$f(x+h)-f(x)=\\frac{{{k}}}{{{w}+h}}-\\frac{{{k}}}{{{w}}}$$", "យកភាគបែងរួម ៖",
               f"$$=\\frac{{{kd(k)}{par(v)}{'-' + kd(k) if k > 0 else '+' + kd(-k)}{par(v+h)}}}{{{par(v+h)}{par(v)}}}=\\frac{{{lx(-k*h)}}}{{{par(v+h)}{par(v)}}}$$",
               "ចែកនឹង $h$ រួចយកលីមីត ៖", f"$$f'(x)=\\lim_{{h\\to0}}\\frac{{{-k}}}{{{par(v+h)}{par(v)}}}=\\frac{{{-k}}}{{{par(v)}^2}}$$", conc(r, f"f'(x)=\\frac{{{-k}}}{{{par(v)}^2}}")]
        add("definition_general", "medium", prob, join(sol), f"f'(x)=\\frac{{{-k}}}{{{par(v)}^2}}",
            [check(f"limit(({k}/(x+h+({b}))-({k})/(x+({b})))/h,h,0)", s(d), "limit definition"), check(f"diff({s(f)},x)", s(d), "rule agrees")])
    else:
        a = r.choice([t for t in range(-4, 6) if t + b != 0])
        c = a + b; val = R(-k, c * c)
        prob = f"គេឱ្យ $f(x)={fl}$ ។ {r.choice(BYDEF)} គណនា $f'({a})$ ។"
        sol = [f"ដែនកំណត់ $D=IR-\\{{{-b}\\}}$ ហើយ ${a}\\in D$ ។", f"យើងមាន $f({a})={lx(R(k,c))}$ ។", f"ចំពោះ $h\\neq0$ តូចគ្រប់គ្រាន់ ៖",
               f"$$f({a}+h)-f({a})=\\frac{{{k}}}{{{lx(h+c)}}}-\\left({lx(R(k,c))}\\right)=\\frac{{{lx(sp.factor(-k*h))}}}{{{kd(c)}{par(h+c)}}}$$",
               f"នោះ $$\\frac{{f({a}+h)-f({a})}}{{h}}=\\frac{{{-k}}}{{{kd(c)}{par(h+c)}}}$$", f"យកលីមីតពេល $h\\to0$ ៖ $$f'({a})=\\frac{{{-k}}}{{{c*c}}}={lx(val)}$$", conc(r, f"f'({a})={lx(val)}")]
        add("definition_at_point", "medium", prob, join(sol), f"f'({a})={lx(val)}",
            [check(f"limit(({k}/({a}+x+({b}))-({s(R(k,c))}))/x,x,0)", s(val), "limit"), check(f"subs(diff({s(f)},x),x,{a})", s(val), "rule agrees")])

def t_def_sqrt(r):
    p = r.choice([1, 1, 2, 3, 4, 5]); c = r.randint(1, 5); a = r.randint(-2, 6); q = c * c - p * a
    w = p * x + q; f = SQ(w); gen = r.random() < .3 and -q / p <= 1
    if not fresh(("ds", f, gen, a if not gen else 0)): return
    if gen:
        d = p / (2 * f); sw = "\\sqrt{" + lx(w) + "}"; swh = "\\sqrt{" + lx(w + p * h) + "}"
        prob = f"{r.choice(BYDEF)} គណនា $f'(x)$ នៃ $f(x)={sw}$ ចំពោះ ${lx(w)}>0$ ។"
        sol = [dom_ge(r, "f", w, *lin_ge(w)[:2]) + f" ដេរីវេមានចំពោះ ${lin_ge(w)[3]}$ ។", "ចំពោះ $h\\neq0$ យើងពិនិត្យផលធៀប ៖", f"$$\\frac{{f(x+h)-f(x)}}{{h}}=\\frac{{{swh}-{sw}}}{{h}}$$", r.choice(["គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់", "ដើម្បីដោះរាងមិនកំណត់ គុណនឹងកន្សោមឆ្លាស់"]) + f" ${swh}+{sw}$ ៖",
               f"$$=\\frac{{{lx(p*h)}}}{{h\\left({swh}+{sw}\\right)}}=\\frac{{{p}}}{{{swh}+{sw}}}$$", "យកលីមីតពេល $h\\to0$ ៖", f"$$f'(x)=\\frac{{{p}}}{{2{sw}}}$$", conc(r, f"f'(x)=\\frac{{{p}}}{{2{sw}}}")]
        add("definition_general", "hard", prob, join(sol), f"f'(x)=\\frac{{{p}}}{{2{sw}}}",
            [check(f"limit((sqrt({s(w)}+{p}*h)-sqrt({s(w)}))/h,h,0)", s(d), "limit definition"), check(f"diff({s(f)},x)", s(d), "rule agrees")])
    else:
        val = R(p, 2 * c); sw = "\\sqrt{" + lx(w) + "}"; inner = lx(p * h + c * c)
        prob = r.choice([f"គេឱ្យ $f(x)={sw}$ ។ {r.choice(BYDEF)} គណនា $f'({a})$ ។", f"{r.choice(BYDEF)} រកដេរីវេនៃ $f(x)={sw}$ ត្រង់ $x={a}$ ។"])
        sol = [dom_ge(r, "f", w, *lin_ge(w)[:2]), f"យើងមាន $f({a})=\\sqrt{{{c*c}}}={c}$ ។", f"$$f({a}+h)=\\sqrt{{{inner}}}$$", "តាមនិយមន័យ ៖", f"$$f'({a})=\\lim_{{h\\to0}}\\frac{{\\sqrt{{{inner}}}-{c}}}{{h}}$$",
               "លីមីតនេះមានរាងមិនកំណត់ $\\frac{0}{0}$ ។ គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ ៖", f"$$\\frac{{\\sqrt{{{inner}}}-{c}}}{{h}}=\\frac{{\\left({inner}\\right)-{c*c}}}{{h\\left(\\sqrt{{{inner}}}+{c}\\right)}}=\\frac{{{p}}}{{\\sqrt{{{inner}}}+{c}}}$$",
               "យកលីមីតពេល $h\\to0$ ៖", f"$$f'({a})=\\frac{{{p}}}{{{c}+{c}}}={lx(val)}$$", conc(r, f"f'({a})={lx(val)}")]
        add("definition_at_point", "hard", prob, join(sol), f"f'({a})={lx(val)}",
            [check(f"limit((sqrt({s(p*x+c*c)})-{c})/x,x,0)", s(val), "limit"), check(f"subs(diff({s(f)},x),x,{a})", s(val), "rule agrees")])

def t_recog(r):
    k = r.randrange(3); a = r.randint(1, 4) if k else r.choice([-2, -1, 1, 2, 3])
    if k == 0:
        n = r.randint(3, 8); g = x**n; num = x**n - a**n; val = n * a**(n - 1); gl = f"x^{{{n}}}"; dl = f"{n}x^{{{n-1}}}"
    elif k == 1:
        p = r.choice([1, 2, 3, 5]); c = r.randint(1, 5); q = c * c - p * a; w = p * x + q; g = SQ(w); num = g - c; val = R(p, 2 * c)
        gl = "\\sqrt{" + lx(w) + "}"; dl = f"\\frac{{{p}}}{{2\\sqrt{{{lx(w)}}}}}"
    else:
        while True:
            b = nz(r, -3, 5); k2 = nz(r, -6, 6)
            if a + b != 0: break
        g = k2 / (x + b); num = g - R(k2, a + b); val = R(-k2, (a + b)**2); gl = f"\\frac{{{k2}}}{{{lx(x+b)}}}"; dl = f"\\frac{{{-k2}}}{{{par(x+b)}^2}}"
    if not fresh(("rg", g, a)): return
    ga = g.subs(x, a); den = lx(x - a)
    nl = f"{gl}-{lx(ga)}" if ga >= 0 else f"{gl}+{lx(-ga)}"
    lim = f"\\lim_{{x\\to{a}}}\\frac{{{nl}}}{{{den}}}"
    prob = r.choice([f"ដោយសម្គាល់ឃើញថាជាដេរីវេនៃអនុគមន៍មួយ គណនាលីមីត ${lim}$ ។", f"គណនា ${lim}$ ដោយប្រើនិយមន័យនៃដេរីវេ ។", f"ប្រើដេរីវេ ដើម្បីរកលីមីត $$L={lim}$$"])
    sol = ([dom_ge(r, "g", w, *lin_ge(w)[:2])] if k == 1 else []) + [f"តាង $g(x)={gl}$ ។ យើងមាន $g({a})={lx(ga)}$ ។", r.choice(["ដូច្នេះលីមីតនេះមានរាង", "លីមីតដែលត្រូវរកគឺ"]) + f" $$\\lim_{{x\\to{a}}}\\frac{{g(x)-g({a})}}{{x-{a}}}".replace("x-" + str(a) + "}", den + "}") + f"=g'({a})$$",
           f"តាមរូបមន្ត $g'(x)={dl}$ ។", f"$$g'({a})={lx(val)}$$", conc(r, f"{lim}={lx(val)}")]
    add("limit_as_derivative", "medium", prob, join(sol), lx(val), [check(f"limit(({s(num)})/({s(x-a)}),x,{a})", s(val), "limit"), check(f"subs(diff({s(g)},x),x,{a})", s(val), "rule agrees")])

def t_abstract(r):
    a = r.randint(-3, 5); Lv = nz(r, -7, 7); p = r.randint(2, 6); q = r.randint(1, 5); k = r.randrange(3)
    if not fresh(("ab", a, Lv, p, q, k)): return
    F = Lv * x + (x - a)**2
    if k == 0:
        lim = f"\\lim_{{h\\to0}}\\frac{{f({lx(a+p*h)})-f({a})}}{{h}}"; val = p * Lv
        lhs = f"limit((({s(F.subs(x,a+p*x))})-({s(F.subs(x,a))}))/x,x,0)"
        st = [f"តាង $t={p}h$ នោះពេល $h\\to0$ គេបាន $t\\to0$ ហើយ $h=\\frac{{t}}{{{p}}}$ ។", f"$${lim}=\\lim_{{t\\to0}}{p}\\cdot\\frac{{f({a}+t)-f({a})}}{{t}}={p}f'({a})$$"]
    elif k == 1:
        lim = f"\\lim_{{h\\to0}}\\frac{{f({lx(a+p*h)})-f({lx(a-q*h)})}}{{h}}"; val = (p + q) * Lv
        lhs = f"limit((({s(F.subs(x,a+p*x))})-({s(F.subs(x,a-q*x))}))/x,x,0)"
        st = [f"បញ្ចូល និងដក $f({a})$ ក្នុងភាគយក ៖", f"$$\\frac{{f({lx(a+p*h)})-f({lx(a-q*h)})}}{{h}}=\\frac{{f({lx(a+p*h)})-f({a})}}{{h}}-\\frac{{f({lx(a-q*h)})-f({a})}}{{h}}$$",
              f"តាមនិយមន័យ លីមីតតួទី១ស្មើ ${p}f'({a})$ ហើយលីមីតតួទី២ស្មើ $-{kd(q)}f'({a})$ ។", f"$${lim}={p}f'({a})+{kd(q)}f'({a})={p+q}f'({a})$$"]
    else:
        lim = f"\\lim_{{x\\to{a}}}\\frac{{f(x)-f({a})}}{{{lx(sp.expand(x**2-a**2))}}}"
        if a == 0: return
        val = R(Lv, 2 * a)
        lhs = f"limit((({s(F)})-({s(F.subs(x,a))}))/({s(x**2-a**2)}),x,{a})"
        st = [f"ដោយ ${lx(sp.expand(x**2-a**2))}={par(x-a)}{par(x+a)}$ គេបាន ៖", f"$$\\frac{{f(x)-f({a})}}{{{lx(sp.expand(x**2-a**2))}}}=\\frac{{f(x)-f({a})}}{{{lx(x-a)}}}\\cdot\\frac{{1}}{{{lx(x+a)}}}$$",
              f"ពេល $x\\to{a}$ កត្តាទី១ខិតជិត $f'({a})$ ហើយកត្តាទី២ខិតជិត $\\frac{{1}}{{{2*a}}}$ ។"]
    prob = r.choice([f"គេដឹងថាអនុគមន៍ $f$ មានដេរីវេត្រង់ $x={a}$ ហើយ $f'({a})={Lv}$ ។ គណនា ${lim}$ ។", f"ឱ្យ $f$ ជាអនុគមន៍មានដេរីវេត្រង់ $x={a}$ ដែល $f'({a})={Lv}$ ។ រកតម្លៃនៃលីមីត $${lim}$$"])
    sol = st + [f"ជំនួស $f'({a})={Lv}$ គេបានលីមីតស្មើ ${lx(val)}$ ។", conc(r, f"{lim}={lx(val)}")]
    add("limit_as_derivative", "hard", prob, join(sol), lx(val), [check(lhs, s(val), "test function with f'(a)=L")])

def t_piece(r):
    a = nz(r, -2, 3); b = r.randint(-4, 4); c = r.randint(-4, 5)
    g = x**2 + b * x + c
    p = 2 * a + b; q = g.subs(x, a) - p * a
    if not fresh(("pc", g, a)): return
    tl = f"f(x)=\\begin{{cases}}{lx(g)} & x\\leq{a}\\\\ ax+b & x>{a}\\end{{cases}}"
    prob = r.choice([f"គេឱ្យអនុគមន៍ $${tl}$$ រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ $f$ មានដេរីវេត្រង់ $x={a}$ ។", f"កំណត់តម្លៃ $a$ និង $b$ ដើម្បីឱ្យអនុគមន៍ $${tl}$$ ជាប់ និងមានដេរីវេត្រង់ $x={a}$ ។"])
    ga = g.subs(x, a)
    sol = [f"អនុគមន៍មានដេរីវេត្រង់ $x={a}$ លុះត្រាតែវាជាប់ត្រង់នោះ ហើយដេរីវេខាងឆ្វេង ស្មើនឹងដេរីវេខាងស្ដាំ ។",
           f"ភាពជាប់៖ លីមីតខាងឆ្វេងគឺ $f({a})={lx(ga)}$ ហើយលីមីតខាងស្ដាំគឺ ${kd(a)}a+b$ ។ ដូច្នេះ $${kd(a)}a+b={lx(ga)}\\quad(1)$$",
           f"ដេរីវេខាងឆ្វេង៖ $({lx(g)})'={lx(2*x+b)}$ ដែលត្រង់ $x={a}$ ស្មើ ${lx(p)}$ ។", "ដេរីវេខាងស្ដាំ៖ $(ax+b)'=a$ ។", f"ដូច្នេះ $a={lx(p)}$ ។",
           f"ជំនួសក្នុង $(1)$ ៖ $b={lx(ga)}-({a})({p})={lx(q)}$ ។", conc(r, f"a={lx(p)},\\ b={lx(q)}")]
    add("piecewise_differentiability", "bacii", prob, join(sol), f"a={lx(p)},\\ b={lx(q)}",
        [check(f"subs(diff({s(g)},x),x,{a})", s(p), "left derivative = a"), check(f"subs({s(g)},x,{a})", s(p * a + q), "continuity")])

def t_abs(r):
    a = r.randint(-3, 4); b = r.randint(-4, 5); kk = r.choice([0, 1])
    if b == a: b = a + 2
    if not fresh(("abs", a, b)): return
    pre = x - b
    fl = f"{par(pre)}\\left|{lx(x-a)}\\right|"
    Lf = a - b; f = pre * sp.Abs(x - a)
    prob = r.choice([f"គេឱ្យ $f(x)={fl}$ ។ សិក្សាថាតើ $f$ មានដេរីវេត្រង់ $x={a}$ ឬទេ ។", f"តើអនុគមន៍ $f(x)={fl}$ មានដេរីវេត្រង់ $x={a}$ ឬទេ ? ពន្យល់ ។"])
    den = lx(x - a)
    sol = [f"យើងមាន $f({a})=0$ ។ ផលធៀបគឺ $$\\frac{{f(x)-f({a})}}{{{den}}}=\\frac{{{par(pre)}\\left|{den}\\right|}}{{{den}}}$$",
           f"ចំពោះ $x>{a}$ យើងមាន $\\left|{den}\\right|={den}$ ដូច្នេះ ដេរីវេខាងស្ដាំ ៖ $$\\lim_{{x\\to{a}^+}}\\left({lx(pre)}\\right)={Lf}$$",
           f"ចំពោះ $x<{a}$ យើងមាន $\\left|{den}\\right|=-\\left({den}\\right)$ ដូច្នេះ ដេរីវេខាងឆ្វេង ៖ $$\\lim_{{x\\to{a}^-}}-\\left({lx(pre)}\\right)={-Lf}$$",
           f"ដោយ ${Lf}\\neq{-Lf}$ ដេរីវេទាំងពីរមិនស្មើគ្នា ។", f"ដូចនេះ អនុគមន៍ $f$ គ្មានដេរីវេត្រង់ $x={a}$ ទេ ដោយ $\\boxed{{f'_+({a})={Lf}\\neq f'_-({a})={-Lf}}}$ ។"]
    add("one_sided_derivative", "hard", prob, join(sol), f"f'_+({a})={Lf},\\ f'_-({a})={-Lf}",
        [check(f"limit(({s(f)})/({s(x-a)}),x,{a},'+')", Lf, "right"), check(f"limit(({s(f)})/({s(x-a)}),x,{a},'-')", -Lf, "left")])

# ---------- rules on abstract u, v ----------
def t_uv(r):
    a = r.randint(-2, 4); u0, u1, v0, v1 = nz(r, -6, 7), nz(r, -5, 6), nz(r, -5, 6), nz(r, -5, 6)
    if not fresh(("uv", a, u0, u1, v0, v1)): return
    U = u0 + u1 * (x - a); V = v0 + v1 * (x - a)
    pv = (u1 * v0 + u0 * v1); qv = R(u1 * v0 - u0 * v1, v0 * v0); sq = 2 * u0 * u1; lc1, lc2 = r.randint(2, 5), r.randint(2, 5); lcv = lc1 * u1 - lc2 * v1
    prob = (r.choice(["គេឱ្យអនុគមន៍ $u$ និង $v$ មានដេរីវេត្រង់ ", "អនុគមន៍ $u$ និង $v$ មានដេរីវេត្រង់ "]) + f"$x={a}$ ដែល $u({a})={u0}$ , $u'({a})={u1}$ , $v({a})={v0}$ , $v'({a})={v1}$ ។ គណនា ៖\n"
            f"ក. $(uv)'({a})$\nខ. $\\left(\\frac{{u}}{{v}}\\right)'({a})$\nគ. $(u^2)'({a})$\nឃ. $({lc1}u-{lc2}v)'({a})$")
    sol = [f"ក. តាមរូបមន្តផលគុណ ៖ $$(uv)'({a})=u'({a})v({a})+u({a})v'({a})=({u1})({v0})+({u0})({v1})={pv}$$",
           f"ខ. តាមរូបមន្តផលចែក ដោយ $v({a})\\neq0$ ៖ $$\\left(\\frac{{u}}{{v}}\\right)'({a})=\\frac{{u'({a})v({a})-u({a})v'({a})}}{{v^2({a})}}=\\frac{{({u1})({v0})-({u0})({v1})}}{{{v0*v0}}}={lx(qv)}$$",
           f"គ. តាមរូបមន្ត $(u^n)'=nu'u^{{n-1}}$ ៖ $$(u^2)'({a})=2u'({a})u({a})=2({u1})({u0})={sq}$$",
           f"ឃ. តាមរូបមន្ត $(ku)'=ku'$ និងដេរីវេនៃផលដក ៖ $$({lc1}u-{lc2}v)'({a})={lc1}({u1})-{lc2}({v1})={lcv}$$",
           f"ដូចនេះ $\\boxed{{(uv)'({a})={pv}}}$ , $\\boxed{{\\left(\\frac{{u}}{{v}}\\right)'({a})={lx(qv)}}}$ , $\\boxed{{(u^2)'({a})={sq}}}$ , $\\boxed{{({lc1}u-{lc2}v)'({a})={lcv}}}$ ។"]
    Us, Vs = s(U), s(V)
    add("rules_abstract_uv", "medium", prob, join(sol), f"{pv};\\ {lx(qv)};\\ {sq};\\ {lcv}",
        [check(f"subs(diff(({Us})*({Vs}),x),x,{a})", pv, "product"), check(f"subs(diff(({Us})/({Vs}),x),x,{a})", s(qv), "quotient"),
         check(f"subs(diff(({Us})**2,x),x,{a})", sq, "square"), check(f"subs(diff({lc1}*({Us})-{lc2}*({Vs}),x),x,{a})", lcv, "linear")])

def t_comp(r):
    a, b = r.randint(-2, 3), r.randint(-3, 4); p, q = nz(r, -5, 6), nz(r, -5, 6); k = r.randrange(2)
    if k == 0:
        if not fresh(("cp", a, b, p, q)): return
        G = b + p * (x - a); F = q * (x - b) + 3
        prob = f"គេឱ្យអនុគមន៍ $f$ និង $g$ មានដេរីវេ ដែល $g({a})={b}$ , $g'({a})={p}$ និង $f'({b})={q}$ ។ តាង $h(x)=f(g(x))$ ។ គណនា $h'({a})$ ។"
        val = p * q
        sol = ["អនុគមន៍ $h=f\\circ g$ ជាអនុគមន៍បណ្ដាក់ ។ តាមរូបមន្ត ៖", "$$h'(x)=g'(x)\\cdot f'(g(x))$$", f"ចំពោះ $x={a}$ ៖", f"$$h'({a})=g'({a})\\cdot f'(g({a}))=({p})\\cdot f'({b})=({p})({q})={val}$$", conc(r, f"h'({a})={val}")]
        add("composite_abstract", "medium", prob, join(sol), f"h'({a})={val}", [check(f"subs(diff({s(F.subs(x,G))},x),x,{a})", val, "test functions")])
    else:
        c = r.randint(1, 5); n = r.randint(2, 3); t = r.randint(1, 3)
        if not fresh(("cq", c, n, t, q)): return
        inner = x**n + c; b2 = t**n + c
        F = q * (x - b2) + x * 0
        G = inner
        val = n * t**(n - 1) * q
        gx = f"g'(x)={lx(sp.diff(inner,x))}\\,f'\\left({lx(inner)}\\right)"
        prob = f"អនុគមន៍ $f$ មានដេរីវេលើ $IR$ ហើយ $f'({b2})={q}$ ។ តាង $g(x)=f\\left({lx(inner)}\\right)$ ។ គណនា $g'(x)$ រួចរកតម្លៃ $g'({t})$ ។"
        sol = [f"តាមរូបមន្តអនុគមន៍បណ្ដាក់ ជាមួយ $u={lx(inner)}$ និង $u'={lx(sp.diff(inner,x))}$ ៖", f"$$g'(x)={lx(sp.diff(inner,x))}\\,f'\\left({lx(inner)}\\right)$$", f"ចំពោះ $x={t}$ យើងមាន ${lx(inner.subs(x,t))}$ ជាតម្លៃនៃ $u$ ដូច្នេះ ៖".replace(lx(inner.subs(x, t)) + "$ ជាតម្លៃនៃ $u$", f"u={b2}$"),
               f"$$g'({t})={n*t**(n-1)}\\,f'({b2})={n*t**(n-1)}({q})={val}$$", f"ដូចនេះ ${B(gx)}$ និង ${B(f"g'({t})={val}")}$ ។"]
        add("composite_abstract", "medium", prob, join(sol), f"{gx},\\ g'({t})={val}", [check(f"subs(diff({s(F.subs(x,G))},x),x,{t})", val, "test function")])

# ---------- parameters ----------
def t_param(r):
    k = r.randrange(3); a = nz(r, -2, 3); m0 = nz(r, -5, 6)
    if k == 0:
        n = r.randint(3, 4); b = r.randint(-5, 5); c0 = r.randint(-4, 4)
        f = x**n + m0 * x**2 + b * x + c0
        if a == 0 or not fresh(("pm", f, a)): return
        val = sp.diff(f, x).subs(x, a)
        ml = lx(x**n) + "+mx^{2}" + (("+" if b > 0 else "-") + (str(abs(b)) if abs(b) != 1 else "") + "x" if b else "") + (("+" if c0 > 0 else "-") + str(abs(c0)) if c0 else "")
        prob = r.choice([f"គេឱ្យ $f(x)={ml}$ ។ រកតម្លៃ $m$ ដើម្បីឱ្យ $f'({a})={val}$ ។", f"កំណត់ប៉ារ៉ាម៉ែត្រ $m$ ដែលធ្វើឱ្យអនុគមន៍ $f(x)={ml}$ មានដេរីវេ $f'({a})={val}$ ។"])
        ca = n * a**(n - 1) + b
        sol = [f"យើងគណនា ៖ $$f'(x)={lx(sp.diff(x**n+b*x,x))}+2mx$$", f"ចំពោះ $x={a}$ ៖ $$f'({a})={ca}+({2*a})m$$", f"លក្ខខណ្ឌ $f'({a})={val}$ ឱ្យសមីការ $${ca}+({2*a})m={val}$$", f"ដោះស្រាយ ៖ $({2*a})m={val-ca}$ នាំឱ្យ $m={m0}$ ។", conc(r, f"m={m0}")]
    elif k == 1:
        b, c, a2 = nz(r, -5, 5), nz(r, -5, 5), r.randint(-2, 2)
        if a2 + c == 0 or m0 * c - b == 0: return
        f = (m0 * x + b) / (x + c)
        if not fresh(("pm2", f, a2)): return
        val = sp.diff(f, x).subs(x, a2); fl = "\\frac{mx" + ("+" if b > 0 else "-") + str(abs(b)) + "}{" + lx(x + c) + "}"
        prob = f"គេឱ្យអនុគមន៍ $f(x)={fl}$ ។ រកតម្លៃ $m$ ដើម្បីឱ្យ $f'({a2})={lx(val)}$ ។"
        sol = [f"ចំពោះ $x\\neq{-c}$ តាមរូបមន្តផលចែក ៖", f"$$f'(x)=\\frac{{m{par(x+c)}-(mx{'+' if b>0 else '-'}{abs(b)})}}{{{par(x+c)}^2}}=\\frac{{{kd(c)}m{'+' if -b>0 else '-'}{abs(b)}}}{{{par(x+c)}^2}}$$",
               f"ចំពោះ $x={a2}$ ភាគបែងស្មើ ${(a2+c)**2}$ ។ លក្ខខណ្ឌឱ្យ ៖", f"$$\\frac{{{kd(c)}m{'+' if -b>0 else '-'}{abs(b)}}}{{{(a2+c)**2}}}={lx(val)}$$", f"ដោះស្រាយសមីការដឺក្រេទី១ គេបាន $m={m0}$ ។", conc(r, f"m={m0}")]
        a = a2
    else:
        trip = {(3, 4): 5, (4, 3): 5, (6, 8): 10, (8, 6): 10, (5, 12): 13, (12, 5): 13}
        t, c2 = r.choice(list(trip)); w = x**2 + c2**2; f = m0 * x + SQ(w); hyp = trip[(t, c2)]; a = t
        if not fresh(("pm3", f, t)): return
        val = sp.diff(f, x).subs(x, t); ml = "mx+\\sqrt{" + lx(w) + "}"
        prob = f"គេឱ្យ $f(x)={ml}$ ។ រក $m$ ដើម្បីឱ្យ $f'({t})={lx(val)}$ ។"
        sol = [f"យើងមាន $D=IR$ ហើយ $$f'(x)=m+\\frac{{x}}{{\\sqrt{{{lx(w)}}}}}$$", f"ចំពោះ $x={t}$ ៖ $\\sqrt{{{t*t+c2*c2}}}={hyp}$ ដូច្នេះ $f'({t})=m+{lx(R(t,hyp))}$ ។", f"លក្ខខណ្ឌឱ្យ $m+{lx(R(t,hyp))}={lx(val)}$ នាំឱ្យ $m={m0}$ ។", conc(r, f"m={m0}")]
    add("parameter_from_derivative", "medium", prob, join(sol), f"m={m0}", [check(f"subs(diff({s(f)},x),x,{a})", s(val), "condition holds at m")])

def t_findabc(r):
    A, Bc, C = nz(r, -4, 4), r.randint(-5, 5), r.randint(-6, 6); p, q, t = r.sample(range(-3, 5), 3)
    f = A * x**2 + Bc * x + C
    if not fresh(("abc", f, p, q)): return
    d = sp.diff(f, x); fp, fq, ft = d.subs(x, p), d.subs(x, q), f.subs(x, t)
    prob = r.choice([f"រកចំនួនពិត $a,b,c$ នៃអនុគមន៍ $f(x)=ax^2+bx+c$ ដោយដឹងថា $f'({p})={fp}$ , $f'({q})={fq}$ និង $f({t})={ft}$ ។", f"គេមានត្រីធា $f(x)=ax^2+bx+c$ ដែល $f'({p})={fp}$ , $f'({q})={fq}$ ហើយ $f({t})={ft}$ ។ កំណត់ $a$ , $b$ , $c$ ។"])
    sol = ["យើងមាន $f'(x)=2ax+b$ ។", "លក្ខខណ្ឌទាំងពីរលើដេរីវេឱ្យប្រព័ន្ធ ៖", f"$$\\begin{{cases}}{2*p}a+b={fp}\\\\ {2*q}a+b={fq}\\end{{cases}}$$",
           f"ដកសមីការទាំងពីរ ៖ ${2*(p-q)}a={fp-fq}$ នាំឱ្យ $a={A}$ ។", f"ជំនួសក្នុងសមីការទី១ គេបាន $b={Bc}$ ។", f"ពី $f({t})={ft}$ យើងបាន $({A})({t*t})+({Bc})({t})+c={ft}$ នាំឱ្យ $c={C}$ ។", conc(r, f"a={A},\\ b={Bc},\\ c={C}")]
    add("parameter_from_derivative", "medium", prob, join(sol), f"a={A},\\ b={Bc},\\ c={C}",
        [check(f"subs(diff({s(f)},x),x,{p})", fp, "f'(p)"), check(f"subs(diff({s(f)},x),x,{q})", fq, "f'(q)"), check(f"subs({s(f)},x,{t})", ft, "f(t)")])

def t_canon(r):
    rt = nz(r, -5, 5); a0 = r.choice([1, 2, 3, -1]); b0 = r.randint(-5, 5); c0 = nz(r, -8, 8)
    v = x - rt; u = sp.expand((a0 * x + b0) * v + c0); f = u / v
    if not fresh(f): return
    d = a0 - c0 / v**2; fd = sp.factor(d)
    fl = "\\frac{" + lx(u) + "}{" + lx(v) + "}"
    prob = f"គេឱ្យ $f(x)={fl}$ ។ ក. រកចំនួនពិត $a,b,c$ ដើម្បីឱ្យ $f(x)=ax+b+\\frac{{c}}{{{lx(v)}}}$ ។\nខ. ទាញរក $f'(x)$ ។"
    sol = [f"ក. ចំពោះ $x\\neq{rt}$ ធ្វើភាគបែងរួម ៖", f"$$ax+b+\\frac{{c}}{{{lx(v)}}}=\\frac{{(ax+b){par(v)}+c}}{{{lx(v)}}}=\\frac{{ax^2+\\left(b{'-' if rt>0 else '+'}{kd(abs(rt))}a\\right)x{'-' if rt>0 else '+'}{kd(abs(rt))}b+c}}{{{lx(v)}}}$$",
           f"ផ្ទឹមមេគុណជាមួយភាគយក ${lx(u)}$ គេបាន $a={a0}$ , $b={b0}$ , $c={c0}$ ។", f"ខ. ដូច្នេះ $f(x)={lx(a0*x+b0)}{'+' if c0>0 else '-'}\\frac{{{abs(c0)}}}{{{lx(v)}}}$ ។ ធ្វើដេរីវេតាមតួ ៖", f"$$f'(x)={a0}{'-' if c0>0 else '+'}\\frac{{{abs(c0)}}}{{{par(v)}^2}}={lx(fd)}$$",
           conc(r, f"a={a0},\\ b={b0},\\ c={c0},\\quad f'(x)={lx(fd)}")]
    add("canonical_form_then_derivative", "medium", prob, join(sol), f"a={a0},\\ b={b0},\\ c={c0},\\ f'(x)={lx(fd)}",
        [check(f"({s(u)})/({s(v)})-({s(a0*x+b0)})", f"({c0})/({s(v)})", "decomposition"), check(f"diff(({s(u)})/({s(v)}),x)", s(fd), "derivative")])

def t_identity(r):
    k = r.randrange(5); a = pos(r, 6)
    if k == 0:
        b = nz(r, -5, 6); y = 1 / (x + b); rel = "y'+y^2=0"; lhs = f"diff({s(y)},x)+({s(y)})**2"; yl = f"\\frac{{1}}{{{lx(x+b)}}}"; rhs = 0
        st = [f"ចំពោះ $x\\neq{-b}$ ៖ $y'=-\\frac{{1}}{{{par(x+b)}^2}}$ ។", f"ហើយ $y^2=\\frac{{1}}{{{par(x+b)}^2}}$ ។", f"បូកលទ្ធផលទាំងពីរ ៖ $$y'+y^2=-\\frac{{1}}{{{par(x+b)}^2}}+\\frac{{1}}{{{par(x+b)}^2}}=0$$"]
    elif k == 1:
        y = SQ(x**2 + a); rel = "yy'=x"; lhs = f"({s(y)})*diff({s(y)},x)"; yl = f"\\sqrt{{{lx(x**2+a)}}}"; rhs = "x"
        st = [f"ដោយ ${lx(x**2+a)}>0$ នោះ $D=IR$ ។ តាមរូបមន្ត $(\\sqrt{{u}})'=\\frac{{u'}}{{2\\sqrt{{u}}}}$ ៖ $$y'=\\frac{{2x}}{{2\\sqrt{{{lx(x**2+a)}}}}}=\\frac{{x}}{{\\sqrt{{{lx(x**2+a)}}}}}$$", f"គុណនឹង $y$ ៖ $$yy'=\\sqrt{{{lx(x**2+a)}}}\\cdot\\frac{{x}}{{\\sqrt{{{lx(x**2+a)}}}}}=x$$"]
    elif k == 2:
        a = r.randint(2, 5); y = SQ(2 * a * x - x**2); rel = f"y^3y''+{a*a}=0"; lhs = f"({s(y)})**3*diff({s(y)},x,2)+{a*a}"; yl = f"\\sqrt{{{lx(2*a*x-x**2)}}}"; rhs = 0
        w = lx(2 * a * x - x**2)
        st = [f"អនុគមន៍កំណត់លុះត្រាតែ ${w}\\geq0$ ។ ដូចនេះ $D=[0;{2*a}]$ ហើយដេរីវេមានចំពោះ $0<x<{2*a}$ ។", f"លើចន្លោះ $0<x<{2*a}$ ៖ $$y'=\\frac{{{2*a}-2x}}{{2\\sqrt{{{w}}}}}=\\frac{{{lx(a-x)}}}{{y}}$$", f"ធ្វើដេរីវេម្ដងទៀត ដោយរូបមន្តផលចែក ៖ $$y''=\\frac{{-y-({lx(a-x)})y'}}{{y^2}}=\\frac{{-y^2-({lx(a-x)})^2}}{{y^3}}$$",
              f"ដោយ $y^2+({lx(a-x)})^2={w}+{lx(sp.expand((a-x)**2))}={a*a}$ គេបាន $y''=-\\frac{{{a*a}}}{{y^3}}$ ។", f"នោះ $y^3y''=-{a*a}$ ឬ ${rel}$ ។"]
    elif k == 3:
        c = nz(r, -5, 5); b = r.choice([t for t in range(-5, 6) if t != c]); y = (x + b) / (x + c); rel = "2(y')^2=(y-1)y''"; lhs = f"2*diff({s(y)},x)**2-(({s(y)})-1)*diff({s(y)},x,2)"; yl = f"\\frac{{{lx(x+b)}}}{{{lx(x+c)}}}"; rhs = 0; det = c - b
        st = [f"ចំពោះ $x\\neq{-c}$ ៖ $$y'=\\frac{{{det}}}{{{par(x+c)}^2}}$$", f"$$y''=\\frac{{{-2*det}}}{{{par(x+c)}^3}}$$", f"ហើយ $y-1=\\frac{{{-det}}}{{{lx(x+c)}}}$ ។",
              f"អង្គឆ្វេង៖ $2(y')^2=\\frac{{{2*det*det}}}{{{par(x+c)}^4}}$ ។", f"អង្គស្ដាំ៖ $(y-1)y''=\\frac{{{-det}}}{{{lx(x+c)}}}\\cdot\\frac{{{-2*det}}}{{{par(x+c)}^3}}=\\frac{{{2*det*det}}}{{{par(x+c)}^4}}$ ។", "អង្គទាំងពីរស្មើគ្នា ។"]
    else:
        c = nz(r, -4, 5); n = r.randint(2, 5); y = (x + c)**n; rel = f"{par(x+c)}y'={n}y"; lhs = f"({s(x+c)})*diff({s(y)},x)-{n}*({s(y)})"; yl = f"{par(x+c)}^{{{n}}}"; rhs = 0
        st = [f"តាមរូបមន្ត $(u^n)'=nu'u^{{n-1}}$ ៖ $y'={n}{par(x+c)}^{{{n-1}}}$ ។".replace("^{1}", ""), f"គុណនឹង ${lx(x+c)}$ ៖ $${par(x+c)}y'={n}{par(x+c)}^{{{n}}}={n}y$$"]
    if not fresh(("id", k, y)): return
    prob = r.choice([f"គេឱ្យអនុគមន៍ $y={yl}$ ។ បង្ហាញថា ${rel}$ ។", f"ផ្ទៀងផ្ទាត់ថាអនុគមន៍ $y={yl}$ បំពេញទំនាក់ទំនង ${rel}$ ។", f"ស្រាយបញ្ជាក់ថា ${rel}$ ដោយដឹងថា $y={yl}$ ។"])
    add("differential_relation", "hard", prob, join(st + [f"ដូចនេះ $\\boxed{{{rel}}}$ ។"]), rel, [check(lhs, rhs, "relation holds")])

def t_second(r):
    k = r.randrange(5); pre2 = ""
    if k == 0:
        a, b = r.choice([1, 2, 3, 4, 5]), r.randint(1, 7); w = a * x + b; f = SQ(w); sw = f"\\sqrt{{{lx(w)}}}"
        d1 = a / (2 * f); d2 = -a * a / (4 * w * f)
        fl = sw; l1 = f"\\frac{{{a}}}{{2{sw}}}"; l2 = f"-\\frac{{{a*a}}}{{4{par(w)}{sw}}}"
        pre2 = dom_ge(r, "y", w, *lin_ge(w)[:2]) + f" ដេរីវេមានចំពោះ ${lin_ge(w)[3]}$ ។"
        mid = [f"សរសេរ $y'=\\frac{{{a}}}{{2}}{par(w)}^{{-\\frac{{1}}{{2}}}}$ ។", f"តាមរូបមន្ត $(u^n)'=nu'u^{{n-1}}$ ៖ $$y''=\\frac{{{a}}}{{2}}\\cdot\\left(-\\frac{{1}}{{2}}\\right)({a}){par(w)}^{{-\\frac{{3}}{{2}}}}$$"]
    elif k == 1:
        c = pos(r, 9); w = x**2 + c; f = SQ(w); sw = f"\\sqrt{{{lx(w)}}}"; d1 = x / f; d2 = c / (w * f)
        fl = sw; l1 = f"\\frac{{x}}{{{sw}}}"; l2 = f"\\frac{{{c}}}{{{par(w)}{sw}}}"
        pre2 = f"ដោយ ${lx(w)}>0$ ជានិច្ច នោះ $D=IR$ ។"
        mid = [f"តាមរូបមន្តផលចែក ៖ $$y''=\\frac{{{sw}-x\\cdot\\frac{{x}}{{{sw}}}}}{{{lx(w)}}}$$", f"គុណភាគយក និងភាគបែងនឹង ${sw}$ ៖ $$y''=\\frac{{{lx(w)}-x^2}}{{{par(w)}{sw}}}$$"]
    elif k == 2:
        while True:
            u, v = lin(r), monic(r); a, b, c, d_ = u.coeff(x, 1), u.coeff(x, 0), 1, v.coeff(x, 0)
            if a * d_ - b: break
        det = a * d_ - b; f = u / v; d1 = det / v**2; d2 = -2 * det / v**3
        fl = f"\\frac{{{lx(u)}}}{{{lx(v)}}}"; l1 = f"\\frac{{{det}}}{{{par(v)}^2}}"; l2 = f"\\frac{{{-2*det}}}{{{par(v)}^3}}"
        pre2 = dom_excl(r, "y", v, [-v.coeff(x, 0)])
        mid = [f"សរសេរ $y'={det}{par(v)}^{{-2}}$ ដូច្នេះ $y''=({det})(-2){par(v)}^{{-3}}$ ។"]
    elif k == 3:
        c = nz(r, -5, 5); n = r.randint(3, 7); a = r.choice([1, 2, 3, -1]); w = a * x + c; f = w**n; d1 = n * a * w**(n - 1); d2 = n * (n - 1) * a * a * w**(n - 2)
        fl = f"{par(w)}^{{{n}}}"; l1 = f"{n*a}{par(w)}^{{{n-1}}}"; l2 = f"{n*(n-1)*a*a}{par(w)}^{{{n-2}}}".replace("^{1}", ""); mid = []
    else:
        f = cubic(r) + r.randint(1, 3) * x**4; d1 = sp.diff(f, x); d2 = sp.diff(d1, x); fl = lx(f); l1 = lx(d1); l2 = lx(d2); mid = []
    if not fresh(("sd", f)): return
    prob = r.choice([f"គណនាដេរីវេទី១ និងដេរីវេទី២ នៃ $y={fl}$ ។", f"គេឱ្យ $y={fl}$ ។ រក $y'$ និង $y''$ ។", f"ចូរគណនា $y''$ ដោយដឹងថា $y={fl}$ ។"])
    sol = ([pre2] if pre2 else []) + ["ដេរីវេទី១ ៖", f"$$y'={l1}$$", "ដេរីវេទី២ ជាដេរីវេនៃ $y'$ ៖"] + mid + [f"$$y''={l2}$$", conc(r, f"y'={l1},\\quad y''={l2}")]
    add("second_derivative", "medium", prob, join(sol), f"y'={l1},\\ y''={l2}", [check(f"diff({s(f)},x)", s(d1), "y'"), check(f"diff({s(f)},x,2)", s(d2), "y''")])

def t_velocity(r):
    t1, t2 = sorted(r.sample(range(1, 9), 2)); k = r.choice([1, 2, 3]); c = r.randint(0, 9)
    v = 3 * k * (x - t1) * (x - t2); sx = sp.integrate(sp.expand(v), x) + c
    if not fresh(("vel", sx)): return
    t = sp.Symbol("t"); st_ = sx.subs(x, t); vl = sp.expand(sp.diff(st_, t)); al = sp.diff(vl, t)
    tt = r.randint(1, 9); vv, aa = vl.subs(t, tt), al.subs(t, tt)
    prob = r.choice([f"វត្ថុមួយធ្វើចលនាត្រង់ ដែលទីតាំងរបស់វាគិតជាម៉ែត្រ កំណត់ដោយ $s(t)={lx(st_)}$ ($t$ គិតជាវិនាទី) ។ ក. គណនាល្បឿន $v(t)$ និងសំទុះ $a(t)$ ។\nខ. រកល្បឿន និងសំទុះត្រង់ $t={tt}$ ។\nគ. រកខណៈដែលល្បឿនស្មើសូន្យ ។",
                     f"ទីតាំងនៃចំណុចមួយលើអ័ក្សកំណត់ដោយ $s(t)={lx(st_)}$ ។ គណនា $v(t)=s'(t)$ , $a(t)=v'(t)$ រួចរក $v({tt})$ , $a({tt})$ និងខណៈ $t$ ដែល $v(t)=0$ ។"])
    va = [f"ល្បឿនជាដេរីវេនៃទីតាំង ៖ $$v(t)=s'(t)={lx(vl)}$$", f"សំទុះជាដេរីវេនៃល្បឿន ៖ $$a(t)=v'(t)={lx(al)}$$"]
    at = [f"ត្រង់ $t={tt}$ ៖ $v({tt})={vv}$ និង $a({tt})={aa}$ ។"]
    zero = [f"ដោះស្រាយ $v(t)=0$ ៖ $$v(t)={3*k}(t-{t1})(t-{t2})=0$$", f"នាំឱ្យ $t={t1}$ ឬ $t={t2}$ ។"]
    fin1 = f"${B('v(t)=' + lx(vl))}$ , ${B('a(t)=' + lx(al))}$"; fin2 = f"${B(f'v({tt})={vv}')}$ , ${B(f'a({tt})={aa}')}$"; fin3 = f"${B(f't={t1}')}$ និង ${B(f't={t2}')}$"
    if has_parts(prob):
        sol = parts(prob, [va + [f"ដូចនេះ {fin1} ។"], at + [f"ដូចនេះ {fin2} ។"], zero + [f"ដូចនេះ ល្បឿនស្មើសូន្យត្រង់ {fin3} ។"]])
    else:
        sol = va + at + zero + [f"ដូចនេះ {fin1} , {fin2} ហើយល្បឿនស្មើសូន្យត្រង់ {fin3} ។"]
    add("application_motion", "medium", prob, join(sol), f"v(t)={lx(vl)},\\ a(t)={lx(al)},\\ v({tt})={vv},\\ a({tt})={aa},\\ t={t1},\\ t={t2}",
        [check(f"diff({s(sx)},x)", s(vl.subs(t, x)), "velocity"), check(f"diff({s(sx)},x,2)", s(al.subs(t, x)), "acceleration"), check(f"subs(diff({s(sx)},x),x,{t1})", 0, "v(t1)=0"), check(f"subs(diff({s(sx)},x),x,{t2})", 0, "v(t2)=0"), check(f"subs(diff({s(sx)},x),x,{tt})", vv, "v"), check(f"subs(diff({s(sx)},x,2),x,{tt})", aa, "a")])

def t_implicit(r):
    k = r.randrange(3)
    if k == 0:
        p, q, hyp = r.choice([(3, 4, 5), (4, 3, 5), (6, 8, 10), (8, 6, 10), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17), (1, 2, None), (2, 1, None)])
        rr = hyp * hyp if hyp else 5
        sp_, sq_ = r.choice([1, -1]), r.choice([1, -1]); p *= sp_; q *= sq_
        Y = (1 if q > 0 else -1) * SQ(rr - x**2); val = R(-p, q)
        if not fresh(("im", rr, p, q)): return
        prob = f"ចំណុច $A({p};{q})$ ស្ថិតនៅលើខ្សែកោង $x^2+y^2={rr}$ ។ ធ្វើដេរីវេលើអង្គទាំងពីរ រួចគណនា $y'$ ត្រង់ចំណុច $A$ ។"
        sol = ["ចាត់ទុក $y$ ជាអនុគមន៍នៃ $x$ ។ ធ្វើដេរីវេលើអង្គទាំងពីរ ៖", "$$2x+2yy'=0$$", "ចំពោះ $y\\neq0$ គេបាន $y'=-\\frac{x}{y}$ ។", f"ត្រង់ $A({p};{q})$ ៖ $$y'=-\\frac{{x}}{{y}}={lx(val)}$$", conc(r, f"y'={lx(val)}")]
        add("implicit", "hard", prob, join(sol), f"y'={lx(val)}", [check(f"subs(diff({s(Y)},x),x,{p})", s(val), "explicit branch")])
    elif k == 1:
        c = nz(r, -12, 12); p = r.choice([t for t in [-4, -3, -2, -1, 1, 2, 3, 4, 6] if c % t == 0]); q = c // p
        if not fresh(("im2", c, p)): return
        val = R(-q, p); Y = c / x
        prob = f"គេឱ្យទំនាក់ទំនង $xy={c}$ ។ ធ្វើដេរីវេលើអង្គទាំងពីរ រួចរក $y'$ ត្រង់ចំណុច $({p};{q})$ ។"
        sol = ["ធ្វើដេរីវេលើអង្គទាំងពីរ ដោយប្រើរូបមន្តផលគុណ ៖", "$$y+xy'=0$$", "ចំពោះ $x\\neq0$ គេបាន $y'=-\\frac{y}{x}$ ។", f"ត្រង់ចំណុច $({p};{q})$ គេបាន $y'={lx(val)}$ ។", conc(r, f"y'={lx(val)}")]
        add("implicit", "medium", prob, join(sol), f"y'={lx(val)}", [check(f"subs(diff({s(Y)},x),x,{p})", s(val), "explicit")])
    else:
        c = r.randint(1, 6); q = r.randint(1, 6); p = R(q * q, c)
        if not fresh(("im3", c, q)): return
        val = R(c, 2 * q); Y = SQ(c * x)
        prob = f"គេឱ្យខ្សែកោង $y^2={c}x$ ។ រក $y'$ ត្រង់ចំណុច $\\left({lx(p)};{q}\\right)$ ។".replace("y^2=1x", "y^2=x")
        sol = ["ធ្វើដេរីវេលើអង្គទាំងពីរ ៖", f"$$2yy'={c}$$", f"ចំពោះ $y\\neq0$ គេបាន $y'=\\frac{{{c}}}{{2y}}$ ។", f"ចំពោះ $y={q}$ គេបាន $y'={lx(val)}$ ។", conc(r, f"y'={lx(val)}")]
        add("implicit", "medium", prob, join(sol), f"y'={lx(val)}", [check(f"subs(diff({s(Y)},x),x,{s(p)})", s(val), "explicit")])

# ---------- sign of f', tables ----------
def signs_for(d, pts):
    """pts: sorted list of (value, 'z' zero | 'x' excluded). returns cols, sign row"""
    vals = [p[0] for p in pts]
    edges = [vals[0] - 1] + [(vals[i] + vals[i + 1]) / 2 for i in range(len(vals) - 1)] + [vals[-1] + 1]
    row = [""]
    for i, e in enumerate(edges):
        row.append("+" if d.subs(x, e) > 0 else "-")
        if i < len(pts): row.append("0" if pts[i][1] == "z" else "\\|")
    row.append("")
    return ["-\\infty"] + [lx(v) for v in vals] + ["+\\infty"], row
def sign_arr(cols, row, name="f"):
    n = 2 * len(cols) - 1
    xr = []
    for i, c in enumerate(cols):
        xr.append(c)
        if i < len(cols) - 1: xr.append("")
    return "\\begin{array}{c|" + "c" * n + "}\nx & " + " & ".join(xr) + " \\\\\n\\hline\n" + name + "'(x) & " + " & ".join(row) + "\n\\end{array}"

def t_study_cubic(r):
    r1, r2 = sorted(r.sample(range(-4, 6), 2)); k = r.choice([6, 6, 3, 12, -6, -3])
    dp = k * (x - r1) * (x - r2)
    C = r.randint(-5, 6)
    f = sp.integrate(sp.expand(dp), x) + C
    if not fresh(f): return
    d = sp.expand(dp); f1, f2 = f.subs(x, r1), f.subs(x, r2)
    pts = [(r1, "z"), (r2, "z")]
    cols, row = signs_for(dp, pts)
    up = k > 0
    limL, limR = ("-\\infty", "+\\infty") if up else ("+\\infty", "-\\infty")
    tab = variation_table(cols, row, [limL, "\\nearrow" if up else "\\searrow", lx(f1), "\\searrow" if up else "\\nearrow", lx(f2), "\\nearrow" if up else "\\searrow", limR])
    prob = r.choice([f"គេឱ្យអនុគមន៍ $f(x)={lx(f)}$ ។ ក. គណនា $f'(x)$ ។\nខ. ដោះស្រាយសមីការ $f'(x)=0$ ។\nគ. សិក្សាសញ្ញានៃ $f'(x)$ រួចសង់តារាងអថេរភាពនៃ $f$ ។",
                     f"គណនាដេរីវេនៃ $f(x)={lx(f)}$ រួចសង់តារាងអថេរភាពនៃ $f$ ។"])
    inc = (f"$(-\\infty;{r1})$ និង $({r2};+\\infty)$", f"$({r1};{r2})$") if up else (f"$({r1};{r2})$", f"$(-\\infty;{r1})$ និង $({r2};+\\infty)$")
    mx, mn = ((r1, f1), (r2, f2)) if up else ((r2, f2), (r1, f1))
    fx = f"f'(x)={k}{par(x-r1)}{par(x-r2)}"
    c1 = [f"ដេរីវេទី១ ៖ $$f'(x)={lx(d)}={k}{par(x-r1)}{par(x-r2)}$$"]
    c2 = [f"បើ $f'(x)=0$ នោះ $x={r1}$ ឬ $x={r2}$ ។", f"តម្លៃនៃអនុគមន៍ត្រង់ឫសទាំងនោះ ៖ $f({r1})={lx(f1)}$ និង $f({r2})={lx(f2)}$ ។"]
    c3 = ["សញ្ញានៃ $f'(x)$ ជាសញ្ញានៃត្រីធាដឺក្រេទី២ ៖ ដូចសញ្ញានៃមេគុណ $" + str(k) + "$ នៅក្រៅឫស និងផ្ទុយពីនោះនៅចន្លោះឫស ។",
          f"តារាងអថេរភាព ៖ $$ {tab} $$", f"អនុគមន៍កើនលើ {inc[0]} ហើយចុះលើ {inc[1]} ។",
          f"អនុគមន៍មានអតិបរមាស្មើនឹង ${lx(mx[1])}$ ត្រង់ $x={mx[0]}$ និងអប្បបរមាស្មើនឹង ${lx(mn[1])}$ ត្រង់ $x={mn[0]}$ ។"]
    two = has_parts(prob); pre = ["អនុគមន៍ពហុធាកំណត់លើ $D=IR$ ។"]
    if two:
        sol = parts(prob, [c1 + [f"ដូចនេះ ${B(fx)}$ ។"], c2 + [f"ដូចនេះ ${B(f'x={r1}')}$ ឬ ${B(f'x={r2}')}$ ។"], c3], pre=pre)
    else:
        sol = pre + c1 + c2 + c3 + [conc(r, fx)]
    add("sign_of_derivative", "bacii", prob, join(sol), fx + (f",\\ x={r1},\\ x={r2}" if two else ""),
        [check(f"diff({s(f)},x)", s(d), "f'"), check(f"subs(diff({s(f)},x),x,{r1})", 0, "root"), check(f"subs(diff({s(f)},x),x,{r2})", 0, "root"), check(f"subs({s(f)},x,{r1})", s(f1), "f(r1)"), check(f"subs({s(f)},x,{r2})", s(f2), "f(r2)")],
        [{"type": "variation_table", "latex": tab, "image": None, "alt_km": "តារាងអថេរភាពនៃអនុគមន៍ដឺក្រេទី៣"}])

def t_sign_rat(r):
    rt = nz(r, -4, 4); e = r.randint(1, 4); be = r.randint(-4, 4)
    v = x - rt; u = sp.expand((x + be) * v + e * e); f = u / v
    if not fresh(f): return
    d = 1 - e * e / v**2; num = sp.expand(v**2 - e * e); fd = sp.factor(num / v**2); z1, z2 = rt - e, rt + e
    pts = [(z1, "z"), (rt, "x"), (z2, "z")]
    cols, row = signs_for(fd, pts)
    tab = sign_arr(cols, row)
    fl = "\\frac{" + lx(u) + "}{" + lx(v) + "}"
    prob = r.choice([f"គេឱ្យ $f(x)={fl}$ ។ គណនា $f'(x)$ រួចសិក្សាសញ្ញានៃ $f'(x)$ ។", f"រកដែនកំណត់នៃ $f(x)={fl}$ គណនា $f'(x)$ ហើយសង់តារាងសញ្ញានៃដេរីវេទី១ ។"])
    du = sp.diff(u, x)
    dd_ = f"D=IR-\\{{{rt}\\}}"; fx_ = f"f'(x)={lx(fd)}"
    pos_ = f"f'(x)>0:\\ x\\in(-\\infty;{z1})\\cup({z2};+\\infty)"; neg_ = f"f'(x)<0:\\ x\\in({z1};{rt})\\cup({rt};{z2})"
    sol = [dom_excl(r, "f", v, [rt]), r.choice(R_QUOT) + " ៖", f"$$f'(x)=\\frac{{{par(du)}{par(v)}-{par(u)}}}{{{par(v)}^2}}=\\frac{{{lx(num)}}}{{{par(v)}^2}}$$",
           f"ភាគបែង ${par(v)}^2>0$ លើ $D$ ដូច្នេះ $f'(x)$ មានសញ្ញាតាមភាគយក ${lx(num)}$ ។", f"បើ $f'(x)=0$ នោះ $x={z1}$ ឬ $x={z2}$ ។", f"សញ្ញាដេរីវេទី១ ៖ $$ {tab} $$",
           f"ដូចនេះ ${B(dd_)}$ , ${B(fx_)}$ ហើយ ${B(pos_)}$ , ${B(neg_)}$ ។"]
    add("sign_of_derivative", "hard", prob, join(sol), f"{dd_},\\ {fx_},\\ {pos_},\\ {neg_}",
        [check(f"diff(({s(u)})/({s(v)}),x)", s(fd), "f'"), check(f"subs(diff(({s(u)})/({s(v)}),x),x,{z1})", 0, "root"), check(f"subs(diff(({s(u)})/({s(v)}),x),x,{z2})", 0, "root")],
        [{"type": "sign_table", "latex": tab, "image": None, "alt_km": "តារាងសញ្ញានៃដេរីវេទី១"}])

def t_solve_k(r):
    r1, r2 = sorted(r.sample(range(-4, 6), 2)); c = r.choice([1, 2, 3]); kk = nz(r, -6, 8); C = r.randint(-5, 5)
    target = 3 * c * (x - r1) * (x - r2) + kk
    f = sp.integrate(sp.expand(target), x) + C
    if not fresh(f): return
    d = sp.expand(target); y1, y2 = f.subs(x, r1), f.subs(x, r2)
    prob = r.choice([f"គេឱ្យខ្សែកោង $(C):y={lx(f)}$ ។ រកអាប់ស៊ីសនៃចំណុចលើ $(C)$ ដែលបន្ទាត់ប៉ះមានមេគុណប្រាប់ទិសស្មើនឹង ${kk}$ ។", f"គេមាន $f(x)={lx(f)}$ ។ ដោះស្រាយសមីការ $f'(x)={kk}$ ។"])
    sol = [f"ដេរីវេ ៖ $$f'(x)={lx(d)}$$".replace("f'(x)", "y'" if "(C)" in prob else "f'(x)"), "មេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះជាតម្លៃនៃដេរីវេ ។ យើងដោះស្រាយ ៖" if "(C)" in prob else "យើងដោះស្រាយ ៖",
           f"$${lx(d)}={kk}$$", f"$${lx(sp.expand(target-kk))}=0$$", f"$${3*c}{par(x-r1)}{par(x-r2)}=0$$", f"គេបាន $x={r1}$ ឬ $x={r2}$ ។", conc(r, f"x={r1},\\ x={r2}")]
    add("solve_derivative_equation", "medium", prob, join(sol), f"x={r1},\\ x={r2}", [check(f"subs(diff({s(f)},x),x,{r1})", kk, "root 1"), check(f"subs(diff({s(f)},x),x,{r2})", kk, "root 2")])

def pgf(e): return str(e).replace("**", "^")
PNGCOUNT = [0]
def t_slope_graph(r):
    k = r.randrange(4)
    if k == 0: f = r.choice([1, -1]) * x**2 + r.randint(-3, 3) * x + r.randint(-3, 3); a = r.randint(-2, 2)
    elif k == 1: f = x**3 + nz(r, -3, 3) * x + r.randint(-2, 2); a = r.choice([-1, 1, 2, 0])
    elif k == 2:
        b = r.randint(-2, 2); c = r.randint(1, 2); f = SQ(x + c * c - 1 + b); a = 1 - b
    else: 
        b = r.randint(-2, 2); kk = r.choice([1, 2, 3, 4, -2, -1]); f = kk / (x + b); a = 1 - b
    if not fresh(("sg", f, a)): return
    d = sp.diff(f, x); m_ = d.subs(x, a); ya = f.subs(x, a)
    if not (m_.is_rational and ya.is_rational): return
    T = ya + m_ * (x - a)
    if k == 2:
        fl = "\\sqrt{" + lx(f.args[0]) + "}"; dlat = "\\frac{1}{2\\sqrt{" + lx(f.args[0]) + "}}"
    elif k == 3:
        fl = ("-" if kk < 0 else "") + "\\frac{" + str(abs(kk)) + "}{" + lx(x + b) + "}"; dlat = lx(sp.factor(d))
    else: fl = lx(f); dlat = lx(d)
    lo, hi = float(a) - 4, float(a) + 4
    ylo, yhi = float(ya) - 6, float(ya) + 6
    extra = f"\\addplot[dashed,domain={lo}:{hi}] {{{pgf(T)}}};\n\\addplot[only marks] coordinates {{({a},{ya})}};\n"
    tk = tikz_graph(pgf(f), int(lo), int(hi), int(ylo), int(yhi), extra)
    if k == 2:                                    # the curve starts at the start of the domain
        tk = tk.replace(f"\\addplot[thick,domain={int(lo)}:", f"\\addplot[thick,domain={max(int(lo), -(f.args[0] - x))}:", 1)
    if k == 3:                                    # never join the two branches across the pole
        tk = tk.replace("samples=200]", f"samples=200,unbounded coords=jump,restrict y to domain={int(ylo) - 1}:{int(yhi) + 1}]", 1)
    tk = re.sub(r"(?<![\d.])(-?\d+)\.0(?!\d)", r"\1", tk)              # -3 in the figure source, never -3.0
    Tl = lx(T)
    prob = f"គេឱ្យខ្សែកោង $(C):y={fl}$ និងចំណុច $A({a};{lx(ya)})$ លើ $(C)$ ។ គណនាមេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះនឹង $(C)$ ត្រង់ $A$ រួចសង់ខ្សែកោង និងបន្ទាត់ប៉ះនោះ ។"
    dtxt = "" if k < 2 else (f"ដែនកំណត់ $D=IR-\\{{{-b}\\}}$ ។ " if k == 3 else f"ដែនកំណត់ $D=\\left[{lx(-(f.args[0] - x))};+\\infty\\right)$ ហើយដេរីវេមានចំពោះ ${lx(f.args[0])}>0$ ។ ")
    sol = [f"{dtxt}ដេរីវេគឺ $y'={dlat}$ ។", f"មេគុណប្រាប់ទិសនៃបន្ទាត់ប៉ះត្រង់ $A$ ស្មើនឹងដេរីវេត្រង់ $x={a}$ ៖ $$y'({a})={lx(m_)}$$", f"បន្ទាត់ប៉ះមានសមីការ $y-y_0=y'(x_0)(x-x_0)$ ដូច្នេះ $y={Tl}$ ។", "សង់ខ្សែកោងជាមួយបន្ទាត់ប៉ះដូចរូប ។", conc(r, f"y'({a})={lx(m_)}")]
    png = dict(f=f, xmin=lo, xmax=hi, ymin=ylo, ymax=yhi, tangent=T, points=[(a, ya)], asymptotes=[("v", -b)] if k == 3 else [])
    add("slope_with_graph", "medium", prob, join(sol), f"y'({a})={lx(m_)}", [check(f"subs(diff({s(f)},x),x,{a})", s(m_), "slope"), check(f"subs({s(f)},x,{a})", s(ya), "point on curve")],
        [{"type": "graph", "latex": tk, "image": None, "alt_km": f"ខ្សែកោង និងបន្ទាត់ប៉ះត្រង់ចំណុច A"}], png)

def t_error(r):
    k = r.randrange(3)
    if k == 0:
        u, v = lin(r), r.choice([quad, lambda q: x**2 + nz(q, -5, 5)])(r); du, dv = sp.diff(u, x), sp.diff(v, x)
        f = u * v
        if not fresh(("er", f)): return
        wrong = sp.expand(du * dv); right = sp.expand(du * v + u * dv)
        prob = f"សិស្សម្នាក់សរសេរថា ដេរីវេនៃ $f(x)={par(u)}{par(v)}$ គឺ $f'(x)={cx(du)}{par(dv)}={lx(wrong)}$ ។ តើគាត់ត្រឹមត្រូវឬទេ ? បើមិនត្រឹមត្រូវ ចូរកែ ។"
        sol = ["សិស្សនោះមិនត្រឹមត្រូវទេ ព្រោះដេរីវេនៃផលគុណមិនស្មើនឹងផលគុណនៃដេរីវេឡើយ ។", f"រូបមន្តត្រឹមត្រូវគឺ $(uv)'=u'v+uv'$ ។ {setuv(r,u,v)}", f"$$f'(x)={cx(du)}{par(v)}+{cx(dv)}{par(u)}={lx(right)}$$", conc(r, f"f'(x)={lx(right)}")]
        add("error_correction", "medium", prob, join(sol), f"f'(x)={lx(right)}", [check(f"diff({s(f)},x)", s(right), "correct derivative")])
    elif k == 1:
        u, v = lin(r), monic(r)
        if sp.gcd(u, v) != 1 or sp.diff(u,x)*v == u: return
        if not fresh(("er", u / v)): return
        du = sp.diff(u, x); wrongn = sp.expand(u - du * v); rightn = sp.expand(du * v - u); fl = f"\\frac{{{lx(u)}}}{{{lx(v)}}}"
        if rightn == 0: return
        prob = f"ក្នុងកិច្ចការមួយ សិស្សសរសេរ $f'(x)=\\frac{{{lx(wrongn)}}}{{{par(v)}^2}}$ សម្រាប់អនុគមន៍ $f(x)={fl}$ ។ រកកំហុស រួចគណនាឡើងវិញ ។"
        sol = ["សិស្សបានប្ដូរលំដាប់តួក្នុងភាគយកនៃរូបមន្តផលចែក គឺសរសេរ $uv'-u'v$ ជំនួសឱ្យ $u'v-uv'$ ដូច្នេះលទ្ធផលខុសសញ្ញា ។", f"គណនាត្រឹមត្រូវ ៖ $$f'(x)=\\frac{{{pa(du)}{par(v)}-{par(u)}(1)}}{{{par(v)}^2}}=\\frac{{{lx(rightn)}}}{{{par(v)}^2}}$$", conc(r, f"f'(x)=\\frac{{{lx(rightn)}}}{{{par(v)}^2}}")]
        add("error_correction", "medium", prob, join(sol), f"f'(x)=\\frac{{{lx(rightn)}}}{{{par(v)}^2}}", [check(f"diff(({s(u)})/({s(v)}),x)", f"({s(rightn)})/({s(v)})**2", "correct derivative")])
    else:
        u = r.choice([lambda q: x**2 + nz(q, -6, 6), lambda q: q.choice([2, 3, 4]) * x + nz(q, -5, 5)])(r); n = r.randint(3, 6); du = sp.diff(u, x); f = u**n
        if not fresh(("er", f)): return
        prob = f"មិត្តរបស់អ្នកគណនា $\\left[{par(u)}^{{{n}}}\\right]'={n}{par(u)}^{{{n-1}}}$ ។ ពន្យល់ថាតើគាត់ភ្លេចអ្វី រួចសរសេរចម្លើយត្រឹមត្រូវ ។"
        c, pp = contentform(n, du); dl = ("" if c == 1 else str(c)) + ("" if pp == 1 else pa(pp)) + par(u) + f"^{{{n-1}}}"
        sol = [f"គាត់ភ្លេចគុណនឹងដេរីវេនៃកន្សោមខាងក្នុង ${lx(u)}$ ។", f"តាមរូបមន្ត $(u^n)'=nu'u^{{n-1}}$ ដែល $u'={lx(du)}$ ៖", f"$$\\left[{par(u)}^{{{n}}}\\right]'={n}\\cdot{pa(du)}{par(u)}^{{{n-1}}}={dl}$$", conc(r, dl)]
        add("error_correction", "easy", prob, join(sol), dl, [check(f"diff({s(f)},x)", s(c * pp * u**(n - 1)), "correct derivative")])

# ---------- driver ----------
def run(fn, quota, maxtry=None):
    n0 = len(ROWS); tries = 0; maxtry = maxtry or quota * 12
    while len(ROWS) - n0 < quota and tries < maxtry:
        tries += 1; fn(rng)
    print(f"{fn.__name__ if hasattr(fn,'__name__') else fn}: {len(ROWS)-n0}")

def spec_fresh():
    for _ in range(40):
        N = rng.choice(["f", "f", "f", "g", "h", "y"])
        sp_ = rng.choice(FAM_LIST)(rng, N)
        if fresh(sp_["f"]): return sp_, N
    return None, None
def w_plain(r):
    a, N = spec_fresh()
    if a: W_plain(r, a, N)
def w_show(r):
    a, N = spec_fresh()
    if a: W_show(r, a, N)
def w_point(r):
    a, N = spec_fresh()
    if a: W_point(r, a, N)
def w_drill(r):
    k = r.randint(2, 3); ss = []
    names = ["f", "g", "h"]
    for i in range(k):
        for _ in range(40):
            sp_ = r.choice(FAM_LIST)(r, names[i])
            if fresh(sp_["f"]): ss.append(sp_); break
    if len(ss) == k: W_drill(r, ss)

def main():
    t0 = time.time()
    for fn, q in [(w_plain, 640), (w_show, 130), (w_point, 340), (w_drill, 110),
                  (t_def_point_h, 75), (t_def_point_x, 55), (t_def_general, 55), (t_def_recip, 50), (t_def_sqrt, 50), (t_recog, 45), (t_abstract, 35),
                  (t_piece, 30), (t_abs, 20), (t_uv, 40), (t_comp, 40), (t_param, 50), (t_findabc, 30), (t_canon, 30), (t_identity, 45), (t_second, 50),
                  (t_velocity, 25), (t_implicit, 30), (t_study_cubic, 45), (t_sign_rat, 35), (t_solve_k, 30), (t_slope_graph, 120), (t_error, 45)]:
        run(fn, q)
    try:
        from rules_hand import hand_rows
        hr = hand_rows()
        for row in hr:
            for fld in ("problem_km", "solution_km", "answer_latex"):
                row[fld] = tidy(row[fld])
        ROWS.extend(hr)
        print("hand", len(hr))
    except ImportError:
        print("no hand rows yet")
    seen = set(); out = []
    for row in ROWS:
        if row["id"] in seen: continue
        seen.add(row["id"]); out.append(row)
    npng = 0
    for row in out:
        p = row.pop("_png", None)
        if p and npng < 300:
            f = p.pop("f")
            row["diagrams"][0]["image"] = plot_png(row["id"], f, **p); npng += 1
    # this generator's own PNGs from earlier runs that no row refers to any more
    keep = {d["image"] for row in out for d in row["diagrams"] if d.get("image")}
    for fn in os.listdir(os.path.join(ROOT, "diagrams")):
        if fn.startswith("rules-") and fn.endswith(".png") and "diagrams/" + fn not in keep:
            os.remove(os.path.join(ROOT, "diagrams", fn))
    write_jsonl(out, "rules.jsonl")
    print("png", npng, "time", round(time.time() - t0, 1))

if __name__ == "__main__":
    main()
