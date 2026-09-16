r"""Generate every LaTeX table in the manuscript from processed results.

No number in the manuscript is typed by hand: each table below is written to
manuscript/tables/*.tex by this script and \input{} into the paper.
"""
from __future__ import annotations
import json, pathlib, sys
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT/"results/v2/processed"; TAB = ROOT/"manuscript/tables"; TAB.mkdir(parents=True, exist_ok=True)
LABEL = {"none":"unmitigated","zne":"ZNE","rem":"REM","zne_rem":"ZNE+REM"}
VERDICT_SHORT = {
    "helps (practically meaningful)": "helps$^{\\ast}$",
    "helps (below delta)":            "helps",
    "harms (practically meaningful)": "harms$^{\\ast}$",
    "harms (below delta)":            "harms",
    "no resolvable difference":       "---",
}
NL = {"ideal":"ideal","dev_lagos":"\\texttt{dev\\_lagos}","dev_algiers":"\\texttt{dev\\_algiers}"}


def sci(x, sig=1):
    """LaTeX scientific notation, e.g. 3.9e-02 -> $3.9\\times10^{-2}$; tiny -> $<10^{-15}$."""
    import math
    if x is None: return "--"
    x = float(x)
    if x <= 0: return "$<10^{-15}$"
    e = math.floor(math.log10(x)); m = x / 10**e
    if e >= -2 and e <= 0:
        return f"${x:.3f}$"
    return f"${m:.{sig}f}\\times10^{{{e}}}$"

def w(name, s):
    (TAB/name).write_text(s); print("wrote", name)

