"""Hand-written rows for topic limit_transcendental: non-template Khmer, every stated result checked."""
import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from common import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from limit_tex import clean_tex, tikz_squeeze

H = []
TOPIC = "limit_transcendental"
def rid(p): return f"{TOPIC}-" + hashlib.sha1(clean_tex(p).encode()).hexdigest()[:10]
def row(sub, diff, prob, sol, ans, checks, diagrams=None, grade=12):
    p = "\n".join(prob) if isinstance(prob, list) else prob
    s = "\n".join(sol)
    if callable(diagrams):
        diagrams = diagrams(rid(p))
    H.append(make_row(TOPIC, sub, diff, clean_tex(p), clean_tex(s), clean_tex(ans), [check(*c) for c in checks], "limit_transcendental_hand", diagrams=diagrams, chapter="limit", grade=grade))

def unit_circle(row_id, xdeg=38):
    """Unit circle with the sine, the arc and the tangent segment. Labels are math only."""
    t = np.radians(xdeg); th = np.linspace(0, np.pi / 2, 200)
    fig, ax = plt.subplots(figsize=(3.6, 3.6), dpi=110)
    ax.plot(np.cos(th), np.sin(th), color="#1f4e9c", lw=1.6)
    ax.plot([0, 1.25], [0, 0], color="k", lw=.8); ax.plot([0, 0], [0, 1.15], color="k", lw=.8)
    ax.plot([0, 1], [0, np.tan(t)], color="#c0392b", lw=1.1); ax.plot([1, 1], [0, np.tan(t)], color="#c0392b", lw=1.1)
    ax.plot([np.cos(t), np.cos(t)], [0, np.sin(t)], color="#2e8b57", lw=1.1); ax.plot([np.cos(t), 1], [np.sin(t), 0], ls="--", color="gray", lw=.9)
    for (a, b, l, dx, dy) in [(0, 0, "$O$", -.07, -.07), (1, 0, "$A$", .03, -.07), (np.cos(t), np.sin(t), "$M$", -.07, .03), (1, np.tan(t), "$T$", .03, .0), (np.cos(t), 0, "$H$", -.03, -.08)]:
        ax.text(a + dx, b + dy, l, fontsize=10)
    ax.text(.2, .05, "$x$", fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    rel = f"diagrams/{row_id}.png"; fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
    return rel
UC_TIKZ = (r"\begin{tikzpicture}[scale=3]" "\n" r"\draw (1,0) arc (0:90:1);" "\n" r"\draw (0,0)--(1.2,0); \draw (0,0)--(0,1.1);" "\n"
           r"\draw (0,0)--(1,0.78)--(1,0); \draw (0.788,0)--(0.788,0.616); \draw[dashed] (0.788,0.616)--(1,0);" "\n"
           r"\node[below left] at (0,0) {$O$}; \node[below] at (1,0) {$A$}; \node[above left] at (0.788,0.616) {$M$}; \node[right] at (1,0.78) {$T$}; \node[below] at (0.788,0) {$H$};" "\n" r"\end{tikzpicture}")
def uc_dia(alt):
    return lambda i: [{"type": "figure", "latex": UC_TIKZ, "image": unit_circle(i), "alt_km": alt}]

def graph_dia(fn, pg, x0, x1, y0, y1, alt, hl=(), bounds=(), tb=(), poles=()):
    """tb: the same bound lines as bounds and hl, in pgfplots syntax, so TikZ and PNG show one figure."""
    def go(i):
        fig, ax = plt.subplots(figsize=(4.2, 3.4), dpi=110)
        xs = np.linspace(x0, x1, 3000); xs = xs[np.abs(xs) > 1e-5]
        ax.plot(xs, fn(xs), color="#1f4e9c", lw=1.4)
        for b in bounds: ax.plot(xs, b(xs), ls="--", color="#c0392b", lw=1)
        for h in hl: ax.axhline(h, ls=":", color="gray", lw=.9)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
        for sd in ("top", "right"): ax.spines[sd].set_visible(False)
        for sd in ("left", "bottom"): ax.spines[sd].set_position("zero")
        ax.grid(alpha=.2)
        rel = f"diagrams/{i}.png"; fig.savefig(os.path.join(ROOT, rel), bbox_inches="tight"); plt.close(fig)
        return [{"type": "graph", "latex": tikz_squeeze(pg, tb, x0, x1, y0, y1, poles=poles), "image": rel, "alt_km": alt}]
    return go

# ---------- long multi-part items ----------
row("proof_sin_limit_geometry", "bacii",
 [r"ក្នុងតម្រុយអរតូណរម៉ាល់ គេមានរង្វង់ផ្ចិត $O$ កាំ $1$ ។ យក $A(1,0)$ និងចំណុច $M$ លើរង្វង់ ដែលមុំ $\widehat{AOM}=x$ រ៉ាដ្យង់ ជាមួយ $0<x<\frac{\pi}{2}$ ។ បន្ទាត់ប៉ះរង្វង់ត្រង់ $A$ កាត់បន្ទាត់ $OM$ ត្រង់ $T$ ។",
  r"ក. គណនាផ្ទៃក្រឡាត្រីកោណ $OAM$ និងត្រីកោណ $OAT$ ជាអនុគមន៍នៃ $x$ ។",
  r"ខ. ដោយប្រៀបធៀបផ្ទៃក្រឡានៃត្រីកោណទាំងពីរ ជាមួយផ្ទៃក្រឡាចម្រៀករង្វង់ $OAM$ ដែលស្មើ $\frac{x}{2}$ បង្ហាញថា $\sin x<x<\tan x$ ។",
  r"គ. ទាញបញ្ជាក់ថា $\cos x<\frac{\sin x}{x}<1$ ។",
  r"ឃ. ទាញរក $\lim_{x\to 0^{+}}\frac{\sin x}{x}$ ។"],
 [r"ក. ត្រីកោណ $OAM$ មានបាត $OA=1$ និងកម្ពស់ $MH=\sin x$ ។ ត្រីកោណ $OAT$ កែងត្រង់ $A$ ហើយ $AT=\tan x$ ។ គេបាន ៖",
  r"$$S_{OAM}=\frac{1}{2}\sin x,\qquad S_{OAT}=\frac{1}{2}\tan x$$",
  r"ខ. តាមរូប ត្រីកោណ $OAM$ នៅក្នុងចម្រៀក ហើយចម្រៀកនៅក្នុងត្រីកោណ $OAT$ ។ ដូច្នេះ ៖",
  r"$$\frac{1}{2}\sin x<\frac{x}{2}<\frac{1}{2}\tan x$$",
  r"គុណនឹង $2$ គេបាន $\sin x<x<\tan x$ ។",
  r"គ. ពី $\sin x<x$ យើងបាន $\frac{\sin x}{x}<1$ ព្រោះ $x>0$ ។ ពី $x<\tan x=\frac{\sin x}{\cos x}$ ហើយ $\cos x>0$ យើងបាន $\cos x<\frac{\sin x}{x}$ ។",
  r"ឃ. កាលណា $x\to 0^{+}$ គេមាន $\cos x\to 1$ ។ កន្សោម $\frac{\sin x}{x}$ នៅចន្លោះ $\cos x$ និង $1$ ដែលមានលីមីត $1$ ដូចគ្នា ។",
  r"ដូចនេះ $\boxed{\lim_{x\to 0^{+}}\frac{\sin x}{x}=1}$ ។"],
 r"\lim_{x\to 0^{+}}\frac{\sin x}{x}=1",
 [("limit(sin(x)/x,x,0,'+')", "1", "final"), ("limit(cos(x),x,0)", "1", "lower bound"), ("subs(tan(x)-x,x,Rational(1,2))>0", "True", "instance of x<tan x"), ("subs(x-sin(x),x,Rational(1,2))>0", "True", "instance of sin x<x")],
 diagrams=uc_dia("រង្វង់ឯកតា មានចំណុច $A$ , $M$ , $T$ និង $H$ ដែលបង្ហាញត្រីកោណ $OAM$ ចម្រៀក និងត្រីកោណ $OAT$ ។"))

row("proof_standard_limits", "bacii",
 [r"គេស្គាល់ $\lim_{x\to 0}\frac{\sin x}{x}=1$ ។", r"១. ទាញរក $\lim_{x\to 0}\frac{\tan x}{x}$ ។", r"២. បង្ហាញថា $\frac{1-\cos x}{x^{2}}=\frac{\sin^{2}x}{x^{2}(1+\cos x)}$ ចំពោះ $x$ ជិត $0$ រួចគណនា $\lim_{x\to 0}\frac{1-\cos x}{x^{2}}$ ។", r"៣. ទាញរក $\lim_{x\to 0}\frac{1-\cos x}{x}$ ។", r"៤. ទាញរក $\lim_{x\to 0}\frac{x-x\cos 2x}{\sin^{3}x}$ ។"],
 [r"១. ដោយ $\tan x=\frac{\sin x}{\cos x}$ យើងសរសេរ $\frac{\tan x}{x}=\frac{\sin x}{x}\cdot\frac{1}{\cos x}$ ។ កត្តាទាំងពីរខិតជិត $1$ ដូច្នេះលីមីតស្មើ $1$ ។",
  r"២. គុណភាគយក និងភាគបែងនឹង $1+\cos x$ ដែលខុសពីសូន្យពេល $x$ ជិត $0$ ៖",
  r"$$\frac{1-\cos x}{x^{2}}=\frac{(1-\cos x)(1+\cos x)}{x^{2}(1+\cos x)}=\frac{1-\cos^{2}x}{x^{2}(1+\cos x)}=\frac{\sin^{2}x}{x^{2}(1+\cos x)}$$",
  r"យកលីមីត ៖ $\left(\frac{\sin x}{x}\right)^{2}\to 1$ និង $\frac{1}{1+\cos x}\to\frac{1}{2}$ ។ គេបាន $\lim_{x\to 0}\frac{1-\cos x}{x^{2}}=\frac{1}{2}$ ។",
  r"៣. យើងមាន $\frac{1-\cos x}{x}=x\cdot\frac{1-\cos x}{x^{2}}\to 0\cdot\frac{1}{2}=0$ ។",
  r"៤. ភាគយកស្មើ $x(1-\cos 2x)=2x\sin^{2}x$ ។ ដូច្នេះ $\frac{x-x\cos 2x}{\sin^{3}x}=\frac{2x\sin^{2}x}{\sin^{3}x}=\frac{2x}{\sin x}\to 2$ ។",
  r"ដូចនេះ លីមីតទាំងបួនគឺ $\boxed{1,\ \frac{1}{2},\ 0,\ 2}$ រៀងគ្នា ។"],
 r"1,\ \frac{1}{2},\ 0,\ 2",
 [("limit(tan(x)/x,x,0)", "1"), ("limit((1-cos(x))/x**2,x,0)", "Rational(1,2)"), ("limit((1-cos(x))/x,x,0)", "0"), ("limit((x-x*cos(2*x))/sin(x)**3,x,0)", "2")])

row("number_e_squeeze", "bacii",
 [r"គេទទួលស្គាល់ថា ចំពោះគ្រប់ $t>0$ គេមាន $\frac{t}{1+t}\le\ln(1+t)\le t$ ។", r"ក. ដោយជំនួស $t=\frac{1}{x}$ ដែល $x>0$ បង្ហាញថា $\frac{x}{x+1}\le x\ln\left(1+\frac{1}{x}\right)\le 1$ ។", r"ខ. ទាញរក $\lim_{x\to+\infty}x\ln\left(1+\frac{1}{x}\right)$ ។", r"គ. ទាញរក $\lim_{x\to+\infty}\left(1+\frac{1}{x}\right)^{x}$ ។", r"ឃ. គណនា $\lim_{x\to+\infty}\left(1+\frac{1}{x}\right)^{3x+2}$ ។"],
 [r"ក. ជំនួស $t=\frac{1}{x}$ ក្នុងវិសមភាព ៖ $\frac{t}{1+t}=\frac{\frac{1}{x}}{1+\frac{1}{x}}=\frac{1}{x+1}$ ។ គេបាន ៖",
  r"$$\frac{1}{x+1}\le\ln\left(1+\frac{1}{x}\right)\le\frac{1}{x}$$", r"គុណនឹង $x>0$ យើងបានវិសមភាពដែលត្រូវបង្ហាញ ។",
  r"ខ. ដោយ $\frac{x}{x+1}\to 1$ កាលណា $x\to+\infty$ កន្សោមកណ្តាលនៅចន្លោះចំនួនពីរដែលខិតជិត $1$ ។ ដូច្នេះ $\lim_{x\to+\infty}x\ln\left(1+\frac{1}{x}\right)=1$ ។",
  r"គ. សរសេរ $\left(1+\frac{1}{x}\right)^{x}=e^{x\ln\left(1+\frac{1}{x}\right)}$ ។ និទស្សន្តខិតជិត $1$ ហើយអនុគមន៍អ៊ិចស្ប៉ូណង់ស្យែលជាប់ ដូច្នេះលីមីតស្មើ $e^{1}=e$ ។",
  r"ឃ. បំបែកនិទស្សន្ត ៖ $$\left(1+\frac{1}{x}\right)^{3x+2}=\left[\left(1+\frac{1}{x}\right)^{x}\right]^{3}\left(1+\frac{1}{x}\right)^{2}$$",
  r"កត្តាទីមួយខិតជិត $e^{3}$ ហើយកត្តាទីពីរខិតជិត $1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to+\infty}\left(1+\frac{1}{x}\right)^{3x+2}=e^{3}}$ ។"],
 r"1,\ e,\ e^{3}",
 [("limit(x*log(1+1/x),x,oo)", "1"), ("limit((1+1/x)**x,x,oo)", "E"), ("limit((1+1/x)**(3*x+2),x,oo)", "exp(3)"), ("limit(x/(x+1),x,oo)", "1", "lower bound")])

row("function_study_limits", "bacii",
 [r"គេឱ្យអនុគមន៍ $f(x)=\frac{e^{x}-1}{x}$ ចំពោះ $x\neq 0$ ។", r"១. គណនា $\lim_{x\to 0}f(x)$ ។ តើគួរកំណត់ $f(0)$ ស្មើប៉ុន្មាន ដើម្បីឱ្យ $f$ ជាប់ត្រង់ $0$ ?", r"២. គណនា $\lim_{x\to-\infty}f(x)$ រួចទាញរកអាស៊ីមតូតដេក ។", r"៣. គណនា $\lim_{x\to+\infty}f(x)$ និង $\lim_{x\to+\infty}\frac{f(x)}{x}$ ។"],
 [r"១. នេះជារូបមន្តគោល ៖ $\lim_{x\to 0}\frac{e^{x}-1}{x}=1$ ។ ដើម្បីឱ្យ $f$ ជាប់ត្រង់ $0$ យើងត្រូវដាក់ $f(0)=1$ ។",
  r"២. កាលណា $x\to-\infty$ គេមាន $e^{x}\to 0$ ដូច្នេះភាគយកខិតជិត $-1$ ហើយភាគបែងខិតជិត $-\infty$ ។ គេបាន $\lim_{x\to-\infty}f(x)=0$ ។ បន្ទាត់ $y=0$ ជាអាស៊ីមតូតដេកត្រង់ $-\infty$ ។",
  r"៣. យើងបំបែក $f(x)=\frac{e^{x}}{x}-\frac{1}{x}$ ។ ដោយ $\frac{e^{x}}{x}\to+\infty$ គេបាន $\lim_{x\to+\infty}f(x)=+\infty$ ។",
  r"ហើយ $\frac{f(x)}{x}=\frac{e^{x}}{x^{2}}-\frac{1}{x^{2}}\to+\infty$ ព្រោះអ៊ិចស្ប៉ូណង់ស្យែលកើនលឿនជាង $x^{2}$ ។",
  r"ដូចនេះ $\boxed{f(0)=1}$ , អាស៊ីមតូតដេកគឺ $\boxed{y=0}$ ហើយលីមីតទាំងពីរត្រង់ $+\infty$ ស្មើ $\boxed{+\infty}$ ។"],
 r"1,\ 0,\ +\infty,\ +\infty",
 [("limit((exp(x)-1)/x,x,0)", "1"), ("limit((exp(x)-1)/x,x,-oo)", "0"), ("limit((exp(x)-1)/x,x,oo)", "oo"), ("limit((exp(x)-1)/x**2,x,oo)", "oo")],
 diagrams=graph_dia(lambda t: (np.exp(t) - 1) / t, "(exp(x)-1)/x", -6, 3, -0.5, 6, "ក្រាបនៃ $f$ កើនពីអ័ក្សអាប់ស៊ីសត្រង់ $-\\infty$ ហើយកាត់អ័ក្សអរដោនេជិត $y=1$ ។", poles=[0]))

row("growth_comparison", "bacii",
 [r"គេឱ្យអនុគមន៍ $g(x)=x\ln x$ កំណត់លើ $(0,+\infty)$ ។", r"ក. ដោយតាង $t=\frac{1}{x}$ បង្ហាញថា $g(x)=-\frac{\ln t}{t}$ រួចគណនា $\lim_{x\to 0^{+}}g(x)$ ។", r"ខ. ទាញរក $\lim_{x\to 0^{+}}x^{x}$ ។ (កំណត់ដោយ $x^{x}=e^{x\ln x}$)", r"គ. គណនា $\lim_{x\to 0^{+}}\left(x^{2}\ln x+\sin x\right)$ ។"],
 [r"ក. ដោយ $x=\frac{1}{t}$ យើងមាន $\ln x=-\ln t$ ។ គេបាន $g(x)=\frac{1}{t}\cdot(-\ln t)=-\frac{\ln t}{t}$ ។", r"បើ $x\to 0^{+}$ នោះ $t\to+\infty$ ។ ដោយ $\lim_{t\to+\infty}\frac{\ln t}{t}=0$ យើងបាន $\lim_{x\to 0^{+}}g(x)=0$ ។",
  r"ខ. និទស្សន្ត $x\ln x$ ខិតជិត $0$ ហើយ $e^{u}$ ជាប់ត្រង់ $u=0$ ដូច្នេះ $\lim_{x\to 0^{+}}x^{x}=e^{0}=1$ ។",
  r"គ. យើងសរសេរ $x^{2}\ln x=x\cdot x\ln x\to 0\cdot 0=0$ ហើយ $\sin x\to 0$ ។", r"ដូចនេះ លីមីតទាំងបីគឺ $\boxed{0,\ 1,\ 0}$ រៀងគ្នា ។"],
 r"0,\ 1,\ 0", [("limit(x*log(x),x,0,'+')", "0"), ("limit(x**x,x,0,'+')", "1"), ("limit(x**2*log(x)+sin(x),x,0,'+')", "0")])

row("squeeze_at_zero", "bacii",
 [r"គេឱ្យអនុគមន៍ $f(x)=x\sin\frac{1}{x}$ ចំពោះ $x\neq 0$ ។", r"១. បង្ហាញថា $|f(x)|\le|x|$ ។ ទាញរក $\lim_{x\to 0}f(x)$ ។", r"២. ដោយតាង $t=\frac{1}{x}$ គណនា $\lim_{x\to+\infty}f(x)$ ។", r"៣. តើក្រាបនៃ $f$ មានអាស៊ីមតូតដេកឬទេ ?"],
 [r"១. ដោយ $\left|\sin\frac{1}{x}\right|\le 1$ យើងបាន $|f(x)|=|x|\left|\sin\frac{1}{x}\right|\le|x|$ ។ មានន័យថា $-|x|\le f(x)\le|x|$ ។", r"អង្គសងខាងខិតជិត $0$ កាលណា $x\to 0$ ដូច្នេះ $\lim_{x\to 0}f(x)=0$ ។",
  r"២. បើ $x\to+\infty$ នោះ $t\to 0^{+}$ ហើយ $f(x)=\frac{\sin t}{t}\to 1$ ។", r"៣. យើងទើបបាន $\lim_{x\to+\infty}f(x)=1$ ។ ដោយ $f$ ជាអនុគមន៍គូ គេក៏បាន $\lim_{x\to-\infty}f(x)=1$ ដែរ ។", r"ដូចនេះ បន្ទាត់ $\boxed{y=1}$ ជាអាស៊ីមតូតដេកនៃក្រាបនៃ $f$ ។"],
 r"0,\ 1,\ y=1", [("limit(x*sin(1/x),x,0)", "0"), ("limit(x*sin(1/x),x,oo)", "1"), ("limit(x*sin(1/x),x,-oo)", "1"), ("limit(Abs(x),x,0)", "0", "bound")],
 diagrams=graph_dia(lambda t: t * np.sin(1 / t), "x*sin(1/x)", -1, 1, -1, 1, "ក្រាបនៃ $x\\sin\\frac{1}{x}$ លំយោលនៅចន្លោះបន្ទាត់ $y=x$ និង $y=-x$ ។", bounds=(lambda t: t, lambda t: -t), tb=("x", "-x"), poles=[0]))

row("exam_guided_multi_part", "bacii",
 [r"គេឱ្យអនុគមន៍ $h(x)=\frac{\sqrt{1+\sin x}-\sqrt{1-\sin x}}{x}$ ។", r"ក. បង្ហាញថា $h(x)=\frac{2\sin x}{x\left(\sqrt{1+\sin x}+\sqrt{1-\sin x}\right)}$ ។", r"ខ. គណនា $\lim_{x\to 0}h(x)$ ។", r"គ. គណនា $\lim_{x\to+\infty}h(x)$ ។"],
 [r"ក. គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់ $\sqrt{1+\sin x}+\sqrt{1-\sin x}$ ៖", r"$$h(x)=\frac{(1+\sin x)-(1-\sin x)}{x\left(\sqrt{1+\sin x}+\sqrt{1-\sin x}\right)}=\frac{2\sin x}{x\left(\sqrt{1+\sin x}+\sqrt{1-\sin x}\right)}$$",
  r"ខ. កាលណា $x\to 0$ គេមាន $\frac{\sin x}{x}\to 1$ ហើយវង់ក្រចកខិតជិត $2$ ។ ដូច្នេះ $\lim_{x\to 0}h(x)=\frac{2}{2}=1$ ។",
  r"គ. ភាគយកនៃរូបដើមមានតម្លៃដាច់ខាតមិនលើស $2\sqrt{2}$ ព្រោះឫសនីមួយៗមិនលើស $\sqrt{2}$ ។ ដូច្នេះ $|h(x)|\le\frac{2\sqrt{2}}{x}$ ចំពោះ $x>0$ ។", r"អង្គស្តាំខិតជិត $0$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}h(x)=1}$ និង $\boxed{\lim_{x\to+\infty}h(x)=0}$ ។"],
 r"1,\ 0", [("limit((sqrt(1+sin(x))-sqrt(1-sin(x)))/x,x,0)", "1"), ("limit(2*sqrt(2)/x,x,oo)", "0", "bound")])

row("exam_multi_part_hand", "bacii",
 [r"គណនាលីមីត ៖", r"ក. $\lim_{x\to 1}\frac{\sqrt{x+3}-2}{x-1}$", r"ខ. $\lim_{x\to 0}\frac{1-\cos 2x}{x\sin x}$", r"គ. $\lim_{x\to\frac{\pi}{4}}\frac{\sin x-\cos x}{x-\frac{\pi}{4}}$"],
 [r"ក. មានរាងមិនកំណត់ $\frac{0}{0}$ ។ គុណនឹងកន្សោមឆ្លាស់ ៖", r"$$\lim_{x\to 1}\frac{\sqrt{x+3}-2}{x-1}=\lim_{x\to 1}\frac{x+3-4}{(x-1)\left(\sqrt{x+3}+2\right)}=\lim_{x\to 1}\frac{1}{\sqrt{x+3}+2}=\frac{1}{4}$$",
  r"ដូចនេះ $\boxed{\lim_{x\to 1}\frac{\sqrt{x+3}-2}{x-1}=\frac{1}{4}}$ ។", r"ខ. ដោយ $1-\cos 2x=2\sin^{2}x$ យើងបាន ៖", r"$$\frac{1-\cos 2x}{x\sin x}=\frac{2\sin^{2}x}{x\sin x}=\frac{2\sin x}{x}$$", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{1-\cos 2x}{x\sin x}=2}$ ។",
  r"គ. តាង $t=x-\frac{\pi}{4}$ ។ បើ $x\to\frac{\pi}{4}$ នោះ $t\to 0$ ។ យើងសរសេរ $\sin x-\cos x=\sqrt{2}\sin\left(x-\frac{\pi}{4}\right)=\sqrt{2}\sin t$ ។", r"$$\lim_{t\to 0}\frac{\sqrt{2}\sin t}{t}=\sqrt{2}$$", r"ដូចនេះ $\boxed{\lim_{x\to\frac{\pi}{4}}\frac{\sin x-\cos x}{x-\frac{\pi}{4}}=\sqrt{2}}$ ។"],
 r"\frac{1}{4},\ 2,\ \sqrt{2}", [("limit((sqrt(x+3)-2)/(x-1),x,1)", "Rational(1,4)"), ("limit((1-cos(2*x))/(x*sin(x)),x,0)", "2"), ("limit((sin(x)-cos(x))/(x-pi/4),x,pi/4)", "sqrt(2)")])

