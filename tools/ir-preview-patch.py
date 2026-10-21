r"""Inventory Reforged for SkyUI 1.2.4 - a larger, centred, fitted item preview with its own size and place controls
(Norden UI - Black 1.0.5, 2026-10-21).

Why: Inventory Reforged's item window keeps its 3D item in a box of PREVIEW_HEIGHT = 130 stage units at the top of the
window and asks the plugin (PlacePreview) for an item (130 - 2 * WINDOW_PAD) / screen height tall. Under Norden UI the
window is taller than that box, so the item sits small in the upper part of a tall black panel; and the plugin sizes
the item by that number alone, so long things (swords, bows, arrows) and tall things (cuirasses) leave the box at any
size that is large enough to look right.

What this changes (ONE script of panel.swf, DoAction_22, and nothing else):
  * Equipment.aimPreview is replaced. The item is aimed at the middle of the whole part of the window above its stats
    and asked for a height of  min(area, window width) * fit * size , where fit is 0.95 for weapons and ammo (long: a
    sword is as long as the height asked for, a bow is 0.86 of it each way) and 1.1 for everything else, and size is
    the player's percentage (100 = fits the box).
  * The size and the place come from the Character controls of the settings popup when the character is switched off:
    the popup then shows an ITEM PREVIEW section (Size, Sideways, Up and down, Reset size and place) with the same
    controls, bound to the same three stored numbers (iScale, iShiftRight, iShiftUp of [Doll], 60 to 140 percent and
    plus or minus 40 percent) the plugin already saves in Data/MCM/Settings/InventoryReforged.ini. The plugin's setter
    takes only its known keys, so no new key could be saved without changing the DLL. With the character on those
    numbers drive the character as before and the item preview uses the defaults (100, middle).

The file must be Inventory Reforged 1.2.4's panel.swf (SHA-256 in extras/inventory-reforged/panel-1.2.4.sha256); the
result is re-decompiled and the tool refuses it unless only DoAction_22.as differs and the edits are all there.
Inventory Reforged's page allows changing and including any part of the mod without asking (credit: Inventory
Reforged for SkyUI, Nexus 195826), see extras/inventory-reforged/PERMISSIONS.txt. The output stays out of git (*.swf).

    python tools/ir-preview-patch.py [--src <Inventory Reforged 1.2.4 panel.swf>] [--out <folder>]
"""
import argparse, hashlib, os, shutil, subprocess, sys, tempfile

FF = r"C:\Program Files (x86)\FFDec\ffdec-cli.exe"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DEFAULT = os.environ.get("NORDEN_IR_PANEL", r"D:\Modlists\Njordlinger\mods\Inventory Reforged for SkyUI\Interface\InventoryReforged\panel.swf")

NEW_FUNCTIONS = '''
Equipment.PREVIEW_FIT = 1.1;
Equipment.PREVIEW_FIT_LONG = 0.95;
Equipment.previewTune = function()
{
   var tune = {size:1,across:0,upward:0};
   if(Equipment.settings.doll != true)
   {
      tune.size = Equipment.number(Equipment.settings.dollScale) / 100;
      tune.across = Equipment.number(Equipment.settings.dollRight) / 100;
      tune.upward = Equipment.number(Equipment.settings.dollUp) / 100;
   }
   return tune;
};
Equipment.aimPreview = function()
{
   var window = Equipment.window;
   var high = window.preview != undefined ? window.preview : Equipment.PREVIEW_HEIGHT;
   var area = high;
   var wide = Equipment.windowWide();
   var tune = Equipment.previewTune();
   var entry = Equipment.windowEntry();
   var fit = entry != undefined && (entry.formType == Equipment.WEAPON || entry.formType == Equipment.AMMO) ? Equipment.PREVIEW_FIT_LONG : Equipment.PREVIEW_FIT;
   var middle;
   if(window.high > 0)
   {
      area = Math.max(high,window.high - Equipment.underCard());
   }
   middle = Equipment.share(window._x + wide / 2 + tune.across * wide,window._y + area / 2 - tune.upward * area);
   if(Equipment.plugin() != undefined && !Equipment.inspecting)
   {
      Equipment.plugin().PlacePreview(middle.x,middle.y,Math.min(area,wide) * fit * tune.size / Stage.visibleRect.height);
   }
};
'''

# (old, new) - each old text must occur exactly once in DoAction_22.as
EDITS_22 = [
    ('''   y += Equipment.lookCheck(sheet,"doll",Equipment.say("Show the character"),undefined,pad,y,inner,Equipment.LOOK_LINE);
''', '''   y += Equipment.lookCheck(sheet,"doll",Equipment.say("Show the character"),undefined,pad,y,inner,Equipment.LOOK_LINE);
   if(Equipment.settings.doll != true)
   {
      y += Equipment.lookHead(sheet,Equipment.say("Item preview"),pad,y,inner);
   }
'''),
    ('''   else
   {
      Equipment.showPlayer();
   }
   Equipment.showLookValues();
   gfx.io.GameDelegate.call("PlaySound",["UIMenuFocus"]);
};
Equipment.flipLook = function(key)''', '''   else
   {
      Equipment.showPlayer();
      Equipment.aimPreview();
   }
   Equipment.showLookValues();
   gfx.io.GameDelegate.call("PlaySound",["UIMenuFocus"]);
};
Equipment.flipLook = function(key)'''),
    ('''      Equipment.changeSetting("doll","bShow:Doll",Equipment.settings.doll != true);
      Equipment.showPlayer();
''', '''      Equipment.changeSetting("doll","bShow:Doll",Equipment.settings.doll != true);
      Equipment.showPlayer();
      Equipment.aimPreview();
      Equipment.makeLook();
'''),
    ('''   Equipment.changeSetting("dollUp",Equipment.LOOK_STEPS.dollUp.id,0);
   Equipment.showPlayer();
''', '''   Equipment.changeSetting("dollUp",Equipment.LOOK_STEPS.dollUp.id,0);
   Equipment.showPlayer();
   Equipment.aimPreview();
'''),
]

