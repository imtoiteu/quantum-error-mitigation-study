# Response to Independent Review

**Branch:** `review-fixes` · **Frozen snapshot preserved:** `main` @ `2fee260` (untouched)
**Date:** 2026-09-16 · **All work simulator-only.**

Each finding below is answered with: what we tested, what the evidence shows, whether it was a
**demonstrated bug** or a **plausible concern that did not materialise**, what we changed, and what
remains a limitation. Reproduce every test with:

```bash
.venv/bin/python tests/test_v2_correctness.py          # exit 0 = all pass
.venv/bin/python experiments/v2/impact_audit.py        # affected-cell quantification
```

---

## Finding 1 — Measurement mapping  → **DEMONSTRATED BUG (two of them). Confirmed and fixed.**

### 1a. `fold()` discarded the layout-induced qubit→clbit mapping — **demonstrated**

v1 `mitigation.fold()` called `remove_final_measurements()` then `measure_all()`, which maps
physical qubit *i* → clbit *i*. That is only correct when the layout is the identity.

**Exact oracle used.** Global folding at odd scale is U·U†·U = U, so the *ideal* output distribution
must be **identical** to the unfolded circuit. Any difference is a bug, independent of noise.

**Evidence** (`tests/test_v2_correctness.py::T1`), 4-qubit circuit whose ideal outcome is the single
bitstring `0101`, line coupling map:

| initial_layout | v1 folded (scale 3) | correct | verdict |
|---|---|---|---|
| `[0,1,2,3]` | `0101` | `0101` | identity layout hides the bug |
| `[3,2,1,0]` | **`1010`** | `0101` | **corrupted** |
| `[1,3,0,2]` | **`0011`** | `0101` | **corrupted** |
| `[2,0,3,1]` | **`1100`** | `0101` | **corrupted** |

The failure is **silent** — no exception, no warning, a perfectly well-formed circuit.

### 1b. `Executor.prepare()` never passed `initial_layout` although the protocol claimed one — **confirmed**

`docs/pilot-protocol.md` §6 stated "explicit `initial_layout` for device models". The v1 code passed
none. Reconciled: v2 `circuits.prepare()` pins `initial_layout=[0..n-1]` when a coupling map is
present, and **records the layout, the routing permutation and the realised clbit→physical map in
every result row** rather than asserting them in prose.

### 1c. REM calibration was indexed by virtual, not physical, qubits — **demonstrated**

v1 calibration circuits were executed **untranspiled**, so calibration index *i* was physical qubit
*i*, while main-circuit clbit *i* read whichever physical qubit the layout assigned. On
`qaoa_p1`/`dev_lagos` the realised layout was `[3,5,4,1,2,0]`, giving:

| clbit | readout error REM assumed | readout error actually applying | ratio |
|---|---|---|---|
| 2 | 0.4638 | **0.0292** | 15.9× too large |
| 4 | 0.0292 | **0.4638** | 15.9× too small |

The confusion matrix was inverted against the wrong qubits.

### Quantified impact on the frozen v1 results

`experiments/v2/impact_audit.py` recomputes the realised layout for every condition. `none` never
folds and never calibrates, so it is unaffected everywhere.

| Condition | layout | affected methods |
|---|---|---|
| all `ideal`, all `param_lam*` | none (no coupling map) | **none — results valid** |
| `tfim`/`dev_algiers` | identity | **none — results valid** |
| `tfim`/`dev_lagos` | `[1,0,3,2]`, routing `[0,3,2,1]` | zne, rem, zne_rem |
| `qaoa_p1`/`dev_lagos` | `[3,5,4,1,2,0]`, routing `[5,1,2,3,4,0]` | zne, rem, zne_rem |
| `qaoa_p1`/`dev_algiers` | `[5,3,2,0,1,4]`, routing `[3,0,2,4,1,5]` | zne, rem, zne_rem |

- **Stage A: 450 / 2400 cells (18.8%) affected.**
- **Stage B: 30 / 40 runs (75%) affected — every mitigated arm.** Stage B ran only on `dev_lagos`.

