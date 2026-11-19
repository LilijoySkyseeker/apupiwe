"""Spelling-to-sound rules (broad IPA) for the near-phonemic panel languages, and a rough transliteration
fallback for romanised words in the others. Tones, stress and length are dropped. The rule sets are written
out in DATA.md."""
import re
import unicodedata


def _nfc(s):
    return unicodedata.normalize("NFC", s)


def _strip(s, keep=""):
    """Remove combining marks except those in keep (as composed characters)."""
    out = []
    for ch in unicodedata.normalize("NFC", s):
        if ch in keep:
            out.append(ch); continue
        d = unicodedata.normalize("NFD", ch)
        out.append("".join(c for c in d if not unicodedata.combining(c)))
    return "".join(out)


def _sub(s, table):
    """Greedy left-to-right longest-match substitution."""
    keys = sorted(table, key=len, reverse=True)
    i, out = 0, []
    while i < len(s):
        for k in keys:
            if s.startswith(k, i):
                out.append(table[k]); i += len(k); break
        else:
            out.append(s[i]); i += 1
    return "".join(out)


# --- Spanish (Latin American, seseo and yeísmo); also Quechua words spelled the Spanish way ---------------
def spanish(w):
    w = w.lower().replace("í", "I").replace("ú", "U")
    w = _strip(w, keep="ñü")
    w = re.sub(r"^h|(?<=[^c])h", "", w)
    w = re.sub(r"c(?=[ei])", "s", w)
    w = re.sub(r"g(?=[ei])", "χ", w)
    w = re.sub(r"gu(?=[ei])", "g", w)
    w = re.sub(r"qu(?=[ei])", "k", w)
    w = re.sub(r"^r|rr|(?<=[lns])r", "R", w)
    w = _sub(w, {"ch": "tʃ", "ll": "ʝ", "ñ": "ɲ", "gü": "ɡw", "ü": "w", "zz": "ts", "c": "k", "z": "s", "j": "x", "v": "b",
                 "x": "ks", "χ": "x", "y": "ʝ", "r": "ɾ", "R": "r", "qu": "k", "g": "ɡ"})
    w = re.sub(r"ʝ$", "i", w)
    w = re.sub(r"(?<=[aeo])i(?=[aeiou]|$)|i(?=[aeou])", "j", w)
    w = re.sub(r"u(?=[aeio])|(?<=[aeo])u", "w", w)
    return w.replace("I", "i").replace("U", "u")


# --- Quechua (Southern Quechua orthography) ----------------------------------------------------------------
SPANISH_HINT = re.compile(r"[bdegofvzxáéíóú]|c(?!h)|qu[ei]|rr|gu")


def quechua(w):
    lw = w.lower()
    if SPANISH_HINT.search(lw):
        return spanish(w)
    lw = lw.replace("’", "'").replace("ʼ", "'")
    return _sub(lw, {"chh": "tʃʰ", "ch'": "tʃʼ", "ch": "tʃ", "kh": "kʰ", "k'": "kʼ", "ph": "pʰ", "p'": "pʼ",
                     "th": "tʰ", "t'": "tʼ", "qh": "qʰ", "q'": "qʼ", "ll": "ʎ", "ñ": "ɲ", "sh": "ʃ", "y": "j",
                     "r": "ɾ"})


# --- Indonesian ---------------------------------------------------------------------------------------------
def indonesian(w):
    w = w.lower()
    w = _sub(w, {"ny": "ɲ", "ng": "ŋ", "sy": "ʃ", "kh": "x", "c": "tʃ", "j": "dʒ", "y": "j", "é": "e", "è": "ɛ",
                 "e": "ə", "g": "ɡ"})
    w = re.sub(r"k$", "ʔ", w) if False else w  # final k kept as k (loans)
    return w


