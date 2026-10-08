import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

gdf = gpd.read_file(
    "SAL_2021_AUST_GDA94_SHP/SAL_2021_AUST_GDA94.shp"
)

greater_sydney = pd.read_csv(
    "greater_sydney_suburbs.csv"
)

# Standardise names
gdf["SAL_NAME21"] = (
    gdf["SAL_NAME21"]
    .str.upper()
    .str.strip()
)

greater_sydney["Suburb"] = (
    greater_sydney["Suburb"]
    .str.upper()
    .str.strip()
)

gdf["SAL_NAME21"] = (
    gdf["SAL_NAME21"]
    .str.upper()
    .str.strip()
    .str.replace(" (NSW)", "", regex=False)
)

greater_sydney["Suburb"] = (
    greater_sydney["Suburb"]
    .str.upper()
    .str.strip()
)

gdf = gdf[
    gdf["SAL_NAME21"].isin(
        greater_sydney["Suburb"]
    )
]

scores = pd.read_csv(
    "datasets/scores/student_liveability_index_scores.csv"
)

scores["Suburb"] = (
    scores["Suburb"]
    .str.upper()
    .str.strip()
)

map_df = gdf.merge(
    scores,
    left_on="SAL_NAME21",
    right_on="Suburb",
    how="inner"
)

fig, ax = plt.subplots(
    figsize=(15, 15)
)

map_df.plot(
    column="Student_Liveability_Index",
    cmap="RdYlGn",
    legend=True,
    linewidth=0.2,
    edgecolor="black",
    ax=ax
)

plt.title(
    "Student Liveability Index Across Greater Sydney",
    fontsize=18
)

plt.axis("off")
plt.show()