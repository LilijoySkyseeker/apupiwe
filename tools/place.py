"""Place roots: give every concept in data/concept-list.tsv a form, keeping today's roots (data/lexicon.tsv) where
the rules allow. The one placement tool (consolidated 2026-11-19 from tests/placement-11/place.py and report.py; the
eleven earlier copies, placement-01 to -11, are in git history, and each test's README records what it changed).

  python3 tools/place.py start [--move FORMS]     # A: today's legal roots kept, the rest placed one at a time -> A.json
  python3 tools/place.py descend SEED --keep X    # C: coordinate descent from A with keep term X -> C-kX-SEED.json
  python3 tools/place.py report [STATE ...]       # report.txt and forms.tsv (default: A.json and every C-*.json)
  python3 tools/place.py write STATE              # put STATE's forms into data/ (lexicon, numbers, compounds, roles),
                                                  # write map.tsv (old -> new), then run tools/check_all.py
  python3 tools/place.py medians                  # random-lexicon medians (made on demand by start, descend, report)
  python3 tools/place.py info
  --state DIR: where state, reports and maps go (default: a new temp dir, printed). Never tools/ or data/.
  Every long step writes its state atomically (tmp file + rename) and resumes from it: rerun with the same --state.

A new concept needs a row in data/concept-list.tsv first (route "root"); `start` then keeps every root that is still
legal and places the new one. `--move kiyo,ode` re-places the named forms (roots or operators). After `write`, apply
map.tsv to the texts with tools/apply_forms.py.

Hard rules (a form that breaks one is never taken; `start` re-places a today's root that breaks one):
  - unique drift key (tools/build.py content_key); a later syllable has an onset; no form on the offensive hard list
  - no root starts with a digit's syllable (mu ni sa de wo ma) or a haplology syllable: a grammar word standing right
    before a content word >= 10 times in the corpus (data/bigrams.tsv, by gloss; forms from data/grammar.tsv)
  - juncture (tools/juncture.py check 3): X and nX not both content words where a grammar word Cn has an open twin C
  - accent (reference 2.12): no two content words differ only by a declared accent merger (acc_neigh)
  - loan vowel: no root takes the drift key of a loan with its added final vowel changed (tools/accent.py also
    checks the vowel dropped)
  - rule J: no word sounds like a shorter content word followed by a grammar word (tiwuye ~ tiwu ye)
  - rule G: no root sounds like two one-syllable grammar words in a row (ti wu ~ tiwu; Decision 23), except roots
    checked and cleared in data/regroup-reviewed.tsv (tests/stress-02/); today's roots by exact sounds, new forms
    by drift key (as rule J)
  - three syllables only for tier 1 (author 2026-11-18); apu "language" locked
The senary reservation (forms kept free for data/senary.tsv) was removed 2026-11-19 (author, goal N6).

Objective (rule 1, design log 2026-10-13/15): per model variant v (confusion2.variants(), 48),
  conf_v = sum_{i != j, same length} W_ij f_i P_v(i heard as j)
  P_v(i -> j) = S_v,initial[i1, j1] * prod_k S_v,internal[ik, jk]
the robust score R = mean over the worst quarter of variants (12 of 48) of conf_v / med_v, med_v = the
variant's median conf over random lexicons (every root at a random valid two-syllable form; loans and
operators at their forms). Placement minimises
  J = med_best * R + EFFORT * sum_i f_i (length_i - 2) [+ KEEP for each root that leaves today's form]
W: same field x3, antonym x30, number words x30 against each other. f: TIER_FREQ. No vowel-start bonus (author,
2026-11-18; was --no-vbonus).
"""
import contextlib, csv, glob, io, json, math, os, random, re, runpy, subprocess, sys, tempfile, time
import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(TOOLS, "..")
sys.path.insert(0, TOOLS)
import build as W
import offensive
import confusion2 as M2
from build import TIER_FREQ, EFFORT

INV, SYL, IDX = W.INV, W.SYL, W.IDX
NS = len(SYL)
assert [o.replace("j", "y") + v + c for o, v, c in M2.SYLLABLES] == SYL  # same syllable indexing


def _arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


_STATE = []


def state_dir():
    if not _STATE:
        d = _arg("--state") or tempfile.mkdtemp(prefix="place-")
        os.makedirs(d, exist_ok=True)
        for bad in (os.path.abspath(TOOLS), os.path.abspath(W.DATA)):
            assert not os.path.abspath(d).startswith(bad), f"--state must not be inside {bad}"
        _STATE.append(d)
        print(f"state dir: {d}", flush=True)
    return _STATE[0]


MOVE = set(_arg("--move").split(",")) if "--move" in sys.argv else set()
FIXED_OPS = set("genso wanme inwun wemen konsin buntu tason nedin mesun manni buni donon lanno anko nuwen kiyu mena".split())
HAPLO_MIN = 10  # a grammar word bans its syllable as a root's first syllable if it stands right before a content word >= 10 times in the corpus (data/bigrams.tsv; ~1% of the 930 such bigrams)
MAX3_TIER = 1   # author 2026-11-18: three syllables only for tier 1
LOCKED = {"language"}   # author 2026-11-18: apu, the language's name
KEEP = float(_arg("--keep", 0.0))
TIE = W.TIE     # C3 tie-break window (2%)
K3 = 400        # three-syllable candidates evaluated per word, drawn from all valid forms; the space is sparse, so
                # the effort term decides most of the choice


def save(name, obj):
    path = os.path.join(state_dir(), name)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh)
    os.replace(tmp, path)


def load_state(name):
    path = name if os.path.sep in name and os.path.exists(name) else os.path.join(state_dir(), name)
    return json.load(open(path)) if os.path.exists(path) else None


def tup(form):
    return tuple(W.split(form))


def show(t):
    return "".join(SYL[s] for s in t)


# ------------------------------------------------------------------------------------------ items
def parse_antonyms(cell, glosses):
    """concept-list antonym cells join glosses with '; ', and some glosses contain '; ' themselves."""
    parts, out, i = cell.split("; "), [], 0
    clean = lambda s: re.sub(r"\s*\((added|decided)\)$", "", s).strip()
    while i < len(parts):
        for j in range(len(parts), i, -1):
            g = clean("; ".join(parts[i:j]))
            if g in glosses:
                out.append(g); i = j; break
        else:
            i += 1
    return out


CURRENT = {r["gloss"]: r["form"] for r in W.read("lexicon.tsv")}   # today's forms are the start


def _loan_vowel_keys():
    """Drift keys a root may not take: each loan with an added final vowel, said with another vowel."""
    import accent as _acc
    out = set()
    for r in W.read("loans.tsv"):
        f, src = r["form"], re.sub(r"[\[\]/ˈˌː.]", "", r["source_ipa"])
        if not src or src[-1] in _acc.VOWELS_IPA or f[-1] not in "aeiou":
            continue
        for v in "aeiou":
            if v != f[-1]:
                try:
                    out.add(INV.content_key(W.split(f[:-1] + v)))
                except Exception:
                    pass
    return out


