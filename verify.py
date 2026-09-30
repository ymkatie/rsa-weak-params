"""Shared checks used by every attack.

verify_factors()  - did the attack really factor N?
verify_key()      - rebuild the private key from p, q and prove it decrypts.
"""
import secrets
from Crypto.Util.number import inverse


def verify_factors(N, p, q):
    """True if p and q are non-trivial factors of N."""
    if p is None or q is None:
        return False
    p, q = int(p), int(q)
    return p > 1 and q > 1 and p * q == N


def verify_key(N, e, p, q):
    """Rebuild d from the recovered p, q and check that it decrypts a random
    message encrypted with the public key. This is the 'we broke the key' proof
    to show in the report, not just 'we found two numbers'."""
    if not verify_factors(N, p, q):
        return False
    phi = (int(p) - 1) * (int(q) - 1)
    d = inverse(e, phi)
    m = secrets.randbelow(N - 2) + 2
    c = pow(m, e, N)
    return pow(c, d, N) == m
