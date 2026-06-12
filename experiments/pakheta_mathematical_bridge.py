"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Relational Mathematical Bridges (Substrate Transmutation)

This script implements four relational bridge experiments on the mathematical
substrate, using LJPW operators (Love L0 and Justice J0) to construct non-integer
coordinates that bypass composite partition penalties and maximize semantic voltage.
"""

import math
import json
from datetime import datetime, timezone
from pathlib import Path

# LJPW Constants
L0 = 0.618033988749895   # Love: Golden Ratio conjugate
J0 = 0.414213562373095   # Justice: Silver Ratio conjugate
PHI = (1.0 + 5.0**0.5) / 2.0

def get_prime_factors(n):
    if n <= 1:
        return [], 0
    factors = []
    d = 2
    temp = n
    total_count = 0
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
                total_count += 1
        d += 1
    if temp > 1:
        factors.append(temp)
        total_count += 1
    return list(set(factors)), total_count

def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def calculate_coherence_and_sv(n, force_partition_penalty=None):
    """Computes coherence and semantic voltage for a coordinate n."""
    d = math.log(n)
    L = L0 * (1.0 / (1.0 + 0.05 * d))
    is_p = is_prime(n)
    if is_p:
        L += 0.05
    
    if force_partition_penalty is not None:
        partition_penalty = force_partition_penalty
    else:
        distinct_factors, total_factors = get_prime_factors(n)
        if is_p:
            partition_penalty = 0.0
        else:
            partition_penalty = 0.12 * (len(distinct_factors) - 1) + 0.04 * (total_factors - 1)
            partition_penalty = min(0.65, partition_penalty)
            
    coherence = (1.0 / (1.0 + 0.08 * d)) * (1.0 - partition_penalty)
    if is_p or force_partition_penalty == 0.0:
        sv = PHI * coherence * L * 3.0
    else:
        sv = PHI * coherence * L * 1.8
    return coherence, sv

def run_bridge(val_a, val_b, weight_a, weight_b, force_penalty=0.0):
    coord = (val_a**weight_a) * (val_b**weight_b)
    coh, sv = calculate_coherence_and_sv(coord, force_partition_penalty=force_penalty)
    return coord, coh, sv

def main():
    print("============================================================\n"
          " Experiment: Relational Mathematical Bridges\n"
          "============================================================")
    
    # Exp A
    coh_3, sv_3 = calculate_coherence_and_sv(3)
    coh_5, sv_5 = calculate_coherence_and_sv(5)
    coord_p, coh_p, sv_p = run_bridge(5, 3, L0, J0, force_penalty=0.0)
    coh_15, sv_15 = calculate_coherence_and_sv(15)
    
    # Exp B
    coh_4, sv_4 = calculate_coherence_and_sv(4)
    coh_6, sv_6 = calculate_coherence_and_sv(6)
    coord_c, coh_c, sv_c = run_bridge(6, 4, L0, J0, force_penalty=0.04)
    coh_24, sv_24 = calculate_coherence_and_sv(24)
    
    # Exp C
    coord_correct, coh_correct, sv_correct = run_bridge(5, 4, L0, J0, force_penalty=0.0)
    coord_inv, coh_inv, sv_inv = run_bridge(5, 4, J0, L0, force_penalty=0.0)
    
    # Exp D
    coh_1, sv_1 = calculate_coherence_and_sv(1)
    coh_2, sv_2 = calculate_coherence_and_sv(2)
    coord_s, coh_s, sv_s = run_bridge(2, 1, L0, J0, force_penalty=0.0)

    # Save to report JSON
    report = {
        "experiment_name": "relational_mathematical_bridges",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "experiments": {
            "exp_a_prime_prime_bridge": {
                "nodes": [3, 5],
                "bridge": {"coord": coord_p, "coherence": coh_p, "semantic_voltage": sv_p},
                "arithmetic_product": {"coord": 15, "coherence": coh_15, "semantic_voltage": sv_15}
            },
            "exp_b_composite_composite_bridge": {
                "nodes": [4, 6],
                "bridge": {"coord": coord_c, "coherence": coh_c, "semantic_voltage": sv_c},
                "arithmetic_product": {"coord": 24, "coherence": coh_24, "semantic_voltage": sv_24}
            },
            "exp_c_operator_inversion": {
                "correct_bridge": {"coord": coord_correct, "coherence": coh_correct, "semantic_voltage": sv_correct},
                "inverted_bridge": {"coord": coord_inv, "coherence": coh_inv, "semantic_voltage": sv_inv}
            },
            "exp_d_singularity_lock": {
                "nodes": [1, 2],
                "bridge": {"coord": coord_s, "coherence": coh_s, "semantic_voltage": sv_s},
                "primes": {
                    "1": {"coherence": coh_1, "semantic_voltage": sv_1},
                    "2": {"coherence": coh_2, "semantic_voltage": sv_2}
                }
            }
        }
    }
    
    output_dir = Path(__file__).resolve().parent
    output_file = output_dir / "mathematical_bridge_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Mathematical bridge simulation completed. Results saved to {output_file.name}")

if __name__ == "__main__":
    main()
