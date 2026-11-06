"""Apply separately sourced historical goalscorer additions without changing upstream CSVs."""
import csv
from collections import Counter
from pathlib import Path

GOAL_COLUMNS = ('date','home_team','away_team','team','scorer','minute','own_goal','penalty','assist')
MATCH_COLUMNS = ('date','home_team','away_team')

def read_merged_goals(data_dir='data', corrections_path='historical_corrections.csv'):
    """Return original goals + verified missing additions; safe against repeated builds.

    A match-level count check prevents inserting additions into a match whose
    upstream dataset has already acquired goal records. In that case, stop for
    manual reconciliation rather than risk duplicates.
    """
    data_dir = Path(data_dir)
    with (data_dir/'goalscorers.csv').open(encoding='utf-8-sig',newline='') as f:
        originals = list(csv.DictReader(f))
    with Path(corrections_path).open(encoding='utf-8-sig',newline='') as f:
        corrections = list(csv.DictReader(f))
    with (data_dir/'results.csv').open(encoding='utf-8-sig',newline='') as f:
        matches = {tuple(r[k] for k in MATCH_COLUMNS):r for r in csv.DictReader(f)}
    by_match = {}
    for r in corrections:
        key = tuple(r[k] for k in MATCH_COLUMNS)
        by_match.setdefault(key, []).append(r)
        if r['team'] != 'Spain' or 'Spain' not in key[1:]:
            raise ValueError(f'Invalid correction team/match: {key}')
        if key not in matches:
            raise ValueError(f'Correction has no matching result: {key}')
    upstream_counts=Counter(tuple(r[k] for k in MATCH_COLUMNS) for r in originals)
    merged=list(originals)
    for key, additions in by_match.items():
        match=matches[key]
        spain_goals=int(match['home_score'] if match['home_team']=='Spain' else match['away_score'])
        if len(additions)!=spain_goals:
            raise ValueError(f'Corrections for {key}: {len(additions)} goals vs {spain_goals} in results.csv')
        if upstream_counts[key]:
            raise ValueError(f'Upstream now has {upstream_counts[key]} scorer records for {key}; reconcile before applying historical overlay')
        merged.extend({k:r[k] for k in GOAL_COLUMNS} for r in additions)
    return merged
