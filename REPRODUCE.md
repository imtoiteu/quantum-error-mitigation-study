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

## 1. Correctness tests (seconds, no data needed)

```bash
$RUN tests/test_v2_correctness.py        # exit 0 = all pass
```
Checks the folding oracle (odd-scale folding must leave the ideal distribution unchanged),
exact ⟨Z_q⟩ invariance, operator-level equivalence, classical-register and measurement-map
preservation, calibration alignment, and that `optimization_level=0` does not cancel folded pairs.

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

## 4. Main study (checkpointed, resumable)

```bash
$RUN experiments/v2/run_study.py --config configs/v2/main_study.yaml
# optional batching on a busy machine:
$RUN experiments/v2/run_study.py --config configs/v2/main_study.yaml --limit 500
```
7,560 cells. Measured wall-clock on a contended 4-vCPU VPS: roughly 3 hours at `nice -n 15`.

## 5. Analysis, tables, figures, traceability

```bash
$RUN experiments/v2/analyze_main.py         # -> results/v2/processed/, figures/fig1-3
$RUN experiments/v2/noise_scaling_audit.py  # -> supplementary/noise_scaling_audit.md
$RUN figures/src/make_pipeline_fig.py       # -> figures/fig0_pipeline.{pdf,png}
$RUN experiments/v2/make_tables.py          # -> manuscript/tables/*.tex (incl. macros.tex)
$RUN experiments/v2/make_claim_evidence.py  # -> CLAIM_EVIDENCE.csv
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
