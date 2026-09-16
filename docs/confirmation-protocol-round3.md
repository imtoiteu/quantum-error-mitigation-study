# Round-3 Protocol Addendum (prospectively fixed)

**Written and committed 2026-09-16, before any round-3 data exists.** Internal prospective
protocol, **not** an external preregistration. Simulator-only. Scope is **not** broadened: same
instances, noise conditions, methods, budget and seed count as round 2.

## 0. Why a rerun is needed

Round 2 seeded the transpiler from the full cell coordinates, which included `method`. Different
methods therefore received different routing permutations for the same instance, noise and seed —
verified: four methods produced **two distinct base circuits** on `prism`/`dev_lagos`/seed 0, with
routing `(1,2,5,3,0,4)` for `none`/`zne_rem` and `(0,2,5,1,3,4)` for `zne`/`rem`. Because routing
determines which physical qubit carries which logical qubit, and physical qubits have different
error rates, **the method ranking was confounded with compilation**.

`impl` was never part of the transpiler coordinates, so the legacy-vs-corrected contrast within a
fixed method was **not** affected (see §5 for what is reused and why).

## 1. Compilation is shared and asserted

The transpiler stream now derives from `compilation_coords`, which accepts **only**
`instance`, `noise`, `seed`, `compile_rep`, and raises on anything else. Consequently one prepared
base circuit — same initial layout, routing permutation, measurement map, gate counts and depth — is
shared by every method, budget and implementation within a cell. Verified: 4 methods × 2 budgets now
yield **one** base circuit.

Each row records `base_fingerprint`, a hash of (initial layout, routing permutation, clbit→physical
map, gate counts, depth). **The analysis asserts that this fingerprint is identical across all arms
of a cell** and reports any violation rather than absorbing it.

Compilation randomness and sampling randomness use **separate named streams** (`transpiler` vs
`simulator`/`calibration`). `compile_rep` is set equal to `seed`, so the 30 seeds supply 30
compilation replicates at no additional cost; this is a blocked design, not a confound, and it is
stated here rather than discovered later.

## 2. Namespace

Round-3 data uses **`v2r3_confirm_2026_09_16`**, never previously used. `v2_main_2026_09_16` and
`v2r2_confirm_2026_09_16` are **retired** and must not generate new data.

## 3. Primary decision-cost endpoint (replaces round 2's regret)

**Estimand.** For each cell, let $m_L$ be the method selected on the selection replicate under the
**legacy** implementation and $m_C$ the method selected under the **corrected** implementation. The
per-cell loss difference is

$$\Delta_{\text{held-out}} \;=\; \frac{\ell^{(1)}(m_L) - \ell^{(1)}(m_C)}{C_{\max}},$$

where $\ell^{(1)}$ is the absolute estimation error measured on the **independent evaluation
replicate** under the corrected implementation. The estimand is the mean of
$\Delta_{\text{held-out}}$ over the six fixed instances, each instance weighted equally.

**This is a paired difference between two named selections.** Round 2 instead compared each
selection against the *minimum over methods on the evaluation replicate*; that minimum is itself a
noisy realisation, not the minimum expected risk, and using it biases the comparison. That endpoint
is withdrawn.

**Resampling unit.** The primary interval is a **stratified bootstrap resampling seeds within each
instance**, then averaging over the six fixed instances — the resampling unit is the *seed within
instance*, and the inference target is these six instances. A secondary **cluster bootstrap
resampling instances** (6 clusters) is reported alongside as the weaker generalisation interval.
Both are labelled wherever they appear.

## 4. Near ties and indistinguishability — reported separately

Two distinct notions, never merged:

* **practical threshold**: candidates whose loss difference is below $0.01\,C_{\max}$, the declared
  practically-negligible margin;
* **statistical indistinguishability**: candidates whose difference is within the Monte-Carlo
  uncertainty of the selection replicate.

Both are reported (a) over **all cells** and (b) over **changed-winner cells only**, and separately
for each **candidate set** (three mitigated methods; and the same set plus unmitigated).

## 5. What is reused, and the justification

| Result | Status |
|---|---|
| Ranking / winner-change / decision-cost analysis | **Rerun** — directly affected by the compilation confound |
| Implementation contrast within a fixed method (F1) | **Rerun on the same fresh data.** It was not confounded (compilation never depended on `impl`), but it costs nothing to recompute from the round-3 run and avoids mixing campaigns |
| Bias/variance decomposition | **Rerun**, same reasoning |
| Two correctness oracles, M3 control, noise-scaling audit | **Not affected** — deterministic, no compilation dependence, no experimental grid |
| Round-1 and round-2 raw data | **Retained unchanged**; round 2 is reported as superseded for ranking claims, with the reason stated |

## 6. Design (unchanged size)

6 instances × 2 device noise conditions × 4 methods × budget 6000 × 30 seeds × 2 implementations ×
2 evaluation replicates = **5040 cells**, identical in size to round 2. No factor is added to gain
significance.

## 7. Stopping

Fixed grid, no outcome-dependent stopping, resumable batches, one worker, capped threads, reduced
priority. If resources prevent completion, whole seed blocks are dropped from the top of the list
and the reduction is reported.

## 8. Changes made after seeing results — declared

The following were introduced *after* round-2 results existed and are labelled as such wherever
reported: the held-out endpoint in §3 (replacing the round-2 regret definition), the separated
near-tie reporting in §4, and the compilation fix in §1. They are corrections prompted by review,
not selections made to improve an outcome; the round-2 numbers they replace are retained and shown.
