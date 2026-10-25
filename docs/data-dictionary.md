# Data dictionary (raw IMDWeb files)

Structural facts about the two raw CSVs, checked with `src/audit_raw_data.py`. Only structure is described here; no analysis. The raw files themselves are **not** in this repository (see `data/README.md`).

## Which file is which

Identified from the **column names in each file's header**, not from the file names:

| Local file name (as downloaded) | Value column | Variable |
|---|---|---|
| `imdweb_B3KKauQB.csv` | `tmax` | Daily maximum temperature |
| `imdweb_5PfvCU0D.csv` | `tmin` | Daily minimum temperature |

IMDWeb generates a different random file name on each download, so always re-identify files by header.

## Columns

| Column | In file | Description |
|---|---|---|
| `time` | both | Date, `YYYY-MM-DD` |
| `point_id` | both | Integer 0-15 identifying one of the 16 study points |
| `lat`, `lon` | both | Coordinates of the point (city location) |
| `tmax_cell_lat`, `tmax_cell_lon` | tmax file | Coordinates of the 1-degree grid cell the value comes from |
| `tmin_cell_lat`, `tmin_cell_lon` | tmin file | Same, for the tmin file |
| `tmax` | tmax file | Daily maximum temperature value |
| `tmin` | tmin file | Daily minimum temperature value |

**Units are not stated in either file.** Confirm against IMD documentation before using (pending). Values carry float32-style precision (e.g. 22.329999923706055) because of how they were exported.

## Observed structure

| Check | Result |
|---|---|
| Rows per file | 140,255 |
| Date range | 2001-01-01 to 2024-12-31 (8,766 calendar days) |
| Points | 16 (`point_id` 0-15) |
| Expected rows (16 x 8,766) | 140,256 |
| Empty cells | none in any column |
| Duplicate (time, point_id) rows | none |
| Missing location-date | `point_id` 14, 2005-06-26 (absent from both files) |
| Match between files on (time, point_id) | exact (140,255 of 140,255) |
| Rows where tmin > tmax | 0 |

Whether the one missing date needs special handling is a validation decision (Issue #3).

## Study points

Coordinates and grid cells are as they appear in the files. City names come from `config/cities.geojson`: its 16 points match the CSV point coordinates exactly, in `point_id` order (checked programmatically).

| point_id | lat | lon | grid cell lat, lon (tmax file) | City (from cities.geojson) |
|---|---|---|---|---|
| 0 | 28.6139 | 77.2090 | 28.5, 77.5 | Delhi |
| 1 | 26.9124 | 75.7873 | 26.5, 75.5 | Jaipur |
| 2 | 23.0225 | 72.5714 | 23.5, 72.5 | Ahmedabad |
| 3 | 19.0760 | 72.8777 | 19.5, 72.5 | Mumbai |
| 4 | 18.5204 | 73.8567 | 18.5, 73.5 | Pune |
| 5 | 26.8467 | 80.9462 | 26.5, 80.5 | Lucknow |
| 6 | 25.5941 | 85.1376 | 25.5, 85.5 | Patna |
| 7 | 22.5726 | 88.3639 | 22.5, 88.5 | Kolkata |
| 8 | 23.2599 | 77.4126 | 23.5, 77.5 | Bhopal |
| 9 | 21.1458 | 79.0882 | 21.5, 79.5 | Nagpur |
| 10 | 17.3850 | 78.4867 | 17.5, 78.5 | Hyderabad |
| 11 | 12.9716 | 77.5946 | 12.5, 77.5 | Bengaluru |
| 12 | 13.0827 | 80.2707 | 13.5, 80.5 | Chennai |
| 13 | 20.2961 | 85.8245 | 20.5, 85.5 | Bhubaneswar |
| 14 | 26.1445 | 91.7362 | 26.5, 91.5 | Guwahati |
| 15 | 9.9312 | 76.2673 | 9.5, 76.5 | Kochi |

The grid-cell columns are provided by the export; the rule used to assign a point to a cell is not documented in the files (pending).
