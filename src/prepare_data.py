# Merges Tmax and Tmin, checks the data, and saves the daily dataset.
"""Prepare and validate the daily temperature dataset."""

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEY = ["point_id", "date"]
OUTPUT_COLUMNS = [
    "point_id", "city", "date", "lat", "lon",
    "tmax_cell_lat", "tmax_cell_lon", "tmin_cell_lat", "tmin_cell_lon",
    "tmax", "tmin", "tmax_record_missing", "tmin_record_missing",
    "tmax_missing", "tmin_missing", "temperature_pair_complete",
]
OUTPUT_NAMES = ["daily_temperatures.csv", "validation_report.json",
                "validation_report.txt", "coverage_by_city_year.csv",
                "heat_thresholds.csv", "city_year_heat.csv", "city_period_comparison.csv"]
MISSING_TOKENS = {"", "na", "nan", "null", "none", "n/a"}


class ValidationError(ValueError):
    """An input cannot safely proceed to the next preparation step."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def numeric_float(text):
    """Use Python's correctly rounded parser, retaining full source precision."""
    try:
        return float(text)
    except ValueError:
        return float("nan")


def add_issue(report, code, message, count=1, examples=None, severity="error"):
    issue = {"code": code, "message": message, "count": int(count)}
    if examples is not None:
        issue["examples"] = examples
    report["errors" if severity == "error" else "warnings"].append(issue)


def flag_rows(report, df, mask, code, message):
    count = int(mask.sum())
    if count:
        sample = df.loc[mask, KEY].head(10).copy()
        sample["date"] = sample["date"].astype(str)
        add_issue(report, code, message, count, sample.to_dict("records"))


def stop_on_errors(report):
    if report["errors"]:
        raise ValidationError("Validation failed; see the report for checks and examples.")


def load_settings(path, lower=None, upper=None):
    settings = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    required = {"start_date", "end_date", "coordinate_tolerance",
                "allowed_missing_records", "temperature_min", "temperature_max"}
    if not isinstance(settings, dict) or set(settings) != required:
        raise ValidationError("Preparation config must contain exactly: " + ", ".join(sorted(required)))
    for field in ("start_date", "end_date"):
        text = settings[field]
        if not isinstance(text, str) or len(text) != 10 or pd.Timestamp(text).strftime("%Y-%m-%d") != text:
            raise ValidationError(field + " must be YYYY-MM-DD.")
    if settings["start_date"] > settings["end_date"]:
        raise ValidationError("start_date must be on or before end_date.")
    tolerance = settings["coordinate_tolerance"]
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or not 0 <= tolerance <= 0.01:
        raise ValidationError("coordinate_tolerance must be finite and between 0 and 0.01 degrees.")
    for field, override in (("temperature_min", lower), ("temperature_max", upper)):
        if override is not None:
            settings[field] = override
        value = settings[field]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
            raise ValidationError(field + " must be a finite number or null.")
    lo, hi = settings["temperature_min"], settings["temperature_max"]
    if lo is not None and hi is not None and lo > hi:
        raise ValidationError("temperature_min must not exceed temperature_max.")
    allowed = settings["allowed_missing_records"]
    if not isinstance(allowed, list):
        raise ValidationError("allowed_missing_records must be a list.")
    keys = []
    for item in allowed:
        if not isinstance(item, dict) or set(item) != {"point_id", "date"}:
            raise ValidationError("Each allowed missing record needs point_id and date.")
        pid, day = item["point_id"], item["date"]
        if isinstance(pid, bool) or not isinstance(pid, int) or pid < 0:
            raise ValidationError("Allowed missing point_id must be a nonnegative integer.")
        if not isinstance(day, str) or pd.Timestamp(day).strftime("%Y-%m-%d") != day:
            raise ValidationError("Allowed missing date must be YYYY-MM-DD.")
        if not settings["start_date"] <= day <= settings["end_date"]:
            raise ValidationError("Allowed missing date is outside the configured period.")
        keys.append((pid, day))
    if len(keys) != len(set(keys)):
        raise ValidationError("Duplicate entries in allowed_missing_records.")
    return settings


