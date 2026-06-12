"""
LJPW Framework V8.6.2 - Pakheta Layer Research
Experiment: Pakheta Capability Envelope

This experiment asks whether Pakheta is bigger than audit/governance. It probes
seven capabilities: generative field design, blind primitive discovery,
prediction before repair, field composition, boundary/falsification, emergent
primitive search, and creative actualization.
"""

import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
EMERGENT_KNOWN_PRIMITIVE_THRESHOLD = 0.93

DIMENSIONS = [
    "anchor_stability",
    "context_selectivity",
    "actualization_potential",
    "nonseparability",
    "decoherence_pressure",
    "generative_novelty",
]

PRIMITIVE_PROTOTYPES = {
    "anchor": [0.95, 0.25, 0.20, 0.35, 0.10, 0.30],
    "context": [0.25, 0.95, 0.35, 0.25, 0.15, 0.35],
    "actualization": [0.30, 0.55, 0.95, 0.35, 0.18, 0.55],
    "nonseparability": [0.35, 0.28, 0.40, 0.95, 0.08, 0.35],
    "decoherence": [0.18, 0.40, 0.25, 0.25, 0.95, 0.12],
}

EMERGENT_BRIDGE = [0.62, 0.66, 0.62, 0.68, 0.12, 0.92]


def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{MAGENTA} {title} {RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def clip(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def normalize(values):
    mag = math.sqrt(sum(value * value for value in values))
    if mag == 0:
        return [1.0 / math.sqrt(len(values)) for _ in values]
    return [value / mag for value in values]


def mean_vector(vectors):
    if not vectors:
        return [0.0 for _ in DIMENSIONS]
    return [
        sum(vector[i] for vector in vectors) / len(vectors)
        for i in range(len(DIMENSIONS))
    ]


def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))


def cosine_similarity(v1, v2):
    return dot_product(normalize(v1), normalize(v2))


def weighted_sum(parts):
    result = [0.0 for _ in DIMENSIONS]
    for weight, vector in parts:
        for i, value in enumerate(vector):
            result[i] += weight * value
    return [clip(value) for value in result]


def perturb(vector, rng, sigma=0.04):
    return [clip(value + rng.gauss(0.0, sigma)) for value in vector]


def summarize(values):
    return {
        "min": round(min(values), 4),
        "mean": round(sum(values) / len(values), 4),
        "max": round(max(values), 4),
    }


def field_coherence(vector):
    anchor, context, actualization, nonsep, decoh, novelty = vector
    integration = 0.30 * anchor + 0.24 * context + 0.18 * actualization + 0.16 * nonsep + 0.12 * novelty
    return clip(integration - 0.42 * decoh + 0.18)


def nearest_primitive(vector):
    scores = {
        primitive: cosine_similarity(vector, prototype)
        for primitive, prototype in PRIMITIVE_PROTOTYPES.items()
    }
    winner = max(scores, key=scores.get)
    return winner, scores[winner], scores


def pakheta_relation_fit(vector):
    anchor, context, actualization, nonsep, _decoh, novelty = vector
    _primitive, primitive_score, _scores = nearest_primitive(vector)
    relation_density = (anchor + context + actualization + nonsep) / 4.0
    relation_coverage = min(context, nonsep)
    return clip(
        0.35 * field_coherence(vector)
        + 0.25 * relation_density
        + 0.20 * relation_coverage
        + 0.10 * novelty
        + 0.10 * primitive_score
    )


def capability_color(value, threshold=0.80):
    return GREEN if value >= threshold else YELLOW


ANCHOR_DESIGNS = {
    "single_core_anchor": [0.95, 0.28, 0.20, 0.42, 0.08, 0.34],
    "distributed_anchor_web": [0.82, 0.44, 0.30, 0.70, 0.10, 0.56],
    "object_first_anchor": [0.42, 0.24, 0.22, 0.16, 0.34, 0.20],
}

