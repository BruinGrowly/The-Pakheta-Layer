"""
C-backed Pakheta Relational LL pseudo-test lab.

This moves the expensive relational Lucas-Lehmer trajectory analysis into C.
Python only orchestrates the sweep and summarizes the returned samples.

The pseudo-test is deliberately not a proof.  It studies whether early/mid
trajectory features such as carry pressure, cyclic transition rate, and LJPW
resonance separate known Mersenne-prime exponents from composite Mersenne
exponents before the final Lucas-Lehmer zero check.
"""

import argparse
import ctypes
import json
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
DLL_PATH = EXPERIMENT_DIR / "relational_calculator.dll"
OUTPUT_FILE = EXPERIMENT_DIR / "relational_ll_c_pseudo_results.json"
LL_PSEUDO_SAMPLE_COUNT = 7

KNOWN_MERSENNE_PRIME_EXPONENTS = {
    2,
    3,
    5,
    7,
    13,
    17,
    19,
    31,
    61,
    89,
    107,
    127,
    521,
    607,
    1279,
    2203,
    2281,
    3217,
    4253,
    4423,
}

STATUS_LABELS = {
    0: "ok",
    1: "invalid_exponent",
    2: "exponent_exceeds_schoolbook_limit",
    3: "exponent_not_prime",
    4: "allocation_failed",
}


class RelationalNumber(ctypes.Structure):
    _fields_ = [
        ("c_L", ctypes.c_int16),
        ("c_J", ctypes.c_int16),
        ("c_P", ctypes.c_int16),
        ("c_W", ctypes.c_int16),
    ]


