"""Probability chapter: counting, events, conditional probability, discrete laws, binomial law, density.
Values are exact fractions from SymPy; enumeration is done by the code itself."""
from kx import *
import itertools
from math import comb, perm, factorial
CH = "probability"
C_ = lambda n, k: f"C_{{{n}}}^{{{k}}}"
Fx = lambda v: T(sp.nsimplify(v))
def dec(v, n=4):
    return f"{float(v):.{n}f}".rstrip("0").rstrip(".")
COL = ["ក្រហម", "ស", "ខៀវ", "ខ្មៅ", "លឿង", "បៃតង"]
BOX = [("ប្រអប់មួយ", "ប៊ូល", "ពណ៌"), ("ថង់មួយ", "ប៊ូល", "ពណ៌"), ("កញ្ចប់មួយ", "ស្ករគ្រាប់", "ពណ៌"), ("ប្រអប់មួយ", "ប៊ិច", "ពណ៌")]
OPEN = ("គេទាញយក", "គេចាប់យក", "គេយកចេញ")
def ck(w, expr, val, note="value"): w.C.append(check(expr, val, note))
def cnt_basic(rng):
    n = rng.randint(5, 14); k = rng.randint(2, min(5, n - 1)); kind = rng.choice(["C", "A", "sum"]); w = W(rng)
    if kind == "C":
        v = comb(n, k); P = f"គណនាតម្លៃនៃចំនួនបន្សំ ${C_(n, k)}$ ។"; w.say(f"តាមរូបមន្ត ${C_('n', 'k')}=\\frac{{n!}}{{k!(n-k)!}}$ ៖"); w.say(f"$${C_(n, k)}=\\frac{{{n}!}}{{{k}!\\,{n - k}!}}=\\frac{{" + "\\times ".join(str(n - i) for i in range(k)) + f"}}{{{k}!}}={v}$$"); ck(w, f"binomial({n},{k})", v)
    elif kind == "A":
        v = perm(n, k); P = f"គណនាតម្លៃនៃចំនួនចម្លាស់ $A_{{{n}}}^{{{k}}}$ ។"; w.say("តាមរូបមន្ត $A_n^k=\\frac{n!}{(n-k)!}$ ៖"); w.say(f"$$A_{{{n}}}^{{{k}}}=\\frac{{{n}!}}{{{n - k}!}}=" + "\\times ".join(str(n - i) for i in range(k)) + f"={v}$$"); ck(w, f"factorial({n})/factorial({n - k})", v)
    else:
        v = comb(n, k) + comb(n, k + 1); P = f"គណនាតម្លៃនៃកន្សោម ${C_(n, k)}+{C_(n, k + 1)}$ ។"; w.say("គណនាចំនួនបន្សំនីមួយៗជាមុនសិន ៖"); w.say(f"$${C_(n, k)}={comb(n, k)}\\quad,\\quad {C_(n, k + 1)}={comb(n, k + 1)}$$"); w.say(f"$${C_(n, k)}+{C_(n, k + 1)}={comb(n, k)}+{comb(n, k + 1)}={v}={C_(n + 1, k + 1)}$$"); ck(w, f"binomial({n + 1},{k + 1})", v)
    return row(w.say(f"{so(w)} $\\boxed{{{v}}}$ ។"), CH, "prob_counting", f"steps_count_{kind}", "easy", P, str(v), "cnt_basic")
def committee(rng):
    m, f = rng.randint(3, 10), rng.randint(3, 10); k = rng.randint(2, min(5, m + f - 1)); w = W(rng); kind = rng.choice(["exact", "least", "most"]); g = rng.choice([("សិស្សប្រុស", "សិស្សស្រី", "ថ្នាក់មួយ", "សិស្ស"), ("គ្រូប្រុស", "គ្រូស្រី", "សាលាមួយ", "គ្រូ"), ("បុគ្គលិកប្រុស", "បុគ្គលិកស្រី", "ក្រុមហ៊ុនមួយ", "បុគ្គលិក")]); a, b, pl, who = rng.choice([g]) if False else g
    tot = comb(m + f, k); i = rng.randint(1, min(k, f))
    if k - i > m: return None
    if kind == "exact":
        n = comb(f, i) * comb(m, k - i); P = f"{pl}មាន{a} ${m}$ នាក់ និង{b} ${f}$ នាក់ ។ គេជ្រើសរើស{who} ${k}$ នាក់ជាក្រុមមួយ ។ តើមានប៉ុន្មានរបៀប ដែលក្រុមនោះមាន{b}ចំនួន ${i}$ នាក់ ?"; w.say(f"ជ្រើសរើស{b} ${i}$ នាក់ពី ${f}$ នាក់ ៖ ${C_(f, i)}={comb(f, i)}$ របៀប ។"); w.say(f"ជ្រើសរើស{a} ${k - i}$ នាក់ពី ${m}$ នាក់ ៖ ${C_(m, k - i)}={comb(m, k - i)}$ របៀប ។"); w.say(f"$$N={C_(f, i)}\\times {C_(m, k - i)}={comb(f, i)}\\times {comb(m, k - i)}={n}$$"); ck(w, f"binomial({f},{i})*binomial({m},{k - i})", n)
    elif kind == "least":
        if k > m: return None
        n = tot - comb(m, k); P = f"{pl}មាន{a} ${m}$ នាក់ និង{b} ${f}$ នាក់ ។ គេជ្រើសរើស{who} ${k}$ នាក់ ។ តើមានប៉ុន្មានរបៀប ដែលមាន{b}យ៉ាងតិចម្នាក់ ?"; w.say(f"ចំនួនរបៀបសរុប ៖ ${C_(m + f, k)}={tot}$ ។"); w.say(f"ចំនួនរបៀបគ្មាន{b}សោះ ៖ ${C_(m, k)}={comb(m, k)}$ ។"); w.say(f"$$N={tot}-{comb(m, k)}={n}$$"); ck(w, f"binomial({m + f},{k})-binomial({m},{k})", n)
    else:
        n = sum(comb(f, j) * comb(m, k - j) for j in range(0, 2) if k - j <= m); 
        if k > m: return None
        P = f"{pl}មាន{a} ${m}$ នាក់ និង{b} ${f}$ នាក់ ។ គេជ្រើសរើស{who} ${k}$ នាក់ ។ តើមានប៉ុន្មានរបៀប ដែលមាន{b}យ៉ាងច្រើនម្នាក់ ?"; w.say(f"ករណីគ្មាន{b} ៖ ${C_(m, k)}={comb(m, k)}$ ។"); w.say(f"ករណីមាន{b}ម្នាក់ ៖ ${C_(f, 1)}\\times {C_(m, k - 1)}={f * comb(m, k - 1)}$ ។"); w.say(f"$$N={comb(m, k)}+{f * comb(m, k - 1)}={n}$$"); ck(w, f"binomial({m},{k})+{f}*binomial({m},{k - 1})", n)
    return row(w.say(f"{so(w)} មាន $\\boxed{{{n}}}$ របៀប ។"), CH, "prob_counting", f"steps_committee_{kind}", "medium", P, str(n), "committee")
