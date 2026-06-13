"""
Pakheta Relational Compatibility Engine.

This experiment starts small with familiar constants.  It does not ask whether
two numeric objects are equal or even similar.  It asks whether two directed
relationships behave compatibly:

    A -> B can be compatible with C -> D

even when A, B, C, and D are very different objects.

Each relation is represented by the ratio B/A, fit to the LJPW coordinate
lattice, then described by operator mix, direction, strength, and purpose
archetype.  Compatibility is measured between relation profiles.
"""

import argparse
import ctypes
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = EXPERIMENT_DIR / "relational_compatibility_results.json"

BASE = 30.0
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)

OPERATORS = {
    "Love": L0,
    "Justice": J0,
    "Power": P0,
    "Wisdom": W0,
}

OPERATOR_KEYS = {
    "Love": "c_L",
    "Justice": "c_J",
    "Power": "c_P",
    "Wisdom": "c_W",
}

CONSTANTS = {
    "one": 1.0,
    "phi": (1.0 + math.sqrt(5.0)) / 2.0,
    "phi_inverse_L0": L0,
    "pi": math.pi,
    "tau": 2.0 * math.pi,
    "e": math.e,
    "sqrt2": math.sqrt(2.0),
    "sqrt3": math.sqrt(3.0),
    "sqrt5": math.sqrt(5.0),
    "ln2_W0": W0,
    "justice_J0": J0,
    "power_P0": P0,
}

PURPOSE_ARCHETYPES = {
    "binding_gathering": {
        "mix": {"Love": 0.66, "Justice": 0.20, "Power": 0.04, "Wisdom": 0.10},
        "preferred_direction": "compressing",
        "read": "Gathers or binds while preserving some boundary.",
    },
    "boundary_differentiation": {
        "mix": {"Love": 0.08, "Justice": 0.70, "Power": 0.08, "Wisdom": 0.14},
        "preferred_direction": "any",
        "read": "Emphasizes distinction, edge, and normalization.",
    },
    "actualizing_growth": {
        "mix": {"Love": 0.10, "Justice": 0.08, "Power": 0.70, "Wisdom": 0.12},
        "preferred_direction": "amplifying",
        "read": "Moves a latent relation into expressed growth or work.",
    },
    "context_scaling": {
        "mix": {"Love": 0.10, "Justice": 0.18, "Power": 0.07, "Wisdom": 0.65},
        "preferred_direction": "any",
        "read": "Changes context, scale, or informational frame.",
    },
    "bridge_harmony": {
        "mix": {"Love": 0.48, "Justice": 0.42, "Power": 0.05, "Wisdom": 0.05},
        "preferred_direction": "any",
        "read": "Connects two nodes through a balanced gather/boundary relation.",
    },
    "integrated_relation": {
        "mix": {"Love": 0.25, "Justice": 0.25, "Power": 0.25, "Wisdom": 0.25},
        "preferred_direction": "any",
        "read": "Uses all operators with similar load.",
    },
}


class CRelationalNumber(ctypes.Structure):
    _fields_ = [
        ("c_L", ctypes.c_int16),
        ("c_J", ctypes.c_int16),
        ("c_P", ctypes.c_int16),
        ("c_W", ctypes.c_int16),
    ]


class CRelationalFit(ctypes.Structure):
    _fields_ = [
        ("coord", CRelationalNumber),
        ("target_log30", ctypes.c_double),
        ("fitted_log30", ctypes.c_double),
        ("signed_log30_residue", ctypes.c_double),
        ("absolute_log30_residue", ctypes.c_double),
        ("coordinate_l1", ctypes.c_int32),
        ("complexity_penalty", ctypes.c_double),
        ("relational_score", ctypes.c_double),
        ("reconstructed_value", ctypes.c_double),
        ("relative_value_error", ctypes.c_double),
    ]


def load_c_fit_library():
    path = EXPERIMENT_DIR / "relational_calculator.dll"
    if not path.exists():
        return None, None
    try:
        lib = ctypes.CDLL(str(path))
        lib.fit_log30_target.argtypes = [ctypes.c_double, ctypes.c_int]
        lib.fit_log30_target.restype = CRelationalFit
        return lib, path
    except OSError:
        return None, None


