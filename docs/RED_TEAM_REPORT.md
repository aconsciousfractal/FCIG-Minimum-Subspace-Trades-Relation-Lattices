# Red-team report

Date: 2026-07-28
Gate: external global-gate audit, independent final red team, and public-package remediation.

## Verdict

The critical external finding was confirmed independently. The two exact
determinants use different equation-row bases and different 1312-column
selections. They are therefore not maximal minors of one fixed 1312-by-1317
presentation. They are, however, order-1312 minors of the same complete
equation matrix.

The manuscript and package now state the correct theorem:

~~~text
I_1312(E_full) R[1/(2*3*17)] = R[1/(2*3*17)].
~~~

The two determinant ideals have lattice-sum index 17^21, so this conclusion is
fully supported. The manuscript contains only the final theorem and direct
certificates; it contains no narrative about a 137 error or its repair.

## Remediations completed in source

- replaced the fixed-map cokernel/Fitting claim by the complete-equation
  determinantal-ideal and structural-rank theorem;
- distinguished the two row and column selections explicitly;
- removed the error-and-repair narrative from the academic manuscript;
- added direct binary recomputation of the reverse determinant at (137,122);
- narrowed CRT replay language to the work actually performed;
- disclosed the compact-receipt boundary for earlier results;
- corrected the reverse binary hash;
- pinned the companion design repository, commit, and object hashes;
- hardened manifest checking against symlinks, realpath escape, and hidden
  unmanifested dependencies;
- added an isolated manifest-only replay and CI matrix;
- pinned SymPy exactly;
- added Maliakas–Stergiopoulou prior art and a preferred paper citation;
- separated release attestation from the circular source manifest;
- corrected the good-prime lemma from a cokernel claim to the exact structural-rank deficiency identity;
- corrected the reverse-row receipt to name G1 plus reverse as the decisive pair and G0 plus reverse as the nonunit negative control;
- made the six source-admitted design hashes and audit-time publication state explicit.

## Remaining boundaries

The other five large global gates and the complete Smith groups remain open.
The public package does not regenerate all historical raw computations or all
189 CRT determinants from the sparse binaries. These are disclosed evidence
boundaries, not hidden assumptions.

Final pass/fail hashes, PDF hash, visual QA, and command results belong in
<code>RELEASE_ATTESTATION.json</code> after the complete rebuild.
