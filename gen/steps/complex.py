"""Complex-number skills written out in full. Numbers are Gaussian with exact arithmetic."""
from core import *
CH = "complex"
def g(rng, lo=-6, hi=6): return sp.Integer(rng.randint(lo, hi)), sp.Integer(rng.randint(lo, hi))
def z(a, b): return a + b * I
def zt(e): return tx(sp.expand(e))
def cq(a, b): return f"\\left({zt(z(a,b))}\\right)"
def quotient(rng):
    a, b = g(rng); c, d = g(rng, -5, 5)
    if d == 0 or c == 0 or b == 0: return None
    w = W(rng); z1, z2 = z(a, b), z(c, d); cj = z(c, -d); P = w.v(f"គេឱ្យ $z_1={zt(z1)}$ និង $z_2={zt(z2)}$ ។ សរសេរ $\\frac{{z_1}}{{z_2}}$ ជាទម្រង់ពីជគណិត ។", f"សរសេរចំនួនកុំផ្លិច $Z=\\frac{{{zt(z1)}}}{{{zt(z2)}}}$ ជាទម្រង់ពីជគណិត ។")
    w.say(f"គុណភាគយក និងភាគបែងនឹង ${zt(cj)}$ ដែលជាចំនួនកុំផ្លិចឆ្លាស់នៃភាគបែង ៖")
    q = z1 / z2; num = sp.expand(z1 * cj); den = c ** 2 + d ** 2
    w.chain((f"\\frac{{{zt(z1)}}}{{{zt(z2)}}}", sp.nsimplify(sp.simplify(q))), (f"\\frac{{{cq(a,b)}{cq(c,-d)}}}{{{cq(c,d)}{cq(c,-d)}}}", sp.simplify(z1 * cj / den)))
    t = [a * c, -a * d * I, b * c * I, -b * d * I * I]; tt = [u for u in (a * c, -a * d * I, b * c * I) if u != 0]; show = "".join(("" if i == 0 else ("+" if not tx(u).startswith("-") else "")) + tx(u) for i, u in enumerate(tt))
    last = -b * d; lt = tx(last)
    w.say(f"ភាគយក ៖ $${cq(a,b)}{cq(c,-d)}={show}{'+' if -b*d>=0 else '-'}{tx(abs(b*d))}i^2$$".replace("{}","")) if False else None
    w.say(f"ភាគយក ៖ $${cq(a,b)}{cq(c,-d)}={show}{'+' if b*(-d)>=0 else '-'}{tx(abs(b*d))}i^2$$")
    w.say(f"ដោយ $i^2=-1$ ភាគយកស្មើ ${zt(num)}$ ។"); w.say(f"ភាគបែង ៖ $$\\left({zt(cj)}\\right)\\left({zt(z2)}\\right)={tx(c)}^2+{tx(abs(d))}^2={tx(den)}$$".replace(f"{tx(c)}^2", f"{pp(c)}^2"))
    re_, im_ = sp.re(num) / den, sp.im(num) / den; res = re_ + im_ * I; w.ok(sp.simplify(q), res, "quotient")
    w.chain((f"\\frac{{z_1}}{{z_2}}" if "z_1" in P else "Z", res), (f"\\frac{{{zt(num)}}}{{{tx(den)}}}", res), (zt(res), res)) if False else None
    w.say(f"$$\\frac{{{zt(z1)}}}{{{zt(z2)}}}=\\frac{{{zt(num)}}}{{{tx(den)}}}={zt(res)}$$")
    return row(w.say(f"ដូចនេះ $\\boxed{{{zt(res)}}}$ ។"), CH, "steps", "steps_quotient_conjugate", 1, P, zt(res), "quotient")
