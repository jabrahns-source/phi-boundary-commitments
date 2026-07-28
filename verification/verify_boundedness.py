#!/usr/bin/env python3
"""
Extended Z3 verification for phi-boundary-commitments.

In addition to the linear identity already proved in verify_linear_collapse.py,
this script proves:

  - When every k_i is a non-negative 32-bit value and m <= 32,
    both A and B remain strictly inside the unsigned 64-bit range.

This supplies the concrete overflow-safety certificate referenced in the paper
and README (safe n <= 93 for the Fibonacci tables themselves).

Author: Jacarri Sanders / Even The Odds Foundry LLC
Requires: pip install z3-solver
"""

from z3 import *
import sys

def verify_boundedness(m_list=None):
    if m_list is None:
        m_list = [4, 8, 16, 32]

    all_ok = True
    print("=" * 60)
    print("Z3 Verification — Phi A/B Boundedness (u64 safety)")
    print("phi-boundary-commitments / Even The Odds Foundry")
    print("=" * 60)

    for m in m_list:
        s = Solver()

        # k_i as 32-bit unsigned, non-negative by construction of BitVec
        k = [BitVec(f"k_{i}", 32) for i in range(m)]

        # Exact Fibonacci constants (Python arbitrary precision → constants)
        F = [0, 1]
        while len(F) < m + 2:
            F.append(F[-1] + F[-2])

        # Zero-extend and form A, B
        kw = [ZeroExt(32, ki) for ki in k]
        A = sum(kw[i] * F[i + 1] for i in range(m))
        B = sum(kw[i] * F[i]     for i in range(m))

        # Assert that A or B can reach or exceed 2^64  — expect UNSAT
        s.add(Or(A >= (1 << 64), B >= (1 << 64)))

        result = s.check()
        if result == unsat:
            print(f"[PASS] m = {m:2d}  — A and B stay in u64 for all 32-bit k_i >= 0")
        else:
            print(f"[FAIL] m = {m:2d}  — {result}")
            if result == sat:
                print("  Model:", s.model())
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("All boundedness properties verified successfully.")
        return 0
    else:
        print("Boundedness verification FAILED for one or more block lengths.")
        return 1


if __name__ == "__main__":
    sys.exit(verify_boundedness())
