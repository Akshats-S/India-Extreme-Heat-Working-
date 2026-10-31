# Verification record

Execution date: 31 October 2026. These are automated and output-inspection
records; no independent human sign-off is recorded.

## Data integrity

- Each original CSV has 140,255 rows. Keys are unique and agree between Tmax
  and Tmin. The sole absent pair is Guwahati, 2005-06-26.
- The full panel contains 140,256 city-days, 16 cities and 8,766 dates. The
  absent pair is retained with blank temperatures and explicit missing flags.
- Every exported Tmax/Tmin was compared with its source using round-trip
  floating-point parsing: zero numerical mismatches. Raw-file fingerprints
  remained unchanged. No imputation, rounding, clipping or outlier deletion.
- Coordinates agree with the 16-city GeoJSON. All 64 nearest-grid checks
  passed; there are no duplicate keys, cross-file grid disagreements or
  Tmin-above-Tmax records.

## Research outputs

- Final daily table: 21 columns. Thresholds: 5,856 rows. Annual summaries:
  384 rows. Period comparisons: 16 rows. Every city-year passes coverage rules.
- The absent temperature pair produces missing, not False, heat flags.
  Guwahati 2005 uses 364 paired dates.
- Daily event counts reconcile with annual summaries; period percentages
  independently reconcile with pooled paired events and denominators.
- Primary daily dataset SHA-256:
  `53af34914e1307f3784123b71f725c9be01ec3a4e2200ba5fcf9072da104f1a1`.
- Four specifications were executed: P90/full reference/five-day window,
  P95, a 2001-2010 reference and a 15-day window. Primary average changes are
  0.8743792731100013 pp for daytime and 5.335022741412352 pp for nighttime.
  Night-minus-day change is positive in 13 cities. Its sign agrees across all
  variants for 15 cities; Delhi changes sign under the earlier-reference diagnostic.
- All five figures were visually inspected for labels, legends, units and
  readable ranges. A regression test protects against clipping city peaks.

## Reproducibility

- Both assessment packages passed all **42 tests**, with warnings treated as
  errors, using an isolated Python 3.12.10 environment installed from the pinned
  requirements. The suite includes real-data acceptance and deliberately
  faulty inputs, percentile/leap/missingness calculations, aggregation,
  provenance, plot ranges, manifests and package source inclusion.
- Each package was generated twice in fresh staging; outputs matched byte
  for byte. The ZIP was extracted and its documented command regenerated the
  included outputs exactly. Original raw inputs stayed unchanged.
- `PACKAGE_CHECKS.json` records execution results in each package.
  `MANIFEST.json` fingerprints every included file. The outer
  `Submissions/package_build_report.json` fingerprints both ZIPs.
- Cleanup removed superseded plans and empty scaffolding. Rebuilt packages
  retain the same scientific-output fingerprints and include current documentation.
  Git attributes preserve packaged bytes in submission clones.

Scientific interpretation limits remain in the methodology and source metadata:
one-degree spatial scale, unverified export clock-time alignment, the post-2008
network change, retrospective reference and unbootstrapped sensitivity caveat.
