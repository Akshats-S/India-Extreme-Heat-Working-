Data source: [India Meteorological Department, via IMDWeb](https://imdweb.lwcc.in/).

# Extreme daytime and nighttime heat across Indian cities

Introduction to Environmental Economics, AY 2026-27.

**Team:** Akshat Srivastava, Krishna Reddy and Jatin Shetty.

**Research question:** To what extent has the frequency of extreme nighttime
heat changed relative to extreme daytime heat across major Indian cities
between 2001 and 2024?

The dataset, preparation, descriptive analysis, economics applications and
replication packages are complete. This repository contains the maintained
source. The [submission repository](https://github.com/Akshats-S/india-extreme-heat-submission)
contains separate, self-contained preliminary and final packages.

## Reproduce

Use Python 3.11+; verification used Python 3.12.10. Original inputs are in
`data/raw/`.

```powershell
python -m pip install -r requirements.txt
python src/run_project.py
python -W error -m unittest discover -s tests -v
```

For the preliminary temperature-only dataset:

```powershell
python src/run_project.py --preliminary
```

Use `python src/audit_raw_data.py` for a read-only audit. Build both verified
submission ZIPs with `python src/build_packages.py`; they are written to the
sibling `Submissions` folder. Each build checks repeated outputs, runs all
tests and verifies regeneration after ZIP extraction.

## Data and outputs

Source: India Meteorological Department (IMD), accessed through
[IMDWeb](https://imdweb.lwcc.in/). Daily maximum/minimum temperature estimates
cover 16 city-associated grid points, 1 January 2001 to 31 December 2024.

| Output | Coverage |
|---|---|
| Daily panel | 140,256 city-days; 16 preliminary columns or 21 final columns |
| Complete temperature pairs | 140,255; Guwahati, 2005-06-26 remains blank and flagged |
| Seasonal threshold table | 5,856 city/calendar-date rows |
| Annual summaries | 384 city-years |
| Early/late comparison | 16 cities; 2001-2005 versus 2020-2024 |
| Descriptive analysis | Six CSVs, four specifications, computed results and five figures |

The pipeline preserves source temperatures without rounding, filling or
deleting outliers. The primary heat definition uses fixed city/calendar-day
P90 thresholds, five-day windows and a 2001-2024 reference. Missing temperatures
produce missing heat flags; day/night comparisons use paired observed dates.

Generated files live in `data/processed/`, `outputs/analysis/` and
`outputs/figures/`. They are git-ignored here and included in the submission
packages. Use the submission repository or built ZIPs for complete deliverables.

## Documentation

| Document | Contents |
|---|---|
| [Preparation](docs/preparation.md) | Ordered cleaning steps and preliminary schema |
| [Methodology](docs/methodology.md) | Heat definitions, denominators and interpretation |
| [Source metadata](docs/source-metadata.md) | Product citations, grid checks and measurement limits |
| [Data dictionary](docs/data-dictionary.md) | Raw file columns and city mapping |
| [Heat output schemas](docs/heat-output-schema.md) | Daily indicators and summary tables |
| [Analysis guide](docs/analysis-guide.md) | Figures, sensitivity checks and package building |
| [Research questions](docs/research-questions.md) | Three economics applications and course techniques |
| [Review guide](docs/review-guide.md) | Replication, spot checks and exact submission contents |
| [Submission requirements](docs/assignment-checklist.md) | Course deliverables and deadlines |
| [Verification record](docs/verification-log.md) | Executed checks and reproducibility evidence |

## Interpretation

These are one-degree interpolated grid estimates, not precise urban-station
measurements. Tmin is a nighttime proxy; the export's exact clock-time/date
convention is unverified. IMD documents a station-network change from 2008
onward. The project-relative percentile indicators and retrospective reference
are documented adaptations, not official heatwave classifications.

The comparisons are descriptive. The economics questions connect exposure to
adaptation timing, public cooling access, instrument choice and policy
evaluation, and specify extra data needed for monetary or causal estimates.

## Submission copies

- Preliminary: **6 November 2026**, from the team-provided handoff.
- Final: **30 November 2026**, from the [course handout](docs/handout/Instructions.pdf).

The preliminary folder contains only the dataset, preparation code, brief
topic outline and essential runtime inputs/instructions. Full verification
records and final-stage materials are kept outside that hand-in. Repository publication is separate from course-portal
submission. Future corrections follow [CONTRIBUTING.md](CONTRIBUTING.md).

Data citation: Srivastava, Rajeevan and Kshirsagar (2009), *Development of a high
resolution daily gridded temperature data set (1969-2005) for the Indian region*,
Atmospheric Science Letters, [doi:10.1002/asl.232](https://doi.org/10.1002/asl.232).
Current IMD product links and access evidence are in the source metadata.
