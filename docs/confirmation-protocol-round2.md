# Round-2 Confirmation Protocol (prospectively fixed)

**Written and committed 2026-09-16, before any round-2 data exists.** Internal prospective
protocol, **not** an external preregistration. Simulator-only; no hardware; no advantage claim.

## 0. Why a fresh run is needed

The round-1 "corrected pilot" is **not** independent of the round-1 main study. All 224 pilot rows
share experimental keys with main-study rows and reproduce their values **bit-for-bit**, because the
round-1 seed hierarchy omitted `instance`, `noise`, `method`, `budget` and `impl` from the stream
coordinates. Nothing in round 1 may be described as independent confirmation of anything else in
round 1. Round-1 data is retained and reported as a single exploratory campaign.

## 1. Seed namespace

Fresh data uses namespace **`v2r2_confirm_2026_09_16`**, never previously used. The round-1
namespace `v2_main_2026_09_16` is **retired** and must not generate new data.

**Pairing contract.** `impl` is deliberately excluded from stream coordinates: the defective and
corrected implementations see identical shot noise for the same cell (common random numbers), so
their difference isolates the implementation. Every other factor is a coordinate, so draws are
independent across instance, noise, method, budget, seed, basis, scale and evaluation replicate.
A collision audit over the realised coordinate set is recorded with the data; we do **not** claim
hash collisions are impossible.

## 2. Design

| Factor | Levels |
|---|---|
| instances | 6 fixed (prism, cycle6, k33, octahedron, path6, wheel5) |
| noise | `dev_lagos`, `dev_algiers` (device snapshots) |
| methods | none, zne, rem, zne_rem |
| budget | 6000 total shots (matched exactly across methods) |
| seeds | 30 |
| implementations | corrected (v2) and defective replica (legacy); legacy only for mitigated arms |
| **evaluation replicates** | **2 independent replicates per cell (`eval_id` 0 and 1)** |

The two replicates exist solely to make decision regret honest (§5). Replicate 0 is the
**selection** sample; replicate 1 is the **evaluation** sample. They are never pooled.

## 3. Inference scope — stated explicitly

**Primary inference is about these six fixed benchmark instances**, i.e. a finite, named population.
Instances are not a random sample from any wider population, and we do not claim they are.

A secondary, explicitly weaker analysis treats instances as exchangeable draws and reports an
**instance-level cluster bootstrap** interval, to indicate what generalisation beyond these six
instances would look like. That interval is labelled as generalisation-oriented and is always wider.

## 4. Estimands and statistics (corrections to round 1)

1. **Normalise before averaging.** Every difference is divided by that instance's own $C_{\max}$
   before any aggregation, so instances with larger cut values do not dominate the mean.
2. **Respect the dependence structure.** Observations are **not** 180 independent draws. Seeds are
   nested within (instance, noise); the same 30 seeds recur across methods and implementations.
   Primary inference is therefore a **cluster-aware analysis with instance as the cluster unit**
   (6 clusters), using an instance-level bootstrap and reporting the per-instance effects
   themselves. Seed-level variability is reported descriptively, never as independent replication.
3. **Distinguish four quantities**, never conflated:
   - $\Delta_{\text{est}}$ — difference between two *estimates*;
   - $\Delta_{|e|}$ — difference between two *absolute estimation errors*;
   - $\hat b$ — estimator **bias**, the mean signed deviation from the exact value;
   - $\hat v$ — sampling **variance** across seeds.
   Round 1 reported $\Delta_{|e|}$ while describing it in the language of bias. Round 2 reports
   $\hat b$ and $\hat v$ separately for each arm and implementation.
4. **Tests target the declared estimand.** The implementation contrast is a paired within-cell
   comparison under common random numbers; the method contrast is an unpaired-in-shot-noise but
   instance-paired comparison. BH adjustment is applied within each declared family and is not
   treated as repairing a sampling model.

## 5. Winner and regret analysis (corrections to round 1)

- The winner set **includes the unmitigated option**, and the scope (which methods were candidates)
  is stated wherever a rate is quoted.
- **Split-sample regret.** The method is selected on replicate 0 and its consequence is measured on
  replicate 1. Same-sample minima are **not** called "best attainable", and same-sample differences
  are **not** called "true regret"; they are reported, if at all, as *observed same-sample
  discrepancies*.
- **Near ties are reported.** For each cell we report the gap between the best and second-best
  candidate; a winner change across a gap smaller than Monte-Carlo noise is not evidence of a
  substantive ranking change.
- Per-instance mean rankings are reported alongside per-seed rates, since they answer different
  questions.

## 6. Language prohibited by this protocol

- "randomises rather than biases" — round 1's own data contradicts it (|signed|/|D| = 0.98 for
  ZNE on `dev_algiers`).
- "at every depth, noise level and shot count" — non-identity permutations are invisible for
  symmetric states and observables, and REM misindexing is invisible when response matrices are
  equal (including the zero-noise case). Both are demonstrated in the test suite.
- "retraction" framing for an unpublished internal pilot. Round 1 is described as a **pilot
  correction**, not a retraction.

## 7. Provenance

Every row records the SHA-256 content hash of each execution-path file, the config hash, the seed
namespace, and the git commit and dirty flag. Round-1 rows recorded `git_dirty=True`; that label
stands and is **not** retroactively revised. Reconstruction evidence for round 1 is reported
separately (`REVIEW_RESPONSE_round2.md` §8).

## 8. Stopping and scope limits

Fixed grid, no outcome-dependent stopping. Executed in resumable batches, one worker, capped
threads, reduced priority. If resources prevent completion, whole seed blocks are dropped from the
top of the seed list and the reduction is reported; no cell is dropped for its outcome.
