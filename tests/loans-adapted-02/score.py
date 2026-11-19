"""How close do adapted loans stay to the forms speakers already use? (author, 2026-11-19; README.md)

For every loan in forms.tsv and every panel language that uses the shared form (mark y or b), the phonetic
distance between the Apupiwe form and that language's own pronunciation (its IPA). Then the same for each
variant of the adaptation rules (tools/names.py), to see which rules keep loans closest to the world.

  python3 score.py               # summary per variant -> results.txt, per-loan table -> loans-scored.tsv

Distance (added; a proxy for recognisability, not a listener model): weighted edit distance over segments.
Substituting two consonants costs the share of differing features (place 0.4, manner 0.4, voicing 0.2);
two vowels: height 0.5 (per step of 3), backness 0.3, rounding 0.2; a consonant for a vowel 1. Inserting or
deleting a consonant costs 1, a vowel 0.5 (an added or lost vowel is less salient than a consonant).
Normalised by the longer form's segment count, so 0 = identical, about 1 = unrelated. Stress, length, tone,
aspiration and other diacritics are ignored. A loan's score is the mean over its y/b languages; also the
mean per region and the worst region.
"""
import csv, os, re, sys, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

REGION = {"zh": "EA", "ja": "EA", "ko": "EA", "vi": "SEA", "th": "SEA", "id": "SEA", "tl": "SEA", "hi": "SA", "bn": "SA",
          "ta": "SA", "fa": "WA", "ar": "WA", "tr": "WA", "ru": "EU", "es": "EU", "fr": "EU", "sw": "SSA", "ha": "SSA",
          "yo": "SSA", "qu": "AM"}

# ------------------------------------------------------------------------------------------ segments and features
# consonant: (place, manner, voiced)
C = {}
def _c(syms, place, manner, voiced):
    for s in syms.split():
        C[s] = (place, manner, voiced)
_c("p", "lab", "stop", 0); _c("b", "lab", "stop", 1); _c("t ʈ", "cor", "stop", 0); _c("d ɖ", "cor", "stop", 1)
_c("c", "pal", "stop", 0); _c("ɟ", "pal", "stop", 1); _c("k q", "vel", "stop", 0); _c("g ɡ ɢ", "vel", "stop", 1)
_c("ʔ", "glot", "stop", 0)
_c("m ɱ", "lab", "nas", 1); _c("n ɳ", "cor", "nas", 1); _c("ɲ", "pal", "nas", 1); _c("ŋ ɴ", "vel", "nas", 1)
_c("ɸ f", "lab", "fric", 0); _c("β v", "lab", "fric", 1); _c("θ s", "cor", "fric", 0); _c("ð z", "cor", "fric", 1)
_c("ʃ ʂ ɕ", "pal", "fric", 0); _c("ʒ ʐ ʑ", "pal", "fric", 1); _c("ç", "pal", "fric", 0); _c("ʝ", "pal", "fric", 1)
_c("x χ", "vel", "fric", 0); _c("ɣ ʁ", "vel", "fric", 1); _c("ħ h", "glot", "fric", 0); _c("ʕ ɦ", "glot", "fric", 1)
_c("tʃ ʧ tɕ ʈʂ", "pal", "aff", 0); _c("dʒ ʤ dʑ ɖʐ", "pal", "aff", 1); _c("ts ʦ", "cor", "aff", 0); _c("dz ʣ", "cor", "aff", 1)
_c("l ɫ ɭ ʎ", "cor", "lat", 1); _c("r ɾ ɹ ɻ ʀ ɽ", "cor", "rhot", 1)
_c("j", "pal", "glide", 1); _c("w ɥ ʋ ɰ", "lab", "glide", 1)
# vowel: (height 0-3, back 0-2, round)
V = {}
def _v(syms, h, b, r):
    for s in syms.split():
        V[s] = (h, b, r)
