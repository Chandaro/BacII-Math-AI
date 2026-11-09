# BacII mathematics: complex numbers, limits and continuity style guide

Companion to `style_guide.md`. Own synthesis for building original Khmer fine-tuning data. No exercise or solution is reproduced. Khmer items are short terms and stock phrases only. Counts describe item types, not item content.

## 0. Evidence

Labels are the same as in `style_guide.md`.

- **[SEEN]**: read on rendered pages of a source.
- **[SNIPPET]**: from a search snippet or a secondary web page; the primary page was not read.
- **[GENERAL]**: general knowledge of the Khmer and French-derived tradition, not confirmed here. Have a Cambodian maths teacher check these.
- **[INFERENCE]** is added where a conclusion is my reasoning from [SEEN] facts rather than something a source states.

Read for this guide, all as rendered page images:

| Source | What was read |
|---|---|
| GitHub `HELMAB/bacii` maths PDFs, science and society, 2014 (two sessions), 2015-2019, 2021, 2022 | Paper pages for most sessions; solution pages for 2014 society, 2021 and 2022 science, 2021 and 2022 society. Repo has no 2020 and nothing after 2022 |
| Kim Sokun, national exam compilations 2007-2017, science stream: `complex-national-exam-pdf.pdf`, `limit-national-exam-pdf.pdf` | All 4 pages |
| Kim Sokun, Grade 12 Basic Level answer book, chapter 1 (limits), 30 pages | Pages 1, 8, 20 only |
| MoEYS textbooks as hosted by math24: Grade 11 Basic, Grade 11 Advanced, Grade 12 Basic, Grade 12 Advanced | Contents pages of all four; Grade 11 Advanced pp. 103-104, 136-137, 145, 147, 175; Grade 11 Basic p. 142; Grade 12 Basic p. 29 |
| SalaDigital item 00007808, author Khem Pothi, 85 pages | Cover, papers 1, 12, 13, 14, 15. **The file served is the social-science volume only** |

Not read: Lim Phalkun books (MediaFire links, not opened); the science-stream papers for 2023-2025; any Kim Sokun Grade 11 complex-number answer book (none located); the High Level limits-of-sequences answer book (downloaded, not read); lessons 2-3 of the complex chapter beyond the pages listed.

Limits of this evidence:

- **No original printed exam was seen.** Every paper is a retyped copy. The `HELMAB` copies say they were extracted by a named compiler (`ដកស្រង់ដោយ`). The SalaDigital copies sit in a compiler's template. Compare section 8 for disagreements between copies.
- The textbook edition may not be the current one. The contents were read from hosted scans whose print years were not legible. **Whether a newer curriculum moved any chapter is unconfirmed.**
- Solutions are teachers' or compilers' model answers, not student scripts.

## 1. Grade and stream placement

Textbook facts below are [SEEN] from the contents pages.

| Sub-topic | Book and place | Grade |
|---|---|---|
| Complex numbers, algebraic form | Advanced, ch. 7, lesson 1 (p. 136) | 11 |
| Complex numbers, trigonometric form | Advanced, ch. 7, lesson 2 (p. 144) | 11 |
| n-th powers and n-th roots | Advanced, ch. 7, lesson 3 (p. 164) | 11 |
| Complex numbers in geometry | Advanced, ch. 7, lesson 4 (p. 174) | 11 |
| Limits and limit rules, first contact | Basic, ch. 5, lesson 1 (p. 140) | 11 |
| Limit of a function | Basic, ch. 1, lesson 1 (p. 2) | 12 |
| Continuity of a function | Basic, ch. 1, lesson 2 (p. 28) | 12 |
| Limit of a sequence | Advanced, ch. 1 (p. 2) | 12 |

Other facts:

