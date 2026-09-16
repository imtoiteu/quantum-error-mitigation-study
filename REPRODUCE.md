# Reproduction Instructions

**All results are simulator-only. No quantum hardware, no cloud account, no credentials required.**

## Environment

Verified on Linux x86_64, Python 3.12.3, 4 vCPU, 8 GB RAM.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt        # exact pins: requirements-lock.txt
```

`requirements-lock.txt` pins all 59 packages, including `ply`, which `mitiq` needs for its
Qiskit↔Cirq conversion but does not pull in automatically. Without it, folding raises
`ModuleNotFoundError` and the ZNE arm cannot run.

## Shared-machine policy

Every command below runs **one worker** with BLAS/OpenMP/Aer threads capped to 1 and reduced
priority. Peak RSS measured: **0.40 GB**. The main study is checkpointed — re-running the same
command resumes from `results/v2/raw/main_study.jsonl` and recomputes nothing.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
RUN="nice -n 15 .venv/bin/python"
```

## 1. Correctness tests — TWO oracles (seconds, no data needed)

```bash
$RUN tests/test_v2_correctness.py        # Oracle A: folding.  exit 0 = all pass
$RUN tests/test_rem_indexing.py          # Oracle B: REM indexing. exit 0 = all pass
```

**Oracle A** checks that odd-scale folding leaves the *exact* ideal probability vector unchanged
(compared as exact statevector probabilities, not sampled estimates), plus operator-level
equivalence, classical-register and measurement-map preservation, and that
`optimization_level=0` does not cancel folded pairs. Clifford circuits agree to the last bit;
with continuous rotations a constant ~1e-11 offset appears from floating-point angle
representation, measured constant at scales 3/5/9.

**Oracle B** is required because **Oracle A cannot detect the calibration defect**: it runs at zero
readout noise, where every response matrix is the identity and permuting identities is undetectable.
Oracle B uses unequal known response matrices and a non-identity measurement map, with an
independently computed reference. That blindness is itself asserted as a test.

## 1b. Positive control against the standard library

```bash
$RUN experiments/v2/positive_control_m3.py    # requires: pip install mthree
```
Runs M3 as documented (`mthree.utils.final_measurement_mapping`) and shows it agrees with the
corrected implementation on every layout. We do not claim any released library is defective.

## 2. Impact audit on the earlier frozen study (seconds)

```bash
$RUN experiments/v2/impact_audit.py
```
Recomputes the realised layout per condition and writes
`results/v2/processed/{layout_audit,stage_a_affected,stage_b_affected}.csv`.

## 3. Instance references (~2 min)

```bash
$RUN experiments/v2/pretrain_v2.py       # -> configs/v2/references.json
```
60 multistart exact-statevector optimisations per instance. Deterministic given the seed hierarchy.

## 4. Round-2 confirmation run (checkpointed, resumable)

```bash
$RUN experiments/v2/run_study.py --config configs/v2/confirm_round2.yaml
# optional batching on a busy machine:
$RUN experiments/v2/run_study.py --config configs/v2/confirm_round2.yaml --limit 500
```
5,040 cells in the fresh namespace `v2r2_confirm_2026_09_16`, with two independent evaluation
replicates per cell (replicate 0 selects, replicate 1 evaluates). Re-running the same command
resumes from the JSONL and recomputes nothing.

**Round-1 data** (`configs/v2/main_study.yaml`, namespace `v2_main_2026_09_16`) is retained for
reference but is a **single exploratory campaign**: its seed coordinates omitted instance, noise,
method and budget, so its "pilot" reproduced main-study values bit-for-bit. Do not treat any part of
it as confirming any other part.

## 5. Analysis, tables, figures, traceability

```bash
$RUN experiments/v2/analyze_round2.py       # -> results/v2r2/processed/, figures/figR2_*
$RUN experiments/v2/noise_scaling_audit.py  # -> supplementary/noise_scaling_audit.md
$RUN figures/src/make_pipeline_fig.py       # -> figures/fig0_pipeline.{pdf,png}
$RUN experiments/v2/make_tables_round2.py         # -> manuscript/tables/*.tex (incl. macros.tex)
$RUN experiments/v2/make_claim_evidence_round2.py # -> CLAIM_EVIDENCE.csv
```

## 6. Manuscript

```bash
cd manuscript
pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex
```

Every number in the PDF comes from `tables/*.tex`, which step 5 generates from raw data.
No numerical result is typed by hand anywhere in the manuscript source.

## Determinism

All randomness derives from `numpy.random.SeedSequence` with named roles
(`src/qemstudy/v2/seeding.py`, master entropy `20260916_0001`). Re-running any step reproduces
identical numbers. Device noise comes from static calibration snapshots pinned by the
`qiskit-ibm-runtime` version — not from live device queries.
