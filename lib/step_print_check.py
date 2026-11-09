"""Check the LaTeX as PRINTED, not the SymPy behind it. Joins $$A=B$$ / $$=C$$ runs, parses each side and compares
numerically at sample points. Usage: step_print_check.py file.jsonl. Reports coverage and mismatches; never edits."""
import json, re, signal, sys
from multiprocessing import Pool
import sympy as sp
from sympy.parsing.latex import parse_latex
XS = sp.Symbol("x")
class T(Exception): pass
def alarm(*a): raise T()
def clean(s):
    s = re.sub(r"\\lim_\{[^{}]*(\{[^{}]*\})?[^{}]*\}", "", s)
    for a, b in (("\\left", ""), ("\\right", ""), ("\\dfrac", "\\frac"), ("\\,", " "), ("\\times", "\\cdot"), ("\\quad", " ")):
        s = s.replace(a, b)
    s = re.sub(r"\\ln ([a-z0-9])", r"\\ln(\1)", s)
    return s.strip().rstrip(".,;")
def val(s, v):
    e = parse_latex(clean(s), backend="lark").subs({sp.Symbol("e"): sp.E, sp.Symbol("i"): sp.I})
    return complex(e.subs(XS, v).evalf())
def split(t):
    out, d, cur = [], 0, ""
    for c in t:
        d += c in "{(["; d -= c in "})]"
        if c == "=" and d == 0: out.append(cur); cur = ""
        else: cur += c
    return out + [cur]
def chains(sol):
    runs = []
    for ln in sol.split("\n"):
        m = re.fullmatch(r"\$\$(.+)\$\$", ln.strip())
        if not m or "\\begin" in m[1] or "\\boxed" in m[1]: runs.append(None); continue
        if m[1].startswith("=") and runs and runs[-1] is not None: runs[-1] += m[1]
        else: runs.append(m[1])
    return [r for r in runs if r]
def row(line):
    signal.signal(signal.SIGALRM, alarm); r = json.loads(line); tested = skipped = 0; bad = []
    for ch in chains(r["solution_km"]):
        parts = split(ch)
        if len(parts) >= 2 and re.fullmatch(r"\s*(f|g|h|y)('|'')?\(?[^=]*\)?\s*", parts[0]) and "\\frac" not in parts[0] and re.search(r"\([a-z]\)|^\s*y", parts[0]): parts = parts[1:]
        for a, b in zip(parts, parts[1:]):
            if not a.strip() or not b.strip(): continue
            if "\\infty" in a + b or "\\Delta" in a + b or "\\alpha" in a + b or "'" in a + b or "z" in a + b: skipped += 1; continue
            try:
                signal.alarm(4); okk = 0
                la, lb = re.search(r"\\lim_\{x\\to\s*(-?\d+)(?:\^[-+])?\}", a), re.search(r"\\lim_\{x\\to\s*(-?\d+)(?:\^[-+])?\}", b)
                pts = (0.37, 1.73, 2.41)
                if bool(la) != bool(lb): pts = (int((la or lb)[1]) + 1e-7,)
                for v in pts:
                    A, B = val(a, v), val(b, v)
                    if A != A or B != B: raise ValueError
                    if abs(A - B) > 1e-4 * max(1, abs(A)): bad.append((r["id"], a[:70], b[:70])); break
                tested += 1
            except BaseException: skipped += 1
            finally: signal.alarm(0)
    return tested, skipped, bad
if __name__ == "__main__":
    for p in sys.argv[1:]:
        L = open(p, encoding="utf-8").read().splitlines()
        with Pool(6) as pool: res = pool.map(row, L, chunksize=40)
        bad = [b for _, _, x in res for b in x]
        print(p, "rows", len(L), "printed steps tested", sum(t for t, _, _ in res), "skipped", sum(s for _, s, _ in res), "mismatches", len(bad), "rows", len({b[0] for b in bad}))
        for b in bad[:20]: print("  ", b)
