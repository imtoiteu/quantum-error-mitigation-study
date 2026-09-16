r"""CLAIM_EVIDENCE.csv for round 3: claim -> data, config, command, output."""
from __future__ import annotations
import csv, json, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROC = ROOT/"results/v2r3/processed"
RAW="results/v2r3/raw/confirm.jsonl"; CFG="configs/v2/confirm_round3.yaml"
AN="python experiments/v2/analyze_round3.py"
rows=[]
def add(loc,claim,value,raw,cfg,cmd,out):
    rows.append(dict(location=loc,claim=claim,value=value,raw_data=raw,config=cfg,command=cmd,output_table=out))

f1=pd.read_csv(PROC/"R3_F1.csv"); bv=pd.read_csv(PROC/"R3_bias_variance.csv")
s=pd.read_csv(PROC/"R3_endpoint.csv")
a=s[(s.candidate_set=="incl_unmitigated")&(s.noise=="ALL")].iloc[0]
tot=json.loads((PROC/"R3_cost.json").read_text()); comp=json.loads((PROC/"R3_compilation_check.json").read_text())

add("Abstract; Sec.VI, Table V","Primary endpoint: paired held-out loss difference (legacy-selected minus corrected-selected)",
    f"{a.delta_heldout:+.4f} of Cmax; stratified CI [{a.ci_lo:+.4f},{a.ci_hi:+.4f}]; cluster CI [{a.cluster_lo:+.4f},{a.cluster_hi:+.4f}]",
    RAW,CFG,AN,"results/v2r3/processed/R3_endpoint.csv")
add("Abstract; Sec.VI","Winner-change rate (identical for both candidate sets)",
    f"{100*a.changed_rate:.1f}% of {int(a.n)} cells",RAW,CFG,AN,"results/v2r3/processed/R3_endpoint.csv")
add("Abstract; Sec.VI, Table VI","Near ties: practical and statistical, all cells",
    f"practical {100*a.tie_practical_all:.1f}%, statistical {100*a.tie_statistical_all:.1f}%, median gap {a.median_gap:.4f}",
    RAW,CFG,AN,"results/v2r3/processed/R3_endpoint.csv")
add("Sec.VI, Table VI","Near ties among CHANGED-WINNER cells",
    f"practical {100*a.tie_practical_changed:.1f}%",RAW,CFG,AN,"results/v2r3/processed/R3_endpoint.csv")
for _,r in s.iterrows():
    add("Table V",f"Held-out endpoint, {r.candidate_set}, {r.noise}",
        f"{r.delta_heldout:+.4f} CI[{r.ci_lo:+.4f},{r.ci_hi:+.4f}] changed={100*r.changed_rate:.1f}%",
        RAW,CFG,AN,"results/v2r3/processed/R3_endpoint.csv")
for _,r in f1.iterrows():
    add("Table III",f"Implementation contrast, {r.method} on {r.noise}",
        f"signed {r.mean_signed:+.4f} CI[{r.ci_lo:+.4f},{r.ci_hi:+.4f}] mean|.|={r.mean_abs:.4f} "
        f"directionality={r.directionality:.2f} p_BH={r['p_adj_BH']:.3e}",RAW,CFG,AN,"results/v2r3/processed/R3_F1.csv")
for _,r in bv.iterrows():
    add("Table IV",f"Bias/variance, {r.method}/{r.noise}/{r.impl}",
        f"bias {r.bias_norm:+.4f} sd {r.sd_norm:.4f} rmse {r.rmse_norm:.4f}",RAW,CFG,AN,"results/v2r3/processed/R3_bias_variance.csv")
add("Sec.III","Compilation shared across all arms of a cell (asserted from data)",
    f"{comp['cells_with_multiple_base_circuits']} violations over {comp['cells_checked']} cells; "
    f"{comp.get('rows_missing_fingerprint',0)} rows missing a fingerprint",RAW,CFG,AN,
    "results/v2r3/processed/R3_compilation_check.json")
add("Sec.III","Realised total shots: max relative deviation across methods",
    f"{tot['budget_max_rel_dev_pct']:.4f}%",RAW,CFG,AN,"results/v2r3/processed/R3_cost.json")
add("Sec.III","Stream-collision audit over the realised coordinate set",
    f"{tot['collisions']} collisions over {tot['n_coords']} coordinates",RAW,CFG,AN,"results/v2r3/processed/R3_cost.json")
add("Sec.III","Total round-3 cost",
    f"{tot['cells']} cells, {tot['total_shots']} shots, 0 scoring shots, {tot['wall_clock_core_hours']:.2f} core-hours",
    RAW,CFG,AN,"results/v2r3/processed/R3_cost.json")
add("Sec.IV-A","Folding oracle: defective folding changes the ideal bitstring under non-identity layout",
    "0101 -> 1010 / 0011 / 1100 for layouts [3,2,1,0]/[1,3,0,2]/[2,0,3,1]","n/a (deterministic)",
    "tests/test_v2_correctness.py","python tests/test_v2_correctness.py","stdout T1")
add("Sec.IV-B, Table II","REM oracle: aligned vs virtual-index calibration, unequal response matrices",
    "aligned ~1e-16; misindexed 1.2e-1 to 2.9e-1; generation path (bitwise) differs from inversion path (tensored)",
    "n/a (deterministic)","tests/test_rem_indexing.py","python tests/test_rem_indexing.py","stdout O3")
add("Sec.IV-B","Ordering: statevector is physical-qubit-indexed, counts are clbit-indexed",
    "re-indexed vs Aer 3.95e-04 (shot noise) versus 8.11e-01 un-reindexed","n/a (deterministic)",
    "tests/test_rem_indexing.py","python tests/test_rem_indexing.py","stdout O1")
add("Sec.IV-B","Folding oracle is blind to the calibration defect at zero readout noise",
    "with p=0 all response matrices are identity, so permuting them is undetectable","n/a (deterministic)",
    "tests/test_rem_indexing.py","python tests/test_rem_indexing.py","stdout O4")
add("Sec.IV-D","Folding amplifies gate noise; readout is a constant attenuation",
    "gate-only <ZZ> 0.980100/0.941480/0.904382 at scales 1/3/5; readout-only 0.810000 at all three = (1-2p)^2",
    "n/a (exact density matrix + explicit response matrix)","n/a",
    "python experiments/v2/noise_scaling_audit.py","supplementary/noise_scaling_audit.md")
add("Sec.V","M3 positive control: mapping agreement AND genuine correction",
    "map agrees on 4/4 layouts; M3 apply_correction recovers to ~3e-5 with correct qubits and fails at 1.2e-1 to 2.9e-1 with virtual indices",
    "n/a (exact)","n/a","python experiments/v2/positive_control_m3.py","supplementary/positive_control_m3.md")
add("Sec.VII","Round-1 pilot was not independent of the round-1 main study",
    "224/224 pilot rows share keys with main-study rows and are bit-for-bit identical",
    "results/v2/raw/pilot.jsonl, results/v2/raw/main_study.jsonl","configs/v2/pilot.yaml",
    "see REVIEW_RESPONSE_round2.md S1","REVIEW_RESPONSE_round2.md")
out=ROOT/"CLAIM_EVIDENCE.csv"
with out.open("w",newline="") as fh:
    wtr=csv.DictWriter(fh,fieldnames=["location","claim","value","raw_data","config","command","output_table"])
    wtr.writeheader(); wtr.writerows(rows)
print(f"wrote {out} with {len(rows)} traced claims")
