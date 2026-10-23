r"""Assemble the FULL "Norden UI - Black" as a FOMOD that mirrors Norden UI's own installer (the owner, 2026-09-24:
"recolor all of Norden UI ... so that I have a more comprehensive build to post to Nexus").

Norden UI (Nexus 166086, by Nithog) installs through a FOMOD of 18 steps / 92 groups / 251 options. This build recolours
EVERY option's SWFs and Wheeler SVGs with the rule in recolour.py / recolour-svg.py (export-xml.py, recolour.py --build
and recolour-svg.py --write run first, with NORDEN_XML / NORDEN_XML_BLACK / NORDEN_BLACK / NORDEN_SVG_ALL pointed at
build\full-*), then recolour-dialogue.py --build (1.0.4: the dialogue box's slate), then this script:

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
of this mod carrying the RaceMenu DIP files and the CPC screen), OUT_ROOT (default: the mod's per-game folder in
"7. current test builds", from the project's package-path resolver).

Build switches:
  NORDEN_INCLUDE_HPM=1      also add the HUD Position Manager widgets option (default OFF - HPM is not released yet and
                            its page waits; 1.0.4 ships without it, the owner 2026-10-07).
  NORDEN_ATELIER_BUILD      folder holding the theme-capable RaceMenuAtelier.dll + .pdb (default build\atelier); both
                            must match the SHA-256 pinned below (ATELIER_*), so only the recorded build can ship.
  NORDEN_ATELIER_THEME      the Norden Black theme.ini (default ..\RaceMenuAtelierNordenBlack\themes\norden-black.ini,
                            the one copy of that file).
"""
import os, re, sys, json, shutil, hashlib, xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(REPO, "build")
SRC = os.environ.get("NORDEN_SRC", os.path.join(BUILD, "source", "main"))
QL_SRC = os.path.join(BUILD, "source", "quickloot-beta")
BLACK = os.environ.get("NORDEN_FULL_BLACK", os.path.join(BUILD, "full-black"))
_PROJECT = os.path.dirname(os.path.dirname(REPO))
if os.environ.get("OUT_ROOT"):
    OUT_ROOT = os.environ["OUT_ROOT"]
else:
    # rule 10 (2026-10-01): packages sit in "<stage>\<Game> - <Mod>"; the one resolver is distro-names.ps1
    sys.path.insert(0, os.path.join(_PROJECT, ".MD", "scripts"))
    import package_paths
    OUT_ROOT = package_paths.package_root(package_paths.STAGE7, "Norden UI - Black", "Skyrim")
    if not OUT_ROOT:
        print("FAIL the package-path resolver returned no folder")
        sys.exit(1)
INCLUDE_HPM = os.environ.get("NORDEN_INCLUDE_HPM", "0") == "1"

