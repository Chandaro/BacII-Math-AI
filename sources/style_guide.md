# BacII mathematics: derivative and function-study style guide

Own synthesis for building Khmer fine-tuning data. No exercise or solution is reproduced here. Khmer items are short terms and stock phrases only.

## 0. Evidence and confidence

Every claim carries one of these labels.

- **[SEEN]**: read on rendered pages of a source.
- **[SNIPPET]**: from a search snippet or a secondary page; the primary page was not read.
- **[GENERAL]**: general knowledge of the Khmer and French-derived tradition; not confirmed in this research. Have a Cambodian maths teacher check these.

What was actually read:

- Kim Sokun's two-page list of national exam derivative items, 2007-2017, science stream.
- Sample pages from the Basic Level answer book by the same author: chapter 2 (derivatives, 30 pages) and chapter 3 (function study, 56 pages).

Limits of this evidence:

- These are **a teacher's model solutions, not student scripts**. No real student answer sheet was found. Treat them as the target register, not as proof of what students write under exam conditions.
- It is essentially **one author and the Basic Level**. Advanced-level answer books, the Lim Phalkun books and the MoEYS textbooks were listed but not read.
- No original exam paper was seen, so the printed exam header and per-question marks are unconfirmed (section 1).

## 1. Exam structure

| Item | Finding | Label |
|---|---|---|
| Science stream maths paper | 125 marks, 150 minutes (2024 notice) | [SNIPPET] MoEYS page; direct fetch rejected |
| Social-science stream maths paper | 75 marks, 90 minutes (2024 notice) | [SNIPPET] same |
| Whole exam | 2 days, 630 minutes, 500 points, pass 237 when the optional language is excluded | [SNIPPET] Sabay, quoting MoEYS for 2023 |
| Grades | A to E at 0.9, 0.8, 0.7, 0.6, 0.5 of the total | [SNIPPET] same |
| Format | Written constructed response, not multiple choice | [SNIPPET] |
| Sessions | Normally one a year; 2014 had two (លើកទី១, លើកទី២) | [SEEN] |
| Timing | Moved around: October 2024, August 2025 | [SNIPPET] |

**Marks allocation per question is not verified.** No source read shows marks beside a question. Do not invent per-item marks in training data. If marks are needed, take them from an original paper. The only proxy found: the derivative item sits in the last, heavier exercises (section 7).

## 2. Numbering and layout

- **Top-level exercises use Roman numerals**: I., II., ... up to VII. in 2015-2017 [SEEN].
- **Parts use Khmer digits** after the Roman numeral, such as `VI. ២.` [SEEN]. Some years use a letter block, such as `VII. B.` in 2015 [SEEN].
- **Textbook and answer-book items** use an Arabic number, then Khmer consonants in order: ក. ខ. គ. ឃ. ង. ច. [SEEN]. Sometimes the separator is a hyphen, as in `ខ-` [SEEN].
- **Years and exam titles** use Khmer digits (២០១៧) [SEEN].
- **Everything inside mathematics** uses Latin letters and Arabic digits [SEEN]. Never write Khmer digits inside a formula.
- **Sentences end with the khan ។**, including after a formula [SEEN]. Solution lines that are mostly formulas often have no ។ [SEEN].
- **Answer-book layout** [SEEN]: the exercise block is restated with all its parts, then a centred bold heading `ដំណោះស្រាយ`. Each part is then repeated by label, followed by one or two `គេបាន` or `យើងបាន` lines, then `ដូចនេះ` and a boxed result. Running headers name the book and chapter.
- **Spaces** separate clauses and surround inline formulas, since Khmer has no word spaces [SEEN].

## 3. How questions are worded

Prompts are terse, imperative and have no subject [SEEN]. The common derivative prompt has a fixed shape:

`គណនាដេរីវេនៃ` + function + `រួចសង់តារាងអថេរភាពនៃ` + `f` + `។`

A follow-up tangent line uses:

`រកសមីការបន្ទាត់ប៉ះនៃខ្សែកោង` + `ត្រង់ចំណុច` + point or abscissa + `។`

Other patterns:

