r"""Norden's Dragon's Eye Minimap movie gets Dragon's Eye Minimap 1.7.5's own frame-1 script (Norden UI - Black 1.1.0,
2026-10-23).

Why: Norden UI's "Norden Dragon Eye Minimap 1.1" patch ships its own Interface\InfinityUI\HUDMenu\HUDMovieBaseInstance\
Minimap.swf - Norden's frame and title placement over the minimap classes of an older Dragon's Eye Minimap. Read tag by
tag against Dragon's Eye Minimap 1.7.5's Minimap.swf (swftags.py), the two movies differ in:
  * tag 1, SetBackgroundColor (Norden UI - Black's recolour) and the MapClip sprite (character 16: Norden moves
    ClearedHint and LocationName below the map) - Norden's look, kept;
  * the class packages (DoInitAction: Map.Display, Map.LocalMap, Map.MapMarker, gfx.io.GameDelegate) - compiled by
    another compiler, but they decompile to the same code apart from register numbers; both create
    IconDisplay.YouAreHereMarker the same way (CreateMarkers: the PlayerLocationMarkerType marker's Icon) and Norden's
    marker art (!assets\MinimapArt.swf, export YouAreHereMarker) places its Icon child on frame 1, as Dragon's Eye
    Minimap's does - kept;
  * the root frame-1 script (DoAction). Dragon's Eye Minimap's (since 1.3.7 / 1.3.9 / 1.4.8) adds Favor to the
    clip's HUD mode flags and SyncVisibilityToHudMode(), which AddToHudElements (the function the plugin invokes when it
    registers the clip) and onEnterFrame's re-registration call, so the clip is made visible when it joins HudElements
    while the HUD mode allows it - HUDModes starts empty, and a clip that registers before the first mode is pushed is
    otherwise never told to show. Norden's is the older script without either.
This tool replaces that one DoAction tag with Dragon's Eye Minimap 1.7.5's, byte for byte (DEM_FRAME1 below, read
out of the 1.7.5 package's Minimap.swf, SHA-256 DEM_FRAME1_SHA256), and nothing else: every other tag of the movie -
the art, Norden's layout, the recolour - is written back unchanged and checked to be unchanged.

The input must be Norden's movie: its frame-1 DoAction must be NORDEN_FRAME1_SHA256 (Norden UI's own, the same in the
original and in the recoloured black copy). A movie that already carries Dragon's Eye Minimap's script is left as it is.
Anything else is refused. Dragon's Eye Minimap is GPL-3.0-or-later, as this repository is. The output stays out of git
(*.swf); build-fomod.py runs this on the package's copy after every other copy step.

    python tools/minimap-dem-patch.py <Minimap.swf> [...]                 patch in place
    python tools/minimap-dem-patch.py <Minimap.swf> --out <file.swf>      write elsewhere
    python tools/minimap-dem-patch.py --check <Minimap.swf> [...]         exit 1 unless it already carries the script
    python tools/minimap-dem-patch.py --dem <DEM Minimap.swf> ...         take the script from a DEM movie (must hash
                                                                         to DEM_FRAME1_SHA256)
"""
import argparse, hashlib, struct, sys, zlib

NORDEN_FRAME1_SHA256 = "649eafdeab8416cc81d4769491425b19177924620ea8bc823c713879216fd8fb"
DEM_FRAME1_SHA256 = "441a41ec887986cc7bc4e6605902fecb348b7d72fa65c9546c0e1c81aabc40da"   # DEM 1.7.5, 1127 bytes
DEM_FRAME1 = bytes.fromhex("".join("""
8812011c005374616765007769647468006865696768740078007900676c6f62616c546f4c6f63616c005f58005f5900416c6c0053746561
6c74684d6f6465005377696d6d696e6700486f7273654d6f646500576172486f7273654d6f6465004661766f72005f6c6576656c30004855
444d6f76696542617365496e7374616e6365004855444d6f646573006c656e677468006861734f776e50726f7065727479005f7669736962
6c6500487564456c656d656e747300707573680053796e635669736962696c697479546f4875644d6f6465007570646174655363616c6566
6f726d005f676c6f62616c00676678457874656e73696f6e7300476c6f62616c46756e63005365744c6f636b46756e6374696f6e008e2900
4d696e696d6170000200062a0001615f706f736974696f6e580002615f706f736974696f6e5900c80096020008001c96020008014e960200
04010c870100031796020008001c96020008024e96020004020c870100041796020008039602000403960200080496020004049605000702
0000004387010005179602000405960500070100000096020008053d179602000806960200040596020008034e1d96020008079602000405
96020008044e1d960200080896020005011d960200080996020005011d960200080a96020005011d960200080b96020005011d960200080c
96020005011d960200080d96020005011d8e1f0053796e635669736962696c697479546f4875644d6f6465000000042900d200960200080e
1c960200080f4e8701000217960200040296010003494c9d0200110017960200040296020008104e9601000349129d02000500960100033e
96020008088701000317960200040296020008104e96020008114e960500070000000067129d02002b00960200040296020008104e960200
040296020008104e96020008114e96050007010000000b4e870100031796020004039602000808494c9d0200190017960200040396050007
010000009602000401960200081252129d020010009602000401960200081396020005014f8e1800416464546f487564456c656d656e7473
000000022900350096020004019605000701000000960200080e1c960200080f4e96020008144e9602000815521796050007000000009602
0008163d178e14006f6e456e7465724672616d65000000052900ac00960200080e1c960200080f4e96020008144e87010002179602000402
96020008114e8701000317960500070000000087010004179602000404960200040348129d02003400960200040296020004044e96020004
0149129d02000500960100033e96020004049605000701000000478701000417990200bbff96020004019605000701000000960200040296
020008155217960500070000000096020008163d17960200081796020005011d960200080841960200080941960200080a41960200080b41
960200080c41960200080d41960200081796020005013c96020008181c960200081996020005014f9605000700000000960200081a1c9602
00081b52170700
""".split()))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(raw):
    """(signature, version, uncompressed body after the 8-byte header)"""
    sig, ver = raw[:3], raw[3]
    if sig == b"CWS":
        return sig, ver, zlib.decompress(raw[8:])
    if sig == b"FWS":
        return sig, ver, raw[8:]
    raise ValueError(f"not an uncompressed or zlib SWF ({sig!r})")


