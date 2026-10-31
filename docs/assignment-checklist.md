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
| Register topic (names, dataset, source link, question title) on the shared topic-registration sheet **before** cleaning data; avoid duplicating another group | **To confirm:** the team must check this is done |
| Dataset is open-access / publicly available | **OPEN:** access terms of the IMDWeb download are not confirmed. Ask the instructor/TF |
| Source website/web link cited | Done in README (IMDWeb). Full citation pending |
| README: dataset source, coverage, relevance to environmental economics | Source and coverage done. **Relevance to environmental economics: pending** (team to write) |
| README: every cleaning/preparation step, in order | Preliminary steps documented in README and `docs/preparation.md`; final heat definitions pending |
| Code: scripts that take raw data and produce the cleaned dataset, matching the README | Preliminary audit/merge/validation/panel implemented and executed (#2/#3, preliminary #5); heat indicators and human review pending |
| Reproducible with **no manual steps** | One preparation command works with raw files already local. Final raw-data access/sharing and teammate reproduction remain **OPEN** |
| 2-3 candidate research questions, each with policy relevance and a course technique (valuation, instrument comparison, CBA/discounting, treatment-effect reasoning) | **Pending** (see `docs/research-questions.md`) |
| Self-contained folder submitted | **Planned:** a separate submission repository (see below) |

## Open questions to settle with the instructor/TF

1. Does the IMDWeb download count as open-access / publicly available? IMD's data-supply procedure (separate from IMDWeb) says supplied data must not be shared with third parties.
2. May the raw CSVs be included in the submitted folder? Team decision for the working repo: the raw CSVs are committed in `data/raw/` for internal use (the repo is public, so they are downloadable). For the submission repo this is still to confirm. IMD's data-supply procedure says supplied data must not be shared with third parties.
3. If raw files cannot be included, is a download script or a documented download step acceptable? (An open Python package, `imdlib`, downloads IMD gridded data by script; whether it covers the needed variables has not been checked.)

## Repository plan

- **This repository (`India-Extreme-Heat-Working-`)** is the working and final source: all code, documentation, issues and AI-assistant instructions live here.
- **A separate submission repository (`india-extreme-heat-submission`)** will hold only what the handout asks for (README, code, candidate research questions, and data as permitted), laid out exactly as requested. It will be built from this repository once the work is finished, so that working files do not need to be stripped out later.

## Verification

Every group member should verify each step of the code (see `docs/verification-log.md`). AI-written code must be read and checked by a person before it is relied on.
