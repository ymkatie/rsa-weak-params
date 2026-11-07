"""4096-bit Coppersmith partial-prime leakage pilot.

Run from repository root:
    sage bench/scale_coppersmith_4096.sage
    sage bench/scale_coppersmith_4096.sage --trials 3 --with-sage
    sage bench/scale_coppersmith_4096.sage --unknown-bits 900 940 960 --trials 5 --with-sage

Default is a low-cost CUSTOM LLL pilot; Sage small_roots is opt-in.
Results go to results/coppersmith_scaling_4096.csv, never the 3072 CSV.
A rerun overwrites the 4096 CSV only when --overwrite is passed.

The imported source scripts may print standalone 512-bit demos; these are
not part of the 4096-bit experiment.
"""
import argparse
import csv
from pathlib import Path
from time import perf_counter
from sage.all import ZZ, Zmod, PolynomialRing, gcd

load("attacks/coppersmith.sage")
load("attacks/coppersmith_lattice.sage")


def sage_baseline(n, high, unknown_bits, beta, epsilon):
    R = PolynomialRing(Zmod(n), "x")
    x = R.gen()
    for root in (x + R(high)).small_roots(
            X=ZZ(2)**unknown_bits, beta=beta, epsilon=epsilon):
        factor = gcd(n, high + ZZ(root))
        if 1 < factor < n and n % factor == 0:
            return ZZ(factor), ZZ(n // factor)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unknown-bits", nargs="+", type=int,
                        default=[850, 900, 950])
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--lattice-sizes", nargs="+", type=int,
                        default=[6, 8],
                        help="For each size s, use m=t=s (dimension=2s)")
    parser.add_argument("--with-sage", action="store_true",
                        help="Also run SageMath small_roots; may be much slower")
    parser.add_argument("--beta", type=float, default=0.499)
    parser.add_argument("--epsilon", type=float, default=0.02)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--output", type=Path,
                        default=Path("results/coppersmith_scaling_4096.csv"))
    args = parser.parse_args()

    bits = 4096
    if args.trials < 1 or not args.lattice_sizes or any(
            size < 1 for size in args.lattice_sizes):
        parser.error("trials and lattice sizes must be positive")
    if not args.unknown_bits or any(k <= 0 or k >= bits // 2
                                    for k in args.unknown_bits):
        parser.error("unknown bits must be between 1 and 2047")
    if not 0 < args.beta <= 0.5 or not 0 < args.epsilon < args.beta:
        parser.error("Require 0 < beta <= 0.5 and 0 < epsilon < beta")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and not args.overwrite:
        parser.error("Output exists; pass --overwrite or choose --output to preserve it")

    fields = ["modulus_bits", "unknown_bits", "trial", "method", "m", "t",
              "dimension", "success", "seconds", "lll_seconds", "error"]
    with args.output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for unknown_bits in args.unknown_bits:
            for trial in range(1, args.trials + 1):
                print(f"Generating 4096-bit RSA key: unknown={unknown_bits}, trial={trial}",
                      flush=True)
                p, q, n = generate_balanced_key(bits)
                high = (p >> unknown_bits) << unknown_bits
                cases = ([("sage", None, None)] if args.with_sage else []) + [
                    ("custom_lll", size, size) for size in args.lattice_sizes]
                for method, m, t in cases:
                    print(f"Starting: N={bits} unknown={unknown_bits} trial={trial} "
                          f"method={method} m={m} t={t}", flush=True)
                    start = perf_counter()
                    factors, metrics, error = None, {}, ""
                    try:
                        if method == "sage":
                            factors = sage_baseline(n, high, unknown_bits,
                                                    args.beta, args.epsilon)
                        else:
                            factors, metrics = recover_prime_high_bits(
                                n, high, unknown_bits, m=m, t=t,
                                max_vectors=m+t)
                        # The intended high-bit prefix must recover the exact p.
                        success = bool(factors is not None and
                                       ZZ(factors[0]) * ZZ(factors[1]) == n
                                       and p in factors)
                    except Exception as exc:
                        success = False
                        error = repr(exc)
                    elapsed = perf_counter() - start
                    writer.writerow({
                        "modulus_bits": bits, "unknown_bits": unknown_bits,
                        "trial": trial, "method": method,
                        "m": m if m is not None else "",
                        "t": t if t is not None else "",
                        "dimension": metrics.get("dimension", ""),
                        "success": int(success), "seconds": f"{elapsed:.9f}",
                        "lll_seconds": metrics.get("lll_seconds", ""),
                        "error": error,
                    })
                    fh.flush()
                    print(f"Completed: method={method} success={success} "
                          f"seconds={elapsed:.3f}"
                          + (f" error={error}" if error else ""), flush=True)
    print("Saved:", args.output, flush=True)


if __name__ == "__main__":
    main()
