"""Compare close-prime RSA and independently generated RSA under Fermat.

Run: python3 -m bench.control_fermat --trials 3
Results are isolated in results/fermat_controls.csv. Existing results are safe.
Independent RSA keys are NOT assumed secure against every attack.
"""
import argparse
import csv
from math import gcd, isqrt
from pathlib import Path
from time import perf_counter
from Crypto.Util.number import getPrime
from attacks.fermat import fermat
from keygen.weak_fermat import weak_fermat


def independent_key(bits, e=65537):
    if bits < 64 or bits % 2:
        raise ValueError("Expected even modulus size >= 64")
    while True:
        p, q = getPrime(bits // 2), getPrime(bits // 2)
        n = p * q
        if p != q and n.bit_length() == bits and gcd(e, (p - 1) * (q - 1)) == 1:
            return n, e, p, q


def expected_checks(n, p, q):
    a = isqrt(n)
    if a * a < n:
        a += 1
    return (p + q) // 2 - a + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sizes", nargs="+", type=int, default=[2048, 3072, 4096])
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--max-iters", type=int, default=10000)
    ap.add_argument("--gap-offset", type=int, default=8)
    ap.add_argument("--output", type=Path, default=Path("results/fermat_controls.csv"))
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    if any(b < 64 or b % 2 for b in args.sizes) or args.trials < 1 or args.max_iters < 1:
        ap.error("Even modulus sizes >=64, positive trials and max-iters required")
    if any(2 > b//4+args.gap_offset or b//4+args.gap_offset >= b//2-1 for b in args.sizes):
        ap.error("Gap offset outside valid range for one of the modulus sizes")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and not args.overwrite:
        ap.error("Output exists: use --overwrite or a new --output path")

    fields = ["modulus_bits", "key_type", "gap_bits", "trial", "success",
              "iteration_cap", "checks_performed", "expected_checks",
              "censored", "seconds", "correct_factors"]
    with args.output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for bits in args.sizes:
            for trial in range(1, args.trials+1):
                for kind in ("close_primes", "independent_primes"):
                    if kind == "close_primes":
                        n, _, p, q = weak_fermat(bits=bits, gap_bits=bits//4+args.gap_offset)
                    else:
                        n, _, p, q = independent_key(bits)
                    exact = expected_checks(n, p, q)
                    print(f"Starting Fermat control N={bits}, {kind}, trial={trial}",
                          flush=True)
                    start = perf_counter()
                    rp, rq, checks = fermat(n, max_iters=args.max_iters)
                    elapsed = perf_counter() - start
                    success = bool(rp is not None and rp*rq == n and {rp,rq} == {p,q})
                    if success != (exact <= args.max_iters):
                        raise AssertionError("Observed recovery inconsistent with exact Fermat checks")
                    if success and checks != exact:
                        raise AssertionError("Incorrect Fermat iteration count")
                    writer.writerow(dict(modulus_bits=bits, key_type=kind,
                        gap_bits=abs(p-q).bit_length(), trial=trial,
                        success=int(success), iteration_cap=args.max_iters,
                        checks_performed=checks, expected_checks=exact,
                        censored=int(not success), seconds=f"{elapsed:.9f}",
                        correct_factors=int(success)))
                    fh.flush()
                    print(f"Completed: {kind} success={success} elapsed={elapsed:.3f}s",
                          flush=True)
    print("Saved:", args.output)


if __name__ == "__main__":
    main()
