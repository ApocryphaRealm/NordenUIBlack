r"""HUD Position Manager widgets in Norden UI - Black's look (2026-10-04, the owner: "lets make it work with norden black
bc we own the file, we cant ship norden art with hpm", then: "make it a FOMOD option if they use HUD Position Manager").

HPM builds its own HUD widgets (breath, casting, shout, detection, level, gold, carry weight, game time) and loads each
from Interface\HUDPositionManager\widgets\<name>.swf, driving named clips - the CLIP CONTRACT:
    Frame   the art behind everything (its size is the widget's size; the art's top-left sits at 0,0)
    Fill    a meter's filled part, registration on its LEFT edge; HPM sets its _xscale 0..100
    Icon    an optional symbol
    Value   an optional text field HPM writes with .text
This tool grafts Norden UI - Black's OWN widget art (the installed, already-recoloured files) into that contract, file
by file: every definition tag of the source is copied unchanged (shapes, bitmaps, sprites, its text fields and its
gfxfontlib font import), the ActionScript is dropped, every sprite is cut to its first frame, and a new root display
list places the pieces under the contract's names. A Fill is always a NEW wrapper sprite at scale 1 holding Norden's
bar at its own scale, offset so the bar's left edge is the wrapper's origin - HPM's _xscale then empties it from the
left without erasing Norden's scale. Norden's mask and gloss over the bar are kept at their depths.

No art lives in the repository: the output goes to build\hpm-widgets (git-ignored) and into the FOMOD's optional
"HUD Position Manager widgets" folder.

    python tools/hpm-widgets.py [--src <Norden UI Black Interface folder>] [--out <folder>]
"""
import argparse
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swftags as T

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("NORDEN_BLACK_INTERFACE", r"D:\modlists\Njordlinger\mods\Norden UI Black\Interface")
OUT = os.path.join(HERE, "build", "hpm-widgets", "Interface", "HUDPositionManager", "widgets")

DEF_CODES = set(T.DEFINE_CODES) | {57, 71}   # + ImportAssets / ImportAssets2 (the gfxfontlib font)


# ------------------------------------------------------------------ writing

class W:
    def __init__(self):
        self.bits = []

    def u(self, v, n):
        for i in range(n - 1, -1, -1):
            self.bits.append((v >> i) & 1)

    def s(self, v, n):
        self.u(v & ((1 << n) - 1), n)

    def out(self):
        b = self.bits + [0] * ((8 - len(self.bits) % 8) % 8)
        return bytes(int("".join(map(str, b[i:i + 8])), 2) for i in range(0, len(b), 8))


def nbits(*vals):
    return max([1] + [(abs(v).bit_length() + 1) if v else 1 for v in vals])


def rect(x0, x1, y0, y1):
    t = [int(round(v * 20)) for v in (x0, x1, y0, y1)]
    w = W(); n = nbits(*t); w.u(n, 5)
    for v in t:
        w.s(v, n)
    return w.out()


def matrix(tx, ty, sx=1.0, sy=1.0):
    w = W()
    if sx != 1.0 or sy != 1.0:
        a, d = int(round(sx * 65536)), int(round(sy * 65536))
        n = nbits(a, d); w.u(1, 1); w.u(n, 5); w.s(a, n); w.s(d, n)
    else:
        w.u(0, 1)
    w.u(0, 1)
    t = [int(round(tx * 20)), int(round(ty * 20))]
    n = nbits(*t) if any(t) else 0
    w.u(n, 5)
    if n:
        w.s(t[0], n); w.s(t[1], n)
    return w.out()


def cxform_mult(r, g, b):
    """CXFORMWITHALPHA, multiply terms only (1.0 = 256)."""
    w = W(); w.u(0, 1); w.u(1, 1)
    vals = [int(round(r * 256)), int(round(g * 256)), int(round(b * 256)), 256]
    n = nbits(*vals); w.u(n, 4)
    for v in vals:
        w.s(v, n)
    return w.out()


def tag(code, body):
    return struct.pack("<HI", (code << 6) | 0x3F, len(body)) + body


def place(depth, cid, name=None, mat=None, clip=None, cx=None):
    flags = 0x02 | (0x04 if mat else 0) | (0x08 if cx else 0) | (0x20 if name else 0) | (0x40 if clip else 0)
    body = struct.pack("<BHH", flags, depth, cid) + (mat or b"") + (cx or b"")
    if name:
        body += name.encode("latin-1") + b"\x00"
    if clip:
        body += struct.pack("<H", clip)
    return tag(26, body)


