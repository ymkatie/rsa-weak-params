"""Compare explicit LLL lattice against SageMath small_roots on identical keys.

Run from repository root: sage bench/compare_coppersmith.sage
Begin with small settings. Larger lattices and moduli can be expensive.
"""
from sage.all import ZZ, Zmod, PolynomialRing, gcd
from pathlib import Path
from time import perf_counter
import csv

load("attacks/coppersmith.sage")
load("attacks/coppersmith_lattice.sage")

BITS = 2048
UNKNOWN_BITS = [460, 465, 470, 475, 480]
TRIALS = 10
LATTICE_PARAMETERS = [(6, 6), (7, 7), (8, 8)]
BETA = 0.49
EPSILON = 0.03


def baseline(N, p_high, unknown_bits):
    R = PolynomialRing(Zmod(N), "x")
    x = R.gen()
    roots = (x + R(p_high)).small_roots(
        X=ZZ(2)**unknown_bits, beta=BETA, epsilon=EPSILON)
    for r in roots:
        p = gcd(N, p_high + ZZ(r))
        if 1 < p < N:
            return (ZZ(p), ZZ(N//p))
    return None


def main():
    output = Path("results/coppersmith_comparison_2048_refined.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["modulus_bits", "unknown_bits", "trial", "method",
                         "m", "t", "success", "total_seconds", "lll_seconds",
                         "lattice_dimension", "error"])
        for k in UNKNOWN_BITS:
            for trial in range(1, TRIALS+1):
                p, q, N = generate_balanced_key(BITS)
                p_high = (p >> k) << k
                start = perf_counter()
                error = ""
                try:
                    factors = baseline(N, p_high, k)
                    success = factors is not None and p in factors
                except Exception as exc:
                    success = False
                    error = repr(exc)
                elapsed = perf_counter()-start
                writer.writerow([BITS,k,trial,"sage", "", "",int(success),
                                 elapsed,"","",error])
                print(f"k={k} trial={trial} sage success={success} time={elapsed:.3f}s", flush=True)
                for m,t in LATTICE_PARAMETERS:
                    start = perf_counter()
                    metrics = {}
                    error = ""
                    try:
                        factors,metrics = recover_prime_high_bits(
                            N,p_high,k,m=m,t=t,max_vectors=m+t)
                        success = factors is not None and p in factors
                    except Exception as exc:
                        success = False
                        error = repr(exc)
                    elapsed = perf_counter()-start
                    writer.writerow([BITS,k,trial,"custom_lll",m,t,int(success),
                                     elapsed,metrics.get("lll_seconds",""),
                                     metrics.get("dimension",""),error])
                    print(f"k={k} trial={trial} m={m} t={t} success={success} time={elapsed:.3f}s", flush=True)
                fh.flush()
    print("Saved:",output)


if __name__ == "__main__":
    main()
