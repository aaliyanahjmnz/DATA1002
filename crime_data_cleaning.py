import pandas as pd

crime = pd.read_csv("datasets/SuburbData26Q1.csv")
sydney = pd.read_csv("greater_sydney_suburbs.csv")

############### GENERAL CLEANING ###############

# Remove rows not containing greater Sydney suburbs
crime["Suburb"] = crime["Suburb"].str.strip().str.upper()
sydney["Suburb"] = sydney["Suburb"].str.strip().str.upper()

sydney_suburbs = set(sydney["Suburb"])

crime_sydney = crime[crime["Suburb"].isin(sydney_suburbs)]

# Removing n/a values
crime_sydney = crime_sydney.dropna(subset=["Suburb"])

# Removing duplicate rows
crime_sydney = crime_sydney.drop_duplicates()

############### FILTERING ###############

# Keep only columns with crime data from Jan 2021 onwards
start_col = crime_sydney.columns.get_loc("Jan 2021") # Find the position of Jan 2021

crime_recent = crime_sydney.iloc[:, list(range(3)) + list(range(start_col, len(crime_sydney.columns)))] # Keep identifier columns + Jan 2021 onwards

# Keep crimes that are inherent to student safety and security
keep_subcategories = {
    "Murder *",
    "Attempted murder",
    "Manslaughter *",
    "Abduction and kidnapping",
    "Domestic violence related assault",
    "Non-domestic violence related assault",
    "Sexual assault",
    "Sexual touching, sexual act and other sexual offences",
    "Intimidation, stalking and harassment",
    "Assault Police",
    "Break and enter dwelling",
    "Break and enter non-dwelling",
    "Motor vehicle theft",
    "Steal from dwelling",
    "Steal from motor vehicle",
    "Steal from person",
    "Steal from retail store",
    "Other theft",
    "Receiving or handling stolen goods",
    "Malicious damage to property",
    "Arson",
    "Robbery without a weapon",
    "Robbery with a firearm",
    "Robbery with a weapon not a firearm",
    "Dealing, trafficking in cannabis",
    "Dealing, trafficking in cocaine",
    "Dealing, trafficking in ecstasy",
    "Dealing, trafficking in narcotics",
    "Dealing, trafficking in amphetamines",
    "Manufacture drug",
    "Importing drugs",
    "Fraud",
    "Blackmail and extortion",
    "Trespass",
    "Offensive conduct",
    "Offensive language",
    "Coercive Control"
}

crime_filtered = crime_recent[
    crime_recent["Subcategory"].isin(keep_subcategories)
]

############### RESTRUCTURING ###############

# Reshape the dataset from wide to long format
crime_long = crime_filtered.melt(
    id_vars=["Suburb", "Offence category", "Subcategory"],
    var_name="Date",
    value_name="Count"
)

# Convert the "Date" column to datetime format
crime_long["Date"] = pd.to_datetime(
    crime_long["Date"],
    format="%b %Y"
)

############### SAVING CLEANED DATASET ###############
crime_long.to_csv("datasets/crime_long.csv", index=False) #saving the cleaned dataset to a new CSV file


