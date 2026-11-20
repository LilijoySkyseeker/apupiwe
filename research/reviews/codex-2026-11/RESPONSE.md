# Response to the outside review (Codex, gpt-6.2-astra, high effort, cold; 2026-11-19)

Brief: `BRIEF.md`; report: `report.txt`. Every claim was checked against the files.

## Fixed at once (errors, no design decision)

- 6. **warehouse** and **shelter** were both **ban kuwi** (a compound added today copied the older one's form): warehouse is now **ban meko** "place for keeping"; the keeping example in 5.4.4 is **wa meko pi to**.
- 13. Stale compounds: password **ila pi udin** (word, not language), keyboard **buguye la** "the buttons" (**tinli** is a lock's key), contacts' note names **dapo**.
- 14. Reference 11.2 still said j → d; it now states the k/g rule before i e (2026-11-19).
- 15. parents is **iwola la**; **mole nun sine** is literally "mother and father".
- 17. The rate example used **sa bifo**; it is **bifo sa** (noun, then count), as in 8.2.1.
- 18. Lesson 1 said **poka** is "TO-tu" (a form map rewrote the bold word, not the pronunciation guide); the vocabulary counts were from October.
- 3. Rule 2.12's wording now gives the contexts (softening between vowels in an unstressed syllable; palatal variants anywhere). With those contexts, **dundi**/**lunli** and **wuye**/**guge** don't break it (their differing consonants are word-initial or after a coda), which is what `tools/accent.py` checks.

## For the author (design decisions)

1. Three-syllable roots that sound like a two-syllable word plus a grammar word (**tiwuye** "spring" vs **tiwu ye** "some of the children"): 79 of 443 (`tools` scan, 2026-11-19). Systematic, from the three-syllable roots of 2026-11-18.
8. **sen** YOU and **son** LOGOPHOR differ only by their vowel, in the same position (pronouns), against rule 2.12's last sentence; **sen** came in with today's short-word layer.
2, 9. **kiyu** "end of phrase": its scope (one level or all open clauses) and names inside relative clauses.
4. An event form for "X broke" (the thing affected, no cause), beside "X broke it", "X broke itself", "X is broken".
10. **fo** before a borrowed verb that collides with a word makes it a name, which can't be a verb.
11. "should" in questions and reports.
12. Parentheses in arithmetic read aloud.
16. **kon nelon ni** "a week from now" vs "next week" (calendar).
5. Case and punctuation when spelling aloud.
7. Verbs' complement patterns (takes an object or not) for learners: `data/roles.tsv` has them; the lessons and dictionary don't show them.

## Outcomes (2026-11-19)

All 18 findings resolved: 1 (rule J, 85 roots re-placed), 8 (pronoun rule, 8 grammar words), 2 and 9 (kiyu: restructuring is the precise way), 10 (clashing borrowings reshaped, not marked with fo), 16 (spec error fixed), 3, 6, 13, 14, 15, 17, 18 (errors fixed); 4, 7, 11 go to the docs rebuild (the language already says them); 5, 12 join "notation read aloud" after v2. Design log, 2026-11-19.
