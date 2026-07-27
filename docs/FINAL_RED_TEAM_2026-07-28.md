# Final red-team adjudication — 2026-07-28

## Scope

An independent read-only sub-agent audited the manuscript, public package,
claim boundaries, exact verifiers, manifest, and release attestation after the
external-review remediation.

## Findings and disposition

| Severity | Finding | Disposition |
|---|---|---|
| P1 | The good-prime lemma called the relevant quantity a cokernel, although the exact sequence controls the deficiency from structural rank | corrected by the identity `(m_B-m_P)-rank(E)=dim Hom(Q,V)` and its exact Hom sequence |
| P1 | The reverse-row receipt said that the decisive ideal sum used G0; the actual decisive pair is G1 replacement plus reverse, while G0 plus reverse is the nonunit negative control | verifier wording corrected and receipt regenerated |
| P2 | `committed:false` and `pushed:false` would become stale immediately after publication | field relabeled `publication_actions_at_audit_time` |
| P3 | The immutable-object paragraph contained a sentence fragment | repaired |
| P3 | Six design-level digests were not distinguished from the hashes directly exposed by the pinned companion checkout | evidence boundary made explicit in the source lock |

The audit found no further material defect in the determinantal-ideal theorem,
the exact index `17^21`, or the boundary leaving five global gates and the
complete Smith groups open. A scan of all fourteen TeX sources found no
academic error-and-repair narrative concerning 137.

## Independent gates

The sub-agent passed the closed-tree manifest, normal replay, optimized replay
with byte-identical receipt, manifest-only replay, and release-attestation
checks in an isolated copy. It did not complete an independent page-rendering
pass. The final post-remediation PDF render and visual inspection are therefore
recorded separately in the release attestation.