def load_cities(path):
    geo = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(geo, dict) or geo.get("type") != "FeatureCollection" or not isinstance(geo.get("features"), list) or not geo["features"]:
        raise ValidationError("Cities must be a nonempty GeoJSON FeatureCollection.")
    crs = geo.get("crs", {}).get("properties", {}).get("name")
    if crs and crs not in {"urn:ogc:def:crs:OGC:1.3:CRS84", "EPSG:4326", "urn:ogc:def:crs:EPSG::4326"}:
        raise ValidationError("City coordinates must use longitude/latitude (CRS84 or EPSG:4326).")
    rows = []
    for pid, feature in enumerate(geo["features"]):
        if not isinstance(feature, dict) or not isinstance(feature.get("geometry"), dict) or not isinstance(feature.get("properties"), dict):
            raise ValidationError("Each GeoJSON feature needs geometry and properties objects.")
        geometry = feature["geometry"]
        coords = geometry.get("coordinates", [])
        city = feature.get("properties", {}).get("city")
        if geometry.get("type") != "Point" or not isinstance(coords, list) or len(coords) != 2 or not isinstance(city, str) or not city.strip():
            raise ValidationError("Each city needs a name and a two-coordinate Point geometry.")
        lon, lat = coords
        if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) for x in coords):
            raise ValidationError("City coordinates must be finite numbers.")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValidationError("City coordinates are outside latitude/longitude bounds.")
        rows.append({"point_id": pid, "city": city, "lat": lat, "lon": lon})
    cities = pd.DataFrame(rows)
    if cities["city"].duplicated().any():
        raise ValidationError("City names must be unique.")
    return cities


def read_raw(path, cities, settings, report):
    """Strictly parse one source and stop before unsafe joins or conversions."""
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        for line, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValidationError(f"{path.name}: record {line} has {len(row)} fields; expected {len(header)}.")
    variables = [v for v in ("tmax", "tmin") if v in header]
    if len(variables) != 1:
        raise ValidationError(f"{path.name}: expected exactly one tmax or tmin value column.")
    var = variables[0]
    expected = {"time", "point_id", "lat", "lon", var + "_cell_lat", var + "_cell_lon", var}
    if len(header) != len(set(header)) or set(header) != expected:
        raise ValidationError(f"{path.name}: schema mismatch; expected {sorted(expected)}; got {header}.")
    # Strings avoid silently accepting malformed tokens or dropping bad rows.
    df = pd.read_csv(path, dtype=str, keep_default_na=False, skip_blank_lines=False)
    if df.empty:
        raise ValidationError(f"{path.name}: no observations.")
    df = df.rename(columns={"time": "date"})
    dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    flag_rows(report, df, ~df["date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}") | dates.isna(),
              var + ".invalid_date", "Dates must be valid YYYY-MM-DD calendar dates.")
    ids = pd.to_numeric(df["point_id"], errors="coerce")
    flag_rows(report, df, ~ids.isin(cities.point_id), var + ".invalid_point_id", "Point IDs must be integers in the city-file order.")
    stop_on_errors(report)
    df["point_id"] = ids.astype("int64")
    df["date"] = dates.dt.strftime("%Y-%m-%d")
    flag_rows(report, df, ~df.date.between(settings["start_date"], settings["end_date"]),
              var + ".outside_period", "Records fall outside the configured study period.")
    flag_rows(report, df, df.duplicated(KEY, keep=False), var + ".duplicate_key", "Duplicate point/date keys would multiply rows during a merge.")
    for column in ("lat", "lon", var + "_cell_lat", var + "_cell_lon", var):
        original = df[column]
        numeric = original.map(numeric_float).astype(float)
        missing = original.str.strip().str.lower().isin(MISSING_TOKENS)
        finite = numeric.notna() & ~numeric.isin([float("inf"), -float("inf")])
        bad = (~finite & ~missing) if column == var else ~finite
        flag_rows(report, df, bad, var + ".invalid_numeric." + column, "Nonfinite/nonnumeric values and missing coordinates are invalid.")
        df[column] = numeric
    stop_on_errors(report)
    lookup = cities.set_index("point_id")
    tol = settings["coordinate_tolerance"]
    for axis, limit in (("lat", 90), ("lon", 180)):
        flag_rows(report, df, (df[axis] - df.point_id.map(lookup[axis])).abs() > tol,
                  var + ".city_coordinate." + axis, "Point coordinates disagree with the city file.")
        col = var + "_cell_" + axis
        flag_rows(report, df, ~df[col].between(-limit, limit), var + ".grid_bounds." + axis, "Grid coordinates are outside geographic bounds.")
        spread = df.groupby("point_id")[col].transform("max") - df.groupby("point_id")[col].transform("min")
        flag_rows(report, df, spread > tol, var + ".grid_changes." + axis, "The source assigns multiple grid coordinates to one point.")
    flag_rows(report, df, df[var].isna(), var + ".missing_value", "A source record has a missing temperature; it is not an allowed absent record.")
    lo, hi = settings["temperature_min"], settings["temperature_max"]
    if lo is not None:
        flag_rows(report, df, df[var] < lo, var + ".below_bound", "Temperature is below the explicitly configured quality-control bound.")
    if hi is not None:
        flag_rows(report, df, df[var] > hi, var + ".above_bound", "Temperature is above the explicitly configured quality-control bound.")
    report["inputs"][var] = {
        "file": path.name, "sha256": sha256(path), "rows": len(df),
        "date_min": df.date.min(), "date_max": df.date.max(),
        "point_ids": sorted(int(x) for x in df.point_id.unique()),
        "duplicate_key_rows": int(df.duplicated(KEY, keep=False).sum()),
        "missing_values": {col: int(n) for col, n in df.isna().sum().items()},
        "temperature_min": float(df[var].min()) if df[var].notna().any() else None,
        "temperature_max": float(df[var].max()) if df[var].notna().any() else None,
    }
    stop_on_errors(report)
    return var, df