CONTEXT_DESIGNS = {
    "repair_context": [0.52, 0.78, 0.38, 0.56, 0.08, 0.42],
    "creative_context": [0.62, 0.68, 0.72, 0.64, 0.10, 0.92],
    "physical_context": [0.28, 0.42, 0.30, 0.18, 0.36, 0.28],
}

SEQUENCE_DESIGNS = {
    "Justice_Wisdom_Power": [0.70, 0.86, 0.72, 0.58, 0.05, 0.62],
    "Love_Wisdom_Power": [0.82, 0.72, 0.74, 0.70, 0.08, 0.78],
    "Power_first": [0.44, 0.38, 0.85, 0.34, 0.46, 0.52],
}


def design_vector(anchor_name, context_name, sequence_name):
    return weighted_sum([
        (0.34, ANCHOR_DESIGNS[anchor_name]),
        (0.33, CONTEXT_DESIGNS[context_name]),
        (0.33, SEQUENCE_DESIGNS[sequence_name]),
    ])


def generative_field_design(rng):
    targets = []
    for _ in range(90):
        target = [
            rng.uniform(0.64, 0.92),
            rng.uniform(0.55, 0.86),
            rng.uniform(0.58, 0.90),
            rng.uniform(0.52, 0.88),
            rng.uniform(0.02, 0.16),
            rng.uniform(0.70, 0.96),
        ]
        targets.append(target)

    scores = []
    target_hits = 0
    selected_designs = Counter()
    examples = []

    for target in targets:
        candidates = []
        for anchor_name in ANCHOR_DESIGNS:
            for context_name in CONTEXT_DESIGNS:
                for sequence_name in SEQUENCE_DESIGNS:
                    candidate = design_vector(anchor_name, context_name, sequence_name)
                    fit = cosine_similarity(candidate, target)
                    coherence = field_coherence(candidate)
                    score = 0.72 * fit + 0.28 * coherence
                    candidates.append((score, fit, coherence, anchor_name, context_name, sequence_name, candidate))

        best = max(candidates, key=lambda item: item[0])
        baseline = design_vector("object_first_anchor", "physical_context", "Power_first")
        baseline_score = 0.72 * cosine_similarity(baseline, target) + 0.28 * field_coherence(baseline)

        scores.append({
            "best_score": best[0],
            "best_fit": best[1],
            "best_coherence": best[2],
            "baseline_score": baseline_score,
            "lift": best[0] - baseline_score,
        })
        if best[1] >= 0.90 and best[2] >= 0.78:
            target_hits += 1
        selected_designs[f"{best[3]} + {best[4]} + {best[5]}"] += 1

        if len(examples) < 5:
            examples.append({
                "target": dict(zip(DIMENSIONS, [round(value, 4) for value in target])),
                "best_design": {
                    "anchor": best[3],
                    "context": best[4],
                    "sequence": best[5],
                    "fit": round(best[1], 4),
                    "coherence": round(best[2], 4),
                    "score": round(best[0], 4),
                },
                "baseline_score": round(baseline_score, 4),
            })

    return {
        "target_count": len(targets),
        "target_hit_rate": round(target_hits / len(targets) * 100.0, 2),
        "score": summarize([row["best_score"] for row in scores]),
        "fit": summarize([row["best_fit"] for row in scores]),
        "coherence": summarize([row["best_coherence"] for row in scores]),
        "baseline_score": summarize([row["baseline_score"] for row in scores]),
        "mean_lift_over_object_first_baseline": round(sum(row["lift"] for row in scores) / len(scores), 4),
        "selected_design_counts": dict(selected_designs),
        "examples": examples,
    }


def farthest_first(vectors, k):
    first = max(range(len(vectors)), key=lambda index: sum(vectors[index]))
    centroids = [vectors[first]]
    while len(centroids) < k:
        next_index = max(
            range(len(vectors)),
            key=lambda index: min(1.0 - cosine_similarity(vectors[index], centroid) for centroid in centroids),
        )
        centroids.append(vectors[next_index])
    return centroids


