"""
Pakheta Relational Lucas-Lehmer Lab.

This experiment reverse-engineers the relational structure inside the
Lucas-Lehmer test.  It does not claim to replace LL.  It asks a sharper
question:

Can the LL recurrence be represented as an exact relational residue calculus,
then projected into LJPW-style features without losing the proof boundary?

The exact residue layer is the Mersenne cycle:
    E_i = 2^i mod (2^p - 1)
    E_i * E_j = E_{(i+j) mod p}

That basis product rule is homomorphic.  The difficult part is canonical
carry repair: cyclic convolution produces integer coefficients on the cycle,
while the canonical residue is a p-bit field after carries and subtraction.
"""

import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = EXPERIMENT_DIR / "relational_ll_lab_results.json"

BASE = 30.0
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)
LJPW = {
    "Love": L0,
    "Justice": J0,
    "Power": P0,
    "Wisdom": W0,
}

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


def decimal_digits_of_mersenne(exponent):
    return int(math.floor(exponent * math.log10(2.0))) + 1


def binary_entropy(probability):
    if probability <= 0.0 or probability >= 1.0:
        return 0.0
    return (
        -probability * math.log2(probability)
        - (1.0 - probability) * math.log2(1.0 - probability)
    )


def bit_positions(value, width):
    return [index for index in range(width) if (value >> index) & 1]


def longest_cyclic_run(bits, target):
    if not bits:
        return 0
    doubled = bits + bits
    best = 0
    current = 0
    for bit in doubled:
        if bit == target:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return min(best, len(bits))


def cyclic_transition_count(bits):
    if not bits:
        return 0
    return sum(
        1 for index, bit in enumerate(bits)
        if bit != bits[(index + 1) % len(bits)]
    )


def ljpw_resonances(positions, width):
    if not positions:
        return {name: 0.0 for name in LJPW}

    rows = {}
    for name, constant in LJPW.items():
        real = 0.0
        imag = 0.0
        for position in positions:
            angle = 2.0 * math.pi * constant * position
            real += math.cos(angle)
            imag += math.sin(angle)
        rows[name] = math.hypot(real, imag) / len(positions)
    return rows


def residue_features(value, exponent, include_carry_pressure=False):
    positions = bit_positions(value, exponent)
    position_set = set(positions)
    popcount = len(positions)
    density = popcount / exponent
    bits = [1 if index in position_set else 0 for index in range(exponent)]
    transitions = cyclic_transition_count(bits)
    resonances = ljpw_resonances(positions, exponent)
    resonance_values = list(resonances.values())

    features = {
        "value_is_zero": value == 0,
        "popcount": popcount,
        "density": density,
        "binary_entropy": binary_entropy(density),
        "cyclic_transition_rate": transitions / exponent,
        "longest_one_run_fraction": longest_cyclic_run(bits, 1) / exponent,
        "longest_zero_run_fraction": longest_cyclic_run(bits, 0) / exponent,
        "balance": 1.0 - abs((2.0 * density) - 1.0),
        "ljpw_resonance": resonances,
        "ljpw_resonance_mean": (
            statistics.fmean(resonance_values) if resonance_values else 0.0
        ),
        "ljpw_resonance_spread": (
            statistics.pstdev(resonance_values) if len(resonance_values) > 1 else 0.0
        ),
    }

    if include_carry_pressure:
        features["formal_square"] = formal_square_features(positions, exponent)

    return features


def formal_square_counts(positions, exponent):
    counts = [0] * exponent
    for left in positions:
        for right in positions:
            counts[(left + right) % exponent] += 1
    return counts


def normalized_entropy(counts):
    total = sum(counts)
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts:
        if count == 0:
            continue
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy / math.log2(len(counts)) if len(counts) > 1 else 0.0


def formal_square_features(positions, exponent):
    counts = formal_square_counts(positions, exponent)
    total_pairs = len(positions) * len(positions)
    if total_pairs == 0:
        return {
            "total_pairs": 0,
            "occupied_cycle_sites": 0,
            "max_bucket": 0,
            "carry_pressure": 0.0,
            "coefficient_entropy": 0.0,
        }

    occupied = sum(1 for count in counts if count)
    carry_mass = sum(max(0, count - 1) for count in counts)
    return {
        "total_pairs": total_pairs,
        "occupied_cycle_sites": occupied,
        "max_bucket": max(counts),
        "carry_pressure": carry_mass / total_pairs,
        "coefficient_entropy": normalized_entropy(counts),
    }


def sample_steps(iterations):
    if iterations <= 0:
        return [0]
    candidates = {
        0,
        1,
        2,
        iterations // 4,
        iterations // 2,
        (3 * iterations) // 4,
        iterations,
    }
    return sorted(step for step in candidates if 0 <= step <= iterations)


def summarize_values(values):
    if not values:
        return None
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "max": max(values),
    }


def summarize_feature_rows(rows):
    metrics = [
        "density",
        "binary_entropy",
        "cyclic_transition_rate",
        "balance",
        "ljpw_resonance_mean",
        "ljpw_resonance_spread",
    ]
    return {
        metric: summarize_values([row[metric] for row in rows])
        for metric in metrics
    }