def digits(rng):
    n = rng.randint(4, 9); ds = sorted(rng.sample(range(1, 10), n)); k = rng.randint(2, min(4, n)); kind = rng.choice(["rep", "norep", "even"]); w = W(rng); L = ",".join(map(str, ds))
    if kind == "rep": v = n ** k; P = f"ពីលេខ ${L}$ តើគេអាចបង្កើតចំនួនមាន ${k}$ ខ្ទង់បានប៉ុន្មាន បើលេខអាចដដែលៗបាន ?"; w.say(f"ខ្ទង់នីមួយៗមាន ${n}$ ជម្រើស ។"); w.say(f"$$N={n}^{{{k}}}={v}$$"); ck(w, f"{n}**{k}", v)
    elif kind == "norep": v = perm(n, k); P = f"ពីលេខ ${L}$ តើគេអាចបង្កើតចំនួនមាន ${k}$ ខ្ទង់ខុសៗគ្នាបានប៉ុន្មាន ?"; w.say(f"នេះជាចម្លាស់ ${k}$ ធាតុពី ${n}$ ធាតុ ៖"); w.say(f"$$N=A_{{{n}}}^{{{k}}}=" + "\\times ".join(str(n - i) for i in range(k)) + f"={v}$$"); ck(w, f"factorial({n})/factorial({n - k})", v)
    else:
        e = sum(d % 2 == 0 for d in ds)
        if e == 0: return None
        v = e * perm(n - 1, k - 1); br_ = sum(1 for t in itertools.permutations(ds, k) if t[-1] % 2 == 0); assert v == br_; P = f"ពីលេខ ${L}$ តើគេអាចបង្កើតចំនួនគូមាន ${k}$ ខ្ទង់ខុសៗគ្នាបានប៉ុន្មាន ?"; w.say(f"ខ្ទង់រាយត្រូវជាលេខគូ ៖ មាន ${e}$ ជម្រើស ។"); w.say(f"ខ្ទង់ ${k - 1}$ ផ្សេងទៀតជ្រើសពីលេខ ${n - 1}$ ដែលនៅសល់ ៖ $A_{{{n - 1}}}^{{{k - 1}}}={perm(n - 1, k - 1)}$ ។"); w.say(f"$$N={e}\\times {perm(n - 1, k - 1)}={v}$$"); ck(w, f"{e}*factorial({n - 1})/factorial({n - k})", v)
    return row(w.say(f"{so(w)} មាន $\\boxed{{{v}}}$ ចំនួន ។"), CH, "prob_counting", f"steps_digits_{kind}", "medium", P, str(v), "digits")
def row_arrange(rng):
    n = rng.randint(4, 9); k = rng.randint(2, 3); w = W(rng); v = factorial(n - k + 1) * factorial(k); tot = factorial(n); pr = R(v, tot); P = f"មនុស្ស ${n}$ នាក់អង្គុយលើកៅអីមួយជួរដោយចៃដន្យ ។ គណនាប្រូបាបដែលមនុស្ស ${k}$ នាក់ជាក់លាក់អង្គុយជាប់គ្នា ។"; w.say(f"ចំនួនករណីអាច ៖ ${n}!={tot}$ ។"); w.say(f"ចាត់ទុកមនុស្ស ${k}$ នាក់ជាមួយក្រុម ៖ គេមាន ${n - k + 1}$ ឯកតា ។"); w.say(f"ចំនួនករណីស្រប ៖ ${n - k + 1}!\\times {k}!={v}$ ។"); w.say(f"$$P=\\frac{{{v}}}{{{tot}}}={T(pr)}$$"); ck(w, f"factorial({n - k + 1})*factorial({k})/factorial({n})", pr)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(pr)}}}$ ។"), CH, "prob_counting", "steps_people_adjacent", "medium", P, T(pr), "row_arrange")
def box_setup(rng, nc=None):
    nc = nc or rng.choice([2, 2, 3]); cs = rng.sample(COL, nc); ns = [rng.randint(2, 9) for _ in cs]; pl, it, _ = rng.choice(BOX)
    desc = " និង ".join(f"{it}{c} ${n}$" for c, n in zip(cs, ns)); return cs, ns, pl, it, desc
def box_exact(rng):
    cs, ns, pl, it, desc = box_setup(rng); N = sum(ns); k = rng.randint(2, min(4, N - 1)); w = W(rng); take = [0] * len(ns); left = k
    for i in range(len(ns) - 1):
        take[i] = rng.randint(0, min(left, ns[i])); left -= take[i]
    take[-1] = left
    if take[-1] > ns[-1]: return None
    fav = 1
    for n, t in zip(ns, take): fav *= comb(n, t)
    tot = comb(N, k); p = R(fav, tot); what = " និង ".join(f"{it}{c} ${t}$" for c, t in zip(cs, take) if t)
    P = f"{pl}មាន{desc} ។ {w.v(*OPEN)}{it} ${k}$ ព្រមគ្នាដោយចៃដន្យ ។ គណនាប្រូបាបដែលបាន{what} ។"; w.say(f"ចំនួនករណីអាច ៖ ${C_(N, k)}={tot}$ ។"); fa = "\\times ".join(C_(n, t) for n, t in zip(ns, take) if t); w.say(f"ចំនួនករណីស្រប ៖ ${fa}={fav}$ ។"); w.say(f"$$P=\\frac{{{fav}}}{{{tot}}}={T(p)}$$" if T(p) != f"\\frac{{{fav}}}{{{tot}}}" else f"$$P={T(p)}$$"); ck(w, "*".join(f"binomial({n},{t})" for n, t in zip(ns, take)) + f"/binomial({N},{k})", p)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(p)}}}$ ។"), CH, "prob_events", "steps_draw_exact", "medium", P, T(p), "box_exact")
def box_least(rng):
    cs, ns, pl, it, desc = box_setup(rng, 2); N = sum(ns); k = rng.randint(2, min(4, ns[1])); w = W(rng); c = cs[0]; tot = comb(N, k); non = comb(ns[1], k); p = 1 - R(non, tot); P = f"{pl}មាន{desc} ។ {w.v(*OPEN)}{it} ${k}$ ព្រមគ្នា ។ គណនាប្រូបាបដែលបាន{it}{c}យ៉ាងតិចមួយ ។"
    w.say(f"តាង $A$ ជាព្រឹត្តិការណ៍ «បាន{it}{c}យ៉ាងតិចមួយ» ។ ព្រឹត្តិការណ៍ផ្ទុយ $\\bar{{A}}$ គឺ «គ្មាន{it}{c}សោះ» ។"); w.say(f"$$P(\\bar{{A}})=\\frac{{{C_(ns[1], k)}}}{{{C_(N, k)}}}=\\frac{{{non}}}{{{tot}}}$$"); w.say(f"$$P(A)=1-P(\\bar{{A}})=1-\\frac{{{non}}}{{{tot}}}={T(p)}$$"); ck(w, f"1-binomial({ns[1]},{k})/binomial({N},{k})", p)
    return row(w.say(f"{so(w)} $\\boxed{{P(A)={T(p)}}}$ ។"), CH, "prob_events", "steps_draw_at_least_one", "medium", P, T(p), "box_least")
def box_same(rng):
    cs, ns, pl, it, desc = box_setup(rng, rng.choice([2, 3])); N = sum(ns); k = 2; w = W(rng); tot = comb(N, k); fav = sum(comb(n, k) for n in ns); p = R(fav, tot); P = f"{pl}មាន{desc} ។ {w.v(*OPEN)}{it} $2$ ព្រមគ្នា ។ គណនាប្រូបាបដែល{it}ទាំងពីរមានពណ៌ដូចគ្នា ។"; w.say(f"ចំនួនករណីអាច ៖ ${C_(N, 2)}={tot}$ ។"); w.say("ករណីស្រប ៖ " + " , ".join(f"ពណ៌{c} ${C_(n, 2)}={comb(n, 2)}$" for c, n in zip(cs, ns)) + " ។"); w.say(f"$$P=\\frac{{{'+'.join(str(comb(n, 2)) for n in ns)}}}{{{tot}}}={T(p)}$$"); ck(w, "(" + "+".join(f"binomial({n},2)" for n in ns) + f")/binomial({N},2)", p)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(p)}}}$ ។"), CH, "prob_events", "steps_draw_same_colour", "medium", P, T(p), "box_same")
