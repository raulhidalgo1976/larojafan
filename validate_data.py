#!/usr/bin/env python3
"""Fail closed when an upstream CSV is malformed or implausibly truncated."""
import csv, sys
from pathlib import Path
root = Path(sys.argv[1] if len(sys.argv) > 1 else 'data')
required = {
 'results': ({'date','home_team','away_team','home_score','away_score','tournament','city','country'}, 40000),
 'goalscorers': ({'date','home_team','away_team','team','scorer','minute','own_goal','penalty','assist'}, 30000),
 'shootouts': ({'date','home_team','away_team','winner'}, 100),
}
for name, (columns, minimum) in required.items():
    path = root / f'{name}.csv'
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not columns.issubset(reader.fieldnames or []):
            raise SystemExit(f'{name}: missing columns {columns-set(reader.fieldnames or [])}')
        rows = sum(1 for _ in reader)
        if rows < minimum: raise SystemExit(f'{name}: only {rows} rows (expected >= {minimum})')
    print(f'{name}: {rows} rows OK')
