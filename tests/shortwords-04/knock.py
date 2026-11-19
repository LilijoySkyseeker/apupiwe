"""Knock-on check for a candidate short-word layer: content roots that the new grammar forms would make illegal.
  - haplology (design log 2026-10-15): a grammar word that stands right before a content word >= 10 times in the
    corpus (tests/placement-03/bigrams.tsv, by gloss) bans its syllable as a root's first syllable
  - juncture.py on the lexicon with the new grammar forms
  python3 knock.py LAYER.tsv
"""
import csv, io, os, re, runpy, sys, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import words as W

layer = {r["gloss"]: r["new"] for r in csv.DictReader((l for l in open(sys.argv[1]) if not l.startswith("#")), delimiter="\t")}
big = list(csv.DictReader(open(os.path.join(ROOT, "tests/placement-03/bigrams.tsv")), delimiter="\t"))
gram = W.read("grammar.tsv")
haplo_old = {r["form"] for r in big if int(r["before_content"]) >= 10 and r["gloss"] in {g["gloss"] for g in gram}}
haplo_new = {layer.get(r["gloss"], r["form"]) for r in big if int(r["before_content"]) >= 10 and r["gloss"] in layer}
lex = W.read("lexicon.tsv")
fixed_routes = {"loan"}
first = lambda f: W.SYL[W.split(f)[0]]
bad = [r for r in lex if r["field"] != "loan" and first(r["form"]) in haplo_new and first(r["form"]) not in haplo_old]
print(f"haplology syllables: old {sorted(haplo_old)}\n                     new {sorted(haplo_new)}")
print(f"roots newly starting with a banned syllable: {len(bad)}: " + ", ".join(f"{r['form']} {r['gloss']} (t{r['tier']})" for r in bad))

rows = [dict(g, form=layer.get(g["gloss"], g["form"])) for g in gram]
orig = W.read
W.read = lambda name: rows if name == "grammar.tsv" else orig(name)
buf = io.StringIO(); code = 0
try:
    with contextlib.redirect_stdout(buf):
        runpy.run_path(os.path.join(ROOT, "tools", "juncture.py"))
except SystemExit as e:
    code = e.code
W.read = orig
print(f"juncture.py with the new grammar forms: exit {code}\n" + buf.getvalue().strip())
