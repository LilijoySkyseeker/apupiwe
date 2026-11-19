import csv, os, sys
base = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/"
YY = """mipen- sanyi manse denwo wonni ninta bumun dadon telun yukin bipi sungun miman fotin sunma sunki tinwan wenyo koson fofun owon fukon soyin kenfi teyi lilen enpin kenken pando yinmi menmen bonbun gonkan somi gonwu sunse nonlen munkan lanfon kodipi genogi kugula fiwun papayo lesin watesi lenlun kenwon wunde wukuto tonfe fisusa fimofa nakiyi etasu sunga bukili mosen tanlin fatike gamuni ninfen kawiwu kisodu tadota kogeka yonaki posaga yawalo tipoku tuyesu meko wamu kunyun polin tunen ninlin londu ganton yinnen liwaka kitimo funeta tuyali fogasi tuleki pabito fiyuwi gekidu likusi wigoso leluna siloya dasosi leyoyi sifada neyafu losoma mogufi putaki puwoko bufefa beyasa bayiga panuya miyoga yuseme liweli tasumo yutote yowise tenume lisaku yadidi nutuba gunago engan yilale yufeyu nugaya osayi gakabe mekega losidu bapuma yinifu witowa siman
lose wenki daka wife wonfi nusun yetun wondon nafo pinki ginsan wenfun tinpa bonpen kunnin kadan mankan munyin siwase nunini diwusa lennan bangun yonme tito fatofu miwin wuyume usigi gobewo dupo yunye yumi wisiwe sangan yuntun neyilo wenma kadeso lolefe sosiwu kinmu foya goyon nenda dogen gugife yukesa tilote sisuma negawi sowimo
kunnon nayuso sidako kaname femete"""
YN = """mipen dusu sunye yonta sansan yanwi mobon panpon sanmun yinpon fafuyi fuseno manwu memabi abuki wilopi yonsu manyin lunwin dayele fomefi gumewe yufule yadaka yeyoto
yeyan wudan kude epise lemifi sowiso bunwan umide"""
NOTES = {
 "kenta": "field action, but the gloss is the basin; sink (go under) is gumewe",
 "yukin": "cover: also the lid (thing)",
 "owon": "birth: event (give birth to X) or the thing?",
 "kodipi": "offering: the thing given, or the act (offer up X)?",
 "fiwun": "care: object or tun (care for X)?",
 "sanmun": "vote: 'vote for X' may take an object",
 "somi": "escape: object = what is escaped? also intransitive",
 "sunse": "continue: also intransitive (it continues)",
 "wukuto": "fail: object = what failed (fail to X, fail a test); also intransitive",
 "fuseno": "protest: 'protest X' may take an object",
 "sunga": "spread: also intransitive (it spreads)",
 "lilen": "increase: also intransitive (it increases)",
 "fogasi": "decrease: also intransitive (become less)",
 "gamuni": "improve: also intransitive (it improves)",
 "ninfen": "settle: object (settle a dispute) or intransitive (settle down)?",
 "yonaki": "withdraw: object (withdraw money) or intransitive (pull back)?",
 "manyin": "explode: transitive use (explode a bomb) possible",
 "yeyoto": "freeze: transitive use (freeze food) possible",
 "bayiga": "roll: also intransitive (it rolls)",
 "losidu": "bend: also intransitive (it bends)",
 "yinifu": "stretch: also intransitive",
 "witowa": "hang: also intransitive (it hangs)",
 "pabito": "heal: also intransitive (the wound heals)",
 "fiyuwi": "fraud: the act (cheat someone) or the thing?",
 "leluna": "revenge: the act (avenge X) or the thing?",
 "likusi": "substitute: also the replacement (thing)",
 "menmen": "pray, worship: object = who is worshipped?",
 "lunwin": "fish: 'fish X' unusual; tiso is the animal",
 "nusun": "experience: event (experience X) or the thing?",
 "lose": "plan: event (plan to X) or the thing?",
 "nafo": "record: event (record X) or the recording?",
 "wudan": "comment: 'comment on X' may take an object",
 "tito": "worry: object = what is worried about?",
 "gobewo": "shock: action (shock someone) or the feeling?",
 "yuntun": "excuse: action (excuse someone) or the thing (a pretext)?",
 "kadeso": "register: also intransitive (enrol)",
 "bunwan": "joke: event (to joke) or the thing?",
 "gesi": "question: thing; asking is mido",
 "fendu": "shame: feeling, like fupu; 'shame someone' possible",
 "somasu": "argument: thing; event or thing?",
 "kunnon": "judge: the person or the act (judge X)?",
 "kaname": "divorce: event (divorce X) or the thing?",
 "sidako": "rape: event or the thing?",
 "femete": "infect: object = who is infected; also the infection",
 "nayuso": "depend: object = what it depends on",
 "minmon": "exercise: thing; 'to exercise' possible",
 "kenfan": "wave: thing; 'wave a hand' possible",
 "tutoyi": "strike: thing; 'to strike' possible",
 "lenbo": "trade: thing; exchange is lenlun",
 "gememi": "itch: like fupu; event or thing?",
}
yy = set(w.rstrip('-') for w in YY.split() if not w.endswith('-'))
yn = set(YN.split())
assert not yy & yn, yy & yn
rows = list(csv.DictReader(open(base+"roles-todo.tsv"), delimiter="\t"))
forms = {r["form"] for r in rows}
assert (yy|yn|set(NOTES)) <= forms, (yy|yn|set(NOTES)) - forms
tmp = base+"roles-new.tsv.tmp"
with open(tmp, "w") as f:
    f.write("form\taction\ttakes_object\tnote\n")
    for r in rows:
        fm = r["form"]
        a, o = ("yes","yes") if fm in yy else ("yes","no") if fm in yn else ("no","no")
        f.write(f"{fm}\t{a}\t{o}\t{NOTES.get(fm,'')}\n")
os.replace(tmp, base+"roles-new.tsv")
