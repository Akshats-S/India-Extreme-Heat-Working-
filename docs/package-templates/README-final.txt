Data source: [India Meteorological Department, via IMDWeb](https://imdweb.lwcc.in/).

# India extreme heat: final replication package

Course: {{COURSE}} | Academic year: {{YEAR}}
Team: {{TEAM}}
Section: {{SECTION}}
Final deadline: November 30, 2026 (course handout).

## Research question and purpose

To what extent has the frequency of extreme nighttime heat changed relative
to extreme daytime heat across major Indian cities between 2001 and 2024?

This folder provides the cleaned dataset, original inputs, complete code,
documentation, candidate economics questions, descriptive results and figures.
It is a replication package with descriptive findings and candidate economics
applications. It does not claim causal policy effects.

## Reproduce everything

Use Python 3.11+ (tested with Python 3.12.10). Extract this ZIP, open a terminal
in the extracted folder and install dependencies once:

    python -m pip install -r requirements.txt

Run the complete preparation and analysis with one command:

    python src/run_project.py

Run all automated tests:

    python -W error -m unittest discover -s tests -v

No raw-data download or manual spreadsheet editing is required because the
original CSVs are bundled under the project's confirmed sharing arrangements.
Dependency installation requires access to a package index or preinstalled
matching packages. PACKAGE_CHECKS.json records fresh-copy verification;
MANIFEST.json fingerprints the included files. Figures are PNGs, so they
regenerate without an interactive desktop.

## Source and coverage

Provider: India Meteorological Department (IMD), Government of India.
Interface: https://imdweb.lwcc.in/ . Product documentation:
https://www.imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html and
https://www.imdpune.gov.in/cmpg/Griddata/Min_1_Bin.html .

Daily Tmax/Tmin cover January 1, 2001 to December 31, 2024 for Delhi, Jaipur,
Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad,
Bengaluru, Chennai, Bhubaneswar, Guwahati and Kochi. There are 8,766 calendar
days and 140,256 city-day rows. Both raw files have 140,255 observations; the
only absent pair is Guwahati on June 26, 2005. Temperatures are in Celsius
based on identified product provenance, with no numerical unit conversion.

The data are one-degree interpolated grid estimates at city-associated points.
They do not directly measure urban heat islands or neighborhood conditions.
IMD documents a station-network change from 2008 onward. Exact export clock-
time alignment is unverified: dates are retained and Tmin is a nighttime proxy.

Citation: Srivastava, A. K., Rajeevan, M., and Kshirsagar, S. R. (2009),
Development of a high resolution daily gridded temperature data set (1969-2005)
for the Indian region, Atmospheric Science Letters, doi:10.1002/asl.232.
The older paper describes the original product; current product pages describe
the later extension. Source evidence was checked October 31, 2026.

## Environmental economics relevance

Comparing daytime/nighttime exposure supports research on adaptation timing,
public cooling access, efficient private cooling, budget allocation and equity.
The three completed candidate questions in RESEARCH_QUESTIONS.md connect the
exposure dataset to cost-benefit/discounting, instrument comparison and
treatment-effect reasoning. Each states the extra cost, population, outcome
or policy data needed. This temperature-only package does not monetize damage
or identify a policy's health effect.

## Every preparation and analysis step, in order

1. Read explicit source, city, preparation and heat configurations. The GeoJSON
   feature order maps point_id 0-15 to city names and coordinates.
2. Validate CSV record widths and exact Tmax/Tmin schemas. Identify variables
   by value-column headers, not random download filenames.
3. Require valid YYYY-MM-DD dates within the configured study period, numeric
   coordinates/temperatures and known integer point IDs. Reject duplicate keys,
   malformed/missing values in existing records and nonfinite values.
4. Check point/grid coordinates, Tmin <= Tmax and broad project QC bounds of
   -90 to 60 Celsius. The final source check rejects IMD's documented 99.9
   sentinel and checks nearest documented grid nodes. These broad checks do
   not certify that every retained value is locally plausible.
5. Build the complete city-day calendar, including leap days, attach city names
   and join Tmax/Tmin one-to-one by point/date. Keep the known Guwahati gap as
   blank temperatures/grid metadata with explicit flags. Do not impute, round,
   clip, drop or convert source temperatures.
6. Fit separate city/calendar-day 90th-percentile thresholds from a fixed
   2001-2024 reference, pooling plus/minus two calendar days across reference
   years. Use type-8 median-unbiased quantiles and circular year-end windows.
   Require at least 90% window coverage and at least 10 reference years.
7. Exclude February 29 from fitting; use the mean of February 28/March 1
   thresholds for that date. Retain actual leap-day observations in counts.
8. Add nullable strict-greater-than warm-day/night flags. Missing temperature
   gives a missing indicator. A compound flag means co-exceedance on the same
   source date, not a proven consecutive chronological day and night.
9. Generate coverage-aware annual counts and percentages. A year must have its
   full calendar, at most 15 missing observations annually and at most 3 in
   every month to receive percentages. Compare day/night on paired dates.
10. Pool paired events and observed dates for 2001-2005 and 2020-2024. Report
    frequency changes and nighttime minus daytime change in percentage points.
11. Validate counts, shares, missing flags and fingerprints; sort by point/date
    and write deterministic daily, threshold, coverage and summary tables.
12. Generate city temperature summaries, equal-city annual means and three
    alternatives to the primary method: P95, a 2001-2010 reference and a
    15-day window. Keep primary files unchanged. The earlier reference is an
    unbootstrapped diagnostic with a reference-boundary sampling caveat.
13. Produce five labeled figures and a results note calculated from the actual
    tables. No figures or numerical findings are manually edited.

The project-relative indicators adapt percentile concepts; they are not
certified ETCCDI indices or official IMD heatwave classifications. The 24-year
retrospective reference partly constrains whole-sample tail frequencies.
Sensitivity checks are not confidence intervals or causal evidence.

## Files to inspect

- data/processed/daily_temperatures.csv: 140,256 daily rows, 21 columns.
- data/processed/heat_thresholds.csv: 5,856 city/calendar-date thresholds.
- data/processed/city_year_heat.csv: 384 city-year summaries.
- data/processed/city_period_comparison.csv: 16 early/late comparisons.
- data/processed/coverage_by_city_year.csv and validation_report.json/.txt.
- outputs/analysis/results-note.md: computed descriptive findings and limits.
- outputs/analysis/: six summary/sensitivity CSVs plus analysis_report.json.
- outputs/figures/: five reproducible PNGs.
- RESEARCH_QUESTIONS.md and TOPIC_OUTLINE.md: written academic components.
- docs/: source evidence, method, complete schemas, review guide and verification.
- src/, config/, tests/ and requirements.txt: all reproducible code/settings.

See docs/review-guide.md for replication and manual spot checks. Team and
course details are in COVER.md.
