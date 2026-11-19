"""Candidate tokens in a panel cell's free-text word field, and lookup keys for each."""
import re
import unicodedata

SCRIPT = dict(
    zh=r"[A-Z]?[\u3400-\u4dbf\u4e00-\u9fff]+",
    ja=r"[A-Z]?[぀-ヿ一-鿿ー・]+",
    ko=r"[가-힯]+(?: [가-힯]+)*",
    th=r"[฀-๿]+(?: [฀-๿]+)*",
    hi=r"[\u0900-\u097f]+(?:[ -][\u0900-\u097f]+)*",
    bn=r"[\u0980-\u09ff]+(?:[ -][\u0980-\u09ff]+)*",
    ta=r"[\u0b80-\u0bff]+(?:[ -][\u0b80-\u0bff]+)*",
    fa=r"[؀-ۿ‌]+(?: [؀-ۿ‌]+)*",
    ar=r"[؀-ۿ]+(?: [؀-ۿ]+)*",
    ru=r"[Ѐ-ӿ́]+(?:[ -][Ѐ-ӿ́]+)*",
)
LATIN = set("vi id tl tr es fr sw ha yo qu".split())
SKIP = set("""also and or the a of in for with beside formal spoken informal loan spanish french english arabic
listed first everyday not is as from colloquial common older sense subs leipzig wt we m the native word
running text bilingual speech short form only rival broad likely no data entry younger speakers used used""".split())


def strip_marks(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))


def keys(lang, tok):
    """Spellings to try in that language's kaikki dump."""
    k = [tok]
    if lang == "ru":
        k.append(tok.replace("́", ""))
    if lang in ("ar", "fa"):
        k.append(re.sub(r"[ً-ٰٟ]", "", tok))
    if lang == "ko":
        k.append(tok.replace(" ", ""))
    if lang in LATIN:
        k += [tok.lower(), tok.replace("-", " "), tok.replace("-", ""), tok.lower().replace("-", "")]
        if lang not in ("vi", "yo", "fr", "es", "tr"):
            k.append(strip_marks(tok).lower())
    if lang == "th":
        k.append(tok.replace(" ", ""))
    out = []
    for x in k:
        if x and x not in out:
            out.append(x)
    return out


def candidates(lang, word):
    """[(token, keys)] in order of appearance. Latin-script languages: 1-3 word n-grams of each
    comma/semicolon/slash segment."""
    out = []
    if lang in SCRIPT:
        for m in re.finditer(SCRIPT[lang], word):
            t = m.group(0).strip()
            if t:
                out.append(t)
        if lang == "ja":  # also each part of a ・-joined or multi-run token
            out += [p for t in list(out) for p in t.split("・") if p and p != t]
    else:
        segs = re.split(r"[,;/()\"“”]|\bbeside\b|\balso\b| < ", word)
        for seg in segs:
            ws = re.findall(r"[^\W\d_](?:[^\W\d_]|[\u0300-\u036f])*(?:[-'’ʼ](?:[^\W\d_]|[\u0300-\u036f])+)*", seg)
            for n in (3, 2, 1):
                for i in range(len(ws) - n + 1):
                    g = ws[i:i + n]
                    if all(x.lower() in SKIP for x in g):
                        continue
                    if n > 1 and any(x.lower() in SKIP for x in g):
                        continue
                    out.append(" ".join(g))
    seen, res = set(), []
    for t in out:
        if t not in seen:
            seen.add(t); res.append((t, keys(lang, t)))
    return res


def latin_tokens(word):
    """Romanisations in a non-Latin cell (for the transliteration fallback)."""
    word = re.sub(r"\(.*?subs.*?\)", "", word)
    word = re.sub(r"\([^)]*[\"“][^)]*\)", "", word)  # parenthesised notes with quoted English glosses
    toks = re.findall(LAT, word)
    out = []
    for t in toks:
        t = " ".join(x for x in t.split() if x.lower() not in SKIP)
        if len(t) > 1:
            out.append(t)
    return out


LAT = r"[A-Za-z\u00c0-\u02af\u1e00-\u1effʼʾʿ'ʹ\u0300-\u036f]+(?:[- ][A-Za-z\u00c0-\u02af\u1e00-\u1effʼʾʿ'ʹ\u0300-\u036f]+)*"


def groups(lang, word):
    """Candidate words of a cell: dicts with keys (kaikki spellings), script (native-script token or None),
    latin (its romanisation, or the Latin-script word itself, or None)."""
    if lang in LATIN or lang not in SCRIPT:
        # notes in parentheses (counts, rivals, etymologies) are skipped unless nothing else is left
        bare = re.sub(r"\([^)]*\)", "", word)
        c = candidates(lang, bare) or candidates(lang, word)
        return [dict(keys=k, script=None, latin=t) for t, k in c]
    clean = re.sub(r"\([^)]*[\"“][^)]*\)", "", word)
    out, used = [], []
    for m in re.finditer(SCRIPT[lang], clean):
        tok = m.group(0).strip()
        rm = re.match(r"\s*\(?\s*(" + LAT + ")", clean[m.end():])
        lat = None
        if rm:
            lat = " ".join(x for x in rm.group(1).split() if x.lower() not in SKIP) or None
            used.append(rm.group(1))
        out.append(dict(keys=keys(lang, tok), script=tok, latin=lat))
        if lang == "ja" and "・" in tok:
            out += [dict(keys=keys(lang, p), script=p, latin=None) for p in tok.split("・") if p]
    for t in latin_tokens(clean):
        if not any(t in u or u in t for u in used):
            out.append(dict(keys=[], script=None, latin=t))
    return out
