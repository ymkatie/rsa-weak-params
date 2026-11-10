"""Three-trial 4096-bit Wiener and shared-prime experiments.

Run: python -u -m bench.run_4096
Existing result files are preserved unless --overwrite is supplied.
"""
import argparse
from pathlib import Path

from bench.bench import RESULTS, run_sweep
from bench import run_shared_prime, run_wiener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attack", choices=["all", "wiener", "shared_prime"], default="all")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("trials must be positive")
    experiments = {
        "wiener": (run_wiener, "d_bits", [1020, 1022, 1024, 1026, 1028]),
        "shared_prime": (run_shared_prime, "shared_pairs", [0, 1, 2]),
    }
    selected = list(experiments) if args.attack == "all" else [args.attack]
    for name in selected:
        path = Path(RESULTS) / f"{name}_4096.csv"
        if path.exists() and not args.overwrite:
            parser.error(f"Refusing to overwrite {path}; use --overwrite explicitly")
    for name in selected:
        runner, parameter, values = experiments[name]

        def make_key(value):
            print(f"Generating {name}: {parameter}={value}, N=4096 bits", flush=True)
            if name == "shared_prime":
                return runner.make_key(value, bits=4096, key_count=4)
            return runner.make_key(value, bits=4096)

        run_sweep(f"{name}_4096", parameter, values, make_key,
                  runner.attack, runner.check, trials=args.trials)


if __name__ == "__main__":
    main()
