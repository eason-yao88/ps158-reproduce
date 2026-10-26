"""The same figure as plot.py, styled after The Economist's charts: red rule
and tag at the top, bold headline with a standfirst, right-hand y labels,
labels on the lines, and a small source line.

Run get_data.py first. Output: figures/networth_gap_economist.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "scf_networth_by_education.csv"
OUT_FILE = ROOT / "figures" / "networth_gap_economist.png"

COLLEGE, HS = "College degree", "High school or less"
RED = "#E3120B"
DARK_BLUE, LIGHT_BLUE, RATIO = "#006BA2", "#3EBCD2", "#DB444B"
INK, GREY, GRID = "#0C0C0C", "#595959", "#D0D0D0"

plt.rcParams["font.family"] = ["Segoe UI", "Arial", "DejaVu Sans"]


def style(ax, ymax, step, fmt):
    ax.set_ylim(0, ymax)
    ax.set_xlim(1987, 2027)
    ax.set_yticks(range(0, ymax + 1, step))
    ax.set_yticklabels([fmt(v) for v in range(0, ymax + 1, step)])
    ax.yaxis.tick_right()
    ax.tick_params(axis="y", length=0, labelsize=9, colors=INK, pad=2)
    ax.tick_params(axis="x", length=4, width=0.8, labelsize=9, colors=INK)
    ax.set_xticks([1989, 1995, 2001, 2007, 2013, 2019, 2025])
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1)


def main():
    df = pd.read_csv(DATA_FILE)
    med = df.pivot(index="year", columns="group", values="median_networth") / 1000
    ratio = med[COLLEGE] / med[HS]

    fig = plt.figure(figsize=(9, 5.4), facecolor="white")
    ax1 = fig.add_axes((0.04, 0.14, 0.42, 0.56))
    ax2 = fig.add_axes((0.54, 0.14, 0.42, 0.56))

    # Red rule and tag across the top
    fig.add_artist(Line2D([0.0, 1.0], [0.995, 0.995], color=RED, linewidth=2.5))
    fig.add_artist(Rectangle((0.02, 0.955), 0.035, 0.035, color=RED, linewidth=0))

    fig.text(0.02, 0.915, "Degrees of separation", fontsize=15, fontweight="bold",
             color=INK, va="top")
    fig.text(0.02, 0.86,
             "United States, median family net worth by education of family head",
             fontsize=11, color=INK, va="top")

    # Left: median net worth, $'000 at 2025 prices
    for group, color in ((COLLEGE, DARK_BLUE), (HS, LIGHT_BLUE)):
        ax1.plot(med.index, med[group], color=color, linewidth=2.4,
                 solid_capstyle="butt")
    style(ax1, 600, 100, lambda v: f"{v:,}")
    ax1.text(2009.5, 310, COLLEGE, color=DARK_BLUE, fontsize=10, fontweight="bold")
    ax1.text(1996, 125, HS, color=LIGHT_BLUE, fontsize=10, fontweight="bold")
    ax1.set_title("Net worth, $'000, 2025 prices", loc="left", fontsize=10,
                  fontweight="bold", color=INK, pad=12)

    # Right: college median as a multiple of high-school-or-less median
    ax2.plot(ratio.index, ratio.values, color=RATIO, linewidth=2.4)
    style(ax2, 8, 2, lambda v: f"{v}")
    for yr, dy, va in ((ratio.index[0], 0.35, "bottom"), (ratio.index[-1], 0.35, "bottom")):
        ax2.text(yr, ratio[yr] + dy, f"{ratio[yr]:.1f}", ha="center", va=va,
                 fontsize=9, color=INK)
    ax2.set_title("College-degree median as a multiple of\nhigh-school-or-less median",
                  loc="left", fontsize=10, fontweight="bold", color=INK, pad=12)

    fig.text(0.02, 0.03,
             "Source: Federal Reserve Board, Survey of Consumer Finances, 1989-2025",
             fontsize=8, color=GREY)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FILE, dpi=200)
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
