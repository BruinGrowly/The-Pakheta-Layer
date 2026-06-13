"""
Pakheta Predictive Relation Families Experiment.

This experiment moves the purpose-first relation search from descriptive
labeling to prediction. It derives archetype profiles (centroids) directly
from cohesive identity families and uses them to:
1. Retrieve a withheld relation from the non-exemplar candidate pool.
2. Predict a missing target constant B given source A and the family archetype.
3. Predict a missing source constant A given target B and the family archetype.
"""

import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import pakheta_relational_compatibility_engine as compat

EXPERIMENT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = EXPERIMENT_DIR / "predictive_relation_families_results.json"

PURPOSE_CONSTANTS = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "five": 5.0,
    "phi": (1.0 + math.sqrt(5.0)) / 2.0,
    "phi_squared": ((1.0 + math.sqrt(5.0)) / 2.0) ** 2,
    "phi_inverse_L0": compat.L0,
    "pi": math.pi,
    "tau": 2.0 * math.pi,
    "e": math.e,
    "sqrt2": math.sqrt(2.0),
    "sqrt3": math.sqrt(3.0),
    "sqrt5": math.sqrt(5.0),
    "ln2_W0": compat.W0,
    "justice_J0": compat.J0,
    "power_P0": compat.P0,
}

RELATION_FAMILIES = {
    "root_closures": {
        "name": "Root Closures",
        "description": "Roots that close exactly on integer values under multiplication.",
        "relations": ["one->sqrt2", "one->sqrt3", "one->sqrt5"],
    },
    "circle_scaling": {
        "name": "Circle Scaling",
        "description": "Boundary doubling/halving and circle-turn relation shifts.",
        "relations": ["pi->tau", "tau->pi", "one->two", "two->one"],
    },
    "golden_harmony": {
        "name": "Golden Harmony",
        "description": "Proportional coherence, reciprocal repairs, and golden growth.",
        "relations": ["one->phi", "phi_inverse_L0->one", "phi->phi_squared", "phi->one", "one->phi_inverse_L0"],
    },
    "natural_growth": {
        "name": "Natural Growth",
        "description": "Logarithmic and exponential growth shifts.",
        "relations": ["one->e", "e->one", "sqrt2->e", "sqrt2->ln2_W0"],
    }
}


def configure_fit(args):
    c_lib, c_path = compat.load_c_fit_library()
    if c_lib is not None and args.fit_engine in ("auto", "c"):
        fit_engine = "c"

        def fit_func(target_log30):
            return compat.c_fit_to_dict(
                c_lib.fit_log30_target(
                    compat.ctypes.c_double(target_log30),
                    compat.ctypes.c_int(args.max_coordinate),
                )
            )

        return fit_func, fit_engine, c_path

    triples = compat.build_coordinate_triples(args.max_coordinate)

    def fit_func(target_log30):
        return compat.python_fit_log30_target(
            target_log30,
            triples,
            args.max_coordinate,
        )

    return fit_func, "python", None


def build_relations(fit_func):
    original_constants = compat.CONSTANTS
    try:
        compat.CONSTANTS = PURPOSE_CONSTANTS
        return compat.build_relations(fit_func)
    finally:
        compat.CONSTANTS = original_constants


def relation_lookup(relations):
    return {relation["id"]: relation for relation in relations}


def cosine(left, right):
    keys = sorted(set(left) | set(right))
    numerator = sum(left.get(key, 0.0) * right.get(key, 0.0) for key in keys)
    left_norm = math.sqrt(sum(left.get(key, 0.0) ** 2 for key in keys))
    right_norm = math.sqrt(sum(right.get(key, 0.0) ** 2 for key in keys))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def profile_compatibility(candidate, archetype):
    mix_similarity = cosine(candidate["operator_mix"], archetype["operator_mix"])
    signed_similarity = (cosine(candidate["signed_operator_vector"], archetype["signed_operator_vector"]) + 1.0) / 2.0
    strength_similarity = math.exp(
        -abs(candidate["log_strength"] - archetype["log_strength"])
    )
    if "direction_distribution" in archetype:
        direction_similarity = sum(
            weight * (1.0 if candidate["direction"] == direction else 0.35)
            for direction, weight in archetype["direction_distribution"].items()
        )
    else:
        direction_similarity = 1.0 if candidate["direction"] == archetype["direction"] else 0.35
    purpose_similarity = cosine(candidate["purpose_scores"], archetype["purpose_scores"])
    fit_support = min(candidate["fit_quality"], archetype["fit_quality"])
    
    compatibility = (
        0.30 * mix_similarity
        + 0.20 * signed_similarity
        + 0.15 * strength_similarity
        + 0.10 * direction_similarity
        + 0.20 * purpose_similarity
        + 0.05 * fit_support
    )
    return compatibility