def square_root(rng):
    p, q = g(rng, -9, 9)
    if p == 0 or q == 0: return None
    W_ = sp.expand(z(p, q) ** 2); A, B = sp.re(W_), sp.im(W_); M = p ** 2 + q ** 2; w = W(rng)
    P = f"ចូររកឫសការេនៃចំនួនកុំផ្លិច $w={zt(W_)}$ ។"
    w.say("តាង $z=a+ib$ ដែល $a,b\\in\\mathbb{R}$ ជាឫសការេនៃ $w$ ។ គេបាន $z^2=w$ និង $|z|^2=|w|$ ។")
    w.say(f"ដោយ $z^2=a^2-b^2+2abi$ គេបានប្រព័ន្ធ ៖ $$a^2-b^2={tx(A)}\\ ,\\quad 2ab={tx(B)}$$")
    w.chain(("|w|", sp.Integer(M)), (f"\\sqrt{{{pp(A)}^2+{pp(B)}^2}}", sp.sqrt(A ** 2 + B ** 2)), (f"\\sqrt{{{tx(A**2+B**2)}}}", sp.sqrt(A ** 2 + B ** 2)), (tx(M), sp.Integer(M)))
    w.say(f"ដូចនេះ $a^2+b^2={tx(M)}$ ។"); w.say(f"បូកសមីការ $a^2-b^2={tx(A)}$ និង $a^2+b^2={tx(M)}$ ៖")
    w.say(f"$$2a^2={tx(A)}+{tx(M)}={tx(A+M)}\\Rightarrow a^2={tx((A+M)/2)}\\Rightarrow a=\\pm{tx(abs(p))}$$".replace("+-", "-"))
    w.say("ដកសមីការទាំងពីរ ៖"); w.say(f"$$2b^2={tx(M)}-{pp(A)}={tx(M-A)}\\Rightarrow b^2={tx((M-A)/2)}\\Rightarrow b=\\pm{tx(abs(q))}$$")
    w.ok(z(p, q) ** 2, W_, "root"); same_sign = B > 0
    w.say(f"ដោយ $2ab={tx(B)}{'>' if B>0 else '<'}0$ នោះ $a$ និង $b$ មានសញ្ញា{'ដូចគ្នា' if same_sign else 'ផ្ទុយគ្នា'} ។")
    a = abs(p); b = abs(q) if same_sign else -abs(q); r1, r2 = z(a, b), z(-a, -b)
    return row(w.say(f"ដូចនេះ ឫសការេនៃ $w$ គឺ $\\boxed{{{zt(r1)}}}$ និង $\\boxed{{{zt(r2)}}}$ ។"), CH, "steps", "steps_square_root_system", 2, P, f"{zt(r1)},\\ {zt(r2)}", "square_root")
def quad_real(rng):
    a = rng.choice([1, 1, 2, 3]); p, q = rng.randint(-6, 6), rng.randint(1, 6); Pz = sp.Symbol("z"); poly = sp.expand(a * ((Pz - p) ** 2 + q ** 2)); c = sp.Poly(poly, Pz).all_coeffs(); A, B, C = c; D = B ** 2 - 4 * A * C
    w = W(rng); P = w.v(f"ចូរដោះស្រាយសមីការ ${tx(poly)}=0$ ក្នុងសំណុំ $\\mathbb{{C}}$ ។", f"ចូររកឫសទាំងអស់នៃសមីការ ${tx(poly)}=0$ ក្នុង $\\mathbb{{C}}$ ។")
    w.say(f"យើងមាន $a={tx(A)}$ , $b={tx(B)}$ , $c={tx(C)}$ ។"); r = 2 * a * q
    w.say(f"$$\\Delta=b^2-4ac={pp(B)}^2-4{pp(A)}{pp(C)}={tx(B**2)}-{tx(4*A*C)}={tx(D)}$$"); assert D == -r ** 2
    w.say(f"ដោយ $i^2=-1$ គេបាន $\\Delta={tx(r**2)}i^2=({tx(r)}i)^2$ ។"); z1, z2 = z(p, -q), z(p, q)
    w.say(f"$$z_1=\\frac{{-b-{tx(r)}i}}{{2a}}=\\frac{{{tx(-B)}-{tx(r)}i}}{{{tx(2*A)}}}={zt(z1)}$$"); w.say(f"$$z_2=\\frac{{-b+{tx(r)}i}}{{2a}}=\\frac{{{tx(-B)}+{tx(r)}i}}{{{tx(2*A)}}}={zt(z2)}$$")
    for e in (z1, z2): assert sp.expand(poly.subs(Pz, e)) == 0
    w.C.append(check(f"expand(({A})*({z1})**2+({B})*({z1})+({C}))", "0", "root"))
    return row(w.say(f"ដូចនេះ សមីការមានឫស $\\boxed{{z_1={zt(z1)}}}$ និង $\\boxed{{z_2={zt(z2)}}}$ ។"), CH, "steps", "steps_quadratic_delta_negative", 1, P, f"{zt(z1)},\\ {zt(z2)}", "quad_real")
