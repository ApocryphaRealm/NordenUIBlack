r"""Inventory Reforged for SkyUI 1.2.4, 1.3.0 and 1.4.0 - a larger, centred, fitted item preview with its own size and place
controls, and the skin's own item card left alone (Norden UI - Black 1.1.0, 2026-10-22).

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

The file must be Inventory Reforged 1.2.4's, 1.3.0's or 1.4.0's panel.swf (SHA-256 in extras/inventory-reforged/panel-<version>.sha256,
found by hash); the result is re-decompiled and the tool refuses it unless only the drawer's and the popup's scripts differ
(1.4.0: DoAction_22 and DoAction_23, plus DoAction_28 for the colour pass - see COLOUR_EDITS) and the edits are all there,
the colour fills read back out of the rebuilt file. Item card: Inventory Reforged takes the menu's own item card (Norden's: itemcard.swf and its
deardiary_dm\\inventory\\itemcard_N_BG.swf art) into its window - it hides the card's background art and Stolen text, adds a
kind line and shifts the card's parts, rescales it to the window width, moves it with the window (and, from 1.3.0, hides it
whenever its window is hidden) and re-breaks its effect text. This tool redefines the functions that do that without those
lines, so Norden's card shows as Norden made it, in Norden's place, all the time.
Inventory Reforged's page allows changing and including any part of the mod without asking (credit: Inventory
Reforged for SkyUI, Nexus 195826), see extras/inventory-reforged/PERMISSIONS.txt. The output stays out of git (*.swf).

    python tools/ir-preview-patch.py [--src <Inventory Reforged panel.swf>] [--out <folder>]   (output: <folder>\\<version>\\panel.swf)
"""
import argparse, hashlib, os, shutil, subprocess, sys, tempfile