LOANV = _loan_vowel_keys()
GSYL = {IDX[g["form"]] for g in W.read("grammar.tsv")}     # J: one-syllable grammar words


def j_bad3(t, occ):
    """J: a three-syllable form whose last syllable is a grammar word and whose first two are a placed word's key."""
    if len(t) != 3 or t[2] not in GSYL:
        return False
    k = INV.content_key(t[:2])
    return any(len(f) == 2 and INV.content_key(f) == k for f in occ)


def j_keys2(occ):
    """J: drift keys a two-syllable form may not take: the first two syllables of placed three-syllable words that
    end in a grammar word."""
    return {INV.content_key(f[:2]) for f in occ if len(f) == 3 and f[2] in GSYL}


def acc_neigh(t):
    """Forms that a declared accent variant brings together with form t (tuple of syllable indices)."""
    out = []
    for k, s in enumerate(t):
        o, v, c = M2.SYLLABLES[s]
        alts = []
        if v in "ie" and o in ("k", "s"):
            alts.append("s" if o == "k" else "k")
        if k > 0 and M2.SYLLABLES[t[k - 1]][2] == "":
            pairs = {"b": "w", "w": "b", "d": "l", "l": "d"}
            if o in pairs:
                alts.append(pairs[o])
            if v in "ou" and o in ("g", "w"):
                alts.append("w" if o == "g" else "g")
            if v in "ie" and o in ("g", "j"):
                alts.append("j" if o == "g" else "g")
        for x in alts:
            if (x, v, c) in M2.SYL_INDEX:
                out.append(t[:k] + (M2.SYL_INDEX[x, v, c],) + t[k + 1:])
    return out


def load_items():
    rows = list(csv.DictReader(open(os.path.join(W.DATA, "concept-list.tsv")), delimiter="\t"))
    items = []
    for r in rows:
        if r["route"] == "loan candidate":   # no form until the loan panel decides
            continue
        items.append({"gloss": r["concept"], "field": r["field"], "tier": int(r["tier"]), "route": r["route"],
                      "old": CURRENT.get(r["concept"], r["form"]), "fixed": r["route"] != "root" or r["concept"] in LOCKED, "ant": r["antonym"]})
    for r in W.read("lexicon.tsv"):
        if r["form"] in FIXED_OPS:
            items.append({"gloss": r["gloss"], "field": r["field"], "tier": int(r["tier"]), "route": "operator",
                          "old": r["form"], "fixed": r["form"] not in MOVE, "ant": ""})
    for it in items:
        it["freq"] = TIER_FREQ[it["tier"]]
    return items, rows


def weights(items):
    n = len(items)
    f = np.array([it["field"] for it in items])
    Wm = np.where(f[:, None] == f[None, :], 3.0, 1.0)
    num = f == "number"
    Wm[np.ix_(num, num)] = 30.0   # author 2026-11-18: number words x30 against each other only
    idx = {it["gloss"]: i for i, it in enumerate(items)}
    pairs = set()
    for l in open(os.path.join(W.DATA, "antonyms.tsv")):
        p = l.rstrip("\n").split("\t")
        if len(p) == 2 and p[0] in idx and p[1] in idx:
            pairs.add(frozenset((idx[p[0]], idx[p[1]])))
    for i, it in enumerate(items):
        if it["ant"]:
            for g in parse_antonyms(it["ant"], idx):
                pairs.add(frozenset((i, idx[g])))
    for p in pairs:
        if len(p) == 2:
            a, b = tuple(p)
            Wm[a, b] = Wm[b, a] = 30.0
    np.fill_diagonal(Wm, 0.0)
    return Wm.astype(np.float32), sorted(tuple(sorted(p)) for p in pairs if len(p) == 2)


ITEMS, CROWS = load_items()
N = len(ITEMS)
FREQ = np.array([it["freq"] for it in ITEMS])
WM, ANT_PAIRS = weights(ITEMS)
MOVABLE = [i for i, it in enumerate(ITEMS) if not it["fixed"]]
OLD = {i: tup(ITEMS[i]["old"]) for i in MOVABLE if ITEMS[i]["old"]}

# ------------------------------------------------------------------------------------------ rules
GRAM = W.read("grammar.tsv")
GFORM = {g["gloss"]: g["form"] for g in GRAM}
DIGITS = W.digit_syllables()                        # mu ni sa de wo ma
BIG = W.read("bigrams.tsv")
HAPLO = {IDX[GFORM[r["gloss"]]] for r in BIG if int(r["before_content"]) >= HAPLO_MIN and r["gloss"] in GFORM}
HAS_ONSET = np.array([INV.syl[s][0] != "" for s in range(NS)])
FIRST_OK = np.array([s not in DIGITS and s not in HAPLO for s in range(NS)])
# juncture.py check 3: a grammar word Cn whose open form C is also a grammar word makes "Cn X" ~ "C nX" for a
# vowel-initial content word X; so X and nX must not both be content words (only if such a pair exists)
GFORMS = {g["form"] for g in GRAM}
JPAIR = any(INV.syl[IDX[f]][2] == "n" and (INV.syl[IDX[f]][0].replace("j", "y") + INV.syl[IDX[f]][1]) in GFORMS for f in GFORMS)
N_OF = {s: M2.SYL_INDEX["n", v, c] for s, (o, v, c) in enumerate(M2.SYLLABLES) if o == ""}       # onsetless -> n-onset
O_OF = {M2.SYL_INDEX["n", v, c]: M2.SYL_INDEX["", v, c] for (o, v, c) in M2.SYLLABLES if o == ""}  # n-onset -> onsetless
LEN2 = np.array([[INV.length((a, b)) - 2.0 for b in range(NS)] for a in range(NS)])
# rule G (Decision 23, tests/stress-02/): no root sounds like two one-syllable grammar words in a row (ti wu ~ tiwu);
# only stress tells them apart. Roots checked and cleared keep their form (data/regroup-reviewed.tsv, form + gloss).
G1 = {IDX[f] for f in GFORMS if len(W.split(f)) == 1}
REVIEWED = {(r["form"], r["gloss"]) for r in W.read("regroup-reviewed.tsv")}
def g_bad(f, gloss):
    """Today's roots: exact sounds (the test measured those)."""
    return len(f) == 2 and f[0] in G1 and f[1] in G1 and (show(f), gloss) not in REVIEWED
GKEYS = {INV.content_key((a, b)) for a in G1 for b in G1}   # new forms: by drift key, as rule J (tiwo ~ ti wu)

KEYS = {}


def kid(key):
    return KEYS.setdefault(key, len(KEYS))