- A sign fact is supplied with `បើគេដឹងថា ...` [SEEN].
- A domain restriction is attached after a comma, as in `, x > -1` [SEEN].
- Multi-item drills open with `... នៃអនុគមន៍ខាងក្រោម` [SEEN].
- A parameter task begins `រកតម្លៃ m ដើម្បីឲ្យ ...` [SEEN].

### Imperative verbs

| Khmer | English | Use | Label |
|---|---|---|---|
| គណនា | calculate | derivative, value, limit | [SEEN] |
| រក | find | equation, value | [SEEN] |
| សង់ | draw, construct | variation table, graph | [SEEN] |
| សិក្សា | study | variation of a function | [SEEN] |
| ផ្ទៀងផ្ទាត់ | verify | identity, fixed point | [SEEN] |
| កំណត់ | determine | constants, domain | [GENERAL] |
| បង្ហាញថា | show that | results | [GENERAL] |
| ស្រាយបញ្ជាក់ | prove | proofs | [GENERAL] |
| ទាញរក, ទាញបញ្ជាក់ | deduce | follow-on parts | [GENERAL] |
| ដោះស្រាយ | solve | equations | [GENERAL] |

## 4. Connective phrases in solutions

All [SEEN] unless marked.

| Function | Khmer | Note |
|---|---|---|
| Opening a computation | យើងបាន | the default opener before `f'(x) = ...` |
| Stating a given fact | យើងមាន | often before a limit or rewritten form |
| Result of a step | គេបាន | impersonal; very frequent |
| "One may write" | គេអាចសរសេរ, សរសេរ ... ជារាង | rewriting before differentiating |
| Since, because | ដោយ, ដោយសារ | a fact, then នោះ |
| Then, it follows | នោះ | pairs with ដោយ or បើ |
| If | បើ | for `f'(x) = 0` |
| For, when | ចំពោះ | case split on a parameter, or `∀x` range |
| And, moreover | ហើយ, និង | ហើយ adds a second result |
| Or | ឬ | `x_1 ... ឬ x_2 ...` |
| Only if | លុះត្រាតែ | the domain step: defined only if denominator is nonzero |
| Therefore (final) | ដូចនេះ | **the standard conclusion marker** |
| According to a formula | តាមរូបមន្ត | citing a formula |
| Confirms that | នោះបញ្ជាក់ថា | closing a verification |
| Defined by | កំណត់ដោយ ៖ | introduces an equation |
| Sign follows | យកសញ្ញាតាម, មានសញ្ញាអាស្រ័យ | sign of `f'` follows the numerator |
| Differentiate both sides | ធ្វើដេរីវេលើអង្គទាំងពីរ | implicit differentiation |
| Constantly negative | ជានិច្ច | `... < 0` ជានិច្ច |
| No solution | សមីការគ្មានឫស | negative discriminant |
| Has no such object | គ្មាន ... ទេ | the negation frame, as in គ្មានអាស៊ីមតូតដេកទេ |

Register: impersonal and compact. A typical line is a short Khmer clause, a formula, and a short clause. There is almost no explanatory prose. **Formulas do most of the work.** Long chains are aligned on `=` over several lines. Implication symbols `⇒` and `⇔` replace many words [SEEN].

## 5. Order of a function study

Observed order in the answer book, as headed with `+` and `-` bullets [SEEN]:

1. **ដែនកំណត់**: state the condition with `លុះត្រាតែ`, then `D = IR - {...}`.
2. **Rewriting** (rational functions): `សរសេរ f(x) ជារាងកាណូនិក`, the quotient plus remainder form. This prepares the slant asymptote.
3. **ទិសដៅអថេរភាព**, with sub-steps:
   - `ដេរីវេទី១`: the quotient rule, simplified and factored.
   - Sign argument: the denominator is nonnegative on `D`, so `f'` takes the sign of the numerator.
   - Roots from `f'(x) = 0`.
   - `សញ្ញាដេរីវេទី១`: a small two-row sign table.
   - `ចំណុចបរមា`: state the maximum and minimum with their abscissas.
