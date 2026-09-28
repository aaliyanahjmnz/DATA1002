import matplotlib.pyplot as plt
import pandas as pd

# Load the cleaned crime data
crime_data = pd.read_csv("datasets/crime_long.csv")

crime_data["Date"] = pd.to_datetime(crime_data["Date"])

# Descriptive statistics of the crime data
print("\n=== CRIME DATA DESCRIPTIVE STATISTICS ===")
print(crime_data["Count"].describe())

# Grouped Summaries
print("\n=== CRIME DATA GROUPED SUMMARIES ===")

# By Suburb
print("\nCrime by Suburb:")
crime_by_suburb = (
    crime_data.groupby("Suburb")["Count"]
    .sum()
    .sort_values(ascending=False)
)

print(crime_by_suburb.head(10))

# By Year
print("\nCrime by Year:")
crime_data["Year"] = crime_data["Date"].dt.year

crime_by_year = (
    crime_data.groupby("Year")["Count"]
    .sum()
)

print(crime_by_year.head(10))

##################### PLOT 1: LOWEST CRIME RATES BY SUBURB #####################

##################### PLOT 2: CRIME OVER TIME #####################

##################### PLOT 3: TOTAL CRIME OVER TIME #####################