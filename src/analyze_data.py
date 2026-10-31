# Creates summary tables and figures from the prepared data.
"""Descriptive summaries, sensitivity checks, figures and a computed results note."""

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from heat_metrics import build_heat_outputs, load_heat_settings
from prepare_data import ROOT, OUTPUT_COLUMNS, atomic_text, csv_text, sha256

DAY_COLOR, NIGHT_COLOR = "#c65b21", "#186ca0"
SCENARIO_LABELS = {"primary_p90": "P90 / 2001-2024 / 5 days", "p95": "P95 / 2001-2024 / 5 days",
                   "early_reference": "P90 / 2001-2010 / 5 days*", "wide_window": "P90 / 2001-2024 / 15 days"}
FIGURE_NAMES = ["annual_city_frequencies.png", "period_frequency_changes.png", "sensitivity_comparison.png",
                "equal_city_mean_frequencies.png", "temperature_distributions.png"]


def read_validated_inputs(data_dir, heat_config):
    report = json.loads((data_dir / "validation_report.json").read_text())
    if report.get("errors") or not report.get("dataset_published") or "heat_metrics" not in report:
        raise ValueError("Analysis requires a successful heat-preparation report.")
    if sha256(heat_config) != report["heat_config_sha256"]:
        raise ValueError("Heat settings changed; rerun preparation before analysis.")
    for name, expected in report["output"]["files_sha256"].items():
        if sha256(data_dir / name) != expected:
            raise ValueError("Prepared file changed after validation: " + name)
    daily = pd.read_csv(data_dir / "daily_temperatures.csv", float_precision="round_trip",
                        dtype={col: "boolean" for col in ("extreme_day", "extreme_night", "compound_extreme")})
    annual = pd.read_csv(data_dir / "city_year_heat.csv", float_precision="round_trip")
    comparison = pd.read_csv(data_dir / "city_period_comparison.csv", float_precision="round_trip")
    if not annual.paired_year_eligible.all() or not (comparison.early_eligible & comparison.late_eligible).all():
        raise ValueError("This descriptive report requires eligible paired city-years/periods; inspect coverage first.")
    return daily, annual, comparison, report


def summarize_temperatures(daily):
    rows = []
    for (pid, city), group in daily.groupby(["point_id", "city"], sort=True):
        row = {"point_id": int(pid), "city": city, "expected_days": len(group),
               "paired_days": int((group.tmax.notna() & group.tmin.notna()).sum())}
        for var in ("tmax", "tmin"):
            values = group[var].dropna()
            row[var + "_observed_days"] = len(values)
            row[var + "_missing_days"] = int(group[var].isna().sum())
            for name, value in (("mean_c", values.mean()), ("std_c", values.std(ddof=1)),
                                ("min_c", values.min()), ("p10_c", values.quantile(0.1)),
                                ("median_c", values.median()), ("p90_c", values.quantile(0.9)), ("max_c", values.max())):
                row[var + "_" + name] = float(value)
        rows.append(row)
    return pd.DataFrame(rows)


