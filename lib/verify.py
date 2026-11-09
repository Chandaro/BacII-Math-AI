"""Independent row checker. Usage: python lib/verify.py out/file.jsonl [...]
Recomputes every claim and audits Khmer, LaTeX and structure. Failing rows go to out/rejected/."""
import json, os, random, re, signal, sys
from collections import Counter
import sympy as sp

x = sp.Symbol("x", real=True)
NS = {"x": x, "oo": sp.oo, "E": sp.E, "pi": sp.pi, "ln": sp.log, "log": sp.log, "sqrt": sp.sqrt,
      "exp": sp.exp, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "diff": sp.diff,
      "limit": sp.limit, "Rational": sp.Rational, "Abs": sp.Abs, "asin": sp.asin, "acos": sp.acos,
      "integrate": sp.integrate, "binomial": sp.binomial, "atan": sp.atan, "atan2": sp.atan2, "I": sp.I, "re": sp.re, "im": sp.im, "conjugate": sp.conjugate,
      "arg": sp.arg, "expand": sp.expand, "factorial": sp.factorial, "floor": sp.floor, "solve": sp.solve, "simplify": sp.simplify, "subs": lambda e, a, b: e.subs(a, b)}
def nint_abs(f, a, b):
    """Numeric integral of |f| on [a,b], split into small pieces so sign changes are handled."""
    import mpmath
    g = sp.lambdify(x, f, "mpmath"); a, b = float(a), float(b)
    return sp.Float(mpmath.quad(lambda t: abs(g(t)), sorted(set(mpmath.linspace(a, b, 41)) | {mpmath.mpf(i) for i in range(int(a), int(b) + 1) if a <= i <= b})), 25)
NS["nint_abs"] = nint_abs
KHMER = re.compile(r"[\u1780-\u17FF]")
REQUIRED = ["id", "chapter", "topic", "subtopic", "difficulty", "problem_km", "solution_km",
            "answer_latex", "diagrams", "checks", "provenance"]

class CheckTimeout(Exception):
    pass
def _alarm(*a):
    raise CheckTimeout()
signal.signal(signal.SIGALRM, _alarm)

def equal(lhs, rhs):
    a, b = sp.sympify(lhs, locals=NS), sp.sympify(rhs, locals=NS)
    if a == b:
        return True
    d = a - b
    if sp.expand(d) == 0:
        return True
    if d.is_number and d.has(sp.Float):
        return abs(float(d)) < 1e-8
    if d.free_symbols:
        rng = random.Random(7); ok = 0
        for _ in range(40):
            v = sp.Rational(rng.randint(-4000, 4000) if _ % 2 else rng.randint(1, 40000), 997)
            try:
                va, vb = complex(a.subs(x, v).evalf()), complex(b.subs(x, v).evalf())
            except Exception:
                continue
            if va != va or vb != vb or abs(va.imag) > 1e-9 or abs(vb.imag) > 1e-9:
                continue
            if abs(va - vb) > 1e-7 * max(1, abs(va)):
                return False
            ok += 1
        return ok >= 8
    return sp.simplify(d) == 0

def strip_math(t):
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    return re.sub(r"\$.*?\$", " ", t, flags=re.S)

def braces_ok(t):
    depth = 0; i = 0
    while i < len(t):
        c = t[i]
        if c == "\\":
            i += 2; continue
        depth += (c == "{") - (c == "}")
        if depth < 0:
            return False
        i += 1
    return depth == 0

def audit(r):
    errs = [f"missing:{k}" for k in REQUIRED if k not in r]
    if errs:
        return errs
    for f in ("problem_km", "solution_km"):
        t = r[f]
        if len(KHMER.findall(t)) < 12:
            errs.append(f"{f}:too_little_khmer")
        if t.replace("$$", "").count("$") % 2:
            errs.append(f"{f}:unbalanced_dollar")
        if not braces_ok(t):
            errs.append(f"{f}:unbalanced_brace")
        out = strip_math(t)
        if re.search(r"[A-Za-z]{2,}", out):
            errs.append(f"{f}:latin_outside_math:{re.search(r'[A-Za-z]{2,}', out).group()}")
        if re.search(r"[\\^_=]", out):
            errs.append(f"{f}:math_outside_dollars")
        if re.search(r"\u200b\u200b|\ufffd", t):
            errs.append(f"{f}:bad_char")
        if re.search(r"\b(sp\.|sympy|None|nan|zoo)\b", t):
            errs.append(f"{f}:code_leak")
    if not r["checks"]:
        errs.append("no_checks")
    for c in r["checks"]:
        try:
            signal.alarm(20)
            if not equal(c["lhs"], c["rhs"]):
                errs.append(f"check_failed:{c['lhs']} != {c['rhs']}")
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            errs.append(f"check_error:{c.get('lhs')}:{type(e).__name__}")
        finally:
            signal.alarm(0)
    for d in r["diagrams"]:
        if d.get("image") and not os.path.exists(d["image"]):
            errs.append(f"missing_image:{d['image']}")
        if not d.get("latex"):
            errs.append("diagram_without_latex")
    return errs

def main(paths):
    os.makedirs("out/rejected", exist_ok=True)
    total = 0; bad = 0; why = Counter()
    for p in paths:
        keep = []; rej = []
        for line in open(p, encoding="utf-8"):
            r = json.loads(line); total += 1
            e = audit(r)
            if e:
                bad += 1; r["_errors"] = e; rej.append(r)
                why.update(k.split(":")[0] + ":" + k.split(":")[1] if ":" in k else k for k in e)
            else:
                keep.append(r)
        base = os.path.basename(p)
        with open(f"out/rejected/{base}", "w", encoding="utf-8") as fh:
            for r in rej:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{base}: {len(keep)} pass, {len(rej)} fail")
    print(f"TOTAL {total} rows, {bad} failed"); print(why.most_common(15))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
