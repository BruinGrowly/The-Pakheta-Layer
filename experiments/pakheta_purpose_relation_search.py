"""
Pakheta Purpose-First Relation Search.

This experiment tests the new compatibility idea against well-known constants.
Instead of asking which objects are similar, it asks:

1. Given a purpose, which directed constant relations are retrieved?
2. Can those relations act as operators that produce known targets?

The second question is the important one.  A relation is not just a fit; it can
be leveraged as a transformation.
"""

import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import pakheta_relational_compatibility_engine as compat


EXPERIMENT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = EXPERIMENT_DIR / "purpose_relation_search_results.json"


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


PURPOSE_BENCHMARKS = {
    "bridge_harmony": {
        "purpose": "bridge_harmony",
        "read": "Relations expected to bridge proportion, boundary, and spatial completion.",
        "expected_relations": {
            "phi->pi": "proportion into circular boundary",
            "phi->tau": "proportion into full-turn boundary",
            "pi->tau": "circle constant into full-turn constant",
            "phi->sqrt5": "golden ratio into its discriminant root",
        },
    },
    "actualizing_growth": {
        "purpose": "actualizing_growth",
        "read": "Relations expected to express growth or actualization.",
        "expected_relations": {
            "one->e": "unit into natural growth",
            "power_P0->e": "Power offset into Euler growth",
            "one->phi": "unit into proportional growth",
        },
    },
    "context_scaling": {
        "purpose": "context_scaling",
        "read": "Relations expected to scale context or dimensional frame.",
        "expected_relations": {
            "one->sqrt2": "unit into diagonal scale",
            "one->sqrt3": "unit into triadic/root scale",
            "one->sqrt5": "unit into golden discriminant scale",
            "pi->tau": "half-turn circle context into full-turn context",
        },
    },
    "binding_gathering": {
        "purpose": "binding_gathering",
        "read": "Relations expected to compress, gather, or return toward unity.",
        "expected_relations": {
            "phi->one": "golden proportion returning to unit",
            "sqrt5->one": "root extension returning to unit",
            "tau->pi": "full turn gathered to half-turn boundary",
            "phi->phi_inverse_L0": "golden proportion compressed into reciprocal",
        },
    },
    "boundary_differentiation": {
        "purpose": "boundary_differentiation",
        "read": "Relations expected to emphasize distinction and boundary.",
        "expected_relations": {
            "one->sqrt2": "unit into first diagonal distinction",
            "one->two": "unit into binary distinction",
            "pi->tau": "circle boundary doubled into full boundary",
            "justice_J0->one": "Justice mode normalized to unit boundary",
        },
    },
    "integrated_relation": {
        "purpose": "integrated_relation",
        "read": "Relations expected to use a balanced operator mix.",
        "expected_relations": {
            "one->phi": "unit into golden integration",
            "phi_inverse_L0->one": "golden reciprocal into unit",
            "sqrt2->e": "root distinction into natural growth",
            "sqrt2->ln2_W0": "root distinction into binary context",
        },
    },
}


OPERATOR_CLOSURE_TESTS = [
    {
        "name": "sqrt2_square_closure",
        "relation": "one->sqrt2",
        "anchor": "sqrt2",
        "expected": "two",
        "purpose": "context_scaling",
        "read": "The diagonal-root relation applied twice closes on 2.",
    },
    {
        "name": "sqrt3_square_closure",
        "relation": "one->sqrt3",
        "anchor": "sqrt3",
        "expected": "three",
        "purpose": "context_scaling",
        "read": "The triadic-root relation applied twice closes on 3.",
    },
    {
        "name": "sqrt5_square_closure",
        "relation": "one->sqrt5",
        "anchor": "sqrt5",
        "expected": "five",
        "purpose": "context_scaling",
        "read": "The golden-discriminant root relation applied twice closes on 5.",
    },
    {
        "name": "golden_reciprocal_repair",
        "relation": "one->phi",
        "anchor": "phi_inverse_L0",
        "expected": "one",
        "purpose": "integrated_relation",
        "read": "The golden growth relation repairs the inverse back to unit.",
    },
    {
        "name": "golden_reciprocal_growth",
        "relation": "phi_inverse_L0->one",
        "anchor": "one",
        "expected": "phi",
        "purpose": "integrated_relation",
        "read": "The inverse-to-unit relation acts as golden growth.",
    },
    {
        "name": "golden_square_closure",
        "relation": "one->phi",
        "anchor": "phi",
        "expected": "phi_squared",
        "purpose": "integrated_relation",
        "read": "The unit-to-golden relation applied to phi closes on phi squared, which is also phi plus one.",
    },
    {
        "name": "unit_doubling_on_circle",
        "relation": "one->two",
        "anchor": "pi",
        "expected": "tau",
        "purpose": "boundary_differentiation",
        "read": "A generic unit-doubling relation transfers onto pi and produces tau.",
    },
    {
        "name": "unit_halving_on_circle",
        "relation": "two->one",
        "anchor": "tau",
        "expected": "pi",
        "purpose": "binding_gathering",
        "read": "A generic unit-halving relation transfers onto tau and returns pi.",
    },
    {
        "name": "circle_full_turn",
        "relation": "pi->tau",
        "anchor": "pi",
        "expected": "tau",
        "purpose": "context_scaling",
        "read": "The circle scaling relation takes pi to tau.",
    },
    {
        "name": "circle_half_turn",
        "relation": "tau->pi",
        "anchor": "tau",
        "expected": "pi",
        "purpose": "binding_gathering",
        "read": "The gathering relation compresses full turn to half turn.",
    },
]


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


