"""Differential equations chapter. Solutions are chosen first, then every printed result is checked by substitution."""
from kx import *
CH = "diffeq"
Ac, Bc, Cc = sp.symbols("A B c")
SAMPLES = ((2, -3), (1, 5), (-4, 1))
def dcheck(w, y, a, p, q, rhs, note="ode"):
    """Residual check of a*y''+p*y'+q*y=rhs for sample constants."""
    for s, t in SAMPLES:
        e = y.subs({Ac: s, Bc: t, Cc: s})
        lhs = a * sp.diff(e, x, 2) + p * sp.diff(e, x) + q * e
        assert sp.simplify(lhs - rhs) == 0, (e, lhs, rhs)
        w.C.append(check(f"({a})*diff({e},x,2)+({p})*diff({e},x)+({q})*({e})", rhs, note))
def eq2(a, p, q):
    t = f"{cf(a)}y''"
    if p: t += ("+" if p > 0 else "-") + cf(abs(p)) + "y'"
    if q: t += ("+" if q > 0 else "-") + cf(abs(q)) + "y"
    return t
def eq1(p, q):
    t = f"{cf(p)}y'"
    if q: t += ("+" if q > 0 else "-") + cf(abs(q)) + "y"
    return t
def lam2(a, p, q):
    t = f"{cf(a)}\\lambda^2"
    if p: t += ("+" if p > 0 else "-") + cf(abs(p)) + "\\lambda"
    if q: t += ("+" if q > 0 else "-") + T(abs(q))
    return t
def exp_term(c, r):
    return c * sp.exp(r * x)
def homog2(w, a, p, q, name=None):
    """Print the solving of a y''+p y'+q y=0; return general solution in A, B."""
    w.say((f"សមីការសម្គាល់នៃ ${name}$ គឺ ៖" if name else w.v("សមីការសម្គាល់ ៖", "សមីការសម្គាល់គឺ ៖")) + f" $${lam2(a, p, q)}=0$$")
    D = p ** 2 - 4 * a * q
    w.say(f"$\\Delta={par(p)}^2-4\\cdot{par(a)}\\cdot{par(q)}={T(D)}$ ។")
    if D > 0:
        s = sp.sqrt(D); r1, r2 = (-p - s) / (2 * a), (-p + s) / (2 * a); r1, r2 = sorted((sp.nsimplify(r1), sp.nsimplify(r2)))
        w.say(f"សមីការមានឫសពីរផ្សេងគ្នា $\\lambda_1={T(r1)}$ និង $\\lambda_2={T(r2)}$ ។"); y = Ac * sp.exp(r1 * x) + Bc * sp.exp(r2 * x); w.say("ចម្លើយទូទៅមានរាង $y=Ae^{\\lambda_1x}+Be^{\\lambda_2x}$ ។")
    elif D == 0:
        r = R(-p, 2 * a); w.say(f"សមីការមានឫសឌុប $\\lambda_1=\\lambda_2={T(r)}$ ។"); y = (Ac * x + Bc) * sp.exp(r * x); w.say("ចម្លើយទូទៅមានរាង $y=(Ax+B)e^{\\lambda x}$ ។")
    else:
        al = R(-p, 2 * a); be = sp.sqrt(-D) / (2 * abs(a)); w.say(f"សមីការមានឫសកុំផ្លិចឆ្លាស់ $\\lambda=\\alpha\\pm i\\beta$ ដែល $\\alpha={T(al)}$ និង $\\beta={T(be)}$ ។"); y = sp.exp(al * x) * (Ac * sp.cos(be * x) + Bc * sp.sin(be * x)); w.say("ចម្លើយទូទៅមានរាង $y=e^{\\alpha x}\\left(A\\cos\\beta x+B\\sin\\beta x\\right)$ ។")
    return y