# RaceMenu Atelier option (1.0.4, the owner 2026-10-07). The DLL is RaceMenu Atelier (emberchain, GPL-3.0) built from
# a patched build (branch upstream-apprentice) at commit
# ATELIER_COMMIT: Atelier 1.0.1 (f05e2c2) plus 09df305 (Apprentice's classes and traits as their own tiles), 370269a
# (optional theme.ini) and 62b288c (uLogLevel read from that theme.ini, so the shipped INI carries the log level) - the first two changes
# emberchain listed for Atelier 1.0.2, whose own build cannot be downloaded (Nexus page removed). Built with
#   xmake f -m releasedbg --skyrim_vr=n --cxflags=/d1trimfile:<clone dir>  &&  xmake build RaceMenuAtelier
# from a clone at a path with no spaces, inside the shared build environment (MODS_BUILD_ENV); 0 build paths and 0 user
# folders in the DLL and the PDB, PDB recorded by bare name, pairing proven. Rebuilt 2026-10-19 from a clean build tree
# (the 2026-10-07 build's PDB carried the user folder; link.exe keeps an old PDB's records).
ATELIER_COMMIT = "62b288c74f9fa26ae05dcf9dd41b8df084e9990a"
ATELIER_DLL_SHA256 = "585c1707475bb7f4ca507ef1fb0cfbdeae6946fb1ebd6c4b968c4ac22d2fb8d0"
ATELIER_PDB_SHA256 = "15c2519732dd57181e43c3a99d0e54c3d6ef17f52de237ad7fd2b40fb481c8cc"
ATELIER_BUILD = os.environ.get("NORDEN_ATELIER_BUILD", os.path.join(BUILD, "atelier"))
ATELIER_THEME = os.environ.get("NORDEN_ATELIER_THEME", os.path.join(os.path.dirname(REPO), "RaceMenuAtelierNordenBlack",
                                                                     "themes", "norden-black.ini"))
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
buttonart = os.path.join(EXTRAS_FROM, "Interface", "racemenu", "buttonart.swf")
if not os.path.exists(dip_dir):
    # 2026-10-04: the flat 1.0.2 package was pruned (rule 23); a previous FOMOD carries the same extras under Extras\
    _fx = os.environ.get("NORDEN_EXTRAS_FOMOD", os.path.join(os.path.dirname(os.path.dirname(REPO)), "10. finalized mods",
                                                             "Skyrim - Norden UI - Black", "Norden UI - Black 1.0.3 FOMOD"))
    dip_dir = os.path.join(_fx, "Extras", "RaceMenu DIP", "Norden Black RaceMenu DIP")
    dip_json = os.path.join(_fx, "Extras", "RaceMenu DIP", "Norden-Black-RaceMenu.json")
    buttonart = os.path.join(_fx, "Extras", "RaceMenu DIP", "buttonart.swf")
    cpc = os.path.join(_fx, "Extras", "Character Progression Control", "levelupmenu.swf")
    EXTRAS_FROM = _fx
    print(f"extras from the previous FOMOD: {_fx}")
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

# RaceMenu Atelier in Norden Black (the owner, 2026-10-07). Stock Atelier 1.0.0/1.0.1 cannot read a theme, so the
# option ships the theme file AND the theme-capable Atelier DLL (see ATELIER_COMMIT). Recommended when Atelier's DLL is
# installed; otherwise optional and unticked, as the HPM option does (a NotUsable default would lock out a player whose
# installer cannot see a loose DLL, or who installs Atelier afterwards).
_sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
_adll = os.path.join(ATELIER_BUILD, "RaceMenuAtelier.dll")
_apdb = os.path.join(ATELIER_BUILD, "RaceMenuAtelier.pdb")
for _f, _want in ((_adll, ATELIER_DLL_SHA256), (_apdb, ATELIER_PDB_SHA256)):
    if not os.path.isfile(_f):
        fail(f"Atelier build missing: {_f} - build {ATELIER_COMMIT[:7]} of the fork (see ATELIER_COMMIT) and copy it there")
    if _sha(_f) != _want:
        fail(f"{_f} is not the recorded Atelier build ({ATELIER_COMMIT[:7]}): SHA-256 {_sha(_f)} != {_want}")
if not os.path.isfile(ATELIER_THEME):
    fail(f"Norden Black Atelier theme missing: {ATELIER_THEME}")
_ap = ET.SubElement(plugins, "plugin", {"name": "RaceMenu Atelier"})
ET.SubElement(_ap, "description").text = (
    "Only if you use RaceMenu Atelier (by emberchain). Dresses Atelier's character-creation screen in Norden UI - "
    "Black's palette: black panels, Norden's silver lines and square corners. Requires RaceMenu Atelier. Atelier 1.0.0 "
    "and 1.0.1 cannot read a theme, so this option also REPLACES Atelier's RaceMenuAtelier.dll with a build that reads "
    "one: Atelier 1.0.1 with the two changes of Atelier 1.0.2 (Apprentice - A Class Overhaul's classes and traits as "
    "their own tiles, and the optional theme.ini) and a log level read from that theme file, RaceMenu Atelier by emberchain (GPL-3.0), patched build from commit "
    + ATELIER_COMMIT[:7] + " (GPL-3.0). Give Norden UI - Black a higher priority than RaceMenu Atelier (in MO2's left "
    "pane, below it) so this DLL wins. Atelier is emberchain's work; used with permission. Delete "
    r"SKSE\Plugins\RaceMenuAtelier\theme.ini to get Atelier's own colours back.")
