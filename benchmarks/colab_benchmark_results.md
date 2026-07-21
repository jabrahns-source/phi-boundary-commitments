# Golden-Ratio FPU Bypass Benchmark Results

**Date:** 2026-07-21  
**Author:** Jacarri Sanders (Even The Odds Foundry / Kerna-Ledger)  
**Repo:** phi-boundary-commitments  
**Paper:** Deterministic State Reduction via Golden-Ratio Polynomials for Low-Latency Quantum Boundary Commitments

## Summary of Measured Results

| Metric | Value |
|--------|-------|
| Block length (m) | 16 |
| Sample k vector | [19, 8, 46, 42, 33, 24, 0, 17, 49, 18, 10, 36, 49, 31, 49, 42] |
| A coefficient | 104137 |
| B coefficient | 64345 |
| ALU path time (5000 updates) | 0.006099 s |
| Naive full path time | 0.023759 s |
| **Speedup** | **3.90x** |
| **Time savings** | **74.3%** |
| Correctness (exact integer equality) | True |
| Sample S at n=20 | 1575177527 |

## Instruction Footprint (from paper Table 2)

- IEEE-754 f64 FPU: 2×pow() + 2×FMUL + FADD → Float rounding drift
- Our u64 ALU: 2×IMUL + ADD + 2×table load → Bit-exact

These results confirm the core claims of the paper:
- The linear basis collapse (Theorem 1) produces exact integer results.
- Per-update cost reduces to two integer multiplies + one addition.
- Significant latency and energy reduction versus the naive full-sum path.

## Files in this directory
- `colab_benchmark.py` — exact runnable test script used to produce these numbers
