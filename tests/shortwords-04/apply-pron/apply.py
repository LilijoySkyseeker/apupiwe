"""Apply map.tsv here (the re-formed short words and the 18 re-placed roots, design log 2026-11-19) to the repo.
Copy of tests/placement-03/apply.py, plus `literals` (only inside "..." in code files) and `cols N` (first N tsv columns).

  python3 apply.py data            # data/lexicon.tsv, numbers.tsv, compounds.tsv, roles.tsv, antonyms.tsv; writes map.tsv
                                   # (old form -> new form) and roles-todo.tsv (new roots with no roles row yet)
  python3 apply.py text FILE ...   # replace old forms by new ones, token by token, in Apupiwe text only (see below)
  python3 apply.py left FILE ...   # list old forms still present in Apupiwe spans (for review)
  python3 apply.py tokens FILE ... # files that are wholly Apupiwe, or code: every lowercase whole-word old form
                                   # (tests/udhr-01/translation.md, grammar/intended.tsv, grammar/*.gf literals and comments)

Text rule (as tests/shortwords-03/APPLY.md): the map is applied simultaneously, one pass per text, so chains and swaps
(nebe -> panwe while lenu -> nebi) can't cascade. In markdown, only **bold** spans are Apupiwe, and only when every
token in the span is a known Apupiwe word (old or new forms, grammar words, digits; a name right after fo is allowed).
In spec/reference.toml every string is checked the same way, plus the fields that are wholly Apupiwe (apu = "...").
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "data")


def read(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


def write(path, rows, cols):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    os.replace(tmp, path)


FORMS = []   # 04: the data step was done by hand
MAP_PATH = os.path.join(HERE, "map.tsv")


def load_map():
    return {r["old"]: r["new"] for r in read(MAP_PATH)}


def cmd_data():
    lex = read(os.path.join(DATA, "lexicon.tsv"))
    concepts = [r for r in FORMS if r["route"] != "operator (fixed)" and r["new form"]]
    by_gloss = {r["concept"]: r for r in concepts}
    by_old = {}
    for r in concepts:
        if r["old form"] and r["route"] == "root":
            by_old.setdefault(r["old form"], r)
    for r in concepts:
        if r["old form"]:
            by_old.setdefault(r["old form"], r)
    ops = {r["old form"] for r in FORMS if r["route"] == "operator (fixed)"}

    out, used, fmap = [], set(), {}
    for row in lex:
        if row["form"] in ops:
            out.append(dict(row)); continue
        c = by_gloss.get(row["gloss"]) or by_old.get(row["form"])
        if c is None or c["concept"] in used:
            sys.exit(f"no concept for lexicon row {row}")
        used.add(c["concept"])
        out.append({"gloss": c["concept"], "field": c["field"], "tier": c["tier"], "form": c["new form"]})
        if c["new form"] != row["form"]:
            fmap[row["form"]] = c["new form"]
    for c in concepts:
        if c["concept"] not in used:
            out.append({"gloss": c["concept"], "field": c["field"], "tier": c["tier"], "form": c["new form"]})
    forms = [r["form"] for r in out]
    assert len(forms) == len(set(forms)), [f for f in forms if forms.count(f) > 1]
    write(os.path.join(DATA, "lexicon.tsv"), out, ["gloss", "field", "tier", "form"])
    write(MAP_PATH, [{"old": k, "new": v} for k, v in sorted(fmap.items())], ["old", "new"])
    print(f"lexicon: {len(lex)} -> {len(out)} rows; {len(fmap)} forms change (map.tsv)")

    nums = read(os.path.join(DATA, "numbers.tsv"))
    for r in nums:
        r["form"] = fmap.get(r["form"], r["form"])
    write(os.path.join(DATA, "numbers.tsv"), nums, ["value", "kind", "form"])

    comp = read(os.path.join(DATA, "compounds.tsv"))
    n = 0
    for r in comp:
        new = " ".join(fmap.get(t, t) for t in r["form"].split())
        n += new != r["form"]
        r["form"] = new
    write(os.path.join(DATA, "compounds.tsv"), comp, ["gloss", "form", "literal"])
    print(f"compounds: {n} of {len(comp)} changed")

    roles = read(os.path.join(DATA, "roles.tsv"))
    rcols = list(roles[0].keys())
    for r in roles:
        r["form"] = fmap.get(r["form"], r["form"])
    have = {r["form"] for r in roles}
    content = [r for r in out if r["form"] not in ops and r["field"] != "number"]
    todo = [r for r in content if r["form"] not in have]
    keep = {r["form"] for r in out}
    roles = [r for r in roles if r["form"] in keep]
    write(os.path.join(DATA, "roles.tsv"), sorted(roles, key=lambda r: r["form"]), rcols)
    write(os.path.join(HERE, "roles-todo.tsv"), todo, ["form", "gloss", "field", "tier"])
    print(f"roles: {len(roles)} rows kept (forms remapped); {len(todo)} new roots need a row (roles-todo.tsv)")

    # antonyms: rename glosses, and add the concept list's antonym column (decided 2026-10-16: "the added antonym
    # pairs are kept"), via placement-01's parser
    sys.path.insert(0, HERE)
    sys.argv = [sys.argv[0], "--no-vbonus"]
    import place as P
    ren = {}
    for row in lex:
        c = by_gloss.get(row["gloss"]) or by_old.get(row["form"])
        if c and c["concept"] != row["gloss"]:
            ren[row["gloss"]] = c["concept"]
    lines = [l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "antonyms.tsv")) if l.strip()]
    pairs = [tuple(ren.get(g, g) for g in p) for p in lines]
    seen = {frozenset(p) for p in pairs}
    glosses = {r["gloss"] for r in out}
    added = 0
    for a, b in P.ANT_PAIRS:
        ga, gb = P.ITEMS[a]["gloss"], P.ITEMS[b]["gloss"]
        if frozenset((ga, gb)) not in seen and ga in glosses and gb in glosses:
            pairs.append((ga, gb)); seen.add(frozenset((ga, gb))); added += 1
    with open(os.path.join(DATA, "antonyms.tsv"), "w") as fh:
        for p in pairs:
            fh.write("\t".join(p) + "\n")
    print(f"antonyms: {len(lines)} -> {len(pairs)} pairs ({added} from the concept list); glosses renamed: {ren}")


# ------------------------------------------------------------------------------------------ text
def known_words():
    w = set()
    for r in read(os.path.join(DATA, "lexicon.tsv")):
        w.add(r["form"])
    for r in read(os.path.join(DATA, "grammar.tsv")):
        w.add(r["form"])
    for r in read(os.path.join(DATA, "numbers.tsv")):
        w.add(r["form"])
    w |= set(load_map())
    return w


TOK = re.compile(r"[a-z]+")


def remap_span(span, M, K):
    toks = TOK.findall(span.lower())
    names = {t for a, t in zip(toks, toks[1:]) if a == "fo" and t not in K}   # a name after fo (NAME) is not checked
    if not toks or any(t not in K and t not in names for t in toks):
        return span, False
    if not any(t in M for t in toks):
        return span, False
    def sub(m):
        t = m.group(0)
        if t in M:
            return M[t]
        if t.lower() in M and t[0].isupper():
            n = M[t.lower()]
            return n[0].upper() + n[1:]
        return t
    return re.sub(r"[A-Za-z]+", sub, span), True


def apply_text(path, M, K, dry=False):
    s = open(path).read()
    hits = []
    if path.endswith(".toml"):
        def q(m):
            new, ch = remap_span(m.group(2), M, K)
            if ch:
                hits.append((m.group(2), new))
            return m.group(1) + new + m.group(3)
        s2 = re.sub(r'(")([^"\n]*)(")', q, s)
        # bold spans inside longer strings
        def b(m):
            new, ch = remap_span(m.group(1), M, K)
            if ch:
                hits.append((m.group(1), new))
            return "**" + new + "**"
        s2 = re.sub(r"\*\*([^*\n]+)\*\*", b, s2)
    else:
        def b(m):
            new, ch = remap_span(m.group(1), M, K)
            if ch:
                hits.append((m.group(1), new))
            return "**" + new + "**"
        s2 = re.sub(r"\*\*([^*\n]+)\*\*", b, s)
    if not dry and s2 != s:
        open(path + ".tmp", "w").write(s2)
        os.replace(path + ".tmp", path)
    return hits


def cmd_text(files):
    M, K = load_map(), known_words()
    for f in files:
        hits = apply_text(f, M, K)
        print(f"{f}: {len(hits)} spans changed")


def cmd_left(files):
    M = load_map()
    for f in files:
        for n, line in enumerate(open(f), 1):
            for span in re.findall(r"\*\*([^*\n]+)\*\*", line) + (re.findall(r'"([^"\n]*)"', line) if f.endswith(".toml") else []):
                left = [t for t in TOK.findall(span.lower()) if t in M]
                if left:
                    print(f"{f}:{n}: {', '.join(left)}  | {span[:100]}")


def cmd_tokens(files):
    M = load_map()
    pat = re.compile(r"(?<![A-Za-z_])(" + "|".join(sorted(M, key=len, reverse=True)) + r")(?![A-Za-z_])")
    for f in files:
        s = open(f).read()
        s2, n = pat.subn(lambda m: M[m.group(1)], s)
        if n:
            open(f + ".tmp", "w").write(s2); os.replace(f + ".tmp", f)
        print(f"{f}: {n} tokens changed")


def _pat(M):
    return re.compile(r"(?<![A-Za-z_])(" + "|".join(sorted(M, key=len, reverse=True)) + r")(?![A-Za-z_])")


def cmd_literals(files):
    """Only inside "..." string literals (code files), every whole old form."""
    M = load_map(); pat = _pat(M)
    for f in files:
        s = open(f).read(); n = [0]
        def lit(m):
            new, k = pat.subn(lambda x: M[x.group(1)], m.group(0)); n[0] += k
            return new
        s2 = re.sub(r'"[^"\n]*"', lit, s)
        if s2 != s:
            open(f + ".tmp", "w").write(s2); os.replace(f + ".tmp", f)
        print(f"{f}: {n[0]} tokens changed")


def cmd_cols(ncols, files):
    """TSV files: only the first ncols columns, every whole old form."""
    M = load_map(); pat = _pat(M)
    for f in files:
        out, n = [], 0
        for line in open(f):
            parts = line.rstrip("\n").split("\t")
            for k in range(min(ncols, len(parts))):
                parts[k], c = pat.subn(lambda x: M[x.group(1)], parts[k]); n += c
            out.append("\t".join(parts) + "\n")
        open(f + ".tmp", "w").write("".join(out)); os.replace(f + ".tmp", f)
        print(f"{f}: {n} tokens changed")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "data":
        cmd_data()
    elif cmd == "text":
        cmd_text(sys.argv[2:])
    elif cmd == "literals":
        cmd_literals(sys.argv[2:])
    elif cmd == "cols":
        cmd_cols(int(sys.argv[2]), sys.argv[3:])
    elif cmd == "tokens":
        cmd_tokens(sys.argv[2:])
    elif cmd == "left":
        cmd_left(sys.argv[2:])
