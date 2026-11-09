"""Limit and continuity skills written out in full."""
from core import *
CH = "limit"
def L_(a, side=""): return f"\\lim_{{x\\to {tx(a)}{side}}}"
def factor00(rng):
    a, b, c = rng.sample(range(-6, 7), 3); k = rng.choice([1, 1, 2]); N, Dn = sp.expand(k * (x - a) * (x - b)), sp.expand((x - a) * (x - c)); w = W(rng); ft = f"\\frac{{{tx(N)}}}{{{tx(Dn)}}}"; lim = L_(a)
    if a == c or a == b: return None
    P = w.v(f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}{ft}$$", f"គេឱ្យអនុគមន៍ $f(x)={ft}$ ។ ចូរគណនា ${lim}f(x)$ ។"); A1, B1, _ = psub(N, sp.Integer(a)); A2, B2, _ = psub(Dn, sp.Integer(a))
    w.say(f"ជំនួស $x={tx(a)}$ ក្នុងភាគយក ៖ ${A1}={B1}=0$ ។"); w.say(f"ជំនួសក្នុងភាគបែង ៖ ${A2}={B2}=0$ ។"); w.say("លីមីតមានរាងមិនកំណត់ $\\frac{0}{0}$ ។ ដូច្នេះ $x=%s$ ជាឫសនៃភាគយក និងភាគបែង ។" % tx(a))
    kk = "" if k == 1 else str(k); w.say("ដាក់ជាផលគុណកត្តា ៖"); w.say(f"$${tx(N)}={kk}\\left({tx(x-a)}\\right)\\left({tx(x-b)}\\right)$$"); w.say(f"$${tx(Dn)}=\\left({tx(x-a)}\\right)\\left({tx(x-c)}\\right)$$"); w.ok(N, k * (x - a) * (x - b)); w.ok(Dn, (x - a) * (x - c))
    v = R(k * (a - b), a - c); w.chain((f"{lim}{ft}", v), (f"{lim}\\frac{{{kk}\\left({tx(x-a)}\\right)\\left({tx(x-b)}\\right)}}{{\\left({tx(x-a)}\\right)\\left({tx(x-c)}\\right)}}", v), (f"{lim}\\frac{{{kk}\\left({tx(x-b)}\\right)}}{{{tx(x-c)}}}", v), ((f"\\frac{{{kk}\\left({tx(a)}{sgn2(-b)}\\right)}}{{{tx(a)}{sgn2(-c)}}}" if k != 1 else f"\\frac{{{tx(a)}{sgn2(-b)}}}{{{tx(a)}{sgn2(-c)}}}"), v), (tx(v), v))
    w.C.append(check(f"limit(({N})/({Dn}),x,{a})", str(v), "limit"))
    return row(w.say(f"ដូចនេះ $\\boxed{{{lim}{ft}={tx(v)}}}$ ។"), CH, "steps", "steps_factor_zero_over_zero", 1, P, tx(v), "factor00")
