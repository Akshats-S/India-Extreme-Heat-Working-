# Preliminary data preparation

Scope: Issues #2 and #3, and the preliminary temperature-table portion of #5.
Extreme-heat definitions (#4) and the final submission package remain pending.

## Run

Use Python 3.11 or newer; verified with Python 3.12.10. From the repository root:

```bash
python -m pip install -r requirements.txt
python src/prepare_data.py
```

This single preparation command audits both raw files, constructs and validates
the merged panel, and writes the outputs. No spreadsheet editing is needed.
The two CSVs must already be available locally. The technical lead confirmed the
project's data-sharing arrangements are resolved on 2026-10-31. Final package
assembly and reproduction must still be completed and documented.

Defaults are relative to the script's repository, so the command also works
when invoked by absolute path from another working directory. Custom paths:

```bash
python src/prepare_data.py /path/to/fileA.csv /path/to/fileB.csv --cities config/cities.geojson --config config/preparation.json --output-dir data/processed
```

The input order and filenames do not determine which variable a file contains.
Identification uses the `tmax` or `tmin` header. Exactly two files are required.

Read-only audit and automated tests:

```bash
python src/audit_raw_data.py
python -W error -m unittest discover -s tests -v
```

The audit prints JSON and never writes files. Both commands use the same
validation functions, avoiding different rules for auditing and preparation.
Tests use clearly synthetic two-city fixtures; the real-data acceptance test
is skipped if either original CSV is unavailable.

## Exact preparation steps

1. Read `config/preparation.json`: study dates, coordinate tolerance, explicitly
   allowed absent records, and optional temperature quality-control bounds.
   Read the GeoJSON's features in order: index 0 is point_id 0, and so on.
   Require unique city names and valid longitude/latitude Point coordinates.
2. Check CSV record widths and exact seven-column schemas, including duplicate
   headers. Read fields as text before conversion. Reject malformed records,
   empty files, ambiguous variables, extra columns and missing columns.
3. Require actual calendar dates in exact `YYYY-MM-DD` format and integer-valued
   IDs belonging to the city file. Reject out-of-period records and duplicate
   `(point_id, date)` keys before joining. Rename source `time` to `date`.
4. Parse temperatures and coordinates as numeric values. Empty or case-insensitive
   `NA`, `NaN`, `null`, `none` and `N/A` temperature tokens are recognized as
   missing and reported as errors in an existing source record. Reject other
   nonnumeric tokens, infinity, and missing/nonfinite coordinate values.
   No undocumented numeric sentinel (such as -999) is silently recoded.
5. Validate point coordinates against the GeoJSON to within the configured
   tolerance (default 0.000001 degrees). Require geographic grid bounds and a
   constant exported cell per point within each file. Retain the supplied cell
   coordinates; do not calculate a new city-to-grid assignment.
6. Construct every combination of configured city and calendar date, including
   leap days. Attach city names and canonical point coordinates from the GeoJSON.
   Join each temperature file on `(point_id, date)` with a one-to-one check.
   Preserve Tmax and Tmin cell coordinates in separate columns. For an absent
   record, leave its temperature and cell metadata blank; set its missing flags.
   Point coordinates are location metadata, so they remain available from the
   GeoJSON even for absent records. Differences within the coordinate tolerance
   are standardized to these canonical point coordinates in the output.
7. Report matched, Tmax-only, Tmin-only and neither-present records. Require
   matching Tmax/Tmin grid coordinates wherever both records exist. Reject
   Tmin greater than Tmax. Require the expected panel length and unique
   city/date and point/date combinations.
8. Detect all missing source records against the complete calendar, including
   entirely missing cities. Only explicitly configured absent keys are allowed
   as warnings. Other absent keys and missing temperatures in existing records
   fail validation. The default whitelist contains Guwahati, 2005-06-26; the
   actual presence/absence in each file is calculated, not assumed. A repaired
   source containing that observation is also accepted and reported as present.
9. Count coverage and missing values per city and year. Sort the daily table
   by `point_id`, then `date`; fix column order; serialize dates consistently and
   numeric values with 17 significant digits. There is no temperature rounding,
   imputation, averaging, interpolation, outlier deletion or unit conversion.
10. Publish validated CSVs and JSON/text reports. Outputs contain no current
    timestamp or absolute input paths, and the report records source/config/city
    SHA-256 hashes (file fingerprints), software versions, settings and the
    dataset fingerprint. Repeating a run on unchanged inputs in the same
    environment must produce identical bytes.

## Failure policy and quality-control bounds

Exit status 0 means preparation passed (possibly with disclosed warnings).
Status 1 means validation or file processing failed. Status 2 covers argument
or output-path/report-writing errors. Validation failure writes a diagnostic
report without publishing a new dataset. Previous CSVs remain unchanged; read
the latest report's `status` and `dataset_published` before using an output.
Each individual output is replaced atomically to avoid a half-written file;
the directory as a whole is not a transactional filesystem operation.

Writing into the repository's raw-data directory, or overwriting an input or
configuration through an output-name collision, is blocked. Raw files are
never edited by preparation.

Temperature units, physical plausibility bounds, and observation windows still
need authoritative confirmation. Consequently there are **no default absolute
temperature bounds**. Input extrema are reported without claiming they are
physically plausible. After the team agrees on appropriate bounds, set
`temperature_min` / `temperature_max` in the JSON config or supply
`--temperature-min` / `--temperature-max` in source units. These are data-quality
checks, not extreme-heat definitions. The metadata warning remains visible even
when a user supplies bounds. No heat-event indicators are implemented here.

## Output files and schema

All four default outputs go into `data/processed/` and are git-ignored.

| File | Contents |
|---|---|
| `daily_temperatures.csv` | Full city-day panel described below |
| `coverage_by_city_year.csv` | Expected days, observed values, missing records/values, and complete pairs for each city-year |
| `validation_report.json` | Machine-readable status, errors/warnings with examples, input fingerprints, merge counts, coverage totals and output schema/fingerprint |
| `validation_report.txt` | Short readable validation summary |

| Daily column(s) | Logical type | Meaning |
|---|---|---|
| `point_id` | integer | Index in the GeoJSON feature order |
| `city` | string | City name from GeoJSON |
| `date` | ISO date string | Calendar date, renamed from `time` |
| `lat`, `lon` | number | Canonical city-point latitude and longitude |
| `tmax_cell_lat`, `tmax_cell_lon` | nullable number | Original Tmax cell metadata; blank if Tmax record absent |
| `tmin_cell_lat`, `tmin_cell_lon` | nullable number | Original Tmin cell metadata; blank if Tmin record absent |
| `tmax`, `tmin` | nullable number | Original temperature scale; units unverified |
| `tmax_record_missing`, `tmin_record_missing` | boolean | Whether that source record was absent |
| `tmax_missing`, `tmin_missing` | boolean | Whether that temperature is blank |
| `temperature_pair_complete` | boolean | Both temperatures are present |

CSV has no stored type metadata: flags serialize as `True` / `False`, missing
numeric values as empty fields. JSON records the in-memory output dtypes. To
reload with exact binary floating-point round-tripping in pandas, use:

```python
import pandas as pd
daily = pd.read_csv("data/processed/daily_temperatures.csv", float_precision="round_trip")
daily["date"] = pd.to_datetime(daily["date"], format="%Y-%m-%d")
```

Coverage columns are `point_id`, `city`, `year`, `expected_days`, `observed_tmax`,
`observed_tmin`, `missing_tmax_records`, `missing_tmin_records`,
`missing_tmax_values`, `missing_tmin_values`, and `complete_pairs`. Counts are
integers. For partial-year custom date ranges, `expected_days` covers only the
configured dates.

## Real-data result (2026-10-31)

The executed preparation produced 140,256 city-day rows: 16 cities over 8,766
days, with 140,255 complete temperature pairs. Both raw files have 140,255 rows;
there are no unmatched source records, duplicate keys, city-coordinate
disagreements, cross-file grid disagreements or Tmin-above-Tmax observations.
The sole absent key is Guwahati, 2005-06-26, in both files. The complete output
retains that row with blank temperatures and cell metadata. Coverage has 384
city-year rows. Validation passes with warnings for the two allowed source
gaps and unresolved metadata/bounds. Human review remains pending.
