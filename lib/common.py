"""Shared helpers for the Khmer BacII derivative dataset. See SCHEMA.md."""
import hashlib, json, os, random, re
import sympy as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

x = sp.Symbol("x", real=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def lx(e):
    """LaTeX for a SymPy expression, in the notation Khmer BacII uses (\\ln, not \\log)."""
    s = sp.latex(e, ln_notation=True) if not isinstance(e, str) else e
    return s

def m(e):
    return "$" + lx(e) + "$"

def pick(rng, options):
    return rng.choice(options)

def s(e):
    """Plain SymPy string for checks."""
    return str(e)

def check(lhs, rhs, note=""):
    """A claim the independent verifier recomputes. lhs must be written from the problem
    definition (e.g. 'diff(x**3,x)'), rhs is the value the solution states."""
    return {"lhs": str(lhs), "rhs": str(rhs), "note": note}

def variation_table(cols, fprime, fvals, name="f"):
    """LaTeX variation table (តារាងអថេរភាព).
    cols:   x-row entries, LaTeX strings, e.g. ['-\\infty','-1','1','+\\infty']
    fprime: signs between/at columns, length 2*len(cols)-1, e.g. ['','+','0','-','0','+','']
    fvals:  f row, same length, values or '\\nearrow' / '\\searrow'; use '\\|' for a forbidden value."""
    n = 2 * len(cols) - 1
    assert len(fprime) == n and len(fvals) == n, "table rows must have 2*len(cols)-1 entries"
    xr = []
    for i, c in enumerate(cols):
        xr.append(c)
        if i < len(cols) - 1:
            xr.append("")
    spec = "c|" + "c" * n
    return ("\\begin{array}{" + spec + "}\n"
            "x & " + " & ".join(xr) + " \\\\\n\\hline\n"
            + name + "'(x) & " + " & ".join(fprime) + " \\\\\n\\hline\n"
            + name + "(x) & " + " & ".join(fvals) + "\n\\end{array}")

def tikz_graph(expr_pgf, xmin, xmax, ymin, ymax, extra=""):
    """pgfplots source of a curve: text a model can learn from. expr_pgf uses pgfplots syntax."""
    return ("\\begin{tikzpicture}\n\\begin{axis}[axis lines=middle,xlabel=$x$,ylabel=$y$,"
            f"xmin={xmin},xmax={xmax},ymin={ymin},ymax={ymax},samples=200]\n"
            f"\\addplot[thick,domain={xmin}:{xmax}] {{{expr_pgf}}};\n{extra}"
            "\\end{axis}\n\\end{tikzpicture}")

def plot_png(row_id, f, xmin=-5, xmax=5, ymin=-6, ymax=6, tangent=None, points=(), asymptotes=()):
    """Render a curve to diagrams/<row_id>.png. Labels are math only: matplotlib cannot shape
    Khmer script correctly, so never put Khmer text in a figure. Returns the relative path."""
    fn = sp.lambdify(x, f, "numpy")
    xs = np.linspace(xmin, xmax, 1500)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(np.asarray(fn(xs), dtype=float), xs.shape).copy()
    ys[np.abs(ys) > 10 * max(abs(ymin), abs(ymax))] = np.nan
    ys[1:][np.abs(np.diff(ys)) > (ymax - ymin)] = np.nan
    fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=110)
    ax.plot(xs, ys, lw=1.8, color="#1f4e9c")
    if tangent is not None:
        tn = sp.lambdify(x, tangent, "numpy")
        ax.plot(xs, np.broadcast_to(np.asarray(tn(xs), dtype=float), xs.shape), lw=1.1, color="#c0392b")
    for a in asymptotes:
        if a[0] == "v":
            ax.axvline(float(a[1]), ls="--", lw=0.9, color="gray")
        else:
            an = sp.lambdify(x, a[1], "numpy")
            ax.plot(xs, np.broadcast_to(np.asarray(an(xs), dtype=float), xs.shape), ls="--", lw=0.9, color="gray")
    for px, py in points:
        ax.plot([float(px)], [float(py)], "o", ms=4, color="#c0392b")
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    for sd in ("top", "right"):
        ax.spines[sd].set_visible(False)
    for sd in ("left", "bottom"):
        ax.spines[sd].set_position("zero")
    ax.grid(alpha=0.2)
    rel = f"diagrams/{row_id}.png"
    fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight")
    plt.close(fig)
    return rel

def make_row(topic, subtopic, difficulty, problem_km, solution_km, answer_latex, checks,
             generator, diagrams=None, marks=None, row_id=None, chapter="derivative", grade=12):
    h = hashlib.sha1(problem_km.encode()).hexdigest()[:10]
    return {
        "id": row_id or f"{topic}-{h}",
        "chapter": chapter, "grade": grade,
        "topic": topic, "subtopic": subtopic, "difficulty": difficulty, "marks": marks,
        "problem_km": problem_km, "solution_km": solution_km, "answer_latex": answer_latex,
        "diagrams": diagrams or [],
        "checks": checks,
        "provenance": {"origin": "original_synthetic", "generator": generator,
                       "source_url": None, "license": None},
    }

def write_jsonl(rows, name):
    path = os.path.join(ROOT, "out", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to out/{name}")
