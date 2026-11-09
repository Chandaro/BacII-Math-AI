"""Shared printing for the integral, differential equation and probability generators.
All values come from SymPy. No text is written by a language model at run time."""
from core import *
K = ["ក", "ខ", "គ", "ឃ", "ង", "ច"]
def T(e):
    if isinstance(e, str): return e
    e = sp.sympify(e)
    if e.is_Add and len(e.args) == 2:
        p, q = e.as_ordered_terms()
        tp, tq = T(p), T(q)
        if tp.startswith("-") and not tq.startswith("-"): return f"{tq} {tp}"
    t = sp.latex(e, ln_notation=True, imaginary_unit="i")
    t = re.sub(r"\\ln\{\\left\(x \\right\)\}\^\{(\d+)\}", r"\\ln^{\1} x", t)
    t = t.replace("\\ln{\\left(x \\right)}", "\\ln x").replace("\\ln{\\left(u \\right)}", "\\ln u")
    t = re.sub(r"\\ln\{\\left\((\d+) \\right\)\}", r"\\ln \1", t)
    t = re.sub(r"\\ln\{\\left\((.+?) \\right\)\}", r"\\ln\\left(\1\\right)", t)
    t = re.sub(r"\\(sin|cos|tan)\^\{(\d+)\}\{\\left\((\d* ?[xu]) \\right\)\}", lambda m: f"\\{m[1]}^{{{m[2]}}} {m[3].replace(' ', '')}", t)
    t = re.sub(r"\\(sin|cos|tan)\{\\left\((\d* ?[xu]) \\right\)\}", lambda m: f"\\{m[1]} {m[2].replace(' ', '')}", t)
    t = re.sub(r"\\(sin|cos|tan)\{\\left\((.+?) \\right\)\}", r"\\\1\\left(\2\\right)", t)
    return t
def TL(e):
    """Primitive with absolute value inside ln, as printed in the answer books."""
    t = T(e); t = re.sub(r"\\ln ([xu])", r"\\ln\\left|\1\\right|", t)
    return re.sub(r"\\ln\\left\((.+?)\\right\)", r"\\ln\\left|\1\\right|", t)
def cf(c):
    """Coefficient before a symbol: nothing for 1, a minus for -1."""
    return "" if c == 1 else ("-" if c == -1 else T(c))
def V(e):
    """Exact value in a printable form."""
    e = sp.expand(e)
    for L in list(e.atoms(sp.log)):
        n = L.args[0]
        if n.is_Integer and n > 1:
            e = e.subs(L, sum(k * sp.Mul(sp.log(q), evaluate=True) for q, k in sp.factorint(n).items()))
    e = sp.expand(e); s = sp.simplify(e)
    return e if s.has(sp.sinh, sp.cosh, sp.tanh, sp.exp) or e.has(sp.E) or e.has(sp.log) else s
def B(e):
    """Brackets around a sum."""
    return f"\\left({T(e)}\\right)" if sp.sympify(e).is_Add else T(e)
def Int(f, a=None, b=None, var="x"):
    lim = "" if a is None else f"_{{{T(a)}}}^{{{T(b)}}}"
    body = f if isinstance(f, str) else B(f)
    if body.startswith("-"): body = f"\\left({body}\\right)"
    return f"\\int{lim} {body}\\,d{var}"
def EV(rng, F, a, b):
    t = F if isinstance(F, str) else T(F)
    return rng.choice((f"\\left[{t}\\right]_{{{T(a)}}}^{{{T(b)}}}", f"\\left.{t}\\right|_{{{T(a)}}}^{{{T(b)}}}"))
def nz(rng, lo=-6, hi=6, skip=(0,)):
    while True:
        v = rng.randint(lo, hi)
        if v not in skip: return v
def so(w):  return w.v("ដូចនេះ", "ដូចនេះ", "សរុបមក")
def gb(w):  return w.v("គេបាន", "យើងបាន", "នាំឱ្យ")
