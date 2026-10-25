# AGENTS.md - read this first (AI coding assistants)

This file is for any AI assistant or chatbot a teammate uses on this repository (Claude, ChatGPT, Copilot, Cursor, Gemini, etc.). Read it fully before suggesting or writing anything.

## Project in 60 seconds

- **What:** university Environmental Economics empirical project (course: Introduction to Environmental Economics, AY 2026-27). Goal: prepare a clean, reproducible dataset, document the preparation process, and identify environmental economics research applications. Causal identification and full econometric analysis are not required.
- **Research question (the project's primary question):** To what extent has the frequency of extreme nighttime heat changed relative to extreme daytime heat across major Indian cities between 2001 and 2024?
- **Study period:** 1 Jan 2001 - 31 Dec 2024 (8,766 calendar days).
- **Cities (16):** Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi.
- **Data:** India Meteorological Department (IMD) daily gridded maximum (Tmax) and minimum (Tmin) temperature, 1 degree resolution, downloaded from IMDWeb (https://imdweb.lwcc.in/). Two CSVs, one per variable. These are gridded values, not urban weather-station readings.
- **Deadline:** replication package due 30 November 2026. Groups of up to 3.
- **Language/tooling:** Python 3, pandas. Dependencies live in `requirements.txt`.
- **Two repositories:** this repository (`India-Extreme-Heat-Working-`) is the working and final source. A separate repository (`india-extreme-heat-submission`) will hold only what the course handout asks for, built from this one at the end. See `docs/assignment-checklist.md`.

## Rules

1. **AI use is allowed for all parts of this project** (code, analysis, writing). The original handout limited AI to coding and verification, but the course instructor has since confirmed full freedom to use AI tools. The humans remain responsible: everything must be read and verified by a team member before it is relied on or submitted (the instructors will review the code).
2. **Never invent** data, statistics, results, thresholds, or processing decisions, and never present guesses as facts. Report only what code actually outputs, and label assumptions as assumptions.
3. **Open decisions belong to the team.** How extreme days/nights are defined, city-to-grid mapping, and similar choices are listed in `docs/methodology.md` (section 4 and 'DECISION PENDING' items). You may propose options with trade-offs, but make choices explicit parameters in code and have the team record its decision in the decision log.
4. **Raw IMD CSVs are committed in `data/raw/`** (team decision: internal use; this repo is public). Do not modify or overwrite them; write all derived data to `data/processed/`. Never commit credentials or personal files.
5. **Do not push to `main`.** Use a branch and a pull request (see `CONTRIBUTING.md`).
6. **Keep documentation honest:** distinguish completed work from planned/pending work, and update docs when behaviour changes. Record human verification in `docs/verification-log.md`.

## Repository map

| Path | Purpose |
|------|---------|
| `README.md` | Human overview with a quick read at the top |
| `AGENTS.md` | This file (assistant instructions); `CLAUDE.md` and `.github/copilot-instructions.md` point here |
| `CONTRIBUTING.md` | Branch / commit / pull request workflow |
| `data/README.md` | Data source, download steps, which file is which |
| `data/raw/` | Raw IMD CSVs (tmax, tmin), committed, read-only |
| `data/processed/` | Pipeline outputs (git-ignored by default) |
| `config/cities.geojson` | The 16 city points (matches the point coordinates in both CSVs) |
| `docs/data-dictionary.md` | Column definitions and observed structural facts about the raw files |
| `docs/methodology.md` | Technical outline and open decisions, decision log |
| `docs/assignment-checklist.md` | Course handout requirements vs. status, open questions for the instructor |
| `docs/research-questions.md` | Template for the 2-3 candidate research questions the handout requires |
| `docs/verification-log.md` | Record of human verification of each step |
| `src/` | Pipeline code. Implemented so far: `audit_raw_data.py` |
| `notebooks/` | Exploration notebooks (none yet) |
| `outputs/figures/` | Generated figures (none yet) |

## Raw data schema (details in docs/data-dictionary.md)

Both raw files share the key columns `time` (YYYY-MM-DD), `point_id` (0-15), `lat`, `lon` (city point). The max file adds `tmax_cell_lat`, `tmax_cell_lon`, `tmax`; the min file adds `tmin_cell_lat`, `tmin_cell_lon`, `tmin`. Identify a file by its value column (`tmax` or `tmin`), never by its filename. Units are not stated in the files. `point_id` 0-15 follows the order of the city list above and of `config/cities.geojson`.

## Known data facts (verified by `src/audit_raw_data.py`)

- Each file has 140,255 rows and no empty cells; no duplicate (time, point_id) rows.
- 16 points x 8,766 days would be 140,256 rows; one location-date is absent from both files: point_id 14 (Guwahati), 2005-06-26.
- The two files match exactly on (time, point_id).

## Common commands

```bash
pip install -r requirements.txt
# the two raw CSVs are already in data/raw/ after cloning, then:
python src/audit_raw_data.py
```

## Work plan

Work is tracked as GitHub Issues #1-#7 (audit, merge, validate, define thresholds, generate cleaned dataset, exploratory visuals, finalize docs). Each has acceptance criteria. The handout requires the final pipeline to run with no manual steps. Before starting, check the issue and ask the user which one they are working on.

## Definition of done for any change

- Code runs from a clean checkout (given the raw files locally).
- No data files or secrets in the diff.
- Docs updated; pending vs done is accurate.
- A person has read and verified AI-written code (log it in `docs/verification-log.md`).
- Opened as a pull request linked to its Issue.
