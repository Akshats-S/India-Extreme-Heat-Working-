# Methodology (technical outline)

> **Status:** preliminary preparation is implemented and executed; human review is pending. The technical lead requested the merge, complete flagged calendar, validation and reproducible command on 2026-10-31. Analytical choices for extreme-heat definitions remain open. Exact implemented transformations and configurable settings are in [preparation.md](preparation.md).

## 1. Research question

"To what extent has the frequency of extreme nighttime heat changed relative to extreme daytime heat across major Indian cities between 2001 and 2024?"

Scope: prepare a clean, reproducible dataset, document the preparation process, and identify environmental economics research applications. Causal identification and full econometric analysis are out of scope.

## 2. Data

| Item | Description |
|------|-------------|
| Provider | India Meteorological Department (IMD), Government of India |
| Access | IMDWeb, <https://imdweb.lwcc.in/> |
| Variables | Daily gridded maximum temperature (Tmax) and minimum temperature (Tmin) |
| Spatial resolution | 1 degree |
| Period | 2001-01-01 to 2024-12-31 (8,766 days) |
| Files | Two CSVs, identified by header column (`tmax` / `tmin`); 140,255 rows each |
| Units | **Not stated in files; to be confirmed from IMD documentation** |
| Cities | Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi |
| City coordinates | `config/cities.geojson`; the CSVs also carry point coordinates and grid-cell coordinates |

Structure and observed facts: see [`data-dictionary.md`](data-dictionary.md).

Limitation to document: values are gridded 1-degree products, not urban weather-station measurements.

## 3. Processing pipeline

1. **Raw audit** - *Implemented.* Shared strict checks in `src/prepare_data.py`; `src/audit_raw_data.py` exposes a read-only audit. Schema, row width, dates, IDs, duplicates, numeric values and coordinates are validated. Units/observation windows and human review remain pending.
2. **City-to-grid mapping** - Exported Tmax/Tmin cell coordinates are retained separately and checked for within-point constancy and cross-file agreement. Point coordinates must match `cities.geojson` within 0.000001 degrees. No new spatial assignment is calculated. **DECISION PENDING:** scientific suitability of the exported cells, especially near boundaries/coastlines.
3. **Merge** - *Implemented.* One-to-one joins on `(point_id, date)` after renaming `time`. This matches the export's point identity and avoids floating-point coordinates as keys; coordinates are independently validated. City names and canonical point coordinates come from GeoJSON feature order.
4. **Validation** - *Implemented for preliminary preparation.* Reject duplicates, invalid dates/IDs/numbers, out-of-period records, coordinate disagreement, unexpected gaps and Tmin above Tmax. Build the full calendar (including leap days); the known absent Guwahati key remains blank and flagged. Only keys explicitly whitelisted in `config/preparation.json` are permitted missing-record warnings. No imputation or deletion. Physical plausibility bounds remain **DECISION PENDING**, disabled by default and configurable; metadata warnings remain visible.
5. **Extreme definitions** - see section 4.
6. **Output** - *Implemented for preliminary preparation.* A deterministic CSV panel, city-year coverage CSV and JSON/text validation reports are written to `data/processed/`. Exact schema is in [preparation.md](preparation.md). Heat indicators await the decisions below.
7. **Exploratory outputs** - *Pending.* Figures and summary statistics in `outputs/`.

## 4. Defining extreme days and nights - DECISIONS PENDING

None of the following has been chosen:

- [ ] **Threshold type:** absolute temperature cutoff(s), percentile-based, or another criterion
- [ ] **If percentile-based:** which percentile(s), computed per city, per calendar day/month/season, or over all days
- [ ] **Reference (baseline) period** for thresholds: the full 2001-2024 sample or a sub-period
- [ ] **Daytime measure:** Tmax
- [ ] **Nighttime measure:** Tmin
- [ ] **Season restriction:** all year vs. specific months
- [ ] **Event definition:** single extreme days vs. consecutive-day spells; minimum spell length if used
- [ ] **Frequency metric:** e.g. count or share of extreme days/nights per city-year (exact metric to be chosen)
- [ ] **Comparison of night vs. day frequency:** how relative change is to be expressed
- [ ] **Consistency with any official IMD heatwave criteria:** whether to reference them

Each choice, with its rationale, is recorded here once made (tracked in Issue #4).

## 5. Other open questions

- Leap days are retained in preliminary preparation; threshold calendar treatment remains open.
- Missing-data tolerance for later annual heat-event metrics remains open; preparation flags all gaps.
- Preliminary dependencies are pinned; final dependencies may expand when heat indicators/figures are implemented.
- License and data attribution text

## 6. Decision log

| Date | Decision | Rationale | Decided by |
|------|----------|-----------|------------|
| 2026-10-31 | Preliminary merge uses point_id/date, retains exported grid metadata, builds the full calendar and flags known gaps without imputation. CSV/JSON/text outputs with stable ordering; no heat thresholds or unit conversion. | Implements the technical lead's requested preliminary pipeline while preserving original values and making missingness visible. Policy is explicit in config and the preparation guide. | Technical lead requested implementation; code/output human review pending |