**Consequence, stated plainly: the v1 Stage B headline ("in-loop optimisation reverses the
estimation ranking") rests on 30 corrupted runs and is RETRACTED.** It is not re-asserted anywhere
in the manuscript. The v1 ideal-noise and parametric-noise Stage A results are unaffected and remain
usable as reported.

### Fixes
`src/qemstudy/v2/circuits.py`: `fold_preserving_measurements()` splits off the terminal
measurements, folds only the unitary core, and re-attaches the **original** `(physical qubit, clbit)`
pairs into a circuit created with `copy_empty_like()` so **classical registers are preserved**
(tested: T3 checks register structure and map equality). `calibration_circuits()` prepares |0⟩/|1⟩ on
the physical qubit each clbit actually reads (T4).

---

## Finding 2 — Noise amplification → **partly a real defect (nominal factors), partly prior art we now cite**

### What we tested
Gate-count scaling per instruction type at nominal scales 2–5, and an **exact density-matrix**
computation of what folding does and does not amplify (not inferred from shots).

### Evidence
Gate counts for the QAOA `prism` circuit (base: 18 cx, 18 sx, 39 rz):

| nominal scale | cx | sx | rz | cx ratio | uniform across error-carrying gates? |
|---|---|---|---|---|---|
| 2.0 | 30 | 42 | 127 | **1.67** | **no** |
| 3.0 | 54 | 54 | 189 | **3.00** | **yes** |
| 4.0 | 66 | 78 | 277 | **3.67** | **no** |
| 5.0 | 90 | 90 | 339 | **5.00** | **yes** |

`rz` scales non-uniformly (4.85× at nominal 3) but is **error-free** in every noise model used —
verified: `NoiseModel.from_backend` reports `noise_instructions = ['cx','id','measure','reset','sx','x']`
for both devices and the `rz` target error is exactly 0.0 (virtual Z). So at **odd** scales every
**error-carrying** gate is folded a whole number of times.

**v1 used nominal scales (1, 2, 3) and fitted Richardson against those nominal values while the
realised cx amplification at nominal 2 was 1.67–2.38 and basis-dependent.** That is a genuine
misspecification. v2 uses **(1, 3, 5)**.

**What folding scales — exact, density-matrix, 4-qubit probe:**

| noise present | ⟨ZZ⟩ at scales 1, 3, 5 | conclusion |
|---|---|---|
| gate noise only (dep. 1e-2) | 0.990000, 0.970299, 0.950990 | amplified as expected |
| readout noise only (p=0.05) | 1.000000, 1.000000, 1.000000 | **exactly invariant** |

### Attribution — this is prior art, not our finding
Majumdar *et al.* (IEEE QCE 2023, arXiv:2307.05203) already state both points: odd factors
{1,3,5,…,2n+1} avoid partial folding (§II, Fig. 4), and "In conventional approaches to unitary
folding, state preparation and measurement (SPAM) error is not amplified" (§V). We **cite them and
adopt their recommendations**; we do not claim either as a contribution. Our addition is only that we
*verify* the realised amplification per gate type in every run and record it, rather than assuming it.

### Caveat we explicitly retain
Equal gate counts are **necessary, not sufficient** for uniform effective noise scaling: coherent
errors, crosstalk, idle/thermal evolution during the longer folded circuit, and non-Markovian effects
are not captured by a count ratio. We therefore validate ideal equivalence (T1, T2, T5) and report
gate counts per scale, but we do **not** claim that odd factors prove uniform noise scaling.

---

## Finding 3 — Randomness → **confirmed defect. Fixed.**

v1 reused a single `seed` for `seed_simulator`, `seed_transpiler` and the NumPy generator, and Stage B
passed `seed + n_evals` as a simulator seed, so `(run 0, eval 5)` and `(run 5, eval 0)` collided.

v2 (`src/qemstudy/v2/seeding.py`) derives every stream from `numpy.random.SeedSequence` with a named
role hashed into the spawn key. Roles: `init_params`, `optimizer`, `simulator`, `calibration`,
`transpiler`, `basis`, `scale`, `bootstrap`. Verified: 64 distinct simulator seeds over 64
`(run, eval)` pairs; the v1 collision pair now differs; streams are reproducible from coordinates.

Simulator draws are kept **independent** across arms — we did **not** adopt common random numbers.
Initial parameters *are* matched across arms where a paired comparison is made (same instance, same
reference parameters), and the pairing is reflected in the analysis (paired tests on seed).

---

## Finding 4 — Scoring → **confirmed. Fixed, and the reviewer's numbers reconcile exactly.**

v1 scored final parameters with a 200 000-shot "ideal" run, injecting shot noise into a quantity that
is exactly computable offline. v2 uses exact statevector expectation (`src/qemstudy/v2/scoring.py`).

**Reconciliation against the reviewer's independently recomputed QAOA p=1 gaps** (mean over 5 seeds,
exact statevector, stored v1 final parameters):

| method | our exact recomputation | reviewer value | match | v1 stored (200k-shot) |
|---|---|---|---|---|
| none | 0.0039843135 | 0.0039843135 | ✅ | 0.0045534657 |
| zne | 0.0227496473 | 0.0227496473 | ✅ | 0.0235604657 |
| rem | 0.0520504818 | 0.0520504818 | ✅ | 0.0527154657 |
| zne_rem | 0.7674806913 | 0.7674806913 | ✅ | 0.7668884657 |

Exact to 10 decimal places. The v1 values were biased by ~6×10⁻⁴ of pure shot noise.

**Three quantities are now kept distinct and never conflated** (`scoring.score`):
`estimation_error` (|estimate − exact noiseless value at the *same* parameters|);
`optimisation_gap_signed` (exact value at found parameters − **best-known ansatz reference**);
`gap_to_optimum_signed` (exact value − exact combinatorial optimum).

