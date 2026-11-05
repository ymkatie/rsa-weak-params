"""Run: python3 -m unittest tests.test_fermat_refined -v"""
import unittest

from attacks.fermat import fermat
from bench.run_fermat_refined import exact_expected_iterations


class FermatRefinedTests(unittest.TestCase):
    def test_close_primes_one_check(self):
        p, q = 101, 103
        N = p*q
        rp, rq, checks = fermat(N, max_iters=10)
        self.assertEqual({rp, rq}, {p, q})
        self.assertEqual(checks, 1)
        self.assertEqual(exact_expected_iterations(N,p,q), checks)

    def test_exact_iterations_agree_with_algorithm(self):
        for p,q in [(101, 113), (101, 151), (1009, 1013), (1009, 1201)]:
            with self.subTest(p=p,q=q):
                N=p*q
                expected=exact_expected_iterations(N,p,q)
                rp,rq,checks=fermat(N,max_iters=expected)
                self.assertEqual({rp,rq},{p,q})
                self.assertEqual(checks,expected)

    def test_iteration_cap_is_censoring(self):
        p,q=101,151
        N=p*q
        expected=exact_expected_iterations(N,p,q)
        self.assertGreater(expected,1)
        rp,rq,checks=fermat(N,max_iters=expected-1)
        self.assertEqual((rp,rq),(None,None))
        self.assertEqual(checks,expected-1)


if __name__ == "__main__":
    unittest.main()
