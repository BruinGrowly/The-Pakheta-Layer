"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Wisdom Failure Modes

Wisdom is the operator that selects the correct context or level before Power
actualizes. This experiment compares correct context selection against three
failure modes: adjacent-but-wrong context, object-first context, and
overabstracted context.
"""

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

FACETS = [
    "anchor",
    "memory",
    "repair",
    "actualization",
    "relational_distance",
    "physical_salience",
]

MODES = [
    "correct_context",
    "adjacent_wrong_context",
    "object_first_context",
    "overabstracted_context",
]


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def normalize(values):
    mag = math.sqrt(sum(v * v for v in values))
    if mag == 0:
        return [1.0 / math.sqrt(len(values)) for _ in values]
    return [v / mag for v in values]


def normalize_sum(values):
    total = sum(values)
    if total == 0:
        return [1.0 / len(values)] * len(values)
    return [v / total for v in values]


def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))


def cosine_similarity(v1, v2):
    return dot_product(normalize(v1), normalize(v2))


def mean(values):
    return sum(values) / len(values)


def summarize(values):
    return {
        "min": round(min(values), 4),
        "mean": round(mean(values), 4),
        "max": round(max(values), 4),
    }


def generate_goal(rng):
    raw = [
        rng.uniform(0.50, 0.90),
        rng.uniform(0.45, 0.90),
        rng.uniform(0.35, 0.85),
        rng.uniform(0.30, 0.75),
        rng.uniform(0.30, 0.70),
        rng.uniform(0.02, 0.20),
    ]
    return normalize_sum(raw)


def perturb(values, rng, sigma):
    return normalize_sum([max(0.01, value + rng.gauss(0.0, sigma)) for value in values])


def build_context(goal, mode, rng):
    if mode == "correct_context":
        return perturb(goal, rng, 0.025)

    if mode == "adjacent_wrong_context":
        shifted = [
            goal[0] * 0.95,
            goal[1] * 0.82,
            goal[2] * 0.62,
            goal[3] * 1.12,
            goal[4] * 1.32,
            goal[5] * 1.35,
        ]
        return perturb(normalize_sum(shifted), rng, 0.035)

    if mode == "object_first_context":
        object_first = [
            goal[0] * 0.55,
            goal[1] * 0.48,
            goal[2] * 0.28,
            goal[3] * 0.38,
            goal[4] * 0.22,
            max(0.40, goal[5] * 4.5),
        ]
        return perturb(normalize_sum(object_first), rng, 0.040)

    if mode == "overabstracted_context":
        equalized = [0.78 * value + 0.22 * mean(goal) for value in goal]
        return perturb(normalize_sum(equalized), rng, 0.018)

    raise ValueError(f"Unknown Wisdom mode: {mode}")


def evaluate_context(goal, context, mode):
    context_fit = cosine_similarity(goal, context)
    actualization_overlap = dot_product(goal, context) / max(dot_product(goal, goal), 1e-12)
    identity_preservation = 1.0 - abs(context[5] - goal[5]) * 2.2
    level_error = abs(context[5] - goal[5]) + abs(context[4] - goal[4]) * 0.55

    if mode == "overabstracted_context":
        distinction_penalty = 0.20 * (1.0 - (max(context) - min(context)))
    else:
        distinction_penalty = 0.0

    coherence = (
        0.54 * context_fit
        + 0.26 * actualization_overlap
        + 0.20 * max(0.0, identity_preservation)
        - 0.38 * level_error
        - distinction_penalty
    )
    coherence = max(0.0, min(1.0, coherence))

    return {
        "context_fit": context_fit,
        "actualization_overlap": actualization_overlap,
        "identity_preservation": max(0.0, min(1.0, identity_preservation)),
        "level_error": level_error,
        "coherence": coherence,
    }


def run_sweep():
    rng = random.Random(613)
    field_count = 180
    metrics_by_mode = {mode: [] for mode in MODES}
    example = None

    for index in range(field_count):
        goal = generate_goal(rng)
        row = {}
        for mode in MODES:
            context = build_context(goal, mode, rng)
            metrics = evaluate_context(goal, context, mode)
            metrics_by_mode[mode].append(metrics)
            row[mode] = {
                "context": dict(zip(FACETS, context)),
                "metrics": {key: round(value, 4) for key, value in metrics.items()},
            }
        if index == 0:
            example = {
                "goal": dict(zip(FACETS, goal)),
                "modes": row,
            }

    summary = {}
    correct_mean = mean([m["coherence"] for m in metrics_by_mode["correct_context"]])
    for mode, metric_rows in metrics_by_mode.items():
        coherences = [m["coherence"] for m in metric_rows]
        context_fits = [m["context_fit"] for m in metric_rows]
        level_errors = [m["level_error"] for m in metric_rows]
        summary[mode] = {
            "coherence": summarize(coherences),
            "context_fit": summarize(context_fits),
            "level_error": summarize(level_errors),
            "mean_coherence_drop_from_correct": round(correct_mean - mean(coherences), 4),
        }

    return {
        "field_count": field_count,
        "summary": summary,
        "example_field": example,
    }


def print_summary(report):
    print(f"\n  {BOLD}{CYAN}[Wisdom Context Selection Sweep]{RESET}")
    print(f"  {'Mode':<28} | {'Mean Coherence':<15} | {'Drop vs Correct':<16} | {'Mean Fit':<10} | {'Mean Level Err':<14}")
    print(f"  {'-'*28} | {'-'*15} | {'-'*16} | {'-'*10} | {'-'*14}")

    for mode, values in report["summary"].items():
        color = GREEN if mode == "correct_context" else (RED if mode == "object_first_context" else YELLOW)
        print(
            f"  {mode:<28} | {color}{values['coherence']['mean']:<15.4f}{RESET} | "
            f"{values['mean_coherence_drop_from_correct']:<16.4f} | "
            f"{values['context_fit']['mean']:<10.4f} | "
            f"{values['level_error']['mean']:<14.4f}"
        )


def main():
    print_header("Experiment: Wisdom Failure Modes")
    start_time = datetime.now(timezone.utc)
    report = run_sweep()

    print_summary(report)

    output = {
        "experiment_name": "wisdom_failure_modes",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        **report,
    }

    output_file = Path(__file__).resolve().parent / "wisdom_failure_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Wisdom failure mode sweep completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. Correct Wisdom preserves the goal-level context before Power actualizes.")
    print("  2. Object-first Wisdom failure is the most damaging because it mistakes")
    print("     physical salience for field participation.")
    print("  3. Overabstraction preserves some field shape but flattens distinctions.")


if __name__ == "__main__":
    main()