_v("i", 3, 0, 0); _v("y", 3, 0, 1); _v("ɪ", 2.5, 0, 0); _v("ʏ", 2.5, 0, 1); _v("ɨ", 3, 1, 0); _v("ʉ", 3, 1, 1)
_v("ɯ", 3, 2, 0); _v("u", 3, 2, 1); _v("ʊ", 2.5, 2, 1); _v("e", 2, 0, 0); _v("ø", 2, 0, 1); _v("ɘ ə ɵ", 1.5, 1, 0)
_v("ɤ", 2, 2, 0); _v("o", 2, 2, 1); _v("ɛ", 1, 0, 0); _v("œ", 1, 0, 1); _v("ɜ ɐ", 1, 1, 0); _v("ʌ", 1, 2, 0)
_v("ɔ", 1, 2, 1); _v("æ", 0.5, 0, 0); _v("a ä", 0, 1, 0); _v("ɑ", 0, 2, 0); _v("ɒ", 0, 2, 1); _v("ɶ", 0, 0, 1)
MULTI = sorted([k for k in C if len(k) > 1], key=len, reverse=True)


def segments(ipa):
    """Broad IPA -> list of segment symbols; diacritics, stress, length, tone and syllable marks dropped.
    Returns (segments, unknown symbols)."""
    s = unicodedata.normalize("NFD", ipa)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[/\[\]()ˈˌːˑ.‿ʰʲʷˀ˞ˠˤ⁽⁾\-–'’ ,˥˦˧˨˩0-9ꜜꜛ↗↘]", "", s).replace("ɡ", "g").replace("ç", "ç")
    out, unk, i = [], [], 0
    while i < len(s):
        for m in MULTI:
            if s.startswith(m, i):
                out.append(m); i += len(m); break
        else:
            ch = s[i]
            if ch in C or ch in V:
                out.append(ch)
            elif ch.isalpha():
                unk.append(ch)
            i += 1
    return out, unk


def sub_cost(a, b):
    if a == b:
        return 0.0
    if a in C and b in C:
        (p1, m1, v1), (p2, m2, v2) = C[a], C[b]
        return 0.4 * (p1 != p2) + 0.4 * (m1 != m2) + 0.2 * (v1 != v2)
    if a in V and b in V:
        (h1, b1, r1), (h2, b2, r2) = V[a], V[b]
        return 0.5 * abs(h1 - h2) / 3 + 0.3 * abs(b1 - b2) / 2 + 0.2 * (r1 != r2)
    return 1.0


def indel(a):
    return 0.5 if a in V else 1.0


def distance(x, y):
    n, m = len(x), len(y)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        D[i][0] = D[i - 1][0] + indel(x[i - 1])
    for j in range(1, m + 1):
        D[0][j] = D[0][j - 1] + indel(y[j - 1])
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j] + indel(x[i - 1]), D[i][j - 1] + indel(y[j - 1]),
                          D[i - 1][j - 1] + sub_cost(x[i - 1], y[j - 1]))
    return D[n][m] / max(n, m, 1)


def apu_segments(form):
    return [{"y": "j"}.get(ch, ch) for ch in form]


# ------------------------------------------------------------------------------------------ adaptation variants
import names   # tools/names.py: the current rules

FRONT = "iɪyʏeɛøœæ"
RHOTIC = "rɾɹʁɻʀɽ"
VOW = "".join(V)


def prepare(ipa, v):
    """Rewrite the source IPA so that names.adapt applies variant v (a dict of switches)."""
    s = ipa.replace("ʧ", "tʃ").replace("ʤ", "dʒ").replace("ɡ", "g").replace("ʦ", "ts").replace("ʣ", "dz")
    s = re.sub(r"[ˈˌ\[\]/ .\-‿()˥˦˧˨˩ꜜꜛ0-9]", "", s.split(",")[0].split("~")[0])
    s = unicodedata.normalize("NFC", "".join(ch for ch in unicodedata.normalize("NFD", s)
                                             if not unicodedata.combining(ch) or ch == "\u0303"))
    if v.get("aff_front"):          # ch/j before a front vowel -> k/g (2.9: k g before i e may sound like ch j)
        s = re.sub(r"(tʃ|tɕ|ʈʂ)(?=[ʰʲː]*[" + FRONT + "])", "k", s)
        s = re.sub(r"(dʒ|dʑ|ɖʐ)(?=[ʰʲː]*[" + FRONT + "])", "g", s)
        if v.get("zh_too"):
            s = re.sub(r"ʒ(?=[ʰʲː]*[" + FRONT + "])", "g", s)
    if v.get("dzh_y"):              # remaining j -> y (as Spanish, Yoruba, many speakers say it)
        s = s.replace("dʒ", "j").replace("dʑ", "j")
    if v.get("drop_final_r"):       # r after a vowel and before a consonant or the end is dropped
        s = re.sub(r"(?<=[" + VOW + r"ː])[" + RHOTIC + r"](?=[^" + VOW + r"]|$)", "", s)
    return s


