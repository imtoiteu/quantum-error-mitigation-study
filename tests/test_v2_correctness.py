"""Regression tests for review findings A1 (mapping) and A2 (noise scaling).

Run:  .venv/bin/python tests/test_v2_correctness.py
Exit code 0 = all pass. No pytest dependency.
"""
from __future__ import annotations
import sys, pathlib, itertools
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, Operator
from qiskit_aer import AerSimulator
from qemstudy.v2.circuits import (fold_preserving_measurements, split_measurements,
                                  measurement_map, calibration_circuits, to_basis, BASIS_GATES)
from qemstudy.mitigation import fold as fold_v1

FAILS = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not cond: FAILS.append(name)

LINE = [[0,1],[1,2],[2,3],[1,0],[2,1],[3,2]]
LAYOUTS = [[0,1,2,3],[3,2,1,0],[1,3,0,2],[2,0,3,1]]
SCALES = [1.0, 2.0, 3.0, 5.0]


def deterministic_circuit():
    qc = QuantumCircuit(4); qc.x(0); qc.x(2); qc.measure_all(); return qc

def entangling_circuit(theta):
    qc = QuantumCircuit(4)
    qc.h(0); qc.cx(0,1); qc.cx(1,2); qc.cx(2,3)
    for q in range(4): qc.ry(theta*(q+1), q)
    qc.measure_all(); return qc


print("\n=== T1. Folding preserves the IDEAL distribution (oracle: U U^dag U = U) ===")
sim = AerSimulator()
for layout in LAYOUTS:
    t = transpile(deterministic_circuit(), basis_gates=BASIS_GATES, coupling_map=LINE,
                  initial_layout=layout, optimization_level=1, seed_transpiler=0)
    base = sim.run(t, shots=2000, seed_simulator=1).result().get_counts()
    for s in (3.0, 5.0):
        v2 = sim.run(fold_preserving_measurements(t, s), shots=2000, seed_simulator=1).result().get_counts()
        check(f"v2 fold scale={s} layout={layout}", base == v2, f"{dict(base)} vs {dict(v2)}")
    v1 = sim.run(fold_v1(t, 3.0), shots=2000, seed_simulator=1).result().get_counts()
    if layout != [0,1,2,3]:
        check(f"v1 fold REPRODUCES THE BUG (expected mismatch) layout={layout}",
              base != v1, f"{dict(base)} vs {dict(v1)}")


print("\n=== T2. Folding preserves EXACT probabilities and expectations (no sampling) ===")
# ROUND-2 CORRECTION (review finding 4): this test previously compared expectation
# values estimated from 40,000 sampled shots, which cannot establish an exact
# identity. It now compares exact statevector probabilities directly.
def exact_probs_of(circ):
    return np.abs(Statevector.from_instruction(
        circ.remove_final_measurements(inplace=False)).data) ** 2

def exact_parity_expval(probs, qubits, n=4):
    idx = np.arange(probs.size)
    par = np.zeros(probs.size)
    for q in qubits:
        par += (idx >> q) & 1
    return float(np.dot(probs, np.where(par % 2 == 0, 1.0, -1.0)))

for layout, theta in itertools.product(LAYOUTS, (0.3, 1.1)):
    t = transpile(entangling_circuit(theta), basis_gates=BASIS_GATES, coupling_map=LINE,
                  initial_layout=layout, optimization_level=1, seed_transpiler=0)
    p0 = exact_probs_of(t)
    for s in (3.0, 5.0):
        ps = exact_probs_of(fold_preserving_measurements(t, s))
        dmax = float(np.abs(ps - p0).max())
        # TOLERANCE, justified: for Clifford circuits the deviation is exactly 0 (see T2b).
        # With continuous rotations a fixed ~1e-11 offset appears from floating-point angle
        # representation in the inverted gates. Measured constant at scales 3, 5 and 9, so it
        # is a representation difference, not length-dependent accumulation. It is nine orders
        # of magnitude below the smallest physical effect reported in this paper (~1e-2).
        check(f"exact probability vector matches under folding (tol 1e-9), layout={layout} "
              f"theta={theta} scale={s}", dmax < 1e-9, f"max|dp| = {dmax:.2e}")
    ps3 = exact_probs_of(fold_preserving_measurements(t, 3.0))
    emax = max(abs(exact_parity_expval(ps3, [q]) - exact_parity_expval(p0, [q])) for q in range(4))
    check(f"exact <Z_q> identical under folding, layout={layout} theta={theta}",
          emax < 1e-12, f"max|d<Z>| = {emax:.2e}")


