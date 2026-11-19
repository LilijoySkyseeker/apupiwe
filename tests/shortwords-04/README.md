# Short words 04: can the grammar words stop resting on accent variants?

Question (author, 2026-11-18, on `tests/accent-01/` option B: "would B give us a better outcome, especially long term?"): what does it cost to re-form the short words so that no two words sharing a position differ only by a sound pair that common accents and sound change bring together?

Why it may matter long term: voiced stops softening between vowels is among the most common sound changes (Spanish, Greek, Celtic, Danish), and short, unstressed, frequent words wear down first. A contrast resting on it is the one most likely to merge as speakers change the language (goal B9, P3).

## Method

`rebuild.py` is `tests/shortwords-03/rebuild.py` (Decision 2's optimiser: model v2, robust score, positions, junctions, offensive tie-break) with two changes:

- `SW_SOFT=1` adds five mergers to hard rule H4 (words sharing a position may not differ only by them): **b/w** (b softened [β̞] ~ w as [ʋ]), **d/l** (d softened or flapped ~ l as a tap), **g/w** before o u, **g/y** before i e (g as [dʒ]), **k/s** before i e (k as [tʃ] ~ s as [ʃ]). Source: `tests/accent-01/`.
- MODMOD and ENDEAR are read from `data/grammar.tsv` (they exist since Decision 2); `reopt` keeps the repaired layer when the start breaks the new rules.

Start: today's applied layer (`today.tsv`). Under the new rule it has 10 violations: **din/lin**, **yi/gi**, **go/wo** (SOME / digit 4), **kin/sin**, **le/de** (ONGOING / digit 3), **se/ke**, **yen/gen**, **lu/du**, **wun/gun**, **wun/bun**. Runs: `reopt --lock OF,ALL` (the name **apu pi we**) at keep 0.005, 0.01 and 0.02 (Decision 2 used 0.01), seeds 1–3, and a control at keep 0.01 without the new rule. `./run.sh`; logs in `logs/`, layers in `runs/`.

## Results

Robust score (model v2, lower is better); today's layer 0.3037.

| run | words changed | robust | accent mergers left |
|---|---|---|---|
| control, no new rule (keep 0.01) | 0 | 0.3037 | 10 |
| minimal patch (`softpatch`: every minimum change set of 9 words, re-formed; best of 60) | 9 | 0.3353 | 0 |
| keep 0.005, seeds 1–3 | 39 / 47 / 33 | 0.2999 / **0.2878** / 0.2945 | 0 |
| keep 0.01, seeds 1–3 | 25 / 23 / 29 | 0.3150 / 0.3335 / 0.3642 | 0 |
| keep 0.02, seeds 1–3 | 24 / 16 / 18 | 0.3627 / 0.3249 / 0.3804 | 0 |

Findings:

1. **The rule can be met at no cost to the model's score**, but only by letting about half the layer move. The minimal patch (9 words; the best set re-forms PART, ONGOING, OR, THAT.comp, WHO.rel, MORE, WHILE, RESULT and digit 4) costs 10%; forcing a few words into the remaining space is worse than reshuffling.
2. **Seeds disagree on almost every form**, as in Decision 2's runs: the score landscape is flat, so the forms themselves carry little information; only the score and the rules do.
3. The 100,000-step runs aren't converged (the stronger keep values do worse than the weaker ones, which shouldn't happen at the optimum). Longer runs (300,000 steps, keep 0.003 and 0.005, seeds 4–9) follow.
