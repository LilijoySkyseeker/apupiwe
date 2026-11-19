# loans-adapted-02: the pronunciation table (forms.tsv)

Task: `PROMPT-data.md`. Output: `forms.tsv`, one row per loan × panel language (82 loans × 20 = 1,640 rows), with broad IPA for every cell marked y or b.

## Progress

- [x] Panel rows collected for all 82 loans (`panel.py` → `panel.tsv`); none missing.
- [x] kaikki entries pulled (`kaikki_pull.py` → `~/work/scratch/loans-adapted-02/kaikki-hits.json`, about 1 minute).
- [x] IPA chosen per cell (`build.py` → `forms.tsv`), with spelling rules and transliteration in `rules.py`.
- [x] Hand checks: every cell where a non-first word was chosen, every kaikki entry with no matching sense, every transliteration, every rule output (see "Checks").
- To rerun from scratch: `python3 -I panel.py && python3 -I kaikki_pull.py && python3 -I build.py` in this folder. Only `build.py` needs rerunning after a change to `rules.py`, `tokens.py` or its `OVERRIDES`.

## Which loans, and which panel row

`data/lexicon.tsv` has 82 rows with field `loan`, oxygen (**okusiden**) among them, so the total is 82, not 82 + 1. `adapted` is the lexicon's current form. Where each loan's panel row comes from:

| Loans | Panel file | Median |
|---|---|---|
| 60 coverage loans (chocolate … mask, pound) | `coverage-01/part3/loanwork/c01–c11.txt` | the block's `median:` |
| dollar, internet, email, battery, euro, yuan, rupee, camera | `coverage-01/part3/loanwork/older.txt` (the 2026-10-13 rerun; its counts match `loans-rerun.tsv`) | the block's `median:` |
| tobacco, calendar | `deeplayer-02/loanwork/panel.txt` | the block's `median:` |
| oxygen | `loans-02/loanwork/panel.txt` | [oksidʒen] |
| .com, hashtag | `symbols-01/panel.tsv` | [kom], [haʃtag] from `symbols-01/README.md` |
| kilometre | the table in `lexicon-ladder-01/loans.md` (✓ y, ✗ n) | [kilometr] |
| metre, centimetre, millimetre, gram, kilogram, litre, kilo | `coverage-01/part3/metric-panel.txt` | **none recorded**; see below |

Choices I made (each also stated in the row's `note`; the panel file is named in every zh row's note):

