"""Applications of the derivative: optimization, motion, rates, related rates, limits,
differentials, Rolle and mean value theorem. Writes out/applications.jsonl. All rows original."""
import random, sys, os, hashlib, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from common import make_row as _make_row
from variation_hand import tidy_row, fnpow, boxed
def make_row(*a, **k):
    return tidy_row(_make_row(*a, **k))

GEN = "applications"; TOPIC = "applications"
rng = random.Random(20261105)
Q = sp.Rational
PI = sp.pi
rows = []; seen = set(); png = [0]
PNG_MAX = 280

PEOPLE = ["សុខា", "ដារ៉ា", "វណ្ណា", "ចន្ថា", "សុភា", "បូរ៉ា", "រតនា", "ពិសី", "វិបុល", "សំណាង", "ម៉ាលី", "សុវណ្ណ", "ធារី", "ពៅ", "លោកតា សុខ", "អ្នកស្រី សុផល", "លោក វុទ្ធី", "កញ្ញា ស្រីនាង"]
PLACES = ["ភ្នំពេញ", "សៀមរាប", "បាត់ដំបង", "កំពត", "កែប", "កំពង់ចាម", "តាកែវ", "ព្រៃវែង", "ពោធិ៍សាត់", "កណ្ដាល", "មណ្ឌលគិរី", "ស្វាយរៀង", "កំពង់ធំ", "ក្រចេះ"]

def P(*o): return rng.choice(o)
def sv(v): return sp.Symbol(v, real=True)
def L(e, v=None):
    if v and v != "x" and hasattr(e, "subs"): e = sp.sympify(e).subs(x, sv(v))
    return re.sub(r"\\(sin|cos|tan|ln)\{\\left\(([a-z]|\d+) \\right\)\}", r"\\\1 \2", fnpow(lx(sp.sympify(e))))
def M(e, v=None): return "$" + L(e, v) + "$"
def BOX(t): return "$$\\boxed{" + t + "}$$"
def DM(t): return "$$" + t + "$$"
def st(e): return str(sp.sympify(e))
def dchk(F, Fp, note="ដេរីវេ"): return check(f"diff({st(F)},x)", st(Fp), note)
def vchk(F, c, val, note="តម្លៃ"): return check(f"({st(F)}).subs(x,{st(c)})", st(val), note)
def d0chk(F, c): return check(f"diff({st(F)},x).subs(x,{st(c)})", "0", "ចំណុចបរមា")
def fin(): return P("ដូចនេះ", "ដូចនេះ", "ដូចនេះ", "សរុបមក", "ដូច្នេះ")
def gb(): return P("យើងបាន", "គេបាន", "គេបាន", "យើងបាន")
def num(v):
    v = sp.simplify(v)
    return v

def add(sub, diff, key, prob, sol, ans, checks, diagrams=None):
    k = (sub, str(key))
    if k in seen: return False
    prob = re.sub(r"\\n(?=[កខគ]\.)", "\n", prob)
    sol = "\n".join(p.strip() for p in re.split(r"(\$\$.*?\$\$)", sol, flags=re.S) if p.strip())
    seen.add(k)
    bx = boxed(sol)
    if bx: ans = ",\\ ".join(bx)
    rid = TOPIC + "-" + hashlib.sha1(prob.encode()).hexdigest()[:10]
    if any(r["id"] == rid for r in rows[-400:]): return False
    if callable(diagrams): diagrams = diagrams(rid)
    rows.append(make_row(TOPIC, sub, diff, prob, sol, ans, checks, GEN, diagrams or [], row_id=rid))
    return True

def run(g, n, tries=None):
    start = len(rows); t = 0
    while len(rows) - start < n and t < (tries or n * 12):
        t += 1
        g()
    print(f"{g.__name__}: {len(rows)-start}")

def vt(v, name, cols, fp, fv):
    t = variation_table(cols, fp, fv, name)
    return (t.replace("\nx & ", "\n" + v + " & ").replace("{array}{c|", "{array}{c|").replace(name + "'(x)", f"{name}'({v})")
             .replace(name + "(x)", f"{name}({v})"))

def vdiag(tab, alt): return {"type": "variation_table", "latex": tab, "image": None, "alt_km": alt}
def fig(tex, alt): return {"type": "figure", "latex": tex, "image": None, "alt_km": alt}

def pgf(f):
    t = str(f).replace("**", "^").replace("log(", "ln(")
    t = re.sub(r"(sin|cos|tan)\(", lambda mo: mo.group(1) + "(deg(1)*", t)
    return t

def graph(rid, f, a, b, lo, hi, alt, var="x", yname="y", pts=()):
    """pgfplots source always; PNG while the budget lasts."""
    tex = tikz_graph(pgf(f), a, b, lo, hi).replace("xlabel=$x$", f"xlabel=${var}$").replace("ylabel=$y$", f"ylabel=${yname}$")
    img = None
    if png[0] < PNG_MAX:
        img = plot_png(rid, f, float(a), float(b), float(lo), float(hi), points=pts); png[0] += 1
    return {"type": "graph", "latex": tex, "image": img, "alt_km": alt}

def endval(F, p):
    if p in (sp.oo, -sp.oo): return sp.limit(F, x, p)
    try:
        v = F.subs(x, p)
        if v.has(sp.zoo, sp.nan, sp.oo, -sp.oo): raise ValueError
        return v
    except Exception:
        return sp.limit(F, x, p, "+" if p == 0 else "-")

def sval(e):
    """Exact value. A logarithm stays symbolic: 49 ln 7, never ln of a 42-digit integer."""
    return sp.expand(e) if sp.sympify(e).has(sp.log) else sp.simplify(sp.simplify(e))

def tail(F, name, v, lo, hi, c, kind, Fpf=None, solve=None, style=None, noun="អនុគមន៍"):
    """Derivative, critical point and justification. Returns text, diagrams, checks, value."""
    Fp = sp.diff(F, x); F2 = sp.diff(Fp, x)
    val = sval(F.subs(x, c))
    assert sp.simplify(Fp.subs(x, c)) == 0, (F, c)
    a0 = float(lo) if lo != -sp.oo else float(c) - 1
    b0 = float(hi) if hi != sp.oo else float(c) + 1
    l, r = (a0 + float(c)) / 2, (b0 + float(c)) / 2
    sl, sr = float(Fp.subs(x, l)), float(Fp.subs(x, r))
    assert (sl > 0 > sr) if kind == "max" else (sl < 0 < sr), (F, c, sl, sr)
    fs = Fpf or L(sp.together(Fp) if F.is_rational_function(x) and not F.is_polynomial(x) else Fp, v)
    txt = [P(f"គណនាដេរីវេ ៖", f"ធ្វើដេរីវេនៃ ${name}$ ធៀបនឹង ${v}$ ៖", f"យើងគណនាដេរីវេទី១ ៖", f"ដេរីវេទី១នៃ ${name}$ គឺ ៖")]
    txt.append(DM(f"{name}'({v})={fs}"))
    txt.append(solve or P(f"បើ ${name}'({v})=0$ នោះ ${v}={L(c)}$ ។", f"ដោះស្រាយសមីការ ${name}'({v})=0$ គេបាន ${v}={L(c)}$ ។", f"${name}'({v})=0$ លុះត្រាតែ ${v}={L(c)}$ ។"))
    chk = [dchk(F, Fp), d0chk(F, c), vchk(F, c, val, "តម្លៃបរមា")]
    style = style or P("table", "table", "second", "sign")
    dg = []
    word = "អតិបរមា" if kind == "max" else "អប្បបរមា"
    if style == "second":
        s2 = sp.simplify(sp.simplify(F2.subs(x, c)))
        if s2 == 0 or (kind == "max") != (s2 < 0): style = "table"
        else:
            txt.append(f"ដេរីវេទី២ ៖ ${name}''({v})={L(sp.expand(F2) if F.is_polynomial(x) else F2, v)}$ ។")
            txt.append(f"ត្រង់ ${v}={L(c)}$ គេបាន ${name}''({L(c)})={L(s2)}{'<0' if kind == 'max' else '>0'}$ នោះ ${name}$ មាន{word}ត្រង់ចំណុចនេះ ។")
            chk.append(check(f"diff({st(F)},x,2).subs(x,{st(c)})", st(s2), "ដេរីវេទី២"))
    if style == "sign":
        a, b = ("<", ">") if kind == "min" else (">", "<")
        lt = f"${L(lo)}<{v}<{L(c)}$" if lo != -sp.oo else f"${v}<{L(c)}$"
        rt = f"${L(c)}<{v}<{L(hi)}$" if hi != sp.oo else f"${v}>{L(c)}$"
        txt.append(f"ចំពោះ {lt} គេបាន ${name}'({v}){a}0$ ហើយចំពោះ {rt} គេបាន ${name}'({v}){b}0$ ។")
        txt.append(f"នាំឲ្យ ${name}$ មាន{word}ត្រង់ ${v}={L(c)}$ ។")
    if style == "table":
        cl = "-\\infty" if lo == -sp.oo else L(lo)
        ch = "+\\infty" if hi == sp.oo else L(hi)
        el, eh = endval(F, lo), endval(F, hi)
        s1, s2_ = ("+", "-") if kind == "max" else ("-", "+")
        ar1, ar2 = ("\\nearrow", "\\searrow") if kind == "max" else ("\\searrow", "\\nearrow")
        ls = lambda e: "+\\infty" if e == sp.oo else ("-\\infty" if e == -sp.oo else L(sval(e)))
        tab = vt(v, name, [cl, L(c), ch], ["", s1, "0", s2_, ""], [ls(el), ar1, L(val), ar2, ls(eh)])
        txt.append(P("តារាងអថេរភាព ៖", f"តារាងអថេរភាពនៃ ${name}$ លើចន្លោះនេះ ៖", f"សញ្ញានៃ ${name}'({v})$ ឲ្យតារាងអថេរភាពដូចខាងក្រោម ៖"))
        txt.append(DM(tab))
        txt.append(f"តាមតារាង ${name}$ មាន{word}ត្រង់ ${v}={L(c)}$ ។")
        dg.append(vdiag(tab, f"តារាងអថេរភាពនៃ ${name}$ បង្ហាញ{word}ត្រង់ ${v}={L(c)}$"))
    return "\n".join(txt), dg, chk, val

# ---- simple figures (labels are math only) ----
def fig_fence(a, b):
    return ("\\begin{tikzpicture}\n\\draw[thick] (0,0) rectangle (4,2);\n\\node[below] at (2,0) {$" + a + "$};\n\\node[left] at (0,1) {$" + b + "$};\n\\end{tikzpicture}")
def fig_box(a, cut):
    return ("\\begin{tikzpicture}\n\\draw[thick] (0,0) rectangle (4,4);\n\\draw[dashed] (0.7,0.7) rectangle (3.3,3.3);\n\\foreach \\p in {(0,0),(3.3,0),(0,3.3),(3.3,3.3)} \\fill[gray!30] \\p rectangle ++(0.7,0.7);\n\\node[below] at (2,0) {$" + a + "$};\n\\node[left] at (0,0.35) {$" + cut + "$};\n\\end{tikzpicture}")
def fig_tri(a, b, c):
    return ("\\begin{tikzpicture}\n\\draw[thick] (0,0) -- (3,0) -- (0,4) -- cycle;\n\\node[below] at (1.5,0) {$" + a + "$};\n\\node[left] at (0,2) {$" + b + "$};\n\\node[right] at (1.5,2.1) {$" + c + "$};\n\\draw (0,0.25) -- (0.25,0.25) -- (0.25,0);\n\\end{tikzpicture}")
def fig_cone(r, h):
    return ("\\begin{tikzpicture}\n\\draw[thick] (-1.5,3) -- (0,0) -- (1.5,3);\n\\draw[thick] (0,3) ellipse (1.5 and 0.3);\n\\draw[dashed] (0,0) -- (0,3);\n\\node[right] at (0,1.5) {$" + h + "$};\n\\node[above] at (0.75,3) {$" + r + "$};\n\\end{tikzpicture}")

# =============================== OPTIMIZATION ===============================
FENCE_CTX = [("ទន្លេមេគង្គ", "របងលួស", "ចិញ្ចឹមមាន់"), ("ប្រឡាយទឹក", "របងឫស្សី", "ដាំបន្លែ"), ("ជញ្ជាំងផ្ទះ", "របងឈើ", "ដាំផ្កា"),
             ("បឹងទន្លេសាប", "សំណាញ់", "ចិញ្ចឹមទា"), ("ជញ្ជាំងសាលា", "របងឈើ", "ធ្វើសួនបន្លែ"), ("ទន្លេបាសាក់", "របងលួស", "ចិញ្ចឹមគោ"), ("ស្ទឹងសង្កែ", "របងឫស្សី", "ដាំស្វាយ")]

def g_fence_area():
    a, b = P((2, 1), (2, 1), (2, 2), (3, 2), (4, 2), (3, 1))
    Lf = rng.choice(range(24, 481, 12)) * a // 2 * 2
    if Lf % (2 * a) or Lf % (2 * b): return
    pn = P(*PEOPLE); bar, fen, use = P(*FENCE_CTX)
    w = sp.Symbol("w")
    y_of = (Lf - a * x) / b
    A = x * (Lf - a * x) / b
    c = Q(Lf, 2 * a); hi = Q(Lf, a)
    if (a, b) == (2, 1):
        desc = f"ដីរាងចតុកោណកែងមួយនៅជាប់{bar} ដោយមិនចាំបាច់ធ្វើរបងនៅផ្នែកជាប់{bar}នោះទេ"
        rel = f"$2x+y={Lf}$"; xn = f"ទទឹង (ជ្រុងកែងនឹង{bar})"; yn = "បណ្តោយ (ជ្រុងស្របនឹង" + bar + ")"
    elif (a, b) == (2, 2):
        desc = "ដីរាងចតុកោណកែងមួយ ដោយព័ទ្ធជុំវិញទាំងបួនជ្រុង"
        rel = f"$2x+2y={Lf}$"; xn = "ទទឹង"; yn = "បណ្តោយ"
    elif (a, b) == (3, 2):
        desc = "ដីរាងចតុកោណកែងមួយ ដោយព័ទ្ធជុំវិញ ហើយខណ្ឌដីជាពីរផ្នែកដោយរបងមួយខ្សែស្របនឹងជ្រុងទទឹង"
        rel = f"$3x+2y={Lf}$"; xn = "ទទឹង"; yn = "បណ្តោយ"
    elif (a, b) == (4, 2):
        desc = "ដីរាងចតុកោណកែងមួយ ដោយព័ទ្ធជុំវិញ ហើយខណ្ឌដីជាបីផ្នែកដោយរបងពីរខ្សែស្របនឹងជ្រុងទទឹង"
        rel = f"$4x+2y={Lf}$"; xn = "ទទឹង"; yn = "បណ្តោយ"
    else:
        desc = f"ដីរាងចតុកោណកែងមួយជាប់{bar} (មិនធ្វើរបងផ្នែកជាប់{bar}) ហើយខណ្ឌជាពីរផ្នែកដោយរបងមួយខ្សែកែងនឹង{bar}"
        rel = f"$3x+y={Lf}$"; xn = f"ជ្រុងកែងនឹង{bar}"; yn = f"ជ្រុងស្របនឹង{bar}"
    prob = P(f"{pn}មាន{fen}ប្រវែង ${Lf}$ ម៉ែត្រ សម្រាប់ព័ទ្ធ{desc} ដើម្បី{use} ។ ចូរកំណត់វិមាត្រនៃដីនោះ ដើម្បីឲ្យក្រឡាផ្ទៃធំបំផុត រួចគណនាក្រឡាផ្ទៃនោះ ។",
             f"ដើម្បី{use} {pn}ចង់ប្រើ{fen}ដែលមានប្រវែងសរុប ${Lf}$ ម៉ែត្រ ព័ទ្ធ{desc} ។ តើត្រូវយកវិមាត្រប៉ុន្មាន ទើបក្រឡាផ្ទៃដីមានតម្លៃអតិបរមា? តើក្រឡាផ្ទៃអតិបរមានោះស្មើប៉ុន្មាន?",
             f"គេប្រើ{fen}សរុប ${Lf}$ ម៉ែត្រ ព័ទ្ធ{desc} ។ រកបណ្តោយនិងទទឹងដែលធ្វើឲ្យក្រឡាផ្ទៃធំជាងគេ ។")
    t, dg, ck, val = tail(A, "S", "x", 0, hi, c, "max", Fpf=L(sp.expand(sp.diff(A, x))))
    yv = y_of.subs(x, c)
    sol = (P(f"តាង $x$ ជា{xn} និង $y$ ជា{yn} (គិតជាម៉ែត្រ) ដែល $x>0$ និង $y>0$ ។\n", f"ឧបមាថា{xn}មានប្រវែង $x$ ម៉ែត្រ ហើយ{yn}មានប្រវែង $y$ ម៉ែត្រ ($x>0,\\ y>0$) ។\n")
           + f"ប្រវែងរបងសរុបឲ្យ {rel} នាំឲ្យ $y={L(y_of)}$ ។\n"
           + f"លក្ខខណ្ឌ $y>0$ ឲ្យ $0<x<{L(hi)}$ ។\n"
           + f"ក្រឡាផ្ទៃដីជាអនុគមន៍នៃ $x$ ៖\n" + DM(f"S(x)=xy={L(sp.expand(A))}") + t + "\n"
           + f"ពេលនោះ $y={L(yv)}$ និង $S={L(val)}$ ។\n"
           + f"{fin()} ដីត្រូវមាន $x={L(c)}$ ម៉ែត្រ និង $y={L(yv)}$ ម៉ែត្រ ហើយក្រឡាផ្ទៃអតិបរមាគឺ ៖\n" + BOX(f"S_{{\\max}}={L(val)}") + "ម៉ែត្រការ៉េ ។")
    ck.append(vchk(y_of, c, yv, "វិមាត្រ"))
    dgs = dg + [fig(fig_fence("y", "x"), "រូបចតុកោណកែងនៃដី មានជ្រុង x និង y")]
    add("optimization_fence", P("easy", "medium"), (a, b, Lf), prob, sol, f"x={L(c)},\\ y={L(yv)},\\ S_{{\\max}}={L(val)}", ck, dgs)

def g_fence_min():
    a, b = P((2, 1), (1, 1), (3, 1), (3, 2))
    xs = rng.randint(4, 40)
    Ar = a * xs * xs if b == 1 else a * xs * xs // b
    if b == 2 and (a * xs * xs) % 2: return
    p1, p2 = 1, 1
    cost = rng.random() < .55
    if cost:
        p1 = rng.randint(2, 9); p2 = P(1, 2, 3, 4, 5, 6)
        # cost = a*p1*x + b*p2*y with y=Ar/x
        val2 = sp.Rational(b * p2 * Ar, a * p1)
        r = sp.sqrt(val2)
        if not r.is_rational: return
        c = r
    else:
        c = sp.sqrt(sp.Rational(b * Ar, a))
    C = a * p1 * x + b * p2 * Ar / x
    pn = P(*PEOPLE)
    place = P(*PLACES)
    if (a, b) == (2, 1): sh = "មួយជ្រុងនៅជាប់ជញ្ជាំងស្រាប់ មិនចាំបាច់ធ្វើរបង"; rel = "2x+y"
    elif (a, b) == (1, 1): sh = "ជ្រុងពីរជាប់គ្នានៅជាប់ជញ្ជាំងស្រាប់ មិនចាំបាច់ធ្វើរបង"; rel = "x+y"
    elif (a, b) == (3, 1): sh = "មួយជ្រុងនៅជាប់ប្រឡាយ មិនធ្វើរបង ហើយមានរបងមួយខ្សែបែងចែកដីជាពីរស្របនឹងជ្រុង $x$"; rel = "3x+y"
    else: sh = "ព័ទ្ធជុំវិញទាំងអស់ ហើយមានរបងមួយខ្សែបែងចែកដីជាពីរស្របនឹងជ្រុង $x$"; rel = "3x+2y"
    if cost:
        costdesc = f"របងស្របនឹងជ្រុង $x$ ថ្លៃ ${p1}$ ដុល្លារក្នុងមួយម៉ែត្រ ហើយរបងស្របនឹងជ្រុង $y$ ថ្លៃ ${p2}$ ដុល្លារក្នុងមួយម៉ែត្រ ។ "
        ask = P("រកវិមាត្រ $x$ និង $y$ ដើម្បីឲ្យចំណាយលើរបងតិចបំផុត ។", "តើត្រូវយក $x$ និង $y$ ប៉ុន្មាន ទើបថ្លៃរបងសរុបមានតម្លៃអប្បបរមា?")
    else:
        costdesc = ""
        ask = P("រកវិមាត្រ $x$ និង $y$ ដើម្បីឲ្យប្រវែងរបងខ្លីបំផុត ។", "តើវិមាត្រប៉ុន្មានដែលត្រូវប្រើរបងតិចជាងគេ?")
    prob = f"{pn}មានដីនៅ{place} ហើយចង់ព័ទ្ធដីរាងចតុកោណកែងវិមាត្រ $x$ និង $y$ ម៉ែត្រ ដែលមានក្រឡាផ្ទៃ ${Ar}$ ម៉ែត្រការ៉េ ដោយ{sh} ។ {costdesc}{ask}"
    nm = "C" if cost else "L"
    t, dg, ck, val = tail(C, nm, "x", 0, sp.oo, c, "min", Fpf=f"{a*p1}-\\frac{{{b*p2*Ar}}}{{x^2}}", style=P("table", "second", "sign"),
                          solve=f"${nm}'(x)=0$ នាំឲ្យ $x^2={L(c**2)}$ ហើយដោយ $x>0$ នោះ $x={L(c)}$ ។")
    yv = sp.Rational(Ar) / c
    lead = (f"ក្រឡាផ្ទៃ $xy={Ar}$ នាំឲ្យ $y=\\frac{{{Ar}}}{{x}}$ ដែល $x>0$ ។\n")
    obj = (f"ថ្លៃរបងសរុប (គិតជាដុល្លារ) ៖\n" + DM(f"C(x)={a}\\cdot{p1}\\,x+{b}\\cdot{p2}\\,y={a*p1}x+\\frac{{{b*p2*Ar}}}{{x}}") if cost else
           f"ប្រវែងរបងសរុប ៖\n" + DM(f"L(x)={rel}={a}x+\\frac{{{b*Ar}}}{{x}}".replace("=1x", "=x")))
    sol = lead + obj + t + f"\nពេលនោះ $y=\\frac{{{Ar}}}{{{L(c)}}}={L(yv)}$ ។\n{fin()} វិមាត្រត្រូវយកគឺ ៖\n" + BOX(f"x={L(c)},\\quad y={L(yv)}") + (f"ហើយថ្លៃអប្បបរមាគឺ ${L(val)}$ ដុល្លារ ។" if cost else f"ហើយប្រវែងរបងខ្លីបំផុតគឺ ${L(val)}$ ម៉ែត្រ ។")
    add("optimization_fence", P("medium", "medium", "hard"), ("min", a, b, Ar, p1, p2), prob, sol, f"x={L(c)},\\ y={L(yv)}", ck, dg + [fig(fig_fence("y", "x"), "ដីរាងចតុកោណកែង")])

BOXMAT = ["សន្លឹកក្រដាសកាតុង", "បន្ទះស័ង្កសី", "បន្ទះដែកស្តើង", "សន្លឹកកាតុង"]
BOXUSE = ["ធ្វើប្រអប់ដាក់នំ", "ធ្វើប្រអប់ដាក់ម្រេចកំពត", "ធ្វើថាសដាក់ត្រី", "ធ្វើប្រអប់ដាក់សម្ភារៈសិក្សា", "ធ្វើធុងដាក់ស្ករត្នោត"]
TRIP = [(3, 8), (5, 8), (7, 15), (8, 15), (5, 21), (16, 21), (1, 1), (7, 40), (33, 40)]
def g_box():
    a0, b0 = P(*TRIP); k = rng.randint(1, 8)
    if a0 == b0: k = rng.randint(1, 30)
    a, b = 6 * a0 * k // (2 if rng.random() < .3 and k % 2 == 0 else 1), 0
    b = a * b0 // a0
    if a > 200 or b > 200: return
    roots = sp.Poly(12 * x**2 - 4 * (a + b) * x + a * b, x).all_roots()
    c = min(roots)
    if not c.is_rational: return
    hi = Q(min(a, b), 2)
    V = x * (a - 2 * x) * (b - 2 * x)
    mat = P(*BOXMAT); use = P(*BOXUSE); pn = P(*PEOPLE)
    sq = a == b
    dim = f"រាងការ៉េជ្រុង ${a}$ សង់ទីម៉ែត្រ" if sq else f"រាងចតុកោណកែងវិមាត្រ ${a}$ សង់ទីម៉ែត្រ និង ${b}$ សង់ទីម៉ែត្រ"
    prob = P(f"{pn}មាន{mat}{dim} ។ គាត់កាត់ការ៉េស្មើគ្នាជ្រុង $x$ សង់ទីម៉ែត្រចេញពីជ្រុងទាំងបួន រួចបត់ឡើង ដើម្បី{use}គ្មានគម្រប ។ រក $x$ ដើម្បីឲ្យមាឌប្រអប់ធំបំផុត ។",
             f"ពី{mat}{dim} គេកាត់ការ៉េតូចៗស្មើគ្នានៅកាច់ជ្រុងទាំងបួន ហើយបត់ជាប្រអប់បើកចំហខាងលើ ។ តើជ្រុងការ៉េដែលកាត់ត្រូវមានប្រវែងប៉ុន្មាន ទើបមាឌប្រអប់អតិបរមា? គណនាមាឌនោះ ។",
             f"ដើម្បី{use} គេប្រើ{mat}{dim} ដោយកាត់កាច់ជ្រុងទាំងបួនជារាងការ៉េ រួចបត់ជ្រុង ។ ចូរកំណត់ទំហំការ៉េដែលកាត់ ដើម្បីឲ្យប្រអប់ផ្ទុកបានច្រើនបំផុត ។")
    Fp = sp.expand(sp.diff(V, x))
    other = max(roots)
    if sq:
        fac = f"{L(a-2*x)}"
        solve = f"$V'(x)=({L(a-2*x)})({L(a-6*x)})$ ។ ក្នុងចន្លោះ $0<x<{L(hi)}$ គេបាន $V'(x)=0$ លុះត្រាតែ $x={L(c)}$ (ចំណែក $x={L(hi)}$ មិនយកព្រោះនៅចុងចន្លោះ) ។"
    else:
        solve = f"$V'(x)=0$ មានឫស $x_1={L(c)}$ និង $x_2={L(other)}$ ។ ដោយ $0<x<{L(hi)}$ គេយកតែ $x={L(c)}$ ។"
    t, dg, ck, val = tail(V, "V", "x", 0, hi, c, "max", Fpf=L(Fp), solve=solve)
    ln, wd = a - 2 * c, b - 2 * c
    sol = (f"តាង $x$ (សង់ទីម៉ែត្រ) ជាជ្រុងការ៉េដែលកាត់ ។ ដើម្បីឲ្យប្រអប់មាន លុះត្រាតែ $0<x<{L(hi)}$ ។\n"
           f"បាតប្រអប់មានវិមាត្រ ${L(a-2*x)}$ និង ${L(b-2*x)}$ ហើយកម្ពស់ $x$ ។ មាឌប្រអប់ ៖\n"
           + DM(f"V(x)=x({L(a-2*x)})({L(b-2*x)})={L(sp.expand(V))}") + t + "\n"
           + f"{fin()} ត្រូវកាត់ការ៉េជ្រុង ៖\n" + BOX(f"x={L(c)}") + f"សង់ទីម៉ែត្រ ហើយប្រអប់មានបាត ${L(ln)}\\times{L(wd)}$ និងមាឌអតិបរមា ${L(val)}$ សង់ទីម៉ែត្រគូប ។")
    add("optimization_box", P("medium", "hard", "bacii"), (a, b), prob, sol, f"x={L(c)},\\ V_{{\\max}}={L(val)}", ck, dg + [fig(fig_box(str(a), "x"), "សន្លឹកដែលកាត់កាច់ជ្រុងបួនជ្រុង x")])

def g_can():
    k = rng.randint(1, 12); closed = rng.random() < .6
    item = P("កំប៉ុងទឹកដោះគោ", "ធុងទឹកស៊ីឡាំង", "កំប៉ុងត្រីខ", "ធុងស្ករត្នោត", "កំប៉ុងកាហ្វេ", "ធុងប្រេង")
    # closed: V = 2 pi k^3 ; open: V = pi k^3
    Vv = (2 if closed else 1) * k**3
    S = (2 if closed else 1) * PI * x**2 + 2 * PI * Vv / x
    c = sp.Integer(k)
    hname = "បិទជិត" if closed else "គ្មានគម្រប"
    prob = P(f"រោងចក្រមួយផលិត{item}រាងស៊ីឡាំង{hname} ដែលមានមាឌ ${Vv}\\pi$ សង់ទីម៉ែត្រគូប ។ រកកាំបាត $r$ និងកម្ពស់ $h$ ដើម្បីឲ្យប្រើសម្ភារៈតិចបំផុត ។",
             f"គេចង់ធ្វើ{item}រាងស៊ីឡាំង{hname} ចំណុះ ${Vv}\\pi$ សង់ទីម៉ែត្រគូប ។ តើកាំនិងកម្ពស់ត្រូវមានប្រវែងប៉ុន្មាន ទើបក្រឡាផ្ទៃសរុបអប្បបរមា?")
    Fpf = (f"{4 if closed else 2}\\pi r-\\frac{{{2*Vv}\\pi}}{{r^2}}")
    solve = f"$S'(r)=0$ នាំឲ្យ $r^3={k**3}$ ដូចនេះ $r={k}$ ។"
    t, dg, ck, val = tail(S, "S", "r", 0, sp.oo, c, "min", Fpf=Fpf, solve=solve)
    h = Q(Vv, k * k)
    sf = "2\\pi r^2+2\\pi rh" if closed else "\\pi r^2+2\\pi rh"
    sol = (f"តាង $r>0$ ជាកាំបាត និង $h>0$ ជាកម្ពស់ (គិតជាសង់ទីម៉ែត្រ) ។\n"
           f"មាឌ $\\pi r^2h={Vv}\\pi$ នាំឲ្យ $h=\\frac{{{Vv}}}{{r^2}}$ ។\nក្រឡាផ្ទៃសរុប ៖\n"
           + DM(f"S(r)={sf}={'2' if closed else ''}\\pi r^2+\\frac{{{2*Vv}\\pi}}{{r}}") + t + f"\nពេលនោះ $h=\\frac{{{Vv}}}{{{k*k}}}={L(h)}$ ។\n{fin()}\n" + BOX(f"r={k},\\quad h={L(h)}") + f"ហើយក្រឡាផ្ទៃតូចបំផុតគឺ ${L(val)}$ សង់ទីម៉ែត្រការ៉េ ។")
    ck.append(check(f"{Vv}/{k}**2", st(h), "កម្ពស់"))
    add("optimization_cylinder", P("medium", "hard"), (k, closed), prob, sol, f"r={k},\\ h={L(h)}", ck, dg)

def g_sqbox():
    k = rng.randint(2, 30); closed = rng.random() < .35
    item = P("អាងទឹក", "ប្រអប់ឈើ", "ធុងស័ង្កសី", "អាងចិញ្ចឹមត្រី", "ទូដាក់អង្ករ")
    u = P(("ម៉ែត្រ", "ម៉ែត្រគូប", "ម៉ែត្រការ៉េ"), ("ដេស៊ីម៉ែត្រ", "ដេស៊ីម៉ែត្រគូប", "ដេស៊ីម៉ែត្រការ៉េ"))
    if closed:
        Vv = k**3; S = 2 * x**2 + 4 * Vv / x; Fpf = f"4x-\\frac{{{4*Vv}}}{{x^2}}"; sf = "2x^2+4xh"; pre = "2x^2"
    else:
        if k % 2: k += 1
        Vv = k**3 // 2; S = x**2 + 4 * Vv / x; Fpf = f"2x-\\frac{{{4*Vv}}}{{x^2}}"; sf = "x^2+4xh"; pre = "x^2"
    c = sp.Integer(k)
    hname = "មានគម្រប" if closed else "គ្មានគម្រប"
    prob = P(f"គេសាង{item}{hname} បាតរាងការ៉េ មានមាឌ ${Vv}$ {u[1]} ។ រកជ្រុងបាត $x$ និងកម្ពស់ $h$ ដើម្បីឲ្យក្រឡាផ្ទៃសម្ភារៈតិចបំផុត ។",
             f"{P(*PEOPLE)}ចង់បាន{item}{hname} បាតជាការ៉េ ចំណុះ ${Vv}$ {u[1]} ។ តើវិមាត្របែបណាដែលចំណាយសម្ភារៈអប្បបរមា?")
    t, dg, ck, val = tail(S, "S", "x", 0, sp.oo, c, "min", Fpf=Fpf, solve=f"$S'(x)=0$ នាំឲ្យ $x^3={k**3}$ ដូចនេះ $x={k}$ ។")
    h = Q(Vv, k * k)
    sol = (f"តាង $x>0$ ជាជ្រុងបាត និង $h>0$ ជាកម្ពស់ ({u[0]}) ។ តាមមាឌ $x^2h={Vv}$ នាំឲ្យ $h=\\frac{{{Vv}}}{{x^2}}$ ។\n"
           f"ក្រឡាផ្ទៃសរុប ៖\n" + DM(f"S(x)={sf}={pre}+\\frac{{{4*Vv}}}{{x}}") + t + f"\nនិង $h={L(h)}$ ។\n{fin()} វិមាត្រគឺ ៖\n" + BOX(f"x={k},\\quad h={L(h)}") + f"ហើយក្រឡាផ្ទៃអប្បបរមាគឺ ${L(val)}$ {u[2]} ។")
    add("optimization_box", "medium", (k, closed), prob, sol, f"x={k},\\ h={L(h)}", ck, dg)