def sprite(sid, children):
    """children: [(depth, cid, name, mat, clip, cx)] - one frame."""
    body = struct.pack("<HH", sid, 1)
    for d, c, n, m, cl, cx in children:
        body += place(d, c, n, m, cl, cx)
    body += tag(1, b"") + b"\x00\x00"
    return tag(39, body)


def clear_shape(sid, w, h):
    """An invisible rectangle (alpha 0 fill) - a text widget's Frame: Norden's STB widgets have no plate, and HPM needs a
    Frame to know the art has loaded and to measure the widget."""
    body = struct.pack("<H", sid) + rect(0, w, 0, h) + bytes([1, 0x00, 0, 0, 0, 0]) + bytes([0])
    wb = W(); wb.u(1, 4); wb.u(0, 4)
    pts = [(0, 0), (w, 0), (w, h), (0, h)]
    x0, y0 = 0, 0
    wb.u(0, 1); wb.u(0, 1); wb.u(0, 1); wb.u(1, 1); wb.u(0, 1); wb.u(1, 1)
    wb.u(1, 5); wb.s(0, 1); wb.s(0, 1)   # move to 0,0 (1-bit zero values)
    wb.u(1, 1)                            # fill style 1
    cx = cy = 0
    for x, y in pts[1:] + [pts[0]]:
        tx, ty = int(round(x * 20)), int(round(y * 20))
        dx, dy = tx - cx, ty - cy
        n = max(2, nbits(dx, dy))
        wb.u(1, 1); wb.u(1, 1); wb.u(n - 2, 4)
        if dx and dy:
            wb.u(1, 1); wb.s(dx, n); wb.s(dy, n)
        elif dx:
            wb.u(0, 1); wb.u(0, 1); wb.s(dx, n)
        else:
            wb.u(0, 1); wb.u(1, 1); wb.s(dy, n)
        cx, cy = tx, ty
    wb.u(0, 6)
    return tag(32, body + wb.out())


# ------------------------------------------------------------------ reading the source

def first_frame_sprite(body):
    """A DefineSprite cut to its first frame, its ActionScript (DoAction) dropped."""
    sid, frames, inner = T.sprite_frames(body)
    keep = b""
    for code, b in inner:
        if code == 12:          # DoAction
            continue
        if code == 0:
            break
        keep += tag(code, b)
        if code == 1:           # the first ShowFrame ends it
            break
    else:
        keep += tag(1, b"")
    return tag(39, struct.pack("<HH", sid, 1) + keep + b"\x00\x00")


class Source:
    def __init__(self, path):
        self.path = path
        self.swf = T.load(path)
        self.defs, self.order, self.fileattr = {}, [], None
        for code, body in self.swf["tags"]:
            if code == 69:
                self.fileattr = body
            if code in DEF_CODES:
                cid = T.char_id(code, body)
                self.order.append((code, body))
                if cid is not None:
                    self.defs[cid] = (code, body)
        self.max_id = max(self.defs)

    def definitions(self):
        out = b""
        for code, body in self.order:
            out += first_frame_sprite(body) if code == 39 else tag(code, body)
        return out

    def children(self, sid):
        code, body = self.defs[sid]
        return T.first_frame_list(T.sprite_frames(body)[2])

    def bbox(self, cid, m=(1, 1, 0, 0, 0, 0)):
        """Bounds of a character under a scale+translate matrix (rotation ignored - none in these files)."""
        sx, sy, _, _, tx, ty = m
        code, body = self.defs[cid]
        if code == 39:
            boxes = []
            for p in self.children(cid):
                if p["id"] is None or p["id"] not in self.defs:
                    continue
                pm = p["matrix"] or (1, 1, 0, 0, 0, 0)
                b = self.bbox(p["id"], (sx * pm[0], sy * pm[1], 0, 0, tx + sx * pm[4], ty + sy * pm[5]))
                if b:
                    boxes.append(b)
            if not boxes:
                return None
            return (min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes))
        b = T.bounds(code, body)
        if not b:
            return None
        xs = sorted([tx + sx * b[0], tx + sx * b[1]]); ys = sorted([ty + sy * b[2], ty + sy * b[3]])
        return (xs[0], xs[1], ys[0], ys[1])


# ------------------------------------------------------------------ the widgets