KEY2 = np.array([[kid(INV.content_key((a, b))) for b in range(NS)] for a in range(NS)])
VALID2 = np.zeros((NS, NS), bool)
OFF2 = np.zeros((NS, NS), bool)
for a in range(NS):
    for b in range(NS):
        fm = SYL[a] + SYL[b]
        OFF2[a, b] = offensive.matches(fm)
        VALID2[a, b] = FIRST_OK[a] and HAS_ONSET[b] and not offensive.blocked(fm)


def valid3(t):
    return FIRST_OK[t[0]] and HAS_ONSET[t[1]] and HAS_ONSET[t[2]] and not offensive.blocked(show(t))


def pool3(seed=5, n=600000):
    """Valid three-syllable forms (a random sample of the ~2.3M), as arrays: forms, key ids, length - 2."""
    rng = np.random.default_rng(seed)
    a = rng.integers(0, NS, n); b = rng.integers(0, NS, n); c = rng.integers(0, NS, n)
    ok = FIRST_OK[a] & HAS_ONSET[b] & HAS_ONSET[c]
    out = [t for t in dict.fromkeys(zip(a[ok].tolist(), b[ok].tolist(), c[ok].tolist())) if valid3(t)]
    F = np.array(out)
    K = np.array([kid(INV.content_key(t)) for t in out])
    L = np.array([INV.length(t) - 2.0 for t in out])
    return F, K, L


# ------------------------------------------------------------------------------------------ model
VARIANTS = M2.variants()
NV = len(VARIANTS)
TOPQ = int(math.ceil(0.25 * NV))
_models = [M2.Model(p) for _, p in VARIANTS]
S0 = np.stack([m.S_initial for m in _models]).astype(np.float32)   # (V, 140, 140) first syllable
S1 = np.stack([m.S_internal for m in _models]).astype(np.float32)  # later syllables
del _models


def conf_total(forms, items_idx=None, Wm=None, freq=None):
    """conf_v (V,) of a whole lexicon. forms: list of tuples (None = absent)."""
    Wm = WM if Wm is None else Wm
    freq = FREQ if freq is None else freq
    out = np.zeros(NV)
    ix = [i for i in range(len(forms)) if forms[i] is not None]
    lens = {}
    for i in ix:
        lens.setdefault(len(forms[i]), []).append(i)
    for L, g in lens.items():
        if len(g) < 2:
            continue
        g = np.array(g)
        F = np.array([forms[i] for i in g])
        Wf = (Wm[np.ix_(g, g)] * freq[g][:, None]).astype(np.float32)
        for v in range(NV):
            P = S0[v][np.ix_(F[:, 0], F[:, 0])]
            for k in range(1, L):
                P = P * S1[v][np.ix_(F[:, k], F[:, k])]
            out[v] += float((P * Wf).sum(dtype=np.float64))
    return out


def pair_matrix(forms, v):
    """P[i, j] under variant v, same-length words, diagonal 0."""
    n = len(forms)
    P = np.zeros((n, n), np.float32)
    lens = {}
    for i, f in enumerate(forms):
        lens.setdefault(len(f), []).append(i)
    for L, g in lens.items():
        g = np.array(g)
        F = np.array([forms[i] for i in g])
        Q = S0[v][np.ix_(F[:, 0], F[:, 0])]
        for k in range(1, L):
            Q = Q * S1[v][np.ix_(F[:, k], F[:, k])]
        P[np.ix_(g, g)] = Q
    np.fill_diagonal(P, 0)
    return P


def cvar(x):
    return np.sort(x)[::-1][:TOPQ].mean()


# ------------------------------------------------------------------------------------------ medians
def random_forms(rng, base, movable, taken_keys):
    forms = list(base)
    taken = set(taken_keys)
    cand = np.argwhere(VALID2)
    for i in movable:
        while True:
            a, b = cand[rng.integers(len(cand))]
            k = KEY2[a, b]
            if k not in taken:
                taken.add(k); forms[i] = (int(a), int(b)); break
    return forms


def _med_worker(args):
    seed, which = args
    os.environ["OMP_NUM_THREADS"] = "1"
    rng = np.random.default_rng(seed)
    if which == "after":
        base = [tup(it["old"]) if it["fixed"] else None for it in ITEMS]
        taken = {kid(INV.content_key(f)) for f in base if f is not None}
        return conf_total(random_forms(rng, base, MOVABLE, taken)).tolist()
    T = TODAY
    base = [tup(it["form"]) if it["fixed"] else None for it in T["items"]]
    taken = {kid(INV.content_key(f)) for f in base if f is not None}
    forms = random_forms(rng, base, [i for i, it in enumerate(T["items"]) if not it["fixed"]], taken)
    return conf_total(forms, Wm=T["W"], freq=T["freq"]).tolist()


def today():
    """Today's lexicon (data/lexicon.tsv, every content word) with the same weights."""
    lex = W.read("lexicon.tsv")
    items = [{"gloss": r["gloss"], "field": r["field"], "tier": int(r["tier"]), "form": r["form"],
              "fixed": r["field"] == "loan" or r["form"] in FIXED_OPS or len(W.split(r["form"])) != 2, "ant": ""} for r in lex]
    for it in items:
        it["freq"] = TIER_FREQ[it["tier"]]
    Wt, _ = weights(items)
    return {"items": items, "W": Wt, "freq": np.array([it["freq"] for it in items]),
            "forms": [tup(it["form"]) for it in items]}


TODAY = today()
NDRAW = 200  # random lexicons per median


def cmd_medians(which=("after", "today")):
    st = load_state("medians.json") or {}
    from multiprocessing import Pool
    for w in which:
        if w in st:
            continue
        done = st.get(w + "_draws", [])
        todo = [(1000 * (w == "today") + s, w) for s in range(len(done), NDRAW)]
        with Pool(min(16, os.cpu_count() or 1)) as pool:
            for k in range(0, len(todo), 32):
                done += pool.map(_med_worker, todo[k:k + 32])
                st[w + "_draws"] = done
                save("medians.json", st)
                print(f"medians {w}: {len(done)}/{NDRAW}", flush=True)
        st[w] = np.median(np.array(done), 0).tolist()
        save("medians.json", st)


def medians(which="after"):
    st = load_state("medians.json")
    if not st or which not in st:
        cmd_medians((which,))
        st = load_state("medians.json")
    return np.array(st[which])


