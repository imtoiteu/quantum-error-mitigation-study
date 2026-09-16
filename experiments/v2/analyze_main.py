"""Main-study analysis, exactly as specified in docs/main-study-protocol.md S6.

Paired-on-(instance,seed) comparisons; Wilcoxon signed-rank (primary) + paired t
(secondary); BCa bootstrap 95% CIs; Benjamini-Hochberg FDR within two declared
families. Absolute effects always reported with the problem scale; ratios never alone.

Outputs: results/v2/processed/*.csv, figures/*.pdf|.png, and a machine-readable
claims table used to build CLAIM_EVIDENCE.csv.
"""
from __future__ import annotations
import json, sys, pathlib, itertools
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW, PROC, FIGS = ROOT/"results/v2/raw", ROOT/"results/v2/processed", ROOT/"figures"
PROC.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)

# Validated categorical palette (scripts/validate_palette.js, light mode ALL PASS).
COLOR = {"none":"#2a78d6","zne":"#eb6834","rem":"#1baf7a","zne_rem":"#eda100"}
MARK  = {"none":"o","zne":"s","rem":"^","zne_rem":"D"}
LABEL = {"none":"unmitigated","zne":"ZNE","rem":"REM","zne_rem":"ZNE+REM"}
ORDER = ["none","zne","rem","zne_rem"]
MITIG = ["zne","rem","zne_rem"]
NOISE_ORDER = ["ideal","dev_lagos","dev_algiers"]
NOISE_LABEL = {"ideal":"ideal (no noise)","dev_lagos":"dev_lagos (readout-dominated)",
               "dev_algiers":"dev_algiers (gate-dominated)"}
RNG = np.random.default_rng(20260916)
DELTA_RATIO = 0.01     # declared practical-effect threshold, approximation-ratio units


