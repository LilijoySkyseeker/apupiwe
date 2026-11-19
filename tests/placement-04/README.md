# Placement 04: roots the new short words make illegal

Question: which roots must move once the short words are re-formed (`tests/shortwords-04/`, design log 2026-11-19) and the accent rule (reference 2.12) holds for content words, and where do they go?

Method: `place.py` is placement-03's, starting from today's lexicon instead of the concept list's old forms, with the haplology table (`bigrams.tsv`) remapped to the new grammar forms and a new hard rule: no two content words differ only by a declared accent merger (`acc_neigh`). `place.py start --no-vbonus` keeps every root that is still legal and places the rest one at a time, on model v2's robust score; no descent, so nothing else moves.

Result: 18 roots move, as predicted: the 14 the new haplology syllables displace and one of each of the four k/s pairs.

| root | old | new |
|---|---|---|
| possible | winbo | sepe |
| list | benge | sema |
| activity | nunli | yenge |
| star | nunma | segin |
| smooth | windi | sesu |
| open | benbi | selon |
| mirror | winka | seyo |
| manage | mosen | dense |
| leg | bendo | sesen |
| knife | nunse | sepun |
| honey | kensen | sanse |
| honest | kakin | yenbun |
| hero | winbin | yendo |
| hell | benten | lunli |
| buttocks | nunfo | sewu |
| butterfly | sense | wanbo |
| brave | winsen | yenli |
| pull | nunya | sekan |

Nine take **se-**, freed when FROM moved from **se** to **don**: the model puts new roots in the emptiest region. Also the tool to use for future roots until `tools/words.py` catches up (AGENTS.md).
