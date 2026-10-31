# Methodology (technical outline)

> **Status:** phases 1 and 2 are implemented under the technical lead's instruction on 2026-10-31 to finish the measurement method and research variables. The choices below are explicit project defaults, not claims of independent team sign-off or official heatwave classifications. Preparation is documented in [preparation.md](preparation.md), source evidence in [source-metadata.md](source-metadata.md), and the final schemas in [heat-output-schema.md](heat-output-schema.md).

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
| Units | Celsius from IMD product documentation; original CSV numerical scale retained |
| Cities | Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati, Kochi |
| City coordinates | `config/cities.geojson`; the CSVs also carry point coordinates and grid-cell coordinates |

Structure and observed facts: see [`data-dictionary.md`](data-dictionary.md).

Limitation to document: values are gridded 1-degree products, not urban weather-station measurements.

## 3. Processing pipeline

1. **Raw audit** - *Implemented.* Shared strict checks in `src/prepare_data.py`; `src/audit_raw_data.py` exposes a read-only audit. Schema, row width, dates, IDs, duplicates, numeric values and coordinates are validated. Source evidence establishes Celsius; exact export clock-time alignment remains a documented limitation.
2. **City-to-grid mapping** - Retain the supplied cell coordinates and validate constancy, cross-file agreement and nearest-node consistency with IMD's documented grid. All 16 points pass. Treat the values as regional exposure proxies; city-scale, coastal and topographic representation remain limitations. Do not infer urban heat-island measurements.
3. **Merge** - *Implemented.* One-to-one joins on `(point_id, date)` after renaming `time`. This matches the export's point identity and avoids floating-point coordinates as keys; coordinates are independently validated. City names and canonical point coordinates come from GeoJSON feature order.
4. **Validation** - *Implemented.* Reject duplicates, invalid dates/IDs/numbers, out-of-period records, coordinate disagreement, unexpected gaps and Tmin above Tmax. Keep the full calendar and known Guwahati gap. Configured absent keys are warnings, not imputed values. Broad project QC bounds [-90, 60] Celsius and IMD's documented 99.9 sentinel prevent obvious input problems; these checks do not certify local plausibility. No temperature is clipped or deleted.
5. **Extreme definitions** - see section 4.
6. **Output** - *Implemented.* The command produces the extended daily panel, threshold table, annual and period summaries, coverage and JSON/text reports. `--skip-heat` reproduces the preliminary temperature-only workflow.
7. **Exploratory outputs** - *Pending.* Figures and summary statistics in `outputs/`.

## 4. Heat measurement method (implemented)

The [ETCCDI warm-day/night definitions](https://etccdi.pacificclimate.org/list_27_indices.shtml)
motivate separate Tmax/Tmin 90th-percentile exceedances from five-day calendar
windows. Their standard reference is 1961-1990 and includes in-base bootstrap
handling. This project has 2001-2024 data only and implements the following
transparent descriptive adaptation, not an exact official TX90p/TN90p product.

| Choice | Project default and rationale |
|---|---|
| Temperature measure | Tmax for daytime and Tmin as nighttime proxy; source dates unchanged because the export's exact clock-time convention is unverified |
| Threshold | Separate 90th percentiles for every city and calendar day; local and seasonal adjustment avoids imposing one temperature on distinct climates |
| Fixed reference | All available years, 2001-2024; use the full 24-year record rather than an arbitrary short early reference. Thresholds stay fixed across evaluated years |
| Seasonal window | Target calendar day plus/minus 2 days, pooled over reference years; wrap December/January on a 365-day calendar |
| Quantile estimator | NumPy `median_unbiased`, Hyndman-Fan type 8; numeric behavior explicit and tested |
| Reference completeness | At least 10 full reference calendar years; at least 90% of the expected observations in every variable/window. Defaults yield 120 expected samples per ordinary threshold |
| Leap days | Omit February 29 from fitting. Its threshold is the mean of February 28 and March 1 thresholds. Retain the actual February 29 observation in event counts and annual denominators |
| Exceedance | Strictly greater than the threshold; equality is not an event. A missing temperature gives a missing indicator |
| Season/event | All-year individual source dates, not consecutive-day heatwaves. Compound means both variables exceed on the same source date |
| Annual quality | Require the full year's calendar, at most 15 missing observations annually and at most 3 in each month; apply separately to day, night and paired availability |
| Annual frequency | Count and percentage of observed dates. Main night/day comparison uses common dates where both temperatures exist |
| Period comparison | Compare pooled paired-date frequencies for 2001-2005 and 2020-2024. Report each change and nighttime minus daytime change in percentage points |
| IMD classification | Do not label these flags as official IMD heatwaves; percentile warmth and operational heatwave warnings measure different things |

The numerical estimator is documented by [NumPy](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html).
The annual/monthly missing limits follow the commonly used defaults exposed by
[climdex.pcic source code](https://github.com/cran/climdex.pcic/blob/master/R/climdex.r).
The 90% window-completeness requirement and minimum 10 years are explicit,
more conservative project choices, not attributed to those software defaults.

Every setting is in `config/heat_metrics.json`. The default reference includes
all evaluated years, so no in-/out-reference boundary is introduced in the
primary series. No bootstrap correction is implemented. Using a different
reference via configuration changes the estimand and can introduce the
in-/out-reference sampling issue noted by ETCCDI. Such variants must retain
that caveat and are sensitivity analyses, not certified ETCCDI indices.

The full-sample reference is retrospective and partly constrains aggregate
exceedance frequencies near the selected tail probability. It does not force
each year to have 10% events, and it does not define real-time warning cutoffs.
Emphasize changes across years/periods rather than interpreting the two
whole-sample event totals as independent evidence of greater heat severity.

## 5. Other open questions

- Phase 3 figures and four-specification sensitivity are implemented; see `analysis-guide.md` and the generated results note.
- Exact export clock-time alignment remains an acknowledged evidence limitation; no date shift is inferred.
- Preparation and plotting dependencies are pinned and installed successfully in a fresh isolated environment.
- IMD attribution is complete; project data sharing is resolved. No new blanket software/data license is assigned by the replication package.

## 6. Decision log

| Date | Decision | Rationale | Decided by |
|------|----------|-----------|------------|
| 2026-10-31 | Preliminary merge uses point_id/date, retains exported grid metadata, builds the full calendar and flags known gaps without imputation. CSV/JSON/text outputs with stable ordering; no heat thresholds or unit conversion. | Implements the technical lead's requested preliminary pipeline while preserving original values and making missingness visible. Policy is explicit in config and the preparation guide. | Technical lead requested implementation; code/output human review pending |
| 2026-10-31 | Phase 1/2 defaults in section 4: fixed 2001-2024 city/calendar-day P90, five-day windows, type-8 quantiles, explicit leap/missing rules, paired frequency comparisons and 2001-2005 versus 2020-2024 changes. Celsius/grid provenance and broad QC documented. | Finish the authorized measurement and research-variable phases with reproducible, configurable choices, preserving scientific limitations rather than inventing unavailable metadata. | Implementation choices made under technical lead's instruction to complete phases 1/2; no independent human verification claimed |
