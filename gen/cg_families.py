"""Parametric families with varied wording and solution routes for complex_geometry."""
import random
from cg_core import *

LET = ["ABCD", "MNPQ", "PQRS", "RSTU", "ABCD", "KLMN"]
FRAME = ["ក្នុងប្លង់កុំផ្លិច ", "ក្នុងប្លង់កុំផ្លិចប្រដាប់ដោយតម្រុយអរតូណរម៉ាល់ $(O,\\vec{i},\\vec{j})$ ",
         "នៅក្នុងប្លង់កុំផ្លិច ", "លើប្លង់កុំផ្លិចដែលមានតម្រុយអរតូណរម៉ាល់ $(O,\\vec{i},\\vec{j})$ "]
LABS = [["ក.", "ខ.", "គ.", "ឃ.", "ង.", "ច."], ["១.", "២.", "៣.", "៤.", "៥.", "៦."], ["ក-", "ខ-", "គ-", "ឃ-", "ង-", "ច-"]]
def join(xs):
    xs = list(xs)
    return ", ".join(xs[:-1]) + " និង " + xs[-1] if len(xs) > 1 else xs[0]
def setup(rng, vals, letters=None):
    n = len(vals); lt = (letters or rng.choice(LET))[:n]; st = rng.randrange(5); fm = rng.choice(FRAME)
    if st in (1, 4) and lt.startswith("A"):
        names = [c.lower() for c in lt]
    elif st == 2:
        names = ["z_{%d}" % (i+1) for i in range(n)]
    else:
        names = ["z_{%s}" % c for c in lt]
    ps = [P(l, nm, v) for l, nm, v in zip(lt, names, vals)]
    eqs = [D(p.n + "=" + zt(p.v)) for p in ps]; pl = join(D(p.l) for p in ps)
    v = rng.randrange(5)
    if v == 0: t = fm + "គេឱ្យចំណុច " + pl + " ជារូបភាពរៀងគ្នានៃចំនួនកុំផ្លិច " + join(eqs) + " ។"
    elif v == 1: t = "គេមានចំនួនកុំផ្លិច " + join(eqs) + " ។ " + fm + "តាង " + pl + " ជារូបភាពរៀងគ្នានៃចំនួនទាំងនេះ ។"
    elif v == 2: t = "គេឱ្យចំនួនកុំផ្លិច " + join(eqs) + " ដែលមានរូបភាពរៀងគ្នា " + pl + " " + fm.strip() + " ។"
    elif v == 3: t = fm + "ចំណុច " + join(D(p.l + "(" + p.n + ")") for p in ps) + " មាន " + join(eqs) + " ។"
    else:
        ps = [P(l, "z_{%s}" % l, val) for l, val in zip(lt, vals)]
        t = fm + "គេឱ្យចំណុច " + join(D(p.l + "(" + zt(p.v) + ")") for p in ps) + " ។ តាង " + D(ps[0].n) + " ជាចំនួនកុំផ្លិចដែលមានរូបភាព " + D(ps[0].l) + " ហើយធ្វើដូចគ្នាចំពោះចំណុចផ្សេងទៀត ។"
    return ps, t
def rz(rng, k=3):
    while True:
        z = rng.randint(-k, k) + rng.randint(-k, k)*I
        if z != 0: return z
U = [2+I, 1+2*I, 3+I, 1+3*I, 2+2*I, 3+0*I, 3*I, 4+0*I, 2-I, 3-I, 1-2*I, 2+3*I, 3-2*I, 1+I, 2*I, 2+0*I, 4+2*I, 4-2*I, 1-3*I]
def tri(rng, kind):
    a = rz(rng, 2); u = rng.choice(U); s_ = rng.choice([1, -1])
    if kind == "ri": t = (a, a+u, a+s_*I*u)
    elif kind == "r":
        k = rng.choice([2, 3]); t = (a, a+u, a+s_*I*k*u)
    elif kind == "iso":
        k = rng.choice([2, 3]); t = (a+s_*I*k*u, a+u, a-u)
    elif kind == "eq": t = (a, a+2*u, a+u*(1+s_*I*sqrt(3)))
    else:
        while True:
            b, c = a+rng.choice(U), a+rng.choice(U)+rng.choice([1, -1, I])
            if nature(a, b, c)[0] == "sc": break
        t = (a, b, c)
    t = [E(z) for z in t]; rng.shuffle(t); return t
def nature(a, b, c):
    """kind, index of the special vertex"""
    d = {0: n2(c-b), 1: n2(c-a), 2: n2(b-a)}   # side opposite each vertex
    if E((b-a)*sp.I - (c-a)*0) == 0: return ("deg", 0)
    if sp.im(E((c-a)*cj(b-a))) == 0: return ("deg", 0)
    if d[0] == d[1] == d[2]: return ("eq", 0)
    for i in range(3):
        j, k = (i+1) % 3, (i+2) % 3
        if d[j] == d[k]:
            return ("ri", i) if d[i] == d[j]+d[k] else ("iso", i)
    for i in range(3):
        j, k = (i+1) % 3, (i+2) % 3
        if d[i] == d[j]+d[k]: return ("r", i)
    return ("sc", 0)
def nat_txt(kind, A):
    return {"eq": "ត្រីកោណសម័ង្ស", "ri": "ត្រីកោណកែងសមបាតត្រង់ " + D(A), "r": "ត្រីកោណកែងត្រង់ " + D(A),
            "iso": "ត្រីកោណសមបាតត្រង់ " + D(A), "sc": "ត្រីកោណដែលជ្រុងទាំងបីមិនស្មើគ្នា ហើយមិនកែង"}[kind]
def tri_dist_sol(ps, rng):
    A, B, C_ = ps; k, i = nature(A.v, B.v, C_.v); s_ = rng.choice(["គេគណនាប្រវែងជ្រុងទាំងបី ៖", "តាមរូបមន្ត " + D("AB=|z_B-z_A|") + " យើងបាន ៖", "យើងគណនាចម្ងាយរវាងកំពូលនីមួយៗ ៖"])
    s_ += DD(dl(A, B)) + DD(dl(A, C_)) + DD(dl(B, C_)).lstrip("\n")
    V = ps[i]; W = [ps[(i+1) % 3], ps[(i+2) % 3]]; h = L(W[0].l+W[1].l); s1, s2 = V.l+W[0].l, V.l+W[1].l
    if k == "eq": s_ += "យើងឃើញថាជ្រុងទាំងបីស្មើគ្នា ។"
    elif k in ("ri", "iso"): s_ += "យើងឃើញថា " + D(s1 + "=" + s2) + " ។"
    if k in ("ri", "r"):
        s_ += " ម្យ៉ាងទៀត " + D(h + "^{2}=" + L(n2(W[1].v-W[0].v)) + "=" + L(n2(W[0].v-V.v)) + "+" + L(n2(W[1].v-V.v)) + "=" + s1 + "^{2}+" + s2 + "^{2}") + " ។ តាមទ្រឹស្តីបទពីតាគ័រ ត្រីកោណនេះកែងត្រង់ " + D(V.l) + " ។"
    return s_ + "\n", k, V.l
def chk_d(ps):
    return [("Abs(%s-%s)" % (C(q.v), C(p.v)), str(md(q.v-p.v)), p.l+q.l) for i, p in enumerate(ps) for q in ps[i+1:]]
def spec_of(ps, closed=True, **kw):
    d = {"pts": [(p.l, p.v) for p in ps]}
    if closed: d["poly"] = [[p.v for p in ps]]
    d.update(kw); return d
def it(sub, diff, prob, sol, ans, checks, spec=None, alt=None):
    return dict(sub=sub, diff=diff, prob=prob, sol=sol.rstrip(), ans=ans, checks=checks, spec=spec, alt=alt, gen="param")
def fin(t): return "ដូចនេះ " + t

# ---- affix / vector ----
def f_mirror(rng):
    a, b = rng.choice([1, 2, 3, 4, -1, -2, -3]), rng.choice([1, 2, 3, 5, -1, -2, -4])
    if abs(a) == abs(b): b += 1
    if b == 0: b = 2
    z = a+b*I
    q = rng.choice(["គេឱ្យចំនួនកុំផ្លិច " + D("z=" + zt(z)) + " ។ តាង " + D("M,\\ M_1,\\ M_2,\\ M_3") + " ជារូបភាពរៀងគ្នានៃ " + D("z,\\ \\bar{z},\\ -z,\\ -\\bar{z}") + " ។ រកកូអរដោនេនៃចំណុចទាំងបួន រួចបង្ហាញថា " + D("MM_1M_2M_3") + " ជាចតុកោណកែង និងគណនាផ្ទៃក្រឡារបស់វា ។",
                    "ចំណុច " + D("M") + " ជារូបភាពនៃ " + D("z=" + zt(z)) + " ក្នុងប្លង់កុំផ្លិច ។ ចំណុច " + D("M_1") + " ជារូបភាពនៃចំនួនកុំផ្លិចឆ្លាស់ " + D("\\bar{z}") + " ចំណុច " + D("M_2") + " ជារូបភាពនៃចំនួនកុំផ្លិចផ្ទុយ " + D("-z") + " និង " + D("M_3") + " ជារូបភាពនៃ " + D("-\\bar{z}") + " ។ ដៅចំណុចទាំងនេះ បង្ហាញថាវាជាកំពូលនៃចតុកោណកែង រួចរកផ្ទៃក្រឡា ។"])
    m1, m2, m3 = cj(z), -z, -cj(z)
    s_ = "យើងមាន " + D("\\bar{z}=" + zt(m1)) + " , " + D("-z=" + zt(m2)) + " និង " + D("-\\bar{z}=" + zt(m3)) + " ។ គេបាន " + D("M(%d;%d)" % (a, b)) + " , " + D("M_1(%d;%d)" % (a, -b)) + " , " + D("M_2(%d;%d)" % (-a, -b)) + " , " + D("M_3(%d;%d)" % (-a, b)) + " ។\n"
    s_ += "ចំនួនកុំផ្លិចនៃវ៉ិចទ័រ " + D(vn("M", "M_1")) + " គឺ " + D("\\bar{z}-z=" + zt(m1-z)) + " ហើយនៃវ៉ិចទ័រ " + D(vn("M_3", "M_2")) + " គឺ " + D("-z+\\bar{z}=" + zt(m2-m3)) + " ។ វាស្មើគ្នា ដូច្នេះ " + D("MM_1M_2M_3") + " ជាប្រលេឡូក្រាម ។\n"
    s_ += "ម្យ៉ាងទៀត " + D(vn("M", "M_1")) + " ស្របនឹងអ័ក្សនិមិត្ត ហើយ " + D(vn("M_1", "M_2")) + " មានចំនួនកុំផ្លិច " + D(zt(m2-m1)) + " ដែលជាចំនួនពិត ទើបវាស្របនឹងអ័ក្សពិត ។ ជ្រុងជាប់គ្នាកែងគ្នា ។\n"
    w, h = abs(2*b), abs(2*a); s_ += "ប្រវែងជ្រុង " + D("MM_1=%d" % w) + " និង " + D("M_1M_2=%d" % h) + " ។\n" + fin(D("MM_1M_2M_3") + " ជាចតុកោណកែង ហើយផ្ទៃក្រឡា " + D("\\boxed{S=%d}" % (w*h)) + " ឯកតាផ្ទៃក្រឡា ។")
    ck = [("conjugate(%s)" % C(z), str(m1), "conj"), ("Abs(%s-%s)*Abs(%s-%s)" % (C(m1), C(z), C(m2), C(m1)), str(w*h), "area"), ("re((%s-%s)*conjugate(%s-%s))" % (C(m1), C(z), C(m2), C(m1)), "0", "perp")]
    return it("point_image_symmetry", "medium", q, s_, "S=%d" % (w*h), ck, {"pts": [("M", z), ("M_1", m1), ("M_2", m2), ("M_3", m3)], "poly": [[z, m1, m2, m3]]}, "ចតុកោណកែងដែលមានកំពូលជារូបភាពនៃ z, ឆ្លាស់, ផ្ទុយ និងផ្ទុយនៃឆ្លាស់ ឆ្លុះនឹងអ័ក្សទាំងពីរ ។")
def f_vector(rng):
    while True:
        vals = [rz(rng), rz(rng), rz(rng)]
        if len({str(v) for v in vals}) == 3: break
    ps, t = setup(rng, vals); A, B, C_ = ps; p, q = rng.choice([(2, 1), (1, 2), (3, 1), (2, 3), (1, 3)]); sg = rng.choice([1, -1])
    AB, AC = B.v-A.v, C_.v-A.v; w = E(p*AB+sg*q*AC)
    ve = (str(p) if p > 1 else "") + vec(A, B) + ("+" if sg > 0 else "-") + (str(q) if q > 1 else "") + vec(A, C_)
    v = rng.randrange(2)
    if v == 0:
        pr = t + " រកចំនួនកុំផ្លិចដែលមានរូបភាពជាវ៉ិចទ័រ " + D(vec(A, B)) + " , " + D(vec(A, C_)) + " និង " + D("\\vec{u}=" + ve) + " រួចគណនា " + D("\\|\\vec{u}\\|") + " ។"
    else:
        pr = t + " គេយកវ៉ិចទ័រ " + D("\\vec{u}=" + ve) + " ។ សរសេរចំនួនកុំផ្លិចនៃ " + D("\\vec{u}") + " ជាទម្រង់ពីជគណិត ហើយទាញរកប្រវែងនៃ " + D("\\vec{u}") + " ។"
    s_ = rng.choice(["វ៉ិចទ័រ " + D(vec(A, B)) + " មានចំនួនកុំផ្លិច " + D(B.n + "-" + A.n), "តាមនិយមន័យ ចំនួនកុំផ្លិចនៃ " + D(vec(A, B)) + " គឺ " + D(B.n + "-" + A.n)]) + " ។ គេបាន" + DD("z_{" + vec(A, B) + "}=" + par(B.v) + "-" + par(A.v) + "=" + zt(AB) + ",\\quad z_{" + vec(A, C_) + "}=" + par(C_.v) + "-" + par(A.v) + "=" + zt(AC))
    s_ += "នាំឱ្យ" + DD("z_{\\vec{u}}=" + (str(p) + "\\times " if p > 1 else "") + par(AB) + ("+" if sg > 0 else "-") + (str(q) + "\\times " if q > 1 else "") + par(AC) + "=" + zt(w))
    s_ += "ប្រវែងនៃវ៉ិចទ័រគឺម៉ូឌុលនៃចំនួននេះ ៖ " + D("\\|\\vec{u}\\|=|" + zt(w) + "|=" + modst(w)) + " ។\n" + fin(D("\\boxed{z_{\\vec{u}}=" + zt(w) + "}") + " ហើយ " + D("\\|\\vec{u}\\|=" + L(md(w))) + " ឯកតា ។")
    ck = [("%d*(%s-%s)+(%d)*(%s-%s)" % (p, C(B.v), C(A.v), sg*q, C(C_.v), C(A.v)), str(w), "u"), ("Abs(%d*(%s-%s)+(%d)*(%s-%s))" % (p, C(B.v), C(A.v), sg*q, C(C_.v), C(A.v)), str(md(w)), "norm")]
    o = A.v
    return it("vector_number", rng.choice(["easy", "medium"]), pr, s_, "z_{\\vec{u}}=" + zt(w), ck, spec_of(ps, False, vec=[(A.v, B.v), (A.v, C_.v), (A.v, A.v+w)], pts=[(p_.l, p_.v) for p_ in ps]+[("U", A.v+w)]), "វ៉ិចទ័រពីចំណុចដើម រួមទាំងវ៉ិចទ័រ u ដែលទាញពីចំណុចទីមួយទៅចំណុច U ។")
def f_midcent(rng):
    while True:
        a, b, c = rz(rng, 4), rz(rng, 4), rz(rng, 4)
        s3 = E(a+b+c); g = ri(s3)
        if all(v % 3 == 0 for v in g) and nature(a, b, c)[0] != "deg": break
    ps, t = setup(rng, [a, b, c]); A, B, C_ = ps; G = s3/3; Mi = E((B.v+C_.v)/2)
    pr = t + rng.choice([" រកចំនួនកុំផ្លិចដែលមានរូបភាពជាចំណុចកណ្តាល " + D("I") + " នៃ " + D("[" + B.l + C_.l + "]") + " និងទីប្រជុំទម្ងន់ " + D("G") + " នៃត្រីកោណ " + D(A.l+B.l+C_.l) + " ។ បង្ហាញថា " + D(vn(A.l, "G") + "=\\frac{2}{3}" + vn(A.l, "I")) + " ។",
                         " តាង " + D("I") + " ជាចំណុចកណ្តាលនៃអង្កត់ " + D("[" + B.l + C_.l + "]") + " ហើយ " + D("G") + " ជាទីប្រជុំទម្ងន់នៃត្រីកោណ ។ គណនា " + D("z_I") + " , " + D("z_G") + " រួចផ្ទៀងផ្ទាត់ទំនាក់ទំនង " + D(vn(A.l, "G") + "=\\frac{2}{3}" + vn(A.l, "I")) + " ។"])
    s_ = "ចំណុចកណ្តាល ៖" + DD("z_I=" + fr(B.n + "+" + C_.n, 2) + "=" + fr(zt(B.v+C_.v), 2) + "=" + zt(Mi)) + "ទីប្រជុំទម្ងន់ ៖" + DD("z_G=" + fr(A.n + "+" + B.n + "+" + C_.n, 3) + "=" + fr(zt(s3), 3) + "=" + zt(G))
    w1, w2 = E(G-A.v), E(Mi-A.v)
    s_ += "ផ្ទៀងផ្ទាត់ ៖ " + D("z_G-" + A.n + "=" + zt(w1)) + " ហើយ " + D("\\frac{2}{3}(z_I-" + A.n + ")=\\frac{2}{3}" + par(w2) + "=" + zt(R(2, 3)*w2)) + " ។ អង្គទាំងពីរស្មើគ្នា ។\n" + fin(D("\\boxed{z_I=" + zt(Mi) + "}") + " , " + D("\\boxed{z_G=" + zt(G) + "}") + " ហើយទំនាក់ទំនងពិត ។")
    ck = [("((%s)+(%s))/2" % (C(B.v), C(C_.v)), str(Mi), "mid"), ("((%s)+(%s)+(%s))/3" % (C(A.v), C(B.v), C(C_.v)), str(E(G)), "centroid"), ("(%s)-(%s)-Rational(2,3)*((%s)-(%s))" % (C(G), C(A.v), C(Mi), C(A.v)), "0", "relation")]
    return it("midpoint_centroid", "medium", pr, s_, "z_G=" + zt(G), ck, spec_of(ps, True, pts=[(p.l, p.v) for p in ps]+[("I", Mi), ("G", G)], seg=[(A.v, Mi)]), "ត្រីកោណជាមួយមេដ្យាន ចំណុចកណ្តាល I និងទីប្រជុំទម្ងន់ G ។")
