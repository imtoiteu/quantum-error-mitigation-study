"""Explicit, hierarchical random-number streams (review finding A3).

v1 defect: `seed` was reused for seed_simulator, seed_transpiler and the NumPy
generator, and Stage B passed `seed + n_evals` as a simulator seed, so streams
for different evaluations could collide with streams for different runs
(e.g. run seed=0 eval=5 and run seed=5 eval=0 shared a simulator seed).

v2 uses numpy.random.SeedSequence with a named, documented hierarchy. Every
stream is derived from (master, role, *coords) by hashing the role name into
the spawn key, so no two roles can ever collide and streams are reproducible
from the coordinates alone.
"""
from __future__ import annotations
import hashlib
import numpy as np

MASTER_ENTROPY = 20260916_0001   # fixed for the whole study; recorded in configs

ROLES = ("init_params", "optimizer", "simulator", "calibration",
         "transpiler", "basis", "scale", "bootstrap")


def _role_key(role: str) -> int:
    if role not in ROLES:
        raise ValueError(f"unknown stream role {role!r}; declare it in ROLES")
    return int.from_bytes(hashlib.blake2b(role.encode(), digest_size=4).digest(), "big")


def seed_sequence(role: str, *coords: int, master: int = MASTER_ENTROPY) -> np.random.SeedSequence:
    """A SeedSequence for one named role at integer coordinates."""
    return np.random.SeedSequence(entropy=master, spawn_key=(_role_key(role), *map(int, coords)))


def generator(role: str, *coords: int, master: int = MASTER_ENTROPY) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(role, *coords, master=master))


def int_seed(role: str, *coords: int, master: int = MASTER_ENTROPY) -> int:
    """A 31-bit integer seed for APIs that take ints (Aer, transpiler)."""
    return int(seed_sequence(role, *coords, master=master).generate_state(1, dtype=np.uint32)[0] >> 1)
