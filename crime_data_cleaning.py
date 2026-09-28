import pandas as pd

crime = pd.read_csv("datasets/SuburbData26Q1.csv")
sydney = pd.read_csv("greater_sydney_suburbs.csv")

############### SUBURB STANDARDISATION ###############

# Standardise suburb names
crime["Suburb"] = crime["Suburb"].str.strip().str.upper()
sydney["Suburb"] = sydney["Suburb"].str.strip().str.upper()

# Sydney-specific suburb name corrections
sydney_variants = {
    "DARLINGTON (SYDNEY)": "DARLINGTON",
    "DURAL (HORNSBY)": "DURAL",
    "ELDERSLIE (CAMDEN)": "ELDERSLIE",
    "ENMORE (INNER WEST)": "ENMORE",
    "GREENDALE (LIVERPOOL)": "GREENDALE",
    "KINGSWOOD (PENRITH)": "KINGSWOOD",
    "LANSDOWNE (CANTERBURY-BANKSTOWN)": "LANSDOWNE",
    "LILLI PILLI (SUTHERLAND SHIRE)": "LILLI PILLI",
    "LONG POINT (CAMPBELLTOWN)": "LONG POINT",
    "NELSON (THE HILLS SHIRE)": "NELSON",
    "PUNCHBOWL (CANTERBURY-BANKSTOWN)": "PUNCHBOWL",
    "SILVERWATER (PARRAMATTA)": "SILVERWATER",
    "ST CLAIR (PENRITH)": "ST CLAIR",
    "SUMMER HILL (INNER WEST)": "SUMMER HILL",
    "THE ROCKS (SYDNEY)": "THE ROCKS"
}

# Apply corrections
crime["Suburb"] = crime["Suburb"].replace(sydney_variants)

# Greater Sydney suburb list
sydney_suburbs = set(sydney["Suburb"])

############### GENERAL CLEANING ###############

# Keep only Greater Sydney suburbs
crime_sydney = crime[crime["Suburb"].isin(sydney_suburbs)]

# Remove missing suburb values
crime_sydney = crime_sydney.dropna(subset=["Suburb"])

# Remove duplicate rows
crime_sydney = crime_sydney.drop_duplicates()

############### FILTERING ###############

# Keep only Jan 2021 onward
start_col = crime_sydney.columns.get_loc("Jan 2021")

crime_recent = crime_sydney.iloc[
    :,
    list(range(3)) + list(range(start_col, len(crime_sydney.columns)))
]

# Keep student-safety-related crime categories
keep_subcategories = {
    "Murder *",
    "Attempted murder",
    "Manslaughter *",
    "Abduction and kidnapping",
    "Domestic violence related assault",
    "Non-domestic violence related assault",
    "Sexual assault",
    "Sexual touching, sexual act and other sexual offences",
    "Intimidation, stalking and harassment",
    "Assault Police",
    "Break and enter dwelling",
    "Break and enter non-dwelling",
    "Motor vehicle theft",
    "Steal from dwelling",
    "Steal from motor vehicle",
    "Steal from person",
    "Steal from retail store",
    "Other theft",
    "Receiving or handling stolen goods",
    "Malicious damage to property",
    "Arson",
    "Robbery without a weapon",
    "Robbery with a firearm",
    "Robbery with a weapon not a firearm",
    "Dealing, trafficking in cannabis",
    "Dealing, trafficking in cocaine",
    "Dealing, trafficking in ecstasy",
    "Dealing, trafficking in narcotics",
    "Dealing, trafficking in amphetamines",
    "Manufacture drug",
    "Importing drugs",
    "Fraud",
    "Blackmail and extortion",
    "Trespass",
    "Offensive conduct",
    "Offensive language",
    "Coercive Control"
}

crime_filtered = crime_recent[
    crime_recent["Subcategory"].isin(keep_subcategories)
]

############### RESTRUCTURING ###############

# Convert from wide to long format
crime_long = crime_filtered.melt(
    id_vars=["Suburb", "Offence category", "Subcategory"],
    var_name="Date",
    value_name="Count"
)

# Convert dates to datetime
crime_long["Date"] = pd.to_datetime(
    crime_long["Date"],
    format="%b %Y"
)

############### FINAL SUMMARY ###############

print("\n=== FINAL DATASET SUMMARY ===")
print(f"Rows: {len(crime_long):,}")
print(f"Columns: {crime_long.shape[1]}")
print(f"Suburbs: {crime_long['Suburb'].nunique()}")
print(f"Crime Types: {crime_long['Subcategory'].nunique()}")
print(
    f"Date Range: {crime_long['Date'].min().date()} "
    f"to {crime_long['Date'].max().date()}"
)

############### SAVE CLEANED DATASET ###############

#crime_long.to_csv("datasets/crime_long.csv",index=False)
#print("\nSaved cleaned dataset to datasets/crime_long.csv")