_afs = ET.SubElement(_ap, "files")
# The option is ONE top-level folder holding the install tree as it lands in the mod folder (SKSE\Plugins\..., docs\...),
# installed with destination "". Why a top-level folder with no separator in its name: the package gate row
# installed-build-is-the-package judges a FOMOD's installed DLL by flattening only such a folder
# (the way Apocrypha Menu Framework's SMF-Name\ is flattened); a per-file mapping from Extras\RaceMenu Atelier\ to
# SKSE\Plugins\ read as "never installed" although the install was right (2026-10-19). Installed result unchanged.
ET.SubElement(_afs, "folder", {"source": "RaceMenu Atelier", "destination": "", "priority": "0"})
_atd = ET.SubElement(_ap, "typeDescriptor")
_adt = ET.SubElement(_atd, "dependencyType")
ET.SubElement(_adt, "defaultType", {"name": "Optional"})
_apat = ET.SubElement(ET.SubElement(_adt, "patterns"), "pattern")
ET.SubElement(ET.SubElement(_apat, "dependencies", {"operator": "And"}), "fileDependency",
              {"file": r"SKSE\Plugins\RaceMenuAtelier.dll", "state": "Active"})
ET.SubElement(_apat, "type", {"name": "Recommended"})
ATELIER_NOTE = f"""RaceMenu Atelier - the build installed by Norden UI - Black

SKSE\\Plugins\\RaceMenuAtelier.dll (and its .pdb) installed by Norden UI - Black's "RaceMenu Atelier" option is
RaceMenu Atelier by emberchain (https://github.com/emberchain/RaceMenuAtelier), licensed GPL-3.0, modified.

RaceMenu Atelier by emberchain (GPL-3.0), patched build from commit {ATELIER_COMMIT[:7]}
  = RaceMenu Atelier 1.0.1 (emberchain, f05e2c2)
  + 09df305  Apprentice - A Class Overhaul's classes and traits get their own tiles and are picked through the menu's
             onItemPress (never ChangeRace)
  + 370269a  optional SKSE\\Plugins\\RaceMenuAtelier\\theme.ini: palette and corner radius
  + 62b288c  uLogLevel in that theme.ini sets the log's verbosity (2 = info, the shipped value)
The first two are the changes emberchain lists for RaceMenu Atelier 1.0.2 (offered upstream as
emberchain/RaceMenuAtelier pull request #1); the third only adds the log level. Build: git submodule update --init --recursive; xmake f -m releasedbg --skyrim_vr=n
--cxflags=/d1trimfile:<clone folder>; xmake build RaceMenuAtelier.
SHA-256 RaceMenuAtelier.dll {ATELIER_DLL_SHA256}
SHA-256 RaceMenuAtelier.pdb {ATELIER_PDB_SHA256}

The licence is the GNU General Public License version 3 (LICENSE in the Norden UI - Black download,
https://www.gnu.org/licenses/gpl-3.0.txt). theme.ini holds the Norden UI - Black palette and the log level.
To go back to stock Atelier, untick the option (or delete these files) and let RaceMenu Atelier's own DLL win.
"""

# Inventory Reforged for SkyUI (1.1.0, the owner 2026-10-21: "adding support in Norden Black to have it recoloured").
# Inventory Reforged (Nexus 195826) is open: its page lets anyone use, change, convert, reupload and include any part
# of it in their own mods, free or not, without asking, credit welcome (read 2026-10-21 from its description). Even so
# this option ships NO changed Inventory Reforged art or code: the mod reads two colours from its own INI
# (iAccentColor, iTextColor) and takes every other colour from the skin it sits on, so the option is its default INI
# with those two numbers changed. Recommended when its DLL is installed, otherwise optional and unticked.
IR_INI = os.path.join(REPO, "extras", "inventory-reforged", "InventoryReforged.ini")
IR_3D_SRC = os.path.join(SRC, "Patches", "Norden default 3D item position 1.1", "MCM", "Settings", "SkyUI_SE.ini")
for _f in (IR_INI, IR_3D_SRC):
    if not os.path.isfile(_f):
        fail(f"Inventory Reforged option input missing: {_f}")
