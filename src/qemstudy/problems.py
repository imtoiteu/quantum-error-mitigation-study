"""Problem definitions with exact classical references.

Two tasks:
  * TFIM VQE   (n=4)  -- exact ground-state energy by dense diagonalisation
  * MaxCut QAOA (n=6) -- exact maximum cut by brute-force enumeration
Both references are exact, not approximate, so "error" is unambiguous.
"""
from __future__ import annotations
import itertools
from dataclasses import dataclass, field
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import efficient_su2

# --------------------------------------------------------------------------- TFIM

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def _kron_at(n: int, ops: dict[int, np.ndarray]) -> np.ndarray:
    """Tensor product over n qubits, with `ops` placed at given indices.

    Qubit 0 is the least significant bit, matching Qiskit's ordering.
    """
    mat = np.array([[1.0 + 0j]])
    for q in range(n - 1, -1, -1):
        mat = np.kron(mat, ops.get(q, I2))
    return mat


@dataclass
class TFIM:
    """Open-chain transverse-field Ising model: H = -J sum Z_i Z_{i+1} - h sum X_i."""
    n: int = 4
    J: float = 1.0
    h: float = 1.0

    @property
    def zz_pairs(self) -> list[tuple[int, int]]:
        return [(i, i + 1) for i in range(self.n - 1)]

    def dense(self) -> np.ndarray:
        H = np.zeros((2 ** self.n, 2 ** self.n), dtype=complex)
        for i, j in self.zz_pairs:
            H -= self.J * _kron_at(self.n, {i: Z, j: Z})
        for i in range(self.n):
            H -= self.h * _kron_at(self.n, {i: X})
        return H

    def exact_ground_energy(self) -> float:
        return float(np.linalg.eigvalsh(self.dense())[0])

    def energy_from_counts(self, counts_z: dict[str, int], counts_x: dict[str, int]) -> float:
        """Reconstruct <H> from Z-basis and X-basis measurement outcomes."""
        e = 0.0
        for i, j in self.zz_pairs:
            e -= self.J * _pauli_parity_expval(counts_z, [i, j], self.n)
        for i in range(self.n):
            e -= self.h * _pauli_parity_expval(counts_x, [i], self.n)
        return e

    # -- circuits ----------------------------------------------------------
    def ansatz(self, reps: int = 1) -> QuantumCircuit:
        return efficient_su2(self.n, reps=reps, entanglement="linear")

    def measured_circuits(self, params: np.ndarray, reps: int = 1) -> dict[str, QuantumCircuit]:
        """Return {basis: circuit} -- 'z' for the ZZ terms, 'x' for the X terms."""
        base = self.ansatz(reps).assign_parameters(np.asarray(params, dtype=float))
        out = {}
        for basis in ("z", "x"):
            qc = QuantumCircuit(self.n)
            qc.compose(base, inplace=True)
            if basis == "x":
                for q in range(self.n):
                    qc.h(q)
            qc.measure_all()
            out[basis] = qc
        return out


def _pauli_parity_expval(counts: dict[str, int], qubits: list[int], n: int) -> float:
    """<prod_{q in qubits} Z_q> from a counts dict of Qiskit bitstrings."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    acc = 0
    for bits, c in counts.items():
        b = bits.replace(" ", "")
        # Qiskit bitstrings are little-endian: rightmost char is qubit 0.
        parity = sum(int(b[n - 1 - q]) for q in qubits) & 1
        acc += c if parity == 0 else -c
    return acc / total


# --------------------------------------------------------------------------- MaxCut / QAOA

PRISM_EDGES = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]


@dataclass
class MaxCutQAOA:
    """MaxCut on the triangular prism graph (3-regular, 6 vertices, 9 edges)."""
    n: int = 6
    edges: list[tuple[int, int]] = field(default_factory=lambda: list(PRISM_EDGES))
    p: int = 1

    def exact_max_cut(self) -> int:
        best = 0
        for assign in itertools.product([0, 1], repeat=self.n):
            cut = sum(1 for i, j in self.edges if assign[i] != assign[j])
            best = max(best, cut)
        return best

    def cut_from_counts(self, counts: dict[str, int]) -> float:
        total = sum(counts.values())
        if total == 0:
            return 0.0
        acc = 0.0
        for bits, c in counts.items():
            b = bits.replace(" ", "")
            assign = [int(b[self.n - 1 - q]) for q in range(self.n)]
            acc += c * sum(1 for i, j in self.edges if assign[i] != assign[j])
        return acc / total

    def num_params(self) -> int:
        return 2 * self.p

    def measured_circuits(self, params: np.ndarray) -> dict[str, QuantumCircuit]:
        params = np.asarray(params, dtype=float)
        gammas, betas = params[: self.p], params[self.p:]
        qc = QuantumCircuit(self.n)
        qc.h(range(self.n))
        for layer in range(self.p):
            for i, j in self.edges:
                qc.rzz(2.0 * gammas[layer], i, j)
            for q in range(self.n):
                qc.rx(2.0 * betas[layer], q)
        qc.measure_all()
        return {"z": qc}
