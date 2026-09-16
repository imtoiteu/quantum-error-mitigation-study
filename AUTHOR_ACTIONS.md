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

## 2. Venue facts that must be checked against the live CfP (blocking)

`docs/venue-decision.md` records these as **UNKNOWN**; they change annually and were deliberately
not guessed:

- [ ] IEEE QCE next-edition **submission deadline**
- [ ] **Page limit** for the technical-paper track (the manuscript is currently formatted for the
      IEEE conference template; check the current limit and trim/expand accordingly)
- [ ] **Registration and publication fees** — amount unknown; do not assume affordable
- [ ] Whether **in-person or virtual presentation** is mandatory for inclusion in proceedings
- [ ] **Review model** (single- vs double-anonymous) for the next edition
- [ ] Whether the venue requires a specific **AI-use disclosure** wording (a draft disclosure section
      is already in the manuscript; replace it with the venue's required text if one exists)

Official source: <https://qce.quantum.ieee.org>

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
