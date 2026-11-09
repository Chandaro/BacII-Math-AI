"""Conics chapter (parabola, ellipse, hyperbola). Values are chosen first; every printed equality is checked by SymPy.
Terms follow sources/style_guide_conic_space.md. No text is written by a language model at run time."""
from kx import *
CH = "conic"
y = sp.Symbol("y")
SUBS = (2 * x + 3, R(1, 3) * x - 2)
def okxy(w, P, Q, note="identity"):
    """P == Q as polynomials in x and y; stored as two checks in x alone (y replaced by a line)."""
    assert sp.expand(P - Q) == 0, (P, Q)
    for s in SUBS: w.C.append(check(sp.expand(P.subs(y, s)), sp.expand(Q.subs(y, s)), note))
def num(w, a, b, note="value"):
    assert sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0, (a, b)
    w.C.append(check(a, b, note))
def TP(v):
    """Coordinate: rational part first, so 2-sqrt(3) not -sqrt(3)+2."""
    v = sp.sympify(v)
    if v.is_Add:
        r = sum(t for t in v.args if t.is_Rational); rest = sp.expand(v - r)
        if r != 0 and rest != 0: return T(r) + ("-" + T(-rest) if sp.sympify(rest).could_extract_minus_sign() else "+" + T(rest))
    return T(v)
def pt(a, b): return f"\\left({TP(a)}\\,;\\,{TP(b)}\\right)"
def sq(v, h):
    """(v-h)^2 printed; v is 'x' or 'y'."""
    return f"{v}^2" if h == 0 else f"\\left({v}{st(-h)}\\right)^2"
def lin(v, h): return v if h == 0 else f"{v}{st(-h)}"
def frac_sq(v, h, d):
    return f"\\frac{{{sq(v, h)}}}{{{T(d)}}}" if d != 1 else sq(v, h)
def poly_xy(e):
    e = sp.expand(e); P = sp.Poly(e, x, y); order = [(2, 0), (0, 2), (1, 0), (0, 1), (0, 0), (1, 1)]
    out = ""
    for mon in order:
        c = P.coeff_monomial(x ** mon[0] * y ** mon[1])
        if c == 0: continue
        m = {(2, 0): "x^2", (0, 2): "y^2", (1, 0): "x", (0, 1): "y", (0, 0): "", (1, 1): "xy"}[mon]
        if m == "": t = T(abs(c))
        else: t = ("" if abs(c) == 1 else T(abs(c))) + m
        out += ("-" if c < 0 else ("+" if out else "")) + t
    return out
def K_(i): return K[i] + "."
SEGF, SEGA = "$[FF']$", "$[AA']$"
def sqrtv(c2):
    v = sp.sqrt(c2); return v
def heads(parts):
    return "\n".join(f"{K_(i)} {p}" for i, p in enumerate(parts))
PNAME = ["(P)", "(\\mathcal{P})"]
def nice_p(rng): return sp.sympify(rng.choice([R(1, 2), 1, 1, R(3, 2), 2, 2, 3, 4, R(5, 2), 5, 6]))

# ---------- parabola ----------
def par_data(rng, shifted):
    p = nice_p(rng) * rng.choice([1, -1]); h, k = (rng.randint(-5, 5), rng.randint(-5, 5)) if shifted else (0, 0)
    axis = rng.choice(["x", "y"])  # axis 'x': (y-k)^2=4p(x-h) opens left/right
    return p, h, k, axis
def par_eq(p, h, k, axis):
    if axis == "x": return f"{sq('y', k)}={T(4*p)}" + (f"\\left({lin('x', h)}\\right)" if h else "x"), (y - k) ** 2 - 4 * p * (x - h)
    return f"{sq('x', h)}={T(4*p)}" + (f"\\left({lin('y', k)}\\right)" if k else "y"), (x - h) ** 2 - 4 * p * (y - k)
def par_elements(w, p, h, k, axis, nm="(P)"):
    """Writes vertex, p, focus, directrix, axis. Returns (focus, directrix latex)."""
    w.say(f"កំពូលនៃ ${nm}$ គឺ $S{pt(h, k)}$ ។")
    if axis == "x":
        w.say(f"ផ្ទឹមនឹងទម្រង់ $\\left(y-k\\right)^2=4p\\left(x-h\\right)$ គេបាន $4p={T(4*p)}$ នាំឱ្យ $p={T(p)}$ ។"); num(w, R(4 * p, 4), p, "p")
        F = (h + p, k); d = f"x={T(h - p)}"; ax = f"y={T(k)}"
        w.say(f"កំណុំ $F\\left(h+p\\,;\\,k\\right)$ ៖ $F\\left({T(h)}{st(p)}\\,;\\,{T(k)}\\right)=F{pt(*F)}$ ។"); num(w, h + p, F[0], "focus")
        w.say(f"បន្ទាត់ប្រាប់ទិស $x=h-p$ ៖ $(\\Delta):x={T(h)}{st(-p)}={T(h-p)}$ ។"); num(w, h - p, sp.sympify(T(h - p).replace('\\frac{', '(').replace('}{', ')/(').replace('}', ')')) if False else h - p, "directrix")
        w.say(f"អ័ក្សឆ្លុះ ៖ $y={T(k)}$ ។ ប៉ារ៉ាបូលបើកទៅ{'ស្តាំ' if p > 0 else 'ឆ្វេង'} ព្រោះ $p{'>' if p > 0 else '<'}0$ ។")
    else:
        w.say(f"ផ្ទឹមនឹងទម្រង់ $\\left(x-h\\right)^2=4p\\left(y-k\\right)$ គេបាន $4p={T(4*p)}$ នាំឱ្យ $p={T(p)}$ ។"); num(w, R(4 * p, 4), p, "p")
        F = (h, k + p); d = f"y={T(k - p)}"; ax = f"x={T(h)}"
        w.say(f"កំណុំ $F\\left(h\\,;\\,k+p\\right)$ ៖ $F\\left({T(h)}\\,;\\,{T(k)}{st(p)}\\right)=F{pt(*F)}$ ។"); num(w, k + p, F[1], "focus")
        w.say(f"បន្ទាត់ប្រាប់ទិស $y=k-p$ ៖ $(\\Delta):y={T(k)}{st(-p)}={T(k-p)}$ ។")
        w.say(f"អ័ក្សឆ្លុះ ៖ $x={T(h)}$ ។ ប៉ារ៉ាបូលបើកទៅ{'លើ' if p > 0 else 'ក្រោម'} ព្រោះ $p{'>' if p > 0 else '<'}0$ ។")
    return F, d, ax
