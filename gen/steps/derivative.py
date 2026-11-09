"""Derivative skills written out in full: each rule, expansion, root, sign and substituted value is shown."""
from core import *
def sg(b): return "" if b == 0 else (f"+{b}" if b > 0 else f"{b}")
CH = "derivative"
def f_(p): return tx(sp.expand(p))
def quad_roots(w, p, var="x"):
    """Solve a quadratic with integer/rational roots, printing Delta."""
    P = sp.Poly(p, x); a, b, c = P.all_coeffs(); D = b ** 2 - 4 * a * c
    w.say(f"យើងមាន $a={tx(a)}$ , $b={tx(b)}$ , $c={tx(c)}$ ។")
    w.chain(("\\Delta", D), (f"b^2-4ac={pp(b)}^2-4{pp(a)}{pp(c)}", D), (tx(D), D))
    r = sp.sqrt(D); x1, x2 = sorted([(-b - r) / (2 * a), (-b + r) / (2 * a)])
    w.say(f"ដោយ $\\Delta>0$ សមីការមានឫសពីរ ៖")
    a1, a2 = ((-b - r) / (2 * a), (-b + r) / (2 * a))
    w.say(f"$$x_1=\\frac{{-b-\\sqrt{{\\Delta}}}}{{2a}}=\\frac{{{tx(-b)}-{tx(r)}}}{{{tx(2*a)}}}={tx(a1)}$$")
    w.say(f"$$x_2=\\frac{{-b+\\sqrt{{\\Delta}}}}{{2a}}=\\frac{{{tx(-b)}+{tx(r)}}}{{{tx(2*a)}}}={tx(a2)}$$")
    w.ok(P.as_expr().subs(x, a1), 0, "root"); w.ok(P.as_expr().subs(x, a2), 0, "root")
    return x1, x2
def show_val(w, p, v, name="f"):
    a, b, val = psub(p, v)
    w.chain((f"{name}({tx(v)})", val), (a, val), (b, val), (tx(val), val))
    return val
def quotient(rng):
    a = rng.choice([1, 1, 2, 3, -1]); b, c = rng.randint(-6, 6), rng.randint(-7, 7); d = rng.choice([1, 1, 2, 3]); e = rng.randint(-5, 5)
    if e == 0: return None
    u, v = a * x ** 2 + b * x + c, d * x + e; f = u / v
    if sp.cancel(f).as_numer_denom()[1] == 1 or sp.gcd(u, v) != 1: return None
    w = W(rng); du, dv = sp.diff(u, x), sp.diff(v, x)
    P = w.v(f"គេឱ្យអនុគមន៍ $f(x)=\\frac{{{tx(u)}}}{{{tx(v)}}}$ ។ គណនាដេរីវេ $f'(x)$ ។", f"ចូរគណនាដេរីវេ $f'(x)$ ចំពោះអនុគមន៍ $f(x)=\\frac{{{tx(u)}}}{{{tx(v)}}}$ ។", f"រកដេរីវេទី១ នៃអនុគមន៍ $y=\\frac{{{tx(u)}}}{{{tx(v)}}}$ ។")
    w.say(f"តាង $u={tx(u)}$ និង $v={tx(v)}$ ។ គេបាន $u'={tx(du)}$ និង $v'={tx(dv)}$ ។")
    w.say("តាមរូបមន្ត $\\left(\\frac{u}{v}\\right)'=\\frac{u'v-uv'}{v^2}$ ៖")
    n1, n2 = sp.expand(du * v), sp.expand(u * dv); num = sp.expand(n1 - n2); den = v ** 2; D = f"\\left({tx(v)}\\right)^2"
    w.chain(("f'(x)", sp.diff(f, x)), (f"\\frac{{\\left({tx(du)}\\right)\\left({tx(v)}\\right)-\\left({tx(u)}\\right)\\left({tx(dv)}\\right)}}{{{D}}}", (du * v - u * dv) / den),
            (f"\\frac{{\\left({tx(n1)}\\right)-\\left({tx(n2)}\\right)}}{{{D}}}", (n1 - n2) / den), (f"\\frac{{{tx(num)}}}{{{D}}}", num / den))
    return row(w.say(f"ដូចនេះ $\\boxed{{f'(x)=\\frac{{{tx(num)}}}{{{D}}}}}$ ។"), CH, "steps", "steps_quotient_expanded", 1, P, f"f'(x)=\\frac{{{tx(num)}}}{{{D}}}", "quotient")
