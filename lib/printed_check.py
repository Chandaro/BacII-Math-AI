"""Independent check of what is PRINTED: read the LaTeX of a question, integrate it numerically,
and compare with the LaTeX of the boxed answer. It never looks at the generator's own values.
Usage: printed_check.py dataset/integral_km.jsonl [sample]. Reports; never edits data."""
import json, random, re, signal, sys
from collections import Counter
from multiprocessing import Pool
import mpmath
import sympy as sp
from sympy.parsing.latex import parse_latex
X = sp.Symbol("x")
class T(Exception): pass
def alarm(*a): raise T()
def clean(s):
    s = s.replace("\\left", "").replace("\\right", "").replace("\\,", " ").replace("\\ln", "\\log")
    s = re.sub(r"\\log\^\{(\d+)\} x", r"(\\log(x))^{\1}", s)
    s = re.sub(r"\\log ([0-9]+)", r"\\log(\1)", s)
    s = re.sub(r"\\log x", r"\\log(x)", s)
    s = re.sub(r"\\(sin|cos|tan)\^\{(\d+)\} (\d*x)", r"(\\\1(\3))^{\2}", s)
    s = re.sub(r"\\(sin|cos|tan) (\d*x)", r"\\\1(\2)", s)
    return s
def val(s):
    e = parse_latex(clean(s), backend="lark")
    return e.subs({sp.Symbol("e"): sp.E, sp.Symbol("pi"): sp.pi})
def one(line):
    signal.signal(signal.SIGALRM, alarm)
    r = json.loads(line); m = re.search(r"\$\$I=\\int_\{(.+?)\}\^\{(.+?)\} (.+?)\\,dx\$\$", r["problem_km"]); b = re.search(r"\\boxed\{I=(.+?)\}\$ ។\s*$", r["solution_km"])
    if not m or not b: return "skip", None
    try:
        signal.alarm(6)
        a, c, f = val(m[1]), val(m[2]), val(m[3]); v = val(b[1])
        g = sp.lambdify(X, f, "mpmath"); num = mpmath.quad(g, mpmath.linspace(float(a), float(c), 9)); want = float(v.evalf())
        ok = abs(float(num) - want) < 1e-6 * max(1, abs(want))
        return ("ok" if ok else "bad"), (None if ok else (r["id"], m[3][:70], str(a), str(c), b[1][:50], float(num)))
    except BaseException as e:
        return "unparsed", None
    finally:
        signal.alarm(0)
if __name__ == "__main__":
    L = open(sys.argv[1], encoding="utf-8").read().splitlines()
    random.Random(1).shuffle(L); L = L[:int(sys.argv[2])] if len(sys.argv) > 2 else L
    with Pool(8) as p: res = p.map(one, L, chunksize=20)
    print(Counter(k for k, _ in res))
    for k, d in res:
        if k == "bad": print(d)
