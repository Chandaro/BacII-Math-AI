"""Hand-written rows for topic complex_polar: non-template Khmer. Every stated result has a SymPy check."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from common import *

H = []
def row(sub, diff, prob, sol, ans, checks, fig=None):
    H.append({"row": make_row("complex_polar", sub, diff, prob.strip(), sol.strip(), ans.strip(), [check(*c) for c in checks],
                              "complex_polar_hand", chapter="complex", grade=11), "fig": fig})

# ------------------------- long multi-part items -------------------------
row("bacii_exact_values", "bacii", r"""
គេមានចំនួនកុំផ្លិច $z_{1}=\sqrt{6}+i\sqrt{2}$ និង $z_{2}=1-i$ ។
១. សរសេរ $z_{1}$ និង $z_{2}$ ជាទម្រង់ត្រីកោណមាត្រ ។
២. គណនា $Z=\frac{z_{1}}{z_{2}}$ ជាទម្រង់ពីជគណិត និងជាទម្រង់ត្រីកោណមាត្រ ។
៣. ទាញរកតម្លៃនៃ $\cos\frac{5\pi}{12}$ , $\sin\frac{5\pi}{12}$ និង $\tan\frac{5\pi}{12}$ ។
៤. គណនា $Z^{6}$ ។
""", r"""
១. យើងមាន $|z_{1}|=\sqrt{6+2}=2\sqrt{2}$ ។ ដាក់ម៉ូឌុលជាកត្តារួម ៖
$$z_{1}=2\sqrt{2}\left(\frac{\sqrt{6}}{2\sqrt{2}}+i\frac{\sqrt{2}}{2\sqrt{2}}\right)=2\sqrt{2}\left(\frac{\sqrt{3}}{2}+\frac{1}{2}i\right)=2\sqrt{2}\left(\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}\right)$$
ចំពោះ $z_{2}$ យើងមាន $|z_{2}|=\sqrt{2}$ ហើយ
$$z_{2}=\sqrt{2}\left(\frac{\sqrt{2}}{2}-i\frac{\sqrt{2}}{2}\right)=\sqrt{2}\left(\cos\left(-\frac{\pi}{4}\right)+i\sin\left(-\frac{\pi}{4}\right)\right)$$
២. គុណភាគយក និងភាគបែងនឹង $1+i$ ៖
$$Z=\frac{\left(\sqrt{6}+i\sqrt{2}\right)(1+i)}{(1-i)(1+i)}=\frac{\sqrt{6}-\sqrt{2}+i\left(\sqrt{6}+\sqrt{2}\right)}{2}$$
តាមទម្រង់ត្រីកោណមាត្រវិញ ម៉ូឌុលគឺ $\frac{2\sqrt{2}}{\sqrt{2}}=2$ ហើយអាគុយម៉ង់គឺ $\frac{\pi}{6}+\frac{\pi}{4}=\frac{5\pi}{12}$ ។ ដូច្នេះ
$$Z=2\left(\cos\frac{5\pi}{12}+i\sin\frac{5\pi}{12}\right)$$
៣. ទម្រង់ទាំងពីរតំណាងចំនួនតែមួយ ។ ប្រៀបធៀបផ្នែកពិត និងផ្នែកនិមិត្ត ៖
$$2\cos\frac{5\pi}{12}=\frac{\sqrt{6}-\sqrt{2}}{2},\quad 2\sin\frac{5\pi}{12}=\frac{\sqrt{6}+\sqrt{2}}{2}$$
នាំឱ្យ $\cos\frac{5\pi}{12}=\frac{\sqrt{6}-\sqrt{2}}{4}$ និង $\sin\frac{5\pi}{12}=\frac{\sqrt{6}+\sqrt{2}}{4}$ ។ ចែកគ្នា ៖
$$\tan\frac{5\pi}{12}=\frac{\sqrt{6}+\sqrt{2}}{\sqrt{6}-\sqrt{2}}=\frac{\left(\sqrt{6}+\sqrt{2}\right)^{2}}{6-2}=\frac{8+4\sqrt{3}}{4}=2+\sqrt{3}$$
៤. តាមរូបមន្តដឺម័រ ៖
$$Z^{6}=2^{6}\left(\cos\frac{5\pi}{2}+i\sin\frac{5\pi}{2}\right)=64\left(\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}\right)=64i$$
ដូចនេះ $\boxed{\tan\frac{5\pi}{12}=2+\sqrt{3}}$ និង $\boxed{Z^{6}=64i}$ ។
""", r"\cos\frac{5\pi}{12}=\frac{\sqrt{6}-\sqrt{2}}{4},\ \sin\frac{5\pi}{12}=\frac{\sqrt{6}+\sqrt{2}}{4},\ \tan\frac{5\pi}{12}=2+\sqrt{3},\ Z^{6}=64i",
[("Abs(sqrt(6)+I*sqrt(2))", "2*sqrt(2)", "modulus"), ("arg(sqrt(6)+I*sqrt(2))", "pi/6", "arg"), ("arg(1-I)", "-pi/4", "arg"),
 ("simplify((sqrt(6)+I*sqrt(2))/(1-I))", "(sqrt(6)-sqrt(2)+I*(sqrt(6)+sqrt(2)))/2", "Z"), ("cos(5*pi/12)", "(sqrt(6)-sqrt(2))/4", "cos"), ("sin(5*pi/12)", "(sqrt(6)+sqrt(2))/4", "sin"),
 ("tan(5*pi/12)", "2+sqrt(3)", "tan"), ("expand(((sqrt(6)-sqrt(2)+I*(sqrt(6)+sqrt(2)))/2)**6)", "64*I", "Z^6")])

row("bacii_complex_coefficient_quadratic", "bacii", r"""
គេឱ្យសមីការ $(E):\ z^{2}-(1+3i)z-2+2i=0$ ។
ក. ផ្ទៀងផ្ទាត់ថា $(1-i)^{2}=-2i$ រួចដោះស្រាយសមីការ $(E)$ ក្នុងសំណុំចំនួនកុំផ្លិច ។
ខ. តាង $z_{1}$ ជាឫសដែលមានផ្នែកពិតខុសពីសូន្យ និង $z_{2}$ ជាឫសមួយទៀត ។ សរសេរ $z_{1}$ , $z_{2}$ និង $\frac{z_{2}}{z_{1}}$ ជាទម្រង់ត្រីកោណមាត្រ ។
គ. គណនា $z_{1}^{12}$ ។
""", r"""
ក. យើងមាន $(1-i)^{2}=1-2i+i^{2}=-2i$ ។
ឌីសគ្រីមីណង់នៃ $(E)$ ៖
$$\Delta=(1+3i)^{2}-4(-2+2i)=1+6i-9+8-8i=-2i=(1-i)^{2}$$
សមីការមានឫសពីរ ៖
$$\frac{1+3i+(1-i)}{2}=1+i,\qquad \frac{1+3i-(1-i)}{2}=2i$$
ខ. ដូច្នេះ $z_{1}=1+i$ និង $z_{2}=2i$ ។ ចំពោះ $z_{1}$ ម៉ូឌុលគឺ $\sqrt{2}$ ហើយ
$$z_{1}=\sqrt{2}\left(\frac{\sqrt{2}}{2}+i\frac{\sqrt{2}}{2}\right)=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$$
ចំពោះ $z_{2}$ ជាចំនួននិមិត្តដែលផ្នែកនិមិត្តវិជ្ជមាន ដូច្នេះ $z_{2}=2\left(\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}\right)$ ។
ចែកម៉ូឌុល និងដកអាគុយម៉ង់ ៖
$$\frac{z_{2}}{z_{1}}=\frac{2}{\sqrt{2}}\left[\cos\left(\frac{\pi}{2}-\frac{\pi}{4}\right)+i\sin\left(\frac{\pi}{2}-\frac{\pi}{4}\right)\right]=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$$
គេឃើញថា $\frac{z_{2}}{z_{1}}=z_{1}$ មានន័យថា $z_{2}=z_{1}^{2}$ ។
គ. តាមរូបមន្តដឺម័រ ៖
$$z_{1}^{12}=\left(\sqrt{2}\right)^{12}\left(\cos 3\pi+i\sin 3\pi\right)=64(-1+0i)=-64$$
ដូចនេះ ឫសនៃ $(E)$ គឺ $\boxed{1+i}$ និង $\boxed{2i}$ ហើយ $\boxed{z_{1}^{12}=-64}$ ។
""", r"z_{1}=1+i,\ z_{2}=2i,\ z_{1}^{12}=-64",
[("expand((1-I)**2)", "-2*I", "square"), ("expand((1+I)**2-(1+3*I)*(1+I)-2+2*I)", "0", "root"), ("expand((2*I)**2-(1+3*I)*(2*I)-2+2*I)", "0", "root"),
 ("simplify(2*I/(1+I))", "1+I", "quotient"), ("expand((1+I)**12)", "-64", "power")])

row("bacii_parametric_trigonometric_form", "bacii", r"""
គេឱ្យ $\theta$ ជាចំនួនពិត ដែល $-\pi<\theta<\pi$ និង $z=1+\cos\theta+i\sin\theta$ ។
១. បង្ហាញថា $z=2\cos\frac{\theta}{2}\left(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2}\right)$ ។
២. ទាញរកម៉ូឌុល និងអាគុយម៉ង់នៃ $z$ ។
៣. អនុវត្ត ៖ យក $\theta=\frac{\pi}{2}$ រួចគណនា $z^{8}$ ។
""", r"""
១. យើងប្រើរូបមន្តមុំពីរដង $1+\cos\theta=2\cos^{2}\frac{\theta}{2}$ និង $\sin\theta=2\sin\frac{\theta}{2}\cos\frac{\theta}{2}$ ៖
$$z=2\cos^{2}\frac{\theta}{2}+2i\sin\frac{\theta}{2}\cos\frac{\theta}{2}=2\cos\frac{\theta}{2}\left(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2}\right)$$
២. ដោយ $-\frac{\pi}{2}<\frac{\theta}{2}<\frac{\pi}{2}$ នោះ $\cos\frac{\theta}{2}>0$ ។ ដូច្នេះកន្សោមខាងលើជាទម្រង់ត្រីកោណមាត្រពិតប្រាកដ ៖ ម៉ូឌុលគឺ $2\cos\frac{\theta}{2}$ ហើយអាគុយម៉ង់គឺ $\frac{\theta}{2}+2k\pi,\ k\in\mathbb{Z}$ ។
៣. ពេល $\theta=\frac{\pi}{2}$ យើងបាន $z=1+i$ ហើយ $2\cos\frac{\pi}{4}=\sqrt{2}$ ។ គេបាន $z=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$ ។ តាមរូបមន្តដឺម័រ ៖
$$z^{8}=\left(\sqrt{2}\right)^{8}\left(\cos 2\pi+i\sin 2\pi\right)=16$$
ដូចនេះ $|z|=2\cos\frac{\theta}{2}$ ហើយ ចំពោះ $\theta=\frac{\pi}{2}$ យើងបាន $\boxed{z^{8}=16}$ ។
""", r"|z|=2\cos\frac{\theta}{2},\ z^{8}=16",
[("Abs(1+cos(2*pi/3)+I*sin(2*pi/3))", "2*cos(pi/3)", "instance theta=2pi/3"), ("1+cos(pi/2)+I*sin(pi/2)", "1+I", "z at pi/2"), ("expand((1+I)**8)", "16", "power"),
 ("1+cos(x)", "2*cos(x/2)**2", "identity"), ("sin(x)", "2*sin(x/2)*cos(x/2)", "identity")])

row("bacii_parametric_trigonometric_form", "bacii", r"""
គេឱ្យ $z=1+\cos\theta+i\sin\theta$ ដែល $\pi<\theta<2\pi$ ។
ក. បង្ហាញថា $\cos\frac{\theta}{2}<0$ រួចសរសេរ $z$ ជាទម្រង់ត្រីកោណមាត្រ ។
ខ. ផ្ទៀងផ្ទាត់លទ្ធផលនេះចំពោះ $\theta=\frac{4\pi}{3}$ ។
""", r"""
ក. ដោយ $\pi<\theta<2\pi$ យើងបាន $\frac{\pi}{2}<\frac{\theta}{2}<\pi$ ដូច្នេះ $\cos\frac{\theta}{2}<0$ ។
យើងប្រើរូបមន្តមុំពាក់កណ្តាល $1+\cos\theta=2\cos^{2}\frac{\theta}{2}$ និង $\sin\theta=2\sin\frac{\theta}{2}\cos\frac{\theta}{2}$ ៖
$$z=2\cos^{2}\frac{\theta}{2}+2i\sin\frac{\theta}{2}\cos\frac{\theta}{2}=2\cos\frac{\theta}{2}\left(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2}\right)$$
ប៉ុន្តែមេគុណ $2\cos\frac{\theta}{2}$ អវិជ្ជមាន ដូច្នេះនេះមិនទាន់ជាទម្រង់ត្រីកោណមាត្រទេ ។
យើងបញ្ចូលសញ្ញាដកទៅក្នុងវង់ក្រចក ដោយប្រើ $-\cos u=\cos(u+\pi)$ និង $-\sin u=\sin(u+\pi)$ ៖
$$z=-2\cos\frac{\theta}{2}\left[\cos\left(\frac{\theta}{2}+\pi\right)+i\sin\left(\frac{\theta}{2}+\pi\right)\right]$$
ឥឡូវមេគុណ $-2\cos\frac{\theta}{2}$ វិជ្ជមាន ហើយជាម៉ូឌុល ។
ខ. យក $\theta=\frac{4\pi}{3}$ ។ យើងបាន $z=1-\frac{1}{2}-i\frac{\sqrt{3}}{2}=\frac{1}{2}-i\frac{\sqrt{3}}{2}$ ដែលមានម៉ូឌុល $1$ និងអាគុយម៉ង់ $-\frac{\pi}{3}$ ។
តាមរូបមន្ត ម៉ូឌុលគឺ $-2\cos\frac{2\pi}{3}=1$ ហើយអាគុយម៉ង់គឺ $\frac{2\pi}{3}+\pi=\frac{5\pi}{3}=-\frac{\pi}{3}+2\pi$ ។ លទ្ធផលទាំងពីរត្រូវគ្នា ។
ដូចនេះ $\boxed{z=-2\cos\frac{\theta}{2}\left[\cos\left(\frac{\theta}{2}+\pi\right)+i\sin\left(\frac{\theta}{2}+\pi\right)\right]}$ ។
""", r"z=-2\cos\frac{\theta}{2}\left[\cos\left(\frac{\theta}{2}+\pi\right)+i\sin\left(\frac{\theta}{2}+\pi\right)\right]",
[("1+cos(4*pi/3)+I*sin(4*pi/3)", "Rational(1,2)-I*sqrt(3)/2", "instance"), ("arg(Rational(1,2)-I*sqrt(3)/2)", "-pi/3", "argument"), ("-2*cos(2*pi/3)", "1", "modulus"),
 ("1+cos(4*pi/3)+I*sin(4*pi/3)", "-2*cos(2*pi/3)*(cos(2*pi/3+pi)+I*sin(2*pi/3+pi))", "formula instance")])

row("bacii_conjugate_power_identity", "bacii", r"""
តាង $n$ ជាចំនួនគត់វិជ្ជមាន ។
១. សរសេរ $1+i\sqrt{3}$ និង $1-i\sqrt{3}$ ជាទម្រង់ត្រីកោណមាត្រ ។
២. បង្ហាញថា $\left(1+i\sqrt{3}\right)^{n}+\left(1-i\sqrt{3}\right)^{n}=2^{n+1}\cos\frac{n\pi}{3}$ ។
៣. ទាញរកតម្លៃនៃ $\left(1+i\sqrt{3}\right)^{9}+\left(1-i\sqrt{3}\right)^{9}$ ។
""", r"""
១. ចំនួនទាំងពីរមានម៉ូឌុល $\sqrt{1+3}=2$ ។ ដោយ $\frac{1}{2}=\cos\frac{\pi}{3}$ និង $\frac{\sqrt{3}}{2}=\sin\frac{\pi}{3}$ យើងបាន
$$1+i\sqrt{3}=2\left(\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}\right),\quad 1-i\sqrt{3}=2\left(\cos\left(-\frac{\pi}{3}\right)+i\sin\left(-\frac{\pi}{3}\right)\right)$$
២. តាមរូបមន្តដឺម័រ ៖
$$\left(1+i\sqrt{3}\right)^{n}=2^{n}\left(\cos\frac{n\pi}{3}+i\sin\frac{n\pi}{3}\right)$$
$$\left(1-i\sqrt{3}\right)^{n}=2^{n}\left(\cos\frac{n\pi}{3}-i\sin\frac{n\pi}{3}\right)$$
បូកអង្គនឹងអង្គ តួនិមិត្តលុបគ្នាអស់ នៅសល់ $2\times 2^{n}\cos\frac{n\pi}{3}=2^{n+1}\cos\frac{n\pi}{3}$ ។
៣. ជំនួស $n=9$ ៖ $2^{10}\cos 3\pi=1024\times(-1)$ ។
ដូចនេះ $\boxed{\left(1+i\sqrt{3}\right)^{9}+\left(1-i\sqrt{3}\right)^{9}=-1024}$ ។
""", r"-1024",
[("arg(1+I*sqrt(3))", "pi/3", "arg"), ("expand((1+I*sqrt(3))**9+(1-I*sqrt(3))**9)", "-1024", "n=9"), ("expand((1+I*sqrt(3))**4+(1-I*sqrt(3))**4)", "2**5*cos(4*pi/3)", "n=4 instance")])

row("textbook_cos_two_pi_over_five", "bacii", r"""
គេឱ្យសមីការ $z^{5}=1$ ក្នុងសំណុំចំនួនកុំផ្លិច ។
ក. ដោះស្រាយសមីការនេះជាទម្រង់ត្រីកោណមាត្រ ។
ខ. តាង $\omega=\cos\frac{2\pi}{5}+i\sin\frac{2\pi}{5}$ ។ បង្ហាញថា $\omega^{4}+\omega^{3}+\omega^{2}+\omega+1=0$ ។
គ. តាង $t=\omega+\frac{1}{\omega}$ ។ បង្ហាញថា $t^{2}+t-1=0$ រួចទាញរកតម្លៃនៃ $\cos\frac{2\pi}{5}$ ។
""", r"""
ក. សរសេរ $z=\rho(\cos\beta+i\sin\beta)$ ។ តាមរូបមន្តដឺម័រ $\rho^{5}=1$ និង $5\beta=2k\pi$ ។ ដូច្នេះ $\rho=1$ ហើយឫសគឺ
$$z_{k}=\cos\frac{2k\pi}{5}+i\sin\frac{2k\pi}{5},\quad k=0,1,2,3,4$$
ខ. ដោយ $\omega^{5}=1$ យើងបាន $(\omega-1)\left(\omega^{4}+\omega^{3}+\omega^{2}+\omega+1\right)=0$ ។ ប៉ុន្តែ $\omega\neq1$ ដូច្នេះកត្តាទីពីរស្មើសូន្យ ។
គ. ចែកសមភាពខាងលើនឹង $\omega^{2}\neq0$ ៖
$$\omega^{2}+\omega+1+\frac{1}{\omega}+\frac{1}{\omega^{2}}=0$$
ដោយ $t^{2}=\omega^{2}+2+\frac{1}{\omega^{2}}$ សមភាពនេះក្លាយជា $t^{2}-2+t+1=0$ គឺ $t^{2}+t-1=0$ ។
ឫសនៃសមីការនេះគឺ $t=\frac{-1\pm\sqrt{5}}{2}$ ។ ម្យ៉ាងទៀត $\frac{1}{\omega}=\cos\frac{2\pi}{5}-i\sin\frac{2\pi}{5}$ នាំឱ្យ $t=2\cos\frac{2\pi}{5}$ ។
ដោយ $0<\frac{2\pi}{5}<\frac{\pi}{2}$ នោះ $t>0$ យើងយក $t=\frac{-1+\sqrt{5}}{2}$ ។
ដូចនេះ $\boxed{\cos\frac{2\pi}{5}=\frac{\sqrt{5}-1}{4}}$ ។
""", r"\cos\frac{2\pi}{5}=\frac{\sqrt{5}-1}{4}",
[("cos(2*pi/5)", "(sqrt(5)-1)/4", "exact value"), ("4*cos(2*pi/5)**2+2*cos(2*pi/5)-1", "0", "t satisfies equation")])

row("trig_cubic_via_triple_angle", "bacii", r"""
១. ដោយប្រើរូបមន្តដឺម័រ បង្ហាញថា $\cos 3\theta=4\cos^{3}\theta-3\cos\theta$ ។
២. ដោះស្រាយសមីការ $\cos 3\theta=\frac{\sqrt{2}}{2}$ ។
៣. ទាញរកឫសទាំងបីនៃសមីការ $4x^{3}-3x=\frac{\sqrt{2}}{2}$ ។
""", r"""
១. តាមរូបមន្តដឺម័រ $(\cos\theta+i\sin\theta)^{3}=\cos 3\theta+i\sin 3\theta$ ។ ពន្លាតអង្គខាងឆ្វេង ហើយយកផ្នែកពិត ៖
$$\cos 3\theta=\cos^{3}\theta-3\cos\theta\sin^{2}\theta=\cos^{3}\theta-3\cos\theta\left(1-\cos^{2}\theta\right)=4\cos^{3}\theta-3\cos\theta$$
២. ដោយ $\frac{\sqrt{2}}{2}=\cos\frac{\pi}{4}$ យើងបាន $3\theta=\pm\frac{\pi}{4}+2k\pi$ នាំឱ្យ $\theta=\pm\frac{\pi}{12}+\frac{2k\pi}{3},\ k\in\mathbb{Z}$ ។
៣. តាង $x=\cos\theta$ ។ សមីការក្លាយជា $\cos 3\theta=\frac{\sqrt{2}}{2}$ ។ តម្លៃ $\cos\theta$ ខុសគ្នាបានពី $\theta=\frac{\pi}{12}$ , $\theta=\frac{\pi}{12}+\frac{2\pi}{3}=\frac{3\pi}{4}$ និង $\theta=\frac{\pi}{12}-\frac{2\pi}{3}=-\frac{7\pi}{12}$ ។ គេបាន
$$x_{1}=\cos\frac{\pi}{12}=\frac{\sqrt{6}+\sqrt{2}}{4},\quad x_{2}=\cos\frac{3\pi}{4}=-\frac{\sqrt{2}}{2},\quad x_{3}=\cos\frac{7\pi}{12}=\frac{\sqrt{2}-\sqrt{6}}{4}$$
សមីការដឺក្រេទីបីមានឫសមិនលើសបី ហើយតម្លៃទាំងបីនេះខុសគ្នា ។
ដូចនេះ ឫសគឺ $\boxed{\frac{\sqrt{6}+\sqrt{2}}{4}}$ , $\boxed{-\frac{\sqrt{2}}{2}}$ និង $\boxed{\frac{\sqrt{2}-\sqrt{6}}{4}}$ ។
""", r"x=\frac{\sqrt{6}+\sqrt{2}}{4},\ x=-\frac{\sqrt{2}}{2},\ x=\frac{\sqrt{2}-\sqrt{6}}{4}",
[("cos(3*x)", "4*cos(x)**3-3*cos(x)", "identity"), ("expand(4*((sqrt(6)+sqrt(2))/4)**3-3*(sqrt(6)+sqrt(2))/4)", "sqrt(2)/2", "root"), ("expand(4*(-sqrt(2)/2)**3+3*sqrt(2)/2)", "sqrt(2)/2", "root"),
 ("expand(4*((sqrt(2)-sqrt(6))/4)**3-3*(sqrt(2)-sqrt(6))/4)", "sqrt(2)/2", "root")])

row("multiple_angle_tangent", "bacii", r"""
ក. ដោយពន្លាត $(\cos\theta+i\sin\theta)^{3}$ បង្ហាញថា $\tan 3\theta=\frac{3\tan\theta-\tan^{3}\theta}{1-3\tan^{2}\theta}$ ។
ខ. យក $\theta=\frac{\pi}{12}$ និងតាង $t=\tan\frac{\pi}{12}$ ។ បង្ហាញថា $t^{3}-3t^{2}-3t+1=0$ ។
គ. ទាញរកតម្លៃនៃ $\tan\frac{\pi}{12}$ ។
""", r"""
ក. តាមរូបមន្តដឺម័រ និងការពន្លាត យើងទាញបាន
$$\cos 3\theta=\cos^{3}\theta-3\cos\theta\sin^{2}\theta,\quad \sin 3\theta=3\cos^{2}\theta\sin\theta-\sin^{3}\theta$$
ចែកអង្គនឹងអង្គ រួចចែកភាគយក និងភាគបែងនឹង $\cos^{3}\theta$ ៖
$$\tan 3\theta=\frac{3\cos^{2}\theta\sin\theta-\sin^{3}\theta}{\cos^{3}\theta-3\cos\theta\sin^{2}\theta}=\frac{3\tan\theta-\tan^{3}\theta}{1-3\tan^{2}\theta}$$
ខ. ពេល $\theta=\frac{\pi}{12}$ យើងមាន $\tan 3\theta=\tan\frac{\pi}{4}=1$ ។ ដូច្នេះ $3t-t^{3}=1-3t^{2}$ គឺ $t^{3}-3t^{2}-3t+1=0$ ។
គ. យើងឃើញថា $t=-1$ ជាឫស ។ ដាក់ជាកត្តា ៖ $(t+1)\left(t^{2}-4t+1\right)=0$ ។ ឫសគឺ $t=-1$ ឬ $t=2\pm\sqrt{3}$ ។
ដោយ $0<\frac{\pi}{12}<\frac{\pi}{4}$ នោះ $0<t<1$ ដូច្នេះត្រូវយកតែ $2-\sqrt{3}$ ។
ដូចនេះ $\boxed{\tan\frac{\pi}{12}=2-\sqrt{3}}$ ។
""", r"\tan\frac{\pi}{12}=2-\sqrt{3}",
[("tan(pi/12)", "2-sqrt(3)", "value"), ("expand((x+1)*(x**2-4*x+1))", "x**3-3*x**2-3*x+1", "factor"), ("expand((2-sqrt(3))**3-3*(2-sqrt(3))**2-3*(2-sqrt(3))+1)", "0", "root"),
 ("tan(3*x)", "(3*tan(x)-tan(x)**3)/(1-3*tan(x)**2)", "identity")])

row("textbook_equation_reduces_to_cube", "bacii", r"""
គេឱ្យសមីការ $z^{6}-9z^{3}+8=0$ ។
១. ដោយតាង $u=z^{3}$ រកតម្លៃរបស់ $u$ ។
២. ដោះស្រាយសមីការដើមក្នុងសំណុំចំនួនកុំផ្លិច ។
៣. បង្ហាញថា ផលគុណនៃឫសទាំងប្រាំមួយស្មើ $8$ ។
""", r"""
១. សមីការក្លាយជា $u^{2}-9u+8=0$ គឺ $(u-1)(u-8)=0$ ។ ដូច្នេះ $u=1$ ឬ $u=8$ ។
២. ករណី $z^{3}=1$ ៖ តាមទម្រង់ត្រីកោណមាត្រ $z=\cos\frac{2k\pi}{3}+i\sin\frac{2k\pi}{3}$ ដែល $k=0,1,2$ ។ យើងបាន
$$z=1,\quad z=-\frac{1}{2}+i\frac{\sqrt{3}}{2},\quad z=-\frac{1}{2}-i\frac{\sqrt{3}}{2}$$
ករណី $z^{3}=8$ ៖ ម៉ូឌុលគឺ $2$ ហើយអាគុយម៉ង់ដូចករណីមុន ដូច្នេះឫសជាពីរដងនៃឫសមុន ៖
$$z=2,\quad z=-1+i\sqrt{3},\quad z=-1-i\sqrt{3}$$
៣. ផលគុណនៃឫសក្រុមទីមួយគឺ $1\times\left(\frac{1}{4}+\frac{3}{4}\right)=1$ ហើយក្រុមទីពីរគឺ $2\times(1+3)=8$ ។
ដូចនេះ សមីការមានឫស $\boxed{1,\ 2,\ -\frac{1}{2}\pm i\frac{\sqrt{3}}{2},\ -1\pm i\sqrt{3}}$ ហើយផលគុណស្មើ $\boxed{8}$ ។
""", r"1,\ 2,\ -\frac{1}{2}\pm i\frac{\sqrt{3}}{2},\ -1\pm i\sqrt{3}",
[("expand((-1+I*sqrt(3))**6-9*(-1+I*sqrt(3))**3+8)", "0", "root"), ("expand((-Rational(1,2)+I*sqrt(3)/2)**6-9*(-Rational(1,2)+I*sqrt(3)/2)**3+8)", "0", "root"),
 ("expand(2*(-1+I*sqrt(3))*(-1-I*sqrt(3))*(-Rational(1,2)+I*sqrt(3)/2)*(-Rational(1,2)-I*sqrt(3)/2))", "8", "product")])

row("textbook_fourth_roots_and_factorisation", "bacii", r"""
ក. សរសេរ $-4$ ជាទម្រង់ត្រីកោណមាត្រ រួចដោះស្រាយសមីការ $z^{4}+4=0$ ។
ខ. ដៅរូបភាពនៃឫសទាំងនោះក្នុងប្លង់កុំផ្លិច រួចបង្ហាញថាជាកំពូលនៃការេមួយ ។
គ. ទាញបង្ហាញថា $z^{4}+4=\left(z^{2}-2z+2\right)\left(z^{2}+2z+2\right)$ ។
""", r"""
ក. យើងមាន $-4=4(\cos\pi+i\sin\pi)$ ។ តាង $z=\rho(\cos\beta+i\sin\beta)$ ។ សមីការ $z^{4}=-4$ ឱ្យ $\rho^{4}=4$ និង $4\beta=\pi+2k\pi$ ។ ដូច្នេះ $\rho=\sqrt{2}$ និង $\beta=\frac{\pi}{4}+\frac{k\pi}{2}$ ។
យក $k=0,1,2,3$ ៖
$$z_{0}=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)=1+i,\quad z_{1}=\sqrt{2}\left(\cos\frac{3\pi}{4}+i\sin\frac{3\pi}{4}\right)=-1+i$$
$$z_{2}=\sqrt{2}\left(\cos\frac{5\pi}{4}+i\sin\frac{5\pi}{4}\right)=-1-i,\quad z_{3}=\sqrt{2}\left(\cos\frac{7\pi}{4}+i\sin\frac{7\pi}{4}\right)=1-i$$
ខ. ចំណុចទាំងបួននៅលើរង្វង់ផ្ចិត $O$ កាំ $\sqrt{2}$ ហើយអាគុយម៉ង់ជាប់គ្នាខុសគ្នា $\frac{\pi}{2}$ ដូច្នេះអង្កត់ទ្រូងកែងគ្នា និងស្មើគ្នា ។ ជ្រុងនីមួយៗមានរង្វាស់ $2$ ឯកតា ។ ដូច្នេះវាជាការេ ។
គ. ឫសឆ្លាស់គ្នាផ្គុំជាគូ ៖
$$(z-1-i)(z-1+i)=(z-1)^{2}+1=z^{2}-2z+2$$
$$(z+1-i)(z+1+i)=(z+1)^{2}+1=z^{2}+2z+2$$
ដូចនេះ $\boxed{z^{4}+4=\left(z^{2}-2z+2\right)\left(z^{2}+2z+2\right)}$ ។
""", r"z=\pm1\pm i",
[("expand((1+I)**4+4)", "0", "root"), ("expand((-1+I)**4+4)", "0", "root"), ("expand((-1-I)**4+4)", "0", "root"), ("expand((1-I)**4+4)", "0", "root"), ("expand((x**2-2*x+2)*(x**2+2*x+2))", "x**4+4", "factorisation"), ("Abs((1+I)-(-1+I))", "2", "side")],
fig=dict(points=[("z_{0}", 1, 1), ("z_{1}", -1, 1), ("z_{2}", -1, -1), ("z_{3}", 1, -1)], circle=(2 ** .5, (0, 0)), poly=True, alt="ការេដែលមានកំពូលជារូបភាពនៃឫសទាំងបួន ចារឹកក្នុងរង្វង់ផ្ចិត O កាំ ឫសការេនៃ 2"))

row("textbook_homographic_power_equation", "hard", r"""
ដោះស្រាយសមីការ $\left(\frac{z+i}{z-i}\right)^{4}=1$ ក្នុងសំណុំចំនួនកុំផ្លិច ដែល $z\neq i$ ។
""", r"""
តាង $u=\frac{z+i}{z-i}$ ។ សមីការក្លាយជា $u^{4}=1$ ដែលមានឫសបួន ៖ $u=1$ , $u=i$ , $u=-1$ , $u=-i$ ។
ពីនិយមន័យនៃ $u$ យើងទាញ $z$ មកវិញ ។
• $u=1$ ៖ $z+i=z-i$ នាំឱ្យ $i=-i$ ដែលមិនពិត ។ ករណីនេះគ្មានឫសទេ ។
• $u=-1$ ៖ $z+i=-z+i$ នាំឱ្យ $z=0$ ។
• $u=i$ ៖ $z+i=iz+1$ នាំឱ្យ $z(1-i)=1-i$ ដូច្នេះ $z=1$ ។
• $u=-i$ ៖ $z+i=-iz-1$ នាំឱ្យ $z(1+i)=-(1+i)$ ដូច្នេះ $z=-1$ ។
ដូចនេះ សំណុំឫសគឺ $\boxed{\{-1,\ 0,\ 1\}}$ ។
""", r"\{-1,\ 0,\ 1\}",
[("simplify(((0+I)/(0-I))**4)", "1", "z=0"), ("simplify(((1+I)/(1-I))**4)", "1", "z=1"), ("simplify(((-1+I)/(-1-I))**4)", "1", "z=-1")])

row("quotient_half_angle_cotangent", "bacii", r"""
គេឱ្យ $z=\cos\alpha+i\sin\alpha$ ដែល $0<\alpha<2\pi$ ។
១. បង្ហាញថា $1+z=2\cos\frac{\alpha}{2}\left(\cos\frac{\alpha}{2}+i\sin\frac{\alpha}{2}\right)$ ។
២. បង្ហាញថា $1-z=-2i\sin\frac{\alpha}{2}\left(\cos\frac{\alpha}{2}+i\sin\frac{\alpha}{2}\right)$ ។
៣. ទាញបង្ហាញថា $\frac{1+z}{1-z}=i\cot\frac{\alpha}{2}$ រួចរកតម្លៃនៃផលចែកនេះចំពោះ $\alpha=\frac{\pi}{3}$ ។
""", r"""
១. យើងមាន $1+\cos\alpha=2\cos^{2}\frac{\alpha}{2}$ និង $\sin\alpha=2\sin\frac{\alpha}{2}\cos\frac{\alpha}{2}$ ។ បូកពីរតួនេះ រួចដាក់ $2\cos\frac{\alpha}{2}$ ជាកត្តារួម យើងបានរូបមន្តដែលត្រូវបង្ហាញ ។
២. ដូចគ្នា $1-\cos\alpha=2\sin^{2}\frac{\alpha}{2}$ ដូច្នេះ
$$1-z=2\sin^{2}\frac{\alpha}{2}-2i\sin\frac{\alpha}{2}\cos\frac{\alpha}{2}=-2i\sin\frac{\alpha}{2}\left(\cos\frac{\alpha}{2}+i\sin\frac{\alpha}{2}\right)$$
គេអាចផ្ទៀងផ្ទាត់ដោយពន្លាតអង្គខាងស្ដាំ និងប្រើ $i^{2}=-1$ ។
៣. ដោយ $0<\frac{\alpha}{2}<\pi$ នោះ $\sin\frac{\alpha}{2}\neq0$ ។ កត្តា $\cos\frac{\alpha}{2}+i\sin\frac{\alpha}{2}$ សម្រួលបាន ៖
$$\frac{1+z}{1-z}=\frac{2\cos\frac{\alpha}{2}}{-2i\sin\frac{\alpha}{2}}=\frac{1}{-i}\cot\frac{\alpha}{2}=i\cot\frac{\alpha}{2}$$
ចំពោះ $\alpha=\frac{\pi}{3}$ យើងបាន $\cot\frac{\pi}{6}=\sqrt{3}$ ។
ដូចនេះ $\boxed{\frac{1+z}{1-z}=i\sqrt{3}}$ ពេល $\alpha=\frac{\pi}{3}$ ។
""", r"\frac{1+z}{1-z}=i\sqrt{3}",
[("simplify((1+(Rational(1,2)+I*sqrt(3)/2))/(1-(Rational(1,2)+I*sqrt(3)/2)))", "I*sqrt(3)", "instance"), ("cot(pi/6)", "sqrt(3)", "cot"), ("1-cos(x)", "2*sin(x/2)**2", "identity")])

row("mixed_high_powers", "hard", r"""
គេឱ្យ $Z=\frac{\left(\sqrt{3}+i\right)^{7}}{(1+i)^{10}}$ ។ រកម៉ូឌុល និងអាគុយម៉ង់នៃ $Z$ រួចសរសេរ $Z$ ជាទម្រង់ពីជគណិត ។
""", r"""
បើពន្លាតនឹងវែងពេក យើងប្រើទម្រង់ត្រីកោណមាត្រ ។ យើងមាន
$$\sqrt{3}+i=2\left(\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}\right),\quad 1+i=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$$
តាមរូបមន្តដឺម័រ ភាគយកមានម៉ូឌុល $2^{7}=128$ និងអាគុយម៉ង់ $\frac{7\pi}{6}$ ។ ភាគបែងមានម៉ូឌុល $\left(\sqrt{2}\right)^{10}=32$ និងអាគុយម៉ង់ $\frac{10\pi}{4}=\frac{5\pi}{2}$ ។
ដូច្នេះ $|Z|=\frac{128}{32}=4$ ហើយអាគុយម៉ង់មួយគឺ
$$\frac{7\pi}{6}-\frac{5\pi}{2}=-\frac{4\pi}{3}=\frac{2\pi}{3}-2\pi$$
យើងយក $\frac{2\pi}{3}$ ។ គេបាន $$Z=4\left(\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}\right)=4\left(-\frac{1}{2}+i\frac{\sqrt{3}}{2}\right)=-2+2i\sqrt{3}$$
ដូចនេះ $|Z|=4$ អាគុយម៉ង់គឺ $\frac{2\pi}{3}+2k\pi,\ k\in\mathbb{Z}$ ហើយ $\boxed{Z=-2+2i\sqrt{3}}$ ។
""", r"Z=-2+2i\sqrt{3}",
[("simplify(expand((sqrt(3)+I)**7)/expand((1+I)**10))", "-2+2*I*sqrt(3)", "Z"), ("Abs(-2+2*I*sqrt(3))", "4", "modulus"), ("arg(-2+2*I*sqrt(3))", "2*pi/3", "argument")])

row("smallest_power_of_quotient", "bacii", r"""
គេឱ្យ $u=\frac{\sqrt{3}+i}{1-i}$ ។
ក. សរសេរ $u$ ជាទម្រង់ត្រីកោណមាត្រ ។
ខ. រកគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ដែល $u^{n}$ ជាចំនួនពិត ។
គ. រកចំនួនគត់វិជ្ជមាន $n$ តូចបំផុត ដែល $u^{n}$ ជាចំនួនពិតវិជ្ជមាន រួចគណនា $u^{n}$ នោះ ។
""", r"""
ក. ភាគយកមានម៉ូឌុល $2$ និងអាគុយម៉ង់ $\frac{\pi}{6}$ ។ ភាគបែងមានម៉ូឌុល $\sqrt{2}$ និងអាគុយម៉ង់ $-\frac{\pi}{4}$ ។ ដូច្នេះ
$$u=\frac{2}{\sqrt{2}}\left[\cos\left(\frac{\pi}{6}+\frac{\pi}{4}\right)+i\sin\left(\frac{\pi}{6}+\frac{\pi}{4}\right)\right]=\sqrt{2}\left(\cos\frac{5\pi}{12}+i\sin\frac{5\pi}{12}\right)$$
ខ. តាមរូបមន្តដឺម័រ $u^{n}=\left(\sqrt{2}\right)^{n}\left(\cos\frac{5n\pi}{12}+i\sin\frac{5n\pi}{12}\right)$ ។ វាជាចំនួនពិត លុះត្រាតែ $\sin\frac{5n\pi}{12}=0$ គឺ $\frac{5n}{12}$ ជាចំនួនគត់ ។ ដោយ $5$ និង $12$ គ្មានតួចែករួមក្រៅពី $1$ នោះ $n$ ត្រូវជាពហុគុណនៃ $12$ ។
គ. ពេល $n=12m$ យើងបាន $\cos 5m\pi=(-1)^{m}$ ។ ដើម្បីឱ្យវិជ្ជមាន $m$ ត្រូវតែគូ ហើយតម្លៃតូចបំផុតគឺ $m=2$ ។ គេបាន $n=24$ និង
$$u^{24}=\left(\sqrt{2}\right)^{24}\left(\cos 10\pi+i\sin 10\pi\right)=4096$$
ដូចនេះ $u^{n}$ ជាចំនួនពិត លុះត្រាតែ $n$ ជាពហុគុណនៃ $12$ ហើយ $\boxed{n=24}$ ឱ្យ $\boxed{u^{24}=4096}$ ។
""", r"n=24,\ u^{24}=4096",
[("Abs(simplify((sqrt(3)+I)/(1-I)))", "sqrt(2)", "modulus"), ("expand(simplify((sqrt(3)+I)/(1-I))**12)", "-64", "n=12"), ("expand(simplify((sqrt(3)+I)/(1-I))**24)", "4096", "n=24")])

row("exact_cos_pi_over_eight", "bacii", r"""
តាង $z=x+iy$ ដែល $x>0$ , $y>0$ និង $z^{2}=1+i$ ។
១. សរសេរ $1+i$ ជាទម្រង់ត្រីកោណមាត្រ រួចបង្ហាញថា អាគុយម៉ង់នៃ $z$ គឺ $\frac{\pi}{8}$ ។
២. ដោយប្រើ $x^{2}-y^{2}$ និង $x^{2}+y^{2}$ រកតម្លៃ $x^{2}$ និង $y^{2}$ ។
៣. ទាញរកតម្លៃនៃ $\cos\frac{\pi}{8}$ និង $\sin\frac{\pi}{8}$ ។
""", r"""
១. $1+i=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$ ។ បើ $\alpha$ ជាអាគុយម៉ង់នៃ $z$ នោះ $2\alpha=\frac{\pi}{4}+2k\pi$ ។ ដោយ $x>0$ និង $y>0$ មុំ $\alpha$ ស្ថិតក្នុងចន្លោះ $\left(0,\frac{\pi}{2}\right)$ ដូច្នេះ $\alpha=\frac{\pi}{8}$ ។
២. ពន្លាត $z^{2}=x^{2}-y^{2}+2ixy=1+i$ ។ ដូច្នេះ $x^{2}-y^{2}=1$ ។ ម្យ៉ាងទៀត $x^{2}+y^{2}=|z|^{2}=\left|z^{2}\right|=\sqrt{2}$ ។ បូក និងដកពីរសមីការនេះ ៖
$$x^{2}=\frac{\sqrt{2}+1}{2},\quad y^{2}=\frac{\sqrt{2}-1}{2}$$
៣. ដោយ $x=|z|\cos\frac{\pi}{8}$ និង $|z|^{2}=\sqrt{2}$ យើងបាន
$$\cos^{2}\frac{\pi}{8}=\frac{x^{2}}{\sqrt{2}}=\frac{\sqrt{2}+1}{2\sqrt{2}}=\frac{2+\sqrt{2}}{4},\quad \sin^{2}\frac{\pi}{8}=\frac{y^{2}}{\sqrt{2}}=\frac{2-\sqrt{2}}{4}$$
តម្លៃទាំងពីរវិជ្ជមាន ព្រោះ $0<\frac{\pi}{8}<\frac{\pi}{2}$ ។
ដូចនេះ $\boxed{\cos\frac{\pi}{8}=\frac{\sqrt{2+\sqrt{2}}}{2}}$ និង $\boxed{\sin\frac{\pi}{8}=\frac{\sqrt{2-\sqrt{2}}}{2}}$ ។
""", r"\cos\frac{\pi}{8}=\frac{\sqrt{2+\sqrt{2}}}{2},\ \sin\frac{\pi}{8}=\frac{\sqrt{2-\sqrt{2}}}{2}",
[("cos(pi/8)**2", "(2+sqrt(2))/4", "cos squared"), ("sin(pi/8)**2", "(2-sqrt(2))/4", "sin squared"), ("Abs(1+I)", "sqrt(2)", "modulus"), ("arg(1+I)", "pi/4", "argument")])

row("binomial_sums_via_de_moivre", "bacii", r"""
ក. ដោយប្រើទម្រង់ត្រីកោណមាត្រ គណនា $(1+i)^{10}$ ។
ខ. ពន្លាត $(1+i)^{10}$ តាមទ្វេធាញូតុន រួចទាញរកតម្លៃនៃ
$$A=1-45+210-210+45-1\quad\text{និង}\quad B=10-120+252-120+10$$
បង្ហាញថា $A$ និង $B$ ជាផ្នែកពិត និងផ្នែកនិមិត្តនៃ $(1+i)^{10}$ ។
""", r"""
ក. $1+i=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$ ។ តាមរូបមន្តដឺម័រ ៖
$$(1+i)^{10}=\left(\sqrt{2}\right)^{10}\left(\cos\frac{5\pi}{2}+i\sin\frac{5\pi}{2}\right)=32\left(\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}\right)=32i$$
ខ. មេគុណទ្វេធានៃស្វ័យគុណទី $10$ គឺ $1,10,45,120,210,252,210,120,45,10,1$ ។ ស្វ័យគុណនៃ $i$ វិលជុំ $1,i,-1,-i$ ដូច្នេះ
$$(1+i)^{10}=\left(1-45+210-210+45-1\right)+i\left(10-120+252-120+10\right)=A+iB$$
ប្រៀបធៀបជាមួយ $32i$ ផ្នែកពិតស្មើ $0$ ហើយផ្នែកនិមិត្តស្មើ $32$ ។
ដូចនេះ $\boxed{A=0}$ និង $\boxed{B=32}$ ។
""", r"A=0,\ B=32",
[("expand((1+I)**10)", "32*I", "power"), ("1-45+210-210+45-1", "0", "A"), ("10-120+252-120+10", "32", "B")])

row("textbook_factor_three_cubes", "bacii", r"""
តាង $\omega=\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}$ ។
១. បង្ហាញថា $\omega^{3}=1$ និង $1+\omega+\omega^{2}=0$ ។
២. បង្ហាញថា ចំពោះគ្រប់ចំនួនពិត $a$ , $b$ , $c$ ៖ $(a+b+c)\left(a+b\omega+c\omega^{2}\right)\left(a+b\omega^{2}+c\omega\right)=a^{3}+b^{3}+c^{3}-3abc$ ។
៣. ផ្ទៀងផ្ទាត់ចំពោះ $a=1$ , $b=2$ , $c=3$ ។
""", r"""
១. តាមរូបមន្តដឺម័រ $\omega^{3}=\cos 2\pi+i\sin 2\pi=1$ ។ ដោយ $\omega^{3}-1=(\omega-1)\left(1+\omega+\omega^{2}\right)=0$ និង $\omega\neq1$ យើងបាន $1+\omega+\omega^{2}=0$ ។
២. គុណកត្តាពីរខាងចុងសិន ៖
$$\left(a+b\omega+c\omega^{2}\right)\left(a+b\omega^{2}+c\omega\right)=a^{2}+b^{2}\omega^{3}+c^{2}\omega^{3}+ab\left(\omega+\omega^{2}\right)+ac\left(\omega+\omega^{2}\right)+bc\left(\omega^{2}+\omega^{4}\right)$$
ជំនួស $\omega^{3}=1$ , $\omega^{4}=\omega$ និង $\omega+\omega^{2}=-1$ ៖ ផលគុណនេះស្មើ $a^{2}+b^{2}+c^{2}-ab-ac-bc$ ។
គុណនឹង $a+b+c$ ជាផលគុណស្គាល់ស្រាប់ ឱ្យ $a^{3}+b^{3}+c^{3}-3abc$ ។
៣. អង្គខាងស្ដាំ ៖ $1+8+27-18=18$ ។ អង្គខាងឆ្វេង ៖ $6\times(1+4+9-2-3-6)=6\times 3=18$ ។
ដូចនេះ សមភាពផ្ទៀងផ្ទាត់ហើយ ដោយអង្គទាំងពីរស្មើ $\boxed{18}$ ។
""", r"18",
[("expand(6*(1+2*(-Rational(1,2)+I*sqrt(3)/2)+3*(-Rational(1,2)+I*sqrt(3)/2)**2)*(1+2*(-Rational(1,2)+I*sqrt(3)/2)**2+3*(-Rational(1,2)+I*sqrt(3)/2)))", "18", "instance"),
 ("expand((x+2+3)*(x**2+4+9-2*x-3*x-6))", "x**3+8+27-18*x", "identity with a=x, b=2, c=3")])

row("textbook_product_of_sines", "bacii", r"""
តាង $\omega=\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}$ ។
ក. បង្ហាញថា $\omega^{k}$ ដែល $k=0,1,\ldots,5$ ជាឫសទាំងអស់នៃ $z^{6}-1=0$ ។
ខ. ទាញបង្ហាញថា $(1-\omega)\left(1-\omega^{2}\right)\left(1-\omega^{3}\right)\left(1-\omega^{4}\right)\left(1-\omega^{5}\right)=6$ ។
គ. បង្ហាញថា $\left|1-\omega^{k}\right|=2\sin\frac{k\pi}{6}$ រួចគណនា $P=\sin\frac{\pi}{6}\sin\frac{\pi}{3}\sin\frac{\pi}{2}\sin\frac{2\pi}{3}\sin\frac{5\pi}{6}$ ។
""", r"""
ក. តាមរូបមន្តដឺម័រ $\left(\omega^{k}\right)^{6}=\cos 2k\pi+i\sin 2k\pi=1$ ។ អាគុយម៉ង់ទាំងប្រាំមួយ $\frac{k\pi}{3}$ ខុសគ្នា ហើយសមីការដឺក្រេទីប្រាំមួយមានឫសមិនលើសប្រាំមួយ ។
ខ. យើងសរសេរ $z^{6}-1=(z-1)(z-\omega)\cdots\left(z-\omega^{5}\right)$ ។ ម្យ៉ាងទៀត $z^{6}-1=(z-1)\left(z^{5}+z^{4}+z^{3}+z^{2}+z+1\right)$ ។ សម្រួលកត្តា $z-1$ ៖
$$(z-\omega)\cdots\left(z-\omega^{5}\right)=z^{5}+z^{4}+z^{3}+z^{2}+z+1$$
ជំនួស $z=1$ អង្គខាងស្ដាំស្មើ $6$ ។
គ. យក $u=\frac{k\pi}{3}$ ។ យើងមាន
$$\left|1-\omega^{k}\right|^{2}=(1-\cos u)^{2}+\sin^{2}u=2-2\cos u=4\sin^{2}\frac{u}{2}$$
ដោយ $0<\frac{u}{2}<\pi$ យើងបាន $\left|1-\omega^{k}\right|=2\sin\frac{k\pi}{6}$ ។
យកម៉ូឌុលនៃសមភាពក្នុង ខ ៖ $2^{5}P=6$ ។
ដូចនេះ $\boxed{P=\frac{3}{16}}$ ។
""", r"P=\frac{3}{16}",
[("sin(pi/6)*sin(pi/3)*sin(pi/2)*sin(2*pi/3)*sin(5*pi/6)", "Rational(3,16)", "P"), ("Abs(1-(Rational(1,2)+I*sqrt(3)/2))", "2*sin(pi/6)", "k=1"),
 ("expand((1-(Rational(1,2)+I*sqrt(3)/2))*(1-(Rational(1,2)+I*sqrt(3)/2)**2)*(1-(Rational(1,2)+I*sqrt(3)/2)**3)*(1-(Rational(1,2)+I*sqrt(3)/2)**4)*(1-(Rational(1,2)+I*sqrt(3)/2)**5))", "6", "product")])

row("textbook_spiral_of_points", "bacii", r"""
ក្នុងប្លង់កុំផ្លិច គេឱ្យចំណុច $M_{n}$ ជារូបភាពនៃ $z_{n}=(1+i)^{n}$ ដែល $n$ ជាចំនួនគត់មិនអវិជ្ជមាន ។
១. គណនា $z_{0}$ , $z_{1}$ , $z_{2}$ , $z_{3}$ និង $z_{4}$ រួចដៅចំណុចទាំងនោះ ។
២. បង្ហាញថា $z_{n+1}-z_{n}=iz_{n}$ ។ ទាញរកប្រភេទនៃត្រីកោណ $OM_{n}M_{n+1}$ ។
៣. រកចំនួនគត់វិជ្ជមាន $n$ តូចបំផុត ដែល $M_{n}$ នៅលើអ័ក្សពិតផ្នែកវិជ្ជមាន ។
""", r"""
១. គុណនឹង $1+i$ ម្ដងមួយៗ យើងបាន ៖ $z_{0}=1$ , $z_{1}=1+i$ , $z_{2}=2i$ , $z_{3}=-2+2i$ , $z_{4}=-4$ ។
២. $z_{n+1}-z_{n}=(1+i)^{n}(1+i-1)=iz_{n}$ ។ យកម៉ូឌុល ៖ $M_{n}M_{n+1}=|z_{n}|=OM_{n}$ ។ ម្យ៉ាងទៀត វ៉ិចទ័រ $\overrightarrow{M_{n}M_{n+1}}$ បានមកពី $\overrightarrow{OM_{n}}$ ដោយគុណនឹង $i$ ដូច្នេះវាកែងនឹងគ្នា ។
ត្រីកោណ $OM_{n}M_{n+1}$ ជាត្រីកោណកែងសមបាតត្រង់ $M_{n}$ ។
៣. យើងមាន $z_{n}=\left(\sqrt{2}\right)^{n}\left(\cos\frac{n\pi}{4}+i\sin\frac{n\pi}{4}\right)$ ។ $M_{n}$ នៅលើអ័ក្សពិតផ្នែកវិជ្ជមាន លុះត្រាតែ $\frac{n\pi}{4}=2k\pi$ គឺ $n=8k$ ។ តម្លៃតូចបំផុតគឺ $n=8$ ដែល $z_{8}=16$ ។
ដូចនេះ $\boxed{n=8}$ ។
""", r"n=8",
[("expand((1+I)**3)", "-2+2*I", "z3"), ("expand((1+I)**4)", "-4", "z4"), ("expand((1+I)**8)", "16", "z8"), ("expand((1+I)**6-(1+I)**5-I*(1+I)**5)", "0", "n=5 instance"), ("Abs((1+I)**3-(1+I)**2)", "Abs((1+I)**2)", "isosceles instance")],
fig=dict(points=[("M_{0}", 1, 0), ("M_{1}", 1, 1), ("M_{2}", 0, 2), ("M_{3}", -2, 2), ("M_{4}", -4, 0)], circle=None, poly=False, alt="ចំណុច M0 ដល់ M4 រៀបជារាងវង់ចេញពីគល់តម្រុយ"))

row("bacii_exact_values", "bacii", r"""
គេមាន $z_{1}=-1+i$ និង $z_{2}=1+i\sqrt{3}$ ។
ក. គណនា $z_{1}\times z_{2}$ ជាទម្រង់ពីជគណិត ។
ខ. រកម៉ូឌុល និងអាគុយម៉ង់នៃ $z_{1}$ , $z_{2}$ ។
គ. សរសេរ $z_{1}\times z_{2}$ ជាទម្រង់ត្រីកោណមាត្រ ដោយយកអាគុយម៉ង់ក្នុងចន្លោះ $(-\pi,\pi]$ ។
ឃ. ទាញរកតម្លៃនៃ $\cos\frac{11\pi}{12}$ និង $\sin\frac{11\pi}{12}$ ។
""", r"""
ក. $z_{1}\times z_{2}=(-1+i)\left(1+i\sqrt{3}\right)=-1-i\sqrt{3}+i+i^{2}\sqrt{3}$ ។ ដោយ $i^{2}=-1$ ៖
$$z_{1}\times z_{2}=-\left(1+\sqrt{3}\right)+i\left(1-\sqrt{3}\right)$$
ខ. $|z_{1}|=\sqrt{2}$ ហើយ $\cos\alpha_{1}=-\frac{\sqrt{2}}{2}$ , $\sin\alpha_{1}=\frac{\sqrt{2}}{2}$ នាំឱ្យ $\alpha_{1}=\frac{3\pi}{4}+2k\pi$ ។
$|z_{2}|=2$ ហើយ $\cos\alpha_{2}=\frac{1}{2}$ , $\sin\alpha_{2}=\frac{\sqrt{3}}{2}$ នាំឱ្យ $\alpha_{2}=\frac{\pi}{3}+2k\pi$ ។
គ. ម៉ូឌុលនៃផលគុណគឺ $2\sqrt{2}$ ហើយ $\frac{3\pi}{4}+\frac{\pi}{3}=\frac{13\pi}{12}$ ។ មុំនេះលើសពី $\pi$ ដូច្នេះដក $2\pi$ ៖ $\frac{13\pi}{12}-2\pi=-\frac{11\pi}{12}$ ។
$$z_{1}\times z_{2}=2\sqrt{2}\left[\cos\left(-\frac{11\pi}{12}\right)+i\sin\left(-\frac{11\pi}{12}\right)\right]$$
ឃ. ប្រៀបធៀបជាមួយលទ្ធផលក្នុងសំណួរ ក ៖
$$2\sqrt{2}\cos\frac{11\pi}{12}=-\left(1+\sqrt{3}\right),\quad -2\sqrt{2}\sin\frac{11\pi}{12}=1-\sqrt{3}$$
គុណភាគយក និងភាគបែងនឹង $\sqrt{2}$ ។
ដូចនេះ $\boxed{\cos\frac{11\pi}{12}=-\frac{\sqrt{6}+\sqrt{2}}{4}}$ និង $\boxed{\sin\frac{11\pi}{12}=\frac{\sqrt{6}-\sqrt{2}}{4}}$ ។
""", r"\cos\frac{11\pi}{12}=-\frac{\sqrt{6}+\sqrt{2}}{4},\ \sin\frac{11\pi}{12}=\frac{\sqrt{6}-\sqrt{2}}{4}",
[("expand((-1+I)*(1+I*sqrt(3)))", "-(1+sqrt(3))+I*(1-sqrt(3))", "product"), ("arg(-1+I)", "3*pi/4", "arg"), ("arg(1+I*sqrt(3))", "pi/3", "arg"), ("cos(11*pi/12)", "-(sqrt(6)+sqrt(2))/4", "cos"), ("sin(11*pi/12)", "(sqrt(6)-sqrt(2))/4", "sin")])

row("quadratic_with_cos_coefficient", "bacii", r"""
គេឱ្យសមីការ $z^{2}-2z\cos\theta+1=0$ ដែល $0<\theta<\pi$ ។
១. ដោះស្រាយសមីការនេះក្នុងសំណុំចំនួនកុំផ្លិច ហើយសរសេរឫសជាទម្រង់ត្រីកោណមាត្រ ។
២. បង្ហាញថា $z_{1}^{n}+z_{2}^{n}=2\cos n\theta$ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ។
៣. អនុវត្ត ៖ បើ $z_{1}$ , $z_{2}$ ជាឫសនៃ $z^{2}-\sqrt{3}z+1=0$ គណនា $z_{1}^{100}+z_{2}^{100}$ ។
""", r"""
១. ឌីសគ្រីមីណង់ ៖ $$\Delta=4\cos^{2}\theta-4=-4\sin^{2}\theta=(2i\sin\theta)^{2}$$
ឫសគឺ $z_{1}=\cos\theta+i\sin\theta$ និង $z_{2}=\cos\theta-i\sin\theta=\cos(-\theta)+i\sin(-\theta)$ ។
២. តាមរូបមន្តដឺម័រ $z_{1}^{n}=\cos n\theta+i\sin n\theta$ និង $z_{2}^{n}=\cos n\theta-i\sin n\theta$ ។ បូកចូលគ្នា យើងបាន $2\cos n\theta$ ។
៣. ដោយ $2\cos\theta=\sqrt{3}$ និង $0<\theta<\pi$ យើងបាន $\theta=\frac{\pi}{6}$ ។ ដូច្នេះ
$$z_{1}^{100}+z_{2}^{100}=2\cos\frac{100\pi}{6}=2\cos\frac{50\pi}{3}$$
ដោយ $\frac{50\pi}{3}=\frac{2\pi}{3}+16\pi$ នោះកូស៊ីនុសស្មើ $\cos\frac{2\pi}{3}=-\frac{1}{2}$ ។
ដូចនេះ $\boxed{z_{1}^{100}+z_{2}^{100}=-1}$ ។
""", r"z_{1}^{100}+z_{2}^{100}=-1",
[("2*cos(100*pi/6)", "-1", "value"), ("expand((sqrt(3)/2+I/2)**2-sqrt(3)*(sqrt(3)/2+I/2)+1)", "0", "root"), ("expand((sqrt(3)/2+I/2)**12)", "1", "period 12"), ("expand((sqrt(3)/2+I/2)**4+(sqrt(3)/2-I/2)**4)", "-1", "100 = 4 mod 12")])

row("bacii_complex_coefficient_quadratic", "bacii", r"""
គេមានសមីការ $z^{2}-2iz-2=0$ ។
ក. ដោះស្រាយសមីការនេះ ។ តាង $z_{1}$ ជាឫសដែលមានផ្នែកពិតវិជ្ជមាន និង $z_{2}$ ជាឫសមួយទៀត ។
ខ. សរសេរ $z_{1}$ និង $z_{2}$ ជាទម្រង់ត្រីកោណមាត្រ ។
គ. គណនា $z_{1}\times z_{2}$ តាមពីរវិធី ។
ឃ. គណនា $z_{1}^{10}+z_{2}^{10}$ ។
""", r"""
ក. យើងអាចបំពេញការេ ៖ $z^{2}-2iz+i^{2}-i^{2}-2=(z-i)^{2}+1-2=(z-i)^{2}-1$ ។ សមីការក្លាយជា $(z-i)^{2}=1$ ។ ដូច្នេះ $z-i=1$ ឬ $z-i=-1$ ។ គេបាន $z_{1}=1+i$ និង $z_{2}=-1+i$ ។
ខ. ចំនួនទាំងពីរមានម៉ូឌុល $\sqrt{2}$ ។ ដូច្នេះ
$$z_{1}=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right),\quad z_{2}=\sqrt{2}\left(\cos\frac{3\pi}{4}+i\sin\frac{3\pi}{4}\right)$$
គ. ពន្លាត ៖ $(1+i)(-1+i)=i^{2}-1=-2$ ។ តាមទម្រង់ត្រីកោណមាត្រ ម៉ូឌុលគឺ $2$ ហើយអាគុយម៉ង់គឺ $\frac{\pi}{4}+\frac{3\pi}{4}=\pi$ ដូច្នេះផលគុណក៏ស្មើ $-2$ ដែរ ។ លទ្ធផលនេះត្រូវនឹងតួថេរនៃសមីការ ។
ឃ. តាមរូបមន្តដឺម័រ ៖
$$z_{1}^{10}=32\left(\cos\frac{5\pi}{2}+i\sin\frac{5\pi}{2}\right)=32i$$
$$z_{2}^{10}=32\left(\cos\frac{15\pi}{2}+i\sin\frac{15\pi}{2}\right)=32\left(\cos\left(-\frac{\pi}{2}\right)+i\sin\left(-\frac{\pi}{2}\right)\right)=-32i$$
ដូចនេះ $\boxed{z_{1}^{10}+z_{2}^{10}=0}$ ។
""", r"z_{1}=1+i,\ z_{2}=-1+i,\ z_{1}^{10}+z_{2}^{10}=0",
[("expand((1+I)**2-2*I*(1+I)-2)", "0", "root"), ("expand((-1+I)**2-2*I*(-1+I)-2)", "0", "root"), ("expand((1+I)*(-1+I))", "-2", "product"), ("expand((1+I)**10)", "32*I", "power"), ("expand((-1+I)**10)", "-32*I", "power")])

row("textbook_twelfth_root_equation", "bacii", r"""
គេឱ្យសមីការ $z^{4}-z^{2}+1=0$ ។
១. ដោយតាង $u=z^{2}$ រក $u$ ជាទម្រង់ត្រីកោណមាត្រ ។
២. ទាញរកឫសទាំងបួននៃសមីការ ជាទម្រង់ពីជគណិត ។
៣. បង្ហាញថា ឫសនីមួយៗផ្ទៀងផ្ទាត់ $z^{12}=1$ ។
""", r"""
១. $u^{2}-u+1=0$ មាន $\Delta=-3=\left(i\sqrt{3}\right)^{2}$ ។ ឫសគឺ
$$u=\frac{1\pm i\sqrt{3}}{2}=\cos\frac{\pi}{3}\pm i\sin\frac{\pi}{3}$$
២. ករណី $z^{2}=\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}$ ៖ ម៉ូឌុលគឺ $1$ ហើយអាគុយម៉ង់គឺ $\frac{\pi}{6}+k\pi$ ។ ឫសគឺ $\pm\left(\frac{\sqrt{3}}{2}+\frac{1}{2}i\right)$ ។
ករណី $z^{2}=\cos\frac{\pi}{3}-i\sin\frac{\pi}{3}$ ៖ ដូចគ្នា អាគុយម៉ង់គឺ $-\frac{\pi}{6}+k\pi$ ។ ឫសគឺ $\pm\left(\frac{\sqrt{3}}{2}-\frac{1}{2}i\right)$ ។
៣. ឫសទាំងអស់មានអាគុយម៉ង់ជាពហុគុណសេសនៃ $\frac{\pi}{6}$ ។ តាមរូបមន្តដឺម័រ $z^{12}=\cos(12\beta)+i\sin(12\beta)$ ហើយ $12\beta$ ជាពហុគុណនៃ $2\pi$ ។ ដូច្នេះ $z^{12}=1$ ។
ដូចនេះ ឫសគឺ $\boxed{z=\pm\frac{\sqrt{3}}{2}\pm\frac{1}{2}i}$ ។
""", r"z=\pm\frac{\sqrt{3}}{2}\pm\frac{1}{2}i",
[("expand((sqrt(3)/2+I/2)**4-(sqrt(3)/2+I/2)**2+1)", "0", "root"), ("expand((sqrt(3)/2-I/2)**4-(sqrt(3)/2-I/2)**2+1)", "0", "root"), ("expand((sqrt(3)/2+I/2)**12)", "1", "twelfth power")])

row("trig_identity_three_directions", "hard", r"""
តាង $\omega=\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}$ និង $z=\cos\theta+i\sin\theta$ ។ ដោយពិនិត្យ $z+z\omega+z\omega^{2}$ បង្ហាញថា $\cos\theta+\cos\left(\theta+\frac{2\pi}{3}\right)+\cos\left(\theta+\frac{4\pi}{3}\right)=0$ ។
""", r"""
យើងដឹងថា $1+\omega+\omega^{2}=0$ ព្រោះ $\omega$ ជាឫសទីបីនៃ $1$ ខុសពី $1$ ។ ដូច្នេះ
$$z+z\omega+z\omega^{2}=z\left(1+\omega+\omega^{2}\right)=0$$
គុណចំនួនកុំផ្លិចជាទម្រង់ត្រីកោណមាត្រ គឺបូកអាគុយម៉ង់ ៖
$$z\omega=\cos\left(\theta+\frac{2\pi}{3}\right)+i\sin\left(\theta+\frac{2\pi}{3}\right),\quad z\omega^{2}=\cos\left(\theta+\frac{4\pi}{3}\right)+i\sin\left(\theta+\frac{4\pi}{3}\right)$$
ផ្នែកពិតនៃផលបូកត្រូវស្មើសូន្យ ។
ដូចនេះ $\boxed{\cos\theta+\cos\left(\theta+\frac{2\pi}{3}\right)+\cos\left(\theta+\frac{4\pi}{3}\right)=0}$ ។ ផ្នែកនិមិត្តឱ្យសមភាពដូចគ្នាចំពោះស៊ីនុស ។
""", r"\cos\theta+\cos\left(\theta+\frac{2\pi}{3}\right)+\cos\left(\theta+\frac{4\pi}{3}\right)=0",
[("cos(x)+cos(x+2*pi/3)+cos(x+4*pi/3)", "0", "identity"), ("sin(x)+sin(x+2*pi/3)+sin(x+4*pi/3)", "0", "identity")])

row("cosine_sum_via_geometric_series", "bacii", r"""
តាង $z=\cos\theta+i\sin\theta$ ដែល $0<\theta<2\pi$ ។
១. បង្ហាញថា $z^{n}-1=2i\sin\frac{n\theta}{2}\left(\cos\frac{n\theta}{2}+i\sin\frac{n\theta}{2}\right)$ ។
២. ដោយប្រើ $z+z^{2}+z^{3}=\frac{z\left(z^{3}-1\right)}{z-1}$ ទាញបង្ហាញថា $\cos\theta+\cos 2\theta+\cos 3\theta=\frac{\sin\frac{3\theta}{2}\cos 2\theta}{\sin\frac{\theta}{2}}$ ។
៣. គណនាផលបូកនេះចំពោះ $\theta=\frac{\pi}{2}$ ។
""", r"""
១. យើងមាន $z^{n}=\cos n\theta+i\sin n\theta$ ។ យក $u=\frac{n\theta}{2}$ ៖
$$z^{n}-1=\cos 2u-1+i\sin 2u=-2\sin^{2}u+2i\sin u\cos u=2i\sin u\left(\cos u+i\sin u\right)$$
២. ប្រើរូបមន្ត ១ ជាមួយ $n=3$ និង $n=1$ ៖
$$\frac{z^{3}-1}{z-1}=\frac{\sin\frac{3\theta}{2}}{\sin\frac{\theta}{2}}\left(\cos\theta+i\sin\theta\right)$$
ព្រោះផលដកនៃអាគុយម៉ង់គឺ $\frac{3\theta}{2}-\frac{\theta}{2}=\theta$ ។ គុណនឹង $z$ បន្ថែមទៀត ៖
$$z+z^{2}+z^{3}=\frac{\sin\frac{3\theta}{2}}{\sin\frac{\theta}{2}}\left(\cos 2\theta+i\sin 2\theta\right)$$
យកផ្នែកពិតនៃអង្គទាំងពីរ យើងបានសមភាពដែលត្រូវបង្ហាញ ។
៣. ជំនួស $\theta=\frac{\pi}{2}$ ៖ $\frac{\sin\frac{3\pi}{4}\cos\pi}{\sin\frac{\pi}{4}}=-1$ ។ ផ្ទៀងផ្ទាត់ដោយផ្ទាល់ ៖ $0+(-1)+0=-1$ ។
ដូចនេះ $\boxed{\cos\theta+\cos 2\theta+\cos 3\theta=-1}$ ពេល $\theta=\frac{\pi}{2}$ ។
""", r"-1",
[("cos(x)+cos(2*x)+cos(3*x)", "sin(3*x/2)*cos(2*x)/sin(x/2)", "identity"), ("cos(pi/2)+cos(pi)+cos(3*pi/2)", "-1", "value")])

row("textbook_square_from_rotation", "hard", r"""
ក្នុងប្លង់កុំផ្លិច គេឱ្យចំណុច $A$ និង $B$ ជារូបភាពនៃ $z_{A}=1+2i$ និង $z_{B}=4+3i$ ។ រកចំនួនកុំផ្លិច $z_{C}$ និង $z_{D}$ ដែល $ABCD$ ជាការេ ហើយកំពូលរៀបតាមទិសច្រាសទ្រនិចនាឡិកា ។
""", r"""
ការគុណនឹង $i$ បង្វិលវ៉ិចទ័រមួយមុំ $\frac{\pi}{2}$ ដោយមិនប្ដូរប្រវែង ព្រោះ $i=\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}$ ។
វ៉ិចទ័រ $\overrightarrow{AB}$ ត្រូវនឹង $z_{B}-z_{A}=3+i$ ។ ក្នុងការេ $ABCD$ វ៉ិចទ័រ $\overrightarrow{BC}$ និង $\overrightarrow{AD}$ បានមកពី $\overrightarrow{AB}$ ដោយគុណនឹង $i$ ៖
$$i(3+i)=-1+3i$$
ដូច្នេះ
$$z_{C}=z_{B}+(-1+3i)=3+6i,\quad z_{D}=z_{A}+(-1+3i)=5i$$
ពិនិត្យ ៖ $CD=|5i-3-6i|=|-3-i|=\sqrt{10}=AB$ ។
ដូចនេះ $\boxed{z_{C}=3+6i}$ និង $\boxed{z_{D}=5i}$ ។
""", r"z_{C}=3+6i,\ z_{D}=5i",
[("I*((4+3*I)-(1+2*I))", "-1+3*I", "rotation"), ("4+3*I+I*(3+I)", "3+6*I", "C"), ("1+2*I+I*(3+I)", "5*I", "D"), ("Abs(5*I-(3+6*I))", "Abs(3+I)", "side"), ("Abs(3+I)", "sqrt(10)", "side")],
fig=dict(points=[("A", 1, 2), ("B", 4, 3), ("C", 3, 6), ("D", 0, 5)], circle=None, poly=True, alt="ការេ ABCD ក្នុងប្លង់កុំផ្លិច"))

row("textbook_equilateral_third_vertex", "hard", r"""
គេឱ្យចំណុច $A$ និង $B$ ជារូបភាពនៃ $z_{A}=1+i$ និង $z_{B}=3+i$ ។ រកចំនួនកុំផ្លិច $z_{C}$ ដែល $ABC$ ជាត្រីកោណសម័ង្ស ។
""", r"""
ត្រីកោណសម័ង្សមាន $AC=AB$ និងមុំ $BAC$ ស្មើ $\frac{\pi}{3}$ ។ ដូច្នេះ $z_{C}-z_{A}$ បានមកពី $z_{B}-z_{A}$ ដោយគុណនឹង $\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}$ ឬ $\cos\frac{\pi}{3}-i\sin\frac{\pi}{3}$ ។
យើងមាន $z_{B}-z_{A}=2$ ។
ករណីទីមួយ ៖ $$z_{C}=1+i+2\left(\frac{1}{2}+i\frac{\sqrt{3}}{2}\right)=2+i\left(1+\sqrt{3}\right)$$
ករណីទីពីរ ៖ $$z_{C}=1+i+2\left(\frac{1}{2}-i\frac{\sqrt{3}}{2}\right)=2+i\left(1-\sqrt{3}\right)$$
ដូចនេះ $\boxed{z_{C}=2+i\left(1+\sqrt{3}\right)}$ ឬ $\boxed{z_{C}=2+i\left(1-\sqrt{3}\right)}$ ។
""", r"z_{C}=2+i\left(1\pm\sqrt{3}\right)",
[("Abs(2+I*(1+sqrt(3))-(1+I))", "2", "AC"), ("Abs(2+I*(1+sqrt(3))-(3+I))", "2", "BC"), ("Abs(2+I*(1-sqrt(3))-(1+I))", "2", "AC"), ("Abs(2+I*(1-sqrt(3))-(3+I))", "2", "BC")],
fig=dict(points=[("A", 1, 1), ("B", 3, 1), ("C", 2, 2.732)], circle=None, poly=True, alt="ត្រីកោណសម័ង្ស ABC ក្នុងករណីទីមួយ"))

row("tangent_power_identity", "bacii", r"""
តាង $\alpha$ ជាចំនួនពិត ដែល $\cos\alpha\neq0$ ។
ក. បង្ហាញថា $\frac{1+i\tan\alpha}{1-i\tan\alpha}=\cos 2\alpha+i\sin 2\alpha$ ។
ខ. ទាញបង្ហាញថា $\left(\frac{1+i\tan\alpha}{1-i\tan\alpha}\right)^{n}=\frac{1+i\tan n\alpha}{1-i\tan n\alpha}$ ចំពោះ $n$ ដែល $\cos n\alpha\neq0$ ។
គ. គណនា $\left(\frac{1+i\tan\frac{\pi}{12}}{1-i\tan\frac{\pi}{12}}\right)^{3}$ ។
""", r"""
ក. គុណភាគយក និងភាគបែងនឹង $\cos\alpha$ ៖
$$\frac{1+i\tan\alpha}{1-i\tan\alpha}=\frac{\cos\alpha+i\sin\alpha}{\cos\alpha-i\sin\alpha}=\frac{\cos\alpha+i\sin\alpha}{\cos(-\alpha)+i\sin(-\alpha)}$$
ចែកចំនួនពីរដែលមានម៉ូឌុល $1$ គឺដកអាគុយម៉ង់ ៖ លទ្ធផលគឺ $\cos 2\alpha+i\sin 2\alpha$ ។
ខ. តាមរូបមន្តដឺម័រ អង្គខាងឆ្វេងស្មើ $\cos 2n\alpha+i\sin 2n\alpha$ ។ យករូបមន្តក្នុងសំណួរ ក ដោយជំនួស $\alpha$ ដោយ $n\alpha$ អង្គខាងស្ដាំក៏ស្មើចំនួននេះដែរ ។
គ. យក $\alpha=\frac{\pi}{12}$ និង $n=3$ ៖ កន្សោមស្មើ
$$\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}=i$$
ដូចនេះ លទ្ធផលគឺ $\boxed{i}$ ។
""", r"i",
[("simplify(((1+I*(2-sqrt(3)))/(1-I*(2-sqrt(3))))**3)", "I", "instance"), ("tan(pi/12)", "2-sqrt(3)", "tan"), ("simplify((1+I*tan(pi/6))/(1-I*tan(pi/6)))", "cos(pi/3)+I*sin(pi/3)", "formula at pi/6")])

# ------------------------- shorter varied items -------------------------
row("modulus_argument_axis", "easy", r"""
រកម៉ូឌុល និងអាគុយម៉ង់នៃចំនួនកុំផ្លិច $z_{1}=-5$ , $z_{2}=3i$ និង $z_{3}=-2i$ ។
""", r"""
ចំនួនទាំងបីនេះនៅលើអ័ក្សមួយក្នុងចំណោមអ័ក្សទាំងពីរ ដូច្នេះមិនចាំបាច់គណនាច្រើនទេ ។
• $z_{1}=-5$ នៅលើអ័ក្សពិតខាងអវិជ្ជមាន ៖ $|z_{1}|=5$ និងអាគុយម៉ង់គឺ $\pi+2k\pi$ ។
• $z_{2}=3i$ នៅលើអ័ក្សនិមិត្តខាងលើ ៖ $|z_{2}|=3$ និងអាគុយម៉ង់គឺ $\frac{\pi}{2}+2k\pi$ ។
• $z_{3}=-2i$ នៅលើអ័ក្សនិមិត្តខាងក្រោម ៖ $|z_{3}|=2$ និងអាគុយម៉ង់គឺ $-\frac{\pi}{2}+2k\pi$ ។
ដូចនេះ $\boxed{z_{1}=5(\cos\pi+i\sin\pi)}$ , $\boxed{z_{2}=3\left(\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}\right)}$ និង $\boxed{z_{3}=2\left(\cos\left(-\frac{\pi}{2}\right)+i\sin\left(-\frac{\pi}{2}\right)\right)}$ ដែល $k\in\mathbb{Z}$ ។
""", r"|z_{1}|=5,\ |z_{2}|=3,\ |z_{3}|=2", [("arg(-5)", "pi", "arg"), ("arg(3*I)", "pi/2", "arg"), ("arg(-2*I)", "-pi/2", "arg"), ("Abs(-2*I)", "2", "mod")])

row("spot_the_error_argument", "medium", r"""
សិស្សម្នាក់សរសេរថា $-1-i=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$ ព្រោះ $\tan\alpha=\frac{-1}{-1}=1$ ។ តើគាត់ខុសត្រង់ណា ? សរសេរចម្លើយដែលត្រឹមត្រូវ ។
""", r"""
ម៉ូឌុល $\sqrt{2}$ ត្រឹមត្រូវ ។ ចំណុចខុសគឺការកំណត់មុំដោយប្រើតែ $\tan\alpha$ ព្រោះមុំពីរខុសគ្នា $\pi$ មានតង់សង់ដូចគ្នា ។
ត្រូវគណនាទាំងកូស៊ីនុស និងស៊ីនុស ៖
$$\cos\alpha=\frac{-1}{\sqrt{2}}=-\frac{\sqrt{2}}{2},\quad \sin\alpha=\frac{-1}{\sqrt{2}}=-\frac{\sqrt{2}}{2}$$
ទាំងពីរអវិជ្ជមាន ដូច្នេះមុំនៅកាដ្រង់ទីបី មិនមែនទីមួយទេ ។ យើងបាន $\alpha=-\frac{3\pi}{4}+2k\pi$ ។
ដូចនេះ $\boxed{-1-i=\sqrt{2}\left[\cos\left(-\frac{3\pi}{4}\right)+i\sin\left(-\frac{3\pi}{4}\right)\right]}$ ។
""", r"-1-i=\sqrt{2}\left[\cos\left(-\frac{3\pi}{4}\right)+i\sin\left(-\frac{3\pi}{4}\right)\right]", [("arg(-1-I)", "-3*pi/4", "arg"), ("Abs(-1-I)", "sqrt(2)", "mod")])

row("spot_the_error_argument", "medium", r"""
ពិនិត្យសមភាព $1-i\sqrt{3}=2\left(\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}\right)$ ។ តើវាត្រឹមត្រូវឬទេ ? បើមិនត្រឹមត្រូវ សូមកែ ។
""", r"""
គណនាអង្គខាងស្ដាំ ៖
$$2\left(\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}\right)=2\left(-\frac{1}{2}+i\frac{\sqrt{3}}{2}\right)=-1+i\sqrt{3}$$
លទ្ធផលនេះជាចំនួនផ្ទុយនៃ $1-i\sqrt{3}$ ដូច្នេះសមភាពមិនត្រឹមត្រូវទេ ។
ចំពោះ $1-i\sqrt{3}$ យើងមាន $|z|=2$ , $\cos\alpha=\frac{1}{2}$ និង $\sin\alpha=-\frac{\sqrt{3}}{2}$ នាំឱ្យ $\alpha=-\frac{\pi}{3}+2k\pi$ ។
ដូចនេះ $\boxed{1-i\sqrt{3}=2\left[\cos\left(-\frac{\pi}{3}\right)+i\sin\left(-\frac{\pi}{3}\right)\right]}$ ។
""", r"1-i\sqrt{3}=2\left[\cos\left(-\frac{\pi}{3}\right)+i\sin\left(-\frac{\pi}{3}\right)\right]", [("arg(1-I*sqrt(3))", "-pi/3", "arg"), ("2*(cos(2*pi/3)+I*sin(2*pi/3))", "-1+I*sqrt(3)", "right side")])

row("proof_product_formula", "medium", r"""
ស្រាយបញ្ជាក់ថា $(\cos a+i\sin a)(\cos b+i\sin b)=\cos(a+b)+i\sin(a+b)$ ។
""", r"""
ពន្លាតអង្គខាងឆ្វេង ហើយប្រើ $i^{2}=-1$ ៖
$$(\cos a+i\sin a)(\cos b+i\sin b)=\cos a\cos b-\sin a\sin b+i(\sin a\cos b+\cos a\sin b)$$
តាមរូបមន្តផលបូកមុំ $\cos a\cos b-\sin a\sin b=\cos(a+b)$ និង $\sin a\cos b+\cos a\sin b=\sin(a+b)$ ។
ដូចនេះ $\boxed{(\cos a+i\sin a)(\cos b+i\sin b)=\cos(a+b)+i\sin(a+b)}$ ។
""", r"\cos(a+b)+i\sin(a+b)", [("cos(x)*cos(pi/3)-sin(x)*sin(pi/3)", "cos(x+pi/3)", "real part, b=pi/3"), ("sin(x)*cos(pi/3)+cos(x)*sin(pi/3)", "sin(x+pi/3)", "imaginary part, b=pi/3")])

row("proof_quotient_formula", "medium", r"""
គេឱ្យ $z_{1}=r_{1}(\cos\alpha_{1}+i\sin\alpha_{1})$ និង $z_{2}=r_{2}(\cos\alpha_{2}+i\sin\alpha_{2})$ ដែល $r_{1},r_{2}>0$ ។ ស្រាយបញ្ជាក់រូបមន្តផលចែក $\frac{z_{1}}{z_{2}}=\frac{r_{1}}{r_{2}}\left[\cos(\alpha_{1}-\alpha_{2})+i\sin(\alpha_{1}-\alpha_{2})\right]$ ។
""", r"""
គុណភាគយក និងភាគបែងនឹងចំនួនឆ្លាស់នៃ $\cos\alpha_{2}+i\sin\alpha_{2}$ ។ ភាគបែងក្លាយជា $\cos^{2}\alpha_{2}+\sin^{2}\alpha_{2}=1$ ។ យើងបាន
$$\frac{z_{1}}{z_{2}}=\frac{r_{1}}{r_{2}}(\cos\alpha_{1}+i\sin\alpha_{1})(\cos\alpha_{2}-i\sin\alpha_{2})$$
ពន្លាត ៖ ផ្នែកពិតគឺ $\cos\alpha_{1}\cos\alpha_{2}+\sin\alpha_{1}\sin\alpha_{2}=\cos(\alpha_{1}-\alpha_{2})$ ហើយផ្នែកនិមិត្តគឺ $\sin\alpha_{1}\cos\alpha_{2}-\cos\alpha_{1}\sin\alpha_{2}=\sin(\alpha_{1}-\alpha_{2})$ ។
ដូចនេះ $\boxed{\frac{z_{1}}{z_{2}}=\frac{r_{1}}{r_{2}}\left[\cos(\alpha_{1}-\alpha_{2})+i\sin(\alpha_{1}-\alpha_{2})\right]}$ ។
""", r"\frac{z_{1}}{z_{2}}=\frac{r_{1}}{r_{2}}\left[\cos(\alpha_{1}-\alpha_{2})+i\sin(\alpha_{1}-\alpha_{2})\right]", [("cos(x)*cos(pi/6)+sin(x)*sin(pi/6)", "cos(x-pi/6)", "real part"), ("sin(x)*cos(pi/6)-cos(x)*sin(pi/6)", "sin(x-pi/6)", "imaginary part")])

row("proof_de_moivre", "hard", r"""
ស្រាយបញ្ជាក់ដោយវិចារកំណើនថា $(\cos\alpha+i\sin\alpha)^{n}=\cos n\alpha+i\sin n\alpha$ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ។
""", r"""
ចំពោះ $n=1$ សមភាពពិតជាក់ស្ដែង ។
ឧបមាថាសមភាពពិតចំពោះ $n=m$ ។ គុណអង្គទាំងពីរនឹង $\cos\alpha+i\sin\alpha$ ៖
$$(\cos\alpha+i\sin\alpha)^{m+1}=(\cos m\alpha+i\sin m\alpha)(\cos\alpha+i\sin\alpha)$$
តាមរូបមន្តផលគុណ អាគុយម៉ង់បូកគ្នា ដូច្នេះអង្គខាងស្ដាំស្មើ $\cos(m+1)\alpha+i\sin(m+1)\alpha$ ។ សមភាពពិតចំពោះ $n=m+1$ ។
ដូចនេះ $\boxed{(\cos\alpha+i\sin\alpha)^{n}=\cos n\alpha+i\sin n\alpha}$ ចំពោះគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ។
""", r"(\cos\alpha+i\sin\alpha)^{n}=\cos n\alpha+i\sin n\alpha", [("expand((cos(pi/6)+I*sin(pi/6))**5)", "cos(5*pi/6)+I*sin(5*pi/6)", "instance n=5")])

row("proof_de_moivre", "hard", r"""
ដោយដឹងថារូបមន្តដឺម័រពិតចំពោះចំនួនគត់វិជ្ជមាន បង្ហាញថាវាពិតដែរចំពោះនិទស្សន្តអវិជ្ជមាន $-n$ ។ រួចគណនា $\left(\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}\right)^{-3}$ ។
""", r"""
យើងមាន
$$(\cos\alpha+i\sin\alpha)^{-n}=\frac{1}{\cos n\alpha+i\sin n\alpha}$$
គុណភាគយក និងភាគបែងនឹង $\cos n\alpha-i\sin n\alpha$ ។ ភាគបែងស្មើ $\cos^{2}n\alpha+\sin^{2}n\alpha=1$ ។ យើងបាន
$$(\cos\alpha+i\sin\alpha)^{-n}=\cos n\alpha-i\sin n\alpha=\cos(-n\alpha)+i\sin(-n\alpha)$$
អនុវត្ត ៖ យក $\alpha=\frac{\pi}{6}$ និង $n=3$ ៖ កន្សោមស្មើ $\cos\left(-\frac{\pi}{2}\right)+i\sin\left(-\frac{\pi}{2}\right)$ ។
ដូចនេះ $\boxed{\left(\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}\right)^{-3}=-i}$ ។
""", r"-i", [("simplify(1/expand((cos(pi/6)+I*sin(pi/6))**3))", "-I", "value")])

row("modulus_of_product_proof", "medium", r"""
ដោយប្រើទម្រង់ត្រីកោណមាត្រ បង្ហាញថា $|z_{1}z_{2}|=|z_{1}|\times|z_{2}|$ ។ អនុវត្តដើម្បីគណនា $\left|\left(3+4i\right)\left(1-i\sqrt{3}\right)\right|$ ។
""", r"""
តាង $z_{1}=r_{1}(\cos\alpha_{1}+i\sin\alpha_{1})$ និង $z_{2}=r_{2}(\cos\alpha_{2}+i\sin\alpha_{2})$ ។ តាមរូបមន្តផលគុណ ៖
$$z_{1}z_{2}=r_{1}r_{2}\left[\cos(\alpha_{1}+\alpha_{2})+i\sin(\alpha_{1}+\alpha_{2})\right]$$
ដោយ $r_{1}r_{2}>0$ វាជាម៉ូឌុលនៃ $z_{1}z_{2}$ ។ ដូច្នេះ $|z_{1}z_{2}|=r_{1}r_{2}=|z_{1}|\times|z_{2}|$ ។
អនុវត្ត ៖ $|3+4i|=\sqrt{9+16}=5$ និង $\left|1-i\sqrt{3}\right|=\sqrt{1+3}=2$ ។
ដូចនេះ $\boxed{\left|\left(3+4i\right)\left(1-i\sqrt{3}\right)\right|=10}$ ។
""", r"10", [("Abs(expand((3+4*I)*(1-I*sqrt(3))))", "10", "modulus")])

row("conjugate_modulus_one", "easy", r"""
គេឱ្យ $z=\cos\theta+i\sin\theta$ ។ បង្ហាញថា $|z|=1$ និង $\frac{1}{z}=\overline{z}$ ។ រួចគណនា $\frac{1}{z}$ ពេល $\theta=\frac{\pi}{3}$ ។
""", r"""
យើងមាន $|z|=\sqrt{\cos^{2}\theta+\sin^{2}\theta}=1$ ។
ម្យ៉ាងទៀត $z\times\overline{z}=|z|^{2}=1$ ដូច្នេះ $\frac{1}{z}=\overline{z}=\cos\theta-i\sin\theta$ ។
ពេល $\theta=\frac{\pi}{3}$ យើងបាន $\frac{1}{z}=\cos\frac{\pi}{3}-i\sin\frac{\pi}{3}$ ។
ដូចនេះ $\boxed{\frac{1}{z}=\frac{1}{2}-i\frac{\sqrt{3}}{2}}$ ។
""", r"\frac{1}{z}=\frac{1}{2}-i\frac{\sqrt{3}}{2}", [("simplify(1/(Rational(1,2)+I*sqrt(3)/2))", "Rational(1,2)-I*sqrt(3)/2", "inverse")])

row("powers_without_trig_form", "easy", r"""
គណនា $(1+i)^{2}$ រួចទាញរកតម្លៃនៃ $(1+i)^{12}$ ដោយមិនប្រើទម្រង់ត្រីកោណមាត្រ ។ ផ្ទៀងផ្ទាត់លទ្ធផលដោយរូបមន្តដឺម័រ ។
""", r"""
$(1+i)^{2}=1+2i+i^{2}=2i$ ។ ដូច្នេះ $(1+i)^{12}=(2i)^{6}=2^{6}i^{6}=64\times(-1)=-64$ ។
ផ្ទៀងផ្ទាត់ ៖ $1+i=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$ ដូច្នេះ
$$(1+i)^{12}=\left(\sqrt{2}\right)^{12}(\cos 3\pi+i\sin 3\pi)=64\times(-1)$$
វិធីទាំងពីរឱ្យលទ្ធផលដូចគ្នា ។
ដូចនេះ $\boxed{(1+i)^{12}=-64}$ ។
""", r"-64", [("expand((1+I)**2)", "2*I", "square"), ("expand((1+I)**12)", "-64", "power")])

row("powers_of_i_de_moivre", "easy", r"""
ដោយសរសេរ $i$ ជាទម្រង់ត្រីកោណមាត្រ គណនា $i^{2026}$ ។
""", r"""
$i=\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}$ ។ តាមរូបមន្តដឺម័រ ៖
$$i^{2026}=\cos 1013\pi+i\sin 1013\pi$$
ដោយ $1013$ ជាចំនួនសេស $\cos 1013\pi=-1$ និង $\sin 1013\pi=0$ ។
ដូចនេះ $\boxed{i^{2026}=-1}$ ។
""", r"-1", [("I**2026", "-1", "power")])

row("product_from_modulus_argument", "easy", r"""
ចំនួនកុំផ្លិច $z_{1}$ មានម៉ូឌុល $2$ និងអាគុយម៉ង់ $\frac{\pi}{3}$ ។ ចំនួនកុំផ្លិច $z_{2}$ មានម៉ូឌុល $3$ និងអាគុយម៉ង់ $\frac{\pi}{6}$ ។ សរសេរ $z_{1}\times z_{2}$ ជាទម្រង់ពីជគណិត ។
""", r"""
គុណម៉ូឌុលនឹងម៉ូឌុល ៖ $2\times 3=6$ ។ បូកអាគុយម៉ង់ ៖ $\frac{\pi}{3}+\frac{\pi}{6}=\frac{\pi}{2}$ ។
$$z_{1}\times z_{2}=6\left(\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}\right)=6(0+i)$$
ដូចនេះ $\boxed{z_{1}\times z_{2}=6i}$ ។
""", r"6i", [("2*(cos(pi/3)+I*sin(pi/3))*3*(cos(pi/6)+I*sin(pi/6))", "6*I", "product")])

row("nonstandard_angle_power", "easy", r"""
គណនាតម្លៃនៃកន្សោម $\left(\cos\frac{\pi}{9}+i\sin\frac{\pi}{9}\right)^{3}$ និង $\left(\cos\frac{\pi}{18}+i\sin\frac{\pi}{18}\right)^{6}$ ។
""", r"""
មុំ $\frac{\pi}{9}$ មិនមែនជាមុំស្គាល់ទេ ប៉ុន្តែរូបមន្តដឺម័របំប្លែងវាទៅជាមុំស្គាល់ ៖
$$\left(\cos\frac{\pi}{9}+i\sin\frac{\pi}{9}\right)^{3}=\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}=\frac{1}{2}+i\frac{\sqrt{3}}{2}$$
ដូចគ្នា $6\times\frac{\pi}{18}=\frac{\pi}{3}$ ដូច្នេះកន្សោមទីពីរក៏ស្មើចំនួននេះដែរ ។
ដូចនេះ លទ្ធផលទាំងពីរគឺ $\boxed{\frac{1}{2}+i\frac{\sqrt{3}}{2}}$ ។
""", r"\frac{1}{2}+i\frac{\sqrt{3}}{2}", [("cos(3*pi/9)+I*sin(3*pi/9)", "Rational(1,2)+I*sqrt(3)/2", "value"), ("cos(6*pi/18)+I*sin(6*pi/18)", "Rational(1,2)+I*sqrt(3)/2", "value")])

row("simplify_trig_quotient", "medium", r"""
សម្រួលកន្សោម $E=\frac{(\cos\theta+i\sin\theta)^{5}}{(\cos 2\theta-i\sin 2\theta)^{2}}$ ។
""", r"""
ភាគយកស្មើ $\cos 5\theta+i\sin 5\theta$ តាមរូបមន្តដឺម័រ ។
សម្រាប់ភាគបែង ត្រូវកែជារាងត្រឹមត្រូវសិន ៖ $\cos 2\theta-i\sin 2\theta=\cos(-2\theta)+i\sin(-2\theta)$ ។ លើកជាការេ យើងបាន $\cos(-4\theta)+i\sin(-4\theta)$ ។
ចែកគ្នា គឺដកអាគុយម៉ង់ ៖ $5\theta-(-4\theta)=9\theta$ ។
ដូចនេះ $\boxed{E=\cos 9\theta+i\sin 9\theta}$ ។
""", r"E=\cos 9\theta+i\sin 9\theta", [("(cos(pi/7)+I*sin(pi/7))**5/(cos(2*pi/7)-I*sin(2*pi/7))**2", "cos(9*pi/7)+I*sin(9*pi/7)", "instance theta=pi/7") if False else ("simplify(expand((cos(pi/12)+I*sin(pi/12))**5)/expand((cos(pi/6)-I*sin(pi/6))**2))", "cos(9*pi/12)+I*sin(9*pi/12)", "instance theta=pi/12")])

row("simplify_trig_quotient", "medium", r"""
សរសេរ $P=(\cos\theta+i\sin\theta)^{3}(\sin\theta+i\cos\theta)$ ជាទម្រង់ត្រីកោណមាត្រ ។
""", r"""
កត្តាទីពីរមិនមែនជាទម្រង់ត្រីកោណមាត្រទេ ព្រោះស៊ីនុសនៅមុខ ។ ដោយ $\sin\theta=\cos\left(\frac{\pi}{2}-\theta\right)$ និង $\cos\theta=\sin\left(\frac{\pi}{2}-\theta\right)$ យើងសរសេរ
$$\sin\theta+i\cos\theta=\cos\left(\frac{\pi}{2}-\theta\right)+i\sin\left(\frac{\pi}{2}-\theta\right)$$
កត្តាទីមួយស្មើ $\cos 3\theta+i\sin 3\theta$ ។ បូកអាគុយម៉ង់ ៖ $3\theta+\frac{\pi}{2}-\theta=2\theta+\frac{\pi}{2}$ ។
ដូចនេះ $\boxed{P=\cos\left(2\theta+\frac{\pi}{2}\right)+i\sin\left(2\theta+\frac{\pi}{2}\right)}$ ។
""", r"P=\cos\left(2\theta+\frac{\pi}{2}\right)+i\sin\left(2\theta+\frac{\pi}{2}\right)", [("expand((cos(pi/6)+I*sin(pi/6))**3*(sin(pi/6)+I*cos(pi/6)))", "cos(2*pi/6+pi/2)+I*sin(2*pi/6+pi/2)", "instance theta=pi/6")])

row("z_plus_inverse", "hard", r"""
ចំនួនកុំផ្លិច $z$ ផ្ទៀងផ្ទាត់ $z+\frac{1}{z}=\sqrt{3}$ ។ រក $z$ ជាទម្រង់ត្រីកោណមាត្រ រួចគណនា $z^{6}+\frac{1}{z^{6}}$ ។
""", r"""
គុណនឹង $z\neq0$ ៖ $z^{2}-\sqrt{3}z+1=0$ ។ ឌីសគ្រីមីណង់ $\Delta=3-4=-1=i^{2}$ ។ ឫសគឺ
$$z=\frac{\sqrt{3}\pm i}{2}=\cos\frac{\pi}{6}\pm i\sin\frac{\pi}{6}$$
ករណីទាំងពីរ តាមរូបមន្តដឺម័រ $z^{6}=\cos\pi\pm i\sin\pi=-1$ ។ ដូច្នេះ $\frac{1}{z^{6}}=-1$ ផងដែរ ។
ដូចនេះ $\boxed{z^{6}+\frac{1}{z^{6}}=-2}$ ។
""", r"-2", [("expand((sqrt(3)/2+I/2)**2-sqrt(3)*(sqrt(3)/2+I/2)+1)", "0", "root"), ("expand((sqrt(3)/2+I/2)**6)", "-1", "sixth power")])

row("z_plus_inverse", "hard", r"""
គេដឹងថា $z+\frac{1}{z}=1$ ។ គណនា $z^{2025}+\frac{1}{z^{2025}}$ ។
""", r"""
ទម្រង់ដែលសមីការនេះមាន ៖ $z^{2}-z+1=0$ មាន $\Delta=-3=\left(i\sqrt{3}\right)^{2}$ ។ ឫសគឺ $z=\frac{1\pm i\sqrt{3}}{2}=\cos\frac{\pi}{3}\pm i\sin\frac{\pi}{3}$ ។
តាមរូបមន្តដឺម័រ $z^{n}+\frac{1}{z^{n}}=2\cos\frac{n\pi}{3}$ ចំពោះឫសទាំងពីរ ។
យក $n=2025=3\times 675$ ៖ $2\cos 675\pi=2\times(-1)$ ព្រោះ $675$ សេស ។
ដូចនេះ $\boxed{z^{2025}+\frac{1}{z^{2025}}=-2}$ ។
""", r"-2", [("2*cos(2025*pi/3)", "-2", "value"), ("expand((Rational(1,2)+I*sqrt(3)/2)**2-(Rational(1,2)+I*sqrt(3)/2)+1)", "0", "root")])

row("z_plus_inverse", "medium", r"""
ឱ្យ $z$ ជាចំនួនកុំផ្លិច ដែល $z+\frac{1}{z}=-\sqrt{2}$ ។ បង្ហាញថា $z^{8}=1$ ។
""", r"""
សមីការសមមូលនឹង $z^{2}+\sqrt{2}z+1=0$ ។ យើងមាន $\Delta=2-4=-2=\left(i\sqrt{2}\right)^{2}$ ។ ឫសគឺ
$$z=\frac{-\sqrt{2}\pm i\sqrt{2}}{2}=\cos\frac{3\pi}{4}\pm i\sin\frac{3\pi}{4}$$
តាមរូបមន្តដឺម័រ $z^{8}=\cos 6\pi\pm i\sin 6\pi$ ។
ដូចនេះ $\boxed{z^{8}=1}$ ។
""", r"z^{8}=1", [("expand((-sqrt(2)/2+I*sqrt(2)/2)**8)", "1", "eighth power"), ("expand((-sqrt(2)/2+I*sqrt(2)/2)**2+sqrt(2)*(-sqrt(2)/2+I*sqrt(2)/2)+1)", "0", "root")])

row("textbook_sum_product_of_cube_roots", "medium", r"""
រកឫសទីបីនៃ $8$ រួចផ្ទៀងផ្ទាត់ថា ផលបូករបស់ពួកវាស្មើ $0$ និងផលគុណស្មើ $8$ ។
""", r"""
សរសេរ $8=8(\cos 0+i\sin 0)$ ។ ឫសទីបីមានម៉ូឌុល $2$ និងអាគុយម៉ង់ $\frac{2k\pi}{3}$ ៖
$$z_{0}=2,\quad z_{1}=2\left(\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}\right)=-1+i\sqrt{3},\quad z_{2}=-1-i\sqrt{3}$$
ផលបូក ៖ $2+\left(-1+i\sqrt{3}\right)+\left(-1-i\sqrt{3}\right)=0$ ។
ផលគុណ ៖ $2\times(1+3)=8$ ។
ដូចនេះ ផលបូកស្មើ $\boxed{0}$ ហើយផលគុណស្មើ $\boxed{8}$ ។
""", r"z_{0}=2,\ z_{1}=-1+i\sqrt{3},\ z_{2}=-1-i\sqrt{3}", [("expand((-1+I*sqrt(3))**3)", "8", "root"), ("expand(2*(-1+I*sqrt(3))*(-1-I*sqrt(3)))", "8", "product")])

row("textbook_square_root_two_methods", "medium", r"""
រកឫសការេនៃ $i$ តាមពីរវិធី ៖ ទម្រង់ត្រីកោណមាត្រ និងទម្រង់ពីជគណិត ។
""", r"""
វិធីទី១ ៖ $i=\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}$ ។ ឫសការេមានម៉ូឌុល $1$ និងអាគុយម៉ង់ $\frac{\pi}{4}+k\pi$ ។ យើងបាន $\frac{\sqrt{2}}{2}+i\frac{\sqrt{2}}{2}$ និងចំនួនផ្ទុយរបស់វា ។
វិធីទី២ ៖ តាង $(x+iy)^{2}=i$ ។ យើងបាន $x^{2}-y^{2}=0$ និង $2xy=1$ ។ សមីការទីមួយឱ្យ $x=y$ ឬ $x=-y$ ។ ដោយ $xy>0$ ត្រូវយក $x=y$ ហើយ $x^{2}=\frac{1}{2}$ ។
ដូចនេះ ឫសការេនៃ $i$ គឺ $\boxed{\pm\frac{\sqrt{2}}{2}(1+i)}$ ។
""", r"\pm\frac{\sqrt{2}}{2}(1+i)", [("expand((sqrt(2)/2*(1+I))**2)", "I", "square root")])

row("textbook_square_root_two_methods", "medium", r"""
ដោះស្រាយសមីការ $z^{2}=-8i$ ។
""", r"""
ទម្រង់ត្រីកោណមាត្រនៃ $-8i$ គឺ $8\left[\cos\left(-\frac{\pi}{2}\right)+i\sin\left(-\frac{\pi}{2}\right)\right]$ ។
តាង $z=\rho(\cos\beta+i\sin\beta)$ ។ យើងបាន $\rho^{2}=8$ និង $2\beta=-\frac{\pi}{2}+2k\pi$ ។ ដូច្នេះ $\rho=2\sqrt{2}$ និង $\beta=-\frac{\pi}{4}+k\pi$ ។
ពេល $k=0$ ៖ $z=2\sqrt{2}\left(\frac{\sqrt{2}}{2}-i\frac{\sqrt{2}}{2}\right)=2-2i$ ។
ពេល $k=1$ ៖ $\beta=\frac{3\pi}{4}$ និង $z=-2+2i$ ។
ដូចនេះ សមីការមានឫស $\boxed{z=2-2i}$ និង $\boxed{z=-2+2i}$ ។
""", r"z=\pm(2-2i)", [("expand((2-2*I)**2)", "-8*I", "root"), ("expand((-2+2*I)**2)", "-8*I", "root")])

row("textbook_cube_roots_minus_one", "medium", r"""
ដោះស្រាយសមីការ $z^{3}+1=0$ ដោយដាក់ជាកត្តា រួចផ្ទៀងផ្ទាត់តាមទម្រង់ត្រីកោណមាត្រ ។
""", r"""
ដាក់ជាកត្តា ៖ $z^{3}+1=(z+1)\left(z^{2}-z+1\right)$ ។ កត្តាទីពីរមាន $\Delta=-3=\left(i\sqrt{3}\right)^{2}$ ។ ឫសគឺ $-1$ និង $\frac{1\pm i\sqrt{3}}{2}$ ។
តាមទម្រង់ត្រីកោណមាត្រ ៖ $-1=\cos\pi+i\sin\pi$ ដូច្នេះឫសមានម៉ូឌុល $1$ និងអាគុយម៉ង់ $\frac{\pi}{3}+\frac{2k\pi}{3}$ គឺ $\frac{\pi}{3}$ , $\pi$ , $\frac{5\pi}{3}$ ។
មុំ $\frac{\pi}{3}$ ឱ្យ $\frac{1}{2}+i\frac{\sqrt{3}}{2}$ មុំ $\pi$ ឱ្យ $-1$ ហើយមុំ $\frac{5\pi}{3}$ ឱ្យ $\frac{1}{2}-i\frac{\sqrt{3}}{2}$ ។ លទ្ធផលត្រូវគ្នា ។
ដូចនេះ សំណុំឫសគឺ $\boxed{\left\{-1,\ \frac{1}{2}+i\frac{\sqrt{3}}{2},\ \frac{1}{2}-i\frac{\sqrt{3}}{2}\right\}}$ ។
""", r"\left\{-1,\ \frac{1}{2}\pm i\frac{\sqrt{3}}{2}\right\}", [("expand((Rational(1,2)+I*sqrt(3)/2)**3)", "-1", "root"), ("expand((Rational(1,2)-I*sqrt(3)/2)**3)", "-1", "root")])

row("textbook_fourth_roots_and_factorisation", "hard", r"""
ដោះស្រាយសមីការ $z^{4}+1=0$ រួចទាញបង្ហាញថា $x^{4}+1=\left(x^{2}-\sqrt{2}x+1\right)\left(x^{2}+\sqrt{2}x+1\right)$ ។
""", r"""
$-1=\cos\pi+i\sin\pi$ ។ ឫសទីបួនមានម៉ូឌុល $1$ និងអាគុយម៉ង់ $\frac{\pi}{4}+\frac{k\pi}{2}$ ។ យើងបាន
$$z=\frac{\sqrt{2}}{2}\pm i\frac{\sqrt{2}}{2},\quad z=-\frac{\sqrt{2}}{2}\pm i\frac{\sqrt{2}}{2}$$
ផ្គុំឫសឆ្លាស់គ្នាជាគូ ។ គូទីមួយមានផលបូក $\sqrt{2}$ និងផលគុណ $1$ ដូច្នេះវាជាឫសនៃ $x^{2}-\sqrt{2}x+1$ ។ គូទីពីរមានផលបូក $-\sqrt{2}$ និងផលគុណ $1$ ដូច្នេះវាជាឫសនៃ $x^{2}+\sqrt{2}x+1$ ។
ដូចនេះ $\boxed{x^{4}+1=\left(x^{2}-\sqrt{2}x+1\right)\left(x^{2}+\sqrt{2}x+1\right)}$ ។
""", r"x^{4}+1=\left(x^{2}-\sqrt{2}x+1\right)\left(x^{2}+\sqrt{2}x+1\right)", [("expand((x**2-sqrt(2)*x+1)*(x**2+sqrt(2)*x+1))", "x**4+1", "factorisation"), ("expand((sqrt(2)/2+I*sqrt(2)/2)**4)", "-1", "root")])

row("modulus_of_root_of_unity", "medium", r"""
បង្ហាញថា បើ $z^{n}=1$ ដែល $n$ ជាចំនួនគត់វិជ្ជមាន នោះ $|z|=1$ ។ តើចំនួន $\frac{3}{5}+\frac{4}{5}i$ ដែលមានម៉ូឌុល $1$ ត្រូវតែជាឫសទី $n$ នៃ $1$ ឬទេ ?
""", r"""
យកម៉ូឌុលនៃអង្គទាំងពីរ ៖ $|z|^{n}=1$ ។ ដោយ $|z|$ ជាចំនួនពិតមិនអវិជ្ជមាន យើងបាន $|z|=1$ ។
ចំពោះសំណួរទីពីរ យើងមាន $\left|\frac{3}{5}+\frac{4}{5}i\right|=\sqrt{\frac{9}{25}+\frac{16}{25}}=1$ ។ ប៉ុន្តែការពិតបញ្ច្រាសមិនចាំបាច់ត្រូវទេ ៖ លក្ខខណ្ឌ $|z|=1$ មិនគ្រប់គ្រាន់ ហើយ $z^{n}=1$ ទាមទារថាអាគុយម៉ង់ជាពហុគុណសនិទាននៃ $\pi$ ។
ឧទាហរណ៍ $\left(\frac{3}{5}+\frac{4}{5}i\right)^{2}=-\frac{7}{25}+\frac{24}{25}i$ មិនមែន $1$ ទេ ។
ដូចនេះ $\boxed{|z|=1}$ ជាលក្ខខណ្ឌចាំបាច់ តែមិនគ្រប់គ្រាន់ទេ ។
""", r"|z|=1", [("Abs(Rational(3,5)+I*Rational(4,5))", "1", "modulus"), ("expand((Rational(3,5)+I*Rational(4,5))**2)", "-Rational(7,25)+I*Rational(24,25)", "square")])

row("pure_imaginary_quotient_modulus_one", "hard", r"""
គេឱ្យ $z=\cos\theta+i\sin\theta$ ដែល $-\pi<\theta<\pi$ ។ បង្ហាញថា $\frac{z-1}{z+1}$ ជាចំនួននិមិត្ត ។ គណនាវាពេល $\theta=\frac{\pi}{2}$ ។
""", r"""
គុណភាគយក និងភាគបែងនឹង $\overline{z}+1$ ។ ដោយ $z\overline{z}=1$ ៖
$$\frac{z-1}{z+1}=\frac{(z-1)\left(\overline{z}+1\right)}{|z+1|^{2}}=\frac{1+z-\overline{z}-1}{|z+1|^{2}}=\frac{z-\overline{z}}{|z+1|^{2}}$$
ភាគយកគឺ $2i\sin\theta$ ហើយភាគបែងជាចំនួនពិតវិជ្ជមាន ។ ដូច្នេះផលចែកជាចំនួននិមិត្ត ។
ពេល $\theta=\frac{\pi}{2}$ យើងមាន $z=i$ និង $|z+1|^{2}=2$ ។ ផលចែកស្មើ $\frac{2i}{2}$ ។
ដូចនេះ $\boxed{\frac{z-1}{z+1}=i}$ ពេល $\theta=\frac{\pi}{2}$ ។
""", r"i", [("simplify((I-1)/(I+1))", "I", "instance"), ("re(simplify((Rational(1,2)+I*sqrt(3)/2-1)/(Rational(1,2)+I*sqrt(3)/2+1)))", "0", "instance theta=pi/3")])

row("perpendicular_from_quotient", "medium", r"""
គេឱ្យចំណុច $A$ និង $B$ ជារូបភាពនៃ $z_{1}=2+i$ និង $z_{2}=-1+2i$ ។ គណនា $\frac{z_{2}}{z_{1}}$ រួចបង្ហាញថា $OA$ កែងនឹង $OB$ ។
""", r"""
គុណភាគយក និងភាគបែងនឹង $2-i$ ៖
$$\frac{z_{2}}{z_{1}}=\frac{(-1+2i)(2-i)}{(2+i)(2-i)}=\frac{-2+i+4i-2i^{2}}{5}=\frac{5i}{5}=i$$
ដោយ $i=\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}$ មុំពី $\overrightarrow{OA}$ ទៅ $\overrightarrow{OB}$ ស្មើ $\frac{\pi}{2}$ ។ ម៉ូឌុលនៃផលចែកស្មើ $1$ ដូច្នេះ $OA=OB$ ដែរ ។
ដូចនេះ $\boxed{\frac{z_{2}}{z_{1}}=i}$ ហើយ $OA$ កែងនឹង $OB$ ។
""", r"\frac{z_{2}}{z_{1}}=i", [("simplify((-1+2*I)/(2+I))", "I", "quotient")],
fig=dict(points=[("A", 2, 1), ("B", -1, 2), ("O", 0, 0)], circle=None, poly=True, alt="ត្រីកោណកែង OAB ក្នុងប្លង់កុំផ្លិច"))

row("collinear_from_quotient", "medium", r"""
គេឱ្យ $z_{1}=1+i\sqrt{3}$ និង $z_{2}=-2-2i\sqrt{3}$ ។ តើចំណុច $O$ , $A(z_{1})$ និង $B(z_{2})$ នៅលើបន្ទាត់តែមួយឬទេ ?
""", r"""
ពិនិត្យផលចែក ៖ $z_{2}=-2\left(1+i\sqrt{3}\right)=-2z_{1}$ ដូច្នេះ $\frac{z_{2}}{z_{1}}=-2$ ជាចំនួនពិត ។
អាគុយម៉ង់នៃផលចែកគឺ $\pi$ ដូច្នេះ $\overrightarrow{OB}=-2\overrightarrow{OA}$ ហើយវ៉ិចទ័រទាំងពីរកូលីនេអ៊ែរ ។
ដូចនេះ ចំណុច $O$ , $A$ និង $B$ នៅលើបន្ទាត់តែមួយ ដោយ $\boxed{\frac{z_{2}}{z_{1}}=-2}$ ។
""", r"\frac{z_{2}}{z_{1}}=-2", [("simplify((-2-2*I*sqrt(3))/(1+I*sqrt(3)))", "-2", "quotient")])

row("equal_powers_condition", "medium", r"""
រកគ្រប់ចំនួនគត់វិជ្ជមាន $n$ ដែល $(1+i)^{n}=(1-i)^{n}$ ។
""", r"""
ដោយ $1-i\neq0$ សមីការសមមូលនឹង $\left(\frac{1+i}{1-i}\right)^{n}=1$ ។
គណនា ៖ $\frac{1+i}{1-i}=\frac{(1+i)^{2}}{2}=\frac{2i}{2}=i$ ។ សមីការក្លាយជា $i^{n}=1$ ។
ដោយ $i=\cos\frac{\pi}{2}+i\sin\frac{\pi}{2}$ យើងបាន $\cos\frac{n\pi}{2}+i\sin\frac{n\pi}{2}=1$ លុះត្រាតែ $\frac{n\pi}{2}=2k\pi$ គឺ $n=4k$ ។
ដូចនេះ $\boxed{n=4k}$ ដែល $k$ ជាចំនួនគត់វិជ្ជមាន ។
""", r"n=4k", [("simplify((1+I)/(1-I))", "I", "quotient"), ("expand((1+I)**4-(1-I)**4)", "0", "n=4"), ("expand((1+I)**2-(1-I)**2)", "4*I", "n=2 fails")])

row("cube_shortcut_large_power", "medium", r"""
បង្ហាញថា $\left(-1+i\sqrt{3}\right)^{3}=8$ រួចគណនា $\left(-1+i\sqrt{3}\right)^{15}+\left(-1-i\sqrt{3}\right)^{15}$ ។
""", r"""
$-1+i\sqrt{3}=2\left(\cos\frac{2\pi}{3}+i\sin\frac{2\pi}{3}\right)$ ។ តាមរូបមន្តដឺម័រ $\left(-1+i\sqrt{3}\right)^{3}=8(\cos 2\pi+i\sin 2\pi)=8$ ។
យកចំនួនកុំផ្លិចឆ្លាស់នៃសមភាពនេះ ៖ $\left(-1-i\sqrt{3}\right)^{3}=8$ ដែរ ។
ដោយ $15=3\times 5$ ស្វ័យគុណទាំងពីរស្មើ $8^{5}=32768$ ។
ដូចនេះ ផលបូកស្មើ $\boxed{65536}$ ។
""", r"65536", [("expand((-1+I*sqrt(3))**3)", "8", "cube"), ("expand((-1+I*sqrt(3))**15+(-1-I*sqrt(3))**15)", "65536", "sum")])

row("multiple_angle_quintuple", "hard", r"""
គេដឹងថា $\cos 5\theta=16\cos^{5}\theta-20\cos^{3}\theta+5\cos\theta$ ជាលទ្ធផលនៃរូបមន្តដឺម័រ ។ ដោយយក $\theta=\frac{\pi}{10}$ រកតម្លៃនៃ $\cos^{2}\frac{\pi}{10}$ ។
""", r"""
ពេល $\theta=\frac{\pi}{10}$ យើងមាន $\cos 5\theta=\cos\frac{\pi}{2}=0$ ។ តាង $c=\cos\frac{\pi}{10}\neq0$ ។ ចែកនឹង $c$ ៖
$$16c^{4}-20c^{2}+5=0$$
ជាសមីការដឺក្រេទីពីរនៃ $c^{2}$ ។ ឫសគឺ
$$c^{2}=\frac{20\pm\sqrt{400-320}}{32}=\frac{5\pm\sqrt{5}}{8}$$
ដោយ $0<\frac{\pi}{10}<\frac{\pi}{6}$ នោះ $c>\frac{\sqrt{3}}{2}$ ហើយ $c^{2}>\frac{3}{4}$ ។ តម្លៃ $\frac{5-\sqrt{5}}{8}$ តូចជាង $\frac{3}{4}$ ដូច្នេះត្រូវយកឫសធំ ។
ដូចនេះ $\boxed{\cos^{2}\frac{\pi}{10}=\frac{5+\sqrt{5}}{8}}$ ។
""", r"\cos^{2}\frac{\pi}{10}=\frac{5+\sqrt{5}}{8}", [("cos(pi/10)**2", "(5+sqrt(5))/8", "value"), ("cos(5*x)", "16*cos(x)**5-20*cos(x)**3+5*cos(x)", "identity")])

row("multiple_angle_in_one_function", "medium", r"""
ដោយប្រើរូបមន្តដឺម័រ សរសេរ $\cos 4\theta$ ជាអនុគមន៍នៃ $\cos\theta$ តែមួយគត់ ។
""", r"""
យកផ្នែកពិតនៃ $(\cos\theta+i\sin\theta)^{4}$ ៖
$$\cos 4\theta=\cos^{4}\theta-6\cos^{2}\theta\sin^{2}\theta+\sin^{4}\theta$$
តាង $c=\cos\theta$ ហើយជំនួស $\sin^{2}\theta=1-c^{2}$ ៖
$$\cos 4\theta=c^{4}-6c^{2}\left(1-c^{2}\right)+\left(1-c^{2}\right)^{2}=c^{4}-6c^{2}+6c^{4}+1-2c^{2}+c^{4}$$
បូកតួដូចគ្នា ។
ដូចនេះ $\boxed{\cos 4\theta=8\cos^{4}\theta-8\cos^{2}\theta+1}$ ។
""", r"\cos 4\theta=8\cos^{4}\theta-8\cos^{2}\theta+1", [("cos(4*x)", "8*cos(x)**4-8*cos(x)**2+1", "identity")])

row("multiple_angle_in_one_function", "medium", r"""
បង្ហាញថា $\frac{\sin 4\theta}{\sin\theta}=8\cos^{3}\theta-4\cos\theta$ ចំពោះ $\sin\theta\neq0$ ។
""", r"""
យកផ្នែកនិមិត្តនៃ $(\cos\theta+i\sin\theta)^{4}$ ៖
$$\sin 4\theta=4\cos^{3}\theta\sin\theta-4\cos\theta\sin^{3}\theta$$
ចែកនឹង $\sin\theta\neq0$ រួចជំនួស $\sin^{2}\theta=1-\cos^{2}\theta$ ៖
$$\frac{\sin 4\theta}{\sin\theta}=4\cos^{3}\theta-4\cos\theta\left(1-\cos^{2}\theta\right)$$
ដូចនេះ $\boxed{\frac{\sin 4\theta}{\sin\theta}=8\cos^{3}\theta-4\cos\theta}$ ។
""", r"\frac{\sin 4\theta}{\sin\theta}=8\cos^{3}\theta-4\cos\theta", [("sin(4*x)/sin(x)", "8*cos(x)**3-4*cos(x)", "identity")])

row("maximum_via_modulus", "medium", r"""
ដោយសរសេរ $\sqrt{3}+i$ ជាទម្រង់ត្រីកោណមាត្រ រកតម្លៃអតិបរមា និងអប្បបរមានៃ $f(x)=\sqrt{3}\cos x+\sin x$ ។
""", r"""
យើងមាន $\sqrt{3}+i=2\left(\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}\right)$ ។ ដូច្នេះ $\sqrt{3}=2\cos\frac{\pi}{6}$ និង $1=2\sin\frac{\pi}{6}$ ។ ជំនួស ៖
$$f(x)=2\left(\cos\frac{\pi}{6}\cos x+\sin\frac{\pi}{6}\sin x\right)=2\cos\left(x-\frac{\pi}{6}\right)$$
ដោយ $-1\le\cos\left(x-\frac{\pi}{6}\right)\le1$ យើងបាន $-2\le f(x)\le2$ ។ តម្លៃ $2$ កើតឡើងត្រង់ $x=\frac{\pi}{6}$ ហើយតម្លៃ $-2$ កើតឡើងត្រង់ $x=\frac{7\pi}{6}$ ។
ដូចនេះ តម្លៃអតិបរមាគឺ $\boxed{2}$ និងតម្លៃអប្បបរមាគឺ $\boxed{-2}$ ។
""", r"\max f=2,\ \min f=-2", [("sqrt(3)*cos(x)+sin(x)", "2*cos(x-pi/6)", "identity"), ("sqrt(3)*cos(pi/6)+sin(pi/6)", "2", "max"), ("sqrt(3)*cos(7*pi/6)+sin(7*pi/6)", "-2", "min")])

row("tangent_power_identity", "medium", r"""
សរសេរ $\frac{1+i\tan\frac{\pi}{6}}{1-i\tan\frac{\pi}{6}}$ ជាទម្រង់ពីជគណិត ។
""", r"""
ដោយ $\tan\frac{\pi}{6}=\frac{\sqrt{3}}{3}$ យើងគុណភាគយក និងភាគបែងនឹង $\cos\frac{\pi}{6}$ ៖
$$\frac{\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}}{\cos\frac{\pi}{6}-i\sin\frac{\pi}{6}}=\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}$$
ព្រោះភាគបែងមានអាគុយម៉ង់ $-\frac{\pi}{6}$ ហើយការចែកដកអាគុយម៉ង់ ។
ដូចនេះ លទ្ធផលគឺ $\boxed{\frac{1}{2}+i\frac{\sqrt{3}}{2}}$ ។
""", r"\frac{1}{2}+i\frac{\sqrt{3}}{2}", [("simplify((1+I*sqrt(3)/3)/(1-I*sqrt(3)/3))", "Rational(1,2)+I*sqrt(3)/2", "value")])

row("high_power_of_simple_quotient", "easy", r"""
គណនាតម្លៃនៃកន្សោម $\left(\frac{1+i}{1-i}\right)^{2026}$ ។
""", r"""
សម្រួលកន្សោមក្នុងវង់ក្រចកសិន ៖ $\frac{1+i}{1-i}=\frac{(1+i)^{2}}{(1-i)(1+i)}=\frac{2i}{2}=i$ ។
ដូច្នេះកន្សោមស្មើ $i^{2026}$ ។ ដោយ $2026=4\times 506+2$ យើងបាន $i^{2026}=i^{2}$ ។
ដូចនេះ លទ្ធផលគឺ $\boxed{-1}$ ។
""", r"-1", [("simplify((1+I)/(1-I))", "I", "quotient"), ("I**2026", "-1", "power")])

row("trigonometric_form_general_angle", "medium", r"""
គេឱ្យ $0<\theta<\frac{\pi}{2}$ ។ សរសេរ $z=\sin\theta-i\cos\theta$ និង $w=-\cos\theta-i\sin\theta$ ជាទម្រង់ត្រីកោណមាត្រ ។
""", r"""
ចំនួនទាំងពីរមានម៉ូឌុល $1$ ព្រោះ $\sin^{2}\theta+\cos^{2}\theta=1$ ។
សម្រាប់ $z$ យើងប្រើ $\sin\theta=\cos\left(\theta-\frac{\pi}{2}\right)$ និង $-\cos\theta=\sin\left(\theta-\frac{\pi}{2}\right)$ ៖
$$z=\cos\left(\theta-\frac{\pi}{2}\right)+i\sin\left(\theta-\frac{\pi}{2}\right)$$
សម្រាប់ $w$ យើងមាន $w=-(\cos\theta+i\sin\theta)$ ។ គុណនឹង $-1=\cos\pi+i\sin\pi$ គឺបូកអាគុយម៉ង់នឹង $\pi$ ។ ដើម្បីឱ្យមុំនៅក្នុង $(-\pi,\pi]$ យើងដក $2\pi$ ៖
$$w=\cos(\theta-\pi)+i\sin(\theta-\pi)$$
ដូចនេះ $\boxed{z=\cos\left(\theta-\frac{\pi}{2}\right)+i\sin\left(\theta-\frac{\pi}{2}\right)}$ និង $\boxed{w=\cos(\theta-\pi)+i\sin(\theta-\pi)}$ ។
""", r"z=\cos\left(\theta-\frac{\pi}{2}\right)+i\sin\left(\theta-\frac{\pi}{2}\right),\ w=\cos(\theta-\pi)+i\sin(\theta-\pi)",
[("sin(x)", "cos(x-pi/2)", "identity"), ("-cos(x)", "sin(x-pi/2)", "identity"), ("-cos(x)", "cos(x-pi)", "identity"), ("-sin(x)", "sin(x-pi)", "identity")])

row("trigonometric_form_general_angle", "hard", r"""
គេឱ្យ $0<\theta<\pi$ ។ សរសេរ $z=\sin\theta+i(1-\cos\theta)$ ជាទម្រង់ត្រីកោណមាត្រ ។
""", r"""
ប្រើរូបមន្តមុំពីរដង $\sin\theta=2\sin\frac{\theta}{2}\cos\frac{\theta}{2}$ និង $1-\cos\theta=2\sin^{2}\frac{\theta}{2}$ ៖
$$z=2\sin\frac{\theta}{2}\cos\frac{\theta}{2}+2i\sin^{2}\frac{\theta}{2}=2\sin\frac{\theta}{2}\left(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2}\right)$$
ដោយ $0<\frac{\theta}{2}<\frac{\pi}{2}$ នោះ $2\sin\frac{\theta}{2}>0$ ។ ដូច្នេះនេះជាទម្រង់ត្រីកោណមាត្រហើយ ។
ដូចនេះ $\boxed{z=2\sin\frac{\theta}{2}\left(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2}\right)}$ មានម៉ូឌុល $2\sin\frac{\theta}{2}$ និងអាគុយម៉ង់ $\frac{\theta}{2}$ ។
""", r"z=2\sin\frac{\theta}{2}\left(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2}\right)",
[("sin(pi/3)+I*(1-cos(pi/3))", "2*sin(pi/6)*(cos(pi/6)+I*sin(pi/6))", "instance theta=pi/3"), ("Abs(sin(pi/3)+I*(1-cos(pi/3)))", "1", "modulus at pi/3")])

row("product_of_three_factors", "medium", r"""
រកម៉ូឌុល និងអាគុយម៉ង់នៃ $Z=(1+i)\left(1+i\sqrt{3}\right)\left(\sqrt{3}+i\right)$ រួចសរសេរ $Z$ ជាទម្រង់ពីជគណិត ។
""", r"""
កត្តាទាំងបីមានទម្រង់ ៖
$$1+i=\sqrt{2}\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right),\ 1+i\sqrt{3}=2\left(\cos\frac{\pi}{3}+i\sin\frac{\pi}{3}\right),\ \sqrt{3}+i=2\left(\cos\frac{\pi}{6}+i\sin\frac{\pi}{6}\right)$$
ម៉ូឌុលនៃ $Z$ គឺ $\sqrt{2}\times 2\times 2=4\sqrt{2}$ ។ អាគុយម៉ង់គឺ $\frac{\pi}{4}+\frac{\pi}{3}+\frac{\pi}{6}=\frac{3\pi}{4}$ ។
$$Z=4\sqrt{2}\left(-\frac{\sqrt{2}}{2}+i\frac{\sqrt{2}}{2}\right)=-4+4i$$
ដូចនេះ $|Z|=4\sqrt{2}$ អាគុយម៉ង់គឺ $\frac{3\pi}{4}+2k\pi,\ k\in\mathbb{Z}$ ហើយ $\boxed{Z=-4+4i}$ ។
""", r"Z=-4+4i", [("expand((1+I)*(1+I*sqrt(3))*(sqrt(3)+I))", "-4+4*I", "Z"), ("arg(-4+4*I)", "3*pi/4", "arg"), ("Abs(-4+4*I)", "4*sqrt(2)", "mod")])

row("equal_values_two_powers", "medium", r"""
ដោយប្រើរូបមន្តដឺម័រ បង្ហាញថា $\left(\sqrt{3}+i\right)^{6}=(1+i)^{12}$ ។
""", r"""
គណនាអង្គនីមួយៗដោយរូបមន្តដឺម័រ ។
$$\left(\sqrt{3}+i\right)^{6}=2^{6}\left(\cos\pi+i\sin\pi\right)=-64$$
$$(1+i)^{12}=\left(\sqrt{2}\right)^{12}\left(\cos 3\pi+i\sin 3\pi\right)=-64$$
ដូចនេះ អង្គទាំងពីរស្មើគ្នា ហើយស្មើ $\boxed{-64}$ ។
""", r"-64", [("expand((sqrt(3)+I)**6)", "-64", "left"), ("expand((1+I)**12)", "-64", "right")])

row("real_part_of_power_formula", "medium", r"""
គេឱ្យ $z=\sqrt{2}+i\sqrt{2}$ ។ រកផ្នែកពិត និងផ្នែកនិមិត្តនៃ $z^{5}$ ដោយមិនពន្លាត ។
""", r"""
$|z|=\sqrt{2+2}=2$ ហើយ $z=2\left(\frac{\sqrt{2}}{2}+i\frac{\sqrt{2}}{2}\right)=2\left(\cos\frac{\pi}{4}+i\sin\frac{\pi}{4}\right)$ ។
តាមរូបមន្តដឺម័រ $z^{5}=32\left(\cos\frac{5\pi}{4}+i\sin\frac{5\pi}{4}\right)$ ។ មុំ $\frac{5\pi}{4}$ នៅកាដ្រង់ទីបី ដូច្នេះកូស៊ីនុស និងស៊ីនុសអវិជ្ជមាន ។
$$z^{5}=32\left(-\frac{\sqrt{2}}{2}-i\frac{\sqrt{2}}{2}\right)=-16\sqrt{2}-16i\sqrt{2}$$
ដូចនេះ ផ្នែកពិតគឺ $\boxed{-16\sqrt{2}}$ និងផ្នែកនិមិត្តគឺ $\boxed{-16\sqrt{2}}$ ។
""", r"-16\sqrt{2},\ -16\sqrt{2}", [("expand((sqrt(2)+I*sqrt(2))**5)", "-16*sqrt(2)-16*I*sqrt(2)", "power")])

row("argument_interval_zero_two_pi", "easy", r"""
រកអាគុយម៉ង់នៃ $z=\sqrt{3}-i$ ក្នុងចន្លោះ $[0,2\pi)$ ។
""", r"""
$|z|=2$ ។ យើងមាន $\cos\alpha=\frac{\sqrt{3}}{2}$ និង $\sin\alpha=-\frac{1}{2}$ ។ មុំនៅកាដ្រង់ទីបួន ដូច្នេះ $\alpha=-\frac{\pi}{6}+2k\pi$ ។
យក $k=1$ ដើម្បីបានមុំក្នុងចន្លោះដែលចង់បាន ៖ $-\frac{\pi}{6}+2\pi=\frac{11\pi}{6}$ ។
ដូចនេះ $\boxed{\alpha=\frac{11\pi}{6}}$ ។
""", r"\alpha=\frac{11\pi}{6}", [("arg(sqrt(3)-I)+2*pi", "11*pi/6", "argument"), ("Abs(sqrt(3)-I)", "2", "mod")])
