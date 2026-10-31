# Verification log

The handout asks every group member to verify each step of the code, because AI tools can make mistakes. Record each check here. A step is only "verified" once a **person** has read the code and checked its output; an assistant's own check does not count as human verification.

| Step / script | What was checked | How | Verified by | Date |
|---|---|---|---|---|
| `src/audit_raw_data.py` | Output matches an independent pandas check (row counts 140,255 per file, 16 points, no empty cells, no duplicate keys, one missing location-date: point 14 on 2005-06-26, files match on keys) | AI assistant ran both and compared | _human verification pending_ | |
| `config/cities.geojson` | 16 city points match the point coordinates in both CSVs, in point_id order | AI assistant compared programmatically | _human verification pending_ | |
| `src/prepare_data.py`, audit wrapper and `tests/test_prepare_data.py` | Strict parsing, full-calendar merge, missingness, coordinate/grid consistency, error exit statuses, optional bounds, precision, reproducibility and raw-file preservation | Automated checks described below | _human verification pending_ | 2026-10-31 |

## Preliminary-stage automated checks executed on 2026-10-31

Workflow clarification received later on 2026-10-31: the technical lead confirms
there is no separate teammate approval requirement for the lead's own work.
Earlier human-verification-pending labels record the absence of a human check;
they do not impose an external-review gate. Topic registration/finalization and
the project's data-sharing issue are confirmed resolved by the lead.

These are execution records, not human sign-off. A teammate must still read the
code and verify the outputs before submission.

- `python -W error -m unittest discover -s tests -v`: **20 tests passed**, none
  skipped, including the real-data acceptance test. Warnings were treated as
  errors. Tests include synthetic leap-day coverage, matched and one-sided
  gaps, an entirely missing city, invalid schemas/CSV widths, dates, IDs,
  duplicates, missing/nonfinite/nonnumeric values, coordinate/grid problems,
  Tmin above Tmax, explicit plausibility bounds, faulty settings, output-path
  protection, failure reports, read-only auditing and repeated execution.
- `python src/prepare_data.py`: completed on the actual raw CSVs. Output:
  **140,256 rows, 16 cities, 8,766 dates, 140,255 complete temperature pairs**.
  The sole absent key is Guwahati (point_id 14), 2005-06-26, in both files.
  It remains in the output with blank temperatures/grid metadata and flags.
  Coverage contains 384 city-year rows. No source-key duplicates, unmatched
  records, coordinate/grid mismatches or Tmin-above-Tmax observations.
- Status is `passed_with_warnings`: two permitted source-record gaps and
  unresolved units/observation windows/physical plausibility bounds. The
  configured absent-record whitelist is explicit; unexpected gaps fail.
- Exact floating-point comparison uses `float_precision="round_trip"` when
  reloading source/output CSVs. A regression test protects against last-digit
  precision loss from fast default numeric parsers. No temperature rounding,
  filling, unit conversion or outlier deletion is performed.
- A fresh local Git clone with the pending implementation changes applied ran
  preparation twice from outside the checkout. **All four output files were
  byte-identical between runs**; the read-only audit changed no output. The
  original raw-file SHA-256 fingerprints were unchanged in both checkouts.
  Every one of the 140,255 Tmax values and 140,255 Tmin values matched the
  exported CSV exactly using round-trip parsing (zero mismatches). The fresh
  clone's daily CSV also matched the working copy. Dataset SHA-256:
  `8bbebb09eceaf59bd6655373b43d66ec07c8284e4dc2c3a11341276dc958ede8`.
- `git diff --check` and compilation of both source scripts and the test module
  passed. All four generated outputs are excluded by the existing `.gitignore`;
  the raw files have no changes in the Git diff.
- Dependencies in `requirements.txt` match the installed versions. Tested with
  Python 3.12.10, pandas 3.0.5 and numpy 2.4.4. No new isolated environment was
  installed; this is not a claim to have tested every Python/platform version.
- At this preliminary snapshot, metadata, scientific measurement choices and
  final data-access arrangements were pending. Later project confirmations
  and phase 1/2 results below supersede that status; the execution record above
  remains a record of the earlier temperature-only implementation.

## Phase 1/2 checks executed on 2026-10-31

- Source evidence checked: IMD maximum/minimum product pages and the cited
  product paper; ETCCDI definitions; NumPy quantile documentation; climdex.pcic
  defaults/source. Sources and their limits are recorded in
  `docs/source-metadata.md` and `docs/methodology.md`.
- `python -W error -m unittest discover -s tests -v`: **34 tests passed**, none
  skipped. The final pass ran from a fresh local clone with implementation
  changes applied, with warnings treated as errors. The suite includes the
  20 preparation tests plus 14 heat/real-data checks: a hand-calculated type-8
  quantile, strict exceedance ties, circular seasonal windows, city separation,
  reference-period isolation, February 29 exclusion/interpolation, nullable
  flags, paired denominators, annual/monthly quality suppression, partial
  calendars, insufficient reference coverage, invalid configs, documented IMD
  sentinel/grid checks, deterministic CLI output and real-data reconciliation.
