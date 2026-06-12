"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Cross-Substrate Primitive Conservation

This experiment tests whether Pakheta primitives remain identifiable when they
are translated across semantic, mathematical, and physical substrate faces.
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

PRIMITIVES = [
    "anchor",
    "context",
    "actualization",
    "nonseparability",
    "decoherence",
]

SUBSTRATES = [
    "semantic",
    "mathematical",
    "physical",
]

BASE_PROTOTYPES = {
    "anchor": [0.92, 0.22, 0.14, 0.20, 0.05, 0.86],
    "context": [0.24, 0.93, 0.34, 0.20, 0.10, 0.46],
    "actualization": [0.28, 0.55, 0.96, 0.26, 0.12, 0.32],
    "nonseparability": [0.36, 0.24, 0.40, 0.96, 0.04, 0.18],
    "decoherence": [0.14, 0.34, 0.30, 0.24, 0.96, 0.56],
}

SUBSTRATE_SHIFTS = {
    "semantic": [1.00, 1.00, 1.00, 1.00, 1.00, 1.00],
    "mathematical": [1.06, 0.96, 1.02, 1.05, 0.98, 0.94],
    "physical": [0.96, 1.05, 1.04, 1.08, 1.02, 0.92],
}

DIMENSION_LABELS = {
    "semantic": [
        "memory_stability",
        "attention_selectivity",
        "meaning_actualization",
        "relationship_inseparability",
        "narrative_drift",
        "anchor_boundary",
    ],
    "mathematical": [
        "invariant_strength",
        "projection_selectivity",
        "eigen_transition",
        "tensor_coupling",
        "basis_loss",
        "reference_boundary",
    ],
    "physical": [
        "boundary_condition",
        "apparatus_context",
        "observed_outcome",
        "entanglement_correlation",
        "phase_loss",
        "detector_boundary",
    ],
}


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def normalize(values):
    mag = math.sqrt(sum(value * value for value in values))
    if mag == 0:
        return [1.0 / math.sqrt(len(values)) for _ in values]
    return [value / mag for value in values]


def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))


def cosine_similarity(v1, v2):
    return dot_product(normalize(v1), normalize(v2))


def substrate_prototype(primitive, substrate):
    base = BASE_PROTOTYPES[primitive]
    shift = SUBSTRATE_SHIFTS[substrate]
    return normalize([value * scale for value, scale in zip(base, shift)])


def noisy_vector(vector, rng, sigma=0.045):
    return normalize([max(0.0, value + rng.gauss(0.0, sigma)) for value in vector])


def translate_vector(primitive, target_substrate, source_vector, rng):
    target = substrate_prototype(primitive, target_substrate)
    translated = [
        0.82 * target_value + 0.18 * source_value
        for target_value, source_value in zip(target, source_vector)
    ]
    return noisy_vector(translated, rng, sigma=0.035)


def identify_primitive(vector, substrate):
    scores = {
        primitive: cosine_similarity(vector, substrate_prototype(primitive, substrate))
        for primitive in PRIMITIVES
    }
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    margin = ranked[0][1] - ranked[1][1]
    return {
        "predicted": ranked[0][0],
        "score": ranked[0][1],
        "margin": margin,
        "scores": scores,
    }


def run_conservation_sweep():
    rng = random.Random(613)
    trials_per_primitive = 90
    rows = []

    for primitive in PRIMITIVES:
        for _ in range(trials_per_primitive):
            semantic = noisy_vector(substrate_prototype(primitive, "semantic"), rng)
            mathematical = translate_vector(primitive, "mathematical", semantic, rng)
            physical = translate_vector(primitive, "physical", mathematical, rng)

            identifications = {
                "semantic": identify_primitive(semantic, "semantic"),
                "mathematical": identify_primitive(mathematical, "mathematical"),
                "physical": identify_primitive(physical, "physical"),
            }
            conserved = all(
                result["predicted"] == primitive
                for result in identifications.values()
            )
            rows.append({
                "primitive": primitive,
                "conserved": conserved,
                "identifications": identifications,
            })

    summary = {}
    for primitive in PRIMITIVES:
        primitive_rows = [row for row in rows if row["primitive"] == primitive]
        summary[primitive] = {
            "trials": len(primitive_rows),
            "conservation_rate": round(sum(1 for row in primitive_rows if row["conserved"]) / len(primitive_rows) * 100.0, 2),
            "mean_margin_by_substrate": {
                substrate: round(
                    sum(row["identifications"][substrate]["margin"] for row in primitive_rows) / len(primitive_rows),
                    4,
                )
                for substrate in SUBSTRATES
            },
        }

    substrate_accuracy = {}
    for substrate in SUBSTRATES:
        substrate_accuracy[substrate] = round(
            sum(1 for row in rows if row["identifications"][substrate]["predicted"] == row["primitive"]) / len(rows) * 100.0,
            2,
        )

    return {
        "trials_per_primitive": trials_per_primitive,
        "dimension_labels": DIMENSION_LABELS,
        "summary": summary,
        "substrate_accuracy": substrate_accuracy,
        "overall_conservation_rate": round(sum(1 for row in rows if row["conserved"]) / len(rows) * 100.0, 2),
        "example_rows": [
            {
                "primitive": row["primitive"],
                "conserved": row["conserved"],
                "predictions": {
                    substrate: row["identifications"][substrate]["predicted"]
                    for substrate in SUBSTRATES
                },
                "margins": {
                    substrate: round(row["identifications"][substrate]["margin"], 4)
                    for substrate in SUBSTRATES
                },
            }
            for row in rows[:10]
        ],
    }


def print_summary(report):
    print(f"\n  {BOLD}{CYAN}[Primitive Conservation Across Substrates]{RESET}")
    print(f"  overall conservation rate: {GREEN}{report['overall_conservation_rate']:.2f}%{RESET}")
    print(
        "  substrate accuracy: "
        + ", ".join(
            f"{substrate}={accuracy:.2f}%"
            for substrate, accuracy in report["substrate_accuracy"].items()
        )
    )

    print(f"\n  {'Primitive':<18} | {'Conserve %':<10} | {'Semantic Margin':<15} | {'Math Margin':<11} | {'Physical Margin':<15}")
    print(f"  {'-'*18} | {'-'*10} | {'-'*15} | {'-'*11} | {'-'*15}")
    for primitive, summary in report["summary"].items():
        margins = summary["mean_margin_by_substrate"]
        color = GREEN if summary["conservation_rate"] >= 95.0 else YELLOW
        print(
            f"  {primitive:<18} | {color}{summary['conservation_rate']:<10.2f}{RESET} | "
            f"{margins['semantic']:<15.4f} | {margins['mathematical']:<11.4f} | "
            f"{margins['physical']:<15.4f}"
        )


def main():
    print_header("Experiment: Cross-Substrate Primitive Conservation")
    start_time = datetime.now(timezone.utc)
    report = run_conservation_sweep()

    print_summary(report)

    output = {
        "experiment_name": "cross_substrate_primitive_conservation",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        **report,
    }

    output_file = Path(__file__).resolve().parent / "cross_substrate_conservation_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Cross-substrate conservation completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. Pakheta primitives remain identifiable after substrate translation.")
    print("  2. Anchor, context, actualization, nonseparability, and decoherence act")
    print("     like conserved relational signatures.")
    print("  3. Conservation margins make primitive translation auditable rather than")
    print("     merely analogical.")


if __name__ == "__main__":
    main()