- **Complex numbers are in no Grade 12 book and not in Grade 11 Basic** [SEEN]. They are taught in Grade 11 and examined at the end of Grade 12.
- Grade 11 Advanced ch. 5 is titled limits and derivatives, but its only lesson is applying derivatives to equations and inequalities [SEEN].
- Grade 12 Advanced has no chapter on limits of functions [SEEN].
- The mathsupporter page swaps the Grade 12 Basic and High chapter lists in its book blurbs. Its solutions list and the book contents agree with the table above [SEEN].

**Stream mapping is [INFERENCE], not stated in any source read.** Society papers stay inside Basic topics. Science papers use both: complex numbers (Advanced only) and conics (Basic only, Grade 12), alongside limits of functions (Basic only). So science stream appears to cover Basic plus Advanced, and society stream Basic only. A teacher should confirm this.

Data rule: tag complex items `grade: 11, exam: BacII science`. Tag limits and continuity `grade: 12`, with `grade: 11` only for the simple rule-based limits of Grade 11 Basic.

## 2. What appears on the papers

### 2.1 Coverage

Science: 16 sessions, 2007-2019 and 2021-2022 (2007-2013 through the compilation only; 2020 not found). Society: 2014-2019, 2021, 2022 and SalaDigital papers 1 and 13-15. Paper 12 is the same paper as society 2022, so 12 to 15 appear to run 2022 to 2025 [INFERENCE]; the pages show no year.

| Finding | Science | Society |
|---|---|---|
| Complex-number exercise | 16 of 16 sessions | 0 in every paper checked |
| Standalone limit exercise | 11 of 16 | Every paper checked |
| Limits inside a function study | 12 of 12 in the compilation; also 2021 | Common; part of the function-study item |
| Continuity item | 0 | 1 (SalaDigital paper 1) |
| Limit of a sequence | 0 | 0 |

The 11 of 16 may undercount. The compilation may be selective for 2008, 2009 and 2011-2013, which were not checked against whole papers. [SEEN]

### 2.2 Complex numbers, science stream [SEEN]

Marks and position:

| | Count of 16 |
|---|---|
| 10 marks | 5 (2007, 2009, 2011-2013) |
| 15 marks | 9 |
| 20 marks | 1 (2014 second session) |
| No marks shown in the copy | 1 (2021) |
| Exercise I | 8 (2007-2013, 2015) |
| Exercise II | 3 (2014 both sessions, 2016) |
| Exercise III | 5 (2017-2019, 2021, 2022) |

Task counts (a session can count more than once):

| Task | Sessions of 16 |
|---|---|
| Write in trigonometric form | 14 |
| Compute sum, difference, product or quotient | About 9 |
| Conjugate used or asked | 5 (2007, 2008, 2019, 2021, 2022) |
| Power of 3 or more, via trigonometric form | 5 (2012, 2016, 2017, 2019, 2022) |
| Modulus and argument asked by name | 4 (2010, 2014 second, 2017, 2021) |
| Solve a quadratic in the complex numbers | 3 (2010, 2011, 2019) |
| Show a number is a root of a given equation | 2 (2014 first, 2021) |
| Powers of `i` | 1 (2014 second) |
| Modulus condition with a parameter | 1 (2008) |
| **Plot in the plane, or any geometry** | **0** |
| **Find n-th roots directly** | **0** |

The core item: two or three numbers with `\sqrt{3}`, `\sqrt{2}` or similar, so that the argument is a standard angle. Then arithmetic, then trigonometric form, then a follow-on such as a power. Arguments are multiples of `\pi/6` or `\pi/4` in every item checked. Do not generate items with non-standard arguments.

Lessons 3 and 4 are lightly tested or untested. Include them for coverage, at low weight, and flag them as textbook-style rather than exam-style.

### 2.3 Limits

Science standalone item [SEEN]: 11 items, 33 parts. Usually three parts labelled ក ខ គ, up to five in 2014 second session. Marks where shown: 20 once, 15 four times, 10 once (2022).

| Part type, my classification | Parts of 33 |
|---|---|
| Contains a trigonometric function, usually needs `\sin u / u` or a substitution | 17 |
| Root, usually rationalised by the conjugate | About 9 |
| Rational, factorise | About 5 |
| At `\pm\infty` | 5 |
| Involves `\ln` or `e^x` | About 6 |

