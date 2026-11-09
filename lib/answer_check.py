"""Final-answer check for chat. check(question, answer) -> {"status", "source", "expected"}.
status: match | partial | mismatch | unchecked.
1. Dataset lookup: if the question is one of the verified dataset or test rows, the model's boxed answers are compared
   with the stored answer, part by part, with SymPy.
2. Otherwise, for one-part questions that ask for a definite integral, a limit, a derivative or a primitive, SymPy
   computes the answer itself.
Anything else is "unchecked": the check never guesses."""
import glob, json, random, re, signal
import sympy as sp
from sympy.parsing.latex import parse_latex

x, y = sp.symbols("x y")
KH = re.compile(r"[\u1780-\u17FF]+")
_index = None

def norm_q(q):
    return re.sub(r"[\s\u17d4\u17d5.,:;!?()\[\]{}$\\]+", "", q).lower()

def index():
    global _index
    if _index is None:
        _index = {}
        for f in glob.glob("dataset/*_km.jsonl"):
            for l in open(f, encoding="utf-8"):
                r = json.loads(l)
                if r.get("answer_latex"): _index.setdefault(norm_q(r["problem_km"]), r["answer_latex"])
        for f in ("finetune/test60.jsonl", "finetune/test60b.jsonl", "finetune/test60c.jsonl"):
            for l in open(f, encoding="utf-8"):
                r = json.loads(l)
                if r.get("answer_latex"): _index[norm_q(r["messages"][1]["content"])] = r["answer_latex"]
    return _index

def boxed(t):
    out, i = [], 0
    while (i := t.find("\\boxed{", i)) >= 0:
        j, d = i + 7, 1
        while j < len(t) and d:
            d += {"{": 1, "}": -1}.get(t[j], 0); j += 1
        out.append(t[i + 7:j - 1]); i = j
    return out

CONCL = re.compile(r"ដូចនេះ|ដូច្នេះ|សរុបមក|ចម្លើយ|Therefore|So ")
def final_math(t):
    """Boxed answers, plus the math on conclusion lines (most answers end parts with a ដូចនេះ line instead of a box)."""
    out = boxed(t)
    for line in t.splitlines():
        if CONCL.search(line) and "\\boxed" not in line:
            out += re.findall(r"\$\$?(.+?)\$\$?", line)
    out += re.findall(r"\$\$?(.+?)\$\$?", t)[-3:]   # the last few formulas of the answer
    return [(boxed(m) or [m])[0] for m in out]

def split_top(s, seps):
    parts, d, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c in "({[": d += 1
        elif c in ")}]": d -= 1
        hit = next((p for p in seps if d == 0 and s.startswith(p, i)), None)
        if hit: parts.append(cur); cur = ""; i += len(hit); continue
        cur += c; i += 1
    return parts + [cur]

def clean(s):
    s = re.sub(r"\\text\{[^}]*\}|\\mathrm\{[^}]*\}", " ", s)
    s = KH.sub(" ", s)
    for a, b in ((r"\left", ""), (r"\right", ""), (r"\dfrac", r"\frac"), (r"\tfrac", r"\frac"), (r"\displaystyle", ""),
                 (r"\,", " "), (r"\;", " "), (r"\!", ""), (r"\ ", " "), ("^{\\circ}", "*\\pi/180"), ("^\\circ", "*\\pi/180"), ("\\%", "/100"), ("\\cdot", "*")):
        s = s.replace(a, b)
    s = re.sub(r"^\s*\(?[A-Za-z]\w*'?\)?\s*:\s*", "", s)             # "(P): ..." name prefix
    s = re.sub(r"\\(?:mathbb|mathbf|operatorname)\{(\w+)\}", r"\1", s)
    s = re.sub(r"\s*\+\s*[cCk]\s*$", "", s.strip())          # constant of integration
    return s.strip().rstrip(".។").strip()

def to_sym(s):
    e = parse_latex(s)
    return e.subs({sp.Symbol("e"): sp.E, sp.Symbol("i"): sp.I, sp.Symbol("pi"): sp.pi})

LABEL = re.compile(r"^[A-Za-z](?:_\{?\w+\}?)?(?:\^\{?\w+\}?)?'*(?:\(.*\))?$")
INEQ = ("<", ">", "\\le", "\\ge", "\\neq", "\\pm", "\\mp", "\\in", "\\cup")
def parts(s):
    """Answer text -> list of (kind, value). kind: val | eq | pt. Parts that cannot be read are left out."""
    out = []
    for p in split_top(clean(s), [",", ";", "\\quad", "\\qquad", "\\text{ និង }"]):
        p = split_top(p, ["\\approx"])[0].strip()
        if not p: continue
        m = re.fullmatch(r"[a-z]\s*\\geq?\s*(\d+)", p)                 # "n >= 13" for a least whole number
        if m: out.append(("val", sp.Integer(m.group(1)))); continue
        try:
            sides = split_top(p, ["="])
            if len(sides) == 2 and LABEL.match(sides[0].strip()): sides = [sides[1]]
            m = re.fullmatch(r"(?:[A-Za-z]'?_?\{?\w*\}?)?\s*\(([^()]*)[;,]([^()]*)(?:[;,]([^()]*))?\)", sides[-1].strip())
            if m:
                out.append(("pt", tuple(to_sym(g) for g in m.groups() if g is not None))); continue
            if any(t in sd for sd in sides for t in INEQ): continue
            if len(sides) == 1: out.append(("val", to_sym(sides[0])))
            else:
                if len(sides) == 2:
                    try: out.append(("eq", to_sym(sides[0]) - to_sym(sides[1])))
                    except Exception: pass
                out.append(("val", to_sym(sides[-1])))     # "long expression = value": the value
        except Exception:
            continue
    return out

