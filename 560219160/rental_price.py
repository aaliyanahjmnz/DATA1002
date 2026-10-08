import pandas as pd
import numpy as np
import openpyxl

df = pd.read_excel("rentalbond_2025_DIRTY_practice.xlsx", sheet_name="Year 2025 Rental Bond Lodgments",header=2) #
great_syd = pd.read_csv("greater_sydney_suburbs.csv")
pcodes_lookup = pd.read_csv("postcodes-lookup.csv")

pcod_sub = pcodes_lookup.columns[1]

#standardising names 
df.columns = df.columns.str.strip().str.title()
great_syd["Suburb"] = great_syd["Suburb"].str.strip().str.title()
pcodes_lookup.columns = pcodes_lookup.columns.str.strip()
pcodes_lookup["Suburb"] = pcodes_lookup["Suburb"].str.strip().str.title()

# General Filtering 
nsw = pcodes_lookup[pcodes_lookup["State"] == "NSW"]

#merged greater sydney with lookup dataset
great_syd = great_syd.merge(nsw[["Suburb", "Postcode"]], on="Suburb", how="left")

#cleaning , data conversion
great_syd = great_syd.dropna(subset=["Postcode"])
great_syd["Postcode"] = great_syd["Postcode"].astype(int)
# North Sydney: lookup only has PO box postcodes (2055, 2059); residential is 2060
great_syd.loc[great_syd["Suburb"] == "North Sydney", "Postcode"] = 2060
great_syd = great_syd.drop_duplicates(subset=["Suburb", "Postcode"])
p = great_syd["Postcode"]
great_syd = great_syd[p.between(2000, 2234) | p.between(2555, 2574) | p.between(2740, 2786)]

#merging suburbs with same postcode (one row per postcode)
pc_labels = great_syd.groupby("Postcode")["Suburb"].apply(" / ".join).reset_index()
#Extract postcode from text
df["Postcode"] = pd.to_numeric(df["Postcode"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
# merged df with postcode labels
df = df.merge(pc_labels, on="Postcode", how="inner")


#CLEANING 
df = df.dropna(axis="columns" , how="all").dropna(how="all").dropna(thresh=2)
date_col = "Lodgement Date"   
df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, format="mixed", errors="coerce")
df["Postcode"] = df["Postcode"].astype(int)
dw_type = "Dwelling Type"
price = "Weekly Rent ($)"
df[dw_type] = df[dw_type].str.strip().str.upper()
mapping_dw = {"F":"Flat","FLAT":"Flat",
              "H":"House","HOUSE":"House",
              "U":"Unknown","UNKNOWN":"Unknown","1":"Unknown","P":"Unknown","G":"Unknown","4":"Unknown","3":"Unknown",
              "I":"Unknown","Y":"Unknown","Z":"Unknown","X":"Unknown","R":"Unknown",
              "T":"Townhouse","TOWNHOUSE":"Townhouse",
              "O":"Other","OTHER":"Other"
              }
df[dw_type] = df[dw_type].replace(mapping_dw)

bednum_col = "Bedrooms"
pd.set_option("display.max_rows", None)
beds_num = pd.to_numeric(df[bednum_col].astype(str).str.replace("$", "", regex=False),errors="coerce")
rent_num = pd.to_numeric(df[price].astype(str).str.replace("$", "", regex=False), errors="coerce")
swapped = (beds_num >= 150) & rent_num.between(0, 20)
df.loc[swapped, price]   = beds_num[swapped]
df.loc[swapped, bednum_col] = rent_num[swapped]
s = df[bednum_col].astype(str).str.strip().str.lower()
s = s.replace({"studio": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5"})
s = s.str.extract(r"^(-?\d+(?:\.\d+)?)")[0]
num = pd.to_numeric(s, errors="coerce")
num[~num.between(0, 6)] = np.nan
df[bednum_col] = num

df[price] = df[price].astype(str).str.replace(r"[^\d.]", "", regex=True)
df[price] = pd.to_numeric(df[price], errors="coerce")
df = df.dropna(subset=[price])

###TRANSFORMATION

rooms = df[bednum_col].replace(0, 1)                  # studio counts as 1 room
df["Rent per Room ($)"] = df[price] / rooms          
df = df[df["Rent per Room ($)"].between(100, 1500)] 
rooms = df[bednum_col].replace(0, 1)              
df["Year"]  = df[date_col].dt.year.astype("Int64")
df["Month"] = df[date_col].dt.month.astype("Int64")
df["Day"]   = df[date_col].dt.day.astype("Int64")

# Filter Year 
df = df[(df["Year"] == 2025)]

### Liveablity scores

pcode_price = df.groupby("Postcode").agg(
    median_ppr=("Rent per Room ($)", "median"),
    n_bonds=("Rent per Room ($)", "size")
).reset_index()
pcode_price = pcode_price[pcode_price["n_bonds"] >= 30] 
print("Postcodes kept:", len(pcode_price))
pcode_price["price_tier"] = pd.qcut(pcode_price["median_ppr"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
pcode_price["avail_tier"] = pd.qcut(pcode_price["n_bonds"], 5, labels=[1, 2, 3, 4, 5]).astype(int)

# File 1: cleaned data for submission
df.to_csv("clean_greater_sydney_rentalbond.csv", index=False)

# File 2: for Liveability score 
housing = great_syd.merge(
    pcode_price[["Postcode", "median_ppr", "n_bonds", "price_tier", "avail_tier"]],
    on="Postcode", how="left")
housing = (housing.sort_values("n_bonds", ascending=False, na_position="last")
                  .drop_duplicates(subset="Suburb", keep="first")
                  .sort_values("Suburb"))
 
housing.to_csv("housing_scores.csv", index=False)


