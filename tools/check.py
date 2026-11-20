"""Check language text for unknown words (roadmap C3, built 2026-10-08).

Hand translation has now used stale word forms three times: forms renamed in a rebuild
(Ate for "far", ban for "rather"). This flags every word that isn't a current grammar word,
root, number word or digit, or a name after the article "fo".

  python check.py FILE...        # checks language lines in code blocks and **bold** spans; exit 1 if any unknown
  python check.py --text "..."   # checks one string
"""
import re, sys
import build as W

KNOWN = ({g["form"] for g in W.read("grammar.tsv")} | {w["form"] for w in W.read("lexicon.tsv")}
         | {r["form"] for r in W.read("numbers.tsv")})


# Sentences outside the lexicon on purpose (as tools/gf_check.py OUTSIDE_SENT, and 11.5's address read aloud)
OUTSIDE = {"mara ben obu": "casual speech: a name without fo (11.1)",
           "wan nawi susi sa": "a speaker's borrowing, not in the lexicon (11.3)",
           "wan ben gugalu bun": "a speaker's borrowing used as a verb (11.3)",
           "mara no gmail mimi komu": "an email address read aloud: its name parts are spelled as written (11.5)"}
TOKEN = r"[A-Za-z]+(?:-[A-Za-z]+)*"   # a name may hold a hyphen (fo wi-fi)


def unknown(text):
    """Unknown words in a span. A name after fo runs to the next known word, or to kiyu when kiyu closes it (11.1)."""
    if text.strip().lower() in OUTSIDE:
        return []
    bad = []
    for part in re.split(r"[,.;:!?]", text):    # a pause ends a name
        toks = re.findall(TOKEN, part)
        lows = [t.lower() for t in toks]
        i = 0
        while i < len(toks):
            t = lows[i]
            if t == "fo":
                j = lows.index("kiyu", i + 1) if "kiyu" in lows[i + 1:] else None
                if j is None:
                    j = i + 1
                    while j < len(toks) and lows[j] not in KNOWN:
                        j += 1
                i = max(j, i + 1)
                continue
            if t not in KNOWN and not (len(toks[i]) == 1 and toks[i].isupper()):   # X, Y: placeholders in a template
                bad.append(toks[i])
            i += 1
    return bad


def check_file(path):
    problems, in_code = [], False
    for n, line in enumerate(open(path), 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        spans = [line] if in_code else re.findall(r"\*\*([^*]+)\*\*", line)
        for sp in spans:
            toks = re.findall(TOKEN, sp)
            known = sum(t.lower() in KNOWN for t in toks)
            if toks and known >= max(1, len(toks) // 2):   # looks like language, not an English gloss
                bad = unknown(sp)
                if bad:
                    problems.append(f"{path}:{n}: {' '.join(bad)}")
    return problems


if __name__ == "__main__":
    if sys.argv[1] == "--text":
        print(unknown(sys.argv[2]) or "ok")
    else:
        out = [p for f in sys.argv[1:] for p in check_file(f)]
        print("\n".join(out) if out else "no unknown words")
        sys.exit(1 if out else 0)
