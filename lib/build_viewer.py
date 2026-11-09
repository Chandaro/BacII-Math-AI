"""Rebuild the viewer data from every chapter file in dataset/."""
import json, os
files = {"derivative": "dataset/derivative_km.jsonl", "complex": "dataset/complex_km.jsonl", "limit": "dataset/limit_km.jsonl", "integral": "dataset/integral_km.jsonl", "diffeq": "dataset/diffeq_km.jsonl", "probability": "dataset/probability_km.jsonl"}
out = []
for ch, p in files.items():
    if not os.path.exists(p): continue
    for l in open(p, encoding="utf-8"):
        r = json.loads(l)
        out.append({"id": r["id"], "c": ch, "gr": r.get("grade"), "x": r.get("exam_fit"), "t": r["topic"], "s": r["subtopic"], "d": r["difficulty"], "p": r["problem_km"], "a": r["solution_km"],
                    "f": r["answer_latex"], "h": "hand" in r["provenance"]["generator"],
                    "g": [{"k": d["type"], "l": d.get("latex", ""), "i": d.get("image"), "c": d.get("alt_km", "")} for d in r["diagrams"]]})
with open("dataset/preview_assets/data.js", "w", encoding="utf-8") as f:
    f.write("window.ROWS=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";")
print(len(out))
