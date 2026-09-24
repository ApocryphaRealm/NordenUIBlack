r"""Assemble the FULL "Norden UI - Black" as a FOMOD that mirrors Norden UI's own installer (the owner, 2026-09-24:
"recolor all of Norden UI ... so that I have a more comprehensive build to post to Nexus").

Norden UI (Nexus 166086, by Nithog) installs through a FOMOD of 18 steps / 92 groups / 251 options. This build recolours
EVERY option's SWFs and Wheeler SVGs with the rule in recolour.py / recolour-svg.py (export-xml.py, recolour.py --build
and recolour-svg.py --write run first, with NORDEN_XML / NORDEN_XML_BLACK / NORDEN_BLACK / NORDEN_SVG_ALL pointed at
build\full-*), then this script:

  1. applies the current build's moreHUD layout (inventory widget right-aligned at 98 %) to both resolutions' presets;
  2. rewrites Norden's ModuleConfig.xml: every step, group, option, flag, condition and image is kept - so a player makes
     the SAME choices they made for Norden - and every <file>/<folder> entry is kept only where the recoloured tree has
     it (an option with nothing to recolour installs nothing);
  3. adds a last step, "Norden UI - Black extras": the black RaceMenu DIP patch, Character Progression Control's
     level-up screen, and Norden's QuickLoot IE 4.0 BETA file recoloured;
  4. copies only the kept files, Norden's installer images, our info.xml, README, LICENSE and NOTICE into
     "7. current test builds\Norden UI - Black <ver> FOMOD".

Art stays out of git (.gitignore); this script is the only thing committed. Norden's permissions: modification and
release on Nexus with credit; no uploads elsewhere.

    python build-fomod.py            build the package
Env: NORDEN_SRC (extracted main archive), NORDEN_FULL_BLACK (recoloured tree), NORDEN_EXTRAS_FROM (a built flat package
of this mod carrying the RaceMenu DIP files and the CPC screen), OUT_ROOT.
"""
import os, re, sys, json, shutil, xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(REPO, "build")
SRC = os.environ.get("NORDEN_SRC", os.path.join(BUILD, "source", "main"))
QL_SRC = os.path.join(BUILD, "source", "quickloot-beta")
BLACK = os.environ.get("NORDEN_FULL_BLACK", os.path.join(BUILD, "full-black"))
OUT_ROOT = os.environ.get("OUT_ROOT", os.path.join(os.path.dirname(os.path.dirname(REPO)), "7. current test builds"))
EXTRAS_FROM = os.environ.get("NORDEN_EXTRAS_FROM", os.path.join(OUT_ROOT, "Norden UI - Black 1.0.2"))
VERSION = open(os.path.join(REPO, "VERSION"), encoding="utf-8-sig").read().strip()
OUT = os.path.join(OUT_ROOT, f"Norden UI - Black {VERSION} FOMOD")
QL_REL = os.path.join("Norden QuickLoot IE 4.0 BETA", "Interface", "LootMenuIE.swf")


def fail(msg):
    print("FAIL", msg)
    sys.exit(1)


def _try_decode(raw, enc):
    try:
        s = raw.decode(enc)
    except UnicodeDecodeError:
        return False
    return "<Version>" in s


def has_files(path):
    if os.path.isfile(path):
        return True
    return os.path.isdir(path) and any(fs for _, _, fs in os.walk(path))


# ---- 1. moreHUD layout, as the current build ships it --------------------------------------------------------------
morehud = 0
for res in ("Norden 1.2.3 16x9", "Norden 1.2.3 21x9"):
    d = os.path.join(SRC, "Patches", res, "SKSE", "Plugins", "moreHUD")
    for f in (os.listdir(d) if os.path.isdir(d) else []):
        if not f.lower().endswith(".json"):
            continue
        s = open(os.path.join(d, f), encoding="utf-8-sig").read()
        s2 = re.sub(r'("!AHZInventoryWidgetRightAligned"\s*:\s*)\d+', r"\g<1>1", s)
        s2 = re.sub(r'("!AHZInventoryWidgetXPercent"\s*:\s*)[0-9.]+', r"\g<1>98.0", s2)
        if s2 == s:
            fail(f"moreHUD preset {res}\\{f}: the two layout keys were not found")
        out = os.path.join(BLACK, "Patches", res, "SKSE", "Plugins", "moreHUD", f)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8", newline="").write(s2)
        morehud += 1