VARS = set(sp.symbols("x y z t n"))
def same_val(a, b):
    ca, cb = sorted(a.free_symbols - VARS, key=str), sorted(b.free_symbols - VARS, key=str)
    if ca and len(ca) == len(cb) and set(ca) != set(cb) and len(ca) <= 3:   # arbitrary constants: c_1, c_2 vs A, B
        import itertools
        return any(_same_val(a.subs(dict(zip(ca, perm)), simultaneous=True), b) for perm in itertools.permutations(cb))
    return _same_val(a, b)

def _same_val(a, b):
    if (a.has(sp.Float) or b.has(sp.Float)) and not (a.free_symbols or b.free_symbols):   # rounded decimals
        try: return abs(complex(sp.N(a)) - complex(sp.N(b))) <= 5e-3 * max(1, abs(complex(sp.N(b))))
        except Exception: pass
    d = sp.simplify(a - b) if not (a.free_symbols or b.free_symbols) else None
    if d is not None:
        try: return abs(complex(sp.N(a - b, 30))) < 1e-7 * max(1, abs(complex(sp.N(b))))
        except Exception: return d == 0
    if a.free_symbols - b.free_symbols or b.free_symbols - a.free_symbols:
        return False
    syms = sorted(a.free_symbols | b.free_symbols, key=str); rng = random.Random(3); ok = 0
    for _ in range(30):
        v = {s: sp.Rational(rng.randint(30, 270), 100) for s in syms}
        try:
            p, q = complex(sp.N(a.subs(v))), complex(sp.N(b.subs(v)))
        except Exception:
            continue
        if abs(p - q) > 1e-6 * max(1, abs(q)): return False
        ok += 1
    return ok >= 5

def same(e, m):
    if {e[0], m[0]} == {"val", "eq"}:          # y = f(x) against  a x + b y + c = 0
        v, q = (e[1], m[1]) if e[0] == "val" else (m[1], e[1])
        return x in v.free_symbols and y not in v.free_symbols and same(("eq", y - v), ("eq", q))
    if e[0] != m[0]: return False
    if e[0] == "val": return same_val(m[1], e[1])
    if e[0] == "pt": return len(e[1]) == len(m[1]) and all(same_val(a, b) for a, b in zip(m[1], e[1]))
    # equations: equal up to a nonzero constant factor
    r = sp.simplify(m[1] / e[1]) if e[1] != 0 else None
    return r is not None and not r.free_symbols and r != 0

def verdict(exp_parts, got_parts):
    if not exp_parts or not got_parts: return "unchecked"
    hits = sum(any(same(e, g) for g in got_parts) for e in exp_parts)
    return "match" if hits == len(exp_parts) else "mismatch" if hits == 0 else "partial"

def compute(q):
    """Expected answer computed by SymPy for one-part questions, or None."""
    if re.search(r"(^|\n)\s*(?:[កខគឃង]|\d)\s*[-.)]", q): return None
    segs = re.findall(r"\$\$?(.+?)\$\$?", q, flags=re.S)
    ints = [s for s in segs if "\\int_" in s]; lims = [s for s in segs if "\\lim" in s]
    try:
        if len(ints) == 1 and not lims:
            e = to_sym(clean(split_top(ints[0], ["="])[-1] if "=" in ints[0] and "\\int" not in ints[0].split("=")[-1] else ints[0].split("=")[-1]))
            v = e.doit() if isinstance(e, sp.Integral) else None
            if v is not None and not v.has(sp.Integral): return ("value", sp.nsimplify(v) if v.is_Float else sp.simplify(v))
        if len(lims) == 1 and not ints:
            e = to_sym(clean(lims[0].split("=")[-1] if "\\lim" in lims[0].split("=")[-1] else lims[0]))
            v = e.doit() if isinstance(e, sp.Limit) else None
            if v is not None and not v.has(sp.Limit): return ("value", v)
        fx = [s for s in segs if re.match(r"\s*[fgh]\s*\(\s*x\s*\)\s*=", s)]
        if len(fx) == 1 and not ints and not lims:
            f = to_sym(clean(fx[0].split("=", 1)[1]))
            only = not re.search(r"ហើយ|រួច|សង់|តារាង|បរមា|សមីការ|បន្ទាត់|ប៉ះ", q)
            if re.match(r"\s*(?:ចូរ)?(?:គណនា|រក)ដេរីវេ", q) and only: return ("value", sp.diff(f, x))
            if re.match(r"\s*(?:ចូរ)?(?:គណនា|រក)ព្រីមីទីវ", q) and only: return ("primitive", f)
    except Exception:
        return None
    return None

def _alarm(*a): raise TimeoutError()

def check(question, answer, seconds=6):
    """Never raises. Runs on the main thread (uses SIGALRM for a time limit)."""
    old = signal.signal(signal.SIGALRM, _alarm); signal.alarm(seconds)
    try:
        got = [p for b in final_math(answer) for p in parts(b)]
        exp = index().get(norm_q(question))
        if exp and exp.strip().lower() not in ("yes", "no"):
            st = verdict(parts(exp), got)
            return {"status": st, "source": "dataset", "expected": exp}
        c = compute(question)
        if c is None or not got: return {"status": "unchecked", "source": None, "expected": None}
        kind, v = c
        if kind == "value":
            return {"status": verdict([("val", v)], got), "source": "sympy", "expected": sp.latex(v)}
        vals = [g[1] for g in got if g[0] == "val"]
        ok = any(same_val(sp.diff(w, x), v) for w in vals)
        return {"status": "match" if ok else "mismatch" if vals else "unchecked", "source": "sympy", "expected": "F'(x)=" + sp.latex(v)}
    except Exception:
        return {"status": "unchecked", "source": None, "expected": None}
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, old)