def product(rng):
    k = rng.choice([1, 1, 2, 3, -1, -2]); a, b = rng.choice([1, 2, 3, -1]), rng.randint(-5, 5); c = rng.choice([0, 0, 1, 2, -3]); kind = rng.choice(["e", "e", "ln"])
    u = a * x + b if c == 0 else x ** 2 + c * x + b; v = sp.exp(k * x) if kind == "e" else sp.log(x)
    if u == 0 or (kind == "e" and False): return None
    w = W(rng); du, dv = sp.diff(u, x), sp.diff(v, x); f = u * v
    P = w.v(f"ចូរគណនាដេរីវេនៃអនុគមន៍ $f(x)={tx(f)}$ ។", f"គេឱ្យអនុគមន៍ $f(x)={tx(f)}$ ។ ចូររកដេរីវេ $f'(x)$ ។")
    w.say(f"តាង $u={tx(u)}$ និង $v={tx(v)}$ ។")
    w.say(f"គេបាន $u'={tx(du)}$ និង $v'={tx(dv)}$ ។")
    w.say("តាមរូបមន្ត $(uv)'=u'v+uv'$ ៖")
    if kind == "e":
        inner = sp.expand(du + k * u); res = inner * v
        w.chain(("f'(x)", sp.diff(f, x)), (f"\\left({tx(du)}\\right){tx(v)}+\\left({tx(u)}\\right)\\left({tx(dv)}\\right)", du * v + u * dv),
                (f"{tx(v)}\\left[{tx(du)}+{pp(k)}\\left({tx(u)}\\right)\\right]", v * (du + k * u)), (f"{br(inner)}{tx(v)}", res))
        ans = f"f'(x)={br(inner)}{tx(v)}"
    else:
        rest = sp.expand(u / x); res = du * sp.log(x) + rest
        w.chain(("f'(x)", sp.diff(f, x)), (f"\\left({tx(du)}\\right)\\ln x+\\left({tx(u)}\\right)\\cdot\\frac{{1}}{{x}}", du * sp.log(x) + u / x), (tx(res), res))
        ans = f"f'(x)={tx(res)}"
    return row(w.say(f"ដូចនេះ $\\boxed{{{ans}}}$ ។"), CH, "steps", "steps_product_expanded", 1, P, ans, "product")
def chainrule(rng):
    a, b, c = rng.choice([1, 2, 3]), rng.randint(-5, 5), rng.randint(-6, 6); n = rng.choice([2, 3, 4, 5, "s"]); u = a * x ** 2 + b * x + c
    if sp.Poly(u, x).degree() < 2: return None
    w = W(rng); du = sp.diff(u, x)
    if n == "s":
        if (b * b - 4 * a * c) >= 0: return None
        f = sp.sqrt(u); ft = f"\\sqrt{{{tx(u)}}}"
        P = f"ចូរគណនាដេរីវេនៃអនុគមន៍ $f(x)={ft}$ ។"
        w.say(f"តាង $u={tx(u)}$ ។ គេបាន $u'={tx(du)}$ ។"); w.say("តាមរូបមន្ត $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ ៖")
        h = sp.expand(du / 2); res = h / f
        w.chain(("f'(x)", sp.diff(f, x)), (f"\\frac{{\\left({tx(u)}\\right)'}}{{2{ft}}}", du / (2 * f)), (f"\\frac{{{tx(du)}}}{{2{ft}}}", du / (2 * f)), (f"\\frac{{{tx(h)}}}{{{ft}}}", res))
        ans = f"f'(x)=\\frac{{{tx(h)}}}{{{ft}}}"
    else:
        f = u ** n; ft = f"\\left({tx(u)}\\right)^{{{n}}}"
        P = f"ចូរគណនាដេរីវេនៃអនុគមន៍ $f(x)={ft}$ ។"
        w.say(f"តាង $u={tx(u)}$ ។ គេបាន $u'={tx(du)}$ ។"); w.say(f"តាមរូបមន្ត $(u^n)'=nu'u^{{n-1}}$ ៖")
        pw = f"\\left({tx(u)}\\right)" + (f"^{{{n-1}}}" if n > 2 else ""); q = sp.expand(n * du)
        w.chain(("f'(x)", sp.diff(f, x)), (f"{n}\\left({tx(u)}\\right)'{pw}", n * du * u ** (n - 1)), (f"{n}\\left({tx(du)}\\right){pw}", n * du * u ** (n - 1)), (f"{br(sp.factor(q))}{pw}", q * u ** (n - 1)))
        ans = f"f'(x)={br(sp.factor(q))}{pw}"
    return row(w.say(f"ដូចនេះ $\\boxed{{{ans}}}$ ។"), CH, "steps", "steps_chain_written", 1, P, ans, "chainrule")