def c_fit_to_dict(fit):
    return {
        "coefficients": {
            "c_L": fit.coord.c_L,
            "c_J": fit.coord.c_J,
            "c_P": fit.coord.c_P,
            "c_W": fit.coord.c_W,
        },
        "target_log30": fit.target_log30,
        "fitted_log30": fit.fitted_log30,
        "signed_log30_residue": fit.signed_log30_residue,
        "absolute_log30_residue": fit.absolute_log30_residue,
        "coordinate_l1": fit.coordinate_l1,
        "complexity_penalty": fit.complexity_penalty,
        "relational_score": fit.relational_score,
        "reconstructed_value": fit.reconstructed_value,
        "relative_value_error": fit.relative_value_error,
    }


def build_coordinate_triples(max_coordinate):
    triples = []
    for c_l in range(-max_coordinate, max_coordinate + 1):
        l_part = c_l * L0
        for c_j in range(-max_coordinate, max_coordinate + 1):
            lj_part = l_part + c_j * J0
            for c_p in range(-max_coordinate, max_coordinate + 1):
                partial = lj_part + c_p * P0
                triples.append((c_l, c_j, c_p, partial, abs(c_l) + abs(c_j) + abs(c_p)))
    return triples


def python_fit_log30_target(target_log30, triples, max_coordinate):
    target_value = BASE ** target_log30
    best = None
    for c_l, c_j, c_p, partial, l1_without_w in triples:
        raw_w = (target_log30 - partial) / W0
        center_w = int(round(raw_w))
        for c_w in (center_w - 1, center_w, center_w + 1):
            if c_w < -max_coordinate or c_w > max_coordinate:
                continue
            fitted_log30 = partial + c_w * W0
            signed_residue = fitted_log30 - target_log30
            residue = abs(signed_residue)
            l1 = l1_without_w + abs(c_w)
            complexity_penalty = 1.0 + l1 / (4.0 * max_coordinate)
            score = residue * complexity_penalty
            if best is None or score < best["relational_score"]:
                reconstructed = BASE ** fitted_log30
                best = {
                    "coefficients": {
                        "c_L": c_l,
                        "c_J": c_j,
                        "c_P": c_p,
                        "c_W": c_w,
                    },
                    "target_log30": target_log30,
                    "fitted_log30": fitted_log30,
                    "signed_log30_residue": signed_residue,
                    "absolute_log30_residue": residue,
                    "coordinate_l1": l1,
                    "complexity_penalty": complexity_penalty,
                    "relational_score": score,
                    "reconstructed_value": reconstructed,
                    "relative_value_error": reconstructed / target_value - 1.0,
                }
    return best


def normalize_vector(vector):
    total = sum(abs(value) for value in vector.values())
    if total == 0.0:
        return {key: 0.0 for key in vector}
    return {key: abs(value) / total for key, value in vector.items()}


def signed_operator_vector(coefficients):
    return {
        operator: coefficients[OPERATOR_KEYS[operator]] * OPERATORS[operator]
        for operator in OPERATORS
    }


def cosine(left, right):
    keys = sorted(set(left) | set(right))
    numerator = sum(left.get(key, 0.0) * right.get(key, 0.0) for key in keys)
    left_norm = math.sqrt(sum(left.get(key, 0.0) ** 2 for key in keys))
    right_norm = math.sqrt(sum(right.get(key, 0.0) ** 2 for key in keys))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def entropy_normalized(values):
    total = sum(values)
    if total <= 0.0:
        return 0.0
    entropy = 0.0
    for value in values:
        if value <= 0.0:
            continue
        probability = value / total
        entropy -= probability * math.log2(probability)
    return entropy / math.log2(len(values)) if len(values) > 1 else 0.0


def direction_for_ratio(ratio):
    if ratio > 1.0 + 1e-12:
        return "amplifying"
    if ratio < 1.0 - 1e-12:
        return "compressing"
    return "identity"


