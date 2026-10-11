# Rental Bond Lodgements – Saidbek (SID: 560219160)

DATA1002 Stage 1 – Best suburbs for USYD students. This folder covers the **price (rental bond)** dataset.

## Data
| File | Description |
|---|---|
| `rentalbond_lodgements_year_2025(original).xlsx` | Original NSW Fair Trading rental bond data, Jan–Dec 2025 |
| `rentalbond_2025_DIRTY_practice.xlsx` | Copy with errors added by AI for cleaning practice (tutor approved) – **input to the code** |
| `greater_sydney_suburbs.csv` | Group's list of Greater Sydney suburbs |
| `postcodes-lookup.csv` | Suburb–postcode lookup (schappim/australian-postcodes, GitHub) |
| `clean_greater_sydney_rentalbond.csv` | Cleaned dataset (215,901 rows, 10 columns) |
| `housing_scores.csv` | Median rent per room, bonds, price_tier and avail_tier per suburb |
| `price_score.csv` | Price score per suburb (price_tier × 2) for the group Liveability Index |

## Code (run in this order)
1. `rental_price.py` – cleans the data, merges with Greater Sydney postcodes, creates rent per room and the 1–5 tiers. Saves `clean_greater_sydney_rentalbond.csv` and `housing_scores.csv`.
2. `data_quality.py` – prints the data quality counts and rows removed by each cleaning step (Section B). Saves nothing.
3. `section_c_stats.py` – prints the descriptive statistics, grouped summaries and correlations (Section C).
4. `charts.py` – creates `chart1_bar.png`, `chart2_box.png` and `chart3_scatter.png`.
5. `rental_score_saidbek.py` – creates `price_score.csv` for the group score.

## How to run
Requires Python 3 with pandas, numpy, openpyxl and matplotlib:

Keep all files in the same folder, then run each script, e.g. `python rental_price.py`.
