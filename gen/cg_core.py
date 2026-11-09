"""Formatting, exact helpers and figure helpers for complex_geometry."""
import os, re, sys
import sympy as sp
from sympy import I, sqrt, pi, Rational as R
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from common import ROOT, plt

X = sp.Symbol("x", real=True); Y = sp.Symbol("y", real=True)
def E(z): return sp.expand(z)
def ri(z):
    a, b = E(z).as_real_imag(); return sp.radsimp(a), sp.radsimp(b)
def cj(z): return E(sp.conjugate(z))
def n2(z):
    a, b = ri(z); return E(a*a + b*b)
def md(z): return sp.sqrt(n2(z))
def dv(p, q):
    return E(sp.radsimp(E(p*cj(q))/n2(q)))
def L(e):
    s_ = e if isinstance(e, str) else sp.latex(e)
    s_ = re.sub(r"(\\[a-zA-Z]+) (?=[a-zA-Z0-9])", r"\1@", s_).replace(" ", "").replace("@", " ")
    return s_
def D(t): return "$" + t + "$"
def DD(t): return "\n$$" + t + "$$\n"
def fr(a, b): return "\\frac{" + str(a) + "}{" + str(b) + "}"
def _im(b):
    if b == 1: return "i"
    if b == -1: return "-i"
    if b.is_Add: return "\\left(" + L(b) + "\\right)i"
    c, r = b.as_coeff_Mul()
    if r != 1 and c.is_Integer:
        h = "" if abs(c) == 1 else str(abs(c))
        return ("-" if c < 0 else "") + h + "i" + L(r)
    return L(b) + "i"
def zt(z):
    a, b = ri(z)
    if b == 0: return L(a)
    if a == 0: return _im(b)
    t = _im(b)
    return L(a) + (t if t.startswith("-") else "+" + t)
def par(z):
    a, b = ri(z)
    if b == 0 and a >= 0 and not a.is_Add: return zt(z)
    if a == 0 and b > 0 and not b.is_Add: return zt(z)
    return "(" + zt(z) + ")"
def sq(v):
    v = sp.nsimplify(v)
    if v.is_Integer and v >= 0: return str(v) + "^{2}"
    if v.is_Integer: return "(" + str(v) + ")^{2}"
    return "\\left(" + L(v) + "\\right)^{2}"
def modst(z):
    """sqrt(a^2+b^2)=...=r"""
    a, b = ri(z); N = n2(z); r = sp.sqrt(N)
    if a == 0 or b == 0:
        return L(r)
    t = "\\sqrt{" + sq(a) + "+" + sq(b) + "}"
    if N.is_Integer and sp.sqrt(N).is_Integer:
        return t + "=\\sqrt{" + str(N) + "}=" + L(r)
    if N.is_Integer and L(r) != "\\sqrt{" + str(N) + "}":
        return t + "=\\sqrt{" + str(N) + "}=" + L(r)
    return t + "=" + L(r)
def C(z):
    return "(" + str(E(z)) + ")"
def divst(p, q, pn=None, qn=None):
    """chain p/q = ... = result (conjugate of the denominator)"""
    w = dv(p, q); head = fr(zt(p), zt(q))
    a, b = ri(q)
    if b == 0:
        return head + "=" + zt(w)
    if a == 0:
        return head + "=" + fr(par(p) + "\\times " + par(cj(q)), par(q) + "\\times " + par(cj(q))) + "=" + fr(zt(E(p*cj(q))), L(n2(q))) + "=" + zt(w)
    return head + "=" + fr(par(p) + par(cj(q)), par(q) + par(cj(q))) + "=" + fr(zt(E(p*cj(q))), L(n2(q))) + "=" + zt(w)
def angt(th): return L(th)
def tf(r, th):
    body = ("\\cos " + L(th) + "+i\\sin " + L(th)) if th > 0 else ("\\cos\\left(" + L(th) + "\\right)+i\\sin\\left(" + L(th) + "\\right)")
    body = body.replace("\\cos \\", "\\cos\\").replace("\\sin \\", "\\sin\\")
    return ("" if r == 1 else L(r)) + "\\left(" + body + "\\right)"
def theta(w):
    t = sp.arg(E(w))
    return t
