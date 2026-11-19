# Ladder audit 01: which word decisions were argued where a rung could measure (2026-11-19)

Question: since the ladders were adopted (2026-10-12), which design-log decisions on a word boundary (one concept or two) or a form route (standard form / loan / built phrase / root) were settled by argument or judgement where a rung could have measured the answer, and would measuring change anything? Follows the author's rule "Let the method decide what it can" (AGENTS.md, 2026-11-19). Report only: nothing else in the repo changed.

## Method

- Scope: every `docs/design-log.md` entry from "Word-decision ladders (2026-10-12)" to today that decides a boundary or a form route. Skipped as grammar, sound or tool decisions: le mu, dife/mena, kon bo, kiyo/kiyu, through, rates with **mesun**, fractions, feko/ok, the endearment word, speech-act words, placement and accent entries, pronouns. Process and rule entries (how the coverage is measured, phrase line, stop rule, "modern life") are rules, not word decisions, so they're listed only where a word decision rests on them.
- For each decision: (1) the rung that decided it, by the entry's own reasoning; (2) whether an earlier rung, or rung 4's family-balanced rate, could have decided it with data; (3) where rung 4 applies and CLICS4 has both concepts, the rate.
- Rates: CLICS4 v1.0 (Zenodo 19608447, kept outside the repo), `/home/agent/work/scratch/clics4/rates_audit01.py` (a copy of `tests/ladder-02/rates_cause.py` with new pairs; output `/home/agent/work/scratch/clics4/rates-audit01.tsv`). Family-balanced percentage of languages using one segment string for both concepts, 95% bootstrap range over families (2,000 resamples). Figures quoted are the "no copies" rows (forms whose source item was a combined concept dropped), as in balance-02 and deeplayer-02; where "all forms" differs a lot, both are given.
- Already measured, not redone: balance-02 (moon/month, day/daytime, hear/listen, take/get, arm/hand, ghost/spirit, ghost/soul, leg/foot), deeplayer-02 (the 17 WOLD pairs), coverage-02 and deeplayer-01/02 (root routes by frequency and WOLD family counts), ladder-02 (other/remain, cause/make). Word/language was rerun as a check: 50.2% (40–60), the figure the log cites.
- **Disagrees** means strictly: the decision lumped and the rate's whole bootstrap range is below 50%, or the decision split and the whole range is above 50%, *and* no higher rung (1–3) decided it with evidence. A rate on the other side of 50 under a higher rung that did decide is not a disagreement. Fewer than ~10 families overlapping is reported as too thin.

## Results