4. **លីមីតនិងអាស៊ីមតូត**: limits at infinity and one-sided limits at excluded values, then vertical and slant asymptotes.
5. **តារាងអថេរភាព**: the full table.
6. **សំណង់ក្រាប**, with sub-steps:
   - Intersection with `y'oy`, then with `x'ox`.
   - `ផ្ចិតឆ្លុះ`: centre of symmetry, checked with `f(2a-x) + f(x) = 2b`.
   - `ក្រាប`: the graph, with asymptotes drawn.

**This differs from the common textbook order of domain, limits, asymptotes, derivative.** In the source read, limits come **after** the derivative and sign. A separate exercise type asks for asymptotes first, using headings `អាស៊ីមតូតទ្រេត`, `អាស៊ីមតូតដេក`, `អាស៊ីមតូតឈរ`. Use the observed order as the default and keep the alternate as a minority variant. Other authors may differ, so check when the Lim Phalkun book or the advanced level is read.

The tangent, when asked, is a separate later step (section 6.4).

## 6. Conventions by task

### 6.1 Notation [SEEN]

- Derivative: `f'(x)`, `y'`, `y''`. Often `(u)'` is left unevaluated for one line.
- Real numbers: **`IR`, not ℝ**, in this source: `D = IR - {-1}`. The set difference is written with a minus sign, not `\setminus`.
- Axes: **`x'ox` and `y'oy`**.
- Point coordinates use a semicolon: `I(-1;-2)`. Some exam items use a comma: `(0,1)`. Both occur.
- Domain: `∀x ∈ D`. Roots: `x_1`, `x_2`. Discriminant: `Δ`, reduced `Δ'`.
- Limits: `lim` with `x→±∞`, `x→-1^-`, `x→-1^+`.
- Case systems use a left square bracket for "or".
- Final answers are in a **drawn box** after `ដូចនេះ` [SEEN]. In LaTeX, use `\boxed{...}`.

### 6.2 Rules for derivatives [SEEN]

Solutions apply rules silently. The rule is not named. The chain-rule form is written first with the inner derivative left as `(...)'`, then evaluated on the next line. Negative powers are used: `គេអាចសរសេរ` the reciprocal as a power, then differentiate. Answers are factored, not expanded.

### 6.3 The variation table [SEEN]

Three rows in a bordered grid, with labels in the first column:

| Row | Content |
|---|---|
| `x` | `-∞`, critical points and excluded values in increasing order, `+∞` |
| `f'(x)` | `+` or `-` per interval, `0` under each critical point |
| `f(x)` | arrows ↗ ↘ with limit and extreme values at arrow ends |

- An **excluded value** is shown by a vertical double bar through the `f'` and `f` rows. The limits sit on either side of it.
- A **two-row sign table** (`x`, `f'(x)`) often comes first; then the full table repeats it.
- Extreme values are placed high for a maximum and low for a minimum. Values at `±∞` go at the arrow ends.

LaTeX: sources draw this in Word. Recommended dataset form, which is our own convention:

```latex
\begin{array}{c|ccccc}
x & -\infty & & a & & +\infty \\ \hline
f'(x) & & + & 0 & - & \\ \hline
f(x) & L_1 & \nearrow & M & \searrow & L_2
\end{array}
```

Mark an excluded value with `\|` in its column.

### 6.4 Tangent line

Prompt wording is [SEEN] in section 3. The formula `y - y_0 = f'(x_0)(x - x_0)` is the standard [GENERAL]. **A worked tangent-at-a-point solution was not seen**, because the garbled text layer could not be searched for it. Confirm the layout from a source before generating these. A tangency condition via a double root, `Δ' = 0`, is also used: `បន្ទាត់ប៉ះនឹងក្រាបលុះត្រាតែ Δ' = 0` [SEEN].

### 6.5 Conclusions [SEEN]

- Derivative results: `ដូចនេះ` then the boxed formula.
- Extrema: `អនុគមន៍មានអតិបរមាស្មើនឹង M ត្រង់ x = a`, and likewise `អប្បបរមា`.
- Monotonic case: `f(x) ជាអនុគមន៍ចុះ`.
- Asymptotes: `បន្ទាត់ ... ជាអាស៊ីមតូតឈរ`, or `... ទ្រេត នៃខ្សែកោង`.
- Fixed point: `ដូចនេះ កូអរដោនេចំណុចនឹងមួយ ... គឺ`.

