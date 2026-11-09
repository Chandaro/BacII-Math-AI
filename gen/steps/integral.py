"""Integral chapter: primitives, definite integrals, area, volume, arc length."""
from kx import *
CH = "integral"
def sg(c): return ("+" if c > 0 else "-") + cf(abs(c))
P_ = lambda w, sub, d, prob, ans, g, topic: row(w, CH, topic, sub, d, prob, ans, g)
ASK_I = ("គណនាអាំងតេក្រាលខាងក្រោមនេះ ៖", "ចូរគណនាអាំងតេក្រាលខាងក្រោម ៖", "គណនាតម្លៃនៃអាំងតេក្រាល ៖", "ចូរគណនាអាំងតេក្រាលមួយនេះ ៖")
ASK_N = ("គណនាអាំងតេក្រាលមិនកំណត់ខាងក្រោម ៖", "ចូរគណនាអាំងតេក្រាលមិនកំណត់ ៖", "រកអាំងតេក្រាលមិនកំណត់ខាងក្រោម ៖")
ASK_P = ("រកព្រីមីទីវនៃអនុគមន៍", "ចូររកព្រីមីទីវនៃអនុគមន៍", "គណនាអាំងតេក្រាលមិនកំណត់នៃអនុគមន៍")
# Basic table: name -> (function, primitive, rule latex)
def basics(rng):
    n = rng.randint(2, 5); k = rng.choice([2, 3, 4, -2, -3]); 
    return [(x ** n, x ** (n + 1) / (n + 1), f"\\int x^{{n}}\\,dx=\\frac{{x^{{n+1}}}}{{n+1}}+c"),
            (x, x ** 2 / 2, None), (sp.Integer(1), x, None),
            (1 / x, sp.log(x), "\\int\\frac{1}{x}\\,dx=\\ln|x|+c"), (1 / x ** 2, -1 / x, "\\int\\frac{1}{x^{2}}\\,dx=-\\frac{1}{x}+c"),
            (sp.sqrt(x), R(2, 3) * x ** R(3, 2), None), (1 / sp.sqrt(x), 2 * sp.sqrt(x), "\\int\\frac{1}{\\sqrt{x}}\\,dx=2\\sqrt{x}+c"),
            (sp.exp(x), sp.exp(x), "\\int e^{x}\\,dx=e^{x}+c"), (sp.exp(k * x), sp.exp(k * x) / k, "\\int e^{kx}\\,dx=\\frac{e^{kx}}{k}+c"),
            (sp.sin(x), -sp.cos(x), "\\int\\sin x\\,dx=-\\cos x+c"), (sp.cos(x), sp.sin(x), "\\int\\cos x\\,dx=\\sin x+c"),
            (sp.sin(abs(k) * x), -sp.cos(abs(k) * x) / abs(k), "\\int\\sin kx\\,dx=-\\frac{\\cos kx}{k}+c"), (sp.cos(abs(k) * x), sp.sin(abs(k) * x) / abs(k), "\\int\\cos kx\\,dx=\\frac{\\sin kx}{k}+c")]
def combo(rng):
    t = rng.sample(basics(rng), rng.choice([2, 2, 3, 3, 4])); cs = [nz(rng, -7, 9) for _ in t]
    return sum(c * a for c, (a, _, _) in zip(cs, t)), sum(c * b for c, (_, b, _) in zip(cs, t)), cs, t
def lin_prim(rng):
    f, F, cs, t = combo(rng); w = W(rng); ok = len(f.args) == len(t) if f.is_Add else False
    if not ok: return None
    P = f"{w.v(*ASK_P)} $f(x)={T(f)}$ ។" if rng.random() < .5 else f"{w.v(*ASK_N)} $$I={Int(f)}$$"
    rules = [r for *_, r in t if r]
    w.say("អនុវត្តរូបមន្តអាំងតេក្រាលលើតួនីមួយៗ ។")
    if rules: w.say(w.v("រូបមន្តដែលប្រើ ៖", "យើងប្រើរូបមន្ត ៖", "តាមរូបមន្តអាំងតេក្រាល ៖") + " $" + "$ , $".join(rules[:3]) + "$ ។")
    w.say("$$" + Int(f) + "=" + "+".join((f"{T(c)}" if abs(c) != 1 else ("-" if c < 0 else "")) + Int(a) for c, (a, _, _) in zip(cs, t)).replace("+-", "-") + "$$")
    w.say(f"$$={TL(F)}+c$$"); w.ok(sp.diff(F, x), f); w.say(w.v("ផ្ទៀងផ្ទាត់ ៖ ដេរីវេនៃលទ្ធផលស្មើអនុគមន៍ក្រោមសញ្ញាអាំងតេក្រាល ។", "ដោយ $c$ ជាចំនួនថេរ ។", "($c$ ថេរ)"))
    w.C.append(check(f"diff({F},x)", f, "primitive"))
    return row(w.say(f"{so(w)} $\\boxed{{{Int(f)}={TL(F)}+c}}$ ។"), CH, "integral_primitive", "steps_linear_combo", "easy", P, f"{TL(F)}+c", "lin_prim")
def nicebounds(rng, f):
    """Pick bounds for which the function is defined."""
    h = f.has(sp.sin, sp.cos); l = f.has(sp.log) or any(a.is_Pow and a.exp.is_negative or a.is_Pow and not a.exp.is_integer for a in sp.preorder_traversal(f))
    if h: return rng.choice([(0, sp.pi), (0, sp.pi / 2), (0, sp.pi / 4), (sp.pi / 6, sp.pi / 2), (sp.pi / 3, sp.pi / 2), (-sp.pi / 2, sp.pi / 2)])
    if l: return rng.choice([(1, 2), (1, 4), (1, 9), (4, 9), (1, sp.E), (2, 3)])
    a = rng.randint(-3, 2); return a, a + rng.randint(1, 4)
def lin_def(rng):
    f, F, cs, t = combo(rng); a, b = nicebounds(rng, f)
    if not (f.is_Add and len(f.args) == len(t)): return None
    if (f.has(sp.log) or any(q.is_Pow and q.exp < 0 for q in sp.preorder_traversal(f) if q.is_Pow and q.exp.is_number)) and a <= 0: return None
    if any(q.is_Pow and not q.exp.is_integer for q in sp.preorder_traversal(f) if q.is_Pow and q.exp.is_number) and a < 0: return None
    v = V(F.subs(x, b) - F.subs(x, a)); v = sp.nsimplify(sp.expand(v)) if v.is_number else v
    if len(T(v)) > 70: return None
    w = W(rng); P = f"{w.v(*ASK_I)} $$I={Int(f, a, b)}$$"
    w.say(w.v("រកព្រីមីទីវនៃតួនីមួយៗ ៖", "យើងមាន ៖", "តាមរូបមន្តញូតុន-លែបនីស ៖ $\\int_a^b f(x)\\,dx=F(b)-F(a)$ ។"))
    w.say(f"$$I={EV(rng, T(F), a, b)}$$"); w.say(f"$$=\\left({T(F.subs(x, b))}\\right)-\\left({T(F.subs(x, a))}\\right)$$"); w.ok(F.subs(x, b) - F.subs(x, a), v); w.say(f"$$={T(v)}$$")
    w.C.append(check(f"integrate({f},(x,{a},{b}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{I={T(v)}}}$ ។"), CH, "integral_definite", "steps_linear_combo_definite", "medium", P, T(v), "lin_def")
# Function of ax+b
def outer_lin(rng):
    a = rng.choice([2, 3, 4, 5, 6, 7]); b = nz(rng, -9, 9); u = a * x + b; n = rng.randint(2, 8); U = sp.Symbol("u", positive=True)
    return rng.choice([(u ** n, U ** n, U ** (n + 1) / (n + 1)), (1 / u, 1 / U, sp.log(U)), (1 / u ** 2, 1 / U ** 2, -1 / U), (sp.sqrt(u), sp.sqrt(U), R(2, 3) * U ** R(3, 2)), (sp.exp(u), sp.exp(U), sp.exp(U)), (sp.sin(u), sp.sin(U), -sp.cos(U)), (sp.cos(u), sp.cos(U), sp.sin(U))]) + (u, a, U)