def f_param_dist(rng):
    d0 = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (6, 8, 10), (8, 6, 10), (12, 5, 13)]); a = rz(rng); a1, a2 = ri(a); p, q, d = d0
    # B = (a1+p or a1-p, m)
    b1 = a1+rng.choice([1, -1])*p; m1, m2 = a2+q, a2-q
    A = P("A", "z_A", a); pr = rng.choice([FRAME[0] + "គេឱ្យចំណុច " + D("A") + " និង " + D("B") + " ជារូបភាពនៃ " + D("z_A=" + zt(a)) + " និង " + D("z_B=" + L(b1) + "+mi") + " ដែល " + D("m") + " ជាចំនួនពិត ។ រកតម្លៃ " + D("m") + " ដើម្បីឱ្យ " + D("AB=%d" % d) + " ។",
                                           "គេមាន " + D("z_A=" + zt(a)) + " , " + D("z_B=" + L(b1) + "+mi") + " ហើយ " + D("m\\in\\mathbb{R}") + " ។ កំណត់ " + D("m") + " ដែល " + D("|z_B-z_A|=%d" % d) + " រួចសរសេរ " + D("z_B") + " ចំពោះតម្លៃនីមួយៗ ។"])
    bx = b1-a1
    s_ = "យើងមាន " + D("z_B-z_A=" + L(bx) + "+(m" + ("-" + L(a2) if a2 > 0 else ("+" + L(-a2) if a2 < 0 else "")) + ")i") + " ។ គេបាន" + DD("AB^{2}=" + sq(bx) + "+(m" + ("-" + L(a2) if a2 > 0 else ("+" + L(-a2) if a2 < 0 else "")) + ")^{2}=%d" % (d*d))
    s_ += "នាំឱ្យ " + D("(m" + ("-" + L(a2) if a2 > 0 else ("+" + L(-a2) if a2 < 0 else "")) + ")^{2}=%d" % (q*q)) + " ឬ " + D("m-" + par(a2) + "=\\pm %d" % q) + " ។ គេបាន " + D("m=" + L(m1)) + " ឬ " + D("m=" + L(m2)) + " ។\n"
    s_ += fin(D("\\boxed{m=" + L(m1) + "}") + " ឬ " + D("\\boxed{m=" + L(m2) + "}") + " ដែលឱ្យ " + D("z_B=" + zt(b1+m1*I)) + " ឬ " + D("z_B=" + zt(b1+m2*I)) + " ។")
    ck = [("Abs(%s-%s)" % (C(b1+m1*I), C(a)), str(d), "m1"), ("Abs(%s-%s)" % (C(b1+m2*I), C(a)), str(d), "m2")]
    return it("distance_parameter", "medium", pr, s_, "m=" + L(m1) + "\\ \\text{ឬ}\\ m=" + L(m2), ck, {"pts": [("A", a), ("B_1", b1+m1*I), ("B_2", b1+m2*I)], "seg": [(a, b1+m1*I), (a, b1+m2*I)], "circ": [(a, d)]}, "រង្វង់ផ្ចិត A និងចំណុច B ពីរដែលនៅលើបន្ទាត់ឈរ ។")

# ---- distance, angle, triangles ----
QW = [1+I, 1-I, -1+I, -1-I, I, -I, 2*I, -2*I, 1+sqrt(3)*I, 1-sqrt(3)*I, sqrt(3)+I, sqrt(3)-I, -1+sqrt(3)*I, -sqrt(3)+I, 3*I, -3*I, 2+2*I, 2-2*I]
def f_perimeter(rng):
    kind = rng.choice(["ri", "r", "iso", "sc", "sc"]); ps, t = setup(rng, tri(rng, kind)); A, B, C_ = ps
    sides = [md(B.v-A.v), md(C_.v-A.v), md(C_.v-B.v)]; per = sum(sides)
    pr = t + rng.choice([" គណនាប្រវែង " + D(A.l+B.l) + " , " + D(A.l+C_.l) + " , " + D(B.l+C_.l) + " រួចទាញរកបរិមាត្រនៃត្រីកោណ " + D(A.l+B.l+C_.l) + " ។",
                         " រកបរិមាត្រនៃត្រីកោណ " + D(A.l+B.l+C_.l) + " ។", " គណនាចម្ងាយរវាងចំណុចទាំងបីពីរៗ រួចបូកបញ្ចូលគ្នាដើម្បីទទួលបានបរិមាត្រ ។"])
    s_ = rng.choice(["ជ្រុងនីមួយៗជាម៉ូឌុលនៃផលដកពីរ ៖", "យើងមាន ៖", "តាមរូបមន្តចម្ងាយក្នុងប្លង់កុំផ្លិច ៖"]) + DD(dl(A, B)) + DD(dl(A, C_)).lstrip("\n") + DD(dl(B, C_)).lstrip("\n")
    s_ += "បូកជ្រុងទាំងបី គេបាន " + D("p=" + L(sides[0]) + "+" + L(sides[1]) + "+" + L(sides[2]) + ("=" + L(per) if per.is_Integer or len(per.args) < 3 else "")) + " ។\n" + fin("បរិមាត្រនៃត្រីកោណគឺ " + D("\\boxed{p=" + L(per) + "}") + " ឯកតា ។")
    ck = chk_d(ps) + [("Abs(%s-%s)+Abs(%s-%s)+Abs(%s-%s)" % (C(B.v), C(A.v), C(C_.v), C(A.v), C(C_.v), C(B.v)), str(per), "perimeter")]
    return it("distance_perimeter", "easy", pr, s_, "p=" + L(per), ck, spec_of(ps), "ត្រីកោណក្នុងប្លង់កុំផ្លិច ។")
def f_angle(rng):
    a = rz(rng, 2); u = rng.choice(U[:15]); w = rng.choice(QW)
    if w.has(sqrt(3)): u = rng.choice([2, 2*I, 1+I, -2, 1, 3])
    ps, t = setup(rng, [a, a+u, a+u*w]); A, B, C_ = ps; q = E(w)
    pr = t + rng.choice([" សរសេរ " + D(fr(C_.n + "-" + A.n, B.n + "-" + A.n)) + " ជាទម្រង់ពីជគណិត និងទម្រង់ត្រីកោណមាត្រ រួចទាញរករង្វាស់មុំ " + D("(" + vec(A, B) + "," + vec(A, C_) + ")") + " និងផលធៀប " + D(fr(A.l+C_.l, A.l+B.l)) + " ។",
                         " គណនាផលចែក " + D(fr(C_.n + "-" + A.n, B.n + "-" + A.n)) + " ។ រកម៉ូឌុល និងអាគុយម៉ង់នៃផលចែកនេះ ហើយបកស្រាយជាធរណីមាត្រ ។",
                         " រករង្វាស់មុំតម្រង់ទិស " + D("(" + vec(A, B) + "," + vec(A, C_) + ")") + " ដោយប្រើផលចែកនៃចំនួនកុំផ្លិចពីរ ។"])
    tx, r, th = argst(q, "w")
    s_ = "តាង " + D("w=" + fr(C_.n + "-" + A.n, B.n + "-" + A.n)) + " ។ យើងមាន " + D(C_.n + "-" + A.n + "=" + zt(C_.v-A.v)) + " និង " + D(B.n + "-" + A.n + "=" + zt(B.v-A.v)) + " ។ គេបាន" + DD("w=" + divst(C_.v-A.v, B.v-A.v)) + tx + "\n"
    s_ += "ដូច្នេះ " + D("w=" + tf(r, th)) + " ។ តាមអត្ថន័យធរណីមាត្រ ម៉ូឌុលនៃ " + D("w") + " គឺ " + D(fr(A.l+C_.l, A.l+B.l)) + " ហើយអាគុយម៉ង់គឺមុំពី " + D(vec(A, B)) + " ទៅ " + D(vec(A, C_)) + " ។\n"
    s_ += fin(D("\\boxed{(" + vec(A, B) + "," + vec(A, C_) + ")=" + L(th) + "+2k\\pi}") + " ហើយ " + D(fr(A.l+C_.l, A.l+B.l) + "=" + L(r)) + " ។")
    ck = [("arg(expand((%s-%s)*conjugate(%s-%s)))" % (C(C_.v), C(A.v), C(B.v), C(A.v)), str(th), "angle"), ("Abs(%s-%s)/Abs(%s-%s)" % (C(C_.v), C(A.v), C(B.v), C(A.v)), str(r), "ratio")]
    return it("angle_quotient", rng.choice(["medium", "hard"]), pr, s_, "(" + vec(A, B) + "," + vec(A, C_) + ")=" + L(th) + "+2k\\pi", ck, spec_of(ps, False, seg=[(A.v, B.v), (A.v, C_.v)]), "មុំពីវ៉ិចទ័រ " + A.l + B.l + " ទៅវ៉ិចទ័រ " + A.l + C_.l + " ។")
def f_tri_dist(rng):
    kind = rng.choice(["ri", "ri", "r", "iso", "iso", "eq"]); ps, t = setup(rng, tri(rng, kind)); A, B, C_ = ps
    pr = t + rng.choice([" តើត្រីកោណ " + D(A.l+B.l+C_.l) + " ជាត្រីកោណប្រភេទអ្វី ? ", " កំណត់ប្រភេទនៃត្រីកោណ " + D(A.l+B.l+C_.l) + " ។", " គណនាប្រវែងជ្រុង រួចទាញរកប្រភេទនៃត្រីកោណ " + D(A.l+B.l+C_.l) + " ។", " បង្ហាញថាត្រីកោណ " + D(A.l+B.l+C_.l) + " មានលក្ខណៈពិសេស ហើយបញ្ជាក់លក្ខណៈនោះ ។"]).rstrip()
    s_, k, V = tri_dist_sol(ps, rng); s_ += fin("ត្រីកោណ " + D(A.l+B.l+C_.l) + " ជា" + nat_txt(k, V) + " ។")
    ck = chk_d(ps)
    return it("triangle_nature_distance", "medium", pr, s_, {"eq": "\\text{ត្រីកោណសម័ង្ស}", "ri": "\\text{ត្រីកោណកែងសមបាតត្រង់ }" + V, "r": "\\text{ត្រីកោណកែងត្រង់ }" + V, "iso": "\\text{ត្រីកោណសមបាតត្រង់ }" + V}[k], ck, spec_of(ps), "ត្រីកោណ " + A.l+B.l+C_.l + " ដែលត្រូវកំណត់ប្រភេទ ។")
def f_tri_quot(rng):
    w, nat = rng.choice([(I, "ri"), (-I, "ri"), (2*I, "r"), (-3*I, "r"), (3*I, "r"), (R(1, 2)+sqrt(3)/2*I, "eq"), (R(1, 2)-sqrt(3)/2*I, "eq"), (-2*I, "r")])
    a = rz(rng, 2); u = rng.choice(U[:12]) if not w.has(sqrt(3)) else rng.choice([2, 2*I, -2, 4, -2*I, 4*I])
    ps, t = setup(rng, [a, a+u, a+u*w]); A, B, C_ = ps; q = E(w); tx, r, th = argst(q, "w")
    pr = t + rng.choice([" សរសេរចំនួន " + D("w=" + fr(C_.n+"-"+A.n, B.n+"-"+A.n)) + " ជាទម្រង់ត្រីកោណមាត្រ រួចទាញរកប្រភេទត្រីកោណ " + D(A.l+B.l+C_.l) + " ។",
                         " បង្ហាញថា " + D(fr(C_.n+"-"+A.n, B.n+"-"+A.n) + "=" + zt(q)) + " ។ តើលទ្ធផលនេះប្រាប់អ្វីអំពីត្រីកោណ " + D(A.l+B.l+C_.l) + " ?"])
    s_ = "តាង " + D("w=" + fr(C_.n+"-"+A.n, B.n+"-"+A.n)) + " ។ យើងគណនា ៖" + DD("w=" + divst(C_.v-A.v, B.v-A.v)) + tx + "\n"
    s_ += "នោះ " + D(fr(A.l+C_.l, A.l+B.l) + "=" + L(r)) + " និង " + D("(" + vec(A, B) + "," + vec(A, C_) + ")=" + L(th) + "+2k\\pi") + " ។\n"
    if nat == "eq": s_ += "មុំត្រង់ " + D(A.l) + " ស្មើ " + D("\\frac{\\pi}{3}") + " ហើយ " + D(A.l+B.l+"="+A.l+C_.l) + " ត្រីកោណសមបាតដែលមានមុំកំពូល " + D("\\frac{\\pi}{3}") + " គឺជាត្រីកោណសម័ង្ស ។\n"; res = "ត្រីកោណសម័ង្ស"
    elif nat == "ri": s_ += "មុំត្រង់ " + D(A.l) + " កែង ហើយជ្រុងជាប់មុំកែងស្មើគ្នា ។\n"; res = "ត្រីកោណកែងសមបាតត្រង់ " + D(A.l)
    else: s_ += "មុំត្រង់ " + D(A.l) + " កែង ប៉ុន្តែ " + D(A.l+C_.l+"="+L(r)+A.l+B.l) + " ។\n"; res = "ត្រីកោណកែងត្រង់ " + D(A.l)
    s_ += fin(D(A.l+B.l+C_.l) + " ជា" + res + " ។")
    ck = [("arg(expand((%s-%s)*conjugate(%s-%s)))" % (C(C_.v), C(A.v), C(B.v), C(A.v)), str(th), "angle"), ("Abs(%s-%s)/Abs(%s-%s)" % (C(C_.v), C(A.v), C(B.v), C(A.v)), str(r), "ratio"), ("expand((%s-%s)*conjugate(%s-%s))/%s" % (C(C_.v), C(A.v), C(B.v), C(A.v), str(n2(B.v-A.v))), str(q), "quotient")]
    return it("triangle_nature_quotient", "hard", pr, s_, zt(q), ck, spec_of(ps), "ត្រីកោណ " + A.l+B.l+C_.l + " កំពូល " + A.l + " ។")
def f_oz(rng):
    """O, M(z), N(wz) for every nonzero z: a general proof with a concrete instance."""
    w, res, th = rng.choice([(I, "កែងសមបាតត្រង់ $O$", pi/2), (-I, "កែងសមបាតត្រង់ $O$", -pi/2), (R(1, 2)+sqrt(3)/2*I, "សម័ង្ស", pi/3), (R(1, 2)-sqrt(3)/2*I, "សម័ង្ស", -pi/3)])
    z0 = rng.choice([3+I, 2-I, 1+2*I, 2, 4*I, 1+I, 3-I]); z1 = E(w*z0)
    wn = zt(w) if w in (I, -I) else "\\left(" + zt(w) + "\\right)"
    pr = "គេឱ្យ " + D("z") + " ជាចំនួនកុំផ្លិចខុសពីសូន្យ ។ ក្នុងប្លង់កុំផ្លិច តាង " + D("M") + " និង " + D("N") + " ជារូបភាពនៃ " + D("z") + " និង " + D("z'=" + wn + "z") + " ។ ស្រាយបញ្ជាក់ថាត្រីកោណ " + D("OMN") + " ជាត្រីកោណ" + res + " ចំពោះគ្រប់ " + D("z") + " ។ រួចអនុវត្តចំពោះ " + D("z=" + zt(z0)) + " ដោយរក " + D("z'") + " និងប្រវែង " + D("MN") + " ។"
    tx, r, t2 = argst(w, "w")
    s_ = "តាង " + D("w=" + zt(w)) + " ។ យើងមាន " + D(fr("z'-0", "z-0") + "=w") + " ។\n" + tx + "\nនោះ " + D("|w|=1") + " ផ្តល់ " + D("ON=OM") + " ហើយមុំ " + D("(\\overrightarrow{OM},\\overrightarrow{ON})=" + L(t2) + "+2k\\pi") + " ។\n"
    s_ += ("មុំកំពូល " + D("O") + " កែង និង " + D("OM=ON") if w in (I, -I) else "ត្រីកោណសមបាតត្រង់ " + D("O") + " ដែលមានមុំកំពូល " + D("\\frac{\\pi}{3}")) + " ដូច្នេះត្រីកោណ " + D("OMN") + " ជាត្រីកោណ" + res + " ។\n"
    s_ += "អនុវត្ត ៖ " + D("z'=" + wn + par(z0) + "=" + zt(z1)) + " ហើយ" + DD("MN=|z'-z|=|" + zt(z1-z0) + "|=" + modst(z1-z0))
    d = sp.radsimp(md(z1-z0)); s_ += fin("លក្ខណៈពិតចំពោះគ្រប់ " + D("z\\neq0") + " ហើយចំពោះ " + D("z=" + zt(z0)) + " គេបាន " + D("\\boxed{z'=" + zt(z1) + "}") + " , " + D("\\boxed{MN=" + L(d) + "}") + " ។")
    ck = [("Abs(%s)" % C(w), "1", "|w|"), ("arg(%s)" % C(w), str(t2), "arg w"), ("(%s)*(%s)" % (C(w), C(z0)), str(z1), "instance"), ("Abs((%s)*(%s)-(%s))" % (C(w), C(z0), C(z0)), str(d), "MN")]
    return it("triangle_general_z", "hard", pr, s_, "MN=" + L(d), ck, {"pts": [("O", 0), ("M", z0), ("N", z1)], "poly": [[0, z0, z1]]}, "ត្រីកោណ OMN ចំពោះករណីអនុវត្ត ។")
