# Tests the analysis calculations and submission packages.
"""Known-answer descriptive aggregation, provenance and chart-range checks."""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analyze_data import (FIGURE_NAMES, SCENARIO_LABELS, make_figures, read_validated_inputs,
                          sensitivity_tables, summarize_temperatures)
from build_packages import copy_sources, extract_checked, verify_manifest, write_manifest
from heat_metrics import build_heat_outputs, load_heat_settings
from prepare_data import OUTPUT_COLUMNS, sha256


class AnalysisTests(unittest.TestCase):
    def test_temperature_summary_uses_observed_values_and_counts_missing(self):
        data = pd.DataFrame({"point_id": [0, 0, 0], "city": ["Synthetic"] * 3,
                             "tmax": [10.0, 20.0, np.nan], "tmin": [1.0, 3.0, 5.0]})
        row = summarize_temperatures(data).iloc[0]
        self.assertEqual(row.expected_days, 3)
        self.assertEqual(row.paired_days, 2)
        self.assertEqual(row.tmax_mean_c, 15)
        self.assertEqual(row.tmax_missing_days, 1)
        self.assertEqual(row.tmin_mean_c, 3)

    def test_sensitivity_known_constant_case_and_primary_inputs_unchanged(self):
        dates = pd.date_range("2001-01-01", "2024-12-31")
        panel = pd.DataFrame({"point_id": 0, "city": "Synthetic", "date": dates.strftime("%Y-%m-%d"),
                              "lat": 28.6, "lon": 77.2, "tmax_cell_lat": 28.5, "tmax_cell_lon": 77.5,
                              "tmin_cell_lat": 28.5, "tmin_cell_lon": 77.5,
                              "tmax": np.where(dates.year < 2020, 30.0, 40.0), "tmin": 20.0})
        for var in ("tmax", "tmin"):
            panel[var + "_record_missing"] = False
            panel[var + "_missing"] = False
        panel["temperature_pair_complete"] = True
        panel = panel[OUTPUT_COLUMNS]
        settings = load_heat_settings(ROOT / "config/heat_metrics.json")
        daily, _, annual, comparison, _ = build_heat_outputs(panel, settings)
        saved = daily.copy(deep=True)
        yearly, periods, summary, robustness, configs = sensitivity_tables(daily, annual, comparison, settings)
        self.assertEqual(len(yearly), 24 * 4)
        self.assertEqual(len(periods), 4)
        self.assertEqual(len(configs), 4)
        self.assertEqual(summary.loc[summary.scenario == "primary_p90", "mean_day_change_pp"].iloc[0], 0)
        self.assertEqual(summary.loc[summary.scenario == "early_reference", "mean_day_change_pp"].iloc[0], 100)
        self.assertFalse(robustness.sign_agrees_all_scenarios.iloc[0])
        self.assertEqual(robustness.negative_scenarios.iloc[0], 1)
        pd.testing.assert_frame_equal(daily, saved)

    def test_analysis_refuses_files_modified_after_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "heat.json"
            config.write_text("{}")
            pd.DataFrame({"extreme_day": [True], "extreme_night": [False], "compound_extreme": [False]}).to_csv(root / "daily_temperatures.csv", index=False)
            pd.DataFrame({"paired_year_eligible": [True]}).to_csv(root / "city_year_heat.csv", index=False)
            pd.DataFrame({"early_eligible": [True], "late_eligible": [True]}).to_csv(root / "city_period_comparison.csv", index=False)
            names = ["daily_temperatures.csv", "city_year_heat.csv", "city_period_comparison.csv"]
            report = {"errors": [], "dataset_published": True, "heat_metrics": {}, "heat_config_sha256": sha256(config),
                      "output": {"files_sha256": {name: sha256(root / name) for name in names}}}
            (root / "validation_report.json").write_text(json.dumps(report))
            self.assertEqual(len(read_validated_inputs(root, config)[0]), 1)
            (root / "city_year_heat.csv").write_text("paired_year_eligible\nFalse\n")
            with self.assertRaisesRegex(ValueError, "changed after validation"):
                read_validated_inputs(root, config)

    def test_shared_annual_chart_range_contains_every_city_peak(self):
        cities = ["Synthetic " + str(i) for i in range(16)]
        daily = pd.DataFrame([{"point_id": i, "city": city, "tmax": 30.0, "tmin": 20.0}
                              for i, city in enumerate(cities)])
        annual = pd.DataFrame([{"point_id": i, "city": city, "year": year,
                                "paired_extreme_day_pct": 2 if i == 0 else 80,
                                "paired_extreme_night_pct": 1}
                               for i, city in enumerate(cities) for year in (2001, 2024)])
        comparison = pd.DataFrame({"point_id": range(16), "city": cities, "day_change_pp": 0,
                                   "night_change_pp": 1, "night_minus_day_change_pp": 1})
        scenarios = pd.concat([comparison.assign(scenario=name) for name in SCENARIO_LABELS], ignore_index=True)
        means = pd.DataFrame({"year": [2001, 2024], "mean_day_pct": [10, 20], "mean_night_pct": [10, 30]})
        inspected = []
        def inspect(fig, directory, name, caption):
            if name == FIGURE_NAMES[0]:
                for ax in fig.axes:
                    for line in ax.lines:
                        if len(line.get_ydata()):
                            self.assertGreaterEqual(ax.get_ylim()[1], max(line.get_ydata()))
                inspected.append(name)
            plt.close(fig)
        with patch("analyze_data.save_figure", side_effect=inspect):
            make_figures(daily, annual, comparison, scenarios, means, Path("unused"))
        self.assertEqual(inspected, [FIGURE_NAMES[0]])

    def test_full_runner_stops_if_preparation_fails(self):
        from run_project import main
        with patch("run_project.prepare", return_value=1) as prepare, patch("analyze_data.main") as analysis:
            self.assertEqual(main([]), 1)
            prepare.assert_called_once()
            analysis.assert_not_called()


