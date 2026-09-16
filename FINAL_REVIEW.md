# Final Internal Review

**Branch:** `review-fixes` · **Frozen snapshot preserved:** `main` @ `2fee260`
**Scope:** five separate passes, run after the main study completed. Simulator-only throughout.

This document records what was checked, what was found, what was fixed, and what remains
**unresolved**. Items are not marked resolved unless there is evidence in the repository.

---

## Pass 1 — Scientific correctness

| Check | Result |
|---|---|
| Folding oracle ($UU^{\dagger}U=U$ leaves the ideal distribution invariant) | **PASS** — `tests/test_v2_correctness.py` T1, four layouts |
| Exact noiseless $\langle Z_q\rangle$ invariant under folding | **PASS** — T2, 8 layout/parameter combinations |
| Classical registers and measurement map preserved | **PASS** — T3 |
| Calibration circuits target the physical qubit each clbit reads | **PASS** — T4 |
| Folded core equals original core as an operator | **PASS** — T5 |
| `optimization_level=0` does not cancel folded pairs | **PASS** — T6 |
| Routing invariance of the measurement map across scales | **PASS** — verified separately; maps such as `(2,0,3,1)` identical at scales 1/3/5 |
| Hamiltonian/objective construction | **PASS** — TFIM dense matrix matches `SparsePauliOp.to_matrix()`; $n{=}2$ ground energy equals $-\sqrt5$ by hand-diagonalisation; MaxCut optima confirmed by brute force |
| Exact statevector scoring | **PASS** — reconciles the reviewer's independently recomputed QAOA gaps to 10 decimal places |
| Instances pairwise non-isomorphic | **PASS** — `networkx.is_isomorphic`; one earlier candidate was isomorphic to `k33` and was replaced |
| Seed hierarchy free of collisions | **PASS** — 64 distinct simulator seeds over 64 (run, eval) pairs; the v1 collision no longer occurs |

**Found and fixed during this pass:** `make_tables.py` had its `__main__` block before the
`macros()` definition (`NameError`); a scripted manuscript edit silently matched nothing because
`str.replace` is a no-op on a miss — all scripted edits now assert their anchor before writing.

## Pass 2 — Experimental validity

| Check | Result |
|---|---|
| Realised total shots equal across methods within each cell | **PASS** — maximum relative deviation reported in `results/v2/processed/budget_match_check.csv` and quoted in the paper |
| Calibration policy constant within every comparison | **PASS** — fixed at `per_estimate`; v1's stage-dependent policy change was the confound and is gone |
| Pairing on (instance, seed) rather than unpaired group means | **PASS** — `analyze_main.py` |
| Multiplicity control over declared families | **PASS** — BH FDR within F1 (6 tests) and F2 (27 tests); everything else labelled exploratory |
| CI overlap not used as a decision rule | **PASS** — Wilcoxon signed-rank primary, paired *t* secondary, BCa bootstrap CIs for effect sizes |
| Absolute effects reported with problem scale | **PASS** — every ratio accompanied by absolute difference and $\Delta/C_{\max}$ against the declared threshold |
| Baselines and ablations | Unmitigated baseline; ideal-noise reference; two contrasting noise regimes; legacy-vs-corrected ablation |
| Cost accounting complete | **PASS** — circuit, calibration, executions, wall-clock; offline scoring is exact and costs zero shots |
| No cells excluded on outcome | **PASS** — full grid executed; no exclusions |

**Weakness acknowledged, not fixed:** the composition arm was declared under-powered at the
practical threshold *in advance* (protocol §5) and remains so.

## Pass 3 — Claim audit

**Claims withdrawn during this work** (each was believed novel before the full texts were read):

| Withdrawn claim | Why | Prior art |
|---|---|---|
| Odd scale factors avoid partial folds | Already established | Majumdar *et al.*, IEEE QCE 2023, §II and Fig. 4 |
| Folding does not amplify SPAM/readout error | Already stated verbatim | Majumdar *et al.*, §V |
| Circuits should be transpiled before amplification | Already established | Majumdar *et al.*, §II ("Transpile first") |
| Shot budget governs which method wins | Already established | Bultrini *et al.*, Quantum 7, 1034 (2023) |
| Accuracy gains need not improve downstream decisions | Already claimed | Scavino, arXiv:2607.02888 |
| ZNE can show spurious apparent improvement | Already published | Köster & Mauerer, arXiv:2607.09360 (accepted, IEEE QCE 2026) |
| "Estimation-vs-optimisation ranking reversal" (v1 headline) | 75% of supporting runs used defective code | — **retracted** |

