# Pilot Protocol

**Compiled:** 2026-09-15 · **Status:** pre-registered. Frozen before data collection.
**All results produced under this protocol are SIMULATOR-ONLY.** No quantum hardware is used.

---

## 1. Tasks

Two problems, deliberately small, both with an exactly computable classical reference.

### 1.1 VQE task — Transverse-Field Ising Model (TFIM), n = 4

```
H = -J Σ_{i=0}^{n-2} Z_i Z_{i+1}  -  h Σ_{i=0}^{n-1} X_i        J = 1.0, h = 1.0
```

- Open boundary chain, 4 qubits, at the critical point h/J = 1 (the hardest parameter regime, and the one with the smallest spectral gap).
- **Classical reference:** exact ground-state energy by dense `numpy.linalg.eigh` on the 16×16 Hamiltonian. Cost is microseconds; there is no approximation.
- **Why TFIM and not H₂:** a molecular Hamiltonian would require `pyscf`/`qiskit-nature`, adding a heavy dependency and an integral-generation step that is itself a reproducibility risk. TFIM is defined by two scalars, is standard in the QEM benchmarking literature, and makes the classical reference trivially verifiable. This is a deliberate trade of chemical relevance for reproducibility.
- **Ansatz:** `efficient_su2(4, reps=1, entanglement='linear')` → 16 parameters, depth ~9 before transpilation.
- **Measurement bases:** 2 (Z-basis for the ZZ terms, X-basis for the X terms). Shot budgets below are **per basis**, and the per-basis split is reported.

### 1.2 QAOA task — MaxCut on the triangular prism graph, n = 6

- Graph: the 3-regular triangular prism — vertices `0..5`, edges `(0,1)(1,2)(2,0)(3,4)(4,5)(5,3)(0,3)(1,4)(2,5)`. 9 edges. Chosen because it is **deterministic** (no graph seed to report), 3-regular, and non-trivial.
- **Classical reference:** brute-force enumeration of all 2⁶ = 64 cuts. Exact maximum cut computed and asserted at run start.
- **QAOA depth:** p = 1 (2 parameters) primary; p = 2 (4 parameters) as a depth-sensitivity arm.
- **Measurement bases:** 1 (the cost Hamiltonian is diagonal in the computational basis).
- **Metric:** approximation ratio `⟨C⟩ / C_max`, following Lubinski *et al.* (ACM TQC 5, 2024).

---

## 2. Noise models

Three families. The two device models were **selected by measurement, not assumption** — candidate
backends were probed for median gate and readout error (see `docs/feasibility-report.md` §3), and
the two chosen differ by ~15× in readout error while sharing the same native two-qubit gate.

| ID | Source | Median 1q err | Median 2q err | Median readout err | Regime |
|---|---|---|---|---|---|
| `ideal` | no noise | — | — | — | reference |
| `dev_lagos` | `FakeLagosV2` (7q) calibration snapshot | 2.5e-04 | 1.05e-02 | **0.169** | **readout-dominated** |
| `dev_algiers` | `FakeAlgiers` (27q) calibration snapshot | 2.2e-04 | 7.9e-03 | **0.011** | **gate-dominated** |
| `param(λ)` | hand-built parametric model | λ·1e-3 | λ·1e-2 | λ·2e-2 | tunable strength |

- Both device models are `cx`-native and have ≥ 7 qubits, so both tasks run on both without a change of basis gate. This controls a confounder: unitary folding behaves differently for `cx` vs `ecr` vs `cz` native gates.
- `param(λ)` composes depolarizing error on 1q/2q gates, thermal relaxation (T1/T2 fixed), and symmetric readout error, all scaled by a single multiplier **λ ∈ {0.5, 1.0, 2.0}**. This supplies the noise-strength sweep required by EQ1; device snapshots alone cannot provide it.
- Device snapshots are **static calibration data shipped with `qiskit-ibm-runtime` 0.42.0**. They are not live device queries, so runs are reproducible. The package version pins the snapshot.

**Total noise settings: 1 ideal + 2 device + 3 λ levels = 6.**

---

## 3. Mitigation arms

| ID | Method | Implementation | Circuit-execution overhead |
|---|---|---|---|
| `none` | unmitigated baseline | — | 1× |
| `zne` | Zero-noise extrapolation | Mitiq 1.1.0, **global unitary folding**, scale factors `[1, 2, 3]`, Richardson fit | 3× |
| `rem` | Readout-error mitigation | tensored (per-qubit) calibration matrix, inverted, applied to the outcome distribution | 1× + calibration |
| `zne_rem` | composition | REM applied to each folded circuit's counts, then extrapolated | 3× + calibration |

- **Calibration for `rem` is measured, never read from the noise model.** It is estimated from 2n calibration circuits (prepare \|0⟩/\|1⟩ on each qubit) executed under the same noise model, consuming real shots from the budget. Using the ground-truth confusion matrix would invalidate the comparison.
- ZNE fit choice is varied in the exploratory arm EQ4 (`linear`, `richardson`, `exp`); the confirmatory arms use Richardson only.

