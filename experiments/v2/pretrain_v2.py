"""Best-known ansatz reference per instance, by multistart exact-statevector optimisation.

IMPORTANT LABELLING (review finding A4): the value stored here is a MULTISTART
NUMERICAL BEST-KNOWN value. It is NOT a proven global optimum of the ansatz.
All downstream reporting calls it `ansatz_reference_best_known`.
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np
from scipy.optimize import minimize
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qemstudy.v2.instances import INSTANCES, MaxCutInstance
from qemstudy.v2.scoring import exact_cut_value
from qemstudy.v2.seeding import generator

OUT = ROOT / "configs" / "v2" / "references.json"
N_STARTS = 60

def main():
    out = {}
    for name in INSTANCES:
        I = MaxCutInstance.get(name, p=1)
        cmax = I.exact_max_cut()
        rng = generator("init_params", abs(hash(name)) % 10_000)
        best_x, best_v = None, -np.inf
        vals = []
        for s in range(N_STARTS):
            x0 = rng.uniform(0, np.pi, I.num_params())
            r = minimize(lambda p: -exact_cut_value(I, p), x0, method="COBYLA",
                         options={"maxiter": 2000, "rhobeg": 0.3})
            vals.append(-r.fun)
            if -r.fun > best_v:
                best_v, best_x = -r.fun, r.x
        vals = np.array(vals)
        out[name] = {
            "instance": name, "n": I.n, "p": 1, "edges": I.edges,
            "exact_max_cut": cmax,
            "ansatz_reference_best_known": float(best_v),
            "ansatz_reference_params": [float(v) for v in best_x],
            "approx_ratio_at_reference": float(best_v / cmax),
            "n_starts": N_STARTS,
            "frac_starts_within_1e-6_of_best": float(np.mean(vals > best_v - 1e-6)),
            "reference_is_proven_global_optimum": False,
        }
        print(f"{name:8s} Cmax={cmax}  best-known <C>={best_v:.6f}  ratio={best_v/cmax:.4f}  "
              f"reached by {100*np.mean(vals>best_v-1e-6):.0f}% of {N_STARTS} starts")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print("wrote", OUT)

if __name__ == "__main__":
    main()