def f_complete_tri(rng):
    """find third vertex of a right isosceles / equilateral triangle by rotation"""
    a, u = rz(rng, 3), rng.choice(U[:15]); s_g = rng.choice([1, -1]); eq = rng.random() < .35
    if eq: u = rng.choice([2, -2, 2*I, 4, 4*I, -2*I]); w = R(1, 2)+s_g*sqrt(3)/2*I; th = s_g*pi/3
    else: w = s_g*I; th = s_g*pi/2
    ps, t = setup(rng, [a, a+u]); A, B = ps; c = E(a+w*u); Cn = "CRSPQL"[0] if "C" not in (A.l, B.l) else "C"
    Cl = {"A": "C", "M": "P", "P": "R", "R": "T", "K": "M"}[A.l]; nm = "z_{%s}" % Cl
    pr = t + " រកចំនួនកុំផ្លិច " + D(nm) + " ដែលមានរូបភាព " + D(Cl) + " ដើម្បីឱ្យ " + D("(" + vec(A, B) + "," + vn(A.l, Cl) + ")=" + L(th) + "+2k\\pi") + " និង " + D(A.l+Cl+"="+A.l+B.l) + " ។ តើត្រីកោណ " + D(A.l+B.l+Cl) + " ជាប្រភេទអ្វី ?"
    s_ = "លក្ខខណ្ឌទាំងពីរមានន័យថា ផលចែក " + D(fr(nm+"-"+A.n, B.n+"-"+A.n)) + " មានម៉ូឌុល " + D("1") + " និងអាគុយម៉ង់ " + D(L(th)) + " ។ គេបាន" + DD(fr(nm+"-"+A.n, B.n+"-"+A.n) + "=" + tf(1, th) + "=" + zt(w))
    s_ += "នាំឱ្យ" + DD(nm + "=" + A.n + "+" + (par(w)) + "(" + B.n + "-" + A.n + ")=" + par(a) + "+" + par(w) + par(u) + "=" + zt(c))
    res = "ត្រីកោណសម័ង្ស" if eq else "ត្រីកោណកែងសមបាតត្រង់ " + D(A.l)
    s_ += ("ត្រីកោណសមបាតដែលមានមុំ " + D("\\frac{\\pi}{3}") + " ជាត្រីកោណសម័ង្ស ។\n") if eq else ("មុំត្រង់ " + D(A.l) + " កែង ហើយជ្រុងទាំងពីរស្មើគ្នា ។\n")
    s_ += fin(D("\\boxed{" + nm + "=" + zt(c) + "}") + " ហើយ " + D(A.l+B.l+Cl) + " ជា" + res + " ។")
    ck = [("Abs(%s-%s)" % (C(c), C(a)), str(md(u)), "equal sides"), ("arg(expand((%s-%s)*conjugate(%s-%s)))" % (C(c), C(a), C(a+u), C(a)), str(th), "angle")]
    return it("third_vertex_rotation", "hard", pr, s_, nm+"="+zt(c), ck, {"pts": [(A.l, a), (B.l, a+u), (Cl, c)], "poly": [[a, a+u, c]]}, "ត្រីកោណដែលកំពូលទីបីបានពីការបង្វិល ។")

# ---- quadrilaterals ----
def quad(rng, kind):
    a = rz(rng, 2); u = rng.choice(U[:15])
    if kind == "para":
        while True:
            w = rng.choice(U[:15])*rng.choice([1, -1])
            if sp.im(E(w*cj(u))) != 0 and sp.re(E(w*cj(u))) != 0 and n2(w) != n2(u): break
    elif kind == "rect": w = rng.choice([1, -1])*I*rng.choice([2, 3])*u
    elif kind == "sq": w = rng.choice([1, -1])*I*u
    else:
        p = rng.choice(U[:12]); k = rng.choice([2, 3]); m = a
        return [E(m+p), E(m+k*I*p), E(m-p), E(m-k*I*p)]
    return [E(a), E(a+u), E(a+u+w), E(a+w)]
QN = {"para": "ប្រលេឡូក្រាម", "rect": "ចតុកោណកែង", "sq": "ការេ", "rh": "ចតុកោណស្មើ"}
def quad_sol(ps, kind, rng):
    A, B, C_, Dd = ps; u = B.v-A.v; w = Dd.v-A.v
    s_ = rng.choice(["ជាដំបូង យើងផ្ទៀងផ្ទាត់ថាវ៉ិចទ័រពីរស្មើគ្នា ៖", "យើងប្រៀបធៀប " + D(B.n+"-"+A.n) + " និង " + D(C_.n+"-"+Dd.n) + " ៖"])
    s_ += DD(B.n+"-"+A.n+"="+zt(u)+",\\quad "+C_.n+"-"+Dd.n+"="+zt(C_.v-Dd.v))
    s_ += "នោះ " + D(vec(A, B)+"="+vec(Dd, C_)) + " ដូច្នេះ " + D(A.l+B.l+C_.l+Dd.l) + " ជាប្រលេឡូក្រាម ។\n"
    q = dv(w, u); s_ += "គណនាផលចែក ៖" + DD(fr(Dd.n+"-"+A.n, B.n+"-"+A.n)+"="+divst(w, u))
    if sp.re(q) == 0: s_ += "ផលចែកនេះជាចំនួននិមិត្តសុទ្ធ នោះ " + D("("+A.l+B.l+")\\perp("+A.l+Dd.l+")") + " ។\n"
    else: s_ += "ផលចែកនេះមិនមែនជាចំនួននិមិត្តសុទ្ធទេ នោះមុំត្រង់ " + D(A.l) + " មិនកែង ។\n"
    s_ += "ម្យ៉ាងទៀត" + DD(dl(A, B)) + DD(dl(A, Dd)).lstrip("\n")
    s_ += ("ជ្រុងជាប់គ្នាស្មើគ្នា ។\n" if n2(u) == n2(w) else "ជ្រុងជាប់គ្នាមិនស្មើគ្នា ។\n")
    return s_ + fin(D(A.l+B.l+C_.l+Dd.l) + " ជា" + QN[kind] + " ។")
def f_quad(rng):
    kind = rng.choice(["para", "rect", "sq", "rh"]); ps, t = setup(rng, quad(rng, kind)); A, B, C_, Dd = ps; nm = A.l+B.l+C_.l+Dd.l
    pr = t + rng.choice([" តើចតុកោណ " + D(nm) + " មានរាងអ្វី ? ", " បង្ហាញថា " + D(nm) + " ជាប្រលេឡូក្រាម រួចបញ្ជាក់ឱ្យច្បាស់ថាវាជាចតុកោណប្រភេទណា ។", " កំណត់ប្រភេទនៃចតុកោណ " + D(nm) + " ។", " ដោយគណនា " + D(fr(Dd.n+"-"+A.n, B.n+"-"+A.n)) + " និងប្រវែងជ្រុង រកប្រភេទនៃ " + D(nm) + " ។"]).rstrip()
    s_ = quad_sol(ps, kind, rng); u = B.v-A.v; w = Dd.v-A.v
    ck = [("(%s-%s)-(%s-%s)" % (C(B.v), C(A.v), C(C_.v), C(Dd.v)), "0", "parallelogram"), ("re(expand((%s-%s)*conjugate(%s-%s)))" % (C(Dd.v), C(A.v), C(B.v), C(A.v)), str(sp.re(E(w*cj(u)))), "dot"), ("Abs(%s-%s)" % (C(B.v), C(A.v)), str(md(u)), "AB"), ("Abs(%s-%s)" % (C(Dd.v), C(A.v)), str(md(w)), "AD")]
    return it("quadrilateral_nature", rng.choice(["medium", "hard"]), pr, s_, "\\text{" + QN[kind] + "}", ck, spec_of(ps), "ចតុកោណ " + nm + " ក្នុងប្លង់កុំផ្លិច ។")
def f_fourth(rng):
    kind = rng.choice(["para", "rect", "sq"]); q = quad(rng, kind); ps, t = setup(rng, q[:3]); A, B, C_ = ps; Dl = {"A": "D", "M": "Q", "P": "S", "R": "U", "K": "N"}[A.l]; nm = "z_{%s}" % Dl
    d = E(A.v+C_.v-B.v); cen = E((A.v+C_.v)/2); name = A.l+B.l+C_.l+Dl
    pr = t + rng.choice([" រកចំនួនកុំផ្លិច " + D(nm) + " ដែលមានរូបភាព " + D(Dl) + " ដើម្បីឱ្យ " + D(name) + " ជាប្រលេឡូក្រាម ។ រួចរកផ្ចិត " + D("J") + " នៃប្រលេឡូក្រាមនេះ ។", " កំណត់ចំណុច " + D(Dl) + " ដែល " + D(vec(A, B) + "=" + vn(Dl, C_.l)) + " ។ រកចំនួនកុំផ្លិចនៃចំណុចប្រសព្វ " + D("J") + " នៃអង្កត់ទ្រូងទាំងពីរ ។"])
    s_ = rng.choice(["ដើម្បីឱ្យ " + D(name) + " ជាប្រលេឡូក្រាម លុះត្រាតែ " + D(vec(A, B)+"="+vn(Dl, C_.l)), "លក្ខខណ្ឌគឺ " + D(vec(A, B)+"="+vn(Dl, C_.l))]) + " ។ គេបាន" + DD(B.n+"-"+A.n+"="+C_.n+"-"+nm+"\\ \\Leftrightarrow\\ "+nm+"="+A.n+"+"+C_.n+"-"+B.n) + "ជំនួសតម្លៃ ៖" + DD(nm+"="+par(A.v)+"+"+par(C_.v)+"-"+par(B.v)+"="+zt(d))
    s_ += "អង្កត់ទ្រូងនៃប្រលេឡូក្រាមកាត់គ្នាត្រង់ចំណុចកណ្តាល ដូច្នេះ" + DD("z_J="+fr(A.n+"+"+C_.n, 2)+"="+fr(zt(A.v+C_.v), 2)+"="+zt(cen)) + fin(D("\\boxed{"+nm+"="+zt(d)+"}")+" និង "+D("\\boxed{z_J="+zt(cen)+"}")+" ។")
    ck = [("%s+%s-%s" % (C(A.v), C(C_.v), C(B.v)), str(d), "D"), ("(%s-%s)-(%s-%s)" % (C(B.v), C(A.v), C(C_.v), C(d)), "0", "vector"), ("(%s+%s)/2-(%s+%s)/2" % (C(A.v), C(C_.v), C(B.v), C(d)), "0", "diagonals"), ("(%s+%s)/2" % (C(A.v), C(C_.v)), str(cen), "J")]
    return it("fourth_vertex", "medium", pr, s_, nm+"="+zt(d), ck, {"pts": [(p.l, p.v) for p in ps]+[(Dl, d), ("J", cen)], "poly": [[A.v, B.v, C_.v, d]], "seg": [(A.v, C_.v), (B.v, d)]}, "ប្រលេឡូក្រាមជាមួយអង្កត់ទ្រូង និងផ្ចិត J ។")
def f_collinear(rng):
    a = rz(rng); u = rng.choice(U[:15]); k = rng.choice([2, 3, -1, -2, R(1, 2)*2+1, 4]); yes = rng.random() < .75
    c = a+k*u if yes else a+k*u+rng.choice([1, I])
    ps, t = setup(rng, [a, a+u, c]); A, B, C_ = ps; q = dv(C_.v-A.v, B.v-A.v)
    pr = t + rng.choice([" តើចំណុចទាំងបីស្ថិតនៅលើបន្ទាត់តែមួយឬទេ ? ", " ដោយគណនា " + D(fr(C_.n+"-"+A.n, B.n+"-"+A.n)) + " សិក្សាថាចំណុច " + join(D(p.l) for p in ps) + " នៅលើបន្ទាត់តែមួយឬអត់ ។"]).rstrip()
    s_ = "យើងគណនា ៖" + DD(fr(C_.n+"-"+A.n, B.n+"-"+A.n)+"="+divst(C_.v-A.v, B.v-A.v))
    if yes: s_ += "ផលចែកនេះជាចំនួនពិត នោះវ៉ិចទ័រ " + D(vec(A, B)) + " និង " + D(vec(A, C_)) + " ស្របគ្នា ព្រោះ " + D(vec(A, C_)+"="+L(q)+vec(A, B)) + " ។\n" + fin("ចំណុច " + join(D(p.l) for p in ps) + " ស្ថិតនៅលើបន្ទាត់តែមួយ ។"); an = "\\text{នៅលើបន្ទាត់តែមួយ}"
    else: s_ += "ផ្នែកនិមិត្តនៃផលចែកនេះខុសពីសូន្យ វាមិនមែនជាចំនួនពិតទេ ។\n" + fin("ចំណុចទាំងបីមិននៅលើបន្ទាត់តែមួយទេ ។"); an = "\\text{មិននៅលើបន្ទាត់តែមួយ}"
    ck = [("im(expand((%s-%s)*conjugate(%s-%s)))" % (C(C_.v), C(A.v), C(B.v), C(A.v)), str(sp.im(E((C_.v-A.v)*cj(B.v-A.v)))), "im")]
    return it("collinear_points", "medium", pr, s_, an, ck, spec_of(ps, False, seg=[(A.v, B.v), (B.v, C_.v)]), "ចំណុចបីក្នុងប្លង់ ។")
def f_param_col(rng):
    a = rz(rng, 2); u = rng.choice([2+I, 1+2*I, 1+I, 3+I, 1-I, 2-I, 1+3*I]); per = rng.random() < .5; ux, uy = ri(u)
    k = rng.choice([2, 3, -1, -2]); cx = ri(a)[0]+k*ux
    target = (a+k*u) if not per else (a+k*I*u); c1 = ri(target)[0]; m = ri(target)[1]
    ps, t = setup(rng, [a, a+u], "ABCD"); A, B = ps
    cond = "ចំណុច $A$, $B$, $C$ នៅលើបន្ទាត់តែមួយ" if not per else "បន្ទាត់ $(AB)$ កែងនឹងបន្ទាត់ $(AC)$"
    pr = t + " គេយកចំណុច " + D("C") + " ជារូបភាពនៃ " + D("z_C=" + L(c1) + "+mi") + " ដែល " + D("m\\in\\mathbb{R}") + " ។ រកតម្លៃ " + D("m") + " ដើម្បីឱ្យ" + cond + " ។"
    ax, ay = ri(a); dx = c1-ax
    Mm = sp.Symbol("m", real=True)
    W = dx+(Mm-ay)*I; num = sp.expand(W*cj(u)); nr, ni = sp.re(num), sp.im(num)
    expr = ni if not per else nr
    s_ = "តាង " + D("Z="+fr("z_C-"+A.n, B.n+"-"+A.n)) + " ។ យើងមាន " + D("z_C-"+A.n+"="+L(dx)+"+("+L(Mm-ay)+")i") + " និង " + D(B.n+"-"+A.n+"="+zt(u)) + " ។\nគុណភាគយកនិងភាគបែងនឹង " + D(zt(cj(u))) + " គេបាន" + DD("Z="+fr(L(nr)+"+\\left("+L(ni)+"\\right)i", L(n2(u))))
    s_ += ("លក្ខខណ្ឌគឺ " + D("Z") + " ជាចំនួនពិត លុះត្រាតែផ្នែកនិមិត្តស្មើសូន្យ ៖" if not per else "បន្ទាត់ទាំងពីរកែងគ្នា លុះត្រាតែ " + D("Z") + " ជាចំនួននិមិត្តសុទ្ធ មានន័យថាផ្នែកពិតស្មើសូន្យ ៖") + DD(fr(L(expr), L(n2(u)))+"=0" if L(expr) == "m" else L(expr)+"=0\\ \\Leftrightarrow\\ m="+L(m))
    s_ += fin(D("\\boxed{m="+L(m)+"}")+" ។")
    ck = [("%s" % ("im" if not per else "re") + "(expand((%s-%s)*conjugate(%s-%s)))" % (C(c1+m*I), C(a), C(a+u), C(a)), "0", "condition"), (str(sp.solve(expr, Mm)[0]), str(m), "m")]
    return it("collinear_perpendicular_parameter", "hard", pr, s_, "m="+L(m), ck, {"pts": [("A", a), ("B", a+u), ("C", c1+m*I)], "seg": [(a, a+u), (a, c1+m*I)]}, "ចំណុច A, B និង C សម្រាប់តម្លៃ m ដែលរកឃើញ ។")
def f_perp(rng):
    a = rz(rng); u = rng.choice(U[:15]); c = rz(rng); k = rng.choice([1, 2, -1, 3]); yes = rng.random() < .7
    w = E(k*I*u) if yes else E(k*u)
    if a == c: c = E(c+1)
    ps, t = setup(rng, [a, a+u, c, c+w]); A, B, C_, Dd = ps; q = dv(Dd.v-C_.v, B.v-A.v)
    pr = t + " គណនា " + D(fr(Dd.n+"-"+C_.n, B.n+"-"+A.n)) + " រួចទាញរកទីតាំងទាក់ទងនៃបន្ទាត់ " + D("("+A.l+B.l+")") + " និង " + D("("+C_.l+Dd.l+")") + " ។"
    s_ = "យើងមាន ៖" + DD(fr(Dd.n+"-"+C_.n, B.n+"-"+A.n)+"="+divst(Dd.v-C_.v, B.v-A.v))
    if yes: s_ += "ផលចែកជាចំនួននិមិត្តសុទ្ធ នោះអាគុយម៉ង់របស់វាគឺ " + D("\\pm\\frac{\\pi}{2}") + " ។\n" + fin("បន្ទាត់ " + D("("+A.l+B.l+")\\perp("+C_.l+Dd.l+")") + " ។"); an = "("+A.l+B.l+")\\perp("+C_.l+Dd.l+")"
    else: s_ += "ផលចែកជាចំនួនពិត នោះវ៉ិចទ័រទាំងពីរស្របគ្នា ។\n" + fin("បន្ទាត់ " + D("("+A.l+B.l+")") + " និង " + D("("+C_.l+Dd.l+")") + " ស្របគ្នា ឬត្រួតគ្នា ។"); an = "("+A.l+B.l+")\\parallel("+C_.l+Dd.l+")"
    if not yes and sp.im(E((C_.v-A.v)*cj(u))) != 0: s_ = s_.replace(" ស្របគ្នា ឬត្រួតគ្នា ។", " ស្របគ្នា ។")
    ck = [("expand((%s-%s)*conjugate(%s-%s))/%s" % (C(Dd.v), C(C_.v), C(B.v), C(A.v), n2(B.v-A.v)), str(q), "quotient")]
    return it("perpendicular_parallel_lines", "medium", pr, s_, an, ck, spec_of(ps, False, seg=[(A.v, B.v), (C_.v, Dd.v)]), "អង្កត់ពីរដើម្បីប្រៀបធៀបទិស ។")
