"""Factor RSA moduli that share primes using pairwise public-key GCDs.

For N1=p*q and N2=p*r with distinct primes, gcd(N1, N2)=p.
This transparent baseline uses n*(n-1)/2 GCDs, not a product-tree batch GCD.
"""
from math import gcd
from operator import index


def shared_prime_gcd(moduli):
    """Return (factors, iterations), preserving input order and duplicates.

    Each factors entry is a sorted (p, q), or None if no proper factor was
    exposed. Inputs must be odd integers > 3, assumed to be two-prime RSA
    moduli; primality is not certified. Duplicate moduli alone reveal no
    proper factor. Empty and singleton collections return no recoveries.
    iterations counts every unordered pair, including duplicate pairs.
    """
    values = []
    for value in moduli:
        if isinstance(value, bool):
            raise TypeError("Moduli must be integers, not booleans")
        value = index(value)
        if value <= 3 or value % 2 == 0:
            raise ValueError("Expected odd moduli > 3")
        values.append(value)
    factors = [None] * len(values)
    iterations = 0
    for i, N in enumerate(values):
        for j in range(i + 1, len(values)):
            M = values[j]
            common = gcd(N, M)
            iterations += 1
            if 1 < common < N:
                factors[i] = tuple(sorted((common, N // common)))
            if 1 < common < M:
                factors[j] = tuple(sorted((common, M // common)))
    return factors, iterations


if __name__ == "__main__":
    import os
    import sys
    from time import perf_counter
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from keygen.weak_shared_prime import weak_shared_prime
    from verify import verify_key

    keys = weak_shared_prime(bits=2048, key_count=4, shared_pairs=1)
    start = perf_counter()
    factors, iterations = shared_prime_gcd(key[0] for key in keys)
    elapsed = perf_counter() - start
    recovered = sum(pair is not None for pair in factors)
    verified = all(verify_key(N, e, *pair)
                   for (N, e, _, _), pair in zip(keys, factors) if pair is not None)
    print(f"Recovered {recovered}/{len(keys)} 2048-bit keys using {iterations} GCDs")
    print(f"Attack time: {elapsed * 1000:.3f} ms")
    print(f"Expected two recoveries, with valid decryption: {recovered == 2 and verified}")
