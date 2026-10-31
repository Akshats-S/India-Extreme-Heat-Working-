# Descriptive analysis and reproducibility

Run the entire project with `python src/run_project.py` after installing
`requirements.txt`. This first prepares/validates the data and heat metrics,
then runs `src/analyze_data.py`. `--preliminary` runs only temperature
preparation. Neither command submits files or edits the original inputs.

Analysis refuses a failed preparation report, a changed heat configuration,
or prepared CSVs whose fingerprints no longer match their validation report.
It requires eligible paired city-years and early/late periods for the stated
comparisons. Rerun preparation after any relevant input change.

## Outputs

`outputs/analysis/` contains:

- `city_temperature_summary.csv`: 16 city rows with observed/missing counts,
  paired counts and Tmax/Tmin means, standard deviations, minima, P10, medians,
  P90 and maxima (degrees Celsius). Standard deviations use ddof=1.
- `equal_city_annual_mean.csv`: 24 years with the arithmetic mean of eligible
  city paired-day/night percentages. These are equal-city, not population-
  weighted or all-India estimates.
- `sensitivity_annual.csv`: 384 city-years x four specifications = 1,536 rows.
- `sensitivity_period_comparison.csv`: 16 cities x four specifications = 64 rows.
- `sensitivity_summary.csv`: four specification summaries, including average
  day/night changes and counts of positive/negative comparison gaps.
- `city_sensitivity.csv`: 16 city comparison ranges and sign-agreement checks.
- `results-note.md`: prose and tables generated from the actual computed results.
- `analysis_report.json`: specifications, key totals, software and output hashes.

`outputs/figures/` contains five PNG figures: annual frequencies by city,
early/late changes, sensitivity comparisons, the equal-city annual mean and
temperature boxplots. Axes, sources, units/periods and key caveats are labeled.
The city panels share a range that contains all plotted peaks. Boxplot outlier
markers are hidden only for legibility; no observation is deleted from data or
calculations. Figures use a noninteractive backend and bundled DejaVu fonts.

## Specifications

The primary P90/2001-2024/five-day method is unchanged. Sensitivity runs use
P95, a 2001-2010 reference, and a 15-day window, changing one element at a time.
They fit from original temperature columns and do not overwrite the primary
dataset. The earlier-reference variant has an in-/out-reference boundary and
no bootstrap correction: treat it as a diagnostic with sampling limitations.
Sign agreement across four scenarios is not a confidence level, significance
test or proof that all reasonable methods would agree.

All frequency changes are percentage-point differences between pooled paired
date frequencies in 2001-2005 and 2020-2024. Annual curves use each year's
paired denominator. The sign of the night-minus-day comparison can be positive
even if both frequencies fell. The results note explains this distinction.

The conclusions are descriptive, conditional on the definitions, selected
grid points and available years. Source-network changes, the unverified
clock-time convention, retrospective thresholds and spatial scale remain
limitations. No causal policy, mortality, demand or welfare effect is estimated.

## Packages

`python src/build_packages.py` builds preliminary/final ZIPs under the sibling
`Submissions` directory. It copies an explicit source/documentation whitelist,
regenerates outputs twice in a fresh staging folder, runs the complete tests,
checks raw-file preservation, builds and extracts each ZIP, and verifies exact
regeneration from the extracted copy. Manifests verify every included file.
Compiled caches, Git history, credentials and assistant instruction files are
excluded. Existing source files and the older preliminary ZIP are preserved.

Use `--verify-python PATH` to verify with another Python environment that has
the pinned requirements installed. A fresh isolated environment was used for
the final package verification; execution evidence is in the verification log.
Team/course metadata is stored in `config/submission.json`. After source or
documentation corrections, rebuild the ZIPs and refresh the matching folders
in the submission repository. The builder creates local packages; course
submission uses the course's specified channel.