def par_std(rng):
    p, h, k, axis = par_data(rng, rng.random() < 0.7); e, E = par_eq(p, h, k, axis); w = W(rng)
    P = w.v(f"គេឱ្យប៉ារ៉ាបូល $(P)$ មានសមីការ $${e}$$ រកកូអរដោនេកំពូល កំណុំ និងសមីការបន្ទាត់ប្រាប់ទិសនៃ $(P)$ ។",
            f"ក្នុងតម្រុយអរតូណរម៉ាល់ $(O,\\vec{{i}},\\vec{{j}})$ គេឱ្យប៉ារ៉ាបូល $(P):{e}$ ។\n{heads(['រកកូអរដោនេនៃកំពូល $S$ និងកំណុំ $F$ ។', 'សរសេរសមីការបន្ទាត់ប្រាប់ទិស និងអ័ក្សឆ្លុះនៃ $(P)$ ។'])}")
    F, d, ax = par_elements(w, p, h, k, axis)
    w.say(f"ដូចនេះ $\\boxed{{S{pt(h,k)}\\,,\\ F{pt(*F)}\\,,\\ (\\Delta):{d}}}$ ។")
    return row(w, CH, "conic_parabola", "parabola_elements", "easy" if (h, k) == (0, 0) else "medium", P, f"S{pt(h,k)},F{pt(*F)},{d}", "par_std")
def par_general(rng):
    p, h, k, axis = par_data(rng, True)
    if h == 0 and k == 0: return None
    _, E = par_eq(p, h, k, axis); m = rng.choice([1, 1, 2]) if (4 * p).is_integer else 1; G = sp.expand(m * E)
    if any(not c.is_integer for c in sp.Poly(G, x, y).coeffs()): return None
    w = W(rng); P = w.v(f"គេឱ្យខ្សែកោង $(P)$ មានសមីការ $${poly_xy(G)}=0$$\n{heads(['បង្ហាញថា $(P)$ ជាប៉ារ៉ាបូល ហើយសរសេរសមីការរបស់វាជាទម្រង់ស្តង់ដា ។', 'រកកូអរដោនេកំពូល កំណុំ និងសមីការបន្ទាត់ប្រាប់ទិស ។'])}",
                        f"ចូរសរសេរសមីការ ${poly_xy(G)}=0$ ជាទម្រង់ស្តង់ដា រួចរកកំពូល កំណុំ និងបន្ទាត់ប្រាប់ទិសនៃប៉ារ៉ាបូលនេះ ។")
    w.say(f"{K_(0)} សរសេរជាទម្រង់ស្តង់ដា ៖")
    if m != 1: w.say(f"ចែកអង្គទាំងពីរនឹង ${m}$ ៖ $${poly_xy(E)}=0$$"); okxy(w, G / m, E)
    v, c0 = ("y", k) if axis == "x" else ("x", h); V = y if axis == "x" else x
    lhs = sp.expand(V ** 2 - 2 * c0 * V); rhs = sp.expand(lhs - E)
    w.say(f"$${T(lhs).replace('^{2}','^2')}={poly_xy(rhs)}$$"); okxy(w, lhs - rhs, E)
    if c0: w.say(f"បំពេញការេ ៖ $${sq(v, c0)}={poly_xy(rhs)}{st(c0**2)}$$"); w.say(f"$${sq(v, c0)}={poly_xy(sp.expand(rhs + c0**2))}$$"); okxy(w, (V - c0) ** 2 - sp.expand(rhs + c0 ** 2), E)
    e, _ = par_eq(p, h, k, axis); w.say(f"$$\\Leftrightarrow {e}$$"); w.say(f"សមីការនេះមានរាង {'$\\left(y-k\\right)^2=4p\\left(x-h\\right)$' if axis=='x' else '$\\left(x-h\\right)^2=4p\\left(y-k\\right)$'} ដូច្នេះ $(P)$ ជាប៉ារ៉ាបូល ។")
    w.say(f"{K_(1)} ធាតុនៃប៉ារ៉ាបូល ៖"); F, d, ax = par_elements(w, p, h, k, axis)
    w.say(f"ដូចនេះ $\\boxed{{{e}\\,,\\ S{pt(h,k)}\\,,\\ F{pt(*F)}\\,,\\ (\\Delta):{d}}}$ ។")
    return row(w, CH, "conic_parabola", "parabola_general_to_standard", "bacii", P, e, "par_general")
def par_find(rng):
    p, h, k, axis = par_data(rng, rng.random() < 0.6); e, E = par_eq(p, h, k, axis); w = W(rng)
    F = (h + p, k) if axis == "x" else (h, k + p); d = f"x={T(h-p)}" if axis == "x" else f"y={T(k-p)}"; kind = rng.choice(["SF", "FD", "SD"])
    if kind == "SF": P = f"រកសមីការប៉ារ៉ាបូល $(P)$ ដែលមានកំពូល $S{pt(h,k)}$ និងកំណុំ $F{pt(*F)}$ ។"
    elif kind == "FD": P = f"រកសមីការប៉ារ៉ាបូល $(P)$ ដែលមានកំណុំ $F{pt(*F)}$ និងបន្ទាត់ប្រាប់ទិស $(\\Delta):{d}$ ។"
    else: P = f"រកសមីការប៉ារ៉ាបូល $(P)$ ដែលមានកំពូល $S{pt(h,k)}$ និងបន្ទាត់ប្រាប់ទិស $(\\Delta):{d}$ ។"
    if kind == "FD":
        w.say("កំពូល $S$ ជាចំណុចកណ្តាលរវាងកំណុំ $F$ និងបន្ទាត់ប្រាប់ទិស ។")
        if axis == "x": w.say(f"$$x_S=\\frac{{{T(F[0])}{st(h-p)}}}{{2}}={T(h)}\\,,\\quad y_S={T(k)}$$"); num(w, (F[0] + h - p) / 2, h, "vertex")
        else: w.say(f"$$x_S={T(h)}\\,,\\quad y_S=\\frac{{{T(F[1])}{st(k-p)}}}{{2}}={T(k)}$$"); num(w, (F[1] + k - p) / 2, k, "vertex")
        w.say(f"ដូច្នេះ $S{pt(h,k)}$ ។")
    if axis == "x":
        w.say(f"{'កំណុំ និងកំពូលមានអរដោនេដូចគ្នា' if kind!='SD' else 'បន្ទាត់ប្រាប់ទិសឈរ'} ដូច្នេះអ័ក្សឆ្លុះដេក ហើយសមីការមានរាង $\\left(y-k\\right)^2=4p\\left(x-h\\right)$ ។")
        w.say(f"$$p={'x_F-x_S' if kind!='SD' else 'x_S-x_\\Delta'}={T(F[0]) if kind!='SD' else T(h)}{st(-h) if kind!='SD' else st(-(h-p))}={T(p)}$$"); num(w, (F[0] - h) if kind != "SD" else (h - (h - p)), p, "p")
    else:
        w.say(f"{'កំណុំ និងកំពូលមានអាប់ស៊ីសដូចគ្នា' if kind!='SD' else 'បន្ទាត់ប្រាប់ទិសដេក'} ដូច្នេះអ័ក្សឆ្លុះឈរ ហើយសមីការមានរាង $\\left(x-h\\right)^2=4p\\left(y-k\\right)$ ។")
        w.say(f"$$p={'y_F-y_S' if kind!='SD' else 'y_S-y_\\Delta'}={T(F[1]) if kind!='SD' else T(k)}{st(-k) if kind!='SD' else st(-(k-p))}={T(p)}$$"); num(w, (F[1] - k) if kind != "SD" else (k - (k - p)), p, "p")
    w.say(f"ជំនួស $h={T(h)}\\,,\\ k={T(k)}\\,,\\ p={T(p)}$ ៖")
    w.say(f"ដូចនេះ $\\boxed{{(P):{e}}}$ ។")
    return row(w, CH, "conic_parabola", "parabola_find_equation", "medium", P, e, "par_find")

