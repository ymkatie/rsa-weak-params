# Wiener and shared-prime GCD at 4096 bits

## Method

These experiments use deliberately weak synthetic RSA keys with exact
4096-bit moduli. Three independently generated trials are run per setting,
matching the repetition count in the saved Coppersmith 4096-bit experiments.
Random keys are not seeded; rerunning reproduces the procedure, not the keys.

- Wiener: private exponent lengths 1020, 1022, 1024, 1026, and 1028 bits.
  Each recovered private exponent and factorization is checked against the
  generated key, and encryption/decryption is verified. The CSV records the
  exact sufficient-bound predicate `(3*d)**4 < N`.
- Shared-prime GCD: four keys per collection with 0, 1, or 2 disjoint
  shared-prime pairs. Expected recoveries are 0, 2, and 4 respectively.
  Each collection requires six pairwise GCDs. Verification checks exact
  factors and decryption for vulnerable keys and rejects false recoveries
  for unrelated keys.
- Only the attack is timed with `perf_counter`; generation and verification
  are excluded. Raw CSVs contain measurements, not secret factors.
- For the GCD zero-reuse control, `success=True` means the result correctly
  contains zero recoveries. It does not mean unrelated keys were broken.

## Reproduction

```bash
python -u -m bench.run_4096
python -m bench.plot_wiener --input results/wiener_4096.csv --output results/wiener_4096.png
python -m bench.plot_shared_prime --input results/shared_prime_4096.csv --output results/shared_prime_4096.png
```

The runner refuses to overwrite existing CSVs unless `--overwrite` is passed.
Original 2048-bit results are preserved. Increase `--trials` for stronger
estimates of recovery probability.

## Environment

Run date: 2026-11-10. Windows 11 (10.0.26300), x64 Python 3.12.14,
PyCryptodome 4.2.0, Matplotlib 3.11.2. Processor reported by Python:
Intel64 Family 6 Model 154 Stepping 4, GenuineIntel.

## Wiener results

| Private exponent bits | Recoveries | Below sufficient bound | Median attack time (ms), all trials |
| --- | --- | --- | --- |
| 1020 | 3/3 | 3/3 | 4.134 |
| 1022 | 3/3 | 3/3 | 4.138 |
| 1024 | 1/3 | 0/3 | 42.763 |
| 1026 | 1/3 | 0/3 | 43.724 |
| 1028 | 0/3 | 0/3 | 44.627 |

All six sampled keys satisfying the sufficient bound were recovered. Two
additional keys outside that bound were recovered. Failed attempts examine
the entire continued fraction, so their runtimes are larger than early
successful recoveries. Raw evidence: `results/wiener_4096.csv`.

## Shared-prime GCD results

| Shared pairs | Keys recovered per collection | Correct trials | Median attack time (ms) |
| --- | --- | --- | --- |
| 0 | 0/4 | 3/3 | 0.302 |
| 1 | 2/4 | 3/3 | 0.318 |
| 2 | 4/4 | 3/3 | 3.798 |

All nine collections matched the intended recoveries, with six GCD calls
per collection. The zero-reuse control produced no false recoveries.
Raw evidence: `results/shared_prime_4096.csv`. The two-pair timings were
more variable (2.716 to 9.417 ms); this small sequential run does not isolate
system load from parameter effects, so the plotted increase should not be
treated as an established scaling trend.

## Validation

All 23 existing unit tests passed. The new runner's overwrite refusal was
checked against the completed Wiener CSV. Both plots were rendered and
visually inspected. Original 2048-bit CSVs and plots were left unchanged.

## Interpretation limits

Three trials are pilot evidence, not precise success-probability estimates.
Wiener's sufficient bound is `d < N^(1/4)/3` for balanced primes; the
1024-bit quarter-modulus scale is not a hard success cutoff. Success beyond
the sufficient bound depends on the key. Shared-prime GCD relies on prime
reuse, which increasing the modulus size does not repair. Neither experiment
demonstrates a break of normally generated RSA keys. Timings from this
Windows/Python run should not be directly ranked against Coppersmith timings
from another machine or runtime.
