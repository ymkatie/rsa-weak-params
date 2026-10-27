"""Sweep private-exponent size: python -m bench.run_wiener."""
from attacks.wiener import wiener
from bench.bench import run_sweep
from keygen.weak_wiener import weak_wiener
from verify import verify_key

BITS = 2048
TRIALS = 5
D_BITS = [100, 200, 300, 400, 450, 500, 505, 508, 509, 510,
          511, 512, 513, 514, 516, 520, 530, 540]


def make_key(d_bits):
    N, e, p, q, d = weak_wiener(BITS, d_bits)
    return {"N": N, "e": e, "p": p, "q": q, "d": d,
            "log": {"d_bits_actual": d.bit_length(),
                    "below_wiener_bound": (3 * d) ** 4 < N}}


def attack(key):
    p, q, d, iterations = wiener(key["N"], key["e"])
    return {"_p": p, "_q": q, "_d": d, "iterations": iterations}


def check(key, out):
    if out["_d"] != key["d"] or not verify_key(key["N"], key["e"], out["_p"], out["_q"]):
        return False
    # Also exercise the recovered d directly, not just the reconstructed key.
    return all(pow(pow(m, key["e"], key["N"]), out["_d"], key["N"]) == m
               for m in (2, 42, key["N"] - 1))


if __name__ == "__main__":
    run_sweep("wiener", "d_bits", D_BITS, make_key, attack, check, trials=TRIALS)