def f_circum(rng):
    if rng.random() < .5:
        ps, t = setup(rng, tri(rng, rng.choice(["ri", "r"]))); k, i = nature(*[p.v for p in ps]); V = ps[i]; W1, W2 = ps[(i+1) % 3], ps[(i+2) % 3]
        cen = E((W1.v+W2.v)/2); r = md(W1.v-cen); nm = "".join(p.l for p in ps)
        pr = t + rng.choice([" បង្ហាញថាត្រីកោណ " + D(nm) + " ជាត្រីកោណកែង រួចរកផ្ចិត និងកាំនៃរង្វង់ចារឹកក្រៅត្រីកោណនេះ ។", " រករង្វង់ដែលកាត់តាមចំណុចទាំងបី ដោយប្រើលក្ខណៈត្រីកោណកែង ។"])
        s_, _, _ = tri_dist_sol(ps, rng); s_ += "ត្រីកោណកែងត្រង់ " + D(V.l) + " មានផ្ចិតរង្វង់ចារឹកក្រៅជាចំណុចកណ្តាល " + D("\\Omega") + " នៃអ៊ីប៉ូតេនុស " + D("["+W1.l+W2.l+"]") + " ។" + DD("z_\\Omega="+fr(zt(W1.v+W2.v), 2)+"="+zt(cen)+",\\quad r="+fr(W1.l+W2.l, 2)+"="+L(sp.radsimp(r))) + fin("ផ្ចិត " + D("\\boxed{z_\\Omega="+zt(cen)+"}") + " និងកាំ " + D("\\boxed{r="+L(sp.radsimp(r))+"}") + " ។")
    else:
        cen = rz(rng, 2); pts0 = rng.choice([[5, 3+4*I, -4+3*I, -3-4*I, 4-3*I, 5*I], [5, -5, 3-4*I, 4+3*I, -3+4*I, -4-3*I]]); rng.shuffle(pts0); o = pts0[:3]
        r = sp.Integer(5)
        ps, t = setup(rng, [E(cen+z) for z in o]); nm = "".join(p.l for p in ps); om = P("\\Omega ", "z_\\Omega", cen)
        pr = t + " គេឱ្យចំណុច " + D("\\Omega") + " ជារូបភាពនៃ " + D("z_\\Omega=" + zt(cen)) + " ។ បង្ហាញថាចំណុចទាំងបីនៅលើរង្វង់ផ្ចិត " + D("\\Omega") + " រួចរកកាំ និងសមីការរង្វង់ក្នុងកូអរដោនេ ។"
        s_ = "យើងគណនាចម្ងាយពី " + D("\\Omega") + " ទៅចំណុចនីមួយៗ ៖" + "".join(DD(dl(om, p)).lstrip("\n") if j else DD(dl(om, p)) for j, p in enumerate(ps)) + "ចម្ងាយទាំងបីស្មើ " + D("5") + " ។\n"
        cx, cy = ri(cen); eqn = L((X-cx)**2)+"+"+L((Y-cy)**2)+"=25"
        s_ += fin("ចំណុចទាំងបីនៅលើរង្វង់ផ្ចិត " + D("\\Omega") + " កាំ " + D("\\boxed{r=5}") + " ដែលមានសមីការ " + D(eqn) + " ។")
    ck = [("Abs(%s-%s)" % (C(p.v), C(cen)), str(sp.radsimp(r)), p.l) for p in ps]
    return it("circumcircle", "hard", pr, s_, "r="+L(sp.radsimp(r)), ck, {"pts": [(p.l, p.v) for p in ps]+[("\\Omega", cen)], "poly": [[p.v for p in ps]], "circ": [(cen, r)]}, "ត្រីកោណ និងរង្វង់ចារឹកក្រៅ ។")

# ---- loci ----
SETM = ["រកសំណុំចំណុច $M$ រូបភាពនៃ $z$ ដែលផ្ទៀងផ្ទាត់", "កំណត់សំណុំចំណុច $M(z)$ ក្នុងប្លង់កុំផ្លិច ដែល", "ក្នុងប្លង់កុំផ្លិច តាង $M$ ជារូបភាពនៃ $z$ ។ រកសំណុំនៃចំណុច $M$ បើគេដឹងថា", "គេឱ្យចំនួនកុំផ្លិច $z$ មានរូបភាព $M$ ។ តើចំណុច $M$ ស្ថិតនៅលើខ្សែអ្វី បើ"]
ZXY = ["តាង $z=x+iy$ ដែល $x,y\\in\\mathbb{R}$ ។ ", "សរសេរ $z=x+iy$ ជាមួយ $x$ និង $y$ ជាចំនួនពិត ។ ", "យក $z=x+iy$ ($x,y$ ជាចំនួនពិត) ។ "]
def sqb(v, s_):  # (x-v)^2 latex
    return L((s_-v)**2)
def circ_eq(c, r2):
    a, b = ri(c); return sqb(a, X)+"+"+sqb(b, Y)+"="+L(r2)
def line_eq(e):
    p = sp.Poly(e, X, Y); g = sp.gcd_list([sp.Integer(v) for v in p.coeffs()]) if all(v.is_Integer for v in p.coeffs()) else 1
    e2 = sp.expand(e/g)
    if sp.Poly(e2, X, Y).coeffs()[0] < 0: e2 = -e2
    return e2, L(e2)+"=0"
def f_loc_circle(rng):
    c = rz(rng); r = rng.choice([1, 2, 3, 4, 5, sqrt(2), sqrt(5)]); form = rng.randrange(5); k = rng.choice([2, 3])
    if form == 0: cond = "|z" + ("-"+par(c) if c != 0 else "") + "|=" + L(r); ex = "Abs(%s-" + C(c) + ")"; pre = ""
    elif form == 1:
        cond = "|\\bar{z}-"+par(cj(c))+"|="+L(r); ex = "Abs(conjugate(%s)-"+C(cj(c))+")"
        pre = "ចំពោះគ្រប់ចំនួនកុំផ្លិច " + D("w") + " យើងមាន " + D("|\\bar{w}|=|w|") + " ដូច្នេះ " + D("|\\bar{z}-"+par(cj(c))+"|=|z-"+par(c)+"|") + " ។\n"
    elif form == 2:
        cond = "|%dz-" % k+par(k*c)+"|="+L(k*r); ex = "Abs(%d*%%s-" % k+C(k*c)+")"
        pre = "ដាក់កត្តា " + D(str(k)) + " ៖ " + D("|%dz-" % k+par(k*c)+"|=%d|z-" % k+par(c)+"|") + " ដូច្នេះលក្ខខណ្ឌក្លាយជា " + D("|z-"+par(c)+"|="+L(r)) + " ។\n"
    elif form == 3:
        b = E(I*c); cond = "|iz-"+par(b)+"|="+L(r); ex = "Abs(I*%s-"+C(b)+")"
        pre = "ដោយ " + D("|i|=1") + " និង " + D("iz-"+par(b)+"=i\\left(z-"+par(c)+"\\right)") + " គេបាន " + D("|z-"+par(c)+"|="+L(r)) + " ។\n"
    else:
        cond = "(z-"+par(c)+")(\\bar{z}-"+par(cj(c))+")="+L(r*r); ex = "Abs(%s-"+C(c)+")**2"
        pre = "ចំពោះគ្រប់ចំនួនកុំផ្លិច " + D("w") + " យើងមាន " + D("w\\bar{w}=|w|^{2}") + " ដូច្នេះលក្ខខណ្ឌនេះសមមូលនឹង " + D("|z-"+par(c)+"|^{2}="+L(r*r)) + " ។\n"
    pr = rng.choice(SETM) + " " + D(cond) + " ។"
    if rng.random() < .5:
        s_ = pre + "តាង " + D("\\Omega") + " ជាចំណុចរូបភាពនៃ " + D(zt(c)) + " ។ កន្សោម " + D("|z-z_\\Omega|") + " គឺចម្ងាយ " + D("\\Omega M") + " ។ គេបាន " + D("\\Omega M="+L(r)) + " ។\n"
    else:
        cx, cy = ri(c); s_ = pre + rng.choice(ZXY) + "យើងបាន " + D("z-"+par(c)+"="+L(X-cx)+"+\\left("+L(Y-cy)+"\\right)i") + " ។ ការេនៃម៉ូឌុលឱ្យ" + DD(circ_eq(c, r*r))
    s_ += fin("សំណុំចំណុច " + D("M") + " គឺរង្វង់ផ្ចិត " + D("\\boxed{\\Omega("+zt(c)+")}") + " កាំ " + D("\\boxed{r="+L(r)+"}") + " ។")
    v = (r*r if form == 4 else (k*r if form == 2 else r))
    ck = [(ex % C(E(c+r)), str(v), "point c+r"), (ex % C(E(c-r)), str(v), "point c-r"), (ex % C(E(c+I*r)), str(v), "point c+ir")]
    return it("locus_circle", rng.choice(["easy", "medium"]), pr, s_, "\\Omega("+zt(c)+"),\\ r="+L(r), ck, {"pts": [("\\Omega", c)], "circ": [(c, r)]}, "រង្វង់ផ្ចិត Ω ដែលជាសំណុំចំណុច M ។")
def f_loc_bis(rng):
    while True:
        a, b = rz(rng), rz(rng)
        if a != b and n2(b-a) > 1: break
    form = rng.randrange(4); a1, a2 = ri(a); b1, b2 = ri(b)
    if form == 0: cond = "|z-"+par(a)+"|=|z-"+par(b)+"|"; pre = ""; ex = "Abs(%s-"+C(a)+")"; ey = "Abs(%s-"+C(b)+")"
    elif form == 1:
        cond = "|\\bar{z}-"+par(cj(a))+"|=|z-"+par(b)+"|"; ex = "Abs(conjugate(%s)-"+C(cj(a))+")"; ey = "Abs(%s-"+C(b)+")"
        pre = "ដោយចំនួនកុំផ្លិចឆ្លាស់មានម៉ូឌុលដូចគ្នា " + D("|\\bar{z}-"+par(cj(a))+"|=|z-"+par(a)+"|") + " ។\n"
    elif form == 2:
        cond = "\\left|"+fr("z-"+par(a), "z-"+par(b))+"\\right|=1"; ex = "Abs(%s-"+C(a)+")/Abs(%s-"+C(b)+")"; ey = "1"
        pre = "លក្ខខណ្ឌមានន័យលុះត្រាតែ " + D("z\\neq "+zt(b)) + " ។ វាសមមូលនឹង " + D("|z-"+par(a)+"|=|z-"+par(b)+"|") + " ។\n"
    else:
        cond = "|iz-"+par(E(I*a))+"|=|z-"+par(b)+"|"; ex = "Abs(I*%s-"+C(E(I*a))+")"; ey = "Abs(%s-"+C(b)+")"
        pre = "ព្រោះ " + D("|iz-"+par(E(I*a))+"|=|i||z-"+par(a)+"|=|z-"+par(a)+"|") + " លក្ខខណ្ឌក្លាយជា " + D("|z-"+par(a)+"|=|z-"+par(b)+"|") + " ។\n"
    pr = rng.choice(SETM) + " " + D(cond) + " ។ សរសេរសមីការរបស់សំណុំនេះក្នុងកូអរដោនេ " + D("(x;y)") + " ។"
    e = sp.expand(2*(b1-a1)*X+2*(b2-a2)*Y+(a1**2+a2**2-b1**2-b2**2)); e2, le = line_eq(e); mid = E((a+b)/2)
    s_ = pre + "តាង " + D("A") + " និង " + D("B") + " ជារូបភាពនៃ " + D(zt(a)) + " និង " + D(zt(b)) + " ។ លក្ខខណ្ឌគឺ " + D("MA=MB") + " ដូច្នេះ " + D("M") + " នៅលើមេដ្យាទ័រនៃ " + D("[AB]") + " ។\n"
    s_ += rng.choice(ZXY) + "ការេអង្គទាំងពីរឱ្យ" + DD(sqb(a1, X)+"+"+sqb(a2, Y)+"="+sqb(b1, X)+"+"+sqb(b2, Y)) + "ពន្លាត ហើយសម្រួលតួ " + D("x^{2}") + " និង " + D("y^{2}") + " គេបាន " + D(L(e)+"=0") + " ។\n"
    s_ += "ផ្ទៀងផ្ទាត់ ៖ ចំណុចកណ្តាល " + D(zt(mid)) + " នៃ " + D("[AB]") + " ផ្ទៀងផ្ទាត់សមីការនេះ ។\n" + fin("សំណុំចំណុច " + D("M") + " គឺមេដ្យាទ័រនៃ " + D("[AB]") + " ដែលមានសមីការ " + D("\\boxed{"+le+"}") + " ។")
    pts = [mid, E(mid+I*(b-a))]
    ck = []
    for p in pts:
        if ey == "1": ck.append((ex % (C(p), C(p)), "1", "point on line"))
        else: ck.append((ex % C(p), ey % C(p), "point on line"))
        px, py = ri(p); ck.append((str(e2.subs({X: px, Y: py})), "0", "line eq"))
    return it("locus_perpendicular_bisector", "medium", pr, s_, le, ck, {"pts": [("A", a), ("B", b)], "seg": [(a, b)], "line": [(pts[0], pts[1])]}, "មេដ្យាទ័រនៃអង្កត់ AB ។")
def f_loc_line(rng):
    p, q = rng.choice([(1, 2), (2, 1), (1, -1), (1, 1), (2, -1), (3, 1), (1, 3), (2, 3)]); c = rng.choice([1, 2, 3, 4, -2, -1, 6]); w = p+q*I; form = rng.randrange(5)
    if form == 0:
        cond = "ផ្នែកពិតនៃ " + D(par(w)+"z") + " ស្មើ " + D(str(c)); e = p*X-q*Y-c; st = D(par(w)+"z=("+L(p*X-q*Y)+")+("+L(q*X+p*Y)+")i"); ex = "re(expand((%s)*%%s))" % C(w); v = c
    elif form == 1:
        cond = "ផ្នែកនិមិត្តនៃ " + D(par(w)+"z") + " ស្មើ " + D(str(c)); e = q*X+p*Y-c; st = D(par(w)+"z=("+L(p*X-q*Y)+")+("+L(q*X+p*Y)+")i"); ex = "im(expand((%s)*%%s))" % C(w); v = c
    elif form == 2:
        cond = D("z+\\bar{z}=%d" % (2*c)); e = X-c; st = D("z+\\bar{z}=2x"); ex = "(lambda: 0)"; ex = "2*re(%s)"; v = 2*c
    elif form == 3:
        cond = D("z-\\bar{z}="+zt(2*c*I)); e = Y-c; st = D("z-\\bar{z}=2iy"); ex = "2*im(%s)"; v = 2*c
    else:
        cond = D(str(p)+"(z+\\bar{z})"+("+" if q > 0 else "-")+"i"+("" if abs(q) == 1 else str(abs(q)))+"(z-\\bar{z})=%d" % (2*c)); e = p*X-q*Y-c; st = D("z+\\bar{z}=2x")+" និង "+D("i(z-\\bar{z})=-2y")+" ដូច្នេះអង្គឆ្វេងស្មើ "+D(L(2*p*X-2*q*Y)); ex = "%d*2*re(%%s)-%d*2*im(%%s)" % (p, q); v = 2*c
    pr = rng.choice(SETM) + " " + cond + " ។"
    e2, le = line_eq(e); s_ = rng.choice(ZXY) + "គេបាន " + st + " ។\nលក្ខខណ្ឌឱ្យ " + D(le) + " ។ នេះជាសមីការបន្ទាត់ ។\n"
    # two points on the line
    co = sp.Poly(e, X, Y)
    if e.has(Y):
        sol = sp.solve(e, Y)[0]; p1 = sol.subs(X, 0)*I; p2 = 2+sol.subs(X, 2)*I
    else:
        x0 = sp.solve(e, X)[0]; p1 = x0; p2 = x0+2*I
    s_ += "បន្ទាត់នេះកាត់តាមចំណុចរូបភាពនៃ " + D(zt(p1)) + " និង " + D(zt(p2)) + " ។\n" + fin("សំណុំចំណុច " + D("M") + " គឺបន្ទាត់ដែលមានសមីការ " + D("\\boxed{"+le+"}") + " ។")
    ck = []
    for pt in (p1, p2):
        ck.append(((ex.replace("%s", C(pt))), str(v), "point on line"))
    return it("locus_line_real_imag", "easy", pr, s_, le, ck, {"line": [(p1, p2)], "pts": [("P", p1), ("Q", p2)]}, "បន្ទាត់ដែលជាសំណុំចំណុច M ។")
def quot_parts(a, b):
    a1, a2 = ri(a); b1, b2 = ri(b)
    return sp.expand((X-a1)*(X-b1)+(Y-a2)*(Y-b2)), sp.expand((Y-a2)*(X-b1)-(X-a1)*(Y-b2))
def f_loc_quot(rng):
    while True:
        a, b = rz(rng, 2)*2, rz(rng, 2)*2
        if a != b: break
    b = E(b); a = E(a); circle = rng.random() < .5; rr, ii = quot_parts(a, b)
    Zt = "Z="+fr("z-"+par(a), "z-"+par(b)); cen = E((a+b)/2); r = md(a-b)/2
    a1, a2 = ri(a); b1, b2 = ri(b)
    pr = "គេឱ្យ " + D(Zt) + " ដែល " + D("z\\neq "+zt(b)) + " ។ តាង " + D("M") + " ជារូបភាពនៃ " + D("z") + " ។ " + rng.choice(["រកសំណុំចំណុច $M$ ដើម្បីឱ្យ", "កំណត់សំណុំចំណុច $M$ ដែល"]) + (" ផ្នែកពិតនៃ " + D("Z") + " ស្មើសូន្យ ។" if circle else " ផ្នែកនិមិត្តនៃ " + D("Z") + " ស្មើសូន្យ ។")
    s_ = rng.choice(ZXY) + "គុណភាគយកនិងភាគបែងនៃ " + D("Z") + " នឹងចំនួនឆ្លាស់នៃភាគបែង ៖" + DD("Z="+fr("\\left[("+L(X-a1)+")+("+L(Y-a2)+")i\\right]\\left[("+L(X-b1)+")-("+L(Y-b2)+")i\\right]", "("+L(X-b1)+")^{2}+("+L(Y-b2)+")^{2}"))
    if circle:
        s_ += "ផ្នែកពិតនៃភាគយកគឺ " + D(L(rr)) + " ។ លក្ខខណ្ឌឱ្យ" + DD(L(rr)+"=0") + "បំពេញជាការេ គេបាន " + D(circ_eq(cen, r*r)) + " ។\nនេះជារង្វង់ផ្ចិត " + D(zt(cen)) + " កាំ " + D(L(r)) + " ដែលមានអង្កត់ផ្ចិត " + D("[AB]") + " ជាមួយ " + D("A("+zt(a)+")") + " និង " + D("B("+zt(b)+")") + " ។ ចំណុច " + D("B") + " ត្រូវដកចេញ ព្រោះ " + D("z\\neq "+zt(b)) + " ។\n"
        s_ += fin("សំណុំចំណុច " + D("M") + " គឺ " + D("\\boxed{"+circ_eq(cen, r*r)+"}") + " ដកចំណុច " + D("B") + " ចេញ ។"); an = circ_eq(cen, r*r)
        pts = [E(cen+r*(a-b)/md(a-b)*I), a]; ck = [("re(expand((%s-%s)*conjugate(%s-%s)))" % (C(p), C(a), C(p), C(b)), "0", "on circle") for p in pts]
        ck.append((str(rr.subs({X: ri(a)[0], Y: ri(a)[1]})), "0", "A on circle"))
        sp_ = {"pts": [("A", a), ("B", b), ("\\Omega", cen)], "circ": [(cen, r)], "seg": [(a, b)]}; alt = "រង្វង់អង្កត់ផ្ចិត AB ដោយដកចំណុច B ។"
    else:
        e2, le = line_eq(ii)
        s_ += "ផ្នែកនិមិត្តនៃភាគយកគឺ " + D(L(ii)) + " ។ លក្ខខណ្ឌឱ្យ" + DD(le) + "ជាសមីការបន្ទាត់ដែលកាត់តាម " + D("A("+zt(a)+")") + " និង " + D("B("+zt(b)+")") + " ។ ចំណុច " + D("B") + " ត្រូវដកចេញ ។\n"
        s_ += fin("សំណុំចំណុច " + D("M") + " គឺបន្ទាត់ " + D("\\boxed{"+le+"}") + " ដកចំណុច " + D("B") + " ចេញ ។"); an = le
        p = E(2*a-b); ck = [("im(expand((%s-%s)*conjugate(%s-%s)))" % (C(p), C(a), C(p), C(b)), "0", "on line"), (str(e2.subs({X: ri(a)[0], Y: ri(a)[1]})), "0", "A on line"), (str(e2.subs({X: ri(b)[0], Y: ri(b)[1]})), "0", "B on line")]
        sp_ = {"pts": [("A", a), ("B", b)], "line": [(a, b)]}; alt = "បន្ទាត់ AB ដោយដកចំណុច B ។"
    return it("locus_quotient", "hard", pr, s_, an, ck, sp_, alt)
