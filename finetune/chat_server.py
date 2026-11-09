"""Local chat for the Khmer math models. Serves dataset/ and /api/chat on 127.0.0.1:8800.
All model work runs on the main thread; HTTP handlers only pass messages through queues."""
import json, os, queue, threading, time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler

PORT = 8800; G = "mlx-community/gemma-3-12b-it-qat-4bit"; MAX = 2500
SYS = "អ្នកជាជំនួយការគណិតវិទ្យា ។ ចូរដោះស្រាយលំហាត់ជាភាសាខ្មែរ ជាជំហានៗ តាមទម្រង់ប្រឡងបាក់ឌុប ហើយសរសេរគណិតវិទ្យាជា LaTeX ។"
INS = "ខាងក្រោមជាលំហាត់ និងសេចក្តីព្រាងដំណោះស្រាយ ។ ចូរសរសេរដំណោះស្រាយនេះឡើងវិញជាភាសាខ្មែរ តាមទម្រង់ប្រឡងបាក់ឌុប ។ រក្សាគ្រប់ជំហាន រូបមន្ត លេខ និងចម្លើយចុងក្រោយឱ្យនៅដដែល ។ កុំគណនាថ្មី និងកុំប្តូរលទ្ធផល ។"
ADAPTERS = {"base": None, "run8": "finetune/adapters/run8-step2400-half"}
MODELS = ["two_step", "run8", "base"]
jobs = queue.Queue(); loaded = {}; drafts = {}; current = None

class Job:
    def __init__(s, key, msgs): s.key, s.msgs, s.out, s.stop = key, msgs, queue.Queue(), threading.Event()

def get(key, job=None):
    if key not in loaded:
        if job: job.out.put({"t": "status", "d": "loading"})
        loaded[key] = load(G, adapter_path=ADAPTERS[key])
    return loaded[key]

import re, sys
sys.path.insert(0, "lib"); from answer_check import check, index
FIX = [(r"ម៉ោង(?:ផ្ទៃក្រឡា|ការ៉េ|ការេ)", "ឯកតាផ្ទៃក្រឡា"), (r"積分", "អាំងតេក្រាល"), (r"យក\S*ារីត\S*\s*(?:ម|មក)?\s*beide\s*ខាង", "យក $\\ln$ អង្គទាំងពីរខាង"),
       (r"យក\S*ារីត\S*\s*(?:ម|មក)?\s*beide", "យក $\\ln$ អង្គទាំងពីរ"), (r"\s?beide\s?", " ទាំងពីរ "), (r"ផលបែងខិតនៃ", "បំណែងចែកប្រូបាបនៃ")]
HOLD = 40  # characters held back so a word split across tokens is fixed before it is shown

def fix(text):
    for p, r in FIX: text = re.sub(p, lambda m, r=r: r, text)
    return text

def looping(text):
    tail = text[-80:]
    return len(text) > 400 and text[-2500:].count(tail) >= 4

def run(key, msgs, job, kind):
    model, tok = get(key, job); job.out.put({"t": "status", "d": "writing" if kind == "text" else "solving"})
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    text, n, t, sent = "", 0, time.time(), 0
    def flush(final=False):
        nonlocal sent
        f = fix(text); upto = len(f) if final else max(sent, len(f) - HOLD)
        if upto > sent: job.out.put({"t": kind, "d": f[sent:upto]}); sent = upto
        return f
    for r in stream_generate(model, tok, prompt, max_tokens=MAX, sampler=make_sampler(temp=0.0)):
        if job.stop.is_set(): return flush(True), n, time.time() - t, "stopped"
        text += r.text; n += 1; flush()
        if n % 32 == 0 and looping(text): return flush(True), n, time.time() - t, "loop"
    return flush(True), n, time.time() - t, "limit" if n >= MAX else "done"

def work(job):
    system = {"role": "system", "content": SYS}; total = secs = 0
    if job.key == "two_step":
        q = job.msgs[-1]["content"]
        if q in drafts: draft = drafts[q]; job.out.put({"t": "draft", "d": draft})
        else:
            draft, n, s, why = run("base", [system, {"role": "user", "content": q}], job, "draft"); total += n; secs += s
            if why == "stopped": return total, secs, why
        msgs, key = [system, {"role": "user", "content": f"{INS}\n\nលំហាត់៖\n{q}\n\nសេចក្តីព្រាង៖\n{draft}"}], "base"
    else: msgs, key = [system] + job.msgs, job.key
    text, n, s, why = run(key, msgs, job, "text")
    if why != "stopped": job.out.put({"t": "check", **check(job.msgs[-1]["content"], text)})
    if job.key == "base" and len(job.msgs) == 1 and why != "stopped": drafts[job.msgs[0]["content"]] = text
    return total + n, secs + s, why

class H(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache"); super().end_headers()
    def local(self):
        o = self.headers.get("Origin")
        return self.headers.get("Host") in (f"localhost:{PORT}", f"127.0.0.1:{PORT}") and o in (None, f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}")
    def do_GET(self):
        if not self.local(): return self.send_error(403)
        if self.path == "/api/status":
            b = json.dumps({"loaded": list(loaded), "models": MODELS, "waiting": jobs.qsize(), "running": current.key if current else None}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); return self.wfile.write(b)
        super().do_GET()
    def do_POST(self):
        if self.path == "/api/stop" and self.local() and "application/json" in self.headers.get("Content-Type", ""):
            for j in list(jobs.queue) + ([current] if current else []): j.stop.set(); j.out.put({"t": "end", "tokens": 0, "seconds": 0, "reason": "stopped"})
            self.send_response(204); self.end_headers(); return
        if self.path != "/api/chat" or not self.local() or "application/json" not in self.headers.get("Content-Type", ""): return self.send_error(403)
        try:
            d = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 200000)))
            msgs = [{"role": m["role"], "content": str(m["content"])} for m in d["messages"] if m["role"] in ("user", "assistant")]
            assert d["model"] in MODELS and msgs and msgs[-1]["role"] == "user"
        except Exception: return self.send_error(400)
        job = Job(d["model"], msgs); jobs.put(job)
        self.send_response(200); self.send_header("Content-Type", "application/x-ndjson"); self.end_headers()
        try:
            while True:
                try: e = job.out.get(timeout=1)
                except queue.Empty: e = {"t": "ping"}
                self.wfile.write((json.dumps(e, ensure_ascii=False) + "\n").encode()); self.wfile.flush()
                if e["t"] in ("end", "error"): break
        except OSError: job.stop.set()

srv = ThreadingHTTPServer(("127.0.0.1", PORT), partial(H, directory="dataset")); srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start(); print(f"chat on http://localhost:{PORT}/chat.html", flush=True)
index(); get("run8"); print("answer check ready, Daro Dai Chav 5 loaded", flush=True)
while True:
    job = jobs.get()
    if job.stop.is_set(): continue
    current = job
    try:
        n, s, why = work(job); job.out.put({"t": "end", "tokens": n, "seconds": round(s, 1), "reason": why})
    except Exception as e:
        print("error", repr(e), flush=True); job.out.put({"t": "error", "d": repr(e)[:200]})
    current = None
