"""Run from repo root: sage bench/run_coppersmith.sage

Writes per-trial data to results/coppersmith.csv. This can be slow near the
root-size limit; start with one epsilon and fewer unknown-bit settings.
"""
import csv
from pathlib import Path
from time import perf_counter

load('attacks/coppersmith.sage')

BITS = 2048
UNKNOWN_BITS = [400, 420, 440, 450, 460, 480, 500, 510, 512]
EPSILONS = [0.03, 0.01, 0.005]
TRIALS = 3


def main():
    output = Path('results/coppersmith.csv')
    output.parent.mkdir(exist_ok=True, parents=True)
    with output.open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['modulus_bits', 'unknown_bits', 'epsilon', 'trial', 'success', 'attack_seconds', 'error'])
        for unknown_bits in UNKNOWN_BITS:
            for trial in range(1, TRIALS + 1):
                p, q, N = generate_balanced_key(BITS)
                p_high = (p >> unknown_bits) << unknown_bits
                for epsilon in EPSILONS:
                    start = perf_counter()
                    error = ''
                    try:
                        result = coppersmith_high_bits(N, p_high, unknown_bits,
                                                       beta=0.5, epsilon=epsilon)
                        success = result is not None and p in result
                    except (ArithmeticError, ValueError, RuntimeError) as exc:
                        success = False
                        error = str(exc)
                    elapsed = perf_counter() - start
                    writer.writerow([BITS, unknown_bits, epsilon, trial,
                                     int(success), f'{elapsed:.9f}', error])
                    file.flush()
                    print(f'unknown={unknown_bits}, epsilon={epsilon}, trial={trial}: '
                          f'{"success" if success else "failure"} ({elapsed:.2f}s)')
    print('Saved:', output)


if __name__ == '__main__':
    main()
