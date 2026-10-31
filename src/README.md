# src/

Python scripts for the data-preparation pipeline. Defaults resolve from the repository location.

## Implemented

| Script | What it does |
|--------|--------------|
| `audit_raw_data.py` | Read-only JSON audit using the same validation functions as preparation; nonzero exit status on important failures. |
| `prepare_data.py` | Strict raw audit, full-calendar merge and default heat workflow. Writes five CSVs plus JSON/text reports. `--skip-heat` preserves preliminary output. |
| `heat_metrics.py` | Configurable fixed seasonal percentiles, nullable daily flags, coverage-aware annual summaries and early/late percentage-point comparisons. |
| `analyze_data.py` | Six descriptive/sensitivity CSVs, five figures, computed results note and fingerprinted analysis report. |
| `run_project.py` | One command for the complete workflow; `--preliminary` runs temperature-only preparation. |
| `build_packages.py` | Separate preliminary/final ZIPs; source whitelist, fresh-stage tests, repeatability, manifests and extracted-copy reproduction. |

```bash
python -m pip install -r requirements.txt
python src/run_project.py
python src/audit_raw_data.py
python src/build_packages.py
python -W error -m unittest discover -s tests -v
```

## Review and submission

| Planned step | Corresponding issue |
|--------------|---------------------|
| Descriptive figures and sensitivity analysis | #6 implemented |
| Final economics questions/documentation and submission packaging | #7 implemented; team names included, review and upload remain user actions |

Exact transformations and preliminary schemas are in [the preparation guide](../docs/preparation.md); the [methodology](../docs/methodology.md), [source metadata](../docs/source-metadata.md) and [heat output schemas](../docs/heat-output-schema.md) document phases 1/2. Automated and human checks remain distinguished honestly.
