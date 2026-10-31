# India-Extreme-Heat-Working-

> **VERY IMPORTANT: NO AI AUTHORSHIP, UNDER ANY CIRCUMSTANCE.** Everything in this repository is authored by the team members under their own GitHub names. AI tools (Claude, Claude Code, ChatGPT, Codex, Gemini, Copilot or any other) may help, but must never be credited or named as author or co-author: no `Co-Authored-By` lines, no "Generated with ..." footers, no tool or session links in commits, pull requests, issues, files or docs. If a tool adds such a line by default, delete it before committing or opening the pull request.

Empirical analysis of extreme daytime and nighttime temperature trends across 16 major Indian cities (2001–2024), using India Meteorological Department data.

## Quick read

| | |
|---|---|
| **Goal** | Prepare a clean, reproducible dataset, document the preparation process, and identify environmental economics research applications. This is a university Environmental Economics empirical project (Introduction to Environmental Economics, AY 2026–27); causal identification and full econometric analysis are **not** in scope. |
| **Research question** | *To what extent has the frequency of extreme nighttime heat changed relative to extreme daytime heat across major Indian cities between 2001 and 2024?* |
| **Dates used** | **1 January 2001 – 31 December 2024** (8,766 calendar days) |
| **Deadline** | Replication package due **30 November 2026** (groups of up to 3). See [`docs/assignment-checklist.md`](docs/assignment-checklist.md). |
| **Cities (16)** | Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi |
| **Data** | IMD daily gridded maximum (Tmax) and minimum (Tmin) temperature, 1° resolution, from [IMDWeb](https://imdweb.lwcc.in/). Two CSVs (one per variable), 140,255 rows each. |
| **Raw data in Git?** | **Yes.** The two raw IMD CSVs are committed in `data/raw/` for team use. This repo is public, so they are publicly downloadable. See [`data/README.md`](data/README.md). |
| **Course handout** | [`docs/handout/Instructions.pdf`](docs/handout/Instructions.pdf) |
| **Status** | Phases 1/2 implemented: cited measurement method, validated daily warm-day/night indicators, thresholds and annual/period summaries. 34 automated tests pass; figures, final economics questions and final packaging remain. |
| **Two repositories** | This repo is the working and final source. A separate repo, `india-extreme-heat-submission`, holds only what the course handout asks for and is built from this one at the end. |
| **Using an AI assistant?** | Start with [`AGENTS.md`](AGENTS.md). AI tools may be used for all parts of the project (confirmed by the course instructor); a team member must verify everything that is submitted. |

## Getting started

```bash
git clone https://github.com/Akshats-S/India-Extreme-Heat-Working-.git
cd India-Extreme-Heat-Working-
python -m pip install -r requirements.txt
# The two raw CSVs are already in data/raw/ after cloning, then:
python src/prepare_data.py
```

This audits, merges and validates both raw files, fits fixed seasonal thresholds, and writes seven files in `data/processed/`: the extended daily panel, threshold table, annual heat summaries, early/late comparisons, coverage and JSON/text reports. The panel has 140,256 rows; Guwahati, 2005-06-26 remains blank and explicitly flagged. Raw data is unchanged. See [the preparation guide](docs/preparation.md), [methodology](docs/methodology.md) and [final output schema](docs/heat-output-schema.md). Use `--skip-heat` for the temperature-only preliminary workflow.

Read-only audit: `python src/audit_raw_data.py`. Tests: `python -W error -m unittest discover -s tests -v`. Tests include synthetic faulty inputs and real-data acceptance checks when raw files are available. Human verification remains pending. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for branches and pull requests.

The [preliminary assessment note](docs/preliminary-assessment.md) contains the brief topic outline, available deliverables and the remaining team/submission checks for November 6.

## Data provenance

| Item | Detail |
|------|--------|
| Provider | India Meteorological Department (IMD), Government of India |
| Download interface | [IMDWeb](https://imdweb.lwcc.in/) |
| Dataset | Daily gridded maximum and minimum temperature, 1° spatial resolution |
| Max-temperature file | The CSV with a `tmax` column (identified from its header) |
| Min-temperature file | The CSV with a `tmin` column (identified from its header) |
| City coordinates | [`config/cities.geojson`](config/cities.geojson) (16 city points; matches the point coordinates in both CSVs) |

Column definitions and observed structure are in [`docs/data-dictionary.md`](docs/data-dictionary.md). The raw files are committed in `data/raw/`. The technical lead confirmed topic registration/finalization and resolution of the project's data-sharing issue on 2026-10-31; see [`docs/assignment-checklist.md`](docs/assignment-checklist.md). Separate teammate approval is not required for the lead's own work.

## Daily maximum vs. minimum temperature

- **Daily maximum temperature (Tmax)** is the highest temperature recorded in a day. It is used here as the *daytime* heat measure.
- **Daily minimum temperature (Tmin)** is the lowest temperature recorded in a day. It is used here as the *nighttime* heat measure.

Celsius units are established from IMD product documentation; the CSV numerical scale is retained without conversion. Exact clock-time/date-label alignment of this export is not established, so source dates are preserved and Tmin is a nighttime proxy. See [source metadata](docs/source-metadata.md).

## Data limitation

IMD's 1° temperatures are interpolated grid estimates associated with city points, not precise city-station measurements or proven averages over city boundaries. The source documents a station-network change from 2008 onward. The 24-year reference, spatial scale and unverified clock-time alignment limit interpretation; full details are in [the methodology](docs/methodology.md).

## Repository structure

```
India-Extreme-Heat-Working-/
├── README.md              Overview and quick read (this file)
├── AGENTS.md              Instructions for AI assistants (read first)
├── CLAUDE.md              Pointer to AGENTS.md
├── CONTRIBUTING.md        Branch / commit / pull request workflow
├── requirements.txt       Python dependencies
├── .gitignore             Python template + data exclusions
├── .github/
│   ├── copilot-instructions.md   Pointer to AGENTS.md
│   └── PULL_REQUEST_TEMPLATE.md  Pull request checklist
├── data/
│   ├── README.md          Sources, download steps, file identification
│   ├── raw/               Raw IMD CSVs (tmax, tmin), committed
│   └── processed/         Pipeline outputs (git-ignored by default)
├── config/
│   ├── cities.geojson     The 16 city points
│   ├── preparation.json   Dates, coordinate tolerance and explicit missing-record policy
│   ├── heat_metrics.json  Fixed seasonal-percentile method and coverage rules
│   └── source_metadata.json  IMD units, grid and source-documentation links
├── src/
│   ├── README.md
│   ├── audit_raw_data.py  Read-only audit using the preparation checks
│   ├── prepare_data.py    Audit, merge, validate and write all outputs
│   └── heat_metrics.py    Fixed thresholds, daily indicators and annual/period summaries
├── tests/                Synthetic edge cases and real-data acceptance checks
├── notebooks/             Exploration notebooks (none yet)
├── outputs/
│   └── figures/           Generated figures (none yet)
└── docs/
    ├── data-dictionary.md       Columns, file identification, observed structure
    ├── methodology.md           Technical outline, open decisions, decision log
    ├── assignment-checklist.md  Course requirements vs. status
    ├── research-questions.md    Candidate research questions (template)
    └── verification-log.md      Who verified which step
```

Empty folders contain a `.gitkeep` placeholder so Git tracks them.

## Data-processing workflow and status

Tracked as GitHub Issues. Open decisions are in [`docs/methodology.md`](docs/methodology.md).

| # | Step | Status |
|---|------|--------|
| 1 | Audit and document the raw datasets | Implemented; Celsius/grid provenance cited; exact clock-time alignment is a disclosed limitation |
| 2 | Merge max and min observations by location and date | Implemented, executed and tested |
| 3 | Validate missing values, duplicates, temperature ranges, spatial coverage | Implemented with explicit broad QC bounds and nearest-grid checks; no claim of independent human sign-off |
| 4 | Define extreme daytime and nighttime thresholds | Implemented as configurable project-relative seasonal percentiles; departures from official indices documented |
| 5 | Generate the cleaned reproducible dataset (must run with no manual steps) | Implemented, including heat indicators and annual/period tables |
| 6 | Exploratory visualizations and summary statistics | Pending |
| 7 | Finalize documentation and verify reproducibility | Pending |

## Reproducibility

| Step | Status |
|------|--------|
| Document data source and download process | Done (`data/README.md`) |
| Obtain raw data from IMDWeb into `data/raw/` | Done; project sharing arrangements confirmed resolved by the technical lead. Final package assembly/reproduction pending |
| Raw-file audit script | Done (`src/audit_raw_data.py`) |
| Pin exact dependency versions | Done for the preliminary pipeline (Python 3.12.10 tested) |
| Processing scripts for merge, validation, thresholds, cleaned dataset | Implemented and tested, including fixed reference thresholds and annual/period summaries |
| One command to regenerate the cleaned dataset | `python src/prepare_data.py` (raw files already local) |
| End-to-end reproduction | Automated tests and repeated-output comparison; actual verification recorded honestly in [verification log](docs/verification-log.md); no separate teammate-review gate for lead-owned work |

## Next steps

1. Follow the remaining phases in [the project roadmap](docs/project-roadmap.md); topic registration and the data-sharing issue are resolved.
2. Build descriptive outputs and sensitivity checks using the documented method (#6); retain the source-date/network limitations.
3. Complete the economics questions and final documentation (#7), then verify the final package.
4. The raw CSVs are in this public repo by team decision. If that changes, remove them and confirm IMD's redistribution terms.
5. Write the candidate research questions and the environmental economics relevance note ([`docs/research-questions.md`](docs/research-questions.md)), then build the separate submission repository.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `main` go through pull requests (a repository rule enforces this).

## Attribution and license

Temperature data: India Meteorological Department (IMD), Government of India, accessed via IMDWeb. Cite Srivastava, Rajeevan and Kshirsagar (2009), *Development of a high resolution daily gridded temperature data set (1969-2005) for the Indian region*, Atmospheric Science Letters, [doi:10.1002/asl.232](https://doi.org/10.1002/asl.232), and the current IMD product documentation listed in [source-metadata.md](docs/source-metadata.md), checked 2026-10-31. Project data sharing is resolved; no general data/software license grant is inferred.
