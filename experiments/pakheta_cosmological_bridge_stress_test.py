"""
Pakheta Cosmological Bridge stress test.

This script treats the hierarchy-scale bridge as a constrained hypothesis:

    alpha / alpha_G(pp) ~= 30 ** (10 * (L0 + J0 + P0 + W0))

It does not try to strengthen the claim by rhetoric. It asks what survives when
we recompute from CODATA 2022 constants, include uncertainty, compare exact-fit
parameters, and scan nearby/null formula spaces.
"""

import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path


# LJPW constants used across the repository.
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)
LJPW_VECTOR = (L0, J0, P0, W0)
LJPW_LABELS = ("L0", "J0", "P0", "W0")
LJPW_SUM = sum(LJPW_VECTOR)


# NIST CODATA 2022 values.
# Source: NIST complete listing, 2022 CODATA adjustment:
# https://physics.nist.gov/cuu/Constants/Table/allascii.txt
CODATA_2022 = {
    "inverse_fine_structure_constant": {
        "value": 137.035999177,
        "standard_uncertainty": 0.000000021,
    },
    "fine_structure_constant": {
        "value": 7.2973525643e-3,
        "standard_uncertainty": 0.0000000011e-3,
    },
    "newtonian_constant_of_gravitation": {
        "value": 6.67430e-11,
        "standard_uncertainty": 0.00015e-11,
        "unit": "m^3 kg^-1 s^-2",
    },
    "proton_mass": {
        "value": 1.67262192595e-27,
        "standard_uncertainty": 0.00000000052e-27,
        "unit": "kg",
    },
    "neutron_mass": {
        "value": 1.67492750056e-27,
        "standard_uncertainty": 0.00000000085e-27,
        "unit": "kg",
    },
    "electron_mass": {
        "value": 9.1093837139e-31,
        "standard_uncertainty": 0.0000000028e-31,
        "unit": "kg",
    },
    "muon_mass": {
        "value": 1.883531627e-28,
        "standard_uncertainty": 0.000000042e-28,
        "unit": "kg",
    },
    "reduced_planck_constant": {
        "value": 1.054571817e-34,
        "standard_uncertainty": 0.0,
        "unit": "J s",
    },
    "speed_of_light": {
        "value": 299792458.0,
        "standard_uncertainty": 0.0,
        "unit": "m s^-1",
    },
}


def relative_uncertainty(value, uncertainty):
    if value == 0.0:
        return 0.0
    return abs(uncertainty / value)


def gravitational_coupling(mass):
    """Dimensionless gravitational coupling alpha_G = G m^2 / (hbar c)."""
    g = CODATA_2022["newtonian_constant_of_gravitation"]["value"]
    hbar = CODATA_2022["reduced_planck_constant"]["value"]
    c = CODATA_2022["speed_of_light"]["value"]
    return g * mass * mass / (hbar * c)


def hierarchy_ratio_for_mass(mass):
    alpha = CODATA_2022["fine_structure_constant"]["value"]
    return alpha / gravitational_coupling(mass)


def hierarchy_ratio_relative_uncertainty(mass_key):
    """Propagate independent relative uncertainties for alpha / alpha_G(m,m)."""
    alpha = CODATA_2022["fine_structure_constant"]
    g = CODATA_2022["newtonian_constant_of_gravitation"]
    mass = CODATA_2022[mass_key]
    terms = [
        relative_uncertainty(alpha["value"], alpha["standard_uncertainty"]) ** 2,
        relative_uncertainty(g["value"], g["standard_uncertainty"]) ** 2,
        (2.0 * relative_uncertainty(mass["value"], mass["standard_uncertainty"])) ** 2,
    ]
    return math.sqrt(sum(terms))


def bridge_prediction(base=30.0, scale=10.0, coefficients=(1, 1, 1, 1)):
    ljpw_combo = sum(c * v for c, v in zip(coefficients, LJPW_VECTOR))
    return base ** (scale * ljpw_combo)


def relative_error(predicted, target):
    return predicted / target - 1.0


def scan_integer_bases(target, min_base=2, max_base=200, scale=10.0, coefficients=(1, 1, 1, 1)):
    rows = []
    for base in range(min_base, max_base + 1):
        predicted = bridge_prediction(base=base, scale=scale, coefficients=coefficients)
        rows.append({
            "base": base,
            "absolute_relative_error": abs(relative_error(predicted, target)),
        })
    rows.sort(key=lambda row: row["absolute_relative_error"])
    return rows


def scan_integer_scales(target, base=30.0, min_scale=1, max_scale=20, coefficients=(1, 1, 1, 1)):
    rows = []
    for scale in range(min_scale, max_scale + 1):
        predicted = bridge_prediction(base=base, scale=scale, coefficients=coefficients)
        rows.append({
            "scale": scale,
            "absolute_relative_error": abs(relative_error(predicted, target)),
        })
    rows.sort(key=lambda row: row["absolute_relative_error"])
    return rows