# --- Tagalog ------------------------------------------------------------------------------------------------
def tagalog(w):
    if "sh" in w.lower() or "-" in w:
        return foreign(w)
    w = _strip(w.lower(), keep="ñ")
    w = _sub(w, {"ng": "ŋ", "ny": "ɲ", "ñ": "ɲ", "ts": "tʃ", "ch": "tʃ", "sy": "ʃ", "dy": "dʒ", "j": "dʒ",
                 "y": "j", "r": "ɾ", "c": "k", "g": "ɡ", "-": "ʔ"})
    return w


# --- Swahili ------------------------------------------------------------------------------------------------
def swahili(w):
    w = w.lower().replace("’", "'")
    return _sub(w, {"ng'": "ŋ", "ny": "ɲ", "ch": "tʃ", "sh": "ʃ", "th": "θ", "dh": "ð", "gh": "ɣ", "kh": "x",
                    "j": "dʒ", "y": "j", "g": "ɡ"})


# --- Turkish ------------------------------------------------------------------------------------------------
def turkish(w):
    w = w.lower().replace("İ", "i")
    return _sub(w, {"c": "dʒ", "ç": "tʃ", "ş": "ʃ", "ğ": "", "ı": "ɯ", "ö": "ø", "ü": "y", "j": "ʒ", "y": "j",
                    "r": "ɾ", "â": "a", "î": "i", "û": "u", "g": "ɡ"})


# --- Yoruba -------------------------------------------------------------------------------------------------
def yoruba(w):
    w = unicodedata.normalize("NFD", w.lower())
    # under-dot vowels and s; drop tone marks (acute, grave, macron)
    w = re.sub(r"ẹ", "ɛ", w); w = re.sub(r"ọ", "ɔ", w); w = re.sub(r"ṣ", "ʃ", w)
    w = w.replace("ẹ", "ɛ").replace("ọ", "ɔ").replace("ṣ", "ʃ")
    # a tone-marked n not followed by a vowel is the syllabic nasal: keep it as n
    w = re.sub("n[̀́̄](?![aeiouɛɔ])", "N", w)
    w = re.sub("[̀́̄̌̂]", "", w)
    w = _nfc(w)
    w = re.sub(r"([aɛiɔu])n(?![aeɛioɔu])", lambda m: m.group(1) + "̃", w)
    w = w.replace("-", "")
    w = re.sub(r"([aeiouɛɔ])(\u0303?)\1", r"\1\2ː", w)
    w = _sub(w, {"N": "n", "gb": "ɡ͡b", "p": "k͡p", "j": "dʒ", "y": "j", "r": "ɾ", "g": "ɡ"})
    return _nfc(w)


# --- Hausa (Boko) -------------------------------------------------------------------------------------------
def hausa(w):
    w = _strip(w.lower(), keep="ƙɗɓƴ")
    w = w.replace("’", "'")
    return _sub(w, {"'y": "ʔʲ", "ƴ": "ʔʲ", "sh": "ʃ", "ts": "sʼ", "c": "tʃ", "j": "dʒ", "ƙ": "kʼ", "y": "j",
                    "r": "r", "f": "ɸ", "g": "ɡ"})


# --- Vietnamese (Hà Nội), per syllable ----------------------------------------------------------------------
VI_INIT = [("ngh", "ŋ"), ("ng", "ŋ"), ("nh", "ɲ"), ("ch", "tɕ"), ("tr", "tɕ"), ("th", "tʰ"), ("ph", "f"),
           ("kh", "x"), ("gh", "ɣ"), ("gi", "z"), ("qu", "kw"), ("đ", "ɗ"), ("d", "z"), ("r", "z"), ("g", "ɣ"),
           ("x", "s"), ("s", "s"), ("c", "k"), ("k", "k"), ("b", "ɓ"), ("v", "v"), ("l", "l"), ("m", "m"),
           ("n", "n"), ("t", "t"), ("h", "h"), ("p", "p")]
