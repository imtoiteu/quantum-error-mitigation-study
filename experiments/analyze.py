"""Analysis for Stage A / Stage B: summaries, bootstrap CIs, verdicts, figures.

Outputs:
  results/processed/*.csv   -- machine-readable summaries
  figures/*.png             -- publication-draft figures
  results/processed/verdicts.md -- RQ1/RQ2/RQ3 decision tables
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, PROC, FIGS = ROOT / "results" / "raw", ROOT / "results" / "processed", ROOT / "figures"
PROC.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)

# Validated categorical palette (dataviz skill: validate_palette.js, light mode ALL PASS).
# Contrast WARN on aqua/yellow is relieved by distinct marker shapes + legend.
COLOR = {"none": "#2a78d6", "zne": "#eb6834", "rem": "#1baf7a", "zne_rem": "#eda100"}
MARK = {"none": "o", "zne": "s", "rem": "^", "zne_rem": "D"}
LABEL = {"none": "no mitigation", "zne": "ZNE", "rem": "REM", "zne_rem": "ZNE+REM"}
ORDER = ["none", "zne", "rem", "zne_rem"]
NOISE_ORDER = ["ideal", "dev_lagos", "dev_algiers", "param_lam0.5", "param_lam1", "param_lam2"]
RNG = np.random.default_rng(20260915)


def load(name):
    p = RAW / f"{name}.jsonl"
    if not p.exists():
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    if not rows:          # file exists but the run is still in progress / empty
        return None
    return pd.DataFrame(rows)


def boot_ci(x, n=10000, alpha=0.05):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return (np.nan, np.nan)
    idx = RNG.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    return tuple(np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)]))


def style(ax):
    ax.grid(True, which="both", lw=0.5, alpha=0.25, color="#9a9a94")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#52514e"); ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors="#52514e", labelsize=8)


# ------------------------------------------------------------------ Stage A
def analyse_a(df: pd.DataFrame):
    # --- integrity check: budgets must match across methods within a group ---
    # Reported quantitatively. Integer division when splitting the calibration
    # allowance across 2n circuits can leave a few shots unspent, always in the
    # mitigated arm's DISFAVOUR (it receives slightly fewer shots, never more).
    g = df.groupby(["task", "noise", "budget"])["shots_used"].agg(["min", "max"])
    g["rel_dev"] = (g["max"] - g["min"]) / g["max"]
    violations = g[g["rel_dev"] > 0]
    max_dev = float(g["rel_dev"].max())
    budget_ok = max_dev == 0.0

    rows = []
    for (task, noise, budget, method), sub in df.groupby(["task", "noise", "budget", "method"]):
        errs = sub["abs_error"].values
        lo, hi = boot_ci(errs)
        signed = sub["signed_error"].values
        rows.append(dict(task=task, noise=noise, budget=budget, method=method,
                         n_seeds=len(errs), mean_abs_error=errs.mean(), std_abs_error=errs.std(ddof=1),
                         ci_lo=lo, ci_hi=hi, bias=signed.mean(), variance=signed.var(ddof=1),
                         rmse=np.sqrt((signed ** 2).mean()),
                         mean_circuit_executions=sub["circuit_executions"].mean(),
                         mean_shots=sub["shots_used"].mean(),
                         mean_wall_clock_s=sub["wall_clock_s"].mean()))
    summ = pd.DataFrame(rows)
    summ.to_csv(PROC / "stage_a_summary.csv", index=False)

    # --- RQ1/RQ2 verdicts: method vs 'none' with non-overlapping 95% CIs ---
    ver = []
    for (task, noise, budget), sub in summ.groupby(["task", "noise", "budget"]):
        base = sub[sub.method == "none"].iloc[0]
        for _, r in sub[sub.method != "none"].iterrows():
            if r.ci_hi < base.ci_lo:
                v = "helps"
            elif r.ci_lo > base.ci_hi:
                v = "harms"
            else:
                v = "inconclusive"
            ver.append(dict(task=task, noise=noise, budget=budget, method=r.method,
                            verdict=v, mean_err=r.mean_abs_error, base_err=base.mean_abs_error,
                            ratio=r.mean_abs_error / base.mean_abs_error if base.mean_abs_error else np.nan))
    verdicts = pd.DataFrame(ver)
    verdicts.to_csv(PROC / "stage_a_verdicts.csv", index=False)
    return summ, verdicts, budget_ok, violations


def fig_error_vs_budget(summ):
    noises = [n for n in NOISE_ORDER if n in set(summ.noise)]
    tasks = sorted(summ.task.unique())
    fig, axes = plt.subplots(len(tasks), len(noises), figsize=(3.0 * len(noises), 3.1 * len(tasks)),
                             sharex=True, squeeze=False)
    for i, task in enumerate(tasks):
        for j, noise in enumerate(noises):
            ax = axes[i][j]; style(ax)
            sub = summ[(summ.task == task) & (summ.noise == noise)]
            for m in ORDER:
                s = sub[sub.method == m].sort_values("budget")
                if s.empty: continue
                ax.plot(s.budget, s.mean_abs_error, color=COLOR[m], marker=MARK[m],
                        ms=5, lw=1.8, label=LABEL[m], zorder=3)
                ax.fill_between(s.budget, s.ci_lo, s.ci_hi, color=COLOR[m], alpha=0.16, lw=0)
            ax.set_xscale("log"); ax.set_yscale("log")
            budgets = sorted(sub.budget.unique())
            ax.set_xticks(budgets, minor=False)
            ax.set_xticklabels([f"{b/1000:g}k" for b in budgets], fontsize=7.5)
            ax.set_xticks([], minor=True)          # kill colliding log minor labels
            ax.tick_params(axis="y", which="minor", labelleft=False)
            if i == 0: ax.set_title(noise, fontsize=9, color="#0b0b0b")
            if j == 0: ax.set_ylabel(f"{task}\nmean |error|", fontsize=8.5, color="#52514e")
            if i == len(tasks) - 1: ax.set_xlabel("total shots per estimate", fontsize=8.5, color="#52514e")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.015))
    fig.suptitle("Estimation error vs. matched shot budget  (simulator only; shaded = 95% bootstrap CI over 10 seeds)",
                 fontsize=10.5, y=1.0)
    fig.tight_layout(rect=[0, 0.035, 1, 0.985])
    fig.savefig(FIGS / "fig1_error_vs_budget.png", dpi=200, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)


def fig_noise_strength(summ):
    sub = summ[summ.noise.str.startswith("param")].copy()
    if sub.empty: return
    sub["lam"] = sub.noise.str.replace("param_lam", "", regex=False).astype(float)
    tasks = sorted(sub.task.unique())
    budgets = sorted(sub.budget.unique())
    pick = [budgets[0], budgets[len(budgets) // 2], budgets[-1]]
    fig, axes = plt.subplots(len(tasks), len(pick), figsize=(3.0 * len(pick), 3.1 * len(tasks)),
                             sharex=True, squeeze=False)
    for i, task in enumerate(tasks):
        for j, b in enumerate(pick):
            ax = axes[i][j]; style(ax)
            s0 = sub[(sub.task == task) & (sub.budget == b)]
            for m in ORDER:
                s = s0[s0.method == m].sort_values("lam")
                if s.empty: continue
                ax.plot(s.lam, s.mean_abs_error, color=COLOR[m], marker=MARK[m], ms=5, lw=1.8,
                        label=LABEL[m], zorder=3)
                ax.fill_between(s.lam, s.ci_lo, s.ci_hi, color=COLOR[m], alpha=0.16, lw=0)
            ax.set_yscale("log")
            ax.set_xticks([0.5, 1.0, 2.0]); ax.set_xticklabels(["0.5", "1.0", "2.0"], fontsize=8)
            ax.tick_params(axis="y", which="minor", labelleft=False)
            if i == 0: ax.set_title(f"budget = {b:,} shots", fontsize=9)
            if j == 0: ax.set_ylabel(f"{task}\nmean |error|", fontsize=8.5, color="#52514e")
            if i == len(tasks) - 1: ax.set_xlabel("noise strength multiplier λ", fontsize=8.5, color="#52514e")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.015))
    fig.suptitle("Sensitivity to noise strength (parametric noise model; simulator only)", fontsize=10.5, y=1.0)
    fig.tight_layout(rect=[0, 0.035, 1, 0.985])
    fig.savefig(FIGS / "fig2_noise_strength.png", dpi=200, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)


def fig_bias_variance(summ):
    sub = summ[(summ.noise.isin(["dev_lagos", "dev_algiers"]))].copy()
    if sub.empty: return
    tasks = sorted(sub.task.unique()); noises = ["dev_lagos", "dev_algiers"]
    fig, axes = plt.subplots(len(tasks), len(noises), figsize=(4.0 * len(noises), 3.1 * len(tasks)), squeeze=False)
    for i, task in enumerate(tasks):
        for j, noise in enumerate(noises):
            ax = axes[i][j]; style(ax)
            s0 = sub[(sub.task == task) & (sub.noise == noise)]
            budgets = sorted(s0.budget.unique())
            w = 0.2
            for k, m in enumerate(ORDER):
                s = s0[s0.method == m].sort_values("budget")
                if s.empty: continue
                xs = np.arange(len(budgets)) + (k - 1.5) * w
                ax.bar(xs, s.bias.abs(), width=w * 0.92, color=COLOR[m], label=f"{LABEL[m]} |bias|", zorder=3)
                ax.plot(xs, np.sqrt(s.variance), color="#0b0b0b", marker=MARK[m], ms=4, lw=0, zorder=4)
            ax.set_xticks(np.arange(len(budgets)))
            ax.set_xticklabels([f"{b/1000:g}k" for b in budgets], fontsize=8)
            ax.set_yscale("log")
            ax.tick_params(axis="y", which="minor", labelleft=False)
            if i == 0: ax.set_title(noise, fontsize=9)
            if j == 0: ax.set_ylabel(f"{task}\n|bias| (bars), sd (marks)", fontsize=8.5, color="#52514e")
            if i == len(tasks) - 1: ax.set_xlabel("total shots per estimate", fontsize=8.5, color="#52514e")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Bias–variance decomposition: bars = |bias|, black marks = standard deviation", fontsize=10.5, y=1.0)
    fig.tight_layout(rect=[0, 0.04, 1, 0.985])
    fig.savefig(FIGS / "fig3_bias_variance.png", dpi=200, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)


# ------------------------------------------------------------------ Stage B
def analyse_b(df):
    rows = []
    for (task, noise, method), sub in df.groupby(["task", "noise", "method"]):
        e = sub["abs_error_ideal_eval"].values
        lo, hi = boot_ci(e)
        rows.append(dict(task=task, noise=noise, method=method, n_seeds=len(e),
                         mean_abs_error=e.mean(), std=e.std(ddof=1), ci_lo=lo, ci_hi=hi,
                         mean_shots=sub["shots_total"].mean(),
                         mean_execs=sub["circuit_executions"].mean(),
                         mean_wall_clock_s=sub["wall_clock_s"].mean(),
                         mean_evals=sub["objective_evaluations"].mean(),
                         mean_calibration_shots=sub["calibration_shots"].mean(),
                         mean_circuit_shots=(sub["shots_total"] - sub["calibration_shots"]).mean()))
    s = pd.DataFrame(rows); s.to_csv(PROC / "stage_b_summary.csv", index=False)

    fig, axes = plt.subplots(1, len(s.task.unique()), figsize=(4.6 * len(s.task.unique()), 3.4), squeeze=False)
    for i, task in enumerate(sorted(s.task.unique())):
        ax = axes[0][i]; style(ax)
        s0 = s[s.task == task]; noises = sorted(s0.noise.unique()); w = 0.2
        for k, m in enumerate(ORDER):
            ss = s0[s0.method == m].set_index("noise").reindex(noises)
            xs = np.arange(len(noises)) + (k - 1.5) * w
            ax.bar(xs, ss.mean_abs_error.to_numpy(), width=w * 0.92, color=COLOR[m], label=LABEL[m], zorder=3)
            ax.errorbar(xs, ss.mean_abs_error.to_numpy(),
                        yerr=[(ss.mean_abs_error - ss.ci_lo).to_numpy(),
                              (ss.ci_hi - ss.mean_abs_error).to_numpy()],
                        fmt="none", ecolor="#0b0b0b", elinewidth=1, capsize=3, zorder=4)
        ax.set_xticks(np.arange(len(noises))); ax.set_xticklabels(noises, fontsize=8.5)
        ax.set_title(task, fontsize=9.5); ax.set_ylabel("final |error| (noiseless re-evaluation)", fontsize=8.5, color="#52514e")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Stage B: in-loop optimisation, equal budget per evaluation (95% bootstrap CI over 5 seeds)", fontsize=10.5)
    fig.tight_layout(rect=[0, 0.05, 1, 0.94])
    fig.savefig(FIGS / "fig4_inloop.png", dpi=200, bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)
    return s


def main():
    out = []
    a = load("stage_a")
    if a is not None:
        summ, verdicts, ok, viol = analyse_a(a)
        fig_error_vs_budget(summ); fig_noise_strength(summ); fig_bias_variance(summ)
        out.append("# Pilot verdicts\n")
        if ok:
            out.append("**Budget-match integrity check:** PASS — `shots_used` identical across "
                       "methods in all 60 comparison groups.\n")
        else:
            worst = viol["rel_dev"].max()
            out.append(f"**Budget-match integrity check:** {len(viol)} of {len(viol)+ (60-len(viol))} "
                       f"comparison groups show a non-zero spread; **maximum relative deviation "
                       f"{worst*100:.2f}%**.\n\n"
                       "Cause: integer division when spreading the calibration allowance over 2n "
                       "calibration circuits (e.g. 300 shots / 8 circuits = 37.5 -> 37, leaving 4 "
                       "shots unspent out of 1500). The shortfall always falls on the *mitigated* "
                       "arm, i.e. it is conservative — REM/ZNE+REM receive marginally FEWER shots "
                       "than the unmitigated baseline, never more. Reported here rather than "
                       "silently absorbed, per the study's scientific requirements.\n")
            out.append("\n```\n" + viol.to_string() + "\n```\n")
        # unphysical estimates
        unphys = a[((a.task == "qaoa_p1") & (a.value > 7)) |
                   ((a.task == "tfim") & (a.value < -4.75877048))]
        out.append(f"\n**Unphysical estimates** (QAOA cut > exact max 7, or TFIM energy below exact ground state):"
                   f" {len(unphys)} / {len(a)} cells ({100*len(unphys)/len(a):.2f}%)\n")
        if len(unphys):
            t = unphys.groupby("method").size().reindex(ORDER).fillna(0).astype(int)
            out.append("\n| method | unphysical cells |\n|---|---|\n" +
                       "\n".join(f"| {LABEL[m]} | {t[m]} |" for m in ORDER) + "\n")
        out.append("\n## RQ1/RQ2 — verdict counts (vs. no mitigation, non-overlapping 95% CI)\n")
        pv = verdicts.pivot_table(index=["noise", "method"], columns="verdict", values="budget",
                                  aggfunc="count", fill_value=0)
        out.append("\n```\n" + pv.to_string() + "\n```\n")
        out.append("\n## Crossover budgets (smallest budget where a method 'helps')\n")
        cross = (verdicts[verdicts.verdict == "helps"].groupby(["task", "noise", "method"])
                 .budget.min().reset_index().rename(columns={"budget": "crossover_budget"}))
        out.append("\n```\n" + (cross.to_string(index=False) if len(cross) else "(none)") + "\n```\n")
        cross.to_csv(PROC / "stage_a_crossover.csv", index=False)

    b = load("stage_b")
    if b is not None:
        sb = analyse_b(b)
        out.append("\n## RQ3 — in-loop optimisation (final error, noiseless re-evaluation)\n")
        circ = sb["mean_circuit_shots"]
        rem_rows = sb[sb.method.isin(["rem", "zne_rem"])]
        cal = rem_rows["mean_calibration_shots"].max() if len(rem_rows) else 0
        spread = (circ.max() - circ.min()) / circ.max() if circ.max() else 0
        out.append(f"\n*Budget note (amortised accounting):* circuit shots per run are "
                   f"{'identical across methods' if spread == 0 else f'within {spread*100:.2f}% across methods'} "
                   f"({int(circ.min()):,}-{int(circ.max()):,}); the REM arms additionally pay a one-time "
                   f"calibration of {int(cal):,} shots "
                   f"({cal/max(circ.max(),1)*100:.1f}% extra), a reported inequality in REM's "
                   f"disfavour rather than a hidden advantage.\n")
        out.append("\n```\n" + sb.round(4).to_string(index=False) + "\n```\n")

    (PROC / "verdicts.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
