"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Relational Locality Phase Diagram

This experiment maps regimes where spatial distance and relational distance are
aligned, independent, inverted, or unstable under context.
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

PHASES = [
    "aligned",
    "independent",
    "inverted",
    "unstable_under_context",
]

CONTEXTS = [
    "physical_context",
    "memory_context",
    "repair_context",
]


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def clip(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def pearson_correlation(x_values, y_values):
    n = len(x_values)
    if n == 0:
        return 0.0
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    dx = [value - mean_x for value in x_values]
    dy = [value - mean_y for value in y_values]
    numerator = sum(a * b for a, b in zip(dx, dy))
    den_x = sum(a * a for a in dx)
    den_y = sum(b * b for b in dy)
    if den_x == 0 or den_y == 0:
        return 0.0
    return numerator / math.sqrt(den_x * den_y)


def generate_pair_distances(phase, context, rng, pair_count=24):
    spatial = [rng.uniform(0.02, 1.0) for _ in range(pair_count)]

    if phase == "aligned":
        relational = [clip(s + rng.gauss(0.0, 0.08)) for s in spatial]
    elif phase == "independent":
        relational = [rng.uniform(0.02, 1.0) for _ in spatial]
    elif phase == "inverted":
        relational = [clip(1.0 - s + rng.gauss(0.0, 0.08)) for s in spatial]
    elif phase == "unstable_under_context":
        if context == "physical_context":
            relational = [clip(s + rng.gauss(0.0, 0.09)) for s in spatial]
        elif context == "memory_context":
            relational = [clip(1.0 - s + rng.gauss(0.0, 0.09)) for s in spatial]
        else:
            relational = [clip(0.55 * rng.uniform(0.02, 1.0) + 0.45 * s + rng.gauss(0.0, 0.07)) for s in spatial]
    else:
        raise ValueError(f"Unknown phase: {phase}")

    return spatial, relational


def classify_phase(correlations):
    values = list(correlations.values())
    span = max(values) - min(values)
    mean_corr = sum(values) / len(values)

    if span >= 0.90:
        return "unstable_under_context"
    if mean_corr >= 0.45:
        return "aligned"
    if mean_corr <= -0.45:
        return "inverted"
    return "independent"


def run_phase_diagram():
    rng = random.Random(613)
    fields_per_phase = 90
    phase_rows = {phase: [] for phase in PHASES}

    for phase in PHASES:
        for _ in range(fields_per_phase):
            correlations = {}
            for context in CONTEXTS:
                spatial, relational = generate_pair_distances(phase, context, rng)
                correlations[context] = pearson_correlation(spatial, relational)
            phase_rows[phase].append({
                "correlations": correlations,
                "predicted_phase": classify_phase(correlations),
            })

    phase_summary = {}
    for phase, rows in phase_rows.items():
        context_means = {
            context: round(sum(row["correlations"][context] for row in rows) / len(rows), 4)
            for context in CONTEXTS
        }
        spans = [
            max(row["correlations"].values()) - min(row["correlations"].values())
            for row in rows
        ]
        correct = sum(1 for row in rows if row["predicted_phase"] == phase)
        phase_summary[phase] = {
            "count": len(rows),
            "context_mean_correlations": context_means,
            "mean_context_span": round(sum(spans) / len(spans), 4),
            "classification_rate": round(correct / len(rows) * 100.0, 2),
        }

    return {
        "fields_per_phase": fields_per_phase,
        "contexts": CONTEXTS,
        "phase_summary": phase_summary,
        "example_rows": {
            phase: {
                "correlations": {
                    context: round(value, 4)
                    for context, value in phase_rows[phase][0]["correlations"].items()
                },
                "predicted_phase": phase_rows[phase][0]["predicted_phase"],
            }
            for phase in PHASES
        },
    }


def print_summary(report):
    print(f"\n  {BOLD}{CYAN}[Relational Locality Phase Diagram]{RESET}")
    print(f"  {'Phase':<24} | {'Physical':<9} | {'Memory':<9} | {'Repair':<9} | {'Span':<8} | {'Class %':<8}")
    print(f"  {'-'*24} | {'-'*9} | {'-'*9} | {'-'*9} | {'-'*8} | {'-'*8}")
    for phase, summary in report["phase_summary"].items():
        means = summary["context_mean_correlations"]
        color = GREEN if summary["classification_rate"] >= 95.0 else YELLOW
        print(
            f"  {phase:<24} | {means['physical_context']:<9.4f} | "
            f"{means['memory_context']:<9.4f} | {means['repair_context']:<9.4f} | "
            f"{summary['mean_context_span']:<8.4f} | "
            f"{color}{summary['classification_rate']:<8.2f}{RESET}"
        )


def main():
    print_header("Experiment: Relational Locality Phase Diagram")
    start_time = datetime.now(timezone.utc)
    report = run_phase_diagram()

    print_summary(report)

    output = {
        "experiment_name": "relational_locality_phase_diagram",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        **report,
    }

    output_file = Path(__file__).resolve().parent / "locality_phase_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Locality phase diagram completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. Relational locality is not one regime. It has phase behavior.")
    print("  2. Spatial and relational distance can align, decouple, invert, or")
    print("     change sign depending on context.")
    print("  3. Context-instability is visible as a wide correlation span.")


if __name__ == "__main__":
    main()
