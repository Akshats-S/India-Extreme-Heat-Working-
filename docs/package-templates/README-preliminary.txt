# India extreme heat: preliminary assessment

Course: {{COURSE}} | Academic year: {{YEAR}}
Team: {{TEAM}}
Section: {{SECTION}}
Preliminary deadline: November 6, 2026 (team-provided handoff).

## What to submit

This self-contained folder contains the preliminary dataset, its preparation
code and a brief research-topic outline. TOPIC_OUTLINE.md is the outline.
data/processed/daily_temperatures.csv is the preliminary cleaned dataset.
The two original source CSVs are included in data/raw/ under the project's
confirmed sharing arrangements. Validation/coverage reports and tests are
supporting material.

## Reproduce

Use Python 3.11+ (tested with Python 3.12.10). Extract the ZIP first and open a
terminal in this folder. Install the pinned dependencies once:

    python -m pip install -r requirements.txt

Then regenerate the preliminary dataset without manual data-editing steps:

    python src/run_project.py --preliminary

Run the automated checks:

    python -W error -m unittest discover -s tests -v

The same code supports the final workflow, but --preliminary deliberately
produces the temperature-only daily table and the three supporting reports.
Tests use synthetic examples and actual raw-data acceptance checks.

## Dataset and preparation

Source: India Meteorological Department, accessed via https://imdweb.lwcc.in/ .
Coverage: 16 selected Indian city points, January 1, 2001 through December 31,
2024; daily maximum/minimum gridded temperatures, one-degree resolution.
The full panel has 140,256 rows and 140,255 complete temperature pairs.
Guwahati, June 26, 2005 remains blank and explicitly flagged in both variables.

Preparation, in order: validate schemas and CSV records; parse exact calendar
dates and numeric values; check IDs, unique point/date keys, city coordinates,
grid consistency, broad Celsius QC bounds and Tmin <= Tmax; construct every
expected city-day; attach city names; join Tmax/Tmin one-to-one; preserve and
flag the known gap; calculate coverage; sort and write deterministic outputs.
Raw values are not imputed, rounded, clipped or converted. Full schemas and
steps are in docs/preparation.md and docs/data-dictionary.md.

## Environmental economics relevance

Daytime/nighttime exposure patterns motivate questions about the timing and
allocation of adaptation services, cooling access and energy-efficient
protection. The topic outline distinguishes exposure evidence from policy
costs, health outcomes or causal effects that require additional data.

## Important limits and review

Values are interpolated grid estimates, not urban station measurements.
Celsius is established from product provenance; exact export clock-time
alignment is unverified, so source dates are retained and Tmin is a nighttime
proxy. See docs/source-metadata.md and docs/review-guide.md. The verification
record and PACKAGE_CHECKS.json describe actual automated checks; they do not
claim human sign-off. MANIFEST.json fingerprints the included files.

Full IMD citation: Srivastava, A. K., Rajeevan, M., and Kshirsagar, S. R. (2009),
Development of a high resolution daily gridded temperature data set (1969-2005)
for the Indian region, Atmospheric Science Letters, doi:10.1002/asl.232.
Product evidence and documentation access date are in config/source_metadata.json.