# ------------------------------------------------------------------------------------------ placer
class Placer:
    def __init__(self, forms):
        self.med = medians("after")
        self.mb = self.med[0]                     # "best" variant
        self.forms = list(forms)
        self.X0 = np.zeros((NV, NS, 2 * N), np.float32)
        self.X1 = np.zeros((NV, NS, 2 * N), np.float32)
        self.owner = {}                           # key id -> item
        self.occ = set()                          # exact forms
        for i, f in enumerate(self.forms):
            if f is not None:
                self._put(i, f)
        self.T = conf_total(self.forms)
        self.eff = sum(EFFORT * FREQ[i] * (INV.length(f) - 2.0) for i, f in enumerate(self.forms) if f is not None)
        self.pool3 = pool3()
        self.rng = np.random.default_rng(11)

    def _cols(self, i, f):
        if len(f) == 2:
            a, b = f
            self.X0[:, :, i] = S0[:, :, a]; self.X0[:, :, N + i] = S0[:, a, :]
            self.X1[:, :, i] = S1[:, :, b]; self.X1[:, :, N + i] = S1[:, b, :]
        else:
            self.X0[:, :, i] = 0; self.X0[:, :, N + i] = 0; self.X1[:, :, i] = 0; self.X1[:, :, N + i] = 0

    def _put(self, i, f):
        k = kid(INV.content_key(f))
        assert self.owner.get(k, i) == i, (ITEMS[i]["gloss"], show(f), self.owner.get(k))
        self.owner[k] = i
        self.occ.add(f)
        self.forms[i] = f
        self._cols(i, f)

    def _remove(self, i):
        f = self.forms[i]
        del self.owner[kid(INV.content_key(f))]
        self.occ.discard(f)
        self.forms[i] = None
        self.X0[:, :, i] = 0; self.X0[:, :, N + i] = 0; self.X1[:, :, i] = 0; self.X1[:, :, N + i] = 0

    def grid2(self, i):
        u = np.concatenate([FREQ[i] * WM[i], WM[i] * FREQ]).astype(np.float32)
        return np.matmul(self.X0 * u, self.X1.transpose(0, 2, 1))     # (V, 140, 140)

    def contrib3(self, i, cands):
        """(V, K) pair cost of word i at each three-syllable candidate against the placed 3-syllable words."""
        others = [k for k, f in enumerate(self.forms) if f is not None and len(f) == 3 and k != i]
        C = np.asarray(cands).reshape(-1, 3)
        res = np.zeros((NV, len(C)))
        if not others:
            return res
        O = np.array([self.forms[k] for k in others])
        wo = (FREQ[i] * WM[i, others]).astype(np.float32)
        wi = (WM[i, others] * FREQ[others]).astype(np.float32)
        for v in range(NV):
            a, b = S0[v], S1[v]
            out = a[C[:, :1], O[None, :, 0]] * b[C[:, 1:2], O[None, :, 1]] * b[C[:, 2:3], O[None, :, 2]]
            inn = a[O[None, :, 0], C[:, :1]] * b[O[None, :, 1], C[:, 1:2]] * b[O[None, :, 2], C[:, 2:3]]
            res[v] = out @ wo + inn @ wi
        return res

    def free2(self, i):
        taken = np.zeros(len(KEYS) + 1, bool)
        for k, o in self.owner.items():
            if o != i:
                taken[k] = True
        ok = VALID2 & ~taken[KEY2]
        for a in range(NS):         # loan-vowel rule
            for b in range(NS):
                if ok[a, b] and INV.content_key((a, b)) in LOANV:
                    ok[a, b] = False
        for a in range(NS):         # rule G (by drift key; a cleared root keeps its own form)
            for b in range(NS):
                if ok[a, b] and INV.content_key((a, b)) in GKEYS and (show((a, b)), ITEMS[i]["gloss"]) not in REVIEWED:
                    ok[a, b] = False
        bad2 = j_keys2(self.occ)    # rule J
        if bad2:
            for a in range(NS):
                for b in range(NS):
                    if ok[a, b] and INV.content_key((a, b)) in bad2:
                        ok[a, b] = False
        for f in self.occ:          # accent rule
            for g in acc_neigh(f):
                if len(g) == 2:
                    ok[g] = False
        if JPAIR:   # juncture.py check 3
            for f in self.occ:
                if len(f) == 2:
                    a, b = f
                    if a in O_OF:
                        ok[O_OF[a], b] = False
                    if a in N_OF:
                        ok[N_OF[a], b] = False
        return ok

    def ok3(self, i, t):
        if not valid3(t) or self.owner.get(kid(INV.content_key(t)), i) != i:
            return False
        if any(g in self.occ for g in acc_neigh(t)):    # accent rule
            return False
        if INV.content_key(t) in LOANV:                 # loan-vowel rule
            return False
        if j_bad3(t, self.occ):                         # rule J
            return False
        if JPAIR:
            a = t[0]
            if a in O_OF and (O_OF[a],) + t[1:] in self.occ:
                return False
            if a in N_OF and (N_OF[a],) + t[1:] in self.occ:
                return False
        return True

    def best(self, i, allow3=None):
        """Best form for movable word i given the others: (form, marginal J). Word i must be removed."""
        allow3 = ITEMS[i]["tier"] <= MAX3_TIER if allow3 is None else allow3
        base = self.T.copy()
        effb = self.eff
        g = self.grid2(i).astype(np.float64)                          # (V,140,140)
        new = (base[:, None, None] + g) / self.med[:, None, None]
        r = -np.partition(-new, TOPQ - 1, axis=0)[:TOPQ].mean(0)       # CVaR per cell
        J0 = self.mb * cvar(base / self.med) + effb
        marg2 = self.mb * r + effb + EFFORT * FREQ[i] * LEN2 - J0
        ok = self.free2(i)
        marg2 = np.where(ok, marg2, np.inf)
        old = OLD.get(i)
        if KEEP and old is not None and len(old) == 2:
            marg2[old] -= KEEP          # keep term: every other form costs KEEP more than today's
        cands = []
        flat = np.argsort(marg2, axis=None)[:200]
        for fl in flat:
            a, b = divmod(int(fl), NS)
            if not np.isfinite(marg2[a, b]):
                break
            cands.append((float(marg2[a, b]), (a, b)))
        best2 = cands[0][0]
        if allow3 and best2 > EFFORT * FREQ[i] * 0.9:   # a 3-syllable form costs at least this much effort
            F3, K3k, L3 = self.pool3
            pick = self.rng.choice(len(F3), K3, replace=False)
            taken = np.zeros(len(KEYS) + 1, bool)
            for k, o in self.owner.items():
                if o != i:
                    taken[k] = True
            pick = pick[~taken[K3k[pick]]]
            pick = np.array([p for p in pick if self.ok3(i, tuple(F3[p]))], int)   # every candidate gets every rule
            forms3 = [tuple(int(x) for x in F3[p]) for p in pick]
            lens3 = L3[pick]
            cur = self.forms_prev.get(i) if hasattr(self, "forms_prev") else None
            if cur is not None and len(cur) == 3:
                forms3.append(cur); lens3 = np.append(lens3, INV.length(cur) - 2.0)
            c3 = self.contrib3(i, forms3)                               # (V,K)
            new3 = (base[:, None] + c3) / self.med[:, None]
            r3 = -np.partition(-new3, TOPQ - 1, axis=0)[:TOPQ].mean(0)
            m3 = self.mb * r3 + effb + EFFORT * FREQ[i] * lens3 - J0
            for k in np.argsort(m3)[:50]:
                cands.append((float(m3[k]), forms3[k]))
        cands.sort()
        lim = cands[0][0] + TIE * abs(cands[0][0])
        near = [c for c in cands if c[0] <= lim]
        clean = [c for c in near if not (OFF2[c[1]] if len(c[1]) == 2 else offensive.matches(show(c[1])))]
        m, f = (clean or near)[0]
        return f, m, g

    def place(self, i, f, g=None):
        """Put word i (removed) at f, updating totals."""
        if len(f) == 2:
            if g is None:
                g = self.grid2(i).astype(np.float64)
            add = g[:, f[0], f[1]]
        else:
            add = self.contrib3(i, [f])[:, 0]
        self.T = self.T + add
        self.eff += EFFORT * FREQ[i] * (INV.length(f) - 2.0)
        self._put(i, f)

    def take_out(self, i):
        f = self.forms[i]
        if len(f) == 2:
            g = self.grid2(i).astype(np.float64)
            sub = g[:, f[0], f[1]]
        else:
            sub = self.contrib3(i, [f])[:, 0]
        self.T = self.T - sub
        self.eff -= EFFORT * FREQ[i] * (INV.length(f) - 2.0)
        self._remove(i)
        return f

    def J(self):
        return self.mb * cvar(self.T / self.med) + self.eff

    def R(self):
        return cvar(self.T / self.med)


