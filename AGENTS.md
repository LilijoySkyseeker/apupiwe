# Working on Apupiwe

Apupiwe (in the language **apu pi we**) is a thought experiment in the best human language, and a real language its author learns and shares. Read `docs/goal.md` first: every rule and word answers to it.

## Where things are

- **Standard:** `docs/goal.md` (P, B, C, L, N items; cite them by id).
- **The language:** `spec/reference.toml` is the source; `docs/language.md` is generated from it (`tools/spec.py build`, `check`). Every rule has an anchor (`#r-4-2-4`).
- **Formal grammar:** `grammar/` (GF; design in `docs/formal-grammar.md`). `tools/gf_check.py` must pass: every reference example parses with its intended reading.
- **Words:** `data/lexicon.tsv` (roots), `data/compounds.tsv` (standard phrases), `data/grammar.tsv`, `data/numbers.tsv`, `data/roles.tsv` (two features the grammar needs); `data/senary.tsv` is reserved, outside the core.
- **Lessons:** none on this branch (author, 2026-11-19): the old ones were deleted (they're in git history, and on the published v1 site) because they caused confusion. Once the language is final, new lessons are written from scratch from the reference and data alone, plus research on how languages are best taught (roadmap "Last"). Until then the reference (`spec/reference.toml`) is the only teaching text, and it must stay correct. The v1 site's machinery (`site/`, `tools/site.py`, the Pages workflow, `docs/why.md`, `examples/`) is deleted on this branch too; `main` keeps the published v1 site until v2.
- **Why:** `docs/design-log.md` (every decision, newest last, with reasons, alternatives and add-back triggers), `docs/rationale.md`, `docs/vocabulary-method.md` (the word-decision ladders, §0), `docs/drift.md`, `research/`.
- **What's next:** `docs/roadmap.md`.
- **Tests:** `tests/NAME/`, each with a README (question, method, results) or results file; long multi-agent runs keep a resumable `PROGRESS.md`.

## How decisions are made

- The author decides anything that shapes the language. Agents research, draft and recommend. Present each decision in full: the problem, an example, the options and a recommendation, one at a time.
- **Sort findings before bringing them** (author, 2026-11-19): a gap in the language (nothing can say it, or rules conflict) is a design question; a wrong statement in the reference or data is a spec error, fixed at once; something the language already says but no text teaches goes to the docs rebuild list (roadmap "Last"), not to the author.
- **Let the method decide what it can** (author, 2026-11-19): where the word-decision ladders (`vocabulary-method.md` §0) or an agreed rule give a clear answer (a measured lump rate, a panel verdict, a frequency line), run them, apply the result, log it with its evidence, and report it to the author in a batch they can overturn. Bring the author only what the method leaves open (no data, a rate near a threshold, goals that conflict) or what changes a rule. Example: `tests/ladder-02/` (CAUSE vs MAKE, 1.8%: "cause" is **ukun**, not **tula**).
- Design by the goal's order: question every requirement and name its source (a person or a concrete external constraint); prefer deleting a part, with the trigger that would bring it back; simplify only what survives; automate last.
- **Check before proposing** (author, 2026-10-13): before proposing to add, change or delete anything, find what the repo already says about it (`tools/why.py TERM` searches the design log, rationale, goal, reference, drift and research notes) and cite its recorded source in the proposal, or say where you looked and found none. Apply the rules already agreed (frequency, the ladders, the culture principle) to your own proposals too, not only to inherited parts.
- Log every decision in `design-log.md`: what was decided, by whom, why, what was rejected, and where it changed the reference, lessons or grammar. Keep the reasoning in the repo, not only in a chat.
- Track all open work in `docs/roadmap.md`, with its source: queued questions, review findings not yet taken up, small fixes. Anything found along the way (a gap a test turns up, a question tabled for later) goes there when it's found, not only into a chat, a working folder outside the repo, or a report. When work is done, move it to "Done" and log the decision.

## Changing things

- Branches: `main` is the published v1 site (GitHub Pages builds on every push to it). Until v2, work goes on `v2-work` and is pushed there; don't push to `main` (author, 2026-10-13).
- To change word forms in texts, use `tests/placement-08/apply/apply.py` with a `map.tsv` beside it (one pass per file; it leaves names after **fo** alone).
- After changing the spec: `spec.py build`, `spec.py check`, `gf_check.py`; regenerate the grammar lexicon with `tools/gf_lexicon.py` after word changes. After any word change: `tools/accent.py` (rule 2.12) and `tools/juncture.py`.
- New words: go down the ladders (`vocabulary-method.md` §0); a new root's form comes from the tools, never by hand. `tools/words.py add-content` still uses mishearing model v1 and doesn't know the haplology or accent rules (roadmap), so until it's updated, place roots with the placement tool (`tests/placement-11/place.py start --no-vbonus`, the newest, with every rule (placement-07 adds `--move FORMS` to re-place named words): today's lexicon kept, roots the rules make illegal placed one at a time; a new concept needs a row in `tests/conceptlist-01/concepts.tsv` first) and run `tools/accent.py`. Loans only where the world shares the form (L4, panel test).
- Public pages follow `docs/style.md` (plain human voice); working notes can be terse.
- Tools run in the Nix dev shell: `direnv exec . python3 tools/…`.
