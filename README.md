# india-extreme-heat

Empirical analysis of extreme daytime and nighttime temperature trends across 16 major Indian cities (2001–2024), using India Meteorological Department data.

> **Project status: early setup.** The repository structure and documentation exist. No data processing, analysis or results have been produced yet. Items marked **Pending** are planned but not implemented.

## Overview

This is a university Environmental Economics empirical project. The objective is to prepare a clean, reproducible dataset, document the preparation process, and identify environmental economics research applications. Establishing causality and full econometric analysis are not part of the scope.

### Research question

> To what extent has the frequency of extreme nighttime heat changed relative to extreme daytime heat across major Indian cities between 2001 and 2024?

## Data provenance

| Item | Detail |
|------|--------|
| Provider | India Meteorological Department (IMD), Government of India |
| Download interface | [IMDWeb](https://imdweb.lwcc.in/) |
| Dataset | Daily gridded maximum and minimum temperature, 1° spatial resolution |
| Files used | Two CSVs downloaded from IMDWeb (maximum and minimum temperature) plus a GeoJSON of city coordinates |
| Which CSV is which | **Pending** - to be confirmed from file headers/metadata, not filenames (see data audit issue) |

**Raw data is not stored in this repository.** IMD's data-supply procedure states that supplied data must not be shared with third parties, and public redistribution terms for the IMDWeb downloads are not confirmed. Raw CSVs are therefore git-ignored. See [`data/README.md`](data/README.md) for how to obtain them.

## Study period and coverage

- **Period:** 1 January 2001 – 31 December 2024
- **Cities (16):** Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi

## Daily maximum vs. minimum temperature

- **Daily maximum temperature (Tmax)** is the highest temperature recorded in a day. It is used here as the *daytime* heat measure.
- **Daily minimum temperature (Tmin)** is the lowest temperature recorded in a day. It is used here as the *nighttime* heat measure.

The exact observation windows and units used in IMD's gridded products are to be confirmed from IMD documentation and the file metadata.

## Data limitation

IMD's 1° gridded temperatures are interpolated area products, not precise urban weather-station measurements. A 1° cell spans roughly 100 km, so values will not capture city-scale effects such as urban heat islands. This limitation should be kept in mind when interpreting any later results.

## Repository structure

```
india-extreme-heat/
├── README.md            Project overview (this file)
├── CONTRIBUTING.md      Collaboration workflow
├── requirements.txt     Placeholder - dependencies not yet pinned
├── .gitignore           Python template + data exclusions
├── data/
│   ├── raw/             Local-only raw IMD downloads (git-ignored)
│   ├── processed/       Outputs of the cleaning pipeline (git-ignored by default)
│   └── README.md        Data sources and download instructions
├── config/
│   └── cities.geojson   City coordinates (to be added - see Next steps)
├── src/                 Pipeline code (none yet)
├── notebooks/           Exploratory notebooks (none yet)
├── outputs/
│   └── figures/         Generated figures (none yet)
└── docs/
    └── methodology.md   Technical outline and open decisions
```

Empty folders contain a `.gitkeep` placeholder so Git tracks them.

## Preliminary data-processing workflow

All steps are **Pending** (tracked as GitHub Issues). Details and open decisions are in [`docs/methodology.md`](docs/methodology.md).

1. Audit and document the raw datasets
2. Merge maximum and minimum temperature observations by location and date
3. Validate missing values, duplicates, temperature ranges and spatial coverage
4. Define extreme daytime and nighttime temperature thresholds
5. Generate the cleaned reproducible dataset
6. Prepare exploratory visualizations and dataset summary statistics
7. Finalize documentation and verify reproducibility

## Reproducibility

| Step | Status |
|------|--------|
| Document data source and download process | Done (see `data/README.md`) |
| Obtain raw data from IMDWeb into `data/raw/` | Manual; per-user, not in Git |
| Pin Python dependencies in `requirements.txt` | **Pending** (placeholder only) |
| Processing scripts in `src/` | **Pending** (none written) |
| Single command / script to regenerate the cleaned dataset | **Pending** |
| End-to-end reproducibility check from a clean checkout | **Pending** |

There is currently nothing to run. Instructions will be added here as code is implemented.

## Project status and next steps

**Done:** repository scaffold, collaboration documentation, methodology outline, work-item Issues.

**Next:**

1. Add `config/cities.geojson` (local file, not yet uploaded to the repo).
2. Audit the two raw CSVs locally and record which is Tmax / Tmin (Issue 1).
3. Work through the remaining Issues in order.
4. Confirm IMD's redistribution terms if the team wants to share raw or derived data publicly.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to `main` should go through pull requests.

## Acknowledgements and data attribution

Temperature data: India Meteorological Department (IMD), Government of India, accessed via IMDWeb. Add the exact citation and access date once confirmed.

## License

No license has been chosen yet. **Pending** team decision.