def f_apol(rng):
    k = rng.choice([2, 2, 2, 3]); v = rng.choice([1, I, 1+I, 2, -1, -I, 1-I, 2*I, 1+2*I]) ; b = rz(rng, 2); d = 3 if k == 2 else 8
    a = E(b+d*v); cen = E(b-v*(1 if k == 2 else 1)); r = k*md(v)
    a1, a2 = ri(a); b1, b2 = ri(b); form = rng.randrange(2)
    cond = "|z-"+par(a)+"|=%d|z-" % k+par(b)+"|" if form == 0 else "\\left|"+fr("z-"+par(a), "z-"+par(b))+"\\right|=%d" % k
    pr = rng.choice(SETM) + " " + D(cond) + " ។" + rng.choice(["", " បង្ហាញថាវាជារង្វង់ រួចរកផ្ចិត និងកាំ ។"])
    e = sp.expand(((X-a1)**2+(Y-a2)**2-k*k*((X-b1)**2+(Y-b2)**2))/(1-k*k))
    s_ = ("លក្ខខណ្ឌសមមូលនឹង " + D("|z-"+par(a)+"|=%d|z-" % k+par(b)+"|") + " ជាមួយ " + D("z\\neq "+zt(b)) + " ។\n" if form else "") + "តាង " + D("A("+zt(a)+")") + " និង " + D("B("+zt(b)+")") + " ។ លក្ខខណ្ឌមានន័យថា " + D("MA=%dMB" % k) + " ។\n" + rng.choice(ZXY) + "ការេអង្គទាំងពីរ ៖" + DD(sqb(a1, X)+"+"+sqb(a2, Y)+"=%d\\left[" % (k*k)+sqb(b1, X)+"+"+sqb(b2, Y)+"\\right]")
    s_ += "ពន្លាត រួចចែកនឹង " + D(str(k*k-1)) + " គេបាន" + DD(L(e)+"=0") + "បំពេញជាការេ ៖" + DD(circ_eq(cen, r*r)) + fin("សំណុំចំណុច " + D("M") + " គឺរង្វង់ផ្ចិត " + D("\\boxed{\\Omega("+zt(cen)+")}") + " កាំ " + D("\\boxed{r="+L(r)+"}") + " ។")
    pts = [E(cen+r*v/md(v)), E(cen-r*v/md(v)), E(cen+r*I*v/md(v))]
    ck = [("Abs(%s-%s)/Abs(%s-%s)" % (C(p), C(a), C(p), C(b)), str(k), "point") for p in pts]
    return it("locus_ratio_distance", "hard", pr, s_, "\\Omega("+zt(cen)+"),\\ r="+L(r), ck, {"pts": [("A", a), ("B", b), ("\\Omega", cen)], "circ": [(cen, r)]}, "រង្វង់ដែលចម្ងាយទៅ A ស្មើ %d ដងចម្ងាយទៅ B ដែល A និង B ជារូបភាពនៃ %s និង %s ។" % (k, zt(a), zt(b)))
def f_region(rng):
    c = rz(rng); r1, r2 = rng.choice([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)]); t = rng.choice([1+I, 2, 3*I, 2+I, 1-2*I, 3+I, -2+I]); tp = E(c+t); d = md(t); ann = rng.random() < .6
    if ann:
        cond = D("%d\\le|z-" % r1+par(c)+"|\\le %d" % r2); desc = "ផ្ទៃរវាងរង្វង់ពីរដែលមានផ្ចិតរួម " + D("\\Omega("+zt(c)+")") + " កាំ " + D(str(r1)) + " និង " + D(str(r2)) + " រួមទាំងរង្វង់ទាំងពីរ"; inside = r1 <= d <= r2
    else:
        cond = D("|z-"+par(c)+"|\\le %d" % r2); desc = "ផ្ទៃក្នុងរង្វង់ផ្ចិត " + D("\\Omega("+zt(c)+")") + " កាំ " + D(str(r2)) + " រួមទាំងរង្វង់នោះ"; inside = d <= r2
    pr = "គេឱ្យលក្ខខណ្ឌ " + cond + " ។ ពិពណ៌នា និងគូសសំណុំចំណុច " + D("M(z)") + " ដែលផ្ទៀងផ្ទាត់លក្ខខណ្ឌនេះ ។ តើចំណុច " + D("T") + " រូបភាពនៃ " + D(zt(tp)) + " ស្ថិតក្នុងសំណុំនេះឬទេ ?"
    s_ = "តាង " + D("\\Omega") + " ជារូបភាពនៃ " + D(zt(c)) + " ។ កន្សោម " + D("|z-"+par(c)+"|") + " គឺចម្ងាយ " + D("\\Omega M") + " ។ សំណុំនេះគឺ" + desc + " ។\nសម្រាប់ចំណុច " + D("T") + " ៖" + DD("\\Omega T=|"+par(tp)+"-"+par(c)+"|=|"+zt(t)+"|="+modst(t))
    s_ += fin("សំណុំគឺ" + desc + " ហើយចំណុច " + D("T") + (" ស្ថិតក្នុងសំណុំនេះ ។" if inside else " មិនស្ថិតក្នុងសំណុំនេះទេ ។"))
    ck = [("Abs(%s-%s)" % (C(tp), C(c)), str(d), "distance")]
    return it("locus_region", "medium", pr, s_, "\\Omega T="+L(d), ck, {"pts": [("\\Omega", c), ("T", tp)], "disk": [(c, r1 if ann else 0, r2)], "circ": [(c, r2)]+([(c, r1)] if ann else [])}, "ផ្ទៃដែលបានគូសពណ៌ជុំវិញផ្ចិត Ω ។")
def f_ray(rng):
    th = rng.choice([pi/4, -pi/4, 3*pi/4, -3*pi/4, pi/2, -pi/2, pi/3, -pi/3, 2*pi/3]); a = rz(rng); a1, a2 = ri(a); cs, sn = sp.cos(th), sp.sin(th); t = 2
    pr = "គេឱ្យ " + D("z\\neq "+zt(a)) + " ជាចំនួនកុំផ្លិចដែលមានរូបភាព " + D("M") + " ។ រកសំណុំចំណុច " + D("M") + " ដើម្បីឱ្យអាគុយម៉ង់នៃ " + D("z-"+par(a)) + " ស្មើ " + D(L(th)+"+2k\\pi") + " ។"
    u = E(cs+I*sn); s_ = "តាង " + D("A") + " ជារូបភាពនៃ " + D(zt(a)) + " ។ អាគុយម៉ង់នៃ " + D("z-"+par(a)) + " គឺមុំ " + D("(\\vec{i},\\overrightarrow{AM})") + " ។ គេបាន " + D("(\\vec{i},\\overrightarrow{AM})="+L(th)+"+2k\\pi") + " ។\nនោះមានចំនួនពិត " + D("t>0") + " ដែល " + D("z-"+par(a)+"=t"+tf(1, th)+"=t\\left("+zt(u)+"\\right)") + " ។\n"
    s_ += fin("សំណុំចំណុច " + D("M") + " គឺកន្លះបន្ទាត់ដែលចេញពី " + D("\\boxed{A("+zt(a)+")}") + " ទៅតាមទិសនៃវ៉ិចទ័រដែលមានចំនួនកុំផ្លិច " + D("\\boxed{"+zt(u)+"}") + " ដោយដកចំណុច " + D("A") + " ចេញ ។")
    pt = E(a+t*u); ck = [("arg(expand(%s-%s))" % (C(pt), C(a)), str(th), "point t=2"), ("arg(expand(%s-%s))" % (C(E(a+3*u)), C(a)), str(th), "point t=3")]
    return it("locus_half_line", "medium", pr, s_, "A("+zt(a)+")", ck, {"pts": [("A", a)], "ray": [(a, pt)]}, "កន្លះបន្ទាត់ចេញពី A ។")
def f_paramc(rng):
    c = rz(rng); r = rng.choice([1, 2, 3, 4]); cx, cy = ri(c)
    v = rng.randrange(2); rs = "" if r == 1 else str(r); zz = (L(cx)+"+"+rs+"\\cos t" if cx else rs+"\\cos t"); wy = (L(cy)+"+"+rs+"\\sin t" if cy else rs+"\\sin t")
    pr = "គេឱ្យ " + D("z=("+zz+")+("+wy+")i") + " ដែល " + D("t") + " ជាចំនួនពិត ។ " + rng.choice(["ពេល $t$ ប្រែប្រួល រកសំណុំចំណុច $M(z)$ ។", "តើរូបភាព $M$ នៃ $z$ រត់លើខ្សែអ្វី ពេល $t$ យកគ្រប់តម្លៃពិត ?"])
    s_ = rng.choice(["តាង $z=x+iy$ ។ ផ្ទឹមផ្នែកពិត និងផ្នែកនិមិត្ត ៖", "យើងកំណត់ $x$ និង $y$ ៖"]) + DD("x="+zz+",\\quad y="+wy) + "នាំឱ្យ " + D(L(X-cx)+"="+rs+"\\cos t") + " និង " + D(L(Y-cy)+"="+rs+"\\sin t") + " ។ ដោយ " + D("\\cos^{2}t+\\sin^{2}t=1") + " គេបាន" + DD(circ_eq(c, r*r)) + fin("ចំណុច " + D("M") + " រត់លើរង្វង់ផ្ចិត " + D("\\boxed{\\Omega("+zt(c)+")}") + " កាំ " + D("\\boxed{r=%d}" % r) + " ។")
    ck = [("Abs((%s)+(%d)*(cos(pi/3)+I*sin(pi/3))-%s)" % (C(c), r, C(c)), str(r), "t=pi/3"), ("Abs((%s)+(%d)*(cos(pi/4)+I*sin(pi/4))-%s)" % (C(c), r, C(c)), str(r), "t=pi/4")]
    return it("locus_parametric", "medium", pr, s_, "\\Omega("+zt(c)+"),\\ r=%d" % r, ck, {"pts": [("\\Omega", c)], "circ": [(c, r)]}, "រង្វង់ដែលចំណុច M រត់ពេល t ប្រែប្រួល ។")

# ---- transformations ----
TH = [(pi/2, I), (-pi/2, -I), (pi, -1), (pi/3, R(1, 2)+sqrt(3)/2*I), (-pi/3, R(1, 2)-sqrt(3)/2*I), (2*pi/3, -R(1, 2)+sqrt(3)/2*I)]
def rt(rng): return rng.choice(TH)
def mapn(a):
    return zt(a) if ri(a)[0] == 0 or ri(a)[1] == 0 else "\\left("+zt(a)+"\\right)"
def mapstr(a, b):
    return ("" if a == 1 else ("-" if a == -1 else mapn(a))) + "z" + ("" if b == 0 else ("+"+zt(b) if not zt(b).startswith("-") else zt(b)))
TN = ["ភ្ជាប់ចំណុច $M(z)$ ទៅចំណុច $M'(z')$", "បំលែងចំណុច $M(z)$ ទៅជាចំណុច $M'(z')$", "ឱ្យត្រូវចំណុច $M(z)$ នឹងចំណុច $M'(z')$"]
def f_trans(rng):
    b = rz(rng); 
    if b == 0: b = 2+I
    a, c = rz(rng), rz(rng); r = rng.choice([1, 2, 3])
    pr = "គេឱ្យបំលែង " + D("T") + " " + rng.choice(TN) + " ដោយ " + D("z'=z+"+par(b)) + " ។ រកវ៉ិចទ័រនៃការរំកិល រូបភាពនៃចំណុច " + D("A("+zt(a)+")") + " និងសមីការរូបភាពនៃរង្វង់ " + D("|z-"+par(c)+"|=%d" % r) + " ។"
    a2, c2 = E(a+b), E(c+b)
    s_ = "យើងមាន " + D("z'-z="+zt(b)) + " ជាចំនួនថេរ ។ មានន័យថា " + D("\\overrightarrow{MM'}") + " ជាវ៉ិចទ័រថេរ " + D("\\vec{u}") + " ដែលមានចំនួនកុំផ្លិច " + D(zt(b)) + " ដូច្នេះ " + D("T") + " ជាការរំកិលតាមវ៉ិចទ័រ " + D("\\vec{u}") + " ។\nរូបភាពនៃ " + D("A") + " ៖ " + D("z_{A'}="+par(a)+"+"+par(b)+"="+zt(a2)) + " ។\nការរំកិលរក្សាប្រវែង ដូច្នេះរង្វង់ផ្ចិត " + D(zt(c)) + " កាំ " + D(str(r)) + " ទៅជារង្វង់ផ្ចិត " + D(par(c)+"+"+par(b)+"="+zt(c2)) + " កាំដដែល ។\n"
    s_ += fin(D("\\boxed{z_{A'}="+zt(a2)+"}") + " ហើយរង្វង់រូបភាពមានសមីការ " + D("\\boxed{|z'-"+par(c2)+"|=%d}" % r) + " ។")
    ck = [("%s+%s" % (C(a), C(b)), str(a2), "A'"), ("Abs((%s+%d)+%s-(%s))" % (C(c), r, C(b), C(c2)), str(r), "image of a circle point")]
    return it("translation", "easy", pr, s_, "z_{A'}="+zt(a2), ck, {"pts": [("A", a), ("A'", a2)], "vec": [(a, a2)], "circ": [(c, r), (c2, r)]}, "ការរំកិលនៃចំណុច A និងរង្វង់ ។")
def f_rot(rng):
    th, w = rt(rng); om = rz(rng, 2); d = rng.choice([2, 2*I, -2, 4, 1+I, 2+2*I]) if sp.sympify(w).has(sqrt(3)) else rng.choice(U[:15]); a = E(om+d); im = E(om+w*d); bb = E(-w*om+om)
    pr = rng.choice(["គេឱ្យចំណុច " + D("\\Omega("+zt(om)+")") + " និង " + D("A("+zt(a)+")") + " ក្នុងប្លង់កុំផ្លិច ។ រកចំនួនកុំផ្លិចនៃចំណុច " + D("A'") + " ដែលបានពីការបង្វិល " + D("A") + " ជុំវិញ " + D("\\Omega") + " មុំ " + D(L(th)) + " ។",
                     "ការបង្វិលផ្ចិត " + D("\\Omega("+zt(om)+")") + " មុំ " + D(L(th)) + " " + rng.choice(TN) + " ។ សរសេរ " + D("z'") + " ជាអនុគមន៍នៃ " + D("z") + " រួចរករូបភាពនៃ " + D("A("+zt(a)+")") + " ។"])
    s_ = "តាមការបង្វិល គេមាន " + D("\\Omega M'=\\Omega M") + " និង " + D("(\\overrightarrow{\\Omega M},\\overrightarrow{\\Omega M'})="+L(th)) + " មានន័យថា" + DD("z'-z_\\Omega="+tf(1, th)+"(z-z_\\Omega)") + "ដោយ " + D(tf(1, th)+"="+zt(w)) + " គេបាន" + DD("z'="+mapn(w)+"\\left(z-"+par(om)+"\\right)+"+par(om)+"="+mapstr(w, bb)) + "ជំនួស " + D("z="+zt(a)) + " ៖" + DD("z_{A'}="+mapn(w)+par(d)+"+"+par(om)+"="+zt(im))
    s_ += fin("រូបមន្តបង្វិលគឺ " + D("z'="+mapstr(w, bb)) + " ហើយ " + D("\\boxed{z_{A'}="+zt(im)+"}") + " ។")
    ck = [("(%s)*(%s-%s)+%s" % (C(sp.cos(th)+I*sp.sin(th)), C(a), C(om), C(om)), str(im), "A'"), ("Abs(%s-%s)-Abs(%s-%s)" % (C(im), C(om), C(a), C(om)), "0", "distance kept"), ("arg(expand((%s-%s)*conjugate(%s-%s)))" % (C(im), C(om), C(a), C(om)), str(th), "angle")]
    return it("rotation", "medium", pr, s_, "z_{A'}="+zt(im), ck, {"pts": [("\\Omega", om), ("A", a), ("A'", im)], "seg": [(om, a), (om, im)]}, "ការបង្វិលចំណុច A ជុំវិញ Ω ។")