def _rt(a, r):
    q = L(sp.radsimp(a/r)); f = fr(L(a), L(r))
    return q if (f == q or r == 1) else f + "=" + q
def argst(w, nm="w", define=False):
    """Khmer text finding modulus and argument, returns (text, r, theta)."""
    a, b = ri(w); r = sp.radsimp(md(w)); th = theta(w)
    t = ("តាង " + D(nm + "=" + zt(w)) + " ។ " if define else "") + D("|" + nm + "|=r=" + modst(w)) + " ។ តាង " + D("\\alpha") + " ជាអាគុយម៉ង់នៃ " + D(nm) + " គេបាន" + \
        DD("\\cos\\alpha=" + _rt(a, r) + ",\\quad\\sin\\alpha=" + _rt(b, r)) + \
        "នាំឱ្យ " + D("\\alpha=" + L(th) + "+2k\\pi,\\ k\\in\\mathbb{Z}") + " ។"
    return t, r, th

# ---------------- text clean-up shared by the three complex generators ----------------
_TERM = re.compile(r"$|[=$|)}\],.;:+\-&\s]|\\(right|quad|qquad|,|\s|\\|Rightarrow|Leftrightarrow|neq|le\b|ge\b|text|end)")
def _close(t, i):
    """t[i:] starts just after an opening bracket. Returns (body_end, after_close), or None."""
    d = 0; j = i
    while j < len(t):
        c = t[j]
        if c == "$": return None
        if t.startswith("\\left(", j): d += 1; j += 6; continue
        if t.startswith("\\right)", j):
            if d == 0: return j, j + 7
            d -= 1; j += 7; continue
        if c == "\\": j += 2; continue
        if c == "(": d += 1
        elif c == ")":
            if d == 0: return j, j + 1
            d -= 1
        j += 1
    return None
def _flip(b):
    """Negate a sum whose first term is signed. Returns None if it is not a plain sum."""
    if re.search(r"=|,|\\pm|\\mp", b): return None
    o = []; d = 0; j = 0
    while j < len(b):
        c = b[j]
        if c == "\\":
            m_ = re.match(r"\\[a-zA-Z]+|\\.", b[j:]); w = m_.group()
            o.append(w); j += len(w); continue
        if c in "{([": d += 1
        elif c in "})]": d -= 1
        o.append(("-" if c == "+" else "+") if d == 0 and c in "+-" else c); j += 1
    return "".join(o)
def _unnest(t):
    """a+(-b+c) -> a-b+c. Also v-(-b+c) -> v+b-c when v is a variable or a closing brace.
    Bracketed numbers subtracted from bracketed numbers stay as written substitution steps."""
    out = []; i = 0
    rx = re.compile(r"([+-])(\\left\(|\()-")
    while True:
        m_ = rx.search(t, i)
        if not m_:
            out.append(t[i:]); return "".join(out)
        sign, op = m_.group(1), m_.group(2); s0 = m_.start(); out.append(t[i:s0]); i = s0
        prev = "".join(out)[-1:]
        cl = _close(t, m_.end())
        ok = cl is not None and (sign == "+" or prev.isalpha() or prev in "}'")
        if ok:
            e, a = cl; body = t[m_.end() - 1:e]; nb = _flip(body); nx = t[a:a + 1]
            single = not re.search(r"(?<!^)[+-]", re.sub(r"\{[^{}]*\}", "", body))
            if nb is None or nx in ("^", "_") or (nx.isdigit() and not (sign == "+" and single)): ok = False
        if not ok:
            out.append(t[s0:m_.end()]); i = m_.end(); continue
        if sign == "-":   # nb starts with +, drop the minus in front
            if _TERM.match(t, a):
                out.append(nb)
            else:
                out.append("+" + op + nb[1:] + t[e:a])
        else:
            if _TERM.match(t, a):
                out.append(body)
            elif not single:
                out.append("-" + op + nb[1:] + t[e:a])
            else:
                out.append(body + ("\\times " if nx.isdigit() else ""))
        i = a
