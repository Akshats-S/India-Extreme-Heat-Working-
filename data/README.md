# Data

## Folders

| Folder | Contents | In Git? |
|---|---|---|
| `data/raw/` | Original IMDWeb downloads: daily maximum (tmax) and minimum (tmin) temperature CSVs. | **Yes** (team decision, see below) |
| `data/processed/` | Outputs of the cleaning and merging scripts. | **No** by default (regenerated from the raw files) |

## Raw files (in `data/raw/`)

| File | Variable | Rows |
|---|---|---|
| `imdweb_B3KKauQB.csv` | tmax | 140,255 |
| `imdweb_5PfvCU0D.csv` | tmin | 140,255 |

Columns: time, point_id, lat, lon, tmax_cell_lat, tmax_cell_lon, and tmax (tmax file) or the matching tmin columns (tmin file). Details, known gaps and the city mapping are in [`docs/data-dictionary.md`](../docs/data-dictionary.md). City coordinates are in [`config/cities.geojson`](../config/cities.geojson).

Known facts from the structural audit: one row is missing (point_id 14, Guwahati, 2005-06-26) in both files; units are not stated in the files.

## Source

India Meteorological Department (IMD) daily gridded temperature, 1 degree, downloaded from IMDWeb (https://imdweb.lwcc.in/): 16 city points, 2001-01-01 to 2024-12-31.

## Rules

- Do not edit or overwrite the files in `data/raw/`. Write all derived data to `data/processed/`.
- Run `python src/audit_raw_data.py` to re-check the raw files.

## Sharing and open-access status

The team decided to keep the raw CSVs in this repository for internal use. Be aware that this repository is public, so the files are downloadable by anyone, and IMD's data-supply procedure says supplied data must not be shared with third parties.

Still open for the submission repo: the course handout requires open-access data and a self-contained folder with no manual steps. Whether IMDWeb data counts as open-access, and whether the raw files may go in the submission, is not confirmed with the instructor/TF. See [`docs/assignment-checklist.md`](../docs/assignment-checklist.md).
