"""Space geometry chapter: vectors, scalar and vector products, lines and planes in space.
Points are chosen first; every printed number is recomputed by SymPy. No text is written by a language model at run time."""
from kx import *
CH = "space"
def num(w, a, b, note="value"):
    assert sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0, (a, b, note)
    w.C.append(check(a, b, note))
def P3(v): return "\\left(" + "\\,;\\,".join(T(c) for c in v) + "\\right)"
def vec(n): return f"\\vec{{{n}}}"
def sub(B, A): return tuple(sp.Integer(b) - sp.Integer(a) for a, b in zip(A, B))
def dot(u, v): return sum(a * b for a, b in zip(u, v))
def cross(u, v): return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
def norm2(u): return sum(c * c for c in u)
def rpt(rng, lo=-5, hi=6): return tuple(sp.Integer(rng.randint(lo, hi)) for _ in range(3))
def ppx(v): return f"\\left({T(v)}\\right)" if v < 0 else T(v)
def dot_line(u, v): return "+".join(f"{ppx(a)}\\times{ppx(b)}" for a, b in zip(u, v)).replace("+-", "-")
def sum_sq(u): return "+".join(f"{ppx(c)}^2" for c in u)
def sqrt_t(n2):
    v = sp.sqrt(n2); return T(v)
def pn_text(n, A):
    """a(x-x0)+b(y-y0)+c(z-z0) with signs folded in and zero terms left out."""
    t = ""
    for c, a0, v in zip(n, A, "xyz"):
        if c == 0: continue
        term = (f"\\left({v}{st(-a0)}\\right)" if a0 != 0 else v)
        t += ("-" if c < 0 else ("+" if t else "")) + ("" if abs(c) == 1 else T(abs(c))) + term
    return t
def plane_t(n, d):
    t = ""
    for c, s in zip(n, "xyz"):
        if c == 0: continue
        t += ("-" if c < 0 else ("+" if t else "")) + ("" if abs(c) == 1 else T(abs(c))) + s
    if d: t += st(d)
    return t + "=0"
def cross_lines(w, u, v, nu="u", nv="v", res="n"):
    c = cross(u, v)
    w.say(f"$${vec(nu)}\\wedge{vec(nv)}=\\left(\\begin{{vmatrix}}{T(u[1])}&{T(u[2])}\\\\{T(v[1])}&{T(v[2])}\\end{{vmatrix}}\\,;\\,\\begin{{vmatrix}}{T(u[2])}&{T(u[0])}\\\\{T(v[2])}&{T(v[0])}\\end{{vmatrix}}\\,;\\,\\begin{{vmatrix}}{T(u[0])}&{T(u[1])}\\\\{T(v[0])}&{T(v[1])}\\end{{vmatrix}}\\right)$$")
    w.say(f"$$=\\left({ppx(u[1])}\\times{ppx(v[2])}-{ppx(u[2])}\\times{ppx(v[1])}\\,;\\,{ppx(u[2])}\\times{ppx(v[0])}-{ppx(u[0])}\\times{ppx(v[2])}\\,;\\,{ppx(u[0])}\\times{ppx(v[1])}-{ppx(u[1])}\\times{ppx(v[0])}\\right)={P3(c)}$$")
    for i in range(3): num(w, f"({u[(i+1)%3]})*({v[(i+2)%3]})-({u[(i+2)%3]})*({v[(i+1)%3]})", c[i], "cross")
    return c
FRAME = "ក្នុងលំហប្រដាប់ដោយតម្រុយអរតូណរម៉ាល់ $(O,\\vec{i},\\vec{j},\\vec{k})$ "
def heads(parts): return "\n".join(f"{K[i]}. {p}" for i, p in enumerate(parts))