def build_panel(paths, cities_path, settings_path, lower=None, upper=None, report=None):
    """Return the full calendar panel, coverage table and computed validation report."""
    if report is None:
        report = {"errors": [], "warnings": [], "inputs": {}, "dataset_published": False}
    settings = load_settings(settings_path, lower, upper)
    cities = load_cities(cities_path)
    if any(x["point_id"] not in set(cities.point_id) for x in settings["allowed_missing_records"]):
        raise ValidationError("Allowed missing point_id is absent from the city file.")
    report.update({"schema_version": 1, "settings": settings,
                   "cities_sha256": sha256(cities_path), "config_sha256": sha256(settings_path),
                   "software": {"python": platform.python_version(), "pandas": pd.__version__},
                   "units": "as supplied; raw CSVs do not contain unit metadata"})
    if len(paths) != 2:
        raise ValidationError(f"Expected exactly two raw CSVs; found {len(paths)}.")
    frames = {}
    for path in paths:
        var, df = read_raw(path, cities, settings, report)
        if var in frames:
            raise ValidationError("The inputs must contain one tmax file and one tmin file.")
        frames[var] = df
    calendar = pd.date_range(settings["start_date"], settings["end_date"])
    panel = pd.MultiIndex.from_product([cities.point_id, calendar.strftime("%Y-%m-%d")], names=KEY).to_frame(index=False)
    panel = panel.merge(cities, on="point_id", validate="many_to_one")
    allowed = {(x["point_id"], x["date"]) for x in settings["allowed_missing_records"]}
    for var in ("tmax", "tmin"):
        frame = frames[var].drop(columns=["lat", "lon"])
        marker = var + "_record_missing"
        panel = panel.merge(frame.assign(**{marker: False}), on=KEY, how="left", validate="one_to_one")
        panel[marker] = panel[marker].isna()
        panel[var + "_missing"] = panel[var].isna()
        missing = panel.loc[panel[marker], KEY]
        is_allowed = pd.Series([tuple(x) in allowed for x in missing.itertuples(index=False, name=None)], index=missing.index, dtype=bool)
        unexpected, approved = missing.loc[~is_allowed], missing.loc[is_allowed]
        if len(unexpected):
            add_issue(report, var + ".unexpected_missing_records", "Unapproved gaps in the complete city-day calendar.",
                      len(unexpected), unexpected.head(10).to_dict("records"))
        if len(approved):
            add_issue(report, var + ".allowed_missing_records", "Known gaps are preserved as flagged rows with blank temperatures.",
                      len(approved), approved.head(10).to_dict("records"), severity="warning")
    both = ~panel.tmax_record_missing & ~panel.tmin_record_missing
    report["merge"] = {
        "both": int(both.sum()),
        "tmax_only": int((~panel.tmax_record_missing & panel.tmin_record_missing).sum()),
        "tmin_only": int((panel.tmax_record_missing & ~panel.tmin_record_missing).sum()),
        "neither": int((panel.tmax_record_missing & panel.tmin_record_missing).sum()),
    }
    for axis in ("lat", "lon"):
        flag_rows(report, panel, both & ((panel["tmax_cell_" + axis] - panel["tmin_cell_" + axis]).abs() > settings["coordinate_tolerance"]),
                  "cross_file.grid_mismatch." + axis, "Tmax and Tmin use different grid coordinates.")
    flag_rows(report, panel, panel.tmin > panel.tmax, "cross_file.tmin_above_tmax", "Daily Tmin exceeds Tmax; values have not been changed.")
    report["cross_file"] = {
        "tmin_above_tmax": int((panel.tmin > panel.tmax).sum()),
        "grid_coordinate_mismatches": int((both & (
            ((panel.tmax_cell_lat - panel.tmin_cell_lat).abs() > settings["coordinate_tolerance"]) |
            ((panel.tmax_cell_lon - panel.tmin_cell_lon).abs() > settings["coordinate_tolerance"])
        )).sum()),
    }
    panel["temperature_pair_complete"] = ~panel.tmax_missing & ~panel.tmin_missing
    panel = panel[OUTPUT_COLUMNS].sort_values(KEY, ignore_index=True)
    if len(panel) != len(cities) * len(calendar) or panel.duplicated(KEY).any() or panel.duplicated(["city", "date"]).any():
        raise ValidationError("Internal panel count or uniqueness check failed.")
    report["panel"] = {
        "rows": len(panel), "expected_rows": len(cities) * len(calendar),
        "cities": len(cities), "calendar_days": len(calendar),
        "date_min": panel.date.min(), "date_max": panel.date.max(),
        "duplicate_city_dates": int(panel.duplicated(["city", "date"]).sum()),
        "complete_temperature_pairs": int(panel.temperature_pair_complete.sum()),
        "missing_tmax": int(panel.tmax_missing.sum()), "missing_tmin": int(panel.tmin_missing.sum()),
    }
    report["allowed_gap_observations"] = [
        {**item, **{var + "_record_missing": bool(panel.loc[(panel.point_id == item["point_id"]) & (panel.date == item["date"]), var + "_record_missing"].iloc[0]) for var in ("tmax", "tmin")}}
        for item in settings["allowed_missing_records"]
    ]
    coverage = panel.assign(year=panel.date.str[:4].astype(int)).groupby(["point_id", "city", "year"], as_index=False).agg(
        expected_days=("date", "size"), observed_tmax=("tmax", "count"), observed_tmin=("tmin", "count"),
        missing_tmax_records=("tmax_record_missing", "sum"), missing_tmin_records=("tmin_record_missing", "sum"),
        missing_tmax_values=("tmax_missing", "sum"), missing_tmin_values=("tmin_missing", "sum"),
        complete_pairs=("temperature_pair_complete", "sum"))
    message = "Raw CSVs omit units and clock-time alignment; see the project source metadata. No numerical conversion is performed."
    if settings["temperature_min"] is None and settings["temperature_max"] is None:
        message += " Physical plausibility bounds are unset; no absolute-temperature cutoff has been applied."
    add_issue(report, "metadata_pending", message, severity="warning")
    stop_on_errors(report)
    report["status"] = "passed_with_warnings" if report["warnings"] else "passed"
    return panel, coverage, report


