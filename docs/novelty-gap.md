# Research Gap Analysis

**Compiled:** 2026-09-15
**Status:** pre-pilot. This document states what we can and cannot claim *given evidence gathered so far*.

## 1. The claim we are NOT making

We are **not** claiming to invent a mitigation method. ZNE, unitary folding, and readout mitigation
are all established (Temme 2017; Giurgica-Tiron 2020; Nation 2021). We are also **not** claiming
quantum advantage of any kind, and the pilot is not capable of supporting such a claim.

We are also **not** claiming that "comparing mitigation methods at matched shot cost" is a new idea.
It is not. It is explicitly discussed in the QEM review (Cai *et al.* 2023) and is the subject of at
least two 2026 preprints (§3 below).

## 2. What the literature establishes

Three findings are well supported and form our premises, not our contribution:

**P1 — ZNE trades bias for variance.** Extrapolation removes noise-induced bias but amplifies
sampling variance through the extrapolation coefficients (Temme *et al.* 2017, PRL 119:180509).
Under a *fixed total shot budget* this trade can go either way.

**P2 — Mitigation has an unavoidable sampling cost.** Takagi *et al.* (npj QI 8, 2022) and Quek
*et al.* (Nat. Phys. 20, 2024) prove lower bounds showing the cost grows exponentially with circuit
volume. So a comparison that ignores cost is not merely unfair — it is measuring the wrong quantity.

**P3 — Readout error dominates at low depth.** Bravyi *et al.* (PRA 103:042605, 2021) show
measurement error is often the largest single error source for shallow circuits. Small VQE/QAOA
circuits are exactly this regime, so readout mitigation is a *serious competitor* to ZNE, not a
minor add-on.

Together P1–P3 imply a concrete, testable expectation: **for small VQAs under a fixed shot budget,
cheap readout mitigation may beat ZNE, and ZNE may be actively harmful.** That expectation appears
not to have been tested systematically across both VQE and QAOA.

## 3. Prior work that comes closest — and why the gap narrowed

Two preprints found by targeted search substantially overlap the obvious framing. Both abstracts
were read directly. **Both are single-author arXiv preprints for which no peer-reviewed venue was
located.**

### 3.1 Alfaro, *The finite-shot help-harm boundary of zero-noise extrapolation* (arXiv:2605.08251, 2026-05-07)
This is the most threatening related work. It defines a "help-harm boundary" — the finite-shot MSE
crossing at which Richardson ZNE stops hurting and starts helping — via a local bias/variance
expansion, validated with Qiskit Aer and IBM checks.

**This pre-empts the headline finding "ZNE can hurt under finite shots."** We must cite it as
establishing that result and must not present it as our own discovery.

What it does **not** do:
- It studies **ZNE alone**. There is no comparison against measurement-error mitigation, and therefore no answer to *which* method to spend a budget on.
- It does not study **VQE or QAOA** as algorithms — it uses generic "variational energy measurements" and stabilizer measurements.
- It reports no controlled sweep across **multiple distinct realistic noise models**.
- No reproducible artifact (code/data/configs) was located.

### 3.2 Chongder, *Hardware-Efficient Error Mitigation and Shot-Efficient Sampling on IBM Quantum Hardware* (arXiv:2608.28535, 2026-08-28)
Combines six techniques including ZNE and REM under a constrained execution budget on IBM hardware.

What it does **not** do: no specific VQE/QAOA study; no explicit equal-total-shot cross-method
comparison; hardware-only, so no controlled noise-strength sweep is possible.

### 3.3 Bultrini *et al.*, *Unifying and benchmarking state-of-the-art QEM techniques* (Quantum 7:1034, 2023)
The closest **peer-reviewed** work. Unifies ZNE, CDR and virtual distillation and their
compositions, finding that combinations help but non-uniformly and problem-dependently.
Its comparison is organised per-circuit-execution rather than per-total-shot, and it does not
include readout mitigation as a primary competitor arm.