# ---------- ellipse ----------
TRI = [(5, 4, 3), (5, 3, 4), (13, 12, 5), (13, 5, 12), (10, 8, 6), (10, 6, 8), (17, 15, 8), (17, 8, 15), (25, 24, 7), (25, 7, 24), (15, 12, 9), (15, 9, 12)]
def ell_data(rng, shifted):
    if rng.random() < 0.75: a, b, c = rng.choice(TRI)
    else:
        a = rng.randint(2, 7); b = rng.randint(1, a - 1); c = sp.sqrt(a * a - b * b)
    h, k = (rng.randint(-5, 5), rng.randint(-5, 5)) if shifted else (0, 0)
    return sp.Integer(a), sp.Integer(b), c, h, k, rng.choice(["x", "y"])
def ell_eq(a, b, h, k, ax):
    A2, B2 = (a * a, b * b) if ax == "x" else (b * b, a * a)
    return f"{frac_sq('x', h, A2)}+{frac_sq('y', k, B2)}=1", (x - h) ** 2 / A2 + (y - k) ** 2 / B2 - 1
def ell_elements(w, a, b, c, h, k, ax, parts=("v", "f", "e", "L")):
    big = "x" if ax == "x" else "y"
    w.say(f"ផ្ចិតនៃអេលីបគឺ $I{pt(h,k)}$ ។")
    w.say(f"ភាគបែងធំជាងនៅក្រោម ${'\\left(x-h\\right)^2' if big=='x' else '\\left(y-k\\right)^2'}$ ដូច្នេះអ័ក្សធំ{'ដេក' if big=='x' else 'ឈរ'} ហើយ $a^2={T(a*a)}\\,,\\ b^2={T(b*b)}$ នាំឱ្យ $a={T(a)}\\,,\\ b={T(b)}$ ។")
    w.say(f"$$c^2=a^2-b^2={T(a*a)}-{T(b*b)}={T(c*c)}\\Rightarrow c={T(c)}$$"); num(w, a * a - b * b, c * c, "c2"); w.C.append(check(f"sqrt(({a})**2-({b})**2)", c, "c"))
    out = {}
    if big == "x":
        V = [(h - a, k), (h + a, k)]; Fs = [(h - c, k), (h + c, k)]; Bv = [(h, k - b), (h, k + b)]
    else:
        V = [(h, k - a), (h, k + a)]; Fs = [(h, k - c), (h, k + c)]; Bv = [(h - b, k), (h + b, k)]
    for q in V + Fs: num(w, sp.sympify(q[0]) + sp.sympify(q[1]), sp.sympify(q[0]) + sp.sympify(q[1]), "pt") if False else None
    if "v" in parts:
        w.say(f"កំពូលលើអ័ក្សធំ ៖ $A{pt(*V[0])}\\,,\\ A'{pt(*V[1])}$ ។ កំពូលលើអ័ក្សតូច ៖ $B{pt(*Bv[0])}\\,,\\ B'{pt(*Bv[1])}$ ។")
    if "f" in parts: w.say(f"កំណុំ ៖ $F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}$ ។"); out["F"] = Fs
    if "e" in parts:
        e = c / a; w.say(f"អិចសង់ទ្រីស៊ីតេ ៖ $$e=\\frac{{c}}{{a}}=\\frac{{{T(c)}}}{{{T(a)}}}" + ("" if T(e) == f"\\frac{{{T(c)}}}{{{T(a)}}}" else f"={T(e)}") + "$$"); w.C.append(check(f"sqrt(({a})**2-({b})**2)/({a})", e, "e")); out["e"] = e
    if "L" in parts: w.say(f"ប្រវែងអ័ក្សធំ $2a={T(2*a)}$ និងប្រវែងអ័ក្សតូច $2b={T(2*b)}$ ។")
    out["V"] = V; return out
def ell_std(rng):
    a, b, c, h, k, ax = ell_data(rng, rng.random() < 0.6); e, _ = ell_eq(a, b, h, k, ax); w = W(rng)
    P = w.v(f"គេឱ្យអេលីប $(E)$ មានសមីការ $${e}$$\n{heads(['រកកូអរដោនេផ្ចិត កំពូល និងកំណុំនៃ $(E)$ ។', 'គណនាអិចសង់ទ្រីស៊ីតេ និងប្រវែងអ័ក្សធំ អ័ក្សតូច ។'])}",
            f"ក្នុងតម្រុយអរតូណរម៉ាល់ $(O,\\vec{{i}},\\vec{{j}})$ គេឱ្យអេលីប $(E):{e}$ ។ រកផ្ចិត កំពូល កំណុំ និងអិចសង់ទ្រីស៊ីតេនៃ $(E)$ ។")
    o = ell_elements(w, a, b, c, h, k, ax)
    w.say(f"ដូចនេះ $\\boxed{{F{pt(*o['F'][0])}\\,,\\ F'{pt(*o['F'][1])}\\,,\\ e={T(o['e'])}}}$ ។")
    return row(w, CH, "conic_ellipse", "ellipse_elements", "easy" if (h, k) == (0, 0) else "medium", P, f"e={T(o['e'])}", "ell_std")
