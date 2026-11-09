"""Complex numbers in geometry (Grade 11 Advanced ch. 7 lesson 4). Writes out/complex/geometry.jsonl.
Part 1 helpers, part 2 parametric families (cg_families.py), part 3 hand rows (complex_geometry_hand.py)."""
import sys, os, glob, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib")); sys.path.insert(0, HERE)
from common import *
from cg_core import *
import cg_families, complex_geometry_hand

def main():
    for f in glob.glob(os.path.join(ROOT, "diagrams", "complex_geometry-*.png")):
        os.remove(f)
    hand = complex_geometry_hand.rows()
    gen = cg_families.rows()
    items, seen = [], set()
    for it in hand + gen:
        k = it["prob"]
        if k in seen: continue
        seen.add(k); items.append(it)
    # PNG budget: hand rows and exam items first, then an even sample of the rest
    order = [i for i, it in enumerate(items) if it.get("spec") and it["gen"] == "hand"]
    order += [i for i, it in enumerate(items) if it.get("spec") and it["gen"] != "hand" and it["diff"] == "bacii"][::3]
    rest = [i for i, it in enumerate(items) if it.get("spec") and it["gen"] != "hand" and it["diff"] != "bacii"]
    order += rest[::9]
    png_set = set(order[:295])
    rows = []
    sp_cmd = lambda t: re.sub(r"(\\[a-zA-Z]+)(?=\d)", lambda m_: m_.group(1) + " ", t)
    for i, it in enumerate(items):
        for k in ("prob", "sol", "ans"):
            it[k] = sp_cmd(it[k])
        r = make_row("complex_geometry", it["sub"], it["diff"], it["prob"], it["sol"], it["ans"],
                     [check(*c) for c in it["checks"]], "complex_geometry_" + it["gen"],
                     chapter="complex", grade=11)
        for k in ("problem_km", "solution_km", "answer_latex"):
            r[k] = tidy(r[k])
        r["exam_fit"] = "bacii_seen" if r["subtopic"] == "exam_trig_form_geometry" else "textbook"
        if it.get("spec"):
            d = {"type": "figure", "latex": tikz(it["spec"]), "image": None, "alt_km": it["alt"]}
            if i in png_set:
                d["image"] = png(r["id"], it["spec"])
            r["diagrams"] = [d]
        rows.append(r)
    write_jsonl(rows, "complex/geometry.jsonl")

if __name__ == "__main__":
    main()