row("exam_multi_part_hand", "bacii",
 [r"គណនាលីមីតខាងក្រោម ៖", r"១. $\lim_{x\to 2}\frac{x^{2}-5x+6}{x^{2}-4}$", r"២. $\lim_{x\to 0}\frac{\sin 3x+\sin 5x}{\tan 4x}$", r"៣. $\lim_{x\to 0}\frac{\cos 3x-\cos 7x}{x^{2}}$", r"៤. $\lim_{x\to+\infty}\left(\sqrt{x^{2}+2x}-x\right)$"],
 [r"១. ដាក់ជាកត្តា ៖ $\frac{(x-2)(x-3)}{(x-2)(x+2)}=\frac{x-3}{x+2}$ ។ ជំនួស $x=2$ យើងបាន $-\frac{1}{4}$ ។",
  r"២. ចែកភាគយក និងភាគបែងនឹង $x$ ៖ ភាគយកខិតជិត $3+5=8$ ហើយភាគបែងខិតជិត $4$ ។ លីមីតស្មើ $2$ ។",
  r"៣. ប្រើ $\cos p-\cos q=-2\sin\frac{p+q}{2}\sin\frac{p-q}{2}$ ៖ $$\cos 3x-\cos 7x=-2\sin 5x\sin(-2x)=2\sin 5x\sin 2x$$", r"$$\frac{2\sin 5x\sin 2x}{x^{2}}=2\cdot\frac{\sin 5x}{x}\cdot\frac{\sin 2x}{x}\to 2\cdot 5\cdot 2=20$$",
  r"៤. គុណនឹងកន្សោមឆ្លាស់ ៖ $$\sqrt{x^{2}+2x}-x=\frac{2x}{\sqrt{x^{2}+2x}+x}=\frac{2}{\sqrt{1+\frac{2}{x}}+1}\to 1$$", r"ដូចនេះ លីមីតទាំងបួនគឺ $\boxed{-\frac{1}{4},\ 2,\ 20,\ 1}$ រៀងគ្នា ។"],
 r"-\frac{1}{4},\ 2,\ 20,\ 1", [("limit((x**2-5*x+6)/(x**2-4),x,2)", "-Rational(1,4)"), ("limit((sin(3*x)+sin(5*x))/tan(4*x),x,0)", "2"), ("limit((cos(3*x)-cos(7*x))/x**2,x,0)", "20"), ("limit(sqrt(x**2+2*x)-x,x,oo)", "1")])

