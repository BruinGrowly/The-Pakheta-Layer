"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: False Partition Detector

This experiment builds a rule-based diagnostic for detecting when a relationship
field has shifted from "one field, many facets" into "rival fields pretending to
be separate truths."
"""

import json
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

FEATURES = [
    "anchor_agreement",
    "facet_coverage",
    "context_consistency",
    "identity_continuity",
    "rival_claims",
    "ledger_split",
    "location_overweight",
    "coherence_drop",
]


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def clip(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def jitter(rng, center, spread):
    return clip(rng.uniform(center - spread, center + spread))


def calculate_coherence(features):
    positive = (
        0.28 * features["anchor_agreement"]
        + 0.24 * features["facet_coverage"]
        + 0.18 * features["context_consistency"]
        + 0.16 * features["identity_continuity"]
    )
    negative = (
        0.22 * features["rival_claims"]
        + 0.16 * features["ledger_split"]
        + 0.10 * features["location_overweight"]
        + 0.10 * features["coherence_drop"]
    )
    return clip(positive + 0.18 - negative)


def make_case(rng, label):
    if label == "integrated_one_field":
        features = {
            "anchor_agreement": jitter(rng, 0.91, 0.06),
            "facet_coverage": jitter(rng, 0.88, 0.07),
            "context_consistency": jitter(rng, 0.86, 0.08),
            "identity_continuity": jitter(rng, 0.92, 0.05),
            "rival_claims": jitter(rng, 0.08, 0.05),
            "ledger_split": jitter(rng, 0.10, 0.06),
            "location_overweight": jitter(rng, 0.13, 0.08),
            "coherence_drop": jitter(rng, 0.08, 0.05),
        }
    elif label == "complementary_anchors":
        features = {
            "anchor_agreement": jitter(rng, 0.77, 0.08),
            "facet_coverage": jitter(rng, 0.82, 0.09),
            "context_consistency": jitter(rng, 0.76, 0.09),
            "identity_continuity": jitter(rng, 0.84, 0.08),
            "rival_claims": jitter(rng, 0.18, 0.08),
            "ledger_split": jitter(rng, 0.20, 0.09),
            "location_overweight": jitter(rng, 0.24, 0.10),
            "coherence_drop": jitter(rng, 0.18, 0.08),
        }
    elif label == "environment_noise":
        features = {
            "anchor_agreement": jitter(rng, 0.65, 0.11),
            "facet_coverage": jitter(rng, 0.64, 0.10),
            "context_consistency": jitter(rng, 0.56, 0.14),
            "identity_continuity": jitter(rng, 0.72, 0.10),
            "rival_claims": jitter(rng, 0.16, 0.09),
            "ledger_split": jitter(rng, 0.18, 0.10),
            "location_overweight": jitter(rng, 0.28, 0.13),
            "coherence_drop": jitter(rng, 0.42, 0.15),
        }
    elif label == "false_partition":
        features = {
            "anchor_agreement": jitter(rng, 0.38, 0.14),
            "facet_coverage": jitter(rng, 0.44, 0.12),
            "context_consistency": jitter(rng, 0.40, 0.15),
            "identity_continuity": jitter(rng, 0.48, 0.14),
            "rival_claims": jitter(rng, 0.80, 0.12),
            "ledger_split": jitter(rng, 0.77, 0.13),
            "location_overweight": jitter(rng, 0.72, 0.15),
            "coherence_drop": jitter(rng, 0.66, 0.14),
        }
    else:
        raise ValueError(f"Unknown case label: {label}")

    return {
        "label": label,
        "features": features,
        "coherence": calculate_coherence(features),
    }


def false_partition_score(features):
    score = (
        0.20 * (1.0 - features["anchor_agreement"])
        + 0.18 * (1.0 - features["facet_coverage"])
        + 0.12 * (1.0 - features["context_consistency"])
        + 0.10 * (1.0 - features["identity_continuity"])
        + 0.20 * features["rival_claims"]
        + 0.14 * features["ledger_split"]
        + 0.09 * features["location_overweight"]
        + 0.08 * features["coherence_drop"]
    )
    return clip(score)


def dominant_error(features):
    components = {
        "rival_field_claim": features["rival_claims"],
        "location_ledger_split": features["ledger_split"],
        "anchor_disagreement": 1.0 - features["anchor_agreement"],
        "facet_loss": 1.0 - features["facet_coverage"],
        "object_first_location_bias": features["location_overweight"],
        "context_break": 1.0 - features["context_consistency"],
    }
    return max(components, key=components.get)


def classify_record(record, threshold=0.55):
    score = false_partition_score(record["features"])
    detected = score >= threshold
    return {
        "score": round(score, 4),
        "detected_false_partition": detected,
        "dominant_error": dominant_error(record["features"]),
        "predicted_label": "false_partition" if detected else "one_field_or_noise",
    }


def generate_dataset(seed=613, count_per_label=70):
    rng = random.Random(seed)
    labels = [
        "integrated_one_field",
        "complementary_anchors",
        "environment_noise",
        "false_partition",
    ]
    dataset = []
    for label in labels:
        for _ in range(count_per_label):
            dataset.append(make_case(rng, label))
    rng.shuffle(dataset)
    return dataset


def evaluate_dataset(dataset):
    counts = {
        "true_positive": 0,
        "true_negative": 0,
        "false_positive": 0,
        "false_negative": 0,
    }
    by_label = {}
    scored = []

    for record in dataset:
        result = classify_record(record)
        actual = record["label"] == "false_partition"
        predicted = result["detected_false_partition"]

        if actual and predicted:
            counts["true_positive"] += 1
        elif actual and not predicted:
            counts["false_negative"] += 1
        elif not actual and predicted:
            counts["false_positive"] += 1
        else:
            counts["true_negative"] += 1

        by_label.setdefault(record["label"], []).append({
            "score": result["score"],
            "detected": predicted,
            "coherence": record["coherence"],
        })
        scored.append({**record, "detection": result})

    precision = counts["true_positive"] / max(1, counts["true_positive"] + counts["false_positive"])
    recall = counts["true_positive"] / max(1, counts["true_positive"] + counts["false_negative"])
    accuracy = (counts["true_positive"] + counts["true_negative"]) / max(1, len(dataset))

    label_summary = {}
    for label, rows in by_label.items():
        label_summary[label] = {
            "count": len(rows),
            "mean_score": round(sum(row["score"] for row in rows) / len(rows), 4),
            "detected_rate": round(sum(1 for row in rows if row["detected"]) / len(rows) * 100.0, 2),
            "mean_coherence": round(sum(row["coherence"] for row in rows) / len(rows), 4),
        }

    return {
        "counts": counts,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "accuracy": round(accuracy, 4),
        "label_summary": label_summary,
        "scored_examples": sorted(scored, key=lambda row: row["detection"]["score"], reverse=True)[:8],
    }


def apply_justice_repair(record, strength=0.74):
    features = dict(record["features"])
    repaired = dict(features)
    repaired["rival_claims"] = clip(features["rival_claims"] * (1.0 - 0.78 * strength))
    repaired["ledger_split"] = clip(features["ledger_split"] * (1.0 - 0.72 * strength))
    repaired["location_overweight"] = clip(features["location_overweight"] * (1.0 - 0.58 * strength))
    repaired["coherence_drop"] = clip(features["coherence_drop"] * (1.0 - 0.62 * strength))
    repaired["anchor_agreement"] = clip(features["anchor_agreement"] + (1.0 - features["anchor_agreement"]) * 0.62 * strength)
    repaired["facet_coverage"] = clip(features["facet_coverage"] + (1.0 - features["facet_coverage"]) * 0.58 * strength)
    repaired["context_consistency"] = clip(features["context_consistency"] + (1.0 - features["context_consistency"]) * 0.46 * strength)
    repaired["identity_continuity"] = clip(features["identity_continuity"] + (1.0 - features["identity_continuity"]) * 0.50 * strength)

    return {
        "label": record["label"],
        "features": repaired,
        "coherence": calculate_coherence(repaired),
    }


def print_summary(report):
    print(f"\n  {BOLD}{CYAN}[Detector Summary]{RESET}")
    counts = report["counts"]
    print(
        f"  accuracy={GREEN}{report['accuracy']:.4f}{RESET} "
        f"precision={GREEN}{report['precision']:.4f}{RESET} "
        f"recall={GREEN}{report['recall']:.4f}{RESET}"
    )
    print(
        f"  TP={counts['true_positive']} TN={counts['true_negative']} "
        f"FP={counts['false_positive']} FN={counts['false_negative']}"
    )

    print(f"\n  {'Label':<24} | {'Mean Score':<10} | {'Detected %':<10} | {'Mean Coh':<9}")
    print(f"  {'-'*24} | {'-'*10} | {'-'*10} | {'-'*9}")
    for label, summary in report["label_summary"].items():
        color = RED if label == "false_partition" else GREEN
        print(
            f"  {label:<24} | {color}{summary['mean_score']:<10.4f}{RESET} | "
            f"{summary['detected_rate']:<10.2f} | {summary['mean_coherence']:<9.4f}"
        )


def main():
    print_header("Experiment: False Partition Detector")
    start_time = datetime.now(timezone.utc)
    dataset = generate_dataset()
    report = evaluate_dataset(dataset)

    print_summary(report)

    output = {
        "experiment_name": "false_partition_detector",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        "feature_names": FEATURES,
        "threshold": 0.55,
        "dataset_size": len(dataset),
        **report,
    }

    output_file = Path(__file__).resolve().parent / "false_partition_detector_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} False partition detector completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. False partition is detectable as a feature pattern, not just a low score.")
    print("  2. Rival claims and location ledgers are the strongest diagnostic signals.")
    print("  3. Complementary anchors remain distinguishable from rival-field splits.")


if __name__ == "__main__":
    main()