VI_FIN = [("ch", "k"), ("nh", "ɲ"), ("ng", "ŋ"), ("c", "k"), ("p", "p"), ("t", "t"), ("m", "m"), ("n", "n"),
          ("i", "j"), ("y", "j"), ("o", "w"), ("u", "w")]
VI_VOW = [("iê", "iə"), ("yê", "iə"), ("ia", "iə"), ("uô", "uə"), ("ua", "uə"), ("ươ", "ɨə"), ("ưa", "ɨə"),
          ("oa", "wa"), ("oă", "wa"), ("oe", "wɛ"), ("uy", "wi"), ("uê", "we"), ("uơ", "wə"), ("uâ", "wə"),
          ("a", "a"), ("ă", "a"), ("â", "ə"), ("e", "ɛ"), ("ê", "e"), ("i", "i"), ("y", "i"), ("o", "ɔ"),
          ("ô", "o"), ("ơ", "ə"), ("u", "u"), ("ư", "ɨ")]
VI_TONE = "̣̀́̃̉"


def _vi_syl(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if c not in VI_TONE)
    s = _nfc(s)
    ini = ""
    for k, v in VI_INIT:
        if s.startswith(k) and not (k == "gi" and len(s) == 2 and False):
            if k == "gi" and len(s) > 2 and s[2] in "aăâeêoôơuư":
                ini, s = v, s[2:]
            elif k == "gi":
                ini, s = v, s[1:]
            else:
                ini, s = v, s[len(k):]
            break
    fin = ""
    for k, v in VI_FIN:
        if s.endswith(k) and len(s) > len(k):
            fin, s = v, s[:-len(k)]
            break
    nuc = _sub(s, dict(VI_VOW))
    if fin == "k" and nuc in ("i", "e", "ɛ") and False:
        pass
    return ini + nuc + fin


def vietnamese(w):
    syl = re.split(r"[\s\-]+", w.strip())
    if any(re.search(r"[fjwz]", x.lower()) for x in syl) or len(syl) == 1 and len(w) > 5 and not re.search(r"[^\x00-\x7f]", w):
        # an unadapted foreign spelling (pizza, hashtag, profile): read letter by letter
        return foreign(w)
    V = "aeiouyăâêôơưàáảãạèéẻẽẹìíỉĩịòóỏõọùúủũụỳýỷỹỵ"
    out = []
    for x in syl:
        bare = _strip(x.lower())
        if re.search(r"[aeiouy][^aeiouy]+[aeiouy]", bare):
            out.append(foreign(x))  # several syllables written as one (rupi, milimet): read letter by letter
        elif x:
            out.append(_vi_syl(x))
    return " ".join(out)


def foreign(w):
    """A foreign (English/French) spelling in a Latin-script cell: letters read at face value."""
    w = _strip(w.lower())
    w = re.sub(r"e$", "", w) if len(w) > 3 else w
    return _sub(w, {"sh": "ʃ", "ch": "tʃ", "th": "t", "ph": "f", "ck": "k", "zz": "ts", "ee": "i", "oo": "u",
                    "c": "k", "j": "dʒ", "y": "j", "x": "ks", "qu": "kw", "g": "ɡ", "-": ""})


# English spellings that appear as-is in Latin-script cells, with a broad reading as the English word
ENGLISH = {"com": "kom", "hashtag": "haʃtaɡ", "email": "imel", "e-mail": "imel", "mail": "mel",
           "profile": "profail", "rupee": "rupi", "t-shirt": "tiʃirt", "taxi": "taksi", "sandwich": "sanwitʃ",
           "code": "kod", "euro": "juro", "website": "websait", "web": "wep"}

SPELL = dict(es=spanish, qu=quechua, id=indonesian, tl=tagalog, sw=swahili, tr=turkish, yo=yoruba, ha=hausa,
             vi=vietnamese)


