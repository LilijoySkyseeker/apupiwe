# Interjections and self-correction through the panel (interjections-01)

Asked by the author, 2026-11-19: "we do need native interjections; also look for the self-correction phrase".
Method: ladder 2 rung 2 (a form the world shares: 12 of the 20 panel languages, 5 of 7 regions, sourced columns only);
where nothing passes, rung 3 (built from existing words, here with the exclamation particle **ka**, 7.1).

## Sources
- **Wt:** English Wiktionary translation tables for ouch, oh, huh, hey, shh, wow, yuck, phew, oops (`wt-panel.txt`,
  fetched 2026-11-19 with `tests/lexicon-ladder-01/panel.py`; "um" has no table).
- **We:** every interjection (pos=intj) in the cached kaikki.org extracts, `extract.py` → `intj.tsv`
  (`~/work/cache/coverage`, fetched 2026-10-13). `count.py` and `show.py` were the first automatic pass; their counts
  had false hits and are superseded by the hand pass.
- Hausa, Yoruba and Quechua have almost no interjection data (27, 88 and 5 entries), so they count as "no" throughout.

## Shape rule (mine, flagged)
Interjections are outside the sound system (reference 2.10), so `names.py` adaptation doesn't apply. Two forms are one
shape when their core sound matches, ignoring h, a glottal stop, length, tone and a final glide.

## Result (`panel.tsv`, hand pass)
| function | shape | count | regions | outcome |
|---|---|---|---|---|
| "oh" (noticing, surprise) | o / a | 17 | 6 | **o** (13 of 17 are o-type) |
| "huh?" | a? / e? | 12 | 5 | **a?** (8 of 12 a-type); Dingemanse et al. 2013 found the same |
| "hey" | e/o + y | 13 | 5 | **ey** (9 of 13 e-type) |
| "shh" | sibilant | 13 | 6 | **ss** |
| "ouch" | ai | 11 | 5 | fails by one: **open, the author decides** |
| "wow" | wa | 10 | 5 | fails; **o** (stretched) and **ka** + a word cover it |
| "uh, um" (hesitation) | e/ə/ɯ (+m) | 10 | 4 | fails; a built filler would be a word, which a filler must not be: **open** |
| "yuck" | none | ≤6 | 3 | built **ka bebu** |
| "phew" | fu/uf | 5 | 3 | built **ka sonli** |
| "oops" | none | ≤5 | 2 | built **ka gagan** |

## Self-correction
The panel's majority marker is "that is / it means" (ar yaʕnī, fa ya'ni, tr yani, sw yaani, hi yānī, bn mane,
ta atāvatu, ru to est', vi tức là, ko 즉; We). Built: **wan yofu** "I mean" + the correction, as its own sentence and
without a pause: *wan yofu fo tomas* has one reading. With a pause, a final name is read as calling someone (4.6.2).
