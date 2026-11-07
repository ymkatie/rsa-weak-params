"""Plot Fermat and Wiener scaling CSV files; run: python3 -m bench.plot_rsa_scaling."""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot(filename, output, title, xfield):
    if not Path(filename).exists():
        print("Not found (run benchmark first):", filename)
        return
    groups = defaultdict(list)
    with open(filename, newline="") as fh:
        for row in csv.DictReader(fh):
            groups[(int(row["modulus_bits"]), int(row[xfield]))].append(int(row["success"]))
    fig, ax = plt.subplots(figsize=(8, 5))
    for bits in sorted({k[0] for k in groups}):
        pts = sorted((offset, sum(values)/len(values)*100)
                     for (size, offset), values in groups.items() if size == bits)
        ax.plot([x for x, _ in pts], [v for _, v in pts], marker="o",
                label=f"{bits}-bit RSA")
    ax.set(xlabel="Weak parameter bits minus modulus_bits / 4",
           ylabel="Recovery success (%)", title=title, ylim=(-5, 105))
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print("Saved:", output)


if __name__ == "__main__":
    plot("results/fermat_scaling.csv", "results/fermat_scaling.png",
         "Fermat: prime gap scaling", "gap_minus_quarter_bits")
    plot("results/wiener_scaling.csv", "results/wiener_scaling.png",
         "Wiener: private exponent scaling", "d_minus_quarter_bits")
