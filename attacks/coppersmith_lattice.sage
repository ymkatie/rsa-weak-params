"""Educational univariate Coppersmith implementation for known high bits of RSA p.

Use SageMath: sage attacks/coppersmith_lattice.sage
The attack knows N and the high bits of p; p is used only in the demo to verify.
This implementation exposes the lattice and LLL rather than calling small_roots().
"""
from sage.all import ZZ, QQ, Zmod, PolynomialRing, matrix, gcd, random_prime
from time import perf_counter


def shifted_polynomials(N, f, m, t):
    """Howgrave-Graham shifts for a monic LINEAR polynomial f(x)."""
    if m < 1 or t < 1 or f.degree() != 1 or f.leading_coefficient() != 1:
        raise ValueError("Require m,t >= 1 and monic linear f")
    R = f.parent()
    x = R.gen()
    return [N**(m-i) * f**i for i in range(m)] + [x**j * f**m for j in range(t)]


def build_lattice(polys, X):
    """Row i is coefficients of g_i(X*x); integer scaling by X**degree."""
    X = ZZ(X)
    if X <= 0:
        raise ValueError("X must be positive")
    dimension = max(g.degree() for g in polys) + 1
    if len(polys) != dimension:
        raise ValueError("Shift polynomials must form a square basis")
    return matrix(ZZ, [[ZZ(g[k]) * X**k for k in range(dimension)]
                       for g in polys])


def integer_roots_from_reduced_basis(B, X, max_vectors=8):
    """Extract candidate integer roots of short lattice polynomials."""
    R = PolynomialRing(ZZ, "x")
    x = R.gen()
    roots = set()
    for row in B.rows()[:max_vectors]:
        if any(ZZ(row[k]) % (ZZ(X)**k) != 0 for k in range(B.ncols())):
            continue
        h = sum((ZZ(row[k]) // (ZZ(X)**k)) * x**k
                for k in range(B.ncols()))
        if h == 0:
            continue
        for root, multiplicity in h.roots(ring=ZZ):
            if 0 <= root < X:
                roots.add(ZZ(root))
    return sorted(roots)


def recover_prime_high_bits(N, p_high, unknown_bits, m=3, t=3,
                            max_vectors=8):
    """Return (factors, metrics). factors is (p,q) or None.

    This is an experimental LLL construction; no recovery guarantee is implied.
    """
    N, p_high = ZZ(N), ZZ(p_high)
    if N <= 1 or unknown_bits < 1 or p_high <= 0:
        raise ValueError("Invalid modulus, prefix or unknown bit count")
    X = ZZ(2)**unknown_bits
    if p_high % X != 0:
        raise ValueError("p_high must have zeroed unknown low bits")
    R = PolynomialRing(ZZ, "x")
    x = R.gen()
    f = x + p_high
    start = perf_counter()
    shifts = shifted_polynomials(N, f, m, t)
    B = build_lattice(shifts, X)
    construction_s = perf_counter() - start
    start = perf_counter()
    reduced = B.LLL()
    lll_s = perf_counter() - start
    start = perf_counter()
    roots = integer_roots_from_reduced_basis(reduced, X, max_vectors)
    factors = None
    for root in roots:
        p = gcd(N, p_high + root)
        if 1 < p < N and N % p == 0:
            factors = (ZZ(p), ZZ(N // p))
            break
    recovery_s = perf_counter() - start
    return factors, {
        "dimension": B.nrows(),
        "construction_seconds": construction_s,
        "lll_seconds": lll_s,
        "root_seconds": recovery_s,
        "candidate_count": len(roots),
    }


def demo(bits=512, unknown_bits=60):
    half = bits // 2
    while True:
        p = random_prime(ZZ(2)**half - 1, lbound=ZZ(2)**(half-1))
        q = random_prime(ZZ(2)**half - 1, lbound=ZZ(2)**(half-1))
        N = p*q
        if p != q and N.nbits() == bits:
            break
    p_high = (p >> unknown_bits) << unknown_bits
    factors, metrics = recover_prime_high_bits(N, p_high, unknown_bits)
    print("RSA bits:", N.nbits(), "unknown bits:", unknown_bits)
    print("Recovered:", factors is not None and p in factors)
    print("Metrics:", metrics)


if __name__ == "__main__":
    demo()
