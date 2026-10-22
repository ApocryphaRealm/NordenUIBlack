r"""Inventory Reforged for SkyUI 1.2.4 and 1.3.0 - a larger, centred, fitted item preview with its own size and place
controls, and the skin's own item card left alone (Norden UI - Black 1.0.5, 2026-10-21).

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

The file must be Inventory Reforged 1.2.4's or 1.3.0's panel.swf (SHA-256 in extras/inventory-reforged/panel-<version>.sha256,
found by hash); the result is re-decompiled and the tool refuses it unless only DoAction_21.as and DoAction_22.as differ and
the edits are all there. Item card: Inventory Reforged takes the menu's own item card (Norden's: itemcard.swf and its
deardiary_dm\\inventory\\itemcard_N_BG.swf art) into its window - it hides the card's background art and Stolen text, adds a
kind line and shifts the card's parts, rescales it to the window width, moves it with the window (and, from 1.3.0, hides it
whenever its window is hidden) and re-breaks its effect text. This tool redefines the functions that do that without those
lines, so Norden's card shows as Norden made it, in Norden's place, all the time.
Inventory Reforged's page allows changing and including any part of the mod without asking (credit: Inventory
Reforged for SkyUI, Nexus 195826), see extras/inventory-reforged/PERMISSIONS.txt. The output stays out of git (*.swf).

    python tools/ir-preview-patch.py [--src <Inventory Reforged panel.swf>] [--out <folder>]   (output: <folder>\\<version>\\panel.swf)
"""
import argparse, hashlib, os, shutil, subprocess, sys, tempfile

