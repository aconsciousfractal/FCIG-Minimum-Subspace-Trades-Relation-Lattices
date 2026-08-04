# Reproducing the public package

## Requirements

- Python 3.10 or newer;
- SymPy 1.14.0, pinned by <code>requirements.txt</code>;
- for the paper, a LaTeX installation providing pdflatex, amsmath, amsthm,
  mathtools, booktabs, enumitem, hyperref, and cleveref.

The arithmetic replay uses integers, finite fields, CRT uniqueness bounds,
cyclotomic multiplication, and integer Smith normal form. No floating-point
computation or random seed is used.

## Package and mathematical gates

From the package root:

~~~bash
python -m pip install -r requirements.txt
python scripts/check_manifest.py --closed-tree
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/verify_manifest_only.py
~~~

The aggregate gate runs, in order:

~~~text
s449c_verify_g1r_replacement_minor.py
s449c_verify_g1r_principal_determinant.py
s449f_verify_reverse_row_determinant.py
s449f_verify_rho_d1_global_gate.py
check_manifest.py
~~~

The generated final JSON is
<code>results/public_package_verification.json</code>. Normal and optimized
runs must produce identical bytes. Claim-critical checks use explicit
exceptions and remain active under <code>python -O</code>.

The manifest-only command copies exactly the files named by
<code>MANIFEST_SHA256.txt</code> into an isolated temporary directory and
repeats both aggregate runs. This detects hidden dependencies on unmanifested
files.

## Evidence boundary

The G-selection verifier directly reconstructs its diagnostic determinant at
(103,8); the reverse-row verifier directly reconstructs its diagnostic
determinant at (137,122). The CRT reconstruction routes then verify the frozen
split-prime list, every recorded coefficient congruence, Hadamard/Fourier
bounds, signed uniqueness, exact cyclotomic norms, and mutations. They do not
regenerate all 189 CRT modular determinants from the sparse binaries.

Earlier census, rational-generation, local-saturation, and selected-prime
claims use compact hash-bound receipts under <code>certificates/legacy/</code>.
The package audits those distributed receipts but does not claim to regenerate
the earlier large matrices from an undistributed workspace.

## Manifest

<code>MANIFEST_SHA256.txt</code> pins all source and evidence files. The
closed-tree mode rejects symlinks, realpath escapes, and non-build files absent
from the manifest. The manifest itself, compiled PDF, LaTeX auxiliary files,
regenerated aggregate receipt, and release attestation are explicit exclusions
to avoid circular hashing.

## Build the paper

From <code>paper/</code>:

~~~bash
job="Minimum_Subspace_Trades_and_Relation_Lattices_in_Three_Binary_Designs"
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
~~~

The bibliography is inline. The source suppresses volatile PDF dates and
trailer IDs. PDF bytes may still depend on the TeX distribution, so the source
manifest does not hash-pin the PDF; <code>RELEASE_ATTESTATION.json</code> binds
the actual public-release PDF and final receipt.
