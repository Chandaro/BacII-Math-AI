import random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from common import *
rng = random.Random(1)
rows = []
for _ in range(30):
    a, b, c = rng.randint(1, 6), rng.randint(-5, 5), rng.randint(-7, 7)
    n = rng.randint(3, 5)
    f = a * x**n + b * x**2 + c
    d = sp.diff(f, x)
    prob = pick(rng, ["គេឱ្យអនុគមន៍", "គេមានអនុគមន៍", "ឱ្យអនុគមន៍"]) + f" $f(x)={lx(f)}$ ។ " + pick(rng, ["ចូរគណនាដេរីវេ", "ចូររកដេរីវេ"]) + " $f'(x)$ ។"
    sol = (f"អនុគមន៍ $f$ កំណត់ចំពោះគ្រប់ $x\\in\\mathbb{{R}}$ ។\n"
           f"តាមរូបមន្ត $(x^n)'=nx^{{n-1}}$ យើងបាន៖\n$$f'(x)=({lx(f)})'={lx(d)}$$\n"
           f"ដូចនេះ $f'(x)={lx(d)}$ ។")
    rows.append(make_row("basic_rules", "polynomial", "easy", prob, sol, f"f'(x)={lx(d)}",
                         [check(f"diff({s(f)},x)", s(d), "f'")], "pilot_basic"))
write_jsonl(rows, "pilot_basic.jsonl")