def sign_study(rng):
    a, b, c = rng.sample(range(-6, 7), 3); a, b = sorted([a, b]); N, Dn = (x - a) * (x - b), x - c
    w = W(rng); ex = f"\\frac{{{tx(sp.expand(N))}}}{{{tx(Dn)}}}"; op = rng.choice([">", "<", "\\geq", "\\leq"])
    P = f"ចូរដោះស្រាយវិសមីការខាងក្រោមនេះ ៖ $${ex}{op}0$$"
    w.say(f"វិសមីការកំណត់លុះត្រាតែ ${tx(Dn)}\\neq0$ ឬ $x\\neq{tx(c)}$ ។")
    w.say(f"ដាក់ភាគយកជាផលគុណកត្តា ៖ ${tx(sp.expand(N))}=\\left({tx(x-a)}\\right)\\left({tx(x-b)}\\right)$ ។")
    w.ok(sp.expand(N), (x - a) * (x - b))
    w.say(f"កត្តានីមួយៗស្មើសូន្យត្រង់ $x={tx(a)}$ , $x={tx(b)}$ និង $x={tx(c)}$ ។")
    pts = sorted([a, b, c]); tests = [pts[0] - 1, R(pts[0] + pts[1], 2), R(pts[1] + pts[2], 2), pts[2] + 1]; E = N / Dn; cells = [""]; signs = []
    for i, t in enumerate(tests):
        val = E.subs(x, t); signs.append(val > 0)
        w.say(f"ចំពោះ $x={tx(t)}$ ៖ កន្សោមមានតម្លៃ ${tx(val)}{'>' if val > 0 else '<'}0$ ។")
        cells.append(sgn(val))
        if i < 3: cells.append("\\|" if pts[i] == c else "0")
    cells.append(""); w.say(f"តាង $E(x)={ex}$ ។ តារាងសញ្ញា ៖"); w.say(sign_table(["-\\infty"] + [tx(p) for p in pts] + ["+\\infty"], cells, "E(x)"))
    want = op in (">", "\\geq"); closed = "\\geq" in op or "\\leq" in op; bounds = [None] + pts + [None]; parts = []
    for i, s_ in enumerate(signs):
        if s_ != want: continue
        lo, hi = bounds[i], bounds[i + 1]
        l = "(-\\infty" if lo is None else (("[" if closed and lo != c else "(") + tx(lo)); h = "+\\infty)" if hi is None else (tx(hi) + ("]" if closed and hi != c else ")"))
        parts.append(f"{l};{h}")
    ans = "x\\in " + "\\cup ".join(parts)
    return row(w.say(f"ដូចនេះ $\\boxed{{{ans}}}$ ។"), CH, "steps", "steps_inequality_sign_table", 2, P, ans, "sign_study")
