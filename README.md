# india-extreme-heat

Empirical analysis of extreme daytime and nighttime temperature trends across 16 major Indian cities (2001–2024), using India Meteorological Department data.

## Quick read

| | |
|---|---|
| **Goal** | Prepare a clean, reproducible dataset, document the preparation process, and identify environmental economics research applications. This is a university Environmental Economics empirical project; causal identification and full econometric analysis are **not** in scope. |
| **Research question** | *To what extent has the frequency of extreme nighttime heat changed relative to extreme daytime heat across major Indian cities between 2001 and 2024?* |
| **Dates used** | **1 January 2001 – 31 December 2024** (8,766 calendar days) |
| **Cities (16)** | Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi |
| **Data** | IMD daily gridded maximum (Tmax) and minimum (Tmin) temperature, 1° resolution, from [IMDWeb](https://imdweb.lwcc.in/). Two CSVs (one per variable), 140,255 rows each. |
| **Raw data in Git?** | **No.** IMD redistribution terms are unconfirmed, so raw CSVs are git-ignored. See [`data/README.md`](data/README.md). |
| **Status** | Scaffold, documentation and raw-file audit done. Merge, validation, thresholds, cleaned dataset and visuals are **pending** (Issues #2–#7). |
| **Using an AI assistant?** | Start with [`AGENTS.md`](AGENTS.md). The course limits AI use to **coding and verification**; no research findings or interpretation. |

## Getting started

```bash
git clone https://github.com/Akshats-S/india-extreme-heat.git
cd india-extreme-heat
pip install -r requirements.txt
# Put the two IMDWeb CSVs in data/raw/ (local only, never committed), then:
python src/audit_raw_data.py
```

Then read [`CONTRIBUTING.md`](CONTRIBUTING.md) (branches and pull requests) and pick an open Issue.

## Data provenance

| Item | Detail |
|------|--------|
| Provider | India Meteorological Department (IMD), Government of India |
| Download interface | [IMDWeb](https://imdweb.lwcc.in/) |
| Dataset | Daily gridded maximum and minimum temperature, 1° spatial resolution |
| Max-temperature file | The CSV with a `tmax` column (identified from its header) |
| Min-temperature file | The CSV with a `tmin` column (identified from its header) |
| City coordinates | `config/cities.geojson` (**pending upload**); coordinates also appear in the CSVs |

Column definitions and observed structure are in [`docs/data-dictionary.md`](docs/data-dictionary.md). IMD's data-supply procedure states that supplied data must not be shared with third parties, so the raw files stay local.

## Daily maximum vs. minimum temperature

- **Daily maximum temperature (Tmax)** is the highest temperature recorded in a day. It is used here as the *daytime* heat measure.
- **Daily minimum temperature (Tmin)** is the lowest temperature recorded in a day. It is used here as the *nighttime* heat measure.

Units and exact observation windows of IMD's gridded products are **pending confirmation** (the files do not state units).

## Data limitation

IMD's 1° gridded temperatures are area products, not precise urban weather-station measurements. A 1° cell spans roughly 100 km, so values will not capture city-scale effects such as urban heat islands. Keep this in mind when interpreting any later results.

## Repository structure

```
india-extreme-heat/
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
│   ├── raw/               Local-only raw IMD downloads (git-ignored)
│   └── processed/         Pipeline outputs (git-ignored by default)
├── config/
│   └── cities.geojson     City coordinates (pending upload)
├── src/
│   ├── README.md
│   └── audit_raw_data.py  Structural audit of the raw CSVs
├── notebooks/             Exploration notebooks (none yet)
├── outputs/
│   └── figures/           Generated figures (none yet)
└── docs/
    ├── data-dictionary.md Columns, file identification, observed structure
    └── methodology.md     Technical outline, open decisions, decision log
```

Empty folders contain a `.gitkeep` placeholder so Git tracks them.

## Data-processing workflow and status

Tracked as GitHub Issues. Open decisions are in [`docs/methodology.md`](docs/methodology.md).

| # | Step | Status |
|---|------|--------|
| 1 | Audit and document the raw datasets | **Partly done:** files identified, structure audited (`src/audit_raw_data.py`, data dictionary). Pending: upload/inspect `cities.geojson`, confirm units |
| 2 | Merge max and min observations by location and date | Pending |
| 3 | Validate missing values, duplicates, temperature ranges, spatial coverage | Pending (audit already shows one missing location-date; see data dictionary) |
| 4 | Define extreme daytime and nighttime thresholds | Pending (team decision) |
| 5 | Generate the cleaned reproducible dataset | Pending |
| 6 | Exploratory visualizations and summary statistics | Pending |
| 7 | Finalize documentation and verify reproducibility | Pending |

## Reproducibility

| Step | Status |
|------|--------|
| Document data source and download process | Done (`data/README.md`) |
| Obtain raw data from IMDWeb into `data/raw/` | Manual, per user, not in Git |
| Raw-file audit script | Done (`src/audit_raw_data.py`) |
| Pin exact dependency versions | **Pending** (minimum versions only) |
| Processing scripts for merge, validation, thresholds, cleaned dataset | **Pending** |
| One command to regenerate the cleaned dataset | **Pending** |
| End-to-end check from a clean checkout | **Pending** |

## Next steps

1. Upload `config/cities.geojson` to `config/` and confirm the 16 city names against the point coordinates.
2. Confirm temperature units and observation windows from IMD documentation.
3. Work through Issues #2–#7.
4. If the team wants to share data publicly, confirm IMD's redistribution terms first.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `main` go through pull requests (a repository rule enforces this).

## Attribution and license

Temperature data: India Meteorological Department (IMD), Government of India, accessed via IMDWeb. Add the exact citation and access date once confirmed. No license has been chosen yet (**pending** team decision).