def vec_basic(rng):
    A, B = rpt(rng), rpt(rng)
    if A == B: return None
    u = sub(B, A); w = W(rng); n2 = norm2(u); I = tuple(sp.Rational(a + b, 2) for a, b in zip(A, B))
    P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}$ និង $B{P3(B)}$ ។\n" + heads(["រកកូអរដោនេនៃវ៉ិចទ័រ $\\vec{AB}$ ។", "គណនាប្រវែង $AB$ ។", "រកកូអរដោនេនៃចំណុចកណ្តាល $I$ នៃអង្កត់ $[AB]$ ។"])
    w.say("ក. កូអរដោនេនៃវ៉ិចទ័រ $\\vec{AB}$ ស្មើកូអរដោនេចុង $B$ ដកកូអរដោនេគល់ $A$ ៖"); w.say(f"$$\\vec{{AB}}=\\left(x_B-x_A\\,;\\,y_B-y_A\\,;\\,z_B-z_A\\right)=\\left({T(B[0])}{st(-A[0])}\\,;\\,{T(B[1])}{st(-A[1])}\\,;\\,{T(B[2])}{st(-A[2])}\\right)={P3(u)}$$")
    for i in range(3): num(w, f"({B[i]})-({A[i]})", u[i], "AB")
    w.say("ខ. ប្រវែង $AB$ ស្មើណិមនៃវ៉ិចទ័រ $\\vec{AB}$ ៖"); w.say(f"$$AB=\\sqrt{{{sum_sq(u)}}}=\\sqrt{{{n2}}}" + ("" if sqrt_t(n2) == f"\\sqrt{{{n2}}}" else f"={sqrt_t(n2)}") + "$$"); w.C.append(check(f"sqrt(({B[0]}-{A[0]})**2+({B[1]}-{A[1]})**2+({B[2]}-{A[2]})**2)", sp.sqrt(n2), "length"))
    w.say("គ. កូអរដោនេនៃចំណុចកណ្តាល $I$ ស្មើមធ្យមនៃកូអរដោនេ $A$ និង $B$ ៖"); w.say(f"$$I\\left(\\frac{{x_A+x_B}}{{2}}\\,;\\,\\frac{{y_A+y_B}}{{2}}\\,;\\,\\frac{{z_A+z_B}}{{2}}\\right)=I{P3(I)}$$")
    for i in range(3): num(w, f"(({A[i]})+({B[i]}))/2", I[i], "mid")
    w.say(f"ដូចនេះ $\\boxed{{\\vec{{AB}}={P3(u)}\\,,\\ AB={sqrt_t(n2)}\\,,\\ I{P3(I)}}}$ ។")
    return row(w, CH, "space_vector", "vector_length_midpoint", "easy", P, f"AB={sqrt_t(n2)}", "vec_basic")
def dot_angle(rng):
    u, v = rpt(rng, -4, 5), rpt(rng, -4, 5)
    if norm2(u) == 0 or norm2(v) == 0: return None
    if rng.random() < 0.35:  # make them perpendicular
        a, b = u[0], u[1]
        if u[2] == 0: return None
        v = (v[0], v[1], sp.Rational(-(a * v[0] + b * v[1]), u[2]))
        if not v[2].is_integer or norm2(v) == 0: return None
    w = W(rng); d = dot(u, v); nu, nv = norm2(u), norm2(v)
    P = FRAME + f"គេឱ្យវ៉ិចទ័រ $\\vec{{u}}={P3(u)}$ និង $\\vec{{v}}={P3(v)}$ ។\n" + heads(["គណនាផលគុណស្កាលែ $\\vec{u}\\cdot\\vec{v}$ ។", "គណនា $\\cos\\theta$ ដែល $\\theta$ ជាមុំរវាង $\\vec{u}$ និង $\\vec{v}$ ។ តើវ៉ិចទ័រទាំងពីរកែងគ្នាឬទេ ?"])
    w.say(f"ក. $$\\vec{{u}}\\cdot\\vec{{v}}={dot_line(u, v)}={T(d)}$$"); w.C.append(check("+".join(f"({a})*({b})" for a, b in zip(u, v)), d, "dot"))
    w.say(f"ខ. $$\\|\\vec{{u}}\\|=\\sqrt{{{sum_sq(u)}}}={sqrt_t(nu)}\\,,\\quad\\|\\vec{{v}}\\|=\\sqrt{{{sum_sq(v)}}}={sqrt_t(nv)}$$")
    cs = sp.nsimplify(d / (sp.sqrt(nu) * sp.sqrt(nv))); cs = sp.radsimp(d / (sp.sqrt(nu) * sp.sqrt(nv)))
    w.say(f"$$\\cos\\theta=\\frac{{\\vec{{u}}\\cdot\\vec{{v}}}}{{\\|\\vec{{u}}\\|\\,\\|\\vec{{v}}\\|}}=\\frac{{{T(d)}}}{{{sqrt_t(nu)}\\times{sqrt_t(nv)}}}={T(cs)}$$"); w.C.append(check(f"({d})/(sqrt({nu})*sqrt({nv}))", cs, "cos"))
    if d == 0: w.say("ដោយ $\\vec{u}\\cdot\\vec{v}=0$ នោះ $\\vec{u}$ និង $\\vec{v}$ កែងគ្នា ។"); tail = "\\vec{u}\\perp\\vec{v}"
    else: w.say("ដោយ $\\vec{u}\\cdot\\vec{v}\\neq0$ នោះ $\\vec{u}$ និង $\\vec{v}$ មិនកែងគ្នាទេ ។"); tail = f"\\cos\\theta={T(cs)}"
    w.say(f"ដូចនេះ $\\boxed{{\\vec{{u}}\\cdot\\vec{{v}}={T(d)}\\,,\\ {tail}}}$ ។")
    return row(w, CH, "space_vector", "scalar_product_angle", "easy", P, f"{T(d)}", "dot_angle")