def ok_today(f, owner, occ, gloss=None):
    """Can today's form stay under the rules? (first syllable, onset, offensive, key free, accent, loan vowel, J, G)"""
    if g_bad(f, gloss):                         # rule G
        return False
    if len(f) == 2 and not VALID2[f]:
        return False
    if len(f) == 3 and not valid3(f):
        return False
    if kid(INV.content_key(f)) in owner:
        return False
    if any(g in occ for g in acc_neigh(f)):     # accent rule
        return False
    if INV.content_key(f) in LOANV:             # loan-vowel rule
        return False
    if j_bad3(f, occ) or (len(f) == 2 and INV.content_key(f) in j_keys2(occ)):   # rule J
        return False
    if JPAIR:
        a = f[0]
        if (a in O_OF and (O_OF[a],) + f[1:] in occ) or (a in N_OF and (N_OF[a],) + f[1:] in occ):
            return False
    return True


def cmd_start():
    st = load_state("A.json")
    if st and st.get("done"):
        print("A done"); return
    forms = [tup(it["old"]) if it["fixed"] else None for it in ITEMS]
    owner = {}
    occ = set()
    for i, f in enumerate(forms):
        if f is not None:
            assert kid(INV.content_key(f)) not in owner, ITEMS[i]["gloss"]
            owner[kid(INV.content_key(f))] = i; occ.add(f)
    kept, todo = [], []
    # two-syllable roots first, so rule J moves the (rarer) three-syllable root, not the word inside it
    for i in sorted(MOVABLE, key=lambda i: len(tup(ITEMS[i]["old"])) if ITEMS[i]["old"] else 9):
        it = ITEMS[i]
        if it["old"] and it["old"] not in MOVE:
            f = tup(it["old"])
            if ok_today(f, owner, occ, it["gloss"]):
                forms[i] = f; owner[kid(INV.content_key(f))] = i; occ.add(f); kept.append(i); continue
        todo.append(i)
    print(f"today's roots kept as they are: {len(kept)}; to place: {len(todo)}"
          + (": " + ", ".join(ITEMS[i]["gloss"] for i in todo[:40]) if todo else ""), flush=True)
    if not todo:
        save("A.json", {"forms": forms, "todo": [], "done": True})
        print("A done: nothing to place"); return
    if st:
        forms = [tuple(f) if f else None for f in st["forms"]]
        todo = st["todo"]
    P = Placer(forms)
    t0 = time.time()
    while todo:
        i = todo[0]
        f, m, g = P.best(i)
        P.place(i, f, g)
        todo = todo[1:]
        if len(todo) % 50 == 0:
            save("A.json", {"forms": P.forms, "todo": todo, "done": False})
            print(f"  A: {len(todo)} left, R {P.R():.4f} J {P.J():.4f} ({time.time() - t0:.0f}s)", flush=True)
    save("A.json", {"forms": P.forms, "todo": [], "done": True, "R": P.R(), "J": P.J()})
    print(f"A done: R {P.R():.4f} J {P.J():.4f}")


def cmd_descend(seed, maxsweeps=12):
    name = f"C-k{KEEP:g}-{seed}.json"
    st = load_state(name)
    if st and st.get("done"):
        print(name, "done"); return
    if st:
        forms, sweep, pos, hist = [tuple(f) for f in st["forms"]], st["sweep"], st["pos"], st["hist"]
        moved = st["moved"]
    else:
        start = load_state("A.json")
        assert start and start.get("done"), "run start first (same --state)"
        forms, sweep, pos, hist, moved = [tuple(f) for f in start["forms"]], 0, 0, [], 0
    P = Placer(forms)
    t0 = time.time()
    while sweep < maxsweeps:
        order = list(MOVABLE)
        random.Random(seed * 1000 + sweep).shuffle(order)
        for k in range(pos, len(order)):
            i = order[k]
            P.forms_prev = {i: P.forms[i]}
            old = P.take_out(i)
            f, m, g = P.best(i)
            P.place(i, f, g)
            if f != old:
                moved += 1
            if (k + 1) % 100 == 0:
                save(name, {"forms": P.forms, "sweep": sweep, "pos": k + 1, "hist": hist, "moved": moved, "done": False})
                print(f"  seed {seed} sweep {sweep + 1} {k + 1}/{len(order)} moved {moved} R {P.R():.4f} J {P.J():.4f} ({time.time() - t0:.0f}s)", flush=True)
        P.T = conf_total(P.forms)   # resync
        hist.append({"sweep": sweep + 1, "moved": moved, "R": P.R(), "J": P.J()})
        print(f"seed {seed} sweep {sweep + 1}: moved {moved}, R {P.R():.4f}, J {P.J():.4f}", flush=True)
        sweep += 1; pos = 0
        done = moved == 0
        moved = 0
        save(name, {"forms": P.forms, "sweep": sweep, "pos": 0, "hist": hist, "moved": 0, "done": done})
        if done:
            break
    st = load_state(name); st["done"] = True; save(name, st)


# ------------------------------------------------------------------------------------------ report
VN = [n for n, _ in VARIANTS]
_out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=_out)


