#!/bin/sh
# Dataset v2: larger step families for the six old chapters. Old files are kept in out/backup_v1/.
P=python3
echo "=== START $(date +%H:%M)"
for c in integral diffeq probability; do
  echo "=== BUILD $c $(date +%H:%M)"; SCALE=3 $P gen/steps/build_new.py $c > out/$c/build.log 2>&1 || echo "BUILD FAILED $c"
  $P lib/verify.py out/$c/steps.jsonl > out/$c/verify.log 2>&1; tail -1 out/$c/verify.log
  $P lib/merge_chapter.py $c > out/$c/merge.log 2>&1; tail -2 out/$c/merge.log | head -c 300; echo
done
echo "=== BUILD steps derivative complex limit $(date +%H:%M)"
SCALE=5 $P gen/steps/build.py > out/steps_build.log 2>&1 || echo "BUILD FAILED steps"
$P - <<'E'
import json
rows = [json.loads(l) for l in open("out/steps_km.jsonl", encoding="utf-8")]
for c in ("derivative", "complex", "limit"):
    with open(f"out/{c}/steps.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            if r["chapter"] == c: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("split", len(rows))
E
for c in derivative complex limit; do
  $P lib/verify.py out/$c/steps.jsonl > out/$c/verify.log 2>&1; tail -1 out/$c/verify.log
  $P lib/merge_chapter.py $c > out/$c/merge.log 2>&1; tail -2 out/$c/merge.log | head -c 300; echo
done
wc -l dataset/*_km.jsonl
echo "=== ALL DONE $(date +%H:%M)"