def three_pts(rng):
    for _ in range(20):
        A, B, C = rpt(rng), rpt(rng), rpt(rng)
        if cross(sub(B, A), sub(C, A)) != (0, 0, 0): return A, B, C
    return None
def cross_area(rng):
    t = three_pts(rng)
    if not t: return None
    A, B, C = t; u, v = sub(B, A), sub(C, A); w = W(rng)
    P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}\\,,\\ B{P3(B)}$ និង $C{P3(C)}$ ។\n" + heads(["គណនាផលគុណវ៉ិចទ័រ $\\vec{AB}\\wedge\\vec{AC}$ ។", "បង្ហាញថា $A\\,,\\,B\\,,\\,C$ មិនរត់ត្រង់គ្នា ហើយគណនាផ្ទៃក្រឡាត្រីកោណ $ABC$ ។"])
    w.say(f"ក. $\\vec{{AB}}={P3(u)}$ និង $\\vec{{AC}}={P3(v)}$ ។"); c = cross_lines(w, u, v, "AB", "AC")
    n2 = norm2(c); S = sp.sqrt(n2) / 2
    w.say(f"ខ. ដោយ $\\vec{{AB}}\\wedge\\vec{{AC}}\\neq\\vec{{0}}$ នោះ $A\\,,\\,B\\,,\\,C$ មិនរត់ត្រង់គ្នាទេ ។")
    w.say(f"$$S_{{ABC}}=\\frac{{1}}{{2}}\\left\\|\\vec{{AB}}\\wedge\\vec{{AC}}\\right\\|=\\frac{{1}}{{2}}\\sqrt{{{sum_sq(c)}}}=\\frac{{1}}{{2}}\\sqrt{{{n2}}}={T(S)}$$"); w.C.append(check(f"sqrt({n2})/2", S, "area"))
    w.say(f"ដូចនេះ $\\boxed{{S_{{ABC}}={T(S)}}}$ ឯកតាផ្ទៃក្រឡា ។")
    return row(w, CH, "space_product", "cross_product_triangle_area", "medium", P, f"S={T(S)}", "cross_area")