def pick2(rng, kind=None):
    kind = kind or rng.choice(["real", "real", "double", "complex", "pure", "zero", "frac"])
    if kind == "real": r1, r2 = rng.sample(range(-7, 8), 2); m = rng.choice([1, 1, 1, 2, 3, -1]); return m, -m * (r1 + r2), m * r1 * r2
    if kind == "frac": a = rng.choice([2, 3]); n = rng.choice([1, -1, 3, -3, 5]); r = rng.randint(-4, 4); return a, -(n + a * r), n * r
    if kind == "double": r = nz(rng, -6, 6); m = rng.choice([1, 1, 2]); return m, -2 * r * m, m * r * r
    if kind == "complex": al, be = nz(rng, -4, 4), rng.randint(1, 6); return 1, -2 * al, al ** 2 + be ** 2
    if kind == "pure": be = rng.randint(1, 9); m = rng.choice([1, 1, 2]); return m, 0, m * be ** 2
    r = nz(rng, -7, 7); return 1, -r, 0
def d_direct(rng):
    from integral import combo
    while True:
        f, F, cs, t = combo(rng)
        if not (f.has(sp.log) or any(q.is_Pow and q.exp.is_number and (q.exp < 0 or not q.exp.is_integer) for q in sp.preorder_traversal(f))): break
    x0 = 0; y0 = rng.randint(-6, 8); c = y0 - F.subs(x, 0); w = W(rng); ini = rng.random() < .6
    P = f"ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល $y'={T(f)}$" + (f" ដែល $y(0)={y0}$ ។" if ini else " ។")
    w.say(f"{gb(w)} $$\\frac{{dy}}{{dx}}={T(f)}$$"); w.say(f"$$y={Int(f)}={T(F)}+c$$ ($c$ ថេរ)")
    if not ini:
        y = F + Cc; dcheck(w, y, 0, 1, 0, f); return row(w.say(f"{so(w)} $\\boxed{{y={T(F)}+c}}$ ។"), CH, "de_first_order", "steps_direct_integration", "easy", P, f"y={T(F)}+c", "d_direct")
    w.say(f"ដោយ $y(0)={y0}$ នាំឱ្យ ${T(F.subs(x, 0))}+c={y0}$ ឬ $c={T(c)}$ ។"); y = F + c; dcheck(w, y, 0, 1, 0, f); w.C.append(check(str(y.subs(x, 0)), y0, "initial"))
    return row(w.say(f"{so(w)} $\\boxed{{y={T(y)}}}$ ។"), CH, "de_first_order", "steps_direct_initial", "easy", P, f"y={T(y)}", "d_direct")
def d_homog1(rng):
    p = rng.choice([1, 1, 2, 3, 4, 5, -2, -3]); q = nz(rng, -9, 9); r = R(-q, p); w = W(rng); ini = rng.random() < .55; x0 = rng.choice([0, 0, 0, 1]); y0 = nz(rng, -6, 9); tt = rng.random() < .3; lhs = eq1(p, q) if not tt else f"{cf(p)}\\frac{{dy}}{{dx}}" + ("+" if q > 0 else "-") + cf(abs(q)) + "y"
    P = w.v("ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលលីនេអែលំដាប់ ១ ៖", "ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល ៖") + f" $${lhs}=0$$" + (f"\nដោយដឹងថា $y({x0})={y0}$ ។" if ini else "")
    w.say(f"{gb(w)} $\\frac{{dy}}{{dx}}={T(r)}y$ ឬ $\\frac{{dy}}{{y}}={T(r)}\\,dx$ ។"); w.say(f"$$\\int\\frac{{dy}}{{y}}=\\int {T(r)}\\,dx$$"); w.say(f"$$\\ln|y|={T(r * x)}+k$$ ($k$ ថេរ)"); w.say(f"នាំឱ្យ $y=\\pm e^{{{T(r * x)}+k}}=ce^{{{T(r * x)}}}$ (យក $c=\\pm e^k$) ។"); e = sp.exp(r * x)
    if not ini:
        y = Cc * e; dcheck(w, y, 0, p, q, 0); return row(w.say(f"{so(w)} $\\boxed{{y=c{T(e)}}}$ ($c$ ថេរ) ។"), CH, "de_first_order", "steps_homogeneous_first", "easy", P, f"y=c{T(e)}", "d_homog1")
    c = y0 * sp.exp(-r * x0); y = y0 * sp.exp(r * (x - x0)); w.say(f"ដោយ $y({x0})={y0}$ នាំឱ្យ $c{T(e.subs(x, x0))}={y0}$ ឬ $c={T(c)}$ ។" if x0 else f"ដោយ $y(0)={y0}$ នាំឱ្យ $c={T(c)}$ ។"); dcheck(w, y, 0, p, q, 0); w.C.append(check(str(y.subs(x, x0)), y0, "initial"))
    return row(w.say(f"{so(w)} $\\boxed{{y={T(y)}}}$ ។"), CH, "de_first_order", "steps_homogeneous_first_initial", "medium", P, f"y={T(y)}", "d_homog1")