def purpose_search_score(relation, purpose):
    return (
        0.76 * relation["purpose_scores"][purpose]
        + 0.14 * relation["fit_quality"]
        + 0.10 * relation["bounded_strength"]
    )


def ranked_for_purpose(relations, purpose):
    rows = []
    for relation in relations:
        rows.append({
            "relation": relation["id"],
            "source": relation["source"],
            "target": relation["target"],
            "ratio": relation["ratio"],
            "direction": relation["direction"],
            "search_score": purpose_search_score(relation, purpose),
            "purpose_score": relation["purpose_scores"][purpose],
            "best_purpose": relation["best_purpose"]["purpose"],
            "fit_quality": relation["fit_quality"],
            "bounded_strength": relation["bounded_strength"],
            "operator_mix": relation["operator_mix"],
        })
    return sorted(rows, key=lambda row: row["search_score"], reverse=True)


def rank_of_relation(ranked, relation_id):
    for index, row in enumerate(ranked, start=1):
        if row["relation"] == relation_id:
            return index, row
    return None, None


def evaluate_purpose_benchmark(relations, benchmark, top_n):
    ranked = ranked_for_purpose(relations, benchmark["purpose"])
    expected_rows = []
    for relation_id, rationale in benchmark["expected_relations"].items():
        rank, row = rank_of_relation(ranked, relation_id)
        expected_rows.append({
            "relation": relation_id,
            "rationale": rationale,
            "rank": rank,
            "percentile": rank / len(ranked) if rank else None,
            "in_top_n": rank <= top_n if rank else False,
            "row": row,
        })
    return {
        "purpose": benchmark["purpose"],
        "read": benchmark["read"],
        "top_n": top_n,
        "top_relations": ranked[:top_n],
        "expected_relations": expected_rows,
        "expected_in_top_n": sum(1 for row in expected_rows if row["in_top_n"]),
        "expected_count": len(expected_rows),
        "median_expected_percentile": statistics.median(
            [row["percentile"] for row in expected_rows if row["percentile"] is not None]
        ),
    }


def evaluate_operator_closure(relations):
    by_id = relation_lookup(relations)
    rows = []
    for test in OPERATOR_CLOSURE_TESTS:
        relation = by_id[test["relation"]]
        predicted = PURPOSE_CONSTANTS[test["anchor"]] * relation["ratio"]
        expected = PURPOSE_CONSTANTS[test["expected"]]
        relative_error = predicted / expected - 1.0
        purpose_ranked = ranked_for_purpose(relations, test["purpose"])
        rank, ranked_row = rank_of_relation(purpose_ranked, test["relation"])
        rows.append({
            "name": test["name"],
            "relation": test["relation"],
            "anchor": test["anchor"],
            "expected": test["expected"],
            "purpose": test["purpose"],
            "read": test["read"],
            "operator_ratio": relation["ratio"],
            "predicted_value": predicted,
            "expected_value": expected,
            "absolute_error": abs(predicted - expected),
            "relative_error": relative_error,
            "absolute_relative_error": abs(relative_error),
            "purpose_rank": rank,
            "purpose_percentile": rank / len(purpose_ranked),
            "purpose_row": ranked_row,
        })
    return rows


def exemplar_score(candidate, exemplars):
    if not exemplars:
        return 0.0
    return statistics.fmean([
        compat.relation_compatibility(candidate, exemplar)["compatibility"]
        for exemplar in exemplars
    ])


def evaluate_exemplar_compatibility(relations, benchmark, top_n):
    by_id = relation_lookup(relations)
    expected_ids = list(benchmark["expected_relations"])
    rows = []

    for withheld_id in expected_ids:
        exemplars = [
            by_id[relation_id]
            for relation_id in expected_ids
            if relation_id != withheld_id and relation_id in by_id
        ]
        ranked = []
        for relation in relations:
            if relation["id"] in {example["id"] for example in exemplars}:
                continue
            ranked.append({
                "relation": relation["id"],
                "source": relation["source"],
                "target": relation["target"],
                "score": exemplar_score(relation, exemplars),
                "best_purpose": relation["best_purpose"]["purpose"],
                "operator_mix": relation["operator_mix"],
                "ratio": relation["ratio"],
                "direction": relation["direction"],
            })
        ranked.sort(key=lambda row: row["score"], reverse=True)
        rank, row = rank_of_relation(ranked, withheld_id)
        rows.append({
            "withheld_relation": withheld_id,
            "rationale": benchmark["expected_relations"][withheld_id],
            "rank": rank,
            "percentile": rank / len(ranked) if rank else None,
            "in_top_n": rank <= top_n if rank else False,
            "row": row,
            "top_relations": ranked[:top_n],
        })

    return {
        "purpose": benchmark["purpose"],
        "read": benchmark["read"],
        "top_n": top_n,
        "withheld_results": rows,
        "withheld_in_top_n": sum(1 for row in rows if row["in_top_n"]),
        "withheld_count": len(rows),
        "median_withheld_percentile": statistics.median([
            row["percentile"] for row in rows if row["percentile"] is not None
        ]),
    }


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


