# HANDOFF — Final Assessment (round 3)

**Branch:** `review-round3` · **Preserved untouched:** `main` @ `2fee260`,
`review-fixes` @ `a5e3bc7`, `review-round2` @ `1595f9f`
**Date:** 2026-09-16 · **Simulator-only. No hardware. No quantum-advantage claim.**

## 1. What this is

**Title.** *Sampling-Free Oracles for Integration Defects in Quantum Error-Mitigation Pipelines*

A **bounded integration-failure case study with a reusable validation artifact**, plus an explicitly
**negative** decision-cost result. It is not the discovery of an unknown hazard: calibrating the
physical qubits a circuit measures is documented practice and `mthree` ships
`final_measurement_mapping` for it.

## 2. Main results (round-3 data, 5,040 cells)

**The defect reliably changes the answer.** All six implementation-contrast tests are significant
after BH adjustment; mean absolute differences span
0.001–0.094 of $C_{\max}$, with directionality up to
0.99 (a one-directional shift, not cancellation). The selected method
changes in **76.4%** of cells, identical with or without the unmitigated option.

**But the downstream decision cost is negligible here.** The primary endpoint — the paired held-out
loss difference between the legacy-selected and corrected-selected method on an *independent*
replicate — is **+0.0007** of $C_{\max}$ (stratified CI
[+0.0001, +0.0013]; cluster CI [+0.0004, +0.0012]).
That is statistically resolvable but roughly **an order of magnitude below the practical threshold
of 0.01 declared in advance**, and on `dev_lagos` the interval **crosses zero**
(-0.0005, CI [-0.0016, +0.0006]).

**Why:** with compilation held fixed, **96.4%** of cells are practical near
ties and **100.0%** are statistically indistinguishable (median top-two gap
under 0.002 $C_{\max}$). The high change rate is near-coin-flipping between near-equivalent
options.

**Integrity:** realised budget deviation **0.0000%**,
**0** stream collisions, **0**
compilation violations over 360 cells, 0 rows missing a fingerprint,
30,240,000 shots, 0 scoring shots, 1.78 core-hours.

## 3. How the corrections changed our own conclusions

| quantity | round 2 (confounded) | round 3 (corrected) |
|---|---|---|
| winner-change rate | 74.7% | 76.4% |
| practical near ties | 53.3% | 96.4% |
| statistically indistinguishable | not reported | 100.0% |
| decision cost | 0.0067 (vs a noisy minimum) | **+0.0007** (paired held-out) |

Removing the compilation confound and replacing the endpoint **cut the apparent decision cost by
about an order of magnitude**. That weakening is reported, not buried.

## 4. Deliverables

`manuscript/manuscript.pdf` (6 pp) + LaTeX source ·
`manuscript/manuscript_author_copy_no_ai_statement.pdf` (identified author reading copy) ·
`supplementary/` · `figures/` (PDF+PNG+source+`.drawio`) · `results/v2r3/{raw,processed}` ·
`configs/v2/confirm_round3.yaml` · `tests/` (two independent oracles) ·
`REVIEW_RESPONSE_round3.md` · `CLAIM_EVIDENCE.csv` (41 claims) · `docs/` · `FINAL_REVIEW.md` ·
`AUTHOR_ACTIONS.md` · `REPRODUCE.md`

## 5. Honest assessment

**Not submission-ready, and the contribution is smaller than at round 2.** The evidence supports
every claim now made, but the headline is partly negative: the defect changes selections reliably
and costs almost nothing downstream in this regime. The design has little power to show such changes
matter, because the methods are nearly tied at this budget — stated as a threat to validity rather
than worked around.

**Practical blocker independent of merit:** no target venue edition has an open call (QCE 2026 closed
27 Apr 2026; QSW 2026 closed 22 Mar 2026; neither 2027 call published).

**Not claimed anywhere:** any in-loop result; any hardware result; any quantum advantage; any
mechanism; that any released library is defective; that the working tree was clean; that the
decision-cost null generalises beyond these conditions; or that round-1/round-2 data confirms
anything.
