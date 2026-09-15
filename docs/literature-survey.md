# Literature Survey — Error Mitigation for Variational Quantum Algorithms

**Compiled:** 2026-09-15
**Method:** Metadata for every entry was retrieved programmatically from the
[Crossref REST API](https://api.crossref.org) (`query.bibliographic`, and ISSN-scoped
`/journals/{issn}/works` queries). Titles, author lists, years, venues, volumes, pages and
DOIs below are therefore taken from publisher-deposited records, not from memory.
The retrieval script is `experiments/lit/` → see `docs/feasibility-report.md` for the exact commands.

## Verification status legend

Because this is a feasibility survey, not all papers were read in full. Each entry carries a
status so that downstream claims can be traced:

| Status | Meaning |
|---|---|
| **[M]** | Metadata verified via Crossref. Content summary is from abstract/search snippets only. |
| **[A]** | Metadata verified **and** abstract read directly from the publisher/arXiv landing page. |
| **[F]** | Metadata verified and full text consulted. |

**No entry in this file was written from unverified recall.** Fields that were not established
in this pass are marked `not verified` rather than guessed. This matters: several plausible-sounding
papers surfaced by keyword search turned out to be preprints, posted-content records or peer-review
stubs, and were excluded.

---

## A. Foundational error-mitigation methods (theory + first demonstrations)

