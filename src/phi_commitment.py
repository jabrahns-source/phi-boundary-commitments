#!/usr/bin/env python3
"""
Reference implementation of Deterministic State Reduction via Golden-Ratio
Polynomials and the randomized omega_strong commitment.

Pure integer arithmetic only. No floating-point operations.

Author: Jacarri Sanders / Even The Odds Foundry LLC
"""

from __future__ import annotations
import hashlib
import os
from dataclasses import dataclass
from typing import List, Sequence, Tuple


# Precomputed Fibonacci table up to F_93 (safe for u64)
def _build_fib_table(max_n: int = 93) -> List[int]:
    F = [0, 1]
    for _ in range(2, max_n + 1):
        F.append(F[-1] + F[-2])
    return F

FIB = _build_fib_table(93)
assert FIB[93] == 12200160415121876738
assert FIB[93] < (1 << 64)


@dataclass(frozen=True)
class PhiState:
    """
    The two-dimensional integer state (A, B) that fully captures any
    Fibonacci-weighted sequence for a fixed pre-quantized vector k.
    """
    A: int
    B: int
    m: int  # original block length (for reference)

    @classmethod
    def from_k(cls, k: Sequence[int]) -> "PhiState":
        """
        Compute the n-invariant coefficients A, B from a pre-quantized
        non-negative integer vector k = (k_0, ..., k_{m-1}).
        """
        if not k:
            raise ValueError("k must be non-empty")
        for ki in k:
            if not isinstance(ki, int) or ki < 0:
                raise ValueError("all k_i must be non-negative integers")

        m = len(k)
        if m > 93:
            # Still mathematically correct, but A/B may exceed u64;
            # we allow it in pure Python (arbitrary precision).
            pass

        A = 0
        B = 0
        for i, ki in enumerate(k):
            # F[i] and F[i+1] are always defined for i < m <= 93 in the table
            # For larger m we fall back to on-the-fly (still exact)
            Fi   = FIB[i]   if i   < len(FIB) else _fib(i)
            Fi1  = FIB[i+1] if i+1 < len(FIB) else _fib(i+1)
            A += ki * Fi1
            B += ki * Fi
        return cls(A=A, B=B, m=m)

    def eval(self, n: int) -> int:
        """
        Evaluate S(k, n) = A * F_{n+1} + B * F_n
        using only table lookups and two multiplications + one addition.
        Safe for n <= 92 (so that n+1 <= 93).
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n + 1 >= len(FIB):
            # Fall back to arbitrary-precision Fibonacci for demonstration
            return self.A * _fib(n + 1) + self.B * _fib(n)
        return self.A * FIB[n + 1] + self.B * FIB[n]

    def __repr__(self) -> str:
        return f"PhiState(A={self.A}, B={self.B}, m={self.m})"


def _fib(n: int) -> int:
    """Arbitrary-precision Fibonacci (only used beyond table)."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def commit(hn: bytes, A: int, B: int, r: bytes) -> bytes:
    """
    omega_strong(hn, A, B, r) = SHA256( hn || A || B || r )

    Canonical encoding:
      - hn : exactly 32 bytes
      - A  : 8-byte big-endian unsigned (or more if A does not fit; we use
             the minimal number of bytes that is a multiple of 8 and sufficient)
      - B  : same rule
      - r  : exactly 32 bytes

    For strict u64 regimes A and B always fit in 8 bytes when k_i are 32-bit
    and m <= 32.
    """
    if len(hn) != 32:
        raise ValueError("hn must be 32 bytes")
    if len(r) != 32:
        raise ValueError("r must be 32 bytes")
    if A < 0 or B < 0:
        raise ValueError("A and B must be non-negative")

    # Fixed-width for the common u64 case; fall back gracefully
    a_bytes = A.to_bytes(8, "big") if A < (1 << 64) else A.to_bytes((A.bit_length() + 7) // 8, "big")
    b_bytes = B.to_bytes(8, "big") if B < (1 << 64) else B.to_bytes((B.bit_length() + 7) // 8, "big")

    # For maximum interoperability in the paper's setting we pad/truncate to 8
    # when possible; here we keep the exact byte length after the 8-byte preference.
    payload = hn + a_bytes + b_bytes + r
    return hashlib.sha256(payload).digest()


def open_commitment(c: bytes, hn: bytes, A: int, B: int, r: bytes) -> bool:
    """Return True iff the opening is valid for commitment c."""
    return c == commit(hn, A, B, r)


def generate_salt() -> bytes:
    """Cryptographically strong 256-bit blinding salt."""
    return os.urandom(32)


# ---------------------------------------------------------------------------
# Convenience: direct evaluation of the original sum (for testing only)
# ---------------------------------------------------------------------------
def direct_sum(k: Sequence[int], n: int) -> int:
    """Compute S(k, n) by the original definition (slow path, for verification)."""
    total = 0
    for i, ki in enumerate(k):
        total += ki * _fib(n + i + 1)
    return total


if __name__ == "__main__":
    # Quick self-check
    k = [3, 1, 4, 1, 5, 9]
    state = PhiState.from_k(k)
    print("State:", state)

    for n in [0, 1, 5, 10, 40, 90]:
        s_red = state.eval(n)
        s_dir = direct_sum(k, n)
        match = "OK" if s_red == s_dir else "MISMATCH"
        print(f"n={n:3d}  reduced={s_red}  direct={s_dir}  [{match}]")

    hn = b"\x11" * 32
    r = generate_salt()
    c = commit(hn, state.A, state.B, r)
    print("Commitment:", c.hex())
    print("Open valid:", open_commitment(c, hn, state.A, state.B, r))
