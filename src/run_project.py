# Runs data preparation and analysis in the correct order.
"""One command to regenerate the complete replication outputs."""

import argparse
import sys

from prepare_data import main as prepare


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preliminary", action="store_true", help="Prepare only the preliminary temperature dataset/reports.")
    args = parser.parse_args(argv)
    result = prepare(["--skip-heat"] if args.preliminary else [])
    if result or args.preliminary:
        return result
    from analyze_data import main as analyze
    return analyze([])


if __name__ == "__main__":
    sys.exit(main())