def box_seq(rng):
    cs, ns, pl, it, desc = box_setup(rng, 2); N = sum(ns); w = W(rng); rep = rng.random() < .5; a, b = ns; c, d = cs
    if rep:
        p = R(a * b, N * N) * 2; P = f"{pl}មាន{desc} ។ គេទាញ{it}មួយ កត់ពណ៌ រួចដាក់វិញ ហើយទាញម្តងទៀត ។ គណនាប្រូបាបដែលបាន{it}ពីរពណ៌ខុសគ្នា ។"; w.say("ការទាញទាំងពីរឯករាជ្យពីគ្នា ព្រោះគេដាក់វិញ ។"); w.say(f"$$P=\\frac{{{a}}}{{{N}}}\\times\\frac{{{b}}}{{{N}}}+\\frac{{{b}}}{{{N}}}\\times\\frac{{{a}}}{{{N}}}={T(p)}$$"); ck(w, f"2*Rational({a},{N})*Rational({b},{N})", p)
    else:
        p = R(a, N) * R(a - 1, N - 1); P = f"{pl}មាន{desc} ។ គេទាញ{it}ម្តងមួយ ពីរដង ដោយមិនដាក់វិញ ។ គណនាប្រូបាបដែលបាន{it}{c}ទាំងពីរដង ។"; w.say(f"ដងទីមួយ ៖ $P(A_1)=\\frac{{{a}}}{{{N}}}$ ។"); w.say(f"ដងទីពីរ ដោយដឹងថាដងទីមួយបាន{c} ៖ $P(A_2|A_1)=\\frac{{{a - 1}}}{{{N - 1}}}$ ។"); w.say(f"$$P=\\frac{{{a}}}{{{N}}}\\times\\frac{{{a - 1}}}{{{N - 1}}}={T(p)}$$"); ck(w, f"Rational({a},{N})*Rational({a - 1},{N - 1})", p)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(p)}}}$ ។"), CH, "prob_events", "steps_draw_sequence", "medium", P, T(p), "box_seq")
def dice(rng):
    kind = rng.choice(["sum", "ge", "dbl", "prod", "diff", "odd"]); w = W(rng); pairs = list(itertools.product(range(1, 7), repeat=2)); s = rng.randint(3, 11); m = rng.choice([6, 8, 12, 4, 10, 15, 18]); d = rng.randint(1, 4)
    test = {"sum": (lambda a, b: a + b == s, f"ផលបូកលេខស្មើ ${s}$"), "ge": (lambda a, b: a + b >= s, f"ផលបូកលេខធំជាង ឬស្មើ ${s}$"), "dbl": (lambda a, b: a == b, "លេខទាំងពីរដូចគ្នា"), "prod": (lambda a, b: a * b == m, f"ផលគុណលេខស្មើ ${m}$"), "diff": (lambda a, b: abs(a - b) == d, f"ផលដកលេខ (ធំដកតូច) ស្មើ ${d}$"), "odd": (lambda a, b: (a + b) % 2 == 1, "ផលបូកលេខជាចំនួនសេស")}[kind]; good = [t for t in pairs if test[0](*t)]; p = R(len(good), 36)
    if not good: return None
    P = f"គេបោះគ្រាប់ឡុកឡាក់ពីរព្រមគ្នា (មុខនីមួយៗមានប្រូបាបស្មើគ្នា) ។ គណនាប្រូបាបដែល{test[1]} ។"; w.say("ចំនួនករណីអាច ៖ $6\\times 6=36$ ។"); ls = " , ".join(f"({a},{b})" for a, b in good); w.say(f"ករណីស្រប ៖ ${ls}$ ។" if len(good) <= 12 else f"រាប់ករណីស្រប បានចំនួន ${len(good)}$ ករណី ។"); w.say(f"$$P=\\frac{{{len(good)}}}{{36}}" + (f"={T(p)}" if T(p) != f"\\frac{{{len(good)}}}{{36}}" else "") + "$$"); ck(w, f"Rational({len(good)},36)", p)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(p)}}}$ ។"), CH, "prob_events", f"steps_dice_{kind}", "easy", P, T(p), "dice")
def coins(rng):
    n = rng.randint(2, 7); k = rng.randint(0, n); w = W(rng); least = rng.random() < .4 and k > 0; tot = 2 ** n
    if least: fav = sum(comb(n, j) for j in range(k, n + 1)); t = f"យ៉ាងតិច ${k}$ ដង"
    else: fav = comb(n, k); t = f"${k}$ ដងពិតប្រាកដ"
    p = R(fav, tot); P = f"គេបោះកាក់មួយ ${n}$ ដង (មុខទាំងពីរមានប្រូបាបស្មើគ្នា) ។ គណនាប្រូបាបដែលផ្ងារឡើងបានរូបខាងក្បាល {t} ។"; w.say(f"ចំនួនករណីអាច ៖ $2^{{{n}}}={tot}$ ។"); w.say(f"ចំនួនករណីស្រប ៖ $" + ("+".join(C_(n, j) for j in range(k, n + 1)) if least else C_(n, k)) + f"={fav}$ ។"); w.say(f"$$P=\\frac{{{fav}}}{{{tot}}}" + (f"={T(p)}" if T(p) != f"\\frac{{{fav}}}{{{tot}}}" else "") + "$$"); ck(w, f"Rational({fav},{tot})", p)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(p)}}}$ ។"), CH, "prob_events", "steps_coins", "easy", P, T(p), "coins")
def cards(rng):
    N = rng.choice([52, 52, 32]); kk = rng.choice(["ace", "heart", "two_ace", "two_heart", "red"]); w = W(rng); hearts = N // 4; aces = 4
    if kk == "ace": p = R(aces, N); t = "សន្លឹកអាត់"; w.say(f"បៀ ${N}$ សន្លឹកមានសន្លឹកអាត់ $4$ ។"); ex = f"Rational(4,{N})"; n = 1
    elif kk == "heart": p = R(hearts, N); t = "សន្លឹកកឺ"; w.say(f"បៀ ${N}$ សន្លឹកមានសន្លឹកកឺ ${hearts}$ ។"); ex = f"Rational({hearts},{N})"; n = 1
    elif kk == "red": p = R(1, 2); t = "សន្លឹកពណ៌ក្រហម"; w.say(f"បៀពាក់កណ្តាល ពោលគឺ ${N // 2}$ សន្លឹក មានពណ៌ក្រហម ។"); ex = "Rational(1,2)"; n = 1
    elif kk == "two_ace": p = R(comb(4, 2), comb(N, 2)); t = "សន្លឹកអាត់ទាំងពីរ"; w.say(f"ចំនួនករណីអាច ៖ ${C_(N, 2)}={comb(N, 2)}$ ។"); w.say(f"ចំនួនករណីស្រប ៖ ${C_(4, 2)}=6$ ។"); ex = f"binomial(4,2)/binomial({N},2)"; n = 2
    else: p = R(comb(hearts, 2), comb(N, 2)); t = "សន្លឹកកឺទាំងពីរ"; w.say(f"ចំនួនករណីអាច ៖ ${C_(N, 2)}={comb(N, 2)}$ ។"); w.say(f"ចំនួនករណីស្រប ៖ ${C_(hearts, 2)}={comb(hearts, 2)}$ ។"); ex = f"binomial({hearts},2)/binomial({N},2)"; n = 2
    P = (f"គេទាញសន្លឹកបៀ $2$ សន្លឹកព្រមគ្នា" if n == 2 else "គេទាញសន្លឹកបៀមួយសន្លឹក") + f"ចេញពីបៀ ${N}$ សន្លឹក (មានបួនប្រភេទ ប្រភេទនីមួយៗមាន ${N // 4}$ សន្លឹក ដែលមានសន្លឹកអាត់មួយ ហើយពាក់កណ្តាលនៃបៀមានពណ៌ក្រហម) ។ គណនាប្រូបាបដែលបាន{t} ។"; w.say(f"$$P={T(p)}$$"); ck(w, ex, p)
    return row(w.say(f"{so(w)} $\\boxed{{P={T(p)}}}$ ។"), CH, "prob_events", f"steps_cards_{kk}", "easy", P, T(p), "cards")