row("exam_multi_part_hand", "bacii",
 [r"គណនាលីមីត ៖", r"ក- $\lim_{x\to 0}\frac{e^{2x}-e^{-x}}{x}$", r"ខ- $\lim_{x\to 0}\frac{\ln(1+x)-x\cos x}{\sin x}$", r"គ- $\lim_{x\to+\infty}x\left(e^{\frac{2}{x}}-1\right)$"],
 [r"ក- បូក និងដក $1$ ៖ $$\frac{e^{2x}-e^{-x}}{x}=2\cdot\frac{e^{2x}-1}{2x}+\frac{e^{-x}-1}{-x}$$", r"តួទាំងពីរខិតជិត $2$ និង $1$ ។ លីមីតស្មើ $3$ ។",
  r"ខ- ចែកភាគយក និងភាគបែងនឹង $x$ ៖ $$\frac{\frac{\ln(1+x)}{x}-\cos x}{\frac{\sin x}{x}}\to\frac{1-1}{1}=0$$",
  r"គ- តាង $t=\frac{2}{x}$ ។ បើ $x\to+\infty$ នោះ $t\to 0^{+}$ ហើយ $x=\frac{2}{t}$ ។ $$x\left(e^{\frac{2}{x}}-1\right)=2\cdot\frac{e^{t}-1}{t}\to 2$$", r"ដូចនេះ លីមីតទាំងបីគឺ $\boxed{3,\ 0,\ 2}$ រៀងគ្នា ។"],
 r"3,\ 0,\ 2", [("limit((exp(2*x)-exp(-x))/x,x,0)", "3"), ("limit((log(1+x)-x*cos(x))/sin(x),x,0)", "0"), ("limit(x*(exp(2/x)-1),x,oo)", "2")])

row("exam_multi_part_hand", "bacii",
 [r"គណនាលីមីតនៃអនុគមន៍ខាងក្រោម ៖", r"ក. $\lim_{x\to 3}\frac{x^{2}-9}{\sqrt{x+1}-2}$", r"ខ. $\lim_{x\to+\infty}\frac{2e^{x}+3}{e^{x}+x}$", r"គ. $\lim_{x\to 0^{+}}\left(\ln x+\frac{1}{x}\right)$"],
 [r"ក. គុណនឹង $\sqrt{x+1}+2$ ៖ $$\frac{(x-3)(x+3)\left(\sqrt{x+1}+2\right)}{x-3}=(x+3)\left(\sqrt{x+1}+2\right)\to 6\cdot 4=24$$",
  r"ខ. ចែកនឹង $e^{x}$ ៖ $$\frac{2+3e^{-x}}{1+\frac{x}{e^{x}}}\to\frac{2}{1}=2$$ ព្រោះ $\frac{x}{e^{x}}\to 0$ ។",
  r"គ. ធ្វើជាប្រភាគតែមួយ ៖ $\ln x+\frac{1}{x}=\frac{x\ln x+1}{x}$ ។ ដោយ $x\ln x\to 0$ ភាគយកខិតជិត $1$ ហើយភាគបែងខិតជិត $0^{+}$ ។ លីមីតស្មើ $+\infty$ ។", r"ដូចនេះ $\boxed{24}$ , $\boxed{2}$ និង $\boxed{+\infty}$ ជាលីមីតរៀងគ្នា ។"],
 r"24,\ 2,\ +\infty", [("limit((x**2-9)/(sqrt(x+1)-2),x,3)", "24"), ("limit((2*exp(x)+3)/(exp(x)+x),x,oo)", "2"), ("limit(log(x)+1/x,x,0,'+')", "oo")])

row("exam_multi_part_hand", "bacii",
 [r"I. គណនាលីមីត ៖", r"ក. $\lim_{x\to\pi}\frac{\sin x}{x-\pi}$", r"ខ. $\lim_{x\to\frac{\pi}{3}}\frac{1-2\cos x}{\sin\left(x-\frac{\pi}{3}\right)}$", r"គ. $\lim_{x\to 1}\frac{\sin(\pi x)}{\ln x}$"],
 [r"ក. តាង $t=x-\pi$ ។ យើងមាន $\sin x=\sin(t+\pi)=-\sin t$ ។ $$\lim_{t\to 0}\frac{-\sin t}{t}=-1$$",
  r"ខ. តាង $t=x-\frac{\pi}{3}$ ។ $$1-2\cos\left(t+\frac{\pi}{3}\right)=1-\cos t+\sqrt{3}\sin t$$", r"ដូច្នេះ $$\frac{1-\cos t+\sqrt{3}\sin t}{\sin t}=\frac{1-\cos t}{\sin t}+\sqrt{3}$$", r"ដោយ $\frac{1-\cos t}{\sin t}=\frac{1-\cos t}{t}\cdot\frac{t}{\sin t}\to 0$ លីមីតស្មើ $\sqrt{3}$ ។",
  r"គ. តាង $t=x-1$ ។ គេបាន $\sin\pi x=\sin(\pi t+\pi)=-\sin\pi t$ និង $\ln x=\ln(1+t)$ ។ $$\frac{-\sin\pi t}{\ln(1+t)}=-\pi\cdot\frac{\sin\pi t}{\pi t}\cdot\frac{t}{\ln(1+t)}\to-\pi$$", r"ដូចនេះ លីមីតទាំងបីគឺ $\boxed{-1,\ \sqrt{3},\ -\pi}$ រៀងគ្នា ។"],
 r"-1,\ \sqrt{3},\ -\pi", [("limit(sin(x)/(x-pi),x,pi)", "-1"), ("limit((1-2*cos(x))/sin(x-pi/3),x,pi/3)", "sqrt(3)"), ("limit(sin(pi*x)/log(x),x,1)", "-pi")])

row("exam_multi_part_hand", "bacii",
 [r"គេឱ្យ $u(x)=\frac{\sin 2x}{x}$ , $v(x)=\frac{e^{3x}-1}{x}$ និង $w(x)=\frac{\ln(1+4x)}{x}$ ។", r"១. គណនា $\lim_{x\to 0}u(x)$ , $\lim_{x\to 0}v(x)$ និង $\lim_{x\to 0}w(x)$ ។", r"២. ទាញរក $\lim_{x\to 0}\frac{\sin 2x+e^{3x}-1}{\ln(1+4x)}$ ។", r"៣. ទាញរក $\lim_{x\to 0}\frac{\sin 2x\left(e^{3x}-1\right)}{x\ln(1+4x)}$ ។"],
 [r"១. តាមរូបមន្តគោលទាំងបី ៖ $\lim_{x\to 0}u(x)=2$ , $\lim_{x\to 0}v(x)=3$ និង $\lim_{x\to 0}w(x)=4$ ។", r"២. ចែកភាគយក និងភាគបែងនឹង $x$ កន្សោមក្លាយជា $\frac{u(x)+v(x)}{w(x)}$ ។ លីមីតស្មើ $\frac{2+3}{4}=\frac{5}{4}$ ។",
  r"៣. កន្សោមនេះស្មើ $\frac{u(x)v(x)}{w(x)}$ ព្រោះ $\frac{\sin 2x}{x}\cdot\frac{e^{3x}-1}{x}\cdot\frac{x}{\ln(1+4x)}$ មានភាគបែងរួម $x\ln(1+4x)$ ។ លីមីតស្មើ $\frac{2\cdot 3}{4}=\frac{3}{2}$ ។", r"ដូចនេះ $\boxed{\frac{5}{4}}$ និង $\boxed{\frac{3}{2}}$ ជាលីមីតនៃសំណួរ ២ និង ៣ ។"],
 r"2,\ 3,\ 4,\ \frac{5}{4},\ \frac{3}{2}", [("limit(sin(2*x)/x,x,0)", "2"), ("limit((exp(3*x)-1)/x,x,0)", "3"), ("limit(log(1+4*x)/x,x,0)", "4"), ("limit((sin(2*x)+exp(3*x)-1)/log(1+4*x),x,0)", "Rational(5,4)"), ("limit(sin(2*x)*(exp(3*x)-1)/(x*log(1+4*x)),x,0)", "Rational(3,2)")])

