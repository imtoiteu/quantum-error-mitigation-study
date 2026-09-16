# Response to Independent Review — Round 3

**Branch:** `review-round3` · **Preserved:** `main` @ `2fee260`, `review-fixes` @ `a5e3bc7`,
`review-round2` @ `1595f9f` · **Date:** 2026-09-16 · **Simulator-only.**

Each issue was **reproduced before being fixed**, and every validation claim was re-checked against
the actual code path rather than against whether the test passed. Scope is unchanged: same
instances, noise conditions, methods, budget and seed count.

| # | Issue | Status | Evidence | Code | Manuscript |
|---|---|---|---|---|---|
| 1 | REM oracle probability ordering | **Confirmed, fixed** | §1 | `src/qemstudy/v2/ordering.py`, `tests/test_rem_indexing.py` | §IV-B, Table I |
| 2 | M3 claim overstated | **Confirmed, fixed** | §2 | `experiments/v2/positive_control_m3.py` | §V |
| 3 | Method-dependent compilation | **Confirmed, rerun** | §3 | `seeding.py`, `runner.py`, `configs/v2/confirm_round3.yaml` | §III, §VI |
| 4 | Decision-cost endpoint | **Accepted, replaced** | §4 | `experiments/v2/analyze_round3.py` | §VI, Table V |
| 5 | Near-tie reporting | **Accepted, expanded** | §5 | `analyze_round3.py` | §VI, Table V |
| 6 | Provenance wording | **Accepted, corrected** | §6 | — | §IX; `REVIEW_RESPONSE_round2.md` §8 |

---

## 1. Probability ordering in the REM oracle — confirmed, and the old test was circular

**Two distinct defects in our own test, both confirmed.**

**(a) Ordering.** `Statevector.from_instruction(circ.remove_final_measurements())` returns
amplitudes indexed by **physical qubit**; measured counts are indexed by **classical bit**. Direct
check, preparing $|1\rangle$ on virtual qubit 0:

| `initial_layout` | statevector argmax | measured argmax | agree |
|---|---|---|---|
| `[0,1,2,3]` | `0001` | `0001` | yes |
| `[3,2,1,0]` | `1000` | `0001` | **no** |
| `[1,3,0,2]` | `0010` | `0001` | **no** |

**(b) Circularity.** The round-2 oracle generated its noisy test vector with `rem.tensored()` and
then recovered it by inverting that same matrix. It could not have detected an error in the shared
object.

**Fix.** `src/qemstudy/v2/ordering.py` adds two independent pieces:
`phys_to_clbit_probs()` re-indexes explicitly, and `apply_readout_bitwise()` applies per-bit flip
probabilities directly — a different code path from the tensored inversion.

**Both are validated against independent references, not against each other:**

- re-indexing vs a 400k-shot Aer measurement: max difference **3.95e-04** (shot noise), against
  **8.11e-01** for the un-reindexed vector;
- bitwise channel vs Aer's own `ReadoutError` model at 600k shots: max difference **9.7e-04**.

The rewritten oracle uses an **asymmetric** probe state (so no permutation is invisible by symmetry),
non-identity maps, and unequal per-qubit errors (0.30, 0.02, 0.15, 0.05). It **generates** with the
bitwise channel and **recovers** with the tensored inversion. Results: aligned calibration recovers
to $\sim\!10^{-16}$; misindexed fails by **1.2e-01 to 2.9e-01**; the identity layout is asserted as
a degenerate case where the defect is invisible; and the folding oracle is asserted blind at $p=0$.

## 2. The M3 claim — confirmed overstated, now a genuine correction control

**Confirmed.** The round-2 script used M3 **only** for `final_measurement_mapping` and then called
*our* `apply_rem` for both outputs. That supports a claim about mapping agreement, not about
independent mitigation, yet the text implied the latter.

**Fix.** The control now runs a **genuine M3 correction**: true per-qubit matrices are injected with
`M3Mitigation.cals_from_matrices`, and `M3.apply_correction` performs the correction using the qubit
list from M3's own `final_measurement_mapping`.

| `initial_layout` | (A) map agreement | (B) M3 correction, correct qubits | (B) M3 correction, virtual index |
|---|---|---|---|
| `[0,1,2,3]` | yes | 4.1e-05 | 4.1e-05 *(degenerate)* |
| `[3,2,1,0]` | yes | 3.4e-05 | **2.1e-01** |
| `[1,3,0,2]` | yes | 4.0e-05 | **1.2e-01** |
| `[2,0,3,1]` | yes | 2.4e-05 | **2.9e-01** |