**Claims retained**, each with evidence in `CLAIM_EVIDENCE.csv`: the two measurement-mapping defects
and their regression tests; the quantified disagreement and best-method flip rate; the regret of
following the defective recommendation; the corrected budget-matched comparison; the 18.8%/75%
impact on the frozen study.

**Distinction from the closest related work is stated explicitly** in the paper (§II): Köster &
Mauerer's artefact is a statistical-regime collapse in a *correct* implementation; ours is a
correctness defect present at any depth and signal level.

**No mechanism claim is made.** The v1 "order-preservation" explanation was removed rather than
softened, because it was never tested.

## Pass 4 — Reproducibility

| Check | Result |
|---|---|
| Clean-room install from `requirements.txt` in a fresh venv | **PASS** — fresh `python3 -m venv`, installed from `requirements.txt` only (`logs/v2/cleanroom.log`) |
| `pip check` dependency consistency | **PASS** — "No broken requirements found." |
| Regression tests pass in the clean room | **PASS** — full suite green under the clean-room interpreter |
| All tables/figures regenerate from archived raw data | **PASS** — `analyze_main.py` → `make_tables.py` → `pdflatex`; no hand-entered numbers |
| Every inline number traceable | **PASS** — `tables/macros.tex` generated; `CLAIM_EVIDENCE.csv` maps claim → data → config → command → output |
| Determinism | **PASS** — named `SeedSequence` hierarchy; static calibration snapshots pinned by package version, not live device queries |
| `ply` pinned | **PASS** — missing from v1 requirements; without it the ZNE arm cannot run at all |

## Pass 5 — Presentation

Checked by rendering the PDF to images and inspecting each page, not by reading the log.

**Found and fixed:** Table V exceeded the column width and its values collided into Table VI
(promoted to a full-width `table*`); the title ran to four lines; budget `1500` rendered as "1k";
a figure legend sat on top of the data cloud; the abstract claimed "We release …" while §IX
correctly states the repository is private (a data-availability misstatement).

---

## Unresolved issues

1. **Literature search is bounded.** arXiv's API was rate-limited from this host, so no systematic
   arXiv sweep and no forward-citation analysis of Bultrini/Majumdar was performed. All
   "not previously studied" statements are bounded accordingly (`docs/novelty-matrix.md` §6).
2. **arXiv:2608.28535 full text not assessed.** If it contains a matched-budget ZNE-vs-REM
   comparison on QAOA, the secondary contribution weakens to a replication. The defect finding is
   unaffected.
3. **No in-loop (optimisation) result.** Out of scope at this compute budget; the paper claims nothing about it.
4. **Simulator-only, 6 qubits, $p=1$, IBM `cx`-native snapshots, one REM variant, global folding,
   Richardson only.** None of these are varied.
5. **Third-party libraries not audited.** We demonstrate the defect in one pipeline built on widely
   used components; we do **not** claim any released library is affected.
6. **Venue facts unverified** — deadline, page limit, fees, review model all recorded as UNKNOWN in
   `docs/venue-decision.md` and listed in `AUTHOR_ACTIONS.md`.
7. **No DOCX** — `pandoc` is absent from this environment.

## Publication-readiness assessment

The manuscript is **complete, internally consistent, and evidence-backed**, and the contribution is
**bounded and honestly scoped**: an implementation-correctness finding with regression tests and a
quantified impact, plus a corrected benchmark. It is *not* a new-method paper and does not claim to be.

**Publication readiness: plausible but unresolved.** The evidence supports the claims made, and the
contribution type has a demonstrated precedent at the target venue (Köster & Mauerer, IEEE QCE 2026).
Whether reviewers judge a correctness-and-replication result sufficiently novel is a judgement this
internal review cannot make, and the bounded literature search (item 1) is the single largest
residual risk. We do not assert acceptance probability.