def comp_lin(rng):
    f, gu, Gu, u, a, U = outer_lin(rng); k = rng.choice([1, 1, 2, 3, 5]); f = k * f; F = sp.nsimplify(k) / a * Gu.subs(U, u); w = W(rng)
    P = f"{w.v(*ASK_N)} $$I={Int(f)}$$"; w.say(f"តាង $u={T(u)}$ {w.v('នាំឱ្យ', 'ដូច្នេះ')} $du={a}\\,dx$ ឬ $dx=\\frac{{du}}{{{a}}}$ ។".replace("\\frac{du}{-", "-\\frac{du}{"))
    w.say(f"$$I={Int(T(R(k, a) * gu), var='u')}$$"); w.say(f"$$={TL(R(k, a) * Gu)}+c$$"); w.say("ជំនួស $u$ វិញ ៖"); w.say(f"$$I={TL(F)}+c$$")
    if not same(sp.diff(F, x) - f, 0) and sp.simplify(sp.diff(F, x) - f) != 0: return None
    w.C.append(check(f"diff({F},x)", f, "primitive"))
    return row(w.say(f"{so(w)} $\\boxed{{I={TL(F)}+c}}$ ។"), CH, "integral_primitive", "steps_sub_linear", "easy", P, f"{TL(F)}+c", "comp_lin")
# u-substitution
def sub_pair(rng):
    c = rng.randint(1, 6); m = rng.choice([2, 3]); n = rng.randint(2, 5)
    U = sp.Symbol("u", positive=True)
    us = [(x ** 2 + c, 0, rng.choice([1, 2, 3])), (x ** 3 + c, 0, rng.choice([1, 2])), (sp.log(x), 1, sp.E), (sp.exp(x) + c, 0, 1), (sp.sin(x), 0, sp.pi / 2), (sp.cos(x) + 2, 0, sp.pi / 2), (sp.sin(x) + c, 0, sp.pi / 2), (x ** 2 + 2 * x + c + 1, 0, rng.choice([1, 2]))]
    u, a, b = rng.choice(us); gs = [(U ** n, U ** (n + 1) / (n + 1)), (1 / U, sp.log(U)), (1 / U ** 2, -1 / U), (sp.sqrt(U), R(2, 3) * U ** R(3, 2)), (1 / sp.sqrt(U), 2 * sp.sqrt(U)), (sp.exp(U), sp.exp(U))]
    g, G = rng.choice(gs)
    return u, a, b, g, G, U
def sub_(rng, definite):
    u, a, b, g, G, U = sub_pair(rng); du = sp.diff(u, x); k = rng.choice([1, 1, 1, 2, R(1, 2), 3]); f = k * du * g.subs(U, u)
    if u == sp.log(x) and g == 1 / sp.sqrt(U) or u == sp.log(x) and g == 1 / U or u == sp.log(x) and g == 1 / U ** 2 or (u == sp.sin(x) and g.has(U) and (g.is_Pow and g.exp < 0)): 
        if definite: return None
    w = W(rng); ft = T(f); P = f"{w.v(*ASK_I)} $$I={Int(f, a, b)}$$" if definite else f"{w.v(*ASK_N)} $$I={Int(f)}$$"
    w.say(f"តាង $u={T(u)}$ {w.v('នាំឱ្យ', 'គេបាន', 'ដូច្នេះ')} $du={B(du)}\\,dx$ ។")
    if not definite:
        F = k * G.subs(U, u); w.say(f"$$I={Int(T(k * g) if k != 1 else T(g), var='u')}$$"); w.say(f"$$={TL(k * G)}+c$$"); w.say(f"ជំនួស $u={T(u)}$ វិញ ៖"); w.say(f"$$I={TL(F)}+c$$")
        if sp.simplify(sp.diff(F, x) - f) != 0: return None
        w.C.append(check(f"diff({F},x)", f, "primitive"))
        return row(w.say(f"{so(w)} $\\boxed{{I={TL(F)}+c}}$ ។"), CH, "integral_primitive", "steps_sub_u", "medium", P, f"{TL(F)}+c", "sub_indef")
    ua, ub = u.subs(x, a), u.subs(x, b)
    if ua == ub or ua <= 0 or ub <= 0: return None
    w.say(f"ប្តូរព្រំដែន ៖ $$\\begin{{cases}}x={T(a)}\\Rightarrow u={T(ua)}\\\\x={T(b)}\\Rightarrow u={T(ub)}\\end{{cases}}$$")
    Gk = k * G; v = V(Gk.subs(U, ub) - Gk.subs(U, ua))
    if len(T(v)) > 60: return None
    w.say(f"$$I={Int(T(k * g), ua, ub, var='u')}={EV(rng, T(Gk), ua, ub)}$$"); w.say(f"$$=\\left({T(Gk.subs(U, ub))}\\right)-\\left({T(Gk.subs(U, ua))}\\right)={T(v)}$$"); w.C.append(check(f"integrate({f},(x,{a},{b}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{I={T(v)}}}$ ។"), CH, "integral_definite", "steps_sub_u_bounds", "bacii", P, T(v), "sub_def")
def sub_indef(rng): return sub_(rng, False)
def sub_def(rng): return sub_(rng, True)
# Integration by parts
def parts_core(w, p, g, kind, k, lab="I"):
    """Print one or two rounds. Return primitive of p*g. kind: exp, sin, cos, ln."""
    if kind == "ln":
        Pp = sp.integrate(p, x); w.say(f"តាង $u=\\ln x$ និង $dv={B(p)}\\,dx$ {w.v('គេបាន', 'នាំឱ្យ')} $du=\\frac{{dx}}{{x}}$ និង $v={T(Pp)}$ ។"); rest = sp.expand(Pp / x); w.say(f"$${lab}={B(Pp)}\\ln x-{Int(rest)}$$"); return Pp * sp.log(x) - sp.integrate(rest, x)
    prim = lambda kd: {"exp": sp.exp(k * x) / k, "sin": -sp.cos(k * x) / k, "cos": sp.sin(k * x) / k}[kd]
    G = prim(kind); dp = sp.diff(p, x)
    w.say(f"តាង $u={T(p)}$ និង $dv={T(g)}\\,dx$ {w.v('គេបាន', 'នាំឱ្យ')} $du={B(dp)}\\,dx$ និង $v={T(G)}$ ។"); w.say("តាមរូបមន្ត $\\int u\\,dv=uv-\\int v\\,du$ ៖")
    kind2 = {"exp": "exp", "sin": "cos", "cos": "sin"}[kind]; g2 = {"exp": sp.exp(k * x), "cos": sp.cos(k * x), "sin": sp.sin(k * x)}[kind2]
    c0 = sp.simplify(G / g2); sign = "-" if c0 > 0 else "+"; ca = cf(abs(c0))
    head = f"{B(p)}\\left({T(G)}\\right)"
    pd = ("" if dp == 1 else B(dp)) + T(g2); w.say(f"$${lab}={head}{sign}{ca}{Int(pd)}$$")
    if sp.degree(dp, x) >= 1:
        G2 = prim(kind2); d2 = sp.diff(dp, x); w.say("អាំងតេក្រាលដែលនៅសល់ត្រូវធ្វើដោយផ្នែកម្តងទៀត ។")
        w.say(f"តាង $u_1={T(dp)}$ និង $dv_1={T(g2)}\\,dx$ {w.v('គេបាន', 'នាំឱ្យ')} $du_1={T(d2)}\\,dx$ និង $v_1={T(G2)}$ ។")
        J = sp.integrate(dp * g2, x); w.say(f"$${Int(pd)}={B(dp)}\\left({T(G2)}\\right)-{Int(T(d2 * G2))}={T(sp.expand(J))}+c_1$$")
    else:
        J = sp.integrate(dp * g2, x); w.say(f"$$={head}{sign}{ca}\\left({T(J)}\\right)+c$$")
    return sp.expand(p * G - c0 * J)
