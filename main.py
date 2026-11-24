#!/usr/bin/env python3
"""Copy entry.png to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Python 3.13, standard library only, no network. The copy is verified
byte-for-byte (size and sha256) and the image is verified to be a
1024x1024 PNG (signature + IHDR dimensions, parsed with the standard
library) before the script reports success.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py          # copy + verify
    python3 main.py --check                          # verify entry.png only
"""

import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path):
    """Return (width, height) of a PNG by parsing its IHDR chunk.

    Raises ValueError if the file is not a PNG or its header is truncated.
    Standard library only (struct); no image library needed.
    """
    with open(path, "rb") as f:
        header = f.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        raise ValueError(f"{path}: not a PNG file (bad signature)")
    # IHDR chunk: length (4 bytes) + type "IHDR" (4 bytes) at offset 8,
    # then width (4 bytes, big-endian) and height (4 bytes) at offset 16.
    if header[12:16] != b"IHDR":
        raise ValueError(f"{path}: first chunk is not IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def check_png(path, label):
    """Verify a file is a 1024x1024 PNG; return (ok, message)."""
    try:
        width, height = png_dimensions(path)
    except (OSError, ValueError) as exc:
        return False, f"error: {label} failed dimension check: {exc}"
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        return (
            False,
            f"error: {label} is {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}",
        )
    return True, f"{label}: {width}x{height} PNG ok"


def main(argv):
    if argv and argv[0] == "--check":
        if not os.path.isfile(SRC):
            print(f"error: {SRC} not found", file=sys.stderr)
            return 1
        ok, message = check_png(SRC, "entry.png")
        if not ok:
            print(message, file=sys.stderr)
            return 1
        size = os.path.getsize(SRC)
        print(f"{message}; {size} bytes, sha256 {sha256(SRC)}")
        return 0

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found", file=sys.stderr)
        return 1
    ok, message = check_png(SRC, "entry.png")
    if not ok:
        print(message, file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    src_size = os.path.getsize(SRC)
    dst_size = os.path.getsize(dst)
    if src_size != dst_size or sha256(SRC) != sha256(dst):
        print("error: copy failed the byte-for-byte self-check", file=sys.stderr)
        return 1
    ok, message = check_png(dst, "copied entry.png")
    if not ok:
        print(message, file=sys.stderr)
        return 1
    print(
        f"copied entry.png: {dst_size} bytes, "
        f"sha256 {sha256(dst)}, {EXPECTED_WIDTH}x{EXPECTED_HEIGHT} PNG verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
