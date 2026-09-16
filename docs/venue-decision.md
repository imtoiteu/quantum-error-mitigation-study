# Venue Decision

**Compiled:** 2026-09-16. All statements below are backed by a retrieved record. **Fees, deadlines,
acceptance rates and indexing that were not verified are marked UNKNOWN and must not be assumed.**

## Contribution type being placed

A **software-correctness / benchmarking-validity** paper for quantum error mitigation:
a silent implementation defect in ZNE/REM pipelines, minimal regression tests with an exact oracle,
a quantified impact on a previously frozen benchmark, and a corrected budget-matched comparison.
Simulator-only. No hardware, no advantage claim. Modest scope, strong artifact.

## Primary venue: IEEE International Conference on Quantum Computing and Engineering (QCE / "IEEE Quantum Week")

**Evidence of fit — QCE demonstrably accepts this exact genre:**

| Paper | Relevance | Record |
|---|---|---|
| Köster & Mauerer, *Benchmarking Error Mitigation: Artefactual Improvements in Zero-Noise Extrapolation* | **A paper whose entire contribution is "a ZNE benchmark result was an artefact"** — the closest possible precedent for our contribution type | arXiv:2607.09360 v2, **"Accepted for publication at IEEE Quantum Week (QCE) 2026"** |
| Majumdar, Rivero, Metz, Hasan, Wang, *Best practices for QEM with dZNE* | A pure methodology/practice paper on dZNE, no new method | IEEE QCE 2023, DOI 10.1109/QCE57702.2023.00102 |
| Giurgica-Tiron, Hindy, LaRose, Mari, Zeng, *Digital zero noise extrapolation for QEM* | dZNE itself was introduced at QCE | IEEE QCE 2020, DOI 10.1109/QCE49297.2020.00045 |
| Finžgar, Ross, Hölscher, Klepsch, Luckow, *QUARK: A Framework for Quantum Computing Application Benchmarking* | Benchmarking-infrastructure paper, simulator-inclusive | IEEE QCE 2022, DOI 10.1109/QCE53715.2022.00042 |
| Pelofske & Russo, *Digital Zero-Noise Extrapolation with Quantum Circuit Unoptimization* | Continued dZNE-methodology acceptance | IEEE QCE 2025, DOI 10.1109/QCE65121.2025.00020 |

**Why this is the primary choice**
1. The 2026 acceptance of Köster & Mauerer is direct, current evidence that a "this ZNE result was not real" paper is in scope — and our finding is the complementary *implementation* failure mode to their *regime* failure mode, so the community context already exists.
2. QCE has a technical-paper track with short page limits suited to a bounded contribution, plus workshops as a within-venue fallback.
3. Wolfgang Mauerer (co-author of P5) also authored *1-2-3 Reproducibility for Quantum Software Experiments* (IEEE SANER 2022, DOI 10.1109/SANER53432.2022.00148), indicating an active reproducibility-minded readership at this venue.
4. Simulator-only work is accepted here (Majumdar's Fig. 7 readout experiment is a noisy-simulator result).

**Verified requirements**
- Official CfP / author information: <https://qce.quantum.ieee.org>
- Format: IEEE conference proceedings template (`IEEEtran`, `conference` option). We use the official IEEEtran class.

**UNKNOWN — must be confirmed by the author before submission**
- Submission deadline for the next edition (deadlines change annually; **not verified**).
- Page limit for the technical-paper track in the next edition (historically ~8–10 pages for QCE technical papers, **not verified for the next edition**).
- Registration/publication fees. **UNKNOWN.** IEEE conferences normally require at least one author to register and present; the amount was not verified and must not be assumed affordable.
- Whether presentation is required for inclusion in proceedings (**normally yes at IEEE conferences, not verified for this edition**).
- Review model (single vs double anonymous) for the next edition. Our LaTeX source carries a switch for anonymous formatting.

## Fallback venue: IEEE Transactions on Quantum Engineering (TQE)

**Evidence of fit**

| Paper | Relevance | Record |
|---|---|---|
| Russo, Mari, Shammah, LaRose, Zeng, *Testing Platform-Independent QEM on Noisy Quantum Computers* | Empirical, multi-method, tooling-centred QEM evaluation | IEEE TQE 4, 1–18 (2023), DOI 10.1109/TQE.2023.3305232 |
| Lubinski *et al.*, *Application-Oriented Performance Benchmarks for Quantum Computing* | Benchmarking-methodology paper | IEEE TQE 4, 1–32 (2023), DOI 10.1109/TQE.2023.3253761 |
| Prodius, Czarnik, McKerns, Sornborger, Cincio, *Robust Design Under Uncertainty in QEM* | QEM still actively published there in 2026 | IEEE TQE 7, 1–13 (2026), DOI 10.1109/TQE.2026.3680641 |

**Why fallback rather than primary:** TQE is a journal with rolling submission (no deadline risk) and
longer articles, which suits the material; but the *closest published precedent for our specific
contribution type* (an artefact/validity paper about ZNE benchmarking) is at QCE, not TQE. If QCE's
next deadline is unreachable, TQE becomes primary with no change of content — only a template swap
(`IEEEtran` journal mode) and expansion of the supplementary material into the main text.

**Fallback adaptation note:** `manuscript/FALLBACK_TQE.md` records the concrete edits required.
We prepare **one** submission at a time; no duplicate submission.

## Venues considered and rejected, with reasons

- **ACM Transactions on Quantum Computing** — publishes ZNE benchmarking (Pelofske *et al.*, DOI 10.1145/3680290) and shot-budget methodology (Bisicchia *et al.*, DOI 10.1145/3841468), but sample articles run 18–86 pages; our bounded contribution would be under-scoped. Retained as a second fallback only if expanded.
- **Quantum / PRX Quantum** — no located precedent for a pure implementation-correctness note; scope expectations substantially exceed this contribution.
- **Quantum Reports, Entropy (MDPI)** — ISSN-scoped Crossref probes returned essentially no QEM-benchmarking readership (see `docs/venue-survey.md`). Topical eligibility is not evidence of fit; rejected.

## Statements deliberately not made

We do not claim any venue is "easy", estimate an acceptance probability, or assert any deadline,
fee, indexing status or ranking that was not verified. Topical fit is not evidence of acceptance.
A workshop or poster acceptance would **not** be equivalent to a full research-paper publication and
would be reported as what it is.