row("find_parameter", "bacii",
 [r"គេឱ្យអនុគមន៍ $f(x)=\frac{\sin ax}{x}$ ចំពោះ $x<0$ , $f(x)=x^{2}+b$ ចំពោះ $x\ge 0$ ដែល $a$ និង $b$ ជាចំនួនពិត ។", r"ក. គណនាលីមីតឆ្វេង និងលីមីតស្តាំនៃ $f$ ត្រង់ $0$ ជាអនុគមន៍នៃ $a$ និង $b$ ។", r"ខ. កំណត់ទំនាក់ទំនងរវាង $a$ និង $b$ ដើម្បីឱ្យ $f$ ជាប់ត្រង់ $0$ ។", r"គ. បើបន្ថែមលក្ខខណ្ឌ $f(1)=4$ រក $a$ និង $b$ ។"],
 [r"ក. $$\lim_{x\to 0^{-}}f(x)=\lim_{x\to 0^{-}}\frac{\sin ax}{x}=a,\qquad\lim_{x\to 0^{+}}f(x)=b$$", r"ខ. យើងមាន $f(0)=b$ ។ $f$ ជាប់ត្រង់ $0$ លុះត្រាតែលីមីតទាំងពីរស្មើ $f(0)$ គឺ $a=b$ ។", r"គ. $f(1)=1+b=4$ នាំឱ្យ $b=3$ ។ តាមទំនាក់ទំនងខាងលើ $a=3$ ។", r"ដូចនេះ $\boxed{a=3,\ b=3}$ ។"],
 r"a=b,\ a=3,\ b=3", [("limit(sin(3*x)/x,x,0,'-')", "3"), ("limit(x**2+3,x,0,'+')", "3"), ("subs(x**2+3,x,1)", "4")])

row("find_parameter", "bacii",
 [r"គេមាន $L=\lim_{x\to 0}\frac{\sqrt{1+ax}-\cos x}{x}$ និង $M=\lim_{x\to 0}\frac{e^{bx}-1}{\sin x}$ ដែល $a$ , $b$ ជាចំនួនពិត ។", r"១. គណនា $L$ ជាអនុគមន៍នៃ $a$ ។", r"២. គណនា $M$ ជាអនុគមន៍នៃ $b$ ។", r"៣. រក $a$ និង $b$ បើ $L=2$ និង $L+M=7$ ។"],
 [r"១. បូក និងដក $1$ នៅភាគយក ៖ $$\frac{\sqrt{1+ax}-\cos x}{x}=\frac{\sqrt{1+ax}-1}{x}+\frac{1-\cos x}{x}$$", r"តួទីមួយ ៖ គុណនឹងកន្សោមឆ្លាស់ បាន $\frac{a}{\sqrt{1+ax}+1}\to\frac{a}{2}$ ។ តួទីពីរខិតជិត $0$ ។ ដូច្នេះ $L=\frac{a}{2}$ ។",
  r"២. $$\frac{e^{bx}-1}{\sin x}=b\cdot\frac{e^{bx}-1}{bx}\cdot\frac{x}{\sin x}\to b$$ ចំពោះ $b\neq 0$ ហើយពេល $b=0$ រូបមន្តនៅតែត្រូវ ។ ដូច្នេះ $M=b$ ។", r"៣. $\frac{a}{2}=2$ នាំឱ្យ $a=4$ ។ $L+M=7$ នាំឱ្យ $b=5$ ។", r"ដូចនេះ $\boxed{a=4,\ b=5}$ ។"],
 r"a=4,\ b=5", [("limit((sqrt(1+4*x)-cos(x))/x,x,0)", "2"), ("limit((exp(5*x)-1)/sin(x),x,0)", "5")])

row("exam_guided_multi_part", "bacii",
 [r"គេឱ្យ $A=\lim_{x\to 0}\frac{1-\cos x\cos 2x\cos 3x}{x^{2}}$ ។", r"ក. បង្ហាញថា $1-\cos x\cos 2x\cos 3x=(1-\cos x)+\cos x(1-\cos 2x)+\cos x\cos 2x(1-\cos 3x)$ ។", r"ខ. ទាញរកតម្លៃ $A$ ។", r"គ. តើលទ្ធផលនេះស្មើ $\frac{1^{2}+2^{2}+3^{2}}{2}$ ឬទេ ?"],
 [r"ក. ពន្លាតអង្គស្តាំ ៖ $$1-\cos x+\cos x-\cos x\cos 2x+\cos x\cos 2x-\cos x\cos 2x\cos 3x$$", r"តួកណ្តាលលុបគ្នាជាគូ នៅសល់ $1-\cos x\cos 2x\cos 3x$ ។",
  r"ខ. ចែកនឹង $x^{2}$ ។ ដោយ $\frac{1-\cos kx}{x^{2}}\to\frac{k^{2}}{2}$ ហើយ $\cos x\to 1$ , $\cos 2x\to 1$ យើងបាន ៖", r"$$A=\frac{1}{2}+1\cdot\frac{4}{2}+1\cdot 1\cdot\frac{9}{2}=7$$", r"គ. យើងមាន $\frac{1+4+9}{2}=7$ ស្មើនឹង $A$ ។", r"ដូចនេះ $\boxed{A=7}$ ហើយចម្លើយសំណួរ គ គឺស្មើ ។"],
 r"A=7", [("limit((1-cos(x)*cos(2*x)*cos(3*x))/x**2,x,0)", "7"), ("subs((1-cos(x))+cos(x)*(1-cos(2*x))+cos(x)*cos(2*x)*(1-cos(3*x))-(1-cos(x)*cos(2*x)*cos(3*x)),x,Rational(1,3))", "0", "identity instance")])

row("exam_guided_multi_part", "bacii",
 [r"គេឱ្យអនុគមន៍ $f(x)=\frac{\ln(1+x)}{x}$ ។", r"១. រកដែនកំណត់នៃ $f$ ។", r"២. គណនា $\lim_{x\to-1^{+}}f(x)$ , $\lim_{x\to 0}f(x)$ និង $\lim_{x\to+\infty}f(x)$ ។", r"៣. ទាញរកអាស៊ីមតូតឈរ និងអាស៊ីមតូតដេកនៃក្រាបនៃ $f$ ។"],
 [r"១. $f$ កំណត់លុះត្រាតែ $1+x>0$ និង $x\neq 0$ ។ ដូច្នេះ $D=(-1,0)\cup(0,+\infty)$ ។",
  r"២. កាលណា $x\to-1^{+}$ គេមាន $\ln(1+x)\to-\infty$ ហើយ $x\to-1$ ។ ផលចែកខិតជិត $+\infty$ ។", r"ត្រង់ $0$ នេះជារូបមន្តគោល ៖ $\lim_{x\to 0}f(x)=1$ ។", r"ត្រង់ $+\infty$ សរសេរ ៖ $$\frac{\ln(1+x)}{x}=\frac{\ln(1+x)}{1+x}\cdot\frac{1+x}{x}$$ តាង $t=1+x\to+\infty$ កត្តាទីមួយ $\frac{\ln t}{t}\to 0$ ហើយកត្តាទីពីរខិតជិត $1$ ។ លីមីតស្មើ $0$ ។",
  r"៣. ពីលីមីតខាងលើ ៖", r"ដូចនេះ បន្ទាត់ $\boxed{x=-1}$ ជាអាស៊ីមតូតឈរ ហើយ $\boxed{y=0}$ ជាអាស៊ីមតូតដេក ។"],
 r"+\infty,\ 1,\ 0", [("limit(log(1+x)/x,x,-1,'+')", "oo"), ("limit(log(1+x)/x,x,0)", "1"), ("limit(log(1+x)/x,x,oo)", "0")],
 diagrams=graph_dia(lambda t: np.log(1 + t) / t, "ln(1+x)/x", -0.98, 8, -0.5, 5, "ក្រាបនៃ $f$ ចុះពីអាស៊ីមតូតឈរ $x=-1$ ទៅអ័ក្សអាប់ស៊ីស ។", poles=[0]))

row("number_e", "bacii",
 [r"គណនាលីមីតខាងក្រោម ដោយប្រើ $\lim_{x\to+\infty}\left(1+\frac{1}{x}\right)^{x}=e$ ឬ $\lim_{u\to 0}(1+u)^{\frac{1}{u}}=e$ ។", r"ក. $\lim_{x\to+\infty}\left(\frac{x+3}{x+1}\right)^{2x}$", r"ខ. $\lim_{x\to 0}(1+\tan x)^{\frac{2}{\sin x}}$", r"គ. $\lim_{x\to 0}(\cos 2x)^{\frac{1}{\sin^{2}x}}$"],
 [r"ក. សរសេរ $\frac{x+3}{x+1}=1+\frac{2}{x+1}$ ។ តាង $t=\frac{x+1}{2}$ ដូច្នេះ $x=2t-1$ ហើយ $2x=4t-2$ ។", r"$$\left(1+\frac{1}{t}\right)^{4t-2}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{4}\left(1+\frac{1}{t}\right)^{-2}\to e^{4}$$",
  r"ខ. តាង $u=\tan x$ ។ បើ $x\to 0$ នោះ $u\to 0$ ។ $$(1+u)^{\frac{2}{\sin x}}=\left[(1+u)^{\frac{1}{u}}\right]^{\frac{2\tan x}{\sin x}}=\left[(1+u)^{\frac{1}{u}}\right]^{\frac{2}{\cos x}}\to e^{2}$$",
  r"គ. ដោយ $\cos 2x=1-2\sin^{2}x$ តាង $u=-2\sin^{2}x$ ។ $$(1+u)^{\frac{1}{\sin^{2}x}}=\left[(1+u)^{\frac{1}{u}}\right]^{-2}\to e^{-2}$$", r"ដូចនេះ លីមីតទាំងបីគឺ $\boxed{e^{4},\ e^{2},\ e^{-2}}$ រៀងគ្នា ។"],
 r"e^{4},\ e^{2},\ e^{-2}", [("limit(((x+3)/(x+1))**(2*x),x,oo)", "exp(4)"), ("limit((1+tan(x))**(2/sin(x)),x,0)", "exp(2)"), ("limit(cos(2*x)**(1/sin(x)**2),x,0)", "exp(-2)")])

row("exam_guided_multi_part", "bacii",
 [r"គេឱ្យអនុគមន៍ $f(x)=\frac{\cos x-1}{x\sin x}$ ចំពោះ $x\in\left(0,\frac{\pi}{2}\right)$ ។", r"ក. បង្ហាញថា $f(x)=-\frac{\tan\frac{x}{2}}{x}$ ។", r"ខ. គណនា $\lim_{x\to 0^{+}}f(x)$ ។", r"គ. គណនា $\lim_{x\to\frac{\pi}{2}^{-}}f(x)$ ។"],
 [r"ក. យើងប្រើ $\cos x-1=-2\sin^{2}\frac{x}{2}$ និង $\sin x=2\sin\frac{x}{2}\cos\frac{x}{2}$ ៖", r"$$f(x)=\frac{-2\sin^{2}\frac{x}{2}}{2x\sin\frac{x}{2}\cos\frac{x}{2}}=-\frac{1}{x}\cdot\frac{\sin\frac{x}{2}}{\cos\frac{x}{2}}=-\frac{\tan\frac{x}{2}}{x}$$",
  r"ខ. តាង $u=\frac{x}{2}$ ៖ $-\frac{\tan u}{2u}\to-\frac{1}{2}$ ។", r"គ. អនុគមន៍ជាប់ត្រង់ $\frac{\pi}{2}$ ដូច្នេះជំនួសផ្ទាល់ក្នុងរូបដើម ៖ $\frac{0-1}{\frac{\pi}{2}\cdot 1}=-\frac{2}{\pi}$ ។", r"ដូចនេះ $\boxed{-\frac{1}{2}}$ និង $\boxed{-\frac{2}{\pi}}$ ជាលីមីតរៀងគ្នា ។"],
 r"-\frac{1}{2},\ -\frac{2}{\pi}", [("limit((cos(x)-1)/(x*sin(x)),x,0,'+')", "-Rational(1,2)"), ("limit((cos(x)-1)/(x*sin(x)),x,pi/2,'-')", "-2/pi"), ("(cos(x)-1)/(x*sin(x))", "-tan(x/2)/x", "identity on sample points")])

