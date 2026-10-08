import pandas as pd
import numpy as np

# Load suburb list
crime = pd.read_csv("datasets/scores/crime_scores.csv")

# Reproducible random values
np.random.seed(1002)

# Mock transport scores
transport = pd.DataFrame({
    "Suburb": crime["Suburb"],
    "Transport_Score": np.random.uniform(4, 10, len(crime)).round(2)
})

# Mock amenities scores
amenities = pd.DataFrame({
    "Suburb": crime["Suburb"],
    "Amenities_Score": np.random.uniform(4, 10, len(crime)).round(2)
})

transport.to_csv("datasets/transport_scores.csv", index=False)
amenities.to_csv("datasets/amenities_scores.csv", index=False)

print("Mock files generated")

