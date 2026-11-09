"""Usage: run_test60b.py <model> <adapter|none> <name>. Resumes; 60 questions on integrals, differential equations, probability, greedy, 2,500-token limit."""
import json, os, sys, time
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
model_id, adapter = sys.argv[1:3]; name = sys.argv[3] if len(sys.argv) > 3 else model_id.split("/")[-1]; out = f"finetune/results_test60b/{name}.jsonl"
os.makedirs("finetune/results_test60b", exist_ok=True)
done = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if os.path.exists(out) else set()
rows = [json.loads(l) for l in open("finetune/test60b.jsonl", encoding="utf-8")]
t0 = time.time(); model, tok = load(model_id, adapter_path=None if adapter == "none" else adapter); print(name, "loaded", round(time.time() - t0), "s", flush=True)
sample = rows[0]["messages"][2]["content"]
ids = tok.encode(sample); print("tokens per char on a Khmer solution", round(len(ids) / len(sample), 2), flush=True)
def prompt(msgs):
    try:
        return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
for i, r in enumerate(rows):
    if r["id"] in done: continue
    p = prompt(r["messages"][:2]); t = time.time()
    a = generate(model, tok, prompt=p, max_tokens=2500, sampler=make_sampler(temp=0.0))
    dt = time.time() - t; n = len(tok.encode(a))
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": r["id"], "model": name, "answer": a, "tokens": n, "seconds": round(dt, 1), "hit_limit": n >= 2490}, ensure_ascii=False) + "\n")
    print(i + 1, len(rows), n, "tokens", round(n / dt, 1), "tok/s", flush=True)