def sgn2(v): return st(v)
def conj(rng):
    r = rng.randint(1, 6); a = rng.randint(-5, 6); p = rng.choice([1, 2, 3]); q = r * r - p * a; k = rng.choice([1, 1, 2, 3])
    root = f"\\sqrt{{{tx(p*x+q)}}}"; den = k * (x - a); w = W(rng); lim = L_(a); ft = f"\\frac{{{root}-{r}}}{{{tx(sp.expand(den))}}}"; P = f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}{ft}$$"; S = sp.sqrt(p * x + q)
    w.say(f"ជំនួស $x={tx(a)}$ ៖ $\\sqrt{{{tx(p*a+q)}}}-{r}={r}-{r}=0$ ហើយភាគបែងស្មើ $0$ ។ លីមីតមានរាងមិនកំណត់ $\\frac{{0}}{{0}}$ ។"); w.say(f"គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ ${root}+{r}$ ៖"); inner = sp.expand(p * x + q - r * r); v = R(p, 2 * r * k); dt = tx(sp.expand(den))
    w.say(f"$${lim}{ft}={lim}\\frac{{\\left({root}-{r}\\right)\\left({root}+{r}\\right)}}{{\\left({dt}\\right)\\left({root}+{r}\\right)}}$$"); w.say(f"$$={lim}\\frac{{\\left({tx(p*x+q)}\\right)-{r*r}}}{{\\left({dt}\\right)\\left({root}+{r}\\right)}}$$"); w.say(f"$$={lim}\\frac{{{tx(inner)}}}{{\\left({dt}\\right)\\left({root}+{r}\\right)}}$$")
    pk = f"{p}" if p != 1 else ""; w.ok(inner, p * (x - a)); kt = "" if k == 1 else str(k); fa = [f"${tx(sp.expand(q_))}={c_}\\left({tx(x-a)}\\right)$" for q_, c_, kk_ in ((inner, pk, p), (den, kt, k)) if kk_ != 1]; w.say(("ដោយ " + " និង ".join(fa) + " " if fa else "") + f"សម្រួលកត្តា ${tx(x-a)}$ ៖"); w.say(f"$$={lim}\\frac{{{p}}}{{{kt}\\left({root}+{r}\\right)}}$$"); w.say(f"$$=\\frac{{{p}}}{{{kt}\\left({r}+{r}\\right)}}=\\frac{{{p}}}{{{tx(2*r*k)}}}" + ("" if tx(v) == f"\\frac{{{p}}}{{{2*r*k}}}" else f"={tx(v)}") + "$$"); w.C.append(check(f"limit((sqrt({p*x+q})-{r})/({sp.expand(den)}),x,{a})", str(v), "limit"))
    return row(w.say(f"ដូចនេះ $\\boxed{{{lim}{ft}={tx(v)}}}$ ។"), CH, "steps", "steps_conjugate_each_line", 2, P, tx(v), "conj")
def at_infinity(rng):
    n = rng.choice([2, 3]); m = rng.choice([n, n, n + 1]); c1 = [rng.choice([1, 2, 3, -2, 4, 5]) if i == 0 else rng.randint(-6, 6) for i in range(n + 1)]; c2 = [rng.choice([1, 2, 3, -1, 4]) if i == 0 else rng.randint(-6, 6) for i in range(n + 1)]
    if m == n + 1: c1, c2 = c2 + [rng.randint(-5, 5)], c2; c1[0] = rng.choice([1, 2, 3, -2])
    sgnv = rng.choice(["+", "-"]); N = sum(c * x ** (len(c1) - 1 - i) for i, c in enumerate(c1)); Dn = sum(c * x ** (len(c2) - 1 - i) for i, c in enumerate(c2)); w = W(rng); lim = f"\\lim_{{x\\to{sgnv}\\infty}}"; ft = f"\\frac{{{tx(N)}}}{{{tx(Dn)}}}"; P = f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}{ft}$$"; a, b = len(c1) - 1, len(c2) - 1
    w.say("លីមីតមានរាងមិនកំណត់ $\\frac{\\infty}{\\infty}$ ។ ដាក់ស្វ័យគុណខ្ពស់បំផុតជាកត្តារួមទាំងភាគយក និងភាគបែង ៖")
    brk = lambda cs, d: "".join((tx(c) if i == 0 else fr(c, "x" + ("^{%d}" % i if i > 1 else ""))) for i, c in enumerate(cs) if c != 0 or i == 0)
    pw = lambda d: f"x^{{{d}}}"; w.say(f"$${lim}{ft}={lim}\\frac{{{pw(a)}\\left({brk(c1,a)}\\right)}}{{{pw(b)}\\left({brk(c2,b)}\\right)}}$$")
    w.say("ដោយ $\\lim_{x\\to\\pm\\infty}\\frac{c}{x^k}=0$ កន្សោមក្នុងវង់ក្រចកនីមួយៗខិតជិតមេគុណទីមួយរបស់វា ៖"); exact = sp.limit(N / Dn, x, sp.oo if sgnv == "+" else -sp.oo)
    if a == b:
        w.say(f"$$={lim}\\frac{{{brk(c1,a)}}}{{{brk(c2,b)}}}=" + (f"\\frac{{{c1[0]}}}{{{c2[0]}}}=" if tx(exact) != f"\\frac{{{c1[0]}}}{{{c2[0]}}}" else "") + f"{tx(exact)}$$"); ans = tx(exact)
    else:
        q = R(c1[0], c2[0]); w.say(f"$$={lim}x\\cdot\\frac{{{brk(c1,a)}}}{{{brk(c2,b)}}}$$"); w.say(f"$$={lim}{tx(q)}x$$" if q not in (1, -1) else f"$$={lim}{'-' if q<0 else ''}x$$"); ans = ("+" if exact == sp.oo else "-") + "\\infty"; w.say(f"$$={ans}$$")
    w.C.append(check(f"limit(({N})/({Dn}),x,{'oo' if sgnv=='+' else '-oo'})", str(exact), "limit"))
    return row(w.say(f"ដូចនេះ $\\boxed{{{lim}{ft}={ans}}}$ ។"), CH, "steps", "steps_top_power_factored", 1, P, ans, "at_infinity")
