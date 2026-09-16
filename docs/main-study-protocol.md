# Main-Study Protocol (prospectively fixed)

**Written and committed:** 2026-09-16, **before any main-study data was generated.**
**This is a prospectively fixed internal protocol, NOT an external preregistration.** It was not
registered with any third party and carries no independent timestamp beyond this repository's git
history (commit containing this file precedes the commit containing `results/v2/raw/main_study.jsonl`).

**Simulator-only. No quantum hardware. No quantum-advantage claim.**

Exploratory pilot data (`results/v2/raw/pilot.jsonl`, instances `prism` and `k33` only) was used to
size this study and is **kept separate** from main-study evaluation data
(`results/v2/raw/main_study.jsonl`). Pilot data is never pooled into confirmatory analysis.

---

## 1. Primary question and outcome

**PQ.** Does the measurement-mapping defect described in `REVIEW_RESPONSE.md` §1 change the
*conclusions* of a budget-matched quantum-error-mitigation benchmark, and by how much?

**Primary outcome.** Per matched cell (instance, noise, method, seed) at budget 6000, the absolute
disagreement between the defective and corrected implementations,
`D = | err_legacy − err_v2 |`, where `err = |estimate − exact noiseless value at the same parameters|`
in units of expected cut value.

**Primary secondary outcome.** The **best-method disagreement rate**: the fraction of
(instance, noise, seed) cells in which the mitigation method with the lowest error under the
defective implementation differs from the one with the lowest error under the corrected
implementation.

**SQ (secondary question).** Under the corrected implementation and matched total shot budgets, how
do `none`, `zne`, `rem` and `zne_rem` compare on QAOA MaxCut across instances, noise conditions and
budgets?

## 2. Estimands and practical-effect threshold

- Estimand for PQ: the population mean of `D` over the instance × noise × seed population defined below, and the population best-method disagreement rate.
- Estimand for SQ: the mean **paired** difference in estimation error between each mitigated method and the unmitigated baseline, at equal realised total shots.
- **Declared practical-effect threshold δ = 0.01 in approximation-ratio units** (1 percentage point of `⟨C⟩ / C_max`), i.e. an absolute cut-value difference of `0.01 × C_max` (0.05–0.12 depending on instance). Differences smaller than δ are reported as *statistically resolvable but not practically meaningful*, never as "worse/better" without that qualifier.
- Every effect is reported as an **absolute difference with a 95% CI**, alongside the ratio and the problem scale. Ratios are never reported alone.

## 3. Instances, methods, noise, budgets, calibration policy

**Instances** — 6 distinct connected 6-vertex graphs, verified pairwise non-isomorphic with
`networkx.is_isomorphic` (an earlier candidate was found isomorphic to `k33` and replaced):

| name | edges | degrees | bipartite | C_max |
|---|---|---|---|---|
| prism | 9 | 3-regular | no | 7 |
| cycle6 | 6 | 2-regular | yes | 6 |
| k33 | 9 | 3-regular | yes | 9 |
| octahedron | 12 | 4-regular | no | 8 |
| path6 | 5 | tree | yes | 5 |
| wheel5 | 10 | mixed 2–4 | no | 8 |

**Algorithm.** QAOA, p = 1, at the **best-known ansatz reference parameters** for each instance
(60 multistart exact-statevector optimisations; `configs/v2/references.json`). The reference is a
**multistart numerical best-known value, explicitly not a proven global ansatz optimum**
(`reference_is_proven_global_optimum: false`). **TFIM is dropped**: the v1 in-loop TFIM arm never
converged and would add an inconclusive second arm rather than a valid comparison.

**Methods.** `none`, `zne`, `rem`, `zne_rem`.

**Noise.** `ideal` (reference), `dev_lagos` (readout-dominated, median readout error 0.169),
`dev_algiers` (gate-dominated, median readout error 0.011). Both are static IBM calibration
snapshots shipped with `qiskit-ibm-runtime` 0.42.0, both `cx`-native, ≥7 qubits.

**Budgets.** Total shots per estimate B ∈ {1500, 6000, 24000}, matched **exactly** across methods
within each cell (pilot verified realised deviation 0.0000%).

**Calibration policy.** **Held fixed at `per_estimate` for every comparison in this study.** The v1
study confounded its claimed ranking reversal with a policy change between stages; here the policy
never varies within a comparison. `cal_fraction = 0.20` of B. Reuse (`amortised`) is a declared
*sensitivity check only* (§8), analysed separately and never merged.