def parts_pick(rng):
    k = rng.choice([1, 1, 2, 3, -1, -2]); deg = rng.choice([1, 1, 1, 2]); p = (rng.choice([1, 2, 3]) * x + rng.randint(-4, 4)) if deg == 1 else x ** 2 + rng.randint(-2, 2) * x + rng.randint(-2, 2); kind = rng.choice(["exp", "exp", "sin", "cos", "ln"])
    if kind == "ln": k = 1; p = rng.choice([sp.Integer(1), x, x ** 2, 2 * x + 1, 3 * x ** 2, x + rng.randint(1, 3)]); g = sp.log(x)
    else:
        if kind != "exp": k = abs(k)
        g = {"exp": sp.exp(k * x), "sin": sp.sin(k * x), "cos": sp.cos(k * x)}[kind]
    return p, g, kind, k
def parts_indef(rng):
    p, g, kind, k = parts_pick(rng); f = p * g; w = W(rng); P = f"{w.v(*ASK_N)} $$I={Int(B(p) + T(g) if not p == 1 else T(g))}$$"; w.say(w.v("ប្រើអាំងតេក្រាលដោយផ្នែក ។", "គណនាដោយផ្នែក ។"))
    F = parts_core(w, p, g, kind, k)
    if sp.simplify(sp.diff(F, x) - f) != 0: return None
    w.C.append(check(f"diff({F},x)", f, "primitive")); w.say(f"$$I={T(F)}+c$$")
    return row(w.say(f"{so(w)} $\\boxed{{I={T(F)}+c}}$ ។"), CH, "integral_parts", f"steps_parts_{kind}", "medium", P, f"{T(F)}+c", "parts_indef")
def parts_def(rng):
    p, g, kind, k = parts_pick(rng); f = p * g; a, b = {"ln": rng.choice([(1, sp.E), (1, 2), (1, sp.E ** 2)]), "exp": rng.choice([(0, 1), (0, 2), (-1, 0), (1, 2)]), "sin": rng.choice([(0, sp.pi), (0, sp.pi / 2)]), "cos": rng.choice([(0, sp.pi), (0, sp.pi / 2)])}[kind]
    w = W(rng); P = f"{w.v(*ASK_I)} $$I={Int(B(p) + T(g) if p != 1 else T(g), a, b)}$$"; w.say(f"រកព្រីមីទីវជាមុនសិន ដោយប្រើអាំងតេក្រាលដោយផ្នែក ។ តាង $J={Int(B(p) + T(g) if p != 1 else T(g))}$ ។"); F = parts_core(w, p, g, kind, k, "J")
    if sp.simplify(sp.diff(F, x) - f) != 0: return None
    v = V(F.subs(x, b) - F.subs(x, a))
    if len(T(v)) > 50: return None
    w.say(f"$$J={T(F)}+c$$"); w.say("ដូច្នេះ ៖"); w.say(f"$$I={EV(rng, T(F), a, b)}$$"); w.say(f"$$=\\left({T(F.subs(x, b))}\\right)-\\left({T(F.subs(x, a))}\\right)={T(v)}$$"); w.C.append(check(f"integrate({f},(x,{a},{b}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{I={T(v)}}}$ ។"), CH, "integral_parts", f"steps_parts_definite_{kind}", "bacii", P, T(v), "parts_def")
# Trig
def trig_pow(rng):
    k = rng.choice([1, 1, 2, 3]); kind = rng.choice(["s2", "c2", "s3", "c3", "t2", "sc"]); a, b = rng.choice([(0, sp.pi), (0, sp.pi / 2), (0, sp.pi / 4), (sp.pi / 6, sp.pi / 2)]); w = W(rng); m = rng.choice([1, 2, 3, 4])
    if kind in ("s2", "c2"):
        f = (sp.sin(k * x) if kind == "s2" else sp.cos(k * x)) ** 2; s = "-" if kind == "s2" else "+"; F = x / 2 + (-1 if kind == "s2" else 1) * sp.sin(2 * k * x) / (4 * k); idt = f"\\{'sin' if kind == 's2' else 'cos'}^2\\theta=\\frac{{1{s}\\cos 2\\theta}}{{2}}"; lin = R(1, 2) + (-1 if kind == "s2" else 1) * sp.cos(2 * k * x) / 2; say = f"ប្រើរូបមន្តបន្ថយស្វ័យគុណ ៖ ${idt}$ ។"
    elif kind in ("s3", "c3"):
        if k != 1: return None
        f = (sp.sin(x) if kind == "s3" else sp.cos(x)) ** 3; F = (-sp.cos(x) + sp.cos(x) ** 3 / 3) if kind == "s3" else (sp.sin(x) - sp.sin(x) ** 3 / 3); lin = (1 - sp.cos(x) ** 2) * sp.sin(x) if kind == "s3" else (1 - sp.sin(x) ** 2) * sp.cos(x); say = "សរសេរ " + ("$\\sin^3x=\\left(1-\\cos^2x\\right)\\sin x$" if kind == "s3" else "$\\cos^3x=\\left(1-\\sin^2x\\right)\\cos x$") + " រួចតាង " + ("$u=\\cos x$" if kind == "s3" else "$u=\\sin x$") + " ។"
    elif kind == "t2":
        if b >= sp.pi / 2: return None
        f = sp.tan(x) ** 2; F = sp.tan(x) - x; lin = 1 / sp.cos(x) ** 2 - 1; say = "ដោយ $\\tan^2x=\\frac{1}{\\cos^2x}-1$ ។"
    else:
        p, q = rng.sample([1, 2, 3, 4, 5], 2)
        if p < q: p, q = q, p
        f = sp.sin(p * x) * sp.cos(q * x); F = -sp.cos((p + q) * x) / (2 * (p + q)) - sp.cos((p - q) * x) / (2 * (p - q)); lin = (sp.sin((p + q) * x) + sp.sin((p - q) * x)) / 2; say = "ប្រើរូបមន្តបំប្លែងផលគុណជាផលបូក ៖ $\\sin A\\cos B=\\frac{1}{2}\\left[\\sin(A+B)+\\sin(A-B)\\right]$ ។"
    f, F, lin = m * f, m * F, m * lin; v = V(F.subs(x, b) - F.subs(x, a))
    if sp.simplify(sp.diff(F, x) - f) != 0 or len(T(v)) > 50: return None
    P = f"{w.v(*ASK_I)} $$I={Int(f, a, b)}$$"; w.say("បំប្លែងកន្សោមក្រោមសញ្ញាអាំងតេក្រាលជាមុនសិន ។"); w.say(say); w.say(f"$$I={Int(lin, a, b)}$$"); w.say(f"$$={EV(rng, T(F), a, b)}$$"); w.say(f"$$={T(v)}$$"); w.C.append(check(f"integrate({f},(x,{a},{b}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{I={T(v)}}}$ ។"), CH, "integral_trig", f"steps_trig_{kind}", "medium", P, T(v), "trig_pow")