def rhs_form(rng, order, a, p, q):
    """Choose a particular solution g with unknown form; return (g, form latex, unknown list, form expr, name)."""
    u, v, t = sp.symbols("a b d"); k = rng.choice(["const", "lin", "exp", "trig"]) if order == 2 else rng.choice(["const", "lin", "quad", "exp", "trig"]); s = rng.choice([1, 2, 3, -1, -2])
    if k == "const":
        if q == 0: return None
        g = sp.Integer(nz(rng, -7, 9)); return g, u, [u], "const"
    if k == "lin":
        if q == 0: return None
        g = nz(rng, -5, 6) * x + rng.randint(-5, 6); return g, u * x + v, [u, v], "lin"
    if k == "quad":
        if q == 0: return None
        g = nz(rng, -3, 4) * x ** 2 + rng.randint(-4, 4) * x + rng.randint(-4, 4); return g, u * x ** 2 + v * x + t, [u, v, t], "quad"
    if k == "exp":
        m = nz(rng, -4, 4); 
        if a * m * m + p * m + q == 0: return None
        return nz(rng, -5, 6) * sp.exp(m * x), u * sp.exp(m * x), [u], "exp"
    m = rng.randint(1, 4)
    if a * (-m * m) + q == 0 and p == 0: return None
    return nz(rng, -5, 5) * sp.cos(m * x) + nz(rng, -5, 5) * sp.sin(m * x), u * sp.cos(m * x) + v * sp.sin(m * x), [u, v], "trig"
def solve_form(w, a, p, q, rhs, form, un, order):
    """Print substitution of the trial form and identification of coefficients."""
    d1, d2 = sp.diff(form, x), sp.diff(form, x, 2); w.say(f"$$g'(x)={T(d1)}$$")
    if order == 2: w.say(f"$$g''(x)={T(d2)}$$")
    L = sp.expand(a * d2 + p * d1 + q * form); basis = [b for b in (x ** 2, x, sp.exp(sp.Wild("e")), sp.cos, sp.sin)]; D = sp.expand(L - rhs); sol = None
    if form.has(sp.exp):
        e = [f for f in form.atoms(sp.exp)][0]; w.say(f"ជំនួសក្នុងសមីការ ផ្ទឹមមេគុណនៃ ${T(e)}$ ៖ ${T(sp.collect(L / e, un[0]))}={T(sp.simplify(rhs / e))}$ ។"); eqs = [sp.simplify(D / e)]
    elif form.has(sp.cos):
        c_ = list(form.atoms(sp.cos))[0]; s_ = list(form.atoms(sp.sin))[0]; eqs = [D.coeff(c_), D.coeff(s_)]; w.say("ជំនួសក្នុងសមីការ ផ្ទឹមមេគុណនៃ $" + T(c_) + "$ និង $" + T(s_) + "$ ៖"); w.say("$$\\begin{cases}" + "\\\\".join(f"{T(e)}=0" for e in eqs) + "\\end{cases}$$")
    else:
        eqs = [c for c in sp.Poly(D, x).all_coeffs()]; w.say("ជំនួសក្នុងសមីការ ផ្ទឹមមេគុណតាមស្វ័យគុណនៃ $x$ ៖"); w.say("$$\\begin{cases}" + "\\\\".join(f"{T(e)}=0" for e in eqs) + "\\end{cases}$$")
    sol = sp.solve(eqs, un, dict=True)[0]; w.say("នាំឱ្យ " + " , ".join(f"${T(k)}={T(v)}$" for k, v in sol.items()) + " ។")
    return form.subs(sol)
