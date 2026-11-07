# RSA Weak Parameters and Implementation Flaw Attacks

Research project benchmarking factorisation and key-recovery attacks on **synthetic, deliberately vulnerable RSA keys** at real-world modulus sizes. The project compares attack success, runtime, algorithmic work, and how weak parameters scale with the modulus.

**Project roles:** Fermat and Coppersmith are the focus of one workstream; Wiener is a separate collaborator workstream. All three remain in this shared repository.

> **Scope:** The experiments do **not** demonstrate that normally generated 2048-, 3072-, or 4096-bit RSA keys are insecure. Success depends on a deliberately constructed weakness or leaked secret information.

## Repository map

| Location | Purpose |
| --- | --- |
| `keygen/` | Deliberately weak RSA key generation |
| `attacks/fermat.py` | Difference-of-squares factorisation of close primes |
| `attacks/coppersmith.sage` | SageMath `small_roots()` baseline for known high bits of a prime |
| `attacks/coppersmith_lattice.sage` | Explicit polynomial shifts, lattice construction, LLL, root verification |
| `attacks/wiener.py` | Small-private-exponent recovery (collaborator workstream) |
| `bench/` | Attack benchmarks and plotting scripts |
| `tests/` | Correctness tests |
| `results/` | Historical and scaling CSV/PNG results (see [results index](results/README.md)) |
| `report/` | Methodology notes |
| `verify.py` | Factor and reconstructed-key checks |
| `run_all.py` | **Legacy** original Fermat/Wiener runs only; does not run all recent experiments |

## Environment

Run from the repository root. Python experiments use:

```bash
python3 -m pip install -r requirements.txt
```

Coppersmith additionally requires a working **SageMath** installation:

```bash
sage --version
```

Keep the benchmark environment and machine specifications in the FYP report. Key generation is excluded from measured attack time unless a specific script explicitly documents otherwise.

## Run the Fermat experiments

```bash
python3 -m unittest tests.test_fermat_refined -v
python3 -m bench.run_fermat           # original 2048-bit sweep (overwrites results/fermat.csv)
python3 -m bench.run_fermat_refined   # refined 2048-bit threshold (overwrites results/fermat_refined.csv)
python3 -m bench.scale_fermat --trials 10  # 2048/3072/4096; writes results/fermat_scaling.csv
python3 -m bench.plot_fermat_refined
python3 -m bench.plot_rsa_scaling     # also plots Wiener if its scaling CSV exists
python attacks/fermat.py        # demo: factor one 2048-bit key
python -m bench.run_fermat      # sweep the prime gap, writes results/fermat.csv (~1.5 min)
python -m bench.plot_fermat     # writes results/fermat.png
python attacks/wiener.py        # demo: recover d and factor a 2048-bit key
python -m bench.run_wiener      # sweep d size, writes results/wiener.csv
python -m bench.plot_wiener     # writes results/wiener.png
python attacks/shared_prime.py # demo: recover two keys sharing a prime
python -m bench.run_shared_prime  # 2048-bit collections; includes no-reuse control
python -m bench.plot_shared_prime # writes results/shared_prime.png
python run_all.py               # all of the above
```

`bench.scale_fermat` defaults to a cap of **2^20** checks, while the older Fermat sweeps use **2^24**. Differences in empirical recovery boundaries are therefore expected. A cap-limited failure is **not** a proof of infeasibility.

## Run the Coppersmith experiments

```bash
sage tests/test_coppersmith_lattice.sage
sage bench/compare_coppersmith.sage  # refined 2048-bit comparison; overwrites its named CSV
sage bench/scale_coppersmith.sage    # 3072-bit pilot; overwrites results/coppersmith_scaling_3072.csv
```

The source modules' Sage `load()` calls can print their standalone 512-bit demos; these are **not** benchmark observations.

### Coppersmith at 4096 bits

A separate, non-destructive **4096-bit pilot** is available:

```bash
sage bench/scale_coppersmith_4096.sage
```

By default it runs one trial each with 850, 900 and 950 unknown low bits, using custom 12×12 and 16×16 lattice configurations. It prints progress before every attempt and writes `results/coppersmith_scaling_4096.csv`.

For a SageMath baseline on identical keys (may be significantly slower):

```bash
sage bench/scale_coppersmith_4096.sage --trials 3 --with-sage --overwrite
```

