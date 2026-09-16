"""Build the submission package with a manifest and checksums.

Includes: compiled manuscript, LaTeX sources, figures (vector + raster + plotting
source + .drawio), supplementary material, review documents, code, configs,
processed results, and raw results if they fit the size budget. Anything omitted
is recorded in the manifest with its retrieval procedure.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys, zipfile, datetime, subprocess

ROOT = pathlib.Path("/root/imtoiteu/quantum-error-mitigation-study")
OUT  = pathlib.Path("/root/imtoiteu/quantum-error-mitigation-review-round2.zip")
MAX_TOTAL_MB = 90.0          # practical package size budget

INCLUDE_GLOBS = [
    "manuscript/**/*", "supplementary/**/*", "figures/**/*",
    "src/**/*.py", "tests/**/*.py", "experiments/**/*.py",
    "configs/**/*", "docs/**/*.md",
    "results/v2/processed/**/*", "results/v2r2/processed/**/*",
    "README.md", "HANDOFF.md", "REVIEW.md", "REVIEW_RESPONSE.md", "FINAL_REVIEW.md",
    "AUTHOR_ACTIONS.md", "REPRODUCE.md", "CLAIM_EVIDENCE.csv",
    "REVIEW_RESPONSE_round2.md",
    "requirements.txt", "requirements-lock.txt", ".gitignore",
    "logs/v2/*.log", "logs/v2r2/*.log",
]
# Large raw data: include if it fits, else record retrieval procedure.
RAW_CANDIDATES = ["results/v2r2/raw/confirm.jsonl",          # round-2 fresh data first
                  "results/v2/raw/main_study.jsonl", "results/v2/raw/pilot.jsonl",
                  "results/raw/stage_a.jsonl", "results/raw/stage_b.jsonl"]
EXCLUDE_PARTS = {".venv", "__pycache__", ".git", ".ipynb_checkpoints"}


def eligible(p: pathlib.Path) -> bool:
    return p.is_file() and not any(part in EXCLUDE_PARTS for part in p.parts)


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    files: list[pathlib.Path] = []
    for g in INCLUDE_GLOBS:
        files += [p for p in ROOT.glob(g) if eligible(p)]
    files = sorted(set(files))
    total = sum(p.stat().st_size for p in files)

    omitted = []
    for rel in RAW_CANDIDATES:
        p = ROOT / rel
        if not p.exists():
            continue
        if (total + p.stat().st_size) / 1e6 <= MAX_TOTAL_MB:
            files.append(p); total += p.stat().st_size
        else:
            omitted.append(rel)

    try:
        commit = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT).decode().strip()
        branch = subprocess.check_output(["git","rev-parse","--abbrev-ref","HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        commit, branch = "unknown", "unknown"

    manifest = {
        "package": OUT.name,
        "built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "git_commit": commit, "git_branch": branch,
        "repository": "git@github-quantum:imtoiteu/quantum-error-mitigation-study.git",
        "repository_visibility": "private at time of packaging",
        "simulator_only": True, "quantum_hardware_used": "none",
        "file_count": len(files),
        "total_bytes": int(total),
        "files": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size,
                   "sha256": sha256(p)} for p in sorted(set(files))],
        "omitted_artifacts": [
            {"path": rel, "reason": "exceeds package size budget",
             "retrieval": f"git clone the repository at commit {commit} (branch {branch}) "
                          f"and read {rel}; or regenerate with the commands in REPRODUCE.md"}
            for rel in omitted],
        "reproduction_entrypoint": "REPRODUCE.md",
        "claim_traceability": "CLAIM_EVIDENCE.csv",
    }

    mpath = ROOT / "PACKAGE_MANIFEST.json"
    mpath.write_text(json.dumps(manifest, indent=2))

    sums = "\n".join(f"{f['sha256']}  {f['path']}" for f in manifest["files"]) + "\n"
    spath = ROOT / "PACKAGE_SHA256SUMS.txt"
    spath.write_text(sums)

    OUT.unlink(missing_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(set(files)):
            z.write(p, p.relative_to(ROOT))
        z.write(mpath, mpath.name)
        z.write(spath, spath.name)

    print(f"package : {OUT}  ({OUT.stat().st_size/1e6:.2f} MB)")
    print(f"files   : {len(files)} + manifest + checksums")
    print(f"omitted : {omitted if omitted else 'none'}")
    bad = [f for f in manifest['files'] if f['bytes'] == 0]
    print(f"zero-byte files: {bad if bad else 'none'}")


if __name__ == "__main__":
    main()
