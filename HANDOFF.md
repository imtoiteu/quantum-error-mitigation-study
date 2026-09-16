# HANDOFF — Error Mitigation for VQAs under Realistic Noise (Pilot)

**Date:** 2026-09-15 · **Stage:** feasibility study + pilot complete · **Paper:** not started (by design)
**All results are SIMULATOR-ONLY. No quantum hardware was used. No quantum-advantage claim is made.**

> **Results are FROZEN for independent review as of 2026-09-16.** Read **[`REVIEW.md`](REVIEW.md)**
> first: it separates preregistered from exploratory analysis, absolute effects from ratios against
> near-zero baselines, and direct evidence from proposed explanations — and lists a material defect
> in the ZNE arm (§6.1). Where this document and `REVIEW.md` differ, `REVIEW.md` is correct.

---

## 1. Proposed research questions

**Confirmatory** (pre-registered in `docs/research-questions.md` before any data was collected):

- **RQ1** — Under a fixed **total** shot budget *B* per estimate, does any mitigation method reduce objective error relative to spending all *B* unmitigated?
- **RQ2** — Where is the shot-budget crossover at which each method starts to help, and does it differ between a cheap method (REM, additive overhead) and an expensive one (ZNE, 3× multiplicative)?
- **RQ3** — Does the estimation-stage verdict transfer to the full optimisation loop, or do variance effects break it?

**Exploratory** (reported, never used for headline claims): noise-strength sensitivity (EQ1), noise-model sensitivity (EQ2), algorithm sensitivity (EQ3), ZNE fit-choice sensitivity (EQ4), wall-clock vs shot cost (EQ5).

---

## 2. Evidence for the research gap

Full analysis with the comparison matrix: `docs/novelty-gap.md`. Summary:

**Established premises (not our contribution):** ZNE trades bias for variance (Temme *et al.*, PRL 119:180509, 2017); mitigation has an unavoidable, exponentially growing sampling cost (Takagi *et al.*, npj QI 8, 2022; Quek *et al.*, Nat. Phys. 20, 2024); readout error dominates at low depth (Bravyi *et al.*, PRA 103:042605, 2021).

**Closest peer-reviewed work:**
- Bultrini *et al.*, *Unifying and benchmarking state-of-the-art QEM techniques*, Quantum **7**:1034 (2023) — unifies ZNE/CDR/virtual distillation, but compares **per circuit execution, not per total shot**, and has no readout-mitigation arm.
- Russo *et al.*, *Testing Platform-Independent QEM*, IEEE TQE **4** (2023) — establishes the paper type; compares mitigated vs unmitigated, not method-vs-method at fixed budget.

**Two 2026 preprints substantially narrow the gap — and must be cited, not ignored:**
- **arXiv:2605.08251** (Alfaro, 2026-05-07, single-author, no peer-reviewed venue located) — defines a finite-shot "help–harm boundary" for ZNE analytically. **This pre-empts the bare claim "ZNE can hurt under finite shots."** It does not compare ZNE against readout mitigation, does not study VQE or QAOA, and releases no artifact.
- **arXiv:2608.28535** (Chongder, 2026-08-28, single-author) — six techniques under a constrained budget on IBM hardware; no VQE/QAOA specificity, no explicit equal-total-shot cross-method comparison, no controlled noise-strength sweep.

**Residual gap (stated precisely):** no located study gives a budget-matched, multi-noise-model, multi-noise-strength comparison of ZNE against measurement-error mitigation *and their composition* on **both** a VQE and a QAOA task, with seeded repeats, confidence intervals, and a released reproducible artifact.

**Honest strength rating: moderate.** This is a *consolidation and measurement* contribution, not a methodological one. Each axis exists somewhere; the combination does not.

**Search limitations that bound this claim:** arXiv's API was rate-limited from this host, so no systematic arXiv sweep was performed (only targeted landing-page reads); Crossref proceedings coverage is incomplete; no forward-citation analysis of Bultrini 2023 / Russo 2023 was done. **All three should be completed before drafting.**

