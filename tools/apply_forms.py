"""Apply a map of word forms (old -> new) to the data and the texts. The one apply tool (consolidated 2026-11-19 from
tests/placement-08/apply/apply.py; the earlier copies are in git history).

MAP is a tab-separated file with the columns old, new (tools/place.py write makes one). Every command applies the
map simultaneously, one pass per file, so chains and swaps (nun -> sen while yen -> nun) can't cascade: run each
command once per file.

  python3 tools/apply_forms.py data MAP              # the form columns of data/lexicon.tsv, grammar.tsv, numbers.tsv,
                                                     # loans.tsv, roles.tsv, and every word of compounds.tsv's forms
  python3 tools/apply_forms.py text MAP FILE ...     # Apupiwe spans in markdown and spec/reference.toml (see below)
  python3 tools/apply_forms.py tokens MAP FILE ...   # files that are wholly Apupiwe, or code: every lowercase whole-word
                                                     # old form (tests/udhr-01/translation.md, grammar/intended.tsv,
                                                     # grammar/*.gf literals and comments)
  python3 tools/apply_forms.py literals MAP FILE ... # only inside "..." string literals (code files)
  python3 tools/apply_forms.py cols MAP N FILE ...   # TSV files: only the first N columns
  python3 tools/apply_forms.py left MAP FILE ...     # list old forms still present in Apupiwe spans (for review)
Every command but `left` runs tools/check_all.py at the end and exits with its result (expect failures until every
file is done).

Text rule (as tests/shortwords-03/APPLY.md): in markdown, only **bold** spans are Apupiwe, and only when every token
in the span is a known Apupiwe word (old or new forms, grammar words, digits; a name right after fo is allowed). In
spec/reference.toml every string is checked the same way, plus the fields that are wholly Apupiwe (apu = "...").
A name after fo (one whitespace-separated word, hyphens included, e.g. fo wi-fi) is never remapped (2026-11-19).
"""
import csv, os, re, subprocess, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
DATA = os.path.join(ROOT, "data")


def read(path):
    with open(path) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_text(path, old, new):
    if new != old:
        with open(path + ".tmp", "w") as fh:
            fh.write(new)
        os.replace(path + ".tmp", path)


def run_check_all():
    """tools/check_all.py; returns its exit code."""
    print("\n== tools/check_all.py", flush=True)
    return subprocess.run([sys.executable, os.path.join(TOOLS, "check_all.py")], cwd=ROOT).returncode


MAP_PATH = [None]


def load_map(path=None):
    rows = read(path or MAP_PATH[0])
    M = {r["old"]: r["new"] for r in rows}
    assert len(M) == len(rows), "map has an old form twice"
    return M


# ------------------------------------------------------------------------------------------ data
DATA_FORMS = {"lexicon.tsv": "form", "grammar.tsv": "form", "numbers.tsv": "form", "loans.tsv": "form",
              "roles.tsv": "form", "compounds.tsv": "form"}


def map_column(path, col, fn, append=()):
    """Rewrite one column of a TSV in place, line by line (other columns, quoting and order untouched); `append`:
    extra rows (dicts). Writes only if something changed; returns the number of rows changed."""
    s = open(path).read()
    lines = s.splitlines()
    cols = lines[0].split("\t")
    k, n = cols.index(col), 0
    for i in range(1, len(lines)):
        parts = lines[i].split("\t")
        if len(parts) > k:
            new = fn(parts[k])
            n += new != parts[k]
            parts[k] = new
            lines[i] = "\t".join(parts)
    lines += ["\t".join(str(r.get(c, "")) for c in cols) for r in append]
    write_text(path, s, "\n".join(lines) + "\n")
    return n


def apply_data(M, files=tuple(DATA_FORMS)):
    """The map on the form columns of data files (compounds: every word of the phrase). Writes only changed files."""
    for name in files:
        n = map_column(os.path.join(DATA, name), DATA_FORMS[name], lambda f: " ".join(M.get(t, t) for t in f.split(" ")))
        print(f"data/{name}: {n} rows changed")


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
    # a name after fo (one whitespace-separated word, hyphens included, e.g. fo wi-fi) is never remapped (2026-11-19)
    protected = {m.group(1) for m in re.finditer(r"\bfo\s+([A-Za-z][\w-]*)", span)}
    if protected:
        parts = re.split(r"(\bfo\s+[A-Za-z][\w-]*)", span)
        out, changed = [], False
        for k, part in enumerate(parts):
            if k % 2 == 1:
                out.append(part); continue
            new, ch = remap_span(part, M, K) if TOK.search(part) else (part, False)
            out.append(new); changed = changed or ch
        return "".join(out), changed
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
            if n == t.lower():
                return t                       # unchanged: keep its capitals (stress marks such as WIfu)
            return n.upper() if t.isupper() and len(t) > 1 else n[0].upper() + n[1:]
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
    if not dry:
        write_text(path, s, s2)
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
        s2, n = pat.subn(lambda m: M[m.group(1)], s) if M else (s, 0)
        write_text(f, s, s2)
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
        s2 = re.sub(r'"[^"\n]*"', lit, s) if M else s
        write_text(f, s, s2)
        print(f"{f}: {n[0]} tokens changed")


def cmd_cols(ncols, files):
    """TSV files: only the first ncols columns, every whole old form."""
    M = load_map(); pat = _pat(M)
    for f in files:
        out, n, s = [], 0, open(f).read()
        for line in s.splitlines(keepends=True):
            nl = line[len(line.rstrip("\n")):]
            parts = line.rstrip("\n").split("\t")
            for k in range(min(ncols, len(parts))):
                if M:
                    parts[k], c = pat.subn(lambda x: M[x.group(1)], parts[k]); n += c
            out.append("\t".join(parts) + nl)
        write_text(f, s, "".join(out))
        print(f"{f}: {n} tokens changed")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, MAP_PATH[0] = sys.argv[1], sys.argv[2]
    files = sys.argv[3:]
    if cmd == "left":
        cmd_left(files); sys.exit(0)
    if cmd == "data":
        apply_data(load_map())
    elif cmd == "text":
        cmd_text(files)
    elif cmd == "literals":
        cmd_literals(files)
    elif cmd == "cols":
        cmd_cols(int(files[0]), files[1:])
    elif cmd == "tokens":
        cmd_tokens(files)
    else:
        sys.exit(__doc__)
    sys.exit(run_check_all())