# FFDec through its jar with a capped heap: ffdec-cli.exe gives Java a heap the size of the machine's RAM and one
# -swf2xml pass reached 11.7 GB beside a running game (2026-10-23). FFDEC_HEAP overrides the 4g cap.
FF = ["java", "-Xmx" + os.environ.get("FFDEC_HEAP", "4g"), "-jar", r"C:\Program Files (x86)\FFDec\ffdec-cli.jar"]
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The scripts of panel.swf are numbered in the order of the source's parts; 1.4.0 added parts, so the numbers moved.
# window = the item window (36-window.as), hero = the Character drawer (38-hero.as), look = the settings popup (38-look.as)
VERSIONS = {
    "1.2.4": {"window": "DoAction_18", "hero": "DoAction_21", "look": "DoAction_22"},
    "1.3.0": {"window": "DoAction_18", "hero": "DoAction_21", "look": "DoAction_22"},
    "1.4.0": {"window": "DoAction_19", "hero": "DoAction_22", "look": "DoAction_23", "colours": True},
}
# a version whose panel.swf is not on disk is read from its archive (read only, never executed)
SRC_ZIPS = {
    "1.3.0": r"D:\Claude output\.MD\backups\quarantine\InventoryReforged-1.3.0\InventoryReforged 1.3.0 195826.zip",
    "1.4.0": r"D:\Claude output\.MD\backups\quarantine\InventoryReforged-1.4.0\InventoryReforged 1.4.0 195826.zip",
}
SRC_DEFAULTS = {
    "1.2.4": os.environ.get("NORDEN_IR_PANEL_124", r"D:\Modlists\Njordlinger\mods\Inventory Reforged for SkyUI\Interface\InventoryReforged\panel.swf"),
    "1.3.0": os.environ.get("NORDEN_IR_PANEL_130", ""),
    "1.4.0": os.environ.get("NORDEN_IR_PANEL_140", ""),
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
Equipment.FIXED_FIT = 0.94;
Equipment.aimPreview = function()
{
   var window = Equipment.window;
   var high = window.preview != undefined ? window.preview : Equipment.PREVIEW_HEIGHT;
   var area = high;
   var wide = Equipment.windowWide();
   var tune = Equipment.previewTune();
   var entry = Equipment.windowEntry();
   var fit = entry != undefined && (entry.formType == Equipment.WEAPON || entry.formType == Equipment.AMMO) ? Equipment.PREVIEW_FIT_LONG : Equipment.PREVIEW_FIT;
   var fixed = Equipment.anchorSlot == undefined && Equipment.fixedOn();
   var middle;
   var size;
   var room;
   var across;
   var upward;
   var reach;
   if(window.high > 0)
   {
      area = Math.max(high,window.high - Equipment.underCard());
   }
   across = tune.across * wide;
   upward = tune.upward * area;
   size = Math.min(area,wide) * fit * tune.size;
   room = size;
   if(fixed)
   {
      room = Math.min(size,Math.max(0,Math.min(wide,area) - 2 * Equipment.WINDOW_PAD) * Equipment.FIXED_FIT);
      size = room;
      reach = Math.max(0,(wide - room) / 2 - Equipment.WINDOW_PAD);
      across = Math.max(- reach,Math.min(reach,across));
      reach = Math.max(0,(area - room) / 2 - Equipment.WINDOW_PAD);
      upward = Math.max(- reach,Math.min(reach,upward));
   }
   middle = Equipment.share(window._x + wide / 2 + across,window._y + area / 2 - upward);
   size /= Stage.visibleRect.height;
   room /= Stage.visibleRect.height;
   if(Equipment.plugin() != undefined && !Equipment.inspecting)
   {
      Equipment.plugin().PlacePreview(middle.x,middle.y,size);
      if(fixed)
      {
         skse.Log("PANELTEST fixed preview: window " + Math.round(wide) + " x " + Math.round(area) + " (model area) at " + Math.round(window._x) + "," + Math.round(window._y) + ", size " + Math.round(size * Stage.visibleRect.height) + ", room " + Math.round(room * Stage.visibleRect.height) + " stage units, offset " + Math.round(across) + "," + Math.round(upward));
      }
   }
};
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
Equipment.FIXED_HEAD = 24;
Equipment.FIXED_NAME_ABOVE = 26;
Equipment.FIXED_CARD_GAP = 24;
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
   var nameTop;
   var room;
   lists.panelContainer.localToGlobal(corner);
   Equipment.toPanel(corner);
   lists.itemList.localToGlobal(rows);
   Equipment.toPanel(rows);
   left = corner.x + 6;
   top = rows.y - Equipment.FIXED_HEAD;
   right = Equipment.rowsEdge().right - Equipment.WINDOW_INSET * Equipment.squash;
   bottom = Equipment.barTop() - Equipment.MARGIN;
   if(name != undefined)
   {
      nameTop = Equipment.partBox(name,Equipment.under).yMin;
      if(nameTop > top + 2 * Equipment.PREVIEW_LEAST && nameTop < bottom + Equipment.FIXED_NAME_ABOVE + Equipment.FIXED_CARD_GAP)
      {
         bottom = nameTop - Equipment.FIXED_NAME_ABOVE - Equipment.FIXED_CARD_GAP;
      }
   }
   room = bottom - top;
   if(right - left < 100 || room < 100)
   {
      skse.Log("PANELTEST fixed: frame not measured, left " + Math.round(left) + " right " + Math.round(right) + " top " + Math.round(top) + " bottom " + Math.round(bottom) + " - window left as it was");
      return undefined;
   }
   window.preview = Math.max(30,room - under);
   Equipment.drawWindow(Math.min(room,window.preview + under));
   window.above = false;
   window.clamped = false;
   window._x = Math.max(left,right - wideP);
   window._y = top;
   window.rowEdge = window._y;
   window.rowMiddle = window._y + window.high / 2;
   skse.Log("PANELTEST fixed: frame x " + Math.round(left) + ".." + Math.round(right) + " y " + Math.round(top) + ".." + Math.round(bottom) + " (list origin y " + Math.round(rows.y) + ", name text top " + (nameTop != undefined ? Math.round(nameTop) : "none") + "), room " + Math.round(room) + ", stats " + Math.round(under) + ", window " + Math.round(wideP) + " x " + Math.round(window.high) + " at " + Math.round(window._x) + "," + Math.round(window._y) + " (locked over the list's right side, full list height)");
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
# 1.4.0 lets the item window wear the card's own frame (the card's background art stretched to the window) and grows the
# card's frame for chests; with Norden's card left alone the window keeps its own plain sheet and adds no frame edge
FRAME_FUNCTIONS = "Equipment.frameWindow = function()\n{\n   return false;\n};\nEquipment.frameEdge = function()\n{\n   return 0;\n};\n"
AIM_FOUR = ("PlacePreview(middle.x,middle.y,size);", "PlacePreview(middle.x,middle.y,size,room);")
CARD_FUNCTIONS = [
    ("sizeWindow", [("   card._yscale = window.wide / Equipment.cardWidth() * 100;\n", "")]),
    ("windowUnits", [("   card._xscale = card._yscale * across / Equipment.squash;\n", "")]),
    ("placeWindow", [("   card._x = at.x;\n   card._y = at.y;\n", ""),
                     ("   menu.itemCard.background._visible = false;\n   menu.itemCard.StolenTextInstance._visible = false;\n", "?"),
                     ("      menu.itemCard.background._visible = false;\n      menu.itemCard.StolenTextInstance._visible = false;\n", "?"),
                     ("   Equipment.layKind();\n", ""),
                     ("   else\n   {\n      rowTop = {x:0,y:row._y};", "   else if(Equipment.fixedOn())\n   {\n      Equipment.placeFixed();\n   }\n   else\n   {\n      rowTop = {x:0,y:row._y};")]),
    ("cardSpan", None),
    # 1.3.0 shows the card only while its window is up; the skin's card is always up
    ("showWindow", [("   Equipment.menu.itemCard._parent._visible = Equipment.window._visible;\n", "?")]),
    ("keepFrameHidden", "Equipment.keepFrameHidden = function()\n{\n};\n"),
    ("effectLines", "Equipment.effectLines = function(text)\n{\n   return text;\n};\n"),
]

# Norden Black panel colours (2026-10-23, the owner: the Inventory Reforged panel "isn't black enough"). Inventory
# Reforged draws its panels itself, in ActionScript: the sheets of the settings popup, the Character drawer, the context
# menu, the tooltip and the junk question are a #1A1A1A-to-black gradient at 84-96 percent, the slot frames a #2C2C2C-to-
# black gradient at 45-72 percent, its buttons #1A1A1A at 80 percent and its tabs and strips black at 40-82 percent, so
# under Norden UI - Black they read grey and see-through beside the black item list. Every one of those fills becomes
# black, opaque (Norden Black's item list is black, 90 percent, its solid parts 100; Inventory Reforged's own item window
# sheet was already black at 100). Lines, accents, the lit (accent) tints, text and icons are not touched.
# (function, old, new) - the function is found in whichever script of panel.swf defines it; one defined before the
# settings popup's script is copied into that script with the edit (a later tag, so the copy wins), one defined in the
# drawer's or the popup's script is edited where it is, and one defined after the popup's script is edited in its own
# script, which is then the third script allowed to differ.
COLOUR_EDITS = [
    ("panelBox", 'clip.beginGradientFill("linear",[1710618,0],[shade,shade + 8 > 100 ? 100 : shade + 8],[0,255],turn);',
     "clip.beginFill(0,100);"),
    ("drawFrame", 'frame.beginGradientFill("linear",[2894892,0],[filled ? 62 : 45,filled ? 72 : 55],[0,255],turn);',
     "frame.beginFill(0,100);"),
    ("drawSheet", 'sheet.beginFill(Equipment.inkOf("sheet"),popup && !Equipment.paper ? 96 : 100);',
     'sheet.beginFill(Equipment.inkOf("sheet"),100);'),
    ("drawJunkAskButton", "button.beginFill(button.lit ? Equipment.GOLD : 1710618,over ? 30 : (button.lit ? 15 : 80));",
     "button.beginFill(button.lit ? Equipment.GOLD : 0,button.lit ? (over ? 30 : 15) : 100);"),
    ("drawAction", "look.beginFill(button.lit ? Equipment.GOLD : 1710618,button.lit ? 25 : 80);",
     "look.beginFill(button.lit ? Equipment.GOLD : 0,button.lit ? 25 : 100);"),
    ("drawLookReset", "look.beginFill(button.lit ? Equipment.GOLD : 1710618,button.lit ? 25 : 80);",
     "look.beginFill(button.lit ? Equipment.GOLD : 0,button.lit ? 25 : 100);"),
    ("drawTab", "tab.beginFill(0,70);", "tab.beginFill(0,100);"),
    ("placePieces", "strip.clip.beginFill(0,82);", "strip.clip.beginFill(0,100);"),
    ("drawPiecesControl", "control.look.beginFill(control.lit && live ? Equipment.GOLD : 0,control.lit && live ? 22 : 40);",
     "control.look.beginFill(control.lit && live ? Equipment.GOLD : 0,control.lit && live ? 22 : 100);"),
    ("drawHeroTab", "tab.look.beginFill(0,lit ? 62 : 42);", "tab.look.beginFill(0,100);"),
    ("drawCompanionTab", "tab.look.beginFill(0,tab.shown ? 70 : (tab.lit ? 62 : 42));", "tab.look.beginFill(0,100);"),
    ("drawLookButton", "Equipment.buttonFill(button.look,lit ? 62 : 42);", "Equipment.buttonFill(button.look,100);"),
    ("drawLookArrow", "look.beginFill(lit ? Equipment.GOLD : 0,lit ? 22 : 40);", "look.beginFill(lit ? Equipment.GOLD : 0,lit ? 22 : 100);"),
]


def script_order(name):
    return 1 if name == "DoAction" else int(name.split("_")[1])


def colour_pass(texts, cfg):
    """texts: script name -> decompiled text. Returns (text appended to the popup's script, {script: [(old, new)]})."""
    look_at = script_order(cfg["look"])
    tail, in_place = "", {}
    for fn, old, new in COLOUR_EDITS:
        head = "Equipment." + fn + " = function("
        homes = [n for n, t in texts.items() if head in t]
        if len(homes) != 1 or texts[homes[0]].count(head) != 1:
            sys.exit(f"FAIL colour edit: {fn} is defined in {homes} (want exactly one script, once)")
        home = homes[0]
        src = texts[home]
        i = src.index(head)
        j = src.index("\n};\n", i) + 4
        body = src[i:j]
        if body.count(old) != 1:
            sys.exit(f"FAIL colour edit: {fn} ({home}) lacks exactly one {old[:60]!r}")
        if script_order(home) < look_at and home != cfg["hero"]:
            tail += body.replace(old, new)
        else:
            in_place.setdefault(home, []).append((body, body.replace(old, new)))
    return tail, in_place


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
    return subprocess.run([*FF, *a], capture_output=True, text=True)


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
    cfg = VERSIONS[version]
    want = open(os.path.join(HERE, "extras", "inventory-reforged", f"panel-{version}.sha256")).read().split()[0]
    if not a.src and version in SRC_ZIPS and os.path.isfile(SRC_ZIPS[version]):
        import zipfile
        z = zipfile.ZipFile(SRC_ZIPS[version])
        data = z.read("core/Interface/InventoryReforged/panel.swf")
        a.src = os.path.join(tempfile.mkdtemp(prefix="irsrc-"), "panel.swf")
        open(a.src, "wb").write(data)
    if not a.src or not os.path.isfile(a.src):
        sys.exit(f"FAIL panel.swf of Inventory Reforged {version} not found: {a.src or '(no path, no archive)'}")
    if sha(a.src) != want:
        sys.exit(f"FAIL {a.src} is not Inventory Reforged {version}'s panel.swf (SHA-256 {sha(a.src)} != {want})")
    tmp = tempfile.mkdtemp(prefix="irpatch-")
    try:
        work = os.path.join(tmp, "src"); os.makedirs(work)
        orig = os.path.join(work, "panel.swf")
        shutil.copy2(a.src, orig)
        ff("-export", "script", os.path.join(tmp, "as_a"), orig)
        imp = os.path.join(tmp, "imp", "scripts", "frame_1"); os.makedirs(imp)
        window_text = open(os.path.join(tmp, "as_a", "scripts", "frame_1", cfg["window"] + ".as"), encoding="utf-8").read().replace("\r\n", "\n")
        four = "Equipment.frameWindow = function(" in window_text
        frame_dir = os.path.join(tmp, "as_a", "scripts", "frame_1")
        texts = {f[:-3]: open(os.path.join(frame_dir, f), encoding="utf-8").read().replace("\r\n", "\n")
                 for f in os.listdir(frame_dir) if f.endswith(".as")}
        # the colour pass is written against 1.4.0's code (the one shipped); 1.2.4 and 1.3.0 build without it
        colour_tail, colour_in_place = colour_pass(texts, cfg) if cfg.get("colours") else ("", {})
        changed = [cfg["hero"], cfg["look"]] + sorted(n for n in colour_in_place if n not in (cfg["hero"], cfg["look"]))
        jobs = [(cfg["look"], colour_in_place.get(cfg["look"], []) + EDITS_22, NEW_FUNCTIONS),
                (cfg["hero"], colour_in_place.get(cfg["hero"], []) + EDITS_21, "")]
        jobs += [(n, colour_in_place[n], "") for n in changed[2:]]
        for name, edits, tail in jobs:
            text = texts[name]
            for old, new in edits:
                if text.count(old) != 1:
                    sys.exit(f"FAIL an edit target in {name} is not there exactly once: {old[:70]!r}")
                text = text.replace(old, new)
            if name == cfg["look"]:
                if four:
                    assert tail.count(AIM_FOUR[0]) == 1
                    tail = tail.replace(AIM_FOUR[0], AIM_FOUR[1])
                tail = tail + card_functions(window_text) + (FRAME_FUNCTIONS if four else "") + colour_tail
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
        if sorted(diffs) != sorted(n + ".as" for n in changed):
            sys.exit(f"FAIL scripts that differ: {diffs} (only {changed} may)")
        got = open(os.path.join(tmp, "as_b", "scripts", "frame_1", cfg["look"] + ".as"), encoding="utf-8").read()
        for needle in ("Equipment.aimPreview = function()", "Equipment.previewTune = function()",
                       'Equipment.say("Item preview")', "Equipment.PREVIEW_FIT_LONG = 0.95", "Equipment.makeLook();"):
            if needle not in got:
                sys.exit(f"FAIL the patched script lacks: {needle}")
        for name, needle in ((cfg["hero"], "tab._y = 0;"), (cfg["look"], "Equipment.placeFixed = function()"), (cfg["look"], "Equipment.CARD_ROOM"),
                             (cfg["look"], "Equipment.keepFrameHidden = function()"), (cfg["look"], "return text;")):
            if needle not in open(os.path.join(tmp, "as_b", "scripts", "frame_1", name + ".as"), encoding="utf-8").read():
                sys.exit(f"FAIL {name} lacks: {needle}")
        # read the colour effect back out of the rebuilt file: the LAST definition of each function (the one that wins)
        # carries the new fill and not the old one
        rebuilt = {n: open(os.path.join(tmp, "as_b", "scripts", "frame_1", n + ".as"), encoding="utf-8").read().replace("\r\n", "\n")
                   for n in texts}
        for fn, old, new in (COLOUR_EDITS if cfg.get("colours") else []):
            head = "Equipment." + fn + " = function("
            last = max((n for n in rebuilt if head in rebuilt[n]), key=script_order)
            body = rebuilt[last][rebuilt[last].rindex(head):]
            body = body[:body.index("\n};\n") + 4]
            if new not in body or old in body:
                sys.exit(f"FAIL colour edit did not take: {fn} in {last}")
        os.makedirs(a.out, exist_ok=True)
        shutil.copy2(out_swf, os.path.join(a.out, "panel.swf"))
        print(f"ok  IR {version}  {os.path.join(a.out, 'panel.swf')}  sha256 {sha(out_swf)}  (only {', '.join(changed)} differ)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
