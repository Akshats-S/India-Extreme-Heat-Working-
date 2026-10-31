# Course assignment checklist

Source: course handout *Empirical Project: Preparing a Dataset & Replication Package* (Introduction to Environmental Economics, AY 2026-27). This page tracks what the handout asks for versus what exists in this repository. Update it as work progresses.

- **Deadline:** 30 November 2026
- **Group size:** pairs or groups of 3
- **Software:** free choice (this project uses Python)
- **AI tools:** the handout limited AI/LLM use to coding and verification, but the course instructor has since confirmed full freedom to use AI tools. Keep the instructor's confirmation (e.g. the email or message) on file in case it is questioned.
- **Evaluation criteria:** (i) novelty of the topic and research questions with clear links to environmental economics, (ii) dataset coverage (time periods, observations), (iii) correct, clean, reproducible code, (iv) clearly described cleaning steps in the README. Source data must be cited with web links. Instructors and TFs will review the code, and each group member is asked to verify every step.

## Deliverables

| Requirement from handout | Status |
|---|---|
| Register topic (names, dataset, source link, question title) on the shared topic-registration sheet **before** cleaning data; avoid duplicating another group | **Done:** technical lead confirms topic registered and finalized, 2026-10-31 |
| Dataset is open-access / publicly available; permitted project data sharing | **Project access/sharing issue resolved:** technical lead confirmation, 2026-10-31. This records the project's resolution, not a new general license grant |
| Source website/web link cited | Done: IMDWeb, IMD product pages and recommended paper citation; evidence in `docs/source-metadata.md` |
| README: dataset source, coverage, relevance to environmental economics | Complete in source and final package README; economics applications specify additional data needed |
| README: every cleaning/preparation step, in order | Complete, including ordered preparation/analysis in the final package README and supporting guides |
| Code: scripts that take raw data and produce the cleaned dataset, matching the README | Phases 1/2 implemented and tested, including fixed thresholds, daily flags and annual/period summaries (#2-#5) |
| Reproducible with **no manual steps** | Both packages passed in a fresh isolated environment: 42 tests each, repeated outputs identical and extracted-ZIP reproduction successful. `python src/run_project.py` regenerates final outputs after dependency installation |
| 2-3 candidate research questions, each with policy relevance and a course technique (valuation, instrument comparison, CBA/discounting, treatment-effect reasoning) | Complete: three candidate applications in `docs/research-questions.md` and final package RESEARCH_QUESTIONS.md |
| Self-contained folder submitted | Preliminary/final ZIPs are built and verified under `Submissions`; team names are included; review, any required portal details and actual upload remain user actions. No submission is claimed |

## Data-sharing status

The technical lead confirmed on 2026-10-31 that the data-sharing issue has been
resolved. Do not keep this as an unresolved project blocker or repeatedly ask
for the same confirmation. Cite IMD and document the actual source/access
details in the final package; no broader redistribution license is inferred.

## Repository plan

- **This repository (`India-Extreme-Heat-Working-`)** is the working and final source: all code, documentation, issues and AI-assistant instructions live here.
- **A separate submission repository (`india-extreme-heat-submission`)** will hold only what the handout asks for (README, code, candidate research questions, and data as permitted), laid out exactly as requested. It will be built from this repository once the work is finished, so that working files do not need to be stripped out later.

The current completed deliverables are local, self-contained ZIPs under the
sibling `Submissions` directory. Publishing to that private repository remains
a separate action and has not been performed. The handout asks for a folder,
not a particular GitHub hosting arrangement.

## Verification

The course's human responsibility requirement still applies. The lead clarified
that separate teammate review is for teammate contributions, not a gate on the
lead's own work. Record actual automated and human checks distinctly in
`docs/verification-log.md`; do not fabricate human verification.