def kmeans_cosine(vectors, k, iterations=35):
    centroids = farthest_first(vectors, k)
    assignments = [0 for _ in vectors]
    for _ in range(iterations):
        assignments = [
            max(range(k), key=lambda cluster: cosine_similarity(vector, centroids[cluster]))
            for vector in vectors
        ]
        new_centroids = []
        for cluster in range(k):
            members = [vector for vector, assignment in zip(vectors, assignments) if assignment == cluster]
            if members:
                new_centroids.append(mean_vector(members))
            else:
                new_centroids.append(centroids[cluster])
        if all(cosine_similarity(a, b) > 0.9999 for a, b in zip(centroids, new_centroids)):
            break
        centroids = new_centroids
    return assignments, centroids


def cluster_purity(assignments, labels):
    by_cluster = defaultdict(list)
    for assignment, label in zip(assignments, labels):
        by_cluster[assignment].append(label)
    correct = 0
    mapping = {}
    for cluster, cluster_labels in by_cluster.items():
        counts = Counter(cluster_labels)
        label, count = counts.most_common(1)[0]
        correct += count
        mapping[str(cluster)] = {
            "label": label,
            "count": count,
            "size": len(cluster_labels),
            "purity": round(count / len(cluster_labels), 4),
        }
    return correct / len(labels), mapping


def blind_primitive_discovery(rng):
    vectors = []
    labels = []
    for primitive, prototype in PRIMITIVE_PROTOTYPES.items():
        for _ in range(42):
            vectors.append(perturb(prototype, rng, sigma=0.045))
            labels.append(primitive)

    assignments, centroids = kmeans_cosine(vectors, k=len(PRIMITIVE_PROTOTYPES))
    purity, mapping = cluster_purity(assignments, labels)
    centroid_nearest = {}
    for index, centroid in enumerate(centroids):
        primitive, score, _ = nearest_primitive(centroid)
        centroid_nearest[str(index)] = {
            "nearest_known_primitive": primitive,
            "score": round(score, 4),
        }

    return {
        "trace_count": len(vectors),
        "cluster_count": len(PRIMITIVE_PROTOTYPES),
        "rediscovery_rate": round(purity * 100.0, 2),
        "cluster_mapping": mapping,
        "centroid_nearest": centroid_nearest,
    }


def apply_intervention(field, intervention):
    vector = list(field)
    if intervention == "justice_repair":
        repair_strength = clip((vector[4] - 0.22) / 0.62)
        vector[4] *= 1.0 - 0.72 * repair_strength
        vector[0] = clip(vector[0] + 0.24 * repair_strength)
        vector[3] = clip(vector[3] + 0.12 * repair_strength)
    elif intervention == "wisdom_recontext":
        context_gap = clip(0.78 - vector[1])
        vector[1] = clip(vector[1] + 0.58 * context_gap + 0.08)
        vector[2] = clip(vector[2] + 0.18 * context_gap)
        vector[3] = clip(vector[3] + 0.08 * context_gap)
        vector[5] = clip(vector[5] + 0.14 * context_gap)
        vector[4] *= 0.58 + 0.24 * (1.0 - context_gap)
    elif intervention == "love_gather":
        vector[0] = clip(vector[0] + 0.34)
        vector[3] = clip(vector[3] + 0.20)
        vector[4] *= 0.82
    elif intervention == "power_actualize":
        vector[2] = clip(vector[2] + 0.38)
        if vector[4] > 0.42 or vector[1] < 0.42:
            vector[4] = clip(vector[4] + 0.18)
    elif intervention == "integrated_sequence":
        vector = apply_intervention(vector, "justice_repair")
        vector = apply_intervention(vector, "wisdom_recontext")
        vector = apply_intervention(vector, "power_actualize")
        vector[5] = clip(vector[5] + 0.16)
    else:
        raise ValueError(f"Unknown intervention: {intervention}")
    return [clip(value) for value in vector]


