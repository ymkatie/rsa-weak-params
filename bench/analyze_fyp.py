"""Summarize Fermat and Coppersmith CSV benchmarks, produce FYP-ready plots.

Run from repository root:
    python3 -m bench.analyze_fyp
    python3 -m bench.analyze_fyp --output-dir results/fyp_analysis

Only reads source CSV files; derived CSV/PNG outputs go to --output-dir.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INPUTS = [
    "results/fermat_scaling.csv",
    "results/fermat_controls.csv",
    "results/coppersmith_comparison_2048_refined.csv",
    "results/coppersmith_scaling_3072.csv",
    "results/coppersmith_scaling_4096.csv",
    "results/coppersmith_scaling_4096_boundary.csv",
    "results/coppersmith_scaling_4096_refined.csv",
    "results/coppersmith_scaling_4096_refined_run2.csv",
    "results/coppersmith_controls.csv",
    "results/coppersmith_lattice_sweep_4096.csv",
]


def read_rows(path):
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            yield row


def is_coppersmith(row):
    return "unknown_bits" in row


def value(row, *names, default=""):
    for name in names:
        result = row.get(name, "")
        if result != "":
            return result
    return default


def normalize(row, source):
    if is_coppersmith(row):
        typ = "coppersmith"
        method = row.get("method", "unknown")
        m = value(row, "m")
        t = value(row, "t")
        setting = int(row["unknown_bits"])
        setting_name = "unknown_bits"
        key_type = row.get("prefix_type", "correct_leak")
    else:
        typ = "fermat"
        method = "fermat"
        m = t = ""
        setting = int(value(row, "gap_minus_quarter_bits", "gap_bits", default="0"))
        setting_name = ("gap_offset" if "gap_minus_quarter_bits" in row
                        else "gap_bits")
        key_type = row.get("key_type", "close_primes")
    seconds = value(row, "seconds", "total_seconds")
    return dict(source=source.name, attack=typ, bits=int(row["modulus_bits"]),
                setting=setting, setting_name=setting_name, method=method,
                m=m, t=t, key_type=key_type, success=int(row["success"]),
                seconds=float(seconds) if seconds else None)


def analyze(files, output):
    rows = []
    for path in files:
        if not path.exists():
            print("Skipping (file not found):", path)
            continue
        try:
            batch = [normalize(row, path) for row in read_rows(path)]
            rows.extend(batch)
            print(f"Read {len(batch)} trials: {path}")
        except (KeyError, ValueError) as exc:
            print(f"Skipping incompatible CSV {path}: {exc}")
    if not rows:
        raise SystemExit("No matching benchmark CSVs found")

    # Keep each source separate: repeat runs could use different random keys,
    # trial counts, parameters or hardware configurations.
    groups = defaultdict(list)
    for row in rows:
        key = tuple(row[k] for k in ("source", "attack", "bits", "setting_name",
                                     "setting", "method", "m", "t", "key_type"))
        groups[key].append(row)
    fields = ["source", "attack", "modulus_bits", "setting_name", "setting",
              "method", "m", "t", "key_type", "trials", "successes",
              "success_rate_percent", "median_seconds", "median_success_seconds"]
    output.mkdir(parents=True, exist_ok=True)
    summary = []
    for key, group in sorted(groups.items()):
        timings = [r["seconds"] for r in group if r["seconds"] is not None]
        successful_timings = [r["seconds"] for r in group
                              if r["success"] and r["seconds"] is not None]
        count = sum(r["success"] for r in group)
        summary.append(dict(zip(fields, list(key) + [
            len(group), count, round(100*count/len(group), 2),
            round(median(timings), 6) if timings else "",
            round(median(successful_timings), 6) if successful_timings else ""])))
    with (output/"summary.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)
    print("Saved:", output/"summary.csv")

    # Independent plots for each input and modulus; no mixing across runs.
    for (source, attack, bits), subset in sorted(_group_summary(summary).items()):
        # Group by method and lattice size; show each one as its own line.
        fig, ax = plt.subplots(figsize=(8, 5))
        grouped = defaultdict(list)
        for r in subset:
            label = r["key_type"] if attack == "fermat" else (
                r["method"] + (f" {r['m']}x{r['t']}" if r["m"] else "")
                + (f" [{r['key_type']}]" if r["key_type"] != "correct_leak" else ""))
            grouped[label].append(r)
        for label, measurements in sorted(grouped.items()):
            measurements.sort(key=lambda r: int(r["setting"]))
            ax.plot([int(r["setting"]) for r in measurements],
                    [float(r["success_rate_percent"]) for r in measurements],
                    marker="o", label=label)
        ax.set_xlabel(subset[0]["setting_name"].replace("_", " "))
        ax.set_ylabel("Recovery success rate (%)")
        ax.set_ylim(-5, 105)
        ax.set_title(f"{attack.title()} {bits}-bit: {source}")
        ax.grid(alpha=0.3)
        ax.legend(fontsize="small")
        fig.tight_layout()
        stem = Path(source).stem
        out = output/f"{stem}_success_{bits}.png"
        fig.savefig(out, dpi=160)
        plt.close(fig)
        print("Saved:", out)

    # Median time is shown on a separate plot; failed attempts are also timed.
    for (source, attack, bits), subset in sorted(_group_summary(summary).items()):
        fig, ax = plt.subplots(figsize=(8, 5))
        grouped = defaultdict(list)
        for r in subset:
            if r["median_seconds"] == "":
                continue
            label = r["key_type"] if attack == "fermat" else (
                r["method"] + (f" {r['m']}x{r['t']}" if r["m"] else "")
                + (f" [{r['key_type']}]" if r["key_type"] != "correct_leak" else ""))
            grouped[label].append(r)
        if not grouped:
            plt.close(fig)
            continue
        for label, measurements in sorted(grouped.items()):
            measurements.sort(key=lambda r: int(r["setting"]))
            ax.plot([int(r["setting"]) for r in measurements],
                    [float(r["median_seconds"]) for r in measurements],
                    marker="o", label=label)
        ax.set_xlabel(subset[0]["setting_name"].replace("_", " "))
        ax.set_ylabel("Median attack duration (seconds; failures included)")
        ax.set_title(f"{attack.title()} {bits}-bit runtime: {source}")
        ax.grid(alpha=0.3)
        ax.legend(fontsize="small")
        fig.tight_layout()
        out = output/f"{Path(source).stem}_runtime_{bits}.png"
        fig.savefig(out, dpi=160)
        plt.close(fig)
        print("Saved:", out)
    return summary


def _group_summary(summary):
    result = defaultdict(list)
    for row in summary:
        result[(row["source"], row["attack"], row["modulus_bits"])].append(row)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--files", nargs="+", type=Path,
                    default=[Path(f) for f in INPUTS])
    ap.add_argument("--output-dir", type=Path, default=Path("results/fyp_analysis"))
    args = ap.parse_args()
    analyze(args.files, args.output_dir)


if __name__ == "__main__":
    main()
