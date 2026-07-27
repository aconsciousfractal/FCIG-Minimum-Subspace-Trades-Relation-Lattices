# Reproducing the P39 EXT04 package

## Requirements

- Python 3.10 or newer;
- `sympy` from `requirements.txt`;
- for the paper only: a LaTeX installation providing `pdflatex`, `amsmath`,
  `amsthm`, `mathtools`, `booktabs`, `enumitem`, `hyperref`, and `cleveref`.

The mathematical replay is exact: integer arithmetic, finite-field
determinants, CRT uniqueness bounds, cyclotomic multiplication, and integer
Smith normal form. No floating-point computation or random seed is used.

The four verifier receipts are byte-locked using explicit CRLF serialization.
The included writers emit that serialization identically on all platforms, and
`.gitattributes` treats JSON certificates as byte-preserved artifacts. This
avoids checkout-dependent receipt or manifest drift.

## One-command mathematical replay

From the package root:

```bash
python -m pip install -r requirements.txt
python scripts/verify_all.py
```

The gate runs, in order:

```text
s449c_verify_g1r_replacement_minor.py
s449c_verify_g1r_principal_determinant.py
s449f_verify_reverse_row_determinant.py
s449f_verify_rho_d1_global_gate.py
check_manifest.py
```

Expected receipt hashes:

```text
95D0D02E6D233DD25CEA69C07C33A3BCF2D850DE3708E2A1115AB6FEDFE56A15
0077E7FCB73D61EF584E3E503CDA539743A118AA631261A0C2DD75BFC8F1DD84
B7F420235A9947C12E28CD5A887EF883BD7F8D0F37836864B18C6365416BDE88
511CD53641E7426650FAA3799BA7D7F3B514F51CA98B69766ADB5E00AE33EBDD
```

The final JSON is `results/public_package_verification.json`.

## Optimized-mode control

```bash
python scripts/verify_all.py
sha256sum results/public_package_verification.json
python -O scripts/verify_all.py
sha256sum results/public_package_verification.json
```

The two receipt hashes must agree. Every assertion that is claim-critical is
implemented with explicit exceptions and remains active under `python -O`.

## Manifest

```bash
python scripts/check_manifest.py
```

`MANIFEST_SHA256.txt` pins the environment-independent package files. It omits
itself, the compiled PDF and LaTeX auxiliary files, and the regenerated
`results/public_package_verification.json`.

## Build the paper

As in the two companion P39 repositories, rebuild from `paper/` with the
title-named job target:

```bash
cd paper
job="Minimum_Subspace_Trades_and_Relation_Lattices_in_Three_Binary_Designs"
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
```

The bibliography is inline, so no BibTeX/Biber pass is required. The source
suppresses volatile PDF dates and trailer IDs. PDF bytes can still depend on
the TeX distribution, so the PDF is reported but not hash-pinned by the source
manifest.

## What is not fully replayed here

The complete historical generation of every earlier census and selected-prime
screen uses the much larger source-locked P39 archive and is not duplicated in
this reviewer-sized package. The relevant frozen receipts and the full minimum
circuit manifest are included under `certificates/legacy/`; see
`README_REVIEWER.md`.
