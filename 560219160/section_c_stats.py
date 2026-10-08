import pandas as pd

bonds = pd.read_csv("clean_greater_sydney_rentalbond.csv")
suburbs = pd.read_csv("housing_scores.csv")
rent = "Weekly Rent ($)"
ppr = "Rent per Room ($)"

# keep only suburbs that got a score, then make one row per postcode
scored = suburbs.dropna(subset=["median_ppr"])
pc = scored.groupby("Postcode").first().reset_index()
pc = pc[["Postcode", "median_ppr", "n_bonds", "price_tier", "Suburb"]]
pc.columns = ["Postcode", "rent", "bonds", "tier", "name"]

# standardised names for some postcodes with popular name
better_names = {2000: "Sydney CBD", 2170: "Liverpool", 2145: "Westmead", 2148: "Blacktown",
                2560: "Campbelltown", 2765: "Riverstone", 2766: "Rooty Hill", 2760: "St Marys",
                2570: "Oran Park", 2557: "Gregory Hills", 2179: "Leppington", 2770: "Mount Druitt",
                2775: "Wisemans Ferry", 2010: "Darlinghurst", 2155: "Kellyville", 2750: "Penrith",
                2747: "Kingswood"}
for postcode, new_name in better_names.items():
    pc.loc[pc["Postcode"] == postcode, "name"] = new_name

# assigned price tier of its postcode 
bonds = bonds.merge(pc[["Postcode", "tier"]], on="Postcode", how="left")
# True/False column: is this lease a studio or 1-bedroom?
bonds["small"] = bonds["Bedrooms"] <= 1


def show(label, value):
    print(label, value)


# SUMMARY ANALYSIS - DESCRIPTIVE STATISTICS
print("DESCRIPTIVE STATISTICS")
show("Bonds in the cleaned dataset", len(bonds))
show("Years in the data", bonds["Year"].unique())
show("Postcodes in the cleaned dataset", bonds["Postcode"].nunique())
show("Postcodes with a score (30+ bonds)", len(pc))
show("Suburbs with a score", len(scored))
show("Suburbs in total", len(suburbs))

print("\nTABLE 1.1 - DESCRIPTIVE STATISTICS OF WEEKLY RENT")
print(bonds[[rent, ppr]].describe().round(1))
print("Skewness:")
print(bonds[[rent, ppr]].skew().round(2))

# GROUPED SUMMARIES - RENT BY NUMBER OF BEDROOMS
print("\nTABLE 1.2 (TOP ROWS) - BY NUMBER OF BEDROOMS (0 = studio)")
by_beds = bonds.groupby("Bedrooms")
print("Bonds:")
print(by_beds.size())
print("Rent per property (median):")
print(by_beds[rent].median())
print("Rent per room (median):")
m = by_beds[ppr].median()
print(m.round(1))
show("Saving per person, 1 -> 2 bedrooms ($)", round(m[1] - m[2], 1))
show("Saving per person, 2 -> 3 bedrooms ($)", round(m[2] - m[3], 1))

# GROUPED SUMMARIES - RENT BY DWELLING TYPE AND MONTH
print("\nTABLE 1.4 - BY DWELLING TYPE")
by_type = bonds.groupby("Dwelling Type")
print("Rent per room (median):")
print(by_type[ppr].median())
print("Rent per property (median):")
print(by_type[rent].median())
print("Mean bedrooms:")
print(by_type["Bedrooms"].mean().round(1))

print("\nTABLE 1.3 - BY MONTH")
by_month = bonds.groupby("Month")
print("Bonds:")
print(by_month.size())
print("Rent per room (median):")
month_ppr = by_month[ppr].median()
print(month_ppr)
show("February compared with April, rent per room (%)", round((month_ppr[2] / month_ppr[4] - 1) * 100, 1))

# GROUPED SUMMARIES - RENT BY PRICE TIER AND BEDROOMS
print("\nTABLE 1.2 (TIER ROWS) - RENT PER ROOM BY PRICE TIER AND BEDROOMS")
in_tiers = bonds.dropna(subset=["tier"])     # only bonds in the 218 scored postcodes
# pivot table
by_tier = in_tiers.pivot_table(index="tier", columns="Bedrooms", values=ppr, aggfunc="median")
print(by_tier.round(1))
print("Tier ranges - cheapest and dearest postcode in each tier ($ per room):")
print(pc.groupby("tier")["rent"].min().round(1))
print(pc.groupby("tier")["rent"].max().round(1))
print("Saving 1 -> 2 bedrooms in each tier ($):")
print((by_tier[1] - by_tier[2]).round(1))
# mean of a True/False column = proportion of True values
print("Leases that are studios or 1-bedrooms, by tier (%):")
print((in_tiers.groupby("tier")["small"].mean() * 100).round(1))

