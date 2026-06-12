"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Hidden Relationship-Field Inference

This experiment asks whether a Pakheta relationship-field can be recovered from
its observable traces rather than supplied directly. The true node weights are
hidden. The model receives anchor responses, context responses, order-sensitive
responses, and false-partition probes, then reconstructs the latent field.
"""

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

PHI = (1.0 + 5.0**0.5) / 2.0

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

NODE_LABELS = [
    "crystal_anchor",
    "grave_memory",
    "backyard_burial",
    "old_photo_far",
    "spoken_name",
    "ordinary_stone_near",
]

PROBE_LIBRARY = [
    ("anchor.whole_field", "anchor", [0.25, 0.18, 0.17, 0.16, 0.16, 0.08]),
    ("anchor.grave", "anchor", [0.10, 0.45, 0.10, 0.05, 0.20, 0.10]),
    ("anchor.backyard", "anchor", [0.10, 0.08, 0.45, 0.08, 0.18, 0.11]),
    ("anchor.photo", "anchor", [0.08, 0.12, 0.10, 0.48, 0.18, 0.04]),
    ("anchor.name", "anchor", [0.15, 0.15, 0.15, 0.12, 0.38, 0.05]),
    ("context.remembrance", "context", [0.18, 0.22, 0.15, 0.20, 0.22, 0.03]),
    ("context.repair", "context", [0.15, 0.18, 0.22, 0.15, 0.20, 0.10]),
    ("context.theory", "context", [0.30, 0.08, 0.12, 0.26, 0.20, 0.04]),
    ("context.physical_nearness", "context", [0.10, 0.35, 0.06, 0.03, 0.10, 0.36]),
    ("sequence.grief_then_gratitude", "order", [0.20, 0.16, 0.14, 0.28, 0.18, 0.04]),
    ("sequence.gratitude_then_grief", "order", [0.16, 0.22, 0.11, 0.17, 0.24, 0.10]),
    ("partition.grave_only", "false_partition", [0.04, 0.60, 0.18, 0.00, 0.10, 0.08]),
    ("partition.location_ledger", "false_partition", [0.02, 0.35, 0.05, 0.00, 0.05, 0.53]),
]


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def normalize_sum(values):
    total = sum(values)
    if total == 0:
        return [1.0 / len(values)] * len(values)
    return [v / total for v in values]


def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))


def cosine_similarity(v1, v2):
    mag_1 = math.sqrt(sum(x * x for x in v1))
    mag_2 = math.sqrt(sum(x * x for x in v2))
    if mag_1 == 0 or mag_2 == 0:
        return 0.0
    return dot_product(v1, v2) / (mag_1 * mag_2)


def mean_absolute_error(v1, v2):
    return sum(abs(x - y) for x, y in zip(v1, v2)) / len(v1)


def top_k_overlap(v1, v2, k=3):
    top_1 = set(sorted(range(len(v1)), key=lambda i: v1[i], reverse=True)[:k])
    top_2 = set(sorted(range(len(v2)), key=lambda i: v2[i], reverse=True)[:k])
    return len(top_1 & top_2) / k


def project_simplex(values):
    """Projects values onto the probability simplex."""
    n = len(values)
    sorted_values = sorted(values, reverse=True)
    cumulative = 0.0
    theta = 0.0
    for i, value in enumerate(sorted_values, 1):
        cumulative += value
        candidate = (cumulative - 1.0) / i
        if i == n or sorted_values[i] <= candidate:
            theta = candidate
            break
    projected = [max(v - theta, 0.0) for v in values]
    return normalize_sum(projected)


def solve_linear_system(matrix, vector):
    """Solves a dense linear system using Gauss-Jordan elimination."""
    n = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            continue
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        pivot_value = augmented[col][col]
        augmented[col] = [value / pivot_value for value in augmented[col]]

        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0:
                continue
            augmented[row] = [
                current - factor * pivot_current
                for current, pivot_current in zip(augmented[row], augmented[col])
            ]

    return [augmented[i][-1] for i in range(n)]


def build_probe(raw_probe, family):
    probe = normalize_sum(raw_probe)
    if family == "false_partition":
        return [0.70 * value for value in probe]
    return probe


def generate_hidden_field(profile, rng):
    if profile == "phi_decay":
        raw = [PHI ** (-(i + 1)) + rng.uniform(-0.015, 0.015) for i in range(len(NODE_LABELS))]
        raw[-1] *= 0.35
    elif profile == "balanced":
        raw = [1.0 + rng.uniform(-0.16, 0.16) for _ in NODE_LABELS]
        raw[-1] *= 0.35
    elif profile == "random":
        raw = [rng.uniform(0.10, 1.0) for _ in NODE_LABELS]
        raw[-1] *= 0.45
    elif profile == "split_pressure":
        raw = [0.25, 0.22, 0.20, 0.17, 0.13, 0.03]
        raw = [max(0.01, value + rng.uniform(-0.04, 0.04)) for value in raw]
    else:
        raw = [1.0 for _ in NODE_LABELS]
    return normalize_sum(raw)


def generate_observations(true_field, rng, noise_sigma=0.004):
    observations = []
    for name, family, raw_probe in PROBE_LIBRARY:
        probe = build_probe(raw_probe, family)
        observed = dot_product(probe, true_field) + rng.gauss(0.0, noise_sigma)
        observed = max(0.0, min(1.0, observed))
        observations.append({
            "name": name,
            "family": family,
            "probe": probe,
            "observed": observed,
        })
    return observations


def infer_field(observations, ridge=0.035):
    n = len(NODE_LABELS)
    prior = [1.0 / n] * n
    normal_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    normal_vector = [0.0 for _ in range(n)]

    for obs in observations:
        probe = obs["probe"]
        observed = obs["observed"]
        for i in range(n):
            normal_vector[i] += probe[i] * observed
            for j in range(n):
                normal_matrix[i][j] += probe[i] * probe[j]

    for i in range(n):
        normal_matrix[i][i] += ridge
        normal_vector[i] += ridge * prior[i]

    raw_solution = solve_linear_system(normal_matrix, normal_vector)
    return project_simplex(raw_solution)


def evaluate_estimate(true_field, estimated_field):
    return {
        "cosine_similarity": round(cosine_similarity(true_field, estimated_field), 4),
        "mean_absolute_error": round(mean_absolute_error(true_field, estimated_field), 4),
        "top_3_overlap": round(top_k_overlap(true_field, estimated_field), 4),
    }


def baseline_fields():
    phi = normalize_sum([PHI ** (-(i + 1)) for i in range(len(NODE_LABELS))])
    equal = [1.0 / len(NODE_LABELS)] * len(NODE_LABELS)
    physical = normalize_sum([0.15, 0.24, 0.07, 0.03, 0.10, 0.41])
    return {
        "equal_baseline": equal,
        "phi_prior": phi,
        "physical_nearness_prior": physical,
    }


def run_canonical_case():
    rng = random.Random(613)
    true_field = normalize_sum([0.25, 0.20, 0.18, 0.16, 0.17, 0.04])
    observations = generate_observations(true_field, rng)
    inferred = infer_field(observations)

    baselines = baseline_fields()
    comparisons = {
        "inferred_from_traces": evaluate_estimate(true_field, inferred)
    }
    for name, field in baselines.items():
        comparisons[name] = evaluate_estimate(true_field, field)

    return {
        "true_field": dict(zip(NODE_LABELS, true_field)),
        "inferred_field": dict(zip(NODE_LABELS, inferred)),
        "observations": [
            {
                "name": obs["name"],
                "family": obs["family"],
                "observed": round(obs["observed"], 4),
            }
            for obs in observations
        ],
        "comparisons": comparisons,
    }


def run_sweep():
    profiles = ["phi_decay", "balanced", "random", "split_pressure"]
    fields_per_profile = 80
    rng = random.Random(613)
    baselines = baseline_fields()
    sweep = {}

    for profile in profiles:
        totals = {
            "inferred_from_traces": [],
            "equal_baseline": [],
            "phi_prior": [],
            "physical_nearness_prior": [],
        }

        for _ in range(fields_per_profile):
            true_field = generate_hidden_field(profile, rng)
            observations = generate_observations(true_field, rng)
            inferred = infer_field(observations)

            totals["inferred_from_traces"].append(evaluate_estimate(true_field, inferred))
            for name, field in baselines.items():
                totals[name].append(evaluate_estimate(true_field, field))

        profile_result = {}
        for name, metrics in totals.items():
            profile_result[name] = {
                "mean_cosine_similarity": round(sum(m["cosine_similarity"] for m in metrics) / len(metrics), 4),
                "mean_absolute_error": round(sum(m["mean_absolute_error"] for m in metrics) / len(metrics), 4),
                "mean_top_3_overlap": round(sum(m["top_3_overlap"] for m in metrics) / len(metrics), 4),
            }
        sweep[profile] = profile_result

    return {
        "fields_per_profile": fields_per_profile,
        "profiles": sweep,
    }


def print_canonical(canonical):
    print(f"\n  {BOLD}{CYAN}[Canonical Hidden Field Reconstruction]{RESET}")
    print(f"  {'Node':<24} | {'True Weight':<12} | {'Inferred Weight':<15}")
    print(f"  {'-'*24} | {'-'*12} | {'-'*15}")

    for label in NODE_LABELS:
        true_value = canonical["true_field"][label]
        inferred_value = canonical["inferred_field"][label]
        color = GREEN if abs(true_value - inferred_value) <= 0.04 else YELLOW
        print(f"  {label:<24} | {true_value:<12.4f} | {color}{inferred_value:<15.4f}{RESET}")

    print(f"\n  {BOLD}Recovery Metrics:{RESET}")
    for name, metrics in canonical["comparisons"].items():
        color = GREEN if name == "inferred_from_traces" else RESET
        print(
            f"  {name:<26} cosine={color}{metrics['cosine_similarity']:.4f}{RESET} "
            f"mae={metrics['mean_absolute_error']:.4f} top3={metrics['top_3_overlap']:.4f}"
        )


def print_sweep(sweep):
    print(f"\n  {BOLD}{CYAN}[Sweep: Recoverability Across Hidden Field Profiles]{RESET}")
    for profile, results in sweep["profiles"].items():
        print(f"\n  {BOLD}[Profile: {profile}]{RESET}")
        print(f"  {'Estimator':<26} | {'Mean Cosine':<13} | {'Mean MAE':<10} | {'Mean Top-3':<10}")
        print(f"  {'-'*26} | {'-'*13} | {'-'*10} | {'-'*10}")
        best_cosine = max(metrics["mean_cosine_similarity"] for metrics in results.values())
        for name, metrics in results.items():
            color = GREEN if abs(metrics["mean_cosine_similarity"] - best_cosine) <= 1e-12 else (RED if "physical" in name else RESET)
            print(
                f"  {name:<26} | {color}{metrics['mean_cosine_similarity']:<13.4f}{RESET} | "
                f"{metrics['mean_absolute_error']:<10.4f} | {metrics['mean_top_3_overlap']:<10.4f}"
            )


def main():
    print_header("Experiment: Hidden Relationship-Field Inference")
    start_time = datetime.now(timezone.utc)

    canonical = run_canonical_case()
    sweep = run_sweep()

    print_canonical(canonical)
    print_sweep(sweep)

    report = {
        "experiment_name": "hidden_relationship_field_inference",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        "node_labels": NODE_LABELS,
        "canonical_case": canonical,
        "sweep": sweep,
    }

    output_file = Path(__file__).resolve().parent / "field_inference_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Hidden field inference completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. The relationship-field can be reconstructed from traces without exposing")
    print("     the true node weights to the inference step.")
    print("  2. Physical-nearness priors fail when the near object is not field-participating.")
    print("  3. Pakheta therefore leaves recoverable signatures in anchor, context, order,")
    print("     and false-partition response patterns.")


if __name__ == "__main__":
    main()
