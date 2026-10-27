"""Generate balanced RSA primes with a deliberately short private exponent.

Choose a short d, then e = d^(-1) mod phi(N); e cannot be fixed at 65537.
These are deliberately insecure educational keys.
"""
import secrets
from math import gcd

from Crypto.Util.number import getPrime


def weak_wiener(bits=2048, d_bits=500):
    """Return (N, e, p, q, d), with exact modulus and exponent bit lengths.

    Even modulus sizes ensure equal-sized primes and p < q < 2*p.
    d_bits may cross the Wiener boundary to measure empirical failures.
    """
    if bits < 16 or bits % 2:
        raise ValueError("bits must be even and at least 16")
    if not 2 <= d_bits <= bits - 2:
        raise ValueError("d_bits must be between 2 and bits - 2")
    while True:
        p, q = sorted((getPrime(bits // 2), getPrime(bits // 2)))
        N = p * q
        phi = (p - 1) * (q - 1)
        if p == q or N.bit_length() != bits:
            continue
        # Reuse the expensive primes while sampling an invertible d. Bound
        # retries because tiny ranges (e.g. d_bits=2, only d=3) may contain
        # no exponent coprime to this phi; then generate fresh primes.
        for _ in range(128):
            d = secrets.randbits(d_bits) | (1 << (d_bits - 1)) | 1
            if gcd(d, phi) == 1:
                e = pow(d, -1, phi)
                return N, e, p, q, d
