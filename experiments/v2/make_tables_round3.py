r"""Round-3 LaTeX tables and macros, generated from results/v2r3/processed."""
from __future__ import annotations
import json, math, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT/"results/v2r3/processed"; TAB = ROOT/"manuscript/tables"; TAB.mkdir(parents=True, exist_ok=True)
LABEL = {"none":"unmitigated","zne":"ZNE","rem":"REM","zne_rem":"ZNE+REM"}
NL = {"dev_lagos":"\\texttt{dev\\_lagos}","dev_algiers":"\\texttt{dev\\_algiers}","ALL":"all"}
CS = {"mitigated_only":"mitigated only","incl_unmitigated":"incl.\\ unmitigated"}


def w(name, s): (TAB/name).write_text(s); print("wrote", name)


def sci(x, sig=1):
    if x is None or (isinstance(x, float) and math.isnan(x)): return "--"
    x = float(x)
    if x <= 0: return "$<10^{-15}$"
    e = math.floor(math.log10(x)); m = x/10**e
    return f"${x:.3f}$" if -2 <= e <= 0 else f"${m:.{sig}f}\\times10^{{{e}}}$"


def t_instances():
    refs = json.loads((ROOT/"configs/v2/references.json").read_text())
    rows = [f"\\texttt{{{k.replace('_',chr(92)+'_')}}} & {len(v['edges'])} & {v['exact_max_cut']} & "
            f"{v['ansatz_reference_best_known']:.4f} & {v['approx_ratio_at_reference']:.4f} & "
            f"{100*v['frac_starts_within_1e-6_of_best']:.0f}\\%\\\\" for k, v in refs.items()]
    w("tab_instances.tex", "\\begin{tabular}{@{}lrrrrr@{}}\n\\toprule\nInstance & $|E|$ & $C_{\\max}$ & "
      "best $\\langle C\\rangle$ & ratio & at best\\\\\n\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")


def t_f1():
    f = pd.read_csv(PROC/"R3_F1.csv")
    rows = [f"{NL[r.noise]} & {LABEL[r.method]} & {int(r.n_cells)} & {r.mean_signed:+.4f} & "
            f"[{r.ci_lo:+.4f}, {r.ci_hi:+.4f}] & [{r.cluster_lo:+.4f}, {r.cluster_hi:+.4f}] & "
            f"{r.mean_abs:.4f} & {r.directionality:.2f} & {sci(r['p_adj_BH'])}\\\\"
            for _, r in f.sort_values(["noise","method"]).iterrows()]
    w("tab_f1.tex", "\\begin{tabular}{@{}llrrllrrr@{}}\n\\toprule\nNoise & Method & $n$ & mean signed & "
      "95\\% CI (stratified) & 95\\% CI (cluster) & mean $|\\cdot|$ & direct. & $p_{\\mathrm{BH}}$\\\\\n"
      "\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")


def t_bv():
    b = pd.read_csv(PROC/"R3_bias_variance.csv")
    rows = [f"{NL.get(r.noise,r.noise)} & {LABEL[r.method]} & {r.impl} & {r.bias_norm:+.4f} & "
            f"[{r.bias_lo:+.4f}, {r.bias_hi:+.4f}] & {r.sd_norm:.4f} & {r.rmse_norm:.4f}\\\\"
            for _, r in b.sort_values(["noise","method","impl"]).iterrows()]
    w("tab_bv.tex", "\\begin{tabular}{@{}lllrlrr@{}}\n\\toprule\nNoise & Method & Impl. & bias & 95\\% CI & "
      "sd & RMSE\\\\\n\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")


def t_endpoint():
    s = pd.read_csv(PROC/"R3_endpoint.csv")
    rows = []
    for _, r in s.iterrows():
        rows.append(f"{CS[r.candidate_set]} & {NL.get(r.noise,r.noise)} & {int(r.n)} & "
                    f"{r.delta_heldout:+.4f} & [{r.ci_lo:+.4f}, {r.ci_hi:+.4f}] & "
                    f"[{r.cluster_lo:+.4f}, {r.cluster_hi:+.4f}] & {100*r.changed_rate:.1f}\\% \\\\")
    w("tab_endpoint.tex", "\\begin{tabular}{@{}llrrllr@{}}\n\\toprule\nCandidate set & Noise & $n$ & "
      "$\\Delta_{\\text{held-out}}$ & 95\\% CI (stratified) & 95\\% CI (cluster) & winner changed\\\\\n"
      "\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")


