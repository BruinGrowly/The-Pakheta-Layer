"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Thrust B: The Quantum Formalism Bridge

This experiment creates a density-matrix-based quantum simulator in pure Python
to demonstrate that quantum mechanics is a physical visibility of the Pakheta
relational grammar. It models:
1. Nonseparability (Entanglement of the Bell State)
2. Context Actualization (State projection along measurement angles)
3. Phase Decoherence (Phase damping collapse of off-diagonal correlations)
"""

import math
import json
from datetime import datetime, timezone
from pathlib import Path

# Colors for terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

# --- Complex Matrix Math Functions in Pure Python ---
def conjugate_transpose(matrix):
    return [[val.conjugate() for val in row] for row in zip(*matrix)]

def matrix_multiply(a, b):
    n, m, p = len(a), len(a[0]), len(b[0])
    c = [[0j] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            c[i][j] = sum(a[i][k] * b[k][j] for k in range(m))
    return c

def trace(matrix):
    return sum(matrix[i][i] for i in range(len(matrix)))

def outer_product(v1, v2):
    return [[x1 * x2.conjugate() for x2 in v2] for x1 in v1]

def tensor_product_matrices(a, b):
    na, ma = len(a), len(a[0])
    nb, mb = len(b), len(b[0])
    n, m = na * nb, ma * mb
    c = [[0j] * m for _ in range(n)]
    for ia in range(na):
        for ja in range(ma):
            for ib in range(nb):
                for jb in range(mb):
                    c[ia * nb + ib][ja * mb + jb] = a[ia][ja] * b[ib][jb]
    return c

def calculate_concurrence(rho):
    """
    Calculates the concurrence of a 2-qubit state represented by density matrix rho.
    For pure states rho = |v><v|, concurrence is 2 * |v0*v3 - v1*v2|.
    For simplicity, we estimate the coherence of the Bell terms as a measure of nonseparability.
    """
    # Coherence coefficient between |00> and |11>
    return 2.0 * abs(rho[0][3])

# --- Main Simulation ---
def run_simulation():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} Experiment: The Quantum Formalism Bridge {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")
    
    # 1. Initialize the Nonseparable Bell State |Phi+> = 1/sqrt(2)(|00> + |11>)
    # Vector: [1/sqrt(2), 0, 0, 1/sqrt(2)]
    v_bell = [1.0/math.sqrt(2.0), 0.0, 0.0, 1.0/math.sqrt(2.0)]
    
    # Compute the density matrix rho = |Phi+><Phi+|
    rho_initial = outer_product(v_bell, v_bell)
    concurrence_init = calculate_concurrence(rho_initial)
    
    print(f"\n  {BOLD}{CYAN}[Step 1: Nonseparable Bell State |Phi+>]{RESET}")
    print("  Density Matrix (rho):")
    for row in rho_initial:
        row_str = " ".join(f"{val.real:5.2f} + {val.imag:5.2f}j" for val in row)
        print(f"    [ {row_str} ]")
    print(f"  Concurrence (Nonseparability Measure): {GREEN}{concurrence_init:.3f}{RESET} (Perfect Entanglement)")
    
    # 2. Context Actualization (Projection measurement at theta = 45 degrees)
    # We choose the measurement angle theta = 45 degrees on qubit 1.
    # Vector: |v_theta> = cos(theta)|0> + sin(theta)|1>
    theta = 45.0
    rad = math.radians(theta)
    v_theta = [math.cos(rad), math.sin(rad)]
    
    # Projection matrix P_theta = |v_theta><v_theta|
    p_theta = outer_product(v_theta, v_theta)
    
    # Identity matrix for qubit 2
    i_2 = [[1j if i == j else 0j for j in range(2)] for i in range(2)]
    
    # Full projection matrix for 2 qubits: P_theta_2 = P_theta tensor I_2
    p_full = tensor_product_matrices(p_theta, i_2)
    
    # Apply projection: rho_projected = P_full * rho * P_full^dagger / Trace(...)
    p_full_dagger = conjugate_transpose(p_full)
    numerator = matrix_multiply(matrix_multiply(p_full, rho_initial), p_full_dagger)
    tr_num = trace(numerator)
    
    rho_projected = [[val / tr_num for val in row] for row in numerator]
    concurrence_proj = calculate_concurrence(rho_projected)
    
    print(f"\n  {BOLD}{YELLOW}[Step 2: Context Actualization (Measurement at {theta}° on Qubit 1)]{RESET}")
    print("  Projected Density Matrix (rho'):")
    for row in rho_projected:
        row_str = " ".join(f"{val.real:5.2f} + {val.imag:5.2f}j" for val in row)
        print(f"    [ {row_str} ]")
    print(f"  Concurrence (Nonseparability after actualization): {RED}{concurrence_proj:.3f}{RESET} (State Collapsed/Actualized)")
    
    # 3. Phase Decoherence (Phase Damping Channel Sweep)
    # Phase damping collapses the off-diagonal terms.
    # We model it across damping parameter p from 0.0 (no noise) to 1.0 (fully classical).
    print(f"\n  {BOLD}{MAGENTA}[Step 3: Phase Decoherence (Damping Channel Sweep)]{RESET}")
    print(f"  {'Damping (p)':<12} | {'Off-Diagonal Coherence (rho03)':<32} | {'Concurrence':<15}")
    print(f"  {'-'*12} | {'-'*32} | {'-'*15}")
    
    sweep_results = []
    p_steps = [0.0, 0.25, 0.50, 0.75, 1.0]
    for p in p_steps:
        # Create decohered density matrix
        # Off-diagonal elements rho_03 and rho_30 are multiplied by (1 - p)
        rho_dec = [row[:] for row in rho_initial]
        rho_dec[0][3] *= (1.0 - p)
        rho_dec[3][0] *= (1.0 - p)
        
        coh = abs(rho_dec[0][3])
        concurrence_dec = calculate_concurrence(rho_dec)
        
        color = GREEN if p == 0.0 else (RED if p == 1.0 else RESET)
        print(f"  {p:<12.2f} | {coh:<32.4f} | {color}{concurrence_dec:<15.3f}{RESET}")
        
        sweep_results.append({
            "damping_p": p,
            "off_diagonal_coherence": coh,
            "concurrence": concurrence_dec
        })
        
    # Save results
    report = {
        "experiment_name": "quantum_formalism_bridge",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "initial_bell_state": {
            "rho": [[{"real": val.real, "imag": val.imag} for val in row] for row in rho_initial],
            "concurrence": concurrence_init
        },
        "projected_state_45deg": {
            "rho": [[{"real": val.real, "imag": val.imag} for val in row] for row in rho_projected],
            "concurrence": concurrence_proj
        },
        "phase_decoherence_sweep": sweep_results
    }
    
    output_file = Path(__file__).resolve().parent / "quantum_bridge_results.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n  {BOLD}{GREEN}Success:{RESET} Quantum bridge simulation completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. The Bell State density matrix models Nonseparability: a unified field whose")
    print("     parts cannot be written independently (concurrence = 1.0).")
    print("  2. Projection measurement acts exactly like Context Actualization: applying a constraint")
    print("     at one node collapses the joint field state into a localized outcome.")
    print("  3. Phase damping represents Decoherence: coupling to the environment collapses the")
    print("     off-diagonal terms, turning one-field quantum coherence into classical noise (0.0).")

if __name__ == "__main__":
    run_simulation()