PROD = [("ក្រមា", "ក្រមា"), ("ស្ករត្នោត", "គីឡូក្រាមស្ករត្នោត"), ("ម្រេចកំពត", "គីឡូក្រាមម្រេច"), ("អង្ករ", "បាវអង្ករ"), ("កាហ្វេមណ្ឌលគិរី", "ថង់កាហ្វេ"), ("នំអន្សម", "នំអន្សម"), ("ក្រូចពោធិ៍សាត់", "កេសក្រូច"), ("សំពត់សូត្រ", "សំពត់សូត្រ"), ("ទឹកត្រី", "ដបទឹកត្រី"), ("ទឹកដោះគោសណ្ដែក", "ដបទឹកដោះគោសណ្ដែក")]
def g_profit_quad():
    pr, un = P(*PROD)
    a = P(Q(1, 2), 1, 2, Q(1, 4), Q(1, 10), Q(1, 5)); c = rng.choice(range(10, 121, 5)) * (1 if a >= 1 else 1)
    xs = rng.randint(10, 80)
    p = 2 * a * xs + c
    if not p.is_integer if hasattr(p, 'is_integer') else False: return
    fixed = rng.choice(range(50, 501, 50))
    Cc = a * x**2 + c * x + fixed
    # selling price p + extra so that max at xs: profit = (p) x - C has max at (p-c)/(2a)
    Pf = p * x - Cc
    company = P("សហគ្រាសមួយ", "ហាងមួយនៅ" + P(*PLACES), "សហករណ៍កសិកម្មមួយ", "អ្នកលក់ម្នាក់")
    prob = P(f"{company}ផលិត{pr} ។ ថ្លៃផលិត $x$ {un}ក្នុងមួយថ្ងៃគឺ $C(x)={L(Cc)}$ (ពាន់រៀល) ហើយលក់ចេញ ${L(p)}$ ពាន់រៀលក្នុងមួយឯកតា ។ រក $x$ ដើម្បីឲ្យប្រាក់ចំណេញអតិបរមា និងគណនាប្រាក់ចំណេញនោះ ។",
             f"សន្មតថា {company}លក់{un}ក្នុងតម្លៃ ${L(p)}$ ពាន់រៀលក្នុងមួយឯកតា ហើយថ្លៃដើមសរុបសម្រាប់ $x$ ឯកតាគឺ $C(x)={L(Cc)}$ ពាន់រៀល ។ តើគួរផលិតប៉ុន្មានឯកតា ទើបចំណេញច្រើនបំផុត?")
    t, dg, ck, val = tail(Pf, "P", "x", 0, sp.oo, sp.Integer(xs), "max", Fpf=L(sp.diff(Pf, x)), style=P("second", "table"))
    sol = (P("ប្រាក់ចំណេញស្មើចំណូលដកថ្លៃដើម ។\n", "តាង $P(x)$ ជាប្រាក់ចំណេញ (ពាន់រៀល) ចំពោះ $x>0$ ។ ចំណូលគឺ $R(x)=" + L(p) + "x$ ។\n")
           + DM(f"P(x)=R(x)-C(x)={L(p)}x-({L(Cc)})={L(Pf)}") + t + f"\n{fin()} ត្រូវផលិត ៖\n" + BOX(f"x={xs}") + f"ឯកតា ហើយប្រាក់ចំណេញអតិបរមាគឺ ${L(val)}$ ពាន់រៀល ។")
    add("optimization_profit", P("easy", "medium"), Pf, prob, sol, f"x={xs},\\ P_{{\\max}}={L(val)}", ck, dg)

def g_profit_cubic():
    p, q = rng.randint(2, 15), rng.randint(16, 40)   # P'(x) = -3k (x-p)(x-q): min at p, max at q
    k = P(1, Q(1, 3), 2)
    Pp = -3 * k * (x - p) * (x - q)
    F0 = rng.choice(range(0, 200, 20))
    Pf = sp.expand(sp.integrate(Pp, x)) - F0
    hi = sp.Integer(q + rng.randint(5, 15))
    pr, un = P(*PROD)
    prob = P(f"ប្រាក់ចំណេញប្រចាំថ្ងៃ (ពាន់រៀល) ពីការលក់ $x$ {un} ត្រូវបានគេប៉ាន់ស្មានដោយ $P(x)={L(Pf)}$ ដែល $0\\le x\\le {hi}$ ។ សិក្សាអថេរភាពនៃ $P$ រួចរកបរិមាណដែលផ្តល់ប្រាក់ចំណេញច្រើនបំផុត ។",
             f"ហាងលក់{pr}មួយមានប្រាក់ចំណេញ $P(x)={L(Pf)}$ ពាន់រៀល បើលក់បាន $x$ ឯកតា ($0\\le x\\le {hi}$) ។ តើត្រូវលក់ប៉ុន្មានឯកតា ដើម្បីបានចំណេញអតិបរមា?")
    Fp = sp.diff(Pf, x); P0, Pq, Pp_, Ph = Pf.subs(x, 0), Pf.subs(x, q), Pf.subs(x, p), Pf.subs(x, hi)
    if not (Pq > P0 and Pq > Ph): return
    tab = vt("x", "P", ["0", str(p), str(q), L(hi)], ["", "-", "0", "+", "0", "-", ""], [L(P0), "\\searrow", L(Pp_), "\\nearrow", L(Pq), "\\searrow", L(Ph)])
    sol = (f"ដែនកំណត់ $[0;{hi}]$ ។ ដេរីវេ ៖\n" + DM(f"P'(x)={L(Fp)}={L(-3*k)}(x-{p})(x-{q})")
           + f"$P'(x)=0$ មានឫស $x_1={p}$ និង $x_2={q}$ ។\nតារាងអថេរភាព ៖\n" + DM(tab)
           + f"គេប្រៀបធៀប $P(0)={L(P0)}$ និង $P({q})={L(Pq)}$ ហើយ $P({q})$ ធំជាង ។\n{fin()} ប្រាក់ចំណេញអតិបរមាកើតមានត្រង់ ៖\n" + BOX(f"x={q},\\quad P_{{\\max}}={L(Pq)}") + "គិតជាពាន់រៀល ។")
    ck = [dchk(Pf, Fp), d0chk(Pf, p), d0chk(Pf, q), vchk(Pf, q, Pq), vchk(Pf, p, Pp_), vchk(Pf, hi, Ph)]
    add("optimization_profit", P("hard", "bacii"), Pf, prob, sol, f"x={q},\\ P_{{\\max}}={L(Pq)}", ck, [vdiag(tab, "តារាងអថេរភាពនៃប្រាក់ចំណេញ")])

def g_avgcost():
    a = P(1, 2, Q(1, 2), Q(1, 4), 3, 5); xs = rng.randint(5, 60); b = rng.randint(2, 40)
    cc = a * xs * xs
    if not cc.is_integer if hasattr(cc, "is_integer") else False: return
    Cc = a * x**2 + b * x + cc
    Av = a * x + b + cc / x
    pr, un = P(*PROD)
    prob = P(f"ថ្លៃផលិតសរុបនៃ $x$ {un} គឺ $C(x)={L(Cc)}$ ពាន់រៀល ។ រក $x$ ដែលធ្វើឲ្យថ្លៃដើមមធ្យមក្នុងមួយឯកតា $\\overline{{C}}(x)=\\frac{{C(x)}}{{x}}$ តូចបំផុត ។",
             f"រោងផលិត{pr}មួយមានថ្លៃផលិត $C(x)={L(Cc)}$ ពាន់រៀល សម្រាប់ $x$ ឯកតា ។ តើគួរផលិតប៉ុន្មានឯកតា ទើបថ្លៃដើមក្នុងមួយឯកតាទាបជាងគេ? ថ្លៃនោះស្មើប៉ុន្មាន?")
    t, dg, ck, val = tail(Av, "\\overline{C}", "x", 0, sp.oo, sp.Integer(xs), "min", Fpf=f"{L(a)}-\\frac{{{L(cc)}}}{{x^2}}", solve=f"$\\overline{{C}}'(x)=0$ នាំឲ្យ $x^2={L(xs**2)}$ ហើយដោយ $x>0$ គេបាន $x={xs}$ ។")
    sol = (f"ថ្លៃដើមមធ្យមចំពោះ $x>0$ គឺ ៖\n" + DM(f"\\overline{{C}}(x)=\\frac{{C(x)}}{{x}}={L(a*x)}+{b}+\\frac{{{L(cc)}}}{{x}}") + t + f"\n{fin()} ត្រូវផលិត ៖\n" + BOX(f"x={xs}") + f"ឯកតា ហើយថ្លៃដើមមធ្យមទាបបំផុតគឺ ៖\n" + BOX(f"\\overline{{C}}({xs})={L(val)}") + "ពាន់រៀលក្នុងមួយឯកតា ។")
    add("optimization_cost", "medium", Cc, prob, sol, f"x={xs},\\ \\overline{{C}}({xs})={L(val)}", ck, dg)

def g_price():
    item = P(("សំបុត្រកម្សាន្តទូកទេសចរណ៍", "សំបុត្រ", "ភ្ញៀវ"), ("បន្ទប់ផ្ទះសំណាក់នៅកែប", "បន្ទប់", "បន្ទប់ជួល"), ("ចាននំបញ្ចុក", "ចាន", "អតិថិជន"), ("ជិះតុកតុកទៅប្រាសាទអង្គរវត្ត", "ដំណើរ", "ដំណើរ"), ("កាហ្វេទឹកកក", "កែវ", "កែវ"))
    n0 = rng.choice(range(40, 401, 20)); p0 = rng.choice(range(4, 41, 2)); dn = P(2, 4, 5, 10); dp = 1
    # after k steps: (p0 + k)(n0 - dn k), max at k = (n0/dn - p0)/2
    kk = Q(n0, dn) - p0
    k = kk / 2
    if k <= 0 or k != int(k): return
    R = (p0 + x) * (n0 - dn * x)
    hi = Q(n0, dn)
    prob = P(f"តម្លៃបច្ចុប្បន្ននៃ{item[0]}គឺ ${p0}$ ពាន់រៀល ហើយលក់បាន ${n0}$ {item[1]}ក្នុងមួយថ្ងៃ ។ ការស្ទង់មតិបង្ហាញថា រាល់ការឡើងថ្លៃ $1$ ពាន់រៀល ធ្វើឲ្យចំនួនលក់ថយ ${dn}$ {item[1]} ។ តើគួរកំណត់ថ្លៃប៉ុន្មាន ដើម្បីឲ្យចំណូលធំបំផុត?",
             f"បើលក់{item[0]}ក្នុងតម្លៃ ${p0}$ ពាន់រៀល គេលក់បាន ${n0}$ {item[1]} ។ បើដំឡើង $x$ ពាន់រៀល គេលក់បានថយ ${dn}x$ {item[1]} ។ រក $x$ ដែលធ្វើឲ្យចំណូលអតិបរមា រួចគណនាចំណូលនោះ ។")
    t, dg, ck, val = tail(R, "R", "x", 0, hi, k, "max", Fpf=L(sp.expand(sp.diff(R, x))), style=P("second", "sign", "table"))
    sol = (f"តាង $x$ (ពាន់រៀល) ជាចំនួនដែលដំឡើង ដែល $0\\le x<{L(hi)}$ ។ ពេលនោះថ្លៃថ្មីគឺ ${L(p0+x)}$ ហើយចំនួនលក់គឺ ${L(n0-dn*x)}$ ។\nចំណូលក្នុងមួយថ្ងៃ ៖\n"
           + DM(f"R(x)=({L(p0+x)})({L(n0-dn*x)})={L(sp.expand(R))}") + t + f"\n{fin()} ត្រូវកំណត់ថ្លៃ ៖\n" + BOX(f"{p0}+{L(k)}={L(p0+k)}") + f"ពាន់រៀល ហើយចំណូលអតិបរមាគឺ ${L(val)}$ ពាន់រៀល ។")
    add("optimization_revenue", P("medium", "medium", "hard"), R, prob, sol, f"p={L(p0+k)},\\ R_{{\\max}}={L(val)}", ck, dg)

def g_trees():
    tree = P("ដើមស្វាយ", "ដើមក្រូច", "ដើមម្រេច", "ដើមដូង", "ដើមទុរេន", "ដើមកាហ្វេ")
    n0 = rng.choice(range(20, 121, 10)); y0 = rng.choice(range(40, 301, 10)); d = P(1, 2, 3, 4, 5)
    # (n0 + x)(y0 - d x), max at x = (y0/d - n0)/2
    k = (Q(y0, d) - n0) / 2
    if k <= 0 or k != int(k) or k > 200: return
    Y = (n0 + x) * (y0 - d * x)
    prob = P(f"ចម្ការមួយនៅ{P(*PLACES)}មាន{tree} ${n0}$ ដើម ហើយមួយដើមៗឲ្យផល ${y0}$ ផ្លែក្នុងមួយឆ្នាំ ។ បើដាំបន្ថែមមួយដើម ទិន្នផលនៃគ្រប់ដើមថយ ${d}$ ផ្លែ ។ តើត្រូវដាំបន្ថែមប៉ុន្មានដើម ទើបផលសរុបច្រើនបំផុត?",
             f"{P(*PEOPLE)}មាន{tree} ${n0}$ ដើម មួយដើមបានផ្លែ ${y0}$ ផ្លែ ។ រាល់{tree}ដាំបន្ថែមមួយដើម ទិន្នផលមួយដើមៗធ្លាក់ចុះ ${d}$ ផ្លែ ដោយសារដើមនៅជិតគ្នាពេក ។ រកចំនួនដើមបន្ថែមដែលផ្តល់ផលសរុបអតិបរមា ។")
    t, dg, ck, val = tail(Y, "Y", "x", 0, Q(y0, d), k, "max", Fpf=L(sp.expand(sp.diff(Y, x))), style=P("second", "sign"))
    sol = (f"បើដាំបន្ថែម $x$ ដើម ($x\\ge0$) នោះមានដើមសរុប ${L(n0+x)}$ ហើយមួយដើមបានផល ${L(y0-d*x)}$ ផ្លែ ។\nផលសរុប ៖\n" + DM(f"Y(x)=({L(n0+x)})({L(y0-d*x)})={L(sp.expand(Y))}") + t
           + f"\n{fin()} ត្រូវដាំបន្ថែម ៖\n" + BOX(f"x={L(k)}") + f"ដើម ហើយផលសរុបអតិបរមាគឺ ${L(val)}$ ផ្លែ ។")
    add("optimization_revenue", "medium", Y, prob, sol, f"x={L(k)},\\ Y_{{\\max}}={L(val)}", ck, dg)

def g_parab_rect():
    n = rng.randint(1, 12); k2 = 3 * n * n
    a = P(1, 1, 2, Q(1, 2), 3)
    Af = 2 * x * a * (k2 - x**2)
    ctx = P("ខ្លោងទ្វារសាលាមួយមានរាងប៉ារ៉ាបូល", "ស្ពានឈើមួយមានធ្នូរាងប៉ារ៉ាបូល", "មាត់រូងភ្នំមួយមានរាងប៉ារ៉ាបូល", "ផ្ទាំងឈើមួយកាត់ជារាងប៉ារ៉ាបូល")
    fy = a * (k2 - x**2)
    prob = f"{ctx} ដែលកំណត់ដោយ $y={L(fy)}$ ($y\\ge0$) ក្នុងប្លង់ $xoy$ ។ គេចង់ដាក់ចតុកោណកែងមួយក្នុងផ្ទៃនោះ ដែលមានបាតលើអ័ក្ស $x'ox$ និងកំពូលពីរលើខ្សែកោង ។ រកក្រឡាផ្ទៃធំបំផុតនៃចតុកោណកែងនោះ ។"
    hi = sp.sqrt(k2)
    t, dg, ck, val = tail(Af, "S", "x", 0, hi, sp.Integer(n), "max", Fpf=L(sp.expand(sp.diff(Af, x))), solve=f"$S'(x)=0$ នាំឲ្យ $x^2={n*n}$ ហើយដោយ $x>0$ នោះ $x={n}$ ។", style=P("second", "sign"))
    hgt = fy.subs(x, n)
    sol = (f"ដោយខ្សែកោងឆ្លុះធៀបនឹងអ័ក្ស $y'oy$ តាងកំពូលខាងស្តាំនៃចតុកោណកែងជា $(x;{L(fy)})$ ដែល $0<x<{L(hi)}$ ។\nបាតមានប្រវែង $2x$ ហើយកម្ពស់ ${L(fy)}$ ។ ក្រឡាផ្ទៃ ៖\n" + DM(f"S(x)=2x({L(fy)})={L(sp.expand(Af))}") + t
           + f"\nចតុកោណកែងមានបាត ${2*n}$ និងកម្ពស់ ${L(hgt)}$ ។\n{fin()}\n" + BOX(f"S_{{\\max}}={L(val)}") + "ឯកតាក្រឡាផ្ទៃ ។")
    def dgm(rid): return dg + [graph(rid, fy, float(-hi) - .5, float(hi) + .5, -1, float(fy.subs(x, 0)) * 1.2, "ប៉ារ៉ាបូល និងចំណុចកំពូលនៃចតុកោណកែង", pts=[(n, hgt), (-n, hgt)])]
    add("optimization_geometry", "hard", fy, prob, sol, f"S_{{\\max}}={L(val)}", ck, dgm if rng.random() < .7 else dg)

def g_semicircle():
    R = rng.choice(range(2, 41, 2)); mode = P("semi", "circle")
    if mode == "semi":
        A = 2 * x * sp.sqrt(R**2 - x**2)
        c = R / sp.sqrt(2)
        prob = P(f"គេកាត់ចតុកោណកែងមួយពីបន្ទះឈើរាងពាក់កណ្តាលរង្វង់កាំ ${R}$ សង់ទីម៉ែត្រ ដោយបាតនៅលើអង្កត់ផ្ចិត ។ រកវិមាត្រចតុកោណកែង ដើម្បីឲ្យក្រឡាផ្ទៃធំបំផុត ។",
                 f"ចតុកោណកែងមួយចារឹកក្នុងពាក់កណ្តាលរង្វង់កាំ ${R}$ ដោយជ្រុងមួយនៅលើអង្កត់ផ្ចិត ។ គណនាក្រឡាផ្ទៃអតិបរមារបស់វា ។")
        setup = f"តាង $x$ ជាពាក់កណ្តាលបាត ($0<x<{R}$) ។ តាមទ្រឹស្តីបទពីតាករ កម្ពស់គឺ $\\sqrt{{{R*R}-x^2}}$ ។"
        Sx = f"S(x)=2x\\sqrt{{{R*R}-x^2}}"; dims = lambda c, h: (2 * c, h)
    else:
        A = 4 * x * sp.sqrt(R**2 - x**2)
        c = R / sp.sqrt(2)
        prob = P(f"គេចង់អារឈើពីគល់ឈើមុខកាត់រង្វង់កាំ ${R}$ សង់ទីម៉ែត្រ ឲ្យបានធ្នឹមមុខកាត់ចតុកោណកែងដែលមានក្រឡាផ្ទៃធំបំផុត ។ រកវិមាត្រនៃមុខកាត់នោះ ។",
                 f"ចតុកោណកែងមួយចារឹកក្នុងរង្វង់កាំ ${R}$ ។ បង្ហាញថា ចតុកោណកែងដែលមានក្រឡាផ្ទៃធំបំផុតគឺជាការ៉េ រួចគណនាក្រឡាផ្ទៃនោះ ។")
        setup = f"តាងវិមាត្រជា $2x$ និង $2y$ ដែល $x^2+y^2={R*R}$ និង $0<x<{R}$ ។ នោះ $y=\\sqrt{{{R*R}-x^2}}$ ។"
        Sx = f"S(x)=4x\\sqrt{{{R*R}-x^2}}"; dims = lambda c, h: (2 * c, 2 * h)
    co = A.subs(x, 1) / sp.sqrt(R**2 - 1)
    Fpf = f"{co}\\cdot\\frac{{{R*R}-2x^2}}{{\\sqrt{{{R*R}-x^2}}}}"
    t, dg, ck, val = tail(A, "S", "x", 0, R, c, "max", Fpf=Fpf, solve=f"$S'(x)=0$ នាំឲ្យ $2x^2={R*R}$ ដូចនេះ $x={L(c)}$ (ព្រោះ $x>0$) ។", style=P("sign", "table"))
    h = sp.sqrt(R**2 - c**2); d1, d2 = dims(c, h)
    sol = (setup + "\nក្រឡាផ្ទៃ ៖\n" + DM(Sx) + "ដោយប្រើរូបមន្តដេរីវេនៃផលគុណ $(uv)'=u'v+uv'$ និង $(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}$ ។\n" + t
           + f"\nវិមាត្រគឺ ${L(d1)}$ និង ${L(d2)}$ ។\n{fin()}\n" + BOX(f"S_{{\\max}}={L(val)}") + "ឯកតាក្រឡាផ្ទៃ ។")
    add("optimization_geometry", P("hard", "bacii"), (mode, R), prob, sol, f"S_{{\\max}}={L(val)}", ck, dg)

def g_cone_cyl():
    Rc = 3 * rng.randint(1, 8); H = rng.randint(3, 30)
    c = sp.Integer(2 * Rc // 3)
    V = PI * x**2 * H * (1 - x / Rc)
    prob = P(f"ស៊ីឡាំងមួយចារឹកក្នុងកោណដែលមានកាំបាត ${Rc}$ និងកម្ពស់ ${H}$ ដោយបាតស៊ីឡាំងនៅលើបាតកោណ ។ រកកាំស៊ីឡាំងដែលធ្វើឲ្យមាឌធំបំផុត ។",
             f"ជាងចម្លាក់ម្នាក់ចង់កាត់ដុំឈើរាងកោណ (កាំបាត ${Rc}$ សង់ទីម៉ែត្រ កម្ពស់ ${H}$ សង់ទីម៉ែត្រ) ឲ្យបានស៊ីឡាំងមានមាឌធំបំផុត ដោយបាតទាំងពីររួមអ័ក្សគ្នា ។ រកកាំនិងកម្ពស់ស៊ីឡាំង ។")
    t, dg, ck, val = tail(V, "V", "r", 0, Rc, c, "max", Fpf=L(sp.factor(sp.diff(V, x)), "r"), solve=f"$V'(r)=0$ នាំឲ្យ $r=0$ (មិនយក) ឬ $r={c}$ ។")
    h = H * (1 - c / sp.Integer(Rc))
    sol = (f"តាង $r$ ជាកាំ និង $h$ ជាកម្ពស់ស៊ីឡាំង ($0<r<{Rc}$) ។ តាមទ្រឹស្តីបទតាលែស (ត្រីកោណដូចគ្នា) ៖\n" + DM(f"\\frac{{h}}{{{H}}}=\\frac{{{Rc}-r}}{{{Rc}}}\\Rightarrow h={L(H*(1-x/Rc),'r')}")
           + "មាឌស៊ីឡាំង ៖\n" + DM(f"V(r)=\\pi r^2h={L(sp.expand(V),'r')}") + t + f"\nពេលនោះ $h={L(h)}$ ។\n{fin()}\n" + BOX(f"r={c},\\quad h={L(h)}") + f"ហើយមាឌអតិបរមាគឺ ${L(val)}$ ឯកតាមាឌ ។")
    add("optimization_geometry", "hard", (Rc, H), prob, sol, f"r={c},\\ h={L(h)}", ck, dg + [fig(fig_cone(str(Rc), str(H)), "កោណដែលមានកាំបាត និងកម្ពស់")])

def g_dist():
    mode = P("sqrt", "parab", "line")
    if mode == "sqrt":
        a = Q(rng.randint(3, 40), 2)
        D = (x - a)**2 + x
        c = a - Q(1, 2)
        prob = P(f"រកចំណុច $M$ លើខ្សែកោង $y=\\sqrt{{x}}$ ដែលនៅជិតចំណុច $A({L(a)};0)$ បំផុត ។", f"គេមានចំណុច $A({L(a)};0)$ និងខ្សែកោង $(C):y=\\sqrt{{x}}$ ។ រកចម្ងាយខ្លីបំផុតពី $A$ ទៅ $(C)$ ។")
        pt = lambda c: sp.sqrt(c); Mx = "M(x;\\sqrt{x})"; lo = 0
        f = sp.sqrt(x)
    else:
        b = sp.Integer(rng.randint(1, 8))
        if mode == "parab":
            # distance from (0,b) to y=x^2 ; D = x^2 + (x^2-b)^2 ; min at x^2 = b - 1/2
            b = Q(2 * rng.randint(1, 30) + 1, 2) if False else (sp.Integer(rng.randint(1, 9))**2 + Q(1, 2))
            D = x**2 + (x**2 - b)**2
            c = sp.sqrt(b - Q(1, 2)); lo = 0
            prob = f"រកចំណុចនៅលើប៉ារ៉ាបូល $y=x^2$ ដែលនៅជិតចំណុច $A(0;{L(b)})$ បំផុត ។"
            pt = lambda c: c**2; Mx = "M(x;x^2)"; f = x**2
        else:
            p = rng.randint(1, 6); q = rng.randint(1, 6)
            # point (p,q) distance to y = 2x + k via calculus
            k = rng.randint(-6, 6); s_ = P(1, 2, 3)
            if q - s_ * p - k == 0: return
            D = (x - p)**2 + (s_ * x + k - q)**2
            c = sp.solve(sp.diff(D, x), x)[0]; lo = -sp.oo
            f = s_ * x + k
            prob = f"ដោយប្រើដេរីវេ រកចំណុច $M$ នៅលើបន្ទាត់ $y={L(f)}$ ដែលនៅជិតចំណុច $A({p};{q})$ បំផុត ។"
            pt = lambda c: f.subs(x, c); Mx = f"M(x;{L(f)})"
    hi = sp.oo
    t, dg, ck, val = tail(D, "D", "x", lo, hi, c, "min", Fpf=L(sp.factor(sp.diff(D, x))), style=P("sign", "table") if mode != "parab" else "sign",
                          solve=(f"$D'(x)=0$ ចំពោះ $x>0$ នាំឲ្យ $x={L(c)}$ ។" if mode == "parab" else None))
    y0 = pt(c); dist = sp.sqrt(val)
    sol = (f"តាង ${Mx}$ ជាចំណុចលើខ្សែកោង{' ដោយយក $x\\ge0$ ព្រោះខ្សែកោងឆ្លុះធៀបនឹង $y' + chr(39) + 'oy$' if mode == 'parab' else ''} ។ ដើម្បីងាយ យើងសិក្សាការ៉េនៃចម្ងាយ $D(x)=AM^2$ ព្រោះ $AM$ តូចបំផុតលុះត្រាតែ $AM^2$ តូចបំផុត ។\n"
           + DM(f"D(x)={L(D)}") + t + f"\nចំណុចដែលរកបានគឺ $M({L(c)};{L(y0)})$ ហើយ $AM=\\sqrt{{{L(val)}}}={L(dist)}$ ។\n{fin()}\n" + BOX(f"M\\left({L(c)};{L(y0)}\\right)") )
    ck.append(check(f"({st(f)}).subs(x,{st(c)})", st(y0), "អរដោនេ"))
    add("optimization_distance", P("medium", "hard"), D, prob, sol, f"M\\left({L(c)};{L(y0)}\\right)", ck, dg)

PYT = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17), (7, 24, 25), (24, 7, 25), (20, 21, 29)]
def g_shore():
    a, b, h = P(*PYT)     # speeds or costs: slow part cost/time v1=a..; ratio v1/v2 = a/h ; x = d*a/b
    k = rng.randint(1, 12)
    d = b * k; xs = a * k
    Lr = xs + rng.randint(1, 30)
    mode = P("cable", "cable", "swim", "pipe")
    if mode == "swim":
        ctx = f"កោះតូចមួយនៅចម្ងាយ ${d}$ គីឡូម៉ែត្រពីចំណុច $A$ នៃឆ្នេរត្រង់ ។ ភូមិ $B$ នៅលើឆ្នេរ ចម្ងាយ ${Lr}$ គីឡូម៉ែត្រពី $A$ ។ អ្នកនេសាទម្នាក់ជិះទូកពីកោះទៅចំណុច $M$ លើឆ្នេរ ក្នុងល្បឿន ${a}$ គីឡូម៉ែត្រក្នុងមួយម៉ោង រួចជិះម៉ូតូពី $M$ ទៅ $B$ ក្នុងល្បឿន ${h}$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ។ រកទីតាំង $M$ ដើម្បីឲ្យរយៈពេលធ្វើដំណើរខ្លីបំផុត ។"
        F = sp.sqrt(x**2 + d**2) / a + (Lr - x) / h
        desc = f"រយៈពេលសរុប (ម៉ោង) គឺ ៖"; nm = "T"; Ff = f"T(x)=\\frac{{\\sqrt{{x^2+{d*d}}}}}{{{a}}}+\\frac{{{Lr}-x}}{{{h}}}"
        fp = f"\\frac{{x}}{{{a}\\sqrt{{x^2+{d*d}}}}}-\\frac{{1}}{{{h}}}"
        slv = f"$T'(x)=0$ នាំឲ្យ ${h}x={a}\\sqrt{{x^2+{d*d}}}$ ។ លើកការ៉េ ៖ ${h*h}x^2={a*a}(x^2+{d*d})$ នាំឲ្យ ${b*b}x^2={a*a*d*d}$ ដូចនេះ $x={xs}$ (ព្រោះ $x>0$) ។"
        unit = "ម៉ោង"
    else:
        c1, c2 = h * P(1, 2, 5), None
        mul = c1 // h; c2 = a * mul
        c1, c2 = h * mul, a * mul     # water cost c1 per km, land cost c2 per km
        thing = "ខ្សែភ្លើង" if mode == "cable" else "បំពង់ទឹក"
        ctx = f"គេត្រូវតភ្ជាប់{thing}ពីស្ថានីយ $S$ នៅលើកោះ ដែលនៅចម្ងាយ ${d}$ គីឡូម៉ែត្រពីចំណុច $A$ នៃច្រាំងត្រង់ ទៅកាន់ភូមិ $B$ នៅលើច្រាំង ចម្ងាយ ${Lr}$ គីឡូម៉ែត្រពី $A$ ។ តម្លៃដាក់ក្រោមទឹកគឺ ${c1}$ ពាន់ដុល្លារក្នុងមួយគីឡូម៉ែត្រ ហើយតាមច្រាំងគឺ ${c2}$ ពាន់ដុល្លារក្នុងមួយគីឡូម៉ែត្រ ។ រកចំណុច $M$ លើច្រាំងដែលត្រូវឲ្យ{thing}ឡើងគោក ដើម្បីចំណាយតិចបំផុត ។"
        F = c1 * sp.sqrt(x**2 + d**2) + c2 * (Lr - x)
        desc = "ចំណាយសរុប (ពាន់ដុល្លារ) គឺ ៖"; nm = "C"; Ff = f"C(x)={c1}\\sqrt{{x^2+{d*d}}}+{c2}({Lr}-x)"
        fp = f"\\frac{{{c1}x}}{{\\sqrt{{x^2+{d*d}}}}}-{c2}"
        slv = f"$C'(x)=0$ នាំឲ្យ ${c1}x={c2}\\sqrt{{x^2+{d*d}}}$ ។ លើកការ៉េ រួចសម្រួល ៖ ${h*h}x^2={a*a}(x^2+{d*d})$ នាំឲ្យ $x={xs}$ (ព្រោះ $x>0$) ។"
        unit = "ពាន់ដុល្លារ"
    t, dg, ck, val = tail(F, nm, "x", 0, Lr, sp.Integer(xs), "min", Fpf=fp, solve=slv, style=P("sign", "table"))
    sol = (f"តាង $x=AM$ (គីឡូម៉ែត្រ) ដែល $0\\le x\\le {Lr}$ ។ តាមទ្រឹស្តីបទពីតាករ ចម្ងាយឆ្លងទឹកគឺ $\\sqrt{{x^2+{d*d}}}$ ហើយចម្ងាយនៅសល់តាមច្រាំងគឺ ${Lr}-x$ ។\n{desc}\n" + DM(Ff) + t
           + f"\n{fin()} ចំណុច $M$ នៅចម្ងាយ ៖\n" + BOX(f"AM={xs}") + f"គីឡូម៉ែត្រពី $A$ ហើយតម្លៃអប្បបរមាគឺ ${L(val)}$ {unit} ។")
    add("optimization_path", P("hard", "bacii"), (mode, a, b, k, Lr), prob := ctx, sol, f"AM={xs}", ck, dg + [fig("\\begin{tikzpicture}\n\\draw[thick] (0,0) -- (6,0);\n\\draw (1,0) -- (1,2.5) -- (3,0);\n\\node[below] at (1,0) {$A$};\n\\node[below] at (3,0) {$M$};\n\\node[below] at (6,0) {$B$};\n\\node[left] at (1,1.25) {$" + str(d) + "$};\n\\node[below] at (2,0) {$x$};\n\\end{tikzpicture}", "ឆ្នេរត្រង់ មានចំណុច A M B និងទីតាំងនៅក្នុងទឹក")])