FF = r"C:\Program Files (x86)\FFDec\ffdec-cli.exe"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DEFAULTS = {
    "1.2.4": os.environ.get("NORDEN_IR_PANEL_124", r"D:\Modlists\Njordlinger\mods\Inventory Reforged for SkyUI\Interface\InventoryReforged\panel.swf"),
    "1.3.0": os.environ.get("NORDEN_IR_PANEL_130", r"D:\Claude output\6. current wip mods\InventoryReforgedDiag\upstream\core\Interface\InventoryReforged\panel.swf"),
}

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
Equipment.FIXED_PREVIEW = 260;
Equipment.FIXED_BASE = 0.8;
Equipment.FIXED_STEP = 0.002;
Equipment.LOOK_STEPS.fixX = {id:"fTurnSpeed:Doll",step:10,least:0,most:100};
Equipment.LOOK_STEPS.fixY = {id:"fTurnSpeed:Doll",step:10,least:0,most:100};
Equipment.fixedRead = function()
{
   var v = Equipment.number(Equipment.settings.turnSpeed);
   var fixed = Equipment.settings.doll != true && v > Equipment.FIXED_BASE - 0.01 && v < Equipment.FIXED_BASE + 0.25;
   var n = fixed ? Math.round((v - Equipment.FIXED_BASE) / Equipment.FIXED_STEP) : 115;
   var across = Math.floor(n / 11);
   Equipment.settings.fixOn = fixed;
   Equipment.settings.fixX = across * 10;
   Equipment.settings.fixY = (n - across * 11) * 10;
};
Equipment.fixedOn = function()
{
   Equipment.fixedRead();
   return Equipment.settings.fixOn == true;
};
Equipment.fixedWrite = function()
{
   var v = Equipment.FIXED_BASE + Equipment.FIXED_STEP * (Math.round(Equipment.settings.fixX / 10) * 11 + Math.round(Equipment.settings.fixY / 10));
   Equipment.settings.turnSpeed = v;
   Equipment.tellSetting("fTurnSpeed:Doll",v);
   Equipment.fixedRead();
};
Equipment.setFixed = function(on)
{
   if(on)
   {
      Equipment.settings.fixX = 100;
      Equipment.settings.fixY = 50;
      Equipment.fixedWrite();
   }
   else
   {
      Equipment.settings.turnSpeed = 0.5;
      Equipment.tellSetting("fTurnSpeed:Doll",0.5);
      Equipment.fixedRead();
   }
};
Equipment.fixedSync = function()
{
   var v = Equipment.number(Equipment.settings.turnSpeed);
   if(Equipment.settings.doll == true && v > Equipment.FIXED_BASE - 0.01 && v < Equipment.FIXED_BASE + 0.25)
   {
      Equipment.settings.turnSpeed = 0.5;
      Equipment.tellSetting("fTurnSpeed:Doll",0.5);
   }
   Equipment.fixedRead();
};
Equipment.placeFixed = function()
{
   var window = Equipment.window;
   var lists = Equipment.menu.inventoryLists;
   var corner = {x:0,y:0};
   var rows = {x:0,y:0};
   var name = Equipment.menu.itemCard.ItemText;
   var under = Equipment.underCard();
   var wideP = Equipment.windowWide();
   var left;
   var right;
   var top;
   var bottom;
   var cardTop;
   var room;
   lists.panelContainer.localToGlobal(corner);
   Equipment.toPanel(corner);
   lists.itemList.localToGlobal(rows);
   Equipment.toPanel(rows);
   left = corner.x + 2;
   top = rows.y + 2;
   right = Equipment.rowsEdge().right - 2;
   bottom = Equipment.barTop() - Equipment.MARGIN;
   if(name != undefined)
   {
      cardTop = Equipment.partBox(name,Equipment.under).yMin - 6;
      if(cardTop > top + 2 * Equipment.PREVIEW_LEAST && cardTop < bottom)
      {
         bottom = cardTop;
      }
   }
   room = bottom - top;
   if(right - left < 100 || room < 100)
   {
      skse.Log("PANELTEST fixed: frame not measured, left " + Math.round(left) + " right " + Math.round(right) + " top " + Math.round(top) + " bottom " + Math.round(bottom) + " - window left as it was");
      return undefined;
   }
   window.preview = Math.max(30,Math.min(Equipment.FIXED_PREVIEW,room - under));
   Equipment.drawWindow(window.preview + under);
   window.above = false;
   window.clamped = window.high > room || wideP > right - left;
   window._x = Math.max(left,Math.min(right - wideP,left + (right - left - wideP) * Equipment.settings.fixX / 100));
   window._y = Math.max(top,Math.min(bottom - window.high,top + (room - window.high) * Equipment.settings.fixY / 100));
   window.rowEdge = window._y;
   window.rowMiddle = window._y + window.high / 2;
   skse.Log("PANELTEST fixed: frame x " + Math.round(left) + ".." + Math.round(right) + " y " + Math.round(top) + ".." + Math.round(bottom) + " (card text top " + (cardTop != undefined ? Math.round(cardTop) : "none") + "), room " + Math.round(room) + ", stats " + Math.round(under) + ", window " + Math.round(wideP) + " x " + Math.round(window.high) + " at " + Math.round(window._x) + "," + Math.round(window._y) + " (sideways " + Equipment.settings.fixX + ", up and down " + Equipment.settings.fixY + ")");
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
      Equipment.fixedSync();
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
EDITS_22 += [
    ("""   var sheet = Equipment.look;
   var pad = Equipment.LOOK_PAD;
   var wide = Equipment.LOOK_WIDE;
""", """   var sheet = Equipment.look;
   var pad = Equipment.LOOK_PAD;
   var wide = Equipment.LOOK_WIDE;
   Equipment.fixedRead();
"""),
    ("""   y += Equipment.lookHead(sheet,Equipment.say("Item window"),pad,y,inner);
""", """   y += Equipment.lookHead(sheet,Equipment.say("Item window"),pad,y,inner);
   if(Equipment.settings.doll != true)
   {
      y += Equipment.lookCheck(sheet,"fixed",Equipment.say("Fixed place"),undefined,pad,y,inner,Equipment.LOOK_LINE);
      if(Equipment.settings.fixOn)
      {
         y += Equipment.lookStepper(sheet,"fixX",Equipment.say("Sideways"),"across",pad,y,inner);
         y += Equipment.lookStepper(sheet,"fixY",Equipment.say("Up and down"),"upward",pad,y,inner);
      }
   }
"""),
    ("""      case "listWidth":
         return [""", """      case "fixX":
         return value <= 0 ? Equipment.say("Left") : (value >= 100 ? Equipment.say("Right") : Equipment.say("#%",value));
      case "fixY":
         return value <= 0 ? Equipment.say("Top") : (value >= 100 ? Equipment.say("Bottom") : Equipment.say("#%",value));
      case "listWidth":
         return ["""),
    ("""Equipment.lookOn = function(key)
{
   if(key == "doll")""", """Equipment.lookOn = function(key)
{
   if(key == "fixed")
   {
      return Equipment.fixedOn();
   }
   if(key == "doll")"""),
    ("""   else
   {
      Equipment.flipSlot(Equipment.SLOTS[Number(key.substr(4))]);
   }
""", """   else if(key == "fixed")
   {
      Equipment.setFixed(!Equipment.fixedOn());
      Equipment.makeLook();
      Equipment.showWindow();
   }
   else
   {
      Equipment.flipSlot(Equipment.SLOTS[Number(key.substr(4))]);
   }
"""),
    ("""   Equipment.changeSetting(key,Equipment.LOOK_STEPS[key].id,value);
   if(key == "listWidth")""", """   if(key == "fixX" || key == "fixY")
   {
      Equipment.settings[key] = value;
      Equipment.fixedWrite();
      Equipment.showWindow();
      Equipment.showLookValues();
      gfx.io.GameDelegate.call("PlaySound",["UIMenuFocus"]);
      return undefined;
   }
   Equipment.changeSetting(key,Equipment.LOOK_STEPS[key].id,value);
   if(key == "listWidth")"""),
    ("""   var quiet = line.key != "listWidth" && Equipment.settings.doll != true;
""", """   var quiet = false;
"""),
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


# Functions of DoAction_18 that move or rescale the SkyUI/Norden item card with Inventory Reforged's window. They are
# copied from the original with those lines taken out and redefined in DoAction_22 (a later tag, so the new definition
# wins; DoAction_18 itself cannot be re-imported - its decompiled loops carry labels the compiler rejects).
# The card then stays where the skin puts it (Norden's Slimventory layout: below the item list) at its own size, and the
# window reserves a fixed room (CARD_ROOM stage units) where the card used to be, which the item preview now uses.
CARD_ROOM = "150"
CARD_FUNCTIONS = [
    ("sizeWindow", [("   card._yscale = window.wide / Equipment.cardWidth() * 100;\n", "")]),
    ("windowUnits", [("   card._xscale = card._yscale * across / Equipment.squash;\n", "")]),
    ("placeWindow", [("   card._x = at.x;\n   card._y = at.y;\n", ""),
                     ("   menu.itemCard.background._visible = false;\n   menu.itemCard.StolenTextInstance._visible = false;\n", ""),
                     ("   Equipment.layKind();\n", ""),
                     ("   else\n   {\n      rowTop = {x:0,y:row._y};", "   else if(Equipment.fixedOn())\n   {\n      Equipment.placeFixed();\n   }\n   else\n   {\n      rowTop = {x:0,y:row._y};")]),
    ("cardSpan", None),
    # 1.3.0 shows the card only while its window is up; the skin's card is always up
    ("showWindow", [("   Equipment.menu.itemCard._parent._visible = Equipment.window._visible;\n", "?")]),
    ("keepFrameHidden", "Equipment.keepFrameHidden = function()\n{\n};\n"),
    ("effectLines", "Equipment.effectLines = function(text)\n{\n   return text;\n};\n"),
]

def card_functions(source):
    out = ""
    for name, edits in CARD_FUNCTIONS:
        head = "Equipment." + name + " = function("
        i = source.index(head)
        j = source.index("\n};\n", i) + 4
        body = source[i:j]
        if edits is None:
            body = "Equipment.cardSpan = function()\n{\n   return {top:0,bottom:Equipment.anchorSlot == undefined && Equipment.fixedOn() ? 0 : Equipment.CARD_ROOM};\n};\n"
        elif isinstance(edits, str):
            body = edits
        else:
            for old, new in edits:
                optional = new == "?"
                if optional:
                    new = ""
                if body.count(old) != 1 and not (optional and body.count(old) == 0):
                    sys.exit(f"FAIL {name}: edit target not there exactly once: {old[:60]!r}")
                body = body.replace(old, new)
        out += body
    return "Equipment.CARD_ROOM = " + CARD_ROOM + ";\n" + out


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ff(*a):
    return subprocess.run([FF, *a], capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="all", help="1.2.4, 1.3.0 or all")
    ap.add_argument("--src", default=None, help="panel.swf of the chosen version (not with 'all')")
    ap.add_argument("--out", default=os.path.join(HERE, "build", "ir-panel"))
    a = ap.parse_args()
    versions = list(SRC_DEFAULTS) if a.version == "all" else [a.version]
    if a.src and len(versions) != 1:
        sys.exit("FAIL --src needs one --version")
    for v in versions:
        patch_one(v, a.src or SRC_DEFAULTS[v], os.path.join(a.out, v, "Interface", "InventoryReforged"))


def patch_one(version, src, outdir):
    class a:
        pass
    a.src, a.out = src, outdir
    if not os.path.isfile(a.src):
        sys.exit(f"FAIL panel.swf not found: {a.src}")
    want = open(os.path.join(HERE, "extras", "inventory-reforged", f"panel-{version}.sha256")).read().split()[0]
    if sha(a.src) != want:
        sys.exit(f"FAIL {a.src} is not Inventory Reforged {version}'s panel.swf (SHA-256 {sha(a.src)} != {want})")
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
            if name == "DoAction_22":
                tail = tail + card_functions(open(os.path.join(tmp, "as_a", "scripts", "frame_1", "DoAction_18.as"), encoding="utf-8").read().replace("\r\n", "\n"))
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
        for name, needle in (("DoAction_21", "tab._y = 0;"), ("DoAction_22", "Equipment.placeFixed = function()"), ("DoAction_22", "Equipment.CARD_ROOM"),
                             ("DoAction_22", "Equipment.keepFrameHidden = function()"), ("DoAction_22", "return text;")):
            if needle not in open(os.path.join(tmp, "as_b", "scripts", "frame_1", name + ".as"), encoding="utf-8").read():
                sys.exit(f"FAIL {name} lacks: {needle}")
        os.makedirs(a.out, exist_ok=True)
        shutil.copy2(out_swf, os.path.join(a.out, "panel.swf"))
        print(f"ok  IR {version}  {os.path.join(a.out, 'panel.swf')}  sha256 {sha(out_swf)}  (only DoAction_21 and 22 differ)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
