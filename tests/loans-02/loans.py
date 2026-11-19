"""loans-02: score the 4 standard-word loan candidates (planet, temperature, oxygen, mass) (loanwork/panel.txt) under the panel rule of 2026-10-15
(at least 12 of 20 languages across at least 5 of the 7 regions), adapt passing medians with tools/names.py,
and check collisions and tools/offensive.py. Writes loans.tsv here.

  direnv exec /home/agent/work/repos/universal-language python3 tests/loans-02/loans.py

A column counts when marked y or b and attested: its source names Wt, We, subs or Leipzig (a memory-only
column, M, counts only once sourced; author 2026-10-13). 'ceiling' adds the u (no data) and memory-only
columns, to show whether any unknown could change a verdict.
"""
import csv, os, re, sys
REPO = "/home/agent/work/repos/universal-language"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO + "/tools")
os.chdir(REPO + "/tools")
import names, offensive, accent

LANGS = [("zh", "EA"), ("ja", "EA"), ("ko", "EA"), ("vi", "SEA"), ("th", "SEA"), ("id", "SEA"), ("tl", "SEA"),
         ("hi", "SA"), ("bn", "SA"), ("ta", "SA"), ("fa", "WA"), ("ar", "WA"), ("tr", "WA"), ("ru", "EU"),
         ("es", "EU"), ("fr", "EU"), ("sw", "SSA"), ("ha", "SSA"), ("yo", "SSA"), ("qu", "AM")]
REG = dict(LANGS)
ORDER = ["EA", "SEA", "SA", "WA", "EU", "SSA", "AM"]


def parse(path):
    items, cur = [], None
    for line in open(path):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("@ "):
            c, page, sense = [x.strip() for x in line[2:].split("|", 2)]
            cur = dict(concept=c, page=page, sense=sense, rows={}, median="", note="", text=[])
            items.append(cur); continue
        m = re.match(r"(median|note|text):\s?(.*)", line)
        if m:
            k, v = m.groups()
            (cur["text"].append(v) if k == "text" else cur.__setitem__(k, v)); continue
        code, rest = line.split(" ", 1)
        word, mark, src = [x.strip() for x in rest.rsplit("|", 2)]
        assert mark in ("y", "n", "b", "u") and code in REG, line
        cur["rows"][code] = (word, mark, src)
    for it in items:
        assert set(it["rows"]) == set(REG), it["concept"]
    return items


def attested(src):
    return any(s in src for s in ("Wt", "We", "subs", "Leipzig"))


def score(it):
    got = [c for c, (w, m, s) in it["rows"].items() if m in "yb" and attested(s)]
    ceil = [c for c, (w, m, s) in it["rows"].items() if m in "ybu"]
    regs = sorted({REG[c] for c in got}, key=ORDER.index)
    cregs = {REG[c] for c in ceil}
    ok = len(got) >= 12 and len(regs) >= 5
    return got, regs, len(ceil), len(cregs), "pass" if ok else "fail"


# collisions: every form the language already uses
FORMS = {}
for name, col in (("lexicon.tsv", "gloss"), ("grammar.tsv", "gloss"), ("numbers.tsv", "value")):
    for r in csv.DictReader(open(os.path.join(REPO, "data", name)), delimiter="\t"):
        FORMS.setdefault(r["form"], []).append(f"{r[col]} ({name.split('.')[0]})")
spell = open(os.path.join(REPO, "docs", "language.md")).read().split('id="r-11-5"')[1].split("##")[0]
for w in re.findall(r"\*\*([a-z]+)\*\*", spell):
    FORMS.setdefault(w, []).append("spelling word (language.md 11.5)")

# What a failing candidate becomes (frequency: all four are on the root list, concepts.tsv tiers 1-2; then the phrase
# line: a phrase only if <=3 syllables or the world's usual compound). Phrase words use today's lexicon forms.
FALLBACK = {
    "planet": "phrase: segin kobi 'moving star', the world's usual compound (zh xingxing, ja wakusei, ko, vi hanh tinh, "
              "ar kawkab sayyar, fa sayyare, tr gezegen, sw sayari, qu puriq quyllur); else a root",
    "temperature": "phrase: kote pi tikun 'level of heat', the world's usual compound (zh wendu, ja/ko ondo, vi nhiet do, "
                   "th, hi tapman, bn, ta, fa, ar darajat al-harara, sw halijoto); tikun is also 'spicy'; else a root",
    "mass": "root 'mass' (tier 1, no world compound across regions); or widen gogo 'heavy' to the noun 'mass, weight' "
            "(the everyday lump in tl bn ta sw ha qu); author's call",
}

rows = []
for it in parse(os.path.join(HERE, "loanwork", "panel.txt")):
    got, regs, cn, cr, v = score(it)
    form = coll = blk = mt = ""
    if v == "pass":
        form = names.adapt(it["median"])
        coll = "; ".join(FORMS.get(form, [])) or "none"
        blk, mt = str(offensive.blocked(form)).lower(), str(offensive.matches(form)).lower()
        nb = [f"{n} = {'; '.join(FORMS[n])}" for n in accent.neighbours(form) if n in FORMS]
        nb_txt = "; ".join(nb) or f"none (checked {' '.join(accent.neighbours(form))})"
        coll += "; accent 2.12: " + nb_txt
    rows.append([it["concept"], f"{len(got)}/20", f"{len(regs)} ({' '.join(regs)})", f"{cn}/{cr}", v,
                 f"[{it['median']}]", form, coll, blk, mt, FALLBACK.get(it["concept"], "loan " + form), it["note"]])
with open(os.path.join(HERE, "loans.tsv"), "w") as f:
    f.write("concept\tcount\tregions\tceiling_count/regions\tverdict\tmedian_ipa\tadapted\tcollision\t"
            "offensive_blocked\toffensive_matches\tdecision\tnote\n")
    for r in rows:
        f.write("\t".join(r) + "\n"); print(*r[:10], sep="\t")
