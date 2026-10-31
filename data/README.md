# Temperature data

Source: India Meteorological Department (IMD), accessed through
[IMDWeb](https://imdweb.lwcc.in/). Daily Tmax/Tmin cover 16 city-associated
one-degree grid points from 1 January 2001 to 31 December 2024.

## Original inputs

| File | Variable | Rows |
|---|---|---|
| `raw/imdweb_B3KKauQB.csv` | Tmax | 140,255 |
| `raw/imdweb_5PfvCU0D.csv` | Tmin | 140,255 |

Both originals are included unchanged. Headers identify the variable; random
download filenames do not define its meaning. City coordinates and point order
are in [cities.geojson](../config/cities.geojson). Detailed columns are in the
[data dictionary](../docs/data-dictionary.md).

The full output has 140,256 city-days. Guwahati, 2005-06-26 is absent in both
sources and remains blank and flagged. No temperature is rounded, imputed,
clipped or deleted. Celsius/grid evidence and clock-time/spatial limitations
are documented in [source metadata](../docs/source-metadata.md).

## Reproduction and storage

```powershell
python src/run_project.py --preliminary
python src/run_project.py
python src/audit_raw_data.py
```

The first command produces the preliminary temperature-only panel and reports;
the second adds heat variables and descriptive analysis. The audit is read-only.
Outputs go to `data/processed/`; figures and analysis tables go to `outputs/`.
Never edit the original CSVs.

Raw inputs are tracked in both repositories. Generated outputs are git-ignored
in the working repository and explicitly included in each submission folder.
Project sharing arrangements are resolved; retain IMD attribution and source
links. Exact preparation steps are in [preparation.md](../docs/preparation.md).
