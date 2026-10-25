# Methodology (technical outline)

> **Status: outline.** Only the raw-file audit (step 1) has been done. No analytical decision below has been made unless explicitly marked *Decided*. Items labelled **DECISION PENDING** must be resolved by the team and recorded here with a date and rationale.

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

1. **Raw audit** - *Partly done.* Files identified from headers; structure checked with `src/audit_raw_data.py`. Pending: confirm units. `cities.geojson` matches the CSV points and supplies the city names.
2. **City-to-grid mapping** - *Pending.* The exported files already give a grid cell per point. **DECISION PENDING:** accept the export's assignment or define another approach; handling of cities near cell boundaries or coastlines.
3. **Merge** - *Pending.* Audit shows both files have identical (time, point_id) keys. **DECISION PENDING:** final join keys and schema.
4. **Validation** - *Pending.* Known so far: no empty cells, no duplicates, one location-date absent (point_id 14, 2005-06-26). **DECISION PENDING:** plausibility ranges, Tmin <= Tmax rule, treatment of the missing date.
5. **Extreme definitions** - see section 4.
6. **Output** - *Pending.* Write cleaned dataset to `data/processed/`. **DECISION PENDING:** file format and column schema.
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

- Handling of leap days and calendar alignment
- Missing-data tolerance per city-year
- Software environment and version pinning
- License and data attribution text

## 6. Decision log

| Date | Decision | Rationale | Decided by |
|------|----------|-----------|------------|
| _none yet_ | | | |
