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


### Knock-on, and the runs that count

The runs above ignored two things, found before choosing: (1) changing a digit breaks the roots placed around **mu ni sa de wo ma** (no root starts with a digit's syllable), and (2) changing a grammar word that often precedes content words breaks the haplology rule for the roots that start with its new syllable. `knock.py` measures both: the 22-word layer above (seed 5, keep 0.005) would have made 89 roots illegal. So the final runs lock the digits and add hard rule H6: the 22 haplology words (`tests/placement-03/bigrams.tsv`, >= 10 bigrams before a content word) may take only today's haplology syllables or, at a cost of 0.005 per displaced root (`SW_ROOT_COST`), syllables that start at most 6 roots (`SW_HAPLO_EXTRA=6`). All 22 share positions with each other, and their syllables include **gen**/**yen** and **ke**/**se**, so without extra syllables the rule can't be met. The start is repaired by min-conflicts (`legal_start`), then annealed at T0 0.02, 300,000 steps.

| run (digits locked, H6) | words changed | robust | roots displaced |
|---|---|---|---|
| keep 0.003, seeds 4–9 | 41 / 34 / 32 / 34 / 22 / 36 | 0.283 / 0.291 / 0.313 / 0.314 / 0.312 / 0.288 | |
| keep 0.005, seeds 4–9 | 24 / 25 / 30 / 28 / **27** / 26 | 0.320 / 0.320 / 0.315 / 0.320 / **0.291** / 0.303 | 14 (seed 8) |

**Chosen (author, 2026-11-19): keep 0.005 seed 8** (`runs/soft-h6-k0.005-8.tsv`): 27 words change, robust 0.304 → 0.291, offensive matches 34 → 35, one-feature same-position pairs 15 → 22 (counted in the robust score), 14 roots displaced. Applied with `apply/apply.py` and `apply/map.tsv` (27 grammar forms and the 18 re-placed roots of `tests/placement-04/`), one pass per file because the map has chains (**nun → sen** while **yen → nun**). Lesson 6 ("little words that look like English") was rebuilt by hand from the new forms; the lesson 1 sound table and lesson 5's warning about "you" were fixed by hand; spans with names after **fo** or loans were checked by hand. Checks: `spec.py check` and `lessons` (reviewed, `--ack`), `gf_check.py` 269 examples (228 with the intended reading), `tools/check.py` (names only), `parse.py` (the same 3 no-parses and 1 ambiguity as before), `juncture.py` (five grammar -n pairs, from six; roadmap), `tools/accent.py` passes, no form `offensive.blocked`.