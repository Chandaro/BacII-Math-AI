"""Usage: build_new.py <integral|diffeq|probability>. Writes out/<chapter>/steps.jsonl. Deterministic."""
import collections, importlib, json, sys, traceback
sys.path.insert(0, "gen/steps")
from core import family
name = sys.argv[1]; m = importlib.import_module(name); rows = []; err = collections.Counter()
def safe(fn):
    def g(rng):
        try: return fn(rng)
        except (AssertionError, ZeroDivisionError, TypeError, ValueError, AttributeError, sp_err) as e:
            err[fn.__name__ + ":" + type(e).__name__ + ":" + str(e)[:80]] += 1; return None
    g.__name__ = fn.__name__; return g
sp_err = Exception
SCALE = float(__import__("os").environ.get("SCALE", "1"))
for i, (fn, n) in enumerate(m.ALL):
    n = int(n * SCALE)
    r = family(safe(fn), n, 9000 + i); rows += r; print(getattr(fn, "__name__", "?"), len(r), "of", n, flush=True)
if hasattr(m, "finish"): rows = m.finish(rows)
with open(f"out/{name}/steps.jsonl", "w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("rows", len(rows)); print(err.most_common(15))