def one_sided(rng):
    a = rng.randint(-5, 5); p, q = rng.choice([1, 2, 3, -1, -2]), rng.randint(-6, 6); k = rng.choice([1, 2]); N = p * x + q; na = N.subs(x, a)
    if na == 0: return None
    Dn = (x - a) ** k; Dd = sp.expand(Dn); f = N / Dn; w = W(rng); ft = f"\\frac{{{tx(N)}}}{{{tx(Dd) if k==1 else '\\left('+tx(x-a)+'\\right)^2'}}}"; P = f"គេឱ្យ $f(x)={ft}$ ។ គណនា $\\lim_{{x\\to {tx(a)}^-}}f(x)$ និង $\\lim_{{x\\to {tx(a)}^+}}f(x)$ ។ តើ $f$ មានលីមីតត្រង់ $x={tx(a)}$ ឬទេ ?"
    A0, B0, _ = psub(N, sp.Integer(a)); w.say(f"កាលណា $x\\to{tx(a)}$ ភាគយកខិតជិត ${A0}={B0}={tx(na)}$ ។"); s = 1 if na > 0 else -1; l = sp.limit(f, x, a, "-"); r = sp.limit(f, x, a, "+"); A = lambda v: "+\\infty" if v == sp.oo else "-\\infty"
    if k == 1:
        w.say(f"បើ $x<{tx(a)}$ នោះ ${tx(x-a)}<0$ ដូច្នេះ ${tx(x-a)}\\to0^-$ ។"); w.say(f"បើ $x>{tx(a)}$ នោះ ${tx(x-a)}>0$ ដូច្នេះ ${tx(x-a)}\\to0^+$ ។")
    else: w.say(f"ដោយ $\\left({tx(x-a)}\\right)^2>0$ គ្រប់ $x\\neq{tx(a)}$ នោះភាគបែងខិតជិត $0^+$ ទាំងសងខាង ។")
    w.say(f"ភាគយក{'វិជ្ជមាន' if na>0 else 'អវិជ្ជមាន'} ដូច្នេះ ៖"); w.say(f"$$\\lim_{{x\\to {tx(a)}^-}}f(x)={A(l)}\\ ,\\quad\\lim_{{x\\to {tx(a)}^+}}f(x)={A(r)}$$"); w.C.append(check(f"limit(({N})/({Dn}),x,{a},'-')", str(l), "left")); w.C.append(check(f"limit(({N})/({Dn}),x,{a},'+')", str(r), "right"))
    if l != r: w.say(f"លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ។"); w.say(f"ដូចនេះ $\\boxed{{f\\text{{ គ្មានលីមីតត្រង់ }}x={tx(a)}}}$ ទេ ។"); ans = "\\text{no limit}"
    else: w.say(f"ដោយលីមីតឆ្វេងស្មើលីមីតស្តាំ នោះ $f$ មានលីមីតត្រង់ $x={tx(a)}$ ។"); w.say(f"ដូចនេះ $\\boxed{{\\lim_{{x\\to {tx(a)}}}f(x)={A(l)}}}$ ។"); ans = A(l)
    return row(w, CH, "steps", "steps_one_sided_signs", 2, P, ans, "one_sided")