def direction_bonus(direction, preferred):
    if preferred == "any":
        return 1.0
    if direction == preferred:
        return 1.0
    if direction == "identity":
        return 0.75
    return 0.35


def purpose_scores(operator_mix, direction):
    scores = {}
    for purpose, archetype in PURPOSE_ARCHETYPES.items():
        mix_score = cosine(operator_mix, archetype["mix"])
        direction_score = direction_bonus(direction, archetype["preferred_direction"])
        scores[purpose] = 0.82 * mix_score + 0.18 * direction_score
    return scores


def classify_purpose(scores):
    purpose = max(scores, key=scores.get)
    return {
        "purpose": purpose,
        "score": scores[purpose],
        "read": PURPOSE_ARCHETYPES[purpose]["read"],
    }


def fit_quality(abs_residue):
    return 1.0 / (1.0 + 1000.0 * abs_residue)


def relation_profile(source, target, fit_func):
    source_value = CONSTANTS[source]
    target_value = CONSTANTS[target]
    ratio = target_value / source_value
    target_log30 = math.log(ratio) / math.log(BASE)
    fit = fit_func(target_log30)
    signed_vector = signed_operator_vector(fit["coefficients"])
    operator_mix = normalize_vector(signed_vector)
    mix_entropy = entropy_normalized(list(operator_mix.values()))
    direction = direction_for_ratio(ratio)
    strength = math.tanh(abs(math.log(ratio)))
    scores = purpose_scores(operator_mix, direction)
    purpose = classify_purpose(scores)

    return {
        "id": f"{source}->{target}",
        "source": source,
        "target": target,
        "source_value": source_value,
        "target_value": target_value,
        "ratio": ratio,
        "direction": direction,
        "log_strength": abs(math.log(ratio)),
        "bounded_strength": strength,
        "fit": fit,
        "signed_operator_vector": signed_vector,
        "operator_mix": operator_mix,
        "operator_mix_entropy": mix_entropy,
        "dominant_operator": max(operator_mix, key=operator_mix.get),
        "fit_quality": fit_quality(fit["absolute_log30_residue"]),
        "purpose_scores": scores,
        "best_purpose": purpose,
    }


def object_similarity_for_relations(left, right):
    source_similarity = math.exp(
        -abs(math.log(left["source_value"] / right["source_value"]))
    )
    target_similarity = math.exp(
        -abs(math.log(left["target_value"] / right["target_value"]))
    )
    same_node_count = len(
        {left["source"], left["target"]} & {right["source"], right["target"]}
    )
    overlap = same_node_count / 2.0
    return {
        "source_target_value_similarity": (source_similarity + target_similarity) / 2.0,
        "node_overlap": overlap,
    }


def relation_compatibility(left, right):
    mix_similarity = cosine(left["operator_mix"], right["operator_mix"])
    signed_similarity = (cosine(left["signed_operator_vector"], right["signed_operator_vector"]) + 1.0) / 2.0
    strength_similarity = math.exp(
        -abs(left["log_strength"] - right["log_strength"])
    )
    direction_similarity = 1.0 if left["direction"] == right["direction"] else 0.35
    purpose_similarity = cosine(left["purpose_scores"], right["purpose_scores"])
    fit_support = min(left["fit_quality"], right["fit_quality"])
    compatibility = (
        0.30 * mix_similarity
        + 0.20 * signed_similarity
        + 0.15 * strength_similarity
        + 0.10 * direction_similarity
        + 0.20 * purpose_similarity
        + 0.05 * fit_support
    )
    object_similarity = object_similarity_for_relations(left, right)
    return {
        "left": left["id"],
        "right": right["id"],
        "compatibility": compatibility,
        "mix_similarity": mix_similarity,
        "signed_similarity": signed_similarity,
        "strength_similarity": strength_similarity,
        "direction_similarity": direction_similarity,
        "purpose_similarity": purpose_similarity,
        "fit_support": fit_support,
        "left_purpose": left["best_purpose"]["purpose"],
        "right_purpose": right["best_purpose"]["purpose"],
        "object_similarity": object_similarity,
        "compatibility_minus_object_similarity": (
            compatibility - object_similarity["source_target_value_similarity"]
        ),
    }


