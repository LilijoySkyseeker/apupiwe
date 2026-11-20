#!/usr/bin/env python3
"""World prevalence of Apupiwe's grammatical features (tests/typology-01).

Usage: python3 -I compute.py GRAMBANK_CLDF_DIR WALS_CLDF_DIR

Reads features.psv (next to this script), computes for every database measure
  n      languages coded for all parameters in the measure (no '?')
  share  k/n, languages with the matching values
  fam    family-balanced share: mean over families of each family's share
         (an isolate, or a WALS "other" language, is its own family)
  areas  macro-areas (of 6) with at least one matching language, and with
         a share of at least 10% among that area's coded languages
writes results.tsv and replaces the table in README.md between the markers.

Grambank: language-level lects only (dialect rows dropped). WALS: all languages.
The first measure of a row is primary: the closest match, and where Grambank
and WALS match equally well, Grambank (the larger sample).
Class from the primary measure (class=auto):
  converged  fam >= 0.50
  common     0.10 <= fam < 0.50 and >= 3 macro-areas at >= 10%
  regional   otherwise, when k > 0
  invented   k == 0
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
csv.field_size_limit(10**9)


def load_grambank(d):
    d = Path(d)
    langs = {}
    for r in csv.DictReader(open(d / "languages.csv", encoding="utf-8")):
        if r["level"] != "language":
            continue
        langs[r["ID"]] = (r["Family_level_ID"] or "iso:" + r["ID"], r["Macroarea"])
    vals = defaultdict(dict)
    for r in csv.DictReader(open(d / "values.csv", encoding="utf-8")):
        if r["Language_ID"] in langs and r["Value"] not in ("?", ""):
            vals[r["Parameter_ID"]][r["Language_ID"]] = r["Value"]
    return langs, vals


def load_wals(d):
    d = Path(d)
    langs = {}
    for r in csv.DictReader(open(d / "languages.csv", encoding="utf-8")):
        if not r["Family"]:
            continue  # genus/family rows, not languages
        fam = r["Family"]
        if fam.lower() == "other":
            fam = "other:" + r["ID"]
        langs[r["ID"]] = (fam, r["Macroarea"])
    vals = defaultdict(dict)
    for r in csv.DictReader(open(d / "values.csv", encoding="utf-8")):
        if r["Language_ID"] in langs:
            vals[r["Parameter_ID"]][r["Language_ID"]] = r["Value"]
    names = {}
    for r in csv.DictReader(open(d / "codes.csv", encoding="utf-8")):
        names[(r["Parameter_ID"], r["Number"])] = r["Name"]
    return langs, vals, names


def parse(expr):
    """'GB070=0&GB044=0' -> [('GB070', {'0'}), ...]"""
    out = []
    for part in expr.split("&"):
        p, v = part.split("=")
        out.append((p.strip(), {x.strip() for x in v.split(",")}))
    return out


def measure(langs, vals, conds):
    coded = None
    for p, _ in conds:
        s = set(vals.get(p, {}))
        coded = s if coded is None else coded & s
    coded = coded or set()
    hit = {l for l in coded if all(vals[p][l] in vs for p, vs in conds)}
    fam_n, fam_k = defaultdict(int), defaultdict(int)
    area_n, area_k = defaultdict(int), defaultdict(int)
    for l in coded:
        f, a = langs[l]
        fam_n[f] += 1
        area_n[a] += 1
        if l in hit:
            fam_k[f] += 1
            area_k[a] += 1
    n, k = len(coded), len(hit)
    fam = sum(fam_k[f] / fam_n[f] for f in fam_n) / len(fam_n) if fam_n else 0.0
    areas_any = sum(1 for a in area_k if a and area_k[a] > 0)
    areas_10 = sum(1 for a in area_n if a and area_k[a] / area_n[a] >= 0.10)
    by_area = ", ".join(f"{a} {100 * area_k[a] / area_n[a]:.0f}%"
                        for a in sorted(area_n) if a)
    return dict(n=n, k=k, share=k / n if n else 0.0, fam=fam, nfam=len(fam_n),
                areas_any=areas_any, areas_10=areas_10, by_area=by_area)


def auto_class(m):
    if m["k"] == 0:
        return "invented"
    if m["fam"] >= 0.50:
        return "converged"
    if m["fam"] >= 0.10 and m["areas_10"] >= 3:
        return "common"
    return "regional"


def label(db, conds, wnames):
    parts = []
    for p, vs in conds:
        if db == "WALS":
            parts.append(p + " " + "/".join(wnames.get((p, v), v) for v in sorted(vs)))
        else:
            parts.append(p + "=" + "/".join(sorted(vs)))
    return db + " " + " & ".join(parts)


def main():
    gb_dir, wals_dir = sys.argv[1], sys.argv[2]
    gb_langs, gb_vals = load_grambank(gb_dir)
    w_langs, w_vals, w_names = load_wals(wals_dir)
    rows = []
    for line in open(HERE / "features.psv", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = [x.strip() for x in line.rstrip("\n").split("|")]
        if f[0] == "id":
            continue
        rows.append(dict(zip(["id", "feature", "rule", "apupiwe", "measures",
                              "match", "class", "note"], f)))
    out = []
    for r in rows:
        ms = []
        if r["measures"] != "none":
            for m in r["measures"].split(";"):
                db, expr = m.strip().split(":", 1)
                conds = parse(expr)
                if db == "GB":
                    res = measure(gb_langs, gb_vals, conds)
                else:
                    res = measure(w_langs, w_vals, conds)
                res["label"] = label(db, conds, w_names)
                ms.append(res)
        r["ms"] = ms
        if r["class"] == "auto":
            r["final"] = auto_class(ms[0])
        else:
            r["final"] = r["class"]
            r["auto"] = auto_class(ms[0]) if ms else ""
        out.append(r)

    with open(HERE / "results.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["id", "measure", "n", "k", "share", "family_balanced",
                    "families", "areas_any", "areas_10pct", "class", "share_by_area"])
        for r in out:
            for i, m in enumerate(r["ms"]):
                w.writerow([r["id"], m["label"], m["n"], m["k"], f"{m['share']:.3f}",
                            f"{m['fam']:.3f}", m["nfam"], m["areas_any"], m["areas_10"],
                            r["final"] if i == 0 else "", m["by_area"]])
            if not r["ms"]:
                w.writerow([r["id"], "none", "", "", "", "", "", "", "", r["final"], ""])

    def esc(s):
        return s.replace("|", "\\|")

    lines = ["| id | feature | rule | Apupiwe's version | database feature(s) | share | family-balanced | macro-areas (any / ≥10%) | class | match | source / note |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out:
        if r["ms"]:
            feat = "<br>".join(f"{m['label']} (n={m['n']})" for m in r["ms"])
            share = "<br>".join(f"{100*m['share']:.0f}%" for m in r["ms"])
            fam = "<br>".join(f"{100*m['fam']:.0f}%" for m in r["ms"])
            areas = "<br>".join(f"{m['areas_any']} / {m['areas_10']}" for m in r["ms"])
        else:
            feat, share, fam, areas = "none", "–", "–", "–"
        rules = ", ".join(f"[{x}](../../docs/language.md#{x})" for x in r["rule"].split(";"))
        cls = f"**{r['final']}**"
        if r["class"] != "auto" and r.get("auto") and r["auto"] != r["final"]:
            cls += f" (numbers alone: {r['auto']})"
        lines.append("| " + " | ".join(esc(x) for x in [
            r["id"], r["feature"], rules, r["apupiwe"], feat, share, fam, areas,
            cls, r["match"], r["note"]]) + " |")
    table = "\n".join(lines)

    counts = defaultdict(list)
    for r in out:
        counts[r["final"]].append(r["id"])
    summary = "\n".join(f"- **{c}**: {len(counts[c])} ({', '.join(counts[c])})"
                        for c in ["converged", "common", "regional", "invented"])

    readme = HERE / "README.md"
    text = readme.read_text(encoding="utf-8")
    for tag, body in (("table", table), ("counts", summary)):
        a, b = f"<!-- {tag} -->", f"<!-- /{tag} -->"
        i, j = text.index(a) + len(a), text.index(b)
        text = text[:i] + "\n" + body + "\n" + text[j:]
    readme.write_text(text, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
