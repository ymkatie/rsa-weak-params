"""Generate RSA keys with a deliberately small private exponent."""
import secrets
from Crypto.Util.number import getPrime, GCD, inverse


def weak_wiener(bits=2048, d_bits=480):
    """Return (N, e, d, p, q). d has exactly d_bits bits."""
    if bits < 32 or d_bits < 2 or d_bits >= bits // 2:
        raise ValueError("Require bits >= 32 and 2 <= d_bits < bits//2")
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
                break
        e = int(inverse(d, phi))
        return N, e, d, p, q


if __name__ == "__main__":
    N, e, d, p, q = weak_wiener()
    print(f"N bits: {N.bit_length()}, d bits: {d.bit_length()}")