def cubic_study(rng):
    a, b = sorted(rng.sample(range(-4, 5), 2)); k = rng.choice([1, 2, -1, -2]); r = rng.randint(-5, 5)
    if (a + b) % 2 and k % 2: return None
    fp = 3 * k * (x - a) * (x - b); f = sp.expand(sp.integrate(sp.expand(fp), x) + r)
    w = W(rng); P = f"សិក្សាអថេរភាព ហើយសង់តារាងអថេរភាពនៃអនុគមន៍ $f(x)={tx(f)}$ ។ រកតម្លៃបរមានៃ $f$ ។"
    w.say("អនុគមន៍ពហុធា ដូច្នេះ $D=IR$ ។"); w.say("ដេរីវេទី១ ៖")
    w.chain(("f'(x)", sp.diff(f, x)), (tx(sp.expand(fp)), sp.expand(fp)))
    w.say(f"បើ $f'(x)=0$ នោះ ${tx(sp.expand(fp))}=0$ ។")
    h = sp.expand(fp / (3 * k)); w.say(f"ចែកអង្គទាំងពីរនឹង ${tx(3*k)}$ គេបាន ${tx(h)}=0$ ។"); x1, x2 = quad_roots(w, h)
    w.say("សញ្ញាដេរីវេទី១ ៖"); t = [a - 1, R(a + b, 2), b + 1]
    for q in t:
        vv = fp.subs(x, q); w.ok(sp.expand(fp).subs(x, q), vv); w.say(f"ចំពោះ $x={tx(q)}$ ៖ $f'\\left({tx(q)}\\right)={tx(vv)}{'>' if vv > 0 else '<'}0$ ។")
    w.say(f"គណនាតម្លៃត្រង់ចំណុចបរមា ៖"); f1, f2 = show_val(w, f, a), None; f2 = show_val(w, f, b)
    lo, hi = ("-\\infty", "+\\infty") if k > 0 else ("+\\infty", "-\\infty")
    lc = sp.Poly(f, x).LC(); w.say(f"លីមីត ៖ $\\lim_{{x\\to-\\infty}}f(x)=\\lim_{{x\\to-\\infty}}{tx(lc*x**3)}={lo}$ និង $\\lim_{{x\\to+\\infty}}f(x)=\\lim_{{x\\to+\\infty}}{tx(lc*x**3)}={hi}$ ។")
    up, dn = "\\nearrow", "\\searrow"; s1, s2 = ("+", "-") if k > 0 else ("-", "+")
    w.say("តារាងអថេរភាព ៖"); w.say(var_table(["-\\infty", tx(a), tx(b), "+\\infty"], ["", s1, "0", s2, "0", s1, ""], [lo, up if k > 0 else dn, tx(f1), dn if k > 0 else up, tx(f2), up if k > 0 else dn, hi]))
    (mx, xm), (mn, xn) = ((f1, a), (f2, b)) if k > 0 else ((f2, b), (f1, a))
    ans = f"\\text{{max}}={tx(mx)}\\ (x={tx(xm)}),\\ \\text{{min}}={tx(mn)}\\ (x={tx(xn)})"
    w.say(f"ដូចនេះ អនុគមន៍មានអតិបរមាស្មើនឹង $\\boxed{{{tx(mx)}}}$ ត្រង់ $x={tx(xm)}$ និងអប្បបរមាស្មើនឹង $\\boxed{{{tx(mn)}}}$ ត្រង់ $x={tx(xn)}$ ។")
    return row(w, CH, "steps", "steps_cubic_variation", 3, P, ans, "cubic_study")