def sensitivity_tables(daily, annual, comparison, settings):
    """Keep primary outputs unchanged; fit alternatives from original columns."""
    if (settings["baseline_start_year"], settings["baseline_end_year"], settings["percentile"], settings["window_days"]) != (2001, 2024, 90, 5):
        raise ValueError("The current report scenarios require the documented primary 2001-2024/P90/5-day method.")
    configurations = {
        "primary_p90": dict(settings), "p95": {**settings, "percentile": 95},
        "early_reference": {**settings, "baseline_end_year": 2010},
        "wide_window": {**settings, "window_days": 15},
    }
    annual_tables, period_tables, summaries = [], [], []
    panel = daily[OUTPUT_COLUMNS].copy()
    for scenario, configuration in configurations.items():
        if scenario == "primary_p90":
            yearly, period = annual.copy(), comparison.copy()
        else:
            _, _, yearly, period, _ = build_heat_outputs(panel, configuration)
        annual_tables.append(yearly.assign(scenario=scenario))
        period_tables.append(period.assign(scenario=scenario))
        summaries.append({"scenario": scenario, "cities": len(period),
                          "mean_day_change_pp": float(period.day_change_pp.mean()),
                          "mean_night_change_pp": float(period.night_change_pp.mean()),
                          "mean_night_minus_day_change_pp": float(period.night_minus_day_change_pp.mean()),
                          "positive_gap_cities": int((period.night_minus_day_change_pp > 1e-12).sum()),
                          "negative_gap_cities": int((period.night_minus_day_change_pp < -1e-12).sum()),
                          "all_periods_eligible": bool((period.early_eligible & period.late_eligible).all()),
                          "reference_boundary_caveat": scenario == "early_reference"})
    periods = pd.concat(period_tables, ignore_index=True)
    robustness = []
    for (pid, city), group in periods.groupby(["point_id", "city"], sort=True):
        values = group.night_minus_day_change_pp
        signs = np.where(values > 1e-12, 1, np.where(values < -1e-12, -1, 0))
        robustness.append({"point_id": int(pid), "city": city,
                           "primary_night_minus_day_change_pp": float(group.loc[group.scenario == "primary_p90", "night_minus_day_change_pp"].iloc[0]),
                           "minimum_gap_pp": float(values.min()), "maximum_gap_pp": float(values.max()),
                           "positive_scenarios": int((signs > 0).sum()), "negative_scenarios": int((signs < 0).sum()),
                           "sign_agrees_all_scenarios": bool(len(set(signs.tolist())) == 1)})
    return pd.concat(annual_tables, ignore_index=True), periods, pd.DataFrame(summaries), pd.DataFrame(robustness), configurations


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines += ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join(lines)


def results_note(daily, comparison, sensitivity, robustness):
    positive = int((comparison.night_minus_day_change_pp > 1e-12).sum())
    stable = int(robustness.sign_agrees_all_scenarios.sum())
    high = comparison.loc[comparison.night_minus_day_change_pp.idxmax()]
    low = comparison.loc[comparison.night_minus_day_change_pp.idxmin()]
    table = markdown_table(["City", "Day change (pp)", "Night change (pp)", "Night minus day change (pp)"],
                           [[row.city, f"{row.day_change_pp:.2f}", f"{row.night_change_pp:.2f}", f"{row.night_minus_day_change_pp:.2f}"] for row in comparison.itertuples()])
    checks = markdown_table(["Variant", "Mean day change (pp)", "Mean night change (pp)", "Positive-gap cities"],
                            [[SCENARIO_LABELS[row.scenario], f"{row.mean_day_change_pp:.2f}", f"{row.mean_night_change_pp:.2f}", row.positive_gap_cities] for row in sensitivity.itertuples()])
    return f'''# Descriptive results and sensitivity checks

This note is generated by `src/analyze_data.py` from the validated real data.
It describes 16 selected city-associated IMD grid points, 2001-2024. These are
project-relative warm-day/night indicators, not official heatwave warnings.

## Primary comparison

The fixed seasonal P90 method compares 2001-2005 with 2020-2024. Frequencies
use paired observed dates; missing temperatures are not counted as non-events.
The panel has {len(daily):,} rows and {int(daily.temperature_pair_complete.sum()):,}
complete temperature pairs. Guwahati, 2005-06-26 remains blank and flagged.

Across the 16 cities, the equal-city mean daytime frequency change is
**{comparison.day_change_pp.mean():.2f} percentage points**, and the nighttime
change is **{comparison.night_change_pp.mean():.2f} percentage points**. The mean
night-minus-day change is **{comparison.night_minus_day_change_pp.mean():.2f} pp**.
These averages give each selected city equal weight; they are not population-
weighted or representative estimates for all India.

The night-minus-day change is positive for **{positive} of {len(comparison)} cities**.
A positive gap means the nighttime frequency increased more, or decreased less,
than the daytime frequency. It does not mean that both frequencies increased.
The largest gap is {high.city} ({high.night_minus_day_change_pp:.2f} pp), and the
smallest is {low.city} ({low.night_minus_day_change_pp:.2f} pp).

{table}

One percentage point is an absolute change in a percentage: 10% to 15% is +5 pp.
The period percentages pool events and paired observed dates; annual plots use
each year's own paired denominator.

## Sensitivity

{checks}

The sign of each city's night-minus-day change agrees across all four variants
for **{stable} of {len(robustness)} cities**. Inspect `city_sensitivity.csv` and
[the sensitivity figure](../figures/sensitivity_comparison.png) for exceptions.
This is a limited specification check, not a confidence interval or a test of
statistical significance. Alternative definitions can change city rankings and
the magnitude or sign of a comparison.

*The early-reference variant is an unbootstrapped diagnostic. Its early period
is inside its reference and its late period is outside, so reference-boundary
sampling effects may contaminate that comparison. It is not an official
ETCCDI index, nor an independent confirmation of the primary result.

## Read the figures

- [Annual frequencies for each city](../figures/annual_city_frequencies.png): paired warm-day/night percentages.
- [Early-to-late changes](../figures/period_frequency_changes.png): daytime and nighttime changes in pp.
- [Sensitivity across definitions](../figures/sensitivity_comparison.png): night-minus-day change under four variants.
- [Equal-city annual mean](../figures/equal_city_mean_frequencies.png): arithmetic mean of the selected city percentages.
- [Temperature distributions](../figures/temperature_distributions.png): Tmax/Tmin in Celsius; plotting outliers is suppressed for legibility, but no data are removed.

## Interpretation limits

The [IMD product documentation](https://www.imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html)
notes fewer stations from 2008 onward. Network changes can affect the series;
these descriptive differences do not isolate a climate-only or policy effect.
One-degree interpolated grid estimates do not identify urban heat islands or
conditions within a particular neighborhood. Celsius comes from product
provenance; the export's exact clock-time alignment is unverified, so Tmin is
a nighttime proxy and source dates are not shifted.

The retrospective 24-year reference uses the same sample being described.
Whole-sample tail frequencies are partly constrained by construction and are
not independent evidence that one type of heat is more severe. The five-day
seasonal windows, leap-day interpolation and no-bootstrap adaptation are
documented in the methodology. Percentile warmth is not an absolute health-
risk threshold. This dataset alone does not measure health damage, electricity
use, adaptation costs, welfare benefits or causal treatment effects.
'''


