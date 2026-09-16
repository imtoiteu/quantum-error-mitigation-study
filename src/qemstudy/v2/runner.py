"""v2 execution: corrected mapping, validated scaling, explicit accounting.

Fixes relative to v1
--------------------
A1  prepare() pins initial_layout and records the clbit->physical map; folding
    re-attaches the original measurements; REM calibrates the physical qubits
    each clbit actually reads.
A2  scale factors default to ODD integers so every error-carrying gate is folded
    a whole number of times (validated in tests/test_v2_correctness.py).
A3  all randomness comes from the named SeedSequence hierarchy in seeding.py.
A5  shots are accounted in separate categories (circuit / calibration) and the
    calibration policy is an explicit, recorded parameter rather than an implicit
    difference between stages.
"""
from __future__ import annotations
import os, time
from dataclasses import dataclass, field

# Cap BLAS/OpenMP before numpy/Aer import in worker processes (shared VPS policy D).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
from qiskit_aer import AerSimulator
from mitiq.zne.inference import RichardsonFactory, LinearFactory, ExpFactory

from ..noise import NoiseSpec
from .circuits import (prepare, fold_preserving_measurements, to_basis,
                       calibration_circuits, legacy_fold, legacy_calibration_circuits)
from .rem import build_confusion, apply_rem
from .seeding import int_seed

ODD_SCALES = (1.0, 3.0, 5.0)
FACTORIES = {"richardson": RichardsonFactory, "linear": LinearFactory, "exp": ExpFactory}


@dataclass
class Cost:
    circuit_shots: int = 0
    calibration_shots: int = 0
    circuit_executions: int = 0
    calibration_executions: int = 0
    wall_clock_s: float = 0.0

    @property
    def total_shots(self) -> int:
        return self.circuit_shots + self.calibration_shots

    def asdict(self):
        return dict(circuit_shots=self.circuit_shots, calibration_shots=self.calibration_shots,
                    total_shots=self.total_shots, circuit_executions=self.circuit_executions,
                    calibration_executions=self.calibration_executions,
                    wall_clock_s=round(self.wall_clock_s, 4))


@dataclass
class Executor:
    noise: NoiseSpec
    n: int
    run_id: int = 0
    max_parallel: int = 1

    def __post_init__(self):
        self.noise_model = self.noise.build()
        backend = self.noise.coupling_backend()
        if backend is not None:
            edges = [tuple(e) for e in backend.coupling_map.get_edges()]
            sub = sorted({tuple(sorted(e)) for e in edges if e[0] < self.n and e[1] < self.n})
            self.coupling_map = [list(e) for e in sub] + [list(reversed(e)) for e in sub]
        else:
            self.coupling_map = None
        self.cost = Cost()
        self._prep_cache: dict = {}

    def prepare(self, qc, tag: str):
        if tag not in self._prep_cache:
            self._prep_cache[tag] = prepare(qc, self.coupling_map, self.n,
                                            int_seed("transpiler", self.run_id))
        return self._prep_cache[tag]

    def run(self, circuits, shots: int, *, role: str, coords: tuple, calibration=False):
        if shots <= 0:
            return [{} for _ in circuits]
        sim = AerSimulator(noise_model=self.noise_model,
                           seed_simulator=int_seed(role, *coords),
                           max_parallel_threads=self.max_parallel,
                           max_parallel_experiments=1)
        res = sim.run(list(circuits), shots=shots).result()
        if calibration:
            self.cost.calibration_shots += shots * len(circuits)
            self.cost.calibration_executions += len(circuits)
        else:
            self.cost.circuit_shots += shots * len(circuits)
            self.cost.circuit_executions += len(circuits)
        return [dict(res.get_counts(i)) for i in range(len(circuits))]


def extrapolate(scales, values, fit="richardson"):
    fac = ExpFactory(list(scales), asymptote=None) if fit == "exp" else FACTORIES[fit](list(scales))
    for s, v in zip(scales, values):
        fac.push({"scale_factor": s}, v)
    return float(fac.reduce())


