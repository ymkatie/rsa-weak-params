"""Week 1 checkpoint: sweep the prime gap on 2048-bit keys and find where
Fermat's method stops working.

Run from the repo root:  python -m bench.run_fermat
"""
import gmpy2

from bench.bench import run_sweep
from keygen.weak_fermat import weak_fermat
from attacks.fermat import fermat
from verify import verify_key

BITS = 2048
MAX_ITERS = 2**24          # ~16.7M steps, a few seconds; beyond this we call it a fail
TRIALS = 5
GAPS = [100, 200, 300, 400, 450, 500, 505, 510, 512, 514,
        516, 518, 520, 522, 524, 526, 528, 530]


def make_key(gap_bits):
    N, e, p, q = weak_fermat(BITS, gap_bits)
    # theory: Fermat needs about (p - q)^2 / (8 sqrt N) steps
    predicted = max(1, int((p - q) ** 2 // (8 * gmpy2.isqrt(N))))
    return {"N": N, "e": e, "p": p, "q": q,
            "log": {"gap_bits_actual": abs(p - q).bit_length(),
                    "predicted_iterations": predicted}}


def attack(key):
    # the attacker only uses N; p and q stay in the key dict for checking
    rp, rq, iters = fermat(key["N"], max_iters=MAX_ITERS)
    return {"_p": rp, "_q": rq, "iterations": iters}


def check(key, out):
    return verify_key(key["N"], key["e"], out["_p"], out["_q"])


if __name__ == "__main__":
    run_sweep("fermat", "gap_bits", GAPS, make_key, attack, check, trials=TRIALS)
