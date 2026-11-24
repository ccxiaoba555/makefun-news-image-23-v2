#!/usr/bin/env python3
"""Copy entry.png to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Python 3.13, standard library only, no network. The copy is verified
byte-for-byte (size and sha256) before the script reports success.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    src_size = os.path.getsize(SRC)
    dst_size = os.path.getsize(dst)
    if src_size != dst_size or sha256(SRC) != sha256(dst):
        print("error: copy failed the byte-for-byte self-check", file=sys.stderr)
        return 1
    print(f"copied entry.png: {dst_size} bytes, sha256 {sha256(dst)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
