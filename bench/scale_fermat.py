"""RSA modulus-size scaling for Fermat's attack.

Run from repo root: python3 -m bench.scale_fermat
Options: --trials 10 --max-iters 16777216 --sizes 2048 3072 4096
Outputs separate CSV; does not overwrite the existing Fermat experiments.
"""
import argparse
import csv
from math import isqrt
from pathlib import Path
from time import perf_counter

from attacks.fermat import fermat
from keygen.weak_fermat import weak_fermat
from verify import verify_factors


def exact_checks(n, p, q):
    a = isqrt(n)
    if a * a < n:
        a += 1
    return (p + q) // 2 - a + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sizes", nargs="+", type=int, default=[2048, 3072, 4096])
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--max-iters", type=int, default=2**20)
    ap.add_argument("--gap-offsets", nargs="+", type=int, default=[10, 12, 14])
    args = ap.parse_args()
    if any(b < 64 or b % 2 for b in args.sizes) or args.trials < 1 or args.max_iters < 1:
        ap.error("sizes must be even and >=64; trials and max-iters must be positive")
    output = Path("results/fermat_scaling.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["modulus_bits", "gap_bits", "gap_minus_quarter_bits", "trial",
              "success", "capped", "max_iters", "iterations",
              "exact_checks", "seconds"]
    with output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for bits in args.sizes:
            for offset in args.gap_offsets:
                gap = bits // 4 + offset
                wins = 0
                for trial in range(1, args.trials + 1):
                    n, _, p, q = weak_fermat(bits=bits, gap_bits=gap)
                    exact = exact_checks(n, p, q)
                    start = perf_counter()
                    rp, rq, checks = fermat(n, max_iters=args.max_iters)
                    elapsed = perf_counter() - start
                    success = verify_factors(n, rp, rq) and {rp, rq} == {p, q}
                    assert (checks == exact) if success else (exact > args.max_iters)
                    wins += bool(success)
                    writer.writerow(dict(modulus_bits=bits, gap_bits=gap,
                                         gap_minus_quarter_bits=offset, trial=trial,
                                         success=int(success), capped=int(not success),
                                         max_iters=args.max_iters, iterations=checks,
                                         exact_checks=exact, seconds=f"{elapsed:.9f}"))
                    fh.flush()
                print(f"Fermat N={bits} gap={gap} (quarter+{offset}): {wins}/{args.trials}", flush=True)
    print("Saved:", output)


if __name__ == "__main__":
    main()