class PackageIntegrityTests(unittest.TestCase):
    @unittest.skipUnless(all((ROOT / "data/raw" / name).exists() for name in
                             ("imdweb_B3KKauQB.csv", "imdweb_5PfvCU0D.csv")), "Original inputs are unavailable.")
    def test_preliminary_runs_without_final_modules_or_development_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root, "preliminary")
            self.assertEqual([p.name for p in (root / "src").iterdir()], ["prepare_data.py"])
            for excluded in ("docs", "tests", "outputs", "COVER.md", "TOPIC_OUTLINE.md", "MANIFEST.json", "PACKAGE_CHECKS.json"):
                self.assertFalse((root / excluded).exists(), excluded)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("Research topic", readme)
            self.assertIn("python src/prepare_data.py --skip-heat", readme)
            result = subprocess.run([sys.executable, "-W", "error", "src/prepare_data.py", "--skip-heat"],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            daily = pd.read_csv(root / "data/processed/daily_temperatures.csv", float_precision="round_trip")
            self.assertEqual(daily.shape, (140256, 16))
            self.assertEqual(int(daily.temperature_pair_complete.sum()), 140255)

    def test_package_includes_city_mapping_and_sources_needed_to_rebuild(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root, "final")
            for name in ("config/cities.geojson", "config/heat_metrics.json", "config/source_metadata.json",
                         "src/run_project.py", "docs/topic-outline.md", "docs/package-templates/README-final.txt",
                         "TOPIC_OUTLINE.md", "RESEARCH_QUESTIONS.md", "README.md"):
                self.assertTrue((root / name).is_file(), name)

    def test_manifest_detects_altered_or_extra_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data.csv").write_text("synthetic,value\n0,1\n")
            write_manifest(root)
            self.assertEqual(verify_manifest(root), 1)
            (root / "data.csv").write_text("synthetic,value\n0,2\n")
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                verify_manifest(root)
            write_manifest(root)
            (root / "extra.txt").write_text("unexpected")
            with self.assertRaisesRegex(ValueError, "file list"):
                verify_manifest(root)

    def test_archive_extraction_rejects_path_escape(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "synthetic.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("../escape.txt", "synthetic")
            with self.assertRaisesRegex(ValueError, "escapes"):
                extract_checked(archive, root / "extract")
            self.assertFalse((root / "escape.txt").exists())


if __name__ == "__main__":
    unittest.main()