| Date | Decision | How it was decided | Could a rung have measured it? | Measured result | Verdict |
|---|---|---|---|---|---|
| 10-13 | Loans re-formed from the panel; metric units one set | L2 rung 2, panel (17–19 of 20) | Already measured | panel | agrees |
| 10-13 | Currencies loans; dollar **dolalu** | L2 rung 2, panel (13 of 19 keep the r) | Already measured | panel | agrees |
| 10-13 | Seven failing loans become phrases (train, licence, electricity, hospital, bicycle, contact, percent) | L2 rung 2 fail, then rung 3 built; partly superseded by the frequency rule (train, hospital, bicycle, electricity, percent got roots) | Already measured (panel, then ranks) | panel; ranks | agrees |
| 10-13 | Moon / month split | L1 rung 1 (calendar month) + rung 3 (5 of 12 lumpers separate) | Rung 4 measured, but rung 1 comes first | 69.9% (61–78), balance-02 | agrees (rung 1 decides before rung 4) |
| 10-13 | Religion: shared concepts core, tradition words borrowed; religion a root | Culture principle (agreed rule) + frequency; later re-checked by rank | Rung 5 frequency, done 10-13 and 10-13 audit | ranks (religion 350) | agrees |
| 10-13 | soul, ghost, miracle, devil core roots, apart from spirit | Rung 5 frequency + panel counts | Rung 4 for the boundaries | GHOST/SOUL 22.0%, GHOST/SPIRIT 7.0% (balance-02); new: DEMON/GHOST 15.0% (8–24), 53 families; SOUL/SPIRIT 0.6%, only 2 families | agrees; soul/spirit too thin |
| 10-13 | devil = demon = evil spirit, one concept | Argument (panel examples) | CLICS has DEMON only | — | no data |
| 10-13 | Word / language split | L1 rung 3 (all 3 lumpers use a separate everyday word) | Rung 4 measured: a coin flip, so rung 3 decides | 50.2% (40–60), rerun matches | agrees (rung 4 undecided) |
| 10-13 | Loan panel rules; 62 coverage loans, 43 native roots | L2 rung 2, panel | Already measured | panel | agrees |
| 10-13 | **nume** "live" also "life" (lump; **pata** removed) | Argument: "one concept in two roles" | Rung 4: BE ALIVE / LIFE | **18.0% (7–31), 10 of 38 families**; all forms 71.4% (63–80), inflated by the source item "BE ALIVE OR LIFE" | **disagrees** (see below) |
| 10-13 | protect / keep split (**kuwi**) | Rung 3 by eye (0 of 20 lump) | Rung 4 | PROTECT/KEEP 3.9% (1–9), 19 fam.; DEFEND/KEEP 0.5%; GUARD/KEEP 6.3% | agrees |
| 10-13 | ask a question / request split (**mido**) | Rung 3 + frequency | Rung 4 | 21.2% (14–29), 74 fam. | agrees |
| 10-13 | misplace / lose a contest split (**agi**) | Argument ("most languages split") | CLICS has no LOSE concepts | — | no data |
| 10-13 | day (24 h) / daytime split | L1 rung 1 (standard) | Measured in balance-02 | 52.9% (35–70) | agrees (rung 1 decides) |
| 10-13 | law / rule split (reverses 10-10 lump) | Rung 3 (ranks; lumpers separate) | Rung 4 | 0.0% (0–0), 36 fam. | agrees |
| 10-13 | need narrowed; "should" is **fon** | Argument | CLICS has no SHOULD | — | no data |
| 10-13 | power / physical strength split (**lula** / **konke**) | Argument | Rung 4 | POWER/STRENGTH 5.0% (0–15), 20 fam.; POWERFUL/STRONG 35.7% (21–51), 21 fam. (all forms 84.4%, combined items) | agrees |
| 10-13 | leg / foot kept apart | Rung 3 (credited); really rung 4 (balance-02) | Measured | 23.4% (17–30) | agrees |
| 10-13 | tree / wood kept apart | Rung 3 ("modern use keeps them apart"; balance-01: 4 of 5 lumpers separate) | Rung 4: a coin flip | 50.0% (41–59), 85 fam. | agrees (rung 4 undecided) |
| 10-13 | hear/listen, take/get, arm/hand two roots | Credited to rung 3; really rung 4 (balance-02 correction) | Measured | 45.7%, 23.2%, 27.6% | agrees |
| 10-13 | see / look two roots | Credited to rung 3 (20–50% band deleted) | Rung 4 | 23.9% (17–32), 84 fam. | agrees |
| 10-13 | paper / book two roots | as above | Rung 4 | 39.3% (27–51), 56 fam. | agrees |
| 10-13 | land / country two roots | as above | Rung 4 | 42.4% (31–54), 53 fam. | agrees (near the line) |
| 10-13 | sacred, bless to phrases; later bless, sin, hell, heaven, holy person roots | Rung 5 frequency (merged-label ranks) | Already measured | ranks 522–1,138 | agrees |
| 10-13 | "wonder" root; miracle built from it | Method §3b (observation, not cause): argument in the spirit of L1 rung 2 | No CLICS concept | — | no data |
| 10-13 | First-word concepts filtered (165 roots, 24 loans, 20 phrases; boy/girl built) | Frequency or deep-layer test; boy/girl by the gender rule (author kept against frequency) | Already measured | wordbank-final.tsv | agrees |
| 10-13 | Percent a root | Rung 5 (rank 436) + panel fail | Already measured | rank, panel | agrees |
| 10-13 | **kilo** for kilogram | L2 rung 2, short-form rule (12 languages, 6 regions) | Already measured | panel | agrees |
| 10-13 | always, often, sometimes, never, later roots | Rung 5 frequency | Already measured | ranks 47–1,574 | agrees |
| 10-13 | email passes; police native root; rupee **lupiya** | L2 rung 2 panel rules | Already measured | panel | agrees |
| 10-15 | ICAO alphabet for spelling aloud | L2 rung 1, standard | Decided by the rung | — | agrees |
| 10-15 | Symbol names: **komu**, **asutagu**; others described | L2 rung 2 panel, then rung 3 | Already measured | panel | agrees |
| 10-15 | No **mama** loan; **mole** stays | L2 rung 2 (thin deciding column fails) + meaning clashes | Already measured | 13/20, thin | agrees |
| 10-15 | here / there roots | Rung 5 (ranks 6, 39) + deep layer | Already measured | ranks | agrees |
| 10-15 | Large numbers stay native, not SI prefixes | Argument (kilo = kilogram clash; no language counts with kilo) | L2 rung 1 doesn't fit: SI prefixes are multipliers, not counting words (rung 1 scope note) | — | no data (no rung measures it) |
| 10-15 | tea an invented root | Panel family split + adaptation clash with digit **te** | Panel already run | — | agrees |
| 10-15 | 51 added concepts (hate, forgive …), holy a root | Rung 5, corrected ranking (balance-02) | Already measured | ranks | agrees |
| 10-15 | Persian/Turkish overrides hold | Rung 1 or rung 4 (balance-02) | Measured | see balance-02 | agrees |
| 10-16 | "parent" a neutral root; mother, father stay roots | L1 rung 2 (C4) for parent; author exception to "gendered person words stay built" for mother/father (C1 cost) | Not a lump question; frequency would support mother/father as roots | — | no data (rung 2 decided) |
| 10-16 | "lie, tell an untruth" a root | Author, with parent | Deep layer: LIE (MISLEAD) in 71 CLICS families | — | agrees |
| 10-16 | Breakfast, lunch, dinner roots | Argument: C1 cost and set consistency | Rung 5: lunch rank 1,425 (past the 1,342 stop), dinner unranked; deep layer: BREAKFAST 46, LUNCH 47, DINNER (SUPPER) 38 CLICS families | — | agrees on the deep-layer route; not measured as such |
| 10-16 | ceiling / roof split | Argument ("most languages split") | No CEILING in CLICS | — | no data |
| 10-16 | infection a root apart from **simi** "sick" | Argument | No INFECTION in CLICS | — | no data |
| 10-16 | attitude one root; opinion a phrase | Argument | No CLICS concepts | — | no data |
| 10-16 | worthy one root; welfare apart from health; pattern one root; urgent a root | Argument | No CLICS concepts | — | no data |
| 10-16 | coal one root; charcoal "wood + coal" | Argument | Rung 4 COAL/CHARCOAL | 1.5%, 1 family | too thin |
| 10-16 | depend apart from **gewan** "trust" | Argument | No CLICS concepts | — | no data |
| 10-16 | deny / refuse split | Argument | Rung 4 | 21.3% (11–34), 39 fam. | agrees |
| 10-16 | comfortable apart from pleasant | Argument | No CLICS concepts | — | no data |
| 10-16 | wild without "savage" | L1 rung 2 (C4) | Decided by the rung | — | agrees |
| 10-16 | common: "ordinary" root, "shared" phrase | Argument | No COMMON in CLICS | — | no data |
| 10-16 | status one root; partner one neutral root | Argument | No CLICS pair | — | no data |
| 10-16 | environment apart from nature | Argument | No CLICS concepts | — | no data |
| 10-16 | destroy apart from **alun** "break" | Argument | Rung 4 | DESTROY/BREAK (BREAKING) 4.6% (1–9), 68 fam. (all forms; no-copies row has 1 family); DESTROY/BREAK (CLEAVE) 17.8% (6–33), 21 fam. | agrees |
| 10-16 | **accuse / blame one root** | Argument ("lump in many languages", Russian and Mandarin examples) | **Rung 4** | **22.2% (12–34), 14 of 43 families** | **disagrees** (see below) |
| 10-16 | warm apart from **tikun** "hot" | Argument (coverage-02 named "lump rate" but none was run) | Rung 4 | 16.7% (10–24), 75 fam. | agrees |
| 10-16 | celebrate a root; include = contain one root; achieve apart from **wonku** "reach" | Argument | No CLICS pairs | — | no data |
| 10-16 | WOLD deep-layer roots (51 strong + 24 borderline, then 20 more) | Deep-layer test, WOLD family counts (≥15 of 24) | Already measured | deeplayer-01 | agrees |
| 10-16 | Cassava, millet roots; camel culture-bound | Culture principle (argued: staple across regions) | No rung measures "shared across cultures" | — | no data |
| 10-16 | Young and sexed animals built | B7 + gender rule (agreed rule) | Rule decides | — | agrees |
| 10-16 | blind, deaf, mute all roots | Argument (set parity) | Deep layer: BLIND 84, DEAF 79, MUTE 56 CLICS families | — | agrees (deep-layer route) |
| 10-16 | order/command a root; relative, spider, shave, fish, herd roots | Rank 76; phrase line; deep layer (judged) | Rank and phrase line already applied | — | agrees |
| 10-16 | Drops: day/month names, titles, specialist terms | Culture principle, specialist rule | No rung measures it | — | no data |
| 10-16 | WOLD boundaries: 16 splits, claw/nail one root; roast/fry split | Rung 4 (deeplayer-02) | Measured | e.g. claw/nail 53.9% (44–63), roast/fry 3.0% (5 fam.) | agrees |
| 10-16 | "defeat" merged into "lose (a contest)" | Argument | No LOSE concept in CLICS | — | no data |
| 10-16 | Older phrases under the phrase line; school subjects roots; civic offices kept, military ranks dropped | Phrase line (rule); culture principle (argued) | Rule applied | — | agrees |
| 10-16 | summer / winter built ("season + hot/cold"), no roots | Argument: set parity across climates | **Rung 5 and the phrase line**: ranks 814, 872 (inside the 1,342 stop); phrase 4 syllables, above the 3-syllable line. sets.md says so itself | ranks | **rule says root** (not a rung-4 case; see below) |
| 10-16 | dusk a root to match dawn | Argument: set parity | Rung 5: dusk rank 5,628, 3 languages (balance-02 list); no DUSK in CLICS for a deep-layer count | rank | frequency doesn't support it; deep layer unchecked |
| 10-16 | pity = compassion one root; envy = jealousy one root; cool a root | Argument (sets pass) | CLICS has PITY and ENVY only, no COOL | — | no data |
| 10-16 | **spicy = tikun "hot"** | Argument: "as the decided chili phrase already uses it" | **Rung 4** | **HOT/SPICY 0.0% (0–0), 0 of 179 varieties in 7 families** | **disagrees, thin** (see below) |
| 10-16 | pound (mortar) apart from crush | Argument | Rung 4 | POUND/CRUSH 5.8%, 2 families; POUND/STRIKE 11.0% (deeplayer-02) | too thin (direction agrees) |
| 10-16 | supper = dinner | Argument | Concepticon itself merges them (DINNER (SUPPER)) | — | agrees |
| 11-19 | Oxygen loan **okusiden** | L2 rung 2 panel (14 of 20, 5 regions) | Already measured | panel | agrees |
| 11-19 | Planet, temperature, useless, export, import, earthquake roots | Phrase line, compound clause deleted (rule) | Rule applied | — | agrees |
| 11-19 | Mass a root (tier 1); weight is **gogo** "heavy" | L1 rung 2 (C4) for mass; weight = heavy by argument ("what speakers feel") | Rung 4 only by proxy: CLICS has HEAVY and the verb WEIGH, no noun WEIGHT | HEAVY/WEIGH 6.0% (0–13), 53 fam. | proxy disagrees; not counted (see below) |
| 11-19 | other / remain; cause / make; miss, degree, sign names | Rung 4 (ladder-02) | Measured | 0.0%, 1.8% | agrees |

