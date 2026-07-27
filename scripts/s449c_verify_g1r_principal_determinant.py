#!/usr/bin/env python3
"""Independent verifier for the S4.49C G1R replacement determinant and norm."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any


sys.set_int_max_str_digits(0)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CRT_INPUT = PROJECT_ROOT / "results" / "s449c_g1r_crt_input.json"
COMPATIBLE_BINARY = (
    PROJECT_ROOT / "results" / "s449c_g1r_replacement_minor_flint.bin"
)
RAW_RESULT = PROJECT_ROOT / "results" / "s449c_g1r_crt_raw.json"
OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "s449c_g1r_principal_determinant_verification.json"
)

MAGIC = b"P39S447CMINOR1\0\0"
HEADER = struct.Struct("<16sIIIIQ")
ENTRY_PREFIX = struct.Struct("<II")
COEFFICIENTS = struct.Struct("<16q")
ORDER = 1312
DEGREE = 16
DIAGNOSTIC_REDUCTIONS = ((103, 8, 89),)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_prime_32(value: int) -> bool:
    if value < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if value == prime:
            return True
        if value % prime == 0:
            return False
    exponent = value - 1
    power = 0
    while exponent % 2 == 0:
        exponent //= 2
        power += 1
    for base in (2, 3, 5, 7, 11):
        witness = pow(base, exponent, value)
        if witness in (1, value - 1):
            continue
        for _ in range(power - 1):
            witness = witness * witness % value
            if witness == value - 1:
                break
        else:
            return False
    return True


def multiply(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    cyclic = [0] * 17
    for left_index, left_value in enumerate(left):
        if not left_value:
            continue
        for right_index, right_value in enumerate(right):
            if right_value:
                cyclic[(left_index + right_index) % 17] += (
                    left_value * right_value
                )
    eliminated = cyclic[16]
    return tuple(cyclic[index] - eliminated for index in range(16))


def conjugate(coefficients: tuple[int, ...], exponent: int) -> tuple[int, ...]:
    cyclic = [0] * 17
    for index, value in enumerate(coefficients):
        if value:
            cyclic[(index * exponent) % 17] += value
    eliminated = cyclic[16]
    return tuple(cyclic[index] - eliminated for index in range(16))


def exact_norm(coefficients: tuple[int, ...]) -> int:
    product = (1,) + (0,) * 15
    for exponent in range(1, 17):
        product = multiply(product, conjugate(coefficients, exponent))
    require(not any(product[1:]), "norm must land in Z")
    return product[0]


def evaluate(coefficients: tuple[int, ...], root: int, prime: int) -> int:
    value = 0
    for coefficient in reversed(coefficients):
        value = (value * root + coefficient) % prime
    return value


def compatible_binary_bound() -> tuple[int, int, int]:
    row_energies = [0] * ORDER
    with COMPATIBLE_BINARY.open("rb") as handle:
        raw_header = handle.read(HEADER.size)
        require(len(raw_header) == HEADER.size, "binary header")
        magic, version, conductor, degree, order, entry_count = HEADER.unpack(
            raw_header
        )
        require(magic == MAGIC, "binary magic")
        require(version == 1 and conductor == 17, "binary field")
        require(degree == DEGREE and order == ORDER, "binary dimensions")
        for _ in range(entry_count):
            raw_prefix = handle.read(ENTRY_PREFIX.size)
            raw_coefficients = handle.read(COEFFICIENTS.size)
            require(
                len(raw_prefix) == ENTRY_PREFIX.size
                and len(raw_coefficients) == COEFFICIENTS.size,
                "binary entry",
            )
            row, column = ENTRY_PREFIX.unpack(raw_prefix)
            require(row < ORDER and column < ORDER, "binary entry index")
            coefficients = COEFFICIENTS.unpack(raw_coefficients)
            coefficient_l1 = sum(abs(value) for value in coefficients)
            require(coefficient_l1 > 0, "binary stored zero")
            row_energies[row] += coefficient_l1 * coefficient_l1
        require(handle.read(1) == b"", "binary trailing data")

    require(all(value > 0 for value in row_energies), "binary zero row")
    product = math.prod(row_energies)
    exponent = 0
    right_side = 32 * 32 * product
    while (17 * (1 << exponent)) ** 2 <= right_side:
        exponent += 1
    require(
        (17 * (1 << exponent)) ** 2 > right_side,
        "bound inequality",
    )
    require(
        exponent == 0
        or (17 * (1 << (exponent - 1))) ** 2 <= right_side,
        "bound minimality",
    )
    return product, exponent + 1, entry_count


def strip_s(value: int) -> tuple[int, dict[str, int]]:
    remaining = abs(value)
    valuations = {}
    for prime in (2, 3, 17):
        exponent = 0
        while remaining and remaining % prime == 0:
            remaining //= prime
            exponent += 1
        valuations[str(prime)] = exponent
    return remaining, valuations


def main() -> int:
    prepared = json.loads(CRT_INPUT.read_text(encoding="utf-8"))
    raw = json.loads(RAW_RESULT.read_text(encoding="utf-8"))
    require(
        prepared["status"] == "PASS_G1R_CRT_INPUT_AND_BOUND",
        "prepared status",
    )
    require(
        raw["status"] == "PASS_EXACT_BOUND_CERTIFIED_RECONSTRUCTION",
        "raw status",
    )

    energy_product, signed_bound_bits, entry_count = compatible_binary_bound()
    bound = prepared["rigorous_bound"]
    require(str(energy_product) == bound["energy_product"], "energy product")
    require(
        signed_bound_bits == bound["signed_reconstruction_bound_bits"],
        "signed bound bits",
    )
    require(
        raw["coefficient_bound_bits"] == signed_bound_bits,
        "raw coefficient bound",
    )
    require(
        raw["target_modulus_bits"] == bound["target_modulus_bits"],
        "raw target modulus",
    )
    require(raw["entry_count"] == entry_count, "raw entry count")
    require(raw["order"] == ORDER, "raw order")

    primes = [int(value) for value in raw["crt_primes"]]
    residue_rows = raw["coefficient_residues_by_prime"]
    planned_primes = prepared["crt_plan"]["split_primes"]
    require(primes == planned_primes, "frozen CRT prime sequence")
    require(len(primes) == raw["crt_prime_count"], "CRT prime count")
    require(len(set(primes)) == len(primes), "CRT primes distinct")
    require(
        all(prime % 17 == 1 and is_prime_32(prime) for prime in primes),
        "CRT split primes",
    )
    modulus = math.prod(primes)
    require(
        modulus.bit_length() == raw["actual_modulus_bits"],
        "actual modulus bits",
    )
    require(
        modulus.bit_length() >= raw["target_modulus_bits"],
        "modulus reaches bound",
    )

    coefficients = tuple(
        int(value) for value in raw["exact_determinant_coefficients"]
    )
    require(len(coefficients) == DEGREE, "coefficient length")
    require(
        max(abs(value).bit_length() for value in coefficients)
        < signed_bound_bits,
        "coefficient exceeds signed bound",
    )
    require(len(residue_rows) == len(primes), "residue row count")
    for prime, residues in zip(primes, residue_rows, strict=True):
        require(len(residues) == DEGREE, "residue row length")
        require(
            all(
                coefficient % prime == int(residue)
                for coefficient, residue in zip(
                    coefficients, residues, strict=True
                )
            ),
            f"CRT coefficient congruence modulo {prime}",
        )

    recorded_norm = int(raw["exact_norm"])
    independent_norm = exact_norm(coefficients)
    require(independent_norm == recorded_norm, "independent exact norm")

    diagnostic_results = []
    for prime, root, expected in DIAGNOSTIC_REDUCTIONS:
        value = evaluate(coefficients, root, prime)
        require(value == expected, f"diagnostic determinant {prime}")
        diagnostic_results.append(
            {
                "prime": prime,
                "root17": root,
                "determinant": value,
            }
        )

    remaining, valuations = strip_s(recorded_norm)
    require(recorded_norm != 0, "replacement determinant norm must be nonzero")

    mutated = list(coefficients)
    mutated[0] += 1
    mutated_tuple = tuple(mutated)
    mutated_diagnostics = [
        evaluate(mutated_tuple, root, prime)
        for prime, root, _ in DIAGNOSTIC_REDUCTIONS
    ]
    require(
        any(
            mutated_value != expected
            for mutated_value, (_, _, expected) in zip(
                mutated_diagnostics, DIAGNOSTIC_REDUCTIONS, strict=True
            )
        ),
        "coefficient mutation must be rejected",
    )
    require(
        exact_norm(mutated_tuple) != recorded_norm,
        "coefficient mutation norm must differ",
    )

    output = {
        "schema": "P39-S449C-G1R-DETERMINANT-INDEPENDENT-VERIFICATION-v1",
        "status": (
            "PASS_G1R_DETERMINANT_S_UNIT"
            if remaining == 1
            else "PASS_G1R_DETERMINANT_RECONSTRUCTED"
        ),
        "method": (
            "Standalone binary-bound replay, deterministic prime audit, "
            "all CRT congruences, direct multiplication of 16 cyclotomic "
            "conjugates, the p=103 diagnostic reduction and coefficient mutation."
        ),
        "inputs": {
            "prepared_input": {
                "path": str(CRT_INPUT.relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(CRT_INPUT),
            },
            "compatible_binary": {
                "path": str(COMPATIBLE_BINARY.relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(COMPATIBLE_BINARY),
            },
            "raw_crt_result": {
                "path": str(RAW_RESULT.relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(RAW_RESULT),
            },
            "verifier": {
                "path": str(Path(__file__).resolve().relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(Path(__file__).resolve()),
            },
        },
        "reconstruction": {
            "entry_count": entry_count,
            "crt_prime_count": len(primes),
            "actual_modulus_bits": modulus.bit_length(),
            "signed_reconstruction_bound_bits": signed_bound_bits,
            "max_actual_coefficient_bits": max(
                abs(value).bit_length() for value in coefficients
            ),
            "coefficient_vector_sha256": canonical_hash(
                [str(value) for value in coefficients]
            ),
            "all_split_primes_valid": True,
            "all_crt_congruences_valid": True,
        },
        "diagnostic_reductions": diagnostic_results,
        "norm": {
            "exact_norm": str(recorded_norm),
            "exact_norm_bits": abs(recorded_norm).bit_length(),
            "s_valuations": valuations,
            "after_removing_2_3_17": str(remaining),
            "after_removing_2_3_17_bits": remaining.bit_length(),
            "non_s_cofactor_is_nontrivial": remaining > 1,
            "independently_recomputed": True,
        },
        "negative_control": {
            "mutation": "increase power-basis coefficient 0 by one",
            "mutated_diagnostic_determinants": mutated_diagnostics,
            "diagnostic_mismatch_detected": True,
            "norm_mismatch_detected": True,
        },
        "decision": (
            "The exact replacement determinant is reconstructed. Compute "
            "the exact ideal sum with the G0 determinant; neither its norm "
            "nor a rational norm gcd can replace that gate."
        ),
        "claim_boundary": (
            "This determines the principal ideal of the exact replacement "
            "minor. Global rho/D1 saturation requires the exact ideal sum "
            "with the G0 determinant."
        ),
    }
    OUTPUT.write_bytes(
        (json.dumps(output, indent=2, sort_keys=True) + "\n")
        .replace("\n", "\r\n")
        .encode("utf-8")
    )
    print(
        json.dumps(
            {
                "status": output["status"],
                "output": str(OUTPUT),
                "output_sha256": sha256_file(OUTPUT),
                "actual_coefficient_bits": output["reconstruction"][
                    "max_actual_coefficient_bits"
                ],
                "norm_bits": output["norm"]["exact_norm_bits"],
                "non_s_bits": output["norm"][
                    "after_removing_2_3_17_bits"
                ],
                "s_valuations": valuations,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
