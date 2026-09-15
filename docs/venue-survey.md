# Venue Survey

**Compiled:** 2026-09-15

**Method.** Rather than relying on reputation, each candidate venue was probed with an
ISSN-scoped Crossref query (`/journals/{issn}/works?query.bibliographic=...`) restricted to
publications from 2023 onward, using the search terms *"quantum error mitigation"* and
*"zero-noise extrapolation error mitigation variational"*. A venue is judged a good fit only if
it has **actually published** work of the type we intend to submit. Conference venues (IEEE QCE)
were probed through their Crossref proceedings records.

> **No submission deadlines are stated in this document.** Deadlines move every year and were not
> verified in this pass. Before submitting, check the official CfP linked for each venue.

---

## Evidence table — what each venue actually publishes

### 1. IEEE Transactions on Quantum Engineering (TQE) — ISSN 2689-1808

Direct hits from the ISSN-scoped query:

| Year | Paper | DOI |
|---|---|---|
| 2023 | Testing Platform-Independent Quantum Error Mitigation on Noisy Quantum Computers (Russo, Mari, Shammah, LaRose, Zeng) | [10.1109/TQE.2023.3305232](https://doi.org/10.1109/TQE.2023.3305232) |
| 2023 | Application-Oriented Performance Benchmarks for Quantum Computing (Lubinski *et al.*) | [10.1109/TQE.2023.3253761](https://doi.org/10.1109/TQE.2023.3253761) |
| 2024 | Distributionally Robust Variational Quantum Algorithms With Shifted Noise (He, Peng, Alexeev, Zhang) | [10.1109/TQE.2024.3409309](https://doi.org/10.1109/TQE.2024.3409309) |
| 2024 | Improving Probabilistic Error Cancellation in the Presence of Nonstationary Noise (Dasgupta, Humble) | [10.1109/TQE.2024.3435757](https://doi.org/10.1109/TQE.2024.3435757) |
| 2026 | Robust Design Under Uncertainty in Quantum Error Mitigation (Prodius, Czarnik, McKerns, Sornborger, Cincio) | [10.1109/TQE.2026.3680641](https://doi.org/10.1109/TQE.2026.3680641) |
| 2026 | Extension of Clifford Data Regression Methods for QEM (Pérez-Guijarro, Pagès-Zamora, Fonollosa) | [10.1109/TQE.2026.3677541](https://doi.org/10.1109/TQE.2026.3677541) |

**Assessment: strongest fit (primary target).**
- Publishes *empirical, multi-method, simulator-and-hardware* mitigation studies — Russo *et al.* 2023 is almost exactly our paper type, by the Mitiq authors.
- Still actively publishing QEM in 2026 (two entries), so the topic is not saturated at this venue.
- Open-access, IEEE-indexed, rolling submission (no fixed deadline) — good for a study whose completion date is uncertain.
- Article length (1–32 pages in the sample) accommodates a full benchmark with appendices.
- CfP / scope: <https://tqe.ieee.org>

### 2. IEEE International Conference on Quantum Computing and Engineering (QCE, "IEEE Quantum Week")

Direct hits (proceedings records):

| Year | Paper | DOI |
|---|---|---|
| 2020 | Digital zero noise extrapolation for quantum error mitigation (Giurgica-Tiron, Hindy, LaRose, Mari, Zeng) | [10.1109/QCE49297.2020.00045](https://doi.org/10.1109/QCE49297.2020.00045) |
| 2022 | QUARK: A Framework for Quantum Computing Application Benchmarking (Finžgar *et al.*) | [10.1109/QCE53715.2022.00042](https://doi.org/10.1109/QCE53715.2022.00042) |
| 2023 | Best Practices for Quantum Error Mitigation with Digital Zero-Noise Extrapolation (Majumdar, Rivero, Metz, Hasan, Wang) | [10.1109/QCE57702.2023.00102](https://doi.org/10.1109/QCE57702.2023.00102) |
| 2023 | Application-Oriented Benchmarking of Quantum Generative Learning Using QUARK (Kiwit *et al.*) | [10.1109/QCE57702.2023.00061](https://doi.org/10.1109/QCE57702.2023.00061) |
| 2025 | Digital Zero-Noise Extrapolation with Quantum Circuit Unoptimization (Pelofske, Russo) | [10.1109/QCE65121.2025.00020](https://doi.org/10.1109/QCE65121.2025.00020) |

**Assessment: strong fit (primary conference target).**
- The 2023 Majumdar *et al.* "Best Practices" paper is direct proof that QCE accepts **methodology/practice** papers about dZNE — not only novel-method papers. This is the closest precedent for our contribution type.
- Papers are short (6–13 pages), which suits a focused, single-message benchmark study.
- Has both a main technical track and workshops, giving a fallback if the main track rejects.
- **Risk:** fixed annual deadline (typically spring, *not verified* — check CfP). Missing it costs a year.
- CfP: <https://qce.quantum.ieee.org>

### 3. ACM Transactions on Quantum Computing (TQC) — ISSN 2643-6817

Direct hits:

| Year | Paper | DOI |
|---|---|---|
| 2024 | Increasing the Measured Effective Quantum Volume with Zero Noise Extrapolation (Pelofske, Russo, LaRose, Mari *et al.*) | [10.1145/3680290](https://doi.org/10.1145/3680290) |
| 2024 | Optimization Applications as Quantum Performance Benchmarks (Lubinski, Coffrin, McGeoch, Sathe *et al.*) | [10.1145/3678184](https://doi.org/10.1145/3678184) |
| 2026 | How Many Shots Are Enough for a Quantum Circuit? (Bisicchia, Bocci, Pimentel, Brogi) | [10.1145/3841468](https://doi.org/10.1145/3841468) |

**Assessment: good fit (secondary journal target).**
- Publishes applied ZNE benchmarking (Pelofske 2024) and shot-budget methodology (Bisicchia 2026) — both core to our study.
- Sample articles are long (18–86 pages), suggesting reviewers expect thorough treatment; a *pilot*-sized result would be under-powered here.
- Best used as the target if the pilot is extended into a full, larger-scale study.
- CfP: <https://dl.acm.org/journal/tqc>

### 4. Quantum Information Processing (QIP, Springer) — ISSN 1573-1332

Direct hits:

| Year | Paper | DOI |
|---|---|---|
| 2021 | Classical symmetries and the Quantum Approximate Optimization Algorithm (Shaydulin, Hadfield, Hogg, Safro) | [10.1007/s11128-021-03298-4](https://doi.org/10.1007/s11128-021-03298-4) |
| 2024 | Quantum error mitigation in the regime of high noise using deep neural network (Zhukov, Pogosov) | [10.1007/s11128-024-04296-y](https://doi.org/10.1007/s11128-024-04296-y) |
| 2024 | Echo-evolution data generation for quantum error mitigation via neural networks (Babukhin) | [10.1007/s11128-024-04603-7](https://doi.org/10.1007/s11128-024-04603-7) |

**Assessment: plausible fit (fallback).**
- Does publish QEM, but the recent QEM output skews toward *machine-learning-based* mitigation rather than benchmarking of standard methods.
- The date-sorted probe (most recent 6 papers, any topic) returned mostly teleportation, coherence and QKD papers — the journal's centre of mass is quantum information theory, not applied NISQ benchmarking.
- Viable fallback, weaker topical match than TQE/QCE.

### 5. Quantum Reports (MDPI) — ISSN 2624-960X and Entropy (MDPI) — ISSN 1099-4300

Probe results:
- **Quantum Reports**: the QEM-targeted query returned no directly relevant mitigation-benchmarking papers. Recent output (Grover variants, QKD, fiber gyroscopes, black-hole information) is topically scattered. One adjacent VQE paper: *Simulating Methylamine Using a Symmetry-Adapted, Qubit Excitation-Based VQE*, Makushin & Fedorov, Quantum Reports **7**, 21 (2025), [10.3390/quantum7020021](https://doi.org/10.3390/quantum7020021).
- **Entropy**: essentially no QEM-benchmarking presence. The single relevant hit was *Quantum Error Mitigation in Optimized Circuits for Particle-Density Correlations in Real-Time Dynamics*, Pomarico *et al.*, Entropy **27**, 427 (2025), [10.3390/e27040427](https://doi.org/10.3390/e27040427) — a lattice-gauge-theory application, not a methods benchmark.

**Assessment: weak topical fit — not recommended as primary targets.**
Both are legitimate indexed journals and would technically accept the work, but neither has an
established readership for applied QEM benchmarking. Submitting there would reduce the chance the
paper is read by the people who would use it. Retain only as last-resort fallbacks.

---

## Recommended venue strategy

| Priority | Venue | Rationale | Risk |
|---|---|---|---|
| **1** | IEEE Transactions on Quantum Engineering | Best topical match; rolling deadline; proven acceptance of exactly this paper type (Russo 2023) | Reviewers will expect a rigorous cost model and may ask for hardware data |
| **2** | IEEE QCE (Quantum Week) | Proven acceptance of dZNE *practice* papers; short format suits a focused result | Annual deadline; simulator-only work may be seen as incremental |
| **3** | ACM Transactions on Quantum Computing | Publishes ZNE benchmarking and shot-budget methodology | Expects larger scope than a pilot |
| 4 | Quantum Information Processing | Publishes QEM and QAOA | Recent QEM output skews ML-based |
| 5 | Quantum Reports / Entropy | Indexed, would accept | Little relevant readership |

**Recommendation:** target **IEEE TQE** as the primary destination, with **IEEE QCE** as the
conference route if a hard deadline is useful for forcing completion. Both have *demonstrated*,
recent acceptance of simulator-based, multi-method, reproducible mitigation studies.

## Facts deliberately not asserted here

The following were **not verified** in this pass and must not be cited without checking:
acceptance rates, impact factors, review turnaround times, submission deadlines, page charges,
and open-access fees.
