"""Shared finishing helpers for the three limit generators: notation clean-up of LaTeX text, graphs split at
poles, squeeze figures, and the row tags that are added after make_row returns."""
import re
from common import tikz_graph

def _group(t, i):
    """t[i] is '{'. Returns the index after the matching '}', or -1."""
    d = 0; j = i
    while j < len(t):
        if t[j] == "\\": j += 2; continue
        d += (t[j] == "{") - (t[j] == "}"); j += 1
        if d == 0: return j
    return -1

def _is_sum(a):
    """True if a has a + or - outside every bracket, after its first character."""
    d = 0; b = a.replace(r"\left(", "(").replace(r"\right)", ")").replace(r"\left[", "[").replace(r"\right]", "]")
    for i, c_ in enumerate(b):
        d += c_ in "({[" ; d -= c_ in ")}]"
        if c_ in "+-" and d == 0 and i > 0: return True
    return False

def _par(a): return r"\left(" + a + r"\right)"

def _rewrite(t):
    """One pass: rewrite the first fraction over 1, over -1 or over a negative integer. Returns (text, changed)."""
    for m in re.finditer(r"\\frac(?=\{)", t):
        e1 = _group(t, m.end())
        if e1 < 0 or e1 >= len(t) or t[e1] != "{": continue
        e2 = _group(t, e1)
        if e2 < 0: continue
        a, b = t[m.end() + 1:e1 - 1], t[e1 + 1:e2 - 1].strip()
        if not re.fullmatch(r"1|-\d+", b): continue
        pre, post = t[:m.start()], t[e2:]
        neg = b.startswith("-")
        if a.lstrip().startswith("-") and not _is_sum(a.strip()):
            a = a.strip()[1:]; neg = not neg
        body = a if b in ("1", "-1") else r"\frac{" + a + "}{" + b[1:] + "}"
        tail = pre.rstrip()
        mult = bool(re.search(r"(\\cdot|\\times|[0-9a-zA-Z)\]])$", tail)) and not re.search(r"\\(to|le|ge|leq|geq|neq|quad|qquad|Rightarrow|Leftrightarrow|approx|in)$", tail)
        follow = bool(re.match(r"\s*(\\cdot|\\times|\^|[0-9a-zA-Z(]|\\left|\\sqrt|\\frac)", post))
        issum = b in ("1", "-1") and _is_sum(a)
        if issum and (neg or tail.endswith("-") or mult or follow):
            body = _par(a)
        if neg:
            if tail.endswith("-"):      # minus over minus
                lead = tail[:-1].rstrip()
                pre = lead + ("" if not lead or re.search(r"[=({,&$]$|\\left\($|\\to$|\\le$|\\ge$", lead) else "+")
                return pre + body + post, True
            if tail.endswith("+"):
                return tail[:-1] + "-" + body + post, True
            if mult:
                return pre + _par("-" + body) + post, True
            return pre + "-" + body + post, True
        return pre + body + post, True
    return t, False

def clean_tex(t):
    """Fractions over 1, minus over minus, brackets around a lone x. Applied to every text field."""
    if not t or "\\" not in t and "(x)" not in t: return t
    changed = False
    for _ in range(200):
        t, ch = _rewrite(t)
        if not ch: break
        changed = True
    if changed:   # a value that was written as a fraction and then again as a number
        t = re.sub(r"(=|\\to\s*)(-?(?:\\frac\{\d+\}\{\d+\}|\d+))=\2(?![\d{/.])", r"\1\2", t)
    t = re.sub(r"(?<=[+\-={(])1x(?![a-zA-Z])", "x", t)   # a coefficient 1 left by a template
    t = re.sub(r"\\(ln|sin|cos|tan|cot)\\left\(x\\right\)", r"\\\1 x", t)
    t = re.sub(r"(?<=[fgh])\\left\(x\\right\)", "(x)", t)
    t = re.sub(r"(?<=[fgh]')\\left\(x\\right\)", "(x)", t)
    t = re.sub(r"(?<![A-Za-z'])\\left\(x\\right\)", "x", t)
    t = re.sub(r"(?<![A-Za-z'])\(x\)\^", "x^", t)
    t = re.sub(r"(?<![A-Za-z'}\\_^])\(x\)", "x", t)
    return t

# ---------- graphs ----------
def split_domain(xmin, xmax, poles, gap=0.02):
    """Sub-intervals of [xmin,xmax] that stop short of each pole, so no sampled line crosses one."""
    cuts = sorted(float(p) for p in poles if xmin < float(p) < xmax)
    out, a = [], float(xmin)
    for p in cuts:
        out.append((a, p - gap)); a = p + gap
    out.append((a, float(xmax)))
    return out

def tikz_poles(expr, xmin, xmax, ymin, ymax, poles, extra="", gap=0.02):
    """tikz_graph with one \\addplot per branch: a single domain across a pole draws a false vertical line."""
    src = tikz_graph(expr, xmin, xmax, ymin, ymax, extra)
    one = f"\\addplot[thick,domain={xmin}:{xmax}] {{{expr}}};\n"
    assert one in src
    many = "".join(f"\\addplot[thick,domain={a:g}:{b:g}] {{{expr}}};\n" for a, b in split_domain(xmin, xmax, poles, gap))
    return src.replace(one, many)

def _one(e):
    """Drop a coefficient 1 from pgfplots source."""
    return re.sub(r"(?<![\d.])1\*", "", e)

def tikz_squeeze(curve, bounds, xmin, xmax, ymin, ymax, poles=(), gap=0.01):
    """The curve (solid, split at poles) and each bound (dashed). Radians, because curves are trigonometric."""
    curve = _one(curve); bounds = [_one(e) for e in bounds]
    src = ("\\begin{tikzpicture}\n\\begin{axis}[axis lines=middle,xlabel=$x$,ylabel=$y$,"
           f"xmin={xmin},xmax={xmax},ymin={ymin},ymax={ymax},samples=400,trig format=rad]\n")
    for a, b in split_domain(xmin, xmax, poles, gap):
        src += f"\\addplot[thick,domain={a:g}:{b:g}] {{{curve}}};\n"
    for e in bounds:
        src += f"\\addplot[dashed,domain={xmin}:{xmax}] {{{e}}};\n"
    return src + "\\end{axis}\n\\end{tikzpicture}"

# ---------- tags added after make_row returns ----------
PLAIN_LIMIT = "limit_at_removable_point"
FIGURE_SUBTOPICS = {"read_graph", "one_sided_read_from_graph", "bacii_read_full_graph"}

def exam_style_limit(sub):
    """Continuity-topic subtopics that are exam-style: the bacii_ items, and plain limits."""
    return sub.startswith("bacii_") or sub == PLAIN_LIMIT

def exam_fit(r):
    if r["topic"] != "limit_continuity": return "bacii_seen"
    return "bacii_seen" if exam_style_limit(r["subtopic"]) else "textbook"

def finish_rows(rows):
    """Run once per generator on the finished rows, whatever path built them."""
    for r in rows:
        r["exam_fit"] = exam_fit(r)
        for d in r["diagrams"]:
            if d.get("alt_km"): d["alt_km"] = clean_tex(d["alt_km"])
            if d["type"] in ("variation_table", "sign_table"): d["latex"] = clean_tex(d["latex"])
            if r["subtopic"] in FIGURE_SUBTOPICS and d["type"] in ("graph", "figure"):
                d["in_problem"] = True
    return rows
