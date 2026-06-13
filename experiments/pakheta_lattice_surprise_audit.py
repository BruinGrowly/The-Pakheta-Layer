"""
Prime-LJPW lattice surprise audit.

This test asks a focused question:

    When the same lattice search is applied to random targets in comparable
    numeric ranges, how often do random numbers fit as well as the physical
    targets?

The goal is not to weaken the bridge research. It is to separate ordinary
lattice density from genuinely unusual coordinate hits.
"""

import bisect
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path


L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)
BASE = 30.0

RNG_SEED = 613


TARGET_GROUPS = {
    "cosmological_constant": {
        "max_c": 50,
        "null_range": {"low": 1.0e-130, "high": 1.0e-110, "distribution": "log_uniform"},
        "null_samples": 2000,
        "targets": {
            "lambda_planck_units": 1.38e-122,
        },
    },
    "heavy_boson_ratios": {
        "max_c": 10,
        "null_range": {"low": 50.0, "high": 150.0, "distribution": "log_uniform"},
        "null_samples": 5000,
        "targets": {
            "higgs_to_proton_mass_ratio": 125100.0 / 938.27208943,
            "w_to_proton_mass_ratio": 80377.0 / 938.27208943,
            "z_to_proton_mass_ratio": 91187.6 / 938.27208943,
        },
    },
    "cosmic_energy_ratios": {
        "max_c": 10,
        "null_range": {"low": 0.1, "high": 10.0, "distribution": "log_uniform"},
        "null_samples": 5000,
        "targets": {
            "dark_energy_to_total_matter": 0.683 / 0.317,
            "dark_matter_to_baryon": 0.268 / 0.049,
        },
    },
    "hubble_tension_ratio": {
        "max_c": 5,
        "null_range": {"low": 1.0, "high": 1.2, "distribution": "uniform"},
        "null_samples": 5000,
        "targets": {
            "late_to_early_H0": 73.0 / 67.4,
        },
    },
    "pmns_neutrino_angles": {
        "max_c": 10,
        "null_range": {"low": 0.05, "high": 1.0, "distribution": "log_uniform"},
        "null_samples": 5000,
        "targets": {
            "theta12_radians": math.radians(33.82),
            "theta23_radians": math.radians(48.3),
            "theta13_radians": math.radians(8.61),
        },
    },
}