### 3.4 Russo *et al.*, *Testing Platform-Independent QEM* (IEEE TQE 4, 2023)
Runs ZNE and PEC across three hardware platforms. Establishes the *paper type* we are writing, but
compares mitigated vs. unmitigated rather than method-vs-method under a fixed budget.

## 4. The residual gap — stated precisely

After accounting for §3, what remains unaddressed is narrow but real:

> **No located study provides a budget-matched, multi-noise-model, multi-noise-strength empirical
> comparison of ZNE against measurement-error mitigation (and their composition) on *both* a VQE and
> a QAOA task, with repeated seeded runs, confidence intervals, and a released reproducible artifact.**

Decomposed into the four axes that are jointly missing:

| Axis | Alfaro 2026 | Chongder 2026 | Bultrini 2023 | Russo 2023 | **This study** |
|---|---|---|---|---|---|
| Budget-matched total shots | ✅ | partial | ❌ (per-execution) | ❌ | ✅ |
| ZNE **vs** readout mitigation | ❌ (ZNE only) | listed, not compared | ❌ (no REM arm) | ❌ (ZNE vs PEC) | ✅ |
| Both VQE **and** QAOA | ❌ | ❌ | partial | ❌ | ✅ |
| Noise-strength sweep, ≥2 noise models | ❌ | ❌ (hardware only) | limited | ❌ | ✅ |
| Seeded repeats + CIs + released artifact | ❌ | ❌ | partial | partial | ✅ |

**Honest strength rating: moderate.** This is a *consolidation and measurement* contribution, not a
methodological one. Each individual axis exists somewhere in the literature; the combination, done
carefully with released artifacts, does not.

## 5. Why this is still worth doing

1. **It is decision-relevant.** A practitioner with a fixed budget currently has no evidence-based answer to "should I spend it on ZNE or on readout calibration?" P3 suggests the field's default (reach for ZNE) may be wrong at small scale.
2. **It matches what the target venues publish.** Majumdar *et al.* (IEEE QCE 2023) is a "best practices" paper; Russo *et al.* (IEEE TQE 2023) is a testing paper; Lubinski *et al.* (IEEE TQE 2023) is a benchmarking-methodology paper. None introduce new methods.
3. **A negative result is publishable here.** If mitigation does not help at matched budget, that is a useful, citable finding for a benchmarking venue — unlike an advantage claim, it does not require beating a classical baseline.

## 6. Conditions under which we should abandon or redesign

This gap is **not strong enough to survive** any of the following. Each is a pre-registered kill criterion:

- **K1.** A peer-reviewed paper is found that already performs the budget-matched ZNE-vs-REM comparison on VQE and QAOA. (Mitigation: re-run the search before writing; if found, pivot to the noise-strength-sensitivity axis only.)
- **K2.** Alfaro (arXiv:2605.08251) is found to have been published in a peer-reviewed venue **and** extended to cross-method comparison. → Redesign around QAOA-specific results or abandon.
- **K3.** The pilot shows effects so small relative to seed-to-seed variance that no conclusion survives at the scale we can afford. → Abandon; do not pad with more noise models.
- **K4.** The pilot result is simply "mitigation always helps, monotonically, everywhere" — i.e. we reproduce the textbook expectation with no nuance. → Insufficient contribution for a paper; abandon or re-scope.

## 7. Search limitations (threats to this gap analysis)

- Searches were English-language, Crossref- and web-search-mediated. Crossref coverage of **conference proceedings is incomplete**, so a relevant IEEE QCE or workshop paper could have been missed.
- arXiv's API was rate-limited from this host, so systematic arXiv full-text search was **not** performed; only targeted landing-page reads. **A full arXiv listing sweep is required before drafting the paper.**
- No citation-graph (forward-citation) analysis of Bultrini 2023 or Russo 2023 was done. Doing so is the highest-value next search step, since a closing paper would most likely cite them.
- Absence of evidence is not evidence of absence: the claim "no located study" is bounded by these limitations and is stated as such throughout.
