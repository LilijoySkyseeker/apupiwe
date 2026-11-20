"""Every interjection (pos=intj) in the cached kaikki.org Wiktionary extracts for the 20 panel languages.
python3 -I extract.py > intj.tsv   (source: ~/work/cache/coverage/kaikki-*.jsonl.gz, fetched 2026-10-13)"""
import gzip, json, os, sys
C = os.path.expanduser("~/work/cache/coverage")
LANGS = ["Chinese","Japanese","Korean","Vietnamese","Thai","Indonesian","Tagalog","Hindi","Bengali","Tamil",
         "Persian","Arabic","Turkish","Russian","Spanish","French","Swahili","Hausa","Yoruba","Quechua"]
print("lang\tword\troman\tipa\ttags\tgloss")
for L in LANGS:
    for line in gzip.open(f"{C}/kaikki-{L}.jsonl.gz", "rt"):
        if '"pos": "intj"' not in line: continue
        e = json.loads(line)
        if e.get("pos") != "intj": continue
        if L == "Chinese" and not any("Mandarin" in json.dumps(s) for s in e.get("sounds", [])): continue
        ipa = next((s["ipa"] for s in e.get("sounds", []) if "ipa" in s), "")
        rom = next((f["form"] for f in e.get("forms", []) if "romanization" in f.get("tags", [])), "")
        for s in e.get("senses", []):
            g = "; ".join(s.get("glosses", [])[-1:])
            if not g: continue
            tags = ",".join(t for t in s.get("tags", []) if t in ("informal","colloquial","childish","slang","dated","obsolete","archaic","rare","literary","dialectal","vulgar","regional"))
            print("\t".join([L, e["word"], rom, ipa, tags, g.replace("\t"," ")[:200]]))
