# Repository instructions

## Project

The Environmental Economics dataset and replication packages are complete.
Maintain the source here; publish assessment copies in
`Akshats-S/india-extreme-heat-submission`, with separate preliminary/final folders.
No implementation tasks remain assigned to teammates.

The primary question compares extreme nighttime and daytime heat across 16
Indian city-associated IMD grid points during 2001-2024. The panel has 140,256
rows and one absent temperature pair: Guwahati, 2005-06-26. Read
`docs/methodology.md` before changing measurements and `docs/review-guide.md`
for replication and submission contents.

## Maintenance rules

- Preserve `data/raw/` exactly. Write derived data to `data/processed/` and
  analysis artifacts to `outputs/`. Never commit credentials or local environments.
- Never invent observations, results, source metadata or human sign-off.
  Automated execution records are in `docs/verification-log.md`.
- Keep percentile, baseline, leap-day, missingness and denominator choices
  explicit in configuration and documented when changed.
- Use feature branches and pull requests; do not push directly to `main`.
  The lead's changes do not require a separate teammate approval.
- Update source/templates, rebuild packages and copy verified deliverables to
  the submission repository. Keep both assessment folders self-contained.
- Keep scientific limitations and source attribution in the deliverables.
- Use the team's Git identity. Do not add tool authorship/co-authorship,
  generated-by footers or session links to commits, PRs or project files.
- The instructor permits AI assistance; responsibility for academic review
  remains with the submitting students. Do not fabricate completed review.

## Commands

```powershell
python -m pip install -r requirements.txt
python src/run_project.py --preliminary
python src/run_project.py
python src/audit_raw_data.py
python -W error -m unittest discover -s tests -v
python src/build_packages.py
```

`prepare_data.py` audits/merges; `heat_metrics.py` defines research variables;
`analyze_data.py` generates summaries/figures; `run_project.py` sequences the
workflow; `build_packages.py` builds and verifies both ZIPs. Tests cover valid
inputs, deliberately faulty examples, known-answer calculations and packaging.

In the working repository, generated data/figures are git-ignored. In the
submission repository they are committed, and Git must preserve their packaged
bytes so final manifests and recorded validation fingerprints remain valid.
The preliminary hand-in contains only the requested dataset, preparation code,
brief outline and essential runtime files; tests/build records remain outside it.

Submission copies exclude development tests, package builders, authoring
templates and duplicate write-ups. Keep those maintenance assets only in this
working repository. Instructions.pdf is a protected comparison reference; keep
all existing copies unchanged.