def forms_of(name):
    st = load_state(name)
    assert st and st.get("done"), f"no finished state {name} in {state_dir()}"
    return [tuple(f) for f in st["forms"]]


def scores(forms, Wm=None, freq=None, med=None):
    Wm = WM if Wm is None else Wm
    freq = FREQ if freq is None else freq
    T = conf_total(forms, Wm=Wm, freq=freq)
    x = T / med
    R = cvar(x)
    eff = sum(EFFORT * freq[i] * (INV.length(f) - 2.0) for i, f in enumerate(forms))
    worst = [VN[k] for k in np.argsort(-x)[:3]]
    return R, med[0] * R + eff, x[0], worst


def sym_pairs(forms):
    """Per pair: best-variant symmetric confusion, and its robust version (mean of the worst quarter of
    variants of P(i->j) + P(j->i)). Upper triangle, same-length pairs only."""
    n = len(forms)
    lens = np.array([len(f) for f in forms])
    iu = np.triu_indices(n, 1)
    same = lens[iu[0]] == lens[iu[1]]
    iu = (iu[0][same], iu[1][same])
    allv = np.zeros((NV, len(iu[0])), np.float32)
    for v in range(NV):
        Pm = pair_matrix(forms, v)
        allv[v] = (Pm + Pm.T)[iu]
    rob = -np.partition(-allv, TOPQ - 1, axis=0)[:TOPQ].mean(0)
    return iu, allv[0], rob


# B2: single-feature neighbours (research/notes/unknown-unknowns.md #9: voicing, e/i, o/u, m/n, f/p, l/y/w, +-final n)
ALT_O = {"p": "bf", "b": "p", "t": "d", "d": "t", "k": "g", "g": "k", "m": "n", "n": "m", "f": "p", "l": "wj", "w": "lj", "j": "lw"}
ALT_V = {"e": "i", "i": "e", "o": "u", "u": "o"}


def neighbours(f):
    out = []
    for k, s in enumerate(f):
        o, v, c = M2.SYLLABLES[s]
        alts = [(x, v, c) for x in ALT_O.get(o, "")] + [(o, x, c) for x in ALT_V.get(v, "")] + [(o, v, "n" if c == "" else "")]
        for a in alts:
            out.append(f[:k] + (M2.SYL_INDEX[a],) + f[k + 1:])
    return out


def b2(forms, which):
    real = set(forms)
    tot = hit = 0
    for i in which:
        for nb in neighbours(forms[i]):
            tot += 1; hit += nb in real
    return hit, tot


def juncture(forms):
    """tools/juncture.py on a placement's lexicon."""
    orig = W.read
    rows = [{"gloss": it["gloss"], "field": it["field"], "tier": str(it["tier"]), "form": show(f)} for it, f in zip(ITEMS, forms)]
    W.read = lambda name: rows if name == "lexicon.tsv" else orig(name)
    buf = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(buf):
            runpy.run_path(os.path.join(TOOLS, "juncture.py"))
    except SystemExit as e:
        code = e.code
    finally:
        W.read = orig
    return code, buf.getvalue().strip()


def junction_risk(forms, roots):
    """n + vowel resegmentation (research/notes/confusion-data.md §3, junction 1; a report, the model has no
    junction term for content words): after a word ending in -n, a vowel-initial root X can be heard as nX, and
    an n-initial root nX after a word ending in a vowel can be heard as -n + X. Risk = how close the re-cut form is
    to a real content word of the same length (symmetric confusion, best variant and worst-quarter mean)."""
    words = {}
    for i, f in enumerate(forms):
        words.setdefault(len(f), []).append(i)
    rows = []
    for i in roots:
        f = forms[i]
        a = f[0]
        if a in N_OF:
            g = (N_OF[a],) + f[1:]; kind = "n+" + show(f)
        elif a in O_OF:
            g = (O_OF[a],) + f[1:]; kind = "-n " + show(g)
        else:
            continue
        others = [j for j in words[len(f)] if j != i]
        O = np.array([forms[j] for j in others])
        sv = np.zeros((NV, len(others)), np.float32)
        for v in range(NV):
            to = S0[v][g[0], O[:, 0]].copy(); fr = S0[v][O[:, 0], g[0]].copy()
            for k in range(1, len(f)):
                to *= S1[v][g[k], O[:, k]]; fr *= S1[v][O[:, k], g[k]]
            sv[v] = to + fr
        rob = -np.partition(-sv, TOPQ - 1, axis=0)[:TOPQ].mean(0)
        k = int(np.argmax(rob))
        exact = any(forms[j] == g for j in others)
        rows.append((float(rob[k]) if not exact else 1.0, float(sv[0, k]), i, others[k], kind, exact))
    return sorted(rows, reverse=True)