- **verified.tsv applied.** For the coverage and older loans, a column that `coverage-01/part3/loanwork/verified.tsv` checked keeps its mark when the result is `yes`, becomes **n** when `no` and **u** when `unknown` (29 cells changed: 23 to u, 6 to n). With this, every coverage loan's y+b count equals its count in `loans-final.tsv`, and every older loan's equals `loans-rerun.tsv`, so these are the final, adopted rows. Memory-only columns that were never checked keep their recorded mark, as the final counts did.
- **First block wins** when a concept appears twice in a file, as `emit.py` does (only dollar in `older.txt`; the two blocks are the same).
- **pound** has no row in `loans-final.tsv`'s pass list: it was adopted as a currency loan by the author's decision (decision 6, `loans-final.tsv` row "loan as a currency only"); its c08 block (strict 11, lenient 14, median [paund]) is used as recorded.
- **rupee**: the lexicon form is **lupiya**; the rerun's median [rupija] is used.
- **Metric units (7 loans).** `metric-panel.txt` lists Wiktionary's translations only, with no marks and no median. Marks are derived: **y** when the language lists a form of the international word, **n** for Mandarin (米/克/升/公斤/厘米/毫米, Sino forms; the kilometre table marks 公里 n) and for Quechua *k'isura* (gram), **u** where the language isn't listed (always Hausa, Quechua mostly, Tamil for centimetre and millimetre, Indonesian and Bengali for millimetre). **kilo** (the everyday short form): y for the 12 languages the design log names (2026-10-13: ja ko vi th hi bn ta tr ru fr sw yo), n for zh, u for the rest, since Wiktionary lists no short form there. Medians are the ones the design log's parts imply (kilo-, senti-, mili- + [metr], [gram], [litr]: [metr], [sentimetr], [milimetr], [gram], [kilogram], [litr], [kilo]); `tools/names.py` turns each into the lexicon's form exactly. Treat these seven as softer than the rest.
- No loan came from `imitative-01` (its only pass, *mama*, isn't a `loan` row).

Mark counts over all 1,640 cells: y 1,147, b 141, n 305, u 47. So **1,288 cells need IPA**.

## Coverage

| Source | y/b cells |
|---|---|
| kaikki | 854 (66%) |
| spelling rule | 222 (17%): sw 59, qu 49, yo 42, ha 26, tr 19, vi 13, id 7, tl 6, es 1 |
| transliteration, automatic | 199 (15%): 177 from the romanisation the panel recorded or an English spelling in a Latin-script cell, 22 from the native script |
| transliteration by hand | 12 (1%) |
| none | 1: robot, Yoruba (mark b, word "(no data)", memory only: there's no word to transcribe) |

By language (y/b cells: kaikki / rule / translit / by hand / none):

| lang | cells | kaikki | rule | translit | by hand | none |
|---|---|---|---|---|---|---|
| zh | 17 | 10 | 0 | 6 | 1 | 0 |
| ja | 71 | 65 | 0 | 6 | 0 | 0 |
| ko | 68 | 64 | 0 | 4 | 0 | 0 |
| vi | 49 | 30 | 13 | 5 | 1 | 0 |
| th | 58 | 52 | 0 | 6 | 0 | 0 |
| id | 75 | 63 | 7 | 5 | 0 | 0 |
| tl | 77 | 62 | 6 | 9 | 0 | 0 |
| hi | 82 | 56 | 0 | 26 | 0 | 0 |
| bn | 77 | 36 | 0 | 39 | 2 | 0 |
| ta | 61 | 20 | 0 | 35 | 6 | 0 |
| fa | 73 | 58 | 0 | 14 | 1 | 0 |
| ar | 68 | 40 | 0 | 27 | 1 | 0 |
| tr | 76 | 53 | 19 | 4 | 0 | 0 |
| ru | 76 | 76 | 0 | 0 | 0 | 0 |
| es | 77 | 75 | 1 | 1 | 0 | 0 |
| fr | 78 | 77 | 0 | 1 | 0 | 0 |
| sw | 69 | 6 | 59 | 4 | 0 | 0 |
| ha | 38 | 10 | 26 | 2 | 0 | 0 |
| yo | 46 | 1 | 42 | 2 | 0 | 1 |
| qu | 52 | 0 | 49 | 3 | 0 | 0 |

The weak spots: **Bengali, Tamil, Arabic and Hindi** rest on transliteration for a third to over half of their cells (Wiktionary has few entries for spoken English loans there), and the African languages and Quechua rest almost wholly on rules (kaikki has almost no IPA for Swahili, Yoruba, Hausa or Quechua words).

## Method

1. **Candidates.** Each cell's free-text word field is split into candidate words (`tokens.py`): runs of the language's script, each paired with the romanisation written right after it; for Latin-script languages, 1–3-word n-grams of each comma/semicolon segment, with parenthesised notes (counts, rivals, etymologies) skipped unless nothing else is left.
2. **Which word.** A cell often lists a native word beside the loan (*máy ảnh; camera beside it*). Each candidate gets a resemblance score to the loan's median (a crude normalised string match on a simplified IPA, also against the word's start so a short form like *moto* can match), and the most similar wins; among near-ties (within 0.05) a candidate with kaikki IPA is preferred, then the first listed. When the chosen word isn't the first listed, the note says "chose X over Y".
3. **IPA, in order:**
   1. **kaikki**: the headword (also tried without Russian stress marks, without Arabic/Persian vowel marks, Korean without spaces, Latin-script lowercased/without hyphens; Chinese simplified entries with no IPA are followed to the traditional entry they point to). Among homographs, an entry whose glosses contain the concept's first word is preferred; `ipa_source` says "(no sense gloss matched)" otherwise (48 cells; all checked, see below). The first IPA of the standard variety: zh Mandarin Standard Chinese (Sinological IPA); fa Iranian (tags Iran/Tehrani; Dari, Tajik, Classical skipped); vi Hà Nội; tl Standard Tagalog; ar the untagged (MSA) line; fr the untagged line (Quebec, Belgium skipped); es the first line without θ (seseo, the majority pronunciation; kaikki lists Castilian first); lines tagged nonstandard or proscribed skipped. Tones, stress, length and syllable dots are left in.
   2. **rule** (`rules.py`), for es, id, tl, sw, tr, yo, ha, qu and romanised vi. Rule sets below.
   3. **translit**: the romanisation the panel recorded, through a per-language table (pinyin, Hepburn, Revised Romanisation, the panel's Thai scheme, IAST-style Indic, Arabic/Persian scholarly); or, where the cell has none, the native script itself (kana; Devanagari, Bengali and Tamil by their shared Unicode layout, with Hindi final and medial schwa deletion and Bengali inherent ɔ; vowelled Arabic/Persian; Hangul by jamo). English spellings in Latin-script cells (*com, hashtag, email, mail, profile, rupee, T-shirt, taxi, sandwich, code, euro*) get a broad reading of the English word, labelled translit.
   4. **by hand** (`build.py` `OVERRIDES`, 12 cells, labelled "translit: by hand" with the reason): Tamil cells that record only an English spelling ("spoken radio/helicopter/T-shirt/gas/vaccine", "hashtag"; Indian-English readings), Bengali *technology* (same) and হ্যাশট্যাগ (the script reader gets ্যা wrong), Mandarin *com* (said in English), Arabic كوم (kaikki has only the homograph "heap" /kawm/; the domain ending is [kom]), Persian *nān-e tost* (the loan part only), Vietnamese *trang web*. Separately, 16 cells are pointed at a named word in the cell rather than the automatic pick (French *pingouin*, Korean 미터 over the variant 메터, Vietnamese *ô-xy*, Turkish *tost*, and kilo's short form in 12 languages); they then go through kaikki/rule/translit as usual and say so in `note`.

### Spelling rules used (broad IPA; tone, stress and length marks dropped)

- **Spanish** (Latin American: seseo, yeísmo): c before e/i → s, z → s; g before e/i → x, j → x; qu/gu before e/i → k/ɡ; gü → ɡw; ch → tʃ; ll, y → ʝ (final y → i); ñ → ɲ; h silent; v → b; x → ks; zz → ts; r → ɾ, but r word-initially, after l n s and rr → r; unstressed i/u next to a vowel → j/w (accented í/ú stay vowels).
- **Quechua** (Southern, official alphabet): ch → tʃ, chh → tʃʰ, ch' → tʃʼ; kh k' ph p' th t' qh q' as aspirated/ejective; ll → ʎ; ñ → ɲ; sh → ʃ; y → j; r → ɾ. A word with Spanish-only letters or spellings (b d e g o f v z x, c not in ch, que/qui, rr, gu, accents) is a Spanish loan and goes through the Spanish rules.
- **Indonesian**: c → tʃ; j → dʒ; y → j; ny → ɲ; ng → ŋ; sy → ʃ; kh → x; e → ə (é → e). The e/ə ambiguity isn't resolved: loans like *kilometer* come out with ə where speakers say e (7 rule cells; most Indonesian cells are kaikki).
- **Tagalog**: ng → ŋ; ny, ñ → ɲ; ts, ch → tʃ; sy → ʃ; dy, j → dʒ; y → j; r → ɾ; c → k. A word with sh or a hyphen is an English spelling (above).
- **Swahili**: ch → tʃ; j → dʒ; sh → ʃ; ny → ɲ; ng' → ŋ; th → θ; dh → ð; gh → ɣ; kh → x; y → j; implosives not marked (b d g j as written).
- **Turkish**: c → dʒ; ç → tʃ; ş → ʃ; j → ʒ; ğ → nothing (lengthening dropped); ı → ɯ; ö → ø; ü → y; y → j; r → ɾ; â î û → a i u.
- **Yoruba**: ẹ → ɛ; ọ → ɔ; ṣ → ʃ; p → k͡p; gb → ɡ͡b; j → dʒ; y → j; r → ɾ; vowel + n not before a vowel → nasal vowel; a tone-marked n not before a vowel → syllabic n; doubled vowels (tone contours such as *éè*) → long vowel; tone marks dropped.
- **Hausa** (Boko): c → tʃ; j → dʒ; sh → ʃ; ts → sʼ; ƙ → kʼ; ɗ ɓ as written; 'y, ƴ → ʔʲ; y → j; f → ɸ; tone and vowel length not written in Boko, so not marked.
- **Vietnamese** (Hà Nội), per written syllable: initials ngh/ng → ŋ, nh → ɲ, ch/tr → tɕ, th → tʰ, ph → f, kh → x, gh/g → ɣ, gi/d/r → z, đ → ɗ, b → ɓ, x/s → s, c/k → k, qu → kw; vowels a → a, ă → a, â → ə, e → ɛ, ê → e, o → ɔ, ô → o, ơ → ə, ư → ɨ, iê/ia/yê → iə, uô/ua → uə, ươ/ưa → ɨə, o/u before a vowel → w; finals ch/c → k, nh → ɲ, ng → ŋ, i/y → j, o/u → w; tones dropped. An unadapted foreign spelling (letters f j w z, or several syllables written as one: *pizza, rupi, milimet*) is read letter by letter instead.

## Checks

- **Every cell where the chosen word wasn't the first listed** (all such notes read "chose X over Y") was read: in each, the chosen word is the loan (*kamera* over *fotoğraf makinesi*, ガレージ over 車庫, *docteur* over *médecin*). Two picks were wrong and are fixed by naming the word: Korean metre (the variant 메터 had been picked over 미터) and Vietnamese oxygen (the note *dưỡng khí* had been picked over *ôxy*).
- **kaikki entries with no matching sense** (48): all checked. Most are the right word with glosses that don't contain the English concept word (*pyjama*, *bisküvi*). Homographs with the same sound were kept (Bengali কম "less" for *com*, Hindi/Bengali বার/बार "time" for *bar*, Bengali জিন "jinn" for *gene*, Persian کام "wish" for *com*, Thai ก๊าซ, all said as the loan is). One homograph with a different sound was replaced by hand (Arabic كوم, above).
- **Transliterations and rule outputs**: read through in full; the tables were fixed where they misread (Arabic emphatics, Thai tones and doubled vowels, Indic ṉ ṟ ḻ, Yoruba syllabic nasals, Spanish stressed í, Vietnamese run-together syllables).
- **Not checked by a native speaker** or against audio. The romanisations come from the panel files, which are partly Wiktionary and partly memory.

## Problems for the analysis

- **The word, not just its sound, is sometimes uncertain.** Cells marked b often name the loan only in passing ("spoken *māsk*", "colloquial *balkōna*", "*restaurante* in bilingual speech"); the IPA is of that word as written in the cell.
- **Some recorded words are long compounds or carry a native part**: Mandarin 拖拉机, 啤酒, 酒吧, 三明治 and 俱乐部 are sound-and-meaning loans (the IPA covers the whole word); Turkish *web sitesi* came out as *sitesi* (with the possessive suffix); Tagalog *motor*, Indonesian *motor* are the short forms the cells list for motorcycle; Hindi टेलीविज़न was chosen over टीवी (both listed; the full form is closer to the median).
- **Shape-rule columns are far from the median by design**: coffee *qahwa*/*kahawa*/*kopi*/コーヒー, tobacco 담배, rupee ரூபாய், pound *fam* (Hausa) and *funt* (Russian) count as the loan under the source-shape rule, so they'll score as distant.
- **Indonesian rule cells** use ə for every e (above); **Hausa and Yoruba** rules don't mark tone or (Hausa) vowel length, which the analysis drops anyway.
- **robot, Yoruba** is marked b with no word, so it has no IPA.
- **Metric units** have derived marks and implied medians (above).
