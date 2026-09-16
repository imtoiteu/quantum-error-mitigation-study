"""Transpilation contract and measurement-preserving folding (review findings A1, A2).

v1 defects addressed here
-------------------------
A1a  `mitigation.fold()` called `remove_final_measurements()` then `measure_all()`.
     When the transpiler chose a non-identity layout, the rebuilt `measure_all()`
     mapped physical qubit i -> clbit i, which is NOT the mapping the transpiled
     circuit used. Demonstrated: a circuit whose ideal outcome is '0101' returned
     '1010' after folding at scale 3, where global folding U U^dag U = U must
     leave the ideal distribution invariant.

A1b  `Executor.prepare()` never passed `initial_layout`, although the protocol
     claimed an explicit layout. The transpiler therefore chose layouts freely,
     and they were non-identity for tfim/dev_lagos, qaoa/dev_lagos and
     qaoa/dev_algiers.

A1c  REM calibration circuits were executed UNTRANSPILED, so calibration index i
     was physical qubit i, while main-circuit clbit i read the physical qubit the
     layout assigned. The confusion matrix was therefore applied to the wrong
     qubits whenever the layout was non-identity.

v2 contract
-----------
* `prepare()` pins `initial_layout=[0..n-1]` and returns the transpiled circuit
  together with the measured (physical qubit -> clbit) map read back off the
  circuit itself, so routing permutations are observed rather than assumed.
* `fold_preserving_measurements()` re-attaches the ORIGINAL measurement
  instructions and keeps the classical registers.
* REM calibration is built on the physical qubits that each clbit actually reads.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from qiskit import QuantumCircuit, transpile
from mitiq.zne.scaling import fold_global

BASIS_GATES = ["sx", "x", "rz", "cx"]


@dataclass(frozen=True)
class Prepared:
    circuit: QuantumCircuit
    clbit_to_phys: tuple[int, ...]   # clbit_to_phys[c] = physical qubit measured into clbit c
    initial_layout: tuple[int, ...] | None
    routing_permutation: tuple[int, ...] | None


def measurement_map(qc: QuantumCircuit) -> tuple[int, ...]:
    """clbit -> physical qubit, read directly off the circuit's measure instructions."""
    m = {}
    for inst in qc.data:
        if inst.operation.name == "measure":
            m[qc.find_bit(inst.clbits[0]).index] = qc.find_bit(inst.qubits[0]).index
    return tuple(m[c] for c in sorted(m))


def split_measurements(qc: QuantumCircuit):
    """Split into (unitary core, [(phys_qubit, clbit), ...]) without touching registers."""
    data = list(qc.data)
    cut = len(data)
    meas: list[tuple[int, int]] = []
    for i in range(len(data) - 1, -1, -1):
        name = data[i].operation.name
        if name == "measure":
            meas.append((qc.find_bit(data[i].qubits[0]).index,
                         qc.find_bit(data[i].clbits[0]).index))
            cut = i
        elif name == "barrier":
            cut = i
        else:
            break
    core = qc.copy_empty_like()
    for inst in data[:cut]:
        core.append(inst.operation, inst.qubits, inst.clbits)
    return core, sorted(meas, key=lambda t: t[1])


def fold_preserving_measurements(qc: QuantumCircuit, scale: float) -> QuantumCircuit:
    """Global unitary folding that re-attaches the ORIGINAL measurement mapping."""
    if scale == 1.0:
        return qc
    core, meas = split_measurements(qc)
    folded_core = fold_global(core.remove_final_measurements(inplace=False), scale)
    out = qc.copy_empty_like()               # same qregs AND cregs
    out.compose(folded_core, qubits=range(folded_core.num_qubits), inplace=True)
    for phys, cl in meas:
        out.measure(phys, cl)
    return out


def to_basis(qc: QuantumCircuit, seed: int) -> QuantumCircuit:
    """Basis translation ONLY (optimization_level=0) so folded pairs are not cancelled."""
    return transpile(qc, basis_gates=BASIS_GATES, optimization_level=0, seed_transpiler=seed)


def prepare(qc: QuantumCircuit, coupling_map, n: int, seed: int) -> Prepared:
    t = transpile(qc, basis_gates=BASIS_GATES, coupling_map=coupling_map,
                  initial_layout=list(range(n)) if coupling_map is not None else None,
                  optimization_level=1, seed_transpiler=seed)
    lay = t.layout
    il = fl = None
    if lay is not None:
        il = tuple(int(x) for x in lay.initial_index_layout(filter_ancillas=True))
        try:
            fl = tuple(int(x) for x in lay.routing_permutation())
        except Exception:
            fl = None
    return Prepared(t, measurement_map(t), il, fl)


def calibration_circuits(clbit_to_phys: tuple[int, ...], n_qubits: int, n_clbits: int):
    """2k circuits preparing |0>/|1> on the PHYSICAL qubit each clbit reads.

    Fixes A1c: calibration is aligned to the measurement map of the prepared
    circuit, not to the virtual index.
    """
    out = []
    for c, phys in enumerate(clbit_to_phys):
        for bit in (0, 1):
            qc = QuantumCircuit(n_qubits, n_clbits)
            if bit:
                qc.x(phys)
            for cc, pp in enumerate(clbit_to_phys):
                qc.measure(pp, cc)
            out.append(qc)
    return out


# --------------------------------------------------------------------------- v1 replicas
# Exact reproductions of the v1 defects, kept so the corrected and defective code
# paths can be run on IDENTICAL seeds and configurations. Used only by the
# implementation-impact experiment; never by the corrected main study.

def legacy_fold(circuit: QuantumCircuit, scale: float) -> QuantumCircuit:
    """v1 fold(): strips measurements and rebuilds them with measure_all().

    Defect A1a: measure_all() maps physical qubit i -> clbit i, discarding the
    layout-induced mapping the transpiled circuit actually used.
    """
    if scale == 1.0:
        return circuit
    stripped = circuit.remove_final_measurements(inplace=False)
    folded = fold_global(stripped, scale)
    out = QuantumCircuit(circuit.num_qubits)
    out.compose(folded, inplace=True)
    out.measure_all()
    return out


def legacy_calibration_circuits(n: int):
    """v1 calibration: prepares |0>/|1> on VIRTUAL index i, ignoring the layout (defect A1c)."""
    out = []
    for q in range(n):
        for bit in (0, 1):
            qc = QuantumCircuit(n)
            if bit:
                qc.x(q)
            qc.measure_all()
            out.append(qc)
    return out