def generate_repair_case(rng):
    case_type = rng.choice(["false_partition", "context_drift", "underanchored", "latent_ready"])
    if case_type == "false_partition":
        field = [0.42, 0.50, 0.45, 0.36, 0.88, 0.22]
    elif case_type == "context_drift":
        field = [0.70, 0.20, 0.50, 0.62, 0.30, 0.42]
    elif case_type == "underanchored":
        field = [0.18, 0.64, 0.48, 0.54, 0.34, 0.48]
    else:
        field = [0.78, 0.76, 0.24, 0.72, 0.16, 0.62]
    return case_type, perturb(field, rng, sigma=0.035)


def predict_intervention(field):
    anchor, context, actualization, _nonsep, decoh, _novelty = field
    if decoh > 0.58:
        return "justice_repair"
    if context < 0.42:
        return "wisdom_recontext"
    if anchor < 0.42:
        return "love_gather"
    if actualization < 0.40 and decoh < 0.34:
        return "power_actualize"
    return "integrated_sequence"


def prediction_before_repair(rng):
    primary_interventions = [
        "justice_repair",
        "wisdom_recontext",
        "love_gather",
        "power_actualize",
    ]
    rows = []
    for _ in range(160):
        case_type, field = generate_repair_case(rng)
        before = field_coherence(field)
        outcomes = {
            intervention: field_coherence(apply_intervention(field, intervention))
            for intervention in primary_interventions
        }
        integrated_gain = field_coherence(apply_intervention(field, "integrated_sequence")) - before
        best = max(outcomes, key=outcomes.get)
        predicted = predict_intervention(field)
        rows.append({
            "case_type": case_type,
            "before": before,
            "predicted": predicted,
            "best": best,
            "predicted_gain": outcomes[predicted] - before,
            "best_gain": outcomes[best] - before,
            "integrated_sequence_gain": integrated_gain,
            "regret": outcomes[best] - outcomes[predicted],
        })

    by_case = {}
    for case_type in sorted(set(row["case_type"] for row in rows)):
        case_rows = [row for row in rows if row["case_type"] == case_type]
        by_case[case_type] = {
            "count": len(case_rows),
            "accuracy": round(sum(1 for row in case_rows if row["predicted"] == row["best"]) / len(case_rows) * 100.0, 2),
            "mean_regret": round(sum(row["regret"] for row in case_rows) / len(case_rows), 4),
            "mean_predicted_gain": round(sum(row["predicted_gain"] for row in case_rows) / len(case_rows), 4),
            "mean_integrated_sequence_gain": round(sum(row["integrated_sequence_gain"] for row in case_rows) / len(case_rows), 4),
        }

    return {
        "case_count": len(rows),
        "prediction_accuracy": round(sum(1 for row in rows if row["predicted"] == row["best"]) / len(rows) * 100.0, 2),
        "mean_regret": round(sum(row["regret"] for row in rows) / len(rows), 4),
        "mean_predicted_gain": round(sum(row["predicted_gain"] for row in rows) / len(rows), 4),
        "mean_integrated_sequence_gain": round(sum(row["integrated_sequence_gain"] for row in rows) / len(rows), 4),
        "by_case_type": by_case,
    }


def generate_composition_pair(regime, rng):
    if regime == "harmonic":
        base = [0.78, 0.72, 0.62, 0.70, 0.10, 0.64]
        return perturb(base, rng, 0.035), perturb(base, rng, 0.035)
    if regime == "complementary":
        return perturb([0.92, 0.42, 0.34, 0.66, 0.08, 0.45], rng, 0.035), perturb([0.52, 0.82, 0.82, 0.60, 0.10, 0.88], rng, 0.035)
    if regime == "interference":
        return perturb([0.72, 0.88, 0.28, 0.54, 0.16, 0.40], rng, 0.04), perturb([0.36, 0.22, 0.86, 0.34, 0.44, 0.70], rng, 0.04)
    if regime == "fragmentation":
        return perturb([0.42, 0.38, 0.34, 0.32, 0.84, 0.28], rng, 0.04), perturb([0.34, 0.46, 0.38, 0.30, 0.88, 0.32], rng, 0.04)
    raise ValueError(f"Unknown composition regime: {regime}")