def lhs_t(order, a, p, q): return eq2(a, p, q) if order == 2 else eq1(p, q)
def nonhom(rng, order):
    if order == 1: a, p, q = 0, rng.choice([1, 1, 2, 3, -1]), nz(rng, -6, 6)
    else: a, p, q = pick2(rng)
    t = rhs_form(rng, order, a, p, q)
    if t is None: return None
    g, form, un, kind = t; rhs = sp.expand(a * sp.diff(g, x, 2) + p * sp.diff(g, x) + q * g); w = W(rng)
    if rhs == 0: return None
    L = lhs_t(order, a, p, q); ini = rng.random() < .45; fm = T(form); r = T(rhs); parts = rng.random() < .6
    if len(r) > 60: return None
    ic = None
    if ini:
        y0 = rng.randint(-5, 6); y1 = rng.randint(-5, 6); ic = f"$y(0)={y0}$" + (f" និង $y'(0)={y1}$" if order == 2 else "")
    if parts:
        pr = f"គេមានសមីការឌីផេរ៉ង់ស្យែល $${L}={r}\\quad(E)$$\nក. ដោះស្រាយសមីការ ${L}=0\\quad(E')$ ។\nខ. រកចំនួនពិតដែលធ្វើឱ្យ $g(x)={fm}$ ជាចម្លើយពិសេសនៃ $(E)$ ។\nគ. ទាញរកចម្លើយទូទៅនៃ $(E)$ ។"
        if ini: pr += f"\nឃ. រកចម្លើយពិសេសនៃ $(E)$ ដែល {ic} ។"
    else: pr = f"ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល $${L}={r}$$" + (f"\nដោយដឹងថា {ic} ។" if ini else "") + f"\n(គេអាចរកចម្លើយពិសេសមានរាង ${fm}$ ។)"
    w.say("ក. ដោះស្រាយសមីការ $(E')$ ៖" if parts else "ដោះស្រាយសមីការអូម៉ូសែន ៖")
    if order == 2: yh = homog2(w, a, p, q, "(E')" if parts else None)
    else:
        rr = R(-q, p); w.say(f"{gb(w)} $y'={T(rr)}y$ នាំឱ្យ $y=c{T(sp.exp(rr * x))}$ ($c$ ថេរ) ។"); yh = Cc * sp.exp(rr * x)
    w.say(f"$$y_h={T(yh)}$$"); w.say("ខ. " + f"តាង $g(x)={fm}$ ។" if parts else f"រកចម្លើយពិសេស ៖ តាង $g(x)={fm}$ ។"); gg = solve_form(w, a, p, q, rhs, form, un, order)
    assert sp.simplify(gg - g) == 0; w.say(f"ដូចនេះ $g(x)={T(g)}$ ។"); y = yh + g; w.say(("គ. " if parts else "") + f"ចម្លើយទូទៅនៃសមីការគឺ $y=y_h+g$ ៖"); w.say(f"$$y={T(y)}$$"); dcheck(w, y, a, p, q, rhs)
    if not ini: return row(w.say(f"{so(w)} $\\boxed{{y={T(y)}}}$ ។"), CH, f"de_{'second' if order == 2 else 'first'}_order", f"steps_nonhomogeneous_{kind}", "bacii", pr, f"y={T(y)}", f"nonhom{order}")
    if order == 1:
        cv = sp.solve(y.subs(x, 0).subs(Cc, Cc) - y0, Cc)[0]; w.say(("ឃ. " if parts else "") + f"ដោយ $y(0)={y0}$ នាំឱ្យ $c={T(cv)}$ ។"); ys = y.subs(Cc, cv)
    else:
        e1 = sp.Eq(y.subs(x, 0), y0); e2 = sp.Eq(sp.diff(y, x).subs(x, 0), y1); s = sp.solve([e1, e2], [Ac, Bc], dict=True)[0]; w.say(("ឃ. " if parts else "") + "ប្រើលក្ខខណ្ឌដើម ៖"); w.say(f"$$\\begin{{cases}}{T(e1.lhs)}={T(y0)}\\\\{T(e2.lhs)}={T(y1)}\\end{{cases}}$$"); w.say(f"នាំឱ្យ $A={T(s[Ac])}$ និង $B={T(s[Bc])}$ ។"); ys = y.subs(s)
    dcheck(w, ys, a, p, q, rhs); w.C.append(check(str(ys.subs(x, 0)), y0, "initial"))
    if len(T(ys)) > 110: return None
    return row(w.say(f"{so(w)} $\\boxed{{y={T(ys)}}}$ ។"), CH, f"de_{'second' if order == 2 else 'first'}_order", f"steps_nonhomogeneous_{kind}_initial", "bacii", pr, f"y={T(ys)}", f"nonhom{order}")