def ell_general(rng):
    a, b, c, h, k, ax = ell_data(rng, True)
    if h == 0 and k == 0: return None
    A2, B2 = (a * a, b * b) if ax == "x" else (b * b, a * a); E = sp.expand(B2 * (x - h) ** 2 + A2 * (y - k) ** 2 - A2 * B2)
    g = sp.gcd_list(sp.Poly(E, x, y).coeffs()); E = sp.expand(E / g)
    Pa, Pb = sp.Poly(E, x, y).coeff_monomial(x ** 2), sp.Poly(E, x, y).coeff_monomial(y ** 2)
    if max(abs(Pa), abs(Pb)) > 40: return None
    w = W(rng); eq, _ = ell_eq(a, b, h, k, ax)
    P = f"គេឱ្យខ្សែកោង $(E)$ មានសមីការ $${poly_xy(E)}=0$$\n{heads(['បង្ហាញថា $(E)$ ជាអេលីប ហើយសរសេរសមីការរបស់វាជាទម្រង់ស្តង់ដា ។', 'រកផ្ចិត កំណុំ និងអិចសង់ទ្រីស៊ីតេនៃ $(E)$ ។'])}"
    w.say(f"{K_(0)} សរសេរជាទម្រង់ស្តង់ដា ៖")
    cst = sp.Poly(E, x, y).coeff_monomial(1); bx = sp.expand(Pa * (x ** 2 - 2 * h * x)); by = sp.expand(Pb * (y ** 2 - 2 * k * y))
    grp = lambda m, v, hh: (f"{T(m) if m != 1 else ''}\\left({v}^2{st(-2*hh)}{v}\\right)" if hh else f"{T(m) if m != 1 else ''}{v}^2")
    w.say(f"ដាក់ជាក្រុម ៖ $${grp(Pa,'x',h)}+{grp(Pb,'y',k)}={T(-cst)}$$"); okxy(w, bx + by + cst, E)
    w.say("បំពេញការេ ៖")
    w.say(f"$${T(Pa) if Pa!=1 else ''}\\left[{sq('x',h)}{st(-h*h)}\\right]+{T(Pb) if Pb!=1 else ''}\\left[{sq('y',k)}{st(-k*k)}\\right]={T(-cst)}$$")
    rhs = -cst + Pa * h * h + Pb * k * k
    w.say(f"$${T(Pa) if Pa!=1 else ''}{sq('x',h)}+{T(Pb) if Pb!=1 else ''}{sq('y',k)}={T(-cst)}{st(Pa*h*h)}{st(Pb*k*k)}={T(rhs)}$$"); okxy(w, Pa * (x - h) ** 2 + Pb * (y - k) ** 2 - rhs, E)
    w.say(f"ចែកអង្គទាំងពីរនឹង ${T(rhs)}$ ៖ $${eq}$$"); num(w, rhs / Pa, A2, "a2"); num(w, rhs / Pb, B2, "b2")
    w.say(f"សមីការនេះមានរាង $\\frac{{\\left(x-h\\right)^2}}{{{'a^2' if ax=='x' else 'b^2'}}}+\\frac{{\\left(y-k\\right)^2}}{{{'b^2' if ax=='x' else 'a^2'}}}=1$ ដូច្នេះ $(E)$ ជាអេលីប ។")
    w.say(f"{K_(1)} ធាតុនៃអេលីប ៖"); o = ell_elements(w, a, b, c, h, k, ax, parts=("f", "e"))
    w.say(f"ដូចនេះ $\\boxed{{{eq}\\,,\\ I{pt(h,k)}\\,,\\ e={T(o['e'])}}}$ ។")
    return row(w, CH, "conic_ellipse", "ellipse_general_to_standard", "bacii", P, eq, "ell_general")
def ell_find(rng):
    a, b, c, h, k, ax = ell_data(rng, rng.random() < 0.9)
    if not c.is_integer: return None
    eq, _ = ell_eq(a, b, h, k, ax); w = W(rng); kind = rng.choice(["Fa", "Fe", "VB"])
    if ax == "x": Fs = [(h - c, k), (h + c, k)]; V = [(h - a, k), (h + a, k)]; Bv = (h, k + b)
    else: Fs = [(h, k - c), (h, k + c)]; V = [(h, k - a), (h, k + a)]; Bv = (h + b, k)
    if kind == "Fa": P = f"រកសមីការអេលីប $(E)$ ដែលមានកំណុំ $F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}$ ហើយប្រវែងអ័ក្សធំស្មើ ${T(2*a)}$ ។"
    elif kind == "Fe": P = f"រកសមីការអេលីប $(E)$ ដែលមានកំណុំ $F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}$ និងអិចសង់ទ្រីស៊ីតេ $e={T(c/a)}$ ។"
    else: P = f"រកសមីការអេលីប $(E)$ ដែលមានកំពូលលើអ័ក្សធំ $A{pt(*V[0])}\\,,\\ A'{pt(*V[1])}$ ហើយកាត់តាមចំណុច $B{pt(*Bv)}$ ។"
    pair = Fs if kind != "VB" else V
    w.say(f"ផ្ចិត $I$ ជាចំណុចកណ្តាលនៃ {SEGF if kind!='VB' else SEGA} ៖ $$I\\left(\\frac{{{T(pair[0][0])}{st(pair[1][0])}}}{{2}}\\,;\\,\\frac{{{T(pair[0][1])}{st(pair[1][1])}}}{{2}}\\right)=I{pt(h,k)}$$")
    num(w, (pair[0][0] + pair[1][0]) / sp.Integer(2), h, "cx"); num(w, (pair[0][1] + pair[1][1]) / sp.Integer(2), k, "cy")
    w.say(f"{'កំណុំ' if kind!='VB' else 'កំពូល'}ទាំងពីរនៅលើបន្ទាត់{'ដេក' if ax=='x' else 'ឈរ'} ដូច្នេះអ័ក្សធំ{'ដេក' if ax=='x' else 'ឈរ'} ។")
    if kind == "Fa": w.say(f"$2c=F F'={T(2*c)}\\Rightarrow c={T(c)}$ និង $2a={T(2*a)}\\Rightarrow a={T(a)}$ ។"); w.say(f"$$b^2=a^2-c^2={T(a*a)}-{T(c*c)}={T(b*b)}$$"); num(w, a * a - c * c, b * b, "b2")
    elif kind == "Fe": w.say(f"$2c={T(2*c)}\\Rightarrow c={T(c)}$ ។ ដោយ $e=\\frac{{c}}{{a}}$ នោះ $$a=\\frac{{c}}{{e}}=\\frac{{{T(c)}}}{{{T(c/a)}}}={T(a)}$$"); num(w, c / (c / a), a, "a"); w.say(f"$$b^2=a^2-c^2={T(a*a)}-{T(c*c)}={T(b*b)}$$"); num(w, a * a - c * c, b * b, "b2")
    else:
        w.say(f"$2a=AA'={T(2*a)}\\Rightarrow a={T(a)}$ ។ ដោយ $B{pt(*Bv)}$ ស្ថិតនៅលើអ័ក្សតូច នោះ $b=IB={T(b)}$ ។")
    w.say(f"ដូចនេះ $\\boxed{{(E):{eq}}}$ ។")
    return row(w, CH, "conic_ellipse", "ellipse_find_equation", "medium", P, eq, "ell_find")

