"""Plot refined Fermat measurements; run: python3 -m bench.plot_fermat_refined."""
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INPUT = Path("results/fermat_refined.csv")
OUTPUT = Path("results/fermat_refined.png")


def main():
    if not INPUT.is_file():
        raise SystemExit("Run python3 -m bench.run_fermat_refined first")
    by_gap = defaultdict(list)
    with INPUT.open(newline="") as fh:
        for row in csv.DictReader(fh):
            by_gap[int(row["requested_gap_bits"])].append(row)
    if not by_gap:
        raise SystemExit("No benchmark rows")
    gaps = sorted(by_gap)
    success_pct = [
        100 * sum(int(row["success"]) for row in by_gap[g]) / len(by_gap[g])
        for g in gaps
    ]
    theoretical = [
        median(int(row["exact_expected_iterations"]) for row in by_gap[g])
        for g in gaps
    ]
    measured = [
        median(int(row["iterations"]) for row in by_gap[g]
               if int(row["success"]))
        if any(int(row["success"]) for row in by_gap[g]) else None
        for g in gaps
    ]
    cap = max(int(row["max_iterations"]) for rows in by_gap.values() for row in rows)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    ax1.plot(gaps, theoretical, "o--", label="Exact theoretical checks")
    valid = [(gap, count) for gap, count in zip(gaps, measured) if count is not None]
    if valid:
        ax1.plot([v[0] for v in valid], [v[1] for v in valid],
                 "o-", label="Observed checks (successful runs)")
    ax1.axhline(cap, linestyle=":", label="Iteration cap (censored)")
    ax1.set_yscale("log")
    ax1.set_ylabel("Fermat checks (log scale)")
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax2.plot(gaps, success_pct, "o-")
    ax2.set_ylabel("Recovery success (%)")
    ax2.set_xlabel("Prime gap length (bits)")
    ax2.set_ylim(-5, 105)
    ax2.grid(alpha=0.3)
    fig.suptitle("Fermat factorisation on 2048-bit RSA: refined transition")
    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