(A) and (B) are now reported as **separate claims**. The unsupported
"independent-mitigation validation" wording is removed. We still make **no claim that any released
library is defective**: the failing configuration is our own virtual-index integration, reproduced
deliberately, and the control's scope is stated (four layouts, four qubits, injected rather than
measured calibration).

## 3. Method-dependent compilation — confirmed confound, affected block rerun

**Confirmed.** The transpiler seed derived from the full cell coordinates, which included `method`.
On `prism`/`dev_lagos`/seed 0 the four methods produced **two distinct base circuits**:

| method | routing permutation |
|---|---|
| `none`, `zne_rem` | `(1,2,5,3,0,4)` |
| `zne`, `rem` | `(0,2,5,1,3,4)` |

Gate counts and depth matched, but routing determines which physical qubit carries which logical
qubit, and physical qubits have different error rates. **The method ranking was confounded with
compilation.**

**Fix.** `compilation_coords()` accepts **only** `instance`, `noise`, `seed`, `compile_rep` and
raises on anything else, so compilation cannot silently acquire a dependence on the arm again.
Verified: 4 methods × 2 budgets now yield **one** base circuit. Compilation and sampling use
**separate named streams**; `compile_rep = seed`, so the 30 seeds supply 30 compilation replicates
at no extra cost (a blocked design, declared in the protocol rather than discovered later).

Every row records a `base_fingerprint` over (initial layout, routing permutation, clbit→physical
map, gate counts, depth), and **the analysis asserts it is identical across all arms of a cell**.

**Rerun scope and reuse justification** (`docs/confirmation-protocol-round3.md` §5): the ranking,
winner-change and decision-cost block is **rerun**. The implementation contrast within a fixed
method was *not* confounded — `impl` was never in the transpiler coordinates — but it is recomputed
from the round-3 data anyway rather than mixing campaigns. The deterministic oracles, the M3
control and the noise-scaling audit have no compilation dependence and are unaffected.

## 4. Decision-cost endpoint — replaced

**Accepted.** Round 2 subtracted the **minimum over methods on the evaluation replicate**. That
minimum is a noisy realisation, not the minimum expected risk, so it is a biased reference.

**Replacement (primary endpoint).** For each cell, with $m_L$ the method selected on the selection
replicate under the legacy implementation and $m_C$ the method selected under the corrected one,

$$\Delta_{\text{held-out}} = \frac{\ell^{(1)}(m_L) - \ell^{(1)}(m_C)}{C_{\max}},$$

where $\ell^{(1)}$ is the loss on the **independent** evaluation replicate under the corrected
implementation. This is a **paired difference between two named selections**, with no minimum taken.

- **Estimand:** the mean of $\Delta_{\text{held-out}}$ over the **six fixed instances**, equally weighted.
- **Resampling unit:** **seed within instance** (stratified bootstrap). A **cluster bootstrap over
  instances** (6 clusters) is reported alongside as the weaker generalisation interval, and both are
  labelled wherever they appear.

## 5. Near ties — separated along both axes

**Accepted.** Round 2 reported one pooled near-tie rate. Round 3 reports, for **each candidate set**
(three mitigated methods; and the same plus unmitigated), over **all cells** and over
**changed-winner cells** separately:

- **practical**: gap below the declared threshold $0.01\,C_{\max}$;
- **statistical**: gap within the Monte-Carlo scale of the selection replicate.

These are different notions and are never merged. The protocol, tests, intervals and manuscript use
the same definitions.

**Changes made after seeing results are labelled as such** in `docs/confirmation-protocol-round3.md`
§8: the held-out endpoint, the separated near-tie reporting, and the compilation fix were all
introduced after round-2 results existed. They are corrections prompted by review, not selections
made to improve an outcome, and the round-2 numbers they replace are retained and shown.

## 6. Provenance wording — corrected

**Accepted.** The statement that the round-2 run "was launched from a clean tree" overstated the
evidence. The recorded hashes establish only that the **eight execution-path files matched their
committed versions**; they say nothing about the rest of the working tree, and the rows themselves
record `git_dirty=True`. The dirty flag arises because the run's own log file is created by the
shell redirect before `provenance()` executes, and logs are tracked — that is an explanation, not a
clean-tree claim.

**Verified execution-file hashes do not imply a clean working tree.** Wording corrected in
`REVIEW_RESPONSE_round2.md` §8, `FINAL_REVIEW.md` and the manuscript. **Original provenance fields
in all stored rows are unchanged.**

---

## Results and remaining uncertainties

*(§7 below is completed from the round-3 run; see `results/v2r3/processed/`.)*
