# Heat indicators and output schema

Run `python src/prepare_data.py` to regenerate all seven files in
`data/processed/`. Use `--skip-heat` for the original four-file preliminary
temperature-only workflow. The read-only audit does not fit heat thresholds.

Settings: `config/heat_metrics.json`; source evidence: `config/source_metadata.json`.
Custom analyses can use `--heat-config path/to/settings.json --output-dir path/to/output`.
Outputs contain no run timestamp or absolute input paths. The report includes
the settings, metadata, software versions and file fingerprints. An analysis
with changed settings must use its own output directory to preserve earlier
results. All generated outputs remain git-ignored.

## Daily table: daily_temperatures.csv

The 16 preliminary columns documented in [preparation.md](preparation.md) are
retained in their original order. Five fields are appended:

| Column | Type | Meaning |
|---|---|---|
| `tmax_threshold_c` | number | Fixed reference-percentile threshold for this city/calendar date |
| `tmin_threshold_c` | number | Corresponding Tmin threshold |
| `extreme_day` | nullable boolean | Tmax strictly exceeds its threshold |
| `extreme_night` | nullable boolean | Tmin strictly exceeds its threshold |
| `compound_extreme` | nullable boolean | Both exceed on the same source date; blank if either temperature is missing |

Thresholds can exist even when a particular date's temperature is missing.
Missing indicators are empty CSV fields, never False or zero. `True` / `False`
are serialized booleans. Reload these indicators as pandas nullable booleans
if further processing must distinguish missing from False.

## Threshold table: heat_thresholds.csv

One row per city and calendar date, including an interpolated February 29:
16 x 366 = 5,856 rows. Columns: `point_id`, `city`, `calendar_day` (MM-DD),
`threshold_is_interpolated`, `baseline_expected_samples`, `tmax_threshold_c`,
`tmax_baseline_samples`, `tmin_threshold_c`, `tmin_baseline_samples`.

For ordinary days, the default expected window size is 24 years x 5 days = 120
observations per variable. Actual sample counts disclose missingness. February
29 has the mean of the February 28/March 1 thresholds; sample counts are blank
because no independent February 29 quantile was fitted.

## Annual table: city_year_heat.csv

One row per city/year (384 rows). All counts are observed counts, not imputed
full-year event totals. Quality rules control whether percentages are reported.

| Column group | Meaning |
|---|---|
| `point_id`, `city`, `year` | Identifiers |
| `expected_days`, `calendar_complete` | Full-year calendar length and whether all rows are included |
| `day_observed_days`, `night_observed_days`, `paired_days` | Nonmissing Tmax, Tmin and common-date denominators |
| `{day,night,paired}_missing_days` | Missing observations against the full year |
| `{day,night,paired}_max_monthly_missing` | Largest monthly missing count |
| `{day,night,paired}_coverage_fraction` | Observed denominator / expected days |
| `{day,night,paired}_year_eligible` | Complete calendar, at most 15 missing per year and at most 3 in every month |
| `extreme_day_count`, `extreme_night_count` | Counts using each variable's own observed dates |
| `extreme_day_pct`, `extreme_night_pct` | 100 x count / respective observed dates, blank if ineligible |
| `paired_extreme_day_count`, `paired_extreme_night_count` | Counts restricted to dates where both temperatures are observed |
| `paired_extreme_day_pct`, `paired_extreme_night_pct` | Comparable percentages using `paired_days`, blank if paired year is ineligible |
| `night_minus_day_pp` | Paired night percentage minus paired day percentage, in percentage points |
| `compound_count`, `compound_pct` | Same-source-date co-exceedance count and paired-date percentage |

`paired_observed_days` is an explicit alias of `paired_days`, provided alongside
the other coverage fields. Counts remain visible when a year is ineligible;
percentages and comparisons are suppressed, rather than silently treating
missing observations as non-events. A partial-year custom study cannot produce
an eligible full-year percentage.

## Period table: city_period_comparison.csv

One row per city (16 rows). For `early` (2001-2005) and `late` (2020-2024),
fields give start/end year, eligibility, paired-day denominator, paired extreme
day/night counts, and their percentages. A period requires every configured
year to exist and pass the paired coverage rule.

Period percentages pool observed event counts and paired-day denominators.
They are not unweighted averages of annual percentages. `day_change_pp` and
`night_change_pp` are late minus early percentages. `night_minus_day_change_pp`
subtracts the daytime change from the nighttime change. A positive number
means the nighttime frequency increased more (or decreased less) over these
periods under this definition. It is a descriptive comparison, not a causal
treatment-effect estimate. Relative growth ratios are avoided because an
early-period event frequency could be zero.

## Existing files and validation

`coverage_by_city_year.csv` retains its preliminary schema. JSON/text reports
now include source-grid checks, the heat configuration, output dimensions,
event/NA totals and the fingerprints of all five CSVs. Strict source checks,
baseline coverage, indicator boundaries, annual counts and 0-100 percentage
bounds are validated before publishing data. A heat-stage failure publishes
no new dataset; read the report before using any CSV from an earlier run.