_irp = ET.SubElement(plugins, "plugin", {"name": "Inventory Reforged - Norden Black colours"})
ET.SubElement(_irp, "description").text = (
    "Only if you use Inventory Reforged for SkyUI (Nexus 195826). Its gold accent and parchment text become Norden UI - "
    "Black's silver (#BBBDBF) and soft white (#E5E5E5): frames, headings, numbers, tabs and names of the equipment "
    "panel. Everything else in the panel (its black sheet, edges, buttons) already follows the skin it sits on, so it is "
    "black under Norden UI - Black. Installs SKSE\\Plugins\\InventoryReforged.ini holding only those two colours - every other setting keeps Inventory Reforged's "
    "own default; no art and no code of Inventory Reforged is included. What you set in its own menu (MCM) still wins, key by "
    "key; delete the file to get its gold back. Give Norden UI - Black a "
    "higher priority than Inventory Reforged so this file wins.")
ET.SubElement(ET.SubElement(_irp, "files"), "folder", {"source": "Inventory Reforged", "destination": "", "priority": "0"})
_irt = ET.SubElement(ET.SubElement(_irp, "typeDescriptor"), "dependencyType")
ET.SubElement(_irt, "defaultType", {"name": "Optional"})
_irpat = ET.SubElement(ET.SubElement(_irt, "patterns"), "pattern")
ET.SubElement(ET.SubElement(_irpat, "dependencies", {"operator": "And"}), "fileDependency",
              {"file": r"SKSE\Plugins\InventoryReforged.dll", "state": "Active"})
ET.SubElement(_irpat, "type", {"name": "Recommended"})
_irq = ET.SubElement(plugins, "plugin", {"name": "Inventory Reforged - item preview size (SkyUI default 3D item position)"})
ET.SubElement(_irq, "description").text = (
    "Only if the 3D item in Inventory Reforged's item window is small or off its place. Inventory Reforged sizes and "
    "places that 3D item from the position SkyUI's own '3D item' settings give the game when the inventory first opens "
    "(Norden UI's installer sets them for its own item card, e.g. scale 0.6 with the Slimventory layout, so the item is "
    "drawn at a fraction of the size). This installs Norden UI's own 'SkyUI Default' file for them (scale 1.5, offsets "
    "-10 / 0), the same as choosing 'SkyUI Default' under Inventory Patches > 3D Item Location in Norden UI's installer. "
    "It also carries that file's other Norden settings (item card and effect widget), so if you use a vertical or "
    "other layout, leave this unticked and set the 3D item scale to 1.5 and the offsets to 0 in SkyUI's MCM "
    "(Advanced > 3D item) instead. Restart the game after changing it. Give Norden UI - Black a higher priority than "
    "Norden UI so this file wins. Norden UI is Nithog's work; this is Nithog's file, unchanged.")
ET.SubElement(ET.SubElement(_irq, "files"), "folder", {"source": "Inventory Reforged preview", "destination": "", "priority": "0"})
ET.SubElement(ET.SubElement(_irq, "typeDescriptor"), "type", {"name": "Optional"})
IR_PANELS = {}   # version -> (patched panel.swf from tools/ir-preview-patch.py, folder in the package)
# Inventory Reforged 1.4.0 is the one shipped: the owner moved to it and 1.2.4 / 1.3.0 are two releases behind. The patch tool still
# builds and checks 1.2.4 and 1.3.0 (python tools/ir-preview-patch.py --version 1.3.0) should an option for them be wanted again.
for _v, _folder in (("1.4.0", "Inventory Reforged panel 1.4.0"),):
    _f = os.path.join(BUILD, "ir-panel", _v, "Interface", "InventoryReforged", "panel.swf")
    if not os.path.isfile(_f):
        fail(f"patched Inventory Reforged {_v} panel.swf missing: {_f} - run tools/ir-preview-patch.py first")
    IR_PANELS[_v] = (_f, _folder)
