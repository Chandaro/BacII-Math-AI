"""Usage: merge_chapter.py <chapter>. Merge out/<chapter>/*.jsonl into dataset/<chapter>_km*.jsonl."""
import glob, hashlib, json, os, re, shutil, subprocess, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from verify import audit
ch = sys.argv[1]
norm = lambda t: re.sub(r"\s+", "", t)
def mkey(r):
    return r["subtopic"] + "|" + norm("|".join(re.findall(r"\$\$?(.+?)\$\$?", r["problem_km"], flags=re.S)))
rows, seen, ms, st, bad_log = [], set(), set(), Counter(), []
def tidy_math(fr):
    if "\\begin" in fr: return fr
    fr, a = re.subn(r"(?<![\\{_^a-zA-Z])i(\d)", lambda m: "i\\cdot " + m.group(1), fr)
    fr, b = re.subn(r"(?<![\d.{^_\\])1(?=[a-zA-Z](?![a-zA-Z]))", "", fr)
    fr, c = re.subn(r"\\frac\{([^{}+\-]+)\}\{1\}", lambda m: m.group(1), fr)
    st["math_tidied"] += a + b + c
    return fr
def tidy(t):
    return re.sub(r"\$\$(.+?)\$\$|\$([^$]+?)\$", lambda m: "$$" + tidy_math(m.group(1)) + "$$" if m.group(1) is not None else "$" + tidy_math(m.group(2)) + "$", t, flags=re.S)
FIG = re.compile(r"ក្រាបខាងក្រោម|ក្រាបខាងលើ|រូបខាងក្រោម|រូបខាងលើ")
def bar(t):
    """Excluded x=0 with an infinite limit needs the double bar in a variation table."""
    def one(m):
        a = m.group(0)
        if not re.search(r"\nx & 0 ", a) or "\\|" in a or not re.search(r"\(x\) & [+-]\\infty & ", a): return a
        st["tables_given_double_bar"] += 1
        a = re.sub(r"'\(x\) &  & ", lambda _: "'(x) & \\| & ", a, count=1)
        return re.sub(r"\(x\) & ([+-]\\infty) & ", lambda k: "(x) & \\|\\," + k.group(1) + " & ", a, count=1)
    return re.sub(r"\\begin\{array\}.*?\\end\{array\}", one, t, flags=re.S)
for p in sorted(glob.glob(f"out/{ch}/*.jsonl")):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line); st["read"] += 1
        r["problem_km"], r["solution_km"], r["answer_latex"] = tidy(r["problem_km"]), tidy(r["solution_km"]), tidy_math(r["answer_latex"])
        if ch == "derivative":
            r["solution_km"] = bar(r["solution_km"])
            for d in r["diagrams"]:
                d["latex"] = bar(d["latex"])
                if FIG.search(r["problem_km"]) and d["type"] in ("graph", "figure"): d["in_problem"] = True
            if r["topic"] == "applications": r["exam_fit"] = "textbook"
        e = audit(r)
        if e:
            st["failed_audit"] += 1; bad_log.append((r["id"], e[:2])); continue
        k = hashlib.sha1(norm(r["problem_km"]).encode()).hexdigest(); m = mkey(r)
        if k in seen:
            st["exact_dup"] += 1; continue
        if m in ms and len(m) > 30:
            st["math_dup"] += 1; continue
        seen.add(k); ms.add(m); r["marks"] = None; rows.append(r)
tmp = f"dataset/.{ch}.tmp.jsonl"
with open(tmp, "w", encoding="utf-8") as fh:
    for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
badf = f"dataset/.{ch}.bad"
print(subprocess.run(["node", "lib/katex_check.js", tmp, badf], capture_output=True, text=True).stdout[:600])
bad = set(open(badf).read().split()); st["failed_katex"] = len(bad)
rows = [r for r in rows if r["id"] not in bad]
os.remove(tmp); os.remove(badf)
def boxed(s):
    out = []; i = 0
    while True:
        i = s.find("\\boxed{", i)
        if i < 0: return out
        j = i + 7; d = 1
        while j < len(s) and d:
            if s[j] == "\\": j += 2; continue
            d += (s[j] == "{") - (s[j] == "}"); j += 1
        out.append(s[i + 7:j - 1]); i = j
for r in rows:
    b = list(dict.fromkeys(boxed(r["solution_km"])))
    if len(b) > 1: r["answer_latex"] = ";\\ ".join(b)
    r.setdefault("exam_fit", "bacii_seen")
    if "textbook" in r["subtopic"]: r["exam_fit"] = "textbook"
def diag(r):
    return "".join("\n\n$$" + d["latex"] + "$$" if d["type"] in ("variation_table", "sign_table") else "\n\n```latex\n" + d["latex"] + "\n```" for d in r["diagrams"] if not d.get("in_problem"))
def ask(r):
    return r["problem_km"] + "".join("\n\n```latex\n" + d["latex"] + "\n```" for d in r["diagrams"] if d.get("in_problem"))
with open(f"dataset/{ch}_km.jsonl", "w", encoding="utf-8") as a, open(f"dataset/{ch}_km_chat.jsonl", "w", encoding="utf-8") as b:
    for r in rows:
        a.write(json.dumps(r, ensure_ascii=False) + "\n")
        b.write(json.dumps({"messages": [{"role": "user", "content": ask(r)}, {"role": "assistant", "content": r["solution_km"] + diag(r)}], "id": r["id"]}, ensure_ascii=False) + "\n")
n = 0
for r in rows:
    for d in r["diagrams"]:
        if d.get("image"): shutil.copy(d["image"], "dataset/" + d["image"]); n += 1
s = {"rows": len(rows), "pipeline": dict(st), "by_topic": Counter(r["topic"] for r in rows), "by_grade": Counter(r["grade"] for r in rows), "by_exam_fit": Counter(r["exam_fit"] for r in rows),
     "by_difficulty": Counter(r["difficulty"] for r in rows), "with_diagram": sum(bool(r["diagrams"]) for r in rows), "png_files": n,
     "diagram_types": Counter(d["type"] for r in rows for d in r["diagrams"]),
     "hand_written": sum("hand" in r["provenance"]["generator"] for r in rows), "avg_solution_chars": round(sum(len(r["solution_km"]) for r in rows) / max(1, len(rows)))}
json.dump(s, open(f"dataset/summary_{ch}.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(s, ensure_ascii=False)); print(bad_log[:8])
