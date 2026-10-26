"""First figure: median net worth of families headed by a college graduate vs.
families headed by someone with a high school education or less, 1989-2025.

Run get_data.py first. Output: figures/networth_gap_by_education.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "scf_networth_by_education.csv"
OUT_FILE = ROOT / "figures" / "networth_gap_by_education.png"

COLLEGE, HS = "College degree", "High school or less"
COLORS = {COLLEGE: "#2a78d6", HS: "#eb6834"}
INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK_2)
    ax.tick_params(colors=INK_2, length=0, labelsize=9)
    ax.set_xticks(range(1989, 2026, 6))


def main():
    df = pd.read_csv(DATA_FILE)
    med = df.pivot(index="year", columns="group", values="median_networth")
    ratio = med[COLLEGE] / med[HS]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), facecolor=SURFACE)

    # Left: median net worth of each group (thousands of 2025 dollars)
    for group in (COLLEGE, HS):
        s = med[group] / 1000
        ax1.plot(s.index, s.values, color=COLORS[group], linewidth=2,
                 marker="o", markersize=5, markeredgecolor=SURFACE)
        ax1.annotate(f"{group}\n${s.iloc[-1]:,.0f}K", (s.index[-1], s.iloc[-1]),
                     xytext=(8, 0), textcoords="offset points", va="center",
                     fontsize=9, color=INK)
    style(ax1)
    ax1.set_ylim(bottom=0)
    ax1.set_xlim(1987, 2033)  # room for the end labels
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}K"))
    ax1.set_title("Median family net worth, by education of family head\n"
                  "(thousands of 2025 dollars)", loc="left", fontsize=10, color=INK)

    # Right: the gap as a ratio of medians
    ax2.plot(ratio.index, ratio.values, color=INK_2, linewidth=2,
             marker="o", markersize=5, markeredgecolor=SURFACE)
    for yr in (ratio.index[0], ratio.index[-1]):
        ax2.annotate(f"{ratio[yr]:.1f}x", (yr, ratio[yr]), xytext=(0, 8),
                     textcoords="offset points", ha="center", fontsize=9, color=INK)
    style(ax2)
    ax2.set_ylim(bottom=0)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}x"))
    ax2.set_title("Gap: college-degree median ÷ high-school-or-less median",
                  loc="left", fontsize=10, color=INK)

    fig.text(0.01, 0.01,
             "Source: Federal Reserve Board, Survey of Consumer Finances summary extracts, "
             "1989-2025. Weighted medians, five implicates pooled.",
             fontsize=8, color=INK_2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FILE, dpi=200)
    print(f"Wrote {OUT_FILE}")
    print(pd.DataFrame({"college": med[COLLEGE], "hs_or_less": med[HS],
                        "ratio": ratio}).round(1))


if __name__ == "__main__":
    main()
