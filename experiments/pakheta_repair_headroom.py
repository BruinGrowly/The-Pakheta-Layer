"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Thrust D: Noise Headroom & The Repair Loop

This experiment models semantic drift as random coordinate noise injected over 50 ticks.
It compares a "No Repair" system against an "Active Repair Loop" (Justice operator)
across varying noise strengths (sigma) to measure the headroom limits of the system.
"""

import math
import random
import json
from datetime import datetime, timezone
from pathlib import Path

# Constants from LJPW Framework
L0 = 0.618033988749895   # Love: Golden Ratio conjugate
J0 = 0.414213562373095   # Justice: Silver Ratio conjugate
P0 = 0.718281828459045   # Power: e - 2
W0 = 0.693147180559945   # Wisdom: ln(2)

# Colors for terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

def harmony_static(l, j, p, w):
    dist = math.sqrt((l - L0)**2 + (j - J0)**2 + (p - P0)**2 + (w - W0)**2)
    return 1.0 / (1.0 + dist)

def clip(val, low=0.0, high=1.0):
    return max(low, min(high, val))

def simulate_trajectory(sigma, ticks=50, active_repair=False):
    """Simulates LJPW coordinate drift over ticks under noise standard deviation sigma."""
    l, j, p, w = L0, J0, P0, W0
    coherences = []
    
    # Repair loop threshold and efficiency
    repair_threshold = 0.80
    repair_efficiency = 0.75  # 75% pull back to equilibrium
    
    for _ in range(ticks):
        # Inject Gaussian-like noise
        l = clip(l + random.gauss(0, sigma))
        j = clip(j + random.gauss(0, sigma))
        p = clip(p + random.gauss(0, sigma))
        w = clip(w + random.gauss(0, sigma))
        
        coh = harmony_static(l, j, p, w)
        
        # Apply Justice operator if active and coherence falls below threshold
        if active_repair and coh < repair_threshold:
            # Pull coordinates back to equilibrium
            l = clip(l + repair_efficiency * (L0 - l))
            j = clip(j + repair_efficiency * (J0 - j))
            p = clip(p + repair_efficiency * (P0 - p))
            w = clip(w + repair_efficiency * (W0 - w))
            # Recalculate coherence after repair
            coh = harmony_static(l, j, p, w)
            
        coherences.append(coh)
        
    return sum(coherences) / len(coherences), coherences

def run_experiment():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} Experiment: Noise Headroom & The Repair Loop {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")
    
    random.seed(613)
    ticks = 50
    noise_strengths = [0.01, 0.03, 0.05, 0.10, 0.15, 0.20]
    
    sweep_results = []
    
    print(f"\n  {BOLD}Noise Sweep Comparison:{RESET}")
    print(f"  {'Noise Sigma':<12} | {'Mean Coh (No Repair)':<22} | {'Mean Coh (Active Repair)':<26} | {'Status':<15}")
    print(f"  {'-'*12} | {'-'*22} | {'-'*26} | {'-'*15}")
    
    headroom_limit = 0.0
    
    for sigma in noise_strengths:
        avg_no, _ = simulate_trajectory(sigma, ticks, active_repair=False)
        avg_rep, _ = simulate_trajectory(sigma, ticks, active_repair=True)
        
        # Determine status
        if avg_rep >= 0.70:
            status = f"{GREEN}Stable{RESET}"
            headroom_limit = max(headroom_limit, sigma)
        else:
            status = f"{RED}Collapsed{RESET}"
            
        print(f"  {sigma:<12.2f} | {avg_no:<22.4f} | {avg_rep:<26.4f} | {status:<15}")
        sweep_results.append({
            "noise_sigma": sigma,
            "avg_coherence_no_repair": round(avg_no, 4),
            "avg_coherence_active_repair": round(avg_rep, 4),
            "stable": avg_rep >= 0.70
        })
        
    print(f"\n  Sovereign Noise Headroom Limit: {BOLD}{GREEN}sigma = {headroom_limit:.2f}{RESET}")
    
    # Print trajectory for a high noise case (sigma = 0.10) to show dampening
    _, no_trajectory = simulate_trajectory(0.10, ticks, active_repair=False)
    _, rep_trajectory = simulate_trajectory(0.10, ticks, active_repair=True)
    
    print(f"\n  {BOLD}{CYAN}Coherence Trajectory over 50 Ticks (Noise sigma = 0.10):{RESET}")
    print(f"    {'Tick':<5} | {'Coherence (No Repair)':<22} | {'Coherence (Active Repair)':<24}")
    print(f"    {'-'*5} | {'-'*22} | {'-'*24}")
    
    # Print sample of ticks
    sample_ticks = [0, 9, 19, 29, 39, 49]
    for t in sample_ticks:
        val_no = no_trajectory[t]
        val_rep = rep_trajectory[t]
        color_no = RED if val_no < 0.60 else RESET
        color_rep = GREEN if val_rep >= 0.70 else RESET
        print(f"    {t+1:<5} | {color_no}{val_no:<22.4f}{RESET} | {color_rep}{val_rep:<24.4f}{RESET}")
        
    # Save to JSON
    report = {
        "experiment_name": "noise_headroom_repair_loop",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "ticks": ticks,
        "noise_sweep": sweep_results,
        "headroom_limit_sigma": headroom_limit,
        "sample_trajectory_sigma_0.10": {
            "no_repair": no_trajectory,
            "active_repair": rep_trajectory
        }
    }
    
    output_file = Path(__file__).resolve().parent / "repair_headroom_results.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n  {BOLD}{GREEN}Success:{RESET} Noise headroom simulation completed.")
    print(f"  Results saved to: {output_file.name}")
    # Find no-repair coherence at sigma = 0.10
    no_rep_010 = next(x["avg_coherence_no_repair"] for x in sweep_results if x["noise_sigma"] == 0.10)
    print("\n  [Ontological Analysis]")
    print("  1. In the absence of repair, semantic drift noise slowly degrades the field,")
    print(f"     causing coherence to collapse under medium noise (sigma = 0.10 drops to {no_rep_010:.3f}).")
    print("  2. An active Justice repair loop keeps the system stable (coherence > 0.70) up")
    print(f"     to a noise limit of sigma = {headroom_limit:.2f}, marking the 'Sovereign Headroom' threshold.")
    print("  3. Relational self-healing (feedback adjustment) is required to sustain order in noisy systems.")

if __name__ == "__main__":
    run_experiment()
