# Reviewer guide

## Fast audit route

1. Read the abstract, Introduction, Section 8, and Section 9 of
   `paper/main.tex` and its included section files.
2. Read `docs/CLAIM_LEDGER.md` and `docs/PUBLIC_CLAIM_BOUNDARY.md`.
3. Run:

   ```bash
   python scripts/verify_all.py
   python -O scripts/verify_all.py
   ```

4. Confirm that both runs end in `PASS_P39_EXT04_PUBLIC_PACKAGE` and that
   `results/public_package_verification.json` is byte-identical.
5. Run `python scripts/check_manifest.py`.

## What the deep replay establishes

The included exact artifacts independently establish:

- the structural validity of the G1-replacement maximal minor;
- the exact CRT reconstruction and cyclotomic norm of that determinant;
- the exact CRT reconstruction and cyclotomic norm of the reverse-row minor;
- the Smith diagonal of the sum of their multiplication lattices:
  `17` repeated 11 times and `289` repeated 5 times;
- index `17^21`;
- the localized surjectivity of the complete `rho/B1` component map away from
  `2`, `3`, and `17`;
- the failure of the older G0/reverse-row pair as a negative control, with
  residual factor `47821880003927349029`.

## Evidence tiers

| Tier | Included evidence | Reviewer conclusion |
|---|---|---|
| A | binaries, CRT inputs/raw outputs, four independent verifiers | clean replay of the new global `rho/B1` theorem |
| B | compact frozen receipts and the complete circuit manifest | hash-bound audit of earlier paper claims |
| C | cited mathematical literature | imported theorems, not re-proved here |

Tier B is intentionally not represented as a clean-room replay of the full
historical 500+ MB research workspace. Before an actual public release, the
owner may either keep this reviewer-sized boundary or add an archival data
deposit. Neither choice changes the theorem proved by the Tier A replay.

## Claims deliberately absent

- no analogous global theorem for the other five large maps;
- no complete global Smith group;
- no statement that all support is contained in `{2,3,17}`;
- no novelty, priority, or “first” claim;
- no theorem imported from the separate P42 tomography project.

## Repository status

This is the public companion repository. The initial release is the
reviewer-sized evidence package described above; the full historical raw
workspace is not silently imported into its claim boundary. No DOI or journal
acceptance is asserted.