# one panel.swf per mod folder, and it belongs to one Inventory Reforged version: the two choices exclude each other
_irg = ET.SubElement(groups, "group", {"name": "Inventory Reforged panel fixes - pick the version you use", "type": "SelectAtMostOne"})
_irgp = ET.SubElement(_irg, "plugins", {"order": "Explicit"})
for _v, (_f, _folder) in IR_PANELS.items():
    _irl = ET.SubElement(_irgp, "plugin", {"name": f"Inventory Reforged {_v} - panel fixes: item preview, Character button, Norden's own item card"})
    ET.SubElement(_irl, "description").text = (
        f"Only for Inventory Reforged for SkyUI {_v} (Nexus 195826), and only if its item window misbehaves under Norden UI. "
        "(1) The 3D item in its item window is small, sits high or leaves the window: it is now aimed at the middle of the "
        "whole part of the window above its stats and sized to fit it (weapons and ammo a little smaller, being long), and with "
        "'Show the character' switched off the settings popup (the cog) has an ITEM PREVIEW section - Size, Sideways, Up and "
        "down, Reset size and place - kept in the same three saved numbers as the character's (60 to 140 percent, plus or "
        "minus 40 percent), so they are remembered; with the character on those numbers belong to the character again. "
        "(2) The CHARACTER button stays at the bottom of the screen when the Character drawer opens; the drawer opens above it. "
        "(3) Norden's item card is left alone: Inventory Reforged takes the menu's own item card into its window - hides the "
        "card's background art, adds a kind line and shifts the card's parts, rescales it to the window width, moves it with the "
        "window, re-breaks its effect text and, from 1.3.0, hides it whenever its window is hidden - so it never looked like "
        "Norden's card. This replaces Inventory Reforged's panel.swf with a copy that does none of that: Norden's card shows as "
        "Norden made it, in Norden's place below the item list, all the time, while the item window still follows the row. "
        "(4) A fixed place for the item window: with 'Show the character' switched off, the cog popup's Item window section has "
        "'Fixed place'. Fixed, the window is locked in one place: it no longer follows the row or the pointer, it stands over the "
        "right side of the item list - over the Type, Weight and Value columns and their headers - from the top of the list's "
        "frame to its bottom, inside that frame and above Norden's card. The 3D item is held inside the window at every size: "
        "it is fitted by its bounding sphere, which no turn of the model can grow, so it never reaches past the window's "
        "edges. It is off by default - nothing changes until you "
        "tick it - and it is kept (it rides in the saved Doll turn speed, which does nothing while the character is hidden; "
        "switching the character on puts the turn speed back to 0.5 and ends Fixed). "
        "The kind line (\"ONE-HANDED, SWORD\") that Inventory Reforged added to the card is not shown. Inventory Reforged's "
        "page allows changing any part of the mod; credit: Inventory Reforged for SkyUI. The file belongs to version "
        f"{_v}: untick this option (or delete the file) after updating Inventory Reforged. Works best with SkyUI's 3D item scale "
        "at 1.5 and offsets 0 (or the 'item preview size' option). Give Norden UI - Black a higher priority than Inventory Reforged.")
    ET.SubElement(ET.SubElement(_irl, "files"), "folder", {"source": _folder, "destination": "", "priority": "0"})
    ET.SubElement(ET.SubElement(_irl, "typeDescriptor"), "type", {"name": "Optional"})
IR_NOTE = """Inventory Reforged for SkyUI - what Norden UI - Black's option installs

SKSE\\Plugins\\InventoryReforged.ini is a settings file of Inventory Reforged for SkyUI (any version)
(https://www.nexusmods.com/skyrimspecialedition/mods/195826) holding only two numbers in [Look]; every other setting keeps the mod's own default:
  iAccentColor 14069864 (gold)       -> 12303807 (#BBBDBF, Norden's silver)
  iTextColor   15130824 (parchment)  -> 15066597 (#E5E5E5, Norden Black's text)
Inventory Reforged's page allows using, changing, converting, reuploading and including any part of the mod in your
own mods without asking; credit: Inventory Reforged for SkyUI. No art and no code of Inventory Reforged is included.
Settings you make in its own menu are kept in Data/MCM/Settings/InventoryReforged.ini and win over this file.
To go back to its own colours, untick the option or delete this file.
"""