def ij_pair(rng):
    k = rng.choice([1, 2, 3]); a, b = rng.choice([(0, sp.pi / 2), (0, sp.pi / 4), (0, sp.pi), (0, sp.pi / 6)]); kind = rng.choice([1, 2]); w = W(rng)
    if kind == 1:
        c, s = sp.cos(k * x) ** 2, sp.sin(k * x) ** 2; S, D = sp.Integer(1), sp.cos(2 * k * x); FS, FD = x, sp.sin(2 * k * x) / (2 * k); sa, da = f"\\cos^2\\theta+\\sin^2\\theta=1", f"\\cos^2\\theta-\\sin^2\\theta=\\cos 2\\theta"
    else:
        c, s = sp.exp(k * x) * sp.cos(x) ** 2, sp.exp(k * x) * sp.sin(x) ** 2; return None
    Iv = sp.simplify(FS.subs(x, b) - FS.subs(x, a)); Dv = sp.simplify(FD.subs(x, b) - FD.subs(x, a)); A, Bv = (Iv + Dv) / 2, (Iv - Dv) / 2
    P = f"គេឱ្យ $I={Int(c, a, b)}$ និង $J={Int(s, a, b)}$ ។\nក. គណនា $I+J$ និង $I-J$ ។\nខ. ទាញរកតម្លៃ $I$ និង $J$ ។"
    w.say("ក. ដោយ $" + sa + "$ គេបាន ៖"); w.say(f"$$I+J={Int(S, a, b)}={EV(rng, T(FS), a, b)}={T(Iv)}$$"); w.say(f"ដោយ ${da}$ គេបាន ៖"); w.say(f"$$I-J={Int(D, a, b)}={EV(rng, T(FD), a, b)}={T(Dv)}$$"); w.say(f"ខ. បូកសមីការទាំងពីរ ៖ $2I={T(Iv + Dv)}$ ។ ដកសមីការទាំងពីរ ៖ $2J={T(Iv - Dv)}$ ។"); w.C += [check(f"integrate({c},(x,{a},{b}))", A, "I"), check(f"integrate({s},(x,{a},{b}))", Bv, "J")]
    return row(w.say(f"{so(w)} $\\boxed{{I={T(A)}}}$ និង $\\boxed{{J={T(Bv)}}}$ ។"), CH, "integral_trig", "steps_I_J_pair", "bacii", P, f"I={T(A)};\\ J={T(Bv)}", "ij_pair")
# Rational
def rat_pf(rng):
    a, b = rng.sample(range(-5, 6), 2); A, Bc = nz(rng, -5, 5), nz(rng, -5, 5); N = sp.expand(A * (x - b) + Bc * (x - a)); D = sp.expand((x - a) * (x - b)); f = N / D; lo = max(a, b) + 1; hi = lo + rng.randint(1, 3); w = W(rng); ft = f"\\frac{{{T(N)}}}{{{T(D)}}}"
    if sp.degree(N, x) < 1: return None
    F = A * sp.log(x - a) + Bc * sp.log(x - b); v = sp.expand(F.subs(x, hi) - F.subs(x, lo)); pt = rng.random() < .5
    P = (f"គេឱ្យអនុគមន៍ $f(x)={ft}$ ។\nក. កំណត់ចំនួនពិត $A$ និង $B$ ដែល $f(x)=\\frac{{A}}{{{T(x - a)}}}+\\frac{{B}}{{{T(x - b)}}}$ ។\nខ. គណនា $I=\\int_{{{lo}}}^{{{hi}}}f(x)\\,dx$ ។") if pt else f"{w.v(*ASK_I)} $$I=\\int_{{{lo}}}^{{{hi}}}{ft}\\,dx$$"
    w.say(("ក. " if pt else "") + f"ភាគបែង ${T(D)}={B(x - a)}{B(x - b)}$ ។ សរសេរ ៖"); w.say(f"$${ft}=\\frac{{A}}{{{T(x - a)}}}+\\frac{{B}}{{{T(x - b)}}}=\\frac{{A\\left({T(x - b)}\\right)+B\\left({T(x - a)}\\right)}}{{{T(D)}}}$$")
    w.say(f"ជំនួស $x={a}$ ៖ ${T(N.subs(x, a))}=A\\left({a - b}\\right)$ នាំឱ្យ $A={A}$ ។"); w.say(f"ជំនួស $x={b}$ ៖ ${T(N.subs(x, b))}=B\\left({b - a}\\right)$ នាំឱ្យ $B={Bc}$ ។"); w.ok(f, A / (x - a) + Bc / (x - b))
    w.say(("ខ. " if pt else "") + f"$$I=\\int_{{{lo}}}^{{{hi}}}\\left(\\frac{{{A}}}{{{T(x - a)}}}{fr(Bc, T(x - b))}\\right)dx$$".replace("\\frac{-", "-\\frac{")); w.say(f"$$={EV(rng, f'{cf(A)}\\ln|{T(x - a)}|{sg(Bc)}\\ln|{T(x - b)}|', lo, hi)}$$"); w.say(f"$$={T(v)}$$"); w.C.append(check(f"integrate(({N})/({D}),(x,{lo},{hi}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{I={T(v)}}}$ ។"), CH, "integral_rational", "steps_partial_fractions", "bacii", P, T(v), "rat_pf")
def rat_div(rng):
    a = nz(rng, -5, 5); p, q, r = rng.choice([1, 2, 3]), rng.randint(-5, 5), nz(rng, -6, 6); N = sp.expand((p * x + q) * (x + a) + r); D = x + a; lo = max(1, -a + 1); hi = lo + rng.randint(1, 3); w = W(rng); ft = f"\\frac{{{T(N)}}}{{{T(D)}}}"; F = p * x ** 2 / 2 + q * x + r * sp.log(x + a); v = sp.expand(F.subs(x, hi) - F.subs(x, lo)); pt = rng.random() < .6
    P = (f"គេឱ្យអនុគមន៍ $f(x)={ft}$ ។\nក. កំណត់ចំនួនពិត $a,b,c$ ដែល $f(x)=ax+b+\\frac{{c}}{{{T(D)}}}$ ។\nខ. គណនា $\\int_{{{lo}}}^{{{hi}}}f(x)\\,dx$ ។") if pt else f"{w.v(*ASK_I)} $$I=\\int_{{{lo}}}^{{{hi}}}{ft}\\,dx$$"
    w.say(("ក. " if pt else "") + "ចែកភាគយកនឹងភាគបែង ៖"); w.say(f"$${T(N)}=\\left({T(p * x + q)}\\right)\\left({T(D)}\\right){st(r)}$$"); w.ok(N, (p * x + q) * D + r); w.say(f"នាំឱ្យ $f(x)={T(p * x + q)}{fr(r, T(D))}$ ។".replace("-\\frac{-", "+\\frac{")); w.say(f"ដូចនេះ $a={p}$ , $b={q}$ , $c={r}$ ។") if pt else None;
    w.say(("ខ. " if pt else "") + f"$$\\int_{{{lo}}}^{{{hi}}}f(x)\\,dx={EV(rng, f'{T(p * x ** 2 / 2 + q * x)}{sg(r)}\\ln|{T(D)}|', lo, hi)}$$"); w.say(f"$$={T(v)}$$"); w.C.append(check(f"integrate(({N})/({D}),(x,{lo},{hi}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{{T(v)}}}$ ។"), CH, "integral_rational", "steps_division", "medium", P, T(v), "rat_div")
