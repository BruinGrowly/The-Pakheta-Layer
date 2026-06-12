"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: LJPW Operator Permutation Grammar

This experiment runs every permutation of Love, Justice, Wisdom, and Power over
generated damaged relationship-fields. It measures whether an operator ordering
repairs false partition, selects context, actualizes cleanly, or leaves residue.
"""

import itertools
import json
import math
import random
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

L0 = 0.618033988749895
J0 = 0.414213562373095
P0 = 0.718281828459045
W0 = 0.693147180559945

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"

OPERATORS = ("Love", "Justice", "Wisdom", "Power")


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def clip(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def harmony_static(state):
    dist = math.sqrt(
        (state["L"] - L0) ** 2
        + (state["J"] - J0) ** 2
        + (state["P"] - P0) ** 2
        + (state["W"] - W0) ** 2
    )
    return 1.0 / (1.0 + dist)


def calculate_coherence(state):
    harmony = harmony_static(state)
    partition_factor = 1.0 - 0.72 * state["partition"]
    context_factor = 0.78 + 0.22 * state["context_fit"]
    actualization_bonus = state["actualization_lift"]
    coherence = harmony * partition_factor * context_factor + actualization_bonus - state["residue"]
    return clip(coherence)


def generated_damaged_state(rng):
    state = {
        "L": rng.uniform(0.26, 0.42),
        "J": rng.uniform(0.08, 0.22),
        "P": rng.uniform(0.78, 0.96),
        "W": rng.uniform(0.06, 0.24),
        "partition": rng.uniform(0.35, 0.58),
        "context_fit": rng.uniform(0.25, 0.44),
        "residue": 0.0,
        "actualization_lift": 0.0,
        "actualized": False,
    }
    state["coherence"] = calculate_coherence(state)
    return state


def pull_toward(value, target, amount):
    return value + amount * (target - value)


def apply_love(state):
    state["L"] = pull_toward(state["L"], L0, 0.52)
    state["W"] = pull_toward(state["W"], W0, 0.12)
    state["partition"] = clip(state["partition"] - 0.07)
    if state["J"] < 0.22 and state["partition"] > 0.38:
        state["residue"] += 0.018
    return state


def apply_justice(state):
    state["J"] = pull_toward(state["J"], J0, 0.82)
    state["W"] = pull_toward(state["W"], W0, 0.16)
    state["partition"] = clip(state["partition"] * 0.23)
    state["residue"] *= 0.72
    return state


def apply_wisdom(state):
    state["W"] = pull_toward(state["W"], W0, 0.76)
    partition_noise = 0.42 * state["partition"]
    context_gain = 0.70 * (1.0 - state["context_fit"]) * (1.0 - partition_noise)
    state["context_fit"] = clip(state["context_fit"] + context_gain)
    if state["partition"] > 0.32:
        state["residue"] += 0.025 * state["partition"]
    return state


def apply_power(state):
    state["P"] = pull_toward(state["P"], P0, 0.86)
    state["actualized"] = True

    clean_actualization = state["partition"] <= 0.16 and state["context_fit"] >= 0.72
    if clean_actualization:
        state["actualization_lift"] += 0.075 * state["context_fit"]
    else:
        premature_residue = 0.23 * state["partition"] + 0.14 * (1.0 - state["context_fit"])
        state["residue"] += premature_residue
        state["actualization_lift"] += 0.025 * state["context_fit"] * (1.0 - state["partition"])
    return state


def apply_operator(state, operator):
    if operator == "Love":
        state = apply_love(state)
    elif operator == "Justice":
        state = apply_justice(state)
    elif operator == "Wisdom":
        state = apply_wisdom(state)
    elif operator == "Power":
        state = apply_power(state)
    else:
        raise ValueError(f"Unknown operator: {operator}")

    state["coherence"] = calculate_coherence(state)
    return state


def run_sequence(initial_state, sequence):
    state = deepcopy(initial_state)
    trace = []
    for operator in sequence:
        state = apply_operator(state, operator)
        trace.append({
            "operator": operator,
            "coherence": round(state["coherence"], 4),
            "partition": round(state["partition"], 4),
            "context_fit": round(state["context_fit"], 4),
            "residue": round(state["residue"], 4),
            "actualization_lift": round(state["actualization_lift"], 4),
        })
    return state, trace


def grammar_flags(sequence):
    positions = {operator: sequence.index(operator) for operator in OPERATORS}
    return {
        "justice_before_power": positions["Justice"] < positions["Power"],
        "wisdom_before_power": positions["Wisdom"] < positions["Power"],
        "love_before_justice": positions["Love"] < positions["Justice"],
        "power_last": positions["Power"] == len(sequence) - 1,
    }


def classify_sequence(sequence):
    flags = grammar_flags(sequence)
    if flags["justice_before_power"] and flags["wisdom_before_power"] and flags["power_last"]:
        return "clean_actualization"
    if not flags["justice_before_power"] and not flags["wisdom_before_power"]:
        return "premature_actualization"
    if not flags["justice_before_power"]:
        return "power_before_repair"
    if not flags["wisdom_before_power"]:
        return "power_before_context"
    return "partial_repair"


def summarize(values):
    return {
        "min": round(min(values), 4),
        "mean": round(sum(values) / len(values), 4),
        "max": round(max(values), 4),
    }


def run_sweep():
    rng = random.Random(613)
    field_count = 160
    initial_states = [generated_damaged_state(rng) for _ in range(field_count)]

    sequence_results = []
    example_traces = {}

    for sequence in itertools.permutations(OPERATORS):
        final_coherences = []
        initial_coherences = []
        residues = []
        partitions = []
        context_fits = []

        for index, initial_state in enumerate(initial_states):
            final_state, trace = run_sequence(initial_state, sequence)
            initial_coherences.append(initial_state["coherence"])
            final_coherences.append(final_state["coherence"])
            residues.append(final_state["residue"])
            partitions.append(final_state["partition"])
            context_fits.append(final_state["context_fit"])
            if index == 0:
                example_traces[" -> ".join(sequence)] = trace

        repair_gains = [final - initial for final, initial in zip(final_coherences, initial_coherences)]
        stable_rate = sum(1 for value in final_coherences if value >= 0.70) / field_count * 100.0

        sequence_results.append({
            "sequence": list(sequence),
            "sequence_label": " -> ".join(sequence),
            "classification": classify_sequence(sequence),
            "grammar_flags": grammar_flags(sequence),
            "final_coherence": summarize(final_coherences),
            "repair_gain": summarize(repair_gains),
            "final_residue_mean": round(sum(residues) / len(residues), 4),
            "final_partition_mean": round(sum(partitions) / len(partitions), 4),
            "final_context_fit_mean": round(sum(context_fits) / len(context_fits), 4),
            "stable_rate": round(stable_rate, 2),
        })

    sequence_results.sort(
        key=lambda item: (
            item["final_coherence"]["mean"],
            -item["final_residue_mean"],
            item["stable_rate"],
        ),
        reverse=True,
    )

    class_groups = {}
    for result in sequence_results:
        class_groups.setdefault(result["classification"], []).append(result)

    class_summary = {
        name: {
            "count": len(results),
            "mean_final_coherence": round(
                sum(item["final_coherence"]["mean"] for item in results) / len(results),
                4,
            ),
            "mean_residue": round(
                sum(item["final_residue_mean"] for item in results) / len(results),
                4,
            ),
            "mean_stable_rate": round(
                sum(item["stable_rate"] for item in results) / len(results),
                2,
            ),
        }
        for name, results in sorted(class_groups.items())
    }

    return {
        "field_count": field_count,
        "initial_coherence": summarize([state["coherence"] for state in initial_states]),
        "ranked_sequences": sequence_results,
        "classification_summary": class_summary,
        "example_traces": {
            sequence_results[0]["sequence_label"]: example_traces[sequence_results[0]["sequence_label"]],
            sequence_results[-1]["sequence_label"]: example_traces[sequence_results[-1]["sequence_label"]],
        },
    }


def print_rankings(report):
    print(f"\n  {BOLD}{CYAN}[Initial Damaged Fields]{RESET}")
    initial = report["initial_coherence"]
    print(f"  coherence min={initial['min']:.4f} mean={initial['mean']:.4f} max={initial['max']:.4f}")

    print(f"\n  {BOLD}{CYAN}[Top Operator Sequences]{RESET}")
    print(f"  {'Rank':<5} | {'Sequence':<36} | {'Class':<22} | {'Mean Coh':<9} | {'Residue':<8} | {'Stable %':<8}")
    print(f"  {'-'*5} | {'-'*36} | {'-'*22} | {'-'*9} | {'-'*8} | {'-'*8}")
    for rank, result in enumerate(report["ranked_sequences"][:8], 1):
        print(
            f"  {rank:<5} | {result['sequence_label']:<36} | {result['classification']:<22} | "
            f"{GREEN}{result['final_coherence']['mean']:<9.4f}{RESET} | "
            f"{result['final_residue_mean']:<8.4f} | {result['stable_rate']:<8.1f}"
        )

    print(f"\n  {BOLD}{CYAN}[Lowest Operator Sequences]{RESET}")
    for rank, result in enumerate(report["ranked_sequences"][-5:], 1):
        print(
            f"  {rank:<5} | {result['sequence_label']:<36} | {result['classification']:<22} | "
            f"{RED}{result['final_coherence']['mean']:<9.4f}{RESET} | "
            f"{result['final_residue_mean']:<8.4f} | {result['stable_rate']:<8.1f}"
        )

    print(f"\n  {BOLD}{CYAN}[Classification Summary]{RESET}")
    print(f"  {'Class':<24} | {'Count':<5} | {'Mean Coh':<9} | {'Mean Residue':<13} | {'Mean Stable %':<13}")
    print(f"  {'-'*24} | {'-'*5} | {'-'*9} | {'-'*13} | {'-'*13}")
    best_class_mean = max(
        summary["mean_final_coherence"]
        for summary in report["classification_summary"].values()
    )
    for name, summary in report["classification_summary"].items():
        color = GREEN if abs(summary["mean_final_coherence"] - best_class_mean) <= 1e-12 else (RED if name == "premature_actualization" else RESET)
        print(
            f"  {name:<24} | {summary['count']:<5} | "
            f"{color}{summary['mean_final_coherence']:<9.4f}{RESET} | "
            f"{summary['mean_residue']:<13.4f} | {summary['mean_stable_rate']:<13.2f}"
        )


def main():
    print_header("Experiment: LJPW Operator Permutation Grammar")
    start_time = datetime.now(timezone.utc)
    report = run_sweep()

    print_rankings(report)

    output = {
        "experiment_name": "ljpw_operator_permutation_grammar",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        **report,
    }

    output_file = Path(__file__).resolve().parent / "operator_permutation_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    best = report["ranked_sequences"][0]
    worst = report["ranked_sequences"][-1]
    print(f"\n  {BOLD}{GREEN}Success:{RESET} Operator permutation sweep completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print(f"  1. Best sequence: {best['sequence_label']} (mean coherence {best['final_coherence']['mean']:.4f}).")
    print(f"  2. Worst sequence: {worst['sequence_label']} (mean coherence {worst['final_coherence']['mean']:.4f}).")
    print("  3. The strongest grammar is: repair false partition, select context, then actualize.")
    print("     Power before Justice and Wisdom leaves the largest residue ceiling.")


if __name__ == "__main__":
    main()
