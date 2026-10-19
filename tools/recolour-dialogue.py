# Norden UI - Black 1.0.4: the dialogue box.
#
# recolour.py darkens NEUTRAL greys (channel spread <= 3) and leaves every hued accent alone. Norden's dialogue menu
# draws its selected-topic box in Norden's slate - (42,52,57) and (91,103,109), spread 15 and 18 - so the rule never
# reached it and the box kept its original colour in a black setup (a player's report, 2026-10-08; found 2026-10-19).
# This pass runs AFTER recolour.py --build and applies the same darkening, v' = max(0, round((v - 51) * 0.5)) on the
# colour's mean, to the slate colours in the dialogue movies ONLY (dialoguemenu.swf in every Norden patch variant and
# the deardiary_dm\dialoguemenu pieces). Every other menu keeps its slate selection colour, as 1.0.3 shipped it.
# Alpha is never touched; the result is a neutral grey, so the box is black with the same fade as before.
#
#   python recolour-dialogue.py [--build]
# Env (same names as recolour.py): NORDEN_XML_BLACK (default build\xml-black), NORDEN_BLACK (the recoloured tree the
# package is assembled from; default build\full-black here, because the full archive is what ships).
import os, re, sys, subprocess, collections
FF = r"C:\Program Files (x86)\FFDec\ffdec-cli.exe"
HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build")
XML_BLACK = os.environ.get("NORDEN_XML_BLACK", os.path.join(HERE, "full-xml-black"))
OUT = os.environ.get("NORDEN_BLACK", os.path.join(HERE, "full-black"))
attr = re.compile(r'(\w+)="([^"]*)"')
node = re.compile(r'<(\w+) type="(RGBA?)"((?:\s+\w+="[^"]*")+)/>')
stats = collections.Counter()

def darken(v):
    return max(0, round((v - 51) * 0.5))

def is_slate(r, g, b):
    # a dark, faintly hued grey: not neutral (recolour.py has it), not a real accent (the silver 187,189,191 and the
    # debug greens/blues are far above or far from grey)
    return 3 < max(r, g, b) - min(r, g, b) <= 24 and max(r, g, b) <= 110

def fix(m):
    a = dict(attr.findall(m.group(3)))
    r, g, b = int(a["red"]), int(a["green"]), int(a["blue"])
    if not is_slate(r, g, b):
        return m.group(0)
    nv = darken(round((r + g + b) / 3))
    stats[((r, g, b), nv)] += 1
    return re.sub(r'(red|green|blue)="\d+"', lambda mm: f'{mm.group(1)}="{nv}"', m.group(0))

def is_dialogue(rel):
    p = rel.replace("\\", "/").lower()
    return "/interface/" in "/" + p and (os.path.basename(p).startswith("dialoguemenu") or "/deardiary_dm/dialoguemenu/" in p)

jobs = []
for root, _, files in os.walk(XML_BLACK):
    for f in files:
        if not f.endswith(".xml"):
            continue
        src = os.path.join(root, f)
        rel = os.path.relpath(src, XML_BLACK)
        if not is_dialogue(rel):
            continue
        s = open(src, encoding="utf-8").read()
        s2 = node.sub(fix, s)
        if s2 != s:
            open(src, "w", encoding="utf-8", newline="\n").write(s2)
        jobs.append((src, os.path.join(OUT, rel[:-4] + ".swf")))   # every dialogue file is rebuilt, so a rerun is safe
print(f"{len(jobs)} dialogue file(s); slate colours darkened this run: {sum(stats.values())}")
print("mapping used (slate -> grey):", sorted(stats.items()))
if "--build" in sys.argv:
    bad = 0
    for xml, out in jobs:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        r = subprocess.run([FF, "-xml2swf", xml, out], capture_output=True, text=True)
        ok = os.path.exists(out) and os.path.getsize(out) > 0
        print(("built " if ok else "FAIL  ") + out)
        bad += 0 if ok else 1
    sys.exit(1 if bad else 0)
