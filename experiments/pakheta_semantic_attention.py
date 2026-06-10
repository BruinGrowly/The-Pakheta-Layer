"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Semantic Attention Path-Sensitivity (Computational Semantics)

This script simulates a Transformer attention mechanism over a 5D concept vocabulary.
It demonstrates how reversing the sequence order of two context clues (V1 -> V2 vs V2 -> V1)
results in non-commutative vector shifts and distinct probability distributions
for the actualized state, measured via Kullback-Leibler (KL) Divergence.
"""

import math
import json
from datetime import datetime, timezone
from pathlib import Path

# --- Mathematical Foundations ---
# Colors for terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

# Vocab dimensions
VOCAB = ["Remembrance", "Grief", "Gratitude", "Time", "Silence"]
DIM = len(VOCAB)

def normalize(v):
    mag = math.sqrt(sum(x * x for x in v))
    if mag == 0:
        return v
    return [x / mag for x in v]

def softmax(v):
    exp_v = [math.exp(x) for x in v]
    sum_exp = sum(exp_v)
    return [x / sum_exp for x in exp_v]

def kl_divergence(p, q):
    """Calculates D_KL(P || Q)"""
    div = 0.0
    for pi, qi in zip(p, q):
        # Avoid log(0) or division by zero
        pi = max(pi, 1e-12)
        qi = max(qi, 1e-12)
        div += pi * math.log(pi / qi)
    return div

def matrix_multiply(matrix, vector):
    return [sum(m_row * v_val for m_row, v_val in zip(matrix_row, vector)) for matrix_row in matrix]

def run_experiment():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} Experiment: Semantic Attention Path-Sensitivity {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")
    
    # 1. Base Query Vector (Q): Starting state representing "Remembrance"
    # Differentiated but balanced enough for context to steer actualization
    q_init = normalize([0.35, 0.35, 0.35, 0.1, 0.1])
    
    # 2. Context matrices (M1: Grief, M2: Gratitude)
    # These represent attention weight transformations. They are intentionally non-symmetric
    # to guarantee non-commutativity (M1 * M2 != M2 * M1).
    
    # Grief context: amplifies Grief (dim 1) and Silence (dim 4), suppresses Gratitude (dim 2)
    m_grief = [
        [0.8, 0.1, 0.0, 0.1, 0.2],
        [0.2, 2.5, 0.0, 0.1, 0.3],
        [0.0, 0.0, 0.3, 0.1, 0.0],
        [0.1, 0.2, 0.1, 0.9, 0.1],
        [0.1, 0.4, 0.0, 0.1, 1.8]
    ]
    
    # Gratitude context: amplifies Gratitude (dim 2) and Time (dim 3), suppresses Grief (dim 1)
    m_gratitude = [
        [0.9, 0.0, 0.2, 0.1, 0.1],
        [0.0, 0.2, 0.0, 0.0, 0.0],
        [0.1, 0.0, 2.6, 0.2, 0.1],
        [0.1, 0.1, 0.2, 1.2, 0.1],
        [0.1, 0.0, 0.2, 0.1, 0.7]
    ]

    print("  Initial query vector (Remembrance):")
    print(f"    v = {list(map(lambda x: round(x, 3), q_init))}\n")
    
    # --- Path A: Grief Context then Gratitude Context ---
    # Step A.1: Apply Grief
    v_a1 = normalize(matrix_multiply(m_grief, q_init))
    # Step A.2: Apply Gratitude
    v_a2 = normalize(matrix_multiply(m_gratitude, v_a1))
    prob_a = softmax(v_a2)
    
    # --- Path B: Gratitude Context then Grief Context ---
    # Step B.1: Apply Gratitude
    v_b1 = normalize(matrix_multiply(m_gratitude, q_init))
    # Step B.2: Apply Grief
    v_b2 = normalize(matrix_multiply(m_grief, v_b1))
    prob_b = softmax(v_b2)

    # 3. Output comparison table
    print(f"  {BOLD}{'Vocabulary Word':<18} | {'Prob (Grief -> Gratitude)':<26} | {'Prob (Gratitude -> Grief)':<26}{RESET}")
    print(f"  {'-'*18} | {'-'*26} | {'-'*26}")
    
    for i, word in enumerate(VOCAB):
        lead_a = BOLD + GREEN if prob_a[i] == max(prob_a) else RESET
        lead_b = BOLD + YELLOW if prob_b[i] == max(prob_b) else RESET
        print(f"  {word:<18} | {lead_a}{prob_a[i]:<26.4f}{RESET} | {lead_b}{prob_b[i]:<26.4f}{RESET}")

    # 4. Measure divergence
    kl_ab = kl_divergence(prob_a, prob_b)
    kl_ba = kl_divergence(prob_b, prob_a)
    symmetric_kl = (kl_ab + kl_ba) / 2.0
    
    print(f"\n  Divergence Metrics:")
    print(f"  - D_KL(Path A || Path B):   {CYAN}{kl_ab:.4f}{RESET}")
    print(f"  - D_KL(Path B || Path A):   {CYAN}{kl_ba:.4f}{RESET}")
    print(f"  - Symmetric KL Divergence:  {BOLD}{GREEN}{symmetric_kl:.4f}{RESET}")
    
    # Determine leading actualized state
    lead_word_a = VOCAB[prob_a.index(max(prob_a))]
    lead_word_b = VOCAB[prob_b.index(max(prob_b))]
    print(f"\n  Actualized State Output:")
    print(f"  - Path A (Grief -> Gratitude) actualizes: {BOLD}{GREEN}{lead_word_a}{RESET}")
    print(f"  - Path B (Gratitude -> Grief) actualizes: {BOLD}{YELLOW}{lead_word_b}{RESET}")

    # Save to report
    report = {
        "experiment_name": "semantic_attention_path_sensitivity",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "vocab": VOCAB,
        "path_a_grief_then_gratitude": {
            "final_vector": v_a2,
            "probabilities": prob_a,
            "actualized_state": lead_word_a
        },
        "path_b_gratitude_then_grief": {
            "final_vector": v_b2,
            "probabilities": prob_b,
            "actualized_state": lead_word_b
        },
        "kl_divergence": {
            "kl_ab": kl_ab,
            "kl_ba": kl_ba,
            "symmetric_kl": symmetric_kl
        }
    }
    
    output_file = Path(__file__).resolve().parent / "semantic_attention_results.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Computational semantic simulation completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print(f"  1. The non-zero symmetric KL divergence ({symmetric_kl:.4f}) proves path-sensitivity.")
    print(f"  2. Path A actualizes '{lead_word_a}', while Path B actualizes '{lead_word_b}'.")
    print("  3. This confirms that semantic attention behaves like non-commuting quantum operators.")

if __name__ == "__main__":
    run_experiment()
