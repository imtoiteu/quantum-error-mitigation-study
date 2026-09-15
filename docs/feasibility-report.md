# Feasibility Report (Phase 2)

**Compiled:** 2026-09-15 · All figures below are **measured on this machine**, not estimated from
documentation.

---

## 1. Environment

| Item | Value | How verified |
|---|---|---|
| OS | Linux 6.8.0-139-generic, x86_64 | `uname` |
| Python | **3.12.3** (CPython, `/usr/bin/python3`) | `python3 --version` |
| CPU | 4 vCPU AMD EPYC (i440fx guest) @ 2.0 GHz, 1 thread/core | `nproc`, `lscpu` |
| RAM | 7 GB total, **~1 GB free at session start** | `free -g` |
| Disk | 23 GB free on `/` | `df -h` |
| Network | PyPI and arxiv.org reachable | live fetch |

**Pre-existing quantum stack: none.** Only `numpy 2.5.2` and `matplotlib 3.11.1` were installed.
A dedicated virtualenv `.venv/` was created and the stack installed into it.

### 1.1 Installed and verified

```
qiskit            2.5.2
qiskit-aer        0.17.2
qiskit-ibm-runtime 0.42.0
mitiq             1.1.0
numpy             2.2.6      (venv; note: differs from the system numpy 2.5.2)
scipy             1.17.1
networkx, pandas, matplotlib, PyYAML
```

Exact transitive pins: `requirements-lock.txt` (58 packages). Direct deps: `requirements.txt`.

> **Install note worth recording:** the first install attempt pinned `mitiq==0.51.0`, which does not
> exist — mitiq's published versions jump from 0.49.0 to 1.0.0. The correct current release is
> **1.1.0**. Additionally, a `pip ... | tail` pipeline masked the failure behind exit code 0; the
> install script now uses `set -o pipefail`. Both are reproducibility hazards worth noting.

---

## 2. Framework decision: **Qiskit** (not PennyLane)

Chosen: **Qiskit + Qiskit Aer + Mitiq.** Reasons, in order of weight:

1. **Realistic noise models are a first-class feature.** `NoiseModel.from_backend()` builds a noise model directly from a shipped IBM device calibration snapshot (gate errors, T1/T2, readout error, per-qubit). This satisfies the "at least two realistic noise models" requirement with *real device calibration data* rather than hand-tuned parameters. PennyLane has no equivalent native path; its realistic-noise story routes through `pennylane-qiskit`, i.e. back to Aer anyway — adding a translation layer and a version-compatibility risk for no gain.
2. **The reference ZNE implementation targets Qiskit.** Mitiq is the software artifact of Giurgica-Tiron *et al.* (IEEE QCE 2020), the paper that defines the digital unitary folding we use. Using it removes a whole class of "did you implement ZNE correctly?" reviewer objections.
3. **Reviewer familiarity at the target venues.** The closest comparable papers — Russo *et al.* (IEEE TQE 2023), Majumdar *et al.* (IEEE QCE 2023), Pelofske *et al.* (ACM TQC 2024) — all use the Qiskit/Mitiq stack. Matching it makes the artifact easier to review and reuse.
4. **We do not need PennyLane's main advantage.** PennyLane's differentiating strength is automatic differentiation and hybrid ML integration. Our optimiser is **SPSA** (gradient-free, chosen because analytic gradients are not available under a noisy shot-based objective anyway), so autodiff buys nothing here.
5. **Readout mitigation tooling.** Calibration-matrix construction and the M3 approach (Nation *et al.* 2021) are native to the Qiskit ecosystem.

**Cost of this choice, stated honestly:** results become somewhat IBM-flavoured (superconducting,
`cx`/`ecr` native gates, IBM readout characteristics). A trapped-ion or neutral-atom noise regime is
not represented. This is recorded as a threat to external validity.

---

## 3. Measured device-noise characteristics (drove the noise-model selection)

Median error rates extracted from each candidate backend's `Target`:

| Backend | qubits | 1q err | 2q err | **readout err** | T1 | T2 | native 2q |
|---|---|---|---|---|---|---|---|
| `fake_manila` | 5 | 2.1e-04 | 1.01e-02 | 0.0219 | 145 µs | 54 µs | cx |
| **`fake_lagos`** | **7** | 2.5e-04 | 1.05e-02 | **0.1690** | 105 µs | 72 µs | **cx** |
| `fake_cairo` | 27 | 2.0e-04 | 9.65e-03 | 0.0139 | 97 µs | 81 µs | cx, ecr |
| **`fake_algiers`** | **27** | 2.2e-04 | 7.94e-03 | **0.0109** | 135 µs | 87 µs | **cx** |
| `fake_kyiv` | 127 | 1.8e-04 | 1.17e-02 | 0.0127 | 287 µs | 118 µs | ecr |
| `fake_torino` | 133 | 2.2e-04 | 4.19e-03 | 0.0229 | 185 µs | 141 µs | cz |
| `fake_sherbrooke` | 127 | 1.9e-04 | 7.79e-03 | 0.0198 | 278 µs | 170 µs | ecr |

