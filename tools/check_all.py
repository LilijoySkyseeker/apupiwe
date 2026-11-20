"""Run every check, in order, and print one line per check; exit 1 if any fails (doghouse review rule 5, author
2026-11-19: one command, run by tools/place.py and tools/apply_forms.py after every change they make).

  python3 tools/check_all.py        # -v: also print each failing check's output in full

  spec      tools/spec.py check            docs/language.md matches spec/reference.toml
  lexicon   tools/gf_lexicon.py            the GF lexicon regenerated from data/ (writes grammar/Lex*.gf)
  grammar   tools/gf_check.py              every reference example parses with its intended reading
  accent    tools/accent.py                rule 2.12, the loan-vowel rule, the short-word hard rules
  juncture  tools/juncture.py              word sequences that sound like another word
  words     tools/check.py docs/language.md  no unknown word in the reference
  offensive offensive.blocked is false for every form in data/lexicon.tsv, grammar.tsv, numbers.tsv
"""
import csv, os, subprocess, sys, time

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TOOLS, ".."))
PY = sys.executable
CHECKS = [
    ("spec", [PY, "tools/spec.py", "check"]),
    ("lexicon", [PY, "tools/gf_lexicon.py"]),
    ("grammar", [PY, "tools/gf_check.py"]),
    ("accent", [PY, "tools/accent.py"]),
    ("juncture", [PY, "tools/juncture.py"]),
    ("words", [PY, "tools/check.py", "docs/language.md"]),
]
NOISE = ("Building prefix dict", "Loading model", "Prefix dict has been built", "Dumping model")   # wordfreq's jieba


def last_line(text):
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith(NOISE)]
    return lines[-1].strip() if lines else ""


def offensive_check():
    sys.path.insert(0, TOOLS)
    import offensive
    bad = []
    for name in ("lexicon.tsv", "grammar.tsv", "numbers.tsv"):
        for r in csv.DictReader(open(os.path.join(ROOT, "data", name)), delimiter="\t"):
            if offensive.blocked(r["form"]):
                bad.append(f"{r['form']} ({name})")
    return (1, "blocked: " + ", ".join(bad)) if bad else (0, "no form is blocked")


def main(verbose=False):
    failed = []
    for name, cmd in CHECKS:
        t0 = time.time()
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"{'ok  ' if ok else 'FAIL'} {name:9} {time.time() - t0:5.1f}s  {last_line(r.stdout + r.stderr)[:150]}", flush=True)
        if not ok:
            failed.append(name)
            if verbose:
                print(r.stdout + r.stderr)
    code, msg = offensive_check()
    print(f"{'ok  ' if code == 0 else 'FAIL'} {'offensive':9}         {msg}")
    if code:
        failed.append("offensive")
    print(f"check_all: {'all passed' if not failed else 'FAILED: ' + ' '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main("-v" in sys.argv))