def volume(rng):
    t = three_pts(rng)
    if not t: return None
    A, B, C = t; D = rpt(rng); u, v, s = sub(B, A), sub(C, A), sub(D, A); c = cross(u, v); m = dot(c, s)
    if m == 0: return None
    w = W(rng); V = sp.Abs(sp.Rational(m, 6))
    P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}\\,,\\ B{P3(B)}\\,,\\ C{P3(C)}$ និង $D{P3(D)}$ ។\n" + heads(["គណនា $\\vec{AB}\\wedge\\vec{AC}$ ។", "បង្ហាញថា $A\\,,\\,B\\,,\\,C\\,,\\,D$ មិននៅលើប្លង់តែមួយ ហើយគណនាមាឌតេត្រាអែត $ABCD$ ។"])
    w.say(f"ក. $\\vec{{AB}}={P3(u)}\\,,\\ \\vec{{AC}}={P3(v)}\\,,\\ \\vec{{AD}}={P3(s)}$ ។"); cross_lines(w, u, v, "AB", "AC")
    w.say(f"ខ. $$\\left(\\vec{{AB}}\\wedge\\vec{{AC}}\\right)\\cdot\\vec{{AD}}={dot_line(c, s)}={T(m)}$$"); w.C.append(check("+".join(f"({a})*({b})" for a, b in zip(c, s)), m, "triple"))
    w.say("ដោយផលគុណចម្រុះខុសពី $0$ នោះចំណុចទាំងបួនមិននៅលើប្លង់តែមួយទេ ។")
    w.say(f"$$V_{{ABCD}}=\\frac{{1}}{{6}}\\left|\\left(\\vec{{AB}}\\wedge\\vec{{AC}}\\right)\\cdot\\vec{{AD}}\\right|=\\frac{{1}}{{6}}\\times{abs(m)}={T(V)}$$"); w.C.append(check(f"Abs({m})/6", V, "volume"))
    w.say(f"ដូចនេះ $\\boxed{{V_{{ABCD}}={T(V)}}}$ ឯកតាមាឌ ។")
    return row(w, CH, "space_product", "tetrahedron_volume", "bacii", P, f"V={T(V)}", "volume")
def reduce_n(n):
    g = sp.gcd_list([c for c in n if c != 0]) if any(n) else 1
    n = tuple(c / g for c in n)
    if next(c for c in n if c != 0) < 0: n = tuple(-c for c in n)
    return n
def plane3(rng):
    t = three_pts(rng)
    if not t: return None
    A, B, C = t; u, v = sub(B, A), sub(C, A); w = W(rng)
    P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}\\,,\\ B{P3(B)}$ និង $C{P3(C)}$ ។\n" + heads(["គណនា $\\vec{n}=\\vec{AB}\\wedge\\vec{AC}$ ។", "សរសេរសមីការប្លង់ $(ABC)$ ។"])
    w.say(f"ក. $\\vec{{AB}}={P3(u)}$ និង $\\vec{{AC}}={P3(v)}$ ។"); c = cross_lines(w, u, v, "AB", "AC")
    n = reduce_n(c); d = -dot(n, A)
    w.say(f"ខ. វ៉ិចទ័រ $\\vec{{n}}$ កែងនឹងប្លង់ $(ABC)$ ។ " + (f"យកវ៉ិចទ័រណរម៉ាល់ $\\vec{{n'}}={P3(n)}$ ដែលកូលីនេអ៊ែរនឹង $\\vec{{n}}$ ។" if n != c else f"វាជាវ៉ិចទ័រណរម៉ាល់នៃប្លង់ ។"))
    w.say(f"ប្លង់កាត់តាម $A{P3(A)}$ មានសមីការ ៖ $${pn_text(n, A)}=0$$")
    w.say(f"$$\\Leftrightarrow {plane_t(n, d)}$$")
    for Q, nm in ((B, "B"), (C, "C")): num(w, f"{n[0]}*({Q[0]})+{n[1]}*({Q[1]})+{n[2]}*({Q[2]})+({d})", 0, f"on{nm}")
    w.say(f"ផ្ទៀងផ្ទាត់ ៖ កូអរដោនេ $B$ និង $C$ ផ្ទៀងផ្ទាត់សមីការនេះ ។")
    w.say(f"ដូចនេះ $\\boxed{{(ABC):{plane_t(n, d)}}}$ ។")
    return row(w, CH, "space_plane", "plane_through_three_points", "medium", P, plane_t(n, d), "plane3")
