import pandas as pd

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

# Keep only suburb records
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
# MERGE POPULATION + SUBURB
##############################

population = population.merge(
    lookup,
    on="SAL_CODE_2021",
    how="inner"
)

population["Suburb"] = (
    population["Suburb"]
    .str.strip()
    .str.upper()
)

population = population.rename(
    columns={
        "Tot_P_P": "Population"
    }
)

##############################
# LOAD CRIME DATA
##############################

crime = pd.read_csv(
    "datasets/crime_long.csv"
)

crime["Suburb"] = (
    crime["Suburb"]
    .str.strip()
    .str.upper()
)

##############################
# TOTAL CRIME BY SUBURB
##############################

crime_by_suburb = (
    crime.groupby("Suburb")["Count"]
    .sum()
    .reset_index()
)

##############################
# MERGE CRIME + POPULATION
##############################

crime_rates = crime_by_suburb.merge(
    population[["Suburb", "Population"]],
    on="Suburb",
    how="inner"
)

##############################
# CALCULATE CRIME RATE
##############################

crime_rates["Crime Rate per 1000"] = (
    crime_rates["Count"] /
    crime_rates["Population"]
) * 1000

##############################
# SORT RESULTS
##############################

crime_rates = crime_rates.sort_values(
    "Crime Rate per 1000",
    ascending=False
)

##############################
# OUTPUT
##############################

print("\n=== TOP 20 HIGHEST CRIME RATES ===")
print(
    crime_rates[
        ["Suburb", "Count", "Population", "Crime Rate per 1000"]
    ].head(20)
)

print("\n=== TOP 20 LOWEST CRIME RATES ===")
print(
    crime_rates[
        ["Suburb", "Count", "Population", "Crime Rate per 1000"]
    ].tail(20)
)

##############################
# SAVE
##############################

crime_rates.to_csv(
    "datasets/crime_rates.csv",
    index=False
)

print("\nSaved to datasets/crime_rates.csv")