class RelationalFit(ctypes.Structure):
    _fields_ = [
        ("coord", RelationalNumber),
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


class RelationalLLSample(ctypes.Structure):
    _fields_ = [
        ("step", ctypes.c_uint32),
        ("fraction", ctypes.c_double),
        ("popcount", ctypes.c_uint32),
        ("density", ctypes.c_double),
        ("binary_entropy", ctypes.c_double),
        ("cyclic_transition_rate", ctypes.c_double),
        ("longest_one_run_fraction", ctypes.c_double),
        ("longest_zero_run_fraction", ctypes.c_double),
        ("balance", ctypes.c_double),
        ("love_resonance", ctypes.c_double),
        ("justice_resonance", ctypes.c_double),
        ("power_resonance", ctypes.c_double),
        ("wisdom_resonance", ctypes.c_double),
        ("ljpw_resonance_mean", ctypes.c_double),
        ("ljpw_resonance_spread", ctypes.c_double),
        ("carry_pressure", ctypes.c_double),
        ("coefficient_entropy", ctypes.c_double),
        ("occupied_cycle_sites", ctypes.c_uint32),
        ("max_bucket", ctypes.c_uint32),
        ("pseudo_likeness", ctypes.c_double),
    ]


class RelationalLLPseudoResult(ctypes.Structure):
    _fields_ = [
        ("exponent", ctypes.c_uint32),
        ("status", ctypes.c_int32),
        ("is_mersenne_prime", ctypes.c_int32),
        ("iterations", ctypes.c_uint32),
        ("word_count", ctypes.c_uint32),
        ("final_low64", ctypes.c_uint64),
        ("final_popcount", ctypes.c_uint32),
        ("exponent_fit", RelationalFit),
        ("sample_count", ctypes.c_uint32),
        ("samples", RelationalLLSample * LL_PSEUDO_SAMPLE_COUNT),
    ]


def load_library():
    lib = ctypes.CDLL(str(DLL_PATH))
    lib.batch_relational_ll_pseudo_probe.argtypes = [
        ctypes.POINTER(RelationalLLPseudoResult),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint32,
    ]
    lib.batch_relational_ll_pseudo_probe.restype = None
    return lib


def is_prime(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def prime_exponents_up_to(limit):
    return [n for n in range(2, limit + 1) if is_prime(n)]


def fit_to_dict(fit):
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
        "reconstructed_exponent": fit.reconstructed_value,
        "relative_exponent_error": fit.relative_value_error,
    }


def sample_to_dict(sample):
    return {
        "step": sample.step,
        "fraction": sample.fraction,
        "popcount": sample.popcount,
        "density": sample.density,
        "binary_entropy": sample.binary_entropy,
        "cyclic_transition_rate": sample.cyclic_transition_rate,
        "longest_one_run_fraction": sample.longest_one_run_fraction,
        "longest_zero_run_fraction": sample.longest_zero_run_fraction,
        "balance": sample.balance,
        "ljpw_resonance": {
            "Love": sample.love_resonance,
            "Justice": sample.justice_resonance,
            "Power": sample.power_resonance,
            "Wisdom": sample.wisdom_resonance,
        },
        "ljpw_resonance_mean": sample.ljpw_resonance_mean,
        "ljpw_resonance_spread": sample.ljpw_resonance_spread,
        "carry_pressure": sample.carry_pressure,
        "coefficient_entropy": sample.coefficient_entropy,
        "occupied_cycle_sites": sample.occupied_cycle_sites,
        "max_bucket": sample.max_bucket,
        "pseudo_likeness": sample.pseudo_likeness,
        "repair_headroom": 1.0 - sample.carry_pressure,
    }


def result_to_dict(result):
    samples = [
        sample_to_dict(result.samples[index])
        for index in range(result.sample_count)
    ]
    return {
        "exponent": result.exponent,
        "status": result.status,
        "status_label": STATUS_LABELS.get(result.status, "unknown_status"),
        "is_mersenne_prime": bool(result.is_mersenne_prime) if result.status == 0 else None,
        "known_mersenne_prime_exponent": result.exponent in KNOWN_MERSENNE_PRIME_EXPONENTS,
        "iterations": result.iterations,
        "word_count": result.word_count,
        "final_low64": result.final_low64,
        "final_popcount": result.final_popcount,
        "relational_exponent_fit": fit_to_dict(result.exponent_fit),
        "samples": samples,
    }


def run_batch(lib, exponents, fit_max_coordinate, max_bits):
    ArrayType = ctypes.c_uint32 * len(exponents)
    ResultArrayType = RelationalLLPseudoResult * len(exponents)
    exponent_array = ArrayType(*exponents)
    result_array = ResultArrayType()

    start = time.perf_counter()
    lib.batch_relational_ll_pseudo_probe(
        result_array,
        exponent_array,
        len(exponents),
        fit_max_coordinate,
        max_bits,
    )
    duration = time.perf_counter() - start
    return [result_to_dict(result) for result in result_array], duration


def nearest_sample(row, target_fraction):
    return min(
        row["samples"],
        key=lambda sample: abs(sample["fraction"] - target_fraction),
    )


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


def auc_score(prime_values, composite_values, higher_is_prime_like=True):
    if not prime_values or not composite_values:
        return None
    wins = 0.0
    total = len(prime_values) * len(composite_values)
    for prime_value in prime_values:
        for composite_value in composite_values:
            left = prime_value
            right = composite_value
            if not higher_is_prime_like:
                left = -left
                right = -right
            if left > right:
                wins += 1.0
            elif left == right:
                wins += 0.5
    return wins / total


def compare_groups(rows, min_exponent=2):
    completed = [
        row for row in rows
        if row["status"] == 0 and row["exponent"] >= min_exponent
    ]
    prime_rows = [row for row in completed if row["is_mersenne_prime"]]
    composite_rows = [row for row in completed if not row["is_mersenne_prime"]]

    metrics = {
        "carry_pressure": False,
        "repair_headroom": True,
        "coefficient_entropy": True,
        "density": False,
        "cyclic_transition_rate": False,
        "ljpw_resonance_mean": True,
        "ljpw_resonance_spread": True,
        "pseudo_likeness": True,
    }
    fractions = {
        "early": 0.05,
        "quarter": 0.25,
        "half": 0.50,
        "three_quarter": 0.75,
    }

    output = {}
    for fraction_name, fraction in fractions.items():
        output[fraction_name] = {}
        for metric, higher_is_prime_like in metrics.items():
            prime_values = [
                nearest_sample(row, fraction)[metric]
                for row in prime_rows
            ]
            composite_values = [
                nearest_sample(row, fraction)[metric]
                for row in composite_rows
            ]
            output[fraction_name][metric] = {
                "mersenne_prime_summary": summarize(prime_values),
                "composite_summary": summarize(composite_values),
                "mean_delta_prime_minus_composite": (
                    statistics.fmean(prime_values) - statistics.fmean(composite_values)
                    if prime_values and composite_values
                    else None
                ),
                "auc_prime_like": auc_score(
                    prime_values,
                    composite_values,
                    higher_is_prime_like=higher_is_prime_like,
                ),
                "higher_is_prime_like": higher_is_prime_like,
            }
    return output


def top_auc_features(group_comparison):
    rows = []
    for fraction_name, metrics in group_comparison.items():
        for metric, data in metrics.items():
            auc = data["auc_prime_like"]
            if auc is None:
                continue
            rows.append({
                "fraction": fraction_name,
                "metric": metric,
                "auc_prime_like": auc,
                "mean_delta_prime_minus_composite": data[
                    "mean_delta_prime_minus_composite"
                ],
                "higher_is_prime_like": data["higher_is_prime_like"],
            })
    return sorted(rows, key=lambda row: row["auc_prime_like"], reverse=True)


def build_report(args):
    lib = load_library()
    exponents = prime_exponents_up_to(args.max_exponent)
    rows, duration = run_batch(
        lib,
        exponents,
        args.fit_max_coordinate,
        args.max_bits,
    )
    completed = [row for row in rows if row["status"] == 0]
    expected_rows = [
        row for row in completed
        if row["exponent"] <= max(KNOWN_MERSENNE_PRIME_EXPONENTS)
    ]
    expected_matches = [
        row for row in expected_rows
        if row["is_mersenne_prime"] == row["known_mersenne_prime_exponent"]
    ]
    comparisons = compare_groups(rows)
    filtered_comparisons = compare_groups(rows, min_exponent=31)

    return {
        "experiment_name": "pakheta_relational_ll_c_pseudo",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "dll_path": str(DLL_PATH),
            "max_exponent": args.max_exponent,
            "max_bits": args.max_bits,
            "fit_max_coordinate": args.fit_max_coordinate,
            "prime_exponent_count": len(exponents),
            "sample_count": LL_PSEUDO_SAMPLE_COUNT,
        },
        "method": {
            "c_substrate": (
                "The DLL runs the LL recurrence, cyclic residue features, "
                "formal-square carry pressure, coefficient entropy, and LJPW "
                "resonance sampling in C."
            ),
            "pseudo_test_read": (
                "These features are candidate filters/classifiers. They do "
                "not replace final zero-residue proof."
            ),
        },
        "summary": {
            "duration_sec": duration,
            "completed_rows": len(completed),
            "expected_rows": len(expected_rows),
            "expected_matches": len(expected_matches),
            "all_expected_matched": (
                len(expected_rows) == len(expected_matches)
                if expected_rows
                else None
            ),
            "mersenne_prime_exponents_found": [
                row["exponent"] for row in completed
                if row["is_mersenne_prime"]
            ],
        },
        "group_comparisons": comparisons,
        "filtered_group_comparisons_min_exponent_31": filtered_comparisons,
        "top_auc_features": top_auc_features(comparisons)[:20],
        "top_auc_features_min_exponent_31": top_auc_features(filtered_comparisons)[:20],
        "rows": rows,
        "interpretation": {
            "short_read": (
                "C makes the pseudo-LL trajectory study cheap enough to run "
                "as a real sweep. The useful signal is measured by AUC and "
                "mean deltas against exact LL outcomes."
            ),
            "boundary": (
                "A strong pseudo feature would still be a candidate-routing "
                "tool, not a primality proof, unless the relational residue "
                "calculus preserves exact final zero detection."
            ),
        },
    }


