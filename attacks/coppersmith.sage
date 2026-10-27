"""Partial-prime high-bit recovery using SageMath's small_roots().

Run demo: sage attacks/coppersmith.sage
The attacker receives N, the known high-bit portion of p, and the number of
unknown low bits. The demo keeps p only for verification.
"""
from sage.all import ZZ, Zmod, PolynomialRing, gcd, random_prime


def coppersmith_high_bits(N, p_high, unknown_bits, beta=0.5, epsilon=0.01):
    """Return (p, q) on recovery, otherwise None."""
    N, p_high = ZZ(N), ZZ(p_high)
    if N <= 1 or unknown_bits < 1 or p_high % (ZZ(2) ** unknown_bits) != 0:
        raise ValueError('Invalid N or high-bit prefix')
    R = PolynomialRing(Zmod(N), 'x')
    x = R.gen()
    f = x + R(p_high)  # monic, root modulo the unknown divisor p of N
    roots = f.small_roots(X=ZZ(2) ** unknown_bits, beta=beta, epsilon=epsilon)
    for root in roots:
        factor = gcd(N, p_high + ZZ(root))
        if 1 < factor < N:
            return ZZ(factor), ZZ(N // factor)
    return None


def generate_balanced_key(bits):
    half = bits // 2
    while True:
        p = random_prime(ZZ(2)**half - 1, lbound=ZZ(2)**(half - 1))
        q = random_prime(ZZ(2)**(bits - half) - 1, lbound=ZZ(2)**(bits - half - 1))
        if p != q and (p * q).nbits() == bits:
            return p, q, p * q


def demo(bits=512, unknown_bits=100):
    p, q, N = generate_balanced_key(bits)
    p_high = (p >> unknown_bits) << unknown_bits
    result = coppersmith_high_bits(N, p_high, unknown_bits)
    print('N bits:', N.nbits(), 'unknown low bits:', unknown_bits)
    print('Recovered p:', result is not None and p in result)


if __name__ == '__main__':
    demo()
