# Row format (one JSON object per line)

| field | meaning |
|---|---|
| id | unique, `<topic>-<hash>` |
| chapter | always `derivative` |
| topic, subtopic | see the topic list in the agent brief |
| difficulty | `easy`, `medium`, `hard`, `bacii` |
| marks | BacII marks if a multi-part exam item, else null |
| problem_km | Exercise in Khmer. All math in `$...$` or `$$...$$` |
| solution_km | Full student write-up from first line to final answer, Khmer prose, math in LaTeX |
| answer_latex | Final answer only, LaTeX, no dollars |
| diagrams | list of `{type, latex, image, alt_km}`. type: `variation_table`, `sign_table`, `graph`, `figure`. `latex` is required (array or pgfplots source). `image` is optional PNG path. |
| checks | list of `{lhs, rhs, note}` SymPy strings; `lhs` from the problem definition, `rhs` the stated result |
| provenance | `{origin, generator, source_url, license}` |

`origin` values: `original_synthetic` (written for this dataset), `open_licensed` (imported, with source and licence).

Rules: no English words outside math. Khmer punctuation (។). Text in figures is math only, because matplotlib cannot shape Khmer.

## Added for complex numbers and limits
`chapter`: `derivative`, `complex`, or `limit`. `grade`: 11 or 12. Files go to `out/<chapter>/<topic>.jsonl`.
Checks may use `I`, `re`, `im`, `conjugate`, `arg`, and one-sided limits such as `limit(1/x,x,0,'+')`. Each check has a 20 second limit.

## Added for integrals, differential equations, probability
`chapter`: also `integral`, `diffeq`, `probability`. All grade 12.
Checks may also use `integrate`, `binomial`, and `nint_abs(f,a,b)`, a numeric integral of the absolute value used for areas.
