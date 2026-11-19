# The four standard-word loan candidates: planet, temperature, oxygen, mass (loans-02)

Task: `PROMPT.md`. The concept list left these four as "loan candidate" (author, 2026-10-16: "standard words (planet, temperature, oxygen, mass) go through the loan panel"; `tests/conceptlist-01/concepts.tsv`). Proposals only: nothing outside this folder changed, nothing committed. Choices of mine are marked **(added)**.

## Progress

- [x] 1 Wiktionary tables fetched for the right sense blocks (`loanwork/wikt-raw.txt`)
- [x] 2 column judgments with sources: subs, Leipzig, kaikki (`loanwork/panel.txt`)
- [x] 3 verdicts, median, adapted form, collisions, offensive and accent checks (`loans.py` → `loans.tsv`)
- [x] 4 standards checked (rung 1), fallbacks for the failures
- [x] 5 README write-up

Rerun from the repo root (a few seconds): `direnv exec . python3 tests/loans-02/loans.py`

## Question

Does the world share a form for each of the four (goal L4, ladder 2 rung 2)? If so, what is the adapted form, and does it clash with anything? If not, does the concept get a root or a phrase?

## Method

As `tests/deeplayer-02/` did it, unchanged:

- **Panel:** the 20 languages, from the English Wiktionary translation tables, fetched 2026-11-19 with `tests/lexicon-ladder-01/panel.py`. Sense blocks: planet "rocky or gaseous spherical bodies orbiting the Sun" (plus the "similar body" and "seven major bodies" blocks for missing columns), temperature "a measure of cold or heat", oxygen "chemical element", mass "physics: quantity of matter which a body contains".
- **Marks and sources:** y / b / n / u per column, each with its source (Wt, We from the kaikki dumps, OpenSubtitles 50k counts, Leipzig 2017 counts). A memory-only column doesn't count. The five-times rival rule applies (turned planet n in tr and bn, temperature n in id, oxygen n in qu). The shape rule is the source-shape reading. All of this is in `panel.txt`'s header.
- **Pass rule:** at least 12 of 20 languages across at least 5 of the 7 regions (author, 2026-10-15).
- **For the pass:** the median pronunciation by position, adapted with `tools/names.py`. Then four checks:
  - collisions against `data/lexicon.tsv`, `grammar.tsv`, `numbers.tsv` and the 11.5 spelling words;
  - `tools/offensive.py`: `blocked` must be false, and `matches` is reported;
  - `tools/accent.py` `neighbours()` against the same forms (rule 2.12).
- **For a failure:** all four are on the root list (concepts.tsv tiers 1–2, ranks 621–1227), so each gets a root unless the phrase line allows a phrase. The phrase line allows one only when it is 3 syllables or fewer, or when it is the world's usual compound.

## Results (`loans.tsv`)

