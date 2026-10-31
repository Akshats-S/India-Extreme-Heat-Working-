# Checks the original temperature files without changing them.
"""Read-only audit using the same checks as the preparation pipeline.

Usage: python src/audit_raw_data.py [fileA.csv fileB.csv]
Accepts the configuration/path options documented by prepare_data.py --help.
Returns nonzero on validation errors and never writes output files.
"""

import sys

from prepare_data import main


if __name__ == "__main__":
    sys.exit(main(audit_only=True))
