# HANDOFF — Final Assessment (round 2)

**Branch:** `review-round2` · **Frozen v1 snapshot:** `main` @ `2fee260` (untouched)
**Date:** 2026-09-16 · **Simulator-only. No quantum hardware. No quantum-advantage claim.**

> Supersedes the round-1 handoff. Round-1 documents remain in git history.

## 1. What this is

**Title.** *Sampling-Free Oracles for Integration Defects in Quantum Error-Mitigation Pipelines*

A **bounded integration-failure case study with a reusable validation artifact**. It is explicitly
**not** the discovery of an unknown hazard: calibrating the physical qubits a circuit measures is
documented practice, and `mthree` ships `final_measurement_mapping` for it. The contribution is:

1. **Two deterministic, sampling-free oracles**, plus the demonstration that they are **not
   interchangeable** — the folding oracle is provably blind to the calibration defect, because at
   zero readout noise every response matrix is the identity.
2. **A measurement of consequences** on a budget-matched QAOA MaxCut benchmark with instance-aware
   inference and split-sample decision regret.
3. **A positive control** showing the standard library used as documented is unaffected.

## 2. Main results (round-2 fresh data, 5,040 cells)

Normalised by each instance's own $C_{\max}$. Primary inference over **six fixed instances**
(stratified bootstrap over seeds within instance); a wider instance-level cluster interval is
reported alongside for generalisation.

- **The effect is arm-dependent, not uniform.** Implementation contrast spans
  0.001–0.096 of $C_{\max}$.
  REM on `dev_algiers` is **unaffected** (directionality 0.13, $p_{\rm BH}$ = 0.29); ZNE and
  ZNE+REM there shift **one-directionally** (directionality 0.99).
- **Bias and variance reported separately.** The defective code gives ZNE a bias of **+0.0714** on
  `dev_algiers` where the corrected code gives **−0.0064**.
- **Winner changes in 74.7%** of cells — identical whether or not the
  unmitigated option is a candidate — **but 53.3% of cells are near
  ties**, so that rate overstates the substantive effect. This qualifier is in the abstract.
- **Split-sample excess regret from the defect: 0.0067** of $C_{\max}$
  overall (defective 0.0226 vs corrected 0.0159),
  concentrated on `dev_algiers` and near zero on `dev_lagos`.
- **Per-instance mean rankings change in 11/12 conditions.**
- **Cost:** 30,240,000 shots, 45,360
  executions, **0 scoring shots** (exact statevector), 1.63 core-hours.
  Realised budget deviation **0.0000%**; **0** stream collisions.

**Negative/null results reported, not suppressed:** one arm shows no resolvable effect; the regret
on `dev_lagos` is ~0.001; and the high near-tie rate is stated as a limit on the winner-change rate.

## 3. Venue — no submittable edition currently has an open call

| Venue | Edition | Status (verified 2026-09-16) |
|---|---|---|
| IEEE QCE | 2026 | **CLOSED** — papers due 27 Apr 2026; conference ran 13–18 Sep 2026 |
| IEEE QCE | 2027 | Call **not published**; all requirements UNKNOWN |
| IEEE QSW | 2026 | **CLOSED** — firm deadline 22 Mar 2026 |
| IEEE QSW | 2027 | Call **not published** |
| IEEE TQE | — | Rolling; the only option open today |

The manuscript is **6 pages** and was **deliberately not expanded** to the 8–10 page window of the
closed QCE 2026 edition. Length must be re-checked against whichever 2027 call is used.

## 4. Deliverables

`manuscript/manuscript.pdf` (6 pp, IEEEtran `[10pt,conference]`) + full LaTeX source ·
`supplementary/` (noise-scaling audit, M3 positive control) · `figures/` (PDF+PNG+plotting source+
editable `.drawio`) · `results/v2r2/{raw,processed}` · `configs/v2/` · `tests/` (two oracles) ·
`REVIEW_RESPONSE_round2.md` · `CLAIM_EVIDENCE.csv` · `docs/` · `FINAL_REVIEW.md` ·
`AUTHOR_ACTIONS.md` · `REPRODUCE.md` ·
`/root/imtoiteu/quantum-error-mitigation-review-round2.zip`

## 5. Honest assessment

**Publication readiness: unresolved, and the contribution is modest by construction.** The evidence
supports every claim made and the artifact reproduces from a clean-room install. But the hazard is
documented, the standard tooling already solves it, the measured decision cost is small in absolute
terms (0.0067 of $C_{\max}$), and over half the winner changes are
near ties. The value rests on the validation oracles and the honest measurement, not on novelty.

**Practical blocker independent of merit:** no target edition has an open call.

**Not claimed anywhere:** any in-loop result; any hardware result; any quantum advantage; any
mechanism; that any released library is defective; that the repository is already public; or that
round-1 data confirms anything.
