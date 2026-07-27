#!/usr/bin/env python3
"""Replay the public gate from only files named by the source manifest."""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
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


def run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(
        completed.returncode == 0,
        "command failed: "
        + " ".join(command)
        + f"\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
    )
    return completed.stdout


def main() -> None:
    entries: list[tuple[str, str]] = []
    for number, line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line or line.startswith("#"):
            continue
        match = LINE.fullmatch(line)
        require(match is not None, f"malformed manifest line {number}")
        expected, relative = match.groups()
        require("\\" not in relative, f"nonportable manifest path {relative}")
        candidate = Path(relative)
        require(
            not candidate.is_absolute() and ".." not in candidate.parts,
            f"unsafe manifest path {relative}",
        )
        source = ROOT / candidate
        require(source.is_file() and not source.is_symlink(), relative)
        require(sha256_file(source) == expected.upper(), relative)
        entries.append((expected.upper(), relative))

    with tempfile.TemporaryDirectory(prefix="p39_manifest_replay_") as raw:
        isolated = Path(raw) / "package"
        isolated.mkdir()
        shutil.copy2(MANIFEST, isolated / MANIFEST.name)
        for _, relative in entries:
            source = ROOT / Path(relative)
            target = isolated / Path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        python = sys.executable
        check = isolated / "scripts" / "check_manifest.py"
        verify = isolated / "scripts" / "verify_all.py"
        run([python, str(check), "--closed-tree"], isolated)
        run([python, str(verify)], isolated)
        receipt = isolated / "results" / "public_package_verification.json"
        first = receipt.read_bytes()
        run([python, "-O", str(verify)], isolated)
        second = receipt.read_bytes()
        require(first == second, "normal and optimized receipts differ")
        run([python, str(check), "--closed-tree"], isolated)
        print(
            "PASS_MANIFEST_ONLY_REPLAY "
            f"files={len(entries)} receipt_sha256={sha256_file(receipt)}"
        )


if __name__ == "__main__":
    main()
