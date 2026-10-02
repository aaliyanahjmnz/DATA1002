import pandas as pd

##############################
# LOAD CLEANED POPULATION DATA
##############################

population = pd.read_csv(
    "datasets/suburb_population.csv"
)

population["Suburb"] = (
    population["Suburb"]
    .str.strip()
    .str.upper()
)

print(
    f"Population suburbs: {population['Suburb'].nunique()}"
)

##############################
# LOAD CRIME DATA
##############################

crime = pd.read_csv(
    "datasets/crime_long.csv"
)

crime["Date"] = pd.to_datetime(
    crime["Date"]
)


##############################
# KEEP ONLY 2021 CRIME DATA
##############################

crime = crime[
    crime["Date"].dt.year == 2021
]

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


print(f"Suburbs before threshold: {len(crime_rates)}")

##############################
# REMOVE VERY SMALL POPULATIONS
##############################

crime_rates = crime_rates[
    crime_rates["Population"] >= 1000
]

print(f"Suburbs after threshold: {len(crime_rates)}")

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