def spell(lang, tok):
    f = SPELL.get(lang)
    if not f:
        return ""
    if not re.search(r"[^\W\d_]", tok):
        return ""
    return f(tok)


# --- transliteration fallback (romanisations recorded in the panel) -----------------------------------------
TR_COMMON = {"sh": "ʃ", "ch": "tʃ", "zh": "ʒ", "kh": "x", "gh": "ɣ", "th": "tʰ", "ph": "pʰ", "ng": "ŋ",
             "ny": "ɲ", "š": "ʃ", "ž": "ʒ", "č": "tʃ", "ś": "ʃ", "ṣ": "ʂ", "ṭ": "ʈ", "ḍ": "ɖ", "ṇ": "ɳ", "ṅ": "ŋ",
             "ñ": "ɲ", "ṛ": "ɽ", "ḷ": "ɭ", "ḥ": "ħ", "ʿ": "ʕ", "ʾ": "ʔ", "ʼ": "", "y": "j", "j": "dʒ", "c": "tʃ",
             "â": "ɒ", "ā": "aː", "ŏ": "ɔ", "ĕ": "ɛ", "ṉ": "n", "ṟ": "r", "ḻ": "ɻ", "ġ": "ɣ", "ẓ": "z", "ī": "iː", "ū": "uː", "ē": "eː", "ō": "oː", "ẓ": "ðˤ", "ṯ": "θ", "ḏ": "ð",
             "q": "q", "g": "ɡ", "r": "r", "ɔ": "ɔ", "ʹ": "ʲ", "ı": "ɯ"}
TR_LANG = dict(
    zh={"zh": "ʈʂ", "ch": "ʈʂʰ", "sh": "ʂ", "x": "ɕ", "q": "tɕʰ", "j": "tɕ", "z": "ts", "c": "tsʰ", "r": "ʐ",
        "p": "pʰ", "t": "tʰ", "k": "kʰ", "b": "p", "d": "t", "g": "k", "ü": "y", "ng": "ŋ", "y": "j", "h": "x"},
    ja={"sh": "ɕ", "ch": "tɕ", "j": "dʑ", "ts": "ts", "f": "ɸ", "r": "ɾ", "y": "j", "u": "ɯ", "ū": "ɯː",
        "g": "ɡ"},
    ko={"eo": "ʌ", "eu": "ɯ", "ae": "ɛ", "oe": "we", "ch": "tɕʰ", "j": "tɕ", "k": "kʰ", "t": "tʰ", "p": "pʰ",
        "g": "k", "d": "t", "b": "p", "r": "ɾ", "ng": "ŋ", "y": "j", "ll": "ll"},
    ar={"ṣ": "sˤ", "ṭ": "tˤ", "ḍ": "dˤ", "ẓ": "ðˤ", "x": "x", "e": "e", "o": "o"},
    fa={"ṣ": "s", "ṭ": "t", "ẓ": "z", "x": "x", "â": "ɒ", "ā": "ɒ"},
    th={"kh": "kʰ", "th": "tʰ", "ph": "pʰ", "ch": "tɕʰ", "c": "tɕ", "ng": "ŋ", "ɔ": "ɔ", "ɛ": "ɛ", "ʉ": "ɯ",
        "y": "j"},
    ru={"ʹ": "ʲ", "y": "ɨ", "j": "j", "e": "e", "x": "x", "c": "ts", "č": "tɕ", "š": "ʂ", "ž": "ʐ", "šč": "ɕː"},
    fr={"ou": "u", "oi": "wa", "eau": "o", "au": "o", "ai": "ɛ", "é": "e", "è": "ɛ", "ê": "ɛ", "ch": "ʃ",
        "j": "ʒ", "qu": "k", "c": "k", "r": "ʁ", "u": "y", "gn": "ɲ", "y": "i"},
)


LETTERS = dict(T="tiː", V="viː", C="siː", D="diː", P="piː")


