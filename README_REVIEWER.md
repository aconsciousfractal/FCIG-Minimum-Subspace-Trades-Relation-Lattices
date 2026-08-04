# Reviewer guide

## Fast audit route

1. Read the title-named PDF under <code>paper/</code>. The global
   <code>rho/B1</code> result is in Section 9.
2. Read <code>docs/CLAIM_LEDGER.md</code> and
   <code>docs/PUBLIC_CLAIM_BOUNDARY.md</code>.
3. Run:

   ~~~bash
   python scripts/check_manifest.py --closed-tree
   python scripts/verify_all.py
   python -O scripts/verify_all.py
   python scripts/verify_manifest_only.py
   ~~~

4. Confirm that both aggregate runs end in
   <code>PASS_MINIMUM_SUBSPACE_TRADES_PUBLIC_PACKAGE</code> and produce the same final
   receipt bytes.

## What the included replay establishes

- each sparse binary has the declared dimensions and hash;
- the two diagnostic determinants are recomputed directly from the binaries;
- the frozen CRT prime and coefficient transcript satisfies every recorded
  congruence and the rigorous signed-uniqueness bounds;
- exact cyclotomic norms are independently recomputed;
- the multiplication-lattice Smith diagonal is 17 repeated 11 times and 289
  repeated 5 times, with index <code>17^21</code>;
- both determinants are linked to distinct row and column selections inside
  the same complete equation matrix;
- the order-1312 determinantal ideal of that complete matrix becomes the unit
  ideal after 17 is inverted.

The suite does not recompute every CRT determinant from the two binary matrices.
Those modular determinant residues are source-admitted construction transcripts;
the public verifier audits their arithmetic consequences fail-closed.

## Evidence tiers

| Tier | Included evidence | Reviewer conclusion |
|---|---|---|
| A | sparse binaries, selection manifests, CRT transcripts, exact arithmetic verifiers | direct diagnostic determinant checks plus independent transcript, norm, ideal-sum, and Smith audit |
| B | compact frozen receipts and circuit manifest | hash-bound audit of earlier paper claims |
| C | cited mathematical literature | imported theorems, not re-proved here |

Tier B is a hash-bound audit of the distributed receipts, not a clean-room
regeneration of the earlier large matrices. Those matrices are not a hidden
dependency of the included replay and are not claimed as independently
reproduced here.

## Claims deliberately absent

- no analogous global theorem for the other five large maps;
- no complete global Smith group;
- no global support statement for all components;
- no novelty, priority, or firstness claim;

## Finite-object lock

The exact three designs are identified by full canonical-key and point-mask
hashes in <code>docs/SOURCE_LOCK.md</code>, and their construction repository
is pinned at commit
<code>40b3e716834e5c02e907cdadc067b3081d7f3227</code>.

## Repository status

This is the public reviewer-sized companion package for release v1.1.0. The
release does not assert a DOI, journal submission, acceptance, or independent
external reproduction.
