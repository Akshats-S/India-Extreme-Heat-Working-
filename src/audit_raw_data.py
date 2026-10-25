'''Structural audit of the two raw IMDWeb CSV files.

Reads the files from data/raw/ (or paths given on the command line), identifies
which file holds daily maximum vs. minimum temperature from the column names
(not the file names), and prints structural checks. It does not modify any data
and does not compute any research results.

Usage:
    python src/audit_raw_data.py                       # scans data/raw/*.csv
    python src/audit_raw_data.py fileA.csv fileB.csv   # explicit paths
'''
import sys
from pathlib import Path

import pandas as pd

EXPECTED_START, EXPECTED_END = '2001-01-01', '2024-12-31'
EXPECTED_POINTS = 16


def identify(df):
    '''Return 'tmax' or 'tmin' based on the value column present in the header.'''
    cols = set(df.columns)
    if 'tmax' in cols and 'tmin' not in cols:
        return 'tmax'
    if 'tmin' in cols and 'tmax' not in cols:
        return 'tmin'
    raise ValueError('Cannot identify variable from columns: ' + str(list(df.columns)))


def audit_one(path):
    df = pd.read_csv(path)
    var = identify(df)
    print('\n=== ' + path.name + ' -> ' + var)
    print('columns:', list(df.columns))
    print('rows:', len(df))
    print('date range:', df['time'].min(), 'to', df['time'].max())
    print('distinct point_id:', df['point_id'].nunique(), '(expected', EXPECTED_POINTS, ')')
    print('missing values per column:', df.isna().sum().to_dict())
    print('duplicate (time, point_id) rows:', int(df.duplicated(['time', 'point_id']).sum()))
    expected_days = [d.strftime('%Y-%m-%d') for d in pd.date_range(EXPECTED_START, EXPECTED_END)]
    gaps = {}
    for pid, times in df.groupby('point_id')['time']:
        have = set(times)
        missing = [d for d in expected_days if d not in have]
        if missing:
            gaps[int(pid)] = missing
    print('dates missing per point_id (vs full calendar range):', gaps or 'none')
    print(var, 'min/max value (units not stated in file):', df[var].min(), df[var].max())
    return var, df


def main(argv):
    paths = [Path(p) for p in argv] if argv else sorted(Path('data/raw').glob('*.csv'))
    if len(paths) != 2:
        sys.exit('Expected exactly 2 CSV files, found ' + str(len(paths)) + '. Put them in data/raw/.')
    found = dict(audit_one(p) for p in paths)
    if set(found) != {'tmax', 'tmin'}:
        sys.exit('The two files must be one tmax file and one tmin file.')
    key = ['time', 'point_id']
    merged = found['tmax'].merge(found['tmin'], on=key, how='outer', indicator=True)
    print('\n=== cross-file checks')
    print('merge match counts on (time, point_id):', merged['_merge'].value_counts().to_dict())
    print('rows where tmin > tmax:', int((merged['tmin'] > merged['tmax']).sum()))


if __name__ == '__main__':
    main(sys.argv[1:])