def dd(rng, den=(10, 20, 100)):
    d = rng.choice(den); return R(rng.randint(1, d - 1), d)
def ptx(v, mode):
    return dec(v) if mode else T(v)
def union(rng):
    d = rng.choice([10, 20, 100]); a = rng.randint(2, d - 2); b = rng.randint(2, d - 2); lo = max(0, a + b - d + 1); hi = min(a, b) - 1
    if hi < lo or hi < 1: return None
    i = rng.randint(max(lo, 1), hi); A, Bv, I_ = R(a, d), R(b, d), R(i, d); U = A + Bv - I_; c1 = I_ / Bv; c2 = I_ / A; m = rng.random() < .6; f = lambda v: ptx(v, m); w = W(rng); ind = I_ == A * Bv
    P = f"គេឱ្យព្រឹត្តិការណ៍ $A$ និង $B$ ដែល $P(A)={f(A)}$ , $P(B)={f(Bv)}$ និង $P(A\\cap B)={f(I_)}$ ។ គណនា ៖\nក. $P(A\\cup B)$\nខ. $P(\\bar{{A}})$\nគ. $P(A|B)$\nឃ. តើ $A$ និង $B$ ជាព្រឹត្តិការណ៍ឯករាជ្យឬទេ ?"
    w.say(f"ក. $$P(A\\cup B)=P(A)+P(B)-P(A\\cap B)={f(A)}+{f(Bv)}-{f(I_)}={f(U)}$$"); w.say(f"ខ. $$P(\\bar{{A}})=1-P(A)=1-{f(A)}={f(1 - A)}$$"); cc = T(c1); w.say(f"គ. $$P(A|B)=\\frac{{P(A\\cap B)}}{{P(B)}}=\\frac{{{f(I_)}}}{{{f(Bv)}}}={cc}$$"); pa = A * Bv; w.say(f"ឃ. $P(A)P(B)={f(A)}\\times {f(Bv)}={T(pa) if not m else dec(pa, 6)}$ ។"); w.say(("ដោយ $P(A\\cap B)=P(A)P(B)$ ដូចនេះ $A$ និង $B$ ឯករាជ្យពីគ្នា ។" if ind else "ដោយ $P(A\\cap B)\\neq P(A)P(B)$ ដូចនេះ $A$ និង $B$ មិនឯករាជ្យពីគ្នាទេ ។")); ck(w, f"Rational({a},{d})+Rational({b},{d})-Rational({i},{d})", U, "union"); ck(w, f"Rational({i},{b})", c1, "cond")
    return row(w.say(f"{so(w)} $\\boxed{{P(A\\cup B)={f(U)}}}$ , $\\boxed{{P(\\bar{{A}})={f(1 - A)}}}$ និង $\\boxed{{P(A|B)={cc}}}$ ។"), CH, "prob_conditional", "steps_union_conditional", "medium", P, f"{f(U)};\\ {f(1 - A)};\\ {cc}", "union")
def two_way(rng):
    a, b, c, d = [rng.randint(4, 40) for _ in range(4)]; w = W(rng); g, h, u, v = rng.choice([("សិស្សប្រុស", "សិស្សស្រី", "ប្រឡងជាប់", "ប្រឡងធ្លាក់"), ("បុគ្គលិកប្រុស", "បុគ្គលិកស្រី", "ជិះម៉ូតូ", "ជិះឡាន"), ("សិស្សប្រុស", "សិស្សស្រី", "ចូលចិត្តគណិតវិទ្យា", "មិនចូលចិត្តគណិតវិទ្យា")]); N = a + b + c + d; p1 = R(a + c, N); p2 = R(c, c + d); p3 = R(c, a + c)
    P = f"ក្រុមមនុស្ស ${N}$ នាក់ ៖ {g} ${a}$ នាក់{u} និង ${b}$ នាក់{v} ។ {h} ${c}$ នាក់{u} និង ${d}$ នាក់{v} ។ គេជ្រើសម្នាក់ដោយចៃដន្យ ។\nក. គណនាប្រូបាបដែលអ្នកនោះ{u} ។\nខ. បើគេដឹងថាអ្នកនោះជា{h} គណនាប្រូបាបដែលគាត់{u} ។\nគ. បើគេដឹងថាអ្នកនោះ{u} គណនាប្រូបាបដែលគាត់ជា{h} ។"
    w.say(f"ក. ចំនួនអ្នក{u} ៖ ${a}+{c}={a + c}$ ។ $$P={T(p1)}$$"); w.say(f"ខ. {h}មាន ${c}+{d}={c + d}$ នាក់ ។ $$P={T(p2)}$$"); w.say(f"គ. ក្នុងចំណោមអ្នក{u} ${a + c}$ នាក់ មាន{h} ${c}$ នាក់ ។ $$P={T(p3)}$$"); ck(w, f"Rational({a}+{c},{N})", p1); ck(w, f"Rational({c},{c}+{d})", p2); ck(w, f"Rational({c},{a}+{c})", p3)
    return row(w.say(f"{so(w)} $\\boxed{{{T(p1)}}}$ , $\\boxed{{{T(p2)}}}$ , $\\boxed{{{T(p3)}}}$ ។"), CH, "prob_conditional", "steps_two_way_table", "medium", P, f"{T(p1)};\\ {T(p2)};\\ {T(p3)}", "two_way")
def bayes(rng):
    k = rng.choice([2, 3]); w = W(rng); shares = rng.choice([[R(3, 5), R(2, 5)], [R(1, 2), R(1, 2)], [R(7, 10), R(3, 10)]]) if k == 2 else rng.choice([[R(1, 2), R(3, 10), R(1, 5)], [R(2, 5), R(2, 5), R(1, 5)], [R(1, 4), R(1, 4), R(1, 2)]]); rates = [R(rng.randint(1, 9), 100) for _ in range(k)]; nm = ["M_1", "M_2", "M_3"][:k]
    tot = sum(s * r for s, r in zip(shares, rates)); j = rng.randrange(k); post = shares[j] * rates[j] / tot; pc = lambda v: dec(v * 100, 2) + "\\%"
    P = "រោងចក្រមួយមានម៉ាស៊ីន " + " , ".join(f"${n}$" for n in nm) + " ផលិតបាន " + " , ".join(f"${pc(s)}$" for s in shares) + " នៃផលិតផលសរុបរៀងគ្នា ។ អត្រាផលិតផលខូចរៀងគ្នា " + " , ".join(f"${pc(r)}$" for r in rates) + f" ។ គេយកផលិតផលមួយដោយចៃដន្យ ។\nក. គណនាប្រូបាបដែលផលិតផលនោះខូច ។\nខ. បើផលិតផលនោះខូច គណនាប្រូបាបដែលវាផលិតដោយ ${nm[j]}$ ។"
    w.say("ក. តាង $D$ ជាព្រឹត្តិការណ៍ «ផលិតផលខូច» ។ តាមរូបមន្តប្រូបាបសរុប ៖"); w.say("$$P(D)=" + "+".join(f"{dec(s)}\\times {dec(r)}" for s, r in zip(shares, rates)) + f"={dec(tot, 6)}$$"); w.say(f"ខ. តាមរូបមន្តបៃយ៍ ៖ $$P({nm[j]}|D)=\\frac{{P({nm[j]})P(D|{nm[j]})}}{{P(D)}}=\\frac{{{dec(shares[j] * rates[j], 6)}}}{{{dec(tot, 6)}}}={T(post)}$$"); ck(w, "+".join(f"Rational({s.p},{s.q})*Rational({r.p},{r.q})" for s, r in zip(shares, rates)), tot, "total"); ck(w, f"Rational({(shares[j] * rates[j]).p},{(shares[j] * rates[j]).q})/Rational({tot.p},{tot.q})", post, "bayes")
    return row(w.say(f"{so(w)} $\\boxed{{P(D)={dec(tot, 6)}}}$ និង $\\boxed{{{T(post)}}}$ ។"), CH, "prob_conditional", "steps_total_bayes", "bacii", P, f"{dec(tot, 6)};\\ {T(post)}", "bayes")
