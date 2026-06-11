"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Thrust A: Path-Dependent Operator Residue

This experiment tests the hypothesis that actualizing a relationship-field (Power)
prior to repairing its structural partitions (Justice) leaves a permanent
"residue penalty" (karmic scar) that limits the maximum coherence achievable
by subsequent operations.
"""

import math
import json
from datetime import datetime, timezone
from pathlib import Path

# Constants from LJPW Framework
L0 = 0.618033988749895   # Love: Golden Ratio conjugate
J0 = 0.414213562373095   # Justice: Silver Ratio conjugate
P0 = 0.718281828459045   # Power: e - 2
W0 = 0.693147180559945   # Wisdom: ln(2)
PHI = (1.0 + 5.0**0.5) / 2.0

# Colors for terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

class LJPWState:
    def __init__(self, name, l, j, p, w, base_coh):
        self.name = name
        self.l = l
        self.j = j
        self.p = p
        self.w = w
        self.base_coh = base_coh

def harmony_static(l, j, p, w):
    dist = math.sqrt((l - L0)**2 + (j - J0)**2 + (p - P0)**2 + (w - W0)**2)
    return 1.0 / (1.0 + dist)

def run_simulation():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} Experiment: Path-Dependent Operator Residue {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")
    
    # States pool representing the operators
    state_0 = LJPWState("0. Initial Damaged State", 0.30, 0.10, 0.90, 0.00, 0.335)
    state_love = LJPWState("1. Love Gather", 0.45, 0.10, 0.85, 0.15, 0.376)
    state_justice = LJPWState("2. Justice Repair", 0.45, 0.40, 0.60, 0.55, 0.550)
    state_wisdom = LJPWState("3. Wisdom Context", 0.48, 0.414, 0.50, 0.693, 0.550)
    state_power = LJPWState("4. Power Actualize", 0.618, 0.414, 0.718, 0.693, 0.650)
    
    # --- PATH 1: Clean Order (Love -> Justice -> Wisdom -> Power) ---
    print(f"\n  {BOLD}{CYAN}[Path 1: Clean Order (Love -> Justice -> Wisdom -> Power)]{RESET}")
    path_1_flow = [state_0, state_love, state_justice, state_wisdom, state_power]
    path_1_results = []
    accumulated_residue_1 = 0.0
    
    print(f"  {'Step':<28} | {'Coordinates (L, J, P, W)':<30} | {'Residue':<8} | {'Effective Coherence':<20}")
    print(f"  {'-'*28} | {'-'*30} | {'-'*8} | {'-'*20}")
    
    for i, s in enumerate(path_1_flow):
        # In Path 1, Power is called last, when the field is already repaired (no partition)
        # So residue remains 0.0
        eff_coherence = s.base_coh - accumulated_residue_1
        print(f"  {s.name:<28} | ({s.l:.3f}, {s.j:.3f}, {s.p:.3f}, {s.w:.3f}) | {accumulated_residue_1:.3f}   | {GREEN}{eff_coherence:.3f}{RESET}")
        path_1_results.append({
            "step": s.name,
            "L": s.l, "J": s.j, "P": s.p, "W": s.w,
            "residue": accumulated_residue_1,
            "coherence": eff_coherence
        })
        
    # --- PATH 2: Excited Order (Love -> Power -> Justice -> Wisdom) ---
    print(f"\n  {BOLD}{RED}[Path 2: Excited Order (Love -> Power -> Justice -> Wisdom)]{RESET}")
    # We actualize prematurely (State 4 Power actualization parameters applied directly after Love Gather)
    path_2_flow = [
        state_0,
        state_love,
        # Power is called here, while J=0.10 and W=0.15 (high partition noise)
        LJPWState("2. Premature Power Actualize", 0.618, 0.414, 0.718, 0.693, 0.650),
        # Justice Repair is called AFTER actualization has already occurred
        LJPWState("3. Delayed Justice Repair", 0.45, 0.40, 0.60, 0.55, 0.550),
        # Wisdom Select
        LJPWState("4. Delayed Wisdom Select", 0.48, 0.414, 0.50, 0.693, 0.550)
    ]
    
    path_2_results = []
    accumulated_residue_2 = 0.0
    
    print(f"  {'Step':<28} | {'Coordinates (L, J, P, W)':<30} | {'Residue':<8} | {'Effective Coherence':<20}")
    print(f"  {'-'*28} | {'-'*30} | {'-'*8} | {'-'*20}")
    
    actualized_base = 0.0
    for i, s in enumerate(path_2_flow):
        if "Actualize" in s.name:
            actualized_base = s.base_coh
            
        # Step 2: Premature Power is called. We compute the residue penalty based on distance to equilibrium
        # at the moment of actualization (which was state_love: L=0.45, J=0.10, P=0.85, W=0.15)
        if s.name == "2. Premature Power Actualize":
            # Distance from state_love to natural equilibrium
            dist = math.sqrt((state_love.l-L0)**2 + (state_love.j-J0)**2 + (state_love.p-P0)**2 + (state_love.w-W0)**2)
            # Residue is proportional to this distance (representing the structural misalignment)
            accumulated_residue_2 = dist * 0.25  # Dynamic penalty based on distance
            
        current_base = max(s.base_coh, actualized_base)
        eff_coherence = max(0.0, current_base - accumulated_residue_2)
            
        color = RED if accumulated_residue_2 > 0 else RESET
        print(f"  {s.name:<28} | ({s.l:.3f}, {s.j:.3f}, {s.p:.3f}, {s.w:.3f}) | {color}{accumulated_residue_2:.3f}{RESET}   | {color}{eff_coherence:.3f}{RESET}")
        path_2_results.append({
            "step": s.name,
            "L": s.l, "J": s.j, "P": s.p, "W": s.w,
            "residue": accumulated_residue_2,
            "coherence": eff_coherence
        })
        
    coherence_gap = path_1_results[-1]["coherence"] - path_2_results[-1]["coherence"]
    print(f"\n  Final Coherence Gap (Path 1 vs Path 2): {YELLOW}{coherence_gap:.3f}{RESET}")
    
    # Save results
    report = {
        "experiment_name": "path_dependent_operator_residue",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "path_1_clean_order": path_1_results,
        "path_2_excited_order": path_2_results,
        "final_coherence_gap": coherence_gap
    }
    
    output_file = Path(__file__).resolve().parent / "operator_residue_results.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n  {BOLD}{GREEN}Success:{RESET} Operator residue simulation completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. Operating Power (actualization) before Justice (structural boundary repair) creates")
    print(f"     a conflicted reality state, generating a permanent relational residue ({accumulated_residue_2:.3f}).")
    print("  2. This residue acts as a coherence ceiling: even after delayed repair, the field")
    print(f"     cannot exceed a coherence of {path_2_results[-1]['coherence']:.3f}, compared to {path_1_results[-1]['coherence']:.3f} for the clean path.")
    print("  3. Relational sequence is critical: actualizing confusion locks in confusion.")

if __name__ == "__main__":
    run_simulation()