def atomic_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".preparation-", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def csv_text(frame):
    # Seventeen significant digits retain binary float precision; no rounding.
    return frame.to_csv(index=False, na_rep="", float_format="%.17g", lineterminator="\n")


def summary_text(report):
    lines = ["IMD temperature preparation validation", "Status: " + report.get("status", "failed"),
             "Dataset published by this run: " + str(report.get("dataset_published", False))]
    if "panel" in report:
        p = report["panel"]
        lines += [f"Panel: {p['rows']:,} / {p['expected_rows']:,} expected rows; {p['cities']} cities; {p['calendar_days']:,} days.",
                  f"Complete temperature pairs: {p['complete_temperature_pairs']:,}; missing Tmax: {p['missing_tmax']}; missing Tmin: {p['missing_tmin']}."]
    if "merge" in report:
        lines.append("Source-record matches: " + json.dumps(report["merge"], sort_keys=True))
    if "heat_metrics" in report:
        heat = report["heat_metrics"]
        lines.append(f"Heat outputs: {heat['threshold_rows']:,} threshold rows; {heat['annual_rows']} city-years; {heat['period_comparison_rows']} city comparisons.")
        lines.append(f"Flagged observations: {heat['extreme_day_count']:,} warm days; {heat['extreme_night_count']:,} warm nights; {heat['compound_extreme_count']:,} same-source-date co-exceedances.")
    for group in ("errors", "warnings"):
        for issue in report[group]:
            lines.append(f"{group.upper()}: {issue['code']} ({issue['count']}): {issue['message']}")
    if report.get("status") == "failed":
        lines.append("No new validated dataset is available from this run. Existing CSVs may belong to an earlier run.")
    return "\n".join(lines) + "\n"