def trig(rng):
    a, b = rng.sample([1, 2, 3, 4, 5, 6, 7], 2); kind = rng.choice(["ss", "st", "tx"]); w = W(rng); lim = "\\lim_{x\\to 0}"; ax = lambda c, nm: f"\\{nm} {c if c!=1 else ''}x"
    if kind == "ss": fn, gn = "sin", "sin"
    elif kind == "st": fn, gn = "sin", "tan"
    else: fn, gn = "tan", "sin"
    F = getattr(sp, fn)(a * x); G = getattr(sp, gn)(b * x); ft = f"\\frac{{{ax(a,fn)}}}{{{ax(b,gn)}}}"; v = R(a, b); P = f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}{ft}$$"; aa, bb = (f"{a}x" if a != 1 else "x"), (f"{b}x" if b != 1 else "x")
    w.say("ជំនួស $x=0$ លីមីតមានរាងមិនកំណត់ $\\frac{0}{0}$ ។"); w.say("ប្រើរូបមន្ត $\\lim_{u\\to 0}\\frac{\\sin u}{u}=1$" + (" ។" if kind == "ss" else " និង $\\lim_{u\\to 0}\\frac{\\tan u}{u}=1$ ។")); w.say(f"$${lim}{ft}={lim}\\left(\\frac{{{ax(a,fn)}}}{{{aa}}}\\times\\frac{{{bb}}}{{{ax(b,gn)}}}\\times\\frac{{{aa}}}{{{bb}}}\\right)$$"); w.say(f"$$=1\\times1\\times{ratio(a,b)}" + ("" if b == 1 or tx(v) == ratio(a, b) else f"={tx(v)}") + ("" if b != 1 else f"={tx(v)}") + "$$"); w.C.append(check(f"limit({F}/({G}),x,0)", str(v), "limit"))
    return row(w.say(f"ដូចនេះ $\\boxed{{{lim}{ft}={tx(v)}}}$ ។"), CH, "steps", "steps_trig_reshaped", 1, P, tx(v), "trig")
def explog(rng):
    a, b = rng.choice([1, 2, 3, 4, 5, -2, -3]), rng.choice([1, 2, 3, 4, 5, 7]); kind = rng.choice(["e", "l"]); w = W(rng); lim = "\\lim_{x\\to 0}"; ca = f"{a}x" if a not in (1, -1) else ("x" if a == 1 else "-x"); bx = f"{b}x" if b != 1 else "x"; v = R(a, b)
    if kind == "e": top, F, form, u = f"e^{{{ca}}}-1", sp.exp(a * x) - 1, "\\lim_{u\\to 0}\\frac{e^{u}-1}{u}=1", f"e^{{{ca}}}-1"
    else: top, F, form, u = f"\\ln\\left(1{'+' if a>0 else ''}{ca}\\right)", sp.log(1 + a * x), "\\lim_{u\\to 0}\\frac{\\ln(1+u)}{u}=1", None
    ft = f"\\frac{{{top}}}{{{bx}}}"; P = f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}{ft}$$"; w.say("ជំនួស $x=0$ លីមីតមានរាងមិនកំណត់ $\\frac{0}{0}$ ។"); w.say(f"តាង $u={ca}$ ។ បើ $x\\to0$ នោះ $u\\to0$ ។ ប្រើរូបមន្ត ${form}$ ៖"); w.say(f"$${lim}{ft}={lim}\\left(\\frac{{{top}}}{{{ca}}}\\times\\frac{{{ca}}}{{{bx}}}\\right)$$"); w.say(f"$$=1\\times{ratio(a,b)}={tx(v)}$$".replace(f"{ratio(a,b)}={ratio(a,b)}", ratio(a, b))); w.C.append(check(f"limit(({F})/({b}*x),x,0)", str(v), "limit"))
    return row(w.say(f"ដូចនេះ $\\boxed{{{lim}{ft}={tx(v)}}}$ ។"), CH, "steps", "steps_exp_log_standard_shaped", 1, P, tx(v), "explog")
