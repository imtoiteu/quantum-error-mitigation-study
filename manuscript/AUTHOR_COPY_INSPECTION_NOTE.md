# Inspection note — `manuscript_author_copy_no_ai_statement`

**Not part of the manuscript.** Separate note, as requested. Date: 2026-09-16.

## Files delivered

| File | Role |
|---|---|
| `manuscript/manuscript_author_copy_no_ai_statement.pdf` | final exported PDF (6 pages, letter, IEEEtran `[10pt,conference]`) |
| `manuscript/manuscript_author_copy_no_ai_statement.tex` | editable source |
| `manuscript/manuscript_author_copy_no_ai_statement.bbl` | bibliography for that source |

The venue-compliant version (`manuscript/manuscript.tex` / `.pdf`) and all disclosure material are
**unchanged and kept separately**. This copy does not replace them. Nothing was submitted or published.

## What was visually inspected

The **exported PDF was rendered to images and inspected page by page**, not judged from build logs.

| Page | Inspected | Outcome |
|---|---|---|
| 1 | title, author block, abstract, intro | clean after fixing a paragraph that read as a continuation |
| 2 | Tables I–II, inline oracle table, body | clean; numeric columns aligned, units and precision consistent |
| 3 | Fig. 1 (pipeline diagram) at printed size, body | clean after three rounds of geometry correction |
| 4 | Tables III–V (full-width), body | clean; no clipped cells or overlapping rules |
| 5 | Figs. 2–3 at printed size, references start | clean after moving Fig. 3's legend off the data |
| 6 | references | clean |

Figure source files were also inspected directly at full resolution:
`figures/fig0_pipeline.png`, `figures/figR2_perinstance.png`.

## Defects found and corrected

1. **Fig. 3 legend obscured data.** The in-axes legend overlapped the `k33` bars in the
   `dev_algiers` panel. Moved to a shared legend below both panels, outside every axes; added
   y-margin so no bar touches the frame. No data changed.
2. **Fig. 3 type size inconsistent with Fig. 2.** Figure width matched so both render at comparable
   type size on the page.
3. **Fig. 1 box text overflowed its borders** ("coupling map, basis" and the DEFECT 2 text). Box
   font reduced to a uniform 6.6 pt within the figure, DEFECT 2 text re-wrapped, box geometry
   recomputed so the rightmost box ends at 0.966 of the axes width.
4. **Fig. 1 annotation collisions.** The "M3 solves this via `final_measurement_mapping`" note
   overlapped first the calibration box and then the footer line; relocated to the clear band
   between the DEFECT 2 box and the footer.
5. **Paragraph read as a continuation.** A `\noindent` on an ordinary new paragraph in §II removed
   its indent; removed so it follows the template's body-paragraph rule. The remaining `\noindent`
   in §IV-A is correct — it follows a centred display table, not a paragraph.

After each correction the affected page and every page whose pagination changed were re-rendered
and re-inspected.

## Verification of this copy

- **Author:** Tran Thi Toi, Military Science Academy, Hanoi, Vietnam, toitt2001@gmail.com — sole and
  corresponding author. Present in the rendered PDF and in PDF metadata (`Author: Tran Thi Toi`).
- **AI-assistance statements removed** from this copy: the "Use of AI assistance" section was
  deleted in full. Scans return **zero** matches for AI/LLM/assistance terms in (a) extracted PDF
  body text, (b) raw PDF bytes including metadata streams and annotations, and (c) the LaTeX source
  including comments. `Creator` and `Producer` metadata fields are empty, so no tool fingerprint
  remains. There are no tracked changes (plain LaTeX, no `changes`/`todonotes` packages).
- **No replacement disclaimer was inserted**, and **no claim is made that AI was not used** or that
  the work was done unassisted — scan for such phrasing returns zero matches.
- **Scientific content unchanged**: results, tables, figures, citations, numbering and
  cross-references are identical to the venue version. Only the author block, the removal of the
  disclosure section, and the presentation fixes above differ.
- Legitimate technical content was **not** removed; this paper contains no technical AI references
  to preserve or strip.

## Known issues that remain

1. **Content defect inherited from the main manuscript — not fixed here, and it needs fixing there.**
   §VI (page 3, right column, first paragraph of "Consequences on a benchmark") states the run was
   made *"from a fresh seed namespace on a clean committed tree."* The clean-tree part **overstates
   the evidence**: the stored rows record `git_dirty=True`, and verified execution-file hashes do not
   imply a clean working tree. This wording was already corrected in `REVIEW_RESPONSE_round2.md` §8
   and `FINAL_REVIEW.md`, but the manuscript body was missed. It is a factual claim, so it is
   **reported rather than silently edited** in this presentation-only pass. It should be corrected in
   the next content revision of both the venue version and this copy.
2. **Page 6 is about two-thirds empty**, holding only references [8]–[16]. `\balance` is applied and
   the two columns on that page are even. This is normal for a paper whose references spill over, and
   it was **not** "fixed" by shrinking fonts or altering margins, which the brief forbids.
3. **Grayscale legibility of the grouped bar charts (Figs. 2b, 2c, 3)** relies on consistent
   left-to-right bar order within each group plus the legend order, since the four series differ by
   hue. They remain decodable in grayscale but not at a glance. Redesigning to hatching was judged an
   unnecessary cosmetic redesign under the stopping rule; flagged so you can decide.
4. **One 3.7 pt overfull horizontal box** remains (§IV-A body text). It is below the visual threshold
   — no text crosses the column rule in the rendered page — and was left rather than re-flowed.
5. **This copy reflects the round-2 result set.** The round-3 rerun was still in progress when this
   copy was exported, so its numbers will change when that analysis lands. No numbers were altered
   here.

## Not done, by scope

No scientific claims, results, experimental design or venue were changed; no experiments were
started, and no scientific revisions were reopened.
