#!/usr/bin/env python3
"""Verify the non-circular public-release attestation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "RELEASE_ATTESTATION.json"
EXPECTED_PATHS = {
    "source_manifest": "MANIFEST_SHA256.txt",
    "paper_pdf": (
        "paper/Minimum_Subspace_Trades_and_Relation_Lattices_"
        "in_Three_Binary_Designs.pdf"
    ),
    "aggregate_receipt": "results/public_package_verification.json",
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


def main() -> None:
    document = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    require(
        document["schema"] == "MINIMUM-SUBSPACE-TRADES-RELEASE-ATTESTATION-v1",
        "schema",
    )
    require(document["status"] == "VERIFIED_PUBLIC_PACKAGE", "status")
    require(document["release_version"] == "1.1.0", "release version")
    for key, expected_relative in EXPECTED_PATHS.items():
        record = document["artifacts"][key]
        require(record["path"] == expected_relative, f"{key} path")
        path = ROOT / Path(expected_relative)
        require(path.is_file() and not path.is_symlink(), f"{key} file")
        require(sha256_file(path) == record["sha256"], f"{key} hash")
    gates = document["gates"]
    require(all(gates.values()), "one or more release gates are false")
    print("PASS_RELEASE_ATTESTATION")


if __name__ == "__main__":
    main()
