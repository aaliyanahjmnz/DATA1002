import pandas as pd


# ==============================
# 1. Read the original CSV file
# ==============================

df = pd.read_csv(
    "tsn-to-tz-mapping.csv",
    dtype={
        "TSN": "string",
        "TZ16_CODE": "string"
    }
)

print("Original number of rows:", len(df))


# ==============================
# 2. Clean column names
# ==============================

df.columns = df.columns.str.strip().str.upper()

df = df.rename(
    columns={
        "NAME": "STOP_NAME",
        "TRANSIT_STOP_TYPE": "STOP_TYPE",
        "TZ16_NAME": "TRAVEL_ZONE_NAME"
    }
)


# ==============================
# 3. Remove latitude and longitude
# ==============================

df = df.drop(
    columns=["LATITUDE", "LONGITUDE"],
    errors="ignore"
)


# ==============================
# 4. Clean text columns
# ==============================

text_columns = df.select_dtypes(
    include=["object", "string"]
).columns

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


# ==============================
# 5. Remove rows missing key data
# ==============================

required_columns = [
    "TSN",
    "STOP_NAME",
    "STOP_TYPE",
    "SUBURB",
    "TZ16_CODE"
]

df = df.dropna(subset=required_columns)


# ==============================
# 6. Standardise suburb names
# ==============================

# Display version
df["SUBURB"] = df["SUBURB"].str.title()

# Uppercase version for merging with group data
df["SUBURB_JOIN_KEY"] = df["SUBURB"].str.upper()


# ==============================
# 7. Remove exact duplicates
# ==============================

rows_before = len(df)

df = df.drop_duplicates().copy()

duplicates_removed = rows_before - len(df)


# ==============================
# 8. Classify transport modes
# ==============================

mode_map = {
    "Bus Stop": "Bus",
    "Train Station": "Train",
    "Train Station Platform": "Train",
    "Ferry Wharf": "Ferry",
    "Light Rail Station": "Light Rail"
}

df["MODE"] = df["STOP_TYPE"].map(mode_map)

df["MODE"] = df["MODE"].fillna("Other")


# ==============================
# 9. Identify primary access points
# ==============================

# A train platform is retained in the cleaned data,
# but it is not counted as a separate access point.

df["PRIMARY_ACCESS_POINT"] = (
    df["STOP_TYPE"] != "Train Station Platform"
)


# ==============================
# 10. Create indicator columns
# ==============================

df["BUS_STOP"] = (
    df["STOP_TYPE"] == "Bus Stop"
).astype(int)

df["TRAIN_STATION"] = (
    df["STOP_TYPE"] == "Train Station"
).astype(int)

df["TRAIN_PLATFORM"] = (
    df["STOP_TYPE"] == "Train Station Platform"
).astype(int)

df["FERRY_WHARF"] = (
    df["STOP_TYPE"] == "Ferry Wharf"
).astype(int)

df["LIGHT_RAIL_STATION"] = (
    df["STOP_TYPE"] == "Light Rail Station"
).astype(int)


# ==============================
# 11. Create a suburb summary
# ==============================

suburb_summary = (
    df.groupby("SUBURB_JOIN_KEY", as_index=False)
    .agg(
        SUBURB=("SUBURB", "first"),

        PRIMARY_ACCESS_POINTS=(
            "PRIMARY_ACCESS_POINT",
            "sum"
        ),

        BUS_STOPS=(
            "BUS_STOP",
            "sum"
        ),

        TRAIN_STATIONS=(
            "TRAIN_STATION",
            "sum"
        ),

        TRAIN_PLATFORMS=(
            "TRAIN_PLATFORM",
            "sum"
        ),

        FERRY_WHARVES=(
            "FERRY_WHARF",
            "sum"
        ),

        LIGHT_RAIL_STATIONS=(
            "LIGHT_RAIL_STATION",
            "sum"
        ),

        MODES_AVAILABLE=(
            "MODE",
            "nunique"
        ),

        TRAVEL_ZONE_COUNT=(
            "TZ16_CODE",
            "nunique"
        ),

        TOTAL_RECORDS=(
            "TSN",
            "count"
        )
    )
)


# ==============================
# 12. Calculate coverage score
# ==============================

# Percentile based on the number of primary access points
suburb_summary["STOP_COUNT_PERCENTILE"] = (
    suburb_summary["PRIMARY_ACCESS_POINTS"]
    .rank(method="average", pct=True)
    * 100
)

# 80% stop coverage + 20% transport-mode diversity
suburb_summary["STOP_COVERAGE_SCORE"] = (
    0.8 * suburb_summary["STOP_COUNT_PERCENTILE"]
    + 0.2 * (
        suburb_summary["MODES_AVAILABLE"] / 4 * 100
    )
).round(1)


# ==============================
# 13. Rank suburbs
# ==============================

suburb_summary = suburb_summary.sort_values(
    by=[
        "STOP_COVERAGE_SCORE",
        "PRIMARY_ACCESS_POINTS"
    ],
    ascending=[False, False]
).reset_index(drop=True)

suburb_summary.insert(
    0,
    "COVERAGE_RANK",
    suburb_summary.index + 1
)


# ==============================
# 14. Save the cleaned files
# ==============================

df.to_csv(
    "clean_transport_stops.csv",
    index=False,
    encoding="utf-8-sig"
)

suburb_summary.to_csv(
    "suburb_transport_summary.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==============================
# 15. Show cleaning results
# ==============================

print("Rows after cleaning:", len(df))
print("Exact duplicates removed:", duplicates_removed)
print("Number of suburbs:", len(suburb_summary))
print("Latitude and longitude removed successfully.")

print("\nFiles created:")
print("1. clean_transport_stops.csv")
print("2. suburb_transport_summary.csv")
