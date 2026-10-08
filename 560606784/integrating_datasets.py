import pandas as pd

# Load datasets
crime = pd.read_csv("datasets/scores/crime_scores.csv")
medical = pd.read_csv("datasets/scores/medical_care_suburb_scores.csv")
price = pd.read_csv("datasets/scores/price_score.csv")
amenities = pd.read_csv("datasets/scores/amenities_scores.csv")
transport = pd.read_csv("datasets/scores/transport_scores.csv")
greater_sydney = pd.read_csv("greater_sydney_suburbs.csv")

for df_ in [crime, medical, price, amenities, transport, greater_sydney]:
    df_["Suburb"] = (
        df_["Suburb"]
        .str.strip()
        .str.upper()
    )

# Rename score columns
crime = crime.rename(columns={"Crime_Score": "crime"})
medical = medical.rename(columns={medical.columns[1]: "medical"})
price = price.rename(columns={price.columns[1]: "price"})
amenities = amenities.rename(columns={amenities.columns[1]: "amenities"})
transport = transport.rename(columns={transport.columns[1]: "transport"})

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