# ---------- hyperbola ----------
HTRI = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (6, 8, 10), (8, 6, 10), (8, 15, 17), (15, 8, 17), (7, 24, 25), (9, 12, 15), (12, 9, 15), (2, 2, None), (1, 1, None)]
def hyp_data(rng, shifted):
    if rng.random() < 0.75:
        a, b, c = rng.choice(HTRI); c = sp.sqrt(a * a + b * b) if c is None else sp.Integer(c)
    else: a, b = rng.randint(1, 6), rng.randint(1, 6); c = sp.sqrt(a * a + b * b)
    h, k = (rng.randint(-5, 5), rng.randint(-5, 5)) if shifted else (0, 0)
    return sp.Integer(a), sp.Integer(b), c, h, k, rng.choice(["x", "y"])
def hyp_eq(a, b, h, k, ax):
    if ax == "x": return f"{frac_sq('x', h, a*a)}-{frac_sq('y', k, b*b)}=1", (x - h) ** 2 / (a * a) - (y - k) ** 2 / (b * b) - 1
    return f"{frac_sq('y', k, a*a)}-{frac_sq('x', h, b*b)}=1", (y - k) ** 2 / (a * a) - (x - h) ** 2 / (b * b) - 1
def asym(a, b, h, k, ax):
    m = b / a if ax == "x" else a / b
    L = []
    for s in (1, -1):
        L.append(f"y={T(sp.expand(s*m*(x-h)+k))}")
    return L, m
def hyp_elements(w, a, b, c, h, k, ax):
    w.say(f"ផ្ចិតនៃអ៊ីពែបូលគឺ $I{pt(h,k)}$ ។")
    w.say(f"ផ្ទឹមនឹងទម្រង់ស្តង់ដា ៖ $a^2={T(a*a)}\\,,\\ b^2={T(b*b)}$ នាំឱ្យ $a={T(a)}\\,,\\ b={T(b)}$ ។ អ័ក្សទទឹង{'ដេក' if ax=='x' else 'ឈរ'} ។")
    w.say(f"$$c^2=a^2+b^2={T(a*a)}+{T(b*b)}={T(c*c)}\\Rightarrow c={T(c)}$$"); num(w, a * a + b * b, c * c, "c2"); w.C.append(check(f"sqrt(({a})**2+({b})**2)", c, "c"))
    if ax == "x": V = [(h - a, k), (h + a, k)]; Fs = [(h - c, k), (h + c, k)]
    else: V = [(h, k - a), (h, k + a)]; Fs = [(h, k - c), (h, k + c)]
    w.say(f"កំពូល ៖ $A{pt(*V[0])}\\,,\\ A'{pt(*V[1])}$ ។"); w.say(f"កំណុំ ៖ $F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}$ ។")
    e = c / a; w.say(f"អិចសង់ទ្រីស៊ីតេ ៖ $$e=\\frac{{c}}{{a}}=\\frac{{{T(c)}}}{{{T(a)}}}" + ("" if T(e) == f"\\frac{{{T(c)}}}{{{T(a)}}}" else f"={T(e)}") + "$$"); w.C.append(check(f"sqrt(({a})**2+({b})**2)/({a})", e, "e"))
    L, m = asym(a, b, h, k, ax)
    w.say(f"អាស៊ីមតូតទាំងពីរ ៖ $$y{st(-k)}=\\pm {T(m) if m!=1 else ''}\\left({lin('x',h)}\\right)$$" if h else f"អាស៊ីមតូតទាំងពីរ ៖ $$y{st(-k)}=\\pm {T(m) if m!=1 else ''}x$$")
    for s in (1, -1): num(w, sp.expand(s * m * (x - h) + k), sp.expand(s * m * (x - h) + k), "asym")
    w.say(f"គឺ $(D_1):{L[0]}$ និង $(D_2):{L[1]}$ ។")
    return Fs, e, L
def hyp_std(rng):
    a, b, c, h, k, ax = hyp_data(rng, rng.random() < 0.6); eq, _ = hyp_eq(a, b, h, k, ax); w = W(rng)
    P = w.v(f"គេឱ្យអ៊ីពែបូល $(H)$ មានសមីការ $${eq}$$\n{heads(['រកកូអរដោនេផ្ចិត កំពូល និងកំណុំនៃ $(H)$ ។', 'គណនាអិចសង់ទ្រីស៊ីតេ ហើយសរសេរសមីការអាស៊ីមតូតនៃ $(H)$ ។'])}",
            f"ក្នុងតម្រុយអរតូណរម៉ាល់ $(O,\\vec{{i}},\\vec{{j}})$ គេឱ្យអ៊ីពែបូល $(H):{eq}$ ។ រកកំពូល កំណុំ អិចសង់ទ្រីស៊ីតេ និងសមីការអាស៊ីមតូតនៃ $(H)$ ។")
    Fs, e, L = hyp_elements(w, a, b, c, h, k, ax)
    w.say(f"ដូចនេះ $\\boxed{{F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}\\,,\\ e={T(e)}\\,,\\ {L[0]}\\,,\\ {L[1]}}}$ ។")
    return row(w, CH, "conic_hyperbola", "hyperbola_elements", "easy" if (h, k) == (0, 0) else "medium", P, f"e={T(e)}", "hyp_std")
