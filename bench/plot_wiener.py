"""Plot results/wiener.csv -> results/wiener.png.

Run from the repo root: python -m bench.plot_wiener
"""
import csv
import os
from collections import defaultdict
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bench.bench import RESULTS


def main():
    data = defaultdict(list)
    with open(os.path.join(RESULTS, "wiener.csv"), newline="") as f:
        for row in csv.DictReader(f):
            data[int(row["d_bits"])].append(row)
    n_bits = int(next(iter(data.values()))[0]["n_bits"])
    # Focus on the transition, keeping the smaller-d trials in the CSV.
    sizes = sorted(b for b in data if b >= n_bits // 4 - 12)
    if not sizes:
        sizes = sorted(data)
    times = [1000 * median(float(r["time_s"]) for r in data[b]) for b in sizes]
    successes = [100 * sum(r["success"] == "True" for r in data[b]) / len(data[b])
                 for b in sizes]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True)
    ax1.plot(sizes, times, "o-", color="#2a78d6")
    ax1.set_ylabel("Median attack time (ms)")
    ax1.set_title(f"Wiener attack on {n_bits}-bit RSA moduli", loc="left")
    ax2.plot(sizes, successes, "o-", color="#2a78d6")
    ax2.set_ylabel("Success (%)")
    ax2.set_ylim(-5, 105)
    ax2.set_yticks([0, 50, 100])
    ax2.set_xlabel("Private exponent bit length")
    ax2.set_xticks(sizes)
    ax2.tick_params(axis="x", labelsize=8, rotation=45)
    for ax in (ax1, ax2):
        ax.axvline(n_bits / 4, color="#eb6834", linestyle="--",
                   label="Approximate N^(1/4) scale")
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
    ax1.legend(frameon=False)
    fig.text(0.5, 0.02, "Sufficient bound: d < N^(1/4)/3 for balanced primes. "
             "Success beyond this bound is key-dependent.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path = os.path.join(RESULTS, "wiener.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
