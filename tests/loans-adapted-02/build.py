"""Build forms.tsv: one row per loan x panel language, with broad IPA of the language's word for y/b cells.

Order of preference per cell: kaikki IPA for a candidate token of the word field; else the spelling rules in
rules.py (es id tl sw tr yo ha qu vi); else a transliteration of the romanisation the panel recorded
(rules.translit). Among a cell's candidates the one closest to the loan's median (or adapted form) wins, so a
native word listed beside the loan isn't picked. Run panel.py and kaikki_pull.py first.
"""
import csv, difflib, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tokens import groups
import rules

HITS = "/home/agent/work/scratch/loans-adapted-02/kaikki-hits.json"
RULE_LANGS = set("es id tl sw tr yo ha qu vi".split())
BAD = ("nonstandard", "proscribed", "Cantonese", "Dari", "Tajik", "Classical-Persian", "Kabuli", "Huế", "Canada",
       "Quebec", "Belgium", "Louisiana", "Egyptian", "Hijazi", "Levantine", "South-Levantine", "Morocco", "Kuwait",
       "Egypt", "letter", "phoneme")
PREFER = dict(zh=("Mandarin",), fa=("Iran", "Tehrani"), vi=("Hà-Nội",), tl=("Standard-Tagalog",))

SIMPLE = str.maketrans({"ɑ": "a", "ɐ": "a", "æ": "a", "ä": "a", "ɛ": "e", "ə": "e", "ɘ": "e", "ɪ": "i", "ʊ": "u",
                        "ɔ": "o", "ɒ": "o", "ɯ": "u", "ɨ": "i", "ʌ": "a", "ʃ": "s", "ʒ": "z", "ɕ": "s", "ʑ": "z",
                        "ɾ": "r", "ɹ": "r", "ʁ": "r", "ʀ": "r", "ɻ": "r", "ɽ": "r", "ɡ": "g", "ɲ": "n", "ŋ": "n",
                        "β": "b", "ð": "d", "ɣ": "g", "χ": "h", "x": "h", "ɸ": "f", "ʋ": "v", "ʝ": "j", "ɟ": "j",
                        "ç": "h", "ʈ": "t", "ɖ": "d", "ɳ": "n", "ɭ": "l", "ʎ": "l", "ɓ": "b", "ɗ": "d", "ʔ": "",
                        "y": "i", "c": "k", "q": "k", "w": "u", "j": "i", "ø": "o", "œ": "e", "ɵ": "o", "ʂ": "s",
                        "ʐ": "z", "ɦ": "h", "ɫ": "l", "ʲ": "", "ʰ": "", "ʷ": "", "ʼ": "", "'": "", "v": "b", "p": "b",
                        "t": "d", "k": "g", "s": "s", "ɤ": "o"})


