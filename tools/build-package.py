#!/usr/bin/env python3
r"""Assemble "Norden UI - Black": Norden UI with its panel grey taken to black, as a mod that sits above Norden UI.

WHAT THIS PACKAGES
    1. The recoloured Norden UI files that recolour.py / recolour-svg.py wrote into the built mod folder
       (NORDEN_BLACK): every Norden SWF with a panel grey in it, Norden's Wheeler SVGs, its moreHUD presets.
    2. Three menus whose art is NOT a loose Norden file. Norden restyles them at run time through the Dynamic
       Interface Patcher; here the patcher's xdelta is applied OFFLINE to the original file and the finished SWF is
       shipped, so a player needs neither DIP nor the Automatic DIP Patcher:
         Interface\racesex_menu.swf              RaceMenu.bsa's race menu      (dip-patches\Norden Black RaceMenu DIP)
         Interface\racemenu\bottombar.swf        RaceMenu.bsa's bottom bar     (same)
         Interface\CharacterProgressionControl\levelupmenu.swf   Character Progression Control's level-up screen
                                                                               (dip-patches\Norden CPC LevelUp DIP)
    The deltas and their DIP .json descriptors are build inputs; none of them is shipped.

WHY THE REPOSITORY HOLDS NO ART
    Norden UI (Nexus 166086, by Nithog) allows modification and release on Nexus with credit, and forbids uploading
    to other sites. So the art - Norden's own and the recoloured copies, and the deltas, which carry it - stays out
    of git (.gitignore); this script reads the built mod folder and the original mods at build time.

WHAT IT REFUSES TO DO
    * ship a DIP delta, a DIP .json, a .prev backup or an MO2 meta.ini;
    * ship a recoloured file that is byte-identical to Norden UI's own (the silent no-op recolour);
    * ship a DIP output that is byte-identical to the file it patches, or one xdelta could not build (a source
      that changed since the delta was made - RaceMenu or CPC updated);
    * ship a SWF that still carries a Norden panel grey (neutral 41-102), read back from the packaged file with
      swf-colour-gate.py --band 41,102, when that gate is available.

Usage:  python tools/build-package.py [output folder]
        Default output is "<repo>/../../7. current test builds/Norden UI - Black <ver>".
Env overrides: NORDEN_BLACK, NORDEN_UI, NORDEN_UI_DIP, RACEMENU_BSA, CPC_MOD, BSARCH, XDELTA, SWF_COLOUR_GATE.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
MODS = r"D:\modlists\Njordlinger\mods"

BUILT = os.environ.get("NORDEN_BLACK", os.path.join(MODS, "unpublished Norden UI - Black"))
NORDEN = os.environ.get("NORDEN_UI", os.path.join(MODS, "Norden UI"))
# Norden UI's second download on the same page (its RaceMenu DIP patch and loose Interface/racemenu/buttonart.swf)
NORDEN_DIP = os.environ.get("NORDEN_UI_DIP", os.path.join(MODS, "Norden UI DIP Patch"))
RACEMENU_BSA = os.environ.get("RACEMENU_BSA", os.path.join(MODS, "RaceMenu", "RaceMenu.bsa"))
CPC_MOD = os.environ.get("CPC_MOD", os.path.join(MODS, "Character Progression Control"))
BSARCH = os.environ.get("BSARCH", r"D:\modlists\Njordlinger\tools\BSArch\BSArch.exe")
XDELTA = os.environ.get("XDELTA", os.path.join(MODS, "Dynamic Interface Patcher - DIP", "DIP", "xdelta", "xdelta.exe"))
GATE = os.environ.get("SWF_COLOUR_GATE", r"D:\Claude output\.MD\scripts\swf-colour-gate.py")
PATCHES = os.path.join(REPO, "dip-patches")

# (shipped path, where the original comes from, delta)
DIP_OUTPUTS = [
    (r"Interface\racesex_menu.swf", ("bsa", r"interface\racesex_menu.swf"),
     r"Norden Black RaceMenu DIP\Patch\RaceMenu.bsa\interface\racesex_menu.bin"),
    (r"Interface\racemenu\bottombar.swf", ("bsa", r"interface\racemenu\bottombar.swf"),
     r"Norden Black RaceMenu DIP\Patch\RaceMenu.bsa\interface\racemenu\bottombar.bin"),
    (r"Interface\CharacterProgressionControl\levelupmenu.swf",
     ("loose", os.path.join(CPC_MOD, r"Interface\CharacterProgressionControl\levelupmenu.swf")),
     r"Norden CPC LevelUp DIP\Patch\interface\CharacterProgressionControl\levelupmenu.bin"),
]
NEVER_SHIP_DIRS = ("norden black racemenu dip", "norden cpc levelup dip", os.path.join("skse", "plugins", "automaticpatcher"))
NEVER_SHIP_EXT = (".bin", ".prev", ".bak")
DOCS = ("LICENSE", "NOTICE.md")


def fail(msg):
    raise SystemExit("build-package: FAIL  " + msg)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def version():
    v = open(os.path.join(REPO, "VERSION"), encoding="utf-8-sig").read().strip()
    if not v.count(".") == 2:
        fail("VERSION does not hold X.Y.Z: %r" % v)
    return v


def shipped(rel):
    low = rel.lower()
    if low == "meta.ini" or low.endswith(NEVER_SHIP_EXT):
        return False
    return not any(low.startswith(d + os.sep) for d in NEVER_SHIP_DIRS)


def main(argv):
    ver = version()
    out = argv[0] if argv else os.path.join(REPO, "..", "..", "7. current test builds", "Norden UI - Black " + ver)
    out = os.path.normpath(out)
    for p, what in ((BUILT, "the built mod folder"), (NORDEN, "Norden UI"), (NORDEN_DIP, "Norden UI DIP Patch"), (RACEMENU_BSA, "RaceMenu.bsa"),
                    (CPC_MOD, "Character Progression Control"), (BSARCH, "BSArch"), (XDELTA, "xdelta")):
        if not os.path.exists(p):
            fail("%s not found: %s" % (what, p))
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    # 1. the recoloured Norden files
    copied, identical, ours = 0, [], []
    for root, _, names in os.walk(BUILT):
        for n in names:
            src = os.path.join(root, n)
            rel = os.path.relpath(src, BUILT)
            if not shipped(rel):
                continue
            orig = next((o for o in (os.path.join(NORDEN, rel), os.path.join(NORDEN_DIP, rel)) if os.path.exists(o)), None)
            if orig:
                if sha(orig) == sha(src):
                    identical.append(rel)
            elif not any(rel.lower() == d[0].lower() for d in DIP_OUTPUTS):
                ours.append(rel)
            dst = os.path.join(out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    if identical:
        fail("%d file(s) are byte-identical to Norden UI's own - the recolour changed nothing: %s"
             % (len(identical), identical[:5]))
    if ours:
        fail("file(s) that are neither Norden UI's nor a DIP output - this package ships Norden's art only: %s" % ours[:5])

    # 2. the DIP outputs, built offline
    tmp = tempfile.mkdtemp(prefix="nub-")
    bsa_dir = os.path.join(tmp, "bsa")
    os.makedirs(bsa_dir)
    r = subprocess.run([BSARCH, "unpack", RACEMENU_BSA, bsa_dir], capture_output=True, text=True)
    if r.returncode != 0:
        fail("BSArch could not unpack RaceMenu.bsa: " + (r.stderr or r.stdout)[-300:])
    for rel, (kind, where), delta in DIP_OUTPUTS:
        orig = os.path.join(bsa_dir, where) if kind == "bsa" else where
        delta = os.path.join(PATCHES, delta)
        if not os.path.exists(orig):
            fail("original for %s not found: %s" % (rel, orig))
        if not os.path.exists(delta):
            fail("delta for %s not found: %s" % (rel, delta))
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        r = subprocess.run([XDELTA, "-d", "-f", "-s", orig, delta, dst], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(dst):
            fail("xdelta could not build %s - has its source mod changed since the delta was made? %s"
                 % (rel, (r.stderr or r.stdout)[-300:]))
        if sha(dst) == sha(orig):
            fail("%s came out identical to the file it patches" % rel)
        print("build-package: built  %-56s %s" % (rel, sha(dst)[:16]))
    shutil.rmtree(tmp, ignore_errors=True)

    # 3. documents
    for d in DOCS:
        shutil.copy2(os.path.join(REPO, d), os.path.join(out, d))
    readme = open(os.path.join(REPO, "dist", "README.txt"), encoding="utf-8").read()
    if ("Version " + ver) not in readme:
        fail("dist\\README.txt does not name version %s" % ver)
    open(os.path.join(out, "README.txt"), "w", encoding="utf-8", newline="\r\n").write(readme)

    # 4. nothing that must not ship, and the colour read back from the package itself
    for root, _, names in os.walk(out):
        for n in names:
            rel = os.path.relpath(os.path.join(root, n), out)
            if rel in DOCS + ("README.txt",):
                continue
            if not shipped(rel) or n.lower().endswith(".json") and "automaticpatcher" in rel.lower():
                fail("package carries a build input: " + rel)
    if os.path.exists(GATE):
        dirs = [os.path.join(out, d) for d in ("Interface", "MapMarkers") if os.path.isdir(os.path.join(out, d))]
        # the tween menu's dividers and arrows (shapes 32, 83) are hand-tuned lighter on purpose
        r = subprocess.run([sys.executable, GATE] + dirs + ["--band", "41,102", "--allow-grey", "tweenmenu.swf:32,83"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-3000:])
            fail("a packaged SWF still carries Norden's panel grey")
        print("build-package: colour gate pass - %d SWFs read back" % r.stdout.count(" pass "))
    else:
        print("build-package: note  swf-colour-gate.py not found; colour not read back")
    total = sum(len(f) for _, _, f in os.walk(out))
    print("build-package: pass  %s  (%d recoloured files, %d DIP outputs, %d files in all)"
          % (out, copied, len(DIP_OUTPUTS), total))


if __name__ == "__main__":
    main(sys.argv[1:])