Counts (76 rows; some rows group several pairs decided the same way):

- **Agrees: 48.** 12 of them newly measured here by rung 4 (protect/keep, ask/request, law/rule, power/strength, see/look, paper/book, land/country, demon/ghost, deny/refuse, destroy/break, warm/hot, and word/language rerun as a check); the other 36 were already measured by a rung (panel, rank, WOLD counts, a cited rate) or follow directly from a rung or agreed rule.
- **Disagrees (strict, rung 4): 3** (live/life, accuse/blame, spicy/hot; spicy/hot on thin data).
- **Agreed rule says otherwise, not rung 4: 1** (summer/winter); plus 1 frequency-only doubt (dusk) and 1 proxy (weight/heavy), not counted as disagreements.
- **No data or too thin: 22** (CLICS lacks the concept, or fewer than 10 families overlap).
- Coin flips (rung 4 undecided, rung 3 decided): word/language 50.2% (40–60) and tree/wood 50.0% (41–59). Near the line but on the decided side: land/country 42.4% (31–54), paper/book 39.3% (27–51).

## Where measuring disagrees

1. **nume "live" also means "life" (2026-10-13, "The remaining boundary cases").** Decided by argument: "one concept in two roles; any root can be a thing or an action". Rung 4: BE ALIVE / LIFE lump in **18.0% (7–31)**, 10 of 38 families, so rung 4 says two words. With combined source items kept the rate is 71.4%, but nearly all of that comes from 495 forms recorded under one item, "BE ALIVE OR LIFE", the same inflation that made roast/fry look 94% one word (deeplayer-02). Caveat for the author: CLICS compares exact strings, and many languages derive the noun from the verb (*vivir*/*vida*), which a role-free root covers by design; whether rung 4 applies to a noun/verb pair at all is a rule question, not a data one. Side note outside the audit's dates: **nume** also lumps "dwell" (2026-10-10 English-leak fix), and DWELL / BE ALIVE lump in only 32.2% (19–46), 18 of 37 families; DWELL / LIFE 3.4% (0–10).
2. **accuse / blame one root (2026-10-16, "Boundaries for the 51 additions").** Decided by judgement: coverage-02 wrote "accuse and blame lump in many languages", citing Russian and Mandarin. Rung 4: ACCUSE / BLAME lump in **22.2% (12–34)**, 14 of 43 families, so rung 4 says two words. No higher rung was applied: rung 3 can only add a split, so it can't rescue a lump. This is the cleanest disagreement: both concepts are well covered and the senses match.
3. **spicy = tikun "hot" (2026-10-16, the sets pass).** Decided by argument: it's what the already-decided chili phrase uses (add-back trigger: a test where "hot food" is read as temperature). Rung 4: HOT / SPICY lump in **0.0% (0–0)**: none of 179 varieties in 7 families uses one word. Thin: SPICY is in only 8 CLICS families, nearly all in mainland East and Southeast Asia (Sino-Tibetan, Hmong-Mien, Tai-Kadai), so the regional spread is poor. It agrees with what the panel's big languages do (Mandarin 辣/热, Japanese *karai*/*atsui*, Hindi *tīkhā*/*garam*, Spanish *picante*/*caliente*; from memory, not measured), and points to an English leak. Before acting, a panel check (balance-01 style) would settle it.

Not strict disagreements, but where measuring would likely change the answer:

- **summer / winter built (2026-10-16, sets pass).** Not a rung-4 question: the agreed frequency rule and the phrase line say roots (ranks 814 and 872, inside the 1,342 stop; the phrase **muyi tikun** is 4 syllables, over the 3-syllable line). `tests/conceptlist-01/sets.md` notes this and chose set parity across climates. Under "Let the method decide", that override is the author's to confirm or reverse.
- **dusk a root (2026-10-16, sets pass).** Admitted for parity with dawn; its frequency rank is 5,628 (3 languages), far outside the line. It could still pass the deep-layer test (named across many families), which hasn't been run for it.
- **weight = gogo "heavy" (2026-11-19).** The C4 half (mass its own root) was decided by rung 2 and stands. The everyday half (weight is "heavy" used as a noun, including "it weighs 5 kg") was argued. The only measurable proxy, HEAVY / WEIGH (the verb), lumps in 6.0% (0–13) of 53 families. CLICS has no noun WEIGHT, so this doesn't test the decision directly.

## Files

- `/home/agent/work/scratch/clics4/rates_audit01.py`, `/home/agent/work/scratch/clics4/rates-audit01.tsv`: the script and its output (outside the repo, like ladder-02's).