row("function_study_limits", "bacii",
 [r"គេឱ្យអនុគមន៍ $f(x)=x-1+\frac{2}{e^{x}+1}$ ។", r"ក. គណនា $\lim_{x\to+\infty}f(x)$ រួចបង្ហាញថាបន្ទាត់ $y=x-1$ ជាអាស៊ីមតូតទ្រេតត្រង់ $+\infty$ ។", r"ខ. គណនា $\lim_{x\to-\infty}f(x)$ និង $\lim_{x\to-\infty}\left[f(x)-(x+1)\right]$ ។", r"គ. ទាញរកអាស៊ីមតូតទ្រេតទីពីរ ។"],
 [r"ក. កាលណា $x\to+\infty$ គេមាន $e^{x}\to+\infty$ ដូច្នេះ $\frac{2}{e^{x}+1}\to 0$ ។ គេបាន $\lim_{x\to+\infty}f(x)=+\infty$ និង $f(x)-(x-1)\to 0$ ។", r"ខ. កាលណា $x\to-\infty$ គេមាន $e^{x}\to 0$ ដូច្នេះ $\frac{2}{e^{x}+1}\to 2$ ។ គេបាន $\lim_{x\to-\infty}f(x)=-\infty$ ។", r"$$f(x)-(x+1)=\frac{2}{e^{x}+1}-2\to 0$$",
  r"គ. លទ្ធផលខាងលើប្រាប់ថា ក្រាបខិតជិតបន្ទាត់ $y=x+1$ ត្រង់ $-\infty$ ។", r"ដូចនេះ $\boxed{y=x+1}$ ជាអាស៊ីមតូតទ្រេតត្រង់ $-\infty$ ។"],
 r"y=x-1,\ y=x+1", [("limit(x-1+2/(exp(x)+1),x,oo)", "oo"), ("limit(2/(exp(x)+1),x,oo)", "0"), ("limit(x-1+2/(exp(x)+1),x,-oo)", "-oo"), ("limit(2/(exp(x)+1)-2,x,-oo)", "0")],
 diagrams=graph_dia(lambda t: t - 1 + 2 / (np.exp(t) + 1), "x-1+2/(exp(x)+1)", -6, 6, -6, 6, "ក្រាបនៃ $f$ ខិតជិតបន្ទាត់ពីរ ត្រង់ $-\\infty$ និងត្រង់ $+\\infty$ ។", bounds=(lambda t: t - 1, lambda t: t + 1), tb=("x-1", "x+1")))

row("change_of_variable_special_angle", "bacii",
 [r"ក. បង្ហាញថា $\sqrt{3}\cos x-\sin x=2\cos\left(x+\frac{\pi}{6}\right)$ ។", r"ខ. ទាញរក $\lim_{x\to\frac{\pi}{3}}\frac{\sqrt{3}\cos x-\sin x}{x-\frac{\pi}{3}}$ ។", r"គ. គណនា $\lim_{x\to\frac{\pi}{3}}\frac{\sqrt{3}\cos x-\sin x}{\sin 3x}$ ។"],
 [r"ក. ពន្លាតអង្គស្តាំ ៖ $$2\cos\left(x+\frac{\pi}{6}\right)=2\left(\frac{\sqrt{3}}{2}\cos x-\frac{1}{2}\sin x\right)=\sqrt{3}\cos x-\sin x$$",
  r"ខ. តាង $t=x-\frac{\pi}{3}$ ។ គេបាន $x+\frac{\pi}{6}=t+\frac{\pi}{2}$ ដូច្នេះ $2\cos\left(t+\frac{\pi}{2}\right)=-2\sin t$ ។ $$\lim_{t\to 0}\frac{-2\sin t}{t}=-2$$",
  r"គ. ជាមួយការតាងដដែល ៖ $\sin 3x=\sin(3t+\pi)=-\sin 3t$ ។ $$\lim_{t\to 0}\frac{-2\sin t}{-\sin 3t}=2\cdot\frac{1}{3}=\frac{2}{3}$$", r"ដូចនេះ $\boxed{-2}$ និង $\boxed{\frac{2}{3}}$ ជាលីមីតរៀងគ្នា ។"],
 r"-2,\ \frac{2}{3}", [("limit((sqrt(3)*cos(x)-sin(x))/(x-pi/3),x,pi/3)", "-2"), ("limit((sqrt(3)*cos(x)-sin(x))/sin(3*x),x,pi/3)", "Rational(2,3)")])

# ---------- shorter hand rows ----------
row("sin_over_x_standard", "easy", r"ហេតុអ្វីបានជា $\lim_{x\to 0}\frac{\sin x^{\circ}}{x}$ មិនស្មើ $1$ ? គណនាលីមីតនេះ ដោយដឹងថា $x^{\circ}=\frac{\pi x}{180}$ រ៉ាដ្យង់ ។",
 [r"រូបមន្ត $\lim_{u\to 0}\frac{\sin u}{u}=1$ ត្រឹមត្រូវតែពេល $u$ គិតជារ៉ាដ្យង់ ។ នៅទីនេះមុំគិតជាដឺក្រេ ដូច្នេះត្រូវប្តូរខ្នាតសិន ។", r"តាង $u=\frac{\pi x}{180}$ ។ យើងបាន $$\frac{\sin\frac{\pi x}{180}}{x}=\frac{\pi}{180}\cdot\frac{\sin u}{u}$$", r"ដូចនេះ លីមីតស្មើ $\boxed{\frac{\pi}{180}}$ មិនមែន $1$ ទេ ។"],
 r"\frac{\pi}{180}", [("limit(sin(pi*x/180)/x,x,0)", "pi/180")])
row("sin_over_x_standard", "medium", r"មិត្តរួមថ្នាក់ម្នាក់សរសេរ $\lim_{x\to 0}\frac{\sin 5x}{\sin 2x}=\frac{5x}{2x}\cdot\frac{\sin}{\sin}=\frac{5}{2}$ ។ ចម្លើយត្រូវ តែការសរសេរខុស ។ ចូរសរសេរដំណោះស្រាយឱ្យត្រឹមត្រូវ ។",
 [r"និមិត្តសញ្ញា $\sin$ មិនមែនជាចំនួនដែលអាចសម្រួលបានទេ ដូច្នេះការសរសេរនោះគ្មានន័យ ។", r"វិធីត្រឹមត្រូវគឺបង្កើតរូបមន្តគោលនៅភាគយក និងភាគបែង ៖", r"$$\frac{\sin 5x}{\sin 2x}=\frac{\sin 5x}{5x}\cdot\frac{2x}{\sin 2x}\cdot\frac{5}{2}$$", r"កាលណា $x\to 0$ កត្តាពីរដំបូងខិតជិត $1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\sin 5x}{\sin 2x}=\frac{5}{2}}$ ។"],
 r"\frac{5}{2}", [("limit(sin(5*x)/sin(2*x),x,0)", "Rational(5,2)")])
row("one_minus_cos", "medium", r"សរសេរលីមីត $\lim_{x\to 0}\frac{1-\cos^{2}3x}{x^{2}\cos 3x}$ ជារាងដែលប្រើ $\frac{\sin u}{u}$ បាន រួចគណនា ។",
 [r"ភាគយកគឺ $\sin^{2}3x$ តាមទំនាក់ទំនង $\sin^{2}u+\cos^{2}u=1$ ។ ដូច្នេះ ៖", r"$$\frac{\sin^{2}3x}{x^{2}\cos 3x}=9\left(\frac{\sin 3x}{3x}\right)^{2}\cdot\frac{1}{\cos 3x}$$", r"វង់ក្រចកខិតជិត $1$ ហើយ $\frac{1}{\cos 3x}\to 1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{1-\cos^{2}3x}{x^{2}\cos 3x}=9}$ ។"],
 "9", [("limit((1-cos(3*x)**2)/(x**2*cos(3*x)),x,0)", "9")])
row("tan_minus_sin", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{\sin 2x-2\tan x}{x^{3}}$ ។",
 [r"ចាប់ផ្តើមពី $\sin 2x=2\sin x\cos x$ និង $\tan x=\frac{\sin x}{\cos x}$ ។ ដាក់ $2\tan x$ ជាកត្តារួម ៖", r"$$\sin 2x-2\tan x=2\tan x\left(\cos^{2}x-1\right)=-2\tan x\sin^{2}x$$", r"ចែកនឹង $x^{3}$ ៖ $$\frac{\sin 2x-2\tan x}{x^{3}}=-2\cdot\frac{\tan x}{x}\cdot\left(\frac{\sin x}{x}\right)^{2}$$", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\sin 2x-2\tan x}{x^{3}}=-2}$ ។"],
 "-2", [("limit((sin(2*x)-2*tan(x))/x**3,x,0)", "-2")])
row("cos_products_and_powers", "hard", r"រកតម្លៃនៃលីមីត $\lim_{x\to 0}\frac{\cos^{2}x-\cos^{2}3x}{x^{2}}$ ។",
 [r"នេះជាផលដកការេ ៖ $$\cos^{2}x-\cos^{2}3x=(\cos x-\cos 3x)(\cos x+\cos 3x)$$", r"កត្តាទីពីរខិតជិត $2$ ។ សម្រាប់កត្តាទីមួយ យើងប្រើ $\frac{\cos x-\cos 3x}{x^{2}}=\frac{1-\cos 3x}{x^{2}}-\frac{1-\cos x}{x^{2}}\to\frac{9}{2}-\frac{1}{2}=4$ ។", r"ផលគុណនៃលីមីតគឺ $4\cdot 2$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\cos^{2}x-\cos^{2}3x}{x^{2}}=8}$ ។"],
 "8", [("limit((cos(x)**2-cos(3*x)**2)/x**2,x,0)", "8"), ("limit((cos(x)-cos(3*x))/x**2,x,0)", "4", "factor")])
row("change_of_variable_pi", "hard", r"ដោយតាង $t=\frac{1}{x}$ គណនាលីមីត $\lim_{x\to+\infty}x\left(\cos\frac{1}{x}-1\right)$ ។",
 [r"បើ $x\to+\infty$ នោះ $t\to 0^{+}$ ។ កន្សោមក្លាយជា ៖", r"$$x\left(\cos\frac{1}{x}-1\right)=\frac{\cos t-1}{t}=-t\cdot\frac{1-\cos t}{t^{2}}$$", r"កត្តា $t$ ខិតជិត $0$ ហើយ $\frac{1-\cos t}{t^{2}}\to\frac{1}{2}$ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{0}$ ។"],
 "0", [("limit(x*(cos(1/x)-1),x,oo)", "0")])
row("change_of_variable_pi", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 1}(1-x)\tan\frac{\pi x}{2}$ ។",
 [r"នៅទីនេះកត្តាទីមួយខិតជិត $0$ ហើយកត្តាទីពីរធំគ្មានកំណត់ ។ យើងប្តូរអថេរ ៖ តាង $t=1-x$ ។ បើ $x\to 1$ នោះ $t\to 0$ ។", r"$$\tan\frac{\pi x}{2}=\tan\left(\frac{\pi}{2}-\frac{\pi t}{2}\right)=\cot\frac{\pi t}{2}$$", r"ដូច្នេះ $$t\cot\frac{\pi t}{2}=\frac{2}{\pi}\cdot\frac{\frac{\pi t}{2}}{\sin\frac{\pi t}{2}}\cdot\cos\frac{\pi t}{2}\to\frac{2}{\pi}$$", r"ដូចនេះ $\boxed{\lim_{x\to 1}(1-x)\tan\frac{\pi x}{2}=\frac{2}{\pi}}$ ។"],
 r"\frac{2}{\pi}", [("limit((1-x)*tan(pi*x/2),x,1)", "2/pi")])
row("root_and_trig", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{\sqrt{1+x\sin x}-\cos x}{x^{2}}$ ។",
 [r"ចែកជាពីរតួ ដោយបូក និងដក $1$ ៖", r"$$\frac{\sqrt{1+x\sin x}-1}{x^{2}}+\frac{1-\cos x}{x^{2}}$$", r"តួទីមួយ គុណនឹងកន្សោមឆ្លាស់ ៖ $$\frac{x\sin x}{x^{2}\left(\sqrt{1+x\sin x}+1\right)}=\frac{\sin x}{x}\cdot\frac{1}{\sqrt{1+x\sin x}+1}\to\frac{1}{2}$$", r"តួទីពីរខិតជិត $\frac{1}{2}$ ដែរ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\sqrt{1+x\sin x}-\cos x}{x^{2}}=1}$ ។"],
 "1", [("limit((sqrt(1+x*sin(x))-cos(x))/x**2,x,0)", "1")])
