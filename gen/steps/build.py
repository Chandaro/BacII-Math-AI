"""Write out/steps_km.jsonl from all step families. Deterministic."""
import importlib, json, os, sys
sys.path.insert(0, "gen/steps")
from core import family
rows = []
for j, name in enumerate(("derivative", "complex", "limit")):
    m = importlib.import_module(name)
    for i, (fn, n) in enumerate(m.ALL):
        n = int(n * float(os.environ.get("SCALE", "1")))
        r = family(fn, n, 7000 + 100 * j + i); rows += r; print(name, fn.__name__, len(r))
os.makedirs("out", exist_ok=True)
with open("out/steps_km.jsonl", "w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("rows", len(rows))
