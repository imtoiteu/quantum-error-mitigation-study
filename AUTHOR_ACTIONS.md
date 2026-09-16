# Author Actions — genuine human decisions still required

Everything listed here needs a person. Nothing here is a task the agent could resolve from the
repository, the code, or public evidence. Items the agent *did* resolve are not listed.

## 1. Identity and affiliation metadata (blocking for submission)

The manuscript currently reads "Author name withheld for review" / "Affiliation withheld for review".
**No author identity, affiliation, ORCID, email, funding source, grant number, ethics approval or
competing-interest statement has been invented.** You must supply:

- [ ] Author list and order
- [ ] Affiliations
- [ ] Corresponding author email
- [ ] ORCID iDs (optional at most venues)
- [ ] Funding / acknowledgement statement, or an explicit "no funding" declaration
- [ ] Competing-interests declaration

Edit the `\author{...}` block in `manuscript/manuscript.tex`. If the target edition uses
double-anonymous review, leave it as-is.

## 2. Venue: no target edition currently has an open call

**Verified 2026-09-16.** This is the most important practical fact in this file.

| Venue / edition | Status |
|---|---|
| IEEE QCE **2026** | **CLOSED** — technical papers were due **27 April 2026** (extended); the conference runs **13–18 September 2026**, i.e. now |
| IEEE QCE **2027** | **Call not published.** All requirements UNKNOWN |
| IEEE QSW **2026** | **CLOSED** — extended firm deadline **22 March 2026** |
| IEEE QSW **2027** | **Call not published.** All requirements UNKNOWN |
| IEEE TQE | Rolling; open today |

**The manuscript was deliberately NOT expanded** to the 8–10 page window retrieved from the QCE 2026
call, because that edition is closed and the 2027 requirements may differ. Padding a paper to a
closed edition's limit would be the wrong action.

**Author actions:**

- [ ] **Decide whether to wait for the QCE 2027 / QSW 2027 calls, or submit to TQE now.** This is a
      genuine judgement call about timing versus topical fit and only you can make it.
- [ ] When a 2027 call appears, **re-verify**: page limit, template version, deadline, review model
      (single/double anonymous), fees, and whether in-person attendance is still mandatory. Only then
      adjust the manuscript length.
- [ ] **QCE 2026 required at least one author to register and attend in person.** If that carries
      over to 2027 and you cannot travel, QCE is not viable and the venue decision changes.
- [ ] Check whether the chosen venue mandates specific **AI-use disclosure** wording; a draft
      disclosure section is already in the manuscript.

**Recorded for reference only (QCE 2026, closed edition):** full papers 8–10 pages plus 2 for
references; `\documentclass[10pt,conference]{IEEEtran}` without `compsoc` (already applied); QSYS
track covers "Testing, validation, and verification of quantum programs and systems" and "Software
techniques for error correction and noise mitigation". Fees were never stated and remain UNKNOWN.

## 3. Decisions the author may wish to override

- [ ] **Venue choice.** Primary IEEE QCE, fallback IEEE TQE, with evidence in
      `docs/venue-decision.md`. If the QCE deadline is unreachable, switch to TQE using
      `manuscript/FALLBACK_TQE.md`. **Submit to one venue only.**
- [ ] **Scope of the retraction statement.** Section VII retracts the earlier frozen study's
      in-loop headline. Confirm you are comfortable with the wording, since it concerns your own
      prior artifact.
- [ ] **Repository visibility.** The paper states the repository is private and will be made public
      on acceptance, and deliberately does **not** claim public availability. If you prefer to make
      it public now, update Section IX and the data-availability wording together.

## 4. Deliverable the agent could not produce

- [ ] **Editable DOCX.** `pandoc` is not installed in this environment and installing it was out of
      scope, so no DOCX was generated. The authoritative deliverables are the LaTeX source and the
      compiled PDF. If a DOCX is required, run
      `pandoc manuscript/manuscript.tex -o manuscript.docx --bibliography=manuscript/references.bib`
      on a machine with pandoc and **check the output**, particularly equations and tables.

## 5. Scientific judgement calls worth a second opinion

- [ ] The literature search is **bounded**: arXiv's API was rate-limited from this host, so no
      systematic arXiv sweep or forward-citation analysis of UNITED / Majumdar was performed
      (`docs/novelty-matrix.md` §6). A librarian-grade search before submission is advisable, and
      would either confirm or narrow the contribution.
- [ ] Full text of arXiv:2608.28535 was **not** assessed. If it contains a matched-budget ZNE-vs-REM
      comparison on QAOA, contribution C2 weakens to a replication. C1 (the defect) is unaffected.
- [ ] Whether to invest compute in a **corrected in-loop experiment**, which the paper currently
      declines to claim anything about.