def slant(rng):
    m, d, Rm = rng.randint(-4, 4), rng.randint(-5, 5), rng.choice([-6, -4, -3, -2, -1, 1, 2, 3, 4, 6])
    if d == 0: return None
    N = sp.expand((x + d) * (x + m) + Rm); f = N / (x + d); w = W(rng); ft = f"\\frac{{{tx(N)}}}{{{tx(x+d)}}}"
    P = f"គេឱ្យ $f(x)={ft}$ ។ រកលីមីតនៃ $f$ ត្រង់ចុងនៃដែនកំណត់ រួចទាញរកអាស៊ីមតូតនៃក្រាប $(C)$ ។"
    w.say(f"អនុគមន៍កំណត់លុះត្រាតែ ${tx(x+d)}\\neq0$ ឬ $x\\neq{tx(-d)}$ ។ ដូចនេះ $D=IR-\\{{{tx(-d)}\\}}$ ។")
    w.say("សរសេរ $f(x)$ ជារាងកាណូនិក ៖ ចែកភាគយកនឹងភាគបែង គេបាន")
    w.chain((tx(N), N), (f"\\left({tx(x+d)}\\right)\\left({tx(x+m)}\\right){st(Rm)}", (x + d) * (x + m) + Rm))
    can = f"{tx(x+m)}{fr(Rm,tx(x+d))}"
    w.chain(("f(x)", f), (can, x + m + Rm / (x + d)))
    w.say("លីមីតត្រង់ $\\pm\\infty$ ៖ ដោយ $\\lim_{x\\to\\pm\\infty}\\frac{%d}{%s}=0$ នោះ" % (Rm, tx(x + d)))
    w.say("$$\\lim_{x\\to-\\infty}f(x)=-\\infty\\ ,\\quad\\lim_{x\\to+\\infty}f(x)=+\\infty$$")
    w.say(f"លីមីតត្រង់ ${tx(-d)}$ ៖ ភាគយកខិតជិត ${tx(N.subs(x,-d))}$ ព្រោះ")
    A, B, val = psub(N, sp.Integer(-d)); w.chain((f"{A}", val), (B, val), (tx(val), val))
    L, Rr = ("+\\infty", "-\\infty") if Rm < 0 else ("-\\infty", "+\\infty")
    w.say(f"កាលណា $x\\to{tx(-d)}^-$ នោះ ${tx(x+d)}\\to0^-$ ហើយកាលណា $x\\to{tx(-d)}^+$ នោះ ${tx(x+d)}\\to0^+$ ។")
    w.say(f"ដោយភាគយក ${'<' if Rm<0 else '>'}0$ គេបាន $$\\lim_{{x\\to{tx(-d)}^-}}f(x)={L}\\ ,\\quad\\lim_{{x\\to{tx(-d)}^+}}f(x)={Rr}$$")
    w.ok(sp.limit(f, x, -d, "-"), sp.oo if Rm < 0 else -sp.oo, "left") if False else None
    assert sp.limit(f, x, -d, "-") == (sp.oo if Rm < 0 else -sp.oo)
    w.C.append(check(f"limit({f},x,{-d},'-')", "oo" if Rm < 0 else "-oo", "left")); w.C.append(check(f"limit({f},x,{-d},'+')", "-oo" if Rm < 0 else "oo", "right"))
    w.say(f"ដូចនេះ បន្ទាត់ $x={tx(-d)}$ ជាអាស៊ីមតូតឈរ ។")
    w.chain((f"\\lim_{{x\\to\\pm\\infty}}\\left[f(x)-\\left({tx(x+m)}\\right)\\right]", sp.Integer(0)), (f"\\lim_{{x\\to\\pm\\infty}}\\frac{{{Rm}}}{{{tx(x+d)}}}", sp.Integer(0)), ("0", sp.Integer(0)))
    ans = f"x={tx(-d)},\\ y={tx(x+m)}"
    return row(w.say(f"ដូចនេះ ក្រាបមានអាស៊ីមតូតឈរ $\\boxed{{x={tx(-d)}}}$ និងអាស៊ីមតូតទ្រេត $\\boxed{{y={tx(x+m)}}}$ ។"), CH, "steps", "steps_slant_with_limits", 3, P, ans, "slant")
