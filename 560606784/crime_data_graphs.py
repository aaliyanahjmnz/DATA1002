import matplotlib.pyplot as plt
import pandas as pd

############### LOAD IN DATA ###############

# Load the cleaned crime data
crime_data = pd.read_csv("datasets/crime_long.csv")

# Convert the "Date" column to datetime format
crime_data["Date"] = pd.to_datetime(crime_data["Date"])

# Load the population data
population_data = pd.read_csv("datasets/suburb_population.csv")

# Load the crime rates data
crime_rates_data = pd.read_csv("datasets/crime_rates.csv")

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
plt.bar(x, y, color='skyblue')

# Add labels and title
plt.xticks(rotation=45, ha='right')
plt.title("Top 10 Suburbs with Lowest Crime Rates")
plt.xlabel("Suburb")
plt.ylabel("Crime Rate per 1000 Residents")
plt.tight_layout()

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
    "GILEAD",
    "DANGAR ISLAND",
    "WESTLEIGH",
    "WILLOUGHBY EAST",
    "KIRKHAM",
    "ST IVES CHASE"
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

# Violent crimes
violent_categories = [
    "Homicide",
    "Assault",
    "Sexual offences",
    "Robbery",
    "Abduction and kidnapping"
]

# Violent crime percentage
safest_suburbs = (
    crime_rates_data
    .sort_values("Crime Rate per 1000")
    .head(20)["Suburb"]
    .tolist()
)

safe_data = crime_data[
    crime_data["Suburb"].isin(safest_suburbs)
].copy()

total_crime = (
    safe_data
    .groupby("Suburb")["Count"]
    .sum()
    .reset_index()
    .rename(columns={"Count": "Total Crime"})
)

violent_crime = (
    safe_data[
        safe_data["Offence category"].isin(
            violent_categories
        )
    ]
    .groupby("Suburb")["Count"]
    .sum()
    .reset_index()
    .rename(columns={"Count": "Violent Crime"})
)

violent_summary = total_crime.merge(
    violent_crime,
    on="Suburb",
    how="left"
)

violent_summary["Violent Crime"] = (
    violent_summary["Violent Crime"]
    .fillna(0)
)

violent_summary["Violent Crime %"] = (
    violent_summary["Violent Crime"]
    /
    violent_summary["Total Crime"]
) * 100

# Add crime rates
violent_summary = violent_summary.merge(
    crime_rates_data[
        ["Suburb", "Crime Rate per 1000"]
    ],
    on="Suburb"
)

# Plot

plt.figure(figsize=(8, 6))

plt.scatter(
    violent_summary["Crime Rate per 1000"],
    violent_summary["Violent Crime %"],
    s=100
)

for _, row in violent_summary.iterrows():
    plt.annotate(
        row["Suburb"],
        (
            row["Crime Rate per 1000"],
            row["Violent Crime %"]
        ),
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.xlabel("Crime Rate per 1,000 Residents")
plt.ylabel("Violent Crime (%)")

plt.title(
    "Crime Rate vs Violent Crime Proportion\nin the Safest Greater Sydney Suburbs"
)

plt.tight_layout()
plt.show()