def f_homot(rng):
    k = rng.choice([2, 3, -2, -1, R(1, 2), -3, R(3, 2)]); om = rz(rng, 2); a = E(om+rng.choice(U[:12])*2); b = E(om+rng.choice(U[:12])*2)
    if a == b: b = E(b+2)
    bb = E((1-k)*om); a2, b2 = E(om+k*(a-om)), E(om+k*(b-om))
    pr = "ការពង្រីកផ្ចិត " + D("\\Omega("+zt(om)+")") + " ផលធៀប " + D("k="+L(k)) + " " + rng.choice(TN) + " ។ សរសេរ " + D("z'") + " តាម " + D("z") + " ។ រករូបភាព " + D("A'") + " និង " + D("B'") + " នៃ " + D("A("+zt(a)+")") + " និង " + D("B("+zt(b)+")") + " រួចផ្ទៀងផ្ទាត់ថា " + D("A'B'=|k|\\,AB") + " ។"
    s_ = "លក្ខខណ្ឌនៃការពង្រីកគឺ " + D("\\overrightarrow{\\Omega M'}=k\\,\\overrightarrow{\\Omega M}") + " ដូច្នេះ " + D("z'-z_\\Omega=k(z-z_\\Omega)") + " ។ គេបាន" + DD("z'="+L(k)+"\\left(z-"+par(om)+"\\right)+"+par(om)+"="+mapstr(k, bb))
    s_ += "រូបភាព ៖" + DD("z_{A'}="+zt(a2)+",\\quad z_{B'}="+zt(b2)) + "ប្រវែង ៖" + DD("AB=|"+zt(b-a)+"|="+modst(b-a)) + DD("A'B'=|"+zt(b2-a2)+"|="+modst(b2-a2)).lstrip("\n")
    d1, d2 = md(b-a), md(b2-a2); s_ += "យើងឃើញថា " + D(L(d2)+"="+L(abs(k))+"\\times "+L(d1)) + " ។\n" + fin(D("\\boxed{z'="+mapstr(k, bb)+"}") + " , " + D("z_{A'}="+zt(a2)) + " , " + D("z_{B'}="+zt(b2)) + " ហើយ " + D("A'B'=|k|\\,AB") + " ពិត ។")
    ck = [("(%s)*(%s-%s)+%s" % (k, C(a), C(om), C(om)), str(a2), "A'"), ("(%s)*(%s-%s)+%s" % (k, C(b), C(om), C(om)), str(b2), "B'"), ("Abs(%s-%s)/Abs(%s-%s)" % (C(b2), C(a2), C(b), C(a)), str(abs(k)), "ratio")]
    return it("homothety", "medium", pr, s_, "z'="+mapstr(k, bb), ck, {"pts": [("\\Omega", om), ("A", a), ("B", b), ("A'", a2), ("B'", b2)], "seg": [(a, b), (a2, b2), (om, a2), (om, b2)]}, "ការពង្រីកអង្កត់ AB ទៅ A'B' ពីផ្ចិត Ω ។")
SIM = [(1+I, sqrt(2), pi/4), (1-I, sqrt(2), -pi/4), (2*I, 2, pi/2), (-2*I, 2, -pi/2), (1+sqrt(3)*I, 2, pi/3), (1-sqrt(3)*I, 2, -pi/3), (-1+I, sqrt(2), 3*pi/4), (sqrt(3)+I, 2, pi/6), (3*I, 3, pi/2), (-1-I, sqrt(2), -3*pi/4), (sqrt(3)-I, 2, -pi/6)]
def f_sim(rng):
    a, r, th = rng.choice(SIM); om = rz(rng, 2); bb = E(om*(1-a))
    tt = rng.choice([1, I, 2, 1+I, -1, 2*I]); z0 = E(om+tt); im = E(om+a*tt)
    pr = "គេឱ្យបំលែង " + D("f") + " " + rng.choice(TN) + " ដែល " + D("z'="+mapstr(a, bb)) + " ។ " + rng.choice(["រកចំណុចនឹង $\\Omega$ នៃ $f$ ។ បង្ហាញថា $f$ គឺការបង្វិលជុំវិញ $\\Omega$ រួចពង្រីកពីផ្ចិត $\\Omega$ ហើយកំណត់មុំ និងផលធៀប ។", "កំណត់ចំណុច $\\Omega$ ដែលនៅនឹង ។ សរសេរ $z'-z_\\Omega$ តាម $z-z_\\Omega$ រួចបកស្រាយជាធរណីមាត្រ ។"])
    s_ = "ចំណុចនឹងផ្ទៀងផ្ទាត់ " + D("z="+mapstr(a, bb)) + " ។ គេបាន" + DD("z_\\Omega="+fr(zt(bb), "1-"+par(a))+"="+zt(om)) + "ដកទំនាក់ទំនងទាំងពីរ " + D("z'="+mapstr(a, bb)) + " និង " + D("z_\\Omega="+mapn(a)+"z_\\Omega"+("+"+zt(bb) if not zt(bb).startswith("-") else zt(bb))) + " គេបាន" + DD("z'-z_\\Omega="+mapn(a)+"(z-z_\\Omega)")
    tx, r2, t2 = argst(a, "a", True); s_ += tx + "\nនាំឱ្យ " + D("\\Omega M'="+L(r)+"\\,\\Omega M") + " និង " + D("(\\overrightarrow{\\Omega M},\\overrightarrow{\\Omega M'})="+L(th)+"+2k\\pi") + " ។\n" + fin("ចំណុចនឹងគឺ " + D("\\boxed{\\Omega("+zt(om)+")}") + " ហើយ " + D("f") + " បង្វិលមុំ " + D("\\boxed{"+L(th)+"}") + " រួចពង្រីកផលធៀប " + D("\\boxed{"+L(r)+"}") + " ។")
    ck = [("(%s)*(%s)+(%s)" % (C(a), C(om), C(bb)), str(om), "fixed"), ("Abs(%s)" % C(a), str(r), "ratio"), ("arg(%s)" % C(a), str(th), "angle"), ("((%s)*(%s)+(%s)-(%s))-(%s)*((%s)-(%s))" % (C(a), C(z0), C(bb), C(om), C(a), C(z0), C(om)), "0", "relation")]
    return it("similarity_fixed_point", "hard", pr, s_, "\\Omega("+zt(om)+")", ck, {"pts": [("\\Omega", om), ("M", z0), ("M'", im)], "seg": [(om, z0), (om, im)]}, "ចំណុច M និងរូបភាព M' ពីផ្ចិត Ω ។")
def f_classify(rng):
    t = rng.choice(["tr", "rot", "hom", "rot", "hom"]); om = rz(rng, 2)
    if t == "tr": b = rz(rng) or 1+I; a = sp.Integer(1); res = "ការរំកិលតាមវ៉ិចទ័រដែលមានចំនួនកុំផ្លិច " + D(zt(b)); s0 = "មេគុណនៃ $z$ ស្មើ $1$ ដូច្នេះ $z'-z$ ថេរ ។\n"; ans = "\\vec{u}("+zt(b)+")"; cks = [("((2+I)+(%s))-(2+I)" % C(b), str(E(b)), "z'-z")]
    elif t == "rot":
        th, a = rt(rng); b = E(om*(1-a)); res = "ការបង្វិលផ្ចិត " + D("\\Omega("+zt(om)+")") + " មុំ " + D(L(th)); ans = "\\Omega("+zt(om)+"),\\ "+L(th)
        s0 = "យើងមាន " + D("|"+zt(a)+"|=1") + " ដូច្នេះ " + D(mapn(a)+"="+tf(1, th)) + " ។ ចំណុចនឹងគឺ " + D("z_\\Omega="+fr(zt(b), "1-"+par(a))+"="+zt(om)) + " ។\n"; cks = [("(%s)*(%s)+(%s)" % (C(a), C(om), C(b)), str(om), "fixed"), ("arg(%s)" % C(a), str(th), "angle")]
    else:
        a = sp.Integer(rng.choice([2, 3, -2, -3])); b = E(om*(1-a)); res = "ការពង្រីកផ្ចិត " + D("\\Omega("+zt(om)+")") + " ផលធៀប " + D(L(a)); ans = "\\Omega("+zt(om)+"),\\ k="+L(a)
        s0 = "មេគុណនៃ $z$ ជាចំនួនពិត " + D("k="+L(a)) + " ខុសពី $1$ ។ ចំណុចនឹងគឺ " + D("z_\\Omega="+fr(zt(b), "1-"+par(a))+"="+zt(om)) + " ។ គេបាន " + D("z'-z_\\Omega="+L(a)+"(z-z_\\Omega)") + " ។\n"; cks = [("(%s)*(%s)+(%s)" % (C(a), C(om), C(b)), str(om), "fixed")]
    pr = "បំលែង " + D("f") + " " + rng.choice(TN) + " មានរូបមន្ត " + D("z'="+mapstr(a, b)) + " ។ " + rng.choice(["តើ $f$ ជាបំលែងអ្វី ? កំណត់ធាតុរបស់វា ។", "កំណត់ប្រភេទនៃ $f$ និងធាតុដែលកំណត់វា ។"])
    pz = rng.choice([1, I, 2, 1+I]); iz = E(a*pz+b)
    s_ = s0 + fin(D("f") + " គឺ" + res + " ។")
    return it("transformation_classify", "medium", pr, s_, ans, cks, {"pts": ([("\\Omega", om)] if t != "tr" else [])+[("M", pz), ("M'", iz)], "vec": [(pz, iz)]}, "ឧទាហរណ៍មួយនៃចំណុច M និងរូបភាព M' ។")
def f_compose(rng):
    (t1, a1), (t2, a2) = rt(rng), rng.choice(TH[:3]); b1, b2 = rz(rng, 2), rz(rng, 2)
    if E(a1*a2) == 1: a2 = -a2 if a2 != -1 else I; 
    A = E(a1*a2); B = E(a2*b1+b2); om = dv(B, 1-A); z0 = rng.choice([1, I, 1+I])
    pr = "គេឱ្យបំលែង " + D("f:\\ z'="+mapstr(a1, b1)) + " និង " + D("g:\\ z''="+mapstr(a2, b2).replace("z", "z'", 1)) + " ។ រករូបមន្តនៃ " + D("z''") + " តាម " + D("z") + " និងចំណុចនឹងនៃបំលែងផ្គុំនេះ ។"
    s_ = "ជំនួស " + D("z'") + " ក្នុង " + D("z''") + " ៖" + DD("z''="+mapn(a2)+"\\left("+mapstr(a1, b1)+"\\right)"+("+"+zt(b2) if not zt(b2).startswith("-") else (zt(b2) if b2 != 0 else ""))+"="+mapstr(A, B)) + "ចំណុចនឹងផ្ទៀងផ្ទាត់ " + D("z="+mapstr(A, B)) + " ។ គេបាន" + DD("z="+divst(B, E(1-A))) + fin(D("\\boxed{z''="+mapstr(A, B)+"}") + " ហើយចំណុចនឹងគឺ " + D("\\boxed{"+zt(om)+"}") + " ។")
    ck = [("(%s)*((%s)*(%s)+(%s))+(%s)" % (C(a2), C(a1), C(z0), C(b1), C(b2)), str(E(A*z0+B)), "instance"), ("expand((%s)*(%s)+(%s)-(%s))" % (C(A), C(om), C(B), C(om)), "0", "fixed")]
    return it("composition", "hard", pr, s_, "z''="+mapstr(A, B), ck, {"pts": [("\\Omega", om), ("M", z0), ("M''", E(A*z0+B))]}, "ចំណុចនឹង Ω ជាមួយឧទាហរណ៍ M និង M'' ។")
def f_image_circle(rng):
    a, r0, th = rng.choice(SIM+[(2, 2, 0), (3, 3, 0), (-2, 2, pi)]); b = rz(rng, 2); c = rz(rng, 2); r = rng.choice([1, 2, 3]); c2 = E(a*c+b); r2 = r0*r
    pr = "ចំណុច " + D("M(z)") + " រត់លើរង្វង់ " + D("|z-"+par(c)+"|=%d" % r) + " ។ គេឱ្យ " + D("z'="+mapstr(a, b)) + " ។ រកសំណុំចំណុច " + D("M'(z')") + " ។"
    s_ = "ពីរូបមន្ត គេបាន " + D("z'-"+par(c2)+"="+mapn(a)+"\\left(z-"+par(c)+"\\right)") + " ព្រោះ " + D(mapn(a)+("" if par(c).startswith("(") or par(c).startswith("\\left") or not mapn(a) or mapn(a)=="-" else "\\times ")+par(c)+("+"+zt(b) if not zt(b).startswith("-") else (zt(b) if b != 0 else ""))+"="+zt(c2)) + " ។\nយកម៉ូឌុលអង្គទាំងពីរ ៖" + DD("|z'-"+par(c2)+"|=|"+zt(a)+"|\\times|z-"+par(c)+"|="+L(r0)+"\\times %d="%r+L(r2)) + fin("សំណុំចំណុច " + D("M'") + " គឺរង្វង់ផ្ចិត " + D("\\boxed{"+zt(c2)+"}") + " កាំ " + D("\\boxed{"+L(r2)+"}") + " ។")
    ck = [("Abs((%s)*((%s)+%d)+(%s)-(%s))" % (C(a), C(c), r, C(b), C(c2)), str(r2), "point 1"), ("Abs((%s)*((%s)+%d*I)+(%s)-(%s))" % (C(a), C(c), r, C(b), C(c2)), str(r2), "point 2"), ("Abs((%s)*((%s)-%d)+(%s)-(%s))" % (C(a), C(c), r, C(b), C(c2)), str(r2), "point 3")]
    return it("image_of_circle", "hard", pr, s_, "\\Omega'("+zt(c2)+"),\\ r'="+L(r2), ck, {"pts": [("\\Omega", c), ("\\Omega'", c2)], "circ": [(c, r), (c2, r2)]}, "រង្វង់ដើម និងរង្វង់រូបភាព ។")

# ---- equations and roots ----
def f_roots_tri(rng):
    p = rng.choice([1, 2, 3, -1, -2]); b = rng.choice([1, 2, 3, 4]); S, Pq = 2*p, p*p+b*b; z1, z2 = p+b*I, p-b*I; t = rng.choice([1, 2]); cpt = p+t*b
    k = "ri" if t == 1 else "iso"
    Q = "z^{2}"+("-%dz" % S if S > 0 else "+%dz" % (-S))+"+%d=0" % Pq
    pr = "ដោះស្រាយសមីការ " + D(Q) + " ក្នុងសំណុំចំនួនកុំផ្លិច ។ តាង " + D("A") + " និង " + D("B") + " ជារូបភាពនៃឫសទាំងពីរ ដោយ " + D("A") + " មានផ្នែកនិមិត្តវិជ្ជមាន ហើយ " + D("C") + " ជារូបភាពនៃ " + D(str(cpt)) + " ។ រកប្រភេទនៃត្រីកោណ " + D("ABC") + " ។"
    s_ = "សមីការមាន " + D("\\Delta'=" + sq(p) + "-%d=%d=(%di)^{2}" % (Pq, -b*b, b)) + " ។ ឫសគឺ " + D("z_1="+zt(z1)) + " និង " + D("z_2="+zt(z2)) + " ។\n"
    ps = [P("A", "z_1", z1), P("B", "z_2", z2), P("C", "z_C", cpt)]; A, B, C_ = ps
    s_ += "ប្រវែងជ្រុង ៖" + DD(dl(C_, A)) + DD(dl(C_, B)).lstrip("\n") + DD(dl(A, B)).lstrip("\n")
    if k == "ri": s_ += "យើងឃើញថា " + D("CA=CB") + " ហើយ " + D("AB^{2}=%d=CA^{2}+CB^{2}" % (4*b*b)) + " ។\n"; res = "ត្រីកោណកែងសមបាតត្រង់ $C$"
    else: s_ += "យើងឃើញថា " + D("CA=CB") + " តែ " + D("AB^{2}\\neq CA^{2}+CB^{2}") + " ។\n"; res = "ត្រីកោណសមបាតត្រង់ $C$"
    s_ += fin("ឫសគឺ " + D("\\boxed{"+zt(z1)+"}") + " និង " + D("\\boxed{"+zt(z2)+"}") + " ហើយ " + D("ABC") + " ជា" + res + " ។")
    ck = [("expand((%s)**2-(%d)*(%s)+%d)" % (C(z1), S, C(z1), Pq), "0", "root"), ("expand((%s)**2-(%d)*(%s)+%d)" % (C(z2), S, C(z2), Pq), "0", "root")] + chk_d(ps)
    return it("equation_roots_triangle", "hard", pr, s_, "z=" + zt(z1) + ",\\ z=" + zt(z2), ck, spec_of(ps), "ត្រីកោណដែលកំពូលជារូបភាពនៃឫស ឆ្លុះនឹងអ័ក្សពិត ។")
def f_unity(rng):
    n, rho, w0 = rng.choice([(3, 2, 8), (3, 2, -8), (3, 2, 8*I), (3, 2, -8*I), (3, 1, 1), (3, 1, I), (4, 2, 16), (4, 1, 1), (4, 2, -16), (4, 1, -1), (6, 1, 1), (6, 2, 64), (6, 1, -1), (4, 3, 81), (3, 4, 64), (3, 3, 27), (3, 3, -27)])
    th0 = sp.arg(w0); ang = [th0/n+2*k*pi/n for k in range(n)]; zs = [E(rho*(sp.cos(t)+I*sp.sin(t))) for t in ang]
    side = sp.radsimp(md(zs[1]-zs[0])); nm = {3: "ត្រីកោណសម័ង្ស", 4: "ការេ", 6: "ឆកោណនិយ័ត"}[n]
    pr = "ដោះស្រាយសមីការ " + D("z^{%d}=%s" % (n, zt(w0))) + " ក្នុងសំណុំចំនួនកុំផ្លិច ដោយប្រើទម្រង់ត្រីកោណមាត្រ ។ បង្ហាញថារូបភាពនៃឫសទាំងអស់ជាកំពូលនៃ" + nm + " រួចគណនាប្រវែងជ្រុង ។"
    s_ = "តាង " + D("z=r(\\cos\\alpha+i\\sin\\alpha)") + " ។ យើងមាន " + D(zt(w0)+"="+tf(abs(w0), th0) if th0 != 0 else zt(w0)+"="+L(abs(w0))+"\\left(\\cos 0+i\\sin 0\\right)") + " ។ តាមរូបមន្តដឺម័រ" + DD("r^{%d}=%s,\\quad %d\\alpha=%s+2k\\pi" % (n, L(abs(w0)), n, L(th0))) + "នាំឱ្យ " + D("r=%d" % rho) + " និង " + D("\\alpha="+fr(L(th0)+"+2k\\pi", n)) + " ដែល " + D("k="+",".join(str(j) for j in range(n))) + " ។\nឫសគឺ ៖" + DD(",\\quad ".join("z_{%d}=%s" % (j, zt(z)) for j, z in enumerate(zs)))
    s_ += "ឫសទាំងអស់មានម៉ូឌុល " + D(str(rho)) + " ដូច្នេះរូបភាពនៅលើរង្វង់ផ្ចិត " + D("O") + " កាំ " + D(str(rho)) + " ហើយមុំរវាងឫសជាប់គ្នាស្មើ " + D(L(2*pi/n)) + " ។ ជ្រុង ៖" + DD("|z_1-z_0|=|"+zt(zs[1]-zs[0])+"|="+L(side)) + fin("រូបភាពនៃឫសជាកំពូលនៃ" + nm + " ដែលមានប្រវែងជ្រុង " + D("\\boxed{"+L(side)+"}") + " ។")
    ck = [("expand(%s**%d)" % (C(z), n), str(w0), "root") for z in zs] + [("Abs(%s-%s)" % (C(zs[1]), C(zs[0])), str(side), "side")]
    return it("roots_regular_polygon", "hard", pr, s_, "\\ell="+L(side), ck, {"pts": [("Z_{%d}" % j, z) for j, z in enumerate(zs)], "poly": [zs], "circ": [(0, rho)]}, "ពហុកោណនិយ័តចារឹកក្នុងរង្វង់ផ្ចិត O ។")

