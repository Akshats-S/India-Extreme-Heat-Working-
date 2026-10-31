"""Independent known-answer and failure checks for the heat measurement method."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from heat_metrics import (attach_indicators, build_heat_outputs, fit_thresholds,
                          load_heat_settings, validate_calendar, validate_imd_grid)
from prepare_data import build_panel, main, sha256


def fixture_settings():
    return {"baseline_start_year": 2001, "baseline_end_year": 2002,
            "percentile": 90, "window_days": 5, "quantile_method": "median_unbiased",
            "minimum_baseline_years": 2, "minimum_window_coverage": 0.9,
            "annual_max_missing_days": 15, "monthly_max_missing_days": 3,
            "early_period": [2001, 2002], "late_period": [2003, 2004]}


def fixture_panel():
    dates = pd.date_range("2001-01-01", "2004-12-31")
    return pd.DataFrame({"point_id": 0, "city": "Synthetic City", "date": dates.strftime("%Y-%m-%d"),
                         "lat": 28.6, "lon": 77.2, "tmax_cell_lat": 28.5, "tmax_cell_lon": 77.5,
                         "tmin_cell_lat": 28.5, "tmin_cell_lon": 77.5,
                         "tmax": np.where(dates.year <= 2002, 30.0, 40.0), "tmin": 20.0})


class HeatMetricTests(unittest.TestCase):
    def setUp(self):
        self.panel = fixture_panel()
        self.settings = fixture_settings()

    def test_known_answer_strict_boundary_annual_counts_and_period_changes(self):
        daily, thresholds, annual, comparison, validation = build_heat_outputs(self.panel, self.settings)
        self.assertEqual(len(daily), 1461)
        self.assertEqual(len(thresholds), 366)
        self.assertTrue((thresholds.tmax_threshold_c == 30).all())
        self.assertTrue((thresholds.tmin_threshold_c == 20).all())
        self.assertFalse(daily.loc[daily.date < "2003-01-01", "extreme_day"].any())
        self.assertFalse(daily.extreme_night.any())
        self.assertEqual(annual.extreme_day_count.tolist(), [0, 0, 365, 366])
        self.assertEqual(annual.extreme_day_pct.tolist(), [0, 0, 100, 100])
        self.assertTrue(annual.paired_year_eligible.all())
        self.assertEqual(annual.night_minus_day_pp.tolist(), [0, 0, -100, -100])
        self.assertEqual(comparison.day_change_pp.iloc[0], 100)
        self.assertEqual(comparison.night_change_pp.iloc[0], 0)
        self.assertEqual(comparison.night_minus_day_change_pp.iloc[0], -100)
        self.assertEqual(validation["extreme_day_count"], 731)

    def test_circular_five_day_window_and_type_eight_hand_calculation(self):
        self.panel["tmax"] = 0.0
        for year, values in [(2001, range(5)), (2002, range(5, 10))]:
            for day, value in zip(["12-30", "12-31", "01-01", "01-02", "01-03"], values):
                self.panel.loc[self.panel.date == f"{year}-{day}", "tmax"] = value
        thresholds = fit_thresholds(self.panel, self.settings)
        jan = thresholds.loc[thresholds.calendar_day == "01-01"].iloc[0]
        # Type 8 for sorted 0..9: h=(10+1/3)*0.9+1/3, giving 8 + 19/30.
        self.assertAlmostEqual(jan.tmax_threshold_c, 8 + 19 / 30)
        self.assertEqual(jan.tmax_baseline_samples, 10)

    def test_thresholds_do_not_use_outside_reference_values(self):
        first = fit_thresholds(self.panel, self.settings)
        self.panel.loc[self.panel.date >= "2003-01-01", "tmax"] = 1000
        second = fit_thresholds(self.panel, self.settings)
        pd.testing.assert_frame_equal(first, second)

    def test_seasonal_windows_and_cities_are_fitted_separately(self):
        self.panel["tmax"] = np.where(self.panel.date.str[5:7].isin(["06", "07", "08"]), 40.0, 10.0)
        second = self.panel.assign(point_id=1, city="Synthetic Other", tmax=self.panel.tmax + 5)
        table = fit_thresholds(pd.concat([self.panel, second], ignore_index=True), self.settings)
        self.assertEqual(table.loc[(table.point_id == 0) & (table.calendar_day == "07-15"), "tmax_threshold_c"].iloc[0], 40)
        self.assertEqual(table.loc[(table.point_id == 0) & (table.calendar_day == "01-15"), "tmax_threshold_c"].iloc[0], 10)
        self.assertEqual(table.loc[(table.point_id == 1) & (table.calendar_day == "01-15"), "tmax_threshold_c"].iloc[0], 15)

    def test_leap_day_excluded_from_fit_and_threshold_interpolated(self):
        self.settings["baseline_end_year"] = 2004
        first = fit_thresholds(self.panel, self.settings)
        self.panel.loc[self.panel.date == "2004-02-29", "tmax"] = 1000
        second = fit_thresholds(self.panel, self.settings)
        pd.testing.assert_frame_equal(first, second)
        leap = second.loc[second.calendar_day == "02-29"].iloc[0]
        neighbors = second.loc[second.calendar_day.isin(["02-28", "03-01"])]
        self.assertEqual(leap.tmax_threshold_c, neighbors.tmax_threshold_c.mean())
        self.assertTrue(leap.threshold_is_interpolated)
        self.assertTrue(pd.isna(leap.tmax_baseline_samples))
        self.assertEqual(len(attach_indicators(self.panel, second)), 1461)

    def test_missing_indicators_and_paired_denominators(self):
        missing = self.panel.date == "2003-06-26"
        self.panel.loc[missing, "tmin"] = np.nan
        daily, _, annual, _, _ = build_heat_outputs(self.panel, self.settings)
        gap = daily.loc[missing].iloc[0]
        self.assertTrue(gap.extreme_day)
        self.assertTrue(pd.isna(gap.extreme_night) and pd.isna(gap.compound_extreme))
        year = annual.loc[annual.year == 2003].iloc[0]
        self.assertEqual(year.day_observed_days, 365)
        self.assertEqual(year.night_observed_days, 364)
        self.assertEqual(year.paired_days, 364)
        self.assertEqual(year.extreme_day_count, 365)
        self.assertEqual(year.paired_extreme_day_count, 364)
        self.assertEqual(year.night_minus_day_pp, -100)
        # A false day flag must not turn an unknown compound event into False.
        self.panel.loc[missing, "tmax"] = 30
        daily = attach_indicators(self.panel, fit_thresholds(self.panel, self.settings))
        self.assertTrue(pd.isna(daily.loc[missing, "compound_extreme"].iloc[0]))

    def test_baseline_coverage_limit(self):
        self.panel.loc[self.panel.date == "2001-01-01", "tmax"] = np.nan
        table = fit_thresholds(self.panel, self.settings)
        self.assertEqual(table.loc[table.calendar_day == "01-01", "tmax_baseline_samples"].iloc[0], 9)
        self.panel.loc[self.panel.date == "2002-01-01", "tmax"] = np.nan
        with self.assertRaisesRegex(ValueError, "Insufficient baseline"):
            fit_thresholds(self.panel, self.settings)

    def test_annual_and_monthly_missing_limits_suppress_percentages(self):
        for label, days in [("monthly", pd.date_range("2003-06-01", periods=4)),
                            ("annual", pd.date_range("2003-01-01", "2003-08-31", freq="15D"))]:
            with self.subTest(limit=label):
                panel = self.panel.copy()
                panel.loc[panel.date.isin(days.strftime("%Y-%m-%d")), ["tmax", "tmin"]] = np.nan
                _, _, annual, comparison, result = build_heat_outputs(panel, self.settings)
                year = annual.loc[annual.year == 2003].iloc[0]
                self.assertFalse(year.paired_year_eligible)
                self.assertTrue(pd.isna(year.extreme_day_pct) and pd.isna(year.night_minus_day_pp))
                self.assertFalse(comparison.late_eligible.iloc[0])
                self.assertTrue(pd.isna(comparison.day_change_pp.iloc[0]))
                self.assertGreater(result["ineligible_paired_city_years"], 0)

    def test_baseline_and_calendar_gaps_fail(self):
        for panel in (self.panel.iloc[1:], pd.concat([self.panel, self.panel.iloc[[0]]]),
                      self.panel.loc[self.panel.date != "2002-05-03"]):
            with self.subTest(rows=len(panel)):
                with self.assertRaises(ValueError):
                    validate_calendar(panel, self.settings)

    def test_partial_year_is_ineligible(self):
        panel = self.panel.loc[self.panel.date <= "2004-06-30"]
        _, _, annual, comparison, _ = build_heat_outputs(panel, self.settings)
        partial = annual.loc[annual.year == 2004].iloc[0]
        self.assertFalse(partial.calendar_complete)
        self.assertTrue(pd.isna(partial.extreme_day_pct))
        self.assertFalse(comparison.late_eligible.iloc[0])

    def test_invalid_heat_configs_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "heat.json"
            for changes in ({"percentile": 100}, {"percentile": float("nan")}, {"window_days": 4},
                            {"minimum_window_coverage": 0}, {"minimum_baseline_years": 10},
                            {"monthly_max_missing_days": -1}, {"quantile_method": "unknown"},
                            {"late_period": [2002, 2004]}):
                with self.subTest(changes=changes):
                    path.write_text(json.dumps({**self.settings, **changes}))
                    with self.assertRaises(ValueError):
                        load_heat_settings(path)

    def test_imd_grid_contract_accepts_nearest_nodes_and_rejects_other_nodes(self):
        metadata = json.loads((ROOT / "config/source_metadata.json").read_text())
        self.assertEqual(validate_imd_grid(self.panel, metadata)["mismatches"], 0)
        wrong = self.panel.assign(tmax_cell_lon=78.5)
        with self.assertRaises(ValueError):
            validate_imd_grid(wrong, metadata)
        sentinel = self.panel.copy()
        sentinel.loc[0, "tmax"] = 99.9
        with self.assertRaisesRegex(ValueError, "missing sentinel"):
            validate_imd_grid(sentinel, metadata)

    def test_end_to_end_cli_outputs_deterministic_and_heat_failure_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            paths = []
            for var in ("tmax", "tmin"):
                columns = ["date", "point_id", "lat", "lon", var + "_cell_lat", var + "_cell_lon", var]
                path = directory / (var + ".csv")
                self.panel[columns].rename(columns={"date": "time"}).to_csv(path, index=False)
                paths.append(path)
            cities = directory / "cities.geojson"
            cities.write_text(json.dumps({"type": "FeatureCollection", "features": [
                {"properties": {"city": "Synthetic City"}, "geometry": {"type": "Point", "coordinates": [77.2, 28.6]}}]}))
            prep = directory / "prep.json"
            prep.write_text(json.dumps({"start_date": "2001-01-01", "end_date": "2004-12-31",
                                        "coordinate_tolerance": 0.000001, "allowed_missing_records": [],
                                        "temperature_min": -90, "temperature_max": 60}))
            heat = directory / "heat.json"
            heat.write_text(json.dumps(self.settings))
            args = [*[str(p) for p in paths], "--cities", str(cities), "--config", str(prep),
                    "--heat-config", str(heat), "--output-dir", str(directory / "out")]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
                snapshot = {p.name: p.read_bytes() for p in (directory / "out").iterdir()}
                self.assertEqual(len(snapshot), 7)
                self.assertEqual(main(args), 0)
                self.assertEqual(snapshot, {p.name: p.read_bytes() for p in (directory / "out").iterdir()})
                heat.write_text(json.dumps({**self.settings, "baseline_start_year": 1990}))
                failure = args[:-1] + [str(directory / "failed")]
                self.assertEqual(main(failure), 1)
                self.assertFalse((directory / "failed/daily_temperatures.csv").exists())


RAW_PATHS = [ROOT / "data/raw/imdweb_B3KKauQB.csv", ROOT / "data/raw/imdweb_5PfvCU0D.csv"]


@unittest.skipUnless(all(p.exists() for p in RAW_PATHS), "Real sources unavailable.")
class RealHeatAcceptanceTests(unittest.TestCase):
    def test_actual_heat_outputs_reconcile_preserve_values_and_known_gap(self):
        hashes = [sha256(p) for p in RAW_PATHS]
        panel, _, _ = build_panel(RAW_PATHS, ROOT / "config/cities.geojson", ROOT / "config/preparation.json")
        settings = load_heat_settings(ROOT / "config/heat_metrics.json")
        daily, thresholds, annual, comparison, result = build_heat_outputs(panel, settings)
        self.assertEqual(len(daily), 140256)
        self.assertEqual(len(thresholds), 16 * 366)
        self.assertEqual(len(annual), 384)
        self.assertEqual(len(comparison), 16)
        self.assertEqual(result["ineligible_paired_city_years"], 0)
        self.assertEqual(result["missing_day_indicators"], 1)
        self.assertEqual(result["missing_night_indicators"], 1)
        gap = daily.loc[daily.tmax.isna()].iloc[0]
        self.assertEqual((gap.city, gap.date), ("Guwahati", "2005-06-26"))
        self.assertTrue(pd.isna(gap.extreme_day) and pd.isna(gap.extreme_night) and pd.isna(gap.compound_extreme))
        guwahati = annual.loc[(annual.city == "Guwahati") & (annual.year == 2005)].iloc[0]
        self.assertEqual(guwahati.paired_days, 364)
        self.assertEqual(int(annual.extreme_day_count.sum()), int(daily.extreme_day.sum()))
        self.assertEqual(int(annual.extreme_night_count.sum()), int(daily.extreme_night.sum()))
        pd.testing.assert_frame_equal(panel[["point_id", "date", "tmax", "tmin"]], daily[["point_id", "date", "tmax", "tmin"]])
        self.assertEqual(hashes, [sha256(p) for p in RAW_PATHS])


if __name__ == "__main__":
    unittest.main()