def save_figure(fig, directory, name, caption):
    directory.mkdir(parents=True, exist_ok=True)
    fig.text(0.5, 0.012, caption, ha="center", va="bottom", fontsize=8, color="#444444")
    handle, temporary = tempfile.mkstemp(dir=directory, suffix=".png")
    os.close(handle)
    try:
        fig.savefig(temporary, dpi=160, format="png", facecolor="white", metadata={"Software": "matplotlib " + matplotlib.__version__})
        os.replace(temporary, directory / name)
    finally:
        plt.close(fig)
        if os.path.exists(temporary):
            os.unlink(temporary)


def make_figures(daily, annual, comparison, sensitivity_periods, mean_annual, directory):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titleweight": "bold", "axes.labelcolor": "#333333"})
    caption = "Source: IMD via IMDWeb | 2001-2024 | Fixed city/calendar-day P90, 5-day windows | Paired observed dates; Tmin is a nighttime proxy"
    city_order = daily[["point_id", "city"]].drop_duplicates().sort_values("point_id")
    fig, axes = plt.subplots(4, 4, figsize=(14, 11), sharex=True, sharey=True)
    handles = None
    for ax, row in zip(axes.flat, city_order.itertuples()):
        part = annual.loc[annual.point_id == row.point_id]
        day, = ax.plot(part.year, part.paired_extreme_day_pct, color=DAY_COLOR, lw=1.6, label="Warm days (Tmax)")
        night, = ax.plot(part.year, part.paired_extreme_night_pct, color=NIGHT_COLOR, lw=1.6, label="Warm nights (Tmin)")
        handles = [day, night]
        ax.set_title(row.city, fontsize=10)
        ax.set_xticks([2001, 2010, 2020, 2024])
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", color="#dddddd", lw=0.6)
    highest = float(annual[["paired_extreme_day_pct", "paired_extreme_night_pct"]].max().max())
    axes.flat[0].set_ylim(0, min(100, max(5, math.ceil(highest / 5) * 5 + 5)))
    for ax in list(axes.flat)[len(city_order):]:
        ax.set_visible(False)
    fig.suptitle("Seasonally unusual warmth across the 16 city grid points", fontsize=17, y=0.98)
    fig.legend(handles, [h.get_label() for h in handles], loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.951), frameon=False)
    fig.supylabel("Share of paired observed dates (%)", x=0.015)
    fig.supxlabel("Year", y=0.035)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.895, bottom=0.10, hspace=0.4, wspace=0.14)
    save_figure(fig, directory, FIGURE_NAMES[0], caption)

    ordered = comparison.sort_values("night_minus_day_change_pp")
    y = np.arange(len(ordered))
    fig, ax = plt.subplots(figsize=(10.5, 8))
    ax.hlines(y, ordered.day_change_pp, ordered.night_change_pp, color="#bbbbbb", lw=2)
    ax.scatter(ordered.day_change_pp, y, color=DAY_COLOR, s=42, label="Daytime change", zorder=3)
    ax.scatter(ordered.night_change_pp, y, color=NIGHT_COLOR, s=42, label="Nighttime change", zorder=3)
    ax.set_yticks(y, ordered.city)
    ax.axvline(0, color="#555555", lw=0.9)
    ax.grid(axis="x", color="#e5e5e5")
    ax.set_xlabel("2020-2024 frequency minus 2001-2005 frequency (percentage points)")
    ax.set_title("How warm-day and warm-night frequencies changed", pad=34, fontsize=15)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=2, frameon=False)
    fig.subplots_adjust(left=0.18, right=0.97, top=0.87, bottom=0.12)
    save_figure(fig, directory, FIGURE_NAMES[1], caption)

    fig, ax = plt.subplots(figsize=(11.5, 8))
    colors = ["#222222", "#8c55a2", "#309d77", "#d08b21"]
    for index, (scenario, label) in enumerate(SCENARIO_LABELS.items()):
        values = sensitivity_periods.loc[sensitivity_periods.scenario == scenario].set_index("city").loc[ordered.city]
        ax.scatter(values.night_minus_day_change_pp, y + (index - 1.5) * 0.13, s=30, color=colors[index], label=label, zorder=3)
    ax.set_yticks(y, ordered.city)
    ax.axvline(0, color="#555555", lw=0.9)
    ax.grid(axis="x", color="#e5e5e5")
    ax.set_xlabel("Nighttime change minus daytime change (percentage points)")
    ax.set_title("Sensitivity of the day-versus-night comparison", fontsize=15, pad=57)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=False, fontsize=9)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.80, bottom=0.12)
    save_figure(fig, directory, FIGURE_NAMES[2], "Source: IMD via IMDWeb | Early 2001-2005 vs late 2020-2024 | *Earlier reference is an unbootstrapped diagnostic with a reference-boundary caveat")

    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    ax.plot(mean_annual.year, mean_annual.mean_day_pct, color=DAY_COLOR, lw=2, label="Warm days (Tmax)")
    ax.plot(mean_annual.year, mean_annual.mean_night_pct, color=NIGHT_COLOR, lw=2, label="Warm nights (Tmin)")
    ax.axvline(2008, color="#999999", lw=1, ls="--", label="IMD network change from 2008")
    ax.set(xlabel="Year", ylabel="Equal-city mean frequency (%)", title="Annual warmth: equal weight for each selected city")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#dddddd")
    ax.legend(frameon=False, fontsize=9)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.17)
    save_figure(fig, directory, FIGURE_NAMES[3], caption + "\nNot population weighted; the network marker is a limitation, not an estimated cause.")

    fig, ax = plt.subplots(figsize=(13, 6.5))
    positions = np.arange(len(city_order)) * 2.5
    for var, color, offset in (("tmax", DAY_COLOR, -0.4), ("tmin", NIGHT_COLOR, 0.4)):
        groups = [daily.loc[daily.point_id == pid, var].dropna().to_numpy() for pid in city_order.point_id]
        box = ax.boxplot(groups, positions=positions + offset, widths=0.65, showfliers=False,
                         patch_artist=True, manage_ticks=False, orientation="vertical")
        for patch in box["boxes"]:
            patch.set(facecolor=color, alpha=0.7)
        for median in box["medians"]:
            median.set(color="#222222")
        ax.plot([], [], color=color, lw=7, label=var.upper())
    ax.set_xticks(positions, city_order.city, rotation=40, ha="right", fontsize=9)
    ax.set(ylabel="Daily temperature (degrees Celsius)", title="Temperature distributions at the selected grid points, 2001-2024")
    ax.grid(axis="y", color="#dddddd")
    ax.legend(frameon=False, ncol=2)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.9, bottom=0.23)
    save_figure(fig, directory, FIGURE_NAMES[4], "Source: IMD via IMDWeb | Boxes: quartiles/median; whiskers: 1.5 IQR | Outlier markers hidden for legibility; all source values retained")