def scan_coefficients(target, coefficient_values, base=30.0, scale=10.0):
    rows = []
    for coefficients in itertools.product(coefficient_values, repeat=4):
        if not any(coefficients):
            continue
        ljpw_combo = sum(c * v for c, v in zip(coefficients, LJPW_VECTOR))
        if ljpw_combo <= 0.0:
            continue
        predicted = bridge_prediction(base=base, scale=scale, coefficients=coefficients)
        rows.append({
            "coefficients": dict(zip(LJPW_LABELS, coefficients)),
            "ljpw_combo": ljpw_combo,
            "absolute_relative_error": abs(relative_error(predicted, target)),
        })
    rows.sort(key=lambda row: row["absolute_relative_error"])
    return rows


def scan_base_and_coefficients(target, coefficient_values, min_base=2, max_base=200, scale=10.0):
    rows = []
    for base in range(min_base, max_base + 1):
        for coefficients in itertools.product(coefficient_values, repeat=4):
            if not any(coefficients):
                continue
            ljpw_combo = sum(c * v for c, v in zip(coefficients, LJPW_VECTOR))
            if ljpw_combo <= 0.0:
                continue
            predicted = bridge_prediction(base=base, scale=scale, coefficients=coefficients)
            rows.append({
                "base": base,
                "coefficients": dict(zip(LJPW_LABELS, coefficients)),
                "ljpw_combo": ljpw_combo,
                "absolute_relative_error": abs(relative_error(predicted, target)),
            })
    rows.sort(key=lambda row: row["absolute_relative_error"])
    return rows


def find_rank(rows, predicate):
    for index, row in enumerate(rows, start=1):
        if predicate(row):
            return index
    return None


def top_rows(rows, count=10):
    return rows[:count]


