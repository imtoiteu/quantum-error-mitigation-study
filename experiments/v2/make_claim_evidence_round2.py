r"""CLAIM_EVIDENCE.csv for round 2: every quantitative claim -> data, config, command, output."""
from __future__ import annotations
import csv, json, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT/"results/v2r2/processed"
RAW = "results/v2r2/raw/confirm.jsonl"; CFG = "configs/v2/confirm_round2.yaml"
RUN = "python experiments/v2/run_study.py --config configs/v2/confirm_round2.yaml"
AN  = "python experiments/v2/analyze_round2.py"

rows=[]
def add(loc, claim, value, raw, cfg, cmd, out):
    rows.append(dict(location=loc, claim=claim, value=value, raw_data=raw, config=cfg,
                     command=cmd, output_table=out))

f1=pd.read_csv(PROC/"R2_F1_implementation_contrast.csv")
bv=pd.read_csv(PROC/"R2_bias_variance.csv")
s=pd.read_csv(PROC/"R2_winner_summary.csv"); allr=s[s.noise=="ALL"].iloc[0]
pr=pd.read_csv(PROC/"R2_per_instance_rankings.csv")
tot=json.loads((PROC/"R2_cost.json").read_text())

add("Abstract; Sec.VI","Range of mean |difference| between implementations, normalised by Cmax",
    f"{f1.mean_absolute_d_abs_norm.min():.3f} to {f1.mean_absolute_d_abs_norm.max():.3f}",
    RAW,CFG,AN,"results/v2r2/processed/R2_F1_implementation_contrast.csv")
add("Abstract; Table IV","Rate at which the selected method changes (scope: 3 mitigated methods)",
    f"{100*allr.flip_rate_3mitigated:.1f}% of {int(allr.n)} cells",RAW,CFG,AN,
    "results/v2r2/processed/R2_winner_summary.csv")
add("Table IV","Same rate with the unmitigated option included in the candidate set",
    f"{100*allr.flip_rate_incl_unmitigated:.1f}%",RAW,CFG,AN,"results/v2r2/processed/R2_winner_summary.csv")
add("Table IV","Near-tie rate (best vs second-best within 0.01 Cmax)",
    f"{100*allr.near_tie_rate_lt_1pct:.1f}%",RAW,CFG,AN,"results/v2r2/processed/R2_winner_summary.csv")
add("Abstract; Table IV","Split-sample excess regret attributable to the defect (select on replicate 0, pay on replicate 1)",
    f"{allr.excess_regret_from_defect:.4f} of Cmax (defective {allr.split_regret_legacy:.4f}, corrected {allr.split_regret_v2:.4f})",
    RAW,CFG,AN,"results/v2r2/processed/R2_winner_summary.csv")
for _,r in f1.iterrows():
    add("Table II",f"Implementation contrast, {r.method} on {r.noise}",
        f"signed {r.mean_d_abs_norm:+.4f} strat CI[{r.ci_lo:+.4f},{r.ci_hi:+.4f}] "
        f"cluster CI[{r.cluster_lo:+.4f},{r.cluster_hi:+.4f}] mean|.|={r.mean_absolute_d_abs_norm:.4f} "
        f"directionality={r.directionality:.2f} p_BH={r['p_adj_BH']:.3e}",
        RAW,CFG,AN,"results/v2r2/processed/R2_F1_implementation_contrast.csv")
for _,r in bv.iterrows():
    add("Table III",f"Bias and variance, {r.method}/{r.noise}/{r.impl}",
        f"bias {r.bias_norm:+.4f} CI[{r.bias_lo:+.4f},{r.bias_hi:+.4f}] sd {r.sd_norm:.4f} rmse {r.rmse_norm:.4f}",
        RAW,CFG,AN,"results/v2r2/processed/R2_bias_variance.csv")
add("Sec.VI","Per-instance mean-ranking winner changes",
    f"{int(pr.changed3.sum())}/{len(pr)} conditions (3 mitigated); {int(pr.changed4.sum())}/{len(pr)} including unmitigated",
    RAW,CFG,AN,"results/v2r2/processed/R2_per_instance_rankings.csv")
