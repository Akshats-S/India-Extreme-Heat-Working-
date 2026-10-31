# Verification log

The handout asks every group member to verify each step of the code, because AI tools can make mistakes. Record each check here. A step is only "verified" once a **person** has read the code and checked its output; an assistant's own check does not count as human verification.

| Step / script | What was checked | How | Verified by | Date |
|---|---|---|---|---|
| `src/audit_raw_data.py` | Output matches an independent pandas check (row counts 140,255 per file, 16 points, no empty cells, no duplicate keys, one missing location-date: point 14 on 2005-06-26, files match on keys) | AI assistant ran both and compared | _human verification pending_ | |
| `config/cities.geojson` | 16 city points match the point coordinates in both CSVs, in point_id order | AI assistant compared programmatically | _human verification pending_ | |
| `src/prepare_data.py`, audit wrapper and `tests/test_prepare_data.py` | Strict parsing, full-calendar merge, missingness, coordinate/grid consistency, error exit statuses, optional bounds, precision, reproducibility and raw-file preservation | Automated checks described below | _human verification pending_ | 2026-10-31 |

## Automated checks executed on 2026-10-31

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
- Human verification, authoritative metadata confirmation, scientific review
  of the exported grid assignment, extreme-heat definitions and final
  submission data-sharing/access arrangements remain pending.
