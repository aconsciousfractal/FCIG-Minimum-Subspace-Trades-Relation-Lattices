#!/usr/bin/env python3
"""Cross-platform SHA-256 manifest checker for the P39 EXT04 package."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST_SHA256.txt"
LINE = re.compile(r"^([0-9A-Fa-f]{64})  ([^\r\n]+)$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    require(MANIFEST.is_file(), "missing MANIFEST_SHA256.txt")
    checked = 0
    seen: set[str] = set()
    for number, raw_line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line or raw_line.startswith("#"):
            continue
        match = LINE.fullmatch(raw_line)
        require(match is not None, f"malformed manifest line {number}")
        expected, relative = match.groups()
        require("\\" not in relative, f"nonportable path on line {number}")
        candidate = Path(relative)
        require(
            not candidate.is_absolute() and ".." not in candidate.parts,
            f"unsafe path on line {number}",
        )
        require(relative not in seen, f"duplicate manifest path: {relative}")
        seen.add(relative)
        path = ROOT / candidate
        require(path.is_file(), f"missing manifest file: {relative}")
        actual = sha256_file(path)
        require(
            actual == expected.upper(),
            f"SHA-256 mismatch for {relative}: {actual} != {expected.upper()}",
        )
        checked += 1
    require(checked > 0, "empty manifest")
    print(f"PASS_MANIFEST_{checked}_FILES")


if __name__ == "__main__":
    main()