---

## 3. Realistic target venues

Chosen by probing what each venue **actually publishes** (ISSN-scoped Crossref queries), not reputation. Full evidence tables: `docs/venue-survey.md`.

| Priority | Venue | Evidence it fits | Risk |
|---|---|---|---|
| **1** | **IEEE Trans. Quantum Engineering** | Russo *et al.* 2023 (10.1109/TQE.2023.3305232) is nearly our paper type; Lubinski *et al.* 2023 benchmarking; still publishing QEM in 2026 (Prodius; Pérez-Guijarro). Rolling deadline. | Reviewers may request hardware data |
| **2** | **IEEE QCE (Quantum Week)** | Majumdar *et al.* 2023 "Best Practices for QEM with dZNE" (10.1109/QCE57702.2023.00102) proves practice/methodology papers are accepted; Giurgica-Tiron 2020 dZNE originated here | Annual deadline (**not verified — check CfP**) |
| **3** | **ACM Trans. Quantum Computing** | Pelofske *et al.* 2024 ZNE benchmarking (10.1145/3680290); Bisicchia *et al.* 2026 shot-budget methodology (10.1145/3841468) | Expects larger scope than a pilot |
| 4 | Quantum Information Processing | Publishes QEM, but recent output skews ML-based | Weaker topical match |
| 5 | Quantum Reports / Entropy | Indexed and would accept | **Little relevant readership — not recommended** |

**No deadlines are asserted anywhere in this repository** — none were verified.

---

## 4. Exact pilot commands

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt     # exact pins: requirements-lock.txt

