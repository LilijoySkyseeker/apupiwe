"""Stress-only and stress-proof regroupings (author's question, 2026-11-19).

A stretch of syllables that can be cut into words in two ways. Stress marks where content words begin
(reference 2.5-2.6: one-syllable grammar words unstressed; digits 0-5 one stressed syllable; every other
word stressed on its first). Two cuts of the same syllables are either
  SAME stress   -> stress can't tell them apart (rule J, the digit rule)
  DIFF stress   -> stress is the only cue (Decision 23: ti wu obu ~ tiwu obu)

Part 1, every pair of words in the vocabulary: w1 w2 re-cut into 1-3 other words.
Part 2, the corpus (reference examples + UDHR translation): every minimal re-cut span inside a pause-free
phrase, and whether the sentence with the re-cut still parses (tools/gf_check.py).

  python tests/stress-01/check.py      # writes pairs.tsv, corpus.tsv, summary.txt next to this file
"""
import collections, csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import words as W
import gf_check as G

def rd(n): return W.read(n)

vocab = {}  # form -> (kind, gloss)
for r in rd("lexicon.tsv"): vocab[r["form"]] = ("root", r["gloss"])
for r in rd("grammar.tsv"): vocab[r["form"]] = ("gram", r["gloss"])
for r in rd("numbers.tsv"):
    vocab.setdefault(r["form"], ("digit" if r["kind"] == "digit" else "num", f"{r['kind']} {r['value']}"))
OPS2 = "genso wanme inwun wemen konsin nedin tason mesun manni buntu buni donon lanno anko nuwen kiyu mena".split()
for f in OPS2:
    vocab.setdefault(f, ("op2", "operator"))

def syl(form):
    s = tuple(W.SYL[i] for i in W.split(form))
    assert "".join(s) == form, form
    return s

SY = {f: syl(f) for f in vocab}
BYSYL = collections.defaultdict(list)
for f, s in SY.items():
    BYSYL[s].append(f)
MAXL = max(len(s) for s in SY.values())

def stress(form):
    k = vocab[form][0]
    n = len(SY[form])
    if k == "gram" and n == 1:
        return (0,)
    return (1,) + (0,) * (n - 1)

def cuts(sylls, maxw=3):
    """All ways to cut a syllable tuple into vocabulary words (at most maxw words)."""
    out = []
    def rec(i, acc):
        if i == len(sylls):
            out.append(tuple(acc)); return
        if len(acc) == maxw: return
        for L in range(1, min(MAXL, len(sylls) - i) + 1):
            for f in BYSYL.get(sylls[i:i + L], ()):
                rec(i + L, acc + [f])
    rec(0, [])
    return out

def pattern(ws): return tuple(x for w in ws for x in stress(w))
def kinds(ws): return " ".join(vocab[w][0] for w in ws)

# ---- part 1: every pair --------------------------------------------------------------------
forms = sorted(vocab)
pairs = []
for a in forms:
    for b in forms:
        s = SY[a] + SY[b]
        for alt in cuts(s):
            if alt == (a, b): continue
            same = pattern(alt) == pattern((a, b))
            pairs.append((a, b, alt, same))

with open(os.path.join(HERE, "pairs.tsv"), "w") as fh:
    fh.write("seq\tglosses\tkinds\theard_as\theard_glosses\theard_kinds\tstress\n")
    for a, b, alt, same in pairs:  # only re-cuts into one or two words; the 3-word ones run to ~80 MB
        if len(alt) > 2: continue
        fh.write(f"{a} {b}\t{vocab[a][1]} + {vocab[b][1]}\t{kinds((a,b))}\t{' '.join(alt)}\t"
                 f"{' + '.join(vocab[w][1] for w in alt)}\t{kinds(alt)}\t{'SAME' if same else 'diff'}\n")

# ---- part 2: the corpus --------------------------------------------------------------------
spec = G.SPEC.load()
sents = []
for rid, apu, eng in G.SPEC.examples(spec):
    if rid in G.OUTSIDE or apu in G.OUTSIDE_SENT: continue
    for s in G.sentences(apu): sents.append((rid, s))