def load(name):
    p = RAW/f"{name}.jsonl"
    rows=[json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    df=pd.DataFrame(rows)
    for k in ("total_shots","circuit_shots","calibration_shots","circuit_executions","calibration_executions"):
        df[k]=df["cost"].apply(lambda c,k=k: c.get(k,0))
    return df


def bca_ci(x, alpha=0.05, n_boot=10000):
    x=np.asarray(x,float); n=len(x)
    if n<3 or np.allclose(x,x[0]): return (float(np.mean(x)),)*2
    th=np.mean(x)
    idx=RNG.integers(0,n,size=(n_boot,n)); boots=x[idx].mean(axis=1)
    z0=stats.norm.ppf((np.sum(boots<th)+0.5)/(n_boot+1))
    jk=np.array([np.mean(np.delete(x,i)) for i in range(n)]); jm=jk.mean()
    num=np.sum((jm-jk)**3); den=6*(np.sum((jm-jk)**2)**1.5)
    a=num/den if den!=0 else 0.0
    def endp(q):
        zq=stats.norm.ppf(q); adj=z0+(z0+zq)/(1-a*(z0+zq))
        return float(np.percentile(boots,100*stats.norm.cdf(adj)))
    return endp(alpha/2), endp(1-alpha/2)


def bh(pvals):
    p=np.asarray(pvals,float); m=len(p); o=np.argsort(p); r=np.empty(m)
    adj=p[o]*m/np.arange(1,m+1); adj=np.minimum.accumulate(adj[::-1])[::-1]
    r[o]=np.clip(adj,0,1); return r


def paired(a, b):
    """Return stats for paired difference a-b."""
    d=np.asarray(a,float)-np.asarray(b,float)
    lo,hi=bca_ci(d)
    try: w=stats.wilcoxon(d, zero_method="wilcox", alternative="two-sided").pvalue
    except Exception: w=np.nan
    t=stats.ttest_rel(a,b).pvalue if len(d)>1 else np.nan
    return dict(n=len(d), mean_diff=float(d.mean()), sd_diff=float(d.std(ddof=1)) if len(d)>1 else np.nan,
                ci_lo=lo, ci_hi=hi, p_wilcoxon=float(w), p_ttest=float(t),
                median_diff=float(np.median(d)))


def style(ax):
    ax.grid(True, lw=.5, alpha=.25, color="#9a9a94"); ax.set_axisbelow(True)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color("#52514e"); ax.spines[s].set_linewidth(.8)
    ax.tick_params(colors="#52514e", labelsize=8)

def save(fig, name):
    for ext in ("pdf","png"):
        fig.savefig(FIGS/f"{name}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ======================================================================= F1
def family1(df):
    """Implementation impact: paired legacy vs v2 at the legacy budget."""
    piv=df[df.budget==6000].pivot_table(
        index=["instance","noise","method","seed"],columns="impl",
        values="estimation_error_abs").dropna()
    rows=[]
    for (noise,method),g in piv.groupby(level=[1,2]):
        st=paired(g["legacy"].values, g["v2"].values)
        ad=np.abs(g["legacy"].values-g["v2"].values)
        lo,hi=bca_ci(ad)
        rows.append(dict(family="F1", noise=noise, method=method, **st,
                         mean_abs_disagreement=float(ad.mean()),
                         abs_ci_lo=lo, abs_ci_hi=hi, median_abs=float(np.median(ad))))
    f1=pd.DataFrame(rows)
    f1["p_adj_BH"]=bh(f1.p_wilcoxon.fillna(1.0))
    f1["significant_BH_0.05"]=f1["p_adj_BH"]<0.05
    f1.to_csv(PROC/"F1_implementation_impact.csv",index=False)

    # best-method disagreement rate
    w=df[(df.budget==6000)&(df.method!="none")].pivot_table(
        index=["instance","noise","seed"],columns=["impl","method"],
        values="estimation_error_abs").dropna()
    recs=[]
    for idx,row in w.iterrows():
        bl=min(MITIG,key=lambda k:row[("legacy",k)]); bv=min(MITIG,key=lambda k:row[("v2",k)])
        # Decision-relevant cost: having followed the defective recommendation, how much
        # worse is that method's TRUE (corrected) error than the truly best method's?
        regret = float(row[("v2",bl)] - row[("v2",bv)])
        recs.append(dict(instance=idx[0],noise=idx[1],seed=idx[2],best_legacy=bl,best_v2=bv,
                         flip=bl!=bv, regret=regret,
                         true_err_best=float(row[("v2",bv)]),
                         true_err_recommended=float(row[("v2",bl)])))
    fl=pd.DataFrame(recs); fl.to_csv(PROC/"F1_best_method_flips.csv",index=False)
    summ=fl.groupby("noise").flip.agg(["size","sum","mean"]).rename(
        columns={"size":"n_cells","sum":"n_flipped","mean":"flip_rate"})
    summ.loc["ALL"]=[len(fl),fl.flip.sum(),fl.flip.mean()]
    # Regret: mean excess TRUE error incurred by following the defective recommendation.
    # Reported alongside the flip rate because a flip between near-identical methods is cheap.
    reg=fl.groupby("noise").regret.agg(["mean","median","max"]).rename(
        columns={"mean":"mean_regret","median":"median_regret","max":"max_regret"})
    reg.loc["ALL"]=[fl.regret.mean(),fl.regret.median(),fl.regret.max()]
    flipped=fl[fl.flip]
    regf=flipped.groupby("noise").regret.agg(["mean","median","max"]).rename(
        columns={"mean":"mean_regret_flipped","median":"median_regret_flipped","max":"max_regret_flipped"})
    if len(flipped):
        regf.loc["ALL"]=[flipped.regret.mean(),flipped.regret.median(),flipped.regret.max()]
    summ=summ.join(reg).join(regf)
    summ["mean_true_err_best"]=fl.groupby("noise").true_err_best.mean().reindex(summ.index)
    summ.loc["ALL","mean_true_err_best"]=fl.true_err_best.mean()
    summ.to_csv(PROC/"F1_flip_rate.csv")
    return f1, fl, summ


# ======================================================================= F2
def family2(df):
    """Corrected method-vs-unmitigated at matched budget, paired on (instance,seed)."""
    v2=df[df.impl=="v2"]
    piv=v2.pivot_table(index=["instance","noise","budget","seed"],columns="method",
                       values="estimation_error_abs").dropna()
    cmax=v2.groupby("instance").exact_max_cut.first()
    rows=[]
    for (noise,budget),g in piv.groupby(level=[1,2]):
        scale=float(cmax.reindex(g.index.get_level_values(0)).mean())
        for m in MITIG:
            st=paired(g[m].values, g["none"].values)
            rows.append(dict(family="F2", noise=noise, budget=budget, method=m, **st,
                             mean_err_method=float(g[m].mean()), mean_err_none=float(g["none"].mean()),
                             ratio=float(g[m].mean()/g["none"].mean()) if g["none"].mean() else np.nan,
                             mean_Cmax=scale,
                             effect_in_ratio_units=float(st["mean_diff"]/scale),
                             practically_meaningful=bool(abs(st["mean_diff"]/scale)>=DELTA_RATIO)))
    f2=pd.DataFrame(rows)
    f2["p_adj_BH"]=bh(f2.p_wilcoxon.fillna(1.0))
    f2["significant_BH_0.05"]=f2["p_adj_BH"]<0.05
    f2["verdict"]=np.where(~f2["significant_BH_0.05"],"no resolvable difference",
                   np.where(f2.mean_diff<0,
                            np.where(f2.practically_meaningful,"helps (practically meaningful)","helps (below delta)"),
                            np.where(f2.practically_meaningful,"harms (practically meaningful)","harms (below delta)")))
    f2.to_csv(PROC/"F2_method_vs_unmitigated.csv",index=False)
    return f2, piv


def costs(df):
    v2=df[df.impl=="v2"]
    c=v2.groupby("method").agg(
        mean_total_shots=("total_shots","mean"), mean_circuit_shots=("circuit_shots","mean"),
        mean_calibration_shots=("calibration_shots","mean"),
        mean_circuit_exec=("circuit_executions","mean"),
        mean_calibration_exec=("calibration_executions","mean"),
        mean_wall_s=("wall_clock_s","mean")).round(3)
    dev=v2.groupby(["budget"]).total_shots.agg(["min","max"])
    dev["rel_dev"]=(dev["max"]-dev["min"])/dev["max"]
    c.to_csv(PROC/"cost_accounting.csv"); dev.to_csv(PROC/"budget_match_check.csv")
    tot=dict(total_shots=int(df.total_shots.sum()),
             circuit_shots=int(df.circuit_shots.sum()),
             calibration_shots=int(df.calibration_shots.sum()),
             circuit_executions=int(df.circuit_executions.sum()),
             calibration_executions=int(df.calibration_executions.sum()),
             scoring_shots=0, wall_clock_core_hours=float(df.wall_clock_s.sum()/3600),
             cells=int(len(df)))
    (PROC/"total_cost.json").write_text(json.dumps(tot,indent=2))
    return c, dev, tot


# ======================================================================= figures
def fig_impl_impact(f1, fl, flip_summ, df):
    piv=df[df.budget==6000].pivot_table(index=["instance","noise","method","seed"],
                                        columns="impl",values="estimation_error_abs").dropna()
    fig,axes=plt.subplots(1,3,figsize=(11.2,3.5),gridspec_kw={"width_ratios":[1.25,1.0,0.85]})
    # (a) paired scatter
    ax=axes[0]; style(ax)
    for m in MITIG:
        g=piv.xs(m,level=2)
        ax.scatter(g["v2"],g["legacy"],s=11,alpha=.55,color=COLOR[m],marker=MARK[m],
                   label=LABEL[m],linewidths=0)
    lim=[0,max(piv.max().max(),1)*1.03]
    ax.plot(lim,lim,color="#52514e",lw=1,ls="--",zorder=1)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("estimation error, corrected code",fontsize=8.5)
    ax.set_ylabel("estimation error, defective code",fontsize=8.5)
    ax.set_title("(a) same seed, same configuration",fontsize=9)
    ax.legend(frameon=False,fontsize=7.5,loc="lower right")
    # (b) |disagreement| by method and noise
    ax=axes[1]; style(ax)
    xs=np.arange(len(MITIG)); w=0.36
    for k,noise in enumerate(["dev_lagos","dev_algiers"]):
        sub=f1[f1.noise==noise].set_index("method").reindex(MITIG)
        ax.bar(xs+(k-0.5)*w, sub.mean_abs_disagreement, width=w*0.92,
               color=["#2a78d6","#eb6834"][k], label=NOISE_LABEL[noise].split(" (")[0], zorder=3)
        ax.errorbar(xs+(k-0.5)*w, sub.mean_abs_disagreement,
                    yerr=[sub.mean_abs_disagreement-sub.abs_ci_lo, sub.abs_ci_hi-sub.mean_abs_disagreement],
                    fmt="none",ecolor="#0b0b0b",elinewidth=1,capsize=2.5,zorder=4)
    ax.set_xticks(xs); ax.set_xticklabels([LABEL[m] for m in MITIG],fontsize=8)
    ax.set_ylabel("mean |disagreement| (cut value)",fontsize=8.5)
    ax.set_title("(b) magnitude of disagreement",fontsize=9)
    ax.legend(frameon=False,fontsize=7.5)
    # (c) best-method flip rate
    ax=axes[2]; style(ax)
    s=flip_summ.drop(index="ALL")
    xs=np.arange(len(s))
    ax.bar(xs,s.flip_rate*100,width=.55,color="#1baf7a",zorder=3)
    for i,v in enumerate(s.flip_rate*100):
        ax.text(i,v+1.5,f"{v:.0f}%",ha="center",fontsize=8,color="#0b0b0b")
    ax.set_xticks(xs); ax.set_xticklabels([i.replace("dev_","") for i in s.index],fontsize=8)
    ax.set_ylim(0,105); ax.set_ylabel("cells where the best method changes (%)",fontsize=8.5)
    ax.set_title("(c) conclusion flips",fontsize=9)
    fig.suptitle("Effect of the measurement-mapping defect (simulator only; QAOA p=1, 6 instances, budget 6000 shots)",
                 fontsize=10)
    fig.tight_layout(rect=[0,0,1,0.93]); save(fig,"fig1_implementation_impact")


def fig_method_comparison(f2, df):
    v2=df[df.impl=="v2"]
    noises=[n for n in NOISE_ORDER if n in set(v2.noise)]
    budgets=sorted(v2.budget.unique())
    fig,axes=plt.subplots(1,len(noises),figsize=(3.6*len(noises),3.4),sharey=False,squeeze=False)
    for j,noise in enumerate(noises):
        ax=axes[0][j]; style(ax)
        for m in ORDER:
            s=(v2[(v2.noise==noise)&(v2.method==m)].groupby("budget")
               .estimation_error_abs.agg(["mean","count","std"]).reindex(budgets))
            ci=1.96*s["std"]/np.sqrt(s["count"])
            ax.plot(budgets,s["mean"],color=COLOR[m],marker=MARK[m],ms=5,lw=1.8,label=LABEL[m],zorder=3)
            ax.fill_between(budgets,s["mean"]-ci,s["mean"]+ci,color=COLOR[m],alpha=.15,lw=0)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xticks(budgets); ax.set_xticklabels([f"{b//1000}k" if b>=1000 else str(b) for b in budgets],fontsize=8)
        ax.set_xticks([],minor=True); ax.tick_params(axis="y",which="minor",labelleft=False)
        ax.set_title(NOISE_LABEL[noise],fontsize=9)
        ax.set_xlabel("total shots per estimate (matched across methods)",fontsize=8.5)
        if j==0: ax.set_ylabel("mean estimation error (cut value)",fontsize=8.5)
    axes[0][0].legend(frameon=False,fontsize=8,loc="best")
    fig.suptitle("Corrected budget-matched comparison (simulator only; shaded = 95% CI of the mean over 6 instances x 30 seeds)",
                 fontsize=10)
    fig.tight_layout(rect=[0,0,1,0.92]); save(fig,"fig2_method_comparison")


def fig_per_instance(df):
    v2=df[(df.impl=="v2")&(df.budget==6000)]
    insts=sorted(v2.instance.unique()); noises=[n for n in NOISE_ORDER if n in set(v2.noise)]
    fig,axes=plt.subplots(1,len(noises),figsize=(3.6*len(noises),3.5),squeeze=False)
    for j,noise in enumerate(noises):
        ax=axes[0][j]; style(ax)
        xs=np.arange(len(insts)); w=0.2
        for k,m in enumerate(ORDER):
            s=(v2[(v2.noise==noise)&(v2.method==m)].groupby("instance")
               .estimation_error_abs.mean().reindex(insts))
            ax.bar(xs+(k-1.5)*w,s.values,width=w*0.9,color=COLOR[m],label=LABEL[m],zorder=3)
        ax.set_xticks(xs); ax.set_xticklabels(insts,fontsize=7.5,rotation=30,ha="right")
        ax.set_title(NOISE_LABEL[noise],fontsize=9)
        if j==0: ax.set_ylabel("mean estimation error (cut value)",fontsize=8.5)
    axes[0][0].legend(frameon=False,fontsize=7.5)
    fig.suptitle("Per-instance heterogeneity at budget 6000 (simulator only; 30 seeds per bar)",fontsize=10)
    fig.tight_layout(rect=[0,0,1,0.92]); save(fig,"fig3_per_instance")


def main():
    df=load("main_study")
    print(f"loaded {len(df)} cells; impls={sorted(df.impl.unique())}")
    f1,fl,flip=family1(df)
    f2,piv=family2(df)
    c,dev,tot=costs(df)
    print("\n=== F1 implementation impact (BH-adjusted) ===")
    print(f1[["noise","method","n","mean_abs_disagreement","abs_ci_lo","abs_ci_hi",
              "mean_diff","p_wilcoxon","p_adj_BH","significant_BH_0.05"]].round(4).to_string(index=False))
    print("\n=== F1 best-method flip rate ===");  print(flip.round(4).to_string())
    print("\n=== F2 method vs unmitigated (BH-adjusted) ===")
    print(f2[["noise","budget","method","n","mean_err_none","mean_err_method","mean_diff",
              "ci_lo","ci_hi","effect_in_ratio_units","p_adj_BH","verdict"]].round(4).to_string(index=False))
    print("\n=== cost accounting ===");  print(c.to_string())
    print("\n=== budget match ===");     print(dev.to_string())
    print("\n=== total study cost ==="); print(json.dumps(tot,indent=2))
    fig_impl_impact(f1,fl,flip,df); fig_method_comparison(f2,df); fig_per_instance(df)
    print("\nfigures written to figures/")

if __name__=="__main__":
    main()