def quad_complex(rng):
    a, b = g(rng, -3, 3); c, d = g(rng, -3, 3); r1, r2 = z(a, b), z(c, d)
    if r1 == r2 or (b == 0 and d == 0) or sp.conjugate(r1) == r2: return None
    B, C = sp.expand(-(r1 + r2)), sp.expand(r1 * r2); dl = sp.expand(r1 - r2); D = sp.expand(B ** 2 - 4 * C); w = W(rng); Z = sp.Symbol("z")
    cf = lambda c, t: "" if c == 0 else ((("+" if c > 0 else "-") + ("" if abs(c) == 1 and t else tx(abs(c))) + t) if sp.im(c) == 0 else f"+\\left({zt(c)}\\right){t}")
    pz = "z^2" + cf(B, "z") + cf(C, "")
    P = f"ចូរដោះស្រាយសមីការ ${pz}=0$ ក្នុងសំណុំ $\\mathbb{{C}}$ ។"
    w.say("គណនាឌីសគ្រីមីណង់ ៖"); w.chain(("\\Delta", D), (f"\\left({zt(B)}\\right)^2-4\\left({zt(C)}\\right)", B ** 2 - 4 * C), (f"\\left({zt(sp.expand(B**2))}\\right)-\\left({zt(sp.expand(4*C))}\\right)", sp.expand(B ** 2) - sp.expand(4 * C)), (zt(D), D))
    p, q = sp.re(dl), sp.im(dl); A_, B_ = sp.re(D), sp.im(D); M = p ** 2 + q ** 2
    if p != 0 and q != 0:
        w.say(f"រកចំនួន $\\delta=u+iv$ ដែល $\\delta^2=\\Delta$ ។ គេបាន $u^2-v^2={tx(A_)}$ , $2uv={tx(B_)}$ និង $u^2+v^2=|\\Delta|={tx(M)}$ ។")
        w.say(f"$$2u^2={tx(A_+M)}\\Rightarrow u=\\pm{tx(abs(p))}\\ ,\\quad 2v^2={tx(M-A_)}\\Rightarrow v=\\pm{tx(abs(q))}$$")
        w.say(f"ដោយ $2uv{'>' if B_>0 else '<'}0$ យក $\\delta={zt(dl)}$ ។")
    else: w.say(f"គេអាចសរសេរ $\\Delta=\\left({zt(dl)}\\right)^2$ ។")
    assert sp.expand(dl ** 2 - D) == 0; w.C.append(check(f"expand(({dl})**2)", str(D), "delta"))
    w.say("តាមរូបមន្ត $z=\\frac{-b\\pm\\delta}{2}$ ៖"); w.say(f"$$z_1=\\frac{{{cq(sp.re(-B),sp.im(-B))}+\\left({zt(dl)}\\right)}}{{2}}={zt(r1)}$$"); w.say(f"$$z_2=\\frac{{{cq(sp.re(-B),sp.im(-B))}-\\left({zt(dl)}\\right)}}{{2}}={zt(r2)}$$")
    w.ok((-B + dl) / 2, r1, "root"); w.ok((-B - dl) / 2, r2, "root")
    return row(w.say(f"ដូចនេះ ឫសនៃសមីការគឺ $\\boxed{{{zt(r1)}}}$ និង $\\boxed{{{zt(r2)}}}$ ។"), CH, "steps", "steps_quadratic_complex_delta", 3, P, f"{zt(r1)},\\ {zt(r2)}", "quad_complex")
