# Response to Independent Review — Round 2

**Branch:** `review-round2` · **Frozen v1 snapshot:** `main` @ `2fee260` (untouched)
**Round-1 package reviewed:** `a5e3bc7` · **Date:** 2026-09-16 · **Simulator-only.**

Every finding below was **independently reproduced before any fix was written**. Where the review is
correct, we say so plainly and state what the corrected claim is. Where a claim of ours does not
survive, it is withdrawn rather than softened.

Reproduce the verification and the fixes:
```bash
.venv/bin/python tests/test_v2_correctness.py        # folding oracle, exact (no sampling)
.venv/bin/python tests/test_rem_indexing.py          # NEW: REM indexing oracle
.venv/bin/python experiments/v2/noise_scaling_audit.py
.venv/bin/python experiments/v2/positive_control_m3.py
.venv/bin/python experiments/v2/analyze_round2.py
```

---

## 1. Pilot contamination — **CONFIRMED. Claim withdrawn.**

**Verified.** All **224 / 224** round-1 "corrected pilot" rows share an experimental key with a
main-study row, and every one reproduces the main-study value **bit-for-bit** (max difference
< 1e-15). Example: `(k33, dev_algiers, none, 6000, seed 0, v2)` = `5.9656666666666665` in both files.

**Cause** is finding 2: the round-1 stream coordinates were `(run_id, eval_id, basis, scale)`, so
`instance`, `noise`, `method`, `budget` and `impl` did not enter the seed. Cells differing only in
those factors drew identical shot noise.

**Withdrawn.** Round 1 contained **no independent confirmation of anything**. The pilot and the main
study are one exploratory campaign, and are now described that way. The word "confirmation" no
longer appears in connection with round-1 data.

**Correction.** `docs/confirmation-protocol-round2.md` was committed **before** any round-2 data, and
a bounded fresh run executes in a **new, never-used namespace** `v2r2_confirm_2026_09_16` from the
clean commit `c228cf4`. Round-1 data is retained unaltered.

## 2. Random streams — **CONFIRMED. Rewritten.**

`src/qemstudy/v2/seeding.py` now builds the coordinate tuple from the **complete cell identity**
(`instance, noise, method, budget, seed, eval_id, basis, scale`) inside a named campaign namespace,
and raises on an unrecognised field so a factor cannot be silently dropped again.

**Intentional pairing is now explicit.** `impl` is *deliberately excluded* from the coordinates:
the defective and corrected implementations see identical shot noise for the same cell. This is
common random numbers, it is the estimand F1 targets, and the analysis treats F1 as a paired
within-cell contrast. Every other factor is independent.

**We do not claim hashing makes collisions impossible.** `audit_collisions()` checks the realised
coordinate set of an actual run; over the 19,440 coordinates of the round-2 grid it reports
**0 collisions**, and that empirical result is recorded with the data.

**Dependence is now handled in inference** — see §7.

## 3. Readout audit — **CONFIRMED. Result was vacuous; corrected.**

**Verified.** The old `noise_scaling_audit.py` called `remove_final_measurements()` and then saved
the density matrix. Aer applies readout error **at measurement**, so the readout channel was never
applied. Direct check:

| computation | ⟨ZZ⟩ |
|---|---|
| old path (measurements removed) | **1.000000** |
| measured under the readout channel, 400k shots | 0.809965 |
| analytic $(1-2p)^2$ at $p=0.05$ | **0.810000** |

The reviewer's value is exactly right. **Our "exactly invariant" evidence was a computation on a
circuit with no measurement.**

**Corrected.** The audit now takes exact density-matrix probabilities and applies the explicit
response matrix, $p_{\text{meas}} = A\,p$, with no sampling:

| noise present | scale 1 | scale 3 | scale 5 | ratio 5/1 |
|---|---|---|---|---|
| none | 1.000000 | 1.000000 | 1.000000 | 1.0000 |
| gate noise only ($10^{-2}$) | 0.980100 | 0.941480 | 0.904382 | 0.9227 |
| **readout only ($p=0.05$)** | **0.810000** | **0.810000** | **0.810000** | **1.0000** |
| both | 0.793881 | 0.762599 | 0.732549 | 0.9227 |

**The substantive conclusion survives but is restated correctly:** readout error contributes a
*constant multiplicative attenuation that does not vary with the scale factor*, so folding cannot
extrapolate it away. It does **not** leave the expectation untouched. Supplementary and manuscript
text updated.

## 4. Separate correctness oracles — **CONFIRMED. New oracle added.**

