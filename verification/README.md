# Z3 Formal Verification — φ-Boundary Commitments

| Script | Property |
|--------|----------|
| `verify_linear_collapse.py` | Linear basis decomposition identity over BitVec64 for m ∈ {4,8,16,32} |
| `verify_boundedness.py` | A and B remain inside u64 when k_i are non-negative 32-bit values and m ≤ 32 |

## Quick run

```bash
pip install z3-solver
python verification/verify_linear_collapse.py
python verification/verify_boundedness.py
```

Both scripts exit 0 on success and print clear [PASS] lines.

These certificates are re-runnable in CI and support the claims in the paper and README.

Even The Odds Foundry LLC · 2026
