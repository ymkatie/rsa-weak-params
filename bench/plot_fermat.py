"""Plot results/fermat.csv -> results/fermat.png

Run from the repo root:  python -m bench.plot_fermat
"""
import csv
import os
from collections import defaultdict
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bench.bench import RESULTS
from bench.run_fermat import MAX_ITERS

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def load(path):
    by_gap = defaultdict(list)
    with open(path) as f:
        for r in csv.DictReader(f):
            by_gap[int(r["gap_bits"])].append(r)
    return dict(sorted(by_gap.items()))


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def main():
    full = load(os.path.join(RESULTS, "fermat.csv"))
    # below ~N^(1/4) every run is 1 iteration, so plot only the transition zone
    ZOOM_FROM = 500
    flat = [g for g in full if g < ZOOM_FROM]
    data = {g: rows for g, rows in full.items() if g >= ZOOM_FROM}
    gaps = list(data)
    n_bits = int(next(iter(data.values()))[0]["n_bits"])
    quarter = n_bits // 4

    ok_gaps, measured = [], []
    for g, rows in data.items():
        wins = [int(r["iterations"]) for r in rows if r["success"] == "True"]
        if wins:
            ok_gaps.append(g)
            measured.append(median(wins))
    predicted = [median(int(r["predicted_iterations"]) for r in rows) for rows in data.values()]
    success = [100 * sum(r["success"] == "True" for r in rows) / len(rows) for rows in data.values()]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True,
                                   gridspec_kw={"height_ratios": [2.2, 1]})
    fig.patch.set_facecolor("white")

    # top: iterations, measured vs theory
    ax1.plot(gaps, predicted, color=ORANGE, lw=2, ls="--", label="Predicted  (p−q)² / 8√N")
    ax1.plot(ok_gaps, measured, color=BLUE, lw=2, marker="o", ms=6,
             markeredgecolor="white", markeredgewidth=1.5, label="Measured (median)")
    ax1.axhline(MAX_ITERS, color=MUTED, lw=1, ls=":")
    ax1.text(gaps[0], MAX_ITERS * 1.6, "iteration cap 2²⁴ (≈3 s): counted as failure",
             color=MUTED, fontsize=8.5)
    ax1.set_yscale("log")
    ax1.set_ylim(0.5, predicted[-1] * 4)
    ax1.set_ylabel("Iterations to factor N", color=INK, fontsize=10)
    ax1.legend(frameon=False, fontsize=9, loc="lower right")
    style(ax1)

    # bottom: success rate
    ax2.plot(gaps, success, color=BLUE, lw=2, marker="o", ms=6,
             markeredgecolor="white", markeredgewidth=1.5)
    ax2.set_ylim(-8, 108)
    ax2.set_yticks([0, 50, 100])
    ax2.set_ylabel("Success (%)", color=INK, fontsize=10)
    ax2.set_xticks(gaps)
    ax2.set_xlabel("Prime gap  log₂|p − q|  (bits)", color=INK, fontsize=10)
    style(ax2)

    for ax in (ax1, ax2):
        ax.axvline(quarter, color=INK, lw=1, alpha=0.5)
    ax1.text(quarter - 0.4, predicted[-1] * 1.5, f"N^¼ = {quarter} bits", color=INK,
             fontsize=8.5, ha="right")

    fig.suptitle(f"Fermat factorisation on {n_bits}-bit RSA moduli", x=0.08, ha="left",
                 fontsize=12.5, color=INK, fontweight="bold")
    fig.text(0.08, 0.895, f"{len(next(iter(data.values())))} keys per gap. Gaps of "
             f"{flat[0]}–{flat[-1]} bits (not shown) all fell in 1 iteration.\n"
             "Above N^¼ each extra bit of gap costs 4× more.",
             fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    out = os.path.join(RESULTS, "fermat.png")
    fig.savefig(out, dpi=200)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
