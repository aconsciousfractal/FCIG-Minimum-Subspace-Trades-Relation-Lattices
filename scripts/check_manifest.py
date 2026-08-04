#!/usr/bin/env python3
"""Fail-closed integrity and reader-surface checker for the public package."""

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
IGNORED_TOP_LEVEL = {".git", "tmp"}
RETIRED_PATHS = {
    "docs/EXTERNAL_RED_TEAM_ADJUDICATION.md",
    "docs/FINAL_RED_TEAM_2026-07-28.md",
    "docs/GATE_HISTORY.md",
    "docs/P39_P42_BOUNDARY.md",
    "docs/RED_TEAM_REPORT.md",
    "docs/RELEASE_READINESS.md",
}
FORBIDDEN_READER_PATTERNS = {
    "internal project label P39": re.compile(r"\bP39\b", re.IGNORECASE),
    "internal project label P42": re.compile(r"\bP42\b", re.IGNORECASE),
    "internal route label EXT04": re.compile(r"\bEXT04\b", re.IGNORECASE),
    "release-candidate wording": re.compile(
        r"\brelease[- ]candidate\b", re.IGNORECASE
    ),
    "internal archive dependency": re.compile(
        r"\b(?:internal|source-locked)\b.{0,80}\barchive\b", re.IGNORECASE
    ),
    "red-team workflow": re.compile(r"\bred[- ]team\b", re.IGNORECASE),
    "sub-agent workflow": re.compile(r"\bsub-agent\b", re.IGNORECASE),
    "internal stage label": re.compile(r"\bS4\.\d+[A-Z]?\b"),
}


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


def source_inventory() -> set[str]:
    actual: set[str] = set()
    for directory, directories, files in os.walk(ROOT, followlinks=False):
        base = Path(directory)
        kept = []
        for name in directories:
            child = base / name
            relative = child.relative_to(ROOT).as_posix()
            if len(child.relative_to(ROOT).parts) == 1 and name in IGNORED_TOP_LEVEL:
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
    return actual


def closed_tree_check(seen: set[str]) -> None:
    actual = source_inventory()
    unmanifested = sorted(actual - seen)
    require(
        not unmanifested,
        "unmanifested package files: " + ", ".join(unmanifested),
    )


def reader_surface_files() -> list[Path]:
    files = [
        ROOT / "README.md",
        ROOT / "README_REVIEWER.md",
        ROOT / "REPRODUCE.md",
        ROOT / "LICENSE_SCOPE.md",
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "CITATION.cff",
    ]
    files.extend(sorted((ROOT / "docs").glob("*.md")))
    files.extend(sorted((ROOT / "paper").rglob("*.tex")))
    return files


def check_reader_surface() -> None:
    for relative in RETIRED_PATHS:
        require(not (ROOT / relative).exists(), f"retired reader path: {relative}")
    for path in reader_surface_files():
        require(path.is_file(), f"missing reader file: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_READER_PATTERNS.items():
            require(
                pattern.search(text) is None,
                f"{label} in {path.relative_to(ROOT).as_posix()}",
            )


def write_manifest() -> None:
    lines = [
        f"{sha256_file(ROOT / relative)}  {relative}"
        for relative in sorted(source_inventory())
    ]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--closed-tree",
        action="store_true",
        help="reject every non-build file not listed in the manifest",
    )
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="regenerate the exact source manifest before checking it",
    )
    args = parser.parse_args()

    if args.write_manifest:
        write_manifest()
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
    check_reader_surface()
    if args.closed_tree:
        closed_tree_check(seen)
    suffix = "_CLOSED_TREE" if args.closed_tree else ""
    print(f"PASS_MANIFEST_{checked}_FILES{suffix}")


if __name__ == "__main__":
    main()