def nonhom1(rng): return nonhom(rng, 1)
def nonhom2(rng): return nonhom(rng, 2)
def homog2_gen(rng):
    a, p, q = pick2(rng); w = W(rng); L = eq2(a, p, q); P = w.v("ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែល ៖", "ដោះស្រាយសមីការឌីផេរ៉ង់ស្យែលលីនេអែលំដាប់ ២ ៖", "រកចម្លើយទូទៅនៃសមីការ ៖") + f" $${L}=0$$"; y = homog2(w, a, p, q); dcheck(w, y, a, p, q, 0)
    return row(w.say(f"{so(w)} $\\boxed{{y={T(y)}}}$ ។"), CH, "de_second_order", "steps_characteristic", "medium", P, f"y={T(y)}", "homog2_gen")
def homog2_ini(rng):
    a, p, q = pick2(rng); y0, y1 = rng.randint(-5, 6), rng.randint(-5, 6); w = W(rng); L = eq2(a, p, q); x0 = 0
    if y0 == 0 and y1 == 0: return None
    P = f"រកចម្លើយពិសេសនៃសមីការ ${L}=0$ ដែលផ្ទៀងផ្ទាត់ $y(0)={y0}$ និង $y'(0)={y1}$ ។"; y = homog2(w, a, p, q); w.say(f"$$y={T(y)}$$"); d = sp.diff(y, x); w.say(f"$$y'={T(sp.expand(d))}$$"); e1, e2 = y.subs(x, 0), d.subs(x, 0); w.say(f"ដោយ $y(0)={y0}$ និង $y'(0)={y1}$ គេបាន ៖"); w.say(f"$$\\begin{{cases}}{T(e1)}={y0}\\\\{T(e2)}={y1}\\end{{cases}}$$"); s = sp.solve([e1 - y0, e2 - y1], [Ac, Bc], dict=True)[0]; w.say(f"នាំឱ្យ $A={T(s[Ac])}$ និង $B={T(s[Bc])}$ ។"); ys = y.subs(s); dcheck(w, ys, a, p, q, 0); w.C += [check(str(ys.subs(x, 0)), y0, "y(0)"), check(str(sp.diff(ys, x).subs(x, 0)), y1, "y'(0)")]
    return row(w.say(f"{so(w)} $\\boxed{{y={T(ys)}}}$ ។"), CH, "de_second_order", "steps_characteristic_initial", "bacii", P, f"y={T(ys)}", "homog2_ini")
def verify_sol(rng):
    a, p, q = pick2(rng); kind = "h"; A, Bv = nz(rng, -5, 5), nz(rng, -5, 5); w = W(rng); W_ = W(rng); y = homog2(W_, a, p, q).subs({Ac: A, Bc: Bv}); L = eq2(a, p, q); d1, d2 = sp.diff(y, x), sp.diff(y, x, 2)
    P = f"បង្ហាញថា អនុគមន៍ $y={T(y)}$ ជាចម្លើយនៃសមីការឌីផេរ៉ង់ស្យែល ${L}=0$ ។"; w.say(f"$$y'={T(sp.expand(d1))}$$"); w.say(f"$$y''={T(sp.expand(d2))}$$"); w.say("ជំនួសក្នុងអង្គខាងឆ្វេងនៃសមីការ ៖"); tm = [f"{cf(a)}\\left({T(sp.expand(d2))}\\right)"] + ([f"{'+' if p > 0 else '-'}{cf(abs(p))}\\left({T(sp.expand(d1))}\\right)"] if p else []) + ([f"{'+' if q > 0 else '-'}{cf(abs(q))}\\left({T(sp.expand(y))}\\right)"] if q else []); w.say("$$" + "".join(tm) + "$$"); ds = [sp.expand(e).as_coefficients_dict() for e in (d2, d1, y)]; line = []
    for ph in sorted({k for d in ds for k in d}, key=str):
        cs_ = [m * d.get(ph, 0) for m, d in zip((a, p, q), ds)]; cs_ = [c for c in cs_ if c != 0]
        if not cs_: continue
        assert sum(cs_) == 0
        line.append("\\left(" + T(cs_[0]) + "".join(("+" + T(c)) if c > 0 else T(c) for c in cs_[1:]) + "\\right)" + ("" if ph == 1 else T(ph)))
    w.say("ប្រមូលតួដូចគ្នា ៖"); w.say("$$=" + "+".join(line) + "=0$$"); dcheck(w, y, a, p, q, 0)
    return row(w.say(f"{so(w)} $y={T(y)}$ ជាចម្លើយនៃសមីការ ។"), CH, "de_second_order", "steps_verify_solution", "easy", P, "0", "verify_sol")