print(f"moreHUD presets with the current layout: {morehud}")
if morehud != 4:
    fail("expected four moreHUD presets (two per resolution)")

# ---- 2. Norden's installer, rewritten against the recoloured tree --------------------------------------------------
raw = open(os.path.join(SRC, "fomod", "ModuleConfig.xml"), "rb").read().decode("utf-16")
raw = re.sub(r"^\s*<!--.*?-->\s*", "", raw, flags=re.S)
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
root = ET.fromstring(raw)
root.find("moduleName").text = "Norden UI - Black"
kept, dropped, copies = 0, 0, set()
for plugin in root.iter("plugin"):
    files = plugin.find("files")
    if files is None:
        continue
    for el in list(files):
        src = el.get("source", "")
        if has_files(os.path.join(BLACK, src)):
            kept += 1
            copies.add(src)
        else:
            files.remove(el)
            dropped += 1
    if len(files) == 0:
        plugin.remove(files)
        desc = plugin.find("description")
        if desc is not None and desc.text and "Nothing to recolour" not in desc.text:
            desc.text = desc.text.rstrip() + "\n\n(Norden UI - Black: nothing to recolour in this option - Norden UI's own files are used.)"
print(f"installer entries kept {kept}, dropped {dropped} (nothing recoloured in them)")

# ---- 3. the extras step ------------------------------------------------------------------------------------------
dip_dir = os.path.join(EXTRAS_FROM, "Norden Black RaceMenu DIP")
dip_json = os.path.join(EXTRAS_FROM, "SKSE", "Plugins", "AutomaticPatcher", "DIP", "Norden-Black-RaceMenu.json")
cpc = os.path.join(EXTRAS_FROM, "Interface", "CharacterProgressionControl", "levelupmenu.swf")
ql = os.path.join(BLACK, QL_REL)
for p in (dip_dir, dip_json, cpc, ql):
    if not os.path.exists(p):
        fail(f"extra missing: {p}")
steps = root.find("installSteps")
step = ET.SubElement(steps, "installStep", {"name": "Norden UI - Black extras"})
groups = ET.SubElement(step, "optionalFileGroups", {"order": "Explicit"})
group = ET.SubElement(groups, "group", {"name": "Menus that are not Norden UI's own files", "type": "SelectAny"})
plugins = ET.SubElement(group, "plugins", {"order": "Explicit"})


def extra(name, desc, entries, typ="Optional"):
    p = ET.SubElement(plugins, "plugin", {"name": name})
    ET.SubElement(p, "description").text = desc
    fs = ET.SubElement(p, "files")
    for kind, s, d in entries:
        ET.SubElement(fs, kind, {"source": s, "destination": d, "priority": "0"})
    td = ET.SubElement(p, "typeDescriptor")
    ET.SubElement(td, "type", {"name": typ})


extra("RaceMenu - black race menu (Automatic DIP Patcher)",
      "The black race menu and bottom bar. RaceMenu's panels live in RaceMenu.bsa, so like Norden UI's own RaceMenu "
      "download this ships a Dynamic Interface Patcher patch: the Automatic DIP Patcher builds the black files from your "
      "own RaceMenu. Requires RaceMenu and the Automatic DIP Patcher; install Norden Racemenu DIP too.",
      [("folder", r"Extras\RaceMenu DIP\Norden Black RaceMenu DIP", "Norden Black RaceMenu DIP"),
       ("file", r"Extras\RaceMenu DIP\Norden-Black-RaceMenu.json", r"SKSE\Plugins\AutomaticPatcher\DIP\Norden-Black-RaceMenu.json"),
       # Norden's own RaceMenu download ships this loose beside its DIP patch; 1.0.2 shipped it black and the first
       # 1.0.3 FOMOD dropped it (2026-09-24, gate rule fomod-delivers-every-file-of-previous)
       ("file", r"Extras\RaceMenu DIP\buttonart.swf", r"Interface\racemenu\buttonart.swf")])