def write_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report):
    summary = report["summary"]
    print()
    print("Pakheta C Relational LL Pseudo Lab")
    print("=" * 39)
    print("Completed rows:", summary["completed_rows"])
    print("Expected matches:", f"{summary['expected_matches']}/{summary['expected_rows']}")
    print("Duration sec:", f"{summary['duration_sec']:.3f}")
    print("Mersenne exponents found:", summary["mersenne_prime_exponents_found"])
    print()
    print("Top pseudo features:")
    for row in report["top_auc_features"][:8]:
        print(
            f"  {row['fraction']} {row['metric']} "
            f"AUC={row['auc_prime_like']:.3f} "
            f"delta={row['mean_delta_prime_minus_composite']:.6f}"
        )
    print()
    print("Top pseudo features, p>=31:")
    for row in report["top_auc_features_min_exponent_31"][:8]:
        print(
            f"  {row['fraction']} {row['metric']} "
            f"AUC={row['auc_prime_like']:.3f} "
            f"delta={row['mean_delta_prime_minus_composite']:.6f}"
        )
    print()
    print(f"Results saved to: {OUTPUT_FILE.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run C-backed relational pseudo-LL feature sweeps."
    )
    parser.add_argument("--max-exponent", type=int, default=1279)
    parser.add_argument("--max-bits", type=int, default=1500)
    parser.add_argument("--fit-max-coordinate", type=int, default=28)
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)
    write_report(report)
    print_summary(report)


if __name__ == "__main__":
    main()