udhr = open(os.path.join(ROOT, "tests", "udhr-01", "translation.md")).read()
for line in udhr.splitlines():
    line = line.strip().replace('"', "")
    if not line or line.startswith("#") or not re.fullmatch(r"[a-z ,.\-'…]+", line.lower()): continue
    for s in G.sentences(line): sents.append(("udhr", s))

hits = []
for src, s in sents:
    toks = s.split()
    # phrases: split at pauses and around names (fo + name token)
    phrases, cur = [], []
    for i, t in enumerate(toks):
        if t == "," or "_" in t or (i and toks[i - 1] == "fo") or t not in vocab:
            if cur: phrases.append(cur)
            cur = []
        else:
            cur.append((i, t))
    if cur: phrases.append(cur)
    for ph in phrases:
        ws = [t for _, t in ph]
        bounds = [0]
        for w in ws: bounds.append(bounds[-1] + len(SY[w]))
        stream = tuple(x for w in ws for x in SY[w])
        for a in range(len(ws)):
            for b in range(a + 1, min(len(ws), a + 4) + 1):
                span = stream[bounds[a]:bounds[b]]
                inner = set(bounds[a + 1:b])
                for alt in cuts(span, maxw=4):
                    if alt == tuple(ws[a:b]): continue
                    ab, p = set(), bounds[a]
                    for w in alt[:-1]:
                        p += len(SY[w]); ab.add(p)
                    if ab & inner: continue  # not minimal: shares an inner boundary
                    if b - a > 1 and not ab: pass
                    same = pattern(alt) == pattern(ws[a:b])
                    new = toks[:ph[a][0]] + list(alt) + toks[ph[b - 1][0] + 1:]
                    hits.append((src, s, " ".join(ws[a:b]), " ".join(alt), same, " ".join(new)))

alts = sorted({h[5] for h in hits})
info, fails = G.parse_all(alts)
parses = {s: len(info.get(i, [])) for i, s in enumerate(alts)}

with open(os.path.join(HERE, "corpus.tsv"), "w") as fh:
    fh.write("source\tsentence\tsaid\theard_as\tstress\talt_parses\talt_sentence\n")
    for src, s, said, alt, same, new in hits:
        fh.write(f"{src}\t{s}\t{said}\t{alt}\t{'SAME' if same else 'diff'}\t{parses[new]}\t{new}\n")

# ---- summary --------------------------------------------------------------------------------
L = []
L.append(f"vocabulary {len(vocab)} words; pairs checked {len(forms)**2}")
c = collections.Counter((same, kinds((a, b)), kinds(alt)) for a, b, alt, same in pairs)
L.append(f"pairs with another cut: {len(pairs)}  (SAME stress {sum(1 for p in pairs if p[3])}, diff {sum(1 for p in pairs if not p[3])})")
for (same, k1, k2), n in c.most_common():
    L.append(f"  {'SAME' if same else 'diff'}  {k1:12} -> {k2:18} {n}")
L.append(f"\ncorpus: {len(sents)} sentences, {sum(len(s.split()) for _, s in sents)} tokens; re-cut spans {len(hits)}")
L.append(f"  distinct (said, heard) {len({(h[2], h[3]) for h in hits})}")
for same in (True, False):
    hs = [h for h in hits if h[4] == same]
    ok = [h for h in hs if parses[h[5]]]
    L.append(f"  {'SAME' if same else 'diff'} stress: {len(hs)} spans, alternative sentence parses in {len(ok)}")
cc = collections.Counter((h[2], h[3], h[4]) for h in hits if parses[h[5]])
L.append("\nre-cuts that still parse, by frequency:")
for (said, alt, same), n in cc.most_common():
    L.append(f"  {n:3}  {'SAME' if same else 'diff'}  {said}  ~  {alt}   ({' + '.join(vocab[w][1] for w in said.split())}  ~  {' + '.join(vocab[w][1] for w in alt.split())})")
open(os.path.join(HERE, "summary.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L[:40]))
