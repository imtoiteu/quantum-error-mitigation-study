"""Build CLAIM_EVIDENCE.csv: every quantitative claim -> data, config, command, output.

Each row names the manuscript location, the claim, the exact value as generated,
the raw-data file it derives from, the config that produced that data, the command
that regenerates it, and the processed output table where it appears.
"""
from __future__ import annotations
import csv, json, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT/"results/v2/processed"
RAWMAIN = "results/v2/raw/main_study.jsonl"
CFGMAIN = "configs/v2/main_study.yaml"
CMD_RUN = "python experiments/v2/run_study.py --config configs/v2/main_study.yaml"
CMD_AN  = "python experiments/v2/analyze_main.py"
CMD_TAB = "python experiments/v2/make_tables.py"
CMD_TEST= "python tests/test_v2_correctness.py"
CMD_AUD = "python experiments/v2/impact_audit.py"

rows=[]
def add(loc, claim, value, raw, cfg, cmd, out):
    rows.append(dict(location=loc, claim=claim, value=value, raw_data=raw,
                     config=cfg, command=cmd, output_table=out))

f1=pd.read_csv(PROC/"F1_implementation_impact.csv")
f2=pd.read_csv(PROC/"F2_method_vs_unmitigated.csv")
flip=pd.read_csv(PROC/"F1_flip_rate.csv",index_col=0)
cost=pd.read_csv(PROC/"cost_accounting.csv",index_col=0)
dev=pd.read_csv(PROC/"budget_match_check.csv",index_col=0)
tot=json.loads((PROC/"total_cost.json").read_text())

add("Abstract; Sec.V", "Best mitigation method changes between defective and corrected code",
    f"{100*flip.loc['ALL','flip_rate']:.0f}% of {int(flip.loc['ALL','n_cells'])} cells",
    RAWMAIN, CFGMAIN, CMD_AN, "results/v2/processed/F1_flip_rate.csv")
add("Abstract; Sec.V", "Range of mean absolute disagreement |D| (expected cut value)",
    f"{f1.mean_abs_disagreement.min():.3f} to {f1.mean_abs_disagreement.max():.3f}",
    RAWMAIN, CFGMAIN, CMD_AN, "results/v2/processed/F1_implementation_impact.csv")
add("Sec.V, Table II", "All 6 F1 tests significant after Benjamini-Hochberg",
    f"max adjusted p = {f1['p_adj_BH'].max():.3e}", RAWMAIN, CFGMAIN, CMD_AN,
    "results/v2/processed/F1_implementation_impact.csv")
for _,r in f1.iterrows():
    add("Table II", f"Mean |D| for {r.method} on {r.noise}",
        f"{r.mean_abs_disagreement:.3f} [{r.abs_ci_lo:.3f}, {r.abs_ci_hi:.3f}]",
        RAWMAIN, CFGMAIN, CMD_AN, "results/v2/processed/F1_implementation_impact.csv")
for _,r in f2.iterrows():
    add("Table IV", f"{r.method} vs unmitigated, {r.noise}, B={int(r.budget)}",
        f"delta={r.mean_diff:+.4f} CI[{r.ci_lo:+.4f},{r.ci_hi:+.4f}] "
        f"delta/Cmax={r.effect_in_ratio_units:+.4f} p_BH={r['p_adj_BH']:.3e} -> {r.verdict}",
        RAWMAIN, CFGMAIN, CMD_AN, "results/v2/processed/F2_method_vs_unmitigated.csv")
add("Sec.III", "Maximum relative deviation of realised total shots across methods",
    f"{100*dev['rel_dev'].max():.4f}%", RAWMAIN, CFGMAIN, CMD_AN,
    "results/v2/processed/budget_match_check.csv")
for m in cost.index:
    r=cost.loc[m]
    add("Table V", f"Realised cost per estimate, {m}",
        f"total_shots={r.mean_total_shots:.0f} circuit={r.mean_circuit_shots:.0f} "
        f"calib={r.mean_calibration_shots:.0f} exec={r.mean_circuit_exec:.1f}+{r.mean_calibration_exec:.1f}",
        RAWMAIN, CFGMAIN, CMD_AN, "results/v2/processed/cost_accounting.csv")
add("Table VI", "Total study cost",
    f"cells={tot['cells']} shots={tot['total_shots']} exec={tot['circuit_executions']+tot['calibration_executions']} "
    f"scoring_shots={tot['scoring_shots']} core_hours={tot['wall_clock_core_hours']:.2f}",
    RAWMAIN, CFGMAIN, CMD_AN, "results/v2/processed/total_cost.json")
add("Sec.IV-C, oracle table", "Defective folding returns a different ideal bitstring under non-identity layout",
    "0101 -> 1010 / 0011 / 1100 for layouts [3,2,1,0]/[1,3,0,2]/[2,0,3,1]",
    "n/a (deterministic test)", "tests/test_v2_correctness.py", CMD_TEST, "stdout, test T1")
add("Sec.IV-B", "REM response-matrix misassignment factor on the realised layout",
    "bit 2 corrected with error 0.4638 when applicable rate was 0.0292 (15.9x)",
    "n/a (deterministic audit)", "configs/v2/references.json", CMD_AUD,
    "results/v2/processed/layout_audit.csv")
add("Sec.IV-D", "Folding amplifies gate noise but leaves readout noise exactly invariant",
    "gate-only <ZZ> = 0.990000/0.970299/0.950990 at scales 1/3/5; readout-only = 1.000000 at all",
    "n/a (exact density matrix)", "n/a", "see supplementary/noise_scaling_audit.md", "supplementary")
add("Sec.VII (retraction)", "Fraction of the earlier frozen study affected by the defect",
    "Stage A 450/2400 cells (18.8%); Stage B 30/40 runs (75%)",
    "results/raw/stage_a.jsonl, results/raw/stage_b.jsonl", "configs/stage_a.yaml, configs/stage_b.yaml",
    CMD_AUD, "results/v2/processed/stage_a_affected.csv, stage_b_affected.csv")
add("Sec.III, Table I", "Ansatz references are multistart best-known, not proven global optima",
    "reference_is_proven_global_optimum=false; 47-100% of 60 restarts reach the best value",
    "n/a", "configs/v2/references.json", "python experiments/v2/pretrain_v2.py",
    "configs/v2/references.json")

out=ROOT/"CLAIM_EVIDENCE.csv"
with out.open("w", newline="") as fh:
    wtr=csv.DictWriter(fh, fieldnames=["location","claim","value","raw_data","config","command","output_table"])
    wtr.writeheader(); wtr.writerows(rows)
print(f"wrote {out} with {len(rows)} traced claims")
