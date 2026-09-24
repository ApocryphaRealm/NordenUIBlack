r"""Install the Norden UI - Black FOMOD into an MO2 mod folder with the SAME choices the player made for Norden UI.

The owner, 2026-09-24: "just install norden black with my options and deactivate the current norden black".
MO2 keeps no record of FOMOD choices (Norden UI's meta.ini has none), so the choices are read back from what is
installed: an option is chosen when the files it places match the player's installed files -

  * where the current Black folder has the destination: the FOMOD's file must equal it byte for byte (Black 1.0.3
    is file-for-file 1.0.2 for the owner's choices);
  * else where the installed Norden UI has it: Norden's ORIGINAL file at the same source path (build\source\main)
    must equal the installed one.

SelectExactlyOne takes the best-matching option (a files-less "skip" option when nothing matches well); SelectAtMostOne
and SelectAny take options that match >= 80% (an add-on replacing files must reproduce them); SelectAll takes
everything; a flag-only question (resolution, Wheeler) takes the answer whose later files reproduce the most of what
is installed. Files are then laid down in the installer's priority order, later overriding earlier, as MO2's
FOMOD installer does.

    python install-with-choices.py <FOMOD folder> <target mod folder> [--dry-run]
"""
import hashlib, os, shutil, sys, configparser
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
FOMOD, TARGET = sys.argv[1], sys.argv[2]
DRY = "--dry-run" in sys.argv
MODS = r"D:\Modlists\Njordlinger\mods"
CUR_BLACK = os.path.join(MODS, "unpublished Norden UI - Black")
NORDEN = os.path.join(MODS, "Norden UI")
ORIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "source", "main")
PREFS = r"D:\Modlists\Njordlinger\profiles\Njordlinger Test\SkyrimPrefs.ini"

