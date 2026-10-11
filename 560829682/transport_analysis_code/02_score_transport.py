"""Score cleaned Greater Sydney infrastructure out of 10 (requires pandas)."""
from pathlib import Path
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--input', default='cleaned_output/greater_sydney_transport_summary.csv')
parser.add_argument('--output', default='greater_sydney_transport_scores.csv')
args = parser.parse_args()
df = pd.read_csv(args.input)
matched = df['MATCH_STATUS'].eq('Matched') & df['PRIMARY_ACCESS_POINTS'].notna()
n = int(matched.sum())
if n < 2:
    raise ValueError('At least two matched suburbs are needed.')
ranks = df.loc[matched, 'PRIMARY_ACCESS_POINTS'].rank(method='average')
percentiles = (ranks - 1) / (n - 1)
df['ACCESS_POINT_PERCENTILE'] = float('nan')
df.loc[matched, 'ACCESS_POINT_PERCENTILE'] = percentiles * 100
df['TRANSPORT_SCORE_10'] = float('nan')
df.loc[matched, 'TRANSPORT_SCORE_10'] = (
    8 * percentiles + 2 * df.loc[matched, 'MODES_AVAILABLE'] / 4
).round(2)
df['TRANSPORT_RANK'] = df['TRANSPORT_SCORE_10'].rank(
    method='min', ascending=False
).astype('Int64')
df = df.sort_values(['TRANSPORT_SCORE_10', 'SUBURB'], ascending=[False, True], na_position='last')
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
df.to_csv(args.output, index=False, encoding='utf-8-sig')
print('Saved:', args.output)
print('Scored suburbs:', n)