def tangent(rng):
    c = [rng.choice([1, 2, -1]), rng.randint(-4, 4), rng.randint(-5, 5), rng.randint(-6, 6)]; f = c[0] * x ** 3 + c[1] * x ** 2 + c[2] * x + c[3]; x0 = sp.Integer(rng.randint(-3, 3))
    w = W(rng); df = sp.diff(f, x); P = f"រកសមីការបន្ទាត់ប៉ះនឹងក្រាប $(C)$ នៃអនុគមន៍ $f(x)={tx(f)}$ ត្រង់ចំណុចមានអាប់ស៊ីស $x_0={tx(x0)}$ ។"
    w.say("សមីការបន្ទាត់ប៉ះមានរាង $y-y_0=f'(x_0)(x-x_0)$ ។"); w.say(f"យើងបាន $f'(x)={tx(df)}$ ។")
    y0 = show_val(w, f, x0); a, b, m = psub(df, x0); w.chain((f"f'({tx(x0)})", m), (a, m), (b, m), (tx(m), m))
    line = sp.expand(m * (x - x0) + y0); xm = f"\\left(x{'+' if x0<0 else '-'}{abs(x0)}\\right)" if x0 != 0 else "x"
    w.say("ជំនួសក្នុងរូបមន្ត ៖")
    w.chain(("y", line), (f"{'' if m==1 else ('-' if m==-1 else tx(m))}{xm}{st(y0)}", m * (x - x0) + y0), (tx(line), line))
    return row(w.say(f"ដូចនេះ សមីការបន្ទាត់ប៉ះគឺ $\\boxed{{y={tx(line)}}}$ ។"), CH, "steps", "steps_tangent_substituted", 2, P, f"y={tx(line)}", "tangent")
def exp_study(rng):
    a, b = rng.randint(1, 6), rng.randint(-9, 9); u = a * x + b; f = u * sp.exp(x); x0 = R(-(a + b), a); w = W(rng)
    P = f"គេឱ្យ $f(x)=\\left({tx(u)}\\right)e^{{x}}$ ។ គណនាលីមីតនៃ $f$ ត្រង់ $\\pm\\infty$ រកអថេរភាព ហើយសង់តារាងអថេរភាព ។"
    w.say("$D=IR$ ។"); w.say(f"លីមីតត្រង់ $+\\infty$ ៖ ${tx(u)}\\to+\\infty$ និង $e^{{x}}\\to+\\infty$ ដូច្នេះ $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។")
    w.say("លីមីតត្រង់ $-\\infty$ ៖ ពន្លាត $f(x)$ ៖"); w.say(f"$$\\lim_{{x\\to-\\infty}}f(x)=\\lim_{{x\\to-\\infty}}\\left({'' if a==1 else a}xe^{{x}}{'' if b==0 else ('+' if b>0 else '-')+('' if abs(b)==1 else str(abs(b)))+'e^{x}'}\\right)$$")
    w.say("ដោយ $\\lim_{x\\to-\\infty}xe^{x}=0$ និង $\\lim_{x\\to-\\infty}e^{x}=0$ គេបាន $\\lim_{x\\to-\\infty}f(x)=0$ ។"); w.C.append(check(f"limit({f},x,-oo)", "0", "limit"))
    w.say("ដូចនេះ បន្ទាត់ $y=0$ ជាអាស៊ីមតូតដេកត្រង់ $-\\infty$ ។"); w.say(f"តាង $u={tx(u)}$ និង $v=e^{{x}}$ នោះ $u'={a}$ និង $v'=e^{{x}}$ ។")
    v2 = sp.expand(a * x + a + b)
    w.chain(("f'(x)", sp.diff(f, x)), (f"{'' if a==1 else a}e^{{x}}+{br(u)}e^{{x}}", a * sp.exp(x) + u * sp.exp(x)), (f"{br(v2)}e^{{x}}", v2 * sp.exp(x)))
    w.say(f"ដោយ $e^{{x}}>0$ ជានិច្ច នោះ $f'(x)$ មានសញ្ញាតាម ${tx(v2)}$ ។"); w.say(f"បើ $f'(x)=0$ នោះ ${tx(v2)}=0$ ឬ $x={tx(x0)}$ ។" if v2 != x else f"បើ $f'(x)=0$ នោះ $x=0$ ។")
    val = sp.simplify(f.subs(x, x0)); w.chain((f"f\\left({tx(x0)}\\right)", val), (f"\\left({tx(a)}{pp(x0)}{sg(b)}\\right)e^{{{tx(x0)}}}", val), (tx(val), val))
    w.say("តារាងអថេរភាព ៖"); w.say(var_table(["-\\infty", tx(x0), "+\\infty"], ["", "-", "0", "+", ""], ["0", "\\searrow", tx(val), "\\nearrow", "+\\infty"]))
    return row(w.say(f"ដូចនេះ អនុគមន៍មានអប្បបរមា $\\boxed{{{tx(val)}}}$ ត្រង់ $x={tx(x0)}$ ។"), CH, "steps", "steps_exp_linear_study", 3, P, f"\\min={tx(val)}", "exp_study")
