# RSA weak-parameter attacks at real key sizes

SC4010 project, and the base for the FYP. Each attack is run against genuine
2048-bit RSA keys that contain one deliberate flaw. The flaw is then swept to
find where the attack stops working.

```
keygen/    weak key generators (one per flaw)
attacks/   the attacks (they only see the public key)
bench/     benchmark harness, one runner and one plot script per attack
results/   CSV + PNG output
report/    report drafts
verify.py  proves a recovered key really decrypts
run_all.py reproduces every result
```

## Setup (macOS, Apple Silicon)

```bash
cd rsa-weak-params
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

If `gmpy2` fails to build, run `brew install gmp mpfr libmpc` and try again,
or use conda: `conda install -c conda-forge gmpy2`.

### SageMath (only needed from Week 3, Coppersmith)

The easiest route on an M-series Mac is a separate conda environment:

```bash
conda create -n sage -c conda-forge sage python=3.11
conda activate sage
sage -c "print(factor(2**64+1))"     # expect 274177 * 67280421310721
```

If conda can't solve the environment, install the prebuilt macOS app from
github.com/3-manifolds/Sage_macOS instead. Avoid the Docker image on an M-series
Mac: it is x86-only and runs slowly under emulation.

## Run it

Run everything from the repo root:

```bash
python attacks/fermat.py        # demo: factor one 2048-bit key
python -m bench.run_fermat      # sweep the prime gap, writes results/fermat.csv (~1.5 min)
python -m bench.plot_fermat     # writes results/fermat.png
python run_all.py               # all of the above
```

## Adding a new attack (the pattern for Weeks 2 and 3)

1. `keygen/weak_<name>.py`: generate a 2048-bit key with the flaw controlled by one parameter.
2. `attacks/<name>.py`: the attack. It takes public values only.
3. `bench/run_<name>.py`: define `make_key(param)`, `attack(key)` and `check(key, out)`,
   then call `run_sweep(...)`. Only `attack` is timed. Keys starting with `_` in its
   output (recovered secrets) are not written to the CSV.
4. `bench/plot_<name>.py`, then add both to `run_all.py`.

## Week 1 results: Fermat

2048-bit N, e = 65537, 5 keys per gap, capped at 2^24 iterations (~3 s):

| log2 abs(p−q) | Result |
|---|---|
| 100–512 | factored in 1 iteration, under 0.1 ms |
| 514–524 | factored; median iterations grow from 3 to about 1.7M |
| 526 | borderline (0–4 of 5 within the cap across runs) |
| 528+ | exceeds the cap |

- Measured iteration counts match the prediction (p−q)² / (8√N) closely.
  Every extra bit of gap costs 4× more.
- Extrapolating at the measured ~3.8M iterations/s, a gap of 540 bits would take
  ~75 years and 560 bits ~10^14 years. Randomly generated 1024-bit primes differ
  in roughly the top bit, so a normal key has a gap near 1023 bits and is safe.
- Guideline for the report: reject any key where |p − q| < 2^(nbits/2 − 100).
  FIPS 186-5 requires |p − q| > 2^(nbits/2 − 100). Check the exact clause before citing it.
