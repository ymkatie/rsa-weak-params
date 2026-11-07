"""Generate RSA collections with exactly controlled prime reuse."""
import secrets
from math import gcd
from operator import index

from Crypto.Util.number import getPrime


def weak_shared_prime(bits=2048, key_count=16, shared_pairs=1):
    """Return shuffled (N, e, p, q) tuples with e=65537 and exact N sizes.

    Each of shared_pairs disjoint pairs shares one prime: exactly
    2*shared_pairs keys are vulnerable. All other primes are globally unique.
    Zero pairs produces a negative control. Secrets are for verification only.
    Primes have their top two bits set, guaranteeing exact-size products
    without potentially long retries against a fixed shared prime.
    """
    if any(isinstance(v, bool) for v in (bits, key_count, shared_pairs)):
        raise TypeError("Generator parameters must be integers")
    bits, key_count, shared_pairs = map(index, (bits, key_count, shared_pairs))
    if bits < 32 or bits % 2:
        raise ValueError("bits must be even and at least 32")
    if key_count < 2 or not 0 <= shared_pairs <= key_count // 2:
        raise ValueError("Require key_count >= 2 and 0 <= shared_pairs <= key_count//2")
    # Guard against exhausting the finite pool for educational tiny keys.
    if key_count > 2 ** (bits // 2 - 8):
        raise ValueError("Too many keys for the requested prime size")
    used = set()
    e = 65537

    def fresh_prime():
        while True:
            p = getPrime(bits // 2)
            if p >> (bits // 2 - 2) == 3 and p not in used and gcd(e, p - 1) == 1:
                used.add(p)
                return p

    def make_key(p):
        q = fresh_prime()
        a, b = sorted((p, q))
        return p * q, e, a, b

    keys = []
    for _ in range(shared_pairs):
        p = fresh_prime()
        keys.extend((make_key(p), make_key(p)))
    while len(keys) < key_count:
        keys.append(make_key(fresh_prime()))
    secrets.SystemRandom().shuffle(keys)
    return keys
