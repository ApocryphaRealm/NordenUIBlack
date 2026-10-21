r"""Inventory Reforged for SkyUI 1.2.4 - a larger, centred item preview (Norden UI - Black 1.0.5, 2026-10-21).

Why: Inventory Reforged's item window keeps its 3D item in a box of PREVIEW_HEIGHT = 130 stage units at the top of the
window and asks the plugin (PlacePreview) for an item (130 - 2 * WINDOW_PAD) / screen height tall. Under Norden UI the
window is taller than that box (the space Inventory Reforged keeps for the item card, which Norden's card does not
fill), so the item sits small in the upper part of a tall black panel. This edits ONE function of panel.swf,
Equipment.aimPreview: the preview is aimed at the whole part of the window above its stats - centred horizontally and
vertically in it - and asked for 1.35 times the height that box allowed, capped at the window's width. The window's own
size and layout are unchanged.

The edit is made in p-code (FFDec's AS2 re-importer cannot read the decompiler's own `loop0:` labels, so a source
re-import of this file fails) on a copy of the ORIGINAL file; the original must be Inventory Reforged 1.2.4's panel.swf
(SHA-256 below) and only the aimPreview function changes - the tool re-decompiles the result and checks that.

Inventory Reforged's page allows changing and including any part of the mod without asking (credit: Inventory Reforged
for SkyUI, Nexus 195826), see extras/inventory-reforged/PERMISSIONS.txt. The output stays out of git (*.swf).

    python tools/ir-preview-patch.py [--src <Inventory Reforged 1.2.4 panel.swf>] [--out <folder>]
"""
import argparse, hashlib, os, re, shutil, subprocess, sys, tempfile

FF = r"C:\Program Files (x86)\FFDec\ffdec-cli.exe"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DEFAULT = os.environ.get("NORDEN_IR_PANEL", r"D:\Modlists\Njordlinger\mods\Inventory Reforged for SkyUI\Interface\InventoryReforged\panel.swf")
ZOOM = "1.35"

AREA = '''Push "area"
Push "high"
GetVariable
DefineLocal
Push "window"
GetVariable
Push "high"
GetMember
Push 0
Greater
Not
If locNoArea
Push "area"
Push "window"
GetVariable
Push "high"
GetMember
Push 0
Push "Equipment"
GetVariable
Push "underCard"
CallMethod
Subtract
Push "high"
GetVariable
Push 2
Push "Math"
GetVariable
Push "max"
CallMethod
SetVariable
locNoArea:'''
FRACTION = '''Push 0
Push "Equipment"
GetVariable
Push "windowWide"
CallMethod
Push "area"
GetVariable
Push 2
Push "Math"
GetVariable
Push "min"
CallMethod
Push 2
Push "Equipment"
GetVariable
Push "WINDOW_PAD"
GetMember
Multiply
Subtract
Push %s
Multiply
Push "Stage"''' % ZOOM


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ff(*a):
    r = subprocess.run([FF, *a], capture_output=True, text=True)
    return r


def patch_pcode(s):
    s = s.replace("\r\n", "\n")
    head = 'Push "aimPreview"\nDefineFunction "", 0 {\n'
    assert s.count(head) == 1, "aimPreview definition not found exactly once"
    i = s.index(head)
    j = s.index("\n}\nloc", i)
    body = s[i:j]
    anchor = "loc3e46:DefineLocal\n"
    assert body.count(anchor) == 1, "the 'high' local was not found"
    body = body.replace(anchor, anchor + AREA)
    old_mid = 'Push "middle"\nPush "window"\nGetVariable\nPush "_y"\nGetMember\nPush "high"\nGetVariable\nPush 2\nDivide'
    assert body.count(old_mid) == 1, "the middle-y expression was not found"
    body = body.replace(old_mid, old_mid.replace('Push "high"\nGetVariable', 'Push "area"\nGetVariable'))
    old_f = 'Push "high"\nGetVariable\nPush 2\nPush "Equipment"\nGetVariable\nPush "WINDOW_PAD"\nGetMember\nMultiply\nSubtract\nPush "Stage"'
    assert body.count(old_f) == 1, "the fraction expression was not found"
    body = body.replace(old_f, FRACTION)
    return s[:i] + body + s[j:]


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
        shutil.copy2(a.src, os.path.join(work, "panel.swf"))
        pc = os.path.join(tmp, "pc")
        ff("-format", "script:pcode", "-export", "script", pc, os.path.join(work, "panel.swf"))
        f18 = os.path.join(pc, "scripts", "frame_1", "DoAction_18.pcode")
        imp = os.path.join(tmp, "imp", "scripts", "frame_1"); os.makedirs(imp)
        open(os.path.join(imp, "DoAction_18.pcode"), "w", encoding="utf-8", newline="\n").write(patch_pcode(open(f18, encoding="utf-8").read()))
        out_swf = os.path.join(tmp, "panel_patched.swf")
        r = ff("-importScript", os.path.join(work, "panel.swf"), out_swf, os.path.join(tmp, "imp", "scripts"))
        if not os.path.isfile(out_swf):
            sys.exit("FAIL import: " + (r.stdout + r.stderr)[-400:])
        # read the effect back: re-decompile both and compare every script
        for tag, swf in (("a", os.path.join(work, "panel.swf")), ("b", out_swf)):
            ff("-export", "script", os.path.join(tmp, "as_" + tag), swf)
        diffs = []
        for dp, _, fs in os.walk(os.path.join(tmp, "as_a")):
            for f in fs:
                pa = os.path.join(dp, f); pb = os.path.join(tmp, "as_b", os.path.relpath(pa, os.path.join(tmp, "as_a")))
                if open(pa, encoding="utf-8").read() != open(pb, encoding="utf-8").read():
                    diffs.append(f)
        if diffs != ["DoAction_18.as"]:
            sys.exit(f"FAIL scripts that differ: {diffs} (only DoAction_18.as may)")
        text = open(os.path.join(tmp, "as_b", "scripts", "frame_1", "DoAction_18.as"), encoding="utf-8").read()
        for needle in ("area = Math.max(high,window.high - Equipment.underCard());",
                       "* " + ZOOM + " / Stage.visibleRect.height", "window._y + area / 2"):
            if needle not in text:
                sys.exit(f"FAIL the patched aimPreview lacks: {needle}")
        os.makedirs(a.out, exist_ok=True)
        shutil.copy2(out_swf, os.path.join(a.out, "panel.swf"))
        print(f"ok  {os.path.join(a.out, 'panel.swf')}  sha256 {sha(out_swf)}  (only Equipment.aimPreview differs)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