_h = {}
def sha(p):
    if p not in _h:
        _h[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return _h[p]

def expand(el):
    """(source file, destination rel, priority) for one <file>/<folder> element."""
    src = el.get("source").replace("/", "\\")
    dst = (el.get("destination") or "").replace("/", "\\")
    pri = int(el.get("priority") or 0)
    full = os.path.join(FOMOD, src)
    if el.tag == "file":
        if el.get("destination") is None:
            dst = os.path.basename(src)
        return [(full, dst, pri)]
    out = []
    for dp, _, fn in os.walk(full):
        for f in fn:
            p = os.path.join(dp, f)
            out.append((p, os.path.join(dst, os.path.relpath(p, full)) if dst else os.path.relpath(p, full), pri))
    return out

def score(entries):
    if not entries:
        return None
    ok = 0
    for src, dst, _ in entries:
        cb, nd = os.path.join(CUR_BLACK, dst), os.path.join(NORDEN, dst)
        if os.path.isfile(cb):
            # present but changed still says the option was chosen - the Automatic DIP Patcher rewrites its descriptor
            ok += 1 if sha(cb) == sha(src) else 0.5
        elif os.path.isfile(nd):
            orig = os.path.join(ORIG, os.path.relpath(src, FOMOD))
            ok += os.path.isfile(orig) and sha(orig) == sha(nd)
    return ok / len(entries)

def plugin_entries(p):
    return [e for el in p.findall("files/*") for e in expand(el)]

def deps_hold(dep, flags):
    if dep is None:
        return True
    op = dep.get("operator", "And")
    res = []
    for d in dep:
        if d.tag == "flagDependency":
            res.append(flags.get(d.get("flag"), "") == (d.get("value") or ""))
        elif d.tag == "dependencies":
            res.append(deps_hold(d, flags))
        else:
            res.append(True)   # file/game/fomm dependencies: not evaluated here
    return all(res) if op == "And" else any(res)

cp = configparser.ConfigParser(strict=False)
cp.read(PREFS, encoding="utf-8")
w, h = float(cp.get("Display", "iSize W", fallback="16")), float(cp.get("Display", "iSize H", fallback="9"))
aspect = "21" if w / h > 2.0 else "16"

root = ET.parse(os.path.join(FOMOD, "fomod", "ModuleConfig.xml")).getroot()


def resolve(force, verbose=False):
    """One pass through the installer. force: {group key: option name} for flag-only exclusive groups."""
    flags, chosen, flagonly = {}, [], []
    for el in root.findall("requiredInstallFiles/*"):
        chosen.extend(expand(el))
    for si, st in enumerate(root.iter("installStep")):
        vis = st.find("visible")
        if vis is not None and not deps_hold(vis.find("dependencies") if vis.find("dependencies") is not None else vis, flags):
            continue
        for gi, g in enumerate(st.iter("group")):
            key = (si, gi)
            gtype, plugs = g.get("type"), g.findall("plugins/plugin")
            scored = [(p, e, score(e)) for p, e in ((p, plugin_entries(p)) for p in plugs)]
            if gtype == "SelectAll":
                pick = scored
            elif all(s is None for _, _, s in scored):
                if gtype == "SelectExactlyOne":
                    flagonly.append((key, [p.get("name") for p in plugs]))
                    want = force.get(key)
                    dflt = next((x for x in scored if x[0].get("name").lstrip("0123456789. ").startswith(aspect)), scored[0])
                    pick = [next((x for x in scored if x[0].get("name") == want), dflt)]
                else:
                    pick = scored   # flag-only SelectAny (e.g. "Proceed"): the flags gate the later steps
            else:
                ranked = sorted([x for x in scored if x[2] is not None], key=lambda x: -x[2])
                skip = next((x for x in scored if x[2] is None), None)
                if gtype == "SelectExactlyOne":
                    # an add-on option replaces files; take it only when it reproduces what is installed
                    pick = [ranked[0]] if skip is None or ranked[0][2] >= 0.8 else [skip]
                elif gtype == "SelectAtMostOne":
                    pick = [ranked[0]] if ranked[0][2] >= 0.8 else []
                else:
                    pick = [x for x in scored if x[2] is None or x[2] >= 0.8]
            if verbose:
                names = {x[0].get("name") for x in pick}
                print(f"[{st.get('name')}] {g.get('name')} ({gtype})")
                for p, e, s in scored:
                    print(f"   [{'x' if p.get('name') in names else ' '}] {p.get('name')}  "
                          + ("" if s is None else f"{s:.0%} of {len(e)} file(s)"))
            for p, e, s in pick:
                chosen.extend(e)
                for f in p.iter("flag"):
                    flags[f.get("name")] = f.text or ""
    cf = root.find("conditionalFileInstalls")
    if cf is not None:
        for pat in cf.findall("patterns/pattern"):
            if deps_hold(pat.find("dependencies"), flags):
                for el in pat.findall("files/*"):
                    chosen.extend(expand(el))
    final = {}
    for i, (src, dst, pri) in sorted(enumerate(chosen), key=lambda t: (t[1][2], t[0])):
        final[dst.lower()] = (src, dst)
    return final, flags, flagonly


def fitness(final):
    """Installed files reproduced, minus current-Black files the install would lose."""
    good = 0
    for src, dst in final.values():
        cb, nd = os.path.join(CUR_BLACK, dst), os.path.join(NORDEN, dst)
        if os.path.isfile(cb):
            good += sha(cb) == sha(src)
        elif os.path.isfile(nd):
            orig = os.path.join(ORIG, os.path.relpath(src, FOMOD))
            good += os.path.isfile(orig) and sha(orig) == sha(nd)
    return good - len(CUR - set(final))


CUR = {os.path.relpath(os.path.join(dp, f), CUR_BLACK).lower() for dp, _, fn in os.walk(CUR_BLACK) for f in fn
       if f.lower() != "meta.ini"}
force = {}
for _ in range(3):   # decide each flag-only question by which answer reproduces more of what is installed
    changed = False
    final, flags, flagonly = resolve(force)
    for key, names in flagonly:
        best = max(names, key=lambda n: fitness(resolve({**force, key: n})[0]))
        if force.get(key) != best:
            force[key], changed = best, True
    if not changed:
        break
final, flags, _ = resolve(force, verbose=True)

print(f"\n{len(final)} file(s) chosen; flags {flags}")

cur = CUR
lost = sorted(cur - set(final))
same = sum(1 for k in cur & set(final) if sha(os.path.join(CUR_BLACK, k)) == sha(final[k][0]))
print(f"against the current Black ({len(cur)} files): {same} identical, {len(cur & set(final)) - same} differ, "
      f"{len(lost)} not in the new install, {len(set(final) - cur)} new")
for k in sorted(k for k in cur & set(final) if sha(os.path.join(CUR_BLACK, k)) != sha(final[k][0])):
    print("   differs:", k, "<-", os.path.relpath(final[k][0], FOMOD))
for k in lost[:30]:
    print("   only in current:", k)
if DRY:
    sys.exit(0)
if os.path.exists(TARGET):
    sys.exit(f"{TARGET} exists - not overwriting")
for src, dst in final.values():
    d = os.path.join(TARGET, dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(src, d)
open(os.path.join(TARGET, "meta.ini"), "w", encoding="utf-8").write(
    "[General]\ngameName=SkyrimSE\nmodid=0\nversion=1.0.3\ninstallationFile=Norden UI - Black 1.0.3 FOMOD.zip\n"
    "comments=installed by tools\\install-with-choices.py with the choices read from the installed Norden UI\n")
print("installed ->", TARGET)
