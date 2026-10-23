# Export every Norden UI SWF to JPEXS XML (swf2xml), 6 at a time, mirroring the Interface tree.
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
# FFDec through its jar with a capped heap: ffdec-cli.exe gives Java a heap the size of the machine's RAM and one
# -swf2xml pass reached 11.7 GB beside a running game (2026-10-23). FFDEC_HEAP overrides the 4g cap.
FF = ["java", "-Xmx" + os.environ.get("FFDEC_HEAP", "4g"), "-jar", r"C:\Program Files (x86)\FFDec\ffdec-cli.jar"]
SRC = os.environ.get("NORDEN_UI", r"D:\modlists\Njordlinger\mods\Norden UI")
OUT = os.environ.get("NORDEN_XML", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "xml"))   # NORDEN_XML: the full-archive build keeps its own XML (2026-09-24)
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
    r = subprocess.run([*FF, "-swf2xml", src, dst], capture_output=True, text=True)
    ok = os.path.exists(dst) and os.path.getsize(dst) > 0
    return (src, "ok" if ok else "FAIL " + (r.stderr or r.stdout)[-300:])
t = time.time()
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(run, jobs))
bad = [r for r in res if not r[1] in ("ok", "cached")]
print(f"{len(jobs)} swfs, {len(bad)} failed, {time.time()-t:.0f}s")
for b in bad: print(b)
