# Formal Verification Certificates (Z3 SMT)

This directory contains machine-checkable SMT certificates that underwrite the algebraic claims of the Kerna-Ledger / Even The Odds Foundry research track.

## Existing Certificates (φ-boundary commitments)

| Script | Claim |
|--------|-------|
| `verify_linear_collapse.py` | A·F_{n+1} + B·F_n identity for the linear collapse |
| `verify_boundedness.py` | A, B stay inside u64 for m ≤ 32 and 32-bit k_i |

## New Certificates — Deterministic Decoherence Annihilation (Aug 2026)

Paper: *Deterministic Decoherence Annihilation: Indefinite Causal Order Routing via Fibonacci-Prime Galois Fields*

| Script | Claim |
|--------|-------|
| `verify_f_matrix_unitarity.py` | The Golden-Ratio F-Matrix is unitary (F F† = I) under the defining equation φ² = φ + 1 |
| `verify_galois_zero_divisors.py` | Zero-divisors exist in d=8 (sat) but are impossible in the Fibonacci-prime field F_89 (unsat) |

### How to run

```bash
pip install z3-solver
python verification/verify_f_matrix_unitarity.py
python verification/verify_galois_zero_divisors.py
```

Both scripts exit with code 0 and print the certificate results when the claims hold.

These certificates are intentionally lightweight, self-contained, and CI-ready. They can be re-executed on every commit to keep the formal guarantees live.