- The default preparation command produced **140,256 daily rows with 21
  columns**, **5,856 thresholds**, **384 city-years**, **16 period comparisons**,
  coverage and JSON/text reports. Actual event totals: 13,756 warm-day flags,
  13,738 warm-night flags and 4,032 same-source-date co-exceedances. These are
  output-validation counts, not a standalone scientific finding.
- The sole missing temperature pair, Guwahati 2005-06-26, has missing (not
  False) day/night/compound indicators. Guwahati 2005 uses 364 paired observed
  dates. All 384 city-years pass the configured coverage rules.
- Source-contract validation passed **64 nearest-grid coordinate checks**
  (16 cities x 2 variables x 2 coordinate axes), with zero mismatches.
- A fresh clone with the changes applied ran the command twice from outside
  the repository. **All seven output files were byte-identical between runs.**
  The audit wrote nothing, and `--skip-heat` still generated the original four
  preliminary files into a separate output directory.
- Every exported Tmax/Tmin was compared with the original CSVs using
  round-trip parsing: no numerical changes. Exported annual event counts were
  independently reconciled against the exported daily flags, and every city's
  early/late percentages were independently recomputed using paired dates.
  Original raw-file fingerprints stayed unchanged in both working copies.
- Extended daily dataset SHA-256:
  `53af34914e1307f3784123b71f725c9be01ec3a4e2200ba5fcf9072da104f1a1`.
- Compilation and `git diff --check` passed. Generated data/report files remain
  git-ignored. Environment: Python 3.12.10, pandas 3.0.5, NumPy 2.4.4; existing
  pinned requirements are sufficient. No new isolated environment was created.
- The technical lead authorized completing phases 1/2 and does not require
  separate teammate approval. No independent human sign-off is invented.
  Exact export clock-time alignment, the post-2008 station-network change,
  regional spatial representation and the retrospective 24-year reference
  remain disclosed interpretation limitations. Figures, sensitivity analysis,
  economics questions and final packaging remain phases 3-5.

## Phase 3-5 checks executed on 2026-10-31

- `python src/run_project.py` completed on the real sources: the seven
  preparation files, six analysis CSVs, computed results note, analysis report
  and five PNG figures were generated. The primary dataset and source values
  remain unchanged from phase 2.
- Four specifications were executed: primary P90/full reference/five-day
  window, P95, P90 with 2001-2010 reference and P90 with a 15-day window.
  Actual primary mean changes across the selected cities: daytime
  0.8743792731100013 pp, nighttime 5.335022741412352 pp; night-minus-day change
  is positive in 13 cities. Signs agree across all four variants for 15 cities;
  Delhi changes sign in the earlier-reference diagnostic. The generated note
  retains sampling/network/spatial/proxy limitations and no causal claim.
- All five figures were visually inspected. A clipped common annual-panel
  range found during QA was fixed; the range now contains every city peak.
  A regression test protects that condition. Final figures have readable
  labels, units, periods, legends and sources. No source observation was
  deleted to simplify a plot.
- Three completed economics applications and the topic outline specify policy
  relevance, course technique and additional data/identification requirements.
  Submission README templates list every preparation/analysis step in order.
- A new Python 3.12.10 virtual environment was created and all pinned packages
  installed from `requirements.txt`; `pip check` reported no broken requirements.
- `src/build_packages.py` built both dated ZIPs using that isolated Python.
  **42 tests passed in each package** with warnings treated as errors, including
  real-data acceptance. The earlier workspace run had 41 tests; one additional
  package-whitelist test was added after fresh staging caught an omitted
  GeoJSON file. That omission was fixed before the packages were delivered.
- Each package's outputs were regenerated twice in fresh staging and matched
  byte-for-byte. Each ZIP was extracted and the documented command regenerated
  the included outputs exactly. Raw-file fingerprints were unchanged. Final
  check/manifest records were verified in the final archives; compiled caches,
  Git history, credentials and assistant instructions are excluded.
- The preliminary package contains 43 files and four generated temperature
  artifacts; the final contains 60 files and 20 generated data/analysis/figure
  artifacts. `PACKAGE_CHECKS.json` and `MANIFEST.json` provide the per-package
  evidence; the sibling `Submissions/package_build_report.json` fingerprints
  the ZIPs. The final named packages were rebuilt using the same isolated
  environment and the full verification sequence.
- The technical lead supplied the names Akshat Srivastava, Krishna Reddy
  and Jatin Shetty. Both covers and submission metadata include those names.
  Section/IDs were not supplied and are only needed if the portal requires
  them. No assessment was uploaded, no private submission repository was
  changed, and no independent human verification is claimed.
