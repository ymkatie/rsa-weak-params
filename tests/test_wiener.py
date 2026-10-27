"""Run with: python -m unittest discover -s tests -v."""
import unittest

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


if __name__ == "__main__":
    unittest.main()