def plane_pn(rng):
    A = rpt(rng); n = rpt(rng, -4, 5)
    if n == (0, 0, 0): return None
    kind = rng.choice(["n", "AB"]); w = W(rng); d = -dot(n, A)
    if kind == "n": P = FRAME + f"សរសេរសមីការប្លង់ $(\\alpha)$ ដែលកាត់តាមចំណុច $A{P3(A)}$ ហើយមានវ៉ិចទ័រណរម៉ាល់ $\\vec{{n}}={P3(n)}$ ។"
    else:
        M = rpt(rng); N = tuple(m + c for m, c in zip(M, n))
        P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}\\,,\\ M{P3(M)}$ និង $N{P3(N)}$ ។ សរសេរសមីការប្លង់ $(\\alpha)$ ដែលកាត់តាម $A$ ហើយកែងនឹងបន្ទាត់ $(MN)$ ។"
        w.say(f"ប្លង់ $(\\alpha)$ កែងនឹង $(MN)$ ដូច្នេះ $\\vec{{MN}}$ ជាវ៉ិចទ័រណរម៉ាល់ ៖ $$\\vec{{MN}}={P3(n)}$$")
        for i in range(3): num(w, f"({N[i]})-({M[i]})", n[i], "MN")
    w.say(f"ប្លង់កាត់តាម $A{P3(A)}$ មានសមីការ $a\\left(x-x_A\\right)+b\\left(y-y_A\\right)+c\\left(z-z_A\\right)=0$ ៖")
    w.say(f"$${pn_text(n, A)}=0$$"); w.say(f"$$\\Leftrightarrow {plane_t(n, d)}$$")
    num(w, f"-(({n[0]})*({A[0]})+({n[1]})*({A[1]})+({n[2]})*({A[2]}))", d, "d")
    w.say(f"ដូចនេះ $\\boxed{{(\\alpha):{plane_t(n, d)}}}$ ។")
    return row(w, CH, "space_plane", "plane_point_normal", "easy", P, plane_t(n, d), "plane_pn")
def param_t(A, u):
    return "\\begin{cases}" + "\\\\".join(f"{s}={T(sp.expand(a + c * sp.Symbol('t')))}" for s, a, c in zip("xyz", A, u)) + "\\end{cases}"
def line_param(rng):
    A, B = rpt(rng), rpt(rng)
    if A == B: return None
    u = sub(B, A); t0 = rng.choice([-2, -1, 2, 3, R(1, 2)]); on = rng.random() < 0.5
    M = tuple(a + t0 * c for a, c in zip(A, u))
    if not on: M = (M[0], M[1], M[2] + rng.choice([1, -1, 2]))
    if not all(sp.sympify(c).is_integer for c in M): return None
    w = W(rng); ts = sp.Symbol("t")
    P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}\\,,\\ B{P3(B)}$ និង $M{P3(M)}$ ។\n" + heads(["សរសេរសមីការប៉ារ៉ាម៉ែត្រនៃបន្ទាត់ $(AB)$ ។", "តើចំណុច $M$ ស្ថិតនៅលើបន្ទាត់ $(AB)$ ឬទេ ?"])
    w.say(f"ក. វ៉ិចទ័រប្រាប់ទិសនៃ $(AB)$ គឺ $\\vec{{AB}}={P3(u)}$ ។"); w.say(f"$$(AB):{param_t(A, u)}\\ ,\\ t\\in\\mathbb{{R}}$$")
    for i in range(3): num(w, f"({B[i]})-({A[i]})", u[i], "u")
    w.say(f"ខ. ជំនួសកូអរដោនេ $M$ ក្នុងសមីការនីមួយៗ ៖")
    vals = []
    for s, a, c, m in zip("xyz", A, u, M):
        if c == 0:
            w.say(f"$${T(m)}={T(a)}$$ " + ("ពិត ។" if m == a else "មិនពិត ។")); vals.append(None if m == a else "bad")
        else:
            tv = sp.Rational(m - a, c); vals.append(tv); w.say(f"$${T(m)}={T(a)}{st(c) if abs(c)!=1 else ('+' if c>0 else '-')}t\\Rightarrow t={T(tv)}$$".replace("+t", "+t").replace("{st(c)}", "")); num(w, f"(({m})-({a}))/({c})", tv, "t")
    ts_ = [v for v in vals if v is not None]
    ok = "bad" not in ts_ and len(set(ts_)) <= 1
    assert ok == on
    if ok: w.say(f"តម្លៃ $t$ ដូចគ្នា ដូច្នេះ $M$ ស្ថិតនៅលើបន្ទាត់ $(AB)$ ។"); ans = "M\\in(AB)"
    else: w.say("តម្លៃ $t$ មិនដូចគ្នា ដូច្នេះ $M$ មិនស្ថិតនៅលើបន្ទាត់ $(AB)$ ទេ ។"); ans = "M\\notin(AB)"
    w.say(f"ដូចនេះ $\\boxed{{(AB):{param_t(A, u)}\\,,\\ {ans}}}$ ។")
    return row(w, CH, "space_line", "line_parametric_point_test", "medium", P, ans, "line_param")
