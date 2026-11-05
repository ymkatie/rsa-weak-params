"""Plot custom LLL vs SageMath results: python3 -m bench.plot_coppersmith"""
from pathlib import Path
import csv
from collections import defaultdict
from statistics import mean
import matplotlib.pyplot as plt


def main():
    src = Path("results/coppersmith_comparison.csv")
    if not src.exists():
        raise SystemExit("Run sage bench/compare_coppersmith.sage first")
    groups = defaultdict(list)
    with src.open(newline="") as fh:
        for row in csv.DictReader(fh):
            label = row["method"]
            if label == "custom_lll":
                label += f" (m={row['m']}, t={row['t']})"
            groups[label, int(row["unknown_bits"])].append(row)
    for metric, filename, ylabel in [
        ("success", "coppersmith_success.png", "Recovery success (%)"),
        ("total_seconds", "coppersmith_runtime.png", "Mean elapsed time (s)"),
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
        dst = Path("results") / filename
        fig.savefig(dst,dpi=160)
        plt.close(fig)
        print("Saved:",dst)


if __name__ == "__main__":
    main()