# ---- exam-style multi-part items ----
def assemble(rng, t, parts):
    lab = rng.choice(LABS); pr = t; s_ = ""; ck = []
    for l, (q, a, c) in zip(lab, parts):
        pr += "\n" + l + " " + q; s_ += l + " " + a.strip() + "\n"; ck += c
    return pr, s_
def f_exam_tri(rng):
    kind = rng.choice(["ri", "ri", "r", "iso", "eq"]); ps, t = setup(rng, tri(rng, kind)); nm = "".join(p.l for p in ps)
    k, i = nature(*[p.v for p in ps]); V, W1, W2 = ps[i], ps[(i+1) % 3], ps[(i+2) % 3]; cks = []
    parts = []; add = []
    coords = join(D(p.l+"("+L(ri(p.v)[0])+";"+L(ri(p.v)[1])+")") for p in ps)
    if not any(ri(p.v)[1].has(sqrt(3)) or ri(p.v)[0].has(sqrt(3)) for p in ps) and rng.random() < .7:
        parts.append(("ដៅចំណុច " + join(D(p.l) for p in ps) + " ក្នុងប្លង់កុំផ្លិច ។", "ចំណុចមានកូអរដោនេ " + coords + " ។ យើងដៅវាដូចរូប ។", []))
    ds, _, _ = tri_dist_sol(ps, rng); parts.append((rng.choice(["គណនាប្រវែងជ្រុង រួចទាញរកប្រភេទនៃត្រីកោណ " + D(nm) + " ។", "កំណត់ប្រភេទនៃត្រីកោណ " + D(nm) + " ដោយប្រើចម្ងាយ ។"]), ds + "ដូចនេះ " + D(nm) + " ជា" + nat_txt(k, V.l) + " ។", chk_d(ps)))
    u, w = W1.v-V.v, W2.v-V.v
    if k in ("ri", "r") or k == "eq":
        q = dv(w, u); tx, r, th = argst(q, "w")
        parts.append(("គណនា " + D("w="+fr(W2.n+"-"+V.n, W1.n+"-"+V.n)) + " រួចរកម៉ូឌុល និងអាគុយម៉ង់នៃ " + D("w") + " ។", "យើងបាន" + DD("w="+divst(w, u)) + tx + "\nដូចនេះ " + D("w="+tf(r, th)) + " ។", [("expand((%s-%s)*conjugate(%s-%s))/%s" % (C(W2.v), C(V.v), C(W1.v), C(V.v), n2(u)), str(q), "w"), ("arg(expand((%s-%s)*conjugate(%s-%s)))" % (C(W2.v), C(V.v), C(W1.v), C(V.v)), str(th), "angle")]))
    # area
    area = abs(sp.im(E(u*cj(w))))/2
    if k in ("ri", "r"): ar = "ត្រីកោណកែងត្រង់ " + D(V.l) + " មានផ្ទៃក្រឡា " + D("S="+fr(1, 2)+"\\times "+V.l+W1.l+"\\times "+V.l+W2.l+"="+fr(1, 2)+"\\times "+L(md(u))+"\\times "+L(md(w))+"="+L(area))
    elif k == "eq": ar = "ត្រីកោណសម័ង្សជ្រុង " + D("a="+L(md(u))) + " មានផ្ទៃក្រឡា " + D("S="+fr("a^{2}\\sqrt{3}", 4)+"="+L(area))
    else:
        mid = P("H", "z_H", E((W1.v+W2.v)/2)); ar = "ចំណុចកណ្តាល " + D("H") + " នៃបាត " + D("["+W1.l+W2.l+"]") + " មាន " + D("z_H="+zt(mid.v)) + " ហើយកម្ពស់ " + D(V.l+"H="+L(md(mid.v-V.v))) + " ។ គេបាន " + D("S="+fr(1, 2)+"\\times "+L(md(W2.v-W1.v))+"\\times "+L(md(mid.v-V.v))+"="+L(area))
    parts.append(("គណនាផ្ទៃក្រឡានៃត្រីកោណ " + D(nm) + " ។", ar + " ឯកតាផ្ទៃក្រឡា ។", [("Abs(im(expand((%s-%s)*conjugate(%s-%s))))/2" % (C(W1.v), C(V.v), C(W2.v), C(V.v)), str(area), "area")]))
    d = E(W1.v+W2.v-V.v); qn = {"ri": "ការេ", "r": "ចតុកោណកែង", "iso": "ចតុកោណស្មើ", "eq": "ចតុកោណស្មើ"}[k]; Dl = "F" if "F" not in nm else "G"
    parts.append(("រកចំនួនកុំផ្លិច " + D("z_"+Dl) + " ដើម្បីឱ្យ " + D(V.l+W1.l+Dl+W2.l) + " ជាប្រលេឡូក្រាម ។ តើចតុកោណនេះមានរាងអ្វី ?", "លក្ខខណ្ឌ " + D(vec(V, W1)+"="+vn(W2.l, Dl)) + " ឱ្យ " + D("z_"+Dl+"="+W1.n+"+"+W2.n+"-"+V.n+"="+zt(d)) + " ។ ព្រោះ " + ({"ri": "មុំ " + D(V.l) + " កែង និងជ្រុងជាប់គ្នាស្មើ", "r": "មុំ " + D(V.l) + " កែង", "iso": "ជ្រុងជាប់គ្នា " + D(V.l+W1.l+"="+V.l+W2.l), "eq": "ជ្រុងជាប់គ្នា " + D(V.l+W1.l+"="+V.l+W2.l)}[k]) + " ប្រលេឡូក្រាមនេះជា" + qn + " ។", [("(%s)+(%s)-(%s)" % (C(W1.v), C(W2.v), C(V.v)), str(d), "fourth")]))
    pts_extra = [(Dl, d)]; circ = []
    if k in ("ri", "r"):
        cen = E((W1.v+W2.v)/2); r = sp.radsimp(md(W1.v-cen))
        parts.append(("រកផ្ចិត " + D("\\Omega") + " និងកាំនៃរង្វង់ចារឹកក្រៅត្រីកោណ " + D(nm) + " ។", "អ៊ីប៉ូតេនុសគឺ " + D("["+W1.l+W2.l+"]") + " ។ គេបាន " + D("z_\\Omega="+fr(W1.n+"+"+W2.n, 2)+"="+zt(cen)) + " និង " + D("r="+fr(W1.l+W2.l, 2)+"="+L(r)) + " ។", [("Abs(%s-%s)" % (C(V.v), C(cen)), str(r), "V on circle")])); circ = [(cen, r)]
    elif k == "iso":
        a1, a2 = ri(W1.v); b1, b2 = ri(W2.v); e = sp.expand(2*(b1-a1)*X+2*(b2-a2)*Y+(a1**2+a2**2-b1**2-b2**2)); e2, le = line_eq(e); vx, vy = ri(V.v)
        parts.append(("រកសំណុំចំណុច " + D("M(z)") + " ដែល " + D("|z-"+W1.n+"|=|z-"+W2.n+"|") + " រួចបង្ហាញថា " + D(V.l) + " ស្ថិតលើសំណុំនេះ ។", "លក្ខខណ្ឌគឺ " + D("M"+W1.l+"=M"+W2.l) + " ដូច្នេះសំណុំគឺមេដ្យាទ័រនៃ " + D("["+W1.l+W2.l+"]") + " ដែលមានសមីការ " + D(le) + " ។ ជំនួសកូអរដោនេ " + D(V.l) + " ឱ្យ " + D(str(e2.subs({X: vx, Y: vy}))+"=0") + " ពិត ព្រោះ " + D(V.l+W1.l+"="+V.l+W2.l) + " ។", [(str(e2.subs({X: vx, Y: vy})), "0", "V on bisector")]))
    if k in ("ri", "r", "iso") and rng.random() < .6:
        im = E(V.v-I*(W1.v-V.v))
        parts.append(("រកចំនួនកុំផ្លិចនៃចំណុច " + D("K") + " ដែលបានពីការបង្វិល " + D(W1.l) + " ជុំវិញ " + D(V.l) + " មុំ " + D("-\\frac{\\pi}{2}") + " ។", "គេមាន " + D("z_K-"+V.n+"=-i("+W1.n+"-"+V.n+")=-i"+par(u)+"="+zt(-I*u)) + " នាំឱ្យ " + D("z_K="+zt(im)) + " ។", [("(%s)-I*((%s)-(%s))" % (C(V.v), C(W1.v), C(V.v)), str(im), "K")]))
    pr, s_ = assemble(rng, t, parts); ck = sum((p[2] for p in parts), [])
    s_ += fin("ត្រីកោណ " + D(nm) + " ជា" + nat_txt(k, V.l) + " មានផ្ទៃក្រឡា " + D("\\boxed{S="+L(area)+"}") + " ។")
    return it("exam_triangle", "bacii", pr, s_, "S="+L(area), ck, spec_of(ps, True, pts=[(p.l, p.v) for p in ps]+pts_extra, seg=[(W1.v, d), (W2.v, d)], circ=circ), "ត្រីកោណ " + nm + " ជាមួយចំណុចទីបួន" + (" និងរង្វង់ចារឹកក្រៅ ។" if circ else " ។"))
STDA = [pi/6, pi/3, pi/2, 2*pi/3, 5*pi/6, -pi/6, -pi/3, -pi/2, -2*pi/3, -5*pi/6]
def f_exam_core(rng):
    a1 = rng.choice(STDA); dd = rng.choice([pi/2, pi/3, -pi/2, -pi/3, 2*pi/3]); a2 = a1+dd
    while a2 > pi: a2 -= 2*pi
    while a2 <= -pi: a2 += 2*pi
    r = rng.choice([2, 2, 4]); r2 = r if rng.random() < .75 else r*2
    z1 = E(r*(sp.cos(a1)+I*sp.sin(a1))); z2 = E(r2*(sp.cos(a2)+I*sp.sin(a2)))
    n = rng.choice([3, 4, 6]); pw = E(z1**n); pa = n*a1; 
    while pa > pi: pa -= 2*pi
    while pa <= -pi: pa += 2*pi
    t = rng.choice(["គេមានចំនួនកុំផ្លិច ", "គេឱ្យចំនួនកុំផ្លិច "]) + D("z_1="+zt(z1)) + " និង " + D("z_2="+zt(z2)) + " ។"
    q = dv(z2, z1); parts = []
    t1, _, _ = argst(z1, "z_1"); t2, _, _ = argst(z2, "z_2")
    parts.append(("សរសេរ " + D("z_1") + " និង " + D("z_2") + " ជាទម្រង់ត្រីកោណមាត្រ ។", t1 + " ដូច្នេះ " + D("z_1="+tf(r, a1)) + " ។\n" + t2 + " ដូច្នេះ " + D("z_2="+tf(r2, a2)) + " ។", [("Abs(%s)" % C(z1), str(r), "|z1|"), ("arg(%s)" % C(z1), str(a1), "arg z1"), ("Abs(%s)" % C(z2), str(r2), "|z2|"), ("arg(%s)" % C(z2), str(a2), "arg z2")]))
    tq, rq, thq = argst(q, "w")
    parts.append(("គណនា " + D("w="+fr("z_2", "z_1")) + " ជាទម្រង់ពីជគណិត រួចសរសេរវាជាទម្រង់ត្រីកោណមាត្រ ។", "យើងបាន" + DD("w="+divst(z2, z1)) + tq + "\nដូចនេះ " + D("w="+tf(rq, thq)) + " ។", [("expand((%s)*conjugate(%s))/%s" % (C(z2), C(z1), n2(z1)), str(q), "w")]))
    nat = None
    if r == r2 and abs(dd) == pi/3: nat = "ត្រីកោណសម័ង្ស"
    elif r == r2 and abs(dd) == pi/2: nat = "ត្រីកោណកែងសមបាតត្រង់ $O$"
    elif abs(dd) == pi/2: nat = "ត្រីកោណកែងត្រង់ $O$"
    elif r == r2: nat = "ត្រីកោណសមបាតត្រង់ $O$"
    else: nat = "ត្រីកោណមានមុំកំពូល " + D(L(abs(dd))) + " ត្រង់ $O$"
    A, B = P("A", "z_1", z1), P("B", "z_2", z2)
    parts.append(("តាង " + D("A") + " និង " + D("B") + " ជារូបភាពនៃ " + D("z_1") + " និង " + D("z_2") + " ក្នុងប្លង់កុំផ្លិច ។ ដោយប្រើលទ្ធផលខាងលើ ទាញរកប្រភេទនៃត្រីកោណ " + D("OAB") + " និងគណនា " + D("AB") + " ។", "យើងមាន " + D(fr("OB", "OA")+"=|w|="+L(rq)) + " និង " + D("(\\overrightarrow{OA},\\overrightarrow{OB})="+L(thq)+"+2k\\pi") + " ។ នោះ " + D("OAB") + " ជា" + nat + " ។\nប្រវែង " + D("AB=|z_2-z_1|=|"+zt(z2-z1)+"|="+L(sp.radsimp(md(z2-z1)))) + " ឯកតា ។", [("Abs(%s-%s)" % (C(z2), C(z1)), str(sp.radsimp(md(z2-z1))), "AB")]))
    parts.append(("ទាញរកតម្លៃនៃ " + D("z_1^{%d}" % n) + " ជាទម្រង់ពីជគណិត ។", "តាមរូបមន្តដឺម័រ" + DD("z_1^{%d}=%d^{%d}\\left[\\cos\\left(%d\\times %s\\right)+i\\sin\\left(%d\\times %s\\right)\\right]=%s" % (n, r, n, n, L(a1) if a1 > 0 else "\\left("+L(a1)+"\\right)", n, L(a1) if a1 > 0 else "\\left("+L(a1)+"\\right)", zt(pw))), [("expand(%s**%d)" % (C(z1), n), str(pw), "power")]))
    pr, s_ = assemble(rng, t, parts); ck = sum((p[2] for p in parts), [])
    s_ += fin(D("OAB") + " ជា" + nat + " ហើយ " + D("\\boxed{z_1^{%d}=%s}" % (n, zt(pw))) + " ។")
    return it("exam_trig_form_geometry", "bacii", pr, s_, "z_1^{%d}=%s" % (n, zt(pw)), ck, {"pts": [("O", 0), ("A", z1), ("B", z2)], "poly": [[0, z1, z2]]}, "ត្រីកោណ OAB ដែល A និង B ជារូបភាពនៃ z1 និង z2 ។")