Types overlap. 10 of 11 items include a trigonometric part. Within an item, the easier algebraic part normally comes first and the trigonometric part after it, though not always.

Society standalone item [SEEN]: marks 10 or 15, 2 to 4 parts. It is easier. Parts are direct substitution, a polynomial, a rational or root `0/0` form, and limits at `\pm\infty`, sometimes with `e^x` or `\ln x`. Trigonometric parts are rare, for example `\sin^2 x` over a multiple of `x`.

Function-study limits [SEEN]: compute `\lim f(x)` at `\pm\infty`, or at `0^+` or an excluded value. Then deduce an asymptote. The prompt often supplies a known limit as a hint in brackets: `(យើងដឹងថា ...)`. This is the main way limits of `\ln x / x` and `x / e^x` enter.

### 2.4 Continuity [SEEN]

Only one exam item found: society paper 1, a two-piece function with a parameter, find the parameter given continuity at the join. Textbook and answer-book drills cover: test at a point, continuity on an interval, and find a constant so that a piecewise function is continuous everywhere.

Keep continuity a small share of the data, and put it in the society and textbook-style slices.

### 2.5 Order on the paper [SEEN]

Science, common recent order: limits, then probability or integrals, then complex numbers, integrals, space geometry and conics, differential equations, and last the function study. The order is not fixed. In 2015 complex came first and limits second; in 2018 probability came first.

Society, common order: limits, integrals, probability, conics, function study. 

## 3. Header and marks [SEEN]

This updates `style_guide.md`, section 1, where marks were unverified.

- **Per-exercise marks are printed** in brackets after the number, in Khmer digits: `I. (១៥ពិន្ទុ)`. Marks are per exercise, never per part.
- Totals check on full copies: science 2016 adds to 125 and society 2016 to 75. Some copies omit marks (2017 and 2021 in places). **Do not invent marks; use the bands in section 2.**
- Header lines: `ប្រឡងសញ្ញាបត្រមធ្យមសិក្សាទុតិយភូមិ`, `សម័យប្រឡង` and a date, `វិញ្ញាសា: គណិតវិទ្យា (ថ្នាក់វិទ្យាសាស្ត្រ)` or `(ថ្នាក់សង្គម)`, `រយៈពេល: ១៥០នាទី` or `៩០នាទី`, `ពិន្ទុ: ១២៥` or `៧៥`, then `ប្រធាន`.
- The solution block is headed `អត្រាកំណែ` or `ចម្លើយ`.
- Science 2014-2022 runs to six or seven exercises and society to five [SEEN].
- Exercise numbers are Roman in most copies; 2018 uses Khmer digits. Parts mix `ក ខ គ`, `១ ២ ៣`, `a b c`, and nested `១. a.` forms. Choose per item, and stay consistent inside it.

## 4. Question wording [SEEN]

Terse, imperative, ends with ។.

### Complex

- Opening: `គេមានចំនួនកុំផ្លិច` (recent) or `គេឱ្យចំនួនកុំផ្លិច` (older), then the numbers joined by `និង`.
- `គណនា` + expressions.
- `សរសេរ` + object + `ជាទម្រង់ត្រីកោណមាត្រ`; likewise `ជាទម្រង់ពីជគណិត`.
- `រកម៉ូឌុល និងអាគុយម៉ង់នៃ` + number. `កំណត់` is an older alternative.
- `ដោះស្រាយសមីការ ... ក្នុងសំណុំចំនួនកុំផ្លិច`.
- `បង្ហាញថា ... ជាឫសរបស់សមីការ`.
- `ទាញរកតម្លៃនៃ` + power, the deduction follow-on.
- Conjugate gloss in brackets: `(... ជាចំនួនកុំផ្លិចឆ្លាស់នៃ ...)`.

### Limits and continuity