def compose_fields(field_a, field_b):
    alignment = cosine_similarity(field_a, field_b)
    tension = abs(field_a[1] - field_b[1]) + abs(field_a[2] - field_b[2]) + abs(field_a[4] - field_b[4])
    combined = weighted_sum([(0.50, field_a), (0.50, field_b)])
    combined[4] = clip(combined[4] + 0.22 * max(0.0, tension - 0.55))
    combined[5] = clip(combined[5] + 0.16 * max(0.0, field_a[5] + field_b[5] - 1.0))
    coherence = field_coherence(combined)
    if coherence >= 0.78 and alignment >= 0.86:
        outcome = "harmonized"
    elif coherence >= 0.72 and combined[5] >= 0.50:
        outcome = "creative_synthesis"
    elif coherence >= 0.58:
        outcome = "interference_managed"
    else:
        outcome = "fragmented"
    return combined, alignment, tension, coherence, outcome


def field_composition(rng):
    regimes = ["harmonic", "complementary", "interference", "fragmentation"]
    rows = []
    for regime in regimes:
        for _ in range(70):
            a, b = generate_composition_pair(regime, rng)
            _combined, alignment, tension, coherence, outcome = compose_fields(a, b)
            rows.append({
                "regime": regime,
                "alignment": alignment,
                "tension": tension,
                "coherence": coherence,
                "outcome": outcome,
            })

    summary = {}
    for regime in regimes:
        regime_rows = [row for row in rows if row["regime"] == regime]
        outcome_counts = Counter(row["outcome"] for row in regime_rows)
        summary[regime] = {
            "count": len(regime_rows),
            "coherence": summarize([row["coherence"] for row in regime_rows]),
            "alignment": summarize([row["alignment"] for row in regime_rows]),
            "tension": summarize([row["tension"] for row in regime_rows]),
            "outcome_counts": dict(outcome_counts),
        }
    return summary


def boundary_falsification(rng):
    cases = []
    for label, center in {
        "pure_noise": [0.18, 0.16, 0.17, 0.12, 0.20, 0.18],
        "isolated_object": [0.62, 0.10, 0.12, 0.08, 0.18, 0.10],
        "mechanical_correlation": [0.22, 0.20, 0.28, 0.18, 0.12, 0.16],
        "valid_relation_control": [0.78, 0.72, 0.60, 0.72, 0.10, 0.58],
    }.items():
        for _ in range(55):
            vector = perturb(center, rng, sigma=0.04)
            primitive, score, _ = nearest_primitive(vector)
            pakheta_fit = pakheta_relation_fit(vector)
            should_abstain = label != "valid_relation_control"
            abstained = pakheta_fit < 0.62
            cases.append({
                "label": label,
                "nearest_primitive": primitive,
                "pakheta_fit": pakheta_fit,
                "should_abstain": should_abstain,
                "abstained": abstained,
            })

    boundary_cases = [case for case in cases if case["should_abstain"]]
    controls = [case for case in cases if not case["should_abstain"]]
    false_positive_rate = sum(1 for case in boundary_cases if not case["abstained"]) / len(boundary_cases) * 100.0
    valid_accept_rate = sum(1 for case in controls if not case["abstained"]) / len(controls) * 100.0

    by_label = {}
    for label in sorted(set(case["label"] for case in cases)):
        label_cases = [case for case in cases if case["label"] == label]
        by_label[label] = {
            "count": len(label_cases),
            "mean_pakheta_fit": round(sum(case["pakheta_fit"] for case in label_cases) / len(label_cases), 4),
            "abstention_rate": round(sum(1 for case in label_cases if case["abstained"]) / len(label_cases) * 100.0, 2),
        }

    return {
        "case_count": len(cases),
        "false_positive_rate_on_boundary_cases": round(false_positive_rate, 2),
        "valid_relation_accept_rate": round(valid_accept_rate, 2),
        "by_label": by_label,
    }