def t1_instances():
    refs=json.loads((ROOT/"configs/v2/references.json").read_text())
    rows=[]
    for k,v in refs.items():
        rows.append(f"\\texttt{{{k.replace('_','\\_')}}} & {len(v['edges'])} & {v['exact_max_cut']} & "
                    f"{v['ansatz_reference_best_known']:.4f} & {v['approx_ratio_at_reference']:.4f} & "
                    f"{100*v['frac_starts_within_1e-6_of_best']:.0f}\\% \\\\")
    w("tab_instances.tex",
      "\\begin{tabular}{@{}lrrrrr@{}}\n\\toprule\nInstance & $|E|$ & $C_{\\max}$ & "
      "best $\\langle C\\rangle$ & ratio & at best \\\\\n\\midrule\n"
      + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

def t2_f1():
    f1=pd.read_csv(PROC/"F1_implementation_impact.csv")
    flip=pd.read_csv(PROC/"F1_flip_rate.csv",index_col=0)
    rows=[]
    for _,r in f1.sort_values(["noise","method"]).iterrows():
        rows.append(f"{NL[r.noise]} & {LABEL[r.method]} & {int(r.n)} & {r.mean_abs_disagreement:.3f} & "
                    f"[{r.abs_ci_lo:.3f}, {r.abs_ci_hi:.3f}] & {r.mean_diff:+.3f} & "
                    f"{sci(r['p_adj_BH'])} \\\\")
    body=("\\begin{tabular}{@{}llrrlrr@{}}\n\\toprule\nNoise & Method & $n$ & mean $|D|$ & 95\\% CI & "
          "mean signed & $p_{\\mathrm{BH}}$ \\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    w("tab_f1.tex", body)
    fr=[]
    for idx,r in flip.iterrows():
        nm = "all" if idx=="ALL" else NL.get(idx,idx).replace("dev\\_","")
        fr.append(f"{nm} & {int(r.n_cells)} & {int(r.n_flipped)} & {100*r.flip_rate:.1f}\\% & "
                  f"{r.mean_regret_flipped:.3f} & {r.mean_true_err_best:.3f} \\\\")
    w("tab_flip.tex",
      "\\begin{tabular}{@{}lrrrrr@{}}\n\\toprule\nNoise & cells & flips & rate & "
      "regret & best \\\\\n\\midrule\n" + "\n".join(fr) +
      "\n\\bottomrule\n\\end{tabular}\n")

def t3_f2():
    f2=pd.read_csv(PROC/"F2_method_vs_unmitigated.csv")
    rows=[]
    for _,r in f2.sort_values(["noise","budget","method"]).iterrows():
        rows.append(f"{NL[r.noise]} & {int(r.budget)} & {LABEL[r.method]} & {r.mean_err_none:.4f} & "
                    f"{r.mean_err_method:.4f} & {r.mean_diff:+.4f} & [{r.ci_lo:+.4f}, {r.ci_hi:+.4f}] & "
                    f"{r.effect_in_ratio_units:+.4f} & {sci(r['p_adj_BH'])} & {VERDICT_SHORT[r.verdict]} \\\\")
    w("tab_f2.tex",
      "\\begin{tabular}{@{}llrrrrlrrl@{}}\n\\toprule\nNoise & $B$ & Method & err$_{\\text{unmit}}$ & "
      "err$_{\\text{method}}$ & $\\Delta$ & 95\\% CI & $\\Delta/C_{\\max}$ & $p_{\\mathrm{BH}}$ & verdict \\\\\n"
      "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

def t4_cost():
    c=pd.read_csv(PROC/"cost_accounting.csv",index_col=0)
    tot=json.loads((PROC/"total_cost.json").read_text())
    rows=[]
    for m in ["none","zne","rem","zne_rem"]:
        if m not in c.index: continue
        r=c.loc[m]
        rows.append(f"{LABEL[m]} & {r.mean_total_shots:,.0f} & {r.mean_circuit_shots:,.0f} & "
                    f"{r.mean_calibration_shots:,.0f} & {r.mean_circuit_exec:.1f} & "
                    f"{r.mean_calibration_exec:.1f} & {r.mean_wall_s:.2f} \\\\")
    w("tab_cost.tex",
      "\\begin{tabular}{@{}lrrrrrr@{}}\n\\toprule\nMethod & total shots & circuit & calibration & "
      "circ.\\ exec. & cal.\\ exec. & wall (s) \\\\\n\\midrule\n" + "\n".join(rows) +
      "\n\\bottomrule\n\\end{tabular}\n")
    w("tab_totalcost.tex",
      "\\begin{tabular}{@{}lr@{}}\n\\toprule\nQuantity & Value \\\\\n\\midrule\n"
      f"Evaluation cells & {tot['cells']:,} \\\\\n"
      f"Total shots (circuit) & {tot['circuit_shots']:,} \\\\\n"
      f"Total shots (calibration) & {tot['calibration_shots']:,} \\\\\n"
      f"Total shots (all) & {tot['total_shots']:,} \\\\\n"
      f"Offline scoring shots & {tot['scoring_shots']:,} (exact statevector) \\\\\n"
      f"Circuit executions & {tot['circuit_executions']:,} \\\\\n"
      f"Calibration executions & {tot['calibration_executions']:,} \\\\\n"
      f"CPU wall-clock & {tot['wall_clock_core_hours']:.2f} core-hours \\\\\n"
      "\\bottomrule\n\\end{tabular}\n")



def macros():
    """Every inline number in the manuscript, as LaTeX macros generated from data."""
    f1=pd.read_csv(PROC/"F1_implementation_impact.csv")
    flip=pd.read_csv(PROC/"F1_flip_rate.csv",index_col=0)
    f2=pd.read_csv(PROC/"F2_method_vs_unmitigated.csv")
    tot=json.loads((PROC/"total_cost.json").read_text())
    dev=pd.read_csv(PROC/"budget_match_check.csv",index_col=0)
    L=[]
    def m(k,v): L.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    m("NumCells", f"{tot['cells']:,}")
    m("TotalShots", f"{tot['total_shots']:,}")
    m("CircuitShots", f"{tot['circuit_shots']:,}")
    m("CalibShots", f"{tot['calibration_shots']:,}")
    m("TotalExec", f"{tot['circuit_executions']+tot['calibration_executions']:,}")
    m("CoreHours", f"{tot['wall_clock_core_hours']:.1f}")
    m("BudgetMaxDev", f"{100*dev['rel_dev'].max():.4f}")
    m("FlipRateAll", f"{100*flip.loc['ALL','flip_rate']:.0f}")
    m("FlipNAll", f"{int(flip.loc['ALL','n_cells'])}")
    m("RegretAll", f"{flip.loc['ALL','mean_regret_flipped']:.3f}")
    m("BestErrAll", f"{flip.loc['ALL','mean_true_err_best']:.3f}")
    for nz in ("dev_lagos","dev_algiers"):
        if nz in flip.index:
            tag=nz.replace('dev_','').capitalize()
            m("Regret"+tag, f"{flip.loc[nz,'mean_regret_flipped']:.3f}")
            m("BestErr"+tag, f"{flip.loc[nz,'mean_true_err_best']:.3f}")
    for nz in ("dev_lagos","dev_algiers"):
        if nz in flip.index:
            m("FlipRate"+nz.replace('dev_','').capitalize(), f"{100*flip.loc[nz,'flip_rate']:.0f}")
    for _,r in f1.iterrows():
        tag=r.method.replace('_','')+r.noise.replace('dev_','').capitalize()
        m("DisA"+tag, f"{r.mean_abs_disagreement:.3f}")
        m("DisACIlo"+tag, f"{r.abs_ci_lo:.3f}"); m("DisACIhi"+tag, f"{r.abs_ci_hi:.3f}")
        m("DisAP"+tag, sci(r['p_adj_BH']))
    m("FONemaxP", sci(f1['p_adj_BH'].max()))
    m("FONeminDis", f"{f1.mean_abs_disagreement.min():.3f}")
    m("FONemaxDis", f"{f1.mean_abs_disagreement.max():.3f}")
    # F2 headline counts
    m("FTwoNTests", f"{len(f2)}")
    m("FTwoHelpsPM", f"{int((f2.verdict=='helps (practically meaningful)').sum())}")
    m("FTwoHarmsPM", f"{int((f2.verdict=='harms (practically meaningful)').sum())}")
    m("FTwoNoDiff", f"{int((f2.verdict=='no resolvable difference').sum())}")
    m("FTwoBelowDelta", f"{int(f2.verdict.str.contains('below delta').sum())}")
    for nz in f2.noise.unique():
        sub=f2[f2.noise==nz]
        m("BestMethod"+nz.replace('dev_','').replace('ideal','Ideal').capitalize(),
          LABEL[sub.loc[sub.mean_err_method.idxmin(),'method']])
    (TAB/"macros.tex").write_text("\n".join(L)+"\n")
    print(f"wrote macros.tex with {len(L)} generated macros")


if __name__=="__main__":
    t1_instances(); t2_f1(); t3_f2(); t4_cost(); macros()
    print("all tables generated from processed results")
