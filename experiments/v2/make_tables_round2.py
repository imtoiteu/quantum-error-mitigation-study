r"""Generate round-2 LaTeX tables and macros from processed round-2 results."""
from __future__ import annotations
import json, math, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT/"results/v2r2/processed"; TAB = ROOT/"manuscript/tables"; TAB.mkdir(parents=True, exist_ok=True)
LABEL = {"none":"unmitigated","zne":"ZNE","rem":"REM","zne_rem":"ZNE+REM"}
NL = {"dev_lagos":"\\texttt{dev\\_lagos}","dev_algiers":"\\texttt{dev\\_algiers}","ALL":"all"}

def w(name, s): (TAB/name).write_text(s); print("wrote", name)

def sci(x, sig=1):
    if x is None or (isinstance(x,float) and math.isnan(x)): return "--"
    x=float(x)
    if x<=0: return "$<10^{-15}$"
    e=math.floor(math.log10(x)); m=x/10**e
    return f"${x:.3f}$" if -2<=e<=0 else f"${m:.{sig}f}\\times10^{{{e}}}$"

def t_instances():
    refs=json.loads((ROOT/"configs/v2/references.json").read_text())
    rows=[f"\\texttt{{{k.replace('_',chr(92)+'_')}}} & {len(v['edges'])} & {v['exact_max_cut']} & "
          f"{v['ansatz_reference_best_known']:.4f} & {v['approx_ratio_at_reference']:.4f} & "
          f"{100*v['frac_starts_within_1e-6_of_best']:.0f}\\%\\\\" for k,v in refs.items()]
    w("tab_instances.tex","\\begin{tabular}{@{}lrrrrr@{}}\n\\toprule\nInstance & $|E|$ & $C_{\\max}$ & "
      "best $\\langle C\\rangle$ & ratio & at best\\\\\n\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")

def t_f1():
    f=pd.read_csv(PROC/"R2_F1_implementation_contrast.csv")
    rows=[]
    for _,r in f.sort_values(["noise","method"]).iterrows():
        rows.append(f"{NL[r.noise]} & {LABEL[r.method]} & {int(r.n_cells)} & {r.mean_d_abs_norm:+.4f} & "
                    f"[{r.ci_lo:+.4f}, {r.ci_hi:+.4f}] & [{r.cluster_lo:+.4f}, {r.cluster_hi:+.4f}] & "
                    f"{r.mean_absolute_d_abs_norm:.4f} & {r.directionality:.2f} & {sci(r['p_adj_BH'])}\\\\")
    w("tab_f1.tex","\\begin{tabular}{@{}llrrllrrr@{}}\n\\toprule\nNoise & Method & $n$ & mean signed & "
      "95\\% CI (stratified) & 95\\% CI (cluster) & mean $|\\cdot|$ & direct. & $p_{\\mathrm{BH}}$\\\\\n"
      "\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")

def t_bv():
    b=pd.read_csv(PROC/"R2_bias_variance.csv")
    rows=[]
    for _,r in b.sort_values(["noise","method","impl"]).iterrows():
        rows.append(f"{NL.get(r.noise,r.noise)} & {LABEL[r.method]} & {r.impl} & {r.bias_norm:+.4f} & "
                    f"[{r.bias_lo:+.4f}, {r.bias_hi:+.4f}] & {r.sd_norm:.4f} & {r.rmse_norm:.4f}\\\\")
    w("tab_bv.tex","\\begin{tabular}{@{}lllrlrr@{}}\n\\toprule\nNoise & Method & Impl. & bias & 95\\% CI & "
      "sd & RMSE\\\\\n\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")

def t_winner():
    s=pd.read_csv(PROC/"R2_winner_summary.csv")
    rows=[]
    for _,r in s.iterrows():
        rows.append(f"{NL.get(r.noise,r.noise)} & {int(r.n)} & {100*r.flip_rate_3mitigated:.1f}\\% & "
                    f"{100*r.flip_rate_incl_unmitigated:.1f}\\% & {100*r.near_tie_rate_lt_1pct:.1f}\\% & "
                    f"{r.split_regret_legacy:.4f} & {r.split_regret_v2:.4f} & {r.excess_regret_from_defect:+.4f}\\\\")
    w("tab_winner.tex","\\begin{tabular}{@{}lrrrrrrr@{}}\n\\toprule\nNoise & $n$ & change (3 mitig.) & "
      "change (incl. unmit.) & near-tie & regret defective & regret corrected & excess\\\\\n"
      "\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")

def macros():
    f=pd.read_csv(PROC/"R2_F1_implementation_contrast.csv")
    s=pd.read_csv(PROC/"R2_winner_summary.csv"); allr=s[s.noise=="ALL"].iloc[0]
    pr=pd.read_csv(PROC/"R2_per_instance_rankings.csv")
    tot=json.loads((PROC/"R2_cost.json").read_text())
    L=[]; m=lambda k,v: L.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    m("FONeminDis", f"{f.mean_absolute_d_abs_norm.min():.3f}")
    m("FONemaxDis", f"{f.mean_absolute_d_abs_norm.max():.3f}")
    m("DirectionalityMax", f"{f.directionality.max():.2f}")
    m("DirectionalityMin", f"{f.directionality.min():.2f}")
    m("FlipRateAllPct", f"{100*allr.flip_rate_3mitigated:.1f}")
    m("FlipRateInclUnmitPct", f"{100*allr.flip_rate_incl_unmitigated:.1f}")
    m("NearTiePct", f"{100*allr.near_tie_rate_lt_1pct:.1f}")
    m("WinnerScope", "the three mitigated methods")
    m("SplitRegretLegacy", f"{allr.split_regret_legacy:.4f}")
    m("SplitRegretV2", f"{allr.split_regret_v2:.4f}")
    m("SplitRegretExcess", f"{allr.excess_regret_from_defect:.4f}")
    m("PerInstChanged", f"{int(pr.changed3.sum())}"); m("PerInstTotal", f"{len(pr)}")
    m("BudgetMaxDev", f"{tot['budget_max_rel_dev_pct']:.4f}")
    m("CollisionCount", f"{tot['collisions']}")
    m("NumCellsR", f"{tot['cells']:,}"); m("TotalShotsR", f"{tot['total_shots']:,}")
    m("CoreHoursR", f"{tot['wall_clock_core_hours']:.2f}")
    (TAB/"macros.tex").write_text("\n".join(L)+"\n"); print(f"wrote macros.tex ({len(L)} macros)")

if __name__=="__main__":
    t_instances(); t_f1(); t_bv(); t_winner(); macros()
    print("round-2 tables generated")
