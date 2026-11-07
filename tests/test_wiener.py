"""Run with: python -m unittest discover -s tests -v."""
import unittest
from math import gcd, isqrt
from unittest.mock import patch

from attacks.wiener import wiener
from keygen.weak_wiener import weak_wiener
from bench.run_wiener import attack, check


class WienerTests(unittest.TestCase):
    def test_known_example(self):
        p, q, d, iterations = wiener(90581, 17993)
        self.assertEqual((p, q, d), (239, 379, 5))
        self.assertGreater(iterations, 0)

    def test_unsuccessful_recovery(self):
        # Textbook RSA example with a large private exponent (2753).
        p, q, d, iterations = wiener(3233, 17)
        self.assertEqual((p, q, d), (None, None, None))
        self.assertGreater(iterations, 0)

    def test_invalid_public_keys(self):
        for N, e in [(0, 3), (3, 2), (10, 3), (15, 1), (15, 15)]:
            with self.subTest(N=N, e=e), self.assertRaises(ValueError):
                wiener(N, e)

    def test_noninteger_public_keys(self):
        for N, e in [(90581.0, 17993), (90581, 17993.0),
                     ("90581", 17993), (90581, None),
                     (True, 3), (90581, True)]:
            with self.subTest(N=N, e=e), self.assertRaises(TypeError):
                wiener(N, e)

    def test_integer_protocol(self):
        class IntegerLike:
            def __init__(self, value):
                self.value = value

            def __index__(self):
                return self.value

        self.assertEqual(wiener(IntegerLike(90581), IntegerLike(17993))[:3],
                         (239, 379, 5))

    def test_balanced_keys_below_bound_deterministically(self):
        # Independent exhaustive prime construction; no random key generator.
        primes = [n for n in range(101, 1000, 2)
                  if all(n % divisor for divisor in range(2, isqrt(n) + 1))]
        recovered = 0
        for i, p in enumerate(primes):
            for q in primes[i + 1:]:
                if q >= 2 * p:
                    break
                N, phi = p * q, (p - 1) * (q - 1)
                for d in range(3, 11, 2):
                    if (3 * d) ** 4 >= N or gcd(d, phi) != 1:
                        continue
                    e = pow(d, -1, phi)
                    with self.subTest(p=p, q=q, d=d):
                        rp, rq, rd, iterations = wiener(N, e)
                        self.assertEqual((rp, rq, rd), (p, q, d))
                        self.assertGreater(iterations, 0)
                        # Include non-units: decryption must also work for
                        # messages divisible by either recovered prime.
                        for message in (0, 1, p, q, N - 1):
                            self.assertEqual(pow(pow(message, e, N), rd, N), message)
                    recovered += 1
        self.assertGreater(recovered, 100)

    def test_prime_and_square_moduli_do_not_produce_keys(self):
        for N in (101, 239 ** 2):
            for e in (3, 17, N - 2):
                with self.subTest(N=N, e=e):
                    self.assertEqual(wiener(N, e)[:3], (None, None, None))

    def test_generated_keys_and_benchmark_verification(self):
        for bits, d_bits in [(64, 2), (256, 32), (2048, 500)]:
            with self.subTest(bits=bits, d_bits=d_bits):
                N, e, p, q, d = weak_wiener(bits, d_bits)
                self.assertEqual(N.bit_length(), bits)
                self.assertEqual(d.bit_length(), d_bits)
                self.assertTrue(p < q < 2 * p)
                self.assertEqual((e * d) % ((p - 1) * (q - 1)), 1)
                self.assertLess((3 * d) ** 4, N)
                key = dict(N=N, e=e, p=p, q=q, d=d)
                out = attack(key)
                self.assertEqual((out["_p"], out["_q"], out["_d"]), (p, q, d))
                self.assertTrue(check(key, out))
                self.assertFalse(check(key, {**out, "_d": d + 1}))

    def test_generator_validation(self):
        for bits, d_bits in [(8, 2), (65, 8), (64, 1), (64, 63)]:
            with self.subTest(bits=bits, d_bits=d_bits), self.assertRaises(ValueError):
                weak_wiener(bits, d_bits)

    def test_tiny_exponent_retries_with_fresh_primes(self):
        # d_bits=2 permits only d=3. The first prime pair has phi divisible
        # by 3, so resampling d alone can never produce a usable key.
        with patch("keygen.weak_wiener.getPrime", side_effect=[193, 197, 227, 233]) as primes:
            with patch("keygen.weak_wiener.secrets.randbits", return_value=0):
                N, e, p, q, d = weak_wiener(16, 2)
        self.assertEqual(primes.call_count, 4)
        self.assertEqual((N, p, q, d), (227 * 233, 227, 233, 3))
        self.assertEqual((e * d) % ((p - 1) * (q - 1)), 1)


if __name__ == "__main__":
    unittest.main()
