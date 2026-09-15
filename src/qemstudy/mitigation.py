"""Mitigation arms with explicit, auditable shot accounting.

Every arm consumes the SAME total shot budget B per objective evaluation.
Each returns a MitigationResult carrying shots_used and circuit_executions so
that budget matching can be asserted after the fact rather than assumed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Sequence
import numpy as np
from qiskit import QuantumCircuit
from mitiq.zne.scaling import fold_global
from mitiq.zne.inference import RichardsonFactory, LinearFactory, ExpFactory

SCALE_FACTORS = (1.0, 2.0, 3.0)
CAL_FRACTION = 0.20          # fraction of B spent on readout calibration


@dataclass
class MitigationResult:
    value: float
    shots_used: int = 0
    circuit_executions: int = 0
    detail: dict = field(default_factory=dict)


# ---------------------------------------------------------------- readout calibration

def calibration_circuits(n: int) -> list[QuantumCircuit]:
    """2n circuits preparing |0> and |1> on each qubit (all others |0>)."""
    out = []
    for q in range(n):
        for bit in (0, 1):
            qc = QuantumCircuit(n)
            if bit:
                qc.x(q)
            qc.measure_all()
            out.append(qc)
    return out


def estimate_confusion(n: int, run: Callable, shots_per_circuit: int, seed: int):
    """Per-qubit 2x2 confusion matrices, MEASURED from calibration circuits.

    Deliberately does not read the ground-truth readout error out of the noise
    model: that would make the REM arm unfairly informed.
    """
    circs = calibration_circuits(n)
    counts_list = run(circs, shots_per_circuit, seed)
    mats = np.zeros((n, 2, 2))
    for idx, counts in enumerate(counts_list):
        q, prepared = idx // 2, idx % 2
        tot = sum(counts.values()) or 1
        p1 = sum(c for b, c in counts.items()
                 if int(b.replace(" ", "")[n - 1 - q]) == 1) / tot
        mats[q, 1, prepared] = p1
        mats[q, 0, prepared] = 1.0 - p1
    execs = len(circs)
    return mats, execs * shots_per_circuit, execs


def apply_rem(counts: dict[str, int], mats: np.ndarray, n: int) -> dict[str, float]:
    """Invert the tensored confusion matrix, then clip and renormalise."""
    dim = 2 ** n
    vec = np.zeros(dim)
    total = sum(counts.values()) or 1
    for b, c in counts.items():
        vec[int(b.replace(" ", ""), 2)] = c / total
    A = np.array([[1.0]])
    for q in range(n - 1, -1, -1):          # qubit 0 least significant
        A = np.kron(A, mats[q])
    try:
        corrected = np.linalg.solve(A, vec)
    except np.linalg.LinAlgError:
        corrected = np.linalg.pinv(A) @ vec
    corrected = np.clip(corrected, 0.0, None)
    s = corrected.sum()
    corrected = corrected / s if s > 0 else vec
    return {format(i, f"0{n}b"): corrected[i] * total
            for i in range(dim) if corrected[i] > 0}


FACTORIES = {"richardson": RichardsonFactory, "linear": LinearFactory, "exp": ExpFactory}


def extrapolate(scale_factors: Sequence[float], values: Sequence[float],
                fit: str = "richardson") -> float:
    if fit == "exp":
        fac = ExpFactory(list(scale_factors), asymptote=None)
    else:
        fac = FACTORIES[fit](list(scale_factors))
    for s, v in zip(scale_factors, values):
        fac.push({"scale_factor": s}, v)
    return float(fac.reduce())


def fold(circuit: QuantumCircuit, scale: float) -> QuantumCircuit:
    """Global unitary folding, preserving the terminal measurements."""
    if scale == 1.0:
        return circuit
    stripped = circuit.remove_final_measurements(inplace=False)
    folded = fold_global(stripped, scale)
    out = QuantumCircuit(circuit.num_qubits)
    out.compose(folded, inplace=True)
    out.measure_all()
    return out