def build_report(args):
    fit_func, fit_engine, c_path = configure_fit(args)
    relations = build_relations(fit_func)
    purpose_results = {
        name: evaluate_purpose_benchmark(relations, benchmark, args.top_n)
        for name, benchmark in PURPOSE_BENCHMARKS.items()
    }
    exemplar_results = {
        name: evaluate_exemplar_compatibility(relations, benchmark, args.top_n)
        for name, benchmark in PURPOSE_BENCHMARKS.items()
    }
    closure_rows = evaluate_operator_closure(relations)

    return {
        "experiment_name": "pakheta_purpose_relation_search",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "fit_engine_requested": args.fit_engine,
            "fit_engine_used": fit_engine,
            "c_fit_library_path": str(c_path) if c_path else None,
            "max_coordinate": args.max_coordinate,
            "constant_count": len(PURPOSE_CONSTANTS),
            "relation_count": len(relations),
            "top_n": args.top_n,
        },
        "method": {
            "purpose_first_search": (
                "Rank constant-pair relations by how strongly they serve a "
                "declared purpose archetype, with support from fit quality and "
                "bounded relation strength."
            ),
            "operator_closure": (
                "Use a retrieved relation as a multiplicative operator on a "
                "known anchor and check whether it produces a known target."
            ),
        },
        "purpose_benchmarks": purpose_results,
        "exemplar_compatibility_benchmarks": exemplar_results,
        "operator_closure_tests": closure_rows,
        "summary": {
            "purpose_expected_in_top_n": {
                name: {
                    "expected_in_top_n": result["expected_in_top_n"],
                    "expected_count": result["expected_count"],
                    "median_expected_percentile": result["median_expected_percentile"],
                }
                for name, result in purpose_results.items()
            },
            "exemplar_withheld_in_top_n": {
                name: {
                    "withheld_in_top_n": result["withheld_in_top_n"],
                    "withheld_count": result["withheld_count"],
                    "median_withheld_percentile": result["median_withheld_percentile"],
                }
                for name, result in exemplar_results.items()
            },
            "operator_closure_absolute_relative_error": summarize([
                row["absolute_relative_error"]
                for row in closure_rows
            ]),
            "operator_closure_median_purpose_percentile": statistics.median([
                row["purpose_percentile"]
                for row in closure_rows
            ]),
        },
        "interpretation": {
            "short_read": (
                "Known constants can be searched by relation-purpose rather "
                "than object similarity. Some familiar relations act as exact "
                "operators, such as one->sqrt2 closing sqrt2 on two."
            ),
            "boundary": (
                "This is still a small purpose grammar. A relation ranking is "
                "not evidence by itself; closure and withheld retrieval tests "
                "are the stronger checks."
            ),
        },
    }


def write_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report):
    print()
    print("Pakheta Purpose-First Relation Search")
    print("=" * 39)
    print("Fit engine:", report["configuration"]["fit_engine_used"])
    print("Constants:", report["configuration"]["constant_count"])
    print("Relations:", report["configuration"]["relation_count"])
    print()
    print("Purpose retrieval:")
    for purpose, result in report["purpose_benchmarks"].items():
        print(
            f"  {purpose:<26} "
            f"{result['expected_in_top_n']}/{result['expected_count']} "
            f"expected in top {result['top_n']} "
            f"median_pct={result['median_expected_percentile']:.3f}"
        )
    print()
    print("Exemplar leave-one-out retrieval:")
    for purpose, result in report["exemplar_compatibility_benchmarks"].items():
        print(
            f"  {purpose:<26} "
            f"{result['withheld_in_top_n']}/{result['withheld_count']} "
            f"withheld in top {result['top_n']} "
            f"median_pct={result['median_withheld_percentile']:.3f}"
        )
    print()
    print("Operator closure:")
    for row in report["operator_closure_tests"]:
        print(
            f"  {row['name']:<28} "
            f"rel={row['relation']:<18} "
            f"{row['anchor']} -> {row['expected']} "
            f"rel_err={row['relative_error']:.3e} "
            f"purpose_pct={row['purpose_percentile']:.3f}"
        )
    print()
    print(f"Results saved to: {OUTPUT_FILE.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Purpose-first relation search over familiar constants."
    )
    parser.add_argument("--max-coordinate", type=int, default=10)
    parser.add_argument(
        "--fit-engine",
        choices=["auto", "c", "python"],
        default="auto",
    )
    parser.add_argument("--top-n", type=int, default=20)
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)
    write_report(report)
    print_summary(report)


if __name__ == "__main__":
    main()
