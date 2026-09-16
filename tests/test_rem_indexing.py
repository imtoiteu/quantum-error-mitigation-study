r"""Deterministic REM-indexing oracle (review finding 4).

WHY A SEPARATE ORACLE IS NEEDED
-------------------------------
The folding-invariance oracle ($U U^{\dagger} U = U$ leaves the ideal distribution
unchanged) cannot detect a misindexed readout-mitigation matrix, because it is run at
ZERO readout noise, where every per-qubit response matrix is the identity and any
permutation of them is also the identity. The two defects therefore need two
independent oracles.

THIS ORACLE
-----------
  * a non-identity measurement map (clbit c reads physical qubit pi(c));
  * UNEQUAL, known per-qubit response matrices, so permuting them is detectable;
  * an independently computed reference: the exact ideal distribution from the
    statevector, and the exact measured distribution p_meas = A_true p_ideal
    obtained by explicit matrix multiplication rather than by sampling.

Correct (physical-qubit-aware) calibration must recover p_ideal to machine precision.
Virtual-index calibration must not.

No sampling anywhere; every number is exact.
"""
from __future__ import annotations
import sys, pathlib, itertools
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qemstudy.v2.circuits import measurement_map, BASIS_GATES
from qemstudy.v2.rem import tensored, apply_rem

FAILS = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not cond: FAILS.append(name)

# Deliberately unequal per-PHYSICAL-qubit readout error rates.
P_ERR = {0: 0.30, 1: 0.02, 2: 0.15, 3: 0.05}
LINE = [[0,1],[1,2],[2,3],[1,0],[2,1],[3,2]]
N = 4


def resp(p):
    return np.array([[1 - p, p], [p, 1 - p]])


def ideal_probs(circ):
    """Exact ideal computational-basis probabilities, indexed by CLBIT string."""
    core = circ.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(core)
    return np.abs(sv.data) ** 2


def mats_for(order):
    """Per-clbit response matrices given the physical qubit each clbit reads."""
    return np.stack([resp(P_ERR[q]) for q in order])


print("\n=== REM indexing oracle: unequal response matrices, non-identity map ===")
qc = QuantumCircuit(N)
qc.h(0); qc.cx(0, 1); qc.ry(0.7, 2); qc.cx(2, 3); qc.rz(0.4, 1)
qc.measure_all()

for layout in ([0,1,2,3], [3,2,1,0], [1,3,0,2], [2,0,3,1]):
    t = transpile(qc, basis_gates=BASIS_GATES, coupling_map=LINE,
                  initial_layout=layout, optimization_level=1, seed_transpiler=0)
    mmap = measurement_map(t)                      # clbit -> physical qubit
    p_ideal = ideal_probs(t)

    # Exact measured distribution under the TRUE per-physical-qubit readout channel.
    A_true = tensored(mats_for(mmap))
    p_meas = A_true @ p_ideal
    check(f"layout={layout}: measured distribution is a valid probability vector",
          abs(p_meas.sum() - 1) < 1e-12 and (p_meas >= -1e-15).all())

    counts = {format(i, f"0{N}b"): p_meas[i] * 1e6 for i in range(2 ** N) if p_meas[i] > 1e-15}

    # (a) CORRECT: calibration aligned to the physical qubit each clbit reads.
    rec_ok, _ = apply_rem(counts, mats_for(mmap), N, clip=False)
    v_ok = np.zeros(2 ** N)
    for b, c in rec_ok.items(): v_ok[int(b, 2)] = c / 1e6
    err_ok = np.abs(v_ok - p_ideal).max()

    # (b) MISINDEXED: calibration indexed by virtual qubit (the v1 defect).
    rec_bad, _ = apply_rem(counts, mats_for(tuple(range(N))), N, clip=False)
    v_bad = np.zeros(2 ** N)
    for b, c in rec_bad.items(): v_bad[int(b, 2)] = c / 1e6
    err_bad = np.abs(v_bad - p_ideal).max()

    check(f"layout={layout}: ALIGNED calibration recovers the exact ideal distribution",
          err_ok < 1e-9, f"max|error| = {err_ok:.2e}")
    if tuple(mmap) == tuple(range(N)):
        check(f"layout={layout}: identity map -> misindexing is undetectable (expected)",
              err_bad < 1e-9, f"max|error| = {err_bad:.2e}")
    else:
        check(f"layout={layout}: MISINDEXED calibration fails to recover it",
              err_bad > 1e-3, f"max|error| = {err_bad:.2e} (aligned: {err_ok:.2e})")

print("\n=== Control: at ZERO readout noise the folding oracle cannot see this defect ===")
mats_id = np.stack([resp(0.0) for _ in range(N)])
t = transpile(qc, basis_gates=BASIS_GATES, coupling_map=LINE, initial_layout=[1,3,0,2],
              optimization_level=1, seed_transpiler=0)
p_ideal = ideal_probs(t)
counts = {format(i, f"0{N}b"): p_ideal[i] * 1e6 for i in range(2 ** N) if p_ideal[i] > 1e-15}
a, _ = apply_rem(counts, mats_id, N, clip=False)
b, _ = apply_rem(counts, mats_id[[1, 3, 0, 2]], N, clip=False)
same = all(abs(a.get(k, 0) - b.get(k, 0)) < 1e-9 for k in set(a) | set(b))
check("with p=0 every response matrix is the identity, so permuting them is invisible", same,
      "-> confirms the two defects require two independent oracles")

print("\n" + ("ALL TESTS PASSED" if not FAILS else f"{len(FAILS)} FAILURES: {FAILS}"))
sys.exit(1 if FAILS else 0)