add("Sec.III","Realised total shots: maximum relative deviation across methods",
    f"{tot['budget_max_rel_dev_pct']:.4f}%",RAW,CFG,AN,"results/v2r2/processed/R2_cost.json")
add("Sec.III","Empirical stream-collision audit over the realised coordinate set",
    f"{tot['collisions']} collisions over {tot['n_coords']} coordinates ({tot['n_distinct_seeds']} distinct seeds)",
    RAW,CFG,AN,"results/v2r2/processed/R2_cost.json")
add("Sec.III","Total round-2 cost",
    f"{tot['cells']} cells, {tot['total_shots']} shots, "
    f"{tot['circuit_executions']+tot['calibration_executions']} executions, 0 scoring shots, "
    f"{tot['wall_clock_core_hours']:.2f} core-hours",RAW,CFG,AN,"results/v2r2/processed/R2_cost.json")
add("Sec.IV-A, oracle table","Defective folding returns a different ideal bitstring under non-identity layout",
    "0101 -> 1010 / 0011 / 1100 for layouts [3,2,1,0]/[1,3,0,2]/[2,0,3,1]",
    "n/a (deterministic)","tests/test_v2_correctness.py",
    "python tests/test_v2_correctness.py","stdout T1")
add("Sec.IV-A","Folding exactness: Clifford exact, rotations show a constant offset",
    "Clifford max|dp| = 0.0 at scales 3/5/9; with rotations 1.04e-11, constant across scales",
    "n/a (deterministic)","tests/test_v2_correctness.py",
    "python tests/test_v2_correctness.py","stdout T2, T2b")
add("Sec.IV-B, Table I","Oracle B: aligned vs virtual-index calibration, unequal response matrices",
    "aligned max error ~1e-16; misindexed up to 1.8e-1; identity layout invisible",
    "n/a (deterministic)","tests/test_rem_indexing.py",
    "python tests/test_rem_indexing.py","stdout")
add("Sec.IV-B","Oracle A is blind to the calibration defect at zero readout noise",
    "with p=0 all response matrices are identity, so permuting them is undetectable",
    "n/a (deterministic)","tests/test_rem_indexing.py",
    "python tests/test_rem_indexing.py","stdout, control block")
add("Sec.IV-D","Folding amplifies gate noise; readout is a constant attenuation",
    "gate-only <ZZ> 0.980100/0.941480/0.904382 at scales 1/3/5; readout-only 0.810000 at all three = (1-2p)^2",
    "n/a (exact density matrix + explicit response matrix)","n/a",
    "python experiments/v2/noise_scaling_audit.py","supplementary/noise_scaling_audit.md")
add("Sec.V","Positive control: M3 used as documented agrees with the corrected implementation",
    "mthree 3.0.0 final_measurement_mapping agrees on all 4 layouts; both recover to ~1e-16; only virtual-index fails",
    "n/a (exact)","n/a","python experiments/v2/positive_control_m3.py",
    "supplementary/positive_control_m3.md")
add("Sec.VII (pilot correction)","Round-1 pilot was not independent of the round-1 main study",
    "224/224 pilot rows share keys with main-study rows and are bit-for-bit identical",
    "results/v2/raw/pilot.jsonl, results/v2/raw/main_study.jsonl","configs/v2/pilot.yaml",
    "see REVIEW_RESPONSE_round2.md S1","REVIEW_RESPONSE_round2.md")
add("Sec.VII (pilot correction)","Fraction of the round-1 pilot affected by the defects",
    "450/2400 estimation cells (18.8%); 30/40 optimisation runs (75%)",
    "results/v2/raw/stage_a.jsonl, stage_b.jsonl","configs/stage_a.yaml, stage_b.yaml",
    "python experiments/v2/impact_audit.py","results/v2/processed/stage_a_affected.csv")

out=ROOT/"CLAIM_EVIDENCE.csv"
with out.open("w",newline="") as fh:
    wtr=csv.DictWriter(fh,fieldnames=["location","claim","value","raw_data","config","command","output_table"])
    wtr.writeheader(); wtr.writerows(rows)
print(f"wrote {out} with {len(rows)} traced claims")
