# Working on Apupiwe

Apupiwe (in the language **apu pi we**) is a thought experiment in the best human language, and a real language its author learns and shares. Read `docs/goal.md` first: every rule and word answers to it.

## Why the project exists (author, 2026-11-19)

The author makes Apupiwe because it's interesting, and because as far as they know nobody has tried this method: a language built from what the world's languages share, measured with modern tools. What makes it interesting is making it as good as it can possibly be; being learnable and usable is part of "good" (B10), as a property of the design. The author's own uses: worldbuilding, naming tools, things and projects, and possibly fiction (a self-consistent language for a science-fiction world, so conversation, including informal speech, must work). It is published as a resource for anyone who wants to learn it; no adoption push. The author doesn't plan to learn to speak it.

## Where things are

- **Standard:** `docs/goal.md` (P, B, C, L, N items; cite them by id).
- **The language:** `spec/reference.toml` is the source; `docs/language.md` is generated from it (`tools/spec.py build`, `check`). Every rule has an anchor (`#r-4-2-4`).
- **Formal grammar:** `grammar/` (GF; design in `docs/formal-grammar.md`). `tools/gf_check.py` must pass: every reference example parses with its intended reading.
- **Words:** `data/lexicon.tsv` (roots), `data/compounds.tsv` (standard phrases), `data/grammar.tsv`, `data/numbers.tsv`, `data/roles.tsv` (two features the grammar needs). The tools' inputs live there too: `data/concept-list.tsv` (every concept, its route, field and tier), `data/bigrams.tsv` (haplology counts), `data/shortwords/` (the short-word optimiser's tables).
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
- One tool per job, all in `tools/` (consolidated 2026-11-19; the old copies in `tests/` are in git history; never run a script from `tests/` to change words): roots `tools/place.py`, short words `tools/shortwords.py`, form changes `tools/apply_forms.py`, checks `tools/check_all.py`.
- To change word forms in data and texts, use `tools/apply_forms.py data|text|tokens|literals MAP FILE...` (one pass per file; it leaves names after **fo** alone).
- After any change: `tools/check_all.py` (spec, GF lexicon, GF check, accent, juncture, unknown words, offensive screen; one line each, non-zero exit if any fails). `tools/place.py write` and `tools/apply_forms.py` run it themselves. After changing the spec, run `spec.py build` first.
- New words: go down the ladders (`vocabulary-method.md` §0); a new root's form comes from the tools, never by hand. Add the concept's row to `data/concept-list.tsv`, then `tools/place.py start --state DIR` (today's lexicon kept, the new root and any root the rules make illegal placed one at a time; `--move FORMS` re-places named words), `tools/place.py report --state DIR` to review, and `tools/place.py write A.json --state DIR` to put it into `data/` (it writes `DIR/map.tsv` for `tools/apply_forms.py` and runs `tools/check_all.py`). New roots need a `data/roles.tsv` row. Loans only where the world shares the form (L4, panel test).
- Public pages follow `docs/style.md` (plain human voice); working notes can be terse.
- Tools run in the Nix dev shell: `direnv exec . python3 tools/…`.