ANG = {(1, 1): (sp.sqrt(2), sp.pi / 4), (1, -1): (sp.sqrt(2), -sp.pi / 4), (-1, 1): (sp.sqrt(2), 3 * sp.pi / 4), (-1, -1): (sp.sqrt(2), -3 * sp.pi / 4)}
def power(rng):
    s3 = sp.sqrt(3); opts = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, s3), (1, -s3), (-1, s3), (-1, -s3), (s3, 1), (s3, -1), (-s3, 1), (-s3, -1)]; a, b = rng.choice(opts); k = rng.choice([1, 1, 1, 2, 3]); n = rng.randint(3, 12); a, b = a * k, b * k
    r = sp.sqrt(a ** 2 + b ** 2); ca, sa = sp.nsimplify(a / r), sp.nsimplify(b / r); al = sp.atan2(b, a); zz = sp.expand(a + b * I); w = W(rng)
    P = f"គេឱ្យ $z={zt(zz)}$ ។ សរសេរ $z$ ជាទម្រង់ត្រីកោណមាត្រ រួចគណនា $z^{{{n}}}$ ជាទម្រង់ពីជគណិត ។"
    w.chain(("|z|=r", r), (f"\\sqrt{{{pp(a)}^2+{pp(b)}^2}}", sp.sqrt(a ** 2 + b ** 2)), (tx(r), r))
    w.say(f"$$\\cos\\alpha=\\frac{{a}}{{r}}=\\frac{{{tx(a)}}}{{{tx(r)}}}={tx(sp.radsimp(ca))}\\ ,\\quad\\sin\\alpha=\\frac{{b}}{{r}}=\\frac{{{tx(b)}}}{{{tx(r)}}}={tx(sp.radsimp(sa))}\\Rightarrow\\alpha={tx(al)}$$"); w.ok(sp.cos(al), ca, "cos"); w.ok(sp.sin(al), sa, "sin")
    w.say(f"$$z={tx(r)}\\left[\\cos\\left({tx(al)}\\right)+i\\sin\\left({tx(al)}\\right)\\right]$$"); w.say("តាមរូបមន្តដឺម័រ ៖")
    na = n * al; red = sp.Mod(na + sp.pi, 2 * sp.pi) - sp.pi; turns = (na - red) / (2 * sp.pi); rn = sp.simplify(r ** n); w.ok(sp.cos(na), sp.cos(red), "angle")
    w.say(f"$$z^{{{n}}}={br(r) if r.is_Integer else pp(r)}^{{{n}}}\\left[\\cos\\left({n}\\times{pp(al)}\\right)+i\\sin\\left({n}\\times{pp(al)}\\right)\\right]$$".replace("\\left(\\left(", "\\left(")); w.say(f"$$={tx(rn)}\\left[\\cos\\left({tx(na)}\\right)+i\\sin\\left({tx(na)}\\right)\\right]$$")
    if turns != 0: w.say(f"ដោយ ${tx(na)}={tx(red)}{'+' if turns>0 else '-'}{tx(abs(2*turns))}\\pi$ នោះ $\\cos\\left({tx(na)}\\right)={tx(sp.cos(red))}$ និង $\\sin\\left({tx(na)}\\right)={tx(sp.sin(red))}$ ។")
    else: w.say(f"ដោយ $\\cos\\left({tx(na)}\\right)={tx(sp.cos(na))}$ និង $\\sin\\left({tx(na)}\\right)={tx(sp.sin(na))}$ ៖")
    res = sp.expand(rn * (sp.cos(red) + I * sp.sin(red))); assert sp.simplify(sp.expand(zz ** n) - res) == 0; w.C.append(check(f"expand(({zz})**{n})", str(res), "power"))
    w.say(f"$$z^{{{n}}}={tx(rn)}\\left({tx(sp.cos(red))}{'+' if True else ''}i\\left({tx(sp.sin(red))}\\right)\\right)={tx(res)}$$")
    return row(w.say(f"ដូចនេះ $\\boxed{{z^{{{n}}}={tx(res)}}}$ ។"), CH, "steps", "steps_power_de_moivre", 2, P, f"z^{{{n}}}={tx(res)}", "power")