### A1 [A] Error Mitigation for Short-Depth Quantum Circuits
- **Authors:** K. Temme, S. Bravyi, J. M. Gambetta — **Year:** 2017 — **Venue:** Physical Review Letters **119**, 180509
- **DOI:** [10.1103/PhysRevLett.119.180509](https://doi.org/10.1103/PhysRevLett.119.180509)
- **Algorithm:** generic short-depth expectation-value estimation (not VQE/QAOA-specific)
- **Noise model:** generic Markovian noise with known generator; analysis in terms of a noise rate λ
- **Mitigation method:** introduces **both** Richardson/zero-noise extrapolation and probabilistic error cancellation (PEC)
- **Baselines:** unmitigated noisy expectation value
- **Metrics:** bias in expectation value; sampling overhead
- **Hardware/simulator:** theory
- **Main findings:** expectation values can be debiased to order λ^n by extrapolating over rescaled noise, at the cost of variance amplification
- **Limitations:** assumes ability to rescale noise exactly; overhead grows exponentially in circuit volume
- **Relevance:** the origin of ZNE. Defines the bias/variance trade-off this study measures empirically.

### A2 [A] Efficient Variational Quantum Simulator Incorporating Active Error Minimization
- **Authors:** Y. Li, S. C. Benjamin — **Year:** 2017 — **Venue:** Physical Review X **7**, 021050
- **DOI:** [10.1103/PhysRevX.7.021050](https://doi.org/10.1103/PhysRevX.7.021050)
- **Algorithm:** variational quantum simulation
- **Mitigation method:** independently proposes error extrapolation ("active error minimization") inside a variational loop
- **Relevance:** first proposal to put extrapolation *inside* a VQA optimisation loop — the "in-loop" arm of our pilot.

### A3 [M] Practical Quantum Error Mitigation for Near-Future Applications
- **Authors:** S. Endo, S. C. Benjamin, Y. Li — **Year:** 2018 — **Venue:** Physical Review X **8**, 031027
- **DOI:** [10.1103/PhysRevX.8.031027](https://doi.org/10.1103/PhysRevX.8.031027)
- **Relevance:** makes extrapolation and quasi-probability practical under realistic gate-set assumptions; standard citation for QEM overhead accounting.

### A4 [A] Quantum error mitigation *(review)*
- **Authors:** Z. Cai, R. Babbush, S. C. Benjamin, S. Endo, W. J. Huggins, *et al.* (8 authors) — **Year:** 2023 — **Venue:** Reviews of Modern Physics **95**, 045005
- **DOI:** [10.1103/RevModPhys.95.045005](https://doi.org/10.1103/RevModPhys.95.045005)
- **Relevance:** the authoritative review. Our taxonomy of methods and overhead definitions follow it. Establishes that *method comparison under matched cost* is the open practical question.

### A5 [M] Fundamental limits of quantum error mitigation
- **Authors:** R. Takagi, S. Endo, S. Minagawa, M. Gu — **Year:** 2022 — **Venue:** npj Quantum Information **8**
- **DOI:** [10.1038/s41534-022-00618-z](https://doi.org/10.1038/s41534-022-00618-z)
- **Main findings:** lower bounds on the sampling cost of *any* mitigation strategy; cost grows exponentially with circuit depth
- **Relevance:** theoretical justification for why a shot-budget-matched comparison is the honest one.

### A6 [M] Exponentially tighter bounds on limitations of quantum error mitigation
- **Authors:** Y. Quek, D. Stilck França, S. Khatri, J. J. Meyer, *et al.* (5 authors) — **Year:** 2024 — **Venue:** Nature Physics **20**, 1648–1658
- **DOI:** [10.1038/s41567-024-02536-7](https://doi.org/10.1038/s41567-024-02536-7)
- **Relevance:** strengthens A5. Directly supports our instruction *not* to claim advantage: mitigation cannot be assumed to scale.

### A7 [M] Universal Sampling Lower Bounds for Quantum Error Mitigation
- **Authors:** R. Takagi, H. Tajima, M. Gu — **Year:** 2023 — **Venue:** Physical Review Letters **131**, 210602
- **DOI:** [10.1103/PhysRevLett.131.210602](https://doi.org/10.1103/PhysRevLett.131.210602)

---

## B. Zero-noise extrapolation — implementations and variants

### B1 [A] Digital zero noise extrapolation for quantum error mitigation
- **Authors:** T. Giurgica-Tiron, Y. Hindy, R. LaRose, A. Mari, W. J. Zeng — **Year:** 2020
- **Venue:** **2020 IEEE International Conference on Quantum Computing and Engineering (QCE / "IEEE Quantum Week")**, pp. 306–316
- **DOI:** [10.1109/QCE49297.2020.00045](https://doi.org/10.1109/QCE49297.2020.00045)
- **Algorithm:** benchmark circuits (randomized benchmarking-style, small observables)
- **Noise model:** depolarizing and hardware noise
- **Mitigation method:** **unitary folding** (global / local) as a gate-level, compiler-only noise-scaling technique + several extrapolation fits (linear, Richardson, poly, exponential)
- **Baselines:** unmitigated
- **Metrics:** absolute error of expectation value
- **Hardware/simulator:** simulator + IBM/Rigetti hardware
- **Main findings:** noise can be scaled digitally without pulse access; fit choice materially changes results
- **Limitations:** folding assumes noise scales ~linearly with gate count — only approximately true
- **Relevance:** **this is the exact ZNE implementation our pilot uses** (via Mitiq), and it is an IEEE Quantum Week paper — direct evidence our target venue accepts this work type.

### B2 [M] Zero-noise extrapolation for quantum-gate error mitigation with identity insertions
- **Authors:** A. He, B. Nachman, W. A. de Jong, C. W. Bauer — **Year:** 2020 — **Venue:** Physical Review A **102**, 012426
- **DOI:** [10.1103/PhysRevA.102.012426](https://doi.org/10.1103/PhysRevA.102.012426)
- **Relevance:** alternative noise-scaling primitive (identity insertion). A sensitivity axis we deliberately do **not** vary in the pilot; noted as a threat to external validity.

### B3 [M] Computationally efficient zero-noise extrapolation for quantum-gate-error mitigation
- **Authors:** V. R. Pascuzzi, A. He, C. W. Bauer, W. A. de Jong, B. Nachman — **Year:** 2022 — **Venue:** Physical Review A **105**, 042406
- **DOI:** [10.1103/PhysRevA.105.042406](https://doi.org/10.1103/PhysRevA.105.042406)

### B4 [M] Best Practices for Quantum Error Mitigation with Digital Zero-Noise Extrapolation
- **Authors:** R. Majumdar, P. Rivero, F. Metz, A. Hasan, D. S. Wang — **Year:** 2023
- **Venue:** **2023 IEEE QCE (Quantum Week)**, pp. 881–887
- **DOI:** [10.1109/QCE57702.2023.00102](https://doi.org/10.1109/QCE57702.2023.00102)
- **Relevance:** closest "methodology guidance" paper to ours, at our #1 target venue. Establishes that IEEE QCE publishes *practice/benchmarking* papers on dZNE rather than only new methods.

### B5 [M] Increasing the Measured Effective Quantum Volume with Zero Noise Extrapolation
- **Authors:** E. Pelofske, V. Russo, R. LaRose, A. Mari, *et al.* (8 authors) — **Year:** 2024
- **Venue:** **ACM Transactions on Quantum Computing 5**, 1–18
- **DOI:** [10.1145/3680290](https://doi.org/10.1145/3680290)
- **Relevance:** demonstrates ACM TQC accepts applied ZNE benchmarking studies. Second venue-fit data point.

### B6 [M] Multi-exponential error extrapolation and combining error mitigation techniques for NISQ applications
- **Authors:** Z. Cai — **Year:** 2021 — **Venue:** npj Quantum Information **7**
- **DOI:** [10.1038/s41534-021-00404-3](https://doi.org/10.1038/s41534-021-00404-3)
- **Relevance:** explicitly about **combining** mitigation techniques — the ZNE+REM composition arm of our pilot.

### B7 [M] Synergetic quantum error mitigation by randomized compiling and zero-noise extrapolation
- **Authors:** T. Kurita, H. Qassim, M. Ishii, H. Oshima, *et al.* (6 authors) — **Year:** 2023 — **Venue:** Quantum **7**, 1184
- **DOI:** [10.22331/q-2023-11-20-1184](https://doi.org/10.22331/q-2023-11-20-1184)
- **Relevance:** composition of methods again; also shows randomized compiling is a confounder we must hold fixed.

---

## C. Measurement / readout error mitigation

### C1 [A] Scalable Mitigation of Measurement Errors on Quantum Computers
- **Authors:** P. D. Nation, H. Kang, N. Sundaresan, J. M. Gambetta — **Year:** 2021 — **Venue:** PRX Quantum **2**, 040326
- **DOI:** [10.1103/PRXQuantum.2.040326](https://doi.org/10.1103/PRXQuantum.2.040326)
- **Algorithm:** generic sampling; demonstrated on Bernstein-Vazirani and similar
- **Noise model:** device readout/assignment error
- **Mitigation method:** **M3** — matrix-free measurement mitigation restricted to the subspace of observed bitstrings
- **Baselines:** full calibration-matrix inversion; unmitigated
- **Metrics:** fidelity/expectation error; classical runtime and memory
- **Main findings:** avoids the 2^n calibration-matrix cost; scales to 100+ qubits
- **Relevance:** the readout-mitigation method our pilot uses as its second mitigation arm.

### C2 [A] Mitigating measurement errors in multiqubit experiments
- **Authors:** S. Bravyi, S. Sheldon, A. Kandala, D. C. McKay, J. M. Gambetta — **Year:** 2021 — **Venue:** Physical Review A **103**, 042605
- **DOI:** [10.1103/PhysRevA.103.042605](https://doi.org/10.1103/PhysRevA.103.042605)
- **Mitigation method:** tensored / correlated calibration models, continuous-time Markov noise model for readout
- **Relevance:** establishes that readout error is often *the dominant* error source for low-depth circuits — motivating why REM is a fair competitor to ZNE, not a footnote.

### C3 [M] Conditionally Rigorous Mitigation of Multiqubit Measurement Errors
- **Authors:** M. R. Geller — **Year:** 2021 — **Venue:** Physical Review Letters **127**, 090502
- **DOI:** [10.1103/PhysRevLett.127.090502](https://doi.org/10.1103/PhysRevLett.127.090502)

### C4 [M] Efficient separate quantification of state preparation errors and measurement errors
- **Authors:** H. Yu, T.-C. Wei — **Year:** 2025 — **Venue:** Quantum **9**, 1724
- **DOI:** [10.22331/q-2025-05-05-1724](https://doi.org/10.22331/q-2025-05-05-1724)
- **Relevance:** SPAM separability — a known confounder when attributing improvement to REM.

### C5 [M] Bayesian mitigation of measurement errors in multiqubit experiments
- **Authors:** F. Cosco, F. Plastina, N. Lo Gullo — **Year:** 2025 — **Venue:** Physical Review A **112**
- **DOI:** [10.1103/d65d-x8lt](https://doi.org/10.1103/d65d-x8lt)

---

## D. Learning-based and alternative mitigation (scope boundary for this study)

### D1 [M] Error mitigation with Clifford quantum-circuit data (CDR)
- **Authors:** P. Czarnik, A. Arrasmith, P. J. Coles, L. Cincio — **Year:** 2021 — **Venue:** Quantum **5**, 592
- **DOI:** [10.22331/q-2021-11-26-592](https://doi.org/10.22331/q-2021-11-26-592)
- **Relevance:** the main method we **exclude** from the pilot, because its training cost (>30 circuits/estimate) makes budget-matching a different experiment. Documented as future work.

### D2 [M] Improving the efficiency of learning-based error mitigation
- **Authors:** P. Czarnik, M. McKerns, A. T. Sornborger, L. Cincio — **Year:** 2025 — **Venue:** Quantum **9**, 1727
- **DOI:** [10.22331/q-2025-05-05-1727](https://doi.org/10.22331/q-2025-05-05-1727)

### D3 [M] Extension of Clifford Data Regression Methods for Quantum Error Mitigation
- **Authors:** C. Pérez-Guijarro, A. Pagès-Zamora, J. R. Fonollosa — **Year:** 2026 — **Venue:** **IEEE Transactions on Quantum Engineering 7**, 1–22
- **DOI:** [10.1109/TQE.2026.3677541](https://doi.org/10.1109/TQE.2026.3677541)
- **Relevance:** venue-fit evidence — IEEE TQE actively publishes QEM method papers *in 2026*.

### D4 [M] Probabilistic error cancellation with sparse Pauli–Lindblad models on noisy quantum processors
- **Authors:** E. van den Berg, Z. K. Minev, A. Kandala, K. Temme — **Year:** 2023 — **Venue:** Nature Physics **19**, 1116–1121
- **DOI:** [10.1038/s41567-023-02042-2](https://doi.org/10.1038/s41567-023-02042-2)
- **Relevance:** PEC is excluded from the pilot (requires device-specific noise learning); noted as the strongest "method we did not test".

### D5 [M] Quantum Error Mitigation as a Universal Error Reduction Technique
- **Authors:** Y. Suzuki, S. Endo, K. Fujii, Y. Tokunaga — **Year:** 2022 — **Venue:** PRX Quantum **3**, 010345
- **DOI:** [10.1103/PRXQuantum.3.010345](https://doi.org/10.1103/PRXQuantum.3.010345)

---

## E. VQE / QAOA under noise

### E1 [M] Error mitigation extends the computational reach of a noisy quantum processor
- **Authors:** A. Kandala, K. Temme, A. D. Córcoles, A. Mezzacapo, *et al.* (6 authors) — **Year:** 2019 — **Venue:** Nature **567**, 491–495
- **DOI:** [10.1038/s41586-019-1040-7](https://doi.org/10.1038/s41586-019-1040-7)
- **Algorithm:** VQE (H2, LiH, BeH2) — **Mitigation:** ZNE via pulse stretching — **Hardware:** IBM superconducting
- **Main findings:** first convincing demonstration that ZNE materially improves VQE energies on hardware
- **Limitations:** single device, no budget-matched comparison against other methods, no error bars across repeated independent runs
- **Relevance:** the canonical "ZNE helps VQE" result. Our study asks whether it still holds when cost is held constant.

### E2 [M] Noise-induced barren plateaus in variational quantum algorithms
- **Authors:** S. Wang, E. Fontana, M. Cerezo, K. Sharma, *et al.* (7 authors) — **Year:** 2021 — **Venue:** Nature Communications **12**
- **DOI:** [10.1038/s41467-021-27045-6](https://doi.org/10.1038/s41467-021-27045-6)
- **Relevance:** noise flattens the VQA cost landscape exponentially. Explains why in-loop mitigation may fail even when estimation-stage mitigation succeeds — a hypothesis the pilot tests directly (RQ3).

### E3 [M] Beyond unital noise in variational quantum algorithms: noise-induced barren plateaus and limit sets
- **Authors:** P. Singkanipa, D. A. Lidar — **Year:** 2025 — **Venue:** Quantum **9**, 1617
- **DOI:** [10.22331/q-2025-01-30-1617](https://doi.org/10.22331/q-2025-01-30-1617)
- **Relevance:** extends E2 to non-unital (amplitude-damping) noise — which is present in our thermal-relaxation noise models.

### E4 [M] Design-Space Exploration of Quantum Approximate Optimization Algorithm under Noise
- **Authors:** M. Alam, A. Ash-Saki, S. Ghosh — **Year:** 2020 — **Venue:** 2020 IEEE Custom Integrated Circuits Conference (CICC), pp. 1–4
- **DOI:** [10.1109/CICC48029.2020.9075903](https://doi.org/10.1109/CICC48029.2020.9075903)
- **Main findings:** the optimal QAOA depth p is bounded by device noise; deeper is not better under realistic noise
- **Relevance:** justifies restricting the pilot to small p (p ∈ {1,2}) and treating p as a noise-sensitivity axis.

### E5 [M] Evaluating Quantum Approximate Optimization Algorithm: A Case Study
- **Authors:** R. Shaydulin, Y. Alexeev — **Year:** 2019 — **Venue:** 2019 Tenth International Green and Sustainable Computing Conference (IGSC), pp. 1–6
- **DOI:** [10.1109/IGSC48788.2019.8957201](https://doi.org/10.1109/IGSC48788.2019.8957201)
- **Relevance:** methodology template for small-scale QAOA empirical studies (optimizer choice dominates).

### E6 [M] Classical symmetries and the Quantum Approximate Optimization Algorithm
- **Authors:** R. Shaydulin, S. Hadfield, T. Hogg, I. Safro — **Year:** 2021 — **Venue:** **Quantum Information Processing 20**
- **DOI:** [10.1007/s11128-021-03298-4](https://doi.org/10.1007/s11128-021-03298-4)
- **Relevance:** venue-fit evidence for QIP; also a source of symmetry-based post-selection (an alternative mitigation we exclude).

### E7 [M] Distributionally Robust Variational Quantum Algorithms With Shifted Noise
- **Authors:** Z. He, B. Peng, Y. Alexeev, Z. Zhang — **Year:** 2024 — **Venue:** **IEEE Transactions on Quantum Engineering 5**, 1–12
- **DOI:** [10.1109/TQE.2024.3409309](https://doi.org/10.1109/TQE.2024.3409309)
- **Relevance:** direct venue-fit evidence: IEEE TQE publishes empirical VQA-under-noise studies.

### E8 [M] Scalable error mitigation for noisy quantum circuits produces competitive expectation values
- **Authors:** Y. Kim, C. J. Wood, T. J. Yoder, S. T. Merkel, *et al.* (7 authors) — **Year:** 2023 — **Venue:** Nature Physics **19**, 752–759
- **DOI:** [10.1038/s41567-022-01914-3](https://doi.org/10.1038/s41567-022-01914-3)

### E9 [M] Evidence for the utility of quantum computing before fault tolerance
- **Authors:** Y. Kim, A. Eddins, S. Anand, K. X. Wei, *et al.* (11 authors) — **Year:** 2023 — **Venue:** Nature **618**, 500–505
- **DOI:** [10.1038/s41586-023-06096-3](https://doi.org/10.1038/s41586-023-06096-3)
- **Relevance:** the highest-profile ZNE-at-scale claim. Its rapid classical refutation (see E10) is a cautionary precedent cited in our threats-to-validity.

### E10 [M] Fast and converged classical simulations of evidence for the utility of quantum computing before fault tolerance
- **Authors:** T. Begušić, J. Gray, G. K.-L. Chan — **Year:** 2024 — **Venue:** Science Advances **10**
- **DOI:** [10.1126/sciadv.adk4321](https://doi.org/10.1126/sciadv.adk4321)
- **Relevance:** **methodological warning.** A headline mitigation result was matched classically within months. Reinforces the instruction not to claim advantage.

---

## F. Benchmarking methodology and reproducibility

### F1 [A] Unifying and benchmarking state-of-the-art quantum error mitigation techniques
- **Authors:** D. Bultrini, M. H. Gordon, P. Czarnik, A. Arrasmith, *et al.* (7 authors) — **Year:** 2023 — **Venue:** Quantum **7**, 1034
- **DOI:** [10.22331/q-2023-06-06-1034](https://doi.org/10.22331/q-2023-06-06-1034)
- **Mitigation methods:** ZNE, CDR, virtual distillation and their compositions, in a unified framework
- **Main findings:** combinations can outperform individual methods, but not uniformly; performance is problem-dependent
- **Limitations:** **comparison is largely per-circuit-execution, not per-total-shot**; limited noise-strength sweep
- **Relevance:** **the closest prior work.** Our gap is defined relative to this paper — see `docs/novelty-gap.md`.

### F2 [A] Volumetric Benchmarking of Error Mitigation with Qermit
- **Authors:** C. Cirstoiu, S. Dilkes, D. Mills, S. Sivarajah, R. Duncan — **Year:** 2023 — **Venue:** Quantum **7**, 1059
- **DOI:** [10.22331/q-2023-07-13-1059](https://doi.org/10.22331/q-2023-07-13-1059)
- **Main findings:** applies volumetric benchmarking to mitigation; provides a reusable software framework (Qermit)
- **Relevance:** second-closest prior work, and the model for how to structure a reproducible mitigation benchmark.

### F3 [M] Testing Platform-Independent Quantum Error Mitigation on Noisy Quantum Computers
- **Authors:** V. Russo, A. Mari, N. Shammah, R. LaRose, W. J. Zeng — **Year:** 2023 — **Venue:** **IEEE Transactions on Quantum Engineering 4**, 1–18
- **DOI:** [10.1109/TQE.2023.3305232](https://doi.org/10.1109/TQE.2023.3305232)
- **Main findings:** runs ZNE and PEC across IBM, IonQ and Rigetti via a platform-independent stack (Mitiq)
- **Relevance:** **strongest venue-fit evidence.** An empirical, multi-method, reproducible mitigation study published in our #1 journal target, by the Mitiq authors.

### F4 [M] Mitiq: A software package for error mitigation on noisy quantum computers
- **Authors:** R. LaRose, A. Mari, S. Kaiser, P. J. Karalekas, *et al.* (19 authors) — **Year:** 2022 — **Venue:** Quantum **6**, 774
- **DOI:** [10.22331/q-2022-08-11-774](https://doi.org/10.22331/q-2022-08-11-774)
- **Relevance:** the software our pilot depends on (v1.1.0). Citing it is mandatory.

### F5 [M] Application-Oriented Performance Benchmarks for Quantum Computing
- **Authors:** T. Lubinski, S. Johri, P. Varosy, J. Coleman, *et al.* (9 authors) — **Year:** 2023 — **Venue:** **IEEE Transactions on Quantum Engineering 4**, 1–32
- **DOI:** [10.1109/TQE.2023.3253761](https://doi.org/10.1109/TQE.2023.3253761)
- **Relevance:** the benchmarking-methodology standard we follow (fixed problem instances, reported shot counts, released code).

### F6 [M] Optimization Applications as Quantum Performance Benchmarks
- **Authors:** T. Lubinski, C. Coffrin, C. McGeoch, P. Sathe, *et al.* (7 authors) — **Year:** 2024 — **Venue:** **ACM Transactions on Quantum Computing 5**, 1–44
- **DOI:** [10.1145/3678184](https://doi.org/10.1145/3678184)
- **Relevance:** QAOA/MaxCut benchmarking protocol; source of our approximation-ratio metric definition.

### F7 [M] QUARK: A Framework for Quantum Computing Application Benchmarking
- **Authors:** J. R. Finžgar, P. Ross, L. Hölscher, J. Klepsch, A. Luckow — **Year:** 2022 — **Venue:** **2022 IEEE QCE (Quantum Week)**, pp. 226–237
- **DOI:** [10.1109/QCE53715.2022.00042](https://doi.org/10.1109/QCE53715.2022.00042)
- **Relevance:** reproducibility-framework design (config-as-artifact, seeded runs) that our `configs/` layout imitates.

### F8 [M] Measuring the capabilities of quantum computers
- **Authors:** T. Proctor, K. Rudinger, K. Young, E. Nielsen, R. Blume-Kohout — **Year:** 2021 — **Venue:** Nature Physics **18**, 75–79
- **DOI:** [10.1038/s41567-021-01409-7](https://doi.org/10.1038/s41567-021-01409-7)
- **Relevance:** volumetric benchmarking methodology.

### F9 [M] 1-2-3 Reproducibility for Quantum Software Experiments
- **Authors:** W. Mauerer, S. Scherzinger — **Year:** 2022 — **Venue:** 2022 IEEE Int. Conf. on Software Analysis, Evolution and Reengineering (SANER), pp. 1247–1248
- **DOI:** [10.1109/SANER53432.2022.00148](https://doi.org/10.1109/SANER53432.2022.00148)
- **Relevance:** concrete reproducibility checklist for quantum software experiments; our repository layout is checked against it.

### F10 [M] How Many Shots Are Enough for a Quantum Circuit?
- **Authors:** R. Bisicchia, G. Bocci, J. F. Pimentel, A. Brogi — **Year:** 2026 — **Venue:** **ACM Transactions on Quantum Computing**
- **DOI:** [10.1145/3841468](https://doi.org/10.1145/3841468)
- **Relevance:** shot-budget determination as a first-class research question at a target venue — supports the framing of our RQ2.

### F11 [M] Robust Design Under Uncertainty in Quantum Error Mitigation
- **Authors:** I. Prodius, P. Czarnik, M. McKerns, A. T. Sornborger, L. Cincio — **Year:** 2026 — **Venue:** **IEEE Transactions on Quantum Engineering 7**, 1–13
- **DOI:** [10.1109/TQE.2026.3680641](https://doi.org/10.1109/TQE.2026.3680641)
- **Relevance:** 2026 TQE QEM paper — confirms the venue is actively receptive *now*.

---

## G. Near-miss preprints (examined specifically to test our novelty claim)

These two were found by targeted search for prior work on **budget-matched** mitigation comparison.
Both are **single-author arXiv preprints with no located peer-reviewed venue**, and their abstracts
were read directly.

### G1 [A] The finite-shot help-harm boundary of zero-noise extrapolation
- **Author:** V. Scavino Alfaro (single author) — **Submitted:** 2026-05-07 — **Venue:** arXiv:2605.08251 — *no peer-reviewed venue located*
- **URL:** <https://arxiv.org/abs/2605.08251>
- **Approach:** primarily analytical (local expansion of MSE), validated with Qiskit Aer and IBM checks
- **Scope:** **ZNE only.** Defines a bias/variance crossover ("help-harm boundary") for fixed Richardson ZNE
- **Does NOT:** compare ZNE against readout/measurement mitigation; does not study VQE or QAOA specifically (uses generic "variational energy measurements")
- **Overlap with us:** **substantial and important.** It establishes analytically that ZNE can *harm* under finite shots — the effect our RQ1 measures empirically
- **Residual gap:** no cross-method comparison, no QAOA, no multi-noise-model sweep, no released reproducible artifact

### G2 [A] Hardware-Efficient Error Mitigation and Shot-Efficient Sampling on IBM Quantum Hardware
- **Author:** S. Chongder (single author, IIT Jodhpur) — **Submitted:** 2026-08-28 — **Venue:** arXiv:2608.28535 — *no peer-reviewed venue located*
- **URL:** <https://arxiv.org/abs/2608.28535>
- **Scope:** six techniques (calibration-aware qubit selection, depth scaling, ZNE, dynamical decoupling, REM, repeated-shot estimation) on IBM hardware under a constrained budget
- **Does NOT:** study VQE or QAOA specifically; does not present an explicit equal-total-shot cross-method comparison
- **Overlap with us:** moderate — shares the "constrained execution budget" framing
- **Residual gap:** hardware-only, no controlled noise-strength sweep, no algorithm-level (VQE/QAOA) objective metrics

> **Honest assessment:** G1 in particular *narrows* our claimed gap considerably and must be cited
> prominently. See `docs/novelty-gap.md` for how the gap is re-scoped in light of it.

---

## Summary counts

| Category | Entries |
|---|---|
| A. Foundational QEM theory | 7 |
| B. ZNE implementations/variants | 7 |
| C. Measurement/readout mitigation | 5 |
| D. Learning-based / excluded methods | 5 |
| E. VQE/QAOA under noise | 10 |
| F. Benchmarking & reproducibility | 11 |
| G. Near-miss preprints | 2 |
| **Total** | **47** |

Peer-reviewed entries: **45 of 47** (G1, G2 are unrefereed preprints, flagged as such).
Target-venue entries (IEEE QCE, IEEE TQE, ACM TQC, QIP): **11**.