The review is right that the folding oracle cannot detect misindexed REM: it runs at zero readout
noise, where every response matrix is the identity and any permutation of identities is the
identity. We now **demonstrate that blindness as a test assertion**, so the limitation is recorded
rather than assumed away.

`tests/test_rem_indexing.py` adds a deterministic oracle with **unequal known per-qubit response
matrices** ($p$ = 0.30, 0.02, 0.15, 0.05), a **non-identity measurement map**, and an
**independently computed reference** (exact statevector probabilities propagated through the
explicit response matrix). No sampling.

| layout | aligned calibration, max error | misindexed calibration, max error |
|---|---|---|
| `[0,1,2,3]` (identity) | 1.1e-16 | 1.1e-16 — *defect invisible, as expected* |
| `[3,2,1,0]` | 5.6e-17 | **1.8e-01** |
| `[1,3,0,2]` | 5.6e-17 | **1.3e-01** |
| `[2,0,3,1]` | 1.7e-16 | **4.9e-02** |

**Sampled "exact" test replaced.** The former T2 estimated an expectation from 40,000 shots and
called the comparison exact. It now compares **exact probability vectors**. Doing so surfaced a real
detail we had not seen: the deviation is **exactly 0 for Clifford circuits** but a **constant
1.04e-11** when continuous rotations are present — *constant across scales 3, 5 and 9*, so it is
floating-point angle representation in the inverted gates, not length-dependent accumulation. The
tolerance is now justified by that measurement instead of asserted, and Clifford exactness is a
separate assertion (T2b).

## 5. Interpretations — **CONFIRMED. "Randomises" withdrawn.**

**Verified against our own round-1 data.** Ratio of |mean signed difference| to mean |difference|:

| noise | method | mean \|D\| | mean signed | ratio |
|---|---|---|---|---|
| dev_algiers | ZNE | 0.405 | +0.397 | **0.980** |
| dev_algiers | ZNE+REM | 0.459 | +0.455 | **0.992** |
| dev_lagos | ZNE | 0.139 | −0.134 | 0.967 |
| dev_lagos | ZNE+REM | 0.676 | −0.428 | 0.633 |
| dev_lagos | REM | 0.436 | −0.272 | 0.623 |
| dev_algiers | REM | 0.006 | −0.001 | 0.135 |

Four of six arms are **nearly one-directional**. The statement "the defect randomises results rather
than biasing them" is **wrong and is removed everywhere** — abstract, body, figure captions, commit
narrative and handoff.

**Four quantities are now separated** and reported individually (`R2_bias_variance.csv`):
difference between *estimates*; difference between *absolute estimation errors*; estimator **bias**
(mean signed deviation from the exact value); sampling **variance** across seeds. Round 1 reported
the second while describing it in the language of the third.

**Universal language removed.** "at every depth, noise level and shot count" is withdrawn. Two
explicit invisibility conditions are now stated in the paper and asserted in the test suite:
non-identity permutations are invisible for symmetric states and observables, and REM misindexing is
invisible whenever the response matrices are equal — including every zero-readout-noise case.

## 6. Winner and regret analysis — **CONFIRMED. Redesigned.**

- **Scope is now stated wherever a rate appears.** The round-1 75.8% selected among **three
  mitigated methods** on **single finite-shot realisations**. Including the unmitigated option
  leaves it unchanged on round-1 data (273/360), because unmitigated rarely wins at $B=6000$ on
  device noise — we report both.
- **Near ties are quantified.** In round-1 data, **24.7%** of cells have a gap below 0.02 between the
  best and second-best mitigated method. Round 2 reports the gap distribution directly.
- **Same-sample language withdrawn.** "best attainable error" and "true regret" are removed. A
  same-sample minimum is now called an *observed same-sample discrepancy*.
- **Split-sample regret introduced.** Round 2 runs **two independent evaluation replicates** per
  cell: replicate 0 selects the method, replicate 1 measures the consequence. That is the only
  regret number the paper reports as a decision cost.
- **Per-instance mean rankings are reported alongside per-seed rates**, since they answer different
  questions. We reproduce the reviewer's exploratory result on round-1 data: the mean-level winner
  changes in **11 of 12** (instance, noise) conditions, both among mitigated methods and including
  the unmitigated option. As the reviewer notes, this is *not* independent confirmation, and it is
  labelled exploratory.

## 7. Statistical analysis — **CONFIRMED. Inference model replaced.**

- **Scope declared.** Primary inference is over the **six fixed benchmark instances** — a finite,
  named population. They are not a random sample and we do not claim they are.
