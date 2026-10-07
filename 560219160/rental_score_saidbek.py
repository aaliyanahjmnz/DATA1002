import pandas as pd 
df = pd.read_csv("housing_scores.csv")
df["price_tier"] = pd.to_numeric(df["price_tier"])*2
data = df[["Suburb", "price_tier"]]
data.to_csv("price_score.csv", index=False)