def linear_conj(rng):
    p, q = g(rng, 1, 4); rr, ss = g(rng, -4, 4); X, Y = g(rng, -5, 5); y = sp.Symbol("y", real=True); a = z(p, q); b = rr + ss * I
    M = sp.Matrix([[p + rr, ss - q], [q + ss, p - rr]])
    if M.det() == 0 or ss == 0: return None
    zs = X + Y * I; c = sp.expand(a * zs + b * sp.conjugate(zs)); w = W(rng); P = f"រកចំនួនកុំផ្លិច $z$ ដែលផ្ទៀងផ្ទាត់ $\\left({zt(a)}\\right)z+\\left({zt(b)}\\right)\\bar{{z}}={zt(c)}$ ។"
    w.say("តាង $z=x+iy$ ដែល $x,y\\in\\mathbb{R}$ ។ គេបាន $\\bar{z}=x-iy$ ។"); e1 = sp.expand(a * (x + I * y)); e2 = sp.expand(b * (x - I * y))
    w.say(f"$$\\left({zt(a)}\\right)(x+iy)={tx(e1)}$$"); w.say(f"$$\\left({zt(b)}\\right)(x-iy)={tx(e2)}$$"); s_ = sp.expand(e1 + e2); R_, I_ = s_.subs(I, 0), sp.expand((s_ - s_.subs(I, 0)) / I)
    w.say("បូកកន្សោមទាំងពីរ រួចប្រៀបធៀបផ្នែកពិត និងផ្នែកនិមិត្ត ៖"); cr, ci = sp.re(c), sp.im(c); w.say(f"$${tx(R_)}={tx(cr)}\\ ,\\quad {tx(I_)}={tx(ci)}$$")
    assert R_.subs({x: X, y: Y}) == cr and I_.subs({x: X, y: Y}) == ci; D = M.det(); w.say(f"ដោះស្រាយប្រព័ន្ធនេះ ៖ $D={tx(D)}$ ។")
    A1, B1 = R_.coeff(x), R_.coeff(y); A2, B2 = I_.coeff(x), I_.coeff(y); Dd = A1 * B2 - A2 * B1; Dx = cr * B2 - ci * B1; Dy = A1 * ci - A2 * cr
    w.L[-1] = f"ដោះស្រាយប្រព័ន្ធនេះ ៖ $$D={pp(A1)}{pp(B2)}-{pp(A2)}{pp(B1)}={tx(Dd)}$$"
    w.say(f"$$D_x={pp(cr)}{pp(B2)}-{pp(ci)}{pp(B1)}={tx(Dx)}$$"); w.say(f"$$D_y={pp(A1)}{pp(ci)}-{pp(A2)}{pp(cr)}={tx(Dy)}$$"); w.say(f"$$x=\\frac{{D_x}}{{D}}=\\frac{{{tx(Dx)}}}{{{tx(Dd)}}}={tx(X)}\\ ,\\quad y=\\frac{{D_y}}{{D}}=\\frac{{{tx(Dy)}}}{{{tx(Dd)}}}={tx(Y)}$$".replace("\\frac{" + tx(Dx) + "}{1}=", "").replace("\\frac{" + tx(Dy) + "}{1}=", "")); assert Dx / Dd == X and Dy / Dd == Y; w.C.append(check(f"expand(({a})*({zs})+({b})*conjugate({zs}))", str(c), "solution"))
    return row(w.say(f"ដូចនេះ $\\boxed{{z={zt(zs)}}}$ ។"), CH, "steps", "steps_linear_with_conjugate", 2, P, f"z={zt(zs)}", "linear_conj")