row("root_and_trig", "hard", r"រកតម្លៃនៃលីមីត $\lim_{x\to 0}\frac{\sqrt[3]{1+\sin x}-1}{x}$ ។",
 [r"តាង $u=\sqrt[3]{1+\sin x}$ ។ កាលណា $x\to 0$ គេមាន $u\to 1$ ហើយ $\sin x=u^{3}-1=(u-1)\left(u^{2}+u+1\right)$ ។", r"ដូច្នេះ $u-1=\frac{\sin x}{u^{2}+u+1}$ ។ គេបាន ៖", r"$$\frac{\sqrt[3]{1+\sin x}-1}{x}=\frac{\sin x}{x}\cdot\frac{1}{u^{2}+u+1}\to 1\cdot\frac{1}{3}$$", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\sqrt[3]{1+\sin x}-1}{x}=\frac{1}{3}}$ ។"],
 r"\frac{1}{3}", [("limit(((1+sin(x))**Rational(1,3)-1)/x,x,0)", "Rational(1,3)")])
row("squeeze_at_infinity", "medium", r"តើការសរសេរ $\lim_{x\to+\infty}\sin x=0$ ត្រឹមត្រូវឬទេ ? គណនា $\lim_{x\to+\infty}\frac{\sin x}{\sqrt{x}}$ ។",
 [r"មិនត្រឹមត្រូវទេ ។ $\sin x$ លំយោលរវាង $-1$ និង $1$ ដោយមិនខិតជិតតម្លៃណាមួយ ដូច្នេះវាគ្មានលីមីតត្រង់ $+\infty$ ទេ ។", r"ប៉ុន្តែចំពោះ $x>0$ យើងមាន $$-\frac{1}{\sqrt{x}}\le\frac{\sin x}{\sqrt{x}}\le\frac{1}{\sqrt{x}}$$", r"អង្គសងខាងខិតជិត $0$ ដូច្នេះកន្សោមកណ្តាលក៏ខិតជិត $0$ ដែរ ។", r"ដូចនេះ $\boxed{\lim_{x\to+\infty}\frac{\sin x}{\sqrt{x}}=0}$ ។"],
 "0", [("limit(sin(x)/sqrt(x),x,oo)", "0"), ("limit(1/sqrt(x),x,oo)", "0", "bound")],
 diagrams=graph_dia(lambda t: np.sin(t) / np.sqrt(np.abs(t)), "sin(x)/sqrt(x)", 0.2, 40, -1.2, 1.2, "ក្រាបលំយោលដែលទំហំតូចទៅៗ នៅចន្លោះខ្សែកោងពីរ ។", bounds=(lambda t: 1 / np.sqrt(np.abs(t)), lambda t: -1 / np.sqrt(np.abs(t))), tb=("1/sqrt(x)", "-1/sqrt(x)")))
row("squeeze_at_infinity", "medium", r"បង្ហាញថា ចំពោះ $x>1$ គេមាន $0<\frac{\ln x}{x^{2}}<\frac{1}{x}$ ដោយដឹងថា $\ln x<x$ ។ ទាញរក $\lim_{x\to+\infty}\frac{\ln x}{x^{2}}$ ។",
 [r"ចំពោះ $x>1$ យើងមាន $\ln x>0$ ដូច្នេះ $\frac{\ln x}{x^{2}}>0$ ។", r"ចែក $\ln x<x$ នឹង $x^{2}>0$ យើងបាន $\frac{\ln x}{x^{2}}<\frac{1}{x}$ ។", r"កាលណា $x\to+\infty$ គេមាន $\frac{1}{x}\to 0$ ។ កន្សោម $\frac{\ln x}{x^{2}}$ ស្ថិតនៅចន្លោះ $0$ និង $\frac{1}{x}$ ។", r"ដូចនេះ $\boxed{\lim_{x\to+\infty}\frac{\ln x}{x^{2}}=0}$ ។"],
 "0", [("limit(log(x)/x**2,x,oo)", "0"), ("limit(1/x,x,oo)", "0", "bound")])
row("comparison_infinite_limit", "medium", r"ដោយដឹងថា $e^{x}\ge 1+x$ ចំពោះគ្រប់ $x$ បង្ហាញថា $\lim_{x\to+\infty}e^{x}=+\infty$ រួចទាញរក $\lim_{x\to-\infty}e^{x}$ ។",
 [r"កាលណា $x\to+\infty$ អង្គស្តាំ $1+x\to+\infty$ ។ ដោយ $e^{x}$ ធំជាងឬស្មើវា គេបាន $\lim_{x\to+\infty}e^{x}=+\infty$ ។", r"សម្រាប់ $-\infty$ យើងតាង $t=-x$ ៖ $e^{x}=\frac{1}{e^{t}}$ ដែល $t\to+\infty$ ។ ភាគបែងធំគ្មានកំណត់ ដូច្នេះប្រភាគខិតជិត $0$ ។", r"ដូចនេះ $\boxed{\lim_{x\to+\infty}e^{x}=+\infty}$ និង $\boxed{\lim_{x\to-\infty}e^{x}=0}$ ។"],
 r"+\infty,\ 0", [("limit(exp(x),x,oo)", "oo"), ("limit(exp(x),x,-oo)", "0"), ("limit(1+x,x,oo)", "oo", "lower bound")])
row("comparison_infinite_limit", "medium", r"គេដឹងថា $\ln x\le x-1$ ចំពោះ $x>0$ ។ ដោយជំនួស $x$ ដោយ $\sqrt{x}$ បង្ហាញថា $\frac{\ln x}{x}\le\frac{2}{\sqrt{x}}$ ចំពោះ $x\ge 1$ រួចទាញរក $\lim_{x\to+\infty}\frac{\ln x}{x}$ ។",
 [r"ជំនួស ៖ $\ln\sqrt{x}\le\sqrt{x}-1<\sqrt{x}$ ។ ដោយ $\ln\sqrt{x}=\frac{1}{2}\ln x$ យើងបាន $\ln x<2\sqrt{x}$ ។", r"ចែកនឹង $x$ ៖ $\frac{\ln x}{x}<\frac{2\sqrt{x}}{x}=\frac{2}{\sqrt{x}}$ ។", r"ចំពោះ $x\ge 1$ យើងមានផងដែរ $\frac{\ln x}{x}\ge 0$ ។ កន្សោមនៅចន្លោះ $0$ និង $\frac{2}{\sqrt{x}}$ ដែលខិតជិត $0$ ។", r"ដូចនេះ $\boxed{\lim_{x\to+\infty}\frac{\ln x}{x}=0}$ ។"],
 "0", [("limit(log(x)/x,x,oo)", "0"), ("limit(2/sqrt(x),x,oo)", "0", "bound")])
row("exponential_standard", "medium", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{e^{x}+e^{-x}-2}{x^{2}}$ ។",
 [r"កត់សម្គាល់ថា ភាគយកជាការេប្រាកដ ៖", r"$$e^{x}+e^{-x}-2=\left(e^{\frac{x}{2}}-e^{-\frac{x}{2}}\right)^{2}=e^{-x}\left(e^{x}-1\right)^{2}$$", r"ដូច្នេះ $$\frac{e^{x}+e^{-x}-2}{x^{2}}=e^{-x}\left(\frac{e^{x}-1}{x}\right)^{2}\to 1\cdot 1^{2}$$", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{e^{x}+e^{-x}-2}{x^{2}}=1}$ ។"],
 "1", [("limit((exp(x)+exp(-x)-2)/x**2,x,0)", "1")])
row("exponential_standard", "hard", r"រកតម្លៃនៃលីមីត $\lim_{x\to 0}\frac{e^{\sin 2x}-e^{\sin x}}{x}$ ។",
 [r"ដាក់ $e^{\sin x}$ ជាកត្តារួម ៖ $$\frac{e^{\sin 2x}-e^{\sin x}}{x}=e^{\sin x}\cdot\frac{e^{\sin 2x-\sin x}-1}{\sin 2x-\sin x}\cdot\frac{\sin 2x-\sin x}{x}$$", r"តាង $u=\sin 2x-\sin x$ ។ កាលណា $x\to 0$ គេមាន $u\to 0$ ដូច្នេះកត្តាកណ្តាលខិតជិត $1$ ។", r"កត្តាទីមួយខិតជិត $1$ ហើយកត្តាចុងក្រោយខិតជិត $2-1=1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{e^{\sin 2x}-e^{\sin x}}{x}=1}$ ។"],
 "1", [("limit((exp(sin(2*x))-exp(sin(x)))/x,x,0)", "1")])
row("exponential_at_infinity", "medium", r"រកអាស៊ីមតូតដេកទាំងពីរនៃក្រាបនៃអនុគមន៍ $f(x)=\frac{3e^{x}-1}{e^{x}+2}$ ។",
 [r"អាស៊ីមតូតដេកបានពីលីមីតត្រង់ $\pm\infty$ ។", r"ត្រង់ $+\infty$ ចែកភាគយក និងភាគបែងនឹង $e^{x}$ ៖ $$f(x)=\frac{3-e^{-x}}{1+2e^{-x}}\to 3$$", r"ត្រង់ $-\infty$ គេមាន $e^{x}\to 0$ ដូច្នេះ $f(x)\to-\frac{1}{2}$ ។", r"ដូចនេះ បន្ទាត់ $\boxed{y=3}$ និង $\boxed{y=-\frac{1}{2}}$ ជាអាស៊ីមតូតដេក ។"],
 r"y=3,\ y=-\frac{1}{2}", [("limit((3*exp(x)-1)/(exp(x)+2),x,oo)", "3"), ("limit((3*exp(x)-1)/(exp(x)+2),x,-oo)", "-Rational(1,2)")],
 diagrams=graph_dia(lambda t: (3 * np.exp(t) - 1) / (np.exp(t) + 2), "(3*exp(x)-1)/(exp(x)+2)", -7, 7, -1.5, 4, "ក្រាបកើនពីបន្ទាត់ $y=-\\frac{1}{2}$ ទៅបន្ទាត់ $y=3$ ។", hl=(3, -0.5), tb=("3", "-0.5")))
row("logarithm_standard", "medium", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{\ln(1+2x)+\ln(1-2x)}{x^{2}}$ ។",
 [r"បញ្ចូលលោការីតទាំងពីរ ៖ $\ln(1+2x)+\ln(1-2x)=\ln\left(1-4x^{2}\right)$ ។", r"តាង $u=-4x^{2}$ ។ បើ $x\to 0$ នោះ $u\to 0$ ។", r"$$\frac{\ln\left(1-4x^{2}\right)}{x^{2}}=-4\cdot\frac{\ln(1+u)}{u}\to-4$$", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\ln(1+2x)+\ln(1-2x)}{x^{2}}=-4}$ ។"],
 "-4", [("limit((log(1+2*x)+log(1-2*x))/x**2,x,0)", "-4")])
row("logarithm_at_infinity", "medium", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to+\infty}\left[\ln(2x+1)-\ln(x+3)\right]$ ហើយពន្យល់ថាហេតុអ្វីមិនអាចដកលីមីតនីមួយៗបាន ។",
 [r"លីមីតនីមួយៗស្មើ $+\infty$ ដូច្នេះបើដកគ្នា យើងជួបរាងមិនកំណត់ $\infty-\infty$ ដែលមិនផ្តល់ចម្លើយ ។", r"យើងត្រូវបង្រួមជាលោការីតតែមួយសិន ៖ $$\ln(2x+1)-\ln(x+3)=\ln\frac{2x+1}{x+3}$$", r"ប្រភាគខិតជិត $2$ ហើយ $\ln$ ជាអនុគមន៍ជាប់ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{\ln 2}$ ។"],
 r"\ln 2", [("limit(log(2*x+1)-log(x+3),x,oo)", "log(2)")])
