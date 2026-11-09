"""Printing faults the review found. Any hit is a bug in a generator. Usage: step_pattern_check.py file.jsonl"""
import json, re, sys, collections
P = {"hidden_minus": r"(?<!\\times)(?<!\\cdot)(?<!\\infty\})(?<!\\to \d\})(?<!\})[0-9a-z)]\s*\\frac\{-", "plus_minus": r"\+\s*-", "times_one_frac": r"\\frac\{-?\d+\}\{1\}", "coef_one": r"(?<![\d.{(+\-=^ ])1e\^|[=(]1x\b|-1\\left", "repeat_value": r"=(\\frac\{[^{}]+\}\{[^{}]+\})=\1(?!\S*\\)", "digit_digit": r"\d\\left\(\d+\\right\)\d", "bad_power": r"\\sqrt\{\d+\}\^", "dollar_after_khmer": r"[\u1780-\u17FF]\$\$\$", "dup_or": r"\$x=([^$]+)\$ ឬ \$x=\1\$"}
for f in sys.argv[1:]:
    c = collections.Counter(); ex = {}
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        for k, p in P.items():
            t = r["problem_km"] + "\n" + r["solution_km"]; m = re.search(p, t)
            if m: c[k] += 1; ex.setdefault(k, (r["subtopic"], t[max(0, m.start() - 50):m.end() + 40].replace("\n", " ")))
    print(f, "pattern hits", dict(c))
    for k, v in ex.items(): print("  ", k, v)