def hyp_general(rng):
    a, b, c, h, k, ax = hyp_data(rng, True)
    if h == 0 and k == 0: return None
    _, E0 = hyp_eq(a, b, h, k, ax); E = sp.expand(E0 * a * a * b * b); g = sp.gcd_list(sp.Poly(E, x, y).coeffs()); E = sp.expand(E / g)
    Pa, Pb = sp.Poly(E, x, y).coeff_monomial(x ** 2), sp.Poly(E, x, y).coeff_monomial(y ** 2)
    if max(abs(Pa), abs(Pb)) > 40: return None
    w = W(rng); eq, _ = hyp_eq(a, b, h, k, ax); cst = sp.Poly(E, x, y).coeff_monomial(1)
    P = f"គេឱ្យខ្សែកោង $(H)$ មានសមីការ $${poly_xy(E)}=0$$\n{heads(['បង្ហាញថា $(H)$ ជាអ៊ីពែបូល ហើយសរសេរសមីការជាទម្រង់ស្តង់ដា ។', 'រកកំណុំ និងសមីការអាស៊ីមតូតនៃ $(H)$ ។'])}"
    w.say(f"{K_(0)} សរសេរជាទម្រង់ស្តង់ដា ៖")
    grp = lambda m, v, hh: ("-" if m < 0 else "") + (f"{T(abs(m)) if abs(m) != 1 else ''}\\left({v}^2{st(-2*hh)}{v}\\right)" if hh else f"{T(abs(m)) if abs(m) != 1 else ''}{v}^2")
    gx, gy = grp(Pa, "x", h), grp(Pb, "y", k); w.say(f"ដាក់ជាក្រុម ៖ $${gx}{'+' if not gy.startswith('-') else ''}{gy}={T(-cst)}$$")
    okxy(w, sp.expand(Pa * (x ** 2 - 2 * h * x) + Pb * (y ** 2 - 2 * k * y) + cst), E)
    rhs = -cst + Pa * h * h + Pb * k * k
    tx_ = lambda m, v, hh: ("-" if m < 0 else "") + (T(abs(m)) if abs(m) != 1 else "") + sq(v, hh)
    t1, t2 = tx_(Pa, "x", h), tx_(Pb, "y", k)
    w.say(f"បំពេញការេ ៖ $${t1}{'+' if not t2.startswith('-') else ''}{t2}={T(-cst)}{st(Pa*h*h)}{st(Pb*k*k)}={T(rhs)}$$"); okxy(w, Pa * (x - h) ** 2 + Pb * (y - k) ** 2 - rhs, E)
    w.say(f"ចែកអង្គទាំងពីរនឹង ${T(rhs)}$ ៖ $${eq}$$"); num(w, rhs / (Pa if ax == "x" else Pb), a * a, "a2")
    w.say("សមីការនេះមានរាងស្តង់ដានៃអ៊ីពែបូល ដូច្នេះ $(H)$ ជាអ៊ីពែបូល ។"); w.say(f"{K_(1)} ធាតុនៃអ៊ីពែបូល ៖")
    Fs, e, L = hyp_elements(w, a, b, c, h, k, ax)
    w.say(f"ដូចនេះ $\\boxed{{{eq}\\,,\\ F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}\\,,\\ {L[0]}\\,,\\ {L[1]}}}$ ។")
    return row(w, CH, "conic_hyperbola", "hyperbola_general_to_standard", "bacii", P, eq, "hyp_general")
def hyp_find(rng):
    a, b, c, h, k, ax = hyp_data(rng, rng.random() < 0.9)
    if not c.is_integer: return None
    eq, _ = hyp_eq(a, b, h, k, ax); w = W(rng); kind = rng.choice(["FV", "VA", "Fe"]); L, m = asym(a, b, h, k, ax)
    if ax == "x": Fs = [(h - c, k), (h + c, k)]; V = [(h - a, k), (h + a, k)]
    else: Fs = [(h, k - c), (h, k + c)]; V = [(h, k - a), (h, k + a)]
    if kind == "FV": P = f"រកសមីការអ៊ីពែបូល $(H)$ ដែលមានកំណុំ $F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}$ និងកំពូល $A{pt(*V[0])}\\,,\\ A'{pt(*V[1])}$ ។"
    elif kind == "VA": P = f"រកសមីការអ៊ីពែបូល $(H)$ ដែលមានកំពូល $A{pt(*V[0])}\\,,\\ A'{pt(*V[1])}$ ហើយមានអាស៊ីមតូតមួយគឺ $(D):{L[0]}$ ។"
    else: P = f"រកសមីការអ៊ីពែបូល $(H)$ ដែលមានកំណុំ $F{pt(*Fs[0])}\\,,\\ F'{pt(*Fs[1])}$ និងអិចសង់ទ្រីស៊ីតេ $e={T(c/a)}$ ។"
    pair = V if kind == "VA" else Fs
    w.say(f"ផ្ចិត $I$ ជាចំណុចកណ្តាលនៃ {SEGA if kind=='VA' else SEGF} ៖ $I{pt(h,k)}$ ។"); num(w, (pair[0][0] + pair[1][0]) / sp.Integer(2), h, "cx"); num(w, (pair[0][1] + pair[1][1]) / sp.Integer(2), k, "cy")
    w.say(f"អ័ក្សទទឹង{'ដេក' if ax=='x' else 'ឈរ'} ដូច្នេះសមីការមានរាង " + ("$\\frac{\\left(x-h\\right)^2}{a^2}-\\frac{\\left(y-k\\right)^2}{b^2}=1$ ។" if ax == "x" else "$\\frac{\\left(y-k\\right)^2}{a^2}-\\frac{\\left(x-h\\right)^2}{b^2}=1$ ។"))
    if kind == "FV": w.say(f"$a=IA={T(a)}$ និង $c=IF={T(c)}$ ។"); w.say(f"$$b^2=c^2-a^2={T(c*c)}-{T(a*a)}={T(b*b)}$$"); num(w, c * c - a * a, b * b, "b2")
    elif kind == "VA":
        w.say(f"$a=IA={T(a)}$ ។ មេគុណប្រាប់ទិសនៃអាស៊ីមតូតគឺ ${'\\frac{b}{a}' if ax=='x' else '\\frac{a}{b}'}={T(m)}$ ។")
        if ax == "x": w.say(f"$$b={T(m)}\\times{T(a)}={T(b)}$$"); num(w, m * a, b, "b")
        else: w.say(f"$$b=\\frac{{a}}{{{T(m)}}}=\\frac{{{T(a)}}}{{{T(m)}}}={T(b)}$$"); num(w, a / m, b, "b")
    else:
        w.say(f"$c=IF={T(c)}$ ។ ដោយ $e=\\frac{{c}}{{a}}$ នោះ $$a=\\frac{{c}}{{e}}=\\frac{{{T(c)}}}{{{T(c/a)}}}={T(a)}$$"); num(w, c / (c / a), a, "a")
        w.say(f"$$b^2=c^2-a^2={T(c*c)}-{T(a*a)}={T(b*b)}$$"); num(w, c * c - a * a, b * b, "b2")
    w.say(f"ដូចនេះ $\\boxed{{(H):{eq}}}$ ។")
    return row(w, CH, "conic_hyperbola", "hyperbola_find_equation", "medium", P, eq, "hyp_find")

