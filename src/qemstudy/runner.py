"""Execution backend and the four mitigation arms, with strict budget accounting.

CRITICAL correctness note (verified empirically, see docs/feasibility-report.md S7):
unitary folding MUST be applied to an already-transpiled circuit, and the folded
circuit must then be re-transpiled at optimization_level=0 ONLY.

  * Folding before transpilation, or re-transpiling at optimization_level>=1,
    causes the transpiler to cancel the folded inverse pairs. Measured: a 3x-folded
    4-qubit circuit collapsed from depth 34 / 9 cx back to depth 12 / 3 cx --
    i.e. ZNE silently becomes a no-op and the extrapolation fits pure noise.
  * Folding emits `sxdg`, which is not in the IBM basis. Left untranslated it would
    receive NO noise from the device noise model, again defeating ZNE.

optimization_level=0 performs basis translation without cancellation.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from .noise import NoiseSpec
from .mitigation import (MitigationResult, SCALE_FACTORS, CAL_FRACTION,
                         estimate_confusion, apply_rem, extrapolate, fold)


@dataclass
class Executor:
    """Owns the simulator, the transpilation contract, and shot bookkeeping."""
    noise: NoiseSpec
    n: int
    seed: int = 0
    _basis: list[str] = field(default_factory=lambda: ["sx", "x", "rz", "cx"])

    def __post_init__(self):
        self.noise_model = self.noise.build()
        self.sim = AerSimulator(noise_model=self.noise_model, seed_simulator=self.seed)
        backend = self.noise.coupling_backend()
        if backend is not None:
            edges = [tuple(e) for e in backend.coupling_map.get_edges()]
            sub = sorted({tuple(sorted(e)) for e in edges if e[0] < self.n and e[1] < self.n})
            self.coupling_map = [list(e) for e in sub] + [list(reversed(e)) for e in sub]
        else:
            self.coupling_map = None       # ideal / param: all-to-all
        self.shots_used = 0
        self.circuit_executions = 0

    # -- transpilation contract -------------------------------------------
    def prepare(self, qc: QuantumCircuit) -> QuantumCircuit:
        return transpile(qc, basis_gates=self._basis, coupling_map=self.coupling_map,
                         optimization_level=1, seed_transpiler=self.seed)

    def _to_basis(self, qc: QuantumCircuit) -> QuantumCircuit:
        # opt level 0: basis translation only -- must NOT cancel folded pairs.
        return transpile(qc, basis_gates=self._basis, optimization_level=0,
                         seed_transpiler=self.seed)

    def run(self, circuits, shots: int, seed: int | None = None):
        if shots <= 0:
            return [{} for _ in circuits]
        sim = self.sim if seed is None else AerSimulator(
            noise_model=self.noise_model, seed_simulator=seed)
        res = sim.run(list(circuits), shots=shots).result()
        self.shots_used += shots * len(circuits)
        self.circuit_executions += len(circuits)
        out = []
        for i in range(len(circuits)):
            c = res.get_counts(i)
            out.append(c if isinstance(c, dict) else dict(c))
        return out


def estimate(executor: Executor, circuits: dict[str, QuantumCircuit],
             combine, method: str, budget: int, seed: int,
             fit: str = "richardson", confusion=None) -> MitigationResult:
    """Evaluate the objective under one mitigation arm at a fixed TOTAL budget.

    `budget` is the total shots per objective evaluation, shared across all
    measurement bases. `combine` maps {basis: counts} -> float.
    """
    t0 = time.perf_counter()
    bases = list(circuits)
    nb = len(bases)
    prepared = {b: executor.prepare(circuits[b]) for b in bases}
    start_shots, start_exec = executor.shots_used, executor.circuit_executions
    detail: dict = {"bases": nb}

    use_rem = method in ("rem", "zne_rem")
    use_zne = method in ("zne", "zne_rem")

    # ---- readout calibration (measured, charged against the budget) -------
    mats = confusion
    if use_rem and mats is None:
        cal_total = int(round(CAL_FRACTION * budget))
        per_cal = max(cal_total // (2 * executor.n), 1)
        mats, _, _ = estimate_confusion(
            executor.n, lambda cs, s, sd: executor.run(cs, s, sd), per_cal, seed + 9973)
        detail["cal_shots_per_circuit"] = per_cal
    circuit_budget = budget - int(round(CAL_FRACTION * budget)) if use_rem else budget

    # ---- main circuits ----------------------------------------------------
    if not use_zne:
        per_basis = max(circuit_budget // nb, 1)
        vals = {}
        for b in bases:
            counts = executor.run([prepared[b]], per_basis, seed)[0]
            vals[b] = apply_rem(counts, mats, executor.n) if use_rem else counts
        value = combine(vals)
        detail["shots_per_basis"] = per_basis
    else:
        k = len(SCALE_FACTORS)
        per_cell = max(circuit_budget // (nb * k), 1)
        scaled_vals, cx_counts = [], {}
        for s in SCALE_FACTORS:
            vals = {}
            for b in bases:
                folded = executor._to_basis(fold(prepared[b], s))
                cx_counts[f"{b}@{s}"] = folded.count_ops().get("cx", 0)
                counts = executor.run([folded], per_cell, seed)[0]
                vals[b] = apply_rem(counts, mats, executor.n) if use_rem else counts
            scaled_vals.append(combine(vals))
        value = extrapolate(SCALE_FACTORS, scaled_vals, fit)
        detail.update(shots_per_cell=per_cell, scaled_values=scaled_vals,
                      cx_per_scale=cx_counts, fit=fit)

    return MitigationResult(
        value=float(value),
        shots_used=executor.shots_used - start_shots,
        circuit_executions=executor.circuit_executions - start_exec,
        detail={**detail, "wall_clock_s": time.perf_counter() - t0},
    )
