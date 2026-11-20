# Stress 01: which word sequences only stress tells apart

Question (author, 2026-11-19): is the language understandable without stress, and does it rest on stress
in noise? This is the computational half; the listening half stays parked (design log 2026-10-15).

Method (`check.py`): two cuts of the same syllables into words, exact sounds (accent variants not included).
Stress per reference 2.5: one-syllable grammar words unstressed, digits 0-5 one stressed syllable, every other
word stressed on its first. SAME = both cuts have the same stress (stress can't help); diff = stress is
the only sound cue. Part 1: every pair of the 1,635 words. Part 2: every minimal re-cut in the corpus
(reference examples + UDHR, 361 sentences, 2,219 tokens), and whether the re-cut sentence still parses (GF).

## Results

- **SAME stress: none**, in the pairs or the corpus. Rule J and the digit rule already removed every
  re-cut that stress can't resolve.
- **diff stress, everywhere.** 217 of 1,566 roots are made entirely of grammar-word syllables (the 64
  one-syllable grammar words fill nearly every syllable), and 790,019 word pairs can be re-cut some other
  way; 184 grammar-word pairs sound like a root. No rule can remove this; stress, grammar and context
  segment the speech, as in natural languages (Mattys et al. 2005: lexical and context cues first,
  stress mainly in noise).
- **Corpus:** 143 stress-only re-cuts (56 distinct), 1 per ~16 tokens. In 48 the re-cut sentence still
  parses. Read by hand (by the agent, one reader), most are nonsense in context (*bawe pi ewo* ~ *ba we
  pi ewo*). Believable ones:
  - *lo wu mon obu* "could she please come" ~ *lowu mon obu* "the man, she comes" (request vs report)
  - *tiwu futa* "the child runs" ~ *ti wu futa* "please run"
  - *tula yefi kin* "do something" ~ *tula ye fikin* "do some naughty…"
- Act particle + grammar word sounding like a root (all 49 in `pairs.tsv`); the ones at the start of a
  request, before *wu* or a subject: *lo wu*/**lowu** man, *ti wu*/**tiwu** child, *ti mon*/**timon**
  half, *ka mon*/**kamon** quality, *lo ta*/**lota** thank, *wu kan*/**wukan** juice, *ti we*/**tiwe**
  sweat, *lo we*/**lowe** song.

Files: `pairs.tsv` (pair re-cuts into one or two words; the summary counts all), `corpus.tsv` (corpus re-cuts, parses of the re-cut sentence),
`summary.txt`.
