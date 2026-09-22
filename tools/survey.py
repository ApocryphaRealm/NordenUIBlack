import os, re, collections
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "xml")
rgb = collections.Counter(); files_per = collections.defaultdict(set); ctx = collections.Counter()
pat = re.compile(r'<(\w+) type="(RGBA?)"((?:\s+\w+="[^"]*")+)/>')
attr = re.compile(r'(\w+)="([^"]*)"')
bg = collections.Counter()
for root, _, files in os.walk(OUT):
    for f in files:
        p = os.path.join(root, f); s = open(p, encoding="utf-8", errors="replace").read()
        for m in pat.finditer(s):
            a = dict(attr.findall(m.group(3)))
            key = (int(a.get("red",0)), int(a.get("green",0)), int(a.get("blue",0)))
            rgb[key] += 1; files_per[key].add(os.path.relpath(p, OUT)); ctx[(m.group(1), key)] += 1
            if m.group(1) == "backgroundColor": bg[key] += 1
print("distinct colours:", len(rgb))
print("neutral greys (r=g=b), by count:")
for k, c in sorted(rgb.items(), key=lambda x: -x[1]):
    if k[0]==k[1]==k[2]: print(f"  {k}  x{c:6d}  in {len(files_per[k]):3d} files")
print("top non-neutral:")
for k, c in sorted(rgb.items(), key=lambda x: -x[1]):
    if not k[0]==k[1]==k[2] and c > 200: print(f"  {k}  x{c:6d}  in {len(files_per[k]):3d} files")
print("background colours:", bg.most_common(8))
print("node names:", collections.Counter(n for n,_ in ctx.elements()).most_common(10))
