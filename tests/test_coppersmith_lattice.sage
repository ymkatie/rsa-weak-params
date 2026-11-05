"""Run from repo root: sage tests/test_coppersmith_lattice.sage"""
from sage.all import ZZ, PolynomialRing
load("attacks/coppersmith_lattice.sage")

R = PolynomialRing(ZZ, "x")
x = R.gen()
polys = shifted_polynomials(101, x+7, 2, 2)
assert len(polys) == 4
B = build_lattice(polys, 8)
assert B.nrows() == 4 and B.ncols() == 4
assert B.det() != 0
try:
    recover_prime_high_bits(100, 123, 4)
except ValueError:
    pass
else:
    raise AssertionError("Expected invalid prefix error")
# Small fixed RSA test: p=1009, q=1013, unknown lower 4 bits
p, q = ZZ(1009), ZZ(1013)
N = p*q
k = 4
p_high = (p >> k) << k
factors, metrics = recover_prime_high_bits(N, p_high, k, m=3, t=3)
assert factors is not None and set(factors) == {p,q}, (factors,metrics)
print("Coppersmith lattice tests passed",metrics)
