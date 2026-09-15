"""Stage 0: pre-optimise ansatz parameters on an IDEAL, infinite-shot simulator.

Stage A then holds these parameters fixed, so that it measures ESTIMATOR quality
alone, uncontaminated by optimiser dynamics. Uses exact statevector expectation
values (no sampling), so the result is deterministic given the seed.
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np
from scipy.optimize import minimize
from qiskit.quantum_info import Statevector, SparsePauliOp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from qemstudy.problems import TFIM, MaxCutQAOA  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "configs" / "pretrained_params.json"


def tfim_op(t: TFIM) -> SparsePauliOp:
    terms = []
    for i, j in t.zz_pairs:
        s = ["I"] * t.n; s[i] = s[j] = "Z"
        terms.append(("".join(reversed(s)), -t.J))
    for i in range(t.n):
        s = ["I"] * t.n; s[i] = "X"
        terms.append(("".join(reversed(s)), -t.h))
    return SparsePauliOp.from_list(terms)


def main():
    rng = np.random.default_rng(20260915)
    out = {}

    # ---- VQE / TFIM ----
    t = TFIM(); op = tfim_op(t); exact = t.exact_ground_energy()
    anz = t.ansatz(reps=1)

    def vqe_cost(p):
        sv = Statevector.from_instruction(anz.assign_parameters(p))
        return float(np.real(sv.expectation_value(op)))

    best = None
    for _ in range(8):
        x0 = rng.uniform(0, 2 * np.pi, anz.num_parameters)
        r = minimize(vqe_cost, x0, method="COBYLA", options={"maxiter": 1200, "rhobeg": 0.5})
        if best is None or r.fun < best.fun:
            best = r
    out["tfim"] = {"n": t.n, "reps": 1, "params": list(map(float, best.x)),
                   "ideal_energy": float(best.fun), "exact_ground_energy": exact,
                   "ansatz_gap": float(best.fun - exact)}
    print(f"TFIM n={t.n}: exact={exact:.6f} ansatz_best={best.fun:.6f} gap={best.fun-exact:.6f}")

    # ---- QAOA / MaxCut ----
    for p in (1, 2):
        q = MaxCutQAOA(p=p); cmax = q.exact_max_cut()

        def qaoa_cost(par):
            qc = q.measured_circuits(par).pop("z").remove_final_measurements(inplace=False)
            probs = np.abs(Statevector.from_instruction(qc).data) ** 2
            tot = 0.0
            for idx, pr in enumerate(probs):
                if pr < 1e-12: continue
                b = format(idx, f"0{q.n}b")
                assign = [int(b[q.n - 1 - k]) for k in range(q.n)]
                tot += pr * sum(1 for i, j in q.edges if assign[i] != assign[j])
            return -tot

        best = None
        for _ in range(20):
            x0 = rng.uniform(0, np.pi, q.num_params())
            r = minimize(qaoa_cost, x0, method="COBYLA", options={"maxiter": 1200, "rhobeg": 0.3})
            if best is None or r.fun < best.fun:
                best = r
        out[f"qaoa_p{p}"] = {"n": q.n, "p": p, "params": list(map(float, best.x)),
                             "ideal_cut": float(-best.fun), "exact_max_cut": cmax,
                             "ideal_approx_ratio": float(-best.fun / cmax)}
        print(f"QAOA p={p}: C_max={cmax} ideal<C>={-best.fun:.6f} approx_ratio={-best.fun/cmax:.6f}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
