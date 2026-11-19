# Accent tolerance 01: which pronunciations count as the same sound

Question (roadmap "Placement checks", 2026-10-15; Globasa rows 12–13; cold-review verdict C §2, A7 F3): which accent variants can the reference declare harmless, with no variant merging two words? And does any grammar-word contrast rest on a variant (the verdict's replacement for "grammar words keep their consonants", a norm speakers can't obey)?

## Method

`pairs.py`: for each pair of sounds that a candidate variant could bring together, list the word pairs (content words, grammar words, digits) that differ only by those two sounds, in the context where the variant applies. Grammar words and digits count as "between vowels": in running speech they usually follow a vowel-final word. Then each pair involving a grammar word or digit is scored with model v2 (`tools/confusion2.py`, robust = mean of the worst quarter of 48 variants, symmetric), against all 2,485 grammar-word and digit pairs.

Candidates: the roadmap's list (l as [ɫ ɾ], p t k ± aspiration, f as [ɸ], w as [ʋ], glottal stop at vowel junctions across words), Globasa's s as [ʃ], and the variants reference 2.9 already calls harmless (k g as "ch" "j" before i e; consonants softening between vowels; vowel + n as a nasal vowel).

## Results

**Content words are safe.** No content pair rests on any of the variants except four under k [tʃ] / s [ʃ] before i/e (**senke** armpit ~ **sense** butterfly, **moken** bear ~ **mosen** manage, **kenken** arrest ~ **kensen** honey, **kakin** honest ~ **kasin** squirrel). The placement's drift keys already keep content words apart.

**No variant merges words on its own.** Every risk is two accents meeting: one speaker's variant of sound A against another speaker's variant of sound B. Twelve grammar-word or digit pairs are exposed, and the model already ranks most of them in the top 2% of grammar pairs:

| sounds | how they meet | pairs (robust score; percentile among grammar pairs) |
|---|---|---|
| b / w | b softened between vowels [β̞] ~ w as [ʋ] | **bo** BECAUSE ~ **wo** 4 (0.140; 99.0), **bun** IT ~ **wun** THAT (0.132; 98.9) |
| d / l | d softened or flapped [ð ɾ] ~ l as a tap [ɾ] | **din** WE.excl ~ **lin** WHILE (0.100; 98.7), **du** TOOL ~ **lu** OR (0.107; 98.7), **de** 3 ~ **le** ONGOING (0.108; 98.8) |
| g / w | g softened [ɣ ɰ] ~ w, before o u | **go** SOME ~ **wo** 4 (0.066; 98.3), **gun** BE ~ **wun** THAT (0.061; 98.1) |
| g / y | g before i e as [dʒ] ~ y, where dʒ and j merge | **gi** WHO.rel ~ **yi** OBVIATIVE (0.092; 98.6), **gen** RESULT ~ **yen** AND (0.086; 98.4) |
| k / s | k before i e as [tʃ] ~ s as [ʃ] | **kin** PART ~ **sin** DONE (0.018; 92.6), **ke** MORE ~ **se** FROM (0.019; 93.4) |
| f / p | f as [ɸ] ~ unaspirated p | **fon** ADVISE ~ **pon** ALSO (0.238; 99.6), **fi** ENDEAR ~ **pi** OF (0.259; 99.7) |

For scale: median grammar pair 0.0001, 90th percentile 0.012, 99th 0.141. **la/le**, the pair the verdict named, is 0.031.

Reading: every exposed pair except f/p comes from a variant reference 2.9 already calls harmless: softening between vowels, and k g before i e. The new candidates (l as [ɾ], w as [ʋ], s as [ʃ]) only create a risk when combined with one of those. f/p is different: [ɸ] and [p] stay distinct; that pair's high score comes from listeners whose first language has no f, which is already in the model and isn't a variant.

## For the author

The decision on which variants to declare, and what to do about the twelve pairs, is in the design log once made.
