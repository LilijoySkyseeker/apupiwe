"""Pull every kaikki entry whose headword is a candidate token from panel.tsv's word column.

Reads the Wiktextract dumps in ~/work/cache/coverage (untrusted data; run with python3 -I) and writes
~/work/scratch/loans-adapted-02/kaikki-hits.json: {lang: {word: [{pos, glosses, sounds}]}}.
"""
import csv, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokens import candidates

DUMP = "/home/agent/work/cache/coverage/kaikki-{}.jsonl.gz"
OUT = "/home/agent/work/scratch/loans-adapted-02/kaikki-hits.json"
LNAME = dict(zh="Chinese", ja="Japanese", ko="Korean", vi="Vietnamese", th="Thai", id="Indonesian", tl="Tagalog",
             hi="Hindi", bn="Bengali", ta="Tamil", fa="Persian", ar="Arabic", tr="Turkish", ru="Russian",
             es="Spanish", fr="French", sw="Swahili", ha="Hausa", yo="Yoruba", qu="Quechua")
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    want = {}
    for r in csv.DictReader(open(os.path.join(HERE, "panel.tsv")), delimiter="\t"):
        if r["mark"] in ("y", "b"):
            for _, keys in candidates(r["lang"], r["word"]):
                want.setdefault(r["lang"], set()).update(keys)
    hits = {}
    for lang, words in sorted(want.items()):
        scan(lang, words, hits.setdefault(lang, {}))
        # second pass: entries with no IPA that point to another headword (simplified -> traditional, alt forms)
        more = {l for w, es in hits[lang].items() if not any(e["sounds"] for e in es) for e in es for l in e["links"]}
        more -= set(hits[lang])
        if more:
            scan(lang, more, hits[lang])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(hits, open(OUT, "w"), ensure_ascii=False)


def scan(lang, words, h):
    if True:
        with gzip.open(DUMP.format(LNAME[lang]), "rt") as f:
            for line in f:
                d = json.loads(line)
                w = d.get("word")
                if w not in words:
                    continue
                glosses = [g for s in d.get("senses", []) for g in s.get("glosses", [])][:6]
                links = [x.get("word") for s in d.get("senses", []) for k in ("alt_of", "form_of") for x in s.get(k, [])]
                sounds = [s for s in d.get("sounds", []) if s.get("ipa")]
                h.setdefault(w, []).append(dict(pos=d.get("pos"), glosses=glosses, links=links, sounds=sounds))
        print(lang, len(words), "wanted,", len(h), "found", flush=True)


if __name__ == "__main__":
    main()
