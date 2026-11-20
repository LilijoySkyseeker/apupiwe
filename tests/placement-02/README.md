# Placement 02: the joint placement rerun under the Placement 1 decision

Question: what do the ~1,457 roots look like when they are placed under the author's Placement 1 decision (design log 2026-11-18)?

- three syllables only for tier 1 (the rarest); every other root has two, the number words included
- **apu** "language" locked as the name
- a keep term, so today's roots move only when moving gains more than the keep penalty
- n + vowel junction risk reported

Everything else is as in `tests/placement-01/` (method table there): the same concept list, model v2 robust objective, weights, hard rules, haplology threshold, C3 tie-break and three-syllable candidate sampling. Proposals only: nothing in `data/` or `docs/` changes until the author reviews the result. **added** marks Claude's choices.

## Method (what changed from placement-01)

| part | source |
|---|---|
| `MAX3_TIER = 1`: a three-syllable form is a candidate only for tier-1 roots | author, 2026-11-18 |
| `LOCKED = {"language"}`: **apu** is fixed, like a loan | author, 2026-11-18 (recommended in the 2026-10-19 handoff) |
| `--keep X`: when a root's form today is still valid, every other form costs X more in J (the same idea as `tests/shortwords-03/rebuild.py --keep`). Today's forms the rules force out pay nothing. | author, 2026-11-18. **added**: X is in J units, swept over 0, 0.03, 0.1 and 0.3 (about 0.1%, 0.3% and 1% of J). placement-01's `keepcheck.py` put the cost of keeping single frequent roots at 0.05% to 2.25% of J. |
| seeds 1 and 2 per keep value, 12 sweeps of coordinate descent from A | placement-01; **added**: two seeds to measure whether the keep term makes the result reproducible (placement-01's seeds agreed on only 14% of forms) |
| n + vowel junction risk (`report.py junction_risk`): for each vowel-initial root X, how close nX is to a real word of the same length, and for each n-initial root nX, how close X is. Robust (worst quarter of variants) and best variant. Reported only, not in the objective. | handoff item 4; junction 1 in `research/notes/confusion-data.md` §3. **added**: no resegmentation rate was found, so it is a ranking, not a probability |
| variant `--no-vbonus` (state names `-nv`): the length term drops its −0.1 for a vowel start, and three-syllable candidates are sampled uniformly instead of half V.CV.CV | **added**: in the start state all 388 three-syllable roots came out vowel-initial. The three-syllable space is nearly empty, so confusion barely separates candidates, and the bonus plus the oversampling decide. Run once, at keep 0.1, for the author to compare |

Commands, from this folder: `direnv exec ../.. python3 place.py medians`, `… place.py start [--no-vbonus]`, `./run.sh` (the keep sweep), `… place.py descend 1 --keep 0.1 --no-vbonus`, `… report.py --keep K [--no-vbonus]`.

## Progress

Resumable as placement-01: every step writes `state/*.json` atomically; rerun the same command.

- [x] medians (`state/medians.json`), A (`state/A.json`), A without the vowel bonus (`state/A-nv.json`)
- [x] keep sweep (`./run.sh`, logs in `logs/`): `report-k{0,0.03,0.1,0.3}.txt`, `forms-k*.tsv`
- [x] no-vowel-bonus run at keep 0.1: `report-nv-k0.1.txt`
- [x] candidate for the author: no vowel bonus, keep 0.03, seeds 1–2 (`state/C-nv-k0.03-*.json`, `report-nv-k0.03.txt`)

## Results

J and R are on the same random baseline as placement-01 (R 1.0 = a random lexicon of the same size; today's 519-word lexicon scores 0.39 against its own baseline). Placement-01's run for comparison: J 27.8 with 663 three-syllable roots, 38.2 with none.

| run | J | R | today's roots moved (104 forced) | seeds agree on a form | near pairs (robust) | vowel-initial roots | junction risk (sum) |
|---|---|---|---|---|---|---|---|
| keep 0 | 30.44 | 0.103 | 336 | (one seed) | 5,451 | 504 | 9.1 |
| keep 0.03 | 32.48 | 0.119 | 135 | 62% | 5,742 | 482 | 10.6 |
| keep 0.1 | 33.53 | 0.128 | 112 | 62% | 5,749 | 487 | 9.7 |
| keep 0.3 | 35.13 | 0.142 | 104 | 70% | 5,729 | 489 | 10.1 |
| **no vowel bonus, keep 0.03 (candidate)** | 33.44* | 0.120 | 136 | 54% | 5,747 | 95 | **7.5** |
| no vowel bonus, keep 0.1 | 34.16* | **0.125** | 113 | (one seed) | 5,752 | **97** | **8.3** |

\* J without the vowel bonus is in a slightly different unit (the length term changed); compare R.

Every run: tier 1 has 402–429 of its 429 roots at three syllables, no other tier has any; unique drift keys, no blocked form, haplology and digit check passed; `juncture.py` fails only on fixed words, as in placement-01 (**denu** "gene" after the digit **de**; the six grammar -n pairs).

Findings:

1. **The keep term works, and 0.03 is the knee.** Keeping every valid root (0.3) costs 15% of J against free placement (0); 0.03 recovers over half of that (J 32.5) while moving only 31 roots that weren't forced, against 232 at keep 0. The seeds now agree on 62% of forms (14% in placement-01).
2. **The −0.1 vowel-start bonus hurts.** With it, almost every three-syllable root is V.CV.CV (401 of 401). Without it (`--no-vbonus`) the robust confusion is lower (R 0.125 vs 0.128 at the same keep), near pairs are about the same (5,752 vs 5,749), the n + vowel junction risk falls by 15%, and vowel-initial roots drop from 487 to 97. The bonus only saves a tenth of a syllable on rare words. Its only source is the code, `tools/build.py` `length()`: `tools/why.py` and a search of docs and research notes find no record of it.
3. **Number words take codas.** Forced off banned syllables (**kefi** starts with **ke**, **mape** with the digit **ma**, **tonen** with **to**), 8, 9 and 10^6 become **manwon**, **enfin**, **munfan**: the ×10 number weight pushes them into the sparse -n region. Two syllables, as decided, but heavy.
4. **Frequent words to look at (keep 0.03):** "can" **lenu → eye** (reads as the English word; also a junction pair with **enye** "bowl"), "come" **obu → eka**, "small" **meli → guti** (MINUS's old form), "big" **kudu → pulu**, "food" **pasu → poso**. Closest frequent near pairs: new/department **duwa~fuwa**, yesterday/coffee **afe~kafe**, true/answer **feko~febo**, above/same **bige~kige**. Worst fixed-word pair still **kilo~kiyo**.

5. **The candidate** (no vowel bonus, keep 0.03; `forms-nv-k0.03.tsv`, `report-nv-k0.03.txt`) moves 32 roots that weren't forced. Frequent ones: "come" **obu → mele**, "can" **lenu → iya**, "small" **meli → nebi**, "food" **pasu → gene** (reads as the English word), "big" **kudu → kulu**, "100" **loki → onwun**.
6. **Number words crowd into won-**: 9 **wonlin**, 10^6 **wonfon**, percent **wonnon**, pair **wonken**, 8 **manwon**, 100 **onwun**, while **wo** is the digit 4. The ×10 weight on any pair with a number word (set for 500 words, placement-01 item 2) drives them into the sparse -n region, where they end up resembling each other and the digit. Question for the author: rescale ×10 for the larger lexicon, or fix these forms by hand.

Scripts consolidated into tools/ on 2026-11-19; the version used here is in git history.