- Science: `គណនាលីមីត` then the parts.
- Society: `គណនាលីមីតនៃអនុគមន៍ខាងក្រោម`.
- In a study: `គណនា` + `\lim` expressions, or `គណនាលីមីតនៃ f(x) ត្រង់ -∞ និងត្រង់ +∞`, or `សិក្សាលីមីតនៃអនុគមន៍ f ត្រង់ ...`.
- Continuity: `រកតម្លៃ a ដោយដឹងថា f ជាប់ត្រង់ x = a`; textbook forms `សិក្សាភាពជាប់ត្រង់ ...` and `តើ f ជាអនុគមន៍ជាប់ត្រង់ ... ឬទេ?`.

## 5. Complex numbers: conventions

### 5.1 Notation

| Item | Convention | Label |
|---|---|---|
| Algebraic form | Textbook definition `a+bi`; exams nearly always put `i` before a root: `a+i\sqrt{b}` | [SEEN] |
| Names | `z`, `z_1`, `z_2`; capitals `A`, `B`, `Z` also occur | [SEEN] |
| Conjugate | `\bar{z}`, `\overline{z_1}` | [SEEN] |
| Opposite | `-z`, named `ចំនួនកុំផ្លិចផ្ទុយ` | [SEEN] |
| Modulus | `|z|`; solutions write `|z| = r = \sqrt{a^2+b^2}` | [SEEN] |
| Argument | `\alpha`, then `\alpha = \theta + 2k\pi,\ k\in\mathbb{Z}`. No `\arg z` symbol seen in the papers | [SEEN] |
| Trigonometric form | `r(\cos\alpha + i\sin\alpha)` | [SEEN] |
| `cis` or `re^{i\theta}` | Not seen in anything read. Avoid | [SEEN] negative |
| Set | `\mathbb{C}`; `ℝ` in papers. Kim Sokun's derivative chapters use `IR` | [SEEN] |
| Product sign | `\times` between numbers, as in `z_1 \times z_2`; textbook uses `z_1 \cdot z_2` | [SEEN] |

### 5.2 Plane wording [SEEN]

The word Argand is not used in anything read. Say `ប្លង់កុំផ្លិច`. A point is the image of a number: `A(z_1)`, phrased `ជារូបភាពរៀងគ្នានៃ z_1 និង z_2`. Distance is `AB = |z_2 - z_1|`, with `ឯកតា` after the value.

### 5.3 Solution layout [SEEN]

1. Repeat the part, then `គេមាន`, `យើងមាន` or `យើងបាន`.
2. For a modulus, write `|z| = r = ...`.
3. For an argument, write `\cos\alpha = a/r` and `\sin\alpha = b/r`, each resolved to `\cos\theta` or `\sin\theta`, then `\Rightarrow \alpha = ...`.
4. An alternative route factors out the modulus, then recognises the bracket: `z = r(... + i...)`.
5. Close with `ដូចនេះ`, naming the object: `ម៉ូឌុលនៃចំនួនកុំផ្លិច z_1 គឺ ...`, `អាគុយម៉ង់ ... គឺ ...`.
6. Powers use the trigonometric form and De Moivre's rule. The rule's name was not seen in the solutions read [GENERAL].
7. For the textbook, `i^2 = -1` is cited inline as `ដោយ i^2 = -1` [SEEN].
8. Properties are proved by computing both sides, labelled (1) and (2), then `ដូចនេះ តាមទំនាក់ទំនង (1) និង (2)` [SEEN].

Textbook markers: `ឧទាហរណ៍`, `ចម្លើយ`, `លំហាត់គំរូ`, `ប្រតិបត្តិ`, `ជាទូទៅ`, `សន្និដ្ឋាន`, `សម្គាល់`, `និយមន័យ` [SEEN]. These are textbook register, and should not appear in exam-style items.

Quadratics in the complex numbers: the layout was not seen in a worked solution. The discriminant form `\Delta = ... = (i\ldots)^2` is [GENERAL]. Confirm before generating at scale.

## 6. Limits and continuity: conventions

### 6.1 Notation [SEEN]

