# src/

Python scripts for the data-preparation pipeline. Run from the repository root.

## Implemented

| Script | What it does |
|--------|--------------|
| `audit_raw_data.py` | Reads the two raw CSVs from `data/raw/` (or paths passed as arguments), identifies which is Tmax and which is Tmin from the column names, and prints structural checks: columns, row counts, date range, point count, empty cells, duplicates, missing location-dates, and the cross-file match on (time, point_id). It does not modify data and computes no research results. |

```bash
pip install -r requirements.txt
python src/audit_raw_data.py
```

## Planned (pending, not implemented)

| Planned step | Corresponding issue |
|--------------|---------------------|
| Merge max and min observations by location and date | #2 |
| Validation checks (missing values, duplicates, ranges, spatial coverage) | #3 |
| Define extreme day/night thresholds (parameterized) | #4 |
| Write the cleaned dataset to `data/processed/` | #5 |

Module names and interfaces for the planned steps will be decided by the team and documented here once code exists.