## 7. Derivative sub-topics and frequency

National exam science stream, 2007-2017: 12 sessions, 13 derivative items, counted from Kim Sokun's compilation [SEEN]. This is a secondary list, possibly selective, and it stops at 2017.

| Feature | Count of 13 |
|---|---|
| Ends with "draw variation table" | 11 |
| Asks a tangent line equation | 3 (2010, 2011, 2014 first session) |
| Asks extreme values explicitly | 1 (2007) |
| Function with `ln` | 7 |
| Function with `e^x` or `e^{-x}` | 5 |
| Rational function, no transcendental term | 1 |

Position in paper: IV in 3 items, V in 1, VI in 6, VII in 3. From 2015 to 2017 it is always VII.

The dominant recent shape is a linear part plus a quotient with `ln x` or `e^x`. This suggests that a dataset weighted towards rational functions would not match the exam. In the answer book, rational functions are the main drill, so the book and exam differ.

Answer-book chapter 2 also drills: power and chain rule, reciprocals, roots, products of powers, implicit differentiation with `y'` and `y''` [SEEN]. Chapter 3 also includes parameter families and fixed points [SEEN].

## 8. Pitfalls for data preparation

- **PDF text layers are unsafe.** Extraction garbles Khmer: subscripts and vowels are dropped or swapped, so ដេរីវេ comes out misspelled. Equations are embedded objects and fall out of order. OCR or manual entry would be needed, and output needs checking by a Khmer reader.
- **Spelling varies.** អនុគមន៍ is standard; អនុគមន៏ occurs in sources. Normalise to អនុគមន៍. Likewise ប្រឡង and ប្រលង, សង់ក្រាប and សង់ក្រាហ្វ. Choose one and record it.
- **Sources contain informal shortcuts**, such as an unsigned `∞` for a two-sided limit. Decide whether to keep or correct them.
- **Answer books contain real errors.** In chapter 2, page 25, part ង of the implicit drill differentiates `4(y+3)^2` as `4y'(y+3)` rather than `8y'(y+3)`, so its `y'` is off by a factor of 2. Check all mathematics independently, for example with a CAS, before any solution becomes a training target.
- **Rights are unresolved.** See `source_inventory.csv`. No source found grants reuse. Generate original exercises in this style instead of copying.
- **2025 paper:** there were reports of a leaked maths exam; treat unofficial copies with caution [SNIPPET].

## 9. Glossary

Column key: S = spelling seen in a source read or listed in this research; G = general knowledge, needs review.

