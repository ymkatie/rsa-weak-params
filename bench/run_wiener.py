"""Run from repo root: python -m bench.run_wiener

Outputs per-trial measurements to results/wiener.csv.
"""
import csv
from pathlib import Path
from time import perf_counter

from attacks.wiener import wiener
from keygen.weak_wiener import weak_wiener

BITS = 2048
D_BITS = sorted(set(range(400, 541, 10)) | set(range(500, 521, 2)))
TRIALS = 10


def main():
    output = Path('results/wiener.csv')
    output.parent.mkdir(exist_ok=True, parents=True)
    with output.open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['modulus_bits', 'd_bits', 'trial', 'success', 'attack_seconds'])
        for d_bits in D_BITS:
            successes = 0
            for trial in range(1, TRIALS + 1):
                N, e, d, p, q = weak_wiener(BITS, d_bits)
                start = perf_counter()
                result = wiener(e, N)
                elapsed = perf_counter() - start
                success = result is not None and result[0] == d and {result[1], result[2]} == {p, q}
                successes += int(success)
                writer.writerow([BITS, d_bits, trial, int(success), f'{elapsed:.9f}'])
            file.flush()
            print(f'd_bits={d_bits}: {successes}/{TRIALS} recovered')
    print('Saved:', output)


if __name__ == '__main__':
    main()