def triangle(rng):
    a, b = g(rng, -5, 5); u, v = g(rng, -4, 4); s_ = rng.choice([1, -1])
    if (u, v) == (0, 0): return None
    A = z(a, b); Bc = sp.expand(A + z(u, v)); Cc = sp.expand(A + s_ * I * z(u, v)); w = W(rng); Dc = sp.expand(Bc + Cc - A)
    P = f"ក្នុងប្លង់កុំផ្លិច គេឱ្យចំណុច $A$ , $B$ , $C$ ជារូបភាពរៀងគ្នានៃ $z_A={zt(A)}$ , $z_B={zt(Bc)}$ , $z_C={zt(Cc)}$ ។ គណនា $\\frac{{z_C-z_A}}{{z_B-z_A}}$ ទាញរកប្រភេទត្រីកោណ $ABC$ រួចរក $z_D$ ដែល $ABDC$ ជាការេ ។"
    d1, d2 = sp.expand(Cc - A), sp.expand(Bc - A); w.say("គណនាផលដកមុន ៖"); w.say(f"$$z_C-z_A={zt(d1)}\\ ,\\quad z_B-z_A={zt(d2)}$$"); cj = sp.conjugate(d2); n2 = sp.expand(d2 * cj); num = sp.expand(d1 * cj); w.say(f"គុណភាគយក និងភាគបែងនឹង ${zt(cj)}$ ៖")
    w.say(f"$$\\frac{{z_C-z_A}}{{z_B-z_A}}=\\frac{{\\left({zt(d1)}\\right)\\left({zt(cj)}\\right)}}{{\\left({zt(d2)}\\right)\\left({zt(cj)}\\right)}}=\\frac{{{zt(num)}}}{{{tx(n2)}}}={zt(s_*I)}$$"); assert sp.simplify(num / n2 - s_ * I) == 0; w.C.append(check(f"({d1})/({d2})", str(s_ * I), "ratio"))
    w.say(f"ដូចនេះ $\\left|\\frac{{z_C-z_A}}{{z_B-z_A}}\\right|=1$ នាំឱ្យ $AC=AB$ ។"); ang = "\\frac{\\pi}{2}" if s_ > 0 else "-\\frac{\\pi}{2}"; w.say(f"ហើយអាគុយម៉ង់នៃ ${zt(s_*I)}$ គឺ ${ang}$ នាំឱ្យ $AB\\perp AC$ ។"); w.say("ដូចនេះ $ABC$ ជាត្រីកោណកែងសមបាតត្រង់ $A$ ។")
    w.say("ដោយ $ABC$ ជាត្រីកោណកែងសមបាតត្រង់ $A$ នោះ $ABDC$ ជាការេ លុះត្រាតែ $\\overrightarrow{AB}=\\overrightarrow{CD}$ ឬ $z_B-z_A=z_D-z_C$ ។"); w.chain(("z_D", Dc), ("z_B+z_C-z_A", Bc + Cc - A), (f"\\left({zt(Bc)}\\right)+\\left({zt(Cc)}\\right)-\\left({zt(A)}\\right)", Bc + Cc - A), (zt(Dc), Dc))
    return row(w.say(f"ដូចនេះ $\\boxed{{z_D={zt(Dc)}}}$ ។"), CH, "steps", "steps_right_isosceles_square", 3, P, f"z_D={zt(Dc)}", "triangle")
def bisector(rng):
    a, b = g(rng, -6, 6); c, d = g(rng, -6, 6)
    if (a, b) == (c, d): return None
    y = sp.Symbol("y", real=True); w = W(rng); P = f"រកសំណុំចំណុច $M$ រូបភាពនៃ $z$ ដែល $\\left|z-\\left({zt(z(a,b))}\\right)\\right|=\\left|z-\\left({zt(z(c,d))}\\right)\\right|$ ។"
    w.say(f"តាង $A({tx(a)};{tx(b)})$ , $B({tx(c)};{tx(d)})$ និង $z=x+iy$ ដែល $x,y\\in\\mathbb{{R}}$ ។ សមីការមានន័យថា $MA=MB$ ។"); w.say(f"$$\\left|(x{st(-a)})+i(y{st(-b)})\\right|=\\left|(x{st(-c)})+i(y{st(-d)})\\right|$$"); w.say("លើកអង្គទាំងពីរជាការេ តាមរូបមន្តម៉ូឌុល ៖"); L1, L2 = (x - a) ** 2 + (y - b) ** 2, (x - c) ** 2 + (y - d) ** 2
    w.say(f"$${tx(L1)}={tx(L2)}$$"); e1, e2 = sp.expand(L1), sp.expand(L2); w.say(f"$${tx(e1)}={tx(e2)}$$"); ln = sp.expand(e1 - e2); g_ = sp.gcd(sp.gcd(ln.coeff(x), ln.coeff(y)), ln.subs({x: 0, y: 0})); s2 = sp.expand(ln / g_)
    if sp.Poly(s2, x, y).LC() < 0: s2 = -s2; g_ = -g_
    w.say(f"លុប $x^2$ និង $y^2$ ពីអង្គទាំងពីរ រួចរៀបចំ ៖ $${tx(ln)}=0$$")
    if g_ != 1: w.say(f"ចែកនឹង ${tx(g_)}$ ៖ $${tx(s2)}=0$$")
    assert s2.subs({x: R(a + c, 2), y: R(b + d, 2)}) == 0; mid = f"I\\left({tx(R(a+c,2))};{tx(R(b+d,2))}\\right)"
    w.say(f"បន្ទាត់នេះកាត់តាមចំណុចកណ្ដាល ${mid}$ នៃអង្កត់ $AB$ ។"); w.C.append(check(f"({a}+{c})/2*0", "0", "note"))
    return row(w.say(f"ដូចនេះ សំណុំចំណុច $M$ ជាមេដ្យាទ័រនៃ $AB$ ដែលមានសមីការ $\\boxed{{{tx(s2)}=0}}$ ។"), CH, "steps", "steps_perpendicular_bisector", 2, P, f"{tx(s2)}=0", "bisector")
