"""Synthetic edge cases plus acceptance checks when the real sources are present."""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from prepare_data import OUTPUT_COLUMNS, ValidationError, build_panel, csv_text, main, sha256


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.city_path = self.directory / "cities.geojson"
        self.config_path = self.directory / "preparation.json"
        self.settings = {
            "start_date": "2024-02-28", "end_date": "2024-03-01",
            "coordinate_tolerance": 0.000001, "allowed_missing_records": [],
            "temperature_min": None, "temperature_max": None,
        }
        self.geo = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"city": name},
             "geometry": {"type": "Point", "coordinates": coords}}
            for name, coords in [("Synthetic North", [77.2, 28.6]), ("Synthetic South", [76.2, 9.9])]
        ]}
        self.city_path.write_text(json.dumps(self.geo), encoding="utf-8")
        self.paths = []
        for var, value in [("tmax", 35.12345678901234), ("tmin", 20.0)]:
            rows = []
            for pid, (lon, lat) in enumerate([[77.2, 28.6], [76.2, 9.9]]):
                for date in ["2024-02-28", "2024-02-29", "2024-03-01"]:
                    rows.append({"time": date, "point_id": pid, "lat": lat, "lon": lon,
                                 var + "_cell_lat": int(lat) + 0.5,
                                 var + "_cell_lon": int(lon) + 0.5, var: value})
            path = self.directory / ("random-name-" + var + ".csv")
            pd.DataFrame(rows).to_csv(path, index=False)
            self.paths.append(path)
        self.write_settings()

    def write_settings(self):
        self.config_path.write_text(json.dumps(self.settings), encoding="utf-8")

    def build(self):
        return build_panel(self.paths, self.city_path, self.config_path)

    def mutate(self, index, edit):
        frame = pd.read_csv(self.paths[index])
        result = edit(frame)
        (frame if result is None else result).to_csv(self.paths[index], index=False)

    def run_cli(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main([str(x) for x in self.paths] + ["--cities", str(self.city_path), "--config", str(self.config_path),
                                                      "--output-dir", str(self.directory / "out"), *extra])

    def test_complete_panel_preserves_values_types_and_leap_day(self):
        panel, coverage, report = self.build()
        self.assertEqual(panel.columns.tolist(), OUTPUT_COLUMNS)
        self.assertEqual(len(panel), 6)
        self.assertEqual(panel.date.tolist().count("2024-02-29"), 2)
        self.assertEqual(str(panel.point_id.dtype), "int64")
        self.assertEqual(str(panel.tmax.dtype), "float64")
        self.assertEqual(str(panel.tmax_missing.dtype), "bool")
        self.assertEqual(panel.tmax.iloc[0], 35.12345678901234)
        self.assertTrue(panel.temperature_pair_complete.all())
        exported = pd.read_csv(io.StringIO(csv_text(panel)), float_precision="round_trip")
        self.assertTrue((panel.tmax == exported.tmax).all())
        self.assertEqual(coverage.expected_days.tolist(), [3, 3])
        self.assertEqual(report["merge"], {"both": 6, "tmax_only": 0, "tmin_only": 0, "neither": 0})
        self.assertEqual(report["errors"], [])

    def test_allowed_gap_stays_in_panel_without_filled_temperatures_or_grid(self):
        self.settings["allowed_missing_records"] = [{"point_id": 1, "date": "2024-02-29"}]
        self.write_settings()
        for index in (0, 1):
            self.mutate(index, lambda df: df.loc[~((df.point_id == 1) & (df.time == "2024-02-29"))])
        panel, coverage, report = self.build()
        gap = panel.loc[(panel.point_id == 1) & (panel.date == "2024-02-29")].iloc[0]
        self.assertEqual(len(panel), 6)
        self.assertTrue(pd.isna(gap.tmax) and pd.isna(gap.tmin) and pd.isna(gap.tmax_cell_lat))
        self.assertTrue(gap.tmax_record_missing and gap.tmin_record_missing and gap.tmax_missing)
        self.assertFalse(gap.temperature_pair_complete)
        self.assertEqual(gap.city, "Synthetic South")
        self.assertEqual(gap.lat, 9.9)
        self.assertEqual(report["merge"]["neither"], 1)
        self.assertTrue(report["allowed_gap_observations"][0]["tmax_record_missing"])
        self.assertEqual(int(coverage.missing_tmax_values.sum()), 1)

    def test_source_decimal_precision_survives_parsing_and_csv_export(self):
        # Default fast CSV/numeric parsers can lose the last binary digit here.
        self.mutate(0, lambda df: df.assign(tmax=22.329999923706055))
        panel, _, _ = self.build()
        raw = pd.read_csv(self.paths[0], float_precision="round_trip")
        exported = pd.read_csv(io.StringIO(csv_text(panel)), float_precision="round_trip")
        self.assertTrue((raw.tmax == exported.tmax).all())

    def test_one_sided_allowed_gap_reports_unmatched_row(self):
        self.settings["allowed_missing_records"] = [{"point_id": 0, "date": "2024-02-28"}]
        self.write_settings()
        self.mutate(1, lambda df: df.iloc[1:])
        panel, _, report = self.build()
        self.assertEqual(report["merge"]["tmax_only"], 1)
        self.assertEqual(report["merge"]["both"], 5)
        self.assertFalse(panel.tmax_record_missing.iloc[0])
        self.assertTrue(panel.tmin_record_missing.iloc[0])

    def test_unapproved_gap_and_completely_missing_city_fail(self):
        for drop in (lambda df: df.iloc[1:], lambda df: df.loc[df.point_id == 0]):
            with self.subTest(drop=drop):
                original = self.paths[0].read_bytes()
                self.mutate(0, drop)
                with self.assertRaises(ValidationError):
                    self.build()
                self.paths[0].write_bytes(original)

    def test_faulty_records_are_rejected(self):
        cases = [
            ("duplicate", lambda df: pd.concat([df, df.iloc[[0]]], ignore_index=True)),
            ("missing schema column", lambda df: df.drop(columns=["lat"])),
            ("extra schema column", lambda df: df.assign(unexpected=1)),
            ("invalid date", lambda df: df.assign(time="2024-02-30")),
            ("noncanonical date", lambda df: df.assign(time="2024-2-28")),
            ("outside period", lambda df: df.assign(time="2023-02-28")),
            ("unexpected id", lambda df: df.assign(point_id=16)),
            ("fractional id", lambda df: df.assign(point_id=0.5)),
            ("missing id", lambda df: df.assign(point_id=float("nan"))),
            ("nonnumeric", lambda df: df.assign(tmax="bad")),
            ("infinite", lambda df: df.assign(tmax=float("inf"))),
            ("missing temperature", lambda df: df.assign(tmax=float("nan"))),
            ("wrong city coordinates", lambda df: df.assign(lat=0)),
            ("missing coordinates", lambda df: df.assign(lon=float("nan"))),
            ("invalid grid", lambda df: df.assign(tmax_cell_lat=91)),
            ("tmin above tmax", lambda df: df.assign(tmax=10)),
        ]
        original = self.paths[0].read_bytes()
        for label, edit in cases:
            with self.subTest(case=label):
                self.paths[0].write_bytes(original)
                self.mutate(0, edit)
                with self.assertRaises(ValidationError):
                    self.build()

    def test_grid_changes_and_cross_file_disagreement_fail(self):
        original = self.paths[0].read_bytes()
        self.mutate(0, lambda df: df.assign(tmax_cell_lon=df.tmax_cell_lon + (df.time == "2024-02-29").astype(int)))
        with self.assertRaises(ValidationError):
            self.build()
        self.paths[0].write_bytes(original)
        self.mutate(0, lambda df: df.assign(tmax_cell_lon=df.tmax_cell_lon + 1))
        with self.assertRaises(ValidationError):
            self.build()

    def test_malformed_csv_and_duplicate_headers_fail(self):
        original = self.paths[0].read_text()
        for malformed in (original.replace("time,point_id", "time,time"), original + "one,two\n", original + "\n", original.replace("35.123", "extra,35.123")):
            with self.subTest(malformed=malformed[-40:]):
                self.paths[0].write_text(malformed)
                with self.assertRaises((ValidationError, ValueError)):
                    self.build()

    def test_two_files_of_same_variable_fail(self):
        self.paths = [self.paths[0], self.paths[0]]
        with self.assertRaises(ValidationError):
            self.build()

    def test_wrong_file_count_and_empty_source_fail(self):
        with self.assertRaises(ValidationError):
            build_panel(self.paths[:1], self.city_path, self.config_path)
        self.mutate(0, lambda df: df.iloc[:0])
        with self.assertRaises(ValidationError):
            self.build()

    def test_configured_plausibility_bounds_are_enforced(self):
        self.assertEqual(self.run_cli("--temperature-max", "30"), 1)
        report = json.loads((self.directory / "out/validation_report.json").read_text())
        self.assertIn("tmax.above_bound", [item["code"] for item in report["errors"]])
        self.assertEqual(self.run_cli("--temperature-min", "40", "--temperature-max", "30"), 1)

    def test_invalid_settings_and_city_metadata_fail(self):
        for changes in ({"start_date": "2025-01-01"}, {"coordinate_tolerance": -1},
                        {"temperature_min": float("inf")},
                        {"allowed_missing_records": [{"point_id": 99, "date": "2024-02-29"}]}):
            with self.subTest(changes=changes):
                settings = self.settings.copy()
                settings.update(changes)
                self.config_path.write_text(json.dumps(settings))
                with self.assertRaises(ValidationError):
                    self.build()
        self.write_settings()
        self.geo["features"][1]["properties"]["city"] = "Synthetic North"
        self.city_path.write_text(json.dumps(self.geo))
        with self.assertRaises(ValidationError):
            self.build()

    def test_output_is_deterministic_with_reversed_inputs_and_shuffled_rows(self):
        first, _, report = self.build()
        for index in (0, 1):
            self.mutate(index, lambda df: df.sample(frac=1, random_state=42))
        self.paths.reverse()
        second, _, _ = self.build()
        self.assertEqual(csv_text(first), csv_text(second))
        self.assertEqual(len(report["inputs"]), 2)

    def test_cli_writes_identical_outputs_and_preserves_raw_files(self):
        before = [sha256(p) for p in self.paths]
        self.assertEqual(self.run_cli(), 0)
        output = self.directory / "out"
        snapshots = {p.name: p.read_bytes() for p in output.iterdir()}
        self.assertEqual(len(snapshots), 4)
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(snapshots, {p.name: p.read_bytes() for p in output.iterdir()})
        self.assertEqual(before, [sha256(p) for p in self.paths])
        self.assertTrue(json.loads((output / "validation_report.json").read_text())["dataset_published"])

    def test_failure_writes_report_and_keeps_previous_dataset_unchanged(self):
        self.assertEqual(self.run_cli(), 0)
        dataset = self.directory / "out/daily_temperatures.csv"
        before = dataset.read_bytes()
        self.mutate(0, lambda df: pd.concat([df, df.iloc[[0]]]))
        self.assertEqual(self.run_cli(), 1)
        self.assertEqual(before, dataset.read_bytes())
        report = json.loads((self.directory / "out/validation_report.json").read_text())
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["dataset_published"])
        self.assertIn("tmax.duplicate_key", [item["code"] for item in report["errors"]])

    def test_first_failure_does_not_publish_a_dataset(self):
        self.mutate(0, lambda df: df.drop(columns=["lat"]))
        self.assertEqual(self.run_cli(), 1)
        self.assertFalse((self.directory / "out/daily_temperatures.csv").exists())

    def test_audit_writes_nothing(self):
        self.assertEqual(self.run_cli("--audit-only"), 0)
        self.assertFalse((self.directory / "out").exists())

    def test_output_cannot_overwrite_raw_directory_or_input(self):
        self.assertEqual(self.run_cli("--output-dir", str(ROOT / "data/raw")), 2)
        renamed = self.directory / "daily_temperatures.csv"
        self.paths[0].rename(renamed)
        self.paths[0] = renamed
        before = renamed.read_bytes()
        self.assertEqual(self.run_cli("--output-dir", str(self.directory)), 2)
        self.assertEqual(before, renamed.read_bytes())

    def test_cli_from_another_working_directory(self):
        result = subprocess.run([sys.executable, str(ROOT / "src/prepare_data.py"),
                                 *[str(p) for p in self.paths], "--cities", str(self.city_path),
                                 "--config", str(self.config_path), "--output-dir", str(self.directory / "out")],
                                cwd=self.directory, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


RAW_PATHS = [ROOT / "data/raw/imdweb_B3KKauQB.csv", ROOT / "data/raw/imdweb_5PfvCU0D.csv"]


@unittest.skipUnless(all(p.exists() for p in RAW_PATHS), "Real raw CSVs are not present; synthetic tests still run.")
class RealDataAcceptanceTests(unittest.TestCase):
    def test_real_panel_gap_coverage_and_unmodified_temperature_values(self):
        before = [sha256(p) for p in RAW_PATHS]
        panel, coverage, report = build_panel(RAW_PATHS, ROOT / "config/cities.geojson", ROOT / "config/preparation.json")
        self.assertEqual(len(panel), 140256)
        self.assertEqual(report["merge"], {"both": 140255, "tmax_only": 0, "tmin_only": 0, "neither": 1})
        self.assertEqual(len(coverage), 16 * 24)
        gap = panel.loc[~panel.temperature_pair_complete]
        self.assertEqual(gap[["city", "date"]].to_dict("records"), [{"city": "Guwahati", "date": "2005-06-26"}])
        self.assertEqual(int(coverage.missing_tmax_values.sum()), 1)
        for var, path in zip(("tmax", "tmin"), RAW_PATHS):
            raw = pd.read_csv(path, float_precision="round_trip").rename(columns={"time": "date"})
            matched = raw.merge(panel, on=["point_id", "date"], validate="one_to_one", suffixes=("_raw", "_clean"))
            self.assertEqual(len(matched), len(raw))
            self.assertTrue((matched[var + "_raw"] == matched[var + "_clean"]).all())
        self.assertEqual(before, [sha256(p) for p in RAW_PATHS])
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
