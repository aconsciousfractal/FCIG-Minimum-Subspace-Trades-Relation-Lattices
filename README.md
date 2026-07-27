# Minimum Subspace Trades and Relation Lattices in Three Binary Designs

Public companion repository for the paper

> **Minimum Subspace Trades and Relation Lattices in Three Binary Designs**
> Oleksiy Babanskyy, 2026.

Repository:
[`aconsciousfractal/FCIG-Minimum-Subspace-Trades-Relation-Lattices`](https://github.com/aconsciousfractal/FCIG-Minimum-Subspace-Trades-Relation-Lattices).
This is a reproducibility release, not a novelty or priority claim.

## Main result

For three fixed group-invariant collections of four-dimensional subspaces of
`F_2^8`, the paper determines the minimum six-block opposite-regulus trades,
their exact censuses, rational generation, and the complete cubic layer of the
incidence toric ideals.

The extension completed here adds an exact characteristic-zero result for one
large component map. If

```text
A = F_{rho,1}^{full}: Z[zeta_17]^1317 -> Z[zeta_17]^1312,
```

then two exact maximal minors generate an ideal of index

```text
17^21 = 69091933913008732880827217,
```

and therefore

```text
coker(A) tensor Z[zeta_17, 1/(2*3*17)] = 0.
```

This is a global theorem for the complete `rho/B1` map, not merely another
finite-prime screen.

## Scope boundary

The package does **not** assert the analogous global theorem for

```text
rho*omega/B1, rho/B2, rho*omega/B2, rho/B3, rho*omega/B3.
```

Those five maps are intentionally deferred. The global Smith groups also
remain open. The finite-prime results proved in the paper are not promoted into
an unsupported global support statement.

## What can be replayed here

- `scripts/verify_all.py` deeply replays the two exact `1312 x 1312` minors,
  their CRT reconstruction and norm checks, and the final `16 x 32`
  multiplication-lattice Smith calculation.
- `certificates/legacy/` freezes the receipts and compact manifests underlying
  the earlier census, rational-generation, local-saturation, and selected-prime
  claims.
- The very large historical raw matrix/circuit workspace is deliberately not
  duplicated. It remains in the source-locked P39 research archive. This
  boundary is documented in `README_REVIEWER.md` and
  `docs/PUBLIC_CLAIM_BOUNDARY.md`.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/check_manifest.py
```

Expected final line:

```text
PASS_P39_EXT04_PUBLIC_PACKAGE
```

See `REPRODUCE.md` for the paper build and the exact expected hashes.

## Layout

```text
paper/         LaTeX source and compiled paper PDF
scripts/       independent exact verifiers and package gate
results/       exact minor inputs, CRT records, and regenerated receipts
certificates/  frozen receipts for the earlier theorem blocks
docs/          claim, source, red-team, artifact, and release boundaries
```

All original content in this directory is covered by the MIT `LICENSE`; see
`LICENSE_SCOPE.md` and `THIRD_PARTY_NOTICES.md`.