# DISTRIBUTION ANALYSIS (one value per postcode)
print("\nDISTRIBUTION ANALYSIS (218 postcodes)")
print("Median rent per room across postcodes ($):")
print(pc["rent"].describe().round(1))
show("Bonds per postcode: min", pc["bonds"].min())
show("Bonds per postcode: median", pc["bonds"].median())
show("Bonds per postcode: max", pc["bonds"].max())
show("Bonds per postcode: skewness", round(pc["bonds"].skew(), 2))

# VISUALISATION 1 - CHEAPEST AND MOST EXPENSIVE POSTCODES
print("\nVISUALISATION 1 (Figure 2.1)")
ranked = pc.sort_values("rent")
columns = ["Postcode", "name", "rent", "bonds"]
print("Ten cheapest postcodes:")
print(ranked.head(10)[columns].round(1))
print("Ten most expensive postcodes:")
print(ranked.tail(10)[columns].round(1))
show("Median of all postcodes - dashed line ($)", round(pc["rent"].median(), 1))
show("Most expensive divided by cheapest (times)", round(pc["rent"].max() / pc["rent"].min(), 2))
show("Fewest bonds among the ten most expensive", ranked.tail(10)["bonds"].min())

# VISUALISATION 2 - RENT PER ROOM BY NUMBER OF BEDROOMS
print("\nVISUALISATION 2 (Figure 2.2)")
show("Fall in rent per room, 1 -> 3 bedrooms (%)", round((1 - m[3] / m[1]) * 100, 1))
show("1-bedroom compared with a room in a 5-bedroom (times)", round(m[1] / m[5], 2))
show("Fewest bonds in a box (n)", by_beds.size().min())
show("Most bonds in a box (n)", by_beds.size().max())

# VISUALISATION 3 - PRICE, AVAILABILITY AND PROPERTY MIX
print("\nVISUALISATION 3 (Figure 2.3)")
# done with .rank() 
show("Spearman rho (bonds vs rent per room)", round(pc["bonds"].rank().corr(pc["rent"].rank()), 2))
show("Pearson r (bonds vs rent per room)", round(pc["bonds"].corr(pc["rent"]), 2))
inner = [2008, 2000, 2016, 2017]     # Chippendale, Sydney CBD, Redfern, Waterloo
rest = pc[~pc["Postcode"].isin(inner)]
show("Pearson r without the four inner-city postcodes", round(rest["bonds"].corr(rest["rent"]), 2))
show("Spearman rho without the four inner-city postcodes", round(rest["bonds"].rank().corr(rest["rent"].rank()), 2))

small_share = bonds.groupby("Postcode")["small"].mean() * 100
pc = pc.merge(small_share.rename("small_pct"), on="Postcode", how="left")
show("Spearman rho, property mix vs rent per room", round(pc["small_pct"].rank().corr(pc["rent"].rank()), 2))
mostly_small = pc[pc["small_pct"] >= 45]
show("Postcodes where 45%+ of leases are studios/1-beds", len(mostly_small))
show("... and how many of them are dearer than the median", (mostly_small["rent"] > pc["rent"].median()).sum())

cheaper = pc["rent"] < pc["rent"].median()
busier = pc["bonds"] >= pc["bonds"].median()
show("Cheaper than the median AND above-median bonds", (cheaper & busier).sum())

# INSIGHTS AND INTERPRETATION
print("\nINSIGHTS")
print("4-bedroom minus 6-bedroom rent per room in each tier ($):")
print((by_tier[4] - by_tier[6]).round(1))
four_beds = in_tiers[in_tiers["Bedrooms"] == 4]
six_beds = in_tiers[in_tiers["Bedrooms"] == 6]
show("4-bedroom leases that are in tier 5 (%)", round((four_beds["tier"] == 5).mean() * 100, 1))
show("6-bedroom leases that are in tier 5 (%)", round((six_beds["tier"] == 5).mean() * 100, 1))

# APPENDIX
print("\nAPPENDIX FIGURE 2.0 - DESCRIPTIVE STATISTICS (extra to Table 1.1)")
iqr = bonds[[rent, ppr]].quantile(0.75) - bonds[[rent, ppr]].quantile(0.25)
print("IQR:")
print(iqr)

print("\nAPPENDIX FIGURE 2.1 - same numbers as Table 1.2 top rows above")
print("APPENDIX FIGURE 2.3 - same numbers as Table 1.3 above")

print("\nAPPENDIX FIGURE 2.2 - POSTCODES BY PRICE AND AVAILABILITY")
show("Split at median rent per room ($)", round(pc["rent"].median(), 1))
show("Split at median bonds", pc["bonds"].median())
print(pd.crosstab(cheaper, busier, rownames=["cheaper"], colnames=["above-median bonds"]))

print("\nAPPENDIX FIGURE 2.4 - CHEAPER AND HIGH-AVAILABILITY POSTCODES (top 10 by bonds)")
best = pc[cheaper & busier].sort_values("bonds", ascending=False).head(10)
print(best[["Postcode", "name", "rent", "bonds"]].round(1))
