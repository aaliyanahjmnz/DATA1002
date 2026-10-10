import pandas as pd

# Load data
crime_rates = pd.read_csv("560606784/datasets/crime_rates.csv")
crime_long = pd.read_csv("560606784/datasets/crime_long.csv")

# --- 1. Crime Rate Score (70%) ---
min_rate = crime_rates["Crime Rate per 1000"].min()
max_rate = crime_rates["Crime Rate per 1000"].max()
crime_rates["rate_score"] = 10 * (1 - (crime_rates["Crime Rate per 1000"] - min_rate) / (max_rate - min_rate))

# --- 2. Composition Score (20%) ---
category_map = {
    "Homicide": "Violent",
    "Assault": "Violent",
    "Sexual offences": "Violent",
    "Abduction and kidnapping": "Violent",
    "Robbery": "Violent",
    "Theft": "Property",
    "Malicious damage to property": "Property",
    "Arson": "Property",
    "Intimidation, stalking and harassment": "Harassment",
    "Coercive Control": "Harassment",
    "Drug offences": "Drug",
    "Disorderly conduct": "Public Order"
}

severity = {
    "Violent": 1.0,
    "Harassment": 0.8,
    "Property": 0.5,
    "Drug": 0.4,
    "Public Order": 0.2
}

crime_long["Crime_Group"] = crime_long["Offence category"].map(category_map).fillna("Other")

group_counts = crime_long.groupby(["Suburb", "Crime_Group"])["Count"].sum().reset_index()
totals = group_counts.groupby("Suburb")["Count"].sum().rename("total")
group_counts = group_counts.merge(totals, on="Suburb")
group_counts["prop"] = group_counts["Count"] / group_counts["total"].replace(0, 1)
group_counts["weighted"] = group_counts["prop"] * group_counts["Crime_Group"].map(lambda x: severity.get(x, 0.2))

risk = group_counts.groupby("Suburb")["weighted"].sum().rename("risk")
composition = (1 - risk).clip(lower=0, upper=1) * 10
composition = composition.rename("composition_score")

# --- 3. Consistency Score (10%) ---
monthly = crime_long.groupby(["Suburb", "Date"])["Count"].sum().reset_index()
sd = monthly.groupby("Suburb")["Count"].std().fillna(0)

min_sd = sd.min()
max_sd = sd.max()
if max_sd == min_sd:
    consistency_score = pd.Series(10, index=sd.index)
else:
    consistency_score = 10 * (1 - (sd - min_sd) / (max_sd - min_sd))

consistency_score = consistency_score.rename("consistency_score")

# --- Final Score ---
result = crime_rates[["Suburb", "rate_score"]].merge(composition, on="Suburb", how="left")
result = result.merge(consistency_score, on="Suburb", how="left")

result = result.fillna(0)

result["Crime_Score"] = (
    0.70 * result["rate_score"] +
    0.20 * result["composition_score"] +
    0.10 * result["consistency_score"]
).round(2)

result = result[["Suburb", "Crime_Score"]].sort_values("Crime_Score", ascending=False)
result.to_csv("crime_score.csv", index=False)

print(result.head())
