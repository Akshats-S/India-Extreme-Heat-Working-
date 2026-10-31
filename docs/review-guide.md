# Replication and submission guide

## Preliminary assessment: 6 November 2026

The team handoff lists three required deliverables: a preliminary dataset,
the software code used to prepare it, and a brief research-topic outline.
The hand-in contains nine files: those deliverables, a short README, and only
the original inputs, preparation settings and dependencies needed to run it.
Final-stage documentation, heat analysis, figures, tests and build records
are excluded. The working repository retains development and verification material.

Extract the preliminary ZIP to a fresh folder and open PowerShell inside it.
Use Python 3.11+ (3.12.10 was tested). Create an environment beside the copy:

```powershell
python -m venv ../heat-review-env
$reviewPython = '../heat-review-env/Scripts/python.exe'
& $reviewPython -m pip install -r requirements.txt
```

Record the supplied raw/daily CSV fingerprints and regenerate:

```powershell
$files = './data/raw/*.csv', './data/processed/daily_temperatures.csv'
$before = Get-ChildItem $files -File | Get-FileHash -Algorithm SHA256
& $reviewPython src/prepare_data.py --skip-heat
$after = Get-ChildItem $files -File | Get-FileHash -Algorithm SHA256
Compare-Object $before $after -Property Path, Hash
```

No comparison output means the supplied data were reproduced and raw files
stayed unchanged. The run also creates coverage and validation diagnostics;
these are generated during execution rather than bundled as extra hand-in items.
Expected daily shape: 140,256 rows, 16 columns and 140,255 complete pairs.
Guwahati, 2005-06-26 remains blank and flagged. Team names and instructions
are in README.md; the brief topic is TOPIC_OUTLINE.md.

The original preliminary-assessment notice has not been provided; the three-item
list and November 6 deadline come from the team handoff. The supplied final
course PDF does not separately specify that checkpoint.

## Final assessment: 30 November 2026

The final handout requires the cleaned dataset, complete reproducible code,
a README with source/coverage/economics relevance and ordered cleaning steps,
and 2-3 candidate questions with policy relevance and course techniques.
The final folder also includes the implemented analysis and verification evidence.

From the final folder, after installing dependencies:

```powershell
python -m pip install -r requirements.txt
python src/run_project.py
python -W error -m unittest discover -s tests -v
```

This regenerates seven preparation files, six analysis CSVs, a results note,
an analysis report and five figures. Expected dimensions: 140,256 daily
rows/21 columns, 5,856 threshold rows, 384 annual rows and 16 period comparisons.
PACKAGE_CHECKS.json records tests and repeated/extracted-copy reproduction;
MANIFEST.json fingerprints the final folder. Preliminary verification records
stay outside its minimal hand-in in the outer package_build_report.json.

## Reading and spot checks

- The source and brief research question are in README.md and TOPIC_OUTLINE.md.
  Check city/date rows against the original CSVs without editing originals.
- Final docs/methodology.md defines P90, the fixed reference, seasonal windows,
  strict exceedance and paired dates. Missing heat flags are blank, not False.
- Final outputs/analysis/results-note.md links to all five figures. Check its
  numbers against CSVs. Equal-city means are not population weighted. A
  positive night-minus-day change can mean nighttime decreased less.
- Final RESEARCH_QUESTIONS.md gives three economics applications with course
  techniques and additional evidence needs.

For development checks, run the complete suite from the working repository or
final package. The preliminary folder deliberately contains no test suite or
final-stage code. Its standalone runtime is verified during package building.

Use the matching dated ZIP or complete assessment folder and follow the portal's
required format/identity fields. GitHub publication is separate from course upload.

## Interpretation limits

Values are one-degree grid estimates. Tmin is a nighttime proxy, with unverified
export clock-time alignment. IMD documents a network change from 2008 onward.
Final analyses disclose the retrospective reference and unbootstrapped sensitivity
caveat. No causal policy or monetary-benefit estimate is claimed. Automated
execution evidence does not imply independent human sign-off.