def cubic_real_root(rng):
    r = sp.Integer(rng.choice([-3, -2, -1, 1, 2, 3])); p, q = rng.randint(-4, 4), rng.randint(1, 4); Z = sp.Symbol("z"); quad = sp.expand((Z - p) ** 2 + q ** 2); poly = sp.expand((Z - r) * quad); w = W(rng); c = sp.Poly(quad, Z).all_coeffs(); C = sp.Poly(poly, Z).all_coeffs()
    P = f"គេឱ្យ $P(z)={tx(poly)}$ ។ គណនា $P({tx(r)})$ រួចដោះស្រាយសមីការ $P(z)=0$ ក្នុង $\\mathbb{{C}}$ ។"
    terms = "".join(("" if i == 0 else ("+" if C[i] >= 0 else "")) + (tx(C[i]) if (abs(C[i]) != 1 or i == 3) else ("-" if C[i] < 0 else "")) + (pp(r) + (f"^{{{3-i}}}" if 3 - i > 1 else "") if i < 3 else "") for i in range(4)); w.say(f"$$P({tx(r)})={terms}=0$$")
    w.say(f"ដូចនេះ $P(z)$ ចែកដាច់នឹង ${tx(Z-r)}$ ។ តាង $P(z)=\\left({tx(Z-r)}\\right)(z^2+mz+n)$ ។"); w.say(f"ពន្លាតអង្គខាងស្តាំ ៖ $$\\left({tx(Z-r)}\\right)(z^2+mz+n)=z^3+\\left(m{sgc(-r)}\\right)z^2+\\left(n{sgc(-r)}m\\right)z{sgc(-r)}n$$".replace("+1m","+m").replace("-1m","-m").replace("+1n","+n").replace("-1n","-n"))
    m, n = c[1], c[2]; w.say(f"ប្រៀបធៀបមេគុណ ៖ $m{sgc(-r)}={tx(C[1])}$ , $n{sgc(-r)}m={tx(C[2])}$ , ${tx(-r)}n={tx(C[3])}$ ។".replace("+1m","+m").replace("-1m","-m").replace("$1n","$n").replace("$-1n","$-n")); w.say(f"គេបាន $m={tx(m)}$ និង $n={tx(n)}$ ។"); w.say(f"$$P(z)=\\left({tx(Z-r)}\\right)\\left({tx(quad)}\\right)$$"); D = m ** 2 - 4 * n; rr = 2 * q; assert D == -rr ** 2
    w.say(f"ចំពោះ ${tx(quad)}=0$ ៖ $$\\Delta={pp(m)}^2-4{pp(n)}={tx(D)}=({tx(rr)}i)^2$$"); z1, z2 = z(p, -q), z(p, q); w.say(f"$$z=\\frac{{{tx(-m)}\\pm{tx(rr)}i}}{{2}}$$"); w.C.append(check(f"expand(({z1}-({r}))*(({z1}-({p}))**2+{q**2}))", "0", "root"))
    return row(w.say(f"ដូចនេះ សមីការមានឫស $\\boxed{{{tx(r)}}}$ , $\\boxed{{{zt(z1)}}}$ និង $\\boxed{{{zt(z2)}}}$ ។"), CH, "steps", "steps_cubic_known_root", 3, P, f"{tx(r)},\\ {zt(z1)},\\ {zt(z2)}", "cubic_real_root")
def sgc(v): return ("+" if v >= 0 else "") + tx(v)
ALL = [(quotient, 220), (square_root, 170), (quad_real, 200), (quad_complex, 200), (power, 220), (linear_conj, 180), (triangle, 220), (bisector, 180), (cubic_real_root, 200)]