.venv/bin/python experiments/pretrain.py    # Stage 0 -> configs/pretrained_params.json
.venv/bin/python experiments/stage_a.py     # Stage A -> results/raw/stage_a.jsonl   (~34 min, 4 cores)
.venv/bin/python experiments/stage_b.py     # Stage B -> results/raw/stage_b.jsonl   (~32 min, 4 cores)
.venv/bin/python experiments/analyze.py     # -> results/processed/, figures/
```

Environment: Python 3.12.3, qiskit 2.5.2, qiskit-aer 0.17.2, qiskit-ibm-runtime 0.42.0, mitiq 1.1.0,
4 vCPU AMD EPYC @ 2.0 GHz, 7 GB RAM. Peak RSS measured 0.24 GB.

---

## 5. Pilot results — including negative results

### 5.1 Design actually executed

Stage A: 2 tasks × 6 noise settings × 5 budgets × 4 methods × 10 seeds = **2400 cells**, 2023 s.
Stage B: 2 tasks × 1 noise model × 4 methods × 5 seeds = **40 runs**, 40 SPSA iterations each.

### 5.2 Budget-match integrity

Automated check over all 60 Stage A comparison groups: **54 groups exactly matched; 6 groups show a maximum relative deviation of 0.27%** (1496 vs 1500 shots at *B*=1500), caused by integer division when spreading 300 calibration shots over 8 circuits. **The shortfall always falls on the mitigated arm**, so it is conservative — REM receives marginally *fewer* shots, never more. Reported in `results/processed/verdicts.md` rather than absorbed silently.

### 5.3 RQ1 — headline result

Verdicts across all 60 (task × noise × budget) cells, by non-overlapping 95% bootstrap CI over 10 seeds:

| Method | helps | harms | inconclusive | mean error ratio vs unmitigated (noisy settings) |
|---|---|---|---|---|
| **REM** | **46** | **0** | 14 | **0.547** |
| ZNE | 34 | 7 | 19 | **1.096** |
| ZNE+REM | 33 | 11 | 16 | 0.958 |

**Three findings, two of them negative:**

1. **Measurement-error mitigation is the only method that never harms** (0/60) and it roughly halves the error on average. For these small VQAs it dominates ZNE at matched budget.
2. **ZNE alone is, on average, worse than doing nothing** (mean ratio 1.096; worst case **4.99×** worse than unmitigated). Its benefit is concentrated in high-noise regimes; in the gate-dominated, low-readout-error `dev_algiers` snapshot it harms in 5 of 10 cells.
3. **Composing methods is the riskiest choice, not the safest.** ZNE+REM has both the best best-case (0.110× error) and the most "harms" verdicts (11/60).

### 5.4 Sanity check that validates the whole pipeline

On the **ideal** (noiseless) simulator, where there is no bias to remove and mitigation can only add variance, every method is strictly worse than doing nothing:

| Method | mean error ratio vs unmitigated, ideal noise |
|---|---|
| REM | 1.129 |
| ZNE | 1.711 |
| ZNE+REM | 2.088 |

This is the theoretically required behaviour and is strong evidence the budget accounting is real rather than an artifact.

### 5.5 RQ2 — crossover budgets

REM crosses into "helps" at **1500–3000 shots in every single configuration**. ZNE's crossover ranges from 1500 up to **12000** shots (both tasks, `param_lam0.5`). **Hypothesis H2 is supported:** the cheap additive-overhead method becomes worthwhile at a substantially smaller budget than the expensive multiplicative-overhead one. Full table: `results/processed/stage_a_crossover.csv`.

### 5.6 Unphysical estimates — **EXPLORATORY / POST-HOC, not preregistered**

> This metric was added *after* a smoke-test estimate exceeded the exact maximum cut. The counts are
> real and reproducible from committed raw data, but the metric was chosen after seeing it would be
> interesting. It is a hypothesis for confirmation, not a confirmed result. See `REVIEW.md` §2c.


161 of 2400 estimates (6.71%) were **physically impossible** — a QAOA cut above the exact maximum of 7, or a TFIM energy below the exact ground state (a variational violation):

| Method | unphysical cells |
|---|---|
| no mitigation | 3 |
| ZNE | 23 |
| REM | 8 |
| **ZNE+REM** | **127** |

Richardson extrapolation is unconstrained and overshoots. **ZNE+REM produced unphysical output in ~21% of its cells.** Any practical deployment needs a physicality constraint; this is a concrete, citable practitioner warning.

### 5.7 EQ2 — the noise model changes the winner

At the largest budget (24 000 shots), the best method **depends on which noise model is used**:

| Noise model | best method (both tasks) |
|---|---|
| `dev_lagos`, `dev_algiers` (device calibration snapshots) | **REM** (except tfim/algiers → ZNE+REM) |
| `param_lam{0.5,1,2}` (parametric) | **ZNE+REM**, consistently |

**This is a caution about the field's methodology, including our own:** a study using only a hand-built parametric noise model would have concluded ZNE+REM is best; one using only device snapshots would have concluded REM is best. Single-noise-model studies are not trustworthy on this question.

### 5.8 EQ5 — circuit executions and wall-clock disagree

| Method | mean circuit executions / estimate | mean wall-clock / estimate |
|---|---|---|
| none | 1.5 | 0.93 s |
| ZNE | 4.5 | 3.11 s |
| **REM** | **11.5** | **1.80 s** |
| ZNE+REM | 14.5 | 3.92 s |

REM uses **2.6× more circuit executions than ZNE but is 1.7× faster in wall-clock**, because its calibration circuits are shallow while ZNE's folded circuits are deep. **Cost models based on circuit count alone mis-rank these methods.**

### 5.9 RQ3 — in-loop optimisation: **the Stage A conclusion reverses**

40 runs, `dev_lagos`, 40 SPSA iterations (81 objective evaluations), 243 000 circuit shots per run
for every method. Final parameters are scored by a **noiseless** re-evaluation, which separates
"did the optimiser find good parameters?" from estimator noise.

**Ratios here are computed against a near-zero baseline and are reported alongside absolute
differences and the problem scale. Ratios alone would be misleading — see `REVIEW.md` §3.**

| Task | Method | final \|error\| | 95% CI | ratio | abs. diff | **% of problem scale** |
|---|---|---|---|---|---|---|
| **QAOA p=1** (scale C_max = 7) | **none** | **0.0046** | [0.0020, 0.0078] | 1.0× | — | — (**best**) |
| | ZNE | 0.0236 | [0.0114, 0.0357] | 5.2× | +0.019 | **+0.27%** |
| | REM | 0.0527 | [0.0077, 0.1220] | 11.6× | +0.048 | **+0.69%** |
| | ZNE+REM | 0.7669 | [0.1415, 1.3923] | 168× | +0.762 | **+10.9%** |
| **TFIM** (scale \|E₀\| = 4.76) | REM | 2.884 | [1.982, 3.975] | 0.93× | −0.205 | −4.3% |
| | none | 3.089 | [2.171, 4.133] | 1.0× | — | — |
| | ZNE | 3.134 | [2.631, 3.716] | 1.01× | +0.045 | +0.9% |
| | ZNE+REM | 4.277 | [3.647, 4.997] | 1.38× | +1.188 | +25.0% |

**Corrected reading:** on QAOA, all three mitigated arms are *statistically* worse than the baseline
(disjoint CIs), but only **ZNE+REM** is worse by a practically meaningful margin (10.9% of the
problem scale). ZNE and REM degrade the final objective by **under 1%** of the scale. All TFIM CIs
overlap the baseline — inconclusive.

**Hypothesis H3 is confirmed, and more strongly than predicted.** H3 anticipated that the *ranking*
would change in-loop. On QAOA it does not merely change — **it inverts**: the method that never
harmed in Stage A (REM, 0 harms in 60 cells) is 11× worse than doing nothing when placed inside the
optimisation loop, and every mitigated arm is significantly worse than the unmitigated baseline.

**Proposed mechanism — a HYPOTHESIS generated by this pilot, not a result confirmed by it.**
An optimiser may need an objective whose *ordering* of parameter points is preserved rather than one
that is unbiased; if noise-induced bias here is near-monotone in the true objective, SPSA would
descend correctly without mitigation, and mitigation would trade that harmless bias for gradient
variance. **This was not tested.** Monotonicity was never measured, bias and variance were never
varied independently, gradient variance was never recorded, and the competing explanation
(unphysical over-correction alone) is confounded with it. See `REVIEW.md` §7 for the full list of
tests that would be needed. Until then the defensible statement is: *mitigation improved estimation
and did not improve optimisation in this single noise condition; the mechanism is unresolved.*

**The unphysicality mechanism compounds it.** In-loop, ZNE+REM produced physically impossible
objective values in **10.25%** (TFIM) and **3.25%** (QAOA) of evaluations — energies below the exact
ground state, cuts above the exact maximum. The optimiser chases these artifacts. Its *observed*
descent looks healthy (−2.20 on TFIM, comparable to the other arms) while its *actual* final
parameters are the worst of any method. **A mitigated objective can look like it is converging
while being actively misleading.**

**TFIM in-loop is underpowered and is reported as inconclusive.** SPSA with 40 iterations on a
16-parameter ansatz does not converge from a random start — all arms end 2.9–4.3 away from the
reference of −4.734, and every CI overlaps the baseline. Only the QAOA arm (2 parameters, well
converged, final error 0.0046 ≈ 0.08% of the exact optimum) supports a confirmatory claim. **No
TFIM in-loop conclusion should be drawn from this pilot.**

---

## 6. Reproducibility information

- **Seeds fixed in config before running:** Stage A `[0..9]`, Stage B `[0..4]`. Results from unlisted seeds are not reportable.
- **Every result row records:** git commit, config SHA-256 (12 chars), hostname, Python/qiskit/aer/mitiq versions, `simulator_only: true`, plus `shots_used`, `circuit_executions`, `wall_clock_s`.
- **Raw data is version-controlled:** `results/raw/*.jsonl`, one JSON object per cell.
- **Configs are version-controlled and frozen:** `configs/stage_a.yaml`, `configs/stage_b.yaml`, `configs/pretrained_params.json`.
- **Exact dependency pins:** `requirements-lock.txt` (58 packages).
- **Transpilation pinned:** `optimization_level=1`, fixed `seed_transpiler`, coupling map restricted to the induced subgraph on physical qubits 0..n−1 (verified connected on both devices).
- **Device noise is static:** `FakeLagosV2` / `FakeAlgiers` ship calibration snapshots inside `qiskit-ibm-runtime` 0.42.0. No live device queries, so runs are deterministic.

### Correctness traps found and guarded (worth carrying forward)

1. **Folding must be post-transpilation, re-transpiled at `optimization_level=0` only.** Measured: a 3×-folded 4-qubit circuit re-transpiled at level 1 collapsed from depth 34 / 9 CX back to depth 12 / 3 CX. ZNE would have silently become a no-op and the extrapolation would have fit pure noise. Guarded and documented in `src/qemstudy/runner.py`.
2. **Folding emits `sxdg`,** which is outside the IBM basis and would have received **no noise** from the device noise model — again defeating ZNE. `optimization_level=0` translates it without cancelling.
3. **REM calibration must be measured, never read from the noise model.** Reading ground truth would unfairly inform the REM arm. Validated: the implementation recovers ⟨Z₀⟩ from 0.667 → 0.983 at 16.9% readout error.
4. **Amortised calibration must not be double-billed.** An early Stage B bug charged REM both a one-time calibration *and* a 20% per-evaluation deduction (17 400 vs 21 000 shots). Fixed; the two accounting regimes are now explicit in `src/qemstudy/runner.py`.

---

## 7. Threats to validity

**Internal**
- One ansatz per task; ansatz choice is a known confounder and was not varied.
- SPSA only. Optimiser choice is known to dominate small-QAOA results (Shaydulin & Alexeev 2019).
- Global folding and Richardson fit only in confirmatory arms; local folding and identity insertion untested.
- `dev_lagos` **qubit 2 has a 46.5% readout error** — effectively unusable for readout. It makes the confusion-matrix inversion ill-conditioned (~14× variance amplification) and plausibly drives much of REM's high-variance behaviour at small budgets on that device. Realistic, but a single pathological qubit carries a lot of weight in these results.
- The 0.27% budget shortfall at *B*=1500 (§5.2), though conservative in direction.

- **ZNE noise scaling is misspecified (material).** Richardson is fitted against nominal factors
  (1, 2, 3), but the achieved two-qubit-gate amplification recorded in `cx_per_scale` is 1.80–2.38 at
  nominal 2.0 (exact at 3.0), and it differs between the two TFIM measurement bases (1.82 vs 2.38).
  The midpoint governs the curvature of a three-point fit. **The ZNE arm's poor showing may be partly
  an implementation artifact.** Must be resolved before publishing any ZNE claim. `REVIEW.md` §6.1.

**External**
- **Simulator only.** Aer noise models omit crosstalk, non-Markovian drift, calibration decay, and leakage. Every conclusion transfers to hardware only as a hypothesis.
- **4–6 qubits.** Nothing here can be extrapolated to scales where mitigation's exponential cost bites.
- **IBM-flavoured.** Superconducting, `cx`-native, IBM readout characteristics. Trapped-ion / neutral-atom regimes unrepresented.
- Two device snapshots only, and §5.7 shows the noise model changes the winner — so even two may be too few.

**Statistical**
- 10 seeds (Stage A) / 5 seeds (Stage B). Bootstrap CIs on 5 seeds are wide and should be read cautiously.
- 60 comparison groups per method with no multiple-comparison correction. The "helps/harms" counts are descriptive, **not** family-wise-error-controlled. With ~60 tests at α=0.05, ~3 false "helps" would be expected by chance — the REM result (46) is far above that, but individual cell verdicts should not be over-read.
- Stage B deviates from pre-registration: restricted from 2 device noise models to 1 (`dev_lagos`) to fit the compute budget. Documented in `configs/stage_b.yaml` with the reasoning; all seeds and iterations were preserved.

---

## 8. Go / no-go recommendation

### Recommendation: **GO — conditional**, targeting IEEE TQE (primary) or IEEE QCE (conference route).

**Kill criteria (pre-registered in `docs/novelty-gap.md` §6) re-checked after the pilot:**

| | Criterion | Status |
|---|---|---|
| K1 | A peer-reviewed paper already does budget-matched ZNE-vs-REM on VQE and QAOA | **Not triggered** — none located, but see the search limitations in §2 |
| K2 | Alfaro (arXiv:2605.08251) published **and** extended to cross-method comparison | **Not triggered** — still an unrefereed single-author preprint, ZNE-only |
| K3 | Effects too small to resolve above seed-to-seed variance | **Not triggered** — 46/60 REM "helps" verdicts by non-overlapping 95% CI |
| K4 | Result is merely "mitigation always helps, monotonically" | **Not triggered** — emphatically the opposite: ZNE averages *worse than nothing* at fixed parameters, the winner depends on the noise model, and in-loop the Stage A ranking **inverts** |

**Why GO:** the pilot produced a decision-relevant, non-obvious, and *self-contradicting* result — mitigation clearly helps expectation-value **estimation** (Stage A: REM 46/60 helps, 0 harms) and clearly hurts **optimisation** at the same budget (Stage B: every mitigated arm significantly worse than doing nothing on the converged QAOA task). That tension is the paper. It comes with a clean internal sanity check (ideal-noise behaviour matches theory exactly), a mechanism supported by diagnostics (unphysical estimates misleading the optimiser), several genuine negative findings, and a working reproducible artifact. The contribution type matches what IEEE TQE and IEEE QCE demonstrably publish.

**Why *conditional* — three things must happen before drafting:**

1. **Close the literature search.** Run the systematic arXiv sweep that the rate limit prevented, plus forward-citation analysis of Bultrini 2023 and Russo 2023. If K1 or K2 triggers, re-scope to the noise-model-dependence finding (§5.7), which is the most defensible novel element.
2. **Harden the statistics.** Increase to ≥30 seeds and apply multiple-comparison control before any "never harms" claim reaches a manuscript. The current 0/60 for REM is encouraging but under-powered for that phrasing.
3. **Add a third device noise model and a second ansatz.** §5.7 shows the conclusion is noise-model-dependent; two snapshots is thin evidence for a claim of that shape. Also re-run without `dev_lagos` qubit 2 to confirm it is not driving the REM result.

**Explicitly NOT recommended:** claiming quantum advantage; claiming REM is universally superior (it is not — ZNE+REM wins on every parametric-noise setting); or presenting any of this as hardware-validated.

### Suggested next scope

Keep the budget-matched framing as the paper's spine, but **lead with the estimation-vs-optimisation reversal (§5.9)** — it is the strongest and most surprising result, it is directly actionable for practitioners, and neither near-miss preprint (§2) touches it. Support it with the **unphysical-estimate mechanism** (§5.6, §5.9) and the **noise-model dependence** (§5.7). A working title along the lines of *"Error mitigation improves estimation and degrades optimisation: a budget-matched study of small VQAs"* captures the contribution.

**Priority for the full study:** fix the TFIM in-loop underpowering (it is the single biggest hole). Either raise the SPSA iteration count until the unmitigated arm converges, or start from perturbed pre-optimised parameters rather than random ones, so that the in-loop comparison is made in a regime where the optimiser actually works. Estimated compute for the full study at 30 seeds, 3 noise models, 2 ansätze: roughly 8–10× the pilot, i.e. ~9–11 hours on 4 cores. Still no cloud hardware required.
