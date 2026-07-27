#!/usr/bin/env python3
"""Fail-closed SHA-256 and closed-tree checker for the P39 package."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_REAL = ROOT.resolve(strict=True)
MANIFEST = ROOT / "MANIFEST_SHA256.txt"
LINE = re.compile(r"^([0-9A-Fa-f]{64})  ([^\r\n]+)$")
EXCLUDED = {
    "MANIFEST_SHA256.txt",
    "RELEASE_ATTESTATION.json",
    "results/public_package_verification.json",
    (
        "paper/Minimum_Subspace_Trades_and_Relation_Lattices_"
        "in_Three_Binary_Designs.pdf"
    ),
}
BUILD_SUFFIXES = {".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_manifest_path(relative: str, number: int) -> Path:
    require("\\" not in relative, f"nonportable path on line {number}")
    candidate = Path(relative)
    require(
        not candidate.is_absolute() and ".." not in candidate.parts,
        f"unsafe path on line {number}",
    )
    cursor = ROOT
    for part in candidate.parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), f"symlink path on line {number}")
    require(cursor.is_file(), f"missing manifest file: {relative}")
    resolved = cursor.resolve(strict=True)
    require(
        resolved.is_relative_to(ROOT_REAL),
        f"manifest path escapes repository: {relative}",
    )
    return resolved


def is_build_artifact(relative: str) -> bool:
    path = Path(relative)
    return (
        path.parts
        and path.parts[0] == "paper"
        and (path.suffix in BUILD_SUFFIXES or relative.endswith(".synctex.gz"))
    )


def closed_tree_check(seen: set[str]) -> None:
    actual: set[str] = set()
    for directory, directories, files in os.walk(ROOT, followlinks=False):
        base = Path(directory)
        kept = []
        for name in directories:
            child = base / name
            relative = child.relative_to(ROOT).as_posix()
            if name == ".git":
                continue
            require(not child.is_symlink(), f"symlink directory: {relative}")
            kept.append(name)
        directories[:] = kept
        for name in files:
            path = base / name
            relative = path.relative_to(ROOT).as_posix()
            require(not path.is_symlink(), f"symlink file: {relative}")
            resolved = path.resolve(strict=True)
            require(
                resolved.is_relative_to(ROOT_REAL),
                f"file escapes repository: {relative}",
            )
            if relative in EXCLUDED or is_build_artifact(relative):
                continue
            actual.add(relative)
    unmanifested = sorted(actual - seen)
    require(
        not unmanifested,
        "unmanifested package files: " + ", ".join(unmanifested),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--closed-tree",
        action="store_true",
        help="reject every non-build file not listed in the manifest",
    )
    args = parser.parse_args()

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
        require(relative not in seen, f"duplicate manifest path: {relative}")
        seen.add(relative)
        path = safe_manifest_path(relative, number)
        actual = sha256_file(path)
        require(
            actual == expected.upper(),
            f"SHA-256 mismatch for {relative}: {actual} != {expected.upper()}",
        )
        checked += 1
    require(checked > 0, "empty manifest")
    if args.closed_tree:
        closed_tree_check(seen)
    suffix = "_CLOSED_TREE" if args.closed_tree else ""
    print(f"PASS_MANIFEST_{checked}_FILES{suffix}")


if __name__ == "__main__":
    main()
