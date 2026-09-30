"""Generate a real-size RSA key whose primes are deliberately too close.

gap_bits controls the flaw: |p - q| is roughly 2**gap_bits.
Fermat's method is fast while |p - q| is well below N**(1/4)
(= 512 bits for a 2048-bit modulus) and hopeless well above it.
"""
import secrets
import gmpy2
from Crypto.Util.number import getPrime, GCD

E = 65537


def weak_fermat(bits=2048, gap_bits=400, e=E):
    """Return (N, e, p, q) with |p - q| in [2**(gap_bits-1), 2**gap_bits)."""
    half = bits // 2
    while True:
        p = getPrime(half)
        # random offset of exactly gap_bits bits, so trials are not identical
        offset = secrets.randbits(gap_bits - 1) | (1 << (gap_bits - 1))
        q = int(gmpy2.next_prime(p + offset))
        N = p * q
        phi = (p - 1) * (q - 1)
        # keep the key valid: correct size, and e invertible mod phi
        if N.bit_length() == bits and q.bit_length() == half and GCD(e, phi) == 1:
            return N, e, p, q


if __name__ == "__main__":
    N, e, p, q = weak_fermat(2048, 400)
    print(f"N bits    : {N.bit_length()}")
    print(f"|p-q| bits: {abs(p - q).bit_length()}")
