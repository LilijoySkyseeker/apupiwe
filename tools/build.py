"""Shared word-form basics: the syllable inventory, drift keys, frequency and effort constants, and the data readers.

Imported by the other tools (place.py, accent.py, juncture.py, check.py, names.py, offensive.py). The original
2026-10-08 builder (build, numbers3, scale) and tools/words.py were deleted on 2026-11-19 (doghouse review,
research/reviews/doghouse-2026-11.md); both are in git history. New roots are placed with tools/place.py.

Drift keys (docs/drift.md): later syllables blur e/i and o/u, middle consonants voice (p t k > b d g), a final -n
melts away, and s/z merge; no two content words may share a key.
"""
import csv, os, re
import numpy as np
from confusion import CP, VP, CODA_MISS

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
VOWELS = "i e a o u".split()
FULL = "p t k f s b d g z m n l w j".split()  # /v/ deleted
TIER_FREQ = {5: 10, 4: 5, 3: 2.5, 2: 1.2, 1: 0.6}
EFFORT = 0.02
TIE = 0.02  # C3: forms within 2% of the cheapest count as "about the same cost" (added by Claude, 2026-10-15)


class Inventory:
    def __init__(self, consonants):
        self.cons = consonants
        self.onsets = [""] + consonants
        self.syl = [(o, v, c) for o in self.onsets for v in VOWELS for c in ("", "n")]
        self.name = [(o.replace("j", "y") + v + c) for o, v, c in self.syl]
        self.idx = {n: i for i, n in enumerate(self.name)}
        on = self.onsets
        C = np.array([[CP[a, b] for b in on] for a in on])
        C /= C.sum(1, keepdims=True)  # renormalize over this inventory
        V = np.array([[VP[a, b] for b in VOWELS] for a in VOWELS])
        n = len(self.syl)
        self.S = np.zeros((n, n))   # mishearing model v1 (confusion.py), kept for reference
        for i, (o1, v1, c1) in enumerate(self.syl):
            for j, (o2, v2, c2) in enumerate(self.syl):
                self.S[i, j] = (C[on.index(o1), on.index(o2)] * V[VOWELS.index(v1), VOWELS.index(v2)]
                                * ((1 - CODA_MISS) if c1 == c2 else CODA_MISS))
        self.later = [i for i, s in enumerate(self.syl) if s[0] != ""]  # non-initial syllables need an onset

    def length(self, form):
        return sum(1 + 0.4 * bool(self.syl[s][2]) for s in form)   # no vowel-start bonus (author, 2026-11-18)

    def content_key(self, form):
        out = []
        for k, s in enumerate(form):
            o, v, c = self.syl[s]
            o = {"z": "s"}.get(o, o)
            if k > 0:
                o = {"p": "b", "t": "d", "k": "g"}.get(o, o)
                v = {"e": "i", "o": "u"}.get(v, v)
                c = ""
            out.append(o + v + c)
        return ".".join(out)

    def grammar_key(self, s):
        o, v, c = self.syl[s]
        return {"z": "s"}.get(o, o) + {"e": "i", "o": "u"}.get(v, v)

    def show(self, form):
        return "".join(self.name[s] for s in form)


INV = Inventory([c for c in FULL if c != "z"])  # 13 consonants since 2026-10-08
SYL, IDX = INV.name, INV.idx


def read(name):
    """A data/ table (tab-separated, with a header) as a list of dicts."""
    with open(os.path.join(DATA, name)) as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def split(form):
    """Split a word into syllable indices; syllables are (C)V(n)."""
    parts = re.findall(r"[^aeiou]?[aeiou](?:n(?![aeiou]))?", form)
    assert "".join(parts) == form, form
    return [IDX[p] for p in parts]


def digit_syllables():
    """The one-syllable digits (mu ni sa de wo ma) as syllable indices."""
    return {IDX[r["form"]] for r in read("numbers.tsv") if r["kind"] == "digit" and r["form"] in IDX}
