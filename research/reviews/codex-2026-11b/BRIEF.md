Review a designed human language against its own stated goal, as an independent outside reviewer.

Why: the language's forms and grammar are about to be fixed for its first real learners; anything wrong in the foundation is cheap to change now and expensive later.

Read (all under /home/agent/work/repos/universal-language/):
- docs/goal.md: the standard. Every finding must cite the goal item it bears on (P, B, C, L, N ids).
- docs/language.md: the reference grammar (rule ids like 4.2.6).
- data/lexicon.tsv, data/grammar.tsv, data/numbers.tsv, data/compounds.tsv, data/loans.tsv: the words.
- Optionally docs/rationale.md for the stated reasons behind choices. Don't read docs/design-log.md, docs/roadmap.md, tests/ or research/.

In scope: where the language fails a guarantee or pays an avoidable cost under its goal; contradictions between the reference and the data; forms likely to be misheard, merged or confused (by sound, in running speech, across accents); rules a native-speaking child or an ordinary adult speaker couldn't follow; gaps (meanings with no way to say them); anything costly to change once people have learned it.
Out of scope: the website, the tools, prose style, and whether the project is worth doing.

Output (plain text): at most 25 findings, most severe first. Each: severity (high / medium / low), the goal item, the evidence (rule ids, quoted forms or examples), why it matters, and a concrete suggested fix. Then a verdict of at most 5 lines. Check your claims against the files; say "unverified" where you couldn't.
