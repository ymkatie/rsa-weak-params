"""Wiener's continued-fraction attack against RSA keys with unusually small d.

Public inputs only: (N, e). Returns (d, p, q) or None.
"""
from math import isqrt


def continued_fraction(a: int, b: int):
    """Yield partial quotients of a/b exactly, using integer arithmetic."""
    while b:
        quotient, remainder = divmod(a, b)
        yield quotient
        a, b = b, remainder


def convergents(partial_quotients):
    """Yield (numerator, denominator) for successive convergents."""
    prev2_n, prev_n = 0, 1
    prev2_d, prev_d = 1, 0
    for a in partial_quotients:
        n = a * prev_n + prev2_n
        d = a * prev_d + prev2_d
        yield n, d
        prev2_n, prev_n = prev_n, n
        prev2_d, prev_d = prev_d, d


def wiener(e: int, N: int):
    """Recover (d, p, q) if the key is vulnerable; otherwise return None."""
    if N <= 1 or e <= 1:
        raise ValueError('N and e must be greater than 1')
    for k, d in convergents(continued_fraction(e, N)):
        if k == 0 or (e * d - 1) % k:
            continue
        phi = (e * d - 1) // k
        s = N - phi + 1  # p + q
        discriminant = s * s - 4 * N
        if discriminant < 0:
            continue
        t = isqrt(discriminant)
        if t * t != discriminant or (s + t) % 2:
            continue
        p, q = (s + t) // 2, (s - t) // 2
        if p > 1 and q > 1 and p * q == N:
            return d, p, q
    return None


if __name__ == '__main__':
    from keygen.weak_wiener import weak_wiener
    N, e, d, p, q = weak_wiener(2048, 480)
    result = wiener(e, N)
    print('2048-bit key recovered:', result is not None and result[0] == d)