def write(path, src, stage_w, stage_h, extra_defs, root):
    """root: [(depth, cid, name, (tx, ty, sx, sy), clip, cx)]"""
    payload = rect(0, stage_w, 0, stage_h) + struct.pack("<HH", 30 << 8, 1)
    payload += tag(69, src.fileattr or struct.pack("<I", 0))
    payload += src.definitions() + extra_defs
    for d, c, n, m, cl, cx in root:
        payload += place(d, c, n, matrix(*m) if m else None, cl, cx)
    payload += tag(1, b"") + b"\x00\x00"
    ver = src.swf["version"]
    raw = b"FWS" + bytes([ver]) + struct.pack("<I", 8 + len(payload)) + payload
    data = b"CWS" + raw[3:8] + zlib.compress(raw[8:])
    open(path, "wb").write(data)
    return len(data)


def meter_from_container(src, container, bar_name, deco_depths, tint=None):
    """A Norden meter (CastingBar_*, oxygenMeter2): its MeterContainer's first-frame list, with the named bar swapped for
    a left-registered Fill wrapper and the decoration + track grouped as Frame. Mask and gloss keep their depths."""
    items = src.children(container)
    bar = next(p for p in items if p["name"] == bar_name)
    bm = bar["matrix"]
    bar_box = src.bbox(bar["id"], bm)                       # in container space
    nid = src.max_id + 1
    frame_id, fill_id = nid, nid + 1
    frame_children, root, other = [], [], []
    for p in items:
        m = p["matrix"] or (1, 1, 0, 0, 0, 0)
        if p["depth"] in deco_depths:
            frame_children.append((p["depth"], p["id"], None, matrix(m[4], m[5], m[0], m[1]), None, None))
        elif p is bar:
            continue
        else:
            other.append(p)
    # the wrapper: origin = the bar's left edge (and its top stays where the container put it)
    wrap_x = bar_box[0]
    fill_children = [(1, bar["id"], None, matrix(bm[4] - wrap_x, bm[5], bm[0], bm[1]), None, None)]
    extra = sprite(frame_id, frame_children) + sprite(fill_id, fill_children)
    # everything's bounds, to put the art's top-left at 0,0
    boxes = [src.bbox(p["id"], p["matrix"] or (1, 1, 0, 0, 0, 0)) for p in items if p["depth"] in deco_depths]
    boxes.append(bar_box)
    x0 = min(b[0] for b in boxes); y0 = min(b[2] for b in boxes)
    x1 = max(b[1] for b in boxes); y1 = max(b[3] for b in boxes)
    root.append((1, frame_id, "Frame", (-x0, -y0, 1.0, 1.0), None, None))
    for p in other:   # the mask and the gloss, at their own depths (the mask clips the fill and the gloss)
        m = p["matrix"] or (1, 1, 0, 0, 0, 0)
        root.append((p["depth"], p["id"], None, (m[4] - x0, m[5] - y0, m[0], m[1]), p["clip"], None))
    root.append((bar["depth"], fill_id, "Fill", (wrap_x - x0, -y0, 1.0, 1.0), None,
                 cxform_mult(*tint) if tint else None))
    root.sort(key=lambda r: r[0])
    return x1 - x0, y1 - y0, extra, root


def text_widget(src, widget, icon_name, text_name):
    """An STB widget (gold, weight, game time): its icon and its own text field (Norden's font, size and colour), with
    an invisible Frame over both."""
    items = {p["name"]: p for p in src.children(widget) if p["name"]}
    icon, text = items[icon_name], items[text_name]
    im, tm = icon["matrix"], text["matrix"]
    ib = src.bbox(icon["id"], im); tb = src.bbox(text["id"], tm)
    x0, y0 = min(ib[0], tb[0]), min(ib[2], tb[2])
    x1, y1 = max(ib[1], tb[1]), max(ib[3], tb[3])
    w, h = x1 - x0, y1 - y0
    fid = src.max_id + 1
    extra = clear_shape(fid, w, h) + sprite(fid + 1, [(1, fid, None, None, None, None)])
    # the text field itself, not the STB sprite around it (that sprite carries STB's script)
    tcode, tbody = src.defs[text["id"]]
    if tcode == 39:   # goldWidget wraps its field in a sprite ("goldText" > "Text")
        inner = src.children(text["id"])[0]
        field_id = inner["id"]
        fm = inner["matrix"]
        tm = (tm[0] * fm[0], tm[1] * fm[1], 0, 0, tm[4] + tm[0] * fm[4], tm[5] + tm[1] * fm[5])
    else:
        field_id = text["id"]
    root = [(1, fid + 1, "Frame", (0.0, 0.0, 1.0, 1.0), None, None),
            (2, icon["id"], "Icon", (im[4] - x0, im[5] - y0, im[0], im[1]), None, None),
            (3, field_id, "Value", (tm[4] - x0, tm[5] - y0, tm[0], tm[1]), None, None)]
    return w, h, extra, root