def g_numbers():
    S = rng.choice(range(6, 121, 3)); m_ = P("xy2", "xy", "sq", "x+1/x", "x3y")
    if m_ == "xy2":
        if S % 3: return
        F = x**2 * (S - x); c = sp.Integer(2 * S // 3); kind = "max"; lo, hi = 0, S
        prob = f"រកចំនួនពិតវិជ្ជមានពីរ $x$ និង $y$ ដែលមានផលបូកស្មើ ${S}$ ហើយផលគុណ $x^2y$ ធំបំផុត ។"
        dep = f"y={S}-x"
    elif m_ == "xy":
        if S % 2: return
        F = x * (S - x); c = sp.Integer(S // 2); kind = "max"; lo, hi = 0, S
        prob = f"គេមានចំនួនវិជ្ជមានពីរដែលមានផលបូកស្មើ ${S}$ ។ រកចំនួនទាំងពីរ ដើម្បីឲ្យផលគុណអតិបរមា ។"
        dep = f"y={S}-x"
    elif m_ == "sq":
        if S % 2: return
        F = x**2 + (S - x)**2; c = sp.Integer(S // 2); kind = "min"; lo, hi = 0, S
        prob = f"រកចំនួនពិតវិជ្ជមានពីរដែលមានផលបូក ${S}$ ហើយផលបូកការ៉េនៃចំនួនទាំងពីរតូចបំផុត ។"
        dep = f"y={S}-x"
    elif m_ == "x3y":
        if S % 4: return
        F = x**3 * (S - x); c = sp.Integer(3 * S // 4); kind = "max"; lo, hi = 0, S
        prob = f"ចំនួនវិជ្ជមាន $x$ និង $y$ ផ្ទៀងផ្ទាត់ $x+y={S}$ ។ រកតម្លៃអតិបរមានៃ $x^3y$ ។"
        dep = f"y={S}-x"
    else:
        p = S * S
        F = x + Q(p) / x; c = sp.Integer(S); kind = "min"; lo, hi = 0, sp.oo
        prob = f"រកចំនួនវិជ្ជមាន $x$ ដែលធ្វើឲ្យផលបូក $x+\\frac{{{p}}}{{x}}$ តូចបំផុត ។"
        dep = None
    t, dg, ck, val = tail(F, "g", "x", lo, hi, c, kind, Fpf=L(sp.factor(sp.diff(F, x))))
    sol = (f"តាមសម្មតិកម្ម ${dep}$ ដែល $0<x<{S}$ ។\n" if dep else "ចំពោះ $x>0$ ") + "តាង ៖\n" + DM(f"g(x)={L(F)}") + t + f"\n{fin()}\n" + BOX(f"x={L(c)},\\quad g={L(val)}")
    add("optimization_numbers", "easy", F, prob, sol, f"x={L(c)},\\ {L(val)}", ck, dg)

def g_trip():
    a = P(Q(1, 2), Q(1, 4), 1, 2, Q(1, 5), Q(1, 10)); v = rng.choice(range(10, 61, 5)); D = rng.choice(range(40, 401, 20))
    b = a * v * v
    veh = P("ទូកម៉ាស៊ីន", "ឡានដឹកទំនិញ", "កាណូត", "នាវាដឹកអ្នកដំណើរ")
    frm, to = rng.sample(PLACES, 2)
    C = D * (a * x + b / x)
    prob = (f"{veh}ធ្វើដំណើរពី{frm}ទៅ{to} ចម្ងាយ ${D}$ គីឡូម៉ែត្រ ក្នុងល្បឿនថេរ $v$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ។ ចំណាយក្នុងមួយម៉ោងគឺ ${L(a*x**2+b,'v')}$ ពាន់រៀល (ប្រេងអាស្រ័យនឹង $v^2$ ហើយប្រាក់ឈ្នួលនិងថ្លៃផ្សេងៗថេរ) ។ រកល្បឿន $v$ ដែលធ្វើឲ្យចំណាយសរុបតិចបំផុត ។")
    t, dg, ck, val = tail(C, "C", "v", 0, sp.oo, sp.Integer(v), "min", Fpf=f"{L(a*D)}-\\frac{{{L(b*D)}}}{{v^2}}", solve=f"$C'(v)=0$ នាំឲ្យ $v^2={v*v}$ ដូចនេះ $v={v}$ (ព្រោះ $v>0$) ។")
    sol = (f"រយៈពេលធ្វើដំណើរគឺ $\\frac{{{D}}}{{v}}$ ម៉ោង ។ ដូច្នេះចំណាយសរុបចំពោះ $v>0$ ៖\n" + DM(f"C(v)=\\frac{{{D}}}{{v}}({L(a*x**2+b,'v')})={L(a*D)}v+\\frac{{{L(b*D)}}}{{v}}") + t + f"\n{fin()} ល្បឿនសន្សំសំចៃបំផុតគឺ ៖\n" + BOX(f"v={v}") + f"គីឡូម៉ែត្រក្នុងមួយម៉ោង ហើយចំណាយសរុបគឺ ${L(val)}$ ពាន់រៀល ។")
    add("optimization_cost", P("medium", "hard"), C, prob, sol, f"v={v}", ck, dg)

def g_poster():
    a, b = rng.randint(1, 6), rng.randint(1, 6); w = rng.randint(4, 40)
    # print w x h, h = A/w ; total (w+2a)(A/w+2b) min at w = sqrt(A a / b)
    A = w * w * b
    if A % a: return
    A = A // a
    F = (x + 2 * a) * (Q(A) / x + 2 * b)
    item = P("ផ្ទាំងផ្សាយពាណិជ្ជកម្ម", "ទំព័រសៀវភៅ", "ផ្ទាំងរូបភាពបុណ្យភ្ជុំ", "ប័ណ្ណប្រកាស")
    prob = P(f"{item}មួយមានផ្នែកបោះពុម្ពរាងចតុកោណកែងក្រឡាផ្ទៃ ${A}$ សង់ទីម៉ែត្រការ៉េ ។ រឹមឆ្វេងនិងស្តាំ ម្ខាងៗ ${a}$ សង់ទីម៉ែត្រ រឹមលើនិងក្រោម ម្ខាងៗ ${b}$ សង់ទីម៉ែត្រ ។ រកវិមាត្រផ្នែកបោះពុម្ព ដើម្បីឲ្យក្រដាសប្រើតិចបំផុត ។")
    Fe = sp.expand(F)
    t, dg, ck, val = tail(F, "S", "x", 0, sp.oo, sp.Integer(w), "min", Fpf=f"{2*b}-\\frac{{{2*a*A}}}{{x^2}}", solve=f"$S'(x)=0$ នាំឲ្យ $x^2={w*w}$ ដូចនេះ $x={w}$ ។")
    h = Q(A, w)
    sol = (f"តាងទទឹងផ្នែកបោះពុម្ពជា $x>0$ នោះកម្ពស់គឺ $\\frac{{{A}}}{{x}}$ ។\nទំហំក្រដាសសរុបមានវិមាត្រ $x+{2*a}$ និង $\\frac{{{A}}}{{x}}+{2*b}$ ។ ក្រឡាផ្ទៃក្រដាស ៖\n"
           + DM(f"S(x)=(x+{2*a})\\left(\\frac{{{A}}}{{x}}+{2*b}\\right)={L(Fe)}") + t + f"\n{fin()} ផ្នែកបោះពុម្ពមានវិមាត្រ ៖\n" + BOX(f"{w}\\times{L(h)}") + f"សង់ទីម៉ែត្រ ហើយក្រដាសមានក្រឡាផ្ទៃ ${L(val)}$ សង់ទីម៉ែត្រការ៉េ ។")
    add("optimization_cost", "hard", F, prob, sol, f"{w}\\times{L(h)}", ck, dg)

def g_trough():
    w = rng.randint(1, 20) * 2
    mode = P("trough", "isoc")
    if mode == "trough":
        F = w**2 * (1 + sp.cos(x)) * sp.sin(x)
        prob = P(f"គេបត់បន្ទះស័ង្កសីទទឹង ${3*w}$ សង់ទីម៉ែត្រ ជាបីផ្នែកស្មើគ្នា ដើម្បីធ្វើទឹកភ្លៀងរាងចតុកោណព្នាយ ។ ជ្រុងទាំងពីរទ្រេតធៀបនឹងខ្សែកែងនឹងបាតដោយមុំ $\\theta$ ។".replace("ទឹកភ្លៀងរាងចតុកោណព្នាយ", "ស្នូកទឹកភ្លៀងមុខកាត់រាងចតុកោណព្នាយ") + " បង្ហាញថាក្រឡាផ្ទៃមុខកាត់គឺ $S(\\theta)=" + L(w*w) + "(1+\\sin\\theta)\\cos\\theta$ រួចរក $\\theta$ ដើម្បីឲ្យស្នូកផ្ទុកទឹកបានច្រើនបំផុត ។")
        F = w**2 * (1 + sp.sin(x)) * sp.cos(x); c = PI / 6
        setup = (f"មុខកាត់មានបាតតូច ${w}$ បាតធំ ${w}+2\\cdot{w}\\sin\\theta$ និងកម្ពស់ ${w}\\cos\\theta$ ។ តាមរូបមន្តក្រឡាផ្ទៃចតុកោណព្នាយ ៖\n"
                 + DM(f"S(\\theta)=\\frac{{{w}+{w}+{2*w}\\sin\\theta}}{{2}}\\cdot{w}\\cos\\theta={L(w*w)}(1+\\sin\\theta)\\cos\\theta") + "ដែល $0\\le\\theta<\\frac{\\pi}{2}$ ។\n")
        fp = f"{L(w*w)}(\\cos^2\\theta-\\sin\\theta-\\sin^2\\theta)={L(w*w)}(1-\\sin\\theta-2\\sin^2\\theta)={L(w*w)}(1+\\sin\\theta)(1-2\\sin\\theta)"
        slv = "$S'(\\theta)=0$ ដោយ $1+\\sin\\theta>0$ នាំឲ្យ $\\sin\\theta=\\frac{1}{2}$ ដូចនេះ $\\theta=\\frac{\\pi}{6}$ ។"
        hi = PI / 2
    else:
        F = Q(w * w, 2) * sp.sin(x); c = PI / 2
        prob = f"ត្រីកោណសមបាតមួយមានជ្រុងស្មើគ្នាពីរប្រវែង ${w}$ ហើយមុំកំពូល $\\theta$ ($0<\\theta<\\pi$) ។ រក $\\theta$ ដែលធ្វើឲ្យក្រឡាផ្ទៃត្រីកោណធំបំផុត ។"
        setup = "តាមរូបមន្ត ៖\n" + DM(f"S(\\theta)=\\frac{{1}}{{2}}\\cdot{w}\\cdot{w}\\sin\\theta={L(Q(w*w,2))}\\sin\\theta")
        fp = f"{L(Q(w*w,2))}\\cos\\theta"; slv = "$S'(\\theta)=0$ នាំឲ្យ $\\cos\\theta=0$ ដូចនេះ $\\theta=\\frac{\\pi}{2}$ ក្នុងចន្លោះ $(0;\\pi)$ ។"
        hi = PI
    t, dg, ck, val = tail(F, "S", "\\theta", 0, hi, c, "max", Fpf=fp, solve=slv, style="sign")
    t = t.replace("x", "\\theta") if False else t
    sol = setup + t + f"\n{fin()}\n" + BOX(f"\\theta={L(c)},\\quad S_{{\\max}}={L(val)}")
    add("optimization_trig", "bacii", (mode, w), prob, sol, f"\\theta={L(c)}", ck, dg)

def g_drug():
    b = P(Q(1, 2), Q(1, 3), Q(1, 4), Q(1, 5), 1, 2, Q(1, 10)); a = rng.randint(2, 60)
    n = P(1, 1, 2)
    ctx = P(("កំហាប់ថ្នាំក្នុងឈាម", "C", "ម៉ោង", "t"), ("ចំនួនអ្នកចូលមើលវីដេអូមួយ (ពាន់នាក់)", "N", "ថ្ងៃ", "t"), ("កម្រិតជាតិអាល់កុលក្នុងឈាម", "C", "ម៉ោង", "t"), ("ចំនួនអ្នកឆ្លងជំងឺផ្តាសាយក្នុងសាលាមួយ", "N", "សប្តាហ៍", "t"))
    F = a * x**n * sp.exp(-b * x); c = sp.Integer(n) / b
    nm = ctx[1]
    prob = P(f"{ctx[0]}ក្រោយពេល $t$ {ctx[2]} ត្រូវបានគំរូដោយ ${nm}(t)={L(F,'t')}$ ដែល $t\\ge0$ ។ តើនៅពេលណាដែលវាឡើងដល់កម្រិតខ្ពស់បំផុត? គណនាកម្រិតនោះ ។",
             f"គេឲ្យ ${nm}(t)={L(F,'t')}$ ជា{ctx[0]}ក្រោយ $t$ {ctx[2]} ។ រកអតិបរមានៃ ${nm}$ លើ $[0;+\\infty)$ ។")
    Fp = sp.factor(sp.diff(F, x))
    uv = f"តាមរូបមន្ត $(uv)'=u'v+uv'$ និង $(e^{{u}})'=u'e^{{u}}$ ។\n"
    t, dg, ck, val = tail(F, nm, "t", 0, sp.oo, c, "max", Fpf=L(Fp, "t"), style=P("table", "sign"),
                          solve=f"ដោយ $e^{{{L(-b*x,'t')}}}>0$ ជានិច្ច ${nm}'(t)$ មានសញ្ញាតាមកត្តាពហុធា ហើយ ${nm}'(t)=0$ ចំពោះ $t>0$ នាំឲ្យ $t={L(c)}$ ។")
    sol = uv + t + f"\n{fin()} កម្រិតខ្ពស់បំផុតកើតឡើងនៅ ៖\n" + BOX(f"t={L(c)}") + f"{ctx[2]} ហើយមានតម្លៃ ${L(val)}$ ។"
    def dgm(rid):
        vmax = float(val)
        return dg + [graph(rid, F, 0, float(c) * 4, 0, vmax * 1.3, "ខ្សែកោងឡើងដល់អតិបរមា រួចចុះខិតជិតសូន្យ", var="t", yname=nm, pts=[(c, val)])]
    add("optimization_exp_log", P("medium", "hard", "bacii"), F, prob, sol, f"t={L(c)}", ck, dgm if rng.random() < .7 else dg)

def g_lnprofit():
    a = rng.randint(2, 60); xs = rng.randint(2, 30); b = Q(a, xs)
    c0 = rng.randint(0, 30)
    F = a * sp.log(x) - b * x + c0
    mode = P("profit", "yield")
    ctx = "ប្រាក់ចំណេញ (លានរៀល) ពេលវិនិយោគ $x$ លានរៀលលើការផ្សាយពាណិជ្ជកម្ម" if mode == "profit" else "ផលស្រូវ (តោន) ពេលប្រើជី $x$ បាវ"
    prob = f"{ctx} ត្រូវបានប៉ាន់ស្មានដោយ $f(x)={L(F)}$ ចំពោះ $x\\ge1$ ។ រក $x$ ដែលធ្វើឲ្យ $f(x)$ អតិបរមា ហើយគណនាតម្លៃអតិបរមានោះ ។"
    t, dg, ck, val = tail(F, "f", "x", 1, sp.oo, sp.Integer(xs), "max", Fpf=f"\\frac{{{a}}}{{x}}-{L(b)}", solve=f"$f'(x)=0$ នាំឲ្យ $x={xs}$ ។", style=P("second", "sign"))
    sol = f"ដែនកំណត់ $[1;+\\infty)$ ។ តាមរូបមន្ត $(\\ln x)'=\\frac{{1}}{{x}}$ ។\n" + t + f"\n{fin()}\n" + BOX(f"x={xs},\\quad f_{{\\max}}={L(val)}")
    add("optimization_exp_log", "medium", F, prob, sol, f"x={xs}", ck, dg)

def g_slant():
    Ls = 3 * rng.randint(1, 20); 
    # cone of slant length; h = L/sqrt3
    V = PI / 3 * x * (Ls**2 - x**2); c = Ls / sp.sqrt(3)
    item = P("មួកកោណ", "ពែងក្រដាសរាងកោណ", "ជីវ៉ាហ្វារាងកោណ", "ក្រវិលកោណ")
    item = P("មួកកោណ", "ពែងក្រដាសរាងកោណ", "ចង្រ្កានរាងកោណ") if False else P("មួកកោណ", "ពែងក្រដាសរាងកោណ", "កោណដាក់ការ៉េម")
    prob = f"គេធ្វើ{item}ដែលមានបន្ទាត់បង្កើត ${Ls}$ សង់ទីម៉ែត្រ ។ រកកម្ពស់កោណ ដើម្បីឲ្យមាឌធំបំផុត រួចគណនាមាឌនោះ ។"
    t, dg, ck, val = tail(V, "V", "h", 0, Ls, c, "max", Fpf=L(sp.expand(sp.diff(V, x)), "h"), solve=f"$V'(h)=0$ នាំឲ្យ $h^2={L(Q(Ls**2,3))}$ ដូចនេះ $h={L(c)}$ (ព្រោះ $h>0$) ។", style=P("sign", "table"))
    sol = (f"តាង $h$ ជាកម្ពស់ និង $r$ ជាកាំបាត ($0<h<{Ls}$) ។ តាមទ្រឹស្តីបទពីតាករ $r^2={Ls*Ls}-h^2$ ។\nមាឌកោណ ៖\n" + DM(f"V(h)=\\frac{{1}}{{3}}\\pi r^2h=\\frac{{\\pi}}{{3}}h({Ls*Ls}-h^2)") + t + f"\n{fin()}\n" + BOX(f"h={L(c)},\\quad V_{{\\max}}={L(val)}") + "ឯកតាគឺសង់ទីម៉ែត្រ និងសង់ទីម៉ែត្រគូប ។")
    add("optimization_geometry", "hard", Ls, prob, sol, f"h={L(c)}", ck, dg + [fig(fig_cone("r", "h"), "កោណមានកាំបាត r និងកម្ពស់ h")])

def g_wire():
    Lw = rng.choice(range(8, 241, 8)); mode = P("two_sq", "tri_area")
    if mode == "two_sq":
        F = (x / 4)**2 + ((Lw - x) / 4)**2; c = sp.Integer(Lw // 2)
        prob = f"ខ្សែលួសមួយប្រវែង ${Lw}$ សង់ទីម៉ែត្រ ត្រូវកាត់ជាពីរកំណាត់ ហើយកំណាត់នីមួយៗពត់ជាការ៉េ ។ តើត្រូវកាត់ត្រង់ណា ទើបផលបូកក្រឡាផ្ទៃការ៉េទាំងពីរតូចបំផុត?"
        setup = f"តាង $x$ ជាប្រវែងកំណាត់ទី១ ($0<x<{Lw}$) ។ ការ៉េទាំងពីរមានជ្រុង $\\frac{{x}}{{4}}$ និង $\\frac{{{Lw}-x}}{{4}}$ ។\n"
        t, dg, ck, val = tail(F, "S", "x", 0, Lw, c, "min", Fpf=L(sp.expand(sp.diff(F, x))))
        sol = setup + DM(f"S(x)=\\frac{{x^2}}{{16}}+\\frac{{({Lw}-x)^2}}{{16}}") + t + f"\n{fin()} ត្រូវកាត់កណ្តាលខ្សែ ៖\n" + BOX(f"x={c},\\quad S_{{\\min}}={L(val)}")
    else:
        # right triangle legs sum = Lw : area max
        F = x * (Lw - x) / 2; c = sp.Integer(Lw // 2)
        prob = f"ត្រីកោណកែងមួយមានផលបូកជ្រុងជាប់មុំកែងទាំងពីរស្មើ ${Lw}$ សង់ទីម៉ែត្រ ។ រកប្រវែងជ្រុងទាំងពីរ ដើម្បីឲ្យក្រឡាផ្ទៃធំបំផុត ។"
        t, dg, ck, val = tail(F, "S", "x", 0, Lw, c, "max", Fpf=L(sp.expand(sp.diff(F, x))))
        sol = f"តាងជ្រុងជាប់មុំកែងទាំងពីរ $x$ និង ${Lw}-x$ ($0<x<{Lw}$) ។\n" + DM(f"S(x)=\\frac{{1}}{{2}}x({Lw}-x)") + t + f"\n{fin()} ត្រីកោណកែងសមបាត ៖\n" + BOX(f"x={c},\\quad S_{{\\max}}={L(val)}")
    add("optimization_geometry", "easy", (mode, Lw), prob, sol, f"x={c}", ck, dg)

# =============================== MOTION ===============================
MOVERS = ["ឡានក្រុង", "ម៉ូតូ", "រថភ្លើង", "ទូកម៉ាស៊ីន", "កង់", "កូនរ៉ូបូត", "រថយន្តដឹកទំនិញ", "ភាគល្អិត"]
def s_units(): return P(("ម៉ែត្រ", "វិនាទី", "ម៉ែត្រក្នុងមួយវិនាទី", "ម៉ែត្រក្នុងមួយវិនាទីការ៉េ"), ("គីឡូម៉ែត្រ", "ម៉ោង", "គីឡូម៉ែត្រក្នុងមួយម៉ោង", "គីឡូម៉ែត្រក្នុងមួយម៉ោងការ៉េ"))

def g_cubic_motion():
    p, q = sorted(rng.sample(range(1, 11), 2))
    k = P(1, 1, 2, Q(1, 3)); s0 = rng.randint(0, 12)
    v = 3 * k * (x - p) * (x - q)
    Sf = sp.expand(sp.integrate(v, x)) + s0
    if any(cf.q > 2 for cf in sp.Poly(Sf, x).coeffs()): return
    mv = P(*MOVERS); u = ("ម៉ែត្រ", "វិនាទី", "ម៉ែត្រក្នុងមួយវិនាទី", "ម៉ែត្រក្នុងមួយវិនាទីការ៉េ")
    V = sp.diff(Sf, x); A = sp.diff(V, x); ve = sp.expand(V)
    mode = P("full", "full", "accel", "dist")
    S = L(Sf, "t")
    dv = f"ល្បឿនជាដេរីវេនៃទីតាំង ហើយសំទុះជាដេរីវេនៃល្បឿន ។\n" + DM(f"v(t)=s'(t)={L(ve,'t')}") + DM(f"a(t)=v'(t)={L(A,'t')}")
    tab = vt("t", "s", ["0", str(p), str(q), "+\\infty"], ["", "+", "0", "-", "0", "+", ""], [L(Sf.subs(x, 0)), "\\nearrow", L(Sf.subs(x, p)), "\\searrow", L(Sf.subs(x, q)), "\\nearrow", "+\\infty"])
    ck = [check(f"diff({st(Sf)},x)", st(ve), "ល្បឿន"), check(f"diff({st(Sf)},x,2)", st(A), "សំទុះ")]
    if mode == "full":
        prob = P(f"{mv}មួយធ្វើចលនាត្រង់ ហើយទីតាំងនៅខណៈ $t\\ge0$ ({u[1]}) គឺ $s(t)={S}$ ({u[0]}) ។\nក. រកល្បឿន និងសំទុះ ។\nខ. តើនៅខណៈណាដែលវាឈប់មួយភ្លែត?\nគ. កំណត់ចន្លោះពេលដែលវាធ្វើដំណើរថយក្រោយ ។",
                 f"ទីតាំងនៃ{mv}លើផ្លូវត្រង់ត្រូវបានផ្តល់ដោយ $s(t)={S}$ ។ សិក្សាចលនា៖ រក $v(t)$ និង $a(t)$ រួចរកខណៈដែលល្បឿនស្មើសូន្យ និងទិសដៅចលនាក្នុងចន្លោះនីមួយៗ ។")
        sol = (dv + f"គេដាក់ $v(t)=0$ ៖ ${L(3*k)}(t-{p})(t-{q})=0$ នាំឲ្យ $t={p}$ ឬ $t={q}$ ។\nតារាងអថេរភាពនៃទីតាំង ៖\n" + DM(tab)
               + f"ចំពោះ $0\\le t<{p}$ និង $t>{q}$ គេបាន $v(t)>0$ ដូច្នេះវាទៅមុខ ។ ចំពោះ ${p}<t<{q}$ គេបាន $v(t)<0$ ដូច្នេះវាថយក្រោយ ។\n{fin()} វាឈប់មួយភ្លែតនៅ ៖\n" + BOX(f"t={p},\\quad t={q}") + f"ហើយថយក្រោយក្នុងចន្លោះ $({p};{q})$ ។")
        ans = f"t={p},\\ t={q}"
        ck += [check(f"diff({st(Sf)},x).subs(x,{p})", "0"), check(f"diff({st(Sf)},x).subs(x,{q})", "0")]
        dg = lambda rid: [vdiag(tab, "តារាងអថេរភាពនៃទីតាំង")] + ([graph(rid, Sf, 0, q + 1.5, float(min(Sf.subs(x, 0), Sf.subs(x, q))) - 2, float(Sf.subs(x, q + 1.5)) + 2, "ក្រាបទីតាំងតាមពេល", var="t", yname="s", pts=[(p, Sf.subs(x, p)), (q, Sf.subs(x, q))])] if rng.random() < .6 else [])
    elif mode == "accel":
        tc = Q(p + q, 2); vm = ve.subs(x, tc)
        prob = f"ទីតាំងនៃ{mv}គឺ $s(t)={S}$ ។ រកខណៈដែលសំទុះស្មើសូន្យ រួចគណនាល្បឿននៅខណៈនោះ ។ តើល្បឿននោះជាតម្លៃអប្បបរមានៃ $v(t)$ ឬទេ?"
        sol = (dv + f"$a(t)=0$ នាំឲ្យ $t={L(tc)}$ ។\nល្បឿននៅខណៈនោះ ៖ $v({L(tc)})={L(vm)}$ ។\nដោយ $a(t)<0$ ចំពោះ $t<{L(tc)}$ និង $a(t)>0$ ចំពោះ $t>{L(tc)}$ នោះ $v$ ចុះហើយកើន ។\n{fin()} ៖\n" + BOX(f"t={L(tc)},\\quad v_{{\\min}}={L(vm)}") + f"ជាតម្លៃអប្បបរមានៃល្បឿន ({u[2]}) ។")
        ans = f"t={L(tc)},\\ v={L(vm)}"
        ck += [check(f"diff({st(Sf)},x,2).subs(x,{st(tc)})", "0"), check(f"diff({st(Sf)},x).subs(x,{st(tc)})", st(vm))]
        dg = []
    else:
        d1 = abs(Sf.subs(x, p) - Sf.subs(x, 0)); d2 = abs(Sf.subs(x, q) - Sf.subs(x, p)); Te = q + 1 + rng.randint(0, 2); d3 = abs(Sf.subs(x, Te) - Sf.subs(x, q))
        tot = d1 + d2 + d3
        prob = f"ភាគល្អិតមួយផ្លាស់ទីលើអ័ក្សមួយតាម $s(t)={S}$ ។ គណនាចម្ងាយសរុបដែលវាបានធ្វើដំណើរពី $t=0$ ដល់ $t={Te}$ (មិនមែនគម្លាតទីតាំងទេ) ។"
        sol = (f"ល្បឿន ៖\n" + DM(f"v(t)=s'(t)={L(ve,'t')}={L(3*k)}(t-{p})(t-{q})") + f"ភាគល្អិតប្តូរទិសនៅ $t={p}$ និង $t={q}$ ។ ដូច្នេះត្រូវគណនាចម្ងាយតាមដុំៗ ៖\n"
               + f"$s(0)={L(Sf.subs(x,0))}$, $s({p})={L(Sf.subs(x,p))}$, $s({q})={L(Sf.subs(x,q))}$, $s({Te})={L(Sf.subs(x,Te))}$ ។\n"
               + DM(f"d=|s({p})-s(0)|+|s({q})-s({p})|+|s({Te})-s({q})|={L(d1)}+{L(d2)}+{L(d3)}={L(tot)}") + f"{fin()} ចម្ងាយសរុបគឺ ៖\n" + BOX(f"d={L(tot)}"))
        ans = f"d={L(tot)}"
        F = st(Sf)
        ck += [check(f"Abs(({F}).subs(x,{p})-({F}).subs(x,0))+Abs(({F}).subs(x,{q})-({F}).subs(x,{p}))+Abs(({F}).subs(x,{Te})-({F}).subs(x,{q}))", st(tot), "ចម្ងាយសរុប")]
        dg = []
    add("motion_polynomial", P("medium", "hard"), (mode, Sf), prob, sol, ans, ck, dg)

THROW = ["បាល់", "ដុំថ្ម", "គ្រាប់កាំជ្រួច", "ព្រួញ", "បាល់ទាត់"]
def g_throw():
    v0 = rng.choice(range(5, 81, 5)); h0 = rng.choice([0, 0, 5, 10, 15, 20, 25, 30, 40, 60]); g = 5
    H = h0 + v0 * x - g * x**2
    tm = Q(v0, 2 * g); hm = H.subs(x, tm)
    disc = sp.sqrt(v0**2 + 4 * g * h0)
    if not disc.is_rational: return
    tl = (v0 + disc) / (2 * g); vl = -(disc)
    who = P(f"{P(*PEOPLE)}គប់{P(*THROW)}ឡើងលើ", f"គេបាញ់{P(*THROW)}ឡើងបញ្ឈរ", f"ក្មេងម្នាក់គប់{P(*THROW)}ពីលើដំបូលផ្ទះ" if h0 else f"ក្មេងម្នាក់គប់{P(*THROW)}ពីដី")
    prob = P(f"{who} ។ កម្ពស់ពីដីក្រោយ $t$ វិនាទីគឺ $h(t)={L(H,'t')}$ (ម៉ែត្រ) ។ រកកម្ពស់ខ្ពស់បំផុត ពេលវេលាធ្លាក់ដល់ដី និងល្បឿននៅពេលប៉ះដី ។",
             f"{who} ដោយកម្ពស់ $h(t)={L(H,'t')}$ ម៉ែត្រ នៅខណៈ $t$ វិនាទី ។\nក. គណនាល្បឿន $v(t)$ ។\nខ. តើវាឡើងដល់កម្ពស់ខ្ពស់បំផុតនៅពេលណា? ខ្ពស់ប៉ុន្មាន?\nគ. តើវាធ្លាក់ដល់ដីនៅពេលណា ហើយក្នុងល្បឿនប៉ុន្មាន?")
    V = sp.diff(H, x)
    sol = ("ល្បឿនជាដេរីវេនៃកម្ពស់ ៖\n" + DM(f"v(t)=h'(t)={L(V,'t')}") + f"នៅកំពូល ល្បឿនស្មើសូន្យ ៖ $v(t)=0$ នាំឲ្យ $t={L(tm)}$ ។\nកម្ពស់នៅខណៈនោះ ៖\n" + DM(f"h({L(tm)})={L(hm)}")
           + f"ពេលប៉ះដី $h(t)=0$ ៖ ${L(H,'t')}=0$ ។ ដោយ $t>0$ គេយកឫសវិជ្ជមាន $t={L(tl)}$ ។\nល្បឿនពេលប៉ះដី ៖ $v({L(tl)})={L(V.subs(x,tl))}$ ម៉ែត្រក្នុងមួយវិនាទី (សញ្ញាដកបញ្ជាក់ថាកំពុងធ្លាក់ចុះ) ។\n"
           + f"{fin()} ៖\n" + BOX(f"h_{{\\max}}={L(hm)},\\quad t={L(tl)},\\quad v={L(V.subs(x,tl))}"))
    ck = [dchk(H, V, "ល្បឿន"), d0chk(H, tm), vchk(H, tm, hm), vchk(H, tl, 0, "ប៉ះដី"), check(f"diff({st(H)},x).subs(x,{st(tl)})", st(V.subs(x, tl)))]
    def dg(rid):
        return [graph(rid, H, 0, float(tl) + .5, 0, float(hm) * 1.2, "ក្រាបកម្ពស់តាមពេល រាងប៉ារ៉ាបូល", var="t", yname="h", pts=[(tm, hm)])] if rng.random() < .6 else []
    add("motion_vertical", P("easy", "medium"), H, prob, sol, f"h_{{\\max}}={L(hm)}", ck, dg)

def g_brake():
    v0 = rng.choice(range(10, 41, 2)); dec = P(2, 4, 5, 8, 10)
    Sb = v0 * x - Q(dec, 2) * x**2
    ts = Q(v0, dec); ds = Sb.subs(x, ts)
    mv = P("រថយន្ត", "ឡានក្រុង", "ម៉ូតូ", "រថភ្លើង")
    road = P("លើផ្លូវជាតិលេខ ៥", "លើផ្លូវជាតិលេខ ៦", "លើស្ពានជ្រោយចង្វារ", "លើផ្លូវល្បឿនលឿនភ្នំពេញ-ព្រះសីហនុ", "លើមហាវិថីព្រះនរោត្តម")
    prob = P(f"{mv}មួយ{road} ចាប់ផ្តើមហ្វ្រាំង ហើយចម្ងាយដែលទៅបានក្រោយហ្វ្រាំង $t$ វិនាទីគឺ $s(t)={L(Sb,'t')}$ ម៉ែត្រ ។ តើវាត្រូវការពេលប៉ុន្មានទើបឈប់? ហើយទៅបានឆ្ងាយប៉ុន្មានក្រោយហ្វ្រាំង?",
             f"អ្នកបើក{mv}{road} ឃើញឧបសគ្គ ក៏ហ្វ្រាំងភ្លាម ។ បើ $s(t)={L(Sb,'t')}$ (ម៉ែត្រ) ជាចម្ងាយក្រោយហ្វ្រាំង រកល្បឿនដើម សំទុះ និងចម្ងាយហ្វ្រាំង ។")
    V = sp.diff(Sb, x)
    sol = (f"ល្បឿននៅខណៈ $t$ ៖\n" + DM(f"v(t)=s'(t)={L(V,'t')}") + f"ល្បឿនដើម $v(0)={v0}$ ម៉ែត្រក្នុងមួយវិនាទី ហើយសំទុះ $a(t)=v'(t)={-dec}$ ម៉ែត្រក្នុងមួយវិនាទីការ៉េ ។\nរថឈប់ពេល $v(t)=0$ នាំឲ្យ $t={L(ts)}$ វិនាទី ។\nចម្ងាយហ្វ្រាំង ៖\n" + DM(f"s({L(ts)})={L(ds)}") + f"{fin()} រថឈប់ក្រោយ ${L(ts)}$ វិនាទី និងទៅបានចម្ងាយ ៖\n" + BOX(f"s={L(ds)}") + "ម៉ែត្រ ។")
    add("motion_braking", "easy", Sb, prob, sol, f"t={L(ts)},\\ s={L(ds)}", [dchk(Sb, V, "ល្បឿន"), d0chk(Sb, ts), vchk(Sb, ts, ds), check(f"diff({st(Sb)},x,2)", str(-dec), "សំទុះ")])

def g_harmonic():
    A = rng.randint(2, 12); w = P(1, 2, 3, 4, Q(1, 2)); ph = P(0, 0, PI / 6, PI / 4, PI / 3)
    fn = P(sp.sin, sp.cos)
    Xf = A * fn(w * x + ph)
    t0 = P(PI / 6, PI / 4, PI / 3, PI / 2) / w
    V = sp.diff(Xf, x); Ac = sp.diff(V, x)
    v0 = sp.simplify(V.subs(x, t0)); a0 = sp.simplify(Ac.subs(x, t0)); x0 = sp.simplify(Xf.subs(x, t0))
    if rng.random() < .35: ctx = P("ទូករសាត់លើរលកឡើងចុះតាម", "ចុងរោលនៃនាឡិកាញ័រតាម")
    ctx = P("ចំណុចមួយលើខ្សែរំញ័រ", "ដុំទម្ងន់ព្យួរនឹងរ៉ឺស័រ", "ទូករសាត់ឡើងចុះលើរលក")
    prob = f"{ctx} មានទីតាំង $y(t)={L(Xf,'t')}$ ។ គណនាល្បឿន និងសំទុះ រួចបង្ហាញថា $y''(t)+{L(w**2)}y(t)=0$ ។ គណនាតម្លៃទាំងនោះនៅខណៈ $t={L(t0)}$ ។"
    sol = ("តាមរូបមន្ត $(\\sin u)'=u'\\cos u$ និង $(\\cos u)'=-u'\\sin u$ ៖\n" + DM(f"v(t)=y'(t)={L(V,'t')}") + DM(f"a(t)=y''(t)={L(Ac,'t')}") + f"ដោយ $a(t)=-{L(w**2)}\\cdot{L(Xf,'t')}=-{L(w**2)}y(t)$ នោះ $y''(t)+{L(w**2)}y(t)=0$ ។\nនៅខណៈ $t={L(t0)}$ ៖\n" + DM(f"y={L(x0)},\\quad v={L(v0)},\\quad a={L(a0)}") + f"{fin()}\n" + BOX(f"v\\left({L(t0)}\\right)={L(v0)},\\quad a\\left({L(t0)}\\right)={L(a0)}"))
    F = st(Xf)
    ck = [check(f"diff({F},x)", st(V)), check(f"diff({F},x,2)+{st(w**2)}*({F})", "0", "សមីការ"), check(f"diff({F},x).subs(x,{st(t0)})", st(v0)), check(f"diff({F},x,2).subs(x,{st(t0)})", st(a0))]
    add("motion_trig", P("medium", "hard"), (Xf, t0), prob, sol, f"v={L(v0)},\\ a={L(a0)}", ck)

def g_exp_motion():
    v_inf = rng.randint(5, 40); k = P(Q(1, 2), 1, 2, Q(1, 4), Q(1, 5))
    mode = P("damp", "rational", "logs")
    if mode == "damp":
        Sf = v_inf * (x + (sp.exp(-k * x) - 1) / k)
        V = sp.diff(Sf, x); t0 = P(1, 2, 3, 4) / k
        prob = f"ទូកមួយចាប់ផ្តើមចេញដំណើរពីនៅស្ងៀម ដោយទីតាំង $s(t)={L(Sf,'t')}$ ។ រកល្បឿន $v(t)$ សំទុះ $a(t)$ និងលីមីតនៃល្បឿនកាលណា $t\\to+\\infty$ ។"
        Lm = v_inf
        Ac = sp.diff(V, x)
        sol = ("តាមរូបមន្ត $(e^{u})'=u'e^{u}$ ៖\n" + DM(f"v(t)=s'(t)={L(V,'t')}") + DM(f"a(t)=v'(t)={L(Ac,'t')}") + f"ដោយ $\\lim_{{t\\to+\\infty}}e^{{{L(-k*x,'t')}}}=0$ នោះ ៖\n" + DM(f"\\lim_{{t\\to+\\infty}}v(t)={v_inf}") + f"ដោយ $a(t)>0$ ជានិច្ច ល្បឿនកើនជានិច្ច ហើយខិតជិត ${v_inf}$ ។\n{fin()}\n" + BOX(f"v(t)={L(V,'t')},\\quad a(t)={L(Ac,'t')},\\quad \\lim_{{t\\to+\\infty}}v(t)={v_inf}"))
        ck = [dchk(Sf, V, "ល្បឿន"), check(f"diff({st(Sf)},x,2)", st(Ac), "សំទុះ"), check(f"limit(diff({st(Sf)},x),x,oo)", str(v_inf), "លីមីត")]
        ans = L(V, "t")
        key = Sf
    elif mode == "rational":
        a = rng.randint(2, 30); b = rng.randint(1, 9)
        Sf = a * x**2 / (x + b)
        V = sp.together(sp.diff(Sf, x)); t0 = rng.randint(1, 6)
        v0 = V.subs(x, t0)
        prob = f"ទីតាំងនៃរថយន្តមួយគឺ $s(t)={L(Sf,'t')}$ ចំពោះ $t\\ge0$ ។ គណនាល្បឿននៅខណៈ $t={t0}$ រួចបង្ហាញថារថយន្តតែងទៅមុខជានិច្ច ។"
        sol = (f"តាមរូបមន្ត $\\left(\\frac{{u}}{{v}}\\right)'=\\frac{{u'v-uv'}}{{v^2}}$ ៖\n" + DM(f"v(t)=s'(t)=\\frac{{{2*a}t(t+{b})-{a}t^2}}{{(t+{b})^2}}=\\frac{{{a}t(t+{2*b})}}{{(t+{b})^2}}") + f"ដោយ $t\\ge0$ នោះភាគយកនិងភាគបែងមិនអវិជ្ជមាន ហើយ $v(t)>0$ ចំពោះ $t>0$ ។ ដូច្នេះរថយន្តទៅមុខជានិច្ច ។\nនៅខណៈ $t={t0}$ ៖ $v({t0})={L(v0)}$ ។\n{fin()}\n" + BOX(f"v({t0})={L(v0)}"))
        ck = [dchk(Sf, a * x * (x + 2 * b) / (x + b)**2, "ល្បឿន"), check(f"diff({st(Sf)},x).subs(x,{t0})", st(v0))]
        ans = f"v({t0})={L(v0)}"; key = (Sf, t0)
    else:
        a = rng.randint(2, 40); b = rng.randint(1, 9)
        Sf = a * sp.log(1 + x / b)
        t0 = b * rng.randint(1, 7); v0 = sp.diff(Sf, x).subs(x, t0)
        V = a / (x + b)
        prob = f"ភាគល្អិតមួយមានទីតាំង $s(t)={L(Sf,'t')}$ ។ រកល្បឿន និងសំទុះនៅខណៈ $t={t0}$ ។"
        Ac = sp.diff(V, x); a0 = Ac.subs(x, t0)
        sol = (f"តាមរូបមន្ត $(\\ln u)'=\\frac{{u'}}{{u}}$ ៖\n" + DM(f"v(t)=s'(t)=\\frac{{{a}}}{{t+{b}}}") + DM(f"a(t)=v'(t)=-\\frac{{{a}}}{{(t+{b})^2}}") + f"នៅខណៈ $t={t0}$ ៖\n{fin()}\n" + BOX(f"v({t0})={L(v0)},\\quad a({t0})={L(a0)}"))
        ck = [dchk(Sf, V, "ល្បឿន"), check(f"diff({st(Sf)},x,2).subs(x,{t0})", st(a0))]
        ans = f"v={L(v0)},\\ a={L(a0)}"; key = (Sf, t0)
    add("motion_transcendental", P("medium", "hard"), key, prob, sol, ans, ck)

def g_avg_inst():
    a = rng.randint(1, 5); b = rng.randint(1, 12); c = rng.randint(0, 9)
    t1 = rng.randint(0, 5); t2 = t1 + P(2, 4, 6)
    Sf = a * x**2 + b * x + c
    avg = (Sf.subs(x, t2) - Sf.subs(x, t1)) / (t2 - t1); tc = Q(t1 + t2, 2)
    mv = P(*MOVERS)
    prob = P(f"{mv}មានទីតាំង $s(t)={L(Sf,'t')}$ (ម៉ែត្រ) ។ គណនាល្បឿនមធ្យមក្នុងចន្លោះ $[{t1};{t2}]$ ហើយរកខណៈ $t$ ដែលល្បឿនខណៈស្មើល្បឿនមធ្យមនោះ ។")
    V = sp.diff(Sf, x)
    sol = (f"ល្បឿនមធ្យម ៖\n" + DM(f"v_m=\\frac{{s({t2})-s({t1})}}{{{t2}-{t1}}}=\\frac{{{L(Sf.subs(x,t2))}-{L(Sf.subs(x,t1))}}}{{{t2-t1}}}={L(avg)}") + f"ល្បឿនខណៈ $v(t)=s'(t)={L(V,'t')}$ ។\n$v(t)={L(avg)}$ នាំឲ្យ $t={L(tc)}$ ។\n{fin()}\n" + BOX(f"v_m={L(avg)},\\quad t={L(tc)}") + "ខណៈនេះជាចំណុចកណ្តាលនៃចន្លោះពេល ។")
    F = st(Sf)
    add("motion_average", "easy", (Sf, t1, t2), prob, sol, f"v_m={L(avg)},\\ t={L(tc)}", [check(f"(({F}).subs(x,{t2})-({F}).subs(x,{t1}))/{t2-t1}", st(avg), "ល្បឿនមធ្យម"), check(f"diff({F},x).subs(x,{st(tc)})", st(avg), "ល្បឿនខណៈ")])

# =============================== RATES OF CHANGE ===============================
def g_rate_growth():
    mode = P("pop", "cool", "tank", "marg", "avg", "conc", "geom", "elect")
    if mode == "pop":
        P0 = rng.choice(range(100, 5001, 100)); k = P(Q(1, 2), Q(1, 4), Q(1, 10), Q(1, 5), Q(3, 10), 1); t0 = rng.randint(1, 8)
        Ff = P0 * sp.exp(k * x); v = sp.diff(Ff, x).subs(x, t0)
        thing = P("បាក់តេរីក្នុងទឹកដោះគោជូរ", "ត្រីក្នុងស្រះ", "ជីវសាស្ត្រនៃសារាយក្នុងបឹង", "អ្នកប្រើកម្មវិធីទូរស័ព្ទមួយ")
        thing = P("បាក់តេរីក្នុងទឹកដោះគោជូរ", "ត្រីក្នុងស្រះ", "អ្នកប្រើកម្មវិធីទូរស័ព្ទមួយ")
        prob = f"ចំនួន{thing}ក្រោយ $t$ ថ្ងៃ គឺ $N(t)={L(Ff,'t')}$ ។ គណនាអត្រាបម្រែបម្រួលនៃ $N$ នៅ $t={t0}$ រួចបង្ហាញថា $N'(t)={L(k)}N(t)$ ។"
        sol = f"តាមរូបមន្ត $(e^{{kt}})'=ke^{{kt}}$ ៖\n" + DM(f"N'(t)={L(sp.diff(Ff,x),'t')}={L(k)}\\cdot{L(Ff,'t')}={L(k)}N(t)") + f"អត្រាកំណើននៅ $t={t0}$ ៖\n{fin()}\n" + BOX(f"N'({t0})={L(v)}") + "ក្នុងមួយថ្ងៃ ។"
        ck = [dchk(Ff, sp.diff(Ff, x)), check(f"diff({st(Ff)},x)-{st(k)}*({st(Ff)})", "0"), check(f"diff({st(Ff)},x).subs(x,{t0})", st(v))]
        ans = f"N'({t0})={L(v)}"; key = (mode, Ff, t0)
    elif mode == "cool":
        Ta = P(25, 28, 30, 20); T0 = P(80, 90, 95, 100, 70); k = P(Q(1, 10), Q(1, 5), Q(1, 20), Q(1, 2)); 
        Ff = Ta + (T0 - Ta) * sp.exp(-k * x); tt = rng.randint(2, 20)
        drink = P("កាហ្វេក្តៅ", "ទឹកតែក្តៅ", "ទឹកក្តៅ")
        v = sp.diff(Ff, x).subs(x, tt)
        Ttarget = Ta + Q(T0 - Ta, 2)
        prob = f"កែវ{drink}មួយត្រជាក់ទៅតាម $T(t)={L(Ff,'t')}$ (អង្សាសេ) ក្រោយ $t$ នាទី ។ គណនាល្បឿនធ្លាក់សីតុណ្ហភាពនៅ $t={tt}$ និងរក $\\lim_{{t\\to+\\infty}}T(t)$ ។"
        sol = "ដេរីវេនៃសីតុណ្ហភាព ៖\n" + DM(f"T'(t)={L(sp.diff(Ff,x),'t')}") + f"នៅ $t={tt}$ ៖ $T'({tt})={L(v)}$ អង្សាសេក្នុងមួយនាទី ។ សញ្ញាដកបញ្ជាក់ថាសីតុណ្ហភាពកំពុងថយ ។\nដោយ $\\lim_{{t\\to+\\infty}}e^{{{L(-k*x,'t')}}}=0$ នោះ $\\lim_{{t\\to+\\infty}}T(t)={Ta}$ ជាសីតុណ្ហភាពបន្ទប់ ។\n{fin()}\n" + BOX(f"T'({tt})={L(v)},\\quad \\lim_{{t\\to+\\infty}}T(t)={Ta}")
        ck = [check(f"diff({st(Ff)},x).subs(x,{tt})", st(v)), check(f"limit({st(Ff)},x,oo)", str(Ta))]
        ans = f"T'({tt})={L(v)}"; key = (mode, Ff, tt)
    elif mode == "tank":
        a = rng.randint(1, 6); b = rng.randint(10, 60); V0 = rng.choice(range(200, 2001, 100)); tt = rng.randint(1, 9)
        T = b + 2 * a * rng.randint(1, 5)
        Vt = V0 + T * x - a * x**2 if False else V0 + b * x - a * x**2
        tm = Q(b, 2 * a); r = sp.diff(Vt, x).subs(x, tt)
        where = P("អាងទឹកមួយនៅភូមិ", "អាងស្តុកទឹកកសិកម្ម", "ធុងទឹកសាលា", "ស្រះនៅវត្ត")
        prob = f"បរិមាណទឹកក្នុង{where}ក្រោយ $t$ ម៉ោង គឺ $V(t)={L(Vt,'t')}$ លីត្រ ។ រកល្បឿនបម្រែបម្រួលបរិមាណនៅ $t={tt}$ ។ តើនៅពេលណាដែលទឹកឈប់កើន?"
        sol = "អត្រាបម្រែបម្រួលជាដេរីវេ ៖\n" + DM(f"V'(t)={L(sp.diff(Vt,x),'t')}") + f"នៅ $t={tt}$ ៖ $V'({tt})={L(r)}$ លីត្រក្នុងមួយម៉ោង ។\nទឹកឈប់កើនពេល $V'(t)=0$ នាំឲ្យ $t={L(tm)}$ ម៉ោង ។\n{fin()}\n" + BOX(f"V'({tt})={L(r)},\\quad t={L(tm)}")
        ck = [check(f"diff({st(Vt)},x).subs(x,{tt})", st(r)), d0chk(Vt, tm)]
        ans = f"V'({tt})={L(r)}"; key = (mode, Vt, tt)
    elif mode == "marg":
        a = P(Q(1, 2), 1, 2, Q(1, 10)); b = rng.randint(5, 50); c = rng.choice(range(100, 1001, 50)); q = rng.choice(range(10, 201, 10))
        Cc = a * x**2 + b * x + c
        mc = sp.diff(Cc, x).subs(x, q); ex = Cc.subs(x, q + 1) - Cc.subs(x, q)
        pr, un = P(*PROD)
        prob = f"ថ្លៃផលិត $x$ {un} គឺ $C(x)={L(Cc)}$ ។ គណនា $C'({q})$" + f" រួចប្រៀបធៀបជាមួយថ្លៃពិតនៃការផលិតឯកតាទី ${q+1}$ គឺ $C({q+1})-C({q})$ ។"
        sol = "ដេរីវេ ៖\n" + DM(f"C'(x)={L(sp.diff(Cc,x))}") + f"នៅ $x={q}$ ៖ $C'({q})={L(mc)}$ ។\nថ្លៃពិត ៖\n" + DM(f"C({q+1})-C({q})={L(Cc.subs(x,q+1))}-{L(Cc.subs(x,q))}={L(ex)}") + f"តម្លៃទាំងពីរខិតជិតគ្នា ព្រោះ $C'(x)$ ជាតម្លៃប្រហែលនៃថ្លៃឯកតាបន្ថែម ។\n{fin()}\n" + BOX(f"C'({q})={L(mc)},\\quad C({q+1})-C({q})={L(ex)}")
        F = st(Cc); ck = [check(f"diff({F},x).subs(x,{q})", st(mc)), check(f"({F}).subs(x,{q+1})-({F}).subs(x,{q})", st(ex))]
        ans = f"C'({q})={L(mc)}"; key = (mode, Cc, q)
    elif mode == "avg":
        a = rng.randint(1, 4); b = rng.randint(-6, 6); c = rng.randint(1, 9); x1 = rng.randint(0, 4); x2 = x1 + P(1, 2, 3, 4)
        Ff = a * x**3 + b * x + c
        av = (Ff.subs(x, x2) - Ff.subs(x, x1)) / (x2 - x1); inst = sp.diff(Ff, x).subs(x, x1)
        prob = f"គេឲ្យ $f(x)={L(Ff)}$ ។ គណនាអត្រាបម្រែបម្រួលមធ្យមនៃ $f$ លើ $[{x1};{x2}]$ និងអត្រាបម្រែបម្រួលខណៈនៅ $x={x1}$ ។"
        sol = "អត្រាមធ្យម ៖\n" + DM(f"\\frac{{f({x2})-f({x1})}}{{{x2}-{x1}}}=\\frac{{{L(Ff.subs(x,x2))}-({L(Ff.subs(x,x1))})}}{{{x2-x1}}}={L(av)}") + "អត្រាខណៈគឺដេរីវេ ៖\n" + DM(f"f'(x)={L(sp.diff(Ff,x))},\\quad f'({x1})={L(inst)}") + f"{fin()}\n" + BOX(f"{L(av)}\\ \\text{{ }}\\ ;\\ {L(inst)}".replace("\\ \\text{ }\\ ;\\ ", ";\\ "))
        F = st(Ff); ck = [check(f"(({F}).subs(x,{x2})-({F}).subs(x,{x1}))/{x2-x1}", st(av)), check(f"diff({F},x).subs(x,{x1})", st(inst))]
        ans = f"{L(av)};\\ {L(inst)}"; key = (mode, Ff, x1, x2)
    elif mode == "conc":
        b = rng.randint(1, 8); a = rng.randint(2, 40)
        Ff = a * x / (x**2 + b**2); tt = rng.randint(1, 10)
        Fp = sp.together(sp.diff(Ff, x)); r = Fp.subs(x, tt)
        prob = f"កំហាប់ថ្នាំក្នុងឈាមក្រោយ $t$ ម៉ោង គឺ $C(t)={L(Ff,'t')}$ ។ រកអត្រាបម្រែបម្រួលនៃកំហាប់នៅ $t={tt}$ ។ បកស្រាយសញ្ញានៃលទ្ធផល ។"
        word = "កំពុងកើន" if r > 0 else ("ឈប់ប្រែប្រួលមួយភ្លែត" if r == 0 else "កំពុងថយ")
        sol = f"តាមរូបមន្តដេរីវេនៃផលចែក ៖\n" + DM(f"C'(t)=\\frac{{{a}(t^2+{b*b})-{a}t\\cdot2t}}{{(t^2+{b*b})^2}}=\\frac{{{a}({b*b}-t^2)}}{{(t^2+{b*b})^2}}") + f"នៅ $t={tt}$ ៖ $C'({tt})={L(r)}$ ។\nកំហាប់{word}នៅខណៈនោះ ។\n{fin()}\n" + BOX(f"C'({tt})={L(r)}")
        ck = [dchk(Ff, a * (b * b - x**2) / (x**2 + b * b)**2), check(f"diff({st(Ff)},x).subs(x,{tt})", st(r))]
        ans = f"C'({tt})={L(r)}"; key = (mode, Ff, tt)
    elif mode == "geom":
        sh, Ff, nm = P(("ក្រឡាផ្ទៃរង្វង់", PI * x**2, "r"), ("មាឌស្វ៊ែ", Q(4, 3) * PI * x**3, "r"), ("ក្រឡាផ្ទៃស្វ៊ែ", 4 * PI * x**2, "r"), ("មាឌគូប", x**3, "a"), ("ក្រឡាផ្ទៃការ៉េ", x**2, "a"))
        r0 = rng.randint(2, 40)
        d = sp.diff(Ff, x); v = d.subs(x, r0)
        prob = f"គណនាអត្រាបម្រែបម្រួលនៃ{sh}ធៀបនឹង ${nm}$ នៅពេល ${nm}={r0}$ ។"
        sol = f"{sh}កំណត់ដោយ ៖\n" + DM(f"f({nm})={L(Ff,nm)}") + "ដេរីវេធៀបនឹងអថេរ ៖\n" + DM(f"f'({nm})={L(d,nm)}") + f"ត្រង់ ${nm}={r0}$ ៖\n{fin()}\n" + BOX(f"f'({r0})={L(v)}")
        ck = [check(f"diff({st(Ff)},x).subs(x,{r0})", st(v))]; ans = L(v); key = (mode, Ff, r0)
    else:
        a = rng.randint(2, 30); w = P(1, 2, Q(1, 2)); tt = PI * rng.randint(1, 5) / (6 * w) 
        Ff = a * sp.sin(w * x)**2
        d = sp.diff(Ff, x); v = sp.simplify(d.subs(x, tt))
        prob = f"កម្រិតទឹកក្នុងព្រែកមួយ (គិតជាដេស៊ីម៉ែត្រពីកម្រិតទាបបំផុត) ប្រែប្រួលតាម $h(t)={L(Ff,'t')}$ ។ រកល្បឿនឡើងចុះនៃទឹកនៅ $t={L(tt)}$ ។"
        sol = "តាមរូបមន្ត $(u^2)'=2uu'$ ៖\n" + DM(f"h'(t)={L(d,'t')}") + f"នៅ $t={L(tt)}$ ៖\n{fin()}\n" + BOX(f"h'\\left({L(tt)}\\right)={L(v)}")
        ck = [dchk(Ff, d), check(f"diff({st(Ff)},x).subs(x,{st(tt)})", st(v))]; ans = L(v); key = (mode, Ff, tt)
    add("rate_of_change", P("easy", "medium"), key, prob, sol, ans, ck)

# =============================== RELATED RATES ===============================
def g_ladder():
    a, b, h = P((3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10), (9, 12, 15), (20, 21, 29))
    r = sp.sympify(P(Q(1, 2), 1, 2, Q(1, 4), Q(3, 10), Q(1, 5)))
    if rng.random() < .5: a, b = b, a
    # ladder h; foot a from wall, top b. foot moves away at r. dy/dt = -a r / b
    rate = -a * r / b
    thing = P("ជណ្ដើរឫស្សី", "ជណ្ដើរឈើ", "ជណ្ដើរដែក")
    pn = P(*PEOPLE)
    prob = P(f"{thing}ប្រវែង ${h}$ ម៉ែត្រ ផ្អែកនឹងជញ្ជាំងផ្ទះ{pn} ។ ជើងជណ្ដើររអិលចេញពីជញ្ជាំងក្នុងល្បឿន ${L(r)}$ ម៉ែត្រក្នុងមួយវិនាទី ។ នៅពេលជើងជណ្ដើរនៅចម្ងាយ ${a}$ ម៉ែត្រពីជញ្ជាំង តើចុងខាងលើធ្លាក់ចុះក្នុងល្បឿនប៉ុន្មាន?",
             f"{pn}ដាក់{thing}ប្រវែង ${h}$ ម៉ែត្រ ផ្អែកនឹងជញ្ជាំងបញ្ឈរ ។ បើជើងជណ្ដើររអិលចេញក្នុងល្បឿនថេរ ${L(r)}$ ម៉ែត្រក្នុងមួយវិនាទី រកល្បឿនចុងលើនៅពេលចុងលើនៅកម្ពស់ ${b}$ ម៉ែត្រពីដី ។")
    sol = (f"តាង $x(t)$ ជាចម្ងាយពីជើងជណ្ដើរទៅជញ្ជាំង និង $y(t)$ ជាកម្ពស់ចុងលើ ។ តាមទ្រឹស្តីបទពីតាករ ៖\n" + DM(f"x^2+y^2={h*h}") + "ធ្វើដេរីវេលើអង្គទាំងពីរធៀបនឹង $t$ ៖\n" + DM("2x\\frac{dx}{dt}+2y\\frac{dy}{dt}=0\\Rightarrow\\frac{dy}{dt}=-\\frac{x}{y}\\cdot\\frac{dx}{dt}")
           + f"ពេល $x={a}$ គេបាន $y=\\sqrt{{{h*h}-{a*a}}}={b}$ ហើយ $\\frac{{dx}}{{dt}}={L(r)}$ ។\n" + DM(f"\\frac{{dy}}{{dt}}=-\\frac{{{a}}}{{{b}}}\\cdot{L(r)}={L(rate)}") + f"{fin()} ចុងលើធ្លាក់ចុះក្នុងល្បឿន ៖\n" + BOX(f"\\left|\\frac{{dy}}{{dt}}\\right|={L(-rate)}") + "ម៉ែត្រក្នុងមួយវិនាទី ។")
    # check: y(x) = sqrt(h^2 - x^2), dy/dx at a times r
    ck = [check(f"diff(sqrt({h*h}-x**2),x).subs(x,{a})*{st(r)}", st(rate), "dy/dt"), check(f"sqrt({h*h}-{a*a})", str(b))]
    add("related_rates_ladder", "medium", (a, b, h, r), prob, sol, f"\\frac{{dy}}{{dt}}={L(rate)}", ck, [fig(fig_tri("x", "y", str(h)), "ជណ្ដើរផ្អែកជញ្ជាំង ជាត្រីកោណកែង")])

def g_circle_sphere():
    mode = P("ripple", "balloon", "balloon2", "oil", "cube", "snow")
    r0 = rng.randint(2, 30); dr = P(Q(1, 2), 1, 2, 3, Q(1, 4), 4, 5)
    if mode == "ripple":
        thing = P("គេបោះដុំថ្មចូលបឹងបឹងកន្សែង", "ដំណក់ទឹកធ្លាក់ក្នុងស្រះ", "ត្រីលោតលើផ្ទៃទឹកទន្លេសាប")
        thing = P("គេបោះដុំថ្មចូលបឹង", "ដំណក់ទឹកធ្លាក់ក្នុងស្រះ", "ត្រីលោតលើផ្ទៃទន្លេសាប")
        V = PI * x**2; ans_v = sp.diff(V, x).subs(x, r0) * dr
        prob = f"{thing} បង្កើតរលករាងរង្វង់ ដែលកាំកើនក្នុងល្បឿន ${L(dr)}$ ម៉ែត្រក្នុងមួយវិនាទី ។ គណនាល្បឿនកើននៃក្រឡាផ្ទៃរង្វង់ នៅពេលកាំស្មើ ${r0}$ ម៉ែត្រ ។"
        sol = "ក្រឡាផ្ទៃ $S=\\pi r^2$ ។ ធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM("\\frac{dS}{dt}=2\\pi r\\frac{dr}{dt}") + f"ជំនួស $r={r0}$ និង $\\frac{{dr}}{{dt}}={L(dr)}$ ៖\n{fin()}\n" + BOX(f"\\frac{{dS}}{{dt}}={L(ans_v)}") + "ម៉ែត្រការ៉េក្នុងមួយវិនាទី ។"
    elif mode == "oil":
        V = PI * x**2; dS = rng.randint(2, 20) * 2 * r0 * PI; ans_v = dS / (2 * PI * r0)
        prob = f"ប្រេងកំពប់លើទឹកជាផ្ទាំងរង្វង់ ដែលក្រឡាផ្ទៃកើន ${L(dS)}$ ម៉ែត្រការ៉េក្នុងមួយនាទី ។ រកល្បឿនកើននៃកាំពេល $r={r0}$ ម៉ែត្រ ។"
        sol = "ពី $S=\\pi r^2$ ធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM("\\frac{dS}{dt}=2\\pi r\\frac{dr}{dt}\\Rightarrow\\frac{dr}{dt}=\\frac{1}{2\\pi r}\\cdot\\frac{dS}{dt}") + f"ជំនួសតម្លៃ ៖\n" + DM(f"\\frac{{dr}}{{dt}}=\\frac{{{L(dS)}}}{{2\\pi\\cdot{r0}}}") + f"{fin()}\n" + BOX(f"\\frac{{dr}}{{dt}}={L(ans_v)}") + "ម៉ែត្រក្នុងមួយនាទី ។"
    elif mode == "balloon":
        V = Q(4, 3) * PI * x**3; ans_v = sp.diff(V, x).subs(x, r0) * dr
        prob = f"ប៉េងប៉ោងរាងស្វ៊ែមួយត្រូវបានបំប៉ោង ដោយកាំកើន ${L(dr)}$ សង់ទីម៉ែត្រក្នុងមួយវិនាទី ។ រកល្បឿនកើននៃមាឌនៅពេល $r={r0}$ សង់ទីម៉ែត្រ ។"
        sol = "មាឌស្វ៊ែ $V=\\frac{4}{3}\\pi r^3$ ។ ធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM("\\frac{dV}{dt}=4\\pi r^2\\frac{dr}{dt}") + f"ជំនួសតម្លៃ ៖\n" + DM(f"\\frac{{dV}}{{dt}}=4\\pi\\cdot{r0}^2\\cdot{L(dr)}") + f"{fin()}\n" + BOX(f"\\frac{{dV}}{{dt}}={L(ans_v)}") + "សង់ទីម៉ែត្រគូបក្នុងមួយវិនាទី ។"
    elif mode == "balloon2":
        V = Q(4, 3) * PI * x**3; dV = 4 * PI * r0**2 * dr; ans_v = dr
        prob = f"ខ្យល់ត្រូវបានបូមចូលប៉េងប៉ោងរាងស្វ៊ែ ក្នុងល្បឿន ${L(dV)}$ សង់ទីម៉ែត្រគូបក្នុងមួយវិនាទី ។ រកល្បឿនកើននៃកាំនៅពេលកាំស្មើ ${r0}$ សង់ទីម៉ែត្រ ។"
        sol = "ពី $V=\\frac{4}{3}\\pi r^3$ គេបាន ៖\n" + DM("\\frac{dV}{dt}=4\\pi r^2\\frac{dr}{dt}\\Rightarrow\\frac{dr}{dt}=\\frac{1}{4\\pi r^2}\\cdot\\frac{dV}{dt}") + f"ដោយ $r={r0}$ ៖\n" + DM(f"\\frac{{dr}}{{dt}}=\\frac{{{L(dV)}}}{{4\\pi\\cdot{r0*r0}}}") + f"{fin()}\n" + BOX(f"\\frac{{dr}}{{dt}}={L(dr)}") + "សង់ទីម៉ែត្រក្នុងមួយវិនាទី ។"
    elif mode == "cube":
        V = x**3; ans_v = sp.diff(V, x).subs(x, r0) * dr
        prob = f"គូបទឹកកកមួយមានជ្រុង $a$ ដែលកំពុងថយក្នុងល្បឿន ${L(dr)}$ សង់ទីម៉ែត្រក្នុងមួយនាទី ។ រកល្បឿនថយនៃមាឌពេល $a={r0}$ សង់ទីម៉ែត្រ ។"
        sol = "មាឌ $V=a^3$ ។ ធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM("\\frac{dV}{dt}=3a^2\\frac{da}{dt}") + f"ដោយ $\\frac{{da}}{{dt}}=-{L(dr)}$ និង $a={r0}$ ៖\n" + DM(f"\\frac{{dV}}{{dt}}=3\\cdot{r0*r0}\\cdot(-{L(dr)})={L(-ans_v)}") + f"{fin()} មាឌថយក្នុងល្បឿន ៖\n" + BOX(L(ans_v)) + "សង់ទីម៉ែត្រគូបក្នុងមួយនាទី ។"
    else:
        V = 4 * PI * x**2; ans_v = sp.diff(V, x).subs(x, r0) * dr
        prob = f"ស្វ៊ែទឹកកកមួយរលាយ ដោយកាំថយ ${L(dr)}$ មីលីម៉ែត្រក្នុងមួយនាទី ។ រកល្បឿនថយនៃក្រឡាផ្ទៃពេលកាំស្មើ ${r0}$ មីលីម៉ែត្រ ។"
        sol = "ក្រឡាផ្ទៃស្វ៊ែ $S=4\\pi r^2$ ។ ធ្វើដេរីវេ ៖\n" + DM("\\frac{dS}{dt}=8\\pi r\\frac{dr}{dt}") + f"ដោយកាំថយ $\\frac{{dr}}{{dt}}=-{L(dr)}$ ។ ជំនួស ៖\n" + DM(f"\\frac{{dS}}{{dt}}=8\\pi\\cdot{r0}\\cdot(-{L(dr)})={L(-ans_v)}") + f"{fin()} ក្រឡាផ្ទៃថយក្នុងល្បឿន ៖\n" + BOX(L(ans_v)) + "មីលីម៉ែត្រការ៉េក្នុងមួយនាទី ។"
    if mode in ("oil", "balloon2"):
        dX = dS if mode == "oil" else dV
        ck = [check(f"{st(dX)}/diff({st(V)},x).subs(x,{r0})", st(ans_v), "អត្រាកាំ")]
    else:
        ck = [check(f"diff({st(V)},x).subs(x,{r0})*{st(dr)}", st(ans_v), "អត្រា")]
    add("related_rates_geometry", P("easy", "medium"), (mode, r0, dr), prob, sol, L(ans_v), ck)

def g_cone_tank():
    Rr, H = P((1, 2), (1, 3), (2, 3), (3, 4), (2, 5), (3, 5), (1, 1), (3, 2))
    k = rng.randint(1, 4); Rr *= k; H *= k
    h0 = H * Q(rng.randint(1, 3), 4)
    q = Q(Rr, H)
    dV = rng.randint(1, 9) * PI * P(1, Q(1, 2), 2) * q**2 * h0**2
    V = PI / 3 * q**2 * x**3
    dh = dV / (PI * q**2 * h0**2)
    thing = P("ធុងរាងកោណបញ្ច្រាស", "ជីងចាក់ទឹករាងកោណ", "អាងទឹករាងកោណបញ្ច្រាស")
    drain = rng.random() < .35
    verb = "ហូរចេញពី" if drain else "ចាក់ចូល"
    prob = f"ទឹក{verb}{thing}ដែលមានកាំមាត់ ${Rr}$ ម៉ែត្រ និងកម្ពស់ ${H}$ ម៉ែត្រ ក្នុងល្បឿន ${L(dV)}$ ម៉ែត្រគូបក្នុងមួយនាទី ។ រកល្បឿន{'ថយ' if drain else 'ឡើង'}នៃកម្ពស់ទឹកនៅពេលទឹកជម្រៅ ${L(h0)}$ ម៉ែត្រ ។"
    sol = (f"តាង $h$ ជាជម្រៅទឹក និង $r$ ជាកាំផ្ទៃទឹក ។ ត្រីកោណដូចគ្នាឲ្យ $\\frac{{r}}{{h}}=\\frac{{{Rr}}}{{{H}}}$ នាំឲ្យ $r={L(q)}h$ ។\nមាឌទឹក ៖\n" + DM(f"V=\\frac{{1}}{{3}}\\pi r^2h={L(V,'h')}")
           + "ធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM(f"\\frac{{dV}}{{dt}}={L(sp.diff(V,x),'h')}\\cdot\\frac{{dh}}{{dt}}") + f"ដោយ $h={L(h0)}$ ៖\n" + DM(f"{'-' if drain else ''}{L(dV)}={L(sp.diff(V,x).subs(x,h0))}\\cdot\\frac{{dh}}{{dt}}") + f"{fin()} ទឹក{'ថយ' if drain else 'ឡើង'}ក្នុងល្បឿន ៖\n" + BOX(f"{L(dh)}") + "ម៉ែត្រក្នុងមួយនាទី ។")
    add("related_rates_tank", P("medium", "hard", "bacii"), (Rr, H, h0, dV, drain), prob, sol, L(dh), [check(f"{st(dV)}/diff({st(V)},x).subs(x,{st(h0)})", st(dh), "dh/dt")], [fig(fig_cone(str(Rr), str(H)), "កោណបញ្ច្រាសនៃធុងទឹក")])

def g_cyl_tank():
    r = rng.randint(1, 8); dV = PI * r * r * P(Q(1, 2), 1, 2, 3, Q(1, 4)); dh = dV / (PI * r * r)
    V = PI * r**2 * x
    prob = P(f"គេចាក់ទឹកចូលធុងស៊ីឡាំងកាំបាត ${r}$ ម៉ែត្រ ក្នុងល្បឿន ${L(dV)}$ ម៉ែត្រគូបក្នុងមួយនាទី ។ រកល្បឿនឡើងនៃកម្ពស់ទឹក ។", f"ធុងទឹកស៊ីឡាំងនៅសាលាមួយមានកាំ ${r}$ ម៉ែត្រ ។ ទឹកចូល ${L(dV)}$ ម៉ែត្រគូបក្នុងមួយនាទី ។ តើផ្ទៃទឹកឡើងលឿនប៉ុន្មាន?")
    sol = f"មាឌទឹកពេលជម្រៅ $h$ គឺ $V=\\pi\\cdot{r}^2h={L(V,'h')}$ ។\nធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM(f"\\frac{{dV}}{{dt}}={L(PI*r*r)}\\frac{{dh}}{{dt}}\\Rightarrow\\frac{{dh}}{{dt}}=\\frac{{{L(dV)}}}{{{L(PI*r*r)}}}") + f"{fin()}\n" + BOX(f"\\frac{{dh}}{{dt}}={L(dh)}") + "ម៉ែត្រក្នុងមួយនាទី ។"
    add("related_rates_tank", "easy", (r, dV), prob, sol, L(dh), [check(f"{st(dV)}/diff({st(V)},x)", st(dh))])

def g_two_cars():
    a, b, h = P((3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (7, 24, 25), (9, 12, 15), (12, 16, 20))
    k = P(1, 2, 3, 5, 10); a, b, h = a * k, b * k, h * k
    v1, v2 = rng.randint(2, 12) * 5, rng.randint(2, 12) * 5
    rate = Q(a * v1 + b * v2, h)
    m1, m2 = rng.sample(["ឡានក្រុង", "ម៉ូតូ", "រថយន្ត", "តុកតុក"], 2); c = P("ភ្នំពេញ", "ស្ទឹងត្រែង", "កំពង់ស្ពឺ", "សៀមរាប")
    prob = f"{m1}ចេញពីផ្លូវបំបែកនៅ{c}ទៅទិសខាងកើតក្នុងល្បឿន ${v1}$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ហើយ{m2}ទៅទិសខាងជើងក្នុងល្បឿន ${v2}$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ។ នៅពេល{m1}នៅចម្ងាយ ${a}$ គីឡូម៉ែត្រ និង{m2}នៅចម្ងាយ ${b}$ គីឡូម៉ែត្រពីផ្លូវបំបែក តើចម្ងាយរវាងគេកើនក្នុងល្បឿនប៉ុន្មាន?"
    sol = (f"តាង $x$ និង $y$ ជាចម្ងាយពីផ្លូវបំបែក ហើយ $z$ ជាចម្ងាយរវាងយានទាំងពីរ ។ ផ្លូវកែងគ្នា ដូច្នេះ $z^2=x^2+y^2$ ។\nធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM("2z\\frac{dz}{dt}=2x\\frac{dx}{dt}+2y\\frac{dy}{dt}") + f"ពេល $x={a}$, $y={b}$ គេបាន $z=\\sqrt{{{a*a}+{b*b}}}={h}$ ។\n" + DM(f"\\frac{{dz}}{{dt}}=\\frac{{{a}\\cdot{v1}+{b}\\cdot{v2}}}{{{h}}}={L(rate)}") + f"{fin()}\n" + BOX(f"\\frac{{dz}}{{dt}}={L(rate)}") + "គីឡូម៉ែត្រក្នុងមួយម៉ោង ។")
    add("related_rates_distance", "medium", (a, b, v1, v2), prob, sol, L(rate), [check(f"diff(sqrt(x**2+{b*b}),x).subs(x,{a})*{v1}+diff(sqrt({a*a}+x**2),x).subs(x,{b})*{v2}", st(rate), "dz/dt"), check(f"sqrt({a*a}+{b*b})", str(h))], [fig(fig_tri("x", "y", "z"), "ផ្លូវកែងគ្នា")])

def g_shadow():
    H = sp.Integer(P(4, 5, 6, 8, 3)); hp = sp.sympify(P(Q(3, 2), Q(8, 5), 2, Q(9, 5))); v = sp.sympify(P(1, Q(3, 2), 2, Q(5, 4)))
    if hp >= H: return
    q = hp / (H - hp); rate = q * v; tip = v + rate
    pn = P(*PEOPLE)
    mode = P("len", "tip")
    prob = f"{pn}មានកម្ពស់ ${L(hp)}$ ម៉ែត្រ ដើរចេញពីបង្គោលភ្លើងបំភ្លឺផ្លូវកម្ពស់ ${H}$ ម៉ែត្រ ក្នុងល្បឿន ${L(v)}$ ម៉ែត្រក្នុងមួយវិនាទី ។ " + ("រកល្បឿនលូតលាស់នៃប្រវែងស្រមោល ។" if mode == "len" else "រកល្បឿននៃចុងស្រមោល ។")
    Rres = rate if mode == "len" else tip
    sol = (f"តាង $x$ ជាចម្ងាយពីបង្គោលទៅ{pn} និង $s$ ជាប្រវែងស្រមោល ។ ត្រីកោណដូចគ្នាឲ្យ ៖\n" + DM(f"\\frac{{s}}{{{L(hp)}}}=\\frac{{x+s}}{{{H}}}\\Rightarrow s={L(q*x)}") + "ធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM(f"\\frac{{ds}}{{dt}}={L(q)}\\frac{{dx}}{{dt}}={L(q)}\\cdot{L(v)}={L(rate)}")
           + ("" if mode == "len" else f"ចុងស្រមោលនៅចម្ងាយ $x+s$ ពីបង្គោល ដូច្នេះល្បឿនគឺ $\\frac{{dx}}{{dt}}+\\frac{{ds}}{{dt}}={L(v)}+{L(rate)}$ ។\n") + f"{fin()}\n" + BOX(L(Rres)) + "ម៉ែត្រក្នុងមួយវិនាទី ។")
    ck = [check(f"diff({st(q)}*x,x)*{st(v)}", st(rate), "ds/dt")]
    if mode == "tip": ck.append(check(f"diff(x+{st(q)}*x,x)*{st(v)}", st(tip), "ចុងស្រមោល"))
    add("related_rates_shadow", "medium", (H, hp, v, mode), prob, sol, L(Rres), ck)

def g_kite():
    a, b, h = P((3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (9, 12, 15), (7, 24, 25))
    k = P(2, 5, 10, 1); a, b, h = a * k, b * k, h * k
    v = rng.randint(1, 8)
    mode = P("kite", "boat")
    if mode == "kite":
        rate = Q(a * v, h)
        prob = f"ខ្លែងមួយហោះនៅកម្ពស់ថេរ ${b}$ ម៉ែត្រ ហើយខ្យល់បក់វាទៅផ្តេកក្នុងល្បឿន ${v}$ ម៉ែត្រក្នុងមួយវិនាទី ។ នៅពេលខ្លែងនៅចម្ងាយផ្តេក ${a}$ ម៉ែត្រពីអ្នកកាន់ខ្សែ តើត្រូវបន្ធូរខ្សែក្នុងល្បឿនប៉ុន្មាន?"
        sol = (f"តាង $x$ ជាចម្ងាយផ្តេក និង $l$ ជាប្រវែងខ្សែ ។ គេបាន $l^2=x^2+{b*b}$ ។\nធ្វើដេរីវេធៀបនឹង $t$ ៖\n" + DM("2l\\frac{dl}{dt}=2x\\frac{dx}{dt}\\Rightarrow\\frac{dl}{dt}=\\frac{x}{l}\\cdot\\frac{dx}{dt}") + f"ពេល $x={a}$ ៖ $l=\\sqrt{{{a*a}+{b*b}}}={h}$ ។\n" + DM(f"\\frac{{dl}}{{dt}}=\\frac{{{a}}}{{{h}}}\\cdot{v}={L(rate)}") + f"{fin()}\n" + BOX(f"\\frac{{dl}}{{dt}}={L(rate)}") + "ម៉ែត្រក្នុងមួយវិនាទី ។")
        ck = [check(f"diff(sqrt(x**2+{b*b}),x).subs(x,{a})*{v}", st(rate))]
    else:
        rate = Q(h * v, a)
        prob = f"គេទាញទូកមួយចូលផែ ដោយខ្សែពួរពីចំណុចលើផែដែលខ្ពស់ជាងច្រមុះទូក ${b}$ ម៉ែត្រ ។ ខ្សែត្រូវបានទាញចូលក្នុងល្បឿន ${v}$ ម៉ែត្រក្នុងមួយនាទី ។ រកល្បឿនទូកពេលវានៅចម្ងាយ ${a}$ ម៉ែត្រពីផែ ។"
        sol = (f"តាង $x$ ជាចម្ងាយទូកពីផែ និង $l$ ជាប្រវែងខ្សែ ។ $l^2=x^2+{b*b}$ ។\nធ្វើដេរីវេ ៖\n" + DM("l\\frac{dl}{dt}=x\\frac{dx}{dt}\\Rightarrow\\frac{dx}{dt}=\\frac{l}{x}\\cdot\\frac{dl}{dt}") + f"ពេល $x={a}$ ៖ $l={h}$ និង $\\frac{{dl}}{{dt}}=-{v}$ ។\n" + DM(f"\\frac{{dx}}{{dt}}=\\frac{{{h}}}{{{a}}}\\cdot(-{v})={L(-rate)}") + f"{fin()} ទូកខិតជិតផែក្នុងល្បឿន ៖\n" + BOX(L(rate)) + "ម៉ែត្រក្នុងមួយនាទី ។")
        ck = [check(f"{v}/diff(sqrt(x**2+{b*b}),x).subs(x,{a})", st(rate))]
    add("related_rates_distance", "medium", (mode, a, b, v), prob, sol, L(rate), ck, [fig(fig_tri("x", str(b), "l"), "ត្រីកោណកែង")])

def g_curve_point():
    mode = P("parab", "hyper", "sqrt", "rect")
    p = rng.randint(1, 6); v = rng.randint(1, 7)
    if mode == "rect":
        w, l = rng.randint(2, 20), rng.randint(2, 20); dw, dl = rng.randint(1, 5), rng.randint(1, 5)
        res = dw * l + w * dl
        prob = f"ចតុកោណកែងមួយមានទទឹង $x$ និងបណ្តោយ $y$ ដែល $x$ កើន ${dw}$ សង់ទីម៉ែត្រក្នុងមួយវិនាទី និង $y$ កើន ${dl}$ សង់ទីម៉ែត្រក្នុងមួយវិនាទី ។ រកល្បឿនកើននៃក្រឡាផ្ទៃពេល $x={w}$ និង $y={l}$ ។"
        sol = f"$S=xy$ ។ តាមដេរីវេនៃផលគុណ ៖\n" + DM("\\frac{dS}{dt}=\\frac{dx}{dt}y+x\\frac{dy}{dt}") + DM(f"\\frac{{dS}}{{dt}}={dw}\\cdot{l}+{w}\\cdot{dl}={res}") + f"{fin()}\n" + BOX(f"\\frac{{dS}}{{dt}}={res}") + "សង់ទីម៉ែត្រការ៉េក្នុងមួយវិនាទី ។"
        ck = [check(f"diff(x*{l},x)*{dw}+diff({w}*x,x)*{dl}", str(res))]; key = (w, l, dw, dl)
    else:
        if mode == "parab": f = x**2 + rng.randint(-4, 4) * x
        elif mode == "hyper": f = Q(rng.randint(2, 24)) / x
        else: f = sp.sqrt(x + rng.randint(0, 8))
        if mode == "sqrt":
            b = f.subs(x, 0)**2; p = rng.randint(2, 7)**2 - b
            if p <= 0: return
        d = sp.diff(f, x); res = d.subs(x, p) * v
        prob = f"ចំណុច $M$ រំកិលលើខ្សែកោង $y={L(f)}$ ដោយអាប់ស៊ីសកើន ${v}$ ឯកតាក្នុងមួយវិនាទី ។ រកល្បឿនបម្រែបម្រួលនៃអរដោនេ នៅពេល $x={p}$ ។"
        sol = "ធ្វើដេរីវេ $y$ ធៀបនឹង $t$ ដោយរូបមន្តអនុគមន៍បណ្ដាក់ ៖\n" + DM(f"\\frac{{dy}}{{dt}}=y'(x)\\cdot\\frac{{dx}}{{dt}}=\\left({L(d)}\\right)\\frac{{dx}}{{dt}}") + f"ត្រង់ $x={p}$ ៖ $y'({p})={L(d.subs(x,p))}$ ។\n{fin()}\n" + BOX(f"\\frac{{dy}}{{dt}}={L(res)}") + "ឯកតាក្នុងមួយវិនាទី ។"
        ck = [check(f"diff({st(f)},x).subs(x,{p})*{v}", st(res))]; key = (f, p, v)
    add("related_rates_curve", "easy", key, prob, sol, L(res), ck)

# =============================== LIMITS ===============================
def dec(v, n=4):
    s_ = f"{float(v):.{n}f}".rstrip("0").rstrip(".")
    return s_

ANG = [PI / 6, PI / 4, PI / 3]
def lim_fn():
    k = rng.randint(0, 9)
    if k == 0:
        n = rng.randint(2, 9); a = P(1, 2, 3, -1, -2); return x**n, sp.Integer(a), f"(x^n)'=nx^{{n-1}}"
    if k == 1:
        r = rng.randint(1, 9); b = rng.randint(0, 9); a = r * r - b; return sp.sqrt(x + b), sp.Integer(a), "(\\sqrt{u})'=\\frac{u'}{2\\sqrt{u}}"
    if k == 2: return sp.sin(x), P(*ANG), "(\\sin x)'=\\cos x"
    if k == 3: return sp.cos(x), P(*ANG), "(\\cos x)'=-\\sin x"
    if k == 4: return sp.tan(x), P(*ANG, 0), "(\\tan x)'=1+\\tan^2x"
    if k == 5:
        c = P(1, 2, 3, -1, 4); return sp.exp(c * x), sp.Integer(P(0, 1, 2, -1)), "(e^{u})'=u'e^{u}"
    if k == 6: return sp.log(x), sp.Integer(rng.randint(1, 12)), "(\\ln x)'=\\frac{1}{x}"
    if k == 7:
        b = rng.randint(0, 6); return 1 / (x + b), sp.Integer(rng.randint(1, 7)), "\\left(\\frac{1}{u}\\right)'=-\\frac{u'}{u^2}"
    if k == 8:
        a = P(8, 27, 64, 1, 125); return x**Q(1, 3), sp.Integer(a), "(x^r)'=rx^{r-1}"
    c = rng.randint(2, 6); return sp.log(c * x + 1), sp.Integer(rng.randint(0, 4)), "(\\ln u)'=\\frac{u'}{u}"

def g_lim_deriv():
    f, a, rule = lim_fn()
    fa = sp.simplify(f.subs(x, a)); d = sp.diff(f, x)
    val = sp.simplify(sp.simplify(d.subs(x, a)))
    form = P("xa", "xa", "h")
    h = sv("h")
    if form == "xa":
        expr = f"\\frac{{{L(f)}-{'(' + L(fa) + ')' if fa < 0 else L(fa)}}}{{{L(x-a)}}}"
        lim = f"\\lim_{{x\\to {L(a)}}}" + expr
        lhs = f"limit(({st(f)}-({st(fa)}))/(x-({st(a)})),x,{st(a)})"
        defn = f"\\lim_{{x\\to {L(a)}}}\\frac{{f(x)-f({L(a)})}}{{x-{L(a)}}}=f'({L(a)})".replace("--", "+")
    else:
        fh = f.subs(x, a + h)
        expr = f"\\frac{{{L(fh)}-{'(' + L(fa) + ')' if fa < 0 else L(fa)}}}{{h}}"
        lim = "\\lim_{h\\to 0}" + expr
        fx = f.subs(x, a + x)
        lhs = f"limit(({st(fx)}-({st(fa)}))/x,x,0)"
        defn = f"\\lim_{{h\\to 0}}\\frac{{f({L(a)}+h)-f({L(a)})}}{{h}}=f'({L(a)})"
    prob = P(f"គណនាលីមីត ${lim}$ ដោយសម្គាល់ឃើញថាវាជាដេរីវេនៃអនុគមន៍មួយ ។", f"ដោយប្រើនិយមន័យដេរីវេ រកលីមីតខាងក្រោម ៖ $${lim}$$", f"គណនាលីមីតខាងក្រោម ៖ ${lim}$ ។", f"បង្ហាញថាលីមីត ${lim}$ ជាតម្លៃដេរីវេត្រង់ចំណុចមួយ រួចគណនាតម្លៃនោះ ។")
    sol = (f"តាង $f(x)={L(f)}$ ។ គេមាន $f({L(a)})={L(fa)}$ ។\nតាមនិយមន័យដេរីវេ ៖\n" + DM(defn) + f"តាមរូបមន្ត ${rule}$ គេបាន ៖\n" + DM(f"f'(x)={L(d)}") + f"ដូច្នេះ $f'({L(a)})={L(val)}$ ។\n{fin()}\n" + BOX(f"{lim}={L(val)}"))
    add("limit_as_derivative", P("easy", "medium"), (f, a, form), prob, sol, L(val), [check(lhs, st(val), "លីមីត"), dchk(f, d)])

def g_lim_given():
    a = rng.randint(-3, 6); p = rng.randint(-5, 9); q = P(-4, -3, -2, 2, 3, 4, 5, 7); k, m_ = rng.randint(1, 5), rng.randint(1, 5)
    mode = P("sym", "one", "prod", "sq")
    g = p + q * (x - a) + (x - a)**2   # a model function with g(a)=p, g'(a)=q
    h = sv("h")
    if mode == "sym":
        val = (k + m_) * q
        lim = f"\\lim_{{h\\to 0}}\\frac{{f({L(a+k*h)})-f({L(a-m_*h)})}}{{h}}"
        lhs = f"limit((({st(g.subs(x,a+k*x))})-({st(g.subs(x,a-m_*x))}))/x,x,0)"
        sol = (f"យើងបំបែកភាគយកដោយបន្ថែមនិងដក $f({a})$ ៖\n" + DM(f"\\frac{{f({L(a+k*h)})-f({a})}}{{h}}-\\frac{{f({L(a-m_*h)})-f({a})}}{{h}}") + f"តាមនិយមន័យដេរីវេ លីមីតតួទី១គឺ ${k}f'({a})$ ហើយលីមីតតួទី២គឺ ${-m_}f'({a})$ ។\nគេបាន ៖\n" + DM(f"L=({k}+{m_})f'({a})={k+m_}\\cdot({q})={val}"))
    elif mode == "one":
        val = k * q
        lim = f"\\lim_{{h\\to 0}}\\frac{{f({L(a+k*h)})-f({a})}}{{h}}"
        lhs = f"limit((({st(g.subs(x,a+k*x))})-({p}))/x,x,0)"
        sol = f"តាង $u={k}h$ ។ កាលណា $h\\to0$ នោះ $u\\to0$ ។\n" + DM(f"L=\\lim_{{u\\to 0}}{k}\\cdot\\frac{{f({a}+u)-f({a})}}{{u}}={k}f'({a})={val}")
    elif mode == "prod":
        if a == 0: return
        val = a * q - p if False else p - a * q
        lim = f"\\lim_{{x\\to {a}}}\\frac{{xf({a})-{L(a)}f(x)}}{{x-{L(a)}}}".replace("--", "+")
        lhs = f"limit((x*({p})-({a})*({st(g)}))/(x-({a})),x,{a})"
        sol = (f"យើងបន្ថែមនិងដក ${L(a)}f({a})$ ក្នុងភាគយក ៖\n" + DM(f"xf({a})-{L(a)}f(x)=(x-{L(a)})f({a})-{L(a)}\\left[f(x)-f({a})\\right]".replace("--", "+")) + "ចែកនឹងភាគបែង រួចយកលីមីត ៖\n" + DM(f"L=f({a})-{L(a)}f'({a})={p}-({a})({q})={val}"))
    else:
        val = 2 * p * q
        lim = f"\\lim_{{x\\to {a}}}\\frac{{f^2(x)-{p*p}}}{{x-{L(a)}}}".replace("--", "+")
        lhs = f"limit((({st(g)})**2-{p*p})/(x-({a})),x,{a})"
        if p == 0: return
        sol = (f"តាង $g(x)=f^2(x)$ នោះ $g({a})={p*p}$ ហើយ $g'(x)=2f(x)f'(x)$ ។\nលីមីតនេះជា $g'({a})$ ៖\n" + DM(f"L=2f({a})f'({a})=2({p})({q})={val}"))
    prob = f"គេឲ្យអនុគមន៍ $f$ មានដេរីវេត្រង់ $x={a}$ ដែល $f({a})={p}$ និង $f'({a})={q}$ ។ គណនា $L={lim}$ ។"
    sol += f"\n{fin()}\n" + BOX(f"L={val}")
    add("limit_as_derivative", P("medium", "hard"), (mode, a, p, q, k, m_), prob, sol, f"L={val}", [check(lhs, str(val), "ផ្ទៀងផ្ទាត់លើអនុគមន៍គំរូដែលមាន f(a) និង f'(a) ដូចសម្មតិកម្ម")])

def lh_pair():
    k = rng.randint(0, 15); a = rng.randint(1, 7); b = rng.randint(1, 7)
    if k == 0 and a != b: return sp.exp(a * x) - 1, b * x, 0
    if k == 1 and a != b: return sp.sin(a * x), sp.sin(b * x), 0
    if k == 2: return 1 - sp.cos(a * x), b * x**2, 0
    if k == 3: return sp.log(1 + a * x), sp.sin(b * x), 0
    if k == 4 and a != b: return sp.exp(a * x) - sp.exp(b * x), x, 0
    if k == 5: return sp.tan(a * x), b * x, 0
    if k == 6: return a * x - sp.sin(a * x), b * x**3, 0
    if k == 7: return sp.exp(a * x) - 1 - a * x, b * x**2, 0
    if k == 8:
        r = rng.randint(-4, 5); s1 = rng.randint(-5, 5); s2 = rng.randint(-5, 5)
        if s1 == r or s2 == r: return None
        return sp.expand((x - r) * (x - s1)), sp.expand((x - r) * (x - s2)), r
    if k == 9:
        n, m2 = rng.sample(range(2, 9), 2); return x**n - 1, x**m2 - 1, 1
    if k == 10:
        r = rng.randint(1, 8); c = rng.randint(0, 8); p = r * r - c; return sp.sqrt(x + c) - r, x - p, p
    if k == 11: return sp.log(x), x**b - 1, 1
    if k == 12 and a != b: return sp.cos(a * x) - sp.cos(b * x), x**2, 0
    if k == 13:
        r = rng.randint(1, 4); s1 = rng.randint(-3, 6)
        return sp.expand((x - r)**2 * (x - s1)), sp.expand((x - r)**2 * (x + a)), r
    if k == 14: return sp.exp(x - b) - 1, sp.log(x - b + 1), b
    if k == 15: return sp.sin(x - b), x**2 - b**2, b
    return None

def g_lhop():
    pr = lh_pair()
    if not pr: return
    N, D, a = pr
    a = sp.Integer(a)
    n, d = N, D; steps = []
    for i in range(4):
        n0, d0 = n.subs(x, a), d.subs(x, a)
        if d0 != 0: break
        if n0 != 0: return
        n, d = sp.diff(n, x), sp.diff(d, x); steps.append((n, d))
    else: return
    if d.subs(x, a) == 0: return
    val = sp.simplify(n.subs(x, a) / d.subs(x, a))
    if not steps or val.has(sp.zoo): return
    lim = f"\\lim_{{x\\to {L(a)}}}\\frac{{{L(N)}}}{{{L(D)}}}"
    prob = P(f"គណនាលីមីតខាងក្រោម ៖ ${lim}$ ។", f"ដោយប្រើវិធានឡូពីតាល់ គណនាលីមីត ៖ $${lim}$$", f"រកតម្លៃនៃលីមីតខាងក្រោម ៖ ${lim}$ ។", f"គេមានអនុគមន៍ $f(x)=\\frac{{{L(N)}}}{{{L(D)}}}$ ។ រកលីមីតនៃ $f(x)$ កាលណា $x$ ខិតជិត ${L(a)}$ ។")
    sol = [P(f"ជំនួស $x={L(a)}$ គេបានភាគយកនិងភាគបែងស្មើ $0$ ជារាងមិនកំណត់ $\\frac{{0}}{{0}}$ ។", f"កាលណា $x\\to{L(a)}$ ភាគយកនិងភាគបែងខិតជិតសូន្យ ។ នេះជារាងមិនកំណត់ $\\frac{{0}}{{0}}$ ។")]
    sol.append(P("តាមវិធានឡូពីតាល់ ធ្វើដេរីវេភាគយកនិងភាគបែងដោយឡែកពីគ្នា ៖", "ដោយអនុគមន៍ទាំងពីរមានដេរីវេ យើងអនុវត្តវិធានឡូពីតាល់ ៖"))
    for i, (nn, dd) in enumerate(steps):
        sol.append(DM(f"L=\\lim_{{x\\to {L(a)}}}\\frac{{{L(nn)}}}{{{L(dd)}}}"))
        if i < len(steps) - 1: sol.append("នៅតែជារាង $\\frac{0}{0}$ ដូច្នេះអនុវត្តវិធានឡូពីតាល់ម្តងទៀត ៖")
    sol.append(f"ឥឡូវភាគបែងខុសពីសូន្យ ។ ជំនួស $x={L(a)}$ ៖\n" + DM(f"L=\\frac{{{L(n.subs(x,a))}}}{{{L(d.subs(x,a))}}}={L(val)}"))
    sol.append(f"{fin()}\n" + BOX(f"{lim}={L(val)}"))
    add("lhopital_0_0", P("medium", "medium", "hard"), (N, D), prob, "\n".join(sol), L(val), [check(f"limit(({st(N)})/({st(D)}),x,{st(a)})", st(val), "លីមីត")])

def g_lhop_inf():
    k = rng.randint(0, 6); a = rng.randint(1, 6); b = rng.randint(1, 6); n = rng.randint(2, 4)
    if k == 0:
        N, D = sp.log(x)**1, x**n; lim = f"\\lim_{{x\\to+\\infty}}\\frac{{\\ln x}}{{x^{{{n}}}}}"; val = 0; lhs = f"limit(log(x)/x**{n},x,oo)"
        body = f"រាងមិនកំណត់ $\\frac{{\\infty}}{{\\infty}}$ ។ តាមវិធានឡូពីតាល់ ៖\n" + DM(f"L=\\lim_{{x\\to+\\infty}}\\frac{{\\frac{{1}}{{x}}}}{{{n}x^{{{n-1}}}}}=\\lim_{{x\\to+\\infty}}\\frac{{1}}{{{n}x^{{{n}}}}}=0")
        key = (k, n)
    elif k == 1:
        lim = f"\\lim_{{x\\to+\\infty}}\\frac{{x^{{{n}}}}}{{e^{{{a}x}}}}"; val = 0; lhs = f"limit(x**{n}*exp(-{a}*x),x,oo)"
        ch = [f"\\frac{{{sp.factorial(n)//sp.factorial(n-i)}x^{{{n-i}}}}}{{{a**i}e^{{{a}x}}}}" for i in range(1, n + 1)]
        body = f"រាងមិនកំណត់ $\\frac{{\\infty}}{{\\infty}}$ ។ អនុវត្តវិធានឡូពីតាល់ ${n}$ ដង ៖\n" + DM("L=\\lim_{x\\to+\\infty}" + "=\\lim_{x\\to+\\infty}".join(ch).replace("x^{1}", "x").replace("x^{0}", "")) + "ភាគយកចុងក្រោយជាចំនួនថេរ ហើយភាគបែងខិតជិត $+\\infty$ ដូច្នេះ $L=0$ ។"
        key = (k, n, a)
    elif k == 2:
        if a == b: return
        lim = f"\\lim_{{x\\to+\\infty}}\\frac{{{a}x+\\ln x}}{{{b}x+\\ln x}}"; val = Q(a, b); lhs = f"limit(({a}*x+log(x))/({b}*x+log(x)),x,oo)"
        body = "រាង $\\frac{\\infty}{\\infty}$ ។ តាមវិធានឡូពីតាល់ ៖\n" + DM(f"L=\\lim_{{x\\to+\\infty}}\\frac{{{a}+\\frac{{1}}{{x}}}}{{{b}+\\frac{{1}}{{x}}}}={L(val)}")
        key = (k, a, b)
    elif k == 3:
        lim = f"\\lim_{{x\\to 0^+}}x^{{{n}}}\\ln x"; val = 0; lhs = f"limit(x**{n}*log(x),x,0)"
        body = f"រាងមិនកំណត់ $0\\cdot\\infty$ ។ សរសេរជារាង $\\frac{{\\infty}}{{\\infty}}$ ៖\n" + DM(f"x^{{{n}}}\\ln x=\\frac{{\\ln x}}{{x^{{{-n}}}}}") + "តាមវិធានឡូពីតាល់ ៖\n" + DM(f"L=\\lim_{{x\\to 0^+}}\\frac{{\\frac{{1}}{{x}}}}{{{-n}x^{{{-n-1}}}}}=\\lim_{{x\\to 0^+}}\\left(-\\frac{{x^{{{n}}}}}{{{n}}}\\right)=0")
        key = (k, n)
    elif k == 4:
        lim = f"\\lim_{{x\\to+\\infty}}x\\left(e^{{\\frac{{{a}}}{{x}}}}-1\\right)"; val = a; lhs = f"limit(x*(exp({a}/x)-1),x,oo)"
        body = "រាង $\\infty\\cdot0$ ។ តាង $u=\\frac{1}{x}$ កាលណា $x\\to+\\infty$ នោះ $u\\to0^+$ ៖\n" + DM(f"L=\\lim_{{u\\to0^+}}\\frac{{e^{{{a}u}}-1}}{{u}}") + "ជារាង $\\frac{0}{0}$ ។ តាមវិធានឡូពីតាល់ ៖\n" + DM(f"L=\\lim_{{u\\to0^+}}{a}e^{{{a}u}}={a}")
        key = (k, a)
    elif k == 5:
        lim = f"\\lim_{{x\\to+\\infty}}x\\ln\\left(1+\\frac{{{a}}}{{x}}\\right)"; val = a; lhs = f"limit(x*log(1+{a}/x),x,oo)"
        body = "តាង $u=\\frac{1}{x}$ ។ កាលណា $x\\to+\\infty$ នោះ $u\\to0^+$ ៖\n" + DM(f"L=\\lim_{{u\\to0^+}}\\frac{{\\ln(1+{a}u)}}{{u}}") + "ជារាង $\\frac{0}{0}$ ។ ឡូពីតាល់ឲ្យ ៖\n" + DM(f"L=\\lim_{{u\\to0^+}}\\frac{{{a}}}{{1+{a}u}}={a}")
        key = (k, a)
    else:
        lim = f"\\lim_{{x\\to+\\infty}}\\frac{{\\ln({a}x+{b})}}{{\\ln x}}"; val = 1; lhs = f"limit(log({a}*x+{b})/log(x),x,oo)"
        body = "រាង $\\frac{\\infty}{\\infty}$ ។ តាមវិធានឡូពីតាល់ ៖\n" + DM(f"L=\\lim_{{x\\to+\\infty}}\\frac{{\\frac{{{a}}}{{{a}x+{b}}}}}{{\\frac{{1}}{{x}}}}=\\lim_{{x\\to+\\infty}}\\frac{{{a}x}}{{{a}x+{b}}}=1")
        key = (k, a, b)
    prob = P(f"គណនាលីមីតខាងក្រោម ៖ $L={lim}$ ។", f"រកតម្លៃនៃលីមីតខាងក្រោម ៖ $${lim}$$", f"ប្រើវិធានឡូពីតាល់ដើម្បីគណនា ${lim}$ ។")
    add("lhopital_infinity", P("medium", "hard"), key, prob, body + f"\n{fin()}\n" + BOX(f"L={L(val)}"), L(val), [check(lhs, st(val), "លីមីត")])

def g_lim_param():
    p = rng.randint(-5, 6); Lv = rng.randint(-6, 9); mode = P("quad", "sqrt", "exp")
    if mode == "quad":
        a = Lv - 2 * p; b = -p * p - a * p
        lim = f"\\lim_{{x\\to {p}}}\\frac{{x^2+ax+b}}{{x-({p})}}={Lv}".replace("x-(-", "x+(").replace("(" , "(")
        lim = f"\\lim_{{x\\to {p}}}\\frac{{x^2+ax+b}}{{{L(x-p)}}}={Lv}"
        prob = f"កំណត់ចំនួនពិត $a$ និង $b$ ដើម្បីឲ្យ ${lim}$ ។"
        sol = (f"ភាគបែងខិតជិត $0$ កាលណា $x\\to{p}$ ។ ដើម្បីឲ្យលីមីតមានតម្លៃកំណត់ ភាគយកត្រូវស្មើសូន្យត្រង់ $x={p}$ ៖\n" + DM(f"{p*p}+{L(p)}a+b=0\\quad(1)".replace("+-", "-")) + f"តាង $f(x)=x^2+ax+b$ ។ ពេលនោះលីមីតគឺ $f'({p})$ ។ ដោយ $f'(x)=2x+a$ ៖\n" + DM(f"{2*p}+a={Lv}\\Rightarrow a={a}") + f"ជំនួសក្នុង $(1)$ គេបាន $b={b}$ ។\n{fin()}\n" + BOX(f"a={a},\\quad b={b}"))
        ck = [check(f"limit((x**2+({a})*x+({b}))/(x-({p})),x,{p})", str(Lv), "លីមីត")]
        ans = f"a={a},\\ b={b}"
    elif mode == "sqrt":
        r = rng.randint(1, 7); lv = Q(1, 2 * r); c = r * r - abs(p)
        pp = abs(p) + 1; c = r * r - pp
        lim = f"\\lim_{{x\\to {pp}}}\\frac{{\\sqrt{{x+a}}-b}}{{x-{pp}}}={L(lv)}"
        prob = f"រកចំនួនពិត $a$ និង $b>0$ ដើម្បីឲ្យ ${lim}$ ។"
        sol = (f"ភាគយកត្រូវស្មើសូន្យត្រង់ $x={pp}$ ៖ $\\sqrt{{{pp}+a}}=b$ ។\nតាង $f(x)=\\sqrt{{x+a}}$ ។ លីមីតជាតម្លៃ $f'({pp})=\\frac{{1}}{{2\\sqrt{{{pp}+a}}}}=\\frac{{1}}{{2b}}$ ។\nគេបាន $\\frac{{1}}{{2b}}={L(lv)}$ នាំឲ្យ $b={r}$ ហើយ ${pp}+a={r*r}$ នាំឲ្យ $a={c}$ ។\n{fin()}\n" + BOX(f"a={c},\\quad b={r}"))
        ck = [check(f"limit((sqrt(x+({c}))-{r})/(x-{pp}),x,{pp})", st(lv), "លីមីត")]
        ans = f"a={c},\\ b={r}"
    else:
        a = rng.randint(1, 8); bb = rng.randint(1, 8); lv = Q(a, bb)
        lim = f"\\lim_{{x\\to 0}}\\frac{{e^{{mx}}-1}}{{{bb}x}}={L(lv)}"
        prob = f"រកតម្លៃ $m$ ដើម្បីឲ្យ ${lim}$ ។"
        sol = f"នេះជារាង $\\frac{{0}}{{0}}$ ។ តាមវិធានឡូពីតាល់ ៖\n" + DM(f"\\lim_{{x\\to 0}}\\frac{{me^{{mx}}}}{{{bb}}}=\\frac{{m}}{{{bb}}}") + f"លក្ខខណ្ឌ $\\frac{{m}}{{{bb}}}={L(lv)}$ នាំឲ្យ $m={a}$ ។\n{fin()}\n" + BOX(f"m={a}")
        ck = [check(f"limit((exp({a}*x)-1)/({bb}*x),x,0)", st(lv), "លីមីត")]
        ans = f"m={a}"; p = (a, bb)
    add("limit_parameter", P("medium", "hard"), (mode, p, Lv), prob, sol, ans, ck)

# =============================== DIFFERENTIALS ===============================
def g_approx():
    k = rng.randint(0, 6)
    if k == 0:
        a = rng.randint(2, 30); hh = P(Q(1, 10), Q(-1, 10), Q(1, 5), Q(2, 10), Q(-3, 10), 1, -1, Q(1, 2)); f = sp.sqrt(x); A = a * a; tgt = A + hh; sym = f"\\sqrt{{{L(sp.Float(tgt,6)) if False else dec(tgt)}}}"; rule = "(\\sqrt{x})'=\\frac{1}{2\\sqrt{x}}"
    elif k == 1:
        a = rng.randint(2, 10); hh = P(Q(1, 10), Q(-1, 10), Q(3, 10), 1, -1, 2); f = x**Q(1, 3); A = a**3; tgt = A + hh; sym = f"\\sqrt[3]{{{dec(tgt)}}}"; rule = "(x^{\\frac{1}{3}})'=\\frac{1}{3}x^{-\\frac{2}{3}}"
    elif k == 2:
        A = 1; hh = P(Q(1, 100), Q(2, 100), Q(-1, 100), Q(3, 100), Q(5, 100), Q(-2, 100)); n = rng.randint(3, 12); f = x**n; tgt = 1 + hh; sym = f"({dec(tgt)})^{{{n}}}"; rule = "(x^n)'=nx^{n-1}"
    elif k == 3:
        A = 1; hh = P(Q(1, 100), Q(2, 100), Q(-3, 100), Q(5, 100), Q(-1, 100), Q(4, 100)); f = sp.log(x); tgt = 1 + hh; sym = f"\\ln({dec(tgt)})"; rule = "(\\ln x)'=\\frac{1}{x}"
    elif k == 4:
        A = 0; hh = P(Q(1, 100), Q(2, 100), Q(-3, 100), Q(5, 100), Q(-1, 100), Q(1, 10)); f = sp.exp(x); tgt = hh; sym = f"e^{{{dec(tgt)}}}"; rule = "(e^x)'=e^x"
    elif k == 5:
        A = rng.randint(2, 20); hh = P(Q(1, 100), Q(-1, 100), Q(2, 100), Q(1, 10)); f = 1 / x; tgt = A + hh; sym = f"\\frac{{1}}{{{dec(tgt)}}}"; rule = "\\left(\\frac{1}{x}\\right)'=-\\frac{1}{x^2}"
    else:
        A = 0; hh = P(Q(1, 100), Q(2, 100), Q(3, 100), Q(5, 100)); f, sym0, rule = P((sp.sin(x), "\\sin", "(\\sin x)'=\\cos x"), (sp.tan(x), "\\tan", "(\\tan x)'=1+\\tan^2x")); tgt = hh; sym = f"{sym0}({dec(tgt)})"
    fa = sp.simplify(f.subs(x, A)); d = sp.diff(f, x); da = sp.simplify(d.subs(x, A))
    val = fa + da * hh
    prob = P(f"ដោយប្រើឌីផេរ៉ង់ស្យែល គណនាតម្លៃប្រហែលនៃ ${sym}$ ។", f"គណនាតម្លៃប្រហែលនៃ ${sym}$ ដោយមិនប្រើម៉ាស៊ីនគិតលេខ ។", f"តាមរូបមន្ត $f(a+h)\\approx f(a)+hf'(a)$ រកតម្លៃប្រហែលនៃ ${sym}$ ។")
    sol = (f"តាង $f(x)={L(f)}$ ។ យក $a={L(A)}$ និង $h={L(hh)}$ ព្រោះ $f(a)$ គណនាបានងាយ ហើយ $h$ តូច ។\n"
           + f"តាមរូបមន្ត ${rule}$ ។ គេបាន $f({L(A)})={L(fa)}$ និង $f'({L(A)})={L(da)}$ ។\nតាមរូបមន្តតម្លៃប្រហែល ៖\n"
           + DM(f"f(a+h)\\approx f(a)+hf'(a)={L(fa)}+\\left({L(hh)}\\right)\\left({L(da)}\\right)={L(val)}") + f"{fin()}\n" + BOX(f"{sym}\\approx {L(val)}\\approx {dec(val)}"))
    add("linear_approximation", P("easy", "medium"), (f, tgt), prob, sol, f"{sym}\\approx {L(val)}", [check(f"({st(f)}).subs(x,{st(A)})+({st(hh)})*diff({st(f)},x).subs(x,{st(A)})", st(val), "តម្លៃប្រហែល")])

def g_differential():
    k = rng.randint(0, 3); a = rng.randint(1, 6); dx = P(Q(1, 10), Q(1, 100), Q(-1, 10), Q(1, 5), Q(1, 20), Q(1, 2))
    p, q, r = rng.randint(1, 5), rng.randint(-5, 5), rng.randint(-5, 5)
    f = [p * x**2 + q * x + r, p * x**3 + q * x, x**2 + q * x + r, p * x**3 - q * x**2 + r][k]
    d = sp.diff(f, x); dy = d.subs(x, a) * dx; Dy = f.subs(x, a + dx) - f.subs(x, a)
    prob = P(f"គេឲ្យ $y={L(f)}$ ។ គណនាឌីផេរ៉ង់ស្យែល $dy$ និងកំណើនពិត $\\Delta y$ ត្រង់ $x={a}$ ចំពោះ $dx=\\Delta x={L(dx)}$ រួចរកកម្រិតខុសគ្នា $\\Delta y-dy$ ។", f"ចំពោះអនុគមន៍ $y={L(f)}$ រកឌីផេរ៉ង់ស្យែល $dy$ រួចប្រៀបធៀប $dy$ ជាមួយ $\\Delta y$ កាលណា $x={a}$ និង $dx={L(dx)}$ ។")
    sol = (f"ឌីផេរ៉ង់ស្យែលកំណត់ដោយ $dy=y'dx$ ។\n" + DM(f"dy=({L(d)})dx") + f"ត្រង់ $x={a}$ និង $dx={L(dx)}$ ៖\n" + DM(f"dy=\\left({L(d.subs(x,a))}\\right)\\left({L(dx)}\\right)={L(dy)}") + "កំណើនពិត ៖\n" + DM(f"\\Delta y=f({L(a+dx)})-f({a})={L(f.subs(x,a+dx))}-\\left({L(f.subs(x,a))}\\right)={L(Dy)}") + f"ផលសងគឺ $\\Delta y-dy={L(Dy-dy)}$ ដែលតូចណាស់ធៀបនឹង $\\Delta y$ ។\n{fin()}\n" + BOX(f"dy={L(dy)},\\quad \\Delta y={L(Dy)}"))
    F = st(f)
    add("differentials", P("easy", "medium"), (f, a, dx), prob, sol, f"dy={L(dy)},\\ \\Delta y={L(Dy)}", [check(f"diff({F},x).subs(x,{a})*{st(dx)}", st(dy), "dy"), check(f"({F}).subs(x,{st(a+dx)})-({F}).subs(x,{a})", st(Dy), "Δy")])

def g_error():
    sh = P(("ស្វ៊ែ", "កាំ", Q(4, 3) * PI * x**3, "មាឌ", "V=\\frac{4}{3}\\pi r^3", "r"), ("គូប", "ជ្រុង", x**3, "មាឌ", "V=a^3", "a"), ("រង្វង់", "កាំ", PI * x**2, "ក្រឡាផ្ទៃ", "S=\\pi r^2", "r"), ("ការ៉េ", "ជ្រុង", x**2, "ក្រឡាផ្ទៃ", "S=a^2", "a"), ("ស្វ៊ែ", "កាំ", 4 * PI * x**2, "ក្រឡាផ្ទៃ", "S=4\\pi r^2", "r"))
    r0 = rng.randint(2, 60); e = P(Q(1, 10), Q(1, 20), Q(1, 100), Q(1, 5), Q(1, 50))
    f = sh[2]; dV = sp.diff(f, x).subs(x, r0) * e; rel = dV / f.subs(x, r0); nv = sh[5]
    nm = sh[4][0]
    pn = P(*PEOPLE)
    prob = f"{pn}វាស់{sh[1]}នៃ{sh[0]}មួយបាន ${r0}$ សង់ទីម៉ែត្រ ដោយមានលម្អៀងអតិបរមា $\\pm{L(e)}$ សង់ទីម៉ែត្រ ។ ដោយប្រើឌីផេរ៉ង់ស្យែល ប៉ាន់ស្មានលម្អៀងនៃ{sh[3]} និងលម្អៀងធៀប ។"
    sol = (f"រូបមន្ត ៖ ${sh[4]}$ ។ ឌីផេរ៉ង់ស្យែល ៖\n" + DM(f"d{nm}={L(sp.diff(f,x),nv)}\\,d{nv}") + f"ជំនួស ${nv}={r0}$ និង $d{nv}={L(e)}$ ៖\n" + DM(f"d{nm}={L(dV)}") + "លម្អៀងធៀប ៖\n" + DM(f"\\frac{{d{nm}}}{{{nm}}}=\\frac{{{L(dV)}}}{{{L(f.subs(x,r0))}}}={L(rel)}") + f"{fin()}\n" + BOX(f"d{nm}\\approx\\pm{L(dV)},\\quad \\frac{{d{nm}}}{{{nm}}}\\approx{L(rel)}"))
    F = st(f)
    add("differentials", "medium", (f, r0, e), prob, sol, f"d{nm}={L(dV)}", [check(f"diff({F},x).subs(x,{r0})*{st(e)}", st(dV)), check(f"diff({F},x).subs(x,{r0})*{st(e)}/({F}).subs(x,{r0})", st(rel))])

def g_linear():
    f, a = P((sp.sqrt(x), P(1, 4, 9, 16, 25, 36)), (sp.log(x), 1), (sp.exp(x), 0), (sp.sin(x), 0), (sp.cos(x), PI / 2), (1 / (1 + x), 0), (sp.sqrt(1 + x), 0), (sp.sqrt(1 + 2 * x), 0), ((1 + x)**rng.randint(3, 12), 0), (x**rng.randint(3, 7), P(1, 2)), (1 / x, P(1, 2, 3, 4, 5)), (sp.sin(x), PI), (sp.exp(2 * x), 0), (sp.exp(-x), 0), (sp.log(1 + x), 0), (sp.log(2 * x + 1), 0), (x * sp.exp(x), 0), (x * sp.log(x), 1))
    a = sp.sympify(a); d = sp.diff(f, x)
    fa = f.subs(x, a); da = d.subs(x, a); Lin = fa + da * (x - a); Le = sp.expand(Lin)
    prob = P(f"រករូបមន្តប្រហែលលីនេអ៊ែរនៃ $f(x)={L(f)}$ ក្បែរ $x={L(a)}$ ។", f"សរសេរសមីការបន្ទាត់ប៉ះនៃខ្សែកោង $y={L(f)}$ ត្រង់ $x={L(a)}$ រួចទាញរកតម្លៃប្រហែលនៃ $f(x)$ ពេល $x$ ក្បែរ ${L(a)}$ ។")
    sol = (f"គេមាន $f({L(a)})={L(fa)}$ ។ ដេរីវេ ៖\n" + DM(f"f'(x)={L(d)}") + f"ដូច្នេះ $f'({L(a)})={L(da)}$ ។\nបន្ទាត់ប៉ះត្រង់ $x={L(a)}$ មានសមីការ $y=f(a)+f'(a)(x-a)$ ។\n" + DM(f"y={L(Le)}") + f"{fin()} ចំពោះ $x$ ក្បែរ ${L(a)}$ ៖\n" + BOX(f"{L(f)}\\approx {L(Le)}"))
    add("linear_approximation", P("easy", "medium"), (f, a, "lin"), prob, sol, f"{L(f)}\\approx {L(Le)}", [check(f"({st(f)}).subs(x,{st(a)})+diff({st(f)},x).subs(x,{st(a)})*(x-({st(a)}))", st(Le), "បន្ទាត់ប៉ះ")])

# =============================== ROLLE AND MEAN VALUE ===============================
def g_rolle():
    k = rng.randint(0, 5)
    if k == 0:
        a, b = sorted(rng.sample(range(-6, 9), 2)); q = rng.randint(-4, 6); p = P(1, 2, -1, 3); f = p * (x - a) * (x - b) + q; c = Q(a + b, 2)
    elif k == 1:
        a, b = sorted(rng.sample(range(-5, 8), 2)); f = sp.expand((x - a)**2 * (x - b)); c = Q(a + 2 * b, 3)
    elif k == 2:
        a, b = sorted(rng.sample(range(-5, 8), 2)); f = sp.expand((x - a) * (x - b)**2); c = Q(2 * a + b, 3)
    elif k == 3:
        A = rng.randint(1, 6); f, a, b, c = P((A * sp.sin(x), 0, PI, PI / 2), (A * sp.cos(x), -PI / 2, PI / 2, sp.Integer(0)), (sp.sin(x) + sp.cos(x), 0, PI / 2, PI / 4), (A * sp.sin(2 * x), 0, PI / 2, PI / 4))
    elif k == 4:
        A = 3 * rng.randint(1, 9); f = x * sp.sqrt(A - x); a, b, c = 0, A, sp.Integer(2 * A // 3)
    else:
        n = rng.randint(1, 6); f = x**2 + Q(n * n * 4) / x**2 if False else x + Q(n * n) / x; a, b, c = sp.Integer(n) / 2 if False else Q(n, 2), 2 * n, sp.Integer(n)
    a, b = sp.sympify(a), sp.sympify(b)
    d = sp.diff(f, x)
    fa, fb = sp.simplify(f.subs(x, a)), sp.simplify(f.subs(x, b))
    if fa != fb: return
    prob = P(f"ផ្ទៀងផ្ទាត់ថាអនុគមន៍ $f(x)={L(f)}$ បំពេញលក្ខខណ្ឌទ្រឹស្តីបទរ៉ូលលើចន្លោះ $[{L(a)};{L(b)}]$ រួចរកចំនួន $c$ ដែល $f'(c)=0$ ។", f"គេឲ្យ $f(x)={L(f)}$ លើ $[{L(a)};{L(b)}]$ ។ ស្រាយបញ្ជាក់ថាមាន $c\\in({L(a)};{L(b)})$ យ៉ាងតិចមួយ ដែល $f'(c)=0$ ហើយកំណត់តម្លៃ $c$ ។")
    if k == 4: cont = f"$f$ ជាប់លើ $[{L(a)};{L(b)}]$ និងមានដេរីវេលើ $({L(a)};{L(b)})$ ។"
    elif k == 5: cont = f"ដោយ $0\\notin[{L(a)};{L(b)}]$ អនុគមន៍ $f$ ជាប់លើ $[{L(a)};{L(b)}]$ និងមានដេរីវេលើ $({L(a)};{L(b)})$ ។"
    else: cont = "$f$ ជាប់ និងមានដេរីវេលើ $IR$ ដូច្នេះជាប់លើចន្លោះបិទ និងមានដេរីវេលើចន្លោះបើក ។"
    dd = sp.factor(d) if f.is_polynomial(x) else d
    roots = f"$f'(c)=0$ ឲ្យ $c={L(c)}$ ដែលស្ថិតនៅក្នុងចន្លោះ $({L(a)};{L(b)})$ ។"
    sol = (cont + f"\nគណនាតម្លៃចុងចន្លោះ ៖ $f({L(a)})={L(fa)}$ និង $f({L(b)})={L(fb)}$ ។ ដូច្នេះ $f({L(a)})=f({L(b)})$ ។\nលក្ខខណ្ឌទ្រឹស្តីបទរ៉ូលត្រូវបានបំពេញ ។\nដេរីវេ ៖\n" + DM(f"f'(x)={L(dd)}") + roots + f"\n{fin()}\n" + BOX(f"c={L(c)}"))
    F = st(f)
    ck = [vchk(f, a, fa), vchk(f, b, fb), check(f"diff({F},x).subs(x,{st(c)})", "0", "c")]
    add("rolle_theorem", P("easy", "medium"), (f, a, b), prob, sol, f"c={L(c)}", ck)

def g_mvt():
    k = rng.randint(0, 6)
    if k == 0:
        p, q, r = rng.randint(1, 5), rng.randint(-6, 6), rng.randint(-6, 6); a, b = sorted(rng.sample(range(-5, 10), 2)); f = p * x**2 + q * x + r; c = Q(a + b, 2)
    elif k == 1:
        p = rng.randint(1, 4); b = 3 * rng.randint(1, 3); a = 0; f = p * x**3 + rng.randint(-3, 3) * x; c = b / sp.sqrt(3)
    elif k == 2:
        m_, n = sorted(rng.sample(range(1, 10), 2)); a, b = m_ * m_, n * n; f = Q(rng.randint(1, 6)) / x; c = sp.Integer(m_ * n)
    elif k == 3:
        m_, n = sorted(rng.sample(range(0, 11), 2)); a, b = m_ * m_, n * n; A = rng.randint(1, 4); f = A * sp.sqrt(x); c = Q(m_ + n, 2)**2
    elif k == 4:
        a, b = 1, sp.E; f = sp.log(x); c = sp.E - 1
    elif k == 5:
        a, b = 0, 1; f = sp.exp(x); c = sp.log(sp.E - 1)
    else:
        n = rng.randint(1, 8); a, b = 0, n; f = x / (x + n) if False else sp.sqrt(x + 1) if False else (x - n)**2 * x + 0 * x if False else x**2 - n * x + rng.randint(-5, 5); c = Q(n, 2)
    a, b = sp.sympify(a), sp.sympify(b)
    fa, fb = f.subs(x, a), f.subs(x, b); sl = sp.simplify(sp.simplify((fb - fa) / (b - a))); d = sp.diff(f, x)
    if k == 4: sl = 1 / (sp.E - 1)
    if k == 5: sl = sp.E - 1
    prob = P(f"អនុវត្តទ្រឹស្តីបទតម្លៃមធ្យមចំពោះ $f(x)={L(f)}$ លើ $[{L(a)};{L(b)}]$ ហើយរកចំនួន $c$ ។", f"រកចំនួន $c\\in({L(a)};{L(b)})$ ដែលបន្ទាត់ប៉ះខ្សែកោង $y={L(f)}$ ត្រង់ $x=c$ ស្របនឹងបន្ទាត់កាត់តាមចំណុចចុងទាំងពីរនៃខ្សែកោងលើ $[{L(a)};{L(b)}]$ ។")
    sol = (f"$f$ ជាប់លើ $[{L(a)};{L(b)}]$ និងមានដេរីវេលើ $({L(a)};{L(b)})$ ។ តាមទ្រឹស្តីបទតម្លៃមធ្យម មាន $c$ ក្នុងចន្លោះនេះដែល ៖\n" + DM(f"f'(c)=\\frac{{f({L(b)})-f({L(a)})}}{{{L(b-a)}}}")
           + f"គណនា ៖ $f({L(a)})={L(fa)}$ និង $f({L(b)})={L(fb)}$ ដូច្នេះមេគុណប្រាប់ទិសនៃអង្កត់គឺ ${L(sl)}$ ។\nដេរីវេ ៖ $f'(x)={L(d)}$ ។\n" + DM(f"f'(c)={L(sl)}\\Rightarrow c={L(c)}") + f"តម្លៃនេះស្ថិតក្នុង $({L(a)};{L(b)})$ ។\n{fin()}\n" + BOX(f"c={L(c)}"))
    F = st(f)
    ck = [check(f"diff({F},x).subs(x,{st(c)})", st(sl), "f'(c)"), check(f"(({F}).subs(x,{st(b)})-({F}).subs(x,{st(a)}))/({st(b)}-({st(a)}))", st(sl), "មេគុណប្រាប់ទិស")]
    add("mean_value_theorem", P("medium", "medium", "easy"), (f, a, b), prob, sol, f"c={L(c)}", ck)

def g_mvt_ineq():
    k = rng.randint(0, 5); n = rng.randint(1, 40); a = rng.randint(1, 15); b = a + rng.randint(1, 15)
    if k == 0:
        prob = f"ដោយប្រើទ្រឹស្តីបទតម្លៃមធ្យមចំពោះ $f(x)=\\ln x$ លើ $[{n};{n+1}]$ ស្រាយបញ្ជាក់ថា $\\frac{{1}}{{{n+1}}}<\\ln{L(Q(n+1,n))}<\\frac{{1}}{{{n}}}$ ។".replace("\\ln\\frac", "\\ln\\frac")
        sol = (f"$f$ ជាប់ និងមានដេរីវេលើ $[{n};{n+1}]$ ដោយ $f'(x)=\\frac{{1}}{{x}}$ ។ មាន $c\\in({n};{n+1})$ ដែល ៖\n" + DM(f"\\ln{n+1}-\\ln{n}=\\frac{{1}}{{c}}({n+1}-{n})=\\frac{{1}}{{c}}") + f"ដោយ ${n}<c<{n+1}$ នោះ $\\frac{{1}}{{{n+1}}}<\\frac{{1}}{{c}}<\\frac{{1}}{{{n}}}$ ។\n{fin()}\n" + BOX(f"\\frac{{1}}{{{n+1}}}<\\ln{L(Q(n+1,n))}<\\frac{{1}}{{{n}}}"))
        ck = [check("diff(log(x),x)", "1/x"), check(f"log({n+1}/{n}) > Rational(1,{n+1})", "True"), check(f"log({n+1}/{n}) < Rational(1,{n})", "True")]
        key = (k, n)
    elif k == 1:
        prob = f"ដោយប្រើទ្រឹស្តីបទតម្លៃមធ្យមចំពោះ $f(x)=\\sqrt{{x}}$ ស្រាយបញ្ជាក់ថា $\\frac{{1}}{{2\\sqrt{{{n+1}}}}}<\\sqrt{{{n+1}}}-\\sqrt{{{n}}}<\\frac{{1}}{{2\\sqrt{{{n}}}}}$ ។"
        sol = (f"$f$ ជាប់លើ $[{n};{n+1}]$ និង $f'(x)=\\frac{{1}}{{2\\sqrt{{x}}}}$ ។ មាន $c\\in({n};{n+1})$ ដែល ៖\n" + DM(f"\\sqrt{{{n+1}}}-\\sqrt{{{n}}}=\\frac{{1}}{{2\\sqrt{{c}}}}") + f"ដោយ $\\sqrt{{{n}}}<\\sqrt{{c}}<\\sqrt{{{n+1}}}$ នោះគេបានវិសមភាពដែលត្រូវស្រាយ ។\n{fin()} វិសមភាពពិតតាមទ្រឹស្តីបទ ។\n" + BOX(f"\\frac{{1}}{{2\\sqrt{{{n+1}}}}}<\\sqrt{{{n+1}}}-\\sqrt{{{n}}}<\\frac{{1}}{{2\\sqrt{{{n}}}}}"))
        ck = [check("diff(sqrt(x),x)", "1/(2*sqrt(x))"), check(f"sqrt({n+1})-sqrt({n}) < 1/(2*sqrt({n}))", "True"), check(f"sqrt({n+1})-sqrt({n}) > 1/(2*sqrt({n+1}))", "True")]
        key = (k, n)
    elif k == 2:
        prob = f"ស្រាយបញ្ជាក់ថា $\\frac{{{b-a}}}{{{b}}}<\\ln{L(Q(b,a))}<\\frac{{{b-a}}}{{{a}}}$ ។".replace("\\ln\\frac", "\\ln\\frac")
        sol = (f"អនុវត្តទ្រឹស្តីបទតម្លៃមធ្យមចំពោះ $f(x)=\\ln x$ លើ $[{a};{b}]$ ។ មាន $c\\in({a};{b})$ ដែល ៖\n" + DM(f"\\ln{b}-\\ln{a}=\\frac{{{b-a}}}{{c}}") + f"ដោយ $\\frac{{1}}{{{b}}}<\\frac{{1}}{{c}}<\\frac{{1}}{{{a}}}$ គុណនឹង ${b-a}>0$ ៖\n{fin()}\n" + BOX(f"\\frac{{{b-a}}}{{{b}}}<\\ln{L(Q(b,a))}<\\frac{{{b-a}}}{{{a}}}"))
        ck = [check(f"log({b}/{a}) > Rational({b-a},{b})", "True"), check(f"log({b}/{a}) < Rational({b-a},{a})", "True"), check("diff(log(x),x)", "1/x")]
        key = (k, a, b)
    elif k == 3:
        A = rng.randint(1, 9)
        prob = f"ស្រាយបញ្ជាក់ថា ចំពោះគ្រប់ចំនួនពិត $a$ និង $b$ គេមាន $|\\sin({A}a)-\\sin({A}b)|\\le {A}|a-b|$ ។"
        sol = (f"តាង $f(x)=\\sin({A}x)$ ។ $f$ ជាប់និងមានដេរីវេលើ $IR$ ដោយ $f'(x)={A}\\cos({A}x)$ ។\nបើ $a=b$ វិសមភាពពិត ។ បើ $a\\ne b$ តាមទ្រឹស្តីបទតម្លៃមធ្យម មាន $c$ នៅចន្លោះ $a$ និង $b$ ដែល ៖\n" + DM(f"\\sin({A}a)-\\sin({A}b)={A}\\cos({A}c)(a-b)") + f"ដោយ $|\\cos({A}c)|\\le1$ ។\n{fin()}\n" + BOX(f"|\\sin({A}a)-\\sin({A}b)|\\le {A}|a-b|"))
        ck = [check(f"diff(sin({A}*x),x)", f"{A}*cos({A}*x)")]
        key = (k, A)
    elif k == 4:
        A = rng.randint(1, 9)
        prob = f"ស្រាយបញ្ជាក់ថា ចំពោះ $x>0$ គេមាន $\\frac{{{A}x}}{{1+{A}x}}<\\ln(1+{A}x)<{A}x$ ។"
        sol = (f"តាង $f(t)=\\ln(1+{A}t)$ លើ $[0;x]$ ។ $f'(t)=\\frac{{{A}}}{{1+{A}t}}$ ។\nតាមទ្រឹស្តីបទតម្លៃមធ្យម មាន $c\\in(0;x)$ ដែល ៖\n" + DM(f"\\ln(1+{A}x)-\\ln1=\\frac{{{A}x}}{{1+{A}c}}") + f"ដោយ $0<c<x$ នោះ $1<1+{A}c<1+{A}x$ ។ ច្រាសរួចគុណនឹង ${A}x>0$ ៖\n{fin()}\n" + BOX(f"\\frac{{{A}x}}{{1+{A}x}}<\\ln(1+{A}x)<{A}x"))
        ck = [check(f"diff(log(1+{A}*x),x)", f"{A}/(1+{A}*x)"), check(f"log(1+{A}*3) < {A}*3", "True"), check(f"log(1+{A}*3) > Rational({3*A},{1+3*A})", "True")]
        key = (k, A)
    else:
        prob = f"ដោយប្រើទ្រឹស្តីបទតម្លៃមធ្យមចំពោះ $f(x)=e^x$ លើ $[{a};{b}]$ បង្ហាញថា ${b-a}e^{{{a}}}<e^{{{b}}}-e^{{{a}}}<{b-a}e^{{{b}}}$ ។"
        sol = (f"$f'(x)=e^x$ ។ មាន $c\\in({a};{b})$ ដែល ៖\n" + DM(f"e^{{{b}}}-e^{{{a}}}={b-a}e^c") + f"ដោយអនុគមន៍ $e^x$ កើន ហើយ ${a}<c<{b}$ នោះ $e^{{{a}}}<e^c<e^{{{b}}}$ ។\n{fin()}\n" + BOX(f"{b-a}e^{{{a}}}<e^{{{b}}}-e^{{{a}}}<{b-a}e^{{{b}}}"))
        ck = [check("diff(exp(x),x)", "exp(x)"), check(f"exp({b})-exp({a}) > {b-a}*exp({a})", "True"), check(f"exp({b})-exp({a}) < {b-a}*exp({b})", "True")]
        key = (k, a, b)
    add("mvt_inequality", P("hard", "bacii"), key, prob, sol, "\\text{ពិត}" if False else "\\square", ck)

def g_roots():
    k = rng.randint(0, 3)
    if k == 0:
        a, b = rng.randint(1, 9), rng.randint(-9, 9); c = -(Q(a, 3) + Q(b, 2)); Pp = a * x**2 + b * x + c; F = Q(a, 3) * x**3 + Q(b, 2) * x**2 + c * x
        prob = f"ស្រាយបញ្ជាក់ថាសមីការ ${L(Pp)}=0$ មានឫសយ៉ាងតិចមួយក្នុងចន្លោះ $(0;1)$ ។"
        sol = (f"តាង $F(x)={L(F)}$ ។ គេបាន $F'(x)={L(Pp)}$ ។\n$F$ ជាប់និងមានដេរីវេលើ $IR$ ហើយ $F(0)=0$ និង $F(1)={L(F.subs(x,1))}$ ។\nតាមទ្រឹស្តីបទរ៉ូល មាន $c\\in(0;1)$ ដែល $F'(c)=0$ ។\n{fin()} សមីការមានឫស $c\\in(0;1)$ ។")
        ck = [dchk(F, Pp), vchk(F, 1, 0), vchk(F, 0, 0)]; key = (k, Pp); ans = "c\\in(0;1)"
    elif k == 1:
        r = sorted(rng.sample(range(-6, 9), P(3, 3, 4)))
        f = sp.Integer(1)
        for t in r: f *= (x - t)
        n = len(r)
        ints = " ".join(f"$({r[i]};{r[i+1]})$" for i in range(n - 1))
        prob = f"គេឲ្យ $f(x)={L(f)}$ ។ ដោយមិនគណនាដេរីវេ បង្ហាញថាសមីការ $f'(x)=0$ មានឫសពិតចំនួន ${n-1}$ គត់ ហើយកំណត់ចន្លោះនៃឫសនីមួយៗ ។"
        sol = (f"$f$ ជាពហុធា ដូច្នេះជាប់និងមានដេរីវេលើ $IR$ ។ គេបាន " + ", ".join(f"$f({t})=0$" for t in r) + f" ។\nតាមទ្រឹស្តីបទរ៉ូលលើចន្លោះនីមួយៗ {ints} សមីការ $f'(x)=0$ មានឫសយ៉ាងតិចមួយក្នុងចន្លោះនីមួយៗ ។\nដោយ $f$ មានដឺក្រេ ${n}$ នោះ $f'$ មានដឺក្រេ ${n-1}$ ហើយមានឫសមិនលើសពី ${n-1}$ ។\n{fin()} $f'(x)=0$ មានឫសពិត ${n-1}$ គត់ គឺមួយក្នុងចន្លោះនីមួយៗ ។")
        ck = [vchk(f, t, 0) for t in r]; key = (k, tuple(r)); ans = f"{n-1}"
    elif k == 2:
        p, q = rng.randint(1, 9), rng.randint(-20, 20)
        if q == 0: return
        f = x**3 + p * x + q
        l, h = -abs(q) - 1, abs(q) + 1
        prob = f"ស្រាយបញ្ជាក់ថាសមីការ ${L(f)}=0$ មានឫសពិតតែមួយគត់ ។"
        sol = (f"តាង $f(x)={L(f)}$ ។ $f$ ជាប់លើ $IR$ ។\nភាពមានឫស ៖ $f({l})={L(f.subs(x,l))}<0$ និង $f({h})={L(f.subs(x,h))}>0$ ដូច្នេះសមីការមានឫសយ៉ាងតិចមួយក្នុង $({l};{h})$ ។\nភាពតែមួយគត់ ៖ បើមានឫសពីរ $a<b$ នោះ $f(a)=f(b)$ ហើយតាមទ្រឹស្តីបទរ៉ូល មាន $c$ ដែល $f'(c)=0$ ។ ប៉ុន្តែ $f'(x)=3x^2+{p}>0$ ជានិច្ច នេះផ្ទុយ ។\n{fin()} សមីការមានឫសពិតតែមួយគត់ ។")
        ck = [dchk(f, 3 * x**2 + p), check(f"({st(f)}).subs(x,{l}) < 0", "True"), check(f"({st(f)}).subs(x,{h}) > 0", "True")]; key = (k, f); ans = "1"
    else:
        a = rng.randint(1, 9)
        f = sp.exp(x) + a * x
        prob = f"ស្រាយបញ្ជាក់ថាសមីការ $e^x+{a}x=0$ មានឫសមិនលើសពីមួយ រួចបង្ហាញថាឫសនោះស្ថិតនៅក្នុង $(-1;0)$ ។"
        sol = (f"តាង $f(x)=e^x+{a}x$ ។ បើមានឫសពីរ តាមទ្រឹស្តីបទរ៉ូល មាន $c$ ដែល $f'(c)=0$ ប៉ុន្តែ $f'(x)=e^x+{a}>0$ ជានិច្ច ។ ដូច្នេះមានឫសមិនលើសពីមួយ ។\n$f(-1)=e^{{-1}}-{a}<0$ និង $f(0)=1>0$ ។ $f$ ជាប់ ដូច្នេះមានឫសក្នុង $(-1;0)$ ។\n{fin()} សមីការមានឫសតែមួយគត់ក្នុង $(-1;0)$ ។")
        ck = [dchk(f, sp.exp(x) + a), check(f"exp(-1)-{a} < 0", "True"), vchk(f, 0, 1)]; key = (k, a); ans = "x_0\\in(-1;0)"
    add("rolle_roots", P("hard", "bacii"), key, prob, sol, ans, ck)

def g_speed():
    frm, to, D0, lim = P(("ភ្នំពេញ", "ព្រះសីហនុ", 180, 100), ("ភ្នំពេញ", "បាវិត", 160, 90), ("សៀមរាប", "ភ្នំពេញ", 300, 90), ("ភ្នំពេញ", "បាត់ដំបង", 280, 90), ("ភ្នំពេញ", "កំពត", 150, 80), ("ភ្នំពេញ", "ក្រចេះ", 240, 80))
    D = D0 + rng.choice(range(-20, 21, 5)); T = sp.sympify(P(Q(3, 2), 2, Q(5, 2), 3, Q(7, 2), Q(9, 4), Q(11, 4))); pn = P(*PEOPLE)
    v = D / T
    if v <= lim: return
    prob = f"{pn}បើកបររថយន្តពី{frm}ទៅ{to} ចម្ងាយ ${D}$ គីឡូម៉ែត្រ ក្នុងរយៈពេល ${L(T)}$ ម៉ោង ។ ល្បឿនកំណត់គឺ ${lim}$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ។ ដោយប្រើទ្រឹស្តីបទតម្លៃមធ្យម បង្ហាញថាយ៉ាងហោចណាស់មានខណៈមួយដែល{pn}បើកលើសល្បឿនកំណត់ ។"
    sol = (f"តាង $s(t)$ ជាចម្ងាយដែលបានធ្វើដំណើរក្រោយ $t$ ម៉ោង ។ $s$ ជាប់លើ $[0;{L(T)}]$ និងមានដេរីវេ ព្រោះរថយន្តធ្វើចលនារលូន ។\nតាមទ្រឹស្តីបទតម្លៃមធ្យម មាន $c\\in(0;{L(T)})$ ដែល ៖\n" + DM(f"s'(c)=\\frac{{s({L(T)})-s(0)}}{{{L(T)}-0}}=\\frac{{{D}}}{{{L(T)}}}={L(v)}") + f"ដោយ ${L(v)}>{lim}$ ។\n{fin()} នៅខណៈ $t=c$ ល្បឿនខណៈស្មើ ៖\n" + BOX(f"s'(c)={L(v)}") + "គីឡូម៉ែត្រក្នុងមួយម៉ោង ដែលលើសល្បឿនកំណត់ ។")
    add("mean_value_theorem", "medium", (D, T, pn), prob, sol, f"s'(c)={L(v)}", [check(f"{D}/({st(T)})", st(v), "ល្បឿនមធ្យម"), check(f"{st(v)} > {lim}", "True")])

# =============================== HAND-WRITTEN ROWS ===============================
def H(sub, diff, prob, sol, ans, checks, diagrams=None):
    assert add(sub, diff, "hand:" + prob[:60], prob, sol, ans, checks, diagrams)

def hand():
    C = check
    H("optimization_geometry", "easy", r"នៅថ្ងៃបុណ្យចូលឆ្នាំ ដារ៉ាចង់ធ្វើខ្លែង ដោយចងឫស្សីពីរដើមកែងគ្នាធ្វើជាអង្កត់ទ្រូង ។ ឫស្សីទាំងពីរមានប្រវែងសរុប $120$ សង់ទីម៉ែត្រ ។ តើត្រូវកាត់ឫស្សីយ៉ាងណា ទើបខ្លែងមានក្រឡាផ្ទៃធំបំផុត?",
      "ខ្លែងមានអង្កត់ទ្រូងកែងគ្នា ដូច្នេះក្រឡាផ្ទៃស្មើពាក់កណ្តាលផលគុណអង្កត់ទ្រូង ។\nតាង $x$ ជាប្រវែងឫស្សីទី១ នោះឫស្សីទី២មានប្រវែង $120-x$ ដែល $0<x<120$ ។\n$$S(x)=\\frac{x(120-x)}{2}=60x-\\frac{x^2}{2}$$\nដេរីវេ $S'(x)=60-x$ រលាយត្រង់ $x=60$ ។ ដោយ $S''(x)=-1<0$ នោះ $S$ មានអតិបរមាត្រង់នោះ ។\nឫស្សីទាំងពីរត្រូវវែងស្មើគ្នា ហើយ $S(60)=1800$ ។\nដូចនេះ ត្រូវកាត់ជាពីរកំណាត់ស្មើគ្នា ៖\n$$\\boxed{60\\text{ cm},\\ S_{\\max}=1800}$$".replace("\\text{ cm}", ""),
      "x=60,\\ S_{\\max}=1800", [C("diff(x*(120-x)/2,x).subs(x,60)", "0"), C("(x*(120-x)/2).subs(x,60)", "1800")])
    H("optimization_geometry", "medium", r"សហគមន៍កសិករមួយនៅស្រុកបាទី ខេត្តតាកែវ ចង់ជីកប្រឡាយស្រោចស្រពដែលមានមុខកាត់រាងចតុកោណកែង ។ គេមានបេតុងអាចចាក់បានប្រវែងសរុប $12$ ម៉ែត្រ សម្រាប់បាតនិងជញ្ជាំងទាំងពីរ ។ ដើម្បីឲ្យទឹកហូរបានច្រើនបំផុត ត្រូវឲ្យជម្រៅប៉ុន្មាន?",
      "ទឹកហូរបានច្រើនបំផុតពេលក្រឡាផ្ទៃមុខកាត់ធំបំផុត ។\nតាង $x$ ជាជម្រៅ (ម៉ែត្រ) ។ បាតប្រឡាយវែង $12-2x$ ដូច្នេះ $0<x<6$ ។\n$$S(x)=x(12-2x)=12x-2x^2$$\nគេបាន $S'(x)=12-4x$ ។ $S'(x)>0$ ពេល $x<3$ និង $S'(x)<0$ ពេល $x>3$ ។\nនៅ $x=3$ បាតវែង $6$ ម៉ែត្រ ហើយ $S(3)=18$ ។\nដូចនេះ ជម្រៅល្អបំផុតគឺ ៖\n$$\\boxed{x=3}$$\nម៉ែត្រ ហើយមុខកាត់មានក្រឡាផ្ទៃ $18$ ម៉ែត្រការ៉េ ។",
      "x=3", [C("diff(x*(12-2*x),x).subs(x,3)", "0"), C("(x*(12-2*x)).subs(x,3)", "18")], [fig(fig_fence("12-2x", "x"), "មុខកាត់ប្រឡាយរាងចតុកោណកែង")])
    H("optimization_trig", "hard", r"ផ្ទាំងបដាបុណ្យអុំទូកមួយព្យួរលើជញ្ជាំង ដោយគែមក្រោមនៅខ្ពស់ជាងភ្នែកអ្នកមើល $2$ ម៉ែត្រ និងគែមលើនៅខ្ពស់ជាងភ្នែក $8$ ម៉ែត្រ ។ អ្នកមើលឈរនៅចម្ងាយ $x$ ម៉ែត្រពីជញ្ជាំង ។ បង្ហាញថា $\tan\theta=\frac{6x}{x^2+16}$ ដែល $\theta$ ជាមុំមើលបដា រួចរកចម្ងាយ $x$ ដែលមើលឃើញបដាក្រោមមុំធំបំផុត ។",
      "តាង $\\alpha$ និង $\\beta$ ជាមុំមើលគែមលើនិងគែមក្រោមធៀបនឹងផ្តេក ។ នោះ $\\tan\\alpha=\\frac{8}{x}$ និង $\\tan\\beta=\\frac{2}{x}$ ហើយ $\\theta=\\alpha-\\beta$ ។\n$$\\tan\\theta=\\frac{\\frac{8}{x}-\\frac{2}{x}}{1+\\frac{16}{x^2}}=\\frac{6x}{x^2+16}$$\nដោយ $0<\\theta<\\frac{\\pi}{2}$ មុំ $\\theta$ ធំបំផុតលុះត្រាតែ $g(x)=\\frac{6x}{x^2+16}$ ធំបំផុត ។\n$$g'(x)=\\frac{6(x^2+16)-12x^2}{(x^2+16)^2}=\\frac{6(16-x^2)}{(x^2+16)^2}$$\nចំពោះ $x>0$ គេបាន $g'(x)=0$ លុះត្រាតែ $x=4$ ។ ភាគបែងវិជ្ជមាន ដូច្នេះសញ្ញាប្តូរពី $+$ ទៅ $-$ ។\nដូចនេះ ត្រូវឈរនៅចម្ងាយ ៖\n$$\\boxed{x=4}$$\nម៉ែត្រ ដែល $\\tan\\theta=\\frac{3}{4}$ ។",
      "x=4", [C("diff(6*x/(x**2+16),x).subs(x,4)", "0"), C("(6*x/(x**2+16)).subs(x,4)", "3/4")])
    H("optimization_path", "bacii", r"ភូមិ $A$ និងភូមិ $B$ នៅខាងម្ខាងនៃទន្លេត្រង់មួយ ដោយមានចម្ងាយពីច្រាំង $3$ គីឡូម៉ែត្រ និង $5$ គីឡូម៉ែត្រ ។ ចំណោលកែងនៃភូមិទាំងពីរលើច្រាំងនៅឆ្ងាយគ្នា $8$ គីឡូម៉ែត្រ ។ គេចង់សង់ស្ថានីយបូមទឹកមួយនៅលើច្រាំង ហើយដាក់បំពង់ត្រង់ទៅភូមិទាំងពីរ ។ តើត្រូវសង់នៅត្រង់ណា ទើបប្រវែងបំពង់សរុបខ្លីបំផុត?",
      "តាង $x$ ជាចម្ងាយពីចំណោលកែងនៃ $A$ ទៅស្ថានីយ ($0\\le x\\le 8$) ។ តាមទ្រឹស្តីបទពីតាករ ប្រវែងបំពង់សរុបគឺ ៖\n$$f(x)=\\sqrt{x^2+9}+\\sqrt{(8-x)^2+25}$$\nដេរីវេ ៖\n$$f'(x)=\\frac{x}{\\sqrt{x^2+9}}-\\frac{8-x}{\\sqrt{(8-x)^2+25}}$$\n$f'(x)=0$ នាំឲ្យ $\\frac{x}{\\sqrt{x^2+9}}=\\frac{8-x}{\\sqrt{(8-x)^2+25}}$ ។ លើកការ៉េ រួចសម្រួល គេបាន $25x^2=9(8-x)^2$ ។\nដោយ $0\\le x\\le8$ នោះ $5x=3(8-x)$ នាំឲ្យ $x=3$ ។\nសញ្ញា ៖ $f'(0)<0$ និង $f'(8)>0$ ដូច្នេះ $x=3$ ជាចំណុចអប្បបរមា ។\n$$f(3)=\\sqrt{18}+\\sqrt{50}=8\\sqrt{2}$$\nដូចនេះ ស្ថានីយនៅចម្ងាយ $3$ គីឡូម៉ែត្រពីចំណោលកែងនៃ $A$ ហើយ ៖\n$$\\boxed{f_{\\min}=8\\sqrt{2}}$$",
      "x=3,\\ 8\\sqrt{2}", [C("diff(sqrt(x**2+9)+sqrt((8-x)**2+25),x).subs(x,3)", "0"), C("(sqrt(x**2+9)+sqrt((8-x)**2+25)).subs(x,3)", "8*sqrt(2)")])
    H("optimization_profit", "medium", r"អ្នកមីងខេងលក់ទឹកត្នោតនៅក្បែរប្រាសាទបាយ័ន ។ ថ្លៃដើមមួយកែវគឺ $4$ រយរៀល ។ បើលក់មួយកែវថ្លៃ $p$ រយរៀល គាត់លក់បាន $200-10p$ កែវក្នុងមួយថ្ងៃ ។ តើគួរលក់ថ្លៃប៉ុន្មាន?",
      "ប្រាក់ចំណេញក្នុងមួយកែវគឺ $p-4$ ដូច្នេះប្រាក់ចំណេញក្នុងមួយថ្ងៃ ៖\n$$B(p)=(p-4)(200-10p)$$\nដែល $4<p<20$ ដើម្បីឲ្យមានចំណេញ និងលក់បាន ។\nតាមដេរីវេនៃផលគុណ ៖\n$$B'(p)=(200-10p)-10(p-4)=240-20p$$\n$B'(p)=0$ នាំឲ្យ $p=12$ ។ ដោយ $B''(p)=-20<0$ នេះជាអតិបរមា ។\nពេលនោះគាត់លក់បាន $80$ កែវ ហើយ $B(12)=8\\cdot80=640$ រយរៀល ។\nដូចនេះ គួរលក់ ៖\n$$\\boxed{p=12}$$\nរយរៀលក្នុងមួយកែវ ។",
      "p=12", [C("diff((x-4)*(200-10*x),x).subs(x,12)", "0"), C("((x-4)*(200-10*x)).subs(x,12)", "640")])
    H("rate_of_change", "medium", r"កញ្ញា សុភា ទើបរៀនត្បាញសូត្រនៅតាកែវ ។ ក្រោយហាត់ $t$ សប្តាហ៍ នាងត្បាញបាន $N(t)=\frac{30t}{t+2}$ ម៉ែត្រក្នុងមួយខែ ។ តើជំនាញរបស់នាងកើនលឿនប៉ុន្មាននៅសប្តាហ៍ទី $2$? ហើយកម្រិតខ្ពស់បំផុតដែលនាងអាចខិតជិតគឺប៉ុន្មាន?",
      "ល្បឿនកើនជំនាញគឺដេរីវេ ៖\n$$N'(t)=\\frac{30(t+2)-30t}{(t+2)^2}=\\frac{60}{(t+2)^2}$$\nនៅ $t=2$ ៖ $N'(2)=\\frac{60}{16}=\\frac{15}{4}$ ម៉ែត្រក្នុងមួយខែក្នុងមួយសប្តាហ៍ ។\nដោយ $N'(t)>0$ ជានិច្ច នាងកាន់តែពូកែ ប៉ុន្តែ $N'(t)$ ថយ ពោលគឺកើនកាន់តែយឺត ។\n$$\\lim_{t\\to+\\infty}\\frac{30t}{t+2}=30$$\nដូចនេះ ៖\n$$\\boxed{N'(2)=\\frac{15}{4},\\quad \\lim_{t\\to+\\infty}N(t)=30}$$",
      "N'(2)=\\frac{15}{4}", [C("diff(30*x/(x+2),x).subs(x,2)", "15/4"), C("limit(30*x/(x+2),x,oo)", "30")])
    H("rate_of_change", "hard", r"នៅរដូវវស្សា កម្ពស់ទឹកទន្លេមេគង្គនៅកំពង់ចាមមួយឆមាស ត្រូវបានគំរូដោយ $h(t)=\frac{-t^3+9t^2}{10}+2$ ម៉ែត្រ ដែល $t$ ជាខែ ($0\le t\le 6$) ។ តើនៅខែណាដែលទឹកឡើងលឿនបំផុត? ល្បឿននោះស្មើប៉ុន្មាន?",
      "ល្បឿនឡើងទឹកគឺ ៖\n$$h'(t)=\\frac{-3t^2+18t}{10}$$\nយើងត្រូវរកអតិបរមានៃ $h'$ ដូច្នេះសិក្សាដេរីវេទី២ ៖\n$$h''(t)=\\frac{-6t+18}{10}$$\n$h''(t)=0$ នាំឲ្យ $t=3$ ។ ចំពោះ $t<3$ គេបាន $h''>0$ និងចំពោះ $t>3$ គេបាន $h''<0$ ។\nដូច្នេះ $h'$ មានអតិបរមាត្រង់ $t=3$ ហើយនេះជាចំណុចរបត់នៃខ្សែកោង $h$ ។\n$$h'(3)=\\frac{-27+54}{10}=\\frac{27}{10}$$\nដូចនេះ ទឹកឡើងលឿនបំផុតនៅខែទី $3$ ក្នុងល្បឿន ៖\n$$\\boxed{\\frac{27}{10}}$$\nម៉ែត្រក្នុងមួយខែ ។",
      "t=3,\\ \\frac{27}{10}", [C("diff((-x**3+9*x**2)/10+2,x,2).subs(x,3)", "0"), C("diff((-x**3+9*x**2)/10+2,x).subs(x,3)", "27/10")],
      lambda rid: [graph(rid, (-x**3 + 9 * x**2) / 10 + 2, 0, 6, 0, 14, "ក្រាបកម្ពស់ទឹកតាមខែ មានចំណុចរបត់ត្រង់ t ស្មើ 3", var="t", yname="h", pts=[(3, sp.Rational(38, 5))])])
    H("rate_of_change", "medium", r"ទន្លេសាបជាទន្លេដែលប្តូរទិសហូរតាមរដូវ ។ សន្មតថាល្បឿនលំហូរគឺ $Q(t)=12\sin\frac{\pi t}{6}$ (ពាន់ម៉ែត្រគូបក្នុងមួយវិនាទី) ដែល $t$ ជាខែ ហើយ $Q>0$ មានន័យថាហូរចូលបឹង ។ រកអត្រាបម្រែបម្រួលនៃ $Q$ នៅ $t=2$ ហើយកំណត់ខែដែលលំហូរខ្លាំងបំផុតក្នុងទិសចូលបឹង ក្នុងចន្លោះ $0\le t\le 12$ ។",
      "ដោយប្រើ $(\\sin u)'=u'\\cos u$ ៖\n$$Q'(t)=12\\cdot\\frac{\\pi}{6}\\cos\\frac{\\pi t}{6}=2\\pi\\cos\\frac{\\pi t}{6}$$\nនៅ $t=2$ ៖ $Q'(2)=2\\pi\\cos\\frac{\\pi}{3}=\\pi$ ។\n$Q'(t)=0$ លើ $[0;12]$ ឲ្យ $t=3$ ឬ $t=9$ ។ គេបាន $Q(3)=12$ និង $Q(9)=-12$ ។\nដូច្នេះលំហូរចូលបឹងខ្លាំងបំផុតនៅ $t=3$ ។\nដូចនេះ ៖\n$$\\boxed{Q'(2)=\\pi,\\quad t=3}$$",
      "Q'(2)=\\pi,\\ t=3", [C("diff(12*sin(pi*x/6),x).subs(x,2)", "pi"), C("diff(12*sin(pi*x/6),x).subs(x,3)", "0"), C("(12*sin(pi*x/6)).subs(x,3)", "12")])
    H("motion_vertical", "easy", r"ផ្លែដូងមួយជ្រុះពីចុងដើមកម្ពស់ $20$ ម៉ែត្រ ។ កម្ពស់នៅខណៈ $t$ វិនាទីគឺ $h(t)=20-5t^2$ ។ តើត្រូវប្រយ័ត្នប៉ុន្មានវិនាទីក្រោយជ្រុះ ទើបផ្លែដូងប៉ះដី? ហើយប៉ះដីក្នុងល្បឿនប៉ុន្មាន?",
      "ផ្លែដូងប៉ះដីពេល $h(t)=0$ ៖ $5t^2=20$ នាំឲ្យ $t=2$ (ព្រោះ $t\\ge0$) ។\nល្បឿនជាដេរីវេនៃកម្ពស់ ៖ $v(t)=h'(t)=-10t$ ។\nនៅ $t=2$ ៖ $v(2)=-20$ ម៉ែត្រក្នុងមួយវិនាទី ។ សញ្ញាដកមានន័យថាធ្លាក់ចុះ ។\nដូចនេះ ៖\n$$\\boxed{t=2,\\quad |v|=20}$$",
      "t=2,\\ |v|=20", [C("(20-5*x**2).subs(x,2)", "0"), C("diff(20-5*x**2,x).subs(x,2)", "-20")])
    H("optimization_distance", "hard", r"ទូកដឹកអ្នកដំណើរ $A$ នៅចម្ងាយ $12$ គីឡូម៉ែត្រខាងកើតកំពង់ផែ ហើយកំពុងបើកឆ្ពោះមកកំពង់ផែក្នុងល្បឿន $4$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ។ នៅពេលជាមួយគ្នា ទូក $B$ ចេញពីកំពង់ផែទៅទិសខាងជើងក្នុងល្បឿន $3$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ។ តើនៅពេលណាដែលទូកទាំងពីរនៅជិតគ្នាបំផុត? ចម្ងាយនោះស្មើប៉ុន្មាន?",
      "យកកំពង់ផែជាគល់ ។ ក្រោយ $t$ ម៉ោង $A$ នៅ $(12-4t;0)$ ហើយ $B$ នៅ $(0;3t)$ ។\nការ៉េនៃចម្ងាយ ៖\n$$D(t)=(12-4t)^2+9t^2=25t^2-96t+144$$\nគេបាន $D'(t)=50t-96$ ហើយ $D'(t)=0$ នាំឲ្យ $t=\\frac{48}{25}$ ។\nដោយ $D''(t)=50>0$ នេះជាអប្បបរមា ។\n$$D\\left(\\frac{48}{25}\\right)=\\frac{1296}{25}\\Rightarrow d=\\frac{36}{5}$$\nដូចនេះ ទូកនៅជិតគ្នាបំផុតក្រោយ $\\frac{48}{25}$ ម៉ោង ដោយមានចម្ងាយ ៖\n$$\\boxed{d=\\frac{36}{5}}$$\nគីឡូម៉ែត្រ ។",
      "t=\\frac{48}{25},\\ d=\\frac{36}{5}", [C("diff((12-4*x)**2+9*x**2,x).subs(x,48/25)", "0"), C("sqrt(((12-4*x)**2+9*x**2).subs(x,48/25))", "36/5")])
    H("optimization_trig", "bacii", r"ជាងសំណង់ត្រូវដឹកបំពង់ដែកមួយកាត់ជ្រុងកែងនៃផ្លូវតូចពីរ ដែលមានទទឹង $1$ ម៉ែត្រ និង $8$ ម៉ែត្រ ។ បំពង់ផ្តេកប៉ះជញ្ជាំងទាំងពីរនិងកាច់ជ្រុងខាងក្នុង ។ បើ $\theta$ ជាមុំរវាងបំពង់និងជញ្ជាំង បង្ហាញថាប្រវែងបំពង់គឺ $L(\theta)=\frac{1}{\sin\theta}+\frac{8}{\cos\theta}$ រួចរកប្រវែងអតិបរមានៃបំពង់ដែលអាចឆ្លងកាត់ជ្រុងបាន ។",
      "បំពង់ត្រូវបានចែកដោយកាច់ជ្រុងជាពីរកំណាត់ ។ កំណាត់ក្នុងផ្លូវទទឹង $1$ ម៉ែត្រមានប្រវែង $\\frac{1}{\\sin\\theta}$ ហើយកំណាត់ក្នុងផ្លូវទទឹង $8$ ម៉ែត្រមានប្រវែង $\\frac{8}{\\cos\\theta}$ ។\nបំពង់ឆ្លងផុតលុះត្រាតែប្រវែងរបស់វាមិនលើសតម្លៃអប្បបរមានៃ $L$ លើ $\\left(0;\\frac{\\pi}{2}\\right)$ ។\n$$L'(\\theta)=-\\frac{\\cos\\theta}{\\sin^2\\theta}+\\frac{8\\sin\\theta}{\\cos^2\\theta}$$\n$L'(\\theta)=0$ នាំឲ្យ $\\tan^3\\theta=\\frac{1}{8}$ ដូចនេះ $\\tan\\theta=\\frac{1}{2}$ ។\nពេលនោះ $\\sin\\theta=\\frac{1}{\\sqrt{5}}$ និង $\\cos\\theta=\\frac{2}{\\sqrt{5}}$ ។\nកាលណា $\\theta\\to0^+$ ឬ $\\theta\\to\\frac{\\pi}{2}^-$ គេបាន $L\\to+\\infty$ ដូច្នេះនេះជាអប្បបរមា ។\n$$L=\\sqrt{5}+4\\sqrt{5}=5\\sqrt{5}$$\nដូចនេះ បំពង់ត្រូវវែងមិនលើសពី ៖\n$$\\boxed{5\\sqrt{5}}$$\nម៉ែត្រ ។",
      "5\\sqrt{5}", [C("diff(1/sin(x)+8/cos(x),x).subs(x,atan(Rational(1,2)))", "0"), C("(1/sin(x)+8/cos(x)).subs(x,atan(Rational(1,2)))", "5*sqrt(5)")])
    H("related_rates_tank", "medium", r"នៅរោងម៉ាស៊ីនកិនស្រូវ អង្ករហូរចេញពីបំពង់ធ្លាក់លើដី ហើយគរជារាងកោណដែលកម្ពស់តែងស្មើនឹងកាំបាត ។ បើអង្ករហូរក្នុងល្បឿន $4\pi$ ម៉ែត្រគូបក្នុងមួយនាទី តើកំពូលគំនរឡើងលឿនប៉ុន្មាន នៅពេលគំនរខ្ពស់ $2$ ម៉ែត្រ?",
      "ដោយ $r=h$ មាឌគំនរគឺ $V=\\frac{1}{3}\\pi r^2h=\\frac{\\pi h^3}{3}$ ។\nធ្វើដេរីវេលើអង្គទាំងពីរធៀបនឹង $t$ ៖\n$$\\frac{dV}{dt}=\\pi h^2\\frac{dh}{dt}$$\nពេល $h=2$ ៖ $4\\pi=4\\pi\\frac{dh}{dt}$ ។\nដូចនេះ ៖\n$$\\boxed{\\frac{dh}{dt}=1}$$\nម៉ែត្រក្នុងមួយនាទី ។",
      "1", [C("4*pi/diff(pi*x**3/3,x).subs(x,2)", "1")], [fig(fig_cone("r", "h"), "គំនរអង្កររាងកោណ")])
    H("related_rates_tank", "hard", r"ស្នូកឲ្យចំណីជ្រូករបស់លោកតា សុខ មានប្រវែង $6$ ម៉ែត្រ ហើយមុខកាត់ជាត្រីកោណសមបាតបញ្ច្រាស ទទឹងមាត់ $2$ ម៉ែត្រ ជម្រៅ $1$ ម៉ែត្រ ។ គាត់ចាក់ទឹកចូលក្នុងល្បឿន $3$ ម៉ែត្រគូបក្នុងមួយនាទី ។ រកល្បឿនឡើងទឹក ពេលទឹកជម្រៅ $\frac{1}{2}$ ម៉ែត្រ ។",
      "ពេលជម្រៅទឹក $h$ ផ្ទៃទឹកមានទទឹង $w$ ។ ត្រីកោណដូចគ្នាឲ្យ $\\frac{w}{h}=\\frac{2}{1}$ នាំឲ្យ $w=2h$ ។\nមាឌទឹក ៖\n$$V=6\\cdot\\frac{wh}{2}=6h^2$$\nធ្វើដេរីវេ ៖ $\\frac{dV}{dt}=12h\\frac{dh}{dt}$ ។\nជំនួស $h=\\frac{1}{2}$ និង $\\frac{dV}{dt}=3$ ៖ $3=6\\frac{dh}{dt}$ ។\nដូចនេះ ៖\n$$\\boxed{\\frac{dh}{dt}=\\frac{1}{2}}$$\nម៉ែត្រក្នុងមួយនាទី ។",
      "\\frac{1}{2}", [C("3/diff(6*x**2,x).subs(x,1/2)", "1/2")])
    H("related_rates_distance", "medium", r"យន្តហោះមួយហោះផ្តេកនៅរយៈកម្ពស់ $3$ គីឡូម៉ែត្រ ក្នុងល្បឿន $600$ គីឡូម៉ែត្រក្នុងមួយម៉ោង ឆ្លងកាត់លើប៉មត្រួតពិនិត្យនៃអាកាសយានដ្ឋានតេជោ ។ ពេលវាហោះផុតប៉មបានចម្ងាយផ្តេក $4$ គីឡូម៉ែត្រ តើចម្ងាយរវាងយន្តហោះនិងប៉មកើនលឿនប៉ុន្មាន?",
      "តាង $x$ ជាចម្ងាយផ្តេក និង $d$ ជាចម្ងាយពីប៉មទៅយន្តហោះ ។ នោះ $d^2=x^2+9$ ។\nធ្វើដេរីវេធៀបនឹង $t$ ៖ $2d\\frac{dd}{dt}=2x\\frac{dx}{dt}$ ។\nពេល $x=4$ គេបាន $d=5$ ។\n$$\\frac{dd}{dt}=\\frac{4}{5}\\cdot600=480$$\nដូចនេះ ៖\n$$\\boxed{\\frac{dd}{dt}=480}$$\nគីឡូម៉ែត្រក្នុងមួយម៉ោង ។",
      "480", [C("diff(sqrt(x**2+9),x).subs(x,4)*600", "480")], [fig(fig_tri("x", "3", "d"), "យន្តហោះ ប៉ម និងចម្ងាយ")])
    H("related_rates_distance", "hard", r"ប៉េងប៉ោងមួយហោះឡើងបញ្ឈរពីវាលព្រះមេរុក្នុងល្បឿន $5$ ម៉ែត្រក្នុងមួយវិនាទី ។ សុវណ្ណឈរមើលនៅចម្ងាយ $100$ ម៉ែត្រពីចំណុចចេញ ។ រកល្បឿនកើនមុំមើល $\theta$ (រ៉ាដ្យង់ក្នុងមួយវិនាទី) ពេលប៉េងប៉ោងនៅកម្ពស់ $100$ ម៉ែត្រ ។",
      "តាង $h$ ជាកម្ពស់ប៉េងប៉ោង ។ គេមាន $\\tan\\theta=\\frac{h}{100}$ ។\nធ្វើដេរីវេធៀបនឹង $t$ ៖\n$$(1+\\tan^2\\theta)\\frac{d\\theta}{dt}=\\frac{1}{100}\\cdot\\frac{dh}{dt}$$\nពេល $h=100$ គេបាន $\\tan\\theta=1$ ។ ដូច្នេះ $2\\frac{d\\theta}{dt}=\\frac{5}{100}$ ។\nដូចនេះ ៖\n$$\\boxed{\\frac{d\\theta}{dt}=\\frac{1}{40}}$$\nរ៉ាដ្យង់ក្នុងមួយវិនាទី ។",
      "\\frac{1}{40}", [C("diff(atan(x/100),x).subs(x,100)*5", "1/40")])
    H("rate_of_change", "medium", r"ថ្មទូរស័ព្ទរបស់រតនាសាកទៅតាមរូបមន្ត $B(t)=100\left(1-e^{-\frac{t}{30}}\right)$ ភាគរយ ក្រោយ $t$ នាទី ។ តើពេលចាប់ផ្តើមសាក ថ្មឡើងលឿនប៉ុន្មាន? ហេតុអ្វីបានជាការសាកយឺតទៅៗ?",
      "ល្បឿនសាកគឺ ៖\n$$B'(t)=\\frac{100}{30}e^{-\\frac{t}{30}}=\\frac{10}{3}e^{-\\frac{t}{30}}$$\nនៅ $t=0$ ៖ $B'(0)=\\frac{10}{3}$ ភាគរយក្នុងមួយនាទី ។\nដោយអនុគមន៍ $e^{-\\frac{t}{30}}$ ចុះ នោះ $B'(t)$ ថយ ពោលគឺថ្មឡើងយឺតទៅៗ ហើយ $\\lim_{t\\to+\\infty}B(t)=100$ ។\nដូចនេះ ៖\n$$\\boxed{B'(0)=\\frac{10}{3}}$$",
      "B'(0)=\\frac{10}{3}", [C("diff(100*(1-exp(-x/30)),x).subs(x,0)", "10/3"), C("limit(100*(1-exp(-x/30)),x,oo)", "100")])
    H("rate_of_change", "bacii", r"ព័ត៌មានមួយរាលដាលក្នុងសាកលវិទ្យាល័យមួយតាមអនុគមន៍ $N(t)=\frac{1000}{1+9e^{-t}}$ (នាក់) ក្រោយ $t$ ថ្ងៃ ។\nក. គណនា $N(0)$ និង $\lim_{t\to+\infty}N(t)$ ។\nខ. គណនា $N'(t)$ ។\nគ. បង្ហាញថាល្បឿនរាលដាលលឿនបំផុតនៅពេល $N=500$ ។",
      "ក. $N(0)=\\frac{1000}{10}=100$ ។ ដោយ $\\lim_{t\\to+\\infty}e^{-t}=0$ នោះ $\\lim_{t\\to+\\infty}N(t)=1000$ ។\nខ. តាមរូបមន្ត $\\left(\\frac{1}{u}\\right)'=-\\frac{u'}{u^2}$ ៖\n$$N'(t)=\\frac{9000e^{-t}}{(1+9e^{-t})^2}$$\nគ. តាង $u=9e^{-t}$ ដែល $u>0$ ។ គេបាន $N'=\\frac{1000u}{(1+u)^2}$ ។\nអនុគមន៍ $g(u)=\\frac{u}{(1+u)^2}$ មាន $g'(u)=\\frac{1-u}{(1+u)^3}$ ដូច្នេះអតិបរមាត្រង់ $u=1$ ។\n$u=1$ ឲ្យ $e^{t}=9$ ពោលគឺ $t=\\ln9$ ហើយ $N(\\ln9)=\\frac{1000}{2}=500$ ។\nល្បឿននៅខណៈនោះគឺ $N'(\\ln 9)=250$ នាក់ក្នុងមួយថ្ងៃ ។\nដូចនេះ ៖\n$$\\boxed{t=\\ln9,\\quad N=500,\\quad N'=250}$$",
      "t=\\ln 9", [C("(1000/(1+9*exp(-x))).subs(x,0)", "100"), C("limit(1000/(1+9*exp(-x)),x,oo)", "1000"), C("diff(1000/(1+9*exp(-x)),x)", "9000*exp(-x)/(1+9*exp(-x))**2"), C("diff(1000/(1+9*exp(-x)),x,2).subs(x,log(9))", "0"), C("(1000/(1+9*exp(-x))).subs(x,log(9))", "500"), C("diff(1000/(1+9*exp(-x)),x).subs(x,log(9))", "250")],
      lambda rid: [graph(rid, 1000 / (1 + 9 * sp.exp(-x)), 0, 8, 0, 1100, "ខ្សែកោងរាងអក្សរអេស មានចំណុចរបត់", var="t", yname="N", pts=[(sp.log(9), 500)])])
    H("lhopital_infinity", "hard", r"ធនាគារមួយផ្តល់ការប្រាក់ $10\%$ ក្នុងមួយឆ្នាំ ហើយបែងចែកគិតការប្រាក់ $n$ ដងក្នុងមួយឆ្នាំ ។ ប្រាក់ $1$ ដុល្លារក្លាយជា $\left(1+\frac{1}{10n}\right)^n$ ដុល្លារ ។ ដោយគណនា $\lim_{x\to+\infty}x\ln\left(1+\frac{1}{10x}\right)$ រកតម្លៃដែលប្រាក់នេះខិតជិតកាលណា $n$ ធំឡើង ។",
      "តាង $u=\\frac{1}{x}$ ។ កាលណា $x\\to+\\infty$ នោះ $u\\to0^+$ ៖\n$$\\lim_{x\\to+\\infty}x\\ln\\left(1+\\frac{1}{10x}\\right)=\\lim_{u\\to0^+}\\frac{\\ln\\left(1+\\frac{u}{10}\\right)}{u}$$\nនេះជារាង $\\frac{0}{0}$ ។ តាមវិធានឡូពីតាល់ ៖\n$$\\lim_{u\\to0^+}\\frac{\\frac{1}{10}}{1+\\frac{u}{10}}=\\frac{1}{10}$$\nដោយ $\\left(1+\\frac{1}{10n}\\right)^n=e^{n\\ln\\left(1+\\frac{1}{10n}\\right)}$ និងអនុគមន៍ $e^x$ ជាប់ ។\nដូចនេះ ប្រាក់ខិតជិត ៖\n$$\\boxed{e^{\\frac{1}{10}}}$$\nដុល្លារ ។",
      "e^{\\frac{1}{10}}", [C("limit(x*log(1+1/(10*x)),x,oo)", "1/10")])
    H("limit_as_derivative", "easy", r"រថភ្លើងពីភ្នំពេញទៅកំពតមានទីតាំង $s(t)=5t^2$ ម៉ែត្រ ពេលចាប់ផ្តើមចេញ ។ គណនា $\lim_{h\to0}\frac{s(2+h)-s(2)}{h}$ រួចបកស្រាយលទ្ធផល ។",
      "គេគណនាភាគយក ៖\n$$s(2+h)-s(2)=5(4+4h+h^2)-20=20h+5h^2$$\nចែកនឹង $h\\ne0$ ៖ $\\frac{s(2+h)-s(2)}{h}=20+5h$ ។\nកាលណា $h\\to0$ លីមីតស្មើ $20$ ។\nលីមីតនេះជាដេរីវេ $s'(2)$ គឺល្បឿនខណៈនៅ $t=2$ ។\nដូចនេះ ៖\n$$\\boxed{s'(2)=20}$$\nម៉ែត្រក្នុងមួយវិនាទី ។",
      "20", [C("limit((5*(2+x)**2-20)/x,x,0)", "20")])
    H("differentials", "easy", r"ស្រះទឹករាងរង្វង់នៅវត្តមួយមានកាំ $10$ ម៉ែត្រ ។ ព្រះសង្ឃចង់ពង្រីកកាំបន្ថែម $0.2$ ម៉ែត្រ ។ ប៉ាន់ស្មានក្រឡាផ្ទៃដែលកើនឡើង ដោយប្រើឌីផេរ៉ង់ស្យែល ហើយប្រៀបធៀបនឹងតម្លៃពិត ។",
      "ក្រឡាផ្ទៃរង្វង់ $S(r)=\\pi r^2$ ដូច្នេះ $dS=2\\pi r\\,dr$ ។\nចំពោះ $r=10$ និង $dr=\\frac{1}{5}$ ៖ $dS=2\\pi\\cdot10\\cdot\\frac{1}{5}=4\\pi$ ។\nកំណើនពិត ៖\n$$\\Delta S=\\pi\\left(\\frac{51}{5}\\right)^2-100\\pi=\\frac{101\\pi}{25}$$\nតម្លៃទាំងពីរខុសគ្នាត្រឹម $\\frac{\\pi}{25}$ ។\nដូចនេះ ៖\n$$\\boxed{dS=4\\pi}$$\nម៉ែត្រការ៉េ ។",
      "4\\pi", [C("diff(pi*x**2,x).subs(x,10)/5", "4*pi"), C("(pi*x**2).subs(x,Rational(51,5))-(pi*x**2).subs(x,10)", "101*pi/25")])
    H("differentials", "medium", r"រយៈពេលយោលនៃប៉ោលនាឡិកាជញ្ជាំងនៅសាលាមួយគឺប្រហែល $T(L)=2\sqrt{L}$ វិនាទី ដែល $L$ ជាប្រវែងគិតជាម៉ែត្រ ។ ក្នុងរដូវក្តៅ ប៉ោលពីប្រវែង $1$ ម៉ែត្រ រីកដល់ $1.02$ ម៉ែត្រ ។ ប៉ាន់ស្មានបម្រែបម្រួលនៃ $T$ ។",
      "គេមាន $T'(L)=\\frac{1}{\\sqrt{L}}$ ដូច្នេះ $dT=\\frac{dL}{\\sqrt{L}}$ ។\nជំនួស $L=1$ និង $dL=\\frac{1}{50}$ ៖\n$$dT=\\frac{1}{50}=0.02$$\nនាឡិកាយឺតបន្តិច ព្រោះរយៈពេលយោលវែងជាងមុន ។\nដូចនេះ ៖\n$$\\boxed{dT\\approx0.02}$$\nវិនាទី ។",
      "0.02", [C("diff(2*sqrt(x),x).subs(x,1)/50", "1/50")])
    H("linear_approximation", "medium", r"វណ្ណាដាក់ប្រាក់ក្នុងគណនីសន្សំដែលមានការប្រាក់ $1\%$ ក្នុងមួយខែ ។ ក្រោយ $12$ ខែ ប្រាក់ $1$ ដុល្លារក្លាយជា $(1.01)^{12}$ ដុល្លារ ។ ដោយប្រើតម្លៃប្រហែលនៃ $f(x)=(1+x)^{12}$ ក្បែរ $x=0$ ប៉ាន់ស្មានចំនួននេះ ។",
      "គេមាន $f(0)=1$ និង $f'(x)=12(1+x)^{11}$ ដូច្នេះ $f'(0)=12$ ។\nចំពោះ $x$ តូច ៖ $f(x)\\approx1+12x$ ។\nជំនួស $x=\\frac{1}{100}$ ៖\n$$(1.01)^{12}\\approx1+\\frac{12}{100}=\\frac{28}{25}=1.12$$\nតម្លៃពិតធំជាងនេះបន្តិច ព្រោះរូបមន្តនេះមិនគិតការប្រាក់លើការប្រាក់ ។\nដូចនេះ ៖\n$$\\boxed{(1.01)^{12}\\approx1.12}$$",
      "1.12", [C("((1+x)**12).subs(x,0)+diff((1+x)**12,x).subs(x,0)/100", "28/25")])
    H("rolle_theorem", "easy", r"បូរ៉ាគប់បាល់ឡើងលើ ហើយចាប់វិញនៅកម្ពស់ដដែលក្រោយ $3$ វិនាទី ដោយ $h(t)=15t-5t^2$ ។ ដោយប្រើទ្រឹស្តីបទរ៉ូល បង្ហាញថាមានខណៈមួយដែលល្បឿនស្មើសូន្យ រួចរកខណៈនោះ ។",
      "$h$ ជាពហុធា ដូច្នេះជាប់និងមានដេរីវេលើ $[0;3]$ ។\nគេបាន $h(0)=0$ និង $h(3)=45-45=0$ ។\nតាមទ្រឹស្តីបទរ៉ូល មាន $c\\in(0;3)$ ដែល $h'(c)=0$ ។\nដោយ $h'(t)=15-10t$ នោះ $c=\\frac{3}{2}$ ។\nដូចនេះ បាល់ឈប់មួយភ្លែតនៅកំពូល ត្រង់ ៖\n$$\\boxed{t=\\frac{3}{2}}$$\nវិនាទី ។",
      "t=\\frac{3}{2}", [C("(15*x-5*x**2).subs(x,3)", "0"), C("diff(15*x-5*x**2,x).subs(x,3/2)", "0")])
    H("rolle_theorem", "hard", r"អ្នករត់ប្រណាំងពីរនាក់ចេញដំណើរព្រមគ្នា ហើយដល់ទីក្នុងពេលដូចគ្នានៅ $t=10$ វិនាទី ។ ទីតាំងរបស់គេគឺ $s_1(t)=\frac{t^2}{2}+5t$ និង $s_2(t)=10t$ ។ ស្រាយបញ្ជាក់ថាមានខណៈមួយដែលគេមានល្បឿនស្មើគ្នា ។ រកខណៈនោះ ។",
      "តាង $g(t)=s_1(t)-s_2(t)=\\frac{t^2}{2}-5t$ ។ $g$ ជាប់និងមានដេរីវេលើ $[0;10]$ ។\nគេបាន $g(0)=0$ និង $g(10)=50-50=0$ ។\nតាមទ្រឹស្តីបទរ៉ូល មាន $c\\in(0;10)$ ដែល $g'(c)=0$ ពោលគឺ $s_1'(c)=s_2'(c)$ ។\n$g'(t)=t-5$ ដូច្នេះ $c=5$ ។\nផ្ទៀងផ្ទាត់ ៖ $s_1'(5)=10$ និង $s_2'(5)=10$ ។\nដូចនេះ ៖\n$$\\boxed{t=5}$$\nវិនាទី ។",
      "t=5", [C("(x**2/2+5*x-10*x).subs(x,10)", "0"), C("diff(x**2/2+5*x,x).subs(x,5)", "10"), C("diff(10*x,x).subs(x,5)", "10")])
    H("mean_value_theorem", "hard", r"អនុគមន៍ $f$ ជាប់លើ $[1;4]$ មានដេរីវេលើ $(1;4)$ ដោយ $f(1)=2$ និង $f'(x)\le3$ គ្រប់ $x$ ។ តើ $f(4)$ អាចមានតម្លៃធំបំផុតប៉ុន្មាន? ផ្តល់ឧទាហរណ៍នៃអនុគមន៍ដែលដល់តម្លៃនោះ ។",
      "តាមទ្រឹស្តីបទតម្លៃមធ្យម មាន $c\\in(1;4)$ ដែល ៖\n$$f(4)-f(1)=3f'(c)\\le9$$\nដូច្នេះ $f(4)\\le2+9=11$ ។\nឧទាហរណ៍ $f(x)=3x-1$ មាន $f(1)=2$ និង $f'(x)=3$ ហើយ $f(4)=11$ ។\nដូចនេះ ៖\n$$\\boxed{f(4)_{\\max}=11}$$",
      "11", [C("(3*x-1).subs(x,1)", "2"), C("(3*x-1).subs(x,4)", "11"), C("diff(3*x-1,x)", "3")])
    H("mvt_inequality", "medium", r"ស្រាយបញ្ជាក់ថា ចំពោះគ្រប់ចំនួនពិត $x$ គេមាន $e^x\ge1+x$ ដោយសិក្សាអថេរភាពនៃអនុគមន៍ $g(x)=e^x-1-x$ ។",
      "ដេរីវេ $g'(x)=e^x-1$ ។ $g'(x)=0$ លុះត្រាតែ $x=0$ ។\nបើ $x<0$ នោះ $g'(x)<0$ ហើយបើ $x>0$ នោះ $g'(x)>0$ ។\n$$\\begin{array}{c|ccccc}x & -\\infty & & 0 & & +\\infty \\\\\\hline g'(x) & & - & 0 & + & \\\\\\hline g(x) & +\\infty & \\searrow & 0 & \\nearrow & +\\infty\\end{array}$$\nអនុគមន៍ $g$ មានអប្បបរមាស្មើ $g(0)=0$ ដូច្នេះ $g(x)\\ge0$ ។\nដូចនេះ ៖\n$$\\boxed{e^x\\ge1+x}$$",
      "e^x\\ge 1+x", [C("diff(exp(x)-1-x,x).subs(x,0)", "0"), C("(exp(x)-1-x).subs(x,0)", "0")],
      [vdiag(vt("x", "g", ["-\\infty", "0", "+\\infty"], ["", "-", "0", "+", ""], ["+\\infty", "\\searrow", "0", "\\nearrow", "+\\infty"]), "តារាងអថេរភាពនៃ g មានអប្បបរមា 0")])
    H("mvt_inequality", "medium", r"ប្រើដេរីវេដើម្បីបង្ហាញថា $\ln x\le x-1$ ចំពោះគ្រប់ $x>0$ ។ តើសមភាពកើតឡើងនៅពេលណា?",
      "តាង $g(x)=x-1-\\ln x$ លើ $(0;+\\infty)$ ។\n$$g'(x)=1-\\frac{1}{x}=\\frac{x-1}{x}$$\nដោយ $x>0$ សញ្ញានៃ $g'$ យកតាម $x-1$ ។ $g$ ចុះលើ $(0;1)$ និងកើនលើ $(1;+\\infty)$ ។\nដូច្នេះ $g$ មានអប្បបរមាត្រង់ $x=1$ ស្មើ $g(1)=0$ ។\nដូចនេះ $g(x)\\ge0$ នាំឲ្យ ៖\n$$\\boxed{\\ln x\\le x-1}$$\nហើយសមភាពកើតឡើងត្រង់ $x=1$ តែមួយគត់ ។",
      "\\ln x\\le x-1", [C("diff(x-1-log(x),x).subs(x,1)", "0"), C("(x-1-log(x)).subs(x,1)", "0")])
    H("optimization_numbers", "medium", r"ផ្ទះបីខ្នងស្ថិតនៅតាមផ្លូវត្រង់មួយ ត្រង់ចំណុចអាប់ស៊ីស $2$, $5$ និង $11$ (គីឡូម៉ែត្រ) ។ មេភូមិចង់ជីកអណ្តូងនៅចំណុច $x$ លើផ្លូវ ដើម្បីឲ្យផលបូកការ៉េនៃចម្ងាយពីអណ្តូងទៅផ្ទះនីមួយៗតូចបំផុត ។ រក $x$ ។",
      "តាង ៖\n$$S(x)=(x-2)^2+(x-5)^2+(x-11)^2$$\nដេរីវេ ៖ $S'(x)=2(x-2)+2(x-5)+2(x-11)=6x-36$ ។\n$S'(x)=0$ នាំឲ្យ $x=6$ ដែលជាមធ្យមនៃអាប់ស៊ីសទាំងបី ។\n$S''(x)=6>0$ ដូច្នេះជាអប្បបរមា ហើយ $S(6)=16+1+25=42$ ។\nដូចនេះ ៖\n$$\\boxed{x=6}$$",
      "x=6", [C("diff((x-2)**2+(x-5)**2+(x-11)**2,x).subs(x,6)", "0"), C("((x-2)**2+(x-5)**2+(x-11)**2).subs(x,6)", "42")])
    H("optimization_geometry", "bacii", r"បង្អួចវិហារមួយមានរាងចតុកោណកែងពាក់ពីលើដោយពាក់កណ្តាលរង្វង់កាំ $r$ ។ បរិមាត្រសរុបនៃបង្អួចស្មើ $8$ ម៉ែត្រ ។ រក $r$ ដើម្បីឲ្យបង្អួចឲ្យពន្លឺចូលច្រើនបំផុត ។",
      "តាង $h$ ជាកម្ពស់ផ្នែកចតុកោណកែង ។ បាតវែង $2r$ ដូច្នេះបរិមាត្រ ៖\n$$2r+2h+\\pi r=8\\Rightarrow 2h=8-2r-\\pi r$$\nក្រឡាផ្ទៃបង្អួច ៖\n$$S(r)=2rh+\\frac{\\pi r^2}{2}=8r-2r^2-\\frac{\\pi r^2}{2}$$\nដេរីវេ ៖ $S'(r)=8-(4+\\pi)r$ ។\n$S'(r)=0$ នាំឲ្យ $r=\\frac{8}{4+\\pi}$ ។ ដោយ $S''(r)=-(4+\\pi)<0$ នេះជាអតិបរមា ។\nក្រឡាផ្ទៃអតិបរមា $S=4r=\\frac{32}{4+\\pi}$ ។\nដូចនេះ ៖\n$$\\boxed{r=\\frac{8}{4+\\pi}}$$\nម៉ែត្រ ។".replace("វិហារ", "វត្ត"),
      "r=\\frac{8}{4+\\pi}", [C("diff(8*x-2*x**2-pi*x**2/2,x).subs(x,8/(4+pi))", "0"), C("(8*x-2*x**2-pi*x**2/2).subs(x,8/(4+pi))", "32/(4+pi)")])
    H("optimization_geometry", "hard", r"ខ្សែលួសប្រវែង $100$ សង់ទីម៉ែត្រត្រូវកាត់ជាពីរ ។ កំណាត់ប្រវែង $x$ ពត់ជាការ៉េ ហើយកំណាត់ទីពីរពត់ជារង្វង់ ។ រក $x$ ដើម្បីឲ្យផលបូកក្រឡាផ្ទៃតូចបំផុត ។",
      "ការ៉េមានជ្រុង $\\frac{x}{4}$ ហើយរង្វង់មានកាំ $\\frac{100-x}{2\\pi}$ ដែល $0<x<100$ ។\n$$S(x)=\\frac{x^2}{16}+\\frac{(100-x)^2}{4\\pi}$$\nដេរីវេ ៖\n$$S'(x)=\\frac{x}{8}-\\frac{100-x}{2\\pi}$$\n$S'(x)=0$ នាំឲ្យ $\\pi x=4(100-x)$ ពោលគឺ $x=\\frac{400}{4+\\pi}$ ។\n$S''(x)=\\frac{1}{8}+\\frac{1}{2\\pi}>0$ ដូច្នេះជាអប្បបរមា ។\nដូចនេះ ៖\n$$\\boxed{x=\\frac{400}{4+\\pi}}$$\nសង់ទីម៉ែត្រ ។",
      "x=\\frac{400}{4+\\pi}", [C("diff(x**2/16+(100-x)**2/(4*pi),x).subs(x,400/(4+pi))", "0")])
    H("optimization_geometry", "hard", r"គេឆ្លាក់ស៊ីឡាំងមួយពីដុំថ្មរាងស្វ៊ែកាំ $3$ ដេស៊ីម៉ែត្រ ។ បើ $h$ ជាកម្ពស់ស៊ីឡាំង រក $h$ ដើម្បីឲ្យមាឌស៊ីឡាំងធំបំផុត ហើយគណនាមាឌនោះ ។",
      "កាំស៊ីឡាំង $r$ ផ្ទៀងផ្ទាត់ $r^2+\\frac{h^2}{4}=9$ តាមទ្រឹស្តីបទពីតាករ ដែល $0<h<6$ ។\n$$V(h)=\\pi r^2h=\\pi\\left(9h-\\frac{h^3}{4}\\right)$$\nដេរីវេ ៖ $V'(h)=\\pi\\left(9-\\frac{3h^2}{4}\\right)$ ។\n$V'(h)=0$ នាំឲ្យ $h^2=12$ ដូចនេះ $h=2\\sqrt{3}$ ។\n$V'$ ប្តូរសញ្ញាពី $+$ ទៅ $-$ ដូច្នេះជាអតិបរមា ។\n$$V(2\\sqrt{3})=\\pi\\cdot2\\sqrt{3}\\cdot(9-3)=12\\sqrt{3}\\pi$$\nដូចនេះ ៖\n$$\\boxed{h=2\\sqrt{3},\\quad V_{\\max}=12\\sqrt{3}\\pi}$$",
      "h=2\\sqrt{3}", [C("diff(pi*(9*x-x**3/4),x).subs(x,2*sqrt(3))", "0"), C("(pi*(9*x-x**3/4)).subs(x,2*sqrt(3))", "12*sqrt(3)*pi")])
    H("optimization_geometry", "bacii", r"បន្ទាត់មួយកាត់តាមចំណុច $A(2;3)$ កាត់អ័ក្ស $x'ox$ ត្រង់ $P(a;0)$ និង $y'oy$ ត្រង់ $Q(0;b)$ ដែល $a>2$ និង $b>3$ ។ បង្ហាញថា $b=\frac{3a}{a-2}$ រួចរកតម្លៃ $a$ ដែលធ្វើឲ្យក្រឡាផ្ទៃត្រីកោណ $OPQ$ តូចបំផុត ។",
      "សមីការបន្ទាត់គឺ $\\frac{x}{a}+\\frac{y}{b}=1$ ។ ដោយ $A$ នៅលើបន្ទាត់ ៖ $\\frac{2}{a}+\\frac{3}{b}=1$ នាំឲ្យ $b=\\frac{3a}{a-2}$ ។\nក្រឡាផ្ទៃ ៖\n$$S(a)=\\frac{ab}{2}=\\frac{3a^2}{2(a-2)}$$\nតាមរូបមន្តដេរីវេនៃផលចែក ៖\n$$S'(a)=\\frac{3}{2}\\cdot\\frac{2a(a-2)-a^2}{(a-2)^2}=\\frac{3a(a-4)}{2(a-2)^2}$$\nចំពោះ $a>2$ គេបាន $S'(a)=0$ លុះត្រាតែ $a=4$ ។ $S'<0$ លើ $(2;4)$ និង $S'>0$ លើ $(4;+\\infty)$ ។\nពេលនោះ $b=6$ និង $S(4)=12$ ។\nដូចនេះ ៖\n$$\\boxed{a=4,\\quad S_{\\min}=12}$$",
      "a=4,\\ S_{\\min}=12", [C("diff(3*x**2/(2*(x-2)),x).subs(x,4)", "0"), C("(3*x**2/(2*(x-2))).subs(x,4)", "12"), C("(3*x/(x-2)).subs(x,4)", "6")])
    H("motion_polynomial", "medium", r"ជណ្តើរយន្តក្នុងអគារខ្ពស់មួយនៅភ្នំពេញឡើងពីជាន់ផ្ទាល់ដី តាមទីតាំង $s(t)=3t^2-\frac{t^3}{5}$ ម៉ែត្រ ដែល $0\le t\le10$ ។\nក. តើជណ្តើរយន្តឈប់នៅពេលណា ហើយនៅកម្ពស់ប៉ុន្មាន?\nខ. តើវាមានល្បឿនធំបំផុតនៅពេលណា?",
      "ក. ល្បឿន ៖ $v(t)=s'(t)=6t-\\frac{3t^2}{5}=\\frac{3t(10-t)}{5}$ ។\n$v(t)=0$ ចំពោះ $t=0$ ឬ $t=10$ ។ វាឈប់នៅ $t=10$ ដោយ $s(10)=300-200=100$ ម៉ែត្រ ។\nខ. សំទុះ ៖ $a(t)=v'(t)=6-\\frac{6t}{5}$ ។\n$a(t)=0$ នាំឲ្យ $t=5$ ។ សំទុះប្តូរពីវិជ្ជមានទៅអវិជ្ជមាន ដូច្នេះ $v$ មានអតិបរមា $v(5)=15$ ម៉ែត្រក្នុងមួយវិនាទី ។\nដូចនេះ ៖\n$$\\boxed{s(10)=100,\\quad t=5,\\quad v_{\\max}=15}$$",
      "s(10)=100,\\ v_{\\max}=15", [C("diff(3*x**2-x**3/5,x).subs(x,10)", "0"), C("(3*x**2-x**3/5).subs(x,10)", "100"), C("diff(3*x**2-x**3/5,x,2).subs(x,5)", "0"), C("diff(3*x**2-x**3/5,x).subs(x,5)", "15")],
      lambda rid: [graph(rid, 3 * x**2 - x**3 / 5, 0, 10, 0, 110, "ក្រាបកម្ពស់ជណ្តើរយន្តតាមពេល", var="t", yname="s", pts=[(5, 50), (10, 100)])])
    H("related_rates_tank", "medium", r"បឹងទំនប់វារីអគ្គិសនីកំចាយមានមាឌ $V(h)=2h^2+h$ (លានម៉ែត្រគូប) នៅពេលទឹកជម្រៅ $h$ ម៉ែត្រ ។ ក្នុងរដូវវស្សា ទឹកហូរចូល $10$ លានម៉ែត្រគូបក្នុងមួយថ្ងៃ ។ តើទឹកឡើងលឿនប៉ុន្មាន ពេល $h=6$ ម៉ែត្រ?",
      "ធ្វើដេរីវេ $V$ ធៀបនឹង $t$ តាមរូបមន្តអនុគមន៍បណ្ដាក់ ៖\n$$\\frac{dV}{dt}=(4h+1)\\frac{dh}{dt}$$\nចំពោះ $h=6$ ៖ $10=25\\frac{dh}{dt}$ ។\nដូចនេះ ៖\n$$\\boxed{\\frac{dh}{dt}=\\frac{2}{5}}$$\nម៉ែត្រក្នុងមួយថ្ងៃ ។",
      "\\frac{2}{5}", [C("10/diff(2*x**2+x,x).subs(x,6)", "2/5")])
    H("optimization_distance", "bacii", r"អំពូលពីរនៅចម្ងាយ $6$ ម៉ែត្រពីគ្នា ។ អំពូលទី១ខ្លាំងជាងអំពូលទី២ $8$ ដង ។ ពន្លឺនៅចំណុចចម្ងាយ $x$ ពីអំពូលទី១គឺ $I(x)=\frac{8}{x^2}+\frac{1}{(6-x)^2}$ ដែល $0<x<6$ ។ រកចំណុចដែលភ្លឺតិចបំផុត ។",
      "ដេរីវេ ៖\n$$I'(x)=-\\frac{16}{x^3}+\\frac{2}{(6-x)^3}$$\n$I'(x)=0$ នាំឲ្យ $\\frac{(6-x)^3}{x^3}=\\frac{1}{8}$ ពោលគឺ $\\frac{6-x}{x}=\\frac{1}{2}$ ដូច្នេះ $x=4$ ។\nកាលណា $x\\to0^+$ ឬ $x\\to6^-$ គេបាន $I\\to+\\infty$ ដូច្នេះ $x=4$ ជាអប្បបរមា ។\n$$I(4)=\\frac{1}{2}+\\frac{1}{4}=\\frac{3}{4}$$\nដូចនេះ ចំណុចងងឹតបំផុតនៅ ៖\n$$\\boxed{x=4}$$\nម៉ែត្រពីអំពូលទី១ ។",
      "x=4", [C("diff(8/x**2+1/(6-x)**2,x).subs(x,4)", "0"), C("(8/x**2+1/(6-x)**2).subs(x,4)", "3/4")])
    H("optimization_cost", "hard", r"ហាងអង្ករមួយនៅផ្សារដើមថ្កូវលក់អង្ករ $1200$ បាវក្នុងមួយឆ្នាំ ។ រាល់ការបញ្ជាទិញម្តងចំណាយ $50$ ដុល្លារ ហើយការរក្សាទុកចំណាយ $3$ ដុល្លារក្នុងមួយបាវក្នុងមួយឆ្នាំ ។ បើបញ្ជាទិញម្តង $x$ បាវ ស្តុកមធ្យមគឺ $\frac{x}{2}$ បាវ ។ រកទំហំបញ្ជាទិញដែលសន្សំបំផុត ។",
      "ចំនួនដងបញ្ជាទិញក្នុងមួយឆ្នាំគឺ $\\frac{1200}{x}$ ។ ចំណាយសរុបក្នុងមួយឆ្នាំ ៖\n$$C(x)=50\\cdot\\frac{1200}{x}+3\\cdot\\frac{x}{2}=\\frac{60000}{x}+\\frac{3x}{2}$$\nចំពោះ $x>0$ ៖\n$$C'(x)=-\\frac{60000}{x^2}+\\frac{3}{2}$$\n$C'(x)=0$ នាំឲ្យ $x^2=40000$ ដូចនេះ $x=200$ ។\n$C''(x)=\\frac{120000}{x^3}>0$ ដូច្នេះជាអប្បបរមា ហើយ $C(200)=600$ ។\nដូចនេះ ត្រូវបញ្ជាទិញម្តងៗ ៖\n$$\\boxed{x=200}$$\nបាវ ដែលត្រូវបញ្ជាទិញ $6$ ដងក្នុងមួយឆ្នាំ ។",
      "x=200", [C("diff(60000/x+3*x/2,x).subs(x,200)", "0"), C("(60000/x+3*x/2).subs(x,200)", "600")])
    H("rate_of_change", "medium", r"បន្ទះសូឡាមួយនៅមណ្ឌលគិរីផលិតថាមពល $P(t)=6\sin\frac{\pi(t-6)}{12}$ គីឡូវ៉ាត់ ចន្លោះម៉ោង $6$ ព្រឹក ដល់ម៉ោង $6$ ល្ងាច ($6\le t\le18$) ។ រកអត្រាបម្រែបម្រួលនៅម៉ោង $8$ ព្រឹក និងពេលដែលផលិតខ្លាំងបំផុត ។",
      "ដេរីវេនៃ $P$ ៖\n$$P'(t)=6\\cdot\\frac{\\pi}{12}\\cos\\frac{\\pi(t-6)}{12}=\\frac{\\pi}{2}\\cos\\frac{\\pi(t-6)}{12}$$\nនៅ $t=8$ ៖ $P'(8)=\\frac{\\pi}{2}\\cos\\frac{\\pi}{6}=\\frac{\\pi\\sqrt{3}}{4}$ ។\n$P'(t)=0$ ឲ្យ $\\frac{\\pi(t-6)}{12}=\\frac{\\pi}{2}$ ពោលគឺ $t=12$ ហើយ $P(12)=6$ ។\nដូចនេះ ៖\n$$\\boxed{P'(8)=\\frac{\\pi\\sqrt{3}}{4},\\quad t=12}$$",
      "t=12", [C("diff(6*sin(pi*(x-6)/12),x).subs(x,8)", "pi*sqrt(3)/4"), C("diff(6*sin(pi*(x-6)/12),x).subs(x,12)", "0"), C("(6*sin(pi*(x-6)/12)).subs(x,12)", "6")])
    H("optimization_exp_log", "medium", r"សិស្សម្នាក់ត្រៀមប្រឡងបាក់ឌុប ។ ពិន្ទុកើនតាមម៉ោងអានក្នុងមួយថ្ងៃ ប៉ុន្តែការហត់នឿយធ្វើឲ្យថយវិញ តាមគំរូ $f(t)=20\ln(t+1)-2t$ ដែល $t$ ជាម៉ោងអាន ($0\le t\le 12$) ។ តើគួរអានប៉ុន្មានម៉ោង?",
      "ដេរីវេ ៖\n$$f'(t)=\\frac{20}{t+1}-2=\\frac{18-2t}{t+1}$$\nដោយ $t+1>0$ សញ្ញានៃ $f'$ យកតាម $18-2t$ ។ $f'(t)=0$ ត្រង់ $t=9$ ។\n$f$ កើនលើ $[0;9]$ និងចុះលើ $[9;12]$ ។\n$$f(9)=20\\ln10-18$$\nដូចនេះ គួរអានប្រហែល ៖\n$$\\boxed{t=9}$$\nម៉ោង ។ អានលើសនេះមិនបានផលទេ ។",
      "t=9", [C("diff(20*log(x+1)-2*x,x).subs(x,9)", "0"), C("(20*log(x+1)-2*x).subs(x,9)", "20*log(10)-18")])
    H("lhopital_0_0", "medium", r"គណនាលីមីតខាងក្រោមដោយវិធីពីរ គឺវិធានឡូពីតាល់ និងកន្សោមឆ្លាស់ ៖ $$\lim_{x\to0}\frac{\sqrt{1+x}-\sqrt{1-x}}{x}$$",
      "វិធីទី១ ៖ រាង $\\frac{0}{0}$ ។ តាមវិធានឡូពីតាល់ ៖\n$$L=\\lim_{x\\to0}\\left(\\frac{1}{2\\sqrt{1+x}}+\\frac{1}{2\\sqrt{1-x}}\\right)=\\frac{1}{2}+\\frac{1}{2}=1$$\nវិធីទី២ ៖ គុណនឹងកន្សោមឆ្លាស់ ៖\n$$\\frac{\\sqrt{1+x}-\\sqrt{1-x}}{x}=\\frac{2x}{x(\\sqrt{1+x}+\\sqrt{1-x})}=\\frac{2}{\\sqrt{1+x}+\\sqrt{1-x}}$$\nកាលណា $x\\to0$ លីមីតស្មើ $\\frac{2}{2}=1$ ។\nដូចនេះ ៖\n$$\\boxed{L=1}$$",
      "1", [C("limit((sqrt(1+x)-sqrt(1-x))/x,x,0)", "1")])
    H("limit_as_derivative", "medium", r"តាមនិយមន័យដេរីវេ រកលីមីត $\lim_{x\to\frac{\pi}{4}}\frac{\tan x-1}{x-\frac{\pi}{4}}$ ។",
      "តាង $f(x)=\\tan x$ ។ គេមាន $f\\left(\\frac{\\pi}{4}\\right)=1$ ។\nលីមីតនេះគឺ $f'\\left(\\frac{\\pi}{4}\\right)$ ។\nដោយ $f'(x)=1+\\tan^2x$ នោះ ៖\n$$f'\\left(\\frac{\\pi}{4}\\right)=1+1=2$$\nដូចនេះ ៖\n$$\\boxed{L=2}$$",
      "2", [C("limit((tan(x)-1)/(x-pi/4),x,pi/4)", "2")])
    H("limit_as_derivative", "bacii", r"គេឲ្យ $f(x)=x^x=e^{x\ln x}$ ចំពោះ $x>0$ ។ គណនា $f'(x)$ រួចទាញរកលីមីត $\lim_{x\to1}\frac{x^x-1}{x-1}$ ។",
      "តាមរូបមន្ត $(e^{u})'=u'e^{u}$ ជាមួយ $u=x\\ln x$ និង $u'=\\ln x+1$ ៖\n$$f'(x)=(\\ln x+1)x^x$$\nគេមាន $f(1)=1$ ។ លីមីតជាដេរីវេត្រង់ $x=1$ ៖\n$$\\lim_{x\\to1}\\frac{f(x)-f(1)}{x-1}=f'(1)=(0+1)\\cdot1=1$$\nដូចនេះ ៖\n$$\\boxed{L=1}$$",
      "1", [C("diff(exp(x*log(x)),x).subs(x,1)", "1")])
    H("differentials", "medium", r"គំនរខ្សាច់រាងកោណមានកម្ពស់ថេរ ហើយកាំបាតវាស់បាន $10$ ម៉ែត្រ ដោយលម្អៀង $0.1$ ម៉ែត្រ ។ ប៉ាន់ស្មានលម្អៀងធៀបនៃមាឌ ជាភាគរយ ។",
      "មាឌកោណ $V=\\frac{1}{3}\\pi r^2h$ ដែល $h$ ថេរ ។ ឌីផេរ៉ង់ស្យែល ៖\n$$dV=\\frac{2}{3}\\pi rh\\,dr$$\nចែកនឹង $V$ ៖\n$$\\frac{dV}{V}=\\frac{2\\,dr}{r}=\\frac{2\\cdot0.1}{10}=\\frac{1}{50}$$\nដូចនេះ លម្អៀងធៀបនៃមាឌប្រហែល ៖\n$$\\boxed{2\\%}$$",
      "2\\%", [C("diff(x**2,x).subs(x,10)*Rational(1,10)/(x**2).subs(x,10)", "1/50")])
    H("related_rates_geometry", "medium", r"ត្រីកោណសមបាតស្មើមួយមានជ្រុង $a$ ដែលកើន $2$ សង់ទីម៉ែត្រក្នុងមួយវិនាទី ។ គណនាល្បឿនកើនក្រឡាផ្ទៃ ពេល $a=4$ សង់ទីម៉ែត្រ ។".replace("សមបាតស្មើ", "សមង្ស"),
      "ក្រឡាផ្ទៃត្រីកោណសមង្ស ៖ $S=\\frac{\\sqrt{3}}{4}a^2$ ។\nធ្វើដេរីវេធៀបនឹង $t$ ៖\n$$\\frac{dS}{dt}=\\frac{\\sqrt{3}}{2}a\\frac{da}{dt}$$\nចំពោះ $a=4$ និង $\\frac{da}{dt}=2$ ៖\n$$\\frac{dS}{dt}=\\frac{\\sqrt{3}}{2}\\cdot4\\cdot2=4\\sqrt{3}$$\nដូចនេះ ៖\n$$\\boxed{\\frac{dS}{dt}=4\\sqrt{3}}$$\nសង់ទីម៉ែត្រការ៉េក្នុងមួយវិនាទី ។",
      "4\\sqrt{3}", [C("diff(sqrt(3)*x**2/4,x).subs(x,4)*2", "4*sqrt(3)")])
    H("rate_of_change", "hard", r"ចំនួនទូរស័ព្ទដែលហាងមួយលក់បានសរុបក្រោយ $t$ ខែ គឺ $S(t)=-t^3+6t^2+15t$ ដែល $0\le t\le5$ ។ រកខណៈដែលការលក់លឿនបំផុត (ចំណុចរបត់នៃខ្សែកោង $S$) និងល្បឿនលក់នៅខណៈនោះ ។",
      "ល្បឿនលក់ ៖ $S'(t)=-3t^2+12t+15=-3(t+1)(t-5)$ ។\nដូច្នេះ $S'(t)\\ge0$ លើ $[0;5]$ ។\nដេរីវេទី២ ៖ $S''(t)=-6t+12$ ។ $S''(t)=0$ នាំឲ្យ $t=2$ ហើយ $S''$ ប្តូរសញ្ញាពី $+$ ទៅ $-$ ។\nដូច្នេះចំណុចអាប់ស៊ីស $t=2$ ជាចំណុចរបត់ ហើយ $S'$ មានអតិបរមា ។\n$$S'(2)=-12+24+15=27$$\nដូចនេះ ៖\n$$\\boxed{t=2,\\quad S'(2)=27}$$\nគ្រឿងក្នុងមួយខែ ។",
      "t=2,\\ 27", [C("diff(-x**3+6*x**2+15*x,x,2).subs(x,2)", "0"), C("diff(-x**3+6*x**2+15*x,x).subs(x,2)", "27")])

def main():
    plan = [(g_fence_area, 60), (g_fence_min, 50), (g_box, 40), (g_can, 24), (g_sqbox, 30), (g_profit_quad, 40), (g_profit_cubic, 30), (g_avgcost, 30), (g_price, 40), (g_trees, 25),
            (g_parab_rect, 15), (g_semicircle, 22), (g_cone_cyl, 24), (g_dist, 30), (g_shore, 40), (g_numbers, 35), (g_trip, 30), (g_poster, 20), (g_trough, 16), (g_drug, 30), (g_lnprofit, 25), (g_slant, 12), (g_wire, 20),
            (g_cubic_motion, 60), (g_throw, 35), (g_brake, 25), (g_harmonic, 30), (g_exp_motion, 35), (g_avg_inst, 15), (g_rate_growth, 110),
            (g_ladder, 30), (g_circle_sphere, 50), (g_cone_tank, 30), (g_cyl_tank, 12), (g_two_cars, 25), (g_shadow, 15), (g_kite, 20), (g_curve_point, 25),
            (g_lim_deriv, 70), (g_lim_given, 35), (g_lhop, 80), (g_lhop_inf, 35), (g_lim_param, 30),
            (g_approx, 60), (g_differential, 30), (g_error, 30), (g_linear, 22),
            (g_rolle, 40), (g_mvt, 35), (g_mvt_ineq, 30), (g_roots, 35), (g_speed, 15)]
    hand()
    print("hand rows", len(rows))
    for g, n in plan:
        run(g, max(10, int(n * 0.68)))
    write_jsonl(rows, "applications.jsonl")
    print("png", png[0])

if __name__ == "__main__":
    main()