# DoAction_21 (the Character drawer): its tab stays at the bottom of the screen; the drawer opens above it.
EDITS_21 = [
    ("""   drawer._y = Math.round(stage._y + stage.touch._height);
   drawer.room = stage.touch._height - Equipment.HERO_TAB_HIGH - Equipment.HERO_INSET;
""", """   drawer._y = Math.round(stage._y + stage.touch._height) - Equipment.HERO_TAB_HIGH;
   drawer.room = stage.touch._height - 2 * Equipment.HERO_TAB_HIGH - Equipment.HERO_INSET;
"""),
    ("""   tab._y = Math.round(- drawer.high - high + (out ? 1 : 0));
""", """   tab._y = 0;
"""),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ff(*a):
    return subprocess.run([FF, *a], capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC_DEFAULT)
    ap.add_argument("--out", default=os.path.join(HERE, "build", "ir-panel", "Interface", "InventoryReforged"))
    a = ap.parse_args()
    if not os.path.isfile(a.src):
        sys.exit(f"FAIL panel.swf not found: {a.src}")
    want = open(os.path.join(HERE, "extras", "inventory-reforged", "panel-1.2.4.sha256")).read().split()[0]
    if sha(a.src) != want:
        sys.exit(f"FAIL {a.src} is not Inventory Reforged 1.2.4's panel.swf (SHA-256 {sha(a.src)} != {want})")
    tmp = tempfile.mkdtemp(prefix="irpatch-")
    try:
        work = os.path.join(tmp, "src"); os.makedirs(work)
        orig = os.path.join(work, "panel.swf")
        shutil.copy2(a.src, orig)
        ff("-export", "script", os.path.join(tmp, "as_a"), orig)
        imp = os.path.join(tmp, "imp", "scripts", "frame_1"); os.makedirs(imp)
        for name, edits, tail in (("DoAction_22", EDITS_22, NEW_FUNCTIONS), ("DoAction_21", EDITS_21, "")):
            text = open(os.path.join(tmp, "as_a", "scripts", "frame_1", name + ".as"), encoding="utf-8").read().replace("\r\n", "\n")
            for old, new in edits:
                if text.count(old) != 1:
                    sys.exit(f"FAIL an edit target in {name} is not there exactly once: {old[:70]!r}")
                text = text.replace(old, new)
            text = text.rstrip("\n") + "\n" + tail
            open(os.path.join(imp, name + ".as"), "w", encoding="utf-8", newline="\n").write(text)
        out_swf = os.path.join(tmp, "panel_patched.swf")
        r = ff("-importScript", orig, out_swf, os.path.join(tmp, "imp", "scripts"))
        if not os.path.isfile(out_swf) or "SEVERE" in r.stdout + r.stderr:
            sys.exit("FAIL import: " + (r.stdout + r.stderr)[-500:])
        ff("-export", "script", os.path.join(tmp, "as_b"), out_swf)
        diffs = []
        for dp, _, fs in os.walk(os.path.join(tmp, "as_a")):
            for f in fs:
                pa = os.path.join(dp, f)
                pb = os.path.join(tmp, "as_b", os.path.relpath(pa, os.path.join(tmp, "as_a")))
                if open(pa, encoding="utf-8").read() != open(pb, encoding="utf-8").read():
                    diffs.append(f)
        if sorted(diffs) != ["DoAction_21.as", "DoAction_22.as"]:
            sys.exit(f"FAIL scripts that differ: {diffs} (only DoAction_21 and 22 may)")
        got = open(os.path.join(tmp, "as_b", "scripts", "frame_1", "DoAction_22.as"), encoding="utf-8").read()
        for needle in ("Equipment.aimPreview = function()", "Equipment.previewTune = function()",
                       'Equipment.say("Item preview")', "Equipment.PREVIEW_FIT_LONG = 0.95", "Equipment.makeLook();"):
            if needle not in got:
                sys.exit(f"FAIL the patched script lacks: {needle}")
        for name, needle in (("DoAction_21", "tab._y = 0;"),):
            if needle not in open(os.path.join(tmp, "as_b", "scripts", "frame_1", name + ".as"), encoding="utf-8").read():
                sys.exit(f"FAIL {name} lacks: {needle}")
        os.makedirs(a.out, exist_ok=True)
        shutil.copy2(out_swf, os.path.join(a.out, "panel.swf"))
        print(f"ok  {os.path.join(a.out, 'panel.swf')}  sha256 {sha(out_swf)}  (only DoAction_21 and 22 differ)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