# HUD Position Manager's own widgets in Norden Black's look (the owner, 2026-10-04: "make it a FOMOD option if they use
# HUD Position Manager because a lot of people aren't going to be using HUD Position Manager yet and we need to maintain
# compatibility with the current"). Built by tools/hpm-widgets.py from the installed Norden UI - Black widget art;
# nothing else in the package changes - the CastingBar / STB Widgets / oxygen meter reskins stay as they were.
# Recommended when HPM's DLL is installed, otherwise optional and unticked.
HPM_WIDGETS = os.environ.get("NORDEN_HPM_WIDGETS", os.path.join(BUILD, "hpm-widgets", "Interface", "HUDPositionManager", "widgets"))
HPM_NAMES = ("breath", "casting", "detection", "shout", "level", "level_badge", "gold", "weight", "time", "playtime", "resist", "equip", "bowdraw", "shoutcharge", "playerhealth", "playermagicka", "playerstamina", "infobar", "bossbar")
if INCLUDE_HPM:
    for _n in HPM_NAMES:
        if not os.path.exists(os.path.join(HPM_WIDGETS, _n + ".swf")):
            fail(f"HPM widget missing: {_n}.swf - run tools/hpm-widgets.py first")
    _p = ET.SubElement(plugins, "plugin", {"name": "HUD Position Manager - its widgets in Norden Black"})
    ET.SubElement(_p, "description").text = (
        "Only if you use HUD Position Manager (1.1 or later). HUD Position Manager builds its own HUD widgets - breath, "
        "casting, shout cooldown, detection, level, gold, carry weight and game time. This dresses them in Norden UI - "
        "Black's own art (the casting bar, oxygen meter and STB widget styles), instead of HUD Position Manager's plain "
        "default look. Place Norden UI - Black above HUD Position Manager so these files win.")
    _fs = ET.SubElement(_p, "files")
    ET.SubElement(_fs, "folder", {"source": r"Extras\HUD Position Manager\widgets",
                                  "destination": r"Interface\HUDPositionManager\widgets", "priority": "0"})
    _td = ET.SubElement(_p, "typeDescriptor")
    _dt = ET.SubElement(_td, "dependencyType")
    ET.SubElement(_dt, "defaultType", {"name": "Optional"})
    _pats = ET.SubElement(_dt, "patterns")
    _pat = ET.SubElement(_pats, "pattern")
    _deps = ET.SubElement(_pat, "dependencies", {"operator": "And"})
    ET.SubElement(_deps, "fileDependency", {"file": r"SKSE\Plugins\HUDPositionManager.dll", "state": "Active"})
    ET.SubElement(_pat, "type", {"name": "Recommended"})
    print("HUD Position Manager option: INCLUDED (NORDEN_INCLUDE_HPM=1)")
else:
    print("HUD Position Manager option: left out (set NORDEN_INCLUDE_HPM=1 to add it)")

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
# 2026-10-07: the installed folder was renamed "Norden UI Black" (installed from Nexus 1.0.3); the old default no longer
# existed and the carry-over silently did nothing, so 1.0.4's first build shipped the automatic hudmenu / tweenmenu /
# QuestItemList. A missing folder now stops the build.
HAND_TUNED_FROM = os.environ.get("NORDEN_HAND_TUNED") or next(
    (p for p in (r"D:\modlists\Njordlinger\mods\Norden UI Black", r"D:\modlists\Njordlinger\mods\unpublished Norden UI - Black")
     if os.path.isdir(p)), "")
if not os.path.isdir(HAND_TUNED_FROM):
    fail("hand-tuned Norden UI - Black folder not found - set NORDEN_HAND_TUNED to the installed Black mod folder")
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
            if "dialoguemenu" in rel.lower():
                continue   # 1.0.4: re-recoloured by recolour-dialogue.py; the installed 1.0.3 copy has the unrecoloured slate box
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
shutil.copy2(buttonart, os.path.join(OUT, "Extras", "RaceMenu DIP", "buttonart.swf"))
os.makedirs(os.path.join(OUT, "Extras", "Character Progression Control"))
shutil.copy2(cpc, os.path.join(OUT, "Extras", "Character Progression Control", "levelupmenu.swf"))
os.makedirs(os.path.join(OUT, "Extras", "QuickLoot IE 4.0 BETA"))
shutil.copy2(ql, os.path.join(OUT, "Extras", "QuickLoot IE 4.0 BETA", "LootMenuIE.swf"))
if INCLUDE_HPM:
    os.makedirs(os.path.join(OUT, "Extras", "HUD Position Manager", "widgets"))
    for _n in HPM_NAMES:
        shutil.copy2(os.path.join(HPM_WIDGETS, _n + ".swf"), os.path.join(OUT, "Extras", "HUD Position Manager", "widgets", _n + ".swf"))