- Exams and recent solutions use lowercase `\lim`. Kim Sokun's answer book often uses capital `Lim` with a hyphen label: `ក- Lim ...`. Normalise to `\lim`.
- One-sided: `x\to 3^-`, `x\to 3^+`, `x\to 0^+`. Infinity is always signed in exam prompts: `x\to+\infty`, `x\to-\infty`; `x\to\pm\infty` occurs.
- Location words: `ត្រង់ +∞`, `ត្រង់ 0`, `កាលណា x\to a`.
- Intervals: `(0,1)`, `[0,3]`; the older French `]0,+\infty[` occurs in the 2014 paper.
- Domain with exclusions: `\mathbb{R}\setminus\{-2,2\}`, or `\mathbb{R}-\{2\}`. One copy has `\Re`.

### 6.2 Indeterminate forms [SEEN]

- Named in brackets after the limit: `(រាងមិនកំណត់ 0/0)` or `(មានរាងមិនកំណត់ ∞/∞)`. Written as a stacked fraction.
- Then a chain on `=` over several lines, with no words between steps.
- Society solutions do this consistently. Science solutions (2021, 2022) often go straight to the chain.
- Direct cases are substituted without comment.
- `∞-∞` and `0×∞` labels were not seen. Use the same frame [GENERAL].

### 6.3 Techniques as shown [SEEN]

- **Conjugate:** numerator and denominator multiplied in one displayed line, then cancelled.
- **Factor out the top power at infinity:** `x^3(...)/x^3(...)`.
- **Substitution:** `តាង t = ... ⇒ x = ...`, then `បើ x → a នោះ t → 0`.
- **Standard limit:** the fraction is reshaped until `\sin u / u` appears, or the formula is cited in brackets, as `(រូបមន្ត ...)`.
- **A second method** is headed `របៀបមួយទៀត`.
- L'Hospital's rule: not seen in the solutions read. Do not use it in exam-style solutions until a teacher confirms it [SEEN negative].
- Limit of a composite: `\ln` is pulled outside, then `\ln 1 = 0`.

### 6.4 Result

`ដូចនេះ` + the full limit statement with its value. Boxing: Kim Sokun and the 2014 compilers box the value; 2021-2022 solutions leave it unboxed. Keep `\boxed{}` as the default, consistent with `style_guide.md`.

If a limit fails to exist, use the frame `លីមីតឆ្វេងមិនស្មើលីមីតស្តាំ ... គ្មានលីមីត ... ទេ` [SEEN, Grade 12 Basic p. 29].

### 6.5 Continuity write-up [SEEN]

The definition has three conditions: `f` is defined at `c`, the limit exists, and the limit equals `f(c)`.

Layout for a piecewise function at the join:

1. Heading: `សិក្សាភាពជាប់ត្រង់ x = c`.
2. Compute `f(c)`.
3. Compute `\lim_{x\to c^-} f(x)` and `\lim_{x\to c^+} f(x)` on separate lines.
4. `យើងឃើញថា` + the three equal values.
5. `នោះ f ជាប់ត្រង់ x = c`.
6. If needed, `សន្និដ្ឋាន៖ f ជាប់លើចន្លោះ ...`.

For a parameter: `f ជាប់ ... លុះត្រាតែ` + the equation, `\Leftrightarrow` the value, then `ដូចនេះ`.

For an interval: state continuity with the reason `ព្រោះ f មិនកំណត់តែត្រង់ x = ...`.

Formal `\varepsilon`-`\delta` proofs appear in the answer book, chapter 1, with `តាមនិយមន័យ` and chains joined by `សមមូល`. They are textbook only; none were seen on a paper.

## 7. Suggested mix [INFERENCE]

From section 2; a judgement, not a source fact.

- Complex: about 70% arithmetic plus trigonometric form plus a follow-on; 15% quadratics and roots of equations; 10% modulus or conjugate conditions; 5% textbook geometry and n-th roots.
- Limits, science: three-part items with at least one trigonometric part.
- Limits, society: rational, root, and limits at infinity.
- Continuity: under 10% of limit items.
- Sequence limits: textbook slice only, labelled not seen on BacII.