def bayes2(rng):
    a1, b1, a2, b2 = [rng.randint(2, 9) for _ in range(4)]; w = W(rng); c = rng.choice(COL[:3]); d = rng.choice([q for q in COL if q != c]); pr = R(1, 2); p = pr * R(a1, a1 + b1) + pr * R(a2, a2 + b2); post = pr * R(a1, a1 + b1) / p
    P = f"ប្រអប់ទី១ មានប៊ូល{c} ${a1}$ និងប៊ូល{d} ${b1}$ ។ ប្រអប់ទី២ មានប៊ូល{c} ${a2}$ និងប៊ូល{d} ${b2}$ ។ គេជ្រើសប្រអប់មួយដោយចៃដន្យ រួចទាញប៊ូលមួយ ។\nក. គណនាប្រូបាបដែលបានប៊ូល{c} ។\nខ. បើបានប៊ូល{c} គណនាប្រូបាបដែលវាមកពីប្រអប់ទី១ ។"
    w.say(f"ក. តាង $B_1$ , $B_2$ ជាព្រឹត្តិការណ៍ «ជ្រើសបានប្រអប់ទី១ ទី២» និង $R$ ជាព្រឹត្តិការណ៍ «បានប៊ូល{c}» ។ តាមរូបមន្តប្រូបាបសរុប ៖"); w.say(f"$$P(R)=\\frac{{1}}{{2}}\\times\\frac{{{a1}}}{{{a1 + b1}}}+\\frac{{1}}{{2}}\\times\\frac{{{a2}}}{{{a2 + b2}}}={T(p)}$$"); w.say(f"ខ. $$P(B_1|R)=\\frac{{\\frac{{1}}{{2}}\\times\\frac{{{a1}}}{{{a1 + b1}}}}}{{{T(p)}}}={T(post)}$$"); ck(w, f"Rational(1,2)*Rational({a1},{a1 + b1})+Rational(1,2)*Rational({a2},{a2 + b2})", p); ck(w, f"Rational(1,2)*Rational({a1},{a1 + b1})/({p})", post)
    return row(w.say(f"{so(w)} $\\boxed{{{T(p)}}}$ និង $\\boxed{{{T(post)}}}$ ។"), CH, "prob_conditional", "steps_two_boxes_bayes", "bacii", P, f"{T(p)};\\ {T(post)}", "bayes2")
def table(xs, ps, f=T, name="P(X=x)"):
    return "$$\\begin{array}{c|" + "c" * len(xs) + "}x & " + " & ".join(T(v) for v in xs) + " \\\\\\hline " + name + " & " + " & ".join(f(p) for p in ps) + "\\end{array}$$"
def moments(w, xs, ps, f, labels=("ខ", "គ. ")):
    E = sum(a * b for a, b in zip(xs, ps)); E2 = sum(a * a * b for a, b in zip(xs, ps)); Vv = E2 - E ** 2
    w.say(f"{labels[0]}. $$E(X)=\\sum x\\,P(X=x)=" + "+".join(f"{par(a)}\\left({f(b)}\\right)" for a, b in zip(xs, ps)) + f"={f(E)}$$")
    w.say(f"{labels[1]}$$E(X^2)=" + "+".join(f"{par(a)}^2\\left({f(b)}\\right)" for a, b in zip(xs, ps)) + f"={f(E2)}$$")
    w.say(f"$$Var(X)=E(X^2)-\\left[E(X)\\right]^2={f(E2)}-\\left({f(E)}\\right)^2={f(Vv)}$$")
    return E, E2, Vv
def dist_fill(rng):
    n = rng.randint(3, 5); xs = sorted(rng.sample(range(-3, 8), n)); d = rng.choice([10, 10, 20]); cuts = sorted(rng.sample(range(1, d), n - 1)); ps = [R(b - a, d) for a, b in zip([0] + cuts, cuts + [d])]; j = rng.randrange(n); m = True; f = lambda v: dec(v, 4); w = W(rng); shown = [("c" if i == j else f(p)) for i, p in enumerate(ps)]; a, b = rng.choice([2, 3, 4, 5]), rng.randint(-5, 6)
    P = "អថេរចៃដន្យដាច់ $X$ មានបំណែងចែកប្រូបាបដូចតារាង ៖\n" + table(xs, shown, lambda s: s) + f"\nក. រកតម្លៃ $c$ ។\nខ. គណនា $E(X)$ ។\nគ. គណនា $Var(X)$ ។\nឃ. គណនា $E({a}X{st(b)})$ ។"
    w.say("ក. ផលបូកប្រូបាបស្មើ $1$ ៖ $" + "+".join(s for s in shown) + f"=1$ នាំឱ្យ $c={f(ps[j])}$ ។"); E, E2, Vv = moments(w, xs, ps, f); v = a * E + b; w.say(f"ឃ. $$E({a}X{st(b)})={a}E(X){st(b)}={a}\\left({f(E)}\\right){st(b)}={f(v)}$$"); ck(w, "+".join(f"({q})*Rational({p.p},{p.q})" for q, p in zip(xs, ps)), E, "E"); ck(w, "+".join(f"({q})**2*Rational({p.p},{p.q})" for q, p in zip(xs, ps)) + f"-Rational({E.p},{E.q})**2", Vv, "Var")
    return row(w.say(f"{so(w)} $\\boxed{{c={f(ps[j])}}}$ , $\\boxed{{E(X)={f(E)}}}$ , $\\boxed{{Var(X)={f(Vv)}}}$ , $\\boxed{{E({a}X{st(b)})={f(v)}}}$ ។"), CH, "prob_distribution", "steps_table_fill_moments", "medium", P, f"c={f(ps[j])};\\ E(X)={f(E)};\\ Var(X)={f(Vv)};\\ {f(v)}", "dist_fill")
def dist_find_x(rng):
    n = rng.randint(3, 4); xs = sorted(rng.sample(range(-3, 9), n)); d = 10; cuts = sorted(rng.sample(range(1, d), n - 1)); ps = [R(b - a, d) for a, b in zip([0] + cuts, cuts + [d])]; f = lambda v: dec(v); w = W(rng); E = sum(a * b for a, b in zip(xs, ps)); shown = [T(v) for v in xs[:-1]] + ["c"]
    P = "អថេរចៃដន្យដាច់ $X$ មានបំណែងចែកដូចតារាង ៖\n$$\\begin{array}{c|" + "c" * n + "}x & " + " & ".join(shown) + " \\\\\\hline P(X=x) & " + " & ".join(f(p) for p in ps) + f"\\end{{array}}$$\nគណនាតម្លៃនៃ $c$ បើ $E(X)={f(E)}$ ។"
    known = sum(a * b for a, b in zip(xs[:-1], ps[:-1])); w.say("តាមនិយមន័យនៃតម្លៃរំពឹងទុក គេបាន ៖"); w.say("$$E(X)=" + "+".join(f"{par(a)}\\left({f(b)}\\right)" for a, b in zip(xs[:-1], ps[:-1])) + f"+{f(ps[-1])}c$$"); w.say(f"$${f(known)}+{f(ps[-1])}c={f(E)}$$"); w.say(f"$$c=\\frac{{{f(E)}-\\left({f(known)}\\right)}}{{{f(ps[-1])}}}={xs[-1]}$$"); ck(w, f"(Rational({E.p},{E.q})-Rational({known.p},{known.q}))/Rational({ps[-1].p},{ps[-1].q})", xs[-1])
    return row(w.say(f"{so(w)} $\\boxed{{c={xs[-1]}}}$ ។"), CH, "prob_distribution", "steps_find_value_from_mean", "medium", P, f"c={xs[-1]}", "dist_find_x")
