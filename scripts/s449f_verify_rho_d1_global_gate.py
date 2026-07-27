#!/usr/bin/env python3
"""Independently verify the two-minor S4.49F rho/D1 global gate."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.set_int_max_str_digits(0)

from sympy import Matrix
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


PROJECT_ROOT = Path(__file__).resolve().parents[1]
G0_RAW = PROJECT_ROOT / "results" / "s449b_g05_crt_raw.json"
G1_RAW = PROJECT_ROOT / "results" / "s449c_g1r_crt_raw.json"
REVERSE_RAW = PROJECT_ROOT / "results" / "s449f_reverse_row_crt_raw.json"
G1_VERIFICATION = (
    PROJECT_ROOT
    / "results"
    / "s449c_g1r_principal_determinant_verification.json"
)
REVERSE_VERIFICATION = (
    PROJECT_ROOT
    / "results"
    / "s449f_reverse_row_determinant_verification.json"
)
SOURCE_IDEAL_SUM = (
    PROJECT_ROOT / "results" / "s449f_rho_d1_g1_reverse_row_ideal_sum.json"
)
OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "s449f_rho_d1_global_gate_verification.json"
)

DEGREE = 16
EXPECTED_INDEX = 17**21
EXPECTED_SMITH = [17] * 11 + [17**2] * 5

CoefficientVector = tuple[int, ...]


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


def multiply(
    left: CoefficientVector, right: CoefficientVector
) -> CoefficientVector:
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
    return tuple(cyclic[index] - eliminated for index in range(DEGREE))


def conjugate(
    coefficients: CoefficientVector, exponent: int
) -> CoefficientVector:
    cyclic = [0] * 17
    for index, value in enumerate(coefficients):
        if value:
            cyclic[(index * exponent) % 17] += value
    eliminated = cyclic[16]
    return tuple(cyclic[index] - eliminated for index in range(DEGREE))


def exact_norm(coefficients: CoefficientVector) -> int:
    product = (1,) + (0,) * 15
    for exponent in range(1, 17):
        product = multiply(product, conjugate(coefficients, exponent))
    require(not any(product[1:]), "norm must land in Z")
    return product[0]


def multiplication_matrix(coefficients: CoefficientVector) -> Matrix:
    columns = []
    for basis_index in range(DEGREE):
        basis = [0] * DEGREE
        basis[basis_index] = 1
        columns.append(multiply(coefficients, tuple(basis)))
    return Matrix(
        DEGREE,
        DEGREE,
        lambda row, column: columns[column][row],
    )


def load_determinant(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    require(
        document["status"] == "PASS_EXACT_BOUND_CERTIFIED_RECONSTRUCTION",
        f"{path.name}: raw status",
    )
    coefficients = tuple(
        int(value) for value in document["exact_determinant_coefficients"]
    )
    require(len(coefficients) == DEGREE, "coefficient length")
    recorded_norm = int(document["exact_norm"])
    recomputed_norm = exact_norm(coefficients)
    require(recomputed_norm == recorded_norm, f"{path.name}: exact norm")
    matrix = multiplication_matrix(coefficients)
    require(
        int(matrix.det()) == recorded_norm,
        f"{path.name}: multiplication-matrix determinant",
    )
    return {
        "path": path,
        "sha256": sha256_file(path),
        "coefficients": coefficients,
        "norm": recorded_norm,
        "matrix": matrix,
    }


def ideal_sum(determinants: list[dict[str, Any]]) -> dict[str, Any]:
    generators = Matrix.hstack(
        *(determinant["matrix"] for determinant in determinants)
    )
    smith = smith_normal_form(generators, domain=ZZ)
    diagonal = [abs(int(smith[index, index])) for index in range(DEGREE)]
    require(all(diagonal), "ideal sum must have full rank")
    index = math.prod(diagonal)
    norm_gcd = 0
    for determinant in determinants:
        norm_gcd = math.gcd(norm_gcd, abs(determinant["norm"]))
    require(norm_gcd % index == 0, "index divides norm gcd")
    remaining = index
    valuations = {}
    for prime in (2, 3, 17):
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        valuations[str(prime)] = exponent
    return {
        "generator_matrix_shape": [DEGREE, DEGREE * len(determinants)],
        "smith_diagonal": diagonal,
        "ideal_sum_index": index,
        "ideal_sum_index_bits": index.bit_length(),
        "norm_gcd": norm_gcd,
        "norm_gcd_bits": norm_gcd.bit_length(),
        "s_valuations": valuations,
        "after_removing_2_3_17": remaining,
        "after_removing_2_3_17_bits": remaining.bit_length(),
    }


def main() -> int:
    g0 = load_determinant(G0_RAW)
    g1 = load_determinant(G1_RAW)
    reverse = load_determinant(REVERSE_RAW)

    g1_receipt = json.loads(G1_VERIFICATION.read_text(encoding="utf-8"))
    reverse_receipt = json.loads(
        REVERSE_VERIFICATION.read_text(encoding="utf-8")
    )
    require(
        g1_receipt["inputs"]["raw_crt_result"]["sha256"] == g1["sha256"],
        "G1 raw hash linkage",
    )
    require(
        reverse_receipt["inputs"]["raw_crt_result"]["sha256"]
        == reverse["sha256"],
        "reverse-row raw hash linkage",
    )

    decisive = ideal_sum([g1, reverse])
    require(
        decisive["smith_diagonal"] == EXPECTED_SMITH,
        "decisive Smith diagonal",
    )
    require(
        decisive["ideal_sum_index"] == EXPECTED_INDEX,
        "decisive ideal index",
    )
    require(
        decisive["after_removing_2_3_17"] == 1,
        "localized ideal must be unit",
    )

    source = json.loads(SOURCE_IDEAL_SUM.read_text(encoding="utf-8"))
    require(source["status"] == "PASS_LOCALIZED_IDEAL_UNIT", "source status")
    require(
        [int(value) for value in source["smith_diagonal"]]
        == decisive["smith_diagonal"],
        "source Smith diagonal",
    )
    require(
        int(source["ideal_sum_index"])
        == decisive["ideal_sum_index"],
        "source ideal index",
    )

    negative = ideal_sum([g0, reverse])
    require(
        negative["after_removing_2_3_17"] > 1,
        "negative-control pair must remain nonunit",
    )
    require(
        negative["after_removing_2_3_17"].bit_length() == 66,
        "negative-control residual size",
    )

    output = {
        "schema": "P39-S449F-RHO-D1-GLOBAL-GATE-VERIFICATION-v1",
        "status": "PASS_RHO_D1_GLOBAL_GATE_AWAY_FROM_S",
        "method": (
            "Standalone cyclotomic multiplication, direct 16-conjugate "
            "norms, multiplication-lattice determinants and Smith form of "
            "the 16x32 concatenated generator matrix."
        ),
        "inputs": {
            "g1_replacement_determinant": {
                "path": str(G1_RAW.relative_to(PROJECT_ROOT)),
                "sha256": g1["sha256"],
                "coefficient_vector_sha256": canonical_hash(
                    [str(value) for value in g1["coefficients"]]
                ),
            },
            "reverse_row_determinant": {
                "path": str(REVERSE_RAW.relative_to(PROJECT_ROOT)),
                "sha256": reverse["sha256"],
                "coefficient_vector_sha256": canonical_hash(
                    [str(value) for value in reverse["coefficients"]]
                ),
            },
            "source_ideal_sum": {
                "path": str(SOURCE_IDEAL_SUM.relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(SOURCE_IDEAL_SUM),
            },
            "verifier": {
                "path": str(
                    Path(__file__).resolve().relative_to(PROJECT_ROOT)
                ),
                "sha256": sha256_file(Path(__file__).resolve()),
            },
        },
        "decisive_two_minor_ideal_sum": {
            **decisive,
            "smith_diagonal": [
                str(value) for value in decisive["smith_diagonal"]
            ],
            "ideal_sum_index": str(decisive["ideal_sum_index"]),
            "norm_gcd": str(decisive["norm_gcd"]),
            "after_removing_2_3_17": str(
                decisive["after_removing_2_3_17"]
            ),
            "exact_identity": "ideal_sum_index = 17^21",
            "localized_ring": "Z[zeta_17,1/(2*3*17)]",
            "localized_unit": True,
        },
        "negative_control": {
            "pair": [
                str(G0_RAW.relative_to(PROJECT_ROOT)),
                str(REVERSE_RAW.relative_to(PROJECT_ROOT)),
            ],
            "mutation": (
                "replace the p=103 G1 column-replacement determinant by "
                "the original G0 determinant"
            ),
            "ideal_sum_index_bits": negative["ideal_sum_index_bits"],
            "s_valuations": negative["s_valuations"],
            "after_removing_2_3_17": str(
                negative["after_removing_2_3_17"]
            ),
            "after_removing_2_3_17_bits": negative[
                "after_removing_2_3_17_bits"
            ],
            "localized_unit": False,
        },
        "conclusion": (
            "The two displayed order-1312 minors belong to the complete "
            "equation matrix determinantal ideal and generate the unit "
            "ideal after inverting 17. Therefore that complete equation "
            "matrix has structural rank 1312 away from S."
        ),
        "claim_boundary": (
            "This closes rho/D1 only. It does not close the other five "
            "large maps, O-75/O-76, or any P42 tomography claim."
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
                "output_sha256": sha256_file(OUTPUT),
                "ideal_sum_index": output[
                    "decisive_two_minor_ideal_sum"
                ]["ideal_sum_index"],
                "smith_diagonal": output[
                    "decisive_two_minor_ideal_sum"
                ]["smith_diagonal"],
                "negative_control_non_s_bits": output["negative_control"][
                    "after_removing_2_3_17_bits"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
