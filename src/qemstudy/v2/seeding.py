"""Explicit random-stream hierarchy with a documented pairing contract.

ROUND-2 CORRECTION (review finding 2)
-------------------------------------
The previous version derived simulator streams from ``(run_id, eval_id, basis, scale)``
only. Because ``instance``, ``noise``, ``method``, ``budget`` and ``impl`` were all
absent, cells differing only in those factors received the SAME simulator seed.

Two consequences, both confirmed empirically:
  * the corrected-pilot and main-study runs shared coordinates, so all 224 pilot
    rows reproduced main-study values bit-for-bit (100% overlap);
  * draws were NOT independent across arms, contrary to what the protocol claimed.

PAIRING CONTRACT (v2r2)
-----------------------
``impl`` is DELIBERATELY EXCLUDED from the coordinate tuple. This is common random
numbers (CRN) between the defective and corrected implementations: for a fixed
(instance, noise, method, budget, seed, basis, scale) both implementations see the
same shot-noise realisation, so their difference isolates the implementation and
nothing else. This is intentional, is the estimand F1 targets, and is reflected in
the analysis by treating F1 as a paired within-cell contrast.

Every OTHER factor -- instance, noise, method, budget, seed, basis, scale, and the
evaluation index -- IS part of the coordinate tuple, so draws are independent across
them. Calibration and transpilation have their own role namespaces.

NAMESPACES
----------
``namespace`` separates whole experiment campaigns. Fresh confirmation data must use
a namespace that has never been used before, so it cannot reproduce earlier values.

COLLISIONS
----------
Distinct coordinate tuples map to distinct spawn keys by construction (the tuple is
carried verbatim into ``SeedSequence.spawn_key``); the role name is hashed into the
leading element. We do NOT claim hash collisions are impossible. Instead
``audit_collisions()`` checks the realised coordinate set of an actual run and the
result is recorded with the data.
"""
from __future__ import annotations
import hashlib
from typing import Iterable, Sequence
import numpy as np

# Campaign namespaces. Never reuse a retired namespace for new data.
NAMESPACES = {
    "v2_main_2026_09_16": 0,       # RETIRED: original main study + contaminated pilot
    "v2r2_confirm_2026_09_16": 1,  # RETIRED: round-2; compilation depended on method (confound)
    "v2r3_confirm_2026_09_16": 3,  # round-3 rerun with compilation shared across methods
    "v2r2_selftest": 2,            # correctness tests only, never experimental data
}
MASTER_ENTROPY = 20260916_0001

ROLES = ("init_params", "optimizer", "simulator", "calibration",
         "transpiler", "bootstrap", "instance_draw")

# ROUND-3 (review finding 3): COMPILATION randomness is separated from SAMPLING
# randomness. The transpiler stream may depend ONLY on these fields, so every method,
# budget and implementation in a cell shares one prepared base circuit -- same layout,
# same routing permutation, same measurement map. Round 2 seeded the transpiler from
# the full cell (including `method`), which produced different routing permutations
# for different methods and confounded the method ranking with compilation.
COMPILATION_FIELDS = ("instance", "noise", "seed", "compile_rep")

# Factors that participate in a simulator/calibration coordinate, in fixed order.
COORD_FIELDS = ("instance", "noise", "method", "budget", "seed", "eval_id", "basis", "scale",
                "compile_rep")
# Deliberately NOT a coordinate field -- see PAIRING CONTRACT above.
PAIRED_FIELDS = ("impl",)


def _h(s: str) -> int:
    return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=4).digest(), "big")


def coords_from(namespace: str, **kw) -> tuple[int, ...]:
    """Build the integer coordinate tuple for a cell.

    Unknown keys raise, so a factor cannot be silently dropped again.
    """
    if namespace not in NAMESPACES:
        raise ValueError(f"unknown namespace {namespace!r}")
    bad = set(kw) - set(COORD_FIELDS) - set(PAIRED_FIELDS)
    if bad:
        raise ValueError(f"unknown coordinate field(s) {sorted(bad)}")
    out = [NAMESPACES[namespace]]
    for f in COORD_FIELDS:
        v = kw.get(f, 0)
        out.append(_h(v) if isinstance(v, str) else int(round(float(v) * 1000)))
    return tuple(out)


def compilation_coords(namespace: str, **kw) -> tuple[int, ...]:
    """Coordinate tuple for the TRANSPILER stream only (review finding 3).

    Deliberately ignores method, budget, eval_id, basis, scale and impl, so a single
    compiled base circuit is shared by every arm of a cell.
    """
    if namespace not in NAMESPACES:
        raise ValueError(f"unknown namespace {namespace!r}")
    bad = set(kw) - set(COMPILATION_FIELDS)
    if bad:
        raise ValueError(f"compilation coords must not depend on {sorted(bad)}")
    out = [NAMESPACES[namespace]]
    for f in COMPILATION_FIELDS:
        v = kw.get(f, 0)
        out.append(_h(v) if isinstance(v, str) else int(round(float(v) * 1000)))
    return tuple(out)


def seed_sequence(role: str, coords: Sequence[int], master: int = MASTER_ENTROPY):
    if role not in ROLES:
        raise ValueError(f"unknown stream role {role!r}; declare it in ROLES")
    return np.random.SeedSequence(entropy=master, spawn_key=(_h(role), *map(int, coords)))


def generator(role: str, coords: Sequence[int], master: int = MASTER_ENTROPY) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(role, coords, master=master))


def int_seed(role: str, coords: Sequence[int], master: int = MASTER_ENTROPY) -> int:
    return int(seed_sequence(role, coords, master=master).generate_state(1, dtype=np.uint32)[0] >> 1)


def audit_collisions(role: str, coord_sets: Iterable[Sequence[int]]) -> dict:
    """Empirical collision audit over the coordinate tuples an actual run used."""
    seen: dict[int, tuple] = {}
    collisions = []
    n = 0
    for c in coord_sets:
        n += 1
        s = int_seed(role, c)
        if s in seen and seen[s] != tuple(c):
            collisions.append((seen[s], tuple(c), s))
        seen[s] = tuple(c)
    return {"role": role, "n_coords": n, "n_distinct_seeds": len(seen),
            "n_collisions": len(collisions), "examples": collisions[:5]}
