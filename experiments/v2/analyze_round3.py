r"""Round-3 analysis (review findings 3, 4, 5).

PRIMARY ENDPOINT (finding 4) — paired held-out loss difference.
For each cell, m_L is the method selected on the SELECTION replicate under the legacy
implementation and m_C the method selected under the corrected implementation. The
per-cell quantity is

    Delta_heldout = ( loss_eval(m_L) - loss_eval(m_C) ) / C_max

where loss_eval is the absolute estimation error on the INDEPENDENT evaluation
replicate under the corrected implementation. Round 2 instead subtracted the minimum
over methods on the evaluation replicate; that minimum is a noisy realisation, not the
minimum expected risk, so that endpoint is withdrawn.

ESTIMAND: the mean of Delta_heldout over the six FIXED instances, equally weighted.
RESAMPLING UNIT: seed within instance (stratified bootstrap). A cluster bootstrap over
instances is reported alongside as the weaker generalisation interval.

NEAR TIES (finding 5) are reported over ALL cells and over CHANGED-WINNER cells, for
each candidate set, and separate the PRACTICAL threshold from STATISTICAL
indistinguishability.

COMPILATION (finding 3): the base-circuit fingerprint is ASSERTED identical across all
arms of a cell; violations are counted and reported, not absorbed.
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np, pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT/"results/v2r3/raw"; PROC = ROOT/"results/v2r3/processed"
PROC.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT/"src"))
MIT = ["zne", "rem", "zne_rem"]
ALL4 = ["none"] + MIT
SETS = {"mitigated_only": MIT, "incl_unmitigated": ALL4}
LABEL = {"none":"unmitigated","zne":"ZNE","rem":"REM","zne_rem":"ZNE+REM"}
RNG = np.random.default_rng(20260916)
NB = 10000
DELTA = 0.01            # declared practical threshold, in C_max units


def load():
    df = pd.DataFrame([json.loads(l) for l in (RAW/"confirm.jsonl").read_text().splitlines() if l.strip()])
    for k in ("total_shots","circuit_shots","calibration_shots","circuit_executions","calibration_executions"):
        df[k] = df["cost"].apply(lambda c, k=k: c.get(k, 0))
    df["loss_norm"] = df["estimation_error_abs"] / df["exact_max_cut"]
    df["signed_norm"] = df["estimation_error_signed"] / df["exact_max_cut"]
    df["fp"] = df["base_fingerprint"].apply(lambda d: d.get("z") if isinstance(d, dict) else None)
    return df


def assert_shared_compilation(df):
    """Finding 3: one base circuit per (instance, noise, seed) across ALL arms."""
    g = df.groupby(["instance","noise","seed"]).fp.nunique()
    bad = g[g > 1]
    out = dict(cells_checked=int(len(g)), cells_with_multiple_base_circuits=int(len(bad)),
               max_distinct=int(g.max()) if len(g) else 0)
    (PROC/"R3_compilation_check.json").write_text(json.dumps(out, indent=2))
    return out, bad


def strat_boot(per_inst, n_boot=NB):
    insts = list(per_inst)
    arrs = [np.asarray(per_inst[i], float) for i in insts]
    point = float(np.mean([a.mean() for a in arrs]))
    draws = np.empty(n_boot)
    for b in range(n_boot):
        draws[b] = np.mean([a[RNG.integers(0, len(a), len(a))].mean() for a in arrs])
    return point, float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def cluster_boot(per_inst, n_boot=NB):
    means = np.array([np.mean(v) for v in per_inst.values()], float)
    k = len(means)
    draws = means[RNG.integers(0, k, size=(n_boot, k))].mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def selection_table(df):
    """Per-cell selections, held-out losses, and tie diagnostics."""
    sel = df[df.eval_id == 0].set_index(["instance","noise","seed","method","impl"])
    ev  = df[df.eval_id == 1].set_index(["instance","noise","seed","method","impl"])
    cmax = df.groupby("instance").exact_max_cut.first()
    # Monte-Carlo scale for "statistically indistinguishable": sd of the loss across
    # seeds within (instance, noise, method) on the selection replicate, corrected impl.
    mc = (df[(df.eval_id == 0) & (df.impl == "v2")]
          .groupby(["instance","noise","method"]).loss_norm.std(ddof=1))
    recs = []
    for key in sorted({k[:3] for k in sel.index}):
        inst, nz, sd_ = key; cm = cmax[inst]
        def g(tab, m, impl):
            try: return float(tab.loc[key + (m, impl)])
            except KeyError: return np.nan
        S = {m: g(sel, m, "legacy") for m in MIT}
        V = {m: g(sel, m, "v2") for m in MIT}
        none_s = g(sel, "none", "v2")
        E = {m: g(ev, m, "v2") for m in MIT}; E["none"] = g(ev, "none", "v2")
        if any(np.isnan(list(S.values())+list(V.values())+list(E.values()))) or np.isnan(none_s):
            continue
        rec = dict(instance=inst, noise=nz, seed=sd_, cmax=cm)
        for sname, cand in SETS.items():
            Sx = dict(S, none=none_s) if "none" in cand else dict(S)
            Vx = dict(V, none=none_s) if "none" in cand else dict(V)
            mL, mC = min(Sx, key=Sx.get), min(Vx, key=Vx.get)
            # PRIMARY ENDPOINT: paired held-out loss difference between the two selections
            rec[f"delta_heldout__{sname}"] = (E[mL] - E[mC]) / cm
            rec[f"win_legacy__{sname}"], rec[f"win_v2__{sname}"] = mL, mC
            rec[f"changed__{sname}"] = mL != mC
            s2 = sorted(Vx.values())
            gap = (s2[1] - s2[0]) / cm
            rec[f"gap__{sname}"] = gap
            rec[f"tie_practical__{sname}"] = gap < DELTA
            sds = [mc.get((inst, nz, m), np.nan) for m in Vx]
            mc_scale = float(np.nanmean(sds)) if len(sds) else np.nan
            rec[f"tie_statistical__{sname}"] = bool(gap < mc_scale) if np.isfinite(mc_scale) else False
            rec[f"mc_scale__{sname}"] = mc_scale
        recs.append(rec)
    w = pd.DataFrame(recs); w.to_csv(PROC/"R3_selection.csv", index=False)
    return w


def endpoint_summary(w):
    rows = []
    for sname in SETS:
        col = f"delta_heldout__{sname}"
        for noise, g in list(w.groupby("noise")) + [("ALL", w)]:
            per_inst = {i: gg[col].values for i, gg in g.groupby("instance")}
            pt, lo, hi = strat_boot(per_inst); clo, chi = cluster_boot(per_inst)
            ch = g[f"changed__{sname}"]
            gap = g[f"gap__{sname}"]
            rows.append(dict(candidate_set=sname, noise=noise, n=len(g),
                delta_heldout=pt, ci_lo=lo, ci_hi=hi, cluster_lo=clo, cluster_hi=chi,
                changed_rate=float(ch.mean()),
                tie_practical_all=float(g[f"tie_practical__{sname}"].mean()),
                tie_practical_changed=float(g.loc[ch, f"tie_practical__{sname}"].mean()) if ch.any() else np.nan,
                tie_statistical_all=float(g[f"tie_statistical__{sname}"].mean()),
                tie_statistical_changed=float(g.loc[ch, f"tie_statistical__{sname}"].mean()) if ch.any() else np.nan,
                median_gap=float(gap.median()),
                delta_heldout_changed=float(g.loc[ch, col].mean()) if ch.any() else np.nan))
    s = pd.DataFrame(rows); s.to_csv(PROC/"R3_endpoint.csv", index=False)
    return s


def family1(df):
    d = df[(df.eval_id == 0) & (df.method.isin(MIT))]
    piv = d.pivot_table(index=["instance","noise","method","seed"], columns="impl",
                        values=["loss_norm","value","exact_max_cut"]).dropna()
    rows = []
    for (noise, method), g in piv.groupby(level=[1, 2]):
        d_abs = g[("loss_norm","legacy")] - g[("loss_norm","v2")]
        by = {i: gg.values for i, gg in d_abs.groupby(level=0)}
        pt, lo, hi = strat_boot(by); clo, chi = cluster_boot(by)
        ptm, _, _ = strat_boot({k: np.abs(v) for k, v in by.items()})
        try: pw = stats.wilcoxon(d_abs.values, zero_method="wilcox").pvalue
        except Exception: pw = np.nan
        rows.append(dict(noise=noise, method=method, n_cells=len(d_abs),
            mean_signed=pt, ci_lo=lo, ci_hi=hi, cluster_lo=clo, cluster_hi=chi,
            mean_abs=ptm, directionality=abs(pt)/ptm if ptm else np.nan, p_wilcoxon=pw))
    f1 = pd.DataFrame(rows)
    p = f1.p_wilcoxon.fillna(1.0).values; m = len(p); o = np.argsort(p); r = np.empty(m)
    adj = p[o]*m/np.arange(1, m+1); adj = np.minimum.accumulate(adj[::-1])[::-1]; r[o] = np.clip(adj, 0, 1)
    f1["p_adj_BH"] = r; f1["significant_BH_0.05"] = f1.p_adj_BH < 0.05
    f1.to_csv(PROC/"R3_F1.csv", index=False)
    return f1


def bias_variance(df):
    d = df[df.eval_id == 0]
    rows = []
    for (impl, noise, method), g in d.groupby(["impl","noise","method"]):
        by = {i: gg.signed_norm.values for i, gg in g.groupby("instance")}
        pb, blo, bhi = strat_boot(by)
        rows.append(dict(impl=impl, noise=noise, method=method, bias_norm=pb,
                         bias_lo=blo, bias_hi=bhi,
                         sd_norm=float(np.sqrt(np.mean([v.var(ddof=1) for v in by.values()]))),
                         rmse_norm=float(np.sqrt(np.mean([np.mean(v**2) for v in by.values()])))))
    bv = pd.DataFrame(rows).sort_values(["noise","method","impl"])
    bv.to_csv(PROC/"R3_bias_variance.csv", index=False); return bv


def costs(df):
    from qemstudy.v2.seeding import coords_from, audit_collisions
    dev = df.groupby("budget").total_shots.agg(["min","max"])
    rel = float(((dev["max"]-dev["min"])/dev["max"]).max())
    coords = [coords_from(r.seed_namespace, instance=r.instance, noise=r.noise, method=r.method,
                          budget=r.budget, seed=r.seed, eval_id=r.eval_id) for r in df.itertuples()]
    aud = audit_collisions("simulator", coords)
    tot = dict(cells=int(len(df)), total_shots=int(df.total_shots.sum()),
               circuit_shots=int(df.circuit_shots.sum()),
               calibration_shots=int(df.calibration_shots.sum()),
               circuit_executions=int(df.circuit_executions.sum()),
               calibration_executions=int(df.calibration_executions.sum()), scoring_shots=0,
               wall_clock_core_hours=float(df.wall_clock_s.sum()/3600),
               budget_max_rel_dev_pct=100*rel, collisions=int(aud["n_collisions"]),
               n_coords=int(aud["n_coords"]), n_distinct_seeds=int(aud["n_distinct_seeds"]))
    (PROC/"R3_cost.json").write_text(json.dumps(tot, indent=2)); return tot


def main():
    df = load()
    print(f"loaded {len(df)} rows; namespace={sorted(df.seed_namespace.unique())}")
    comp, bad = assert_shared_compilation(df)
    print(f"\n=== compilation-sharing assertion === {comp}")
    if comp["cells_with_multiple_base_circuits"]:
        print("  *** VIOLATION: base circuit differs across arms in some cells ***")
        print(bad.head().to_string())
    w = selection_table(df); s = endpoint_summary(w)
    f1 = family1(df); bv = bias_variance(df); tot = costs(df)
    pd.set_option("display.width", 220)
    print("\n=== PRIMARY ENDPOINT: paired held-out loss difference (legacy-selected - corrected-selected) ===")
    print(s[["candidate_set","noise","n","delta_heldout","ci_lo","ci_hi","cluster_lo","cluster_hi",
             "changed_rate","delta_heldout_changed"]].round(5).to_string(index=False))
    print("\n=== near ties: practical (<0.01 Cmax) vs statistical, all cells vs changed-winner cells ===")
    print(s[["candidate_set","noise","n","changed_rate","tie_practical_all","tie_practical_changed",
             "tie_statistical_all","tie_statistical_changed","median_gap"]].round(4).to_string(index=False))
    print("\n=== F1 implementation contrast ===")
    print(f1[["noise","method","n_cells","mean_signed","ci_lo","ci_hi","mean_abs","directionality","p_adj_BH"]].round(4).to_string(index=False))
    print("\n=== bias / variance ===")
    print(bv[["impl","noise","method","bias_norm","sd_norm","rmse_norm"]].round(4).to_string(index=False))
    print("\n=== cost / audit ===")
    print(json.dumps(tot, indent=2))


if __name__ == "__main__":
    main()
