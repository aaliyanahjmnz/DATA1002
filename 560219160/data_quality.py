"""
data_quality.py - prints every number used in Section B (Data Quality Assessment
and Data Cleaning). It never changes the original files and saves nothing.

Part 1 counts the quality issues in the Greater Sydney bonds BEFORE cleaning.
Part 2 repeats the cleaning steps of rental_price.py and prints how many rows
each step removes, so rental_price.py itself can stay free of print statements.
"""
import pandas as pd
import numpy as np

def show(label, value):
    print(f"  {label:<48}{value:>10,}")

# =====================================================================
# Load files and build the Greater Sydney postcode list (as in rental_price.py)
# =====================================================================
df = pd.read_excel("rentalbond_2025_DIRTY_practice.xlsx",
                   sheet_name="Year 2025 Rental Bond Lodgments", header=2)
great_syd = pd.read_csv("greater_sydney_suburbs.csv")
lookup = pd.read_csv("postcodes-lookup.csv")

df.columns = df.columns.str.strip().str.title()
great_syd["Suburb"] = great_syd["Suburb"].str.strip().str.title()
lookup.columns = lookup.columns.str.strip()
lookup["Suburb"] = lookup["Suburb"].str.strip().str.title()
nsw = lookup[lookup["State"] == "NSW"]
great_syd = great_syd.merge(nsw[["Suburb", "Postcode"]], on="Suburb", how="left")
great_syd = great_syd.dropna(subset=["Postcode"])
great_syd["Postcode"] = great_syd["Postcode"].astype(int)
great_syd.loc[great_syd["Suburb"] == "North Sydney", "Postcode"] = 2060
great_syd = great_syd.drop_duplicates(subset=["Suburb", "Postcode"])
p = great_syd["Postcode"]
great_syd = great_syd[p.between(2000, 2234) | p.between(2555, 2574) | p.between(2740, 2786)]
pc_labels = great_syd.groupby("Postcode")["Suburb"].apply(" / ".join).reset_index()