def dist_plane(rng):
    n = rpt(rng, -4, 5)
    if n == (0, 0, 0): return None
    d = sp.Integer(rng.randint(-9, 9)); M = rpt(rng); w = W(rng); val = dot(n, M) + d; n2 = norm2(n); D = sp.radsimp(sp.Abs(val) / sp.sqrt(n2))
    P = FRAME + f"គេឱ្យប្លង់ $(\\alpha):{plane_t(n, d)}$ និងចំណុច $M{P3(M)}$ ។ គណនាចម្ងាយពីចំណុច $M$ ទៅប្លង់ $(\\alpha)$ ។"
    w.say("ចម្ងាយពីចំណុច $M(x_0;y_0;z_0)$ ទៅប្លង់ $ax+by+cz+d=0$ គឺ $$d\\left(M,(\\alpha)\\right)=\\frac{\\left|ax_0+by_0+cz_0+d\\right|}{\\sqrt{a^2+b^2+c^2}}$$")
    w.say(f"$$d\\left(M,(\\alpha)\\right)=\\frac{{\\left|{dot_line(n, M)}{st(d)}\\right|}}{{\\sqrt{{{sum_sq(n)}}}}}=\\frac{{{abs(val)}}}{{{sqrt_t(n2)}}}" + ("" if T(D) == f"\\frac{{{abs(val)}}}{{{sqrt_t(n2)}}}" else f"={T(D)}") + "$$")
    w.C.append(check(f"Abs(({n[0]})*({M[0]})+({n[1]})*({M[1]})+({n[2]})*({M[2]})+({d}))/sqrt({n2})", D, "dist"))
    if val == 0: w.say("ចម្ងាយស្មើ $0$ មានន័យថា $M$ ស្ថិតនៅលើប្លង់ ។")
    w.say(f"ដូចនេះ $\\boxed{{d\\left(M,(\\alpha)\\right)={T(D)}}}$ ។")
    return row(w, CH, "space_distance", "distance_point_plane", "easy", P, T(D), "dist_plane")
def line_plane(rng):
    n = rpt(rng, -3, 4); A = rpt(rng); u = rpt(rng, -3, 4)
    if n == (0, 0, 0) or u == (0, 0, 0): return None
    k = dot(n, u)
    if k == 0: return None
    t0 = rng.choice([-2, -1, 1, 2, 3]); Mp = tuple(a + t0 * c for a, c in zip(A, u)); d = -dot(n, Mp)
    w = W(rng); ts = sp.Symbol("t")
    P = FRAME + f"គេឱ្យបន្ទាត់ $(d):{param_t(A, u)}\\ ,\\ t\\in\\mathbb{{R}}$ និងប្លង់ $(\\alpha):{plane_t(n, d)}$ ។ រកកូអរដោនេនៃចំណុចប្រសព្វ $I$ រវាង $(d)$ និង $(\\alpha)$ ។"
    w.say("ជំនួស $x\\,,\\,y\\,,\\,z$ ពីសមីការ $(d)$ ក្នុងសមីការ $(\\alpha)$ ៖")
    parts = "+".join(f"{ppx(c) if c!=1 else ''}\\left({T(sp.expand(a + q * ts))}\\right)" for c, a, q in zip(n, A, u) if c != 0).replace("+-", "-")
    w.say(f"$${parts}{st(d)}=0$$"); lin_ = sp.expand(sum(c * (a + q * ts) for c, a, q in zip(n, A, u)) + d)
    w.say(f"$${T(lin_)}=0\\Rightarrow t={T(t0)}$$"); assert sp.solve(lin_, ts) == [t0]
    w.C.append(check(f"({n[0]})*(({A[0]})+({u[0]})*({t0}))+({n[1]})*(({A[1]})+({u[1]})*({t0}))+({n[2]})*(({A[2]})+({u[2]})*({t0}))+({d})", 0, "t"))
    w.say(f"ជំនួស $t={T(t0)}$ ក្នុង $(d)$ ៖ $$x={T(A[0])}{st(u[0]*t0)}={T(Mp[0])}\\,,\\ y={T(A[1])}{st(u[1]*t0)}={T(Mp[1])}\\,,\\ z={T(A[2])}{st(u[2]*t0)}={T(Mp[2])}$$")
    for i in range(3): num(w, f"({A[i]})+({u[i]})*({t0})", Mp[i], "I")
    w.say(f"ដូចនេះ $\\boxed{{I{P3(Mp)}}}$ ។")
    return row(w, CH, "space_line", "line_plane_intersection", "medium", P, f"I{P3(Mp)}", "line_plane")
