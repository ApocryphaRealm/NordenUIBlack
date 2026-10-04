r"""Minimal SWF tag reader/writer for grafting Norden UI - Black's widget art into HUD Position Manager's clip contract
(2026-10-04). Reads a SWF (FWS/CWS) into (code, body) tags, walks DefineSprite timelines, reads PlaceObject2/3
character ids, names, depths, clip depths and matrices, and shape/edit-text bounds. No art is stored by this tool; it
reads the installed Norden UI - Black files on the build machine.

    python tools/swftags.py <file.swf>      # dump the definition list and every sprite's first-frame display list
"""
import struct
import sys
import zlib

DEFINE_CODES = {2: "Shape", 22: "Shape2", 32: "Shape3", 83: "Shape4", 39: "Sprite", 37: "EditText", 11: "Text",
                33: "Text2", 6: "BitsJPEG", 21: "BitsJPEG2", 35: "BitsJPEG3", 90: "BitsJPEG4", 20: "BitsLossless",
                36: "BitsLossless2", 10: "Font", 48: "Font2", 75: "Font3", 46: "MorphShape", 84: "MorphShape2",
                7: "Button", 34: "Button2", 14: "Sound"}


class Bits:
    def __init__(self, data, pos=0):
        self.data, self.byte, self.bit = data, pos, 0

    def u(self, n):
        v = 0
        for _ in range(n):
            b = (self.data[self.byte] >> (7 - self.bit)) & 1
            v = (v << 1) | b
            self.bit += 1
            if self.bit == 8:
                self.bit, self.byte = 0, self.byte + 1
        return v

    def s(self, n):
        v = self.u(n)
        return v - (1 << n) if n and v & (1 << (n - 1)) else v

    def align(self):
        if self.bit:
            self.bit, self.byte = 0, self.byte + 1
        return self.byte


def read_rect(data, pos):
    b = Bits(data, pos)
    n = b.u(5)
    r = [b.s(n) / 20.0 for _ in range(4)]   # xmin, xmax, ymin, ymax in px
    return r, b.align()


def read_matrix(data, pos):
    b = Bits(data, pos)
    sx = sy = 1.0
    r0 = r1 = 0.0
    if b.u(1):
        n = b.u(5); sx = b.s(n) / 65536.0; sy = b.s(n) / 65536.0
    if b.u(1):
        n = b.u(5); r0 = b.s(n) / 65536.0; r1 = b.s(n) / 65536.0
    n = b.u(5)
    tx = b.s(n) / 20.0 if n else 0.0
    ty = b.s(n) / 20.0 if n else 0.0
    return (sx, sy, r0, r1, tx, ty), b.align()


def load(path):
    raw = open(path, "rb").read()
    sig, ver = raw[:3], raw[3]
    if sig == b"CWS":
        body = zlib.decompress(raw[8:])
    elif sig == b"FWS":
        body = raw[8:]
    else:
        raise ValueError(f"{path}: not an uncompressed or zlib SWF ({sig})")
    rect, pos = read_rect(body, 0)
    rate, count = struct.unpack_from("<HH", body, pos)
    tags = parse_tags(body, pos + 4)
    return {"version": ver, "rect": rect, "rate": rate, "frames": count, "tags": tags}


def parse_tags(data, pos, end=None):
    tags = []
    end = len(data) if end is None else end
    while pos < end:
        h = struct.unpack_from("<H", data, pos)[0]; pos += 2
        code, ln = h >> 6, h & 0x3F
        if ln == 0x3F:
            ln = struct.unpack_from("<I", data, pos)[0]; pos += 4
        tags.append((code, data[pos:pos + ln]))
        pos += ln
        if code == 0:
            break
    return tags


def char_id(code, body):
    return struct.unpack_from("<H", body, 0)[0] if code in DEFINE_CODES else None


def place_info(code, body):
    """PlaceObject2 (26) / PlaceObject3 (70): dict of flags, depth, character id, matrix, name, clip depth."""
    flags = body[0]
    pos = 1
    flags3 = 0
    if code == 70:
        flags3 = body[1]; pos = 2
    depth = struct.unpack_from("<H", body, pos)[0]; pos += 2
    if code == 70 and (flags3 & 0x08 or (flags3 & 0x10 and flags & 0x02)):
        # class name present (HasClassName, or HasImage with HasCharacter)
        e = body.index(b"\x00", pos); pos = e + 1
    cid = None
    if flags & 0x02:
        cid = struct.unpack_from("<H", body, pos)[0]; pos += 2
    mat = None
    if flags & 0x04:
        mat, pos = read_matrix(body, pos)
    if flags & 0x08:   # colour transform: skip it
        b = Bits(body, pos); add = b.u(1); mul = b.u(1); n = b.u(4)
        for _ in range((4 if mul else 0) + (4 if add else 0)):
            b.s(n)
        pos = b.align()
    if flags & 0x10:
        pos += 2
    name = None
    if flags & 0x20:
        e = body.index(b"\x00", pos); name = body[pos:e].decode("latin-1"); pos = e + 1
    clip = None
    if flags & 0x40:
        clip = struct.unpack_from("<H", body, pos)[0]
    return {"move": bool(flags & 0x01), "depth": depth, "id": cid, "matrix": mat, "name": name, "clip": clip}


