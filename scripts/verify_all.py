#!/usr/bin/env python3
"""Fail-closed one-command verifier for the public package."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "public_package_verification.json"
SCHEMA = "MINIMUM-SUBSPACE-TRADES-PUBLIC-PACKAGE-VERIFICATION-v1"

REPLAYS = (
    (
        "s449c_verify_g1r_replacement_minor.py",
        "s449c_g1r_replacement_minor_verification.json",
        "95D0D02E6D233DD25CEA69C07C33A3BCF2D850DE3708E2A1115AB6FEDFE56A15",
    ),
    (
        "s449c_verify_g1r_principal_determinant.py",
        "s449c_g1r_principal_determinant_verification.json",
        "0077E7FCB73D61EF584E3E503CDA539743A118AA631261A0C2DD75BFC8F1DD84",
    ),
    (
        "s449f_verify_reverse_row_determinant.py",
        "s449f_reverse_row_determinant_verification.json",
        "E2CE27333088A61FD696FBDFFFC502B85E5C3671FB9349A07F5C603507B06D17",
    ),
    (
        "s449f_verify_rho_d1_global_gate.py",
        "s449f_rho_d1_global_gate_verification.json",
        "B960ADA66A473AA3211EECC59727A7DD480DF10A1B37FDFDAFC8146CA2B18CC8",
    ),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def run_script(name: str) -> str:
    command = [sys.executable]
    if sys.flags.optimize:
        command.append("-O")
    command.append(str(SCRIPTS / name))
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(
        completed.returncode == 0,
        f"{name} failed with exit {completed.returncode}\n"
        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
    )
    return completed.stdout.strip()


def main() -> None:
    checks: list[dict[str, str]] = []
    for script, receipt, expected_hash in REPLAYS:
        stdout = run_script(script)
        receipt_path = RESULTS / receipt
        require(receipt_path.is_file(), f"{script} did not produce {receipt}")
        actual_hash = sha256_file(receipt_path)
        require(
            actual_hash == expected_hash,
            f"{receipt} hash mismatch: {actual_hash} != {expected_hash}",
        )
        checks.append(
            {
                "script": script,
                "receipt": f"results/{receipt}",
                "sha256": actual_hash,
            }
        )
        print(f"PASS {script}: {actual_hash}")
        if stdout:
            print(stdout.splitlines()[-1])

    manifest_stdout = run_script("check_manifest.py")
    require(
        manifest_stdout.startswith("PASS_MANIFEST_"),
        f"unexpected manifest output: {manifest_stdout}",
    )

    receipt = {
        "schema": SCHEMA,
        "status": "PASS",
        "replays": checks,
        "manifest_sha256": sha256_file(ROOT / "MANIFEST_SHA256.txt"),
        "theorem": {
            "component": "rho/B1",
            "complete_equation_columns": 1317,
            "structural_rank": 1312,
            "coefficient_ring": "Z[zeta_17]",
            "determinantal_ideal": (
                "I_1312(E_full) is the unit ideal after inverting 17"
            ),
            "ideal_index": 17**21,
            "smith_diagonal": [17] * 11 + [17**2] * 5,
        },
        "scope_boundary": {
            "global_maps_proved": ["rho/B1"],
            "global_maps_deferred": [
                "rho*omega/B1",
                "rho/B2",
                "rho*omega/B2",
                "rho/B3",
                "rho*omega/B3",
            ],
            "global_smith_groups": "OPEN",
        },
    }
    RESULTS.mkdir(exist_ok=True)
    OUTPUT.write_bytes(canonical_bytes(receipt))
    print(manifest_stdout)
    print(f"RECEIPT_SHA256={sha256_file(OUTPUT)}")
    print("PASS_MINIMUM_SUBSPACE_TRADES_PUBLIC_PACKAGE")


if __name__ == "__main__":
    main()
