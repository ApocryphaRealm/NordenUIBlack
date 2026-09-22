# Export every Norden UI SWF to JPEXS XML (swf2xml), 6 at a time, mirroring the Interface tree.
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
FF = r"C:\Program Files (x86)\FFDec\ffdec-cli.exe"
SRC = os.environ.get("NORDEN_UI", r"D:\modlists\Njordlinger\mods\Norden UI")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "xml")
jobs = []
for root, _, files in os.walk(SRC):
    for f in files:
        if f.lower().endswith(".swf"):
            src = os.path.join(root, f); rel = os.path.relpath(src, SRC)
            dst = os.path.join(OUT, rel[:-4] + ".xml"); jobs.append((src, dst))
def run(j):
    src, dst = j
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return (src, "cached")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    r = subprocess.run([FF, "-swf2xml", src, dst], capture_output=True, text=True)
    ok = os.path.exists(dst) and os.path.getsize(dst) > 0
    return (src, "ok" if ok else "FAIL " + (r.stderr or r.stdout)[-300:])
t = time.time()
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(run, jobs))
bad = [r for r in res if not r[1] in ("ok", "cached")]
print(f"{len(jobs)} swfs, {len(bad)} failed, {time.time()-t:.0f}s")
for b in bad: print(b)
