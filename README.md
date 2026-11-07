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
```

`bench.scale_fermat` defaults to a cap of **2^20** checks, while the older Fermat sweeps use **2^24**. Differences in empirical recovery boundaries are therefore expected. A cap-limited failure is **not** a proof of infeasibility.

## Run the Coppersmith experiments

```bash
sage tests/test_coppersmith_lattice.sage
sage bench/compare_coppersmith.sage  # refined 2048-bit comparison; overwrites its named CSV
sage bench/scale_coppersmith.sage    # 3072-bit pilot; overwrites results/coppersmith_scaling_3072.csv
```

The source modules' Sage `load()` calls can print their standalone 512-bit demos; these are **not** benchmark observations.

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