def adapt(ipa, v):
    return names.adapt(prepare(ipa, v), "echo" if v.get("echo") else "default")


VARIANTS = {
    "current": {},
    "aff-front": {"aff_front": True},
    "aff-front+zh": {"aff_front": True, "zh_too": True},
    "j-as-y": {"dzh_y": True},
    "aff-front+j-as-y": {"aff_front": True, "dzh_y": True},
    "drop-final-r": {"drop_final_r": True},
    "echo-vowel": {"echo": True},
    "aff-front+drop-r": {"aff_front": True, "drop_final_r": True},
    "aff-front+drop-r+echo": {"aff_front": True, "drop_final_r": True, "echo": True},
}


# ------------------------------------------------------------------------------------------ scoring
def load():
    rows = list(csv.DictReader(open(os.path.join(HERE, "forms.tsv")), delimiter="\t"))
    loans = collections.OrderedDict()
    for r in rows:
        L = loans.setdefault(r["concept"], {"adapted": r["adapted"], "median": r["median_ipa"], "langs": {}})
        if r["mark"] in ("y", "b") and r["ipa"].strip():
            L["langs"][r["lang"]] = r["ipa"]
    return loans


def apu_variants(form):
    """The form as said in the reference and with the declared harmless variants that matter here (reference 2.9):
    k g before i e as ch j; p t k b d g as written. Each segment list is one way to say it."""
    base = apu_segments(form)
    outs = [base]
    alt = [("tʃ" if x == "k" else "dʒ") if x in "kg" and i + 1 < len(base) and base[i + 1] in "ie" else x
           for i, x in enumerate(base)]
    if alt != base:
        outs.append(alt)
    return outs


def score_form(form, langs, with_variants=False):
    forms = apu_variants(form) if with_variants else [apu_segments(form)]
    per = {}
    for lg, ipa in langs.items():
        seg, _ = segments(ipa)
        if seg:
            per[lg] = min(distance(a, seg) for a in forms)
    if not per:
        return None
    reg = collections.defaultdict(list)
    for lg, d in per.items():
        reg[REGION[lg]].append(d)
    regm = {k: sum(x) / len(x) for k, x in reg.items()}
    return {"mean": sum(per.values()) / len(per), "regions": sum(regm.values()) / len(regm),
            "worst": max(regm.values()), "per": per, "regm": regm}


def medoid(langs):
    """The y/b language form closest to all the others (added variant 'medoid source')."""
    segs = {lg: segments(ipa)[0] for lg, ipa in langs.items()}
    segs = {k: v for k, v in segs.items() if v}
    best = min(segs, key=lambda a: sum(distance(segs[a], segs[b]) for b in segs if b != a))
    return langs[best], best


