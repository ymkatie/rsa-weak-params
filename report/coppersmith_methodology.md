# Coppersmith: partial-prime high-bit recovery

## Threat model
Given RSA modulus N=pq and the most significant bits of p, represent
p=p_high+x with 0<=x<2^k. The unknown x is a small root of f(x)=p_high+x
modulo the unknown divisor p of N. No factor is passed to the attack.

## Implementations
- `attacks/coppersmith.sage`: SageMath `small_roots` baseline.
- `attacks/coppersmith_lattice.sage`: explicit integer polynomial shifts,
  coefficient scaling, lattice construction, LLL reduction, integer-root
  extraction and GCD verification.

For the monic linear polynomial f(x), construct shifts
N^(m-i) f(x)^i for i=0,...,m-1 and x^j f(x)^m for j=0,...,t-1.
Scale coefficient of x^k by X^k to encode |x|<X, then apply LLL.
Reconstruct integer polynomials from short vectors and test their integer
roots using gcd(N,p_high+x). These are experimental parameters; not every
choice of m,t yields a successful lattice attack.

## Experiments
`sage bench/compare_coppersmith.sage` compares methods on the SAME RSA keys,
logging modulus size, unknown bits, method, lattice parameters, recovery
success, total runtime, LLL runtime and lattice dimension.
`python3 -m bench.plot_coppersmith` plots success and runtime.

For final experiments, increase trials and repeat at 1024/2048-bit moduli,
then refine the transition range. Distinguish measured thresholds from
theoretical bounds and record machine/SageMath version.

## Correctness and limitations
Check recovered factors multiply to N and match the generated primes.
The custom implementation handles only a monic linear univariate polynomial
and is not a substitute for general multivariate Coppersmith solvers.
A balanced 2048-bit RSA prime has 1024 bits, but beta=0.5 is not
necessarily a valid lower bound for every random prime; use a conservative
beta justified by prime size for theoretical comparisons.
Results should not be claimed before running experiments.

## Attribution
Conceptual comparison: https://github.com/kionactf/coppersmith
This is an independent educational implementation, not a copy of its code.
