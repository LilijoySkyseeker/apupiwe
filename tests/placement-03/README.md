# Placement 03: the placement with all of the author's settings

Question: the final candidate forms for the ~1,457 roots, under every decision so far (design log 2026-11-18): three syllables only for tier 1; **apu** locked; no vowel-start length bonus; keep term 0.03; number words weighted ×30 against each other and at the ordinary weight against everything else.

Method: `tests/placement-02/` (and its parent, `tests/placement-01/`), with one change in `place.py` `weights()`: number–number pairs ×30 instead of ×10 for any pair with a number word. Run: `./run.sh` (medians, start without the vowel bonus, seeds 1 and 2 at `--keep 0.03 --no-vbonus`, report). Since `tools/build.py` now has no vowel bonus, `--no-vbonus` only switches off the oversampling of V.CV.CV candidates.

## Progress

- [ ] `./run.sh` (logs in `logs/`)
- [ ] results below

## Results

(pending)