def main():
    loans = load()
    loans = {k: v for k, v in loans.items() if v["langs"]}
    out = []
    say = lambda *a: (print(*a), out.append(" ".join(str(x) for x in a)))
    rows = []
    repro = sum(1 for L in loans.values() if L["median"] and safe(L["median"], {}) == L["adapted"])
    say(f"{len(loans)} loans with IPA for at least one y/b language; the current rules reproduce {repro} of their forms "
        f"from the recorded median (the rest were chosen by hand or from another source; 'current' scores the real forms)")
    summary = {}
    for name, v in list(VARIANTS.items()) + [("medoid source (current rules)", {"medoid": True}),
                                             ("medoid source + aff-front", {"medoid": True, "aff_front": True})]:
        tot = collections.defaultdict(list)
        changed = 0
        for c, L in loans.items():
            if name == "current":
                form = L["adapted"]
            else:
                src = medoid(L["langs"])[0] if v.get("medoid") else L["median"]
                form = safe(src, v) or L["adapted"]
            changed += form != L["adapted"]
            sc = score_form(form, L["langs"])
            if sc is None:
                continue
            for k in ("mean", "regions", "worst"):
                tot[k].append(sc[k])
            tot["regions+var"].append(score_form(form, L["langs"], True)["regions"])
            rows.append({"variant": name, "concept": c, "form": form, "mean": round(sc["mean"], 3),
                         "regions": round(sc["regions"], 3), "worst": round(sc["worst"], 3),
                         "worst_region": max(sc["regm"], key=sc["regm"].get)})
        summary[name] = {k: sum(x) / len(x) for k, x in tot.items()}
        summary[name]["changed"] = changed
    say(f"\n{'variant':34}{'changed':>8}{'mean':>8}{'regions':>9}{'worst reg':>10}{'regions, variants':>19}   (distance: 0 identical, ~1 unrelated)")
    for name, s in summary.items():
        say(f"{name:34}{s['changed']:>8}{s['mean']:>8.3f}{s['regions']:>9.3f}{s['worst']:>10.3f}{s['regions+var']:>19.3f}")
    with open(os.path.join(HERE, "loans-scored.tsv"), "w") as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    if FAIL:
        say("\nadaptation failures (fell back to the current form):", dict(FAIL.most_common(8)))
    open(os.path.join(HERE, "results.txt"), "w").write("\n".join(out) + "\n")


FAIL = collections.Counter()


def safe(ipa, v):
    try:
        f = adapt(ipa, v)
        import words as W
        W.split(f)
        return f
    except Exception as e:
        FAIL[str(e)[:60]] += 1
        return None


def nearest(argv):
    """Per loan: candidates = the current form, and every form the rules (current, aff-front) make from the median
    or from any y/b language's own IPA; keep those the language allows (W.split) and that don't collide with another
    word. Report the candidate with the lowest region-balanced distance where it beats the current form."""
    import words as W
    lex = {r["form"]: r["gloss"] for r in W.read("lexicon.tsv")}
    gram = {r["form"] for r in W.read("grammar.tsv")} | {r["form"] for r in W.read("numbers.tsv")}
    loans = {k: v for k, v in load().items() if v["langs"]}
    rows, gains = [], []
    for c, L in loans.items():
        cur = score_form(L["adapted"], L["langs"])
        cands = {}
        for src_name, src in [("median", L["median"])] + [(lg, ipa) for lg, ipa in L["langs"].items()]:
            for vn in ("current", "aff-front"):
                f = safe(src, VARIANTS[vn])
                if f and f != L["adapted"] and f not in gram and (f not in lex or lex[f] == c):
                    cands.setdefault(f, f"{vn} from {src_name}")
        best = None
        for f, how in cands.items():
            sc = score_form(f, L["langs"])
            if sc and (best is None or sc["regions"] < best[1]["regions"]):
                best = (f, sc, how)
        gain = cur["regions"] - best[1]["regions"] if best else 0.0
        rows.append({"concept": c, "current": L["adapted"], "current_regions": round(cur["regions"], 3),
                     "current_worst": round(cur["worst"], 3), "best": best[0] if best else "",
                     "best_regions": round(best[1]["regions"], 3) if best else "", "gain": round(gain, 3),
                     "how": best[2] if best else ""})
        gains.append(gain)
    rows.sort(key=lambda r: -r["gain"])
    with open(os.path.join(HERE, "nearest.tsv"), "w") as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} loans; a candidate beats the current form for {sum(g > 0 for g in gains)}; by more than 0.05 for "
          f"{sum(g > 0.05 for g in gains)}, more than 0.10 for {sum(g > 0.10 for g in gains)}")
    print(f"region-balanced mean: current {sum(r['current_regions'] for r in rows) / len(rows):.3f}, best per loan "
          f"{sum(min(r['current_regions'], r['best_regions'] or 9) for r in rows) / len(rows):.3f}")
    for r in rows[:30]:
        print(f"  {r['concept']:28} {r['current']:14} {r['current_regions']:.3f} -> {r['best']:14} {r['best_regions']}  "
              f"(gain {r['gain']:+.3f}; {r['how']})")


if __name__ == "__main__":
    if sys.argv[1:2] == ["nearest"]:
        nearest(sys.argv[2:])
    else:
        main()
