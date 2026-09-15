"""Stage A -- budget-matched estimation accuracy at fixed parameters (RQ1, RQ2).

Every (task, noise, budget, method, seed) cell spends the SAME total shots.
Writes one JSON object per cell to results/raw/stage_a.jsonl.
"""
from __future__ import annotations
import json, sys, time, pathlib, itertools, subprocess, platform, hashlib
from multiprocessing import Pool
import numpy as np, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from qemstudy.problems import TFIM, MaxCutQAOA          # noqa: E402
from qemstudy.noise import NoiseSpec                    # noqa: E402
from qemstudy.runner import Executor, estimate          # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "stage_a.yaml").read_text())
PARAMS = json.loads((ROOT / "configs" / "pretrained_params.json").read_text())
OUT = ROOT / "results" / "raw" / "stage_a.jsonl"


def provenance() -> dict:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        commit = "unknown"
    cfg_hash = hashlib.sha256((ROOT / "configs" / "stage_a.yaml").read_bytes()).hexdigest()[:12]
    import qiskit, qiskit_aer, mitiq
    return {"git_commit": commit, "config_sha256_12": cfg_hash, "host": platform.node(),
            "python": platform.python_version(), "qiskit": qiskit.__version__,
            "qiskit_aer": qiskit_aer.__version__, "mitiq": mitiq.__version__,
            "simulator_only": True}


def build(task: str):
    """Return (n, circuits_fn, combine_fn, reference_value, metric_name)."""
    if task == "tfim":
        t = TFIM(); pr = PARAMS["tfim"]
        circ = t.measured_circuits(np.array(pr["params"]), reps=pr["reps"])
        return (t.n, circ, lambda v: t.energy_from_counts(v["z"], v["x"]),
                pr["ideal_energy"], "energy")
    if task.startswith("qaoa"):
        p = int(task.split("_p")[1]); q = MaxCutQAOA(p=p); pr = PARAMS[task]
        circ = q.measured_circuits(np.array(pr["params"]))
        return (q.n, circ, lambda v: q.cut_from_counts(v["z"]), pr["ideal_cut"], "cut")
    raise ValueError(task)


def cell(job):
    task, noise_cfg, method, budget, seed = job
    n, circ, comb, ref, metric = build(task)
    ns = NoiseSpec(noise_cfg["name"], noise_cfg["kind"], noise_cfg.get("lam", 1.0))
    ex = Executor(ns, n, seed=seed)
    t0 = time.perf_counter()
    r = estimate(ex, circ, comb, method, budget, seed, fit=CFG["zne_fit"])
    return {"task": task, "noise": noise_cfg["name"], "noise_kind": noise_cfg["kind"],
            "lam": noise_cfg.get("lam", 1.0), "method": method, "budget": budget,
            "seed": seed, "metric": metric, "value": r.value, "reference": ref,
            "abs_error": abs(r.value - ref), "signed_error": r.value - ref,
            "shots_used": r.shots_used, "circuit_executions": r.circuit_executions,
            "wall_clock_s": time.perf_counter() - t0,
            "cx_per_scale": r.detail.get("cx_per_scale"),
            "scaled_values": r.detail.get("scaled_values")}


def main():
    jobs = [(t, nz, m, b, s) for t, nz, m, b, s in itertools.product(
        CFG["tasks"], CFG["noise"], CFG["methods"], CFG["budgets"], CFG["seeds"])]
    print(f"Stage A: {len(jobs)} cells, 4 workers")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prov = provenance()
    t0 = time.perf_counter()
    with OUT.open("w") as fh, Pool(4) as pool:
        for i, row in enumerate(pool.imap_unordered(cell, jobs, chunksize=4), 1):
            fh.write(json.dumps({**row, "provenance": prov}) + "\n")
            if i % 200 == 0:
                el = time.perf_counter() - t0
                print(f"  {i}/{len(jobs)}  {el:6.1f}s elapsed  eta {el/i*(len(jobs)-i):6.1f}s", flush=True)
    print(f"done in {time.perf_counter()-t0:.1f}s -> {OUT}")


if __name__ == "__main__":
    main()