def main():
    start_time = datetime.now(timezone.utc)

    proton_mass = CODATA_2022["proton_mass"]["value"]
    target_alpha_g = gravitational_coupling(proton_mass)
    target_ratio = hierarchy_ratio_for_mass(proton_mass)
    target_relative_uncertainty = hierarchy_ratio_relative_uncertainty("proton_mass")

    predicted_ratio = bridge_prediction()
    error = relative_error(predicted_ratio, target_ratio)
    sigma_distance = abs(error) / target_relative_uncertainty

    required_exponent = math.log(target_ratio) / math.log(30.0)
    required_scale = required_exponent / LJPW_SUM
    required_base = target_ratio ** (1.0 / (10.0 * LJPW_SUM))
    alpha = CODATA_2022["fine_structure_constant"]["value"]
    g = CODATA_2022["newtonian_constant_of_gravitation"]["value"]
    hbar = CODATA_2022["reduced_planck_constant"]["value"]
    c = CODATA_2022["speed_of_light"]["value"]
    mass_for_exact_formula = math.sqrt(alpha * hbar * c / (g * predicted_ratio))

    base_scan = scan_integer_bases(target_ratio)
    scale_scan = scan_integer_scales(target_ratio)
    coeff_scan_nonnegative = scan_coefficients(target_ratio, range(0, 4))
    coeff_scan_mixed = scan_coefficients(target_ratio, range(-2, 4))
    base_coeff_scan = scan_base_and_coefficients(target_ratio, range(0, 4))

    original_coefficients = {"L0": 1, "J0": 1, "P0": 1, "W0": 1}
    original_abs_error = abs(error)

    alternative_masses = {}
    for key in ("electron_mass", "muon_mass", "proton_mass", "neutron_mass"):
        ratio = hierarchy_ratio_for_mass(CODATA_2022[key]["value"])
        alternative_masses[key] = {
            "hierarchy_ratio": ratio,
            "bridge_relative_error": relative_error(predicted_ratio, ratio),
            "bridge_absolute_relative_error": abs(relative_error(predicted_ratio, ratio)),
        }

    report = {
        "experiment_name": "cosmological_bridge_stress_test",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        "source": "NIST CODATA 2022 complete listing, https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
        "codata_2022": CODATA_2022,
        "ljpw": {
            "L0": L0,
            "J0": J0,
            "P0": P0,
            "W0": W0,
            "sum": LJPW_SUM,
        },
        "primary_test": {
            "target_alpha_G_proton_proton": target_alpha_g,
            "target_ratio_alpha_over_alpha_G": target_ratio,
            "target_relative_standard_uncertainty": target_relative_uncertainty,
            "predicted_ratio_30_pow_10_sum_ljpw": predicted_ratio,
            "relative_error": error,
            "absolute_relative_error": abs(error),
            "sigma_distance_from_codata": sigma_distance,
            "within_one_sigma": sigma_distance <= 1.0,
            "within_three_sigma": sigma_distance <= 3.0,
        },
        "exact_fit_diagnostics": {
            "required_exponent_for_base_30": required_exponent,
            "actual_exponent_10_sum_ljpw": 10.0 * LJPW_SUM,
            "required_scale_for_base_30_and_ljpw_sum": required_scale,
            "scale_delta_from_10": required_scale - 10.0,
            "required_base_for_scale_10_and_ljpw_sum": required_base,
            "base_delta_from_30": required_base - 30.0,
            "base_percent_delta_from_30": (required_base / 30.0 - 1.0) * 100.0,
            "mass_for_exact_formula_kg": mass_for_exact_formula,
            "mass_ratio_to_proton": mass_for_exact_formula / proton_mass,
            "mass_percent_delta_from_proton": (mass_for_exact_formula / proton_mass - 1.0) * 100.0,
        },
        "sensitivity": {
            "d_ln_prediction_d_scale": LJPW_SUM * math.log(30.0),
            "d_ln_prediction_d_base_at_30": (10.0 * LJPW_SUM) / 30.0,
            "d_ln_target_ratio_d_mass": -2.0,
            "interpretation": {
                "scale_shift_0_001_relative_change": math.exp(0.001 * LJPW_SUM * math.log(30.0)) - 1.0,
                "base_shift_0_01_relative_change": math.exp(0.01 * (10.0 * LJPW_SUM) / 30.0) - 1.0,
                "mass_shift_0_5_percent_target_change": (1.005 ** -2.0) - 1.0,
            },
        },
        "constrained_scans": {
            "integer_base_2_to_200_fixed_scale_10_original_coefficients": {
                "original_rank": find_rank(base_scan, lambda row: row["base"] == 30),
                "better_than_original_count": sum(row["absolute_relative_error"] < original_abs_error for row in base_scan),
                "top_10": top_rows(base_scan),
            },
            "integer_scale_1_to_20_fixed_base_30_original_coefficients": {
                "original_rank": find_rank(scale_scan, lambda row: row["scale"] == 10),
                "better_than_original_count": sum(row["absolute_relative_error"] < original_abs_error for row in scale_scan),
                "top_10": top_rows(scale_scan),
            },
            "coefficients_0_to_3_fixed_base_30_scale_10": {
                "original_rank": find_rank(coeff_scan_nonnegative, lambda row: row["coefficients"] == original_coefficients),
                "better_than_original_count": sum(row["absolute_relative_error"] < original_abs_error for row in coeff_scan_nonnegative),
                "searched_formula_count": len(coeff_scan_nonnegative),
                "top_10": top_rows(coeff_scan_nonnegative),
            },
            "coefficients_minus2_to_3_fixed_base_30_scale_10": {
                "original_rank": find_rank(coeff_scan_mixed, lambda row: row["coefficients"] == original_coefficients),
                "better_than_original_count": sum(row["absolute_relative_error"] < original_abs_error for row in coeff_scan_mixed),
                "searched_formula_count": len(coeff_scan_mixed),
                "top_10": top_rows(coeff_scan_mixed),
            },
            "base_2_to_200_coefficients_0_to_3_fixed_scale_10": {
                "original_rank": find_rank(
                    base_coeff_scan,
                    lambda row: row["base"] == 30 and row["coefficients"] == original_coefficients,
                ),
                "better_than_original_count": sum(row["absolute_relative_error"] < original_abs_error for row in base_coeff_scan),
                "searched_formula_count": len(base_coeff_scan),
                "top_10": top_rows(base_coeff_scan),
            },
        },
        "alternative_mass_tests": alternative_masses,
        "cautious_read": {
            "passes_constrained_integer_base_scan": find_rank(base_scan, lambda row: row["base"] == 30) == 1,
            "passes_constrained_integer_scale_scan": find_rank(scale_scan, lambda row: row["scale"] == 10) == 1,
            "passes_small_nonnegative_coefficient_scan": find_rank(
                coeff_scan_nonnegative,
                lambda row: row["coefficients"] == original_coefficients,
            ) == 1,
            "misses_codata_uncertainty_by_many_sigma": sigma_distance > 100.0,
            "base_or_scale_freedom_can_create_competing_fits": find_rank(
                base_coeff_scan,
                lambda row: row["base"] == 30 and row["coefficients"] == original_coefficients,
            ) > 1,
        },
    }

    output_file = Path(__file__).resolve().parent / "cosmological_bridge_stress_results.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Cosmological Bridge Stress Test")
    print("============================================================")
    print(f"Target alpha/alpha_G(pp):     {target_ratio:.6e}")
    print(f"Bridge prediction:            {predicted_ratio:.6e}")
    print(f"Relative error:               {error * 100.0:.6f}%")
    print(f"CODATA sigma distance:        {sigma_distance:.1f} sigma")
    print(f"Required scale for exact fit: {required_scale:.9f}")
    print(f"Required base for exact fit:  {required_base:.9f}")
    print(f"Base scan rank for 30:        {report['constrained_scans']['integer_base_2_to_200_fixed_scale_10_original_coefficients']['original_rank']}")
    print(f"Scale scan rank for 10:       {report['constrained_scans']['integer_scale_1_to_20_fixed_base_30_original_coefficients']['original_rank']}")
    print("Results saved to: cosmological_bridge_stress_results.json")


if __name__ == "__main__":
    main()