def _unbracket(t):
    """=\\left(\\cos u+i\\sin u\\right) -> =\\cos u+i\\sin u when the modulus is 1 and nothing multiplies it."""
    key = "=\\left(\\cos"; out = []; i = 0
    while True:
        j = t.find(key, i)
        if j < 0:
            out.append(t[i:]); return "".join(out)
        s0 = j + 7; cl = _close(t, s0); out.append(t[i:j + 1]); i = j + 1
        if cl and "\\sin" in t[s0:cl[0]] and _TERM.match(t, cl[1]) and t[cl[1]:cl[1] + 1] != "^":
            out.append(t[s0:cl[0]]); i = cl[1]
def tidy(t):
    """Sign and bracket clean-up applied to every problem, solution and answer."""
    t = re.sub(r"=\+(?!\\infty)", "=", t)
    while True:
        u = _unnest(t)
        if u == t: return _unbracket(t)
        t = u

class P:
    def __init__(s_, l, n, v): s_.l, s_.n, s_.v = l, n, E(v)
def dl(p, q):
    w = q.v - p.v
    return p.l + q.l + "=|" + q.n + "-" + p.n + "|=|" + par(q.v) + "-" + par(p.v) + "|=|" + zt(w) + "|=" + modst(w)
def vec(p, q): return "\\overrightarrow{" + p.l + q.l + "}"
def vn(p, q): return "\\overrightarrow{" + p + q + "}"

# ---------------- figures ----------------
def bounds(sp_):
    xs, ys = [0.0], [0.0]
    def add(z):
        a, b = complex(sp.N(z)).real, complex(sp.N(z)).imag; xs.append(a); ys.append(b)
    for _, z in sp_.get("pts", []): add(z)
    for pl in sp_.get("poly", []):
        for z in pl: add(z)
    for a, b in sp_.get("seg", []) + sp_.get("line", []) + sp_.get("vec", []): add(a); add(b)
    for c, r in sp_.get("circ", []):
        cc = complex(sp.N(c)); rr = float(sp.N(r)); xs += [cc.real-rr, cc.real+rr]; ys += [cc.imag-rr, cc.imag+rr]
    for c, r, r2 in sp_.get("disk", []):
        cc = complex(sp.N(c)); rr = float(sp.N(r2)); xs += [cc.real-rr, cc.real+rr]; ys += [cc.imag-rr, cc.imag+rr]
    return int(np.floor(min(xs)))-1, int(np.ceil(max(xs)))+1, int(np.floor(min(ys)))-1, int(np.ceil(max(ys)))+1
def f3(z):
    c = complex(sp.N(z)); return round(c.real, 3), round(c.imag, 3)
def clip_line(p, q, b):
    (x1, y1), (x2, y2) = f3(p), f3(q); dx, dy = x2-x1, y2-y1
    ts = []
    for v, d, lo, hi in ((x1, dx, b[0], b[1]), (y1, dy, b[2], b[3])):
        if abs(d) > 1e-9: ts += sorted([(lo-v)/d, (hi-v)/d])
    if abs(dx) < 1e-9: t0, t1 = ts
    elif abs(dy) < 1e-9: t0, t1 = ts
    else: t0, t1 = max(ts[0], ts[2]), min(ts[1], ts[3])
    return (round(x1+t0*dx, 3), round(y1+t0*dy, 3)), (round(x1+t1*dx, 3), round(y1+t1*dy, 3))