def continuity(rng):
    c = rng.randint(-3, 4); p, q = rng.choice([1, 2, -1]), rng.randint(-4, 4); r = rng.randint(-4, 4); m = rng.choice([1, 2, 3, -1, -2]); w = W(rng); left = p * x ** 2 + q * x + r; A, B, val = psub(left, sp.Integer(c)); k = sp.Symbol("k")
    if c == 0: return None
    kv = R(val - m * c, 1); P = f"គេឱ្យអនុគមន៍ $$f(x)=\\begin{{cases}} {tx(left)}, & x\\leq {c} \\\\ {tx(m*x)}+k, & x>{c} \\end{{cases}}$$ រកតម្លៃ $k$ ដើម្បីឱ្យ $f$ ជាប់ត្រង់ $x={c}$ ។"
    w.say(f"សិក្សាភាពជាប់ត្រង់ $x={c}$ ៖"); w.say(f"$$f({c})={A}={B}={tx(val)}$$"); w.say(f"$$\\lim_{{x\\to {c}^-}}f(x)=\\lim_{{x\\to {c}^-}}\\left({tx(left)}\\right)={tx(val)}$$"); w.say(f"$$\\lim_{{x\\to {c}^+}}f(x)=\\lim_{{x\\to {c}^+}}\\left({tx(m*x)}+k\\right)={('' if abs(m)==1 else tx(m)) if m>0 else ('-' if m==-1 else tx(m))}{pp(c)}+k={tx(m*c)}+k$$"); w.say(f"$f$ ជាប់ត្រង់ $x={c}$ លុះត្រាតែ $\\lim_{{x\\to {c}^-}}f(x)=\\lim_{{x\\to {c}^+}}f(x)=f({c})$ ។")
    w.say(f"$${tx(m*c)}+k={tx(val)}\\Leftrightarrow k={tx(val)}{sgn2(-m*c)}={tx(kv)}$$"); w.C.append(check(f"({left}).subs(x,{c})" if False else f"subs({left},x,{c})", f"({m*c})+({kv})", "join"))
    return row(w.say(f"ដូចនេះ $\\boxed{{k={tx(kv)}}}$ ។"), CH, "steps", "steps_continuity_parameter_linear", 2, P, f"k={tx(kv)}", "continuity")
def ln_zero(rng):
    a = rng.choice([1, 2, 3, 4]); b = rng.randint(1, 5); n = rng.choice([1, 2]); kind = rng.choice(["xln", "lnx"]); w = W(rng)
    if kind == "xln":
        f = a * x ** n * sp.log(x) + b; ft = tx(f); lim = "\\lim_{x\\to 0^+}"; P = f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}\\left({ft}\\right)$$"; w.say("លីមីតនៃ $%s$ មានរាងមិនកំណត់ $0\\times\\infty$ ។" % tx(x**n*sp.log(x))); w.say("ប្រើរូបមន្ត $\\lim_{x\\to 0^+}x\\ln x=0$ ។")
        if n == 2: w.say("$$x^{2}\\ln x=x\\left(x\\ln x\\right)$$ ដោយ $x\\to0^+$ និង $x\\ln x\\to0$ នោះ $x^{2}\\ln x\\to0$ ។")
        w.say(f"$${lim}\\left({ft}\\right)={a}\\times0+{b}={b}$$"); v = sp.Integer(b); w.C.append(check(f"limit({f},x,0,'+')", str(v), "limit")); ans = tx(v); full = f"{lim}\\left({ft}\\right)={ans}"
    else:
        f = (a * sp.log(x) + b) / x ** n; ft = f"\\frac{{{tx(a*sp.log(x)+b)}}}{{{tx(x**n)}}}"; lim = "\\lim_{x\\to+\\infty}"; P = f"ចូរគណនាលីមីតខាងក្រោមនេះ ៖ $${lim}{ft}$$"; w.say("បំបែកជាផលបូកនៃប្រភាគពីរ ៖"); w.chain((ft, f), (f"{a}\\cdot\\frac{{\\ln x}}{{{tx(x**n)}}}+\\frac{{{b}}}{{{tx(x**n)}}}", a * sp.log(x) / x ** n + b / x ** n)); w.say("ដោយ $\\lim_{x\\to+\\infty}\\frac{\\ln x}{x}=0$ និង $\\lim_{x\\to+\\infty}\\frac{%d}{%s}=0$ នោះ ៖" % (b, tx(x**n)))
        if n == 2: w.say("ហើយ $\\frac{\\ln x}{x^{2}}=\\frac{\\ln x}{x}\\times\\frac{1}{x}\\to0$ ។")
        w.say(f"$${lim}{ft}={a}\\times0+0=0$$"); w.C.append(check(f"limit({f},x,oo)", "0", "limit")); ans = "0"; full = f"{lim}{ft}=0"
    return row(w.say(f"ដូចនេះ $\\boxed{{{full}}}$ ។"), CH, "steps", "steps_ln_standard_forms", 1, P, ans, "ln_zero")
ALL = [(factor00, 220), (conj, 180), (at_infinity, 220), (one_sided, 200), (trig, 90), (explog, 80), (continuity, 200), (ln_zero, 40)]
