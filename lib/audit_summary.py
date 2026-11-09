"""Usage: audit_summary.py <file.jsonl>. Count audit failures by family, without editing anything."""
import json, sys
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, "lib")
from verify import audit
def one(l):
    r = json.loads(l); return r["subtopic"], audit(r)
if __name__ == "__main__":
    L = open(sys.argv[1], encoding="utf-8").read().splitlines()
    with Pool(8) as p: res = p.map(one, L, chunksize=40)
    c = Counter(); ex = {}
    for s, e in res:
        for k in e:
            key = (s, k.split(":")[0] + ":" + (k.split(":")[1][:22] if ":" in k else "")); c[key] += 1; ex.setdefault(key, k[:170])
    print(sys.argv[1], "rows", len(L), "failed", sum(1 for _, e in res if e))
    for k, v in c.most_common(25): print(v, k, ex[k])