- **Dependence respected.** 180 observations were never 180 independent draws: seeds are nested in
  (instance, noise) and the same seeds recur across methods and implementations. Primary uncertainty
  now comes from a **stratified bootstrap** (resample seeds *within* instance, average over the six),
  and a **secondary instance-level cluster bootstrap** (6 clusters) indicates what generalisation
  beyond these instances would look like. Both are reported side by side; the cluster interval is
  always wider and is labelled generalisation-oriented.
- **Normalisation before averaging.** Every difference is divided by that instance's own $C_{\max}$
  before aggregation, so instances with larger cut values no longer dominate.
- **Tests target the declared estimand**, and we state explicitly that **BH adjustment does not
  repair a sampling model** — it is applied within a declared family after the estimand and
  dependence structure are fixed.

## 8. Provenance — **CONFIRMED. Reconstructed, not relabelled.**

All 7,560 round-1 rows record `git_commit=414fa51`, `git_dirty=True`, `config_sha256=86ed20de…`.

**Reconstruction evidence** (`git show`, content hashes):
- the recorded config hash **still matches** the current `configs/v2/main_study.yaml` byte-for-byte;
- every **execution-path** file — `runner.py`, `circuits.py`, `rem.py`, `seeding.py`, `instances.py`,
  `scoring.py`, `noise.py`, `run_study.py` — is **byte-identical** between `414fa51` and the post-run
  commit `830ebdc`;
- the only files that changed in that window were *analysis and reporting* scripts
  (`analyze_main.py`, `make_tables.py`, `make_claim_evidence.py`, `make_package.py`,
  `noise_scaling_audit.py`), none of which participates in generating a data row.

**The `git_dirty=True` label stands and is not revised.** This is reconstruction, not a clean-run
guarantee. Round-2 rows additionally record the **SHA-256 content hash of every execution-path
file**, and the fresh run was launched from a clean tree at commit `c228cf4`.

## 9. Contribution and external comparison — **ACCEPTED. Contribution reframed.**

**Physical-qubit-aware calibration is established practice.** The standard library ships
`mthree.utils.final_measurement_mapping` for exactly this purpose, and IBM's documented workflow is
*"First, we find the physical qubits that the virtual qubits map to. Next, we perform calibration on
the physical qubits to obtain their measurement noise profile."* (IBM Quantum blog, H. Kang,
3 April 2024). We treat it as established and cite it.

**Positive control run, and we do not blame any library.** `experiments/v2/positive_control_m3.py`
runs M3 (mthree 3.0.0) **as documented**. Its independently implemented mapping agrees with our
corrected map on all four layouts, and both recover the exact distribution to machine precision;
only our own earlier virtual-index integration fails. We explicitly do **not** misuse a library and
then call the library defective.

**Contribution reassessed and narrowed to:**
> a **bounded integration-failure case study** with a **reusable, sampling-free validation artifact**
> — two deterministic oracles that detect these integration errors without a noise model, plus a
> quantified measurement of how far such an error can move a complete budget-matched benchmark.

It is **not** the discovery of an unknown hazard, and the paper says so in the introduction.

**"Retraction" framing removed.** Round 1 was an unpublished internal pilot. It is now described as
a **pilot correction**, in one short subsection, and it is not a novelty claim.

## 10. Finishing — actions taken

Only the experiments needed to resolve these issues were run; the round-1 grid was **not** re-run.
The round-2 grid is bounded (5,040 cells, one worker, capped threads, `nice -n 15`, checkpointed).
All tables, figures, abstract, claims, protocol deviations and limitations are regenerated from data.
The pipeline diagram was rebuilt (overflow fixed, prohibited universal language removed, M3's
`final_measurement_mapping` noted) and the compiled PDF is visually inspected page by page.
Venue is reassessed in `docs/venue-decision.md` without assuming TQE is an easier fallback.

---

## Remaining uncertainties, stated plainly

1. **Round-1 data cannot be repaired.** It remains a single exploratory campaign with correlated
   streams. Nothing in it is confirmatory, and the corrected conclusions rest on round-2 data.
2. **Six fixed instances, two device snapshots, $p=1$, 6 qubits, one REM variant, global folding,
   Richardson only.** Generalisation beyond this is not supported; the cluster interval indicates
   how much wider honest generalisation would be.
3. **Literature search is still bounded** — arXiv's API remained rate-limited from this host, so no
   systematic sweep or forward-citation analysis was performed.
4. **The contribution is modest by construction.** With physical-qubit-aware calibration established
   and the tooling already available, the case study's value rests on the validation artifact and
   the quantified downstream effect, not on novelty of the hazard.