**ZNE.** Global unitary folding at **odd** scale factors (1, 3, 5) — following Majumdar *et al.*
(IEEE QCE 2023) — Richardson extrapolation, fitted post-transpilation and re-transpiled at
`optimization_level=0` only. Realised per-scale gate counts are recorded in every row.

**REM.** Tensored per-qubit confusion-matrix inversion with clipping and renormalisation, calibrated
on the physical qubits each clbit actually reads. `rem_negative_mass` and `rem_cond_number` recorded per cell.

## 4. Seed structure

All randomness from `numpy.random.SeedSequence` with named roles (`src/qemstudy/v2/seeding.py`),
master entropy `20260916_0001`. Roles: `init_params`, `optimizer`, `simulator`, `calibration`,
`transpiler`, `basis`, `scale`, `bootstrap`. **Seeds 0–29** (30 per condition), fixed here before
any run. Simulator draws are **independent** across arms — common random numbers were not adopted.
Ansatz parameters are identical across arms by construction (the reference parameters), which is what
makes the per-seed pairing valid.

## 5. Sample size rationale

From the **pilot** (32 pairs per method, instances `prism`/`k33`, budget 6000):

| method | mean \|D\| | sd | Cohen's d | n for 80% power, α=0.05 | planned n |
|---|---|---|---|---|---|
| rem | 0.320 | 0.373 | 0.86 | 11 | 360 |
| zne | 0.287 | 0.217 | 1.32 | 5 | 360 |
| zne_rem | 0.701 | 0.429 | 1.64 | 3 | 360 |

Planned n per method for PQ = 6 instances × 2 device noise × 30 seeds = **360 pairs**, far above
requirement; the study is powered for the *secondary* comparisons, not the primary one.
For SQ, the largest observed seed-to-seed sd was 0.58 (`zne_rem`); detecting the practical threshold
δ ≈ 0.07 cut units in a paired design needs n ≈ (2.80 × 0.58 / 0.07)² ≈ 538 in the worst case —
we have 6 × 30 = 180 pairs per (noise, budget), so **the `zne_rem` arm is expected to be
under-powered at δ and this is declared in advance**, not discovered afterwards. 30 seeds is used
because it is affordable under the shared-VPS budget, not because 30 is a sufficiency rule.

## 6. Analysis plan

- **Pairing.** All comparisons are **paired on (instance, seed)** — never unpaired group means.
- **Tests.** Wilcoxon signed-rank (primary, distribution-free) with a paired *t*-test reported alongside. Effect sizes as mean paired differences with **BCa bootstrap 95% CIs** (10 000 resamples, `bootstrap` seed role).
- **Multiplicity.** Two declared families, Benjamini–Hochberg FDR at 0.05 within each:
  - **F1 (implementation impact):** 3 methods × 2 device-noise conditions = **6 tests**.
  - **F2 (method vs unmitigated at matched budget):** 3 methods × 3 noise × 3 budgets = **27 tests**.
  - Anything outside F1/F2 is exploratory and labelled as such.
- **CI overlap is never used as a decision rule.**
- Individual-run variation is reported (per-seed distributions), not only means.
- Costs (`circuit_shots`, `calibration_shots`, executions, wall-clock) are reported for every arm.

## 7. Stopping rules

Fixed grid; no interim-result-dependent stopping. The run executes in resumable batches until the
grid completes. If the shared VPS prevents completion, **whole budget levels are dropped in the order
24000, then 1500** (recorded in the manuscript), never individual instances, seeds, methods or noise
conditions. No cell is excluded on the basis of its outcome.

## 8. Planned sensitivity checks (declared now, analysed separately from confirmatory results)

1. **REM clipping**: rerun a subgrid with `clip=False` (raw quasi-distribution) to measure whether clipping changes conclusions.
2. **Calibration reuse**: rerun a subgrid with `amortised` calibration to quantify the policy effect that v1 confounded.
3. **Extrapolation family**: linear vs Richardson on the same (1,3,5) data.
4. **Conditioning**: relation between `rem_cond_number` and REM error, given `dev_lagos` qubit 2 has a 46.4% readout error.
5. **Instance-level heterogeneity**: per-instance effects reported, not just pooled.

## 9. Exclusions

None planned. Cells that error out are re-run; if any cell cannot be produced, it is reported as
missing with the reason. Unsuccessful and null results are reported.

## 10. What this study will NOT claim

No in-loop/optimisation claim (the corrected in-loop experiment is out of scope at this compute
budget); no hardware claim; no quantum-advantage claim; no generalisation beyond p = 1, 6 qubits,
IBM `cx`-native superconducting snapshots, one REM implementation and one folding style.
