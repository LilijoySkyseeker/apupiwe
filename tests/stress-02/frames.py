"""Stress 02: which grammar-word pairs that sound like a root matter (Decision 23; follows stress-01).

For each of the 184 pairs g1 g2 ~ root R from tests/stress-01/pairs.tsv:
  1. can g1 g2 stand together?  Frames: corpus sentences with two adjacent one-syllable grammar words of
     g1's and g2's classes (data/grammar.tsv); the pair is substituted in and the sentence parsed (GF).
     Exact-word matches first, at most CAP frames per pair.
  2. does R fit there?  In each frame where g1 g2 parses, g1 g2 is replaced by R and parsed again.
  3. weight: grammar-word frequency (data/grammar.tsv freq) of g1 and g2, root tier, and stakes as in
     tests/deletion-01 (3 for speech acts, negation and warning; 1 for politeness and stance; 2 otherwise).

  python tests/stress-02/frames.py     # writes results.tsv and examples.tsv next to this file
"""
import collections, csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build as W, gf_check as G
G.build()

CAP = 12
gram = {r["form"]: r for r in W.read("grammar.tsv")}
tier = {r["form"]: r["tier"] for r in W.read("lexicon.tsv")}
gloss = {r["form"]: r["gloss"] for r in W.read("lexicon.tsv")}
HI = {"Q", "REQUEST", "INSTRUCT", "ADVISE", "INTEND", "WH", "NOT", "WARN", "EXCLAIM"}
LO = {"POLITE", "YOUKNOW", "ENDEAR", "FOCUS"}
def stakes(g):
    gl = gram[g]["gloss"]
    return 3 if gl in HI else 1 if gl in LO else 2

pairs = []
for r in csv.DictReader(open(os.path.join(ROOT, "tests", "stress-01", "pairs.tsv")), delimiter="\t"):
    if r["kinds"] == "gram gram" and r["heard_kinds"] == "root":
        g1, g2 = r["seq"].split(); pairs.append((g1, g2, r["heard_as"]))

sents = []
for rid, apu, eng in G.SPEC.examples(G.SPEC.load()):
    if rid in G.OUTSIDE or apu in G.OUTSIDE_SENT: continue
    sents += G.sentences(apu)
for line in open(os.path.join(ROOT, "tests", "udhr-01", "translation.md")):
    line = line.strip().replace('"', "")
    if line and not line.startswith("#") and re.fullmatch(r"[a-z ,.\-'…]+", line.lower()):
        sents += G.sentences(line)
sents = [s for s in dict.fromkeys(sents) if len(s.split()) <= 14]  # short ones parse fast and read clearly

slots = collections.defaultdict(list)  # (class1, class2) -> [(sentence tokens, i)]
after = collections.defaultdict(list)  # class -> [(tokens, i)]: a word of that class at i
for s in sents:
    t = s.split()
    for i in range(len(t)):
        if t[i] in gram:
            after[gram[t[i]]["class"]].append((t, i))
        if i + 1 < len(t) and t[i] in gram and t[i + 1] in gram:
            slots[(gram[t[i]]["class"], gram[t[i + 1]]["class"])].append((t, i))

jobs = {}
for g1, g2, R in pairs:
    cand = slots.get((gram[g1]["class"], gram[g2]["class"]), [])
    cand = sorted(cand, key=lambda c: -((c[0][c[1]] == g1) * 2 + (c[0][c[1] + 1] == g2)))
    # three frame kinds, in this order: both words substituted (same classes, adjacent); g2 inserted after
    # a word of g1's class (which becomes g1); g1 inserted before a word of g2's class (which becomes g2)
    ins1 = [(t[:i] + [g1, g2] + t[i + 1:], t[:i] + [R] + t[i + 1:]) for t, i in after.get(gram[g1]["class"], [])]
    ins2 = [(t[:i] + [g1, g2] + t[i + 1:], t[:i] + [R] + t[i + 1:]) for t, i in after.get(gram[g2]["class"], [])]
    sub = [(t[:i] + [g1, g2] + t[i + 2:], t[:i] + [R] + t[i + 2:]) for t, i in cand]
    seen, fr = set(), []
    for k, group in enumerate((sub, ins1, ins2)):
        n = 0
        for a_, b_ in group:
            s1 = " ".join(a_)
            if s1 in seen: continue
            seen.add(s1); fr.append((s1, " ".join(b_))); n += 1
            if n == CAP // 3 * (2 if k == 0 else 1) + (CAP % 3): break
    jobs[(g1, g2, R)] = fr

def parse(ss):
    ss = sorted(set(ss)); info, _ = G.parse_all(ss)
    return {s: len(info.get(i, [])) for i, s in enumerate(ss)}

P1 = parse([a for fr in jobs.values() for a, _ in fr])
P2 = parse([b for fr in jobs.values() for a, b in fr if P1[a]])

with open(os.path.join(HERE, "results.tsv"), "w") as fh, open(os.path.join(HERE, "examples.tsv"), "w") as ex:
    fh.write("pair\tglosses\troot\troot_gloss\troot_tier\tframes\tpair_parses\troot_fits\tfreq_g1\tfreq_g2\tstakes\tweight\n")
    ex.write("pair\troot\tsaid\theard\n")
    for (g1, g2, R), fr in jobs.items():
        ok1 = [a for a, _ in fr if P1[a]]
        ok2 = [(a, b) for a, b in fr if P1[a] and P2.get(b)]
        f1, f2 = float(gram[g1]["freq"]), float(gram[g2]["freq"])
        st = max(stakes(g1), stakes(g2))
        w = (min(f1, f2) * st * len(ok2) / len(fr)) if fr else 0
        fh.write(f"{g1} {g2}\t{gram[g1]['gloss']} + {gram[g2]['gloss']}\t{R}\t{gloss[R]}\t{tier[R]}\t{len(fr)}\t"
                 f"{len(ok1)}\t{len(ok2)}\t{f1}\t{f2}\t{st}\t{w:.2f}\n")
        for a, b in ok2[:3]:
            ex.write(f"{g1} {g2}\t{R}\t{a}\t{b}\n")
print("done")