def run_lucas_lehmer_trajectory(exponent, include_carry_pressure):
    if exponent == 2:
        return {
            "exponent": exponent,
            "mersenne_digits": decimal_digits_of_mersenne(exponent),
            "iterations": 0,
            "is_mersenne_prime": True,
            "known_mersenne_prime_exponent": exponent in KNOWN_MERSENNE_PRIME_EXPONENTS,
            "final_residue": 0,
            "sample_features": [
                {
                    "step": 0,
                    "fraction": 1.0,
                    "features": residue_features(0, exponent, include_carry_pressure),
                }
            ],
            "trajectory_summary": {},
        }

    modulus = (1 << exponent) - 1
    iterations = exponent - 2
    samples = set(sample_steps(iterations))
    state = 4 % modulus
    all_feature_rows = []
    sample_feature_rows = []

    for step in range(0, iterations + 1):
        features = residue_features(
            state,
            exponent,
            include_carry_pressure=include_carry_pressure and step in samples,
        )
        if step < iterations:
            all_feature_rows.append(features)
        if step in samples:
            sample_feature_rows.append({
                "step": step,
                "fraction": step / iterations if iterations else 1.0,
                "features": features,
            })
        if step < iterations:
            state = ((state * state) - 2) % modulus

    return {
        "exponent": exponent,
        "mersenne_digits": decimal_digits_of_mersenne(exponent),
        "iterations": iterations,
        "is_mersenne_prime": state == 0,
        "known_mersenne_prime_exponent": exponent in KNOWN_MERSENNE_PRIME_EXPONENTS,
        "final_residue_low64": state & ((1 << 64) - 1),
        "final_popcount": state.bit_count(),
        "sample_features": sample_feature_rows,
        "trajectory_summary": summarize_feature_rows(all_feature_rows),
    }


def evaluate_cyclic_convolution(positions, exponent):
    modulus = (1 << exponent) - 1
    residue = sum(1 << position for position in positions) % modulus
    counts = formal_square_counts(positions, exponent)
    formal_value = sum(count * (1 << index) for index, count in enumerate(counts))
    return (formal_value % modulus) == ((residue * residue) % modulus)


def homomorphism_probe():
    probes = [
        (11, [0, 2, 5]),
        (13, [1, 4, 9, 10]),
        (31, [0, 3, 7, 14, 25]),
    ]
    basis_pass = True
    convolution_pass = True

    for exponent, positions in probes:
        modulus = (1 << exponent) - 1
        for left in range(exponent):
            for right in range(exponent):
                product = ((1 << left) * (1 << right)) % modulus
                expected = 1 << ((left + right) % exponent)
                if product != expected:
                    basis_pass = False
        if not evaluate_cyclic_convolution(positions, exponent):
            convolution_pass = False

    return {
        "exact_basis_product_rule": "E_i * E_j = E_(i+j mod p)",
        "basis_product_rule_passed": basis_pass,
        "cyclic_convolution_square_passed": convolution_pass,
        "interpretation": (
            "The coefficient cycle is a real exact homomorphic layer. "
            "The hard part is not cyclic multiplication; it is canonical "
            "carry repair plus the localized '-2' perturbation while retaining "
            "enough state to prove final zero."
        ),
    }


def group_rows_by_result(rows):
    prime_rows = [row for row in rows if row["is_mersenne_prime"]]
    composite_rows = [row for row in rows if not row["is_mersenne_prime"]]
    return prime_rows, composite_rows


def feature_metric(features, metric):
    current = features
    for part in metric.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def metric_at_fraction(row, target_fraction, metric):
    samples = row["sample_features"]
    nearest = min(
        samples,
        key=lambda sample: abs(sample["fraction"] - target_fraction),
    )
    return feature_metric(nearest["features"], metric)


def compare_groups(rows, min_exponent=2):
    filtered_rows = [row for row in rows if row["exponent"] >= min_exponent]
    prime_rows, composite_rows = group_rows_by_result(filtered_rows)
    comparisons = {}
    metrics = [
        "density",
        "binary_entropy",
        "cyclic_transition_rate",
        "balance",
        "ljpw_resonance_mean",
        "ljpw_resonance_spread",
        "formal_square.carry_pressure",
        "formal_square.coefficient_entropy",
    ]
    for fraction_name, fraction in [
        ("quarter", 0.25),
        ("half", 0.50),
        ("three_quarter", 0.75),
    ]:
        comparisons[fraction_name] = {}
        for metric in metrics:
            prime_values = [
                metric_at_fraction(row, fraction, metric)
                for row in prime_rows
                if row["iterations"] > 0
            ]
            prime_values = [value for value in prime_values if value is not None]
            composite_values = [
                metric_at_fraction(row, fraction, metric)
                for row in composite_rows
                if row["iterations"] > 0
            ]
            composite_values = [value for value in composite_values if value is not None]
            comparisons[fraction_name][metric] = {
                "mersenne_prime_summary": summarize_values(prime_values),
                "composite_summary": summarize_values(composite_values),
                "mean_delta_prime_minus_composite": (
                    statistics.fmean(prime_values) - statistics.fmean(composite_values)
                    if prime_values and composite_values
                    else None
                ),
            }
    return comparisons


