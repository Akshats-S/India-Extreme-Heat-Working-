# Data directory

**Status:** no dataset is committed to this repository yet. Nothing in this folder has been processed.

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
- Geography: 16 Indian cities (listed in the top-level README; coordinates in `config/cities.geojson`)

## Why raw files are not in Git

IMD's published data-supply procedure states that supplied data must not be shared with third parties and is provided for a declared purpose. Public redistribution of the raw CSVs is therefore **unclear/not confirmed**, so they are excluded from this public repository until permission is confirmed. Do not commit them.

## How to obtain the raw data (manual)

1. Open IMDWeb (<https://imdweb.lwcc.in/>) and select the daily gridded maximum temperature and minimum temperature products at 1-degree resolution.
2. Request/download the period 2001-01-01 to 2024-12-31 for the study cities.
3. Save the files into `data/raw/` **on your own machine**. Record the exact filenames and download date in the table below.

| File name | Variable (confirmed from file header) | Download date | Downloaded by |
|-----------|---------------------------------------|---------------|---------------|
| _pending_ | _pending: identify from header/metadata, not filename_ | _pending_ | _pending_ |
| _pending_ | _pending_ | _pending_ | _pending_ |

The file audit is tracked in a GitHub Issue ("Audit and document the raw datasets").
