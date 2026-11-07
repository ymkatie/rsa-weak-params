"""Sweep disjoint shared-prime pairs in a fixed-size RSA collection."""
import argparse

from attacks.shared_prime import shared_prime_gcd
from bench.bench import run_sweep
from keygen.weak_shared_prime import weak_shared_prime
from verify import verify_key

BITS = 2048
KEY_COUNT = 16
TRIALS = 3
SHARED_PAIRS = [0, 1, 2, 4, 8]


def make_key(shared_pairs, bits=BITS, key_count=KEY_COUNT):
    keys = weak_shared_prime(bits, key_count, shared_pairs)
    return {"N": keys[0][0], "e": keys[0][1], "keys": keys,
            "log": {"key_count": key_count, "expected_recovered": 2 * shared_pairs}}


def attack(key):
    # Only public moduli cross the attack boundary.
    factors, iterations = shared_prime_gcd(item[0] for item in key["keys"])
    return {"_factors": factors, "iterations": iterations,
            "recovered_keys": sum(pair is not None for pair in factors)}


def check(key, out):
    keys, factors = key["keys"], out["_factors"]
    if len(factors) != len(keys):
        return False
    for i, ((N, e, p, q), pair) in enumerate(zip(keys, factors)):
        # Ground truth uses generated secrets, outside the timed attack.
        vulnerable = any(i != j and (p in other[2:] or q in other[2:])
                         for j, other in enumerate(keys))
        if vulnerable:
            if pair != (p, q) or not verify_key(N, e, *pair):
                return False
        elif pair is not None:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, default=BITS)
    parser.add_argument("--keys", type=int, default=KEY_COUNT)
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--shared-pairs", type=int, nargs="+", default=None)
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    values = args.shared_pairs if args.shared_pairs is not None else [
        v for v in SHARED_PAIRS if v <= args.keys // 2]
    run_sweep("shared_prime", "shared_pairs", values,
              lambda v: make_key(v, args.bits, args.keys), attack, check,
              trials=args.trials)


if __name__ == "__main__":
    main()
