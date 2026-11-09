"""Merge verified topic files, drop duplicates, export training files and stats."""
import glob, hashlib, json, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from verify import audit

def norm(t):
    t = re.sub(r"\s+", "", t)
    return t
def math_key(r):
    """Same math in a different wording counts as a duplicate."""
    ms = re.findall(r"\$\$?(.+?)\$\$?", r["problem_km"], flags=re.S)
    return r["topic"] + "|" + r["subtopic"] + "|" + norm("|".join(ms))

rows, seen, mseen = [], set(), set()
stats = Counter()
for p in sorted(glob.glob("out/*.jsonl")):
    b = os.path.basename(p)
    if b.startswith("pilot") or b.startswith("dataset") or b.startswith("train"):
        continue
    for line in open(p, encoding="utf-8"):
        r = json.loads(line); stats["read"] += 1
        if audit(r):
            stats["failed_audit"] += 1; continue
        k = hashlib.sha1(norm(r["problem_km"]).encode()).hexdigest()
        mk = math_key(r)
        if k in seen:
            stats["exact_dup"] += 1; continue
        if mk in mseen and len(mk) > 30:
            stats["math_dup"] += 1; continue
        seen.add(k); mseen.add(mk); rows.append(r)

os.makedirs("dataset", exist_ok=True)
with open("dataset/derivative_km.jsonl", "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
def diag(r):
    return "".join("\n\n$$" + d["latex"] + "$$" if d["type"] in ("variation_table", "sign_table") else "\n\n```latex\n" + d["latex"] + "\n```" for d in r["diagrams"])
with open("dataset/derivative_km_chat.jsonl", "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps({"messages": [
            {"role": "user", "content": r["problem_km"]},
            {"role": "assistant", "content": r["solution_km"] + diag(r)}], "id": r["id"]}, ensure_ascii=False) + "\n")
summary = {"rows": len(rows), "pipeline": dict(stats),
           "by_topic": Counter(r["topic"] for r in rows), "by_difficulty": Counter(r["difficulty"] for r in rows),
           "with_diagram": sum(bool(r["diagrams"]) for r in rows),
           "with_png": sum(any(d.get("image") for d in r["diagrams"]) for r in rows),
           "avg_solution_chars": round(sum(len(r["solution_km"]) for r in rows) / max(1, len(rows)))}
json.dump(summary, open("dataset/summary.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