| # | Khmer | English | LaTeX or notation | Src |
|---|---|---|---|---|
| 1 | ដេរីវេ | derivative | `f'(x)` | S |
| 2 | ដេរីវេទី១ | first derivative | `f'(x)` | S |
| 3 | ដេរីវេទី២ | second derivative | `f''(x)` | G |
| 4 | អនុគមន៍ | function | `f`, `y=f(x)` | S |
| 5 | ដែនកំណត់ | domain | `D` | S |
| 6 | លីមីត | limit | `\lim_{x\to a}` | S |
| 7 | អាស៊ីមតូត | asymptote | | S |
| 8 | អាស៊ីមតូតឈរ | vertical asymptote | `x=a` | S |
| 9 | អាស៊ីមតូតដេក | horizontal asymptote | `y=b` | S |
| 10 | អាស៊ីមតូតទ្រេត | slant asymptote | `y=ax+b` | S |
| 11 | អថេរភាព | variation | | S |
| 12 | ទិសដៅអថេរភាព | direction of variation | | S |
| 13 | តារាងអថេរភាព | variation table | `array` | S |
| 14 | សិក្សាអថេរភាព | study the variation | | S |
| 15 | សញ្ញា | sign | `+`, `-` | S |
| 16 | សញ្ញាដេរីវេទី១ | sign of the first derivative | | S |
| 17 | បន្ទាត់ប៉ះ | tangent line | `y-y_0=f'(x_0)(x-x_0)` | S |
| 18 | សមីការបន្ទាត់ប៉ះ | tangent equation | | S |
| 19 | ខ្សែកោង | curve | `(C)` | S |
| 20 | ក្រាប | graph | | S |
| 21 | សង់ក្រាប | sketch the graph | | S |
| 22 | សំណង់ក្រាប | graph construction | | S |
| 23 | ត្រង់ចំណុច | at the point | `x=a` | S |
| 24 | ចំណុច | point | `A(x;y)` | S |
| 25 | ចំណុចប្រសព្វ | intersection point | | S |
| 26 | ចំណុចបរមា | extreme point | | S |
| 27 | ចំណុចនឹង | fixed point | | S |
| 28 | អតិបរមា | maximum | `\max` | S |
| 29 | អប្បបរមា | minimum | `\min` | S |
| 30 | តម្លៃអតិបរមា | maximum value | | S |
| 31 | ផ្ចិតឆ្លុះ | centre of symmetry | `I(a;b)` | S |
| 32 | អ័ក្ស | axis | `x'ox`, `y'oy` | S |
| 33 | កូអរដោនេ | coordinates | `(x;y)` | S |
| 34 | អនុគមន៍កើន | increasing function | | S |
| 35 | អនុគមន៍ចុះ | decreasing function | | S |
| 36 | អនុគមន៍គូ | even function | `f(-x)=f(x)` | S |
| 37 | ភាពជាប់ | continuity | | S |
| 38 | ភាពដាច់ | discontinuity | | S |
| 39 | ខិតជិត | approach | `\to` | S |
| 40 | សមីការ | equation | | S |
| 41 | ឫស | root | `x_1,x_2` | S |
| 42 | រាងកាណូនិក | canonical form | | S |
| 43 | អង្គ | side of an equation | | S |
| 44 | តម្លៃ | value | | S |
| 45 | រូបមន្ត | formula | | S |
| 46 | លំហាត់ | exercise | | S |
| 47 | វិញ្ញាសា | exam paper | | S |
| 48 | ដំណោះស្រាយ | solution | | S |
| 49 | កំណែ | corrected answers | | S |
| 50 | ជំពូក | chapter | | S |
| 51 | អាំងតេក្រាល | integral | `\int` | S |
| 52 | ចំនួនកុំផ្លិច | complex number | `z` | S |
| 53 | ស្វ៊ីត | sequence | `(u_n)` | G |
| 54 | លោការីត | logarithm | `\ln x` | S |
| 55 | អ៊ិចស្ប៉ូណង់ស្យែល | exponential | `e^x` | G |
| 56 | ត្រីកោណមាត្រ | trigonometry | `\sin,\cos,\tan` | S |
| 57 | អនុគមន៍សនិទាន | rational function | `P(x)/Q(x)` | S |
| 58 | ពហុធា | polynomial | `P(x)` | G |
| 59 | ភាគយក | numerator | | G |
| 60 | ភាគបែង | denominator | | G |
| 61 | ផលគុណ | product | `uv` | G |
| 62 | ផលចែក | quotient | `u/v` | G |
| 63 | ផលបូក | sum | `u+v` | G |
| 64 | អនុគមន៍បណ្ដាក់ | composite function | `f\circ g` | S |
| 65 | មេគុណប្រាប់ទិស | slope | `m`, `f'(x_0)` | G |
| 66 | អាប់ស៊ីស | abscissa | `x` | G |
| 67 | អរដោនេ | ordinate | `y` | G |
| 68 | ចំណុចរបត់ | inflection point | `f''=0` | G |
| 69 | ឌីសគ្រីមីណង់ | discriminant | `\Delta` | G |
| 70 | អថេរ | variable | `x` | G |
| 71 | ថេរ | constant | `c` | G |
| 72 | ប៉ារ៉ាម៉ែត្រ | parameter | `m` | G |
| 73 | អនន្ត | infinity | `\infty` | G |
| 74 | ចន្លោះ | interval | `(a;b)`, `[a;b]` | G |
| 75 | សំណុំចំនួនពិត | set of real numbers | `IR` | G |
| 76 | ស្របនឹង | parallel to | `\parallel` | G |
| 77 | កែងនឹង | perpendicular to | `\perp` | G |
| 78 | ប្រសព្វ | intersect | | S |
| 79 | ប៉ះ | touch, be tangent | | S |
| 80 | ស្មើនឹង | equal to | `=` | S |
