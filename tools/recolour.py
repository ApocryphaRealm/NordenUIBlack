# Norden UI -> black. Every neutral or near-neutral grey (channel spread <= 3) at or below 102 in any colour node (fills, gradients, lines,
# text, backgrounds) is darkened: v' = max(0, round((v - 51) * 0.5)). Norden's panel grey 51 becomes pure
# black; its secondary greys keep half their offset above the panel (102 -> 26, 88 -> 19, 64 -> 7) so headers
# and hover states stay distinguishable. Alpha is never touched, so opacity / fade levels are unchanged.
import os, re, subprocess, sys, time, collections
from concurrent.futures import ThreadPoolExecutor
FF = r"C:\Program Files (x86)\FFDec\ffdec-cli.exe"
HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build")
SRC_XML = os.path.join(HERE, "xml"); DST_XML = os.path.join(HERE, "xml-black")
MOD = os.environ.get("NORDEN_BLACK", r"D:\modlists\Njordlinger\mods\unpublished Norden UI - Black")
attr = re.compile(r'(\w+)="([^"]*)"')
node = re.compile(r'<(\w+) type="(RGBA?)"((?:\s+\w+="[^"]*")+)/>')
stats = collections.Counter()
def darken(v): return max(0, round((v - 51) * 0.5))
def fix(m):
    a = dict(attr.findall(m.group(3)))
    r, g, b = int(a["red"]), int(a["green"]), int(a["blue"])
    if not (max(r, g, b) - min(r, g, b) <= 3 and max(r, g, b) <= 102): return m.group(0)
    nv = darken(round((r + g + b) / 3)); stats[(r, nv)] += 1
    s = m.group(0)
    return re.sub(r'(red|green|blue)="\d+"', lambda mm: f'{mm.group(1)}="{nv}"', s)
jobs = []
for root, _, files in os.walk(SRC_XML):
    for f in files:
        if not f.endswith(".xml"): continue
        src = os.path.join(root, f); rel = os.path.relpath(src, SRC_XML)
        dst = os.path.join(DST_XML, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
        s = open(src, encoding="utf-8").read(); s2 = node.sub(fix, s)
        open(dst, "w", encoding="utf-8", newline="\n").write(s2)
        jobs.append((dst, os.path.join(MOD, rel[:-4] + ".swf"), s != s2))
changed = [j for j in jobs if j[2]]
print(f"{len(jobs)} files, {len(changed)} with a grey to darken")
print("mapping used:", sorted(stats.items()))
def build(j):
    dst, out, _ = j
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run([FF, "-xml2swf", dst, out], capture_output=True, text=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 0) else "FAIL " + dst + (r.stderr or r.stdout)[-200:]
if "--build" in sys.argv:
    t = time.time()
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(build, changed))
    bad = [r for r in res if r.startswith("FAIL")]
    print(f"built {len(res)-len(bad)} swfs, {len(bad)} failed, {time.time()-t:.0f}s"); [print(b) for b in bad]