print("\n=== T2b. Clifford-only folding is EXACT to the last bit (tolerance 0) ===")
for layout in LAYOUTS:
    qc = QuantumCircuit(4); qc.h(0); qc.cx(0,1); qc.cx(1,2); qc.cx(2,3); qc.measure_all()
    t = transpile(qc, basis_gates=BASIS_GATES, coupling_map=LINE, initial_layout=layout,
                  optimization_level=1, seed_transpiler=0)
    p0 = exact_probs_of(t)
    worst = max(float(np.abs(exact_probs_of(fold_preserving_measurements(t, s)) - p0).max())
                for s in (3.0, 5.0, 9.0))
    check(f"Clifford folding exact at scales 3,5,9, layout={layout}", worst == 0.0,
          f"max|dp| = {worst:.1e}")

print("\n=== T3. Classical registers and measurement map preserved ===")
for layout in LAYOUTS:
    t = transpile(entangling_circuit(0.7), basis_gates=BASIS_GATES, coupling_map=LINE,
                  initial_layout=layout, optimization_level=1, seed_transpiler=0)
    f = fold_preserving_measurements(t, 3.0)
    check(f"clbit->phys map identical, layout={layout}", measurement_map(t) == measurement_map(f),
          f"{measurement_map(t)} vs {measurement_map(f)}")
    check(f"creg structure identical, layout={layout}",
          [c.size for c in t.cregs] == [c.size for c in f.cregs] and t.num_clbits == f.num_clbits)


print("\n=== T4. Calibration circuits target the physical qubits the clbits read ===")
t = transpile(entangling_circuit(0.7), basis_gates=BASIS_GATES, coupling_map=LINE,
              initial_layout=[1,3,0,2], optimization_level=1, seed_transpiler=0)
mmap = measurement_map(t)
cals = calibration_circuits(mmap, t.num_qubits, t.num_clbits)
ok = True
for c, phys in enumerate(mmap):
    prep1 = cals[2*c+1]
    xs = [prep1.find_bit(i.qubits[0]).index for i in prep1.data if i.operation.name == "x"]
    if xs != [phys]: ok = False
    if measurement_map(prep1) != mmap: ok = False
check(f"calibration X targets clbit's physical qubit and reuses the map (map={mmap})", ok)


print("\n=== T5. Unitary equivalence of the folded core (operator-level, not sampling) ===")
for s in (3.0, 5.0):
    qc = QuantumCircuit(3); qc.h(0); qc.cx(0,1); qc.rz(0.4,1); qc.cx(1,2); qc.ry(0.9,2)
    qc.measure_all()
    t = transpile(qc, basis_gates=BASIS_GATES, optimization_level=1, seed_transpiler=0)
    core_t,_ = split_measurements(t)
    core_f,_ = split_measurements(fold_preserving_measurements(t, s))
    check(f"folded core == original core as an operator, scale={s}",
          Operator(core_f.remove_final_measurements(inplace=False)).equiv(
              Operator(core_t.remove_final_measurements(inplace=False))))


print("\n=== T6. to_basis(optimization_level=0) does not cancel folded pairs ===")
qc = QuantumCircuit(4); qc.h(0); qc.cx(0,1); qc.cx(1,2); qc.cx(2,3); qc.measure_all()
t = transpile(qc, basis_gates=BASIS_GATES, coupling_map=LINE, initial_layout=[0,1,2,3],
              optimization_level=1, seed_transpiler=0)
cx0 = t.count_ops().get("cx", 0)
prev = 0
mono = True
for s in SCALES:
    f = to_basis(fold_preserving_measurements(t, s), 0)
    cx = f.count_ops().get("cx", 0)
    if cx < prev: mono = False
    prev = cx
    print(f"      scale={s}: cx={cx} (base {cx0}, ratio {cx/cx0:.2f})")
check("cx count is non-decreasing in scale factor and exceeds base", mono and prev > cx0)

print("\n" + ("ALL TESTS PASSED" if not FAILS else f"{len(FAILS)} FAILURES: {FAILS}"))
sys.exit(1 if FAILS else 0)