def level_widget(src, widget):
    """lvlWidget: its meter back as Frame, its meter as a left-registered Fill, its level text as Value."""
    items = {p["name"]: p for p in src.children(widget) if p["name"]}
    back, meter, text = items["lvlMeter_Back"], items["lvlMeter_Meter"], items["lvl_Text"]
    bm, mm, tm = back["matrix"], meter["matrix"], text["matrix"]
    bb, mb, tb = src.bbox(back["id"], bm), src.bbox(meter["id"], mm), src.bbox(text["id"], tm)
    x0 = min(bb[0], mb[0], tb[0]); y0 = min(bb[2], mb[2], tb[2])
    x1 = max(bb[1], mb[1], tb[1]); y1 = max(bb[3], mb[3], tb[3])
    nid = src.max_id + 1
    wrap_x = mb[0]
    extra = sprite(nid, [(1, back["id"], None, matrix(bm[4], bm[5], bm[0], bm[1]), None, None)])
    extra += sprite(nid + 1, [(1, meter["id"], None, matrix(mm[4] - wrap_x, mm[5], mm[0], mm[1]), None, None)])
    root = [(1, nid, "Frame", (-x0, -y0, 1.0, 1.0), None, None),
            (2, nid + 1, "Fill", (wrap_x - x0, -y0, 1.0, 1.0), None, None),
            (3, text["id"], "Value", (tm[4] - x0, tm[5] - y0, tm[0], tm[1]), None, None)]
    return x1 - x0, y1 - y0, extra, root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    def s(name):
        return Source(os.path.join(a.src, name))

    jobs = {
        # meters: (source, container sprite id found by its name, the bar's name, the decoration depths)
        "casting.swf": lambda: meter_job(s("CastingBar_Spell.swf"), "MeterContainer", "Bar", (1, 2)),
        "shout.swf": lambda: meter_job(s("CastingBar_Shout.swf"), "MeterContainer", "Bar", (1, 2)),
        "detection.swf": lambda: meter_job(s("CastingBar_Spell.swf"), "MeterContainer", "Bar", (1, 2), tint=(1.0, 0.35, 0.3)),
        "breath.swf": lambda: meter_job(s("oxygenMeter2.swf"), "MeterContainer", "Bar", (1, 2)),
        "level.swf": lambda: widget_job(s("lvlWidget.swf"), level_widget),
        "gold.swf": lambda: widget_job(s("goldWidget.swf"), lambda src, w: text_widget(src, w, "gold_Icon", "goldText")),
        "weight.swf": lambda: widget_job(s("weightWidget.swf"), lambda src, w: text_widget(src, w, "weightIcon", "weight_Text")),
        "time.swf": lambda: widget_job(s("gametimeWidget.swf"), lambda src, w: text_widget(src, w, "gametimeIcon1", "gametime_Text")),
    }

    def find_sprite(src, name):
        for cid, (code, body) in src.defs.items():
            if code != 39:
                continue
            for p in src.children(cid):
                if p["name"] == name:
                    return p["id"]
        for p in T.first_frame_list(src.swf["tags"]):
            if p["name"] == name:
                return p["id"]
        raise KeyError(name)

    def meter_job(src, container_name, bar, deco, tint=None):
        cid = find_sprite(src, container_name)
        return src, meter_from_container(src, cid, bar, deco, tint)

    def widget_job(src, fn):
        wid = find_sprite(src, "widget")
        return src, fn(src, wid)

    for name, job in jobs.items():
        src, (w, h, extra, root) = job()
        n = write(os.path.join(a.out, name), src, w, h, extra, root)
        print(f"{name:14} {w:7.1f} x {h:6.1f}  {n:7} bytes  from {os.path.basename(src.path)}  [{', '.join(r[2] for r in root if r[2])}]")


if __name__ == "__main__":
    main()