def derive_archetype(exemplars):
    if not exemplars:
        return None
    
    avg_mix = {}
    for op in ["Love", "Justice", "Power", "Wisdom"]:
        avg_mix[op] = statistics.fmean([e["operator_mix"].get(op, 0.0) for e in exemplars])
        
    avg_signed = {}
    for op in ["Love", "Justice", "Power", "Wisdom"]:
        avg_signed[op] = statistics.fmean([e["signed_operator_vector"].get(op, 0.0) for e in exemplars])
        
    avg_log_strength = statistics.fmean([e["log_strength"] for e in exemplars])
    
    directions = [e["direction"] for e in exemplars]
    direction_counts = {
        direction: directions.count(direction)
        for direction in sorted(set(directions))
    }
    max_direction_count = max(direction_counts.values())
    top_directions = [
        direction
        for direction, count in direction_counts.items()
        if count == max_direction_count
    ]
    majority_direction = top_directions[0] if len(top_directions) == 1 else "mixed"
    direction_distribution = {
        direction: count / len(directions)
        for direction, count in direction_counts.items()
    }
    
    avg_purpose = {}
    purposes = list(exemplars[0]["purpose_scores"].keys())
    for p in purposes:
        avg_purpose[p] = statistics.fmean([e["purpose_scores"].get(p, 0.0) for e in exemplars])
        
    avg_fit_quality = statistics.fmean([e["fit_quality"] for e in exemplars])
    
    return {
        "operator_mix": avg_mix,
        "signed_operator_vector": avg_signed,
        "log_strength": avg_log_strength,
        "direction": majority_direction,
        "direction_distribution": direction_distribution,
        "purpose_scores": avg_purpose,
        "fit_quality": avg_fit_quality
    }


def run_experiments(relations, fit_func, top_n):
    original_constants = compat.CONSTANTS
    try:
        compat.CONSTANTS = PURPOSE_CONSTANTS
        by_id = relation_lookup(relations)
        results = {}

        for family_key, family in RELATION_FAMILIES.items():
            family_relations = [by_id[rid] for rid in family["relations"] if rid in by_id]
            if len(family_relations) < 2:
                continue

            family_results = {
                "name": family["name"],
                "description": family["description"],
                "relation_predictions": [],
                "target_predictions": [],
                "source_predictions": []
            }

            # 1. Leave-One-Out Relation Prediction
            for withheld in family_relations:
                exemplars = [r for r in family_relations if r["id"] != withheld["id"]]
                archetype = derive_archetype(exemplars)

                # Rank all non-exemplar relations in the DB against this archetype.
                ranked_relations = []
                for r in relations:
                    # Exclude exemplar relations themselves
                    if r["id"] in [ex["id"] for ex in exemplars]:
                        continue
                    score = profile_compatibility(r, archetype)
                    ranked_relations.append({
                        "relation_id": r["id"],
                        "score": score,
                        "direction": r["direction"],
                        "best_purpose": r["best_purpose"]["purpose"]
                    })
                ranked_relations.sort(key=lambda x: x["score"], reverse=True)

                # Find rank of withheld
                withheld_rank = None
                for idx, r in enumerate(ranked_relations, start=1):
                    if r["relation_id"] == withheld["id"]:
                        withheld_rank = idx
                        break

                family_results["relation_predictions"].append({
                    "withheld_relation": withheld["id"],
                    "score": ranked_relations[withheld_rank - 1]["score"] if withheld_rank else 0.0,
                    "rank": withheld_rank,
                    "candidate_pool_size": len(ranked_relations),
                    "percentile": withheld_rank / len(ranked_relations) if withheld_rank else None,
                    "in_top_n": withheld_rank <= top_n if withheld_rank else False,
                    "top_retrieved": ranked_relations[:5]
                })

            # 2. Missing Target Prediction (Given source A, predict B)
            # 3. Missing Source Prediction (Given target B, predict A)
            for withheld in family_relations:
                exemplars = [r for r in family_relations if r["id"] != withheld["id"]]
                archetype = derive_archetype(exemplars)

                source = withheld["source"]
                target = withheld["target"]

                # Predict target (varying target constant X for relation source -> X)
                target_candidates = []
                for const_name in PURPOSE_CONSTANTS:
                    if const_name == source:
                        continue
                    # Construct candidate profile source -> const_name
                    candidate_rel = compat.relation_profile(source, const_name, fit_func)
                    score = profile_compatibility(candidate_rel, archetype)
                    target_candidates.append({
                        "candidate_target": const_name,
                        "score": score
                    })
                target_candidates.sort(key=lambda x: x["score"], reverse=True)

                target_rank = None
                for idx, tc in enumerate(target_candidates, start=1):
                    if tc["candidate_target"] == target:
                        target_rank = idx
                        break

                family_results["target_predictions"].append({
                    "source": source,
                    "expected_target": target,
                    "score": target_candidates[target_rank - 1]["score"] if target_rank else 0.0,
                    "rank": target_rank,
                    "is_first": target_rank == 1,
                    "top_predictions": target_candidates[:3]
                })

                # Predict source (varying source constant Y for relation Y -> target)
                source_candidates = []
                for const_name in PURPOSE_CONSTANTS:
                    if const_name == target:
                        continue
                    candidate_rel = compat.relation_profile(const_name, target, fit_func)
                    score = profile_compatibility(candidate_rel, archetype)
                    source_candidates.append({
                        "candidate_source": const_name,
                        "score": score
                    })
                source_candidates.sort(key=lambda x: x["score"], reverse=True)

                source_rank = None
                for idx, sc in enumerate(source_candidates, start=1):
                    if sc["candidate_source"] == source:
                        source_rank = idx
                        break

                family_results["source_predictions"].append({
                    "expected_source": source,
                    "target": target,
                    "score": source_candidates[source_rank - 1]["score"] if source_rank else 0.0,
                    "rank": source_rank,
                    "is_first": source_rank == 1,
                    "top_predictions": source_candidates[:3]
                })

            results[family_key] = family_results

        return results
    finally:
        compat.CONSTANTS = original_constants


