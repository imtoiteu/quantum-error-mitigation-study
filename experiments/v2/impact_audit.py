"""Quantify which frozen v1 results are affected by review findings A1a-A1c.

A cell is AFFECTED iff (a) its noise condition induced a non-identity layout AND
(b) its method uses folding (zne, zne_rem) or REM calibration (rem, zne_rem).
'none' never folds and never calibrates, so it is unaffected everywhere.
"""
from __future__ import annotations
import sys, json, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qemstudy.problems import TFIM, MaxCutQAOA
from qemstudy.noise import NoiseSpec
from qemstudy.runner import Executor

PAR = json.loads((ROOT / "configs" / "pretrained_params.json").read_text())

def layout_is_trivial(task, noise_name, noise_kind, lam):
    n, circs = ((4, TFIM().measured_circuits(np.array(PAR['tfim']['params']), reps=1))
                if task == 'tfim' else
                (6, MaxCutQAOA(p=1).measured_circuits(np.array(PAR['qaoa_p1']['params']))))
    ex = Executor(NoiseSpec(noise_name, noise_kind, lam), n, seed=0)
    for qc in circs.values():
        t = ex.prepare(qc)
        if t.layout is None:
            continue
        il = list(t.layout.initial_index_layout(filter_ancillas=True))
        try: rp = list(t.layout.routing_permutation())
        except Exception: rp = list(range(n))
        if il != list(range(n)) or rp != list(range(n)):
            return False, il, rp
    return True, None, None

def main():
    sa = pd.DataFrame([json.loads(l) for l in (ROOT/'results/raw/stage_a.jsonl').read_text().splitlines()])
    sb = pd.DataFrame([json.loads(l) for l in (ROOT/'results/raw/stage_b.jsonl').read_text().splitlines()])
    conds = sa[['task','noise','noise_kind','lam']].drop_duplicates()
    rows=[]
    for _,c in conds.iterrows():
        triv, il, rp = layout_is_trivial(c.task, c.noise, c.noise_kind, c.lam)
        rows.append(dict(task=c.task, noise=c.noise, trivial_layout=triv,
                         initial_layout=str(il), routing_perm=str(rp)))
    lay = pd.DataFrame(rows)
    lay.to_csv(ROOT/'results/v2/processed/layout_audit.csv', index=False)
    print("=== Layout audit (bug is ACTIVE where trivial_layout is False) ===")
    print(lay.to_string(index=False))

    AFFECTED_METHODS = {'zne','rem','zne_rem'}
    bad = set(lay[~lay.trivial_layout].apply(lambda r:(r.task,r.noise),axis=1))
    sa['affected'] = sa.apply(lambda r: (r.task,r.noise) in bad and r.method in AFFECTED_METHODS, axis=1)
    sb['affected'] = sb.apply(lambda r: (r.task,r.noise) in bad and r.method in AFFECTED_METHODS, axis=1)
    print(f"\n=== Stage A: {sa.affected.sum()} / {len(sa)} cells affected "
          f"({100*sa.affected.mean():.1f}%) ===")
    print(sa.groupby(['task','noise','method']).affected.any().unstack().to_string())
    print(f"\n=== Stage B: {sb.affected.sum()} / {len(sb)} runs affected "
          f"({100*sb.affected.mean():.1f}%) ===")
    print(sb.groupby(['noise','method']).affected.any().unstack().to_string())
    sa[['task','noise','method','budget','seed','affected']].to_csv(
        ROOT/'results/v2/processed/stage_a_affected.csv', index=False)
    sb[['task','noise','method','seed','affected']].to_csv(
        ROOT/'results/v2/processed/stage_b_affected.csv', index=False)

if __name__ == '__main__':
    main()
