r"""Round-2 analysis with corrected inference (review findings 5, 6, 7).

WHAT CHANGED FROM ROUND 1
  * Every difference is normalised by that instance's own C_max BEFORE averaging.
  * Primary inference is over SIX FIXED instances: a stratified bootstrap resamples
    seeds WITHIN each instance and averages across the six, because for a fixed
    instance the only random element is the seed. A secondary, deliberately weaker
    CLUSTER bootstrap resamples instances, to indicate what generalisation beyond
    these six would look like. The two are always reported side by side.
  * Four quantities are kept distinct and never conflated:
        d_est  difference between estimates
        d_abs  difference between absolute estimation errors
        bias   mean signed deviation of an estimate from the exact value
        var    sampling variance of the estimate across seeds
  * Winner sets include the unmitigated option and the candidate set is always named.
  * Regret is SPLIT-SAMPLE: replicate 0 selects, replicate 1 evaluates. Same-sample
    minima are reported separately and explicitly labelled as observed discrepancies.
  * Near ties are quantified.
"""
from __future__ import annotations
import json, sys, pathlib, itertools
import numpy as np, pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT/"results/v2r2/raw"; PROC = ROOT/"results/v2r2/processed"
PROC.mkdir(parents=True, exist_ok=True)
MIT = ["zne", "rem", "zne_rem"]
ALL4 = ["none"] + MIT
LABEL = {"none":"unmitigated","zne":"ZNE","rem":"REM","zne_rem":"ZNE+REM"}
RNG = np.random.default_rng(20260916)
NB = 10000


def load():
    df = pd.DataFrame([json.loads(l) for l in (RAW/"confirm.jsonl").read_text().splitlines() if l.strip()])
    for k in ("total_shots","circuit_shots","calibration_shots","circuit_executions","calibration_executions"):
        df[k] = df["cost"].apply(lambda c, k=k: c.get(k, 0))
    # normalised quantities (review finding 7)
    df["d_abs_norm"] = df["estimation_error_abs"] / df["exact_max_cut"]
    df["signed_norm"] = df["estimation_error_signed"] / df["exact_max_cut"]
    return df