**Labelling corrected.** The ansatz reference is a **multistart numerical best-known value, not a
proven global optimum**; `configs/v2/references.json` carries
`"reference_is_proven_global_optimum": false` and the fraction of starts reaching it
(47–100% over 60 starts per instance). **Signed** gaps are reported so improvement over the reference
cannot be hidden by `abs()`. (For the v1 Stage B data specifically, no run exceeded the reference, so
`abs()` concealed nothing there — but the practice is corrected regardless.)

---

## Finding 5 — Resource accounting → **confirmed omission. Fixed.**

v1 Stage B totals omitted the offline final-scoring shots: 200 000 per run × 40 runs = **8 000 000
unreported shots**, equal to **82% of the entire reported Stage B budget of 9 732 000 shots**. The
true v1 Stage B cost was therefore ~17 732 000 shots, not the 9 732 000 reported. v2 removes those shots entirely (exact scoring costs zero shots) and
separates the remaining categories.

v2 records per cell: `circuit_shots`, `calibration_shots`, `total_shots`, `circuit_executions`,
`calibration_executions`, every measurement basis, every noise scale, and (for loops) optimizer
evaluations — plus `wall_clock_s` and `peak_rss_gb`. **Optimisation budget** and **total study cost**
are reported as separate lines; validation/scoring is reported separately again.

**Calibration policy is now an explicit, recorded parameter** (`per_estimate` / `reused`) rather than
an implicit difference between stages. The review is correct that v1 confounded its claimed ranking
reversal with a calibration-policy change (Stage A charged calibration per estimate; Stage B
amortised it once per run). The corrected study **holds the policy fixed within any comparison** and
varies it only as a declared factor.

**Integer allocation is handled transparently:** where a budget is not divisible by (bases × scales)
or by 2k calibration circuits, the residual is reported per cell rather than absorbed; the analysis
asserts realised `total_shots` equality and prints the maximum relative deviation.

---

## Finding 6 — REM definition → **documented; clipping effect measured.**

`src/qemstudy/v2/rem.py` states the full definition: independent per-qubit response model, tensored
A = ⊗_q A_q, exact `np.linalg.solve` inversion (pseudo-inverse only on singularity), negative-entry
clipping then renormalisation — **explicitly a biased estimator**. Every cell records
`rem_negative_mass` (probability mass removed by clipping) and `rem_cond_number` (2-norm condition
number of the tensored matrix), so the conditioning is observable rather than assumed.
`clip=False` returns the raw quasi-distribution so the clipping effect can be measured directly; this
is a declared sensitivity check in the main-study protocol.

**Stated assumptions that can fail:** no correlated readout error; measurement error not separable
from state-preparation error; stationary calibration. **This is one REM implementation
(tensored matrix inversion). Results must not be read as characterising M3, twirled, or
learning-based readout mitigation.**

---

## Finding 7 — Statistics and claims → **accepted in full; claims withdrawn or narrowed.**

| Review point | Action |
|---|---|
| v1 Stage B remains exploratory | Accepted, and now moot: it is **retracted** (75% of runs corrupted, Finding 1). It is reported as a retracted result, not as evidence. |
| Do not infer a mechanism from below-ground-state estimates | The order-preservation mechanism is **removed as a claim**. Unphysical estimates are reported as an observation only. |
| Do not call small absolute losses important because ratios are large | Enforced: every ratio is reported with its absolute difference and the problem scale (see `REVIEW.md` §3). The "REM 11× worse" phrasing is withdrawn — the absolute effect was 0.69% of the problem scale. |
| Do not use CI overlap as the sole comparison procedure | v2 analysis uses **paired per-seed differences** with a paired test and BH multiplicity control over a declared family, reporting effect sizes with CIs; CI overlap is never the decision rule. |
| Do not treat a finite-sample ideal-noise result as theory-guaranteed | The v1 "ideal-noise sanity check matches theory" framing is softened: it is a finite-sample observation consistent with the bias/variance argument, not a theoretical guarantee. |

---

## Remaining limitations (not fixed)

1. **Simulator-only.** Aer device snapshots omit crosstalk, drift, leakage and non-Markovian effects.
2. **Small scale.** 6 qubits, p = 1. Nothing extrapolates to sizes where mitigation cost bites.
3. **One REM implementation, one folding style** (global), one extrapolation family (Richardson/linear).
4. **IBM `cx`-native devices only.**
5. **Literature search is bounded.** No forward-citation sweep of UNITED/Majumdar was completed (arXiv API rate-limited from this host); all "not previously studied" statements are bounded accordingly (`docs/novelty-matrix.md` §6).
6. **The corrected in-loop (optimisation) experiment is not re-run at the scale needed for a confirmatory claim.** The paper therefore makes **no in-loop claim at all**; it reports estimation-stage results plus the implementation finding.
