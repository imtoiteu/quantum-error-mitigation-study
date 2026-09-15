# Error Mitigation for Variational Quantum Algorithms under Realistic Noise

**A reproducible empirical pilot study — feasibility stage.**

> **Status: pilot / feasibility study. Not a finished paper.**
> **All results in this repository are SIMULATOR-ONLY. No quantum hardware was used.**
> No claim of quantum advantage is made anywhere in this work, and the study is not
> designed to support one.

## What this is

A budget-matched empirical comparison of quantum error-mitigation methods on two small
variational quantum algorithms under realistic noise. The central methodological commitment:

> **Every mitigation method is given exactly the same total shot budget per objective
> evaluation.** Zero-noise extrapolation costs 3× the circuit executions of no mitigation, so
> comparing them at equal shots-per-circuit hides that cost. Here, a method that needs 3×
> the executions gets ⅓ the shots each.

## Research questions

| | Question |
|---|---|
| **RQ1** | Does mitigation still help when *total* shot cost is held constant? |
| **RQ2** | Where is the shot-budget crossover, and does it differ between methods? |
| **RQ3** | Does the estimation-stage verdict transfer to the full optimisation loop? |

Full statements, hypotheses and pre-registered decision rules: [`docs/research-questions.md`](docs/research-questions.md).

## Experimental design

| Axis | Values |
|---|---|
| **Tasks** | TFIM VQE (4 qubits, exact reference by diagonalisation) · MaxCut QAOA (6 qubits, prism graph, exact reference by enumeration) |
| **Noise** | ideal · `dev_lagos` (readout-dominated, 16.9% median readout error) · `dev_algiers` (gate-dominated, 1.1%) · parametric model at λ ∈ {0.5, 1.0, 2.0} |
| **Mitigation** | none · ZNE (global folding, Richardson) · REM (measured confusion matrix) · ZNE+REM |
| **Budgets** | 1 500 · 3 000 · 6 000 · 12 000 · 24 000 total shots per estimate |
| **Seeds** | 10 (Stage A), 5 (Stage B) — fixed in config before running |

The two device noise models were **chosen by measuring** candidate backends' error rates, not by
reputation: they differ ~15× in readout error while sharing near-identical two-qubit gate error and
the same native `cx` gate. See [`docs/feasibility-report.md`](docs/feasibility-report.md) §3.

## Repository layout

```
docs/          literature survey, venue survey, gap analysis, research questions,
               pilot protocol, feasibility report
src/qemstudy/  problems.py  -- tasks + exact classical references
               noise.py     -- ideal / device-snapshot / parametric noise models
               mitigation.py-- ZNE folding, extrapolation, readout calibration + inversion
               runner.py    -- execution + strict shot accounting
experiments/   pretrain.py  -- Stage 0: ideal-simulator parameter pre-optimisation
               stage_a.py   -- Stage A: estimation accuracy at matched budget
               stage_b.py   -- Stage B: in-loop optimisation
               analyze.py   -- summaries, bootstrap CIs, verdicts, figures
configs/       frozen experiment configs + pre-trained parameters
results/raw/   one JSON object per experimental cell (version-controlled)
results/processed/ summary CSVs and verdict tables
figures/       generated figures
```

## Reproducing

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # exact pins in requirements-lock.txt

.venv/bin/python experiments/pretrain.py    # Stage 0 -> configs/pretrained_params.json
.venv/bin/python experiments/stage_a.py     # Stage A -> results/raw/stage_a.jsonl
.venv/bin/python experiments/stage_b.py     # Stage B -> results/raw/stage_b.jsonl
.venv/bin/python experiments/analyze.py     # -> results/processed/, figures/
```

Environment used: Python 3.12.3, qiskit 2.5.2, qiskit-aer 0.17.2, mitiq 1.1.0,
4 vCPU AMD EPYC. Every result row carries its git commit, config hash, and package versions.

## A correctness trap worth knowing

Unitary folding must be applied to an **already-transpiled** circuit, and the folded circuit
re-transpiled at `optimization_level=0` **only**. Measured on this codebase: re-transpiling a
3×-folded circuit at `optimization_level=1` collapsed it from depth 34 / 9 CX back to depth 12 /
3 CX — the transpiler cancels the folded inverse pairs and **ZNE silently becomes a no-op**.
Folding also emits `sxdg`, which is outside the IBM basis and would otherwise receive no noise.
See the module docstring in [`src/qemstudy/runner.py`](src/qemstudy/runner.py).

## Scientific commitments

- No quantum-advantage claim.
- No comparison at unequal shot budgets without reporting it; an automated check asserts budget equality and its result is printed in the verdicts file.
- Multiple noise levels and multiple noise models, never a single one.
- All runs reported — no best-run selection. Aggregates are mean ± 95% bootstrap CI over seeds.
- Exploratory results are reported separately from confirmatory ones.
- All settings in version-controlled config files; seeds fixed before running.
- Simulator results are labelled as such everywhere.

## Handoff

[`HANDOFF.md`](HANDOFF.md) carries the research questions, gap evidence, target venues, exact
commands, pilot results including negative results, reproducibility information, threats to
validity, and the go/no-go recommendation.
