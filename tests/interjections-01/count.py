"""Panel count for interjection forms: a language counts when its dictionary (kaikki, Wiktionary) lists an
interjection with this function whose pronunciation matches the form's pattern. python3 -I count.py"""
import csv, re, unicodedata
REG = {"Chinese":"EA","Japanese":"EA","Korean":"EA","Vietnamese":"SEA","Thai":"SEA","Indonesian":"SEA","Tagalog":"SEA",
       "Hindi":"SA","Bengali":"SA","Tamil":"SA","Persian":"WA","Arabic":"WA","Turkish":"WA","Russian":"EU","Spanish":"EU",
       "French":"EU","Swahili":"SSA","Hausa":"SSA","Yoruba":"SSA","Quechua":"AM"}
def plain(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c)[0] == "L" or c in " -")
    return s.replace("ʔ","").replace("ˀ","")
TESTS = [  # (function, gloss pattern, form name, pronunciation pattern on romanisation/IPA, whole)
 ("pain", r"\bpain|\bouch|\bhurt", "ai", r"^h?a[iɪjy]"),
 ("surprise", r"surpris|astonish|\bwow\b|amaze|wonder|admir", "wa", r"^[wvbu]?[wvʋ]a+[ɑ]?h?$|^o?a$|^wow$|^wau$"),
 ("surprise", r"surpris|astonish|\bwow\b|amaze|wonder|admir", "o", r"^h?[oɔ]+h?$"),
 ("realise", r"realiz|realis|understanding|\bI see\b|\boh\b|\bah\b", "a/o", r"^h?[aɑäoɔ]+h?$"),
 ("huh", r"\bwhat\?|pardon|didn't hear|repeat|\bhuh\b|\beh\?|surprise|question", "huh", r"^h?[aɑäeɛəɤɯʌ]+[nŋ̃]?h?$"),
 ("quiet", r"silence|\bquiet|\bhush|\bshh|\bsh\b|be still", "sh", r"^[tʈ]?[sʃʂɕɕçcč][sʃhtt]*$|^[sʃʂ][uɯyiw]+[tʔ]?$|^[t]?[sʃʂ]+[tʔ]?$|^ch[iu]t|^cup$|^čup$|^chu|^ṣah"),
 ("disgust", r"disgust|\byuck|\bew\b|revuls|\bgross", "fu", r"^[fpɸ][uyiw]+[fh]?$|^p?f[iy]?ou?$|^t?fou$|^pif$|^fi$"),
 ("disgust", r"disgust|\byuck|\bew\b|revuls|\bgross", "chi", r"^[ct][ʃɕs]?h?[iī]+$|^chī$|^xí$|^ǐi$"),
 ("relief", r"relief|\bphew", "uf", r"^[hp]?[ufɸ]+[uwfhy]*$|^ouf$|^fiou$|^phù$|^ph?u$"),
 ("attention", r"attract.*attention|get.*attention|\bhey\b|calling", "ey/oy", r"^h?[eɛoɔua]?[ij]$|^h?[oɔuea]y$|^h?[eɛ]$|^ê$|^hé$"),
 ("hesitate", r"hesitat|filler|\bum\b|\buh\b|\ber\b", "e/em", r"^h?[eɛəøœɤɯʌ]+m?$|^ə̀əm$|^um$|^hum$|^ɯm$|^[ʌɔ]m$|^ơ$|^ờ$"),
]
rows = list(csv.DictReader(open("intj.tsv"), delimiter="\t"))
out = csv.writer(open("counts.tsv","w"), delimiter="\t"); out.writerow(["function","form","languages","n","regions","witnesses"])
for fn, gp, name, fp in TESTS:
    hit = {}
    for r in rows:
        if "obsolete" in r["tags"] or "archaic" in r["tags"]: continue
        if not re.search(gp, r["gloss"], re.I): continue
        cands = [plain(x) for x in (r["roman"], r["ipa"].strip("/[]"), r["word"]) if x]
        cands = [re.sub(r"[ .ː˧˦˨˩˥ˈ-]", "", c) for c in cands]
        if any(re.search(fp, c) for c in cands):
            hit.setdefault(r["lang"], f'{r["word"]} {r["roman"] or r["ipa"]}')
    regs = sorted({REG[l] for l in hit})
    out.writerow([fn, name, ",".join(hit), len(hit), len(regs), " | ".join(f"{l[:3]}:{w}" for l,w in hit.items())])
    print(f"{fn:9} {name:6} {len(hit):2}/20 {len(regs)} regions  " + " | ".join(f"{l[:3]}:{w}" for l,w in hit.items())[:260])