row("logarithm_shift", "medium", r"ដោយតាង $t=x-e$ គណនាលីមីត $\lim_{x\to e}\frac{\ln^{2}x-1}{x-e}$ ។",
 [r"ដាក់ភាគយកជាកត្តា ៖ $\ln^{2}x-1=(\ln x-1)(\ln x+1)$ ។", r"កត្តា $\ln x+1\to 2$ ។ សម្រាប់ផ្នែកដែលនៅសល់ យើងមាន $\ln x-1=\ln\frac{x}{e}=\ln\left(1+\frac{t}{e}\right)$ ។", r"$$\frac{\ln\left(1+\frac{t}{e}\right)}{t}=\frac{1}{e}\cdot\frac{\ln\left(1+\frac{t}{e}\right)}{\frac{t}{e}}\to\frac{1}{e}$$", r"ដូចនេះ $\boxed{\lim_{x\to e}\frac{\ln^{2}x-1}{x-e}=\frac{2}{e}}$ ។"],
 r"\frac{2}{e}", [("limit((log(x)**2-1)/(x-E),x,E)", "2/E")])
row("mixed_trig_exp_log", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{\ln(1+\sin^{2}x)}{e^{x^{2}}-1}$ ។",
 [r"យើងបង្កើតរូបមន្តគោលទាំងនៅភាគយក និងនៅភាគបែង ៖", r"$$\frac{\ln\left(1+\sin^{2}x\right)}{e^{x^{2}}-1}=\frac{\ln\left(1+\sin^{2}x\right)}{\sin^{2}x}\cdot\frac{x^{2}}{e^{x^{2}}-1}\cdot\left(\frac{\sin x}{x}\right)^{2}$$", r"កាលណា $x\to 0$ ទាំង $\sin^{2}x$ និង $x^{2}$ ខិតជិត $0$ ដូច្នេះកត្តាទាំងបីខិតជិត $1$ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{1}$ ។"],
 "1", [("limit(log(1+sin(x)**2)/(exp(x**2)-1),x,0)", "1")])
row("mixed_trig_exp_log", "hard", r"រកតម្លៃនៃលីមីត $\lim_{x\to\frac{\pi}{2}}\frac{\ln(\sin x)}{\cos^{2}x}$ ។",
 [r"តាង $u=\sin x-1$ ។ កាលណា $x\to\frac{\pi}{2}$ គេមាន $u\to 0$ ។", r"ភាគបែង ៖ $\cos^{2}x=1-\sin^{2}x=(1-\sin x)(1+\sin x)=-u(1+\sin x)$ ។", r"$$\frac{\ln(1+u)}{-u(1+\sin x)}=-\frac{\ln(1+u)}{u}\cdot\frac{1}{1+\sin x}\to-1\cdot\frac{1}{2}$$", r"ដូចនេះ $\boxed{\lim_{x\to\frac{\pi}{2}}\frac{\ln(\sin x)}{\cos^{2}x}=-\frac{1}{2}}$ ។"],
 r"-\frac{1}{2}", [("limit(log(sin(x))/cos(x)**2,x,pi/2)", "-Rational(1,2)")])
row("number_e", "medium", r"បើគេដាក់ប្រាក់ $1$ ឯកតា ជាមួយអត្រាការប្រាក់ $100\%$ ក្នុងមួយឆ្នាំ ហើយចែកឆ្នាំជា $x$ ដង ស្មើៗគ្នា ប្រាក់ចុងឆ្នាំគឺ $\left(1+\frac{1}{x}\right)^{x}$ ។ តើប្រាក់នេះខិតជិតប៉ុន្មាន កាលណា $x$ ធំឡើង ? ចុះបើអត្រាគឺ $5\%$ ?",
 [r"ករណីដំបូងគឺលីមីតគោល ៖ $\lim_{x\to+\infty}\left(1+\frac{1}{x}\right)^{x}=e$ ។", r"ករណីទីពីរ ប្រាក់ចុងឆ្នាំគឺ $\left(1+\frac{0.05}{x}\right)^{x}$ ។ តាង $t=\frac{x}{0.05}$ ។", r"$$\left(1+\frac{0.05}{x}\right)^{x}=\left[\left(1+\frac{1}{t}\right)^{t}\right]^{0.05}\to e^{0.05}$$", r"ដូចនេះ ប្រាក់ខិតជិត $\boxed{e}$ ក្នុងករណីទីមួយ និង $\boxed{e^{0.05}}$ ក្នុងករណីទីពីរ ។"],
 r"e,\ e^{0.05}", [("limit((1+1/x)**x,x,oo)", "E"), ("limit((1+Rational(1,20)/x)**x,x,oo)", "exp(Rational(1,20))")])
row("number_e", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\left(\frac{1+x}{1-x}\right)^{\frac{1}{x}}$ ។",
 [r"បំបែកជាផលចែកនៃស្វ័យគុណពីរ ៖ $$\left(\frac{1+x}{1-x}\right)^{\frac{1}{x}}=\frac{(1+x)^{\frac{1}{x}}}{(1-x)^{\frac{1}{x}}}$$", r"ភាគយកខិតជិត $e$ ។ ចំពោះភាគបែង តាង $u=-x$ ៖ $(1-x)^{\frac{1}{x}}=\left[(1+u)^{\frac{1}{u}}\right]^{-1}\to e^{-1}$ ។", r"ផលចែកខិតជិត $\frac{e}{e^{-1}}=e^{2}$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\left(\frac{1+x}{1-x}\right)^{\frac{1}{x}}=e^{2}}$ ។"],
 "e^{2}", [("limit(((1+x)/(1-x))**(1/x),x,0)", "exp(2)")])
row("number_e", "hard", r"រកតម្លៃនៃលីមីត $\lim_{x\to+\infty}\left(\cos\frac{2}{x}\right)^{x^{2}}$ ។",
 [r"តាង $t=\frac{1}{x}$ ។ បើ $x\to+\infty$ នោះ $t\to 0^{+}$ ហើយកន្សោមក្លាយជា $(\cos 2t)^{\frac{1}{t^{2}}}$ ។", r"តាង $u=\cos 2t-1$ ។ យើងបាន ៖ $$(\cos 2t)^{\frac{1}{t^{2}}}=\left[(1+u)^{\frac{1}{u}}\right]^{\frac{\cos 2t-1}{t^{2}}}$$", r"និទស្សន្តខិតជិត $-2$ ព្រោះ $\frac{1-\cos 2t}{t^{2}}\to 2$ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{e^{-2}}$ ។"],
 "e^{-2}", [("limit(cos(2/x)**(x**2),x,oo)", "exp(-2)")])
row("exponential_base_a", "medium", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{4^{x}-2^{x}}{x}$ ដោយពីររបៀប ។",
 [r"របៀបទី១ ៖ ដោយ $\frac{a^{x}-1}{x}\to\ln a$ យើងបំបែក $\frac{4^{x}-1}{x}-\frac{2^{x}-1}{x}\to\ln 4-\ln 2=\ln 2$ ។", r"របៀបមួយទៀត ៖ ដាក់ $2^{x}$ ជាកត្តារួម ៖ $$\frac{4^{x}-2^{x}}{x}=2^{x}\cdot\frac{2^{x}-1}{x}\to 1\cdot\ln 2$$", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{4^{x}-2^{x}}{x}=\ln 2}$ ។"],
 r"\ln 2", [("limit((4**x-2**x)/x,x,0)", "log(2)")])
row("one_sided_no_limit", "medium", r"គេឱ្យ $f(x)=\frac{|x|}{\sin x}$ ។ រកលីមីតឆ្វេង និងលីមីតស្តាំត្រង់ $0$ ។ តើ $f$ មានលីមីតត្រង់ $0$ ឬទេ ?",
 [r"ចំពោះ $x>0$ ជិត $0$ ៖ $f(x)=\frac{x}{\sin x}\to 1$ ។", r"ចំពោះ $x<0$ ជិត $0$ ៖ $|x|=-x$ ដូច្នេះ $f(x)=-\frac{x}{\sin x}\to-1$ ។", r"ដូចនេះ លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ព្រោះ $\boxed{-1\neq 1}$ ។ អនុគមន៍ $f$ គ្មានលីមីតត្រង់ $0$ ទេ ។"],
 r"\lim_{x\to 0^{-}}f(x)=-1,\ \lim_{x\to 0^{+}}f(x)=1", [("limit(Abs(x)/sin(x),x,0,'-')", "-1"), ("limit(Abs(x)/sin(x),x,0,'+')", "1")],
 diagrams=graph_dia(lambda t: np.abs(t) / np.sin(t), "abs(x)/sin(x)", -3, 3, -6, 6, "ក្រាបមានពីរមែក ដែលជិត $x=0$ មែកឆ្វេងខិតជិត $-1$ ហើយមែកស្តាំខិតជិត $1$ ។", poles=[0]))
row("one_sided_infinite", "easy", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0^{+}}\frac{\ln x}{1+x}$ និង $\lim_{x\to 0^{+}}\frac{1}{\sin x}$ ។",
 [r"លីមីតទីមួយ ៖ ភាគយកខិតជិត $-\infty$ ហើយភាគបែងខិតជិត $1$ ។ លទ្ធផលគឺ $-\infty$ ។", r"លីមីតទីពីរ ៖ ចំពោះ $x>0$ ជិត $0$ យើងមាន $\sin x>0$ ហើយ $\sin x\to 0$ ។ ប្រភាគខិតជិត $+\infty$ ។", r"ដូចនេះ $\boxed{-\infty}$ និង $\boxed{+\infty}$ ជាលីមីតរៀងគ្នា ។"],
 r"-\infty,\ +\infty", [("limit(log(x)/(1+x),x,0,'+')", "-oo"), ("limit(1/sin(x),x,0,'+')", "oo")])
row("limit_as_derivative", "medium", r"ដោយសម្គាល់ឃើញថាកន្សោមជាផលធៀបកំណើន គណនា $\lim_{h\to 0}\frac{\sin\left(\frac{\pi}{3}+h\right)-\sin\frac{\pi}{3}}{h}$ ។",
 [r"កន្សោមនេះគឺជានិយមន័យនៃ $f'\left(\frac{\pi}{3}\right)$ ដោយ $f(x)=\sin x$ ។", r"យើងមាន $f'(x)=\cos x$ ដូច្នេះ $f'\left(\frac{\pi}{3}\right)=\cos\frac{\pi}{3}=\frac{1}{2}$ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{\frac{1}{2}}$ ។"],
 r"\frac{1}{2}", [("limit((sin(pi/3+x)-sin(pi/3))/x,x,0)", "Rational(1,2)")])
row("limit_as_derivative", "medium", r"តើលីមីត $\lim_{x\to 0}\frac{e^{x}-1}{x}$ និង $\lim_{x\to 1}\frac{\ln x}{x-1}$ ជាដេរីវេនៃអនុគមន៍អ្វី ត្រង់ចំណុចណា ? ទាញរកតម្លៃរបស់វា ។",
 [r"លីមីតទីមួយជា $f'(0)$ ដោយ $f(x)=e^{x}$ ព្រោះ $f(0)=1$ ។ យើងមាន $f'(x)=e^{x}$ ដូច្នេះ $f'(0)=1$ ។", r"លីមីតទីពីរជា $g'(1)$ ដោយ $g(x)=\ln x$ ព្រោះ $g(1)=0$ ។ យើងមាន $g'(x)=\frac{1}{x}$ ដូច្នេះ $g'(1)=1$ ។", r"ដូចនេះ លីមីតទាំងពីរស្មើ $\boxed{1}$ ។"],
 "1", [("limit((exp(x)-1)/x,x,0)", "1"), ("limit(log(x)/(x-1),x,1)", "1")])
