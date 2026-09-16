# Novelty Matrix — evidence-based comparison against prior work

**Compiled:** 2026-09-16. **Method:** metadata verified via Crossref/arXiv landing pages; full text
retrieved and searched where legally available (Majumdar *et al.* PDF extracted and grepped locally).
Claims marked *(abstract only)* were not verified against full text — **absence of a detail in an
abstract is not evidence that the paper omits it.**

## 1. The four papers the review named

### P1 — Bultrini, Gordon, Czarnik, Arrasmith, Cerezo, Coles, Cincio, *Unifying and benchmarking state-of-the-art quantum error mitigation techniques* ("UNITED")
- arXiv:2107.13470 v1 2021-07-28, **v2 2023-05-22**; **Quantum 7, 1034 (2023)**; DOI [10.22331/q-2023-06-06-1034](https://doi.org/10.22331/q-2023-06-06-1034)
- Methods: **ZNE, CDR, VD** and combinations (UNITED). **REM is not among the compared methods** *(abstract + method list)*.
- Problems: random circuits **and QAOA applied to Max-Cut**, varying qubits, depth, and **total shots**.
- Budgets: shot budget is a **primary axis**; benchmarked up to ~10^10 shots. "performance of different techniques depends strongly on shot budgets, with more powerful methods requiring more shots."
- Noise: **trapped-ion** device-derived model.
- Regime: expectation-value estimation at fixed parameters *(no optimisation loop identified)*.

### P2 — Scavino, *Decision Kernels for Quantum Error Mitigation: Why Accuracy Gains Need Not Improve Downstream Decisions*
- arXiv:2607.02888, submitted 2026-07-03, v1. **No peer-reviewed venue located.** Single author.
- Theory + Aer simulation. Methods discussed: **CDR, PEC**. Proves quotient factorisation, a marginal no-go theorem, a QEM pullback theorem, Gaussian decision-risk formulas.
- Core claim: accuracy (MSE) improvements need not improve shift-invariant downstream decisions (argmin, ranking, top-k, **optimizer-step acceptance**).
- **This pre-empts any generic "mitigation improves estimation but not decisions" framing.** We therefore do not claim that framing.

### P3 — Majumdar, Rivero, Metz, Hasan, Wang, *Best practices for quantum error mitigation with digital zero-noise extrapolation*
- arXiv:2307.05203 v1 2023-07-07, v2 2023-07-20; **IEEE Quantum Week (QCE) 2023**; DOI [10.1109/QCE57702.2023.00102](https://doi.org/10.1109/QCE57702.2023.00102). **Full text retrieved and searched.**
- **"Transpile first"** (§II): "noise should be amplified in circuits that have already been transpiled to a particular device"; folding before transpilation "would under- or over-represent the noise".
- **Odd integer scale factors** (§II): factors outside {1,3,5,…,2n+1} are "partially folding circuits because gates in the original circuit are not all folded an equal number of times"; Fig. 4 "Partial folding should be executed with care."
- **Readout error is not amplified** (§V, "Readout error"): "In conventional approaches to unitary folding, state preparation and measurement (SPAM) error is not amplified."
- **dZNE composed with REM** (Fig. 7): with a depolarising (p=0.01 on CNOT) + readout (p(0|1)=0.02, p(1|0)=0.01) toy model, "the gap between the readout mitigated and unmitigated cases shrinks with increasing depth as gate errors become the major source of error."
- They use **local** folding. No matched-total-shot budget comparison; no QAOA optimisation; no multi-instance statistics or confidence intervals; **no discussion of measurement mapping, classical registers, or routing permutations** (searched: "layout", "routing", "measure" — only the transpile-first ordering argument appears).

### P4 — Scavino Alfaro, *The finite-shot help-harm boundary of zero-noise extrapolation*
- arXiv:2605.08251, submitted 2026-05-07, v1, "22 pages, 4 figures". **No peer-reviewed venue located.** Single author (same surname family as P2; author identity not confirmed from the listings).
- **ZNE only**; analytic bias/variance expansion + Aer validation. No REM comparison, no QAOA/VQE specificity, no released artifact located.

## 2. Additional closely-related work found by targeted search

### P5 — Köster & Mauerer, *Benchmarking Error Mitigation: Artefactual Improvements in Zero-Noise Extrapolation*
- arXiv:2607.09360 v1 2026-07-10, v2 2026-08-03. **Accepted for publication at IEEE Quantum Week (QCE) 2026.**
- Identifies **artefactual** ZNE improvement: when amplification pushes past usable signal, Richardson ZNE "collapses into a fixed rescaling of a single noisy measurement". Overshoots ideal by up to 21% on IQM Euro-Q-Exa. Uses a "garbage-folding" negative control.
- **Explicitly a statistical/physical-regime artefact, not a software defect** *(abstract + our reading)*. No layout/measurement-mapping discussion; no REM.
- **This is our closest relative and our primary point of contrast.**

### P6 — Chongder, *Hardware-Efficient Error Mitigation and Shot-Efficient Sampling on IBM Quantum Hardware*
- arXiv:2608.28535 v1 2026-08-28, single author, no venue located. Constrained execution budget on IBM hardware combining qubit selection, depth scaling, ZNE, DD, REM, repeated-shot estimation. *(abstract only — QAOA/MaxCut, seeds and CIs not confirmed.)*

### P7 — Russo, Mari, Shammah, LaRose, Zeng, *Testing Platform-Independent QEM on Noisy Quantum Computers*, **IEEE TQE 4 (2023)**, DOI [10.1109/TQE.2023.3305232](https://doi.org/10.1109/TQE.2023.3305232) — ZNE and PEC across IBM/IonQ/Rigetti; mitigated-vs-unmitigated, not budget-matched method-vs-method.

### P8 — Also located, not fully assessed *(abstract only)*: arXiv:2603.10224 (verifiable benchmark circuits to reduce QEM bias); arXiv:2601.18680 (error-mitigation-aware benchmarking for quantum optimisation).

## 3. Comparison matrix

| Axis | P1 UNITED | P3 Majumdar | P4 Alfaro | P5 Köster–Mauerer | P2 Decision Kernels | **This work** |
|---|---|---|---|---|---|---|
| ZNE studied | ✅ | ✅ (local fold) | ✅ | ✅ | — | ✅ (global fold) |
| **REM as a compared arm** | ❌ | composed, not compared at equal cost | ❌ | ❌ | ❌ | ✅ |
| Matched **total**-shot comparison | shots are an axis; equality across methods not established | ❌ | analytic | ❌ | fixed-allocation converse | ✅ asserted per cell |
| QAOA / MaxCut | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ 6 distinct instances |
| Device-calibration noise | trapped-ion | toy depolarising+readout | Aer | IQM hardware | calibrated model | 2 IBM snapshots, contrasting channel mix |
| **Implementation correctness of folding** (measurement map, classical registers, layout) | ❌ | transpile-order only | ❌ | ❌ (regime artefact) | ❌ | ✅ **primary contribution** |
| Regression tests + quantified corruption of published conclusions | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Released artifact | partial | ❌ located | ❌ located | ❌ located | ❌ located | ✅ |

## 4. What we therefore do NOT claim

- **Not novel:** that folding leaves SPAM/readout error unamplified (**P3 §V states it explicitly**); that odd scale factors avoid partial folds (**P3 §II**); that one should transpile before folding (**P3 §II**); that shot budget governs which method wins (**P1**); that accuracy gains need not improve downstream decisions (**P2**); that ZNE can produce spurious apparent improvement (**P5**).
- We reproduce and cite each of these rather than re-deriving them as findings.

## 5. Remaining contribution (narrow, evidence-backed)

> **C1 (primary).** A *silent implementation* failure mode in ZNE/REM pipelines: unitary folding that rebuilds terminal measurements discards the layout-induced qubit→clbit mapping, and readout calibration indexed by virtual rather than physical qubits misassigns the confusion matrix. We give minimal regression tests with an exact oracle (global folding at odd scale must leave the *ideal* distribution invariant), show both defects are silent — no error, no warning — and **quantify the damage on a real, previously frozen benchmark: 18.8% of estimation cells and 75% of optimisation runs were affected, and the corrupted results supported a headline conclusion that does not survive correction.**
>
> **C2 (secondary).** A corrected, budget-matched comparison of ZNE, REM and their composition on QAOA MaxCut across 6 distinct 6-vertex instances and two IBM calibration snapshots with contrasting error-channel mix (median readout error 16.9% vs 1.1%), with paired analysis, multiplicity control and released artifacts — extending P1 (which omits REM) and P3 (which composes REM but does not equalise cost).

**Distinction from P5, stated explicitly:** Köster & Mauerer's artefact is a *physical-regime* collapse that occurs in a correct implementation once amplification exceeds usable signal. Ours is a *correctness* defect that occurs at any depth or signal level, is invisible to their negative control, and is fixed by code rather than by choosing scale factors. The two are complementary failure modes of the same pipeline.

## 6. Honest unresolved comparisons

- P3's Fig. 7 readout/depth interaction is qualitatively adjacent to our C2; we cite it as prior and frame C2 as the cost-equalised, multi-instance, device-calibrated version rather than as a new phenomenon.
- P6 full text not assessed; if it contains a matched-budget ZNE-vs-REM comparison on QAOA, C2 weakens to a replication. C1 is unaffected.
- P2 and P4 are unrefereed single-author preprints; their status may change.
- No forward-citation sweep of P1/P3 was completed (arXiv API rate-limited from this host); **this bounds all "not studied" statements above.**
