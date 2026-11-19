"""Collect the final panel row (word, mark, median) for every loan in data/lexicon.tsv.

Writes panel.tsv (concept, adapted, median_ipa, lang, mark, word, src, note): one row per loan x language.
Sources, by loan: coverage-01/part3/loanwork/c01-c11.txt and older.txt (with verified.tsv applied),
deeplayer-02/loanwork/panel.txt, loans-02/loanwork/panel.txt, symbols-01/panel.tsv,
lexicon-ladder-01/loans.md (kilometre), coverage-01/part3/metric-panel.txt (other metric units: no marks
were recorded there, so this script derives them; see DATA.md).
"""
import csv, glob, os, re

REPO = "/home/agent/work/repos/universal-language"
T = REPO + "/tests/"
HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = "zh ja ko vi th id tl hi bn ta fa ar tr ru es fr sw ha yo qu".split()
NAME = dict(zip("Mandarin Japanese Korean Vietnamese Thai Indonesian Tagalog Hindi Bengali Tamil Persian Arabic "
                "Turkish Russian Spanish French Swahili Hausa Yoruba Quechua".split(), LANGS))


def parse_panel(path):
    """emit.parse format; the first block for a concept wins (as emit.py does)."""
    items, cur = {}, None
    for line in open(path):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("@ "):
            c = line[2:].split("|")[0].strip()
            cur = dict(rows={}, median="", note="", file=os.path.relpath(path, T))
            if c not in items:
                items[c] = cur
            continue
        m = re.match(r"(median|note|verdict|text):\s?(.*)", line)
        if m:
            if m.group(1) in ("median", "note"):
                cur[m.group(1)] = m.group(2)
            continue
        code, rest = line.split(" ", 1)
        w, mk, src = [x.strip() for x in rest.rsplit("|", 2)]
        cur["rows"][code] = (w, mk, src, "")
    return items


def coverage():
    ver = {(r["concept"], r["lang"]): r for r in
           csv.DictReader(open(T + "coverage-01/part3/loanwork/verified.tsv"), delimiter="\t")}
    out = {}
    files = sorted(glob.glob(T + "coverage-01/part3/loanwork/c[0-9][0-9].txt")) + [T + "coverage-01/part3/loanwork/older.txt"]
    for f in files:
        for c, it in parse_panel(f).items():
            for code, (w, mk, src, note) in list(it["rows"].items()):
                v = ver.get((c, code))
                if v:
                    r = v["result"]
                    new = mk if r == "yes" else ("n" if r == "no" else "u")
                    vn = f"verified.tsv: {r}" + (f" ({v['form']})" if v["form"] not in ("", "-") else "")
                    if new != mk:
                        vn += f"; recorded {mk} -> {new}"
                    it["rows"][code] = (w, new, src + "; verified", vn)
            out.setdefault(c, it)
    return out


def symbols():
    out = {}
    for r in csv.DictReader(open(T + "symbols-01/panel.tsv"), delimiter="\t"):
        c = {"com": ".com", "hashtag": "hashtag"}.get(r["form"])
        if not c:
            continue
        it = out.setdefault(c, dict(rows={}, median={".com": "kom", "hashtag": "haʃtag"}[c], note="",
                                    file="symbols-01/panel.tsv (median from symbols-01/README.md)"))
        it["rows"][r["lang"]] = (r["everyday"], r["shared"], r["src"], r.get("note") or "")
    return out


def kilometre():
    md = open(T + "lexicon-ladder-01/loans.md").read()
    sec = md.split("### kilometre", 1)[1].split("\n### ", 1)[0]
    it = dict(rows={}, median="kilometr", note="", file="lexicon-ladder-01/loans.md")
    for line in sec.splitlines():
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0] in NAME:
            mk = {"✓": "y", "✗": "n"}.get(cells[2], "b")
            it["rows"][NAME[cells[0]]] = (cells[1], mk, cells[3], "")
    return it


# The metric units were adopted as one set of parts (design log 2026-10-13: kilo, senti, mili + metulu, gulamu,
# litulu); no per-unit median was recorded. These are the medians those parts imply.
IMPLIED = dict(metre="metr", gram="gram", litre="litr", kilogram="kilogram", centimetre="sentimetr",
               millimetre="milimetr")


