"""
Pakheta Higgs hierarchy bridge.

This pass asks whether the Higgs hierarchy problem has a relational address:

1. The Higgs mass as a compact electroweak coordinate relative to the proton.
2. The full Planck/Higgs separation as a direct prime-LJPW hierarchy coordinate.
3. The two-step bridge from Planck scale through the cosmological mass anchor
   into the Higgs coordinate.

No new constants are fitted inside this script. The Higgs/proton coordinate is
the existing electroweak coordinate used by the prediction atlas.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path


BASE = 30.0
L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)
LJPW_SUM = L0 + J0 + P0 + W0

OPERATOR_VALUES = {
    "c_L": L0,
    "c_J": J0,
    "c_P": P0,
    "c_W": W0,
}

CODATA_2022 = {
    "fine_structure_constant": 7.2973525643e-3,
    "newtonian_constant_of_gravitation": 6.67430e-11,
    "reduced_planck_constant": 1.054571817e-34,
    "speed_of_light": 299792458.0,
    "electron_volt_joule": 1.602176634e-19,
    "proton_mass_MeV": 938.27208943,
}

HIGGS_TARGETS = {
    "atlas_2023_combined_MeV": 125110.0,
    "atlas_2023_uncertainty_MeV": 110.0,
    "repo_legacy_MeV": 125100.0,
}

# Existing electroweak coordinate from the prediction atlas.
HIGGS_TO_PROTON_COORDINATE = {
    "c_L": -5,
    "c_J": -3,
    "c_P": 9,
    "c_W": -1,
}

# Direct full-Planck/Higgs hierarchy coordinate found under coefficient cap 14.
FULL_PLANCK_TO_HIGGS_COORDINATE = {
    "c_L": 14,
    "c_J": -8,
    "c_P": -3,
    "c_W": 12,
}

# Secondary comparison for the reduced Planck mass convention.
REDUCED_PLANCK_TO_HIGGS_COORDINATE = {
    "c_L": -9,
    "c_J": 19,
    "c_P": 16,
    "c_W": -4,
}


def exponent_from_coefficients(coefficients):
    return sum(coefficients[key] * OPERATOR_VALUES[key] for key in OPERATOR_VALUES)


def value_from_coefficients(coefficients):
    return BASE ** exponent_from_coefficients(coefficients)


def kg_to_mev(mass_kg):
    joules = mass_kg * CODATA_2022["speed_of_light"] ** 2
    return joules / CODATA_2022["electron_volt_joule"] / 1.0e6


def full_planck_mass_mev():
    mass_kg = math.sqrt(
        CODATA_2022["reduced_planck_constant"]
        * CODATA_2022["speed_of_light"]
        / CODATA_2022["newtonian_constant_of_gravitation"]
    )
    return kg_to_mev(mass_kg)


def reduced_planck_mass_mev():
    return full_planck_mass_mev() / math.sqrt(8.0 * math.pi)


def hierarchy_ratio():
    return BASE ** (10.0 * LJPW_SUM)


def bridge_mass_anchor_mev():
    mass_kg = math.sqrt(
        CODATA_2022["fine_structure_constant"]
        * CODATA_2022["reduced_planck_constant"]
        * CODATA_2022["speed_of_light"]
        / (CODATA_2022["newtonian_constant_of_gravitation"] * hierarchy_ratio())
    )
    return kg_to_mev(mass_kg)


def residual(predicted, observed, uncertainty=None):
    delta = predicted - observed
    row = {
        "predicted_MeV": predicted,
        "observed_MeV": observed,
        "delta_MeV": delta,
        "absolute_delta_MeV": abs(delta),
        "relative_delta": predicted / observed - 1.0,
        "absolute_relative_delta": abs(predicted / observed - 1.0),
    }
    if uncertainty:
        row["sigma_units"] = delta / uncertainty
    return row


def ratio_residual(predicted, observed):
    delta = predicted - observed
    return {
        "predicted_ratio": predicted,
        "observed_ratio": observed,
        "delta": delta,
        "relative_delta": predicted / observed - 1.0,
        "absolute_relative_delta": abs(predicted / observed - 1.0),
    }


def coordinate_report(coefficients):
    return {
        "coefficients": coefficients,
        "exponent": exponent_from_coefficients(coefficients),
        "value": value_from_coefficients(coefficients),
    }


def build_report():
    start = datetime.now(timezone.utc)
    full_planck = full_planck_mass_mev()
    reduced_planck = reduced_planck_mass_mev()
    proton = CODATA_2022["proton_mass_MeV"]
    higgs_target = HIGGS_TARGETS["atlas_2023_combined_MeV"]
    higgs_uncertainty = HIGGS_TARGETS["atlas_2023_uncertainty_MeV"]
    higgs_legacy = HIGGS_TARGETS["repo_legacy_MeV"]

    higgs_coordinate = coordinate_report(HIGGS_TO_PROTON_COORDINATE)
    full_planck_coordinate = coordinate_report(FULL_PLANCK_TO_HIGGS_COORDINATE)
    reduced_planck_coordinate = coordinate_report(REDUCED_PLANCK_TO_HIGGS_COORDINATE)

    higgs_from_proton = proton * higgs_coordinate["value"]
    higgs_from_full_planck = full_planck / full_planck_coordinate["value"]
    higgs_from_reduced_planck = reduced_planck / reduced_planck_coordinate["value"]

    mass_anchor = bridge_mass_anchor_mev()
    higgs_from_mass_anchor = mass_anchor * higgs_coordinate["value"]
    full_planck_to_higgs_from_two_step = full_planck / higgs_from_mass_anchor

    observed_full_planck_ratio = full_planck / higgs_target
    observed_reduced_planck_ratio = reduced_planck / higgs_target

    return {
        "experiment_name": "pakheta_higgs_hierarchy_bridge",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start).total_seconds(),
        "source": {
            "constants": "CODATA 2022 values already used by the Pakheta bridge scripts.",
            "higgs_mass_target": (
                "ATLAS 2023 combined Run 1 + Run 2 mass result: 125.11 +/- 0.11 GeV; "
                "repo legacy comparison: 125.10 GeV."
            ),
        },
        "posture": "relationship_first_higgs_hierarchy",
        "constants": {
            "base": BASE,
            "L0": L0,
            "J0": J0,
            "P0": P0,
            "W0": W0,
            "ljpw_sum": LJPW_SUM,
            "full_planck_mass_MeV": full_planck,
            "reduced_planck_mass_MeV": reduced_planck,
            "proton_mass_MeV": proton,
            "higgs_targets": HIGGS_TARGETS,
        },
        "cosmological_hierarchy_bridge": {
            "R_LJPW": hierarchy_ratio(),
            "formula": "R_LJPW = 30^(10 * (L0 + J0 + P0 + W0))",
            "mass_anchor_MeV": mass_anchor,
            "mass_anchor_relation": (
                "m_star = sqrt(alpha * hbar * c / (G * R_LJPW)); this is the same "
                "mass anchor used in the nuclear binding ladder."
            ),
        },
        "predictions": {
            "higgs_as_proton_relative_coordinate": {
                "formula": "m_H = m_p * 30^(-5L0 - 3J0 + 9P0 - W0)",
                "coordinate": higgs_coordinate,
                "predicted_mass_MeV": higgs_from_proton,
                "atlas_2023_overlay": residual(
                    higgs_from_proton,
                    higgs_target,
                    uncertainty=higgs_uncertainty,
                ),
                "repo_legacy_overlay": residual(higgs_from_proton, higgs_legacy),
                "read": (
                    "The Higgs sits as a compact electroweak coordinate about 133.338 proton masses above the proton."
                ),
            },
            "full_planck_to_higgs_direct_coordinate": {
                "formula": "M_P / m_H = 30^(14L0 - 8J0 - 3P0 + 12W0)",
                "coordinate": full_planck_coordinate,
                "observed_full_planck_to_higgs_ratio": observed_full_planck_ratio,
                "ratio_overlay": ratio_residual(
                    full_planck_coordinate["value"],
                    observed_full_planck_ratio,
                ),
                "predicted_mass_MeV": higgs_from_full_planck,
                "atlas_2023_overlay": residual(
                    higgs_from_full_planck,
                    higgs_target,
                    uncertainty=higgs_uncertainty,
                ),
                "read": (
                    "The full Planck/Higgs hierarchy gap itself lands on a clean prime-LJPW address."
                ),
            },
            "reduced_planck_to_higgs_secondary_coordinate": {
                "formula": "M_reduced_P / m_H = 30^(-9L0 + 19J0 + 16P0 - 4W0)",
                "coordinate": reduced_planck_coordinate,
                "observed_reduced_planck_to_higgs_ratio": observed_reduced_planck_ratio,
                "ratio_overlay": ratio_residual(
                    reduced_planck_coordinate["value"],
                    observed_reduced_planck_ratio,
                ),
                "predicted_mass_MeV": higgs_from_reduced_planck,
                "atlas_2023_overlay": residual(
                    higgs_from_reduced_planck,
                    higgs_target,
                    uncertainty=higgs_uncertainty,
                ),
                "read": (
                    "The reduced Planck convention also has an address, but with larger coefficients."
                ),
            },
            "two_step_cosmological_bridge_to_higgs": {
                "formula": "m_H = m_star * 30^(-5L0 - 3J0 + 9P0 - W0)",
                "predicted_mass_MeV": higgs_from_mass_anchor,
                "atlas_2023_overlay": residual(
                    higgs_from_mass_anchor,
                    higgs_target,
                    uncertainty=higgs_uncertainty,
                ),
                "full_planck_to_predicted_higgs_ratio": full_planck_to_higgs_from_two_step,
                "read": (
                    "The two-step bridge lands at the electroweak scale but is low because m_star is a bound-nuclear "
                    "anchor below the free proton. Precision Higgs placement wants the free proton anchor."
                ),
            },
        },
        "working_interpretation": {
            "plain_read": (
                "The Higgs is not appearing as an arbitrary 125 GeV object in this grammar. It appears as a compact "
                "electroweak coordinate relative to the proton, while the huge Planck/Higgs separation also has a "
                "direct lattice address."
            ),
            "hierarchy_shape": [
                "Planck scale",
                "full Planck/Higgs hierarchy coordinate",
                "Higgs electroweak coordinate",
                "proton/free-matter anchor",
                "cosmological bridge mass anchor",
            ],
            "next_tests": [
                "Carry the same electroweak coordinate posture to the Higgs vacuum expectation value.",
                "Map the top-quark Yukawa relation against Higgs/proton and Higgs/Planck coordinates.",
                "Compare W/Z/H ratios as a relational electroweak triangle instead of three independent mass hits.",
            ],
        },
    }


def main():
    report = build_report()
    output_file = Path(__file__).resolve().parent / "higgs_hierarchy_bridge_results.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Pakheta Higgs Hierarchy Bridge")
    print("============================================================")
    proton_overlay = report["predictions"]["higgs_as_proton_relative_coordinate"]["atlas_2023_overlay"]
    print(
        "Higgs/proton coordinate:"
        f" predicted={proton_overlay['predicted_MeV'] / 1000.0:.9f} GeV,"
        f" observed={proton_overlay['observed_MeV'] / 1000.0:.9f} GeV,"
        f" delta={proton_overlay['delta_MeV']:+.6f} MeV"
    )
    planck_overlay = report["predictions"]["full_planck_to_higgs_direct_coordinate"]["atlas_2023_overlay"]
    print(
        "Full Planck/Higgs coordinate:"
        f" predicted={planck_overlay['predicted_MeV'] / 1000.0:.9f} GeV,"
        f" observed={planck_overlay['observed_MeV'] / 1000.0:.9f} GeV,"
        f" delta={planck_overlay['delta_MeV']:+.6f} MeV"
    )
    two_step = report["predictions"]["two_step_cosmological_bridge_to_higgs"]["atlas_2023_overlay"]
    print(
        "Two-step cosmological bridge:"
        f" predicted={two_step['predicted_MeV'] / 1000.0:.9f} GeV,"
        f" delta={two_step['delta_MeV']:+.6f} MeV"
    )
    print("Results saved to: higgs_hierarchy_bridge_results.json")


if __name__ == "__main__":
    main()
