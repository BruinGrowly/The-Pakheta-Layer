"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Pakheta Recovery Loop

This experiment combines false-partition detection with a Justice repair step:

detect split -> identify primitive error -> apply Justice repair -> remeasure coherence
"""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pakheta_false_partition_detector import (
    apply_justice_repair,
    calculate_coherence,
    classify_record,
    generate_dataset,
)

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def summarize(values):
    return {
        "min": round(min(values), 4),
        "mean": round(sum(values) / len(values), 4),
        "max": round(max(values), 4),
    }


def no_op_record(record):
    return {
        "label": record["label"],
        "features": dict(record["features"]),
        "coherence": calculate_coherence(record["features"]),
    }


def run_recovery_loop():
    dataset = generate_dataset(seed=811, count_per_label=80)
    rows = []

    for record in dataset:
        before_detection = classify_record(record)
        before_coherence = record["coherence"]

        if before_detection["detected_false_partition"]:
            after = apply_justice_repair(record)
            action = "justice_repair"
        else:
            after = no_op_record(record)
            action = "no_repair"

        after_detection = classify_record(after)
        after_coherence = after["coherence"]

        rows.append({
            "label": record["label"],
            "action": action,
            "dominant_error": before_detection["dominant_error"],
            "before_score": before_detection["score"],
            "after_score": after_detection["score"],
            "before_coherence": round(before_coherence, 4),
            "after_coherence": round(after_coherence, 4),
            "coherence_gain": round(after_coherence - before_coherence, 4),
            "still_detected": after_detection["detected_false_partition"],
            "recovered": (
                record["label"] == "false_partition"
                and before_detection["detected_false_partition"]
                and not after_detection["detected_false_partition"]
                and after_coherence - before_coherence >= 0.25
            ),
        })

    false_rows = [row for row in rows if row["label"] == "false_partition"]
    non_false_rows = [row for row in rows if row["label"] != "false_partition"]
    repaired_rows = [row for row in rows if row["action"] == "justice_repair"]

    primitive_errors = Counter(row["dominant_error"] for row in repaired_rows)
    false_recovered = sum(1 for row in false_rows if row["recovered"])
    unnecessary_repairs = sum(1 for row in non_false_rows if row["action"] == "justice_repair")

    report = {
        "dataset_size": len(rows),
        "repaired_count": len(repaired_rows),
        "false_partition_count": len(false_rows),
        "false_partition_recovery_rate": round(false_recovered / max(1, len(false_rows)) * 100.0, 2),
        "unnecessary_repair_count": unnecessary_repairs,
        "unnecessary_repair_rate": round(unnecessary_repairs / max(1, len(non_false_rows)) * 100.0, 2),
        "false_partition_score": {
            "before": summarize([row["before_score"] for row in false_rows]),
            "after": summarize([row["after_score"] for row in false_rows]),
        },
        "false_partition_coherence": {
            "before": summarize([row["before_coherence"] for row in false_rows]),
            "after": summarize([row["after_coherence"] for row in false_rows]),
            "gain": summarize([row["coherence_gain"] for row in false_rows]),
        },
        "primitive_error_counts": dict(primitive_errors),
        "sample_recoveries": sorted(false_rows, key=lambda row: row["coherence_gain"], reverse=True)[:8],
    }
    return report


def print_summary(report):
    print(f"\n  {BOLD}{CYAN}[Recovery Loop Summary]{RESET}")
    print(f"  repaired_count:              {report['repaired_count']}")
    print(f"  false_partition_count:       {report['false_partition_count']}")
    print(f"  false_partition_recovery:    {GREEN}{report['false_partition_recovery_rate']:.2f}%{RESET}")
    print(f"  unnecessary_repair_rate:     {YELLOW}{report['unnecessary_repair_rate']:.2f}%{RESET}")

    before_score = report["false_partition_score"]["before"]
    after_score = report["false_partition_score"]["after"]
    before_coh = report["false_partition_coherence"]["before"]
    after_coh = report["false_partition_coherence"]["after"]
    gain = report["false_partition_coherence"]["gain"]

    print(
        f"\n  False partition score mean:  {RED}{before_score['mean']:.4f}{RESET} -> "
        f"{GREEN}{after_score['mean']:.4f}{RESET}"
    )
    print(
        f"  False partition coherence:   {RED}{before_coh['mean']:.4f}{RESET} -> "
        f"{GREEN}{after_coh['mean']:.4f}{RESET} "
        f"(gain {gain['mean']:.4f})"
    )

    print(f"\n  {BOLD}Dominant primitive errors repaired:{RESET}")
    for name, count in sorted(report["primitive_error_counts"].items(), key=lambda item: item[1], reverse=True):
        print(f"  - {name}: {count}")


def main():
    print_header("Experiment: Pakheta Recovery Loop")
    start_time = datetime.now(timezone.utc)
    report = run_recovery_loop()

    print_summary(report)

    output = {
        "experiment_name": "pakheta_recovery_loop",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        **report,
    }

    output_file = Path(__file__).resolve().parent / "recovery_loop_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Pakheta recovery loop completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. Detection plus Justice repair converts rival-field assumptions back")
    print("     toward one-field-many-facets structure.")
    print("  2. The loop repairs the score and the coherence, not only the label.")
    print("  3. This turns Pakheta from diagnosis into a measurable repair protocol.")


if __name__ == "__main__":
    main()