## 8. Pitfalls

- **Copies disagree.** Compilation and retyped paper differ for 2017 (the second number) and 2015 (the sign of a number). Treat every copy as unverified.
- **Retyped solutions contain typos**, for example a mistyped line then corrected in 2022, and a broken function header in the 2021 copy. Check all mathematics independently before use.
- **Spelling varies.** លីមីត and លីមិត; ពីជគណិត and ពិជគណិត; ឱ្យ, ឲ្យ and អោយ; ប្រឡង and ប្រលង. Normalise to លីមីត and ឱ្យ. The standard form for algebraic needs a Khmer reader's decision; I read both.
- **Text layers are unsafe.** All reading here was from rendered images, some at low resolution. Khmer spellings marked [SEEN] still need a native check.
- **Inventory correction:** SalaDigital item 00007808 is the social-science volume, so it does not contain complex-number items. The science volume was not located.
- **2025:** reported leak of the science maths paper; treat unofficial copies with caution [SNIPPET].
- **Rights:** the HELMAB repo says documents belong to their owners. Nothing read grants reuse. Generate original items only.

## 9. Glossary: complex numbers

| # | Khmer | English | LaTeX | Label |
|---|---|---|---|---|
| 1 | ចំនួនកុំផ្លិច | complex number | `z` | [SEEN] |
| 2 | សំណុំចំនួនកុំផ្លិច | set of complex numbers | `\mathbb{C}` | [SEEN] |
| 3 | ទម្រង់ពីជគណិត | algebraic form | `a+ib` | [SEEN] |
| 4 | ទម្រង់ត្រីកោណមាត្រ | trigonometric form | `r(\cos\alpha+i\sin\alpha)` | [SEEN] |
| 5 | ផ្នែកពិត | real part | `a` | [SEEN] |
| 6 | ផ្នែកនិមិត្ត | imaginary part | `b` | [SEEN] |
| 7 | ឯកតានិមិត្ត | imaginary unit | `i,\ i^2=-1` | [SEEN] |
| 8 | ចំនួននិមិត្ត | imaginary number | `bi` | [SEEN] |
| 9 | ចំនួនកុំផ្លិចឆ្លាស់ | conjugate | `\bar{z}` | [SEEN] |
| 10 | ចំនួនកុំផ្លិចផ្ទុយ | opposite | `-z` | [SEEN] |
| 11 | ម៉ូឌុល | modulus | `\lvert z\rvert` | [SEEN] |
| 12 | អាគុយម៉ង់ | argument | `\alpha` | [SEEN] |
| 13 | លក្ខណៈម៉ូឌុល | properties of the modulus | `\lvert z_1z_2\rvert=\lvert z_1\rvert\lvert z_2\rvert` | [SEEN] |
| 14 | ប្លង់កុំផ្លិច | complex plane | | [SEEN] |
| 15 | រូបភាព | image of a number | `A(z)` | [SEEN] |
| 16 | ប្រមាណវិធី | operation | | [SEEN] |
| 17 | វិធីបូក | addition | `+` | [SEEN] |
| 18 | វិធីដក | subtraction | `-` | [SEEN] |
| 19 | វិធីគុណ | multiplication | `\times` | [SEEN] |
| 20 | ផលបូក | sum | `z_1+z_2` | [SEEN] |
| 21 | ផលដក | difference | `z_1-z_2` | [SEEN] |
| 22 | ផលគុណ | product | `z_1\times z_2` | [SEEN] |
| 23 | ផលចែក | quotient | `z_1/z_2` | [GENERAL] |
| 24 | ស្វ័យគុណទី n | n-th power | `z^n` | [SEEN] |
| 25 | ឫសទី n | n-th root | `\sqrt[n]{z}` | [SEEN] |
| 26 | ឫស | root of an equation | `z_1,z_2` | [SEEN] |
| 27 | សមីការ | equation | | [SEEN] |
| 28 | សមីការដឺក្រេទីពីរ | quadratic equation | `az^2+bz+c=0` | [GENERAL] |
| 29 | ឌីសគ្រីមីណង់ | discriminant | `\Delta` | [GENERAL] |
| 30 | រូបមន្តដឺម័រ | De Moivre's formula | `(\cos\alpha+i\sin\alpha)^n` | [GENERAL] |
| 31 | ចំនួនពិត | real number | `\mathbb{R}` | [SEEN] |
| 32 | ចំនួនគត់រ៉ឺឡាទីប | integer | `\mathbb{Z}` | [SEEN] |
| 33 | ចម្ងាយ | distance | `AB=\lvert z_2-z_1\rvert` | [SEEN] |
| 34 | ប្រវែង | length | `AB` | [SEEN] |
| 35 | ឯកតា | unit | | [SEEN] |
| 36 | ត្រីកោណសមបាត | isosceles triangle | | [SEEN] |
| 37 | ត្រីកោណកែង | right triangle | | [SEEN] |
| 38 | ត្រីកោណសម័ង្ស | equilateral triangle | | [SEEN] |
| 39 | អ័ក្សពិត | real axis | | [GENERAL] |
| 40 | អ័ក្សនិមិត្ត | imaginary axis | | [GENERAL] |
| 41 | តម្រុយអរតូណរម៉ាល់ | orthonormal frame | `(O,\vec{i},\vec{j})` | [SEEN] |
| 42 | ទំនាក់ទំនង | relation | | [SEEN] |
| 43 | លក្ខខណ្ឌ | condition | | [SEEN] |
| 44 | សរសេរ | write | | [SEEN] |
| 45 | គណនា | calculate | | [SEEN] |
| 46 | កំណត់ | determine | | [SEEN] |
| 47 | បង្ហាញថា | show that | | [SEEN] |
| 48 | ផ្ទៀងផ្ទាត់ | verify | | [SEEN] |
| 49 | ទាញរក | deduce | | [SEEN] |
| 50 | ដោះស្រាយ | solve | | [SEEN] |
| 51 | អនុវត្តន៍ក្នុងធរណីមាត្រ | applications to geometry | | [SEEN] |
| 52 | ដែល | where, such that | | [SEEN] |
| 53 | ស៊ីនុស | sine | `\sin` | [GENERAL] |
| 54 | កូស៊ីនុស | cosine | `\cos` | [GENERAL] |
| 55 | មុំ | angle | `\alpha` | [GENERAL] |