The benchmark refuses to overwrite an existing 4096-bit CSV unless `--overwrite` is specified. To keep both pilots, pass a different path using `--output results/coppersmith_scaling_4096_baseline.csv`. Commit or back up the first CSV before rerunning.

The known-high-bits attack becomes more challenging as unknown low bits approach the theoretical scale around `modulus_bits / 4` (about 1024 for a 4096-bit N), but the exact observed boundary depends on the lattice configuration and SageMath parameters. The defaults are a pilot, **not** a full boundary characterization.

## Shared-prime GCD attack

If `N1 = p*q` and `N2 = p*r` with distinct primes, `gcd(N1, N2) = p`.
Both public moduli can then be factored and their private exponents rebuilt.
This attack needs a collection of public keys containing prime reuse; a
single independent key does not supply that information. See
[Mining Your Ps and Qs (Heninger et al., 2012)](https://factorable.net/paper.html).

`attacks.shared_prime.shared_prime_gcd(moduli)` returns `(factors, iterations)`.
The factors list follows input order, with sorted `(p, q)` tuples or `None`.
Duplicate moduli alone do not reveal a factor, but duplicates can still be
recovered if a different modulus shares a prime. The implementation also
handles keys whose two primes are shared with different neighbouring keys.
Inputs are assumed to be two-prime RSA moduli; the attack validates integer
inputs and proper factors, but does not certify primality.

This is a pairwise baseline: for `K` keys it always performs `K*(K-1)/2`
GCDs. It is not the product/remainder-tree batch GCD algorithm used for very
large collections. `iterations` counts GCD calls, not Euclidean steps.

The generator creates exact-size moduli with `e=65537`, globally unique primes
except for deliberately shared ones, and shuffled key order. By default the
primes have their top two bits set to ensure exact-size products without
repeatedly rejecting partners for a fixed shared prime. The
benchmark uses 16 keys per collection, 2048-bit moduli, three trials, and
0, 1, 2, 4, or 8 disjoint shared-prime pairs. Exactly twice that many keys
should be recovered. This sweep studies reuse prevalence, not a mathematical
success threshold; the GCD count is fixed for a fixed collection size.

Only the public-modulus attack is timed. Generation and decryption verification
are outside the timer. CSV `success` means the entire collection matches ground
truth, including correctly returning no factors in the zero-reuse control.
`recovered_keys` records actual compromises. Factors and private keys are not
written to CSV. The plot shows recovery counts and attack-only runtime.

A smaller 2048-bit sweep (overwrites `results/shared_prime.csv`):

```powershell
python -m bench.run_shared_prime --bits 2048 --keys 4 --trials 1 --shared-pairs 0 1 2
python -m bench.plot_shared_prime
```

## Adding a new attack (the pattern for Week 3)

Plot an existing data file without replacing earlier figures:

```bash
python3 -m bench.plot_coppersmith --input results/coppersmith_comparison_2048_refined.csv --prefix coppersmith_2048_refined
```

The original Coppersmith plotting command still works with the default input `results/coppersmith_comparison.csv`:

```bash
python3 -m bench.plot_coppersmith
```

The attack model is **partial disclosure of the high bits of one RSA prime**. This is a leakage/implementation-flaw experiment, rather than evidence that all primes of a particular size are weak.

## Wiener (collaborator)

```bash
python3 -m bench.run_wiener
python3 -m bench.plot_wiener
python3 -m bench.scale_wiener --trials 10
```

These are maintained separately from the Fermat/Coppersmith workstream.

## Testing and result interpretation

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

SageMath tests are invoked separately as shown above. Some test and benchmark scripts create random keys, so empirical success rates vary across runs.

- Always verify recovered factors satisfy `p*q == N`.
- Compare attacks using the same modulus sizes **and appropriately scaled vulnerable parameters**, not only raw bit lengths.
- Record trial counts, software versions, compute hardware and runtime limits.
- Treat close-to-threshold success rates as empirical estimates, not exact theoretical bounds.
- Benchmarks overwrite the **specified output CSV** when rerun. Commit or copy important results first.

See [results index](results/README.md), [Coppersmith methodology](report/coppersmith_methodology.md), and [RSA scaling methodology](report/rsa_scaling_methodology.md).
