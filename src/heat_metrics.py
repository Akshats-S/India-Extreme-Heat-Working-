"""Project-relative, seasonally adjusted warm-day/night indicators.

Definitions and departures from official ETCCDI indices are explicit in
docs/methodology.md. All fits use a fixed reference period, never a moving year.
"""

import calendar
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

CALENDAR_DAYS = pd.date_range("2001-01-01", "2001-12-31").strftime("%m-%d").tolist()
HEAT_COLUMNS = ["tmax_threshold_c", "tmin_threshold_c", "extreme_day", "extreme_night", "compound_extreme"]
HEAT_OUTPUT_NAMES = ["heat_thresholds.csv", "city_year_heat.csv", "city_period_comparison.csv"]


def load_heat_settings(path):
    settings = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    required = {"baseline_start_year", "baseline_end_year", "percentile", "window_days", "quantile_method",
                "minimum_baseline_years", "minimum_window_coverage", "annual_max_missing_days",
                "monthly_max_missing_days", "early_period", "late_period"}
    if not isinstance(settings, dict) or set(settings) != required:
        raise ValueError("Heat config must contain exactly: " + ", ".join(sorted(required)))
    for key in ("baseline_start_year", "baseline_end_year", "window_days", "minimum_baseline_years",
                "annual_max_missing_days", "monthly_max_missing_days"):
        if isinstance(settings[key], bool) or not isinstance(settings[key], int):
            raise ValueError(key + " must be an integer.")
    first, last = settings["baseline_start_year"], settings["baseline_end_year"]
    if not 1678 <= first <= last <= 2261:
        raise ValueError("Invalid baseline years.")
    if not 2 <= settings["minimum_baseline_years"] <= last - first + 1:
        raise ValueError("Baseline must contain at least minimum_baseline_years (at least two).")
    if not 1 <= settings["window_days"] <= 31 or settings["window_days"] % 2 != 1:
        raise ValueError("window_days must be odd, from 1 to 31.")
    if settings["quantile_method"] not in {"median_unbiased", "linear"}:
        raise ValueError("Supported quantile methods: median_unbiased or linear.")
    for key, low, high in (("percentile", 50, 100), ("minimum_window_coverage", 0, 1)):
        value = settings[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low < value <= high:
            raise ValueError(key + " is outside its valid range.")
    if settings["percentile"] == 100:
        raise ValueError("percentile must be strictly below 100.")
    if not 0 <= settings["annual_max_missing_days"] <= 366 or not 0 <= settings["monthly_max_missing_days"] <= 31:
        raise ValueError("Missing-data limits must be nonnegative and within the calendar length.")
    for key in ("early_period", "late_period"):
        period = settings[key]
        if not isinstance(period, list) or len(period) != 2 or any(isinstance(x, bool) or not isinstance(x, int) for x in period) or period[0] > period[1]:
            raise ValueError(key + " must contain ordered start/end years.")
    if settings["early_period"][1] >= settings["late_period"][0]:
        raise ValueError("Early and late comparison periods must be ordered and disjoint.")
    return settings


def validate_imd_grid(panel, metadata, tolerance=0.000001):
    """Check the retained export coordinates against the documented IMD grid."""
    if metadata.get("temperature_units") != "degC":
        raise ValueError("Source metadata must establish degC for this IMD product.")
    sentinel = metadata["documented_missing_sentinel"]
    for var in ("tmax", "tmin"):
        if panel[var].eq(sentinel).any():
            raise ValueError(f"{var}: documented IMD missing sentinel {sentinel} encountered; no value is imputed or classified.")
    step = metadata["grid_step_degrees"]
    if not isinstance(step, (int, float)) or step <= 0:
        raise ValueError("Source grid step must be positive.")
    checked = 0
    for axis, prefix in (("lat", "latitude"), ("lon", "longitude")):
        lower, upper = metadata["grid_" + prefix + "_min"], metadata["grid_" + prefix + "_max"]
        nodes = np.arange(lower, upper + step / 2, step)
        city_points = panel[["point_id", axis]].drop_duplicates()
        nearest = {}
        for row in city_points.itertuples(index=False, name=None):
            pid, value = row
            distances = np.abs(nodes - value)
            nearest[pid] = nodes[distances <= distances.min() + tolerance]
        for var in ("tmax", "tmin"):
            col = var + "_cell_" + axis
            observed = panel.loc[panel[col].notna(), ["point_id", col]].drop_duplicates()
            for pid, value in observed.itertuples(index=False, name=None):
                if not np.any(np.abs(nearest[pid] - value) <= tolerance):
                    raise ValueError(f"{col}: point {pid} does not match a nearest documented IMD grid node.")
                checked += 1
    return {"nearest_grid_coordinate_checks": checked, "mismatches": 0}


def validate_calendar(panel, settings):
    needed = {"point_id", "city", "date", "tmax", "tmin"}
    if not needed.issubset(panel.columns) or panel.empty:
        raise ValueError("Heat calculation needs the nonempty prepared daily panel.")
    dates = pd.to_datetime(panel.date, format="%Y-%m-%d", errors="raise")
    if panel.duplicated(["point_id", "date"]).any():
        raise ValueError("Heat input has duplicate city/date keys.")
    start, end = dates.min(), dates.max()
    count = len(pd.date_range(start, end))
    for _, group in panel.groupby("point_id", sort=True):
        if len(group) != count or group.date.min() != start.strftime("%Y-%m-%d") or group.date.max() != end.strftime("%Y-%m-%d"):
            raise ValueError("Heat input must retain every calendar date for every city.")
        if group.city.nunique() != 1:
            raise ValueError("Each point_id must identify exactly one city.")
        for var in ("tmax", "tmin"):
            values = group[var].dropna().to_numpy(dtype=float)
            if not np.isfinite(values).all():
                raise ValueError("Heat input contains a nonfinite temperature.")
    first, last = settings["baseline_start_year"], settings["baseline_end_year"]
    if start > pd.Timestamp(first, 1, 1) or end < pd.Timestamp(last, 12, 31):
        raise ValueError("The entire fixed baseline must be present in the prepared calendar.")
    for key in ("early_period", "late_period"):
        first, last = settings[key]
        if first < start.year or last > end.year:
            raise ValueError(key + " lies outside the study period.")


def fit_thresholds(panel, settings):
    """Fit fixed per-city five-day calendar windows; interpolate Feb 29 only."""
    first, last = settings["baseline_start_year"], settings["baseline_end_year"]
    years = last - first + 1
    width = settings["window_days"]
    offsets = np.arange(-(width // 2), width // 2 + 1)
    window_indices = (np.arange(365)[:, None] + offsets) % 365
    expected = years * width
    minimum = math.ceil(expected * settings["minimum_window_coverage"])
    tables = []
    for pid, group in panel.groupby("point_id", sort=True):
        reference = group.loc[group.date.between(f"{first}-01-01", f"{last}-12-31") & (group.date.str[5:] != "02-29")].sort_values("date")
        if len(reference) != years * 365:
            raise ValueError("Baseline has missing calendar rows; retain explicit blank rows.")
        table = pd.DataFrame({"point_id": pid, "city": group.city.iloc[0], "calendar_day": CALENDAR_DAYS,
                              "threshold_is_interpolated": False, "baseline_expected_samples": expected})
        for var in ("tmax", "tmin"):
            values = reference[var].to_numpy(dtype=float).reshape(years, 365)
            windows = values[:, window_indices].transpose(1, 0, 2).reshape(365, expected)
            observed = np.isfinite(windows).sum(axis=1)
            if (observed < minimum).any():
                day = CALENDAR_DAYS[int(np.flatnonzero(observed < minimum)[0])]
                raise ValueError(f"Insufficient baseline coverage: point {pid}, {var}, calendar day {day}.")
            table[var + "_threshold_c"] = np.nanquantile(windows, settings["percentile"] / 100,
                                                         axis=1, method=settings["quantile_method"])
            table[var + "_baseline_samples"] = observed
        leap = {"point_id": pid, "city": group.city.iloc[0], "calendar_day": "02-29",
                "threshold_is_interpolated": True, "baseline_expected_samples": pd.NA,
                "tmax_baseline_samples": pd.NA, "tmin_baseline_samples": pd.NA}
        for var in ("tmax", "tmin"):
            leap[var + "_threshold_c"] = float(table.loc[table.calendar_day.isin(["02-28", "03-01"]), var + "_threshold_c"].mean())
        table = pd.concat([table, pd.DataFrame([leap])], ignore_index=True)
        for col in ("baseline_expected_samples", "tmax_baseline_samples", "tmin_baseline_samples"):
            table[col] = table[col].astype("Int64")
        tables.append(table)
    return pd.concat(tables, ignore_index=True).sort_values(["point_id", "calendar_day"], ignore_index=True)


def attach_indicators(panel, thresholds):
    daily = panel.assign(calendar_day=panel.date.str[5:]).merge(
        thresholds[["point_id", "calendar_day", "tmax_threshold_c", "tmin_threshold_c"]],
        on=["point_id", "calendar_day"], how="left", validate="many_to_one")
    if daily[["tmax_threshold_c", "tmin_threshold_c"]].isna().any().any():
        raise ValueError("A daily observation has no fitted threshold.")
    for var, flag in (("tmax", "extreme_day"), ("tmin", "extreme_night")):
        daily[flag] = (daily[var] > daily[var + "_threshold_c"]).astype("boolean").mask(daily[var].isna(), pd.NA)
    pair = daily.tmax.notna() & daily.tmin.notna()
    daily["compound_extreme"] = (daily.extreme_day & daily.extreme_night).mask(~pair, pd.NA)
    return daily.drop(columns="calendar_day").sort_values(["point_id", "date"], ignore_index=True)


def summarize_years(daily, settings):
    rows = []
    for (pid, city, year), group in daily.assign(year=daily.date.str[:4].astype(int)).groupby(["point_id", "city", "year"], sort=True):
        expected = 366 if calendar.isleap(year) else 365
        complete_calendar = len(group) == expected
        pair = group.tmax.notna() & group.tmin.notna()
        row = {"point_id": int(pid), "city": city, "year": int(year), "expected_days": expected,
               "calendar_complete": complete_calendar, "paired_days": int(pair.sum())}
        for label, observed, flags in (("day", group.tmax.notna(), group.extreme_day),
                                       ("night", group.tmin.notna(), group.extreme_night),
                                       ("paired", pair, group.compound_extreme)):
            n = int(observed.sum())
            monthly_missing = (~observed).groupby(group.date.str[:7]).sum()
            missing = expected - n
            eligible = complete_calendar and missing <= settings["annual_max_missing_days"] and int(monthly_missing.max()) <= settings["monthly_max_missing_days"]
            row[label + "_observed_days"] = n
            row[label + "_missing_days"] = missing
            row[label + "_max_monthly_missing"] = int(monthly_missing.max())
            row[label + "_coverage_fraction"] = n / expected
            row[label + "_year_eligible"] = bool(eligible)
            count = int(flags.sum())
            name = "compound" if label == "paired" else "extreme_" + label
            row[name + "_count"] = count
            row[name + "_pct"] = 100 * count / n if eligible and n else None
        for label, flag in (("day", "extreme_day"), ("night", "extreme_night")):
            count = int(group.loc[pair, flag].sum())
            row["paired_extreme_" + label + "_count"] = count
            row["paired_extreme_" + label + "_pct"] = 100 * count / row["paired_days"] if row["paired_year_eligible"] and row["paired_days"] else None
        row["night_minus_day_pp"] = (row["paired_extreme_night_pct"] - row["paired_extreme_day_pct"]) if row["paired_year_eligible"] else None
        rows.append(row)
    return pd.DataFrame(rows)


def compare_periods(annual, settings):
    rows = []
    for (pid, city), group in annual.groupby(["point_id", "city"], sort=True):
        row = {"point_id": int(pid), "city": city}
        valid = True
        for label, key in (("early", "early_period"), ("late", "late_period")):
            first, last = settings[key]
            part = group.loc[group.year.between(first, last)]
            eligible = len(part) == last - first + 1 and bool(part.paired_year_eligible.all())
            n = int(part.paired_days.sum())
            row[label + "_start_year"], row[label + "_end_year"] = first, last
            row[label + "_eligible"] = eligible
            row[label + "_paired_days"] = n
            valid = valid and eligible and n > 0
            for measure in ("day", "night"):
                count = int(part["paired_extreme_" + measure + "_count"].sum())
                row[label + "_extreme_" + measure + "_count"] = count
                row[label + "_extreme_" + measure + "_pct"] = 100 * count / n if eligible and n else None
        for measure in ("day", "night"):
            row[measure + "_change_pp"] = row["late_extreme_" + measure + "_pct"] - row["early_extreme_" + measure + "_pct"] if valid else None
        row["night_minus_day_change_pp"] = row["night_change_pp"] - row["day_change_pp"] if valid else None
        rows.append(row)
    return pd.DataFrame(rows)


def build_heat_outputs(panel, settings):
    validate_calendar(panel, settings)
    thresholds = fit_thresholds(panel, settings)
    daily = attach_indicators(panel, thresholds)
    annual = summarize_years(daily, settings)
    comparison = compare_periods(annual, settings)
    # Counts and shares must reconcile with the observed denominators.
    for prefix, denom in (("extreme_day", "day_observed_days"), ("extreme_night", "night_observed_days"),
                          ("compound", "paired_days"), ("paired_extreme_day", "paired_days"), ("paired_extreme_night", "paired_days")):
        if (annual[prefix + "_count"] > annual[denom]).any() or (annual[prefix + "_count"] < 0).any():
            raise ValueError("Invalid annual event count: " + prefix)
        pct = annual[prefix + "_pct"].dropna()
        if not pct.between(0, 100).all():
            raise ValueError("Invalid annual percentage: " + prefix)
    validation = {"method": "project-relative calendar-day percentile; not official ETCCDI/IMD heatwave classification",
                  "settings": settings, "threshold_rows": len(thresholds), "annual_rows": len(annual),
                  "period_comparison_rows": len(comparison), "extreme_day_count": int(daily.extreme_day.sum()),
                  "extreme_night_count": int(daily.extreme_night.sum()),
                  "compound_extreme_count": int(daily.compound_extreme.sum()),
                  "missing_day_indicators": int(daily.extreme_day.isna().sum()),
                  "missing_night_indicators": int(daily.extreme_night.isna().sum()),
                  "ineligible_paired_city_years": int((~annual.paired_year_eligible).sum()),
                  "numpy_version": np.__version__}
    return daily, thresholds, annual, comparison, validation