def coplanar(rng):
    t = three_pts(rng)
    if not t: return None
    A, B, C = t; u, v = sub(B, A), sub(C, A); c = cross(u, v); on = rng.random() < 0.5
    if on:
        a, b = rng.choice([(1, 1), (2, -1), (-1, 2), (1, -2), (3, 1)]); D = tuple(A[i] + a * u[i] + b * v[i] for i in range(3))
    else:
        D = rpt(rng)
    s = sub(D, A); m = dot(c, s)
    if (m == 0) != on: return None
    w = W(rng)
    P = FRAME + f"គេឱ្យចំណុច $A{P3(A)}\\,,\\ B{P3(B)}\\,,\\ C{P3(C)}$ និង $D{P3(D)}$ ។ តើចំណុចទាំងបួននៅលើប្លង់តែមួយឬទេ ?"
    w.say(f"$\\vec{{AB}}={P3(u)}\\,,\\ \\vec{{AC}}={P3(v)}\\,,\\ \\vec{{AD}}={P3(s)}$ ។"); cross_lines(w, u, v, "AB", "AC")
    w.say(f"$$\\left(\\vec{{AB}}\\wedge\\vec{{AC}}\\right)\\cdot\\vec{{AD}}={dot_line(c, s)}={T(m)}$$"); w.C.append(check("+".join(f"({p})*({q})" for p, q in zip(c, s)), m, "triple"))
    if on: w.say("ផលគុណចម្រុះស្មើ $0$ ដូច្នេះវ៉ិចទ័រទាំងបីនៅលើប្លង់តែមួយ ។"); w.say("ដូចនេះ $\\boxed{A\\,,\\,B\\,,\\,C\\,,\\,D\\ \\text{នៅលើប្លង់តែមួយ}}$ ។"); ans = "yes"
    else: w.say("ផលគុណចម្រុះខុសពី $0$ ។"); w.say("ដូចនេះ $\\boxed{A\\,,\\,B\\,,\\,C\\,,\\,D\\ \\text{មិននៅលើប្លង់តែមួយ}}$ ទេ ។"); ans = "no"
    return row(w, CH, "space_product", "four_points_coplanar", "medium", P, ans, "coplanar")
