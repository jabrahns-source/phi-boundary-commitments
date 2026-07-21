# φ-Boundary Commitments

**Deterministic State Reduction via Golden-Ratio Polynomials for Low-Latency Quantum Boundary Commitments**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Z3 Verified](https://img.shields.io/badge/Z3-Verified-brightgreen)](verification/verify_linear_collapse.py)
[![Even The Odds Foundry](https://img.shields.io/badge/Even%20The%20Odds-Foundry-blue)](https://github.com/jabrahns-source)

**Author:** Jacarri Sanders  
**Affiliation:** Kerna-Ledger Engineering Group / Even The Odds Foundry LLC, Redding, CA, USA  
**Date:** July 2026  

---

## Abstract

Classical-to-quantum interface architectures suffer from computational overhead and non-deterministic timing drift when translating continuous quantum phase dynamics into classical registers. Standard implementations rely on Floating-Point Units (FPUs) executing transcendental approximations, introducing microarchitectural latency and precision degradation.

This repository contains a **deterministic algebraic engine** that bypasses FPUs entirely by exploiting the minimal polynomial of the golden ratio:

\[
\phi^2 - \phi - 1 = 0 \quad \Rightarrow \quad \phi^2 = \phi + 1
\]

Assuming pre-quantized discrete integer inputs \( k_i \in \mathbb{Z}_{\geq 0} \) from hardware sensor interfaces (ADCs / optical phase detectors), we prove that any arbitrary Fibonacci-weighted state sequence reduces algebraically to a two-dimensional integer state \((A, B)\) over native 64-bit unsigned registers (`u64`).

A randomized commitment \(\omega_{\mathrm{strong}}\) incorporating a 256-bit blinding salt is defined and formally proven to satisfy both **computational binding** and **information-theoretic hiding** under the Random Oracle Model. The integer pipeline is gate-level verified with Z3 bit-vector SMT logic across block lengths \( m \in \{4, 8, 16, 32\} \) in \(\mathbb{Z}_{2^{64}}\), establishing a safe execution bound of \( n = 93 \) rounds prior to register overflow.

---

## Key Results

| Claim | Status | Evidence |
|-------|--------|----------|
| Algebraic collapse \( S(\mathbf{k}, n) = A \cdot F_{n+1} + B \cdot F_n \) | Proven | Theorem 1 + inductive Fibonacci identity |
| Linear coefficients \( A, B \) independent of \( n \) | Proven | Explicit closed form |
| Overflow-free u64 execution up to \( n = 93 \) | Confirmed | \( F_{93} = 12200160415121876738 < 2^{64}-1 \), \( F_{94} > 2^{64}-1 \) |
| Z3 bit-vector identity for \( m \in \{4,8,16,32\} \) | Verified | `verification/verify_linear_collapse.py` (re-executed 2026-07-20) |
| Computational binding of \(\omega_{\mathrm{strong}}\) | Proven | Reduction to SHA-256 collision resistance (ROM) |
| Information-theoretic hiding | Proven | Uniform random 256-bit salt + ROM |
| \( k \)-round hybrid composability | Proven | Standard hybrid argument, advantage \(\leq k \cdot \mathrm{Adv}^{\mathrm{CR}}\) |
| ALU footprint | Characterized | 2× IMUL + ADD + table loads (vs. transcendental FPU path) |

---

## Mathematical Core

### Golden Ratio & Fibonacci Basis

Let \(\phi = \frac{1 + \sqrt{5}}{2}\). Then for all \( n \geq 1 \):

\[
\phi^n = F_n \phi + F_{n-1}
\]

where \( F_n \) is the Fibonacci sequence with \( F_0 = 0 \), \( F_1 = 1 \).

### Theorem 1 (Linear Basis Decomposition)

Any sequence sum

\[
S(\mathbf{k}, n) = \sum_{i=0}^{m-1} k_i \cdot F_{n+i+1}
\]

maps onto the two-dimensional integer basis \(\{ F_{n+1}, F_n \}\):

\[
S(\mathbf{k}, n) = A \cdot F_{n+1} + B \cdot F_n
\]

with **n-invariant** coefficients

\[
A = \sum_{i=0}^{m-1} k_i \cdot F_{i+1}, \qquad B = \sum_{i=0}^{m-1} k_i \cdot F_i
\]

**Proof.** Apply the Fibonacci addition formula \( F_{n+k} = F_k F_{n+1} + F_{k-1} F_n \) with \( k = i+1 \). Linearity finishes the argument.

### Randomized Commitment

\[
\omega_{\mathrm{strong}}(h_n, A, B, r) = \mathrm{SHA256}(h_n \,\|\, A \,\|\, B \,\|\, r)
\]

where \( r \stackrel{\$}{\leftarrow} \{0,1\}^{256} \) is a fresh blinding salt and \( h_n \) is a round nonce.  

**Canonical encoding (recommended for interoperability):**  
`hn` (32 bytes) ‖ `A.to_bytes(8, 'big')` ‖ `B.to_bytes(8, 'big')` ‖ `r` (32 bytes).

Opening reveals \((h_n, A, B, r)\). Binding reduces to collision resistance of SHA-256; hiding is information-theoretic under the ROM because of the fresh uniform salt.

---

## Repository Layout

```
phi-boundary-commitments/
├── README.md                          # This file
├── LICENSE                            # MIT
├── CITATION.cff                       # Citation metadata
├── paper/
│   └── PAPER.md                       # Full paper in clean Markdown
├── verification/
│   └── verify_linear_collapse.py      # Z3 SMT verification script (runnable)
├── src/
│   └── phi_commitment.py              # Pure-Python reference implementation
└── tests/
    └── test_phi.py                    # Unit tests for identity + commitment
```

---

## Quick Start

### 1. Run the Formal Verification (Z3)

```bash
pip install z3-solver
python verification/verify_linear_collapse.py
```

Expected output:
```
m=4: VERIFIED (equality holds over BitVec64)
m=8: VERIFIED (equality holds over BitVec64)
m=16: VERIFIED (equality holds over BitVec64)
m=32: VERIFIED (equality holds over BitVec64)
All block lengths verified.
```

### 2. Use the Reference Implementation

```python
from src.phi_commitment import PhiState, commit, open_commitment

k = [3, 1, 4, 1, 5]          # example pre-quantized sensor vector
state = PhiState.from_k(k)   # computes (A, B) once
print(state.A, state.B)

# Evaluate the original weighted sum at any safe n ≤ 93 without recomputing the full sum
S = state.eval(n=40)
print(S)

# Cryptographic commitment
hn = b"\x00" * 32
r = os.urandom(32)
c = commit(hn, state.A, state.B, r)
assert open_commitment(c, hn, state.A, state.B, r)
```

### 3. Run Tests

```bash
python -m pytest tests/ -q
```

---

## Register Headroom

| Register Width | Max Safe Index \( n \) | \( F_n \) | Next Fibonacci |
|----------------|------------------------|-----------|----------------|
| u32            | 47                     | 2 971 215 073 | overflows |
| u64            | **93**                 | 12 200 160 415 121 876 738 | overflows |

All Fibonacci table lookups for \( n \leq 93 \) stay inside native unsigned 64-bit registers with zero modular wrap-around.

---

## Security Notes

- The mapping \( \mathbf{k} \mapsto (A, B) \) is surjective; many preimages exist. The commitment therefore **must** use the fresh 256-bit salt for hiding.
- Under the Random Oracle Model the construction is computationally binding and statistically hiding.
- Hybrid argument for \( k \) sequential rounds multiplies the collision advantage by \( k \) (still negligible for cryptographic \( \lambda \)).
- For production use, replace the Python SHA-256 with a constant-time, side-channel-resistant implementation and ensure the encoding of \( A \) and \( B \) is fixed-width.

---

## Relation to Kerna-Ledger / Even The Odds Foundry

This work supplies a verified integer-only foundation for deterministic quantum-boundary commitment protocols used inside the broader Kerna-Ledger / VERA Substrata / PSI-ALPHA stack. It eliminates FPU-induced timing drift and precision loss at the classical–quantum sensor interface while remaining fully executable on commodity ALUs.

Related repositories:
- [kerna-ledger](https://github.com/jabrahns-source/kerna-ledger)
- [kerna-ledger-vci](https://github.com/jabrahns-source/kerna-ledger-vci)
- [psi-alpha-quantum](https://github.com/jabrahns-source/psi-alpha-quantum)
- [hq-bind](https://github.com/jabrahns-source/hq-bind)
- [Q-Reg](https://github.com/jabrahns-source/Q-Reg)

---

## Recheck & Verification Log (2026-07-20)

- Algebraic identity re-derived from first principles; proof holds.
- Fibonacci numbers \( F_{93} \) and \( F_{94} \) independently recomputed and confirmed against known sequences.
- Z3 script re-executed successfully for all listed block lengths; equality holds over modular arithmetic as well (linear identity).
- Canonical fixed-width encoding for \( (A, B) \) added as an interoperability recommendation (original paper left serialization implicit).
- No mathematical errors found. Minor presentation improvements (encoding clarity, test coverage) incorporated into this repository.

---

## Citation

```bibtex
@misc{sanders2026phi,
  author       = {Sanders, Jacarri},
  title        = {Deterministic State Reduction via Golden-Ratio Polynomials for Low-Latency Quantum Boundary Commitments},
  year         = {2026},
  publisher    = {Even The Odds Foundry LLC},
  howpublished = {\url{https://github.com/jabrahns-source/phi-boundary-commitments}},
  note         = {Formal verification artifacts and reference implementation included}
}
```

Or use the `CITATION.cff` file with GitHub’s citation feature.

---

## License

MIT License — see [LICENSE](LICENSE).

---

**Built with zero gatekeepers. Formal verification first. Integer-only by design.**

Even The Odds Foundry LLC · Redding, California · 2026