def summarize_metrics(results):
    all_rel_ranks = []
    all_rel_percentiles = []
    all_target_ranks = []
    all_source_ranks = []
    correct_target_count = 0
    correct_source_count = 0
    total_target_predictions = 0
    total_source_predictions = 0

    for family in results.values():
        for r_pred in family["relation_predictions"]:
            if r_pred["rank"] is not None:
                all_rel_ranks.append(r_pred["rank"])
                all_rel_percentiles.append(r_pred["percentile"])
        for t_pred in family["target_predictions"]:
            all_target_ranks.append(t_pred["rank"])
            if t_pred["is_first"]:
                correct_target_count += 1
            total_target_predictions += 1
        for s_pred in family["source_predictions"]:
            all_source_ranks.append(s_pred["rank"])
            if s_pred["is_first"]:
                correct_source_count += 1
            total_source_predictions += 1

    return {
        "total_relationships_tested": len(all_rel_ranks),
        "relation_retrieved_median_rank": statistics.median(all_rel_ranks) if all_rel_ranks else None,
        "relation_retrieved_median_percentile": statistics.median(all_rel_percentiles) if all_rel_percentiles else None,
        "relation_retrieved_mean_rank": statistics.fmean(all_rel_ranks) if all_rel_ranks else None,
        "target_prediction_median_rank": statistics.median(all_target_ranks) if all_target_ranks else None,
        "source_prediction_median_rank": statistics.median(all_source_ranks) if all_source_ranks else None,
        "target_prediction_accuracy_rank_1": correct_target_count / total_target_predictions if total_target_predictions else 0.0,
        "source_prediction_accuracy_rank_1": correct_source_count / total_source_predictions if total_source_predictions else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Predictive Relation Families experiment."
    )
    parser.add_argument("--max-coordinate", type=int, default=10)
    parser.add_argument(
        "--fit-engine",
        choices=["auto", "c", "python"],
        default="auto",
    )
    parser.add_argument("--top-n", type=int, default=20)
    args = parser.parse_args()

    print("Executing Predictive Relation Families Experiment...")
    fit_func, fit_engine, c_path = configure_fit(args)
    relations = build_relations(fit_func)

    results = run_experiments(relations, fit_func, args.top_n)
    metrics = summarize_metrics(results)

    report = {
        "experiment_name": "pakheta_predictive_relation_families",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "fit_engine_used": fit_engine,
            "max_coordinate": args.max_coordinate,
            "constant_count": len(PURPOSE_CONSTANTS),
            "relation_count": len(relations),
            "top_n": args.top_n
        },
        "metrics": metrics,
        "family_results": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\nExperiment Complete.")
    print("=" * 40)
    print(f"Fit Engine: {fit_engine}")
    print(f"Total Relations: {len(relations)}")
    print(f"Total Relationships Tested: {metrics['total_relationships_tested']}")
    print(f"Median Relation LOO Rank: {metrics['relation_retrieved_median_rank']}")
    print(f"Median Relation LOO Percentile: {metrics['relation_retrieved_median_percentile']:.2%}")
    print(f"Target Prediction Median Rank: {metrics['target_prediction_median_rank']}")
    print(f"Source Prediction Median Rank: {metrics['source_prediction_median_rank']}")
    print(f"Target Prediction Rank 1 Accuracy: {metrics['target_prediction_accuracy_rank_1']:.2%}")
    print(f"Source Prediction Rank 1 Accuracy: {metrics['source_prediction_accuracy_rank_1']:.2%}")
    print(f"Results saved to: {OUTPUT_FILE.name}\n")


if __name__ == "__main__":
    main()