def tikz(sp_):
    b = bounds(sp_); o = ["\\begin{tikzpicture}[scale=0.6,>=stealth]"]
    o.append(f"\\draw[very thin,gray!30] ({b[0]},{b[2]}) grid ({b[1]},{b[3]});")
    o.append(f"\\draw[->] ({b[0]},0)--({b[1]},0) node[right]{{$x$}};")
    o.append(f"\\draw[->] (0,{b[2]})--(0,{b[3]}) node[above]{{$y$}};")
    o.append("\\node[below left] at (0,0) {$O$};")
    for c, r, r2 in sp_.get("disk", []):
        cx, cy = f3(c)
        o.append(f"\\fill[blue!15,even odd rule] ({cx},{cy}) circle ({float(sp.N(r2)):.3f}) ({cx},{cy}) circle ({float(sp.N(r)):.3f});")
    for pl in sp_.get("poly", []):
        o.append("\\draw[thick,blue!70!black] " + " -- ".join("(%s,%s)" % f3(z) for z in pl) + " -- cycle;")
    for a, c in sp_.get("seg", []):
        o.append("\\draw[thick] (%s,%s) -- (%s,%s);" % (f3(a)+f3(c)))
    for a, c in sp_.get("vec", []):
        o.append("\\draw[->,thick,red!70!black] (%s,%s) -- (%s,%s);" % (f3(a)+f3(c)))
    for a, c in sp_.get("line", []):
        p, q = clip_line(a, c, b); o.append(f"\\draw[thick,red!70!black] ({p[0]},{p[1]}) -- ({q[0]},{q[1]});")
    for a, c in sp_.get("ray", []):
        p, q = clip_line(a, c, b); s0 = f3(a)
        d = (f3(c)[0]-s0[0], f3(c)[1]-s0[1])
        e = q if (q[0]-s0[0])*d[0]+(q[1]-s0[1])*d[1] > 0 else p
        o.append(f"\\draw[thick,red!70!black] ({s0[0]},{s0[1]}) -- ({e[0]},{e[1]});")
    for c, r in sp_.get("circ", []):
        cx, cy = f3(c); o.append(f"\\draw[thick,red!70!black] ({cx},{cy}) circle ({float(sp.N(r)):.3f});")
    for l, z in sp_.get("pts", []):
        cx, cy = f3(z); o.append(f"\\fill ({cx},{cy}) circle (2pt) node[above right]{{${l}$}};")
    o.append("\\end{tikzpicture}")
    return "\n".join(o)
def png(row_id, sp_):
    b = bounds(sp_); fig, ax = plt.subplots(figsize=(4.0, 4.0), dpi=100)
    ax.set_aspect("equal"); ax.set_xlim(b[0], b[1]); ax.set_ylim(b[2], b[3])
    for sd in ("top", "right"): ax.spines[sd].set_visible(False)
    for sd in ("left", "bottom"): ax.spines[sd].set_position("zero")
    ax.grid(alpha=0.25); ax.set_xticks(range(b[0], b[1]+1)); ax.set_yticks(range(b[2], b[3]+1)); ax.tick_params(labelsize=6)
    t = np.linspace(0, 2*np.pi, 300)
    for c, r, r2 in sp_.get("disk", []):
        cx, cy = f3(c); ax.add_patch(plt.Circle((cx, cy), float(sp.N(r2)), color="#c9dbf5", zorder=0))
        if float(sp.N(r)) > 0: ax.add_patch(plt.Circle((cx, cy), float(sp.N(r)), color="white", zorder=0))
    for pl in sp_.get("poly", []):
        q = [f3(z) for z in pl]+[f3(pl[0])]; ax.plot(*zip(*q), lw=1.6, color="#1f4e9c")
    for a, c in sp_.get("seg", []): ax.plot(*zip(f3(a), f3(c)), lw=1.3, color="black")
    for a, c in sp_.get("vec", []):
        ax.annotate("", xy=f3(c), xytext=f3(a), arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.4))
    for a, c in sp_.get("line", []):
        p, q = clip_line(a, c, b); ax.plot(*zip(p, q), lw=1.4, color="#c0392b")
    for a, c in sp_.get("ray", []):
        p, q = clip_line(a, c, b); s0 = f3(a); d = (f3(c)[0]-s0[0], f3(c)[1]-s0[1])
        e = q if (q[0]-s0[0])*d[0]+(q[1]-s0[1])*d[1] > 0 else p
        ax.plot(*zip(s0, e), lw=1.4, color="#c0392b")
    for c, r in sp_.get("circ", []):
        cx, cy = f3(c); rr = float(sp.N(r)); ax.plot(cx+rr*np.cos(t), cy+rr*np.sin(t), lw=1.4, color="#c0392b")
    for l, z in sp_.get("pts", []):
        cx, cy = f3(z); ax.plot([cx], [cy], "o", ms=4, color="#c0392b")
        ax.annotate("$" + l + "$", (cx, cy), textcoords="offset points", xytext=(4, 4), fontsize=9)
    rel = f"diagrams/{row_id}.png"
    fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
    return rel
