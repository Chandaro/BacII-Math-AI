"""Check printed steps inside solutions: pure-number equalities, and f'(x)=A=B definition chains.
Usage: step_check.py <file.jsonl> ... Reports mismatches; never edits data."""
import json, re, signal, sys
from multiprocessing import Pool
import sympy as sp
from sympy.parsing.latex import parse_latex
X = sp.Symbol("x")
ALLOWED = re.compile(r"^(?:[\d\s+\-*/().,^{}=]|\\(?:frac|dfrac|sqrt|cdot|times|left|right|pi|ln|div|,|;)|\be\b|i\b)*$")
def clean(s):
    s = s.replace("\\left", "").replace("\\right", "").replace("\\dfrac", "\\frac").replace("\\,", " ").replace("\\;", " ").replace("\\times", "\\cdot")
    return s.strip().rstrip(".,;")
def val(s, x=None):
    e = parse_latex(clean(s), backend="lark")
    e = e.subs({sp.Symbol("e"): sp.E, sp.Symbol("i"): sp.I})
    if x is not None:
        e = e.subs(X, x)
    return complex(e.evalf())
class T(Exception): pass
def alarm(*a): raise T()
def frags(t):
    for m in re.finditer(r"\$\$([\s\S]+?)\$\$|\$([^$]+?)\$", t):
        yield m.group(1) or m.group(2)
def row(line):
    signal.signal(signal.SIGALRM, alarm)
    r = json.loads(line); tested = 0; bad = []
    for fr in frags(r["solution_km"]):
        if "\\begin" in fr or "\\approx" in fr or "\\neq" in fr or "<" in fr or ">" in fr or "\\Rightarrow" in fr or "\\iff" in fr or "\\Leftrightarrow" in fr or "\\boxed" in fr:
            continue
        parts = fr.split("=")
        if len(parts) < 2: continue
        chain = bool(re.match(r"^\s*[fgh](?:'|'')?\(x\)\s*$", parts[0])) and len(parts) >= 3
        if not chain and not all(ALLOWED.match(p) and p.strip() for p in parts): continue
        seq = parts[1:] if chain else parts
        for a, b in zip(seq, seq[1:]):
            try:
                signal.alarm(3)
                pts = (0.37, 1.73, 2.41) if chain else (None,)
                for v in pts:
                    A, B = val(a, v), val(b, v)
                    if A != A or B != B: raise ValueError
                    if abs(A - B) > 1e-6 * max(1, abs(A)):
                        bad.append((r["id"], fr[:110])); break
                tested += 1
            except BaseException:
                pass
            finally:
                signal.alarm(0)
    return tested, bad
if __name__ == "__main__":
    for p in sys.argv[1:]:
        lines = open(p, encoding="utf-8").read().splitlines()
        with Pool(6) as pool:
            res = pool.map(row, lines, chunksize=50)
        tested = sum(t for t, _ in res); bad = [b for _, x in res for b in x]
        print(p, "rows", len(lines), "printed steps tested", tested, "mismatches", len(bad), "rows", len({b[0] for b in bad}))
        for b in bad[:25]: print("  ", b)
