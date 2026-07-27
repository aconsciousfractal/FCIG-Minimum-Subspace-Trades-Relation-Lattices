# Minimum Subspace Trades and Relation Lattices in Three Binary Designs

Companion package for the paper

> **Minimum Subspace Trades and Relation Lattices in Three Binary Designs**
> Oleksiy Babanskyy, 2026.

PDF: [paper/Minimum_Subspace_Trades_and_Relation_Lattices_in_Three_Binary_Designs.pdf](paper/Minimum_Subspace_Trades_and_Relation_Lattices_in_Three_Binary_Designs.pdf).

## What the paper proves

For three fixed group-invariant collections of four-dimensional subspaces of
<code>F_2^8</code>, the paper determines the minimum six-block opposite-regulus
trades, their exact censuses, rational generation, and the complete cubic layer
of the incidence toric ideals. It proves integral saturation at 2, 3, 17, 137,
219097, and 3288036131.

For the large <code>rho/B1</code> component, let <code>E_full</code> be the
complete matrix of all minimum-circuit equations over
<code>Z[zeta_17]</code>. It has 1317 columns and structural rank at most 1312.
Two exact order-1312 minors of <code>E_full</code>, obtained from different row
and column selections, generate an ideal of index

~~~text
17^21 = 69091933913008732880827217.
~~~

Therefore

~~~text
I_1312(E_full) Z[zeta_17, 1/(2*3*17)] = Z[zeta_17, 1/(2*3*17)],
~~~

so the complete equation module has structural rank 1312 at every prime of the
localized ring. This is a determinantal-ideal theorem about the complete
equation matrix, not a surjectivity claim for one fixed 1312-by-1317
presentation.

## What is and is not claimed

The analogous global gate remains open for

~~~text
rho*omega/B1, rho/B2, rho*omega/B2, rho/B3, rho*omega/B3.
~~~

The global Smith groups also remain open. Finite-prime screens are not promoted
to an unsupported global support statement.

## Evidence boundary

- The two sparse binaries are parsed independently and their displayed modular
  determinants are recomputed directly at (103,8) and (137,122).
- The frozen CRT transcript is audited for prime validity, every coefficient
  congruence, rigorous reconstruction bounds, uniqueness, exact norms, Smith
  form, and mutation controls. The package does not regenerate all 189 CRT
  determinants from the binaries.
- <code>certificates/legacy/</code> contains compact, hash-bound receipts for
  the earlier census, rational-generation, local-saturation, and selected-prime
  claims. The large raw research workspace remains in the source-locked P39
  archive.

## Quick start

~~~bash
python -m pip install -r requirements.txt
python scripts/check_manifest.py --closed-tree
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/verify_manifest_only.py
~~~

Expected aggregate final line:

~~~text
PASS_P39_EXT04_PUBLIC_PACKAGE
~~~

See [REPRODUCE.md](REPRODUCE.md) and
[README_REVIEWER.md](README_REVIEWER.md) for the exact scope.

## Locked finite objects

The three designs are pinned by canonical-key and point-mask SHA-256 hashes in
[docs/SOURCE_LOCK.md](docs/SOURCE_LOCK.md). Their construction is tied to
FCIG-Common-Marked-Lattice-Designs at commit
<code>40b3e716834e5c02e907cdadc067b3081d7f3227</code>.

## Layout

~~~text
paper/         manuscript sources and title-named PDF
scripts/       exact verifiers, manifest gate, isolated replay
results/       exact minor inputs, CRT records, regenerated receipts
certificates/  compact frozen receipts for earlier theorem blocks
docs/          claim, source, red-team, artifact, and release boundaries
~~~

Original content is covered by the MIT LICENSE; see LICENSE_SCOPE.md and
THIRD_PARTY_NOTICES.md.
