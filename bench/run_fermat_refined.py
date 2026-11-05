"""Refined Fermat gap benchmark; run: python3 -m bench.run_fermat_refined.

Does not overwrite results/fermat.csv. Failed cap-limited trials are censored,
not evidence that the modulus could never be factored.
"""
import csv
import math
import os
import time
from statistics import median

from attacks.fermat import fermat
from keygen.weak_fermat import weak_fermat
from verify import verify_factors

BITS = 2048
GAPS = [522, 523, 524, 525, 526, 527, 528]
TRIALS = 20
MAX_ITERS = 2**24
OUTFILE = "results/fermat_refined.csv"


def exact_expected_iterations(N, p, q):
    """Exact number of checks made by fermat() if allowed to finish.

    Starts at ceil(sqrt(N)), checks that candidate first (iteration 1).
    For odd RSA primes, (p+q)//2 is the first valid successful candidate.
    """
    a0 = math.isqrt(N)
    if a0 * a0 < N:
        a0 += 1
    return (p + q) // 2 - a0 + 1


def approximate_iterations(N, p, q):
    """Leading-order cost plus the iteration-1 counting convention."""
    return max(1, (p-q)**2 / (8 * math.sqrt(N)) + 1) if N.bit_length() < 1024 else (
        max(1, (p-q)**2 // (8 * math.isqrt(N)) + 1)
    )


def main():
    os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
    with open(OUTFILE, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "modulus_bits", "requested_gap_bits", "actual_gap_bits", "trial",
            "success", "censored_by_iteration_cap", "max_iterations",
            "iterations", "exact_expected_iterations",
            "approximate_iterations", "time_seconds", "iterations_per_second"])
        writer.writeheader()
        for gap in GAPS:
            results = []
            for trial in range(1, TRIALS + 1):
                N, e, p, q = weak_fermat(bits=BITS, gap_bits=gap)
                exact = exact_expected_iterations(N, p, q)
                approx = approximate_iterations(N, p, q)
                start = time.perf_counter()
                rp, rq, iterations = fermat(N, max_iters=MAX_ITERS)
                elapsed = time.perf_counter() - start
                success = verify_factors(N, rp, rq) and {rp, rq} == {p, q}
                capped = not success and exact > MAX_ITERS
                if success and iterations != exact:
                    raise AssertionError(
                        f"Fermat check mismatch: measured {iterations}, predicted {exact}")
                if not success and exact <= MAX_ITERS:
                    raise AssertionError("Unexpected failure within iteration cap")
                row = {
                    "modulus_bits": N.bit_length(),
                    "requested_gap_bits": gap,
                    "actual_gap_bits": abs(p - q).bit_length(),
                    "trial": trial,
                    "success": int(success),
                    "censored_by_iteration_cap": int(capped),
                    "max_iterations": MAX_ITERS,
                    "iterations": iterations,
                    "exact_expected_iterations": exact,
                    "approximate_iterations": approx,
                    "time_seconds": f"{elapsed:.9f}",
                    "iterations_per_second": f"{iterations/elapsed:.2f}" if elapsed else "",
                }
                writer.writerow(row)
                fh.flush()
                results.append(row)
                print(f"gap={gap} trial={trial:02d} success={success} "
                      f"checks={iterations} expected={exact} time={elapsed:.3f}s",
                      flush=True)
            wins = sum(r["success"] for r in results)
            print(f"gap={gap}: {wins}/{TRIALS} recovered; "
                  f"median time {median(float(r['time_seconds']) for r in results):.3f}s",
                  flush=True)
    print("Saved:", OUTFILE)


if __name__ == "__main__":
    main()
