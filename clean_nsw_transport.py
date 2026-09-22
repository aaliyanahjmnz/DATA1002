"""Clean the TfNSW TSN-to-TZ16 data and summarise transport access by suburb.

Run:
    python clean_nsw_transport.py tsn-to-tz-mapping.csv

Outputs:
    clean_transport_stops.csv
    suburb_transport_summary.csv
"""

import argparse
from pathlib import Path

import pandas as pd


def clean_transport_data(input_file: str, output_folder: str = "cleaned_output"):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Read the original CSV.
    df = pd.read_csv(input_file, dtype={"TSN": "string", "TZ16_CODE": "string"})
    original_rows = len(df)

    # 2. Standardise column names.
    df.columns = df.columns.str.strip().str.upper()
    df = df.rename(
        columns={
            "NAME": "STOP_NAME",
            "TRANSIT_STOP_TYPE": "STOP_TYPE",
            "TZ16_NAME": "TRAVEL_ZONE_NAME",
        }
    )

    # 3. Trim repeated spaces in all text columns.
    text_columns = df.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # 4. Create a consistent suburb key for merging with group data.
    df["SUBURB_JOIN_KEY"] = df["SUBURB"].str.upper()
    df["SUBURB"] = df["SUBURB"].str.title()

    # 5. Convert coordinates to numeric values.
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")

    # Broad NSW boundary check. Invalid values are flagged instead of silently removed.
    df["COORDINATE_VALID"] = (
        df["LATITUDE"].between(-38.0, -28.0)
        & df["LONGITUDE"].between(140.5, 154.5)
    )

    # 6. Remove exact duplicate rows. Do not remove stops merely because they have
    # similar names: stops on opposite sides of a road are separate valid records.
    df = df.drop_duplicates().copy()

    # 7. Group the original stop types into transport modes.
    mode_map = {
        "Bus Stop": "Bus",
        "Train Station": "Train",
        "Train Station Platform": "Train",
        "Ferry Wharf": "Ferry",
        "Light Rail Station": "Light Rail",
    }
    df["MODE"] = df["STOP_TYPE"].map(mode_map).fillna("Other")

    # Platforms are useful records, but they should not be counted as separate
    # public access points when the train station itself is already counted.
    df["PRIMARY_ACCESS_POINT"] = df["STOP_TYPE"].ne("Train Station Platform")

    # 8. Create indicator columns for an easy suburb-level aggregation.
    df["BUS_STOP"] = df["STOP_TYPE"].eq("Bus Stop").astype(int)
    df["TRAIN_STATION"] = df["STOP_TYPE"].eq("Train Station").astype(int)
    df["TRAIN_PLATFORM"] = df["STOP_TYPE"].eq("Train Station Platform").astype(int)
    df["FERRY_WHARF"] = df["STOP_TYPE"].eq("Ferry Wharf").astype(int)
    df["LIGHT_RAIL_STATION"] = df["STOP_TYPE"].eq("Light Rail Station").astype(int)

    # 9. Aggregate the cleaned data by suburb.
    summary = (
        df.groupby("SUBURB_JOIN_KEY", as_index=False)
        .agg(
            SUBURB=("SUBURB", "first"),
            PRIMARY_ACCESS_POINTS=("PRIMARY_ACCESS_POINT", "sum"),
            BUS_STOPS=("BUS_STOP", "sum"),
            TRAIN_STATIONS=("TRAIN_STATION", "sum"),
            TRAIN_PLATFORMS=("TRAIN_PLATFORM", "sum"),
            FERRY_WHARVES=("FERRY_WHARF", "sum"),
            LIGHT_RAIL_STATIONS=("LIGHT_RAIL_STATION", "sum"),
            MODES_AVAILABLE=("MODE", "nunique"),
            TRAVEL_ZONE_COUNT=("TZ16_CODE", "nunique"),
            ALL_RECORDS=("TSN", "size"),
            CENTROID_LATITUDE=("LATITUDE", "mean"),
            CENTROID_LONGITUDE=("LONGITUDE", "mean"),
        )
    )

    # 10. Add a transparent stop-coverage score.
    # It measures stop coverage only, not service frequency or travel time.
    summary["STOP_COUNT_PERCENTILE"] = (
        summary["PRIMARY_ACCESS_POINTS"].rank(method="average", pct=True) * 100
    )
    summary["STOP_COVERAGE_SCORE"] = (
        0.8 * summary["STOP_COUNT_PERCENTILE"]
        + 0.2 * (summary["MODES_AVAILABLE"] / 4 * 100)
    ).round(1)

    summary = summary.sort_values(
        ["STOP_COVERAGE_SCORE", "PRIMARY_ACCESS_POINTS"],
        ascending=[False, False],
    ).reset_index(drop=True)
    summary.insert(0, "COVERAGE_RANK", summary.index + 1)

    # 11. Save the results.
    clean_file = output_path / "clean_transport_stops.csv"
    summary_file = output_path / "suburb_transport_summary.csv"
    df.to_csv(clean_file, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_file, index=False, encoding="utf-8-sig")

    print(f"Original rows: {original_rows:,}")
    print(f"Rows after cleaning: {len(df):,}")
    print(f"Exact duplicates removed: {original_rows - len(df):,}")
    print(f"Suburbs: {len(summary):,}")
    print(f"Invalid coordinates: {(~df['COORDINATE_VALID']).sum():,}")
    print(f"Saved: {clean_file}")
    print(f"Saved: {summary_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean NSW transport-stop data")
    parser.add_argument("input_file", help="Path to tsn-to-tz-mapping.csv")
    parser.add_argument(
        "--output-folder",
        default="cleaned_output",
        help="Folder for the two output CSV files",
    )
    args = parser.parse_args()
    clean_transport_data(args.input_file, args.output_folder)
