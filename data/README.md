# Data directory

**Status:** no dataset is committed to this repository. Nothing in this folder has been processed. The two raw files have been identified and structurally audited (see `docs/data-dictionary.md`).

## Layout

| Path | Purpose | Tracked in Git? |
|------|---------|-----------------|
| `data/raw/` | Original IMDWeb downloads (daily maximum and minimum temperature CSVs). | **No** (ignored; only a placeholder is tracked) |
| `data/processed/` | Outputs of the cleaning/merging scripts. | **No** by default (regenerated from raw data) |

## Source

- Provider: India Meteorological Department (IMD), Government of India
- Download interface: <https://imdweb.lwcc.in/>
- Dataset: daily gridded maximum and minimum temperature, 1-degree spatial resolution
- Period: 2001-01-01 to 2024-12-31
- Geography: 16 Indian cities (listed in the top-level README; coordinates in `config/cities.geojson`, pending upload)

## Why raw files are not in Git

IMD's published data-supply procedure states that supplied data must not be shared with third parties and is provided for a declared purpose. Public redistribution of the raw CSVs is therefore **unclear / not confirmed**, so they are excluded from this public repository until permission is confirmed. Do not commit them.

## Which file is which (from the file headers)

| Local file name | Value column | Variable | Rows |
|-----------------|--------------|----------|------|
| `imdweb_B3KKauQB.csv` | `tmax` | Daily maximum temperature | 140,255 |
| `imdweb_5PfvCU0D.csv` | `tmin` | Daily minimum temperature | 140,255 |

IMDWeb gives each download a random file name, so identify files by their header (`src/audit_raw_data.py` does this), not by name. Download date and downloader: **pending** (to be filled in by whoever downloaded them).

## How to obtain the raw data (manual)

1. Open IMDWeb (<https://imdweb.lwcc.in/>) and select the daily gridded maximum and minimum temperature products at 1-degree resolution.
2. Request/download 2001-01-01 to 2024-12-31 for the 16 study cities.
3. Save the two CSVs into `data/raw/` **on your own machine**. Never commit them.
4. Run `python src/audit_raw_data.py` to check structure and confirm which file is which.

Teammates who need the files should obtain them from IMDWeb themselves or ask the team member who downloaded them (share privately, not through this repository).
