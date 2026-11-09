"""Compare disclosed correct RSA prime prefix against an unrelated decoy prefix.

This is a negative *incorrect-information* control, NOT an attack on RSA
with no prime leakage (there is no suitable polynomial without leakage).

From the repo root:
    sage bench/control_coppersmith.sage
    sage bench/control_coppersmith.sage --bits 4096 --unknown-bits 850 --trials 3
Output: results/coppersmith_controls.csv (overwrite is opt-in).
"""
import argparse
import csv
from pathlib import Path
from time import perf_counter
from sage.all import ZZ

load("attacks/coppersmith.sage")
load("attacks/coppersmith_lattice.sage")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, default=2048)
    parser.add_argument("--unknown-bits", type=int, default=400)
    parser.add_argument("--trials", type=int, default=2)
    parser.add_argument("--lattice-size", type=int, default=6)
    parser.add_argument("--output", type=Path,
                        default=Path("results/coppersmith_controls.csv"))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.bits < 64 or args.bits % 2 or not 0 < args.unknown_bits < args.bits//2:
        parser.error("Require even RSA bits >=64 and unknown bits in (0, bits/2)")
    if args.trials < 1 or args.lattice_size < 1:
        parser.error("Trials and lattice size must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and not args.overwrite:
        parser.error("Output already exists; choose --output or --overwrite")

    fields = ["modulus_bits", "unknown_bits", "trial", "prefix_type",
              "method", "m", "t", "dimension", "success", "seconds",
              "lll_seconds", "error"]
    with args.output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for trial in range(1, args.trials+1):
            print(f"Generating N={args.bits}, trial={trial}", flush=True)
            p, q, n = generate_balanced_key(args.bits)
            # Generate unrelated prime only to construct a nonmatching prefix.
            # The attacker is NOT given p or q. The decoy prefix is confirmed
            # not to match the high bits of either factor of this N.
            while True:
                decoy_p, _, _ = generate_balanced_key(args.bits)
                decoy_high = (decoy_p >> args.unknown_bits) << args.unknown_bits
                if decoy_high not in ((p >> args.unknown_bits) << args.unknown_bits,
                                      (q >> args.unknown_bits) << args.unknown_bits):
                    break
            high = (p >> args.unknown_bits) << args.unknown_bits
            for prefix_type, prefix in (("correct_leak", high),
                                        ("unrelated_decoy", decoy_high)):
                print(f"Starting: {prefix_type}, N={args.bits}, trial={trial}",
                      flush=True)
                start = perf_counter()
                error = ""
                metrics = {}
                try:
                    factors, metrics = recover_prime_high_bits(
                        n, prefix, args.unknown_bits, m=args.lattice_size,
                        t=args.lattice_size, max_vectors=2*args.lattice_size)
                    success = bool(factors and ZZ(factors[0])*ZZ(factors[1]) == n
                                   and p in factors)
                except Exception as exc:
                    success = False
                    error = repr(exc)
                elapsed = perf_counter() - start
                writer.writerow(dict(modulus_bits=args.bits,
                    unknown_bits=args.unknown_bits, trial=trial,
                    prefix_type=prefix_type, method="custom_lll",
                    m=args.lattice_size, t=args.lattice_size,
                    dimension=metrics.get("dimension", ""), success=int(success),
                    seconds=f"{elapsed:.9f}",
                    lll_seconds=metrics.get("lll_seconds", ""), error=error))
                fh.flush()
                print(f"Completed: {prefix_type} success={success} "
                      f"seconds={elapsed:.3f}", flush=True)
    print("Saved:", args.output)


if __name__ == "__main__":
    main()