def percentile(sorted_values, q):
    if not sorted_values:
        return None
    if q <= 0:
        return sorted_values[0]
    if q >= 1:
        return sorted_values[-1]
    position = q * (len(sorted_values) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return sorted_values[low]
    weight = position - low
    return sorted_values[low] * (1.0 - weight) + sorted_values[high] * weight


def sample_target(rng, range_spec):
    low = range_spec["low"]
    high = range_spec["high"]
    if range_spec["distribution"] == "log_uniform":
        return math.exp(math.log(low) + rng.random() * (math.log(high) - math.log(low)))
    if range_spec["distribution"] == "uniform":
        return low + rng.random() * (high - low)
    raise ValueError(f"Unsupported null distribution: {range_spec['distribution']}")


def build_pair_index(max_c):
    left_pairs = []
    right_pairs = []
    for c_l in range(-max_c, max_c + 1):
        for c_j in range(-max_c, max_c + 1):
            left_pairs.append((c_l * L0 + c_j * J0, c_l, c_j))
    for c_p in range(-max_c, max_c + 1):
        for c_w in range(-max_c, max_c + 1):
            right_pairs.append((c_p * P0 + c_w * W0, c_p, c_w))
    right_pairs.sort(key=lambda row: row[0])
    right_values = [row[0] for row in right_pairs]
    return left_pairs, right_pairs, right_values


def search_lattice(target, index):
    left_pairs, right_pairs, right_values = index
    target_exponent = math.log(target) / math.log(BASE)
    best = {
        "absolute_relative_error": float("inf"),
        "relative_error": None,
        "calculated_value": None,
        "calculated_exponent": None,
        "coefficients": None,
    }

    for left_value, c_l, c_j in left_pairs:
        need = target_exponent - left_value
        insertion = bisect.bisect_left(right_values, need)
        for right_index in (insertion - 1, insertion, insertion + 1):
            if 0 <= right_index < len(right_pairs):
                right_value, c_p, c_w = right_pairs[right_index]
                exponent = left_value + right_value
                calculated = BASE ** exponent
                relative_error = calculated / target - 1.0
                absolute_relative_error = abs(relative_error)
                if absolute_relative_error < best["absolute_relative_error"]:
                    best = {
                        "absolute_relative_error": absolute_relative_error,
                        "relative_error": relative_error,
                        "calculated_value": calculated,
                        "calculated_exponent": exponent,
                        "coefficients": {
                            "c_L": c_l,
                            "c_J": c_j,
                            "c_P": c_p,
                            "c_W": c_w,
                        },
                    }
    return best


def classify_hit(null_percentile_at_or_better, actual_error, null_median):
    if actual_error > null_median:
        return "weak_or_miss"
    if null_percentile_at_or_better <= 1.0:
        return "rare_hit"
    if null_percentile_at_or_better <= 5.0:
        return "strong_hit"
    if null_percentile_at_or_better <= 20.0:
        return "ordinary_fit"
    return "dense_lattice_fit"


def audit_group(name, config, rng, index_cache):
    max_c = config["max_c"]
    if max_c not in index_cache:
        index_cache[max_c] = build_pair_index(max_c)
    index = index_cache[max_c]

    null_errors = []
    for _ in range(config["null_samples"]):
        target = sample_target(rng, config["null_range"])
        null_errors.append(search_lattice(target, index)["absolute_relative_error"])
    null_errors.sort()

    null_summary = {
        "samples": config["null_samples"],
        "range": config["null_range"],
        "min_error": null_errors[0],
        "p01_error": percentile(null_errors, 0.01),
        "p05_error": percentile(null_errors, 0.05),
        "p10_error": percentile(null_errors, 0.10),
        "median_error": percentile(null_errors, 0.50),
        "p90_error": percentile(null_errors, 0.90),
    }

    target_results = {}
    for target_name, target_value in config["targets"].items():
        fit = search_lattice(target_value, index)
        random_at_or_better = bisect.bisect_right(null_errors, fit["absolute_relative_error"])
        null_percentile_at_or_better = (random_at_or_better / len(null_errors)) * 100.0
        target_results[target_name] = {
            "target_value": target_value,
            **fit,
            "null_percentile_at_or_better": null_percentile_at_or_better,
            "classification": classify_hit(
                null_percentile_at_or_better,
                fit["absolute_relative_error"],
                null_summary["median_error"],
            ),
        }

    return {
        "group": name,
        "max_c": max_c,
        "null_summary": null_summary,
        "targets": target_results,
    }


def evaluate_prediction_landmarks():
    predicted_mass = 933.740752167
    landmarks = {
        "free_proton": 938.27208943,
        "free_neutron": 939.56542194,
        "free_nucleon_mean": (938.27208943 + 939.56542194) / 2.0,
        "atomic_mass_constant_1u": 931.49410372,
        "deuteron_per_nucleon": 1875.61294500 / 2.0,
        "helion_per_nucleon": 2808.39161112 / 3.0,
        "triton_per_nucleon": 2808.92113668 / 3.0,
        "alpha_particle_per_nucleon": 3727.3794118 / 4.0,
        "one_u_plus_deuteron_binding_total": 931.49410372 + (938.27208943 + 939.56542194 - 1875.61294500),
    }
    ranked = []
    for name, value in landmarks.items():
        delta = predicted_mass - value
        ranked.append({
            "name": name,
            "value_MeV": value,
            "delta_MeV": delta,
            "absolute_delta_MeV": abs(delta),
            "relative_delta": delta / value,
        })
    ranked.sort(key=lambda row: row["absolute_delta_MeV"])
    return {
        "predicted_mass_anchor_MeV": predicted_mass,
        "ranked_landmarks": ranked,
        "fits": [
            "one_u_plus_deuteron_binding_total",
            "inside_light_bound_nucleon_per_nucleon_band",
        ],
        "does_not_fit": [
            "free_proton_precision_identity",
            "free_neutron_precision_identity",
            "free_nucleon_mean_precision_identity",
        ],
    }


def evaluate_entropy_frontier():
    l_sum = L0 + J0 + P0 + W0
    weights = [L0 ** i for i in range(1, 7)]
    total = sum(weights)
    normalized = [weight / total for weight in weights]
    field_entropy = -sum(p * math.log(p) for p in normalized if p > 0)
    rows = []
    for partition_penalty in (0.0, 0.2, 0.4, 0.6, 0.8):
        entropy_limit = 5.0 * l_sum * (1.0 - partition_penalty)
        rows.append({
            "partition_penalty": partition_penalty,
            "field_entropy": field_entropy,
            "entropy_limit": entropy_limit,
            "collapsed_into_silo": field_entropy > entropy_limit,
        })
    collapse_threshold = 1.0 - field_entropy / (5.0 * l_sum)
    return {
        "observed_sweep": rows,
        "collapse_observed_in_current_sweep": any(row["collapsed_into_silo"] for row in rows),
        "partition_penalty_needed_for_this_field_to_collapse": collapse_threshold,
        "assessment": "The tested penalties stop at 0.8, while this field needs a penalty above the threshold to collapse.",
    }


def main():
    start = datetime.now(timezone.utc)
    rng = random.Random(RNG_SEED)
    index_cache = {}

    groups = {}
    for name, config in TARGET_GROUPS.items():
        groups[name] = audit_group(name, config, rng, index_cache)

    all_targets = []
    for group in groups.values():
        for target_name, result in group["targets"].items():
            all_targets.append({
                "group": group["group"],
                "name": target_name,
                "classification": result["classification"],
                "absolute_relative_error": result["absolute_relative_error"],
                "null_percentile_at_or_better": result["null_percentile_at_or_better"],
                "coefficients": result["coefficients"],
            })
    all_targets.sort(key=lambda row: (row["null_percentile_at_or_better"], row["absolute_relative_error"]))

    report = {
        "experiment_name": "prime_ljpw_lattice_surprise_audit",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start).total_seconds(),
        "seed": RNG_SEED,
        "base": BASE,
        "ljpw_constants": {
            "L0": L0,
            "J0": J0,
            "P0": P0,
            "W0": W0,
        },
        "groups": groups,
        "ranked_targets_by_surprise": all_targets,
        "prediction_landmark_check": evaluate_prediction_landmarks(),
        "entropy_frontier_check": evaluate_entropy_frontier(),
        "summary": {
            "rare_hits": [row for row in all_targets if row["classification"] == "rare_hit"],
            "strong_hits": [row for row in all_targets if row["classification"] == "strong_hit"],
            "ordinary_or_dense_fits": [
                row for row in all_targets
                if row["classification"] in ("ordinary_fit", "dense_lattice_fit")
            ],
            "weak_or_miss": [row for row in all_targets if row["classification"] == "weak_or_miss"],
        },
    }

    output_file = Path(__file__).resolve().parent / "lattice_surprise_audit_results.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Prime-LJPW Lattice Surprise Audit")
    print("============================================================")
    print("Targets ranked by null-surprise:")
    for row in all_targets:
        print(
            f"  {row['group']:<28} {row['name']:<34}"
            f" error={row['absolute_relative_error'] * 100.0:>9.5f}%"
            f" null<={row['null_percentile_at_or_better']:>6.2f}%"
            f" {row['classification']}"
        )
    entropy = report["entropy_frontier_check"]
    print("\nEntropy frontier:")
    print(f"  collapse observed in current sweep: {entropy['collapse_observed_in_current_sweep']}")
    print(
        "  partition penalty threshold for collapse:"
        f" {entropy['partition_penalty_needed_for_this_field_to_collapse']:.4f}"
    )
    print("\nPrediction landmark nearest match:")
    nearest = report["prediction_landmark_check"]["ranked_landmarks"][0]
    print(
        f"  {nearest['name']} delta={nearest['delta_MeV']:+.6f} MeV"
    )
    print("Results saved to: lattice_surprise_audit_results.json")


if __name__ == "__main__":
    main()