def main(argv=None, audit_only=False):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_files", nargs="*", type=Path, help="Two source CSVs, in either order; defaults to data/raw/*.csv.")
    parser.add_argument("--cities", type=Path, default=ROOT / "config/cities.geojson")
    parser.add_argument("--config", type=Path, default=ROOT / "config/preparation.json")
    parser.add_argument("--heat-config", type=Path, default=ROOT / "config/heat_metrics.json")
    parser.add_argument("--source-metadata", type=Path, default=ROOT / "config/source_metadata.json")
    parser.add_argument("--skip-heat", action="store_true", help="Produce only the preliminary temperature panel and coverage.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--temperature-min", type=float, help="Explicit lower QC bound in source units; no default.")
    parser.add_argument("--temperature-max", type=float, help="Explicit upper QC bound in source units; no default.")
    parser.add_argument("--audit-only", action="store_true", help="Run the same checks and print JSON without writing files.")
    args = parser.parse_args(argv)
    audit_only = audit_only or args.audit_only
    paths = args.raw_files or sorted((ROOT / "data/raw").glob("*.csv"))
    report = {"errors": [], "warnings": [], "inputs": {}, "dataset_published": False}
    if not audit_only:
        output_dir = args.output_dir.resolve()
        raw_dir = (ROOT / "data/raw").resolve()
        protected = {p.resolve() for p in [*paths, args.cities, args.config, args.heat_config, args.source_metadata]}
        if output_dir == raw_dir or raw_dir in output_dir.parents or any((output_dir / n).resolve() in protected for n in OUTPUT_NAMES):
            print("ERROR: output directory could overwrite raw inputs or configuration.", file=sys.stderr)
            return 2
    try:
        panel, coverage, report = build_panel(paths, args.cities, args.config,
                                             args.temperature_min, args.temperature_max, report)
        if not audit_only:
            frames = {"coverage_by_city_year.csv": coverage}
            if not args.skip_heat:
                from heat_metrics import build_heat_outputs, load_heat_settings, validate_imd_grid
                settings = load_heat_settings(args.heat_config)
                metadata = json.loads(args.source_metadata.read_text(encoding="utf-8-sig"))
                report["source_grid"] = validate_imd_grid(panel, metadata, report["settings"]["coordinate_tolerance"])
                panel, thresholds, annual, comparison, heat = build_heat_outputs(panel, settings)
                frames.update({"heat_thresholds.csv": thresholds, "city_year_heat.csv": annual,
                               "city_period_comparison.csv": comparison})
                report["heat_metrics"] = heat
                report["heat_config_sha256"] = sha256(args.heat_config)
                report["source_metadata_sha256"] = sha256(args.source_metadata)
                report["source_metadata"] = metadata
                report["units"] = metadata["temperature_units"]
                report["warnings"] = [item for item in report["warnings"] if item["code"] != "metadata_pending"]
                add_issue(report, "source_date_alignment", "Exact clock-time alignment is not established for this export; retain source dates and use Tmin as a nighttime proxy.", severity="warning")
                add_issue(report, "reference_method", "Project-relative percentiles use the configured available-data baseline and no ETCCDI bootstrap; these are not official ETCCDI or IMD heatwave indices.", severity="warning")
                add_issue(report, "source_network_change", metadata["network_caveat"], severity="warning")
                if heat["ineligible_paired_city_years"]:
                    add_issue(report, "ineligible_city_years", "Annual percentages are suppressed for city-years failing coverage rules.", heat["ineligible_paired_city_years"], severity="warning")
                report["status"] = "passed_with_warnings" if report["warnings"] else "passed"
            frames = {"daily_temperatures.csv": panel, **frames}
            # Validate and serialize everything before publishing any data file.
            serialized = {name: csv_text(frame) for name, frame in frames.items()}
            fingerprints = {}
            for name, text in serialized.items():
                atomic_text(args.output_dir / name, text)
                fingerprints[name] = hashlib.sha256(text.encode("utf-8")).hexdigest()
            report["dataset_published"] = True
            report["output"] = {"file": "daily_temperatures.csv", "sha256": fingerprints["daily_temperatures.csv"],
                                "files_sha256": fingerprints, "columns": panel.columns.tolist(),
                                "dtypes": {col: str(panel[col].dtype) for col in panel}}
    except (ValueError, OSError, KeyError, TypeError, OverflowError, csv.Error) as exc:
        if not report["errors"]:
            add_issue(report, "input_or_output_failure", str(exc))
        report["status"] = "failed"
    if audit_only:
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    else:
        try:
            atomic_text(args.output_dir / "validation_report.json", json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
            atomic_text(args.output_dir / "validation_report.txt", summary_text(report))
        except OSError as exc:
            print(f"ERROR: could not write validation report: {exc}", file=sys.stderr)
            return 2
        print(summary_text(report), end="")
        print("Outputs: " + str(args.output_dir.resolve()))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