def from_general(rng):
    r1, r2 = rng.sample(range(-7, 8), 2); w = W(rng); p, q = -(r1 + r2), r1 * r2; y = Ac * sp.exp(r1 * x) + Bc * sp.exp(r2 * x); P = f"រកសមីការឌីផេរ៉ង់ស្យែលលីនេអែលំដាប់ ២ មេគុណថេរ ដែលមានចម្លើយទូទៅ $y={T(y)}$ ។"; w.say(f"ចម្លើយទូទៅបង្ហាញថា សមីការសម្គាល់មានឫស $\\lambda_1={r1}$ និង $\\lambda_2={r2}$ ។"); w.say(f"សមីការសម្គាល់ ៖ $$\\left({T(sp.Symbol('lambda') - r1)}\\right)\\left({T(sp.Symbol('lambda') - r2)}\\right)=0$$"); w.say(f"$$ {lam2(1, p, q)}=0$$"); dcheck(w, y, 1, p, q, 0)
    return row(w.say(f"{so(w)} $\\boxed{{{eq2(1, p, q)}=0}}$ ។"), CH, "de_second_order", "steps_equation_from_solution", "medium", P, f"{eq2(1, p, q)}=0", "from_general")
def sep(rng):
    kind = rng.choice(["xy", "yy", "ey", "yx", "y2"]); k = rng.randint(1, 12); w = W(rng); m = rng.randint(1, 9); y0 = rng.randint(1, 9)
    if kind == "xy":
        f = k * x ** rng.choice([1, 1, 2]) ; Fp = sp.integrate(f, x); y = y0 * sp.exp(Fp); P = f"ដោះស្រាយសមីការ $y'={T(f)}y$ ដែល $y(0)={y0}$ ។"; w.say(f"{gb(w)} $\\frac{{dy}}{{y}}={T(f)}\\,dx$ ។"); w.say(f"$$\\ln|y|={T(Fp)}+k$$"); w.say(f"$$y=c{T(sp.exp(Fp))}$$ (យក $c=\\pm e^k$)"); w.say(f"ដោយ $y(0)={y0}$ នាំឱ្យ $c={y0}$ ។"); res = sp.diff(y, x) - f * y
    elif kind == "yy":
        c2 = y0 ** 2; f = k * x + m; Fp = sp.integrate(f, x); y = sp.sqrt(2 * Fp + c2); P = f"ដោះស្រាយសមីការ $yy'={T(f)}$ ដែល $y(0)={y0}$ និង $y>0$ ។"; w.say(f"{gb(w)} $y\\,dy=\\left({T(f)}\\right)dx$ ។"); w.say(f"$$\\frac{{y^2}}{{2}}={T(Fp)}+c$$"); w.say(f"ដោយ $y(0)={y0}$ នាំឱ្យ $c={T(R(c2, 2))}$ ។"); w.say(f"$$y^2={T(sp.expand(2 * Fp + c2))}$$"); res = y * sp.diff(y, x) - f
    elif kind == "ey":
        f = rng.choice([sp.exp(x), 2 * x, sp.cos(x), 3 * x ** 2]) * k; Fp = sp.integrate(f, x); c = 1 - Fp.subs(x, 0); y = sp.log(Fp + c); P = f"ដោះស្រាយសមីការ $e^{{y}}y'={T(f)}$ ដែល $y(0)=0$ ។"; w.say(f"{gb(w)} $e^y\\,dy={B(f)}\\,dx$ ។"); w.say(f"$$e^y={T(Fp)}+c$$"); w.say(f"ដោយ $y(0)=0$ នាំឱ្យ $1={T(Fp.subs(x, 0))}+c$ ឬ $c={T(c)}$ ។"); res = sp.exp(y) * sp.diff(y, x) - f
    elif kind == "yx":
        n = rng.choice([1, 2, 3, -1, -2]); y = y0 * x ** n; P = f"ដោះស្រាយសមីការ $xy'={cf(n)}y$ លើ $(0;+\\infty)$ ដែល $y(1)={y0}$ ។"; w.say(f"{gb(w)} $\\frac{{dy}}{{y}}={T(n)}\\frac{{dx}}{{x}}$ ។".replace("=1\\frac", "=\\frac").replace("=-1\\frac", "=-\\frac")); w.say(f"$$\\ln|y|={cf(n)}\\ln x+k$$"); w.say(f"$$y={T(Cc * x ** n)}$$ (យក $c=\\pm e^k$)"); w.say(f"ដោយ $y(1)={y0}$ នាំឱ្យ $c={y0}$ ។"); res = x * sp.diff(y, x) - n * y
    else:
        y = 1 / (k * x + R(1, y0)); P = f"ដោះស្រាយសមីការ $y'={T(-k)}y^2$ ដែល $y(0)={y0}$ ។"; w.say(f"{gb(w)} $\\frac{{dy}}{{y^2}}={T(-k)}\\,dx$ ។"); w.say(f"$$-\\frac{{1}}{{y}}={T(-k * x)}+c$$"); w.say(f"ដោយ $y(0)={y0}$ នាំឱ្យ $c={T(R(-1, y0))}$ ។"); res = sp.diff(y, x) + k * y ** 2
    assert sp.simplify(res) == 0
    w.C.append(check(str(res), 0, "residual"))
    return row(w.say(f"{so(w)} $\\boxed{{y={T(y)}}}$ ។"), CH, "de_first_order", f"steps_separable_{kind}", "medium", P, f"y={T(y)}", "sep")
