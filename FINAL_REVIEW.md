# Final Internal Review (round 2)

**Branch:** `review-round2` · **Frozen v1 snapshot:** `main` @ `2fee260` (untouched)
**Round-1 package:** `a5e3bc7` · **Date:** 2026-09-16 · **Simulator-only throughout.**

Five passes. Nothing is marked resolved without evidence in the repository. Items that remain
unresolved are listed in §6 and are not softened.

---

## Pass 1 — Scientific correctness

| Check | Result |
|---|---|
| Oracle A: odd-scale folding preserves the **exact** ideal probability vector | **PASS** — exact statevector comparison, four layouts, scales 3/5 |
| Clifford folding exact to the last bit | **PASS** — max\|dp\| = 0.0 at scales 3, 5, 9 |
| Rotation circuits: deviation characterised, not assumed | **PASS** — constant 1.04e-11 across scales 3/5/9 ⇒ floating-point angle representation, not accumulation. Tolerance justified by measurement |
| Operator-level equivalence of the folded core | **PASS** |
| Classical registers and measurement map preserved | **PASS** |
| Oracle B: REM indexing with **unequal** response matrices | **PASS** — aligned ~1e-16; misindexed up to 1.8e-1 |
| **Oracle A is blind to the calibration defect at p=0** | **PASS, asserted as a test** — the two oracles are not interchangeable |
| Readout channel actually applied | **PASS (was FAIL)** — 0.810000 = $(1-2p)^2$, previously a vacuous 1.000000 |
| Seed streams respond to every factor | **PASS** — 0 collisions over the realised coordinate set |
| Positive control vs `mthree` used as documented | **PASS** — agrees on all layouts, both exact to ~1e-16 |

**Found and fixed in this pass:** the readout audit computed on a circuit with the measurements
removed; the "exact" folding test estimated from 40,000 sampled shots; seed coordinates missing five
factors.

## Pass 2 — Experimental validity

| Check | Result |
|---|---|
| Realised total shots equal across methods | **PASS** — maximum relative deviation reported per budget |
| Calibration policy constant within comparisons | **PASS** |
| Pairing contract explicit and justified | **PASS** — `impl` excluded on purpose (common random numbers); every other factor independent |
| Fresh data independent of round 1 | **PASS** — new namespace, verified to produce different values for the same cell |
| Normalisation before averaging | **PASS** — per-instance $C_{\max}$ |
| Dependence respected | **PASS** — stratified bootstrap within six fixed instances; cluster bootstrap reported as the weaker generalisation interval |
| Bias and variance separated from differences of absolute errors | **PASS** |
| Winner scope named; near ties quantified | **PASS** |
| Decision regret uses an independent sample | **PASS** — replicate 0 selects, replicate 1 pays |
| No outcome-dependent exclusions | **PASS** — full grid, no cell dropped |

## Pass 3 — Claim audit

**Withdrawn in round 2** (in addition to the seven withdrawn in round 1):

| Withdrawn | Why |
|---|---|
| Round-1 "fresh independent confirmation" | 224/224 pilot rows bit-identical to main-study rows |
| "randomises rather than biases" | Our own data: \|signed\|/\|D\| = 0.98 and 0.99 for two arms |
| "at every depth, noise level and shot count" | Two explicit invisibility conditions now asserted as tests |
| Folding leaves readout noise "exactly invariant" at 1.0 | Vacuous computation; corrected to constant attenuation at 0.81 |
| "best attainable error" / "true regret" | Same-sample minima; replaced by split-sample regret |
| "retraction" framing | It was an unpublished internal pilot; now a short pilot-correction subsection |
| Physical-qubit-aware calibration as a novel insight | Established practice; `mthree` ships `final_measurement_mapping` |
| IEEE TQE as a natural easier fallback | Asserted without evidence in round 1; demoted |

**Retained**, each traced in `CLAIM_EVIDENCE.csv`: the two integration defects and their oracles;
the demonstrated non-interchangeability of the oracles; the measured implementation contrast with
instance-aware intervals; split-sample regret; the positive control.

**Contribution is stated as bounded** in the abstract and introduction: an integration-failure case
study plus a reusable validation artifact — explicitly *not* the discovery of an unknown hazard.

## Pass 4 — Reproducibility

| Check | Result |
|---|---|
| Clean-room install from `requirements.txt` | **PASS** (round 1, unchanged) — fresh venv, `pip check` clean, tests green |
| Fresh run launched from a clean committed tree | **PASS** — commit `c228cf4`, `git status` empty at launch |
| Execution-path content hashes recorded per row | **PASS** — 8 files hashed into every round-2 row |
| Round-1 provenance reconstructed, not relabelled | **PASS** — config hash still matches; all execution-path files byte-identical between `414fa51` and `830ebdc`; `git_dirty=True` stands |
| Tables and figures regenerate from archived raw data | **PASS** |
| No number typed by hand | **PASS** — all inline values via generated `macros.tex` |
| Determinism | **PASS** — named coordinate hierarchy, static calibration snapshots |

## Pass 5 — Presentation

Checked by rendering the PDF to images and inspecting each page.

**Found and fixed:** pipeline-diagram box overflow and an overlapping annotation; the diagram still
carried the prohibited phrase "a bug, at any noise level", now replaced by the two-oracle statement;
document class corrected to `[10pt,conference]` per the IEEE requirement.

---

## 6. Unresolved issues

1. **No target edition has an open call.** IEEE QCE 2026 closed 27 April 2026 and is running
   13–18 September 2026; IEEE QSW 2026 closed 22 March 2026; neither 2027 call is published.
   Page limit, template, deadline, review model and fees for any submittable edition are **UNKNOWN**.
   The manuscript was deliberately **not** padded to the closed edition's 8–10 page window.
2. **In-person attendance was mandatory at QCE 2026.** If that carries to 2027 and the author cannot
   travel, the venue decision changes materially. This is the most consequential author decision.
3. **Round-1 data cannot be repaired.** It is a single exploratory campaign with correlated streams
   and a dirty tree. No claim rests on it.
4. **Literature search remains bounded** — arXiv's API stayed rate-limited from this host, so no
   systematic sweep or forward-citation analysis was performed.
5. **Scope.** Six fixed instances, two device snapshots, $p=1$, six qubits, one REM variant, global
   folding, Richardson only. Generalisation is indicated only by the wider cluster interval.
6. **Third-party libraries not audited.** The positive control indicates `mthree` used as documented
   is unaffected; we make no claim about any other library.
7. **No DOCX** — `pandoc` is absent from this environment.

## 7. Publication-readiness assessment

**Unresolved, and more modestly so than in round 1.** The evidence now supports every claim made,
the artifact is reproducible from a clean environment, and the framing matches what the work actually
establishes. But the contribution is deliberately small: the hazard is documented, the standard
tooling already solves it, and the value rests on the validation oracles and the measured downstream
effect. Whether that clears the bar at a software-engineering venue is a judgement this process
cannot make, and **there is currently no open call to submit to**, which is a practical blocker
independent of merit.