def translit(lang, tok):
    if tok.isupper() and len(tok) <= 3 and all(c in LETTERS for c in tok):
        return " ".join(LETTERS[c] for c in tok)  # an English abbreviation said by its letter names
    t = _nfc(tok.lower())
    if lang == "zh":
        t = _strip(t, keep="ü")
    if lang == "th":  # drop tone marks; doubled vowel letters are long vowels
        t = unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", t)
                                                 if c not in "\u0300\u0301\u0302\u030c"))
        t = re.sub(r"([aeiouɔɛəʉ])\1", r"\1ː", t)
    if lang == "fr":
        t = re.sub(r"(e|s|t|d|x)$", "", _strip(t, keep="éèê"))
    table = dict(TR_COMMON)
    table.update(TR_LANG.get(lang, {}))
    out = _sub(t, table)
    out = re.sub(r"[\s\-]+", " ", out).strip()
    return out


def adapted_ipa(form):
    """Apupiwe spelling to IPA (only used as the comparison target when no median was recorded)."""
    return form.replace("y", "j")


# --- script transliteration (cells with no romanisation and no kaikki entry) --------------------------------
_INDIC_CONS = {0x15: "k", 0x16: "kʰ", 0x17: "ɡ", 0x18: "ɡʱ", 0x19: "ŋ", 0x1A: "tʃ", 0x1B: "tʃʰ", 0x1C: "dʒ",
               0x1D: "dʒʱ", 0x1E: "ɲ", 0x1F: "ʈ", 0x20: "ʈʰ", 0x21: "ɖ", 0x22: "ɖʱ", 0x23: "ɳ", 0x24: "t̪",
               0x25: "t̪ʰ", 0x26: "d̪", 0x27: "d̪ʱ", 0x28: "n", 0x29: "n", 0x2A: "p", 0x2B: "pʰ", 0x2C: "b",
               0x2D: "bʱ", 0x2E: "m", 0x2F: "j", 0x30: "r", 0x31: "r", 0x32: "l", 0x33: "ɭ", 0x34: "ɻ", 0x35: "ʋ",
               0x36: "ʃ", 0x37: "ʂ", 0x38: "s", 0x39: "ɦ"}
_INDIC_VOW = {0x05: "a", 0x06: "aː", 0x07: "i", 0x08: "iː", 0x09: "u", 0x0A: "uː", 0x0B: "ri", 0x0E: "e",
              0x0F: "eː", 0x10: "ɛː", 0x11: "ɔ", 0x12: "o", 0x13: "oː", 0x14: "ɔː"}
_INDIC_MATRA = {0x3E: "aː", 0x3F: "i", 0x40: "iː", 0x41: "u", 0x42: "uː", 0x43: "ri", 0x45: "ɛ", 0x46: "e",
                0x47: "eː", 0x48: "ɛː", 0x49: "ɔ", 0x4A: "o", 0x4B: "oː", 0x4C: "ɔː"}
_INDIC_BASE = dict(hi=0x0900, bn=0x0980, ta=0x0B80)
_INHERENT = dict(hi="ə", bn="ɔ", ta="a")
_NUKTA = {"ज": "z", "फ": "f", "ड": "ɽ", "ढ": "ɽʱ", "क": "q", "ख": "x", "ग": "ɣ", "য": "j", "ড": "ɽ", "ঢ": "ɽʱ"}


