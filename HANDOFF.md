# HANDOFF — Final Assessment

**Branch:** `review-fixes` · **Frozen v1 snapshot preserved untouched:** `main` @ `2fee260`
**Date:** 2026-09-16 · **Simulator-only. No quantum hardware. No quantum-advantage claim.**

> This file supersedes the earlier v1 handoff, which described a study whose headline has since been
> **retracted**. The v1 document is preserved in git history on `main`.

## 1. What this project now is

A **software-correctness and benchmarking-validity** paper for quantum error mitigation, plus a
corrected benchmark. It is not a new-method paper and does not claim to be.

**Title.** *Silent Measurement-Mapping Defects Change Which Quantum Error-Mitigation Method Appears Best*

**Contribution, bounded:**
1. Two silent measurement-mapping defects in a budget-matched ZNE/REM pipeline, with minimal
   regression tests built on an exact oracle that needs no noise model.
2. A quantified impact on benchmark conclusions, measured by running identical seeds and
   configurations through the defective and corrected code.
3. A corrected budget-matched comparison of ZNE, REM and their composition on QAOA MaxCut over six
   distinct instances and two calibration snapshots with contrasting error-channel mix.
4. A **retraction** of the v1 headline.

## 2. Main results

**Implementation impact** (F1; 180 paired cells per row, BH-controlled):
all six tests significant; mean absolute disagreement
0.006–0.676 in expected cut value.
The signed means are far smaller than the absolute ones — **the defect randomises results rather
than biasing them**, which is why it is hard to notice.

**Conclusion flips:** the best-performing method changes in
**75.8% of 360 cells**. Flips are not
cheap: mean regret among flipped cells is 0.206 against a best
attainable error of 0.378.

**Corrected benchmark** (F2; 27 tests, n=180 each, BH-controlled) — the winner depends on which
error channel dominates:

| Noise regime | Result |
|---|---|
| `ideal` | every mitigation arm **harms**; nothing to correct, only variance added |
| `dev_algiers` (gate-dominated) | ZNE and ZNE+REM help substantially at every budget; REM helps but below the practical threshold |
| `dev_lagos` (readout-dominated) | ZNE helps modestly throughout; REM is indistinguishable from baseline at 1500 shots and only pays off at 24000 shots ($\Delta=-0.328$) |

**Negative and null results are reported, not suppressed:** 2 of 27 F2 tests show practically
meaningful *degradation*, 11 are statistically resolvable but below the practical threshold, and 1
shows no resolvable difference.

**Cost:** 7,560 cells, 74,520,000 shots
(66,852,000 circuit + 7,668,000 calibration),
63,000 executions, 0 scoring shots (exact
statevector), 1.68 core-hours. Realised budget match: **0.0000%**
deviation across methods at all three budgets.

## 3. Deliverables

`manuscript/manuscript.pdf` (7 pp, IEEEtran conference) and full LaTeX source · `supplementary/` ·
`figures/` (PDF + PNG + plotting source + editable `.drawio`) · `results/v2/{raw,processed}` ·
`configs/v2/` · `tests/` · `REVIEW_RESPONSE.md` · `CLAIM_EVIDENCE.csv` (47 traced claims) ·
`docs/novelty-matrix.md` · `docs/venue-decision.md` · `docs/main-study-protocol.md` ·
`FINAL_REVIEW.md` · `AUTHOR_ACTIONS.md` · `REPRODUCE.md` ·
`/root/imtoiteu/quantum-error-mitigation-submission-package.zip`

## 4. Venue

**Primary: IEEE QCE (Quantum Week).** Evidence: Köster & Mauerer, *Artefactual Improvements in
Zero-Noise Extrapolation* (arXiv:2607.09360v2) is **accepted at IEEE QCE 2026** — a paper whose whole
contribution is that a ZNE benchmark result was an artefact. Also Majumdar *et al.* (QCE 2023),
Giurgica-Tiron *et al.* (QCE 2020), Finžgar *et al.* (QCE 2022), Pelofske & Russo (QCE 2025).
**Fallback: IEEE TQE** (rolling deadline; `manuscript/FALLBACK_TQE.md`).
Deadline, page limit, fees and review model are **UNKNOWN and must be checked** — see `AUTHOR_ACTIONS.md`.

## 5. Honest assessment

**Publication readiness: plausible but unresolved.** The evidence supports every claim made, the
artifact is complete and reproducible from a clean environment, and the contribution type has a
current precedent at the target venue. Whether reviewers judge a correctness-and-replication result
sufficiently novel is not something this internal process can decide.

**The single largest residual risk** is that the literature search is bounded: arXiv's API was
rate-limited from this host, so no systematic sweep or forward-citation analysis of UNITED/Majumdar
was performed, and arXiv:2608.28535's full text was not assessed. If that paper contains a
matched-budget ZNE-vs-REM comparison on QAOA, contribution 3 weakens to a replication. Contributions
1, 2 and 4 are unaffected.

**Seven claims were withdrawn during this work** after reading full texts rather than abstracts —
six as prior art, one retracted for resting on defective code. See `FINAL_REVIEW.md` Pass 3.

**Not claimed anywhere:** any in-loop/optimisation result, any hardware result, any quantum
advantage, any mechanism, that any released third-party library is affected, or that the repository
is already public.