def dist_hyper(rng):
    cs, ns, pl, it, desc = box_setup(rng, 2); a, b = ns; N = a + b; k = rng.randint(2, min(4, N - 1)); w = W(rng); c = cs[0]; vals = [i for i in range(0, min(a, k) + 1) if k - i <= b]; tot = comb(N, k); ps = [R(comb(a, i) * comb(b, k - i), tot) for i in vals]
    P = f"{pl}មាន{desc} ។ {w.v(*OPEN)}{it} ${k}$ ព្រមគ្នា ។ តាង $X$ ជាអថេរចៃដន្យតាងចំនួន{it}{c}ដែលទាញបាន ។\nក. កំណត់បំណែងចែកប្រូបាបនៃ $X$ ។\nខ. គណនា $E(X)$ ។\nគ. គណនា $Var(X)$ ។"
    w.say(f"ក. $X$ អាចយកតម្លៃ ${','.join(map(str, vals))}$ ។ ចំនួនករណីអាច ៖ ${C_(N, k)}={tot}$ ។")
    for i, p in zip(vals, ps): w.say(f"$$P(X={i})=\\frac{{{C_(a, i)}\\times {C_(b, k - i)}}}{{{C_(N, k)}}}={T(p)}$$")
    w.say("បំណែងចែកប្រូបាប ៖"); w.say(table(vals, ps)); E = sum(i * p for i, p in zip(vals, ps)); E2 = sum(i * i * p for i, p in zip(vals, ps)); Vv = E2 - E ** 2; w.say("ខ. $$E(X)=" + "+".join(f"{i}\\left({T(p)}\\right)" for i, p in zip(vals, ps)) + f"={T(E)}$$"); w.say("គ. $$E(X^2)=" + "+".join(f"{i}^2\\left({T(p)}\\right)" for i, p in zip(vals, ps)) + f"={T(E2)}$$"); w.say(f"$$Var(X)=E(X^2)-\\left[E(X)\\right]^2={T(E2)}-\\left({T(E)}\\right)^2={T(Vv)}$$"); ck(w, f"Rational({k}*{a},{N})", E, "E"); ck(w, "+".join(f"binomial({a},{i})*binomial({b},{k - i})" for i in vals) + f"-binomial({N},{k})", 0, "sum")
    return row(w.say(f"{so(w)} $\\boxed{{E(X)={T(E)}}}$ និង $\\boxed{{Var(X)={T(Vv)}}}$ ។"), CH, "prob_distribution", "steps_law_from_draw", "bacii", P, f"E(X)={T(E)};\\ Var(X)={T(Vv)}", "dist_hyper")
def dist_labels(rng):
    n1, n2 = rng.randint(2, 5), rng.randint(2, 5); l1, l2 = rng.sample(range(1, 7), 2); k = rng.randint(2, min(4, n1 + n2 - 1)); w = W(rng); N = n1 + n2; tot = comb(N, k); law = {}
    for i in range(0, min(n1, k) + 1):
        if k - i > n2: continue
        s = i * l1 + (k - i) * l2; law[s] = law.get(s, 0) + comb(n1, i) * comb(n2, k - i)
    xs = sorted(law); ps = [R(law[v], tot) for v in xs]; P = f"ក្នុងប្រអប់មួយមានផលិតផល ${N}$ ដែលគេសរសេរលេខ ${l1}$ លើផលិតផល ${n1}$ និងលេខ ${l2}$ លើផលិតផល ${n2}$ ទៀត ។ គេទាញយកផលិតផល ${k}$ ព្រមគ្នាដោយចៃដន្យ ។ តាង $X$ ជាផលបូកលេខលើផលិតផលដែលទាញបាន ។ ចូរកំណត់បំណែងចែកប្រូបាបនៃ $X$ និងគណនា $E(X)$ ។"
    w.say(f"ចំនួនករណីអាច ៖ ${C_(N, k)}={tot}$ ។")
    for i in range(0, min(n1, k) + 1):
        if k - i > n2: continue
        s = i * l1 + (k - i) * l2; w.say(f"យកលេខ ${l1}$ ចំនួន ${i}$ និងលេខ ${l2}$ ចំនួន ${k - i}$ ៖ $X={s}$ មាន ${C_(n1, i)}\\times {C_(n2, k - i)}={comb(n1, i) * comb(n2, k - i)}$ ករណី ។")
    w.say("បំណែងចែកប្រូបាប ៖"); w.say(table(xs, ps)); E = sum(a * b for a, b in zip(xs, ps)); w.say("$$E(X)=" + "+".join(f"{a}\\left({T(b)}\\right)" for a, b in zip(xs, ps)) + f"={T(E)}$$"); ck(w, f"{k}*Rational({n1}*{l1}+{n2}*{l2},{N})", E, "E")
    return row(w.say(f"{so(w)} $\\boxed{{E(X)={T(E)}}}$ ។"), CH, "prob_distribution", "steps_sum_of_labels", "bacii", P, f"E(X)={T(E)}", "dist_labels")