def indic(lang, word):
    base = _INDIC_BASE[lang]
    out_words = []
    for w in word.split():
        out, i, chars = [], 0, list(w)
        while i < len(chars):
            ch = chars[i]; o = ord(ch) - base
            nxt = ord(chars[i + 1]) - base if i + 1 < len(chars) else None
            if o in _INDIC_CONS:
                c = _INDIC_CONS[o]
                if nxt == 0x3C:  # nukta
                    c = _NUKTA.get(ch, c); i += 1
                    nxt = ord(chars[i + 1]) - base if i + 1 < len(chars) else None
                if lang == "bn" and o == 0x2C:  # Bengali ব is b
                    c = "b"
                if lang == "bn" and o == 0x2F:
                    c = "dʒ"
                out.append(c)
                if nxt == 0x4D:
                    i += 1
                elif nxt in _INDIC_MATRA:
                    out.append(_INDIC_MATRA[nxt]); i += 1
                else:
                    out.append("@")  # inherent vowel, resolved below
            elif o in _INDIC_VOW:
                out.append(_INDIC_VOW[o])
            elif o in (0x01, 0x02):
                out.append("̃" if o == 0x01 else "n")
            elif ch == "‌" or ch == "-":
                pass
            else:
                out.append(ch)
            i += 1
        if lang == "hi":  # medial schwa deletion: V C @ C V -> V C C V
            V = lambda x: x and (x[0] in "aeiouɛɔə@")
            for k in range(1, len(out) - 2):
                if out[k] == "@" and not V(out[k - 1]) and k >= 2 and V(out[k - 2]) and not V(out[k + 1]) \
                        and k + 2 < len(out) and V(out[k + 2]) and out[k + 2] != "@":
                    out[k] = ""
        s = "".join(out)
        if lang == "bn":
            s = s.replace("ː", "")
        if lang in ("hi", "bn"):
            s = re.sub(r"@$", "", s)  # final inherent vowel dropped
        s = s.replace("@", _INHERENT[lang])
        out_words.append(s)
    return " ".join(out_words)


_KANA = {}
for row in ("a i u e o|ka ki ku ke ko|sa shi su se so|ta chi tsu te to|na ni nu ne no|ha hi fu he ho|"
            "ma mi mu me mo|ya - yu - yo|ra ri ru re ro|wa - - - wo|ga gi gu ge go|za ji zu ze zo|"
            "da ji zu de do|ba bi bu be bo|pa pi pu pe po").split("|"):
    pass
_KATA = ("ア:a イ:i ウ:u エ:e オ:o カ:ka キ:ki ク:ku ケ:ke コ:ko サ:sa シ:shi ス:su セ:se ソ:so タ:ta チ:chi ツ:tsu "
         "テ:te ト:to ナ:na ニ:ni ヌ:nu ネ:ne ノ:no ハ:ha ヒ:hi フ:fu ヘ:he ホ:ho マ:ma ミ:mi ム:mu メ:me モ:mo "
         "ヤ:ya ユ:yu ヨ:yo ラ:ra リ:ri ル:ru レ:re ロ:ro ワ:wa ヲ:o ン:N ガ:ga ギ:gi グ:gu ゲ:ge ゴ:go ザ:za ジ:ji "
         "ズ:zu ゼ:ze ゾ:zo ダ:da ヂ:ji ヅ:zu デ:de ド:do バ:ba ビ:bi ブ:bu ベ:be ボ:bo パ:pa ピ:pi プ:pu ペ:pe ポ:po "
         "ヴ:vu ァ:~a ィ:~i ゥ:~u ェ:~e ォ:~o ャ:~ya ュ:~yu ョ:~yo ッ:Q ー:-")
KATA = dict(x.split(":") for x in _KATA.split())


def kana(word):
    s = ""
    for ch in word:
        if "ぁ" <= ch <= "ゖ":
            ch = chr(ord(ch) + 0x60)
        r = KATA.get(ch)
        if r is None:
            s += ch if ch.isascii() else ""
            continue
        if r.startswith("~"):
            v = r[1:]
            if v.startswith("y"):  # small ya/yu/yo: palatalise
                if s.endswith("shi") or s.endswith("chi") or s.endswith("ji"):
                    s = s[:-1] + v[1:]
                else:
                    s = s[:-1] + v
            else:
                s = s[:-1] + v  # ティ ti, ファ fa
            continue
        s += r
    s = re.sub(r"Q(.)", r"\1\1", s).replace("Q", "")
    s = re.sub(r"(.)-", r"\1ː", s)
    s = s.replace("N", "n")
    return _sub(s, {"ssh": "ɕɕ", "tch": "ttɕ", "sh": "ɕ", "ch": "tɕ", "ts": "ts", "j": "dʑ", "f": "ɸ", "r": "ɾ", "y": "j", "u": "ɯ",
                    "g": "ɡ"})