extra("Character Progression Control - level-up screen",
      "Character Progression Control's level-up screen in Norden's style, black. Only for Character Progression Control.",
      [("file", r"Extras\Character Progression Control\levelupmenu.swf", r"Interface\CharacterProgressionControl\levelupmenu.swf")])
extra("QuickLoot IE 4.0 BETA",
      "Norden UI's separate 'Norden UI Quickloot 4.0 BETA' download, black. Only if you use QuickLoot IE 4.0 and that "
      "Norden file; otherwise leave it unticked.",
      [("file", r"Extras\QuickLoot IE 4.0 BETA\LootMenuIE.swf", r"Interface\LootMenuIE.swf")])

# ---- 4. the package ------------------------------------------------------------------------------------------------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "fomod"))
n = 0
for rel in sorted(copies):
    s = os.path.join(BLACK, rel)
    d = os.path.join(OUT, rel)
    if os.path.isfile(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        n += 1
    else:
        for dp, _, fs in os.walk(s):
            for f in fs:
                t = os.path.join(d, os.path.relpath(os.path.join(dp, f), s))
                os.makedirs(os.path.dirname(t), exist_ok=True)
                shutil.copy2(os.path.join(dp, f), t)
                n += 1
# ---- 4b. hand-tuned files carry over ------------------------------------------------------------------------------
# Some shipped files were tuned by hand after the automatic rule (the tween menu's dividers and arrows, shapes 32/83,
# kept lighter on purpose; hudmenu.swf; QuestItemList.swf). The tuned copy lives in the installed Black build
# (HAND_TUNED_FROM). Wherever an installer option ships the SAME Norden original (by hash) the tuned copy replaces the
# automatic one; an option whose Norden file differs (another aspect ratio or style) keeps the automatic recolour and
# is listed, so nothing tuned is silently lost.
import hashlib
HAND_TUNED_FROM = os.environ.get("NORDEN_HAND_TUNED", r"D:\modlists\Njordlinger\mods\unpublished Norden UI - Black")
NORDEN_INSTALLED = os.environ.get("NORDEN_UI", r"D:\modlists\Njordlinger\mods\Norden UI")
_h = lambda p: hashlib.sha1(open(p, "rb").read()).hexdigest()
by_src = {}
for dp, _, fs in os.walk(os.path.join(SRC, "Patches")):
    for f in fs:
        if f.lower().endswith((".swf", ".svg")):
            p = os.path.join(dp, f)
            by_src.setdefault(_h(p), []).append(os.path.relpath(p, SRC))
tuned, untuned_variants = 0, []
if os.path.isdir(HAND_TUNED_FROM):
    for dp, _, fs in os.walk(HAND_TUNED_FROM):
        for f in fs:
            if not f.lower().endswith((".swf", ".svg")):
                continue
            hand = os.path.join(dp, f)
            rel = os.path.relpath(hand, HAND_TUNED_FROM)
            orig = os.path.join(NORDEN_INSTALLED, rel)
            if not os.path.exists(orig):
                continue
            for src_rel in by_src.get(_h(orig), []):
                auto = os.path.join(OUT, src_rel)
                if os.path.exists(auto) and _h(auto) != _h(hand):
                    shutil.copy2(hand, auto)
                    tuned += 1
                    print(f"  hand-tuned: {src_rel}")
            # variants of the same file name in other options, built from a DIFFERENT Norden original
            base = os.path.basename(rel).lower()
            same = set(by_src.get(_h(orig), []))
            for h_, rels in by_src.items():
                for r in rels:
                    if os.path.basename(r).lower() == base and r not in same and os.path.exists(os.path.join(OUT, r)) \
                            and _h(os.path.join(OUT, r)) != _h(hand) and base in ("tweenmenu.swf", "hudmenu.swf", "questitemlist.swf"):
                        untuned_variants.append(r)
print(f"hand-tuned files carried into {tuned} option file(s)")
if untuned_variants:
    print("variants built from a different Norden original keep the automatic recolour:")
    for r in sorted(set(untuned_variants)):
        print("   ", r)

shutil.copytree(dip_dir, os.path.join(OUT, "Extras", "RaceMenu DIP", "Norden Black RaceMenu DIP"))
shutil.copy2(dip_json, os.path.join(OUT, "Extras", "RaceMenu DIP", "Norden-Black-RaceMenu.json"))
shutil.copy2(os.path.join(EXTRAS_FROM, "Interface", "racemenu", "buttonart.swf"),
             os.path.join(OUT, "Extras", "RaceMenu DIP", "buttonart.swf"))
os.makedirs(os.path.join(OUT, "Extras", "Character Progression Control"))
shutil.copy2(cpc, os.path.join(OUT, "Extras", "Character Progression Control", "levelupmenu.swf"))
os.makedirs(os.path.join(OUT, "Extras", "QuickLoot IE 4.0 BETA"))
shutil.copy2(ql, os.path.join(OUT, "Extras", "QuickLoot IE 4.0 BETA", "LootMenuIE.swf"))
shutil.copytree(os.path.join(SRC, "Images"), os.path.join(OUT, "Images"))
for f in ("LICENSE", "NOTICE.md"):
    s = os.path.join(EXTRAS_FROM, f)
    if os.path.exists(s):
        shutil.copy2(s, os.path.join(OUT, f))
ET.indent(root, space="\t")
xml = ET.tostring(root, encoding="unicode")
open(os.path.join(OUT, "fomod", "ModuleConfig.xml"), "w", encoding="utf-16", newline="\r\n").write(xml)
info = f"""<fomod>
	<Name>Norden UI - Black</Name>
	<Author>ApocryphaRealm</Author>
	<Version>{VERSION}</Version>
	<Website>https://www.nexusmods.com/skyrimspecialedition/mods/166086</Website>
	<Description>Norden UI by Nithog with its panel grey taken to black, for every option of Norden UI's installer. Install Norden UI first, then this, choosing the same options; this mod sits above Norden UI.</Description>
</fomod>
"""
open(os.path.join(OUT, "fomod", "info.xml"), "w", encoding="utf-16", newline="\r\n").write(info)
_info_raw = open(os.path.join(SRC, "fomod", "info.xml"), "rb").read()
_info = next((_info_raw.decode(e) for e in ("utf-8-sig", "utf-16", "cp1252") if _try_decode(_info_raw, e)), "")
_m = re.search(r"<Version>\s*([0-9][0-9.]*)", _info)
NORDEN_VERSION = _m.group(1) if _m else "?"
readme = f"""Norden UI - Black {VERSION}

Norden UI (by Nithog, Nexus 166086) with its panel grey taken to black - for EVERY option of Norden UI's own installer.
Norden's #333333 panels become pure black; its lighter greys keep half their distance above the panel, so headers,
hover states and dividers stay distinct. Text, borders, hued accents, alpha and every fade are Norden's own.

Install: Norden UI first, then this, in a slot ABOVE Norden UI (higher priority). This installer asks the same
questions as Norden UI's - pick the same answers. Options with nothing to recolour install nothing and leave Norden's
own files in place. The last page offers the menus that are not Norden's loose files: RaceMenu (through the Automatic
DIP Patcher, like Norden's own RaceMenu download), Character Progression Control's level-up screen, and Norden's
QuickLoot IE 4.0 BETA file.

Requirements: Norden UI {NORDEN_VERSION}.
Credit: all art is Nithog's Norden UI, recoloured with permission terms that allow a modified release on Nexus with credit.
"""
open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(readme)
print(f"package: {OUT}")
print(f"  {n} recoloured file(s) from {len(copies)} installer entr(ies), plus extras, images and fomod")
