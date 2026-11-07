"""Plot custom LLL vs SageMath results: python3 -m bench.plot_coppersmith"""
import argparse
from pathlib import Path
import csv
from collections import defaultdict
from statistics import mean
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/coppersmith_comparison.csv", help="Input comparison CSV")
    parser.add_argument("--prefix", default="coppersmith", help="Output file prefix (in results/)")
    args = parser.parse_args()
    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f"Input CSV not found: {src}")
    groups = defaultdict(list)
    with src.open(newline="") as fh:
        for row in csv.DictReader(fh):
            label = row["method"]
            if label == "custom_lll":
                label += f" (m={row['m']}, t={row['t']})"
            groups[label, int(row["unknown_bits"])].append(row)
    for metric, filename, ylabel in [
        ("success", "success.png", "Recovery success (%)"),
        ("total_seconds", "runtime.png", "Mean elapsed time (s)"),
    ]:
        fig, ax = plt.subplots(figsize=(9,5))
        for label in sorted({key[0] for key in groups}):
            points = sorted((bits, rows) for (name,bits),rows in groups.items()
                            if name == label)
            xs = [bits for bits,_ in points]
            ys = [mean(float(r[metric]) for r in rows) * (100 if metric=="success" else 1)
                  for _,rows in points]
            ax.plot(xs,ys,marker="o",label=label)
        ax.set_xlabel("Unknown low bits of p")
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        dst = Path("results") / f"{args.prefix}_{filename}"
        fig.savefig(dst,dpi=160)
        plt.close(fig)
        print("Saved:",dst)


if __name__ == "__main__":
    main()
