# Doghouse review of the Apupiwe project (2026-11-19)

Asked for by the author ("it has become complicated"), focusing on rules 0–2. Written by Claude, who built much of what is reviewed, so read it as a self-review checked against the record, not an outside one. Proposals only; nothing here was deleted.

## 0. The goal

Stated (`docs/goal.md`, AGENTS.md): a thought experiment in the best human language, and a real language its author learns and shares.

One level up (a guess, from what the author does): the author enjoys designing it and wants a language they find convincing *and* can use. The two halves pull differently: "best" rewards ever finer design; "learn and share" rewards a language that exists and gets used. In six weeks the project has 406 commits, 199 design-log entries and 59 tests, and one human test (the author reading ten sentences aloud, 2026-10-09). The author has not started learning. Real listener tests won't happen (author, 2026-11-19).

What would change this: if the use half has quietly dropped and the project is now the design experiment itself, most of this review's "reduce" proposals become optional.

## 1. Requirements, traced

Most requirements land on the author: the goal's guarantees (B2, B3, B9, B10), L4 (loans), the 1,500-root base, the culture principle, the sets rule, the freeze conditions. Several hard rules came from reviews or Claude and were approved by the author: drift keys (2026-10-08), the digit and haplology rules, juncture checks, rule 2.12 (accent), the loan-vowel rule, the pronoun-vowel rule, rule J. Each was added for a finding; the pain was **seen** for some (tiwuye / tiwu ye; denu; sen / son; the 8 errors of the first review) and **predicted** for others (haplology, loan vowels, accent mergers), from models or typology.

The requirement with the weakest owner is precision itself: placements compared to three decimals on a mishearing model whose own runs disagree on most forms (seeds agree on 14–62% of forms; layers differ by 1–6%). Nobody can check those differences, and no listener ever will. The requirement "as robust as the model can make it" has no owner beyond "more is better".

## 2. The parts

The central part is the **design machinery**: models, ~12 hard rules, agent pipelines, reviews and per-decision tests that turn every question into a measured, logged decision. It is for the "best" half, and it works: the decisions are mostly sound (the audit agreed with 48 of 51 measurable ones). But it has grown by locally defensible steps (a rule, then a check for the rule, then a test of the check), and it now produces work faster than the author can decide it (22 decisions on 2026-11-19).

| part | serves | asked by | pain without it (seen?) | proposal |
|---|---|---|---|---|
| Mishearing model v2 (48 listener variants, worst-quarter score) | B2 | author, 2026-10-13 | v1 misrated voicing and l/n (seen) | **keep, and freeze**: no more tuning; treat differences under ~5% as ties |
| The placement already done (1,465 roots) | everything | author | — | **keep**; it's finished |
| 11 copies of `place.py`, 6 of `apply.py`, 3 of `rebuild.py` in `tests/` | reruns | nobody; copies were the habit | none: git history keeps every version | **reduce** to one placement tool, one short-word tool, one apply tool in `tools/`, with the rules in one place |
| `tools/words.py` | adding words | Oct design | none now: out of date, and a trap (AGENTS.md warns against it) | **delete**; new words go through the one placement tool |
| `tools/parse.py` | an early example checker | Oct | none: the GF check covers every example; parse.py's 3 failures were never acted on | **delete** (the roadmap already planned it) |
| `tools/build.py` | first lexicon build (2026-10-08) | Oct | none for the builder; `Inventory` is used by everything | **reduce** to the shared `Inventory` |
| `tools/accent.py` reading positions from `tests/shortwords-04/` | rule 2.12 | author | — | **keep**, move the position table into `data/` (a tool shouldn't depend on a test folder) |
| ~12 hard rules for word forms, scattered across tools | B2, B4, B9 | author | seen for some, predicted for others | **keep**, list them in one table (rule, owner, pain seen or predicted); predicted-only rules get an add-back-style trigger to delete |
| Reserved senary forms (`data/senary.tsv`; the placement avoids them) | the senary project | author, 2026-10-09 | none in this language: goal N6 says it isn't tailored to projects that use it | **delete** the reservation; senary adapts to the language |
| The optional precision layer of the grammar (confidence in sixths, three evidentials, logophor, obviative, stance particles, MODMOD, ENDEAR) | B3 | author, from the October tests | interpersonal gaps seen in multilang-01 | **keep**, but untested by any learner: the first use test should include them (rule 3) |
| `tests/` (59 folders, 45 MB, mostly run state and logs) | the record behind decisions | author ("reasoning in the repo") | READMEs are cited by the log; the state files aren't | **reduce**: keep each README and its small results; drop run state and logs (git history keeps them) |
| `research/notes/` (37) | sources for decisions | author | cited | keep |
| `AGENTS.local.md` (56 lines) | agents' notes | — | partly stale (a one-month Codex plan, old file names, superseded rules) | **reduce** to what's still true |
| The design log (199 entries) | "reasoning in the repo" | author | — | keep |
| Per-decision process (full restatement, one at a time) | author's attention | author | — | keep; the new "method decides, author gets a batch" rule is the reduction it needed |

Parts this review would add: one table of the rules, and one command that runs every check (below). Both replace scattered things; neither adds a rule.

## 3. The smallest test

The project's biggest unknown is the half no model measures: can the author learn and use it (B10, and the reason to share it)? Real listeners won't happen, but the author can. Smallest version, soonest: a flashcard deck generated straight from `data/` (the 63 grammar words and the 100 most frequent roots), and a week of writing a few sentences a day, logging every place they got stuck, forgot a word or couldn't say something. That tests learnability, the docs gap and the grammar's optional layer in one go, and it would tell the lesson rebuild what learners actually need. It doesn't wait for the new lessons; the reference is enough to start.

## 4. Optimisations

Flagged: optimising placements and layers on the model score past what can be verified (keep sweeps, seed sweeps, three-decimal comparisons). The measure is fine; its resolution isn't. Stop at "within ~5% is a tie" and prefer fewer changes.

## 5. What became permanent

Six checks (`spec.py check`, `gf_check.py`, `accent.py`, `juncture.py`, `check.py`, the offensive screen) are each "run after any change": that relies on an agent remembering, and today several stale items slipped through (wi-fi, old compounds, a word-sequence clash). Make it impossible: **one command** that runs them all, run automatically by the placement and apply tools at the end of every change. Delete `parse.py` from that set.

## The one question

Is "a language the author learns and uses" still half the goal? If yes, the next step is a week of using it, not more design; the machinery has done its job and should be frozen and reduced. If no, the design can go on, and the reductions above are housekeeping.
