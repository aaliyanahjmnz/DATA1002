import pandas as pd

##############################
# LOAD CRIME DATA
##############################

crime = pd.read_csv("datasets/crime_long.csv")

crime_suburbs = set(
    crime["Suburb"]
    .astype(str)
    .str.strip()
    .str.upper()
    .unique()
)

##############################
# LOAD POPULATION DATA
##############################

population = pd.read_csv(
    "datasets/2021Census_G01_NSW_SAL.csv"
)

population = population[
    ["SAL_CODE_2021", "Tot_P_P"]
]

##############################
# LOAD SUBURB LOOKUP
##############################

lookup = pd.read_excel(
    "metadata/2021SAL.xlsx",
    sheet_name="2021_ASGS_Non_ABS_Structures"
)

lookup = lookup[
    lookup["ASGS_Structure"] == "SAL"
]

lookup = lookup[
    ["Census_Code_2021", "Census_Name_2021"]
]

lookup = lookup.rename(
    columns={
        "Census_Code_2021": "SAL_CODE_2021",
        "Census_Name_2021": "Suburb"
    }
)

##############################
# STANDARDISE NAMES
##############################

lookup["Suburb"] = (
    lookup["Suburb"]
    .astype(str)
    .str.strip()
    .str.upper()
    .str.replace(r"\s*\([^)]*\)", "", regex=True)
)

duplicates = [
    'DARLINGTON',
    'DURAL',
    'ELDERSLIE',
    'ENMORE',
    'GREENDALE',
    'KINGSWOOD',
    'LANSDOWNE',
    'LILLI PILLI',
    'LONG POINT',
    'NELSON',
    'PUNCHBOWL',
    'SILVERWATER',
    'ST CLAIR',
    'SUMMER HILL',
    'THE ROCKS'
]

##############################
# MERGE LOOKUP + POPULATION
##############################

suburb_population = population.merge(
    lookup,
    on="SAL_CODE_2021",
    how="inner"
)

suburb_population = suburb_population[
    ["Suburb", "Tot_P_P"]
]

suburb_population = suburb_population.rename(
    columns={
        "Tot_P_P": "Population"
    }
)

##############################
# KEEP ONLY CRIME SUBURBS
##############################

suburb_population = suburb_population[
    suburb_population["Suburb"].isin(crime_suburbs)
]

##############################
# SORT & SAVE
##############################

suburb_population = suburb_population.sort_values(
    "Suburb"
)

suburb_population.to_csv(
    "datasets/suburb_population.csv",
    index=False
)

suburb_population = (
    suburb_population
    .groupby("Suburb", as_index=False)
    ["Population"]
    .sum()
)