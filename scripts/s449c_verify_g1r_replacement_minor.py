#!/usr/bin/env python3
"""Independently verify the S4.49C rho/D1 p=103 replacement minor."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BINARY = PROJECT_ROOT / "results" / "s449c_g1r_replacement_minor.bin"
DEFAULT_MANIFEST = PROJECT_ROOT / "results" / "s449c_g1r_replacement_minor.json"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "s449c_g1r_replacement_minor_verification.json"
)

SCHEMA = "P39-S449C-G1R-REPLACEMENT-MINOR-VERIFICATION-v1"
SOURCE_SCHEMA = "P39-S449C-G1R-RHO-D1-REPLACEMENT-MINOR-v1"
MAGIC = b"P39S449CG1MIN1\0\0"
HEADER = struct.Struct("<16sIIIIQ")
ENTRY_PREFIX = struct.Struct("<II")
COEFFICIENTS = struct.Struct("<16q")
DEGREE = 16
TARGET = 1312
PRIME = 103
ROOT = 8
EXPECTED_DETERMINANT = 89

CoefficientVector = tuple[int, ...]
ExactRow = dict[int, CoefficientVector]
SparseRow = dict[int, int]


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


def permutation_parity(sequence: list[int]) -> int:
    require(len(sequence) == len(set(sequence)), "pivot columns must be unique")
    visited = [False] * len(sequence)
    cycles = 0
    for start in range(len(sequence)):
        if visited[start]:
            continue
        cycles += 1
        current = start
        while not visited[current]:
            visited[current] = True
            current = sequence[current]
    return (len(sequence) - cycles) & 1


def read_exact_matrix(path: Path) -> tuple[list[ExactRow], dict[str, int]]:
    rows: list[ExactRow] = [dict() for _ in range(TARGET)]
    with path.open("rb") as handle:
        raw_header = handle.read(HEADER.size)
        require(len(raw_header) == HEADER.size, "truncated binary header")
        magic, version, degree, row_count, column_count, entry_count = (
            HEADER.unpack(raw_header)
        )
        require(magic == MAGIC, "binary magic")
        require(version == 1, "binary version")
        require(degree == DEGREE, "coefficient degree")
        require(row_count == TARGET, "row count")
        require(column_count == TARGET, "column count")

        previous_key: tuple[int, int] | None = None
        for _ in range(entry_count):
            raw_prefix = handle.read(ENTRY_PREFIX.size)
            raw_coefficients = handle.read(COEFFICIENTS.size)
            require(
                len(raw_prefix) == ENTRY_PREFIX.size
                and len(raw_coefficients) == COEFFICIENTS.size,
                "truncated binary entry",
            )
            row_index, column_index = ENTRY_PREFIX.unpack(raw_prefix)
            coefficients = COEFFICIENTS.unpack(raw_coefficients)
            require(row_index < TARGET, "entry row index")
            require(column_index < TARGET, "entry column index")
            key = (row_index, column_index)
            require(
                previous_key is None or previous_key < key,
                "entries must be strictly row-major",
            )
            require(any(coefficients), "stored zero polynomial")
            rows[row_index][column_index] = coefficients
            previous_key = key
        require(handle.read(1) == b"", "trailing binary data")

    return rows, {
        "version": version,
        "degree": degree,
        "rows": row_count,
        "columns": column_count,
        "entry_count": entry_count,
    }


def evaluate_polynomial(coefficients: CoefficientVector) -> int:
    value = 0
    for coefficient in reversed(coefficients):
        value = (value * ROOT + coefficient) % PRIME
    return value


def evaluate_matrix(exact_rows: list[ExactRow]) -> list[SparseRow]:
    finite_rows: list[SparseRow] = []
    for exact_row in exact_rows:
        finite_row = {}
        for column, coefficients in exact_row.items():
            value = evaluate_polynomial(coefficients)
            if value:
                finite_row[column] = value
        finite_rows.append(finite_row)
    return finite_rows


def transpose(rows: list[SparseRow]) -> list[SparseRow]:
    transposed: list[SparseRow] = [dict() for _ in range(TARGET)]
    for row_index, row in enumerate(rows):
        for column_index, value in row.items():
            transposed[column_index][row_index] = value
    return transposed


def rank_and_determinant(rows: list[SparseRow]) -> dict[str, Any]:
    pivots: dict[int, SparseRow] = {}
    pivot_order: list[int] = []
    pivot_product = 1
    for source_row in rows:
        reduced = {
            column: value % PRIME
            for column, value in source_row.items()
            if value % PRIME
        }
        for pivot_column in pivot_order:
            factor = reduced.get(pivot_column, 0)
            if not factor:
                continue
            for column, value in pivots[pivot_column].items():
                updated = (reduced.get(column, 0) - factor * value) % PRIME
                if updated:
                    reduced[column] = updated
                elif column in reduced:
                    del reduced[column]
        if not reduced:
            continue
        pivot_column = min(reduced)
        pivot_value = reduced[pivot_column]
        inverse = pow(pivot_value, -1, PRIME)
        pivots[pivot_column] = {
            column: value * inverse % PRIME
            for column, value in reduced.items()
        }
        pivot_order.append(pivot_column)
        pivot_product = pivot_product * pivot_value % PRIME

    result: dict[str, Any] = {
        "rank": len(pivot_order),
        "pivot_order_sha256": canonical_hash(pivot_order),
    }
    if len(rows) == TARGET and len(pivot_order) == TARGET:
        parity = permutation_parity(pivot_order)
        result["pivot_parity"] = parity
        result["determinant"] = (
            pivot_product if parity == 0 else (-pivot_product) % PRIME
        )
    return result


def update_reduction_hash(
    digest: Any, row_id: list[int], row: SparseRow
) -> None:
    digest.update(struct.pack("<QI", row_id[0], row_id[1]))
    digest.update(struct.pack("<I", len(row)))
    for column, value in sorted(row.items()):
        digest.update(struct.pack("<II", column, value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source = json.loads(args.manifest.read_text(encoding="utf-8"))
    require(source["schema"] == SOURCE_SCHEMA, "source schema")
    require(
        source["status"] == "PASS_G1R_EXACT_REPLACEMENT_MINOR",
        "source status",
    )

    exact_rows, binary_header = read_exact_matrix(args.binary)
    binary_sha256 = sha256_file(args.binary)
    matrix_manifest = source["matrix"]
    require(binary_sha256 == matrix_manifest["binary_sha256"], "binary hash")
    require(
        args.binary.stat().st_size == matrix_manifest["binary_bytes"],
        "binary byte count",
    )
    require(
        binary_header["entry_count"] == matrix_manifest["entry_count"],
        "binary entry count",
    )
    require(
        sum(len(row) for row in exact_rows)
        == binary_header["entry_count"],
        "parsed entry count",
    )

    selection = source["selection"]
    selected_rows = selection["selected_rows"]
    require(len(selected_rows) == TARGET, "selected row count")
    require(
        canonical_hash(selected_rows) == selection["selected_rows_sha256"],
        "selected row hash",
    )
    selected_columns = selection["canonical_selected_columns"]
    require(len(selected_columns) == TARGET, "selected column count")
    require(
        selected_columns == sorted(selected_columns)
        and len(set(selected_columns)) == TARGET,
        "canonical column order",
    )
    require(
        canonical_hash(selected_columns)
        == selection["canonical_selected_columns_sha256"],
        "selected column hash",
    )
    require(
        selected_rows[-1] == selection["restoring_row"] == [2863, 0],
        "restoring row",
    )

    finite_rows = evaluate_matrix(exact_rows)
    reduction_digest = hashlib.sha256()
    for row_id, finite_row in zip(selected_rows, finite_rows, strict=True):
        update_reduction_hash(reduction_digest, row_id, finite_row)
    source_reduction = source["diagnostic_reductions"][0]
    require(source_reduction["prime"] == PRIME, "source prime")
    require(source_reduction["root17"] == ROOT, "source root")
    require(
        reduction_digest.hexdigest()
        == source_reduction["entrywise_reduction_sha256"],
        "entrywise reduction hash",
    )

    transpose_certificate = rank_and_determinant(transpose(finite_rows))
    require(transpose_certificate["rank"] == TARGET, "transpose rank")
    require(
        transpose_certificate["determinant"] == EXPECTED_DETERMINANT,
        "transpose determinant",
    )
    require(
        source_reduction["canonical_determinant"] == EXPECTED_DETERMINANT,
        "source determinant",
    )
    prefix_certificate = rank_and_determinant(finite_rows[:-1])
    require(prefix_certificate["rank"] == TARGET - 1, "prefix rank")

    negative_transpose = transpose(finite_rows)
    negative_transpose[-1] = dict(negative_transpose[0])
    negative_certificate = rank_and_determinant(negative_transpose)
    require(
        negative_certificate["rank"] < TARGET,
        "duplicate-column negative control must lose rank",
    )

    output = {
        "schema": SCHEMA,
        "status": "PASS_INDEPENDENT_G1R_REPLACEMENT_VERIFICATION",
        "method": {
            "parser": "standalone binary parser; no import from the builder",
            "determinant": "sparse modular elimination on the transposed matrix",
            "prefix": "independent rank on the first 1311 original rows",
        },
        "inputs": {
            "binary": {
                "path": str(args.binary.relative_to(PROJECT_ROOT)),
                "sha256": binary_sha256,
            },
            "source_manifest": {
                "path": str(args.manifest.relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(args.manifest),
            },
            "verifier": {
                "path": str(Path(__file__).resolve().relative_to(PROJECT_ROOT)),
                "sha256": sha256_file(Path(__file__).resolve()),
            },
        },
        "binary_header": binary_header,
        "diagnostic_reduction": {
            "prime": PRIME,
            "root17": ROOT,
            "entrywise_reduction_sha256": reduction_digest.hexdigest(),
            "transpose_rank": transpose_certificate["rank"],
            "transpose_pivot_order_sha256": (
                transpose_certificate["pivot_order_sha256"]
            ),
            "transpose_pivot_parity": transpose_certificate["pivot_parity"],
            "transpose_determinant": transpose_certificate["determinant"],
            "original_prefix_rank": prefix_certificate["rank"],
        },
        "negative_control": {
            "prime": PRIME,
            "mutation": (
                "replace the final transposed row by the first "
                "(duplicate an original column)"
            ),
            "rank": negative_certificate["rank"],
            "expected": f"rank < {TARGET}",
        },
        "claim_boundary": (
            "This independently verifies the exact replacement artifact and "
            "its p=103 reduction. The determinant ideal and its ideal sum "
            "with the G0 determinant are not computed here."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        (json.dumps(output, indent=2, sort_keys=True) + "\n")
        .replace("\n", "\r\n")
        .encode("utf-8")
    )
    print(
        json.dumps(
            {
                "status": output["status"],
                "output": str(args.output),
                "output_sha256": sha256_file(args.output),
                "determinant": transpose_certificate["determinant"],
                "negative_control_rank": negative_certificate["rank"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
