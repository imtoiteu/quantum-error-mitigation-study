"""Readout-error mitigation: explicit definition and diagnostics (review finding A6).

Definition (this is ONE REM method; results must not be generalised to all REM):
  * Model: independent per-qubit readout, so the joint response matrix is a
    tensor product A = (x)_q A_q with A_q[m, p] = Pr(measure m | prepared p).
  * Calibration: 2k circuits preparing |0>/|1> on the PHYSICAL qubit each clbit
    reads (see circuits.calibration_circuits), executed under the same noise
    model and charged against the shot budget.
  * Inversion: solve A x = p_hat exactly (np.linalg.solve), not pseudo-inverse,
    unless A is singular.
  * Clipping: negative entries -> 0, then renormalise to sum 1. This is the
    standard practical fix; it is a BIASED estimator. `clip=False` returns the
    raw (possibly negative) quasi-distribution so the effect can be measured.

ASSUMPTIONS THAT CAN FAIL: no correlated readout error; no state-preparation
error separate from measurement error; stationary calibration.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class RemDiagnostics:
    negative_mass: float          # total |negative| probability removed by clipping
    cond_number: float            # 2-norm condition number of the tensored A
    min_diag: float               # smallest per-qubit Pr(correct)


def build_confusion(counts_list, clbit_to_phys, n_clbits) -> np.ndarray:
    """Per-clbit 2x2 matrices A_c[m, p] from the 2k calibration circuits."""
    k = len(clbit_to_phys)
    mats = np.zeros((k, 2, 2))
    for idx, counts in enumerate(counts_list):
        c, prepared = idx // 2, idx % 2
        tot = sum(counts.values()) or 1
        p1 = sum(v for b, v in counts.items()
                 if int(b.replace(" ", "")[n_clbits - 1 - c]) == 1) / tot
        mats[c, 1, prepared] = p1
        mats[c, 0, prepared] = 1.0 - p1
    return mats


def tensored(mats: np.ndarray) -> np.ndarray:
    A = np.array([[1.0]])
    for c in range(mats.shape[0] - 1, -1, -1):   # clbit 0 is least significant
        A = np.kron(A, mats[c])
    return A


def apply_rem(counts: dict, mats: np.ndarray, n_clbits: int, clip: bool = True):
    dim = 2 ** n_clbits
    total = sum(counts.values()) or 1
    vec = np.zeros(dim)
    for b, v in counts.items():
        vec[int(b.replace(" ", ""), 2)] = v / total
    A = tensored(mats)
    cond = float(np.linalg.cond(A))
    try:
        x = np.linalg.solve(A, vec)
    except np.linalg.LinAlgError:
        x = np.linalg.pinv(A) @ vec
    neg = float(-x[x < 0].sum())
    if clip:
        x = np.clip(x, 0.0, None)
        s = x.sum()
        x = x / s if s > 0 else vec
    diag = RemDiagnostics(neg, cond, float(min(mats[c, p, p] for c in range(mats.shape[0]) for p in (0, 1))))
    out = {format(i, f"0{n_clbits}b"): x[i] * total for i in range(dim) if abs(x[i]) > 1e-15}
    return out, diag
