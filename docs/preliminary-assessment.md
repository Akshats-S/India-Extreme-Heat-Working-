# Preliminary assessment: topic outline and deliverables

Team-provided preliminary deadline: 6 November 2026. The preliminary dataset,
code and topic outline are prepared; the assessment has not been submitted.
The technical lead confirmed topic registration/finalization and resolution of
data sharing on 2026-10-31. Separate teammate review is not a gate on the lead's
own work.

## Topic outline

**Title:** Extreme daytime and nighttime heat across 16 Indian cities, 2001-2024

**Research question:** To what extent has the frequency of extreme nighttime
heat changed relative to extreme daytime heat across major Indian cities
between 2001 and 2024?

This project prepares a reproducible daily temperature dataset using India
Meteorological Department (IMD) gridded maximum (Tmax) and minimum (Tmin)
temperatures accessed through [IMDWeb](https://imdweb.lwcc.in/). It covers
1 January 2001 to 31 December 2024 for Delhi, Jaipur, Ahmedabad, Mumbai, Pune,
Lucknow, Patna, Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai,
Bhubaneswar, Guwahati and Kochi. Daily Tmax and Tmin are daytime/nighttime
proxies. Celsius is established from the IMD product documentation; exact
export clock-time alignment remains unverified and source dates are retained.

The environmental economics motivation is adaptation to heat exposure. A
comparison of daytime and nighttime patterns could inform questions about the
timing and geographic allocation of cooling and heat-protection measures.
The temperature dataset supplies exposure information; it does not measure
health effects, cooling demand, policy costs or policy effectiveness. Studying
those outcomes or conducting cost-benefit analysis would require additional
data and an appropriate research design.

The preliminary deliverable is a clean daily temperature panel and the code
that prepares it. The pipeline checks source schemas, dates, duplicates,
locations and temperature consistency, joins Tmax and Tmin by point/date, and
accounts for every expected city-day. It preserves missing observations with
explicit flags and does not impute temperatures. Both source files omit
Guwahati on 26 June 2005. The complete panel therefore contains 140,256 rows,
of which 140,255 contain both temperatures.

The data represent 1-degree grid cells associated with city points, rather
than city weather stations or direct measurements of urban heat islands.
The current repository also implements the phase 1/2 threshold and frequency
method in `docs/methodology.md`. The earlier preliminary ZIP is a preserved
temperature-only snapshot. No trend or causal findings are claimed in this
topic outline.

## Deliverables available locally

After running `python src/prepare_data.py --skip-heat` from the repository root
for the temperature-only preliminary workflow (omit the flag to include the
phase 2 heat variables):

- `data/processed/daily_temperatures.csv`: preliminary cleaned dataset.
- `data/processed/coverage_by_city_year.csv`: coverage for all 384 city-years.
- `data/processed/validation_report.txt` and `validation_report.json`: validation.
- `src/prepare_data.py` and `src/audit_raw_data.py`: preparation and audit code.
- `config/cities.geojson`, `config/preparation.json` and `requirements.txt`:
  location mapping, explicit settings and pinned dependencies.
- `tests/test_prepare_data.py`: synthetic edge cases and real-data acceptance.
- [Preparation guide](preparation.md): exact transformations and run instructions.
- This document: brief topic outline.

Generated datasets/reports are intentionally git-ignored and must be regenerated
locally. Their exclusion from Git is not an omission from the local deliverables.
The technical lead has confirmed the project's data-sharing arrangements are resolved.

## Readiness checklist

- [x] Preliminary daily dataset generated from the actual source files.
- [x] Preparation code, configuration, schema and instructions available.
- [x] Twenty automated tests passed, including real-data acceptance checks.
- [x] Repeated preparation in a fresh repository copy produced identical files.
- [x] Original raw files and exact temperature values preserved.
- [x] Brief research-topic outline drafted above.
- [x] Review workflow clarified: no separate teammate approval for the lead's own work; automated evidence recorded without claiming human sign-off.
- [x] Topic registration and finalization confirmed by the technical lead, 2026-10-31.
- [x] Project data-sharing issue confirmed resolved by the technical lead, 2026-10-31.
- [ ] Confirm any additional preliminary-submission instructions and team details.
- [ ] Assemble and submit the dataset, code and topic outline as instructed.

Source documentation and nearest-grid consistency checks now establish the
phase 1 measurement contract, with explicit date-alignment and spatial limits.
Heat indicators are implemented; the 2-3 final candidate research questions
remain phase 4 work and are outside the preliminary scope in the team handoff.
The final assessment is due 30 November 2026.
