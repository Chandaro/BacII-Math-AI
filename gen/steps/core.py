"""Worked-solution writer. Every printed equality is checked by SymPy here and stored in row['checks']
so lib/verify.py can recompute it separately. No text is written by a language model at run time."""
import os, random, re, sys
import sympy as sp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
from common import x, check, make_row
I, R = sp.I, sp.Rational
def tx(e):
    if isinstance(e, str): return e
    t = sp.latex(e, ln_notation=True, imaginary_unit="i")
    t = t.replace("\\ln{\\left(x \\right)}", "\\ln x")
    t = re.sub(r"\\ln\{\\left\((\d+) \\right\)\}", r"\\ln \1", t)
    return re.sub(r"\\ln\{\\left\((.+?) \\right\)\}", r"\\ln\\left(\1\\right)", t)
def fr(n, d):
    """Signed fraction term for use after another term: +a/b or -a/b, never a/b with a hidden minus."""
    return ("+" if n >= 0 else "-") + f"\\frac{{{abs(n)}}}{{{d}}}"
def st(n):
    """Signed number after another term; nothing for zero."""
    return "" if n == 0 else (f"+{tx(n)}" if n > 0 else tx(n))
def br(e):
    """Brackets only around a sum."""
    return f"\\left({tx(e)}\\right)" if sp.sympify(e).is_Add else tx(e)
def ratio(a, b):
    """a/b for printing after a times sign."""
    q = sp.Rational(a, b)
    if b == 1 or q.is_integer: return pp(q) if q < 0 else tx(q)
    return f"\\frac{{{a}}}{{{b}}}"
def pp(v):
    """Always bracketed, for a value multiplied by a printed number."""
    return f"\\left({tx(v)}\\right)"
def par(v):
    """Value ready to substitute: brackets for negatives and fractions."""
    t = tx(v)
    return f"\\left({t}\\right)" if (t.startswith("-") or "frac" in t or "+" in t) else t
def same(a, b):
    d = sp.simplify(sp.expand(a) - sp.expand(b))
    return d == 0
class W:
    """A solution being written line by line."""
    def __init__(s, rng): s.L, s.C, s.rng = [], [], rng
    def say(s, t): s.L.append(t); return s
    def v(s, *opts): return s.rng.choice(opts)
    def ok(s, a, b, note="step"):
        assert same(a, b), (a, b)
        if not ({str(q) for q in (sp.sympify(a) - sp.sympify(b)).free_symbols} - {"x"}):
            s.C.append(check(a, b, note))
    def chain(s, *items, pre=""):
        """items: expression, or (latex, expression). Prints one = per line and checks each step."""
        ts = [i[0] if isinstance(i, tuple) else tx(i) for i in items]
        es = [i[1] if isinstance(i, tuple) else i for i in items]
        for a, b in zip(es, es[1:]): s.ok(a, b)
        s.L.append(f"$${pre}{ts[0]}" + (f"={ts[1]}$$" if len(ts) > 1 else "$$"))
        for t in ts[2:]: s.L.append(f"$$={t}$$")
        return s
    def text(s): return "\n".join(s.L)
def psub(p, v, name="f"):
    """(printed substitution, printed term values, value) for a polynomial p at v."""
    P = sp.Poly(p, x); a, b = [], []
    for (d,), c in P.terms():
        val = c * v ** d
        ct = tx(c) if (d == 0 or abs(c) != 1) else ("-" if c < 0 else "")
        pw = "" if d == 0 else (par(v) if ct in ("", "-") and d == 1 and False else pp(v)) + (f"^{{{d}}}" if d > 1 else "")
        if d and "frac" in ct: ct = pp(c)
        a.append((ct + pw)); b.append(tx(val))
    join = lambda L: L[0] + "".join(t if t.startswith("-") else "+" + t for t in L[1:])
    return join(a), join(b), p.subs(x, v)
def sgn(v): return "+" if v > 0 else "-"
def interval(a, b, sep=";"): return f"({tx(a)}{sep}{tx(b)})"
def sign_table(cols, cells, label="f'(x)"):
    """cols latex list; cells 2n-1 entries."""
    n = 2 * len(cols) - 1; xr = []
    for i, c in enumerate(cols):
        xr.append(c)
        if i < len(cols) - 1: xr.append("")
    return "$$\\begin{array}{c|" + "c" * n + "}\nx & " + " & ".join(xr) + " \\\\\n\\hline\n" + label + " & " + " & ".join(cells) + "\n\\end{array}$$"
def var_table(cols, signs, vals, name="f"):
    n = 2 * len(cols) - 1; xr = []
    for i, c in enumerate(cols):
        xr.append(c)
        if i < len(cols) - 1: xr.append("")
    return ("$$\\begin{array}{c|" + "c" * n + "}\nx & " + " & ".join(xr) + " \\\\\n\\hline\n" + name + "'(x) & " + " & ".join(signs)
            + " \\\\\n\\hline\n" + name + "(x) & " + " & ".join(vals) + "\n\\end{array}$$")
def row(w, chapter, topic, sub, diff, problem, answer, gen):
    grade = 12 if chapter != "limit" else 12
    w.say("") if False else None
    return make_row(topic, sub, diff, problem, w.text(), answer, w.C, f"steps/{gen}", chapter=chapter, grade=grade)
def family(fn, n, seed, tries=40):
    """Run a generator until n different questions exist, or the parameter space runs out."""
    rng = random.Random(seed); out = {}; miss = 0
    while len(out) < n and miss < tries * 10:
        r = fn(rng)
        if r is None or r["problem_km"] in out: miss += 1; continue
        out[r["problem_km"]] = r
    return list(out.values())
