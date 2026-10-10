import pandas as pd

# Load datasets
crime = pd.read_csv("datasets/scores/crime_scores.csv")
medical = pd.read_csv("datasets/scores/medical_care_suburb_scores.csv")
price = pd.read_csv("datasets/scores/price_score.csv")
amenities = pd.read_csv("datasets/scores/building_scores_by_suburb.csv")
transport = pd.read_csv("datasets/scores/greater_sydney_transport_scores.csv")
greater_sydney = pd.read_csv("datasets/greater_sydney_suburbs.csv")

for df_ in [crime, medical, price, amenities, transport, greater_sydney]:
    df_["Suburb"] = (
        df_["Suburb"]
        .str.strip()
        .str.upper()
    )

# Rename score columns
crime = crime[["Suburb", "Crime_Score"]].rename(
    columns={"Crime_Score": "crime"}
)

medical = medical[["Suburb", medical.columns[1]]].rename(
    columns={medical.columns[1]: "medical"}
)

price = price[["Suburb", price.columns[1]]].rename(
    columns={price.columns[1]: "price"}
)

amenities = amenities[["Suburb", "sports_and_amenities_score"]].rename(
    columns={"sports_and_amenities_score": "amenities"}
)

transport = transport[["Suburb", "TRANSPORT_SCORE_10"]].rename(
    columns={"TRANSPORT_SCORE_10": "transport"}
)

# Master suburb list
df = greater_sydney[["Suburb"]]

# Merge scores
df = df.merge(crime, on="Suburb", how="left")
df = df.merge(medical, on="Suburb", how="left")
df = df.merge(price, on="Suburb", how="left")
df = df.merge(amenities, on="Suburb", how="left")
df = df.merge(transport, on="Suburb", how="left")

# Fill missing values with column averages
for col in ["crime", "medical", "price", "amenities", "transport"]:
    df[col] = df[col].fillna(df[col].mean())

# Reverse price tier so higher = more affordable
df["price"] = 12 - df["price"]

# Student Liveability Index
df["Student_Liveability_Index"] = (
    df["price"] * 0.40 +
    df["crime"] * 0.25 +
    df["transport"] * 0.15 +
    df["amenities"] * 0.10 +
    df["medical"] * 0.10
).round(2)

# Sort
df = df.sort_values(
    "Student_Liveability_Index",
    ascending=False
)

for col in ["crime", "medical", "price", "amenities", "transport"]:
    df[col] = df[col].fillna(df[col].mean()).round(2)

# Save
df.to_csv(
    "datasets/scores/student_liveability_index_scores.csv",
    index=False
)

print(df.head(10))

# Get top 10 suburbs by SLI
top10 = (
    df.nlargest(10, "Student_Liveability_Index")
    .copy()
)

# Add ranking column
top10.insert(0, "Rank", range(1, len(top10) + 1))

# Round values
score_cols = [
    "Student_Liveability_Index",
    "price",
    "crime",
    "transport",
    "amenities",
    "medical"
]

top10[score_cols] = top10[score_cols].round(2)

# Save CSV
top10.to_csv(
    "datasets/scores/top_10_suburbs.csv",
    index=False
)

print(top10)
