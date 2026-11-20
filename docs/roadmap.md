# Roadmap

Where the project is and what comes next. Decisions and their reasons are in `design-log.md`; this file is the queue. Updated 2026-11-19.

**Handoff (2026-11-19): where the work stands.** Since 2026-11-18 the critical path is done: the roots are placed (`tests/placement-03` to `-07`), the short words re-formed under the accent rule (`tests/shortwords-04/`), the standard-word loans, fractions and juncture decided, loan adaptation measured (`tests/loans-adapted-02/`) and the audit of exceptions closed; every decision is in the design log. **Next: "Open before v2" below, top to bottom.** The v2 site comes last. Tools for words: `tests/placement-06/place.py` (roots), `tests/shortwords-04/rebuild.py` (short words); after any word change run `tools/accent.py` and `tools/juncture.py` (AGENTS.md). Codex (non-Claude second opinion): see AGENTS.local.md.

**How the backlog is worked (author, 2026-10-15):** finish the current backlog one item at a time. Anything *new* a review turns up gets one test before it joins: does it block v2, i.e. would it change word forms or grammar that are costly to change once the author is learning? If not, it goes under "After v2", not into the queue. If the backlog keeps churning (growing rather than shrinking), the same test is applied to the whole backlog. v2 is done when: the short words are rebuilt, the concept list is closed and the ~1,500 roots placed once, the reference, grammar and lessons agree, and the v2 site is built.

## After v2 (new findings that don't block it)

- Moved from the October queue (2026-11-19): rework the docs so agents can use the language (task-oriented guides, worked examples; 2026-10-13); culture-bound vocabulary beyond religion (holidays, food, titles, kinship, clothing, law); the coverage texts lean European (11 of 20); `offensive.matches`' three known faults (tie-break only); tool defects (`tests/balance-02/concepts_fix.py`'s comma-synonym fix not merged into `tools/`, `concepts.py` never combines synonyms across languages, `build.py` splits antonym rows on any whitespace, `tools/check.py` has no plain-text mode).
- When the freeze returns (auxlang survey, 2026-10-13): freeze only the grammar words and base roots, after the dictionary and lessons are usable (Lojban froze too early).

- Physics basics (author, 2026-11-19, with the mass decision): force, gravity and energy through the concept ladder on their own merits.

