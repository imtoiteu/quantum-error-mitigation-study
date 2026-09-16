"""MaxCut instance family for the main study (multiple instances => generality claim)."""
from __future__ import annotations
import itertools
from dataclasses import dataclass, field
import numpy as np

# Six connected 6-vertex graphs spanning degree/structure. Deterministic: no graph seed.
INSTANCES = {
    "prism":      [(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5)],   # 3-regular, 9 edges
    "cycle6":     [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)],                     # 2-regular, 6 edges
    "k33":        [(0,3),(0,4),(0,5),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5)],   # bipartite 3-regular
    # NOTE: an earlier candidate "mobius" was verified isomorphic to k33 (networkx
    # is_isomorphic) and was replaced by the octahedron to keep instances distinct.
    "octahedron": [(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),
                   (2,4),(2,5),(3,4),(3,5)],                                 # 4-regular, 12 edges
    "path6":      [(0,1),(1,2),(2,3),(3,4),(4,5)],                           # tree, 5 edges
    "wheel5":     [(0,1),(1,2),(2,3),(3,4),(4,1),(0,2),(0,3),(0,4),(1,5),(5,3)],
}


@dataclass
class MaxCutInstance:
    name: str
    n: int = 6
    p: int = 1
    edges: list = field(default_factory=list)

    @classmethod
    def get(cls, name: str, p: int = 1):
        return cls(name=name, edges=list(INSTANCES[name]), p=p)

    def exact_max_cut(self) -> int:
        best = 0
        for a in itertools.product([0, 1], repeat=self.n):
            best = max(best, sum(1 for i, j in self.edges if a[i] != a[j]))
        return best

    def num_params(self) -> int:
        return 2 * self.p

    def measured_circuits(self, params):
        from qiskit import QuantumCircuit
        params = np.asarray(params, float)
        g, b = params[:self.p], params[self.p:]
        qc = QuantumCircuit(self.n, self.n)
        qc.h(range(self.n))
        for L in range(self.p):
            for i, j in self.edges:
                qc.rzz(2.0 * g[L], i, j)
            for q in range(self.n):
                qc.rx(2.0 * b[L], q)
        for q in range(self.n):
            qc.measure(q, q)
        return {"z": qc}

    def cut_from_counts(self, counts) -> float:
        tot = sum(counts.values())
        if tot == 0: return 0.0
        acc = 0.0
        for bits, c in counts.items():
            bb = bits.replace(" ", "")
            a = [int(bb[self.n - 1 - q]) for q in range(self.n)]
            acc += c * sum(1 for i, j in self.edges if a[i] != a[j])
        return acc / tot