def node_profiles(fit_func):
    rows = []
    for name, value in CONSTANTS.items():
        target_log30 = math.log(value) / math.log(BASE)
        fit = fit_func(target_log30)
        rows.append({
            "name": name,
            "value": value,
            "fit": fit,
        })
    return rows


def build_relations(fit_func):
    relations = []
    for source in CONSTANTS:
        for target in CONSTANTS:
            if source == target:
                continue
            relations.append(relation_profile(source, target, fit_func))
    return relations


def build_pairwise_compatibilities(relations):
    rows = []
    for left_index, left in enumerate(relations):
        for right in relations[left_index + 1:]:
            if left["id"] == right["id"]:
                continue
            rows.append(relation_compatibility(left, right))
    return rows


def relation_lookup(relations):
    return {relation["id"]: relation for relation in relations}


def summarize(values):
    if not values:
        return None
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "max": max(values),
    }


def purpose_leaders(relations, count=5):
    rows = {}
    for purpose in PURPOSE_ARCHETYPES:
        ranked = sorted(
            relations,
            key=lambda relation: relation["purpose_scores"][purpose],
            reverse=True,
        )
        rows[purpose] = [
            {
                "relation": relation["id"],
                "ratio": relation["ratio"],
                "score": relation["purpose_scores"][purpose],
                "direction": relation["direction"],
                "operator_mix": relation["operator_mix"],
            }
            for relation in ranked[:count]
        ]
    return rows


def top_compatible_for_relation(target_relation_id, relations, compatibilities, count=10, disjoint_only=False):
    relation = relation_lookup(relations)[target_relation_id]
    rows = []
    for compatibility in compatibilities:
        if compatibility["left"] == target_relation_id:
            other_id = compatibility["right"]
        elif compatibility["right"] == target_relation_id:
            other_id = compatibility["left"]
        else:
            continue
        other = relation_lookup(relations)[other_id]
        if disjoint_only and ({relation["source"], relation["target"]} & {other["source"], other["target"]}):
            continue
        rows.append({
            **compatibility,
            "other_relation": other_id,
            "other_ratio": other["ratio"],
            "other_operator_mix": other["operator_mix"],
            "other_best_purpose": other["best_purpose"],
        })
    return sorted(rows, key=lambda row: row["compatibility"], reverse=True)[:count]