## 10. Glossary: limits and continuity

| # | Khmer | English | LaTeX | Label |
|---|---|---|---|---|
| 1 | លីមីត | limit | `\lim` | [SEEN] |
| 2 | លីមីតនៃអនុគមន៍ | limit of a function | `\lim_{x\to a}f(x)` | [SEEN] |
| 3 | លីមីតនៃស្វ៊ីត | limit of a sequence | `\lim_{n\to+\infty}u_n` | [SEEN] |
| 4 | លីមីតឆ្វេង | left limit | `\lim_{x\to a^-}` | [SEEN] |
| 5 | លីមីតស្តាំ | right limit | `\lim_{x\to a^+}` | [SEEN] |
| 6 | មានលីមីត | has a limit | | [SEEN] |
| 7 | គ្មានលីមីត | has no limit | | [SEEN] |
| 8 | រាងមិនកំណត់ | indeterminate form | `\frac{0}{0},\ \frac{\infty}{\infty}` | [SEEN] |
| 9 | ប្រមាណវិធីលើលីមីត | limit rules | | [SEEN] |
| 10 | ភាពជាប់ | continuity | | [SEEN] |
| 11 | ភាពជាប់នៃអនុគមន៍ | continuity of a function | | [SEEN] |
| 12 | អនុគមន៍ជាប់ | continuous function | | [SEEN] |
| 13 | ជាប់ត្រង់ | continuous at | `x=c` | [SEEN] |
| 14 | ជាប់លើចន្លោះ | continuous on an interval | `[a,b]` | [SEEN] |
| 15 | ជាប់គ្រប់តម្លៃ x | continuous for all x | `\forall x` | [SEEN] |
| 16 | មិនជាប់ | not continuous | | [SEEN] |
| 17 | អនុគមន៍ដាច់ត្រង់ | discontinuous at | `x=c` | [SEEN] |
| 18 | សិក្សាភាពជាប់ | study continuity | | [SEEN] |
| 19 | និយមន័យ | definition | | [SEEN] |
| 20 | តាមនិយមន័យ | by definition | `\varepsilon,\ \delta` | [SEEN] |
| 21 | ស្រាយបញ្ជាក់ | prove | | [SEEN] |
| 22 | អនុគមន៍ថេរ | constant function | `f(x)=c` | [SEEN] |
| 23 | ពហុធា | polynomial | `P(x)` | [SEEN] |
| 24 | អនុគមន៍សនិទាន | rational function | `P(x)/Q(x)` | [SEEN] |
| 25 | អនុគមន៍លោការីត | logarithmic function | `\ln x` | [SEEN] |
| 26 | អនុគមន៍ត្រីកោណមាត្រ | trigonometric function | `\sin x` | [SEEN] |
| 27 | ត្រង់ | at | `+\infty` | [SEEN] |
| 28 | កាលណា | when, as | `x\to a` | [SEEN] |
| 29 | តាង | let | `t=x-a` | [SEEN] |
| 30 | រូបមន្ត | formula | | [SEEN] |
| 31 | របៀបមួយទៀត | another method | | [SEEN] |
| 32 | យើងដឹងថា | we know that | | [SEEN] |
| 33 | យើងឃើញថា | we see that | | [SEEN] |
| 34 | សន្និដ្ឋាន | conclusion | | [SEEN] |
| 35 | ដូចនេះ | therefore | | [SEEN] |
| 36 | ជាទូទៅ | in general | | [SEEN] |
| 37 | សម្គាល់ | remark | | [SEEN] |
| 38 | សមមូល | equivalent to | `\Leftrightarrow` | [SEEN] |
| 39 | នាំឱ្យ | implies | `\Rightarrow` | [SEEN] |
| 40 | លុះត្រាតែ | if and only if | `\Leftrightarrow` | [SEEN] |
| 41 | ដែនកំណត់ | domain | `D` | [SEEN] |
| 42 | ចន្លោះ | interval | `(a,b)` | [SEEN] |
| 43 | អាស៊ីមតូតឈរ | vertical asymptote | `x=a` | [SEEN] |
| 44 | អាស៊ីមតូតដេក | horizontal asymptote | `y=b` | [SEEN] |
| 45 | អាស៊ីមតូតទ្រេត | slant asymptote | `y=ax+b` | [SEEN] |
| 46 | ភាគយក | numerator | | [GENERAL] |
| 47 | ភាគបែង | denominator | | [GENERAL] |
| 48 | អនន្ត | infinity | `\infty` | [GENERAL] |
| 49 | ខិតជិត | approach | `\to` | [GENERAL] |
| 50 | កន្សោមឆ្លាស់ | conjugate expression | `\sqrt{a}+\sqrt{b}` | [GENERAL] |
| 51 | ដាក់ជាកត្តា | factorise | | [GENERAL] |
| 52 | តម្លៃដាច់ខាត | absolute value | `\lvert x\rvert` | [GENERAL] |
| 53 | ទ្រឹស្តីបទតម្លៃកណ្តាល | intermediate value theorem | | [GENERAL] |
| 54 | អនុគមន៍កំណត់ជាផ្នែក | piecewise function | `\begin{cases}` | [GENERAL] |
| 55 | ស្វ៊ីតរួម | convergent sequence | | [GENERAL] |

Items 16 and 17 of this table, and any other [SEEN] term here, were read on images. Have a Khmer reader check them before they are used as spelling targets.