print("DATASET SIZE")
show("Rows in the practice file", len(df))
raw_postcode = df["Postcode"].copy()          # keep the original values for Part 1
df["Postcode"] = pd.to_numeric(df["Postcode"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
df["Raw Postcode"] = raw_postcode
df = df.merge(pc_labels, on="Postcode", how="inner")
show("Rows after Greater Sydney merge", len(df))
show("Bonds removed by the merge (not Sydney)", len(raw_postcode) - len(df))
show("Greater Sydney suburbs in the group list", great_syd["Suburb"].nunique())

# =====================================================================
# PART 1 - quality issues in the Greater Sydney rows (before cleaning)
# =====================================================================
gs = df.drop(columns=["Raw Postcode", "Suburb"])
print("\nPART 1 - QUALITY ISSUES (Greater Sydney rows, before cleaning)")
show("Empty columns (all blank)", int(gs.isna().all().sum()))

is_text = df["Raw Postcode"].map(lambda v: isinstance(v, str))
five_digit = df["Raw Postcode"].map(lambda v: isinstance(v, int) and v >= 10000)
show("Postcode stored as text ('NSW 2000', '2000.0')", int(is_text.sum()))
show("Postcode with 5 digits (e.g. 20080)", int(five_digit.sum()))

for col in ["Lodgement Date", "Dwelling Type", "Bedrooms", "Weekly Rent ($)"]:
    show(f"Blank cells in {col}", int(gs[col].isna().sum()))
beds = gs["Bedrooms"].dropna().astype(str).str.strip()
rent = gs["Weekly Rent ($)"].dropna().astype(str).str.strip()
show('"U" (unknown) in Bedrooms', int((beds.str.upper() == "U").sum()))
show('"U" (unknown) in Weekly Rent', int((rent.str.upper() == "U").sum()))

dw = gs["Dwelling Type"].dropna().astype(str)
dw_up = dw.str.strip().str.upper()
codes = {"F", "H", "T", "O", "U"}
words = {"FLAT", "HOUSE", "TOWNHOUSE", "OTHER", "UNKNOWN"}
show("Dwelling Type: different spellings in total", dw.nunique())
show("Dwelling Type: valid but badly spelled", int((~dw.isin(codes) & dw_up.isin(codes | words)).sum()))
show("Dwelling Type: invalid codes (1, 3, G, P...)", int((~dw_up.isin(codes | words)).sum()))

beds_num = pd.to_numeric(beds, errors="coerce")
rent_num = pd.to_numeric(rent, errors="coerce")
show("Bedrooms written as text ('two', '2 bed')", int((beds_num.isna() & (beds.str.upper() != "U")).sum()))
show("Weekly Rent written as text ('$999.99')", int((rent_num.isna() & (rent.str.upper() != "U")).sum()))

b = pd.to_numeric(gs["Bedrooms"].astype(str).str.replace("$", "", regex=False), errors="coerce")
r = pd.to_numeric(gs["Weekly Rent ($)"].astype(str).str.replace("$", "", regex=False), errors="coerce")
swap = (b >= 150) & r.between(0, 20)
show("Swapped Bedrooms / Weekly Rent", int(swap.sum()))
show("Negative bedrooms", int((b < 0).sum()))
show("More than 6 bedrooms (not swapped)", int(((b > 6) & ~swap).sum()))

r_clean = pd.to_numeric(gs["Weekly Rent ($)"].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce")
show("Placeholder rents ($0 or $9,999+)", int(((r_clean <= 0) | (r_clean >= 9999)).sum()))

d = pd.to_datetime(gs["Lodgement Date"], dayfirst=True, format="mixed", errors="coerce")
show("Blank or unreadable dates", int(d.isna().sum()))
show("Dates outside 2025 (2024, 2026, 2205)", int((d.notna() & (d.dt.year != 2025)).sum()))

key = ["Lodgement Date", "Raw Postcode", "Dwelling Type", "Bedrooms", "Weekly Rent ($)"]
show("Exact duplicate rows (kept on purpose)", int(df.duplicated(subset=key).sum()))

# =====================================================================
# PART 2 - effect of each cleaning step (same code as rental_price.py)
# =====================================================================
print("\nPART 2 - ROWS REMOVED BY EACH CLEANING STEP")
df = df.drop(columns=["Raw Postcode"])
before = len(df)
df = df.dropna(axis="columns", how="all").dropna(how="all").dropna(thresh=2)
show("Empty rows removed", before - len(df))

date_col, dw_type, bednum_col, price = "Lodgement Date", "Dwelling Type", "Bedrooms", "Weekly Rent ($)"
df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, format="mixed", errors="coerce")
df["Postcode"] = df["Postcode"].astype(int)
df[dw_type] = df[dw_type].str.strip().str.upper()
mapping_dw = {"F": "Flat", "FLAT": "Flat", "H": "House", "HOUSE": "House",
              "U": "Unknown", "UNKNOWN": "Unknown", "1": "Unknown", "P": "Unknown", "G": "Unknown",
              "4": "Unknown", "3": "Unknown", "I": "Unknown", "Y": "Unknown", "Z": "Unknown",
              "X": "Unknown", "R": "Unknown", "T": "Townhouse", "TOWNHOUSE": "Townhouse",
              "O": "Other", "OTHER": "Other"}
df[dw_type] = df[dw_type].replace(mapping_dw)

beds_num = pd.to_numeric(df[bednum_col].astype(str).str.replace("$", "", regex=False), errors="coerce")
rent_num = pd.to_numeric(df[price].astype(str).str.replace("$", "", regex=False), errors="coerce")
swapped = (beds_num >= 150) & rent_num.between(0, 20)
show("Swapped rows switched back", int(swapped.sum()))
df.loc[swapped, price] = beds_num[swapped]
df.loc[swapped, bednum_col] = rent_num[swapped]
s = df[bednum_col].astype(str).str.strip().str.lower()
s = s.replace({"studio": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5"})
s = s.str.extract(r"^(-?\d+(?:\.\d+)?)")[0]
num = pd.to_numeric(s, errors="coerce")
show("Bedrooms set to missing (outside 0-6)", int((num.notna() & ~num.between(0, 6)).sum()))
num[~num.between(0, 6)] = np.nan
df[bednum_col] = num

df[price] = df[price].astype(str).str.replace(r"[^\d.]", "", regex=True)
df[price] = pd.to_numeric(df[price], errors="coerce")
before = len(df)
df = df.dropna(subset=[price])
show("Rows with no valid rent removed", before - len(df))

rooms = df[bednum_col].replace(0, 1)
df["Rent per Room ($)"] = df[price] / rooms
ppr = df["Rent per Room ($)"]
show("Removed: unknown bedrooms (no rent per room)", int(ppr.isna().sum()))
show("Removed: rent per room below $100", int((ppr < 100).sum()))
show("Removed: rent per room above $1,500", int((ppr > 1500).sum()))
df = df[ppr.between(100, 1500)]

df["Year"] = df[date_col].dt.year.astype("Int64")
show("Removed: blank or unreadable dates", int(df["Year"].isna().sum()))
show("Removed: dates outside 2025", int((df["Year"].notna() & (df["Year"] != 2025)).sum()))
df = df[df["Year"] == 2025]
df["Month"] = df[date_col].dt.month.astype("Int64")
df["Day"] = df[date_col].dt.day.astype("Int64")

print("\nFINAL DATASET")
show("Rows in cleaned dataset", len(df))
show("Columns in cleaned dataset", df.shape[1])

pcode_price = df.groupby("Postcode").agg(median_ppr=("Rent per Room ($)", "median"),
                                         n_bonds=("Rent per Room ($)", "size")).reset_index()
show("Postcodes before the 30-bond minimum", len(pcode_price))
pcode_price = pcode_price[pcode_price["n_bonds"] >= 30]
show("Postcodes kept (30+ bonds)", len(pcode_price))

housing = great_syd.merge(pcode_price[["Postcode", "median_ppr"]], on="Postcode", how="left")
housing = housing.sort_values("median_ppr", na_position="last").drop_duplicates(subset="Suburb")
show("Suburbs in housing_scores.csv", len(housing))
show("Suburbs with no housing score", int(housing["median_ppr"].isna().sum()))

# =====================================================================
# PART 3 - effect of the minimum number of bonds per postcode
# A postcode needs at least 30 bonds to get a housing score. This part counts
# how many suburbs would be left without a score at stricter minimums.
# =====================================================================
print("\nPART 3 - EFFECT OF THE MINIMUM NUMBER OF BONDS")
bonds_per_postcode = df.groupby("Postcode").size()
for minimum in [30, 100, 200]:
    kept = set(bonds_per_postcode[bonds_per_postcode >= minimum].index)
    no_score = great_syd.groupby("Suburb")["Postcode"].apply(lambda s: not s.isin(kept).any()).sum()
    print(f"  Minimum {minimum:>3} bonds: {len(kept):>3} postcodes kept, {no_score:>3} suburbs with no score")