def strat_boot(per_inst_seed_vals, n_boot=NB):
    """Primary: six FIXED instances; resample seeds within each, average across instances."""
    insts = list(per_inst_seed_vals)
    point = float(np.mean([np.mean(per_inst_seed_vals[i]) for i in insts]))
    draws = np.empty(n_boot)
    arrs = [np.asarray(per_inst_seed_vals[i], float) for i in insts]
    for b in range(n_boot):
        draws[b] = np.mean([a[RNG.integers(0, len(a), len(a))].mean() for a in arrs])
    return point, float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def cluster_boot(per_inst_seed_vals, n_boot=NB):
    """Secondary (weaker): resample INSTANCES with replacement -> generalisation interval."""
    insts = list(per_inst_seed_vals)
    means = np.array([np.mean(per_inst_seed_vals[i]) for i in insts], float)
    k = len(means)
    draws = means[RNG.integers(0, k, size=(n_boot, k))].mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def bh(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p); r = np.empty(m)
    adj = p[o]*m/np.arange(1, m+1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    r[o] = np.clip(adj, 0, 1); return r


# ---------------------------------------------------------------- F1: implementation contrast
def family1(df):
    """Paired under common random numbers: legacy vs corrected, same cell."""
    d = df[df.eval_id == 0]
    piv = d.pivot_table(index=["instance","noise","method","seed"], columns="impl",
                        values=["estimation_error_abs","value","exact_max_cut"])
    rows = []
    for (noise, method), g in piv.groupby(level=[1, 2]):
        cmax = g[("exact_max_cut","v2")]
        d_abs = ((g[("estimation_error_abs","legacy")] - g[("estimation_error_abs","v2")]) / cmax)
        d_est = ((g[("value","legacy")] - g[("value","v2")]) / cmax)
        by_inst_abs, by_inst_est = {}, {}
        for inst, gg in d_abs.groupby(level=0): by_inst_abs[inst] = gg.values
        for inst, gg in d_est.groupby(level=0): by_inst_est[inst] = gg.values
        pt, lo, hi = strat_boot(by_inst_abs); clo, chi = cluster_boot(by_inst_abs)
        ptm, _, _ = strat_boot({k: np.abs(v) for k, v in by_inst_abs.items()})
        pe, elo, ehi = strat_boot(by_inst_est)
        # test targets the declared estimand: paired within-cell contrast
        try: pw = stats.wilcoxon(d_abs.values, zero_method="wilcox").pvalue
        except Exception: pw = np.nan
        rows.append(dict(noise=noise, method=method, n_cells=len(d_abs), n_instances=len(by_inst_abs),
            mean_d_abs_norm=pt, ci_lo=lo, ci_hi=hi, cluster_lo=clo, cluster_hi=chi,
            mean_absolute_d_abs_norm=ptm,
            directionality=abs(pt)/ptm if ptm else np.nan,
            mean_d_est_norm=pe, d_est_lo=elo, d_est_hi=ehi, p_wilcoxon=pw))
    f1 = pd.DataFrame(rows)
    f1["p_adj_BH"] = bh(f1.p_wilcoxon.fillna(1.0))
    f1["significant_BH_0.05"] = f1.p_adj_BH < 0.05
    f1.to_csv(PROC/"R2_F1_implementation_contrast.csv", index=False)
    return f1


# ---------------------------------------------------------------- bias / variance, separately
def bias_variance(df):
    d = df[df.eval_id == 0]
    rows = []
    for (impl, noise, method), g in d.groupby(["impl","noise","method"]):
        per_inst_bias, per_inst_var = {}, {}
        for inst, gg in g.groupby("instance"):
            per_inst_bias[inst] = gg.signed_norm.values
            per_inst_var[inst] = [gg.signed_norm.var(ddof=1)]
        pb, blo, bhi = strat_boot(per_inst_bias)
        rows.append(dict(impl=impl, noise=noise, method=method,
                         bias_norm=pb, bias_lo=blo, bias_hi=bhi,
                         sd_norm=float(np.sqrt(np.mean([v[0] for v in per_inst_var.values()]))),
                         rmse_norm=float(np.sqrt(np.mean([np.mean(v**2) for v in per_inst_bias.values()])))))
    bv = pd.DataFrame(rows).sort_values(["noise","method","impl"])
    bv.to_csv(PROC/"R2_bias_variance.csv", index=False)
    return bv


# ---------------------------------------------------------------- winners, ties, split-sample regret
def winners(df):
    sel = df[df.eval_id == 0].set_index(["instance","noise","seed","method","impl"]).estimation_error_abs
    ev  = df[df.eval_id == 1].set_index(["instance","noise","seed","method","impl"]).estimation_error_abs
    cmax = df.groupby("instance").exact_max_cut.first()
    keys = sorted({k[:3] for k in sel.index})
    recs = []
    for key in keys:
        inst = key[0]; cm = cmax[inst]
        def get(tab, m, impl):
            try: return float(tab.loc[key + (m, impl)])
            except KeyError: return np.nan
        S_leg = {m: get(sel, m, "legacy") for m in MIT}
        S_v2  = {m: get(sel, m, "v2") for m in MIT}
        none_s = get(sel, "none", "v2")
        if any(np.isnan(list(S_leg.values()) + list(S_v2.values()))) or np.isnan(none_s):
            continue
        S_leg4 = dict(S_leg, none=none_s); S_v24 = dict(S_v2, none=none_s)
        w_leg3, w_v23 = min(S_leg, key=S_leg.get), min(S_v2, key=S_v2.get)
        w_leg4, w_v24 = min(S_leg4, key=S_leg4.get), min(S_v24, key=S_v24.get)
        # SPLIT-SAMPLE regret: choose on replicate 0, pay on replicate 1
        E_v2 = {m: get(ev, m, "v2") for m in MIT}; E_v2["none"] = get(ev, "none", "v2")
        if any(np.isnan(list(E_v2.values()))): continue
        oracle_eval = min(E_v2.values())
        recs.append(dict(instance=inst, noise=key[1], seed=key[2], cmax=cm,
            win_legacy3=w_leg3, win_v2_3=w_v23, flip3=w_leg3 != w_v23,
            win_legacy4=w_leg4, win_v2_4=w_v24, flip4=w_leg4 != w_v24,
            gap_top2_v2_norm=(sorted(S_v2.values())[1]-sorted(S_v2.values())[0])/cm,
            regret_split_legacy_norm=(E_v2[w_leg4]-oracle_eval)/cm,
            regret_split_v2_norm=(E_v2[w_v24]-oracle_eval)/cm,
            same_sample_discrepancy_norm=(S_v24[w_leg4]-S_v24[w_v24])/cm))
    w = pd.DataFrame(recs); w.to_csv(PROC/"R2_winners.csv", index=False)
    out = []
    for noise, g in w.groupby("noise"):
        bi_r_leg = {i: gg.regret_split_legacy_norm.values for i, gg in g.groupby("instance")}
        bi_r_v2  = {i: gg.regret_split_v2_norm.values for i, gg in g.groupby("instance")}
        rl, rl_lo, rl_hi = strat_boot(bi_r_leg); rv, rv_lo, rv_hi = strat_boot(bi_r_v2)
        out.append(dict(noise=noise, n=len(g),
            flip_rate_3mitigated=g.flip3.mean(), flip_rate_incl_unmitigated=g.flip4.mean(),
            near_tie_rate_lt_1pct=float((g.gap_top2_v2_norm < 0.01).mean()),
            median_gap_top2_norm=float(g.gap_top2_v2_norm.median()),
            split_regret_legacy=rl, slo=rl_lo, shi=rl_hi,
            split_regret_v2=rv, vlo=rv_lo, vhi=rv_hi,
            excess_regret_from_defect=rl-rv,
            mean_same_sample_discrepancy=float(g.same_sample_discrepancy_norm.mean())))
    allr = dict(noise="ALL", n=len(w),
        flip_rate_3mitigated=w.flip3.mean(), flip_rate_incl_unmitigated=w.flip4.mean(),
        near_tie_rate_lt_1pct=float((w.gap_top2_v2_norm < 0.01).mean()),
        median_gap_top2_norm=float(w.gap_top2_v2_norm.median()),
        split_regret_legacy=float(w.regret_split_legacy_norm.mean()), slo=np.nan, shi=np.nan,
        split_regret_v2=float(w.regret_split_v2_norm.mean()), vlo=np.nan, vhi=np.nan,
        excess_regret_from_defect=float(w.regret_split_legacy_norm.mean()-w.regret_split_v2_norm.mean()),
        mean_same_sample_discrepancy=float(w.same_sample_discrepancy_norm.mean()))
    s = pd.DataFrame(out + [allr]); s.to_csv(PROC/"R2_winner_summary.csv", index=False)
    # per-instance MEAN rankings (a different question from per-seed rates)
    m = df[df.eval_id == 0].groupby(["instance","noise","impl","method"]).estimation_error_abs.mean()
    rr = []
    for inst in sorted(df.instance.unique()):
        for nz in sorted(df[df.impl == "legacy"].noise.unique()):
            try:
                L = {x: m[(inst,nz,"legacy",x)] for x in MIT}
                V = {x: m[(inst,nz,"v2",x)] for x in MIT}
                V4 = dict(V, none=m[(inst,nz,"v2","none")]); L4 = dict(L, none=m[(inst,nz,"v2","none")])
            except KeyError: continue
            rr.append(dict(instance=inst, noise=nz, win_legacy=min(L,key=L.get), win_v2=min(V,key=V.get),
                           changed3=min(L,key=L.get)!=min(V,key=V.get),
                           win_legacy4=min(L4,key=L4.get), win_v2_4=min(V4,key=V4.get),
                           changed4=min(L4,key=L4.get)!=min(V4,key=V4.get)))
    pr = pd.DataFrame(rr); pr.to_csv(PROC/"R2_per_instance_rankings.csv", index=False)
    return w, s, pr


def main():
    df = load()
    print(f"loaded {len(df)} rows; replicates={sorted(df.eval_id.unique())}; "
          f"namespace={df.seed_namespace.unique()}")
    f1 = family1(df); bv = bias_variance(df); w, s, pr = winners(df)
    pd.set_option("display.width", 200)
    print("\n=== F1 implementation contrast (normalised by per-instance Cmax) ===")
    print(f1[["noise","method","n_cells","mean_d_abs_norm","ci_lo","ci_hi","cluster_lo","cluster_hi",
              "directionality","p_adj_BH"]].round(4).to_string(index=False))
    print("\n=== bias and variance, reported SEPARATELY (normalised) ===")
    print(bv[["impl","noise","method","bias_norm","bias_lo","bias_hi","sd_norm","rmse_norm"]].round(4).to_string(index=False))
    print("\n=== winners / ties / SPLIT-SAMPLE regret ===")
    print(s.round(4).to_string(index=False))
    print("\n=== per-instance mean rankings ===")
    print(pr.to_string(index=False))

if __name__ == "__main__":
    main()
