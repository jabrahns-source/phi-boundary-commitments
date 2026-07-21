# ============================================================
# EXACT GOLDEN-RATIO FPU BYPASS FROM THE PAPER
# Deterministic State Reduction via Golden-Ratio Polynomials
# Jacarri Sanders - Even The Odds Foundry / Kerna-Ledger
# ============================================================

import numpy as np
import time
import matplotlib.pyplot as plt

print("Loading exact algorithm from paper...")

# ----------------------------------------------------------
# Fibonacci helper (exact integer)
# ----------------------------------------------------------
def fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Precompute Fibonacci up to safe u64 limit (n=93 from Table 1)
MAX_N = 93
F = [fib(i) for i in range(MAX_N + 5)]

# ----------------------------------------------------------
# REAL ALGORITHM (Theorem 1)
# ----------------------------------------------------------
def compute_AB(k):
    """Compute the invariant coefficients A and B exactly as in the paper"""
    m = len(k)
    A = 0
    B = 0
    for i in range(m):
        A += k[i] * F[i + 1]
        B += k[i] * F[i]
    return A, B

def state_update_ALU(A, B, n):
    """u64 ALU path: 2 multiplies + 1 add (exactly as Table 2)"""
    return A * F[n + 1] + B * F[n]

# ----------------------------------------------------------
# BASELINE: Naive full sum
# ----------------------------------------------------------
def naive_full_sum(k, n):
    """Expensive path that recomputes every Fibonacci term every time"""
    S = 0
    for i in range(len(k)):
        S += k[i] * F[n + i + 1]
    return S

# ----------------------------------------------------------
# BENCHMARK
# ----------------------------------------------------------
m = 16                    # block length (paper verifies 4,8,16,32)
k = np.random.randint(0, 50, size=m).tolist()   # pre-quantized sensor vector

print(f"Block length m = {m}")
print(f"Sample k vector: {k}")

# Precompute A, B once
A, B = compute_AB(k)
print(f"A = {A}")
print(f"B = {B}")

num_updates = 5000
n_start = 10

# --- ALU path ---
start = time.time()
for i in range(num_updates):
    n = n_start + (i % 40)
    S_alu = state_update_ALU(A, B, n)
alu_time = time.time() - start

# --- Naive full path ---
start = time.time()
for i in range(num_updates):
    n = n_start + (i % 40)
    S_naive = naive_full_sum(k, n)
naive_time = time.time() - start

# Verify correctness
n_test = 20
S1 = state_update_ALU(A, B, n_test)
S2 = naive_full_sum(k, n_test)
correct = (S1 == S2)

print("\n=== RESULTS (from paper algorithm) ===")
print(f"ALU path time ({num_updates} updates): {alu_time:.6f} s")
print(f"Naive full path time:                  {naive_time:.6f} s")
print(f"Speedup: {naive_time / alu_time:.2f}x")
print(f"Time savings: {(1 - alu_time/naive_time)*100:.1f}%")
print(f"Correctness check (exact integer equality): {correct}")
print(f"Sample S at n={n_test}: {S1}")

print("\nInstruction footprint (Table 2):")
print("IEEE-754 f64 FPU : 2×pow() + 2×FMUL + FADD   → Float rounding drift")
print("Your u64 ALU     : 2×IMUL + ADD + 2×table load → Bit-exact")

# Chart
plt.figure(figsize=(8,5))
plt.bar(['Naive Full Path', 'Your ALU Bypass'], [naive_time, alu_time])
plt.ylabel('Time for 5000 state updates (seconds)')
plt.title('Golden-Ratio Fibonacci State Reduction\n(Paper Algorithm)')
plt.show()
