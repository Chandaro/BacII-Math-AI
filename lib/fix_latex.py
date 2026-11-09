"""Repair mechanical LaTeX joins in out/*.jsonl. Text only: never touches checks."""
import glob, json, os, re
from collections import Counter
RULES = [
 (r"\\lee(?=\^)", r"\\le e", "le_e"), (r"\\leqe(?![a-z])", r"\\leq e", "leq_e"),
 (r"\\geqe(?![a-z])", r"\\geq e", "geq_e"), (r"\\geqx(?![a-z])", r"\\geq x", "geq_x"),
 (r"\\leqx(?![a-z])", r"\\leq x", "leq_x"),
 (r"\\(max|min)([fgh])(?![a-z])", r"\\\1 \2", "maxmin"),
 (r"(?<![\w}])([a-z])\^\{(\d+)\}\^\{(\d+)\}", r"\\left(\1^{\2}\\right)^{\3}", "double_sup"),
 (r"\\iff ([^$]+?)\\iff \1(?=\$)", r"\\iff \1", "iff_repeat"),
 (r"(?<==)-1\(", r"-(", "minus_one"),
]
c = Counter()
def fix(t):
    for pat, rep, name in RULES:
        t, n = re.subn(pat, rep, t); c[name] += n
    return t
for p in glob.glob("out/*.jsonl"):
    rows = [json.loads(l) for l in open(p, encoding="utf-8")]
    for r in rows:
        for f in ("problem_km", "solution_km", "answer_latex"):
            r[f] = fix(r[f])
        for d in r["diagrams"]:
            d["latex"] = fix(d["latex"])
    with open(p, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(dict(c))
