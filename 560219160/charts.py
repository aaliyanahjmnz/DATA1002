import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,        
    "axes.spines.right": False,
    "axes.titlesize": 10,
    "axes.titleweight": "normal",
})
BLUE, ORANGE, GREY, INK = "#0072B2", "#D55E00", "#888888", "#333333"   # Okabe-Ito blue/orange
#standardised names 
bonds = pd.read_csv("clean_greater_sydney_rentalbond.csv")
h = pd.read_csv("housing_scores.csv").dropna(subset=["median_ppr"])
pc = h.groupby("Postcode").agg(rent=("median_ppr", "first"),
                               bonds=("n_bonds", "first"),
                               name=("Suburb", "first")).reset_index()
better_names = {2000: "Sydney CBD", 2170: "Liverpool", 2145: "Westmead", 2148: "Blacktown",
                2560: "Campbelltown", 2765: "Riverstone", 2766: "Rooty Hill", 2760: "St Marys",
                2570: "Oran Park", 2557: "Gregory Hills", 2179: "Leppington", 2770: "Mount Druitt",
                2775: "Wisemans Ferry", 2010: "Darlinghurst", 2155: "Kellyville", 2750: "Penrith",
                2747: "Kingswood"}
for postcode, new_name in better_names.items():
    pc.loc[pc["Postcode"] == postcode, "name"] = new_name
sydney_median = pc["rent"].median()      
bond_median = pc["bonds"].median()       

#Viz 1: 
pc = pc.sort_values("rent", kind="stable")
top = pd.concat([pc.head(10), pc.tail(10)])
colors = [BLUE] * 10 + [ORANGE] * 10
labels = top["name"] + " (" + top["bonds"].astype(int).map("{:,}".format) + ")"

fig, ax = plt.subplots(figsize=(6.3, 3.9))
bars = ax.barh(labels, top["rent"], color=colors, height=0.7)
ax.bar_label(bars, labels=[f"${int(v + 0.5)}" for v in top["rent"]],
             padding=3, fontsize=7.5, color=INK)              
ax.axvline(sydney_median, color=GREY, linestyle="--", linewidth=1, zorder=0)
ax.set_xlim(0, 880)
ax.tick_params(axis="y", length=0, labelsize=8)
ax.set_xlabel("Median weekly rent per room ($)")
ax.set_title("Most expensive postcode cost 4.2× the cheapest", pad=22)
ax.legend(handles=[Patch(color=ORANGE, label="10 most expensive"),
                   Patch(color=BLUE, label="10 cheapest"),
                   Line2D([], [], color=GREY, linestyle="--", label=f"Median of all postcodes (${sydney_median:.0f})")],
          loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=8)  # legend above the plot
plt.tight_layout()
plt.savefig("chart1_bar.png", dpi=300)
plt.close()

# VIZ 2
groups, ticks = [], []
for b, name in zip(range(7), ["Studio", "1", "2", "3", "4", "5", "6"]):
    rents = bonds.loc[bonds["Bedrooms"] == b, "Rent per Room ($)"].dropna()
    groups.append(rents)
    ticks.append(f"{name}\nn = {len(rents):,}")

fig, ax = plt.subplots(figsize=(6.3, 3.0))
ax.boxplot(groups, showfliers=False, widths=0.55,
           medianprops=dict(color=ORANGE, linewidth=1.5),
           boxprops=dict(color=INK), whiskerprops=dict(color=INK), capprops=dict(color=INK))
ax.set_xticks(range(1, 8))
ax.set_xticklabels(ticks, fontsize=8)
ax.tick_params(axis="x", length=0)
ax.set_xlabel("Number of bedrooms")
ax.set_ylabel("Weekly rent per room ($)")
ax.set_title("Rent per room falls as more people share")
ax.yaxis.grid(True, color="#e5e5e5", linewidth=0.6)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("chart2_box.png", dpi=300)
plt.close()

# ---------- CHART 3: scatter, leasing activity vs rent, coloured by property mix ----------
small_share = bonds.groupby("Postcode")["Bedrooms"].apply(lambda b: (b <= 1).mean() * 100)
pc["small"] = pc["Postcode"].map(small_share)

fig, ax = plt.subplots(figsize=(6.3, 3.5))
dots = ax.scatter(pc["bonds"], pc["rent"], c=pc["small"], cmap="viridis", s=16,
                  edgecolors="#444444", linewidths=0.3)
cbar = fig.colorbar(dots, ax=ax, pad=0.02)
cbar.set_label("Studios and 1-bedrooms (% of leases)", fontsize=8)
cbar.outline.set_visible(False)
ax.set_xscale("log")
ax.set_xlim(22, 20000)
ax.set_xticks([30, 100, 300, 1000, 3000, 10000])
ax.set_xticklabels(["30", "100", "300", "1,000", "3,000", "10,000"])
ax.set_ylim(150, 820)
ax.axhline(sydney_median, color=GREY, linestyle=":", linewidth=1, label=f"Median rent (${sydney_median:.0f})")
ax.axvline(bond_median, color=GREY, linestyle="--", linewidth=1, label=f"Median bonds ({bond_median:.0f})")
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=8)  # legend above the plot
# to avoid overlapping labels, few annotated 
offsets = {2008: (-5, 4, "right"), 2016: (-5, -4, "right"), 2000: (5, 0, "left"),
           2017: (5, 0, "left"), 2145: (5, 0, "left"), 2170: (5, 0, "left")}
for postcode, (dx, dy, side) in offsets.items():
    row = pc[pc["Postcode"] == postcode].iloc[0]
    ax.annotate(row["name"], (row["bonds"], row["rent"]), xytext=(dx, dy),
                textcoords="offset points", ha=side, va="center", fontsize=7.5, color=INK)
ax.set_xlabel("Number of bonds per suburb (leasing activity)")
ax.set_ylabel("Median weekly rent per room ($)")
plt.tight_layout()
plt.savefig("chart3_scatter.png", dpi=300)
plt.close()
print("saved 3 charts")