---

## 4. The budget-matching rule (the core methodological commitment)

Every method receives **exactly the same total number of shots** *B* per objective-function
evaluation. This is the rule that makes RQ1 meaningful.

| Method | Allocation of total budget *B* (per measurement basis) |
|---|---|
| `none` | *B* shots on the bare circuit |
| `zne` | ⌊*B*/3⌋ shots at each of scale factors 1, 2, 3 |
| `rem` | 0.8·*B* on the circuit + 0.2·*B* split evenly over the 2n calibration circuits |
| `zne_rem` | 0.8·*B* split three ways over scale factors + 0.2·*B* on calibration |

- **Budget sweep:** *B* ∈ {1500, 3000, 6000, 12000, 24000}. All values divisible by 3 and by 5, so no allocation requires rounding that would break the match.
- **Reported invariant:** every results row records `shots_used`, `circuit_executions`, and `wall_clock_s`. A post-run assertion checks that `shots_used` is equal across methods within a comparison group; any deviation is surfaced, not silently absorbed.
- **Calibration amortisation.** The estimation-stage experiment charges calibration **strictly per estimate** (the conservative choice, worst case for REM). The in-loop experiment amortises one calibration set over the whole optimisation run (realistic practice). **Both accounting choices are reported**, because the choice materially changes REM's apparent cost.

---

## 5. Experiment stages

### Stage A — Estimation accuracy at fixed parameters (confirmatory: RQ1, RQ2)

Parameters are **pre-optimised once** on the ideal simulator and then frozen, so that this stage
measures estimator quality alone, with no optimiser dynamics confounding it.

- Grid: 2 tasks × 6 noise settings × 5 budgets × 4 methods × **10 seeds**
- Per condition, record: estimate, absolute error vs. exact reference, shots used, circuit executions, wall-clock.
- Analysis: mean absolute error and RMSE with **95% bootstrap CIs (10 000 resamples) over seeds**; bias²/variance decomposition.

### Stage B — In-loop optimisation (confirmatory: RQ3)

- Optimiser: **SPSA**, 40 iterations (2 objective evaluations per iteration = 80 evaluations per run). SPSA is chosen because it is the standard noisy-objective optimiser for VQAs and needs a fixed, predictable number of evaluations.
- Grid: 2 tasks × 2 device noise models × 4 methods × **5 seeds** = 80 runs.
- Fixed budget *B* = 3000 per evaluation for every method.
- Record the full optimisation trace, not just the endpoint.

### Stage C — Exploratory sweeps (EQ1–EQ5)

Run from the Stage A data where possible (λ sweep, noise-model comparison, algorithm comparison,
wall-clock) plus a small dedicated run for EQ4 (ZNE fit choice). **Reported in a separate
"Exploratory" section and never used to support a confirmatory claim.**

---

## 6. Randomness and reproducibility

- Three independent seed streams per run, all derived deterministically from a single integer `seed`: `seed_simulator`, `seed_transpiler`, and the NumPy generator for SPSA perturbations.
- Seeds for confirmatory stages: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` (Stage A), `[0, 1, 2, 3, 4]` (Stage B). Committed in `configs/` **before** execution.
- Transpilation is pinned: `optimization_level=1`, fixed `seed_transpiler`, explicit `initial_layout` for device models so qubit selection cannot drift between runs.
- Every result row carries the git commit hash, config hash, package versions, and hostname.
- Raw per-run JSON is written to `results/raw/` and committed.

---

## 7. What gets measured (required outputs)

Per the study requirements, every condition records:

1. objective error (energy error for VQE; approximation-ratio gap for QAOA)
2. variance across seeds and 95% bootstrap CI
3. mitigation overhead — both `circuit_executions` and `shots_used`
4. number of circuit evaluations
5. wall-clock execution time
6. sensitivity to noise strength (λ sweep)
7. sensitivity to shot budget (*B* sweep)

---

## 8. Pre-registered stopping and kill criteria

- If Stage A wall-clock exceeds **75 minutes**, reduce the budget sweep to {1500, 6000, 24000} and rerun — do not silently drop seeds.
- If seed-to-seed standard deviation exceeds the method-to-method difference for **all** budgets and **all** noise models, report kill criterion **K3** from `docs/novelty-gap.md` and recommend no-go.
- Kill criteria K1–K4 in `docs/novelty-gap.md` are re-checked after the pilot.

## 9. Known limitations of this protocol (stated in advance)

- **Simulator-only.** Aer noise models are approximations: they omit crosstalk, non-Markovian drift, and calibration decay. Conclusions transfer to hardware only as hypotheses.
- **Small scale.** 4–6 qubits. Results must not be extrapolated to scales where mitigation's exponential cost bites (Takagi 2022; Quek 2024).
- **One ansatz per task.** Ansatz choice is a known confounder and is not varied in the pilot.
- **Global folding only** for confirmatory arms. Local folding and identity insertion (He *et al.* 2020) are untested.
- **SPSA only.** Optimiser choice is known to dominate small-QAOA results (Shaydulin & Alexeev 2019); not varied here.
