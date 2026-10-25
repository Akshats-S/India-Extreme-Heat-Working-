# AGENTS.md - read this first (AI coding assistants)

This file is for any AI assistant or chatbot a teammate uses on this repository (Claude, ChatGPT, Copilot, Cursor, Gemini, etc.). Read it fully before suggesting or writing anything.

## Project in 60 seconds

- **What:** university Environmental Economics empirical project. Goal: build a clean, reproducible dataset, document the preparation process, and identify environmental economics research applications. No causal identification or full econometric analysis is required.
- **Research question (fixed, do not change or add to it):** To what extent has the frequency of extreme nighttime heat changed relative to extreme daytime heat across major Indian cities between 2001 and 2024?
- **Study period:** 1 Jan 2001 - 31 Dec 2024 (8,766 calendar days).
- **Cities (16):** Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi.
- **Data:** India Meteorological Department (IMD) daily gridded maximum (Tmax) and minimum (Tmin) temperature, 1 degree resolution, downloaded from IMDWeb (https://imdweb.lwcc.in/). Two CSVs, one per variable. These are gridded values, not urban weather-station readings.
- **Language/tooling:** Python 3, pandas. Dependencies live in `requirements.txt`.

## Hard rules (non-negotiable)

1. **Course AI policy:** AI use in this course is limited to **coding and verification**. Do NOT write research findings, interpretations, conclusions, discussion text, or new research questions. If asked, decline and tell the user to write it themselves. Helping with code, debugging, tests, and checking that code/data behave as intended is fine.
2. **Never invent** data, statistics, results, thresholds, or processing decisions. Report only what code actually outputs.
3. **Open decisions belong to the team.** How extreme days/nights are defined, city-to-grid mapping, and similar choices are listed in `docs/methodology.md` (section 4 and 'DECISION PENDING' items). Do not silently pick one: make choices explicit parameters in code and ask the user to record the team's decision in the decision log.
4. **Never commit raw IMD data** (anything in `data/raw/`, or any `*.csv`/`*.nc`) - IMD's terms on redistribution are unconfirmed. Never commit credentials or personal files.
5. **Do not push to `main`.** Use a branch and a pull request (see `CONTRIBUTING.md`).
6. **Keep documentation honest:** distinguish completed work from planned/pending work. Update docs when behaviour changes.

## Repository map

| Path | Purpose |
|------|---------|
| `README.md` | Human overview with a quick read at the top |
| `AGENTS.md` | This file (assistant instructions); `CLAUDE.md` and `.github/copilot-instructions.md` point here |
| `CONTRIBUTING.md` | Branch / commit / pull request workflow |
| `data/README.md` | Data source, download steps, which file is which |
| `data/raw/` | Local-only raw CSVs (git-ignored) |
| `data/processed/` | Pipeline outputs (git-ignored by default) |
| `config/cities.geojson` | City coordinates (pending upload by the team) |
| `docs/data-dictionary.md` | Column definitions and observed structural facts about the raw files |
| `docs/methodology.md` | Technical outline and open decisions, decision log |
| `src/` | Pipeline code. Implemented so far: `audit_raw_data.py` |
| `notebooks/` | Exploration notebooks (none yet) |
| `outputs/figures/` | Generated figures (none yet) |

## Raw data schema (details in docs/data-dictionary.md)

Both raw files share the key columns `time` (YYYY-MM-DD), `point_id` (0-15), `lat`, `lon` (city point). The max file adds `tmax_cell_lat`, `tmax_cell_lon`, `tmax`; the min file adds `tmin_cell_lat`, `tmin_cell_lon`, `tmin`. Identify a file by its value column (`tmax` or `tmin`), never by its filename. Units are not stated in the files.

## Known data facts (verified by `src/audit_raw_data.py`)

- Each file has 140,255 rows and no empty cells; no duplicate (time, point_id) rows.
- 16 points x 8,766 days would be 140,256 rows; one location-date is absent from both files: point_id 14, 2005-06-26.
- The two files match exactly on (time, point_id).

## Common commands

```bash
pip install -r requirements.txt
# put the two IMDWeb CSVs in data/raw/ (local only), then:
python src/audit_raw_data.py
```

## Work plan

Work is tracked as GitHub Issues #1-#7 (audit, merge, validate, define thresholds, generate cleaned dataset, exploratory visuals, finalize docs). Each has acceptance criteria. Before starting, check the issue and ask the user which one they are working on.

## Definition of done for any change

- Code runs from a clean checkout (given the raw files locally).
- No data files or secrets in the diff.
- Docs updated; pending vs done is accurate.
- Opened as a pull request linked to its Issue.