def build_report(args):
    c_lib, c_path = load_c_fit_library()
    triples = None

    if c_lib is not None and args.fit_engine in ("auto", "c"):
        fit_engine = "c"

        def fit_func(target_log30):
            return c_fit_to_dict(
                c_lib.fit_log30_target(
                    ctypes.c_double(target_log30),
                    ctypes.c_int(args.max_coordinate),
                )
            )
    else:
        fit_engine = "python"
        triples = build_coordinate_triples(args.max_coordinate)

        def fit_func(target_log30):
            return python_fit_log30_target(
                target_log30,
                triples,
                args.max_coordinate,
            )

    nodes = node_profiles(fit_func)
    relations = build_relations(fit_func)
    compatibilities = build_pairwise_compatibilities(relations)
    compatibility_ranked = sorted(
        compatibilities,
        key=lambda row: row["compatibility"],
        reverse=True,
    )
    low_object_ranked = sorted(
        [
            row for row in compatibilities
            if row["object_similarity"]["node_overlap"] == 0.0
            and row["object_similarity"]["source_target_value_similarity"] < args.low_object_similarity_threshold
        ],
        key=lambda row: row["compatibility"],
        reverse=True,
    )
    relation_by_id = relation_lookup(relations)
    phi_pi = relation_by_id["phi->pi"]

    report = {
        "experiment_name": "pakheta_relational_compatibility_engine",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "fit_engine_requested": args.fit_engine,
            "fit_engine_used": fit_engine,
            "c_fit_library_path": str(c_path) if c_path else None,
            "max_coordinate": args.max_coordinate,
            "constant_count": len(CONSTANTS),
            "relation_count": len(relations),
            "compatibility_pair_count": len(compatibilities),
            "low_object_similarity_threshold": args.low_object_similarity_threshold,
        },
        "method": {
            "node": "A positive constant with an LJPW coordinate fit.",
            "relation": "A directed transformation A -> B represented by ratio B/A.",
            "compatibility": (
                "Relation-to-relation similarity over operator mix, signed operator "
                "shape, direction, strength, purpose archetype, and fit support."
            ),
            "purpose_read": (
                "Purpose labels are not final ontology. They are small archetypes "
                "for measuring relational role: binding, boundary, growth, context, "
                "bridge, and integrated relation."
            ),
        },
        "nodes": nodes,
        "relations": relations,
        "compatibility_summary": {
            "compatibility": summarize([row["compatibility"] for row in compatibilities]),
            "compatibility_minus_object_similarity": summarize([
                row["compatibility_minus_object_similarity"]
                for row in compatibilities
            ]),
        },
        "purpose_leaders": purpose_leaders(relations),
        "phi_to_pi_relation": phi_pi,
        "phi_to_pi_top_compatible_relations": top_compatible_for_relation(
            "phi->pi",
            relations,
            compatibilities,
            count=12,
            disjoint_only=False,
        ),
        "phi_to_pi_top_disjoint_compatible_relations": top_compatible_for_relation(
            "phi->pi",
            relations,
            compatibilities,
            count=12,
            disjoint_only=True,
        ),
        "top_compatible_relation_pairs": compatibility_ranked[:30],
        "top_compatible_low_object_similarity_pairs": low_object_ranked[:30],
        "interpretation": {
            "short_read": (
                "This is a small numeric compatibility engine. It shows how "
                "relations can be compared by role and operator behavior even "
                "when the objects are not numerically similar."
            ),
            "important_boundary": (
                "Compatibility is not equality and not proof. It is a way to "
                "measure whether two transformations serve a similar relational "
                "purpose."
            ),
        },
    }
    return report


def write_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report):
    phi_pi = report["phi_to_pi_relation"]
    print()
    print("Pakheta Relational Compatibility Engine")
    print("=" * 42)
    print("Fit engine:", report["configuration"]["fit_engine_used"])
    print("Constants:", report["configuration"]["constant_count"])
    print("Relations:", report["configuration"]["relation_count"])
    print("Compatibility pairs:", report["configuration"]["compatibility_pair_count"])
    print()
    print(
        "phi -> pi:",
        f"ratio={phi_pi['ratio']:.6f}",
        f"direction={phi_pi['direction']}",
        f"purpose={phi_pi['best_purpose']['purpose']}",
        f"strength={phi_pi['bounded_strength']:.4f}",
    )
    print("operator mix:", {
        key: round(value, 4)
        for key, value in phi_pi["operator_mix"].items()
    })
    print()
    print("Top phi -> pi compatible relations:")
    for row in report["phi_to_pi_top_compatible_relations"][:8]:
        print(
            f"  {row['other_relation']:<28} "
            f"compat={row['compatibility']:.4f} "
            f"purpose={row['right_purpose'] if row['left'] == 'phi->pi' else row['left_purpose']}"
        )
    print()
    print("Compatible relations with low object similarity:")
    for row in report["top_compatible_low_object_similarity_pairs"][:8]:
        print(
            f"  {row['left']:<28} ~ {row['right']:<28} "
            f"compat={row['compatibility']:.4f} "
            f"object_sim={row['object_similarity']['source_target_value_similarity']:.4f}"
        )
    print()
    print(f"Results saved to: {OUTPUT_FILE.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Measure compatibility between numeric relationships."
    )
    parser.add_argument("--max-coordinate", type=int, default=10)
    parser.add_argument(
        "--fit-engine",
        choices=["auto", "c", "python"],
        default="auto",
    )
    parser.add_argument("--low-object-similarity-threshold", type=float, default=0.55)
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)
    write_report(report)
    print_summary(report)


if __name__ == "__main__":
    main()
