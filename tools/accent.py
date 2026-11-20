"""Check reference rule 2.12 (design log 2026-11-19): no two content words, and no two short words that can stand
in the same place, differ only by sounds a harmless accent variant (2.9) brings together. Run after any word change.

  python tools/accent.py        # exit 1 and list the pairs if the rule is broken

Content words: k/s before i e in any syllable; b/w, d/l, g/w before o u, g/y before i e in a later syllable after an
open one (between vowels, unstressed). Short words: the same sound pairs, for words that share a position in
tests/shortwords-04/rebuild.py (its position table and the GF substitution counts).

Also (author, 2026-11-19; research/notes/names-and-loans.md §5): a loan's added final vowel is the part speakers
vary, so no other word may sit on a loan with that vowel changed (same drift key). A final vowel is added when the
loan's source (data/loans.tsv, the panel's median) ends in a consonant; the vowel may also be dropped, so the
form without it may not be another word either.
"""
import os, re, subprocess, sys
import words as W

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def neighbours(form):
    S = [(re.match(r"[^aeiou]?", s).group(0), re.search(r"[aeiou]", s).group(0), "n" if s.endswith("n") and len(s) > 1 and s[-2] in "aeiou" else "")
         for s in (W.SYL[i] for i in W.split(form))]
    out = []
    for k, (o, v, c) in enumerate(S):
        alts = []
        if v in "ie" and o in ("k", "s"):
            alts.append("s" if o == "k" else "k")
        if k > 0 and S[k - 1][2] == "":
            alts += {"b": ["w"], "w": ["b"], "d": ["l"], "l": ["d"]}.get(o, [])
            if v in "ou" and o in ("g", "w"):
                alts.append("w" if o == "g" else "g")
            if v in "ie" and o in ("g", "y"):
                alts.append("y" if o == "g" else "g")
        for x in alts:
            out.append("".join((x if j == k else a) + b + cc for j, (a, b, cc) in enumerate(S)))
    return out


VOWELS_IPA = "aeiouɪʊəɛɔæɑʌɐɒyøœɯɨ"


def loan_vowel_clashes(lex):
    """Loans whose added final vowel, said as another vowel, gives another word's drift key."""
    forms = {r["form"]: r["gloss"] for r in lex}
    keys = {W.INV.content_key(W.split(f)): f for f in forms}
    out = []
    for r in W.read("loans.tsv"):
        f, src = r["form"], re.sub(r"[\[\]/ˈˌː.]", "", r["source_ipa"])
        if not src or src[-1] in VOWELS_IPA or f[-1] not in "aeiou":
            continue
        for v in "aeiou":
            alt = f[:-1] + v
            if v == f[-1]:
                continue
            try:
                k = W.INV.content_key(W.split(alt))
            except Exception:
                continue
            other = alt if alt in forms and alt != f else keys.get(k)
            if other and other != f:
                out.append((f, forms[f], alt, other, forms[other]))
        # the added vowel dropped (2026-11-19, second outside review): geni said [dʒen] is the grammar word gen
        cut = f[:-1]
        try:
            ok = bool(W.split(cut)) and "".join(W.SYL[i] for i in W.split(cut)) == cut
        except Exception:
            ok = False
        if ok:
            gram = {g["form"]: g["gloss"] for g in W.read("grammar.tsv")}
            kc = W.INV.content_key(W.split(cut))
            hit = (cut, gram[cut]) if cut in gram else ((keys[kc], forms[keys[kc]]) if kc in keys and keys[kc] != f else None)
            if hit:
                out.append((f, forms[f], cut, hit[0], hit[1]))
    return out


def main():
    lex = W.read("lexicon.tsv")
    forms = {r["form"]: r["gloss"] for r in lex}
    bad = sorted({tuple(sorted((f, n))) for f in forms for n in neighbours(f) if n in forms})
    for a, b in bad:
        print(f"content: {a} {forms[a]} ~ {b} {forms[b]}")
    lv = sorted(set(loan_vowel_clashes(lex)))
    for f, g, alt, o, og in lv:
        print(f"loan vowel: {f} {g} said as {alt} ~ {o} {og}")
    env = dict(os.environ, SW_SOFT="1")
    code = ("import sys; sys.argv=['x']; sys.path.insert(0, 'tests/shortwords-04'); import rebuild as R\n"
            "for v in R.violations(R.OLD_SYL): print('short words:', *v)")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True)
    short = [l for l in r.stdout.splitlines() if l.startswith("short words:")]
    print("\n".join(short))
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(2)
    if bad or short or lv:
        sys.exit(1)
    print("no contrast rests on an accent variant")


if __name__ == "__main__":
    main()