def run_analysis(data_dir, analysis_dir, figure_dir, heat_config):
    daily, annual, comparison, preparation = read_validated_inputs(data_dir, heat_config)
    settings = load_heat_settings(heat_config)
    yearly_sensitivity, period_sensitivity, sensitivity, robustness, configurations = sensitivity_tables(daily, annual, comparison, settings)
    temperature = summarize_temperatures(daily)
    mean_annual = annual.groupby("year", as_index=False).agg(cities=("city", "nunique"),
        mean_day_pct=("paired_extreme_day_pct", "mean"), mean_night_pct=("paired_extreme_night_pct", "mean"),
        mean_night_minus_day_pp=("night_minus_day_pp", "mean"))
    tables = {"city_temperature_summary.csv": temperature, "equal_city_annual_mean.csv": mean_annual,
              "sensitivity_annual.csv": yearly_sensitivity, "sensitivity_period_comparison.csv": period_sensitivity,
              "sensitivity_summary.csv": sensitivity, "city_sensitivity.csv": robustness}
    make_figures(daily, annual, comparison, period_sensitivity, mean_annual, figure_dir)
    for name, frame in tables.items():
        atomic_text(analysis_dir / name, csv_text(frame))
    atomic_text(analysis_dir / "results-note.md", results_note(daily, comparison, sensitivity, robustness))
    hashes = {name: sha256(analysis_dir / name) for name in [*tables, "results-note.md"]}
    hashes.update({"../figures/" + name: sha256(figure_dir / name) for name in FIGURE_NAMES})
    report = {"status": "passed", "primary_dataset_sha256": preparation["output"]["sha256"],
              "heat_config_sha256": sha256(heat_config), "scenarios": configurations,
              "figures": FIGURE_NAMES, "files_sha256": hashes,
              "primary_positive_gap_cities": int((comparison.night_minus_day_change_pp > 1e-12).sum()),
              "cities_with_sign_agreement_all_scenarios": int(robustness.sign_agrees_all_scenarios.sum()),
              "mean_day_change_pp": float(comparison.day_change_pp.mean()),
              "mean_night_change_pp": float(comparison.night_change_pp.mean()),
              "mean_night_minus_day_change_pp": float(comparison.night_minus_day_change_pp.mean()),
              "matplotlib_version": matplotlib.__version__}
    atomic_text(analysis_dir / "analysis_report.json", json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--analysis-dir", type=Path, default=ROOT / "outputs/analysis")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "outputs/figures")
    parser.add_argument("--heat-config", type=Path, default=ROOT / "config/heat_metrics.json")
    args = parser.parse_args(argv)
    raw = (ROOT / "data/raw").resolve()
    for target in (args.analysis_dir, args.figure_dir):
        resolved = target.resolve()
        if resolved == raw or raw in resolved.parents or resolved == args.data_dir.resolve():
            print("ERROR: analysis outputs must not overwrite raw/prepared inputs.", file=sys.stderr)
            return 2
    try:
        report = run_analysis(args.data_dir, args.analysis_dir, args.figure_dir, args.heat_config)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("Analysis failed: " + str(exc), file=sys.stderr)
        return 1
    print(f"Analysis passed: {len(report['figures'])} figures; four sensitivity variants; {report['primary_positive_gap_cities']} positive-gap cities under the primary definition.")
    print("Results: " + str((args.analysis_dir / "results-note.md").resolve()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