def emergent_primitive_search(rng):
    vectors = []
    labels = []
    for primitive, prototype in PRIMITIVE_PROTOTYPES.items():
        for _ in range(36):
            vectors.append(perturb(prototype, rng, sigma=0.050))
            labels.append(primitive)
    for _ in range(42):
        vectors.append(perturb(EMERGENT_BRIDGE, rng, sigma=0.040))
        labels.append("bridge_candidate")

    assignments, centroids = kmeans_cosine(vectors, k=len(PRIMITIVE_PROTOTYPES) + 1)
    purity, mapping = cluster_purity(assignments, labels)
    emergent_clusters = []
    for cluster_index, centroid in enumerate(centroids):
        cluster_labels = [label for label, assignment in zip(labels, assignments) if assignment == cluster_index]
        if not cluster_labels:
            continue
        majority_label, majority_count = Counter(cluster_labels).most_common(1)[0]
        nearest, nearest_score, _ = nearest_primitive(centroid)
        if majority_label == "bridge_candidate" and nearest_score <= EMERGENT_KNOWN_PRIMITIVE_THRESHOLD:
            emergent_clusters.append({
                "cluster": cluster_index,
                "majority_label": majority_label,
                "purity": round(majority_count / len(cluster_labels), 4),
                "nearest_known_primitive": nearest,
                "nearest_known_score": round(nearest_score, 4),
                "size": len(cluster_labels),
            })

    return {
        "trace_count": len(vectors),
        "cluster_count": len(PRIMITIVE_PROTOTYPES) + 1,
        "overall_cluster_purity": round(purity * 100.0, 2),
        "known_primitive_similarity_threshold": EMERGENT_KNOWN_PRIMITIVE_THRESHOLD,
        "emergent_cluster_count": len(emergent_clusters),
        "emergent_clusters": emergent_clusters,
        "cluster_mapping": mapping,
    }


def creative_actualization(rng):
    targets = [
        [0.74, 0.68, 0.84, 0.76, 0.06, 0.96],
        [0.82, 0.74, 0.76, 0.86, 0.05, 0.88],
        [0.68, 0.88, 0.78, 0.70, 0.08, 0.94],
    ]
    seeds = {
        "anchor": PRIMITIVE_PROTOTYPES["anchor"],
        "context": PRIMITIVE_PROTOTYPES["context"],
        "actualization": PRIMITIVE_PROTOTYPES["actualization"],
        "nonseparability": PRIMITIVE_PROTOTYPES["nonseparability"],
        "bridge_candidate": EMERGENT_BRIDGE,
    }
    sequence_boosts = {
        "Love_Justice_Wisdom_Power": [0.82, 0.78, 0.76, 0.78, 0.05, 0.78],
        "Wisdom_Love_Power": [0.74, 0.86, 0.82, 0.70, 0.08, 0.88],
        "Justice_Bridge_Power": [0.76, 0.72, 0.84, 0.88, 0.04, 0.92],
    }

    rows = []
    for target in targets:
        for _ in range(40):
            best = None
            for seed_a_name, seed_a in seeds.items():
                for seed_b_name, seed_b in seeds.items():
                    if seed_a_name == seed_b_name:
                        continue
                    for sequence_name, sequence_vector in sequence_boosts.items():
                        candidate = weighted_sum([
                            (0.30, seed_a),
                            (0.30, seed_b),
                            (0.40, sequence_vector),
                        ])
                        candidate = perturb(candidate, rng, sigma=0.018)
                        fit = cosine_similarity(candidate, target)
                        coherence = field_coherence(candidate)
                        novelty = candidate[5]
                        score = 0.50 * fit + 0.30 * coherence + 0.20 * novelty
                        if best is None or score > best["score"]:
                            best = {
                                "seed_a": seed_a_name,
                                "seed_b": seed_b_name,
                                "sequence": sequence_name,
                                "score": score,
                                "fit": fit,
                                "coherence": coherence,
                                "novelty": novelty,
                                "decoherence": candidate[4],
                            }

            stable_novel = best["fit"] >= 0.90 and best["coherence"] >= 0.78 and best["novelty"] >= 0.56 and best["decoherence"] <= 0.22
            rows.append({**best, "stable_novel_form": stable_novel})

    return {
        "attempt_count": len(rows),
        "stable_novel_rate": round(sum(1 for row in rows if row["stable_novel_form"]) / len(rows) * 100.0, 2),
        "score": summarize([row["score"] for row in rows]),
        "fit": summarize([row["fit"] for row in rows]),
        "coherence": summarize([row["coherence"] for row in rows]),
        "novelty": summarize([row["novelty"] for row in rows]),
        "top_designs": sorted(
            [
                {
                    "seed_a": row["seed_a"],
                    "seed_b": row["seed_b"],
                    "sequence": row["sequence"],
                    "score": round(row["score"], 4),
                    "fit": round(row["fit"], 4),
                    "coherence": round(row["coherence"], 4),
                    "novelty": round(row["novelty"], 4),
                }
                for row in rows
            ],
            key=lambda item: item["score"],
            reverse=True,
        )[:8],
    }


