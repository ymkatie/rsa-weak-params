"""Plot shared-prime recovery counts and attack-only runtime."""
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
    with open(os.path.join(RESULTS, "shared_prime.csv"), newline="") as stream:
        for row in csv.DictReader(stream):
            data[int(row["shared_pairs"])].append(row)
    if not data:
        raise ValueError("No shared-prime benchmark rows to plot")
    rows = [row for group in data.values() for row in group]
    configurations = {(int(r["n_bits"]), int(r["key_count"])) for r in rows}
    if len(configurations) != 1:
        raise ValueError("Plot requires a single key size and collection size")
    bits, count = configurations.pop()
    sizes = sorted(data)
    times = [1000 * median(float(r["time_s"]) for r in data[v]) for v in sizes]
    recovered = [sum(int(r["recovered_keys"]) for r in data[v]) / len(data[v])
                 for v in sizes]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax1.plot(sizes, times, "o-", color="#2a78d6")
    ax1.set_ylabel("Median attack time (ms)")
    ax1.set_title(f"Shared-prime GCD: {count} RSA keys, {bits} bits each", loc="left")
    ax2.plot(sizes, recovered, "o-", label="Mean recovered keys")
    ax2.plot(sizes, [2 * v for v in sizes], "--", label="Expected vulnerable keys")
    ax2.set_ylabel("Keys recovered")
    ax2.set_xlabel("Disjoint pairs sharing a prime")
    ax2.set_xticks(sizes)
    ax2.set_ylim(-0.5, count + 0.5)
    ax2.legend(frameon=False)
    for ax in (ax1, ax2):
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path = os.path.join(RESULTS, "shared_prime.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