def ln_study(rng):
    a, c, b = rng.choice([1, 2, 3]), rng.choice([1, 2, 3, 4, 6]), rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]); f = a * x + b - c * sp.log(x); x0 = R(c, a); w = W(rng); ft = tx(f)
    P = f"គេឱ្យ $f(x)={ft}$ ។ រកដែនកំណត់ លីមីតត្រង់ចុងដែនកំណត់ អថេរភាព និងតម្លៃអប្បបរមានៃ $f$ ។"
    w.say("អនុគមន៍កំណត់លុះត្រាតែ $x>0$ ។ ដូចនេះ $D=(0;+\\infty)$ ។")
    w.say(f"លីមីតត្រង់ $0^+$ ៖ កាលណា $x\\to0^+$ នោះ $\\ln x\\to-\\infty$ ដូច្នេះ $-{c if c!=1 else ''}\\ln x\\to+\\infty$ ។ គេបាន $\\lim_{{x\\to0^+}}f(x)=+\\infty$ ។")
    w.say("លីមីតត្រង់ $+\\infty$ ៖ ដាក់ $x$ ជាកត្តារួម ៖"); fac = f"x\\left({a}{fr(b,'x')}-{c}\\cdot\\frac{{\\ln x}}{{x}}\\right)"
    w.chain(("f(x)", f), (fac, x * (a + b / x - c * sp.log(x) / x)))
    w.say(f"ដោយ $\\lim_{{x\\to+\\infty}}\\frac{{\\ln x}}{{x}}=0$ នោះកន្សោមក្នុងវង់ក្រចកខិតជិត ${a}>0$ ។ គេបាន $\\lim_{{x\\to+\\infty}}f(x)=+\\infty$ ។"); w.C.append(check(f"limit({f},x,oo)", "oo", "limit"))
    num = a * x - c; w.chain(("f'(x)", sp.diff(f, x)), (f"{a}-\\frac{{{c}}}{{x}}", a - c / x), (f"\\frac{{{tx(num)}}}{{x}}", num / x))
    w.say(f"ដោយ $x>0$ នោះ $f'(x)$ មានសញ្ញាតាម ${tx(num)}$ ។ បើ $f'(x)=0$ នោះ $x={tx(x0)}$ ។")
    val = f.subs(x, x0); w.chain((f"f\\left({tx(x0)}\\right)", val), (f"{tx(a)}{pp(x0)}{sg(b)}-{c}\\ln {tx(x0) if x0.is_integer else par(x0)}", val), (tx(val), val))
    w.say("តារាងអថេរភាព ៖"); w.say(var_table(["0", tx(x0), "+\\infty"], ["\\|", "-", "0", "+", ""], ["\\|+\\infty", "\\searrow", tx(val), "\\nearrow", "+\\infty"]))
    return row(w.say(f"ដូចនេះ តម្លៃអប្បបរមានៃ $f$ គឺ $\\boxed{{{tx(val)}}}$ ត្រង់ $x={tx(x0)}$ ។"), CH, "steps", "steps_ln_linear_study", 3, P, f"\\min={tx(val)}", "ln_study")
ALL = [(quotient, 220), (product, 200), (chainrule, 180), (sign_study, 220), (cubic_study, 240), (slant, 240), (tangent, 200), (exp_study, 90), (ln_study, 180)]