def metric():
    """metric-panel.txt lists Wiktionary translations only. Marks derived here: y when a listed form carries
    the international unit's consonants, n when only a native or calqued word is listed, u when the language
    is absent. kilo: the 12 languages the design log (2026-10-13, 'kilo is the everyday word') counts."""
    txt = open(T + "coverage-01/part3/metric-panel.txt").read()
    blocks = {}
    for part in txt.split("=== ")[1:]:
        name = part.split("\n", 1)[0].strip()
        body = part.split("\n", 1)[1] if "\n" in part else ""
        if "--- [" not in body:
            continue
        first = body.split("--- [", 1)[1].split("\n--- [", 1)[0]
        rows = {}
        for line in first.splitlines()[1:]:
            m = re.match(r"\s+(\w+): (.*)", line)
            if m and m.group(1) in NAME:
                rows[NAME[m.group(1)]] = m.group(2)
        blocks[name] = rows
    native = {"zh"}  # 米/克/升/公斤/厘米/毫米: Sino forms, n as the kilometre table marks 公里
    out = {}
    for name, rows in blocks.items():
        if name == "kilometre":
            continue
        it = dict(rows={}, median=IMPLIED[name], note="", file="coverage-01/part3/metric-panel.txt (marks derived; "
                  "median not recorded, implied by the design log's parts, 2026-10-13)")
        for c in LANGS:
            w = rows.get(c)
            if w is None:
                it["rows"][c] = ("(not listed)", "u", "-", "")
            elif c in native:
                it["rows"][c] = (w, "n", "Wt", "")
            elif c == "qu":
                it["rows"][c] = (w, "n", "Wt", "native word listed")
            else:
                it["rows"][c] = (w, "y", "Wt", "")
        out[name] = it
    # kilo, the short form
    kg = blocks["kilogram"]
    kilo_langs = "ja ko vi th hi bn ta tr ru fr sw yo".split()
    it = dict(rows={}, median="kilo", note="", file="coverage-01/part3/metric-panel.txt kilogram block; design log "
              "2026-10-13 (median not recorded; implied)")
    for c in LANGS:
        w = kg.get(c)
        if c in kilo_langs:
            it["rows"][c] = (w, "y", "Wt", "")
        elif c == "zh":
            it["rows"][c] = (w, "n", "Wt", "")
        else:
            it["rows"][c] = (w or "(not listed)", "u", "Wt" if w else "-", "short form kilo not listed for this language")
    out["kilo"] = it
    return out


def main():
    cov = coverage()
    dl = parse_panel(T + "deeplayer-02/loanwork/panel.txt")
    l2 = parse_panel(T + "loans-02/loanwork/panel.txt")
    sym = symbols()
    met = metric()
    met["kilometre"] = kilometre()
    lex = [r for r in csv.DictReader(open(REPO + "/data/lexicon.tsv"), delimiter="\t") if r["field"] == "loan"]
    out, missing = [], []
    for r in lex:
        g = r["gloss"]
        if g == "kilogram, everyday short form":
            key = "kilo"
        elif g.startswith(".com"):
            key = ".com"
        else:
            key = g.split(" (")[0].split(",")[0].strip()
        it = None
        for src in (cov, dl, l2, sym, met):
            if key in src:
                it = src[key]; break
        if not it:
            missing.append(g); continue
        for c in LANGS:
            w, mk, s, note = it["rows"].get(c, ("", "u", "-", "no row"))
            notes = ["panel: " + it["file"]] if c == "zh" else []
            if note:
                notes.append(note)
            out.append([r["gloss"], r["form"], f"[{it['median']}]" if it["median"] else "", c, mk, w, s, "; ".join(notes)])
    with open(os.path.join(HERE, "panel.tsv"), "w") as f:
        f.write("concept\tadapted\tmedian_ipa\tlang\tmark\tword\tsrc\tnote\n")
        for row in out:
            f.write("\t".join(x.replace("\t", " ") for x in row) + "\n")
    print(len(lex), "loans;", len(out), "rows; missing:", missing)


if __name__ == "__main__":
    main()