# ---------- tangent lines ----------
def tangent(rng):
    kind = rng.choice(["P", "E", "H"]); w = W(rng)
    if kind == "P":
        p = nice_p(rng) * rng.choice([1, -1]); t = rng.choice([-4, -3, -2, -1, R(-1, 2), R(1, 2), 1, 2, 3, 4, 5]); y0 = 2 * p * t; x0 = p * t * t  # y^2=4px
        if not (x0.is_integer if hasattr(x0, "is_integer") else True) or not sp.sympify(y0).is_integer: return None
        nm = f"y^2={T(4*p)}x"; F = y ** 2 - 4 * p * x
        P = f"គេឱ្យប៉ារ៉ាបូល $(P):{nm}$ និងចំណុច $M{pt(x0,y0)}$ ។\n{heads(['ផ្ទៀងផ្ទាត់ថា $M$ ស្ថិតនៅលើ $(P)$ ។', 'សរសេរសមីការបន្ទាត់ប៉ះ $(T)$ នឹង $(P)$ ត្រង់ចំណុច $M$ ។'])}"
        w.say(f"{K_(0)} ជំនួសកូអរដោនេ $M$ ៖ $${pp(y0) if y0<0 else T(y0)}^2={T(y0*y0)}\\ \\text{{និង}}\\ {T(4*p)}\\times{par(x0)}={T(4*p*x0)}$$"); num(w, sp.sympify(y0) ** 2, 4 * p * x0, "on")
        w.say("អង្គទាំងពីរស្មើគ្នា ដូច្នេះ $M$ ស្ថិតនៅលើ $(P)$ ។")
        w.say(f"{K_(1)} បន្ទាត់ប៉ះនឹងប៉ារ៉ាបូល $y^2=4px$ ត្រង់ $M(x_0;y_0)$ មានសមីការ $y_0y=2p\\left(x+x_0\\right)$ ។")
        w.say(f"ដោយ $4p={T(4*p)}$ នោះ $2p={T(2*p)}$ ។"); w.say(f"$${T(y0)}y={T(2*p)}\\left(x{st(x0)}\\right)$$")
        m = 2 * p / y0; c0 = 2 * p * x0 / y0; line = sp.expand(m * x + c0)
        w.say(f"$$y={T(line)}$$"); num(w, sp.expand((2 * p * (x + x0)) / y0), line, "tangent")
        # derivative check: implicit slope 2p/y0
        w.C.append(check(f"2*{p}/({y0})", str(m), "slope"))
        ans = f"y={T(line)}"
    elif kind == "E":
        a, b, c = rng.choice([(5, 4, 3), (5, 3, 4), (10, 8, 6), (10, 6, 8), (15, 12, 9), (15, 9, 12), (25, 24, 7), (25, 7, 24)]); a, b = sp.Integer(a), sp.Integer(b)
        pts = [(sp.Integer(0), b), (a, sp.Integer(0)), (R(3, 5) * a, R(4, 5) * b), (R(4, 5) * a, R(3, 5) * b), (R(-3, 5) * a, R(4, 5) * b), (R(4, 5) * a, R(-3, 5) * b)]
        x0, y0 = rng.choice(pts[2:]); x0, y0 = x0 * rng.choice([1, -1]), y0 * rng.choice([1, -1]); nm = f"\\frac{{x^2}}{{{a*a}}}+\\frac{{y^2}}{{{b*b}}}=1"
        P = f"គេឱ្យអេលីប $(E):{nm}$ និងចំណុច $M{pt(x0,y0)}$ ។\n{heads(['ផ្ទៀងផ្ទាត់ថា $M$ ស្ថិតនៅលើ $(E)$ ។', 'សរសេរសមីការបន្ទាត់ប៉ះ $(T)$ នឹង $(E)$ ត្រង់ចំណុច $M$ ។'])}"
        w.say(f"{K_(0)} $$\\frac{{{pp(x0) if (x0<0 or not x0.is_integer) else T(x0)}^2}}{{{a*a}}}+\\frac{{{pp(y0) if (y0<0 or not y0.is_integer) else T(y0)}^2}}{{{b*b}}}=\\frac{{{T(x0*x0)}}}{{{a*a}}}+\\frac{{{T(y0*y0)}}}{{{b*b}}}={T(x0*x0/(a*a))}+{T(y0*y0/(b*b))}=1$$"); num(w, x0 ** 2 / a ** 2 + y0 ** 2 / b ** 2, 1, "on")
        w.say("ដូច្នេះ $M$ ស្ថិតនៅលើ $(E)$ ។")
        w.say(f"{K_(1)} បន្ទាត់ប៉ះនឹងអេលីប $\\frac{{x^2}}{{a^2}}+\\frac{{y^2}}{{b^2}}=1$ ត្រង់ $M(x_0;y_0)$ មានសមីការ $\\frac{{x_0x}}{{a^2}}+\\frac{{y_0y}}{{b^2}}=1$ ។")
        A1, B1 = x0 / a ** 2, y0 / b ** 2; w.say(f"$$\\frac{{{par(x0)}x}}{{{a*a}}}+\\frac{{{par(y0)}y}}{{{b*b}}}=1\\Leftrightarrow {T(A1)}x{st(B1)}y=1$$".replace("+-", "-")); num(w, A1, x0 / a ** 2, "A")
        line = sp.expand((1 - A1 * x) / B1); w.say(f"$$y={T(line)}$$"); num(w, sp.expand((1 - A1 * x) / B1), line, "tangent")
        w.C.append(check(f"-({b*b}*{x0})/({a*a}*{y0})", str(sp.expand(line.coeff(x))), "slope")); ans = f"y={T(line)}"
    else:
        a, b, c = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (6, 8, 10), (8, 6, 10)]); a, b = sp.Integer(a), sp.Integer(b)
        x0, y0 = rng.choice([(R(5, 3) * a, R(4, 3) * b), (R(5, 4) * a, R(3, 4) * b), (R(-5, 3) * a, R(4, 3) * b), (R(5, 4) * a, R(-3, 4) * b), (R(13, 5) * a, R(12, 5) * b)])
        nm = f"\\frac{{x^2}}{{{a*a}}}-\\frac{{y^2}}{{{b*b}}}=1"
        P = f"គេឱ្យអ៊ីពែបូល $(H):{nm}$ និងចំណុច $M{pt(x0,y0)}$ ។\n{heads(['ផ្ទៀងផ្ទាត់ថា $M$ ស្ថិតនៅលើ $(H)$ ។', 'សរសេរសមីការបន្ទាត់ប៉ះ $(T)$ នឹង $(H)$ ត្រង់ចំណុច $M$ ។'])}"
        w.say(f"{K_(0)} $$\\frac{{{par(x0)}^2}}{{{a*a}}}-\\frac{{{par(y0)}^2}}{{{b*b}}}={T(x0*x0/(a*a))}-{T(y0*y0/(b*b))}=1$$"); num(w, x0 ** 2 / a ** 2 - y0 ** 2 / b ** 2, 1, "on")
        w.say("ដូច្នេះ $M$ ស្ថិតនៅលើ $(H)$ ។")
        w.say(f"{K_(1)} បន្ទាត់ប៉ះនឹងអ៊ីពែបូល $\\frac{{x^2}}{{a^2}}-\\frac{{y^2}}{{b^2}}=1$ ត្រង់ $M(x_0;y_0)$ មានសមីការ $\\frac{{x_0x}}{{a^2}}-\\frac{{y_0y}}{{b^2}}=1$ ។")
        A1, B1 = x0 / a ** 2, y0 / b ** 2; w.say(f"$$\\frac{{{par(x0)}x}}{{{a*a}}}-\\frac{{{par(y0)}y}}{{{b*b}}}=1\\Leftrightarrow {T(A1)}x{st(-B1)}y=1$$")
        line = sp.expand((A1 * x - 1) / B1); w.say(f"$$y={T(line)}$$"); num(w, sp.expand((A1 * x - 1) / B1), line, "tangent")
        w.C.append(check(f"({b*b}*{x0})/({a*a}*{y0})", str(sp.expand(line.coeff(x))), "slope")); ans = f"y={T(line)}"
    w.say(f"ដូចនេះ $\\boxed{{(T):{ans}}}$ ។")
    return row(w, CH, "conic_tangent", "tangent_at_point", "medium", P, ans, "tangent")