def calibrate(ex: Executor, prep, shots_total: int, eval_id: int, legacy: bool = False):
    """Measure per-clbit confusion matrices aligned to prep.clbit_to_phys.

    legacy=True reproduces the v1 defect A1c: calibration on VIRTUAL indices,
    ignoring the layout, so the confusion matrix is applied to the wrong qubits.
    """
    cals = (legacy_calibration_circuits(prep.circuit.num_clbits)
            if legacy else
            calibration_circuits(prep.clbit_to_phys, prep.circuit.num_qubits, prep.circuit.num_clbits))
    per = max(shots_total // len(cals), 1)
    counts = ex.run(cals, per, role="calibration", coords=(ex.run_id, eval_id), calibration=True)
    return build_confusion(counts, prep.clbit_to_phys, prep.circuit.num_clbits)


def estimate(ex: Executor, circuits: dict, combine, method: str, budget: int, *,
             eval_id: int = 0, scales=ODD_SCALES, fit="richardson",
             confusion=None, cal_fraction: float = 0.20, clip: bool = True,
             legacy_mapping: bool = False):
    """One budget-matched objective estimate. `budget` = TOTAL shots across bases."""
    t0 = time.perf_counter()
    c0 = ex.cost.asdict()
    bases = list(circuits)
    preps = {b: ex.prepare(circuits[b], f"{b}") for b in bases}
    nb = len(bases)
    use_rem = method in ("rem", "zne_rem")
    use_zne = method in ("zne", "zne_rem")
    detail = {"bases": nb, "scales": list(scales) if use_zne else [1.0],
              "legacy_mapping": bool(legacy_mapping),
              "clbit_to_phys": {b: list(preps[b].clbit_to_phys) for b in bases},
              "initial_layout": {b: preps[b].initial_layout for b in bases},
              "routing_permutation": {b: preps[b].routing_permutation for b in bases}}

    mats, circuit_budget = confusion, budget
    if use_rem and mats is None:
        cal_total = int(round(cal_fraction * budget))
        mats = calibrate(ex, preps[bases[0]], cal_total, eval_id, legacy=legacy_mapping)
        circuit_budget = budget - cal_total
        detail["calibration_policy"] = "per_estimate"
    elif use_rem:
        detail["calibration_policy"] = "reused"

    rem_diag = None
    if not use_zne:
        per = max(circuit_budget // nb, 1)
        vals = {}
        for bi, b in enumerate(bases):
            cnt = ex.run([preps[b].circuit], per, role="simulator",
                         coords=(ex.run_id, eval_id, bi, 0))[0]
            if use_rem:
                cnt, rem_diag = apply_rem(cnt, mats, preps[b].circuit.num_clbits, clip=clip)
            vals[b] = cnt
        value = combine(vals)
        detail["shots_per_basis"] = per
    else:
        k = len(scales)
        per = max(circuit_budget // (nb * k), 1)
        svals, gate_counts = [], {}
        for si, s in enumerate(scales):
            vals = {}
            for bi, b in enumerate(bases):
                folder = legacy_fold if legacy_mapping else fold_preserving_measurements
                fc = to_basis(folder(preps[b].circuit, s),
                              int_seed("transpiler", ex.run_id, si))
                ops = fc.count_ops()
                gate_counts[f"{b}@{s}"] = {g: int(ops.get(g, 0)) for g in ("cx", "sx", "x")}
                cnt = ex.run([fc], per, role="simulator", coords=(ex.run_id, eval_id, bi, si))[0]
                if use_rem:
                    cnt, rem_diag = apply_rem(cnt, mats, fc.num_clbits, clip=clip)
                vals[b] = cnt
            svals.append(combine(vals))
        value = extrapolate(scales, svals, fit)
        detail.update(shots_per_cell=per, scaled_values=svals,
                      gate_counts_per_scale=gate_counts, fit=fit)

    if rem_diag is not None:
        detail["rem_negative_mass"] = rem_diag.negative_mass
        detail["rem_cond_number"] = rem_diag.cond_number
        detail["rem_min_diag"] = rem_diag.min_diag
    c1 = ex.cost.asdict()
    detail["cost_delta"] = {k: c1[k] - c0[k] for k in c1 if isinstance(c1[k], (int, float))}
    detail["wall_clock_s"] = time.perf_counter() - t0
    return float(value), detail, mats
