# Placement 03: the placement with all of the author's settings

Question: the final candidate forms for the ~1,457 roots, under every decision so far (design log 2026-11-18): three syllables only for tier 1; **apu** locked; no vowel-start length bonus; keep term 0.03; number words weighted ×30 against each other and at the ordinary weight against everything else.

Method: `tests/placement-02/` (and its parent, `tests/placement-01/`), with one change in `place.py` `weights()`: number–number pairs ×30 instead of ×10 for any pair with a number word. Run: `./run.sh` (medians, start without the vowel bonus, seeds 1 and 2 at `--keep 0.03 --no-vbonus`, report). Since `tools/build.py` now has no vowel bonus, `--no-vbonus` only switches off the oversampling of V.CV.CV candidates.

## Progress

- [x] `./run.sh` (logs in `logs/`): `report-nv-k0.03.txt`, `forms-nv-k0.03.tsv` (seed 2, lowest J)
- [x] results below

## Results

| | placement-02 candidate (×10 any number pair) | **placement-03** |
|---|---|---|
| J / R | 33.44 / 0.120 | 31.74 / 0.133 (different weights, so not directly comparable) |
| today's roots moved (104 forced) | 136 | **122** (18 unforced) |
| seeds agree on a form | 54% | 60% |
| near pairs (robust) | 5,747 | 5,639 |
| vowel-initial roots | 95 | 100 |
| n + vowel junction risk (sum) | 7.5 | 7.8 |
| B2 margin, roots | 0.00% | 0.00% |

Checks as before: tier 1 has 402 of 429 at three syllables, other tiers none; haplology and digit check passed; `juncture.py` fails only on fixed words (**denu** after **de**; the six grammar -n pairs). 1,099 forms differ from placement-02's candidate, almost all of them new roots.

**Number words** are ordinary two-syllable forms again, and every one that had a form keeps it: 6 **ufo**, 7 **oma**, 100 **loki**, 1000 **munno**, 10 **yawu**, POINT **mimi**, MINUS **guti**, POWER **unun**, 10^9 **siwin**. Forced moves: 8 **kefi → pepe**, 9 **mape → tuli**, 10^6 **tonen → tiya**. New: pair **lanye**, average **fonton**, sum **nayon**, amount **wiyun**, rate **teyupu** (tier 1), percent **lonwon**. The won- cluster is gone.

**Unforced moves (18):** can **lenu → nebi** (tier 5), many **feli → fefa**, big **kudu → tugu** (tier 4); use **bone → fone**, start **tuko → diye**, stand **kolu → yako**, smell **kanko → fopan**, sit **goyu → doyu**, above **bige → fide** (tier 3); wind, turn, tool, strong, star, sea, narrow, horse, back (tier 2).

**Near pairs among frequent words:** yesterday/coffee **afe~kafe** (loan), stop/salty **bamo~fano**, true/answer **feko~febo**, need/MINUS **wupi~guti**, form/perfect **sisa~sita**, film/base **wabi~wati**. Closest antonyms: tell/ask **iko~mido**, fast/slow **yobe~gake**, happy/sad **sogi~bayi**; all far below the near-pair threshold.

## Applied (2026-11-18)

The forms above are in the repo (design log "Placement final"). `apply.py` did it and can be rerun; `map.tsv` is the old → new map (128 forms: the 122 moved roots, phone **liga → doni** among them, and the six former loans hour, minute, second, photo, degree, police, now roots **yiwo yuku dati silu yinse dope**).

- **Data:** `data/lexicon.tsv` 519 → 1,555 rows (1,457 roots, 81 loans, 17 operators); `numbers.tsv` (8 **pepe**, 9 **tuli**, 10^6 **tiya**); `compounds.tsv` (24 of 58 phrases); `antonyms.tsv` 154 → 196 pairs (the concept list's antonym column, kept 2026-10-16); glosses follow the concept list (nail, key). `roles.tsv` 490 → 1,520: the 1,030 new roots were classified by a helper agent following the existing rows' conventions (`roles-new.tsv`; its hand decisions as word lists in `roles_make.py`; a random sample of 45 checked by Claude; its 40 least certain rows are mostly noun/verb-ambiguous glosses such as birth, plan, record, judge, and ambitransitive verbs).
- **Text:** reference (101 spans), lessons (107), why, rationale, vocabulary-method, formal-grammar, site/index, README's example (also fixed old short words **kon te** → **pe ma**, missed in the short-word apply), UDHR translation (289 tokens) and page, `grammar/intended.tsv`, GF literals and comments, `tools/parse.py` comments, `tools/gf_lexicon.py` (RESULT **tula**, God **dakuwu**, hour/minute/second no longer loans). The reference and lesson now say hours, minutes and seconds have their own words instead of "are borrowed".
- **Not changed (history):** design log, roadmap entries, research, other tests, `vocabulary-plan.md`, `number-base.md`, `measurement.md` (senary, outside the core), `grammar/QUESTIONS.md` (resolved questions). GF function names **Kefi**/**Mape** for 8 and 9 keep their old names; only their strings changed.
- **Checks:** `spec.py build`, `check`, `lessons` (reviewed: only forms changed, plus the hour wording; `--ack`, 156 rules); `gf_lexicon.py` (1,520 roots); `gf_check.py` 269 examples, 228 parse with the intended reading, 111 precise, 33 citations, 8 outside; `tools/check.py` no unknown words except names and history; no form `offensive.blocked`; `confusion2.py` self-check. `tools/parse.py` (the older template checker) has the same 3 no-parses and 1 ambiguity as before the change (6.1.2, 9.2.5, 11.1; 5.4.4). `juncture.py` reports only the known fixed-word problems (**denu** after **de**; the six grammar -n pairs; roadmap).

Scripts consolidated into tools/ on 2026-11-19; the version used here is in git history.
