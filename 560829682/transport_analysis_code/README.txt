Python transport analysis code

01_clean_greater_sydney_transport.py: final Greater Sydney cleaning and suburb aggregation.
02_score_transport.py: 80% access-point rank + 20% mode diversity; score out of 10.
archived/clean_nsw_transport.py: earlier saved cleaning version (preserved).

Requires Python and pandas. Place tsn-to-tz-mapping.csv and greater_sydney_suburbs.csv beside the scripts.
Run in Terminal from this folder:
python 01_clean_greater_sydney_transport.py
python 02_score_transport.py

The scoring script was extracted from the previously executed scoring code.
Unmatched suburbs remain unscored. R visualisations are not included.
