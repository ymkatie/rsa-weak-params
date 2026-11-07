"""Shared-prime attack correctness, controls, and benchmark integration."""
import csv
import tempfile
import unittest
from math import gcd
from unittest.mock import patch

from attacks.shared_prime import shared_prime_gcd
from keygen.weak_shared_prime import weak_shared_prime
from bench.run_shared_prime import make_key, attack, check
from bench.bench import run_sweep
from verify import verify_key


class SharedPrimeTests(unittest.TestCase):
    def test_known_pair_and_unrelated_key(self):
        factors, iterations = shared_prime_gcd([101 * 113, 101 * 127, 131 * 137])
        self.assertEqual(factors, [(101, 113), (101, 127), None])
        self.assertEqual(iterations, 3)

    def test_empty_singleton_and_coprime_collections(self):
        for values in ([], [15], [15, 77, 221]):
            with self.subTest(values=values):
                factors, iterations = shared_prime_gcd(iter(values))
                self.assertEqual(factors, [None] * len(values))
                self.assertEqual(iterations, len(values) * (len(values) - 1) // 2)

    def test_duplicate_moduli_need_an_independent_collision(self):
        self.assertEqual(shared_prime_gcd([15, 15]), ([None, None], 1))
        self.assertEqual(shared_prime_gcd([15, 15, 21]),
                         ([(3, 5), (3, 5), (3, 7)], 3))

    def test_both_factors_shared_with_different_neighbours(self):
        # A naive gcd(N, product_of_others) gives N for each of these keys.
        self.assertEqual(shared_prime_gcd([15, 21, 35]),
                         ([(3, 5), (3, 7), (5, 7)], 3))

    def test_invalid_moduli(self):
        for value in (0, -15, 3, 4, 100):
            with self.subTest(value=value), self.assertRaises(ValueError):
                shared_prime_gcd([15, value])
        for value in (True, 15.0, "15", None):
            with self.subTest(value=value), self.assertRaises(TypeError):
                shared_prime_gcd([value])

    def test_generator_validation(self):
        for args in ((16, 4, 1), (33, 4, 1), (64, 1, 0),
                     (64, 4, -1), (64, 4, 3), (32, 10000, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                weak_shared_prime(*args)
        with self.assertRaises(TypeError):
            weak_shared_prime(64, 4, True)

    def test_exact_collision_counts_and_decryption(self):
        for pairs in (0, 1, 3):
            keys = weak_shared_prime(bits=64, key_count=6, shared_pairs=pairs)
            self.assertEqual(len({key[0] for key in keys}), 6)
            collisions = sum(gcd(a[0], b[0]) > 1
                             for i, a in enumerate(keys) for b in keys[i + 1:])
            self.assertEqual(collisions, pairs)
            factors, iterations = shared_prime_gcd(key[0] for key in keys)
            self.assertEqual(iterations, 15)
            self.assertEqual(sum(pair is not None for pair in factors), 2 * pairs)
            for (N, e, p, q), pair in zip(keys, factors):
                self.assertEqual(N.bit_length(), 64)
                self.assertEqual(p.bit_length(), 32)
                self.assertEqual(q.bit_length(), 32)
                self.assertLess(p, q)
                self.assertEqual(e, 65537)
                self.assertEqual(gcd(e, (p - 1) * (q - 1)), 1)
                if pair is not None:
                    self.assertEqual(pair, (p, q))
                    self.assertTrue(verify_key(N, e, *pair))

    def test_2048_bit_recovery(self):
        key = make_key(1, bits=2048, key_count=2)
        out = attack(key)
        self.assertEqual(out["recovered_keys"], 2)
        self.assertEqual(out["iterations"], 1)
        self.assertTrue(check(key, out))
        self.assertFalse(check(key, {**out, "_factors": [None, None]}))

    def test_checker_rejects_false_positives_and_truncated_results(self):
        key = make_key(0, bits=64, key_count=2)
        out = attack(key)
        self.assertTrue(check(key, out))
        self.assertFalse(check(key, {**out, "_factors": []}))
        self.assertFalse(check(key, {**out, "_factors": [key["keys"][0][2:], None]}))

    def test_csv_logs_measurements_without_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("bench.bench.RESULTS", directory):
                path = run_sweep("shared_prime", "shared_pairs", [0, 1, 2],
                                 lambda pairs: make_key(pairs, bits=64, key_count=4),
                                 attack, check, trials=1, verbose=False)
            with open(path, newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual([row["recovered_keys"] for row in rows], ["0", "2", "4"])
        for row in rows:
            self.assertEqual(row["success"], "True")
            self.assertEqual(row["iterations"], "6")
            self.assertEqual(set(row), {"shared_pairs", "trial", "n_bits", "success",
                                       "time_s", "iterations", "recovered_keys",
                                       "key_count", "expected_recovered"})


if __name__ == "__main__":
    unittest.main()
