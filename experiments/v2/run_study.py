"""Main-study driver: config-driven, checkpointed, resumable, single-worker.

Shared-VPS policy (D): one worker, BLAS/OpenMP/Aer capped to 1 thread, nice'd,
append-only JSONL with flush after every cell so an interrupted batch resumes
without loss and without recomputation.

Usage:
  python experiments/v2/run_study.py --config configs/v2/main_study.yaml [--limit N]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, json, hashlib, itertools, pathlib, platform, subprocess, sys, time, resource
import numpy as np, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qemstudy.v2.instances import MaxCutInstance                      # noqa: E402
from qemstudy.v2.runner import Executor, estimate                     # noqa: E402
from qemstudy.v2.scoring import exact_cut_value                       # noqa: E402
from qemstudy.noise import NoiseSpec                                  # noqa: E402


EXEC_PATH_FILES = [
    "src/qemstudy/v2/runner.py", "src/qemstudy/v2/circuits.py", "src/qemstudy/v2/rem.py",
    "src/qemstudy/v2/seeding.py", "src/qemstudy/v2/instances.py", "src/qemstudy/v2/scoring.py",
    "src/qemstudy/noise.py", "experiments/v2/run_study.py",
]


def exec_path_hashes() -> dict:
    """Content hash of every file that participates in generating a data row.

    ROUND-2 (review finding 8): the earlier run recorded git_dirty=True with no way
    to tell which code actually executed. Content hashes make the executed version
    identifiable regardless of working-tree state.
    """
    out = {}
    for rel in EXEC_PATH_FILES:
        f = ROOT / rel
        out[rel] = hashlib.sha256(f.read_bytes()).hexdigest()[:16] if f.exists() else None
    return out


def provenance(cfg_path: pathlib.Path) -> dict:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).decode().strip())
    except Exception:
        commit, dirty = "unknown", True
    import qiskit, qiskit_aer, mitiq
    return {"git_commit": commit, "git_dirty": dirty,
            "exec_path_sha256": exec_path_hashes(),
            "config_sha256": hashlib.sha256(cfg_path.read_bytes()).hexdigest(),
            "host": platform.node(), "python": platform.python_version(),
            "qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__,
            "mitiq": mitiq.__version__, "simulator_only": True, "hardware_used": "none"}


def cell_key(c) -> str:
    return "|".join(str(c.get(k, 0)) for k in
                    ("instance", "noise", "method", "budget", "seed", "impl", "eval_id"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--limit", type=int, default=0, help="stop after N new cells (batching)")
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = yaml.safe_load(cfg_path.read_text())
    if "seed_namespace" not in cfg:
        raise SystemExit("config must declare seed_namespace (see src/qemstudy/v2/seeding.py)")
    refs = json.loads((ROOT / "configs" / "v2" / "references.json").read_text())
    out_path = ROOT / cfg["output"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    done = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                try: done.add(cell_key(json.loads(line)))
                except Exception: pass
    prov = provenance(cfg_path)

    jobs = []
    n_rep = int(cfg.get("eval_replicates", 1))
    for inst, nz, meth, bud, seed, impl, ev in itertools.product(
            cfg["instances"], cfg["noise"], cfg["methods"],
            cfg["budgets"], cfg["seeds"], cfg["impls"], range(n_rep)):
        if impl == "legacy":
            if meth == "none" or bud != cfg["legacy_budget"] or nz["kind"] != "device":
                continue                      # legacy arm only where the defect can act
        jobs.append(dict(instance=inst, noise=nz["name"], noise_kind=nz["kind"],
                         lam=nz.get("lam", 1.0), method=meth, budget=bud,
                         seed=seed, impl=impl, eval_id=ev))
    todo = [j for j in jobs if cell_key(j) not in done]
    print(f"total cells {len(jobs)}, already done {len(jobs)-len(todo)}, to run {len(todo)}", flush=True)
    if args.limit:
        todo = todo[:args.limit]
        print(f"batch limited to {len(todo)}", flush=True)

    t0 = time.perf_counter()
    with out_path.open("a") as fh:
        for i, j in enumerate(todo, 1):
            I = MaxCutInstance.get(j["instance"], p=cfg["p"])
            r = refs[j["instance"]]
            params = r["ansatz_reference_params"]
            circ = I.measured_circuits(params)
            comb = lambda v, I=I: I.cut_from_counts(v["z"])
            ns = NoiseSpec(j["noise"], j["noise_kind"], j["lam"])
            ex = Executor(ns, I.n, run_id=j["seed"],
                          namespace=cfg["seed_namespace"],
                          cell=dict(instance=j["instance"], noise=j["noise"],
                                    method=j["method"], budget=j["budget"], seed=j["seed"]))
            val, detail, _ = estimate(
                ex, circ, comb, j["method"], j["budget"],
                eval_id=j.get("eval_id", 0), scales=tuple(cfg["scales"]), fit=cfg["fit"],
                cal_fraction=cfg["cal_fraction"], clip=cfg["rem_clip"],
                legacy_mapping=(j["impl"] == "legacy"))
            exact_at_params = exact_cut_value(I, params)
            row = {**j, **prov, "seed_namespace": cfg["seed_namespace"],
                   "value": val,
                   "exact_noiseless_at_params": exact_at_params,
                   "ansatz_reference_best_known": r["ansatz_reference_best_known"],
                   "exact_max_cut": r["exact_max_cut"],
                   # estimation error: |estimate - exact noiseless value at the SAME params|
                   "estimation_error_abs": abs(val - exact_at_params),
                   "estimation_error_signed": val - exact_at_params,
                   "cost": detail["cost_delta"],
                   "rem_negative_mass": detail.get("rem_negative_mass"),
                   "rem_cond_number": detail.get("rem_cond_number"),
                   "gate_counts_per_scale": detail.get("gate_counts_per_scale"),
                   "clbit_to_phys": detail.get("clbit_to_phys"),
                   "initial_layout": detail.get("initial_layout"),
                   "routing_permutation": detail.get("routing_permutation"),
                   "wall_clock_s": detail["wall_clock_s"],
                   "peak_rss_gb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6}
            fh.write(json.dumps(row) + "\n"); fh.flush()
            if i % 100 == 0 or i == len(todo):
                el = time.perf_counter() - t0
                print(f"  {i}/{len(todo)}  {el:7.1f}s  eta {el/i*(len(todo)-i):7.1f}s  "
                      f"rss {row['peak_rss_gb']:.2f}GB", flush=True)
    print(f"batch done in {time.perf_counter()-t0:.1f}s -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