_AR = {"ا": "aː", "أ": "ʔa", "إ": "ʔi", "آ": "ʔaː", "ب": "b", "ت": "t", "ث": "θ", "ج": "dʒ", "ح": "ħ", "خ": "x",
       "د": "d", "ذ": "ð", "ر": "r", "ز": "z", "س": "s", "ش": "ʃ", "ص": "sˤ", "ض": "dˤ", "ط": "tˤ", "ظ": "ðˤ",
       "ع": "ʕ", "غ": "ɣ", "ف": "f", "ق": "q", "ك": "k", "ک": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h",
       "ة": "a", "و": "w", "ي": "j", "ی": "j", "ى": "aː", "ء": "ʔ", "پ": "p", "چ": "tʃ", "ژ": "ʒ", "گ": "ɡ",
       "ڤ": "v"}
_HARAKA = {"َ": "a", "ِ": "i", "ُ": "u", "ْ": "", "ّ": ":"}


def arabic(lang, word):
    out = []
    chars = [c for c in word if c != "‌"]
    for i, ch in enumerate(chars):
        if ch in _HARAKA:
            h = _HARAKA[ch]
            if h == ":" and out:
                if out[-1] in ("a", "i", "u") and len(out) > 1:
                    out.insert(len(out) - 1, out[-2])
                else:
                    out.append(out[-1])
            else:
                out.append(h)
            continue
        if ch == " ":
            out.append(" "); continue
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        prev = out[-1] if out else ""
        v = _AR.get(ch, "")
        if prev == "i" and ch in "يی" and nxt not in _HARAKA:
            out.append("ː"); continue
        if prev == "u" and ch == "و" and nxt not in _HARAKA:
            out.append("ː"); continue
        # unvowelled ي/و between consonants or final: long vowel
        if ch in "يی" and nxt not in _HARAKA and prev not in ("", " ", "a", "aː"):
            v = "iː" if lang == "ar" else "i"
        elif ch == "و" and nxt not in _HARAKA and prev not in ("", " ", "a", "aː"):
            v = "uː" if lang == "ar" else "u"
        elif ch == "ا" and lang == "fa":
            v = "ɒ"
        out.append(v)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def script(lang, word):
    if lang in _INDIC_BASE:
        return indic(lang, word)
    if lang == "ja":
        return kana(word)
    if lang in ("ar", "fa"):
        return arabic(lang, word)
    if lang == "ko":
        return hangul(word)
    return ""


_KO_I = "k kk n t tt ɾ m p pp s ss - tɕ tɕɕ tɕʰ kʰ tʰ pʰ h".split()
_KO_V = "a ɛ ja jɛ ʌ e jʌ je o wa wɛ we jo u wʌ we wi ju ɯ ɰi i".split()
_KO_F = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l", "p", "l", "m", "p", "p", "t", "t",
         "ŋ", "t", "t", "k", "t", "p", "t"]


def hangul(word):
    out = []
    for ch in word:
        o = ord(ch) - 0xAC00
        if not 0 <= o < 11172:
            out.append(" " if ch == " " else "")
            continue
        i, v, f = o // 588, (o % 588) // 28, o % 28
        ini = _KO_I[i].replace("-", "")
        if ini == "ɾ" and out and out[-1].endswith("l"):
            ini = "l"
        out.append(ini + _KO_V[v] + _KO_F[f])
    s = "".join(out)
    s = s.replace("lɾ", "ll")
    return s
