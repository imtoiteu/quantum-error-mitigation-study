"""Exact, shot-free scoring for offline simulator-only evaluation (review finding A4).

v1 scored final parameters with a 200,000-shot 'ideal' run, injecting ~6e-4 of
shot noise into the reported optimisation gap. Offline we can evaluate the
noiseless objective exactly from the statevector, so we do.

Three quantities are kept DISTINCT and never conflated:
  estimation_error : |estimate - exact noiseless value at the SAME parameters|
  optimisation_gap : signed (exact value at found params) - (best-known ansatz ref)
  gap_to_optimum   : signed (exact value at found params) - (exact combinatorial optimum)
The ansatz reference is a MULTISTART NUMERICAL best-known value, NOT a proven
global optimum of the ansatz; it is labelled as such everywhere.
"""
from __future__ import annotations
import numpy as np
from qiskit.quantum_info import Statevector


def exact_cut_value(problem, params) -> float:
    qc = problem.measured_circuits(np.asarray(params, float))["z"].remove_final_measurements(inplace=False)
    probs = np.abs(Statevector.from_instruction(qc).data) ** 2
    n, edges = problem.n, problem.edges
    idx = np.arange(probs.size)
    bits = ((idx[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)   # bits[:, q] = qubit q
    cuts = sum((bits[:, i] != bits[:, j]).astype(float) for i, j in edges)
    return float(np.dot(probs, cuts))


def score(problem, params, ansatz_reference: float, exact_optimum: float) -> dict:
    v = exact_cut_value(problem, params)
    return {"exact_value": v,
            "optimisation_gap_signed": v - ansatz_reference,
            "gap_to_optimum_signed": v - exact_optimum,
            "approx_ratio": v / exact_optimum}
