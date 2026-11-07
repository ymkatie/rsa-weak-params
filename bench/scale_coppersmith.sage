"""Pilot Coppersmith scaling to 3072-bit RSA.

From the repo root: sage bench/scale_coppersmith.sage
Compares SageMath's small_roots with explicit LLL on identical generated keys.
Uses separate output and modest lattice sizes; increase after pilot succeeds.
The two loaded attack scripts may print their 512-bit demos in Sage's load context.
"""
from sage.all import ZZ, Zmod, PolynomialRing, gcd
from pathlib import Path
from time import perf_counter
import csv

load("attacks/coppersmith.sage")
load("attacks/coppersmith_lattice.sage")

BITS = 3072
UNKNOWN_BITS = [580, 620, 640]
TRIALS = 3
LATTICE_PARAMETERS = [(6, 6), (8, 8)]
BETA = 0.499
EPSILON = 0.02
OUTPUT = Path("results/coppersmith_scaling_3072.csv")


def baseline(N, high, k):
    R = PolynomialRing(Zmod(N), "x")
    x = R.gen()
    roots = (x + R(high)).small_roots(X=ZZ(2)**k, beta=BETA, epsilon=EPSILON)
    for root in roots:
        factor = gcd(N, high + ZZ(root))
        if 1 < factor < N and N % factor == 0:
            return (ZZ(factor), ZZ(N // factor))
    return None


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["modulus_bits", "unknown_bits", "trial", "method",
                         "m", "t", "dimension", "success",
                         "seconds", "lll_seconds", "error"])
        for k in UNKNOWN_BITS:
            for trial in range(1, TRIALS + 1):
                p, q, N = generate_balanced_key(BITS)
                high = (p >> k) << k
                cases = [("sage", None, None)] + [
                    ("custom_lll", m, t) for m, t in LATTICE_PARAMETERS]
                for method, m, t in cases:
                    start = perf_counter()
                    error = ""
                    metrics = {}
                    try:
                        if method == "sage":
                            factors = baseline(N, high, k)
                        else:
                            factors, metrics = recover_prime_high_bits(
                                N, high, k, m=m, t=t, max_vectors=m+t)
                        success = factors is not None and p in factors
                    except Exception as exc:
                        success = False
                        error = repr(exc)
                    elapsed = perf_counter() - start
                    writer.writerow([BITS, k, trial, method, m or "", t or "",
                                     metrics.get("dimension", ""),
                                     int(success), f"{elapsed:.9f}",
                                     metrics.get("lll_seconds", ""), error])
                    fh.flush()
                    print(f"N={BITS} k={k} trial={trial} method={method} "
                          f"m={m} t={t} success={success} time={elapsed:.3f}s",
                          flush=True)
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    main()
