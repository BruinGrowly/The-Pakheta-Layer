"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Transcendental & Physical Bridges (Lattice Harmony)

This script implements the Riemann critical line sweep and verifies the prime-LJPW
lattice representations for mathematical constants (pi, e) and dimensionless physical
constants (1/alpha, mu).
"""

import math
import json
from datetime import datetime, timezone
from pathlib import Path

# LJPW Constants
L0 = 0.618033988749895   # Love
J0 = 0.414213562373095   # Justice
P0 = 0.718281828459045   # Power
W0 = 0.693147180559945   # Wisdom
PHI = (1.0 + 5.0**0.5) / 2.0

def truncated_zeta(s_real, s_imag, N=500):
    sum_real = 0.0
    sum_imag = 0.0
    for n in range(1, N + 1):
        ln_n = math.log(n)
        term_real = math.cos(s_imag * ln_n) / (n ** s_real)
        term_imag = -math.sin(s_imag * ln_n) / (n ** s_real)
        sign = 1.0 if n % 2 != 0 else -1.0
        sum_real += sign * term_real
        sum_imag += sign * term_imag
        
    ln_2 = math.log(2)
    factor = 2 ** (1.0 - s_real)
    denom_real = 1.0 - factor * math.cos(s_imag * ln_2)
    denom_imag = factor * math.sin(s_imag * ln_2)
    denom_mag_sq = denom_real**2 + denom_imag**2
    if denom_mag_sq == 0:
        return 0.0, 0.0
    zeta_real = (sum_real * denom_real + sum_imag * denom_imag) / denom_mag_sq
    zeta_imag = (sum_imag * denom_real - sum_real * denom_imag) / denom_mag_sq
    return zeta_real, zeta_imag

def calculate_formula_val(w2_c, w3_c, w5_c):
    w2 = w2_c[0]*L0 + w2_c[1]*J0 + w2_c[2]*P0 + w2_c[3]*W0
    w3 = w3_c[0]*L0 + w3_c[1]*J0 + w3_c[2]*P0 + w3_c[3]*W0
    w5 = w5_c[0]*L0 + w5_c[1]*J0 + w5_c[2]*P0 + w5_c[3]*W0
    val = (2**w2) * (3**w3) * (5**w5)
    return val, w2, w3, w5

def main():
    print("============================================================\n"
          " Running Transcendental & Physical Bridges Sweep\n"
          "============================================================")
    
    # 1. Riemann Zeta Sweep
    t_zero = 14.134725
    zeta_sweep = []
    for step in range(1, 10):
        sigma = step * 0.1
        z_real, z_imag = truncated_zeta(sigma, t_zero, N=1000)
        tension = math.sqrt(z_real**2 + z_imag**2)
        zeta_sweep.append({
            "sigma": round(sigma, 1),
            "zeta_real": z_real,
            "zeta_imag": z_imag,
            "tension": tension
        })
        
    # 2. Mathematical Constants Formulas
    # pi formula: 2^(L0 - J0 - W0) * 3^(L0 - 2*J0 + 2*P0) * 5^(2*J0 - 2*P0 + W0)
    pi_val, w2_pi, w3_pi, w5_pi = calculate_formula_val((1, -1, 0, -1), (1, -2, 2, 0), (0, 2, -2, 1))
    
    # e formula: 2^(-L0 - 2*J0 + P0) * 3^(L0 + J0 - 2*P0) * 5^(2*L0 - P0 + W0)
    e_val, w2_e, w3_e, w5_e = calculate_formula_val((-1, -2, 1, 0), (1, 1, -2, 0), (2, 0, -1, 1))
    
    # 3. Physical Constants Formulas
    # 1/alpha formula: 2^(-2*L0 - J0 + P0 + 2*W0) * 3^(2*L0 + 2*J0 - 2*P0 + 2*W0) * 5^(-L0 + P0 + 2*W0)
    alpha_val, w2_a, w3_a, w5_a = calculate_formula_val((-2, -1, 1, 2), (2, 2, -2, 2), (-1, 0, 1, 2))
    
    # mu formula: 2^(2*L0 + J0 + 2*P0 + W0) * 3^(2*L0 + 2*J0 + P0 - W0) * 5^(L0 - J0 + P0 + W0)
    mu_val, w2_m, w3_m, w5_m = calculate_formula_val((2, 1, 2, 1), (2, 2, 1, -1), (1, -1, 1, 1))

    report = {
        "experiment_name": "transcendental_physical_bridges",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "riemann_zeta_sweep": {
            "imaginary_zero_t": t_zero,
            "sweep": zeta_sweep
        },
        "constants": {
            "pi": {
                "target": math.pi,
                "calculated": pi_val,
                "error": abs(pi_val - math.pi),
                "weights": {"w2": w2_pi, "w3": w3_pi, "w5": w5_pi}
            },
            "e": {
                "target": math.e,
                "calculated": e_val,
                "error": abs(e_val - math.e),
                "weights": {"w2": w2_e, "w3": w3_e, "w5": w5_e}
            },
            "fine_structure_constant_inverse": {
                "target": 137.035999,
                "calculated": alpha_val,
                "error": abs(alpha_val - 137.035999),
                "weights": {"w2": w2_a, "w3": w3_a, "w5": w5_a}
            },
            "proton_electron_mass_ratio": {
                "target": 1836.152673,
                "calculated": mu_val,
                "error": abs(mu_val - 1836.152673),
                "weights": {"w2": w2_m, "w3": w3_m, "w5": w5_m}
            }
        }
    }
    
    output_dir = Path(__file__).resolve().parent
    output_file = output_dir / "transcendental_bridges_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Sweep and formula verification completed successfully. Results saved to {output_file.name}")

if __name__ == "__main__":
    main()