# Absolute value, properties, mean value
def abs_val(rng):
    r1, r2 = sorted(rng.sample(range(-4, 5), 2)); kind = rng.choice([1, 2]); w = W(rng)
    g = x - r1 if kind == 1 else sp.expand((x - r1) * (x - r2)); pts = [r1] if kind == 1 else [r1, r2]; a = pts[0] - rng.randint(1, 3); b = pts[-1] + rng.randint(1, 3); P = f"{w.v(*ASK_I)} $$I=\\int_{{{a}}}^{{{b}}}\\left|{T(g)}\\right|\\,dx$$"
    edges = [a] + pts + [b]; w.say(f"សិក្សាសញ្ញានៃ ${T(g)}$ ៖ វាស្មើសូន្យត្រង់ " + " និង ".join(f"$x={p}$" for p in pts) + " ។"); parts = []; v = 0; G = sp.integrate(g, x)
    for lo, hi in zip(edges, edges[1:]):
        s = 1 if g.subs(x, R(lo + hi, 2)) > 0 else -1; parts.append((lo, hi, s)); v += s * (G.subs(x, hi) - G.subs(x, lo))
    w.say("$$I=" + "+".join(Int(B(s * g), lo, hi) for lo, hi, s in parts) + "$$"); w.say("$$=" + "+".join(f"\\left[{T(s * G)}\\right]_{{{lo}}}^{{{hi}}}" for lo, hi, s in parts) + "$$"); w.say("$$=" + "+".join(f"\\left({T(s * (G.subs(x, hi) - G.subs(x, lo)))}\\right)" for lo, hi, s in parts) + f"={T(v)}$$"); w.C.append(check(f"nint_abs({g},{a},{b})", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{I={T(v)}}}$ ។"), CH, "integral_definite", "steps_absolute_value", "bacii", P, T(v), "abs_val")
def props(rng):
    a = rng.randint(-3, 1); b = a + rng.randint(1, 3); c = b + rng.randint(1, 3); p, q, r = nz(rng), nz(rng), nz(rng); m, n = nz(rng, -5, 5), nz(rng, -5, 5); w = W(rng); v1 = p + q; v2 = m * p + n * r
    P = f"គេដឹងថា $\\int_{{{a}}}^{{{b}}}f(x)\\,dx={p}$ , $\\int_{{{b}}}^{{{c}}}f(x)\\,dx={q}$ និង $\\int_{{{a}}}^{{{b}}}g(x)\\,dx={r}$ ។ គណនា ៖\nក. $\\int_{{{a}}}^{{{c}}}f(x)\\,dx$\nខ. $\\int_{{{b}}}^{{{a}}}f(x)\\,dx$\nគ. $\\int_{{{a}}}^{{{b}}}\\left[{cf(m)}f(x){sg(n)}g(x)\\right]dx$"
    w.say(f"ក. តាមទំនាក់ទំនងឆាល ៖ $$\\int_{{{a}}}^{{{c}}}f(x)\\,dx=\\int_{{{a}}}^{{{b}}}f(x)\\,dx+\\int_{{{b}}}^{{{c}}}f(x)\\,dx={p}{st(q)}={v1}$$"); w.say(f"ខ. ប្តូរព្រំដែនប្តូរសញ្ញា ៖ $$\\int_{{{b}}}^{{{a}}}f(x)\\,dx=-\\int_{{{a}}}^{{{b}}}f(x)\\,dx={-p}$$"); w.say(f"គ. តាមលក្ខណៈលីនេអ៊ែរ ៖ $$\\int_{{{a}}}^{{{b}}}\\left[{cf(m)}f(x){sg(n)}g(x)\\right]dx={cf(m)}\\left({p}\\right){sg(n)}\\left({r}\\right)={v2}$$"); w.C += [check(f"{p}+{q}", v1, "a"), check(f"{m}*{p}+{n}*{r}", v2, "c")]
    return row(w.say(f"{so(w)} $\\boxed{{{v1}}}$ , $\\boxed{{{-p}}}$ , $\\boxed{{{v2}}}$ ។"), CH, "integral_definite", "steps_properties", "easy", P, f"{v1};\\ {-p};\\ {v2}", "props")
def mean_val(rng):
    f, F, cs, t = combo(rng); a, b = nicebounds(rng, f)
    if f.has(sp.sin, sp.cos, sp.log) or any(q.is_Pow and q.exp.is_number and (q.exp < 0 or not q.exp.is_integer) for q in sp.preorder_traversal(f)) or f.has(sp.exp): 
        n = rng.randint(1, 3); f = sum(nz(rng, -4, 6) * x ** i for i in range(n + 1)); F = sp.integrate(f, x); a = rng.randint(-2, 2); b = a + rng.randint(1, 4)
    v = (F.subs(x, b) - F.subs(x, a)); m = v / (b - a); w = W(rng); P = f"គណនាតម្លៃមធ្យមនៃអនុគមន៍ $f(x)={T(f)}$ លើចន្លោះ $\\left[{a};{b}\\right]$ ។"
    w.say("តម្លៃមធ្យម ៖ $$\\bar{f}=\\frac{1}{b-a}\\int_a^bf(x)\\,dx$$"); pre = "" if b - a == 1 else f"\\frac{{1}}{{{b - a}}}"; w.say(f"$$\\bar{{f}}={pre}{Int(f, a, b)}={pre}{EV(rng, T(F), a, b)}$$"); w.say(f"$$={pre}\\left({T(v)}\\right)={T(m)}$$"); w.C.append(check(f"integrate({f},(x,{a},{b}))/({b - a})", m, "mean"))
    return row(w.say(f"{so(w)} $\\boxed{{\\bar{{f}}={T(m)}}}$ ។"), CH, "integral_definite", "steps_mean_value_textbook", "medium", P, T(m), "mean_val")
def riemann(rng):
    a = rng.randint(0, 2); b = a + rng.randint(1, 3); c, d = rng.choice([1, 2, 3]), rng.randint(-3, 3); kind = rng.choice([1, 2]); f = c * x + d if kind == 1 else c * x ** 2 + d; h = b - a; n, i = sp.symbols("n i", positive=True, integer=True); xi = a + h * i / n; w = W(rng); P = f"គណនា $\\int_{{{a}}}^{{{b}}}{B(f)}\\,dx$ តាមនិយមន័យ ដោយប្រើផលបូកអាំងតេក្រាល ។"
    w.say(f"ចែកអង្កត់ $\\left[{a};{b}\\right]$ ជា $n$ ផ្នែកស្មើៗគ្នា គេបាន $\\Delta x=\\frac{{{h}}}{{n}}$ និង $x_i={T(xi)}$ ។"); S = sp.simplify(sp.summation(f.subs(x, xi) * h / n, (i, 1, n))); fi = sp.expand(f.subs(x, xi)); w.say(f"$$f(x_i)={T(fi)}$$"); w.say("ផលបូកអាំងតេក្រាល ៖ ដោយ $\\sum_{i=1}^{n}i=\\frac{n(n+1)}{2}$ និង $\\sum_{i=1}^{n}i^2=\\frac{n(n+1)(2n+1)}{6}$ គេបាន ៖"); w.say(f"$$S_n=\\sum_{{i=1}}^{{n}}f(x_i)\\Delta x=\\sum_{{i=1}}^{{n}}\\left({T(fi)}\\right)\\frac{{{h}}}{{n}}={T(sp.expand(S))}$$"); v = sp.limit(S, n, sp.oo); w.say(f"លីមីតនៃ $S_n$ កាលណា $n\\to\\infty$ ៖ $$\\lim_{{n\\to\\infty}}S_n={T(v)}$$"); w.C.append(check(f"integrate({f},(x,{a},{b}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{{T(v)}}}$ ។"), CH, "integral_definite", "steps_riemann_textbook", "medium", P, T(v), "riemann")
def recur(rng):
    kind = rng.choice(["e", "ln"]); w = W(rng); n = sp.Symbol("n")
    if kind == "e":
        P = "គេឱ្យ $I_n=\\int_0^1x^ne^x\\,dx$ ចំពោះ $n\\in\\mathbb{N}$ ។\nក. គណនា $I_0$ ។\nខ. បង្ហាញថា $I_{n+1}=e-(n+1)I_n$ ។\nគ. ទាញរក " + rng.choice(["$I_1$ និង $I_2$ ។", "$I_2$ និង $I_3$ ។", "$I_3$ ។"]); vals = [sp.E - 1]
        for k in range(4): vals.append(sp.expand(sp.E - (k + 1) * vals[-1]))
        w.say("ក. $$I_0=\\int_0^1e^x\\,dx=\\left[e^x\\right]_0^1=e-1$$"); w.say("ខ. តាង $u=x^{n+1}$ និង $dv=e^x\\,dx$ គេបាន $du=(n+1)x^n\\,dx$ និង $v=e^x$ ។"); w.say("$$I_{n+1}=\\left[x^{n+1}e^x\\right]_0^1-(n+1)\\int_0^1x^ne^x\\,dx=e-(n+1)I_n$$"); w.say("គ. អនុវត្តទំនាក់ទំនងនេះជាបន្តបន្ទាប់ ៖")
        for k in range(1, 4): w.say(f"$$I_{k}=e-{cf(k)}I_{k - 1}={T(vals[k])}$$"); w.C.append(check(f"integrate(x**{k}*exp(x),(x,0,1))", vals[k], f"I{k}"))
        L = "I_3=" + T(vals[3])
    else:
        return None
    return row(w.say(f"{so(w)} $\\boxed{{{L}}}$ ។"), CH, "integral_parts", "steps_recurrence_In", "bacii", P, L, "recur")
def prim_cond(rng):
    while True:
        f, F, cs, t = combo(rng)
        if not (any(q.is_Pow and q.exp.is_number and (q.exp < 0 or not q.exp.is_integer) for q in sp.preorder_traversal(f)) or f.has(sp.sin, sp.cos)): break
    x0 = rng.choice([0, 0, 1]); y0 = nz(rng, -6, 8); c = y0 - F.subs(x, x0)
    if F.has(sp.log) and x0 == 0: x0 = 1; c = y0 - F.subs(x, 1)
    w = W(rng); P = f"រកព្រីមីទីវ $F$ នៃអនុគមន៍ $f(x)={T(f)}$ ដែល $F({x0})={y0}$ ។"; w.say(f"ព្រីមីទីវទូទៅ ៖ $$F(x)={T(F)}+c$$ ($c$ ថេរ)"); w.say(f"ដោយ $F({x0})={y0}$ គេបាន ${T(F.subs(x, x0))}+c={y0}$ នាំឱ្យ $c={T(c)}$ ។"); G = F + c; w.C += [check(f"diff({G},x)", f, "primitive"), check(str(G.subs(x, x0)), y0, "value")]
    return row(w.say(f"{so(w)} $\\boxed{{F(x)={T(G)}}}$ ។"), CH, "integral_primitive", "steps_primitive_condition", "easy", P, f"F(x)={T(G)}", "prim_cond")
def prim_coef(rng):
    a, b = nz(rng, -4, 5), rng.randint(-5, 5); k = rng.choice([1, 2, -1, 3]); G = (a * x + b) * sp.exp(k * x); f = sp.expand(sp.diff(G, x) / sp.exp(k * x)) * sp.exp(k * x); p, q = sp.Poly(sp.expand(f / sp.exp(k * x)), x).all_coeffs(); w = W(rng); A, Bs = sp.symbols("a b"); e = sp.exp(k * x); ft = f"\\left({T(p * x + q)}\\right){T(e)}"
    lo, hi = rng.choice([(0, 1), (0, 2), (-1, 0)]); v = sp.expand(G.subs(x, hi) - G.subs(x, lo)); P = f"គេឱ្យអនុគមន៍ $f(x)={ft}$ ។\nក. កំណត់ចំនួនពិត $a$ និង $b$ ដែល $F(x)=(ax+b){T(e)}$ ជាព្រីមីទីវនៃ $f$ ។\nខ. ទាញរក $\\int_{{{lo}}}^{{{hi}}}f(x)\\,dx$ ។"
    w.say(f"ក. $F'(x)=a{T(e)}{sg(k)}(ax+b){T(e)}=\\left({T(k * A * x + A + k * Bs)}\\right){T(e)}$ ។"); w.say(f"ដោយ $F'(x)=f(x)$ ផ្ទឹមមេគុណ ៖ $$\\begin{{cases}}{T(k * A)}={T(p)}\\\\{T(A + k * Bs)}={T(q)}\\end{{cases}}$$"); w.say(f"នាំឱ្យ $a={a}$ និង $b={b}$ ។ ដូចនេះ $F(x)={B(a * x + b)}{T(e)}$ ។"); w.say(f"ខ. $$\\int_{{{lo}}}^{{{hi}}}f(x)\\,dx=F({hi})-F({lo})={T(v)}$$"); w.C += [check(f"diff({G},x)", f, "F'"), check(f"integrate({f},(x,{lo},{hi}))", v, "value")]
    return row(w.say(f"{so(w)} $\\boxed{{a={a},\\ b={b}}}$ និង $\\boxed{{{T(v)}}}$ ។"), CH, "integral_primitive", "steps_find_coefficients", "bacii", P, f"a={a};\\ b={b};\\ {T(v)}", "prim_coef")
def show_then(rng):
    n = rng.choice([0, 1, 2]); kind = rng.choice(["xlnx", "lnx2"]); w = W(rng); e = rng.choice([sp.E, sp.E ** 2])
    if kind == "xlnx": F, f, ft, sh, dv = x * sp.log(x) - x, sp.log(x), "\\ln x", "x\\ln x-x", "\\ln x+x\\cdot\\frac{1}{x}-1=\\ln x"
    else: F, f, ft, sh, dv = x * sp.log(x) ** 2 - 2 * x * sp.log(x) + 2 * x, sp.log(x) ** 2, "\\ln^2x", "x\\ln^2x-2x\\ln x+2x", "\\ln^2x+2\\ln x-2\\ln x-2+2=\\ln^2x"
    v = V(F.subs(x, e) - F.subs(x, 1)); P = f"ក. បង្ហាញថា $F(x)={sh}$ ជាព្រីមីទីវនៃ $f(x)={ft}$ លើ $(0;+\\infty)$ ។\nខ. ទាញរក $\\int_1^{{{T(e)}}}{ft}\\,dx$ ។"; w.say(f"ក. គណនាដេរីវេ ៖ $$F'(x)={dv}$$"); w.ok(sp.diff(F, x), f); w.say(f"ដូចនេះ $F$ ជាព្រីមីទីវនៃ $f$ ។"); w.say(f"ខ. $$\\int_1^{{{T(e)}}}{ft}\\,dx=F\\left({T(e)}\\right)-F(1)=\\left({T(F.subs(x, e))}\\right)-\\left({T(F.subs(x, 1))}\\right)={T(v)}$$"); w.C.append(check(f"integrate({f},(x,1,{e}))", v, "value"))
    return row(w.say(f"{so(w)} $\\boxed{{{T(v)}}}$ ។"), CH, "integral_primitive", "steps_show_then_use", "medium", P, T(v), "show_then")
# Area, volume, length
def area_axis(rng):
    r1, r2 = sorted(rng.sample(range(-6, 7), 2)); s = rng.choice([1, -1, 2, -2, 3, -3]); f = sp.expand(s * (x - r1) * (x - r2)); F = sp.integrate(f, x); v = abs(F.subs(x, r2) - F.subs(x, r1)); w = W(rng); P = f"គណនាផ្ទៃក្រឡានៃផ្ទៃដែលខណ្ឌដោយក្រាបតាងអនុគមន៍ $y={T(f)}$ និងអ័ក្ស $x'ox$ ។"
    w.say(f"ចំណុចប្រសព្វជាមួយអ័ក្ស ៖ ${T(f)}=0$ នាំឱ្យ $x_1={r1}$ , $x_2={r2}$ ។"); sg = "ក្រាបនៅខាងលើអ័ក្ស" if s < 0 else "ក្រាបនៅខាងក្រោមអ័ក្ស"; w.say(f"លើចន្លោះ $\\left[{r1};{r2}\\right]$ {sg} ។"); g = f if s < 0 else -f; G = F if s < 0 else -F; w.say(f"$$S={Int(g, r1, r2)}={EV(rng, T(G), r1, r2)}$$"); w.say(f"$$=\\left({T(G.subs(x, r2))}\\right)-\\left({T(G.subs(x, r1))}\\right)={T(v)}$$"); w.C.append(check(f"nint_abs({f},{r1},{r2})", v, "area"))
    r = row(w.say(f"{so(w)} $\\boxed{{S={T(v)}}}$ ឯកតាផ្ទៃក្រឡា ។"), CH, "integral_area", "steps_area_axis", "medium", P, T(v), "area_axis"); r["_plot"] = (str(f), "0", r1, r2); return r
def area_two(rng):
    r1, r2 = sorted(rng.sample(range(-3, 5), 2)); kind = rng.choice(["pl", "pp"]); c = rng.choice([1, 1, 2, 3]); d = sp.expand(c * (x - r1) * (r2 - x))   # top - bottom
    if kind == "pl": g = nz(rng, -3, 3) * x + rng.randint(-4, 4); f = sp.expand(g + d)
    else: q = rng.choice([1, 2, -1]); g = q * x ** 2 + rng.randint(-3, 3) * x + rng.randint(-3, 3); f = sp.expand(g + d)
    if sp.degree(f, x) < 2 and kind == "pp": return None
    F = sp.integrate(d, x); v = F.subs(x, r2) - F.subs(x, r1); w = W(rng); P = f"គណនាផ្ទៃក្រឡាដែលខណ្ឌដោយក្រាបតាងអនុគមន៍ $f(x)={T(f)}$ និង $g(x)={T(g)}$ ។"
    w.say(f"ចំណុចប្រសព្វ ៖ ${T(f)}={T(g)}$ សមមូល ${T(sp.expand(-d))}=0$ នាំឱ្យ $x={r1}$ ឬ $x={r2}$ ។"); w.say(f"លើចន្លោះ $\\left[{r1};{r2}\\right]$ គេមាន $f(x)-g(x)={T(d)}\\geq0$ ។"); w.say(f"$$S={Int(d, r1, r2)}={EV(rng, T(F), r1, r2)}$$"); w.say(f"$$=\\left({T(F.subs(x, r2))}\\right)-\\left({T(F.subs(x, r1))}\\right)={T(v)}$$"); w.C.append(check(f"nint_abs(({f})-({g}),{r1},{r2})", v, "area"))
    r = row(w.say(f"{so(w)} $\\boxed{{S={T(v)}}}$ ឯកតាផ្ទៃក្រឡា ។"), CH, "integral_area", f"steps_area_two_curves_{kind}", "bacii", P, T(v), "area_two"); r["_plot"] = (str(f), str(g), r1, r2); return r
def area_tr(rng):
    kind = rng.choice(["exp", "ln", "inv", "sin", "sqrt"]); k = rng.randint(1, 9); w = W(rng)
    if kind == "exp": f = k * sp.exp(x) + rng.randint(0, 3); a, b = rng.choice([(0, 1), (0, 2), (-1, 1), (1, 2)])
    elif kind == "ln": f = sp.log(x) * k; a, b = rng.choice([(1, sp.E), (1, sp.E ** 2)])
    elif kind == "inv": f = k / x + rng.randint(0, 2); a, b = rng.choice([(1, 2), (1, sp.E), (1, 3), (2, 4)])
    elif kind == "sin": f = k * sp.sin(x); a, b = rng.choice([(0, sp.pi), (0, sp.pi / 2)])
    else: f = k * sp.sqrt(x); a, b = rng.choice([(0, 1), (0, 4), (1, 4), (0, 9)])
    F = sp.integrate(f, x); v = V(F.subs(x, b) - F.subs(x, a)); P = f"គណនាផ្ទៃក្រឡានៃផ្ទៃដែលខណ្ឌដោយក្រាបតាងអនុគមន៍ $y={T(f)}$ អ័ក្ស $x'ox$ និងបន្ទាត់ឈរ $x={T(a)}$ , $x={T(b)}$ ។"; w.say(f"លើចន្លោះ $\\left[{T(a)};{T(b)}\\right]$ គេមាន $y\\geq0$ ។"); w.say(f"$$S={Int(f, a, b)}={EV(rng, T(F), a, b)}$$"); w.say(f"$$={T(v)}$$"); w.C.append(check(f"integrate({f},(x,{a},{b}))", v, "area"))
    r = row(w.say(f"{so(w)} $\\boxed{{S={T(v)}}}$ ឯកតាផ្ទៃក្រឡា ។"), CH, "integral_area", f"steps_area_{kind}", "medium", P, T(v), "area_tr"); r["_plot"] = (str(f), "0", float(a), float(b)); return r
def area_asym(rng):
    d = nz(rng, -3, 3); p, q, r = rng.choice([1, 2]), rng.randint(-3, 3), rng.choice([1, 2, 3, 4, 5]); N = sp.expand((p * x + q) * (x + d) + r); D = x + d; lo = max(1, -d + 1); hi = lo + rng.randint(1, 4); v = r * sp.log(hi + d) - r * sp.log(lo + d); v = sp.expand_log(v, force=False); w = W(rng); ft = f"\\frac{{{T(N)}}}{{{T(D)}}}"
    P = f"គេឱ្យអនុគមន៍ $f(x)={ft}$ ។\nក. បង្ហាញថា បន្ទាត់ $(d):y={T(p * x + q)}$ ជាអាស៊ីមតូតទ្រេតនៃក្រាប $(C)$ ។\nខ. សិក្សាទីតាំង $(C)$ ធៀបនឹង $(d)$ លើ $\\left[{lo};{hi}\\right]$ ។\nគ. គណនាផ្ទៃក្រឡាខណ្ឌដោយ $(C)$ , $(d)$ និងបន្ទាត់ឈរ $x={lo}$ , $x={hi}$ ។"
    w.say(f"ក. ចែកភាគយកនឹងភាគបែង ៖ $f(x)={T(p * x + q)}+\\frac{{{r}}}{{{T(D)}}}$ ។"); w.ok(N / D, p * x + q + r / D); w.say(f"$$\\lim_{{x\\to\\pm\\infty}}\\left[f(x)-\\left({T(p * x + q)}\\right)\\right]=\\lim_{{x\\to\\pm\\infty}}\\frac{{{r}}}{{{T(D)}}}=0$$"); w.say("ដូចនេះ $(d)$ ជាអាស៊ីមតូតទ្រេត ។"); w.say(f"ខ. លើ $\\left[{lo};{hi}\\right]$ គេមាន ${T(D)}>0$ នាំឱ្យ $f(x)-y=\\frac{{{r}}}{{{T(D)}}}>0$ ។ ដូចនេះ $(C)$ នៅខាងលើ $(d)$ ។"); w.say(f"គ. $$S=\\int_{{{lo}}}^{{{hi}}}\\frac{{{r}}}{{{T(D)}}}\\,dx={EV(rng, f'{cf(r)}\\ln\\left|{T(D)}\\right|', lo, hi)}$$"); w.say(f"$$={T(v)}$$"); w.C.append(check(f"integrate(({N})/({D})-({p * x + q}),(x,{lo},{hi}))", v, "area"))
    rr = row(w.say(f"{so(w)} $\\boxed{{S={T(v)}}}$ ឯកតាផ្ទៃក្រឡា ។"), CH, "integral_area", "steps_area_slant_asymptote", "bacii", P, T(v), "area_asym"); rr["_plot"] = (f"({N})/({D})", str(p * x + q), lo, hi); return rr
def vol_one(rng):
    kind = rng.choice(["poly", "sqrt", "exp", "sin", "inv", "line"]); k = rng.randint(1, 9); w = W(rng)
    if kind == "poly": r = rng.randint(1, 3); f = k * (r ** 2 - x ** 2) if k < 3 else r ** 2 - x ** 2; a, b = -r, r
    elif kind == "sqrt": f = sp.sqrt(k * x); a, b = 0, rng.randint(1, 5)
    elif kind == "exp": f = sp.exp(k * x); a, b = 0, rng.choice([1, 2])
    elif kind == "sin": f = sp.sin(x); a, b = 0, sp.pi
    elif kind == "inv": f = k / x; a, b = 1, rng.randint(2, 5)
    else: f = k * x + rng.randint(0, 3); a, b = 0, rng.randint(1, 4)
    sq = sp.expand(f ** 2) if kind != "sin" else sp.sin(x) ** 2; G = sp.integrate(sq, x); v = V(sp.pi * (G.subs(x, b) - G.subs(x, a))); P = f"គណនាមាឌសូលីតបរិវត្ត កំណត់បានពីរង្វិលជុំវិញអ័ក្ស $x'ox$ នៃផ្ទៃដែលខណ្ឌដោយក្រាបតាងអនុគមន៍ $y={T(f)}$ អ័ក្ស $x'ox$ លើចន្លោះ $\\left[{T(a)};{T(b)}\\right]$ ។"
    w.say("រូបមន្ត ៖ $V=\\pi\\int_a^b\\left[f(x)\\right]^2dx$ ។"); w.say(f"$$V=\\pi{Int(sq, a, b)}$$"); w.say(f"$$=\\pi{EV(rng, T(G), a, b)}$$"); w.say(f"$$={T(v)}$$"); w.C.append(check(f"pi*integrate(({f})**2,(x,{a},{b}))", v, "volume"))
    return row(w.say(f"{so(w)} $\\boxed{{V={T(v)}}}$ ឯកតាមាឌ ។"), CH, "integral_volume", f"steps_volume_{kind}", "medium", P, T(v), "vol_one")
def vol_two(rng):
    m = rng.choice([1, 4, 9, 16]); r = sp.sqrt(m)
    t = rng.choice([1, 2]); 
    if t == 1: f, g = 2 * m - x ** 2, x ** 2; a, b = -r, r
    else: q = rng.randint(1, 9); f, g = q * x, x ** 2; a, b = 0, q
    sq = sp.expand(f ** 2 - g ** 2); G = sp.integrate(sq, x); v = V(sp.pi * (G.subs(x, b) - G.subs(x, a))); w = W(rng); P = f"គណនាមាឌសូលីតបរិវត្តកំណត់បានពីរង្វិលជុំវិញអ័ក្ស $x'ox$ នៃផ្ទៃដែលខណ្ឌដោយក្រាបតាងអនុគមន៍ $f(x)={T(f)}$ និង $g(x)={T(g)}$ ។"
    w.say(f"ចំណុចប្រសព្វ ៖ ${T(f)}={T(g)}$ នាំឱ្យ $x={T(a)}$ ឬ $x={T(b)}$ ។"); w.say(f"$$V=\\pi{Int(f'\\left[\\left({T(f)}\\right)^2-\\left({T(g)}\\right)^2\\right]', a, b)}$$"); w.say(f"$$=\\pi{Int(sq, a, b)}$$"); w.say(f"$$=\\pi{EV(rng, T(G), a, b)}={T(v)}$$"); w.C.append(check(f"pi*integrate(({f})**2-({g})**2,(x,{a},{b}))", v, "volume"))
    return row(w.say(f"{so(w)} $\\boxed{{V={T(v)}}}$ ឯកតាមាឌ ។"), CH, "integral_volume", "steps_volume_two_curves", "bacii", P, T(v), "vol_two")
def arc(rng):
    n = rng.choice([2, 3]); a, b = rng.choice([(1, 2), (1, 3), (2, 3)]); k = rng.randint(1, 4); w = W(rng)
    if n == 3: f = x ** 3 / 3 + 1 / (4 * x); u = x ** 2 + 1 / (4 * x ** 2); d = x ** 2 - 1 / (4 * x ** 2)
    else: f = x ** 2 / 2 - sp.log(x) / 4; u = x + 1 / (4 * x); d = x - 1 / (4 * x)
    G = sp.integrate(u, x); v = V(G.subs(x, b) - G.subs(x, a)); P = f"គណនាប្រវែងធ្នូនៃក្រាបតាងអនុគមន៍ $y={T(f)}$ ពី $x={a}$ ទៅ $x={b}$ ។"; w.say(f"$$y'={T(d)}$$"); w.say("ប្រវែងធ្នូ ៖ $L=\\int_a^b\\sqrt{1+\\left(y'\\right)^2}\\,dx$ ។"); w.ok(1 + d ** 2, u ** 2); w.say(f"ដោយ $1+\\left(y'\\right)^2=\\left({T(u)}\\right)^2$ គេបាន ៖"); w.say(f"$$L={Int(u, a, b)}={EV(rng, T(G), a, b)}={T(v)}$$"); w.C.append(check(f"integrate({u},(x,{a},{b}))", v, "length"))
    return row(w.say(f"{so(w)} $\\boxed{{L={T(v)}}}$ ឯកតាប្រវែង ។"), CH, "integral_volume", "steps_arc_length", "bacii", P, T(v), "arc")
ALL = [(lin_prim, 900), (lin_def, 900), (comp_lin, 700), (sub_indef, 700), (sub_def, 700), (parts_indef, 500), (parts_def, 500), (trig_pow, 300), (ij_pair, 30), (rat_pf, 600), (rat_div, 500), (abs_val, 300), (props, 300), (mean_val, 200), (riemann, 150), (recur, 3), (prim_cond, 400), (prim_coef, 300), (show_then, 6), (area_axis, 200), (area_two, 500), (area_tr, 60), (area_asym, 300), (vol_one, 150), (vol_two, 30), (arc, 6)]

def finish(rows):
    """Draw the shaded region for area rows, after duplicates are gone."""
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from common import ROOT, tikz_graph
    os.makedirs(os.path.join(ROOT, "diagrams"), exist_ok=True)
    for r in rows:
        d = r.pop("_plot", None)
        if not d: continue
        fs, gs, a, b = d; f = sp.sympify(fs, locals={"x": x}); g = sp.sympify(gs, locals={"x": x}); a, b = float(a), float(b); pad = max(1.0, (b - a) * .35)
        lo = a - pad if not f.has(sp.log, sp.sqrt) and not any(q.is_Pow and q.exp.is_number and q.exp < 0 for q in sp.preorder_traversal(f)) else a + (0 if a > 0.3 else 1e-3); hi = b + pad
        xs = np.linspace(lo, hi, 500); xi = np.linspace(a if a > 0 or not f.has(sp.log) else 1e-3, b, 300)
        ev = lambda e, t: np.broadcast_to(np.asarray(sp.lambdify(x, e, "numpy")(t), dtype=float), t.shape)
        with np.errstate(all="ignore"):
            yf, yg = ev(f, xs), ev(g, xs); fi, gi = ev(f, xi), ev(g, xi)
        fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=100); ax.plot(xs, yf, lw=1.8, color="#1f4e9c")
        if g != 0: ax.plot(xs, yg, lw=1.6, color="#c0392b")
        ax.fill_between(xi, fi, gi, color="#1f4e9c", alpha=.22, hatch="///", edgecolor="#1f4e9c", lw=0)
        top = max(fi.max(), gi.max(), 0); bot = min(fi.min(), gi.min(), 0); m = max(1.0, (top - bot) * .25); ax.set_ylim(bot - m, top + m); ax.set_xlim(lo, hi)
        for sd in ("top", "right"): ax.spines[sd].set_visible(False)
        for sd in ("left", "bottom"): ax.spines[sd].set_position("zero")
        ax.grid(alpha=.2); rel = f"diagrams/{r['id']}.png"; fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
        pg = lambda e: str(e).replace("**", "^").replace("log", "ln")
        extra = "" if g == 0 else f"\\addplot[thick,domain={lo:.2f}:{hi:.2f}] {{{pg(g)}}};\n"
        r["diagrams"] = [{"type": "graph", "latex": tikz_graph(pg(f), round(lo, 2), round(hi, 2), round(bot - m, 2), round(top + m, 2), extra), "image": rel, "alt_km": "ក្រាប និងផ្ទៃដែលត្រូវគណនា"}]
    return rows