def tags(body):
    """[(code, start, header_end, end)] of the root timeline, after the RECT, frame rate and frame count."""
    nbits = body[0] >> 3
    pos = (5 + 4 * nbits + 7) // 8 + 4
    out = []
    while pos < len(body):
        start = pos
        h = struct.unpack_from("<H", body, pos)[0]; pos += 2
        code, ln = h >> 6, h & 0x3F
        if ln == 0x3F:
            ln = struct.unpack_from("<I", body, pos)[0]; pos += 4
        out.append((code, start, pos, pos + ln))
        pos += ln
        if code == 0:
            break
    return out


def frame1_doaction(body, tl):
    """Index of the one root DoAction (12) before the first ShowFrame (1)."""
    found = []
    for i, (code, *_ ) in enumerate(tl):
        if code == 1:
            break
        if code == 12:
            found.append(i)
    if len(found) != 1:
        raise ValueError(f"expected one frame-1 DoAction on the root timeline, found {len(found)}")
    return found[0]


def long_tag(code, payload):
    return struct.pack("<HI", (code << 6) | 0x3F, len(payload)) + payload


def patch(raw, script):
    """(new raw bytes or None when already patched, message)"""
    sig, ver, body = read(raw)
    tl = tags(body)
    i = frame1_doaction(body, tl)
    _, start, hend, end = tl[i]
    have = sha(body[hend:end])
    if have == DEM_FRAME1_SHA256:
        return None, "already carries Dragon's Eye Minimap 1.7.5's frame-1 script"
    if have != NORDEN_FRAME1_SHA256:
        raise ValueError(f"frame-1 DoAction is neither Norden's nor DEM 1.7.5's (sha256 {have}) - not the movie this tool is for")
    new_body = body[:start] + long_tag(12, script) + body[end:]
    new_raw = sig + bytes([ver]) + struct.pack("<I", 8 + len(new_body)) + (zlib.compress(new_body, 9) if sig == b"CWS" else new_body)
    verify(raw, new_raw)
    return new_raw, f"frame-1 DoAction replaced ({end - hend} -> {len(script)} bytes); every other tag unchanged"


def verify(old_raw, new_raw):
    """Read the result back: same tag count, every tag but the frame-1 DoAction byte-identical, that one DEM's."""
    _, _, ob = read(old_raw)
    _, _, nb = read(new_raw)
    if struct.unpack_from("<I", new_raw, 4)[0] != 8 + len(nb):
        raise ValueError("written file length field does not match the body")
    ot, nt = tags(ob), tags(nb)
    if len(ot) != len(nt):
        raise ValueError(f"tag count changed {len(ot)} -> {len(nt)}")
    i = frame1_doaction(nb, nt)
    if ob[:ot[0][1]] != nb[:nt[0][1]]:
        raise ValueError("movie header (stage, frame rate, frame count) changed")
    for k, (a, b) in enumerate(zip(ot, nt)):
        if a[0] != b[0]:
            raise ValueError(f"tag {k} code changed {a[0]} -> {b[0]}")
        if k == i:
            if sha(nb[b[2]:b[3]]) != DEM_FRAME1_SHA256:
                raise ValueError("the new frame-1 DoAction does not read back as DEM 1.7.5's")
        elif ob[a[2]:a[3]] != nb[b[2]:b[3]]:
            raise ValueError(f"tag {k} (code {a[0]}) changed - only the frame-1 DoAction may differ")


def carries(raw):
    _, _, body = read(raw)
    tl = tags(body)
    _, _, hend, end = tl[frame1_doaction(body, tl)]
    return sha(body[hend:end]) == DEM_FRAME1_SHA256


def script_from_dem(path):
    _, _, body = read(open(path, "rb").read())
    tl = tags(body)
    _, _, hend, end = tl[frame1_doaction(body, tl)]
    s = body[hend:end]
    if sha(s) != DEM_FRAME1_SHA256:
        raise ValueError(f"{path}: frame-1 DoAction sha256 {sha(s)} is not DEM 1.7.5's {DEM_FRAME1_SHA256}")
    return s


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("swf", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dem")
    a = ap.parse_args(argv)
    if sha(DEM_FRAME1) != DEM_FRAME1_SHA256:
        print("FAIL the embedded DEM script does not match its hash"); return 1
    script = script_from_dem(a.dem) if a.dem else DEM_FRAME1
    if a.out and len(a.swf) != 1:
        print("FAIL --out takes one input"); return 1
    bad = 0
    for p in a.swf:
        raw = open(p, "rb").read()
        try:
            if a.check:
                ok = carries(raw)
                print(f"{'ok  ' if ok else 'FAIL'} {p}: {'carries' if ok else 'does not carry'} DEM 1.7.5's frame-1 script")
                bad += 0 if ok else 1
                continue
            new, msg = patch(raw, script)
        except ValueError as e:
            print(f"FAIL {p}: {e}"); bad += 1; continue
        dst = a.out or p
        if new is not None:
            open(dst, "wb").write(new)
        elif a.out:
            open(dst, "wb").write(raw)
        print(f"ok   {dst}: {msg}  sha256 {sha(open(dst, 'rb').read())}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