def simple(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[\[\]/ˈˌː.\-‿͡ ˀ˥˦˧˨˩⁰¹²³⁴⁵⁶⁷⁸⁹()~]", "", s)
    s = s.translate(SIMPLE)
    s = s.replace("dz", "z").replace("ds", "s").replace("ts", "s").replace("dʃ", "s")
    return re.sub(r"[^a-z]", "", s)


def sim(a, b):
    """Resemblance of candidate a to target b; also against a's start, so a short form (moto) matches a long
    word (motorcycle)."""
    a, b = simple(a), simple(b)
    if not a or not b:
        return 0.0
    full = difflib.SequenceMatcher(None, a, b).ratio()
    head = difflib.SequenceMatcher(None, a[:len(b) + 1], b).ratio() * 0.9
    return max(full, head)


def pick_ipa(lang, entries, concept):
    """First IPA of the standard variety, from the entry whose sense matches the concept if any."""
    key = re.split(r"[ ,(]", concept.lower())[0]
    ordered = sorted(entries, key=lambda e: 0 if any(key in g.lower() for g in e["glosses"]) else 1)
    for e in ordered:
        snd = [s for s in e["sounds"] if not any(t in BAD for t in s.get("tags", []) + s.get("raw_tags", []))]
        if lang in PREFER:
            pref = [s for s in snd if any(t in PREFER[lang] for t in s.get("tags", []) + s.get("raw_tags", []))]
            snd = pref or ([] if lang == "zh" else snd)
        if lang == "es":  # seseo, the majority pronunciation (Latin America, Andalusia, Canaries)
            snd = [x for x in snd if "θ" not in x["ipa"]] or snd
        if snd:
            return snd[0]["ipa"], any(key in g.lower() for g in e["glosses"])
    return None, False


# Cells the automatic pass can't read: an English spelling recorded for a spoken loan, a word outside the cell's
# main text, or a script the transliterator gets wrong. (concept start, lang) -> ("token", word to look up)
# or ("ipa", ipa, note). Every one is a broad reading by hand, labelled translit.
OVERRIDES = {
    (".com", "zh"): ("ipa", "kʰɔm", "English reading of com"),
    ("hashtag", "bn"): ("ipa", "hæʃʈæɡ", "Bengali ্যা read as æ"),
    ("hashtag", "ta"): ("ipa", "haʃʈæɡ", "English spelling in the cell; Indian-English reading"),
    ("radio", "ta"): ("ipa", "reːɖijoː", "English spelling in the cell; Indian-English reading"),
    ("helicopter", "ta"): ("ipa", "helikaːpʈar", "English spelling in the cell; Indian-English reading"),
    ("T-shirt", "ta"): ("ipa", "ʈiːʃarʈ", "English spelling in the cell; Indian-English reading"),
    ("gas", "ta"): ("ipa", "ɡaːs", "English spelling in the cell; Indian-English reading"),
    ("vaccine", "ta"): ("ipa", "vaːksin", "English spelling in the cell; Indian-English reading"),
    ("technology", "bn"): ("ipa", "ʈeknolodʒi", "English spelling in the cell; Indian-English reading"),
    ("toast", "fa"): ("ipa", "tost", "the loan part of nān-e tost"),
    ("penguin", "fr"): ("token", "pingouin"),
    ("website", "vi"): ("ipa", "tɕaːŋ wɛp", "the whole phrase; the cell names no site-shaped word"),
    ("metre", "ko"): ("token", "미터"),
    ("oxygen", "vi"): ("token", "ô-xy"),
    ("toast", "tr"): ("token", "tost"),
    (".com", "ar"): ("ipa", "kom", "kaikki كوم is the homograph 'heap' /kawm/; the domain ending is said [kom]"),
    ("kilogram, everyday", "ja"): ("token", "キロ"), ("kilogram, everyday", "ko"): ("token", "킬로"),
    ("kilogram, everyday", "vi"): ("token", "ki-lô"), ("kilogram, everyday", "th"): ("token", "กิโล"),
    ("kilogram, everyday", "hi"): ("token", "किलो"), ("kilogram, everyday", "bn"): ("token", "কিলো"),
    ("kilogram, everyday", "ta"): ("token", "கிலோ"), ("kilogram, everyday", "tr"): ("token", "kilo"),
    ("kilogram, everyday", "ru"): ("token", "кило́"), ("kilogram, everyday", "fr"): ("token", "kilo"),
    ("kilogram, everyday", "sw"): ("token", "kilo"), ("kilogram, everyday", "yo"): ("token", "kílò"),
}


def override(r):
    for (c, l), v in OVERRIDES.items():
        if r["lang"] == l and r["concept"].startswith(c):
            return v
    return None


def main():
    hits = json.load(open(HITS))
    rows = list(csv.DictReader(open(os.path.join(HERE, "panel.tsv")), delimiter="\t"))
    out, stats = [], {}
    for r in rows:
        lang, mark = r["lang"], r["mark"]
        ipa, source, notes = "", "", [r["note"]] if r["note"] else []
        if mark in ("y", "b"):
            target = r["median_ipa"].strip("[]") or rules.adapted_ipa(r["adapted"])
            cands = []  # (score, token, kaikki ipa or None, other ipa, other source)
            ov = override(r)
            if ov and ov[0] == "ipa":
                out.append([r["concept"], r["adapted"], r["median_ipa"], lang, mark, r["word"], ov[1],
                            "translit: by hand", "; ".join(notes + [ov[2]])])
                stats["translit"] = stats.get("translit", 0) + 1
                continue
            gs = groups(lang, ov[1]) if ov else groups(lang, r["word"])
            if ov:
                notes.append(f"the cell's word {ov[1]} used")
            for g in gs:
                kipa, sense_ok, kkey = None, False, None
                for k in g["keys"]:
                    ents = hits.get(lang, {}).get(k)
                    if ents:
                        kipa, sense_ok = pick_ipa(lang, ents, r["concept"])
                        if kipa:
                            kkey = k; break
                other, osrc = "", ""
                if lang in RULE_LANGS and g["latin"] and g["latin"].lower() in rules.ENGLISH:
                    other, osrc = rules.ENGLISH[g["latin"].lower()], "translit"
                elif lang in RULE_LANGS and g["latin"]:
                    other, osrc = rules.spell(lang, g["latin"]), f"rule-{lang}"
                elif g["latin"]:
                    other, osrc = rules.translit(lang, g["latin"]), "translit"
                if not other and g["script"]:
                    other, osrc = rules.script(lang, g["script"]), "translit"
                # resemblance of the word itself: its best representation (romanisation as written counts too)
                reps = [x for x in (kipa, other, g["latin"]) if x]
                if not reps:
                    continue
                score = max(sim(x, target) for x in reps)
                cands.append((score, g["script"] or g["latin"], kipa, sense_ok, kkey, other, osrc, g["latin"]))
            if cands:
                top = max(c[0] for c in cands)
                # among near-equal candidates, prefer one with a kaikki IPA, then the first listed
                near = [c for c in cands if c[0] >= top - 0.05]
                best = next((c for c in near if c[2]), near[0])
                score, tok, kipa, sense_ok, kkey, other, osrc, lat = best
                if kipa:
                    ipa, source = kipa, f"kaikki: {kkey}" + ("" if sense_ok else " (no sense gloss matched)")
                elif other:
                    ipa, source = other, f"{osrc}: {lat if osrc != 'translit' or lat else tok}"
                else:
                    ipa, source = "", "none"
                if best is not cands[0] and cands[0][1] not in tok and tok not in cands[0][1]:
                    notes.append(f"chose {tok} over {cands[0][1]}")
            else:
                source = "none"
            stats.setdefault(source.split(":")[0].split(" ")[0], 0)
            stats[source.split(":")[0].split(" ")[0]] += 1
        out.append([r["concept"], r["adapted"], r["median_ipa"], lang, mark, r["word"], ipa, source, "; ".join(notes)])
    with open(os.path.join(HERE, "forms.tsv"), "w") as f:
        f.write("concept\tadapted\tmedian_ipa\tlang\tmark\tword\tipa\tipa_source\tnote\n")
        for row in out:
            f.write("\t".join(x.replace("\t", " ") for x in row) + "\n")
    print(stats)


if __name__ == "__main__":
    main()
