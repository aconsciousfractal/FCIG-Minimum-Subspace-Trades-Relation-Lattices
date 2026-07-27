# Red-team report

Date: 2026-07-27
Gate: S4.49J standalone-repository and title-named-PDF remediation audit.

## Result

No unresolved claim-critical defect remains in the integrated manuscript.

## Checks passed

- the global statement is restricted to the complete `rho/B1` map;
- the exact domain/codomain dimensions are `1317 -> 1312`;
- both maximal minors are exact characteristic-zero objects;
- finite-field reductions are diagnostics, not substitutes for the exact
  determinant proof;
- CRT modulus bounds exceed the certified coefficient bounds;
- the `16 x 32` multiplication lattice is rebuilt independently;
- the Smith diagonal and index imply unit ideal only after inverting
  `2*3*17`;
- the Fitting-ideal implication is stated with its module-theoretic scope;
- the negative-control residual is
  `47821880003927349029` (an earlier prose-only decimal was corrected);
- the other five global maps and the global Smith groups remain open;
- P39/P42 tomography is cross-referenced but not merged logically;
- the manuscript has no novelty/priority assertion;
- normal and `python -O` replays are byte-identical;
- the complete PDF was compiled and visually inspected page by page;
- the repository is a standalone clone directly under the local repository
  root, with `origin` bound to the public GitHub repository;
- the compiled PDF is title-named directly under `paper/`, matching both
  earlier P39 companion repositories;
- every PDF/build/path reference names that canonical title-named artifact;
- JSON certificates remain byte-preserved because some receipts intentionally
  use CRLF serialization, the sole documented exception to the two models'
  text-normalized JSON convention.

## Release evidence boundary

The public repository adopts the reviewer-sized Tier A/Tier B boundary. The
full historical raw archive may be deposited separately later, but it is not
required for the autonomous replay of the global `rho/B1` theorem and is not
presented as if it were included here.