def dist_line(rng):
    A = rpt(rng); u = rpt(rng, -3, 4); M = rpt(rng)
    if u == (0, 0, 0): return None
    AM = sub(M, A); c = cross(AM, u)
    if c == (0, 0, 0): return None
    w = W(rng); n2c, n2u = norm2(c), norm2(u); D = sp.radsimp(sp.sqrt(n2c) / sp.sqrt(n2u))
    P = FRAME + f"គេឱ្យបន្ទាត់ $(d)$ កាត់តាម $A{P3(A)}$ មានវ៉ិចទ័រប្រាប់ទិស $\\vec{{u}}={P3(u)}$ និងចំណុច $M{P3(M)}$ ។ គណនាចម្ងាយពី $M$ ទៅបន្ទាត់ $(d)$ ។"
    w.say("ចម្ងាយពី $M$ ទៅបន្ទាត់ $(d)$ គឺ $$d\\left(M,(d)\\right)=\\frac{\\left\\|\\vec{AM}\\wedge\\vec{u}\\right\\|}{\\|\\vec{u}\\|}$$")
    w.say(f"$\\vec{{AM}}={P3(AM)}$ ។"); cross_lines(w, AM, u, "AM", "u")
    w.say(f"$$\\left\\|\\vec{{AM}}\\wedge\\vec{{u}}\\right\\|=\\sqrt{{{sum_sq(c)}}}={sqrt_t(n2c)}\\,,\\quad\\|\\vec{{u}}\\|=\\sqrt{{{sum_sq(u)}}}={sqrt_t(n2u)}$$")
    w.say(f"$$d\\left(M,(d)\\right)=\\frac{{{sqrt_t(n2c)}}}{{{sqrt_t(n2u)}}}={T(D)}$$"); w.C.append(check(f"sqrt({n2c})/sqrt({n2u})", D, "dist"))
    w.say(f"ដូចនេះ $\\boxed{{d\\left(M,(d)\\right)={T(D)}}}$ ។")
    return row(w, CH, "space_distance", "distance_point_line", "bacii", P, T(D), "dist_line")
def plane_angle(rng):
    n1, n2 = rpt(rng, -3, 4), rpt(rng, -3, 4)
    if norm2(n1) == 0 or norm2(n2) == 0 or cross(n1, n2) == (0, 0, 0): return None
    d1, d2 = sp.Integer(rng.randint(-6, 6)), sp.Integer(rng.randint(-6, 6)); w = W(rng); dt = dot(n1, n2)
    cs = sp.radsimp(sp.Abs(dt) / (sp.sqrt(norm2(n1)) * sp.sqrt(norm2(n2))))
    P = FRAME + f"គេឱ្យប្លង់ $(P):{plane_t(n1, d1)}$ និង $(Q):{plane_t(n2, d2)}$ ។ គណនា $\\cos\\varphi$ ដែល $\\varphi$ ជាមុំរវាងប្លង់ទាំងពីរ ។ តើប្លង់ទាំងពីរកែងគ្នាឬទេ ?"
    w.say(f"វ៉ិចទ័រណរម៉ាល់ ៖ $\\vec{{n_1}}={P3(n1)}$ និង $\\vec{{n_2}}={P3(n2)}$ ។")
    w.say(f"$$\\vec{{n_1}}\\cdot\\vec{{n_2}}={dot_line(n1, n2)}={T(dt)}$$"); w.C.append(check("+".join(f"({a})*({b})" for a, b in zip(n1, n2)), dt, "dot"))
    w.say(f"$$\\cos\\varphi=\\frac{{\\left|\\vec{{n_1}}\\cdot\\vec{{n_2}}\\right|}}{{\\|\\vec{{n_1}}\\|\\,\\|\\vec{{n_2}}\\|}}=\\frac{{{abs(dt)}}}{{{sqrt_t(norm2(n1))}\\times{sqrt_t(norm2(n2))}}}={T(cs)}$$"); w.C.append(check(f"Abs({dt})/(sqrt({norm2(n1)})*sqrt({norm2(n2)}))", cs, "cos"))
    if dt == 0: w.say("ដោយ $\\vec{n_1}\\cdot\\vec{n_2}=0$ នោះប្លង់ទាំងពីរកែងគ្នា ។"); tail = "(P)\\perp(Q)"
    else: w.say("ដោយ $\\vec{n_1}\\cdot\\vec{n_2}\\neq0$ នោះប្លង់ទាំងពីរមិនកែងគ្នាទេ ។"); tail = f"\\cos\\varphi={T(cs)}"
    w.say(f"ដូចនេះ $\\boxed{{{tail}}}$ ។")
    return row(w, CH, "space_plane", "angle_between_planes", "medium", P, tail, "plane_angle")
ALL = [(vec_basic, 1300), (dot_angle, 1300), (cross_area, 1300), (volume, 1300), (plane3, 1400), (plane_pn, 1200),
       (line_param, 1200), (dist_plane, 1200), (line_plane, 1300), (coplanar, 1100), (dist_line, 1100), (plane_angle, 1100)]
