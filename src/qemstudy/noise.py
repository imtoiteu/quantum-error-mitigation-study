"""Noise-model construction.

Three families, all reproducible:
  * ideal            -- no noise
  * device snapshots -- NoiseModel.from_backend() on shipped IBM calibration data
  * param(lam)       -- hand-built model with a single tunable strength multiplier

Device snapshots come from qiskit-ibm-runtime's fake_provider and are STATIC data
pinned by the package version, not live device queries.
"""
from __future__ import annotations
from dataclasses import dataclass
from qiskit_aer.noise import (NoiseModel, depolarizing_error, thermal_relaxation_error,
                              ReadoutError)
from qiskit_ibm_runtime.fake_provider import FakeLagosV2, FakeAlgiers

# Selected by measured error rates (see docs/feasibility-report.md S3):
# lagos  -> readout-dominated (median readout err 0.169)
# algiers-> gate-dominated    (median readout err 0.011)
# Both are cx-native with >=7 qubits, which controls the folding confounder.
DEVICES = {"dev_lagos": FakeLagosV2, "dev_algiers": FakeAlgiers}

# param() reference rates at lam = 1.0
P1Q, P2Q, PRO = 1e-3, 1e-2, 2e-2
T1_US, T2_US, GATE_1Q_NS, GATE_2Q_NS = 100.0, 80.0, 50.0, 400.0


@dataclass(frozen=True)
class NoiseSpec:
    name: str
    kind: str          # 'ideal' | 'device' | 'param'
    lam: float = 1.0

    def build(self) -> NoiseModel | None:
        if self.kind == "ideal":
            return None
        if self.kind == "device":
            return NoiseModel.from_backend(DEVICES[self.name]())
        if self.kind == "param":
            return _build_param(self.lam)
        raise ValueError(f"unknown noise kind {self.kind!r}")

    def coupling_backend(self):
        """Backend to transpile against, or None for ideal/param (all-to-all)."""
        return DEVICES[self.name]() if self.kind == "device" else None


def _build_param(lam: float) -> NoiseModel:
    """Depolarizing + thermal relaxation + readout error, all scaled by `lam`."""
    nm = NoiseModel()
    t1, t2 = T1_US * 1e3, T2_US * 1e3          # ns
    # Thermal relaxation weakens as lam grows -> shorten coherence times.
    t1_s, t2_s = t1 / max(lam, 1e-9), t2 / max(lam, 1e-9)

    e1 = depolarizing_error(min(lam * P1Q, 1.0), 1).compose(
        thermal_relaxation_error(t1_s, t2_s, GATE_1Q_NS))
    e2 = depolarizing_error(min(lam * P2Q, 1.0), 2).compose(
        thermal_relaxation_error(t1_s, t2_s, GATE_2Q_NS).tensor(
            thermal_relaxation_error(t1_s, t2_s, GATE_2Q_NS)))
    nm.add_all_qubit_quantum_error(e1, ["sx", "x", "rx", "h", "u", "u1", "u2", "u3"])
    nm.add_all_qubit_quantum_error(e2, ["cx", "cz", "ecr", "rzz"])
    p = min(lam * PRO, 0.49)
    nm.add_all_qubit_readout_error(ReadoutError([[1 - p, p], [p, 1 - p]]))
    return nm


def all_noise_specs() -> list[NoiseSpec]:
    return ([NoiseSpec("ideal", "ideal")]
            + [NoiseSpec(n, "device") for n in DEVICES]
            + [NoiseSpec(f"param_lam{l:g}", "param", l) for l in (0.5, 1.0, 2.0)])