def dist_game(rng):
    win, lose = rng.randint(2, 20), rng.randint(1, 8); N = rng.choice([32, 52]); kind = rng.choice(["card", "die"]); w = W(rng)
    if kind == "card": pw = R(N // 4, N); t = f"គាត់ទាញសន្លឹកបៀមួយពីបៀ ${N}$ សន្លឹក ដែលមានសន្លឹកកឺ ${N // 4}$ ។ បើបានសន្លឹកកឺ"; ot = "បើផ្ទុយពីនេះ"
    else: f_ = rng.randint(1, 3); pw = R(f_, 6); t = "គាត់បោះគ្រាប់ឡុកឡាក់មួយ ។ " + ("បើបានលេខ $1$" if f_ == 1 else f"បើបានលេខតូចជាង ឬស្មើ ${f_}$"); ot = "បើផ្ទុយពីនេះ"
    xs = [-lose, win]; ps = [1 - pw, pw]; P = f"អ្នកលេងល្បែងម្នាក់ ៖ {t} គាត់បានចំណេញ ${win}$ ដុល្លារ ។ {ot} គាត់ខាត ${lose}$ ដុល្លារ ។ តាង $X$ ជាចំណេញ ។\nក. កំណត់បំណែងចែកប្រូបាបនៃ $X$ ។\nខ. គណនា $E(X)$ ។\nគ. តើល្បែងនេះមានប្រយោជន៍ដល់អ្នកលេងឬទេ ?"; E = sum(a * b for a, b in zip(xs, ps))
    w.say(f"ក. $X$ យកតម្លៃ ${-lose}$ និង ${win}$ ។"); w.say(f"$$P(X={win})={T(pw)}\\quad,\\quad P(X={-lose})={T(1 - pw)}$$"); w.say(table(xs, ps)); w.say(f"ខ. $$E(X)=\\left({-lose}\\right)\\left({T(1 - pw)}\\right)+{win}\\left({T(pw)}\\right)={T(E)}$$"); w.say("គ. " + ("ដោយ $E(X)>0$ ល្បែងនេះមានប្រយោជន៍ដល់អ្នកលេង ។" if E > 0 else ("ដោយ $E(X)=0$ ល្បែងនេះស្មើភាព ។" if E == 0 else "ដោយ $E(X)<0$ ល្បែងនេះមិនមានប្រយោជន៍ដល់អ្នកលេងទេ ។"))); ck(w, f"{-lose}*(1-Rational({pw.p},{pw.q}))+{win}*Rational({pw.p},{pw.q})", E)
    return row(w.say(f"{so(w)} $\\boxed{{E(X)={T(E)}}}$ ។"), CH, "prob_distribution", f"steps_game_{kind}", "medium", P, f"E(X)={T(E)}", "dist_game")
def dist_dice(rng):
    kind = rng.choice(["max", "min", "diff", "sum", "five"]); w = W(rng); law = {}
    if kind == "five":
        pr = list(itertools.product(range(1, 7), repeat=3)); fn = lambda t: t.count(5); d = "ចំនួនលេខ $5$ ក្នុងលទ្ធផលនីមួយៗ"; sb = "គេបោះគ្រាប់ឡុកឡាក់បីព្រមគ្នា (មុខនីមួយៗមានប្រូបាបស្មើគ្នា) ។"
    else:
        pr = list(itertools.product(range(1, 7), repeat=2)); fn = {"max": max, "min": min, "diff": lambda *t: abs(t[0] - t[1]), "sum": lambda *t: sum(t)}[kind]; fn = (lambda g: (lambda t: g(*t)))(fn); d = {"max": "លេខធំជាងគេ", "min": "លេខតូចជាងគេ", "diff": "ផលដកលេខ (ធំដកតូច)", "sum": "ផលបូកលេខ"}[kind]; sb = "គេបោះគ្រាប់ឡុកឡាក់ពីរព្រមគ្នា (មុខនីមួយៗមានប្រូបាបស្មើគ្នា) ។"
    for t in pr: law[fn(t)] = law.get(fn(t), 0) + 1
    xs = sorted(law); ps = [R(law[v], len(pr)) for v in xs]; E = sum(a * b for a, b in zip(xs, ps)); P = f"{sb} តាង $X$ ជាអថេរចៃដន្យ «{d}» ។ ធ្វើតារាងបំណែងចែកប្រូបាបនៃ $X$ រួចគណនា $E(X)$ ។"; w.say(f"ចំនួនករណីអាច ៖ ${len(pr)}$ ។ រាប់ករណីតាមតម្លៃនីមួយៗនៃ $X$ ៖"); w.say(table(xs, ps)); w.say("$$E(X)=" + "+".join(f"{a}\\left({T(b)}\\right)" for a, b in zip(xs, ps)) + f"={T(E)}$$"); ck(w, f"Rational({sum(fn(t) for t in pr)},{len(pr)})", E)
    return row(w.say(f"{so(w)} $\\boxed{{E(X)={T(E)}}}$ ។"), CH, "prob_distribution", f"steps_dice_law_{kind}", "medium", P, f"E(X)={T(E)}", "dist_dice")
def bterm(n, k, p):
    return f"C({n},{k})\\cdot({dec(p)})^{{{k}}}\\cdot(1-{dec(p)})^{{{n}-{k}}}"
def bval(n, k, p): return comb(n, k) * p ** k * (1 - p) ** (n - k)
def extreme(v): return v < R(1, 10000) or v > 1 - R(1, 10000)
def bin_basic(rng):
    n = rng.randint(4, 14); p = R(rng.randint(1, 9), 10); k = rng.randint(1, min(n - 1, 5)); w = W(rng); ev = rng.choice(["eq", "le", "ge"])
    v = {"eq": bval(n, k, p), "le": sum(bval(n, i, p) for i in range(k + 1)), "ge": 1 - sum(bval(n, i, p) for i in range(k))}[ev]; t = {"eq": f"P(X={k})", "le": f"P(X\\leq {k})", "ge": f"P(X\\geq {k})"}[ev]; E = n * p; Vv = n * p * (1 - p)
    if extreme(v): return None
    P = f"$X$ ជាអថេរចៃដន្យនៃ $Bin({n},{dec(p)})$ ។ គណនា ៖\nក. ${t}$\nខ. $E(X)$ និង $Var(X)$"
    w.say("ក. រូបមន្ត ៖ $P(X=k)=C(n,k)\\,p^k(1-p)^{n-k}$ ។")
    if ev == "eq": w.say(f"$$P(X={k})={bterm(n, k, p)}\\approx {dec(v)}$$")
    elif ev == "le":
        for i in range(k + 1): w.say(f"$$P(X={i})={bterm(n, i, p)}\\approx {dec(bval(n, i, p), 6)}$$")
        w.say(f"$${t}=" + "+".join(f"P(X={i})" for i in range(k + 1)) + f"\\approx {dec(v)}$$")
    else:
        w.say(f"ប្រើព្រឹត្តិការណ៍ផ្ទុយ ៖ ${t}=1-P(X\\leq {k - 1})$ ។")
        for i in range(k): w.say(f"$$P(X={i})={bterm(n, i, p)}\\approx {dec(bval(n, i, p), 6)}$$")
        w.say(f"$${t}=1-\\left(" + "+".join(f"P(X={i})" for i in range(k)) + f"\\right)\\approx {dec(v)}$$")
    w.say(f"ខ. $$E(X)=np={n}\\times {dec(p)}={dec(E)}$$"); w.say(f"$$Var(X)=np(1-p)={n}\\times {dec(p)}\\times {dec(1 - p)}={dec(Vv)}$$"); ck(w, {"eq": f"binomial({n},{k})*Rational({p.p},{p.q})**{k}*Rational({(1 - p).p},{(1 - p).q})**{n - k}"}.get(ev, "+".join(f"binomial({n},{i})*Rational({p.p},{p.q})**{i}*Rational({(1 - p).p},{(1 - p).q})**{n - i}" for i in (range(k + 1) if ev == "le" else range(k, n + 1)))), v, "binomial")
    return row(w.say(f"{so(w)} $\\boxed{{{t}\\approx {dec(v)}}}$ , $\\boxed{{E(X)={dec(E)}}}$ , $\\boxed{{Var(X)={dec(Vv)}}}$ ។"), CH, "prob_binomial", f"steps_binomial_{ev}", "medium", P, f"{dec(v)};\\ {dec(E)};\\ {dec(Vv)}", "bin_basic")
WORD = [("សិស្សម្នាក់ប្រឡងជាប់តេស្តភាសាអង់គ្លេស", "សិស្សមួយក្រុមមានគ្នា", "នាក់ប្រឡងជាប់", "នាក់"), ("ផលិតផលមួយខូច", "កញ្ចប់ផលិតផលមួយមាន", "ផលិតផលខូច", "គ្រឿង"), ("កីឡាករម្នាក់ស៊ុតបាល់ចូល", "គាត់ស៊ុតបាល់", "ដងចូល", "ដង"), ("ស្ត្រីម្នាក់ប្រើទូរស័ព្ទឆ្លាតវៃ", "គេសួរស្ត្រី", "នាក់ប្រើ", "នាក់"), ("គ្រាប់ពូជមួយដុះ", "គេដាំគ្រាប់ពូជ", "គ្រាប់ដុះ", "គ្រាប់")]
def bin_word(rng):
    a, b, c, u = rng.choice(WORD); n = rng.randint(4, 15); p = R(rng.randint(1, 19), 20); k = rng.randint(1, min(n - 1, 8)); w = W(rng); v = bval(n, k, p); one = 1 - (1 - p) ** n
    if extreme(v) or extreme(one): return None
    P = f"គេដឹងថាប្រូបាបដែល{a} ស្មើនឹង ${dec(p)}$ ហើយករណីនីមួយៗឯករាជ្យពីគ្នា ។ {b} ${n}$ {u} ។\nក. គណនាប្រូបាបដែលមាន ${k}$ {c} ។\nខ. គណនាប្រូបាបដែលមានយ៉ាងតិច $1$ {c} ។\nគ. គណនាចំនួនមធ្យមដែលរំពឹងទុក ។"
    w.say(f"តាង $X$ ជាអថេរចៃដន្យ ។ តាមសម្មតិកម្ម យើងបាន $n={n}$ និង $p={dec(p)}$ ។ ដូចនេះ $X$ មានច្បាប់ $Bin({n},{dec(p)})$ ។"); w.say(f"ក. $$P(X={k})={bterm(n, k, p)}\\approx {dec(v)}$$"); w.say(f"ខ. $$P(X\\geq 1)=1-P(X=0)=1-\\left({dec(1 - p)}\\right)^{{{n}}}\\approx {dec(one)}$$"); E = n * p; w.say(f"គ. $$E(X)=np={n}\\times {dec(p)}={dec(E)}$$"); ck(w, f"binomial({n},{k})*Rational({p.p},{p.q})**{k}*Rational({(1 - p).p},{(1 - p).q})**{n - k}", v); ck(w, f"1-Rational({(1 - p).p},{(1 - p).q})**{n}", one)
    return row(w.say(f"{so(w)} $\\boxed{{{dec(v)}}}$ , $\\boxed{{{dec(one)}}}$ , $\\boxed{{{dec(E)}}}$ ។"), CH, "prob_binomial", "steps_binomial_word", "bacii", P, f"{dec(v)};\\ {dec(one)};\\ {dec(E)}", "bin_word")
def bin_mode(rng):
    n = rng.randint(5, 20); p = R(rng.randint(1, 9), 10); w = W(rng); vals = {k: bval(n, k, p) for k in range(n + 1)}; mode = max(vals, key=vals.get); E = n * p
    if sum(1 for v in vals.values() if v == vals[mode]) > 1: return None
    near = [k for k in (mode - 1, mode, mode + 1) if 0 <= k <= n]; P = f"$X$ ជាអថេរចៃដន្យនៃ $Bin({n},{dec(p)})$ ។ រកតម្លៃនៃ $X$ ដែលកើតឡើងញឹកញាប់ជាងគេ (ម៉ូត) ។"; w.say(f"យើងបាន $n={n}$ និង $p={dec(p)}$ នាំឱ្យ $E(X)=np={dec(E)}$ ។"); lo_, hi_ = (n + 1) * p - 1, (n + 1) * p; assert lo_ <= mode <= hi_; w.say(f"ម៉ូតផ្ទៀងផ្ទាត់ $(n+1)p-1\\leq x\\leq(n+1)p$ ពោលគឺ ${dec(lo_)}\\leq x\\leq {dec(hi_)}$ ។"); w.say("ផ្ទៀងផ្ទាត់ដោយគណនាប្រូបាបក្បែរនោះ ៖")
    for k in near: w.say(f"$$P(X={k})={bterm(n, k, p)}\\approx {dec(vals[k])}$$")
    w.say(f"ដោយ $P(X={mode})$ មានតម្លៃធំជាងគេ គេបាន $x={mode}$ ជាម៉ូត ។"); ck(w, f"binomial({n},{mode})*Rational({p.p},{p.q})**{mode}*Rational({(1 - p).p},{(1 - p).q})**{n - mode}", vals[mode])
    return row(w.say(f"{so(w)} $\\boxed{{x={mode}}}$ ។"), CH, "prob_binomial", "steps_binomial_mode", "medium", P, f"x={mode}", "bin_mode")
def bin_n(rng):
    p = R(rng.randint(1, 6), 10); t = rng.choice([R(9, 10), R(95, 100), R(99, 100)]); w = W(rng); nv = 1
    while 1 - (1 - p) ** nv < t: nv += 1
    q = 1 - p; P = f"ក្នុងការសាកល្បងនីមួយៗ ប្រូបាបជោគជ័យស្មើ ${dec(p)}$ ។ តើត្រូវធ្វើការសាកល្បងឯករាជ្យយ៉ាងតិចប៉ុន្មានដង ទើបប្រូបាបដែលជោគជ័យយ៉ាងតិចម្តង ធំជាង ឬស្មើ ${dec(t)}$ ?"; w.say(f"ប្រូបាបជោគជ័យយ៉ាងតិចម្តងក្នុង $n$ ដង គឺ $1-\\left({dec(q)}\\right)^n$ ។"); w.say(f"$$1-\\left({dec(q)}\\right)^n\\geq {dec(t)}\\iff\\left({dec(q)}\\right)^n\\leq {dec(1 - t)}$$"); w.say(f"យកលោការីតទាំងសងខាង ដោយ $\\ln {dec(q)}<0$ ៖ $$n\\geq\\frac{{\\ln {dec(1 - t)}}}{{\\ln {dec(q)}}}\\approx {float(sp.log(1 - t) / sp.log(q)):.2f}$$"); ck(w, f"floor(log(Rational({(1 - t).p},{(1 - t).q}))/log(Rational({q.p},{q.q})))+1", nv)
    return row(w.say(f"{so(w)} ត្រូវធ្វើយ៉ាងតិច $\\boxed{{n={nv}}}$ ដង ។"), CH, "prob_binomial", "steps_minimum_trials", "bacii", P, f"n={nv}", "bin_n")
def density(rng):
    kind = rng.choice(["x", "x2", "lin"]); b = rng.randint(1, 5); w = W(rng); c = sp.Symbol("k"); g = {"x": x, "x2": x ** 2, "lin": b + 1 - x}[kind]; I = sp.integrate(g, (x, 0, b)); k = 1 / I; f = k * g; a1 = R(b, 2); pr = sp.integrate(f, (x, 0, a1)); E = sp.integrate(x * f, (x, 0, b)); gt = T(g)
    P = f"អថេរចៃដន្យជាប់ $X$ មានអនុគមន៍ដង់ស៊ីតេ $f(x)=k{B(g)}$ លើ $\\left[0;{b}\\right]$ និង $f(x)=0$ ក្រៅពីនេះ ។\nក. រកតម្លៃ $k$ ។\nខ. គណនា $P\\left(0\\leq X\\leq {T(a1)}\\right)$ ។\nគ. គណនា $E(X)$ ។"
    w.say(f"ក. ដោយ $\\int_0^{{{b}}}f(x)\\,dx=1$ គេបាន $k\\int_0^{{{b}}}{B(g)}\\,dx=1$ ។"); w.say(f"$$k\\times {T(I)}=1$$ នាំឱ្យ $k={T(k)}$ ។"); w.say(f"ខ. $$P\\left(0\\leq X\\leq {T(a1)}\\right)=\\int_0^{{{T(a1)}}}{B(f)}\\,dx={T(pr)}$$"); w.say(f"គ. $$E(X)=\\int_0^{{{b}}}x f(x)\\,dx=\\int_0^{{{b}}}{B(sp.expand(x * f))}\\,dx={T(E)}$$"); ck(w, f"integrate({f},(x,0,{b}))", 1, "total"); ck(w, f"integrate({f},(x,0,{a1}))", pr, "P"); ck(w, f"integrate(x*({f}),(x,0,{b}))", E, "E")
    return row(w.say(f"{so(w)} $\\boxed{{k={T(k)}}}$ , $\\boxed{{{T(pr)}}}$ , $\\boxed{{E(X)={T(E)}}}$ ។"), CH, "prob_distribution", f"steps_density_textbook_{kind}", "medium", P, f"k={T(k)};\\ {T(pr)};\\ {T(E)}", "density")
ALL = [(cnt_basic, 200), (committee, 500), (digits, 200), (row_arrange, 20), (box_exact, 900), (box_least, 500), (box_same, 400), (box_seq, 500), (dice, 40), (coins, 40), (cards, 12), (union, 500), (two_way, 500), (bayes, 400), (bayes2, 400), (dist_fill, 700), (dist_find_x, 400), (dist_hyper, 500), (dist_labels, 400), (dist_game, 300), (dist_dice, 6), (bin_basic, 800), (bin_word, 800), (bin_mode, 150), (bin_n, 20), (density, 12)]