| Concept | Count | Regions | Verdict | Median | Adapted | Collisions / offensive / accent | Recommendation |
|---|---|---|---|---|---|---|---|
| oxygen | 14/20 | 5 (SEA SA WA EU SSA) | **pass** (no column decides) | [oksidʒen] | ***okusiden*** | no collision; `blocked` false, `matches` false; accent neighbours *okukiden*, *okusilen* not in use | loan **okusiden** |
| planet | 6/20 | 3 (SEA EU SSA) | fail | [planeta] | – | – | phrase **segin kobi** "moving star" (the world's usual compound) |
| temperature | 4/20 | 2 (SEA EU) | fail | [temperatura] | – | – | phrase **kote pi tikun** "level of heat" (the world's usual compound) |
| mass | 4/20 | 2 (SEA EU) | fail | [masa] | – | – | **root** "mass", or widen **gogo** "heavy" (author's call) |

How each one came out:

- **oxygen passes cleanly.**
  - The 14 columns are vi th id tl hi bn ta fa ar tr es fr sw yo. The Sino and Russian calques (氧, 酸素, 산소, кислород) and Quechua *muksichaq* don't count. Hausa has no data.
  - Without any single column it still has 13 across 5 regions, so the thin columns (tl with no subtitle count, ta with 6 tokens, yo with 10) don't decide.
  - The median by position is in `panel.txt`. The only close vote was the third consonant: dʒ in 7 columns, ʒ in 3.
- **planet fails.**
  - Six columns share *planeta/planet*: id tl ru es fr yo. Turkish *planet* loses to *gezegen* (6.2×), and Bengali to *graha* (8.3×).
  - The world's build is "moving/wandering star": zh 行星, ja 惑星, ko 행성, vi *hành tinh*, ar *kawkab sayyār*, fa *sayyâre*, tr *gezegen*, sw *sayari*, qu *puriq quyllur* (plus id *bintang siarah*, listed second). That is 9 or more languages in EA, SEA, WA, SSA and AM, which makes it the world's usual compound.
  - It's also what's seen: a light in the sky like a star that moves against the others. So it's a description, not a wrong belief (C4), even though a planet isn't a star.
  - Shape: **segin kobi** "star moving", with a describing word after the noun (5.2.1). It has 4 syllables.
- **temperature fails.**
  - Only tl ru es fr borrow it. Indonesian *temperatur* loses to *suhu* (7.8×), and no South Asian subtitle list has the spoken English word.
  - The world's build is heat/warmth + degree/measure/level/state: zh ja ko vi th hi bn ta fa ar sw, 11 languages in 5 regions. That is the usual compound.
  - Shape: **kote pi tikun** "level of heat", 5 syllables. The cost: **tikun** is also "spicy" (sets pass), so the phrase can also read "how spicy". Context nearly always settles it. **kote pi kukedo** "level of warmth" (as zh 温度) avoids that, but runs to 6 syllables.
- **mass fails, and has no world compound.**
  - Only id ru es fr borrow *masa/massa*.
  - The calques split two ways: "substance/block amount" (zh ja ko vi hi, 2 regions) and "lump" (ar *kutla*, tr *kütle*).
  - Everyday speech in tl bn ta sw ha qu uses the "weight" word, and Wiktionary lists ja *omosa* and ar *wazn* too.
  - So no phrase qualifies (**disin pi wiyun** "amount of substance" would be 5 syllables and only one region group's build). That leaves a root, or the lump with **gogo** (question 3).

## Standards (ladder 1 rung 1, ladder 2 rung 1; goal L3)

- **oxygen.** IUPAC decides the element and its symbol **O**. Its official names are in English, used as a lingua franca ("international English", per Wikipedia's *Chemical element* article on IUPAC naming; I couldn't fetch the IUPAC paper itself, since the publisher refused). National names stay in use (Sauerstoff, кислород, 酸素).
  - So the standard fixes the concept and a written symbol. Its spoken name is English *oxygen* [ɒksɪdʒən] → **okusidan**, which differs from the panel's **okusiden** only in the last vowel. **okusidan** also has no collision, no offensive match, and no accent neighbour in use.
  - Ladder 2 puts rung 1 above the panel. But the author sent these words to the panel (2026-10-16), and design log l.499 reads loans as "the form most languages share". So I recommend the panel median and flag the choice (question 1).
- **planet.** IAU Resolution B5 (2006) fixes the boundary for the Solar System (eight planets; Pluto a dwarf planet), and the IAU has a working definition for exoplanets. That settles ladder 1 (the sense is "planet" by the IAU's line). The IAU works in English and French, so no spoken form is international. The standard doesn't bear on the form.
- **temperature, mass.** Both are SI base quantities (thermodynamic temperature, unit kelvin; mass, unit kilogram) in ISO 80000 and the SI Brochure. Their quantity names are given in English and French only, so again no international spoken form. The lexicon already has the SI unit loans (**kilogulamu**, **kilo**, **gulamu**) and **yinse** "degree (°)".
  - For mass, the standard bears on the boundary. SI's mass is what everyday "weight in kilograms" measures, and weight in SI is a force.
  - So lumping mass with everyday heaviness matches the standard's everyday concept. Only the physicist's "weight (force)" falls outside, and that is "force of gravity".
  - Under rung 1's scope (author, 2026-10-13), that argues for, not against, the **gogo** option.

## Questions for the author

1. **Oxygen: the panel median or IUPAC's English name?**
   - **Problem:** ladder 2 puts "an international standard form" above the panel. IUPAC's official name is English *oxygen*. The panel's median is [oksidʒen].
   - **Example:** **okusiden** (panel) vs **okusidan** (IUPAC English). Both are clean on collisions, offensive and accent checks.
   - **Options:**
     - (a) **okusiden**: the world's median, the author's 2026-10-16 routing, and design log l.499's "form most languages share".
     - (b) **okusidan**: rung 1 read literally. The cost is English becoming the source form, which the rationale (l.169) records as a cost to avoid.
   - **Recommendation:** (a). The symbol O is the real international standard, and it is written, not spoken.
2. **Planet and temperature as phrases.**
   - **Problem:** both are frequent (tiers 2), so a 4- or 5-syllable phrase costs something every use. But the phrase line says the world's usual compound stays a phrase, as welcome, library and prime minister did (2026-10-16).
   - **Options:**
     - (a) the phrases **segin kobi** "moving star" and **kote pi tikun** "level of heat";
     - (b) roots for both.
   - **Recommendation:** (a), by the agreed rule. If the author takes (a) for temperature, choose **tikun** (shorter, "spicy" reading possible) or **kukedo** (6 syllables, no ambiguity). Add-back trigger for a root: a test where either phrase is misread or measurably slows text (weather reports).
3. **Mass: a root, or widen gogo "heavy"?**
   - **Problem:** no world form and no world compound. Six panel languages say it with their "weight" word, and SI's mass is what everyday weighing measures.
   - **Example:** "the mass of the box is 5 kg" as **gogo pi [box] …** "the heaviness of the box".
   - **Options:**
     - (a) a new root "mass" (tier 1, from the placement tool);
     - (b) **gogo** "heavy; mass, weight (as a noun)", with physics' force-weight said as "force of gravity".
   - **Recommendation:** (b). It saves a root, matches the standard's everyday concept, and follows how half the panel speaks. Add-back trigger: physics text where mass and weight must contrast in one sentence ("weightless but still has mass") and **gogo** fails.

## Caveats

- **One rater** made the panel judgments.
- **Thin columns:** the Hausa columns are all unknown (no Wiktionary entries; Leipzig has nothing), and Yoruba and Quechua are thin. None of them could change a verdict: the ceilings are planet 7, temperature 7 and mass 5.
- **Forms:** the phrase forms use today's lexicon forms (**segin** star, **kobi** move, **kote** level, **tikun** hot, **kukedo** warm, **gogo** heavy).
- **Not yet run:** the oxygen form is vowel-initial and 4 syllables. Run `tools/juncture.py` on it when it is adopted, as AGENTS.md asks after a word change; it wasn't run here, since nothing in `data/` changed.