**Selected: `fake_lagos` and `fake_algiers`.** They differ by **~15×** in readout error (0.169 vs
0.011) while having near-identical two-qubit gate error, and both are `cx`-native with ≥ 7 qubits.
This makes them a readout-dominated / gate-dominated contrast that directly discriminates between
readout mitigation and gate-error mitigation — the central comparison of RQ1. Had we picked by
reputation (e.g. "newest device"), we would have chosen `fake_kyiv` + `fake_torino`, which differ in
native gate (`ecr` vs `cz`), confounding unitary folding.

---

## 4. Measured throughput

Hardware-efficient ansatz, `reps=2`, transpiled at `optimization_level=1`:

| qubits | noise | transpiled depth | 1024 shots | 4096 shots |
|---|---|---|---|---|
| 4 | ideal | 9 | 30 ms | 6 ms |
| 4 | `fake_manila` | 18 | 262 ms | 97 ms |
| 4 | `fake_algiers` | 18 | 362 ms | 411 ms |
| 6 | ideal | 11 | 22 ms | 46 ms |
| 6 | `fake_algiers` | 20 | 514 ms | 397 ms |
| 8 | ideal | 13 | 9 ms | 11 ms |
| 8 | `fake_algiers` | 22 | 619 ms | 426 ms |

**Peak RSS: 0.24 GB.** Two findings that matter for the design:

- **Runtime is dominated by per-circuit setup, not shot count.** Going from 1024 to 4096 shots barely changes wall-clock (sometimes reduces it, within noise). Consequence: **large shot budgets are nearly free; the number of distinct circuit executions is the real cost driver.** This is exactly the quantity mitigation overhead multiplies, so the cost model in `docs/pilot-protocol.md` §4 counts circuit executions as well as shots.
- **Memory is a non-issue.** 0.24 GB peak against ~1 GB free. Density-matrix simulation is not needed; Aer's noisy trajectory sampling at 4–6 qubits is trivial. The earlier RAM concern does not bind.

Budget assumption for planning: **~0.4 s per noisy circuit execution**, 4-way process parallelism.

---

## 5. Resource estimate for the pilot

| Stage | Conditions | Circuit executions | Serial est. | 4-core est. |
|---|---|---|---|---|
| A — estimation accuracy | 2 tasks × 6 noise × 5 budgets × 4 methods × 10 seeds = 2400 | ~19 200 | ~128 min | **~32 min** |
| B — in-loop optimisation | 2 tasks × 2 noise × 4 methods × 5 seeds = 80 runs × 80 evals | ~19 200 | ~128 min | **~32 min** |
| C — exploratory (EQ4 extra) | ZNE fit variants | ~2 000 | ~13 min | **~4 min** |
| **Total** | | **~40 000** | ~4.5 h | **≈ 68 min** |

Against the 2-hour budget this leaves ~50 minutes of headroom, which absorbs transpilation overhead,
analysis, and one full re-run if a bug is found. The pre-registered trim rule
(`docs/pilot-protocol.md` §8) reduces the budget sweep if Stage A exceeds 75 minutes.

**Cloud hardware is NOT required and NOT used.** The user confirmed simulator-only scope. Every
result will be labelled simulator-only. The code keeps a clean backend seam so a hardware arm could
be added later without redesign, but no such claim is made.

---

## 6. Feasibility verdict

**Feasible.** Every technical precondition is satisfied and measured:

- ✅ Stack installs and imports on Python 3.12.3
- ✅ Device calibration snapshots load and expose the error rates we need
- ✅ Two qualitatively distinct, `cx`-native realistic noise models identified by measurement
- ✅ Mitiq ZNE factories available (`LinearFactory`, `RichardsonFactory`, `ExpFactory`, …)
- ✅ Throughput and memory comfortably within budget
- ✅ Classical references are exact and cheap for both tasks

**The binding risk is scientific, not computational:** whether the effect is large enough to resolve
above seed-to-seed variance at this scale. That is precisely what the pilot is designed to find out,
and kill criterion K3 covers the negative outcome.
