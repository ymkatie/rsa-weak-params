"""RSA modulus-size scaling for Wiener's attack.

Run: python3 -m bench.scale_wiener
Options: --trials 10 --sizes 2048 3072 4096
Generates keys outside the attack timer. Writes a new CSV.
"""
import argparse
import csv
from pathlib import Path
from time import perf_counter

from attacks.wiener import wiener
from keygen.weak_wiener import weak_wiener


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sizes", nargs="+", type=int, default=[2048, 3072, 4096])
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--d-offsets", nargs="+", type=int, default=[-4, -2, 0, 2, 4])
    args = ap.parse_args()
    if any(b < 64 or b % 2 for b in args.sizes) or args.trials < 1:
        ap.error("sizes must be even and >=64; trials must be positive")
    output = Path("results/wiener_scaling.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["modulus_bits", "d_bits", "d_minus_quarter_bits", "trial",
              "below_sufficient_bound", "success", "convergents", "seconds"]
    with output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for bits in args.sizes:
            for offset in args.d_offsets:
                d_bits = bits // 4 + offset
                wins = 0
                for trial in range(1, args.trials + 1):
                    n, e, p, q, d = weak_wiener(bits=bits, d_bits=d_bits)
                    start = perf_counter()
                    rp, rq, rd, convergents = wiener(n, e)
                    elapsed = perf_counter() - start
                    success = rd == d and rp == p and rq == q
                    wins += bool(success)
                    writer.writerow(dict(modulus_bits=bits, d_bits=d_bits,
                                         d_minus_quarter_bits=offset, trial=trial,
                                         below_sufficient_bound=int((3*d)**4 < n),
                                         success=int(success),
                                         convergents=convergents,
                                         seconds=f"{elapsed:.9f}"))
                    fh.flush()
                print(f"Wiener N={bits} d={d_bits} (quarter{offset:+d}): {wins}/{args.trials}", flush=True)
    print("Saved:", output)


if __name__ == "__main__":
    main()
