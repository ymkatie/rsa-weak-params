"""Fermat's factorisation.

Write N = a^2 - b^2 = (a - b)(a + b). Start a at ceil(sqrt(N)) and step up
until a^2 - N is a perfect square b^2; then p = a - b, q = a + b.

The number of steps is about (p - q)^2 / (8 * sqrt(N)), so it is instant when
p and q are close and grows with the square of the gap. For a 2048-bit N the
break-even point is |p - q| around 2**512 = N**(1/4).
"""
import gmpy2


def fermat(N, max_iters=10**6):
    """Return (p, q, iterations). p and q are None if max_iters is reached."""
    N = gmpy2.mpz(N)
    a = gmpy2.isqrt(N)
    if a * a < N:
        a += 1
    b2 = a * a - N
    for i in range(1, max_iters + 1):
        if gmpy2.is_square(b2):
            b = gmpy2.isqrt(b2)
            return int(a - b), int(a + b), i
        # (a+1)^2 - N = a^2 - N + 2a + 1: update incrementally, no big multiply
        b2 += 2 * a + 1
        a += 1
    return None, None, max_iters


if __name__ == "__main__":
    import sys, os, time
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from keygen.weak_fermat import weak_fermat
    from verify import verify_key

    N, e, p, q = weak_fermat(bits=2048, gap_bits=500)
    print(f"Target: {N.bit_length()}-bit N, |p-q| is {abs(p - q).bit_length()} bits")
    t = time.perf_counter()
    rp, rq, iters = fermat(N)
    dt = time.perf_counter() - t
    print(f"Factored in {iters} iteration(s), {dt * 1000:.2f} ms")
    print(f"p = {hex(rp)[:40]}...")
    print(f"Private key recovered and decrypts correctly: {verify_key(N, e, rp, rq)}")
