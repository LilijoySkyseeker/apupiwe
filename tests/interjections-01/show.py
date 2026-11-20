import csv,re,sys,collections
F={"pain":r"\bpain|\bouch|\bhurt","surprise":r"surpris|astonish|\bwow\b|amaze","disgust":r"disgust|\byuck|\bew\b|revuls","realise":r"realiz|realis|understanding|\bI see\b","hesitate":r"hesitat|filler|\bum\b|\buh\b|\ber\b","attention":r"attract.*attention|get.*attention|\bhey\b","quiet":r"silence|\bquiet|\bhush|\bshh|\bsh\b","oops":r"\boops|mistake|clumsy|blunder","relief":r"relief|\bphew","huh":r"\bwhat\?|pardon|didn't hear|repeat|\bhuh\b","pity":r"pity|sympath|\balas","annoy":r"annoy|frustrat|impatien|exasperat","warn":r"warn|watch out|look out","encourage":r"encourag|come on|\bcheer","agree":r"\bokay\b|\bOK\b|agreement|assent","repair":r"I mean|that is to say|rather|correct.*(self|mistake)|or rather|in other words|namely"}
rows=list(csv.DictReader(open('intj.tsv'),delimiter='\t'))
for k in sys.argv[1:]:
    print("==",k); d=collections.defaultdict(dict)
    for r in rows:
        if re.search(F[k],r['gloss'],re.I) and 'obsolete' not in r['tags'] and 'archaic' not in r['tags']:
            d[r['lang']].setdefault(r['word'],(r['roman'] or r['ipa'])[:18])
    for L,w in d.items():
        ws=sorted(w.items(),key=lambda x:len(x[0]))[:5]
        print(f"  {L[:6]:6} "+" | ".join(f"{a} {b}" for a,b in ws))
