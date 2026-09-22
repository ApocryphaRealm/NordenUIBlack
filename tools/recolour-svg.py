r"""Norden UI's Wheeler art -> Norden UI - Black (the owner, 2026-09-20: "recolor the norden wheeler art for norden black").

Same rule as recolour.py applies to the SWFs, applied to the SVG colour attributes (fill, stroke, stop-color, and the
same names inside style="..."): every neutral grey (channel spread <= 3) at or below 102 is darkened with
v' = max(0, round((v - 51) * 0.5)). Hued colours - Norden's steel blue-greys (#5b676d, #76858d), the icon tints - are
left exactly as they are, as they were in the SWF pass. Alpha / opacity attributes are never touched.

Source: D:\modlists\Njordlinger\mods\Norden UI\SKSE\Plugins\wheeler\ (Norden's own files, the only art this recolour owns)
Output: the SAME relative path inside Norden UI - Black (MO2) and the NordenUIBlack repo; only files that changed are written.
Read-back: after writing, every output file is re-read and checked - a neutral <= 102 left in it fails the run (the
swf-colour-gate lesson: prove the effect on the shipped file, not the script).

    python recolour-svg.py            report what would change
    python recolour-svg.py --write    write the changed files and read them back
"""
import os, re, sys, collections, shutil

SRC = os.path.join(os.environ.get("NORDEN_UI", r"D:\modlists\Njordlinger\mods\Norden UI"), "SKSE", "Plugins", "wheeler")
DSTS = [os.path.join(os.environ.get("NORDEN_BLACK", r"D:\modlists\Njordlinger\mods\unpublished Norden UI - Black"), "SKSE", "Plugins", "wheeler")]
HEX = re.compile(r'(?P<key>\b(?:fill|stroke|stop-color|flood-color|lighting-color)\s*[:=]\s*"?)(?P<hex>#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})(?![0-9a-fA-F])')

def parse(h):
    h = h[1:]
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def neutral_low(rgb):
    return max(rgb) - min(rgb) <= 3 and max(rgb) <= 102

def darken(v):
    return max(0, round((v - 51) * 0.5))

stats = collections.Counter()

def fix(m):
    rgb = parse(m.group("hex"))
    if not neutral_low(rgb):
        return m.group(0)
    nv = darken(round(sum(rgb) / 3))
    stats[(m.group("hex").lower(), "#%02x%02x%02x" % (nv, nv, nv))] += 1
    return m.group("key") + "#%02x%02x%02x" % (nv, nv, nv)

changed = []
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.lower().endswith(".svg"):
            continue
        p = os.path.join(root, f)
        s = open(p, encoding="utf-8", errors="replace").read()
        s2 = HEX.sub(fix, s)
        if s2 != s:
            changed.append((os.path.relpath(p, SRC), s2))

print(f"{len(changed)} svg(s) carry a grey to darken:")
for rel, _ in changed:
    print("  ", rel)
print("mapping used:", sorted(stats.items()))

if "--write" in sys.argv:
    bad = []
    for rel, s2 in changed:
        for d in DSTS:
            out = os.path.join(d, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8", newline="\n").write(s2)
            back = open(out, encoding="utf-8").read()
            # a source grey that the rule maps to another value must not survive in the shipped file
            forbidden = {src for (src, dst) in stats if src != dst}
            left = [m.group("hex") for m in HEX.finditer(back) if m.group("hex").lower() in forbidden]
            if left:
                bad.append((out, left))
    if bad:
        for out, left in bad:
            print("FAIL still grey:", out, left)
        sys.exit(1)
    print(f"wrote {len(changed)} file(s) to each of {len(DSTS)} destination(s); read-back clean")