def build_report(args):
    exponents = prime_exponents_up_to(args.max_exponent)
    rows = [
        run_lucas_lehmer_trajectory(
            exponent,
            include_carry_pressure=args.include_carry_pressure,
        )
        for exponent in exponents
    ]
    prime_rows, composite_rows = group_rows_by_result(rows)

    report = {
        "experiment_name": "pakheta_relational_lucas_lehmer_lab",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "max_exponent": args.max_exponent,
            "prime_exponent_count": len(exponents),
            "include_carry_pressure": args.include_carry_pressure,
        },
        "relational_transposition": {
            "Pakheta_Node": "A bit position E_i = 2^i on the p-cycle.",
            "Pakheta_Anchor": "The prime exponent p and modulus M_p = 2^p - 1.",
            "Pakheta_Context": "The current LL recurrence step.",
            "Pakheta_Actualization": "Canonical residue after cyclic fold, carry repair, and subtraction by 2.",
            "Pakheta_Coherence": "Final zero residue after p-2 updates.",
            "Pakheta_Decoherence": "Carry pressure, boundary density, and residue spread before repair.",
            "Love": "Cyclic gathering: high powers fold back into the same relational field.",
            "Justice": "Carry repair and exact boundary normalization.",
            "Power": "Squaring actualizes the next residue state.",
            "Wisdom": "Exponent/candidate selection and trajectory interpretation.",
        },
        "candidate_exact_calculus": {
            "cycle_basis": "E_i = 2^i mod (2^p - 1)",
            "multiplication": "E_i * E_j = E_(i+j mod p)",
            "general_square": "A residue square is cyclic convolution over the p-cycle.",
            "repair_relation": "Canonical bits require carry repair using 2E_i = E_(i+1) and E_p = E_0.",
            "zero_relation": "The all-ones p-bit field is congruent to zero modulo 2^p - 1.",
            "fit_read": (
                "This is an exact relational residue calculus candidate. "
                "It is homomorphic before canonical carry repair; the research "
                "problem is whether carry repair can be compressed without "
                "losing exact zero detection."
            ),
        },
        "homomorphism_probe": homomorphism_probe(),
        "summary": {
            "tested_prime_exponents": len(rows),
            "mersenne_prime_rows": len(prime_rows),
            "composite_mersenne_rows": len(composite_rows),
            "mersenne_prime_exponents_found": [
                row["exponent"] for row in prime_rows
            ],
        },
        "group_comparisons": compare_groups(rows),
        "filtered_group_comparisons_min_exponent_31": compare_groups(
            rows,
            min_exponent=31,
        ),
        "trajectory_rows": rows,
        "interpretation": {
            "short_read": (
                "The Mersenne cycle supplies a genuine exact relational layer: "
                "basis products are cyclic and homomorphic. The current LJPW "
                "log-coordinate layer can describe residue patterns, but it "
                "does not by itself preserve enough information to replace LL."
            ),
            "next_research_move": (
                "Freeze the exact cyclic coefficient calculus, then test "
                "whether carry-repair features predict final zero earlier than "
                "the LL endpoint across larger known exponent sets."
            ),
        },
    }
    return report


def write_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def print_summary(report):
    summary = report["summary"]
    hom = report["homomorphism_probe"]
    print()
    print("Pakheta Relational Lucas-Lehmer Lab")
    print("=" * 39)
    print("Prime exponents tested:", summary["tested_prime_exponents"])
    print("Mersenne-prime rows:", summary["mersenne_prime_rows"])
    print("Composite rows:", summary["composite_mersenne_rows"])
    print("Basis product homomorphism:", hom["basis_product_rule_passed"])
    print("Cyclic convolution square:", hom["cyclic_convolution_square_passed"])
    print("Mersenne exponents found:", summary["mersenne_prime_exponents_found"])
    print()
    half = report["group_comparisons"]["half"]
    for metric in [
        "density",
        "cyclic_transition_rate",
        "ljpw_resonance_mean",
    ]:
        delta = half[metric]["mean_delta_prime_minus_composite"]
        print(f"Half-trajectory {metric} delta:", f"{delta:.6f}")
    carry_delta = half["formal_square.carry_pressure"]["mean_delta_prime_minus_composite"]
    filtered_carry_delta = report[
        "filtered_group_comparisons_min_exponent_31"
    ]["half"]["formal_square.carry_pressure"]["mean_delta_prime_minus_composite"]
    print("Half-trajectory carry_pressure delta:", f"{carry_delta:.6f}")
    print("Half-trajectory carry_pressure delta p>=31:", f"{filtered_carry_delta:.6f}")
    print()
    print(f"Results saved to: {OUTPUT_FILE.name}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reverse-engineer relational structure in LL trajectories."
    )
    parser.add_argument("--max-exponent", type=int, default=521)
    parser.add_argument(
        "--include-carry-pressure",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_report(args)
    write_report(report)
    print_summary(report)


if __name__ == "__main__":
    main()
