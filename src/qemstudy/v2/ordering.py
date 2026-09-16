r"""Explicit conversion between physical-qubit order and classical-bit order.

ROUND-3 CORRECTION (review finding 1)
-------------------------------------
`Statevector.from_instruction(circ.remove_final_measurements())` returns amplitudes
indexed by **physical qubit**: bit q of the index is physical qubit q. Measured counts
are indexed by **classical bit**: bit c of the bitstring is clbit c, which records
physical qubit pi(c). Under a non-identity measurement map the two orderings differ,
and conflating them silently mislabels every outcome.

Verified directly: for a circuit preparing |1> on virtual qubit 0 under
initial_layout [3,2,1,0], the statevector argmax is '1000' while the measured argmax
is '0001'.
"""
from __future__ import annotations
import numpy as np


def phys_to_clbit_probs(p_phys: np.ndarray, clbit_to_phys) -> np.ndarray:
    """Re-index a physical-qubit-ordered probability vector into clbit order.

    clbit_to_phys[c] is the physical qubit that clbit c records. Every measured qubit
    must appear exactly once (the map is a bijection onto the measured set).
    """
    k = len(clbit_to_phys)
    if len(set(clbit_to_phys)) != k:
        raise ValueError("measurement map is not injective")
    n_phys = int(round(np.log2(len(p_phys))))
    out = np.zeros(2 ** k)
    idx = np.arange(len(p_phys))
    j = np.zeros(len(p_phys), dtype=np.int64)
    for c, phys in enumerate(clbit_to_phys):
        if phys >= n_phys:
            raise ValueError(f"clbit {c} maps to physical qubit {phys} outside the state")
        j |= (((idx >> phys) & 1) << c)
    np.add.at(out, j, p_phys)
    return out


def apply_readout_bitwise(p_clbit: np.ndarray, err_by_clbit) -> np.ndarray:
    """Apply independent per-clbit readout error WITHOUT building a tensored matrix.

    Deliberately a different code path from `rem.tensored()`, so a test that generates
    a distribution here and recovers it with `rem.apply_rem` is not inverting the same
    object it used to construct the input.
    """
    p = np.asarray(p_clbit, float).copy()
    k = len(err_by_clbit)
    for c, e in enumerate(err_by_clbit):
        p01, p10 = (e, e) if np.isscalar(e) else (e[0], e[1])   # P(1|0), P(0|1)
        new = np.zeros_like(p)
        for i in range(p.size):
            bit = (i >> c) & 1
            flipped = i ^ (1 << c)
            stay, flip = (1 - p01, p01) if bit == 0 else (1 - p10, p10)
            new[i] += p[i] * stay
            new[flipped] += p[i] * flip
        p = new
    return p
