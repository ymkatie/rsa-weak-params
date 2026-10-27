"""Recover RSA keys with small d using convergents of the public ratio e/N.

For balanced primes p < q < 2*p, d < N**(1/4)/3 is a sufficient
condition. Some keys beyond that bound also work; failure is not a proof
that a key is secure. All arithmetic below is exact integer arithmetic.
"""
from math import isqrt


def wiener(N, e):
    """Return (p, q, d, iterations), or (None, None, None, iterations).

    iterations counts all continued-fraction convergents examined, including
    the initial 0/1. Inputs must be an odd modulus N > 3 and 1 < e < N.
    """
    if N <= 3 or N % 2 == 0 or not 1 < e < N:
        raise ValueError("Expected odd N > 3 and 1 < e < N")

    numerator, denominator = e, N
    k_prev2, k_prev1 = 0, 1
    d_prev2, d_prev1 = 1, 0
    iterations = 0
    while denominator:
        a, remainder = divmod(numerator, denominator)
        numerator, denominator = denominator, remainder
        k = a * k_prev1 + k_prev2
        d = a * d_prev1 + d_prev2
        k_prev2, k_prev1 = k_prev1, k
        d_prev2, d_prev1 = d_prev1, d
        iterations += 1

        # ed - k*phi(N) = 1, so a correct k must divide ed - 1.
        if k == 0 or (e * d - 1) % k:
            continue
        phi = (e * d - 1) // k
        if not 0 < phi < N:
            continue
        # p + q = N - phi(N) + 1; solve x^2 - (p+q)x + N = 0.
        s = N - phi + 1
        discriminant = s * s - 4 * N
        if discriminant < 0:
            continue
        root = isqrt(discriminant)
        if root * root != discriminant or (s - root) % 2:
            continue
        p, q = (s - root) // 2, (s + root) // 2
        if 1 < p < q and p * q == N:
            return p, q, d, iterations
    return None, None, None, iterations


if __name__ == "__main__":
    import os
    import sys
    import time
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from keygen.weak_wiener import weak_wiener
    from verify import verify_key

    N, e, p, q, d = weak_wiener(bits=2048, d_bits=500)
    print(f"Target: {N.bit_length()}-bit N, {d.bit_length()}-bit private exponent")
    start = time.perf_counter()
    rp, rq, rd, iters = wiener(N, e)
    elapsed = time.perf_counter() - start
    print(f"Examined {iters} convergents in {elapsed * 1000:.2f} ms")
    print(f"Private exponent recovered exactly: {rd == d}")
    print(f"Recovered key decrypts correctly: {verify_key(N, e, rp, rq)}")