_ao = os.path.join(OUT, "RaceMenu Atelier", "SKSE", "Plugins")
os.makedirs(os.path.join(_ao, "RaceMenuAtelier"))
os.makedirs(os.path.join(OUT, "RaceMenu Atelier", "docs"))
shutil.copy2(_adll, os.path.join(_ao, "RaceMenuAtelier.dll"))
shutil.copy2(_apdb, os.path.join(_ao, "RaceMenuAtelier.pdb"))
shutil.copy2(ATELIER_THEME, os.path.join(_ao, "RaceMenuAtelier", "theme.ini"))
open(os.path.join(OUT, "RaceMenu Atelier", "docs", "RaceMenu Atelier - Norden UI - Black build.txt"), "w", encoding="utf-8", newline="\r\n").write(ATELIER_NOTE)
if _sha(os.path.join(_ao, "RaceMenuAtelier.dll")) != ATELIER_DLL_SHA256:
    fail("the packaged RaceMenuAtelier.dll does not match the recorded build")
_iro = os.path.join(OUT, "Inventory Reforged")
os.makedirs(os.path.join(_iro, "SKSE", "Plugins"))
os.makedirs(os.path.join(_iro, "docs"))
shutil.copy2(IR_INI, os.path.join(_iro, "SKSE", "Plugins", "InventoryReforged.ini"))
open(os.path.join(_iro, "docs", "Inventory Reforged - Norden UI - Black.txt"), "w", encoding="utf-8", newline="\r\n").write(IR_NOTE)
_irv = os.path.join(OUT, "Inventory Reforged preview", "MCM", "Settings")
os.makedirs(_irv)
shutil.copy2(IR_3D_SRC, os.path.join(_irv, "SkyUI_SE.ini"))
for _v, (_f, _folder) in IR_PANELS.items():
    _d = os.path.join(OUT, _folder, "Interface", "InventoryReforged")
    os.makedirs(_d)
    shutil.copy2(_f, os.path.join(_d, "panel.swf"))
    os.makedirs(os.path.join(OUT, _folder, "docs"))
    open(os.path.join(OUT, _folder, "docs", f"Inventory Reforged {_v} panel.swf - Norden UI - Black.txt"), "w", encoding="utf-8", newline="\r\n").write(
        f"Interface\\InventoryReforged\\panel.swf installed by Norden UI - Black's \"panel fixes\" option is\n"
        f"panel.swf of Inventory Reforged for SkyUI {_v} (Nexus 195826) with TWO scripts changed (DoAction_21, 22):\n"
        "DoAction_22: Equipment.aimPreview is replaced - the 3D item is aimed at the middle of the whole part of the item window\n"
        "above its stats and sized to min(area, window width) x fit (0.95 weapons and ammo, 1.1 the rest) x the player's size - and\n"
        "the settings popup gets an ITEM PREVIEW section (Size, Sideways, Up and down, Reset) when the character is switched off,\n"
        "using the saved numbers of the character controls (iScale, iShiftRight, iShiftUp of [Doll]). DoAction_22 also redefines\n"
        "sizeWindow, windowUnits, placeWindow, cardSpan, showWindow, keepFrameHidden and effectLines without the lines that moved,\n"
        "rescaled, hid, restyled and re-worded the menu's item card (Norden's), so it shows as Norden made it, in Norden's place.\n"
        "DoAction_22 also adds a Fixed place mode for the item window (Item window section of the popup: Fixed place), locked over the right side of the item list at the list frame's full height, the 3D item held inside it by its bounding sphere (PlacePreview's room), kept in the saved Doll turn speed (fTurnSpeed) while the character is hidden.\n"
        "DoAction_21 (Character drawer): the CHARACTER tab stays at the bottom, the drawer opens above it.\n"
        "Inventory Reforged's page allows changing and including any part of the mod without asking; credit: Inventory Reforged\n"
        "for SkyUI. Tool: tools/ir-preview-patch.py in the Norden UI - Black repository. Delete this file (or untick the option)\n"
        "after updating Inventory Reforged.\n")