def cmd_report(names):
    """Scores, near pairs, B2 margin, p-initial count, moves, haplology and juncture checks, offensive matches;
    report.txt and forms.tsv in the state dir."""
    if not names:
        names = ["A.json"] + sorted(os.path.basename(p) for p in glob.glob(os.path.join(state_dir(), "C-*.json")))
    medA, medT = medians("after"), medians("today")
    T = TODAY
    say(f"{N} content words ({len(MOVABLE)} roots placed, {N - len(MOVABLE)} fixed: loans and operators); {NV} variants; "
        f"robust score R = mean of worst {TOPQ} of conf_v / random median (1.0 = random lexicon)")
    say(f"random medians, best variant: today {medT[0]:.2f}, full list {medA[0]:.2f}; v1 variant: today {medT[-1]:.2f}, full list {medA[-1]:.2f}")
    Rt, Jt, bt, wt = scores(T["forms"], T["W"], T["freq"], medT)
    say(f"today's lexicon ({len(T['forms'])} words, data/lexicon.tsv): R {Rt:.4f} | best variant {bt:.4f} | worst variants {', '.join(wt)}")
    res = {}
    for nm in names:
        f = forms_of(nm)
        R, J, b, w = scores(f, med=medA)
        res[nm] = (R, J, f)
        say(f"{nm}: R {R:.4f} | J {J:.3f} | best variant {b:.4f} | worst variants {', '.join(w)}")
    cs = [n for n in names if os.path.basename(n).startswith("C")] or names
    pick = min(cs, key=lambda n: res[n][1])
    forms = res[pick][2]
    say(f"chosen: {pick} (lowest J)")
    if len(cs) > 1:
        same = sum(1 for i in MOVABLE if len({res[n][2][i] for n in cs}) == 1)
        sl = sum(1 for i in MOVABLE if len({len(res[n][2][i]) for n in cs}) == 1)
        say(f"seeds agree on {same} of {len(MOVABLE)} root forms ({100 * same / len(MOVABLE):.0f}%); on length for {sl}")
    an = [n for n in names if os.path.basename(n).startswith("A")]
    A = res[an[0]][2] if an else None

    # length
    n3 = [i for i in MOVABLE if len(forms[i]) == 3]
    say(f"three-syllable roots: {len(n3)}" + (": " + ", ".join(f"{ITEMS[i]['gloss']} {show(forms[i])}" for i in n3) if n3 else ""))
    t1 = [i for i in MOVABLE if ITEMS[i]["tier"] == 1]
    say(f"  tier 1: {sum(len(forms[i]) == 3 for i in t1)} of {len(t1)} at three syllables; other tiers: {sum(len(forms[i]) == 3 for i in MOVABLE if ITEMS[i]['tier'] > 1)}")
    vi = lambda i: INV.syl[forms[i][0]][0] == ""
    say(f"  vowel-initial roots: {sum(vi(i) for i in MOVABLE)} of {len(MOVABLE)} (two-syllable {sum(vi(i) for i in MOVABLE if len(forms[i]) == 2)}, three-syllable {sum(vi(i) for i in n3)})")
    # moved
    old = [i for i in MOVABLE if ITEMS[i]["old"]]
    mv = [i for i in old if show(forms[i]) != ITEMS[i]["old"]]
    must = [i for i in old if A is not None and show(A[i]) != ITEMS[i]["old"]]
    say(f"today's roots moved: {len(mv)} of {len(old)} (forced by the rules: {len(must)})")
    # near pairs
    tf = T["forms"]
    iu0, b0, r0 = sym_pairs(tf)
    thr_b, thr_r = np.quantile(b0, 0.99), np.quantile(r0, 0.99)
    iu, bb, rr = sym_pairs(forms)
    say(f"near pairs (above today's 99th percentile of pair confusion): best variant thr {thr_b:.2e}: today {int((b0 > thr_b).sum())} "
        f"of {len(b0)} pairs, after {int((bb > thr_b).sum())} of {len(bb)}; robust (worst-quarter mean) thr {thr_r:.2e}: today "
        f"{int((r0 > thr_r).sum())}, after {int((rr > thr_r).sum())}")
    if A is not None:
        _, ba, ra = sym_pairs(A)
        say(f"  A (one at a time): best {int((ba > thr_b).sum())}, robust {int((ra > thr_r).sum())}")
    # nearest-neighbour confusion, frequency-weighted, best variant
    Pm = pair_matrix(forms, 0); nn = (Pm + Pm.T).max(1)
    Pt = pair_matrix(tf, 0); nnt = (Pt + Pt.T).max(1)
    say(f"frequency-weighted nearest-neighbour confusion (best variant): today {(T['freq'] * nnt).sum() / T['freq'].sum():.5f}, after {(FREQ * nn).sum() / FREQ.sum():.5f}")
    # B2
    troots = [i for i, it in enumerate(T["items"]) if not it["fixed"]]
    h0, t0 = b2(tf, troots)
    roots = MOVABLE
    h1, t1 = b2(forms, roots)
    h2, t2 = b2(forms, range(N))
    say(f"B2 margin (single-feature neighbours that are real words): today's roots {h0}/{t0} = {100 * h0 / t0:.2f}%; "
        f"new roots {h1}/{t1} = {100 * h1 / t1:.2f}%; all content words {h2}/{t2} = {100 * h2 / t2:.2f}%")
    if A is not None:
        ha, ta = b2(A, roots)
        say(f"  A (one at a time): roots {ha}/{ta} = {100 * ha / ta:.2f}%")
    # p-initial
    p0 = sum(1 for i in troots if INV.syl[tf[i][0]][0] == "p")
    p1 = sum(1 for i in roots if INV.syl[forms[i][0]][0] == "p")
    pall = sum(1 for i in range(N) if INV.syl[forms[i][0]][0] == "p")
    say(f"p-initial roots: today {p0} of {len(troots)}; after {p1} of {len(roots)} (all content words incl. loans: {pall})")
    on = {}
    for i in roots:
        o = INV.syl[forms[i][0]][0] or "V"
        on[o] = on.get(o, 0) + 1
    say("  first-onset counts, new roots: " + " ".join(f"{k}:{v}" for k, v in sorted(on.items(), key=lambda x: -x[1])))
    # haplology / digit check
    bad = [i for i in roots if forms[i][0] in HAPLO or forms[i][0] in DIGITS]
    fixedbad = [i for i in range(N) if ITEMS[i]["fixed"] and (forms[i][0] in HAPLO or forms[i][0] in DIGITS)]
    say(f"haplology + digit check (roots starting with {' '.join(sorted(SYL[s] for s in HAPLO))} or a digit): "
        f"{'passed' if not bad else 'FAILED ' + str([show(forms[i]) for i in bad])}; fixed words that do (kept by rule 2): "
        + ", ".join(f"{show(forms[i])} ({ITEMS[i]['gloss']})" for i in fixedbad))
    keys = [INV.content_key(f) for f in forms]
    say(f"unique drift keys: {'yes' if len(set(keys)) == N else 'NO'}; "
        f"second syllable onset: {'yes' if all(all(HAS_ONSET[s] for s in f[1:]) for f in forms) else 'NO'}; "
        f"blocked forms: {sum(offensive.blocked(show(f)) for f in forms)}")
    code, txt = juncture(forms)
    say(f"juncture.py on the result: exit {code}: {txt}")
    offr = [i for i in roots if offensive.matches(show(forms[i]))]
    offt = [i for i in troots if offensive.matches(show(tf[i]))]
    say(f"offensive.matches (C3 tie-break only): new roots {len(offr)}: " + ", ".join(f"{show(forms[i])} ({ITEMS[i]['gloss']})" for i in offr)
        + f"; today's roots {len(offt)}")

    # n + vowel junction risk
    jr = junction_risk(forms, MOVABLE)
    say(f"\nn + vowel junction risk (vowel- or n-initial roots, {len(jr)}; re-cut form vs nearest real word, robust / best variant):")
    if A is not None:
        ja = junction_risk(A, MOVABLE)
        say(f"  sum of robust risk: after {sum(r[0] for r in jr):.3e}; A (today's roots kept) {sum(r[0] for r in ja):.3e}; exact clashes after {sum(r[5] for r in jr)}")
    for r, b, i, j, kind, ex in jr[:15]:
        say(f"  {r:.2e} {b:.2e}  {kind} ({ITEMS[i]['gloss']}, t{ITEMS[i]['tier']})  ~  {show(forms[j])} {ITEMS[j]['gloss']} (t{ITEMS[j]['tier']}){'  EXACT' if ex else ''}")

    # lists for the author
    pos = {(a, b): k for k, (a, b) in enumerate(zip(*iu))}
    say("\nantonym pairs, closest (best-variant / robust symmetric confusion):")
    ap = []
    for a, b in ANT_PAIRS:
        k = pos.get((min(a, b), max(a, b)))
        if k is not None:
            ap.append((rr[k], bb[k], a, b))
    for r, b, x, y in sorted(ap, reverse=True)[:15]:
        say(f"  {r:.2e} {b:.2e}  {show(forms[x])} {ITEMS[x]['gloss']}  ~  {show(forms[y])} {ITEMS[y]['gloss']}")
    say("\nnear pairs among frequent words (both tier >= 3), by robust confusion, top 25:")
    fr = [(rr[k], bb[k], a, b) for k, (a, b) in enumerate(zip(*iu)) if ITEMS[a]["tier"] >= 3 and ITEMS[b]["tier"] >= 3]
    for r, b, x, y in sorted(fr, reverse=True)[:25]:
        say(f"  {r:.2e} {b:.2e}  {show(forms[x])} {ITEMS[x]['gloss']} (t{ITEMS[x]['tier']}, {ITEMS[x]['field']})  ~  "
            f"{show(forms[y])} {ITEMS[y]['gloss']} (t{ITEMS[y]['tier']}, {ITEMS[y]['field']})  W {WM[x, y]:.0f}")
    say("\nall near pairs (robust, above today's 99th percentile), top 40:")
    top = np.argsort(-rr)[:40]
    for k in top:
        a, b = iu[0][k], iu[1][k]
        say(f"  {rr[k]:.2e} {bb[k]:.2e}  {show(forms[a])} {ITEMS[a]['gloss']} (t{ITEMS[a]['tier']})  ~  {show(forms[b])} {ITEMS[b]['gloss']} (t{ITEMS[b]['tier']})")
    say("\nfrequent roots (tier >= 4) whose form changed:")
    for i in sorted(old, key=lambda i: (-ITEMS[i]["tier"], ITEMS[i]["gloss"])):
        if ITEMS[i]["tier"] >= 4 and show(forms[i]) != ITEMS[i]["old"]:
            say(f"  t{ITEMS[i]['tier']} {ITEMS[i]['gloss']}: {ITEMS[i]['old']} -> {show(forms[i])}")
    say("\nnew roots, tier >= 4:")
    for i in MOVABLE:
        if ITEMS[i]["tier"] >= 4 and not ITEMS[i]["old"]:
            say(f"  t{ITEMS[i]['tier']} {ITEMS[i]['gloss']}: {show(forms[i])}")

    d = state_dir()
    with open(os.path.join(d, "forms.tsv.tmp"), "w") as fh:
        fh.write("concept\told form\tnew form\tfield\ttier\troute\n")
        byg = {it["gloss"]: (it, f) for it, f in zip(ITEMS, forms)}
        for r in CROWS:
            it, f = byg.get(r["concept"], (None, None))
            fh.write(f"{r['concept']}\t{r['form']}\t{show(f) if f else ''}\t{r['field']}\t{r['tier']}\t{r['route']}\n")
        for it, f in zip(ITEMS, forms):
            if it["route"] == "operator":
                fh.write(f"{it['gloss']}\t{it['old']}\t{show(f)}\t{it['field']}\t{it['tier']}\toperator (fixed)\n")
    os.replace(os.path.join(d, "forms.tsv.tmp"), os.path.join(d, "forms.tsv"))
    with open(os.path.join(d, "report.txt"), "w") as fh:
        fh.write(_out.getvalue())
    print(f"wrote {os.path.join(d, 'report.txt')} and forms.tsv")


