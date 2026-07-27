# Claim ledger

Status vocabulary: `PROVED`, `COMPUTER-ASSISTED PROVED`, `IMPORTED`, `OPEN`,
`NOT CLAIMED`.

| ID | Claim | Status | Main evidence |
|---|---|---|---|
| C1 | Minimum point trades in the locked triple are six-block opposite-regulus trades | PROVED + IMPORTED classification | paper Sections 3–4; cited Krotov classification |
| C2 | Exact censuses of minimum circuits for all three configurations | COMPUTER-ASSISTED PROVED | `certificates/legacy/s444b_ext04_minimum_circuit_manifest.json` and frozen receipts |
| C3 | Minimum trades span every full rational relation module | COMPUTER-ASSISTED PROVED | frozen full-kernel receipts at 409 and 613 |
| C4 | These circuits give the complete degree-three toric layer | PROVED | paper Section 6 and fiber criterion |
| C5 | Local saturation at 2, 3, 17, 137, 219097, and 3288036131 | COMPUTER-ASSISTED PROVED | legacy receipts and paper Sections 7–8 |
| C6 | All five non-`rho/B1` large maps pass the selected-prime maximal-minor screens stated in the paper | COMPUTER-ASSISTED PROVED | S4.48F/J frozen receipts |
| C7 | The complete `rho/B1` map is surjective over `Z[zeta_17,1/(2*3*17)]` | PROVED with exact certificate | `scripts/verify_all.py`; paper Section 9 |
| C8 | The two-minor ideal has multiplication-lattice Smith diagonal `17^11,289^5` and index `17^21` | COMPUTER-ASSISTED PROVED | `results/s449f_rho_d1_global_gate_verification.json` |
| O1 | Corresponding global theorem for the other five large maps | OPEN / DEFERRED | deliberately outside this release |
| O2 | Complete global Smith groups | OPEN | no claim |
| N1 | Support of every global cokernel is contained in `{2,3,17}` | NOT CLAIMED | finite screens do not imply this |
| N2 | Novelty, priority, or firstness | NOT CLAIMED | dated prior-art search is not a priority certificate |
| N3 | P42 tomography theorems are used in P39 | NOT CLAIMED | projects are synchronized but logically separate |