- How notation is read aloud (author, 2026-11-19; with the outside review's parentheses in arithmetic and letter case when spelling aloud, findings 12 and 5): Greek letters (the letter name "pi" is the grammar word **pi** "of", and a loan needs two syllables, so π needs an adapted form through the loan panel), operators and equations. Writing already passes notation through (reference 3.4); arithmetic read aloud is treated as a reading of notation (9.2.5).

- `tools/words.py` lags the current rules (found 2026-11-19): it scores with mishearing model v1, doesn't know the haplology rule or rule 2.12, and `move` drops antonym weighting (it passes no antonyms to `add_content`). Until fixed, place roots with `tests/placement-04/place.py` (AGENTS.md). Bring `add-content` onto `confusion2`, the haplology table and `tools/accent.py`'s neighbours, or retire it in favour of the placement tool.

- From the Globasa review (author, 2026-10-15): a learning order from running-text coverage ("the first N roots cover X%", row 62); old → new tables per release when the freeze returns (row 5); dictionary glosses in several languages (row 61).

**Why the project is public:** to share it because it's cool, with people who don't want a git repo or a markdown file. Others using or contributing is a happy surprise, not a goal. It will later live on the author's own site, skyseekerlabs.net. So: a plain static site that can move by copying a folder, and no adoption or governance machinery.

## Done (2026-10-10 to 10-12)

- Spec as structured source: `spec/reference.toml` → `docs/language.md` (`tools/spec.py`), every rule anchored (`#r-4-2-4`); lessons tag the rules they teach and `spec.py lessons` flags lessons whose rules changed.
- Static site (`tools/site.py`, GitHub Pages).
- The goal (`goal.md`), then a cold adversarial review against it (`research/reviews/cold-review-2026-10/`): **keep with repairs**.
- Formal grammar in GF, phase 2 (`formal-grammar.md`, `grammar/`): every reference example parses with its intended reading; the UDHR parses.

## Open before v2: the language itself (author, 2026-11-19: the site comes last)

Triaged 2026-11-19: every item of the October queue is done (design log) or moved to "After v2", except these.

1. ~~Outside review~~ done 2026-11-19 (`research/reviews/codex-2026-11/`); its design questions are being decided (RESPONSE.md). Was: **Outside review** of the design and the final forms by a non-Claude model (Codex), cold (process risk 1 of the unknown-unknowns review; the October plan for "a non-Claude model for one month").
2. ~~Regression test~~ moved to "Last" (author, 2026-11-19: it would mostly test the docs, which will be rebuilt).
3. ~~Record the phrases already decided~~ done 2026-11-19 (design log).
4. ~~Senses the concept walk flagged as uncovered~~ and 5. ~~symbol names~~ done 2026-11-19 by the ladders (`tests/ladder-02/`). The pronoun rule and rule J applied 2026-11-19 (`tests/placement-08/`). Next: the regression test (2).

## Last: the docs and lessons, rebuilt from scratch (author, 2026-11-19)

Once the language itself is final, before the v2 site. The old lessons were deleted from this branch on 2026-11-19 (git history keeps them; `tools/site.py` still expects `docs/learn.md` and is rebuilt with the site).
- **Lessons from scratch,** from the reference and data alone, plus research on how languages are best taught (to do: a research pass on language pedagogy before writing). Not adapted from today's lessons.
- **Docs that agents and people can produce text from** (2026-10-13 item): worked examples for producing text, not only rules.
- **Teach what the language already says but no text explains** (from the outside review, 2026-11-19): "the robot broke down" is **lewe gun** + the action word (4.5.4, finding 4); show whether each verb takes an object (`data/roles.tsv`, finding 7); "should" in questions and reports (finding 11, check it is sayable with **kifa**, **wupi** or **upe** first).
- **Regression translation test** (moved here from "Open before v2"): blind translation and back-translation by fresh Claude and Codex agents, and a fresh agent writing Apupiwe from the new docs alone; include **feko** answers and the UI button set. Run on the final language with the new docs, so it tests both.

### Website: frozen at v1 (author, 2026-10-13)

The published site stays at v1 until the language is solid; then a v2 site is built from first principles, keeping v1's spirit. Work is committed on the branch `v2-work` and pushed there as a backup; `main` (which the site builds from) isn't touched until v2. The repo's reference and lessons stay in sync meanwhile. Known false statements on v1 are left as they are (no one is reading it yet) and are fixed in v2:

- Public-page fixes deferred during the batch: the Esperanto/creole sentence in "How it's built" (fact-check C15, C17, C18); `why.md` digit figures (0.26% / 2.3% describe a modelled ideal set); learn.md "ran out of short sounds"; clusivity "among the most stable" (Austronesian only). Also `why.md`'s number-base answer still cites the base-6 transmission figures (0.26% vs 2.3%) that were cut on 2026-10-12 (they were for ideal digit sets, per 10-digit ID).
- Re-check the UDHR translation against the batch's rules.
- Build v2 of the site from first principles.

## Later

- Formal grammar phase 3 (English concrete syntax) and phase 4 (every document checked by one command); `tools/parse.py` retires then.
- Senary gets its own vocabulary and page (a separate project; its words are reserved in `data/senary.tsv`).
- **Needs real human listeners or readers (running list; author, 2026-10-15: keep a running note of what really needs testing with humans).** Model or AI checks stand in until then; add to this list whenever a decision rests on one. Trigger for running them: listeners or readers from at least three language families, or money for a crowd study (~$150–300 for 60 listeners; `research/notes/unknown-unknowns.md` #1).
  - Listening: the mishearing model's ranking of word pairs (listening-01's 32 pairs; the final short words and roots), in noise, by listeners of several first languages (B2; cold review's first repair).
  - Listening: recognition of adapted loans (**intelunetu**, **kilometulu** …) by speakers of the panel languages; screened by Codex 2026-10-15 (`tests/loans-adapted-01/`); test especially the rules behind most low scores: affricates → **t**/**d** (before i e → **k**/**g** since 2026-11-19, `tests/loans-adapted-02/`) and final r → **-lu** (**metulu**, **dolalu**, **biyalu**).
  - Listening: stress heard as pitch plus force, including whispered and sung speech (reference 2.6, decided 2026-10-15).
  - Listening: sentences where a pause is the only cue to structure, and the **kiyu** alternative (auxlang survey R6).
  - Reading: **feko** as the answer after a negative question, read the same way by speakers of polarity- and truth-based languages (4.8.6; unmeasured).
  - Reading: verbs with no object (4.5.4; Codex read 16 of 16 as intended, 2026-10-15).
  - Native speakers: offensive-word grades for the non-European languages (`research/notes/offensive-strength.md`), and the symbol-name near misses (@, dot) in Tagalog, Swahili, Hausa, Yoruba (`tests/symbols-01/`).
  - Listening: the five grammar-word pairs that differ only by a final -n, in different positions (**fo/fon**, **yo/yon**, **ka/kan**, **ya/yan**, **wa/wan**; 2026-11-19).
  - Learners: a learner trial (B10) and human readers for meaning (B1), as the cold review asked; a cross-language word-learning test of invented vs world-sourced roots (the Globasa floorboard trigger).

## Deliberately not built

Each with the trigger that would bring it back:
- wiki software: non-git people want to edit;
- contribution governance: a real group forms;
- CI: the build is stable and the repo is public;
- tools on the website (tabled 2026-10-11): a word-by-word gloss page is cheap and first in line; the parser in the browser waits until learners ask whether their sentences are grammatical; the name adapter until people ask how to say their name;
- YouTube transcripts as a frequency source (2026-10-13): the coverage rerun still misses common modern concepts.
