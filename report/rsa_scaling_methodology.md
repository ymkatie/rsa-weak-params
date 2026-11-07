# Scaling RSA weak-parameter attacks across modulus sizes

These scripts test deliberately weak *synthetic* RSA keys, not third-party keys.

## Execution
From the repository root:

```bash
python3 -m bench.scale_fermat
python3 -m bench.scale_wiener
python3 -m bench.plot_rsa_scaling
sage bench/scale_coppersmith.sage
```

Start with default pilot trials (5 for Fermat/Wiener, 3 for Coppersmith).
Increase to ten trials for Fermat/Wiener using `--trials 10` after verifying
correctness. Fermat's default iteration cap is 2^20; a higher cap can be
requested with `--max-iters 16777216`, but increases runtime for failures.

## Fair comparison

- Sizes for Fermat and Wiener: 2048 / 3072 / 4096 bits.
- For each modulus size n, study weak-parameter lengths relative to n/4.
  This controls for the different theoretical scales.
- Fermat: prime-gap bits n/4 + {10,12,14}; count exact required checks
  separately from completed iteration-limited attack checks.
- Wiener: private exponent bits n/4 + {-4,-2,0,2,4}; record
  whether the sufficient bound (3d)^4 < N holds.
- Coppersmith: 3072-bit pilot, 580/620/640 unknown bits.
  Compare identical keys against SageMath small_roots and custom LLL.
- Time only attacks, not vulnerable key generation. Store one row per trial.
- Recovery failures under an iteration cap are **censored**, not
  proofs of cryptographic security.
- For reproducibility record system specs, Sage/Python versions and
  experimental configuration; increase trial counts near transitions.

Output files are distinct from pre-existing results. Do not describe expected
trends as measured outcomes until the scripts have been run.
