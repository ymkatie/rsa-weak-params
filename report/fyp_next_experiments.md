# Fermat and Coppersmith: controlled FYP experiments

**Scope:** Synthetic deliberately weak or leaked RSA keys only. Wiener and shared-prime attacks are other project workstreams.

## A. Controls (new)

Fermat: independent balanced primes vs deliberately close primes, at the
**same 2048/3072/4096-bit modulus sizes** and identical attack iteration cap.
Independent keys are sampled with normal prime generation, but this experiment
does not assert they are immune to every possible RSA attack. The script also
records the *exact number of checks Fermat would require* for each generated
key, even if the attack reaches its computational cap.

```bash
python3 -m bench.control_fermat --trials 3
```

Coppersmith: use the same modulus with its actual leaked high-bit prime prefix
versus an unrelated decoy prefix from a different generated key. This is an
**incorrect-information control**, not an experiment on fully secret primes.
Without any prime leakage there is no known prefix with which to construct
the polynomial used by this attack.

```bash
sage bench/control_coppersmith.sage
```

Default outputs: `results/fermat_controls.csv` and
`results/coppersmith_controls.csv`. Both refuse to overwrite existing CSVs
unless given `--overwrite` or a different `--output`.

## B. Lattice-size sweep at the observed 4096-bit boundary

The existing 4096-bit runner accepts any `--lattice-sizes`. A size of
`s` means `m=t=s`, yielding an integer lattice of dimension `2s`.
Study sensitivity to m,t without modifying the attack implementation.

Pilot (one trial, unique output):

```bash
sage bench/scale_coppersmith_4096.sage --unknown-bits 950 955 960 --trials 1 --lattice-sizes 6 7 8 10 --output results/coppersmith_lattice_sweep_4096.csv
```

Repeat with 10 trials in a **new file** if pilot is successful. 20x20
LLL may use substantially more time or memory. Note that increasing dimension
does not mathematically guarantee success and the best m,t values can depend
on the unknown-bit length.

## C. Produce analysis and report-ready plots

```bash
python3 -m bench.analyze_fyp
```

Outputs grouped `results/fyp_analysis/summary.csv` plus separate success-rate
and runtime plots per source CSV and modulus. It reads historical CSV schemas
(`seconds` or `total_seconds`, `dimension` or `lattice_dimension`)
without rewriting the underlying experimental data.

Interpret timing comparisons conservatively: configurations may use different
lattice parameters and Sage `small_roots` can use an algorithmically
different basis or optimisation. Failed attacks have recorded runtimes, so
the median over *all* attempts and the median over successes are separate.

## D. Methodology and limitations

- Generated prime factors are retained in memory for validation only, never
  exported into experimental CSVs.
- Record hardware, Sage/Python versions, trial counts, randomness, runtime
  caps, and the exact LLL configuration in the final dissertation.
- Repeat settings independently; a 3/3 result is a pilot, not a precise
  estimate of a 100% success probability.
- Fermat failures after an iteration limit are **censored** (not proof of
  cryptographic security). For normal RSA prime gaps, predicted checks are
  astronomical even though a short control run terminates quickly.
- Coppersmith high-bit recovery requires specific leaked information.
  The decoy control tests incorrect knowledge, **not** a complete absence of
  exploitable side channels or a proof of RSA security.
- To cite a result, keep the raw CSV and runner version in the same Git commit.
