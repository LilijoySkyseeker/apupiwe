# Placement 05: the seven new roots of 2026-11-19

Question: forms for the roots the author's decisions of 2026-11-19 added (design log: the world-compound clause deleted; mass a root by C4): planet, temperature, mass, useless, export, import, earthquake; with the loan **okusiden** "oxygen" (`tests/loans-02/`) fixed.

Method: `tests/placement-04/place.py` unchanged (today's lexicon kept; v2 robust score; haplology, digits, juncture, accent rule 2.12), `start --no-vbonus`: every existing root kept (1,456), the seven placed one at a time. The four new concepts were added to `tests/conceptlist-01/concepts.tsv` at tier 1 (their walk ranks 1130–1452, where 85% of concepts are tier 1); export/import recorded as antonyms.

Result: planet **wensin**, temperature **munya** (tier 2); mass **kinebe**, useless **sewubo**, export **ayomi**, import **yafumu**, earthquake **gakodo** (tier 1). None is `offensive.blocked` or `matches`; `tools/accent.py` and the grammar check pass; `juncture.py` reports only the known fixed-word problems.

Scripts consolidated into tools/ on 2026-11-19; the version used here is in git history.
