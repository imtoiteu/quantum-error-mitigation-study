# Venue Decision (round 2, reassessed)

**Compiled:** 2026-09-16. Facts below were retrieved from official calls for papers. Anything not
retrieved is marked **UNKNOWN** and must be checked by the author before submission. No acceptance
probability is estimated and no venue is described as easy.

## What changed since round 1

The contribution was reframed (see `REVIEW_RESPONSE_round2.md` §9) from an implied discovery to a
**bounded integration-failure case study with a reusable validation artifact**. That is a
**quantum-software-engineering** contribution — testing, validation, toolchain/transpiler
correctness — not an error-mitigation methods contribution. The venue set changes accordingly.

**Round 1's fallback reasoning is withdrawn.** IEEE TQE is *not* automatically an easier fallback:
it is a quantum-engineering journal whose error-mitigation output is methods-oriented, and a software
validation case study is a weaker topical match there than at a software venue. Round 1 treated TQE
as a safe second option without evidence; that was unjustified.

## Primary: IEEE Quantum Week (QCE), **QSYS — Software Systems track**

**Verified from the official Call for Technical Papers** (<https://qce.quantum.ieee.org/2026/call-for-technical-papers/>):

| Requirement | Verified value |
|---|---|
| Full paper length | **8–10 pages** including figures, tables and appendices, **plus 2 pages for references** |
| Short paper length | 4–6 pages plus 1 page references |
| Template | `\documentclass[10pt,conference]{IEEEtran}`, **without** `compsoc`; title 24pt, body 10pt |
| Attendance | **"a commitment for at least one author to register and attend the conference in person upon acceptance"** |
| Authorship | must comply with the IEEE Policy on Authorship |
| Review model | **UNKNOWN** — not stated on the page retrieved |
| Deadline | **UNKNOWN** — the technical-papers page refers to a separate deadlines page |
| Fees | **UNKNOWN** — not stated; must not be assumed affordable |

**Track fit, quoted from the call.** QSYS lists *"Testing, validation, and verification of quantum
programs and systems"* and *"Software techniques for error correction and noise mitigation"*. Our
contribution — deterministic validation oracles for an error-mitigation toolchain, plus a measured
integration failure — sits in the intersection of those two bullets.

**Precedent for the paper type at this venue.** Köster & Mauerer, *Benchmarking Error Mitigation:
Artefactual Improvements in Zero-Noise Extrapolation*, is **accepted at IEEE QCE 2026**
(arXiv:2607.09360v2) — a paper whose entire contribution is that a ZNE benchmark result was an
artefact. Also Majumdar *et al.* (QCE 2023, dZNE best practices), Giurgica-Tiron *et al.* (QCE 2020),
Finžgar *et al.* (QCE 2022, benchmarking framework), Pelofske & Russo (QCE 2025).

**Consequence for this manuscript:** it must be **8–10 pages** to qualify as a full paper. The
current draft is shorter and is being expanded with material currently in the supplement (the
bias/variance analysis and the per-instance results), not padded.

## Secondary: IEEE International Conference on Quantum Software (QSW)

**Verified** (<https://services.conferences.computer.org/2026/qsw/qsw-call-for-papers/>). Topic fit is
excellent — the call explicitly lists *"Testing methodologies for quantum and hybrid applications"*,
*"Regression testing and evolution of quantum software"*, *"Compilers, transpilers, simulators,
optimizers, and code generators"*, *"Program equivalence, refinement, and transformation"* and
*"Statistical verification with confidence guarantees"*. Our oracles are regression tests for a
transpiler-sensitive toolchain, so this is arguably the single closest topical match of any venue
considered.

**Blocking fact: the 2026 cycle has closed.** Verified dates: submissions 8 March 2026, extended
"firm" deadline **22 March 2026**, notifications 10 May 2026, camera-ready 31 May 2026. Today is
16 September 2026, so **QSW 2026 cannot be submitted to**. The QSW 2027 call was not available at the
time of writing. Page limits, template, fees and review model for QSW are **UNKNOWN**.

## Tertiary: IEEE Transactions on Quantum Engineering

Retained only as a third option, with its round-1 justification withdrawn. It has a rolling deadline
and publishes empirical mitigation work (Russo *et al.* 2023; Lubinski *et al.* 2023; Prodius *et al.*
2026), but a software-validation case study is a weaker match for a quantum-engineering journal than
for QCE-QSYS or QSW. Adaptation notes in `manuscript/FALLBACK_TQE.md` remain valid if chosen.

## Recommendation

1. **IEEE QCE, QSYS track** — best combination of verified topical fit and demonstrated acceptance of
   this exact paper type. Requires expansion to the verified 8–10 page window and an in-person
   attendance commitment.
2. **IEEE QSW** — closest topical match, but only from the 2027 cycle onward; monitor the call.
3. **IEEE TQE** — third option, not a default fallback.

Submit to **one** venue at a time.

## Deliberately not asserted

Acceptance probability; any deadline, fee, page limit or review model not quoted above; that any
venue is easy; that a workshop or poster acceptance would be equivalent to a full paper.