def t_ties():
    s = pd.read_csv(PROC/"R3_endpoint.csv")
    rows = []
    for _, r in s.iterrows():
        tpc = "--" if pd.isna(r.tie_practical_changed) else f"{100*r.tie_practical_changed:.1f}\\%"
        tsc = "--" if pd.isna(r.tie_statistical_changed) else f"{100*r.tie_statistical_changed:.1f}\\%"
        rows.append(f"{CS[r.candidate_set]} & {NL.get(r.noise,r.noise)} & {int(r.n)} & "
                    f"{100*r.tie_practical_all:.1f}\\% & {tpc} & "
                    f"{100*r.tie_statistical_all:.1f}\\% & {tsc} & {r.median_gap:.4f}\\\\")
    w("tab_ties.tex", "\\begin{tabular}{@{}llrrrrrr@{}}\n\\toprule\n & & & "
      "\\multicolumn{2}{c}{practical ($<0.01\\,C_{\\max}$)} & \\multicolumn{2}{c}{statistical} & \\\\\n"
      "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\n"
      "Candidate set & Noise & $n$ & all & changed & all & changed & median gap\\\\\n"
      "\\midrule\n"+"\n".join(rows)+"\n\\bottomrule\n\\end{tabular}\n")


def macros():
    f = pd.read_csv(PROC/"R3_F1.csv")
    s = pd.read_csv(PROC/"R3_endpoint.csv")
    tot = json.loads((PROC/"R3_cost.json").read_text())
    comp = json.loads((PROC/"R3_compilation_check.json").read_text())
    a_all = s[(s.candidate_set=="mitigated_only") & (s.noise=="ALL")].iloc[0]
    a_inc = s[(s.candidate_set=="incl_unmitigated") & (s.noise=="ALL")].iloc[0]
    L = []
    def m(k, v):
        if not k.isalpha():
            raise ValueError(f"macro name {k!r} must be letters only (LaTeX restriction)")
        L.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    m("FONeminDis", f"{f.mean_abs.min():.3f}"); m("FONemaxDis", f"{f.mean_abs.max():.3f}")
    m("DirectionalityMax", f"{f.directionality.max():.2f}")
    m("DirectionalityMin", f"{f.directionality.min():.2f}")
    m("FlipRateAllPct", f"{100*a_all.changed_rate:.1f}")
    m("FlipRateInclUnmitPct", f"{100*a_inc.changed_rate:.1f}")
    m("WinnerScope", "the three mitigated methods")
    m("HeldOutDelta", f"{a_inc.delta_heldout:+.4f}")
    m("HeldOutLo", f"{a_inc.ci_lo:+.4f}"); m("HeldOutHi", f"{a_inc.ci_hi:+.4f}")
    m("HeldOutClusterLo", f"{a_inc.cluster_lo:+.4f}"); m("HeldOutClusterHi", f"{a_inc.cluster_hi:+.4f}")
    m("TiePracticalAllPct", f"{100*a_inc.tie_practical_all:.1f}")
    m("TiePracticalChangedPct", f"{100*a_inc.tie_practical_changed:.1f}")
    m("TieStatAllPct", f"{100*a_inc.tie_statistical_all:.1f}")
    m("BudgetMaxDev", f"{tot['budget_max_rel_dev_pct']:.4f}")
    m("CollisionCount", f"{tot['collisions']}")
    m("CompilationCellsChecked", f"{comp['cells_checked']:,}")
    m("CompilationViolations", f"{comp['cells_with_multiple_base_circuits']}")
    m("NumCellsR", f"{tot['cells']:,}"); m("TotalShotsR", f"{tot['total_shots']:,}")
    m("CoreHoursR", f"{tot['wall_clock_core_hours']:.2f}")
    (TAB/"macros.tex").write_text("\n".join(L)+"\n")
    print(f"wrote macros.tex ({len(L)} macros)")


if __name__ == "__main__":
    t_instances(); t_f1(); t_bv(); t_endpoint(); t_ties(); macros()
    print("round-3 tables generated")
