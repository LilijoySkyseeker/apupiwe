"""Accent tolerance check (roadmap "Placement checks", Globasa rows 12-13): for each pair of sounds a declared variant
could bring together, list the word pairs that differ only by that pair of sounds, in the context where the variant
applies. Grammar words and digits count as "between vowels" too: in running speech they follow a vowel-final word.

  python3 pairs.py            # summary + every grammar/digit pair; content pairs by count, first examples
"""
import csv, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import words as W

SYL = re.compile(r"([^aeiou]?)([aeiou])(n?)(?=[^aeiou]?[aeiou]|$)")


def syls(form):
    out, i = [], 0
    for m in SYL.finditer(form):
        out.append((m.group(1), m.group(2), m.group(3)))
    assert "".join(o + v + c for o, v, c in out) == form, form
    return out


# (sound A, sound B, how a variant brings them together, context test(position, prev syllable, this syllable))
inter = lambda k, prev, s, short: short or (k > 0 and prev[2] == "")          # between vowels
front = lambda k, prev, s, short: s[1] in "ie"
back = lambda k, prev, s, short: s[1] in "ou" and (short or (k > 0 and prev[2] == ""))
anyp = lambda k, prev, s, short: True
CASES = [
    ("b", "w", "b softened between vowels [β̞] vs w as [ʋ]", inter),
    ("d", "l", "d softened [ð] vs l as a tap [ɾ]", inter),
    ("g", "w", "g softened [ɣ, ɰ] vs w before o/u", back),
    ("g", "y", "g before i/e as [dʒ] vs y [j] (dʒ/j merge in many accents)", front),
    ("k", "s", "k before i/e as [tʃ] vs s as [ʃ]", front),
    ("f", "p", "f as [ɸ] vs unaspirated p", anyp),
]


def words():
    out = []
    for r in W.read("lexicon.tsv"):
        out.append((r["form"], r["gloss"], "content"))
    for r in W.read("grammar.tsv"):
        out.append((r["form"], r["gloss"], "grammar"))
    for r in W.read("numbers.tsv"):
        if r["kind"] == "digit" and len(r["form"]) <= 3:
            out.append((r["form"], r["value"], "digit"))
    return out


def main():
    ws = words()
    by = {}
    for f, g, k in ws:
        by.setdefault(f, (g, k))
    for a, b, how, ctx in CASES:
        hits = []
        for f, (g, kind) in by.items():
            S = syls(f)
            short = kind != "content"
            for k, s in enumerate(S):
                if s[0] != a:
                    continue
                prev = S[k - 1] if k else ("", "", "")
                if not ctx(k, prev, s, short):
                    continue
                other = "".join((b if j == k else x[0]) + x[1] + x[2] for j, x in enumerate(S))
                if other in by:
                    hits.append((f, g, kind, other) + by[other])
        gram = [h for h in hits if h[2] != "content" or h[5] != "content"]
        cont = [h for h in hits if h[2] == "content" and h[5] == "content"]
        print(f"\n{a}/{b}: {how}: {len(hits)} pairs ({len(gram)} involving grammar words or digits, {len(cont)} content)")
        for f, g, k1, o, g2, k2 in gram:
            print(f"   {f} {g} ({k1})  ~  {o} {g2} ({k2})")
        if cont:
            print("   content: " + "; ".join(f"{f} {g} ~ {o} {g2}" for f, g, _, o, g2, _ in cont[:12]) + (" …" if len(cont) > 12 else ""))


if __name__ == "__main__":
    main()
