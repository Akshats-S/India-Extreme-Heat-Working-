# Your review and submission guide

This guide is for your own review as technical lead. It does not impose a new
teammate-approval gate. The packages are prepared locally; no assessment has
been uploaded and the private submission repository has not been changed.

## What has been built

Original IMD Tmax/Tmin CSVs and the 16-city GeoJSON were checked against each
other. The code validates structure, dates, IDs, duplicates, values, coordinates,
known gaps and Tmin <= Tmax; joins the temperatures; and retains every expected
city-day. Source temperatures retain full precision. The complete panel has
140,256 rows, including one missing pair: Guwahati, 2005-06-26.

The final workflow adds source/grid provenance checks, fixed seasonal percentile
thresholds, nullable heat flags, annual frequencies, early/late comparisons,
four measurement variants, five figures, computed descriptive results and
three candidate economics applications. Code, configuration, dependencies,
documentation and both submission packages are reproducible and fingerprinted.

## Review in this order

1. **Identity and assignment fit.** Extract the relevant ZIP. Check COVER.md
   and README.md. Confirm the supplied names: Akshat Srivastava, Krishna Reddy
   and Jatin Shetty. Add section/IDs only if your submission system
   requires them. Topic registration and project data sharing are resolved.
2. **Topic and economics.** Read TOPIC_OUTLINE.md. For the final package, read
   RESEARCH_QUESTIONS.md and check that you can explain each course technique
   and why extra data would be needed for the proposed policy analysis.
3. **Method.** Read docs/methodology.md and config/heat_metrics.json. Be able to
   explain a percentile, a fixed reference, a five-day seasonal window, strict
   exceedance, a paired denominator and a percentage point. P90 is relative
   warmth for each city/time of year; it is not an official heatwave warning.
4. **Data spot checks.** Open a copy of daily_temperatures.csv without saving
   edits. Filter Guwahati, 2005-06-26: temperatures are blank, missing flags
   true, and heat flags blank in the final table. Check several other city-
   dates against the original CSVs using (point_id, date); city names follow
   GeoJSON feature order. Compare a temperature with its fitted threshold:
   only a strictly greater value should be flagged. Keep the originals intact.
5. **Coverage and validation.** Read data/processed/validation_report.txt and
   its JSON counterpart. Expect 140,256 rows and 140,255 complete pairs. The
   final table has 21 columns, 5,856 thresholds, 384 annual rows and 16 period
   comparisons. Guwahati 2005 has 364 paired days. Expected warnings disclose
   the known gap, clock-time alignment, project-relative method and network
   change; they should not be silently removed to obtain a clean-looking report.
6. **Results and figures (final).** Read outputs/analysis/results-note.md, then
   open all five figures. Check that the narrative matches the CSV tables and
   that the sensitivity caveat is retained. Equal-city means are not weighted
   by population. A positive night-minus-day change need not mean both rose.
7. **Run it yourself.** Use the commands below in a freshly extracted copy.
   Read the short source modules in the order listed. Tests provide evidence,
   but your ability to explain the decisions matters for an instructor review.

## Commands and code reading order

Install once in your chosen Python 3.11+ environment (3.12.10 was tested):

```powershell
python -m pip install -r requirements.txt
```

For November 6:

```powershell
python src/run_project.py --preliminary
```

For the final submission:

```powershell
python src/run_project.py
```

Check all tests:

```powershell
python -W error -m unittest discover -s tests -v
```

Read src/run_project.py first (the sequence), src/prepare_data.py next (cleaning
and joining), src/heat_metrics.py (definitions), and src/analyze_data.py
(summaries/figures). src/build_packages.py assembles and verifies the packages.
A join matches two tables by a shared key; a fingerprint is a SHA-256 digest
used to detect file changes. Deterministic means identical inputs/settings in
the tested environment regenerate identical output bytes.

## Exactly what to submit on November 6

The team-provided handoff specifies a preliminary dataset, the software code
used to prepare it, and a brief topic outline. Submit the new preliminary ZIP
from Submissions, or its extracted folder if your portal requests a folder.
It includes:

- TOPIC_OUTLINE.md: the brief research topic and economics motivation.
- data/processed/daily_temperatures.csv: the 16-column temperature-only panel.
- src/, config/, requirements.txt and README.md: complete preparation code,
  settings and instructions.
- data/raw/: the permitted original inputs needed to reproduce the dataset.
- Coverage/validation reports, tests and supporting documentation.

The November 6 deadline/requirements are from your handoff. The provided PDF
does not separately specify that checkpoint. If your portal has extra fields
or an update, follow those instructions when uploading. No invented portal
format, team identity or submission confirmation is included here.

## Exactly what to submit on November 30

The provided handout asks for a self-contained replication folder: cleaned
dataset, complete code, a README describing source/coverage/economics relevance
and every ordered preparation step, plus 2-3 questions with policy relevance
and a course technique. Submit the final ZIP or its extracted folder as required.
It contains all of that, including raw inputs, settings, pinned dependencies,
the three completed questions, figures, descriptive results, sensitivity tables,
tests and machine-readable validation/provenance records.

Use the final ZIP rather than a GitHub source download: generated datasets and
figures are deliberately git-ignored in the working repository. GitHub alone
therefore does not contain every included submission artifact. Add any required
names/IDs/portal fields before upload, and retain the submitted ZIP unchanged.

## Limits you should be ready to explain

These are one-degree grid estimates, not precise urban measurements. Tmin is a
nighttime proxy; the export's exact observation/date clock convention is unknown.
IMD documents a network change from 2008 onward. The 24-year retrospective
reference and unbootstrapped adaptation differ from official ETCCDI indices.
The earlier-reference sensitivity has an additional reference-boundary caveat.
No causal effects, health damage, electricity use or monetary benefits are
estimated. Candidate policy questions explicitly state their additional data
and identification requirements.
