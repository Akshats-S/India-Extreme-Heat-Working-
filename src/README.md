# src/

Python scripts for the data-preparation pipeline. Defaults resolve from the repository location.

## Implemented

| Script | What it does |
|--------|--------------|
| `audit_raw_data.py` | Read-only JSON audit using the same validation functions as preparation; nonzero exit status on important failures. |
| `prepare_data.py` | Strict input audit, one-to-one Tmax/Tmin merge, complete city-day calendar, missing flags, validation, coverage summaries and deterministic CSV/JSON/text outputs. |

```bash
python -m pip install -r requirements.txt
python src/prepare_data.py
python src/audit_raw_data.py
python -W error -m unittest discover -s tests -v
```

## Planned (pending, not implemented)

| Planned step | Corresponding issue |
|--------------|---------------------|
| Define extreme day/night thresholds (parameterized) | #4 |
| Extend the preliminary cleaned dataset with agreed heat indicators | #5 (final scope) |

Exact transformations, output schema, configuration, failure policy and limitations are in [the preparation guide](../docs/preparation.md). No extreme-heat definition is chosen by the preliminary pipeline. Human verification is pending.