row("direct_substitution_rules", "easy", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{\cos x+e^{x}}{x+2}$ ។ បញ្ជាក់ថាហេតុអ្វីមិនចាំបាច់សម្រួលកន្សោម ។",
 [r"ភាគបែងខិតជិត $2\neq 0$ ហើយភាគយកខិតជិត $1+1=2$ ។ គ្មានរាងមិនកំណត់ទេ ដូច្នេះតាមប្រមាណវិធីលើលីមីត យើងជំនួសតម្លៃបានភ្លាម ។", r"$$\lim_{x\to 0}\frac{\cos x+e^{x}}{x+2}=\frac{\cos 0+e^{0}}{0+2}=\frac{2}{2}$$", r"ដូចនេះ លីមីតស្មើ $\boxed{1}$ ។"],
 "1", [("limit((cos(x)+exp(x))/(x+2),x,0)", "1")], grade=11)
row("direct_substitution_rules", "easy", r"គេដឹងថា $\lim_{x\to 2}f(x)=3$ និង $\lim_{x\to 2}g(x)=-1$ ។ គណនា $\lim_{x\to 2}\left[e^{g(x)+1}f(x)+\sin\left(\pi g(x)\right)\right]$ ។",
 [r"តាមប្រមាណវិធីលើលីមីត និងភាពជាប់នៃអនុគមន៍ $e^{u}$ និង $\sin u$ យើងជំនួសលីមីតទៅក្នុងកន្សោម ៖", r"$$e^{-1+1}\cdot 3+\sin(-\pi)=1\cdot 3+0$$", r"ដូចនេះ លីមីតស្មើ $\boxed{3}$ ។"],
 "3", [("exp(-1+1)*3+sin(-pi)", "3", "substitution of the limits")], grade=11)
row("sin_over_x_sum_forms", "medium", r"គេឱ្យ $f(x)=\frac{x+\sin x}{x-\sin 2x}$ ។ គណនា $\lim_{x\to 0}f(x)$ និង $\lim_{x\to+\infty}f(x)$ ហើយប្រៀបធៀបវិធីដោះស្រាយ ។",
 [r"ត្រង់ $0$ ៖ ចែកភាគយក និងភាគបែងនឹង $x$ ៖ $f(x)=\frac{1+\frac{\sin x}{x}}{1-\frac{\sin 2x}{x}}\to\frac{1+1}{1-2}=-2$ ។ នៅទីនេះយើងប្រើ $\frac{\sin u}{u}\to 1$ ។", r"ត្រង់ $+\infty$ ៖ រាងដូចគ្នា តែឥឡូវ $\frac{\sin x}{x}\to 0$ និង $\frac{\sin 2x}{x}\to 0$ ព្រោះ $\sin x$ និង $\sin 2x$ នៅចន្លោះ $-1$ និង $1$ ។ គេបាន $f(x)\to 1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}f(x)=-2}$ និង $\boxed{\lim_{x\to+\infty}f(x)=1}$ ។"],
 r"-2,\ 1", [("limit((x+sin(x))/(x-sin(2*x)),x,0)", "-2"), ("limit((x+sin(x))/(x-sin(2*x)),x,oo)", "1")])
row("growth_comparison", "medium", r"តម្រៀបតាមល្បឿនកើន ដោយគណនា $\lim_{x\to+\infty}\frac{\ln x}{\sqrt{x}}$ និង $\lim_{x\to+\infty}\frac{x^{3}}{e^{x}}$ ។",
 [r"លីមីតទីមួយ ៖ តាង $t=\sqrt{x}$ ។ បើ $x\to+\infty$ នោះ $t\to+\infty$ ហើយ $\frac{\ln x}{\sqrt{x}}=\frac{2\ln t}{t}\to 0$ ។", r"លីមីតទីពីរ ៖ តាង $t=\frac{x}{3}$ ៖ $\frac{e^{x}}{x^{3}}=\frac{1}{27}\left(\frac{e^{t}}{t}\right)^{3}\to+\infty$ ដូច្នេះ $\frac{x^{3}}{e^{x}}\to 0$ ។", r"លទ្ធផលប្រាប់ថា $\ln x$ កើនយឺតជាង $\sqrt{x}$ ហើយ $x^{3}$ កើនយឺតជាង $e^{x}$ ។", r"ដូចនេះ លីមីតទាំងពីរស្មើ $\boxed{0}$ ។"],
 "0", [("limit(log(x)/sqrt(x),x,oo)", "0"), ("limit(x**3/exp(x),x,oo)", "0")])
row("bounded_term_at_infinity", "medium", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to-\infty}\frac{2x+\cos x}{x-3}$ ។",
 [r"ចំពោះ $x<0$ ចែកភាគយក និងភាគបែងនឹង $x$ ៖ $$\frac{2+\frac{\cos x}{x}}{1-\frac{3}{x}}$$", r"ដោយ $\left|\frac{\cos x}{x}\right|\le\frac{1}{|x|}\to 0$ ភាគយកខិតជិត $2$ ។ ភាគបែងខិតជិត $1$ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{2}$ ។"],
 "2", [("limit((2*x+cos(x))/(x-3),x,-oo)", "2")])
row("continuity_extension", "medium", [r"គេឱ្យអនុគមន៍ $f$ កំណត់ដោយ ៖", r"$$f(x)=\begin{cases}\frac{\tan 2x}{\ln(1+x)} & x>0\\ a e^{x}+1 & x\le 0\end{cases}$$", r"រកតម្លៃ $a$ ដោយដឹងថា $f$ ជាប់ត្រង់ $x=0$ ។"],
 [r"សិក្សាភាពជាប់ត្រង់ $x=0$ ។ យើងមាន $f(0)=a+1$ ។", r"លីមីតឆ្វេង ៖ $\lim_{x\to 0^{-}}f(x)=a+1$ ។", r"លីមីតស្តាំ ៖ $$\lim_{x\to 0^{+}}\frac{\tan 2x}{\ln(1+x)}=\lim_{x\to 0^{+}}\frac{\tan 2x}{x}\cdot\frac{x}{\ln(1+x)}=2$$", r"$f$ ជាប់ត្រង់ $x=0$ លុះត្រាតែ $a+1=2$ $\Leftrightarrow$ $a=1$ ។", r"ដូចនេះ $\boxed{a=1}$ ។"],
 "a=1", [("limit(tan(2*x)/log(1+x),x,0,'+')", "2"), ("limit(exp(x)+1,x,0,'-')", "2")])
row("two_methods", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 0}\frac{\tan x}{\sqrt{1+x}-\sqrt{1-x}}$ ។ បន្ទាប់មកពិនិត្យលទ្ធផលដោយរបៀបមួយទៀត ។",
 [r"របៀបទី១ ៖ គុណនឹងកន្សោមឆ្លាស់ ។ យើងបាន $$\frac{\tan x\left(\sqrt{1+x}+\sqrt{1-x}\right)}{2x}=\frac{\tan x}{x}\cdot\frac{\sqrt{1+x}+\sqrt{1-x}}{2}\to 1\cdot 1$$", r"របៀបមួយទៀត ៖ ចែកភាគយក និងភាគបែងនឹង $x$ ។ ភាគយកខិតជិត $1$ ។ ភាគបែង $\frac{\sqrt{1+x}-1}{x}+\frac{1-\sqrt{1-x}}{x}\to\frac{1}{2}+\frac{1}{2}=1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 0}\frac{\tan x}{\sqrt{1+x}-\sqrt{1-x}}=1}$ ។"],
 "1", [("limit(tan(x)/(sqrt(1+x)-sqrt(1-x)),x,0)", "1")])
row("find_parameter", "medium", r"តើចំនួនពិត $k$ ស្មើប៉ុន្មាន ដើម្បីឱ្យលីមីត $\lim_{x\to 0}\frac{\sin x-k}{x}$ មានតម្លៃកំណត់ ? គណនាតម្លៃនោះ ។",
 [r"ភាគបែងខិតជិត $0$ ។ បើ $k\neq 0$ ភាគយកខិតជិត $-k\neq 0$ ហើយប្រភាគធំគ្មានកំណត់ ដូច្នេះលីមីតគ្មានតម្លៃកំណត់ទេ ។", r"ដូច្នេះ យើងត្រូវមាន $k=0$ ។ ពេលនោះ $\lim_{x\to 0}\frac{\sin x}{x}=1$ ។", r"ដូចនេះ $\boxed{k=0}$ ហើយលីមីតស្មើ $\boxed{1}$ ។"],
 r"k=0,\ 1", [("limit(sin(x)/x,x,0)", "1"), ("limit((sin(x)-1)/x,x,0,'+')", "-oo", "instance k=1 diverges")])
row("find_parameter", "hard", r"រកចំនួនពិត $a$ និង $b$ ដើម្បីឱ្យ $\lim_{x\to+\infty}\left[\ln\left(e^{2x}+1\right)-ax-b\right]=0$ ។",
 [r"យើងសរសេរ $\ln\left(e^{2x}+1\right)=2x+\ln\left(1+e^{-2x}\right)$ ។", r"ដូច្នេះ កន្សោមស្មើ $(2-a)x-b+\ln\left(1+e^{-2x}\right)$ ។ តួចុងក្រោយខិតជិត $0$ ។", r"ដើម្បីឱ្យលីមីតជាចំនួនកំណត់ មេគុណនៃ $x$ ត្រូវស្មើសូន្យ គឺ $a=2$ ។ បន្ទាប់មកលីមីតស្មើ $-b$ ដូច្នេះ $b=0$ ។", r"ដូចនេះ $\boxed{a=2,\ b=0}$ ហើយបន្ទាត់ $y=2x$ ជាអាស៊ីមតូតទ្រេត ។"],
 r"a=2,\ b=0", [("limit(log(exp(2*x)+1)-2*x,x,oo)", "0")])
row("change_of_variable_shift", "medium", r"ដោយតាង $t=x+2$ គណនាលីមីត $\lim_{x\to-2}\frac{\sin(x+2)}{x^{2}+3x+2}$ ។",
 [r"បើ $x\to-2$ នោះ $t\to 0$ ។ ដាក់ភាគបែងជាកត្តា ៖ $x^{2}+3x+2=(x+2)(x+1)=t(t-1)$ ។", r"$$\lim_{t\to 0}\frac{\sin t}{t(t-1)}=\lim_{t\to 0}\frac{\sin t}{t}\cdot\frac{1}{t-1}=1\cdot(-1)$$", r"ដូចនេះ $\boxed{\lim_{x\to-2}\frac{\sin(x+2)}{x^{2}+3x+2}=-1}$ ។"],
 "-1", [("limit(sin(x+2)/(x**2+3*x+2),x,-2)", "-1")])
row("change_of_variable_shift", "hard", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to 1}\frac{\sqrt{x}-1}{\sin(\ln x)}$ ។",
 [r"តាង $u=\ln x$ ដូច្នេះ $x=e^{u}$ ។ បើ $x\to 1$ នោះ $u\to 0$ ហើយ $\sqrt{x}=e^{\frac{u}{2}}$ ។", r"$$\frac{e^{\frac{u}{2}}-1}{\sin u}=\frac{e^{\frac{u}{2}}-1}{\frac{u}{2}}\cdot\frac{u}{\sin u}\cdot\frac{1}{2}$$", r"កត្តាពីរដំបូងខិតជិត $1$ ។", r"ដូចនេះ $\boxed{\lim_{x\to 1}\frac{\sqrt{x}-1}{\sin(\ln x)}=\frac{1}{2}}$ ។"],
 r"\frac{1}{2}", [("limit((sqrt(x)-1)/sin(log(x)),x,1)", "Rational(1,2)")])
row("trig_factor_at_pi_over_4", "medium", r"គណនាលីមីតខាងក្រោម ៖ $\lim_{x\to\frac{\pi}{4}}\frac{\sin 2x-1}{\cos^{2}2x}$ ។",
 [r"តាង $s=\sin 2x$ ។ ដោយ $\cos^{2}2x=1-s^{2}=(1-s)(1+s)$ យើងសម្រួលបាន ៖", r"$$\frac{s-1}{(1-s)(1+s)}=-\frac{1}{1+s}$$", r"កាលណា $x\to\frac{\pi}{4}$ គេមាន $s\to 1$ ។", r"ដូចនេះ លីមីតស្មើ $\boxed{-\frac{1}{2}}$ ។"],
 r"-\frac{1}{2}", [("limit((sin(2*x)-1)/cos(2*x)**2,x,pi/4)", "-Rational(1,2)")])

def hand_rows():
    return H