def sprite_frames(body):
    """A DefineSprite body: (sprite id, frame count, inner tags)."""
    sid, frames = struct.unpack_from("<HH", body, 0)
    return sid, frames, parse_tags(body, 4)


def first_frame_list(tags):
    """The display list after the first ShowFrame of a timeline."""
    shown = {}
    for code, body in tags:
        if code in (26, 70):
            p = place_info(code, body)
            if p["move"] and p["depth"] in shown and p["id"] is None:
                old = shown[p["depth"]]
                shown[p["depth"]] = dict(old, matrix=p["matrix"] or old["matrix"], name=p["name"] or old["name"])
            else:
                shown[p["depth"]] = p
        elif code in (5, 28):   # RemoveObject / RemoveObject2
            d = struct.unpack_from("<H", body, 2 if code == 5 else 0)[0]
            shown.pop(d, None)
        elif code == 1:
            break
    return [shown[d] for d in sorted(shown)]


def bounds(code, body):
    """A shape's or edit text's bounds (px), else None."""
    if code in (2, 22, 32, 83, 37, 46, 84):
        return read_rect(body, 2)[0]
    if code in (11, 33):
        return read_rect(body, 2)[0]
    return None


def _skip_matrix(data, pos):
    return read_matrix(data, pos)[1]


def shape_bitmaps(code, body):
    """The bitmap ids a shape's FIRST fill-style array refers to (bitmap fills 0x40..0x43). Enough for the simple shapes
    a widget is made of; styles added later in the shape records are not walked."""
    if code not in (2, 22, 32, 83):
        return set()
    pos = 2
    _, pos = read_rect(body, pos)
    if code == 83:
        _, pos = read_rect(body, pos)
        pos += 1
    n = body[pos]; pos += 1
    if n == 0xFF and code != 2:
        n = struct.unpack_from("<H", body, pos)[0]; pos += 2
    rgba = code in (32, 83)
    ids = set()
    for _ in range(n):
        t = body[pos]; pos += 1
        if t == 0x00:
            pos += 4 if rgba else 3
        elif t in (0x10, 0x12, 0x13):
            pos = _skip_matrix(body, pos)
            hdr = body[pos]; pos += 1
            pos += (hdr & 0x0F) * (1 + (4 if rgba else 3))
            if t == 0x13:
                pos += 2
        elif 0x40 <= t <= 0x43:
            bid = struct.unpack_from("<H", body, pos)[0]; pos += 2
            pos = _skip_matrix(body, pos)
            if bid != 0xFFFF:
                ids.add(bid)
        else:
            break
    return ids


def edit_text_font(body):
    """A DefineEditText's font id, or None."""
    _, pos = read_rect(body, 2)
    f1 = body[pos]
    if f1 & 0x01:
        return struct.unpack_from("<H", body, pos + 2)[0]
    return None


def closure(defs, roots):
    """Every character id the roots need: sprite children over ALL frames, shapes' bitmaps, edit texts' fonts."""
    need, todo = set(), list(roots)
    while todo:
        cid = todo.pop()
        if cid in need or cid not in defs:
            if cid not in defs:
                need.add(cid)   # an imported id (a font from gfxfontlib): kept so its import entry is copied
            continue
        need.add(cid)
        code, body = defs[cid]
        if code == 39:
            for c, b in sprite_frames(body)[2]:
                if c in (26, 70):
                    p = place_info(c, b)
                    if p["id"] is not None:
                        todo.append(p["id"])
        elif code in (2, 22, 32, 83):
            todo.extend(shape_bitmaps(code, body))
        elif code == 37:
            f = edit_text_font(body)
            if f is not None:
                todo.append(f)
    return need


def dump(path):
    swf = load(path)
    print(f"{path}: SWF {swf['version']}, stage {swf['rect']}, {swf['frames']} frames, {len(swf['tags'])} tags")
    defs = {}
    for code, body in swf["tags"]:
        cid = char_id(code, body)
        if cid is not None:
            defs[cid] = (code, body)
    for cid in sorted(defs):
        code, body = defs[cid]
        kind = DEFINE_CODES[code]
        if code == 39:
            sid, frames, inner = sprite_frames(body)
            acts = sum(1 for c, _ in inner if c in (12, 59))
            items = ", ".join(f"d{p['depth']}:{p['id']}{'=' + p['name'] if p['name'] else ''}{' clip' + str(p['clip']) if p['clip'] else ''}"
                              f"@{(round(p['matrix'][4], 1), round(p['matrix'][5], 1), round(p['matrix'][0], 2), round(p['matrix'][1], 2)) if p['matrix'] else ''}"
                              for p in first_frame_list(inner))
            print(f"  {cid:4} Sprite  frames={frames} actions={acts}  [{items}]")
        else:
            b = bounds(code, body)
            print(f"  {cid:4} {kind:12} {[round(v, 1) for v in b] if b else ''}")
    print("  root:", [(p['depth'], p['id'], p['name']) for p in first_frame_list(swf["tags"])])
    print("  other tags:", sorted({c for c, _ in swf["tags"] if c not in DEFINE_CODES}))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        dump(p)
