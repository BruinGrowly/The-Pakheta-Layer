"""
Pakheta Cosmological Bridge prediction pass.

This script keeps the cosmological bridge grammar fixed and asks what it
predicts before any target matching:

    R_LJPW = 30 ** (10 * (L0 + J0 + P0 + W0))
    m_star = sqrt(alpha * hbar * c / (G * R_LJPW))

The result is then compared with CODATA/NIST particle and light-nuclear mass
landmarks. The comparison is intentionally descriptive: it identifies where the
predicted mass lands, and which interpretations survive without retuning.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path


L0 = (math.sqrt(5.0) - 1.0) / 2.0
J0 = math.sqrt(2.0) - 1.0
P0 = math.e - 2.0
W0 = math.log(2.0)
LJPW_SUM = L0 + J0 + P0 + W0


# NIST CODATA 2022 values.
# Source: NIST complete listing, 2022 CODATA adjustment:
# https://physics.nist.gov/cuu/Constants/Table/allascii.txt
CODATA_2022 = {
    "fine_structure_constant": 7.2973525643e-3,
    "newtonian_constant_of_gravitation": 6.67430e-11,
    "reduced_planck_constant": 1.054571817e-34,
    "speed_of_light": 299792458.0,
    "electron_volt_joule": 1.602176634e-19,
    "atomic_mass_constant_kg": 1.66053906892e-27,
    "atomic_mass_constant_MeV": 931.49410372,
    "electron_mass_kg": 9.1093837139e-31,
    "electron_mass_MeV": 0.51099895069,
    "muon_mass_kg": 1.883531627e-28,
    "muon_mass_MeV": 105.6583755,
    "proton_mass_kg": 1.67262192595e-27,
    "proton_mass_MeV": 938.27208943,
    "neutron_mass_kg": 1.67492750056e-27,
    "neutron_mass_MeV": 939.56542194,
    "deuteron_mass_kg": 3.3435837768e-27,
    "deuteron_mass_MeV": 1875.61294500,
    "helion_mass_kg": 5.0064127862e-27,
    "helion_mass_MeV": 2808.39161112,
    "triton_mass_kg": 5.0073567512e-27,
    "triton_mass_MeV": 2808.92113668,
    "alpha_particle_mass_kg": 6.6446573450e-27,
    "alpha_particle_mass_MeV": 3727.3794118,
}


def mev_from_kg(mass_kg):
    joules = mass_kg * CODATA_2022["speed_of_light"] ** 2
    return joules / CODATA_2022["electron_volt_joule"] / 1.0e6


def gravitational_coupling(mass_kg):
    return (
        CODATA_2022["newtonian_constant_of_gravitation"]
        * mass_kg
        * mass_kg
        / (CODATA_2022["reduced_planck_constant"] * CODATA_2022["speed_of_light"])
    )


def bridge_ratio():
    return 30.0 ** (10.0 * LJPW_SUM)


def predicted_mass_kg():
    return math.sqrt(
        CODATA_2022["fine_structure_constant"]
        * CODATA_2022["reduced_planck_constant"]
        * CODATA_2022["speed_of_light"]
        / (CODATA_2022["newtonian_constant_of_gravitation"] * bridge_ratio())
    )


def relative_error(predicted, target):
    return predicted / target - 1.0


def binding_energy(total_constituent_mass_mev, bound_mass_mev):
    return total_constituent_mass_mev - bound_mass_mev


def make_landmarks():
    proton = CODATA_2022["proton_mass_MeV"]
    neutron = CODATA_2022["neutron_mass_MeV"]
    deuteron = CODATA_2022["deuteron_mass_MeV"]
    helion = CODATA_2022["helion_mass_MeV"]
    triton = CODATA_2022["triton_mass_MeV"]
    alpha = CODATA_2022["alpha_particle_mass_MeV"]
    atomic_mass = CODATA_2022["atomic_mass_constant_MeV"]

    deuteron_binding = binding_energy(proton + neutron, deuteron)
    helion_binding = binding_energy(2.0 * proton + neutron, helion)
    triton_binding = binding_energy(proton + 2.0 * neutron, triton)
    alpha_binding = binding_energy(2.0 * proton + 2.0 * neutron, alpha)

    return {
        "leptonic_scales": {
            "electron": CODATA_2022["electron_mass_MeV"],
            "muon": CODATA_2022["muon_mass_MeV"],
        },
        "free_hadron_scales": {
            "proton": proton,
            "neutron": neutron,
            "free_nucleon_mean": (proton + neutron) / 2.0,
        },
        "light_nuclear_per_nucleon_scales": {
            "alpha_particle_per_nucleon": alpha / 4.0,
            "atomic_mass_constant_1u": atomic_mass,
            "helion_per_nucleon": helion / 3.0,
            "triton_per_nucleon": triton / 3.0,
            "deuteron_per_nucleon": deuteron / 2.0,
        },
        "binding_energies": {
            "deuteron_total": deuteron_binding,
            "deuteron_per_nucleon": deuteron_binding / 2.0,
            "helion_total": helion_binding,
            "helion_per_nucleon": helion_binding / 3.0,
            "triton_total": triton_binding,
            "triton_per_nucleon": triton_binding / 3.0,
            "alpha_total": alpha_binding,
            "alpha_per_nucleon": alpha_binding / 4.0,
        },
        "composite_candidate_scales": {
            "atomic_mass_constant_plus_deuteron_binding_total": atomic_mass + deuteron_binding,
            "atomic_mass_constant_plus_deuteron_binding_per_nucleon": atomic_mass + deuteron_binding / 2.0,
            "alpha_per_nucleon_plus_deuteron_binding_total": alpha / 4.0 + deuteron_binding,
        },
    }


def flatten_landmarks(landmark_groups):
    rows = []
    for group_name, group in landmark_groups.items():
        for name, mass_mev in group.items():
            rows.append({
                "group": group_name,
                "name": name,
                "mass_MeV": mass_mev,
            })
    return rows


def rank_landmarks(m_star_mev, rows):
    ranked = []
    for row in rows:
        delta = m_star_mev - row["mass_MeV"]
        ranked.append({
            **row,
            "delta_MeV_predicted_minus_landmark": delta,
            "absolute_delta_MeV": abs(delta),
            "absolute_relative_delta": abs(delta / row["mass_MeV"]),
        })
    ranked.sort(key=lambda item: item["absolute_delta_MeV"])
    return ranked


def evaluate_hypotheses(m_star_mev, landmarks):
    proton = landmarks["free_hadron_scales"]["proton"]
    nucleon_mean = landmarks["free_hadron_scales"]["free_nucleon_mean"]
    nuclear_per_nucleon = landmarks["light_nuclear_per_nucleon_scales"]
    lower = min(nuclear_per_nucleon.values())
    upper = max(nuclear_per_nucleon.values())
    atomic_plus_deuteron = landmarks["composite_candidate_scales"][
        "atomic_mass_constant_plus_deuteron_binding_total"
    ]
    deuteron_binding = landmarks["binding_energies"]["deuteron_total"]
    offset_from_1u = m_star_mev - nuclear_per_nucleon["atomic_mass_constant_1u"]

    return {
        "free_proton_identity": {
            "target_MeV": proton,
            "delta_MeV": m_star_mev - proton,
            "absolute_relative_delta": abs(relative_error(m_star_mev, proton)),
            "survives_as_precision_identity": False,
            "reason": "The predicted mass is about 4.53 MeV below the free proton.",
        },
        "free_nucleon_mean_identity": {
            "target_MeV": nucleon_mean,
            "delta_MeV": m_star_mev - nucleon_mean,
            "absolute_relative_delta": abs(relative_error(m_star_mev, nucleon_mean)),
            "survives_as_precision_identity": False,
            "reason": "The predicted mass is about 5.18 MeV below the free nucleon mean.",
        },
        "light_nuclear_per_nucleon_band": {
            "band_min_MeV": lower,
            "band_max_MeV": upper,
            "inside_band": lower <= m_star_mev <= upper,
            "nearest_band_edges": {
                "distance_to_min_MeV": m_star_mev - lower,
                "distance_to_max_MeV": upper - m_star_mev,
            },
            "reason": "The prediction lands inside the light bound-nucleon per-nucleon mass band.",
        },
        "atomic_mass_plus_deuteron_binding_candidate": {
            "target_MeV": atomic_plus_deuteron,
            "delta_MeV": m_star_mev - atomic_plus_deuteron,
            "absolute_relative_delta": abs(relative_error(m_star_mev, atomic_plus_deuteron)),
            "offset_from_1u_MeV": offset_from_1u,
            "deuteron_binding_total_MeV": deuteron_binding,
            "offset_minus_deuteron_binding_MeV": offset_from_1u - deuteron_binding,
            "offset_to_deuteron_binding_relative_delta": abs(
                relative_error(offset_from_1u, deuteron_binding)
            ),
            "reason": "The prediction is close to 1u plus the total deuteron binding energy.",
        },
    }


def main():
    start_time = datetime.now(timezone.utc)
    ratio = bridge_ratio()
    m_star_kg = predicted_mass_kg()
    m_star_mev = mev_from_kg(m_star_kg)
    target_alpha_g = gravitational_coupling(m_star_kg)

    landmarks = make_landmarks()
    ranked_landmarks = rank_landmarks(m_star_mev, flatten_landmarks(landmarks))
    hypotheses = evaluate_hypotheses(m_star_mev, landmarks)

    report = {
        "experiment_name": "cosmological_bridge_predictions",
        "date_executed": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": (datetime.now(timezone.utc) - start_time).total_seconds(),
        "source": "NIST CODATA 2022 complete listing, https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
        "frozen_bridge": {
            "formula": "R_LJPW = 30 ** (10 * (L0 + J0 + P0 + W0))",
            "R_LJPW": ratio,
            "L0": L0,
            "J0": J0,
            "P0": P0,
            "W0": W0,
            "LJPW_sum": LJPW_SUM,
        },
        "prediction": {
            "formula": "m_star = sqrt(alpha * hbar * c / (G * R_LJPW))",
            "mass_kg": m_star_kg,
            "mass_MeV": m_star_mev,
            "mass_u": m_star_kg / CODATA_2022["atomic_mass_constant_kg"],
            "alpha_G_at_m_star": target_alpha_g,
        },
        "landmarks": landmarks,
        "ranked_landmark_matches": ranked_landmarks,
        "hypothesis_evaluation": hypotheses,
        "cautious_read": {
            "primary_prediction": "The fixed bridge predicts a mass anchor near 933.741 MeV/c^2.",
            "does_not_hit_free_proton": True,
            "lands_inside_light_nuclear_per_nucleon_band": hypotheses[
                "light_nuclear_per_nucleon_band"
            ]["inside_band"],
            "closest_simple_landmark": ranked_landmarks[0],
            "strongest_candidate_observation": {
                "statement": "m_star is close to 1u plus the total deuteron binding energy.",
                "delta_MeV": hypotheses["atomic_mass_plus_deuteron_binding_candidate"][
                    "delta_MeV"
                ],
                "offset_minus_deuteron_binding_MeV": hypotheses[
                    "atomic_mass_plus_deuteron_binding_candidate"
                ]["offset_minus_deuteron_binding_MeV"],
            },
        },
    }

    output_file = Path(__file__).resolve().parent / "cosmological_bridge_prediction_results.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("============================================================")
    print(" Cosmological Bridge Prediction Pass")
    print("============================================================")
    print(f"Predicted mass anchor: {m_star_mev:.9f} MeV/c^2")
    print(f"Predicted mass in u:   {report['prediction']['mass_u']:.9f} u")
    print("\nNearest landmarks:")
    for row in ranked_landmarks[:5]:
        print(
            f"  {row['name']:<52}"
            f" {row['mass_MeV']:.9f} MeV"
            f"  delta={row['delta_MeV_predicted_minus_landmark']:+.9f}"
        )
    candidate = hypotheses["atomic_mass_plus_deuteron_binding_candidate"]
    print("\nCandidate structure:")
    print(f"  m_star - 1u:                    {candidate['offset_from_1u_MeV']:.9f} MeV")
    print(f"  deuteron binding energy total:  {candidate['deuteron_binding_total_MeV']:.9f} MeV")
    print(f"  difference:                     {candidate['offset_minus_deuteron_binding_MeV']:+.9f} MeV")
    print("Results saved to: cosmological_bridge_prediction_results.json")


if __name__ == "__main__":
    main()
