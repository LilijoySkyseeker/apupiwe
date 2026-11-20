# Stress 02: which grammar-word pairs that sound like a root matter

Question (author, 2026-11-19, Decision 23): instead of hand-picking which of the 184 grammar-word pairs
that sound like a root (`tests/stress-01/`) need fixing, measure it. Method in `frames.py`:

1. **Can the pair stand together?** Frames from the corpus (reference examples + UDHR, sentences of 14
   words or fewer): two adjacent grammar words of the pair's classes, replaced by the pair; or the pair
   inserted at a word of either word's class. Up to 16 frames per pair, parsed with GF.
2. **Does the root fit there?** In each frame where the pair parses, the pair becomes the root; parsed again.
3. **Weight** = lower grammar-word frequency (data/grammar.tsv) × stakes (as in tests/deletion-01: 3 for
   speech acts, negation and warning, 1 for politeness and stance, 2 otherwise) × share of frames where
   both parse.
4. **Does the root reading make sense?** Grammatical isn't believable, so the example sentences of the top
   31 by weight were read word by word, by the agent (one reader).

## Results

- 89 of the 184 pairs never parse together in any frame: the grammar rules them out.
- 95 can stand together; in 94 the root also parses in the same place (`results.tsv`, `examples.tsv`).
- Read by hand, the root reading is believable in **six**; the rest are nonsense in context
  (*ta yu nawi* "which of us eats" ~ *tayu nawi* "agree eats"):

| said | heard | stakes |
|---|---|---|
| *lo wu mon obu* "could she please come" | *lowu mon obu* "the man, she comes" | request vs report |
| *ti wu mon obu* "please let her come" | *tiwu mon obu* "the child, she comes" | instruction vs report |
| *ti mon obu* "let her come" | *timon obu* "half (of them) come" | instruction vs report |
| *ta ten nuta* "we're very afraid" | *taten nuta* "the cat is afraid" | who |
| *ten bun upe* "it's very good" | *tenbun upe* "the sword is good" | what |
| *mon ga ke nawi* "she only eats more" | *mon gake nawi* "she eats slowly" | how |

- Of the eight roots hand-picked earlier (stress-01), three hold up (*lowu*, *tiwu*, *timon*); *kamon*,
  *lota*, *wukan*, *tiwe*, *lowe* don't (nonsense in context, or almost never grammatical), and three
  new ones appear (*taten*, *tenbun*, *gake*).

## Applied (Decision 23 A, author, 2026-11-19)

The six moved (`tools/place.py start`, every other root kept): child **lenu**, man **dage**, half **bedun**,
cat **kimon**, sword **migon**, slow **geyin**. Rule G in `tools/place.py` and `tools/juncture.py` 5; the 178
others are in `data/regroup-reviewed.tsv` with their verdicts.