def print_section(title):
    print(f"\n  {BOLD}{CYAN}[{title}]{RESET}")


def main():
    print_header("Experiment: Pakheta Capability Envelope")
    start_time = datetime.now(timezone.utc)
    rng = random.Random(613)

    generative = generative_field_design(rng)
    discovery = blind_primitive_discovery(rng)
    prediction = prediction_before_repair(rng)
    composition = field_composition(rng)
    boundary = boundary_falsification(rng)
    emergent = emergent_primitive_search(rng)
    creative = creative_actualization(rng)

    print_section("Capability Summary")
    print(f"  generative target hit rate:       {GREEN}{generative['target_hit_rate']:.2f}%{RESET}")
    print(f"  blind primitive rediscovery:      {GREEN}{discovery['rediscovery_rate']:.2f}%{RESET}")
    print(f"  prediction-before-repair accuracy:{capability_color(prediction['prediction_accuracy'] / 100.0)} {prediction['prediction_accuracy']:.2f}%{RESET}")
    print(f"  boundary false-positive rate:     {GREEN}{boundary['false_positive_rate_on_boundary_cases']:.2f}%{RESET}")
    print(f"  emergent primitive clusters:      {GREEN}{emergent['emergent_cluster_count']}{RESET}")
    print(f"  creative stable-novel rate:       {GREEN}{creative['stable_novel_rate']:.2f}%{RESET}")

    print_section("Composition Outcomes")
    for regime, values in composition.items():
        print(
            f"  {regime:<15} coherence={values['coherence']['mean']:.4f} "
            f"alignment={values['alignment']['mean']:.4f} outcomes={values['outcome_counts']}"
        )

    output = {
        "experiment_name": "pakheta_capability_envelope",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        "dimensions": DIMENSIONS,
        "capabilities": {
            "generative_field_design": generative,
            "blind_primitive_discovery": discovery,
            "prediction_before_repair": prediction,
            "field_composition": composition,
            "boundary_falsification": boundary,
            "emergent_primitive_search": emergent,
            "creative_actualization": creative,
        },
        "limits_observed": [
            "Fragmentation compositions remain low-coherence rather than being forced into success.",
            "Boundary cases are allowed to abstain instead of receiving a Pakheta explanation.",
            "Latent-ready fields can still prefer Love/gathering before Power when binding headroom remains.",
            "Emergent primitive search only proposes a candidate cluster; it does not canonize a new primitive.",
        ],
    }

    output_file = Path(__file__).resolve().parent / "capability_envelope_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {BOLD}{GREEN}Success:{RESET} Pakheta capability envelope completed.")
    print(f"  Results saved to: {output_file.name}")
    print("\n  [Ontological Analysis]")
    print("  1. Pakheta can be probed as a generative and predictive relation-space,")
    print("     not only as an audit or repair mechanism.")
    print("  2. The model should be allowed to abstain at its boundary; otherwise")
    print("     Pakheta collapses into an all-purpose metaphor.")
    print("  3. Emergent primitive search gives candidates, not canonized primitives.")


if __name__ == "__main__":
    main()
