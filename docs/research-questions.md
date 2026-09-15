# Research Questions and Hypotheses

**Compiled:** 2026-09-15 · **Status:** pre-registered before pilot execution.

Each question states the hypothesis, the measured quantity, the decision rule, and what a
**negative result** looks like. Confirmatory questions are separated from exploratory ones.

---

## Confirmatory questions

These three are the pilot's reason to exist. They are fixed before any data is collected, and the
analysis for each is specified below.

### RQ1 — Does error mitigation still help when total shot cost is held constant?

> Under a fixed **total** shot budget *B* per expectation-value estimate, does any mitigation
> method reduce the error in the estimated objective relative to spending all *B* shots unmitigated?

- **Motivation:** premises P1–P2 in `docs/novelty-gap.md`. ZNE with *k* noise-scale factors spends *B/k* shots per point, so its variance grows even as its bias falls.
- **Primary metric:** absolute error \|Ê − E_exact\| of the objective at fixed, pre-optimised parameters, where E_exact is from exact diagonalisation (VQE) or brute-force enumeration (QAOA).
- **Secondary metric:** root-mean-square error (RMSE) over seeds, decomposed into bias² + variance.
- **Design:** every method receives exactly *B* total shots. Unmitigated: *B* shots on one circuit. ZNE(k scales): *B/k* per scale. REM: *B* − *B_cal* on the circuit, *B_cal* on calibration. ZNE+REM: budget split is documented per config.
- **Decision rule:** a method "helps" at budget *B* if its mean absolute error is lower than unmitigated with non-overlapping 95% bootstrap CIs across ≥5 independent seeds.
- **Negative result (fully acceptable):** no method beats unmitigated at any tested *B*. This is a publishable finding at a benchmarking venue and is explicitly *not* a project failure.

### RQ2 — Where is the crossover in shot budget, and does it differ between methods?

> How does the help/harm verdict of RQ1 change as *B* is swept, and is the crossover budget
> different for ZNE, REM, and their composition?

- **Motivation:** Alfaro (arXiv:2605.08251) establishes analytically that a crossover exists for ZNE. We measure it empirically and — the part not covered by that work — compare where it sits for a *cheap* method (REM, overhead ≈ 1×) versus an *expensive* one (ZNE, overhead = k×).
- **Metric:** mean absolute error vs. *B*, per method, per noise model; crossover *B\** = smallest budget at which a method's CI falls entirely below unmitigated.
- **Hypothesis H2:** REM's crossover budget is lower than ZNE's, because its overhead is additive (one calibration set) rather than multiplicative.
- **Negative result:** no crossover within the tested range, or crossovers indistinguishable within CIs.

### RQ3 — Does the estimation-stage verdict transfer to the full optimisation loop?

> Does a method that improves *expectation-value estimation* at fixed parameters also improve the
> *final converged objective* when placed inside the VQA optimisation loop at the same total budget?

- **Motivation:** noise-induced barren plateaus (Wang *et al.* 2021; Singkanipa & Lidar 2025) mean a lower-bias estimator can still fail to guide an optimiser, especially if it has higher variance. This is the gap between "mitigation works" and "mitigation is useful".
- **Metric:** final objective error after a fixed number of optimiser iterations, and the total circuit evaluations consumed.
- **Hypothesis H3:** the ranking of methods changes between the estimation stage and the in-loop stage, with high-variance methods (ZNE) doing relatively worse in-loop.
- **Negative result:** rankings are identical, i.e. the cheap estimation-stage experiment is a sufficient proxy. This would itself be a useful methodological finding.

---

## Exploratory questions

Analysed and reported, but **not** used to support headline claims. Any pattern found here requires
a fresh confirmatory experiment before it may be claimed.

- **EQ1 — Noise-strength sensitivity.** How does the verdict change as a scalar noise-strength multiplier λ is swept over the parametric noise model? Is there a noise level above which all mitigation fails?
- **EQ2 — Noise-model sensitivity.** Do conclusions drawn under a 5-qubit-era calibration snapshot (`FakeManilaV2`) hold under a modern 127-qubit one (`FakeKyiv`)? This tests whether results are an artifact of one device generation.
- **EQ3 — Algorithm sensitivity.** Do VQE (energy, continuous) and QAOA (approximation ratio, combinatorial) agree on the method ranking?
- **EQ4 — Extrapolation-fit sensitivity.** How much of ZNE's performance depends on the choice of fit (linear vs. Richardson vs. exponential)? A large dependence is itself a threat to ZNE's practical usefulness.
- **EQ5 — Wall-clock vs. shot cost.** Does the shot-based cost model agree with measured classical wall-clock overhead? Relevant because REM's cost is partly classical post-processing.

---

## Explicit non-questions

Stated so that scope creep is visible if it happens:

- We do **not** ask whether quantum hardware beats classical methods. No advantage claim is in scope.
- We do **not** evaluate PEC or CDR. Both need a noise-learning or training phase whose cost model differs enough to require a separate design (see `docs/novelty-gap.md` §D).
- We do **not** claim results transfer to real hardware. All Phase-3 results are **simulator-only** and will be labelled as such in every figure and table.
- We do **not** study circuits large enough to be classically hard. The pilot is 4–8 qubits by design.

---

## Pre-registered analysis commitments

1. Seeds are fixed in config files and committed **before** runs; results from unlisted seeds are not reportable.
2. All runs are reported. There is no "best run" selection. Aggregates are mean ± 95% bootstrap CI over seeds.
3. Total shots consumed, circuit evaluations, and wall-clock are logged per condition and reported in every comparison table.
4. If a comparison is made at unequal budget for any reason, the inequality is stated in the caption of that specific table or figure.
5. Exploratory findings are reported in a section titled "Exploratory" and are never described as confirmed.
