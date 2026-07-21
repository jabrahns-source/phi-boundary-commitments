#!/usr/bin/env python3
"""
Z3 Bit-Vector Formal Verification of the Linear Basis Decomposition
for Fibonacci-weighted state sequences (Theorem 1).

Author: Jacarri Sanders / Even The Odds Foundry LLC
Date: 2026-07-20
Re-verified: 2026-07-20

Proves that for every block length m in {4, 8, 16, 32},
the identity

    sum_i k_i * F_{n+i+1}  ==  A * F_{n+1} + B * F_n

holds over unsigned 64-bit modular arithmetic for all k_i, Fn, Fn1
(where A, B are the n-invariant coefficients defined in the paper).
"""

from z3 import *
import sys

def verify_multi_m(m_list=None):
    if m_list is None:
        m_list = [4, 8, 16, 32]

    all_ok = True
    print("=" * 60)
    print("Z3 Bit-Vector Verification — Linear Collapse Identity")
    print("phi-boundary-commitments / Even The Odds Foundry")
    print("=" * 60)

    for m in m_list:
        s = Solver()

        # k_i : 32-bit unsigned (typical ADC / sensor width)
        k = [BitVec(f"k_{i}", 32) for i in range(m)]
        # Zero-extend to 64-bit working registers
        kw = [ZeroExt(32, ki) for ki in k]

        # Exact Fibonacci constants computed in Python (arbitrary precision)
        F = [0, 1]
        for _ in range(2, m + 5):
            F.append(F[-1] + F[-2])

        # A and B expressions (64-bit BitVec)
        A = sum(kw[i] * F[i + 1] for i in range(m))
        B = sum(kw[i] * F[i]     for i in range(m))

        Fn  = BitVec("Fn",  64)
        Fn1 = BitVec("Fn1", 64)

        # Expanded weighted sum
        S = sum(kw[i] * (F[i + 1] * Fn1 + F[i] * Fn) for i in range(m))

        # Target reduced form
        target = A * Fn1 + B * Fn

        # Assert the negation of the identity; expect UNSAT
        s.add(S != target)

        result = s.check()
        if result == unsat:
            print(f"[PASS] m = {m:2d}  — equality holds for all inputs over Z/2^64Z")
        else:
            print(f"[FAIL] m = {m:2d}  — {result}")
            all_ok = False
            if result == sat:
                print("  Model:", s.model())

    print("=" * 60)
    if all_ok:
        print("All block lengths verified successfully.")
        return 0
    else:
        print("Verification FAILED for one or more block lengths.")
        return 1


def print_fib_bounds():
    """Confirm the u64 overflow boundary used in the paper."""
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    f93 = fib(93)
    f94 = fib(94)
    max_u64 = (1 << 64) - 1
    print("\nRegister Headroom Check:")
    print(f"  F_93 = {f93}")
    print(f"  F_94 = {f94}")
    print(f"  2^64-1 = {max_u64}")
    print(f"  F_93 < 2^64-1 : {f93 < max_u64}")
    print(f"  F_94 > 2^64-1 : {f94 > max_u64}")
    assert f93 < max_u64 and f94 > max_u64
    print("  Boundary confirmed: n <= 93 is safe for u64 Fibonacci tables.")


if __name__ == "__main__":
    print_fib_bounds()
    sys.exit(verify_multi_m())
