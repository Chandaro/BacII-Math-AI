"""Build training-ready files in dataset/training/. Deterministic. See dataset/training/README.md."""
import json, os, random, re
from collections import Counter, defaultdict
SEED, SKEL_CAP, FAMILY_CAP, TEXTBOOK_SHARE, HAND_WEIGHT, HOLD, HAND_TEST, VAL, PILOT = 2026, 2, 80, 0.15, 3, 0.08, 0.15, 0.03, 2500
SYSTEM = "អ្នកជាជំនួយការគណិតវិទ្យា ។ ចូរដោះស្រាយលំហាត់ជាភាសាខ្មែរ ជាជំហានៗ តាមទម្រង់ប្រឡងបាក់ឌុប ហើយសរសេរគណិតវិទ្យាជា LaTeX ។"
rng = random.Random(SEED)
rows = []
for ch in ("derivative", "complex", "limit"):
    for l in open(f"dataset/{ch}_km.jsonl", encoding="utf-8"):
        rows.append(json.loads(l))
is_hand = lambda r: "hand" in r["provenance"]["generator"]
mask = lambda t: re.sub(r"\d+", "0", re.sub(r"\$\$?.*?\$\$?", "#", t, flags=re.S))
ws = lambda t: re.sub(r"\s+", "", t)
for r in rows:
    r["_ps"], r["_ss"] = ws(mask(r["problem_km"])), ws(mask(r["solution_km"]))
    r["_fam"] = (r["chapter"], r["topic"], r["subtopic"])

def to_chat(r):
    user = r["problem_km"] + "".join("\n\n```latex\n" + d["latex"] + "\n```" for d in r["diagrams"] if d.get("in_problem"))
    ans = r["solution_km"]; have = ws(ans); dup = 0
    for d in r["diagrams"]:
        if d["type"] in ("variation_table", "sign_table") and not d.get("in_problem"):
            if ws(d["latex"]) in have: dup += 1
            else: ans += "\n\n$$" + d["latex"] + "$$"
    return {"id": r["id"], "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}, {"role": "assistant", "content": ans}]}
stats = Counter()

# 1. Hold out whole template families per topic.
fam = defaultdict(list)
for r in rows:
    if not is_hand(r): fam[r["_fam"]].append(r)
held = set()
by_topic = defaultdict(list)
for k, v in fam.items(): by_topic[k[1]].append((k, len(v)))
for topic, items in sorted(by_topic.items()):
    total = sum(n for _, n in items); taken = 0
    items = sorted(items); rng.shuffle(items)
    for k, n in items:
        if n < 8 or n > 0.05 * total + 20: continue
        if taken >= HOLD * total: break
        held.add(k); taken += n
test_unseen = [r for r in rows if r["_fam"] in held]
rest = [r for r in rows if r["_fam"] not in held]
tskel = {r["_ss"] for r in test_unseen} | {r["_ps"] for r in test_unseen}
before = len(rest)
rest = [r for r in rest if r["_ss"] not in tskel and r["_ps"] not in tskel]
stats["removed_shared_wording_with_test"] = before - len(rest)

# 2. Hand-written test set.
hand = sorted([r for r in rest if is_hand(r)], key=lambda r: r["id"]); rng.shuffle(hand)
n = int(len(hand) * HAND_TEST); test_hand, hand_train = hand[:n], hand[n:]
gen = [r for r in rest if not is_hand(r)]

# 3. Cap templates.
rng.shuffle(gen); sk, fc, capped = Counter(), Counter(), []
for r in gen:
    if sk[r["_ss"]] >= SKEL_CAP: stats["cut_same_solution_pattern"] += 1; continue
    if fc[r["_fam"]] >= FAMILY_CAP: stats["cut_family_cap"] += 1; continue
    sk[r["_ss"]] += 1; fc[r["_fam"]] += 1; capped.append(r)

# 4. Limit textbook-style rows.
tb = [r for r in capped if r.get("exam_fit") == "textbook"]; ex = [r for r in capped if r.get("exam_fit") != "textbook"]
keep = int(TEXTBOOK_SHARE / (1 - TEXTBOOK_SHARE) * (len(ex) + len(hand_train)))
stats["cut_textbook_share"] = max(0, len(tb) - keep); capped = ex + tb[:keep]

# 5. Validation by whole solution pattern.
g = defaultdict(list)
for r in capped: g[r["_ss"]].append(r)
keys = sorted(g); rng.shuffle(keys); val, n = [], 0
vk = set()
for k in keys:
    if n >= VAL * len(capped): break
    vk.add(k); val += g[k]; n += len(g[k])
vp = {r["_ps"] for r in val}
train_gen = [r for r in capped if r["_ss"] not in vk and r["_ps"] not in vp]
stats["removed_shared_wording_with_val"] = len(capped) - len(val) - len(train_gen)

held_q = {r["_ps"] for r in val + test_hand + test_unseen}
n0 = len(train_gen) + len(hand_train)
train_gen = [r for r in train_gen if r["_ps"] not in held_q]
hand_train = [r for r in hand_train if r["_ps"] not in held_q]
stats["removed_same_question_wording_as_heldout"] = n0 - len(train_gen) - len(hand_train)
train = train_gen + hand_train * HAND_WEIGHT
rng.shuffle(train)
out = "dataset/training"; os.makedirs(out, exist_ok=True)
def w(name, rs, meta=False):
    with open(f"{out}/{name}", "w", encoding="utf-8") as f:
        for r in rs:
            o = to_chat(r)
            if meta: o.update(chapter=r["chapter"], topic=r["topic"], subtopic=r["subtopic"], difficulty=r["difficulty"], answer_latex=r["answer_latex"])
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
w("train.jsonl", train); w("val.jsonl", val)
w("test_unseen_templates.jsonl", test_unseen, True); w("test_handwritten.jsonl", test_hand, True)
# Pilot: balanced over chapters, keeps all weighted hand rows that fit.
pc = defaultdict(list)
for r in train: pc[r["chapter"]].append(r)
pilot = []
for c, v in pc.items(): pilot += v[:PILOT // 3 + 1]
rng.shuffle(pilot); w("train_pilot.jsonl", pilot[:PILOT])
for r in {x["id"]: x for x in train}.values():
    have = ws(r["solution_km"])
    stats["tables_kept_once_not_repeated"] += sum(1 for d in r["diagrams"] if d["type"] in ("variation_table", "sign_table") and ws(d["latex"]) in have)
L = sorted(len(to_chat(r)["messages"][2]["content"]) for r in train)
rep = {"seed": SEED, "settings": {"solution_pattern_cap": SKEL_CAP, "family_cap": FAMILY_CAP, "textbook_share_max": TEXTBOOK_SHARE, "hand_weight": HAND_WEIGHT},
       "source_rows": len(rows), "train_rows": len(train), "train_unique_rows": len({r["id"] for r in train}), "train_hand_unique": len(hand_train),
       "train_pilot": min(PILOT, len(pilot)), "val": len(val), "test_unseen_templates": len(test_unseen), "test_handwritten": len(test_hand),
       "held_out_families": len(held), "pipeline": dict(stats),
       "train_by_chapter": Counter(r["chapter"] for r in train), "test_by_chapter": Counter(r["chapter"] for r in test_unseen),
       "train_exam_fit": Counter(r.get("exam_fit", "untagged_derivative") for r in train),
       "answer_chars_p50_p95_max": [L[len(L) // 2], L[int(len(L) * .95)], L[-1]]}
json.dump(rep, open(f"{out}/split_report.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=0))
