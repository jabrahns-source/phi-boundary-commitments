#!/usr/bin/env python3
"""
Unit tests for the phi-boundary state reduction and commitment scheme.
"""

import os
import sys
import unittest

# Allow importing from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from phi_commitment import (
    PhiState,
    commit,
    open_commitment,
    generate_salt,
    direct_sum,
    FIB,
)


class TestLinearCollapse(unittest.TestCase):
    def test_basic_identity(self):
        k = [1, 2, 3, 4]
        state = PhiState.from_k(k)
        for n in range(0, 50):
            self.assertEqual(state.eval(n), direct_sum(k, n))

    def test_zero_vector(self):
        k = [0, 0, 0]
        state = PhiState.from_k(k)
        self.assertEqual(state.A, 0)
        self.assertEqual(state.B, 0)
        self.assertEqual(state.eval(10), 0)

    def test_single_element(self):
        k = [7]
        state = PhiState.from_k(k)
        # A = 7 * F_1 = 7 * 1 = 7
        # B = 7 * F_0 = 0
        self.assertEqual(state.A, 7)
        self.assertEqual(state.B, 0)
        for n in [0, 1, 5, 20]:
            self.assertEqual(state.eval(n), 7 * FIB[n + 1])

    def test_large_n_safe(self):
        k = [1, 1, 1]
        state = PhiState.from_k(k)
        # n=92 is the largest where n+1=93 still fits the table
        s = state.eval(92)
        self.assertIsInstance(s, int)
        self.assertGreater(s, 0)

    def test_known_fib_values(self):
        self.assertEqual(FIB[0], 0)
        self.assertEqual(FIB[1], 1)
        self.assertEqual(FIB[10], 55)
        self.assertEqual(FIB[93], 12200160415121876738)


class TestCommitment(unittest.TestCase):
    def test_round_trip(self):
        k = [5, 3, 2]
        state = PhiState.from_k(k)
        hn = b"\xab" * 32
        r = generate_salt()
        c = commit(hn, state.A, state.B, r)
        self.assertTrue(open_commitment(c, hn, state.A, state.B, r))

    def test_binding_different_state(self):
        """Different (A,B) with same salt and hn must produce different commitment
        (except with negligible probability of collision)."""
        s1 = PhiState.from_k([1, 0, 0])
        s2 = PhiState.from_k([0, 1, 0])
        hn = b"\x00" * 32
        r = generate_salt()
        c1 = commit(hn, s1.A, s1.B, r)
        c2 = commit(hn, s2.A, s2.B, r)
        self.assertNotEqual(c1, c2)

    def test_hiding_different_salts(self):
        """Same state, different salts → different commitments."""
        state = PhiState.from_k([9, 9, 9])
        hn = b"\xff" * 32
        r1 = generate_salt()
        r2 = generate_salt()
        c1 = commit(hn, state.A, state.B, r1)
        c2 = commit(hn, state.A, state.B, r2)
        self.assertNotEqual(c1, c2)

    def test_invalid_open(self):
        state = PhiState.from_k([1])
        hn = b"\x11" * 32
        r = generate_salt()
        c = commit(hn, state.A, state.B, r)
        # Wrong salt
        self.assertFalse(open_commitment(c, hn, state.A, state.B, generate_salt()))
        # Wrong A
        self.assertFalse(open_commitment(c, hn, state.A + 1, state.B, r))


class TestEdgeCases(unittest.TestCase):
    def test_negative_k_rejected(self):
        with self.assertRaises(ValueError):
            PhiState.from_k([1, -1, 2])

    def test_empty_k_rejected(self):
        with self.assertRaises(ValueError):
            PhiState.from_k([])


if __name__ == "__main__":
    unittest.main()
