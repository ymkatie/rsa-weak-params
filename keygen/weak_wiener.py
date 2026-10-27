"""Generate deliberately weak RSA keys for controlled experiments only."""
import secrets
from Crypto.Util.number import getPrime, GCD, inverse


def weak_wiener(bits=2048, d_bits=480):
    """Return (N, e, d, p, q) with d of exactly d_bits and gcd(d,phi)=1."""
    if bits < 32 or d_bits < 2 or d_bits >= bits // 2:
        raise ValueError('Require bits >= 32 and 2 <= d_bits < bits//2')
    while True:
        p = getPrime(bits // 2)
        q = getPrime(bits - bits // 2)
        if p == q:
            continue
        N = p * q
        if N.bit_length() != bits:
            continue
        phi = (p - 1) * (q - 1)
        while True:
            d = secrets.randbits(d_bits - 1) | (1 << (d_bits - 1)) | 1
            if GCD(d, phi) == 1:
                return N, int(inverse(d, phi)), d, p, q