# ---------- identify the conic ----------
def identify(rng):
    t = rng.choice(["P", "E", "H"])
    if t == "P": return par_general(rng)
    if t == "E": return ell_general(rng)
    return hyp_general(rng)

# ---------- line and conic ----------
def line_conic(rng):
    kind = rng.choice(["P", "E"]); w = W(rng)
    if kind == "P":
        p = rng.choice([1, 2, 3, 4, 5, 6]); r1, r2 = rng.sample([-12, -10, -8, -6, -4, -3, -2, -1, 1, 2, 3, 4, 6, 8, 10, 12], 2)  # y-values of intersections
        A = (sp.Rational(r1 * r1, 4 * p), r1); B = (sp.Rational(r2 * r2, 4 * p), r2)
        if A[0] == B[0]: return None
        m = sp.Rational(B[1] - A[1], B[0] - A[0]); q = A[1] - m * A[0]
        if not (m.is_integer or (2 * m).is_integer or (3 * m).is_integer) or abs(m) > 8: return None
        conic = f"y^2={4*p}x"; line = f"y={T(m*x+q)}"
        P = f"គេឱ្យប៉ារ៉ាបូល $(P):{conic}$ និងបន្ទាត់ $(d):{line}$ ។ រកកូអរដោនេនៃចំណុចប្រសព្វរវាង $(P)$ និង $(d)$ ។"
        w.say(f"ពីសមីការ $(d)$ គេបាន $x=\\frac{{y{st(-q)}}}{{{T(m)}}}$ ។" if m != 1 else f"ពីសមីការ $(d)$ គេបាន $x=y{st(-q)}$ ។")
        quad = sp.expand(m * y ** 2 - 4 * p * y + 4 * p * q)  # from y^2 = 4p (y-q)/m
        w.say(f"ជំនួសក្នុង $(P)$ ៖ $$y^2={4*p}\\times\\frac{{y{st(-q)}}}{{{T(m)}}}\\Leftrightarrow {T(quad).replace('y^{2}','y^2')}=0$$")
        num(w, sp.expand(quad.subs(y, x)), sp.expand(m * (x - r1) * (x - r2)), "quad")
        w.say(f"ឫសនៃសមីការគឺ $y_1={r1}$ និង $y_2={r2}$ ។"); w.say(f"$$x_1=\\frac{{{r1*r1}}}{{{4*p}}}={T(A[0])}\\,,\\quad x_2=\\frac{{{r2*r2}}}{{{4*p}}}={T(B[0])}$$")
        num(w, sp.Rational(r1 * r1, 4 * p), A[0], "x1"); num(w, m * A[0] + q, r1, "onA"); num(w, m * B[0] + q, r2, "onB")
        ans = f"{pt(*A)},{pt(*B)}"
    else:
        a, b, c = rng.choice(TRI[:8]); a, b = sp.Integer(a), sp.Integer(b)
        P1, P2 = rng.sample([(a, 0), (0, b), (-a, 0), (0, -b), (R(3, 5) * a, R(4, 5) * b), (R(-3, 5) * a, R(4, 5) * b), (R(4, 5) * a, R(-3, 5) * b)], 2)
        P1 = tuple(sp.sympify(v) for v in P1); P2 = tuple(sp.sympify(v) for v in P2)
        if P1[0] == P2[0]: return None
        m = (P2[1] - P1[1]) / (P2[0] - P1[0]); q = P1[1] - m * P1[0]
        conic = f"\\frac{{x^2}}{{{a*a}}}+\\frac{{y^2}}{{{b*b}}}=1"; line = f"y={T(m*x+q)}"
        P = f"គេឱ្យអេលីប $(E):{conic}$ និងបន្ទាត់ $(d):{line}$ ។ រកកូអរដោនេនៃចំណុចប្រសព្វរវាង $(E)$ និង $(d)$ ។"
        quad = sp.expand((b * b * x * x + a * a * (m * x + q) ** 2 - a * a * b * b)); lc = sp.Poly(quad, x).LC(); qn = sp.expand(quad / sp.gcd_list(sp.Poly(quad, x).coeffs()))
        w.say(f"ជំនួស $y={T(m*x+q)}$ ក្នុងសមីការ $(E)$ ៖ $$\\frac{{x^2}}{{{a*a}}}+\\frac{{\\left({T(m*x+q)}\\right)^2}}{{{b*b}}}=1$$")
        w.say(f"គុណអង្គទាំងពីរនឹង ${a*a*b*b}$ ហើយសម្រួល ៖ $${T(qn).replace('x^{2}','x^2')}=0$$"); num(w, sp.expand(qn * sp.gcd_list(sp.Poly(quad, x).coeffs())), quad, "quad")
        roots = sorted(sp.solve(qn, x), key=lambda v: float(v))
        if len(roots) != 2: return None
        w.say(f"ឫសនៃសមីការគឺ $x_1={T(roots[0])}$ និង $x_2={T(roots[1])}$ ។")
        pts_ = [(r_, sp.expand(m * r_ + q)) for r_ in roots]
        for r_, yy in pts_: w.say(f"បើ $x={T(r_)}$ នោះ $y={T(m)}\\times{par(r_)}{st(q)}={T(yy)}$ ។" if m != 1 else f"បើ $x={T(r_)}$ នោះ $y={T(yy)}$ ។"); num(w, qn.subs(x, r_), 0, "root"); num(w, r_ ** 2 / a ** 2 + yy ** 2 / b ** 2, 1, "onE")
        ans = ",".join(pt(*p_) for p_ in pts_); A, B = pts_
    w.say(f"ដូចនេះ ចំណុចប្រសព្វគឺ $\\boxed{{{pt(*A)}\\ \\text{{និង}}\\ {pt(*B)}}}$ ។")
    return row(w, CH, "conic_line", "line_conic_intersection", "medium", P, ans, "line_conic")

ALL = [(par_std, 1400), (par_general, 1400), (par_find, 1200), (ell_std, 1400), (ell_general, 1500), (ell_find, 1100),
       (hyp_std, 1400), (hyp_general, 1500), (hyp_find, 1100), (tangent, 900), (line_conic, 900)]
