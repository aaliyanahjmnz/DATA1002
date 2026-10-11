"""Run with pandas: python clean_greater_sydney_transport.py --transport PATH --suburbs PATH.
Postcode aliases are explicit Sydney locality choices, not blanket suffix removal.
No service-frequency or journey-time accessibility score is calculated.
"""
from pathlib import Path
import argparse
import json
import pandas as pd

ALIASES = {
    'DARLINGTON 2008': 'DARLINGTON', 'DURAL 2158': 'DURAL',
    'ELDERSLIE 2570': 'ELDERSLIE', 'ENMORE 2042': 'ENMORE',
    'GREENDALE 2745': 'GREENDALE', 'KINGSWOOD 2747': 'KINGSWOOD',
    'LANSDOWNE 2163': 'LANSDOWNE', 'LILLI PILLI 2229': 'LILLI PILLI',
    'LONG POINT 2564': 'LONG POINT', 'NELSON 2765': 'NELSON',
    'PUNCHBOWL 2196': 'PUNCHBOWL', 'RIVERVIEW 2066': 'RIVERVIEW',
    'SILVERWATER 2128': 'SILVERWATER', 'ST CLAIR 2759': 'ST CLAIR',
    'SUMMER HILL 2130': 'SUMMER HILL', 'THE ROCKS 2000': 'THE ROCKS',
}
MODES = {'Bus Stop': 'Bus', 'Train Station': 'Train',
         'Train Station Platform': 'Train', 'Ferry Wharf': 'Ferry',
         'Light Rail Station': 'Light Rail'}

def clean_text(series):
    return series.astype('string').str.strip().str.replace(r'\s+', ' ', regex=True).replace('', pd.NA)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--transport', default='tsn-to-tz-mapping.csv')
    p.add_argument('--suburbs', default='greater_sydney_suburbs.csv')
    p.add_argument('--output', default='cleaned_output')
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(args.transport, dtype='string')
    reference = pd.read_csv(args.suburbs, dtype='string')
    reference.columns = reference.columns.str.strip().str.upper()
    reference['SUBURB'] = clean_text(reference['SUBURB'])
    reference['SUBURB_JOIN_KEY'] = reference['SUBURB'].str.upper()
    reference = reference.dropna(subset=['SUBURB_JOIN_KEY']).drop_duplicates('SUBURB_JOIN_KEY')
    df = raw.copy()
    df.columns = df.columns.str.strip().str.upper()
    df = df.rename(columns={'NAME': 'STOP_NAME', 'TRANSIT_STOP_TYPE': 'STOP_TYPE',
                            'TZ16_NAME': 'TRAVEL_ZONE_NAME'})
    for column in df.columns:
        df[column] = clean_text(df[column])
    required = ['TSN', 'STOP_NAME', 'STOP_TYPE', 'SUBURB', 'TZ16_CODE']
    missing = df[required].isna().any(axis=1)
    missing_count = int(missing.sum())
    df = df.loc[~missing].copy()
    # Check exact duplicates while coordinates still distinguish records.
    duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    df['SOURCE_SUBURB'] = df['SUBURB']
    source_key = df['SUBURB'].str.upper()
    df['SUBURB_JOIN_KEY'] = source_key.replace(ALIASES)
    df['MATCH_METHOD'] = source_key.map(lambda v: 'postcode_alias' if v in ALIASES else 'exact_name')
    included = df['SUBURB_JOIN_KEY'].isin(reference['SUBURB_JOIN_KEY'])
    excluded = df.loc[~included].groupby('SOURCE_SUBURB', as_index=False).agg(RECORDS=('TSN', 'size'))
    excluded['REASON'] = 'No approved match to reference; outside scope or name requires review'
    excluded.to_csv(out / 'excluded_transport_suburbs.csv', index=False)
    kept = df.loc[included].copy()
    canonical = reference.set_index('SUBURB_JOIN_KEY')['SUBURB']
    kept['SUBURB'] = kept['SUBURB_JOIN_KEY'].map(canonical)
    kept = kept.drop(columns=['LATITUDE', 'LONGITUDE'], errors='ignore')
    kept['MODE'] = kept['STOP_TYPE'].map(MODES).fillna('Other')
    kept['PRIMARY_ACCESS_POINT'] = kept['STOP_TYPE'].ne('Train Station Platform')
    indicators = {'BUS_STOPS': 'Bus Stop', 'TRAIN_STATIONS': 'Train Station',
                  'TRAIN_PLATFORMS': 'Train Station Platform', 'FERRY_WHARVES': 'Ferry Wharf',
                  'LIGHT_RAIL_STATIONS': 'Light Rail Station'}
    work = kept.copy()
    for col, typ in indicators.items():
        work[col] = work['STOP_TYPE'].eq(typ).astype(int)
    agg = {col: (col, 'sum') for col in indicators}
    summary = work.groupby('SUBURB_JOIN_KEY', as_index=False).agg(
        PRIMARY_ACCESS_POINTS=('PRIMARY_ACCESS_POINT', 'sum'),
        MODES_AVAILABLE=('MODE', 'nunique'), TRAVEL_ZONE_COUNT=('TZ16_CODE', 'nunique'),
        TOTAL_RECORDS=('TSN', 'size'), **agg)
    summary = reference.merge(summary, on='SUBURB_JOIN_KEY', how='left', validate='one_to_one')
    summary['MATCH_STATUS'] = summary['TOTAL_RECORDS'].notna().map({True: 'Matched', False: 'No matched records'})
    # Keep unavailable counts blank, rather than implying zero transport provision.
    for col in ['PRIMARY_ACCESS_POINTS', 'MODES_AVAILABLE', 'TRAVEL_ZONE_COUNT', 'TOTAL_RECORDS', *indicators]:
        summary[col] = summary[col].astype('Int64')
    kept.to_csv(out / 'greater_sydney_transport_stops_cleaned.csv', index=False, encoding='utf-8-sig')
    summary.to_csv(out / 'greater_sydney_transport_summary.csv', index=False, encoding='utf-8-sig')
    summary.loc[summary.MATCH_STATUS.ne('Matched'), ['SUBURB', 'SUBURB_JOIN_KEY', 'MATCH_STATUS']].to_csv(
        out / 'suburbs_without_matched_stops.csv', index=False)
    pd.DataFrame(list(ALIASES.items()), columns=['SOURCE_SUBURB', 'SUBURB_JOIN_KEY']).to_csv(
        out / 'suburb_postcode_aliases.csv', index=False)
    audit = dict(original_rows=len(raw), reference_suburbs=len(reference), missing_key_rows=missing_count,
                 exact_duplicates_removed=duplicates, retained_rows=len(kept),
                 excluded_rows=int((~included).sum()), matched_suburbs=int(summary.TOTAL_RECORDS.notna().sum()),
                 unmatched_suburbs=int(summary.TOTAL_RECORDS.isna().sum()),
                 postcode_alias_rows=int(kept.MATCH_METHOD.eq('postcode_alias').sum()),
                 unknown_stop_types=sorted(kept.loc[kept.MODE.eq('Other'), 'STOP_TYPE'].unique().tolist()),
                 repeated_tsn_rows=int(kept.TSN.duplicated(keep=False).sum()))
    (out / 'cleaning_audit.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))
    print('Suburbs without matched records:', ', '.join(summary.loc[summary.TOTAL_RECORDS.isna(), 'SUBURB']))

if __name__ == '__main__':
    main()
