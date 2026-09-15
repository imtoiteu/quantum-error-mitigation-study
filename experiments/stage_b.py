"""Stage B -- in-loop VQA optimisation under each mitigation arm (RQ3).

Each objective evaluation spends the same total budget regardless of method.
Readout calibration is amortised: estimated once per run and reused, which is
realistic practice. Its cost is recorded separately so both accounting choices
can be reported.
"""
from __future__ import annotations
import json, sys, time, pathlib, itertools, platform, subprocess, hashlib
from multiprocessing import Pool
import numpy as np, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from qemstudy.problems import TFIM, MaxCutQAOA           # noqa: E402
from qemstudy.noise import NoiseSpec                     # noqa: E402
from qemstudy.runner import Executor, estimate           # noqa: E402
from qemstudy.mitigation import estimate_confusion, CAL_FRACTION  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "stage_b.yaml").read_text())
PARAMS = json.loads((ROOT / "configs" / "pretrained_params.json").read_text())
OUT = ROOT / "results" / "raw" / "stage_b.jsonl"


def make_objective(task):
    """Return (n, n_params, build_circuits, combine, reference, sign).

    `sign` = +1 when the objective is minimised directly (energy), -1 when the
    raw metric must be negated to be minimised (cut size).
    """
    if task == "tfim":
        t = TFIM(); pr = PARAMS["tfim"]
        return (t.n, t.ansatz(reps=1).num_parameters,
                lambda p: t.measured_circuits(p, reps=pr["reps"]),
                lambda v: t.energy_from_counts(v["z"], v["x"]),
                pr["ideal_energy"], +1.0)
    p = int(task.split("_p")[1]); q = MaxCutQAOA(p=p); pr = PARAMS[task]
    return (q.n, q.num_params(), lambda par: q.measured_circuits(par),
            lambda v: q.cut_from_counts(v["z"]), pr["ideal_cut"], -1.0)


def run_one(job):
    task, noise_cfg, method, seed = job
    n, npar, mk_circ, comb, ref, sign = make_objective(task)
    ns = NoiseSpec(noise_cfg["name"], noise_cfg["kind"], noise_cfg.get("lam", 1.0))
    budget = CFG["budget_per_eval"]
    sp = CFG["spsa"]
    rng = np.random.default_rng(seed)
    ex = Executor(ns, n, seed=seed)

    # amortised calibration (charged once, recorded separately)
    confusion, cal_shots, cal_execs = None, 0, 0
    if method in ("rem", "zne_rem"):
        per_cal = max(int(round(CAL_FRACTION * budget)) // (2 * n), 1)
        confusion, cal_shots, cal_execs = estimate_confusion(
            n, lambda cs, s, sd: ex.run(cs, s, sd), per_cal, seed + 9973)

    x = rng.uniform(0, 2 * np.pi, npar)
    t0 = time.perf_counter()
    trace, shots_total, exec_total, n_evals = [], cal_shots, cal_execs, 0

    def f(params):
        nonlocal shots_total, exec_total, n_evals
        r = estimate(Executor(ns, n, seed=seed), mk_circ(params), comb, method,
                     budget, seed + n_evals, confusion=confusion)
        shots_total += r.shots_used; exec_total += r.circuit_executions; n_evals += 1
        return sign * r.value, r.value

    for k in range(sp["iterations"]):
        ak = sp["a"] / (0.1 * sp["iterations"] + k + 1) ** sp["alpha"]
        ck = sp["c"] / (k + 1) ** sp["gamma"]
        delta = rng.choice([-1.0, 1.0], size=npar)
        fp, _ = f(x + ck * delta)
        fm, _ = f(x - ck * delta)
        x = x - ak * (fp - fm) / (2.0 * ck) * delta
        trace.append({"iter": k, "f_plus": fp, "f_minus": fm})

    # Final objective, evaluated NOISELESSLY to score the parameters found.
    # This separates "did the optimiser find good parameters?" from estimator noise.
    final_noisy, raw = f(x)
    ideal_ex = Executor(NoiseSpec("ideal", "ideal"), n, seed=seed)
    from qemstudy.runner import estimate as est
    final_ideal = est(ideal_ex, mk_circ(x), comb, "none", 200000, seed).value

    return {"task": task, "noise": noise_cfg["name"], "method": method, "seed": seed,
            "budget_per_eval": budget, "iterations": sp["iterations"],
            "final_params": list(map(float, x)),
            "final_value_noisy": raw, "final_value_ideal_eval": final_ideal,
            "reference": ref, "abs_error_ideal_eval": abs(final_ideal - ref),
            "shots_total": shots_total, "circuit_executions": exec_total,
            "objective_evaluations": n_evals, "calibration_shots": cal_shots,
            "wall_clock_s": time.perf_counter() - t0, "trace": trace}


def provenance():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        commit = "unknown"
    import qiskit, qiskit_aer, mitiq
    return {"git_commit": commit,
            "config_sha256_12": hashlib.sha256((ROOT / "configs" / "stage_b.yaml").read_bytes()).hexdigest()[:12],
            "host": platform.node(), "python": platform.python_version(),
            "qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__,
            "mitiq": mitiq.__version__, "simulator_only": True}


def main():
    jobs = list(itertools.product(CFG["tasks"], CFG["noise"], CFG["methods"], CFG["seeds"]))
    print(f"Stage B: {len(jobs)} runs, 4 workers", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prov = provenance(); t0 = time.perf_counter()
    with OUT.open("w") as fh, Pool(4) as pool:
        for i, row in enumerate(pool.imap_unordered(run_one, jobs), 1):
            fh.write(json.dumps({**row, "provenance": prov}) + "\n"); fh.flush()
            el = time.perf_counter() - t0
            print(f"  {i}/{len(jobs)} {row['task']:8s} {row['noise']:12s} {row['method']:8s} "
                  f"err={row['abs_error_ideal_eval']:.4f} {el:6.1f}s eta {el/i*(len(jobs)-i):6.1f}s", flush=True)
    print(f"done in {time.perf_counter()-t0:.1f}s -> {OUT}")


if __name__ == "__main__":
    main()