shutil.copytree(os.path.join(SRC, "Images"), os.path.join(OUT, "Images"))
# LICENSE and NOTICE come from the repo (they used to be copied from the previous release - library 7050's seeding
# trap: a notice changed in the repo would never have reached the package)
for f in ("LICENSE", "NOTICE.md"):
    shutil.copy2(os.path.join(REPO, f), os.path.join(OUT, f))
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
HPM_README = (", HUD Position Manager's own HUD widgets (breath, casting, shout,\ndetection, level, gold, carry weight, "
              "game time) in Norden UI - Black's art - recommended only when HUD\nPosition Manager is installed -"
              if INCLUDE_HPM else "")
readme = f"""Norden UI - Black {VERSION}

Norden UI (by Nithog, Nexus 166086) with its panel grey taken to black - for EVERY option of Norden UI's own installer.
Norden's #333333 panels become pure black; its lighter greys keep half their distance above the panel, so headers,
hover states and dividers stay distinct. Text, borders, hued accents, alpha and every fade are Norden's own.

Install: Norden UI first, then this, in a slot ABOVE Norden UI (higher priority). This installer asks the same
questions as Norden UI's - pick the same answers. Options with nothing to recolour install nothing and leave Norden's
own files in place. The last page offers the menus that are not Norden's loose files: RaceMenu (through the Automatic
DIP Patcher, like Norden's own RaceMenu download), Character Progression Control's level-up screen, Norden's
QuickLoot IE 4.0 BETA file{HPM_README}, and RaceMenu Atelier.

RaceMenu Atelier (optional): for players who use RaceMenu Atelier by emberchain. It dresses Atelier's screen in
Norden UI - Black's palette (black panels, Norden's silver lines, square corners). Atelier 1.0.0 and 1.0.1 cannot read
a theme, so the option installs SKSE\\Plugins\\RaceMenuAtelier\\theme.ini AND replaces Atelier's RaceMenuAtelier.dll
with a build that reads it: Atelier 1.0.1 plus the two changes of Atelier 1.0.2 (Apprentice - A Class Overhaul's
classes and traits as their own tiles; the optional theme.ini). It is recommended only when RaceMenuAtelier.dll is
installed. Give Norden UI - Black a HIGHER priority than RaceMenu Atelier - in MO2's left pane, place it BELOW RaceMenu
Atelier - so this DLL wins. Delete theme.ini for Atelier's own colours; untick the option to go back to stock Atelier.
RaceMenu Atelier is GPL-3.0; the build is RaceMenu Atelier by emberchain (GPL-3.0), patched build from commit {ATELIER_COMMIT[:7]} (see NOTICE.md and
docs\\RaceMenu Atelier - Norden UI - Black build.txt).

Inventory Reforged (optional, 1.1.0): for players who use Inventory Reforged for SkyUI (Nexus 195826). Its gold accent and
parchment text become Norden's silver (#BBBDBF) and soft white (#E5E5E5); the rest of its panel already follows the skin,
so it is black under Norden UI - Black. The option is a settings file holding only those two colours
(SKSE\\Plugins\\InventoryReforged.ini; every other setting keeps the mod's own default) - no art or code of Inventory Reforged. Its menu settings still win. A second,
unticked choice, "item preview size", installs Norden UI's 'SkyUI Default' 3D item position for players whose 3D item in
Inventory Reforged's item window is small. A third, unticked choice (Inventory Reforged 1.4.0), "panel fixes", replaces its panel.swf with a copy where two scripts changed: the item preview, the Character button staying at the bottom, and Norden's own item card left alone (allowed by that mod's page).
Give Norden UI - Black a higher priority than Inventory Reforged.

Requirements: Norden UI {NORDEN_VERSION}. For the RaceMenu Atelier option: RaceMenu Atelier (and RaceMenu). For the Inventory Reforged options: Inventory Reforged for SkyUI.
Credit: all art is Nithog's Norden UI, recoloured with permission terms that allow a modified release on Nexus with credit.
RaceMenu Atelier is emberchain's (GPL-3.0), modified and shipped with emberchain's permission.
Inventory Reforged for SkyUI is its author's work (Nexus 195826); its settings file is reused with the permission its page gives.
"""
open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(readme)
print(f"package: {OUT}")
print(f"  {n} recoloured file(s) from {len(copies)} installer entr(ies), plus extras, images and fomod")
