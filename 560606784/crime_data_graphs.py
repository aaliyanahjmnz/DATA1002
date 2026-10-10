import matplotlib.pyplot as plt
import pandas as pd

############### LOAD IN DATA ###############

# Load the cleaned crime data
crime_data = pd.read_csv("560606784/datasets/crime_long.csv")

# Convert the "Date" column to datetime format
crime_data["Date"] = pd.to_datetime(crime_data["Date"])

# Load the population data
population_data = pd.read_csv("datasets/suburb_population.csv")

# Load the crime rates data
crime_rates_data = pd.read_csv("560606784/datasets/crime_rates.csv")

############### SUMMARY STATISTICS ###############

# Descriptive statistics of the crime data
print("\n=== CRIME DATA DESCRIPTIVE STATISTICS ===")
print(crime_data["Count"].describe())

# Grouped Summaries
print("\n=== CRIME DATA GROUPED SUMMARIES ===")

## By Suburb
print("\nCrime by Suburb:")
crime_by_suburb = (
    crime_data.groupby("Suburb")["Count"]
    .sum()
    .sort_values(ascending=False)
)

print(crime_by_suburb.head(10))

## By Year
print("\nCrime by Year:")
crime_data["Year"] = crime_data["Date"].dt.year

crime_by_year = (
    crime_data.groupby("Year")["Count"]
    .sum()
)

print(crime_by_year.head(10))

##################### PLOT 1: LOWEST CRIME RATES BY SUBURB #####################

# Assign x and y values for the bar chart
x = crime_rates_data["Suburb"].tail(10)
y = crime_rates_data["Crime Rate per 1000"].tail(10)

# Make bar chart
plt.barh(x, y, color='skyblue')

# Add labels and title
plt.xticks(rotation=45, ha='right')
plt.title("Lowest Crime Rates by Suburb in Greater Sydney (2021)")
plt.xlabel("Crime Rate per 1000 Residents")
plt.ylabel("Suburb")
plt.tight_layout()

for i, v in enumerate(y):
    plt.text(
        v + 0.1,
        i,
        f"{v:.1f}",
        va="center"
    )

##################### PLOT 2: CRIME COMPOSITION OF LOWEST CRIME RATES #####################

# Assign a mapping of offence categories to broader crime groups
category_mapping = {
    # Violent Crime
    "Homicide": "Violent Crime",
    "Assault": "Violent Crime",
    "Sexual offences": "Violent Crime",
    "Abduction and kidnapping": "Violent Crime",
    "Robbery": "Violent Crime",

    # Property Crime
    "Theft": "Property Crime",
    "Malicious damage to property": "Property Crime",
    "Arson": "Property Crime",

    # Drug Crime
    "Drug offences": "Drug Crime",

    # Personal Safety
    "Intimidation, stalking and harassment": "Harassment / Control",
    "Coercive Control": "Harassment / Control",

    # Public Order
    "Disorderly conduct": "Public Order",

    # Other
    "Blackmail and extortion": "Other"
}

# Safest suburbs (based on lowest crime rates graph)
safest_suburbs = [
    "CHATSWOOD WEST",
    "EAST RYDE",
    "NORTH EPPING",
    "DAVIDSON",
    "BARDWELL VALLEY",
    "BONNET BAY",
    "CHERRYBROOK",
    "EAST KILLARA",
    "WILLOUGHBY EAST",
    "BLAIR ATHOL"
]

safe_data = crime_data[crime_data["Suburb"].isin(safest_suburbs)].copy()

# Map categories to broader crime groups
safe_data["Crime Group"] = safe_data["Offence category"].map(category_mapping)

# Aggregate
composition = (safe_data.groupby(["Suburb", "Crime Group"])["Count"].sum().reset_index())

# Convert to Percentages
composition_pivot = (
    composition
    .pivot(
        index="Suburb",
        columns="Crime Group",
        values="Count"
    )
    .fillna(0)
)

composition_percent = (
    composition_pivot.div(
        composition_pivot.sum(axis=1),
        axis=0
    ) * 100
)

# Plot
composition_percent.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 6)
)

plt.title(
    "Crime Composition of the Safest Greater Sydney Suburbs"
)

plt.xlabel("Suburb")
plt.ylabel("Percentage of Total Crime")

plt.legend(
    title="Crime Category",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()

##################### PLOT 3: CRIME RATE VS VIOLENT CRIME #####################

# Get safest suburbs based on lowest crime rates
safest_suburbs = (
    crime_rates_data
    .sort_values("Crime Rate per 1000")
    .head(10)["Suburb"]
    .tolist()
)

# Aggregate crime data per year
crime_data["Year"] = pd.to_datetime(
    crime_data["Date"]
).dt.year

safe_data = crime_data[
    crime_data["Suburb"].isin(safest_suburbs)
].copy()

annual_crime = (
    safe_data
    .groupby(["Suburb", "Date"])["Count"]
    .sum()
    .reset_index()
)

# Create boxplot
plt.figure(figsize=(10, 6))

annual_crime.boxplot(
    column="Count",
    by="Suburb",
    grid=False,
    rot=45
)

plt.title(
    "Monthly Crime Distribution in the Safest Greater Sydney Suburbs"
)

plt.suptitle("")  # Removes automatic Pandas title

plt.xlabel("Suburb")
plt.ylabel("Annual Recorded Crime")

plt.tight_layout()