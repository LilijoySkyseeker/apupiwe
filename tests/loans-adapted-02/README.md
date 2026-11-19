# Loans adapted 02: how close do adapted loans stay to the forms the world uses?

Question (author, 2026-11-19, prompted by **denu** "gene"): a loan enters the language only because the world shares its form (goal L4), so its adapted form should stay recognisable to the speakers who already use it. Which adaptation rules keep loans closest? Real listener tests are unlikely ever to happen (author), so this is measured. `tests/loans-adapted-01/` (2026-10-15) was a model's estimate of recognition; this is a phonetic measurement against each language's own pronunciation.

## Method

- **Data** (`forms.tsv`, `DATA.md`): every loan in `data/lexicon.tsv`, with each panel language's word and mark from the loan panels, and its IPA (Wiktionary via the kaikki dumps first, spelling rules for near-phonemic orthographies next).
- **Distance** (`score.py`): weighted edit distance over segments between the Apupiwe form and the language's IPA (consonant features: place, manner, voicing; vowel features: height, backness, rounding; an added or lost vowel costs half a consonant), normalised by length: 0 identical, about 1 unrelated. Stress, length, tone and other diacritics are ignored. **added**: a proxy for recognisability, not a listener model.
- **Score**: per loan, the mean over its y/b languages; then each region's mean, and the mean of the seven regions (each region counts once, as in the panel rule and N3), plus the worst region. A second column scores each language against the closest declared accent variant of the form (reference 2.9: k g before i e as ch j), since speakers may say the form that way.
- **Variants** of the adaptation rules (`tools/names.py`), applied to the panel's median form: affricates before front vowels to k/g (whose declared variants are the affricates themselves); the same for zh; j as y; a final r dropped instead of kept as **-lu**; echo vowels instead of **u**; combinations; and choosing the source form as the medoid of the languages' forms instead of the median.

## Results

Data (`DATA.md`): 82 loans × 20 languages; 1,288 cells marked y or b, 1,287 with IPA (kaikki 66%, spelling rules 17%, transliteration 16%). The current rules reproduce all 82 forms from the recorded medians. Full table: `results.txt`; per loan: `loans-scored.tsv`, `nearest.tsv`.

| variant | loans changed | region-balanced distance | worst region | with declared variants |
|---|---|---|---|---|
| current rules | 0 | 0.229 | 0.323 | 0.228 |
| ch/j before i e → k/g | 4 | 0.228 | 0.322 | 0.225 |
| j → y | 5 | 0.226 | 0.321 | 0.226 |
| both | 5 | 0.227 | 0.321 | **0.224** |
| final r dropped | 16 | 0.230 | 0.325 | 0.229 |
| echo vowels | 54 | 0.231 | 0.329 | 0.231 |
| medoid source form | 30 | 0.230 | 0.331 | 0.230 |
| nearest rule-made form per loan | 53 | 0.213 | | |

Findings:
1. **On average the rules are already close to the world** (0.23 on a 0–1 scale); no global variant moves the mean by more than 0.005. Re-choosing every loan's form one by one gains 7% (no loan by more than 0.08), within the data's noise; not worth the churn.
2. **The one rule that matters is "ch/j → t/d".** Before a front vowel it makes the outliers: with k/g instead, whose declared variant is the original sound, gene 0.369 → 0.215 (**geni**; **genu** would be a near-twin of **geno** "find"), technology 0.172 → 0.118, oxygen 0.259 → 0.188, engineer 0.317 → 0.266.
3. The loans farthest from the world (website **sayitu** 0.41, beer, hashtag, pound, sugar, circus, T-shirt, garage) are far because the world says them many ways; no rule-made form gets meaningfully closer.

**Decided (author, 2026-11-19): option A**, "ch/j before i e → k/g" in `tools/names.py`; applied: **geni**, **tekunologi**, **okusigen**, **inginiyalu** (`apply/map.tsv`). Rejected: also "j elsewhere → y" (one loan, pajamas; add-back trigger: a second loan where it helps); keeping the rules. The **denu** juncture exception is gone.
