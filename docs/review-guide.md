# Replication and submission guide

Each assessment folder is self-contained. The original inputs, cleaned data,
code, settings and pinned dependencies are bundled. Preliminary output has
16 daily columns; final output has 21, including heat thresholds and flags.

## Preliminary replication on Windows

Extract the preliminary ZIP into a fresh review folder. Open PowerShell inside
the extracted package folder containing README.md, requirements.txt and src/.
Use the same PowerShell window for the following commands.

Create a separate environment beside the package (Python 3.12.10 was tested):

```powershell
python -m venv ..heat-review-env
$reviewPython = '..heat-review-envScriptspython.exe'
& $reviewPython -m pip install -r requirements.txt
```

Record the bundled raw/output fingerprints, regenerate and compare:

```powershell
$before = Get-ChildItem '.data
aw', '.dataprocessed' -File |
  Get-FileHash -Algorithm SHA256
& $reviewPython src/run_project.py --preliminary
$after = Get-ChildItem '.data
aw', '.dataprocessed' -File |
  Get-FileHash -Algorithm SHA256
Compare-Object $before $after -Property Path, Hash
```

No comparison output means identical raw and generated files. A SHA-256
fingerprint detects changed file contents. Run the complete test suite:

```powershell
& $reviewPython -W error -m unittest discover -s tests -v
```

Expected result: 42 tests, OK. The preliminary table contains 140,256 rows,
16 columns and 140,255 complete pairs; coverage contains 384 city-years.
The validation report has no errors and retains documented warnings.

## Final replication

From the final package folder, after installing requirements in the chosen
Python environment, run:

```powershell
python src/run_project.py
python -W error -m unittest discover -s tests -v
```

This regenerates seven preparation files, six analysis CSVs, a results note,
an analysis report and five figures. Expected dimensions are 140,256 daily
rows/21 columns, 5,856 threshold rows, 384 annual rows and 16 period comparisons.
PACKAGE_CHECKS.json records tests and repeated/extracted-copy reproduction;
MANIFEST.json fingerprints included files.

## Reading and spot checks

- COVER.md identifies Akshat Srivastava, Krishna Reddy and Jatin Shetty.
  TOPIC_OUTLINE.md explains the registered question and economics motivation.
- docs/methodology.md and config/heat_metrics.json define city/calendar-day
  P90, fixed reference, seasonal windows, strict exceedance and paired dates.
- In daily_temperatures.csv, Guwahati, 2005-06-26 has blank temperatures and
  true missing flags. Final heat flags are blank, not False. Guwahati 2005
  has 364 paired dates. Compare other rows with the raw point/date records.
- Final outputs/analysis/results-note.md links to all five figures. Check its
  numbers against the CSVs. Equal-city means are not population weighted.
  A positive night-minus-day change can mean nighttime decreased less.
- RESEARCH_QUESTIONS.md in the final folder gives three candidate applications
  with policy relevance, course techniques and additional evidence needs.

The code sequence is run_project.py, prepare_data.py, heat_metrics.py and
analyze_data.py. build_packages.py assembles the local verified ZIPs.

## Assessment contents

| Assessment | Required material |
|---|---|
| Preliminary, 6 November 2026 | Cleaned temperature dataset, preparation code, brief topic outline; supporting README, raw inputs, settings, reports and tests included |
| Final, 30 November 2026 | Cleaned dataset, complete reproducible code, README with source/coverage/economics relevance and ordered preparation steps, 2-3 candidate questions with policy relevance/course techniques |

The preliminary requirements come from the team handoff. The final requirements
and date come from docs/handout/Instructions.pdf. The final package additionally
includes figures, computed results, sensitivity tables and provenance records.

Use the matching dated ZIP or its complete assessment folder. Generated data
are included in the submission repository; they are git-ignored in the working
repository. Use the portal's requested format and any required IDs/section.
GitHub publication is separate from course submission.

## Interpretation limits

Values are one-degree grid estimates. Tmin is a nighttime proxy, with unverified
export clock-time alignment. IMD documents a network change from 2008 onward.
The retrospective 24-year reference, no-bootstrap adaptation and early-reference
boundary caveat are disclosed. No causal policy, health-damage, electricity-use
or monetary-benefit estimate is claimed. Automated tests are execution evidence,
not independent human sign-off.