def f_exam_quad(rng):
    kind = rng.choice(["rect", "sq", "rh", "para"]); ps, t = setup(rng, quad(rng, kind)); A, B, C_, Dd = ps; nm = A.l+B.l+C_.l+Dd.l; cen = E((A.v+C_.v)/2)
    u, w = B.v-A.v, Dd.v-A.v; d1, d2 = C_.v-A.v, Dd.v-B.v; area = abs(sp.im(E(u*cj(w)))); parts = []
    parts.append(("ដៅចំណុចទាំងបួនក្នុងប្លង់កុំផ្លិច រួចបង្ហាញថា " + D(nm) + " ជាប្រលេឡូក្រាម ។", "យើងមាន " + D(B.n+"-"+A.n+"="+zt(u)) + " និង " + D(C_.n+"-"+Dd.n+"="+zt(C_.v-Dd.v)) + " ។ ដូចនេះ " + D(vec(A, B)+"="+vec(Dd, C_)) + " ហើយ " + D(nm) + " ជាប្រលេឡូក្រាម ។", [("(%s-%s)-(%s-%s)" % (C(B.v), C(A.v), C(C_.v), C(Dd.v)), "0", "para")]))
    parts.append(("រកចំនួនកុំផ្លិចនៃផ្ចិត " + D("J") + " នៃប្រលេឡូក្រាម ។", D("z_J="+fr(A.n+"+"+C_.n, 2)+"="+fr(zt(A.v+C_.v), 2)+"="+zt(cen)) + " ។ ពិនិត្យ " + D(fr(B.n+"+"+Dd.n, 2)+"="+zt((B.v+Dd.v)/2)) + " ក៏ស្មើដែរ ។", [("(%s+%s)/2" % (C(A.v), C(C_.v)), str(cen), "J"), ("(%s+%s)/2" % (C(B.v), C(Dd.v)), str(cen), "J2")]))
    q = dv(d2, d1); parts.append(("គណនា " + D("q="+fr(Dd.n+"-"+B.n, C_.n+"-"+A.n)) + " ។ តើអង្កត់ទ្រូងទាំងពីរកែងគ្នាឬទេ ?", "យើងបាន" + DD("q="+divst(d2, d1)) + ("ផ្នែកពិតស្មើសូន្យ នោះអង្កត់ទ្រូងកែងគ្នា ។" if sp.re(q) == 0 else "ផ្នែកពិតខុសពីសូន្យ នោះអង្កត់ទ្រូងមិនកែងគ្នាទេ ។"), [("expand((%s-%s)*conjugate(%s-%s))/%s" % (C(Dd.v), C(B.v), C(C_.v), C(A.v), n2(d1)), str(q), "q")]))
    parts.append(("គណនាប្រវែង " + D(A.l+B.l) + " , " + D(A.l+Dd.l) + " , " + D(A.l+C_.l) + " និង " + D(B.l+Dd.l) + " រួចទាញរកប្រភេទនៃ " + D(nm) + " ។", "".join(DD(dl(p, q2)).lstrip("\n") if j else DD(dl(p, q2)) for j, (p, q2) in enumerate([(A, B), (A, Dd), (A, C_), (B, Dd)])) + {"sq": "ជ្រុងជាប់គ្នាស្មើគ្នា ហើយអង្កត់ទ្រូងស្មើគ្នា ដូចនេះវាជាការេ ។", "rect": "អង្កត់ទ្រូងស្មើគ្នា តែជ្រុងជាប់គ្នាមិនស្មើគ្នា ដូចនេះវាជាចតុកោណកែង ។", "rh": "ជ្រុងជាប់គ្នាស្មើគ្នា តែអង្កត់ទ្រូងមិនស្មើគ្នា ដូចនេះវាជាចតុកោណស្មើ ។", "para": "ជ្រុងជាប់គ្នាមិនស្មើគ្នា ហើយអង្កត់ទ្រូងមិនស្មើគ្នា ដូចនេះវាជាប្រលេឡូក្រាមធម្មតា ។"}[kind], [("Abs(%s-%s)" % (C(q2.v), C(p.v)), str(md(q2.v-p.v)), p.l+q2.l) for p, q2 in [(A, B), (A, Dd), (A, C_), (B, Dd)]]))
    parts.append(("គណនាផ្ទៃក្រឡានៃ " + D(nm) + " ។", ({"sq": D("S="+A.l+B.l+"^{2}="+L(area)), "rect": D("S="+A.l+B.l+"\\times "+A.l+Dd.l+"="+L(area)), "rh": D("S="+fr(A.l+C_.l+"\\times "+B.l+Dd.l, 2)+"="+L(area))}.get(kind) or ("តាមវ៉ិចទ័រ " + D(vec(A, B)) + " និង " + D(vec(A, Dd)) + " ផ្ទៃក្រឡាគឺតម្លៃដាច់ខាតនៃផ្នែកនិមិត្តនៃ " + D("\\overline{("+B.n+"-"+A.n+")}("+Dd.n+"-"+A.n+")") + " ។ " + D("\\overline{("+zt(u)+")}("+zt(w)+")="+zt(E(cj(u)*w))) + " នាំឱ្យ " + D("S="+L(area)))) + " ឯកតាផ្ទៃក្រឡា ។", [("Abs(im(expand(conjugate(%s-%s)*(%s-%s))))" % (C(B.v), C(A.v), C(Dd.v), C(A.v)), str(area), "area")]))
    if kind in ("rect", "sq"):
        r = sp.radsimp(md(C_.v-cen)); parts.append(("បង្ហាញថាកំពូលទាំងបួននៅលើរង្វង់តែមួយ រួចសរសេរលក្ខខណ្ឌ " + D("|z-z_J|=r") + " ។", "អង្កត់ទ្រូងស្មើគ្នា ហើយកាត់គ្នាត្រង់ចំណុចកណ្តាល នោះ " + D("J"+A.l+"=J"+B.l+"=J"+C_.l+"=J"+Dd.l+"="+L(r)) + " ។ រង្វង់គឺ " + D("|z-"+par(cen)+"|="+L(r)) + " ។", [("Abs(%s-%s)" % (C(p.v), C(cen)), str(r), p.l) for p in ps]))
    pr, s_ = assemble(rng, t, parts); ck = sum((p[2] for p in parts), [])
    s_ += fin(D(nm) + " ជា" + QN[kind] + " ដែលមានផ្ទៃក្រឡា " + D("\\boxed{S="+L(area)+"}") + " ឯកតាផ្ទៃក្រឡា ។")
    return it("exam_quadrilateral", "bacii", pr, s_, "S="+L(area), ck, spec_of(ps, True, pts=[(p.l, p.v) for p in ps]+[("J", cen)], seg=[(A.v, C_.v), (B.v, Dd.v)]), "ចតុកោណ " + nm + " ជាមួយអង្កត់ទ្រូង និងផ្ចិត J ។")
def f_exam_locus(rng):
    while True:
        a, b = rz(rng, 2)*2, rz(rng, 2)*2
        a, b = E(a), E(b)
        if a != b: break
    rr, ii = quot_parts(a, b); e1, le = line_eq(ii); cen = E((a+b)/2); r = md(a-b)/2; a1, a2 = ri(a); b1, b2 = ri(b)
    den = L((X-b1)**2)+"+"+L((Y-b2)**2); e3 = sp.expand(2*(b1-a1)*X+2*(b2-a2)*Y+(a1**2+a2**2-b1**2-b2**2)); e4, le3 = line_eq(e3)
    t = "គេឱ្យចំនួនកុំផ្លិច " + D("Z="+fr("z-"+par(a), "z-"+par(b))) + " ដែល " + D("z=x+iy") + " , " + D("z\\neq "+zt(b)) + " ។ ក្នុងប្លង់កុំផ្លិច តាង " + D("M(z)") + " , " + D("A("+zt(a)+")") + " និង " + D("B("+zt(b)+")") + " ។"
    p1 = E(cen+r*(a-b)/md(a-b)*I); p2 = E(2*a-b); p3 = E(cen+I*(b-a))
    parts = [("សរសេរផ្នែកពិត និងផ្នែកនិមិត្តនៃ " + D("Z") + " តាម " + D("x") + " និង " + D("y") + " ។", "គុណនឹងចំនួនឆ្លាស់នៃភាគបែង គេបាន" + DD("Z="+fr(L(rr)+"+\\left("+L(ii)+"\\right)i", den)) + "ផ្នែកពិតមានភាគយក " + D(L(rr)) + " ហើយផ្នែកនិមិត្តមានភាគយក " + D(L(ii)) + " ។", [("expand(((%s)-(%s))*conjugate((%s)-(%s)))" % (C(p3), C(a), C(p3), C(b)), str(rr.subs({X: ri(p3)[0], Y: ri(p3)[1]}) + I*ii.subs({X: ri(p3)[0], Y: ri(p3)[1]})), "numerator at a sample z")]),
             ("រកសំណុំ " + D("(\\Gamma_1)") + " នៃចំណុច " + D("M") + " ដែលផ្នែកនិមិត្តនៃ " + D("Z") + " ស្មើសូន្យ ។", "លក្ខខណ្ឌ " + D(L(ii)+"=0") + " សមមូលនឹង " + D(le) + " ។ ដូចនេះ " + D("(\\Gamma_1)") + " គឺបន្ទាត់ " + D("(AB)") + " ដកចំណុច " + D("B") + " ចេញ ។", [("im(expand((%s-%s)*conjugate(%s-%s)))" % (C(p2), C(a), C(p2), C(b)), "0", "on line")]),
             ("រកសំណុំ " + D("(\\Gamma_2)") + " នៃចំណុច " + D("M") + " ដែលផ្នែកពិតនៃ " + D("Z") + " ស្មើសូន្យ ។", "លក្ខខណ្ឌ " + D(L(rr)+"=0") + " ។ បំពេញជាការេ គេបាន " + D(circ_eq(cen, r*r)) + " ។ ដូចនេះ " + D("(\\Gamma_2)") + " គឺរង្វង់អង្កត់ផ្ចិត " + D("[AB]") + " ដកចំណុច " + D("B") + " ចេញ ។", [("re(expand((%s-%s)*conjugate(%s-%s)))" % (C(p1), C(a), C(p1), C(b)), "0", "on circle")]),
             ("រកសំណុំ " + D("(\\Gamma_3)") + " នៃចំណុច " + D("M") + " ដែល " + D("|Z|=1") + " ។", "លក្ខខណ្ឌសមមូលនឹង " + D("MA=MB") + " ។ ដូចនេះ " + D("(\\Gamma_3)") + " គឺមេដ្យាទ័រនៃ " + D("[AB]") + " ដែលមានសមីការ " + D(le3) + " ។", [("Abs(%s-%s)/Abs(%s-%s)" % (C(p3), C(a), C(p3), C(b)), "1", "on bisector")])]
    pr, s_ = assemble(rng, t, parts); ck = sum((p[2] for p in parts), [])
    s_ += fin("សំណុំទាំងបីគឺបន្ទាត់ " + D("\\boxed{"+le+"}") + " , រង្វង់ " + D("\\boxed{"+circ_eq(cen, r*r)+"}") + " និងបន្ទាត់ " + D("\\boxed{"+le3+"}") + " ដោយដកចំណុច " + D("B") + " ចេញពីសំណុំពីរដំបូង ។")
    return it("exam_locus", "bacii", pr, s_, le+",\\ "+circ_eq(cen, r*r), ck, {"pts": [("A", a), ("B", b)], "line": [(a, b), (cen, p3)], "circ": [(cen, r)]}, "បន្ទាត់ AB រង្វង់អង្កត់ផ្ចិត AB និងមេដ្យាទ័រនៃ AB ។")
def f_exam_map(rng):
    a, r0, th = rng.choice(SIM+[(I, 1, pi/2), (-I, 1, -pi/2), (R(1, 2)+sqrt(3)/2*I, 1, pi/3)]); om = rz(rng, 2); bb = E(om*(1-a)); d = rng.choice([2, 2*I, -2, 1+I, 2+2*I, 4]); A0 = E(om+d); A1 = E(om+a*d); c = E(om+rng.choice([1, I, -1, 2*I, 2+I])); rr = rng.choice([1, 2]); c1 = E(a*c+bb); r1 = r0*rr
    t = "គេឱ្យបំលែង " + D("f") + " " + rng.choice(TN) + " កំណត់ដោយ " + D("z'="+mapstr(a, bb)) + " ។"
    tx, _, _ = argst(a, "a", True); nat = {pi/2: "កែងត្រង់ $\\Omega$", -pi/2: "កែងត្រង់ $\\Omega$"}.get(th, "មានមុំ " + D(L(abs(th))) + " ត្រង់ $\\Omega$")
    if r0 == 1: nat = "សម័ង្ស" if abs(th) == pi/3 else "កែងសមបាតត្រង់ $\\Omega$"
    parts = [("រកចំណុចនឹង " + D("\\Omega") + " នៃ " + D("f") + " ។", "ចំណុចនឹងផ្ទៀងផ្ទាត់ " + D("z="+mapstr(a, bb)) + " ។ គេបាន " + D("z_\\Omega="+fr(zt(bb), "1-"+par(a))+"="+zt(om)) + " ។", [("(%s)*(%s)+(%s)" % (C(a), C(om), C(bb)), str(om), "fixed")]),
             ("បង្ហាញថា " + D("z'-z_\\Omega="+mapn(a)+"(z-z_\\Omega)") + " រួចរកម៉ូឌុល និងអាគុយម៉ង់នៃ " + D("a="+zt(a)) + " ។", "ដកទំនាក់ទំនង " + D("z_\\Omega="+mapn(a)+"z_\\Omega"+("+"+zt(bb) if not zt(bb).startswith("-") else zt(bb))) + " ពី " + D("z'="+mapstr(a, bb)) + " គេបានទំនាក់ទំនងដែលត្រូវបង្ហាញ ។\n" + tx, [("Abs(%s)" % C(a), str(r0), "ratio"), ("arg(%s)" % C(a), str(th), "angle")]),
             ("រកចំនួនកុំផ្លិចនៃរូបភាព " + D("A'") + " នៃចំណុច " + D("A("+zt(A0)+")") + " ។ តើត្រីកោណ " + D("\\Omega AA'") + " មានលក្ខណៈអ្វី ?", D("z_{A'}="+mapn(a)+par(A0)+("+"+zt(bb) if not zt(bb).startswith("-") else zt(bb))+"="+zt(A1)) + " ។ ពីទំនាក់ទំនងខាងលើ " + D("\\Omega A'="+L(r0)+"\\,\\Omega A") + " និងមុំ " + D("(\\overrightarrow{\\Omega A},\\overrightarrow{\\Omega A'})="+L(th)) + " ។ ត្រីកោណនេះ" + nat + " ។", [("(%s)*(%s)+(%s)" % (C(a), C(A0), C(bb)), str(A1), "A'")]),
             ("រកសំណុំចំណុច " + D("M'") + " ពេល " + D("M") + " រត់លើរង្វង់ " + D("|z-"+par(c)+"|=%d" % rr) + " ។", "ផ្ចិតទៅជា " + D(mapn(a)+par(c)+("+"+zt(bb) if not zt(bb).startswith("-") else zt(bb))+"="+zt(c1)) + " ហើយកាំគុណនឹង " + D("|a|="+L(r0)) + " ។ សំណុំគឺរង្វង់ " + D("|z'-"+par(c1)+"|="+L(r1)) + " ។", [("Abs((%s)*((%s)+%d)+(%s)-(%s))" % (C(a), C(c), rr, C(bb), C(c1)), str(r1), "circle point")])]
    pr, s_ = assemble(rng, t, parts); ck = sum((p[2] for p in parts), [])
    s_ += fin("ចំណុចនឹងគឺ " + D("\\boxed{\\Omega("+zt(om)+")}") + " ហើយរង្វង់រូបភាពមានកាំ " + D("\\boxed{"+L(r1)+"}") + " ។")
    return it("exam_transformation", "bacii", pr, s_, "\\Omega("+zt(om)+")", ck, {"pts": [("\\Omega", om), ("A", A0), ("A'", A1)], "poly": [[om, A0, A1]], "circ": [(c, rr), (c1, r1)]}, "ត្រីកោណ ΩAA' និងរង្វង់ដើម រង្វង់រូបភាព ។")
def f_exam_eq(rng):
    p = rng.choice([1, 2, -1, -2, 3]); b = rng.choice([1, 2, 3]); r0 = rng.choice([p+b, p-b, p+2*b, p+3*b]); S, Pq = 2*p, p*p+b*b
    Pz = sp.expand((X-r0)*(X**2-S*X+Pq)); co = sp.Poly(Pz, X).all_coeffs()
    poly = L(Pz.subs(X, sp.Symbol("z"))); z1, z2 = p+b*I, p-b*I
    t = "គេឱ្យពហុធា " + D("P(z)="+poly) + " ដែល " + D("z") + " ជាចំនួនកុំផ្លិច ។"
    A, B, Cc = P("A", "z_1", z1), P("B", "z_2", z2), P("C", "z_3", r0); ps = [A, B, Cc]; k, i = nature(z1, z2, sp.Integer(r0))
    if k == "deg": return None
    ptxt = "z^{2}"+("-%dz" % S if S > 0 else "+%dz" % (-S))+"+%d" % Pq
    z_ = sp.Symbol("z")
    parts = [("គណនា " + D("P("+L(r0)+")") + " ។", "ជំនួស " + D("z="+L(r0)) + " គេបាន " + D("P("+L(r0)+")=0") + " ។ ដូចនេះ " + D(L(r0)) + " ជាឫសមួយ ។", [(str(Pz.subs(X, r0)), "0", "P(r0)")]),
             ("រកចំនួនពិត " + D("\\beta") + " និង " + D("\\gamma") + " ដើម្បីឱ្យ " + D("P(z)=\\left("+L(z_-r0)+"\\right)\\left(z^{2}+\\beta z+\\gamma\\right)") + " ។", "ពន្លាត ហើយផ្ទឹមមេគុណ គេបាន " + D("\\beta=%d" % (-S)) + " និង " + D("\\gamma=%d" % Pq) + " ។", [("expand((x-(%s))*(x**2-(%d)*x+%d))" % (r0, S, Pq), str(Pz), "factor")]),
             ("ដោះស្រាយសមីការ " + D("P(z)=0") + " ក្នុងសំណុំចំនួនកុំផ្លិច ។", "ចំពោះ " + D(ptxt+"=0") + " គេមាន " + D("\\Delta'="+sq(p)+"-%d=%d=(%di)^{2}" % (Pq, -b*b, b)) + " ។ ឫសគឺ " + D("z_1="+zt(z1)) + " , " + D("z_2="+zt(z2)) + " និង " + D("z_3="+L(r0)) + " ។", [("expand((%s)**2-(%d)*(%s)+%d)" % (C(z1), S, C(z1), Pq), "0", "root")]),
             ("តាង " + D("A,\\ B,\\ C") + " ជារូបភាពនៃ " + D("z_1,\\ z_2,\\ z_3") + " ។ កំណត់ប្រភេទនៃត្រីកោណ " + D("ABC") + " ។", tri_dist_sol(ps, rng)[0] + "ដូចនេះ " + D("ABC") + " ជា" + nat_txt(k, ps[i].l) + " ។", chk_d(ps))]
    pr, s_ = assemble(rng, t, parts); ck = sum((p_[2] for p_ in parts), [])
    s_ += fin("ឫសនៃ " + D("P(z)=0") + " គឺ " + D("\\boxed{"+zt(z1)+"}") + " , " + D("\\boxed{"+zt(z2)+"}") + " , " + D("\\boxed{"+L(r0)+"}") + " ។")
    return it("exam_equation_geometry", "bacii", pr, s_, "z_1="+zt(z1)+",\\ z_2="+zt(z2)+",\\ z_3="+L(r0), ck, spec_of(ps), "ត្រីកោណ ABC ដែលកំពូលជារូបភាពនៃឫសទាំងបី ។")

TABLE = [(f_mirror, 35), (f_vector, 40), (f_midcent, 35), (f_param_dist, 35), (f_perimeter, 35), (f_angle, 55), (f_tri_dist, 60), (f_tri_quot, 45), (f_oz, 25), (f_complete_tri, 40),
         (f_quad, 55), (f_fourth, 35), (f_collinear, 30), (f_param_col, 35), (f_perp, 30), (f_circum, 40),
         (f_loc_circle, 50), (f_loc_bis, 40), (f_loc_line, 35), (f_loc_quot, 40), (f_apol, 35), (f_region, 25), (f_ray, 25), (f_paramc, 20),
         (f_trans, 25), (f_rot, 40), (f_homot, 30), (f_sim, 30), (f_classify, 25), (f_compose, 20), (f_image_circle, 25), (f_roots_tri, 20), (f_unity, 17),
         (f_exam_tri, 70), (f_exam_core, 60), (f_exam_quad, 45), (f_exam_locus, 30), (f_exam_map, 30), (f_exam_eq, 30)]
def rows():
    out = []; seen = set(); rng = random.Random(20261105)
    for f, n in TABLE:
        got = tries = 0; n = int(n*.82)
        while got < n and tries < n*6:
            tries += 1
            r = f(rng)
            if r is None or r["prob"] in seen: continue
            # near-duplicate guard: same maths, different wording
            key = (f.__name__, tuple(sorted(re.findall(r"\$[^$]*\$", r["prob"]))))
            if key in seen: continue
            seen.add(r["prob"]); seen.add(key); out.append(r); got += 1
    return out
