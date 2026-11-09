"""Six-chapter training files in dataset/training_v2/. Deterministic.
The first three chapters keep their dataset/training/ split exactly, so no old test row can reach training.
Integrals, differential equations and probability are split here with the same steps as build_split.py.
SKEL_CAP is higher than the old value of 2: these chapters have few wording patterns, and 2 would leave
about 1,600 rows. 10 gives each new chapter about the size of the smaller old chapters."""
import glob, json, os, random, re, shutil
from collections import Counter, defaultdict
from pathlib import Path
from mlx_lm.utils import load_tokenizer

SEED, SKEL_CAP, FAMILY_CAP, TEXTBOOK_SHARE, HOLD, VAL, PILOT, MAX_TOKENS = 2027, 10, 80, 0.15, 0.08, 0.03, 2500, 2300
NEW = ("integral", "diffeq", "probability")
OLD, OUT = "dataset/training", "dataset/training_v2"
L = lambda p: [json.loads(l) for l in open(p, encoding="utf-8")]
tok = load_tokenizer(Path(glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--gemma-3-12b-it-qat-4bit/snapshots/*"))[0]))
SYSTEM = L(f"{OLD}/val.jsonl")[0]["messages"][0]["content"]
rng = random.Random(SEED)
mask = lambda t: re.sub(r"\d+", "0", re.sub(r"\$\$?.*?\$\$?", "#", t, flags=re.S))
ws = lambda t: re.sub(r"\s+", "", t)
fm = lambda t: tuple(re.findall(r"\$\$?(.*?)\$\$?", t, flags=re.S))
def ntok(r):
    t = tok.apply_chat_template(r["messages"], tokenize=True)
    return len(t["input_ids"]) if hasattr(t, "keys") else len(t)
def to_chat(r):
    ans = r["solution_km"]; have = ws(ans)
    for d in r["diagrams"]:
        if d["type"] in ("variation_table", "sign_table") and ws(d["latex"]) not in have: ans += "\n\n$$" + d["latex"] + "$$"
    return {"id": r["id"], "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": r["problem_km"]}, {"role": "assistant", "content": ans}]}

rows = [r for c in NEW for r in L(f"dataset/{c}_km.jsonl")]
stats = Counter()
for r in rows:
    r["_ps"], r["_ss"], r["_fam"] = ws(mask(r["problem_km"])), ws(mask(r["solution_km"])), (r["chapter"], r["topic"], r["subtopic"])

# 1. Hold out whole template families per topic.
fam = defaultdict(list)
for r in rows: fam[r["_fam"]].append(r)
by_topic = defaultdict(list)
for k, v in fam.items(): by_topic[k[1]].append((k, len(v)))
held = set()
for topic, items in sorted(by_topic.items()):
    if topic == "integral_volume": continue  # all volume families share one solution pattern, so holding one out removes the whole topic
    total = sum(n for _, n in items); taken = 0
    items = sorted(items); rng.shuffle(items)
    for k, n in items:
        if n < 8 or n > 0.05 * total + 20: continue
        if taken >= HOLD * total: break
        held.add(k); taken += n
test = [r for r in rows if r["_fam"] in held]
rest = [r for r in rows if r["_fam"] not in held]
# Match on solution pattern only: question openers such as "compute the integral" are shared by unrelated families.
tsk = {r["_ss"] for r in test}
n0 = len(rest); rest = [r for r in rest if r["_ss"] not in tsk]; stats["removed_shared_solution_pattern_with_test"] = n0 - len(rest)

# 2. Cap templates.
rng.shuffle(rest); sk, fc, capped = Counter(), Counter(), []
for r in rest:
    if sk[r["_ss"]] >= SKEL_CAP: stats["cut_same_solution_pattern"] += 1; continue
    if fc[r["_fam"]] >= FAMILY_CAP: stats["cut_family_cap"] += 1; continue
    sk[r["_ss"]] += 1; fc[r["_fam"]] += 1; capped.append(r)

# 3. Limit textbook-style rows.
tb = [r for r in capped if r.get("exam_fit") == "textbook"]; ex = [r for r in capped if r.get("exam_fit") != "textbook"]
keep = int(TEXTBOOK_SHARE / (1 - TEXTBOOK_SHARE) * len(ex)); stats["cut_textbook_share"] = max(0, len(tb) - keep); capped = ex + tb[:keep]

# 4. Validation by whole solution pattern.
g = defaultdict(list)
for r in capped: g[r["_ss"]].append(r)
keys = sorted(g); rng.shuffle(keys); val, n, vk = [], 0, set()
for k in keys:
    if n >= VAL * len(capped): break
    vk.add(k); val += g[k]; n += len(g[k])
vp = {r["problem_km"] for r in val}
train = [r for r in capped if r["_ss"] not in vk and r["problem_km"] not in vp]
stats["removed_shared_solution_pattern_with_val"] = len(capped) - len(val) - len(train)

# 5. Nothing that matches any test question, by wording or by formulas; nothing too long for training.
old_tests = sum((L(p) for p in (f"{OLD}/test_unseen_templates.jsonl", f"{OLD}/test_handwritten.jsonl", "finetune/test60.jsonl", "finetune/baseline_test.jsonl")), [])
hq = {r["messages"][1]["content"] for r in old_tests}; hf = {fm(q) for q in hq}
tq = {r["problem_km"] for r in test}; tf = {fm(q) for q in tq}
n0 = len(train); train = [r for r in train if r["problem_km"] not in hq | tq and fm(r["problem_km"]) not in hf | tf]; stats["removed_same_formulas_as_test"] = n0 - len(train)
n0 = len(train); train = [r for r in train if ntok(to_chat(r)) <= MAX_TOKENS]; stats["removed_too_long"] = n0 - len(train)

# 6. Write. Old chapters are copied row for row.
old_train, old_val = L(f"{OLD}/train.jsonl"), L(f"{OLD}/val.jsonl")
new_train = [to_chat(r) for r in train]
all_train = old_train + new_train; rng.shuffle(all_train)
all_val = old_val + [to_chat(r) for r in val]
def meta(r):
    o = to_chat(r); o.update(chapter=r["chapter"], topic=r["topic"], subtopic=r["subtopic"], difficulty=r["difficulty"], answer_latex=r["answer_latex"]); return o
all_test = L(f"{OLD}/test_unseen_templates.jsonl") + [meta(r) for r in test]
os.makedirs(OUT, exist_ok=True)
def w(name, rs):
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
        for r in rs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
w("train.jsonl", all_train); w("val.jsonl", all_val); w("test_unseen_templates.jsonl", all_test)
shutil.copy(f"{OLD}/test_handwritten.jsonl", f"{OUT}/test_handwritten.jsonl")
ch = {}
for c in ("derivative", "complex", "limit") + NEW:
    for r in L(f"dataset/{c}_km.jsonl"): ch[r["id"]] = c
pc = defaultdict(list)
for r in all_train: pc[ch[r["id"]]].append(r)
pilot = []
for c in sorted(pc): pilot += pc[c][:PILOT // 6 + 1]
rng.shuffle(pilot); w("train_pilot.jsonl", pilot[:PILOT])

# 7. Report and leak checks on the written files.
q = lambda rs: {r["messages"][1]["content"] for r in rs}
tr, va, te, th = L(f"{OUT}/train.jsonl"), L(f"{OUT}/val.jsonl"), L(f"{OUT}/test_unseen_templates.jsonl"), L(f"{OUT}/test_handwritten.jsonl")
extra = L("finetune/test60.jsonl") + L("finetune/baseline_test.jsonl")
T = sorted(ntok(r) for r in new_train)
rep = {"seed": SEED, "settings": {"solution_pattern_cap_new": SKEL_CAP, "family_cap": FAMILY_CAP, "textbook_share_max": TEXTBOOK_SHARE, "max_tokens": MAX_TOKENS},
       "train_rows": len(tr), "train_new_rows": len(new_train), "train_old_rows": len(old_train), "val": len(va), "test_unseen_templates": len(te), "test_handwritten": len(th), "train_pilot": min(PILOT, len(pilot)),
       "held_out_new_families": len(held), "pipeline": dict(stats),
       "train_by_chapter": Counter(ch[r["id"]] for r in tr), "val_by_chapter": Counter(ch[r["id"]] for r in va), "test_by_chapter": Counter(ch[r["id"]] for r in te),
       "new_train_by_topic": Counter(r["topic"] for r in train), "new_train_unique_solution_patterns": len({r["_ss"] for r in train}),
       "new_rows_tokens_p50_p95_max": [T[len(T) // 2], T[int(len(T) * .95)], T[-1]],
       "leaks": {"train_and_val": len(q(tr) & q(va)), "train_and_test": len(q(tr) & q(te)), "train_and_handwritten": len(q(tr) & q(th)), "train_and_test60_or_baseline": len(q(tr) & q(extra)),
                 "new_val_and_test": len(q([to_chat(r) for r in val]) & q(te))},
       "old_train_unchanged": sorted(json.dumps(r, sort_keys=True) for r in old_train) == sorted(json.dumps(r, sort_keys=True) for r in tr if ch[r["id"]] not in NEW)}
json.dump(rep, open(f"{OUT}/split_report.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=0))