# ------------------------------------------------------------------------------------------ write
def cmd_write(name):
    """Put a finished state's forms into data/: lexicon.tsv (changed forms; new concepts appended), then the map
    (old form -> new form) on numbers.tsv, compounds.tsv and roles.tsv (tools/apply_forms.py data step); map.tsv in
    the state dir for the texts. Runs tools/check_all.py at the end."""
    import apply_forms as AF
    forms = forms_of(name)
    lex = W.read("lexicon.tsv")
    by_gloss = {r["gloss"]: r for r in lex}
    fmap, added = {}, []
    for it, f in zip(ITEMS, forms):
        new = show(f)
        r = by_gloss.get(it["gloss"])
        if r is None:
            added.append({"gloss": it["gloss"], "field": it["field"], "tier": str(it["tier"]), "form": new})
        elif r["form"] != new:
            fmap[r["form"]] = new
    forms_all = [fmap.get(r["form"], r["form"]) for r in lex] + [r["form"] for r in added]
    assert len(forms_all) == len(set(forms_all)), sorted({f for f in forms_all if forms_all.count(f) > 1})
    AF.map_column(os.path.join(W.DATA, "lexicon.tsv"), "form", lambda f: fmap.get(f, f), append=added)
    mpath = os.path.join(state_dir(), "map.tsv")
    with open(mpath, "w") as fh:
        fh.write("old\tnew\n" + "".join(f"{k}\t{v}\n" for k, v in sorted(fmap.items())))
    print(f"lexicon.tsv: {len(fmap)} forms changed, {len(added)} roots added")
    for r in added:
        print(f"  new: {r['form']} {r['gloss']} ({r['field']}, tier {r['tier']})")
    AF.apply_data(fmap, files=("numbers.tsv", "compounds.tsv", "roles.tsv"))
    have = {r["form"] for r in W.read("roles.tsv")}
    todo = [r["form"] + " " + r["gloss"] for r in W.read("lexicon.tsv") if r["field"] not in ("number", "loan") and r["form"] not in FIXED_OPS
            and r["form"] not in have]
    if todo:
        print(f"roles.tsv needs a row for: {', '.join(todo)} (tools/gf_lexicon.py fails until it has one)")
    if fmap:
        print(f"map: {mpath}; apply it to the texts: tools/apply_forms.py text {mpath} spec/reference.toml docs/*.md ..."
              " (then tokens / literals for grammar/ and the UDHR translation; see its docstring)")
    sys.exit(AF.run_check_all())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    rest = [a for a in sys.argv[2:] if not a.startswith("--")]
    rest = [a for a in rest if a not in (_arg("--state"), _arg("--keep"), _arg("--move"))]
    if cmd == "medians":
        cmd_medians()
    elif cmd == "start":
        cmd_start()
    elif cmd == "descend":
        cmd_descend(int(rest[0]) if rest else 1)
    elif cmd == "report":
        cmd_report(rest)
    elif cmd == "write":
        assert rest, "write STATE (e.g. A.json or C-k0.03-1.json in --state DIR)"
        cmd_write(rest[0])
    elif cmd == "info":
        print(N, "items;", len(MOVABLE), "movable;", len(ANT_PAIRS), "antonym pairs;", NV, "variants; HAPLO", sorted(SYL[s] for s in HAPLO),
              "; JPAIR", JPAIR, "; valid 2-syll forms", int(VALID2.sum()))
    else:
        sys.exit(__doc__)
