# Fallback adaptation note: IEEE TQE

Used only if the IEEE QCE deadline is unreachable. **One submission at a time; not a duplicate submission.**

## Required edits

1. **Document class.** Replace
   `\documentclass[conference]{IEEEtran}` with `\documentclass[journal]{IEEEtran}`
   and drop `\IEEEoverridecommandlockouts` and `\balance`.
2. **Length.** TQE articles are substantially longer than QCE papers (sampled articles run 12–32
   pages). Move the following from `supplementary/` into the main text:
   - the full noise-scaling audit (`supplementary/noise_scaling_audit.md` → a Methods subsection);
   - the complete per-instance tables, currently summarised in Fig. 4;
   - the full regression-test description (currently compressed into Sec. IV-C).
3. **Abstract.** TQE expects a longer structured abstract; expand with an explicit
   Background / Method / Results / Conclusion structure.
4. **Add an "Impact Statement"** — TQE requires one (a short non-technical statement of significance).
   This must be written by the author; it is not drafted here because it is a claims statement.
5. **Keywords.** Use the IEEE taxonomy terms rather than free text.
6. **Anonymity.** TQE is single-anonymous; restore the author block.

## What does NOT change

The experiments, data, analysis, figures, claim traceability and all numerical results are
venue-independent and require no modification.