PEOPLE = [("ចំនួនបាក់តេរី", "ម៉ោង"), ("ចំនួនប្រជាជនក្នុងក្រុងមួយ", "ឆ្នាំ"), ("ចំនួនត្រីក្នុងស្រះមួយ", "ខែ"), ("ចំនួនកោសិកា", "ថ្ងៃ")]
def growth(rng):
    who, un = rng.choice(PEOPLE); N0 = rng.choice([100, 200, 300, 500, 800, 1000, 2000, 5000]); m = rng.choice([2, 3, 4, 5]); t1 = rng.randint(1, 8); t2 = t1 * rng.choice([2, 3]); w = W(rng); k = sp.log(m) / t1; v = N0 * m ** (t2 // t1)
    P = f"{who}កើនឡើងតាមសមីការ $N'(t)=kN(t)$ ដែល $t$ គិតជា{un} ។ នៅពេល $t=0$ គេមាន $N={N0}$ ហើយនៅពេល $t={t1}$ គេមាន $N={N0 * m}$ ។\nក. រក $N(t)$ ។\nខ. គណនា $N({t2})$ ។"
    w.say(f"ក. ចម្លើយទូទៅនៃ $N'=kN$ គឺ $N(t)=ce^{{kt}}$ ។ ដោយ $N(0)={N0}$ នាំឱ្យ $c={N0}$ ។"); w.say(f"ដោយ $N({t1})={N0 * m}$ គេបាន ${N0}e^{{{t1}k}}={N0 * m}$ ឬ $e^{{{t1}k}}={m}$ នាំឱ្យ $k=\\frac{{\\ln {m}}}{{{t1}}}$ ។".replace("{1}k", "k")); w.say(f"$$N(t)={N0}e^{{\\frac{{\\ln {m}}}{{{t1}}}t}}={N0}\\cdot {m}^{{\\frac{{t}}{{{t1}}}}}$$"); w.say(f"ខ. $$N({t2})={N0}\\cdot {m}^{{{t2 // t1}}}={v}$$"); w.C.append(check(f"{N0}*exp(log({m})/{t1}*{t2})", v, "N"))
    return row(w.say(f"{so(w)} $\\boxed{{N(t)={N0}\\cdot {m}^{{\\frac{{t}}{{{t1}}}}}}}$ និង $\\boxed{{N({t2})={v}}}$ ។"), CH, "de_first_order", "steps_growth_word", "medium", P, str(v), "growth")
def decay(rng):
    H = rng.choice([2, 3, 4, 5, 6, 8, 10, 12]); M0 = rng.choice([40, 80, 100, 160, 200, 320, 400]); n = rng.choice([2, 3, 4]); w = W(rng); t2 = H * n; v = R(M0, 2 ** n); P = f"សារធាតុមួយរលាយតាមសមីការ $m'(t)=-km(t)$ ដោយ $k>0$ ។ ម៉ាសដើមគឺ ${M0}$ ក្រាម ហើយក្រោយ ${H}$ ឆ្នាំ ម៉ាសនៅសល់ពាក់កណ្តាល ។ រកម៉ាសនៅសល់ក្រោយ ${t2}$ ឆ្នាំ ។"
    w.say(f"ចម្លើយទូទៅ ៖ $m(t)=ce^{{-kt}}$ ។ ដោយ $m(0)={M0}$ នាំឱ្យ $c={M0}$ ។"); w.say(f"ដោយ $m({H})={R(M0, 2)}$ គេបាន $e^{{-{H}k}}=\\frac{{1}}{{2}}$ នាំឱ្យ $k=\\frac{{\\ln 2}}{{{H}}}$ ។"); w.say(f"$$m({t2})={M0}e^{{-\\frac{{\\ln 2}}{{{H}}}\\cdot {t2}}}={M0}\\cdot 2^{{-{n}}}={T(v)}$$"); w.C.append(check(f"{M0}*exp(-log(2)/{H}*{t2})", v, "m"))
    return row(w.say(f"{so(w)} ម៉ាសនៅសល់ស្មើ $\\boxed{{{T(v)}}}$ ក្រាម ។"), CH, "de_first_order", "steps_decay_word", "medium", P, T(v), "decay")
def cooling(rng):
    Ta = rng.choice([20, 25, 30]); d0 = rng.choice([60, 70, 80]); r = rng.choice([2]); t1 = rng.choice([5, 10, 15, 20]); n = rng.choice([2, 3]); w = W(rng); T0 = Ta + d0; T1 = Ta + R(d0, 2); v = Ta + R(d0, 2 ** n); P = f"ទឹកក្តៅមួយកែវមានសីតុណ្ហភាព ${T0}$ ដឺក្រេ ក្នុងបន្ទប់ ${Ta}$ ដឺក្រេ ។ សីតុណ្ហភាពផ្ទៀងផ្ទាត់សមីការ $T'(t)=-k\\left(T(t)-{Ta}\\right)$ ដែល $k>0$ ។ ក្រោយ ${t1}$ នាទី សីតុណ្ហភាពនៅសល់ ${T(T1)}$ ដឺក្រេ ។ រក $T({t1 * n})$ ។"
    w.say(f"តាង $u=T-{Ta}$ គេបាន $u'=-ku$ នាំឱ្យ $u=ce^{{-kt}}$ ។"); w.say(f"ដោយ $u(0)={d0}$ នាំឱ្យ $c={d0}$ ។"); w.say(f"ដោយ $u({t1})={T(R(d0, 2))}$ គេបាន $e^{{-{t1}k}}=\\frac{{1}}{{2}}$ ។"); w.say(f"$$T({t1 * n})={Ta}+{d0}\\left(e^{{-{t1}k}}\\right)^{{{n}}}={Ta}+\\frac{{{d0}}}{{{2 ** n}}}={Ta}+{T(R(d0, 2 ** n))}={T(v)}$$"); w.C.append(check(f"{Ta}+{d0}*exp(-log(2)/{t1}*{t1 * n})", v, "T"))
    return row(w.say(f"{so(w)} $\\boxed{{T({t1 * n})={T(v)}}}$ ដឺក្រេ ។"), CH, "de_first_order", "steps_cooling_word", "medium", P, T(v), "cooling")
ALL = [(d_direct, 500), (d_homog1, 450), (nonhom1, 900), (homog2_gen, 900), (homog2_ini, 900), (nonhom2, 1500), (verify_sol, 300), (from_general, 150), (sep, 500), (growth, 150), (decay, 120), (cooling, 40)]
